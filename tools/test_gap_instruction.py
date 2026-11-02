from copy import deepcopy
from pathlib import Path
import unittest,json
from market_comparison import build_market_comparison
from market_instruction import build_market_instruction
from validate_stacks import ROOT,read
from model_context import model_session

class GapInstructionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.market=read(ROOT/'source/references-couts-integration.yaml');cls.market['instruction']=build_market_instruction(cls.market)
  cls.spec=read(ROOT/'source/comparaison-solutions.yaml')
  cls.units=read(ROOT/'source/estimations-core-retenues.yaml')['units']
 def case(self,spec):return next(g['instruction'] for g in spec['gaps'] if g['id']=='G02')
 def test_baseline_replays_and_does_not_become_increment(self):
  with model_session():
   c=build_market_comparison(self.market);i=next(g['instruction'] for g in c['gaps'] if g['id']=='G02')
  self.assertEqual(i['baseline']['adopted_jh'],next(u['total_jh'] for u in self.units if u['id']==i['baseline']['unit_id']))
  self.assertLessEqual(sum(a['jh'] for a in i['baseline']['family_allocations']),i['baseline']['adopted_jh'])
  self.assertEqual(i['baseline']['internal_backlog_jh'],next(a['jh'] for a in i['baseline']['family_allocations'] if a['id']=='backlog'))
  self.assertEqual(i['baseline']['backlog_cfp'],40)
  self.assertIsNone(i['quantification']['net_extra_jh'])
  self.assertEqual(c['summary']['adopted_java_spring_jh'],sum(u['total_jh'] for u in self.units if u['stack']=='java-spring'))
  self.assertEqual(i['experiment_result']['tests'],18)
  self.assertTrue(all(cell['complete_ba_coverage'] is None for r in c['rows'] for cell in r['cells']))
 def test_trial_is_frozen_and_not_a_product_or_effort_validation(self):
  for mutate in [lambda i:i['experiment'].update(report_sha256='0'*64),lambda i:i['experiment'].update(implementation_sha256='0'*64),lambda i:i.update(status='qualifie'),lambda i:i['quantification'].update(new_equivalent_units=1000),lambda i:i['quantification'].update(new_cfp=0),lambda i:i['quantification'].update(net_extra_jh=0)]:
   spec=deepcopy(self.spec);mutate(self.case(spec))
   with self.subTest(mutate=mutate),self.assertRaisesRegex(ValueError,'ERR_MARKET_COMPARISON|ERR_GAP_INSTRUCTION'):
    build_market_comparison(self.market,spec=spec)
 def test_foreign_needs_and_funding_cannot_be_claimed(self):
  for key in ['need_refs','evidence_refs','mechanism_refs']:
   spec=deepcopy(self.spec);self.case(spec)['criteria'][0][key]=['missing']
   with self.subTest(key=key),self.assertRaisesRegex(ValueError,'ERR_GAP_INSTRUCTION'):
    build_market_comparison(self.market,spec=spec)
 def test_case_proofs_are_in_download_closure(self):
  with model_session() as snapshot:
   c=build_market_comparison(self.market)
   names={p.relative_to(ROOT).as_posix() for p in snapshot.documents}
  i=next(g['instruction'] for g in c['gaps'] if g['id']=='G02')
  self.assertIn(i['experiment']['report_ref'],names);self.assertIn(i['experiment']['implementation_ref'],names)
  self.assertNotIn('sources/client/copil-4.pptx',names)

if __name__=='__main__':unittest.main()
