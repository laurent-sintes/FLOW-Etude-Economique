"""Iteration 3: coherent component size, direct Java delegation review and conditional consolidation."""
from pathlib import Path
from collections import defaultdict
import hashlib,importlib.util,json,math,re,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
from model_context import model_session
from estimation_calculation import formula,rounded
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=importlib.util.spec_from_file_location('support2',OUT/'iteration2.py');support=importlib.util.module_from_spec(s);s.loader.exec_module(support)
MANUAL={
 'orders':[('axelor','SaleOrderLineServiceImpl.java'),('erpnext','erpnext/controllers/selling_controller.py'),('erpnext','erpnext/controllers/buying_controller.py'),('odoo','addons/sale/models/sale_order_line.py'),('odoo','addons/purchase/models/purchase_order_line.py')],
 'master-plan':[('axelor','MrpLineServiceImpl.java')],
 'backlog':[('axelor','ReservedQtyServiceImpl.java')],
 'workflow':[('platform','axelor-core/src/main/java/com/axelor/quartz/SchedulerProvider.java')],
 'supervision':[('platform','axelor-core/src/main/java/com/axelor/db/audit/AuditTracker.java')]
}
RESERVED={'optimization','promising','service-planning','coordination','customs','workflow','supervision','intelligence'}
def additions(f,plan,previous):
 seen={(x['repo'],x['path']) for x in previous if not x.get('missing')};new=[];review=[]
 def add(repo,path,reason):
  if '/' not in path:
   choices=list((ROOT/plan['repos'][repo]['root']).rglob(path))
   if len(choices)!=1:review.append(dict(target=path,status='unresolved_or_ambiguous',matches=len(choices)));return
   path=choices[0].relative_to(ROOT/plan['repos'][repo]['root']).as_posix()
  if (repo,path) in seen:return
  got=support.source(dict(repo=repo,path=path),plan)
  if got.get('missing'):review.append(dict(target=path,status='missing'));return
  got['addition_reason']=reason;new.append(got);seen.add((repo,got['path']))
 for repo,path in MANUAL.get(f['slug'],[]):add(repo,path,'Complément de composant métier motivé par analyse-2.')
 # Resolve only direct typed service calls in the largest selected Java methods.
 inp=read(OUT/f['slug']/'entrees-2.json')
 picked=sorted([x for x in inp['source_selection'] if x['product']=='axelor'],key=lambda x:-x['program_units'])[:2]
 for selection in picked:
  owner=next((x for x in previous if x.get('repo')==selection['repo'] and x.get('path')==selection['path']),None)
  if owner is None:continue
  text=(ROOT/owner['root_path']).read_text(encoding='utf-8')
  fields=dict((name,typ) for typ,name in re.findall(r'(?:protected|private|public)\s+(?:final\s+)?([A-Z]\w*(?:Service|ServiceImpl))\s+(\w+)\s*;',text))
  for field,method in sorted(set(re.findall(r'\b(\w+)\.(\w+)\s*\(',selection['source']))):
   typ=fields.get(field)
   if not typ:continue
   if re.search('AppBase|UnitConversion|Sequence|Currency|Tax|Mail|Auth|Meta',typ):
    review.append(dict(caller=selection['name'],target=typ+'.'+method,status='generic_or_excess_not_new_construction'));continue
   filename=typ if typ.endswith('Impl') else typ+'Impl'
   candidates=list((ROOT/plan['repos']['axelor']['root']).rglob(filename+'.java'))
   if len(candidates)==1:
    path=candidates[0].relative_to(ROOT/plan['repos']['axelor']['root']).as_posix()
    add('axelor',path,'Appel direct '+selection['name']+' → '+field+'.'+method)
    resolved=next((x for x in new+previous if x.get('repo')=='axelor' and x.get('path')==path),None)
    target=next((m for m in resolved.get('methods',[]) if m['name']==method),None) if resolved else None
    review.append(dict(caller=selection['name'],target=typ+'.'+method,path=path,status='callee_source_verified' if target else 'callee_method_not_resolved',
      method_excerpt=target['source'] if target else None))
   else:review.append(dict(caller=selection['name'],target=typ+'.'+method,status='unresolved_or_ambiguous',matches=len(candidates)))
 return new,review
