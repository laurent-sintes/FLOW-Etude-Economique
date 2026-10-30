"""HTTP revision contract: reload signals must match the page actually served."""
import json
import re
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen
from serve_study_app import make_handler
from validate_stacks import ROOT


class RevisionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='server-revision-',dir=ROOT/'tmp')
        self.root=Path(self.tmp.name)
        self.index=self.root/'app/dist/index.html'
        self.index.parent.mkdir(parents=True)
        self.index.write_text('<head><title></title></head><script src="/assets/a.js"></script>')
        self.root_patch=patch('serve_study_app.ROOT',self.root);self.root_patch.start()
        self.study=SimpleNamespace(ui={'id':'flow-study','document_title':'FLOW','reload_storage_key':'flow-session','labels':{'loading':'Loading','retry':'Retry'},'errors':{'network':'Network','render':'Render','reset_session':'Reset session'}},version='model-a',bootstrap=lambda **kw:{'model_version':'model-a'})
        self.study.files=set();self.study.edition={'mode':'current'}
        self.start()

    def start(self):
        self.server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(self.study))
        self.thread=Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.url=f'http://127.0.0.1:{self.server.server_port}'

    def stop(self):
        self.server.shutdown();self.server.server_close();self.thread.join()

    def tearDown(self):
        self.stop();self.root_patch.stop();self.tmp.cleanup()

    def get(self,path='/api/health'):
        with urlopen(self.url+path) as r:
            self.assertEqual(r.headers['Cache-Control'],'no-store')
            return json.load(r)

    def test_document_bootstrap_and_poll_share_revision(self):
        expected=self.get()['server_revision']
        self.assertEqual(expected,self.get()['server_revision'])
        self.assertEqual(expected,self.get('/api/bootstrap')['server_revision'])
        with urlopen(self.url) as r: page=r.read().decode()
        config=json.loads(re.search(r'id="app-config" type="application/json">(.*?)</script>',page)[1])
        self.assertEqual(expected,config['server_revision'])

    def test_restart_signals_change_without_changing_model(self):
        old=self.get();self.stop();self.start();new=self.get()
        self.assertNotEqual(old['server_revision'],new['server_revision'])
        self.assertEqual(old['version'],new['version'])

    def test_rebuild_is_not_served_before_restart(self):
        old=self.get()['server_revision']
        self.index.write_text('<head><title></title></head><script src="/assets/b.js"></script>')
        self.assertEqual(old,self.get()['server_revision'])
        with urlopen(self.url) as response:self.assertIn('/assets/a.js',response.read().decode())
        self.stop();self.start()
        self.assertNotEqual(old,self.get()['server_revision'])

    def test_partial_build_keeps_serving_pinned_client(self):
        old=self.get()['server_revision']
        original=self.index.read_bytes();self.index.unlink()
        self.assertEqual(old,self.get()['server_revision'])
        with urlopen(self.url) as response:self.assertIn('/assets/a.js',response.read().decode())
        self.index.write_bytes(original)
        self.assertEqual(old,self.get()['server_revision'])


if __name__=='__main__':unittest.main(verbosity=2)
