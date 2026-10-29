"""Close audit08 after reproducibility and visual review; no model mutation."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
def read(n):return json.loads((HERE/n).read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument("--visual-reviewed",action="store_true");args=parser.parse_args()
 if not args.visual_reviewed:raise ValueError("Review desktop, mobile and COCOMO images before closing.")
 tracked=["iteration-08-calculs.json","iteration-08-resultats.json","iteration-08.html"]
 before={n:sha(HERE/n) for n in tracked}
 execution=[]
 for name in ["iteration-08-experiments.py","iteration-08-report.py"]:
  r=subprocess.run([sys.executable,"-B",str(HERE/name)],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace",check=True)
  execution.append({"script":name,"exit_code":r.returncode,"stdout":r.stdout.strip()})
 after={n:sha(HERE/n) for n in tracked}
 if before!=after:raise AssertionError({"non_reproducible":{k:[before[k],after[k]] for k in before if before[k]!=after[k]}})
 result=read("iteration-08-resultats.json");review=read("iteration-08-revue.json");integrity=read("iteration-08-integrite.json")
 for d in [result,review]:
  for p,h in d["input_sha256"].items():
   if sha(HERE/p)!=h:raise AssertionError("Changed dependency: "+p)
 context=read("iteration-08-contexte.json")
 for group in ["source_hashes","additional_source_hashes"]:
  for p,h in context[group].items():
   if sha(ROOT/p)!=h:raise AssertionError("Changed source: "+p)
 browser=read("iteration-08-browser-check.json")
 assert all(c["passed"] for c in browser["checks"])
 assert all(c["passed"] for c in result["checks"])
 assert integrity["all_targeted_integrity_checks_passed"]
 assert not review["material_anomalies"]
 assert result["full_core_jh"] is None and result["full_contract_jh"] is None and result["selected_estimate_jh"] is None
 manifest={
  "id":"iteration-08-verification","date":"2026-10-29","status":"audit_clos_pour_decision_utilisateur",
  "recommendation":result["recommendation"],
  "source_files_checked":len(context["source_hashes"]),"additional_instruction_files_checked":len(context["additional_source_hashes"]),
  "sources_unchanged":True,
  "consolidation_checks":len(result["checks"]),"consolidation_all_passed":True,
  "independent_mathematical_review_ref":"iteration-08-revue.json",
  "independent_integrity_ref":"iteration-08-integrite.json",
  "reproduction":{"identical":True,"before":before,"after":after,"executions":execution},
  "browser":{"checks":browser["checks"],"screenshot_refs":browser["screenshots"],"visual_reviewed_by_assistant":True,"observation":"Desktop, mobile and COCOMO table inspected; readable with contained table scroll on mobile."},
  "limits":["These checks establish reproducibility, arithmetic and inspected input integrity, not predictive accuracy or investment admissibility.","No real FLOW development effort or performance guarantee has been measured.","Existing unrelated Git changes were not reverted. No application test suite was required for audit-only changes."],
  "decision_gate":{"automatic_iteration09":False,"user_decision_pending":True,"external_contacts_or_purchases":False},
  "report_dependency_sha256":{"iteration-07-report.py":sha(HERE/"iteration-07-report.py")},
  "artifacts_sha256":{p.name:sha(p) for p in sorted(HERE.glob("iteration-08*")) if p.is_file() and p.name!="iteration-08-verification.json"}
 }
 (HERE/"iteration-08-verification.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"status":manifest["status"],"artifacts":len(manifest["artifacts_sha256"]),"checks":manifest["consolidation_checks"],"reproducible":True,"sources_unchanged":True}))
if __name__=="__main__":main()
