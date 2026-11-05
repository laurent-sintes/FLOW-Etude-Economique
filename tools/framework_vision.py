"""Validate the short framework overview without adding economic inputs."""
from copy import deepcopy

from jsonschema import Draft202012Validator

from content_model import resolve_text_tree, validate_glossary_literals
from validate_stacks import ROOT, read


SOURCE = 'source/vision-framework.yaml'
ERROR = 'ERR_FRAMEWORK_VISION'


def _object(properties):
    return dict(type='object', properties=properties, required=list(properties),
                additionalProperties=False)


TEXT = dict(type='string', minLength=1, pattern=r'\S')
IDENTIFIER = dict(type='string', pattern='^[a-z][a-z0-9-]*$')
TITLE_TEXT = _object(dict(title=TEXT, text=TEXT))
PARAGRAPHS = dict(type='array', minItems=1, items=TEXT)
MATRIX_ROW = _object(dict(id=IDENTIFIER, title=TEXT, make=PARAGRAPHS, buy=PARAGRAPHS))
READING_LINK = _object(dict(href=TEXT, label=TEXT))
PROOF_LEVEL = _object(dict(id=IDENTIFIER, title=TEXT, text=TEXT, href=TEXT, label=TEXT))
SCHEMA = _object(dict(
    version=dict(const=1), id=dict(const='framework-vision'),
    opening=TITLE_TEXT,
    adaptation=_object(dict(title=TEXT, text=TEXT, href=dict(const='#comparer'), label=TEXT,
        reference_link=_object(dict(href=dict(const='#parametres'), label=TEXT)))),
    approach=_object(dict(title=TEXT,intro=TEXT,
        labels=_object(dict(inputs=TEXT,treatment=TEXT,output=TEXT,links=TEXT)),
        steps=dict(type='array',minItems=7,maxItems=7,
        items=_object(dict(id=IDENTIFIER,title=TEXT,text=TEXT,inputs=TEXT,treatment=TEXT,output=TEXT,
            links=dict(type='array',minItems=1,items=READING_LINK)))),
        matrix=_object(dict(caption=TEXT, activity_label=TEXT, make_label=TEXT, buy_label=TEXT,
            rows=dict(type='array', minItems=3, maxItems=3, items=MATRIX_ROW), notes=PARAGRAPHS)))),
    evidence=_object(dict(title=TEXT, items=dict(type='array', minItems=1,
        items=_object(dict(id=IDENTIFIER, title=TEXT, text=TEXT, href=TEXT, label=TEXT))))),
    confidence=_object(dict(title=TEXT, text=TEXT,
        levels=dict(type='array', minItems=4, maxItems=4, items=PROOF_LEVEL),
        links=dict(type='array', minItems=1, items=READING_LINK), limits_title=TEXT,
        limits=dict(type='array', minItems=1, items=TEXT))),
    next=_object(dict(title=TEXT, links=dict(type='array', minItems=3, maxItems=3, items=READING_LINK))),
))

ARRAY_TEXT = dict(type='array', minItems=1, items=TEXT)
PROVIDER = _object(dict(option_ref=TEXT, status=TEXT, example=TEXT, inputs=ARRAY_TEXT, treatment=ARRAY_TEXT, output=TEXT,
    limits=ARRAY_TEXT, links=dict(type='array', minItems=1, items=READING_LINK)))
STACK_READING = _object(dict(title=TEXT, intro=TEXT, choices=TEXT,
    groups=dict(type='array', minItems=1, items=_object(dict(title=TEXT,
        element_refs=dict(type='array', minItems=1, uniqueItems=True, items=TEXT))))))
PROVIDER['properties']['stack_reading'] = STACK_READING

MAKE_AUDIT = _object(dict(title=TEXT,intro=TEXT,steps=dict(type='array',minItems=1,items=_object(dict(title=TEXT,text=TEXT,rule_refs=dict(type='array',uniqueItems=True,items=TEXT)))),method=dict(enum=['core_method','net_method','run_method']),sections=dict(type='array',uniqueItems=True,items=TEXT),links=dict(type='array',minItems=1,items=READING_LINK)))
MAPPING = _object(dict(
    title=TEXT, intro=TEXT, shortcut=TEXT, relation=TEXT,
    steps=dict(type='array', minItems=5, maxItems=5, items=TITLE_TEXT),
    example=_object(dict(
        title=TEXT, capability_label=TEXT, function_label=TEXT, feature_label=TEXT,
        code_label=TEXT, boundary_label=TEXT,
        capability_ref=TEXT, function_ref=TEXT, component_source=TEXT, component_ref=TEXT,
        references=dict(type='array', minItems=1, items=_object(dict(
            title=TEXT, source=TEXT, repository=dict(type='string',pattern=r'^https://github[.]com/[^/]+/[^/]+$'),
            file_refs=dict(type='array',minItems=1,uniqueItems=True,items=TEXT)))))),
    estimation=TITLE_TEXT, roles=_object(dict(title=TEXT,text=TEXT,href=TEXT,label=TEXT)), appendix=READING_LINK, return_label=TEXT,
))
MAKE_AUDIT['properties']['mapping'] = MAPPING

