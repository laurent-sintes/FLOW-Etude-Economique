"""User adoption: portable COSMIC proofs, unique funding and all economic horizons."""
from test_support import active_reference
from collections import Counter
from copy import deepcopy
import json,unittest
from unittest.mock import patch
from validate_stacks import ROOT
from estimation_inputs import registry,load_proofs
from estimation_preparation import prepare
from estimation_calculation import metamodel,evaluate_rule
from test_support import reference_study

class ScenarioScopeAdoptionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.study=reference_study();cls.reg=registry();cls.docs=load_proofs(cls.reg)
  cls.specs=[c for c in cls.reg['calculations'] if c['recipe']=='scenario_scope_adoption_v1']
  cls.before=json.loads((ROOT/'audits/2026-11-02-adoption-perimetre-scenarios/before-financial.json').read_text(encoding='utf-8'))
  cls.rules={r['id']:r for r in metamodel()['rules']}
 def formula(self,id,**v):return evaluate_rule(self.rules[id],**v)
 def test_portable_replay_counts_and_input_immutability(self):
  self.assertEqual(len(self.specs),5);scope=self.docs['audits/2026-11-02-adoption-perimetre-scenarios/scope.json'];before=deepcopy(scope)
  for c in self.specs:
   with patch('pathlib.Path.read_text',side_effect=AssertionError('No disk')),patch('pathlib.Path.read_bytes',side_effect=AssertionError('No disk')):
    p=prepare(self.docs,c,self.reg,self.formula)
   row=next(r for r in scope['units'] if r['unit_id']==c['unit_id'])
   self.assertEqual(p['method'],'COSMIC × ISBSG')
   self.assertEqual(sum(len(x[k]) for x in p['trace']['scope_adoption']['processes'] for k in ('E','R','W','X')),row['CFP'])
   self.assertEqual(sum(p['allocation']['role_effort_jh'].values()),row['proposal_jh'])
  self.assertEqual(scope,before)
 def test_cross_scope_overlap_and_count_tampering_are_rejected(self):
  c=next(c for c in self.specs if c['unit_id']=='supply-controls-java-spring')
  for kind in ('duplicate','credit','wrong_capability','count','benchmark','decision'):
   docs=deepcopy(self.docs);r=next(r for r in docs[c['inputs']['revision_proposal']]['units'] if r['unit_id']==c['unit_id'])
   if kind=='duplicate':r['processes'].append(deepcopy(r['processes'][0]))
   if kind=='credit':r['kept_process_ids']=[r['removed_process_ids'][0]]
   if kind=='wrong_capability':r['processes'][0]['capabilities']=['BC-020']
   if kind=='count':r['CFP']+=1
   if kind=='benchmark':r['benchmark']['hours_per_CFP']=25
   if kind=='decision':next(x for x in docs[c['inputs']['revision_hypotheses']]['units'] if x['id']==c['unit_id'])['proposal_jh']+=10
   with self.subTest(kind=kind),self.assertRaises(ValueError):prepare(docs,c,self.reg,self.formula)
 def test_funding_and_current_units_reconcile(self):
  units=self.study.economic['options'][0]['core_units']
  self.assertEqual(sum(u['total_jh'] for u in units),active_reference()['total_jh'])
  self.assertEqual(sum(u['cost_eur_ht'] for u in units),active_reference()['cost_eur_ht'])
  self.assertEqual(Counter(u['method'] for u in units),active_reference()['methods'])
  counts=Counter(x['mechanism'] for c in self.reg['calculations'] for x in c['funding_claims'] if x['mode']=='funded')
  self.assertEqual(set(counts),{m['id'] for m in self.reg['mechanisms']});self.assertTrue(all(v==1 for v in counts.values()))
  core=self.study.content['gross_evaluations']['phases']['acquisition']['options']['java-spring']['core']
  self.assertNotIn('revision_summary',core);self.assertEqual(core['adopted_jh'],active_reference()['total_jh'])
 def test_five_options_horizons_and_personal_simulations(self):
  s=self.study;self.assertEqual(s.simulate(s.parameters),s.baseline)
  parameters=deepcopy(s.parameters);parameters['options']['java-spring']['build']=3749300
  counter={o['stack']:o for o in s.simulate(parameters)['options']}
  for o in s.baseline['options']:
   self.assertEqual([h['years'] for h in o['horizons']],[3,5,7,10])
   if o['stack']!='java-spring':self.assertEqual(o,counter[o['stack']]);continue
   for h,old in zip(o['horizons'],counter[o['stack']]['horizons']):
    self.assertAlmostEqual(h['totals']['total']-old['totals']['total'],(active_reference()['cost_eur_ht']-3749300)*h['build_progress'],places=2)
    self.assertAlmostEqual(sum(h['cost_natures'].values()),h['totals']['total'],places=2)
if __name__=='__main__':unittest.main()
