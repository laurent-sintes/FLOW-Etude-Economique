"""Release isolation, pure simulations, transport and approved numeric parity."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from validate_stacks import ROOT, read, UniqueKeyLoader
from model_context import model_session
from test_support import study_copy
from study_snapshot import candidate, publish, load, pack_content, unpack_content
from study_app import Study

class RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study=study_copy()

    def test_all_horizons_conserve_the_same_funding(self):
        for option in self.study.baseline['options']:
            for horizon in option['horizons']:
                total=round(sum(a['total'] for a in option['annual'][:horizon['years']]),2)
                self.assertEqual(total,horizon['totals']['total'])
                self.assertEqual(total,round(sum(horizon['responsibilities'].values()),2))

    def test_simulation_has_no_file_access(self):
        with patch.object(Path,'read_bytes',side_effect=AssertionError('disk access')), \
             patch.object(Path,'read_text',side_effect=AssertionError('disk access')):
            self.assertEqual(self.study.baseline,self.study.simulate(self.study.parameters))

    def test_source_cache_is_scoped_and_copies_are_isolated(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as folder:
            path=Path(folder)/'value.yaml';path.write_text('value: 1')
            with model_session():
                first=read(path);first['value']=99
                self.assertEqual(read(path)['value'],1)
            path.write_text('value: 2')
            with model_session():self.assertEqual(read(path)['value'],2)
            with self.assertRaises(ValueError):
                with model_session():
                    read(path);path.write_text('value: 3')

    def test_complexity_validation_is_shared_only_within_one_load(self):
        from capability_catalog import catalog as validate
        with patch('study_app.catalog',wraps=validate) as check:
            with model_session():
                a=Study._complexity_grid();a['rows'].clear()
                self.assertTrue(Study._complexity_grid()['rows'])
                self.assertEqual(check.call_count,1)
            with model_session():Study._complexity_grid()
            self.assertEqual(check.call_count,2)

    def test_duplicate_yaml_keys_still_fail(self):
        import yaml
        with self.assertRaises(ValueError):yaml.load('amount: 1\namount: 2',Loader=UniqueKeyLoader)

    def test_canonical_transport_preserves_every_business_row(self):
        packed=pack_content(self.study.content);restored=unpack_content(packed)
        self.assertEqual(restored['business_map'],self.study.content['business_map'])
        self.assertIs(restored['complexity']['rows'],restored['business_map']['rows'])
        self.assertNotIn('rows',packed['complexity'])
        self.assertLess(len(json.dumps(packed)),len(json.dumps(self.study.content))*.5)

    def test_release_survives_draft_edits_and_detects_corruption(self):
        bundle=candidate(self.study)
        released=Study.from_release(bundle)
        self.assertEqual(released.simulate(released.parameters),self.study.baseline)
        original=deepcopy(released.parameters)
        self.study.parameters['common']['bonus_continuite_pct']+=1
        try:self.assertEqual(released.parameters,original)
        finally:self.study.parameters=original
        with patch.object(Path,'read_bytes',side_effect=AssertionError('draft read')):
            self.assertEqual(released.simulate(original),self.study.baseline)
            self.assertIn(b'hebergement_build',released.document_bytes('source/modele-composable.yaml'))
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as folder:
            path=Path(folder)/'current.json';publish(bundle,path);old=path.read_bytes()
            invalid=deepcopy(bundle);invalid['payload']['parameters']['common']['bonus_continuite_pct']+=1
            with self.assertRaises(ValueError):publish(invalid,path)
            self.assertEqual(path.read_bytes(),old)
            self.assertEqual(load(path)['sha256'],bundle['sha256'])
