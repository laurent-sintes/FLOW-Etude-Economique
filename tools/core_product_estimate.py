"""Reproduce a proposed complete product from frozen code analogues; never change adopted decisions."""
from collections import defaultdict
from copy import deepcopy
import hashlib,math
from jsonschema import Draft202012Validator
from validate_stacks import ROOT,read
from model_context import scoped_model,model_memo
from estimation_calculation import formula,rounded,alignment
SOURCE='source/proposition-produit-core.yaml'
SCHEMA='source/schema-proposition-produit-core.yaml'
ERROR='ERR_PRODUCT_PROPOSAL:'
def require(v,msg):
 if not v:raise ValueError(ERROR+msg)
def dependencies():
 d=read(ROOT/SOURCE);return {SOURCE,SCHEMA,d['inputs']['path'],d['technical_trials']['evidence']['path'],'tools/core_product_estimate.py','source/plan-investissement.yaml','source/deploiement-groupe.yaml'}|({d['adoption']['basis']['path']} if d.get('adoption') else set())
def load_inputs():
 d=read(ROOT/SOURCE);Draft202012Validator(read(ROOT/SCHEMA)).validate(d);p=(ROOT/d['inputs']['path']).resolve();require(p.is_relative_to(ROOT.resolve()),'evidence path');require(hashlib.sha256(p.read_bytes()).hexdigest()==d['inputs']['sha256'],'evidence changed');return d,read(p)
def validate_technical_trials(trials,proof,inputs,inputs_sha256):
 require(proof.get('version')==1 and proof.get('id')==trials['id'] and proof.get('status')==trials['status'],'technical trial identity')
 require(proof.get('proposal_inputs_sha256')==inputs_sha256,'technical trial proposal binding')
 groups=proof.get('check_groups',[]);require(bool(groups) and len({g['id'] for g in groups})==len(groups),'technical trial check groups')
 count=0
 for group in groups:
  checks=group['checks'];require(bool(checks) and all(isinstance(c.get('id'),str) and c['id'] for c in checks),'technical trial check identities')
  require(all(c.get('passed') is True for c in checks),'technical trial failed check');count+=len(checks)
 require(proof.get('archive',{}).get('encoding')=='gzip-base64' and proof['archive'].get('files',0)>0,'technical trial archive')
 for row in trials['funding']:require(set(row['module_refs'])<=set(inputs['groups']),'technical trial unknown funding')
 require(trials['effort_effect']=='unchanged','technical trial cannot change adopted effort')
 result=deepcopy(trials);result['checks_passed']=count
 for row in result['funding']:
  row['module_labels']=[inputs['groups'][id]['label'] for id in row['module_refs']]
  row['function_refs']=sorted({f for id in row['module_refs'] for f in inputs['measurements']['groups'][id]['functions']})
 return result

def load_technical_trials(doc,inputs):
 trials=doc['technical_trials'];ref=trials['evidence'];path=(ROOT/ref['path']).resolve();require(path.is_relative_to(ROOT.resolve()),'technical trial evidence path')
 require(hashlib.sha256(path.read_bytes()).hexdigest()==ref['sha256'],'technical trial evidence changed')
 return validate_technical_trials(trials,read(path),inputs,doc['inputs']['sha256'])

def apportioned(total,weights):
 require(total>=0 and math.isfinite(total),'invalid effort');require(all(v>=0 and math.isfinite(v) for v in weights.values()) and sum(weights.values())>0,'invalid weights')
 den=sum(weights.values());raw={k:total*v/den for k,v in weights.items()};result={k:int(v) for k,v in raw.items()}
 for k in sorted(raw,key=lambda k:raw[k]-result[k],reverse=True)[:int(total)-sum(result.values())]:result[k]+=1
 require(sum(result.values())==total,'role allocation');return result

