from copy import deepcopy
import unittest
from jsonschema import Draft202012Validator, ValidationError
from mdm_cosmic import project,calculate,SOURCE,SCHEMA
from validate_stacks import ROOT,read

class MdmCosmicTests(unittest.TestCase):
    def setUp(self):
        self.doc=read(ROOT/SOURCE)
        self.benchmark=read(ROOT/self.doc['benchmark_ref'])
        self.caps={c['native_id'] for c in read(ROOT/'audits/2026-11-05-estimation-mdm-oss/scope.json')['coverage']}

    def test_independent_count_and_conversion(self):
        d=calculate(self.caps)
        counts={k:sum(len(p['movements'][k]) for p in self.doc['processes']) for k in ('E','R','W','X')}
        self.assertEqual(d['cfp'],sum(counts.values()))
        self.assertEqual(d['jh'],d['cfp']*self.benchmark['retained_hours_per_CFP']*self.benchmark['retained_factor']/self.doc['day_hours'])
        self.assertEqual(sum(g['cfp'] for g in d['groups']),d['cfp'])
        self.assertEqual(len(self.caps),33)

    def test_duplicates_missing_scope_and_bad_parameters_rejected(self):
        for kind in ('process','movement','scope','hours'):
            d=deepcopy(self.doc)
            if kind=='process':d['processes'].append(d['processes'][0])
            if kind=='movement':d['processes'][0]['movements']['E']*=2
            if kind=='scope':d['processes'][0]['capability_refs']=['invented']
            if kind=='hours':d['day_hours']=0
            with self.subTest(kind=kind),self.assertRaises((ValueError,ValidationError)):
                Draft202012Validator(read(ROOT/SCHEMA)).validate(d)
                project(d,self.benchmark,self.caps)

    def test_no_io_replay_and_no_input_mutation(self):
        from unittest.mock import patch
        original=deepcopy(self.doc)
        with patch('mdm_cosmic.read',side_effect=AssertionError('I/O')):
            result=project(self.doc,self.benchmark,self.caps)
        self.assertEqual(self.doc,original)
        self.assertGreater(result['jh'],0)
