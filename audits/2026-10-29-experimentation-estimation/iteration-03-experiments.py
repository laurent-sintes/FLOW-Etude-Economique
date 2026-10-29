"""Calculate the isolated iteration 03 from frozen hypotheses; no active-model writes."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import argparse, hashlib, json, math, sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tmp/model-deps"))
import yaml

def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def add(values):
    values = list(values)
    return [sum(v[i] for v in values) for i in range(3)]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    names = ["iteration-03-contrat.json", "iteration-03-protocole.json",
             "iteration-03-m1-common.json", "iteration-03-m1-ref.json",
             "iteration-03-m1-stock.json", "iteration-03-m2.json",
             "iteration-03-couverture.json", "iteration-03-revue.json",
             "iteration-03-decision.json", "iteration-03-contexte.json",
             "iteration-02-code-oss.json", "iteration-02-cadre-spring.json",
             "iteration-03-references.json", "iteration-02-preuves.json"]
    docs = {n: read(n) for n in names}
    contract, protocol = docs[names[0]], docs[names[1]]
    m1 = {docs[n]["ensemble"]: docs[n] for n in names[2:5]}
    m2 = docs[names[5]]
    coverage, review, decision, context = [docs[n] for n in names[6:10]]
    roles = contract["roles"]
    groups = ["COMMON", "REF", "STOCK"]
    checks = []

    def check(label, condition):
        checks.append({"label": label, "passed": bool(condition)})
        if not condition:
            raise AssertionError(label)

    def triplet(v):
        return (isinstance(v, list) and len(v) == 3 and
                all(isinstance(n, (int, float)) and not isinstance(n, bool) and math.isfinite(n) for n in v)
                and 0 <= v[0] <= v[1] <= v[2])

    check("Contrat et protocole figés avant comparaison", protocol["frozen_before_estimates"] and not m2["M1_consulted_before_freeze"])
    check("Neuf rôles uniques", len(roles) == len(set(roles)) == 9)
    packages = [p for lot in m1.values() for p in lot["packages"]]
    check("Identifiants de paquets uniques", len({p["id"] for p in packages}) == len(packages))
    check("Paquets : rôles connus et triplets ordonnés", all(
        p["effort"] and set(p["effort"]) <= set(roles) and all(triplet(v) for v in p["effort"].values())
        for p in packages))
    check("M2 : neuf rôles et triplets ordonnés par ensemble", all(
        set(m2["lots"][g]["roles"]) == set(roles) and all(triplet(r["jh"]) for r in m2["lots"][g]["roles"].values())
        for g in groups))
    calculated = {}
    for method in ["M1", "M2"]:
        lots = {}
        for g in groups:
            by_role = ({r: add(p["effort"].get(r, [0, 0, 0]) for p in m1[g]["packages"]) for r in roles}
                       if method == "M1" else {r: m2["lots"][g]["roles"][r]["jh"] for r in roles})
            total = add(by_role.values())
            frozen = (m1[g].get("frozen_total_jh", m1[g].get("total_jh")) if method == "M1"
                      else m2["lots"][g]["total_jh"])
            check(method + " " + g + " : somme égale au total figé", total == frozen)
            lots[g] = {"by_role": by_role, "total_jh": total, "financing_owner": g}
        overall_roles = {r: add(lots[g]["by_role"][r] for g in groups) for r in roles}
        total = add(lot["total_jh"] for lot in lots.values())
        check(method + " : conservation rôle / ensemble", add(overall_roles.values()) == total)
        calculated[method] = {"lots": lots, "by_role": overall_roles, "total_jh": total}
    check("M2 : somme globale égale au gel macro", calculated["M2"]["total_jh"] == m2["frozen_total_jh"])
    check("Variante expiration tenue hors base", add(m1["STOCK"]["variant"]["effort"].values()) == m1["STOCK"]["variant"]["frozen_total_jh"])
    check("Variante snapshot REF inconnue", m1["REF"]["variant"]["delta_jh"] is None)
    check("Aucune modification des chiffres en revue", review["numeric_estimates_changed"] is False)

    thresholds = protocol["materiality"]
    def compare(a, b, threshold):
        delta = b - a
        pct = 100 * delta / a if a else None
        return {"m1": a, "m2": b, "delta_jh": delta, "delta_pct": pct,
                "material": abs(pct) > threshold if pct is not None else b != 0,
                "zero_basis": a == 0}
    overall = compare(calculated["M1"]["total_jh"][1], calculated["M2"]["total_jh"][1], thresholds["total_relative_alert_pct"])
    cmp_lots = {g: compare(calculated["M1"]["lots"][g]["total_jh"][1], calculated["M2"]["lots"][g]["total_jh"][1], thresholds["total_relative_alert_pct"]) for g in groups}
    cmp_roles = {r: compare(calculated["M1"]["by_role"][r][1], calculated["M2"]["by_role"][r][1], thresholds["role_relative_alert_pct"]) for r in roles}
    cmp_details = {g: {r: compare(calculated["M1"]["lots"][g]["by_role"][r][1], calculated["M2"]["lots"][g]["by_role"][r][1], thresholds["role_relative_alert_pct"]) for r in roles} for g in groups}
    check("Écarts des ensembles réconciliés avec le global", sum(v["delta_jh"] for v in cmp_lots.values()) == overall["delta_jh"])

    grid = yaml.safe_load((ROOT / "source/grille-complexite.yaml").read_text(encoding="utf-8"))
    native = yaml.safe_load((ROOT / "sources/cartographie-scm-2026-10-24.yaml").read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in native["nodes"]}
    blocks = {b["capacite_id"]: b for b in grid["blocs"]}
    check("Cartographie : 88 capacités uniques", len(blocks) == len(grid["blocs"]) == 88)
    covered = set(contract["REF"]["capabilities"] + contract["STOCK"]["capabilities"])
    check("Six capacités partiellement étudiées", len(covered) == 6 and covered <= set(blocks))
    native_rows, financing = [], []
    for group in coverage["scope_groups"]:
        g = group["id"]
        owner = group["reporting_owner"]
        check(g + " : propriétaire natif connu", owner in nodes)
        if g != "COMMON":
            check(g + " : périmètre conforme au contrat", set(group["capability_refs"]) == set(contract[g]["capabilities"]) and set(group["function_refs"]) == set(contract[g]["native_functions"]))
            functions = {f["id"] for c in group["capability_refs"] for f in blocks[c]["fonctions"]}
            check(g + " : fonctions référencées présentes", set(group["function_refs"]) <= functions)
        for c in group["capability_refs"]:
            check(g + "/" + c + " : propriétaire dans le chemin natif", owner in blocks[c]["chemin"])
        financing.append({"id": g, "owner": owner, "beneficiary_refs": group["capability_refs"],
                          "total_jh": calculated["M1"]["lots"][g]["total_jh"],
                          "by_role": calculated["M1"]["lots"][g]["by_role"]})
    for c in sorted(covered):
        g = "REF" if c in contract["REF"]["capabilities"] else "STOCK"
        native_rows.append({"capability_ref": c, "label": nodes.get(c, {}).get("fields", {}).get("name", c),
                            "bc_ref": blocks[c]["id"], "path": blocks[c]["chemin"],
                            "financing_refs": [g, "COMMON"], "own_jh": None,
                            "status": "part_non_isolee"})
    rollups = []
    paths = {n: path[:i + 1] for b in blocks.values() for path in [b["chemin"]] for i, n in enumerate(path)}
    for node in sorted({x["owner"] for x in financing} | {b["chemin"][1] for c, b in blocks.items() if c in covered}):
        ids = [f["id"] for f in financing if node in paths.get(f["owner"], [f["owner"]])]
        unique = set(ids)
        total = add(calculated["M1"]["lots"][g]["total_jh"] for g in unique)
        rollups.append({"native_ref": node, "label": nodes.get(node, {}).get("fields", {}).get("name", node),
                        "level": nodes[node]["kind"], "financing_refs": sorted(unique), "studied_part_jh": total,
                        "full_unit_jh": None,
                        "by_role": {r: add(calculated["M1"]["lots"][g]["by_role"][r] for g in unique) for r in roles}})
    domain = next(x for x in rollups if x["native_ref"] == grid["domaine_id"])
    check("M3 : conservation au domaine, communs une seule fois", domain["studied_part_jh"] == calculated["M1"]["total_jh"])
    check("M3 : aucun JH propre inventé aux capacités", all(x["own_jh"] is None for x in native_rows))
    # Dependency union, including repeated references, must still fund each ensemble once.
    repeated = ["COMMON"] * 6 + ["REF"] * 2 + ["STOCK"] * 4
    check("M3 : bénéficiaires multiples sans duplication", add(calculated["M1"]["lots"][g]["total_jh"] for g in set(repeated)) == domain["studied_part_jh"])
    check("Sources d'entrée et paramètres inchangés", all((ROOT / p).is_file() and sha(ROOT / p) == h for p, h in context["source_hashes"].items()))

    refs = docs["iteration-03-references.json"]
    resolved = []
    for g in groups:
        for p in m1[g]["packages"]:
            for ref in p["proof_refs"]:
                target = m1[g].get("proof_catalog", {}).get(ref, ref)
                target = refs.get("package_overrides", {}).get(p["id"], {}).get(ref, refs.get("overrides", {}).get(target, target))
                file, _, pointer = target.partition("#")
                obj = docs.get(file) or read(file)
                if pointer:
                    if not pointer.startswith("/"):
                        raise ValueError("Use explicit JSON pointer: " + target)
                    for part in pointer[1:].split("/"):
                        part = part.replace("~1", "/").replace("~0", "~")
                        obj = obj[int(part)] if isinstance(obj, list) else obj[part]
                resolved.append({"package": p["id"], "reference": ref, "target": target})
    check("Références documentaires résolues", len(resolved) > 0)
    check("Les trois OSS ont un registre de lecture, pas de tests exécutés", all(
        p["code_read"] and not p["tests_executed"] for p in docs["iteration-02-code-oss.json"]["products"]))

    result = {"id": "iteration-03-resultats", "date": contract["date"], "unit": "JH",
              "provenance": context["producer"], "range_meaning": contract["uncertainty_rule"],
              "estimates": calculated, "comparison": {"overall": overall, "ensembles": cmp_lots,
              "roles": cmp_roles, "roles_by_ensemble": cmp_details,
              "sum_absolute_ensemble_deltas_jh": sum(abs(v["delta_jh"]) for v in cmp_lots.values()),
              "comparability": review["comparability"]},
              "native_reporting": {"financing": financing, "units": rollups, "capabilities": native_rows,
              "covered_capabilities_partial": len(covered), "unestimated_capabilities": len(blocks) - len(covered),
              "full_core_jh": None, "note": coverage["native_rollup"]},
              "effective_role_states": review["effective_role_states"],
              "resolved_proof_refs": resolved, "recommendation": decision["recommendation"],
              "market_method_status": {"COSMIC": "Taille fonctionnelle ; témoin limité en itération02, aucun décompte complet du panier ni conversion en JH ici.",
              "COCOMO_II": "Conditions de taille logique, adaptation et calibration non réunies ; aucun JH COCOMO inventé.",
              "ISBSG": "Données empiriques historiques, pas barème Spring par rôle applicable à ce panier.",
              "consequence": "La confrontation numérique des trois références reste incomplète. M1 et M2 sont deux hypothèses d'ingénierie, pas des substituts à cette validation."},
              "input_sha256": {n: sha(HERE / n) for n in names},
              "source_files_checked": len(context["source_hashes"]), "checks": checks}
    from iteration03_render import render
    report = render(result, docs)
    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.ids, self.links = [], []
        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if "id" in a:
                self.ids.append(a["id"])
            if tag == "a" and "href" in a:
                self.links.append(a["href"])
    parsed = Links()
    parsed.feed(report)
    if len(parsed.ids) != len(set(parsed.ids)):
        raise AssertionError("Duplicate HTML anchors")
    for url in parsed.links:
        parts = urlparse(url)
        if parts.scheme in ("http", "https"):
            continue
        if not parts.path and parts.fragment not in parsed.ids:
            raise AssertionError("Missing HTML anchor: " + url)
        if parts.path and parts.path not in {"iteration-03-resultats.json", "iteration-03.html"} and not (HERE / unquote(parts.path)).is_file():
            raise AssertionError("Missing local artifact: " + url)
    if "\ufffd" in report:
        raise AssertionError("Invalid Unicode replacement character")
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if (HERE / "iteration-03-resultats.json").read_text(encoding="utf-8") != encoded:
            raise AssertionError("Results differ from frozen inputs")
        if (HERE / "iteration-03.html").read_text(encoding="utf-8") != report:
            raise AssertionError("Report differs from computed results")
    else:
        (HERE / "iteration-03-resultats.json").write_text(encoded, encoding="utf-8")
        (HERE / "iteration-03.html").write_text(report, encoding="utf-8")
    if not all((HERE / file).is_file() for file in ["iteration-03-resultats.json", "iteration-03.html"]):
        raise AssertionError("Generated output missing")
    print(json.dumps({"checks": len(checks), "all_passed": all(c["passed"] for c in checks),
                      "html_links": len(parsed.links), "html_anchors": len(parsed.ids),
                      "mode": "check" if args.check else "write",
                      "M1": calculated["M1"]["total_jh"], "M2": calculated["M2"]["total_jh"],
                      "active_files_unchanged": result["source_files_checked"]}, ensure_ascii=True))

if __name__ == "__main__":
    main()
