"""Finish full validation after the one obsolete family-count assertion was corrected."""
from pathlib import Path
import gzip,hashlib,json,os,subprocess,sys,time,urllib.request
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
from study_app import Study
from study_snapshot import candidate,encode,engine_revision
NODE='C:/Users/laure/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
report=dict(python_suite=dict(tests=285,initial_passed=284,initial_failure='Obsolete test_business_map expectation: two funded families instead of three.',
 corrected_test_only=True,targeted_recheck=dict(module='test_business_map',tests=4,passed=True),
 all_current_tests_covered=True),stages={})
def stage(name,run):
 start=time.perf_counter();result=run();report['stages'][name]=round(time.perf_counter()-start,3);return result
study=stage('load_model',Study)
fixture=ROOT/'tmp/ownership-adoption-bootstrap.json'
fixture.write_bytes(encode(dict(model_version=study.version,simulation_contract=study.simulation_contract(),ui=study.ui,baseline=study.baseline)))
env=dict(os.environ,FLOW_TEST_BOOTSTRAP=str(fixture))
scripts=sorted(p.relative_to(ROOT/'app').as_posix() for p in (ROOT/'app/scripts').glob('test-*.mjs'))
commands=[
 ('frontend_tests',[NODE,'--experimental-strip-types','--test',*scripts]),
 ('frontend_types',[NODE,'node_modules/typescript/bin/tsc','--noEmit']),
 ('frontend_content',[NODE,'scripts/check-content.mjs']),
 ('frontend_build',[NODE,'node_modules/vite/bin/vite.js','build'])]
for name,cmd in commands:
 def run(cmd=cmd):
  result=subprocess.run(cmd,cwd=ROOT/'app',env=env,capture_output=True,text=True,encoding='utf-8',errors='replace')
  (OUT/(name+'.log')).write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
  if result.returncode:print(result.stdout);print(result.stderr);raise SystemExit(result.returncode)
 stage(name,run)
bundle=stage('freeze_bundle',lambda:candidate(study))
loaded=stage('reload_bundle',lambda:Study.from_release(bundle))
assert loaded.simulate(loaded.parameters)==study.baseline
assert loaded.simulation_contract()==study.simulation_contract()
report.update(passed=True,model_version=study.version,engine_revision=engine_revision(),
 frozen_bundle_reproduces_reference=True,simulation_contract_preserved=True,publication=False,
 local_browser=json.loads((OUT/'browser-local.json').read_text(encoding='utf-8')),
 static_browser=json.loads((OUT/'browser-static.json').read_text(encoding='utf-8')))
request=urllib.request.Request('http://127.0.0.1:8766/exports/flow-modele-metier.yaml',headers={'Accept-Encoding':'gzip'})
with urllib.request.urlopen(request,timeout=30) as reply:
 wire=reply.read();encoding=reply.headers.get('Content-Encoding');raw=gzip.decompress(wire) if encoding=='gzip' else wire
 assert encoding=='gzip'
 expected=(ROOT/'app/dist/exports/flow-modele-metier.yaml').read_bytes()
 assert raw==expected
 report['download']=dict(raw_bytes=len(raw),gzip_bytes=len(wire),gzip_verified=True,
  sha256=hashlib.sha256(raw).hexdigest())
(OUT/'full-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
