"""Read-only counter-review probes. Only the audit evidence JSON is written.

Run with the repository Python dependencies on PYTHONPATH. Mutations are confined
to deep copies; no model, UI, economic output or scenario file is changed.
"""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from validate_stacks import read
from validate_complexity_grid import validate as validate_grid
from business_calibration import validate as validate_business
from buy_qualification import validate as validate_buy, integration_paths
from study_app import Study


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def probe(fn):
    try:
        fn()
        return dict(accepted=True)
    except Exception as exc:
        return dict(accepted=False, error=type(exc).__name__, message=str(exc))


grid, snapshot, method = validate_grid()
model = validate_business()
buy = validate_buy(model)
paths, catalog = integration_paths()
nodes = {n['id']: n for n in snapshot['nodes']}
scope = read(ROOT / 'source/explications-modele.yaml')['perimetre_compare']
blocks = {b['bloc']: b for b in model['blocs']}
buy_sources = {ref for r in buy['revues'] for ref in model['couvertures'][r['couverture_ref']]['sources']}
all_sources = {**read(ROOT / 'sources/core-system-solutions-2026-10-22.yaml')['sources'], **model.get('preuves', {})}
function_ids = {f['id'] for b in grid['blocs'] for f in b['fonctions']}

def referenced_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from referenced_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from referenced_strings(v)

facts = dict(
    scope_count=len(scope),
    scope_labels=[r['fonction'] for r in scope],
    scope_row_fields=sorted(set(k for r in scope for k in r)),
    source_node_kinds=dict(Counter(n['kind'] for n in snapshot['nodes'])),
    blocks=len(grid['blocs']), functions=len(function_ids),
    make_work_rows=len(model['blocs']) + 1,
    make_assignments=sum(len(r['stacks']) for r in [*model['blocs'], model['transverse']]),
    work_templates=len(model['lots']),
    work_template_usage=dict(Counter(a['travaux_ref'] for r in [*model['blocs'],model['transverse']] for a in r['stacks'].values())),
    scenarios_exactly_copy_grid_functions=sum(b['scenario']==' ; '.join(f['resultat'] for f in g['fonctions']) for b,g in zip(model['blocs'],grid['blocs'])),
    boundaries_exactly_copy_grid=sum(b['frontiere']==g['frontiere'] for b,g in zip(model['blocs'],grid['blocs'])),
    buy_reviews=len(buy['revues']),
    buy_statuses=dict(Counter(r['statut'] for r in buy['revues'])),
    buy_decision_texts=[dict(count=n, text=t) for t, n in Counter(r['decision'] for r in buy['revues']).most_common()],
    buy_coverage_templates=dict(Counter(r['couverture_ref'] for r in buy['revues'])),
    buy_coverage_source_ids=sorted(buy_sources),
    buy_coverage_source_ids_absent_from_qualification_sources=sorted(buy_sources - buy['sources'].keys()),
    buy_coverage_source_ids_absent_from_merged_registry=sorted(buy_sources - all_sources.keys()),
    buy_exceptions=len(buy['exceptions']), buy_developments=len(buy['developpements']),
    functions_explicitly_referenced_by_calibration=sorted(function_ids & set(referenced_strings(model))),
    functions_explicitly_referenced_by_buy=sorted(function_ids & set(referenced_strings(buy))),
    integration_scenarios=len(paths['scenarios']), integration_paths=len(catalog['paths']),
    integration_activities=len({a for lot in paths['lots'] for a in lot['activites']}),
    integration_linked_capabilities=len({c for s in paths['scenarios'] for c in s['capacites']}),
    capabilities_without_integration_scenario=sorted({b['capacite_id'] for b in grid['blocs']}-{c for s in paths['scenarios'] for c in s['capacites']}),
    integration_capture_same_source_revision=(snapshot['provenance']['sha256'] == read(ROOT / paths['capture'])['provenance']['sha256']),
)
facts['replenishment_example'] = dict(
    exception=next(e for e in buy['exceptions'] if e['id']=='reassort-sap'),
    capacity_reviews=[dict(**r,name=nodes[r['capacite']]['fields']['name']) for r in buy['revues'] if r['stack']=='sap' and r['bloc'] in ('BC-034','BC-037','BC-040','BC-043','BC-044')],
    interpretation='Mapping to review; the records do not prove missing product functionality or new cost.',
)

