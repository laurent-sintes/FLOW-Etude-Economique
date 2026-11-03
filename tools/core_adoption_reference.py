"""Explicit frozen regression reference for adopted costs; never recompute expectations in tests."""
from copy import deepcopy
from pathlib import Path, PurePosixPath
from collections import Counter
import hashlib,json

POINTER='tools/fixtures/active-adoption.json'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def raw_json(value):return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
def build_reference(study,decision_ref,decision_sha,root,before=None):
    units=next(o['core_units'] for o in study.economic['options'] if o['stack']=='java-spring')
    purpose=next(o for o in study.content['core_product_scope']['options'] if o['stack']=='java-spring')
    decision=json.loads((Path(root)/decision_ref).read_text(encoding='utf-8'))
    assert sha((Path(root)/decision_ref).read_bytes())==decision_sha
    return dict(format=1,before=before,decision=dict(path=decision_ref,sha256=decision_sha),total_jh=sum(u['total_jh'] for u in units),cost_eur_ht=sum(u['cost_eur_ht'] for u in units),delta_jh=decision['delta_jh'],delta_cost_eur_ht=None if decision.get('previous_cost_eur_ht') is None else sum(u['cost_eur_ht'] for u in units)-decision['previous_cost_eur_ht'],
        unit_days=[u['total_jh'] for u in units],methods=dict(Counter(u['method'] for u in units)),role_totals=dict(Counter({r['id']:sum(next(x['jh'] for x in u['roles'] if x['id']==r['id']) for u in units) for r in units[0]['roles']})),
        units={u['id']:dict(jh=u['total_jh'],months=u['months'],cost_eur_ht=u['cost_eur_ht'],roles={r['id']:r['jh'] for r in u['roles']},work={w['id']:w['jh'] for w in u['trace'].get('work_package_adoption',{}).get('work',[])}) for u in units},
        purpose_totals={k:v['jh'] for k,v in purpose['purposes'].items()},completion_costs={o['stack']:o['service_completion']['total_eur_ht'] for o in study.content['economic_evaluations']['options']},
        ten_year_costs={o['stack']:o['horizons'][-1]['totals']['total'] for o in study.baseline['options']})

def load_reference(root):
    root=Path(root).resolve();pointer=json.loads((root/POINTER).read_text(encoding='utf-8'))
    name=PurePosixPath(pointer['path']);assert not name.is_absolute() and '..' not in name.parts
    path=(root/name).resolve();assert path.is_relative_to(root)
    raw=path.read_bytes();assert sha(raw)==pointer['sha256'],'Frozen test reference changed'
    doc=json.loads(raw);ref=doc['decision'];decision_path=(root/ref['path']).resolve();assert decision_path.is_relative_to(root)
    assert sha(decision_path.read_bytes())==ref['sha256'],'Adopted decision proof changed'
    decision=json.loads(decision_path.read_text(encoding='utf-8'))
    cost=decision['construction_cost_eur_ht']
    if 'pricing_revision' in doc:
        price_ref=doc['pricing_revision'];price_path=(root/price_ref['path']).resolve();assert price_path.is_relative_to(root)
        price_raw=price_path.read_bytes();assert sha(price_raw)==price_ref['sha256'],'Pricing revision proof changed'
        pricing=json.loads(price_raw);cost=pricing['construction_cost_eur_ht']
        assert pricing['effort_decision']==doc['decision'] and pricing['total_jh']==doc['total_jh']
    assert doc['total_jh']==decision['proposal_jh'] and doc['cost_eur_ht']==cost
    assert doc['unit_days']==[u['proposal_jh'] for u in decision['units']]
    return deepcopy(doc)
