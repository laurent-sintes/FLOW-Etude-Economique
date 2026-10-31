"""Run the unchanged complete check with test names, then retain its report."""
from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
from tools import check_model
original=unittest.TextTestRunner
class DetailedRunner(original):
 def __init__(self,*args,**kwargs):
  kwargs['verbosity']=2
  super().__init__(*args,**kwargs)
unittest.TextTestRunner=DetailedRunner
sys.argv=[sys.argv[0],'--full']
status=check_model.main()
if status==0:
 report=json.loads((ROOT/'tmp/check-model-last.json').read_text(encoding='utf-8'))
 (Path(__file__).parent/'full-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raise SystemExit(status)
