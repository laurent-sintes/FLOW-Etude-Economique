"""HTTP checks isolated from economic and editorial tests."""
from test_support import study_copy
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import json,unittest,gzip
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory
from serve_study_app import make_handler,load_current_study

class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study=study_copy()
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(cls.study))
        cls.thread=Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.url=f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def setUp(self):self.p=self.study.parameters

    def test_http_api_and_origin(self):
        with urlopen(self.url+'/api/health') as r:self.assertEqual(json.load(r)['version'],self.study.version)
        body=json.dumps(dict(parameters=self.p,model_version=self.study.version)).encode()
        req=Request(self.url+'/api/simulate',data=body,headers={'Content-Type':'application/json'})
        with urlopen(req) as r:self.assertEqual(json.load(r)['options'],self.study.baseline['options'])
        req=Request(self.url+'/api/simulate',data=body,headers={'Content-Type':'application/json','Origin':'https://external.invalid'})
        with self.assertRaises(HTTPError) as e:urlopen(req)
        self.assertEqual(e.exception.code,403)

    def test_current_loading_freezes_sources_without_reading_saved_snapshot(self):
        with patch('study_snapshot.load',side_effect=AssertionError('saved snapshot must not be read')):
            study=load_current_study()
        self.assertEqual(study.edition['mode'],'current')
        self.assertEqual(study.baseline['options'],self.study.baseline['options'])
        with patch.object(Path,'read_bytes',side_effect=AssertionError('unexpected source reread')):
            self.assertEqual(study.simulate(study.parameters),study.baseline)
            self.assertIn(b'hebergement_build',study.document_bytes('source/modele-composable.yaml'))

    def test_health_detects_changed_sources_without_changing_loaded_model(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/'source.yaml';path.write_text('value: 1',encoding='utf-8')
            study=study_copy();study.source_digests[str(path)]='observed-by-loader'
            server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(study))
            thread=Thread(target=server.serve_forever,daemon=True);thread.start()
            url=f'http://127.0.0.1:{server.server_port}'
            try:
                with urlopen(url+'/api/health') as response:before=json.load(response)
                self.assertEqual(before['mode'],'current');self.assertTrue(before['sources_current'])
                path.write_text('value: 200',encoding='utf-8')
                with urlopen(url+'/api/health') as response:after=json.load(response)
                self.assertFalse(after['sources_current'])
                self.assertEqual(after['server_revision'],before['server_revision'])
                self.assertEqual(study.simulate(study.parameters),study.baseline)
            finally:
                server.shutdown();server.server_close();thread.join()

    def test_light_bootstrap_compression_and_legacy_content(self):
        def get(path,encoding='identity'):
            with urlopen(Request(self.url+path,headers={'Accept-Encoding':encoding})) as r:
                raw=r.read();headers=r.headers
                return raw,headers
        light,h=get('/api/bootstrap?view=essential')
        packed,z=get('/api/bootstrap?view=essential','gzip')
        self.assertEqual(gzip.decompress(packed),light)
        self.assertEqual(z['Content-Encoding'],'gzip')
        self.assertEqual(z['Vary'],'Accept-Encoding')
        self.assertEqual(int(z['Content-Length']),len(packed))
        refused,h=get('/api/bootstrap?view=essential','gzip;q=0, *;q=1')
        self.assertIsNone(h.get('Content-Encoding'));self.assertEqual(refused,light)
        self.assertLess(len(packed),len(light)/2)
        small=json.loads(light);full=json.loads(get('/api/bootstrap')[0])
        self.assertEqual(set(small['content']),{'complexity','framework','market_method','core_evaluation','synvance_reference','delivery_method','delivery_readiness'})
        self.assertEqual(len(small['content']['complexity']['rows']),88)
        self.assertEqual(len(small['content']['core_evaluation']),5)
        for key in ('delivery_method','delivery_readiness'):
            self.assertEqual(small['content'][key],full['content'][key])
        self.assertEqual([row['capability_id'] for row in small['content']['delivery_readiness']['scope']['rows']],
                         [row['capacite_id'] for row in small['content']['complexity']['rows']])
        for key in small:
            if key!='content':self.assertEqual(small[key],full[key])
        self.assertLess(len(light),1_100_000)
        self.assertLess(len(light),len(get('/api/bootstrap')[0])/8)
        self.assertIn('business_map',full['content'])

    def test_capability_proof_uses_loaded_model_and_checks_version(self):
        from urllib.parse import urlencode
        row=self.study.content['business_map']['rows'][0]
        for identifier in (row['id'],row['capacite_id']):
            url=self.url+'/api/capability?'+urlencode(dict(id=identifier,model_version=self.study.version))
            with urlopen(url) as r:proof=json.load(r)
            self.assertEqual(proof['title'],row['capacite']['nom'])
            self.assertEqual(proof['text'],row['capacite']['definition']+' '+row['frontiere'])
            self.assertEqual(proof['source'],self.study.content['business_map']['source']['path'])
        with self.assertRaises(HTTPError) as error:urlopen(self.url+'/api/capability?id=x&model_version=old')
        self.assertEqual(error.exception.code,409)

    def test_market_build_is_a_versioned_documentary_read(self):
        from urllib.parse import urlencode
        url=self.url+'/api/market-build?'+urlencode(dict(model_version=self.study.version))
        with urlopen(url) as response:record=json.load(response)
        build=self.study.content['market']['reperes_build_core']
        self.assertEqual(record,{key:build[key] for key in ('etude_oss','cadre_comparaison','fiches_produit','candidats_a_etudier')})
        self.assertEqual(record['etude_oss']['nature'],'diagnostic_reconstruction_oss')
        self.assertEqual(set(record['fiches_produit']),
                         {'erpnext','odoo-community','tryton','axelor-open-suite','microsoft','sap'})
        self.assertNotIn('references',record)
        with self.assertRaises(HTTPError) as error:urlopen(self.url+'/api/market-build?model_version=old')
        self.assertEqual(error.exception.code,409)

    def test_market_references_use_loaded_content_without_expanding_bootstrap(self):
        from urllib.parse import urlencode
        from market_reading import build_market_reading
        from unittest.mock import patch
        url=self.url+'/api/market-references?'+urlencode(dict(model_version=self.study.version))
        expected=build_market_reading(self.study.content['market'])
        with patch.object(Path,'read_bytes',side_effect=AssertionError('unexpected source read')):
            with urlopen(url) as response:record=json.load(response)
            with urlopen(Request(url,headers={'Accept-Encoding':'gzip'})) as response:
                self.assertEqual(json.loads(gzip.decompress(response.read())),record)
        self.assertEqual(record,expected)
        self.assertEqual(len(record['projects']),len(self.study.content['market']['references']))
        self.assertNotIn('references',self.study.bootstrap(essential=True)['content']['market_method'])
        with self.assertRaises(HTTPError) as error:urlopen(self.url+'/api/market-references?model_version=old')
        self.assertEqual(error.exception.code,409)

    def test_economic_reading_uses_frozen_reference_and_checks_version(self):
        from urllib.parse import urlencode
        from unittest.mock import patch
        url=self.url+'/api/economic-evaluations?'+urlencode(dict(model_version=self.study.version))
        with patch.object(Path,'read_bytes',side_effect=AssertionError('unexpected source read')):
            with urlopen(url) as response:record=json.load(response)
            with urlopen(Request(url,headers={'Accept-Encoding':'gzip'})) as response:
                self.assertEqual(json.loads(gzip.decompress(response.read())),record)
        self.assertEqual(record,self.study.content['economic_evaluations'])
        self.assertEqual([row['stack'] for row in record['options']],[row['stack'] for row in self.study.baseline['options']])
        self.assertNotIn('economic_evaluations',self.study.bootstrap(essential=True)['content'])
        for version in ('', 'old'):
            with self.assertRaises(HTTPError) as error:urlopen(self.url+'/api/economic-evaluations?model_version='+version)
            self.assertEqual(error.exception.code,409)

    def test_compressed_proof_and_simulation_retain_exact_content(self):
        from urllib.parse import quote
        path='/api/document?path='+quote('source/modele-composable.yaml#definitions')
        with urlopen(self.url+path) as r:proof=json.load(r)
        with urlopen(Request(self.url+path,headers={'Accept-Encoding':'gzip'})) as r:
            self.assertEqual(json.loads(gzip.decompress(r.read())),proof)
        req=Request(self.url+'/api/simulate',data=json.dumps(dict(parameters=self.p,model_version=self.study.version)).encode(),headers={'Content-Type':'application/json','Accept-Encoding':'gzip'})
        with urlopen(req) as r:self.assertEqual(json.loads(gzip.decompress(r.read())),self.study.baseline)

    def test_server_keeps_client_assets_paired_with_loaded_release(self):
        with TemporaryDirectory() as folder:
            dist=Path(folder);(dist/'assets').mkdir()
            (dist/'index.html').write_text('<html><head><title></title></head><body><div id="root"></div><script src="/assets/app.js"></script></body></html>',encoding='utf-8')
            (dist/'assets/app.js').write_text('old-client',encoding='utf-8')
            server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(self.study,static_root=dist))
            thread=Thread(target=server.serve_forever,daemon=True);thread.start()
            url=f'http://127.0.0.1:{server.server_port}'
            try:
                with urlopen(url+'/api/health') as response:revision=json.load(response)['server_revision']
                (dist/'index.html').write_text('<html>new-client</html>',encoding='utf-8')
                (dist/'assets/app.js').unlink()
                with urlopen(url+'/') as response:
                    self.assertTrue(response.headers['Content-Type'].startswith('text/html'))
                    html=response.read().decode('utf-8')
                with urlopen(url+'/assets/app.js') as response:script=response.read().decode('utf-8')
                with urlopen(url+'/api/health') as response:self.assertEqual(json.load(response)['server_revision'],revision)
                self.assertIn('old-client',script)
                self.assertIn('id="app-config"',html)
                self.assertIn(self.study.ui['labels']['retry'],html)
                self.assertNotIn('new-client',html)
            finally:
                server.shutdown();server.server_close();thread.join()

    def test_yaml_download_compression_preserves_original_bytes(self):
        with TemporaryDirectory() as folder:
            root=Path(folder);(root/'index.html').write_text('<div id="root"></div>',encoding='utf-8')
            (root/'exports').mkdir()
            raw=('modèle: données métier\n'*2000).encode()
            (root/'exports/model.yaml').write_bytes(raw)
            server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(self.study,static_root=root))
            thread=Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                url=f'http://127.0.0.1:{server.server_port}/exports/model.yaml'
                for encoding in ('gzip','identity','gzip;q=0'):
                    with urlopen(Request(url,headers={'Accept-Encoding':encoding})) as response:
                        body=response.read()
                        self.assertIn('application/yaml',response.headers['Content-Type'])
                        if encoding=='gzip':
                            self.assertEqual(response.headers['Content-Encoding'],'gzip')
                            self.assertEqual(gzip.decompress(body),raw)
                            self.assertLess(len(body),len(raw))
                        else:
                            self.assertIsNone(response.headers.get('Content-Encoding'))
                            self.assertEqual(body,raw)
            finally:
                server.shutdown();server.server_close();thread.join()
