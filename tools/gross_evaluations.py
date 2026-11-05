"""Read-only phase results. The proposal never enters valuation or simulation inputs."""
from copy import deepcopy
import hashlib
import math
from pathlib import PurePosixPath

from validate_stacks import ROOT, read
from content_model import resolve_text_tree
from model_context import CURRENT
from calculate_costs import volume, money_round
from decimal import Decimal

SOURCE = 'source/evaluation-charges-brutes.yaml'
PHASES = ('acquisition', 'integration', 'fonctionnement')
OPTIONS = ('java-spring', 'microsoft', 'sap')


def _require(condition, message):
    if not condition:
        raise ValueError('ERR_GROSS_EVALUATIONS: ' + message)


def _document(path, expected=None):
    file = (ROOT / path).resolve()
    _require(file.is_relative_to(ROOT.resolve()) and file.is_file(), 'Missing or unsafe proof')
    value = read(file)
    if expected:
        snapshot = CURRENT.get()
        actual = snapshot.digests[file] if snapshot else hashlib.sha256(file.read_bytes()).hexdigest()
        _require(actual == expected, 'Proof fingerprint mismatch: ' + path)
    return value


def dependencies():
    source = _document(SOURCE)
    path = source['proposal']['path']
    proposal = _document(path, source['proposal']['sha256'])
    paths = {SOURCE, path, 'source/organisation-delivery.yaml'}
    for relative, sha in proposal['inputs_sha256'].items():
        # The proposal records its local hypotheses by basename.
        relative = str((PurePosixPath(path).parent / relative)) if '/' not in relative else relative
        _document(relative, sha)
        paths.add(relative)
    from integration_units import dependencies as unit_dependencies
    from domain_costs import dependencies as domain_dependencies
    from mdm_oss_estimation import dependencies as mdm_dependencies
    return paths | _revision_dependencies(source) | unit_dependencies() | domain_dependencies() | mdm_dependencies()


def _revision_dependencies(spec):
    paths = set()
    for ref in spec.get('unit_revisions',{}).values():
        proof = _document(ref['path'],ref['sha256'])
        paths.add(ref['path'])
        for relative, expected in proof['inputs_sha256'].items():
            file = (ROOT / relative).resolve()
            _require(file.is_relative_to(ROOT.resolve()) and file.is_file(), 'Unsafe revision evidence')
            snapshot = CURRENT.get()
            if snapshot:
                snapshot.read(file,lambda content:content)
            actual = snapshot.digests[file] if snapshot else hashlib.sha256(file.read_bytes()).hexdigest()
            _require(actual == expected, 'Revision evidence changed: ' + relative)
            paths.add(relative)
    return paths


