"""Consolidate the Stock proposal using canonical rules, with no adoption."""
from pathlib import Path
import ast,hashlib,importlib.util,itertools,json,math,re,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tmp/model-deps'),str(ROOT/'tools'),str(ROOT/'tmp/master-data-native-23/parser-deps')]
import yaml
from estimation_calculation import formula,rounded,alignment
from model_context import model_session

def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def module(name,p):
 s=importlib.util.spec_from_file_location(name,ROOT/p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 d=read(OUT.relative_to(ROOT).as_posix()+'/inputs.json')
 freeze=read(OUT.relative_to(ROOT).as_posix()+'/input-freeze.json')
 assert sha(OUT/'inputs.json')==freeze['input_sha256']
 r=read(d['native_calculation']);old=read('audits/2026-10-30-stock-opportunite-08/inputs.json')
 provenance=read('audits/2026-10-30-stock-opportunite-08/provenance.json')
 for p,h in provenance['protected'].items():assert sha(ROOT/p)==h,p
 for dep in provenance['dependencies']:assert sha(ROOT/dep['path'])==dep['sha256'],dep['path']
 md=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))
 md=next(u for u in md['units'] if u['id']=='master-data-java-spring')
 assert md['total_jh']==1500 and md['months']==17
 c=old['cocomo'];E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum'])
 F=formula('schedule_exponent',D=c['D'],E=E,B=c['B'])
 def effort(units):return formula('cocomo_effort',A=c['A'],KSLOC=units/1000,E=E,EM=c['other_EM'],SCED=c['SCED'],month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor'])
 for row in r['rows']:
  assert math.isclose(effort(row['base_equivalent_units']+row['Flow_complements_equivalent_units']),row['total_stock_jh'],rel_tol=1e-12)
 anchor=next(x for x in r['rows'] if x['id']==d['selected_reference'])
 odoo=next(x for x in r['rows'] if x['id']=='odoo')
 total=rounded(anchor['total_stock_jh'],d['rounding_jh'])
 activities_source=read('audits/2026-10-30-master-data-calcul/repartitions-sources.json')
 a=activities_source['cocomo'];phases=a['phase_effort_percent_of_base']
 role_labels={x['id']:x['label'] for x in md['roles']};raw_roles={k:0. for k in role_labels}
 activities=[];cells=[]
 assert set(d['activity_role_weights'])=={x['id'] for x in a['activities']}
 for act in a['activities']:
  weights=d['activity_role_weights'][act['id']]
  assert set(weights)<=set(act['possible_flow_roles']) and math.isclose(sum(weights.values()),1)
  share=sum(x*y for x,y in zip(phases,act['percent_by_phase']))/100/sum(phases)
  jh=total*share
  activities.append(dict(id=act['id'],label=act['label'],jh=jh,published_phase_percent=act['percent_by_phase'],
   role_weights=weights,rationale=d['mapping_rationales'][act['id']]))
  for role,w in weights.items():
   raw_roles[role]+=jh*w;cells.append(dict(activity=act['id'],role=role,weight=w,jh=jh*w))
 assert math.isclose(sum(raw_roles.values()),total)
 step=d['role_rounding_jh'];assigned={k:math.floor(v/step)*step for k,v in raw_roles.items()}
 order=sorted(raw_roles,key=lambda k:(-(raw_roles[k]/step-math.floor(raw_roles[k]/step)),k))
 for k in order[:round((total-sum(assigned.values()))/step)]:assigned[k]+=step
 assert sum(assigned.values())==total
 months=formula('cocomo_schedule',C=c['C'],JH=total,effort_phase_factor=c['effort_phase_factor'],
  day_hours=c['day_hours'],month_hours=c['month_hours'],SCED=c['SCED'],F=F,schedule_phase_factor=c['schedule_phase_factor'])
 planning=rounded(months,d['schedule_rounding_months'])
 capacity=yaml.safe_load((ROOT/'source/deploiement-groupe.yaml').read_text(encoding='utf-8'))['calendrier_autonome']['capacite']['jours_productifs_etp_mois']
 md_roles={x['id']:x['jh'] for x in md['roles']}
 roles=[dict(id=k,label=role_labels[k],unrounded_jh=raw_roles[k],jh=assigned[k],master_data_retained_jh=md_roles[k],
   cumulative_proposed_jh=md_roles[k]+assigned[k],average_people_at_capacity_convention=assigned[k]/planning/capacity) for k in role_labels]
 # Exact decomposition by size, without fitting or modifying any native estimate.
 delta_base=odoo['base_equivalent_units']-anchor['base_equivalent_units']
 pos_o=odoo['detail']['analogue_bank']['positions_component']['program_units']
 pos_a=anchor['detail']['analogue_bank']['positions_component']['program_units']
 position_ids=[s['id'] for s in old['complement_module_analogies'] if s['analogue']=='positions_component']
 position_fraction=sum(s['central'] for s in old['complement_module_analogies'] if s['id'] in position_ids)
 delta_position=(pos_o-pos_a)*position_fraction
 delta_other=odoo['Flow_complements_equivalent_units']-anchor['Flow_complements_equivalent_units']-delta_position
 size_gap=delta_base+delta_position+delta_other
 gap=odoo['total_stock_jh']-anchor['total_stock_jh']
 decomposition=[
  dict(cause='base_native',size_delta=delta_base),
  dict(cause='analogue_position_F02_F05',size_delta=delta_position),
  dict(cause='autres_analogues_et_descriptions',size_delta=delta_other)]
 for x in decomposition:
  x['share_of_size_gap_pct']=100*x['size_delta']/size_gap
  x['descriptive_share_of_jh_gap']=gap*x['size_delta']/size_gap
 assert math.isclose(size_gap,(odoo['base_equivalent_units']+odoo['Flow_complements_equivalent_units'])-(anchor['base_equivalent_units']+anchor['Flow_complements_equivalent_units']))
 # Source witnesses qualify packaging differences; they do not quantify all excess code.
 scope=module('scope09','audits/2026-10-30-stock-perimetres-02/build.py')
 repos=read('audits/2026-10-30-master-data-comparable-reuse/measurements.json')['repos']
 witnesses=[]
 for w in d['review_witnesses']:
  path=ROOT/repos[w['repo']]['root']/w['path'];raw=path.read_bytes()
  attribution=next(x for x in old['attributions'] if x['repo']==w['repo'] and x['path']==w['path'])
  assert sha(path)==attribution['sha256']
  if path.suffix=='.py':
   nodes=[n for n in ast.walk(ast.parse(raw.decode('utf-8-sig'))) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==w['name']]
   assert len(nodes)==1
   lo,hi=nodes[0].lineno,nodes[0].end_lineno
  else:
   _,methods,_=scope.parse(path);ms=[m for m in methods if m['name']==w['name']];assert len(ms)==1
   lo,hi=ms[0]['start'],ms[0]['end']
  selected={(n['kind'],n['start'],n['end']) for n in attribution['whole_method_nodes'] if lo<=n['start']<=n['end']<=hi}
  witnesses.append(dict(**w,start_line=lo,end_line=hi,sha256=sha(path),measured_whole_method_nodes=len(selected),
   url='https://github.com/'+repos[w['repo']]['repository']+'/blob/'+repos[w['repo']]['commit']+'/'+w['path']+'#L'+str(lo)))
 functional=read(old['functional_contract_ref'])
 CFP=functional['result']['CFP'];h=functional['result']['hours_per_CFP']
 functional_jh=formula('cosmic_effort',CFP=CFP,hours_per_CFP=h,factor=1,day_hours=c['day_hours'])
 implied=formula('implied_productivity',JH=anchor['total_stock_jh'],day_hours=c['day_hours'],CFP=CFP)
 # Published implementation medians: illustrative scale only, no applicability correction.
 implementation_scale=[dict(published_median_percent=p,illustrative_jh=functional_jh*p/100,
   residual_jh_after_removing_this_hypothetical_share=functional_jh*(1-p/100)-anchor['total_stock_jh']) for p in [7.4,8.4]]
 schedule=dict(unrounded_months=months,proposed_months=planning,formula='3.67 * (340 / 1.18 * 7 / 152) ** 0.31794 * 1.25',
  source_rule='source/fondamentaux.yaml#estimation_model.rules.cocomo_schedule',
  productive_jh_per_person_month=capacity,average_people=total/planning/capacity,
  role_availability_confirmed=False,
  starts_when='Travaux Stock effectivement engagés, services Master Data nécessaires disponibles ; pas délai depuis le démarrage du programme.',
  scope='Délai local calculé du produit logiciel Stock, qualification et préparation de mise en service incluses.',
  limit='Pas planning engagé, pas neuf personnes à plein temps. Les 17 mois Master Data et le délai Stock ne sont pas additionnés.')
 result=dict(id=d['id'],status=d['status'],input_sha256=freeze['input_sha256'],primary_method='COCOMO II',crosscheck='COSMIC × ISBSG',
  proposed_jh=total,raw_reference_jh=anchor['total_stock_jh'],rounding_delta_jh=total-anchor['total_stock_jh'],
  proposed_common_base_jh=rounded(anchor['base_common_jh'],10),
  proposed_Flow_complements_jh=total-rounded(anchor['base_common_jh'],10),
  selected_reference=d['selected_reference'],selection_rationale=d['selection_rationale'],framework_assumption=d['framework_assumption'],
  size=dict(common_equivalent_units=anchor['base_equivalent_units'],Flow_complements_equivalent_units=anchor['Flow_complements_equivalent_units'],
   total_equivalent_KSLOC=anchor['total_equivalent_KSLOC'],definition=old['size_meaning'],cocomo=c,E=E,F=F),
  native_estimates=[dict(id=x['id'],unrounded_jh=x['total_stock_jh'],display=x['display'],
    alignment_vs_java=alignment(x['total_stock_jh'],anchor['total_stock_jh'])) for x in r['rows']],
  odoo_gap=dict(**alignment(odoo['total_stock_jh'],anchor['total_stock_jh']),
   base_difference_jh=odoo['base_common_jh']-anchor['base_common_jh'],
   Flow_complement_difference_jh=odoo['Flow_complements_marginal_jh']-anchor['Flow_complements_marginal_jh'],
   position_analogue_odoo_units=pos_o,position_analogue_java_units=pos_a,
   position_analogue_size_ratio=pos_o/pos_a,position_module_ids=position_ids,
   size_decomposition=decomposition,source_witnesses=witnesses,
   decomposition_note='Parts descriptives du désaccord de taille et répartition proportionnelle de l’écart JH ; pas efforts autonomes ni décomposition causale mesurée.',
   conclusion='Odoo est plus volumineux dans ce modèle de source : davantage de base native et un analogue K2 élargi à plusieurs responsabilités. Les attributions grossières et conventions de langage subsistent ; 534 JH ne prouvent pas que Spring coûterait autant, ni que Java serait intrinsèquement plus productif.',
   no_corrected_odoo_estimate_invented=True,native_inputs_08_unchanged=True),
  functional_control=dict(CFP=CFP,hours_per_CFP=h,factor=1,jh=functional_jh,
   alignment_vs_unrounded_java=alignment(functional_jh,anchor['total_stock_jh']),
   implied_java_hours_per_CFP=implied,implied_rate_not_used_to_recalibrate=True,
   productivity_gap_hours_per_CFP=h-implied,
   source='https://cosmic-sizing.org/wp-content/uploads/2015/07/Performance-of-Business-Application-Real-Time-and-Component-Software-Projects-2012.pdf',
   source_table=7,source_printed_page=12,effort_definition_printed_pages=[46,47],
   cohort='Projets métier historiques terminés entre 1999 et 2011 ; repère Java multi-plateforme/PC normalisé à 100–200 CFP, pas sous-échantillon Stock Spring.',
   activity_alignment_status='partiel_pas_strictement_appaire',
   activities='ISBSG Normalized Level 1 : planifier, spécifier, concevoir, construire, tester et mettre en œuvre. COCOMO : phases Inception, Élaboration, Construction et Transition, incluant pilotage logiciel et préparation de mise en service.',
   staff_boundary='ISBSG exclut les intervenants non affectés formellement au projet ; la proposition Flow répartit les travaux spécifiques de plateforme et de sécurité. Les experts rattachés sont inclus dans la proposition.',
   differences=['Le benchmark 20 h/CFP n’est pas conditionné à la réutilisation des services Master Data déjà financés.',
    '169 CFP proposés mesurent le service fonctionnel cible ; les tailles de code analogues et leurs attributions sont estimées, pas du code Flow réalisé.',
    'Le déploiement du benchmark peut couvrir plus que la mise en service logicielle initiale ; la part de la cohorte PDR Java effectivement concernée est inconnue.',
    'Une sous-estimation des tailles COCOMO ou une surestimation du comptage fonctionnel reste possible ; aucun écart n’est expliqué automatiquement par la méthode.'],
   implementation_illustrations=implementation_scale,
   illustration_note='7,4 % et 8,4 % sont des médianes globales de populations distinctes publiées en annexe, pas des corrections appliquées ni un intervalle. Elles ne suffisent pas à faire disparaître l’écart.',
   reconciliation='Origines possibles identifiées et écart arithmétique quantifié ; ventilation causale des 143,84 JH non démontrée. Contrôle conservé à 482,86 JH, aucune moyenne ni ajustement de convergence.'),
  activities=activities,activity_to_role=cells,roles=roles,role_allocation_status=d['allocation_status'],
  role_rounding_jh=step,activity_reference=a,isbsg_distribution_preserved_but_not_applied=activities_source['isbsg'],
  schedule=schedule,hypothesis_sensitivities=anchor['hypothesis_impacts'],
  limits=dict(probability=None,statistical_uncertainty=None,human_review=None,observed_project_effort=None,
   assumptions=old['assumptions'],framework_equivalence_is_hypothesis=True,
   no_specific_numeric_stock_performance_guarantee=True,
   MD_service_objectives='Les objectifs S1 de comparaison et la qualification propres à Master Data restent chez leur propriétaire ; ils ne valent pas tests de charge ni garanties Stock.',
   no_extra_ai_discount=True,no_extra_qa_or_coordination=True),
  scope=dict(capabilities=d['scope_capabilities'],
   common='Registre/mouvements, positions actuelles et datées, apports connus, comptages/ajustements et engagements.',
   Flow_complements='Admission/révision/double date/filiation, provenance/fraîcheur, protocoles et autorité, identité des commandes et expiration, contributions planning/Finance/produit, rapprochement après reprise.',
   excludes=['Intégration, connecteurs et migrations spécifiques Beaumanoir','Comptabilité générale et valorisation financière','WMS physique et terminaux','ATP/CTP/PTP, allocation et optimisation','Run, MCO et achats','Garantie de réservation distribuée entre bases'],
   reuse_owner='master-data-java-spring',reuse_policy=old['reuse_policy']),
  cumulative=dict(retained_gross_jh=md['total_jh'],retained_master_data_months=md['months'],proposed_stock_gross_jh=total,
   proposed_java_gross_jh=md['total_jh']+total,roles=sum(x['cumulative_proposed_jh'] for x in roles),
   explanation='Cumul Master Data retenue + proposition Stock. Pas adoption, pas somme des quatre alternatives ni recalcul COCOMO intégré de tout Flow.',
   combined_months=None,schedules_are_not_added=True),
  progress=dict(total_capabilities=88,studied_in_current_method=14,retained=6,stock_consolidated_proposed=8,
   studied_or_proposed_pct=100*14/88,retained_pct=100*6/88,other_capabilities=74,stock_percent_of_88=100*8/88,
   new_capabilities_this_iteration=0,new_retained_decisions=0,
   improvement='Consolidation Java/Spring, ventilation des activités vers les rôles, délai calculé et explication documentée des désaccords. La couverture n’augmente pas.',
   historical_note='Les repérages historiques des 88 capacités ne deviennent pas 88 estimations actuelles.'),
  next_iteration=dict(general_refinement_worthwhile=False,
   recommendation='Arrêter l’affinage Stock à périmètre constant et passer à une autre famille. Réouvrir sur changement d’architecture, garanties, disponibilité du patrimoine, interface ou équipe.',
   targeted_validation='Au jalon d’architecture/réalisation : corrections rétroactives, première réservation concurrente et reprise, avec scénario reproductible ; pas préalable imposé à cette étude d’opportunité.',
   uncertainty_reduction='Aucune réduction statistiquement démontrée. Meilleure traçabilité des causes et sensibilité des hypothèses, pas précision prédictive prouvée.'),
  active_business_model_changed=False,application_changed=False)
 write('results.json',result)
 (OUT/'bilan.yaml').write_text(yaml.safe_dump(result,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
 dependencies={x['path']:x['sha256'] for x in provenance['dependencies']}
 for path in ['audits/2026-10-30-stock-opportunite-08/provenance.json','audits/2026-10-30-master-data-consolidation/inputs.json',
  'source/estimations-core-retenues.yaml','source/deploiement-groupe.yaml','tools/estimation_calculation.py','tools/model_context.py',
  'tmp/master-data-triangulation-2026-10-30/cosmic-isbsg-2012.pdf','tmp/master-data-triangulation-2026-10-30/cocomo-ii-v21.pdf']:
  dependencies[path]=sha(ROOT/path)
 for path in [OUT/'inputs.json',OUT/'input-freeze.json',Path(__file__),OUT/'results.json',OUT/'bilan.yaml',OUT/'verify.py']:
  dependencies[path.relative_to(ROOT).as_posix()]=sha(path)
 write('provenance.json',dict(dependencies=[dict(path=p,sha256=h) for p,h in sorted(dependencies.items())],protected=provenance['protected']))
 print(json.dumps(dict(proposed_jh=total,roles={r['id']:r['jh'] for r in roles},months=months,proposed_months=planning,
  cumulative=result['cumulative'],odoo_gap_jh=gap,cosmic_gap_jh=functional_jh-anchor['total_stock_jh']),ensure_ascii=False,indent=2))
if __name__=='__main__':
 with model_session():main()
