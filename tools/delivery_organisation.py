"""Delivery ownership and conserved readings of existing effort and funding."""
from copy import deepcopy
from work_units import build_work_units, dependencies as work_dependencies
from team_consolidation import consolidate, dependencies as consolidation_dependencies
from decimal import Decimal
import math

from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read

SOURCE = 'source/organisation-delivery.yaml'
SCHEMA = 'source/schema-organisation-delivery.yaml'
TABLE_SCHEMA = 'source/schema-ventilation-equipes.yaml'
PHASES = ('acquisition', 'integration', 'fonctionnement')


def require(condition, message):
    if not condition:
        raise ValueError('ERR_DELIVERY_ORGANISATION: ' + message)


def dependencies():
    return {SOURCE, SCHEMA, TABLE_SCHEMA, 'tools/delivery_organisation.py'} | work_dependencies() | consolidation_dependencies()


def validate(document):
    Draft202012Validator(read(ROOT / SCHEMA)).validate(document)
    teams = {t['id']: t for t in document['teams']}
    require(len(teams) == len(document['teams']), 'Duplicate team')
    require(not {'governance', 'unallocated'} & teams.keys(), 'Reserved team identity')
    types = {t['id'] for t in document['team_types']}
    require(len(types) == len(document['team_types']), 'Duplicate team type')
    require(types == {'stream-aligned', 'platform', 'complicated-subsystem', 'enabling'}, 'Team type scope')
    modes = {m['id'] for m in document['interaction_modes']}
    require(len(modes) == len(document['interaction_modes']), 'Duplicate interaction mode')
    require(modes == {'collaboration', 'x-as-a-service', 'facilitating'}, 'Interaction mode scope')
    require(tuple(p['id'] for p in document['phases']) == PHASES, 'Phase scope')
    require(document['governance']['id'] not in teams, 'Governance is not a delivery team')
    for team in teams.values():
        require(team['type'] in types, 'Unknown team type')
        require(set(team['responsibilities']) == set(PHASES), 'Missing lifecycle responsibility')
        require(set(team['capacity']) == set(PHASES), 'Missing capacity status')
    owners = document['work_owners']
    require(len({(r['kind'], r['ref']) for r in owners}) == len(owners), 'Duplicate work ownership')
    for row in owners:
        require(row['team_ref'] is None or row['team_ref'] in teams, 'Unknown owner')
        require(len(row['candidate_refs']) == len(set(row['candidate_refs'])), 'Duplicate candidate')
        require(set(row['candidate_refs']) <= teams.keys(), 'Unknown candidate')
        require(row['team_ref'] is None or row['team_ref'] in row['candidate_refs'], 'Owner not a candidate')
        if row['team_ref'] and row['kind'] == 'core_unit':
            require(teams[row['team_ref']]['type'] != 'enabling', 'Enabling cannot own maintained software')
    require(len({r['id'] for r in document['interactions']}) == len(document['interactions']), 'Duplicate interaction')
    for relation in document['interactions']:
        require(relation['source'] in teams and relation['target'] in teams, 'Unknown interaction endpoint')
        require(relation['source'] != relation['target'], 'Self interaction')
        require(relation['mode'] in modes, 'Unknown interaction mode')
        require(bool(relation['phases']) and set(relation['phases']) <= set(PHASES), 'Unknown interaction phase')
        if relation['mode'] in {'collaboration', 'facilitating'}:
            require(bool(relation['exit_criterion']), 'Temporary interaction requires exit criterion')
    return deepcopy(document)


def partition(records, team_ids):
    """Partition each source record once. Unknown totals remain unknown."""
    require(len(team_ids) == len(set(team_ids)) and not {'governance', 'unallocated', None} & set(team_ids), 'Invalid partition teams')
    require(len({r['id'] for r in records}) == len(records), 'Duplicate source record')
    result = []
    for phase in PHASES:
        phase_rows = [r for r in records if r['phase'] == phase]
        def total(rows, field):
            values = [r[field] for r in rows if r[field] is not None]
            if not values:
                return None
            require(all(type(v) in (int, float) and math.isfinite(v) and v >= 0 for v in values), 'Invalid measure')
            return float(sum((Decimal(str(v)) for v in values), Decimal(0)))
        for row in phase_rows:
            require(row['team_ref'] in {*team_ids, None, 'governance'}, 'Unknown record owner')
        totals = {field: total(phase_rows, field) for field in ('jh', 'cost_eur_ht')}
        buckets = []
        for owner in [*team_ids, 'governance', None]:
            rows = [r for r in phase_rows if r['team_ref'] == owner]
            buckets.append(dict(team_ref=owner, jh=total(rows, 'jh'), cost_eur_ht=total(rows, 'cost_eur_ht'), record_ids=[r['id'] for r in rows]))
        for field, expected in totals.items():
            if expected is not None:
                actual = sum((Decimal(str(b[field])) for b in buckets if b[field] is not None), Decimal(0))
                require(actual == Decimal(str(expected)) if field == 'cost_eur_ht' else math.isclose(float(actual), expected, abs_tol=1e-8), 'Partition does not conserve ' + field)
        result.append(dict(id=phase, totals=totals, buckets=buckets))
    require(all(r['phase'] in PHASES for r in records), 'Unknown record phase')
    return result


