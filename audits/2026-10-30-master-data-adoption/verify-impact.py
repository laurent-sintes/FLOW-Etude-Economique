from pathlib import Path
import sys,json
sys.path[:0]=['tmp/model-deps','tools']
from study_app import Study
root=Path('audits/2026-10-30-master-data-adoption')
before=json.loads((root/'baseline.json').read_text(encoding='utf-8'))
s=Study()
assert s.simulation_contract()==before['contract'],'Simulation parameter meaning changed'
checks=[]
for old,new in zip(before['baseline']['options'],s.baseline['options']):
 assert old['stack']==new['stack']
 slug=new['stack']
 for key in ('integration','annual_base','services','editor_prices','service_start_month','initial_months','hosting_build'):
  assert old[key]==new[key],(slug,key)
 if slug!='java-spring':assert old==new,(slug,'unexpected economic change')
 else:
  assert new['build']-old['build']==944000
  for old_h,new_h in zip(old['horizons'],new['horizons']):
   for key in ('integration','mco_run'):
    assert old_h['totals'][key]==new_h['totals'][key],(slug,new_h['years'],key)
 checks.append(dict(stack=slug,build_delta=new['build']-old['build'],
  integration_delta=new['integration']-old['integration'],global_months=new['initial_months'],
  horizons=[dict(years=h['years'],total_delta=round(h['totals']['total']-o['totals']['total'],2)) for o,h in zip(old['horizons'],new['horizons'])]))
result=dict(status='passed',scope='Master Data Java/Spring only',simulation_contract_preserved=True,options=checks,
 retained=s._essential_core_evaluation()[0],
 funding_rule='Project roles funded once at family level; no additional IA discount or proportional coordination.',
 limitations='Retained estimate, not statistically calibrated. Remaining 82 Java capacities and all .NET/Rust capabilities unestimated.')
(root/'impact-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
print(json.dumps(checks,ensure_ascii=True))