def project_unit_revision(proof, unit):
    """Recount the proposed boundary and value it with current roles, never adopt it."""
    from estimation_calculation import formula, rounded
    from core_product_estimate import apportioned
    if proof.get('recipe')=='scenario_scope_revision_v1':
        return project_scenario_revision(proof,unit)
    _require(proof['status']=='proposal_not_adopted' and proof['unit_id']==unit['id'], 'Revision identity mismatch')
    _require(proof['baseline_jh']==unit['total_jh'] and proof['baseline_CFP']==unit['trace']['CFP'], 'Stale revision basis')
    basis_path = next(p for p in proof['inputs_sha256'] if p.endswith('/cosmic-controls.json'))
    basis = _document(basis_path,proof['inputs_sha256'][basis_path])
    old = {p['id']:p for p in basis['processes']}
    removed, kept = set(proof['removed_process_ids']), set(proof['kept_process_ids'])
    _require(not removed & kept and removed | kept == set(old), 'Revision double counts baseline processes')
    _require(removed == {p['id'] for p in old.values() if 'BC-008' in p['capabilities']}, 'Revision policy scope mismatch')
    _require(sum(len(old[id]['movements']) for id in kept)==proof['kept_CFP'] and sum(len(old[id]['movements']) for id in removed)==proof['replaced_policy_CFP'], 'Revision baseline count mismatch')
    _require(proof['benchmark']=={k:basis[k] for k in ('hours_per_CFP','factor','day_hours')}, 'Revision benchmark mismatch')
    processes = proof['processes']
    _require(len({p['id'] for p in processes})==len(processes) and bool(processes), 'Duplicate revision process')
    for p in processes:
        _require(p['E'] and (p['W'] or p['X']) and p['scope_reason'], 'Incomplete revision boundary')
        for key in ('E','R','W','X'):
            _require(len(p[key])==len(set(p[key])) and all(isinstance(v,str) and v for v in p[key]), 'Duplicate revision movement')
    cfp = sum(len(p[k]) for p in processes for k in ('E','R','W','X'))
    _require(proof['kept_CFP']+proof['replaced_policy_CFP']==proof['baseline_CFP'], 'Revision replacement mismatch')
    _require(cfp==proof['policy_CFP'] and proof['kept_CFP']+cfp==proof['total_CFP'], 'Revision functional total mismatch')
    raw = formula('cosmic_effort',CFP=proof['total_CFP'],**proof['benchmark'])
    days = rounded(raw,proof['rounding_jh'])
    _require(math.isclose(raw,proof['raw_jh'],abs_tol=1e-8) and days==proof['proposal_jh'], 'Revision calculation mismatch')
    roles = apportioned(days,{r['id']:r['jh'] for r in unit['roles']})
    cost = money_round(sum((Decimal(str(roles[r['id']]))*Decimal(str(r['rate_eur_jh'])) for r in unit['roles']),Decimal(0))+Decimal(str(days))*Decimal(str(unit['tooling_eur_jh'])))
    return dict(status=proof['status'],jh=days,raw_jh=raw,cost_eur_ht=cost,delta_jh=days-unit['total_jh'],delta_cost_eur_ht=money_round(Decimal(str(cost))-Decimal(str(unit['cost_eur_ht']))),policy_CFP=cfp,kept_CFP=proof['kept_CFP'],replaced_CFP=proof['replaced_policy_CFP'],total_CFP=proof['total_CFP'],hours_per_CFP=proof['benchmark']['hours_per_CFP'],day_hours=proof['benchmark']['day_hours'],assessment=proof['assessment'],processes=[dict(id=p['id'],label=p['label'],CFP=sum(len(p[k]) for k in ('E','R','W','X')),reason=p['scope_reason']) for p in processes],roles=[dict(id=r['id'],label=r['label'],jh=roles[r['id']]) for r in unit['roles']])


def project_scenario_revision(proof, unit):
    """Replace a whole old functional boundary, rather than add overlapping fragments."""
    from estimation_calculation import formula, rounded
    from core_product_estimate import apportioned
    _require(proof['status']=='proposal_not_adopted' and proof['unit_id']==unit['id'], 'Revision identity mismatch')
    _require(proof['baseline_jh']==unit['total_jh'] and proof['baseline_CFP']==unit['trace']['CFP'], 'Stale revision basis')
    _require(proof['basis_path'] in proof['inputs_sha256'], 'Missing functional basis')
    basis=_document(proof['basis_path'],proof['inputs_sha256'][proof['basis_path']])
    _require(proof['benchmark']=={k:basis[k] for k in ('hours_per_CFP','factor','day_hours')}, 'Revision benchmark mismatch')
    removed,kept=proof['removed_process_ids'],proof['kept_process_ids']
    _require(len(removed)==len(set(removed)) and not kept and set(removed)=={p['id'] for p in basis['processes']}, 'Revision double counts baseline processes')
    processes=proof['processes'];allowed={c['id'] for c in unit['capabilities']}
    _require(bool(processes) and len({p['id'] for p in processes})==len(processes),'Duplicate revision process')
    for p in processes:
        _require(p['E'] and (p['W'] or p['X']) and p['trigger'] and p['scope_reason'], 'Incomplete revision boundary')
        _require(bool(p['capabilities']) and set(p['capabilities'])<=allowed, 'Revision capability scope mismatch')
        for k in ('E','R','W','X'):
            _require(len(p[k])==len(set(p[k])) and all(isinstance(v,str) and v for v in p[k]),'Duplicate revision movement')
    cfp=sum(len(p[k]) for p in processes for k in ('E','R','W','X'))
    raw=formula('cosmic_effort',CFP=cfp,**proof['benchmark']);days=rounded(raw,proof['rounding_jh'])
    _require(cfp==proof['CFP'] and math.isclose(raw,proof['raw_jh'],abs_tol=1e-8) and days==proof['proposal_jh'],'Revision calculation mismatch')
    roles=apportioned(days,{r['id']:r['jh'] for r in unit['roles']})
    cost=money_round(sum((Decimal(str(roles[r['id']]))*Decimal(str(r['rate_eur_jh'])) for r in unit['roles']),Decimal(0))+Decimal(str(days))*Decimal(str(unit['tooling_eur_jh'])))
    return dict(kind='scenario_scope',status=proof['status'],jh=days,raw_jh=raw,cost_eur_ht=cost,
        delta_jh=days-unit['total_jh'],delta_cost_eur_ht=money_round(Decimal(str(cost))-Decimal(str(unit['cost_eur_ht']))),
        total_CFP=cfp,baseline_CFP=proof['baseline_CFP'],hours_per_CFP=proof['benchmark']['hours_per_CFP'],day_hours=proof['benchmark']['day_hours'],
        assessment=proof['assessment'],supersedes_policy_revision=proof['supersedes_policy_revision'],
        processes=[dict(id=p['id'],label=p['label'],CFP=sum(len(p[k]) for k in ('E','R','W','X')),reason=p['scope_reason']) for p in processes],
        roles=[dict(id=r['id'],label=r['label'],jh=roles[r['id']]) for r in unit['roles']])


