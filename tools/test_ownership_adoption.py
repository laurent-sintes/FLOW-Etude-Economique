"""Adopted Ownership: independent funding, pure reconstruction, temporal count and export."""
from copy import deepcopy
import hashlib,json
import unittest
from unittest.mock import patch
from model_context import model_session
from estimation_inputs import contract,load_proofs,registry,validate_binding,validate_funding
from estimation_preparation import prepare
from estimation_calculation import formula,evaluate_rule,calculate
from retained_core import validate
from export_business_model import compose
from validate_stacks import ROOT
from test_support import study_copy

class OwnershipAdoptionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with model_session() as snapshot:
   cls.units=validate()['units'];cls.unit=next(u for u in cls.units if u['id']=='inventory-ownership-java-spring')
   cls.spec,cls.registry=contract(cls.unit['calculation']);cls.docs=load_proofs(cls.registry)
   cls.result=calculate(cls.unit['calculation']);cls.bundle=compose(snapshot.documents,snapshot.digests)
 def prepared(self,change=None):
  docs=deepcopy(self.docs);views={k:docs[p] for k,p in self.spec['inputs'].items()}
  if change:change(views,docs)
  with model_session():return prepare(docs,self.spec,self.registry,formula)
 def test_adopted_roles_schedule_and_prior_families(self):
  before=json.loads((ROOT/'audits/2026-10-30-propriete-stock-adoption-05/baseline.json').read_text(encoding='utf-8'))
  self.assertEqual(self.units[:2],before['retained_units'])
  self.assertEqual((self.result['total_jh'],self.result['months']),(100,7))
  self.assertEqual(self.result['roles'],dict(coordination=11,analyse_produit=10,architecture=9,dev_java=37,dev_frontend=6,qa=14,plateforme=9,ux=2,securite=2))
  self.assertAlmostEqual(self.result['unrounded_months'],7.072892092893779)
  for p in ('source/referentiel-capacites.yaml','sources/cartographie-scm-2026-10-24.yaml'):
   self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),before['file_hashes'][p])
 def test_native_new_sizes_and_COSMIC_reconstructed(self):
  p=self.prepared()
  for row in p['rows']:
   self.assertEqual(row['common_jh'],0)
   self.assertEqual(row['complements_jh'],row['jh'])
  self.assertAlmostEqual(p['rows'][3]['jh'],98.9157173042935)
  self.assertAlmostEqual(p['trace']['complement_units'],1281.05)
  self.assertEqual((p['trace']['CFP'],p['trace']['processes'],p['trace']['groups']),(80,9,21))
  self.assertEqual(p['trace']['movements'],dict(E=9,R=35,W=15,X=21))
  self.assertAlmostEqual(self.result['alignment']['functional']['jh'],80*20/7)
  self.assertAlmostEqual(self.result['alignment']['functional']['gap_pct'],131.0769560193113)
 def test_export_reconstructs_without_disk_or_OSS_checkout(self):
  b=self.bundle;reg=b['model']['source/calculs-estimation-core.yaml']
  spec=next(c for c in reg['calculations'] if c['id']==self.unit['calculation']['id'])
  rules={r['id']:r for r in b['metamodel']['estimation_model']['rules']}
  with patch('validate_stacks.read',side_effect=AssertionError('disk forbidden')):
   p=prepare(b['evidence'],spec,reg,lambda id,**v:evaluate_rule(rules[id],**v))
  self.assertEqual(p['trace']['CFP'],80)
  self.assertAlmostEqual(p['rows'][3]['jh'],98.9157173042935)
 def test_aggregate_coverage_and_consumed_owners(self):
  study=study_copy();core=study.content['stacks']['java-spring']['economic']
  self.assertEqual(core['jh']['core_project_roles_jh'],6660)
  family=next(u for u in core['core_units'] if u['id']==self.unit['id'])
  self.assertEqual((family['labour_eur_ht'],family['tooling_eur_ht']),(62150,800))
  consumed=[m for m in family['funding'] if m['funding_mode']=='consumed']
  self.assertEqual({m['funding_owner'] for m in consumed},{'master-data-java-spring','stock-java-spring'})
  self.assertTrue(all(m['funding_owner_label'] for m in consumed))
  self.assertEqual(len([m for m in family['funding'] if m['funding_mode']=='funded']),6)
  self.assertIsNone(family['uncertainty']['confidence_level'])
  coverage=next(r for r in study._essential_core_evaluation() if r['stack']=='java-spring')['coverage']
  self.assertEqual((coverage['covered'],coverage['remaining']),(88,0))
 def test_funding_and_cross_family_binding_rejected(self):
  doc=registry();own=next(c for c in doc['calculations'] if c['id']==self.spec['id'])
  next(c for c in own['funding_claims'] if c['mode']=='consumed')['mode']='funded'
  with self.assertRaisesRegex(ValueError,'already owned'):registry(doc)
  with self.assertRaisesRegex(ValueError,'no adopted funding owner'):validate_funding([self.unit])
  u=deepcopy(self.unit);u['calculation']={'id':'stock-java-spring-v1'}
  with self.assertRaisesRegex(ValueError,'does not belong'):validate_binding(u)
 def test_changed_analogues_hypotheses_or_temporal_counts_rejected(self):
  changes=[
   lambda v,d:v['specification'].update(analogue_contract_sha256='0'*64),
   lambda v,d:v['native_inputs']['banks']['axelor']['central']['correction_chain'].update(program_units=1),
   lambda v,d:v['native_inputs']['hypotheses']['modules'][0].update(central=999),
   lambda v,d:v['native_inputs']['hypotheses']['schemas'][0]['fields'].append(v['native_inputs']['hypotheses']['schemas'][0]['fields'][0]),
   lambda v,d:v['allocation']['activity_role_weights']['implementation'].update(dev_java=.9),
   lambda v,d:v['cosmic_refinement']['add_movements'].pop(),
   lambda v,d:v['cosmic']['processes'][0]['movements'].append(deepcopy(v['cosmic']['processes'][0]['movements'][0])),
   lambda v,d:v['cosmic']['productivity'].update(day_hours=8),
   lambda v,d:v['specification']['reused_mechanisms'].pop(),
  ]
  for n,change in enumerate(changes):
   with self.subTest(change=n),self.assertRaises(ValueError):self.prepared(change)
if __name__=='__main__':unittest.main()
