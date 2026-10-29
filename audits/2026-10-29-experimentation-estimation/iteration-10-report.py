"""Inventory opportunity report from iteration10 JSON, no independent budget calculation."""
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
 d=read("iteration-10-resultats.json");h=read("iteration-10-contrat.json");lots=read("iteration-10-lots.json");proof=read("iteration-10-preuves.json")
 roles=d["roles"];sections=[];cal=d["calendar"];pr=d["progress"]
 body=base.note(p("<strong>Gestion des stocks : "+n(d["incremental"]["total"][1])+" JH bruts supplémentaires.</strong>")+
 p("Scénarios bas / central / haut : <strong>"+t(d["incremental"]["total"])+" JH</strong>. Délai supplémentaire : <strong>"+t(cal["incremental_public_months"])+" mois</strong>, sous l’organisation proposée.")+
 p("Référentiels + stocks : <strong>"+n(d["cumulative_estimated"]["total"][1])+" JH centraux</strong>, socle initial compté une seule fois."))
 body+=p("Les dix capacités Inventory Management sont estimées sur les six capacités de référentiels09 supposées réalisées. Le cumul concerne <strong>16 capacités sous hypothèses</strong>, pas tout le Core System. Aucun budget des anciens pilotes STOCK03 ou PLAN05 n’est ajouté.")
 body+=p("Estimation d’ingénierie assistée par IA, <strong>classe C</strong>. Les comparaisons de code décrivent des mécanismes et leurs limites ; elles ne mesurent pas le temps humain de leur réalisation. Les centres et facteurs de variation sont des jugements explicites. Les demi-journées conservent les sommes, sans prétendre à cette précision de prévision.")
 body+=p("Le principal progrès est la couverture des dix capacités avec des travaux financés, des rôles, des hypothèses de service et un calendrier. La confiance n’est pas devenue statistiquement mesurée. Le haut suppose plusieurs cycles de reprise et ne constitue pas un plafond contractuel.")
 sections.append(("synthese","Résultat de l’estimation",body))
 body=table(["Financement incrémental","Bas JH","Central JH","Haut JH"],[[e(g["label"])]+[n(v) for v in g["total"]] for g in d["groups"]]+[["TOTAL STOCKS"]+[n(v) for v in d["incremental"]["total"]]],"Les dix capacités, leurs communs et les extensions nécessaires")
 body+=p("Les travaux propres totalisent <strong>"+n(d["direct"]["total"][1])+" JH</strong> ; extensions, mécanismes et activités transverses totalisent <strong>"+n(d["common"]["total"][1])+" JH</strong>. Une ligne propre ne représente pas une capacité autonome livrable : elle utilise les ensembles communs.")
 body+=ul(["Extensions du socle : module stocks, droits, schémas/migrations, navigation et pipelines ; ajout de pièces justificatives sécurisées. Le socle09 reste financé dans09.",
 "Mécanismes communs aux stocks : transactions et concurrence, dimensions/quantités/références, publications durables et accusés, reconstruction et reprise.",
 "Qualification et coordination : campagnes fonctionnelles et non-régression des références utilisées, charge/concurrence/restauration, revue de sécurité, corrections, documentation et synchronisation des travaux."])
 body+=p("Le moteur d’enregistrement ne suffit pas à implémenter toutes les règles de stock : les sémantiques physique, propriété et réservation restent séparées dans leurs lots. Les connexions à Finance ou aux exécutants sont des contrats génériques ; les adaptateurs Beaumanoir réels restent en intégration.")
 sections.append(("financement","Travaux propres et mécanismes communs",body))
 body=table(["Rôle","Stocks : bas / central / haut JH","Référentiels : central","Cumul : central"],[[e(label),t(d["incremental"]["roles"][r]),n(d["reference_family"]["roles"][r][1]),n(d["cumulative_estimated"]["roles"][r][1])] for r,label in roles.items()]+[["TOTAL",t(d["incremental"]["total"]),n(d["reference_family"]["total"][1]),n(d["cumulative_estimated"]["total"][1])]],"JH humains bruts par rôle ; aucun tarif ni gain IA")
 body+=p("Les JH développeur Java + interface des stocks sont <strong>"+t(d["developer_gross_jh"])+" JH</strong>, avec tests développeur et revues. QA indépendante, architecture, sécurité et autres efforts sont comptés séparément une seule fois.")
 body+=table(["Unité"]+[e(x) for x in roles.values()]+["Total"],[[e(g["id"])]+[n(g["roles"][r][1]) if g["roles"][r][1] else "—" for r in roles]+[n(g["total"][1])] for g in d["groups"]],"Matrice centrale par unité et rôle ; les tirets ne suppriment pas les travaux financés dans les communs")
 body+=p("La QA, la livraison et une partie des revues sont transverses. Aucune allocation en dix parts égales n’est utilisée pour fabriquer un coût autonome par capacité.")
 sections.append(("roles","Charges par rôle et par unité",body))
 body=table(["Patrimoine prévu en09","Réutilisation dans10","Travail supplémentaire financé"],[[e(", ".join(x["owner09"])),e(x["retained"]),e(x["increment"])] for x in h["reuse"]],"Réutilisation sans seconde remise ni double financement")
 body+=ul(h["overlap_rules"])
 body+=table(["Ensemble","Bas / central / haut JH"],[["Référentiels09, inchangés",t(d["reference_family"]["total"])],["Stocks10, incrément",t(d["incremental"]["total"])],["Cumul des deux familles",t(d["cumulative_estimated"]["total"])]],"Cumul conservé à périmètre explicite")
 body+=p("<strong>Formule :</strong> cumul = estimation09 + nouveaux lots10, chaque financement une fois. Les bornes sont additionnées comme scénarios cohérents, sans supposer que les incertitudes se compensent. Aucun prorata par nombre de capacités ne permet d’extrapoler au Core complet.")
 sections.append(("cumul","Réutilisation et cumul économique",body))
 body=ul(h["assumptions"])
 body+=p("<strong>Exclusions :</strong>")+ul(h["exclusions"])
 body+=p("Ces hypothèses remplacent les détails de spécification indisponibles pour estimer. Elles sont proposées pour l’étude, sans être attribuées à une exigence approuvée. Les activités de clarification pendant réalisation sont financées ; aucune spécification préalable exhaustive n’est demandée.")
 sections.append(("hypotheses","Hypothèses de produit et de service",body))
 body=p("Les lots de filiation, d’historique, de propriété et de réservation portent les plus grandes amplitudes. La comparaison marché est plus directe sur inventaire et quantités que sur le registre autonome de propriété avec conditions d’accord et double date.")
 body+=table(["Lot","Objet","Bas / central / haut JH","Facteurs bas / haut","Cause"],[[e(x["id"]),e(x["label"]),t(x["total"]),str(x["range_factors"][0]).replace(".",",")+" / "+str(x["range_factors"][1]).replace(".",","),e(x["range_cause"])] for x in d["packages"]],"Fourchettes de jugement par lot — classe C, non percentiles")
 body+=p("<strong>Formule :</strong> bas/haut du rôle = centre × facteur du lot, arrondi vers l’extérieur à la demi-journée. Centre = travaux estimés dans le lot. Les facteurs sont des hypothèses de l’analyste, pas des coefficients de complexité placés sur la cartographie d’entrée.")
 body+=p("Le scénario haut conserve les mêmes fonctions, volumes et garanties cibles ; il anticipe plus de corrections. Une exigence nouvelle de règles libres, de volumétrie supérieure ou de reprise sans coopération des producteurs doit être estimée comme variante. Les méthodes ne fournissent ici aucun P50/P80 ni probabilité d’atteinte.")
 body+=table(["Lot","Travaux financés","Décomposition centrale Java, tests inclus"],[[e(x["id"]),e(x["work"]),"<br>".join(e(k)+" : "+n(v)+" JH" for k,v in x["java_breakdown"])] for x in d["packages"]],"Justification du principal effort de réalisation ; bases des autres rôles dans le dossier de lots")
 sections.append(("incertitude","Fourchettes et justification des charges",body))
 body=base.note(p("<strong>Stocks : "+t(cal["incremental_public_months"])+" mois supplémentaires</strong>, scénarios bas / central / haut.")+
 p("Enchaînement séquentiel référentiels puis stocks : <strong>"+t(cal["sequential_public_months"])+" mois</strong> pour les deux familles."))
 body+=p("Le central représente environ <strong>"+n(cal["average_contribution_people"][1])+" personnes en contribution moyenne</strong>. Les capacités maximales ci-dessous sont mobilisées selon la charge, pas facturées à plein temps tout au long des phases. Le budget de réservation d’une équipe complète serait différent.")
 body+=table(["Phase successive","Bas / central / haut mois","Rôle limitant central"],[[e(x["label"]),t(x["duration_months"]),e(roles.get(x["limiting_role"][1],"Plancher de phase"))] for x in cal["phases"]],"Ordre de réalisation : socle, registres, usages, qualification")
 body+=table(["Capacité mobilisable"]+[e(x["id"]) for x in cal["phases"]],[[e(label)]+[n(x["staff"][r]) for x in cal["phases"]] for r,label in roles.items()],"Personnes disponibles par rôle et phase ; une fraction désigne une disponibilité partielle")
 body+=p("<strong>Formule :</strong> durée de phase = maximum du plancher et de la charge de chaque rôle ÷ (personnes mobilisables × 18 JH/mois). Les phases sont successives et les contributions parallèles à l’intérieur. Les planchers reflètent une convention de séquencement, pas une durée mesurée. Le calendrier n’est pas un ordonnancement détaillé prouvé.")
 body+=p("Les 52 JH de coordination Q104 sont répartis 4/16/16/16 entre les phases, en plus de la coordination initiale E101. Toutes les charges sont conservées et les capacités de chaque rôle vérifiées. Les tests développeur accompagnent les lots ; la QA de bout en bout est finalisée en P4.")
 body+=p("La moyenne centrale ne signifie pas qu’une équipe interchangeable de cinq personnes suffit. Il faut pouvoir mobiliser jusqu’à trois Java en P2/P3, deux développeurs d’interface en P3 et deux QA en P4, ainsi que les spécialistes. Le modèle exclut recrutement et attente externe. Une disponibilité différente impose un autre planning.")
 body+=p("Durées calculées avant arrondi : stocks "+t(cal["incremental_months"])+" mois ; cumul séquentiel "+t(cal["sequential_total_months"])+" mois. Le cumul additionne les durées non arrondies puis arrondit au mois supérieur. Aucun lancement en parallèle de deux équipes n’est présumé.")
 sections.append(("delai","Délai et organisation",body))
 lookup={x["id"]:x for x in proof["evidence"]}
 body=p("Treize observations ciblées dans les sources Odoo, Tryton et Axelor ont été enregistrées aux révisions conservées. Les produits n’ont pas été exécutés ; les observations ne constituent pas des mesures de productivité ou de performance.")
 body+=table(["Capacité","Fonctions natives financées","Limite métier","Code comparé"],[[e(c["block"]+" — "+c["name"]),"<br>".join(e(f["id"]+" : "+f["resultat"]) for f in c["functions"]),e(c["boundary"])," ".join(link(lookup[k]["url"],k) for k in c["evidence_ids"])] for c in d["coverage"]],"Dix capacités, vingt-neuf fonctions natives : correspondances partielles et différences explicites")
 body+=table(["Preuve","Observation","Différence FLOW"],[[link(x["url"],x["id"]),e(x["observed"]),e(x["delta"])] for x in proof["evidence"]],"Les produits éclairent le travail ; leurs périmètres ne sont pas copiés intégralement")
 body+=p("Les composants Spring et PostgreSQL fournissent des primitives techniques. Aucun composant ERP complet n’est déclaré transplantable en l’état. La réservation, la propriété et l’historique restent des travaux produit composés sur ces primitives.")
 body+=ul(list(d["crosschecks"].values()))
 sections.append(("marche","Marché, fonctions et limites de transposition",body))
 body=table(["Indicateur","Avant","Après"],[
 ["Capacités comparées distinctes","20 / 88","25 / 88 (+5)"],
 ["Propositions complètes sous hypothèses","6 / 88","16 / 88 (+10)"],
 ["Autres capacités étudiées partiellement","14","9"],
 ["Capacités sans étude comparative","68","63"],
 ["Capacités calibrées empiriquement","0","0"]],"Le cumul compte des identifiants, pas des parts de coût")
 body+=p("Nouvelles comparaisons : Stocktaking, Inventory Ownership Transfer Decision, Inventory Ownership Ledger, Accounting Data Provision et Product Feedback. Les cinq autres stocks avaient déjà une étude partielle ; elles ne sont pas comptées une deuxième fois.")
 old=read("iteration-07-resultats.json");cumids=set(pr["cumulative_ids"]);oldcaps=[c for c in old["coverage"] if c["id"] in cumids]
 body+=table(["Famille étudiée cumulée","Capacités natives"],[[name,"<br>".join(e(c["block"]+" — "+c["name"]) for c in oldcaps if c["path_names"][1]==name)] for name in dict.fromkeys(c["path_names"][1] for c in oldcaps)],"Liste cumulative des 25 capacités étudiées")
 body+=p("<strong>Ce qui progresse :</strong> cinq capacités supplémentaires comparées et les dix stocks chiffrés sous hypothèses, des communs isolés et un cumul sans doublon avec les référentiels. <strong>Ce qui reste fragile :</strong> généalogie, temporalité, propriété et contention, dont les plages restent larges.")
 body+=p("<strong>Suite recommandée :</strong> passer à l’orchestration des processus avec la même méthode. Une nouvelle itération sur les stocks n’est utile qu’en cas d’omission, double compte ou hypothèse majeure nouvelle. L’itération suivante devra préserver les financements de publications, transitions locales et identités déjà retenus.")
 body+=p(str(len(d["checks"]))+" contrôles de sommes, couverture, propriétaires, phases et empreintes ont passé. Ils ne démontrent pas une précision prédictive. Aucun paramètre économique actif, aucune source métier, aucun commit ou déploiement n’a été modifié.")
 body+=p("Dossier : "+link("iteration-10-resultats.json","résultats et matrices")+" · "+link("iteration-10-contrat.json","hypothèses et frontières")+" · "+link("iteration-10-lots.json","lots et bases par rôle")+" · "+link("iteration-10-preuves.json","preuves de code")+" · "+link("iteration-10-estimation.py","calcul reproductible")+" · "+link("iteration-09.html","référentiels09"))
 sections.append(("avancement","Avancement et prochaine étape",body))
 nav="".join('<a href="#'+i+'">'+e(title)+'</a>' for i,title,_ in sections)
 output='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FLOW — Gestion des stocks et cumul — Itération10</title><style>'+base.STYLE+' main p,main li{overflow-wrap:anywhere}</style></head><body><a class="skip" href="#synthese">Aller au contenu</a><header class="hero"><div class="eyebrow">FLOW · Étude d’opportunité · Itération 10</div><h1>Gestion des stocks : charge supplémentaire et cumul</h1><p>Dix capacités, leurs mécanismes communs et les extensions du socle de référentiels.</p><p class="small">29 octobre 2026 · Estimation conditionnelle de classe C · Sources actives inchangées</p></header><div class="layout"><nav class="toc"><strong>Dans ce rapport</strong>'+nav+'</nav><main>'+''.join(base.section(i,title,body) for i,title,body in sections)+'</main></div><footer>Proposition d’opportunité ; aucun total complet du Core System ni probabilité de livraison revendiquée.</footer></body></html>'
 (HERE/"iteration-10.html").write_text(output,encoding="utf-8")
 print(json.dumps({"report":"iteration-10.html","sections":len(sections)}))
if __name__=="__main__":main()
