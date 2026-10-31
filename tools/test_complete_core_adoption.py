"""Adoption of the full Java/Spring scope: preserved decisions, unique funding and portable proofs."""
from collections import Counter
from copy import deepcopy
import base64,gzip,hashlib,json,unittest
from unittest.mock import patch
from validate_stacks import ROOT
from model_context import model_session
from estimation_inputs import registry,contract,load_proofs,validate_binding
from estimation_preparation import prepare
from estimation_calculation import calculate,formula,evaluate_rule
from estimation_components import unpack_archives
from retained_core import validate
from export_business_model import compose
from test_support import study_copy

class CompleteCoreAdoptionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with model_session() as snapshot:
   cls.units=validate()['units'];cls.registry=registry();cls.docs=load_proofs(cls.registry)
   cls.new=[u for u in cls.units if next(c for c in cls.registry['calculations'] if c['id']==u['calculation']['id'])['recipe']=='coherent_components_v1']
   cls.results={u['id']:calculate(u['calculation']) for u in cls.new}
   cls.bundle=compose(snapshot.documents,snapshot.digests)
 def test_prior_decisions_contracts_and_native_input_are_unchanged(self):
  baseline=json.loads((ROOT/'audits/2026-10-30-core-adoption-09/baseline.json').read_text(encoding='utf-8'))
  self.assertEqual(self.units[:3],baseline['units'])
  self.assertEqual(self.registry['calculations'][:3],baseline['calculations'])
  for p in ('source/referentiel-capacites.yaml','source/analyse-perimetre-core.yaml','sources/cartographie-scm-2026-10-24.yaml'):
   self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),baseline['source_hashes'][p])
 def test_global_roles_coverage_and_valuation_reconcile_without_common_surcharge(self):
  self.assertEqual(len(self.units),11);self.assertEqual(len(self.new),5)
  self.assertEqual(sum(u['total_jh'] for u in self.units),6660)
  self.assertEqual(sum(u['total_jh'] for u in self.new),1880)
  caps=[c['id'] for u in self.units for c in u['capabilities']]
  self.assertEqual(len(caps),len(set(caps)));self.assertEqual(set(caps),{f'BC-{n:03}' for n in range(1,89)})
  totals=Counter()
  for u in self.units:
   totals.update({r['id']:r['jh'] for r in u['roles']})
  self.assertEqual(totals,dict(coordination=747,analyse_produit=660,architecture=594,dev_java=2011,dev_frontend=903,qa=943,plateforme=508,ux=150,securite=144))
  study=study_copy();java=next(x for x in study._essential_core_evaluation() if x['stack']=='java-spring')
  self.assertEqual(java['estimation_status'],'fully_estimated')
  self.assertEqual((java['coverage']['covered'],java['coverage']['remaining']),(88,0))
  economic=study.content['stacks']['java-spring']['economic']
  self.assertEqual(economic['detail_build'],dict(prestations=4198680,pilotage=0))
  for u in self.new:
   result=self.results[u['id']]
   self.assertTrue(result['trace']['no_common_280_added'])
   self.assertEqual(sum(p['jh'] for p in result['trace']['component_allocations']),u['total_jh'])
   self.assertEqual((u['total_jh'],u['months']),(result['total_jh'],result['months']))
   self.assertEqual(result['consolidation']['schedule_aggregation'],'none')
 def test_initial_payload_keeps_summaries_and_calculations_keep_proofs_isolated(self):
  from estimation_inputs import _frozen_calculation_proofs,digest
  study=study_copy();summary=next(r for r in study.bootstrap(essential=True)['content']['core_evaluation'] if r['stack']=='java-spring')
  self.assertEqual(len(summary['units']),11)
  self.assertTrue(all(set(u)=={'id','label','total_jh','months','capabilities'} for u in summary['units']))
  self.assertEqual(sum(u['total_jh'] for u in summary['units']),6660)
  self.assertTrue(all('alignment' in u for u in study._essential_core_evaluation()[0]['units']))
  with model_session():
   reg=registry();before=digest(_frozen_calculation_proofs(reg))
   for u in self.units:calculate(u['calculation'])
   self.assertEqual(digest(_frozen_calculation_proofs(reg)),before)
   result=calculate(self.new[0]['calculation']);result['roles']['dev_java']=999999
   self.assertNotEqual(calculate(self.new[0]['calculation'])['roles']['dev_java'],999999)
 def test_each_of_seventy_new_mechanisms_is_funded_once(self):
  funded=Counter(x['mechanism'] for c in self.registry['calculations'] for x in c['funding_claims'] if x['mode']=='funded')
  new=[m for m in self.registry['mechanisms'] if m['id'].startswith('flow-')]
  self.assertEqual(len(new),70);self.assertTrue(all(funded[m['id']]==1 for m in new))
  for u in self.new:
   clone=deepcopy(u);clone['calculation']=self.new[0]['calculation'] if u!=self.new[0] else self.new[1]['calculation']
   with self.assertRaisesRegex(ValueError,'does not belong'):validate_binding(clone)
 def test_all_six_calculations_reconstruct_from_download_without_disk(self):
  bundle=self.bundle;reg=bundle['model']['source/calculs-estimation-core.yaml']
  rules={x['id']:x for x in bundle['metamodel']['estimation_model']['rules']}
  for u in self.new:
   spec=next(c for c in reg['calculations'] if c['id']==u['calculation']['id'])
   with self.subTest(unit=u['id']),patch('validate_stacks.read',side_effect=AssertionError('disk forbidden')):
    p=prepare(bundle['evidence'],spec,reg,lambda id,**v:evaluate_rule(rules[id],**v))
   expected=self.results[u['id']]
   self.assertEqual(p['trace']['CFP'],expected['trace']['CFP'])
   self.assertEqual(len(p['rows']),4)
   for row,retained in zip(p['rows'],expected['alignment']['rows']):
    self.assertAlmostEqual(row['jh'],retained['jh'])
    self.assertAlmostEqual(row['common_jh']+row['complements_jh'],row['jh'])
 def test_archives_preserve_original_bytes_and_integrity(self):
  spec=next(c for c in self.registry['calculations'] if c['id']==self.new[0]['calculation']['id'])
  archive=self.docs[spec['inputs']['archives']]
  self.assertEqual(len(unpack_archives(archive)),6)
  for entry in archive['documents'].values():
   raw=gzip.decompress(base64.b64decode(entry['data']))
   self.assertEqual(raw,(ROOT/entry['path']).read_bytes())
  bad=deepcopy(archive);bad['documents']['proposal_inputs']['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'Archived evidence changed'):unpack_archives(bad)
 def test_module_scope_and_duplicate_atoms_cannot_silently_change_cost(self):
  spec=next(c for c in self.registry['calculations'] if c['id']==self.new[0]['calculation']['id'])
  for mutate in (
   lambda d:d['families'][0].update(quantity=999),
   lambda d:d['families'][0]['bindings'][0]['atoms'].append(deepcopy(d['families'][0]['bindings'][0]['atoms'][0])),
   lambda d:d['families'][0].update(extension_fraction=999),
  ):
   docs=deepcopy(self.docs);archive=docs[spec['inputs']['archives']];entry=archive['documents']['proposal_inputs']
   inputs=json.loads(gzip.decompress(base64.b64decode(entry['data'])));mutate(inputs)
   raw=json.dumps(inputs,ensure_ascii=False).encode();entry.update(sha256=hashlib.sha256(raw).hexdigest(),data=base64.b64encode(gzip.compress(raw,mtime=0)).decode())
   with model_session(),self.assertRaises(ValueError):prepare(docs,spec,self.registry,formula)
 def test_bad_functional_boundary_or_reuse_is_rejected(self):
  spec=next(c for c in self.registry['calculations'] if c['id']==self.new[0]['calculation']['id'])
  for key,mutate in (
   ('cosmic',lambda d:d['processes'][0]['movements'].append(deepcopy(d['processes'][0]['movements'][0]))),
   ('cosmic',lambda d:d['processes'][0]['movements'][0].update(group='unknown')),
   ('cosmic',lambda d:d.update(factor=.8)),
   ('specification',lambda d:d['reused_mechanisms'].pop()),
   ('specification',lambda d:d.update(group_id='orders')),
  ):
   docs=deepcopy(self.docs);mutate(docs[spec['inputs'][key]])
   with model_session(),self.assertRaises(ValueError):prepare(docs,spec,self.registry,formula)

if __name__=='__main__':unittest.main()
