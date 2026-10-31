"""Local synthetic identity broker + real Superset HTTP app for browser embedding trial."""
from pathlib import Path
import json,threading,urllib.parse
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from superset.app import create_app
app=create_app();app.config['GUEST_TOKEN_JWT_EXP_SECONDS']=30
from superset import security_manager
R=Path.cwd();T=R/'tmp/targeted-runtime';ids=json.loads((T/'superset/fixture-ids.json').read_text());counts={'A':0,'B':0}
HTML='''<!doctype html><html lang="fr"><meta charset="utf-8"><title>Essai FLOW · pilotage</title><style>body{font:16px system-ui;margin:25px;background:#f5f7f6;color:#182632}iframe{width:100%;height:800px;border:0}button,select{font:inherit;padding:9px}h1{color:#236159}</style><small>Données fictives · identité simulée · essai d’intégration</small><h1>Historique Temporal analysé avec PM4JS</h1><label>Organisation <select id="org"><option>A</option><option>B</option></select></label><p id="state">Chargement…</p><div id="dashboard"></div><script src="/sdk.js"></script><script>let handle;async function open(){if(handle)handle.unmount();let org=document.getElementById('org').value;handle=await supersetEmbeddedSdk.embedDashboard({id:'EMBED_ID',supersetDomain:'http://127.0.0.1:18988',mountPoint:document.getElementById('dashboard'),fetchGuestToken:async()=>{const r=await fetch('/token',{method:'POST',headers:{'Content-Type':'application/json','X-Trial-User':'lecteur-'+org},body:JSON.stringify({dashboard:'trial-mining'})});if(!r.ok)throw Error('Token refused');return (await r.json()).token;},dashboardUiConfig:{hideTitle:false,hideChartControls:true},iframeTitle:'Tableau de bord des processus',referrerPolicy:'strict-origin-when-cross-origin'});document.getElementById('state').textContent='Organisation '+org+' · tableau de bord intégré';}document.getElementById('org').onchange=open;open();</script></html>'''.replace('EMBED_ID',ids['embedded_uuid'])
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path=='/sdk.js':body=(T/'superset-embedded-sdk/package/bundle/index.js').read_bytes();kind='text/javascript'
  elif self.path=='/counts':body=json.dumps(counts).encode();kind='application/json'
  else:body=HTML.encode();kind='text/html; charset=utf-8'
  self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
 def do_POST(self):
  principal=self.headers.get('X-Trial-User','');body=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}')
  if self.path!='/token' or principal not in ('lecteur-A','lecteur-B') or body!={'dashboard':'trial-mining'}:self.send_error(403);return
  org=principal[-1]
  with app.app_context():token=security_manager.create_guest_access_token(dict(username='trial-browser-'+org),[dict(type='dashboard',id=ids['embedded_uuid'])],[dict(clause="organisation = '"+org+"'")])
  counts[org]+=1;self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(json.dumps(dict(token=token)).encode())
 def log_message(self,*args):pass
threading.Thread(target=ThreadingHTTPServer(('127.0.0.1',18989),Handler).serve_forever,daemon=True).start()
app.run(host='127.0.0.1',port=18988,debug=False,use_reloader=False,threaded=True)
