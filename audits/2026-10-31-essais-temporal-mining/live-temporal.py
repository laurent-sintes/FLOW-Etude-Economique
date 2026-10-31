"""Live SDK/Temporal server trial. Principals and business effects are synthetic fixtures."""
from pathlib import Path
import json,time,urllib.request,urllib.error
R=Path.cwd();O=R/'audits/2026-10-31-essais-temporal-mining/results';O.mkdir(exist_ok=True);URL='http://127.0.0.1:18980';checks=[];run='t'+str(int(time.time()))
def call(path,body=None,user='designer-A'):
 req=urllib.request.Request(URL+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json','X-Trial-User':user})
 try:
  with urllib.request.urlopen(req,timeout=20) as r:return r.status,json.load(r)
 except urllib.error.HTTPError as e:return e.code,json.load(e)
def check(id,ok,detail=None):
 checks.append(dict(id=id,passed=bool(ok),detail=detail));assert ok,(id,detail)
def state(id,expected='WAITING',user='designer-A'):
 end=time.monotonic()+25;last=None
 while time.monotonic()<end:
  status,last=call('/cases?caseId='+id,user=user)
  if status==200 and last.get('state')==expected:return last
  time.sleep(.05)
 raise AssertionError((id,expected,last))
def start(id,v,mode='none',user='designer-A'):
 status,d=call('/cases',dict(caseId=id,version=v,failureMode=mode),user);check('start-'+id,status==202,d);return state(id,user=user)
def approve(id,event='accept',approved=True,user='gestionnaire-A'):
 return call('/outcomes',dict(caseId=id,eventId=event,approved=approved),user)
def history(id,user='designer-A'):
 status,d=call('/history?caseId='+id,user=user);assert status==200;return d
status,models=call('/models');latest=max([m['version'] for m in models],default=0)
status,v1=call('/models',dict(name='Parcours atelier '+run,expectedVersion=latest,express=False));check('publish-v1',status==201,v1['version']);v1=v1['version']
status,_=call('/models',dict(name='obsolete',expectedVersion=latest));check('optimistic-publication-rejects-stale-version',status==409)
status,_=call('/models',dict(name='unauthorised',expectedVersion=v1),user='lecteur-A');check('reader-cannot-publish',status==403)
old=run+'-old';start(old,v1)
status,v2=call('/models',dict(name='Parcours métier modifié '+run,expectedVersion=v1,express=True,control=True));check('publish-v2-with-new-control',status==201,v2['version']);v2=v2['version']
fresh=run+'-new';start(fresh,v2)
status,_=approve(old,user='lecteur-A');check('reader-cannot-complete-human-task',status==403)
status,other=call('/models',user='designer-B');check('organisation-B-sees-no-A-models',status==200 and not any(m['organisation']=='A' for m in other))
status,_=approve(old,user='gestionnaire-B');check('organisation-B-cannot-complete-A-case',status in (404,503))
assert approve(old)[0]==202;assert approve(fresh)[0]==202
oldstate=state(old,'COMPLETED');newstate=state(fresh,'COMPLETED')
check('old-instance-keeps-frozen-definition',oldstate['definitionVersion']==v1 and 'notifier' in oldstate['completed'] and 'verifier_capacite' not in oldstate['completed'],oldstate)
check('new-instance-uses-editor-version-without-worker-redeployment',newstate['definitionVersion']==v2 and 'notifier_express' in newstate['completed'] and 'verifier_capacite' in newstate['completed'],newstate)
check('duplicate-answer-idempotent',approve(old)[0]==200);check('conflicting-answer-rejected',approve(old,approved=False)[0]==409)
status,_=call('/cases',dict(caseId=old,version=v1));check('duplicate-workflow-id-rejected',status==409)
for id in (old,fresh):history(id)
retry=run+'-retry';start(retry,v1,'lost-ack');approve(retry);state(retry,'COMPLETED');status,effects=call('/effects');key='A/A-'+retry+'/admettre';keys={k for e in effects['effects'] for k in e};check('lost-ack-retried-with-one-durable-effect',effects['attempts'][key]==2 and key in keys,effects['attempts'][key]);history(retry)
unsafe=run+'-unsafe';start(unsafe,v1,'non-idempotent');approve(unsafe);state(unsafe,'COMPLETED');_,effects=call('/effects');keys={k for e in effects['effects'] for k in e};check('negative-control-no-exactly-once-without-adapter',len([k for k in keys if '/A-'+unsafe+'/admettre/' in k])==2)
comp=run+'-comp';start(comp,v1,'notify-always-fails');approve(comp);state(comp,'COMPENSATED');_,effects=call('/effects');keys={k for e in effects['effects'] for k in e};check('provider-failure-compensated',not any('/A-'+comp+'/' in k for k in keys));history(comp)
reject=run+'-reject';start(reject,v1);approve(reject,approved=False);check('business-rejection-route',state(reject,'REJECTED')['state']=='REJECTED');history(reject)
restart=run+'-worker';start(restart,v1);status,_=call('/test/restart-worker',{});check('worker-factory-restarted',status==200);assert approve(restart)[0]==202;check('live-worker-restart-resumes-history',state(restart,'COMPLETED')['state']=='COMPLETED');history(restart)
durable=run+'-durable';start(durable,v2);prefix=history(durable)
record=dict(status='phase1_passed',date='2026-10-31',runtime='Temporal CLI 1.9.1 official SQLite dev server; Java SDK 1.36.0; Spring 6.2 (Boot 3.5.7 BOM)',run=run,version1=v1,version2=v2,pending_case=durable,pending_history_prefix=prefix,checks=checks,limits=['Fixture identities are simulated, not SSO authentication.','Business actions use a local synthetic effect store, not production stock/ERP services.','A single-node dev server does not demonstrate production HA or RTO.'])
(O/'temporal-live-phase1.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(dict(status=record['status'],checks=len(checks),passed=sum(c['passed'] for c in checks),pending_case=durable),ensure_ascii=False))
