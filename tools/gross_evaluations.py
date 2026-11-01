"""Read-only phase results. The proposal never enters valuation or simulation inputs."""
from copy import deepcopy
import hashlib
import math
from pathlib import PurePosixPath

from validate_stacks import ROOT, read
from content_model import resolve_text_tree
from model_context import CURRENT
from calculate_costs import volume

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
    paths = {SOURCE, path}
    for relative, sha in proposal['inputs_sha256'].items():
        # The proposal records its local hypotheses by basename.
        relative = str((PurePosixPath(path).parent / relative)) if '/' not in relative else relative
        _document(relative, sha)
        paths.add(relative)
    return paths


def hydrate_gross_ui(ui):
    result = deepcopy(ui)
    spec = _document(SOURCE)
    _require(spec['version'] == 1 and spec['id'] == 'gross-evaluations', 'Unknown presentation contract')
    _require(set(spec['phases']) == set(PHASES), 'Phase mismatch')
    result['essential']['gross_evaluations'] = {key:spec['labels'][key] for key in ('method', 'results')}
    return result


def validate_proposal(proposal, units, spec):
    _require(spec['proposal']['status'] == proposal['status'] == 'proposal_not_adopted', 'Proposal must remain unadopted')
    adopted = {u['id']:u for u in units}
    rows = proposal['units']
    _require(len(rows) == len(adopted) and len({r['id'] for r in rows}) == len(rows), 'Duplicate or missing unit')
    _require({r['id'] for r in rows} == set(adopted) == set(spec['unit_arbitrations']), 'Unit scope mismatch')
    for row in rows:
        _require(row['adopted_jh'] == adopted[row['id']]['total_jh'], 'Adopted decision changed: ' + row['id'])
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
    _require(len(refs)==len(set(refs)) and set(refs)=={r['structure_ref'] for r in costs['rows']}, 'Quote phase scope')
    wanted = mapping[phase]
    _require(len(wanted) == len(set(wanted)), 'Duplicate quote structure')
    return [dict(id=r['structure_ref'], title=r['title'], **deepcopy(r[slug]))
            for ref in wanted for r in costs['rows'] if r['structure_ref'] == ref]


def build_gross_evaluations(economic, data, baseline, content, glossary, version):
    """Project source JH and existing quote prices, without creating a budget."""
    spec = resolve_text_tree(_document(SOURCE), glossary, path=SOURCE)
    proof = _document(spec['proposal']['path'],spec['proposal']['sha256'])
    units = next(o for o in economic['options'] if o['stack']=='java-spring')['core_units']
    proposal_rows = validate_proposal(proof, units, spec)
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
            if phase == 'acquisition':
                if slug == 'java-spring':
                    active = {u['id']:u for u in units}
                    reading['core'] = dict(proof=deepcopy(spec['proposal']),status=proof['status'],adopted_jh=proof['adopted_jh'],proposal_jh=proof['proposal_jh'],
                        delta_jh=proof['delta_jh'],delta_pct=proof['delta_pct'],date=proof['date'],
                        rows=[dict(id=r['id'],label=active[r['id']]['label'],adopted_jh=r['adopted_jh'],
                            proposal_jh=r['proposal_jh'],delta_jh=r['delta_jh'],rationale=spec['unit_arbitrations'][r['id']],
                            references=[{key:ref[key] for key in ('id','label','jh')} for ref in active[r['id']]['alignment']['rows']]) for r in proposal_rows])
                    reading['scope'] = L['reference_note']
                    core = reading['core']
                    role_totals = {}
                    for row in core['rows']:
                        unit = active[row['id']]
                        row['label'] = row['label'].removesuffix(' Java/Spring')
                        row['detail'] = dict(date=unit['decision_date'],
                            includes=[_prose(t) for t in unit['includes']], excludes=[_prose(t) for t in unit['excludes']],
                            explanation=_prose(unit['provenance']['explanation']), proof=deepcopy(unit['provenance']),
                            roles=[dict(id=r['id'],label=r['label'],jh=r['jh']) for r in unit['roles']])
                        row['detail']['proof']['explanation'] = row['detail']['explanation']
                        for role in unit['roles']:
                            item = role_totals.setdefault(role['id'],dict(id=role['id'],label=role['label'],jh=0))
                            item['jh'] += role['jh']
                    core['roles'] = list(role_totals.values())
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
                management = [_row(role,L['programme_'+role],duration*group['pilotage']['jours_par_etp_mois']*scenario[role+'_etp'],
                                   L['jh'],L['initial']) for role in ('direction','coordination')]
                groups.append(_group('programme',L['programme_coordination'],management))
                reading['total_jh'] = sum(r['value'] for g in groups for r in g['rows'])
                reading['scope'] = L['integration_scope']
                for g in groups:
                    g['subtotal_jh'] = sum(r['value'] for r in g['rows'])
                for row in management:
                    row['note'] = L['programme_note']
                    row['context'] = _prose(group['pilotage']['justification'])
                    row['factors'] = [dict(label=L['duration'],value=duration),dict(label=L['days_month'],value=group['pilotage']['jours_par_etp_mois']),dict(label=L['people'],value=scenario[row['id']+'_etp'])]
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
    return dict(model_version=version,labels=L,phases=phases,proof=dict(path=spec['proposal']['path'],sha256=spec['proposal']['sha256']),
                pending=content['core_product_scope'].get('pending'),source=SOURCE)
