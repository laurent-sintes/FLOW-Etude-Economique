from pathlib import Path
import sys,json,hashlib,math,importlib.util,collections,html
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding="utf-8")
sys.path[:0]=[str(ROOT/"tmp/model-deps"),str(ROOT/"tools")]
import yaml
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,x):(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
P=ROOT/"audits/2026-10-30-master-data-spring-flow"
G=ROOT/"audits/2026-10-30-master-data-decomposition-gap"
N=ROOT/"audits/2026-10-30-master-data-comparable-reuse"
if not (OUT/"baseline.json").exists():
 paths=[p for folder in ("source","config","app/src","app/scripts","tools") for p in (ROOT/folder).rglob("*") if p.is_file() and p.suffix in (".yaml",".md",".py",".ts",".tsx",".css",".mjs")]
 save("baseline.json",{"files":{p.relative_to(ROOT).as_posix():sha(p) for p in paths}})
inputs=read(P/"inputs.json");analogues=read(P/"analogues.json");previous=read(P/"results.json")
native=read(N/"results.json");decision=read(G/"benchmark-decision.json")
distribution=read(ROOT/"audits/2026-10-30-master-data-calcul/repartitions-sources.json")["cocomo"]
sp=importlib.util.spec_from_file_location("counter",ROOT/"audits/2026-10-30-master-data-natif/measure.py")
counter=importlib.util.module_from_spec(sp);sp.loader.exec_module(counter)
checks=[]
def ck(condition,label):
 assert condition,label
 checks.append(label)
samples={s["id"]:s for s in analogues["samples"]}
methods={}
inspected=[]
for sid in ("AXPACK_SERVICE","AXUNIT_CONVERSION","AXSHARING_QUERY"):
 s=samples[sid];p=ROOT/s["path"];ck(sha(p)==s["sha256"],sid+" source hash")
 data=p.read_bytes();tree=counter.PARSERS[".java"].parse(data)
 ck(not tree.root_node.has_error,sid+" parsed")
 for n in sorted(counter.walk(tree.root_node),key=lambda n:n.start_byte):
  if n.type!="method_declaration" or not any(a<=n.start_point.row+1<=b for a,b in s["ranges"]):continue
  count=sum((x.type.endswith("_statement") and x.type!="empty_statement") or x.type in counter.JAVA_EXTRA for x in counter.walk(n))
  row={"id":sid+":"+str(n.start_point.row+1),"sample":sid,"path":s["path"],"commit":s["commit"],"sha256":s["sha256"],"start_line":n.start_point.row+1,"end_line":n.end_point.row+1,"name":n.child_by_field_name("name").text.decode(),"program_units":count,
       "calls":sorted(set(x.child_by_field_name("name").text.decode() for x in counter.walk(n) if x.type=="method_invocation" and x.child_by_field_name("name"))),
       "note":"Taille du corps et de sa déclaration ; pas une fermeture automatique de tous les appels. Les dépendances doivent être déjà financées ou ajoutées explicitement."}
  methods[row["id"]]=row;inspected.append(row)
blocks={b["id"]:b for b in inputs["blocks"]}
mappings=read(OUT/"mapping-input.json")
changes=[]
for bid,refs,rationale in mappings:
 ck(bid in blocks and blocks[bid]["kind"]=="rule" and blocks[bid]["quantity"]==1,bid+" eligible")
 keys=[sid+":"+str(line) for sid,line in refs]
 ck(len(set(keys))==len(keys),bid+" no duplicate method")
 measured=sum(methods[k]["program_units"] for k in keys)
 changes.append({"block":bid,"family":blocks[bid]["family"],"contracts":blocks[bid]["contracts"],"previous_units":analogues["unit_bank"]["rule"]["range"][1],"proposed_units":measured,"method_refs":keys,"rationale":rationale,
 "evidence_status":"Code mesuré ; correspondance FLOW proposée par analyse assistée par IA, sans validation humaine ni effort observé."})
old_delta=previous["size_delta"]["central"]["delta_equivalent_units"]
delta=old_delta+sum(r["proposed_units"]-r["previous_units"] for r in changes)
c=inputs["cocomo"];E=c["B"]+.01*c["SF_sum"];F=c["D"]+.2*(E-c["B"])
def calc(ks,em):
 pm=c["A"]*ks**E*em
 return {"equivalent_KSLOC":ks,"PM_elaboration_construction":pm,"base_jh":pm*c["month_hours"]/c["day_hours"],"total_jh":pm*c["month_hours"]/c["day_hours"]*c["effort_phase_factor"],"schedule_months":c["C"]*pm**F*c["schedule_phase_factor"]}
cosmic=read(P/"cosmic-candidate.json")
cfp=sum(m["cfp"] for p in cosmic["processes"] for m in p["movements"])
benchmark=cfp*decision["retained_hours_per_CFP"]*decision["retained_factor"]/c["day_hours"]
ck(cfp==420 and benchmark==1200,"functional reference without factor 0.8")
rows=[]
for n in native["results"]:
 ref=n["scenarios"]["central"];old=next(r for r in previous["reference_sensitivities"] if r["id"]==n["id"])["scenarios"]["central"]
 reproduced=calc(ref["equivalent_KSLOC"]+old_delta/1000,ref["EM"])
 ck(math.isclose(reproduced["total_jh"],old["total_jh"]),n["id"]+" previous total reproduced")
 current=calc(ref["equivalent_KSLOC"]+delta/1000,ref["EM"])
 activities=[]
 for act in distribution["activities"]:
  fraction=sum(p*a for p,a in zip(distribution["phase_effort_percent_of_base"],act["percent_by_phase"]))/10000
  activities.append({"id":act["id"],"label":act["label"],"jh":current["base_jh"]*fraction,"possible_roles":act["possible_flow_roles"],"status":"Répartition publiée appliquée au modèle ; ventilation entre rôles non mesurée."})
 ck(math.isclose(sum(x["jh"] for x in activities),current["total_jh"]),n["id"]+" activities reconcile")
 common=ref["total_jh"];increment=current["total_jh"]-common
 # Cumulative rounding preserves the displayed total.
 common_display=round(common);total_display=round(current["total_jh"])
 rows.append({"id":n["id"],"label":n["label"],"common_jh":common,"flow_complements_jh":increment,**current,"previous_total_jh":old["total_jh"],"change_jh":current["total_jh"]-old["total_jh"],"gap_vs_functional_jh":current["total_jh"]-benchmark,"gap_vs_functional_pct":100*(current["total_jh"]/benchmark-1),"implied_hours_per_CFP":current["total_jh"]*c["day_hours"]/cfp,
 "display":{"common":common_display,"complements":total_display-common_display,"total":total_display},"activities":activities})
save("method-measures.json",inspected)
save("treatment-mapping.json",changes)
assumptions=[
"Équivalence des services des frameworks retenue à facteur 1, sans preuve d’égalité de productivité. Aucune reconstruction complète de Spring ou des plateformes natives.",
"Les tailles natives et leur réutilisation sont héritées de l’audit24. Les fonctions de création/édition directe ne sont pas encore isolées du périmètre commun avant transposition au contrat FLOW.",
"La présente correction remplace huit analogies de classe par des méthodes nommées. Les correspondances fonctionnelles sont des hypothèses d’ingénierie, pas des mesures de code FLOW.",
"Les sept lectures utilisent le schéma déjà dimensionné et des opérateurs ORM standards. Si un schéma ou un traitement spécialisé manque, cette hypothèse doit être révisée.",
"Les méthodes communes prises comme analogues n’impliquent pas que les huit traitements FLOW partagent automatiquement une seule implémentation ; chaque adaptateur métier est compté. La réutilisation d’un moteur générique reste dans la base commune.",
"70 des 78 traitements de type règle gardent leur ancienne analogie ; les autres catégories, les 313 champs, 42 modèles et 190 unités de structure sont inchangés. Leur précision n’est pas démontrée.",
"Le squelette et les déclarations des analogues peuvent se recouvrir ; aucune suppression arbitraire de 190 unités n’a été faite.",
"COCOMO couvre ici quatre phases via les conventions 1,18 pour l’effort et 1,25 pour le délai. Le calendrier est une sortie de modèle ; ce n’est pas un engagement d’une équipe dimensionnée.",
"Les niveaux de service S1 ne sont ni testés ni appariés au groupe ISBSG. COSMIC 420 CFP reste un comptage candidat ; 20 h/CFP et facteur 1 sont les conventions retenues.",
"Aucun gain IA supplémentaire, supplément QA, moyenne des quatre références ni coefficient destiné à rapprocher les méthodes n’est ajouté."
]
inputs_used=[P/"inputs.json",P/"analogues.json",P/"results.json",P/"cosmic-candidate.json",N/"results.json",G/"benchmark-decision.json",ROOT/"audits/2026-10-30-master-data-calcul/repartitions-sources.json",OUT/"mapping-input.json",ROOT/"audits/2026-10-30-master-data-natif/measure.py"]
grid=yaml.safe_load((ROOT/"source/grille-complexite.yaml").read_text(encoding="utf-8"))
progress={"master_data_capabilities_cumulative":6,"master_data_total":6,"whole_core_capabilities":len(grid["blocs"]),"whole_core_share_four_reference_method_pct":600/len(grid["blocs"]),"new_capabilities":0,"native_references":4,"analogue_methods_inspected":len(inspected),"treatments_refined":len(changes),"rule_treatments_total":sum(b["kind"]=="rule" for b in inputs["blocks"]),"all_residual_treatments":len(inputs["blocks"]),"functional_processes":len(cosmic["processes"]),"CFP":cfp,"production_guarantees_tested":0,"independently_calibrated_estimates":0,
"meaning":"100% des six capacités Master Data représentées, pas 100% des exigences vérifiées. 6/88 désigne cette méthode comparable, pas la couverture documentaire historique de tout le Core System. Aucun pourcentage de périmètre suffisamment certain n’est déduit des seuls calculs."}
result={"id":"audit27-master-data-spring-reprise","status":"candidat_partiel_non_adopte","scope":"BC-002 à BC-007 : projet logiciel Master Data Spring, hors intégration Groupe, MCO et autres familles du Core System.","rows":rows,"formula":{"E":E,"F":F,"cocomo":c,"effort":"2.94 × (K_natif_equivalent + K_complements)^1.0997 × EM × 152/7 × 1.18","schedule":"3.67 × PM_elaboration_construction^0.31794 × 1.25"},"size":{"previous_complements_units":old_delta,"proposed_complements_units":delta,"change_units":delta-old_delta},"functional":{"CFP":cfp,"hours_per_CFP":20,"factor":1,"day_hours":7,"jh":benchmark},"progress":progress,"assumptions":assumptions,"activity_source":distribution,"role_split":None,"probabilistic_interval":None,"active_economy_changed":False,
"next_iteration":{"worthwhile":True,"priority":"Aligner le périmètre commun natif avec le contrat FLOW : isoler l’édition directe des fiches, les contrôles partagés et l’admission de contributions. Puis traiter les analogies des règles complexes et leurs appels partagés.","stop_rule":"Ne pas poursuivre le découpage en méthodes si aucune différence de fonction, de réutilisation ou de taille suffisamment justifiée ne peut modifier la décision."},
"input_hashes":{p.relative_to(ROOT).as_posix():sha(p) for p in inputs_used}}
measurements=read(N/"measurements.json")
ck(sha(N/"inputs.json")==native["inputs_sha256"],"native inputs unchanged")
ck(sha(N/"measurements.json")==native["measurements_sha256"],"native measurements unchanged")
for source in measurements["files"]:
 path=ROOT/measurements["repos"][source["repo"]]["root"]/source["path"]
 ck(sha(path)==source["sha256"],"native code "+source["repo"]+"/"+source["path"])
result["native_code_verified"]={"files":len(measurements["files"]),"repositories":measurements["repos"],"note":"Pinned native selection rehashed, not a new functional review of every file."}
result["input_hashes"].update({p.relative_to(ROOT).as_posix():sha(p) for p in (N/"inputs.json",N/"measurements.json")})
save("results.json",result)
ck(len(changes)==8 and len(inspected)==18,"bounded review 8 treatments 18 methods")
ck(delta==8286.5,"215 units removed from the proposed size")
for p,h in read(OUT/"baseline.json")["files"].items():ck(sha(ROOT/p)==h,"active unchanged "+p)
save("verification.json",{"passed":True,"checks":len(checks),"active_files_unchanged":len(read(OUT/"baseline.json")["files"]),"limits":"Contrôle de calcul, périmètre de modification et empreintes ; ne valide pas les hypothèses de taille ou la productivité."})
print(json.dumps({"rows":[{k:r[k] for k in ("id","display","schedule_months","change_jh","gap_vs_functional_pct")} for r in rows],"progress":progress,"checks":len(checks)},ensure_ascii=False,indent=2))
