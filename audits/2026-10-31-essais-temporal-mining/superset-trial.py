"""Real Superset application/API trial. No production identity or data is used."""
from pathlib import Path
import json,sqlite3,secrets,uuid,time,copy
from superset.app import create_app
app=create_app()
from superset import db,security_manager
from superset.models.core import Database
from superset.connectors.sqla.models import SqlaTable
from superset.models.slice import Slice
from superset.models.dashboard import Dashboard
from superset.models.embedded_dashboard import EmbeddedDashboard
import jwt
R=Path.cwd();O=R/'audits/2026-10-31-essais-temporal-mining/results';T=R/'tmp/targeted-runtime/superset';T.mkdir(exist_ok=True)
checks=[]
def check(id,ok,detail=None):
 checks.append(dict(id=id,passed=bool(ok),detail=detail));assert ok,(id,detail)
with app.app_context():
 data=T/'events.db'
 with sqlite3.connect(data) as c:
  c.execute('CREATE TABLE IF NOT EXISTS mining_events(organisation TEXT,case_id TEXT,version INTEGER,activity TEXT,timestamp TEXT,source_id TEXT)');c.execute('DELETE FROM mining_events')
  events=json.loads((O/'mining-events.json').read_text('utf8'))
  c.executemany('INSERT INTO mining_events VALUES (?,?,?,?,?,?)',[(r['organisation'],r['case_id'],r['version'],r['activity'],r['timestamp'],r['source_id']) for r in events])
  c.executemany('INSERT INTO mining_events VALUES (?,?,?,?,?,?)',[('B','B-confidentiel',1,'secret_B','2026-10-31T00:00:00Z','B:'+str(i)) for i in range(3)])
 admin=security_manager.find_user(username='trial-admin')
 if not admin:admin=security_manager.add_user('trial-admin','Trial','Admin','trial@example.invalid',security_manager.find_role('Admin'),secrets.token_urlsafe(24))
 database=db.session.query(Database).filter_by(database_name='Trial Mining').first()
 if not database:
  database=Database(database_name='Trial Mining',expose_in_sqllab=False);database.set_sqlalchemy_uri('sqlite:///'+str(data).replace('\\','/'));db.session.add(database);db.session.commit()
 dataset=db.session.query(SqlaTable).filter_by(table_name='mining_events',database_id=database.id).first()
 if not dataset:
  dataset=SqlaTable(table_name='mining_events',database_id=database.id,owners=[admin]);db.session.add(dataset);db.session.commit();dataset.fetch_metadata();db.session.commit()
 chart=db.session.query(Slice).filter_by(slice_name='Activités par organisation — essai').first()
 params=dict(viz_type='table',datasource=f'{dataset.id}__table',query_mode='raw',all_columns=['organisation','case_id','activity'],row_limit=1000,time_range='No filter')
 if not chart:chart=Slice(slice_name='Activités par organisation — essai',viz_type='table',datasource_id=dataset.id,datasource_type='table',owners=[admin]);db.session.add(chart)
 chart.params=json.dumps(params);db.session.commit()
 dash=db.session.query(Dashboard).filter_by(slug='trial-mining').first()
 if not dash:dash=Dashboard(dashboard_title='Processus FLOW · données fictives',slug='trial-mining',published=True,owners=[admin]);db.session.add(dash)
 dash.slices=[chart];dash.position_json=json.dumps({'DASHBOARD_VERSION_KEY':'v2','ROOT_ID':{'type':'ROOT','id':'ROOT_ID','children':['GRID_ID']},'GRID_ID':{'type':'GRID','id':'GRID_ID','children':['ROW-1'],'parents':['ROOT_ID']},'ROW-1':{'type':'ROW','id':'ROW-1','children':['CHART-1'],'parents':['ROOT_ID','GRID_ID'],'meta':{'background':'BACKGROUND_TRANSPARENT'}},'CHART-1':{'type':'CHART','id':'CHART-1','children':[],'parents':['ROOT_ID','GRID_ID','ROW-1'],'meta':{'chartId':chart.id,'width':12,'height':50,'sliceName':chart.slice_name}}});dash.json_metadata='{}';db.session.commit()
 embed=db.session.query(EmbeddedDashboard).filter_by(dashboard_id=dash.id).first()
 if not embed:embed=EmbeddedDashboard(dashboard_id=dash.id,allow_domain_list='http://127.0.0.1:18980,http://127.0.0.1:18989');db.session.add(embed);db.session.commit()
 ids=dict(dataset_id=dataset.id,chart_id=chart.id,dashboard_id=dash.id,embedded_uuid=str(embed.uuid));(T/'fixture-ids.json').write_text(json.dumps(ids),'utf8')
 form=dict(params,slice_id=chart.id,dashboardId=dash.id)
 query=dict(datasource=dict(id=dataset.id,type='table'),force=False,result_format='json',result_type='full',form_data=form,queries=[dict(columns=['organisation','case_id','activity'],metrics=[],row_limit=1000,time_range='No filter',filters=[],orderby=[],extras=dict(having='',where=''))])
 chart.query_context=json.dumps(query);db.session.commit()

 # Second chart consumes actual PM4JS algorithm outputs, not a hand-entered metric.
 metrics=json.loads((O/'mining-metrics.json').read_text('utf8'))
 with sqlite3.connect(data) as c:
  c.execute('CREATE TABLE IF NOT EXISTS mining_arcs(organisation TEXT,version INTEGER,source TEXT,target TEXT,count INTEGER,mean_seconds REAL)');c.execute('DELETE FROM mining_arcs')
  c.executemany('INSERT INTO mining_arcs VALUES (?,?,?,?,?,?)',[(r['organisation'],r['version'],r['source'],r['target'],r['count'],r['mean_seconds']) for r in metrics])
 md=db.session.query(SqlaTable).filter_by(table_name='mining_arcs',database_id=database.id).first()
 if not md:md=SqlaTable(table_name='mining_arcs',database_id=database.id,owners=[admin]);db.session.add(md);db.session.commit();md.fetch_metadata();db.session.commit()
 cols=['organisation','version','source','target','count','mean_seconds']
 mp=dict(viz_type='table',datasource=f'{md.id}__table',query_mode='raw',all_columns=cols,row_limit=1000,time_range='No filter')
 mc=db.session.query(Slice).filter_by(slice_name='Fréquences et durées calculées par PM4JS').first()
 if not mc:mc=Slice(slice_name='Fréquences et durées calculées par PM4JS',viz_type='table',datasource_id=md.id,datasource_type='table',owners=[admin]);db.session.add(mc)
 mc.params=json.dumps(mp);db.session.commit()
 mq=dict(datasource=dict(id=md.id,type='table'),force=False,result_format='json',result_type='full',form_data=dict(mp,slice_id=mc.id,dashboardId=dash.id),queries=[dict(columns=cols,metrics=[],row_limit=1000,time_range='No filter',filters=[],orderby=[],extras=dict(having='',where=''))]);mc.query_context=json.dumps(mq)
 dash.slices=[mc,chart];position=json.loads(dash.position_json);position['GRID_ID']['children']=['ROW-2','ROW-1'];position['ROW-2']=dict(type='ROW',id='ROW-2',children=['CHART-2'],parents=['ROOT_ID','GRID_ID'],meta=dict(background='BACKGROUND_TRANSPARENT'));position['CHART-2']=dict(type='CHART',id='CHART-2',children=[],parents=['ROOT_ID','GRID_ID','ROW-2'],meta=dict(chartId=mc.id,width=12,height=45,sliceName=mc.slice_name));dash.position_json=json.dumps(position);db.session.commit()
 ids.update(metrics_dataset_id=md.id,metrics_chart_id=mc.id);(T/'fixture-ids.json').write_text(json.dumps(ids),'utf8')

