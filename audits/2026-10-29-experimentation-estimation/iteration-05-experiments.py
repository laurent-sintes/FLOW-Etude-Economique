"""Rebuild the isolated iteration05 results. No active model mutation."""
import json, hashlib, sys, html
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
P = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tmp/model-deps"))
import yaml
def read(name): return json.loads((P/name).read_text(encoding="utf-8"))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def add(values): return [sum(v[i] for v in values) for i in range(3)]
def check(label, condition):
    checks.append({"label":label,"passed":bool(condition)})
    if not condition: raise AssertionError(label)
def triple(v): return isinstance(v,list) and len(v)==3 and all(isinstance(x,(int,float)) and x>=0 for x in v) and v[0]<=v[1]<=v[2]
checks=[]
contract=read("iteration-05-contrat-v1.1.json")
original=read("iteration-05-contrat.json")
roles=contract["roles"]
context=read("iteration-05-contexte.json")
prior=read("iteration-03-resultats.json")["estimates"]["M1"]
m1={}
for ensemble in ("EXEC","ORCH","PLAN"):
    source=read("iteration-05-m1-"+ensemble.lower()+".json")
    totals=source.get("role_totals",source.get("totals_by_role"))
    packages=source["packages"]
    normalized=[]
    for pkg in packages:
        values=pkg.get("roles",pkg.get("effort"))
        check(ensemble+"/"+pkg["id"]+" : rôles et triplets",set(values)<=set(roles) and all(triple(v) for v in values.values()))
        normalized.append({"id":pkg["id"],"name":pkg.get("name",pkg.get("label")),"by_role":values,"total_jh":add(list(values.values()))})
    computed={r:add([pkg["by_role"].get(r,[0,0,0]) for pkg in normalized]) for r in roles}
    check(ensemble+" : total par rôle conservé",computed==totals)
    t=add(list(computed.values()))
    check(ensemble+" : total déclaré conservé",t==source.get("total",source.get("total_jh")))
    m1[ensemble]={"by_role":computed,"total_jh":t,"packages":normalized,"role_states":source["role_states"],"source":"iteration-05-m1-"+ensemble.lower()+".json"}
    check(ensemble+" : contrat de chiffrage conservé",sha(P/source["contract_ref"].split("#",1)[0])==source["contract_sha256"])
check("Précision v1.1 sans changement EXEC/ORCH",original["EXEC"]==contract["EXEC"] and original["ORCH"]==contract["ORCH"])
check("Méthode candidate préservée",sha(P/"iteration-04-methode-candidate.json")==context["frozen_method_sha256"])
check("Dix rôles uniques",len(roles)==len(set(roles))==10)
m2raw=read("iteration-05-m2.json")
m2={}
for e in m1:
    cells=[x for x in m2raw["assessments"] if x["ensemble"]==e]
    rr={x["role"]:x["jh"] for x in cells}
    check(e+" : comparaison mêmes rôles et triplets",set(rr)==set(roles) and all(triple(v) for v in rr.values()))
    m2[e]={"by_role":rr,"total_jh":add(list(rr.values()))}
    check(e+" : comparaison total conservé",m2[e]["total_jh"]==m2raw["totals_by_ensemble"][e])
check("M2 contrat préservé",sha(P/m2raw["contract_ref"].split("#",1)[0])==m2raw["contract_sha256"])
increment=add([v["total_jh"] for v in m1.values()])
comparison_increment=add([v["total_jh"] for v in m2.values()])
check("M2 incrément conservé",comparison_increment==m2raw["total_increment_jh"])
by_role={r:add([v["by_role"][r] for v in m1.values()]) for r in roles}
cumulative_role={r:add([prior["by_role"].get(r,[0,0,0]),by_role[r]]) for r in roles}
cumulative=add([prior["total_jh"],increment])
check("Cumul unique du périmètre évalué",cumulative==add(list(cumulative_role.values())))
check("Ancienne base inchangée",prior["total_jh"]==[246,409,642])
comparison=[]
for e in m1:
    a,b=m1[e]["total_jh"][1],m2[e]["total_jh"][1]
    role_deltas=[]
    for r in roles:
        x,y=m1[e]["by_role"][r][1],m2[e]["by_role"][r][1]
        pct=(y-x)*100/x if x else None
        role_deltas.append({"role":r,"M1":x,"M2":y,"delta_jh":y-x,"delta_pct":pct,"investigate":abs(pct)>25 if pct is not None else y!=x})
    comparison.append({"ensemble":e,"M1":a,"M2":b,"delta_jh":b-a,"delta_pct":(b-a)*100/a,"investigate":abs((b-a)*100/a)>15,"roles":role_deltas})
