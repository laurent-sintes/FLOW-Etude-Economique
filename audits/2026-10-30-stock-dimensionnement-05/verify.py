"""Verify the Stock sizing trial, preserve the retained model and document its rejection."""
from pathlib import Path
from collections import Counter
import json,hashlib,math,sys,ast,importlib.util
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tmp/model-deps'),str(ROOT/'tools'),str(ROOT/'tmp/master-data-native-23/parser-deps')]
import yaml
from model_context import model_session
from estimation_calculation import formula
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mod(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
scope=mod('scope_check',ROOT/'audits/2026-10-30-stock-perimetres-02/build.py')
counter=mod('counter_check',ROOT/'audits/2026-10-30-master-data-natif/measure.py')

def main():
 inputs=load(OUT/'inputs.json');results=load(OUT/'results.json');samples=load(OUT/'analogues.json')['samples'];provenance=load(OUT/'provenance.json')
 sensitivity=load(OUT/'sensibilite-analogies.json')
 checks={}
 for dep in provenance['dependencies']:assert sha(ROOT/dep['path'])==dep['sha256'],dep['path']
 checks['dependency_hashes']=len(provenance['dependencies'])
 for p,h in provenance['protected'].items():assert sha(ROOT/p)==h,p
 checks['protected_business_inputs_unchanged']=len(provenance['protected'])
 selected_raw_sources={}
 for product in ['erpnext','odoo','tryton','axelor']:
  for rel in [f'audits/2026-10-30-stock-mesures-03/{product}-mesures.json',f'audits/2026-10-30-stock-completion-04/{product}-presentation.json']:
   for file in load(ROOT/rel)['files']:
    p=ROOT/scope.repos[product]['root']/file['path'];assert sha(p)==file['sha256'],p
    selected_raw_sources[str(p)]=sha(p)
 checks['raw_native_core_and_presentation_files']=len(selected_raw_sources)
 for a in samples:
  p=ROOT/scope.repos[a['repo']]['root']/a['path'];assert sha(p)==a['sha256']
  raw=p.read_bytes();text=raw.decode('utf-8-sig')
  fragment='\n'.join(text.splitlines()[a['start']-1:a['end']]);assert fragment==a['source_fragment']
  assert a['commit']==scope.repos[a['repo']]['commit']
  if p.suffix=='.py':
   nodes=[n for n in ast.walk(ast.parse(text)) if isinstance(n,ast.stmt)
     and not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str))
     and a['start']<=n.lineno<=n.end_lineno<=a['end']]
  else:
   tree=scope.JAVA.parse(raw);assert not tree.root_node.has_error
   nodes=[n for n in counter.walk(tree.root_node)
     if ((n.type.endswith('_statement') and n.type!='empty_statement') or n.type in counter.JAVA_EXTRA)
     and a['start']<=n.start_point.row+1<=n.end_point.row+1<=a['end']]
  assert len(nodes)==a['program_units']==len(a['counted_nodes'])
  assert a['source_url'].startswith('https://github.com/'),a['source_url']
 checks['whole_method_analogues_recounted']=len(samples)
 assert len({w['id'] for w in inputs['work']})==len(inputs['work'])==66
 assert len({s['name'] for s in inputs['schemas']})==len(inputs['schemas'])==17
 assert sum(len(s['fields']) for s in inputs['schemas'])==126
 assert all(len(s['fields'])==len(set(s['fields'])) for s in inputs['schemas'])
 assert all(x['quantity']==1 for x in inputs['work'])
 checks['residual_behaviors_distinct']=len(inputs['work'])
 checks['proposed_data_structures']=len(inputs['schemas'])
 checks['proposed_new_models']=sum(s['new_model'] for s in inputs['schemas'])
 checks['proposed_model_extensions']=sum(not s['new_model'] for s in inputs['schemas'])
 for r in inputs['reuse']:
  assert r['funding_owner']=='master-data-java-spring' and r['additional_generic_component_units']==0
 checks['generic_reuse_owners_with_no_second_component_charge']=len(inputs['reuse'])
 matrix=load(OUT/'couverture-processus.json')
 assert len(matrix)==84
 for p in ['erpnext','odoo','tryton','axelor']:
  entries=[r for r in matrix if r['product']==p]
  assert set(r['process'] for r in entries)=={f'S{i:02d}' for i in range(1,22)}
 checks['process_to_native_target_mappings']=len(matrix)
 assert len(load(OUT/'frontieres-resolues-pour-la-proposition.json'))==41
 checks['native_boundary_dispositions']=41
 c=load(ROOT/'audits/2026-10-30-master-data-spring-flow/inputs.json')['cocomo']
 with model_session():
  E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum'])
  for r in results['rows']:
   lines=r['lines']
   assert len({l['id'] for l in lines})==len(lines)
   extra=sum(l['program_units']+l['declarative_units'] for l in lines)
   assert extra==r['proposed_complement_units']
   size=extra+r['measured_native_core_units'];assert size==r['total_equivalent_units']
   independent=c['A']*(size/1000)**E*c['month_hours']/c['day_hours']*c['effort_phase_factor']
   assert math.isclose(independent,r['trial_jh'],rel_tol=1e-12)
   assert math.isclose(r['measured_core_only_jh']+r['trial_complements_marginal_jh'],r['trial_jh'])
   assert math.isclose(sum(p['jh_share_of_marginal_complements'] for p in r['package_sizes_and_allocations']),r['trial_complements_marginal_jh'])
   assert math.isclose(sum(a['jh'] for a in r['activities']),r['trial_jh'])
   assert len(r['activities'])==7
   assert r['receivable_stock_family_jh'] is None and r['native_implemented_full_family_jh'] is None and r['cumulative_with_stock_jh'] is None
   assert r['functional_comparison']['alignment']['gap_pct'] is None
   assert not r['eligibility']['conditional_target_cost_receivable']
   s=next(s for s in sensitivity['checks'] if s['product']==r['id'])
   assert s['count']==40
   assert math.isclose(s['change_jh'],s['alternative_trial_jh']-r['trial_jh'])
 checks['four_arithmetic_trials_and_seven_activity_distributions']=4
 retained=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))
 md=next(u for u in retained['units'] if u['id']=='master-data-java-spring')
 assert md['total_jh']==1500 and md['months']==17 and sum(x['jh'] for x in md['roles'])==1500
 assert all('stock' not in u['id'] for u in retained['units'])
 checks['retained_1500_jh_17_months_and_roles_preserved']=True
 report=dict(id='stock-dimensionnement-05',status='dimensionnement_essaye_quatre_calculs_non_recevables',
  outcome='Les compléments sont explicités et mesurés par analogies. Leur transformation en coût de famille reste refusée : les analogies par catégories de méthodes ne démontrent pas la taille de mécanismes complets.',
  scope=dict(capabilities=['BC-009','BC-010','BC-011','BC-012','BC-013','BC-016','BC-017','BC-018'],functional_processes=21,proposed_CFP=169),
  completed=dict(native_code_method_samples=32,alternative_method_samples=4,residual_behaviors=66,data_structures=17,new_models=13,extensions_to_native_models=4,
   added_fields=126,proposed_process_interfaces=21,native_boundary_dispositions=41,master_data_generic_reuse_mechanisms=8),
  packages=[dict(id=p['id'],work=p['work'],behavior_count=sum(w['package']==p['id'] for w in inputs['work']),
    data_structures=[s['name'] for s in inputs['schemas'] if s['package']==p['id']],reuse=p['reuse'],
    new_work=p['new'],status='inventaire et essai de taille établis ; équivalence d’un mécanisme complet non démontrée')
    for p in inputs['packages']],
  measurements_vs_assumptions=dict(
   measured='Méthodes natives complètes, bornes, instructions/déclarations, empreintes et révisions. Leur code original est joint aux échantillons.',
   modeled='66 traitements cibles, 17 structures, branchements de 21 processus et configurations. Quantités et correspondances aux analogues proposées pour le contrat fonctionnel.',
   calculated='Quatre essais COCOMO via le moteur canonique, contribution marginale des compléments, sept activités publiées, contre-épreuve de sélection des analogues.',
   not_established='Équivalence fonctionnelle des petites catégories de méthodes avec les mécanismes Stock complets, absence de recouvrement entre règles et branchements, dépendances applicatives fermées, objectifs de service dimensionnés.'),
  native_costs=[dict(product=r['id'],receivable_stock_jh=None,
     reason='Noyau natif partiel + taille de compléments par analogies encore non qualifiées.',
     trial_evidence='results.json#rows/'+str(i)) for i,r in enumerate(results['rows'])],
  diagnostic_only=dict(trial_file='results.json',is_retained_budget=False,
   analogy_size_share_pct_by_reference={r['id']:r['sensitivities_not_probability']['residual_size_share_pct'] for r in results['rows']},
   sensitivity_pct_by_reference={s['product']:s['change_pct'] for s in sensitivity['checks']},
   interpretation='À périmètre et quantités constants, remplacer le gabarit de validation change le résultat de -7,4 % à +43,1 %. Les validations choisies portent des comportements différents : cela révèle une catégorie trop large, pas une incertitude statistique.',
   numerical_alignment=None,reason_no_alignment='Natifs incomplets, analogies non qualifiées et garanties de service non appariées. Ne pas interpréter leur écart aux 483 JH fonctionnels comme une validation.'),
  current_estimates=dict(cumulative_adopted_gross_jh=1500,master_data_months=17,stock_retained_jh=None,stock_schedule_months=None,stock_role_allocation=None),
  progress=dict(total_capabilities=88,campaign_capabilities_framed=14,campaign_framed_pct=100*14/88,
    previously_studied_historical_capabilities=88,historical_coverage_does_not_equal_current_cost_eligibility=True,
    stock_with_proposed_functional_contract=8,stock_with_work_inventory_and_sizing_trial=8,
    stock_with_receivable_complete_estimate=0,adopted_capabilities=6,adopted_coverage_pct=100*6/88,
    remaining_java_not_adopted=82,receivable_native_stock_family_calculations=0,diagnostic_native_stack_trials=4),
  what_became_less_uncertain=[
   'Les responsabilités génériques réutilisées et celles propres au Stock sont séparées avec un propriétaire unique.',
   'Finance et Product Feedback sont bornés à leurs contributions, corrections et retours ; pas de moteur comptable ni de PLM.',
   'Les traitements, champs et interfaces supposés sont visibles et leur calcul peut être reproduit.',
   'La fragilité du choix des petites méthodes est maintenant mesurée, au lieu d’être masquée par la précision des quatre résultats.'],
  what_did_not_become_less_uncertain=[
   'Le coût total de Stock : aucune estimation nouvelle adoptable.',
   'La taille complète des mécanismes de correction temporelle et de réservation concurrente.',
   'Le coût des garanties de volume, délai de réponse et reprise ; aucun objectif chiffré engagé.',
   'La productivité spécifique à Stock ou la précision du proxy AST utilisé dans COCOMO.'],
  next_iteration=dict(worthwhile=True,approach_change_required=True,
   not_worthwhile='Répéter ou affiner les coefficients du même catalogue de petites méthodes pour chercher quatre chiffres proches.',
   objective='Prendre deux mécanismes complets et bornés : correction rétroactive des quantités et engagement concurrent d’une quantité donnée. Dans chaque OSS, mesurer validation, transaction, résultat et reprise comme une chaîne ; isoler l’allocation/valorisation non retenue et la réutilisation.',
   decision_gate='Si une chaîne ne peut être isolée, conserver un coût natif inconnu pour cette référence ; ne pas fabriquer son équivalent à partir d’un simple gabarit. Étendre seulement les chaînes qualifiées aux autres compléments.',
   reason='Le blocage est localisé dans l’assiette de taille, pas dans l’arithmétique COCOMO. Une nouvelle mesure ciblée peut changer cette assiette ; un nouveau tour de formules ne le peut pas.'),
  verification=dict(status='contrôles des sources, mesures et calculs réussis ; coûts non qualifiés',checks=checks,
    application_changed=False,reference_capabilities_changed=False,economic_decisions_changed=False,OSS_runtime_tests_executed=False))
 (OUT/'bilan.yaml').write_text(yaml.safe_dump(report,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
 (OUT/'verification.json').write_text(json.dumps(dict(checks=checks,all_consistency_checks_passed=True,economic_estimates_receivable=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(checks=checks,economic_estimates_receivable=False),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
