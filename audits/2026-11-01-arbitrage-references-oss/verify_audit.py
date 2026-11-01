"""Verify the concrete findings and completeness of the read-only audit."""
from pathlib import Path
import json,math,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
r=json.loads((P/'results.json').read_text(encoding='utf-8'));a=json.loads((P/'arbitrages.json').read_text(encoding='utf-8'))
u={x['id']:x for x in r['units']};assert len(u)==len(a['units'])==11
assert set(u)=={x['id'] for x in a['units']}
assert sum(x['adopted_jh'] for x in u.values())==6660
assert len({c['id'] for x in u.values() for c in x['capabilities']})==88
assert sum(len(x['comparisons']) for x in u.values())==44
for x in a['units']:
 assert set(x['alternatives'])=={'erpnext','odoo','tryton','axelor'}
 for source in x['evidence']:assert (ROOT/source).is_file(),source
f=r['professional']['files'];assert {p:len(v) for p,v in f['supply-workbenches'].items()}==dict(erpnext=7,odoo=56,tryton=1,axelor=14)
assert round(next(x['maximum_to_minimum'] for x in r['ranking'] if x['id']=='supply-workbenches-java-spring'),2)==24.88
banks=u['master-plan-java-spring']['families']['master-plan'];assert {p:v['analogue'] for p,v in banks.items()}==dict(erpnext=1418,odoo=370,tryton=214,axelor=679)
assert math.isclose(sum(r['families'][name]['quantity']*r['families'][name]['fraction'] for name in ('master-plan','plan-preparation')),4.4)
g=r['professional']['raw_equivalent_units'];assert max(g['analytics-mining'],key=g['analytics-mining'].get)=='odoo'
base=g['process-studio']['axelor']*.5+g['human-forms']['axelor']*.5+g['analytics-mining']['odoo']*.75
assert math.isclose(base,17372.6275)
for x in u['process-management-java-spring']['size_trace']['component_sizes'].values():assert math.isclose(x['new_equivalent_units'],base)
bundle=next(x for x in f['process-studio']['axelor'] if x['path']=='react/bpm/bundled-config.js');assert bundle['program_units']+bundle['declarative_units']==897
assert r['coherent_source_files_verified']==117 and r['professional']['local_files_verified']==1315
before=json.loads((P/'protected-before.json').read_text(encoding='utf-8'))
for name,expected in before.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
result=dict(status='passed',lots=11,oss_readings=44,arbitrages_complete=True,quantitative_findings_verified=True,protected_files_unchanged=len(before),adopted_jh=6660)
(P/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
