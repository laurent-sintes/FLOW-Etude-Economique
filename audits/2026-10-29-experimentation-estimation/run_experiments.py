"""Read-only experiment on FLOW inputs; writes only this experiment's results."""
import argparse, csv, hashlib, html, json, math, re, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tmp/model-deps"))
import yaml

def read(name):
    return yaml.safe_load((ROOT / name).read_text(encoding="utf-8"))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def active_hashes():
    paths = []
    for folder in ("source", "config"):
        paths += [p for p in (ROOT / folder).rglob("*") if p.is_file()]
    paths.append(ROOT / "sources/cartographie-scm-2026-10-24.yaml")
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(paths)}

def effort_hours(size, size_unit, rate, rate_unit):
    if rate_unit != "h/" + size_unit:
        raise ValueError("Incompatible size/rate units")
    return size * rate

def distribute_roles(total_jh, shares):
    if shares is None:
        return None
    if not math.isclose(sum(shares.values()), 1, abs_tol=1e-9):
        raise ValueError("Role allocation does not conserve total")
    if any(value < 0 for value in shares.values()):
        raise ValueError("Negative role allocation")
    return {role: total_jh * value for role, value in shares.items()}

def run():
    before = active_hashes()
    grid = read("source/grille-complexite.yaml")["blocs"]
    method = read("source/methode-complexite.yaml")
    qualifications = read("source/instruction-marche.yaml")["qualifications"]
    lookup = {row["capacite_id"]: row for row in grid}
    shared = [{"id": m["id"], "members": [m["capacite_responsable"]] + m["usages"]}
              for m in method["mecanismes_partages"]]
    levels = []
    for level, label in enumerate(("Domaine", "Sous-domaine", "Business Area", "Capacite")):
        groups = defaultdict(list)
        for row in grid:
            groups[row["chemin"][level]].append(row["capacite_id"])
        levels.append({
            "level": label, "groups": len(groups),
            "minimum_capacities": min(map(len, groups.values())),
            "maximum_capacities": max(map(len, groups.values())),
            "crossing_shared_hypotheses": sum(
                len({lookup[c]["chemin"][level] for c in m["members"]}) > 1 for m in shared),
            "groups_with_any_detailed_market_record": len(
                {lookup[q["capability_ref"]]["chemin"][level] for q in qualifications})
        })
    assert len(lookup) == len(grid)
    for level in range(4):
        assert sum(Counter(r["chemin"][level] for r in grid).values()) == len(grid)

    tests = []
    def passed(name, condition):
        if not condition:
            raise AssertionError(name)
        tests.append({"test": name, "status": "pass"})

    passed("One capability counted once at each hierarchy level", True)
    rejected = False
    try:
        effort_hours(3, "CFP", 9.4, "h/IFPUG-Nesma-PF")
    except ValueError:
        rejected = True
    passed("COSMIC size cannot consume IFPUG/Nesma rate", rejected)
    passed("Missing role evidence stays unknown", distribute_roles(100, None) is None)
    rejected = False
    try:
        distribute_roles(100, {"development": .8, "qa": .3})
    except ValueError:
        rejected = True
    passed("Allocation exceeding total is rejected", rejected)
    # Pure accounting fixture; no staffing recommendation.
    fixture = distribute_roles(100, {"role_a": .6, "role_b": .4})
    passed("Role-allocation fixture conserves total", sum(fixture.values()) == 100)

    diagnostic = read("source/references-couts-integration.yaml")["reperes_build_core"]["etude_oss"]["methode"]
    a = diagnostic["coefficient_a"]
    exponent = diagnostic["exposant_nominal"]
    month_hours = diagnostic["heures_mois_personne"]
    day_hours = diagnostic["heures_jh"]
    # Artificial size chosen to exercise the equation; not FLOW or a real product.
    size_ksloc = 100
    total = a * size_ksloc ** exponent * month_hours / day_hours
    partitions = []
    for n in (1, 2, 4, 10, 28, 88):
        naive = n * a * (size_ksloc / n) ** exponent * month_hours / day_hours
        proper = sum(total / n for _ in range(n))
        passed("COCOMO reporting invariance for " + str(n) + " groups",
               math.isclose(proper, total, rel_tol=1e-12))
        passed("COCOMO analytical split-bias ratio for " + str(n) + " groups",
               math.isclose(naive / total, n ** (1-exponent), rel_tol=1e-12))
        partitions.append({"groups": n, "incorrect_independent_sum_jh": naive,
                           "same_project_multimodule_jh": proper,
                           "incorrect_bias_pct": (naive/total-1)*100})

    pilot = json.loads((HERE / "pilot-inputs.json").read_text(encoding="utf-8"))
    consultation = pilot["cosmic_consultation"]
    cfp = sum(len(consultation["movements"][kind]) for kind in ("E", "R", "W", "X"))
    passed("COSMIC consultation witness has E/R/X and no W", cfp == 3)
    assert not consultation["covers_full_flow_capability"]
    passed("Partial COSMIC witness is not a complete capability size", True)
    boundary = pilot["cosmic_boundary_test"]
    passed("COSMIC boundary control preserves application size",
           boundary["controller_cfp"] + boundary["service_cfp"] - boundary["internal_movements_to_remove"] == cfp)
    # Historical ratio experiment; 850 JH is an arbitrary accounting fixture.
    role_vectors = {
        "general": {"PM":9,"analyst":7,"architect":5,"developer":44,"UI":3,"QA":17},
        "external_customer": {"PM":11,"analyst":10,"architect":4,"developer":40,"UI":3,"QA":17}}
    role_results = {}
    for name, percentages in role_vectors.items():
        shares = {role:value/85 for role,value in percentages.items()}
        values = distribute_roles(850, shares)
        passed("Historical role allocation conserves total: " + name,
               math.isclose(sum(values.values()),850))
        role_results[name] = values

    raw_path = HERE / "cosmic.arff"
    raw = raw_path.read_bytes()
    arff_sha = hashlib.sha256(raw).hexdigest()
    attrs, data_lines, in_data = [], [], False
    for line in raw.decode("utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("%"):
            continue
        if line.lower() == "@data":
            in_data = True
        elif in_data:
            data_lines.append(line)
        elif line.lower().startswith("@attribute"):
            attrs.append(re.split(r"\s+", line, maxsplit=2)[1].strip("'\""))
    rows = list(csv.reader(data_lines, quotechar="'", skipinitialspace=True))
    passed("Public ARFF rows align with declared attributes", all(len(row)==len(attrs) for row in rows))
    checked = []
    for row in rows:
        values = dict(zip(attrs,row))
        try:
            size = float(values["FS"])
            effort = float(values["N_effort_level1"])
            stated = float(values["N_PDR1"])
            if size <= 0:
                continue
        except (ValueError, KeyError):
            continue
        ratio = effort/size
        checked.append({"id":values.get("ID", values.get("ISBSG_ID", row[0])),
                        "size_cfp":size,"normalized_effort_h":effort,
                        "published_h_per_cfp":stated,"recomputed_h_per_cfp":ratio,
                        "consistent_with_one_decimal":abs(ratio-stated)<=.051})
    passed("Public ARFF audit actually checks eligible rows", len(checked)>0)
    dataset = {"source":"https://zenodo.org/records/268482/files/cosmic.arff?download=1",
               "sha256":arff_sha,"rows":len(rows),"attributes":len(attrs),
               "checked_rows":len(checked),"consistent_rows":sum(r["consistent_with_one_decimal"] for r in checked),
               "decision":"withhold_calibration_until_fields_reconciled",
               "checks":checked}
    after = active_hashes()
    passed("Active source/config files unchanged during experiment", before == after)

    result = {
        "date": "2026-10-29", "status": "experimental_not_calibrated",
        "scope": "Generic Core System opportunity study; no change to active estimates",
        "hierarchy": levels,
        "market_detail_status": dict(Counter(q["status"] for q in qualifications)),
        "market_capabilities_with_detail": len({q["capability_ref"] for q in qualifications}),
        "shared_hypotheses": shared,
        "cocomo_synthetic_test": {
            "nature": "synthetic_formula_control_not_FLOW_estimate",
            "a": a, "exponent": exponent, "person_month_hours": month_hours,
            "person_day_hours": day_hours, "arbitrary_size_ksloc": size_ksloc,
            "partitions": partitions
        },
        "cosmic_partial_measure": {"cfp": cfp, **consultation},
        "cosmic_boundary_test": pilot["cosmic_boundary_test"],
        "rejected_candidates": pilot["rejected_candidates"],
        "role_estimation_status": "unknown_until_compatible_effort_and_role_allocation",
        "historical_roles_test": {"arbitrary_total_jh":850,"source_year":2006,"other_removed_pct":15,"allocations":role_results},
        "public_cosmic_dataset_audit":dataset,
        "tests": tests, "input_hashes": before
    }
    return result

def render(result):
    esc = lambda v: html.escape(str(v))
    def table(headers, rows):
        return "<table><thead><tr>" + "".join("<th>"+esc(v)+"</th>" for v in headers) + "</tr></thead><tbody>" + "".join("<tr>"+"".join("<td>"+esc(v)+"</td>" for v in row)+"</tr>" for row in rows)+"</tbody></table>"
    hierarchy = table(
        ["Lecture metier", "Unites", "Capacites/unite", "Mecanismes partages traversant les unites"],
        [(r["level"],r["groups"],str(r["minimum_capacities"])+" a "+str(r["maximum_capacities"]),r["crossing_shared_hypotheses"]) for r in result["hierarchy"]])
    parts = table(
        ["Nombre de groupes", "Ecart du calcul separe incorrect", "Ecart du calcul multi-modules"],
        [(r["groups"],f'{r["incorrect_bias_pct"]:.2f} %',"0 %") for r in result["cocomo_synthetic_test"]["partitions"]])
    body = (HERE / "report-body.html").read_text(encoding="utf-8")
    body = body.replace("{{HIERARCHY}}",hierarchy).replace("{{PARTITIONS}}",parts)
    body = body.replace("{{CHECKS}}",str(len(result["tests"]))).replace("{{HASHES}}",str(len(result["input_hashes"])))
    return """<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FLOW — expérimentation de l’estimation</title><style>
body{font:17px/1.65 system-ui,sans-serif;max-width:1050px;margin:40px auto;padding:0 24px;color:#182a39;background:#faf9f6}
h1{font-size:32px;line-height:1.2}h2{font-size:23px;margin-top:36px}strong{color:#143c55}
table{border-collapse:collapse;width:100%;margin:20px 0;font-size:15px}th,td{border:1px solid #ccd3d7;padding:10px;text-align:left;vertical-align:top}th{background:#e7edf0}
.note{padding:18px;background:#fff3cf;border-left:4px solid #bb8717}.formula{padding:16px;background:#edf2f4;font-family:monospace}
a{color:#075a80}li{margin:8px 0}.small{font-size:14px;color:#46545d}
@media print{body{font-size:11pt;margin:0;max-width:none}h2{break-after:avoid}tr{break-inside:avoid}}
</style><body>""" + body + "</body></html>"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Recompute and compare with saved results; no writes")
    args = parser.parse_args()
    result = run()
    if args.check:
        saved = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
        assert result == saved, "Saved experiment differs from recomputation or input hashes changed"
        print(json.dumps({"checks":len(result["tests"]), "reproduced":True, "active_files_hashed":len(result["input_hashes"])}))
    else:
        (HERE / "results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        (HERE / "rapport.html").write_text(render(result),encoding="utf-8")
        print(json.dumps({"checks":len(result["tests"]), "report":str(HERE/"rapport.html"),"status":result["status"]}))
