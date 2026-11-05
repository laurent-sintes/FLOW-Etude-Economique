"""Guard the adopted project effort against double funding and false precision."""
from test_support import active_reference
from capability_catalog import analysis
from copy import deepcopy
import unittest
from model_context import scoped_model
from unittest.mock import patch
from jsonschema import ValidationError
from retained_core import validate, value_units, coverage
from calculate_costs import calculate_option
from test_support import study_copy
from current_cost_inputs import active_doc


class RetainedCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = study_copy()

    def test_adopted_scope_role_sum_and_cost_identity(self):
        economic = self.study.content['stacks']['java-spring']['economic']
        unit = next(u for u in economic['core_units'] if u['id']=='master-data-java-spring')
        self.assertEqual((unit['total_jh'], unit['months']), (active_reference()['units']['master-data-java-spring']['jh'], active_reference()['units']['master-data-java-spring']['months']))
        self.assertEqual(sum(r['jh'] for r in unit['roles']), active_reference()['units']['master-data-java-spring']['jh'])
        self.assertEqual({r['id']:r['jh'] for r in unit['roles']}, active_reference()['units']['master-data-java-spring']['roles'])
        self.assertEqual(unit['labour_eur_ht'], sum(r['jh']*r['rate_eur_jh'] for r in unit['roles']))
        self.assertEqual(unit['cost_eur_ht'], unit['labour_eur_ht']+unit['tooling_eur_ht'])
        self.assertEqual(economic['detail_build']['prestations'], sum(u['cost_eur_ht'] for u in economic['core_units']))
        self.assertEqual(economic['detail_build']['pilotage'], 0)
        self.assertEqual(economic['jh']['core_project_roles_jh'], active_reference()['total_jh'])
        self.assertEqual(economic['jh']['core_backend'], 0)  # no project roles disguised as backend days
        self.assertEqual(economic['jh']['core_frontend'], 0)
        self.assertEqual(economic['jh']['core_avant_ia'], active_reference()['total_jh'])

    def test_legacy_ai_and_coordination_do_not_reduce_or_inflate_family(self):
        calibration = deepcopy(self.study.content['calibration'])
        calibration['pilotage']['build_pct'] = 75
        calibration['ia']['taux_pct']['java-spring'] = {k:99 for k in calibration['ia']['taux_pct']['java-spring']}
        calibration['ia']['frontend_pct'] = 99
        changed = calculate_option('java-spring', active_doc('java-spring'), calibration, service_years=1)
        ref = self.study.content['stacks']['java-spring']['economic']
        self.assertEqual(changed['detail_build'], ref['detail_build'])
        self.assertEqual(changed['core_units'], ref['core_units'])

    def test_unknown_coverage_and_family_delay_are_not_global_delivery(self):
        rows = {r['stack']:r for r in self.study._essential_core_evaluation()}
        java = rows['java-spring']
        blocks = {b['id'] for b in analysis()['blocs']}
        self.assertEqual((java['coverage']['covered'],java['coverage']['total'],java['coverage']['remaining']),
                         (len(blocks),len(blocks),0))
        self.assertIsNone(java['uncertainty_pct'])
        self.assertEqual(set(java['coverage']['remaining_capabilities']), blocks-{c['id'] for u in java['units'] for c in u['capabilities']})
        for slug in ('dotnet','rust'):
            self.assertEqual(rows[slug]['coverage']['covered'],0)
            self.assertEqual(rows[slug]['estimation_status'],'pending_reestimation')
            self.assertFalse(rows[slug]['units'])
        self.assertNotEqual(self.study.baseline['parameters']['options']['java-spring']['build_mois'],java['units'][0]['months'])
        u = java['units'][0]
        self.assertIsNone(u['uncertainty']['confidence_level'])
        self.assertAlmostEqual(u['schedule']['average_fte']*u['months']*u['schedule']['productive_jh_per_month'],active_reference()['units']['master-data-java-spring']['jh'])

    @scoped_model
    def test_invalid_or_duplicate_funding_is_rejected(self):
        for mutate, message in [
            (lambda d:d['units'].append(deepcopy(d['units'][0])), 'Duplicate family owner'),
            (lambda d:d['units'][0]['roles'][0].update(jh=171), 'Role effort reconciliation'),
            (lambda d:d['units'][0]['capabilities'].append(deepcopy(d['units'][0]['capabilities'][0])), 'Duplicate family capability'),
            (lambda d:d['units'][0]['capabilities'][0].update(native_id='invented'), 'Unknown native'),
            (lambda d:d['units'][0]['provenance'].update(sha256='0'*64), 'evidence changed'),
        ]:
            doc = validate(); mutate(doc)
            with self.assertRaisesRegex(AssertionError,message): validate(doc)
        doc=validate();doc['units'][0]['invented_discount']=.8
        with self.assertRaises(ValidationError): validate(doc)
        features=[dict(feature='BC-002',plages_jh={'central':{'developpement':1}})]
        with self.assertRaisesRegex(AssertionError,'overlaps legacy'):value_units('java-spring',features,8)

    def test_family_is_not_split_or_repeated_on_capabilities(self):
        metrics=self.study.content['journey']['metrics']
        family=metrics['work_totals']['java-spring']
        self.assertEqual(family['family_jh'],active_reference()['total_jh'])
        caps=metrics['map']['capabilities']
        covered=[c for c in caps.values() if c['stacks']['java-spring']['retained_units']]
        self.assertEqual(len(covered),len(analysis()['blocs']))
        self.assertTrue(all(c['stacks']['java-spring']['raw_jh']['central'] is None for c in covered))
        retained_ids = {unit['id'] for unit in validate()['units']}
        self.assertTrue(all(c['stacks']['java-spring']['retained_units'][0]['id'] in retained_ids for c in covered))


if __name__ == '__main__':
    unittest.main()
