from pathlib import Path
import json,math,hashlib,subprocess,collections
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
GIT=r"C:/Users/laure/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe"
def load(n):return json.loads((OUT/n).read_text(encoding="utf-8-sig"))
m=load("measurements.json");i=load("inputs.json");r=load("results.json");b=load("baseline.json")
failures=[];count=0
def check(label,value):
 global count
 count+=1
 if not value:failures.append(label)
trees={}
for name,repo in m["repos"].items():
 head=subprocess.check_output([GIT,"-C",str(ROOT/repo["root"]),"rev-parse","HEAD"],text=True).strip()
 check("commit:"+name,head==repo["commit"])
 raw=subprocess.check_output([GIT,"-C",str(ROOT/repo["root"]),"ls-tree","-rz","HEAD"]);tree={}
 for entry in raw.split(b"\0"):
  if not entry:continue
  meta,path=entry.split(b"\t",1);mode,kind,sha=meta.split()
  if kind==b"blob":tree[path.decode()]=sha.decode()
 trees[name]=tree
keys=set();verified=0
for f in m["files"]:
 key=(f["product"],f["repo"],f["path"])
 check("unique:"+str(key),key not in keys);keys.add(key)
 data=(ROOT/m["repos"][f["repo"]]["root"]/f["path"]).read_bytes()
 candidates=[data,data.replace(b"\r\n",b"\n")]
 ok=any(hashlib.sha1(b"blob "+str(len(d)).encode()+b"\0"+d).hexdigest()==trees[f["repo"]].get(f["path"]) for d in candidates)
 check("git_blob:"+f["path"],ok);verified+=int(ok)
 check("snapshot:"+f["path"],hashlib.sha256(data).hexdigest()==f["sha256"])
 check("nonnegative:"+f["path"],f["program_units"]>=0 and f["declarative_units"]>=0)
for path,h in b["files"].items():check("active_unchanged:"+path,hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h)
proof_count=0
for contract in i["scope"]["contracts"]:
 for product,proofs in contract["proofs"].items():
  for repo,path in proofs:
   proof_count+=1;check("contract_source:"+contract["id"]+":"+product+":"+path,(product,repo,path) in keys)
for result in r["results"]:
 for scenario in i["scenarios"]:
  s=result["scenarios"][scenario["id"]];p=result["id"]
  rows=[x for x in m["files"] if x["product"]==p]
  new=sum(x["program_units"]+scenario["declarative_weight"]*x["declarative_units"] for x in rows if x["treatment"]=="new")
  reused=sum(x["program_units"]+scenario["declarative_weight"]*x["declarative_units"] for x in rows if x["treatment"]=="reused")
  adjustment=scenario["AA"]/100+scenario["IM"]*.003
  expected_units=new+reused*adjustment
  pm=math.exp(math.log(2.94)+1.0997*math.log(expected_units/1000))*scenario["PERS"]*scenario["PREX"]
  expected_jh=pm*152/7*1.18
  expected_months=math.exp(math.log(3.67)+.31794*math.log(pm))*1.25
  check("effort:"+p+scenario["id"],math.isclose(expected_jh,s["total_jh"],rel_tol=1e-12))
  check("schedule:"+p+scenario["id"],math.isclose(expected_months,s["total_schedule_months"],rel_tol=1e-12))
 check("activity_total:"+result["id"],math.isclose(sum(a["jh"] for a in result["activities_central"]),result["scenarios"]["central"]["total_jh"],rel_tol=1e-12))
 check("scenario_order:"+result["id"],result["scenarios"]["lower"]["total_jh"]<result["scenarios"]["central"]["total_jh"]<result["scenarios"]["upper"]["total_jh"])
 check("no_probability:"+result["id"],result["probability"] is None)
 check("monotonic_sensitivities:"+result["id"],all(v[0]<v[1] for v in result["single_parameter_sensitivity"].values()))
# Verify that the targeted wrong-boundary files/blocks are actually absent, not just listed in prose.
for product,repo,path in [
 ("erpnext","erpnext","erpnext/stock/get_item_details.py"),("erpnext","erpnext","erpnext/utilities/transaction_base.py"),
 ("odoo","odoo","addons/stock/models/stock_warehouse.py"),("odoo","odoo","addons/delivery/models/delivery_carrier.py"),
 ("tryton","tryton","modules/product_kit/stock.py"),("axelor","axelor","axelor-stock/src/main/java/com/axelor/apps/stock/service/StockLocationLineServiceImpl.java")]:
 check("transaction_file_excluded:"+path,(product,repo,path) not in keys)
removed=[(x["product"],e["name"]) for x in m["files"] for e in x["excluded_blocks"]]
for pair in [("erpnext","validate_opening_stock"),("odoo","StockRoute"),("tryton","ProductsByLocations"),("axelor","getStockIndicators")]:check("transaction_block_excluded:"+str(pair),pair in removed)
check("no_parse_errors",not m["errors"])
check("input_hash",hashlib.sha256((OUT/"inputs.json").read_bytes()).hexdigest()==r["inputs_sha256"])
check("measurement_hash",hashlib.sha256((OUT/"measurements.json").read_bytes()).hexdigest()==r["measurements_sha256"])
check("manual_reference_example",abs(2.94*100**1.15-586.61)<.01)
check("unmodified_reuse_central",i["reuse"]["DM"]==0 and i["reuse"]["CM"]==0 and i["reuse"]["SU"]==0)
check("no_sum_of_alternatives",r["progress"]["sum_of_alternatives"] is None)
out={"passed":not failures,"checks":count,"failures":failures,"source_files_verified":verified,"active_files_unchanged":len(b["files"]),"contract_source_links":proof_count,"status":"Contrôles d'arithmétique, de frontière déclarée et de traçabilité. Aucune validation historique des JH ni revue humaine externe.","parent_counter_tests":"../2026-10-30-master-data-natif/verification.json"}
(OUT/"verification.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(out,ensure_ascii=False));raise SystemExit(0 if out["passed"] else 1)
