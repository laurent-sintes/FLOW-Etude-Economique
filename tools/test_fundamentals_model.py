"""Model-page ownership, native references and release isolation."""
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

from architecture_model import load_architecture, hydrate_architecture, validate_architecture, validate_economic_links
from content_model import resolve_text_tree
from fundamentals_model import SOURCE, SCHEMA, compile_fundamentals, hydrate_fundamentals
from study_app import Study
from study_snapshot import candidate
from test_support import study_copy
from validate_stacks import ROOT, read


class FundamentalsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = study_copy()
        cls.document = read(ROOT / SOURCE)
        cls.native = read(ROOT / cls.document['business_map']['source'])
        cls.glossary = cls.study.glossary
        cls.architecture = load_architecture(cls.glossary)
        cls.ui = read(ROOT / 'config/application.yaml')

    def compile(self, document=None, native=None, glossary=None):
        return compile_fundamentals(document or self.document, glossary or self.glossary,
                                    self.architecture, self.study.data['options'], native or self.native)

    def test_native_names_and_relationships_drive_map_without_copies(self):
        native = deepcopy(self.native)
        next(n for n in native['nodes'] if n['id'] == 'domain-sales')['fields']['name'] = 'Commerce renommé à la source'
        model = self.compile(native=native)
        view = hydrate_fundamentals(self.ui, model)['essential']['model_map']
        sales = next(d for s in view['systems'] for d in s['domains'] if d['id'] == 'domain-sales')
        self.assertEqual(sales['label'], 'Commerce renommé à la source')
        self.assertEqual(len(model['native_map']['nodes']), 16)
        self.assertEqual(len(model['native_map']['relations']), 12)
        self.assertTrue(all(r['type'] == 'presents' for r in model['native_map']['relations']))
        self.assertTrue(all('label' not in s for s in self.document['business_map']['systems']))
        self.assertEqual(next(s['id'] for s in view['systems'] if s.get('program_scope')),
                         self.document['business_map']['program_scope']['system_ref'])

    def test_invalid_domain_relations_fail_before_rendering(self):
        def unknown_entity(d): d['relations'][0]['target'] = 'missing'
        def wrong_kind(d): d['relations'][0]['target'] = 'si_boardriders'
        def cyclic(d): d['relations'].append({'id': 'cycle', 'type': 'implements', 'source': 'core_system', 'target': 'flow_core_system'})
        def unknown_layer(d): d['entities'][0]['layer_refs'] = ['missing']
        def unknown_cost(d): d['phases'][0]['costs'].append('missing')
        def repeated_cost(d): d['phases'][0]['costs'].append('obtention')
        def unknown_target(d): d['phases'][0]['target_ref'] = 'missing'
        def bad_option(d): d['strategies'][0]['option_refs'][0] = 'sap'
        def missing_option(d): d['strategies'][0]['option_refs'].pop()
        def missing_implementation(d): d['strategies'][0].pop('implementation_ref')
        def unknown_notion(d): d['phases'][0]['notion'] = 'missing'
        def unknown_field(d): d['entities'][0]['budget'] = 100
        def missing_system(d): d['business_map']['systems'][0]['node_ref'] = 'missing'
        def missing_relation(d): d['business_map']['systems'][0]['domain_relation_refs'][0] = 'missing'
        def bad_scope(d): d['business_map']['outside_scope'].append('system-business-operations')
        def bad_position(d): d['business_map']['positioning']['domain_ref'] = 'domain-finance'
        def wrong_workload_direction(d): d['estimation']['relations'][0]['source_ref'] = 'net'
        def missing_workload_stage(d): d['estimation']['relations'][1]['target_ref'] = 'missing'
        def current_application_status(d): d['estimation']['status_ref'] = 'core'
        def repeated_workload_stage(d): d['estimation']['stages'][1]['id'] = 'gross'
        def unknown_workload_notion(d): d['estimation']['stages'][0]['notion'] = 'missing'
        def missing_activity(d): d['activity_reading']['type_refs'].pop()
        def repeated_activity(d): d['activity_reading']['type_refs'] = ['build', 'build']
        def unknown_activity(d): d['activity_reading']['type_refs'][0] = 'missing'
        def copied_activity_definition(d): d['activity_reading']['types'] = []
        def repeated_chapter(d): d['reading']['chapters'][1]['id'] = d['reading']['chapters'][0]['id']
        def wrong_chapter_order(d): d['reading']['chapters'].reverse()
        def missing_chapter(d): d['reading']['chapters'].pop()
        def unknown_reading_field(d): d['reading']['budget'] = 100
        def obsolete_disclosure_label(d): d['reading']['map_details'] = 'Contenu à déplier'
        def missing_coverage_label(d): d['reading'].pop('coverage_label')
        def wrong_next_page(d): d['reading']['next_href'] = '#complexite'
        def unknown_reading_link(d): d['reading']['strategy_links'][0]['href'] = 'source/missing.md'
        def repeated_reading_link(d): d['reading']['strategy_links'][1]['href'] = d['reading']['strategy_links'][0]['href']
        def missing_activity_summary(d): d['activity_reading']['summaries'].pop()
        def unknown_activity_summary(d): d['activity_reading']['summaries'][0]['type_ref'] = 'missing'
        def repeated_activity_summary(d): d['activity_reading']['summaries'][1]['type_ref'] = 'build'
        for change in (unknown_entity, wrong_kind, cyclic, unknown_layer, unknown_cost, repeated_cost, unknown_target,
                       bad_option, missing_option, missing_implementation, unknown_notion, unknown_field,
                       missing_system, missing_relation, bad_scope, bad_position,
                       wrong_workload_direction, missing_workload_stage, current_application_status,
                       repeated_workload_stage, unknown_workload_notion,
                       missing_activity, repeated_activity, unknown_activity, copied_activity_definition,
                       repeated_chapter, wrong_chapter_order, missing_chapter, unknown_reading_field,
                       obsolete_disclosure_label, missing_coverage_label, wrong_next_page,
                       unknown_reading_link, repeated_reading_link, missing_activity_summary,
                       unknown_activity_summary, repeated_activity_summary):
            with self.subTest(change=change.__name__):
                document = deepcopy(self.document)
                change(document)
                with self.assertRaisesRegex(ValueError, 'ERR_FUNDAMENTALS'):
                    self.compile(document=document)

    def test_changed_native_parent_is_rejected(self):
        native = deepcopy(self.native)
        ref = self.document['business_map']['systems'][0]['domain_relation_refs'][0]
        next(r for r in native['relations'] if r['id'] == ref)['source_id'] = 'system-business-operations'
        with self.assertRaisesRegex(ValueError, 'native domain relationship'):
            self.compile(native=native)

    def test_ui_only_controls_presentation_not_domain_content(self):
        model = self.compile()
        def caption(e): e['model_map']['systems'][0]['label'] = 'Local name'
        def unknown_system(e): e['model_map']['systems'][0]['system_ref'] = 'missing'
        def local_phase(e): e['calendar'][0]['costs'] = ['missing']
        def unknown_phase(e): e['calendar'][0]['phase_ref'] = 'missing'
        def local_choice(e): e['choices'][0]['text'] = 'Local definition'
        def local_limit(e): e['model_limit'] = 'Local rule'
        def unknown_concept(e): e['concepts'][0]['entity_ref'] = 'missing'
        def local_activities(e): e['model_activities'] = {'types': []}
        def local_reading(e): e['model_reading'] = {'chapters': []}
        def local_status(e): e['core_status_summary'] = 'Local status'
        def local_page_intro(e): e['pages']['modele']['intro'] = 'Local introduction'
        def local_chapter_title(e): e['model_choice'] = 'Local title'
        for change in (caption, unknown_system, local_phase, unknown_phase, local_choice, local_limit,
                       unknown_concept, local_activities, local_reading, local_status, local_page_intro, local_chapter_title):
            with self.subTest(change=change.__name__):
                ui = deepcopy(self.ui)
                change(ui['essential'])
                with self.assertRaisesRegex(ValueError, 'ERR_FUNDAMENTALS'):
                    hydrate_fundamentals(ui, model)
        ui = deepcopy(self.ui)
        ui['essential']['calendar'].reverse()
        actual = hydrate_fundamentals(ui, model)['essential']['calendar']
        self.assertEqual(actual, hydrate_fundamentals(self.ui, model)['essential']['calendar'])

    def test_activity_reading_uses_glossary_and_preserves_canonical_sources(self):
        glossary = deepcopy(self.glossary)
        glossary['notions']['run_activities']['libelle'] = 'Service continu'
        glossary['notions']['run_activities']['definition'] = 'Définition mise à jour dans le glossaire.'
        document = deepcopy(self.document)
        document['activity_reading']['type_refs'].reverse()
        model = self.compile(document=document, glossary=glossary)
        view = resolve_text_tree(hydrate_fundamentals(self.ui, model), glossary)['essential']['model_activities']
        self.assertEqual([item['id'] for item in view['types']], document['activity_reading']['type_refs'])
        run = next(item for item in view['types'] if item['id'] == 'run')
        self.assertEqual(run['notion'], 'run_activities')
        self.assertEqual(run['label'], 'Service continu')
        self.assertEqual(run['definition'], glossary['notions']['run_activities']['definition'])
        self.assertNotEqual(run['definition'], glossary['notions']['run']['definition'])
        self.assertNotIn('types', document['activity_reading'])
        self.assertEqual(model['phases'], document['phases'])
        view['types'].clear()
        self.assertEqual(len(model['activity_reading']['types']), 2)

    def test_method_reading_preserves_ownership_without_current_application_status(self):
        model = self.compile()
        view = hydrate_fundamentals(self.ui, model)['essential']
        reading = view['model_reading']
        self.assertEqual(reading['scope'], model['business_map']['scope_summary'])
        self.assertEqual(reading['activity_note'], model['activity_reading']['note'])
        self.assertEqual(reading['workload_note'], model['estimation']['note'])
        from evaluation_status import load_status
        self.assertEqual(view['core_status_summary'], load_status()['summary'])
        self.assertNotIn('status_summary', reading)
        self.assertNotIn('status_source', reading)
        self.assertNotIn('status', view['model_workload'])
        self.assertEqual(view['model_workload']['stages'], model['estimation']['stages'])
        self.assertIn('#evaluation-core', {item['href'] for item in view['model_workload']['links']})
        self.assertEqual(view['pages']['modele']['intro'], reading['intro'])
        self.assertEqual(self.ui['document_routes']['source/offres-synvance.md'], '#synvance')
        concepts = {item['notion']: item for item in view['concepts']}
        for entity in model['entities']:
            if entity.get('notion') in concepts:
                self.assertEqual(concepts[entity['notion']]['text'], entity['text'])
                self.assertIn('definition', self.glossary['notions'][entity['notion']])
        reading['chapters'].clear()
        view['model_workload']['stages'].clear()
        self.assertTrue(model['reading']['chapters'])
        self.assertTrue(model['estimation']['stages'])

    def test_cost_explanations_and_economic_classification_have_one_owner(self):
        architecture = deepcopy(self.architecture)
        architecture['cost_structures'][0]['description']['examples'] = ['Exemple métier modifié']
        view = hydrate_architecture(self.ui, architecture)['essential']['model_rows']
        self.assertEqual(view[0]['examples'], ['Exemple métier modifié'])
        cloud = next(c for c in architecture['cost_structures'] if c['id'] == 'run_cloud')
        self.assertEqual(set(cloud['cost_nature_refs']), {'run_cloud', 'technical_purchases'})
        validate_economic_links(architecture, self.study.baseline)
        cloud['cost_nature_refs'].remove('technical_purchases')
        with self.assertRaisesRegex(ValueError, 'ERR_ARCHITECTURE'):
            validate_economic_links(architecture, self.study.baseline)
        cloud['cost_nature_refs'].append('unknown_nature')
        with self.assertRaisesRegex(ValueError, 'ERR_ARCHITECTURE'):
            validate_economic_links(architecture, self.study.baseline)
        cloud['cost_nature_refs'] = ['obtention']
        with self.assertRaisesRegex(ValueError, 'ERR_ARCHITECTURE'):
            validate_architecture(architecture, self.glossary)
        ui = deepcopy(self.ui)
        ui['essential']['model_rows'][0]['text'] = 'Local budget explanation'
        with self.assertRaisesRegex(ValueError, 'ERR_ARCHITECTURE'):
            hydrate_architecture(ui, self.architecture)

    def test_glossary_propagates_and_compiled_objects_are_isolated(self):
        glossary = deepcopy(self.glossary)
        glossary['notions']['core_system']['libelle'] = 'Noyau métier'
        model = self.compile(glossary=glossary)
        view = resolve_text_tree(hydrate_fundamentals(self.ui, model), glossary)
        self.assertIn('Noyau métier', view['essential']['choices'][0]['text'])
        model['phases'][0]['costs'].clear()
        self.assertTrue(self.document['phases'][0]['costs'])

    def test_release_freezes_fundamentals_and_native_evidence(self):
        study = study_copy()
        bundle = candidate(study)
        released = Study.from_release(bundle)
        expected = deepcopy(study.fundamentals)
        for source in (SOURCE, SCHEMA, self.document['business_map']['source']):
            self.assertIn(source, bundle['payload']['documents'])
            self.assertIn(str((ROOT / source).resolve()), study.source_digests)
        study.fundamentals['phases'].clear()
        self.assertEqual(released.fundamentals, expected)
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('unexpected draft read')):
            self.assertEqual(released.simulate(released.parameters), study.baseline)
            self.assertEqual(released.bootstrap(essential=True)['ui']['essential']['model_map'],
                             study.ui['essential']['model_map'])

    def test_changed_fundamentals_or_native_source_blocks_mixed_release(self):
        study = study_copy()
        original = Path.read_bytes
        for source in (SOURCE, self.document['business_map']['source']):
            def changed(path):
                raw = original(path)
                return raw + b'\n' if path.resolve() == (ROOT / source).resolve() else raw
            with self.subTest(source=source), patch.object(Path, 'read_bytes', changed):
                with self.assertRaisesRegex(ValueError, 'Draft changed since loading'):
                    candidate(study)


if __name__ == '__main__':
    unittest.main()
