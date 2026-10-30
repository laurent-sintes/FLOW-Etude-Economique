"""Static publication keeps the same calculations, evidence and parameter contract."""
from copy import deepcopy
import gzip
import hashlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.parse import quote, unquote
import unittest
from zipfile import ZipFile

from build_pages import build_pages, normalize_base
from document_excerpt import document_excerpt
from pages_runtime import load_runtime
from study_snapshot import candidate, encode, ENGINE_FILES
from test_support import study_copy
from validate_stacks import ROOT


class PagesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = study_copy()
        cls.bundle = candidate(cls.study)
        cls.runtime = load_runtime(encode(cls.bundle).decode('utf-8'), cls.study.version, cls.study.simulation_contract())

    def request(self, path, body=None):
        return json.loads(self.runtime.request(path, '' if body is None else json.dumps(body)))

    def test_browser_adapter_reuses_engine_without_sources_and_preserves_inputs(self):
        before = deepcopy(self.study.parameters)
        alternate = deepcopy(before)
        alternate['options']['java-spring']['build'] *= 1.1
        alternate['options']['microsoft']['integration_mois'] += 1
        alternate['common']['inflation_cloud'] += 0.005
        for parameters in (before, alternate):
            expected = self.study.simulate(parameters, self.study.version)
            with patch.object(Path, 'read_bytes', side_effect=AssertionError('simulation rereads disk')):
                actual = self.request('/api/simulate', dict(parameters=parameters, model_version=self.study.version))
            self.assertEqual(actual, dict(status=200, data=expected))
        self.assertEqual(self.runtime.study.parameters, before)
        self.assertEqual(self.runtime.study.baseline, self.study.baseline)
        self.assertEqual(self.runtime.study.edition['mode'], 'current')

    def test_parameter_and_version_errors_remain_explicit(self):
        body = dict(parameters=deepcopy(self.study.parameters), model_version='old')
        self.assertEqual(self.request('/api/simulate', body)['data']['error'], 'version')
        body['model_version'] = self.study.version
        body['parameters']['common']['unknown'] = 1
        self.assertEqual(self.request('/api/simulate', body)['data']['error'], 'unknown_parameter')
        self.assertEqual(json.loads(self.runtime.request('/api/simulate', '{'))['status'], 400)
        self.assertEqual(self.request('https://example.test/api/simulate', body)['status'], 404)
        broken = deepcopy(self.bundle)
        broken['payload']['version'] = 'edited'
        with self.assertRaises(ValueError):
            load_runtime(json.dumps(broken), self.study.version, self.study.simulation_contract())
        with self.assertRaises(ValueError):
            load_runtime(encode(self.bundle).decode(), 'old', self.study.simulation_contract())

    def test_document_fragments_use_the_same_frozen_evidence(self):
        for reference in ('source/calibration-couts.yaml#pilotage', 'source/offres-synvance.md'):
            source, _, fragment = reference.partition('#')
            suffix = Path(source).suffix
            expected = dict(path=source, format=suffix, **document_excerpt(
                self.study.document_bytes(source).decode('utf-8-sig'), suffix, fragment))
            with patch.object(Path, 'read_bytes', side_effect=AssertionError('document rereads disk')):
                actual = self.request('/api/document?path=' + quote(reference))
            self.assertEqual(actual, dict(status=200, data=expected))
        for source in ('../AGENTS.md', 'sources/../AGENTS.md', 'C:/Windows/win.ini', 'source/unknown.yaml'):
            self.assertEqual(self.request('/api/document?path=' + quote(source))['status'], 404)

    def test_static_delivery_matches_loaded_data_and_original_proof_bytes(self):
        before = deepcopy(self.study.bootstrap(essential=True))
        with TemporaryDirectory(prefix='pages-test-', dir=ROOT / 'tmp') as temporary:
            output = Path(temporary)
            (output / 'index.html').write_text('<html><head><title></title></head><body><div id="root"></div></body></html>', encoding='utf-8')
            (output / 'assets').mkdir()
            (output / 'assets' / 'app.js').write_text('export const compiled=true;', encoding='utf-8')
            manifest = build_pages(output, '/FLOW-Etude-Economique/', self.study)
            self.assertEqual(manifest, json.loads((output / 'site-manifest.json').read_text(encoding='utf-8')))
            self.assertEqual(manifest['simulation_contract'], self.study.simulation_contract())
            self.assertEqual(manifest['model_version'], self.study.version)
            exported = json.loads((output / manifest['bootstrap']).read_text(encoding='utf-8'))
            for key in ('baseline', 'content', 'glossary', 'model_version', 'simulation_contract'):
                self.assertEqual(exported[key], json.loads(encode(before[key])))
            self.assertEqual(exported['ui']['parameters'], before['ui']['parameters'])
            self.assertTrue(exported['ui']['brand_assets']['flow'].startswith('/FLOW-Etude-Economique/'))
            self.assertEqual(self.study.bootstrap(essential=True), before)
            for url in [manifest['bootstrap'], *manifest['routes'].values(), manifest['python']['archive'], manifest['python']['model']]:
                self.assertIn(manifest['server_revision'], url)
                self.assertTrue((output / url).is_file())
            for key in ('archive', 'model'):
                raw = (output / manifest['python'][key]).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), manifest['python'][key + '_sha256'])
            frozen = json.loads(gzip.decompress((output / manifest['python']['model']).read_bytes()))
            self.assertEqual(frozen['payload'], json.loads(encode(self.bundle['payload'])))
            with ZipFile(io.BytesIO((output / manifest['python']['archive']).read_bytes())) as archive:
                for name in (*ENGINE_FILES, 'pages_runtime.py', 'document_excerpt.py'):
                    self.assertEqual(archive.read('tools/' + name), (ROOT / 'tools' / name).read_bytes())
            self.assertEqual(set(manifest['documents']), set(self.bundle['payload']['documents']))
            for source, record in manifest['documents'].items():
                raw = (output / unquote(record['url'])).read_bytes()
                self.assertEqual(raw, self.study.document_bytes(source))
                self.assertEqual(hashlib.sha256(raw).hexdigest(), record['sha256'])
            capabilities = json.loads((output / manifest['routes']['/api/capability']).read_text(encoding='utf-8'))
            row = self.study.content['business_map']['rows'][0]
            self.assertEqual(capabilities[row['id']], capabilities[row['capacite_id']])
            self.assertIn('static_site', (output / 'index.html').read_text(encoding='utf-8'))
            self.assertTrue((output / '.nojekyll').is_file())

    def test_builder_rejects_unsafe_output_and_bases(self):
        for base in ('https://example.test/', '//example.test/', '/a/../b', '/a?x=1', '/a\\b'):
            with self.assertRaises(ValueError):
                normalize_base(base)
        self.assertEqual(normalize_base('/project'), '/project/')
        with self.assertRaises(ValueError):
            build_pages(ROOT, '/', self.study)


if __name__ == '__main__':
    unittest.main()
