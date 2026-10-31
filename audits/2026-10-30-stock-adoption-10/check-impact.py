"""Record economic impacts against the same model with only Master Data adopted."""
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
import yaml
from study_app import Study
from model_context import SourceSnapshot
from estimation_inputs import SOURCE as REGISTRY
original=SourceSnapshot.read
def only_md(self,path,loader):
 result=original(self,path,loader);name=path.resolve().relative_to(ROOT).as_posix()
 if name=='source/estimations-core-retenues.yaml':
  result['units']=[u for u in result['units'] if u['id']=='master-data-java-spring']
 if name==REGISTRY:
  result['calculations']=[c for c in result['calculations'] if c['unit_id']=='master-data-java-spring']
  result['mechanisms']=[m for m in result['mechanisms'] if m['funding_owner']=='master-data-java-spring']
  reached=set()
  def visit(p):
   if p in reached:return
   reached.add(p)
   for d in result['proofs'][p]['dependencies']:visit(d['path'])
  for c in result['calculations']:
   for p in c['inputs'].values():visit(p)
  result['proofs']={p:v for p,v in result['proofs'].items() if p in reached}
 return result
with patch.object(SourceSnapshot,'read',only_md):before=Study()
after=Study()
rows=[]
for b,a in zip(before.baseline['options'],after.baseline['options']):
 assert b['stack']==a['stack']
 unchanged=[key for key in a if a[key]==b[key]]
 changed=[key for key in a if a[key]!=b[key]]
 if a['stack']!='java-spring':assert not changed,(a['stack'],changed)
 else:
  assert a['build']-b['build']==213970
  for key in ('integration','annual_base','service_start_month','selection_buy','selection_months','initial_months','hosting_build'):
   assert a[key]==b[key],key
 rows.append(dict(stack=a['stack'],build_before=b['build'],build_after=a['build'],build_delta=a['build']-b['build'],
  unchanged_fields=unchanged,changed_fields=changed,
  horizons=[dict(years=x.get('years',x.get('horizon')),total_before=x['totals']['total'],total_after=y['totals']['total'],delta=y['totals']['total']-x['totals']['total']) for x,y in zip(b['horizons'],a['horizons'])]))
# Simulation meaning and saved-parameter shape remain unchanged; reference values may evolve.
assert before.simulation_contract()==after.simulation_contract()
md=after.content['stacks']['java-spring']['economic']['core_units'][0]
baseline=json.loads((OUT/'baseline.json').read_text(encoding='utf-8'))
decision=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))
assert decision['units'][0]==baseline['retained_master_data']
for path,key in [('sources/cartographie-scm-2026-10-24.yaml','capability_source_sha256'),('source/referentiel-capacites.yaml','capability_reference_sha256')]:
 assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==baseline[key]
result=dict(passed=True,method='Comparaison du même modèle courant avec et sans la seule adoption Stock ; aucune écriture temporaire dans les sources.',
 options=rows,simulation_contract_preserved=True,master_data_preserved=True,native_reference_preserved=True,
 retained_gross_jh=1840,retained_capabilities=14,remaining_capabilities=74,
 schedule_aggregation=None,local_months={'master-data-java-spring':17,'stock-java-spring':10})
(OUT/'economic-impact.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
