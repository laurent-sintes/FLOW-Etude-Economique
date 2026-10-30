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
                         document_path=self.study.document_path)
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
        result = self.compile()
        for option, original in zip(result['options'], self.study.baseline['options']):
            with self.subTest(stack=option['stack']):
                self.assertEqual([row['amount'] for row in option['integration']['detail']],
                                 [row['amount'] for row in original['funding_ledger'] if row['phase']=='integration'])
                self.assertAlmostEqual(sum(row['amount'] for row in option['integration']['detail']), original['integration'], places=2)
                self.assertEqual(option['annual']['breakdown'], list(self.study.content['stacks'][option['stack']]['economic_reading']['buckets'].values()))
                if option['mode']=='Make':
                    core=option['core']
                    self.assertEqual(core['total_jh'], self.study.content['stacks'][option['stack']]['economic']['jh']['core_avant_ia'])
                    self.assertGreater(core['natures']['qualification'],0)
                    self.assertEqual(len(core['features']), len(self.study.content['stacks'][option['stack']]['features']))
                    for row, source in zip(core['features'], self.study.content['stacks'][option['stack']]['features']):
                        self.assertEqual(row['charges'], source['plages_jh']['central'])
                        self.assertEqual(row['justification'], source['justification'])
                else:
                    self.assertIsNone(option['core'])
        result['options'][0]['core']['features'][0]['charges']['qualification']=-1
        self.assertGreater(self.study.content['stacks'][result['options'][0]['stack']]['features'][0]['plages_jh']['central']['qualification'],0)

    def test_inconsistent_documentary_decompositions_are_rejected(self):
        content=deepcopy(self.study.content)
        content['stacks']['java-spring']['features'][0]['plages_jh']['central']['qualification']+=1
        with self.assertRaisesRegex(ValueError,'core charge ownership'):
            self.compile(content=content)
        content=deepcopy(self.study.content)
        content['stacks']['java-spring']['economic_reading']['buckets']['socle']['total']+=1
        with self.assertRaisesRegex(ValueError,'annual detail ownership'):
            self.compile(content=content)

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
