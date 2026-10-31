"""Independent audit checks; no model or source mutations."""
from pathlib import Path
from collections import Counter
import ast,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
import yaml
from capability_catalog import analysis,native
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
e=read(OUT/'preuves-code.json');v=read(OUT/'verification.json');p=read(OUT/'provenance.json')
for name,h in p['protected_active_inputs'].items():assert sha(ROOT/name)==h,name
for name,h in p['evidence_dependencies'].items():assert sha(ROOT/name)==h,name
for name,h in p['outputs'].items():assert sha(OUT/name)==h,name
assert len(e['files'])==29 and len(e['witnesses'])==25
assert len({(f['product'],f['path']) for f in e['files']})==29
assert Counter(f['product'] for f in e['files'])==dict(erpnext=8,odoo=7,tryton=6,axelor=8)
repos=read(ROOT/'audits/2026-10-30-master-data-comparable-reuse/measurements.json')['repos']
for product,s in e['summary'].items():
 rows=[f for f in e['files'] if f['product']==product]
 witnesses=[w for w in e['witnesses'] if w['product']==product]
 assert s['files']==len(rows) and s['witness_methods']==len(witnesses)
 assert s['raw_component_program_units']==sum(r['program_units'] for r in rows)
 assert s['raw_component_declarative_units']==sum(r['declarative_units'] for r in rows)
 assert s['ownership_effort_jh'] is None
 union={}
 for w in witnesses:
  source=ROOT/repos[product]['root']/w['path']
  assert sha(source)==w['sha256']
  ns={(n['kind'],n['start'],n['end']) for n in w['nodes']}
  assert len(ns)==w['program_units'] and all(w['start']<=a<=b<=w['end'] for _,a,b in ns)
  assert 0<=w['known_Stock_floor_overlap']<=len(ns)
  union.setdefault(w['path'],set()).update(ns)
 assert sum(len(nodes) for nodes in union.values())==s['witness_program_units_union']
 for f in rows:
  assert f['commit']==repos[product]['commit'] and sha(ROOT/repos[product]['root']/f['path'])==f['sha256']
  assert f['git_content_verified_with_CRLF_normalization'] and not f['eligible_as_new_ownership_effort']
family=yaml.safe_load((OUT/'cadrage.yaml').read_text(encoding='utf-8'))
originals={n['id']:n for n in native()['nodes']}
assert len(family['evaluation_unit']['capabilities'])==2
for c in family['evaluation_unit']['capabilities']:
 for k,value in c['fields'].items():assert value==originals[c['native_id']]['fields'].get(k)
assert len(family['outputs'])==6 and len(family['new_Flow_modules_to_size'])==6
ret=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))['units']
assert sum(u['total_jh'] for u in ret)==1840
assert [(u['id'],u['total_jh'],u['months']) for u in ret]==[('master-data-java-spring',1500,17),('stock-java-spring',340,10)]
assert len({c['id'] for u in ret for c in u['capabilities']})==14
assert v['passed'] and v['studied_capabilities']==16 and not v['ownership_estimate_adopted']
print(json.dumps({'passed':True,'native_source_files':29,'code_methods':25,'source_pins':4,'stock_master_data_reuse_separated':True,'protected_model_unchanged':True,'retained_gross_jh':1840,'retained_capabilities':14,'studied_capabilities':16},ensure_ascii=False))
