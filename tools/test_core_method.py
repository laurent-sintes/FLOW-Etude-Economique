"""The displayed method has one owner; illustrations never change economics."""
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

from content_model import resolve_text_tree, validate_glossary_literals
from core_method import (METHOD_SOURCE, NET_METHOD_SOURCE, LEVERS_METHOD_SOURCE,
                         compile_method, compile_net_method, compile_levers_method,
                         hydrate_core_method, hydrate_net_method, hydrate_levers_method)
from validate_stacks import ROOT, read
from test_support import study_copy
from study_app import Study
from study_snapshot import candidate


def illustrative_document():
    """Exercise the compatible example format without restoring a public example."""
    return dict(
        schema_version=1, id='core-evaluation-opportunity',
        principle=dict(title='Test method',text='Synthetic teaching content.'),
        notice=dict(title='Test fixture',text='No economic input.'),
        navigation_label='Test navigation',
        sections=[dict(
            id='test-illustration',kind='example',eyebrow='Fictional test data',
            title='Test illustration',lead='Synthetic values.',
            blocks=[dict(kind='table',caption='Test table',columns=['Input','Output'],rows=[['A','B']]),
                    dict(kind='example',ref='test-example')])],
        examples=[dict(
            id='test-example',title='Test example',note='Synthetic values.',
            columns=['Work','Basis','Effort'],
            rows=[dict(id='test-work',label='Work',basis='Synthetic basis.',quantity=3,unit_jh=12)],
            total_label='Test total',unit='JH',
            uncertainty=dict(down_pct=5,up_pct=15,label='Test uncertainty',explanation='Synthetic range.'))],
        next=dict(href='#calcul-net',label='Next page'))


class CoreMethodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document=read(ROOT/METHOD_SOURCE)

    def test_illustration_is_derived_without_mutating_its_source(self):
        source=illustrative_document()
        example=source['examples'][0]
        example['rows'][0]['unit_jh']=17
        example['uncertainty'].update(down_pct=10,up_pct=20)
        actual=compile_method(source)['examples'][0]
        expected=sum(row['quantity']*row['unit_jh'] for row in example['rows'])
        self.assertEqual(actual['total_jh'],expected)
        self.assertEqual(actual['uncertainty']['lower_jh'],round(expected*.9,2))
        self.assertEqual(actual['uncertainty']['upper_jh'],round(expected*1.2,2))
        self.assertNotIn('total_jh',example)
        self.assertNotIn('jh',example['rows'][0])

    def test_invalid_or_ambiguous_content_is_rejected(self):
        broken=[]
        item=illustrative_document();item['examples'][0]['id']='missing-example';broken.append(item)
        item=illustrative_document();item['sections'].append(deepcopy(item['sections'][0]));broken.append(item)
        item=illustrative_document();item['examples'][0]['rows'][0]['unit_jh']=-1;broken.append(item)
        item=illustrative_document();item['examples'][0]['rows'][0]['unit_jh']=float('nan');broken.append(item)
        item=illustrative_document();item['examples'][0]['rows'][0]['jh']=120;broken.append(item)
        item=illustrative_document();item['examples'][0]['total_jh']=160;broken.append(item)
        item=illustrative_document()
        table=next(b for s in item['sections'] for b in s['blocks'] if b['kind']=='table')
        table['rows'][0].pop();broken.append(item)
        for document in broken:
            with self.subTest(document=broken.index(document)),self.assertRaisesRegex(ValueError,'ERR_CORE_METHOD'):
                compile_method(document)

    def test_fictional_illustration_cannot_be_presented_as_a_method_step(self):
        for change in ('kind','eyebrow'):
            document=illustrative_document()
            section=next(s for s in document['sections'] if any(b['kind']=='example' for b in s['blocks']))
            section.pop(change)
            with self.subTest(missing=change),self.assertRaisesRegex(ValueError,'ERR_CORE_METHOD'):
                compile_method(document)

    def test_reading_links_allow_known_routes_and_reject_ambiguous_targets(self):
        source=illustrative_document()
        block=dict(kind='links',items=[dict(href=href,label='Read the associated page')
                                     for href in ('#parametres', '#leviers', '#etude-marche')])
        source['sections'][0]['blocks'].append(block)
        self.assertEqual(compile_method(source)['sections'][0]['blocks'][-1],block)
        for href in ('#missing-page','https://example.com','javascript:alert(1)'):
            document=deepcopy(source)
            document['sections'][0]['blocks'][-1]['items'][0]['href']=href
            with self.subTest(href=href),self.assertRaisesRegex(ValueError,'ERR_CORE_METHOD'):
                compile_method(document)
        repeated=deepcopy(source)
        repeated['sections'][0]['blocks'][-1]['items'].append(deepcopy(block['items'][0]))
        with self.assertRaisesRegex(ValueError,'duplicate reading link'):
            compile_method(repeated)

    def test_page_uses_the_canonical_method_and_current_glossary(self):
        ui=hydrate_core_method(read(ROOT/'config/application.yaml'))
        self.assertEqual(ui['essential']['core_method'],compile_method(self.document))
        glossary=read(ROOT/'source/glossaire.yaml')
        validate_glossary_literals(ui['essential']['core_method'],glossary,path=METHOD_SOURCE)
        glossary['notions']['core_system']['libelle']='Noyau métier'
        resolved=resolve_text_tree(ui['essential']['core_method'],glossary)
        self.assertIn('Noyau métier',str(resolved))
        self.assertNotIn('{{notion.core_system}}',str(resolved))
        self.assertIn('{{notion.core_system}}',str(self.document))
        malformed=read(ROOT/'config/application.yaml')
        malformed['essential']['core_method']['source']='other-method.yaml'
        with self.assertRaisesRegex(ValueError,'ERR_CORE_METHOD'):hydrate_core_method(malformed)

    def test_release_freezes_method_and_presentation_is_not_an_economic_input(self):
        study=study_copy()
        economics=deepcopy(study.baseline)
        released=Study.from_release(candidate(study))
        reference=deepcopy(released.ui['essential']['core_method'])
        study.ui['essential']['core_method']['principle']['text']='Modified presentation.'
        self.assertEqual(study.simulate(study.parameters),economics)
        with patch.object(Path,'read_bytes',side_effect=AssertionError('unexpected draft read')):
            self.assertEqual(released.bootstrap(essential=True)['ui']['essential']['core_method'],reference)
            self.assertEqual(released.simulate(released.parameters),economics)

    def test_net_document_is_separate_and_cannot_embed_unvalidated_budgets(self):
        document=read(ROOT/NET_METHOD_SOURCE)
        hydrated=hydrate_net_method(read(ROOT/'config/application.yaml'))
        self.assertEqual(hydrated['essential']['net_method'],compile_net_method(document))
        document['budget']=1000
        with self.assertRaisesRegex(ValueError,'ERR_NET_METHOD'):
            compile_net_method(document)
        ui=read(ROOT/'config/application.yaml')
        ui['essential']['net_method']['source']=METHOD_SOURCE
        with self.assertRaisesRegex(ValueError,'ERR_NET_METHOD'):
            hydrate_net_method(ui)

    def test_levers_document_requires_its_owner_and_hands_off_to_the_economic_study(self):
        document=read(ROOT/LEVERS_METHOD_SOURCE)
        ui=read(ROOT/'config/application.yaml')
        value=hydrate_levers_method(ui)['essential']['levers_method']
        self.assertEqual(value,compile_levers_method(document))
        self.assertEqual(value['next']['href'],'#etude-marche')
        self.assertNotIn('document',ui['essential']['levers_method'])
        for field,value in (('id','net-calculation'),('budget',1000)):
            invalid=deepcopy(document)
            invalid[field]=value
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'ERR_LEVERS_METHOD'):
                compile_levers_method(invalid)
        invalid=deepcopy(document)
        invalid['next']['href']='#parametres'
        with self.assertRaisesRegex(ValueError,'ERR_LEVERS_METHOD'):
            compile_levers_method(invalid)
        ui['essential']['levers_method']['source']=NET_METHOD_SOURCE
        with self.assertRaisesRegex(ValueError,'ERR_LEVERS_METHOD'):
            hydrate_levers_method(ui)


if __name__=='__main__':unittest.main()