def hydrate_gross_ui(ui):
    result = deepcopy(ui)
    spec = _document(SOURCE)
    _require(spec['version'] == 1 and spec['id'] == 'gross-evaluations', 'Unknown presentation contract')
    _require(set(spec['phases']) == set(PHASES), 'Phase mismatch')
    result['essential']['gross_evaluations'] = {key:spec['labels'][key] for key in ('method', 'results')}
    return result


def validate_proposal(proposal, units, spec):
    _require(proposal['status'] in ('proposal_not_adopted','adopted') and spec['proposal']['status'] in ('proposal_not_adopted','adopted'), 'Invalid revision status')
    adopted_revision = spec['proposal']['status'] == 'adopted'
    adopted = {u['id']:u for u in units}
    rows = proposal['units']
    _require(len(rows) == len(adopted) and len({r['id'] for r in rows}) == len(rows), 'Duplicate or missing unit')
    _require({r['id'] for r in rows} == set(adopted) == set(spec['unit_arbitrations']), 'Unit scope mismatch')
    for row in rows:
        _require(row['proposal_jh' if adopted_revision else 'adopted_jh'] == adopted[row['id']]['total_jh'], 'Adopted decision changed: ' + row['id'])
        _require(isinstance(row['proposal_jh'], (float,int)) and not isinstance(row['proposal_jh'],bool)
                 and math.isfinite(row['proposal_jh']) and row['proposal_jh'] > 0, 'Invalid proposed effort')
        _require(row['delta_jh'] == row['proposal_jh'] - row['adopted_jh'], 'Invalid unit difference')
        current_scope = {(c['id'],c.get('native_id')) for c in adopted[row['id']]['capabilities']}
        _require(current_scope == {(c['id'],c.get('native_id')) for c in row['capabilities']}, 'Capability scope changed')
    for key in ('adopted_jh','proposal_jh','delta_jh'):
        _require(math.isclose(sum(row[key] for row in rows),proposal[key],abs_tol=1e-8), 'Invalid proposal total')
    return rows


def _prose(text):
    return text.replace(' ; ', '. ').replace('; ', '. ').replace(' ;', '.')


def _row(id, label, value, unit, note):
    return dict(id=id,label=label,value=value,unit=unit,note=_prose(note))


def _group(id, title, rows, note=''):
    return dict(id=id,title=title,rows=rows,note=note)


def _quotes(costs, phase, slug, spec):
    mapping = spec['quote_phases'][slug]
    refs = [ref for p in PHASES for ref in mapping[p]]
    _require(len(refs)==len(set(refs)) and set(refs)=={r['structure_ref'] for r in costs['rows'] if r['structure_ref']!='transformation'}, 'Quote phase scope')
    wanted = mapping[phase]
    _require(len(wanted) == len(set(wanted)), 'Duplicate quote structure')
    return [dict(id=r['structure_ref'], title=r['title'], **deepcopy(r[slug]))
            for ref in wanted for r in costs['rows'] if r['structure_ref'] == ref]


