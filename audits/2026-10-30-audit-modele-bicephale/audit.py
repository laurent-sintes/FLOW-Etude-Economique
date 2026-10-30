"""Read-only audit of active inputs; fault probes use isolated in-memory copies."""
from pathlib import Path
from copy import deepcopy
from collections import Counter
from unittest.mock import patch
import hashlib, json, math, sys
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
from validate_stacks import read
from model_context import model_session
from estimation_calculation import calculate, formula, metamodel
from retained_core import validate, coverage
from capability_catalog import analysis

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def active_hashes():
    return {p.relative_to(ROOT).as_posix():sha(p) for folder in ('source','sources','config','tools','app/src')
            for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in ('.yaml','.yml','.json','.py','.ts','.tsx','.css','.md')}
before=active_hashes()
with model_session() as snapshot:
    doc=validate()
    binding=doc['units'][0]['calculation']
    result=calculate(binding)
    active_dependencies={p.relative_to(ROOT).as_posix():h for p,h in snapshot.digests.items()}
previous=load(binding['evidence']['path']); allocation=load(binding['allocation']['path'])
probes=[]
def attempt(name,fn,expected):
    try:
        value=fn();probes.append(dict(id=name,expected=expected,actual='accepted',value=value))
    except Exception as e:probes.append(dict(id=name,expected=expected,actual='rejected',error=type(e).__name__+': '+str(e)))
def wrong_family():
    changed=deepcopy(doc); unit=deepcopy(changed['units'][0]); target=next(r for r in analysis()['blocs'] if r['id']=='BC-008')
    unit.update(id='audit-false-policy-estimate',label='Audit only: other family',capabilities=[dict(id=target['id'],native_id=target['capacite_id'])])
    changed['units'].append(unit)
    valid=validate(changed)
    return dict(units=len(valid['units']),total_jh=sum(u['total_jh'] for u in valid['units']),same_calculation=True)
def wrong_stack():
    changed=deepcopy(doc);changed['units'][0]['stack']='rust'
    valid=validate(changed)
    return dict(stack=valid['units'][0]['stack'],total_jh=valid['units'][0]['total_jh'])
def run_modified(change):
    evidence,inputs=deepcopy(previous),deepcopy(allocation)
    change(evidence,inputs)
    with patch('estimation_calculation.checked',side_effect=[evidence,inputs]):
        value=calculate(binding)
    return dict(total_jh=value['total_jh'],roles=value['roles'],functional_jh=value['alignment']['functional']['jh'],comparability=value['alignment']['comparability_status'])
attempt('calculation_reused_for_unrelated_family',wrong_family,'reject scope mismatch')
attempt('java_calculation_declared_as_rust',wrong_stack,'reject unproved stack transfer')
attempt('negative_activity_weight',lambda:run_modified(lambda e,i:i['activity_role_weights']['environment'].update(plateforme=-0.1,dev_java=1.1)),'reject negative allocation weight')
attempt('extra_phase_column',lambda:run_modified(lambda e,i:e['activity_source']['activities'][0]['percent_by_phase'].append(999)),'reject unmatched phase column')
attempt('different_day_conventions',lambda:run_modified(lambda e,i:e['functional'].update(day_hours=8)),'reject or mark unit mismatch')
attempt('invalid_common_complements_split',lambda:run_modified(lambda e,i:e['rows'][0].update(common_jh=1,flow_complements_jh=1)),'reject component total mismatch')
attempt('negative_functional_size',lambda:formula('cosmic_effort',CFP=-420,hours_per_CFP=20,factor=1,day_hours=7),'reject negative functional size')
full=coverage([dict(capabilities=[dict(id=b['id']) for b in analysis()['blocs']])],[b['id'] for b in analysis()['blocs']])

native=load('audits/2026-10-30-master-data-comparable-reuse/results.json')
inputs=load('audits/2026-10-30-master-data-comparable-reuse/inputs.json')
measures=load('audits/2026-10-30-master-data-comparable-reuse/measurements.json')
scenario=next(s for s in inputs['scenarios'] if s['id']=='central');c=inputs['cocomo']
E=c['B']+.01*c['SF_sum'];F=c['D']+.2*(E-c['B'])
a=(scenario['AA']+.3*scenario['IM'])/100
rows=[]
for entry in native['results']:
    sizes=measures['summary'][entry['id']]; n=sizes['new'];r=sizes['reused'];w=scenario['declarative_weight']
    k=(n['program_units']+w*n['declarative_units']+a*(r['program_units']+w*r['declarative_units']))/1000
    effort=lambda size: c['A']*size**E*scenario['PERS']*scenario['PREX']*c['other_EM']*c['month_hours']/c['day_hours']*c['effort_phase_factor']
    common=effort(k);total=effort(k+previous['size']['proposed_complements_units']/1000)
    original=next(x for x in previous['rows'] if x['id']==entry['id'])
    assert math.isclose(total,original['total_jh'],rel_tol=1e-12)
    assert math.isclose(common,original['common_jh'],rel_tol=1e-12)
    rows.append(dict(id=entry['id'],common_jh=common,complements_jh=total-common,total_jh=total,complements_pct=100*(total-common)/total))
cosmic=load('audits/2026-10-30-master-data-spring-flow/cosmic-candidate.json')
groups={g['id'] for g in cosmic['groups']}; issues=[];movements=Counter()
for process in cosmic['processes']:
    keys=[(m['type'],m['group']) for m in process['movements']]
    if len(keys)!=len(set(keys)):issues.append(dict(process=process['id'],reason='repeated group/type requires semantic review'))
    assert all(m['type'] in 'ERWX' and m['cfp']==1 and m['group'] in groups for m in process['movements'])
    assert sum(m['cfp'] for m in process['movements'])==process['count']['cfp']
    movements.update(m['type'] for m in process['movements'])
