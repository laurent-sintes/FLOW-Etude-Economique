"""Automation must fail closed and retain test failures in usable reports."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
from validation_changes import classify, editorial_change, plan
from validation_reporting import TimedResult, save_report, run_directory
from validate_stacks import ROOT


class ValidationAutomationTests(unittest.TestCase):
    def test_only_existing_editorial_fields_and_css_can_reduce_checks(self):
        before = {'format':1, 'files':{'source/a.yaml':{'sha256':'a','document':{'title':'old','rate':1}}}}
        after = {'format':1, 'files':{'source/a.yaml':{'sha256':'b','document':{'title':'new','rate':1}}}}
        self.assertEqual(classify(before,after)['mode'],'presentation')
        after['files']['source/a.yaml']['document']['rate']=2
        self.assertEqual(classify(before,after)['mode'],'full')
        self.assertEqual(classify(before,{'files':{}})['mode'],'full')
        self.assertFalse(editorial_change({'estimation_model':{'title':'a'}},{'estimation_model':{'title':'b'}}))
        self.assertFalse(editorial_change({'title':'a'},{'title':'a','note':'b'}))
        self.assertFalse(editorial_change({'unknown':'a'},{'unknown':'b'}))
        self.assertEqual(classify({'files':{'app/src/a.css':{'sha256':'a'}}},{'files':{'app/src/a.css':{'sha256':'b'}}})['mode'],'presentation')
        self.assertEqual(classify({'files':{'app/src/a.tsx':{'sha256':'a'}}},{'files':{'app/src/a.tsx':{'sha256':'b'}}})['mode'],'presentation')
        self.assertEqual(classify({'files':{'tools/a.py':{'sha256':'a'}}},{'files':{'tools/a.py':{'sha256':'b'}}})['mode'],'full')

    def test_absent_or_invalid_full_baseline_requires_full_validation(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as folder:
            root=Path(folder)
            self.assertEqual(plan(root)['mode'],'full')
            (root/'tmp').mkdir()
            (root/'tmp/validation-full-manifest.json').write_text('{}')
            self.assertEqual(plan(root)['mode'],'full')

    def test_failed_subtests_errors_and_skips_have_json_and_junit(self):
        class Fixture(unittest.TestCase):
            def test_failure(self):
                with self.subTest(case='bad'):self.fail('expected fixture failure')
            def test_error(self):raise ValueError('expected fixture error')
            @unittest.skip('expected fixture skip')
            def test_skip(self):pass
        result=unittest.TextTestRunner(stream=io.StringIO(),resultclass=TimedResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(Fixture))
        self.assertFalse(result.wasSuccessful())
        self.assertEqual({r['status'] for r in result.records},{'error','failure','skipped'})
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as folder:
            root=Path(folder)
            directory=run_directory(root)
            report={'status':'failed','test_results':result.records,'error':'pipeline failed'}
            save_report(report,directory,root/'tmp/last.json')
            self.assertEqual(json.loads((root/'tmp/last.json').read_text(encoding='utf-8')),report)
            xml=ET.parse(directory/'junit.xml').getroot()
            self.assertEqual(xml.get('failures'),'1')
            self.assertEqual(xml.get('errors'),'2')
            self.assertEqual(xml.get('tests'),'4')

    def test_pipeline_errors_still_save_report_and_stage_duration(self):
        import check_model
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as folder:
            root=Path(folder)
            with patch.object(check_model,'ROOT',root), patch('sys.argv',['check_model','--content']), \
                 patch('validation_changes.snapshot',return_value={'files':{}}), \
                 patch.object(check_model,'content_only',side_effect=ValueError('expected pipeline error')), \
                 patch('sys.stdout',io.StringIO()), patch('sys.stderr',io.StringIO()):
                self.assertEqual(check_model.main(),1)
            report=json.loads((root/'tmp/check-model-last.json').read_text(encoding='utf-8'))
            self.assertEqual(report['status'],'failed')
            self.assertIn('editorial',report['stages'])
            self.assertIn('expected pipeline error',report['error'])

    def test_manifest_roundtrip_keeps_numeric_yaml_keys_unchanged(self):
        current={'files':{'source/a.yaml':{'sha256':'identical','document':{'levels':{1:'low',2:'high'}}}}}
        persisted=json.loads(json.dumps(current))
        self.assertEqual(classify(persisted,current)['changes'],[])
        self.assertEqual(classify(persisted,current)['mode'],'presentation')
        self.assertFalse(editorial_change({'value':1},{'value':True}))
        self.assertFalse(editorial_change({'value':1},{'value':1.0}))
