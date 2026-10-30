"""Verify retained experiment, economic conservation and audit artifacts, without repeating timed solvers."""
from pathlib import Path
import ast,json,hashlib,subprocess,sys,xml.etree.ElementTree as ET
A=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda n:json.loads((A/n).read_text(encoding='utf-8'))
checks=[]
def check(ok,label):
 if not ok:raise AssertionError(label)
 checks.append(label)
previous=load('iteration-14-verification.json')
for name,h in previous['artifacts_sha256'].items():
 p=A/name
 if not p.exists():p=A.parents[1]/name
 check(p.exists() and H(p)==h,'Previous14 unchanged '+name)
# Recompute only deterministic artifacts from retained Java results.
names=['iteration-15-cases.json','iteration-15-resultats.json','iteration-15-interpretation.json','iteration-15.html']
hashes={name:H(A/name) for name in names}
for script in ['iteration-15-generate.py','iteration-15-analyse.py','iteration-15-report.py']:
 p=subprocess.run([sys.executable,'-B',str(A/script)],capture_output=True,text=True,encoding='utf-8')
 check(p.returncode==0,'Recompute '+script+(' '+p.stderr if p.returncode else ''))
for name,h in hashes.items():check(H(A/name)==h,'Reproducible '+name)
d=load('iteration-15-resultats.json');old=load('iteration-14-resultats.json');runtime=load('iteration-15-runtime.json')
check(d['cumulative_estimated']==old['cumulative_estimated'],'All cumulative role envelopes unchanged')
check(d['cumulative_coverage']==old['cumulative_coverage'],'Cumulative unique capability list unchanged')
check(d['calendar_preserved']==old['calendar'],'Calendar assumptions and raw durations preserved')
check(d['full_core_jh'] is None,'Full Core remains unknown')
check(d['revision_delta_jh']==[0,0,0],'No unsupported reduction or addition')
check(d['uncertainty_class']=='C' and d['statistical_percentiles'] is None,'No invented certainty percentile')
check(d['progress']['not_compared']==32 and d['progress']['compared_cumulative']==56,'Coverage56+32=88')
for name,h in runtime['sources'].items():check(H(A/name)==h,'Executed Java source unchanged '+name)
cp=(A/'iteration-15-prototype/target/classpath.txt').read_text().strip()
import os
jars={Path(p).name:Path(p) for p in cp.split(os.pathsep) if Path(p).is_file()}
for j in runtime['artifacts']:check(H(jars[j['name']])==j['sha256'],'Executed dependency '+j['name'])
root=ET.parse(A/'iteration-15-prototype/pom.xml').getroot()
ns={'m':'http://maven.apache.org/POM/4.0.0'}
deps={n.find('m:artifactId',ns).text:n.find('m:version',ns).text if n.find('m:version',ns) is not None else None for n in root.findall('m:dependencies/m:dependency',ns)}
check(deps['timefold-solver-core']==runtime['versions']['timefold'],'Timefold pinned binary version')
check(deps['ortools-java']==runtime['versions']['ortools'],'OR-Tools pinned binary version')
check(load('iteration-15-initial-invalid-adapter/EXCLUDED.json')['status']=='EXCLUDED_FROM_COMPARISON','Initial invalid adapter clearly excluded')
for f in A.glob('iteration-15-*.py'):ast.parse(f.read_text(encoding='utf-8'));checks.append('Syntax '+f.name)
for f in A.glob('iteration-15-*.json'):json.loads(f.read_text(encoding='utf-8'));checks.append('JSON '+f.name)
browser=load('iteration-15-browser-check.json')
check(len(browser['checks'])==2 and all(c['passed'] for c in browser['checks']),'Desktop/mobile browser checks')
for s in browser['screenshots']:check((A/s).exists(),'Screenshot '+s)
files=[]
for p in A.glob('iteration-15*'):
 if p.is_file():files.append(p)
 else:files.extend(x for x in p.rglob('*') if x.is_file() and 'target' not in x.relative_to(p).parts)
manifest={str(p.relative_to(A)).replace('\\','/'):H(p) for p in sorted(files) if p.name!='iteration-15-verification.json'}
out={'id':'iteration-15-verification','status':'complete','validation_checks':len(d['checks']),'artifact_checks':len(checks),'checks':checks,
'comparison_runs':276,'additional_solver_probes':2,'synthetic_cases':23,'small_exact_oracles':20,
'visual_reviewed':['desktop','roles','algorithm_chain','mobile'],'previous14_unchanged':True,
'economy_preserved':True,'calibration_of_jh':False,
'meaning':'Checks establish artifact consistency and bounded experiment correctness, not business completeness, predictive effort accuracy or a general solver ranking.',
'artifacts_sha256':manifest}
(A/'iteration-15-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:out[k] for k in ['status','validation_checks','artifact_checks','comparison_runs','economy_preserved']},ensure_ascii=False))
