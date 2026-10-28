"""Canonical architecture taxonomy and qualitative cost coverage, without valuation."""
from copy import deepcopy

from jsonschema import Draft202012Validator

from content_model import resolve_text_tree, validate_glossary_literals
from validate_stacks import ROOT, read

SOURCE = 'source/architecture.yaml'
SCHEMA = 'source/schema-architecture.yaml'

# Stable domain identities consumed by the ledger. Labels, coverage and the client
# allocation remain editable; these associations express their economic meaning.
COST_SEMANTICS = {
    'obtention': ('obtention_initiale_core_system', {'obtention'}, {'build'}),
    'integration': ('integration_deploiement_initiaux', {'integration'}, {'build'}),
    'core_care': ('maintenance_core', {'core_care'}, {'build'}),
    'client_care': ('mco_plateforme_beaumanoir', {'client_care'}, {'build', 'run'}),
    'run_cloud': ('socle_technique_cloud', {'run_cloud', 'technical_purchases'}, {'run'}),
    'grouped_buy': ('grouped_buy', {'grouped_buy'}, {'build', 'run'}),
    'operations_support': ('operations_support', {'operations_support'}, {'run'}),
}


def fail(path, message):
    raise ValueError(f'ERR_ARCHITECTURE:{path}: {message}')


def unique(rows, key, path):
    values = [row[key] for row in rows]
    if len(values) != len(set(values)):
        fail(path, f'duplicate {key}')
    return set(values)


def validate_cost_semantics(document):
    """Reject valid-looking references that change the meaning of engine totals."""
    structures = document['cost_structures']
    if unique(structures, 'id', 'cost_structures') != set(COST_SEMANTICS):
        fail('cost_structures', 'missing or unknown cost structure')
    for structure in structures:
        sid = structure['id']; path = 'cost_structures/' + sid
        notion, natures, activities = COST_SEMANTICS[sid]
        if structure['notion'] != notion:
            fail(path + '/notion', 'incompatible cost notion')
        if set(structure['cost_nature_refs']) != natures:
            fail(path + '/cost_nature_refs', 'incompatible calculated natures')
        if set(structure['activity_type_refs']) != activities:
            fail(path + '/activity_type_refs', 'incompatible Build/Run convention')
        if ('activity_allocation' in structure) != (sid == 'client_care'):
            fail(path + '/activity_allocation', 'only client care has a quantified Build/Run allocation')


def validate_architecture(document, glossary):
    """Validate independently of the UI, preserving stable identities and conditions."""
    errors = list(Draft202012Validator(read(ROOT / SCHEMA)).iter_errors(document))
    if errors:
        error = errors[0]
        fail(SOURCE + '/' + '/'.join(map(str, error.absolute_path)), error.message)
    activity_ids = unique(document['activity_types'], 'id', 'activity_types')
    expected_activities = {'build': 'build', 'run': 'run_activities'}
    if activity_ids != set(expected_activities):
        fail('activity_types', 'expected Build and Run activity identities')
    for activity in document['activity_types']:
        if activity['notion'] not in glossary['notions']:
            fail('activity_types/' + activity['id'], 'unknown glossary notion')
        if activity['notion'] != expected_activities[activity['id']]:
            fail('activity_types/' + activity['id'], 'incompatible activity notion')
    layers = unique(document['layers'], 'id', 'layers')
    parts = [part for layer in document['layers'] for part in layer.get('parts', [])]
    part_ids = unique(parts, 'id', 'parts')
    if layers & part_ids:
        fail('parts', 'layer and part identities must be distinct')
    unique(document['cost_structures'], 'id', 'cost_structures')
    unique(document['cost_structures'], 'notion', 'cost_structures')
    natures = [ref for item in document['cost_structures'] for ref in item['cost_nature_refs']]
    if len(natures) != len(set(natures)):
        fail('cost_nature_refs', 'a calculated nature must belong to one structure only')
    validate_cost_semantics(document)
    used_conditions = set()
    for structure in document['cost_structures']:
        path = 'cost_structures/' + structure['id']
        if structure['notion'] not in glossary['notions']:
            fail(path, 'unknown glossary notion')
        if not set(structure['activity_type_refs']) <= activity_ids:
            fail(path, 'unknown activity type')
        if 'activity_allocation' in structure and set(structure['activity_type_refs']) != activity_ids:
            fail(path, 'activity allocation requires both Build and Run')
        if 'activity_allocation' in structure and not 0 <= structure['activity_allocation']['build_pct'] <= 100:
            fail(path, 'Build allocation must be a finite percentage between 0 and 100')
        coverage = unique(structure['coverage'], 'layer', path)
        if not coverage <= layers:
            fail(path, 'unknown layer')
        for link in structure['coverage']:
            if 'condition' in link:
                if link['condition'] not in document['conditions']:
                    fail(path, 'unknown coverage condition')
                used_conditions.add(link['condition'])
    if used_conditions != set(document['conditions']):
        fail('conditions', 'unused coverage condition')
    validate_glossary_literals(document, glossary, path=SOURCE)
    resolve_text_tree(document, glossary, path=SOURCE)
    return deepcopy(document)


