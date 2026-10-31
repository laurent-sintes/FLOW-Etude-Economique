"""Four native Ownership estimates from frozen sizing assumptions and canonical rules."""
from pathlib import Path
from collections import Counter
import hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
import yaml
from estimation_calculation import formula,alignment,rounded
from model_context import model_session
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def verify_inputs():
 d=read('inputs.json');f=read('input-freeze.json')
 for name,key in [('inputs.json','input_sha256'),('hypotheses.json','hypotheses_sha256'),('cosmic.json','cosmic_sha256')]:assert sha(OUT/name)==f[key],name
 for p,h in d['input_hashes'].items():assert sha(ROOT/p)==h,p
 for p,h in d['raw_source_hashes'].items():assert sha(ROOT/p)==h,p
 for p,h in d['protected_active_inputs'].items():assert sha(ROOT/p)==h,p
 return d

def sizes(d,p,attribution='central',modules='central',override=None,w=1):
 h=d['hypotheses'];bank=d['banks'][p][attribution];template=d['schema_templates'][p];override=override or {}
 blocks=[];program=declarative=0
 for module in h['modules']:
  k=module['id'];fraction=override.get(k,module[modules])
  behavior=bank[module['analogue']]['program_units']
  scaffold=d['new_module_scaffolding'][p]['program_units_per_new_service_module']
  pu=formula('module_analogy',reference_units=behavior,fraction=fraction,scaffold_units=scaffold)
  du=0;models=[]
  for sc in h['schemas']:
   if sc['package']!=k:continue
   n=len(sc['fields']);view=int(sc['view'])
   model_p=n*template['program_per_field']+template.get('program_per_new_model',0)
   model_d=n*template['declarations_per_field']+template['per_new_model']+view*(n*template['view_field']+template['view_model'])
   pu+=model_p;du+=model_d
   models.append(dict(name=sc['name'],fields=n,view=bool(view),program_units=model_p,declarative_units=model_d))
  units=formula('equivalent_size',new_program=pu,new_declarative=du,w=w,AAM=0,reused_program=0,reused_declarative=0)
  blocks.append(dict(id=k,name=module['name'],analogue=module['analogue'],analogue_units=behavior,
   fraction=fraction,new_behavior_units=behavior*fraction,scaffold_program_units=scaffold,models=models,
   program_units=pu,declarative_units=du,equivalent_units=units,hypothesis=module['basis']))
  program+=pu;declarative+=du
 config=sum(h['configuration'].values());declarative+=config
 total=formula('equivalent_size',new_program=program,new_declarative=declarative,w=w,AAM=0,reused_program=0,reused_declarative=0)
 return dict(program_units=program,declarative_units=declarative,configuration_units=config,equivalent_units=total,blocks=blocks,
  schema_count=len(h['schemas']),specific_fields=sum(len(s['fields']) for s in h['schemas']),declarative_weight=w)

