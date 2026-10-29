"""Audit14 reproducible opportunity estimate; no active model changes."""
import sys,json,math,hashlib,copy,subprocess,os,itertools
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
 inputs=read("iteration-14-entrees.json");data=inputs["lots"];contract=inputs["contract"]
 prior=read("iteration-13-resultats.json");allcaps=read("iteration-07-resultats.json")["coverage"]
 roles=data["roles"];check("Compatible roles",roles==list(prior["roles"]))
 # Git HEAD and exact file bytes: frozen source observation, no code execution.
 env={k:v for k,v in os.environ.items() if not k.startswith("GIT_")}
 for root,repo,commit in inputs["repositories"].values():
  head=subprocess.check_output(["git","-C",str(ROOT/root),"rev-parse","HEAD"],env=env,text=True).strip()
  check("Frozen commit "+repo,head==commit)
 proofs=copy.deepcopy(inputs["evidence"]);refs={x["id"]:x for x in proofs}
 for x in proofs:
  p=ROOT/x["local_path"];lines=p.read_text(encoding="utf-8").splitlines();x["sha256"]=sha(p)
  if x["repository"]=="google/or-tools":
   check("Frozen source snapshot "+x["id"],sha(p)==x["snapshot_sha256"])
  else:
   repo_root=ROOT/inputs["repositories"][x["id"][0]][0]
   committed=subprocess.check_output(["git","-C",str(repo_root),"show",x["commit"]+":"+x["path"]],env=env)
   check("Source matches commit "+x["id"],p.read_bytes().replace(b"\r\n",b"\n")==committed.replace(b"\r\n",b"\n"))
  check("Source ranges "+x["id"],all(1<=a<=b<=len(lines) for a,b in x["line_ranges"]))
  x["excerpts"]=[{"start":a,"end":b,"text":"\n".join(lines[a-1:b])} for a,b in x["line_ranges"]]
 write("iteration-14-preuves.json",{"evidence":proofs,"method":"Lecture de 9 extraits ciblés dans trois ERP OSS et3 extraits OR-Tools Java, pas preuve de leur couverture exhaustive ni mesure de charge."})
 # Analytical examples: no ERP or Spring runtime execution.
 cases=[]
 obligations=set(range(30));reserved=set(range(20));stock=100
 available=stock-len(obligations|reserved)
 check("Obligation reservation overlap",available==70 and stock-len(obligations)-len(reserved)==50)
 cases.append({"id":"X1","question":"Stock100, engagement30 dont20 déjà réservés sur la même portion.","naive_available":50,"retained_available":available,"explanation":"L’engagement et sa réservation désignent une même obligation. La provenance évite de retirer deux fois20 ; S142 ne reconstruit pas le registre Reservation10."})
 pool=10;requests=[6,6]
 check("Joint request feasibility",all(q<=pool for q in requests) and sum(requests)>pool)
 cases.append({"id":"X2","question":"Deux lignes de6 consomment le même stock de10.","each_line_alone":True,"whole_request_feasible":False,"uncovered_quantity":sum(requests)-pool,"explanation":"Deux réponses positives indépendantes ne forment pas une promesse d’ensemble. ATP doit signaler2 manquants ou proposer des dates/ressources différentes, selon autorité de fractionnement."})
 material=12;hours=4;hours_per_unit=.5;requested=10
 possible=min(material,int(hours/hours_per_unit))
 check("Finite CTP capacity",possible==8 and possible<requested)
 cases.append({"id":"X3","question":"Besoin10, matière12, capacité4h et0,5h par unité avant échéance.","material_only_possible":12,"finite_capacity_possible":possible,"explanation":"La matière permet10 mais la capacité seulement8. Le délai standard ne justifie pas la promesse ; les2 restantes nécessitent un autre créneau réellement admissible. Sans capacité fournie, réponse indéterminée."})
 costs={"A":{"goods":80,"transport":None},"B":{"goods":95,"transport":10}}
 known={k:(None if any(x is None for x in v.values()) else sum(v.values())) for k,v in costs.items()}
 check("Unknown cost not zero",known["A"] is None and known["B"]==105)
 cases.append({"id":"X4","question":"OptionA : coût80, transport inconnu ; optionB : coût95 + transport10.","costs":known,"automatic_cheapest":None,"explanation":"A ne peut pas être déclarée moins chère sur une somme incomplète. PTP expose le poste absent ; une décision explicite reste possible. Une option violant le service obligatoire serait rejetée même moins chère."})
 proposed_free=10;requested_qty=8;actual_free=6;version=(4,5)
 confirmable=version[0]==version[1] and requested_qty<=actual_free
 check("Revalidation before action",not confirmable and requested_qty<=proposed_free)
 cases.append({"id":"X5","question":"Proposition8 sur disponible10 ; avant confirmation, disponible6 et version changée.","confirmable":confirmable,"explanation":"La durée de validité ne garantit pas l’immobilisation du stock. Orders doit obtenir une revalidation et le résultat de l’acte de réservation/engagement ; pas d’effet exactement une fois présumé à distance."})
 domain=[["A","B"],["A"]]
 valid=lambda choice:len(set(choice))==len(choice)
 full=[x for x in itertools.product(*domain) if valid(x)]
 truncated=[x for x in itertools.product(*[["A"],["A"]]) if valid(x)]
 check("Truncation loses the only solution",full==[("B","A")] and not truncated)
 check("Independent validator rejects shared resource",not valid(("A","A")))
 cases.append({"id":"X6","question":"Deux lignes : la première accepte A ou B, la seconde seulement A ; A est moins cher.","full_solutions":full,"truncated_solutions":truncated,"explanation":"Trier puis garder seulement le premier candidat élimine la seule solution faisable. Une recherche sur le domaine tronqué ne peut pas conclure à l’impossibilité initiale ; le validateur rejette A utilisé deux fois."})
 baskets=[]
 for choices in itertools.product(["A","B"],repeat=3):
  cost=6*choices.count("A")+2*choices.count("B")+(10 if "B" in choices else 0)
  baskets.append((cost,choices))
 best=min(baskets)
 check("Shared fixed cost changes economic choice",best==(16,("B","B","B")) and 3*6==18)
 cases.append({"id":"X7","question":"Trois lignes : A coûte6 par ligne ; B coûte2 par ligne plus10 fixes partagés.","line_by_line_cost":18,"whole_request_optimum":best[0],"whole_request_choice":best[1],"explanation":"Le choix isolé préfère A ; la demande entière préfère B à16 contre18. PTP doit préserver l’assiette des coûts fixes ; le résultat exact ici provient de l’énumération des8 combinaisons, pas d’un benchmark de solveurs."})
 write("iteration-14-experiences.json",{"kind":"Sept contre-exemples analytiques et énumérations inventés ; aucun runtime ERP, Timefold ou OR-Tools exécuté.","cases":cases,"passed":7})

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
 ids={p["id"]:p for p in ps};check("Unique lot owners",len(ids)==len(ps)==11)
 def agg(selected):
  rs={r:[sum(ids[k]["effort"].get(r,[0,0,0])[i] for k in selected) for i in range(3)] for r in roles}
  return {"roles":rs,"total":[sum(v[i] for v in rs.values()) for i in range(3)]}
 caps=sorted([x for x in read("iteration-06-perimetre-a.json")["capabilities"] if x["grid_id"] in [f"BC-{n:03}" for n in range(46,49)]],key=lambda x:x["grid_id"])
 labels={"COMMUN":"Mécanismes communs de promesse","QUAL":"QA, qualification et coordination",**{c["grid_id"]:c["name"] for c in caps}}
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
  coverage.append({"id":c["id"],"block":c["grid_id"],"name":c["name"],"path":[x["id"] for x in c["native_path"]],"path_names":[x["name"] for x in c["native_path"]],"functions":c["native_functions"],"boundary":c["boundary"],"source_boundary":c["source_boundary"],"guarantees":c["guarantees"],"core_integration":c["core_integration"],"source_refs":c["source_refs"],"unknowns":c["unknowns"],"own_package":pid,"shared_owners":["E141","E142","S141","S142","S143","Q141","Q142","Q143"],"evidence_ids":ids[pid]["evidence"],"status":"Proposition complète sous hypothèses14 ; classe C non calibrée. Comparaison de mécanismes partiels, pas couverture totale démontrée par un ERP."})
 check("3 capabilities9 functions",len(coverage)==3 and len({f["id"] for c in coverage for f in c["functions"]})==9)
 before=set(prior["progress"]["cumulative_ids"]);studied=before|{c["id"] for c in caps}
 check("Unique cumulative56 new3",len(studied)==56 and len(studied-before)==3)
 check("Native universe88",len(allcaps)==88 and studied<=set(c["id"] for c in allcaps))
 conditional=prior["progress"]["conditional_estimated_now"]+len(caps)
 check("Coverage partition",conditional==56 and 88-len(studied)==32)
 ctx=read("iteration-08-contexte.json")
 for group in ["source_hashes","additional_source_hashes"]:
  for p,h in ctx[group].items():check("Active source unchanged "+p,sha(ROOT/p)==h)
 verification=read("iteration-13-verification.json")
 for n,h in verification["artifacts_sha256"].items():check("Previous audit unchanged "+n,sha(HERE/n)==h)
 files=["iteration-14-entrees.json","iteration-14-preuves.json","iteration-14-experiences.json","iteration-14-estimation.py","iteration-14-code-ortools/manifest.json","iteration-13-resultats.json","iteration-13-verification.json","iteration-06-perimetre-a.json","iteration-07-resultats.json","iteration-08-contexte.json"]
 result={"id":"iteration-14-resultats","date":"2026-10-29","status":"proposition_opportunite_conditionnelle_classe_C","roles":prior["roles"],"packages":ps,"groups":groups,"common":common,"direct":direct,"incremental":total,"previous_cumulative":prior["cumulative_estimated"],"cumulative_estimated":cum,"developer_gross_jh":[total["roles"]["dev_java"][i]+total["roles"]["dev_frontend"][i] for i in range(3)],
 "coverage":coverage,"cumulative_coverage":[{k:c[k] for k in ["id","name","block","path","path_names"] if k in c} for c in allcaps if c["id"] in studied],
 "progress":{"total_native":88,"compared_before":len(before),"compared_cumulative":len(studied),"new_compared":len(studied-before),"new_ids":sorted(studied-before),"cumulative_ids":sorted(studied),"conditional_estimated_before":prior["progress"]["conditional_estimated_now"],"conditional_estimated_now":conditional,"partial_other":len(studied)-conditional,"not_compared":88-len(studied),"empirically_calibrated":0,"meaning":"Couverture en nombre de capacités ; ne mesure ni la part du budget total, ni une précision statistique. Conditionnel ne signifie pas certifié fiable."},
 "calendar":{"phases":phases,"incremental_months":months,"incremental_public_months":[math.ceil(v-1e-9) for v in months],"sequential_total_months":combined,"sequential_public_months":[math.ceil(v-1e-9) for v in combined],"average_contribution_people":[total["total"][i]/(capacity*months[i]) for i in range(3)],"assumptions":data["schedule"]},
 "uncertainty":{"class":"C","percentiles":None,"meaning":data["bounds"],"main_risks":contract["risks"]},"fragile_capabilities":["BC-047","BC-048"],"previous_reserves_preserved":sorted(set(prior["fragile_capabilities"]+prior.get("previous_reserves_preserved",[]))),
 "crosschecks":{"COSMIC":"Revue du contenu des9 fonctions et de leurs entrées/sorties/lectures/écritures ; aucun comptage CFP complet ni productivité appliquée.","COCOMO":"Pas de taille comparable complète ni de coefficient réutilisation calibré ; aucun résultat chiffré COCOMO. Calendrier calculé par capacités des rôles et séquences.","ISBSG":"Aucune donnée de charge observée comparable ajoutée ; pas de calibration ni validation croisée entre trois méthodes."},
 "algorithm_chain":contract["algorithm_chain"],"stack_components":contract["components"],"refinement":inputs["refinement"],"full_core_jh":None,"active_model_changed":False,"next_iteration":{"same_scope":True,"new_scope":False,"recommendation":"Priorité : essais comparatifs ciblés des chaînes algorithmiques et de CP-SAT/Timefold sur cas ATP/CTP/PTP bornés, pour examiner faisabilité, qualité, latence et coût d’intégration. Ensuite BC008 et BC049 pour les dépendances encore ouvertes.","deferred":"Transport, prestations, finance et autres capacités non comparées restent inconnus, pas zéro.","reopen_triggers":["Nouvelle garantie ou volume hors contrat","Autorité d’engagement incompatible","Dépendance matière/opération ou critère économique hors contrat","Omission ou double financement"]},"checks":checks,"input_sha256":{n:sha(HERE/n) for n in files}}
 write("iteration-14-stack-java.json",{"date":"2026-10-29","status":"stack_du_candidat_estimation_non_appliquee_aux_sources_actives","components":contract["components"],"algorithm_chain":contract["algorithm_chain"],"sources":contract["public_sources"]})
 write("iteration-14-resultats.json",result)
 print(json.dumps({"incremental":total,"cumulative":cum["total"],"months":result["calendar"]["incremental_public_months"],"sequence":result["calendar"]["sequential_public_months"],"checks":len(checks)},ensure_ascii=False))
if __name__=="__main__":main()