def token(org='A',scoped=True,resource=None,expired=False):
 with app.app_context():
  tok=security_manager.create_guest_access_token(dict(username='trial-'+org,first_name='Essai',last_name=org),[dict(type='dashboard',id=resource or ids['embedded_uuid'])],[dict(clause="organisation = '"+org+"'")] if scoped else [])
  if expired:
   claims=jwt.decode(tok,app.config['GUEST_TOKEN_JWT_SECRET'],algorithms=[app.config['GUEST_TOKEN_JWT_ALGO']],audience=app.config['GUEST_TOKEN_JWT_AUDIENCE']);claims['exp']=int(time.time())-5;tok=jwt.encode(claims,app.config['GUEST_TOKEN_JWT_SECRET'],algorithm=app.config['GUEST_TOKEN_JWT_ALGO'])
  return tok

def request(tok,q=None):
 with app.test_client() as c:
  h={'X-GuestToken':tok,'Referer':'http://127.0.0.1:18980/'}
  csrf=c.get('/api/v1/security/csrf_token/',headers=h)
  if csrf.status_code==200:h['X-CSRFToken']=csrf.json['result']
  r=c.post('/api/v1/chart/data',headers=h,json=q or query)
  return r.status_code,r.get_json()
results=[]
for org in ['A','B','A','B']:
 status,out=request(token(org));rows=out.get('result',[{}])[0].get('data',[]) if out else []
 check('native-chart-query-isolates-'+org,status==200 and bool(rows) and {r['organisation'] for r in rows}=={org},dict(http=status,rows=len(rows),response=out if status!=200 else None))
 results.append(dict(organisation=org,rows=len(rows),cache_key=out['result'][0].get('cache_key'),is_cached=out['result'][0].get('is_cached'),sql=out['result'][0].get('query')))
