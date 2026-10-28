"""Qualify skill output and prepare a reviewable candidate; never change active costs."""
from copy import deepcopy
from decimal import Decimal
import hashlib
import json
import math
from jsonschema import Draft202012Validator, FormatChecker
from model_context import model_memo, CURRENT
from validate_stacks import ROOT, read
from evaluation_status import load_status

SOURCE = 'source/evaluation-core.yaml'
SCHEMA = 'source/schema-evaluation-core.yaml'
KINDS = ('developpeur', 'qa_independante', 'architecture_transverse', 'pilotage', 'autre')
BOUNDS = ('bas', 'central', 'haut')
MARKET_SOURCE = 'source/instruction-marche.yaml'
MARKET_PREFIX = MARKET_SOURCE + '#qualifications/'


class QualificationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise QualificationError(message)


def index(rows, name):
    result = {row['id']: row for row in rows}
    require(len(result) == len(rows), 'Duplicate ' + name)
    return result


def references(values, allowed, name):
    require(set(values) <= set(allowed), 'Unknown ' + name + ': ' + str(set(values) - set(allowed)))


def acyclic(graph, name):
    done = set()
    def visit(node, trail):
        require(node not in trail, 'Cyclic ' + name + ': ' + node)
        if node in done:
            return
        for target in graph.get(node, []):
            visit(target, trail | {node})
        done.add(node)
    for node in graph:
        visit(node, set())


def market_qualifications(d, market=None):
    """Resolve the market's records without becoming a second owner of its facts."""
    refs = {ref for fn in d['functions'] for ref in fn.get('market_qualification_refs', [])}
    if not refs:
        return {}
    from market_instruction import build_market_instruction
    market = read(ROOT / 'source/references-couts-integration.yaml') if market is None else market
    built = build_market_instruction(market, instruction=read(ROOT / MARKET_SOURCE), core_functions=d['functions'])
    records = {MARKET_PREFIX + row['id']: row for row in built['qualifications']}
    references(refs, records, 'market qualification')
    declared_documents = set(read(ROOT / 'config/publication.yaml')['documents'])
    resolved = {}
    for ref in sorted(refs):
        record = records[ref]
        proofs = []
        for proof in record['evidence_refs']:
            source_ref = proof['source_ref']
            if source_ref.startswith(('http://', 'https://')):
                # The recorded URL is frozen; its remote content was not fetched.
                proofs.append(dict(source_ref=source_ref, sha256=None))
                continue
            path_ref = source_ref.split('#')[0]
            require(path_ref in declared_documents, 'Market evidence must be declared for snapshot: ' + path_ref)
            path = (ROOT / path_ref).resolve()
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            session = CURRENT.get()
            if session is not None:
                require(path not in session.digests or session.digests[path] == digest,
                        'Market evidence changed during loading: ' + path_ref)
                session.digests[path] = digest
            proofs.append(dict(source_ref=source_ref, sha256=digest))
        payload = dict(qualification=deepcopy(record), evidence_digests=proofs)
        payload['sha256'] = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        resolved[ref] = payload
    return resolved