def main():
 plan=read(OUT/'plan.json');native=read(ROOT/'audits/2026-10-30-propriete-stock-calcul-02/inputs.json')
 allocation=read(ROOT/'audits/2026-10-30-stock-consolidation-09/inputs.json')
 activities=read(ROOT/'audits/2026-10-30-master-data-calcul/repartitions-sources.json')['cocomo']
 baseline=read(OUT/'baseline.json');labels={r['id']:r['label'] for r in baseline['units'][0]['roles']}
 done=16;summary=[]
 for f in plan['families']:
  folder=OUT/f['slug'];two=read(folder/'iteration-2.json');i2=read(folder/'entrees-2.json');a2=read(folder/'analyse-2.json')
  previous=[]
  for x in i2['source_files']:
   if x.get('missing'):continue
   previous.append(dict(x,methods=support.support.symbols(ROOT/x['root_path'])))
  added,review=additions(f,plan,previous);sources=previous+added
  banks={p:0 for p in ['erpnext','odoo','tryton','axelor']};source_measures=[];seen_sources=set()
  for file in sources:
   identity=file['repo'],file['path']
   if identity in seen_sources:continue
   seen_sources.add(identity);product='erpnext' if file['repo']=='frappe' else 'axelor' if file['repo']=='platform' else file['repo']
   nodes=set()
   for method in file['methods']:
    nodes|={(n['kind'],n['start'],n['end'],n['col'],n['end_col']) for n in method['nodes']}
   banks[product]+=len(nodes)
   source_measures.append(dict(repo=file['repo'],product=product,path=file['path'],root_path=file['root_path'],sha256=file['sha256'],commit=file['commit'],
    program_units=len(nodes),nodes=[list(x) for x in sorted(nodes)],addition_reason=file.get('addition_reason'),
    measurement_scope='Union des instructions de toutes les méthodes du composant, hors champs/imports/constructeurs ; pertinence supposée appliquée séparément.'))
  frozen=dict(family=f['id'],iteration=3,analysis_2_sha256=sha(folder/'analyse-2.json'),previous_result_sha256=sha(folder/'iteration-2.json'),
   method_change='Composants métier cohérents et services directs, au lieu des seuls noms de méthodes sélectionnés.',
   unchanged_attribution=i2['attribution'],unchanged_complement_fraction=i2['new_complement_fraction'],
   native_reference_banks=banks,source_measures=source_measures,delegation_review=review,
   schema_hypotheses=i2['schemas'],COSMIC_sha256=sha(folder/'cosmic-2.json'),
   policy='Changement de mesure guidé par analyse-2, sans changer les coefficients pour atteindre un chiffre cible.')
  save(folder/'entrees-3.json',frozen);save(folder/'gel-3.json',dict(inputs_sha256=sha(folder/'entrees-3.json'),policy='Gel avant calcul des JH de l’itération 3.'))
  c=i2['cocomo'];E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum']);F=formula('schedule_exponent',D=c['D'],E=E,B=c['B']);rows=[]
  for product,bank in banks.items():
   if bank==0:rows.append(dict(id=product,jh=None,reason='Source native insuffisante.'));continue
   t=native['schema_templates'][product];scaffold=native['new_module_scaffolding'][product]['program_units_per_new_service_module']
   pu=sum(len(s['fields'])*t['program_per_field']+t.get('program_per_new_model',0) for s in i2['schemas'])
   du=sum(len(s['fields'])*t['declarations_per_field']+t['per_new_model']+len(s['fields'])*t['view_field']+t['view_model'] for s in i2['schemas'])
   base=bank*i2['attribution'];extra=bank*i2['new_complement_fraction']+scaffold+pu+du;size=base+extra
   def effort(x):return formula('cocomo_effort',A=c['A'],KSLOC=x/1000,E=E,EM=c['other_EM'],SCED=c['SCED'],month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor'])
   jh=effort(size);basejh=effort(base)
   rows.append(dict(id=product,native_analogue_units=bank,base_equivalent_units=base,complement_equivalent_units=extra,equivalent_units=size,
    common_analogy_jh=basejh,complement_marginal_jh=jh-basejh,jh=jh,rounded_jh=rounded(jh,10),not_observed_effort=True))
  java=next(x for x in rows if x['id']=='axelor');total=java.get('rounded_jh')
  weights=allocation['activity_role_weights'];raw_roles={r:0. for r in labels};activity_results=[]
  for a in activities['activities']:
   share=sum(p*q for p,q in zip(activities['phase_effort_percent_of_base'],a['percent_by_phase']))/sum(activities['phase_effort_percent_of_base'])/100
   value=(total or 0)*share;activity_results.append(dict(id=a['id'],label=a['label'],jh=value,percent_by_phase=a['percent_by_phase'],weights=weights[a['id']]))
   for role,w in weights[a['id']].items():raw_roles[role]+=value*w
  roles={k:math.floor(v) for k,v in raw_roles.items()};order=sorted(roles,key=lambda k:(-(raw_roles[k]-math.floor(raw_roles[k])),k))
  for k in order[:round((total or 0)-sum(roles.values()))]:roles[k]+=1
  assert sum(roles.values())==(total or 0)
  months=formula('cocomo_schedule',C=c['C'],JH=total,effort_phase_factor=c['effort_phase_factor'],day_hours=c['day_hours'],month_hours=c['month_hours'],SCED=c['SCED'],F=F,schedule_phase_factor=c['schedule_phase_factor']) if total else None
  control=two['functional']['jh'];gap=control-java['jh'] if java.get('jh') else None
  status='candidat_conditionnel_non_adopte' if f['slug'] not in RESERVED and total else 'ordre_de_grandeur_non_consolidable'
  done+=len(f['capabilities'])
  result=dict(family=f['id'],slug=f['slug'],iteration=3,status=status,scope=f['native_capabilities'],native_estimates=rows,
   proposed_java_jh=total if status=='candidat_conditionnel_non_adopte' else None,
   diagnostic_java_jh=java['jh'],diagnostic_rounded_jh=total,
   roles=[dict(id=k,label=labels[k],jh=roles[k]) for k in roles],
   roles_status='Répartition du diagnostic total par activités publiées COCOMO et clés d’organisation Stock proposées ; pas charge observée ni adoption.',
   activities=activity_results,activity_source_ref='audits/2026-10-30-master-data-calcul/repartitions-sources.json#cocomo',
   delay=dict(calculated_months=months,rounded_months=rounded(months,1) if months else None,
    status='Délai local nominal du diagnostic ; pas engagement ni calendrier global. Dépend des mécanismes des autres familles.'),
   functional_control=dict(**two['functional'],gap_jh=gap,gap_pct=100*gap/java['jh'] if gap is not None else None,denominator=java.get('jh'),not_confidence=True),
   measured_change=dict(java_units_iteration_2=i2['native_reference_banks']['axelor'],java_units_iteration_3=banks['axelor'],
    jh_iteration_2=next(r for r in two['rows'] if r['id']=='axelor')['jh'],jh_iteration_3=java['jh'],additional_source_files=len(added),
    resolved_direct_calls=sum(x['status']=='callee_source_verified' for x in review),remaining_delegations=sum(x['status'] in ('unresolved_or_ambiguous','callee_method_not_resolved') for x in review)),
   limits=[a2['family_specific_check'],'Les parts de pertinence et de nouveau code sont des hypothèses non calibrées.',
    'Le composant natif peut rester plus large que le périmètre Flow ; les quatre chiffres ne sont ni des charges historiques ni des validations indépendantes.',
    'Un même code peut servir d’analogue à plusieurs familles ; cela ne prouve pas à lui seul un mécanisme Flow commun ni un financement distinct.',
    'Le comptage COSMIC est proposé, sans revue humaine ni preuve d’exhaustivité.'],
   cumulative=dict(adopted_jh=1940,newly_adopted_jh=0,capabilities_reviewed=done,total_capabilities=88,reviewed_pct=100*done/88),
   next_iteration_worthwhile=True,next_iteration_reason='Audit transversal demandé : vérifier les mécanismes communs, l’exhaustivité fonctionnelle et les analogues non appariés avant une nouvelle adoption.',
   lineage=dict(iteration_1_sha256=sha(folder/'iteration-1.json'),analysis_1_sha256=sha(folder/'analyse-1.json'),iteration_2_sha256=sha(folder/'iteration-2.json'),analysis_2_sha256=sha(folder/'analyse-2.json'),inputs_3_sha256=sha(folder/'entrees-3.json')))
  save(folder/'iteration-3.json',result)
  summary.append(dict(family=f['slug'],capabilities=f['capabilities'],status=status,native={r['id']:r.get('rounded_jh') for r in rows},proposed_jh=result['proposed_java_jh'],diagnostic_jh=total,COSMIC_jh=control,months=result['delay']['rounded_months'],reviewed_capabilities=done))
  print(json.dumps(summary[-1],ensure_ascii=False))
 save(OUT/'synthese-iteration-3.json',summary)
 plan['status']='three_iterations_complete_pending_final_audit';save(OUT/'plan.json',plan)
if __name__=='__main__':
 with model_session():main()
