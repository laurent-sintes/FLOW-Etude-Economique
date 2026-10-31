"""Stock adoption: pure reconstruction, reuse ownership, rejection and export."""
from copy import deepcopy
import hashlib
import unittest
from unittest.mock import patch
from model_context import model_session
from estimation_inputs import contract,load_proofs,validate_binding,registry,validate_funding
from estimation_calculation import formula,evaluate_rule,calculate
from estimation_preparation import prepare
from retained_core import validate
from export_business_model import compose
from validate_stacks import ROOT,read
from test_support import study_copy

class StockAdoptionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with model_session() as snapshot:
   cls.units=validate()['units'];cls.unit=next(u for u in cls.units if u['id']=='stock-java-spring')
   cls.spec,cls.registry=contract(cls.unit['calculation']);cls.proofs=load_proofs(cls.registry)
   cls.result=calculate(cls.unit['calculation']);cls.bundle=compose(snapshot.documents,snapshot.digests)
 def prepared(self,change=None):
  docs=deepcopy(self.proofs);views={k:docs[p] for k,p in self.spec['inputs'].items()}
  if change:change(views,docs)
  with model_session():return prepare(docs,self.spec,self.registry,formula)
 def test_decisions_roles_scope_and_cost(self):
  md=next(u for u in self.units if u['id']=='master-data-java-spring')
  self.assertEqual((md['total_jh'],md['months']),(1500,17))
  r=self.result;self.assertEqual((r['total_jh'],r['months']),(340,10))
  self.assertEqual(r['roles'],dict(coordination=40,analyse_produit=35,architecture=30,dev_java=125,dev_frontend=20,qa=50,plateforme=30,ux=5,securite=5))
  self.assertAlmostEqual(r['unrounded_months'],10.436994130535364)
  study=study_copy();core=study.content['stacks']['java-spring']['economic']
  self.assertEqual(core['jh']['core_project_roles_jh'],6660)
  self.assertEqual(core['detail_build']['prestations'],4198680)
  stock=next(u for u in core['core_units'] if u['id']=='stock-java-spring')
  self.assertEqual((stock['labour_eur_ht'],stock['tooling_eur_ht']),(211250,2720))
  covered=next(x for x in study._essential_core_evaluation() if x['stack']=='java-spring')['coverage']
  self.assertEqual((covered['covered'],covered['remaining']),(88,0))
 def test_native_sizes_and_functional_count_reconstructed(self):
  p=self.prepared();self.assertEqual((p['trace']['component_files'],p['trace']['recorded_files']),(62,63))
  self.assertEqual((p['trace']['CFP'],p['trace']['processes'],p['trace']['groups']),(169,21,20))
  rows={r['id']:r for r in p['rows']}
  for k,v in dict(erpnext=318.17039662584926,odoo=534.2250939927217,tryton=318.3495261820652,axelor=339.0185977157613).items():
   self.assertAlmostEqual(rows[k]['jh'],v)
   self.assertAlmostEqual(rows[k]['common_jh']+rows[k]['complements_jh'],v)
  self.assertAlmostEqual(p['trace']['complement_units'],1498.97)
  a=self.result['alignment'];self.assertAlmostEqual(a['functional']['jh'],169*20/7)
  self.assertAlmostEqual(a['functional']['gap_pct'],42.42792168646102)
 def test_download_reconstructs_stock_without_disk_or_checkout(self):
  b=self.bundle;reg=b['model']['source/calculs-estimation-core.yaml'];rules={r['id']:r for r in b['metamodel']['estimation_model']['rules']}
  spec=next(c for c in reg['calculations'] if c['id']=='stock-java-spring-v1')
  with patch('validate_stacks.read',side_effect=AssertionError('disk forbidden')):
   p=prepare(b['evidence'],spec,reg,lambda id,**v:evaluate_rule(rules[id],**v))
  self.assertAlmostEqual(p['rows'][3]['jh'],339.0185977157613)
  self.assertEqual(p['trace']['CFP'],169)
 def test_master_data_source_and_decision_unchanged(self):
  import json
  before=json.loads((ROOT/'audits/2026-10-30-stock-adoption-10/baseline.json').read_text(encoding='utf-8'))
  self.assertEqual(self.units[0],before['retained_master_data'])
  for path,key in [('sources/cartographie-scm-2026-10-24.yaml','capability_source_sha256'),('source/referentiel-capacites.yaml','capability_reference_sha256')]:
   self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),before[key])
 def test_stock_cannot_claim_master_data_funding_or_drop_owner(self):
  doc=registry();stock=next(c for c in doc['calculations'] if c['unit_id']=='stock-java-spring')
  next(c for c in stock['funding_claims'] if c['mode']=='consumed')['mode']='funded'
  with self.assertRaisesRegex(ValueError,'already owned'):registry(doc)
  with self.assertRaisesRegex(ValueError,'no adopted funding owner'):validate_funding([self.unit])
  unit=deepcopy(self.unit);unit['calculation']={'id':'master-data-java-spring-v1'}
  with self.assertRaisesRegex(ValueError,'does not belong'):validate_binding(unit)
 def test_mutated_measures_hypotheses_and_counts_rejected(self):
  changes=[
   lambda v,d:v['native_inputs']['attributions'][0]['attribution'].update(central=-.1),
   lambda v,d:v['native_inputs']['attributions'][0].update(available_declarative=999),
   lambda v,d:v['native_inputs']['attributions'].append(deepcopy(v['native_inputs']['attributions'][0])),
   lambda v,d:v['native_inputs']['complement_module_analogies'][0].update(central=999),
   lambda v,d:v['native_inputs']['attributions'][0].update(additional_framework_assimilation=.1),
   lambda v,d:v['allocation']['activity_role_weights']['implementation'].update(dev_java=.9),
   lambda v,d:v['native_measures']['files'][0]['nodes'].pop(),
   lambda v,d:v['cosmic']['processes'][0]['movements'].append(deepcopy(v['cosmic']['processes'][0]['movements'][0])),
   lambda v,d:v['cosmic']['processes'][0]['count'].update(CFP=999),
   lambda v,d:v['cosmic']['result'].update(day_hours=8),
  ]
  for n,change in enumerate(changes):
   with self.subTest(change=n),self.assertRaises(ValueError):self.prepared(change)
 def test_shared_services_display_owner_and_nonprobabilistic_alignment(self):
  stock=next(u for u in study_copy().content['stacks']['java-spring']['economic']['core_units'] if u['id']=='stock-java-spring')
  consumed=[m for m in stock['funding'] if m['funding_mode']=='consumed']
  self.assertEqual(len(consumed),7)
  self.assertTrue(all(m['funding_owner']=='master-data-java-spring' and m['funding_owner_label']=='Master Data Java/Spring' for m in consumed))
  self.assertIsNone(stock['uncertainty']['confidence_level'])
  self.assertFalse(stock['consolidation']['integrated_core_estimate'])
  self.assertEqual(stock['consolidation']['schedule_aggregation'],'none')

if __name__=='__main__':unittest.main()
