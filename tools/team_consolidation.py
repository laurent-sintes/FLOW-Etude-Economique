"""Versioned working consolidation. Retained ledgers are never rewritten."""
from copy import deepcopy
from decimal import Decimal
import math
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read
from work_estimation import money
from work_units import split_record, known_sum, validate_abaque
from project_investment import phase_expense

SOURCE = 'source/scenarios-chiffrage.yaml'
SCHEMA = 'source/schema-scenarios-chiffrage.yaml'
LABELS = 'config/consolidation-equipes.yaml'
FIELDS = ('source_jh', 'gross_jh', 'net_jh', 'cost_eur_ht', 'projected_cost_eur_ht')
PHASES = ('acquisition', 'integration', 'fonctionnement')


def dependencies():
    return {SOURCE, SCHEMA, LABELS, 'tools/team_consolidation.py'}


def require(ok, message):
    if not ok:
        raise ValueError('ERR_TEAM_CONSOLIDATION: ' + message)


def project(cost, period, recurrence, horizon):
    """Constant source prices, same cumulative rounding as retained projection."""
    start, end = period['start_month'], period['end_month']
    if cost is None or start is None or end is None or horizon['end_month'] is None:
        return None
    if recurrence == 'annual':
        return phase_expense(cost * (end-start)/12, start, end-start, horizon['start_month'], horizon['end_month'])
    return phase_expense(cost, start, end-start, horizon['start_month'], horizon['end_month'])


def _reference_rows(org, unit, rules, selection, horizon):
    rows = []
    for record in unit['measurements']:
        valuation = next((v for v in unit['estimation']['cost_bridge'] if v['record_ref'] == record['id']), None)
        pieces = split_record(record, unit['id'], rules, valuation=valuation)
        for i, piece in enumerate(pieces):
            gross, net = [], []
            valued = {r['id']: r for r in unit['estimation']['reference']['roles']}
            for role in piece['roles']:
                v = valued.get(role['id'], {})
                source_role = next(r for r in record['roles'] if r['id'] == role['id'])
                share = role['jh']/source_role['jh'] if source_role['jh'] else 1
                gross.append(None if v.get('gross_jh') is None else v['gross_jh']*share)
                net.append(None if v.get('net_jh') is None else v['net_jh']*share)
            # A monetary bridge is not a second workload record.
            source_jh = piece['jh']
            period = dict(start_month=record['start_month'], end_month=record['end_month'])
            for key in period:
                if selection['period'][key] is not None:
                    period[key] = selection['period'][key]
            if unit['recurrence'] == 'annual' and period['start_month'] is None:
                period['start_month'] = org['reading']['service_start_month']
            priced_roles = record['roles'] if record['roles'] and record['jh'] is not None and all('rate_eur_jh' in r for r in record['roles']) else [dict(r,jh=r['net_jh']) for r in valuation['roles']] if valuation and valuation['status']=='reconciled' else []
            labour = None
            fees = None
            unclassified = piece['cost_eur_ht']
            if record['cost_eur_ht'] is not None and priced_roles:
                amounts=[money(Decimal(str(r['jh']))*Decimal(str(r['rate_eur_jh']))) for r in priced_roles]
                labour=known_sum([_actor_amount(amount,rules,unit['id'],unit['phase_ref'],'effort',r['id'],record['team_ref'],piece['team_ref']) for r,amount in zip(priced_roles,amounts)])
                fees=_actor_amount(money(Decimal(str(record['cost_eur_ht']))-sum(Decimal(str(a)) for a in amounts)),rules,unit['id'],unit['phase_ref'],'cost','expense:non-labour',record['team_ref'],piece['team_ref'])
                unclassified=None
            elif selection.get('work_kind')=='expense':
                fees=piece['cost_eur_ht'];unclassified=None
            rows.append(dict(piece, labour_eur_ht=labour,non_labour_eur_ht=fees,unclassified_eur_ht=unclassified, id=piece.get('id', record['id']) + '/'+str(i), record_ref=record['id'],
                source_jh=source_jh, gross_jh=known_sum(gross) if gross and all(v is not None for v in gross) else None,
                net_jh=known_sum(net) if net and all(v is not None for v in net) else source_jh if unit['estimation']['method'] in ('retained_core','capacity_period') else None,
                component_applicability=dict(labour_eur_ht=selection.get('work_kind')!='expense',non_labour_eur_ht=True,unclassified_eur_ht=not(record['cost_eur_ht'] is not None and bool(priced_roles) or selection.get('work_kind')=='expense')),
                period=period, component_kind='source', human_applicable=source_jh is not None,
                cost_applicable=record['cost_eur_ht'] is not None or record['jh'] is None or not any(r['cost_eur_ht'] is not None for r in unit['measurements']),
                projected_cost_eur_ht=project(piece['cost_eur_ht'], period, unit['recurrence'], horizon)))
    return rows


