from pathlib import Path
import sys,time,statistics,json,subprocess,gzip,urllib.request,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
from study_app import Study
from model_context import model_session
from retained_core import validate
from export_business_model import export,compose,encode,write_if_changed,DEFAULT_OUTPUT
out=Path(__file__).resolve().parent
def sample(fn,n):
    values=[]
    for _ in range(n):
        t=time.perf_counter();fn();values.append(time.perf_counter()-t)
    return dict(samples_s=values,median_s=statistics.median(values),min_s=min(values),max_s=max(values),n=n)
report={}
report['study_load']=sample(Study,3)
report['retained_validation']=sample(validate,3)
def old_export():
    with model_session() as snapshot:
        Study();raw=encode(compose(snapshot.documents,snapshot.digests))
    assert raw==DEFAULT_OUTPUT.read_bytes()
    write_if_changed(DEFAULT_OUTPUT,raw)
report['uncached_export_path']=sample(old_export,1)
report['cached_export']=sample(lambda:export(),5)
def cli():
    r=subprocess.run([sys.executable,'-B','-m','tools.export_business_model'],capture_output=True,text=True,check=True)
    assert json.loads(r.stdout)['cache_hit']
report['cached_export_cli']=sample(cli,5)
health=json.load(urllib.request.urlopen('http://127.0.0.1:8766/api/health'))
with urllib.request.urlopen('http://127.0.0.1:8766/api/bootstrap?view=essential') as response:data=json.load(response)
body=json.dumps(dict(parameters=data['baseline']['parameters'],model_version=health['version'])).encode()
report['http']={}
for name,path,payload in [('bootstrap','/api/bootstrap?view=essential',None),('simulate','/api/simulate',body),('download','/exports/flow-modele-metier.yaml',None)]:
    sizes=[];encodings=[];samples=[];types=[]
    for _ in range(10 if name!='download' else 3):
        t=time.perf_counter()
        with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8766'+path,data=payload,headers={'Accept-Encoding':'gzip','Content-Type':'application/json'})) as response:
            raw=response.read();encodings.append(response.headers.get('Content-Encoding'));types.append(response.headers.get('Content-Type'));sizes.append(len(raw))
        samples.append(time.perf_counter()-t)
        if name=='download':
            assert gzip.decompress(raw)==DEFAULT_OUTPUT.read_bytes()
    report['http'][name]=dict(samples_s=samples,median_s=statistics.median(samples),transfer_bytes=sizes,encodings=encodings,content_types=types)
with model_session():
    unit=validate()['units'][0];assert (unit['total_jh'],unit['months'])==(1500,17)
report['full_check']=json.loads(Path('tmp/check-model-last.json').read_text(encoding='utf-8'))
report['health']=health
(out/'after.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('full_check','health')},ensure_ascii=False,indent=2))
