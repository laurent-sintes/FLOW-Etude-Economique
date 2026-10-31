"""Financial integrity of professional scope and an explicitly unadopted complete-product proposal."""
from copy import deepcopy
import unittest
from core_product_scope import partition
from core_product_estimate import calculate,load_inputs,validate_technical_trials
from model_context import model_session
from validate_stacks import ROOT,read
from test_support import reference_study
class ProductScopeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.study=reference_study();cls.units=next(o['core_units'] for o in cls.study.economic['options'] if o['stack']=='java-spring');cls.proposal=cls.study.content['core_product_scope']['proposal'];cls.inputs=load_inputs()[1];cls.basis=read(ROOT/load_inputs()[0]['adoption']['basis']['path'])['baseline_units']
 def calc(self,d):
  with model_session():return calculate(d,self.basis)
 def test_reference_and_replacement_are_separate(self):
  r=self.proposal;self.assertEqual((r['status'],r['adopted_jh'],r['total_jh']),('retained',6660,6660));self.assertEqual(r['total_jh'],4160-340+2010+160+670);self.assertEqual(self.study.parameters['options']['java-spring']['build'],4198680);self.assertEqual([u['total_jh'] for u in self.units[:3]],[1500,340,100])
 def test_both_purposes_conserve_each_role_and_cost(self):
  r=self.proposal;self.assertEqual(sum(v['jh'] for v in r['purposes'].values()),r['total_jh']);self.assertEqual(sum(v['eur_ht'] for v in r['purposes'].values()),r['eur_ht'])
  for role in r['roles']:self.assertEqual(sum(v['roles'][role['id']] for v in r['purposes'].values()),role['jh'])
  self.assertEqual(r['existing_it_partition_jh'],104);self.assertEqual(r['purposes']['it-complement']['jh'],104+670)
 def test_alignment_uses_unrounded_reference_and_grouping_is_not_added(self):
  r=self.proposal;c=r['cosmic_process'];self.assertNotEqual(c['reference_unrounded_jh'],r['rows'][0]['jh']);self.assertAlmostEqual(c['alignment']['gap_pct'],100*(c['jh']/c['reference_unrounded_jh']-1));self.assertAlmostEqual(r['grouping_sensitivity']['single_project_jh'],8066.294275404798);self.assertEqual(r['total_jh'],6660)
 def test_unknown_is_not_zero_and_partial_partitions_stay_unknown(self):
  r=partition(self.units,[]);self.assertIsNone(r['purposes']['it-complement']['jh']);self.assertEqual(r['unallocated_jh'],6660);self.assertIsNone(r['additional_required_jh'])
 def test_declared_partition_cannot_create_or_lose_a_role_day(self):
  u=self.units[0];roles={r['id']:r['jh'] for r in u['roles']};a=dict(unit_id=u['id'],basis='Work attribution',evidence_refs=['proof'],shares=[dict(purpose_id='business-runtime',jh_by_role=roles),dict(purpose_id='it-complement',jh_by_role={})])
  r=partition([u],[a]);self.assertTrue(r['partition_complete']);self.assertEqual(r['purposes']['business-runtime']['jh'],1500)
  a['shares'][1]['jh_by_role']['qa']=1
  with self.assertRaisesRegex(ValueError,'conservation'):partition([u],[a])
 def test_file_reuse_credit_and_module_domains(self):
  for mutation in ('duplicate','negative','excess_credit'):
   d=deepcopy(self.inputs)
   if mutation=='duplicate':d['measurements']['files'].append(deepcopy(d['measurements']['files'][0]))
   if mutation=='negative':d['groups']['process-studio']['fraction']=-1
   if mutation=='excess_credit':d['measurements']['files'][0]['existing_MD_credit_units']=1e9
   with self.assertRaises(ValueError):self.calc(d)
 def test_export_replay_requires_no_oss_checkout(self):
  from unittest.mock import patch
  from estimation_calculation import metamodel,evaluate_rule
  with model_session():rules={r['id']:r for r in metamodel()['rules']}
  def replay_rule(id,**values):return evaluate_rule(rules[id],**values)
  with patch('core_product_estimate.formula',side_effect=AssertionError('Disk-backed formula access forbidden')),patch('pathlib.Path.read_bytes',side_effect=AssertionError('File reads forbidden')),patch('pathlib.Path.read_text',side_effect=AssertionError('File reads forbidden')):
   r=calculate(deepcopy(self.inputs),deepcopy(self.basis),rule_function=replay_rule)
  self.assertEqual((r['total_jh'],r['eur_ht']),(self.proposal['total_jh'],self.proposal['eur_ht']))
 def test_trials_do_not_recalibrate_or_adopt_effort(self):
  t=self.proposal['technical_trials'];self.assertEqual(t['effort_effect'],'unchanged');self.assertGreater(t['checks_passed'],0)
  self.assertEqual(self.proposal['total_jh'],6660);self.assertEqual(sum(u['total_jh'] for u in self.units),6660)
  self.assertTrue(all(row['function_refs'] for row in t['funding']))
 def test_trial_evidence_rejects_failure_unknown_funding_and_other_proposal(self):
  from validate_stacks import read,ROOT
  doc,_=load_inputs();trials=doc['technical_trials'];proof=read(ROOT/trials['evidence']['path'])
  for kind in ('failure','funding','binding'):
   t=deepcopy(trials);p=deepcopy(proof)
   if kind=='failure':p['check_groups'][0]['checks'][0]['passed']=False
   if kind=='funding':t['funding'][0]['module_refs']=['unknown']
   if kind=='binding':p['proposal_inputs_sha256']='0'*64
   with self.assertRaisesRegex(ValueError,'technical trial'):validate_technical_trials(t,p,self.inputs,doc['inputs']['sha256'])
 def test_trial_download_archive_is_complete_and_self_contained(self):
  import base64,gzip,hashlib,json
  from validate_stacks import read,ROOT
  doc,_=load_inputs();proof=read(ROOT/doc['technical_trials']['evidence']['path']);a=proof['archive'];raw=gzip.decompress(base64.b64decode(a['payload']))
  self.assertEqual(hashlib.sha256(raw).hexdigest(),a['uncompressed_sha256']);files=json.loads(raw);self.assertEqual(len(files),a['files'])
  for item in files.values():self.assertEqual(hashlib.sha256(item['text'].encode('utf8')).hexdigest(),item['sha256'])
  self.assertTrue(any(path.endswith('durable-restart.py') for path in files));self.assertTrue(any('/results/live/' in path for path in files))
 def test_cosmic_consumed_functions_are_not_added(self):
  c=self.proposal['cosmic'];self.assertEqual(c['CFP_by_group']['supply-workbenches'],5);self.assertEqual(self.proposal['cosmic_process']['CFP'],216);self.assertEqual(self.proposal['it_cosmic']['CFP'],68)
  consumed=[p for rows in self.inputs['cosmic']['processes'].values() for p in rows if p['scope']=='existing_function_consumed'];self.assertEqual(len(consumed),10)
 def test_sensitivities_are_one_at_a_time_and_reference_unchanged(self):
  r=self.proposal;self.assertEqual(len(r['sensitivities']),16);self.assertTrue(any(s['delta_jh']>0 for s in r['sensitivities']));self.assertTrue(any(s['delta_jh']<0 for s in r['sensitivities']));self.assertEqual(self.study.baseline['options'][0]['build'],4198680)
if __name__=='__main__':unittest.main()