@model_memo
def validate(doc=None):
    d = deepcopy(doc) if doc is not None else read(ROOT / SOURCE)
    Draft202012Validator(read(ROOT / SCHEMA), format_checker=FormatChecker()).validate(d)
    load_status(d['status_ref'])
    grid = read(ROOT / 'source/grille-complexite.yaml')['blocs']
    capabilities = {row['capacite_id']: row for row in grid}
    need_owners = {f['id']: row['capacite_id'] for row in grid for f in row['fonctions']}
    scope = d['scope']
    references(scope['capability_refs'], capabilities, 'capability')
    evidence = d['evidence']
    declared_documents = set(read(ROOT / 'config/publication.yaml')['documents'])
    for key, proof in evidence.items():
        ref = proof['reference']
        if not ref.startswith('https://'):
            document_ref = ref.split('#')[0]
            path = (ROOT / document_ref).resolve()
            require(path.is_relative_to(ROOT.resolve()) and path.is_file(), 'Invalid evidence path: ' + key)
            require(document_ref in declared_documents, 'Evidence must be declared for snapshot: ' + key)
    functions = index(d['functions'], 'function')
    market = read(ROOT / 'source/references-couts-integration.yaml')
    products = market['reperes_build_core']['fiches_produit']
    linked_market = market_qualifications(d, market)
    for fn in functions.values():
        references(fn['capability_refs'], scope['capability_refs'], 'function capability')
        references(fn['need_refs'], need_owners, 'native function')
        require({need_owners[r] for r in fn['need_refs']} <= set(fn['capability_refs']), 'Function need outside capability')
        market_records = [linked_market[ref]['qualification'] for ref in fn.get('market_qualification_refs', [])]
        for record in market_records:
            require(record['capability_ref'] in fn['capability_refs'] and set(record['need_refs']) <= set(fn['need_refs']),
                    'Market qualification does not match Core capability and needs')
            require(record['evaluation_function_ref'] in (None, fn['id']), 'Market qualification points to another Core function')
        if fn['status'] == 'non_etudie':
            require(not fn['observations'] and not market_records, 'Unstudied function has observations')
        if fn['status'] == 'qualifie':
            local_qualified = fn['observations'] and all(o['classification'] != 'inconnu' for o in fn['observations'])
            market_qualified = market_records and all(row['status'] == 'qualifie' for row in market_records)
            if market_records:
                require(market_qualified, 'Qualified Core function references unqualified market records')
            covered_needs = {need for row in market_records if row['status'] == 'qualifie' for need in row['need_refs']}
            require(local_qualified or (market_qualified and covered_needs == set(fn['need_refs'])),
                    'Qualified function needs qualified observations covering its needs')
        for observation in fn['observations']:
            require(observation['product_ref'] in products, 'Unknown observed product')
            references(observation['evidence_refs'], evidence, 'observation evidence')
            if observation['classification'] != 'inconnu':
                require(observation['evidence_refs'] and observation['differences'], 'Observation requires evidence and differences')
    require(set().union(*(set(fn['capability_refs']) for fn in functions.values())) == set(scope['capability_refs']),
            'Every scoped capability needs an explicit qualification status')
    components = index(d['components'], 'component')
    for component in components.values():
        require(component['ecosystem'] in scope['ecosystems'], 'Component outside ecosystem scope')
        known = read(ROOT / f"source/stacks/{component['ecosystem']}.yaml")['elements']
        require(component['component_ref'] in {c['id'] for c in known}, 'Unknown stack component')
        references(component['evidence_refs'], evidence, 'component evidence')
        if component['status'] == 'retenu':
            require(component['evidence_refs'] and all(component[k] for k in ('licence', 'version', 'interfaces', 'compatibility', 'limits')),
                    'Retained component lacks reuse checks')
    lots = index(d['lots'], 'lot')
    mechanisms = index(d['mechanisms'], 'shared mechanism')
    for mechanism in mechanisms.values():
        owner = mechanism['owner_lot_ref']
        consumers = mechanism['consumer_lot_refs']
        require(owner in lots and owner not in consumers, 'Shared mechanism owner')
        references(consumers, lots, 'mechanism consumer')
        require(all(owner in lots[c]['dependency_refs'] for c in consumers), 'Consumer must depend on funding owner')
        require(all(any(mechanism['id'] in e['mechanism_refs'] for e in rows)
                    for rows in lots[owner]['estimates'].values()), 'Shared mechanism lacks an explicit owner effort')
    legacy = {r['capacite']: r for r in read(ROOT / 'source/recalibration-metier.yaml')['blocs']}
    used_legacy = set()
    efforts = {}
    for lot in lots.values():
        references(lot['capability_refs'], scope['capability_refs'], 'lot capability')
        references(lot['function_refs'], functions, 'lot function')
        for fn in lot['function_refs']:
            require(set(functions[fn]['capability_refs']) & set(lot['capability_refs']), 'Lot does not serve its function')
        references(lot['dependency_refs'], lots, 'lot dependency')
        references(lot['component_refs'], components, 'lot component')
        require(set(lot['estimates']) == set(scope['ecosystems']), 'Incomplete ecosystem coverage')
        if lot['legacy_ref']:
            cap = lot['legacy_ref']['capability_ref']
            require(cap in lot['capability_refs'] and cap in legacy, 'Unknown historical assignment')
            require(cap not in used_legacy, 'Duplicate historical funding assignment')
            used_legacy.add(cap)
        for ecosystem, rows in lot['estimates'].items():
            index(rows, 'effort within ' + lot['id'] + '/' + ecosystem)
            for effort in rows:
                key = (ecosystem, lot['id'], effort['id'])
                efforts[key] = effort
                references(effort['mechanism_refs'], mechanisms, 'effort mechanism')
                for mechanism_ref in effort['mechanism_refs']:
                    mechanism = mechanisms[mechanism_ref]
                    if lot['id'] != mechanism['owner_lot_ref']:
                        require(lot['id'] in mechanism['consumer_lot_refs'] and effort['status'] == 'inclus'
                                and effort['included_in'] and effort['included_in']['lot_ref'] == mechanism['owner_lot_ref'],
                                'Shared work must be funded once by its owner')
                require((effort['status'] == 'estime') == (effort['jh'] is not None), 'Unknown/included/not applicable effort is not numeric zero')
                require((effort['status'] == 'inclus') == (effort['included_in'] is not None), 'Included effort requires its funding reference')
                if effort['status'] in ('inclus', 'sans_objet'):
                    require(effort['explanation'], 'Inclusion or exclusion requires a reason')
                if effort['status'] == 'inconnu':
                    require(effort['decision'] != 'retenu', 'Unknown effort cannot be retained')
                provenance = effort['provenance']
                references(provenance['evidence_refs'], evidence, 'effort evidence')
                review = effort['review']
                references(review['evidence_refs'], evidence, 'review evidence')
                if review['status'] == 'non_realisee':
                    require(review['reviewer'] is None and review['date'] is None and not review['evidence_refs'], 'Unperformed human review must remain unknown')
                else:
                    require(review['reviewer'] and review['date'] and review['evidence_refs'], 'Human review must be traceable')
                if effort['jh'] is not None:
                    values = [effort['jh'][b] for b in BOUNDS]
                    require(all(math.isfinite(v) for v in values) and values == sorted(values), 'Invalid effort range')
                    require(provenance['origin'] != 'inconnue' and provenance['rationale'] and effort['uncertainty'], 'Estimate needs provenance and uncertainty')
                    if not any(values):
                        require(effort['explanation'], 'Zero estimate requires a reason')
                    if provenance['origin'] in ('mesuree', 'transposee'):
                        require(any(evidence[r]['kind'] == 'mesure_effort' for r in provenance['evidence_refs']), 'Observed/transposed effort needs a measured effort source')
                    if effort['decision'] == 'retenu':
                        require(provenance['date'] and provenance['assisted_by_ai'] is not None
                                and all(effort['conditions'].values()), 'Retained effort needs date and realization conditions')
    acyclic({lot['id']: lot['dependency_refs'] for lot in lots.values()}, 'lot dependencies')
    included_graph = {}
    for (ecosystem, lot_id, effort_id), effort in efforts.items():
        ref = effort['included_in']
        if ref:
            target = (ecosystem, ref['lot_ref'], ref['effort_ref'])
            require(target in efforts, 'Unknown funding effort')
            require(efforts[target]['kind'] == effort['kind'], 'Inclusion cannot change effort kind')
            included_graph['/'.join((ecosystem, lot_id, effort_id))] = ['/'.join(target)]
    acyclic(included_graph, 'effort inclusions')
    return d


