"""Readable audit13 report; all figures derived from the result."""
import sys,json,html,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def read(n):return json.loads((HERE/n).read_text(encoding="utf-8"))
spec=importlib.util.spec_from_file_location("style07",HERE/"iteration-07-report.py")
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
def e(x):return html.escape(str(x))
def n(x):
 return f"{x:,.1f}".replace(","," ").replace(".0","").replace(".",",")
def triple(v):return " / ".join(n(x) for x in v)
def tbl(headers,rows,caption):
 return base.table(headers,["<tr>"+"".join("<td>"+str(x)+"</td>" for x in row)+"</tr>" for row in rows],caption)
def ul(items):return "<ul>"+"".join("<li>"+e(x)+"</li>" for x in items)+"</ul>"
def main():
 r=read("iteration-13-resultats.json");i=read("iteration-13-entrees.json");c=i["contract"];d=i["lots"];p=read("iteration-13-preuves.json");xp=read("iteration-13-experiences.json")
 roles=r["roles"];inc=r["incremental"];cum=r["cumulative_estimated"];cal=r["calendar"];sections=[]
 def add(id,title,body):sections.append((id,title,base.section(id,title,body)))
 add("decision","Résultat et décision",
 base.note("<p><strong>Huit capacités supplémentaires, 24 fonctions : "+n(inc["total"][1])+" JH centraux.</strong> Fourchette "+triple([inc["total"][0],inc["total"][2]])+" JH. Le cumul des familles09–13 atteint <strong>"+n(cum["total"][1])+" JH</strong>, de "+n(cum["total"][0])+" à "+n(cum["total"][2])+" JH. <strong>Ce n’est pas le total du Core System.</strong></p>")+
 "<p>Cette itération propose le cycle générique des commandes et engagements. Les sources des trois ERP montrent des mécanismes comparables, mais pas une couverture complète des particularités FLOW. Le niveau utile de chiffrage reste <strong>la famille avec ses mécanismes communs</strong> ; les capacités servent à décrire les écarts et à restituer les travaux propres.</p>"+
 "<p><strong>Oui, une autre itération vaut le coup :</strong> traiter la promesse ATP/CTP/PTP et sa frontière avec réservation/protection. Refaire la même famille sans information nouvelle ne justifierait pas davantage de précision.</p>"+
 "<p>Sources actives, application et chiffres économiques inchangés. Les JH ci-dessous sont une proposition d’ingénierie assistée par IA, classe C, non calibrée ; aucune validation humaine revendiquée.</p>"+
 tbl(["Ce qui a progressé","Ce qui reste incertain"],[
 ["8 capacités supplémentaires reliées à des mécanismes lus dans Odoo, Tryton et Axelor.","Le code ne donne pas les jours effectivement consacrés à ces fonctions."],
 ["Propriétaire identifié pour les états, faits, reliquats et raccords avec les familles10–12.","Retours combinés, restructuration après engagement et accords de consignation."],
 ["Quatre exemples analytiques rendent visibles les erreurs de double compte ou d’autorité.","Les exemples n’exécutent ni les ERP ni un futur Core Spring."],
 ["Charge par rôle et calendrier explicite, sans addition d’anciens pilotes.","35 capacités restent non comparées ; les réserves de planification12 restent ouvertes."]
 ],"Progrès de la méthode, sans prétendre réduire statistiquement l’incertitude."))
 add("roles","JH par rôle",
 "<p>Ordre des valeurs : <strong>bas / central / haut</strong>. Tous les rôles sont inclus dans le total brut de réalisation. Les développeurs représentent "+triple(r["developer_gross_jh"])+" JH, tests développeur compris ; la QA indépendante reste séparée.</p>"+
 tbl(["Rôle","Commandes : bas / central / haut (JH)","Cumul09–13 : central (JH)"],[[e(label),triple(inc["roles"][key]),n(cum["roles"][key][1])] for key,label in roles.items()]+[["TOTAL",triple(inc["total"]),n(cum["total"][1])]],"Charge additionnelle et cumul ; aucun gain IA ni seconde remise de réutilisation.")+
 "<p>Le zéro en modélisation/optimisation signifie <strong>aucun nouveau solveur dans cette famille</strong>. Les 350 JH centraux de ce rôle financés en12 restent dans le cumul. Les montants d’achat, le Run et le pilotage du programme ne sont pas ajoutés.</p>"+
 tbl(["Rôle","Base du jugement de charge"],[[e(roles[k]),e(v)] for k,v in d["role_basis"].items()],"Les valeurs ne sont pas des charges de projet observées."))
 add("allocation","Mécanismes communs et capacités",
 "<p>Les mécanismes communs représentent "+triple(r["common"]["total"])+" JH, qualification et coordination comprises ; les particularités des huit capacités représentent "+triple(r["direct"]["total"])+" JH. Une ligne de capacité ne peut pas être vendue comme un coût autonome sans sa quote-part de patrimoine partagé. Aucune ventilation arbitraire de ce patrimoine n’est imposée.</p>"+
 tbl(["Propriétaire","Travaux propres","Bas / central / haut (JH)"],[[e(g["id"]),e(g["label"]),triple(g["total"])] for g in r["groups"]],"Somme des groupes égale au total de la famille.")+
 tbl(["Groupe"]+[e(v) for v in roles.values()]+["Total"],[[e(g["label"])]+[n(g["roles"][k][1]) for k in roles]+[n(g["total"][1])] for g in r["groups"]],"JH centraux par rôle et unité métier ; tableau défilant horizontalement sur petit écran.")+
 tbl(["Déjà financé par","Patrimoine","Travail nouveau ici"],[[e(x["owner"]),e(x["asset"]),e(x["delta"])] for x in c["reuse"]],"Chaque mécanisme a un seul propriétaire de financement."))
 add("hypotheses","Périmètre et garanties proposées",
 tbl(["Sujet","Contrat retenu pour l’estimation"],[[e(a),e(b)] for a,b in c["assumptions"]],"Hypothèses bornées proposées pour une étude d’opportunité, pas spécification approuvée.")+
 "<h3>Exclusions</h3>"+ul(c["exclusions"])+
 "<h3>Frontières métier conservées</h3>"+
 tbl(["Capacité","Fonctions natives","Frontière et autorité externe"],[[e(x["block"]+" — "+x["name"]),ul([f["id"]+" : "+f["resultat"] for f in x["functions"]]),e(x["boundary"])+"<p>"+e(x["core_integration"]["integration_or_external_authority"])+"</p>"] for x in r["coverage"]],"Huit capacités de Order Lifecycle Management, dans Order Management."))
 body="<p>Chaque central est une décomposition de travail proposée. Les facteurs de bornes expriment la sensibilité aux reprises ; ce ne sont ni des scores métier ni des coefficients COCOMO. Les bornes sont arrondies vers l’extérieur au demi-JH. <strong>Même contenu dans les trois scénarios.</strong></p>"
 for lot in r["packages"]:
  body+="<article class='card'><h3>"+e(lot["id"]+" — "+lot["label"])+"</h3><p><strong>"+triple(lot["total"])+" JH</strong> · facteurs bas/haut "+triple(lot["factors"])+".</p><p>"+e(lot["work"])+"</p>"
  actions=[["Java",e(a["action"]),n(a["jh"])] for a in lot["java_actions"]]+[["Interface",e(a["action"]),n(a["jh"])] for a in lot["frontend_actions"]]
  if actions:body+=tbl(["Réalisation","Travail","JH centraux"],actions,"Tests développeur inclus ; corrections croisées identifiées séparément.")
  body+="<p>"+e(lot["range_reason"])+"</p><p class='small'>Observations : "+", ".join("<a href='#proof-"+e(ref)+"'>"+e(ref)+"</a>" for ref in lot["evidence"])+". "+e(lot["origin"])+"</p></article>"
 add("lots","Origine des charges par lot",body)
 add("delais","Délai et mobilisation",
 "<p><strong>"+triple(cal["incremental_public_months"])+" mois pour cette famille</strong>, soit "+n(cal["incremental_public_months"][1])+" mois centraux. Phases séquentielles, deux développeurs Java et un développeur interface au maximum dans ce scénario, autres rôles mobilisés selon les phases ; QA jusqu’à deux personnes en qualification. Contribution moyenne centrale : "+n(cal["average_contribution_people"][1])+" personnes à 18 JH/mois. Effectifs disponibles non confirmés.</p>"+
 base.note("<p><strong>Durée d’une phase = maximum du plancher de séquence et de chaque charge de rôle / (effectif mobilisable ×18JH par mois).</strong> Les contributions fractionnées sont possibles ; les disponibilités affichées sont des plafonds, pas des personnes occupées à plein temps.</p>")+
 tbl(["Phase","Mois bas / central / haut avant arrondi","Rôle limitant au central"],[[e(ph["label"]),triple(ph["duration_months"]),e(roles.get(ph["limiting_role"][1],ph["limiting_role"][1]))] for ph in cal["phases"]],"Somme des durées non arrondies, puis arrondi supérieur au mois.")+
 tbl(["Phase"]+[e(v) for v in roles.values()],[[e(ph["label"])]+[n(ph["staff"][key]) for key in roles] for ph in cal["phases"]],"Nombre maximal de personnes mobilisables par rôle pendant chaque phase.")+
 "<p>Si les familles09,10,11,12,13 étaient réalisées strictement l’une après l’autre avec leurs équipes proposées, la somme serait <strong>"+triple(cal["sequential_public_months"])+" mois</strong>. Cette somme conserve l’information de durée ; <strong>elle n’est pas un calendrier de programme optimisé</strong>, ni un délai complet du Core. Les dépendances et les travaux parallèles devront être planifiés à l’échelle du programme.</p>")
 add("incertitude","Incertitude et limites",
 "<p><strong>Classe C pour les huit capacités.</strong> L’étude peut discuter un ordre de grandeur sous les hypothèses affichées, mais aucune probabilité de dépassement ni précision statistique n’est établie. Les bornes du cumul additionnent les scénarios bas ou hauts simultanés ; elles ne sont pas un P10/P90. Les taux de couverture ne deviennent pas des taux de budget couvert.</p>"+
 tbl(["Zone","Capacités","Conséquence"],[[e(x["label"]),e(", ".join(x["caps"])),e(x["effect"])] for x in c["risks"]],"Réserves fortes supplémentaires sur BC025/026/027 ; consignation à analogie plus partielle.")+
 "<p>Les réserves fortes de12 sur BC040,041,042,044 sont conservées. Cette itération ne les résout pas et ne modifie pas leurs montants.</p>"+
 tbl(["Méthode","Usage réel dans cette itération"],[[e(k),e(v)] for k,v in r["crosschecks"].items()],"Pas de validation croisée chiffrée revendiquée entre COSMIC, COCOMO et ISBSG."))
 add("experiences","Quatre vérifications du découpage",
 tbl(["Cas inventé","Résultat analytique et conséquence"],[[e(x["question"]),e(x["explanation"])] for x in xp["cases"]],"Exemples de raisonnement calculés, pas tests d’un produit ni échantillon statistique.")+
 "<p>Ils montrent pourquoi un même champ « quantité réalisée » ou un unique statut de clôture ne suffit pas. Ils ne démontrent ni performance, ni justesse d’une future implémentation, ni productivité de l’équipe.</p>")
 body="<p>Lecture ciblée de fichiers source locaux figés par commit et empreinte. Les mécanismes ERP sont des références de conception ; leur code n’est pas incorporé à Spring. Une absence dans l’extrait ne démontre pas une absence dans le produit.</p>"
 for x in p["evidence"]:
  body+="<article class='card' id='proof-"+e(x["id"])+"'><h3>"+e(x["id"]+" — "+x["repository"])+"</h3><p>"+e(x["observed"])+"</p><p><strong>Écart FLOW :</strong> "+e(x["flow_delta"])+"</p><p class='small'><a href='"+e(x["url"])+"'>Source au commit figé</a> · lignes "+e(str(x["line_ranges"]))+"</p><p class='checksum'>"+e(x["commit"])+" · SHA256 "+e(x["sha256"])+"</p></article>"
 body+="<p><a href='iteration-13-preuves.json'>Registre avec chemins, empreintes et extraits exacts</a>.</p>"
 add("preuves","Comparaison avec le code du marché",body)
 progress=r["progress"]
 add("avancement","Avancement cumulé",
 tbl(["Indicateur","Avant","Après","Progression"],[
 ["Capacités comparées aux mécanismes du marché","45/88","53/88 — 60,2%","+8"],
 ["Propositions complètes sous hypothèses, non calibrées","45/88","53/88 — 60,2%","+8"],
 ["Comparaisons partielles hors propositions complètes","0","0","0"],
 ["Capacités non comparées","43","35","−8"],
 ["Capacités avec calibration empirique","0","0","0"]
 ],"« Complète » porte sur la proposition conditionnelle de contenu, pas sur une couverture ERP ni une preuve de précision.")+
 "<p>Il n’existe pas encore de nombre défendable de capacités dont l’incertitude serait statistiquement « raisonnable ». Le dispositif distingue donc la couverture conditionnelle et les réserves explicites. L’ajout de ces huit capacités étend le périmètre et ferme côté Orders des contrats jusque-là simulés dans les hypothèses ; <strong>aucun logiciel n’a été implémenté dans cette étude</strong>.</p>"+
 tbl(["Code","Identifiant natif","Capacité"],[[e(x["block"]),e(x["id"]),e(x["name"])] for x in sorted(r["cumulative_coverage"],key=lambda x:x["block"])],"Les 53 capacités uniques cumulées, sans addition des anciens pilotes.")+
 "<h3>Suite recommandée</h3><p>"+e(r["next_iteration"]["recommendation"])+"</p><p>"+e(r["next_iteration"]["deferred"])+"</p><p>Réouvrir cette famille seulement en cas de :</p>"+ul(r["next_iteration"]["reopen_triggers"]))
 add("verification","Reproductibilité",
 "<p>"+str(len(r["checks"]))+" contrôles de calcul, capacité des rôles, unicité des financements, cohérence des cumuls, empreintes des sources actives et conservation de l’audit12. La vérification finale ajoute le contrôle du rendu et la régénération à l’identique. Ces contrôles portent sur la cohérence du dossier, pas sur la précision des JH.</p>"+
 "<p><a href='iteration-13-resultats.json'>Résultats détaillés</a> · <a href='iteration-13-entrees.json'>Hypothèses et lots</a> · <a href='iteration-13-verification.json'>Vérification finale</a> · <a href='iteration-12.html'>Itération12</a>.</p>")
 nav="<nav class='toc' aria-label='Sommaire'><strong>Dans cette itération</strong>"+"".join("<a href='#"+id+"'>"+e(title)+"</a>" for id,title,b in sections)+"</nav>"
 doc="<!doctype html><html lang='fr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>FLOW — Itération 13 : commandes et engagements</title><style>"+base.STYLE+"\nmain p,main li,td{overflow-wrap:anywhere}.card{margin-bottom:1rem}"+ "</style></head><body><a class='skip' href='#decision'>Aller au contenu</a><header class='hero'><div class='eyebrow'>Étude d’opportunité FLOW · Spring · 29 octobre 2026</div><h1>Commandes et engagements</h1><p>Itération 13 · D04 · Huit capacités. Comparer les mécanismes du marché, isoler les travaux communs, estimer l’investissement et conserver les limites.</p></header><div class='layout'>"+nav+"<main>"+"".join(b for id,title,b in sections)+"</main></div><footer>Proposition d’audit conditionnelle. Aucun montant appliqué aux sources économiques actives.</footer></body></html>"
 (HERE/"iteration-13.html").write_text(doc,encoding="utf-8")
 print("Report13 generated")
if __name__=="__main__":main()
