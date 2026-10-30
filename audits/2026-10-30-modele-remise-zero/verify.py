import sys,json,hashlib
from pathlib import Path
sys.path[:0]=['tmp/model-deps','tools']
sys.stdout.reconfigure(encoding='utf-8')
from study_app import Study
from validate_stacks import read
a=Path('audits/2026-10-30-modele-remise-zero')
before=json.loads((a/'before-economics.json').read_text(encoding='utf-8'))
s=Study();after={'baseline':s.baseline,'economic':s.economic,'parameters':s.parameters,'core':s._essential_core_evaluation()}
(a/'after-economics.json').write_text(json.dumps(after,ensure_ascii=False,indent=2),encoding='utf-8')
checks=[];impact=[]
def check(ok,label):
 assert ok,label
 checks.append(label)
for old,new in zip(before['baseline']['options'],after['baseline']['options']):
 check(old['stack']==new['stack'],'same option '+new['stack'])
 slug=new['stack']
 for k in ('integration','annual_base','services','service_start_month','initial_months','hosting_build','selection_buy','selection_months','editor_prices'):
  check(old[k]==new[k],slug+' unchanged '+k)
 if new['mode']=='Buy':check(old==new,slug+' full equality')
 else:
  check(new['build']==0,slug+' build zero')
  for h in new['horizons']:
   prior=next(x for x in old['horizons'] if x['years']==h['years'])
   for key in ('integration','mco_run'):check(h['totals'][key]==prior['totals'][key],slug+str(h['years'])+' unchanged '+key)
   delta=round(h['totals']['total']-prior['totals']['total'],2)
   build_delta=round(h['totals']['build']-prior['totals']['build'],2)
   check(abs(delta-build_delta)<.02,slug+str(h['years'])+' reconciled total')
 for h in new['horizons']:
  prior=next(x for x in old['horizons'] if x['years']==h['years'])
  impact.append({'stack':slug,'years':h['years'],'before_eur':prior['totals']['total'],'after_eur':h['totals']['total'],'delta_eur':round(h['totals']['total']-prior['totals']['total'],2)})
cal=read(Path('source/recalibration-metier.yaml'))
oldcal=read(a/'before/source/recalibration-metier.yaml')
for k in ('maintenance','blocs','transverse','couvertures','dependances'):
 check(cal[k]==oldcal[k],'calibration unchanged '+k)
check(all(not any(v[b]) for v in cal['lots'].values() for b in ('bas','central','haut')),'all construction ranges zero')
for r in after['core']:
 if r['mode']=='Make':
  check(r['uncertainty_pct'] is None,r['stack']+' no invented uncertainty')
  check(r['estimation_status']=='pending_reestimation',r['stack']+' explicit pending status')
hashes=json.loads((a/'before-hashes.json').read_text())
changed=[p for p,h in hashes.items() if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
report={'checks':checks,'impact':impact,'changed_existing_files':changed,'core_before':before['core'],'core_after':after['core']}
(a/'impact.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'checks':len(checks),'impact':impact,'changed_files':changed},ensure_ascii=False,indent=2))
