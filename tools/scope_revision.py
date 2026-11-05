"""Versioned native scope revisions. Proposals never enter retained funding."""
from copy import deepcopy
from decimal import Decimal
import hashlib
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read
from core_product_estimate import apportioned
from work_estimation import price_roles, money

SOURCE='source/revision-master-data.yaml'
SCHEMA='source/schema-revision-perimetre.yaml'

def dependencies():
    d=read(ROOT/SOURCE)
    return {SOURCE,SCHEMA,d['capture']['path'],d['baseline']['proof'],d['baseline']['scope']['path'],d['svg_ref'],'tools/scope_revision.py'}|({d['adoption']['decision_ref']['path']} if d.get('adoption') else set())

def require(ok,message):
    if not ok:raise ValueError('ERR_SCOPE_REVISION: '+message)

def compile_revision(core_units,source=None):
    d=deepcopy(source if source is not None else read(ROOT/SOURCE))
    Draft202012Validator(read(ROOT/SCHEMA)).validate(d)
    capture=d['capture'];path=(ROOT/capture['path']).resolve()
    require(path.is_relative_to(ROOT.resolve()) and path.is_file(),'Invalid capture path')
    require(hashlib.sha256(path.read_bytes()).hexdigest()==capture['sha256'],'Capture changed')
    native=read(path);nodes={n['id']:n for n in native['nodes']}
    children={}
    for r in native['relations']:
        if r['type'] in ('contains','presents'):children.setdefault(r['source_id'],[]).append(r['target_id'])
    def descendants(id):
        seen=set();pending=[id]
        while pending:
            n=pending.pop()
            if n in seen:continue
            seen.add(n);pending+=children.get(n,[])
        return seen
    caps=lambda id:{n for n in descendants(id) if nodes[n]['kind']=='capability'}
    mdm=caps('domain-master-data');scm=caps('supply-chain-orchestration');local=caps('business-references')
    require(len(mdm)==33 and local=={'master-data-ingestion'},'Unexpected revision scope')
    ids=[p['id'] for p in d['packages']]
    require(len(ids)==len(set(ids)),'Duplicate package')
    groups={g['id'] for g in d['groups']}
    require(len(groups)==len(d['groups']) and groups=={'scm','common','families'},'Group scope')
    for p in d['packages']:
        require(p['group'] in groups and type(p['jh']) is int and p['jh']>0,'Invalid package effort')
        require(p['estimate_kind']=='engineering_assumption','Unsupported measurement claim')
        refs=p['capability_refs']
        require(refs and len(refs)==len(set(refs)) and set(refs)<=(local if p['group']=='scm' else mdm),'Package outside its native scope')
    require({c for p in d['packages'] for c in p['capability_refs']}==mdm|local,'Incomplete native coverage')
    if d['status']=='adopted':
        ref=d['adoption']['baseline_ref'];raw=(ROOT/ref['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest()==ref['sha256'],'Adopted baseline changed')
        basis=read(ROOT/ref['path']);old=deepcopy(basis['reference_unit'])
        rates={r['id']:r['rate_eur_jh'] for u in core_units if u['id']==old['id'] for r in u['roles']}
        for role in old['roles']:role['rate_eur_jh']=rates[role['id']]
        tools=read(ROOT/'source/calibration-couts.yaml')['couts_communs']['outillage_realisation_eur_par_jh']
        old['cost_eur_ht']=money(sum(Decimal(str(r['jh']))*Decimal(str(r['rate_eur_jh'])) for r in old['roles'])+Decimal(str(tools))*old['total_jh'])
    else:
        old=next(u for u in core_units if u['id']==d['baseline']['unit_ref'])
    require(d['work_unit_ref']=='core/'+old['id'] and d['phase_ref']=='acquisition' and d['option_ref']=='java-spring','Wrong replacement binding')
    retained=next(u for u in read(ROOT/d['baseline']['path'])['units'] if u['id']==old['id'])
    require(retained['provenance']['path']==d['baseline']['proof'] and retained['provenance']['sha256']==d['baseline']['sha256'],'Wrong retained proof')
    proof=(ROOT/d['baseline']['proof']).resolve()
    require(proof.is_relative_to(ROOT.resolve()) and hashlib.sha256(proof.read_bytes()).hexdigest()==d['baseline']['sha256'],'Retained proof changed')
    require(old['total_jh']==retained['total_jh'],'Reference effort drift')
    scope=d['baseline']['scope'];scope_path=(ROOT/scope['path']).resolve()
    require(scope_path.is_relative_to(ROOT.resolve()) and hashlib.sha256(scope_path.read_bytes()).hexdigest()==scope['sha256'],'Retained work scope changed')
    prior=next(u for u in read(scope_path)['units'] if u['id']==old['id'])['work']
    require(sum(w['jh'] for w in prior)==old['total_jh'],'Prior work does not reconcile')
    cross=d['crosswalk']
    require(len(cross)==len(prior) and {c['baseline_package'] for c in cross}=={w['id'] for w in prior},'Incomplete replacement crosswalk')
    require(all(set(c['target_packages'])<=set(ids) for c in cross),'Unknown replacement package')
    d['prior_work']=[dict(id=w['id'],label=w['label'],jh=w['jh'],target_packages=next(c['target_packages'] for c in cross if c['baseline_package']==w['id'])) for w in prior]

    tools=read(ROOT/'source/calibration-couts.yaml')['couts_communs']['outillage_realisation_eur_par_jh']
    weights={r['id']:r['jh'] for r in old['roles']}
    for g in d['groups']:
        g['jh']=sum(p['jh'] for p in d['packages'] if p['group']==g['id'])
        allocated=apportioned(g['jh'],weights)
        g['roles']=price_roles([dict(id=r['id'],label=r['label'],net_jh=allocated[r['id']],rate_eur_jh=r['rate_eur_jh']) for r in old['roles']])
        g['labour_eur_ht']=money(sum(Decimal(str(r['labour_eur_ht'])) for r in g['roles']))
        g['tooling_eur_ht']=money(Decimal(g['jh'])*Decimal(str(tools)))
        g['cost_eur_ht']=money(Decimal(str(g['labour_eur_ht']))+Decimal(str(g['tooling_eur_ht'])))
    d['proposed']={k:sum(g[k] for g in d['groups']) for k in ('jh','labour_eur_ht','tooling_eur_ht','cost_eur_ht')}
    refs=[ref for lot in d['lots'] for ref in lot['group_refs']]
    require(len(refs)==len(set(refs)) and set(refs)==groups,'Lots must partition all groups once')
    require(len(d['lots'])==len({lot['id'] for lot in d['lots']}),'Duplicate lot')
    for lot in d['lots']:
        lot.update({k:sum(g[k] for g in d['groups'] if g['id'] in lot['group_refs']) for k in ('jh','labour_eur_ht','tooling_eur_ht','cost_eur_ht')})
    d['reference']=dict(jh=old['total_jh'],cost_eur_ht=old['cost_eur_ht'])
    d['delta']={k:money(Decimal(str(d['proposed'][k]))-Decimal(str(d['reference'][k]))) for k in ('jh','cost_eur_ht')}
    current=dict(jh=sum(u['total_jh'] for u in core_units),cost_eur_ht=money(sum(Decimal(str(u['cost_eur_ht'])) for u in core_units)))
    d['core_reference']={k:money(Decimal(str(current[k]))-Decimal(str(d['delta'][k]))) for k in current} if d['status']=='adopted' else current
    d['core_proposed']={k:money(Decimal(str(d['core_reference'][k]))+Decimal(str(d['delta'][k]))) for k in ('jh','cost_eur_ht')}
    d['historical']=d['status']=='adopted' and next(u for u in core_units if u['id']==old['id'])['provenance']['path']!=d['adoption']['decision_ref']['path']
    if d['historical']:
        ref=d['adoption']['decision_ref']
        raw=(ROOT/ref['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest()==ref['sha256'],'Historical decision changed')
        decision=read(ROOT/ref['path'])
        d['core_reference']=dict(jh=decision['adopted_jh'],cost_eur_ht=decision['previous_cost_eur_ht'])
        d['core_proposed']=dict(jh=decision['proposal_jh'],cost_eur_ht=decision['construction_cost_eur_ht'])
    d['scope']=dict(master_data_capabilities=len(mdm),scm_capabilities=len(scm),total_capabilities=len(mdm|scm),replaced_capabilities=len(old['capabilities']),target_lot_capabilities=len(mdm|local),removed=[c['native_id'] for c in old['capabilities'] if c['native_id'] not in scm])
    d['hierarchy']=[]
    for id in ('domain-master-data','supply-chain-orchestration'):
        d['hierarchy'].append(dict(id=id,label=nodes[id]['fields']['name'],count=len(caps(id)),subdomains=[dict(id=s,label=nodes[s]['fields']['name'],count=len(caps(s)),capabilities=[dict(id=c,label=nodes[c]['fields']['name']) for c in nodes if c in caps(s)]) for s in children[id] if nodes[s]['kind']=='area']))
    d['native_version']=native['version']
    for impact in d['impacts']:
        if impact['id']=='build':
            impact['extra_jh']=d['delta']['jh'];impact['extra_eur_ht']=d['delta']['cost_eur_ht']
    # Context summary is independent of the scope used by retained calculations.
    d['provenance']=dict(source=capture['origin'],sha256=capture['sha256'],as_of=capture['as_of'])
    return d


def prepare_scope_adoption(documents,contract,registry,formula,use_cache=False):
    """Replay the frozen baseline, then apply the adopted disjoint native-scope lots."""
    from estimation_preparation import prepare
    from estimation_inputs import digest
    basis=documents[contract['inputs']['revision_basis']]
    scope=documents[contract['inputs']['revision_proposal']]
    decision=documents[contract['inputs']['revision_hypotheses']]
    require(basis['id']=='native-scope-adoption-basis' and scope['id']=='adopted-native-scope','Invalid scope adoption proofs')
    require(decision['status']=='adopted' and decision['scope_revision_id']==scope['revision']['id'],'Scope adoption decision mismatch')
    row=next(r for r in scope['units'] if r['id']==contract['unit_id'])
    require(contract['scope']==row['scope'] and contract['funding_claims']==row['funding_claims'],'Scope or funding proof mismatch')
    original=next(c for c in basis['registry']['calculations'] if c['unit_id']==basis['reference_unit']['id'])
    prior=prepare(documents,original,basis['registry'],formula,use_cache=use_cache)
    ids=row['package_refs'];require(ids and len(ids)==len(set(ids)),'Duplicate scope work')
    work=[p for p in scope['revision']['packages'] if p['id'] in ids]
    require(len(work)==len(ids) and all(p['estimate_kind']=='engineering_assumption' for p in work),'Unknown scope package')
    all_ids=[p for u in scope['units'] for p in u['package_refs']]
    require(len(all_ids)==len(set(all_ids)) and set(all_ids)=={p['id'] for p in scope['revision']['packages']},'Scope work must be funded once')
    days=sum(p['jh'] for p in work);require(days==row['total_jh'] and days==sum(row['roles'].values()),'Scope role effort drift')
    require(row['scope']['native_source']==scope['native_source'],'Scope capture binding drift')
    native=scope['native_capture'];require(digest(scope['analysis']['blocs'])==scope['analysis_digest'],'Scope analysis proof changed')
    selected=[b for b in scope['analysis']['blocs'] if b['id'] in {c['id'] for c in row['scope']['capabilities']}]
    require(digest(selected)==row['scope']['analysis_sha256'],'Native scope analysis drift')
    edges={(r['source_id'],r['target_id']) for r in native['relations']}
    require(all(all(pair in edges for pair in zip(b['chemin'],b['chemin'][1:])) for b in selected),'Native hierarchy drift')
    prior['method']='Estimation détaillée par livrable';prior['retained_effort_jh']=days
    prior['allocation'].update(role_effort_jh=deepcopy(row['roles']),rounding_jh=1,role_allocation_basis='Ventilation des ensembles de travaux adoptés. Chaque JH et chaque rôle sont consommés une fois.')
    prior['trace']['work_package_adoption']=dict(work=[dict(id=p['id'],label=p['label'],jh=p['jh'],scope=p['deliverable'],reuse=scope['revision']['assumptions'][2],scenario_refs=[scope['revision']['id']],funding_ref=row['funded_work_ref'],effort_status='engineering_assumption_not_observed') for p in work],previous_jh=basis['reference_unit']['total_jh'] if row['id']==basis['reference_unit']['id'] else 0,retained_jh=days,comparison_scope='historical',effort_status='engineering_assumption_not_observed')
    prior['trace']['native_scope_adoption']=dict(revision_id=scope['revision']['id'],lot_ref=row['lot_ref'],native_source=deepcopy(scope['native_source']),decision_ref=contract['inputs']['revision_hypotheses'])
    return prior
