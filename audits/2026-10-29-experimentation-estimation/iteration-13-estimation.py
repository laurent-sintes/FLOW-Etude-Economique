"""Audit13 reproducible opportunity estimate; no active model changes."""
import sys,json,math,hashlib,copy,subprocess,os
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def read(n):return json.loads((HERE/n).read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(HERE/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
 checks=[]
 def check(n,ok):
  if not ok:raise AssertionError(n)
  checks.append(n)
 inputs=read("iteration-13-entrees.json");data=inputs["lots"];contract=inputs["contract"]
 prior=read("iteration-12-resultats.json");allcaps=read("iteration-07-resultats.json")["coverage"]
 roles=data["roles"];check("Compatible roles",roles==list(prior["roles"]))
 # Git HEAD and exact file bytes: frozen source observation, no code execution.
 env={k:v for k,v in os.environ.items() if not k.startswith("GIT_")}
 for root,repo,commit in inputs["repositories"].values():
  head=subprocess.check_output(["git","-C",str(ROOT/root),"rev-parse","HEAD"],env=env,text=True).strip()
  check("Frozen commit "+repo,head==commit)
 proofs=copy.deepcopy(inputs["evidence"]);refs={x["id"]:x for x in proofs}
 for x in proofs:
  p=ROOT/x["local_path"];lines=p.read_text(encoding="utf-8").splitlines();x["sha256"]=sha(p)
  repo_root=ROOT/inputs["repositories"][x["id"][0]][0]
  committed=subprocess.check_output(["git","-C",str(repo_root),"show",x["commit"]+":"+x["path"]],env=env)
  check("Source matches commit "+x["id"],p.read_bytes().replace(b"\r\n",b"\n")==committed.replace(b"\r\n",b"\n"))
  check("Source ranges "+x["id"],all(1<=a<=b<=len(lines) for a,b in x["line_ranges"]))
  x["excerpts"]=[{"start":a,"end":b,"text":"\n".join(lines[a-1:b])} for a,b in x["line_ranges"]]
 write("iteration-13-preuves.json",{"evidence":proofs,"method":"Lecture de 11 extraits ciblés dans trois OSS, pas preuve de leur couverture exhaustive ni mesure de charge."})
 # Analytical counterexamples: distinguish quantities and authorities. Not a product test.
 cases=[]
 plan=100;converted=60;remaining_plan=plan-converted;purchase=60
 check("Single economic supply",remaining_plan+purchase==100 and plan+purchase==160)
 cases.append({"id":"X1","question":"Une proposition de100 devient un achat de60.","naive_supply":plan+purchase,"retained_supply":remaining_plan+purchase,"explanation":"La provenance consomme60 de la proposition. S132 + B021 ; B03912 ne réalise pas seul la substitution côté Orders."})
 original=100;fulfilled=40;cancel_accepted=50;remaining=original-fulfilled-cancel_accepted
 check("Partial cancellation conservation",remaining==10 and fulfilled+cancel_accepted+remaining==original)
 current_version=4;command_version=3
 check("Stale change rejected",command_version!=current_version)
 cases.append({"id":"X2","question":"Commande100, réalisé40, annulation de50 acceptée ; autre modification reçue sur une version ancienne.","remaining":remaining,"realized_preserved":fulfilled,"stale_change":"refusée","explanation":"Annulation demandée ne vaut pas acceptée. Les40 réalisés restent un fait ; la modification périmée ne remplace pas la version4."})
 return_qty=10;received=6;credited=4;refunded=4;physical_remaining=return_qty-received
 check("Return branches not additive",physical_remaining==4 and credited==refunded and received+credited+refunded==14)
 cases.append({"id":"X3","question":"Retour10 : reçu6, avoir4 et remboursement4 sur les mêmes quatre unités.","physical_remaining":physical_remaining,"credited":credited,"refunded":refunded,"explanation":"Ces compteurs se recouvrent.14 n’est pas une quantité de retour. Les4 remboursés peuvent avoir terminé leur suite financière sans prouver réception ni résolution des6 autres."})
 commitment=100;already_done=40;children=[20,40];same_terms=False
 check("Split conservation",already_done+sum(children)==commitment)
 check("Quantity equality insufficient for merge",not same_terms)
 cases.append({"id":"X4","question":"Engagement100 dont40 réalisés ; reste scindé en20+40. Deux objets ont des prix incompatibles.","active_remaining":sum(children),"naive_parent_plus_children":commitment+sum(children),"merge_authorized":False,"explanation":"Le parent conserve l’histoire mais son reste transféré n’est plus exécutable. La somme conservée n’autorise pas une fusion commerciale : matrice et autorité explicites dans B027."})
 write("iteration-13-experiences.json",{"kind":"Contre-exemples analytiques inventés pour éprouver le découpage ; aucun runtime ERP/Spring testé.","cases":cases,"passed":4})
 ps=[]
 for raw in data["packages"]:
  p=copy.deepcopy(raw);lo,hi=p["factors"]
  check("Factors "+p["id"],0<lo<=1<=hi)
  check("Java actions "+p["id"],sum(x["jh"] for x in p["java_actions"])==p["central"].get("dev_java",0))
  check("Frontend actions "+p["id"],sum(x["jh"] for x in p["frontend_actions"])==p["central"].get("dev_frontend",0))
  check("Evidence "+p["id"],bool(p["evidence"]) and all(x in refs for x in p["evidence"]))
  check("Roles "+p["id"],set(p["central"])<=set(roles))
  p["effort"]={r:[math.floor(v*lo*2+1e-8)/2,v,math.ceil(v*hi*2-1e-8)/2] for r,v in p["central"].items()}
  p["total"]=[sum(v[i] for v in p["effort"].values()) for i in range(3)];ps.append(p)
 ids={p["id"]:p for p in ps};check("Unique lot owners",len(ids)==len(ps)==14)
 def agg(selected):
  rs={r:[sum(ids[k]["effort"].get(r,[0,0,0])[i] for k in selected) for i in range(3)] for r in roles}
  return {"roles":rs,"total":[sum(v[i] for v in rs.values()) for i in range(3)]}
 caps=sorted([x for x in read("iteration-06-perimetre-a.json")["capabilities"] if x["grid_id"] in [f"BC-{n:03}" for n in range(20,28)]],key=lambda x:x["grid_id"])
 labels={"COMMUN":"Mécanismes communs Commandes","QUAL":"QA, qualification et coordination",**{c["grid_id"]:c["name"] for c in caps}}
 groups=[{"id":g,"label":labels[g],"packages":[p["id"] for p in ps if p["group"]==g],**agg([p["id"] for p in ps if p["group"]==g])} for g in ["COMMUN"]+[c["grid_id"] for c in caps]+["QUAL"]]
 total=agg(list(ids));common=agg([p["id"] for p in ps if not p["group"].startswith("BC")]);direct=agg([p["id"] for p in ps if p["group"].startswith("BC")])
 cumroles={r:[prior["cumulative_estimated"]["roles"][r][i]+total["roles"][r][i] for i in range(3)] for r in roles}
 cum={"roles":cumroles,"total":[prior["cumulative_estimated"]["total"][i]+total["total"][i] for i in range(3)]}
 for i in range(3):
  check("Groups total "+str(i),sum(g["total"][i] for g in groups)==total["total"][i])
  check("Common and direct "+str(i),common["total"][i]+direct["total"][i]==total["total"][i])
  check("Cumulative roles "+str(i),sum(v[i] for v in cumroles.values())==cum["total"][i])
 phaseids=[k for ph in data["schedule"]["phases"] for k in ph["packages"]]
 check("One phase per lot",len(phaseids)==len(set(phaseids))==len(ids) and set(phaseids)==set(ids))
 allocation=data["schedule"]["coordination_split"];capacity=data["schedule"]["days_per_person_month"]
 check("Coordination shares",math.isclose(sum(allocation["shares"].values()),1))
 phases=[]
 for ph in data["schedule"]["phases"]:
  staff=dict(zip(roles,ph["staff"]));work=agg(ph["packages"])
  for i in range(3):
   r=allocation["role"];pid=allocation["package"]
   change=ids[pid]["effort"][r][i]*allocation["shares"][ph["id"]]-(ids[pid]["effort"][r][i] if pid in ph["packages"] else 0)
   work["roles"][r][i]+=change;work["total"][i]+=change
  durations=[];limiting=[]
  for i in range(3):
   check("Staff covers nonzero work "+ph["id"]+str(i),all(staff[r]>0 or v[i]==0 for r,v in work["roles"].items()))
   needs={r:v[i]/(staff[r]*capacity) if staff[r]>0 else 0 for r,v in work["roles"].items()}
   duration=max(ph["floor_months"][i],max(needs.values()));durations.append(duration)
   limiting.append(max(needs,key=needs.get) if max(needs.values())>=ph["floor_months"][i] else "plancher de séquence")
   check("Capacity "+ph["id"]+str(i),all(v[i]<=staff[r]*capacity*duration+1e-8 for r,v in work["roles"].items()))
  phases.append({**ph,"staff":staff,**work,"duration_months":durations,"limiting_role":limiting})
 for r in roles:
  for i in range(3):check("Phase role conservation "+r+str(i),math.isclose(sum(ph["roles"][r][i] for ph in phases),total["roles"][r][i]))
 months=[sum(ph["duration_months"][i] for ph in phases) for i in range(3)]
 combined=[prior["calendar"]["sequential_total_months"][i]+months[i] for i in range(3)]
 coverage=[]
 for c in caps:
  pid="B"+c["grid_id"][3:];check("Capability owner "+c["grid_id"],ids[pid]["group"]==c["grid_id"])
  coverage.append({"id":c["id"],"block":c["grid_id"],"name":c["name"],"path":[x["id"] for x in c["native_path"]],"path_names":[x["name"] for x in c["native_path"]],"functions":c["native_functions"],"boundary":c["boundary"],"source_boundary":c["source_boundary"],"guarantees":c["guarantees"],"core_integration":c["core_integration"],"source_refs":c["source_refs"],"unknowns":c["unknowns"],"own_package":pid,"shared_owners":["E131","S131","S132","Q131","Q132","Q133"],"evidence_ids":ids[pid]["evidence"],"status":"Proposition complète sous hypothèses13 ; classe C non calibrée. Comparaison de mécanismes partiels, pas couverture totale démontrée par un ERP."})
 check("8 capabilities24 functions",len(coverage)==8 and len({f["id"] for c in coverage for f in c["functions"]})==24)
 before=set(prior["progress"]["cumulative_ids"]);studied=before|{c["id"] for c in caps}
 check("Unique cumulative53 new8",len(studied)==53 and len(studied-before)==8)
 check("Native universe88",len(allcaps)==88 and studied<=set(c["id"] for c in allcaps))
 conditional=prior["progress"]["conditional_estimated_now"]+len(caps)
 check("Coverage partition",conditional==53 and 88-len(studied)==35)
 ctx=read("iteration-08-contexte.json")
 for group in ["source_hashes","additional_source_hashes"]:
  for p,h in ctx[group].items():check("Active source unchanged "+p,sha(ROOT/p)==h)
 verification=read("iteration-12-verification.json")
 for n,h in verification["artifacts_sha256"].items():check("Previous audit unchanged "+n,sha(HERE/n)==h)
 files=["iteration-13-entrees.json","iteration-13-preuves.json","iteration-13-experiences.json","iteration-13-estimation.py","iteration-12-resultats.json","iteration-12-verification.json","iteration-06-perimetre-a.json","iteration-07-resultats.json","iteration-08-contexte.json"]
 result={"id":"iteration-13-resultats","date":"2026-10-29","status":"proposition_opportunite_conditionnelle_classe_C","roles":prior["roles"],"packages":ps,"groups":groups,"common":common,"direct":direct,"incremental":total,"previous_cumulative":prior["cumulative_estimated"],"cumulative_estimated":cum,"developer_gross_jh":[total["roles"]["dev_java"][i]+total["roles"]["dev_frontend"][i] for i in range(3)],
 "coverage":coverage,"cumulative_coverage":[{k:c[k] for k in ["id","name","block","path","path_names"] if k in c} for c in allcaps if c["id"] in studied],
 "progress":{"total_native":88,"compared_before":len(before),"compared_cumulative":len(studied),"new_compared":len(studied-before),"new_ids":sorted(studied-before),"cumulative_ids":sorted(studied),"conditional_estimated_before":prior["progress"]["conditional_estimated_now"],"conditional_estimated_now":conditional,"partial_other":len(studied)-conditional,"not_compared":88-len(studied),"empirically_calibrated":0,"meaning":"Couverture en nombre de capacités ; ne mesure ni la part du budget total, ni une précision statistique. Conditionnel ne signifie pas certifié fiable."},
 "calendar":{"phases":phases,"incremental_months":months,"incremental_public_months":[math.ceil(v-1e-9) for v in months],"sequential_total_months":combined,"sequential_public_months":[math.ceil(v-1e-9) for v in combined],"average_contribution_people":[total["total"][i]/(capacity*months[i]) for i in range(3)],"assumptions":data["schedule"]},
 "uncertainty":{"class":"C","percentiles":None,"meaning":data["bounds"],"main_risks":contract["risks"]},"fragile_capabilities":["BC-025","BC-026","BC-027"],"previous_reserves_preserved":prior["fragile_capabilities"],
 "crosschecks":{"COSMIC":"Revue du contenu des24 fonctions et de leurs entrées/sorties/lectures/écritures ; aucun comptage CFP complet ni productivité appliquée.","COCOMO":"Pas de taille comparable complète ni de coefficient réutilisation calibré ; aucun résultat chiffré COCOMO. Calendrier calculé par capacités des rôles et séquences.","ISBSG":"Aucune donnée de charge observée comparable ajoutée ; pas de calibration ni validation croisée entre trois méthodes."},
 "full_core_jh":None,"active_model_changed":False,"next_iteration":{"same_scope":False,"new_scope":True,"recommendation":"Promesse ATP/CTP/PTP et frontière avec réservation/protection : fermer le lien entre plan, disponibilité et engagement sans ajouter des stocks ou des solveurs déjà financés.","deferred":"Transport, prestations, finance et autres capacités non comparées restent inconnus, pas zéro.","reopen_triggers":["Nouvelle garantie ou volume hors contrat","Autorité d’engagement incompatible","Cas de filiation ou de retour non représentable","Omission ou double financement"]},"checks":checks,"input_sha256":{n:sha(HERE/n) for n in files}}
 write("iteration-13-resultats.json",result)
 print(json.dumps({"incremental":total,"cumulative":cum["total"],"months":result["calendar"]["incremental_public_months"],"sequence":result["calendar"]["sequential_public_months"],"checks":len(checks)},ensure_ascii=False))
if __name__=="__main__":main()
