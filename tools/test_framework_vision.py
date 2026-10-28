"""Overview ownership, real reading links and frozen presentation isolation."""
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

from content_model import resolve_text_tree
from framework_vision import SOURCE, compile_vision, hydrate_framework_vision
from study_app import Study
from study_snapshot import candidate
from test_support import study_copy
from validate_stacks import ROOT, read


class FrameworkVisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = read(ROOT / SOURCE)
        cls.glossary = read(ROOT / 'source/glossaire.yaml')
        cls.ui = read(ROOT / 'config/application.yaml')
        cls.documents = read(ROOT / 'config/publication.yaml')['documents']
        essential = cls.ui['essential']
        cls.routes = {row['id'] for row in essential['nav']} & set(essential['pages'])

    def compile(self, document):
        return compile_vision(document, self.glossary, self.routes, self.documents)

    def test_single_owner_resolves_current_glossary_without_mutating_source(self):
        before = deepcopy(self.document)
        compiled = self.compile(self.document)
        self.assertEqual(compiled, before)
        self.assertIsNot(compiled, self.document)
        hydrated = hydrate_framework_vision(self.ui, self.glossary)
        self.assertEqual(hydrated['essential']['framework_vision'], compiled)
        self.assertEqual(self.ui['essential']['framework_vision'], {'source': SOURCE})
        compiled['opening']['text'] = 'Périmètre : {{notion.core_system}}.'
        glossary = deepcopy(self.glossary)
        glossary['notions']['core_system']['libelle'] = 'Noyau métier'
        self.assertEqual(resolve_text_tree(compiled, glossary)['opening']['text'], 'Périmètre : Noyau métier.')
        self.assertEqual(self.document, before)

    def test_unknown_fields_duplicates_and_unresolved_reading_links_are_rejected(self):
        def unknown_root(d): d['budget'] = 1000
        def unknown_nested(d): d['confidence']['amount'] = 1000
        def wrong_version(d): d['version'] = 2
        def blank_text(d): d['opening']['text'] = '  '
        def missing_limits_title(d): d['confidence'].pop('limits_title')
        def missing_adaptation(d): d.pop('adaptation')
        def wrong_adaptation_link(d): d['adaptation']['href'] = '#simuler'
        def unknown_adaptation_field(d): d['adaptation']['budget'] = 1000
        def duplicate_step(d): d['approach']['steps'].append(deepcopy(d['approach']['steps'][0]))
        def missing_step(d): d['approach']['steps'].pop()
        def reordered_steps(d): d['approach']['steps'].reverse()
        def unknown_step(d): d['approach']['steps'][0]['id'] = 'other'
        def duplicate_proof(d): d['evidence']['items'].append(deepcopy(d['evidence']['items'][0]))
        def duplicate_destination(d): d['evidence']['items'][1]['href'] = d['evidence']['items'][0]['href']
        def unknown_route(d): d['evidence']['items'][0]['href'] = '#absent'
        def legacy_route(d): d['evidence']['items'][0]['href'] = '#perimetres'
        def ignored_query(d): d['evidence']['items'][0]['href'] = '#marche?section=absent'
        def unknown_document(d): d['evidence']['items'][0]['href'] = 'source/missing.md'
        def unknown_glossary(d): d['opening']['text'] = '{{notion.absent}}'
        def copied_glossary(d): d['opening']['text'] = self.glossary['notions']['core_system']['libelle']
        def wrong_next(d): d['next']['href'] = '#comparer'
        for change in (unknown_root, unknown_nested, wrong_version, blank_text, missing_limits_title,
                       missing_adaptation, wrong_adaptation_link, unknown_adaptation_field, duplicate_step,
                       missing_step, reordered_steps, unknown_step,
                       duplicate_proof, duplicate_destination, unknown_route, legacy_route,
                       ignored_query, unknown_document, unknown_glossary, copied_glossary, wrong_next):
            document = deepcopy(self.document)
            change(document)
            with self.subTest(change=change.__name__), self.assertRaisesRegex(ValueError, 'ERR_FRAMEWORK_VISION'):
                self.compile(document)

    def test_hydration_rejects_local_copies_and_undeclared_routes(self):
        for reference in (None, {'source': 'source/fondamentaux.yaml'},
                          {'source': SOURCE, 'text': 'Local override.'}):
            ui = deepcopy(self.ui)
            ui['essential']['framework_vision'] = reference
            with self.subTest(reference=reference), self.assertRaisesRegex(ValueError, 'ERR_FRAMEWORK_VISION'):
                hydrate_framework_vision(ui, self.glossary)
        for route in ('modele', 'leviers'):
            ui = deepcopy(self.ui)
            ui['essential']['pages'].pop(route)
            with self.subTest(missing_route=route), self.assertRaisesRegex(ValueError, 'unknown reading link'):
                hydrate_framework_vision(ui, self.glossary)

    def test_snapshot_freezes_overview_and_sources_without_affecting_simulations(self):
        study = study_copy()
        baseline = deepcopy(study.baseline)
        contract = study.simulation_contract()
        bundle = candidate(study)
        self.assertIn(SOURCE, bundle['payload']['documents'])
        self.assertIn('tools/framework_vision.py', bundle['payload']['documents'])
        self.assertIn(str((ROOT / SOURCE).resolve()), study.source_digests)
        released = Study.from_release(bundle)
        frozen = deepcopy(released.ui['essential']['framework_vision'])
        study.ui['essential']['framework_vision']['opening']['text'] = 'Changed presentation.'
        self.assertEqual(study.simulate(study.parameters), baseline)
        self.assertEqual(study.simulation_contract(), contract)
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('unexpected source read')):
            self.assertEqual(released.bootstrap(essential=True)['ui']['essential']['framework_vision'], frozen)
            self.assertEqual(released.simulate(released.parameters), baseline)


if __name__ == '__main__':
    unittest.main()
