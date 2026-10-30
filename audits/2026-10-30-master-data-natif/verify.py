from pathlib import Path
import json,hashlib,subprocess,math,ast,tempfile,importlib.util
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
GIT=r"C:/Users/laure/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe"
def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
m=load(OUT/"manifest.json");q=load(OUT/"measurements.json");i=load(OUT/"inputs.json");r=load(OUT/"results.json");b=load(OUT/"baseline.json")
checks=[];failures=[]
def check(label,value):
    checks.append(label)
    if not value:failures.append(label)
trees={}
eol_normalized=0
for key,repo in m["repos"].items():
    raw=subprocess.check_output([GIT,"-C",str(ROOT/repo["root"]),"ls-tree","-rz","HEAD"])
    tree={}
    for entry in raw.split(b"\0"):
        if not entry:continue
        meta,path=entry.split(b"\t",1)
        mode,kind,sha=meta.split(b" ")
        if kind==b"blob":tree[path.decode("utf-8")]=sha.decode()
    trees[key]=tree
    head=subprocess.check_output([GIT,"-C",str(ROOT/repo["root"]),"rev-parse","HEAD"],text=True).strip()
    check("commit:"+key,head==repo["commit"])
seen=set()
for row in m["files"]:
    repo,path=row["repo"],row["path"];key=(row["product"],repo,path)
    check("unique:"+str(key),key not in seen);seen.add(key)
    content=(ROOT/m["repos"][repo]["root"]/path).read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(content)).encode()+b"\0"+content).hexdigest()
    blob_matches=trees[repo].get(path)==blob
    if not blob_matches and b"\r\n" in content:
        normalized=content.replace(b"\r\n",b"\n")
        blob_lf=hashlib.sha1(b"blob "+str(len(normalized)).encode()+b"\0"+normalized).hexdigest()
        blob_matches=trees[repo].get(path)==blob_lf
        if blob_matches:eol_normalized+=1
    check("git_blob:"+repo+":"+path,blob_matches)
    check("sha256:"+repo+":"+path,hashlib.sha256(content).hexdigest()==row["sha256"])
for path,h in b["files"].items():check("active_unchanged:"+path,hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h)
check("no_parser_errors",not q["errors"])
check("all_files_measured",len(q["files"])==len(m["files"]))
for fam in i["scope"]["families"]:
    for product in i["products"]:
        repo,path=fam[product["id"]]
        check("functional_evidence:"+product["id"]+":"+fam["label"],(product["id"],repo,path) in seen)
for row in r["results"]:
    subtotal=[x for x in q["files"] if x["product"]==row["id"]]
    p=sum(x["program_units"] for x in subtotal);d=sum(x["declarative_units"] for x in subtotal)
    check("recomputed_size:"+row["id"],row["program_units"]==p and row["declarative_units"]==d)
    # Independent expression, no call to calculate.estimate().
    base_pm=math.exp(math.log(2.94)+1.0997*math.log((p+d)/1000))
    full_jh=base_pm*152*118/700
    months=math.exp(math.log(3.67)+.31794*math.log(base_pm))*1.25
    check("independent_effort:"+row["id"],math.isclose(full_jh,row["nominal"]["jh_full"],rel_tol=1e-12))
    check("independent_schedule:"+row["id"],math.isclose(months,row["nominal"]["schedule_full_months"],rel_tol=1e-12))
    check("activities_reconcile:"+row["id"],math.isclose(sum(a["jh"] for a in row["activities"]),full_jh,rel_tol=1e-12))
    check("sensitivity_ordered:"+row["id"],row["declarative_sensitivity"][0]["jh_full"]<full_jh<row["declarative_sensitivity"][2]["jh_full"])
    check("not_flow_budget:"+row["id"],row["budget_admitted"] is False and row["historical_observed_effort"] is None)
# Regression cases target known overcounting risks, independent of source totals.
spec=importlib.util.spec_from_file_location("measure_native",OUT/"measure.py");mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
with tempfile.TemporaryDirectory(prefix="native23-check-") as tmp:
    cases=[
      ("python.py",'"""documentation"""\nx = (\n  1 + 2\n)\n# begin: auto-generated types\ny: int\n# end: auto-generated types\ntry:\n    x += 1\nexcept ValueError, TypeError:\n    pass\n',4,0),
      ("string.js",'const text = "a;b;c";\nfunction f() { return text; }\n',3,0),
      ("Generic.java",'class A<T> { private String text = "a;b"; void f() { int x = 1; if (x > 0) { x++; } } }',6,0),
      ("seed.xml",'<tryton><data><record model="country.country"><field name="code">FR</field></record><record model="ir.ui.view"><field name="model">party.party</field></record></data></tryton>',0,2),
      ("Form.tsx",'export function Form() { return <div><input /></div>; }',2,2)
    ]
    for name,content,program,decl in cases:
        p=Path(tmp)/name;p.write_text(content,encoding="utf-8");v=mod.measure(p)
        check("counter_regression:"+name,v["program_units"]==program and v["declarative_units"]==decl)
check("manual_published_example",abs(2.94*100**1.15-586.61)<.01)
out={"passed":not failures,"check_count":len(checks),"failures":failures,"source_files_verified_against_git":len(m["files"])-sum(f.startswith("git_blob:") for f in failures),"windows_eol_normalization_only":eol_normalized,"active_source_files_unchanged":len(b["files"]),"parser_errors":len(q["errors"]),"functional_evidence_links":len(i["scope"]["families"])*len(i["products"]),"note":"Vérifie source, comptage et arithmétique. Ne valide ni la frontière économique ni la calibration du modèle."}
(OUT/"verification.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({**out,"failures":failures[:20],"failure_count":len(failures)},ensure_ascii=False))
raise SystemExit(0 if out["passed"] else 1)