def allocation_table(organisation, zone='paris'):
    """Derived business table, keyed by option, zone, phase and owner."""
    reading = organisation['reading']
    rows = []
    for phase in reading['phases']:
        for bucket in phase['buckets']:
            owner = bucket['team_ref']
            kind = 'unallocated' if owner is None else 'governance' if owner == 'governance' else 'team'
            rows.append(dict(id=phase['id']+'/'+(owner or 'unallocated'), phase_ref=phase['id'], owner_kind=kind,
                             team_ref=owner if kind == 'team' else None,
                             governance_ref=organisation['governance']['id'] if kind == 'governance' else None,
                             jh=bucket['jh'], cost_eur_ht=bucket['cost_eur_ht'],
                             period_basis='annual' if phase['id'] == 'fonctionnement' else 'phase',
                             record_ids=list(bucket['record_ids'])))
    table = dict(id='team-phase-allocation', option=reading['option'], zone=zone,
                 calculation_ref='tools/delivery_organisation.py', ownership_ref='source/abaque-ventilation.yaml',
                 rows=rows, records=deepcopy(reading['records']),
                 totals=[dict(phase_ref=p['id'], **p['totals']) for p in reading['phases']])
    Draft202012Validator(read(ROOT / TABLE_SCHEMA)).validate(table)
    require(len(rows) == len({r['id'] for r in rows}), 'Duplicate allocation cell')
    return table


