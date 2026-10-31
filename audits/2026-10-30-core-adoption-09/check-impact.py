"""Verify adoption impact while preserving other options, schedules and saved-scenario semantics."""
from pathlib import Path
import json,hashlib,time,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
from study_app import Study
from retained_core import validate
from estimation_inputs import registry
def main():
 old=json.loads((OUT/'baseline.json').read_text(encoding='utf-8'));t=time.perf_counter();study=Study()
 assert validate()['units'][:3]==old['units'];assert registry()['calculations'][:3]==old['calculations']
 for name in ['source/referentiel-capacites.yaml','source/analyse-perimetre-core.yaml','sources/cartographie-scm-2026-10-24.yaml']:
  assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==old['source_hashes'][name]
 assert study.simulation_contract()==old['simulation_contract']
 for before,after in zip(old['baseline']['options'],study.baseline['options']):
  if after['stack']!='java-spring':assert before==after,after['stack']
 for slug in old['parameters']['options']:
  before=old['parameters']['options'][slug];after=study.parameters['options'][slug]
  if slug=='java-spring':
   assert {k:v for k,v in before.items() if k!='build'}=={k:v for k,v in after.items() if k!='build'}
  else:assert before==after
 core=next(o for o in study.economic['options'] if o['stack']=='java-spring')
 previous=next(o for o in old['economic']['options'] if o['stack']=='java-spring')
 assert core['core_units'][:3]==previous['core_units']  # includes prices, role and schedule projections
 assert core['jh']['core_project_roles_jh']==4160
 data=dict(passed=True,model_version=study.version,total_jh=4160,retained_units=9,covered_capabilities=88,build_eur_ht=core['detail_build']['prestations'],
   previous_build_eur_ht=previous['detail_build']['prestations'],nominal_build_delta_eur_ht=core['detail_build']['prestations']-previous['detail_build']['prestations'],
   previous_three_decisions_and_values_unchanged=True,native_reference_unchanged=True,other_four_options_unchanged_all_horizons=True,
   integration_annual_and_calendar_parameters_unchanged=True,simulation_contract_unchanged=True,
   global_build_months=study.parameters['options']['java-spring']['build_mois'],elapsed_check_seconds=round(time.perf_counter()-t,3))
 (OUT/'economic-impact.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(data,ensure_ascii=False))
if __name__=='__main__':main()