def summarize(doc=None):
    """Report qualification gaps without pretending that an unknown effort is zero."""
    d = validate(doc)
    result = dict(source=SOURCE, status=load_status(d['status_ref']), purpose=d['purpose'],
                  capabilities=len(d['scope']['capability_refs']), functions=len(d['functions']), lots=len(d['lots']),
                  ecosystems={}, historical_reference=[],
                  unassigned_functions=sorted(set(fn['id'] for fn in d['functions']) -
                                              {ref for lot in d['lots'] for ref in lot['function_refs']}))
    for ecosystem in d['scope']['ecosystems']:
        rows = [(lot['id'] + '/' + e['id'], e) for lot in d['lots'] for e in lot['estimates'][ecosystem]]
        result['ecosystems'][ecosystem] = dict(
            retained=sum(e['decision'] == 'retenu' for _, e in rows),
            unknown=[ref for ref, e in rows if e['status'] == 'inconnu'],
            not_retained=[ref for ref, e in rows if e['decision'] != 'retenu'],
            complete=not result['unassigned_functions'] and all(fn['status'] == 'qualifie' for fn in d['functions'])
                     and all(e['decision'] == 'retenu' and e['status'] != 'inconnu' for _, e in rows))
    calibration = read(ROOT / 'source/recalibration-metier.yaml')
    assignments = {r['capacite']: r for r in calibration['blocs']}
    for lot in d['lots']:
        if not lot['legacy_ref']:
            continue
        row = assignments[lot['legacy_ref']['capability_ref']]
        result['historical_reference'].append(dict(lot_ref=lot['id'], funding_ref=row['bloc'],
            source=lot['legacy_ref']['source'], nature='hypothese_historique_non_recalibree',
            by_ecosystem={eco: dict(lot_ref=row['stacks'][eco]['travaux_ref'],
                natures=calibration['methode']['natures'],
                ranges={b: calibration['lots'][row['stacks'][eco]['travaux_ref']][b] for b in BOUNDS})
                for eco in d['scope']['ecosystems']}))
    return result


