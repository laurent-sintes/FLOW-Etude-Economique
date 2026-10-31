"""Business metamodel, reproducibility and interpretation boundaries."""
from copy import deepcopy
import unittest
from model_context import scoped_model
from unittest.mock import patch
from model_context import model_session
from validate_stacks import ROOT, read
from capability_catalog import native, catalog
from estimation_calculation import metamodel, calculate, alignment, formula, META
from retained_core import validate
from current_cost_inputs import active_doc
from test_support import study_copy

class EstimationCalculationTests(unittest.TestCase):
    def test_native_content_and_relationships_are_unchanged(self):
        snapshot=native()
        nodes={n['id']:n for n in snapshot['nodes']}
        for row in catalog()['rows']:
            self.assertEqual(row['capacite']['native'],nodes[row['capacite_id']])
            self.assertEqual(row['capacite']['nom'],nodes[row['capacite_id']]['fields']['name'])
            self.assertNotIn('complexite',row)
            self.assertNotIn('calibration',row)
        self.assertTrue(snapshot['relations'])

    def test_current_model_does_not_consume_retired_inputs(self):
        with model_session() as session:
            from study_app import Study
            Study()
            paths={str(p).replace('\\','/') for p in session.digests}
            for name in ('grille-complexite.yaml','methode-complexite.yaml','recalibration-metier.yaml','evaluation-core.yaml'):
                self.assertFalse(any(p.endswith('/'+name) for p in paths),name)

    def test_four_references_and_adoption_reproduce(self):
        unit=validate()['units'][0];result=calculate(unit['calculation'])
        self.assertEqual((result['total_jh'],result['months']),(1500,17))
        self.assertEqual(result['roles'],{r['id']:r['jh'] for r in unit['roles']})
        a=result['alignment']
        self.assertEqual(len(a['rows']),4)
        self.assertAlmostEqual(a['reference_jh'],1496.947499268186)
        self.assertAlmostEqual(a['functional']['jh'],1200)
        self.assertAlmostEqual(a['functional']['gap_jh'],1200-a['reference_jh'])
        self.assertAlmostEqual(a['functional']['gap_pct'],100*(1200-a['reference_jh'])/a['reference_jh'])
        self.assertAlmostEqual(a['rounding_delta_jh'],1500-a['reference_jh'])
        self.assertAlmostEqual(a['spread_jh'],164.2050916852886)
        self.assertAlmostEqual(sum(r['jh'] for r in result['activities']),1500)

    @scoped_model
    def test_decision_drift_is_rejected(self):
        for field,value in [('method','invented'),('months',99)]:
            document=validate();document['units'][0][field]=value
            with self.assertRaises(AssertionError):validate(document)
        document=validate()
        document['units'][0]['roles'][0]['jh']+=10
        document['units'][0]['roles'][1]['jh']-=10
        with self.assertRaisesRegex(AssertionError,'allocation drift'):validate(document)
        document=validate();document['units'][0]['calculation']['id']='invented'
        with self.assertRaisesRegex(ValueError,'Unknown calculation'):validate(document)

    def test_alignment_is_not_a_probability_and_handles_missing_denominator(self):
        self.assertEqual(alignment(80,100)['gap_pct'],-20)
        self.assertIsNone(alignment(80,0)['gap_pct'])
        self.assertEqual(alignment(80,0)['reason'],'nonpositive_reference')
        self.assertIsNone(alignment(None,100)['gap_jh'])
        self.assertEqual(alignment(100,100)['gap_pct'],0)

    def test_arithmetic_is_restricted_and_schema_rejects_unknown_relations(self):
        with self.assertRaises(ValueError):formula('signed_gap',candidate=1,reference=float('nan'))
        with self.assertRaises(ValueError):formula('signed_gap',candidate=1,reference=2,discount=.8)
        real=read
        bad=read(ROOT/META);bad['estimation_model']['relations'][0]['target']='invented'
        def source(path):return deepcopy(bad) if path==ROOT/META else real(path)
        with patch('estimation_calculation.read',side_effect=source):
            with self.assertRaisesRegex(ValueError,'endpoint'):metamodel()
        bad=read(ROOT/META)
        rule=next(r for r in bad['estimation_model']['rules'] if r['id']=='signed_gap')
        rule['expression']="__import__('os')"
        with patch('estimation_calculation.read',side_effect=source):
            with self.assertRaisesRegex(ValueError,'Unsupported'):formula('signed_gap',candidate=1,reference=2)

    def test_buy_and_annual_inputs_remain_separate(self):
        for slug in ('java-spring','dotnet','rust'):
            self.assertFalse(active_doc(slug)['core'])
        study=study_copy()
        self.assertEqual(study.baseline['options'][0]['build'],4198680)
        self.assertEqual(len(study.content['business_map']['family_funding']),11)
        self.assertFalse(study.content['business_map']['funding'])

if __name__=='__main__':unittest.main()
