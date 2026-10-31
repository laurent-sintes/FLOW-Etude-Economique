from pathlib import Path
import json,sys
from copy import deepcopy
R=Path.cwd();O=R/'audits/2026-10-30-audit-fonctions-transverses';sys.path[:0]=[str(R/'tools'),str(R/'tmp/model-deps')]
from study_app import Study
from core_product_estimate import calculate,load_inputs
from model_context import model_session
from estimation_calculation import formula
s=Study();d=load_inputs()[1];r=s.content['core_product_scope']['proposal'];u=next(o['core_units'] for o in s.economic['options'] if o['stack']=='java-spring');md=json.loads((R/'audits/2026-10-30-master-data-comparable-reuse/measurements.json').read_text(encoding='utf-8'));idx={(x['repo'],x['path']):x for x in md['files']}
steps=[]
with model_session():
 for stage in (1,2,3):
  test=deepcopy(d)
  if stage!=3:test['measurements']=json.loads((O/f'components-iteration-{stage}.json').read_text(encoding='utf-8'))
  for f in test['measurements']['files']:
   old=idx.get((f['repo'],f['path']));f['existing_MD_credit_units']=0 if not old else min(f['program_units']+f['declarative_units'],old['program_units']+old['declarative_units'])*(.035 if old['treatment']=='reused' else 1)
  result=calculate(test,u);steps.append(dict(iteration=stage,files=len(test['measurements']['files']),total_jh=result['total_jh'],process_jh=result['rows'][0]['jh'],it_jh=result['rows'][2]['jh'],workbench_jh=result['rows'][1]['jh']))
 primary=next(x for x in r['comparative_rows'] if x['id']=='axelor');c=d['cocomo'];E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum']);other_sizes=sum(row['new_units'] for unit in d['code_audit']['units'] if unit['id']!='processes' for row in unit['rows'] if row['id']=='axelor');size=other_sizes+primary['process_size']+primary['it_size']+primary['workbench_size'];jh=formula('cocomo_effort',A=c['A'],KSLOC=size/1000,E=E,EM=c['other_EM'],SCED=c['SCED'],month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor']);grouping=dict(equivalent_logical_units=size,single_project_jh=jh,sum_of_economic_units_jh=r['total_jh'],gap_jh=jh-r['total_jh'],gap_pct=100*(jh/r['total_jh']-1),note='Sensibilité de regroupement : un seul projet supposé homogène contre lots cohérents. Ne prouve ni nouveaux travaux ni leur calendrier ; aucune provision automatique ajoutée.')
(O/'iteration-history.json').write_text(json.dumps(dict(steps=steps,grouping_sensitivity=grouping),ensure_ascii=False,indent=2),encoding='utf-8');(O/'proposal-results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(steps);print(grouping);print(r['comparative_rows'])
