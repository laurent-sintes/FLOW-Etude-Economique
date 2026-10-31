"""Record the final adopted state and completed validations, without changing the model."""
from pathlib import Path
from collections import Counter
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tmp/model-deps'))
import yaml
def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
run=read('validation-run.json')
assert run['exit_code']==0,run
if run['source_changes_during_validation']:
 post=read('post-validation.json')
 assert post['passed'] and post['source_stable'] and run['source_changes_during_validation']==[post['path']]
 assert sha(ROOT/post['path'])==post['sha256']
log=(ROOT/'tmp/core-adoption-full-final.log').read_text(encoding='utf-8')
start=log.rfind('{\n  "mode"')
assert start>=0,'Missing complete validation report'
full=json.JSONDecoder().raw_decode(log[start:])[0]
assert full['mode']=='full' and full['tests']>=290 and full['frontend']
(OUT/'full-validation.json').write_text(json.dumps(full,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
local=read('browser-local.json');static=read('browser-static.json');impact=read('economic-impact.json')
assert local['passed'] and static['passed'] and impact['passed']
assert len(static['pythonBrowserParity'])==6
units=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))['units']
assert len(units)==9 and sum(u['total_jh'] for u in units)==4160
roles=Counter()
for u in units:roles.update({r['id']:r['jh'] for r in u['roles']})
report=dict(status='adopted_and_verified',total_jh=4160,capabilities=88,units=9,previous_three_decisions_preserved=True,
 build_eur_ht=impact['build_eur_ht'],other_four_options_and_all_horizons_preserved=True,integration_annual_and_global_calendar_preserved=True,
 simulation_contract_preserved=True,local_delays_not_summed=True,python_tests=full['tests'],frontend=full['frontend'],validation_source_changes=run['source_changes_during_validation'],changed_test_module_replayed=bool(run['source_changes_during_validation']),
 browser_local=local,browser_static=static,global_roles=dict(roles),no_publish_or_git_push=True,server='http://127.0.0.1:8766')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'bilan.yaml').write_text(yaml.safe_dump(dict(summary=report,units=[dict(id=u['id'],label=u['label'],jh=u['total_jh'],months=u['months'],roles=u['roles'],hypotheses=u['assumptions']) for u in units]),allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
files={p.relative_to(ROOT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='provenance.json' and '__pycache__' not in p.parts}
for p in ['source/estimations-core-retenues.yaml','source/calculs-estimation-core.yaml','source/referentiel-capacites.yaml','source/analyse-perimetre-core.yaml','source/fondamentaux.yaml','source/statut-evaluation.yaml','tools/estimation_components.py','tools/estimation_inputs.py','tools/estimation_calculation.py','tools/retained_core.py','tools/study_app.py','app/src/CoreEvaluationPage.tsx']:
 files[p]=sha(ROOT/p)
(OUT/'provenance.json').write_text(json.dumps(dict(files=files,skill_sha256=sha(Path('C:/Users/laure/.codex/skills/flow-evaluer-core-system/SKILL.md'))),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=report['status'],JH=4160,coverage='88/88',python_tests=full['tests'],build_eur_ht=report['build_eur_ht']),ensure_ascii=False))
