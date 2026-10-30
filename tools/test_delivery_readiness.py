"""Delivery evidence stays documentary, closed, and separate from financial inputs."""
from copy import deepcopy
import json
import unittest
from urllib.parse import parse_qs, urlsplit

from delivery_readiness import compile_delivery, METHOD_SOURCE, DOSSIER_SOURCE, ATLAS
from study_app import Study
from validate_stacks import ROOT, read


class DeliveryReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.method = read(ROOT / METHOD_SOURCE)
        cls.dossier = read(ROOT / DOSSIER_SOURCE)
        cls.complexity = Study._complexity_grid()
        cls.snapshot = read(ROOT / cls.complexity['source'])
        cls.decision = read(ROOT / 'source/decision-make-buy.yaml')
        cls.glossary = read(ROOT / 'source/glossaire.yaml')
        cls.documents = set(read(ROOT / 'config/publication.yaml')['documents'])

    def compile(self, **overrides):
        def document_path(path):
            self.assertIn(path.split('#')[0], self.documents)
            self.assertTrue((ROOT / path.split('#')[0]).is_file())
        args = dict(method=self.method, dossier=self.dossier, complexity=self.complexity,
            snapshot=self.snapshot, decision=self.decision, glossary=self.glossary,
            document_path=document_path)
        args.update(overrides)
        return compile_delivery(**args)

    def test_two_reading_pages_have_visible_sections_and_no_calculation(self):
        method, dossier = self.compile()
        self.assertEqual(method['next']['href'], '#marche')
        self.assertEqual([section['id'] for section in method['sections']], ['maitrise','capacite','preuve','trajectoire'])
        self.assertEqual([section['id'] for section in dossier['sections']], ['organisation','points-chauds','partenaire','jalons'])
        for page in (method, dossier):
            self.assertEqual(page['examples'], [])
            self.assertNotIn('amount_eur', json.dumps(page))
            for section in page['sections']:
                for block in section['blocks']:
                    self.assertIn(block['kind'], ('paragraphs','bullets','table','links','callout'))
                    if block['kind'] == 'table':
                        self.assertTrue(all(len(row) == len(block['columns']) for row in block['rows']))
        links = [item['href'] for section in dossier['sections'] for block in section['blocks']
                 if block['kind'] == 'links' for item in block['items']]
        self.assertIn('#perimetre-retenu', links)
        self.assertIn('#synvance', links)

    def test_scope_is_derived_from_the_loaded_capture_and_preserves_native_ids(self):
        _, dossier = self.compile()
        scope = dossier['scope']
        self.assertEqual(scope['source']['version'], self.snapshot['provenance']['version'])
        self.assertEqual(scope['source']['revision'], self.snapshot['provenance']['sha256'])
        self.assertEqual(scope['source']['date'], self.snapshot['date_capture'])
        self.assertEqual(scope['link']['href'], ATLAS)
        self.assertEqual(len(scope['rows']), len(self.complexity['rows']))
        for row, original in zip(scope['rows'], self.complexity['rows']):
            self.assertEqual(row['capability_id'], original['capacite_id'])
            self.assertNotIn('complexity', row)
            self.assertEqual(row['definition'], original['capacite']['definition'])
            self.assertEqual(row['boundary'], original['capacite']['perimetre'])
            self.assertEqual(row['name'], original['capacite']['nom'])
            self.assertEqual(row['path'], [node['nom'] for node in original['hierarchie']])
            self.assertEqual(parse_qs(urlsplit(row['href']).fragment.split('?',1)[1])['node'], [row['capability_id']])

    def test_scope_hierarchy_partitions_capabilities_by_native_parentage(self):
        _, dossier = self.compile()
        scope = dossier['scope']
        originals = {row['capacite_id']: row for row in self.complexity['rows']}
        grouped_ids = []
        for domain in scope['hierarchy']:
            for subdomain in domain['subdomains']:
                for area in subdomain['areas']:
                    for capability_id in area['capability_ids']:
                        grouped_ids.append(capability_id)
                        original = originals[capability_id]
                        self.assertEqual([domain['id'], subdomain['id'], area['id']],
                                         [node['id'] for node in original['hierarchie']])
                        self.assertEqual([domain['label'], subdomain['label'], area['label']],
                                         [node['nom'] for node in original['hierarchie']])
        self.assertEqual(len(grouped_ids), len(set(grouped_ids)))
        self.assertEqual(set(grouped_ids), set(originals))

    def test_scope_scale_uses_the_canonical_ordinal_definitions_without_regrading(self):
        _, dossier = self.compile()
        scope = dossier['scope']
        self.assertNotIn('scale', scope)
        self.assertNotIn('axes', scope)
        self.assertTrue(all('complexity' not in row for row in scope['rows']))

    def test_missing_partner_proofs_are_never_presented_as_available(self):
        _, dossier = self.compile()
        partner = next(section for section in dossier['sections'] if section['id'] == 'partenaire')
        self.assertTrue(all('Pièce à obtenir' in row[1] for row in partner['blocks'][0]['rows']))
        for proof in self.dossier['proofs']:
            if proof['status'] == 'attendue':
                self.assertIsNone(proof['source_ref'])
                self.assertIsNone(proof['href'])
        self.assertTrue(all(gate['status'] == 'a_demontrer' for gate in self.dossier['gates']))

    def test_unknown_fields_references_and_unconfirmed_validation_are_rejected(self):
        changes = [lambda d: d.update(budget=1),
                   lambda d: d['hotspots'][0]['capability_refs'].append('invented-capability'),
                   lambda d: d['roles'][0]['criteria_refs'].append('invented-criterion'),
                   lambda d: d['roles'][0].update(decision_ref='invented-decision'),
                   lambda d: d['hotspots'][0].update(gate_ref='invented-gate'),
                   lambda d: d['roles'][0].update(status='demontre'),
                   lambda d: d['scope']['link'].update(href='https://example.com/')]
        for change in changes:
            dossier = deepcopy(self.dossier)
            change(dossier)
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.compile(dossier=dossier)

    def test_expected_documents_cycles_and_proof_roles_are_checked(self):
        changes = [lambda d: d['proofs'][2].update(source_ref='source/decision-make-buy.yaml'),
                   lambda d: d['proofs'][0].update(source_ref=None),
                   lambda d: d['gates'][0]['depends_on'].append(d['gates'][-1]['id']),
                   lambda d: d['hotspots'][0].update(available_refs=['demonstration'])]
        for change in changes:
            dossier = deepcopy(self.dossier)
            change(dossier)
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.compile(dossier=dossier)

    def test_method_links_and_table_shapes_are_checked(self):
        for field in ('link', 'width'):
            method = deepcopy(self.method)
            if field == 'link':
                method['next']['href'] = 'source/fondamentaux.yaml'
            else:
                method['criteria'][2]['blocks'][0]['rows'][0].append('extra')
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.compile(method=method)

    def test_compilation_is_pure_and_outputs_are_isolated(self):
        before = deepcopy((self.method, self.dossier, self.complexity, self.snapshot, self.decision))
        result = self.compile()
        self.assertEqual(before, (self.method, self.dossier, self.complexity, self.snapshot, self.decision))
        result[1]['scope']['rows'][0]['name'] = 'mutated'
        self.assertNotEqual(self.compile()[1]['scope']['rows'][0]['name'], 'mutated')


if __name__ == '__main__':
    unittest.main()
