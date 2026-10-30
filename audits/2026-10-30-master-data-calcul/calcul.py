"""Master Data audit: external effort models, no hand-entered task durations."""
from pathlib import Path
import json,hashlib,math,sys,collections
ROOT=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding='utf-8')
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,d):(A/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
I=load(A/'entrees.json');checks=[]
def check(condition,label):
 if not condition:raise AssertionError(label)
 checks.append(label)
B=load(A/'baseline.json')
for p,h in B['files'].items():check(sha(ROOT/p)==h,'Preserved '+p)
inputs={k:load((A/v).resolve()) for k,v in I['sources'].items()}
C,T,M,J,TS=(inputs[k] for k in ['cosmic','size','cocomo','java','typescript'])
check(I['units']['jh_hours']==M['constants']['jh_hours']==7,'7-hour JH convention')
check(I['units']['cocomo_person_month_hours']==M['constants']['person_month_hours']==152,'152-hour COCOMO month')
# Check source-file evidence without pretending that target quantities are measured.
samples=[]
for s in J['samples']:
 p=ROOT/s['path'];check(sha(p)==s['sha256'],'Java source hash '+s['id'])
 check(sum(x['logical_units_proxy'] for x in s['detail'])==s['logical_units_proxy'],'Java measurement sum '+s['id'])
 samples.append({'id':s['id'],'path':s['path'],'commit':s['commit'],'sha256':s['sha256'],'measured_proxy_units':s['logical_units_proxy'],'ranges':s['ranges']})
for s in TS['files']:
 check(sha(ROOT/s['cache_path'])==s['sha256'],'TS source hash '+s['id'])
 check(sum(s['counts'].values())==s['total_logical'],'TS measurement sum '+s['id'])
 samples.append({'id':s['id'],'path':s['cache_path'],'commit':s['commit'],'sha256':s['sha256'],'measured_proxy_units':s['total_logical'],'ranges':s['ranges']})
save('preuves-tailles.json',{'meaning':'Code OSS observé ; quantités cibles FLOW et transposition en unités compatibles COCOMO restent hypothèses. Aucun effort mesuré ici.','samples':samples})
# Recount data movements; no effort included in size.
counts=collections.Counter(); process_rows=[]
for p in C['processes']:
 ids=[m['id'] for m in p['movements']]
 check(len(ids)==len(set(ids)),'Unique movement IDs '+p['id'])
 check(len({(m['type'],m['group']) for m in p['movements']})==len(ids),'Unique type/group in process '+p['id'])
 pc=collections.Counter(m['type'] for m in p['movements'])
 check(all(m['cfp']==1 and m['type'] in 'ERWX' for m in p['movements']),'Unit movement '+p['id'])
 check(pc['E']>=1 and pc['W']+pc['X']>=1,'Complete conditional process '+p['id'])
 check(all(pc[k]==p['count'][k] for k in 'ERWX'),'Per-process recount '+p['id'])
 check(sum(pc.values())==p['count']['cfp'],'Process total '+p['id'])
 counts.update(pc)
 process_rows.append({'id':p['id'],'label':p['label'],'movements':dict(pc),'cfp':sum(pc.values()),'native_function_ids':p['native_function_ids'],'assumptions':p['assumption_ids']})
cfp=sum(counts.values())
check(cfp==C['result']['conditional_expanded_subset_cfp']==350,'350 conditional CFP independently recounted')
check(len(process_rows)==25,'25 distinct functional processes')
check(len(set(x for p in process_rows for x in p['native_function_ids']))==14,'14 native functions touched')
check(C['result']['full_family_cfp'] is None,'Unknown full-family size preserved')
# Recompute candidate logical size from quantities and measured analogical anchors.
models=T['schema_inventory'];nf=sum(len(m['fields']) for m in models);nm=len(models)
check(nf==360 and nm==53,'Candidate schema inventory')
schema=[nf*T['schema_size']['field_units'][j]+nm*T['schema_size']['structure_units_per_model'][j] for j in range(3)]
check(schema==T['schema_size']['size_range'],'Schema size arithmetic')
br=[0,0,0]
for p in T['backend_blocks']:
 check(p['quantity']==len(p['blocks']),'Candidate block quantity '+p['id'])
 r=[p['quantity']*u for u in p['unit_range']]
 check(r==p['size_range'],'Block size arithmetic '+p['id'])
 br=[br[j]+r[j] for j in range(3)]
annotations=sum(p['quantity']*2 for p in T['backend_blocks'] if p['kind']=='controller')+len(T['backend_blocks'])
check(annotations==T['backend_structure']['source_annotations'],'Annotations arithmetic')
java=[br[j]+schema[j]+annotations+T['backend_structure']['scaffold_size_range'][j] for j in range(3)]
ui=T['ui']; common=sum(s['total_logical'] for s in TS['files'])
check(common==ui['common_measured_analogy_units'],'UI common measurements')
ts=[common+sum(r['quantity']*T['analogical_unit_bank']['ui_action']['range'][j] for r in ui['routes'])+nf*ui['field_rendering']['units_per_field'][j]+nm*ui['type_and_route_glue']['units_per_model'][j] for j in range(3)]
sloc=[java[j]+ts[j] for j in range(3)]
check(java==T['sizes']['Java_new_product'],'Java size reproduced')
check(ts==T['sizes']['TypeScript_new_product'],'TS size reproduced')
check(sloc==T['sizes']['new_delivered_product_logical_SLOC'],'Total size reproduced')
# Published COCOMO II equations. Scenario ratings are assumptions, coefficients are sourced.
def cocomo(ksloc,e,em=1,em_sced=1,schedule_pct=100):
 pmns=2.94*ksloc**e*em; pm=pmns*em_sced;f=.28+.2*(e-.91)
 return {'ksloc':ksloc,'exponent':e,'multiplier':em,'person_months':pm,'effort_hours':pm*152,'effort_jh':pm*152/7,'months':3.67*pmns**f*schedule_pct/100,'schedule_exponent':f}
cases=[]
for s in M['scenarios']:
 sf={k:M['scale_factors'][k][v] for k,v in s['sf'].items()}
 em={k:M['effort_multipliers'][k][v] for k,v in s['em'].items()}
 e=.91+.01*sum(sf.values())
 for label,size in zip(['bas','central','haut'],sloc):
  r=cocomo(size/1000,e,math.prod(v for k,v in em.items() if k!='SCED'),em['SCED'],M['schedule_percent'][s['em']['SCED']])
  cases.append({'scenario':s['id'],'label':s['label'],'size_variant':label,'rating_status':'hypothèse, pas mesure de l’équipe FLOW','scale_factors':sf,'multipliers':em,**r})
nom=next(c for c in cases if c['scenario']=='nominal' and c['size_variant']=='central')
example=cocomo(100,1.15)
check(abs(example['person_months']-586.61)<.01,'USC published effort example')
check(abs(example['months']-29.7)<.1,'USC published schedule example')
check(math.isclose(nom['exponent'],1.0997),'Nominal exponent')
compressed=cocomo(nom['ksloc'],nom['exponent'],em_sced=1.14,schedule_pct=85)
check(math.isclose(compressed['effort_jh']/nom['effort_jh'],1.14),'SCED effort')
check(math.isclose(compressed['months']/nom['months'],.85),'SCED schedule excludes effort compression multiplier')
for c in cases:check(math.isclose(c['effort_jh']*7,c['effort_hours']),'Hour conservation '+c['scenario']+c['size_variant'])
check(cocomo(10,nom['exponent'])['effort_jh']>cocomo(3,nom['exponent'])['effort_jh']+cocomo(7,nom['exponent'])['effort_jh'],'Aggregate size before exponent')
# COSMIC size * published ISBSG rate. The source's adjustment is NOT an AI duration.
bm=I['benchmark'];base=bm['main']['hours_per_cfp'];spread=bm['main']['spread_hours_per_cfp'];factor=bm['size_correction']['factor']
def isbsg(size):
 lo,hi=bm['size_correction']['applicable_band']
 if not lo<size<hi:raise ValueError('Outside published band; do not reuse 0.8 blindly')
 rates=[(base-spread)*factor,base*factor,(base+spread)*factor]
 return {'cfp':size,'hours_per_cfp':rates,'effort_hours':[size*r for r in rates],'effort_jh':[size*r/7 for r in rates]}
emp=isbsg(cfp)
check(isbsg(400)['effort_hours'][1]==6400,'ISBSG published 400-CFP worked example')
check(emp['effort_hours'][1]==5600 and emp['effort_jh'][1]==800,'ISBSG 350-CFP calculation')
check(all(math.isclose(h,j*7) for h,j in zip(emp['effort_hours'],emp['effort_jh'])),'ISBSG hour conservation')
# Rejection rather than arbitrary typo correction.
bad=(158,23,38);check(not bad[0]<=bad[1]<=bad[2],'Table2 P25 anomaly detected; not used')
sensitivity=[]
for s in C['sensitivity']:
 if isinstance(s['delta_cfp'],int):
  sensitivity.append({'id':s['id'],'hypothesis':s['change'],'added_cfp':s['delta_cfp'],'result':isbsg(cfp+s['delta_cfp'])})
sensitivity.append({'id':'combined_three_explicit_changes','hypothesis':'Manifeste lu + valeurs complètes du flux de changements + audit des consultations, si les trois exigences sont retenues.','added_cfp':sum(s['delta_cfp'] for s in C['sensitivity'] if isinstance(s['delta_cfp'],int)),'result':isbsg(cfp+sum(s['delta_cfp'] for s in C['sensitivity'] if isinstance(s['delta_cfp'],int)))})
alternatives=[]
for b in bm['alternatives']:
 rate=b['hours_per_cfp']*b.get('correction',1)
 alternatives.append({'id':b['id'],'hours_per_cfp_used':rate,'cfp':cfp,'effort_jh':cfp*rate/7,'cohort_n':b['cohort_n'],'scope':b['reason'],'same_empirical_source':True})
ref=load(A/'reference-source.json');check(sha(ROOT/ref['local_analysis_copy'])==ref['sha256'],'Benchmark PDF hash')
save('recompte-cosmic.json',{'unit':'CFP','scope':'Sous-ensemble conditionnel, non taille complète Master Data','total':cfp,'movements':dict(counts),'processes':process_rows,'assumptions':C['assumptions'],'open_questions':C['remaining_checklist']})
save('recalcul-taille.json',{'candidate_models':nm,'candidate_fields':nf,'java':java,'typescript':ts,'total_sloc':sloc,'schema_component':schema,'backend_component':br,'annotations':annotations,'status':'Conception cible et transposition de tailles OSS hypothétiques ; aucune mesure du futur FLOW.','full_scope':False,'unsupported_components':T['separate_not_sized']})
# Published phase/activity allocation. Preserve base effort, no duplicated additions.
D=inputs['distributions']; dist=D['cocomo'];allocation=[]
for j in range(4):check(sum(x['percent_by_phase'][j] for x in dist['activities'])==100,'Published activity column sums100 '+str(j))
check(sum(dist['phase_effort_percent_of_base'][j] for j in [1,2])==100,'COCOMO base E+C=100')
for x in dist['activities']:
 weight=sum(dist['phase_effort_percent_of_base'][j]*x['percent_by_phase'][j]/10000 for j in [1,2])
 allocation.append({'activity':x['id'],'label':x['label'],'fraction':weight,'effort_jh':nom['effort_jh']*weight,'possible_roles':x['possible_flow_roles'],'mapping_limit':x['mapping']})
check(math.isclose(sum(x['fraction'] for x in allocation),1),'Allocation fractions conserve100%')
check(math.isclose(sum(x['effort_jh'] for x in allocation),nom['effort_jh']),'Allocated JH conserve nominal COCOMO total')
check(sum(x['percent'] for x in D['isbsg']['activities'])==99,'ISBSG raw99% preserved without rescaling')
check(not D['isbsg']['apply_to_current_calculation'],'No ISBSG allocation on incompatible6-activity denominator')
check(sha(ROOT/ref['cocomo']['local_analysis_copy'])==ref['cocomo']['sha256'],'COCOMO PDF hash')
save('repartition-calculee.json',{'basis':'COCOMO nominal on candidate partial size; E+C only; default activity hypothesis','base_jh':nom['effort_jh'],'rows':allocation,'effort_by_role':None,'isbsg_allocation':None,'additions_to_total':0,'source':'repartitions-sources.json'})
R={'id':'master-data-21-results','date':'2026-10-30','status':'conditional_calculations_scope_reconciliation_failed',
 'cosmic':{'cfp':cfp,'processes':len(process_rows),'full_family_cfp':None},
 'isbsg':{'main':emp,'alternative_calculations':alternatives,'scope_sensitivity':sensitivity,'uncertainty':'Dispersion de référence publiée transférée sous hypothèses ; pas une probabilité de couverture FLOW.'},
 'cocomo':{'cases':cases,'nominal_central':nom,'uncertainty':'Sensibilité à la taille et aux notes de contexte ; aucune borne probabiliste.'},
 'comparison':{'cocomo_nominal_minus_isbsg_pct':100*(nom['effort_jh']/emp['effort_jh'][1]-1),'meaning':'Différence arithmétique de deux calculs sur des assiettes non identiques ; pas indicateur de validation.','comparable_scope':False,'independent_empirical_effort_routes':2,'cosmic_is_not_third_effort_model':True,'retained_mean':None},
 'progress':{'capabilities_touched':6,'capabilities_in_family':6,'native_functions_touched':14,'complete_capabilities_with_reconciled_calculated_effort':0,'new_external_calculation_route':1,'new_human_flow_effort_observations':0,'whole_core_reestimated':False},
 'retained':I['outcome_policy'],'active_model_changed':False,'no_ai_task_duration_inputs':True,'checks':checks,
 'source_hashes':{str((A/v).resolve().relative_to(ROOT)).replace('\\','/'):sha((A/v).resolve()) for v in I['sources'].values()},
 'input_sha256':sha(A/'entrees.json'),'calculator_sha256':sha(Path(__file__))}
save('resultats.json',R)
print(json.dumps({'cfp':cfp,'isbsg_jh':emp['effort_jh'],'cocomo_nominal_jh':nom['effort_jh'],'cocomo_months':nom['months'],'gap_arithmetic_pct':R['comparison']['cocomo_nominal_minus_isbsg_pct'],'checks':len(checks),'full_family_jh':None},ensure_ascii=False))
