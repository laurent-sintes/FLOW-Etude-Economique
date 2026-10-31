"""Reproduce a complete-family proposal from frozen inputs; retained decisions stay untouched."""
from pathlib import Path
from collections import defaultdict
import json,hashlib,math,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
from model_context import model_session
from estimation_calculation import formula,rounded,alignment
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(stage):
 folder=OUT/f'iteration-{stage:02}';data=read(folder/'inputs.json')
 assert sha(folder/'inputs.json')==read(folder/'freeze.json')['inputs_sha256']
 base=read(OUT/'baseline.json');native=read(ROOT/'audits/2026-10-30-propriete-stock-calcul-02/inputs.json')
 common=read(ROOT/data['common_results_ref']);meas=read(ROOT/data['common_measurements_ref'])
 dist=read(ROOT/'audits/2026-10-30-master-data-calcul/repartitions-sources.json')['cocomo']
 alloc=read(ROOT/'audits/2026-10-30-stock-consolidation-09/inputs.json')['activity_role_weights']
 c=data['cocomo'];E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum']);F=formula('schedule_exponent',D=c['D'],E=E,B=c['B'])
 def effort(u):
  return formula('cocomo_effort',A=c['A'],KSLOC=u/1000,E=E,EM=c['other_EM'],SCED=c['SCED'],month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor']) if u else 0
 products=['erpnext','odoo','tryton','axelor'];owners={};families=data['families'];lookup={f['slug']:f for f in families}
 # Native base atoms from iteration 4 are funded by their common owner, except the excluded supplied kernels.
 for b in meas['bindings']:
  for a in b['atoms']:
   mechanism=a.get('base_owner')
   if not mechanism:continue
   if b['product'] in common['reuse_adjustment']['base_exclusions'].get(mechanism,[]):continue
   owner=next(x['owner'] for x in meas['specification']['mechanisms'] if x['id']==mechanism)
   owners[(b['repo'],b['path'],('D:' if b['kind']=='declarative' else '')+a['key'])]=owner
 localbank={};localbase={};baseassignment=[]
 priority=['orders','master-plan','plan-preparation','optimization','service-planning']+[f['slug'] for f in families if f['slug'] not in ['orders','master-plan','plan-preparation','optimization','service-planning']]
 for slug in priority:
  f=lookup[slug];localbank[slug]=dict.fromkeys(products,0);localbase[slug]=dict.fromkeys(products,0);seen=set()
  for b in f['bindings']:
   for a in b['atoms']:
    key=(b['repo'],b['path'],a['key'])
    if key in seen:continue
    seen.add(key);localbank[slug][b['product']]+=1
    if not b['provided_kernel'] and key not in owners:
     owners[key]=slug;localbase[slug][b['product']]+=1
    baseassignment.append(dict(family=slug,repo=b['repo'],path=b['path'],atom=a['key'],owner=owners.get(key),provided_kernel=b['provided_kernel']))
 labels={r['id']:r['label'] for r in base['units'][0]['roles']}
 totals=dict.fromkeys(products,0);rawtotals=dict.fromkeys(products,0);missing=[];result=[];coverage=[]
 for f in families:
  slug=f['slug'];rows=[];original=common['owners'].get(slug)
  for p in products:
   old=next(r for r in original['rows'] if r['id']==p) if original else None
   common_size=old['equivalent_units'] if old else 0
   bank=localbank[slug][p];scaffold=native['new_module_scaffolding'][p]['program_units_per_new_service_module'];t=native['schema_templates'][p]
   # A specific measured provider may replace an incomplete native source bank, never an invented JH.
   provider=f.get('analogue_provider')
   if provider:bank=provider['units'][p]
   if bank==0:
    rows.append(dict(id=p,jh=None,reason='Analogue local incomplet'));missing.append([slug,p]);continue
   new=formula('module_analogy',reference_units=bank,fraction=f['extension_fraction']*f['quantity'],scaffold_units=scaffold*f['quantity'])
   models=[dict(name=s['name'],fields=s['fields'],program_units=len(s['fields'])*t['program_per_field']+t.get('program_per_new_model',0),declarative_units=len(s['fields'])*t['declarations_per_field']+t['per_new_model']+len(s['fields'])*t['view_field']+t['view_model']) for s in f['schemas']]
   schemas=sum(x['program_units']+x['declarative_units'] for x in models)
   additional=f.get('additional_modules',[]);mods=[]
   for mod in additional:
    size=formula('module_analogy',reference_units=mod['units'][p],fraction=mod['fraction'],scaffold_units=scaffold*mod.get('scaffolds',1))
    mods.append(dict(id=mod['id'],units=size,basis=mod['basis']))
   size=common_size+localbase[slug][p]+new+schemas+sum(x['units'] for x in mods)
   jh=effort(size);r=dict(id=p,common_equivalent_units=common_size,native_local_base_units=localbase[slug][p],analogue_program_units=bank,new_local_code_units=new,models=models,additional_modules=mods,equivalent_units=size,jh=jh,rounded_jh=rounded(jh,10),common_cost_embedded_not_added=True,local_marginal_jh=jh-effort(common_size),not_observed_cost=True)
   rows.append(r);totals[p]+=r['rounded_jh'];rawtotals[p]+=jh
  java=next(x for x in rows if x['id']=='axelor');chosen=java.get('rounded_jh');roles=[];activities=[]
  if chosen is not None:
   weight=dict.fromkeys(labels,0.)
   for a in dist['activities']:
    share=sum(x*y for x,y in zip(dist['phase_effort_percent_of_base'],a['percent_by_phase']))/sum(dist['phase_effort_percent_of_base'])/100
    actjh=chosen*share;activities.append(dict(id=a['id'],jh=actjh,percent_by_phase=a['percent_by_phase'],weights=alloc[a['id']]))
    for k,w in alloc[a['id']].items():weight[k]+=actjh*w
   rd={k:math.floor(v) for k,v in weight.items()}
   for k in sorted(weight,key=lambda k:(-(weight[k]-math.floor(weight[k])),k))[:round(chosen-sum(rd.values()))]:rd[k]+=1
   roles=[dict(id=k,label=labels[k],jh=v) for k,v in rd.items()]
   months=formula('cocomo_schedule',C=c['C'],JH=chosen,effort_phase_factor=c['effort_phase_factor'],day_hours=c['day_hours'],month_hours=c['month_hours'],SCED=c['SCED'],F=F,schedule_phase_factor=c['schedule_phase_factor'])
  else:months=None
  cosmic_ref=f.get('cosmic_ref','audits/2026-10-30-familles-restantes/'+slug+'/cosmic-2.json');cosmic=read(ROOT/cosmic_ref)
  movements=[(v['type'],v['group']) for proc in cosmic['processes'] for v in proc['movements']]
  functional=formula('cosmic_effort',CFP=len(movements),hours_per_CFP=20,factor=1,day_hours=7)
  for row in rows:
   if row.get('jh') is not None and java.get('jh') is not None:row['alignment_vs_java']=alignment(row['jh'],java['jh'])
  entry=dict(slug=slug,id=f['id'],name=f['name'],capabilities=f['capabilities'],scope=f['scope'],rows=rows,proposed_java_jh=chosen,roles=roles,activities=activities,raw_months=months,nominal_months=rounded(months,1) if months else None,delay_status='Nominal local COCOMO ; pas un calendrier intégré ni un engagement d’équipe.',cosmic=dict(ref=cosmic_ref,CFP=len(movements),jh=functional,alignment_vs_java=alignment(functional,java['jh']) if java.get('jh') else None,published_benchmark_hours_per_CFP=20,benchmark_not_reuse_calibrated=True),funding_scope='Famille entière : commun intégré + travail local. Ne pas ajouter les 280 JH communs.',fraction=f['extension_fraction'],module_quantity=f['quantity'])
  result.append(entry)
  for cap in f['functions']:
   for fn in cap['functions']:coverage.append(dict(capability=cap['capability'],function=fn['id'],result=fn['resultat'],cost_owner=slug,target_module=f['local_module_id'],common_consumption=f['common_consumption'],costed=chosen is not None,evidence='Code natif mesuré et modules nouveaux supposés par analogie ; pas une preuve de réalisation Flow.'))

 economic=[]
 if data.get('economic_units'):
  totals=dict.fromkeys(products,0);rawtotals=dict.fromkeys(products,0)
  for group in data['economic_units']:
   members=[x for x in result if x['slug'] in group['families']];grows=[]
   for p in products:
    sizes=[next(r for r in x['rows'] if r['id']==p) for x in members]
    assert all(x.get('jh') is not None for x in sizes)
    size=sum(x['equivalent_units'] for x in sizes);jh=effort(size);value=rounded(jh,10)
    grows.append(dict(id=p,equivalent_units=size,jh=jh,rounded_jh=value))
    totals[p]+=value;rawtotals[p]+=jh
   java=next(x for x in grows if x['id']=='axelor');chosen=java['rounded_jh']
   weights=dict.fromkeys(labels,0.)
   for a in dist['activities']:
    share=sum(x*y for x,y in zip(dist['phase_effort_percent_of_base'],a['percent_by_phase']))/sum(dist['phase_effort_percent_of_base'])/100
    for k,w in alloc[a['id']].items():weights[k]+=chosen*share*w
   rroles={k:math.floor(v) for k,v in weights.items()}
   for k in sorted(weights,key=lambda k:(-(weights[k]-math.floor(weights[k])),k))[:round(chosen-sum(rroles.values()))]:rroles[k]+=1
   size_total=java['equivalent_units'];shares={}
   for member in members:
    size=next(x for x in member['rows'] if x['id']=='axelor')['equivalent_units'];shares[member['slug']]=chosen*size/size_total
   allocated={k:math.floor(v) for k,v in shares.items()}
   for k in sorted(shares,key=lambda k:(-(shares[k]-math.floor(shares[k])),k))[:round(chosen-sum(allocated.values()))]:allocated[k]+=1
   for member in members:
    member['independent_fragment_diagnostic_jh']=member['proposed_java_jh']
    member['proposed_java_jh']=allocated[member['slug']];member['economic_unit']=group['id']
    member['allocation_status']='Part du total de l’unité cohérente proportionnelle à la taille équivalente ; pas un chiffrage indépendant de Business Area.'
    member['roles']=[];member['nominal_months']=None;member['raw_months']=None
   months=formula('cocomo_schedule',C=c['C'],JH=chosen,effort_phase_factor=c['effort_phase_factor'],day_hours=c['day_hours'],month_hours=c['month_hours'],SCED=c['SCED'],F=F,schedule_phase_factor=c['schedule_phase_factor'])
   cr=group.get('cosmic_ref')
   if cr:
    cc=read(ROOT/cr);cfp=sum(len(proc['movements']) for proc in cc['processes'])
   else:cfp=sum(x['cosmic']['CFP'] for x in members)
   fjh=formula('cosmic_effort',CFP=cfp,hours_per_CFP=20,factor=1,day_hours=7)
   for row in grows:row['alignment_vs_java']=alignment(row['jh'],java['jh'])
   economic.append(dict(**group,capabilities=sorted({cap for f in members for cap in f['capabilities']}),rows=grows,proposed_java_jh=chosen,
    roles=[dict(id=k,label=labels[k],jh=v) for k,v in rroles.items()],nominal_months=rounded(months,1),raw_months=months,
    family_allocations=allocated,COSMIC=dict(ref=cr,CFP=cfp,jh=fjh,alignment_vs_java=alignment(fjh,java['jh']),status='rebased_component_count' if cr else 'sum_of_previous_component_counts_not_yet_rebased',not_confidence=True)))

 complete=not any(p=='axelor' for f,p in missing);sumjava=totals['axelor'] if complete else None
 report=dict(iteration=stage,status='complete_opportunity_proposal' if complete else 'incomplete_proposal',families=result,assumptions=dict(cocomo=c,metric=data['counter_ref'],primary='COCOMO II',control='COSMIC × ISBSG',no_AI_discount=True,no_extra_pilotage=True,code_hypotheses_not_observed=True),new_native_subtotals=totals,new_native_unrounded_subtotals=rawtotals,missing_native_analogues=missing,progress=dict(total_capabilities=88,retained_capabilities=16,retained_jh=1940,proposed_additional_capabilities=len({x['capability'] for x in coverage if x['costed']}),complete_proposed_capabilities=16+len({x['capability'] for x in coverage if x['costed']}),functions_costed=sum(x['costed'] for x in coverage),total_functions=len(coverage),remaining_functions=sum(not x['costed'] for x in coverage)),cumulative=dict(retained_jh=1940,additional_proposed_jh=sumjava,complete_proposed_jh=1940+sumjava if complete else None,common_280_already_embedded=True,not_an_integrated_cocomo_estimate=True,no_schedules_summed=True,no_active_model_change=True),function_coverage=coverage,native_base_assignment=baseassignment)
 report['economic_units']=economic
 save(folder/'results.json',report)
 print(json.dumps(dict(iteration=stage,cumulative=report['cumulative'],progress=report['progress'],units={g['id']:g['proposed_java_jh'] for g in economic},families={f['slug']:f['proposed_java_jh'] for f in result},missing=missing),ensure_ascii=False))
if __name__=='__main__':
 with model_session():run(int(sys.argv[1]))
