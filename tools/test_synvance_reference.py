"""The input dossier preserves offer prices and never imports FLOW supplements."""
from copy import deepcopy
from unittest.mock import patch
import unittest

from synvance_reference import SOURCE, compile_synvance_reference
from validate_stacks import ROOT, read
from test_support import reference_study


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
        study = reference_study()
        cls.architecture = study.architecture
        cls.baseline = study.baseline
        cls.economic_evaluations = study.content['economic_evaluations']

    def compile(self, **changes):
        def document_path(path):
            self.assertIn(path.split('#')[0], self.documents)
            self.assertTrue((ROOT / path.split('#')[0]).is_file())
        args = dict(editorial=self.editorial, guide=self.guide, prices=self.prices,
            annual=self.annual, glossary=self.glossary, document_path=document_path,
            architecture=self.architecture, baseline=self.baseline, economic_evaluations=self.economic_evaluations)
        args.update(changes)
        return compile_synvance_reference(**args)

    def test_brief_resolves_original_evidence_and_rejects_broken_references(self):
        guide = deepcopy(self.guide)
        piece = next(row for row in guide['pieces'] if row['id'] == 'copil')
        piece['titre'] = 'Original committee record'
        result = self.compile(guide=guide)
        question = next(row for row in result['brief']['questions'] if row['id'] == 'choix')
        self.assertTrue(any(proof['label'] == piece['titre'] and
            proof['path'] == 'sources/client/copil-5.pdf#page=8' for proof in question['proofs']))
        self.assertNotIn('proof_refs', question)
        for target in ('question', 'highlights'):
            editorial = deepcopy(self.editorial)
            item = editorial['brief']['questions'][0] if target == 'question' else editorial['brief']['highlights']
            item['proof_refs'] = ['missing']
            with self.assertRaisesRegex(ValueError, 'unknown proof'):
                self.compile(editorial=editorial)
        editorial = deepcopy(self.editorial)
        editorial['brief']['questions'][1]['id'] = editorial['brief']['questions'][0]['id']
        with self.assertRaisesRegex(ValueError, 'duplicate id:brief/questions'):
            self.compile(editorial=editorial)

    def test_business_scope_rejects_unknown_evidence_and_duplicate_axes(self):
        for target in ('architecture', 'axis', 'candidate', 'oms'):
            editorial = deepcopy(self.editorial)
            business = editorial['business']
            if target == 'architecture':
                business['architecture_proof_refs'] = ['missing']
            else:
                item = {'axis': business['axes'][0], 'candidate': business['others'][0], 'oms': business['oms']}[target]
                item['proof_refs'] = ['missing']
            with self.assertRaisesRegex(ValueError, 'unknown proof'):
                self.compile(editorial=editorial)
        editorial = deepcopy(self.editorial)
        editorial['business']['axes'][1]['id'] = editorial['business']['axes'][0]['id']
        with self.assertRaisesRegex(ValueError, 'duplicate id:business/axes'):
            self.compile(editorial=editorial)

    def test_pattern_reading_requires_known_patterns_and_original_evidence(self):
        result = self.compile()
        for provider in result['business']['pattern_reading']['providers']:
            self.assertTrue(provider['proofs'])
            self.assertNotIn('proof_refs', provider)
        for field, value, error in [('pattern_ref', 'unknown', 'unknown architecture pattern'),
                                    ('proof_refs', ['unknown'], 'unknown proof')]:
            editorial = deepcopy(self.editorial)
            editorial['business']['pattern_reading']['providers'][0][field] = value
            with self.assertRaisesRegex(ValueError, error):
                self.compile(editorial=editorial)

    def test_cost_comparison_tracks_sources_and_covers_all_documented_annual_posts(self):
        annual = deepcopy(self.annual)
        post = next(row for row in annual['sap']['postes'] if row['id'] == 'rfi-evolutions')
        post['montants_documentes_eur_ht'][0]['montant'] += 123.45
        result = self.compile(annual=annual)
        rows = {row['structure_ref']:row for row in result['costs']['rows']}
        entry = next(e for e in rows['client_care']['sap']['entries'] if e['source_id'] == 'evolutions')
        self.assertEqual(entry['amounts'][0]['amount_eur'], post['montants_documentes_eur_ht'][0]['montant'])
        self.assertNotIn('amount_eur', rows['client_care']['microsoft'])
        self.assertEqual(rows['client_care']['microsoft']['entries'], [])
        editorial = deepcopy(self.editorial)
        next(row for row in editorial['costs']['rows'] if row['structure_ref'] == 'client_care')['sap']['entries'].pop()
        with self.assertRaisesRegex(ValueError, 'source annual comparison coverage:sap'):
            self.compile(editorial=editorial)

    def test_model_comparison_reconciles_all_structures_and_horizons_without_repricing(self):
        result = self.compile()
        model = result['costs']['model']
        self.assertEqual([h['years'] for h in model['horizons']], [3,5,7,10])
        for horizon in model['horizons']:
            self.assertEqual({r['id'] for r in horizon['rows']}, {r['id'] for r in self.architecture['cost_structures']})
            for slug in ('microsoft','sap'):
                option = next(o for o in self.baseline['options'] if o['stack'] == slug)
                original = next(h for h in option['horizons'] if h['years'] == horizon['years'])
                self.assertAlmostEqual(sum(row['amounts'][slug] for row in horizon['rows']), original['totals']['total'], places=2)
                self.assertEqual(horizon['totals'][slug], original['totals']['total'])
                cloud = next(row for row in horizon['rows'] if row['id'] == 'run_cloud')
                self.assertAlmostEqual(cloud['amounts'][slug], original['cost_natures']['run_cloud'] + original['cost_natures']['technical_purchases'], places=2)
        changed = deepcopy(self.baseline)
        option = next(o for o in changed['options'] if o['stack'] == 'microsoft')
        option['horizons'][0]['cost_natures']['grouped_buy'] += 100
        option['horizons'][0]['totals']['total'] += 100
        updated = self.compile(baseline=changed)
        self.assertEqual(updated['costs']['model']['horizons'][0]['totals']['microsoft'], model['horizons'][0]['totals']['microsoft'] + 100)
        option['horizons'][0]['totals']['total'] += 10
        with self.assertRaisesRegex(ValueError, 'model total reconciliation:microsoft'):
            self.compile(baseline=changed)

    def test_cost_comparison_rejects_duplicate_categories_and_has_isolated_outputs(self):
        editorial = deepcopy(self.editorial)
        editorial['costs']['rows'][1]['structure_ref'] = editorial['costs']['rows'][0]['structure_ref']
        with self.assertRaisesRegex(ValueError, 'cost structure coverage'):
            self.compile(editorial=editorial)
        architecture = deepcopy(self.architecture)
        architecture['cost_structures'][0]['cost_nature_refs'].append('grouped_buy')
        with self.assertRaisesRegex(ValueError, 'duplicate model nature allocation'):
            self.compile(architecture=architecture)
        before = deepcopy((self.architecture,self.baseline,self.economic_evaluations))
        result = self.compile()
        result['costs']['model']['bridge'][0]['annual']['items']['services_mco'] = -1
        result['costs']['model']['horizons'][0]['rows'][0]['amounts']['microsoft'] = -1
        self.assertEqual((self.architecture,self.baseline,self.economic_evaluations), before)

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
