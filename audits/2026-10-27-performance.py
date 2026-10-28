"""Read-only performance audit; writes only its measurement report."""
import cProfile, io, json, statistics, time, pstats, gzip
from copy import deepcopy
from pathlib import Path
from study_app import Study
from study_snapshot import load,encode
from validate_stacks import ROOT

def measure(fn,n):
    times=[]
    for _ in range(n):
        start=time.perf_counter();value=fn();times.append((time.perf_counter()-start)*1000)
    return value,dict(samples=n,median_ms=round(statistics.median(times),2),min_ms=round(min(times),2),max_ms=round(max(times),2))

report={'scope':'Local process, warm OS file cache, no full validation suite, no source/reference/session mutation','measurements':{}}
m=report['measurements']
bundle,m['release_read_and_validate']=measure(lambda:load(ROOT/'release/current.json'),3)
study,m['release_materialize_and_validate_again']=measure(lambda:Study.from_release(bundle),3)
_,m['server_bootstrap_prepare']=measure(lambda:study.bootstrap(compact=True),3)
_,m['draft_build']=measure(Study,3)
_,m['simulate']=measure(lambda:study.simulate(study.parameters),20)
_,m['simulate_data_deepcopy']=measure(lambda:deepcopy(study.data),20)
boot=study.bootstrap(compact=True)
_,m['bootstrap_encode']=measure(lambda:encode(boot),5)
report['sizes']={'release_bytes':(ROOT/'release/current.json').stat().st_size,'bootstrap_bytes':len(encode(boot)),'bootstrap_gzip_bytes':len(gzip.compress(encode(boot))),'simulation_bytes':len(encode(study.baseline)),
    'bootstrap_sections':{k:len(encode(v)) for k,v in boot.items()},'content_sections':{k:len(encode(v)) for k,v in boot['content'].items()},
    'assets':{p.name:p.stat().st_size for p in (ROOT/'app/dist/assets').iterdir() if p.suffix in ('.js','.css')}}
for label,fn in [('draft',Study),('simulation',lambda:study.simulate(study.parameters))]:
    profile=cProfile.Profile();profile.runcall(fn)
    output=io.StringIO();pstats.Stats(profile,stream=output).strip_dirs().sort_stats('cumulative').print_stats(22)
    report[label+'_profile']=output.getvalue()
(ROOT/'audits/2026-10-27-performance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