def _shares(rules, uid, phase, measure, component, owner=None):
    matches = [r for r in rules['overrides'] if r['work_unit_ref']==uid and r['phase_ref']==phase and r['measure']==measure and r['component_ref'] in (component, '*')]
    rule = next((r for r in matches if r['component_ref']==component), next(iter(matches), None))
    if rule:
        shares, rule_ref = deepcopy(rule['shares']), rule['id']
    else:
        shares, rule_ref = ([dict(team_ref=owner, share_pct=100)] if owner else []), 'source-owner' if owner else 'unallocated'
    remaining = 100-sum(Decimal(str(s['share_pct'])) for s in shares)
    if remaining:
        shares.append(dict(team_ref=None, share_pct=float(remaining)))
    return shares, rule_ref


def _actor_amount(amount, rules, uid, phase, measure, component, owner, actor):
    shares,_ = _shares(rules,uid,phase,measure,component,owner)
    previous,cumulative=Decimal(0),Decimal(0)
    result=Decimal(0)
    for share in shares:
        cumulative+=Decimal(str(share['share_pct']))/100
        endpoint=Decimal(str(money(Decimal(str(amount))*cumulative)))
        if cumulative==1: endpoint=Decimal(str(amount))
        if share['team_ref']==actor: result+=endpoint-previous
        previous=endpoint
    return float(result)


def _proposal_rows(org, unit, rules, selection, horizon):
    result = unit['estimation']['proposal']['result']
    inputs = unit['estimation']['proposal']['inputs']
    mode = result.get('cost_mode')
    human = mode not in ('fixed_purchase', 'resource_usage', 'included')
    period = deepcopy(selection['period'])
    billing = period['billing_period'] or inputs.get('billing_period')
    period.pop('billing_period')
    # Quantities and amounts have an explicit phase/annual basis.
    compatible = billing in ('month','year') if unit['recurrence']=='annual' else billing in ('once','month','year')
    if unit['recurrence']=='annual':
        factor = 12 if billing=='month' else 1
    elif billing=='once':
        factor = 1
    elif period['start_month'] is not None and period['end_month'] is not None:
        duration=Decimal(str(period['end_month']))-Decimal(str(period['start_month']))
        factor=duration if billing=='month' else duration/12
    else:
        factor=None
    roles = result['roles']
    components = [(r['id'], 'effort', dict(source_jh=None, gross_jh=r['gross_jh'], net_jh=r['net_jh'], cost_eur_ht=r['labour_eur_ht']), True) for r in roles]
    if not roles and human:
        components.append(('work', 'effort', dict(source_jh=None,gross_jh=None,net_jh=None,cost_eur_ht=None), True))
    expenses = result.get('non_labour_eur_ht', inputs['expenses_eur_ht'])
    if mode != 'included':
        components.append(('expense:non-labour' if human else 'expense:total', 'cost', dict(source_jh=None,gross_jh=None,net_jh=None,cost_eur_ht=expenses), False))
    rows = []
    for component, measure, amounts, applicable in components:
        shares, rule = _shares(rules, unit['id'], unit['phase_ref'], measure, component)
        previous, cumulative = {k:Decimal(0) for k in amounts}, Decimal(0)
        for i, share in enumerate(shares):
            if not share['share_pct']:
                continue
            cumulative += Decimal(str(share['share_pct']))/100
            values = {}
            for key, value in amounts.items():
                if value is None or factor is None:
                    values[key] = None
                else:
                    amount = Decimal(str(value))*Decimal(str(factor))
                    if key=='cost_eur_ht':amount=Decimal(str(money(amount)))
                    endpoint = Decimal(str(money(amount*cumulative))) if key=='cost_eur_ht' else amount*cumulative
                    if cumulative==1: endpoint=amount
                    values[key] = float(endpoint-previous[key]); previous[key] = endpoint
            rows.append(dict(id='proposal/'+unit['id']+'/'+component+'/'+str(i), record_ref=None, team_ref=share['team_ref'],
                **values, labour_eur_ht=values['cost_eur_ht'] if applicable else None,non_labour_eur_ht=values['cost_eur_ht'] if not applicable else None,unclassified_eur_ht=None, jh=values['net_jh'], roles=[r for r in roles if r['id']==component], component_kind='labour' if applicable else 'expense',
                component_ref=component, rule_refs=[rule], share_pct=share['share_pct'], contribution_kinds=[share.get('contribution_kind','unallocated')], period=period, billing_period=billing, billing_compatible=compatible,
                component_applicability=dict(labour_eur_ht=applicable,non_labour_eur_ht=not applicable,unclassified_eur_ht=False),
                human_applicable=applicable, projected_cost_eur_ht=project(values['cost_eur_ht'], period, unit['recurrence'], horizon)))
    return rows


