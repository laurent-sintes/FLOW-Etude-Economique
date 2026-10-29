"""Stocks: conditional engineering estimate and incremental consolidation, audit only."""
import hashlib,json,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
def read(n):return json.loads((HERE/n).read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(HERE/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
 data=read("iteration-10-lots.json");ref=read("iteration-09-resultats.json");proof=read("iteration-10-preuves.json");contract=read("iteration-10-contrat.json")
 native=read("iteration-06-perimetre-a.json");roles=ref["roles"];checks=[]
 def check(n,ok):
  checks.append({"check":n,"passed":bool(ok)})
  if not ok:raise AssertionError(n)
 check("Roles are unchanged",list(roles)==data["roles"])
 pids={x["id"] for x in proof["evidence"]}
 for p in proof["evidence"]:
  check("Code hash "+p["id"],sha(ROOT/p["cache_path"])==p["sha256"])
  lines=(ROOT/p["cache_path"]).read_text(encoding="utf-8").splitlines()
  check("Read ranges "+p["id"],all(1<=a<=b<=len(lines) for a,b in p["ranges"]))
 ps=[]
 for p in data["packages"]:
  p=dict(p);lo,hi=p["range_factors"]
  check("Java decomposition "+p["id"],sum(v for _,v in p["java_breakdown"])==p["central"]["dev_java"])
  check("Evidence ids "+p["id"],all(x in pids for x in p["proof_ids"]))
  p["effort"]={r:[math.floor(c*lo*2)/2,c,math.ceil(c*hi*2)/2] for r,c in p["central"].items()}
  check("Ordered estimates "+p["id"],all(0<=v[0]<=v[1]<=v[2] for v in p["effort"].values()))
  p["total"]=[sum(v[i] for v in p["effort"].values()) for i in range(3)];ps.append(p)
 ids={p["id"]:p for p in ps};check("Unique funding owners",len(ids)==len(ps)==20)
 def agg(selected):
  values={r:[sum(ids[k]["effort"].get(r,[0,0,0])[i] for k in selected) for i in range(3)] for r in roles}
  return {"roles":values,"total":[sum(v[i] for v in values.values()) for i in range(3)]}
 labels={"EXT":"Extensions du socle déjà financé","COMMUN":"Mécanismes communs aux stocks","QUAL":"Qualification et coordination transverses"}
 caps=[c for c in native["capabilities"] if c["native_path"][1]["id"]=="D01"]
 for c in caps:labels[c["grid_id"]]=c["name"]
 group_order=["EXT","COMMUN"]+[c["grid_id"] for c in caps]+["QUAL"]
 groups=[{"id":g,"label":labels[g],"packages":[p["id"] for p in ps if p["group"]==g],**agg([p["id"] for p in ps if p["group"]==g])} for g in group_order]
 total=agg(list(ids));common=agg([p["id"] for p in ps if not p["group"].startswith("BC")]);direct=agg([p["id"] for p in ps if p["group"].startswith("BC")])
 cumulative_roles={r:[ref["total"]["roles"][r][i]+total["roles"][r][i] for i in range(3)] for r in roles}
 cum={"roles":cumulative_roles,"total":[ref["total"]["total"][i]+total["total"][i] for i in range(3)]}
 for i in range(3):
  check("Shared plus own "+str(i),common["total"][i]+direct["total"][i]==total["total"][i])
  check("Groups equal total "+str(i),sum(g["total"][i] for g in groups)==total["total"][i])
  check("Cumulative roles "+str(i),sum(v[i] for v in cumulative_roles.values())==cum["total"][i])
 phaseids=[x for ph in data["schedule"]["phases"] for x in ph["packages"]]
 check("Phase attribution",len(phaseids)==len(set(phaseids))==len(ids) and set(phaseids)==set(ids))
 phases=[];capacity=data["schedule"]["days_per_person_month"]
 for ph in data["schedule"]["phases"]:
  staff=dict(zip(roles,ph["staff"]));work=agg(ph["packages"]);allocation=data["schedule"]["coordination_split"];pid=allocation["package"];r=allocation["role"]
  for i in range(3):
   change=ids[pid]["effort"][r][i]*allocation["shares"].get(ph["id"],0)-(ids[pid]["effort"][r][i] if pid in ph["packages"] else 0)
   work["roles"][r][i]+=change;work["total"][i]+=change
  durations=[];limiting=[]
  for i in range(3):
   needs={r:v[i]/(staff[r]*capacity) for r,v in work["roles"].items()}
   duration=max(ph["floor_months"][i],max(needs.values()));durations.append(duration)
   limiting.append(max(needs,key=needs.get) if max(needs.values())>=ph["floor_months"][i] else "plancher")
   check("Capacity "+ph["id"]+str(i),all(v[i]<=staff[r]*capacity*duration+1e-8 for r,v in work["roles"].items()))
  phases.append({**ph,"staff":staff,**work,"duration_months":durations,"limiting_role":limiting})
 months=[sum(ph["duration_months"][i] for ph in phases) for i in range(3)]
 combined_months=[months[i]+ref["calendar"]["total_months"][i] for i in range(3)]
 for r in roles:
  for i in range(3):check("Phase workload "+r+str(i),math.isclose(sum(ph["roles"][r][i] for ph in phases),total["roles"][r][i]))
 check("Ordered calendar",months[0]<=months[1]<=months[2])
 coverage=[]
 for c in caps:
  pid="B"+c["grid_id"].split("-")[1];p=ids[pid]
  ev=[e["id"] for e in proof["evidence"] if c["grid_id"] in e["caps"]]
  check("Compared and funded "+c["grid_id"],bool(ev) and p["group"]==c["grid_id"])
  coverage.append({"id":c["id"],"block":c["grid_id"],"name":c["name"],"path":c["native_path"],"functions":c["native_functions"],"boundary":c["boundary"],"own_package":pid,"shared_owners":["EXT","COMMUN","QUAL"],"evidence_ids":ev,"market_match":"Comparaison partielle avec différences et ingénierie propre explicites.","effort_status":"Proposition complète conditionnelle de classe C, non calibrée","existing_unknowns":c["unknowns"]})
 check("Native functions covered",len(coverage)==10 and len({f["id"] for c in coverage for f in c["functions"]})==29)
 prior=set(ref["cumulative"]["ids"]);current=prior|{c["id"] for c in caps};new=sorted(current-prior)
 check("Unique cumulative coverage",len(current)==25 and len(new)==5)
 context=read("iteration-08-contexte.json")
 for group in ["source_hashes","additional_source_hashes"]:
  for p,h in context[group].items():check("Active source unchanged "+p,sha(ROOT/p)==h)
 input_files=["iteration-10-contrat.json","iteration-10-preuves.json","iteration-10-lots.json","iteration-10-estimation.py","iteration-09-resultats.json","iteration-09-verification.json","iteration-06-perimetre-a.json","iteration-07-resultats.json","iteration-08-contexte.json"]
 result={"id":"iteration-10-resultats","date":"2026-10-29","status":"proposition_opportunite_conditionnelle_classe_C","roles":roles,"packages":ps,"groups":groups,"common":common,"direct":direct,"incremental":total,"reference_family":ref["total"],"cumulative_estimated":cum,
 "developer_gross_jh":[total["roles"]["dev_java"][i]+total["roles"]["dev_frontend"][i] for i in range(3)],
 "scope":"Dix capacités Inventory Management plus leurs extensions/communs, sur les six références09 supposées réalisées.",
 "coverage":coverage,
 "progress":{"total_native":88,"compared_before":20,"compared_cumulative":25,"new_compared":5,"new_ids":new,"cumulative_ids":sorted(current),"conditional_estimated_before":6,"conditional_estimated_now":16,"partial_other":9,"not_compared":63,"empirically_calibrated":0,"meaning":"Progrès de couverture comparative et propositions d’ingénierie, pas de calibration statistique ni d’admission au modèle actif."},
 "calendar":{"phases":phases,"incremental_months":months,"incremental_public_months":[math.ceil(x-1e-9) for x in months],"reference_months":ref["calendar"]["total_months"],"sequential_total_months":combined_months,"sequential_public_months":[math.ceil(x-1e-9) for x in combined_months],"average_contribution_people":[total["total"][i]/(18*months[i]) for i in range(3)],"assumptions":data["schedule"]},
 "uncertainty":{"class":"C","percentiles":None,"meaning":data["bounds"],"main_risks":contract["risks"]},
 "crosschecks":{"COSMIC":"Revue des 29 fonctions natives et de leurs entrées, écritures, lectures et sorties comme contrôle de contenu ; aucun nouveau comptage CFP complet ni conversion en JH revendiqué.","COCOMO":"Pas de taille complète comparable établie pour ces dix capacités. Aucune extrapolation des chiffres partiels08 ni application de leur calendrier. Le délai10 est calculé par charge/capacité et séquencement.","ISBSG":"Pas de nouvelle productivité compatible retenue ; estimation d’ingénierie assumée."},
 "full_core_jh":None,"active_model_changed":False,
 "next_iteration":{"same_family":False,"new_family":True,"recommendation":"Orchestration des processus, en réutilisant les mécanismes et en évitant de refinancer les transitions locales déjà retenues.","reopen_triggers":["Omission ou double financement identifié","Hypothèse majeure de volumétrie, historique ou règles modifiée","Équipe disponible différente nécessitant un autre calendrier"]},
 "checks":checks,"input_sha256":{n:sha(HERE/n) for n in input_files}}
 write("iteration-10-resultats.json",result)
 print(json.dumps({"incremental":total,"cumulative":cum["total"],"groups":[{"id":g["id"],"total":g["total"]} for g in groups],"months":months,"sequential":combined_months,"public":[result["calendar"]["incremental_public_months"],result["calendar"]["sequential_public_months"]],"checks":len(checks)},ensure_ascii=True))
if __name__=="__main__":main()
