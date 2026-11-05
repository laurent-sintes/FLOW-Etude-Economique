"""Common estimation contracts. Reference figures stay source-owned and immutable."""
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP
import math
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read
from calculate_costs import annual_work_valuation, role_rates, volume
from retained_core import referenced_value
from current_cost_inputs import active_doc
from model_inputs import annual_scenario

SCHEMA='source/schema-contrat-estimation.yaml'
LABELS='config/contrat-estimation.yaml'


def dependencies():
    spec=read(ROOT/'source/unites-travail.yaml')
    paths={r['rate_ref']['path'] for u in spec['units'] for r in (u['estimation_contract']['proposal']['roles'] or []) if r['rate_ref']}
    return {SCHEMA,LABELS,'tools/work_estimation.py','source/maintenance/maintenance-java-spring.yaml'} | paths


def require(ok,message):
    if not ok:raise ValueError('ERR_WORK_ESTIMATE: '+message)


def money(value):
    return float(Decimal(str(value)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))


def total(values):
    return None if any(v is None for v in values) or not values else float(sum(Decimal(str(v)) for v in values))


def price_roles(roles):
    """Net effort prices each role. Unknown net effort or rate keeps cost unknown."""
    result=deepcopy(roles)
    for r in result:
        r['labour_eur_ht']=None if r['net_jh'] is None or r['rate_eur_jh'] is None else money(Decimal(str(r['net_jh']))*Decimal(str(r['rate_eur_jh'])))
    return result


def quantity_estimate(proposal):
    """A proposal never replaces a reference or enters the funding ledger."""
    mode=proposal.get('cost_mode') or ('human' if proposal['roles'] else None)
    if mode in ('fixed_purchase','resource_usage','included'):
        require(not proposal['roles'], 'Nonhuman estimate cannot contain human roles')
        amount=proposal['expenses_eur_ht'];quantity=proposal['quantity'];price=proposal.get('unit_price_eur_ht')
        for value in (amount,quantity,price):
            require(value is None or type(value) in (int,float) and math.isfinite(value) and value>=0,'Invalid nonhuman price or quantity')
        if mode=='resource_usage':
            amount=None if any(v is None for v in (amount,quantity,price)) else money(Decimal(str(amount))+Decimal(str(quantity))*Decimal(str(price)))
        if mode=='included': amount=None
        scope=all(proposal.get(k) for k in ('deliverable','acceptance','assumptions','evidence_refs'))
        complete=scope and (bool(proposal.get('included_in_ref')) if mode=='included' else amount is not None and bool(proposal.get('billing_period')))
        if mode=='resource_usage':complete=complete and all(proposal.get(k) for k in ('count_unit','counting_rule','quantity_basis'))
        return dict(status='proposal' if complete else 'to_complete',cost_mode=mode,human_applicable=False,roles=[],gross_jh=None,net_jh=None,labour_eur_ht=None,non_labour_eur_ht=amount,cost_eur_ht=amount)
    rows=proposal['roles']
    expenses=proposal['expenses_eur_ht']
    require(expenses is None or type(expenses) in (int,float) and math.isfinite(expenses) and expenses>=0,'Invalid proposal expenses')
    require(proposal['quantity'] is None or type(proposal['quantity']) in (int,float) and math.isfinite(proposal['quantity']) and proposal['quantity']>=0,'Invalid quantity')
    if rows is None:return dict(status='to_complete',cost_mode=mode,human_applicable=True,roles=[],gross_jh=None,net_jh=None,labour_eur_ht=None,non_labour_eur_ht=expenses,cost_eur_ht=None)
    require(len(rows)==len({r['id'] for r in rows}),'Duplicate proposal role')
    valued=[]
    for r in rows:
        for k in ('fixed_jh','unit_jh','gain_pct','rate_eur_jh'):
            v=r[k];require(v is None or type(v) in (int,float) and math.isfinite(v) and v>=0,'Invalid proposal '+k)
        require(r['gain_pct'] is None or r['gain_pct']<=100,'Invalid gain')
        rate=None
        if r['rate_ref'] is not None:
            ref=r['rate_ref'];path=(ROOT/ref['path']).resolve()
            require(path.is_relative_to(ROOT.resolve()) and path.is_file(),'Invalid rate source')
            require(r['rate_eur_jh'] is None,'Ambiguous proposal rate')
            require(path.suffix in {'.yaml','.yml','.json'},'Invalid rate document')
            try:rate=referenced_value(ref)
            except (KeyError,ValueError,StopIteration,TypeError) as error:
                raise ValueError('ERR_WORK_ESTIMATE: Unknown rate pointer') from error
            require(type(rate) in (int,float) and math.isfinite(rate) and rate>=0,'Invalid referenced rate')
        require(r['rate_eur_jh'] is None or rate is None,'Ambiguous proposal rate')
        rate=r['rate_eur_jh'] if rate is None else rate
        gross=None if proposal['quantity'] is None or r['fixed_jh'] is None or r['unit_jh'] is None else r['fixed_jh']+proposal['quantity']*r['unit_jh']
        net=None if gross is None or r['gain_pct'] is None else gross*(1-r['gain_pct']/100)
        valued.append(dict(id=r['id'],label=r['label'],gross_jh=gross,gain_pct=r['gain_pct'],net_jh=net,rate_eur_jh=rate,source_ref=r['rate_ref']))
    valued=price_roles(valued);labour=total([r['labour_eur_ht'] for r in valued]);expenses=proposal['expenses_eur_ht']
    require(expenses is None or type(expenses) in (int,float) and math.isfinite(expenses) and expenses>=0,'Invalid proposal expenses')
    cost=None if labour is None or expenses is None else money(Decimal(str(labour))+Decimal(str(expenses)))
    complete=cost is not None and bool(proposal['deliverable']) and bool(proposal['acceptance']) and bool(proposal['count_unit']) and bool(proposal['counting_rule']) and bool(proposal['quantity_basis']) and bool(proposal['assumptions']) and bool(proposal['evidence_refs'])
    return dict(status='proposal' if complete else 'to_complete',cost_mode=mode,human_applicable=True,non_labour_eur_ht=expenses,roles=valued,gross_jh=total([r['gross_jh'] for r in valued]),net_jh=total([r['net_jh'] for r in valued]),labour_eur_ht=labour,cost_eur_ht=cost)


