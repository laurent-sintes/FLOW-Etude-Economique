"""Adoption transactions must be reviewable, stale-safe and recoverable."""
from copy import deepcopy
from pathlib import Path
import base64,json,tempfile,unittest
from unittest.mock import patch
import adoption_transaction as tx
from validate_stacks import ROOT
from core_adoption_reference import load_reference

class TransactionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'tmp');self.root=Path(self.tmp.name).resolve()
  assert self.root.is_relative_to((ROOT/'tmp').resolve())
  (self.root/'source').mkdir();(self.root/'source/a.yaml').write_bytes(b'old: 1\n')
 def tearDown(self):self.tmp.cleanup()
 def plan(self):return tx.create_plan(self.root,{'source/a.yaml':b'new: 2\n','audits/example/new.json':b'{"value":3}\n'},{'source/a.yaml':tx.digest(b'old: 1\n')},{'total_jh':3},{'passed':True})
 def test_apply_is_bound_to_the_validated_contents_and_is_not_repeatable(self):
  p=self.plan();r=tx.apply(p);self.assertEqual(r['status'],'committed');self.assertEqual((self.root/'source/a.yaml').read_bytes(),b'new: 2\n')
  with self.assertRaisesRegex(ValueError,'Stale'):tx.apply(p)
 def test_stale_tampered_or_escaping_plans_cannot_write(self):
  p=self.plan();(self.root/'source/a.yaml').write_bytes(b'user edit\n')
  with self.assertRaisesRegex(ValueError,'Stale'):tx.apply(p)
  self.assertFalse((self.root/'audits/example/new.json').exists())
  doc=json.loads(p.read_text(encoding='utf-8'));doc['entries'][0]['after']='changed';p.write_bytes(tx.encode(doc))
  with self.assertRaisesRegex(ValueError,'Plan changed'):tx.apply(p)
  for name in ('../outside.yaml','source/../../outside.yaml','tools/validate_stacks.py','C:/outside.yaml'):
   with self.subTest(name=name),self.assertRaises(ValueError):tx.target(self.root,name)
 def test_mid_write_failure_restores_exact_bytes_and_removes_new_files(self):
  p=self.plan()
  def fail(name):
   if name.startswith('audits/'):raise OSError('disk failure')
  with self.assertRaisesRegex(OSError,'disk failure'):tx.apply(p,after_write=fail)
  self.assertEqual((self.root/'source/a.yaml').read_bytes(),b'old: 1\n');self.assertFalse((self.root/'audits/example/new.json').exists());self.assertFalse((self.root/'tmp/core-adoptions/pending.json').exists())
 def interrupted(self):
  p=self.plan();doc,_=tx.load_plan(p)
  for e in doc['entries']:tx.atomic(tx.target(self.root,e['path']),base64.b64decode(e['after']))
  record=dict(id=doc['id'],plan=str(p),plan_sha256=doc['sha256'],status='applying')
  tx.atomic(p.parent/'journal.json',tx.encode(record));tx.atomic(self.root/'tmp/core-adoptions/pending.json',tx.encode(record));return p
 def test_recovery_restores_interrupted_writes_and_blocks_model_reads_until_done(self):
  import model_context
  self.interrupted()
  with patch.object(model_context,'__file__',str(self.root/'tools/model_context.py')):
   with self.assertRaisesRegex(ValueError,'ADOPTION_IN_PROGRESS'):
    with model_context.model_session():pass
   self.assertEqual(tx.recover(self.root)['status'],'rolled_back')
   with model_context.model_session():pass
  self.assertEqual((self.root/'source/a.yaml').read_bytes(),b'old: 1\n')
 def test_recovery_will_not_overwrite_foreign_edits_and_lock_is_exclusive(self):
  self.interrupted();(self.root/'source/a.yaml').write_bytes(b'foreign edit\n')
  with self.assertRaisesRegex(ValueError,'foreign'):tx.recover(self.root)
  self.assertEqual((self.root/'source/a.yaml').read_bytes(),b'foreign edit\n');self.assertTrue((self.root/'tmp/core-adoptions/pending.json').exists())
  with tx.lock(self.root):
   with self.assertRaisesRegex(ValueError,'lock'):
    with tx.lock(self.root):pass

class AdoptionCommandTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  from test_support import reference_study
  cls.study=reference_study()
 def test_frozen_reference_is_isolated_and_bound_to_the_adopted_decision(self):
  from test_support import active_reference
  a=active_reference();a['total_jh']=-1;self.assertGreater(active_reference()['total_jh'],0)
  self.assertEqual(active_reference()['total_jh'],sum(u['total_jh'] for u in self.study.economic['options'][0]['core_units']))
 def test_unchanged_proposal_is_a_noop_and_invalid_scope_cannot_be_staged(self):
  from adopt_core import template,project
  from estimation_inputs import registry,load_proofs
  from model_context import model_session
  with model_session():
   reg=registry();docs=load_proofs(reg);proposal=template(self.study)
   changes,summary=project(proposal,self.study,reg,docs,'No new budget')
   self.assertIsNone(changes);self.assertEqual(summary['status'],'no_change')
   for kind in ('duplicate','owner','purpose','case'):
    bad=deepcopy(proposal);w=bad['units'][0]['work'][0]
    if kind=='duplicate':bad['units'][0]['work'].append(deepcopy(w))
    if kind=='owner':w['funding_ref']='unknown-owner'
    if kind=='purpose':bad['units'][0]['purpose_totals']['support']+=1
    if kind=='case':w['scenario_refs']=['unknown-case']
    with self.subTest(kind=kind),self.assertRaises(ValueError):project(bad,self.study,reg,docs,'No new budget')
 def test_prepared_contract_package_uses_the_same_projection_without_new_engine_code(self):
  import yaml
  from adopt_core import template,project,project_contracts,refresh_reading
  from estimation_inputs import registry,load_proofs
  from model_context import model_session
  with model_session():
   reg=registry();docs=load_proofs(reg);proposal=template(self.study);proposal['units']=proposal['units'][:1]
   proposal['units'][0]['work'][0]['jh']+=1;proposal['units'][0]['purpose_totals']['core-domain']+=1
   changes,summary=project(proposal,self.study,deepcopy(reg),docs,'Prepared package validation')
   documents={name:json.loads(raw) if name.endswith('.json') else raw.decode('utf-8') if name.endswith('.md') else yaml.safe_load(raw) for name,raw in changes.items() if name!='source/version-modele.yaml'}
   package=dict(format=1,method='prepared_contracts',date=proposal['date'],decision_ref=summary['decision']['path'],documents=documents)
   projected,other=project_contracts(package,self.study,reg,docs,'Prepared package validation')
   self.assertEqual(other['total_jh'],summary['total_jh']);self.assertEqual(other['cost_eur_ht'],summary['cost_eur_ht'])
   refresh_reading(projected)
   self.assertNotIn('7 630',yaml.safe_load(projected['source/statut-evaluation.yaml'])['core']['text'])
   with self.assertRaises(ValueError):project_contracts(package,self.study,reg,docs,'Wrong validation')
   package['documents']['tools/validate_stacks.py']='unsafe'
   with self.assertRaises(ValueError):project_contracts(package,self.study,reg,docs,'Prepared package validation')

 def test_changed_proposal_is_validated_then_applied_only_in_its_isolated_copy(self):
  from adopt_core import template,prepare_adoption
  from core_adoption_reference import POINTER
  proposal=template(self.study);proposal['units']=proposal['units'][:1];row=proposal['units'][0]
  next(w for w in row['work'] if w['id']=='MD09')['jh']+=10;row['purpose_totals']['core-domain']+=10
  before=(ROOT/'source/estimations-core-retenues.yaml').read_bytes();result=prepare_adoption(proposal,'Test in isolated workspace only')
  self.assertEqual(result['summary']['delta_jh'],10);self.assertTrue(result['timings']['validation']>0);self.assertEqual((ROOT/'source/estimations-core-retenues.yaml').read_bytes(),before)
  plan,root=tx.load_plan(result['plan']);stage=Path(plan['validation']['workspace']);self.assertNotEqual(stage,ROOT)
  receipt=ROOT/'tmp/core-adoption-last-test.json';receipt.write_bytes(tx.encode(dict(summary=result['summary'],timings=result['timings'],plan=result['plan'],real_sources_unchanged=True)))
  changes={e['path']:base64.b64decode(e['after']) for e in plan['entries']}
  # Reset candidate files to their frozen before-images, without touching the real project.
  for e in plan['entries']:
   p=tx.target(stage,e['path'])
   if e['before'] is None:
    if p.exists():p.unlink()
   else:tx.atomic(p,base64.b64decode(e['before']))
  isolated=tx.create_plan(stage,changes,plan['inputs'],plan['summary'],plan['validation']);tx.apply(isolated)
  expected=load_reference(stage);self.assertEqual(expected['total_jh'],plan['summary']['total_jh']);self.assertEqual(expected['before']['parameters'],self.study.parameters)
  self.assertEqual((ROOT/'source/estimations-core-retenues.yaml').read_bytes(),before)

if __name__=='__main__':unittest.main()