bad_source = deepcopy(model)
bad_source['couvertures']['ms_reference']['sources'] = ['AUDIT_MISSING_SOURCE']
bad_component = deepcopy(model)
bad_component['couvertures']['ms_reference']['composants'] = ['AUDIT_MISSING_COMPONENT']
bad_identity = deepcopy(model)
bad_identity['blocs'][0]['capacite'] = 'AUDIT_MISSING_CAPABILITY'
duplicate_review = deepcopy(buy)
duplicate_review['revues'][0] = deepcopy(duplicate_review['revues'][1])

probes = dict(
    current_cartography=probe(lambda: validate_grid(check_current=True)),
    missing_buy_proof=probe(lambda: validate_business(bad_source)),
    missing_buy_component=probe(lambda: validate_business(bad_component)),
    missing_capability=probe(lambda: validate_business(bad_identity)),
    duplicate_buy_review=probe(lambda: validate_buy(model, duplicate_review)),
)

study = Study()
economic = []
for o in study.economic['options']:
    if o['stack'] not in ('java-spring', 'dotnet', 'rust'):
        continue
    features = {f['feature']: f['cout_eur_ht'] for f in o['features']}
    economic.append(dict(stack=o['stack'],
        capability_work_eur=round(sum(v for k,v in features.items() if k != 'TRANSVERSE'),2),
        transverse_work_eur=features['TRANSVERSE'],
        published_detail=o['detail_build'], build_eur=o['synthese_eur_ht']['build_core']))

current_contract = study.simulation_contract()
current_version = study.version
version_input = {p: sha(ROOT / p) for p in sorted(study.files) if (ROOT / p).suffix in ('.yaml', '.md', '.py')}
assert current_version == hashlib.sha256(json.dumps(version_input, sort_keys=True).encode()).hexdigest()
commented_config = (ROOT / 'config/application.yaml').read_bytes() + b'\n# isolated audit comment, not written\n'
version_input['config/application.yaml'] = hashlib.sha256(commented_config).hexdigest()
changed_version = hashlib.sha256(json.dumps(version_input, sort_keys=True).encode()).hexdigest()
probes['editorial_change_changes_model_version'] = dict(
    changed=current_version != changed_version,
    simulation_contract_unchanged=study.simulation_contract() == current_contract,
    old_named_scenario_rejected_by_server=not probe(lambda: study.simulate(study.parameters, version=changed_version))['accepted'],
)

inputs = [
    'source/grille-complexite.yaml','source/methode-complexite.yaml',
    'sources/cartographie-scm-2026-10-24.yaml','sources/cartographie-scenarios-2026-10-26.yaml',
    'source/recalibration-metier.yaml','source/schema-recalibration-metier.yaml',
    'source/qualification-buy.yaml','source/schema-qualification-buy.yaml',
    'source/parcours-integration.yaml','source/explications-modele.yaml',
    'source/ecarts-perimetre-flow-rfi.md','source/core-system-features.yaml',
    'tools/validate_complexity_grid.py','tools/business_calibration.py','tools/buy_qualification.py',
    'tools/calculate_costs.py','tools/study_app.py','app/src/Simulations.tsx',
    'app/src/ComplexityGrid.tsx','app/src/BusinessCalibration.tsx','app/src/IntegrationEstimates.tsx',
    'app/src/views.tsx','app/src/readerNavigation.ts','config/application.yaml',
]
output = dict(date='2026-10-27', kind='audit-only', facts=facts, probes=probes,
    make_build_composition=economic,
    baseline_horizons={o['stack']:o['horizons'] for o in study.baseline['options']},
    baseline_model_version=current_version, simulation_contract=current_contract,
    input_sha256={p:sha(ROOT/p) for p in inputs})
destination = ROOT / 'audits/2026-10-27-fond-de-carte-metier-preuves.json'
destination.write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(dict(evidence=str(destination), facts={k:facts[k] for k in (
    'blocks','functions','make_assignments','work_templates','buy_reviews','buy_statuses',
    'scenarios_exactly_copy_grid_functions','boundaries_exactly_copy_grid',
    'integration_scenarios','integration_linked_capabilities')}, probes=probes),ensure_ascii=False,indent=2))
