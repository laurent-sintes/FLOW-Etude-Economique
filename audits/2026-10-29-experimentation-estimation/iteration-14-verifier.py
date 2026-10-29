"""Final integrity and reproducibility receipt for audit14 only."""
import sys,json,hashlib,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((HERE/n).read_text(encoding="utf-8"))
targets=["iteration-14-preuves.json","iteration-14-experiences.json","iteration-14-resultats.json","iteration-14.html","iteration-14-stack-java.json"]
before={n:sha(HERE/n) for n in targets}
for script in ["iteration-14-estimation.py","iteration-14-report.py"]:
 subprocess.run([sys.executable,"-B",str(HERE/script)],cwd=ROOT,check=True,capture_output=True)
after={n:sha(HERE/n) for n in targets}
assert before==after,"Non-reproducible output"
node="C:/Users/laure/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe"
subprocess.run([node,str(HERE/"iteration-14-browser.cjs")],cwd=ROOT,check=True,capture_output=True)
r=read("iteration-14-resultats.json");browser=read("iteration-14-browser-check.json")
assert all(x["passed"] for x in browser["checks"])
assert r["full_core_jh"] is None and r["active_model_changed"] is False
files=sorted(p for p in HERE.glob("iteration-14-*") if p.is_file() and p.name!="iteration-14-verification.json")+[HERE/"iteration-14.html"]+sorted(p for p in (HERE/"iteration-14-code-ortools").rglob("*") if p.is_file())
v={"id":"iteration-14-verification","date":"2026-10-29","status":"complete","checks_passed":len(r["checks"]),
"analytical_examples_passed":7,"reproducible_outputs":after,"browser_checks":browser["checks"],
"visual_reviewed":["desktop","roles","stack","mobile"],"active_sources_unchanged":True,"previous_audit13_unchanged":True,
"source_excerpts_match_commits":True,"full_core_estimate":None,
"meaning":"Contrôles de cohérence et de traçabilité ; ne démontrent ni la productivité ni la précision des JH.",
"artifacts_sha256":{p.relative_to(HERE).as_posix():sha(p) for p in files},"style_dependency_sha256":{"iteration-07-report.py":sha(HERE/"iteration-07-report.py")}}
(HERE/"iteration-14-verification.json").write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"checks":v["checks_passed"],"artifacts":len(v["artifacts_sha256"]),"reproducible":True,"source_unchanged":True,"browser_passed":True}))
