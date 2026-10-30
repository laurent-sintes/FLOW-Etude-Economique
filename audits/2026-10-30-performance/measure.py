"""Read-only performance measurements, reproducible on the active checkout."""
from pathlib import Path
import sys,time,json,statistics,cProfile,pstats,hashlib,platform,gzip,urllib.request
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
from validate_stacks import ROOT,read
from study_app import Study
from retained_core import validate
from model_context import model_session
from export_business_model import compose,encode
OUT=Path(__file__).resolve().parent
def summary(values):
    return dict(n=len(values),min_s=min(values),median_s=statistics.median(values),max_s=max(values),samples_s=values)
def timed(fn):
    start=time.perf_counter();value=fn();return time.perf_counter()-start,value
report={'environment':dict(python=sys.version,platform=platform.platform(),conditions='Sequential runs, same machine; warm OS disk cache; no production source changes.')}
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('source','sources','config','tools','app/src') for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in ('.yaml','.json','.py','.tsx','.ts','.css')}
health=json.load(urllib.request.urlopen('http://127.0.0.1:8766/api/health'))
bootstrap=json.load(urllib.request.urlopen('http://127.0.0.1:8766/api/bootstrap?view=essential'))
payload=json.dumps(dict(parameters=bootstrap['baseline']['parameters'],model_version=health['version'])).encode()
http={}
for name,path,body in [('health','/api/health',None),('bootstrap','/api/bootstrap?view=essential',None),('simulate','/api/simulate',payload),('download','/exports/flow-modele-metier.yaml',None)]:
    samples=[];sizes=[];decoded=[];encodings=[]
    for _ in range(10 if name!='download' else 3):
        request=urllib.request.Request('http://127.0.0.1:8766'+path,data=body,headers={'Accept-Encoding':'gzip','Content-Type':'application/json'})
        start=time.perf_counter()
        with urllib.request.urlopen(request) as response:
            raw=response.read();encoding=response.headers.get('Content-Encoding');assert response.status==200
        samples.append(time.perf_counter()-start);sizes.append(len(raw));decoded.append(len(gzip.decompress(raw)) if encoding=='gzip' else len(raw));encodings.append(encoding)
    http[name]={**summary(samples),'transfer_bytes':sizes,'decoded_bytes':decoded,'encodings':encodings}
report['http']=http
print('HTTP',json.dumps({k:round(v['median_s']*1000,1) for k,v in http.items()}),flush=True)
loads=[]
for _ in range(3):
    elapsed,study=timed(Study);loads.append(elapsed);print('Study load',round(elapsed,3),flush=True)
report['study_load']=summary(loads)
sim=[]
for _ in range(20):
    elapsed,result=timed(lambda:study.simulate(study.parameters));sim.append(elapsed)
    assert result==study.baseline
report['simulation_python']=summary(sim)
# Compare exactly the same validation, outside versus inside a bounded snapshot.
validations={}
for name,scoped in [('standalone',False),('one_snapshot',True)]:
    runs=[]
    for _ in range(2):
        def run():
            if scoped:
                with model_session():return validate()
            return validate()
        elapsed,result=timed(run);runs.append(elapsed)
        assert result['units'][0]['total_jh']==1500 and result['units'][0]['months']==17
        print('Validation',name,round(elapsed,3),flush=True)
    validations[name]=summary(runs)
report['retained_validation']=validations
# Attribute load cost; instrumented duration must not be treated as normal latency.
profiler=cProfile.Profile()
start=time.perf_counter();profiler.enable()
with model_session() as snapshot:
    study=Study()
profiler.disable();report['profiled_load_s']=time.perf_counter()-start
profiler.dump_stats(str(OUT/'study-load.prof'))
stats=pstats.Stats(profiler)
with (OUT/'study-profile.txt').open('w',encoding='utf-8') as f:
    stats.stream=f;stats.sort_stats('cumulative').print_stats(35)
report['profile_top']=[dict(file=key[0],line=key[1],function=key[2],primitive_calls=value[0],calls=value[1],self_s=value[2],cumulative_s=value[3]) for key,value in sorted(stats.stats.items(),key=lambda kv:kv[1][3],reverse=True)[:35]]
elapsed,bundle=timed(lambda:compose(snapshot.documents,snapshot.digests));report['export_compose_s']=elapsed
elapsed,raw=timed(lambda:encode(bundle));report['export_encode_s']=elapsed;report['export_bytes']=len(raw)
report['last_full_check']=json.loads((ROOT/'tmp/check-model-last.json').read_text(encoding='utf-8'))
report['original_full_check']=json.loads((ROOT/'audits/2026-10-30-application-cible/verification.json').read_text(encoding='utf-8'))
# Keep only prior timing evidence from the nested audit, not its entire application payload.
def find_check(value):
    if isinstance(value,dict):
        if value.get('mode')=='full' and 'stages' in value:return value
        for x in value.values():
            match=find_check(x)
            if match:return match
    if isinstance(value,list):
        for x in value:
            match=find_check(x)
            if match:return match
report['original_full_check']=find_check(report['original_full_check'])
assert all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest for name,digest in hashes.items())
report['unchanged_active_files']=len(hashes)
(OUT/'python.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('DONE',json.dumps(dict(load=report['study_load'],validation=validations,simulation=report['simulation_python'],export_compose_s=report['export_compose_s'],export_encode_s=report['export_encode_s'],unchanged_files=len(hashes))),flush=True)
