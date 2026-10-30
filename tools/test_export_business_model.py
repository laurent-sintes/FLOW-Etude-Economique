"""Contracts for the one-file model download and change detection."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
import yaml
from export_business_model import compose, encode, write_if_changed, METAMODEL
from model_context import model_session
from study_app import Study
from validate_stacks import ROOT


class ExportBusinessModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with model_session() as snapshot:
            Study()
            cls.documents = deepcopy(snapshot.documents)
            cls.digests = dict(snapshot.digests)
        cls.bundle = compose(cls.documents, cls.digests)

    def test_active_data_and_canonical_metamodel_are_preserved(self):
        result = yaml.load(encode(self.bundle), Loader=getattr(yaml, 'CSafeLoader', yaml.SafeLoader))
        self.assertEqual(result['metamodel'], self.documents[ROOT / METAMODEL])
        for path, value in result['model'].items():
            self.assertEqual(value, self.documents[ROOT / path])
        self.assertIn('source/estimations-core-retenues.yaml', result['model'])
        self.assertIn('sources/cartographie-scm-2026-10-24.yaml', result['model'])
        self.assertTrue(any(p.startswith('audits/') and p.endswith('.json') for p in result['evidence']))
        self.assertNotIn('source/complexite-metier.yaml', result['model'])
        self.assertNotIn('source/recalibration-metier.yaml', result['model'])
        self.assertNotIn('source/couts-15-ans.yaml', result['model'])
        self.assertNotIn('config/application.yaml', result['model'])

    def test_model_and_metamodel_changes_invalidate_content(self):
        for relative in (METAMODEL, 'source/estimations-core-retenues.yaml'):
            documents = deepcopy(self.documents)
            documents[ROOT / relative]['_test_change'] = True
            digests = {**self.digests, ROOT / relative: 'changed'}
            changed = compose(documents, digests)
            self.assertNotEqual(encode(changed), encode(self.bundle))
            self.assertNotEqual(changed['source_fingerprint'], self.bundle['source_fingerprint'])

    def test_no_rewrite_for_identical_content_and_repair_corruption(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'model.yaml'
            raw = encode(self.bundle)
            self.assertTrue(write_if_changed(path, raw))
            before = path.stat().st_mtime_ns
            self.assertFalse(write_if_changed(path, raw))
            self.assertEqual(path.stat().st_mtime_ns, before)
            path.write_bytes(b'corrupt')
            self.assertTrue(write_if_changed(path, raw))
            self.assertEqual(path.read_bytes(), raw)

    def test_dependency_order_does_not_change_output(self):
        reverse = dict(reversed(list(self.documents.items())))
        self.assertEqual(encode(compose(reverse, self.digests)), encode(self.bundle))

    def test_export_cache_skips_loading_but_rebuilds_for_dependencies_and_corruption(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        import export_business_model as exporter
        from validate_stacks import read
        import hashlib
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as folder:
            folder=Path(folder); output=folder/'model.yaml'; marker=folder/'dependency.txt'
            marker.write_text('one',encoding='utf-8')
            def load():
                read(ROOT/METAMODEL)
                read(ROOT/'source/estimations-core-retenues.yaml')
                return SimpleNamespace(files={marker.relative_to(ROOT).as_posix()})
            with patch.object(exporter,'Study',side_effect=load) as build:
                first=exporter.export(output)
                self.assertFalse(first['cache_hit'])
                before=output.stat().st_mtime_ns
                second=exporter.export(output)
                self.assertTrue(second['cache_hit']); self.assertEqual(build.call_count,1)
                self.assertEqual(output.stat().st_mtime_ns,before)
                stale=SimpleNamespace(source_digests={str(ROOT/METAMODEL):'0'*64})
                with self.assertRaisesRegex(ValueError,'Source changed'):
                    exporter.export(output,study=stale)
                marker.write_text('two',encoding='utf-8')
                self.assertFalse(exporter.export(output)['cache_hit'])
                output.write_bytes(b'corrupt')
                repaired=exporter.export(output)
                self.assertFalse(repaired['cache_hit'])
                self.assertEqual(hashlib.sha256(output.read_bytes()).hexdigest(),first['sha256'])
                signature=exporter.generator_signature()
                with patch.object(exporter,'generator_signature',return_value={**signature,'test_new_engine':True}):
                    self.assertFalse(exporter.export(output)['cache_hit'])
                Path(str(output)+'.cache.json').write_text('{broken',encoding='utf-8')
                self.assertFalse(exporter.export(output)['cache_hit'])
                output.unlink()
                self.assertFalse(exporter.export(output)['cache_hit'])
