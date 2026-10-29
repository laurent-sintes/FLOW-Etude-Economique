"""Iteration09: engineering estimate, explicit inherited judgements, no model update."""
from pathlib import Path
from collections import defaultdict
import json, hashlib, math, importlib.util
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
def read(n):return json.loads((HERE/n).read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(HERE/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
ROLES={"analyse_produit":"Analyse produit","architecture":"Architecture","dev_java":"Développement Java","dev_frontend":"Développement interface","ux":"Conception des parcours (UX)","qa":"QA indépendante","plateforme":"Plateforme et livraison","securite":"Sécurité","coordination":"Coordination technique"}
GROUPS=[
("SOCLE","Socle technique commun",["C701","C702","C703","C704","C705","C706","C707"]),
("MECANISMES","Mécanismes communs des référentiels",["I702","I703","I704","I705","V706","V707"]),
("TRANSVERSE","Conception et qualification transverses",["I701","V708","Q701","Q702","Q703","Q704"]),
("BC-002","Ingestion : parcours propres",["I706"]),
("BC-003","Partenaires et accords : travaux propres",["V701"]),
("BC-004","Marchandise : travaux propres",["V702"]),
("BC-005","Conditionnement : travaux propres",["V703"]),
("BC-006","Fournitures et équipements : travaux propres",["V704"]),
("BC-007","Services et tarifs reçus : travaux propres",["V705"])]
def main():
 h=read("iteration-09-hypotheses.json");old=read("iteration-07-m1.json")
 proofs=read("iteration-07-marche-preuves.json");spring=read("iteration-07-spring-preuves.json")
 checks=[]
 def check(n,b):
  checks.append({"check":n,"passed":bool(b)})
  if not b:raise AssertionError(n)
 owners={pid:g for g,label,pids in GROUPS for pid in pids}
 check("Every package has one owner",len(owners)==sum(len(ids) for _,_,ids in GROUPS)==len(old["packages"]))
 proof_ids={p["id"] for p in proofs["proofs"]}|{p["id"] for p in spring["evidence"]}
 for p in proofs["proofs"]:
  if p.get("cache_path") and p.get("sha256"):check("OSS "+p["id"],sha(ROOT/p["cache_path"])==p["sha256"])
 packages=[]
 for p in old["packages"]:
  q=json.loads(json.dumps(p));pid=p["id"];rev=h["central_revisions"].get(pid,{})
  q["previous_effort"]=q.pop("effort");q["owner"]=owners[pid]
  central={r:v[1] for r,v in q["previous_effort"].items()};central.update(rev.get("effort",{}))
  lo,hi,cause=h["ranges"][pid]
  q["effort"]={r:[max(.5,math.floor(c*lo*2)/2),c,math.ceil(c*hi*2)/2] for r,c in central.items()}
  q["current_basis"]={"inherited":p["central_basis"],"revision":rev.get("reason","Centre M1 reconduit comme hypothèse d’ingénierie, sans nouvelle observation ni calibration.")}
  q["uncertainty"]={"class":"C","low_factor":lo,"high_factor":hi,"cause":cause,"meaning":h["uncertainty"]}
  q["provenance"]="M1 réexaminé et amendé explicitement ; auteur assistant IA ; aucune revue humaine attribuée."
  q["total"]=[sum(v[i] for v in q["effort"].values()) for i in range(3)]
  check("Proofs resolve "+pid,all(x in proof_ids for x in q["proof_ids"]))
  check("Ordered scenarios "+pid,all(0<=v[0]<=v[1]<=v[2] for v in q["effort"].values()))
  packages.append(q)
 byid={p["id"]:p for p in packages}
 def summarize(ids):
  role={r:[sum(byid[pid]["effort"].get(r,[0,0,0])[i] for pid in ids) for i in range(3)] for r in ROLES}
  return {"roles":role,"total":[sum(v[i] for v in role.values()) for i in range(3)]}
 groups=[{"id":g,"label":label,"packages":ids,**summarize(ids)} for g,label,ids in GROUPS]
 total=summarize(list(byid));common=summarize([p for g,_,ids in GROUPS if not g.startswith("BC") for p in ids])
 direct=summarize([p for g,_,ids in GROUPS if g.startswith("BC") for p in ids])
 check("Direct plus shared equals total",all(common["total"][i]+direct["total"][i]==total["total"][i] for i in range(3)))
 check("Central reconciles previous plus explicit changes",total["total"][1]==sum(sum(v[1] for v in p["effort"].values()) for p in old["packages"])+sum(v-byid[pid]["previous_effort"].get(r,[0,0,0])[1] for pid,x in h["central_revisions"].items() for r,v in x["effort"].items()))
 assigned=[pid for p in h["schedule"]["phases"] for pid in p["packages"]]
 check("Schedule counts every package exactly once",len(assigned)==len(set(assigned))==len(byid) and set(assigned)==set(byid))
 phases=[];capacity=h["schedule"]["jh_per_person_month"]
 for phase in h["schedule"]["phases"]:
  s=summarize(phase["packages"])
  alloc=h["schedule"]["coordination_allocation"];pid=alloc["package"];role=alloc["role"]
  for i in range(3):
   amount=byid[pid]["effort"][role][i]
   adjustment=amount*alloc["shares"].get(phase["id"],0)-(amount if pid in phase["packages"] else 0)
   s["roles"][role][i]+=adjustment;s["total"][i]+=adjustment
  dur=[];bottlenecks=[]
  for i in range(3):
   needs={r:v[i]/(phase["staff"][r]*capacity) for r,v in s["roles"].items()}
   duration=max(phase["floor_months"][i],max(needs.values()));dur.append(duration)
   bottlenecks.append(max(needs,key=needs.get) if max(needs.values())>=phase["floor_months"][i] else "plancher")
   check("Capacity fits "+phase["id"]+" "+str(i),all(v[i]<=phase["staff"][r]*capacity*duration+1e-8 for r,v in s["roles"].items()))
  phases.append({**phase,**s,"duration_months":dur,"limiting_role":bottlenecks})
 months=[sum(p["duration_months"][i] for p in phases) for i in range(3)]
 check("Ordered calendar",months[0]<=months[1]<=months[2])
 for r in ROLES:
  for i in range(3):check("Phase effort conserved "+r+str(i),math.isclose(sum(p["roles"][r][i] for p in phases),total["roles"][r][i]))
 context=read("iteration-08-contexte.json")
 for group in ["source_hashes","additional_source_hashes"]:
  for p,d in context[group].items():check("Source unchanged "+p,sha(ROOT/p)==d)
 oldresult=read("iteration-07-resultats.json")
 funcs={f["id"]:f for f in proofs["functions"]}
 coverage=[]
 for cap in oldresult["family"]:
  ids=next(g["packages"] for g in groups if g["id"]==cap["block"])
  coverage.append({"id":cap["id"],"block":cap["block"],"name":cap["name"],"native_functions":cap["function_ids"],"own_packages":ids,"shared_dependencies":[x["id"] for x in groups if not x["id"].startswith("BC")],"completeness":"Estimation complète sous les hypothèses09, pas garantie réalisée.","functions":[funcs[f] for f in cap["function_ids"]]})
 check("Six capabilities and fourteen functions",len(coverage)==6 and sum(len(c["native_functions"]) for c in coverage)==14)
 inputs=["iteration-09-hypotheses.json","iteration-09-estimation.py","iteration-07-m1.json","iteration-07-m2.json","iteration-07-contrat-v1.1.json","iteration-07-marche-preuves.json","iteration-07-spring-preuves.json","iteration-07-resultats.json","iteration-08-calculs.json","iteration-08-contexte.json"]
 result={"id":"iteration-09-resultats","date":h["date"],"status":"estimation_opportunite_conditionnelle_classe_C","origin":h["method"],"roles":ROLES,
 "packages":packages,"groups":groups,"common":common,"direct":direct,"total":total,
 "developer_gross_jh":[total["roles"]["dev_java"][i]+total["roles"]["dev_frontend"][i] for i in range(3)],
 "previous_m1_total":[560,904,1449],"central_delta_vs_m1":total["total"][1]-904,
 "scenario_rules":h["assumptions"],"exclusions":h["exclusions"],"coverage":coverage,
 "calendar":{"phases":phases,"total_months":months,"public_months_ceiling":[math.ceil(x-1e-9) for x in months],"average_contribution_people":[total["total"][i]/(capacity*months[i]) for i in range(3)],"assumptions":h["schedule"]},
 "cumulative":{"compared_capabilities":20,"total_capabilities":88,"new_compared_capabilities":0,"scenario_estimated_capabilities":6,"conditional_opportunity_proposals":6,"measured_or_calibrated_admissions":0,"other_partial":14,"not_compared":68,"ids":oldresult["cumulative_comparative_ids"],"meaning":"Six propositions utilisables pour étudier un investissement conditionnel ; nouveau critère d’usage, pas six preuves acquises ni précision démontrée."},
 "crosschecks":{"COCOMO":"Résultats08 conservés comme sensibilités sur du code partiel : aucune addition, aucun ajustement de09 pour obtenir accord, aucun remplacement du calendrier chargé par rôle.","COSMIC":"350 points conditionnels/25 processus08 utilisés comme contrôle de contenu ; aucun taux CFP/JH.","ISBSG":"Aucun taux compatible retenu ; pas de condition bloquante.","M2":"839/1287/1968 JH historiques, mêmes hypothèses générales mais démarche différente ; divergence de jugement conservée, pas moyenne ni validation indépendante."},
 "full_core_jh":None,"statistical_percentiles":None,
 "next_iteration":{"worthwhile_on_same_six":False,"worthwhile_on_new_family":True,"trigger":"Omission, double compte ou hypothèse de réalisation majeure nouvelle ; sinon élargir la couverture avec la même méthode."},
 "checks":checks,"input_sha256":{n:sha(HERE/n) for n in inputs}}
 write("iteration-09-resultats.json",result)
 print(json.dumps({"total":result["total"],"groups":[{"id":g["id"],"total":g["total"]} for g in groups],"months":months,"public_months":result["calendar"]["public_months_ceiling"],"checks":len(checks)},ensure_ascii=True))
if __name__=="__main__":main()
