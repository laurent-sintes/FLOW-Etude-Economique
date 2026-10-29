"""French audit report, rendered only from the isolated iteration 03 files."""
from html import escape

LABELS = {"analyse_produit":"Analyse produit et fonctionnelle", "architecture":"Architecture",
          "dev_java":"Développement Java / Spring", "dev_frontend":"Développement des interfaces",
          "ux":"Conception des interactions (UX)", "qa":"QA indépendante",
          "plateforme":"Environnement et chaîne de livraison", "securite":"Expertise sécurité",
          "coordination":"Coordination technique"}
GROUPS = {"COMMON":"Socle commun aux deux pilotes", "REF":"Références produits / variantes",
          "STOCK":"Positions de stock / réservations"}
def e(v):
    return escape(str(v), quote=True)
def n(v):
    return f"{v:g}".replace(".", ",")
def pct(v):
    return "base nulle" if v is None else f"{v:+.1f} %".replace(".", ",")
def span(v):
    return n(v[0]) + " – " + n(v[2])
def ul(values):
    return "<ul>" + "".join("<li>" + e(v) + "</li>" for v in values) + "</ul>"
def table(headers, rows):
    return "<div class='scroll'><table><thead><tr>" + "".join("<th scope='col'>" + e(h) + "</th>" for h in headers) + "</tr></thead><tbody>" + "".join("<tr>" + "".join("<td>" + str(c) + "</td>" for c in row) + "</tr>" for row in rows) + "</tbody></table></div>"
def paragraph(value):
    return "<p>" + e(value) + "</p>"

