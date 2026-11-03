"""Regional prices must change funded labor without altering contracts or effort."""
from copy import deepcopy
import unittest
from project_rates import load_rates, compile_rates, regional_study, SOURCE, OBSERVATIONS, province_price
from validate_stacks import ROOT, read
from test_support import reference_study

class ProjectRateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=reference_study()
        cls.variant=regional_study(cls.base,'province')
        cls.rates=cls.base.content['framework']['project_rates']

    def test_region_formula_uses_explicit_ratio_and_half_up_rounding(self):
        self.assertEqual(province_price(1000,.75),750)
        self.assertEqual(province_price(1000,.7625),775)
        self.assertEqual(province_price(850,1.03),875)

    def test_each_role_has_two_positive_prices_and_traceable_geographic_basis(self):
        observations=read(ROOT/OBSERVATIONS)['rate_study']
        self.assertEqual({r['id'] for r in self.rates['roles']},{r['id'] for r in observations['roles']})
        for role in self.rates['roles']:
            self.assertGreater(role['paris'],0);self.assertGreater(role['province'],0)
            self.assertEqual(role['province']%25,0)
            self.assertTrue(role['rationale'] and role['peers'])
            self.assertTrue(all(p['source_id'] in self.rates['sources'] for p in role['peers']))
        pmo=next(r for r in self.rates['roles'] if r['id']=='pmo')
        self.assertGreater(pmo['province'],pmo['paris'])

    def test_missing_role_and_invalid_price_cannot_be_published(self):
        policy=read(ROOT/SOURCE);study=read(ROOT/OBSERVATIONS)['rate_study']
        values={r['id']:r['paris'] for r in self.rates['roles']}
        bad=deepcopy(policy);bad['roles'].pop()
        with self.assertRaisesRegex(ValueError,'ROLE_COVERAGE'):compile_rates(bad,study,values)
        values['backend']=float('nan')
        with self.assertRaisesRegex(ValueError,'RATE_VALUE'):compile_rates(policy,study,values)

    def test_paris_stays_reference_and_personal_simulation_contract_is_unchanged(self):
        self.assertIs(regional_study(self.base,'paris'),self.base)
        self.assertEqual(self.variant.simulation_contract(),self.base.simulation_contract())
        self.assertEqual(next(o for o in self.base.content['framework']['tariffs'] if o['key']=='java-spring')['prices'][0]['value'],550)
        with self.assertRaisesRegex(ValueError,'RATE_ZONE'):regional_study(self.base,'unknown')

    def test_regional_budgets_preserve_efforts_schedules_and_supplier_bundles(self):
        for original,regional in zip(self.base.baseline['options'],self.variant.baseline['options']):
            self.assertEqual(original['stack'],regional['stack'])
            self.assertEqual(original['service_start_month'],regional['service_start_month'])
            self.assertEqual(original['editor_prices'],regional['editor_prices'])
            for key in ('hebergement','ipaas','licences_complementaires'):
                self.assertEqual(original['annual_base'][key],regional['annual_base'][key])
            if original['mode']=='Buy':
                before=next(o for o in self.base.economic['options'] if o['stack']==original['stack'])
                after=next(o for o in self.variant.economic['options'] if o['stack']==original['stack'])
                self.assertEqual(before['detail_integration']['base_rfi'],after['detail_integration']['base_rfi'])
                for a,b in zip(before['maintenance_annuelle'],after['maintenance_annuelle']):
                    for key in ('licences_rfi','forfaits_rfi'):
                        self.assertEqual(a['postes_eur_ht'][key],b['postes_eur_ht'][key])
            if original['stack'] in ('java-spring','microsoft','sap'):
                self.assertNotEqual(original['horizons'],regional['horizons'])
            for h in regional['horizons']:
                self.assertAlmostEqual(sum(h['cost_natures'].values()),h['totals']['total'],2)
        for a,b in zip(self.base.content['economic_evaluations']['options'],self.variant.content['economic_evaluations']['options']):
            if a['core'] and b['core']:
                self.assertEqual(a['core']['total_jh'],b['core']['total_jh'])
