"""Scope replacement is explicit, reproducible and outside the retained ledger."""
from copy import deepcopy
import hashlib
import unittest
from scope_revision import compile_revision,SOURCE,dependencies
from validate_stacks import ROOT,read
from test_support import reference_study

class ScopeRevisionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.study=reference_study();cls.units=next(o for o in cls.study.economic['options'] if o['stack']=='java-spring')['core_units']
 def test_replacement_conserves_retained_decisions(self):
  before=deepcopy(self.units);raw=(ROOT/'source/estimations-core-retenues.yaml').read_bytes();d=compile_revision(self.units)
  self.assertEqual(self.units,before);self.assertEqual((ROOT/'source/estimations-core-retenues.yaml').read_bytes(),raw)
  self.assertEqual({lot['id']:lot['jh'] for lot in d['lots']},{'master-data':2670,'operational-references':400})
  self.assertEqual(sum(lot['cost_eur_ht'] for lot in d['lots']),d['proposed']['cost_eur_ht'])
  self.assertIn('Conception',next(p for p in d['packages'] if p['id']=='OR02')['label'])
  self.assertEqual(d['reference']['jh'],1600);self.assertEqual(d['proposed']['jh'],3070);self.assertEqual(d['delta']['jh'],1470);self.assertEqual(d['core_reference']['jh'],7630);self.assertEqual(d['core_proposed']['jh'],9100)
  self.assertEqual(sum(w['jh'] for w in d['prior_work']),1600)
  self.assertEqual([g['jh'] for g in d['groups']],[400,1940,730]);self.assertEqual(d['scope']['total_capabilities'],116);self.assertEqual(d['scope']['target_lot_capabilities'],34);self.assertEqual(len(d['scope']['removed']),5)
  for g in d['groups']:
   self.assertEqual(sum(r['net_jh'] for r in g['roles']),g['jh']);self.assertEqual(g['cost_eur_ht'],g['labour_eur_ht']+g['tooling_eur_ht'])
  self.assertEqual(d['core_proposed']['cost_eur_ht'],d['core_reference']['cost_eur_ht']+d['delta']['cost_eur_ht']);self.assertTrue(all(u['value'] is None for u in d['unknowns']))
 def test_wrong_capture_duplicate_work_and_out_of_scope_capability_are_rejected(self):
  for change in ('capture','duplicate','coverage','lot','binding'):
   d=read(ROOT/SOURCE)
   if change=='capture':d['capture']['sha256']='0'*64
   elif change=='duplicate':d['packages'].append(deepcopy(d['packages'][0]))
   elif change=='coverage':d['packages'][0]['capability_refs']=['cap-mdm-authority']
   elif change=='lot':d['lots'][1]['group_refs'].append('common')
   else:d['work_unit_ref']='core/other'
   with self.subTest(change=change),self.assertRaisesRegex(ValueError,'ERR_SCOPE_REVISION'):compile_revision(self.units,d)
 def test_both_domains_are_in_current_context_without_rewriting_historical_capture(self):
  self.assertEqual(self.study.fundamentals['business_map']['positioning']['domain_refs'],['domain-master-data','supply-chain-orchestration'])
  ref=read(ROOT/'source/referentiel-capacites.yaml');self.assertEqual(hashlib.sha256((ROOT/ref['source']).read_bytes()).hexdigest(),ref['sha256'])
  self.assertTrue({SOURCE,'sources/cartographie-business-operations-2026-11-05.svg'}<=dependencies())
