from copy import deepcopy
from unittest.mock import patch
import unittest
from release_dependencies import project,SOURCE
from validate_stacks import ROOT,read
from test_support import reference_study

class ReleaseDependencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study=reference_study()
        cls.org=cls.study.content['delivery_organisation']
        cls.doc=read(ROOT/SOURCE)

    def test_projection_conserves_build_and_freezes_initial_scope(self):
        before=deepcopy(self.doc)
        with patch('release_dependencies.read',side_effect=AssertionError('IO')):
            result=project(self.doc,self.org)
        self.assertEqual(self.doc,before)
        self.assertEqual(result,self.org['release_dependencies'])
        self.assertEqual(len(result['releases']),len(self.org['teams'])-1)
        self.assertAlmostEqual(sum(r['jh'] for r in result['releases']),sum(r['jh'] for r in self.org['charge_dossier']['phases'][0]['rows']))
        for r in result['releases']:
            self.assertTrue(all(c['work_unit_ref'].startswith('core/') for c in r['work_contributions']))
        altered=deepcopy(self.org)
        for p in altered['charge_dossier']['phases'][1:]:p['rows']=[]
        self.assertEqual(project(self.doc,altered),result)

    def test_unknown_duplicate_self_and_out_of_range_rejected(self):
        for kind in ('unknown','duplicate','self','threshold','excluded','empty','path'):
            d=deepcopy(self.doc);c=d['constraints'][0]
            if kind=='unknown':c['provider_release_ref']='missing'
            elif kind=='duplicate':d['constraints'].append(deepcopy(c))
            elif kind=='self':c['consumer_release_ref']=c['provider_release_ref']
            elif kind=='threshold':c['threshold_pct']=101
            elif kind=='excluded':d['excluded_team_refs']=[]
            elif kind=='empty':c['prerequisite']=''
            elif kind=='path':c['evidence_refs']=['../outside']
            with self.subTest(kind=kind),self.assertRaises(ValueError):project(d,self.org)

    def test_production_cycle_rejected_but_partial_contract_cycle_not_assumed_blocking(self):
        d=deepcopy(self.doc);c=next(c for c in d['constraints'] if c['gate']=='production')
        reverse=dict(c,id='reverse',provider_release_ref=c['consumer_release_ref'],consumer_release_ref=c['provider_release_ref'])
        d['constraints'].append(reverse)
        with self.assertRaisesRegex(ValueError,'production cycle'):project(d,self.org)
        reverse.update(gate='start',threshold_pct=30)
        project(d,self.org)

    def test_paas_and_contract_gates_are_explicit_hypotheses(self):
        for c in self.doc['constraints']:
            self.assertEqual(c['assessment'],'sequencing_assumption')
            self.assertEqual(c['threshold_pct'],100 if c['gate']=='production' else 20 if c['provider_release_ref']=='paas-r1' else 30)
            self.assertTrue(c['prerequisite'] and c['work_scope'] and c['justification'] and c['evidence_refs'])
        mdm=next(c for c in self.doc['constraints'] if c['provider_release_ref']=='mdm-platform-r1' and c['consumer_release_ref']=='master-data-r1' and c['gate']=='start')
        self.assertIn('Simulateur',mdm['prerequisite'])
