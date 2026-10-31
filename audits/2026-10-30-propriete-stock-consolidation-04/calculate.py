"""Consolidation proposée de la propriété : référence Java inchangée, rôles et délai traçables."""
from pathlib import Path
from collections import defaultdict
import hashlib,importlib.util,json,math,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
import yaml
from model_context import model_session
from estimation_calculation import formula,rounded,alignment
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def verify_inputs(d):
 assert sha(OUT/'inputs.json')==read(OUT/'input-freeze.json')['inputs_sha256']
 for key in ['input_hashes','protected_active_inputs']:
  for p,h in d[key].items():assert sha(ROOT/p)==h,p
 native=read(ROOT/'audits/2026-10-30-propriete-stock-calcul-02/inputs.json')
 review=read(ROOT/'audits/2026-10-30-propriete-stock-java-03/inputs.json')
 raw=dict(native['raw_source_hashes'])
 for row in review['code']:
  if row['root_path'] in raw:assert raw[row['root_path']]==row['sha256']
  raw[row['root_path']]=row['sha256']
 for p,h in raw.items():assert sha(ROOT/p)==h,p
 return raw
def main():
 d=read(OUT/'inputs.json');raw=verify_inputs(d)
 prior=ROOT/'audits/2026-10-30-propriete-stock-calcul-02'
 native=read(prior/'inputs.json');old=read(prior/'results.json')
 spec=importlib.util.spec_from_file_location('ownership_native02',prior/'calculate.py');calc=importlib.util.module_from_spec(spec);spec.loader.exec_module(calc)
 reconstructed=calc.calculate(native,d['selected_reference'])
 original=next(r for r in old['rows'] if r['id']==d['selected_reference'])
 assert reconstructed['detail']==original['detail'] and math.isclose(reconstructed['jh'],original['jh'])
 total=rounded(reconstructed['jh'],d['rounding_jh'])
 c=native['cocomo'];E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum']);F=formula('schedule_exponent',D=c['D'],E=E,B=c['B'])
 months=formula('cocomo_schedule',C=c['C'],JH=total,effort_phase_factor=c['effort_phase_factor'],
  day_hours=c['day_hours'],month_hours=c['month_hours'],SCED=c['SCED'],F=F,schedule_phase_factor=c['schedule_phase_factor'])
 planning=rounded(months,d['schedule_rounding_months'])
 decisions=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))['units']
 assert [(u['id'],u['total_jh'],u['months']) for u in decisions]==[('master-data-java-spring',1500,17),('stock-java-spring',340,10)]
 labels={r['id']:r['label'] for r in decisions[0]['roles']};active_roles=defaultdict(float)
 for u in decisions:
  for r in u['roles']:active_roles[r['id']]+=r['jh']
 distributions=read(ROOT/'audits/2026-10-30-master-data-calcul/repartitions-sources.json')
 a=distributions['cocomo'];phases=a['phase_effort_percent_of_base'];activities=[];raw_roles={r:0. for r in labels};cells=[]
 assert set(d['activity_role_weights'])=={x['id'] for x in a['activities']}
 for act in a['activities']:
  weights=d['activity_role_weights'][act['id']]
  assert set(weights)<=set(act['possible_flow_roles']) and math.isclose(sum(weights.values()),1)
  share=sum(p*q for p,q in zip(phases,act['percent_by_phase']))/sum(phases)/100
  value=total*share
  activities.append(dict(id=act['id'],label=act['label'],jh=value,share=share,
   published_percent_by_phase=act['percent_by_phase'],role_weights=weights,
   role_rationale=d['activity_role_rationales'][act['id']]))
  for role,w in weights.items():
   raw_roles[role]+=value*w;cells.append(dict(activity=act['id'],role=role,weight=w,jh=value*w))
 assert math.isclose(sum(raw_roles.values()),total)
 step=d['role_rounding_jh'];assigned={r:math.floor(v/step)*step for r,v in raw_roles.items()}
 order=sorted(raw_roles,key=lambda k:(-(raw_roles[k]/step-math.floor(raw_roles[k]/step)),k))
 for role in order[:round((total-sum(assigned.values()))/step)]:assigned[role]+=step
 assert sum(assigned.values())==total
 capacity=yaml.safe_load((ROOT/'source/deploiement-groupe.yaml').read_text(encoding='utf-8'))['calendrier_autonome']['capacite']['jours_productifs_etp_mois']
 roles=[dict(id=k,label=labels[k],unrounded_jh=raw_roles[k],jh=assigned[k],already_adopted_jh=active_roles[k],
  cumulative_proposed_jh=active_roles[k]+assigned[k]) for k in labels]
 functional=old['functional_control'];assert functional['CFP']==80 and math.isclose(functional['jh'],80*20/7)
 mechanisms=yaml.safe_load((ROOT/'source/calculs-estimation-core.yaml').read_text(encoding='utf-8'))['mechanisms']
 funding=[dict(id=m['id'],label=m['label'],funding_owner=m['funding_owner']) for m in mechanisms]
 module_alloc=[dict(id=x['id'],name=x['name'],equivalent_units=x['equivalent_units'],
  allocated_jh_from_raw_calculation=x['allocated_jh'],allocated_jh_from_proposed_total=x['allocated_jh']/reconstructed['jh']*total) for x in original['allocation']]
 # These are allocations of the one nonlinear calculation, never separate summed COCOMO estimates.
 assert math.isclose(sum(x['allocated_jh_from_proposed_total'] for x in module_alloc),total)
 adopted=sum(u['total_jh'] for u in decisions)
 isbsg=distributions['isbsg']
 out=dict(id=d['id'],status=d['status'],scope=d['scope'],primary_method=d['primary_method'],selected_reference=d['selected_reference'],
  proposed_jh=total,raw_reference_jh=reconstructed['jh'],rounding_delta_jh=total-reconstructed['jh'],
  selection_rationale=d['selection_rationale'],decision_policy=d['decision_policy'],
  formula_rules_ref='source/fondamentaux.yaml#estimation_model',
  size=dict(equivalent_units=reconstructed['detail']['equivalent_units'],equivalent_KSLOC=reconstructed['total_equivalent_KSLOC'],
   convention='Proxy logique de code après réutilisation, non calibré en SLOC physiques. Les fractions de nouveaux modules sont supposées.',
   program_units=reconstructed['detail']['program_units'],declarative_units=reconstructed['detail']['declarative_units'],
   E=E,F=F,parameters=c,source_calculation='audits/2026-10-30-propriete-stock-calcul-02/results.json#rows.axelor'),
  native_comparisons=[dict(id=r['id'],label=r['label'],jh=r['jh'],rounded_jh=r['rounded_jh'],
   alignment_vs_java=alignment(r['jh'],original['jh'])) for r in old['rows']],
  module_allocation=module_alloc,module_allocation_is_not_independent_effort=True,
  activities=activities,activity_to_role=cells,roles=roles,
  role_allocation_status=d['role_policy'],role_rounding_jh=step,activity_reference=a,
  published_ISBSG_activity_distribution=dict(source=isbsg['source'],table=isbsg['table'],pages=isbsg['pages'],
   population=isbsg['population'],activities=isbsg['activities'],sum_percent=isbsg['sum_percent'],
   applied_to_roles=False,reason='Autre cohorte et assiette : ne pas appliquer ces parts aux 229 JH. Conservation des données publiées, sans renormalisation.'),
  schedule=dict(proposed_months=planning,calculated_months_on_proposed_jh=months,
   calculated_months_on_raw_jh=original['schedule_months'],source_rule='cocomo_schedule',
   parameters=dict(C=c['C'],JH=total,effort_phase_factor=c['effort_phase_factor'],day_hours=c['day_hours'],
    month_hours=c['month_hours'],SCED=c['SCED'],F=F,schedule_phase_factor=c['schedule_phase_factor']),
   productive_jh_per_person_month=capacity,average_people=formula('average_team',JH=total,months=planning,capacity=capacity),
   condition=d['schedule_policy'],allocation_is_not_nine_fulltime_posts=True,combined_core_schedule=None),
  crosscheck=dict(method='COSMIC × ISBSG',CFP=80,hours_per_CFP=20,factor=1,day_hours=7,jh=functional['jh'],
   alignment_vs_unrounded_java=alignment(functional['jh'],reconstructed['jh']),
   alignment_vs_proposed_total=alignment(functional['jh'],total),
   implied_java_hours_per_CFP=reconstructed['jh']*7/80,
   observed_Flow_productivity=None,
   explanation='80 × 20 ÷ 7 = 228,57 JH. Le rendement historique ne reflète pas de façon calibrée la réutilisation de cette famille. La taille de code COCOMO reste une hypothèse. Aucune correction chiffrée des deux biais ne peut être démontrée.',
   count_unchanged=True,no_average_of_methods=True,no_confidence_score=True),
  assumptions=d['assumptions'],sensitivity_pairs=original['sensitivities'],
  sensitivity_note='Variations une famille d hypothèses à la fois, non additives ; pas enveloppe budgétaire ni intervalle probabiliste. Écarts comparés aux 98,9157 JH non arrondis.',
  reuse_funding=dict(policy=d['funding_policy'],existing_owners=funding,additional_generic_foundation_construction_jh=0,
   zero_means_already_funded=True,new_ownership_modules=[m['id'] for m in native['hypotheses']['modules']],
   family_specific_adaptations_included=True),
  scope_exclusions=['Règles et clauses spécifiques Beaumanoir, négociation de contrats et langage universel de règles.',
   'Comptabilité financière, valorisation et facturation.','Nouveau moteur de stock physique, réservation ou orchestration.',
   'Moteur temporel universel de toute la plateforme.','Déploiements Groupe, migration générale, exploitation et maintenance annuelles.'],
  cumulative=dict(adopted_jh=adopted,proposed_ownership_jh=total,proposed_java_cumulative_jh=adopted+total,
   adopted_families=[dict(id=u['id'],jh=u['total_jh'],months=u['months']) for u in decisions],
   proposed_role_sum=sum(x['cumulative_proposed_jh'] for x in roles),combined_months=None,
   schedules_added=False,integrated_cocomo_estimate=False,active_model_changed=False),
  progress=dict(total_capabilities=88,studied_and_with_proposed_or_adopted_estimate=16,studied_pct=100*16/88,
   adopted=14,adopted_pct=100*14/88,if_proposal_adopted=16,remaining_to_estimate=72,
   new_capabilities_studied=0,new_capabilities_adopted=0),
  conclusion=dict(proposed_for_opportunity_study=True,predictive_validation=False,statistical_uncertainty=None,
   genuine_progress='Proposition décisionnelle à 100 JH avec activités, neuf rôles et délai reproduits ; le désaccord avec le contrôle reste visible.',
   uncertainty_reduced=False,
   next_general_source_iteration_worthwhile=False,
   recommendation='Passer à la décision sur cette base, puis à une autre famille. Réouvrir uniquement si une hypothèse de périmètre, de patrimoine disponible, de volume ou d équipe change.',
   no_new_adoption=True),verified_raw_source_files=len(raw),active_model_changed=False,application_changed=False)
 save('results.json',out)
 (OUT/'bilan.yaml').write_text(yaml.safe_dump(out,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
 print(json.dumps(dict(proposed_jh=total,roles={r['id']:r['jh'] for r in roles},months=months,proposed_months=planning,
  cumulative=out['cumulative'],crosscheck=out['crosscheck'],raw_source_files=len(raw)),ensure_ascii=False,indent=2))
if __name__=='__main__':
 with model_session():main()
