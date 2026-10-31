"""Project documentary delivery conditions, never change economics or simulations."""
from copy import deepcopy
from urllib.parse import urlencode, urlsplit

from jsonschema import Draft202012Validator
from content_model import resolve_text_tree, validate_glossary_literals
from validate_stacks import ROOT, read

METHOD_SOURCE = 'source/conditions-realisation.yaml'
DOSSIER_SOURCE = 'source/capacite-realisation.yaml'
ERROR = 'ERR_DELIVERY_READINESS'
ATLAS = 'https://laurent-sintes.github.io/Urbanisation-SCM/'
ROUTES = {'#vision', '#modele', '#marche', '#synvance', '#conditions-realisation',
          '#capacite-realisation', '#cartographie', '#modele?section=scope'}


def obj(properties):
    return dict(type='object', properties=properties, required=list(properties), additionalProperties=False)


def array(items, minimum=1):
    return dict(type='array', items=items, minItems=minimum)


TEXT = dict(type='string', minLength=1, pattern=r'\S')
ID = dict(type='string', pattern='^[a-z][a-z0-9-]*$')
TEXTS = array(TEXT)
REFS = dict(type='array', items=TEXT, minItems=1, uniqueItems=True)
TITLE_TEXT = obj(dict(title=TEXT, text=TEXT))
LINK = obj(dict(href=TEXT, label=TEXT))
BLOCK = dict(oneOf=[obj(dict(kind=dict(enum=['paragraphs', 'bullets']), items=TEXTS)),
    obj(dict(kind=dict(const='table'), caption=TEXT, columns=TEXTS, rows=array(TEXTS))),
    obj(dict(kind=dict(const='links'), items=array(LINK)))])
METHOD_SCHEMA = obj(dict(version=dict(const=1), id=dict(const='conditions-realisation'),
    principle=TITLE_TEXT, notice=TITLE_TEXT, navigation_label=TEXT, result_label=TEXT,
    criteria=array(obj(dict(id=ID, title=TEXT, lead=TEXT, expected=TEXT, blocks=array(BLOCK)))), next=LINK))
STATES = ('a_constituer', 'a_confirmer', 'a_demontrer')
DOSSIER_SCHEMA = obj(dict(version=dict(const=1), id=dict(const='capacite-realisation'), date=TEXT,
    principle=TITLE_TEXT, notice=TITLE_TEXT, navigation_label=TEXT, method_link=LINK,
    context=obj(dict(source=TEXT, status=dict(const='rapporte'), text=TEXT)),
    labels=obj(dict(states=obj({key: TEXT for key in STATES}),
        proof_states=obj({key: TEXT for key in ('disponible', 'attendue')}),
        role_columns=dict(type='array', items=TEXT, minItems=3, maxItems=3),
        proof_columns=dict(type='array', items=TEXT, minItems=3, maxItems=3),
        partner_columns=dict(type='array', items=TEXT, minItems=2, maxItems=2),
        **{key: TEXT for key in ('proof_label', 'validation_label', 'proceed_label', 'reconsider_label',
             'risk_label', 'action_label', 'available_label', 'gate_label', 'capability_label',
             'review_date', 'available_summary', 'expected_summary', 'validation_suffix', 'proof_access', 'actor_label', 'partner_requirement')})),
    sections=obj({key: obj(dict(title=TEXT, lead=TEXT)) for key in ('organisation', 'points-chauds', 'partenaire', 'jalons')}),
    scope=obj(dict(id=dict(const='perimetre'), title=TEXT, introduction=TEXT, note=TEXT, link=LINK,
        labels=obj({key: TEXT for key in ('search', 'results', 'boundary', 'native_reference', 'back_label', 'capture_date', 'version',
            'navigation_title', 'hierarchy_summary', 'open_capabilities', 'back_to_navigation', 'capability_count', 'capability_count_one',
            'results_one', 'no_results', 'subdomain', 'business_area')}))),
    proofs=array(obj(dict(id=ID, title=TEXT, short_title=TEXT, status=dict(enum=['disponible', 'attendue']),
        kind=dict(enum=['document_entree', 'reference_partenaire', 'preuve_realisation']),
        source_ref=dict(type=['string', 'null']), href=dict(type=['string', 'null']), detail=TEXT))),
    roles=array(obj(dict(id=ID, title=TEXT, actor=TEXT, validation_owner=TEXT,
        status=dict(enum=list(STATES)), criteria_refs=REFS, proof_refs=REFS, decision_ref=ID))),
    hotspots=array(obj(dict(id=ID, title=TEXT, capability_refs=REFS, risk=TEXT, action=TEXT,
        available_refs=REFS, expected_refs=REFS, gate_ref=ID, role_ref=ID))),
    partner=array(obj(dict(id=ID, title=TEXT, proof_ref=ID))),
    gates=array(obj(dict(id=ID, title=TEXT, expected=TEXT, validation_owner=TEXT,
        status=dict(enum=list(STATES)), criteria_refs=REFS, proof_refs=REFS,
        depends_on=dict(type='array', items=ID, uniqueItems=True), decision_ref=ID,
        proceed=TEXT, reconsider=TEXT))), next=LINK))


