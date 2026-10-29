"""Iteration11 opportunity estimate. No active model edits or calibrated productivity."""
import json,math,hashlib,copy
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def read(n):return json.loads((HERE/n).read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(HERE/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
 checks=[]
 def check(name,ok):
  if not ok:raise AssertionError(name)
  checks.append(name)
 data=read("iteration-11-lots.json");contract=read("iteration-11-contrat.json");proof=read("iteration-11-preuves.json")
 prior=read("iteration-10-resultats.json");native=read("iteration-06-perimetre-c.json");allcaps=read("iteration-07-resultats.json")["coverage"]
 roles=data["roles"];check("Role compatibility",roles==list(prior["roles"]))
 refs={x["id"]:x for x in proof["evidence"]}
 for x in refs.values():
  check("Proof integrity "+x["id"],sha(ROOT/x["local_path"])==x["sha256"])
  lines=(ROOT/x["local_path"]).read_text(encoding="utf-8").splitlines()
  check("Proof ranges "+x["id"],all(1<=a<=z<=len(lines) for a,z in x["line_ranges"]))
 ps=[]
 for raw in data["packages"]:
  p=copy.deepcopy(raw);lo,hi=p["factors"]
  check("Factors "+p["id"],0<lo<=1<=hi)
  check("Java action sum "+p["id"],sum(a["jh"] for a in p["java_actions"])==p["central"].get("dev_java",0))
  check("Frontend action sum "+p["id"],sum(a["jh"] for a in p["frontend_actions"])==p["central"].get("dev_frontend",0))
  check("Evidence references "+p["id"],bool(p["evidence"]) and all(k in refs for k in p["evidence"]))
  check("Role names "+p["id"],all(r in roles for r in p["central"]))
  p["effort"]={r:[math.floor(v*lo*2+1e-8)/2,v,math.ceil(v*hi*2-1e-8)/2] for r,v in p["central"].items()}
  check("Ordered charge "+p["id"],all(0<=x[0]<=x[1]<=x[2] for x in p["effort"].values()))
  p["total"]=[sum(v[i] for v in p["effort"].values()) for i in range(3)];ps.append(p)
 ids={p["id"]:p for p in ps}
 check("Unique lot owner",len(ids)==len(ps)==18)
 def agg(selected):
  values={r:[sum(ids[k]["effort"].get(r,[0,0,0])[i] for k in selected) for i in range(3)] for r in roles}
  return {"roles":values,"total":[sum(v[i] for v in values.values()) for i in range(3)]}
 caps=[c for c in native["capabilities"] if c["native_path"][1]=="subdomain-process-management" and int(c["bc_ref"].split("-")[1])<=86]
 excluded=[c for c in native["capabilities"] if c["native_path"][1]=="subdomain-process-management" and int(c["bc_ref"].split("-")[1])>86]
 labels={"MOTEUR":"Raccordement et qualification du moteur","COMMUN":"Contrats et composition techniques communs","QUAL":"Qualification, corrections et coordination"}
 labels.update({c["bc_ref"]:c["native_name"] for c in caps})
 order=["MOTEUR","COMMUN"]+[c["bc_ref"] for c in caps]+["QUAL"]
 groups=[{"id":g,"label":labels[g],"packages":[p["id"] for p in ps if p["group"]==g],**agg([p["id"] for p in ps if p["group"]==g])} for g in order]
 total=agg(list(ids));common=agg([p["id"] for p in ps if not p["group"].startswith("BC")]);direct=agg([p["id"] for p in ps if p["group"].startswith("BC")])
 cumulative_roles={r:[prior["cumulative_estimated"]["roles"][r][i]+total["roles"][r][i] for i in range(3)] for r in roles}
 cum={"roles":cumulative_roles,"total":[prior["cumulative_estimated"]["total"][i]+total["total"][i] for i in range(3)]}
 for i in range(3):
  check("Groups equal total "+str(i),sum(g["total"][i] for g in groups)==total["total"][i])
  check("Common plus direct "+str(i),common["total"][i]+direct["total"][i]==total["total"][i])
  check("Cumulative by role "+str(i),sum(v[i] for v in cum["roles"].values())==cum["total"][i])
 phaseids=[k for ph in data["schedule"]["phases"] for k in ph["packages"]]
 check("One phase per lot",len(phaseids)==len(set(phaseids))==len(ids) and set(phaseids)==set(ids))
 phases=[];capacity=data["schedule"]["days_per_person_month"];allocation=data["schedule"]["coordination_split"]
 check("Coordination shares",math.isclose(sum(allocation["shares"].values()),1))
 for ph in data["schedule"]["phases"]:
  staff=dict(zip(roles,ph["staff"]));work=agg(ph["packages"])
  pid=allocation["package"];r=allocation["role"]
  for i in range(3):
   change=ids[pid]["effort"][r][i]*allocation["shares"][ph["id"]]-(ids[pid]["effort"][r][i] if pid in ph["packages"] else 0)
   work["roles"][r][i]+=change;work["total"][i]+=change
  durations=[];limiting=[]
  for i in range(3):
   needs={r:v[i]/(staff[r]*capacity) for r,v in work["roles"].items()}
   duration=max(ph["floor_months"][i],max(needs.values()));durations.append(duration)
   limiting.append(max(needs,key=needs.get) if max(needs.values())>=ph["floor_months"][i] else "plancher de séquence")
   check("Capacity "+ph["id"]+str(i),all(v[i]<=staff[r]*capacity*duration+1e-8 for r,v in work["roles"].items()))
  phases.append({**ph,"staff":staff,**work,"duration_months":durations,"limiting_role":limiting})
 for r in roles:
  for i in range(3):check("Phase charge conservation "+r+str(i),math.isclose(sum(ph["roles"][r][i] for ph in phases),total["roles"][r][i]))
 months=[sum(ph["duration_months"][i] for ph in phases) for i in range(3)]
 combined=[prior["calendar"]["sequential_total_months"][i]+months[i] for i in range(3)]
 coverage=[]
 for c in caps:
  pid="B"+c["bc_ref"].split("-")[1]
  check("Funded native capability "+c["bc_ref"],pid in ids and ids[pid]["group"]==c["bc_ref"])
  coverage.append({"id":c["id"],"block":c["bc_ref"],"name":c["native_name"],"path":c["native_path"],"functions":c["native_functions"],"boundary":c["native_boundary"],"boundaries":c["boundaries"],"own_package":pid,"shared_owners":["E111","S111","S112","Q111","Q112","Q113","Q114"],"evidence_ids":ids[pid]["evidence"],"status":"Proposition complète sous les hypothèses bornées11 ; classe C, non calibrée","evidence_strength":"Correspondances partielles et écarts propres ; aucun produit n’est déclaré couvrir la capacité native en totalité."})
 check("11 capabilities and33 functions",len(coverage)==11 and len({f["id"] for c in coverage for f in c["functions"]})==33)
 studied_before=set(prior["progress"]["cumulative_ids"]);studied=studied_before|{c["id"] for c in caps}
 check("Unique cumulative comparison",len(studied)==30 and len(studied-studied_before)==5)
 check("Native universe",len(allcaps)==88 and studied.issubset({c["id"] for c in allcaps}))
 conditional=prior["progress"]["conditional_estimated_now"]+len(caps)
 check("Progress partition",conditional==27 and len(studied)-conditional==3 and 88-len(studied)==58)
 ctx=read("iteration-08-contexte.json")
 for group in ["source_hashes","additional_source_hashes"]:
  for p,h in ctx[group].items():check("Active source unchanged "+p,sha(ROOT/p)==h)
 verification=read("iteration-10-verification.json")
 for n,h in verification["artifacts_sha256"].items():check("Previous audit unchanged "+n,sha(HERE/n)==h)
 files=["iteration-11-contrat.json","iteration-11-lots.json","iteration-11-preuves.json","iteration-11-estimation.py","iteration-10-resultats.json","iteration-10-verification.json","iteration-06-perimetre-c.json","iteration-07-resultats.json","iteration-08-contexte.json"]
 result={"id":"iteration-11-resultats","date":"2026-10-29","status":"proposition_opportunite_conditionnelle_classe_C","roles":prior["roles"],"packages":ps,"groups":groups,"common":common,"direct":direct,"incremental":total,"previous_cumulative":prior["cumulative_estimated"],"cumulative_estimated":cum,
 "developer_gross_jh":[total["roles"]["dev_java"][i]+total["roles"]["dev_frontend"][i] for i in range(3)],
 "coverage":coverage,"excluded_capabilities":[{"id":c["id"],"block":c["bc_ref"],"name":c["native_name"]} for c in excluded],
 "progress":{"total_native":88,"compared_before":25,"compared_cumulative":len(studied),"new_compared":len(studied-studied_before),"new_ids":sorted(studied-studied_before),"cumulative_ids":sorted(studied),"conditional_estimated_before":16,"conditional_estimated_now":conditional,"partial_other":len(studied)-conditional,"not_compared":88-len(studied),"empirically_calibrated":0,"meaning":"Couverture de propositions sous hypothèses, pas taux de coût couvert ni précision statistique."},
 "calendar":{"phases":phases,"incremental_months":months,"incremental_public_months":[math.ceil(v-1e-9) for v in months],"previous_sequential_months":prior["calendar"]["sequential_total_months"],"sequential_total_months":combined,"sequential_public_months":[math.ceil(v-1e-9) for v in combined],"average_contribution_people":[total["total"][i]/(18*months[i]) for i in range(3)],"assumptions":data["schedule"]},
 "uncertainty":{"class":"C","percentiles":None,"meaning":data["bounds"],"main_risks":contract["risks"]},
 "crosschecks":{"COSMIC":"Revue des33 fonctions natives et des échanges/lectures/écritures attendus pour contrôler le contenu. Pas de comptage CFP complet ni conversion en JH.","COCOMO":"Pas de taille complète comparable de ces11 capacités. Pas d’application chiffrée ni de validation croisée revendiquée ; délai par charge/capacité et séquencement.","ISBSG":"Aucune productivité empirique compatible ajoutée. Les JH restent des jugements d’ingénierie étayés par mécanismes et travaux."},
 "full_core_jh":None,"active_model_changed":False,"next_iteration":{"same_scope":False,"new_scope":True,"recommendation":"Planification/optimisation : avancer le périmètre métier et choisir le bon niveau d’estimation, sans recomptage de Process Planning ni Planning Data Provision.","deferred":"Process Mining et Operational Analysis & Reporting restent à traiter séparément ; pas zéro.","reopen_triggers":["Omission ou double financement démontré","Contrats des commandes/effets externes incompatibles avec les hypothèses","Migration en vol ou composition libre exigée","Volumétrie ou équipe disponible significativement différente"]},
 "checks":checks,"input_sha256":{n:sha(HERE/n) for n in files}}
 write("iteration-11-resultats.json",result)
 print(json.dumps({"incremental":total,"cumulative":cum["total"],"groups":[{"id":g["id"],"total":g["total"]} for g in groups],"months":months,"sequential":combined,"public":[result["calendar"]["incremental_public_months"],result["calendar"]["sequential_public_months"]],"checks":len(checks)},ensure_ascii=True))
if __name__=="__main__":main()
