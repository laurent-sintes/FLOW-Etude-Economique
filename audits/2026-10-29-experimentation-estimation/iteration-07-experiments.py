"""Consolidation iteration 07: source read-only, audit outputs only."""
from __future__ import annotations
import json,sys,hashlib,statistics
from pathlib import Path
from collections import defaultdict,Counter
ROOT=Path(__file__).resolve().parents[2]
A=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"tmp/model-deps"))
import yaml
def read(n): return json.loads((A/n).read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):(A/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
checks=[]
def check(label,truth):
 checks.append({"check":label,"passed":bool(truth)})
 if not truth:raise AssertionError(label)
def plus(a,b):return [x+y for x,y in zip(a,b)]
def walk(x):
 if isinstance(x,dict):
  yield x
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)
ctx=read("iteration-07-contexte.json")
contract=read("iteration-07-contrat-v1.1.json")
m1=read("iteration-07-m1.json");m2=read("iteration-07-m2.json")
market=read("iteration-07-marche-preuves.json")
spring=read("iteration-07-spring-preuves.json")
scope=read("iteration-07-perimetre.json")
cosmic=read("iteration-07-cosmic.json")
decision=read("iteration-07-decision.json")
previous=read("iteration-06-resultats.json")
review=read("iteration-07-revue-m1.json")
review2=read("iteration-07-revue-ecarts-m2.json")
contract_sha=sha(A/"iteration-07-contrat-v1.1.json")
check("Contrat v1.1 commun aux deux estimations",m1["contract_sha256"]==m2["contract_sha256"]==contract_sha)
check("M1 initial preserve",sha(A/"iteration-07-m1.json")=="155fb736b5089269f6d4a6af6b3baa4447b1f5a4747dcb372e0f1ec0ebf7c679")
check("M2 initial preserve",sha(A/"iteration-07-m2.json")=="1d2db49143d9db49658dab0421f2333f9576b9bc07aed2c4b71a22ee167749c2")
check("Pas de lecture reciproque des chiffres avant gel",m1["no_m2_values_seen"] and m2["provenance"]["m1_consulted"] is False)
for p,h in {**ctx["source_hashes"],**ctx["additional_source_hashes"]}.items():
 check("Source preservee : "+p,sha(ROOT/p)==h)
check("Methode candidate preservee",sha(A/"iteration-04-methode-candidate.json")==ctx["frozen_method_sha256"])
check("Resultat precedent preserve",sha(A/"iteration-06-resultats.json")==ctx["previous_result_sha256"])
for document,label in [(contract,"contrat"),(m2,"M2")]:
 for name,h in document["input_sha256"].items():
  check("Entree figee "+label+" : "+name,sha(A/name)==h)
proofs={p["id"]:p for p in market["proofs"]}
spring_ids={e["id"] for e in spring["evidence"]}
verified_code={}
for obj in walk(market):
 if isinstance(obj.get("cache_path"),str) and isinstance(obj.get("sha256"),str):
  path=obj["cache_path"]
  check("Empreinte de code : "+path,sha(ROOT/path)==obj["sha256"])
  verified_code[path]=obj["sha256"]
for p in market["proofs"]:
 lines=(ROOT/p["cache_path"]).read_text(encoding="utf-8-sig").splitlines()
 for start,end in p["ranges"]:
  check("Lignes source : "+p["id"]+" "+str(start),1<=start<=end<=len(lines))
 for ex in p.get("excerpts",[]):
  check("Extrait source : "+p["id"]+" "+str(ex["line"]),ex["text"].strip() in lines[ex["line"]-1])
