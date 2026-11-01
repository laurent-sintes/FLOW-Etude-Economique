"""The economic page projects one frozen reference, with no alternate calculations."""
from copy import deepcopy
from unittest.mock import patch
import unittest

from document_excerpt import document_excerpt
from economic_reading import ANNUAL_KEYS, SOURCE, compile_economic_evaluations
from test_support import study_copy
from validate_stacks import ROOT, read


class EconomicReadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = study_copy()
        cls.editorial = read(ROOT / SOURCE)

    def compile(self, **changes):
        arguments = dict(baseline=self.study.baseline, content=self.study.content,
                         editorial=self.editorial, glossary=self.study.glossary,
                         document_path=self.study.document_path, inputs=self.study.data['options'][0]['composable']['inputs'])
        arguments.update(changes)
        return compile_economic_evaluations(**arguments)

    def test_every_amount_and_duration_follows_its_loaded_owner(self):
        result = self.compile()
        self.assertEqual(result['model_version'], self.study.version)
        self.assertEqual([o['stack'] for o in result['options']], [o['stack'] for o in self.study.baseline['options']])
        self.assertEqual(len(result['options']), 5)
        for option, original in zip(result['options'], self.study.baseline['options']):
            with self.subTest(stack=option['stack']):
                self.assertEqual(option['integration']['budget_eur_ht'], original['integration'])
                duration = (self.study.baseline['make_integration_months'] if original['mode'] == 'Make'
                            else self.study.parameters['options'][original['stack']]['integration_mois'])
                self.assertEqual(option['integration']['months'], duration)
                self.assertEqual(option['annual']['total_eur_ht'], self.study.content['stacks'][original['stack']]['economic_reading']['total'])
                self.assertEqual(option['annual']['service_allocation'], original['services'])
                for key in ANNUAL_KEYS[:-1]:
                    self.assertEqual(option['annual']['items'][key], original['annual_base'][key])
                if original['mode'] == 'Make':
                    self.assertIsNone(option['selection'])
                    self.assertIsNone(option['annual']['items']['offre_editeur'])
                else:
                    self.assertEqual(option['selection']['budget_eur_ht'], original['selection_buy'])
                    self.assertEqual(option['selection']['months'], original['selection_months'])
                    self.assertEqual(option['annual']['items']['offre_editeur'], original['editor_prices'][0])
                    self.assertIsNone(option['annual']['service_allocation']['core'])
        self.assertEqual(result, self.study.content['economic_evaluations'])

    def test_compile_does_not_read_sources_or_mutate_reference_and_returns_isolated_values(self):
        baseline, content, editorial = deepcopy(self.study.baseline), deepcopy(self.study.content), deepcopy(self.editorial)
        with patch('economic_reading.read', side_effect=AssertionError('unexpected read')):
            result = self.compile()
        result['options'][0]['annual']['items']['services_mco'] = -1
        result['options'][0]['annual']['service_allocation']['core'] = -1
        result['editorial']['sections']['annual']['rows'].clear()
        self.assertEqual(self.study.baseline, baseline)
        self.assertEqual(self.study.content, content)
        self.assertEqual(self.editorial, editorial)

    def test_mismatched_totals_and_option_coverage_fail_before_publication(self):
        baseline = deepcopy(self.study.baseline)
        baseline['options'][0]['integration'] += 1
        with self.assertRaisesRegex(ValueError, 'integration ownership'):
            self.compile(baseline=baseline)
        baseline = deepcopy(self.study.baseline)
        baseline['options'][0]['annual_base']['hebergement'] += 1
        with self.assertRaisesRegex(ValueError, 'annual ownership'):
            self.compile(baseline=baseline)
        baseline = deepcopy(self.study.baseline)
        baseline['options'].pop()
        with self.assertRaisesRegex(ValueError, 'option coverage'):
            self.compile(baseline=baseline)
        baseline = deepcopy(self.study.baseline)
        baseline['options'][0]['editor_prices'] = [0]
        with self.assertRaisesRegex(ValueError, 'editor price sequence'):
            self.compile(baseline=baseline)

    def test_source_schema_and_editorial_links_are_strict(self):
        editorial = deepcopy(self.editorial)
        editorial['unknown'] = 'rejected'
        with self.assertRaisesRegex(ValueError, 'ERR_ECONOMIC_READING'):
            self.compile(editorial=editorial)
        editorial = deepcopy(self.editorial)
        editorial['sections']['annual']['rows'].reverse()
        with self.assertRaisesRegex(ValueError, 'annual row contract'):
            self.compile(editorial=editorial)
        editorial = deepcopy(self.editorial)
        editorial['links'][0]['href'] = '#missing'
        with self.assertRaisesRegex(ValueError, 'ERR_ECONOMIC_READING'):
            self.compile(editorial=editorial)
        editorial = deepcopy(self.editorial)
        editorial['sections']['annual']['sources'][0]['path'] = 'source/missing.yaml'
        with self.assertRaisesRegex(ValueError, 'missing_document'):
            self.compile(editorial=editorial)

    def test_readable_details_reconcile_and_preserve_their_source_work(self):
        result=self.compile()
        for option,original in zip(result['options'],self.study.baseline['options']):
            self.assertEqual([r['amount'] for r in option['integration']['detail']],[r['amount'] for r in original['funding_ledger'] if r['phase']=='integration'])
            self.assertAlmostEqual(sum(r['amount'] for r in option['integration']['detail']),original['integration'],places=2)
            if option['mode']=='Make':
                core=option['core']
                self.assertEqual(core['total_jh'],sum(u['total_jh'] for u in core['units']))
                self.assertEqual(len(core['features']),88)
                self.assertTrue(all(not row['charges'] for row in core['features']))
                self.assertFalse(core['natures'])
            else:self.assertIsNone(option['core'])
        result['options'][0]['core']['units'][0]['roles'][0]['jh']=-1
        self.assertGreater(self.study.content['stacks'][result['options'][0]['stack']]['economic']['core_units'][0]['roles'][0]['jh'],0)

    def test_inconsistent_documentary_decompositions_are_rejected(self):
        content=deepcopy(self.study.content)
        content['stacks']['java-spring']['economic']['core_units'][0]['total_jh']+=1
        with self.assertRaisesRegex(ValueError,'core charge ownership'):
            self.compile(content=content)
        content=deepcopy(self.study.content)
        content['stacks']['java-spring']['economic_reading']['buckets']['socle']['total']+=1
        with self.assertRaisesRegex(ValueError,'annual detail ownership'):
            self.compile(content=content)

    def test_cost_bridges_conserve_all_options_and_horizons(self):
        before = deepcopy(self.study.baseline)
        for reading, option in zip(self.compile()['options'], before['options']):
            if option['mode'] == 'Buy':
                self.assertAlmostEqual(sum(reading['integration']['offer_bridge'].values()), option['integration'], places=2)
            else:
                self.assertIsNone(reading['integration']['offer_bridge'])
            for bridge, horizon in zip(reading['spending_bridge'], option['horizons']):
                self.assertEqual(bridge['years'], horizon['years'])
                self.assertGreaterEqual(bridge['recurring_eur_ht'], 0)
                self.assertAlmostEqual(bridge['transition_eur_ht']+bridge['recurring_eur_ht'], horizon['totals']['mco_run'], places=2)
        self.assertEqual(self.study.baseline, before)
        java = next(row for row in self.compile()['options'] if row['stack']=='java-spring')
        last = next(row for row in java['spending_bridge'] if row['years']==10)
        self.assertAlmostEqual(last['transition_eur_ht'], 1294824.15, places=2)
        self.assertAlmostEqual(last['recurring_eur_ht'], 3898507.05, places=2)

    def test_offer_bridge_rejects_an_unowned_supplement(self):
        content = deepcopy(self.study.content)
        content['stacks']['microsoft']['economic']['detail_integration']['complements_flow'] += 1
        with self.assertRaisesRegex(ValueError, 'offer bridge ownership'):
            self.compile(content=content)

    def test_dimensioning_follows_loaded_inputs_and_is_isolated(self):
        result = self.compile()
        inputs = self.study.data['options'][0]['composable']['inputs']['volumes']
        self.assertEqual(result['drivers']['perimeter'], inputs['perimetre'])
        self.assertEqual(result['drivers']['annual_volumes'], inputs['volumes'])
        result['drivers']['perimeter']['utilisateurs_nominatifs'] = -1
        self.assertGreater(inputs['perimetre']['utilisateurs_nominatifs'], 0)

    def test_completion_spending_includes_early_contracts_and_all_transition_costs(self):
        result = self.compile()
        known = {'java-spring':8170877.10, 'microsoft':7620227.45, 'sap':16850516.68}
        for option in result['options']:
            original = next(o for o in self.study.baseline['options'] if o['stack']==option['stack'])
            completion = option['service_completion']
            self.assertEqual(completion['month'], original['service_start_month'])
            self.assertAlmostEqual(completion['initial_eur_ht']+completion['subscriptions_eur_ht'], completion['total_eur_ht'], places=2)
            self.assertAlmostEqual(completion['initial_eur_ht'], sum(row['amount'] for row in original['funding_ledger']), places=2)
            if option['mode']=='Make':self.assertEqual(completion['subscriptions_eur_ht'],0)
            else:self.assertGreater(completion['subscriptions_eur_ht'],0)
            if option['stack'] in known:self.assertAlmostEqual(completion['total_eur_ht'],known[option['stack']],places=2)
        ms = next(o for o in result['options'] if o['stack']=='microsoft')['service_completion']
        self.assertAlmostEqual(ms['subscriptions_eur_ht'],3100171.45,places=2)
        result['options'][0]['service_completion']['total_eur_ht']=-1
        self.assertGreater(self.compile()['options'][0]['service_completion']['total_eur_ht'],0)

    def test_completion_rejects_a_journal_extending_beyond_the_service_date(self):
        baseline=deepcopy(self.study.baseline)
        option=baseline['options'][0]
        next(line for line in option['funding_ledger'] if line['phase']=='mco_run')['end']=option['service_start_month']+1
        with self.assertRaisesRegex(ValueError,'completion journal'):
            self.compile(baseline=baseline)

    def test_comparison_keeps_the_same_horizon_and_reference(self):
        reference=next(o for o in self.study.baseline['options'] if o['stack']=='java-spring')
        for reading in self.compile()['options']:
            option=next(o for o in self.study.baseline['options'] if o['stack']==reading['stack'])
            self.assertEqual(reading['comparison']['reference'],reference['stack'])
            for row in reading['comparison']['horizons']:
                value=next(h['totals']['total'] for h in option['horizons'] if h['years']==row['years'])
                anchor=next(h['totals']['total'] for h in reference['horizons'] if h['years']==row['years'])
                self.assertAlmostEqual(anchor+row['difference_eur_ht'],value,places=2)
                self.assertGreaterEqual(row['amount_eur_ht'],0)
                self.assertEqual(row['direction'],'higher' if value>anchor else 'lower' if value<anchor else 'equal')

    def test_projected_years_distinguish_project_transition_and_full_service(self):
        result={o['stack']:{r['year']:r['stage'] for r in o['annual']['projected_stages']} for o in self.compile()['options']}
        for slug,before,partial,full in [('java-spring',6,7,8),('microsoft',3,4,5)]:
            self.assertEqual(result[slug][before],'before_service')
            self.assertEqual(result[slug][partial],'partial_service')
            self.assertEqual(result[slug][full],'full_service')
        self.assertEqual(result['sap'][3],'before_service')
        self.assertEqual(result['sap'][4],'full_service')

    def test_sponsor_sections_reject_duplicated_or_misassigned_topics(self):
        for field,reason in [('determinants','sponsor determinant contract'),('scope_rows','sponsor scope contract')]:
            editorial=deepcopy(self.editorial)
            editorial['sponsor'][field][0]=deepcopy(editorial['sponsor'][field][1])
            with self.assertRaisesRegex(ValueError,reason):
                self.compile(editorial=editorial)

    def test_documentary_fragments_reach_complete_evidence(self):
        paths = set()

        def collect(value):
            if isinstance(value, dict):
                for entry in value.values():
                    collect(entry)
            elif isinstance(value, list):
                for entry in value:
                    collect(entry)
            elif isinstance(value, str) and value.startswith('source/'):
                paths.add(value)

        collect(self.compile())
        for reference in paths:
            with self.subTest(reference=reference):
                filename, _, fragment = reference.partition('#')
                path = self.study.document_path(filename)
                self.assertTrue(path.is_file())
                if fragment:
                    result = document_excerpt(path.read_text(encoding='utf-8'), path.suffix, fragment)
                    self.assertEqual(result['focus']['status'], 'matched')


if __name__ == '__main__':
    unittest.main()
