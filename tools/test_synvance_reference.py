"""The input dossier preserves offer prices and never imports FLOW supplements."""
from copy import deepcopy
from unittest.mock import patch
import unittest

from synvance_reference import SOURCE, compile_synvance_reference
from validate_stacks import ROOT, read


class SynvanceReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.editorial = read(ROOT / SOURCE)
        cls.guide = read(ROOT / 'source/parcours-synvance.yaml')
        cls.glossary = read(ROOT / 'source/glossaire.yaml')
        cls.prices = {slug: read(ROOT / f'source/chiffrage/chiffrage-{slug}.yaml')['integration']['prix_rfi']
            for slug in ('microsoft', 'sap')}
        cls.annual = {slug: read(ROOT / f'source/maintenance/maintenance-{slug}.yaml')['valorisation_annuelle']
            for slug in ('microsoft', 'sap')}
        cls.documents = set(read(ROOT / 'config/publication.yaml')['documents'])

    def compile(self, **changes):
        def document_path(path):
            self.assertIn(path.split('#')[0], self.documents)
            self.assertTrue((ROOT / path.split('#')[0]).is_file())
        args = dict(editorial=self.editorial, guide=self.guide, prices=self.prices,
            annual=self.annual, glossary=self.glossary, document_path=document_path)
        args.update(changes)
        return compile_synvance_reference(**args)

    def test_prices_follow_their_owners_and_keep_published_total_distinct(self):
        prices = deepcopy(self.prices)
        prices['microsoft']['postes_eur'][0] += 123.45
        prices['microsoft']['total_imprime_eur'] += 123.45
        prices['sap']['postes_eur'][1] += 321.12
        result = self.compile(prices=prices)
        microsoft, sap = result['synthesis']['providers']
        ms = {r['id']: r['amount_eur'] for r in microsoft['integration']['rows']}
        self.assertEqual(ms['pilote-copil'], prices['microsoft']['postes_eur'][0])
        self.assertEqual(ms['poles-copil'], prices['microsoft']['postes_eur'][1])
        self.assertEqual(ms['total-copil'], prices['microsoft']['total_imprime_eur'])
        rows = {r['id']: r['amount_eur'] for r in sap['integration']['rows']}
        self.assertAlmostEqual(rows['somme-lots'], sum(prices['sap']['postes_eur']))
        self.assertEqual(rows['total-imprime'], prices['sap']['total_imprime_eur'])
        self.assertAlmostEqual(rows['ecart-total'], rows['total-imprime'] - rows['somme-lots'])
        self.assertNotEqual(rows['total-imprime'], rows['somme-lots'])

    def test_annual_sequences_are_documented_prices_without_projection_or_estimates(self):
        annual = deepcopy(self.annual)
        for owner in annual.values():
            for post in owner['postes']:
                post['projection']['a_partir_annee'] = 999
                if post['montants_documentes_eur_ht']:
                    post['montants_documentes_eur_ht'][0]['montant'] += .37
        result = self.compile(annual=annual)
        for provider in result['synthesis']['providers']:
            source = {row['id']:row for row in annual[provider['id']]['postes']}
            instructions = next(p for p in self.editorial['synthesis']['providers'] if p['id']==provider['id'])
            for row, spec in zip(provider['annual']['rows'], instructions['annual']['rows']):
                expected = source[spec['post_ref']]
                self.assertEqual(row['source_year'], expected['annee_prix'])
                self.assertEqual(row['amounts'], [dict(year=a['annee'], amount_eur=a['montant'])
                    for a in expected['montants_documentes_eur_ht']])
                self.assertNotIn('projection',row)
        initial_support=result['synthesis']['providers'][0]['annual']['rows'][1]
        self.assertEqual(len(initial_support['amounts']),1)

    def test_overview_uses_the_same_provider_rows_and_never_its_own_amounts(self):
        prices=deepcopy(self.prices)
        prices['microsoft']['total_imprime_eur'] += 123.45
        prices['sap']['postes_eur'][0] += 543.21
        result=self.compile(prices=prices)
        providers={provider['id']:provider for provider in result['synthesis']['providers']}
        self.assertEqual([card['id'] for card in result['overview']['cards']],['microsoft','sap'])
        for card in result['overview']['cards']:
            self.assertEqual(card['href'],'#synvance-'+card['id'])
            self.assertEqual(len(card['highlights']),1)
            highlight=card['highlights'][0]
            original=next(row for row in providers[card['id']]['integration']['rows'] if row['id']==highlight['id'])
            self.assertEqual({k:v for k,v in highlight.items() if k!='label'},
                {k:v for k,v in original.items() if k!='label'})
            highlight['proofs'].clear()
            self.assertTrue(original['proofs'])
        self.assertEqual(result['overview']['cards'][0]['highlights'][0]['amount_eur'],
            prices['microsoft']['total_imprime_eur'])
        self.assertAlmostEqual(result['overview']['cards'][1]['highlights'][0]['amount_eur'],
            sum(prices['sap']['postes_eur']))
        editorial=deepcopy(self.editorial)
        editorial['overview']['cards'][0]['highlights'][0]['row_ref']='somme-lots'
        with self.assertRaisesRegex(ValueError,'overview row'):
            self.compile(editorial=editorial)
        editorial=deepcopy(self.editorial)
        editorial['overview']['cards'][0]['highlights'][0]['amount_eur']=1
        with self.assertRaisesRegex(ValueError,'ERR_SYNVANCE_REFERENCE'):
            self.compile(editorial=editorial)

    def test_provider_contexts_and_reading_roles_cannot_override_source_meaning(self):
        result=self.compile()
        self.assertNotIn('context',result)
        microsoft,sap=result['synthesis']['providers']
        self.assertNotEqual(microsoft['context'],sap['context'])
        for provider in (microsoft,sap):
            self.assertTrue(provider['context']['title'])
            self.assertTrue(provider['context']['lead'])
            self.assertTrue(provider['context']['items'])
        self.assertEqual([row['reading_role'] for row in microsoft['integration']['rows']],
            ['detail','detail','published'])
        self.assertEqual([row['reading_role'] for row in sap['integration']['rows']],
            ['detail','detail','detail','sum','published','difference'])
        editorial=deepcopy(self.editorial)
        del editorial['synthesis']['providers'][0]['context']
        with self.assertRaisesRegex(ValueError,'ERR_SYNVANCE_REFERENCE'):
            self.compile(editorial=editorial)
        editorial=deepcopy(self.editorial)
        editorial['context']=dict(title='Shared context',paragraphs=['Shared context'])
        with self.assertRaisesRegex(ValueError,'ERR_SYNVANCE_REFERENCE'):
            self.compile(editorial=editorial)
        editorial=deepcopy(self.editorial)
        editorial['synthesis']['providers'][0]['integration']['rows'][0]['reading_role']='published'
        with self.assertRaisesRegex(ValueError,'ERR_SYNVANCE_REFERENCE'):
            self.compile(editorial=editorial)

    def test_input_links_follow_original_catalogue_before_price_reading(self):
        guide = deepcopy(self.guide)
        item = next(row for row in guide['pieces'] if row['id'] == 'demande')
        item['path'] = item['path'].split('#')[0] + '#page=6'
        result = self.compile(guide=guide)
        expected = {row['path'] for row in guide['pieces'] if row['id'] in {
            'demande', 'besoins', 'questionnaire_microsoft', 'questionnaire_sap'}}
        self.assertEqual({row['path'] for row in result['overview']['inputs']}, expected)
        editorial = deepcopy(self.editorial)
        editorial['overview']['inputs'][0]['piece_ref'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'input evidence coverage'):
            self.compile(editorial=editorial)

    def test_compilation_is_pure_and_returns_isolated_values(self):
        before=deepcopy((self.editorial,self.guide,self.prices,self.annual))
        with patch('synvance_reference.read',side_effect=AssertionError('unexpected source read')):
            result=self.compile()
        result['documents']['items'][0]['title']='changed'
        result['synthesis']['providers'][0]['annual']['rows'][0]['amounts'].clear()
        self.assertEqual((self.editorial,self.guide,self.prices,self.annual),before)

    def test_original_documents_are_all_available_and_no_model_file_is_an_action(self):
        result=self.compile()
        documents=result['documents']['items']
        self.assertEqual(sum(row['format']=='pdf' for row in documents),5)
        self.assertEqual(sum(row['format']=='xlsx' for row in documents),2)
        for provider in result['synthesis']['providers']:
            for section in ('integration','annual'):
                for row in provider[section]['rows']:
                    self.assertTrue(row['proofs'])
                    self.assertTrue(all(p['path'].split('#')[0].endswith(('.pdf','.xlsx')) for p in row['proofs']))
                    self.assertNotIn('proof_refs',row)
                    self.assertNotIn('binding',row)

    def test_contextual_proofs_name_the_exact_original_and_recorded_passage(self):
        result=self.compile()
        microsoft,sap=result['synthesis']['providers']
        self.assertEqual(microsoft['integration']['rows'][0]['proofs'][0]['path'],
            'sources/client/copil-5.pdf#page=7')
        self.assertEqual(microsoft['integration']['rows'][0]['proofs'][1]['path'],
            'sources/client/microsoft-1.pdf#page=39')
        self.assertTrue(all(row['proofs'][0]['path']=='sources/client/delaware-septembre.pdf#page=38'
            for row in sap['integration']['rows']))
        self.assertEqual(sap['annual']['rows'][0]['proofs'][0]['path'],
            'sources/client/delaware-septembre.pdf#page=45')
        self.assertTrue(all(row['proofs'][0]['path']=='sources/client/delaware-septembre.pdf#page=37'
            for row in sap['annual']['rows'][1:]))
        support=microsoft['annual']['rows'][1]['proofs'][0]
        self.assertEqual(support['path'],'sources/client/microsoft-questionnaire.xlsx')
        self.assertIn('C13/D13',support['location'])
        evidence=read(ROOT/'sources/integration-maintenance-2026-10-22.yaml')['sources']
        for provider in result['synthesis']['providers']:
            original={row['id']:row for row in self.annual[provider['id']]['postes']}
            specs=next(p for p in self.editorial['synthesis']['providers'] if p['id']==provider['id'])
            for row,spec in zip(provider['annual']['rows'],specs['annual']['rows']):
                expected={evidence[ref]['reference'] for ref in original[spec['post_ref']]['sources']}
                observed={proof['path'].split('#')[0] for proof in row['proofs']}
                self.assertTrue(expected <= observed)
        editorial=deepcopy(self.editorial)
        editorial['passages'][0]['page']=None
        with self.assertRaisesRegex(ValueError,'page must name a PDF passage'):
            self.compile(editorial=editorial)
        editorial=deepcopy(self.editorial)
        editorial['passages'][0]['piece_ref']='missing'
        with self.assertRaisesRegex(ValueError,'unknown source piece'):
            self.compile(editorial=editorial)

    def test_invented_bindings_proofs_or_unknown_prices_are_rejected(self):
        editorial=deepcopy(self.editorial)
        editorial['synthesis']['providers'][0]['integration']['rows'][0]['binding']='model-total'
        with self.assertRaisesRegex(ValueError,'ERR_SYNVANCE_REFERENCE'):
            self.compile(editorial=editorial)
        editorial=deepcopy(self.editorial)
        editorial['synthesis']['providers'][0]['integration']['rows'][0]['proof_refs']=['missing']
        with self.assertRaisesRegex(ValueError,'unknown proof'):
            self.compile(editorial=editorial)
        prices=deepcopy(self.prices)
        prices['microsoft']['postes_eur'][0]=None
        with self.assertRaisesRegex(ValueError,'invalid source number'):
            self.compile(prices=prices)

    def test_repeated_or_estimated_annual_rows_cannot_be_presented_as_documented(self):
        annual=deepcopy(self.annual)
        row=next(p for p in annual['microsoft']['postes'] if p['id']=='MAI-010/licences')
        row['methode']='estimation'
        with self.assertRaisesRegex(ValueError,'not a documented price'):
            self.compile(annual=annual)
        annual=deepcopy(self.annual)
        row=next(p for p in annual['microsoft']['postes'] if p['id']=='MAI-010/licences')
        row['montants_documentes_eur_ht'].append(deepcopy(row['montants_documentes_eur_ht'][0]))
        with self.assertRaisesRegex(ValueError,'source year sequence'):
            self.compile(annual=annual)


if __name__ == '__main__':
    unittest.main()
