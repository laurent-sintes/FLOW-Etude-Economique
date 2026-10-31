from pathlib import Path
import gzip,hashlib,json,time,urllib.request
R=Path.cwd();O=R/'audits/2026-10-30-audit-fonctions-transverses';base='http://127.0.0.1:8766'
def get(path,packed=False):
 start=time.perf_counter();req=urllib.request.Request(base+path,headers={'Accept-Encoding':'gzip'} if packed else {})
 with urllib.request.urlopen(req,timeout=40) as r:raw=r.read();headers=dict(r.headers);status=r.status
 plain=gzip.decompress(raw) if headers.get('Content-Encoding')=='gzip' else raw
 return plain,dict(status=status,seconds=round(time.perf_counter()-start,4),transferred_bytes=len(raw),uncompressed_bytes=len(plain),content_encoding=headers.get('Content-Encoding'),content_type=headers.get('Content-Type'))
raw,h=get('/api/health');health=json.loads(raw);assert health['id']=='flow-study' and health['sources_current'] and health['mode']=='current';assert health['client_build_sha256']==hashlib.sha256((R/'app/dist/index.html').read_bytes()).hexdigest()
raw,b=get('/api/bootstrap?view=essential',True);data=json.loads(raw);p=data['content']['core_product_scope']['proposal'];assert p['total_jh']==6660 and p['eur_ht']==4198680;java=next(x for x in data['baseline']['options'] if x['stack']=='java-spring');assert java['build']==2620030
horizon=next(x for x in java['horizons'] if x['years']==10);assert horizon['totals']==dict(build=2620030.,integration=2677372.95,mco_run=5193331.2,total=10490734.15)
raw,download=get('/exports/flow-modele-metier.yaml',True);expected=(R/'app/dist/exports/flow-modele-metier.yaml').read_bytes();assert raw==expected;assert download['content_encoding']=='gzip'
_,cached=get('/exports/flow-modele-metier.yaml',True)
body=json.dumps(dict(parameters=data['baseline']['parameters'],model_version=data['model_version'])).encode();start=time.perf_counter()
with urllib.request.urlopen(urllib.request.Request(base+'/api/simulate',data=body,headers={'Content-Type':'application/json'}),timeout=40) as r:sim=json.load(r)
assert sim==data['baseline'];simulate_seconds=round(time.perf_counter()-start,4)
record=dict(status='passed',url=base,health=health,bootstrap=b,download=download,cached_download=cached,download_sha256=hashlib.sha256(expected).hexdigest(),proposal_jh=p['total_jh'],proposal_eur_ht=p['eur_ht'],adopted_jh=p['adopted_jh'],adopted_build_eur_ht=java['build'],ten_years=horizon['totals'],reference_simulation_preserved=True,simulate_seconds=simulate_seconds)
(O/'local-http-verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(record,ensure_ascii=False,indent=2))