def render(result, docs):
    contract = docs["iteration-03-contrat.json"]
    review = docs["iteration-03-revue.json"]
    decision = docs["iteration-03-decision.json"]
    coverage = docs["iteration-03-couverture.json"]
    code = docs["iteration-02-code-oss.json"]
    roles = contract["roles"]
    groups = ["COMMON", "REF", "STOCK"]
    m1, m2 = result["estimates"]["M1"], result["estimates"]["M2"]
    comp = result["comparison"]
    main = []
    main.append("<header><p class='eyebrow'>FLOW · ÉTUDE D’OPPORTUNITÉ · 29 OCTOBRE 2026</p><h1>Itération 03 — premiers JH par rôle</h1><p>Deux ensembles fonctionnels bornés, un socle commun et deux estimations conservées séparément.</p></header>")
    main.append("<section id='resultat'><h2>Un premier chiffrage traçable, une précision encore à établir</h2>")
    main.append(f"<div class='key'><strong>{n(m1['total_jh'][1])} JH centraux</strong><p>Plage de sensibilité : {span(m1['total_jh'])} JH pour le panier expérimental. Ce montant ne chiffre ni les six capacités complètes ni le Core System.</p></div>")
    main.append("<p>La base détaillée M1 additionne les travaux à réaliser avec Spring, par rôle. Le code des produits du marché justifie des mécanismes et des dépendances ; les durées restent des hypothèses d’ingénierie assistées par IA, sans effort de projet comparable observé.</p>")
    main.append(f"<p>Le contrepoint global M2 aboutit à <strong>{n(m2['total_jh'][1])} JH</strong> ({span(m2['total_jh'])}). L’écart net de {n(comp['overall']['delta_jh'])} JH, soit {pct(comp['overall']['delta_pct'])}, masque des écarts opposés entre ensembles. Cet accord global ne valide pas la précision.</p>")
    main.append("<p><strong>Décision : poursuivre une itération ciblée.</strong> Stabiliser les garanties et les responsabilités, puis éprouver deux difficultés techniques. Ne pas produire une troisième estimation globale pour rechercher un accord.</p></section>")

    main.append("<section id='jh'><h2>JH par rôle : base détaillée M1</h2><p>Contributions, pas effectifs : une personne peut tenir plusieurs rôles. Les tests développeur et la revue de code sont compris dans le développement ; la QA est indépendante. Convention : 7 heures par JH.</p>")
    rows = []
    for r in roles:
        vals = [n(m1["lots"][g]["by_role"][r][1]) for g in groups]
        if r == "plateforme":
            vals[2] = "0 · inclus dans le commun"
        if r == "securite":
            vals[2] = "0 · sans revue spécialisée distincte"
        rows.append([e(LABELS[r])] + vals + ["<strong>" + n(m1["by_role"][r][1]) + "</strong>", span(m1["by_role"][r])])
    rows.append(["<strong>Total du panier</strong>"] + ["<strong>" + n(m1["lots"][g]["total_jh"][1]) + "</strong>" for g in groups] + ["<strong>" + n(m1["total_jh"][1]) + "</strong>", span(m1["total_jh"])])
    main.append(table(["Rôle","Socle commun","Références","Stock","Total central · JH","Bas – haut · JH"], rows))
    main.append("<p>La sécurité du stock est vérifiée par développement et QA dans M1. COMMON finance sa propre revue initiale ; il ne finance pas implicitement une revue spécialisée du stock. Cette dernière est prévue dans M2 et reste une décision d’organisation à prendre.</p>")
    main.append("<p>Bas, central et haut gardent le même périmètre. Ce sont des scénarios de sensibilité, pas des percentiles ni un intervalle de confiance. Les demi-journées viennent des additions ; elles ne constituent pas une précision démontrée.</p>")
    main.append("<div class='formula'>JH d’un rôle = somme de ses travaux financés une fois.<br>Coût à terme = somme des JH de chaque rôle × son tarif en € HT / JH.</div><p>Aucune valorisation en euros à cette étape : il faut d’abord stabiliser les responsabilités et qualifier les tarifs. Les JH ne donnent pas directement un délai calendaire.</p></section>")

    main.append("<section id='ecarts'><h2>La proximité du total masque les décisions à résoudre</h2>")
    rows = []
    for g in groups:
        v = comp["ensembles"][g]
        rows.append([e(GROUPS[g]), n(v["m1"]) + " · " + span(m1["lots"][g]["total_jh"]),
                     n(v["m2"]) + " · " + span(m2["lots"][g]["total_jh"]),
                     n(v["delta_jh"]), pct(v["delta_pct"]), "À expliquer" if v["material"] else "Sous le seuil de pilotage"])
    main.append(table(["Ensemble","M1 central · bas–haut","M2 central · bas–haut","Écart JH","Écart relatif","Lecture"], rows))
    main.append(f"<p>La somme des écarts absolus entre ensembles atteint {n(comp['sum_absolute_ensemble_deltas_jh'])} JH, tandis que leur compensation laisse seulement {n(comp['overall']['delta_jh'])} JH au total. Ce diagnostic n’ajoute aucun budget.</p>")
    main.append(paragraph(review["comparability"]))
    rows = []
    for r in roles:
        v = comp["roles"][r]
        rows.append([e(LABELS[r]), n(v["m1"]), n(v["m2"]), pct(v["delta_pct"]),
                     "À expliquer" if v["material"] else "Sous le seuil"])
    main.append(table(["Rôle · total panier","M1 JH","M2 JH","Écart relatif","Lecture"], rows))
    main.append("<p>Seuils annoncés avant comparaison : plus de 15 % par ensemble ou 25 % par rôle. Ce sont des alertes de pilotage, pas des objectifs de précision. Calcul : 100 × (M2 − M1) / M1 ; si M1 est nul, présence et différence absolue remplacent le pourcentage.</p>")
    rows = []
    for g in groups:
        for r in roles:
            v = comp["roles_by_ensemble"][g][r]
            if v["material"]:
                rows.append([e(GROUPS[g]), e(LABELS[r]), n(v["m1"]), n(v["m2"]), pct(v["delta_pct"])])
    main.append("<h3>Contributions à examiner dans chaque ensemble</h3>" + table(["Ensemble","Rôle","M1 JH","M2 JH","Écart"], rows))
    main.append("<p>Un changement de rôle ne prouve pas une réduction du travail. Par exemple, M1 distingue 5 JH de plateforme propres à REF ; M2 rattache ces tâches au développement, à la QA ou au socle.</p>")
    main.append("<h3>Ce que la revue a clarifié</h3>")
    for finding in review["findings"]:
        main.append("<article><h4>" + e(finding["subject"]) + "</h4>" + paragraph(finding["finding"]) + paragraph(finding["action"]) + "</article>")
    main.append(paragraph(review["revision_rule"]) + "</section>")

    main.append("<section id='maille'><h2>Restituer au niveau métier sans inventer une ventilation</h2>")
    main.append(paragraph(decision["granularity"]) + paragraph(decision["why_not_optimal"]))
    rows = []
    for u in result["native_reporting"]["units"]:
        rows.append([e(u["label"]) + "<br><small>" + e(u["level"]) + " · " + e(u["native_ref"]) + "</small>",
                     ", ".join(u["financing_refs"]), n(u["studied_part_jh"][1]), "Inconnu"])
    main.append(table(["Unité native","Financements du sous-total","Part étudiée · JH centraux","Total de l’unité métier"], rows))
    main.append("<p>Les lignes des différents niveaux ne s’additionnent pas entre elles. La part des références est portée au sous-domaine Operational References ; le stock au regroupement métier Inventory State Management. Les mêmes financements remontent au domaine. Le commun reste visible au domaine.</p>")
    rows = [[e(c["bc_ref"]), e(c["label"]), e(c["capability_ref"]), " + ".join(c["financing_refs"]), "Part non isolée"] for c in result["native_reporting"]["capabilities"]]
    main.append(table(["Repère","Capacité","Identifiant natif","Ensembles bénéficiaires","JH propres"], rows))
    main.append(paragraph(coverage["native_rollup"]) + ul(coverage["limits"]))
    main.append("<p><strong>Le total du Core System reste inconnu.</strong> Les 82 autres capacités ne sont ni estimées, ni réputées sans effort. Le rattachement à une capacité signifie un bénéfice partiel, pas sa livraison intégrale.</p></section>")

    main.append("<section id='perimetre'><h2>Le contrat du panier expérimental</h2>")
    main.append(paragraph(contract["classification"]))
    main.append(ul([contract["baseline"][k] for k in ["stack","database","ui","architecture","team","quality","performance_assumption"]]))
    for g in groups:
        main.append("<article><h3>" + e(GROUPS[g]) + "</h3><h4>Compris</h4>" + ul(contract[g]["includes"]) + "<h4>Hors périmètre</h4>" + ul(contract[g]["excludes"]) + "</article>")
    for g in ["REF","STOCK"]:
        d = docs["iteration-03-m1-" + g.lower() + ".json"]
        main.append("<h3>Hypothèses de détail — " + e(GROUPS[g]) + "</h3>" + ul(d["assumptions"]))
    main.append("<p>Ces hypothèses ne sont pas une spécification approuvée de FLOW. L’absence de suppression des objets absents d’un lot complet et l’expiration sur commande sont particulièrement structurantes.</p>")
    main.append("<h3>Variantes séparées</h3>")
    v = docs["iteration-03-m1-stock.json"]["variant"]
    main.append(paragraph(v["change"] + " : " + n(v["frozen_total_jh"][1]) + " JH centraux supplémentaires (" + span(v["frozen_total_jh"]) + "). Hors base, estimation d’ingénierie."))
    main.append("<p>Faire d’un import complet un instantané désactivant les objets absents : charge supplémentaire inconnue. Cette variante n’est pas absorbée dans la borne haute de REF.</p></section>")

    main.append("<section id='methode'><h2>Ce que les méthodes apportent à ce stade</h2>")
    for name, description in result["market_method_status"].items():
        main.append("<p><strong>" + e(name.replace("_"," ")) + ".</strong> " + e(description) + "</p>")
    main.append("<p>La méthode testée relie capacité métier → mécanisme observé ou exigé → travaux Spring restant à réaliser → contributions par rôle. Aucune note de complexité, aucun nombre de lignes de code ni pourcentage forfaitaire de réutilisation ne multiplie les jours.</p>")
    main.append("<p>M1 détaille les paquets. M2 apprécie globalement les trois ensembles avant de voir M1. M3 restitue les mêmes coûts dans la hiérarchie métier ; il ne constitue pas une troisième estimation indépendante.</p>")
    main.append("<p>La complexité reste un profil explicatif : données et relations, cohérence des opérations, concurrence et reprise, réutilisation et dépendances, interfaces et contrôle du produit. Elle sert à identifier les travaux et les inconnues.</p></section>")

    main.append("<section id='travaux'><h2>Des mécanismes aux travaux et aux durées proposées</h2><p>Chaque paquet relie son fondement à un travail restant à réaliser. Les références n’attestent pas sa durée. Les tests des OSS ont été lus, pas exécutés.</p>")
    targets = list(dict.fromkeys(x["target"] for x in result["resolved_proof_refs"]))
    target_ids = {t:"preuve-" + str(i + 1) for i,t in enumerate(targets)}
    for g in groups:
        d = docs["iteration-03-m1-" + g.lower() + ".json"]
        main.append("<h3>" + e(GROUPS[g]) + "</h3>")
        for p in d["packages"]:
            vals = [sum(v[i] for v in p["effort"].values()) for i in range(3)]
            main.append("<article id='paquet-" + e(p["id"]) + "'><h4>" + e(p["id"] + " · " + p["label"]) + "</h4>" + paragraph(p["work"]) + "<p><strong>" + n(vals[1]) + " JH centraux · " + span(vals) + " JH</strong></p>" + paragraph(p["rationale"]))
            main.append(table(["Contribution","Bas · JH","Central · JH","Haut · JH"], [[e(LABELS[r])] + [n(v) for v in p["effort"][r]] for r in roles if r in p["effort"]]))
            if p.get("central_basis"):
                main.append(ul([LABELS[r] + " : " + v for r,v in p["central_basis"].items()]))
            links = [x for x in result["resolved_proof_refs"] if x["package"] == p["id"]]
            main.append("<p>Fondements : " + " · ".join("<a href='#" + target_ids[x["target"]] + "'>" + e(x["reference"]) + "</a>" for x in links) + ".</p></article>")
    main.append("</section><section id='preuves'><h2>Références et limites de preuve</h2>")
    main.append(paragraph(docs["iteration-03-references.json"]["evidence_interpretation"]))
    for product in code["products"]:
        main.append("<article><h3>" + e(product["name"]) + "</h3>" + paragraph(product["finding"]) + paragraph(product["spring_implication"]) + paragraph(product["limits"]) + "<p><small>Révisions : " + e(" · ".join(product["commits"])) + "</small></p></article>")
    main.append("<p>ERPNext/Frappe demeure l’ancre initiale de l’expérience. La lecture ciblée des trois comparables supplémentaires — Odoo, Tryton et Axelor — a été conservée dans l’itération02. Cette itération ne prétend pas avoir exécuté leurs produits.</p>")
    for t in targets:
        file, _, pointer = t.partition("#")
        obj = docs[file]
        if pointer:
            for part in pointer[1:].split("/"):
                part = part.replace("~1","/").replace("~0","~")
                obj = obj[int(part)] if isinstance(obj, list) else obj[part]
        main.append("<article id='" + target_ids[t] + "'><h4>" + e(target_ids[t].replace("preuve-","Référence ")) + "</h4><p><a href='" + e(file) + "'>" + e(t) + "</a></p>")
        if isinstance(obj, dict):
            for key in ["label","finding","spring_implication","limits","title","summary","name","purpose","limitation"]:
                if obj.get(key):
                    main.append(paragraph(obj[key]))
            url = obj.get("url")
            if isinstance(url,str):
                main.append("<p><a href='" + e(url) + "'>Consulter la source citée</a></p>")
        elif isinstance(obj,str):
            main.append(paragraph(obj))
        else:
            main.append("<p>Cadre ou registre de contexte. Voir le document pour le détail et ses limites de transposition.</p>")
        main.append("</article>")
    main.append("</section><section id='suite'><h2>Une autre itération vaut-elle le coût ? Oui, avec une borne</h2>")
    rec = decision["recommendation"]
    main.append(paragraph(rec["reason"]) + paragraph(rec["next_objective"]))
    main.append(table(["Travail suivant","Résultat observable attendu"], [[e(x["task"]), e(x["observable"])] for x in rec["tasks"]]))
    main.append("<div class='key'>" + paragraph(rec["investigation_bound"]) + "</div>" + paragraph(rec["stop_condition"]) + paragraph(rec["proof_limit"]))
    main.append("<p>Ces essais sont des témoins de conception. Aucun écran complet ni spécification exhaustive du produit n’est demandé. Une garantie vérifiée peut préciser un travail ; elle ne prouve pas sa durée de réalisation.</p>")
    main.append(table(["Étape de l’entonnoir","Résultat courant"], [[e(s["id"]),e(s["detail"])] for s in decision["stages"]]))
    main.append("</section><section id='controle'><h2>Traçabilité et contrôles</h2>")
    main.append(f"<p>{len(result['checks'])} contrôles arithmétiques, de périmètre et de provenance passent. Les {result['source_files_checked']} empreintes des sources actives, paramètres et cartographie sont inchangées. Les résultats et ce rapport sont reproductibles par le script de l’audit.</p>")
    main.append("<p>Ces contrôles ne sont ni des tests du produit Spring, ni une validation de la justesse des efforts. Aucune modification du modèle économique actif, aucun commit ni publication.</p>")
    main.append("<p><a href='iteration-03-resultats.json'>Résultats calculés</a> · <a href='iteration-03-experiments.py'>Calcul et contrôle de reproduction</a> · <a href='iteration-03-contrat.json'>Contrat expérimental</a> · <a href='iteration-03-protocole.json'>Protocole figé</a> · <a href='iteration-03-decision.json'>Décision</a> · <a href='iteration-02.html'>Itération précédente</a> · <a href='plan-iterations.html'>Plan de l’entonnoir</a></p></section>")
    nav = [("resultat","Résultat"),("jh","JH par rôle"),("ecarts","Écarts et revue"),("maille","Unités métier"),("perimetre","Périmètre"),("methode","Méthodes"),("travaux","Travaux détaillés"),("preuves","Preuves"),("suite","Suite et arrêt"),("controle","Contrôles")]
    css = """*{box-sizing:border-box}html{scroll-behavior:auto}body{margin:0;background:#FAF8F4;color:#182632;font:16px/1.65 Aptos,'Segoe UI',Arial,sans-serif}a{color:#236159;text-underline-offset:3px;overflow-wrap:anywhere}a:focus-visible{outline:3px solid #C24F00;outline-offset:4px}nav{position:fixed;inset:0 auto 0 0;width:200px;padding:35px 20px;background:#fff;border-right:1px solid #EADFCD}nav strong{color:#236159;font-size:24px}nav a{display:block;margin:14px 0}main{max-width:1320px;margin-left:200px;padding:40px 48px 80px}header{background:#D9F2EA;border-radius:16px;padding:30px 38px;margin-bottom:35px}h1{font-size:36px;line-height:1.2;margin:12px 0}h2{font-size:27px;line-height:1.25}h3{font-size:21px}h4{font-size:18px;margin:5px 0 12px}.eyebrow{font-weight:700;font-size:13px;letter-spacing:.06em}section{padding:16px 0 30px;border-bottom:1px solid #EADFCD;scroll-margin-top:24px}article{background:#fff;padding:20px 24px;margin:18px 0;border-left:3px solid #D9F2EA}p{max-width:100ch}li{margin:7px 0}.key{background:#FFF0DB;border-left:5px solid #FF7A1A;padding:18px 24px;margin:22px 0}.key>strong{font-size:28px}.key p{margin:6px 0}.formula{background:#F0F8F5;padding:18px;font-weight:650}.scroll{overflow-x:auto;margin:22px 0}table{border-collapse:collapse;width:100%;background:#fff;font-size:14px}th{background:#F4F8F6;text-align:left;font-size:13px}th,td{padding:12px 14px;border-bottom:1px solid #EADFCD;vertical-align:top}small{font-size:12px;color:#45525A}td{min-width:85px}td:first-child{min-width:190px}tr:last-child td{border-bottom:2px solid #D9F2EA}@media(max-width:900px){nav{position:static;width:auto;padding:16px 20px}nav a{display:inline-block;margin:7px 12px 7px 0}main{margin:0;padding:20px}header{padding:25px}h1{font-size:29px}}@media print{nav{display:none}main{margin:0;padding:0}header{background:#fff}article,tr{break-inside:avoid}a{color:#182632}body{font-size:11pt}.scroll{overflow:visible}}"""
    return "<!doctype html><html lang='fr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>FLOW · Itération 03 · JH par rôle</title><style>" + css + "</style></head><body><nav aria-label='Sommaire'><strong>FLOW</strong>" + "".join("<a href='#" + k + "'>" + e(v) + "</a>" for k,v in nav) + "</nav><main>" + "".join(main) + "</main></body></html>\n"
