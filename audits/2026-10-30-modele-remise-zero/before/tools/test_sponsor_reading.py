"""Sponsor atlas: native partitions, exact published sums and live source values."""
from collections import Counter
from copy import deepcopy
from decimal import Decimal
import unittest

from sponsor_reading import MAKE, metrics, validate_editorial
from test_support import study_copy
from study_app import Study


def decimal_sum(values):
    return sum((Decimal(str(value)) for value in values), Decimal(0))


class SponsorReadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = study_copy()

    def test_atlas_partitions_native_scope_without_transverse_or_neighbors(self):
        source = self.study.content['business_map']
        atlas = self.study.content['journey']['metrics']['map']
        expected = {row['capacite_id'] for row in source['rows']}
        self.assertEqual(set(atlas['capabilities']), expected)
        self.assertEqual(len(atlas['areas']), 9)
        self.assertEqual(len(atlas['business_areas']), 28)
        for groups in (atlas['areas'], atlas['business_areas']):
            self.assertEqual(Counter(cap for group in groups for cap in group['capabilities']),
                             Counter({identifier: 1 for identifier in expected}))
        self.assertFalse(expected.intersection(node['id'] for node in atlas['neighbors']))
        self.assertEqual(atlas['source'], source['source'])
        for row in source['rows']:
            cap = atlas['capabilities'][row['capacite_id']]
            self.assertEqual(cap['path'], row['chemin'])
            self.assertEqual(cap['name'], row['capacite']['nom'])
            self.assertEqual(cap['block'], row['id'])

    def test_cost_layers_reconcile_owned_work_then_transverse_then_pilotage(self):
        result = self.study.content['journey']['metrics']
        atlas = result['map']
        for slug in MAKE:
            total = result['work_totals'][slug]
            transverse = result['transverse'][slug]
            for groups in (atlas['areas'], atlas['business_areas'], atlas['capabilities'].values()):
                attributed = decimal_sum(group['stacks'][slug]['prestations_eur_ht'] for group in groups)
                self.assertEqual(attributed + Decimal(str(transverse['prestations_eur_ht'])),
                                 Decimal(str(total['prestations_eur_ht'])))
                for case in ('bas', 'central', 'haut'):
                    self.assertEqual(sum(group['stacks'][slug]['raw_jh'][case] for group in groups)
                                     + transverse['raw_jh'][case], total['raw_jh'][case])
            self.assertEqual(decimal_sum([total['prestations_eur_ht'], total['pilotage_eur_ht']]),
                             Decimal(str(total['build_eur_ht'])))
            self.assertEqual(sum(total['composition']['central']), total['raw_jh']['central'])
            self.assertGreater(total['raw_jh']['central'], total['composition']['central'][2])

    def test_five_operations_reuse_baseline_budget_duration_and_full_capacity_year(self):
        rows = self.study.content['journey']['metrics']['options']
        self.assertEqual([row['stack'] for row in rows], [o['stack'] for o in self.study.baseline['options']])
        for row, option in zip(rows, self.study.baseline['options']):
            self.assertEqual(row['integration_eur_ht'], option['integration'])
            self.assertEqual(row['build_eur_ht'], option['obtention'])
            self.assertEqual(row['build_months'] + row['integration_months'], option['service_start_month'])
            self.assertEqual(Decimal(str(row['annual_eur_ht'])),
                             decimal_sum([*option['annual_base'].values(), *option['editor_prices'][:1]]).quantize(Decimal('.01')))
            self.assertEqual(row['annual_eur_ht'], self.study.content['stacks'][row['stack']]['economic_reading']['total'])
        self.assertEqual(len({row['integration_eur_ht'] for row in rows if row['mode'] == 'Make'}), 3)

    def test_atlas_preserves_complexity_axes_and_buy_statuses_without_coverage_score(self):
        source = self.study.content['business_map']['rows']
        atlas = self.study.content['journey']['metrics']['map']
        for group in atlas['areas']:
            members = [row for row in source if row['capacite_id'] in group['capabilities']]
            for axis, values in group['complexity'].items():
                self.assertEqual(values['high'], sum(row['complexite'][axis]['niveau'] >= 4 for row in members))
                self.assertEqual(values['count'], len(members))
                self.assertNotIn('average', values)
            for slug in ('microsoft', 'sap'):
                self.assertEqual(group['buy'][slug]['counts'], dict(Counter(row['buy'][slug]['statut'] for row in members)))

    def test_source_change_updates_only_its_funded_owner_and_ancestors(self):
        content, baseline = deepcopy(self.study.content), deepcopy(self.study.baseline)
        before = content['journey']['metrics']
        row = content['business_map']['rows'][0]
        slug = MAKE[0]
        row['work']['stacks'][slug] = deepcopy(row['work']['stacks'][slug])
        assignment = row['work']['stacks'][slug]
        assignment['work']['central'][2] += 1
        assignment['valuation']['cout_eur_ht'] += 100
        # The funding registry is a separate projection of the same owned price.
        fund = next(f for f in content['business_map']['funding'] if f['id'] == assignment['funding_id'])
        fund['valuation'] = deepcopy(assignment['valuation'])
        content['stacks'][slug]['economic']['detail_build']['prestations'] += 100
        next(o for o in baseline['options'] if o['stack'] == slug)['build'] += 100
        after = metrics(content, baseline)
        self.assertEqual(after['work_totals'][slug]['raw_jh']['central'], before['work_totals'][slug]['raw_jh']['central'] + 1)
        for identifier, cap in after['map']['capabilities'].items():
            old = before['map']['capabilities'][identifier]
            delta = 1 if identifier == row['capacite_id'] else 0
            self.assertEqual(cap['stacks'][slug]['raw_jh']['central'], old['stacks'][slug]['raw_jh']['central'] + delta)
            self.assertEqual(decimal_sum([cap['stacks'][slug]['prestations_eur_ht'], -old['stacks'][slug]['prestations_eur_ht']]),
                             Decimal(delta * 100))
        self.assertEqual(after['transverse'], before['transverse'])

    def test_market_gap_is_documentary_and_tracks_existing_source_values(self):
        result = self.study.content['journey']['metrics']['market']
        sap = self.study.content['stacks']['sap']
        self.assertEqual(result['sap']['printed_total_eur_ht'], sap['pricing']['total_imprime_eur'])
        self.assertEqual(result['sap']['sum_lots_eur_ht'], sap['economic']['detail_integration']['base_rfi'])
        self.assertEqual(Decimal(str(result['sap']['discrepancy_eur_ht'])),
                         decimal_sum([sap['pricing']['total_imprime_eur'], -sap['economic']['detail_integration']['base_rfi']]))
        self.assertEqual(result['references_count'], len(self.study.content['market']['references']))
        self.assertEqual(result['eligible_count'], self.study.content['market']['analyse_dispersion']['resultat_actuel']['references_eligibles'])

    def test_editorial_links_cannot_introduce_unknown_domains_or_scenarios(self):
        current = self.study.content['journey']
        wrong = deepcopy(current)
        wrong['atlas']['neighbors'][0]['native'] = ['invented-domain']
        with self.assertRaisesRegex(AssertionError, 'Unknown neighboring domain'):
            validate_editorial(wrong, self.study.content, self.study.document_path)
        wrong = deepcopy(current)
        wrong['operations']['scenario'] = 'invented-scenario'
        with self.assertRaisesRegex(AssertionError, 'Unknown integration scenario'):
            validate_editorial(wrong, self.study.content, self.study.document_path)


if __name__ == '__main__':
    unittest.main(verbosity=2)
