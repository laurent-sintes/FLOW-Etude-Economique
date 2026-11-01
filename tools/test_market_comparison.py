from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch
from validate_stacks import ROOT,read
from market_comparison import build_market_comparison,SOURCE
from market_instruction import build_market_instruction
from market_reading import build_market_reading
from capability_catalog import native,analysis

class MarketComparisonTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.market=read(ROOT/'source/references-couts-integration.yaml');cls.market['instruction']=build_market_instruction(cls.market)
  cls.spec=read(ROOT/SOURCE);cls.snapshot=native();cls.grid=analysis()
  cls.mechanisms=read(ROOT/'source/calculs-estimation-core.yaml')['mechanisms'];cls.retained=read(ROOT/'source/estimations-core-retenues.yaml')['units']
 def build(self,spec=None,market=None):
  return build_market_comparison(self.market if market is None else market,spec=self.spec if spec is None else spec,snapshot=self.snapshot,grid=self.grid,mechanisms=self.mechanisms,retained=self.retained)
 def test_native_matrix_exclusions_and_unknowns_are_preserved(self):
  original=deepcopy(self.spec);c=self.build();self.assertEqual(self.spec,original)
  self.assertEqual(c['summary']['compared_capabilities'],84);self.assertEqual(c['summary']['compared_business_areas'],27)
  pairs={(r['id'],s['product_ref']) for r in c['rows'] for s in r['cells']};self.assertEqual(len(pairs),28*6)
  nodes={n['id']:n for n in self.snapshot['nodes']}
  for r in c['rows']:
   self.assertEqual(r['name'],nodes[r['id']]['fields']['name'])
   self.assertEqual({x['id'] for x in r['capabilities']},{b['capacite_id'] for b in self.grid['blocs'] if b['chemin'][-2]==r['id']})
  excluded=[r for r in c['rows'] if not r['included']];self.assertEqual(len(excluded),1)
  self.assertTrue(all(x['reading_status']=='hors_perimetre' for x in excluded[0]['cells']))
  self.assertTrue(all(x['complete_ba_coverage'] is None for r in c['rows'] for x in r['cells']))
 def test_hierarchy_is_native_and_documentary_comparison_excludes_estimates(self):
  c=self.build();nodes={n['id']:n for n in self.snapshot['nodes']}
  for row in c['rows']:
   block=next(b for b in self.grid['blocs'] if b['chemin'][-2]==row['id'])
   self.assertEqual([n['id'] for n in row['hierarchy']],block['chemin'][:-2])
   self.assertEqual([n['name'] for n in row['hierarchy']],[nodes[k]['fields']['name'] for k in block['chemin'][:-2]])
  market=deepcopy(self.market);market['comparison']=c
  shown=build_market_reading(market)['documentary_comparison']
  self.assertNotIn('summary',shown);self.assertNotIn('budget_review',shown)
  self.assertTrue(all('instruction' not in g and 'funding_candidates' not in g for g in shown['gaps']))
  self.assertEqual(shown['rows'],c['rows'])
 def test_no_false_coverage_or_budget(self):
  c=self.build();self.assertEqual(c['summary']['adopted_java_spring_jh'],sum(u['total_jh'] for u in self.retained if u['stack']=='java-spring'))
  self.assertIsNone(c['summary']['net_extra_jh']);self.assertEqual(c['summary']['reviewed_business_area_pairs'],0)
  def false_coverage(s):s['business_areas'][0]['assessments'][0].update(complete_ba_coverage=True,review=dict(date='2026-10-31',reviewer='Test',decision='retenu'))
  for mutate in [false_coverage,lambda s:s['business_areas'][0]['assessments'][0].update(complete_ba_coverage=False),lambda s:s['gaps'][0].update(net_extra_jh=0),lambda s:s['gaps'][0].update(net_extra_initial_eur_ht=1000),lambda s:s['gaps'][0].update(treatment_status='traite'),lambda s:s['business_areas'][0]['assessments'][0].update(coverage_pct=100)]:
   with self.subTest(mutate=mutate):
    s=deepcopy(self.spec);mutate(s)
    with self.assertRaisesRegex(ValueError,'ERR_MARKET_COMPARISON'):self.build(s)
 def test_unknown_duplicate_and_mismatched_links_are_rejected(self):
  mutations=[lambda s:s['business_areas'].pop(),lambda s:s['business_areas'].append(deepcopy(s['business_areas'][0])),lambda s:s['business_areas'][0]['assessments'].pop(),lambda s:s['business_areas'][0]['assessments'][0].update(product_ref='missing'),lambda s:s['gaps'][0].update(evidence_refs=['missing']),lambda s:s['gaps'][0].update(funding_owner_refs_to_reconcile=['missing']),lambda s:s['sources'][0].update(source_ref='../secret'),lambda s:s['rfi_crosswalk'][0].update(proposed_need_refs=['BC-001.01']),lambda s:s['rfi_crosswalk'][0].update(gap_ref='G06')]
  for mutate in mutations:
   with self.subTest(mutate=mutate):
    s=deepcopy(self.spec);mutate(s)
    with self.assertRaisesRegex(ValueError,'ERR_MARKET_COMPARISON'):self.build(s)
 def test_frozen_reading_and_mutations_are_isolated(self):
  m=deepcopy(self.market);m['comparison']=self.build()
  with patch.object(Path,'read_bytes',side_effect=AssertionError('No documentary IO')):
   shown=build_market_reading(m)
  self.assertEqual(shown['comparison'],m['comparison']);shown['comparison']['rows'].clear();self.assertTrue(m['comparison']['rows'])
 def test_shared_gap_funding_and_compositions_are_referenced(self):
  c=self.build();sources={s['id']:s for s in c['sources']}
  self.assertIn('110',sources['ms-season']['location']);self.assertIn('248',sources['sap-backlog']['location'])
  for p in c['products']:
   fiche=self.market['reperes_build_core']['fiches_produit'][p['id']]
   self.assertEqual(p['components'],fiche['composition']['produits']);self.assertEqual(p['version'],fiche['version_edition'])
  self.assertEqual(len(c['gaps']),len({g['id'] for g in c['gaps']}))
  for g in c['gaps']:
   self.assertIsNone(g['net_extra_jh']);self.assertEqual(len(g['funding_candidates']),len({m['id'] for m in g['funding_candidates']}))
 def test_details_are_deferred_and_packaged_with_the_metamodel(self):
  from test_support import study_copy
  from model_context import model_session
  from export_business_model import compose
  from estimation_calculation import metamodel
  study=study_copy();essential=study.bootstrap(essential=True)
  self.assertNotIn('comparison',essential['content']['market_method'])
  self.assertEqual(set(study.ui['essential']['estimation_model']),{'rules','implementations'})
  self.assertEqual(study.content['market']['comparison']['summary']['products'],6)
  with model_session() as snapshot:
   read(ROOT/SOURCE);read(ROOT/'source/schema-comparaison-solutions.yaml');read(ROOT/'source/fondamentaux.yaml')
   package=compose(snapshot.documents,snapshot.digests)
  self.assertIn(SOURCE,package['model']);self.assertIn('source/schema-comparaison-solutions.yaml',package['schemas'])
  self.assertIn('solution_gap',{x['id'] for x in metamodel()['objects']})

if __name__=='__main__':unittest.main()
