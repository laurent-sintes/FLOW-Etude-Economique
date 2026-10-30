"""Application notes preserve provenance while staying outside calculation inputs."""
from copy import deepcopy
import unittest

from application_framework import SOURCE, compile_application
from evaluation_status import load_status
from validate_stacks import ROOT, read


class ApplicationFrameworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = read(ROOT / SOURCE)
        cls.glossary = read(ROOT / 'source/glossaire.yaml')
        cls.documents = read(ROOT / 'config/publication.yaml')['documents']
        cls.routes = set(read(ROOT / 'config/application.yaml')['essential']['pages'])

    def compile(self, document):
        return compile_application(document, self.glossary, self.routes, self.documents)

    def test_status_is_derived_from_its_owner_and_outputs_are_isolated(self):
        before = deepcopy(self.document)
        result = self.compile(self.document)
        self.assertEqual(result['economic']['status']['summary'], load_status()['summary'])
        self.assertEqual(result['economic']['status']['source'], load_status()['active_source'])
        self.assertNotIn('status', self.document['economic'])
        result['market']['sections'].clear()
        self.assertEqual(self.document, before)

    def test_unknown_results_overrides_and_unresolved_links_are_rejected(self):
        def price(d): d['economic']['budget'] = 1000
        def copied_status(d): d['economic']['status'] = {'text': 'Local copy'}
        def duplicate(d): d['market']['sections'].append(deepcopy(d['market']['sections'][0]))
        def missing_section(d): d['hypotheses']['sections'].pop()
        def unknown_section(d): d['economic']['sections'][0]['id'] = 'unrendered-section'
        def unknown(d): d['economic']['sections'][0]['links'][0]['href'] = '#missing-page'
        def external(d): d['economic']['sections'][0]['links'][0]['href'] = 'https://example.com'
        for change in (price, copied_status, duplicate, missing_section, unknown_section, unknown, external):
            document = deepcopy(self.document)
            change(document)
            with self.subTest(change=change.__name__), self.assertRaisesRegex(ValueError, 'ERR_FRAMEWORK_APPLICATION'):
                self.compile(document)


if __name__ == '__main__':
    unittest.main()
