"""Rapport de décision 08 : affichage des résultats figés, sans calcul d'effort."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("flow_report07_helpers", HERE / "iteration-07-report.py")
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
STYLE, esc, table, section, note, ref_link = (
    helpers.STYLE, helpers.esc, helpers.table, helpers.section, helpers.note, helpers.ref_link
)

def load(name):
    return json.loads((HERE / name).read_text(encoding="utf-8-sig"))

def fmt(value, digits=0):
    return f"{value:,.{digits}f}".replace(",", "\u202f").replace(".", ",")

def paragraph(text):
    return "<p>" + text + "</p>"

def render(data, decision):
    for field in ("full_core_jh", "full_core_months", "full_contract_jh",
                  "full_contract_months", "cumulative_jh", "selected_estimate_jh"):
        if data[field] is not None:
            raise ValueError("Aucun total retenu ou cumul de charges ne peut être affiché.")
    if data["recommendation"] != decision["recommendation"]:
        raise ValueError("Décision et résultats ne sont pas cohérents.")
    if any(c.get("passed") is False for c in data["checks"]):
        raise ValueError("Un contrôle consolidé a échoué.")
    m = {x["id"]: x["current"] for x in data["metrics"]}
    cosmic = data["cosmic"]
    empirical = data["empirical"]
    ratios = data["cocomo"]["sensitivity_ratios"]
    sections = []

    body = note("<strong>Recommandation : modifier l’approche.</strong>" +
        paragraph(esc(decision["conclusion"])) +
        paragraph("Cette décision concerne le dispositif d’estimation expérimenté. Elle ne propose pas d’arrêter FLOW."))
    body += paragraph("Le dernier essai apporte une taille de code candidate, un calcul conditionnel de charge et de délai, "
        "et une mesure fonctionnelle sensiblement élargie. Il permet de mieux voir ce qui influence les résultats. "
        "<strong>Il ne démontre pas une amélioration de la précision suffisante pour retenir un budget.</strong>")
    body += paragraph("Les acquis restent utiles : cartographie native, frontières des fonctions, mécanismes observés dans "
        "Odoo, Tryton et Axelor, travaux communs identifiés et hypothèses discutables. "
        "<strong>Le code OSS aide à décrire le travail, mais ne fournit pas les charges humaines de sa réalisation.</strong>")
    body += paragraph("Une prochaine étape doit apporter une preuve extérieure : estimation de réalisation argumentée, "
        "choix d’architecture confirmé, mesure ciblée ou références empiriques compatibles. Répéter les mêmes calculs "
        "avec les mêmes données ne suffit pas. Les analyses isolées avant gel restent des analyses d’agents IA, "
        "pas plusieurs avis externes indépendants.")
    sections.append(section("decision", "Décider du changement de méthode", body))

    body = paragraph(f"Le cumul reste <strong>{m['comparative']} capacités étudiées sur {m['inventory']}</strong>. "
        f"Les {m['scenario_complete']} capacités d’Operational References ont toutes leurs fonctions représentées dans "
        f"le scénario de l’itération 07. Les {m['partial_only']} autres restent partielles et "
        f"{m['not_comparative']} capacités n’ont pas d’estimation comparative. "
        f"<strong>{m['opportunity_admitted']} capacité est admise comme estimation complète suffisamment étayée "
        "pour l’opportunité.</strong>")
    body += paragraph("Ces indicateurs comptent des capacités, de poids et de contenu différents. "
        "Ils ne mesurent ni une part du coût, ni l’avancement d’une réalisation. Aucune capacité nouvelle n’est "
        "ajoutée au cumul par ce dernier essai.")
    rows = []
    for s in data["subdomains"]:
        rows.append("<tr><th scope='row'>" + esc(s["name"]) + "</th>" +
            "".join("<td class='num'>" + fmt(s[k]) + "</td>"
                    for k in ("total", "comparative", "scenario_estimated", "opportunity_admitted")) + "</tr>")
    body += table(["Sous-domaine natif", "Périmètre", "Étudiées", "Scénarisées", "Admissibles"],
                  rows, "Cumul par sous-domaine — capacités distinctes, aucun cumul de JH")
    studied = [c for c in data["coverage"] if c["comparatively_studied"]]
    groups = {}
    for c in studied:
        groups.setdefault(c["path_names"][1], []).append(c)
    rows = []
    for group, members in groups.items():
        names = "<ul class='plain-list'>" + "".join(
            "<li><span class='id'>" + esc(c["block"]) + "</span> — " + esc(c["name"]) + "</li>"
            for c in members) + "</ul>"
        status = "Famille étudiée ici ; scénario 07, non admis" if members[0]["scenario_estimated"] else "Études partielles antérieures"
        rows.append("<tr><th scope='row'>" + esc(group) + "</th><td>" + names + "</td><td>" + esc(status) + "</td></tr>")
    body += table(["Regroupement", "Capacités : libellés natifs conservés", "État"],
                  rows, "Les capacités du cumul — Operational References identifie la famille de six capacités")
    sections.append(section("cumul", "Le périmètre progresse en compréhension, pas en admission", body))

    sizes = data["size"]["new_delivered_product_KSLOC"]
    body = paragraph("La taille candidate vaut <strong>" + " / ".join(fmt(v, 3) for v in sizes) +
        " milliers d’unités logiques de code produit</strong> pour les variantes basse, centrale et haute. "
        "Ce sont des hypothèses de densité d’implémentation d’une même conception partielle ; "
        "ce ne sont ni des mesures d’un logiciel FLOW livré ni des percentiles.")
    body += paragraph("De petits blocs OSS ont été effectivement lus et comptés à des versions identifiées. "
        "Ils fournissent des analogies pour les contrôleurs, règles, traitements et interactions. "
        "La quantité de modèles, de champs et de blocs cibles est ensuite un jugement d’ingénierie. "
        "Le choix de blocs comparables et leur transposition vers Spring restent à justifier.")
    body += paragraph("Java et TypeScript sont distingués puis réunis selon une convention explicite. "
        "Le compteur TypeScript inclut notamment déclarations, propriétés d’objets, éléments et attributs JSX. "
        "<strong>L’équivalence de ces unités avec le corpus de calibration COCOMO n’est pas démontrée.</strong> "
        "Les bibliothèques intactes ne sont pas recomptées comme du nouveau code et aucune seconde remise Spring n’est appliquée.")
    body += "<ul class='plain-list'><li><strong>Versions canoniques :</strong> les différences sémantiques à convertir "
    body += "entre les deux versions requises restent inconnues.</li><li><strong>Données :</strong> les instructions SQL, "
    body += "contraintes, migrations et index ne sont pas absorbés par la seule logique Java.</li>"
    body += "<li><strong>Livraison :</strong> les moyens d’environnements, sauvegarde, restauration et supervision "
    body += "restent à dimensionner. Les garanties de charge, sécurité et reprise demandent des essais.</li></ul>"
    body += paragraph("Le code des tests est exclu de cette taille de produit, sans supprimer les activités de test "
        "de l’effort logiciel. L’inconnu ne vaut pas zéro. " +
        ref_link("iteration-08-taille.json", "Conception, analogies et limites de taille") + ".")
    sections.append(section("taille", "Une taille candidate désormais calculable, toujours partielle", body))

    body = note("<strong>Ces résultats concernent le code produit dimensionné et le cycle logiciel COCOMO.</strong>" +
        paragraph("Sans tarif ni gain IA appliqué. Aucune cellule n’est retenue comme estimation complète de la famille, de ses moyens communs ou du Core."))
    rows = []
    cases = data["cocomo"]["cases"]
    contexts = list(dict.fromkeys(c["scenario_id"] for c in cases))
    for context in contexts:
        chosen = [c for c in cases if c["scenario_id"] == context]
        row = "<tr><th scope='row'>" + esc(chosen[0]["scenario_label"]) + "</th>"
        for variant in ("bas", "central", "haut"):
            c = next(x for x in chosen if x["size_variant"] == variant)
            row += "<td><strong>" + fmt(c["effort_jh"]) + " JH</strong><br>" + fmt(c["development_months"], 1) +                 " mois<br><span class='small muted'>Effectif moyen : " + fmt(c["staffing_average"], 1) + "</span></td>"
        rows.append(row + "</tr>")
    headers = ["Contexte proposé"] + [
        label + " · " + fmt(size, 3) + " KSLOC"
        for label, size in zip(("Taille basse", "Taille centrale", "Taille haute"), sizes)]
    body += table(headers, rows, "Trois contextes × trois tailles — JH bruts conditionnels, calendrier et effectif moyen implicite")
    method = load("iteration-08-methode.json")
    constants = method["constants"]
    body += note("<strong>Formules et unités</strong>" +
        paragraph("<code>PM_NS = " + fmt(constants["A"], 2) + " × Taille<sup>E</sup> × M<br>"
            "PM = PM_NS × EM_SCED ; JH = PM × " + fmt(constants["person_month_hours"]) + " / " + fmt(constants["jh_hours"]) + "<br>"
            "TDEV = " + fmt(constants["C"], 2) + " × PM_NS<sup>F</sup> × SCED% / 100</code>") +
        paragraph("Taille est le code candidat en KSLOC ; M est le produit des multiplicateurs d’effort hors SCED. "
            "PM_NS est l’effort nominal en personnes-mois ; PM intègre le multiplicateur de compression EM_SCED. "
            "Une personne-mois vaut " + fmt(constants["person_month_hours"]) + " heures et un JH " + fmt(constants["jh_hours"]) + " heures. "
            "TDEV est le délai en mois ; SCED% fixe le pourcentage du délai nominal.") +
        paragraph("<code>E = " + fmt(constants["B"], 2) + " + 0,01 × ΣSF ; F = " + fmt(constants["D"], 2) +
            " + 0,2 × (E − " + fmt(constants["B"], 2) + ")</code>. "
            "E et F sont des exposants sans unité ; SF désigne les facteurs d’échelle du projet. "
            "Le délai utilise PM_NS, sans compter deux fois la compression."))
    body += paragraph("Le nominal est un repère mathématique. Le contexte expérimenté suppose une équipe stable, "
        "compétente et bien outillée ; le contexte difficile renforce les risques et les contraintes. "
        "Aucun ne décrit une équipe disponible ou une capacité partenaire déjà prouvée.")
    body += paragraph("Les JH expriment le travail cumulé des personnes. Les mois expriment le temps écoulé "
        "entre les jalons logiciels LCO et IOC, correspondant ici à l’élaboration et à la construction. "
        "Le calendrier complet du contrat et du programme reste inconnu. L’effectif affiché est une moyenne "
        "implicite, sans engagement de recrutement, disponibilité ou répartition par rôle.")
    body += paragraph("Le modèle distingue l’effort nominal et l’effet d’une compression du délai. "
        "La conversion des personnes-mois en JH conserve les heures ; elle ne transforme pas la charge en calendrier. "
        "Les activités logicielles déjà couvertes interdisent d’ajouter mécaniquement l’ancienne QA ou l’architecture. " +
        ref_link("iteration-08-calculs.json", "Résultats et contrôles des formules") + " · " +
        ref_link("https://www.rose-hulman.edu/class/cs/csse372/201310/Homework/CII_modelman2000.pdf",
                 "Manuel primaire USC COCOMO II") + ".")
    body += paragraph("<strong>Diagnostic de sensibilité :</strong> à taille centrale, changer le contexte "
        "multiplie l’effort entre les extrêmes par " + fmt(ratios["context_at_central_size"], 2) +
        " ; au contexte nominal, changer la taille le multiplie par " + fmt(ratios["size_at_nominal_context"], 2) +
        ". Ces rapports signalent les hypothèses influentes. Ils ne forment pas un intervalle de confiance, "
        "ne donnent aucune probabilité et ne démontrent pas qu’un résultat central serait le plus vraisemblable.")
    sections.append(section("cocomo", "COCOMO conserve la charge et le délai sous conditions", body))

    body = paragraph("Le scénario COSMIC élargi atteint <strong>" +
        fmt(cosmic["conditional_expanded_subset_cfp"]) + " points de fonction COSMIC (CFP) sur " +
        fmt(cosmic["functional_processes"]) + " processus conditionnels</strong>. "
        "Il comprend réception, réexamen, consultations, administration, export, usages conservés et "
        "rapprochement après restauration. Les entrées, lectures, écritures et sorties sont délimitées "
        "à la frontière de l’application.")
    body += paragraph("Les fonctions natives sont toutes reliées, sans rendre le comptage complet ou validé. "
        "La purge, le cycle des habilitations et plusieurs choix de protocole restent ouverts. "
        "Les treize sujets de référence ne sont ni des tables imposées ni treize points fonctionnels. "
        "Les API internes et les occurrences ne multiplient pas les mouvements.")
    body += paragraph(esc(cosmic["aggregation"]))
    body += paragraph("<strong>Aucun taux CFP → JH ou CFP → LOC n’est appliqué.</strong> "
        "Le périmètre COSMIC et le périmètre du code candidat diffèrent ; leur écart ne peut pas être "
        "présenté en pourcentage. La taille fonctionnelle aide à révéler les échanges oubliés, "
        "sans mesurer à elle seule l’effort des garanties. " +
        ref_link("iteration-08-cosmic.json", "Processus et hypothèses COSMIC") + " · " +
        ref_link("https://cosmic-sizing.org/cosmic-sizing/intro/measurement-process/", "Méthode COSMIC officielle") + ".")
    sections.append(section("cosmic", "La mesure fonctionnelle vérifie le contenu du besoin", body))

    body = paragraph("<strong>Aucun nouveau taux de productivité applicable n’a été retenu.</strong> Les " + fmt(empirical["previous_case_studies_reexamined"]) +
        " cas Gencel étaient déjà connus ; leur relecture précise les activités couvertes, les traitements "
        "exclus et l’usage de génération de code. Ils montrent que des efforts observés existent, "
        "sans établir une productivité FLOW. " +
        ref_link("https://www.diva-portal.org/smash/get/diva2:836007/FULLTEXT01.pdf", "Étude primaire de Gencel") + ".")
    body += paragraph("Une publication réunissant 337 observations COSMIC a été repérée. Les données détaillées "
        "n’ont pas été obtenues ni qualifiées pour cet essai. Les références ISBSG restent une voie à examiner "
        "avec des unités, activités, technologies et garanties compatibles. Ce constat ne signifie pas "
        "qu’aucune référence utilisable n’existe ailleurs. " +
        ref_link("https://aperta.ulakbim.gov.tr/records/279553", "Dépôt de la publication") + " · " +
        ref_link("iteration-08-references-effort.json", "Qualification des références d’effort") + ".")
    body += paragraph("COSMIC, COCOMO et ISBSG remplissent des fonctions différentes : mesurer une taille "
        "fonctionnelle, calculer un effort conditionnel, documenter des réalisations. Ils ne constituent "
        "pas trois estimations indépendantes déjà réconciliées. Un accord numérique éventuel avec les anciennes "
        "hypothèses de JH ne serait pas une validation.")
    body += paragraph("Pour ce nouvel essai, le calcul conditionnel reste en classe C (hypothèse d’ingénierie) et l’estimation complète de la famille en classe D (données insuffisantes) : taille totale et rôles restent indéterminés. Cette appréciation ne réécrit pas les classes historiques des scénarios 07.")
    sections.append(section("preuves", "La preuve d’effort extérieure reste à obtenir", body))

    body = paragraph("<strong>Famille cohérente et travaux communs reste le niveau pratique candidat.</strong> "
        "Il rend les dépendances et le financement unique des mécanismes partagés lisibles. "
        "La capacité native conserve la traçabilité ; les fonctions et blocs servent à examiner les hypothèses. "
        "Aucune comparaison empirique ne démontre que ce niveau donne une précision optimale.")
    body += paragraph("Les JH par rôle restent indispensables à la décision : analyse produit, architecture, "
        "développement Java, développement interface, conception des parcours, QA indépendante, plateforme et "
        "livraison, sécurité, coordination technique. Les scénarios antérieurs sont conservés, mais COCOMO "
        "ne fournit pas leur nouvelle ventilation. Il faut rapprocher activités, inclusions et responsabilités "
        "avant de reprendre une charge.")
    body += table(["Unité de travail", "Charge à justifier", "Réalisation à décrire", "Preuve et réserve"],
        ["<tr><td>Famille et mécanismes propres</td><td>JH bas / central / haut par rôle</td>"
         "<td>Composition d’équipe, dépendances et délai</td><td>Référence comparable, hypothèse et inconnue</td></tr>",
         "<tr><td>Travaux communs, comptés une fois</td><td>Mêmes rôles ; propriétaire explicite</td>"
         "<td>Disponibilité et ordre des contributions</td><td>Inclusions réconciliées avec la famille</td></tr>"],
        "Matrice proposée pour la prochaine preuve — aucune ventilation chiffrée nouvelle")
    body += paragraph("Faire examiner le même contrat court, ses garanties S1 et la conception candidate par "
        "des personnes ayant réalisé des produits Spring comparables. Obtenir des propositions séparées avec "
        "JH par rôle, calendrier et preuves ; expliquer les désaccords par des travaux ou conditions, "
        "sans moyenne arbitraire. Une réalisation ciblée peut instruire une difficulté dominante, "
        "sans devenir un taux universel.")
    body += paragraph("<strong>L’acceptabilité dépend de la décision d’investissement.</strong> "
        "Un historique local n’est pas une condition absolue : une référence extérieure correctement transposée "
        "ou une estimation de réalisation étayée peut aider. La prochaine étape réussit si elle apporte une "
        "estimation complète réconciliée avec le contrat et une confrontation extérieure documentée. "
        "Sinon, conserver une enveloppe exploratoire et arrêter le raffinement numérique. "
        "Aucune consultation, dépense ou itération suivante n’est déclenchée ici.")
    sections.append(section("suite", "Obtenir une proposition de réalisation vérifiable", body))

    links = [
        ("iteration-08-resultats.json", "Résultats consolidés et cumul"),
        ("iteration-08-decision.json", "Décision proposée"),
        ("iteration-07-contrat-v1.1.json", "Contrat commun de la famille"),
        ("iteration-08-methode.json", "Paramètres et conventions COCOMO"),
        ("iteration-08-taille.json", "Taille candidate et preuves de code"),
        ("iteration-08-revue.json", "Revue des unités, équations et limites"),
        ("iteration-07.html", "Scénarios historiques par rôle"),
    ]
    body = paragraph("Les " + fmt(len(data["checks"])) +
        " contrôles consolidés vérifient calculs, identifiants et empreintes des entrées. Les liens sont vérifiés séparément dans le navigateur. "
        "Ils ne prouvent ni la validité de marché, ni l’effort réel, ni les performances du produit. "
        "La revue arithmétique indépendante confirme la cohérence des calculs ; "
        "elle n’ajoute aucune calibration empirique.")
    body += "<ul class='plain-list'>" + "".join(
        "<li>" + ref_link(path, label) + "</li>" for path, label in links) + "</ul>"
    sections.append(section("sources", "Traçabilité de la décision", body))
    nav_items = [("decision", "Décision"), ("cumul", "Cumul natif"), ("taille", "Taille candidate"),
                 ("cocomo", "Charge et délai"), ("cosmic", "Taille fonctionnelle"),
                 ("preuves", "Références d’effort"), ("suite", "Prochaine preuve"), ("sources", "Traçabilité")]
    nav = "<nav class='toc' aria-label='Sommaire'><strong>Dans ce rapport</strong>" + "".join(
        "<a href='#" + key + "'>" + esc(label) + "</a>" for key, label in nav_items) + "</nav>"
    extra_style = ".toc{max-height:95vh;overflow:auto}#cocomo th:first-child{min-width:12rem}#cocomo td{min-width:10rem}#cumul .plain-list{margin:0}#cumul th:first-child{min-width:10rem}"
    page = "<!doctype html><html lang='fr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>" +         "<title>FLOW — Itération 08 : modifier l’approche d’estimation</title><style>" + STYLE + extra_style +         "</style></head><body><a class='skip' href='#main'>Aller au contenu</a><header class='hero'>" +         "<div class='eyebrow'><span class='marker' aria-hidden='true'></span>FLOW · Étude d’opportunité · Itération 08</div>" +         "<h1>Modifier l’approche d’estimation</h1><p>Dernier essai automatique : les calculs deviennent plus explicites ; " +         "la prochaine preuve doit venir de conditions de réalisation documentées.</p><p class='small muted'>" +         esc(data["date"]) + " · Audit de décision · Sources actives inchangées</p></header><div class='layout'>" +         nav + "<main id='main'>" + "".join(sections) + "</main></div><footer><p>Recommandation sur la méthode ; " +         "aucun arrêt du programme FLOW et aucun budget complet retenu.</p></footer></body></html>\n"
    return page

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "iteration-08.html")
    args = parser.parse_args()
    if args.output.resolve() != (HERE / "iteration-08.html").resolve():
        raise ValueError("Seul iteration-08.html est une sortie autorisée.")
    data, decision = load("iteration-08-resultats.json"), load("iteration-08-decision.json")
    page = render(data, decision)
    args.output.write_text(page, encoding="utf-8")
    print(json.dumps({"output": str(args.output.resolve()), "effort_recalculated": False,
                      "results_sha256": hashlib.sha256((HERE / "iteration-08-resultats.json").read_bytes()).hexdigest()},
                     ensure_ascii=True))

if __name__ == "__main__":
    main()



