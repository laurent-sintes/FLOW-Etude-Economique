"""Full instruction inventory and guarded documentary price extensions."""
from copy import deepcopy
import unittest

from market_instruction import build_market_instruction, SOURCE
from market_oss import enrich_market_products
from validate_stacks import ROOT, read


class MarketInstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.market = read(ROOT / 'source/references-couts-integration.yaml')
        cls.grid = read(ROOT / 'source/grille-complexite.yaml')
        cls.source = read(ROOT / SOURCE)

    def record(self):
        block = next(block for block in self.grid['blocs'] if block['id'] == 'BC-010')
        return dict(id='test-observation', capability_ref=block['capacite_id'], product_ref='erpnext',
            need_refs=[block['fonctions'][0]['id']], function_label='Fonction de contrôle du contrat',
            evaluation_function_ref=None, status='a_qualifier', classification='fait_observe',
            evidence_refs=[dict(source_ref='source/references-couts-integration.yaml', location='reperes_build_core/fiches_produit/erpnext/evaluations/transactions')],
            differences=['Périmètre du besoin à confirmer.'], unknowns=['Parité non démontrée.'], review=None)

    def test_proposed_functions_belong_to_separate_analysis(self):
        from test_support import study_copy
        study=study_copy()
        rows=study.content['market']['instruction']['capabilities']
        for row in rows:
            self.assertEqual(row['analysis_source'],'source/analyse-perimetre-core.yaml')
            self.assertEqual([f['id'] for f in row['proposed_functions']],row['need_refs'])
        self.assertTrue(all('fonctions' not in r for r in study.bootstrap(essential=True)['content']['complexity']['rows']))

    def test_all_capability_product_pairs_exist_without_fabricated_coverage(self):
        before = deepcopy(self.market)
        instruction = deepcopy(self.source)
        instruction['qualifications'] = []
        matrix = build_market_instruction(self.market, grid=self.grid, instruction=instruction)
        self.assertEqual(self.market, before)
        self.assertEqual(matrix['summary']['pairs'], 84 * 6)
        self.assertEqual(matrix['summary']['pairs_by_status'], dict(non_etudie=354, reperes_axes=150, qualification_detaillee=0))
        self.assertEqual(matrix['summary']['retained_qualifications'], 0)
        self.assertEqual(len({(row['capability_ref'], row['product_ref']) for row in matrix['rows']}), 504)
        for row in matrix['rows']:
            self.assertEqual(row['functional_status'], 'non_qualifie')
            self.assertTrue(row['pending_need_refs'])
            self.assertNotIn(row['bc_ref'], {'BC-016', 'BC-017', 'BC-074', 'BC-075'})
            self.assertEqual(bool(row['observation_refs']), row['status'] == 'reperes_axes')
        for progress in matrix['progress']:
            self.assertEqual((progress['non_etudie'], progress['reperes_axes'], progress['qualification_detaillee']), (59, 25, 0))

    def test_precise_qualification_keeps_gaps_and_does_not_claim_whole_capability(self):
        instruction = deepcopy(self.source)
        record = self.record()
        record.update(status='qualifie', unknowns=[], review=dict(date='2026-10-28', reviewer='Contrôle de contrat', decision='retenu'))
        instruction['qualifications'] = [record]
        result = build_market_instruction(self.market, grid=self.grid, instruction=instruction)
        row = next(row for row in result['rows'] if row['capability_ref'] == record['capability_ref'] and row['product_ref'] == 'erpnext')
        self.assertEqual(row['status'], 'qualification_detaillee')
        self.assertNotIn(record['need_refs'][0], row['pending_need_refs'])
        self.assertTrue(row['pending_need_refs'])
        self.assertEqual(result['qualifications'][0]['differences'], record['differences'])

    def test_unknowns_cannot_be_promoted_and_fields_references_are_closed(self):
        mutations = [lambda row: row.update(status='qualifie'),
                     lambda row: row.update(classification='inconnu', unknowns=[]),
                     lambda row: row.update(product_ref='missing'),
                     lambda row: row.update(need_refs=['BC-001.01']),
                     lambda row: row.update(evaluation_function_ref='missing'),
                     lambda row: row.update(evidence_refs=[]),
                     lambda row: row.update(budget=100)]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                instruction = deepcopy(self.source)
                record = self.record()
                mutate(record)
                instruction['qualifications'] = [record]
                with self.assertRaisesRegex(ValueError, 'ERR_MARKET_INSTRUCTION'):
                    build_market_instruction(self.market, grid=self.grid, instruction=instruction, core_functions=[])

    def test_optional_core_link_matches_native_capability_and_need(self):
        instruction = deepcopy(self.source)
        record = self.record()
        record['evaluation_function_ref'] = 'test-function'
        instruction['qualifications'] = [record]
        function = dict(id='test-function', capability_refs=[record['capability_ref']], need_refs=record['need_refs'])
        build_market_instruction(self.market, grid=self.grid, instruction=instruction, core_functions=[function])
        function['capability_refs'] = ['other-capability']
        with self.assertRaisesRegex(ValueError, 'Core evaluation function'):
            build_market_instruction(self.market, grid=self.grid, instruction=instruction, core_functions=[function])

    def test_product_price_requires_located_evidence_units_scope_and_sequence(self):
        data = deepcopy(self.market['reperes_build_core'])
        fiche = data['fiches_produit']['microsoft']
        fiche['prix_observe_eur_ht'] = 100
        ids = {block['id'] for block in self.grid['blocs']}
        with self.assertRaisesRegex(ValueError, 'qualification_prix'):
            enrich_market_products(data, ids)
        fiche['qualification_prix'] = dict(observe=dict(nature='reconstruction_produit', date='2026-10-28',
            devise='EUR', unite='EUR', regime_fiscal='HT', perimetre='Périmètre de test du contrat uniquement',
            inclusions='Travaux décrits dans la preuve', exclusions='Licences et exploitation', sequence='Construction initiale',
            preuves=[dict(source_ref='source/references-couts-integration.yaml', localisation='Test du contrat, pas une donnée observée')]), retraite_flow=None)
        enrich_market_products(data, ids)
        fiche['qualification_prix']['observe']['unite'] = 'kEUR'
        with self.assertRaisesRegex(ValueError, 'EUR units'):
            enrich_market_products(data, ids)

    def test_flow_product_price_requires_observed_base_and_reviewed_bridge(self):
        data = deepcopy(self.market['reperes_build_core'])
        fiche = data['fiches_produit']['microsoft']
        fiche['prix_retraite_flow_eur_2026'] = 100
        fiche['qualification_prix'] = dict(observe=None, retraite_flow=dict(nature='reconstruction_produit', date='2026-10-28',
            devise='EUR', unite='EUR', regime_fiscal='HT', perimetre='Test du périmètre FLOW', inclusions='Développement',
            exclusions='Licences', sequence='Initiale', preuves=[dict(source_ref='source/references-couts-integration.yaml', localisation='Test')],
            annee_valeur=2026, pont_perimetre='Ajouts et retraits à documenter', hypotheses='Hypothèse de contrôle',
            revue=dict(date='2026-10-28', auteur='Contrôle de contrat', decision='retenu')))
        with self.assertRaisesRegex(ValueError, 'requires observed price'):
            enrich_market_products(data, {block['id'] for block in self.grid['blocs']})


if __name__ == '__main__':
    unittest.main()