labels={"analyse_produit":"Analyse produit","architecture":"Architecture","dev_java":"Développement Java","dev_frontend":"Développement interface","ux":"Conception des parcours (UX)","qa":"QA indépendante","plateforme":"Plateforme et livraison","securite":"Sécurité","coordination":"Coordination technique"}
roles=list(labels)
def empty():return {r:[0,0,0] for r in roles}
common=empty();family=empty()
groups=defaultdict(lambda:[0,0,0])
ratios=[]
function_refs=set()
for p in m1["packages"]:
 check("Paquet classe C : "+p["id"],p["solidity"]=="C")
 check("Preuves declarees : "+p["id"],set(p["proof_ids"])<=set(proofs)|spring_ids)
 for f in p["contract_functions"]:function_refs.add(f)
 for role,v in p["effort"].items():
  check("Role et bornes : "+p["id"]+"/"+role,role in labels and len(v)==3 and 0<v[0]<=v[1]<=v[2])
  check("Fondement explicite : "+p["id"]+"/"+role,bool(p["central_basis"].get(role)))
  dest=common if p["group"]=="COMMON07" else family
  dest[role]=plus(dest[role],v);groups[p["group"]]=plus(groups[p["group"]],v)
  ratios.append(v[2]/v[1])
check("Sommes M1 par groupe",dict(groups)==m1["totals_by_group"])
check("Toutes les fonctions contractuelles representees",function_refs=={f["id"] for f in contract["functional_contract"]})
def model(c,f):
 rows=[{"role":r,"label":labels[r],"COMMON07":c[r],"REF07":f[r],"total":plus(c[r],f[r])} for r in roles]
 res={"COMMON07":[sum(c[r][i] for r in roles) for i in range(3)],"REF07":[sum(f[r][i] for r in roles) for i in range(3)],"by_role":rows}
 res["total"]=plus(res["COMMON07"],res["REF07"])
 res["developer_brut"]=[sum(x["total"][i] for x in rows if x["role"] in ["dev_java","dev_frontend"]) for i in range(3)]
 return res
models={"M1":model(common,family)}
cm=empty();fm=empty()
for row in m2["estimates_by_role"]:
 role=row["role"]
 cm[role]=[row["COMMON07"][s] for s in ["bas","central","haut"]]
 fm[role]=[row["REF07"][s] for s in ["bas","central","haut"]]
 check("Somme M2 role : "+role,plus(cm[role],fm[role])==[row["total"][s] for s in ["bas","central","haut"]])
models["M2"]=model(cm,fm)
for key,ref in [("COMMON07","COMMON07"),("REF07","REF07"),("total","ensemble")]:
 check("Somme M2 : "+key,models["M2"][key]==[m2["totals"][ref][s] for s in ["bas","central","haut"]])
comparisons=[]
for r1,r2 in zip(models["M1"]["by_role"],models["M2"]["by_role"]):
 a,b=r1["total"],r2["total"];delta=b[1]-a[1];pct=100*delta/a[1]
 comparisons.append({"role":r1["role"],"label":r1["label"],"M1":a,"M2":b,"delta_central":delta,"relative_pct":round(pct,2),"flag":abs(pct)>25})
owners=[]
for key in ["COMMON07","REF07","total"]:
 a,b=models["M1"][key],models["M2"][key]
 owners.append({"owner":key,"M1":a,"M2":b,"delta_central":b[1]-a[1],"relative_pct":round((b[1]-a[1])/a[1]*100,2)})
comparison={"total_delta_central":owners[-1]["delta_central"],"total_relative_pct":owners[-1]["relative_pct"],"owners":owners,"by_role":comparisons,"selected_estimate":None,
 "meaning":"Comparaison au meme contrat, sans moyenne. Les divergences ne sont pas une mesure de l'erreur reelle.",
 "review_ref":"iteration-07-revue-ecarts-m2.json"}
check("Ecarts roles reconcilies avec total",sum(x["delta_central"] for x in comparisons)==comparison["total_delta_central"])
grid=yaml.load((ROOT/"source/grille-complexite.yaml").read_text(encoding="utf-8"),Loader=getattr(yaml,"CSafeLoader",yaml.SafeLoader))["blocs"]
blocks={b["capacite_id"]:b for b in grid}
scope_ids=set(contract["scope_ids"])
old_ids=set(previous["cumulative_comparative_ids"])
market_caps={c["id"]:c for c in market["capabilities"]}
check("Six capacites verifiees",scope_ids==set(market_caps)=={c["id"] for c in scope["capabilities"]} and len(scope_ids)==6)
native_ids={f["id"] for c in scope_ids for f in blocks[c]["fonctions"]}
check("Quatorze fonctions natives",len(native_ids)==14 and native_ids==set(contract["native_function_ids"])=={f["id"] for f in market["functions"]})
mapping={row["id"]:row for row in m2["native_function_coverage"]}
check("Couverture macro native exhaustive",set(mapping)==native_ids)
for row in review["coverage"]["native_mapping"]:
 check("Couverture travaux native : "+",".join(row["native"]),set(row["native"])<=native_ids and set(row["packages"])<={p["id"] for p in m1["packages"]})
