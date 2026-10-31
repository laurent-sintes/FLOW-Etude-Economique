"""Trace a gap instruction to existing funding, without inventing a size or effort."""
from copy import deepcopy
from pathlib import Path
import hashlib
from validate_stacks import ROOT,read
from model_context import CURRENT


def _require(ok,reason):
    if not ok:raise ValueError('ERR_GAP_INSTRUCTION '+reason)

def _evidence(name,expected,*,code=False):
    path=(ROOT/name).resolve()
    _require(name.startswith('audits/') and path.is_relative_to(ROOT.resolve()) and path.is_file(),'invalid evidence path')
    session=CURRENT.get()
    if session is not None:
        if code:value=session.read(path,lambda text:text)
        else:value=read(path)
        digest=session.digests[path]
    else:
        raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        value=raw.decode('utf-8-sig') if code else read(path)
    _require(digest==expected,'evidence digest changed')
    return value

def compile_gap_instruction(case,gap,grid,sources,mechanisms,retained):
    result=deepcopy(case)
    needs={n['id']:b for b in grid['blocs'] for n in b['fonctions']}
    ids=[c['id'] for c in case['criteria']];_require(len(ids)==len(set(ids)),'duplicate criterion')
    for c in case['criteria']:
        _require(c['need_refs'] and set(c['need_refs'])<=set(needs),'criterion need mismatch')
        _require(c['evidence_refs'] and set(c['evidence_refs'])<=set(sources),'criterion evidence mismatch')
        _require(c['mechanism_refs'] and set(c['mechanism_refs'])<=set(mechanisms),'criterion funding mismatch')
    for followup in case['buy_followup']:
        _require(followup['product_ref'] in gap['product_refs'],'Buy product mismatch')
        _require(set(followup['evidence_refs'])<=set(sources),'Buy evidence mismatch')
    experiment=case['experiment']
    report=_evidence(experiment['report_ref'],experiment['report_sha256'])
    _evidence(experiment['implementation_ref'],experiment['implementation_sha256'],code=True)
    _require(report['status']=='passed' and report['tests']>0,'experiment incomplete')
    # Its success documents this experiment only. It cannot qualify the ERP or calibrate JH.
    _require(case['status']=='qualification_partielle','experiment cannot promote qualification')
    q=case['quantification']
    _require(all(q[k] is None for k in ('new_equivalent_units','new_cfp','net_extra_jh')),'unjustified incremental estimate')
    registry=read(ROOT/'source/calculs-estimation-core.yaml')
    contract=next((x for x in registry['calculations'] if x['id']==q['calculation_ref']),None)
    _require(contract is not None and contract['stack']=='java-spring','calculation reference mismatch')
    _require(contract['recipe']=='coherent_components_v1','unsupported baseline boundary')
    from estimation_components import unpack_archives
    archived=unpack_archives(read(ROOT/contract['inputs']['archives']))
    families={f['slug']:f for f in archived['proposal_inputs']['families']}
    spec=read(ROOT/contract['inputs']['specification'])
    _require(set(q['family_refs'])<=set(spec['families']),'families outside coherent unit')
    _require('backlog' in q['family_refs'],'allocation baseline missing')
    from estimation_calculation import calculate
    calculation=calculate({'id':q['calculation_ref']})
    unit=next((u for u in retained if u['id']==contract['unit_id']),None)
    _require(unit is not None and unit['total_jh']==calculation['total_jh'],'adopted baseline mismatch')
    cosmic=read(ROOT/contract['inputs']['cosmic'])
    processes=[p for p in cosmic['processes'] if p['id'].startswith('backlog-')]
    backlog=families['backlog'];bank=[b for b in backlog['bindings'] if b['repo']=='axelor' and not b['provided_kernel']]
    allocations={x['id']:x for x in calculation['trace']['component_allocations']}
    result['baseline']=dict(unit_id=unit['id'],unit_label=unit['label'],adopted_jh=unit['total_jh'],
        unrounded_jh=calculation['alignment']['reference_jh'],equivalent_units=calculation['trace']['component_sizes']['axelor']['equivalent_units'],
        internal_backlog_jh=allocations['backlog']['jh'],backlog_cfp=sum(len(p['movements']) for p in processes),
        selected_axelor_units=sum(len(b['atoms']) for b in bank),module_quantity=backlog['quantity'],analogy_fraction=backlog['extension_fraction'],
        schemas=deepcopy(backlog['schemas']),processes=[dict(id=p['id'],label=p['label'],movements=[dict(type=m['type'],group=m['group']) for m in p['movements']]) for p in processes],
        family_allocations=[deepcopy(allocations[f]) for f in q['family_refs']],
        source_paths=[contract['inputs']['archives'],contract['inputs']['specification'],contract['inputs']['cosmic']])
    result['experiment_result']=dict(tests=report['tests'],status=report['status'],scope=report['scope'])
    for c in result['criteria']:
        c['funding']=[dict(id=k,label=mechanisms[k]['label'],owner=mechanisms[k]['funding_owner']) for k in c['mechanism_refs']]
    return result