SCHEMA['properties']['journey'] = _object(dict(title=TEXT,
    options=dict(type='array', minItems=3, maxItems=3, items=_object(dict(id=TEXT,label=TEXT,short_label=TEXT,status=TEXT))),
    pending=TEXT, flow=ARRAY_TEXT, consolidation=TITLE_TEXT, method_groups=dict(type='array',minItems=1,items=_object(dict(id=TEXT,title=TEXT))), labels=_object({key:TEXT for key in ('common','inputs','treatment','output','limits','compare','option','next','references','steps','future','state','example','phase','phases','secondary','formula','variables','implementation','audit')}),
    phases=dict(type='array',minItems=3,maxItems=3,items=_object(dict(id=TEXT,title=TEXT,short_title=TEXT,intro=TEXT,make=TEXT,buy=TEXT,make_audit=MAKE_AUDIT,
        providers=dict(type='array',minItems=3,maxItems=3,items=PROVIDER)))),
    scenario=_object(dict(intro=TEXT,example=TITLE_TEXT,primary=READING_LINK,steps=dict(type='array',minItems=1,items=TITLE_TEXT),future=TEXT,
        links=dict(type='array',minItems=1,items=READING_LINK))),
    methods=dict(type='array',minItems=1,items=_object(dict(href=TEXT,label=TEXT,text=TEXT,group=TEXT)))))
SCHEMA['required'].append('journey')



def _mapping_example(spec):
    from capability_catalog import catalog
    def evidence(path):
        target=(ROOT/path).resolve()
        if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
            raise ValueError(f'{ERROR}:mapping:unknown evidence:{path}')
        return read(target)
    try:
        capability=next(row for row in catalog()['rows'] if row['id']==spec['capability_ref'])
        function=next(row for row in capability['fonctions'] if row['id']==spec['function_ref'])
        component=next(row for row in evidence(spec['component_source'])['components'] if row['id']==spec['component_ref'])
        if capability['id'] not in component['capabilities']:
            raise ValueError(f'{ERROR}:mapping:component does not cover capability')
        references=[]
        for reference in spec['references']:
            perimeter=evidence(reference['source'])
            files=next(row for row in perimeter['components'] if row['component']==component['id'])['files']
            if not set(reference['file_refs'])<=set(files):
                raise ValueError(f'{ERROR}:mapping:file outside component')
            references.append(dict(title=reference['title'],revision=perimeter['source_revision'],
                files=[dict(path=path,url=reference['repository']+'/blob/'+perimeter['source_revision']+'/'+path)
                       for path in reference['file_refs']]))
    except (KeyError,StopIteration) as error:
        raise ValueError(f'{ERROR}:mapping:unresolved capability, function or component') from error
    return dict(capability=dict(id=capability['id'],native_id=capability['capacite_id'],
                                label=capability['capacite']['nom'],definition=capability['capacite']['definition']),
                function=deepcopy(function),feature=dict(id=component['id'],label=component['label'],
                   outcome=component['common_outcome'],boundary=component['common_boundary']),references=references)