def build_organisation(economic, baseline, content, source=None):
    document = validate(source if source is not None else read(ROOT / SOURCE))
    owners = {(r['kind'], r['ref']): r for r in document['work_owners']}
    units = next(o for o in economic['options'] if o['stack'] == 'java-spring')['core_units']
    option = next(o for o in baseline['options'] if o['stack'] == 'java-spring')
    end_build = option['initial_months']
    require({r['ref'] for r in document['work_owners'] if r['kind'] == 'core_unit'} == {u['id'] for u in units}, 'Core unit scope drift')
    for kind, path in [('integration_activity', 'source/integration.yaml'), ('maintenance_activity', 'source/maintenance.yaml')]:
        allowed = {r['id'] for r in read(ROOT / path)['activites']}
        require({r['ref'] for r in document['work_owners'] if r['kind'] == kind} == allowed, 'Activity scope drift')
    records = []
    def add(id, phase, label, jh=None, cost=None, team=None, source_ref='', roles=None, start=None, end=None, obj='', candidates=None, basis=''):
        if phase in document['excluded_workload_phases']:
            jh, roles = None, []
        records.append(dict(id=id, phase=phase, label=label, jh=jh, cost_eur_ht=cost, team_ref=team, source_ref=source_ref,
                            roles=roles or [], start_month=start, end_month=end, object=obj,
                            candidate_refs=candidates or [], basis=basis))
    for unit in units:
        owner = owners[('core_unit', unit['id'])]
        add('core/' + unit['id'], 'acquisition', unit['label'], unit['total_jh'], unit['cost_eur_ht'], owner['team_ref'],
            'source/estimations-core-retenues.yaml',
            [{k: r[k] for k in ('id', 'label', 'jh', 'rate_eur_jh')} for r in unit['roles']],
            start=0, end=end_build, obj='core_system', candidates=owner['candidate_refs'], basis=owner['basis'])
    gross = content['gross_evaluations']['phases']
    for phase, kind in [('integration', 'integration_activity'), ('fonctionnement', 'maintenance_activity')]:
        activity_path = 'source/integration.yaml' if phase == 'integration' else 'source/maintenance.yaml'
        activities = {r['id']: r for r in read(ROOT / activity_path)['activites']}
        role_names = read(ROOT / activity_path)['roles']
        for group in gross[phase]['options']['java-spring']['groups']:
            if group['id'] not in {'common', 'deployment', 'programme', 'annual-work'}:
                continue
            for row in group['rows']:
                owner = owners.get((kind, row['id']))
                team = 'governance' if group['id'] == 'programme' else owner['team_ref'] if owner else None
                role_shares = activities.get(row['id'], {}).get('roles_pct', {})
                roles = [dict(id=id, label=role_names[id]['nom'], jh=row['value'] * share / 100)
                         for id, share in role_shares.items() if share]
                if roles:
                    require(math.isclose(sum(r['jh'] for r in roles), row['value'], abs_tol=1e-8), 'Activity role shares')
                add('effort/' + phase + '/' + row['id'], phase, row['label'], jh=row['value'], team=team,
                    source_ref=activity_path, roles=roles,
                    obj='programme' if team == 'governance' else 'adaptations_client' if phase == 'integration' else 'annual_work',
                    candidates=owner['candidate_refs'] if owner else [], basis=owner['basis'] if owner else document['labels']['unallocated_reason'])
    office = read(ROOT / 'source/modele-composable.yaml')['equipe_transformation']
    for role in office['roles']:
        add('governance/build/' + role['id'], 'acquisition', role['nom'],
            jh=end_build * office['jours_par_an'] / 12 * role['etp'], team='governance',
            source_ref='source/modele-composable.yaml', obj='programme', start=0, end=end_build, basis=document['governance']['funding_note'])
    require(sum(Decimal(str(u['cost_eur_ht'])) for u in units) == Decimal(str(option['build'])), 'Core cost must match funded construction')
    maintenance_names = {r['id']: r['nom'] for r in read(ROOT / 'source/maintenance.yaml')['activites']}
    for row in option['funding_ledger']:
        require(0 <= row['start'] <= row['end'] <= option['service_start_month'], 'Invalid funding period')
        require(not row['start'] < end_build < row['end'], 'Funding period crosses build boundary: split the funded periods explicitly')
        if row['id'] == 'construction_core':
            continue  # Already partitioned by retained unit, including role mix and tooling.
        phase = 'acquisition' if row['end'] <= end_build else 'integration'
        team = 'governance' if row['financement_id'].startswith('transformation_') else None
        specific = owners.get(('funding', row['id']))
        shared = owners.get(('funding', row['financement_id']))
        require(not (specific and shared and specific['team_ref'] != shared['team_ref']), 'Conflicting funding attribution')
        owner = specific or shared
        if owner:
            team = owner['team_ref']
        label = document['funding_labels'].get(row['financement_id'], maintenance_names.get(row['financement_id']))
        require(label is not None, 'Missing financing label: ' + row['financement_id'])
        add('funding/' + row['id'], phase, label,
            cost=row['amount'], team=team, source_ref=row['source'], start=row['start'], end=row['end'], obj=row['objet'],
            candidates=owner['candidate_refs'] if owner else [], basis=owner['basis'] if owner else document['labels']['unallocated_reason'])
    annual = next(o for o in content['economic_evaluations']['options'] if o['stack'] == 'java-spring')['annual']
    allowed_funding = {r['id'] for r in option['funding_ledger']} | {r['financement_id'] for r in option['funding_ledger']}
    allowed_annual = {r['id'] for g in annual['breakdown'] for r in g['items']}
    require(all(r['ref'] in allowed_funding for r in document['work_owners'] if r['kind'] == 'funding'), 'Unknown funding binding')
    require(all(r['ref'] in allowed_annual for r in document['work_owners'] if r['kind'] == 'annual_cost'), 'Unknown annual cost binding')
    for group in annual['breakdown']:
        for row in group['items']:
            owner = owners.get(('annual_cost', row['id']))
            add('annual/' + row['id'], 'fonctionnement', row['nom'], cost=row['montant'],
                team=owner['team_ref'] if owner else None, source_ref=row['source'],
                obj={'socle': 'core_system', 'integration': 'adaptations_client'}.get(group['id'], 'shared_services'),
                candidates=owner['candidate_refs'] if owner else [], basis=owner['basis'] if owner else document['labels']['unallocated_reason'])
    phases = partition(records, [t['id'] for t in document['teams']])
    # Calendar periods differ from historical budget tags. Hosting the build and
    # maintaining the first releases during integration are funded in mco_run.
    expected = {'acquisition': float(sum((Decimal(str(r['amount'])) for r in option['funding_ledger'] if r['end'] <= end_build), Decimal(0))),
                'integration': float(sum((Decimal(str(r['amount'])) for r in option['funding_ledger'] if r['end'] > end_build), Decimal(0))),
                'fonctionnement': annual['total_eur_ht']}
    for phase in phases:
        require(Decimal(str(phase['totals']['cost_eur_ht'])) == Decimal(str(expected[phase['id']])), 'Funding reconciliation: ' + phase['id'])
        phase.update(next(p for p in document['phases'] if p['id'] == phase['id']))
    document['reading'] = dict(phases=phases, records=records, service_start_month=option['service_start_month'],
                               build_months=end_build, capacity_status='to_dimension', option='java-spring')
    document['work_catalog'] = build_work_units(economic, document)
    contributed = document['work_catalog']['allocations']
    allocated_phases = partition(contributed, [t['id'] for t in document['teams']])
    source_by_piece = {r['id']: r['record_ref'] for r in contributed}
    for phase in allocated_phases:
        phase.update(next(p for p in document['phases'] if p['id'] == phase['id']))
        for bucket in phase['buckets']:
            bucket['record_ids'] = list(dict.fromkeys(source_by_piece[r] for r in bucket['record_ids']))
    document['reading']['phases'] = allocated_phases
    document['allocation_table'] = allocation_table(document)
    document['team_consolidations'] = consolidate(document)
    return document
