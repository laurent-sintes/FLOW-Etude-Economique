"""Independent checks and readable summary for the Stock opportunity estimates."""
from pathlib import Path
import json,hashlib,math,sys,importlib.util,copy
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tmp/model-deps'),str(ROOT/'tools')]
import yaml
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 provenance=load(OUT/'provenance.json')
 for d in provenance['dependencies']:assert sha(ROOT/d['path'])==d['sha256'],d['path']
 for p,h in provenance['protected'].items():assert sha(ROOT/p)==h,p
 inputs=load(OUT/'inputs.json');freeze=load(OUT/'input-freeze.json');results=load(OUT/'results.json')
 assert freeze['input_sha256']==sha(OUT/'inputs.json')==results['input_sha256']
 c=inputs['cocomo'];E=c['B']+.01*c['SF_sum'];F=c['D']+.2*(E-c['B'])
 def effort(units,EM=1):
  return c['A']*(units/1000)**E*EM*c['SCED']*c['month_hours']/c['day_hours']*c['effort_phase_factor']
 assert len(inputs['attributions'])==62
 assert len(inputs['schemas'])==17 and sum(len(s['fields']) for s in inputs['schemas'])==124
 assert len(inputs['mapped_native_fields'])==2
 assert len(inputs['complement_module_analogies'])==7
 for d in inputs['attributions']:
  a=d['attribution'];assert 0<=a['lower']<=a['central']<=a['upper']<=1
  assert d['known_stock_program_floor']<=d['available_program']
  assert d['known_stock_declarative_floor']<=d['available_declarative']
  assert d['additional_framework_assimilation']==0
 rows=results['rows'];assert len(rows)==4
 checks={}
 for r in rows:
  s=r['detail'];p=r['id']
  assert len({x['path'] for x in s['core']})==len(s['core'])
  assert math.isclose(sum(x['program_units'] for x in s['core']),s['core_program'])
  assert math.isclose(sum(x['declarative_units'] for x in s['core']),s['core_declarative'])
  assert math.isclose(sum(x['program_units'] for x in s['complements']),s['complements_program'])
  assert math.isclose(sum(x['declarative_units'] for x in s['complements'])+s['configuration_declarative_units'],s['complements_declarative'])
  # Independently reconstruct each central attribution from fixed source size and floor.
  bypath={x['path']:x for x in s['core']}
  for d in inputs['attributions']:
   if d['product']!=p:continue
   line=bypath[d['path']]
   assert math.isclose(line['program_units'],max(d['available_program']*d['attribution']['central'],d['known_stock_program_floor']))
   assert math.isclose(line['declarative_units'],max(d['available_declarative']*d['attribution']['central'],d['known_stock_declarative_floor']))
  for b in s['complements']:
   spec=next(x for x in inputs['complement_module_analogies'] if x['id']==b['id'])
   assert math.isclose(b['new_behavior_program_units'],b['reference_behavior_units']*spec['central'])
   assert math.isclose(b['program_units'],b['new_behavior_program_units']+b['service_scaffold_program_units']+sum(m['program_units'] for m in b['models']))
   assert math.isclose(b['declarative_units'],sum(m['declarative_units'] for m in b['models']))
   # Data descriptions and view descriptors are separate from method-only analogy code.
   assert all('source_slices' in a for a in s['analogue_bank'].values())
  base=s['core_program']+s['core_declarative']
  extra=s['complements_program']+s['complements_declarative']
  assert math.isclose(base,r['base_equivalent_units'])
  assert math.isclose(extra,r['Flow_complements_equivalent_units'])
  assert math.isclose(effort(base),r['base_common_jh'],rel_tol=1e-12)
  assert math.isclose(effort(base+extra),r['total_stock_jh'],rel_tol=1e-12)
  assert math.isclose(r['base_common_jh']+r['Flow_complements_marginal_jh'],r['total_stock_jh'])
  assert math.isclose(sum(x['allocated_marginal_jh'] for x in r['complement_allocation']),r['Flow_complements_marginal_jh'])
  months=c['C']*(r['total_stock_jh']/c['effort_phase_factor']*c['day_hours']/c['month_hours']/c['SCED'])**F*c['schedule_phase_factor']
  assert math.isclose(months,r['local_schedule_months'],rel_tol=1e-12)
  assert len(r['activities'])==7 and math.isclose(sum(a['jh'] for a in r['activities']),r['total_stock_jh'])
  display=r['display']
  assert display['base_common_jh']+display['Flow_complements_jh']==display['total_stock_jh']
  assert abs(display['base_common_jh']-r['base_common_jh'])<=5.00001
  assert abs(display['total_stock_jh']-r['total_stock_jh'])<=5.00001
  assert abs(display['Flow_complements_jh']-r['Flow_complements_marginal_jh'])<=10.00001
  assert len(r['hypothesis_impacts'])==8
  for impact in r['hypothesis_impacts']:
   assert math.isclose(impact['lower_total_jh']-r['total_stock_jh'],impact['lower_change_jh'])
   assert math.isclose(impact['upper_total_jh']-r['total_stock_jh'],impact['upper_change_jh'])
   assert impact['lower_total_jh']<=r['total_stock_jh']<=impact['upper_total_jh']
  pers=next(x for x in r['hypothesis_impacts'] if x['id']=='capacite-equipe-PERS')
  assert math.isclose(pers['lower_total_jh'],r['total_stock_jh']*.83)
  assert math.isclose(pers['upper_total_jh'],r['total_stock_jh']*1.26)
  prex=next(x for x in r['hypothesis_impacts'] if x['id']=='experience-ecosysteme-PREX')
  assert math.isclose(prex['lower_total_jh'],r['total_stock_jh']*.87)
  assert math.isclose(prex['upper_total_jh'],r['total_stock_jh']*1.12)
  functional=r['COSMIC_ISBSG_control']
  assert math.isclose(functional['jh'],169*20/7)
  gap=functional['jh']-r['total_stock_jh']
  assert math.isclose(functional['descriptive_alignment']['gap_jh'],gap)
  assert math.isclose(functional['descriptive_alignment']['gap_pct'],100*gap/r['total_stock_jh'])
  checks[p]=dict(base_jh=r['base_common_jh'],complements_jh=r['Flow_complements_marginal_jh'],total_jh=r['total_stock_jh'],
    size_and_non_linear_effort_reconciled=True,activity_total_reconciled=True,sensitivities=8)
 retained=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))
 md=next(u for u in retained['units'] if u['id']=='master-data-java-spring')
 assert md['total_jh']==1500 and md['months']==17 and sum(r['jh'] for r in md['roles'])==1500
 assert not any('stock' in u['id'] for u in retained['units'])
 anchor=next(r for r in rows if r['id']=='axelor')
 assert results['cumulative']['candidate_java_master_data_plus_stock_jh']==1500+anchor['display']['total_stock_jh']==1840
 assert results['cumulative']['retained_gross_jh']==1500
 report=dict(id='stock-opportunite-08',status='estimations_d_opportunite_conditionnelles_proposees_non_adoptees',
  outcome='Quatre charges calculées à partir de tailles estimées, dans les écosystèmes natifs, pour la famille Stock cible. Les hypothèses remplacent l’exigence de séparation parfaite du code et restent visibles.',
  estimates=[dict(reference=r['id'],**r['display'],unrounded_base_jh=r['base_common_jh'],unrounded_complements_jh=r['Flow_complements_marginal_jh'],
    unrounded_total_jh=r['total_stock_jh'],size_core_units=r['base_equivalent_units'],size_complement_units=r['Flow_complements_equivalent_units']) for r in rows],
  base_scope='Registre et effets des mouvements, positions actuelles/passées et apports connus, comptages/ajustements, quantités engagées et protections natives de concurrence. L’intégration Beaumanoir, la comptabilité générale, le PLM, la promesse et l’optimisation ne sont pas chiffrés.',
  complement_scope=[dict(id=m['id'],analogue=m['analogue'],assumed_fraction=m['central'],range=[m['lower'],m['upper']],basis=m['reasoning'],
    shares_by_reference={r['id']:next(x['allocated_marginal_jh'] for x in r['complement_allocation'] if x['id']==m['id']) for r in rows}) for m in inputs['complement_module_analogies']],
  complement_allocation_note='Les parts par ensemble répartissent le supplément COCOMO selon la taille estimée. Leur somme rejoint le supplément ; ce ne sont pas sept efforts COCOMO autonomes.',
  reuse=dict(owner='master-data-java-spring',services='Identités/références, enveloppes d’admission, versions, protection, coordinateur de reprise et mise en service.',
    exact_native_MD_overlap_deduction_preserved=True,no_second_framework_assimilation=True,
    native_fields_mapped_instead_of_recreated=inputs['mapped_native_fields'],
    dependency='Patrimoine financé et supposé utilisable ; pas une observation de code Flow livré.'),
  hypotheses=inputs['assumptions'],
  source_attribution_examples=[
    dict(reference='erpnext',component='stock_ledger.py',central_share=.35,meaning='Part de taille Stock estimée du composant mêlé à la valorisation ; plancher des instructions déjà mesurées conservé.'),
    dict(reference='odoo',component='stock_move.py',central_share=.4,meaning='Part de taille Stock estimée ; exécution de colis/reliquats/réaffectation largement retirée.'),
    dict(reference='tryton',component='move.py',central_share=.75,meaning='Part de taille Stock estimée ; coût/prélèvement natifs séparés à la maille du composant.'),
    dict(reference='axelor',component='StockMoveServiceImpl.java',central_share=.3,meaning='Part de taille Stock estimée ; réalisation physique, prix et effets de service excédentaires écartés par attribution.')
  ],
  hypothesis_impacts=[dict(reference=r['id'],changes=r['hypothesis_impacts']) for r in rows],
  sensitivity_interpretation='Variations une famille d’hypothèses à la fois autour du résultat non arrondi. Ni cumul de marges, ni enveloppe de scénarios, ni intervalle probabiliste.',
  formula=dict(source='source/fondamentaux.yaml#estimation_model',rule_ids=['equivalent_size','cocomo_exponent','cocomo_effort','nonlinear_complements','cocomo_schedule','signed_gap','signed_gap_pct','spread','spread_pct'],
    cocomo_parameters=inputs['cocomo'],estimated_sizes_are_not_observed_efforts=True,
    activity_scope='Analyse/exigences, conception, réalisation et tests développeur, QA, gestion/configuration, pilotage logiciel et préparation du déploiement selon la répartition publiée. Aucune remise IA ni provision QA/pilotage supplémentaire.'),
  functional_check=dict(CFP=169,hours_per_CFP=20,factor=1,jh=169*20/7,
    comparisons={r['id']:r['COSMIC_ISBSG_control']['descriptive_alignment'] for r in rows},
    interpretation='Repère conditionnel COSMIC × ISBSG conservé. Il est plus élevé que trois références et plus bas qu’Odoo ; le désaccord reste visible. Aucune calibration locale ni preuve de meilleure précision n’est déduite.'),
  cumulative=results['cumulative'],
  progress=dict(total_capabilities=88,campaign_capabilities_framed=14,
    capabilities_with_retained_estimate=6,retained_coverage_pct=100*6/88,
    stock_capabilities_with_conditional_opportunity_estimate=8,
    campaign_capabilities_with_retained_or_proposed_estimate=14,proposed_or_retained_coverage_pct=100*14/88,
    new_opportunity_estimates=4,new_retained_estimates=0,
    historical_note='Les 88 capacités ont des repérages historiques ; les 14 désignent la méthode actuelle. Les propositions Stock n’augmentent pas automatiquement le budget retenu.'),
  progress_assessment=dict(calculation_progress=True,
    explanation='La méthode produit enfin quatre ordres de grandeur et expose le prix des hypothèses. Le changement est l’acceptation explicite de tailles estimées, pas l’obtention de nouvelles charges de projets observées.',
    uncertainty_quantification='Sensibilités calculées ; pas réduction statistiquement démontrée de l’incertitude.',
    largest_limits=['Pertinence des attributions de code mixte.','Taille nouvelle des modules Flow, notamment restitution/contrats et protocoles.','Compétence/expérience de l’équipe et convention de poids du déclaratif.','Équivalence des frameworks et objectifs de service supposés.']),
  next_iteration=dict(worthwhile=True,focus='Consolider le candidat Java/Spring à partir d’Axelor, discuter les attributions dominantes et expliquer l’écart Odoo sur les compléments de position/fourniture. Un examen ciblé seulement si son impact peut changer le budget retenu.',
    not_worthwhile='Reprendre un inventaire général de toutes les méthodes ou forcer les quatre valeurs à se rejoindre.'),
  evidence=['inputs.json','attribution-hypotheses.json','input-freeze.json','results.json','calculate.py','prepare.py','verification.json'],
  active_business_model_changed=False,app_changed=False,retained_1500_jh_17_months_preserved=True)
 (OUT/'bilan.yaml').write_text(yaml.safe_dump(report,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
 depmap={d['path']:d['sha256'] for d in provenance['dependencies']}
 for p in [Path(__file__).resolve(),OUT/'calculate.py',OUT/'results.json',OUT/'bilan.yaml']:
  depmap[str(p.relative_to(ROOT)).replace('\\','/')]=sha(p)
 provenance['dependencies']=[dict(path=p,sha256=h) for p,h in sorted(depmap.items())]
 write('provenance.json',provenance)
 result=dict(consistency_checks_passed=True,input_freeze_preserved=True,native_references=4,central_values_and_32_sensitivities_checked=True,
  stock_totals_jh={r['id']:r['display']['total_stock_jh'] for r in rows},
  native_sizes_and_MD_deduplication_checked=True,complement_modules=7,schema_fields=124,mapped_native_fields=2,
  published_activities_preserved=True,local_schedules_preserved=True,
  retained_cumulative_gross_jh=1500,conditional_java_candidate_cumulative_gross_jh=1840,retained_master_data_months=17,
  stock_is_adopted=False,application_changed=False,checks=checks)
 write('verification.json',result)
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
