"""Market methodology is shared editorial evidence, never a price input."""
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

from content_model import resolve_text_tree, validate_glossary_literals
from core_method import MARKET_METHOD_SOURCE, compile_market_method, hydrate_market_method
from validate_stacks import ROOT, read
from test_support import study_copy
from study_app import Study
from study_snapshot import candidate


class MarketMethodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document=read(ROOT/MARKET_METHOD_SOURCE)

    def test_method_uses_its_source_without_mutating_it_or_product_evidence(self):
        original=deepcopy(self.document)
        source_ui=read(ROOT/'config/application.yaml')
        ui=hydrate_market_method(source_ui)
        self.assertEqual(ui['essential']['market_method']['document'],compile_market_method(original))
        self.assertEqual(self.document,original)
        self.assertEqual(ui['essential']['market_method']['application'],source_ui['essential']['market_method']['application'])
        ui['essential']['market_method']['application']['label']='Changed presentation'
        self.assertNotEqual(ui['essential']['market_method']['application'],source_ui['essential']['market_method']['application'])
        self.assertEqual(set(ui['essential']['market_method']), {'application', 'document'})
        glossary=read(ROOT/'source/glossaire.yaml')
        validate_glossary_literals(original,glossary,path=MARKET_METHOD_SOURCE)
        glossary['notions']['core_system']['libelle']='Noyau métier'
        rendered=resolve_text_tree(original,glossary)
        self.assertIn('Noyau métier',rendered['principle']['text'])
        self.assertIn('{{notion.core_system}}',original['principle']['text'])

    def test_schema_rejects_conflicting_methods_tables_and_arbitrary_prices(self):
        broken=[]
        item=deepcopy(self.document);item['id']='core-evaluation-opportunity';broken.append(item)
        item=deepcopy(self.document);item['sections'].append(deepcopy(item['sections'][0]));broken.append(item)
        item=deepcopy(self.document);item['price_eur']=100;broken.append(item)
        item=deepcopy(self.document)
        table=next(b for s in item['sections'] for b in s['blocks'] if b['kind']=='table')
        table['rows'][0].pop();broken.append(item)
        item=deepcopy(self.document);item['examples']=[{}];broken.append(item)
        item=deepcopy(self.document);item['next']['href']='#parametres';broken.append(item)
        for index,document in enumerate(broken):
            with self.subTest(index=index),self.assertRaisesRegex(ValueError,'ERR_MARKET_METHOD'):
                compile_market_method(document)

    def test_missing_owner_is_not_silently_replaced_by_another_method(self):
        ui=read(ROOT/'config/application.yaml')
        ui['essential']['market_method']['source']='source/methode-evaluation-core.yaml'
        with self.assertRaisesRegex(ValueError,'ERR_MARKET_METHOD'):hydrate_market_method(ui)
        ui=read(ROOT/'config/application.yaml')
        ui['essential']['market_method'].pop('application')
        with self.assertRaisesRegex(ValueError,'ERR_MARKET_METHOD'):hydrate_market_method(ui)
        for href in ('#marche', '#missing-page', 'https://example.com'):
            ui=read(ROOT/'config/application.yaml')
            ui['essential']['market_method']['application']['href']=href
            with self.subTest(href=href),self.assertRaisesRegex(ValueError,'ERR_MARKET_METHOD'):
                hydrate_market_method(ui)

    def test_market_hands_its_references_to_the_next_estimation_page(self):
        study=study_copy()
        essential=study.ui['essential']
        order=next(group['items'] for group in essential['nav_groups'] if 'marche' in group['items'])
        destination=essential['market_method']['document']['next']['href'].removeprefix('#')
        self.assertEqual(destination,order[order.index('marche')+1])
        self.assertIn(destination,essential['pages'])

    def test_release_freezes_method_and_market_text_does_not_change_costs(self):
        study=study_copy()
        baseline=deepcopy(study.baseline)
        product_fiches=deepcopy(study.content['market']['reperes_build_core']['fiches_produit'])
        released=Study.from_release(candidate(study))
        frozen=deepcopy(released.ui['essential']['market_method'])
        study.ui['essential']['market_method']['document']['notice']['text']='Changed draft narrative'
        self.assertEqual(study.simulate(study.parameters),baseline)
        self.assertEqual(study.content['market']['reperes_build_core']['fiches_produit'],product_fiches)
        with patch.object(Path,'read_bytes',side_effect=AssertionError('unexpected draft read')):
            actual=released.bootstrap(essential=True)
            self.assertEqual(actual['ui']['essential']['market_method'],frozen)
            self.assertEqual(released.simulate(released.parameters),baseline)


if __name__=='__main__':unittest.main()
