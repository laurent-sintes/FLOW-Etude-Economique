from pathlib import Path
import json,hashlib,math,sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[];errors=[]
def check(ok,label):
 checks.append(label)
 if not ok:errors.append(label)
i=read(OUT/"inputs.json");r=read(OUT/"results.json");a=read(OUT/"analogues.json");cfp=read(OUT/"cosmic-candidate.json")
native=read(ROOT/"audits/2026-10-30-master-data-comparable-reuse/measurements.json")
for p,h in read(OUT/"baseline.json")["files"].items():check(sha(ROOT/p)==h,"active:"+p)
for p,h in i["input_hashes"].items():check(sha(ROOT/p)==h,"input:"+p)
for n,h in r["input_hashes"].items():check(sha(OUT/n)==h,"output-input:"+n)
for f in native["files"]:
 p=ROOT/native["repos"][f["repo"]]["root"]/f["path"];check(sha(p)==f["sha256"],"native:"+f["repo"]+"/"+f["path"])
for s in a["samples"]:check(sha(ROOT/s["path"])==s["sha256"],"analogue:"+s["id"])
ids=[b["id"] for b in i["blocks"]];check(len(ids)==len(set(ids)),"unique residual blocks")
contracts=set(c for b in i["blocks"] for c in b["contracts"])|set(c for s in i["schemas"] for c in s["contracts"])
check(all(f"F{x:02}" in contracts for x in range(1,12)),"11 contract sections mapped")
old=read(ROOT/"audits/2026-10-29-experimentation-estimation/iteration-08-taille.json")
for d in i["deduplication"]:
 original=next(x for x in old["backend_blocks"] if x["id"]==d["id"])["blocks"]
 keep=d["included_residual"];excluded=d["already_in_native_equivalent_reference"]
 check(not set(keep)&set(excluded) and set(keep+excluded)==set(original),"partition:"+d["id"])
 for x in excluded:check(d["id"]+"/"+x not in ids,"not recharged:"+d["id"]+"/"+x)
for sc in i["schemas"]:check(not set(sc["fields"])&set(sc["already_in_reference"]),"schema disjoint:"+sc["name"])
for s in r["selected"]["scenarios"].values():
 pm=2.94*s["equivalent_KSLOC"]**1.0997
 scenario=next(k for k,v in r["selected"]["scenarios"].items() if v is s)
 em={"lower":.83*.87,"central":1.0,"upper":1.26*1.12}[scenario]
 jh=pm*em*152/7*1.18;months=3.67*(pm*em)**.31794*1.25
 check(math.isclose(jh,s["total_jh"]),"arithmetic effort "+scenario)
 check(math.isclose(months,s["months"]),"arithmetic schedule "+scenario)
 check(math.isclose(s["common_reference_jh"]+s["incremental_flow_jh"],jh),"increment reconciliation "+scenario)
check(math.isclose(sum(x["jh"] for x in r["activities"]),r["selected"]["scenarios"]["central"]["total_jh"]),"activity reconciliation")
check(math.isclose(sum(x["jh"] for x in r["increment_allocation"]),r["selected"]["scenarios"]["central"]["incremental_flow_jh"]),"increment allocation reconciliation")
groups={x["id"] for x in cfp["groups"]};process_ids=[]
for p in cfp["processes"]:
 process_ids.append(p["id"]);check(sum(m["cfp"] for m in p["movements"])==p["count"]["cfp"],"CFP sum:"+p["id"])
 check(all(m["group"] in groups and m["type"] in "ERWX" and m["cfp"]==1 for m in p["movements"]),"CFP movements:"+p["id"])
 check(any(m["type"]=="E" for m in p["movements"]),"CFP trigger:"+p["id"])
check(len(process_ids)==len(set(process_ids)),"unique functional processes")
total=sum(p["count"]["cfp"] for p in cfp["processes"])
check(total==r["functional_crosscheck"]["size_CFP"],"functional total")
check(math.isclose(total*20*.8/7,r["functional_crosscheck"]["jh"]["central"]),"ISBSG conversion")
check(300<=total<=500,"benchmark size band")
check(r["uncertainty"]["percentile"] is None,"no fictitious percentile")
check(i["framework_policy"]["adjustment_factor"]==1 and not i["framework_policy"]["observed_equivalence_of_effort"],"neutral framework hypothesis, not observed equality")
out={"passed":not errors,"checks":len(checks),"errors":errors,"native_source_files":len(native["files"]),"analogue_samples":len(a["samples"]),"active_files_unchanged":len(read(OUT/"baseline.json")["files"]),"limitations":"Vérifie intégrité, frontières déclarées et calculs ; ne valide pas la conception, les quantités proposées, l'équivalence de productivité ni la performance S1."}
(OUT/"verification.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out,ensure_ascii=False))
if errors:sys.exit(1)
