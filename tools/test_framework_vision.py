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
        self.assertEqual(compiled['adaptation']['href'], '#comparer')
        self.assertEqual(compiled['adaptation']['reference_link']['href'], '#parametres')
        hydrated = hydrate_framework_vision(self.ui, self.glossary)
        hydrated_vision = deepcopy(hydrated['essential']['framework_vision'])
        stack_elements = {e['id']: e for e in read(ROOT / 'source/stacks/java-spring.yaml')['elements']}
        for group in hydrated_vision['journey']['phases'][0]['providers'][0]['stack_reading']['groups']:
            elements = group.pop('elements')
            self.assertEqual(elements, [dict(id=ref, name=stack_elements[ref]['nom'], description=stack_elements[ref]['description']) for ref in group['element_refs']])
        resolved=hydrated_vision['journey']['phases'][0]['make_audit']['mapping']['example'].pop('resolved')
        self.assertEqual(resolved['capability']['native_id'],'D01.g')
        self.assertEqual(resolved['function']['id'],'BC-010.01')
        self.assertEqual(resolved['feature']['id'],'K1')
        self.assertEqual(hydrated_vision, compiled)
        self.assertEqual(self.ui['essential']['framework_vision'], {'source': SOURCE})
        compiled['opening']['text'] = 'Périmètre : {{notion.core_system}}.'
        glossary = deepcopy(self.glossary)
        glossary['notions']['core_system']['libelle'] = 'Noyau métier'
        self.assertEqual(resolve_text_tree(compiled, glossary)['opening']['text'], 'Périmètre : Noyau métier.')
        self.assertEqual(self.document, before)
        self.assertEqual([level['id'] for level in before['confidence']['levels']],
                         ['method', 'application', 'review', 'delivery'])
        # Application and human review can share a dossier while remaining different proof levels.
        self.assertEqual(before['confidence']['levels'][1]['href'], before['confidence']['levels'][2]['href'])

    def test_unknown_fields_duplicates_and_unresolved_reading_links_are_rejected(self):
        def unknown_root(d): d['budget'] = 1000
        def unknown_nested(d): d['confidence']['amount'] = 1000
        def wrong_version(d): d['version'] = 2
        def blank_text(d): d['opening']['text'] = '  '
        def missing_limits_title(d): d['confidence'].pop('limits_title')
        def missing_proof_levels(d): d['confidence'].pop('levels')
        def incomplete_proof_levels(d): d['confidence']['levels'].pop()
        def reordered_proof_levels(d): d['confidence']['levels'].reverse()
        def copied_proof_level(d): d['confidence']['levels'][1] = deepcopy(d['confidence']['levels'][0])
        def unknown_proof_level_field(d): d['confidence']['levels'][0]['budget'] = 1000
        def invalid_proof_level_route(d): d['confidence']['levels'][0]['href'] = '#absent'
        def missing_confidence_links(d): d['confidence'].pop('links')
        def duplicate_confidence_link(d): d['confidence']['links'].append(deepcopy(d['confidence']['links'][0]))
        def invalid_confidence_link(d): d['confidence']['links'][0]['href'] = '#absent'
        def missing_adaptation(d): d.pop('adaptation')
        def wrong_adaptation_link(d): d['adaptation']['href'] = '#leviers'
        def unknown_adaptation_field(d): d['adaptation']['budget'] = 1000
        def duplicate_step(d): d['approach']['steps'].append(deepcopy(d['approach']['steps'][0]))
        def missing_step(d): d['approach']['steps'].pop()
        def reordered_steps(d): d['approach']['steps'].reverse()
        def unknown_step(d): d['approach']['steps'][0]['id'] = 'other'
        def missing_matrix(d): d['approach'].pop('matrix')
        def duplicate_matrix_row(d): d['approach']['matrix']['rows'][1] = deepcopy(d['approach']['matrix']['rows'][0])
        def reordered_matrix(d): d['approach']['matrix']['rows'].reverse()
        def missing_matrix_cell(d): d['approach']['matrix']['rows'][0].pop('make')
        def empty_matrix_cell(d): d['approach']['matrix']['rows'][0]['buy'] = []
        def unknown_matrix_budget(d): d['approach']['matrix']['rows'][0]['budget'] = 1000
        def duplicate_proof(d): d['evidence']['items'].append(deepcopy(d['evidence']['items'][0]))
        def duplicate_destination(d): d['evidence']['items'][1]['href'] = d['evidence']['items'][0]['href']
        def unknown_route(d): d['evidence']['items'][0]['href'] = '#absent'
        def legacy_route(d): d['evidence']['items'][0]['href'] = '#perimetres'
        def ignored_query(d): d['evidence']['items'][0]['href'] = '#marche?section=absent'
        def unknown_document(d): d['evidence']['items'][0]['href'] = 'source/missing.md'
        def unknown_glossary(d): d['opening']['text'] = '{{notion.absent}}'
        def copied_glossary(d): d['opening']['text'] = self.glossary['notions']['core_system']['libelle']
        def wrong_next(d): d['next']['links'][0]['href'] = '#absent'
        for change in (unknown_root, unknown_nested, wrong_version, blank_text, missing_limits_title,
                       missing_proof_levels, incomplete_proof_levels, reordered_proof_levels, copied_proof_level,
                       unknown_proof_level_field, invalid_proof_level_route, missing_confidence_links,
                       duplicate_confidence_link, invalid_confidence_link, missing_adaptation, wrong_adaptation_link, unknown_adaptation_field, duplicate_step,
                       missing_step, reordered_steps, unknown_step, missing_matrix, duplicate_matrix_row,
                       reordered_matrix, missing_matrix_cell, empty_matrix_cell, unknown_matrix_budget,
                       duplicate_proof, duplicate_destination, unknown_route, legacy_route,
                       ignored_query, unknown_document, unknown_glossary, copied_glossary, wrong_next):
            document = deepcopy(self.document)
            change(document)
            with self.subTest(change=change.__name__), self.assertRaisesRegex(ValueError, 'ERR_FRAMEWORK_VISION'):
                self.compile(document)

    def test_overview_requires_complete_stage_handoffs_and_resolvable_links(self):
        compiled=self.compile(self.document)
        self.assertEqual([s['id'] for s in compiled['approach']['steps']],
                         ['besoin','acquisition','integration','fonctionnement','delivery','valorisation','comparaison'])
        for field in ('inputs','treatment','output','links'):
            broken=deepcopy(self.document)
            broken['approach']['steps'][0].pop(field)
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'ERR_FRAMEWORK_VISION'):
                self.compile(broken)
        for links in ([dict(href='#missing-stage',label='Missing')],
                      [dict(href='#acquisition',label='A'),dict(href='#acquisition',label='B')]):
            broken=deepcopy(self.document)
            broken['approach']['steps'][0]['links']=links
            with self.assertRaisesRegex(ValueError,'ERR_FRAMEWORK_VISION'):
                self.compile(broken)

    def test_hydration_rejects_local_copies_and_undeclared_routes(self):
        for reference in (None, {'source': 'source/fondamentaux.yaml'},
                          {'source': SOURCE, 'text': 'Local override.'}):
            ui = deepcopy(self.ui)
            ui['essential']['framework_vision'] = reference
            with self.subTest(reference=reference), self.assertRaisesRegex(ValueError, 'ERR_FRAMEWORK_VISION'):
                hydrate_framework_vision(ui, self.glossary)
        for route in ('modele', 'parametres', 'comparer', 'cartographie', 'synvance', 'conditions-realisation', 'preetude-projets', 'preetude-solutions', 'preetude-couts'):
            ui = deepcopy(self.ui)
            ui['essential']['pages'].pop(route)
            with self.subTest(missing_route=route), self.assertRaisesRegex(ValueError, 'unknown reading link'):
                hydrate_framework_vision(ui, self.glossary)

    def test_pre_studies_are_visible_inputs_and_readiness_has_no_standalone_group(self):
        groups = [group for group in self.ui['essential']['nav_groups'] if not group.get('hidden')]
        self.assertEqual(next(group for group in groups if group['label']=='Études préalables')['items'], ['preetudes', 'synvance', 'cartographie', 'preetude-projets', 'preetude-solutions', 'preetude-couts', 'preetude-productivite'])
        self.assertNotIn('capacite-realisation', [page for group in groups for page in group['items']])
        self.assertEqual(next(group for group in groups if group['label'] == 'Dossier économique')['items'], ['comparer', 'evaluation-core', 'parametres'])
        links = {item['href'] for item in self.document['evidence']['items']}
        self.assertTrue({'#preetude-projets', '#preetude-solutions', '#preetude-couts'} <= links)

    def test_phase_options_and_method_links_are_validated(self):
        for change in ('order','option','link','budget'):
            document=deepcopy(self.document)
            phase=document['journey']['phases'][0]
            if change=='order':document['journey']['phases'].reverse()
            elif change=='option':phase['providers'][0]['option_ref']='rust'
            elif change=='link':phase['providers'][0]['links'][0]['href']='#missing'
            else:phase['providers'][0]['budget']=1000
            with self.subTest(change=change),self.assertRaisesRegex(ValueError,'ERR_FRAMEWORK_VISION'):
                self.compile(document)
        compiled=self.compile(self.document)
        self.assertEqual([p['id'] for p in compiled['journey']['phases']],['acquisition','integration','fonctionnement'])
        for phase in compiled['journey']['phases']:
            self.assertEqual([p['option_ref'] for p in phase['providers']],['java-spring','microsoft','sap'])

    def test_stack_reading_rejects_unknown_duplicate_and_misplaced_components(self):
        for change in ('unknown', 'duplicate', 'phase', 'provider'):
            document = deepcopy(self.document)
            providers = document['journey']['phases'][0]['providers']
            reading = providers[0]['stack_reading']
            if change == 'unknown': reading['groups'][0]['element_refs'] = ['missing']
            elif change == 'duplicate': reading['groups'][1]['element_refs'].append(reading['groups'][0]['element_refs'][0])
            elif change == 'phase': document['journey']['phases'][1]['providers'][0]['stack_reading'] = providers[0].pop('stack_reading')
            else: providers[1]['stack_reading'] = providers[0].pop('stack_reading')
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'ERR_FRAMEWORK_VISION'):
                self.compile(document)

    def test_make_audit_rejects_invented_rules_and_formula_sections(self):
        for target in ('rule','section'):
            document=deepcopy(self.document)
            audit=document['journey']['phases'][0]['make_audit']
            if target=='rule':audit['steps'][0]['rule_refs']=['missing']
            else:audit['sections']=['missing']
            with self.subTest(target=target),self.assertRaisesRegex(ValueError,'ERR_FRAMEWORK_VISION'):
                self.compile(document)
        document=deepcopy(self.document)
        document['journey']['methods'][0]['group']='missing'
        with self.assertRaisesRegex(ValueError,'invalid method group'):
            self.compile(document)

    def test_mapping_rejects_a_different_function_component_or_file(self):
        for field in ('function','component','file'):
            document=deepcopy(self.document)
            example=document['journey']['phases'][0]['make_audit']['mapping']['example']
            if field=='function':example['function_ref']='BC-011.01'
            elif field=='component':example['component_ref']='K2'
            else:example['references'][0]['file_refs']=['README.md']
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'ERR_FRAMEWORK_VISION:mapping'):
                self.compile(document)
        compiled=hydrate_framework_vision(self.ui,self.glossary)['essential']['framework_vision']
        example=compiled['journey']['phases'][0]['make_audit']['mapping']['example']
        for spec,actual in zip(example['references'],example['resolved']['references']):
            perimeter=read(ROOT/spec['source'])
            self.assertEqual(actual['revision'],perimeter['source_revision'])
            self.assertEqual([f['path'] for f in actual['files']],spec['file_refs'])
            for file in actual['files']:
                self.assertEqual(file['url'],spec['repository']+'/blob/'+actual['revision']+'/'+file['path'])

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