grid=yaml.safe_load((ROOT/"source/grille-complexite.yaml").read_text(encoding="utf-8"))
native=yaml.safe_load((ROOT/"sources/cartographie-scm-2026-10-24.yaml").read_text(encoding="utf-8"))
nodes={n["id"]:n for n in native["nodes"]}
old_contract=read("iteration-03-contrat.json")
by_cap={}
for e in ["REF","STOCK"]:
    for c in old_contract[e]["capabilities"]: by_cap.setdefault(c,[]).append(e)
for e in ["ORCH","PLAN"]:
    for c in contract[e]["capabilities"]: by_cap.setdefault(c,[]).append(e)
check("Toutes les capacités sélectionnées existent",set(by_cap)<=set(b["capacite_id"] for b in grid["blocs"]))
functions={f["id"] for b in grid["blocs"] for f in b["fonctions"]}
check("Toutes les fonctions sélectionnées existent",all(f in functions for e in ["ORCH","PLAN"] for f in contract[e]["native_functions"]))
coverage=[]
for b in grid["blocs"]:
    cid=b["capacite_id"]
    coverage.append({"id":cid,"block":b["id"],"name":nodes[cid]["fields"]["name"],"path":b["chemin"],"status":"partiellement évaluée" if cid in by_cap else "non évaluée","financing_refs":by_cap.get(cid,[]),"own_jh":None,"complete_jh":None})
check("88 capacités uniques",len(coverage)==len({r["id"] for r in coverage})==88)
check("16 capacités partiellement traitées, jamais complètes",sum(r["status"]=="partiellement évaluée" for r in coverage)==16)
owners={"COMMON":"supply-chain-orchestration","REF":"business-references","STOCK":"ba-inventory-position-management","EXEC":"supply-chain-orchestration","ORCH":"subdomain-process-management","PLAN":"domain-plan"}
lots={**prior["lots"],**m1}
ledger=[{"financing_ref":e,"owner":owner,"owner_name":nodes[owner]["fields"]["name"],"jh":lots[e]["total_jh"],"by_role":{r:lots[e]["by_role"].get(r,[0,0,0]) for r in roles}} for e,owner in owners.items()]
check("Un propriétaire pour chacun des six financements",len(ledger)==len({r["financing_ref"] for r in ledger})==6)
check("Restitution native conserve le cumul",add([r["jh"] for r in ledger])==cumulative)
check("Aucun effort inventé par capacité",all(r["own_jh"] is None and r["complete_jh"] is None for r in coverage))
source_changes=[f for f,h in context["source_hashes"].items() if sha(ROOT/f)!=h]
check("88 sources, paramètres et cartographie inchangés",len(context["source_hashes"])==88 and not source_changes)
proofs=[]
for name in ["iteration-05-orch-preuves.json","iteration-05-plan-preuves.json"]:
    for row in read(name)["evidence"]:
        path=row.get("local_path",row["path"])
        real=ROOT/path
        check("Preuve locale présente : "+row["id"],real.is_file())
        if row.get("sha256"):check("Preuve inchangée : "+row["id"],sha(real)==row["sha256"])
        proofs.append({"id":row["id"],"source":name,"local_path":path,"sha256":sha(real),"url":row["url"],"finding":row.get("observed",row.get("finding")),"limit":row.get("limit",row.get("limits"))})
spring=read("iteration-05-spring-preuves.json")
for row in spring["evidence"]:
    proofs.append({"id":row["id"],"source":"iteration-05-spring-preuves.json","url":row["url"],"git_blob_sha":row["git_blob_sha"],"finding":row["observation"],"limit":row["use"]})