def compile_vision(document, glossary, routes, documents):
    """Keep one editable text owner and reject unresolvable reading links."""
    errors = sorted(Draft202012Validator(SCHEMA).iter_errors(document), key=lambda e: str(e.path))
    if errors:
        error = errors[0]
        raise ValueError(f'{ERROR}:{SOURCE}:{list(error.path)}:{error.message}')

    if [step['id'] for step in document['approach']['steps']] != ['besoin','acquisition','integration','fonctionnement','delivery','valorisation','comparaison']:
        raise ValueError(f'{ERROR}:{SOURCE}:approach.steps:expected complete evaluation reading order')

    if [row['id'] for row in document['approach']['matrix']['rows']] != ['acquisition', 'integration', 'fonctionnement']:
        raise ValueError(f'{ERROR}:{SOURCE}:approach.matrix:expected acquisition, integration and operation reading order')

    if [level['id'] for level in document['confidence']['levels']] != ['method', 'application', 'review', 'delivery']:
        raise ValueError(f'{ERROR}:{SOURCE}:confidence.levels:expected method, application, review and delivery order')

    for rows, key, location in ((document['approach']['steps'], 'id', 'approach.steps'),
                                (document['evidence']['items'], 'id', 'evidence.items'),
                                (document['evidence']['items'], 'href', 'evidence.items'),
                                (document['confidence']['links'], 'href', 'confidence.links'),
                                (document['next']['links'], 'href', 'next.links')):
        values = [row[key] for row in rows]
        if len(values) != len(set(values)):
            raise ValueError(f'{ERROR}:{SOURCE}:{location}:duplicate {key}')

    allowed = {'#' + route for route in routes} | {
        path for path in documents if path.startswith(('source/', 'sources/'))}
    if 'synvance' in routes:
        allowed.update('#synvance-'+key for key in ('microsoft','sap','costs','business','oms'))
    if 'complexite' in routes:
        allowed.update(('#complexite?focus=formules','#complexite?focus=roles'))
    if 'modele' in routes:
        allowed.add('#modele?section=scope')
    for link in [document['adaptation'], document['adaptation']['reference_link'], *document['evidence']['items'],
                 *document['confidence']['levels'], *document['confidence']['links'], *document['next']['links']]:
        if link['href'] not in allowed:
            raise ValueError(f'{ERROR}:{SOURCE}:unknown reading link:{link["href"]}')

    journey = document['journey']
    if [row['id'] for row in journey['options']] != ['java-spring','microsoft','sap']:
        raise ValueError(f'{ERROR}:journey:unknown or repeated option')
    if [row['id'] for row in journey['phases']] != ['acquisition','integration','fonctionnement']:
        raise ValueError(f'{ERROR}:journey:invalid phase order')
    for phase in journey['phases']:
        if [p['option_ref'] for p in phase['providers']] != ['java-spring','microsoft','sap']:
            raise ValueError(f'{ERROR}:journey:unknown or repeated phase option')
    stack = read(ROOT / 'source/stacks/java-spring.yaml')
    element_ids = {element['id'] for element in stack['elements']}
    for phase in journey['phases']:
        for provider in phase['providers']:
            reading = provider.get('stack_reading')
            if reading:
                refs = [ref for group in reading['groups'] for ref in group['element_refs']]
                if phase['id'] != 'acquisition' or provider['option_ref'] != 'java-spring' or len(refs) != len(set(refs)) or not set(refs) <= element_ids:
                    raise ValueError(f'{ERROR}:journey:invalid stack reading references')
    groups=[g['id'] for g in journey['method_groups']]
    if len(groups)!=len(set(groups)) or any(m['group'] not in groups for m in journey['methods']):
        raise ValueError(f'{ERROR}:journey:invalid method group')
    rules={rule['id'] for rule in read(ROOT/'source/fondamentaux.yaml')['estimation_model']['rules']}
    methods={'core_method':'source/methode-evaluation-core.yaml','net_method':'source/methode-calcul-net.yaml','run_method':'source/methode-calcul-run.yaml'}
    for phase in journey['phases']:
        audit=phase['make_audit']
        if any(ref not in rules for step in audit['steps'] for ref in step['rule_refs']):
            raise ValueError(f'{ERROR}:journey:unknown canonical rule')
        sections={section['id']:section for section in read(ROOT/methods[audit['method']])['sections']}
        for ref in audit['sections']:
            if ref not in sections or not any(b['kind']=='formula' for b in sections[ref]['blocks']):
                raise ValueError(f'{ERROR}:journey:unknown formula section')
    def check_links(value):
        if isinstance(value,dict):
            if 'href' in value and value['href'] not in allowed:
                raise ValueError(f"{ERROR}:unknown reading link:{value['href']}")
            for child in value.values():check_links(child)
        elif isinstance(value,list):
            for child in value:check_links(child)
    for phase in journey['phases']:
        if 'mapping' in phase['make_audit']:
            if phase['id']!='acquisition':
                raise ValueError(f'{ERROR}:mapping:expected acquisition phase')
            _mapping_example(phase['make_audit']['mapping']['example'])
    check_links(document['approach'])
    for step in document['approach']['steps']:
        hrefs=[link['href'] for link in step['links']]
        if len(hrefs)!=len(set(hrefs)):
            raise ValueError(f'{ERROR}:approach.steps:duplicate reading link')
    check_links(journey)

    try:
        validate_glossary_literals(document, glossary, path=SOURCE)
        resolve_text_tree(document, glossary, path=SOURCE)
    except ValueError as error:
        raise ValueError(f'{ERROR}:{error}') from error
    return deepcopy(document)


def hydrate_framework_vision(ui, glossary):
    """Place the validated overview in the already frozen UI payload."""
    essential = ui['essential']
    if essential.get('framework_vision') != {'source': SOURCE}:
        raise ValueError(f'{ERROR}:config/application.yaml:expected canonical source')
    routes = {item['id'] for item in essential['nav']} & set(essential['pages'])
    documents = read(ROOT / 'config/publication.yaml')['documents']
    document = compile_vision(read(ROOT / SOURCE), glossary, routes, documents)
    mapping=document['journey']['phases'][0]['make_audit'].get('mapping')
    if mapping:
        mapping['example']['resolved']=_mapping_example(mapping['example'])
    elements = {element['id']: element for element in read(ROOT / 'source/stacks/java-spring.yaml')['elements']}
    for provider in document['journey']['phases'][0]['providers']:
        if 'stack_reading' in provider:
            for group in provider['stack_reading']['groups']:
                group['elements'] = [dict(id=ref, name=elements[ref]['nom'], description=elements[ref]['description'])
                                     for ref in group['element_refs']]
    value = deepcopy(ui)
    value['essential']['framework_vision'] = document
    return value
