"""Domain objects and relationships behind the Model page; no economic calculation."""
from copy import deepcopy

from jsonschema import Draft202012Validator

from content_model import resolve_text_tree, validate_glossary_literals
from validate_stacks import ROOT, read

SOURCE = 'source/fondamentaux.yaml'
SCHEMA = 'source/schema-fondamentaux.yaml'
READING_CHAPTERS = ('scope', 'strategies', 'activities', 'workload', 'costs', 'calendar')


def fail(path, message):
    raise ValueError(f'ERR_FUNDAMENTALS:{path}: {message}')


def index(rows, key, path):
    result = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get(key), str):
            fail(path, 'missing identity: ' + key)
        if row[key] in result:
            fail(path, 'duplicate identity: ' + row[key])
        result[row[key]] = row
    return result


def compile_fundamentals(document, glossary, architecture, options, native):
    errors = list(Draft202012Validator(read(ROOT / SCHEMA)).iter_errors(document))
    if errors:
        error = errors[0]
        fail('/'.join(map(str, error.absolute_path)), error.message)
    entities = index(document['entities'], 'id', 'entities')
    relations = index(document['relations'], 'id', 'relations')
    strategies = index(document['strategies'], 'id', 'strategies')
    phases = index(document['phases'], 'id', 'phases')
    activities = index(architecture['activity_types'], 'id', 'activity_types')
    chapters = index(document['reading']['chapters'], 'id', 'reading/chapters')
    if tuple(chapters) != READING_CHAPTERS:
        fail('reading/chapters', 'expected the six concepts in their reading order')
    links = index(document['reading']['strategy_links'], 'href', 'reading/strategy_links')
    if set(links) != {'source/offres-synvance.md', '#etude-marche'}:
        fail('reading/strategy_links', 'missing strategy evidence route')
    for href in links:
        if href.startswith('source/') and not (ROOT / href).is_file():
            fail('reading/strategy_links', 'missing strategy evidence document: ' + href)
    if set(document['activity_reading']['type_refs']) != set(activities):
        fail('activity_reading/type_refs', 'missing or unknown activity type')
    activity_summaries = index(document['activity_reading']['summaries'], 'type_ref', 'activity_reading/summaries')
    if set(activity_summaries) != set(activities):
        fail('activity_reading/summaries', 'missing or unknown activity summary')
    stages = index(document['estimation']['stages'], 'id', 'estimation/stages')
    if {stage['notion'] for stage in stages.values()} != {'charge_brute','charge_nette','charge_totale_projet'}:
        fail('estimation/stages', 'expected gross, net and total project notions')
    for stage in stages.values():
        if stage['notion'] not in glossary['notions']:
            fail(stage['id'], 'unknown workload notion')
    transitions = index(document['estimation']['relations'], 'operation', 'estimation/relations')
    expected_transitions = {'apply_productivity': ('charge_brute','charge_nette'),
                            'add_project_activities': ('charge_nette','charge_totale_projet')}
    if set(transitions) != set(expected_transitions):
        fail('estimation/relations', 'missing workload transition')
    for operation, relation in transitions.items():
        source, target = relation['source_ref'], relation['target_ref']
        if source not in stages or target not in stages:
            fail('estimation/relations', 'unknown workload stage')
        if (stages[source]['notion'], stages[target]['notion']) != expected_transitions[operation]:
            fail('estimation/relations', 'incompatible workload transition')
    layer_ids = {layer['id'] for layer in architecture['layers']}
    cost_ids = {cost['id'] for cost in architecture['cost_structures']}
    if document['program_ref'] not in entities or entities[document['program_ref']]['kind'] != 'program':
        fail('program_ref', 'unknown program')
    for item in [*entities.values(), *strategies.values(), *phases.values()]:
        if 'notion' in item and item['notion'] not in glossary['notions']:
            fail(item['id'], 'unknown glossary notion')
    for entity in entities.values():
        if not set(entity.get('layer_refs', [])) <= layer_ids:
            fail(entity['id'], 'unknown architecture layer')
    triples = set()
    signatures = {'implements': ({'platform'}, {'platform'}),
                  'composed_of': ({'platform'}, {'platform', 'adaptations'}),
                  'targets': ({'program'}, {'platform'}),
                  'unifies': ({'platform'}, {'information_system'})}
    for relation in relations.values():
        source, target = relation['source'], relation['target']
        if source not in entities or target not in entities or source == target:
            fail(relation['id'], 'unknown or reflexive entity relationship')
        sources, targets = signatures[relation['type']]
        if entities[source]['kind'] not in sources or entities[target]['kind'] not in targets:
            fail(relation['id'], 'incompatible entity kinds')
        triple = (source, relation['type'], target)
        if triple in triples:
            fail(relation['id'], 'duplicate relationship')
        triples.add(triple)
    if {ref for source, _, target in triples for ref in (source, target)} != set(entities):
        fail('relations', 'entity has no relationship')
    # Composition and implementation cannot contain circular definitions.
    graph = {key: [] for key in entities}
    for source, kind, target in triples:
        if kind in ('composed_of', 'implements'):
            graph[source].append(target)
    done = set()
    def visit(key, path):
        if key in path:
            fail(key, 'cyclic composition or implementation')
        if key in done:
            return
        for target in graph[key]:
            visit(target, path | {key})
        done.add(key)
    for key in graph:
        visit(key, set())
    economic_options = index(options, 'stack', 'options')
    assigned = set()
    for strategy in strategies.values():
        if strategy['target_ref'] not in entities or entities[strategy['target_ref']]['kind'] != 'platform':
            fail(strategy['id'], 'unknown strategy target')
        implementation = strategy.get('implementation_ref')
        if strategy['mode'] == 'Make' and not implementation:
            fail(strategy['id'], 'Make requires an implementation')
        if implementation and (implementation, 'implements', strategy['target_ref']) not in triples:
            fail(strategy['id'], 'missing implementation relationship')
        for option in strategy['option_refs']:
            if option not in economic_options or economic_options[option]['mode'] != strategy['mode']:
                fail(strategy['id'], 'unknown option or incompatible Make/Buy mode')
            if option in assigned:
                fail(option, 'option assigned to multiple strategies')
            assigned.add(option)
    if assigned != set(economic_options):
        fail('strategies', 'unassigned economic option')
    used_costs = set()
    for phase in phases.values():
        if phase['target_ref'] not in entities or entities[phase['target_ref']]['kind'] != 'platform':
            fail(phase['id'], 'unknown phase target')
        if not set(phase['costs']) <= cost_ids:
            fail(phase['id'], 'unknown cost structure')
        used_costs.update(phase['costs'])
    if used_costs != cost_ids:
        fail('phases', 'cost structure absent from every phase')
    mapping = document['business_map']
    selected_systems = index(mapping['systems'], 'node_ref', 'business_map/systems')
    nodes = index(native['nodes'], 'id', 'native/nodes')
    native_relations = index(native['relations'], 'id', 'native/relations')
    selected_nodes, selected_relations, domains = {}, {}, set()
    for system in selected_systems.values():
        ref = system['node_ref']
        if ref not in nodes or nodes[ref]['kind'] != 'business_system':
            fail(ref, 'unknown native business system')
        selected_nodes[ref] = nodes[ref]
        for relation_ref in system['domain_relation_refs']:
            relation = native_relations.get(relation_ref)
            if not relation or relation['type'] != 'presents' or relation['source_id'] != ref:
                fail(ref, 'unknown or mismatched native domain relationship')
            target = relation['target_id']
            if target not in nodes or nodes[target]['kind'] != 'domain' or target in domains:
                fail(ref, 'unknown or repeated native domain')
            domains.add(target)
            selected_nodes[target] = nodes[target]
            selected_relations[relation_ref] = relation
    scope, positioning = mapping['program_scope'], mapping['positioning']
    if scope['entity_ref'] not in entities or scope['system_ref'] not in selected_systems:
        fail('program_scope', 'unknown program or system')
    if entities[scope['entity_ref']]['kind'] != 'program':
        fail('program_scope', 'scope owner must be a program')
    if scope['entity_ref'] != document['program_ref']:
        fail('program_scope', 'scope belongs to another program')
    if not set(mapping['outside_scope']) <= set(selected_systems) or scope['system_ref'] in mapping['outside_scope']:
        fail('outside_scope', 'unknown system or conflicting program scope')
    if positioning['entity_ref'] not in entities or positioning['domain_ref'] not in domains:
        fail('positioning', 'unknown platform or domain')
    if entities[positioning['entity_ref']]['kind'] != 'platform':
        fail('positioning', 'positioned entity must be a platform')
    scope_domains = {native_relations[ref]['target_id'] for ref in selected_systems[scope['system_ref']]['domain_relation_refs']}
    if positioning['domain_ref'] not in scope_domains:
        fail('positioning', 'platform positioned outside the program scope')
    prose = deepcopy(document)
    for strategy in prose['strategies']:
        strategy.pop('mode')  # Engine enum, not an editable display caption.
    validate_glossary_literals(prose, glossary, path=SOURCE)
    resolve_text_tree(document, glossary, path=SOURCE)
    result = deepcopy(document)
    result['activity_reading']['types'] = [
        {'id': ref, 'notion': activities[ref]['notion'],
         'label': '{{notion.' + activities[ref]['notion'] + '}}',
         'text': activity_summaries[ref]['text'],
         'definition': glossary['notions'][activities[ref]['notion']]['definition']}
        for ref in document['activity_reading']['type_refs']]
    # Preserve native identity and evidence references without duplicating the full atlas in the bootstrap.
    result['native_map'] = {
        'nodes': [{'id': n['id'], 'kind': n['kind'], 'label': n['fields']['name'],
                   'source_refs': deepcopy(n.get('source_refs', []))} for n in selected_nodes.values()],
        'relations': [{key: deepcopy(r[key]) for key in ('id', 'type', 'source_id', 'target_id', 'source_refs')}
                      for r in selected_relations.values()]}
    return result