def value_unit_comparisons(unit):
    """Read-only valuations at the retained unit's role mix, rates and tooling."""
    comparisons=[dict(r,method='COCOMO II') for r in unit['alignment']['rows'] if r['id']!='selected-oss']
    comparisons.append(dict(unit['alignment']['functional'],method='COSMIC × ISBSG'))
    base=Decimal(str(unit['total_jh']))
    for row in comparisons:
        if row['jh'] is None:
            row['cost_eur_ht']=None
            continue
        days=Decimal(str(row['jh']))
        labour=sum((Decimal(str(r['jh']))/base*days*Decimal(str(r['rate_eur_jh'])) for r in unit['roles']),Decimal(0))
        row['cost_eur_ht']=money_round(labour+days*Decimal(str(unit['tooling_eur_jh'])))
    return [{key:row[key] for key in ('id','label','method','jh','cost_eur_ht')} for row in comparisons]


def build_gross_evaluations(economic, data, baseline, content, glossary, version):
    """Project source JH and existing quote prices, without creating a budget."""
    spec = resolve_text_tree(_document(SOURCE), glossary, path=SOURCE)
    proof = _document(spec['proposal']['path'],spec['proposal']['sha256'])
    units = next(o for o in economic['options'] if o['stack']=='java-spring')['core_units']
    proposal_rows = validate_proposal(proof, units, spec)
    _require(set(spec['unit_analyses']) == {u['id'] for u in units}, 'Analysis scope mismatch')
    _require(len(spec['analysis_order']) == len(units) and set(spec['analysis_order']) == set(spec['unit_analyses']), 'Analysis reading order mismatch')
    for analysis in spec['unit_analyses'].values():
        _require(set(analysis) == {'finding', 'oss', 'cosmic', 'decision', 'remaining'} and all(isinstance(v,str) and v.strip() for v in analysis.values()), 'Incomplete unit analysis')
    L = spec['labels']
    options = {o['stack']:o for o in data['options']}
    current = options['java-spring']
    inputs = current['composable']['inputs']
    group = inputs['group']
    scenario = group['scenarios']['central']
    costs = content['synvance_reference']['costs']
    integration_names = {r['id']:r['nom'] for r in _document('source/integration.yaml')['activites']}
    annual_names = {r['id']:r['nom'] for r in _document('source/maintenance.yaml')['activites']}
    selection = _document('source/selection-buy.yaml')
    excluded_phases = _document('source/organisation-delivery.yaml')['excluded_workload_phases']
    phases = {}
    for phase in PHASES:
        phases[phase] = dict(intro=spec['phases'][phase]['intro'], options={})
        for slug in OPTIONS:
            groups = []
            reading = dict(groups=groups, quotes=[] if slug=='java-spring' else _quotes(costs,phase,slug,spec),
                           total_jh=None,total_unit=L['annual_jh'] if phase=='fonctionnement' else L['jh'],
                           total_label=L['annual_human_total'] if phase=='fonctionnement' else L['human_total'])
            phases[phase]['options'][slug] = reading
            reading['summary'] = spec['phases'][phase]['summaries'][slug]
            reading['scope'] = ''
            reading['workload_status'] = 'historical_pending_review' if phase in excluded_phases and slug=='java-spring' else 'current'
            reading['workload_note'] = L['historical_workload_note'] if reading['workload_status']=='historical_pending_review' else None
            if reading['workload_note']:reading['total_label'] = L['historical_human_total']
            from domain_costs import context as domain_context
            reading['domain_note'] = domain_context()['labels']['phase_pending'] if phase!='acquisition' or slug!='java-spring' else None
            if phase == 'acquisition':
                if slug == 'java-spring':
                    active = {u['id']:u for u in units}
                    reading['core'] = dict(proof=deepcopy(spec['proposal']),status=spec['proposal']['status'],adopted_jh=sum(u['total_jh'] for u in units),proposal_jh=proof['proposal_jh'],
                        delta_jh=proof['delta_jh'],delta_pct=proof['delta_pct'],date=proof['date'],
                        rows=[dict(id=r['id'],label=active[r['id']]['label'],adopted_jh=active[r['id']]['total_jh'],
                            adopted_cost_eur_ht=active[r['id']]['cost_eur_ht'],comparisons=value_unit_comparisons(active[r['id']]),
                            proposal_jh=r['proposal_jh'],delta_jh=r['delta_jh'],rationale=spec['unit_arbitrations'][r['id']],
                            references=[{key:ref[key] for key in ('id','label','jh')} for ref in active[r['id']]['alignment']['rows'] if ref['id']!='selected-oss']) for r in proposal_rows])
                    reading['scope'] = L['reference_note']
                    core = reading['core']
                    from domain_costs import core_reading
                    core['domain_reading'] = core_reading(units)
                    from mdm_oss_estimation import build_mdm_assessment
                    core['mdm_oss_assessment'] = build_mdm_assessment(units)
                    role_totals = {}
                    for row in core['rows']:
                        unit = active[row['id']]
                        row['label'] = row['label'].removesuffix(' Java/Spring')
                        scope_selection = spec['unit_scope'][unit['id']]
                        row['detail'] = dict(date=unit['decision_date'],
                            includes=[_prose(unit['includes'][i]) for i in scope_selection['includes']], excludes=[_prose(unit['excludes'][i]) for i in scope_selection['excludes']],
                            scope_note=next((_prose(a['hypothesis']) for a in unit['assumptions'] if a['id']==scope_selection.get('assumption')), ''),
                            explanation=_prose(spec['unit_arbitrations'][unit['id']]), proof=deepcopy(unit['provenance']),
                            roles=[dict(id=r['id'],label=r['label'],jh=r['jh']) for r in unit['roles']])
                        row['detail']['proof']['explanation'] = row['detail']['explanation']
                        for role in unit['roles']:
                            item = role_totals.setdefault(role['id'],dict(id=role['id'],label=role['label'],jh=0))
                            item['jh'] += role['jh']
                        if unit['trace'].get('native_scope_adoption'):
                            row['detail']['historical_comparisons'] = deepcopy(row['comparisons'])
                            row['comparisons'] = [dict(c,jh=None,cost_eur_ht=None) for c in row['comparisons']]
                        row['detail']['work_packages'] = deepcopy(unit['trace'].get('work_package_adoption',{}).get('work',[]))
                        row['detail']['method'] = unit['method']
                        row['detail']['functional_retained'] = unit['method'] == 'COSMIC × ISBSG'
                        row['detail']['analysis'] = deepcopy(spec['unit_analyses'][unit['id']])
                        a = unit['alignment']
                        row['detail']['analysis_metrics'] = dict(CFP=unit['trace']['CFP'],reference_jh=a['reference_jh'],cosmic_jh=a['functional']['jh'],gap_jh=a['functional']['gap_jh'],gap_pct=a['functional']['gap_pct'],implied_hours_per_CFP=a['implied_hours_per_CFP'])
                        if unit['id'] in spec.get('unit_revisions',{}):
                            ref = spec['unit_revisions'][unit['id']]
                            row['detail']['revision'] = project_unit_revision(_document(ref['path'],ref['sha256']),unit)
                            row['detail']['revision']['proof'] = deepcopy(ref)
                            row['detail']['revision']['core_candidate_jh'] = core['adopted_jh'] + row['detail']['revision']['delta_jh']
                    revised=[r for r in core['rows'] if r['detail'].get('revision',{}).get('kind')=='scenario_scope']
                    if revised:
                        delta=sum(r['detail']['revision']['delta_jh'] for r in revised)
                        cost_delta=sum((Decimal(str(r['detail']['revision']['delta_cost_eur_ht'])) for r in revised),Decimal(0))
                        core['revision_summary']=dict(jh=core['adopted_jh']+delta,delta_jh=delta,
                            cost_eur_ht=money_round(sum((Decimal(str(r['adopted_cost_eur_ht'])) for r in core['rows']),Decimal(0))+cost_delta),
                            delta_cost_eur_ht=money_round(cost_delta),rows=[dict(id=r['id'],label=r['label'],baseline_jh=r['adopted_jh'],jh=r['detail']['revision']['jh'],cost_eur_ht=r['detail']['revision']['cost_eur_ht']) for r in revised])
                    core['comparison_totals'] = []
                    for reference in core['rows'][0]['comparisons']:
                        values = [
                            next(item['jh'] for item in row['comparisons'] if item['id'] == reference['id'])
                            for row in core['rows']
                        ]
                        total = None if None in values else math.fsum(values)
                        core['comparison_totals'].append(dict(id=reference['id'], jh=total))
                    core['analysis_order'] = list(spec['analysis_order'])
                    core['roles'] = list(role_totals.values())
                    activity_totals = {}
                    for unit in units:
                        for activity in unit['activities']:
                            item = activity_totals.setdefault(activity['id'], dict(
                                id=activity['id'], label=activity['label'], values=[]))
                            _require(item['label'] == activity['label'], 'Conflicting activity labels')
                            item['values'].append(activity['jh'])
                    core['activities'] = [
                        dict(id=item['id'], label=item['label'], jh=math.fsum(item['values']))
                        for item in activity_totals.values()
                    ]
                    _require(math.isclose(math.fsum(a['jh'] for a in core['activities']),
                                          core['adopted_jh'], abs_tol=1e-8), 'Activity effort does not reconcile')
                    reading['construction'] = [L['core_note'],L['core_construction']]
                else:
                    rows = [_row(r['id'],_prose(r['livrable']),r['jh'],L['jh'],L['initial']) for r in selection['travaux']]
                    groups.append(_group('selection',L['selection'],rows,L['selection_note']))
                    reading['total_jh'] = sum(r['value'] for r in rows)
                    reading['scope'] = L['selection_scope']
                    reading['construction'] = [L['selection_price_note'],_prose(selection['portee']),_prose(selection['calendrier'])]
            elif phase == 'integration' and slug=='java-spring':
                rows = []
                for r in inputs['work']['integration']['activites']:
                    aid = r['activite']
                    if aid not in group['substitution']['activites_conservees']:
                        continue
                    days = scenario['interfaces']*scenario['jh_par_interface'] if aid=='INT-006' else r['jh_avant_ia']
                    if aid=='INT-007':
                        days += scenario['migration_jh_supplementaires']
                    row = _row(aid,integration_names[aid],days,L['jh'],L['interface_note'] if aid=='INT-006' else r['justification'])
                    if aid=='INT-006':
                        row['factors'] = [dict(label=L['interface_count'],value=scenario['interfaces']),dict(label=L['interface_unit'],value=scenario['jh_par_interface'])]
                    rows.append(row)
                groups.append(_group('common',L['common_work'],rows))
                deployed = [_row('deployment-'+str(i),name,days,L['jh'],L['initial'])
                            for i,(name,days) in enumerate(zip(group['perimetre']['poles_candidats'],scenario['deploiement_jh_par_unite']))]
                for row in deployed:
                    row['note'] = _prose(group['deploiement']['contenu'])
                    row['exclusions'] = _prose(group['deploiement']['exclusions'])
                    row['context'] = _prose(group['deploiement']['limite'])
                groups.append(_group('deployment',L['deployment'],deployed))
                duration = baseline['make_integration_months']
                team=inputs['config']['equipe_transformation']
                management=[_row(role['id'],role['nom'],duration*team['jours_par_an']/12*role['etp'],L['jh'],L['programme_note']) for role in team['roles']]
                groups.append(_group('programme',team['nom'],management))
                reading['total_jh'] = sum(r['value'] for g in groups for r in g['rows'])
                reading['scope'] = L['integration_scope']
                for g in groups:
                    g['subtotal_jh'] = sum(r['value'] for r in g['rows'])
                funded = next(o for o in baseline['options'] if o['stack']==slug)['funding_ledger']
                provisions = [_row(r['id'],L['common_work'] if r['id']=='coordination_commune' else L['deployment'],r['amount'],
                                   L['euro'],L['coordination_note']) for r in funded if r['id'] in ('coordination_commune','coordination_deploiements')]
                groups.append(_group('coordination',L['coordination'],provisions,L['coordination_note']))
                reading['construction'] = [L['integration_note'],_prose(group['perimetre']['migration']),_prose(scenario['nature'])]
            elif phase=='integration':
                reading['construction'] = [L['quote_note'],next(r for r in costs['rows'] if r['structure_ref']=='integration')['comparison']]
            elif phase=='fonctionnement':
                if slug=='java-spring':
                    rows=[]
                    for r in inputs['work']['maintenance']['activites']:
                        if r['traitement']!='estimation':
                            continue
                        days = r['jh_fixes_avant_ia']+sum(volume(inputs['volumes'],c['volume_ref'])*c['jh_unitaire'] for c in r['charges'])
                        row = _row(r['activite'],annual_names[r['activite']],days,L['annual_jh'],L['annual_reference'])
                        row['terms'] = [dict(label=L['volume_labels'][c['volume_ref']],quantity=volume(inputs['volumes'],c['volume_ref']),unit_jh=c['jh_unitaire'],note=_prose(c.get('travail',''))) for c in r['charges']]
                        row['fixed_jh'] = r['jh_fixes_avant_ia']
                        rows.append(row)
                    groups.append(_group('annual-work',L['annual_human_total'],rows,L['annual_note']))
                    reading['total_jh'] = sum(r['value'] for r in rows)
                    reading['scope'] = L['annual_scope']
                    annual = next(o for o in content['economic_evaluations']['options'] if o['stack']==slug)['annual']
                    pilotage = [r for g in annual['breakdown'] for r in g['items'] if r['id']=='pilotage']
                    _require(len(pilotage)==1, 'Missing annual coordination owner')
                    groups.append(_group('annual-coordination',L['annual_coordination'],[_row('annual-pilotage',L['annual_pilotage'],pilotage[0]['montant'],L['annual_euro'],L['annual_coordination_note'])],L['annual_coordination_note']))
                    reading['construction'] = []
                else:
                    reading['construction'] = [costs['source_horizon']['introduction'],costs['source_horizon']['provider_notes'][slug],costs['source_horizon']['note']]
                base=options[slug]['base_annuelle']
                rows = [_row(key,L[key],base[key],L['annual_euro'],L['annual_reference'])
                        for key in ('hebergement','ipaas','licences_complementaires')]
                rows.append(_row('outillage',L['outillage'],inputs['calibration']['couts_communs']['outillage_support_annuel'],L['annual_euro'],L['services_note']))
                groups.append(_group('services',L['services'],rows,L['services_note']))
    review = content['market']['comparison']['budget_review']
    for phase in PHASES:
        for slug in OPTIONS:
            reading=phases[phase]['options'][slug]
            phase_ref=dict(acquisition='obtain_core',integration='integrate_deploy',fonctionnement='operate_evolve')[phase]
            reading['remaining']=[dict(id=a['id'],label=a['title'],scope=_prose(a['residual_scope']),proof_to_price=_prose(a['proof_to_price']),value=a['net_extra_jh']) for a in review['additions'] if a['stack']==slug and a['phase_ref']==phase_ref]
    core=phases['acquisition']['options']['java-spring']['core']
    core['programme_roles']=deepcopy(next(g['rows'] for g in phases['integration']['options']['java-spring']['groups'] if g['id']=='programme'))
    core['transformation_items']=deepcopy(spec['transformation_items'])
    core['professional_functions']=[dict(id=f['id'],label=f['label'],owners=sorted({m['owner'] for m in f['existing_funding']})) for f in content['core_product_scope']['functions']]
    core['gap_reviews']=[dict(id=r['gap_ref'],title=r['title'],status=spec['gap_labels'][r['gap_ref']],funded=_prose(r['already_funded']),residual=_prose(r['residual']),owners=deepcopy(r['funding_owners']),sources=deepcopy(r['sources'])) for r in review['reviews']]
    core['priority_gaps']=[g for g in core['gap_reviews'] if g['id'] in spec['priority_gap_refs']]
    from integration_units import compile_units, attach_active_work
    return dict(integration_units=attach_active_work(compile_units(),phases['integration']['options']['java-spring']['groups']),model_version=version,labels=L,phases=phases,proof=dict(path=spec['proposal']['path'],sha256=spec['proposal']['sha256']),
                pending=content['core_product_scope'].get('pending'),source=SOURCE)
