"""Explicit, targeted development checks. Never issues a full validation receipt."""
import argparse
import ast
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))


def impacted_tests(root, paths):
    """Follow Python imports transitively, including imports inside functions."""
    modules = {p.stem: p for p in (root / 'tools').glob('*.py')}
    dependencies = {}
    for name, path in modules.items():
        tree = ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.removeprefix('tools.').split('.')[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.removeprefix('tools.').split('.')[0])
                if node.module == 'tools':
                    imports.update(alias.name for alias in node.names)
        dependencies[name] = imports
    affected = {Path(p).stem for p in paths if p.startswith('tools/') and p.endswith('.py')}
    while True:
        expanded = affected | {name for name, deps in dependencies.items() if deps & affected}
        if expanded == affected:
            break
        affected = expanded
    return sorted(name for name in affected if name.startswith('test_') and name in modules)


def plan(root, paths, extra_tests=(), targeted=False):
    selected = set(extra_tests)
    unresolved = []
    if targeted and not extra_tests:
        unresolved.append("Explicit --tests required with --targeted")
    frontend = False
    content = False
    for name in paths:
        path = Path(name)
        if name.startswith('tools/') and path.suffix == '.py':
            tests = [] if targeted else impacted_tests(root, [name])
            selected.update(tests)
            if not tests and not extra_tests:
                unresolved.append(name)
        elif name.startswith('app/src/') and path.suffix in {'.css', '.ts', '.tsx'}:
            frontend |= path.suffix != '.css'
        elif name.startswith('app/scripts/') and path.name.startswith('test-') and path.suffix == '.mjs':
            frontend = True
        elif name.startswith(('source/', 'config/')):
            content = True
            # Shared financial/input invariants, without HTTP, release or browser suites.
            selected.update(['test_model_inputs', 'test_cost_separation', 'test_composable_costs',
                             'test_estimation_calculation', 'test_business_contract'])
        elif path.suffix.lower() in {'.md', '.css', '.svg', '.png', '.jpg', '.ico'}:
            pass
        elif not extra_tests:
            unresolved.append(name)
    # A selected module/class already includes its named methods. Run each test once.
    selected = {name for name in selected if not any(name.startswith(parent + '.') for parent in selected if parent != name)}
    return dict(paths=paths, python_tests=sorted(selected), frontend=frontend, content=content,
                selection_mode='explicit' if targeted else 'transitive',
                unresolved=unresolved, certification=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--paths', nargs='+', required=True, help='All files changed for this local task')
    parser.add_argument('--tests', nargs='*', default=[], help='Additional unittest modules, classes or methods')
    parser.add_argument('--targeted', action='store_true', help='Use explicit --tests instead of transitive Python selection. Source financial contracts remain mandatory.')
    parser.add_argument('--plan-only', action='store_true')
    parser.add_argument('--browser', action='store_true', help='Explicit comprehensive browser regression')
    args = parser.parse_args()
    paths = []
    for name in args.paths:
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT):
            parser.error('Path outside project: ' + name)
        paths.append(path.relative_to(ROOT).as_posix())
    selection = plan(ROOT, sorted(set(paths)), args.tests, targeted=args.targeted)
    if args.plan_only:
        print(json.dumps(selection, indent=2))
        return 2 if selection['unresolved'] else 0
    from validation_reporting import Progress, TimedResult, run_directory, save_report, test_ids
    directory = run_directory(ROOT)
    progress = Progress(directory, ROOT / 'tmp/check-dev-progress.json')
    started = time.perf_counter()
    report = dict(mode='dev', status='failed', selection=selection, stages={}, certification=False)
    def stage(name, fn):
        start = time.perf_counter()
        progress.phase(name)
        try:
            return fn()
        finally:
            report['stages'][name] = round(time.perf_counter() - start, 3)
            progress.end_phase()
    def node(arguments):
        result = subprocess.run([shutil.which('node') or 'node', *arguments], cwd=ROOT / 'app',
                                capture_output=True, text=True, encoding='utf-8', errors='replace')
        (directory / ('node-' + str(len(report['stages'])) + '.log')).write_text(result.stdout + result.stderr, encoding='utf-8')
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
    try:
        if selection['unresolved']:
            raise ValueError('Define targeted checks for: ' + ', '.join(selection['unresolved']) + '. No automatic full run.')
        if selection['content']:
            from test_support import reference_study
            stage('content', reference_study)
        if selection['python_tests']:
            suite = unittest.defaultTestLoader.loadTestsFromNames(selection['python_tests'])
            report['scheduled_test_ids'] = list(test_ids(suite))
            progress.schedule(suite.countTestCases())
            result = stage('python_tests', lambda: unittest.TextTestRunner(verbosity=1, resultclass=lambda *a, **k: TimedResult(*a, progress=progress, **k)).run(suite))
            report.update(tests=result.testsRun, test_results=result.records)
            if not result.wasSuccessful():
                return 1
        if selection['frontend']:
            stage('types', lambda: node(['node_modules/typescript/bin/tsc', '--noEmit']))
            stage('frontend_tests', lambda: node(['--experimental-strip-types', '--test',
                *sorted(p.relative_to(ROOT / 'app').as_posix() for p in (ROOT / 'app/scripts').glob('test-*.mjs'))]))
            stage('content_static', lambda: node(['scripts/check-content.mjs']))
        if args.browser:
            from prepare_static_app import prepare
            from test_support import reference_study
            from browser_checks import check
            stage('static_delivery', prepare)
            stage('browser', lambda: check(reference_study(), directory))
        report['status'] = 'passed'
        return 0
    except Exception as error:
        report['error'] = str(error)
        return 1
    finally:
        report['seconds'] = round(time.perf_counter() - started, 3)
        progress.close(report['status'])
        save_report(report, directory, ROOT / 'tmp/check-dev-last.json')
        print(json.dumps({k: v for k, v in report.items() if k not in {'test_results', 'scheduled_test_ids'}}, indent=2))


if __name__ == '__main__':
    raise SystemExit(main())