def require(condition, message):
    if not condition:
        raise ValueError(ERROR + ':' + message)


def index(rows, label):
    result = {row['id']: row for row in rows}
    require(len(result) == len(rows), 'duplicate ' + label)
    return result


def validate_schema(value, schema, source):
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda error: str(error.path))
    if errors:
        error = errors[0]
        raise ValueError(f'{ERROR}:{source}:{list(error.path)}:{error.message}')


def compile_delivery(method, dossier, complexity, snapshot, decision, glossary, document_path):
    """Validate a closed evidence register and produce two continuous reading pages."""
    validate_schema(method, METHOD_SCHEMA, METHOD_SOURCE)
    validate_schema(dossier, DOSSIER_SCHEMA, DOSSIER_SOURCE)
    for value, source in ((method, METHOD_SOURCE), (dossier, DOSSIER_SOURCE)):
        validate_glossary_literals(value, glossary, path=source)
    method = resolve_text_tree(deepcopy(method), glossary, path=METHOD_SOURCE)
    dossier = resolve_text_tree(deepcopy(dossier), glossary, path=DOSSIER_SOURCE)
    criteria = index(method['criteria'], 'criterion')
    proofs = index(dossier['proofs'], 'proof')
    roles = index(dossier['roles'], 'role')
    gates = index(dossier['gates'], 'gate')
    index(dossier['hotspots'], 'hotspot')
    index(dossier['partner'], 'partner question')
    capabilities = {row['capacite_id']: row for row in complexity['rows']}
    require(len(capabilities) == len(complexity['rows']), 'duplicate native capability')
    decision_criteria = index(decision['criteres'], 'decision criterion')
    decision_proofs = index(decision['preuves'], 'decision proof')
    require(dossier['scope']['link']['href'] == ATLAS, 'unregistered cartography destination')

    def refs(values, known, location):
        require(set(values) <= set(known), 'unknown ' + location)

    def link(href):
        require(href in ROUTES or href == ATLAS, 'unknown reading link:' + href)
        require(not urlsplit(href).path.lower().endswith(('.yaml', '.yml')), 'model data link')

    link(method['next']['href'])
    link(dossier['next']['href'])
    link(dossier['method_link']['href'])
    for criterion in criteria.values():
        for block in criterion['blocks']:
            if block['kind'] == 'links':
                for item in block['items']:
                    link(item['href'])
            if block['kind'] == 'table':
                require(all(len(row) == len(block['columns']) for row in block['rows']), 'table width')
    for proof in proofs.values():
        if proof['status'] == 'attendue':
            require(proof['source_ref'] is None and proof['href'] is None, 'expected proof has invented document')
        else:
            require(bool(proof['source_ref']) and bool(proof['href']), 'available proof lacks source')
            require(not proof['source_ref'].startswith(('http:', 'https:')), 'available proof needs a local recorded source')
            document_path(proof['source_ref'])
            link(proof['href'])
    for role in roles.values():
        refs(role['criteria_refs'], criteria, 'role criterion')
        refs(role['proof_refs'], proofs, 'role proof')
        require(role['decision_ref'] in decision_criteria, 'unknown organisation decision basis')
    for gate in gates.values():
        refs(gate['criteria_refs'], criteria, 'gate criterion')
        refs(gate['proof_refs'], proofs, 'gate proof')
        refs(gate['depends_on'], gates, 'preceding gate')
        require(gate['decision_ref'] in decision_proofs, 'unknown decision proof basis')
    visited = set()

    def visit(key, path):
        require(key not in path, 'cyclic gate sequence')
        if key not in visited:
            for previous in gates[key]['depends_on']:
                visit(previous, path | {key})
            visited.add(key)

    for key in gates:
        visit(key, set())
    for hotspot in dossier['hotspots']:
        refs(hotspot['capability_refs'], capabilities, 'hotspot capability')
        refs(hotspot['available_refs'], proofs, 'hotspot available proof')
        refs(hotspot['expected_refs'], proofs, 'hotspot expected proof')
        require(all(proofs[key]['status'] == 'disponible' for key in hotspot['available_refs']), 'unavailable hotspot input')
        require(all(proofs[key]['status'] == 'attendue' for key in hotspot['expected_refs']), 'hotspot expected proof state')
        require(hotspot['gate_ref'] in gates and hotspot['role_ref'] in roles, 'unknown hotspot actor or gate')
    for question in dossier['partner']:
        require(question['proof_ref'] in proofs, 'unknown partner proof')
    document_path('source/decision-make-buy.yaml')
    document_path(complexity['source'])
    require(snapshot['domaine_id'] == complexity['rows'][0]['chemin'][0], 'scope snapshot mismatch')
    native = {node['id']: node for node in snapshot['nodes']}
    require(set(capabilities) <= set(native), 'scope absent from capture')

    def page(source):
        return {key: deepcopy(source[key]) for key in ('id', 'principle', 'notice', 'navigation_label', 'next')}

    method_page = page(method)
    method_page.update(examples=[], sections=[dict(id=row['id'], title=row['title'], lead=row['lead'],
        blocks=[*row['blocks'], dict(kind='callout', title=method['result_label'], text=row['expected'])])
        for row in method['criteria']])
    result = page(dossier)
    result.update(examples=[], sections=[dict(id=key, **value, blocks=[]) for key, value in dossier['sections'].items()])
    # One documentary register; relations keep IDs rather than repeating proof text.
    for key in ('date', 'context', 'labels', 'method_link', 'roles', 'hotspots', 'partner', 'gates', 'proofs'):
        result[key] = deepcopy(dossier[key])
    scope = deepcopy(dossier['scope'])
    scope['source'] = dict(path=complexity['source'], date=snapshot['date_capture'],
        version=snapshot['provenance']['version'], revision=snapshot['provenance']['sha256'])
    scope['rows'] = [dict(id=row['id'], capability_id=row['capacite_id'], name=row['capacite']['nom'],
        path=[node['nom'] for node in row['hierarchie']], boundary=row['capacite']['perimetre'], definition=row['capacite']['definition'],
        href=ATLAS + '#/sheet?' + urlencode({'node': row['capacite_id']})) for row in complexity['rows']]
    domains = {}
    for row in complexity['rows']:
        domain, subdomain, area = row['hierarchie']
        domain_group = domains.setdefault(domain['id'], dict(id=domain['id'], label=domain['nom'], subdomains={}))
        subdomain_group = domain_group['subdomains'].setdefault(subdomain['id'],
            dict(id=subdomain['id'], label=subdomain['nom'], areas={}))
        area_group = subdomain_group['areas'].setdefault(area['id'],
            dict(id=area['id'], label=area['nom'], capability_ids=[]))
        area_group['capability_ids'].append(row['capacite_id'])
    scope['hierarchy'] = [dict(id=domain['id'], label=domain['label'], subdomains=[
        dict(id=subdomain['id'], label=subdomain['label'], areas=list(subdomain['areas'].values()))
        for subdomain in domain['subdomains'].values()]) for domain in domains.values()]
    result['scope'] = scope
    return method_page, result


def build_delivery_readiness(complexity, glossary, document_path):
    return compile_delivery(read(ROOT / METHOD_SOURCE), read(ROOT / DOSSIER_SOURCE), complexity,
        read(ROOT / complexity['source']), read(ROOT / 'source/decision-make-buy.yaml'), glossary, document_path)
