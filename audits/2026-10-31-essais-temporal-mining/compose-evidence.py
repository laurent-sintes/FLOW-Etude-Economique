from pathlib import Path
import json,hashlib,gzip,base64,xml.etree.ElementTree as ET,shutil
R=Path.cwd();A=R/'audits/2026-10-31-essais-temporal-mining';O=A/'results'
report=A/'temporal/target/surefire-reports/flow.trial.TemporalTrialTest.txt';shutil.copy2(report,O/'temporal-final.txt')
x=ET.parse(A/'temporal/target/surefire-reports/TEST-flow.trial.TemporalTrialTest.xml').getroot();assert int(x.attrib['failures'])==0 and int(x.attrib['errors'])==0
junit=[dict(id=c.attrib['name'],passed=not any(c.find(k) is not None for k in ('failure','error','skipped'))) for c in x.findall('testcase')]
groups=[dict(id='temporal-unit',checks=junit)]
for name in ['temporal-live-phase1','temporal-durable-restart','mining','superset','browser']:
 d=json.loads((O/(name+'.json')).read_text('utf8'));assert all(c['passed'] for c in d['checks']);groups.append(dict(id=name,checks=d['checks']))
paths=[A/'runtime-provenance.json',A/'sources/superset-base-requirements.txt',A/'sources/superset-embedded-sdk.json',A/'sources/temporal-cli-checksums.txt',A/'temporal/pom.xml']
paths+=list((A/'temporal/src').rglob('*.java'))+list((A/'temporal/src').rglob('*.html'))
paths += [A/n for n in ['live-temporal.py','durable-restart.py','mining.cjs','superset-trial.py','superset-http.py','browser.mjs']]
paths+=[p for p in O.glob('*.json') if p.name!='summary.json']+list(O.glob('*.txt'))+list((O/'live').glob('*.json'))+list((O/'temporal').glob('*.json'))
files={}
for p in sorted(set(paths)):
 raw=p.read_bytes();files[p.relative_to(R).as_posix()]=dict(sha256=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf-8-sig'))
payload=json.dumps(files,ensure_ascii=False,separators=(',',':')).encode();compressed=gzip.compress(payload,mtime=0)
prior=json.loads((R/'audits/2026-10-30-audit-fonctions-transverses/proposal-results.json').read_text('utf8'))
proof=dict(version=1,id='temporal-mining-2026-10-31',date='2026-10-31',status='targeted_trials_completed',proposal_inputs_sha256=hashlib.sha256((R/'audits/2026-10-30-audit-fonctions-transverses/proposal-inputs.json').read_bytes()).hexdigest(),check_groups=groups,financial_reference={k:prior[k] for k in ['total_jh','adopted_jh','eur_ht','cosmic_process','it_cosmic','purposes']},archive=dict(encoding='gzip-base64',uncompressed_sha256=hashlib.sha256(payload).hexdigest(),files=len(files),payload=base64.b64encode(compressed).decode()),interpretation=dict(technical_feasibility='Demonstrated only within the recorded synthetic fixtures and bounded catalogue.',effort_calibration='Not supplied by these trials: prototype duration and line count are not project actuals.',initial_failure='In-memory replacement-worker fixture timed out. Original failed result retained; restart requirement then passed against the official SQLite server, including abrupt server+worker process stop.',statistical_uncertainty='Unknown. No confidence score or statistical interval follows from passing checks.'))
(A/'technical-evidence.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),'utf8')
summary=dict(checks_passed=sum(len(g['checks']) for g in groups),groups=[dict(id=g['id'],passed=len(g['checks'])) for g in groups],archived_files=len(files),archive_bytes=len(compressed),evidence_sha256=hashlib.sha256((A/'technical-evidence.json').read_bytes()).hexdigest())
(O/'summary.json').write_text(json.dumps(summary,indent=2),'utf8');print(json.dumps(summary))
