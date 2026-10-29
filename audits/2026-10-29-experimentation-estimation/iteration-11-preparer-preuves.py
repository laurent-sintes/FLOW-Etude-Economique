"""Freeze inspected source observations for iteration11; audit only."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
def read(n):return json.loads((HERE/n).read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(HERE/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
old=read("iteration-05-orch-preuves.json")
selected={"OD-ACTIVITY","OD-AUTOMATION","TY-WORKFLOW","TY-QUEUE","TY-TRIGGER","AX-TASK","AX-WORKFLOW"}
evidence=[]
for x in old["evidence"]:
 if x["id"] not in selected:continue
 assert sha(ROOT/x["local_path"])==x["sha256"],x["id"]
 y={k:x[k] for k in ["id","local_path","commit","sha256","url","observed","line_ranges"]}
 y["delta"]=x["limit"];y["kind"]="implementation_read"
 if y["id"]=="TY-QUEUE":
  y["line_ranges"]=[[140,211]]
  y["observed"]="Exécution sous utilisateur/contexte, verrouillage de la tâche, fin enregistrée ; remise en attente des tâches prises mais non terminées et sans erreur liée."
 y["review"]="Extraits relus dans cette itération ; aucun test produit exécuté."
 evidence.append(y)
pins={"odoo":("tmp/odoo20-audit/","299075f17026b830a9755f3c43f3e83143995946","odoo/odoo"),"tryton":("tmp/tryton-code-audit-2026-10-28/","e011222dc305c431677e586706fd241dffe02236","tryton/tryton"),"axelor":("tmp/oss-audit-axelor/","e7cbea53bae88d2540f59a70b09bf0f326f1022e","axelor/axelor-open-suite")}
def add(i,product,path,ranges,observed,delta):
 root,commit,repo=pins[product];local=root+path
 evidence.append(dict(id=i,local_path=local,commit=commit,sha256=sha(ROOT/local),url=f"https://github.com/{repo}/blob/{commit}/{path}#L{ranges[0][0]}",line_ranges=ranges,observed=observed,delta=delta,kind="implementation_read",review="Extraits relus ; aucun test produit exécuté."))
add("AX-TEMPLATE","axelor","axelor-project/src/main/java/com/axelor/apps/project/service/ProjectTemplateServiceImpl.java",[[59,115]],
"Le service complète les modèles de tâches parents, puis appelle la création d’un projet depuis un modèle ou prépare son assistant.",
"Analogie partielle de composition réutilisable ; aucun algorithme d’adaptation de parcours engagé ni maintien d’engagements Supply démontré.")
add("OD-DEADLINE","odoo","addons/mail/models/mail_activity.py",[[227,253]],
"État en retard/aujourd’hui/prévu en fonction de l’échéance et du fuseau ; date issue du type d’activité.",
"Les calendriers ouvrés, pauses et escalades FLOW ne sont pas démontrés par cet extrait ; ils sont dimensionnés comme travaux propres.")
add("OD-VISIBILITY","odoo","addons/mail/models/mail_activity.py",[[866,955]],
"Regroupement par document/type des activités actives et terminées, dates, personnes affectées, contrôle des documents lisibles et pièces.",
"Analogie de vue agrégée ; ne prouve ni rapprochement multi-commandes ni sémantique engagement/réalisé/restant ou historique à deux dates.")
add("TY-ALERT","tryton","modules/quality/quality.py",[[636,707]],
"Alerte qualité avec origine, société, responsables et états ouvert/en traitement/reporté/résolu, transitions et actions déclarées.",
"Analogie d’exception avec responsable ; portée multi-dossiers, preuve de remédiation et droits d’intervention propres à FLOW.")
manifest=read("iteration-11-code-flowable/manifest.json")
f={Path(x["local_path"]).name:x for x in manifest}
def flow(i,name,ranges,observed,delta,kind="implementation_read"):
 x=f[name]
 evidence.append(dict(id=i,local_path=x["local_path"],commit=x["commit"],sha256=x["sha256"],url=x["url"],line_ranges=ranges,observed=observed,delta=delta,kind=kind,review="Source figée téléchargée et extraits lus ; aucun essai runtime."))
flow("F-SPRING","SpringProcessEngineConfiguration.java",[[104,154]],
"Configuration crée l’intercepteur et le contexte transactionnels Spring et enveloppe le DataSource pour participer aux transactions.",
"Composition exacte de la transaction FLOW/moteur à qualifier ; aucun effet externe atomique déduit.")
flow("F-JOBS","DefaultJobManager.java",[[237,291]],
"Déplacement d’un job vers l’échec terminal et remise en job exécutable avec nombre de reprises, via gestionnaires persistants.",
"Reprise technique ne prouve ni succès du résultat métier ni effet externe unique ; les états métier restent FLOW.")
flow("F-TASK","TaskService.java",[[168,192],[232,280],[499,509],[649,657]],
"API de prise en charge, délégation/résolution, complétion, affectation et échéance. Le contrat précise que claim/setAssignee ne vérifient pas l’existence de l’utilisateur dans l’identité.",
"Déclaration d’API lue, non preuve d’exécution ; admissibilité, autorisations, calendriers ouvrés et parcours utilisateur restent à financer.", "api_contract_read")
flow("F-RUNTIME","RuntimeService.java",[[1188,1212],[1315,1329],[1494,1497]],
"API de suspension/reprise, message corrélé à une exécution et changement d’état. Suspension d’une instance n’implique pas celle de toute sa hiérarchie.",
"Déclaration d’API lue ; FLOW doit contrôler portée, droits, engagements et effets. Le message présuppose une exécution corrélée ; conservation des signaux précoces à composer.", "api_contract_read")
flow("F-CHANGE","ChangeActivityStateCmd.java",[[25,49]],
"La commande vérifie la présence des identifiants de mouvement/activation et de l’instance lorsque nécessaire, puis délègue au DynamicStateManager.",
"L’appel n’est pas une preuve de sûreté métier. Hypothèse retenue : adapter seulement les segments futurs à un point de contrôle, sans migration arbitraire.")
flow("F-POM","pom.xml",[[52,58]],
"Le fichier de dépendances du commit étudié référence Spring Boot3.5.4, Spring Framework6.2.10 et Security6.5.3.",
"Ancre de comparaison figée, pas recommandation de version de production2026 ; la qualification des dépendances est E111.", "build_configuration_read")
for x in evidence:
 lines=(ROOT/x["local_path"]).read_text(encoding="utf-8").splitlines()
 assert all(1<=a<=z<=len(lines) for a,z in x["line_ranges"]),x["id"]
write("iteration-11-preuves.json",{"id":"iteration-11-preuves","date":"2026-10-29","evidence":evidence,
 "license":{"product":"Flowable OSS","commit":f["LICENSE"]["commit"],"url":f["LICENSE"]["url"],"sha256":f["LICENSE"]["sha256"],"observation":"Fichier LICENSE Apache License 2.0 ; aucun composant commercial Flowable supposé disponible. Qualification des dépendances et notices comprise dans E111 ; pas un avis juridique."},
 "docs":[{"url":"https://www.flowable.com/open-source/docs/bpmn/ch05-Spring","observed":"Documentation d’intégration transactionnelle Spring consultée ; le code figé reste l’ancre technique."},{"url":"https://www.flowable.com/open-source/docs/bpmn/ch18-Advanced","observed":"Documentation du cycle des jobs, temporisations persistées et échecs terminaux ; configuration à qualifier."}],
 "limitations":["17 observations de code, dont deux contrats d’API et une configuration de build ; aucun benchmark exécuté.","Les trois ERP restent des comparables fonctionnels, pas des modules transplantés dans Spring.","La comparaison ne produit aucun JH observé, ratio de productivité ni gain calculé par lignes de code."]})
print(json.dumps({"proofs":len(evidence)}))
