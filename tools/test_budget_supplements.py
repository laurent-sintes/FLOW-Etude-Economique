"""Regressions for funding attribution and honest completeness of budget reserves."""
from copy import deepcopy
import unittest
from validate_stacks import ROOT,read
from model_context import model_session
from market_comparison import build_market_comparison
from budget_supplements import compile_budget_review,SOURCE
from capability_catalog import analysis

class BudgetSupplementTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.spec=read(ROOT/SOURCE);cls.grid=analysis();cls.mechanisms=read(ROOT/'source/calculs-estimation-core.yaml')['mechanisms']
  with model_session():cls.comparison=build_market_comparison(read(ROOT/'source/references-couts-integration.yaml'))
 def build(self,spec=None,comparison=None):
  with model_session():return compile_budget_review(self.comparison if comparison is None else comparison,self.grid,self.mechanisms,spec=self.spec if spec is None else spec)
 def test_all_gaps_options_phases_and_unknown_totals(self):
  b=self.comparison['budget_review'];gaps={g['id'] for g in self.comparison['gaps']}
  self.assertEqual({r['gap_ref'] for r in b['reviews']},gaps)
  self.assertEqual(b['summary']['reviewed_gap_option_phases'],len(gaps)*5*3)
  self.assertEqual(b['summary']['functional_qualification'],'partial')
  for key in ['net_extra_jh','net_extra_initial_eur_ht','net_extra_annual_eur_ht','known_subtotal_initial_eur_ht']:self.assertIsNone(b['summary'][key])
  self.assertFalse(b['summary']['adopted_amounts_changed'])
  self.assertEqual(b['summary']['unique_reserves'],len(b['additions']))
  self.assertGreater(b['summary']['unpriced_reserves'],0)
  self.assertTrue(all(c['complete_ba_coverage'] is None for r in self.comparison['rows'] for c in r['cells']))
 def test_shared_services_reserve_is_one_object_for_two_gaps(self):
  b=self.comparison['budget_review'];a=next(a for a in b['additions'] if a['id']=='CB-JAVA-SERVICES')
  self.assertEqual(set(a['gap_refs']),{'G06','G07'})
  for gid in a['gap_refs']:self.assertIn(a['id'],next(r for r in b['reviews'] if r['gap_ref']==gid)['addition_refs'])
  spec=deepcopy(self.spec);spec['additions'].append(dict(a,id='CLONED-SERVICES'))
  with self.assertRaisesRegex(ValueError,'duplicate work package'):self.build(spec)
 def test_no_fabricated_zero_or_price_or_calculation(self):
  for key,value in [('net_extra_jh',0),('net_extra_initial_eur_ht',10000),('net_extra_annual_eur_ht',0),('estimate_ref','orders-java-spring-v1')]:
   spec=deepcopy(self.spec);spec['additions'][0][key]=value
   with self.subTest(key=key),self.assertRaisesRegex(ValueError,'ERR_BUDGET_SUPPLEMENT'):self.build(spec)
 def test_missing_gap_or_product_or_phase_is_not_full_review(self):
  spec=deepcopy(self.spec);spec['reviews'].pop()
  with self.assertRaisesRegex(ValueError,'every declared gap'):self.build(spec)
  spec=deepcopy(self.spec);del spec['reviews'][0]['product_actions']['erpnext']
  with self.assertRaisesRegex(ValueError,'every compared product'):self.build(spec)
  spec=deepcopy(self.spec);spec['reviews'][-1]['non_budget_treatments']=[]
  with self.assertRaisesRegex(ValueError,'all economic options and phases'):self.build(spec)
 def test_unknown_need_funding_activity_and_scope_are_rejected(self):
  for field in ['need_refs','mechanism_refs']:
   spec=deepcopy(self.spec);spec['reviews'][0]['criteria'][0][field]=['foreign']
   with self.subTest(field=field),self.assertRaisesRegex(ValueError,'ERR_BUDGET_SUPPLEMENT'):self.build(spec)
  for field in ['integration_activity_refs','maintenance_activity_refs','evidence_refs']:
   spec=deepcopy(self.spec);spec['reviews'][0][field]=['foreign']
   with self.subTest(field=field),self.assertRaisesRegex(ValueError,'ERR_BUDGET_SUPPLEMENT'):self.build(spec)
 def test_unrelated_baseline_or_false_family_is_rejected(self):
  for reference in [dict(calculation_ref='orders-java-spring-v1',family_refs=[]),dict(calculation_ref='supply-controls-java-spring-v1',family_refs=['backlog'])]:
   spec=deepcopy(self.spec);spec['reviews'][0]['baseline_refs']=[reference]
   with self.assertRaisesRegex(ValueError,'ERR_BUDGET_SUPPLEMENT'):self.build(spec)
 def test_reserve_links_and_non_budget_treatments_are_consistent(self):
  spec=deepcopy(self.spec);spec['reviews'][0]['addition_refs'].pop()
  with self.assertRaisesRegex(ValueError,'bidirectional'):self.build(spec)
  spec=deepcopy(self.spec);spec['reviews'][0]['non_budget_treatments']=[dict(stack='java-spring',phase_ref='obtain_core',reason='inconsistent')]
  with self.assertRaisesRegex(ValueError,'incompatible non-budget'):self.build(spec)
 def test_adopted_lots_are_reproduced_and_not_summed_per_gap(self):
  b=self.comparison['budget_review'];units={u['id']:u for u in read(ROOT/'source/estimations-core-retenues.yaml')['units']}
  for r in b['reviews']:
   for base in r['baselines']:
    self.assertEqual(base['adopted_jh'],units[base['unit_id']]['total_jh'])
    self.assertLessEqual(sum(a['jh'] for a in base['allocations']),base['adopted_jh'])
  g7=next(r for r in b['reviews'] if r['gap_ref']=='G07')
  names={s['name'] for base in g7['baselines'] for s in base['schemas']}
  self.assertIn('service-order-repair-alteration-contract',names)
  self.assertIn('service-order-personalization-contract',names)
  self.assertNotIn('total_funded_jh',b['summary'])
 def test_financial_owner_and_option_locators_are_checked(self):
  spec=deepcopy(self.spec)
  a=next(a for a in spec['additions'] if a['id']=='CB-MICROSOFT-INTEGRATION')
  a['existing_funding_refs'][0]['source_ref']='source/chiffrage/chiffrage-sap.yaml'
  with self.assertRaisesRegex(ValueError,'another option'):self.build(spec)
  spec=deepcopy(self.spec);spec['additions'][0]['existing_funding_refs'][0]['keys']=['not_a_financing']
  with self.assertRaisesRegex(ValueError,'missing existing funding locator'):self.build(spec)
 def test_source_and_proof_closure_and_input_isolation(self):
  spec=deepcopy(self.spec)
  with model_session() as session:
   out=compile_budget_review(self.comparison,self.grid,self.mechanisms)
   names={p.relative_to(ROOT).as_posix() for p in session.documents}
  for a in out['additions']:
   self.assertTrue({f['source_ref'] for f in a['existing_funding_refs']}<=names)
  self.assertIn(SOURCE,names);self.assertIn('source/schema-complements-budgetaires.yaml',names)
  for r in out['reviews']:
   for b in r['baselines']:
    self.assertTrue(set(b['evidence_paths'])<=names)
  out['reviews'][0]['residual']='changed'
  self.assertEqual(self.spec,spec)

if __name__=='__main__':unittest.main()