check('RLS-partitions-cache-key',results[0]['cache_key']!=results[1]['cache_key'])
status,unscoped=request(token(scoped=False));rows=unscoped.get('result',[{}])[0].get('data',[]) if unscoped else []
check('negative-control-token-without-RLS-exposes-both-organisations',status==200 and {r['organisation'] for r in rows}=={'A','B'},dict(http=status,rows=len(rows)))
status,out=request(token(resource=str(uuid.uuid4())));check('wrong-dashboard-resource-rejected',status in (401,403),dict(http=status))
status,out=request(token(expired=True));check('expired-guest-token-rejected',status in (401,403),dict(http=status))
altered=copy.deepcopy(query);altered['queries'][0]['columns'].append('source_id');status,out=request(token(),altered);check('negative-control-exposed-dataset-columns-remain-queryable',status==200 and all(r['organisation']=='A' for r in out['result'][0]['data']) and 'source_id' in out['result'][0]['data'][0],dict(http=status,note='Expose a curated reporting dataset; chart configuration alone is not the column security boundary in this fixture.'))
for org in ['A','B']:
 status,out=request(token(org),mq);actual=out.get('result',[{}])[0].get('data',[]) if out else [];expected=[r for r in metrics if r['organisation']==org]
 key=lambda r:(r['version'],r['source'],r['target'])
 check('PM4JS-metrics-displayed-exactly-for-'+org,status==200 and sorted(actual,key=key)==sorted(expected,key=key),dict(http=status,rows=len(actual)))
with app.test_client() as c:
 ok=c.get('/embedded/'+ids['embedded_uuid'],headers={'Referer':'http://127.0.0.1:18980/'})
 no=c.get('/embedded/'+ids['embedded_uuid'],headers={'Referer':'https://untrusted.example.invalid/'})
 check('embed-allowed-origin',ok.status_code==200,ok.status_code);check('embed-forbidden-origin',no.status_code==403,no.status_code)
r=dict(status='passed',date='2026-10-31',version='apache-superset 6.1.0, official release constraints',checks=checks,queries=results,fixture=ids,limits=['Actual Superset query/security/cache code, accessed through Flask integrated HTTP client.','Fixture identities, no SSO or real production datasource.','Guest tokens must be minted server-side with mandatory row-level organisation rules.','The exposed dataset must contain only permitted columns; a modified request accessed source_id within A in this fixture.','No proof of production HA, refresh capacity or confidential-data handling from this local trial.'])
(O/'superset.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8');print(json.dumps(dict(status=r['status'],checks=len(checks),queries=results,fixture=ids),ensure_ascii=False))
