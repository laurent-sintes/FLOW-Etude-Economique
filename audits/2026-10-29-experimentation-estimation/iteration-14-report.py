"""Audit14 HTML. Figures come exclusively from result JSON."""
import sys,json,html,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def read(n):return json.loads((HERE/n).read_text(encoding="utf-8"))
spec=importlib.util.spec_from_file_location("style07",HERE/"iteration-07-report.py")
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
def e(x):return html.escape(str(x))
def n(x):return f"{x:,.1f}".replace(","," ").replace(".0","").replace(".",",")
def triple(v):return " / ".join(n(x) for x in v)
def tbl(headers,rows,caption):
 return base.table(headers,["<tr>"+"".join("<td>"+str(x)+"</td>" for x in row)+"</tr>" for row in rows],caption)
def ul(items):return "<ul>"+"".join("<li>"+e(x)+"</li>" for x in items)+"</ul>"
def main():
 r=read("iteration-14-resultats.json");inputs=read("iteration-14-entrees.json");c=inputs["contract"];d=inputs["lots"]
 proof=read("iteration-14-preuves.json");xp=read("iteration-14-experiences.json")
 roles=r["roles"];inc=r["incremental"];cum=r["cumulative_estimated"];cal=r["calendar"];progress=r["progress"]
 sections=[]
 def add(id,title,body):sections.append((id,title,base.section(id,title,body)))
 add("decision","Résultat et décision",
 base.note("<p><strong>Trois capacités supplémentaires : "+n(inc["total"][1])+" JH bruts centraux</strong>, de "+n(inc["total"][0])+" à "+n(inc["total"][2])+" JH. Cumul des familles09–14 : <strong>"+n(cum["total"][1])+" JH</strong>, de "+n(cum["total"][0])+" à "+n(cum["total"][2])+" JH. <strong>Le total du Core reste inconnu.</strong></p>")+
 tbl(["Capacité","Question traitée","Limite conservée"],[
 ["ATP — Available-to-Promise","Quelles quantités et dates proposer avec les ressources présentes ou futures admissibles ?","Une proposition ne réserve ni ne confirme."],
 ["CTP — Capable-to-Promise","Quels apports supplémentaires seraient faisables, compte tenu des matières, opérations et capacités ?","Un délai standard ne prouve pas la capacité ; graphe de dépendances borné."],
 ["PTP — Profitable-to-Promise","Quelle option admissible retenir selon ses conséquences économiques et de service ?","Coût inconnu distinct de zéro ; prix confirmé et autorité commerciale conservés."]
 ],"Order Promising, sous-domaine Availability D03 ; BC-046 à BC-048.")+
 "<p>Le niveau utile d’évaluation reste <strong>la famille, ses mécanismes communs et ses travaux propres</strong>. L’ATP possède des analogies plus directes dans les extraits ERP. Le CTP et le PTP exigent davantage de transposition ; leur incertitude reste forte.</p>"+
 "<p><strong>Oui, poursuivre vaut le coup</strong> : essais comparatifs des combinaisons d’algorithmes et des solveurs sur quelques cas représentatifs. Ensuite, traiter les politiques BC-008 et la visibilité des capacités BC-049 encore ouvertes.</p>"+
 "<p>Proposition d’ingénierie assistée par IA, <strong>classe C non calibrée</strong>. Sources actives et application inchangées. Aucun logiciel FLOW n’est implémenté par cette étude, aucune revue humaine revendiquée.</p>")
 add("roles","JH par rôle",
 "<p>Bas / central / haut, même contenu dans les trois scénarios. Les JH développeur bruts incluent leurs tests : "+triple(r["developer_gross_jh"])+" JH. QA indépendante et autres rôles séparés.</p>"+
 tbl(["Rôle","Promesse : bas / central / haut (JH)","Cumul09–14 : central (JH)"],[[e(v),triple(inc["roles"][k]),n(cum["roles"][k][1])] for k,v in roles.items()]+[["TOTAL",triple(inc["total"]),n(cum["total"][1])]],"Aucun ratio de lignes de code, gain IA ni seconde remise de réutilisation.")+
 "<p>Les <strong>"+n(inc["roles"]["expert_optimisation"][1])+" JH de modélisation et optimisation</strong> financent les contraintes propres au CTP, les critères du PTP et la validation des résultats. Timefold est déjà financé en12 ; OR-Tools est ajouté en E142. Leurs algorithmes ne définissent pas les modèles métier ni la manière de les combiner.</p>"+
 tbl(["Rôle","Travaux servant de base au jugement"],[[e(roles[k]),e(v)] for k,v in d["role_basis"].items()],"Estimation d’ingénierie, pas charge de projet observée."))
 add("algorithmes","Stack Java et combinaison des algorithmes",
 "<p><strong>OR-Tools est ajouté à la stack Java/Spring de l’estimation.</strong> Le scénario chiffré retient CP-SAT pour les contraintes discrètes du CTP et réutilise les traitements d’affectation déjà financés en12. Le choix définitif attend des essais : aucune supériorité de performance n’est démontrée ici.</p>"+
 tbl(["Composant","Usage proposé","Financement","État"],[[e(x["name"]),e(x["role"]),e(x["funding"]),e(x["status"])] for x in c["components"]],"Les rôles sont distincts ; il ne s’agit pas de financer deux implémentations complètes de chaque capacité.")+
 tbl(["Étape","Propriétaire","Mécanisme","Garantie/limite"],[[e(x["stage"]),e(x["owner"]),e(x["mechanism"]),e(x["guarantee"])] for x in c["algorithm_chain"]],"La bibliothèque de résolution est une partie de la chaîne. Aucun tri ou filtre de convenance ne prouve la faisabilité globale.")+
 "<p>Le code Java d’OR-Tools expose intervalles optionnels, non-chevauchement et capacité cumulée. Les contraintes CP-SAT utilisent des unités entières ; les statuts distinguent solution faisable, optimum, impossibilité démontrée pour le modèle et recherche indéterminée. Le chargement natif implique une qualification JDK/OS/ressources. <a href='https://developers.google.com/optimization/cp/cp_solver'>Documentation CP-SAT</a> · <a href='https://developers.google.com/optimization/introduction/java'>API Java</a>. Les fichiers lus sont figés au commit de v9.14, qui n’est pas présenté comme la dernière version.</p>"+
 "<h3>Révision pendant cette itération</h3><p>Le premier calcul de "+n(r["refinement"]["initial_central_jh"])+" JH ne distinguait pas suffisamment la composition des algorithmes et ne finançait pas OR-Tools Java. Le candidat final ajoute <strong>"+n(r["refinement"]["delta_central_jh"])+" JH centraux</strong>, sans changer les trois capacités couvertes :</p>"+
 tbl(["Travail explicitement ajouté","JH centraux"],[["E142 — intégration OR-Tools Java/native","48"],["S143 — composition/sélection des algorithmes","72"],["Q141 — qualification et corrections des combinaisons","22"],["Q143 — revues techniques supplémentaires","4"]],"Les146JH sont déjà inclus dans les nouveaux totaux, jamais ajoutés une seconde fois.")+
 "<p><a href='iteration-14-stack-java.json'>Stack Java détaillée</a>. Les modèles métiers B046–048 restent propriétaires des calculs, E142 de l’intégration native et S143 de leur combinaison. Les workers, imports, données et registre de réservation ne sont pas reconstruits.</p>")

 add("financement","Mécanismes communs et unités métier",
 tbl(["Groupe","Travaux","Bas / central / haut (JH)"],[[e(g["id"]),e(g["label"]),triple(g["total"])] for g in r["groups"]],"Les montants propres aux capacités s’ajoutent une fois aux communs et à la qualification.")+
 tbl(["Groupe"]+[e(v) for v in roles.values()]+["Total"],[[e(g["label"])]+[n(g["roles"][k][1]) for k in roles]+[n(g["total"][1])] for g in r["groups"]],"JH centraux par rôle et capacité. Les coûts communs restent visibles, sans ventilation arbitraire.")+
 tbl(["Propriétaire","Patrimoine ou dépendance","Travail nouveau / limite"],[[e(x["owner"]),e(x["asset"]),e(x["delta"])] for x in c["reuse"]],"Un financement par mécanisme. Une capacité non estimée n’est jamais valorisée à zéro.")+
 "<p>Les références ERP servent à comparer les mécanismes ; <strong>leur code n’est pas repris dans Spring</strong>. Le patrimoine FLOW des itérations précédentes est supposé construit pour calculer l’incrément.</p>")
 add("contrat","Hypothèses, frontières et garanties",
 tbl(["Sujet","Contrat proposé"],[[e(a),e(b)] for a,b in c["assumptions"]],"Hypothèses explicites pour l’opportunité, pas spécification approuvée ni performance démontrée.")+
 "<h3>Exclusions</h3>"+ul(c["exclusions"])+
 tbl(["Capacité","Fonctions natives","Garanties attendues et frontière"],[[e(x["block"]+" — "+x["name"]),ul([f["id"]+" : "+f["resultat"] for f in x["functions"]]),ul([g["text"] for g in x["guarantees"]["source_derived"]])+"<p>"+e(x["boundary"])+"</p>"] for x in r["coverage"]],"Les neuf fonctions sont conservées ; garanties documentaires attendues, pas garanties logicielles acquises."))
 body="<p>Les centrales proviennent des travaux proposés ci-dessous. Facteurs de bornes = sensibilité aux reprises, par jugement non calibré ; arrondis extérieurs au demi-JH. Une exigence hors contrat oblige à réestimer.</p>"
 for lot in r["packages"]:
  body+="<article class='card'><h3>"+e(lot["id"]+" — "+lot["label"])+"</h3><p><strong>"+triple(lot["total"])+" JH</strong> · facteurs bas/haut "+triple(lot["factors"])+".</p><p>"+e(lot["work"])+"</p>"
  actions=[["Java",e(a["action"]),n(a["jh"])] for a in lot["java_actions"]]+[["Interface",e(a["action"]),n(a["jh"])] for a in lot["frontend_actions"]]
  if actions:body+=tbl(["Réalisation","Action","JH centraux"],actions,"Tests développeur et corrections d’assemblage distingués.")
  body+="<p><strong>Modélisation :</strong> "+e(lot["expert_basis"])+"</p><p>"+e(lot["range_reason"])+"</p><p class='small'>Observations : "+", ".join("<a href='#proof-"+e(ref)+"'>"+e(ref)+"</a>" for ref in lot["evidence"])+". "+e(lot["origin"])+"</p></article>"
 add("lots","Origine des charges",body)
 add("delais","Délai et équipe",
 "<p><strong>"+triple(cal["incremental_public_months"])+" mois</strong> pour cette famille, soit "+n(cal["incremental_public_months"][1])+" mois centraux. Deux développeurs Java, un développeur interface au maximum ; spécialiste modélisation jusqu’à une personne pendant les calculs, QA jusqu’à deux en qualification, autres contributions fractionnées. Contribution moyenne centrale : "+n(cal["average_contribution_people"][1])+" personnes à18JH/mois. Disponibilités non confirmées.</p>"+
 base.note("<p><strong>Durée d’une phase = maximum du plancher de séquence et des charges par rôle / (effectif mobilisable ×18JH/mois).</strong> Les rôles ne sont pas interchangeables. Ces durées ne viennent pas d’un calcul COCOMO.</p>")+
 tbl(["Phase","Mois bas / central / haut avant arrondi","Rôle limitant au central"],[[e(ph["label"]),triple(ph["duration_months"]),e(roles.get(ph["limiting_role"][1],ph["limiting_role"][1]))] for ph in cal["phases"]],"Durées brutes additionnées, puis arrondi supérieur au mois.")+
 tbl(["Phase"]+[e(v) for v in roles.values()],[[e(ph["label"])]+[n(ph["staff"][k]) for k in roles] for ph in cal["phases"]],"Personnes mobilisables par rôle ; ce sont des plafonds de capacité, pas des taux d’occupation permanents.")+
 "<p>La succession stricte des familles09–14 donne "+triple(cal["sequential_public_months"])+" mois. Cette information est conservée pour la traçabilité ; <strong>elle n’est pas un calendrier optimisé du programme</strong>, ni le délai du Core complet. Un programme multiéquipes pourrait organiser d’autres chevauchements, avec dépendances et coordination à dimensionner.</p>")
 add("incertitude","Incertitude et limites de méthode",
 "<p><strong>Classe C pour les trois capacités ; réserves fortes sur CTP et PTP.</strong> Les fourchettes additionnent des hypothèses basses ou hautes simultanées. Elles ne sont ni P10/P90 ni probabilités de dépassement. La couverture peut progresser sans preuve nouvelle de productivité.</p>"+
 tbl(["Zone","Capacités","Conséquence"],[[e(x["label"]),e(", ".join(x["caps"])),e(x["effect"])] for x in c["risks"]],"L’incertitude de données opérationnelles ne se résout pas par un solveur.")+
 "<p>Les réserves antérieures sont conservées : "+e(", ".join(r["previous_reserves_preserved"]))+". Aucun de leurs montants n’est révisé par cette itération.</p>"+
 tbl(["Méthode","Usage réel"],[[e(k),e(v)] for k,v in r["crosschecks"].items()],"Pas de validation croisée chiffrée COSMIC/COCOMO/ISBSG revendiquée."))
 add("experiences","Sept vérifications du raisonnement",
 tbl(["Cas inventé","Résultat et conséquence"],[[e(x["question"]),e(x["explanation"])] for x in xp["cases"]],"Calculs analytiques ciblés, pas tests des produits ni mesure de productivité.")+
 "<p>Ils éprouvent le décompte des obligations, la cohérence multilignes, la capacité finie, le coût inconnu et la revalidation. Les scripts n’exécutent ni les ERP ni un Core Spring. Les garanties de production restent à réaliser et tester.</p>")
 body="<p>Neuf observations ciblées dans trois ERP OSS, complétées par trois observations dans le code Java d’OR-Tools. Commits et empreintes contrôlés. Aucun jugement d’absence produit n’est déduit d’une absence dans un extrait.</p>"
 for x in proof["evidence"]:
  body+="<article class='card' id='proof-"+e(x["id"])+"'><h3>"+e(x["id"]+" — "+x["repository"])+"</h3><p>"+e(x["observed"])+"</p><p><strong>Transposition et limite :</strong> "+e(x["flow_delta"])+"</p><p><a href='"+e(x["url"])+"'>Source au commit figé</a> · lignes "+e(str(x["line_ranges"]))+"</p><p class='checksum'>Commit "+e(x["commit"])+" · SHA256 "+e(x["sha256"])+"</p></article>"
 body+="<p><a href='iteration-14-preuves.json'>Chemins, empreintes et extraits exacts</a>.</p>"
 add("preuves","Ce que montre le code du marché",body)
 add("avancement","Avancement et cumul",
 tbl(["Indicateur","Avant","Après","Variation"],[
 ["Capacités comparées","53/88","56/88 — 63,6%","+3"],
 ["Propositions complètes sous hypothèses, non calibrées","53","56","+3"],
 ["Comparaisons partielles hors propositions complètes","0","0","0"],
 ["Capacités non comparées","35","32","−3"],
 ["Capacités avec calibration empirique","0","0","0"]
 ],"Couverture en nombre de capacités, pas pourcentage de coût du Core ni mesure de précision.")+
 "<p><strong>Ce qui progresse :</strong> trois décisions de promesse distinguées, nouvelles contraintes CTP/PTP financées explicitement, rôle du solveur délimité, revalidation séparée de la confirmation et dépendances BC008/049 rendues visibles. <strong>Ce qui ne progresse pas :</strong> aucune charge observée compatible n’est ajoutée ; on ne peut pas annoncer un taux de capacités dont la précision serait statistiquement garantie.</p>"+
 tbl(["Code","Identifiant natif","Capacité"],[[e(x["block"]),e(x["id"]),e(x["name"])] for x in sorted(r["cumulative_coverage"],key=lambda x:x["block"])],"Les56 capacités uniques cumulées ; anciens pilotes non ajoutés aux charges.")+
 "<h3>Suite utile</h3><p>"+e(r["next_iteration"]["recommendation"])+"</p><p>Une simple relecture apporterait peu ; des essais comparatifs produiraient une information nouvelle sur les stratégies de calcul et leurs limites, sans fournir à eux seuls une productivité en JH. Réouvrir en cas de :</p>"+ul(r["next_iteration"]["reopen_triggers"]))
 add("verification","Vérification et pièces",
 "<p>"+str(len(r["checks"]))+" contrôles de calcul, de capacité des rôles, de provenance, d’intégrité des extraits et de conservation des sources actives/audit13. La vérification finale confirme la régénération identique et le rendu navigateur. Ces contrôles ne démontrent pas la précision des JH.</p>"+
 "<p><a href='iteration-14-resultats.json'>Résultats</a> · <a href='iteration-14-entrees.json'>Hypothèses et lots</a> · <a href='iteration-14-verification.json'>Vérification finale</a> · <a href='iteration-13.html'>Itération13</a>.</p>")
 nav="<nav class='toc' aria-label='Sommaire'><strong>Dans cette itération</strong>"+"".join("<a href='#"+id+"'>"+e(title)+"</a>" for id,title,b in sections)+"</nav>"
 doc="<!doctype html><html lang='fr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>FLOW — Itération14 : promesse ATP, CTP et PTP</title><style>"+base.STYLE+"\nmain p,main li,td{overflow-wrap:anywhere}.card{margin-bottom:1rem}</style></head><body><a class='skip' href='#decision'>Aller au contenu</a><header class='hero'><div class='eyebrow'>Étude d’opportunité FLOW · Spring · 29 octobre2026</div><h1>Promesse : disponibilité, faisabilité et choix économique</h1><p>Itération14 · ATP, CTP, PTP · Trois capacités et neuf fonctions. Réutiliser le patrimoine, identifier les contraintes nouvelles et expliciter les limites.</p></header><div class='layout'>"+nav+"<main>"+"".join(b for id,title,b in sections)+"</main></div><footer>Proposition d’audit conditionnelle ; aucune modification de l’économie active.</footer></body></html>"
 for a,b in [("Itération14","Itération 14"),("Itération13","Itération 13"),("familles09","familles 09"),("octobre2026","octobre 2026"),("Les56","Les 56"),("à18JH","à 18 JH"),("×18JH","×18 JH")]:doc=doc.replace(a,b)
 (HERE/"iteration-14.html").write_text(doc,encoding="utf-8")
 print("Report14 generated")
if __name__=="__main__":main()