def calculate(d,p,attribution='central',modules='central',override=None,w=1,pers=1,prex=1):
 s=sizes(d,p,attribution,modules,override,w);c=d['cocomo']
 E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum']);F=formula('schedule_exponent',D=c['D'],E=E,B=c['B'])
 total=formula('cocomo_effort',A=c['A'],KSLOC=s['equivalent_units']/1000,E=E,EM=c['other_EM']*pers*prex,SCED=c['SCED'],
  month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor'])
 months=formula('cocomo_schedule',C=c['C'],JH=total,effort_phase_factor=c['effort_phase_factor'],day_hours=c['day_hours'],month_hours=c['month_hours'],SCED=c['SCED'],F=F,schedule_phase_factor=c['schedule_phase_factor'])
 allocation=[dict(id=b['id'],name=b['name'],equivalent_units=b['equivalent_units'],allocated_jh=total*b['equivalent_units']/s['equivalent_units']) for b in s['blocks']]
 allocation.append(dict(id='configuration',name='Configurations de la propriété',equivalent_units=w*s['configuration_units'],allocated_jh=total*w*s['configuration_units']/s['equivalent_units']))
 assert math.isclose(sum(a['allocated_jh'] for a in allocation),total)
 return dict(id=p,label=d['native_reference_labels'][p],jh=total,rounded_jh=rounded(total,d['hypotheses']['rounding_jh']),
  total_equivalent_KSLOC=s['equivalent_units']/1000,E=E,F=F,EM=c['other_EM']*pers*prex,
  schedule_months=months,detail=s,allocation=allocation)

def cosmic_count(d):
 cosmic=read('cosmic.json')
 refinement=read('cosmic-refinement.json');review_freeze=read('refinement-freeze.json')
 assert sha(OUT/'cosmic-refinement.json')==review_freeze['cosmic_refinement_sha256']
 assert sha(OUT/refinement['base'])==refinement['base_sha256']
 cosmic['groups']=[refinement['updated_group'] if g['id']=='DETERMINATION' else g for g in cosmic['groups']]+[refinement['group']]
 for addition in refinement['add_movements']:
  process=next(p for p in cosmic['processes'] if p['id']==addition['process'])
  process['movements'].append(dict(id=addition['process']+'-'+addition['type']+'-'+addition['group'],type=addition['type'],group=addition['group'],cfp=1))
 groups={g['id'] for g in cosmic['groups']};assert len(groups)==len(cosmic['groups'])
 seen=set();pids=set();totals=Counter();counts=[]
 for p in cosmic['processes']:
  assert p['id'] not in pids and p['functional_user'] and p['trigger'];pids.add(p['id'])
  counts_p=Counter();types=set()
  for m in p['movements']:
   key=m['type'],m['group']
   assert m['id'] not in seen and key not in types and m['group'] in groups and m['type'] in 'ERWX' and m['cfp']==1
   seen.add(m['id']);types.add(key);counts_p[m['type']]+=1
  assert counts_p['E']>=1 and counts_p['W']+counts_p['X']>=1
  counts.append(dict(id=p['id'],label=p['label'],**{k:counts_p[k] for k in 'ERWX'},CFP=sum(counts_p.values())))
  totals.update(counts_p)
 cfp=sum(totals.values());h=d['hypotheses']['COSMIC_policy']
 source=json.loads((ROOT/'audits/2026-10-30-master-data-calcul/entrees.json').read_text(encoding='utf-8-sig'))
 assert source['benchmark']['main']['hours_per_cfp']==h['productivity_hours_per_CFP'] and source['units']['jh_hours']==h['day_hours']
 jh=formula('cosmic_effort',CFP=cfp,hours_per_CFP=h['productivity_hours_per_CFP'],factor=h['factor'],day_hours=h['day_hours'])
 return dict(CFP=cfp,processes=len(pids),groups=len(groups),movements=dict(totals),process_counts=counts,
  hours_per_CFP=h['productivity_hours_per_CFP'],factor=h['factor'],day_hours=h['day_hours'],jh=jh,
  published_size_factor_if_independent_50_100_CFP=1.1 if 50<=cfp<100 else None,
  productivity_calibrated_to_ownership=False,boundary_and_activity_limits=h,original_CFP_before_group_review=76,group_refinement=refinement,benchmark_cohort='Java multi-plateforme/PC historique ; pas calibration des écosystèmes Python natifs',native_Python_productivity_calibrated=False)

def main():
 d=verify_inputs();h=d['hypotheses'];rows=[calculate(d,p) for p in h['native_references']]
 functional=cosmic_count(d);phases=d['activities']['phase_effort_percent_of_base']
 for r in rows:
  r['activities']=[]
  for a in d['activities']['activities']:
   share=sum(x*y for x,y in zip(phases,a['percent_by_phase']))/100/sum(phases)
   r['activities'].append(dict(id=a['id'],label=a['label'],jh=r['jh']*share,published_phase_percent=a['percent_by_phase']))
  assert math.isclose(sum(a['jh'] for a in r['activities']),r['jh'])
  r['alignment_COSMIC']=alignment(functional['jh'],r['jh'])
  r['implied_hours_per_CFP']=formula('implied_productivity',JH=r['jh'],day_hours=d['cocomo']['day_hours'],CFP=functional['CFP'])
  cases=[
   ('attribution-des-analogues',dict(attribution='lower'),dict(attribution='upper'),'Parts natives des chaînes de référence, sans modification des budgets Master Data et Stock.'),
   ('volume-des-six-modules',dict(modules='lower'),dict(modules='upper'),'Six fractions modifiées ensemble ; schémas et structures fixes. Une seule famille d’hypothèses, pas intervalle probabiliste.'),
   ('registre-et-deux-dates',dict(override={k['id']:k['lower'] for k in h['modules'] if k['id'] in ('OWN-F04','OWN-F05')}),
     dict(override={k['id']:k['upper'] for k in h['modules'] if k['id'] in ('OWN-F04','OWN-F05')}),'Volumes du nouveau registre et des corrections/lectures aux deux dates, uniquement.'),
   ('poids-declaratif',dict(w=.5),dict(w=2),'Convention de poids des modèles et vues, comme Stock.'),
   ('capacite-equipe',dict(pers=.83),dict(pers=1.26),'Sensibilité PERS héritée des conventions de l’étude, pas observation d’équipe.'),
   ('experience-ecosysteme',dict(prex=.87),dict(prex=1.12),'Sensibilité PREX, équipe nominale au point de comparaison.')]
  r['sensitivities']=[]
  for id,lo,hi,note in cases:
   low=calculate(d,r['id'],**lo)['jh'];high=calculate(d,r['id'],**hi)['jh']
   r['sensitivities'].append(dict(id=id,lower_jh=low,upper_jh=high,lower_change_jh=low-r['jh'],upper_change_jh=high-r['jh'],note=note,not_additive=True))
 anchor=next(r for r in rows if r['id']==h['selected_java_reference'])
 for r in rows:r['alignment_vs_java_native']=alignment(r['jh'],anchor['jh'])
 spread=formula('spread',maximum=max(r['jh'] for r in rows),minimum=min(r['jh'] for r in rows))
 retained=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))['units']
 assert [(u['total_jh'],u['months']) for u in retained]==[(1500,17),(340,10)]
 cumulative=sum(u['total_jh'] for u in retained)
 result=dict(id=h['id'],status='quatre_estimations_natives_conditionnelles_non_adoptees',
  freeze=read('input-freeze.json'),rows=rows,functional_control=functional,
  dispersion=dict(jh=spread,pct_of_java_reference=spread/anchor['jh']*100,reference=anchor['jh'],not_confidence=True,
   note='Hypothèses de taille et COCOMO partagées, proxy de code non calibré entre langages. Des analogues Java plus compacts produisent une estimation plus basse, pas une preuve de meilleure productivité.'),
  cumulative=dict(retained_gross_jh=cumulative,Master_Data_retained_jh=1500,Stock_retained_jh=340,ownership_adopted_jh=None,
   isolated_java_native_extension_rounded_jh=anchor['rounded_jh'],
   arithmetic_java_candidate_if_adopted_jh=cumulative+anchor['rounded_jh'],
   candidate_status='Addition indicative seulement ; aucune estimation Flow/Spring consolidée ou nouvelle adoption dans cette itération.',
   schedules_are_not_added=True,integrated_core_estimate=False),
  progress=dict(total_capabilities=88,capabilities_studied=16,capabilities_with_retained_or_proposed_estimate=16,
   proposed_or_retained_pct=100*16/88,retained_capabilities=14,retained_pct=100*14/88,
   new_capabilities_estimated=2,new_capabilities_adopted=0,remaining_to_estimate=72,remaining_to_adopt=74,
   functional_scope='BC-014 et BC-015 regroupées au niveau de la Business Area ; pas ventilation artificielle par capacité.'),
  conclusions=dict(calculations_now_available=True,effort_is_modelled_not_observed=True,
   uncertainty_quantified_statistically=False,uncertainty_progress='Les fractions de code, données et écarts sont calculables ; leur justesse et la productivité Flow restent des hypothèses.',
   next_iteration_worthwhile=True,
   next_iteration_focus='Une consolidation ciblée Java/Spring doit examiner si les chaînes Java constituent une analogie suffisante pour le registre autonome aux deux dates et expliquer le désaccord avec les trois autres références et COSMIC. Aucun nouvel inventaire général.',
   permanent_loop_guard='Réviser uniquement une hypothèse de volume ou de périmètre identifiable. Sans nouvelle base, conserver le désaccord et décider au niveau de l’étude ; ne pas ajuster pour faire converger.'),
  activity_reference=d['activities'],active_model_changed=False,application_changed=False,skill_changed=False,adoption=False)
 save('results.json',result)
 for p,h in d['protected_active_inputs'].items():assert sha(ROOT/p)==h
 print(json.dumps(dict(rows=[dict(id=r['id'],jh=r['jh'],rounded_jh=r['rounded_jh'],equivalent_KSLOC=r['total_equivalent_KSLOC'],schedule_months=r['schedule_months'],
  COSMIC_gap_jh=r['alignment_COSMIC']['gap_jh'],COSMIC_gap_pct=r['alignment_COSMIC']['gap_pct'],
  sensitivities=r['sensitivities']) for r in rows],functional= dict(CFP=functional['CFP'],processes=functional['processes'],groups=functional['groups'],movements=functional['movements'],jh=functional['jh']),
  cumulative=result['cumulative']),ensure_ascii=False,indent=2))
if __name__=='__main__':
 with model_session():main()
