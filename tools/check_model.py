"""Single entry point: quick invariants, editorial checks, or complete validation."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
try: import yaml
except ImportError: sys.path.insert(0,str(ROOT/'tmp/yaml-stacks/deps'));import yaml
from test_support import reference_study
from study_app import Study
from study_snapshot import candidate, publish, load, encode
from validate_stacks import read

def preserve(study,path):
    witness=json.loads(Path(path).read_text(encoding='utf-8'))
    assert witness['contract']==study.simulation_contract(), 'Simulation meaning changed'
    for name,case in witness['cases'].items():
        actual=study.simulate(case['parameters'])
        assert {k:v for k,v in actual.items() if k!='model_version'}=={k:v for k,v in case['result'].items() if k!='model_version'},name
    return len(witness['cases'])

def content_only():
    """Validate current sources and their editorial projections without writing them."""
    return reference_study()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--quick',action='store_true');mode.add_argument('--content',action='store_true');mode.add_argument('--full','--release',dest='release',action='store_true')
    parser.add_argument('--publish',action='store_true',help='Replace release/current.json only after all release checks pass')
    parser.add_argument('--preserve',type=Path,help='Explicit numeric parity witness for a refactor; not a permanent historical gate')
    args=parser.parse_args()
    if args.publish and not args.release:parser.error('--publish requires --full')
    started=time.perf_counter();report=dict(mode='full' if args.release else 'content' if args.content else 'quick',stages={})
    def stage(name,fn):
        start=time.perf_counter();result=fn();report['stages'][name]=round(time.perf_counter()-start,3);return result
    if args.content:
        stage('editorial',content_only)
    else:
        study=stage('load_model',reference_study)
        if args.preserve:report['preserved_scenarios']=stage('numeric_parity',lambda:preserve(study,args.preserve))
        loader=unittest.TestLoader()
        suite=loader.discover(str(ROOT/'tools'),pattern='test_*.py') if args.release else loader.loadTestsFromNames([
            'test_model_runtime','test_model_inputs','test_cost_separation','test_composable_costs',
            'test_architecture_model','test_market_references','test_estimation_calculation',
            'test_market_instruction','test_maintenance_specialisation'])
        result=stage('python_tests',lambda:unittest.TextTestRunner(verbosity=1).run(suite))
        report['tests']=result.testsRun
        if not result.wasSuccessful():return 1
        if args.release:
            def frontend():
                import shutil
                node=shutil.which('node')
                if not node:raise RuntimeError('Node.js is required for release checks')
                fixture=ROOT/'tmp/check-model-bootstrap.json'
                fixture.write_bytes(encode(dict(model_version=study.version,simulation_contract=study.simulation_contract(),ui=study.ui,baseline=study.baseline)))
                import os
                environment=dict(os.environ,FLOW_TEST_BOOTSTRAP=str(fixture))
                scripts=sorted(p.relative_to(ROOT/'app').as_posix() for p in (ROOT/'app/scripts').glob('test-*.mjs'))
                commands=[[node,'--experimental-strip-types','--test',*scripts],
                          [node,'node_modules/typescript/bin/tsc','--noEmit'],
                          [node,'scripts/check-content.mjs'],
                          [node,'node_modules/vite/bin/vite.js','build']]
                for command in commands:
                    result=subprocess.run(command,cwd=ROOT/'app',env=environment,capture_output=True,text=True,encoding='utf-8',errors='replace')
                    if result.returncode:
                        print(result.stdout);print(result.stderr);raise RuntimeError('Frontend checks failed')
                report['frontend']='tests, types, content, build passed'
            stage('frontend',frontend)
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
    report['seconds']=round(time.perf_counter()-started,3)
    (ROOT/'tmp/check-model-last.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
