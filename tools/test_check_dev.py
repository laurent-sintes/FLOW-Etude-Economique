"""The development selector must stay targeted and never certify a full run."""
from pathlib import Path
import tempfile
import unittest
from check_dev import impacted_tests, plan


class DevSelectionTests(unittest.TestCase):
    def test_css_and_docs_do_not_load_model_or_frontend_suite(self):
        selection = plan(Path('.'), ['app/src/style.css', 'AGENTS.md'])
        self.assertFalse(selection['frontend'])
        self.assertFalse(selection['content'])
        self.assertEqual(selection['python_tests'], [])
        self.assertFalse(selection['certification'])

    def test_typescript_checks_frontend_without_python(self):
        selection = plan(Path('.'), ['app/src/App.tsx'])
        self.assertTrue(selection['frontend'])
        self.assertEqual(selection['python_tests'], [])

    def test_python_dependencies_include_indirect_and_function_imports(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'tools').mkdir()
            for name, code in {'engine': '', 'adapter': 'def run():\n import engine',
                               'test_adapter': 'from tools import adapter', 'test_other': 'import os'}.items():
                (root / 'tools' / (name + '.py')).write_text(code)
            self.assertEqual(impacted_tests(root, ['tools/engine.py']), ['test_adapter'])
            self.assertEqual(impacted_tests(root, ['tools/test_other.py']), ['test_other'])

    def test_unknown_change_is_reported_without_falling_back_to_full(self):
        selection = plan(Path('.'), ['app/package-lock.json'])
        self.assertEqual(selection['unresolved'], ['app/package-lock.json'])
        self.assertNotIn('full', selection.values())

    def test_model_changes_keep_contract_and_financial_tests(self):
        selection = plan(Path('.'), ['source/fondamentaux.yaml'])
        self.assertTrue(selection['content'])
        self.assertIn('test_business_contract', selection['python_tests'])
        self.assertIn('test_composable_costs', selection['python_tests'])

    def test_unknown_change_can_have_explicit_targeted_tests(self):
        selection = plan(Path('.'), ['app/package-lock.json'], ['test_check_dev'])
        self.assertEqual(selection['unresolved'], [])
        self.assertEqual(selection['python_tests'], ['test_check_dev'])

    def test_explicit_targeting_keeps_source_contracts_without_import_expansion(self):
        from unittest.mock import patch
        with patch('check_dev.impacted_tests', side_effect=AssertionError('No import expansion')):
            selection = plan(Path('.'), ['tools/engine.py', 'source/rates.yaml'], ['test_work_package_adoption'], targeted=True)
        self.assertIn('test_work_package_adoption', selection['python_tests'])
        self.assertIn('test_business_contract', selection['python_tests'])
        self.assertIn('test_composable_costs', selection['python_tests'])
        self.assertFalse(selection['certification'])
        self.assertEqual(selection['unresolved'], [])
        self.assertTrue(plan(Path('.'), ['tools/engine.py'], targeted=True)['unresolved'])

    def test_selected_module_or_class_does_not_repeat_its_named_methods(self):
        selection = plan(Path('.'), [], ['test_a', 'test_a.Case.test_one', 'test_b.Case', 'test_b.Case.test_two', 'test_c.Case.test_three'])
        self.assertEqual(selection['python_tests'], ['test_a', 'test_b.Case', 'test_c.Case.test_three'])

    def test_failed_run_saves_report_without_full_validation_receipt(self):
        import io
        import json
        from unittest.mock import patch
        import check_dev
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'tmp').mkdir()
            receipt = root / 'tmp/validation-full-manifest.json'
            receipt.write_text('unchanged full proof')
            with patch.object(check_dev, 'ROOT', root), patch('sys.stdout', io.StringIO()), \
                 patch('sys.argv', ['check_dev', '--paths', 'unknown.bin']):
                self.assertEqual(check_dev.main(), 1)
            report = json.loads((root / 'tmp/check-dev-last.json').read_text())
            self.assertEqual(report['status'], 'failed')
            self.assertFalse(report['certification'])
            self.assertEqual(receipt.read_text(), 'unchanged full proof')
