"""Market evidence controls shared by loading and the standalone diagnostic."""
from copy import deepcopy
from contextlib import redirect_stdout
from io import StringIO
import unittest

from analyze_cost_references import PATH, validate_market_references
from validate_stacks import read


class MarketReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.market = read(PATH)

    def setUp(self):
        self.data = deepcopy(self.market)

    def test_current_references_validate_without_mutation_or_output(self):
        with redirect_stdout(StringIO()) as captured:
            report = validate_market_references(self.data)
        self.assertEqual(captured.getvalue(), '')
        self.assertEqual(self.data, self.market)
        self.assertEqual((report['references'], report['prices'], report['normalized'], report['eligible']), (15, 15, 12, 0))

    def test_inconsistent_normalized_price_is_rejected(self):
        norm = self.data['references'][0]['normalisation_2026']
        norm['min_eur'] += 12345
        norm['max_eur'] += 12345
        with self.assertRaisesRegex(AssertionError, 'actualisation incohérente'):
            validate_market_references(self.data)

    def test_exchange_rate_must_match_its_evidence_even_if_arithmetic_is_consistent(self):
        norm = self.data['references'][0]['normalisation_2026']
        norm['devise_par_eur'] *= 2
        norm['min_eur'] /= 2
        norm['max_eur'] /= 2
        with self.assertRaisesRegex(AssertionError, 'taux de change différent'):
            validate_market_references(self.data)

    def test_normalized_price_requires_date_currency_and_published_scope(self):
        for field, value, message in [('date_prix', None, 'sans date'), ('devise', 'JPY', 'devise inconnue')]:
            with self.subTest(field=field):
                broken = deepcopy(self.market)
                broken['references'][0]['cout_publie'][field] = value
                with self.assertRaisesRegex(AssertionError, message):
                    validate_market_references(broken)
        self.data['references'][0]['projet']['inclus_dans_prix'] = ''
        with self.assertRaisesRegex(AssertionError, 'assiette publiée incomplète'):
            validate_market_references(self.data)

    def test_index_period_must_match_the_published_price_date(self):
        self.data['references'][0]['normalisation_2026']['periode_depart'] = '2019-09'
        with self.assertRaisesRegex(AssertionError, 'concordance avec la date'):
            validate_market_references(self.data)

    def test_unknown_normalization_is_not_zero_or_half_known(self):
        entry = next(row for row in self.data['references'] if row['cout_publie']['date_prix'] is None)
        self.assertIsNone(entry['normalisation_2026']['min_eur'])
        validate_market_references(self.data)
        entry['normalisation_2026']['min_eur'] = 0
        with self.assertRaisesRegex(AssertionError, 'partiellement inconnue'):
            validate_market_references(self.data)

    def test_non_finite_or_boolean_amount_is_rejected(self):
        for value in (float('inf'), float('nan'), True):
            with self.subTest(value=value):
                broken = deepcopy(self.market)
                broken['references'][0]['normalisation_2026']['max_eur'] = value
                with self.assertRaisesRegex(AssertionError, 'Nombre'):
                    validate_market_references(broken)


if __name__ == '__main__':
    unittest.main()
