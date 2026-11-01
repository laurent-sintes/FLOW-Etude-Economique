"""Targeted checks for the separate proposal, without loading or rebuilding the app."""
from pathlib import Path
import unittest,json,hashlib,math
from validate_stacks import read
from estimation_calculation import formula,rounded
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def load(name):return json.loads((P/name).read_text(encoding='utf-8'))
class ProposalTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.result=load('results.json');cls.hypotheses=load('hypotheses.json');cls.audit=json.loads((ROOT/cls.hypotheses['baseline']).read_text(encoding='utf-8'))
 def test_total_and_deltas_reconcile_without_adoption(self):
  r=self.result;self.assertEqual(r['status'],'proposal_not_adopted');self.assertEqual(sum(u['adopted_jh'] for u in r['units']),6660)
  self.assertEqual(sum(u['proposal_jh'] for u in r['units']),r['proposal_jh']);self.assertEqual(sum(u['delta_jh'] for u in r['units']),r['proposal_jh']-6660)
 def test_scope_and_funding_owners_are_preserved(self):
  active=read(ROOT/'source/estimations-core-retenues.yaml')['units'];proposed={u['id']:u for u in self.result['units']}
  self.assertEqual(set(proposed),{u['id'] for u in active})
  for u in active:
   self.assertEqual(proposed[u['id']]['capabilities'],u['capabilities']);self.assertEqual(proposed[u['id']]['professional_functions'],u.get('professional_functions',[]))
  caps=[c['id'] for u in proposed.values() for c in u['capabilities']];self.assertEqual(len(caps),88);self.assertEqual(len(set(caps)),88)
  funded=[c['mechanism'] for c in self.result['funding_claims'] if c['mode']=='funded'];self.assertEqual(len(funded),len(set(funded)))
 def test_calculation_inputs_and_adopted_units_unchanged(self):
  for path,expected in load('calculation-inputs-protected.json').items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),expected,path)
  active={u['id']:u['total_jh'] for u in read(ROOT/'source/estimations-core-retenues.yaml')['units']}
  for u in self.result['units']:self.assertEqual(u['adopted_jh'],active[u['id']])
 def test_hypotheses_and_audit_provenance_are_exact(self):
  for path,expected in self.result['inputs_sha256'].items():
   source=P/path if path=='hypotheses.json' else ROOT/path
   self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),expected,path)
 def test_measured_banks_reconcile_to_unique_frozen_atoms(self):
  for name,bank in self.result['measured_analogue_selections'].items():
   keys=[(f['repo'],f['path'],a) for f in bank['files'] for a in f['atoms']]
   self.assertEqual(len(keys),len(set(keys)),name);self.assertEqual(len(keys),bank['units'],name)
   self.assertEqual(sum(sum(f['methods'].values()) for f in bank['files']),bank['units'],name)
 def test_java_fixed_parts_and_new_behaviour_reconcile(self):
  for u in self.result['units']:
   parts=u['calculation_details'].get('families',[])
   if not parts:continue
   for f in parts:
    expected=f['java_fixed_size']+f['new_bank']*f['equivalence_factor']*f['fraction']*f['module_count']
    self.assertGreaterEqual(f['java_fixed_size'],0);self.assertAlmostEqual(expected,f['candidate_size'],places=8)
   self.assertAlmostEqual(sum(f['candidate_size'] for f in parts),u['equivalent_units'],places=8)
 def test_each_changed_lot_uses_one_canonical_cocomo_calculation(self):
  originals={u['id']:u for u in self.audit['units']}
  for u in self.result['units']:
   if u['equivalent_units'] is None:
    self.assertEqual(u['proposal_jh'],u['adopted_jh']);continue
   c=originals[u['id']]['cocomo'];exponent=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum'])
   raw=formula('cocomo_effort',A=c['A'],KSLOC=u['equivalent_units']/1000,E=exponent,EM=c['other_EM'],SCED=c['SCED'],month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor'])
   self.assertAlmostEqual(raw,u['raw_proposal_jh'],places=8);self.assertEqual(rounded(raw,u['rounding_jh']),u['proposal_jh'])
 def test_scope_filters_include_assignment_and_exclude_external_engines(self):
  banks=self.result['measured_analogue_selections'];allocation={m for f in banks['allocation']['files'] for m in f['methods']}
  self.assertTrue({'allocate_serial_batch_qty','set_reserved_serial_batch_entries'}<=allocation)
  forbidden={'make_gl_entries','make_pos_gl_entries','get_gl_entries','get_sub_assembly_items','make_work_order','get_directions','process_route'}
  for bank in banks.values():self.assertFalse(forbidden&{m for f in bank['files'] for m in f['methods']})
  sensitivity=[s for s in self.result['sensitivity'] if s['id']=='new_foreign_analogue_units'];self.assertLessEqual(sensitivity[0]['total_jh'],self.result['proposal_jh']);self.assertGreaterEqual(sensitivity[1]['total_jh'],self.result['proposal_jh'])
if __name__=='__main__':unittest.main()
