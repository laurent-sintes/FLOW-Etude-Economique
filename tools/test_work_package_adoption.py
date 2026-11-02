"""Adopted deliverable sums, portable evidence, tamper rejection and economic deltas."""
from test_support import active_reference
from copy import deepcopy
from collections import Counter
import unittest
from unittest.mock import patch
from estimation_inputs import registry,load_proofs
from estimation_preparation import prepare
from estimation_calculation import metamodel,evaluate_rule
from test_support import reference_study
from validate_stacks import ROOT
import json

class WorkPackageAdoptionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.study=reference_study();cls.reg=registry();cls.docs=load_proofs(cls.reg)
  cls.specs=[c for c in cls.reg['calculations'] if c['recipe']=='work_package_adoption_v1']
  cls.rules={r['id']:r for r in metamodel()['rules']}
 def formula(self,id,**v):return evaluate_rule(self.rules[id],**v)
 def test_portable_replay_and_input_immutability(self):
  self.assertEqual(len(self.specs),active_reference()['methods']['Estimation détaillée par livrable']);before=deepcopy(self.docs['audits/2026-11-02-adoption-quatre-lots/scope.json']);ids=[]
  for c in self.specs:
   with patch('pathlib.Path.read_text',side_effect=AssertionError('No disk')),patch('pathlib.Path.read_bytes',side_effect=AssertionError('No disk')):
    p=prepare(self.docs,c,self.reg,self.formula)
   self.assertEqual(p['method'],'Estimation détaillée par livrable');work=p['trace']['work_package_adoption']['work'];ids.extend(w['id'] for w in work)
   self.assertEqual(sum(w['jh'] for w in work),p['retained_effort_jh']);self.assertEqual(sum(p['allocation']['role_effort_jh'].values()),p['retained_effort_jh'])
   self.assertTrue(p['rows']);self.assertGreater(p['functional']['CFP'],0)
  expected=sum(len(u['work']) for u in active_reference()['units'].values());self.assertEqual(len(ids),expected);self.assertEqual(len(set(ids)),expected)
  self.assertEqual(before,self.docs['audits/2026-11-02-adoption-quatre-lots/scope.json'])
 def test_wrong_owner_duplicate_effort_and_decision_are_rejected(self):
  c=next(c for c in self.specs if c['unit_id']=='master-data-java-spring')
  for kind in ('duplicate','negative','boolean','foreign_owner','case','observed','decision','editing'):
   docs=deepcopy(self.docs);scope=docs[c['inputs']['revision_proposal']];row=next(r for r in scope['units'] if r['id']==c['unit_id']);w=row['work'][0]
   if kind=='duplicate':row['work'].append(deepcopy(w))
   if kind=='negative':w['jh']=-1
   if kind=='boolean':w['jh']=True
   if kind=='foreign_owner':w['funding_ref']='professional-supply-workbenches'
   if kind=='case':w['scenario_refs']=['missing-case']
   if kind=='observed':w['effort_status']='observed'
   if kind=='decision':next(r for r in docs[c['inputs']['revision_hypotheses']]['units'] if r['id']==c['unit_id'])['proposal_jh']+=1
   if kind=='editing':row['work']=[w for w in row['work'] if w['id']!='MD09']
   with self.subTest(kind=kind),self.assertRaises(ValueError):prepare(docs,c,self.reg,self.formula)
 def test_budget_scope_and_correction_are_adopted(self):
  s=self.study;units=s.economic['options'][0]['core_units']
  self.assertEqual(sum(u['total_jh'] for u in units),active_reference()['total_jh']);self.assertEqual(sum(u['cost_eur_ht'] for u in units),active_reference()['cost_eur_ht'])
  self.assertEqual(Counter(u['method'] for u in units),active_reference()['methods'])
  caps=[c['id'] for u in units for c in u['capabilities']];self.assertEqual(len(caps),len(set(caps)));self.assertEqual(len(caps),88)
  md=next(u for u in units if u['id']=='master-data-java-spring');work=md['trace']['work_package_adoption']['work'];self.assertEqual(next(w['jh'] for w in work if w['id']=='MD09'),active_reference()['units']['master-data-java-spring']['work']['MD09'])
  claims=Counter(x['mechanism'] for c in self.reg['calculations'] for x in c['funding_claims'] if x['mode']=='funded');self.assertTrue(all(n==1 for n in claims.values()))
  core=s.content['gross_evaluations']['phases']['acquisition']['options']['java-spring']['core'];self.assertEqual(core['adopted_jh'],active_reference()['total_jh']);self.assertNotIn('revision_summary',core)
  self.assertEqual(sum(len(r['detail']['work_packages']) for r in core['rows']),sum(len(u['work']) for u in active_reference()['units'].values()))
 def test_twenty_horizons_and_simulation_parameters(self):
  s=self.study;self.assertEqual(s.simulate(s.parameters),s.baseline)
  before=active_reference()['before']
  self.assertEqual(before['parameters']['options']['java-spring']['build']+active_reference()['delta_cost_eur_ht'],active_reference()['cost_eur_ht'])
  current=s.simulate(before['parameters']);self.assertEqual({k:v for k,v in current.items() if k!='model_version'},{k:v for k,v in before['baseline'].items() if k!='model_version'})
  original={o['stack']:o for o in before['baseline']['options']}
  for o in s.baseline['options']:
   old=original[o['stack']]
   if o['stack']!='java-spring':self.assertEqual(o,old);continue
   for h,p in zip(o['horizons'],old['horizons']):
    self.assertAlmostEqual(h['totals']['total']-p['totals']['total'],active_reference()['delta_cost_eur_ht']*h['build_progress'],places=2)
    self.assertAlmostEqual(sum(h['cost_natures'].values()),h['totals']['total'],places=2)

if __name__=='__main__':unittest.main()
