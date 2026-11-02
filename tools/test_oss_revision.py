"""Regression checks for adopted OSS selections and visible unpriced scope."""
from test_support import active_reference
from collections import Counter
from copy import deepcopy
import json
import unittest
from unittest.mock import patch
from estimation_inputs import registry, load_proofs
from estimation_preparation import prepare
from estimation_calculation import metamodel, evaluate_rule
from test_support import reference_study
from validate_stacks import ROOT

class OSSRevisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study=reference_study();cls.reg=registry();cls.docs=load_proofs(cls.reg)
        cls.rules={r['id']:r for r in metamodel()['rules']}
        cls.specs=[c for c in cls.docs['audits/2026-11-02-adoption-perimetre-scenarios/basis.json']['registry']['calculations'] if c['recipe']=='oss_reference_revision_v1']
        cls.before=json.loads((ROOT/'audits/2026-11-02-adoption-revision-oss/before-financial.json').read_text(encoding='utf8'))
    def formula(self,id,**values):return evaluate_rule(self.rules[id],**values)
    def test_revision_replays_without_io_and_preserves_funding(self):
        self.assertEqual(len(self.specs),7)
        for spec in self.specs:
            with self.subTest(unit=spec['unit_id']),patch('pathlib.Path.read_text',side_effect=AssertionError('disk forbidden')),patch('pathlib.Path.read_bytes',side_effect=AssertionError('disk forbidden')):
                p=prepare(self.docs,spec,self.reg,self.formula)
            self.assertEqual(p['allocation']['selected_reference'],'selected-oss')
            self.assertEqual(len(p['rows']),5)
            self.assertGreater(p['trace']['revision']['equivalent_units'],0)
            self.assertEqual(spec['funding_claims'],next(c for c in self.docs[spec['inputs']['revision_basis']]['registry']['calculations'] if c['id']==spec['id'])['funding_claims'])
        owners=Counter(x['mechanism'] for c in self.reg['calculations'] for x in c['funding_claims'] if x['mode']=='funded')
        self.assertTrue(all(v==1 for v in owners.values()))
    def test_changed_scope_bank_and_total_are_rejected(self):
        for kind in ('scope','bank','total'):
            spec=deepcopy(next(c for c in self.specs if c['unit_id']=='supply-controls-java-spring'));docs=deepcopy(self.docs)
            if kind=='scope':spec['scope']['capabilities']=[]
            proposal=docs[spec['inputs']['revision_proposal']]
            row=next(r for r in proposal['units'] if r['id']==spec['unit_id'])
            if kind=='bank':row['calculation_details']['families'][0]['new_bank']+=1
            if kind=='total':row['proposal_jh']+=10
            with self.subTest(kind=kind),self.assertRaises(ValueError):prepare(docs,spec,self.reg,self.formula)
    def test_five_options_and_four_horizons_reconcile(self):
        s=self.study;before={o['stack']:o for o in self.before['baseline']['options']}
        self.assertEqual(s.parameters['options']['java-spring']['build'],active_reference()['cost_eur_ht'])
        self.assertEqual(self.before['parameters']['options']['java-spring']['build']-3749300,449380)
        parameters=deepcopy(s.parameters)
        parameters['options']['java-spring']['build']=self.before['parameters']['options']['java-spring']['build']
        counterfactual={o['stack']:o for o in s.simulate(parameters)['options']}
        for o in s.baseline['options']:
            self.assertEqual([h['years'] for h in o['horizons']],[3,5,7,10])
            if o['stack']!='java-spring':
                self.assertEqual(o,counterfactual[o['stack']])
                continue
            self.assertEqual(o['annual_base'],before[o['stack']]['annual_base'])
            for h,old in zip(o['horizons'],counterfactual[o['stack']]['horizons']):
                self.assertAlmostEqual(old['totals']['total']-h['totals']['total'],(self.before['parameters']['options']['java-spring']['build']-active_reference()['cost_eur_ht'])*h['build_progress'],places=2)
                self.assertAlmostEqual(sum(h['cost_natures'].values()),h['totals']['total'],places=2)
    def test_current_estimate_and_missing_features_share_the_same_page_data(self):
        reading=self.study.content['gross_evaluations'];core=reading['phases']['acquisition']['options']['java-spring']['core']
        self.assertEqual(core['status'],'adopted');self.assertEqual(core['adopted_jh'],active_reference()['total_jh'])
        self.assertEqual([r['adopted_jh'] for r in core['rows']],active_reference()['unit_days'])
        self.assertEqual({r['id'] for r in core['gap_reviews']},{f'G{i:02}' for i in range(1,10)})
        self.assertEqual({r['id'] for r in core['priority_gaps']},{'G01','G03'})
        self.assertEqual(len(core['professional_functions']),20)
        self.assertEqual(sum(r['jh'] for r in core['roles']),active_reference()['total_jh'])
        self.assertEqual(sum(r['value'] for r in core['programme_roles']),2700)
        comparison=self.study.content['market']['comparison']['budget_review']
        by_id={r['gap_ref']:r for r in comparison['reviews']}
        for gap in core['gap_reviews']:self.assertEqual(gap['residual'],by_id[gap['id']]['residual'].replace(' ; ','. ').replace('; ','. ').replace(' ;','.'))
        for phase in reading['phases'].values():
            for option in phase['options'].values():self.assertTrue(all(r['value'] is None for r in option['remaining']))
    def test_original_evidence_and_personal_simulations_are_preserved(self):
        s=self.study
        self.assertEqual(s.simulate(s.parameters),s.baseline)
        self.assertEqual(self.docs['audits/2026-11-01-proposition-references-oss/results.json']['status'],'proposal_not_adopted')
        old=self.docs['audits/2026-11-02-adoption-revision-oss/basis.json']
        current={u['id']:u for u in s.economic['options'][0]['core_units']}
        for u in old['units']:
            if u['id'] in ('stock-java-spring',):
                self.assertEqual(current[u['id']]['total_jh'],u['total_jh'])
            self.assertEqual(current[u['id']]['capabilities'],u['capabilities'])
if __name__=='__main__':unittest.main()
