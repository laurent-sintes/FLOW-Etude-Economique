"""Calculate the proposed common mechanisms only; owners fund once, consumers fund zero reconstruction."""
from pathlib import Path
from collections import defaultdict
import json,hashlib,math,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
from model_context import model_session
from estimation_calculation import formula,rounded,alignment
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 freeze=read(OUT/'economic-input-freeze.json')
 for name,key in [('specification.json','specification_sha256'),('measurements.json','measurements_sha256'),('funding.json','funding_sha256'),('cosmic.json','cosmic_sha256')]:
  assert sha(OUT/name)==freeze[key],name
 m=read(OUT/'measurements.json');s=m['specification'];funding=read(OUT/'funding.json');cf=read(OUT/'cosmic.json')
 native=read(ROOT/'audits/2026-10-30-propriete-stock-calcul-02/inputs.json');c=native['cocomo']
 distribution=read(ROOT/s['activity_ref'])['cocomo'];alloc=read(ROOT/s['allocation_ref'])['activity_role_weights']
 labels={r['id']:r['label'] for r in read(OUT/'baseline.json')['units'][0]['roles']}
 E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum']);F=formula('schedule_exponent',D=c['D'],E=E,B=c['B'])
 owners=list(dict.fromkeys(x['owner'] for x in s['mechanisms']));byowner={};subtotals={p:0 for p in ('erpnext','odoo','tryton','axelor')}
 for owner in owners:
  rows=[]
  for p in subtotals:
   parts=[]
   for mechanism in s['mechanisms']:
    if mechanism['owner']!=owner:continue
    id=mechanism['id'];t=native['schema_templates'][p];scaffold=native['new_module_scaffolding'][p]['program_units_per_new_service_module']
    models=[]
    for schema in mechanism['schemas']:
     name,fields=schema.split(':',1);n=len(fields.split(','))
     pu=n*t['program_per_field']+t.get('program_per_new_model',0)
     du=n*t['declarations_per_field']+t['per_new_model']+n*t['view_field']+t['view_model']
     models.append(dict(name=name,fields=fields.split(','),program_units=pu,declarative_units=du))
    new=formula('module_analogy',reference_units=m['bank_program_units'][id][p],fraction=mechanism['fraction'],scaffold_units=scaffold)
    schemaunits=sum(x['program_units']+x['declarative_units'] for x in models)
    base=m['base_units_owned_once'][id][p]
    parts.append(dict(mechanism=id,base_units=base,new_behavior_and_scaffold_units=new,extension_schema_units=schemaunits,
      equivalent_units=base+new+schemaunits,models=models,analogue_units=m['bank_program_units'][id][p],new_fraction=mechanism['fraction']))
   total=sum(x['equivalent_units'] for x in parts);base=sum(x['base_units'] for x in parts)
   def effort(units):return 0 if not units else formula('cocomo_effort',A=c['A'],KSLOC=units/1000,E=E,EM=c['other_EM'],SCED=c['SCED'],month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor'])
   jh=effort(total);common=effort(base)
   rows.append(dict(id=p,equivalent_units=total,measured_base_units=base,modelled_new_units=total-base,
    base_analogy_jh=common,new_complements_marginal_jh=jh-common,jh=jh,rounded_jh=rounded(jh,10),parts=parts))
  java=next(r for r in rows if r['id']=='axelor');chosen=java['rounded_jh'];roles=dict.fromkeys(labels,0.);activities=[]
  for a in distribution['activities']:
   phases=distribution['phase_effort_percent_of_base'];share=sum(x*y for x,y in zip(phases,a['percent_by_phase']))/sum(phases)/100
   jh=chosen*share;activities.append(dict(id=a['id'],jh=jh,published_percent_by_phase=a['percent_by_phase'],proposed_role_weights=alloc[a['id']]))
   for key,w in alloc[a['id']].items():roles[key]+=jh*w
  assigned={k:math.floor(v) for k,v in roles.items()};order=sorted(roles,key=lambda k:(-(roles[k]-math.floor(roles[k])),k))
  for key in order[:round(chosen-sum(assigned.values()))]:assigned[key]+=1
  assert sum(assigned.values())==chosen
  months=formula('cocomo_schedule',C=c['C'],JH=chosen,effort_phase_factor=c['effort_phase_factor'],day_hours=c['day_hours'],month_hours=c['month_hours'],SCED=c['SCED'],F=F,schedule_phase_factor=c['schedule_phase_factor']) if chosen else None
  check=formula('cosmic_effort',CFP=cf[owner]['CFP'],hours_per_CFP=20,factor=1,day_hours=7)
  for row in rows:row['alignment_vs_java']=alignment(row['jh'],java['jh']);subtotals[row['id']]+=row['rounded_jh']
  byowner[owner]=dict(owner=owner,scope='Mécanismes communs uniquement, pas toute la famille.',status='proposition_conditionnelle_non_adoptee',
   rows=rows,java_common_jh=chosen,java_raw_jh=java['jh'],roles=[dict(id=k,label=labels[k],jh=v) for k,v in assigned.items()],
   role_status='Clés Stock proposées pour les travaux communs ; révision des rôles spécialisés et des équipes encore nécessaire.',
   local_nominal_months=rounded(months,1) if months else None,raw_months=months,
   schedule_status='Délai nominal du seul lot commun, sans calendrier global ni engagement de disponibilité.',
   functional=dict(CFP=cf[owner]['CFP'],jh=check,alignment_vs_java=alignment(check,java['jh']),
    scope='Contrôle du seul composant commun ; ne pas additionner les CFP entre propriétaires.',not_confidence=True),
   mechanism_allocations=[dict(id=x['mechanism'],equivalent_units=x['equivalent_units'],allocated_jh=chosen*x['equivalent_units']/java['equivalent_units']) for x in java['parts']])
 candidate=subtotals['axelor'];perfamily=[]
 for family in s['scope_families']:
  owned=[m for m in s['mechanisms'] if m['owner']==family]
  consumed=[q for q in funding['claims'] if q['family']==family and q['mode']!='proposed_funding']
  perfamily.append(dict(family=family,funded_here=[m['id'] for m in owned],common_funding_jh=byowner[family]['java_common_jh'] if family in byowner else 0,
   consumed=consumed,additional_common_reconstruction_jh=0,specific_family_work_jh=None,specific_family_scope=s['outside_common_scope'][family],
   complete_family_estimate_jh=None,note='Zéro de reconstruction commune signifie consommation d’un financement identifié ; les compléments propres restent inconnus, pas gratuits.'))
 result=dict(id=s['id'],status='iteration_4_common_work_funding_proposal',owners=byowner,families=perfamily,
  convention=dict(cocomo=c,exponent=E,logical_metric=s['metrics_ref'],declarative_weight=1,rounding_jh=10,
   no_global_AI_discount=True,no_extra_coordination=True),
  common_native_subtotals=subtotals,common_java_subtotal_jh=candidate,
  cumulative=dict(adopted_jh=1940,proposed_common_additional_jh=candidate,adopted_plus_proposed_common_only_jh=1940+candidate,
   proposed_value_is_not_adopted=True,global_core_estimate_jh=None,
   reason='Le sous-total porte sur onze mécanismes communs à six propriétaires ; compléments locaux et autres familles non inclus.',
   integrated_COCOMO=False,schedules_added=False),
  progress=dict(total_capabilities=88,adopted_capabilities=16,adopted_pct=16/88*100,
    campaign_capabilities_reviewed=88,iteration4_families=len(s['scope_families']),
    iteration4_capabilities_touched=sum(len(read(ROOT/'audits/2026-10-30-familles-restantes'/family/'iteration-3.json')['scope']) for family in s['scope_families']),
    new_complete_capabilities_adopted=0,shared_mechanisms_with_one_owner=len(s['mechanisms'])),
  limitations=['Les nouveaux volumes de code sont supposés par analogie et non observés sur Flow.',
   'L’analogue BPM Axelor Studio appelle Camunda ; la transposition des fonctions communes vers Flowable est une hypothèse, pas une compatibilité démontrée.',
   'La composition réactive avancée, les variantes métier et les garanties de service restent hors du sous-total commun.',
   'Les bibliothèques et services déjà disponibles sont consommés ; leur reconstruction n’est pas financée.',
   'Le registre métier de Case aux deux dates reste dimensionné par analogie, sans équivalent natif complet démontré.'],
  active_model_changed=False,adoption=False)
 save('results.json',result)
 print(json.dumps(dict(common_by_owner={k:v['java_common_jh'] for k,v in byowner.items()},four_native_common_subtotals=subtotals,cumulative=result['cumulative'],progress=result['progress']),ensure_ascii=False,indent=2))
if __name__=='__main__':
 with model_session():main()