def annual_context():
    doc=active_doc('java-spring');cal=read(ROOT/'source/calibration-couts.yaml')
    return dict(volume_labels=read(ROOT/'source/evaluation-charges-brutes.yaml')['labels']['volume_labels'],work={r['activite']:r for r in doc['maintenance']['activites']},
                activities={r['id']:r for r in read(ROOT/'source/maintenance/maintenance-java-spring.yaml')['activites']},
                scenario=annual_scenario(),rates=role_rates(read(ROOT/'source/stacks/java-spring.yaml')),
                tools=cal['couts_communs']['outillage_realisation_eur_par_jh'])


def annual_roles(row,context):
    roles=context['activities'][row['activite']]['roles']
    valued=annual_work_valuation(row,roles,context['rates'],context['scenario'],context['tools'])
    lines=price_roles([dict(id=id,label=read(ROOT/'source/maintenance.yaml')['roles'][id]['nom'],gross_jh=valued['gross_jh']*r['part_pct']/100,
                           gain_pct=valued['gain_pct'],net_jh=valued['net_jh']*r['part_pct']/100,rate_eur_jh=context['rates'][id],
                           source_ref='source/maintenance/maintenance-java-spring.yaml#'+row['activite']) for id,r in roles.items() if r['part_pct']])
    return lines,valued