cumulative=sorted(old_ids|scope_ids)
new=sorted(scope_ids-old_ids)
check("Cumul20 et increment4",len(cumulative)==20 and len(new)==4)
for c in sorted(scope_ids):
 check("Comparaison effective pour capacite : "+c,market_caps[c]["comparison_status"]=="comparaison_code_effective_partielle" and bool(market_caps[c]["proof_ids"]))
coverage=[]
for old in previous["capabilities"]:
 c={k:old[k] for k in ["id","name","block","path","path_names"]}
 c.update({"comparatively_studied":c["id"] in cumulative,"scenario_estimated":c["id"] in scope_ids,"opportunity_admitted":False,
  "status":"scenario_S1_entierement_represente_dans_estimations" if c["id"] in scope_ids else ("etude_partielle_anterieure" if c["id"] in old_ids else "cadree_sans_estimation_comparative"),
  "framed":True})
 coverage.append(c)
check("Inventaire sans doublon",len(coverage)==len({c["id"] for c in coverage})==88)
capmap={c["id"]:c for c in coverage}
family_rows=[]
for c in scope["capabilities"]:
 cid=c["id"];own=set()
 for row in review["coverage"]["native_mapping"]:
  if set(row["native"])&set(c["native_function_ids"]):own.update(row["packages"])
 family_rows.append({"id":cid,"name":c["name"],"block":blocks[cid]["id"],"path_names":capmap[cid]["path_names"],
  "function_ids":c["native_function_ids"],"direct_packages":sorted(own),
  "shared_packages":["COMMON07","I703","I704","V706","V707","V708","Q701","Q702","Q703","Q704"],
  "comparative_status":market_caps[cid]["comparison_status"],"scenario_estimated":True,"opportunity_admitted":False,
  "full_autonomous_jh":None,
  "meaning":"Contributions propres et dependances partagees ; pas de total autonome obtenu par prorata.",
  "function_reviews":[next(f for f in market["functions"] if f["id"]==fid) for fid in c["native_function_ids"]]})
subdomains=[]
for old in previous["subdomains"]:
 caps=[c for c in coverage if c["path"][1]==old["id"]]
 subdomains.append({"id":old["id"],"name":old["name"],"total":len(caps),"comparative":sum(c["comparatively_studied"] for c in caps),
  "scenario_estimated":sum(c["scenario_estimated"] for c in caps),"opportunity_admitted":0})
check("Sous-domaines reconcilies",sum(s["total"] for s in subdomains)==88 and sum(s["comparative"] for s in subdomains)==20)
for proc in cosmic["processes"]:
 check("CFP mouvements : "+proc["id"],all(m["type"] in "ERXW" and m["cfp"]==1 for m in proc["movements"]))
counts=Counter(m["type"] for p in cosmic["processes"] for m in p["movements"])
check("COSMIC sous-ensemble uniquement",sum(counts.values())==cosmic["result"]["conditional_subset_cfp"]==18 and cosmic["result"]["full_family_cfp"] is None and cosmic["result"]["cfp_to_jh_rate"] is None)
for t in "ERXW":check("CFP categorie "+t,counts.get(t,0)==cosmic["result"]["movements"][t])
metrics=[]
def metric(id,label,prev,cur,den,meaning):
 metrics.append({"id":id,"label":label,"previous":prev,"current":cur,"delta":cur-prev if prev is not None else None,"denominator":den,"meaning":meaning})
