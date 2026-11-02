"""Compare old/new loading in one process, ABBA order, isolated model sessions."""
from pathlib import Path
import sys,time,json,gc,statistics
from contextlib import ExitStack
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
import yaml
from validate_stacks import UniqueKeyLoader
from capability_catalog import native
from study_app import Study
OUT=Path(__file__).resolve().parent
reference=json.loads((OUT/'profile-before.json').read_text(encoding='utf-8'))
rows=[]
for mode in ('before','after','after','before'):
 gc.collect()
 with ExitStack() as stack:
  if mode=='before':
   stack.enter_context(patch('validate_stacks.load_json',side_effect=lambda text:yaml.load(text,Loader=UniqueKeyLoader)))
   stack.enter_context(patch('estimation_inputs.native_kinds',side_effect=lambda:{n['id']:n['kind'] for n in native()['nodes']}))
  start=time.perf_counter();study=Study();seconds=time.perf_counter()-start
  assert study.parameters==reference['parameters']
  assert {k:v for k,v in study.baseline.items() if k!='model_version'}=={k:v for k,v in reference['baseline'].items() if k!='model_version'}
 rows.append(dict(mode=mode,seconds=seconds));del study
 print(json.dumps(rows[-1]),flush=True)
medians={mode:statistics.median(r['seconds'] for r in rows if r['mode']==mode) for mode in ('before','after')}
result=dict(measurements=rows,median_seconds=medians,reduction_pct=100*(1-medians['after']/medians['before']),economy_unchanged=True,method='ABBA, same process and data, two fresh Study loads per implementation. Old JSON parser and full native projection restored only through process-local patches. No profiling overhead.',limits='Local workstation measurements, two runs per implementation. Not a CI threshold or a browser benchmark.')
(OUT/'benchmark.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result),flush=True)