def build_estimate(unit,core,context):
    spec=deepcopy(unit['estimation_contract'])
    Draft202012Validator(read(ROOT/SCHEMA)).validate(spec)
    require(spec['option_ref']=='java-spring','Unsupported reference option')
    proposal=quantity_estimate(spec['proposal'])
    records=unit['measurements'];details=unit['detail'];uid=unit['id'];aid=uid.split('/')[-1]
    method='pending';role_lines=[];terms=[];gains=None;scope=unit.get('outcome');acceptance=None;boundary=None
    source_refs=sorted({r['source_ref'] for r in records});calculation_ref=None
    if details:
        method='quantity_roles';scope=details['deliverable'];acceptance=deepcopy(details['acceptance']);boundary=details['boundary']
        terms=[dict(id='quantity',quantity=details['quantity'],unit=details['count_unit'],unit_jh=None,basis=details['quantity_basis'],counting_rule=details['counting_rule'])]
        source_refs.append('source/unites-integration.yaml#'+unit['integration_unit_ref'])
        role_names=read(ROOT/'source/integration.yaml')['roles']
        role_lines=price_roles([dict(id=id,label=role_names[id]['nom'],gross_jh=None,gain_pct=None,net_jh=None,rate_eur_jh=context['rates'].get(id),source_ref='source/stacks/java-spring.yaml#interventions') for id in role_names])
    if uid.startswith('core/'):
        method='retained_core';u=core[aid];calculation_ref=u['calculation']['id']
        role_lines=price_roles([dict(id=r['id'],label=r['label'],gross_jh=None,gain_pct=None,net_jh=r['jh'],rate_eur_jh=r['rate_eur_jh'],source_ref='source/estimations-core-retenues.yaml#'+aid) for r in u['roles']])
    elif uid.startswith('maintenance/'):
        method='annual_volume';row=context['work'][aid];role_lines,valued=annual_roles(row,context);gains=valued['gain_pct']
        terms=[dict(id=c['volume_ref'],quantity=volume(context['scenario'],c['volume_ref']),unit=context['volume_labels'].get(c['volume_ref'],c['volume_ref']),unit_jh=c['jh_unitaire'],basis=c.get('travail'),counting_rule=None) for c in row['charges']]
        terms.insert(0,dict(id='fixed',quantity=1,unit='fixed',unit_jh=row['jh_fixes_avant_ia'],basis='source/chiffrage/chiffrage-java-spring.yaml#'+aid,counting_rule=None))
        source_refs+=['source/maintenance.yaml#scenario_annuel','source/chiffrage/chiffrage-java-spring.yaml#maintenance','source/unites-maintenance.yaml']
    elif uid.startswith('governance/'):
        method='capacity_period'
        office=read(ROOT/'source/modele-composable.yaml')['equipe_transformation'];r=next(r for r in office['roles'] if r['id']==aid)
        effort=next((r for r in records if r['jh'] is not None),None)
        # Integration workload is explicitly pending, even when an envelope exists.
        role_lines=price_roles([dict(id=r['id'],label=r['nom'],gross_jh=None,gain_pct=None,net_jh=effort['jh'] if effort else None,rate_eur_jh=r['tarif_eur_jh'],source_ref='source/modele-composable.yaml#equipe_transformation')])
    elif any(r['jh'] is not None for r in records):method='retained_effort'
    elif any(r['cost_eur_ht'] is not None for r in records):method='source_amount'
    declared_scope=spec.get('scope',{})
    scope=declared_scope.get('deliverable') or scope
    acceptance=deepcopy(declared_scope.get('acceptance') or acceptance)
    boundary=declared_scope.get('boundary') or boundary
    if any(v is not None for v in declared_scope.values()):source_refs.append('source/unites-travail.yaml#'+uid+'/estimation_contract/scope')
    bridge=[]
    for record in records:
        if record['cost_eur_ht'] is None:continue
        lines=[];non_labour=None;calc=None
        if method=='retained_core':
            lines=deepcopy(role_lines);non_labour=core[aid]['tooling_eur_ht'];calc=money(Decimal(str(total([r['labour_eur_ht'] for r in lines])))+Decimal(str(non_labour)))
        elif method=='annual_volume':
            row=deepcopy(context['work'][aid])
            if aid=='MAI-009':
                want_core=record['id'].endswith('/core')
                row['charges']=[c for c in row['charges'] if (c['volume_ref']=='evolutions_fonctionnelles_an.core_generique')==want_core]
                row['jh_fixes_avant_ia']=0
            lines,v=annual_roles(row,context);non_labour=money(v['net_jh']*context['tools']);calc=money(v['cost_eur_ht'])
        elif method=='capacity_period' and record['phase']=='acquisition':
            lines=deepcopy(role_lines);non_labour=0;calc=total([r['labour_eur_ht'] for r in lines])
        delta=None if calc is None else money(Decimal(str(record['cost_eur_ht']))-Decimal(str(calc)))
        require(delta is None or abs(delta)<=.02,'Reference valuation mismatch: '+record['id'])
        # A cent residual is explicit. It is never turned into extra effort.
        bridge.append(dict(id='valuation/'+record['id'],record_ref=record['id'],source_ref=record['source_ref'],status='amount_only' if calc is None else 'reconciled',
                           roles=lines,labour_eur_ht=total([r['labour_eur_ht'] for r in lines]),non_labour_eur_ht=non_labour,calculated_eur_ht=calc,
                           retained_eur_ht=record['cost_eur_ht'],rounding_eur_ht=delta))
    reference=dict(gross_jh=total([r['gross_jh'] for r in role_lines]),net_jh=total([r['net_jh'] for r in role_lines]),
                   source_jh=unit['totals']['jh'],cost_eur_ht=unit['totals']['cost_eur_ht'],roles=role_lines)
    starts=[r['start_month'] for r in records if r['start_month'] is not None];ends=[r['end_month'] for r in records if r['end_month'] is not None]
    missing=[]
    if scope is None:missing.append('deliverable')
    if not acceptance:missing.append('acceptance')
    if method in ('pending','quantity_roles'):
        if not terms or any(t['quantity'] is None for t in terms):missing.append('quantity')
        missing+=['unit_effort','gain']
        if not role_lines or any(r['rate_eur_jh'] is None for r in role_lines):missing.append('rates')
    elif method=='source_amount':missing.append('cost_detail')
    elif reference['net_jh'] is None:missing.append('effort')
    if not starts and unit['recurrence']=='initial':missing.append('period')
    require(total([b['retained_eur_ht'] for b in bridge])==unit['totals']['cost_eur_ht'],'Cost source conservation')
    return dict(id='estimate/'+uid,version=spec['version'],work_unit_ref=uid,option_ref=spec['option_ref'],phase_ref=unit['phase_ref'],
                decision_status='retained_reference' if any(r['jh'] is not None or r['cost_eur_ht'] is not None for r in records) else 'to_establish',method=method,calculation_ref=calculation_ref,
                scope=dict(deliverable=scope,acceptance=acceptance,boundary=boundary),period=dict(basis=unit['recurrence'],start_month=min(starts) if starts else None,end_month=max(ends) if ends else None),
                terms=terms,reference=reference,cost_bridge=bridge,proposal=dict(inputs=spec['proposal'],result=proposal),missing=sorted(set(missing)),
                source_refs=sorted(set(source_refs)),status='to_complete' if missing else 'linked')
