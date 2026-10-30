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
    adaptation=_object(dict(title=TEXT, text=TEXT, href=dict(const='#leviers'), label=TEXT)),
    approach=_object(dict(title=TEXT, steps=dict(type='array', minItems=1,
        items=_object(dict(id=IDENTIFIER, title=TEXT, text=TEXT))),
        matrix=_object(dict(caption=TEXT, activity_label=TEXT, make_label=TEXT, buy_label=TEXT,
            rows=dict(type='array', minItems=2, maxItems=2, items=MATRIX_ROW), notes=PARAGRAPHS)))),
    evidence=_object(dict(title=TEXT, items=dict(type='array', minItems=1,
        items=_object(dict(id=IDENTIFIER, title=TEXT, text=TEXT, href=TEXT, label=TEXT))))),
    dimensions=_object(dict(title=TEXT, items=dict(type='array', minItems=1, items=TITLE_TEXT))),
    confidence=_object(dict(title=TEXT, text=TEXT,
        levels=dict(type='array', minItems=4, maxItems=4, items=PROOF_LEVEL),
        links=dict(type='array', minItems=1, items=READING_LINK), limits_title=TEXT,
        limits=dict(type='array', minItems=1, items=TEXT))),
    next=_object(dict(title=TEXT, links=dict(type='array', minItems=3, maxItems=3, items=READING_LINK))),
))


def compile_vision(document, glossary, routes, documents):
    """Keep one editable text owner and reject unresolvable reading links."""
    errors = sorted(Draft202012Validator(SCHEMA).iter_errors(document), key=lambda e: str(e.path))
    if errors:
        error = errors[0]
        raise ValueError(f'{ERROR}:{SOURCE}:{list(error.path)}:{error.message}')

    if [step['id'] for step in document['approach']['steps']] != ['besoin', 'investissement']:
        raise ValueError(f'{ERROR}:{SOURCE}:approach.steps:expected need and investment reading order')

    if [row['id'] for row in document['approach']['matrix']['rows']] != ['build', 'run']:
        raise ValueError(f'{ERROR}:{SOURCE}:approach.matrix:expected Build and Run reading order')

    if [level['id'] for level in document['confidence']['levels']] != ['method', 'application', 'review', 'delivery']:
        raise ValueError(f'{ERROR}:{SOURCE}:confidence.levels:expected method, application, review and delivery order')

    for rows, key, location in ((document['approach']['steps'], 'id', 'approach.steps'),
                                (document['evidence']['items'], 'id', 'evidence.items'),
                                (document['evidence']['items'], 'href', 'evidence.items'),
                                (document['dimensions']['items'], 'title', 'dimensions.items'),
                                (document['confidence']['links'], 'href', 'confidence.links'),
                                (document['next']['links'], 'href', 'next.links')):
        values = [row[key] for row in rows]
        if len(values) != len(set(values)):
            raise ValueError(f'{ERROR}:{SOURCE}:{location}:duplicate {key}')

    allowed = {'#' + route for route in routes} | {
        path for path in documents if path.startswith(('source/', 'sources/'))}
    for link in [document['adaptation'], *document['evidence']['items'],
                 *document['confidence']['levels'], *document['confidence']['links'], *document['next']['links']]:
        if link['href'] not in allowed:
            raise ValueError(f'{ERROR}:{SOURCE}:unknown reading link:{link["href"]}')

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
    value = deepcopy(ui)
    value['essential']['framework_vision'] = document
    return value
