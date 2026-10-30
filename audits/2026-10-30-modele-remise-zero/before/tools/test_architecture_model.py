"""Domain ownership, invalid references, frozen loading and unchanged economics."""
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

from architecture_model import SOURCE, SCHEMA, hydrate_architecture, validate_architecture, validate_economic_links
from content_model import resolve_text_tree
from study_app import Study
from study_snapshot import candidate
from test_support import study_copy
from validate_stacks import ROOT, read


class ArchitectureModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = read(ROOT / SOURCE)
        cls.glossary = read(ROOT / 'source/glossaire.yaml')
        cls.ui = read(ROOT / 'config/application.yaml')

    def test_model_drives_labels_parts_and_conditional_coverage(self):
        document = deepcopy(self.document)
        document['layers'][0]['label'] = 'Interfaces du Groupe'
        document['layers'][0]['parts'][0]['examples'] = 'Parcours spécifiques'
        document['conditions']['contract_inclusion'] = 'Uniquement si le contrat le prévoit.'
        validated = validate_architecture(document, self.glossary)
        rendered = hydrate_architecture(self.ui, validated)['essential']['model_architecture']
        self.assertEqual(rendered['layers'][0]['label'], 'Interfaces du Groupe')
        self.assertEqual(rendered['layers'][0]['parts'][0]['examples'], 'Parcours spécifiques')
        buy = next(block for block in rendered['blocks'] if block['cost'] == 'grouped_buy')
        self.assertEqual(buy['scope_note'], document['conditions']['contract_inclusion'])
        links = next(row for row in validated['cost_structures'] if row['id'] == 'grouped_buy')['coverage']
        self.assertEqual([link['layer'] for link in links if 'condition' not in link], ['core_system'])
        self.assertEqual(buy['layers'], [link['layer'] for link in links])
        self.assertNotIn('layers', self.ui['essential']['model_architecture'])
        self.assertNotIn('icon', document['layers'][0])

    def test_model_rejects_ambiguous_identity_unknown_fields_and_references(self):
        def duplicate_layer(d): d['layers'].append(deepcopy(d['layers'][0]))
        def duplicate_part(d): d['layers'][0]['parts'].append(deepcopy(d['layers'][0]['parts'][0]))
        def duplicate_structure(d): d['cost_structures'].append(deepcopy(d['cost_structures'][0]))
        def duplicate_link(d): d['cost_structures'][0]['coverage'] *= 2
        def unknown_layer(d): d['cost_structures'][0]['coverage'][0]['layer'] = 'missing'
        def unknown_condition(d): d['cost_structures'][0]['coverage'][0]['condition'] = 'missing'
        def unknown_notion(d): d['cost_structures'][0]['notion'] = 'missing'
        def unknown_field(d): d['layers'][0]['budget'] = 1
        def orphan_condition(d): d['conditions']['unused'] = 'Non référencée'
        def missing_activity_type(d): d['activity_types'].pop()
        def duplicate_activity_type(d): d['activity_types'][1] = deepcopy(d['activity_types'][0])
        def unknown_activity_notion(d): d['activity_types'][0]['notion'] = 'missing'
        def swapped_activity_notion(d): d['activity_types'][0]['notion'] = 'run_activities'
        def unknown_activity_ref(d): d['cost_structures'][0]['activity_type_refs'] = ['missing']
        def missing_activity_refs(d): d['cost_structures'][0].pop('activity_type_refs')
        def empty_activity_refs(d): d['cost_structures'][0]['activity_type_refs'] = []
        def repeated_activity_ref(d): d['cost_structures'][0]['activity_type_refs'] = ['build', 'build']
        def missing_activity_scope(d): d['cost_structures'][0].pop('activity_scope')
        def monetary_activity_allocation(d): d['cost_structures'][0]['activity_shares'] = {'build': 100}
        for change in (duplicate_layer, duplicate_part, duplicate_structure, duplicate_link,
                       unknown_layer, unknown_condition, unknown_notion, unknown_field, orphan_condition,
                       missing_activity_type, duplicate_activity_type, unknown_activity_notion, swapped_activity_notion,
                       unknown_activity_ref, missing_activity_refs, empty_activity_refs, repeated_activity_ref,
                       missing_activity_scope, monetary_activity_allocation):
            with self.subTest(change=change.__name__):
                document = deepcopy(self.document)
                change(document)
                with self.assertRaisesRegex(ValueError, 'ERR_ARCHITECTURE'):
                    validate_architecture(document, self.glossary)

    def test_activity_tags_follow_canonical_references_without_cost_allocation(self):
        document = deepcopy(self.document)
        structure = next(row for row in document['cost_structures'] if row['id'] == 'client_care')
        structure['activity_type_refs'] = ['run', 'build']
        structure['activity_scope'] = 'Périmètre mixte explicité dans le modèle.'
        glossary = deepcopy(self.glossary)
        glossary['notions']['run_activities']['libelle'] = 'Service continu'
        validated = validate_architecture(document, glossary)
        view = resolve_text_tree(hydrate_architecture(self.ui, validated), glossary)
        row = next(r for r in view['essential']['model_rows'] if r['key'] == structure['id'])
        self.assertEqual(row['activity_tags'], [
            {'id': 'run', 'label': 'Service continu'},
            {'id': 'build', 'label': glossary['notions']['build']['libelle']}])
        self.assertEqual(row['activity_scope'], structure['activity_scope'])
        validated_structure = next(row for row in validated['cost_structures'] if row['id'] == structure['id'])
        self.assertEqual(validated_structure['cost_nature_refs'], structure['cost_nature_refs'])
        row['activity_tags'].clear()
        self.assertEqual(validated_structure['activity_type_refs'], ['run', 'build'])
        ui = deepcopy(self.ui)
        ui['essential']['model_rows'][0]['activity_tags'] = [{'id': 'run', 'label': 'Local'}]
        with self.assertRaisesRegex(ValueError, 'ERR_ARCHITECTURE'):
            hydrate_architecture(ui, validated)

    def test_activity_allocation_is_bounded_and_run_is_derived(self):
        for build_pct in (0, 37.5, 50, 100):
            with self.subTest(build_pct=build_pct):
                document = deepcopy(self.document)
                structure = next(row for row in document['cost_structures'] if row['id'] == 'client_care')
                structure['activity_type_refs'] = ['build', 'run']
                structure['activity_allocation'] = {'build_pct': build_pct, 'basis': 'Hypothèse de pilotage.'}
                validated = validate_architecture(document, self.glossary)
                view = hydrate_architecture(self.ui, validated)['essential']['model_rows']
                allocation = next(row for row in view if row['key'] == structure['id'])['activity_allocation']
                self.assertEqual(allocation['build_pct'] + allocation['run_pct'], 100)
                self.assertEqual(allocation['run_pct'], 100 - build_pct)
                self.assertEqual(allocation['source'], SOURCE + '#cost_structures/' + structure['id'] + '/activity_allocation')
                validated_structure = next(row for row in validated['cost_structures'] if row['id'] == structure['id'])
                self.assertNotIn('run_pct', validated_structure['activity_allocation'])
                self.assertEqual(validated_structure['cost_nature_refs'], structure['cost_nature_refs'])
                allocation['build_pct'] = -1
                self.assertEqual(validated_structure['activity_allocation']['build_pct'], build_pct)
        base = deepcopy(self.document)
        client_index = next(i for i,row in enumerate(base['cost_structures']) if row['id'] == 'client_care')
        base['cost_structures'][client_index]['activity_allocation'] = {'build_pct': 50, 'basis': 'Hypothèse de pilotage.'}
        def missing_basis(s): s['activity_allocation'].pop('basis')
        def separate_run(s): s['activity_allocation']['run_pct'] = 20
        def non_mixed(s): s['activity_type_refs'] = ['build']
        for invalid in (-0.1, 100.1, True, None, '50', float('nan'), float('inf'), float('-inf')):
            document = deepcopy(base)
            document['cost_structures'][client_index]['activity_allocation']['build_pct'] = invalid
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, 'ERR_ARCHITECTURE'):
                validate_architecture(document, self.glossary)
        for change in (missing_basis, separate_run, non_mixed):
            document = deepcopy(base)
            change(document['cost_structures'][client_index])
            with self.subTest(change=change.__name__), self.assertRaisesRegex(ValueError, 'ERR_ARCHITECTURE'):
                validate_architecture(document, self.glossary)

    def test_semantic_permutations_cannot_relabel_existing_budgets(self):
        def swapped_natures(rows):
            rows['obtention']['cost_nature_refs'],rows['integration']['cost_nature_refs'] = (
                rows['integration']['cost_nature_refs'],rows['obtention']['cost_nature_refs'])
        def swapped_notions(rows):
            rows['obtention']['notion'],rows['integration']['notion'] = (
                rows['integration']['notion'],rows['obtention']['notion'])
        def core_as_run(rows): rows['core_care']['activity_type_refs'] = ['run']
        def build_as_mixed(rows): rows['obtention']['activity_type_refs'] = ['build','run']
        def unexplained_buy_split(rows): rows['grouped_buy']['activity_allocation'] = {'build_pct': 50, 'basis': 'Non documenté.'}
        def missing_client_split(rows): rows['client_care'].pop('activity_allocation')
        for change in (swapped_natures,swapped_notions,core_as_run,build_as_mixed,unexplained_buy_split,missing_client_split):
            document=deepcopy(self.document)
            change({row['id']:row for row in document['cost_structures']})
            with self.subTest(change=change.__name__):
                with self.assertRaisesRegex(ValueError,'ERR_ARCHITECTURE'):
                    validate_architecture(document,self.glossary)
                with self.assertRaisesRegex(ValueError,'ERR_ARCHITECTURE'):
                    validate_economic_links(document,{'options':[]})

    def test_ui_cannot_override_model_or_silently_draw_false_boundaries(self):
        def local_layers(v): v['layers'] = []
        def local_coverage(v): v['blocks'][0]['layers'] = ['iaas']
        def missing_cost(v): v['blocks'].pop()
        def missing_icon(v): v['layer_icons'].pop('iaas')
        def overlap(v): v['blocks'][2]['lane'] = 1
        def negative_lane(v): v['blocks'][0]['lane'] = -1
        def unknown_source(v): v['source'] = 'source/other.yaml'
        for change in (local_layers, local_coverage, missing_cost, missing_icon, overlap, negative_lane, unknown_source):
            with self.subTest(change=change.__name__):
                ui = deepcopy(self.ui)
                change(ui['essential']['model_architecture'])
                with self.assertRaisesRegex(ValueError, 'ERR_ARCHITECTURE'):
                    hydrate_architecture(ui, self.document)
        document = deepcopy(self.document)
        document['cost_structures'][0]['coverage'].append({'layer': 'iaas'})
        validate_architecture(document, self.glossary)  # Valid domain relation, unsupported rectangular drawing.
        with self.assertRaisesRegex(ValueError, 'non-contiguous'):
            hydrate_architecture(self.ui, document)

    def test_glossary_change_propagates_without_mutating_sources(self):
        glossary = deepcopy(self.glossary)
        glossary['notions']['core_system']['libelle'] = 'Noyau métier'
        validated = validate_architecture(self.document, glossary)
        resolved = resolve_text_tree(validated, glossary)
        core = next(layer for layer in resolved['layers'] if layer['id'] == 'core_system')
        self.assertEqual(core['label'], 'Noyau métier')
        self.assertIn('Noyau métier', core['definition'])
        validated['layers'][0]['label'] = 'Changed copy'
        self.assertNotEqual(self.document['layers'][0]['label'], 'Changed copy')

    def test_release_freezes_domain_and_view_without_draft_reads(self):
        study = study_copy()
        bundle = candidate(study)
        released = Study.from_release(bundle)
        reference = deepcopy(study.architecture)
        for source in (SOURCE, SCHEMA):
            self.assertIn(source, bundle['payload']['documents'])
            self.assertIn(str((ROOT / source).resolve()), study.source_digests)
        study.architecture['layers'][0]['label'] = 'Future draft'
        study.ui['essential']['model_architecture']['layers'][0]['label'] = 'Future rendering'
        self.assertEqual(released.architecture, reference)
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('unexpected draft read')):
            self.assertEqual(released.simulate(released.parameters), study.baseline)
            view = released.bootstrap(essential=True)['ui']['essential']['model_architecture']
            self.assertEqual(view['layers'][0]['label'], reference['layers'][0]['label'])

    def test_changed_architecture_source_prevents_mixed_release(self):
        study = study_copy()
        original = Path.read_bytes
        def changed(path):
            raw = original(path)
            return raw + b'\n' if path.resolve() == (ROOT / SOURCE).resolve() else raw
        with patch.object(Path, 'read_bytes', changed), self.assertRaisesRegex(ValueError, 'Draft changed since loading'):
            candidate(study)


if __name__ == '__main__':
    unittest.main()
