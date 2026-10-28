"""Regression cases that must invalidate a falsely complete or calibrated grid."""
from copy import deepcopy
import unittest
from jsonschema import ValidationError
from validate_complexity_grid import validate
from validate_stacks import ROOT,read

class GridTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.grid=read(ROOT/'source/grille-complexite.yaml')
    def test_reference_and_live_capture(self):validate(check_current=True)
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