def candidate(doc=None, lot_refs=None):
    """Return retained, calculable work for review, with dependency closure and no write.

    Developer JH and other effort kinds remain separate. This output is deliberately
    not applied to the legacy six-nature calibration or the active cost engine.
    """
    d = validate(doc)
    require(d['purpose'] != 'pilote_historique', 'Historical qualification is not a new evaluation candidate')
    lots = {lot['id']: lot for lot in d['lots']}
    selected = set(lot_refs) if lot_refs is not None else set(lots)
    require(bool(selected), 'Empty candidate scope')
    references(selected, lots, 'candidate lot')
    pending = list(selected)
    while pending:
        lot = lots[pending.pop()]
        dependencies = set(lot['dependency_refs'])
        dependencies |= {e['included_in']['lot_ref'] for rows in lot['estimates'].values() for e in rows if e['included_in']}
        for dependency in dependencies - selected:
            selected.add(dependency)
            pending.append(dependency)
    output = dict(kind='candidat_pour_relecture', applied=False, source=SOURCE,
                  qualification_sha256=hashlib.sha256(json.dumps(d, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
                  lot_refs=sorted(selected), scope_exclusions=d['scope']['exclusions'], ecosystems={})
    selected_functions = {ref for lot_id in selected for ref in lots[lot_id]['function_refs']}
    require(all(fn['status'] == 'qualifie' for fn in d['functions'] if fn['id'] in selected_functions),
            'Candidate contains unqualified functions')
    if lot_refs is None:
        require(selected_functions == {fn['id'] for fn in d['functions']}, 'Candidate has unfunded functions')
    selected_refs = {ref for fn in d['functions'] if fn['id'] in selected_functions
                     for ref in fn.get('market_qualification_refs', [])}
    output['functions'] = [deepcopy(fn) for fn in d['functions'] if fn['id'] in selected_functions]
    output['market_qualifications'] = {ref: value for ref, value in market_qualifications(d).items() if ref in selected_refs}
    output['inputs_sha256'] = hashlib.sha256(json.dumps(dict(core=output['qualification_sha256'],
        market=output['market_qualifications']), sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    for ecosystem in d['scope']['ecosystems']:
        rows = []
        present_kinds = {e['kind'] for lot_id in selected for e in lots[lot_id]['estimates'][ecosystem]}
        totals = {kind: {bound: Decimal(0) for bound in BOUNDS} for kind in KINDS if kind in present_kinds}
        for lot_id in sorted(selected):
            lot = lots[lot_id]
            require(all(c['status'] == 'retenu' for c in d['components'] if c['id'] in lot['component_refs'] and c['ecosystem'] == ecosystem),
                    'Candidate contains unqualified reuse')
            for effort in lot['estimates'][ecosystem]:
                require(effort['decision'] == 'retenu' and effort['status'] != 'inconnu',
                        'Candidate contains unretained or unknown effort: ' + ecosystem + '/' + lot_id + '/' + effort['id'])
                if effort['status'] == 'estime':
                    for bound in BOUNDS:
                        totals[effort['kind']][bound] += Decimal(str(effort['jh'][bound]))
                elif effort['status'] == 'inclus':
                    ref = effort['included_in']
                    target = next(e for e in lots[ref['lot_ref']]['estimates'][ecosystem] if e['id'] == ref['effort_ref'])
                    require(target['status'] in ('estime', 'inclus') and target['decision'] == 'retenu', 'Included work lacks retained funding')
                rows.append(dict(lot_ref=lot_id, capability_refs=lot['capability_refs'], function_refs=lot['function_refs'], **deepcopy(effort)))
        output['ecosystems'][ecosystem] = dict(efforts=rows,
            unrepresented_effort_kinds=[kind for kind in KINDS if kind not in present_kinds],
            totals_jh={kind: {b: float(v) for b, v in bounds.items()} for kind, bounds in totals.items()})
    return output


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', action='store_true', help='Print a retained review candidate, never apply it')
    args = parser.parse_args()
    print(json.dumps(candidate() if args.candidate else summarize(), ensure_ascii=False, indent=2))
