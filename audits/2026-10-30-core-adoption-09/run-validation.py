"""Run the complete existing validation with visible progress and source consistency."""
from pathlib import Path
import contextlib,hashlib,json,sys,time,unittest
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps'),str(ROOT)]
import tools.check_model as checks
class ProgressResult(unittest.TextTestResult):
 def startTest(self,test):
  super().startTest(test)
  if self.testsRun%25==0:
   self.stream.write('\nProgress '+str(self.testsRun)+': '+str(test)+'\n');self.stream.flush()
class ProgressRunner(unittest.TextTestRunner):
 resultclass=ProgressResult
def fingerprints():
 paths=[]
 for folder in ['source','config','tools','app/src','app/scripts']:
  paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in ['.yaml','.yml','.py','.tsx','.ts','.mjs','.css'] and '__pycache__' not in p.parts)
 return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
before=fingerprints();start=time.perf_counter();sys.argv=['check_model','--full'];unittest.TextTestRunner=ProgressRunner
log=ROOT/'tmp/core-adoption-full-final.log'
with log.open('w',encoding='utf-8',buffering=1) as stream,contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
 result=checks.main()
after=fingerprints();changed=[p for p in set(before)|set(after) if before.get(p)!=after.get(p)]
report=dict(exit_code=result,elapsed_seconds=round(time.perf_counter()-start,3),source_changes_during_validation=changed)
(OUT/'validation-run.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report));print(log.read_text(encoding='utf-8')[-5000:])
raise SystemExit(result or bool(changed))
