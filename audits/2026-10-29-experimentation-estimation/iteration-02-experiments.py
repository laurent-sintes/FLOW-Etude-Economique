"""Reproduce isolated funnel diagnostics. Never writes source/ or config/.
The historical rate function below is deliberately naive and rejected for FLOW.
Run with --check to compare saved results without writing files.
"""
from pathlib import Path
from collections import Counter
from html import escape
from html.parser import HTMLParser
import argparse, hashlib, json, math, sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tmp/model-deps"))
import yaml

def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def esc(value):
    return escape(str(value), quote=True)

def table(headers, rows):
    return "<div class='table'><table><thead><tr>" + "".join("<th>" + esc(x) + "</th>" for x in headers) + "</tr></thead><tbody>" + "".join("<tr>" + "".join("<td>" + str(x) + "</td>" for x in row) + "</tr>" for row in rows) + "</tbody></table></div>"

def bullets(values):
    return "<ul>" + "".join("<li>" + esc(x) + "</li>" for x in values) + "</ul>"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    names = ["iteration-02-cadre-spring.json", "iteration-02-preuves.json", "iteration-02-pilotes.json", "iteration-02-contexte.json", "iteration-02-code-oss.json"]
    contract, refs, pilots, context, code = [read(n) for n in names]
    entries = {x["id"]: x for x in refs["entries"]}
    data = entries["ISBSG-2012"]["data"]
    checks = []
    def check(label, condition):
        checks.append({"label": label, "passed": bool(condition)})
        if not condition:
            raise AssertionError(label)

    # Boundary overlap is deliberately explicit for this rejected diagnostic.
    # At an exact shared endpoint, select the first published band.
    def naive_historical_hours(size):
        for band in data["bands"]:
            if size >= band["min"] and (band["max"] is None or size <= band["max"]):
                return size * data["interpolated_base"] * band["factor"]
        raise ValueError("Outside published size bands; no extrapolation.")

    example = naive_historical_hours(400)
    check("Reproduction de l'exemple publie 400 CFP / 6400 h", math.isclose(example, 6400))
    thresholds = []
    for threshold in [50, 100, 200, 300, 500, 1000]:
        before, after = threshold - 1, threshold + 1
        h1, h2 = naive_historical_hours(before), naive_historical_hours(after)
        thresholds.append({"threshold_cfp": threshold, "before_cfp": before, "after_cfp": after, "before_hours": round(h1, 6), "after_hours": round(h2, 6), "delta_pct": round(100 * (h2 - h1) / h1, 4), "effort_decreases": h2 < h1})
    check("La transposition mecanique revele les six sauts descendants", all(x["effort_decreases"] for x in thresholds))
    split = []
    for parts in [[400], [200, 200], [190, 210], [40] * 10]:
        hours = sum(naive_historical_hours(p) for p in parts)
        split.append({"parts_cfp": parts, "same_total_cfp": sum(parts), "naive_hours": round(hours, 6), "difference_pct": round(100 * (hours-example) / example, 4)})
    check("Le decoupage artificiel 2 x 200 modifie le resultat de 25 %", math.isclose(split[1]["difference_pct"], 25))
    check("Le biais existe aussi hors bornes de classe", split[2]["difference_pct"] != 0)
    micro_rejected = False
    try:
        naive_historical_hours(3)
    except ValueError:
        micro_rejected = True
    check("La consultation de 3 CFP n'est pas extrapolee hors plage", micro_rejected)

    grid = yaml.safe_load((ROOT / "source/grille-complexite.yaml").read_text(encoding="utf-8"))["blocs"]
    by_cap = {x["capacite_id"]: x for x in grid}
    native_functions = {f["id"] for b in grid for f in b["fonctions"]}
    scope_counts = {"capabilities": len(grid), "business_areas": len({b["chemin"][2] for b in grid}), "subdomains": len({b["chemin"][1] for b in grid})}
    reference_blocks = [b for b in grid if b["chemin"][1] == "business-references"]
    ba_counts = dict(sorted(Counter(b["chemin"][2] for b in reference_blocks).items()))
    check("Le constat BC vers BA est calcule depuis la cartographie", len(reference_blocks) == 6 and len(ba_counts) == 6 and set(ba_counts.values()) == {1})
    role_ids = {r["id"] for r in contract["roles"]}
    owner_ids = [x["id"] for x in pilots["shared_owners"]]
    check("Chaque financement commun a un identifiant unique", len(owner_ids) == len(set(owner_ids)))
    for p in pilots["families"]:
        check(p["id"] + " : rattachements natifs existants", all(c in by_cap for c in p["native_capability_refs"]))
        check(p["id"] + " : fonctions natives existantes", set(p["native_function_refs"]) <= native_functions)
        check(p["id"] + " : dependances communes referencees", set(p["common_owner_refs"]) <= set(owner_ids))
        check(p["id"] + " : roles complets mais efforts inconnus conserves", set(p["jh_by_role"]) == role_ids and all(v is None for v in p["jh_by_role"].values()) and p["complete_jh"] is None)
        check(p["id"] + " : aucun petit comptage presente comme complet", p["size"]["complete_value"] is None)
    check("Aucune voie annonce des JH FLOW calculables aujourd'hui", all(not r["flow_jh_available"] for r in refs["routes"]))
    check("Les trois OSS complementaires ont une inspection de code explicite", {p["id"] for p in code["products"]} == {"odoo", "tryton", "axelor"} and all(p["code_read"] and p["evidence"] for p in code["products"]))
    check("Aucune execution des tests produits n'est pretendue", all(p["tests_executed"] is False for p in code["products"]))
    source_changed = [name for name, before in context["active_source_hashes_before"].items() if not (ROOT / name).is_file() or sha(ROOT / name) != before]
    result = {
        "schema_version": 1, "iteration": "02", "date": context["date"],
        "nature": "Controles de methode et instruction de code ; pas une estimation du budget FLOW.",
        "checks": checks, "checks_passed": len(checks),
        "active_source_hashes_changed_since_capture": source_changed,
        "input_sha256": {n: sha(HERE / n) for n in names},
        "naive_historical_rate_test": {
            "source_ref": "ISBSG-2012", "formula_for_diagnostic_only": "H = S * 20 * facteur_de_bande",
            "endpoint_convention": "Premier intervalle publie contenant la borne ; 200 affecte a 100-200. Les essais 199/201 et 190/210 ne dependent pas de cette convention.",
            "units": "heures historiques ; aucune conversion en JH FLOW",
            "example_400_cfp_hours": example, "thresholds": thresholds, "artificial_split": split,
            "decision": "Rejeter l'automatisation de cette transposition par bandes. Ni erreur de la base ISBSG ni preuve de maille optimale FLOW.",
            "three_cfp_not_used_for_effort": micro_rejected
        },
        "native_scope_counts": scope_counts, "reference_capabilities_per_ba": ba_counts,
        "flow_estimate": {"full_jh": None, "jh_by_role": {r: None for r in sorted(role_ids)}, "status": "non_etabli"},
        "progress": context["progress"],
        "source_code_review": {"products": [p["id"] for p in code["products"]], "scope": "Deux familles d'apprentissage ; inspection partielle, pas audit exhaustif des produits."},
        "next_action": context["next_action"],
    }

    blocks = []
    blocks.append("<header><p>FLOW · Étude d’opportunité · 29 octobre 2026</p><h1>Itération 02 — Spring, preuves et maille d’évaluation</h1><p>Premier passage de l’entonnoir. Résultats expérimentaux séparés des sources économiques.</p></header>")
    blocks.append("<section class='lead'><h2>Ce que ce passage établit</h2><p><strong>Le cadre est défini, les références sont triées et les trois comparables OSS ont été inspectés sur les deux familles pilotes.</strong> La maille candidate est un ensemble fonctionnel cohérent relié aux unités métier natives. Aucun total de JH FLOW ni optimum de précision n’est encore démontré.</p><p>La chaîne à instruire est : capacité → fonctions observées dans le code → mécanismes et dépendances → réutilisation Spring → travaux restants → JH par rôle.</p></section>")
    blocks.append("<nav><a href='#code'>Code des OSS</a><a href='#contrat'>Cadre Spring</a><a href='#essais'>Essais</a><a href='#pilotes'>Pilotes</a><a href='#preuves'>Références</a><a href='#suite'>Décisions et suite</a></nav>")
    blocks.append("<section id='code'><h2>Ce qui a réellement été lu dans le code</h2><p>" + esc(code["scope_note"]) + "</p>")
    for p in code["products"]:
        blocks.append("<h3>" + esc(p["name"]) + "</h3><p><strong>Commit(s) :</strong> " + esc(" ; ".join(p["commits"])) + "</p><p>" + esc(p["finding"]) + "</p><p><strong>Conséquence pour Spring :</strong> " + esc(p["spring_implication"]) + "</p>")
        blocks.append(table(["Pièce de code", "Observation"], [[f"<a href='{esc(e['url'])}'>{esc(e['label'])}</a>", esc(e["finding"])] for e in p["evidence"]]))
        blocks.append("<p><strong>Limites :</strong> " + esc(p["limits"]) + "</p>")
    blocks.append(table(["Aspect", "Odoo", "Tryton", "Axelor", "Conséquence"], [[esc(x["aspect"]),esc(x["odoo"]),esc(x["tryton"]),esc(x["axelor"]),esc(x["implication"])] for x in code["comparison"]]))
    blocks.append("<h3>Profil de complexité issu des preuves</h3><p>" + esc(code["complexity_model_candidate"]["principle"]) + "</p>")
    blocks.append(table(["Dimension observable", "Appuis", "Effet sur les travaux"], [[esc(x["dimension"]),esc(x["evidence"]),esc(x["effect_on_work"])] for x in code["complexity_model_candidate"]["dimensions"]]))
    blocks.append("<p>" + esc(code["complexity_model_candidate"]["conversion_rule"]) + "</p>")
    blocks.append("<p>La présence de tests dans les dépôts est une preuve de scénarios décrits. Ces tests n’ont pas été exécutés ici ; ni performance ni couverture exhaustive ne sont annoncées.</p></section>")

    blocks.append("<section id='contrat'><h2>Cadre de l’expérience Spring</h2><p>" + esc(contract["purpose"]) + "</p>")
    blocks.append(table(["Frontière", "Règle"], [[esc(x["name"]), esc(x["rule"])] for x in contract["boundaries"]]))
    tb = contract["technical_baseline"]
    blocks.append("<h3>Instantané technique</h3><p><strong>Java 21 / Spring Boot 3.5.7.</strong> " + esc(tb["nature"]) + "</p><p>" + esc(tb["architecture_hypothesis"]) + "</p>")
    blocks.append(table(["Composant", "Version"], [[esc(k), esc(v)] for k,v in tb["versions"]]))
    blocks.append("<p><strong>À figer avant un essai exécuté :</strong> " + esc(", ".join(tb["open_versions"])) + ".</p>")
    blocks.append(table(["Patrimoine proposé", "Travaux restants"], [[esc(x["component"]), esc(x["residual"])] for x in tb["reuse"]]))
    blocks.append("<h3>Activités et rôles</h3><p>Convention expérimentale : <strong>7 h par JH</strong>. " + esc(contract["role_rule"]) + "</p>")
    blocks.append(table(["Contribution", "Travaux à dimensionner", "JH actuels"], [[esc(r["name"]), esc(r["work"]), "Inconnus"] for r in contract["roles"]]))
    blocks.append("<p>" + esc(contract["effort_convention"]["warning"]) + "</p>")
    blocks.append("<h3>Frontière Core / intégration</h3><p>Les comportements standards et garanties génériques sont dans le Core. Les règles propres au Groupe, mappings de ses applications, reprises et déploiements clients restent à part.</p>")
    blocks.append(bullets(contract["effort_convention"]["separate_or_excluded"]))
    blocks.append("<h3>Calcul attendu</h3>" + bullets(contract["formulas"]) + "<p>" + esc(contract["unknowns_policy"]) + "</p></section>")

    blocks.append("<section id='essais'><h2>Essais de transposition : deux usages éliminés</h2><p>Le rapport historique <a href='" + esc(entries["ISBSG-2012"]["url"]) + "#page=12'>ISBSG/COSMIC 2012, tableaux 7–8</a> est un contrepoint. Nous testons ici ce qui arrive si ses bandes indicatives deviennent une formule automatique : <code>H = taille × 20 × facteur de bande</code>. Ces tailles sont des témoins de contrôle, pas des tailles FLOW.</p>")
    blocks.append("<h3>Franchir une classe fait artificiellement baisser l’effort</h3>")
    blocks.append(table(["Taille avant → après", "Heures avant → après", "Variation"], [[f"{x['before_cfp']} → {x['after_cfp']} CFP", f"{x['before_hours']:g} → {x['after_hours']:g} h", f"{x['delta_pct']:.2f} %"] for x in thresholds]))
    blocks.append("<p>Décision : ce barème par paliers ne devient pas un calcul de production. Aucun lissage arbitraire n’est ajouté pour le rendre acceptable.</p><h3>Découper le même projet change le résultat</h3>")
    blocks.append(table(["Découpage artificiel", "Heures calculées", "Écart au projet de 400 CFP"], [[esc(" + ".join(map(str,x["parts_cfp"]))) + " CFP", f"{x['naive_hours']:g} h", f"{x['difference_pct']:.2f} %"] for x in split]))
    blocks.append("<p>Pour le témoin 2 × 200, 200 est affecté à la classe 100–200. Le témoin 190 + 210 évite cette convention de borne et montre également un écart. Ces essais mettent en défaut une transposition naïve ; ils ne mettent pas en défaut les observations ISBSG et ne sélectionnent pas la bonne maille FLOW.</p>")
    blocks.append("<p>Le témoin ERPNext de <strong>3 CFP</strong> reste une consultation partielle. Il est hors de la plage publiée et n’est pas multiplié par un taux projet.</p></section>")

    blocks.append("<section id='pilotes'><h2>Deux ensembles pilotes et trois mailles candidates</h2>")
    blocks.append("<p>La capture contient " + str(scope_counts["capabilities"]) + " capacités, " + str(scope_counts["business_areas"]) + " Business Areas et " + str(scope_counts["subdomains"]) + " sous-domaines. Dans Operational References, les six capacités sont réparties dans six Business Areas : passer de BC à BA ne change pas la décomposition.</p>")
    blocks.append(table(["Maille", "Utilité", "Limite"], [[esc(m["name"]),esc(m["use"]),esc(m["limitation"])] for m in pilots["granularity_candidates"]]))
    for p in pilots["families"]:
        blocks.append("<h3>" + esc(p["name"]) + "</h3><p>" + esc(p["purpose"]) + "</p><p><strong>Capacités :</strong> " + esc(", ".join(p["native_capability_refs"])) + ". <strong>Lot propriétaire :</strong> " + esc(p["software_owner"]) + ".</p>")
        blocks.append("<p><strong>Sous-ensemble comparable :</strong></p>" + bullets(p["comparable_subset"]))
        blocks.append("<p><strong>Travaux résiduels à instruire :</strong></p>" + bullets(p["residual_work"]))
        blocks.append("<p><strong>Encore ouvert :</strong></p>" + bullets(p["noncovered_or_open"]))
        blocks.append("<p><strong>Décision :</strong> " + esc(p["decision"]) + "</p>")
    blocks.append("<h3>Financement commun, compté une seule fois</h3>")
    blocks.append(table(["Propriétaire", "Bénéficiaires", "État"], [[esc(s["id"]),esc(", ".join(s["beneficiaries"])),esc(s["status"])] for s in pilots["shared_owners"]]))
    blocks.append("<p>" + esc(pilots["comparison_rule"]) + "</p></section>")

    blocks.append("<section id='preuves'><h2>Admission des références</h2><p>" + esc(refs["search"]["conclusion"]) + "</p>")
    blocks.append(table(["Référence", "Usage", "Limites"], [[f"<a href='{esc(r['url'])}'>{esc(r['title'])}</a><br><small>{esc(r['locator'])}</small>", esc(r["decision"]) + "<br>" + esc(r["supports"]), esc(r["limit"])] for r in refs["entries"]]))
    blocks.append(table(["Voie", "Calcul actuellement possible", "Entrées manquantes"], [[esc(r["name"]),esc(r["computable"]),bullets(r["required"])] for r in refs["routes"]]))
    blocks.append("</section><section id='suite'><h2>Décisions et suite de l’entonnoir</h2>")
    blocks.append(table(["Étape", "État", "Condition"], [[esc(x["id"]),esc(x["state"]),esc(x["gate"])] for x in context["progress"]]))
    blocks.append(table(["Décision", "Objet", "Motif"], [[esc(x["decision"]),esc(x["subject"]),esc(x["reason"])] for x in context["decisions"]]))
    blocks.append("<p><strong>Prochain passage :</strong> " + esc(context["next_action"]) + "</p><p>Aucun bilan interne n’est disponible à ce jour. La voie d’ingénierie devra porter ses propres hypothèses explicites ; l’accord entre deux méthodes ne remplacera pas des efforts réels comparables.</p>")
    blocks.append("<h3>Reproduction et contrôles</h3><p>" + "__CHECK_COUNT__" + " contrôles de cohérence de cette expérience réussis. Cela ne valide ni la précision des estimations ni les logiciels inspectés.</p><p>Script : <a href='iteration-02-experiments.py'>iteration-02-experiments.py</a> ; résultats : <a href='iteration-02-resultats.json'>iteration-02-resultats.json</a>. Le paramètre <code>--check</code> recalcule sans écrire.</p>")
    blocks.append("<p>" + ("Les empreintes des 88 fichiers source/config et de capture contrôlés sont inchangées depuis le relevé de ce cycle." if not source_changed else "Des sources ont changé depuis le relevé : " + esc(", ".join(source_changed)) + ". Réexaminer les dépendances avant réutilisation.") + "</p>")
    blocks.append("<p>" + esc(context["time_note"]) + " Fenêtre enregistrée : " + esc(context["tracked_from_utc"]) + " → " + esc(context["tracked_until_utc"]) + ".</p>")
    blocks.append("<p>Analyse assistée par IA, sans revue humaine déclarée. Les JH et budgets actifs n’ont pas été recalibrés. Le plan initial et le rapport précédent restent conservés.</p></section>")

    style = "body{margin:0;background:#FAF8F4;color:#182632;font:16px/1.6 'Segoe UI',Arial,sans-serif}main{max-width:1120px;margin:auto;padding:24px}header{background:#236159;color:white;padding:30px;border-radius:12px}h1{line-height:1.2;font-size:32px}h2{font-size:25px;border-bottom:2px solid #D9F2EA;padding-bottom:8px}h3{margin-top:30px}section{background:white;padding:26px;margin:24px 0;border-radius:10px}.lead{background:#D9F2EA}nav{display:flex;flex-wrap:wrap;gap:18px;margin:22px 0}a{color:#236159}a:focus{outline:3px solid #C24F00}table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;vertical-align:top;border:1px solid #d6dedb;padding:10px}th{background:#F4F8F6}small{color:#45525A}.table{overflow-x:auto}code{background:#FFF0DB;padding:3px}li{margin:5px 0}@media print{body{background:white}main{padding:0}section{break-inside:auto}nav{display:none}header{color:#182632;background:white}tr{break-inside:avoid}}"
    html = "<!doctype html><html lang='fr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>FLOW — Itération 02 Spring</title><style>" + style + "</style></head><body><main>" + "".join(blocks) + "</main></body></html>"
    HTMLParser().feed(html)
    check("Le rapport conserve les accents sans caractere de remplacement", "\ufffd" not in html and "Ã©" not in html)
    html = html.replace("__CHECK_COUNT__", str(len(checks)))
    result["checks"] = checks
    result["checks_passed"] = len(checks)
    if args.check:
        check("Les resultats sauvegardes sont reproductibles", read("iteration-02-resultats.json") == result)
        expected = (HERE / "iteration-02.html").read_text(encoding="utf-8")
        check("Le rapport sauvegarde est reproductible", expected == html)
        print(json.dumps({"mode":"check","checks_passed":len(checks),"source_changes":source_changed}))
    else:
        (HERE / "iteration-02-resultats.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        (HERE / "iteration-02.html").write_text(html,encoding="utf-8")
        print(json.dumps({"mode":"write","checks_passed":len(checks),"source_changes":source_changed,"report":str(HERE / "iteration-02.html")}))
if __name__ == "__main__":
    main()