def load_architecture(glossary):
    return validate_architecture(read(ROOT / SOURCE), glossary)


def validate_economic_links(document, baseline):
    """Check the classification against actual engine output, without new sums or budgets."""
    validate_cost_semantics(document)
    expected = {ref for item in document['cost_structures'] for ref in item['cost_nature_refs']}
    for option in baseline['options']:
        for row in option['annual']:
            if set(row['cost_natures']) != expected:
                fail('cost_nature_refs/' + option['stack'], 'missing or unknown calculated nature')


def hydrate_architecture(ui, document):
    """Project the domain model into the existing diagram transport contract."""
    view = ui['essential']['model_architecture']
    if set(view) != {'source', 'title', 'intro', 'layers_title', 'layer_icons', 'blocks'} or view['source'] != SOURCE:
        fail('view', 'expected canonical source and presentation settings only')
    layer_ids = [layer['id'] for layer in document['layers']]
    if set(view['layer_icons']) != set(layer_ids):
        fail('view/layer_icons', 'missing or unknown layer')
    icons = {'applications', 'process', 'integration', 'core', 'platform', 'containers', 'infrastructure'}
    if any(icon not in icons for icon in view['layer_icons'].values()):
        fail('view/layer_icons', 'unsupported icon')
    structures = {item['id']: item for item in document['cost_structures']}
    activities = {item['id']: item for item in document['activity_types']}
    rows = ui['essential']['model_rows']
    if unique(rows, 'key', 'view/model_rows') != set(structures):
        fail('view/model_rows', 'missing or unknown cost structure')
    for row in rows:
        if set(row) != {'key', 'icon'} or row['icon'] != row['key']:
            fail('view/model_rows/' + row['key'], 'only cost identity and icon are allowed')
    blocks = view['blocks']
    for block in blocks:
        if not isinstance(block, dict) or not {'cost', 'lane'} <= set(block) or set(block) - {'cost', 'lane', 'lane_span'}:
            fail('view/blocks', 'only cost reference and placement are allowed')
        for key in ('lane', 'lane_span'):
            value = block.get(key, 1)
            if type(value) is not int or not 1 <= value <= 4:
                fail('view/blocks', 'invalid lane or span')
        if block['lane'] + block.get('lane_span', 1) > 5:
            fail('view/blocks', 'placement exceeds four lanes')
    if unique(blocks, 'cost', 'view/blocks') != set(structures):
        fail('view/blocks', 'missing or unknown cost structure')
    compiled = {key: deepcopy(view[key]) for key in ('title', 'intro', 'layers_title')}
    compiled['layers'] = []
    for layer in document['layers']:
        item = {key: deepcopy(value) for key, value in layer.items() if key != 'definition'}
        for part in item.get('parts', []):
            part.pop('id')
        item['icon'] = view['layer_icons'][layer['id']]
        compiled['layers'].append(item)
    compiled['blocks'] = []
    occupied = set()
    for block in blocks:
        coverage = structures[block['cost']]['coverage']
        ids = [link['layer'] for link in coverage]
        positions = sorted(layer_ids.index(id) for id in ids)
        if positions != list(range(min(positions), max(positions) + 1)):
            fail('view/blocks/' + block['cost'], 'non-contiguous coverage requires another rendering')
        cells = {(row, lane) for row in positions for lane in range(block['lane'], block['lane'] + block.get('lane_span', 1))}
        if occupied & cells:
            fail('view/blocks/' + block['cost'], 'overlapping cost blocks')
        occupied |= cells
        item = {**deepcopy(block), 'layers': ids}
        conditions = list(dict.fromkeys(link['condition'] for link in coverage if 'condition' in link))
        if conditions:
            item['scope_note'] = ' '.join(document['conditions'][key] for key in conditions)
        compiled['blocks'].append(item)
    compiled['note'] = document['rules']['financing']
    compiled['service_note'] = document['rules']['ownership']
    result = deepcopy(ui)
    result['essential']['model_rows'] = [
        {**deepcopy(row), 'title': '{{notion.' + structures[row['key']]['notion'] + '}}',
         'activity_tags': [{'id': ref, 'label': '{{notion.' + activities[ref]['notion'] + '}}'}
                           for ref in structures[row['key']]['activity_type_refs']],
         'activity_scope': structures[row['key']]['activity_scope'],
         **deepcopy(structures[row['key']]['description'])} for row in rows]
    for row in result['essential']['model_rows']:
        allocation = structures[row['key']].get('activity_allocation')
        if allocation is not None:
            row['activity_allocation'] = {
                **deepcopy(allocation), 'run_pct': 100 - allocation['build_pct'],
                'source': SOURCE + '#cost_structures/' + row['key'] + '/activity_allocation'}
    result['essential']['model_architecture'] = compiled
    return result
