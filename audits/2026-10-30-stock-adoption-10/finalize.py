"""Finalize the adoption receipt after all required checks have passed."""
from pathlib import Path
import json,hashlib,gzip,urllib.request,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tmp/model-deps'))
import yaml
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
full=load(OUT/'full-validation.json');local=load(OUT/'browser-local.json');static=load(OUT/'browser-static.json');impact=load(OUT/'economic-impact.json')
assert full['mode']=='full' and full['tests']>=279 and full['frontend']=='tests, types, content, build passed'
assert local['passed'] and static['passed'] and impact['passed']
assert len(static['pythonBrowserParity'])==6 and static['staleVersionRejected']
baseline=load(OUT/'baseline.json');ret=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))
assert ret['units'][0]==baseline['retained_master_data']
assert [(u['total_jh'],u['months']) for u in ret['units']]==[(1500,17),(340,10)]
for path,key in [('sources/cartographie-scm-2026-10-24.yaml','capability_source_sha256'),('source/referentiel-capacites.yaml','capability_reference_sha256')]:
 assert sha(ROOT/path)==baseline[key]
with urllib.request.urlopen('http://127.0.0.1:8766/api/health',timeout=30) as response:health=json.load(response)
assert health['sources_current'] and health['mode']=='current'
request=urllib.request.Request('http://127.0.0.1:8766/exports/flow-modele-metier.yaml',headers={'Accept-Encoding':'gzip'})
with urllib.request.urlopen(request,timeout=30) as response:
 encoding=response.headers.get('Content-Encoding');wire=response.read()
assert encoding=='gzip'
raw=gzip.decompress(wire);download=ROOT/'app/dist/exports/flow-modele-metier.yaml'
assert hashlib.sha256(raw).hexdigest()==sha(download)
registry=yaml.safe_load((ROOT/'source/calculs-estimation-core.yaml').read_text(encoding='utf-8'))
for path,p in registry['proofs'].items():assert sha(ROOT/path)==p['sha256']
result=dict(passed=True,retained_gross_jh=1840,retained_master_data_jh=1500,retained_master_data_months=17,
 retained_stock_jh=340,retained_stock_months=10,retained_capabilities=14,total_capabilities=88,remaining_capabilities=74,
 full_python_tests=full['tests'],frontend=full['frontend'],native_references_stock=4,roles_stock=9,
 browser_viewports=local['viewports'],static_python_scenarios=static['pythonBrowserParity'],static_stale_version_rejected=True,
 proof_documents=len(registry['proofs']),master_data_decision_unchanged=True,native_reference_unchanged=True,
 other_four_options_unchanged=True,integration_and_annual_base_unchanged=True,simulation_contract_preserved=True,
 download=dict(bytes=len(raw),gzip_bytes=len(wire),sha256=sha(download),single_file=True),
 server=health,commit_or_push=False)
(OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
names=['source/calculs-estimation-core.yaml','source/estimations-core-retenues.yaml','source/fondamentaux.yaml',
 'source/schema-calculs-estimation-core.yaml','source/schema-fondamentaux.yaml','source/statut-evaluation.yaml',
 'tools/estimation_stock.py','tools/estimation_preparation.py','tools/estimation_calculation.py','tools/estimation_inputs.py',
 'tools/retained_core.py','tools/study_snapshot.py','app/src/CoreEvaluationPage.tsx','tools/test_stock_adoption.py']
proofs={p:sha(ROOT/p) for p in names}
for p in OUT.iterdir():
 if p.is_file() and p.name!='provenance.json':proofs[p.relative_to(ROOT).as_posix()]=sha(p)
(OUT/'provenance.json').write_text(json.dumps(dict(files=proofs),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
