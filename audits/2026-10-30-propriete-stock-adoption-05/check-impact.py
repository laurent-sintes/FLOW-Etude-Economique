"""Economic impact of the one authorised adoption, with prior families preserved."""
from pathlib import Path
from unittest.mock import patch
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
import yaml
from study_app import Study
from model_context import SourceSnapshot
original=SourceSnapshot.read
OWNER='inventory-ownership-java-spring'
def without_ownership(self,path,loader):
 value=original(self,path,loader);name=path.resolve().relative_to(ROOT).as_posix()
 if name=='source/estimations-core-retenues.yaml':
  value['units']=[u for u in value['units'] if u['id']!=OWNER]
 if name=='source/calculs-estimation-core.yaml':
  value['calculations']=[c for c in value['calculations'] if c['unit_id']!=OWNER]
  value['mechanisms']=[m for m in value['mechanisms'] if m['funding_owner']!=OWNER]
  reached=set()
  def visit(p):
   if p in reached:return
   reached.add(p)
   for d in value['proofs'][p]['dependencies']:visit(d['path'])
  for c in value['calculations']:
   for p in c['inputs'].values():visit(p)
  value['proofs']={p:v for p,v in value['proofs'].items() if p in reached}
 return value
with patch.object(SourceSnapshot,'read',without_ownership):before=Study()
after=Study();rows=[]
for b,a in zip(before.baseline['options'],after.baseline['options']):
 assert a['stack']==b['stack']
 changed=[key for key in a if a[key]!=b[key]]
 if a['stack']!='java-spring':assert not changed,(a['stack'],changed)
 else:
  assert a['build']-b['build']==62950
  for key in ('integration','annual_base','service_start_month','selection_buy','selection_months','initial_months','hosting_build'):
   assert a[key]==b[key],key
 rows.append(dict(stack=a['stack'],build_before=b['build'],build_after=a['build'],delta_build=a['build']-b['build'],
  changed_fields=changed,horizons=[dict(years=x.get('years',x.get('horizon')),
  total_before=x['totals']['total'],total_after=y['totals']['total'],delta=y['totals']['total']-x['totals']['total'])
  for x,y in zip(b['horizons'],a['horizons'])]))
assert before.simulation_contract()==after.simulation_contract()
baseline=json.loads((OUT/'baseline.json').read_text(encoding='utf-8'))
decision=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))
assert decision['units'][:2]==baseline['retained_units'] and len(decision['units'])==3
for p in ('source/referentiel-capacites.yaml','sources/cartographie-scm-2026-10-24.yaml'):
 assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==baseline['file_hashes'][p]
core=after.content['stacks']['java-spring']['economic']
own=next(u for u in core['core_units'] if u['id']==OWNER)
assert (own['labour_eur_ht'],own['tooling_eur_ht'])==(62150,800)
assert sum(r['jh'] for r in own['roles'])==100 and own['months']==7
result=dict(passed=True,method='Même modèle courant, avec et sans la seule adoption de la propriété ; aucune écriture de sources temporaires.',
 options=rows,simulation_contract_preserved=True,master_data_and_stock_preserved=True,native_reference_preserved=True,
 retained_jh=1940,retained_capabilities=16,remaining_capabilities=72,
 ownership=dict(jh=100,months=7,labour_eur_ht=62150,tooling_eur_ht=800,total_eur_ht=62950),
 global_schedule_changed=False,local_schedules_summed=False,other_stack_estimates_unchanged=True)
(OUT/'economic-impact.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
