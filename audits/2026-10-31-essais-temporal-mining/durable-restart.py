from pathlib import Path
import json,time,urllib.request
R=Path.cwd();O=R/'audits/2026-10-31-essais-temporal-mining/results'
p=json.loads((O/'temporal-live-phase1.json').read_text('utf-8')); cid=p['pending_case']; base='http://127.0.0.1:18980'
def call(path,body=None):
 req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body else None,headers={'Content-Type':'application/json','X-Trial-User':'gestionnaire-A'})
 with urllib.request.urlopen(req,timeout=8) as r:return json.load(r)
for n in range(60):
 try:
  before=call('/cases?caseId='+cid);break
 except Exception:time.sleep(.5)
assert before['state']=='WAITING',before
answer=call('/outcomes',dict(caseId=cid,eventId='after-process-restart',approved=True))
for n in range(100):
 after=call('/cases?caseId='+cid)
 if after['state']=='COMPLETED':break
 time.sleep(.1)
assert after['state']=='COMPLETED',after
history=call('/history?caseId='+cid)
old=p['pending_history_prefix']['events']; new=history['events']
assert new[:len(old)]==old,'Persisted history changed'
r=dict(status='passed',date='2026-10-31',case=cid,before=before,after=after,unchanged_history_prefix_events=len(old),final_events=len(new),checks=[dict(id='workflow-survives-abrupt-server-and-worker-process-stop',passed=True),dict(id='durable-history-prefix-identical',passed=True)],limits=['Abrupt process restart on one SQLite dev server; not a cluster failover or production RTO measurement.'])
(O/'temporal-durable-restart.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf-8');print(json.dumps(r,ensure_ascii=False))
