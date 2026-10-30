"""Regression cases that must invalidate a falsely complete or calibrated grid."""
from copy import deepcopy
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from jsonschema import ValidationError
import validate_complexity_grid as grid_validation
from validate_complexity_grid import validate
from validate_stacks import ROOT,read

class GridTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.grid=read(ROOT/'source/grille-complexite.yaml')
    def test_reference_capture(self):validate()
    def test_live_capture_when_external_source_is_available(self):
        snapshot=read(ROOT/self.grid['dependances']['cartographie'])
        native=Path(snapshot['provenance']['fichier'])
        if not native.is_file():
            self.skipTest('Live cartography check requires the separate native repository; the committed capture is validated independently')
        validate(check_current=True)
    def test_current_source_fingerprint_rejects_a_changed_native_file(self):
        snapshot_path=ROOT/self.grid['dependances']['cartographie']
        snapshot=deepcopy(read(snapshot_path))
        with TemporaryDirectory(prefix='native-cartography-') as temporary:
            native=Path(temporary)/'model.yaml'
            native.write_bytes(b'version: test\nnodes: []\nrelations: []\n')
            snapshot['provenance']['fichier']=str(native)
            snapshot['provenance']['sha256']=hashlib.sha256(native.read_bytes()).hexdigest()
            def fixture_read(path):
                return deepcopy(snapshot) if path==snapshot_path else read(path)
            with patch.object(grid_validation,'read',side_effect=fixture_read):
                validate(check_current=True)
                native.write_bytes(native.read_bytes()+b'# source changed\n')
                with self.assertRaisesRegex(AssertionError,'Current cartography differs'):
                    validate(check_current=True)
    def reject(self,change):
        model=deepcopy(self.grid);change(model)
        with self.assertRaises((AssertionError,ValidationError,KeyError)):validate(model)
    def test_wrong_business_area(self):
        self.reject(lambda g:g['blocs'][0]['chemin'].__setitem__(2,g['blocs'][1]['chemin'][2]))
    def test_missing_capability(self):self.reject(lambda g:g['blocs'].pop())
    def test_unaccounted_behavior(self):
        self.reject(lambda g:next(b for b in g['blocs'] if b['variantes_source'])['variantes_source'].pop())
    def test_no_automatic_jh_transfer(self):
        self.reject(lambda g:g['blocs'][0]['calibration'].__setitem__('jh_par_stack',{'java-spring':100}))
    def test_wrong_historical_link(self):self.reject(lambda g:g['blocs'][0].__setitem__('precedent',['CSF-032']))
    def test_out_of_scale(self):self.reject(lambda g:g['blocs'][0]['complexite']['algorithmique'].__setitem__('niveau',6))
    def test_stale_snapshot(self):
        self.reject(lambda g:g['empreintes'].__setitem__(g['dependances']['cartographie'],'0'*64))

if __name__=='__main__':unittest.main(verbosity=2)
