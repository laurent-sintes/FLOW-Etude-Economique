from copy import deepcopy
import unittest
from integration_units import compile_units,estimate,ROLES
class IntegrationUnitsTests(unittest.TestCase):
 def test_dimensioning_and_funding_guards(self):
  d=compile_units();self.assertEqual(len(d['units']),26)
  self.assertTrue(all(o['estimate']['total_jh'] is None for u in d['units'] for o in u['options'].values()))
  setup=dict.fromkeys(ROLES,0);unit=dict.fromkeys(ROLES,0);setup['integration']=3;unit['integration']=4
  self.assertEqual(estimate(2,setup,unit)['total_jh'],11)
  self.assertIsNone(estimate(None,setup,unit)['total_jh'])
  for bad in (True,-1,float('nan'),float('inf')):
   with self.assertRaises(ValueError):estimate(bad,setup,unit)
  self.assertEqual(estimate(0,setup,unit)['total_jh'],3)
 def test_contract_rejects_false_precision_and_wrong_funding(self):
  from validate_stacks import ROOT,read
  from integration_units import SOURCE
  original=read(ROOT/SOURCE)
  for mutation in ('duplicate','option','quantity','funding','included','effort','scenario','extra'):
   d=deepcopy(original);u=d['units'][0];o=u['options']['microsoft']
   if mutation=='duplicate':d['units'].append(deepcopy(u))
   if mutation=='option':del u['options']['sap']
   if mutation=='quantity':u['quantity']=2
   if mutation=='funding':o['funding_group']='make-common'
   if mutation=='included':o['inclusion']='inclus_documente';o['estimate_basis']=None
   if mutation=='effort':o['unit_jh']['integration']=4;o['estimate_basis']=None
   if mutation=='scenario':u['scenario_refs']=['invented']
   if mutation=='extra':u['invented_budget']=100
   with self.subTest(mutation=mutation),self.assertRaises(ValueError):compile_units(d)
 def test_deployment_and_shared_packages_are_not_duplicated(self):
  d=compile_units();groups={o['funding_group'] for u in d['units'] for o in u['options'].values()}
  self.assertEqual(groups,set(d['funding_groups']))
  self.assertEqual(len(groups),4)
  for u in d['units']:
   if u['activity_ref'] in ('INT-012','INT-013'):self.assertEqual(u['options']['java-spring']['funding_group'],'make-deployment')
  self.assertFalse(any('amount' in g for g in d['funding_groups'].values()))

 def test_reconciliation_rejects_cross_option_and_invented_active_values(self):
  from validate_stacks import ROOT,read
  from integration_units import SOURCE
  original=read(ROOT/SOURCE)
  for mutation in ('cross','missing','range','active'):
   d=deepcopy(original)
   if mutation=='cross':d['units'][0]['options']['sap']['reconciliation']['package_refs']=['ms-standard']
   if mutation=='missing':d['units'][0]['options']['sap']['reconciliation']['package_refs']=['invented']
   if mutation=='range':d['packages']['ms-standard']['measures'][0]['high']=1
   if mutation=='active':d['packages']['make-INT-006']['measures']=[dict(label='invented',low=300,high=300,unit='JH')]
   with self.subTest(mutation=mutation),self.assertRaises(ValueError):compile_units(d)
 def test_active_work_projection_does_not_allocate_or_mutate_shared_packages(self):
  from integration_units import attach_active_work
  d=compile_units();ids=[p['work_ref'] for p in d['packages'].values() if p['kind']=='make_activity']
  groups=[dict(id='common',rows=[dict(id=k,label=k,value=537 if k=='INT-006' else 1) for k in ids]),dict(id='deployment',rows=[dict(label='A',value=333),dict(label='B',value=222)])]
  before=deepcopy(groups);result=attach_active_work(d,groups)
  self.assertEqual(groups,before)
  self.assertEqual(d['packages']['make-INT-006']['measures'],[])
  self.assertEqual(result['packages']['make-INT-006']['measures'][0]['low'],537)
  self.assertEqual([m['low'] for m in result['packages']['make-deployment']['measures']],[333,222])
  self.assertEqual(result['packages']['sap-training']['measures'][0]['low'],0)
  training=next(u for u in result['units'] if u['id']=='training')
  self.assertEqual(training['options']['sap']['inclusion'],'a_rapprocher')
  self.assertIsNone(training['options']['sap']['estimate']['total_jh'])
  self.assertEqual(result['packages']['ms-standard']['measures'][0]['low'],520)
  self.assertFalse('total_jh' in result)
