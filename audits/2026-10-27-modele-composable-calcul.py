"""Isolated composable proposal: no imports into, or writes to, the active engine.

Run with the repository YAML dependencies on PYTHONPATH. Monetary allocations
use differences of rounded cumulative amounts; the funding parent is not a line.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from copy import deepcopy
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from validate_stacks import read

HERE = Path(__file__).resolve().parent
CFG = HERE / '2026-10-27-modele-composable.yaml'
OUT = HERE / '2026-10-27-modele-composable-preuves.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def active_hashes():
    return {p.relative_to(ROOT).as_posix(): sha(p)
            for folder in ['source', 'sources', 'config', 'tools', 'app/src']
            for p in sorted((ROOT / folder).rglob('*'))
            if p.is_file() and p.suffix in ['.yaml', '.py', '.tsx', '.ts', '.css',
                                          '.md', '.json', '.pdf', '.xlsx', '.pptx', '.docx']}


def d(x):
    return Decimal(str(x))


def cents(x):
    return int((d(x) * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def split(amount, weights):
    """Allocate integer cents, preserving the parent, including zero weights."""
    total = sum(map(d, weights))
    assert total > 0 and all(d(w) >= 0 for w in weights)
    result, cumulative, previous = [], Decimal(0), 0
    for weight in weights:
        cumulative += d(weight)
        current = int((d(amount) * cumulative / total).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
        result.append(current - previous)
        previous = current
    assert sum(result) == amount
    return result


def validate_ledger(rows, parents, acceptances):
    assert len({r['id'] for r in rows}) == len(rows), 'duplicate line'
    seen = {}
    for r in rows:
        assert set(cfg['contrat']['champs_ligne']) <= set(r)
        assert r['objet'] in cfg['contrat']['objets']
        assert r['prestation'] in cfg['contrat']['prestations']
        assert r['responsabilite'] in cfg['contrat']['responsabilites']
        assert r['debut_mois'] < r['fin_mois']
        assert r['montant_eur_ht'] >= 0 and r['source_refs']
        if r['responsabilite'] == 'mco_client':
            assert r['objet'] == 'adaptations_client', 'Core cannot be client MCO'
            assert r['debut_mois'] >= acceptances[r['reception_id']], 'MCO before acceptance'
        seen.setdefault(r['financement_id'], 0)
        seen[r['financement_id']] += cents(r['montant_eur_ht'])
    assert seen == parents, 'parent and allocations differ or duplicated financing'
    hosting = [r for r in rows if r['financement_id'] == 'hebergement_build']
    infra = [r for r in rows if r['financement_id'] == 'moyens_techniques_pendant_deploiement']
    for a in hosting:
        for b in infra:
            assert a['fin_mois'] <= b['debut_mois'], 'hosting phases overlap'


def validate_buy(originals, registry):
    assert [r['source_record'] for r in registry] == originals, 'Buy price or coverage mutated'
    by_id = {r['id']: r for r in registry}
    assert len(by_id) == len(registry)
    for r in registry:
        src = r['source_record']
        if src.get('finance_par'):
            assert src['finance_par'] in by_id
            assert not src['montants_documentes_eur_ht'], 'included price counted twice'
        assert all(v is None for v in r['parts_financieres_eur_ht'].values()), 'unsupported Buy split'


before = active_hashes()
cfg = read(CFG)
base_path = ROOT / cfg['dependances']['enveloppe']
base = json.loads(base_path.read_text(encoding='utf-8'))
for path, digest in base['source_hashes'].items():
    assert sha(ROOT / path) == digest, f'Stale input: {path}'
plan = read(ROOT / cfg['dependances']['calendrier'])
active = read(ROOT / cfg['dependances']['resultats_actifs'])
build_cost = {o['stack']: o['totaux_eur_ht']['build'] for o in active['options']}
grid = read(ROOT / cfg['dependances']['cartographie'])
bycap = {b['capacite_id']: b for b in grid['blocs']}
map_links = {kind: [bycap[c] for c in cfg['cartographie'][kind]]
             for kind in ['core', 'adaptations', 'usage_run']}
volumes = read(ROOT / 'source/maintenance.yaml')['scenario_annuel']['volumes']


def hosting(duration, profile):
    start, rows = 0, []
    assert sum(d(p['part_duree']) for p in cfg['hebergement_build']['phases']) == 1
    for phase in cfg['hebergement_build']['phases']:
        months = float(d(duration) * d(phase['part_duree']))
        components = phase['couts_mensuels_eur_ht'][profile]
        rows.append({'id': phase['id'], 'debut_mois': start, 'fin_mois': start + months,
                     'duree_mois': months, 'composants_mensuels_eur_ht': components,
                     'montant_eur_ht': cents(d(months) * sum(map(d, components.values()))) / 100})
        start += months
    assert start == duration
    return {'phases': rows, 'total_eur_ht': sum(cents(r['montant_eur_ht']) for r in rows) / 100}


def compute(slug, previous):
    build = plan['build_make_mois'][slug]
    end = build + previous['duration_months']
    first_open = min(c['go_live_month'] for c in previous['cohorts'])
    first_accept = min(c['stabilization_end'] for c in previous['cohorts'])
    acceptances = {'commun': build + first_accept}
    acceptances.update({str(c['unit']): build + c['stabilization_end'] for c in previous['cohorts']})
    rows, parents = [], {}

    def add(parent, label, amount, obj, service, responsibility, start, stop, source, reception=None):
        if stop <= start:
            assert amount == 0
            return
        row = dict(id=f'{parent}/{label}', option=slug, financement_id=parent, objet=obj,
                   prestation=service, responsabilite=responsibility, debut_mois=start,
                   fin_mois=stop, montant_eur_ht=amount / 100, source_refs=source)
        if reception is not None:
            row['reception_id'] = reception
        rows.append(row)

    evidence_ref = [cfg['dependances']['enveloppe']]
    items = previous['items_eur_ht']
    for name, value in items.items():
        if name == 'exploitation_transitoire_client':
            continue  # Replaced by funded activity children, never both.
        parents[name] = cents(value)
        obj, service, resp = 'adaptations_client', 'integration', 'integration_client'
        if name == 'maintien_core':
            obj, service, resp = 'core_system', 'maintien', 'cycle_vie_core_system'
        elif name == 'moyens_techniques_pendant_deploiement':
            obj, service, resp = 'plateforme', 'exploitation', 'run'
        elif 'coordination' in name:
            obj, service = 'programme', 'pilotage'
        add(name, 'unique', parents[name], obj, service, resp, build, end, evidence_ref)

    raw = read(ROOT / f'source/chiffrage/chiffrage-{slug}.yaml')
    raw005 = next(r for r in raw['maintenance']['activites'] if r['activite'] == 'MAI-005')
    variable_jh = sum(d(volumes[c['volume_ref']]) * d(c['jh_unitaire']) for c in raw005['charges'])
    fixed_jh = d(raw005['jh_fixes_avant_ia'])
    assert fixed_jh + variable_jh == d(previous['transient_services']['MAI-005']['annual_jh_no_gain'])
    assert sum(cents(s['cost_eur']) for s in previous['transient_services'].values()) == cents(items['exploitation_transitoire_client'])
    for aid, s in previous['transient_services'].items():
        parents[aid] = amount = cents(s['cost_eur'])
        definition = cfg['classification_make'][aid]
        refs = evidence_ref + [f'source/chiffrage/chiffrage-{slug}.yaml#maintenance/activites/{aid}']
        if aid in ['MAI-001', 'MAI-002', 'MAI-004']:
            cohorts = previous['cohorts']
            weights = [d(c['share']) * d(c['variable_service_months']) for c in cohorts]
            for c, part in zip(cohorts, split(amount, weights)):
                add(aid, str(c['unit']), part, definition['objet'], definition['prestation'],
                    definition['responsabilite'], build + c['stabilization_end'], end, refs, str(c['unit']))
        else:
            if aid == 'MAI-005':
                fixed, amount = split(amount, [fixed_jh, variable_jh])
                add(aid, 'surveillance', fixed, 'adaptations_client', 'exploitation', 'run',
                    build + first_open, end, refs)
            if aid in ['MAI-005', 'MAI-006']:
                pre, post = split(amount, [first_accept - first_open, previous['duration_months'] - first_accept])
                add(aid, 'avant_reception', pre, 'adaptations_client', 'integration', 'integration_client',
                    build + first_open, build + first_accept, refs)
                add(aid, 'apres_reception', post, 'adaptations_client', 'maintien', 'mco_client',
                    build + first_accept, end, refs, 'commun')
            else:
                add(aid, 'partage', amount, definition['objet'], definition['prestation'],
                    definition['responsabilite'], build + first_open, end, refs)
    assert sum(cents(r['montant_eur_ht']) for r in rows) == cents(previous['total_eur_ht'])
    transition = {k: sum(cents(r['montant_eur_ht']) for r in rows if r['responsabilite'] == k) / 100
                  for k in cfg['contrat']['responsabilites']}
    host = hosting(build, cfg['hebergement_build']['cas_central'])
    parents['hebergement_build'] = cents(host['total_eur_ht'])
    for phase in host['phases']:
        add('hebergement_build', phase['id'], cents(phase['montant_eur_ht']), 'plateforme', 'exploitation',
            'run', phase['debut_mois'], phase['fin_mois'], [CFG.relative_to(ROOT).as_posix() + '#hebergement_build'])
    parents['construction_core'] = cents(build_cost[slug])
    add('construction_core', 'unique', parents['construction_core'], 'core_system', 'construction',
        'cycle_vie_core_system', 0, build, [cfg['dependances']['resultats_actifs']])
    validate_ledger(rows, parents, acceptances)
    total = sum(cents(r['montant_eur_ht']) for r in rows)
    assert total == cents(previous['total_eur_ht']) + cents(host['total_eur_ht']) + cents(build_cost[slug])
    return {'ledger': rows, 'funding_parents_cents_not_additive': parents, 'acceptances': acceptances,
            'transition_by_responsibility_eur_ht': transition,
            'reclassement_initial_eur_ht': (cents(transition['integration_client']) - cents(previous['integration_migration_eur_ht'])) / 100,
            'hosting_build': host, 'transition_eur_ht': previous['total_eur_ht'],
            'transition_plus_hosting_build_eur_ht': (total - cents(build_cost[slug])) / 100,
            'construction_core_eur_ht': build_cost[slug],
            'total_through_stabilization_eur_ht': total / 100,
            'limite': 'Période bornée, euros constants ; pas un nouveau TCO. Build actif conservé, autres hypothèses issues de la proposition Groupe.'}


scenarios = {name: {slug: compute(slug, data) for slug, data in variants.items()}
             for name, variants in base['scenarios'].items()}
buy = {}
for option, spec in cfg['buy'].items():
    if not isinstance(spec, dict):
        continue
    originals = read(ROOT / spec['source'])['valorisation_annuelle']['postes']
    registry = []
    for row in originals:
        annotation = spec['groupes'].get(row['id'], {})
        registry.append({'id': row['id'], 'source_record': deepcopy(row), 'annotation': annotation,
                         'parts_financieres_eur_ht': {k: None for k in annotation.get('services', [])}})
    validate_buy(originals, registry)
    buy[option] = {'source': spec['source'], 'registre': registry,
                   'totaux_par_responsabilite_eur_ht': None,
                   'limite': 'Registre des prix sources, pas un budget Buy complet recalculé. Estimations et projections actives inchangées.'}


def must_reject(callback):
    try:
        callback()
    except AssertionError:
        return True
    raise AssertionError('Invalid case was accepted')


central = scenarios['central']['java-spring']
original = central['ledger']
parents = central['funding_parents_cents_not_additive']
acceptances = central['acceptances']
duplicate = deepcopy(original) + [deepcopy(original[0])]
assert must_reject(lambda: validate_ledger(duplicate, parents, acceptances))
double_parent = deepcopy(original) + [dict(original[0], id='second-financement')]
assert must_reject(lambda: validate_ledger(double_parent, parents, acceptances))
bad_core = deepcopy(original)
next(r for r in bad_core if r['responsabilite'] == 'mco_client')['objet'] = 'core_system'
assert must_reject(lambda: validate_ledger(bad_core, parents, acceptances))
bad_date = deepcopy(original)
next(r for r in bad_date if r['responsabilite'] == 'mco_client')['debut_mois'] = 0
assert must_reject(lambda: validate_ledger(bad_date, parents, acceptances))
overlap = deepcopy(original)
next(r for r in overlap if r['financement_id'] == 'hebergement_build')['fin_mois'] = 49
assert must_reject(lambda: validate_ledger(overlap, parents, acceptances))
bad_buy = deepcopy(buy['sap']['registre'])
next(r for r in bad_buy if r['id'] == 'MAI-010/licences')['parts_financieres_eur_ht']['run'] = 1
assert must_reject(lambda: validate_buy([r['source_record'] for r in buy['sap']['registre']], bad_buy))
bad_buy_price = deepcopy(buy['microsoft']['registre'])
next(r for r in bad_buy_price if r['id'] == 'MAI-010/licences')['source_record']['montants_documentes_eur_ht'][0]['montant'] += 1
assert must_reject(lambda: validate_buy([r['source_record'] for r in buy['microsoft']['registre']], bad_buy_price))
assert split(100, [1, 1, 1]) == [33, 34, 33]
assert split(101, [1, 0, 1]) == [51, 0, 50]
after = active_hashes()
assert before == after, 'Active model changed'
inputs = set(base['source_hashes']) | set(cfg['dependances'].values()) | {
    CFG.relative_to(ROOT).as_posix(), Path(__file__).relative_to(ROOT).as_posix(),
    'source/maintenance/maintenance-microsoft.yaml', 'source/maintenance/maintenance-sap.yaml'}
result = {'statut': cfg['statut'], 'definition': cfg, 'scenarios': scenarios, 'buy': buy,
          'hosting_sensitivities': {str(months): {profile: hosting(months, profile)
                                  for profile in ['sobre', 'central', 'soutenu']} for months in [36, 48, 60]},
          'map_links': map_links,
          'checks': {'active_files_unchanged': len(before), 'scenario_stack_cases': sum(map(len, scenarios.values())),
                     'invalid_cases_rejected': 7, 'cents_conserved': True, 'buy_source_rows_preserved': True,
                     'active_reference_unchanged': True, 'hosting_is_vendor_quote': False,
                     'contractual_inclusions_validated': False, 'full_tco_recomputed': False},
          'source_hashes': {p: sha(ROOT / p) for p in sorted(inputs)}}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'checks': result['checks'], 'central': {
    k: {key: val for key, val in v.items() if key.endswith('eur_ht')}
    for k, v in scenarios['central'].items()}}, ensure_ascii=False, indent=2))
