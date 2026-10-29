"""Frozen source observations and small analytical counterexamples; audit only."""
import json,hashlib,itertools
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(n):return json.loads((HERE/n).read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(HERE/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
old=read("iteration-05-plan-preuves.json")
ranges={"PLAN-OD-01":[[411,428],[454,472],[499,527]],"PLAN-OD-02":[[1269,1324]],"PLAN-TR-01":[[302,364]],"PLAN-TR-02":[[163,221],[274,299]],"PLAN-AX-01":[[368,418],[457,507]],"PLAN-AX-02":[[560,636]],"PLAN-AX-03":[[61,95]]}
observed={
"PLAN-OD-01":"Positions disponibles/projetées et approvisionnements en cours ; sous le minimum, cible moins projection, arrondi au multiple et horizon de lieu/date.",
"PLAN-OD-02":"Filtrage dates, unité, quantité et variante ; préclassement fournisseurs puis choix dans les lignes du premier partenaire admissible.",
"PLAN-TR-01":"Parcours daté des positions projetées : première rupture sous minimum et quantité minimale dans l’intervalle.",
"PLAN-TR-02":"Rapprochement des nouvelles demandes avec les demandes déjà liées à des achats ; cible moins position, conversion/arrondi et origine conservée. Ce code est une analogie, pas un algorithme validé pour FLOW.",
"PLAN-AX-01":"Tri par date/type/séquence et nouvelle passe après proposition, garde-fou1000 itérations ; traitement spécifique des lignes déjà éditées. Rien dans l’extrait ne démontre un optimum.",
"PLAN-AX-02":"Minimum/multiple fournisseur, rapprochement avec proposition précédente, distinction proposition/arrivée estimée, dates et origines conservées.",
"PLAN-AX-03":"Cible moins quantité courante/future avec minimum de réapprovisionnement et plafond éventuel."}
evidence=[]
for x in old["evidence"]:
 if x["id"] not in ranges:continue
 evidence.append(dict(id=x["id"],local_path=x["path"],commit=x["commit"],sha256=sha(ROOT/x["path"]),url=x["url"],line_ranges=ranges[x["id"]],observed=observed[x["id"]],delta=x["limits"],kind="implementation_read",review="Extraits relus dans12 ; aucun test OSS exécuté."))
def add(i,path,commit,repo,rel,r,obs,delta):
 evidence.append(dict(id=i,local_path=path,commit=commit,sha256=sha(ROOT/path),url=f"https://github.com/{repo}/blob/{commit}/{rel}#L{r[0][0]}",line_ranges=r,observed=obs,delta=delta,kind="implementation_read",review="Extraits relus ; aucun test OSS exécuté."))
add("TR-FORECAST","tmp/tryton-code-audit-2026-10-28/modules/stock_forecast/forecast.py","e011222dc305c431677e586706fd241dffe02236","tryton/tryton","modules/stock_forecast/forecast.py",[[339,383],[394,435]],
"Le calcul nommé quantity_executed agrège des mouvements non annulés selon dates effectives ou prévues et exclut ceux issus de prévision. Les mouvements de prévision sont ensuite générés sur la quantité résiduelle répartie par dates.",
"Le nom ne signifie pas uniquement des réalisations physiques constatées. Les règles FLOW de consommation des commandes, granularités, versions et limites nécessitent un modèle propre ; aucune statistique de prévision démontrée.")
add("AX-FORECAST","tmp/oss-audit-axelor/axelor-supplychain/src/main/java/com/axelor/apps/supplychain/service/MrpForecastServiceImpl.java","e7cbea53bae88d2540f59a70b09bf0f326f1022e","axelor/axelor-open-suite","axelor-supplychain/src/main/java/com/axelor/apps/supplychain/service/MrpForecastServiceImpl.java",[[33,59]],
"Confirmation seulement depuis brouillon ; annulation seulement depuis états autorisés, dans une transaction avec retour arrière sur exception.",
"Une validation d’état ne prouve pas qualification des unités, versions/horizons, qualité de prévision, cohérence interplans ou estimation de service.")
manifest=read("iteration-12-code-timefold/manifest.json");f={Path(x["local_path"]).name:x for x in manifest}
def tf(i,name,r,obs,delta,kind):
 x=f[name];evidence.append(dict(id=i,local_path=x["local_path"],commit=x["commit"],sha256=x["sha256"],url=x["url"],line_ranges=r,observed=obs,delta=delta,kind=kind,review="Code figé lu ; combinaison Spring et solveur non exécutée."))
tf("T-MANAGER","DefaultSolverManager.java",[[40,72],[110,166]],"Pool de threads, registre des jobs en ConcurrentHashMap, refus d’un identifiant déjà en résolution, arrêt anticipé et retrait du job à la fin.",
"Ce gestionnaire ne fournit pas de journal durable des problèmes/résultats. FLOW doit persister, reconnaître l’interruption et relancer depuis un instantané ; aucune reprise de l’état de recherche en mémoire présumée.","implementation_read")
tf("T-API","SolverManager.java",[[22,74]],"Contrat de résolution asynchrone de plusieurs problèmes du même domaine, avec threads de calcul et de consommation des meilleures solutions.",
"L’API ne définit ni les contraintes FLOW, ni leur validité, ni un optimum. Validation métier et modèle à financer séparément.","api_contract_read")
tf("T-POM","pom.xml",[[20,58]],"Le build du commit figé référence Spring Boot3.5.5.","Référence de comparaison de l’itération05 ; version de production supportée à qualifier dansE121. Aucune recommandation de conserver cette génération.","build_configuration_read")
for x in evidence:
 ls=(ROOT/x["local_path"]).read_text(encoding="utf-8").splitlines()
 assert all(1<=a<=z<=len(ls) for a,z in x["line_ranges"]),x["id"]
write("iteration-12-preuves.json",{"id":"iteration-12-preuves","date":"2026-10-29","evidence":evidence,"license":{"product":"Timefold OSS","commit":f["LICENSE.txt"]["commit"],"url":f["LICENSE.txt"]["url"],"sha256":f["LICENSE.txt"]["sha256"],"observation":"Fichier de licence Apache2.0 lu. Produits hébergés et fonctions commerciales non supposés inclus. Dépendances/notices à qualifier dansE121."},"docs":[{"url":"https://docs.timefold.ai/timefold-solver/1.x/quickstart/spring-boot/spring-boot-quickstart","observed":"Intégration Spring et définition d’un modèle/contraintes propres à l’application ; documentation1.x vivante distincte du code figé."},{"url":"https://docs.timefold.ai/timefold-solver/1.x/optimization-algorithms/overview","observed":"Recherche de la meilleure solution dans le temps disponible ; aucune garantie générale d’optimum, taille du problème déterminante."}],"limitations":["12 observations de code dont une API et une configuration ; aucun essai OSS ou benchmark de performance exécuté.","Odoo/Tryton/Axelor sont des comparables fonctionnels ; aucun transplant de leur code dans Spring retenu.","BC040/041/042/044 ont des correspondances indirectes : appliquer un seuil ne démontre pas son optimisation.","Aucun temps humain observé ni équivalence lignes de code/JH."]})
# An exhaustive small instance makes the local/global distinction concrete.
demands=["A","B"];sources=["S1","S2"];cost={("A","S1"):1,("A","S2"):3,("B","S1"):2}
def valid(a):
 vals=[v for v in a.values() if v]
 return len(vals)==len(set(vals)) and all(v is None or (k,v) in cost for k,v in a.items())
def score(a):return(sum(v is not None for v in a.values()),-sum(cost[(k,v)] for k,v in a.items() if v))
solutions=[dict(zip(demands,v)) for v in itertools.product([None]+sources,repeat=2)]
solutions=[a for a in solutions if valid(a)]
best=max(solutions,key=score);greedy={"A":"S1","B":None}
assert score(best)[0]==2 and score(greedy)[0]==1
protected=max([a for a in solutions if a["B"]=="S1"],key=score)
assert protected["A"]=="S2"
forecast=100;orders=60;residual=max(0,forecast-orders);assert orders+residual==100
available_day3=sum(q for day,q in [(0,20),(5,30)] if day<=3);assert available_day3==20
write("iteration-12-experiences.json",{"id":"iteration-12-experiences","status":"4 contre-exemples analytiques exécutés sur données inventées, pas tests du futur produit","cases":[{"question":"Une affectation locale moins chère peut-elle laisser une demande évitablement non couverte ?","input":{"demand_each":1,"capacity_each":1,"costs":[{"demand":a,"source":b,"cost":c} for (a,b),c in cost.items()]},"greedy":greedy,"best_exhaustive":best,"served":[1,2],"lesson":"Les ressources partagées peuvent nécessiter une comparaison conjointe ; cela ne justifie pas un solveur pour chaque capacité."},{"question":"Le lien engagé deB reste-t-il protégé ?","result":protected,"lesson":"Un coût inférieur ne peut pas justifier la rupture silencieuse d’un engagement."},{"question":"Prévision100 et commandes60 représentent-elles160 de besoin ?","residual":residual,"retained_demand":orders+residual,"lesson":"La règle de consommation doit être explicite et testable ; cette règle simple n’est pas une politique Beaumanoir."},{"question":"Une arrivée au jour5 couvre-t-elle une demande au jour3 ?","available_day3":available_day3,"naive_total":50,"lesson":"Les dates conditionnent l’admissibilité ; conserver les quantités ne suffit pas."}],"passed":4,"limits":["Aucun JH déduit des temps d’exécution ou de la taille de ces exemples.","Timefold n’a pas été exécuté ; l’énumération exhaustive n’est utilisée que comme référence de ce minuscule exemple.","Ces exemples ne valident ni la qualité des politiques ni les performances du périmètre réel."]})
print(json.dumps({"evidence":len(evidence),"analytical_cases":4}))
