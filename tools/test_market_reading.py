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
                self.assertEqual(shown['sources'], source['sources'])
                self.assertEqual(shown['source_ref'],
                                 'source/references-couts-integration.yaml#references/' + source['id'])

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


if __name__ == '__main__':
    unittest.main()
