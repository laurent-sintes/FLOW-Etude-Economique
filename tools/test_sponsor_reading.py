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
        result=self.study.content['journey']['metrics']
        self.assertFalse(result['transverse'])
        for slug,total in result['work_totals'].items():
            self.assertEqual(total['pilotage_eur_ht'],0)
            self.assertEqual(total['build_eur_ht'],sum(u['cost_eur_ht'] for u in total['units']))
            self.assertEqual(total['raw_jh']['central'],sum(u['total_jh'] for u in total['units']))
            self.assertTrue(all(c['stacks'][slug]['raw_jh']['central'] is None for c in result['map']['capabilities'].values()))

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
        source=self.study.content['business_map']['rows']
        for group in self.study.content['journey']['metrics']['map']['areas']:
            members=[row for row in source if row['capacite_id'] in group['capabilities']]
            self.assertNotIn('complexity',group)
            for slug in ('microsoft','sap'):
                self.assertEqual(group['buy'][slug]['counts'],dict(Counter(row['buy'][slug]['statut'] for row in members)))

    def test_source_change_updates_only_its_funded_owner_and_ancestors(self):
        content,baseline=deepcopy(self.study.content),deepcopy(self.study.baseline)
        content['business_map']['family_funding'][0]['cout_eur_ht']+=100
        with self.assertRaises(AssertionError):
            metrics(content,baseline)
        content=deepcopy(self.study.content)
        content['business_map']['funding'].append({'id':'unexpected-legacy'})
        with self.assertRaisesRegex(AssertionError,'Legacy Make funding'):
            metrics(content,baseline)

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