metric("inventory","Capacités dans le périmètre",88,88,88,"Cartographie stable ; pas un décompte de coûts.")
metric("framed","Capacités cadrées documentairement",88,88,88,"Résultat, frontière, garanties et questions repérés.")
metric("comparative","Cumul distinct des capacités étudiées par comparaison avec hypothèses de JH",16,20,88,"Quatre capacités de références nouvelles ; chaque identifiant compte une seule fois.")
metric("scenario_complete","Capacités dont toutes les fonctions sont représentées dans un chiffrage de scénario",0,6,88,"Sous les hypothèses S1 seulement ; toutes garanties à réaliser/qualifier, aucune précision acquise.")
metric("partial_only","Capacités restant au stade d'étude partielle",16,14,88,"Deux anciennes capacités de références passent à la portée S1 complète ; quatre nouvelles rejoignent ce scénario.")
metric("not_comparative","Capacités sans estimation comparative",72,68,88,"Les 68 restent cadrées, mais sans étude comparative avec hypothèses de JH.")
metric("opportunity_admitted","Capacités complètes à l'incertitude jugée suffisante pour l'opportunité",0,0,88,"Aucune admission : durées non calibrées, différences de réalisation non tranchées et scénarios proposés.")
metric("families_scenario","Familles entières avec estimations de scénario par rôle",0,1,None,"Operational References, avec socle commun séparé.")
check("Etats de couverture exclusifs",6+14+68==88)
check("Aucune admission inventee",decision["scope_status"]["opportunity_admitted_capabilities"]==0)
inputs=["iteration-07-protocole.json","iteration-07-contexte.json","iteration-07-contrat-v1.1.json","iteration-07-perimetre.json","iteration-07-marche-preuves.json","iteration-07-spring-preuves.json","iteration-07-cosmic.json","iteration-07-m1.json","iteration-07-m2.json","iteration-07-revue-perimetre.json","iteration-07-revue-m1.json","iteration-07-revue-ecarts-m2.json","iteration-07-decision.json"]
result={"id":"iteration-07-resultats","date":"2026-10-29","contract_ref":"iteration-07-contrat-v1.1.json","contract_sha256":contract_sha,
 "metrics":metrics,"models":models,"comparison":comparison,"family":family_rows,"coverage":coverage,"subdomains":subdomains,
 "cumulative_comparative_ids":cumulative,"new_comparative_ids":new,
 "full_core_jh":None,"cumulative_jh":None,"selected_estimate_jh":None,
 "methods":{"COSMIC":cosmic["result"],"COCOMO_II":{"effort_jh":None,"reason":decision["methods"]["COCOMO_II"]},"ISBSG":{"effort_jh":None,"reason":decision["methods"]["ISBSG"]}},
 "range_diagnostic":{"contributions":len(ratios),"upper_ratio_150_175":sum(1.5<=v<=1.75 for v in ratios),"median_upper_ratio":statistics.median(ratios),
  "meaning":"Amplitude surtout heuristique, pas risque mesure. Ne pas retoucher les bornes pour effacer ce constat."},
 "traceability_reserve":{"subject":"Interface des etats de reprise/reconciliation/purge suspendue dans M1","candidate_owners":["I706","V708"],"status":"Affectation a confirmer ; aucune omission certaine ou correction de JH decidee.","effect":"Les estimations visent S1 complet ; cette reserve empeche de considerer la decomposition entierement validee."},
 "decision":decision,"service_scenario":contract["service_scenario"],"packages":m1["packages"],
 "evidence_summary":{"proofs":len(market["proofs"]),"code_files_hash_checked":len(verified_code),"functions_with_partial_comparables":sum(bool(f["proof_ids"]) for f in market["functions"]),"native_functions":14,"new_runtime_tests":0,"observed_human_effort_records":0},
 "source_files_checked":len(ctx["source_hashes"]),"additional_instruction_files_checked":len(ctx["additional_source_hashes"]),
 "checks":checks,"input_sha256":{n:sha(A/n) for n in inputs}}
save("iteration-07-resultats.json",result)
print(json.dumps({"models":{k:{q:v[q] for q in ["COMMON07","REF07","total","developer_brut"]} for k,v in models.items()},
 "cumulative":len(cumulative),"new":len(new),"scenario_capabilities":len(family_rows),"delta_pct":comparison["total_relative_pct"],
 "checks":len(checks),"code_files":len(verified_code),"range_contributions":len(ratios)},ensure_ascii=True))