def _applicable(row, field):
    if row['component_kind']=='included':return False
    if field in ('cost_eur_ht','projected_cost_eur_ht'):return row.get('cost_applicable',True)
    if field=='source_jh':return row['estimate_source']=='reference' and row['human_applicable']
    return row['human_applicable']


def _metric_reasons(field):
    shared={'scope','estimate','kind','coverage','assignment','billing'}
    if field.endswith('jh'):return shared|{'effort'}
    return shared|{'valuation','period','horizon'} if field=='projected_cost_eur_ht' else shared|{'valuation'}


def _project_contributions(rows,horizon):
    """Prorate the source/component once, then conserve its cents across actors."""
    groups={}
    for row in rows:
        key=(row['work_unit_ref'],row.get('record_ref') or row.get('component_ref'),row['period']['start_month'],row['period']['end_month'])
        groups.setdefault(key,[]).append(row)
    for group in groups.values():
        relevant=[r for r in group if r.get('cost_applicable',True) and r['component_kind']!='included']
        if not relevant:continue
        if any(r['cost_eur_ht'] is None for r in relevant):
            for row in relevant:row['projected_cost_eur_ht']=None
            continue
        amount=sum(Decimal(str(r['cost_eur_ht'])) for r in relevant)
        first=relevant[0];target=project(float(amount),first['period'],first['recurrence'],horizon)
        cumulative,previous=Decimal(0),Decimal(0)
        for row in relevant:
            if target is None:row['projected_cost_eur_ht']=None;continue
            cumulative+=Decimal(str(row['cost_eur_ht']))
            endpoint=Decimal(str(money(Decimal(str(target))*cumulative/amount))) if amount else Decimal(0)
            if cumulative==amount:endpoint=Decimal(str(target))
            row['projected_cost_eur_ht']=float(endpoint-previous);previous=endpoint


