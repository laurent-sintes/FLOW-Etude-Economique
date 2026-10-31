"""Independent arithmetic examples and automated canonical contract gates."""
from copy import deepcopy
import unittest
from unittest.mock import patch
from jsonschema import ValidationError
from estimation_calculation import metamodel, formula, evaluate_rule
from model_context import model_session
from business_contract import coverage_report

# Literal expected values are independent of the production expression evaluator.
ARITHMETIC_CASES = {
 'cocomo_exponent': ({'B':1, 'SF_sum':10}, 1.1),
 'schedule_exponent': ({'D':.3, 'E':1.5, 'B':1}, .4),
 'cocomo_effort': ({'A':2, 'KSLOC':4, 'E':1, 'EM':1, 'SCED':1, 'month_hours':140, 'day_hours':7, 'effort_phase_factor':1}, 160),
 'cosmic_effort': ({'CFP':10, 'hours_per_CFP':7, 'factor':1, 'day_hours':7}, 10),
 'cocomo_schedule': ({'C':2, 'JH':20, 'effort_phase_factor':1, 'day_hours':7, 'month_hours':140, 'SCED':1, 'F':1, 'schedule_phase_factor':1}, 2),
 'signed_gap': ({'candidate':80, 'reference':100}, -20),
 'signed_gap_pct': ({'candidate':80, 'reference':100}, -20),
 'spread': ({'maximum':120, 'minimum':80}, 40),
 'spread_pct': ({'maximum':120, 'minimum':80, 'reference':100}, 40),
 'implied_productivity': ({'JH':10, 'day_hours':7, 'CFP':5}, 14),
 'role_price': ({'JH':10, 'rate':600}, 6000),
 'average_team': ({'JH':100, 'months':5, 'capacity':20}, 1),
 'coverage': ({'covered':20, 'total':80}, 25),
 'reuse_assimilation': ({'AA':2, 'IM':10}, .05),
 'equivalent_size': ({'new_program':10, 'new_declarative':4, 'reused_program':20, 'reused_declarative':8, 'w':.5, 'AAM':.1}, 14.4),
 'module_analogy': ({'reference_units':100, 'fraction':.2, 'scaffold_units':5}, 25),
 'purpose_unallocated_jh': ({'total':100, 'business':60, 'it':30}, 10),
 'purpose_unallocated_cost': ({'total':100, 'business':60, 'it':30}, 10),
}


class ArithmeticContractTests(unittest.TestCase):
    pass


def example(rule_id, values, expected):
    def check(self):
        with model_session():
            rule = next(r for r in metamodel()['rules'] if r['id'] == rule_id)
            self.assertEqual(set(values), set(rule['variables']))
            self.assertAlmostEqual(formula(rule_id, **values), expected)
            for key in values:
                invalids = [True, None, float('nan'), float('inf'), -1]
                domain = rule['domains'][key]
                if 'exclusiveMinimum' in domain:
                    invalids.append(domain['exclusiveMinimum'])
                if 'maximum' in domain:
                    invalids.append(domain['maximum'] + 1)
                for invalid in invalids:
                    with self.subTest(variable=key, invalid=invalid):
                        changed = dict(values, **{key: invalid})
                        with self.assertRaises((ValueError, ValidationError)):
                            formula(rule_id, **changed)
    return check


for _id, (_values, _expected) in ARITHMETIC_CASES.items():
    setattr(ArithmeticContractTests, 'test_' + _id, example(_id, _values, _expected))


class BusinessContractTests(unittest.TestCase):
    def test_every_rule_has_a_real_regression_and_new_rules_fail(self):
        report = coverage_report()
        self.assertTrue(report['rules'])
        model = deepcopy(metamodel())
        model['rules'].append(dict(model['rules'][0], id='uncovered_rule'))
        with self.assertRaisesRegex(ValueError, 'coverage drift'):
            coverage_report(model)
        with self.assertRaisesRegex(ValueError, 'Missing executable'):
            coverage_report(available=set())

    def test_formula_index_cannot_leak_public_mutations_or_cross_sessions(self):
        import estimation_calculation as engine
        with patch.object(engine, 'metamodel', wraps=metamodel) as load:
            with model_session():
                self.assertEqual(formula('signed_gap', candidate=3, reference=1), 2)
                public = metamodel()
                next(r for r in public['rules'] if r['id']=='signed_gap')['expression']='0'
                self.assertEqual(formula('signed_gap', candidate=3, reference=1), 2)
                self.assertEqual(load.call_count, 1)
            with model_session():
                self.assertEqual(formula('signed_gap', candidate=3, reference=1), 2)
            self.assertEqual(load.call_count, 2)
        rule = next(r for r in metamodel()['rules'] if r['id']=='signed_gap')
        rule['expression']='candidate + reference'
        self.assertEqual(evaluate_rule(rule, candidate=3, reference=1), 4)

    def test_changed_rules_and_relations_are_revalidated(self):
        from validate_stacks import ROOT, read
        from estimation_calculation import META
        document = read(ROOT/META)
        document['estimation_model']['relations'][0]['target']='absent'
        with model_session(), self.assertRaisesRegex(ValueError, 'endpoint'):
            metamodel(document)
        document = read(ROOT/META)
        document['estimation_model']['rules'].append(deepcopy(document['estimation_model']['rules'][0]))
        with model_session(), self.assertRaisesRegex(ValueError, 'Duplicate'):
            metamodel(document)
