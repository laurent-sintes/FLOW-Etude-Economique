"""Generic work catalog and conserved contributions to adopted source measures.

Scope links never distribute a budget. Every retained source measure is consumed
once. Role effort carries its existing rate, expenses use a separate key.
"""
from copy import deepcopy
from work_estimation import build_estimate, annual_context, dependencies as estimate_dependencies, LABELS as ESTIMATE_LABELS
from decimal import Decimal, ROUND_HALF_UP
import math
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read
from capability_catalog import native

SOURCE = 'source/unites-travail.yaml'
SCHEMA = 'source/schema-unites-travail.yaml'
ABAQUE = 'source/abaque-ventilation.yaml'
ABAQUE_SCHEMA = 'source/schema-abaque-ventilation.yaml'


def dependencies():
    return {SOURCE, SCHEMA, ABAQUE, ABAQUE_SCHEMA, 'tools/work_units.py', 'source/unites-integration.yaml'} | estimate_dependencies()


def require(condition, message):
    if not condition:
        raise ValueError('ERR_WORK_UNITS: ' + message)


def known_sum(values):
    known = [Decimal(str(v)) for v in values if v is not None]
    return float(sum(known)) if known else None


def validate_abaque(document, team_ids, unit_ids):
    Draft202012Validator(read(ROOT / ABAQUE_SCHEMA)).validate(document)
    require(len({r['id'] for r in document['overrides']}) == len(document['overrides']), 'Duplicate override identity')
    keys = set()
    for row in document['overrides']:
        key = (row['work_unit_ref'], row['phase_ref'], row['measure'], row['component_ref'])
        require(key not in keys, 'Duplicate allocation override')
        keys.add(key)
        require(row['work_unit_ref'] in unit_ids, 'Unknown override unit')
        actors = [s['team_ref'] for s in row['shares']]
        require(len(actors) == len(set(actors)), 'Duplicate contributor')
        require(set(actors) <= set(team_ids) | {'governance'}, 'Unknown contributor')
        require(all(math.isfinite(s['share_pct']) for s in row['shares']), 'Invalid share')
        require(sum(Decimal(str(s['share_pct'])) for s in row['shares']) <= 100, 'Shares exceed 100 percent')
    return deepcopy(document)


