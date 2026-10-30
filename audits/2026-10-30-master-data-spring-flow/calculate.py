from pathlib import Path
import json,hashlib,math,sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def save(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
i=read(OUT/"inputs.json");a=read(OUT/"analogues.json");native=read(ROOT/"audits/2026-10-30-master-data-comparable-reuse/results.json")
c=i["cocomo"];E=c["B"]+.01*c["SF_sum"];F=c["D"]+.2*(E-c["B"])
def calc(ks,em):
 pm=c["A"]*ks**E*em
 return {"equivalent_KSLOC":ks,"person_months_EC":pm,"base_jh":pm*c["month_hours"]/c["day_hours"],"total_jh":pm*c["month_hours"]/c["day_hours"]*c["effort_phase_factor"],"months":c["C"]*pm**F*c["schedule_phase_factor"]}
details=[];by_scenario={}
for index,s in enumerate(i["scenarios"]):
 totals={f:{"program":0,"declarative":0,"equivalent":0} for f in i["families"]}
 def add(id,f,p,d,basis):
  w=s["declarative_weight"];eq=p+w*d
  totals[f]["program"]+=p;totals[f]["declarative"]+=d;totals[f]["equivalent"]+=eq
  details.append({"scenario":s["id"],"id":id,"family":f,"program":p,"declarative":d,"equivalent":eq,"basis":basis})
 for b in i["blocks"]:
  add(b["id"],b["family"],b["quantity"]*a["unit_bank"][b["kind"]]["range"][index],0,b["basis"])
 u=i["schema_units"]
 for sc in i["schemas"]:
  n=len(sc["fields"]);new=int(sc["new_model"])
  p=n*u["program_per_field"][index]
  d=n*(u["declarative_per_field"][index]+u["ui_declarative_per_field"][index])+new*(u["declarative_per_new_model"][index]+u["ui_declarative_per_new_model"][index])
  add("SCHEMA/"+sc["name"],sc["family"],p,d,"Champs additionnels et rendu/configuration ; champs ordinaires et moteurs réutilisés exclus.")
 for cf in i["configuration"]:add("CONFIG/"+cf["id"],cf["family"],0,cf["quantity"]*cf["unit_range"][index],cf["basis"])
 # Minimal structural declarations around new service groups, not entire generic controllers.
 groups={b["id"].split("/")[0] for b in i["blocks"]}
 for g in sorted(groups):
  bs=[b for b in i["blocks"] if b["id"].split("/")[0]==g]
  add("STRUCTURE/"+g,bs[0]["family"],[3,5,8][index],0,"Une déclaration de classe/méthode/injection par groupe, densité proposée ; pas d'annotation recomptée comme statement.")
 by_scenario[s["id"]]={"families":totals,"delta_equivalent_units":sum(v["equivalent"] for v in totals.values()),"program":sum(v["program"] for v in totals.values()),"declarative":sum(v["declarative"] for v in totals.values())}
# Reference is carried as effort-equivalent anchor under equivalence, not as physical Spring SLOC.
references=[]
for n in native["results"]:
 scenarios={}
 for s in i["scenarios"]:
  prev=n["scenarios"][s["id"]];d=by_scenario[s["id"]];ks=prev["equivalent_KSLOC"]+d["delta_equivalent_units"]/1000
  out=calc(ks,prev["EM"]);out["common_reference_jh"]=prev["total_jh"];out["incremental_flow_jh"]=out["total_jh"]-prev["total_jh"];out["delta_KSLOC"]=d["delta_equivalent_units"]/1000
  scenarios[s["id"]]=out
 references.append({"id":n["id"],"label":n["label"],"scenarios":scenarios})
selected=next(r for r in references if r["id"]==i["reference_choice"]["id"])
central=selected["scenarios"]["central"];delta=by_scenario["central"]["delta_equivalent_units"]
allocation=[]
for k,v in by_scenario["central"]["families"].items():
 # Symmetric proportional allocation of total increment: sums exactly; not separate estimations.
 allocation.append({"id":k,"label":i["families"][k],"equivalent_units":v["equivalent"],"jh":central["incremental_flow_jh"]*v["equivalent"]/delta,"allocation_not_independent_estimate":True})
dist=read(ROOT/"audits/2026-10-30-master-data-calcul/repartitions-sources.json")["cocomo"]
activities=[]
for row in dist["activities"]:
 ratio=sum(x*y for x,y in zip(dist["phase_effort_percent_of_base"],row["percent_by_phase"]))/10000
 activities.append({"id":row["id"],"label":row["label"],"jh":central["base_jh"]*ratio,"possible_roles":row["possible_flow_roles"],"allocation_status":"Répartition par défaut publiée ; pas de JH observés par rôle."})
assert math.isclose(sum(x["jh"] for x in activities),central["total_jh"])
assert math.isclose(sum(x["jh"] for x in allocation),central["incremental_flow_jh"])
# Conditional functional size, independent of the SLOC calculation.
old=read(ROOT/"audits/2026-10-29-experimentation-estimation/iteration-08-cosmic.json")
processes=[dict(p,origin="iteration08_retained_under_explicit_protocol_assumptions") for p in old["processes"]]
groups=[dict(g) for g in old["data_groups"]]
for id,obj in [("DG-RETENTION","Politique de conservation"),("DG-PURGE-REQUEST","Demande de purge des versions"),("DG-PURGE-REPORT","Rapport de purge et motifs de refus"),("DG-AUDIT-QUERY","Critères d'accès au journal"),("DG-RETENTION-TICK","Échéance de maintenance du journal")]:
 groups.append({"id":id,"object":obj,"status":"Groupe proposé pour le scénario25 ; non certifié."})
business=[g["id"] for g in old["data_groups"] if g.get("subject_id")]
def process(id,label,trigger,moves,contracts):
 movements=[]
 for typ,gs in moves.items():
  for group in gs:movements.append({"id":f"{id}-{typ}-{len(movements)+1}","type":typ,"group":group,"cfp":1})
 count={t:sum(x["type"]==t for x in movements) for t in "ERWX"};count["cfp"]=sum(count.values())
 processes.append({"id":id,"label":label,"functional_user":"Administrateur/opérateur ou ordonnanceur externe","trigger":trigger,"contract_function_ids":contracts,"movements":movements,"count":count,"status":"Processus candidat complet sous hypothèses explicites, non mesure certifiée."})
process("P01","Purger un ensemble canonique de versions",
"Un opérateur demande la purge d'un ensemble identifié ; un seul déclencheur, toutes les catégories de références possibles ; un refus partiel est un résultat prévu.",
{"E":["DG-PURGE-REQUEST"],"R":business+["DG-USAGE","DG-EXPORT","DG-PUBLICATION","DG-RECONCILIATION","DG-RETENTION"],
"W":business+["DG-CHANGE","DG-AUDIT"],"X":["DG-PURGE-REPORT","DG-OUTCOME"]},["F03","F10"])
process("J01","Consulter le journal sensible","Un administrateur demande les traces selon critères.",
{"E":["DG-AUDIT-QUERY"],"R":["DG-AUDIT"],"W":[],"X":["DG-AUDIT","DG-OUTCOME"]},["F10","F11"])
process("J02","Exporter le journal sensible","Un administrateur demande un export traçable du journal.",
{"E":["DG-AUDIT-QUERY"],"R":["DG-AUDIT"],"W":["DG-AUDIT"],"X":["DG-AUDIT","DG-OUTCOME"]},["F10","F11"])
process("J03","Appliquer la rétention du journal","L'ordonnanceur déclenche l'échéance ; paramètres modifiés par configuration de déploiement.",
{"E":["DG-RETENTION-TICK"],"R":["DG-AUDIT","DG-RETENTION"],"W":["DG-AUDIT"],"X":["DG-OUTCOME"]},["F10"])
cfp=sum(p["count"]["cfp"] for p in processes)
assert 300<=cfp<=500
benchmark=read(ROOT/"audits/2026-10-30-master-data-calcul/entrees.json")["benchmark"]
b=benchmark["main"];factor=benchmark["size_correction"]["factor"];h=b["hours_per_cfp"];spread=b["spread_hours_per_cfp"]
functional={"size_CFP":cfp,"process_count":len(processes),"jh":{k:cfp*v*factor/c["day_hours"] for k,v in [("lower",h-spread),("central",h),("upper",h+spread)]},
"benchmark_ref":benchmark["url"],"hours_per_cfp_central":h*factor,"scope":"Effort normalisé de l'équipe sur six activités. Les fonctions proposées sont comptées ; les niveaux de performance/reprise/sécurité et le déploiement S1 ne sont pas appariés au cohort historique.","probability":None,"certified":False,"nonfunctional_comparability":False,"schedule_months":None}
save("cosmic-candidate.json",{"groups":groups,"processes":processes,"result":functional,
"resolved_as_assumptions":["PURGE : P01 proposé ; aucune purge sûre sans rapprochement complet.","RIGHTS : gestion dans IdP ; contrôle de portée FLOW dans les traitements, pas d'administration locale supplémentaire.","AUDIT-ACCESS : J01/J02/J03.","API-EQUIVALENCE : mêmes événements, données et résultats côté humain/machine.","RECOVERY-MANIFEST : manifeste durable fourni par opérateur, clôture via R02 ; pas de notification autonome nouvelle.","PROCESS-DECOMPOSITION : admission/publication ou réexamen identiques I01/I02 ; pas de workflow indépendant de validation."],
"unresolved":["Groupes et indépendance des événements non revus humainement.","350CFP antérieurs étaient partiels ; le nouveau scénario est plus explicite mais pas une spécification approuvée.","S1 ne peut pas être justifié par la seule productivité CFP historique."],
"input_hashes":{"iteration08":hashlib.sha256((ROOT/"audits/2026-10-29-experimentation-estimation/iteration-08-cosmic.json").read_bytes()).hexdigest()}})
sens={}
for name,keys in [("unit_size",["lower","upper"]),("reference",[])]:
 if name=="unit_size":
  base=next(r for r in native["results"] if r["id"]=="axelor")["scenarios"]["central"]
  sens[name]=[calc(base["equivalent_KSLOC"]+by_scenario[k]["delta_equivalent_units"]/1000,base["EM"])["total_jh"] for k in keys]
sens["RCPX_nominal_to_high"]=[central["total_jh"],calc(central["equivalent_KSLOC"],1.33)["total_jh"]]
out={"id":i["id"],"selected_reference":i["reference_choice"],"selected":selected,"reference_sensitivities":references,
"size_delta":by_scenario,"increment_allocation":allocation,"activities":activities,"activity_source":dist["source"],
"formula":{"E":E,"F":F,"effort":"2.94 × (K_reference_equivalente + K_delta_FLOW)^E × EM × 152/7 × 1.18","schedule":"3.67 × PM_EC^F × 1.25","integration_of_native_framework":"Déjà dans K_reference ; pas une nouvelle remise ni une nouvelle charge Spring.",
"increment":"Calcul du total moins calcul du périmètre commun, avec les mêmes paramètres. La non-linéarité est préservée ; pas addition d'estimations COCOMO isolées.",
"allocation":"Répartition proportionnelle du supplément par taille équivalente des familles, descriptive et non causalité mesurée."},
"functional_crosscheck":functional,"cocomo_vs_functional_central_ratio":central["total_jh"]/functional["jh"]["central"],
"interpretation":"La confrontation est partiellement alignée sur les activités. Elle ne valide pas le total : tailles proposées, référence d'effort équivalente et exigences S1 non appariées. Ne pas moyenner les deux voies.",
"sensitivity":sens,"uncertainty":i["uncertainty"],"progress":{"business_capabilities_cumulative":6,"business_capabilities_total":6,"new_business_capabilities":0,"contract_sections_mapped":11,"contract_sections_total":11,"four_native_references":4,"code_analogue_samples_recounted":len(a["samples"]),"residual_blocks":len(i["blocks"]),"backend_blocks_not_charged_again":sum(len(d["already_in_native_equivalent_reference"]) for d in i["deduplication"]),"scenarios_calculated":3,"certified_functional_measurements":0,"externally_calibrated_effort_estimates":0,"verified_S1_guarantees":0,"functional_processes_before":25,"functional_processes_after":len(processes),"CFP_before":350,"CFP_after":cfp,"meaning":"100% des six capacités concernées et 11 rubriques représentées sous hypothèses ; pas 100% des exigences détaillées ni 100% des garanties vérifiées. L'absence de calibration n'interdit pas un ordre de grandeur d'opportunité, mais conserve la classe C."},
"next_iteration":"Utile si elle cible l'assemblage CRUD/droits/import et un scénario de publication/reprise sur les sources comparables. Une nouvelle itération de coefficients ou un portage ligne à ligne n'apporterait pas de preuve supplémentaire.",
"input_hashes":{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in ["inputs.json","analogues.json"]}}
save("size-detail.json",details);save("results.json",out)
print(json.dumps({"selected":selected,"cosmic":functional,"delta_sizes":{k:v["delta_equivalent_units"] for k,v in by_scenario.items()},"ratio":out["cocomo_vs_functional_central_ratio"],"progress":out["progress"]},ensure_ascii=False))
