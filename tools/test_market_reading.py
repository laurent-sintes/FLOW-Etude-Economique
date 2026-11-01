"""The reader sees unchanged prices, unknowns, periods and documentary provenance."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from market_reading import build_market_reading
from validate_stacks import ROOT, read


class MarketReadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.market = read(ROOT / 'source/references-couts-integration.yaml')

    def test_all_projects_keep_original_normalized_and_transposed_values_separate(self):
        presentation = build_market_reading(self.market)
        self.assertEqual([r['id'] for r in presentation['projects']],
                         [r['id'] for r in self.market['references']])
        for source, shown in zip(self.market['references'], presentation['projects']):
            with self.subTest(reference=source['id']):
                self.assertEqual(shown['price'], source['cout_publie'])
                self.assertEqual(shown['normalized'], source['normalisation_2026'])
                self.assertEqual(shown['transposed'], source['transposition_au_perimetre_flow_beaumanoir'])
                self.assertEqual(shown['proofs'], source['lecture_flow']['preuves'])
                self.assertEqual(shown['similarities'], source['lecture_flow']['similitudes'])
                self.assertEqual(shown['differences'], source['lecture_flow']['differences'])
                self.assertEqual(shown['lesson'], source['lecture_flow']['enseignement'])
                self.assertEqual(shown['sources'], source['sources'])
                self.assertEqual(shown['source_ref'],
                                 'source/references-couts-integration.yaml#references/' + source['id'])

    def test_phase_guardrails_keep_unknown_flow_ranges_and_canonical_published_bounds(self):
        original = deepcopy(self.market)
        frozen = json.loads(json.dumps(self.market))
        before = deepcopy(frozen)
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('no source reread')):
            phases = build_market_reading(frozen)['phase_summary']['phases']
        self.assertEqual([row['id'] for row in phases], ['acquisition', 'integration', 'fonctionnement'])
        self.assertTrue(all(row['flow_range'] is None for row in phases))
        self.assertEqual([(g['min_eur'], g['max_eur']) for g in phases[1]['groups']],
                         [(7_000_000, 20_000_000), (1_517_180, 14_294_386)])
        self.assertEqual(len(phases[1]['groups'][0]['references']), 4)
        self.assertTrue(all('?view=services&focus=' in ref['href'] for ref in phases[2]['references']))
        self.assertEqual(frozen, before)
        frozen['reperes_exploratoires_marche']['contrepoints_dynamics']['minimum_eur_2026'] = 2_000_000
        self.assertEqual(build_market_reading(frozen)['phase_summary']['phases'][1]['groups'][1]['min_eur'],
                         2_000_000)
        phases[1]['groups'][0]['references'].clear()
        self.assertEqual(self.market, original)

    def test_phase_guardrails_reject_unbound_references_and_missing_phases(self):
        broken = deepcopy(self.market)
        broken['synthese_phases']['phases'][2]['references'].append('unbound-project')
        with self.assertRaises(KeyError):
            build_market_reading(broken)
        broken = deepcopy(self.market)
        broken['synthese_phases']['phases'].pop()
        with self.assertRaisesRegex(ValueError, 'three FLOW phases'):
            build_market_reading(broken)

    def test_services_keep_each_observation_once_with_its_original_period_and_scope(self):
        services = build_market_reading(self.market)['services']
        self.assertEqual(len(services), len(self.market['references']))
        for source, shown in zip(self.market['references'], services):
            expected = source['lecture_flow']['observations']
            self.assertEqual(len(shown['observations']), len(expected))
            for original, observation in zip(expected, shown['observations']):
                self.assertEqual({k: v for k, v in observation.items() if k != 'evidence'}, original)
                self.assertEqual(observation['evidence'],
                                 self.market['echelle_qualite_prix_source'][original['qualite_prix_source']])

    def test_instruction_scope_and_normalization_provenance_remain_separate_from_prices(self):
        from market_instruction import build_market_instruction
        market = deepcopy(self.market)
        market['instruction'] = build_market_instruction(market)
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('no source reread')):
            reading = build_market_reading(market)
        self.assertEqual(reading['instruction'], market['instruction'])
        self.assertEqual(reading['comparison_scope'], market['reperes_build_core']['etude_oss']['perimetre'])
        self.assertEqual(reading['monetary_sources'], market['sources_monetaires'])
        self.assertEqual(reading['effort']['lignes'], market['reperes_build_core']['lignes'])
        for source, shown in zip(market['references'], reading['projects']):
            self.assertEqual(shown['review_date'], source['lecture_flow']['date_revue'])
            self.assertEqual(shown['price'].get('reserve'), source['cout_publie'].get('reserve'))
            self.assertEqual(shown['normalized'], source['normalisation_2026'])
        reading['instruction']['qualifications'].clear()
        self.assertTrue(market['instruction']['qualifications'])
        reading['monetary_sources'].clear()
        self.assertTrue(market['sources_monetaires'])

    def test_projection_works_from_frozen_content_without_disk_reads_or_shared_mutations(self):
        source = deepcopy(self.market)
        frozen = json.loads(json.dumps(source))
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('no source reread')):
            self.assertEqual(build_market_reading(source), build_market_reading(frozen))
            presentation = build_market_reading(source)
        presentation['projects'][0]['price']['min'] = -1
        presentation['projects'][0]['proofs'].clear()
        presentation['services'][0]['observations'].clear()
        self.assertEqual(source, self.market)

    def test_documentary_fiches_never_expose_computed_effort_or_transposed_prices(self):
        source = deepcopy(self.market)
        for fiche in source['reperes_build_core']['fiches_produit'].values():
            fiche['code']['effort_jh'] = 987654321
            fiche['prix_retraite_flow_eur_2026'] = 123456789
        shown = build_market_reading(source)['documentary_products']
        raw = json.dumps(shown)
        for forbidden in ('effort_jh', 'calcul_cocomo', 'prix_retraite_flow_eur_2026', '987654321', '123456789'):
            self.assertNotIn(forbidden, raw)
        self.assertEqual(set(shown['fiches_produit']), set(source['reperes_build_core']['fiches_produit']))
        for key, row in shown['fiches_produit'].items():
            self.assertEqual(row['code']['pncloc'], source['reperes_build_core']['fiches_produit'][key]['code']['pncloc'])
            self.assertEqual(row['evaluations'], source['reperes_build_core']['fiches_produit'][key]['evaluations'])
        shown['fiches_produit'].clear()
        self.assertEqual(len(source['reperes_build_core']['fiches_produit']), 6)


if __name__ == '__main__':
    unittest.main()
