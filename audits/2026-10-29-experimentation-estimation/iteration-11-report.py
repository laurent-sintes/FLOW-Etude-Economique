"""Continuous opportunity audit report; values read from calculation results."""
import json,html,importlib.util,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def read(n):return json.loads((HERE/n).read_text(encoding="utf-8"))
spec=importlib.util.spec_from_file_location("report07",HERE/"iteration-07-report.py")
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
e=html.escape
def n(x):return f"{x:,.1f}".rstrip("0").rstrip(".").replace(","," ").replace(".",",")
def t(v):return " / ".join(n(x) for x in v)
def p(s):return "<p>"+s+"</p>"
def ul(xs):return "<ul>"+"".join("<li>"+e(x)+"</li>" for x in xs)+"</ul>"
def table(h,rows,caption):return base.table(h,["<tr>"+"".join("<td>"+str(x)+"</td>" for x in row)+"</tr>" for row in rows],caption)
def link(f,label):return '<a href="'+e(f)+'">'+e(label)+'</a>'
def main():
 d=read("iteration-11-resultats.json");h=read("iteration-11-contrat.json");lots=read("iteration-11-lots.json");proof=read("iteration-11-preuves.json")
 roles=d["roles"];cal=d["calendar"];pr=d["progress"];sections=[]
 body=base.note(p("<strong>Orchestration opérationnelle : "+n(d["incremental"]["total"][1])+" JH bruts supplémentaires.</strong>")+
 p("Bas / central / haut : <strong>"+t(d["incremental"]["total"])+" JH</strong>. Délai supplémentaire proposé : <strong>"+t(cal["incremental_public_months"])+" mois</strong>.")+
 p("Cumul référentiels + stocks + orchestration : <strong>"+n(d["cumulative_estimated"]["total"][1])+" JH centraux</strong>, pour <strong>27 capacités sous hypothèses</strong>."))
 body+=p("Cette itération traite les <strong>11 capacités BC-076 à BC-086</strong>, soit 33 fonctions natives : définitions, composition, événements, conduite, contributions humaines, affectations, délais, interventions, exceptions, registre et visibilité. <strong>Process Mining et Operational Analysis & Reporting restent à traiter séparément.</strong>")
 body+=p("Le cumul est partiel : ce n’est pas le total du Core System. Il suppose disponibles les référentiels et mécanismes de stocks financés dans les itérations09 et10. Les anciens pilotes ORCH05 et EXEC05 ne sont jamais ajoutés.")
 body+=p("<strong>Classe C : estimation d’ingénierie assistée par IA, non calibrée.</strong> La lecture du code explique les mécanismes existants et les écarts ; elle ne mesure pas le temps de leur réalisation. Aucun P50/P80, aucune validation statistique par trois méthodes et aucune revue humaine non effectuée ne sont revendiqués.")
 body+=p("Les demi-journées servent à conserver les sommes du calcul ; l’ordre de grandeur à retenir pour cette famille est <strong>environ 1 500 JH</strong>. La borne haute n’est pas un plafond garanti.")
 sections.append(("synthese","Résultat et périmètre",body))
 body=p("<strong>Réutiliser un moteur Spring et construire le produit FLOW autour de lui.</strong> Flowable fournit des primitives de tâches, jobs, temporisations et état d’exécution. FLOW doit préserver les autorités, les engagements, les résultats reconnus et la preuve des interventions.")
 body+=p("La référence technique figée est Flowable OSS 7.2.0 au commit indiqué dans les preuves. Son code de configuration Spring et ses interfaces ont été lus ; la combinaison cible n’a pas été exécutée. Le fichier LICENSE examiné est Apache 2.0. Aucune interface propriétaire ni module commercial n’est supposé inclus.")
 body+=p("Les API examinées rendent deux limites concrètes visibles : affecter une tâche ne vérifie pas à lui seul l’admissibilité du collaborateur ; suspendre une instance ne suspend pas nécessairement toute sa hiérarchie. FLOW doit donc porter les contrôles de portée et d’autorité.")
 body+=p("L’adaptation retenue porte sur les <strong>segments futurs à un point de contrôle</strong>, sans modifier silencieusement activités engagées et résultats acquis. Les modèles et règles propres à Beaumanoir appartiennent à l’intégration. Process Planning ne finance pas un solveur d’optimisation logistique.")
 body+=table(["Propriétaire déjà financé","Patrimoine utilisé","Travail supplémentaire"],[[e(x["owner"]),e(x["asset"]),e(x["delta"])] for x in h["reuse"]],"Chaque mécanisme commun conserve un propriétaire unique")
 body+=p("Réutiliser une convention de reconstruction ne signifie pas que le registre des stocks devient celui des processus. Le journal métier et ses projections sont chiffrés dans BC-085 ; la récupération technique du moteur est dans E111/S112. Les tests de la composition figurent dans Q112.")
 sections.append(("reutilisation","Moteur, réutilisation et frontières",body))
 body=table(["Travaux supplémentaires","Bas JH","Central JH","Haut JH"],[[e(g["id"]+" — "+g["label"])]+[n(v) for v in g["total"]] for g in d["groups"]]+[["TOTAL"]+[n(v) for v in d["incremental"]["total"]]],"Les travaux propres des capacités s’ajoutent une seule fois à leurs communs")
 body+=p("Les capacités portent <strong>"+n(d["direct"]["total"][1])+" JH propres</strong>. Moteur, contrats communs et qualification/coordination représentent <strong>"+n(d["common"]["total"][1])+" JH</strong>. Une ligne BC seule n’est donc pas le prix d’une capacité autonome livrable.")
 body+=p("<strong>Niveau d’évaluation proposé : le sous-domaine opérationnel pour l’enveloppe, les capacités pour expliquer les écarts.</strong> Les communs représentent environ 41% du centre. Une ventilation arbitraire par capacité donnerait une précision apparente. Les matrices permettent de consolider au niveau Business Area sans compter plusieurs fois les communs.")
 sections.append(("financement","Charges par capacité et mécanisme",body))
 body=table(["Rôle","Orchestration bas / central / haut JH","Cumul central JH"],[[e(label),t(d["incremental"]["roles"][r]),n(d["cumulative_estimated"]["roles"][r][1])] for r,label in roles.items()]+[["TOTAL",t(d["incremental"]["total"]),n(d["cumulative_estimated"]["total"][1])]],"JH humains bruts ; aucune valorisation par tarif ni remise IA")
 body+=p("Développement Java + interface : <strong>"+t(d["developer_gross_jh"])+" JH</strong>, tests développeur et revues compris. Les autres rôles, dont QA indépendante, sont identifiés séparément.")
 body+=table(["Unité"]+[e(x) for x in roles.values()]+["Total"],[[e(g["id"])]+[n(g["roles"][r][1]) if g["roles"][r][1] else "—" for r in roles]+[n(g["total"][1])] for g in d["groups"]],"Matrice centrale ; un tiret n’efface pas les travaux financés dans les communs")
 body+=table(["Rôle","Base de l’hypothèse"],[[e(roles[r]),e(v)] for r,v in lots["role_basis"].items()],"Les journées proposées sont des jugements d’ingénierie")
 sections.append(("roles","JH par rôle et unité métier",body))
 body=table(["Périmètre","Bas JH","Central JH","Haut JH"],[
 ["Référentiels09"]+[n(v) for v in read("iteration-09-resultats.json")["total"]["total"]],
 ["Stocks10 supplémentaires"]+[n(v) for v in read("iteration-10-resultats.json")["incremental"]["total"]],
 ["Orchestration11 supplémentaire"]+[n(v) for v in d["incremental"]["total"]],
 ["CUMUL PARTIEL"]+[n(v) for v in d["cumulative_estimated"]["total"]]],"Même convention de brut, qualités et rôles explicites ; les trois enveloppes sont additionnées scénario par scénario")
 body+=p("Les anciens pilotes partiels ne constituent pas un quatrième poste. Le cumul n’ajoute ni une nouvelle authentification, ni une nouvelle CI, ni un second stockage de pièces, ni un second transport durable. Les raccordements et la nouvelle qualification sont en revanche des efforts supplémentaires.")
 body+=p("Les enveloppes basses/hautes se cumulent sans supposer des risques indépendants. La composition des processus, les contrats de commandes et l’historique peuvent affecter plusieurs lots ensemble.")
 sections.append(("cumul","Cumul économique sans double compte",body))
 body=table(["Hypothèse de chiffrage","Contenu retenu"],[[e(a),e(b)] for a,b in h["assumptions"]],"Hypothèses proposées pour estimer ; ni besoins intégralement spécifiés ni garanties déjà démontrées")
 body+=ul(h["exclusions"])
 body+=p("Les critères de vérification majeurs sont la conservation des engagements lors d’une adaptation, le signal anticipé ou corrigé, les décisions concurrentes, la reprise après accusé perdu, l’autorisation d’une intervention, les calendriers et la reconstitution à date. Leurs campagnes sont financées ; elles n’ont pas été exécutées dans cet audit d’estimation.")
 sections.append(("hypotheses","Hypothèses de produit et garanties attendues",body))
 body=p(e(lots["bounds"]))
 body+=table(["Point incertain","Capacités","Pourquoi il reste incertain"],[[e(x["label"]),e(", ".join(x["caps"])),e(x["effect"])] for x in h["risks"]],"Les principaux motifs de variation")
 body+=table(["Lot","Bas / central / haut JH","Facteurs bas / haut","Travail et variation"],[[e(x["id"]+" — "+x["label"]),t(x["total"]),e(str(x["factors"][0])+" / "+str(x["factors"][1])),e(x["work"])+"<br><strong>Variation :</strong> "+e(x["range_reason"])] for x in d["packages"]],"18 lots avec hypothèses distinctes ; les facteurs ne sont pas des scores de complexité")
 body+=table(["Lot","Java : actions et JH centraux","Interface : actions et JH centraux"],[[e(x["id"]),"<br>".join(e(a["action"])+": "+n(a["jh"]) for a in x["java_actions"]),"<br>".join(e(a["action"])+": "+n(a["jh"]) for a in x["frontend_actions"]) or "Inclus dans les parcours propres / sans interface propre"] for x in d["packages"]],"Les actions rendent la charge révisable ; elles ne constituent pas une mesure de productivité")
 body+=p("La couverture progresse ; <strong>aucun seuil de précision raisonnable n’est statistiquement démontré</strong>. Ces propositions servent à discuter l’investissement sous les hypothèses retenues. Elles ne sont pas des engagements de livraison au forfait.")
 sections.append(("incertitude","Fourchettes et justification des charges",body))
 body=p("<strong>Délai de la famille : "+t(cal["incremental_public_months"])+" mois</strong> (bas / central / haut), après disponibilité des communs09/10. Le centre représente environ "+n(cal["average_contribution_people"][1])+" personnes mobilisées en moyenne, avec des profils et pics différents ; ce n’est pas une équipe de personnes interchangeables.")
 body+=table(["Phase","Bas / central / haut mois","Rôle limitant au centre"],[[e(x["label"]),t(x["duration_months"]),e(roles.get(x["limiting_role"][1],x["limiting_role"][1]))] for x in cal["phases"]],"Phases séquentielles, travaux par rôle parallèles dans chacune")
 body+=table(["Phase"]+[e(x) for x in roles.values()],[[e(x["id"])]+[n(x["staff"][r]) for r in roles] for x in cal["phases"]],"Disponibilité maximale par rôle et par phase ; personnes à temps partiel possibles, pas charges supplémentaires")
 body+=p("<strong>Durée d’une phase = maximum du plancher de séquence et de chaque charge par rôle ÷ (personnes disponibles ×18JH/mois).</strong> Les planchers sont des hypothèses de dépendances et cycles de retour, non calibrées. La coordination est répartie sur les quatre phases et ne se rajoute pas à la charge.")
 body+=p(e(lots["schedule"]["dependencies"]))
 body+=p("En conservant une réalisation successive référentiels → stocks → orchestration, le cumul est <strong>"+t(cal["sequential_public_months"])+" mois</strong>. Il s’agit d’un scénario de séquencement comparable aux itérations précédentes, <strong>pas du calendrier optimal ou obligatoire du programme</strong>. Un travail parallèle exigerait un scénario d’équipes et de dépendances distinct.")
 body+=p("Les durées publiques sont arrondies au mois supérieur après calcul des cumuls non arrondis. Ni recrutement ni délai de disponibilité des services externes ne sont ajoutés. Aucun calcul COCOMO de délai n’est revendiqué.")
 sections.append(("delai","Délai et organisation",body))
 lookup={x["id"]:x for x in proof["evidence"]}
 body=table(["Capacité","Fonctions natives financées","Frontière","Code comparé"],[[e(c["block"]+" — "+c["name"]),"<br>".join(e(f["id"]+" : "+f["resultat"]) for f in c["functions"]),e(c["boundary"])," ".join(link(lookup[k]["url"],k) for k in c["evidence_ids"])] for c in d["coverage"]],"11 capacités et 33 fonctions, correspondances partielles explicitement qualifiées")
 body+=table(["Preuve et nature","Observation","Limite / travaux FLOW"],[[link(x["url"],x["id"])+"<br>"+e(x["kind"]),e(x["observed"]),e(x["delta"])] for x in proof["evidence"]],"Odoo, Tryton, Axelor et patrimoine Flowable figés ; les API lues ne sont pas des tests d’implémentation")
 body+=ul(proof["limitations"])
 body+=p("Documentation complémentaire : "+link(proof["docs"][0]["url"],"intégration Spring")+" et "+link(proof["docs"][1]["url"],"exécuteur asynchrone")+". Licence figée : "+link(proof["license"]["url"],"Flowable LICENSE")+".")
 body+=table(["Méthode","Usage effectif dans cette itération"],[[e(k),e(v)] for k,v in d["crosschecks"].items()],"La confrontation chiffrée des trois méthodes n’est pas obtenue ; l’approche retenue depuis09 est l’estimation d’ingénierie")
 sections.append(("marche","Preuves et limites de comparaison",body))
 body=table(["Indicateur","Avant","Après"],[
 ["Capacités distinctes comparées","25 /88","30 /88 (+5), soit 34%"],
 ["Propositions complètes sous hypothèses","16 /88","27 /88 (+11), soit 31%"],
 ["Autres capacités étudiées partiellement","9","3"],
 ["Capacités restant à comparer","63","58"],
 ["Capacités calibrées empiriquement","0","0"]],"Les capacités sont comptées une fois par identifiant ; ce n’est pas un pourcentage de coût couvert")
 old=read("iteration-07-resultats.json");selected=[c for c in old["coverage"] if c["id"] in set(pr["cumulative_ids"])]
 body+=table(["Famille","Capacités étudiées cumulées"],[[name,"<br>".join(e(c["block"]+" — "+c["name"]) for c in selected if c["path_names"][1]==name)] for name in dict.fromkeys(c["path_names"][1] for c in selected)],"Liste cumulative des 30 capacités comparées")
 body+=p("Les cinq nouvelles comparaisons portent sur Process Planning, Work Assignment, Work Deadline Management, Process Exception Management et Process, Tasks & Order Visibility. Les six autres capacités avaient une étude partielle ; elles ne sont pas recomptées.")
 body+=p("<strong>Progrès :</strong> onze capacités disposent d’un périmètre de produit, de travaux financés, de rôles et d’un délai ; le cumul conserve les communs une seule fois. <strong>Incertitude persistante :</strong> adaptation, effets externes et temporalités ; aucune baisse statistiquement prouvée de l’erreur.")
 body+=p("<strong>Une autre itération vaut le coup sur la planification/optimisation.</strong> Le gain attendu est d’étendre le périmètre et d’isoler les mécanismes de calcul, sans refacturer Process Planning ni Planning Data Provision. Process Mining et Operational Analysis & Reporting restent explicitement à instruire. Refaire cette même estimation d’orchestration sans nouvelle hypothèse apporterait peu.")
 body+=p(str(len(d["checks"]))+" contrôles de cohérence, couverture, capacité et empreintes passent. Ils ne testent pas le futur produit et ne prouvent pas une précision prédictive. Aucun changement du modèle économique actif ni des sources métier, aucun commit ou déploiement.")
 body+=p("Dossier : "+link("iteration-11-resultats.json","résultats et matrices")+" · "+link("iteration-11-contrat.json","hypothèses")+" · "+link("iteration-11-lots.json","lots et bases")+" · "+link("iteration-11-preuves.json","preuves")+" · "+link("iteration-11-estimation.py","calcul")+" · "+link("iteration-10.html","rapport précédent"))
 sections.append(("avancement","Avancement et prochaine itération",body))
 nav="".join('<a href="#'+i+'">'+e(title)+'</a>' for i,title,_ in sections)
 css=base.STYLE+" main p,main li{overflow-wrap:anywhere}"
 output='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FLOW — Orchestration des processus — Itération11</title><style>'+css+'</style></head><body><a class="skip" href="#synthese">Aller au contenu</a><header class="hero"><div class="eyebrow">FLOW · Étude d’opportunité · Itération11</div><h1>Orchestration des processus : charge supplémentaire et cumul</h1><p>Onze capacités opérationnelles, un moteur réutilisé et des responsabilités métier explicites.</p><p class="small">29 octobre 2026 · Proposition de classe C · Sources actives inchangées</p></header><div class="layout"><nav class="toc"><strong>Dans ce rapport</strong>'+nav+'</nav><main>'+''.join(base.section(i,title,body) for i,title,body in sections)+'</main></div><footer>Estimation d’opportunité partielle ; aucun total complet du Core System ni probabilité de livraison revendiquée.</footer></body></html>'
 (HERE/"iteration-11.html").write_text(output,encoding="utf-8")
 print(json.dumps({"report":"iteration-11.html","sections":len(sections)}))
if __name__=="__main__":main()
