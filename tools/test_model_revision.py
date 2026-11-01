"""Human revision identity and monotonic increments without changing calculation contracts."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
import yaml
from model_revision import validate_revision, next_revision, bump

class ModelRevisionTests(unittest.TestCase):
 def test_strict_identity_rejects_invalid_dates_numbers_and_fields(self):
  valid=dict(format_version=1,date='2026-11-01',number=1)
  self.assertEqual(validate_revision(valid),dict(date='2026-11-01',number=1))
  for change in [dict(format_version=True),dict(date='2026-02-30'),dict(date='2026-1-1'),dict(date=123),dict(number=0),dict(number=True),dict(number=1.5),dict(extra=1)]:
   with self.subTest(change=change),self.assertRaises(ValueError):validate_revision({**valid,**change})
 def test_counter_increases_across_days_without_reset_or_source_mutation(self):
  current=dict(format_version=1,date='2026-11-01',number=17);before=deepcopy(current)
  self.assertEqual(next_revision(current,'2026-11-01'),dict(format_version=1,date='2026-11-01',number=18))
  self.assertEqual(next_revision(current,'2026-11-02'),dict(format_version=1,date='2026-11-02',number=18))
  self.assertEqual(current,before)
  with self.assertRaisesRegex(ValueError,'BACKDATE'):next_revision(current,'2026-10-31')
 def test_explicit_bump_persists_successive_numbers_and_invalid_bump_keeps_original(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'version.yaml';path.write_text("format_version: 1\ndate: '2026-11-01'\nnumber: 1\n",encoding='utf8')
   self.assertEqual(bump(path,'2026-11-01')['number'],2)
   self.assertEqual(bump(path,'2026-11-02')['number'],3)
   before=path.read_bytes()
   with self.assertRaises(ValueError):bump(path,'2026-10-31')
   self.assertEqual(path.read_bytes(),before)
   self.assertEqual(yaml.safe_load(path.read_text('utf8'))['number'],3)
 def test_loaded_and_frozen_versions_match_without_reloading_a_source(self):
  from test_support import reference_study
  from study_snapshot import candidate
  from study_app import Study
  from unittest.mock import patch
  study=reference_study();bundle=candidate(study)
  with patch('study_app.read',side_effect=AssertionError('Unexpected source read')):
   restored=Study.from_release(bundle)
  self.assertEqual(restored.bootstrap(essential=True)['model_revision'],study.model_revision)
  self.assertEqual(restored.baseline,study.baseline)
  self.assertEqual(restored.simulation_contract(),study.simulation_contract())
