"""Read-only timing audit. Experimental cache is local to this process only."""
import sys,time,json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
from copy import deepcopy

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import validate_stacks
original_read=validate_stacks.read
mode='baseline';phase='imports';cache={};reads=defaultdict(Counter);read_seconds=defaultdict(float)
def measured_read(path):
    key=(mode,phase);relative=Path(path).relative_to(ROOT).as_posix()
    start=time.perf_counter();reads[key][relative]+=1
    try:
        if mode=='cache_experimental':
            if relative not in cache:cache[relative]=original_read(path)
            return deepcopy(cache[relative])
        return original_read(path)
    finally:read_seconds[key]+=time.perf_counter()-start
validate_stacks.read=measured_read
from study_app import Study
records=[];digests={}
def stage(name,operation):
    global phase
    phase=name;start=time.perf_counter();value=operation();elapsed=time.perf_counter()-start
    key=(mode,phase)
    record=dict(mode=mode,phase=phase,seconds=round(elapsed,4),yaml_calls=sum(reads[key].values()),unique_yaml=len(reads[key]),yaml_seconds=round(read_seconds[key],4),
                top_reads=reads[key].most_common(12))
    records.append(record);print(json.dumps(record,ensure_ascii=False),flush=True)
    return value
for mode in ('baseline','cache_experimental'):
    study=stage('Study_init',Study)
    result=stage('simulate',lambda:study.simulate(deepcopy(study.parameters)))
    encoded=stage('serialize_bootstrap',lambda:json.dumps(study.bootstrap(),ensure_ascii=False,allow_nan=False).encode())
    digests[mode]=dict(bootstrap_sha256=hashlib.sha256(encoded).hexdigest(),bootstrap_bytes=len(encoded),simulation_sha256=hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest())
assert digests['baseline']==digests['cache_experimental'],'Experimental cache changed output'
out=dict(date='2026-10-27',protocol='One sequential run per variant; wall time with instrumented YAML reads. Cache returns deep copies; no active files changed. No cold filesystem cache guarantee; not a statistical benchmark.',records=records,outputs=digests)
(ROOT/'audits/2026-10-27-performance-modele-mesures.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