def split_record(record, unit_ref, abaque, used=None, valuation=None):
    """Allocate one source record by role and expense, never by capability count."""
    result = {}
    def distribute(value, measure, component, role=None):
        if value is None:
            return
        require(type(value) in (int, float) and math.isfinite(value) and value >= 0, 'Invalid source measure')
        matches = [r for r in abaque['overrides'] if r['work_unit_ref'] == unit_ref and r['phase_ref'] == record['phase']
                   and r['measure'] == measure and r['component_ref'] in {component, '*'}]
        rule = next((r for r in matches if r['component_ref'] == component), next(iter(matches), None))
        if rule:
            if used is not None:
                used.add(rule['id'])
            shares = deepcopy(rule['shares'])
            rule_ref = rule['id']
        else:
            owner = record['team_ref']
            default = next(r for r in abaque['rules'] if r['id'] == ('governance' if owner == 'governance' else 'source-owner' if owner else 'unallocated'))
            shares = [dict(team_ref=owner, share_pct=default['share_pct'], contribution_kind='responsibility', basis=record['basis'])] if owner else []
            rule_ref = default['id']
        remainder = Decimal(100) - sum((Decimal(str(s['share_pct'])) for s in shares), Decimal(0))
        if remainder:
            shares.append(dict(team_ref=None, share_pct=float(remainder), contribution_kind='unallocated', basis=abaque['labels']['remainder']))
        amount, cumulative, previous = Decimal(str(value)), Decimal(0), Decimal(0)
        for share in shares:
            if not share['share_pct']:
                continue
            cumulative += Decimal(str(share['share_pct'])) / 100
            endpoint = amount * cumulative
            if component.startswith('expense:') or (role is not None and measure == 'cost'):
                endpoint = endpoint.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            if cumulative == 1:
                endpoint = amount
            allocated, previous = endpoint - previous, endpoint
            actor = share['team_ref']
            bucket = result.setdefault(actor, dict(team_ref=actor, jh=None, cost_eur_ht=None, roles=[], rule_refs=[], contribution_kinds=[]))
            field = 'jh' if measure == 'effort' else 'cost_eur_ht'
            bucket[field] = known_sum([bucket[field], float(allocated)])
            bucket['rule_refs'] = sorted(set(bucket['rule_refs']) | {rule_ref})
            bucket['contribution_kinds'] = sorted(set(bucket['contribution_kinds']) | {share['contribution_kind']})
            if role is not None and measure == 'effort':
                bucket['roles'].append(dict(deepcopy(role), jh=float(allocated)))
    roles = record['roles']
    if record['jh'] is not None and roles:
        require(math.isclose(sum(r['jh'] for r in roles), record['jh'], abs_tol=1e-8), 'Role effort does not reconcile')
        for role in roles:
            distribute(role['jh'], 'effort', role['id'], role)
    else:
        distribute(record['jh'], 'effort', 'work')
    valuation_roles = valuation['roles'] if valuation and valuation['status']=='reconciled' else []
    priced = roles and record['jh'] is not None and all('rate_eur_jh' in r for r in roles)
    if (priced or valuation_roles) and record['cost_eur_ht'] is not None:
        roles = roles if priced else [dict(r,jh=r['net_jh']) for r in valuation_roles]
        priced_amounts = [(Decimal(str(r['jh'])) * Decimal(str(r['rate_eur_jh']))).quantize(Decimal('.01'), rounding=ROUND_HALF_UP) for r in roles]
        labour = sum(priced_amounts)
        require(labour <= Decimal(str(record['cost_eur_ht'])), 'Role prices exceed adopted cost')
        # The effort key determines the cost of each priced role. No second price.
        cost_rules = deepcopy(abaque)
        for row in list(cost_rules['overrides']):
            if row['measure'] == 'effort':
                cost_rules['overrides'].append(dict(row, measure='cost'))
        original = abaque
        abaque = cost_rules
        for role, amount in zip(roles, priced_amounts):
            distribute(float(amount), 'cost', role['id'], role)
        abaque = original
        distribute(float(Decimal(str(record['cost_eur_ht'])) - labour), 'cost', 'expense:non-labour')
    else:
        distribute(record['cost_eur_ht'], 'cost', 'expense:total')
    # Unknown measurements still carry their source responsibility, without zero.
    if not result:
        result[record['team_ref']] = dict(team_ref=record['team_ref'], jh=None, cost_eur_ht=None, roles=[], rule_refs=['unmeasured'], contribution_kinds=['responsibility'])
    for field in ('jh', 'cost_eur_ht'):
        total = known_sum([r[field] for r in result.values()])
        expected = record[field]
        require(total is None if expected is None else total is not None and math.isclose(total, expected, abs_tol=1e-8), 'Measure not conserved: ' + field)
    return list(result.values())


