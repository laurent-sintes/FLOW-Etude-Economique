"""Comparable integration work units. Proposed effort never mutates adopted budgets."""
from copy import deepcopy
import math
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read
SOURCE='source/unites-integration.yaml'
SCHEMA='source/schema-unites-integration.yaml'
OPTIONS=('java-spring','microsoft','sap')
ROLES=('developpement','integration','support_n3','support_n1')
def require(ok,message):
    if not ok:raise ValueError('ERR_INTEGRATION_UNITS: '+message)
def numeric(value):return type(value) in (int,float) and math.isfinite(value) and value>=0
def estimate(quantity,setup,unit):
    require(quantity is None or numeric(quantity),'Invalid quantity')
    require(set(setup)==set(unit)==set(ROLES),'Invalid roles')
    for value in [*setup.values(),*unit.values()]:require(value is None or numeric(value),'Invalid effort')
    if quantity is None or any(v is None for v in [*setup.values(),*unit.values()]):return dict(roles=None,total_jh=None)
    roles={role:setup[role]+quantity*unit[role] for role in ROLES}
    return dict(roles=roles,total_jh=sum(roles.values()))
def dependencies():
    d=read(ROOT/SOURCE)
    return {SOURCE,SCHEMA,'source/integration.yaml','source/parcours-integration.yaml'}|{x['path'] for x in d['sources'].values()}|{x['path'] for x in d['funding_groups'].values()}
def compile_units(spec=None):
    d=deepcopy(read(ROOT/SOURCE) if spec is None else spec)
    errors=list(Draft202012Validator(read(ROOT/SCHEMA)).iter_errors(d));require(not errors,errors[0].message if errors else '')
    activities={a['id']:a for a in read(ROOT/'source/integration.yaml')['activites']}
    scenarios={s['scenario'] for s in read(ROOT/'source/parcours-integration.yaml')['scenarios']}
    require(len({u['id'] for u in d['units']})==len(d['units']),'Duplicate work identity')
    require({u['activity_ref'] for u in d['units']}==set(activities),'Incomplete activity coverage')
    for ref in [*d['sources'].values(),*d['funding_groups'].values()]:
        p=(ROOT/ref['path']).resolve();require(p.is_relative_to(ROOT.resolve()) and p.is_file(),'Unsafe or missing source')
    for key,p in d['packages'].items():
        require(p['source_ref'] in d['sources'],'Unknown package evidence')
        if p['kind']=='source':
            require(p['option']!='java-spring' and p['work_ref'] is None,'Source observation cannot override Make')
        else:
            require(p['option']=='java-spring' and not p['measures'],'Active Make effort must be read from the calculation')
            require(p['work_ref'] in activities if p['kind']=='make_activity' else p['work_ref']=='deployment','Invalid active work reference')
        for m in p['measures']:
            require(numeric(m['low']) and numeric(m['high']) and m['low']<=m['high'],'Invalid observed range')
    for u in d['units']:
        require(set(u['source_refs'])<=set(d['sources']),'Unknown evidence')
        require(set(u['scenario_refs'])<=scenarios,'Unknown scenario')
        require(u['quantity'] is None or bool(u['quantity_basis'] and u['quantity_basis'].strip()),'Quantity needs a basis')
        u['activity_label']=activities[u['activity_ref']]['nom']
        for slug,o in u['options'].items():
            f=d['funding_groups'].get(o['funding_group']);require(f is not None and f['option']==slug,'Wrong funding owner')
            expected='make-deployment' if u['activity_ref'] in ('INT-012','INT-013') else 'make-common'
            if slug=='java-spring':require(o['funding_group']==expected,'Deployment substitution must be preserved')
            if o['inclusion'] in ('inclus_documente','sans_objet'):require(bool(o['estimate_basis'] and o['estimate_basis'].strip()),'Inclusion or exclusion needs evidence')
            for ref in o['reconciliation']['package_refs']:
                p=d['packages'].get(ref)
                require(p is not None and p['option']==slug,'Wrong or missing reconciliation package')
            if o['inclusion'] in ('inclus_documente','partiel','complement'):
                require(bool(o['estimate_basis'] and o['estimate_basis'].strip()),'Coverage needs evidence')
            result=estimate(u['quantity'],o['setup_jh'],o['unit_jh'])
            if any(v is not None for v in [*o['setup_jh'].values(),*o['unit_jh'].values()]):require(bool(o['estimate_basis'] and o['estimate_basis'].strip()),'Effort needs a basis')
            if o['inclusion']=='sans_objet':require(result['total_jh'] in (None,0),'Not applicable cannot carry effort')
            o['estimate']=result;o['funding_label']=f['label']
    # A shared package has no monetary value here: it cannot be summed per row.
    return d


def attach_active_work(grid, groups):
    """Project existing results, never recompute or allocate a shared budget per unit."""
    d=deepcopy(grid)
    common=next(g for g in groups if g['id']=='common')
    deployment=next(g for g in groups if g['id']=='deployment')
    rows={r['id']:r for r in common['rows']}
    for p in d['packages'].values():
        if p['kind']=='make_activity':
            require(p['work_ref'] in rows,'Missing active work')
            r=rows[p['work_ref']];p['label']=p['work_ref']+' · '+r['label']
            p['measures']=[dict(label=p['work_ref'],low=r['value'],high=r['value'],unit='JH')]
        elif p['kind']=='make_deployment':
            p['measures']=[dict(label=r['label'],low=r['value'],high=r['value'],unit='JH') for r in deployment['rows']]
    return d
