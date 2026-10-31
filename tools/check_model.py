"""Single entry point: quick invariants, editorial checks, or complete validation."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import unittest
import traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from validation_reporting import TimedResult, run_directory, save_report, test_ids
try: import yaml
except ImportError: sys.path.insert(0,str(ROOT/'tmp/yaml-stacks/deps'));import yaml
from test_support import reference_study
from study_app import Study
from study_snapshot import candidate, publish, load, encode
from validate_stacks import read

def preserve(study,path):
    witness=json.loads(Path(path).read_text(encoding='utf-8'))
    assert witness['contract']==study.simulation_contract(), 'Simulation meaning changed'
    cases = dict(witness['cases'], **witness.get('edge_cases', {}))
    for name,case in cases.items():
        actual=study.simulate(case['parameters'])
        assert {k:v for k,v in actual.items() if k!='model_version'}=={k:v for k,v in case['result'].items() if k!='model_version'},name
    return len(cases)

def content_only():
    """Validate current sources and their editorial projections without writing them."""
    return reference_study()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--quick',action='store_true');mode.add_argument('--content',action='store_true');mode.add_argument('--full','--release',dest='release',action='store_true')
    parser.add_argument('--publish',action='store_true',help='Replace release/current.json only after all release checks pass')
    parser.add_argument('--browser',action='store_true',help='Also validate the static application in a real browser. Automatic presentation checks always include it.')
    parser.add_argument('--compare',type=Path,help='Earlier full report and test inventory for timing and coverage comparison')
    parser.add_argument('--preserve',type=Path,help='Explicit numeric parity witness for a refactor; not a permanent historical gate')
    mode.add_argument('--auto',action='store_true',help='Use the last successful full run and semantic source changes to select full or presentation checks')
    args=parser.parse_args()
    requested_auto=args.auto
    if args.auto:
        from validation_changes import plan
        selection=plan(ROOT)
        args.release=selection['mode']=='full'
        args.content=not args.release
    if args.browser and (args.quick or (args.content and not requested_auto)):parser.error('--browser requires --full or --auto')
    if args.publish and (not args.release or requested_auto):parser.error('--publish requires --full')
    directory=run_directory(ROOT)
    started=time.perf_counter();report=dict(mode='full' if args.release else 'presentation' if requested_auto else 'content' if args.content else 'quick',stages={})
    def stage(name,fn):
        start=time.perf_counter()
        try:return fn()
        finally:report['stages'][name]=round(time.perf_counter()-start,3)
    report['directory']=str(directory)
    if requested_auto:report['selection']=selection
    report['status']='failed'
    comparison_baseline=None
    try:
        if args.release and args.compare:
            comparison_baseline=json.loads(args.compare.read_text(encoding='utf-8'))
        from validation_changes import snapshot
        initial_manifest=snapshot(ROOT)
        if args.content and not requested_auto:
            stage('editorial',content_only)
        else:
            study=stage('load_model',reference_study)
            if args.preserve:report['preserved_scenarios']=stage('numeric_parity',lambda:preserve(study,args.preserve))
            loader=unittest.TestLoader()
            suite=loader.discover(str(ROOT/'tools'),pattern='test_*.py') if args.release else loader.loadTestsFromNames([
                'test_model_runtime','test_model_inputs','test_cost_separation','test_composable_costs',
                'test_architecture_model','test_market_references','test_estimation_calculation',
                'test_market_instruction','test_maintenance_specialisation','test_business_contract','test_validation_automation'])
            if requested_auto and not args.release:
                suite=loader.loadTestsFromName('test_business_contract')
            from business_contract import coverage_report
            report['business_contract']=stage('business_contract',lambda:coverage_report())
            report['scheduled_test_ids']=list(test_ids(suite))
            if args.release and args.compare:
                previous=comparison_baseline
                expected=set(previous.get('test_ids',previous.get('scheduled_test_ids',[])))
                missing=expected-set(report['scheduled_test_ids'])
                if missing:raise AssertionError('Removed tests: '+str(sorted(missing)))
                report['coverage_preserved']=len(expected)
            result=stage('python_tests',lambda:unittest.TextTestRunner(verbosity=1,resultclass=TimedResult).run(suite))
            report['test_results']=result.records
            report['failures']=len(result.failures)
            report['errors']=len(result.errors)
            report['skipped']=len(result.skipped)
            report['business_contract']['executed']=sorted({r['id'] for r in result.records if r['status']=='passed'} & set(report['business_contract']['test_ids']))
            report['tests']=result.testsRun
            if not result.wasSuccessful():return 1
            if args.release:
                passed={r['id'] for r in result.records if r['status']=='passed'}
                required=set(report['business_contract']['test_ids'])
                if args.compare:required |= expected
                if required-passed:raise AssertionError('Required regression tests did not pass: '+str(sorted(required-passed)))
            if args.release or requested_auto:
                def frontend():
                    import shutil
                    node=shutil.which('node')
                    if not node:raise RuntimeError('Node.js is required for release checks')
                    fixture=directory/'bootstrap.json'
                    fixture.write_bytes(encode(dict(model_version=study.version,simulation_contract=study.simulation_contract(),ui=study.ui,baseline=study.baseline)))
                    import os
                    environment=dict(os.environ,FLOW_TEST_BOOTSTRAP=str(fixture))
                    scripts=sorted(p.relative_to(ROOT/'app').as_posix() for p in (ROOT/'app/scripts').glob('test-*.mjs'))
                    commands=[[node,'--experimental-strip-types','--test',*scripts],
                              [node,'node_modules/typescript/bin/tsc','--noEmit'],
                              [node,'scripts/check-content.mjs'],
                              [node,'node_modules/vite/bin/vite.js','build']]
                    for index,command in enumerate(commands):
                        command_started=time.perf_counter()
                        result=subprocess.run(command,cwd=ROOT/'app',env=environment,capture_output=True,text=True,encoding='utf-8',errors='replace')
                        (directory/f'frontend-{index}.log').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
                        report['stages'][f'frontend_{index}']=round(time.perf_counter()-command_started,3)
                        if result.returncode:
                            print(result.stdout);print(result.stderr);raise RuntimeError('Frontend checks failed')
                    report['frontend']='tests, types, content, build passed'
                stage('frontend',frontend)
                from prepare_static_app import prepare
                from build_pages import build_pages
                stage('static_delivery',lambda:prepare(ROOT/'app/dist',root=ROOT,force=True,
                    builder=lambda output,base:build_pages(output,base,study=study)))
                if args.browser or (requested_auto and not args.release):
                    from browser_checks import check
                    browser=stage('browser',lambda:check(study,directory,args.preserve))
                    report['browser']=dict(status=browser['status'],seconds=browser['seconds'],
                        http_api_requests=browser['httpApiRequests'],routes={k:len(v) for k,v in browser['routes'].items()})
                if args.publish:
                    # Generated documents are exports of this already calculated object.
                    from copy import deepcopy
                    from project_investment import project
                    # Compatibility export only: the live model uses valuation(),
                    # while this historical URL retains its full 15-year meaning.
                    from calculate_costs import calculate
                    def exports():
                        (ROOT/'source/couts-15-ans.yaml').write_text(yaml.safe_dump(calculate(),allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
                        (ROOT/'source/investissements-10-ans.yaml').write_text(yaml.safe_dump(project(deepcopy(study.data),10),allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
                        (ROOT/'source/investissements-15-ans.yaml').write_text(yaml.safe_dump(project(deepcopy(study.data)),allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
                    stage('document_exports',exports)
                bundle=stage('freeze_release',lambda:candidate(study))
                released=stage('load_release',lambda:Study.from_release(bundle))
                assert released.simulate(released.parameters)==study.baseline
                if args.preserve:preserve(released,args.preserve)
                report['bootstrap_bytes']=len(encode(released.bootstrap(compact=True)))
                report['essential_bootstrap_bytes']=len(encode(released.bootstrap(essential=True)))
                report['release_bytes']=len(encode(bundle))
                report['release_id']=bundle['sha256'][:12]
                current=ROOT/'release/current.json'
                if current.exists():
                    old=load(current)['payload']['baseline']
                    report['delta_10_years']={n['stack']:round(n['horizons'][-1]['totals']['total']-o['horizons'][-1]['totals']['total'],2) for o,n in zip(old['options'],study.baseline['options'])}
                if args.publish:
                    stage('publish',lambda:publish(bundle,current));report['published']=True
        if args.release:
            from validation_changes import snapshot
            manifest=snapshot(ROOT)
            generated={'source/couts-15-ans.yaml','source/investissements-10-ans.yaml','source/investissements-15-ans.yaml'} if args.publish else set()
            before={k:v for k,v in initial_manifest['files'].items() if k not in generated}
            after={k:v for k,v in manifest['files'].items() if k not in generated}
            if before != after:raise ValueError('Inputs changed during validation')
            manifest['report']=str(directory/'report.json')
            (ROOT/'tmp/validation-full-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False),encoding='utf-8')
        report['status']='passed'
        return 0
    except Exception:
        report['status']='failed'
        report['error']=traceback.format_exc()
        print(report['error'],file=sys.stderr)
        return 1
    finally:
        report['seconds']=round(time.perf_counter()-started,3)
        if comparison_baseline is not None:
            previous=comparison_baseline.get('full_report',comparison_baseline)
            if previous.get('seconds'):
                report['comparison']=dict(before_seconds=previous['seconds'],after_seconds=report['seconds'],
                    saved_seconds=round(previous['seconds']-report['seconds'],3),
                    faster_pct=round(100*(1-report['seconds']/previous['seconds']),2))
        save_report(report,directory,ROOT/'tmp/check-model-last.json')
        summary={k:v for k,v in report.items() if k not in ('test_results','scheduled_test_ids','business_contract')}
        print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':raise SystemExit(main())