def load_fundamentals(glossary, architecture, options):
    document = read(ROOT / SOURCE)
    # Validate the source pointer before opening any file it names.
    errors = list(Draft202012Validator(read(ROOT / SCHEMA)).iter_errors(document))
    if errors:
        fail(SOURCE, errors[0].message)
    return compile_fundamentals(document, glossary, architecture, options,
                                read(ROOT / document['business_map']['source']))


def hydrate_fundamentals(ui, document):
    e = ui['essential']
    if e.get('fundamentals') != {'source': SOURCE}:
        fail('view', 'expected canonical fundamentals source')
    if any(key in e for key in ('calendar_text', 'model_limit', 'model_workload', 'model_activities', 'model_reading',
                              'model_concepts', 'model_choice', 'model_calendar', 'model_complexity_link')):
        fail('view', 'domain explanations cannot be overridden locally')
    if 'intro' in e['pages']['modele']:
        fail('view/pages/modele', 'introduction belongs to the fundamentals source')
    entities = {item['id']: item for item in document['entities']}
    result = deepcopy(ui)
    target = result['essential']
    target['model_reading'] = deepcopy(document['reading'])
    target['model_reading'].update({
        'scope': document['business_map']['scope_summary'],
        'activity_note': document['activity_reading']['note'],
        'workload_note': document['estimation']['note'],
    })
    target['pages']['modele']['intro'] = document['reading']['intro']
    chapters = {item['id']: item for item in document['reading']['chapters']}
    # Keep resolved captions compatible while the source owns their single definition.
    for key, chapter in (('model_concepts', 'scope'), ('model_choice', 'strategies'), ('model_calendar', 'calendar')):
        target[key] = chapters[chapter]['title']
    target['model_complexity_link'] = document['reading']['next_label']
    target['model_workload'] = deepcopy(document['estimation'])
    target['model_activities'] = {key: deepcopy(document['activity_reading'][key])
                                for key in ('title', 'intro', 'note', 'types')}
    index(e['concepts'], 'entity_ref', 'view/concepts')
    target['concepts'] = []
    for concept in e['concepts']:
        if set(concept) != {'entity_ref', 'icon'} or concept['entity_ref'] not in entities:
            fail('view/concepts', 'only an existing entity reference and icon are allowed')
        entity = entities[concept['entity_ref']]
        if 'notion' not in entity or 'text' not in entity:
            fail('view/concepts', 'displayed context entity requires a glossary notion and a short reading text')
        target['concepts'].append({'notion': entity['notion'], 'icon': concept['icon'], 'text': entity['text']})
    for ui_key, domain_key, ref, prose in (
        ('choices', 'strategies', 'strategy_ref', ('tags', 'text')),
        ('calendar', 'phases', 'phase_ref', ('text', 'bullets', 'costs'))):
        owners = {item['id']: item for item in document[domain_key]}
        if set(index(e[ui_key], ref, 'view/' + ui_key)) != set(owners):
            fail('view/' + ui_key, 'missing or unknown domain reference')
        target[ui_key] = []
        settings = {item[ref]: item for item in e[ui_key]}
        for item in e[ui_key]:
            if set(item) != {ref, 'icon'}:
                fail('view/' + ui_key, 'only identity and icon are allowed')
        for owner in document[domain_key]:
            item = settings[owner['id']]
            target[ui_key].append({'title': '{{notion.' + owner['notion'] + '}}', 'icon': item['icon'],
                                   **{key: deepcopy(owner[key]) for key in prose if key in owner}})
    target['calendar_text'] = document['phase_reading']
    target['model_limit'] = document['limitations']
    view = e['model_map']
    allowed = {'title', 'caption', 'note_title', 'program_scope', 'outside_scope', 'systems'}
    if set(view) != allowed:
        fail('view/model_map', 'only headings, status labels and layout are allowed')
    mapping = document['business_map']
    systems = {s['node_ref']: s for s in mapping['systems']}
    nodes = {n['id']: n for n in document['native_map']['nodes']}
    relations = {r['id']: r for r in document['native_map']['relations']}
    if set(index(view['systems'], 'system_ref', 'view/model_map/systems')) != set(systems):
        fail('view/model_map/systems', 'missing or unknown native system reference')
    positions = set()
    compiled = {key: deepcopy(value) for key, value in view.items() if key != 'systems'}
    compiled.update({key: deepcopy(mapping[key]) for key in ('source', 'note', 'estimation', 'scope')})
    notion = entities[mapping['positioning']['entity_ref']].get('notion')
    if not notion:
        fail('positioning', 'platform badge requires a glossary notion')
    compiled['flow'] = '{{notion.' + notion + '.court}}'
    compiled['systems'] = []
    for setting in view['systems']:
        if set(setting) != {'system_ref', 'position'} or setting['position'] not in {'left', 'center', 'right', 'bottom'}:
            fail('view/model_map/systems', 'invalid position or domain override')
        if setting['position'] in positions:
            fail('view/model_map/systems', 'overlapping positions')
        positions.add(setting['position'])
        ref = setting['system_ref']
        item = {'id': ref, 'label': nodes[ref]['label'], 'position': setting['position'], 'domains': []}
        if ref == mapping['program_scope']['system_ref']:
            item['program_scope'] = True
        if ref in mapping['outside_scope']:
            item['outside_scope'] = True
        for relation_ref in systems[ref]['domain_relation_refs']:
            domain = nodes[relations[relation_ref]['target_id']]
            child = {'id': domain['id'], 'label': domain['label']}
            if domain['id'] == mapping['positioning']['domain_ref']:
                child['flow'] = True
            item['domains'].append(child)
        compiled['systems'].append(item)
    target['model_map'] = compiled
    target.pop('fundamentals')
    return result
