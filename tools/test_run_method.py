"""Run methodology has a frozen owner, independent of budget calculations."""
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

from content_model import resolve_text_tree, validate_glossary_literals
from core_method import RUN_METHOD_SOURCE, compile_run_method, hydrate_run_method
from validate_stacks import ROOT, read
from test_support import study_copy
from study_app import Study
from study_snapshot import candidate


class RunMethodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document=read(ROOT/RUN_METHOD_SOURCE)

    def test_canonical_document_is_isolated_and_uses_the_current_vocabulary(self):
        source=deepcopy(self.document)
        ui=read(ROOT/'config/application.yaml')
        hydrated=hydrate_run_method(ui)
        self.assertEqual(hydrated['essential']['run_method'],compile_run_method(source))
        self.assertEqual(ui['essential']['run_method'],{'source':RUN_METHOD_SOURCE})
        glossary=read(ROOT/'source/glossaire.yaml')
        validate_glossary_literals(source,glossary,path=RUN_METHOD_SOURCE)
        glossary['notions']['run_activities']['libelle']='Service courant'
        resolved=resolve_text_tree(hydrated['essential']['run_method'],glossary)
        self.assertIn('Service courant',str(resolved))
        hydrated['essential']['run_method']['sections'].clear()
        self.assertTrue(self.document['sections'])
        self.assertEqual(self.document,source)

    def test_schema_rejects_inconsistent_content_and_embedded_economic_results(self):
        broken=[]
        item=deepcopy(self.document);item['id']='net-calculation';broken.append(item)
        item=deepcopy(self.document);item['sections'].append(deepcopy(item['sections'][0]));broken.append(item)
        item=deepcopy(self.document);item['budget_eur']=1000;broken.append(item)
        item=deepcopy(self.document);item['examples']=[{}];broken.append(item)
        item=deepcopy(self.document)
        item['sections'][0]['blocks'].append(dict(kind='table',caption='Test table',columns=['A','B'],rows=[['A']]))
        broken.append(item)
        item=deepcopy(self.document);item['next']['href']='#missing-page';broken.append(item)
        for index,document in enumerate(broken):
            with self.subTest(index=index),self.assertRaisesRegex(ValueError,'ERR_RUN_METHOD'):
                compile_run_method(document)
        for reference in ({'source':'source/methode-calcul-net.yaml'},
                          {'source':RUN_METHOD_SOURCE,'text':'Local override.'},None):
            ui=read(ROOT/'config/application.yaml')
            ui['essential']['run_method']=reference
            with self.subTest(reference=reference),self.assertRaisesRegex(ValueError,'ERR_RUN_METHOD'):
                hydrate_run_method(ui)

    def test_method_links_follow_the_public_reading_order(self):
        study=study_copy()
        essential=study.ui['essential']
        nav={item['id']:item for item in essential['nav']}
        order=next(group['items'] for group in essential['nav_groups'] if 'calcul-run' in group['items'])
        self.assertEqual(order[order.index('calcul-net')+1],'calcul-run')
        for key in ('net_method','run_method'):
            target=essential[key]['next']['href'].removeprefix('#')
            self.assertIn(target,nav)
            self.assertIn(target,essential['pages'])
        self.assertEqual(essential['net_method']['next']['href'],'#calcul-run')
        self.assertEqual(essential['pages']['calcul-run']['title'],nav['calcul-run']['label'])

    def test_release_freezes_method_without_changing_costs_or_reading_sources_again(self):
        study=study_copy()
        baseline=deepcopy(study.baseline)
        bundle=candidate(study)
        self.assertIn(RUN_METHOD_SOURCE,bundle['payload']['documents'])
        self.assertIn(str((ROOT/RUN_METHOD_SOURCE).resolve()),study.source_digests)
        released=Study.from_release(bundle)
        frozen=deepcopy(released.ui['essential']['run_method'])
        study.ui['essential']['run_method']['notice']['text']='Changed presentation.'
        self.assertEqual(study.simulate(study.parameters),baseline)
        with patch.object(Path,'read_bytes',side_effect=AssertionError('unexpected current-source read')):
            self.assertEqual(released.bootstrap(essential=True)['ui']['essential']['run_method'],frozen)
            self.assertEqual(released.simulate(released.parameters),baseline)


if __name__=='__main__':unittest.main()