def consolidate(org, scenario=None):
    """One row vector drives matrix and detail, preserving nullable known subtotals."""
    spec = deepcopy(read(ROOT/SOURCE) if scenario is None else scenario)
    Draft202012Validator(read(ROOT/SCHEMA)).validate(spec)
    catalog = org['work_catalog']; units = {u['id']:u for u in catalog['units']}
    selections = {s['work_unit_ref']:s for s in spec['selections']}
    require(len(selections)==len(spec['selections']) and selections.keys()==units.keys(), 'Select every work unit exactly once')
    require(spec['projection']['end_month'] is None or spec['projection']['end_month']>spec['projection']['start_month'], 'Invalid horizon')
    for value in spec['projection'].values():
        require(not isinstance(value,(int,float)) or math.isfinite(value), 'Invalid horizon number')
    teams = [t['id'] for t in org['teams']]
    excluded, replacements, grouped, pending_replacements = set(), {}, set(), set()
    for group in spec['coverage_groups']:
        a,b = set(group['replaced_refs']),set(group['replacing_refs'])
        require(a and b and not a&b and a|b <= units.keys(), 'Invalid coverage members')
        require(not (a|b)&grouped, 'Overlapping coverage groups')
        grouped |= a|b
        require(len({(units[u]['phase_ref'],units[u]['recurrence']) for u in a|b})==1, 'Coverage crosses phase or period basis')
        remaining=group['remaining_work_refs']
        require(remaining is None or set(remaining)<=b, 'Remaining work must belong to replacing scope')
        if group['confirmed'] is True:
            require(bool(group['basis']) and remaining is not None, 'Missing coverage justification or remaining scope review')
            excluded |= a
            for uid in b: replacements[uid]=group['id']
        else:
            pending_replacements |= b
    require(len({g['id'] for g in spec['coverage_groups']})==len(spec['coverage_groups']), 'Duplicate coverage identity')
    overrides = []
    for assignment in spec['assignments']:
        uid = assignment['work_unit_ref']
        require(uid in selections, 'Unknown assignment unit')
        selected = selections[uid]
        require(assignment['estimate_source']==selected['estimate_source'] and assignment['estimate_version']==selected['estimate_version'], 'Assignment version mismatch')
        require(assignment['phase_ref']==units[uid]['phase_ref'], 'Assignment phase mismatch')
        for share in assignment['shares']:
            actor=next((t for t in org['teams'] if t['id']==share['team_ref']),None)
            require(not actor or actor.get('type')!='enabling' or share['contribution_kind']=='enabling', 'Enabling contribution must be accompaniment')
        overrides.append({k:v for k,v in assignment.items() if k not in ('estimate_source','estimate_version')})
    rules = deepcopy(catalog['abaque'])
    replaced_keys = {(r['work_unit_ref'],r['phase_ref'],r['measure'],r['component_ref']) for r in overrides}
    rules['overrides'] = [r for r in rules['overrides'] if selections[r['work_unit_ref']]['estimate_source']=='reference' and (r['work_unit_ref'],r['phase_ref'],r['measure'],r['component_ref']) not in replaced_keys]+overrides
    validate_abaque(rules,teams,units)
    reference, working, pending = [],[],[]
    issues, unit_readings = {}, {}
    for uid,u in units.items():
        s = selections[uid]
        require(s['estimate_version']==u['estimation']['version'], 'Unknown estimate version')
        require(all(v is None or not isinstance(v,(int,float)) or math.isfinite(v) for v in s['period'].values()), 'Invalid period number')
        require(s['period']['end_month'] is None or s['period']['start_month'] is None or s['period']['end_month']>s['period']['start_month'], 'Invalid contribution period')
        for row in _reference_rows(org,u,catalog['abaque'],dict(s,work_kind=None,period=dict(start_month=None,end_month=None)),spec['projection']):
            reference.append(dict(row,work_unit_ref=uid,phase_ref=u['phase_ref'],estimate_source='reference',estimate_version=u['estimation']['version'],recurrence=u['recurrence'],label=u['label']))
        require(u['recurrence']==('annual' if u['phase_ref']=='fonctionnement' else 'initial'), 'Mixed initial and annual phase basis')
        if uid in excluded:
            unit_readings[uid]=dict(work_unit_ref=uid,label=u['label'],phase_ref=u['phase_ref'],recurrence=u['recurrence'],selection=deepcopy(s),status='excluded',missing=[],team_refs=[],contribution_ids=[],pending_contribution_ids=[],included_in_ref=None,**{f:None for f in FIELDS})
            continue
        source = s['estimate_source']
        require(source!='reference' or bool(u['measurements']), 'Reference without source measures')
        reason = []
        require(source!='reference' or s['accounting']=='reference', 'Reference accounting mismatch')
        if source=='proposal':
            inputs=u['estimation']['proposal']['inputs'];result=u['estimation']['proposal']['result']
            scope_keys=['deliverable','acceptance','assumptions','evidence_refs']
            if result.get('cost_mode') in ('human','resource_usage'):
                scope_keys+=['count_unit','counting_rule','quantity_basis']
            if not all(inputs.get(k) for k in scope_keys):reason.append('estimate')
            if result.get('cost_mode') in ('human','resource_usage') and inputs['quantity'] is None:reason.append('estimate')
            require(s['accounting']!='reference', 'Proposal accounting mismatch')
            mode=result.get('cost_mode')
            if not mode: reason.append('kind')
            included=mode=='included'
            expected_kind='expense' if mode in ('fixed_purchase','resource_usage','included') else 'mixed' if inputs['expenses_eur_ht'] not in (None,0) else 'human'
            require(s['work_kind'] is None or s['work_kind']==expected_kind or mode=='human' and s['work_kind'] in ('human','mixed'), 'Work kind contradicts pricing mode')
            require(not included or s['accounting'] in (None,'included'), 'Inclusion accounting mismatch')
            require(included or s['accounting']!='included', 'Inclusion accounting without inclusion')
            if included:
                ref=inputs.get('included_in_ref')
                require(ref in units and ref!=uid and ref not in excluded, 'Invalid inclusion owner')
                require((units[ref]['phase_ref'],units[ref]['recurrence'])==(u['phase_ref'],u['recurrence']), 'Inclusion crosses phase or period basis')
            accounted = included and s['accounting']=='included' or uid in replacements or s['accounting']=='additional' and bool(s['basis']) and uid not in pending_replacements
            if not accounted: reason.append('coverage')
            rows=_proposal_rows(org,u,rules,s,spec['projection'])
            for row in rows:
                if not row['billing_compatible']:
                    reason.append('billing')
                    row.update({f:None for f in (*FIELDS,'labour_eur_ht','non_labour_eur_ht','unclassified_eur_ht')})
            if included:
                rows=[dict(id='included/'+uid,record_ref=None,team_ref=None,source_jh=None,gross_jh=None,net_jh=None,cost_eur_ht=None,projected_cost_eur_ht=None,period=s['period'],human_applicable=False,cost_applicable=False,component_kind='included',rule_refs=[],included_in_ref=ref)]
            if not accounted:
                pending.extend(dict(r,work_unit_ref=uid,label=u['label'],phase_ref=u['phase_ref'],estimate_source=source,estimate_version=s['estimate_version'],recurrence=u['recurrence']) for r in rows)
                # Unconfirmed scope remains outside the working ledger.
                # Its gaps and intended actors are retained in the unit reading.
        else:
            rows=_reference_rows(org,u,rules,s,spec['projection'])
            accounted=True
            if s['work_kind'] is None and any(r['jh'] is None and r['cost_eur_ht'] is not None and not r['roles'] and not any(b['record_ref']==r['id'] and b['status']=='reconciled' for b in u['estimation']['cost_bridge']) for r in u['measurements']):
                reason.append('kind')
        for assignment in (r for r in overrides if r['work_unit_ref']==uid):
            allowed=({r['id'] for r in (u['estimation']['proposal']['result']['roles'] if source=='proposal' else u['estimation']['reference']['roles'])}|{'work','*'}) if assignment['measure']=='effort' else ({'expense:non-labour'} if source=='proposal' and mode=='human' else {'expense:total'} if source=='proposal' else {'expense:total','expense:non-labour'})
            require(assignment['component_ref'] in allowed, 'Unknown assignment component')
        if not rows: reason.append('estimate')
        if source=='reference' and (not u['estimation']['scope']['deliverable'] or not u['estimation']['scope'].get('acceptance')): reason.append('estimate')
        if source=='reference':
            require(s['work_kind']!='expense' or not any(r['jh'] is not None for r in u['measurements']), 'Expense cannot erase measured human effort')
        shared_reason=sorted(set(reason))
        for row in rows:
            local=list(shared_reason)
            if row['component_kind']!='included':
                if source=='reference' and s['work_kind'] in ('human','mixed') and u['estimation']['reference']['net_jh'] is None: local.append('effort')
                if row.get('cost_applicable',True) and row['cost_eur_ht'] is None: local.append('valuation')
                if row['human_applicable'] and row['net_jh'] is None: local.append('effort')
                if row['team_ref'] is None and (row['cost_eur_ht'] is None or row['cost_eur_ht']>0 or row['human_applicable'] and (row['net_jh'] is None or row['net_jh']>0)): local.append('assignment')
                if row['period']['start_month'] is None or row['period']['end_month'] is None: local.append('period')
            row['missing']=sorted(set(local))
            if accounted: working.append(dict(row,work_unit_ref=uid,phase_ref=u['phase_ref'],estimate_source=source,estimate_version=s['estimate_version'],recurrence=u['recurrence'],label=u['label']))
        issues[uid]=sorted({i for row in rows for i in row['missing']}|set(shared_reason))
        unit_readings[uid]=dict(work_unit_ref=uid,label=u['label'],phase_ref=u['phase_ref'],recurrence=u['recurrence'],selection=deepcopy(s),status='pending' if not accounted else 'included' if source=='proposal' and included else 'partial' if issues[uid] else 'complete',missing=issues[uid],team_refs=sorted({r['team_ref'] for r in rows if r['team_ref'] is not None}),contribution_ids=[r['id'] for r in rows] if accounted else [],pending_contribution_ids=[r['id'] for r in rows] if not accounted else [],included_in_ref=ref if source=='proposal' and included else None,**{f:known_sum([r[f] for r in rows]) if accounted else None for f in FIELDS})
    # Inclusion is a traceable exemption, never a second cost or an inclusion cycle.
    inclusions={u:units[u]['estimation']['proposal']['inputs'].get('included_in_ref') for u,s in selections.items() if s['estimate_source']=='proposal' and units[u]['estimation']['proposal']['result'].get('cost_mode')=='included' and u not in excluded}
    for uid in inclusions:
        seen=set();cursor=uid
        while cursor in inclusions:
            require(cursor not in seen,'Inclusion cycle');seen.add(cursor);cursor=inclusions[cursor]
    for uid in inclusions:
        cursor=inclusions[uid]
        inherited=[]
        while cursor in inclusions:
            inherited.extend(issues.get(cursor,[]));cursor=inclusions[cursor]
        issues[uid]=sorted(set(issues.get(uid,[])+inherited+issues.get(cursor,[])))
    for row in working:
        if row['component_kind']=='included':row['missing']=issues[row['work_unit_ref']]
    reviews={r['phase_ref']:r for r in spec['scope_reviews']}
    require(set(reviews)==set(PHASES) and len(reviews)==len(spec['scope_reviews']), 'Review all three phases')
    for uid,reading in unit_readings.items():
        if uid in inclusions:
            reading['missing']=issues[uid]
            reading['status']='partial' if issues[uid] else 'included'
    _project_contributions(reference,spec['projection'])
    _project_contributions(working,spec['projection'])
    for uid,reading in unit_readings.items():
        contributions=[r for r in working if r['work_unit_ref']==uid]
        intended=[r for r in pending if r['work_unit_ref']==uid]
        periods=[r['period'] for r in contributions or intended]
        reading['effective_period']={key:(min(p[key] for p in periods) if key=='start_month' else max(p[key] for p in periods)) if periods and all(p[key] is not None for p in periods) else None for key in ('start_month','end_month')}
        reading['rule_refs']=sorted({rule for r in contributions or intended for rule in r.get('rule_refs',[])})
        reading['projected_cost_eur_ht']=known_sum([r['projected_cost_eur_ht'] for r in contributions])
        reading['pending_cost_eur_ht']=known_sum([r['cost_eur_ht'] for r in intended])
        reading['team_contributions']=[dict(team_ref=actor,**{f:known_sum([r[f] for r in contributions if r['team_ref']==actor]) for f in FIELDS},rule_refs=sorted({rule for r in contributions if r['team_ref']==actor for rule in r.get('rule_refs',[])}),contribution_kinds=sorted({kind for r in contributions if r['team_ref']==actor for kind in r.get('contribution_kinds',[])})) for actor in sorted({r['team_ref'] for r in contributions},key=lambda a:a or '')]
    def aggregate(detail, external=(), overall=(), mode='working'):
        missing=sorted(set(overall)|{i for r in detail for i in r.get('missing',[])})
        states={}
        for field in FIELDS:
            applicable=[r for r in detail if _applicable(r,field)]
            reasons=set(external if mode=='working' else ())
            for r in applicable:
                reasons.update(i for i in r.get('missing',[]) if i in _metric_reasons(field))
                if r[field] is None:reasons.add('effort' if field.endswith('jh') else 'valuation')
                if r['team_ref'] is None and (r[field] is None or r[field]>0):reasons.add('assignment')
            if field=='projected_cost_eur_ht' and spec['projection']['end_month'] is None and applicable:reasons.add('horizon')
            state='partial' if reasons else 'complete' if applicable else 'not_applicable'
            states[field]=dict(status=state,missing=sorted(reasons))
        return dict(**{f:known_sum([r[f] for r in detail]) for f in FIELDS},metric_states=states,missing=missing,
                    status='partial' if missing else 'complete' if detail else 'not_applicable',contribution_ids=[r['id'] for r in detail])
    def matrix(rows,is_working):
        result=[]
        for phase in PHASES:
            detail=[r for r in rows if r['phase_ref']==phase]
            external=[]
            review=reviews[phase]
            if is_working:
                if not (review['complete'] is True and review['basis']):external.append('scope')
                if any('coverage' in v for uid,v in issues.items() if units[uid]['phase_ref']==phase):external.append('coverage')
            for actor in teams+['governance',None]:
                owned=[r for r in detail if r['team_ref']==actor]
                row=aggregate(owned,external,external, 'working' if is_working else 'reference')
                if is_working:
                    for field in FIELDS:
                        if any(r['team_ref'] is None and _applicable(r,field) and (r[field] is None or r[field]>0) for r in detail):
                            row['metric_states'][field]['missing']=sorted(set(row['metric_states'][field]['missing'])|{'assignment'})
                            row['metric_states'][field]['status']='partial'
                    if any('assignment' in v['missing'] for v in row['metric_states'].values()):
                        row['missing']=sorted(set(row['missing'])|{'assignment'});row['status']='partial'
                result.append(dict(row,team_ref=actor,phase_ref=phase))
        return result
    def totals(rows,is_working=False):
        result=[]
        for p in PHASES:
            external=[]
            if is_working and not(reviews[p]['complete'] is True and reviews[p]['basis']):external.append('scope')
            if is_working and any('coverage' in v for uid,v in issues.items() if units[uid]['phase_ref']==p):external.append('coverage')
            result.append(dict(phase_ref=p,**aggregate([r for r in rows if r['phase_ref']==p],external,external,'working' if is_working else 'reference')))
        return result
    phase_readings=[]
    for phase in PHASES:
        active=[r for r in unit_readings.values() if r['phase_ref']==phase and r['status']!='excluded']
        reasons=sorted({i for r in active for i in r['missing']})
        if not(reviews[phase]['complete'] is True and reviews[phase]['basis']):reasons=sorted(set(reasons)|{'scope'})
        phase_readings.append(dict(phase_ref=phase,units=len(active),complete_units=sum(not r['missing'] and r['status']!='pending' for r in active),pending_units=sum(r['status']=='pending' for r in active),excluded_units=sum(r['phase_ref']==phase and r['status']=='excluded' for r in unit_readings.values()),missing=reasons,gaps=[dict(reason=i,work_unit_refs=[r['work_unit_ref'] for r in active if i in r['missing']]) for i in reasons],status='partial' if reasons else 'complete'))
    return dict(labels=read(ROOT/LABELS)['labels'],scenario=spec,reference=dict(contributions=reference,rows=matrix(reference,False),totals=totals(reference)),
                working=dict(contributions=working,rows=matrix(working,True),totals=totals(working,True),issues=issues,pending_contributions=pending,
                             unit_readings=list(unit_readings.values()),phase_readings=phase_readings,excluded_work_units=sorted(excluded),coverage_groups=spec['coverage_groups']))
