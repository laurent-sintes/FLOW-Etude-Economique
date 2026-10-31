"""Static preparation cache and a web server that only serves files."""
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from prepare_static_app import prepare
from validate_stacks import ROOT


class StaticApplicationTests(unittest.TestCase):
    def test_cache_detects_source_changes_missing_files_and_corruption(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as folder:
            root=Path(folder)
            output=root/'app/dist'
            output.mkdir(parents=True)
            fingerprint={'a':'1'}
            calls=[]
            def builder(output,base):
                calls.append(base)
                (output/'index.html').write_text('static client')
                manifest={'id':'flow-study','server_revision':'test-revision','base':base}
                (output/'site-manifest.json').write_text(json.dumps(manifest))
                return manifest
            with patch('prepare_static_app.inputs',side_effect=lambda root:dict(fingerprint)):
                self.assertFalse(prepare(output,root=root,builder=builder)['cached'])
                self.assertTrue(prepare(output,root=root,builder=builder)['cached'])
                fingerprint['a']='2'
                self.assertFalse(prepare(output,root=root,builder=builder)['cached'])
                (output/'index.html').write_text('corrupted')
                self.assertFalse(prepare(output,root=root,builder=builder)['cached'])
                (output/'site-manifest.json').unlink()
                self.assertFalse(prepare(output,root=root,builder=builder)['cached'])
                self.assertEqual(len(calls),4)
            with self.assertRaises(ValueError):prepare(root/'outside',root=root,builder=builder)

    def test_concurrent_source_change_cannot_be_certified_as_cached_build(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as folder:
            root=Path(folder)
            (root/'app/dist').mkdir(parents=True)
            with patch('prepare_static_app.inputs',side_effect=[{'a':'1'},{'a':'2'}]):
                with self.assertRaisesRegex(ValueError,'Sources changed'):
                    prepare(root=root,builder=lambda output,base:{'server_revision':'r'})
            self.assertFalse(list((root/'tmp/static-app').glob('*.json')))

    def test_static_http_server_has_no_api_or_simulation_endpoint(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as folder:
            (Path(folder)/'index.html').write_text('browser-only')
            handler=partial(SimpleHTTPRequestHandler,directory=folder)
            server=ThreadingHTTPServer(('127.0.0.1',0),handler)
            thread=Thread(target=server.serve_forever,daemon=True)
            thread.start()
            url=f'http://127.0.0.1:{server.server_port}'
            try:
                with urlopen(url) as response:self.assertEqual(response.read(),b'browser-only')
                with self.assertRaises(HTTPError) as error:urlopen(url+'/api/health')
                self.assertEqual(error.exception.code,404)
                with self.assertRaises(HTTPError) as error:urlopen(Request(url+'/api/simulate',data=b'{}'))
                self.assertEqual(error.exception.code,501)
            finally:
                server.shutdown();server.server_close();thread.join()
