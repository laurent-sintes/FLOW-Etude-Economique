"""Adopted professional estimate: portable preparation, unique funding and financial reconciliation."""
from collections import Counter
from copy import deepcopy
import json,unittest
from unittest.mock import patch
from validate_stacks import ROOT
from model_context import model_session
from estimation_inputs import registry,load_proofs,validate_binding
from estimation_preparation import prepare
from estimation_calculation import calculate,formula,evaluate_rule,rounded
from retained_core import validate
from test_support import reference_study

class ProfessionalAdoptionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.study=reference_study();cls.units=validate()['units'];cls.reg=registry();cls.docs=load_proofs(cls.reg)
  cls.specs=[c for c in cls.reg['calculations'] if c['recipe']=='professional_components_v1']
 def test_total_roles_purposes_and_budget_are_adopted_once(self):
  p=self.study.content['core_product_scope']['proposal'];self.assertEqual((p['status'],p['adopted_jh'],p['total_jh']),('retained',6660,6660));self.assertEqual(p['previous_adopted_jh'],4160)
  self.assertEqual(self.study.parameters['options']['java-spring']['build'],4198680)
  split=next(o for o in self.study.content['core_product_scope']['options'] if o['stack']=='java-spring')
  self.assertTrue(split['partition_complete']);self.assertEqual(split['unallocated_jh'],0)
  self.assertEqual((split['purposes']['business-runtime']['jh'],split['purposes']['it-complement']['jh']),(5886,774))
  self.assertEqual((split['purposes']['business-runtime']['eur_ht'],split['purposes']['it-complement']['eur_ht']),(3706338,492342))
  self.assertEqual(sum(r['jh'] for r in p['roles']),6660)
  for role in p['roles']:self.assertEqual(sum(v['roles'][role['id']] for v in p['purposes'].values()),role['jh'])
 def test_original_families_and_native_reference_are_preserved(self):
  b=self.docs[self.specs[0]['inputs']['adoption_basis']];before=json.loads(json.dumps(__import__('yaml').safe_load(b['source_snapshots']['source/estimations-core-retenues.yaml'])))['units']
  actual={u['id']:u for u in self.units}
  for old in before:
   if old['id']!='process-management-java-spring':self.assertEqual(actual[old['id']],old)
  caps=[c['id'] for u in self.units for c in u['capabilities']];self.assertEqual(len(caps),88);self.assertEqual(len(set(caps)),88)
  for c in self.specs:
   if c['scope']['level']=='professional_function_group':self.assertEqual(c['scope']['capabilities'],[]);self.assertNotIn('native_id',c['scope'])
 def test_three_calculations_replay_from_exported_documents_without_io(self):
  from estimation_calculation import metamodel
  with model_session():rules={r['id']:r for r in metamodel()['rules']}
  def f(id,**v):return evaluate_rule(rules[id],**v)
  for c in self.specs:
   with self.subTest(component=c['unit_id']),patch('pathlib.Path.read_text',side_effect=AssertionError('disk forbidden')),patch('pathlib.Path.read_bytes',side_effect=AssertionError('disk forbidden')):
    result=prepare(self.docs,c,self.reg,f)
   self.assertEqual(len(result['rows']),4);self.assertEqual(sum(result['allocation']['role_effort_jh'].values()),next(u['total_jh'] for u in self.units if u['id']==c['unit_id']))
   expected=calculate({'id':c['id']});self.assertEqual(expected['trace']['CFP'],result['trace']['CFP'])
   for row in result['rows']:self.assertAlmostEqual(row['common_jh']+row['complements_jh'],row['jh'])
 def test_group_funding_scope_and_cosmic_duplicates_are_rejected(self):
  c=self.specs[0]
  for kind in ('groups','cosmic','credit','activities'):
   spec=deepcopy(c);docs=deepcopy(self.docs);d=docs[c['inputs']['proposal_inputs']]
   if kind=='groups':spec['recipe_parameters']['module_groups']=['data-services']
   if kind=='cosmic':d['cosmic']['processes']['process-studio'][0]['E'].append(d['cosmic']['processes']['process-studio'][0]['E'][0])
   if kind=='credit':d['measurements']['files'][0]['existing_MD_credit_units']=1e12
   if kind=='activities':docs[c['inputs']['adoption_basis']]['activity_source']['activities'][0]['percent_by_phase'].append(100)
   with model_session(),self.subTest(kind=kind),self.assertRaises(ValueError):prepare(docs,spec,self.reg,formula)
 def test_each_professional_group_has_one_funding_owner(self):
  counts=Counter(x['mechanism'] for c in self.reg['calculations'] for x in c['funding_claims'] if x['mode']=='funded');groups=[m for m in self.reg['mechanisms'] if m['basis']['kind']=='professional_group'];self.assertEqual(len(groups),7)
  self.assertTrue(all(counts[m['id']]==1 for m in groups))
  u=deepcopy(next(u for u in self.units if u['id']=='professional-it-java-spring'));u['capabilities']=[dict(id='BC-001',native_id='invented')]
  with self.assertRaises(ValueError):validate_binding(u)
 def test_published_activity_distribution_and_explicit_roles_stay_distinct(self):
  for c in self.specs:
   r=calculate({'id':c['id']});self.assertAlmostEqual(sum(a['jh'] for a in r['activities']),r['total_jh']);self.assertTrue(all(a['role_weights']=={} for a in r['activities']));self.assertTrue(r['trace']['role_allocation_basis'])
  self.assertEqual(rounded(18.36264282846441,.1),18.4);self.assertEqual(rounded(8.212869832055368,.1),8.2)
 def test_other_options_and_calendars_are_preserved(self):
  before=json.loads((ROOT/'audits/2026-10-31-adoption-produit-professionnel/before-financial.json').read_text('utf8'));old={o['stack']:o for o in before['baseline']['options']}
  for o in self.study.baseline['options']:
   if o['stack']!='java-spring':self.assertEqual(o,old[o['stack']])
  self.assertEqual(self.study.parameters['options']['java-spring']['build_mois'],before['parameters']['options']['java-spring']['build_mois'])
  self.assertEqual(self.study.content['core_product_scope']['proposal']['cosmic_process']['CFP'],216)
  self.assertEqual(self.study.content['core_product_scope']['proposal']['it_cosmic']['CFP'],68)
if __name__=='__main__':unittest.main()