def calculate(d,adopted,change=None,decl_weight=1,credit=True,rule_function=None):
 calc=rule_function or formula
 require(type(decl_weight) in (int,float) and math.isfinite(decl_weight) and decl_weight>0,'invalid declarative weight')
 if change:require(change[0] in d['groups'],'unknown module assumption')
 c=d['cocomo'];E=calc('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum']);F=calc('schedule_exponent',D=c['D'],E=E,B=c['B'])
 def effort(size):return calc('cocomo_effort',A=c['A'],KSLOC=size/1000,E=E,EM=c['other_EM'],SCED=c['SCED'],month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor']) if size else 0
 def schedule(jh):return calc('cocomo_schedule',C=c['C'],JH=jh,effort_phase_factor=c['effort_phase_factor'],day_hours=c['day_hours'],month_hours=c['month_hours'],SCED=c['SCED'],F=F,schedule_phase_factor=c['schedule_phase_factor'])
 products=('erpnext','odoo','tryton','axelor');measures=d['measurements'];groups={gid:dict.fromkeys(products,0.) for gid in d['groups']};credits={gid:dict.fromkeys(products,0.) for gid in groups}
 identities=set()
 for f in measures['files']:
  key=(f['repo'],f['path']);require(key not in identities,'duplicate source file');identities.add(key);require(f['pinned_equal'],'unpinned source')
  for k in ('program_units','declarative_units','existing_MD_credit_units'):require(type(f[k]) in (int,float) and math.isfinite(f[k]) and f[k]>=0,'invalid code measure')
  require(f['existing_MD_credit_units']<=f['program_units']+f['declarative_units'],'credit exceeds measured size')
  val=f['program_units']+decl_weight*f['declarative_units'];sub=min(val,f['existing_MD_credit_units']) if credit else 0
  groups[f['group']][f['product']]+=val-sub;credits[f['group']][f['product']]+=sub
 # Larger graph/analytics implementations define the shared connector analogue; a CRM query is insufficient.
 bank=max(groups['analytics-mining'].values());groups['analytics-mining']={p:bank for p in products}
 # Comparable autonomous studio: only the complete Axelor perimeter is used. State-machine builders are not equivalent.
 bank=groups['process-studio']['axelor'];groups['process-studio']={p:bank for p in products}
 # Designer/portal analogue: Axelor complete perimeter; generic render-only implementations are not equivalent.
 bank=groups['human-forms']['axelor'];groups['human-forms']={p:bank for p in products}
 scaled={}
 for gid,vals in groups.items():
  fraction=(change[1] if change and change[0]==gid else d['groups'][gid]['fraction']);require(type(fraction) in (float,int) and math.isfinite(fraction) and fraction>=0,'invalid module assumption');scaled[gid]={p:val*fraction for p,val in vals.items()}
 prior=d['code_audit']['new']['component_details']['details'];retained_sizes={u['id']:{r['id']:r['new_units'] for r in u['rows']} for u in d['code_audit']['units']}
 old={u['id']:u for u in adopted};process_id='process-management-java-spring';require(process_id in old,'missing process decision')
 java=old[process_id];rate_index={r['id']:r['rate_eur_jh'] for r in java['roles']};require(set(rate_index)==set(d['roles_it'])==set(d['roles_business']),'role keys')
 for u in adopted:require(all(r['rate_eur_jh']==rate_index[r['id']] for r in u['roles']),'retained role rates differ; preserve unit-specific valuation')
 for weights in (d['roles_it'],d['roles_business']):require(math.isclose(sum(weights.values()),1),'role weights must sum to one')
 result=[]
 for p in products:
  base=prior['workflow'][p]+prior['supervision'][p];require(math.isclose(sum(prior[g][p] for g in ('workflow','supervision','human-work','intelligence')),retained_sizes['processes'][p],rel_tol=1e-9),'process boundary mismatch')
  process_size=base+sum(scaled[g][p] for g in ('process-studio','human-forms','analytics-mining'))
  it_size=sum(scaled[g][p] for g in ('admin-security','operations-lifecycle','data-services'));workbench_size=scaled['supply-workbenches'][p]
  process_jh=rounded(effort(process_size),10);it_jh=rounded(effort(it_size),10);bench_jh=rounded(effort(workbench_size),10)
  fixed=sum(u['total_jh'] for id,u in old.items() if id!=process_id) if p=='axelor' else sum(rounded(effort(v[p]),100 if id=='master_data' else 10) for id,v in retained_sizes.items() if id!='processes')
  total=fixed+process_jh+it_jh+bench_jh
  result.append(dict(id=p,retained_other_units_jh=fixed,process_base_units=base,removed_old_units=prior['human-work'][p]+prior['intelligence'][p],process_size=process_size,process_raw_jh=effort(process_size),process_jh=process_jh,process_months=schedule(process_jh),it_size=it_size,it_raw_jh=effort(it_size),it_jh=it_jh,it_months=schedule(it_jh),workbench_size=workbench_size,workbench_raw_jh=effort(workbench_size),workbench_jh=bench_jh,workbench_months=schedule(bench_jh),total_jh=total,nominal_effort_based_months=schedule(total)))
 selected=next(r for r in result if r['id']=='axelor');process_total=selected['process_jh'];base_jh=effort(selected['process_base_units']);weights={r['id']:r['jh']/java['total_jh']*base_jh+d['roles_business'][r['id']]*(process_total-base_jh) for r in java['roles']}
 proc_roles=apportioned(process_total,weights);it_roles=apportioned(selected['it_jh'],d['roles_it']);bench_roles=apportioned(selected['workbench_jh'],d['roles_business'])
 rows=[dict(id='process-management-revised',label='Process Management avec studios, portail, formulaires et pilotage',purpose='business-runtime',jh=process_total,months=selected['process_months'],roles=proc_roles,replaces=process_id),dict(id='supply-workbenches',label='Ateliers visuels de planification et de décision',purpose='business-runtime',jh=selected['workbench_jh'],months=selected['workbench_months'],roles=bench_roles,replaces=None),dict(id='professional-it',label='Administration, robustesse et services IT complémentaires',purpose='it-complement',jh=selected['it_jh'],months=selected['it_months'],roles=it_roles,replaces=None)]
 oldit=apportioned(round(old['master-data-java-spring']['total_jh']*d['md_partition']['fraction']),{r['id']:r['jh'] for r in old['master-data-java-spring']['roles']})
 roles=defaultdict(int);purposes={'business-runtime':dict(jh=0,eur_ht=0.,roles=defaultdict(int)),'it-complement':dict(jh=0,eur_ht=0.,roles=defaultdict(int))}
 def add(purpose,rs,tooling):
  target=purposes[purpose]
  for id,v in rs.items():roles[id]+=v;target['roles'][id]+=v;target['jh']+=v;target['eur_ht']+=calc('role_price',JH=v,rate=rate_index[id])+v*tooling
 for u in adopted:
  if u['id']==process_id:continue
  rs={r['id']:r['jh'] for r in u['roles']};it=oldit if u['id']=='master-data-java-spring' else dict.fromkeys(rs,0)
  add('it-complement',it,u['tooling_eur_jh']);add('business-runtime',{id:rs[id]-it[id] for id in rs},u['tooling_eur_jh'])
 for row in rows:
  add(row['purpose'],row['roles'],java['tooling_eur_jh']);row['eur_ht']=round(sum(calc('role_price',JH=v,rate=rate_index[id])+v*java['tooling_eur_jh'] for id,v in row['roles'].items()),2)
 for v in purposes.values():v['eur_ht']=round(v['eur_ht'],2);v['roles']=dict(v['roles'])
 equivalent_total=sum(v['axelor'] for id,v in retained_sizes.items() if id!='processes')+selected['process_size']+selected['it_size']+selected['workbench_size'];integrated=effort(equivalent_total)
 grouping=dict(equivalent_logical_units=equivalent_total,single_project_jh=integrated,sum_of_units_jh=selected['total_jh'],gap_jh=integrated-selected['total_jh'],gap_pct=100*(integrated/selected['total_jh']-1))
 cost=round(sum(v['eur_ht'] for v in purposes.values()),2);require(sum(roles.values())==selected['total_jh']==sum(v['jh'] for v in purposes.values()),'complete effort conservation')
 require(sum(row['jh'] for row in rows)+sum(u['total_jh'] for id,u in old.items() if id!=process_id)==selected['total_jh'],'replacement total')
 return dict(rows=rows,grouping_sensitivity=grouping,comparative_rows=result,total_jh=selected['total_jh'],eur_ht=cost,roles=[dict(id=id,label=next(r['label'] for r in java['roles'] if r['id']==id),jh=v,rate_eur_jh=rate_index[id]) for id,v in roles.items()],purposes=purposes,existing_it_partition_jh=sum(oldit.values()),nominal_effort_based_months=selected['nominal_effort_based_months'],groups_equivalent_units=scaled,credited_MD_units=credits,adopted_jh=sum(u['total_jh'] for u in adopted),status='proposal_not_adopted',comparability='Les quatre lectures partagent les analogues complets Axelor pour studios/formulaires et le même analogue de pilotage. Ce ne sont pas quatre observations indépendantes de coût natif ni des bilans de projets.')

def functional_forecast(d):
 for gid,rr in d['cosmic']['processes'].items():
  require(gid in d['groups'] and len({x['id'] for x in rr})==len(rr),'COSMIC process identities')
  for x in rr:
   require(x['scope'] in ('new','existing_function_consumed'),'COSMIC funding scope')
   for k in ('E','R','W','X'):require(len(x[k])==len(set(x[k])) and all(isinstance(v,str) and v for v in x[k]),'COSMIC data groups counted twice')
 cfps={g:sum(len(x[k]) for x in rr if x['scope']=='new' for k in ('E','R','W','X')) for g,rr in d['cosmic']['processes'].items()}
 old_process=d['cosmic']['retained_processes'];kept=[x for x in old_process['processes'] if x['id'] not in d['cosmic']['replaced_process_ids']]
 retained=sum(m['cfp'] for x in kept for m in x['movements'])
 counts={g:sum(x['scope']=='new' for x in rr) for g,rr in d['cosmic']['processes'].items()}
 return dict(CFP_by_group=cfps,process_CFP=retained+sum(cfps[g] for g in ('process-studio','human-forms','analytics-mining')),process_count=len(kept)+sum(counts[g] for g in ('process-studio','human-forms','analytics-mining')),process_counts=counts)

@scoped_model
def build_product_proposal(economic):
 doc,d=load_inputs();trials=load_technical_trials(doc,d);active=next(o['core_units'] for o in economic['options'] if o['stack']==doc['stack']);adopted=active
 if doc.get('adoption'):
  ref=doc['adoption']['basis'];path=(ROOT/ref['path']).resolve();require(path.is_relative_to(ROOT.resolve()) and hashlib.sha256(path.read_bytes()).hexdigest()==ref['sha256'],'adoption basis changed')
  adopted=deepcopy(read(path)['baseline_units']);rates={r['id']:r['rate_eur_jh'] for r in active[0]['roles']}
  for u in adopted:
   u['tooling_eur_jh']=active[0]['tooling_eur_jh']
   for role in u['roles']:role['rate_eur_jh']=rates[role['id']]
 r=calculate(d,adopted)
 sensitivities=[]
 for gid,g in d['groups'].items():
  for v in g['test_values']:
   test=calculate(d,adopted,change=(gid,v));sensitivities.append(dict(id=gid,value=v,total_jh=test['total_jh'],delta_jh=test['total_jh']-r['total_jh']))
 for w in (.5,2):
  test=calculate(d,adopted,decl_weight=w);sensitivities.append(dict(id='declarative-weight',value=w,total_jh=test['total_jh'],delta_jh=test['total_jh']-r['total_jh']))
 cfps=functional_forecast(d)['CFP_by_group']
 old_process=d['cosmic']['retained_processes'];kept=[x for x in old_process['processes'] if x['id'] not in d['cosmic']['replaced_process_ids']]
 retained_CFP=sum(m['cfp'] for x in kept for m in x['movements']);process_CFP=retained_CFP+sum(cfps[g] for g in ('process-studio','human-forms','analytics-mining'))
 process_cosmic=formula('cosmic_effort',CFP=process_CFP,hours_per_CFP=d['cosmic']['hours_per_CFP'],factor=1,day_hours=d['cosmic']['day_hours'])
 r['cosmic_process']=dict(CFP=process_CFP,retained_CFP=retained_CFP,jh=process_cosmic,alignment=alignment(process_cosmic,next(x['process_raw_jh'] for x in r['comparative_rows'] if x['id']=='axelor')),reference_unrounded_jh=next(x['process_raw_jh'] for x in r['comparative_rows'] if x['id']=='axelor'),hours_per_CFP_to_match=next(x['process_raw_jh'] for x in r['comparative_rows'] if x['id']=='axelor')*d['cosmic']['day_hours']/process_CFP,kept_process_ids=[x['id'] for x in kept],replaced_process_ids=d['cosmic']['replaced_process_ids'])
 r['it_cosmic']=dict(CFP=sum(cfps[g] for g in ('admin-security','operations-lifecycle','data-services')))
 r['it_cosmic']['jh']=formula('cosmic_effort',CFP=r['it_cosmic']['CFP'],hours_per_CFP=d['cosmic']['hours_per_CFP'],factor=1,day_hours=d['cosmic']['day_hours']);r['it_cosmic']['alignment']=alignment(r['it_cosmic']['jh'],next(x['it_raw_jh'] for x in r['comparative_rows'] if x['id']=='axelor'));r['it_cosmic']['reference_unrounded_jh']=next(x['it_raw_jh'] for x in r['comparative_rows'] if x['id']=='axelor')
 plan=read(ROOT/'source/plan-investissement.yaml')['build_make_mois'][doc['stack']];capacity=read(ROOT/'source/deploiement-groupe.yaml')['calendrier_autonome']['capacite']['jours_productifs_etp_mois'];r['planning']=dict(reference_months=plan,productive_days_per_person_month=capacity,average_people_at_reference=r['total_jh']/plan/capacity,average_people_at_nominal=r['total_jh']/r['nominal_effort_based_months']/capacity)
 r.update(technical_trials=trials,reading=doc['reading'],sensitivities=sensitivities,assumptions=d['assumptions'],cosmic=dict(CFP_by_group=cfps,jh_by_group={g:formula('cosmic_effort',CFP=v,hours_per_CFP=d['cosmic']['hours_per_CFP'],factor=1,day_hours=d['cosmic']['day_hours']) for g,v in cfps.items()},status=d['cosmic']['status'],limit=d['cosmic']['ISBSG_limit']),measured_files=len(d['measurements']['files']),scope_functions=len({f for g in d['measurements']['groups'].values() for f in g['functions']}),existing_it_partition_basis=d['md_partition']['basis'],module_assumptions=[dict(id=id,**g) for id,g in d['groups'].items()],source_ref=SOURCE)
 if doc.get('adoption'):
  require(doc['status']=='retained','adoption status mismatch')
  require({u['id'] for u in active}==set(doc['adoption']['unit_ids']),'adoption unit identities')
  require(sum(u['total_jh'] for u in active)==r['total_jh'],'adoption effort mismatch')
  require(math.isclose(sum(u['cost_eur_ht'] for u in active),r['eur_ht'],abs_tol=.005),'adoption valuation mismatch')
  role_totals={id:sum(next(x['jh'] for x in u['roles'] if x['id']==id) for u in active) for id in rates}
  require(role_totals=={x['id']:x['jh'] for x in r['roles']},'adoption role mismatch')
  r.update(status='retained',previous_adopted_jh=r['adopted_jh'],adopted_jh=r['total_jh'],decision_date=doc['adoption']['decision_date'])
 return r