check("Trois OSS, 29 lectures ciblées et sept preuves Spring",len(proofs)==36)
oracle=[(x, x+2*(10-x)+(10-x)+10*x) for x in range(11)]
check("Oracle affectation : minimum30 contre 110",min(v for x,v in oracle)==30 and max(v for x,v in oracle)==110)
cosmic=read("iteration-05-cosmic.json")
check("COSMIC cinq consultations et 21 CFP conditionnels",len(cosmic["functional_processes"])==5 and sum(p["conditional_cfp"] for p in cosmic["functional_processes"])==21)
check("COSMIC pas de taille complète ni conversion JH",all(cosmic["count"][k] is None for k in ["full_orch_cfp","full_plan_cfp","full_core_cfp"]))
check("COSMIC mouvements conservés",sum(len(p["movements"]) for p in cosmic["functional_processes"])==21)
old_caps=set(old_contract["REF"]["capabilities"]+old_contract["STOCK"]["capabilities"])
new_caps=set(by_cap)
all_paths={b["capacite_id"]:b["chemin"] for b in grid["blocs"]}
def touched(caps,depth):return len({all_paths[c][depth] for c in caps})
metrics=[
 {"metric":"Capacités dans la cartographie","previous":88,"current":88,"delta":0,"meaning":"Inventaire du périmètre, sans dire qu’il est évalué."},
 {"metric":"Capacités partiellement étudiées","previous":len(old_caps),"current":len(new_caps),"delta":len(new_caps)-len(old_caps),"meaning":"Une partie des fonctions a été examinée. Ce ratio ne mesure pas le pourcentage fonctionnel ou économique couvert."},
 {"metric":"Capacités entièrement évaluées","previous":0,"current":0,"delta":0,"meaning":"Aucune des capacités n’est couverte dans toute sa portée native et toutes ses garanties attendues."},
 {"metric":"Capacités restant sans évaluation","previous":88-len(old_caps),"current":88-len(new_caps),"delta":len(old_caps)-len(new_caps),"meaning":"À instruire, en plus des parties encore ouvertes des capacités partiellement traitées."},
 {"metric":"Sous-domaines abordés partiellement","previous":touched(old_caps,1),"current":touched(new_caps,1),"delta":touched(new_caps,1)-touched(old_caps,1),"meaning":"Nombre de sous-domaines touchés, sur "+str(len({b["chemin"][1] for b in grid["blocs"]}))+" ; aucune couverture complète implicite."},
 {"metric":"Business Areas abordées partiellement","previous":touched(old_caps,2),"current":touched(new_caps,2),"delta":touched(new_caps,2)-touched(old_caps,2),"meaning":"Nombre de Business Areas touchées, sur "+str(len({b["chemin"][2] for b in grid["blocs"]}))+" ; pas un pourcentage de coût."},
 {"metric":"Groupes fonctionnels bornés avec hypothèses de JH","previous":2,"current":4,"delta":2,"meaning":"REF, STOCK, ORCH et PLAN ; les deux lots communs sont comptés séparément."},
 {"metric":"Lots communs dimensionnés","previous":1,"current":2,"delta":1,"meaning":"Socle initial et extension d’exécution durable, financés une fois."},
 {"metric":"Contributions groupe × rôle dimensionnées","previous":sum(v[1]>0 for lot in prior["lots"].values() for v in lot["by_role"].values()),"current":sum(v[1]>0 for lot in lots.values() for v in lot["by_role"].values()),"delta":sum(v[1]>0 for lot in m1.values() for v in lot["by_role"].values()),"meaning":"Toutes restent classe C, sans calibration empirique."},
 {"metric":"Estimations de groupe déclarées suffisantes pour une décision d’investissement","previous":None,"current":0,"delta":None,"meaning":"Critère introduit à cette itération. Les quatre groupes fonctionnels restent à qualifier pour cet usage ; 0 déclaré suffisant ne signifie pas que leurs fonctions sont irréalisables."},
 {"metric":"Capacités complètes avec incertitude jugée raisonnable pour l’étude d’opportunité","previous":None,"current":0,"delta":None,"meaning":"Aucun périmètre natif complet n’a encore satisfait les critères d’usage. Pas de pourcentage arbitraire attribué à une capacité partielle."}
]
progress={"basis":"Même cartographie de 88 capacités ; comparaison à la fin de l’itération04","metrics":metrics,"reasonableness_criteria":["Périmètre de décision suffisamment défini : résultat, frontières, garanties et exclusions explicites.","Travaux obligatoires, dépendances, rôles et financements couverts, sans inconnue majeure cachée.","Appuis marché et hypothèses de durée traçables, avec limites de transposition.","Fourchette expliquée, écarts de comparaison compris ; classer C ne prouve pas une précision.","La décision d’investissement reste défendable dans cette fourchette, ou les conditions qui la font basculer sont explicites."],"current_verdict":"Chiffrages de témoins utiles à l’instruction de la méthode, à qualifier pour une décision d’investissement ; total Core inconnu.","important":"Une estimation d’ingénierie de classe C peut servir une étude d’opportunité si son périmètre et ses risques sont maîtrisés. Aucune plage universelle ni classe seule n’accorde ce statut."}