def build_work_units(economic, organisation, source=None, abaque=None):
    doc = deepcopy(source if source is not None else read(ROOT / SOURCE))
    Draft202012Validator(read(ROOT / SCHEMA)).validate(doc)
    ids = {u['id'] for u in doc['units']}
    require(len(ids) == len(doc['units']), 'Duplicate work unit')
    teams = {t['id']: t for t in organisation['teams']}
    rules = validate_abaque(abaque if abaque is not None else read(ROOT / ABAQUE), teams, ids)
    records = {r['id']: r for r in organisation['reading']['records']}
    refs = [ref for u in doc['units'] for ref in u['record_refs']]
    require(len(refs) == len(set(refs)) and set(refs) == set(records), 'Source measures must be bound exactly once')
    core = {u['id']: u for o in economic['options'] if o['stack'] == 'java-spring' for u in o['core_units']}
    caps = {n['id']: n['fields']['name'] for n in native()['nodes'] if n['kind'] == 'capability'}
    integration = {u['id']: u for u in read(ROOT / 'source/unites-integration.yaml')['units']}
    def capabilities(refs):
        require(set(refs) <= core.keys(), 'Unknown capability scope unit')
        found = sorted({c['native_id'] for ref in refs for c in core[ref]['capabilities']})
        require(set(found) <= caps.keys(), 'Unknown native capability')
        return [dict(id=c, label=caps[c]) for c in found]
    activities = {r['id']: r for path in ('source/integration.yaml','source/maintenance.yaml') for r in read(ROOT / path)['activites']}
    estimate_context = annual_context()
    allocations, used = [], set()
    for unit in doc['units']:
        require(unit['parent_ref'] is None or unit['parent_ref'] in ids and unit['parent_ref'] != unit['id'], 'Invalid parent')
        bound = [records[r] for r in unit['record_refs']]
        require(all(r['phase'] == unit['phase_ref'] for r in bound), 'Work unit phase drift')
        unit['capabilities'] = capabilities(unit['core_scope_refs'])
        unit['capability_status'] = 'linked' if unit['capabilities'] else 'to_establish'
        detail = integration.get(unit['integration_unit_ref'])
        if unit['integration_unit_ref'] is not None:
            require(detail is not None, 'Unknown integration work unit')
            unit['detail'] = {k: deepcopy(detail[k]) for k in ('deliverable','acceptance','count_unit','counting_rule','quantity','quantity_basis','boundary','activity_ref')}
        else:
            unit['detail'] = None
        activity = activities.get(unit['id'].split('/')[-1])
        unit['outcome'] = activity.get('livrable') if activity else ' · '.join(core[unit['core_scope_refs'][0]].get('includes', [])) if unit['nature']=='core_build' and unit['core_scope_refs'] else None
        unit['measurements'] = deepcopy(bound)
        unit['totals'] = {field: known_sum([r[field] for r in bound]) for field in ('jh','cost_eur_ht')}
        unit['estimation'] = build_estimate(unit, core, estimate_context)
        unit_allocations = []
        for record in bound:
            for i, piece in enumerate(split_record(record, unit['id'], rules, used, next((b for b in unit['estimation']['cost_bridge'] if b['record_ref']==record['id']), None))):
                piece.update(id=record['id']+'/@'+str(i), work_unit_ref=unit['id'], record_ref=record['id'], phase=record['phase'])
                allocations.append(piece)
                unit_allocations.append(piece)
        unit['totals'] = {field: known_sum([r[field] for r in bound]) for field in ('jh','cost_eur_ht')}
        unit['unknown_measures'] = {field: sum(r[field] is None for r in bound) for field in ('jh','cost_eur_ht')}
        unit['contributions'] = []
        for actor in sorted({p['team_ref'] for p in unit_allocations}, key=lambda a:a or ''):
            rows = [p for p in unit_allocations if p['team_ref'] == actor]
            unit['contributions'].append(dict(team_ref=actor, **{f:known_sum([r[f] for r in rows]) for f in ('jh','cost_eur_ht')},
                rule_refs=sorted({r for p in rows for r in p['rule_refs']}), contribution_kinds=sorted({r for p in rows for r in p['contribution_kinds']})))
        unit['candidate_refs'] = sorted({c for r in bound for c in r['candidate_refs']} - {p['team_ref'] for p in unit_allocations})
        # Detail units inherit candidate scope, never a budget or an assignment.
        if not bound and detail:
            owner = next((r for r in organisation['work_owners'] if r['kind']=='integration_activity' and r['ref']==detail['activity_ref']), None)
            unit['candidate_refs'] = list(owner['candidate_refs']) if owner else []
    parents = {u['id']: u['parent_ref'] for u in doc['units']}
    for uid in parents:
        seen = set()
        while uid is not None:
            require(uid not in seen, 'Cyclic work decomposition')
            seen.add(uid)
            uid = parents[uid]
    require(used == {r['id'] for r in rules['overrides']}, 'Unused override or unknown component')
    for rule in rules['overrides']:
        for share in rule['shares']:
            if share['team_ref'] in teams and teams[share['team_ref']]['type']=='enabling':
                require(share['contribution_kind']=='enabling', 'Enabling contribution must be accompaniment')
    require(len(doc['team_scopes']) == len({s['team_ref'] for s in doc['team_scopes']}) and {s['team_ref'] for s in doc['team_scopes']} == teams.keys(), 'Team scope coverage')
    for scope in doc['team_scopes']:
        scope['capabilities'] = capabilities(scope['core_scope_refs'])
    order = {ref:i for i,ref in enumerate(records)}
    allocations.sort(key=lambda r:order[r['record_ref']])
    doc['capability_links'] = [dict(work_unit_ref=u['id'],capability_ref=c['id'],status='linked') for u in doc['units'] for c in u['capabilities']]
    doc['allocations'] = allocations
    doc['abaque'] = rules
    doc['estimate_labels'] = read(ROOT/ESTIMATE_LABELS)['labels']
    doc['estimation_summary'] = [dict(phase_ref=p,units=sum(u['phase_ref']==p for u in doc['units']),pending=sum(u['phase_ref']==p and bool(u['estimation']['missing']) for u in doc['units'])) for p in ('acquisition','integration','fonctionnement')]
    doc['option'] = 'java-spring'
    return doc
