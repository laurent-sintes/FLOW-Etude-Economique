"""Replay explicit functional sizing hypotheses without changing adopted effort."""
from copy import deepcopy
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read
from estimation_calculation import formula

SOURCE='source/comptage-cosmic-mdm.yaml'
SCHEMA='source/schema-comptage-cosmic-mdm.yaml'

def dependencies():
    doc=read(ROOT/SOURCE)
    return {SOURCE,SCHEMA,'tools/mdm_cosmic.py',doc['benchmark_ref'],*doc['proof_refs']}

def project(doc,benchmark,expected_caps,rule_function=formula):
    ids=[p['id'] for p in doc['processes']]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate MDM process')
    caps={c for p in doc['processes'] for c in p['capability_refs']}
    if caps!=set(expected_caps):raise ValueError('MDM COSMIC scope mismatch')
    rows=[]
    for p in doc['processes']:
        movements=p['movements']
        if not movements['E'] or not (movements['W'] or movements['X']):raise ValueError('Incomplete MDM process')
        if any(len(v)!=len(set(v)) for v in movements.values()):raise ValueError('Duplicate MDM movement')
        rows.append(dict(deepcopy(p),cfp=sum(len(v) for v in movements.values())))
    cfp=sum(p['cfp'] for p in rows)
    params=dict(hours_per_CFP=benchmark['retained_hours_per_CFP'],factor=benchmark['retained_factor'],day_hours=doc['day_hours'])
    jh=rule_function('cosmic_effort',CFP=cfp,**params)
    return dict(id=doc['id'],cfp=cfp,jh=jh,parameters=params,processes=rows,
                groups=[dict(id=g,cfp=sum(p['cfp'] for p in rows if p['group']==g)) for g in ('common','studio','families')],
                counting_basis=doc['counting_basis'],boundary=doc['boundary'],family_rule=doc['family_rule'],activity_scope=doc['activity_scope'],
                proof_refs=[SOURCE,doc['benchmark_ref'],*doc['proof_refs']])

def calculate(expected_caps):
    doc=read(ROOT/SOURCE)
    Draft202012Validator(read(ROOT/SCHEMA)).validate(doc)
    return project(doc,read(ROOT/doc['benchmark_ref']),expected_caps)