decision=read("iteration-05-decision.json")
progress["judgement"]=decision["progress_judgement"]
inputs=["iteration-05-protocole.json","iteration-05-contexte.json","iteration-05-contrat.json","iteration-05-contrat-v1.1.json","iteration-05-m1-exec.json","iteration-05-m1-orch.json","iteration-05-m1-plan.json","iteration-05-m2.json","iteration-05-cosmic.json","iteration-05-admission-cosmic-proposition.json","iteration-05-orch-preuves.json","iteration-05-plan-preuves.json","iteration-05-spring-preuves.json","iteration-05-decision.json","iteration-03-resultats.json","iteration-04-methode-candidate.json"]
result={"progress":progress,"numbers_use":"Hypothèses de travail expérimentales, aucun budget Core retenu","id":"iteration-05-results","date":"2026-10-29","unit":"JH bruts tous rôles de 7h, avant gains de productivité et réutilisation déjà intégrée","provenance":"Ingénierie assistée par IA, sans charge comparable observée ni revue humaine","range_meaning":"Enveloppe de sensibilité au même périmètre, pas des percentiles","previous_jh":prior["total_jh"],"M1":m1,"M2":m2,"increment_jh":increment,"increment_by_role":by_role,"cumulative_evaluated_jh":cumulative,"cumulative_by_role":cumulative_role,"full_core_jh":None,"full_core_reason":"72 capacités non évaluées et16 seulement partielles, exigences de production hors contrats ; aucune extrapolation proportionnelle.","comparison_increment_jh":comparison_increment,"comparison_on_same_previous_basis_jh":add([prior["total_jh"],comparison_increment]),"comparison":comparison,"comparison_net_delta_jh":comparison_increment[1]-increment[1],"comparison_sum_absolute_ensemble_deltas_jh":sum(abs(r["delta_jh"]) for r in comparison),"native_financing_ledger":ledger,"coverage":coverage,"evidence":proofs,"cosmic":cosmic,"decision":decision,"input_sha256":{n:sha(P/n) for n in inputs},"source_files_checked":len(context["source_hashes"]),"checks":checks}
(P/"iteration-05-resultats.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

# Render the same figures; no autonomous calculation of effort in the HTML.
def esc(x): return html.escape(str(x))
def fmt(x):
    if x is None:return "Inconnu"
    return ("{:,.1f}".format(x).rstrip("0").rstrip(".") if x%1 else "{:,.0f}".format(x)).replace(","," ").replace(".",",")
def table(headers, rows):
    return '<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+esc(v)+'</th>' for v in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(v)+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def para(s): return "<p>"+s+"</p>"
def listing(items): return "<ul>"+''.join("<li>"+esc(s)+"</li>" for s in items)+"</ul>"
def link(name,label=None):return '<a href="'+esc(name)+'">'+esc(label or name)+'</a>'
labels={"analyse_produit":"Analyse produit","architecture":"Architecture","dev_java":"Développement Java","dev_frontend":"Développement des interfaces","ux":"Conception des parcours utilisateur","qa":"QA indépendante","plateforme":"Plateforme technique","securite":"Sécurité","coordination":"Coordination technique","expert_optimisation":"Expertise en optimisation"}
names={"COMMON":"Socle initial des deux pilotes","REF":"Références produit/variante","STOCK":"Positions et réservations","EXEC":"Exécution durable commune","ORCH":"Dossier, attentes et décisions","PLAN":"Affectations et comparaison de scénarios"}
body='<header><p class="eyebrow">FLOW · Étude économique · Expérimentation du 29 octobre 2026</p><h1>Orchestration et planification : périmètre évalué et JH</h1><p>Itération 05 · Méthode éprouvée sur deux familles réservées · Sources actives inchangées</p></header>'
body+='<div class="warning"><strong>Le total de FLOW Core System reste inconnu.</strong><p>Les chiffres ci-dessous concernent des fonctions bornées pour expérimenter la méthode. Ils couvrent des parties de 16 capacités sur 88 ; ils ne représentent ni 16 capacités complètes, ni un pourcentage du coût du Core. Les 72 autres capacités et les compléments de périmètre restent à évaluer.</p></div>'
body+='<div class="cards"><div><span>Périmètre abordé</span><strong>16 capacités partielles</strong><p>+10 depuis l’itération précédente</p></div><div><span>Périmètre entièrement évalué</span><strong>0 capacité</strong><p>72 restent sans évaluation</p></div><div><span>Total Core complet</span><strong>Inconnu</strong><p>Aucun chiffre forcé</p></div></div>'
body+='<section id="avancement"><h2>Avancement et aptitude au chiffrage</h2>'
body+=table(["Indicateur","Précédent","Actuel","Évolution","Ce qu’il signifie"],[[esc(x["metric"]),fmt(x["previous"]) if x["previous"] is not None else "Non mesuré",fmt(x["current"]),fmt(x["delta"]) if x["delta"] is not None else "Nouveau critère",esc(x["meaning"])] for x in metrics])
body+=para("<strong>Quand l’incertitude devient-elle raisonnable pour l’étude d’opportunité ?</strong>")
body+=listing(progress["reasonableness_criteria"])
body+=para(esc(progress["important"]))
body+='<h3>Progresse-t-on ou tourne-t-on en rond ?</h3>'
body+=para("<strong>"+esc(decision["progress_judgement"]["overall"])+"</strong>")
body+=listing(decision["progress_evidence"])
body+=para(esc(decision["progress_judgement"]["next_gate"]))
body+=para("Les quatre groupes fonctionnels restent à qualifier pour une décision d’investissement. Leur chiffrage borné n’est pas une estimation complète des unités métier. Les montants détaillés ci-après sont conservés comme hypothèses de travail pour l’audit.")
body+='</section>'
body+=para("Un JH correspond à 7 heures. La réutilisation retenue est déjà intégrée aux travaux : aucun second abattement. Aucun gain de productivité IA n’est appliqué. Les bornes décrivent la sensibilité des hypothèses au même périmètre ; elles ne sont pas des percentiles.")
body+='<nav><a href="#avancement">Avancement</a> · <a href="#charges">Hypothèses de charge</a> · <a href="#portee">Périmètre</a> · <a href="#comparaison">Deux estimations</a> · <a href="#methodes">Méthodes</a> · <a href="#suite">Suite</a> · <a href="#preuves">Preuves</a></nav>'
body+='<section id="charges"><h2>Hypothèses de charge des périmètres d’essai</h2>'
body+=table(["Travaux financés","Bas (JH)","Central (JH)","Haut (JH)"],[[esc(names[e]),*map(fmt,lots[e]["total_jh"])] for e in owners]+[["<strong>Cumul du périmètre évalué</strong>",*['<strong>'+fmt(v)+'</strong>' for v in cumulative]]])
body+=para("Les 409 JH précédemment annoncés correspondent au socle initial 109 + références 141 + stock 159. Ils n’ont jamais constitué une estimation de l’ensemble du Core. L’exécution durable ajoutée ici finance une extension précise du socle ; elle n’est comptée qu’une fois.")
body+='<h3>Effort cumulé par rôle</h3>'
body+=table(["Rôle","Bas (JH)","Central (JH)","Haut (JH)","Ajout central (JH)"],[[esc(labels[r]),*map(fmt,cumulative_role[r]),fmt(by_role[r][1])] for r in roles])
body+=para("La contribution Java cumulée est de "+fmt(cumulative_role["dev_java"][1])+" JH ; Java et interfaces totalisent "+fmt(cumulative_role["dev_java"][1]+cumulative_role["dev_frontend"][1])+" JH de développement brut, tests développeur inclus. Les autres rôles restent distincts. La coordination technique ne couvre pas le pilotage complet du programme.")
for e in m1:
    body+='<h3>'+esc(names[e])+' — détail par rôle</h3>'
    rows=[]
    for r in roles:
        state=m1[e]["role_states"][r]
        rows.append([esc(labels[r]),*map(fmt,m1[e]["by_role"][r]),"C" if m1[e]["by_role"][r][1] else "Non mobilisé distinctement"])
    body+=table(["Rôle","Bas (JH)","Central (JH)","Haut (JH)","Solidité"],rows)
    body+=table(["Paquet de travaux","Bas (JH)","Central (JH)","Haut (JH)"],[[esc(p["id"]+" · "+p["name"]),*map(fmt,p["total_jh"])] for p in m1[e]["packages"]])
    body+=para("Actions, temps proposés, causes de variation et garanties financées : "+link(m1[e]["source"],"fiche détaillée de cette estimation")+".")
body+=para("<strong>Classe C : estimation d’ingénierie documentée, sans calibration sur des charges de réalisations comparables.</strong> Une preuve de code ou un test technique ne transforme pas ces durées en observations. Les quatre cases sans contribution distincte dans les nouveaux ensembles n’ont pas de classe.")
body+='</section><section id="portee"><h2>Ce qui est évalué</h2>'
for e in ["EXEC","ORCH","PLAN"]:
    part=contract[e]
    body+='<h3>'+esc(names[e])+'</h3>'
    if e=="PLAN":body+=para(esc(part["bounds"]))
    body+=listing(part["includes"])
    body+=para("<strong>Hors de ce périmètre :</strong>")
    body+=listing(part["excludes"])
body+=para("Les paramètres et objectifs du cas d’optimisation sont des hypothèses de qualification du produit générique. Ils ne décrivent pas les règles Beaumanoir. Le cas demande de privilégier la couverture, puis le coût, avec déficit explicite et aucune réservation automatique.")
body+='<h3>Rattachement à la cartographie métier</h3>'
body+=para("Le niveau d’estimation retenu est un groupe cohérent de fonctions. Ses bénéficiaires peuvent appartenir à plusieurs Business Areas. Les montants ci-dessous sont les financements du seul périmètre étudié ; les totaux complets des unités métier restent inconnus.")
body+=table(["Financement unique","Unité métier de rattachement","Central partiel (JH)"],[[esc(names[r["financing_ref"]]),esc(r["owner_name"]),fmt(r["jh"][1])] for r in ledger])
body+=para("La publication de positions datées pour la planification (BC-012) est financée dans PLAN ; elle n’était pas couverte par STOCK. Ce rattachement économique transversal n’en déplace pas l’identité métier. Les vues de dossier bénéficient aussi à la visibilité des processus, sans ouvrir un financement ni prétendre couvrir toute cette capacité.")
body+=table(["Capacité partiellement étudiée","Financements à consulter","JH propres complets"],[[esc(r["id"]+" · "+r["name"]),esc(", ".join(r["financing_refs"])),"Inconnus"] for r in coverage if r["financing_refs"]])
body+=para("Les 72 capacités restantes sont conservées comme non évaluées dans "+link("iteration-05-resultats.json","le registre de couverture complet")+". Aucune division arbitraire des charges entre capacités n’a été faite.")
body+='</section><section id="comparaison"><h2>Pourquoi deux estimations ?</h2>'
body+=para("L’estimation détaillée additionne les paquets de travaux par rôle. Une seconde estimation, plus globale, a été produite par un autre agent sur le même contrat sans voir les premiers chiffres. Elle sert à repérer les oublis et hypothèses fragiles. Deux estimations assistées par IA ne sont pas deux projets réalisés ; leur accord ne prouve pas la précision des JH.")
body+=table(["Périmètre ajouté","Détaillée (JH)","Comparaison (JH)","Écart (JH)","Écart (%)"],[[esc(names[r["ensemble"]]),fmt(r["M1"]),fmt(r["M2"]),fmt(r["delta_jh"]),fmt(round(r["delta_pct"],1))] for r in comparison])
body+=para("L’ajout détaillé vaut "+fmt(increment[1])+" JH ; l’estimation de comparaison vaut "+fmt(comparison_increment[1])+" JH. Sur la même base précédente 409, cela donnerait respectivement "+fmt(cumulative[1])+" et "+fmt(prior["total_jh"][1]+comparison_increment[1])+" JH partiels. Aucun mélange ni moyenne des chiffres n’est retenu.")
body+=para("La somme des écarts absolus entre les trois groupes est de "+fmt(result["comparison_sum_absolute_ensemble_deltas_jh"])+" JH ; leur écart net est de "+fmt(result["comparison_net_delta_jh"])+" JH. Le rapprochement du total masque donc des compensations.")
alerts=[[esc(names[r["ensemble"]]),esc(labels[d["role"]]),fmt(d["M1"]),fmt(d["M2"]),fmt(round(d["delta_pct"],1)) if d["delta_pct"] is not None else "État différent"] for r in comparison for d in r["roles"] if d["investigate"]]
body+=table(["Groupe","Rôle à examiner","Détaillée (JH)","Comparaison (JH)","Écart (%)"],alerts)
body+=para("Les seuils 15 % par groupe et 25 % par rôle déclenchent un examen. Ils ne sont pas des seuils de justesse. La revue spécialisée du JSON et du compilateur ORCH n’était pas explicitement financée dans la seconde estimation : son écart sécurité ne peut être lu comme un simple désaccord de durée. Les chiffres initiaux restent conservés.")
body+=listing(decision["comparison_findings"])
body+='</section><section id="methodes"><h2>Ce que les trois méthodes apportent à cette étape</h2>'
body+=table(["Méthode","Usage actuel","Limite"],[
["COSMIC","Mesurer des mouvements de données fonctionnels","21 CFP sous hypothèses pour 5 consultations seulement ; ni taille complète ni conversion en JH."],
["COCOMO II","Structurer taille cible, réutilisation et facteurs d’effort","Taille cible admissible et facteurs calibrés indisponibles ; aucun calcul COCOMO de JH retenu."],
["ISBSG","Chercher des réalisations mesurées comparables","Pas de référence actuellement admissible pour calibrer ces travaux Spring par rôle."]])
body+=para("Les 21 CFP décrivent un sous-ensemble borné de consultations :")
body+=table(["Consultation","Points fonctionnels sous hypothèses"],[[esc(p["label"]),fmt(p["conditional_cfp"])] for p in cosmic["functional_processes"]])
body+=para("Les modifications, l’exécution des dossiers et les calculs d’affectation ne sont pas comptés dans ce sous-total. COSMIC intègre la manipulation des données dans les mouvements, sans mesurer séparément la difficulté algorithmique. Les deux familles peuvent donc demander des travaux très différents à nombre de mouvements voisin.")
body+=para(link("iteration-05-cosmic.json","Frontières, hypothèses et comptage détaillé")+" · "+link("iteration-05-admission-cosmic-proposition.json","Conditions d’admission des méthodes"))
body+='<h3>Réutilisation et preuves de marché</h3>'
body+=para("Les corps de code et des tests ont été lus aux commits figés pour Odoo, Tryton et Axelor. Ils éclairent les transitions, reprises, tâches, calculs de besoins et sélections locales. Les portions examinées n’établissent pas un optimiseur global comparable à tout FLOW. Les tests OSS n’ont pas été exécutés.")
body+=para("Flowable OSS 7.2.0 et Timefold Solver 1.26.0 sont les composants candidats de cette expérience Spring. Leur code montre des mécanismes réutilisables ; intégration et qualité des résultats restent à qualifier. Timefold gère ses travaux en mémoire : PLAN finance la conservation des entrées et résultats et la relance explicite après interruption.")
body+=para("La référence Boot 3.5.7 est conservée pour cette comparaison expérimentale. Elle ne constitue pas une recommandation de version de production ; la cible et sa maintenance devront être revues avant réalisation.")
body+='</section><section id="suite"><h2>Une autre itération vaut-elle le coût ?</h2>'
body+=para("<strong>"+esc(decision["recommendation"])+"</strong>")
body+=listing(decision["next_iteration"])
body+=para(esc(decision["stop_rule"]))
body+=para("Aucune révision structurelle de méthode. Une précision de périmètre a borné les ressources PLAN à 70 lignes avant gel des estimations. Le rôle d’expert en optimisation applique la règle existante : identifier les rôles réellement nécessaires. Aucun coefficient supplémentaire n’a été créé.")
body+='<h3>Contrôles et limites</h3>'
body+=para(str(len(checks))+" contrôles de cohérence réussis lors de cette génération : sommes, rôles, contrats figés, références, empreintes de code et 88 sources actives préservées. L’oracle minuscule d’affectation a été vérifié arithmétiquement (30 contre 110) ; aucun solveur n’a été exécuté dans cette itération.")
body+=listing(decision["remaining_limits"])
body+='</section><section id="preuves"><h2>Traçabilité</h2>'
body+=para(link("iteration-05-contrat-v1.1.json","Contrat commun")+" · "+link("iteration-05-protocole.json","Protocole")+" · "+link("iteration-05-resultats.json","Calculs et couverture")+" · "+link("iteration-05-experiments.py","Script reproductible")+" · "+link("iteration-05-decision.json","Décision et revue"))
body+=table(["Preuve","Observation","Limite"],[[link(r["url"],r["id"]),esc(r["finding"]),esc(r["limit"])] for r in proofs])
body+='</section><footer>Audit expérimental · Aucun changement des sources économiques, de la cartographie ou de l’application · Aucun commit ni publication</footer>'
css="body{margin:0;background:#FAF8F4;color:#182632;font-family:Aptos,'Segoe UI',sans-serif;line-height:1.55}main{max-width:1180px;margin:auto;padding:40px 32px}header{border-bottom:3px solid #236159;margin-bottom:26px}.eyebrow{color:#236159;font-weight:700}h1{font-size:2.2rem;line-height:1.2}h2{color:#236159;margin-top:46px;border-top:1px solid #b9ccc6;padding-top:20px}h3{margin-top:30px}.warning{background:#FFF0DB;border-left:5px solid #FF7A1A;padding:18px 22px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:24px 0}.cards>div{background:#D9F2EA;padding:20px}.cards strong{display:block;font-size:1.7rem;color:#236159}.cards span{font-weight:600}nav{padding:16px 0}a{color:#236159;text-decoration-thickness:1px;text-underline-offset:3px}.table-wrap{overflow-x:auto;margin:16px 0}table{width:100%;border-collapse:collapse;background:white}th{text-align:left;background:#236159;color:white;font-weight:600}td,th{padding:10px 13px;vertical-align:top;border-bottom:1px solid #d8dfda}tbody tr:nth-child(even){background:#f1f7f4}p{max-width:1050px}li{margin:8px 0}footer{border-top:2px solid #236159;margin-top:50px;padding-top:20px;color:#4a5d57;font-size:.9rem}@media(max-width:700px){main{padding:24px 16px}.cards{grid-template-columns:1fr}h1{font-size:1.8rem}}@media print{main{padding:10px}nav{display:none}thead{display:table-header-group}tr{break-inside:avoid}a{color:inherit}}"
document='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FLOW — Itération 05 — Périmètre évalué et JH</title><style>'+css+'</style></head><body><main>'+body+'</main></body></html>'
(P/"iteration-05.html").write_text(document,encoding="utf-8")
print(json.dumps({"checks":len(checks),"previous":prior["total_jh"],"increment":increment,"cumulative_evaluated":cumulative,"full_core":None,"comparison_increment":comparison_increment,"source_files":len(context["source_hashes"])}))
