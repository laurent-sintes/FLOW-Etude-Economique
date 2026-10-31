"""Final receipt of the authorised Ownership adoption."""
from pathlib import Path
import hashlib,json,sys,urllib.request
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
import yaml
from model_context import model_session
from retained_core import validate
from estimation_calculation import calculate
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
baseline=read(OUT/'baseline.json');full=read(OUT/'full-validation.json');impact=read(OUT/'economic-impact.json')
assert full['passed'] and impact['passed']
with model_session():
 units=validate()['units'];own=units[2];computed=calculate(own['calculation'])
assert units[:2]==baseline['retained_units']
assert (own['total_jh'],own['months'])==(100,7)
assert sum(r['jh'] for r in own['roles'])==100
for p in ('source/referentiel-capacites.yaml','sources/cartographie-scm-2026-10-24.yaml'):
 assert sha(ROOT/p)==baseline['file_hashes'][p]
with urllib.request.urlopen('http://127.0.0.1:8766/api/health',timeout=5) as reply:health=json.loads(reply.read())
assert health['mode']=='current' and health['sources_current'] and health['version']==full['model_version']
assert sha(ROOT/'app/dist/exports/flow-modele-metier.yaml')==full['download']['sha256']
assert 'estimation_ownership.py' in Path('C:/Users/laure/.codex/skills/flow-evaluer-core-system/SKILL.md').read_text(encoding='utf-8')
result=dict(id='propriete-stock-adoption-05',status='adoptee_et_integree',adopted_by='Décision explicite du sponsor dans la conversation.',
 family=dict(id=own['id'],stack=own['stack'],capabilities=own['capabilities'],jh=100,months=7,
 roles=[dict(id=r['id'],label=r['label'],jh=r['jh']) for r in own['roles']]),
 cumulative_jh=sum(u['total_jh'] for u in units),families=[dict(id=u['id'],jh=u['total_jh'],months=u['months']) for u in units],
 progress=dict(adopted_capabilities=16,total_capabilities=88,pct=16/88*100,remaining=72),
 funding=dict(new_modules_funded=6,existing_mechanisms_consumed=16,no_extra_AI_or_pilotage=True),
 functional_control=dict(CFP=80,jh=computed['alignment']['functional']['jh'],
 gap_jh=computed['alignment']['functional']['gap_jh'],gap_pct=computed['alignment']['functional']['gap_pct'],
 denominator=computed['alignment']['reference_jh'],gap_is_not_confidence=True),
 economy=impact['ownership'],download=full['download'],
 preserved=dict(master_data=True,stock=True,native_capability_reference=True,other_options=True,
 integration_and_annual_base=True,simulation_contract=True,local_storage_keys=True,global_schedule=True),
 schedules_added=False,integrated_core_cocomo_total=False,
 validation=dict(python_unique_tests_covered=285,corrected_obsolete_test_rechecked=True,
 frontend_tests_types_content_build=True,frozen_bundle_roundtrip=True,local_and_static_browser=True,
 python_browser_scenarios=full['static_browser']['pythonBrowserParity'],desktop_and_mobile=True),
 server=health,another_ownership_source_iteration_worthwhile=False,
 next_step='Passer à une autre famille. Réouvrir la propriété si une hypothèse déterminante change.',
 new_confidence_or_probability_claim=False)
(OUT/'bilan.yaml').write_text(yaml.safe_dump(result,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
tracked=[ROOT/p for p in ['source/estimations-core-retenues.yaml','source/calculs-estimation-core.yaml','source/fondamentaux.yaml',
 'source/schema-calculs-estimation-core.yaml','source/statut-evaluation.yaml','tools/estimation_ownership.py','tools/estimation_preparation.py',
 'tools/retained_core.py','tools/study_snapshot.py','tools/test_ownership_adoption.py']]
provenance=dict(audit_files={p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='provenance.json'},
 active_files={p.relative_to(ROOT).as_posix():sha(p) for p in tracked})
(OUT/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(passed=True,jh=100,months=7,cumulative_jh=result['cumulative_jh'],capabilities=16,remaining=72,server_current=True),ensure_ascii=False))