cfp=sum(movements.values());assert cfp==previous['functional']['CFP']==420
nested=[]
for name,expected in previous['input_hashes'].items():
    path=ROOT/name
    nested.append(dict(path=name,exists=path.is_file(),matches=path.is_file() and sha(path)==expected,active_dependency=name in active_dependencies))
files=[]
for row in measures['files']:
    path=ROOT/measures['repos'][row['repo']]['root']/row['path']
    if not path.is_file() or sha(path)!=row['sha256']:files.append(dict(path=str(path),exists=path.is_file()))
# Independently reconcile recorded file measures and complement construction.
for product, totals in measures['summary'].items():
    for treatment in ('new','reused'):
        selected=[r for r in measures['files'] if r['product']==product and r['treatment']==treatment]
        assert len(selected)==totals[treatment]['files']
        for key in ('program_units','declarative_units'):
            assert sum(r[key] for r in selected)==totals[treatment][key]
pinput=load('audits/2026-10-30-master-data-spring-flow/inputs.json')
analogues=load('audits/2026-10-30-master-data-spring-flow/analogues.json')
u=pinput['schema_units']; w=1
parts=dict(blocks=sum(b['quantity']*analogues['unit_bank'][b['kind']]['range'][1] for b in pinput['blocks']))
parts['schemas']=sum(len(sc['fields'])*u['program_per_field'][1]+w*(len(sc['fields'])*(u['declarative_per_field'][1]+u['ui_declarative_per_field'][1])+int(sc['new_model'])*(u['declarative_per_new_model'][1]+u['ui_declarative_per_new_model'][1])) for sc in pinput['schemas'])
parts['configuration']=sum(x['quantity']*x['unit_range'][1]*w for x in pinput['configuration'])
parts['structure']=5*len({b['id'].split('/')[0] for b in pinput['blocks']})
changes=load('audits/2026-10-30-master-data-spring-reprise/treatment-mapping.json')
methods={m['id']:m for m in load('audits/2026-10-30-master-data-spring-reprise/method-measures.json')}
for change in changes:
    assert sum(methods[k]['program_units'] for k in change['method_refs'])==change['proposed_units']
assert math.isclose(sum(parts.values()),previous['size']['previous_complements_units'])
parts['method_refinement']=sum(x['proposed_units']-x['previous_units'] for x in changes)
assert math.isclose(sum(parts.values()),previous['size']['proposed_complements_units'])
preparation=dict(recorded_file_measures_reconciled=True,complement_parts=parts,total_equivalent_complement_units=sum(parts.values()),refined_treatments=len(changes),method_samples=len(methods),boundary='Recomposition depuis les mesures enregistrées et empreintes de code, pas nouvelle validation sémantique des analogies.')

metadoc=read(ROOT/'source/fondamentaux.yaml')['estimation_model']
exports=read(ROOT/'app/dist/exports/flow-modele-metier.yaml')
export_missing=[r['path'] for r in nested if r['path'].endswith(('.json','.yaml','.yml')) and r['path'] not in exports['model']]
# Illustrative same-E modules: illustrates consolidation policy, not a new estimate.
k=next(r for r in previous['rows'] if r['id']=='axelor')['equivalent_KSLOC']
def effort(size):return c['A']*size**E*c['other_EM']*c['month_hours']/c['day_hours']*c['effort_phase_factor']
anchor=next(r for r in rows if r['id']=='axelor')
report=dict(status='audit_completed_with_findings',active_estimates_changed=False,
 baseline=dict(total_jh=result['total_jh'],months=result['months'],unrounded_months=result['unrounded_months'],roles=result['roles'],rows=rows,
 functional_jh=result['alignment']['functional']['jh'],gap_pct=result['alignment']['functional']['gap_pct'],spread_pct=result['alignment']['spread_pct'],rounding_jh=result['alignment']['rounding_delta_jh']),
 mathematical_checks=dict(preparation=preparation,E=E,F=F,AAM=a,recomputed_four_references=True,role_total=sum(result['roles'].values()),activity_total=sum(r['jh'] for r in result['activities']),
 cosmic_recount=dict(processes=len(cosmic['processes']),groups=len(groups),CFP=cfp,movements=dict(movements),structural_issues=issues)),
 probes=probes,full_coverage_probe=full,
 provenance=dict(nested_inputs=nested,measured_code_files=len(measures['files']),code_hash_failures=files,missing_upstream_inputs_in_download=export_missing,active_dependencies=active_dependencies),
 model=dict(objects=len(metadoc['objects']),relations=len(metadoc['relations']),rules=len(metadoc['rules']),arithmetic_rules=sum(r['kind']=='arithmetic' for r in metadoc['rules']),algorithm_rules=sum(r['kind']=='algorithm' for r in metadoc['rules'])),
 illustrative_sensitivity=dict(not_a_new_estimate=True,complement_size_plus_10pct_jh=effort(k+previous['size']['proposed_complements_units']/10000)-anchor['total_jh'],
 COCOMO_equivalent_hours_per_CFP=anchor['total_jh']*7/cfp,
 independent_twins_jh=2*effort(k),single_integrated_twins_jh=effort(2*k),integrated_vs_sum_pct=100*(effort(2*k)/(2*effort(k))-1)))
after=active_hashes();assert before==after,'Audit changed active files'
report['unchanged_files']=len(before)
(OUT/'evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'active-input-hashes.json').write_text(json.dumps(before,indent=2),encoding='utf-8')
print(json.dumps(dict(status=report['status'],baseline=report['baseline'],probes=probes,code_hash_failures=len(files),nested_hash_failures=sum(not r['matches'] for r in nested),export_missing=export_missing,unchanged_files=len(before)),ensure_ascii=False,indent=2))
