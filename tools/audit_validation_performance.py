"""Read-only performance audit of model loading and existing validation reports.

Run from the project root. Profiling is optional and never publishes a release.
"""
import argparse
from collections import defaultdict
from copy import deepcopy
import cProfile
import json
from pathlib import Path
import pstats
import re
import sys
import time
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from study_app import Study
from model_context import SourceSnapshot


def audit(profile=False):
    reads=defaultdict(lambda:dict(calls=0,parses=0,seconds=0,parse_seconds=0))
    original=SourceSnapshot.read
    def measured(snapshot,path,loader):
        key=str(path.resolve().relative_to(ROOT))
        record=reads[key]
        record['calls']+=1
        def parsed(raw):
            started=time.perf_counter()
            try:return loader(raw)
            finally:
                record['parses']+=1
                record['parse_seconds']+=time.perf_counter()-started
        started=time.perf_counter()
        try:return original(snapshot,path,parsed)
        finally:record['seconds']+=time.perf_counter()-started
    profiler=cProfile.Profile() if profile else None
    started=time.perf_counter()
    with patch.object(SourceSnapshot,'read',measured):
        if profiler:profiler.enable()
        try:study=Study()
        finally:
            if profiler:profiler.disable()
    load_seconds=time.perf_counter()-started
    copies=[]
    for _ in range(2):
        started=time.perf_counter();clone=deepcopy(study);copies.append(time.perf_counter()-started)
        assert clone.baseline==study.baseline
    started=time.perf_counter()
    for _ in range(6):assert study.simulate(study.parameters)==study.baseline
    simulation_seconds=time.perf_counter()-started
    last=ROOT/'tmp/check-model-last.json'
    report=dict(measurement=dict(profiled=profile,repetitions=1,load_seconds=load_seconds,
        copy_seconds=copies,six_reference_simulations_seconds=simulation_seconds,
        sources=len(reads),source_read_calls=sum(r['calls'] for r in reads.values()),
        source_parses=sum(r['parses'] for r in reads.values())),
        last_full=json.loads(last.read_text(encoding='utf-8')) if last.exists() else None,
        slow_sources=sorted([dict(path=k,**v) for k,v in reads.items()],key=lambda r:r['seconds'],reverse=True)[:20])
    log=ROOT/'tmp/synvance-editorial-full.log'
    if log.exists():
        report['historical_slow_tests']=sorted([dict(test=m[0],seconds=float(m[1])) for m in
            re.findall(r'Completed: (\S+) ([0-9.]+) s',log.read_text(encoding='utf-8',errors='replace'))],key=lambda r:r['seconds'],reverse=True)
    if profiler:
        target=ROOT/'tmp/validation-load.prof';profiler.dump_stats(str(target))
        stats=pstats.Stats(profiler)
        report['profile']=[dict(file=str(key[0]),line=key[1],function=key[2],primitive_calls=value[0],calls=value[1],self_seconds=value[2],cumulative_seconds=value[3])
            for key,value in sorted(stats.stats.items(),key=lambda kv:kv[1][2],reverse=True)[:25]]
        report['profile_note']='Profile timings include instrumentation overhead. Cumulative times overlap and must not be summed.'
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',action='store_true')
    parser.add_argument('--output',type=Path,default=ROOT/'tmp/validation-performance.json')
    args=parser.parse_args();report=audit(args.profile)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(output=str(args.output),measurement=report['measurement'],slow_sources=report['slow_sources'][:5],profile=report.get('profile',[])[:7]),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
