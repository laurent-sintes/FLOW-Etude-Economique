"""Current application notes, separate from reusable methods and economic inputs."""
from copy import deepcopy

from jsonschema import Draft202012Validator

from content_model import resolve_text_tree, validate_glossary_literals
from evaluation_status import load_status
from validate_stacks import ROOT, read

SOURCE = 'source/application-framework.yaml'
ERROR = 'ERR_FRAMEWORK_APPLICATION'
TEXT = {'type': 'string', 'minLength': 1, 'pattern': r'\S'}
SECTION_IDS = {
    'economic': {'scope', 'calendar', 'maturity'},
    'hypotheses': {'productivity', 'coordination', 'annual_means', 'annual_expertise', 'offer_sequences'},
    'market': {'evidence_status', 'cocomo'},
}


def obj(properties, required=None):
    return {'type': 'object', 'properties': properties,
            'required': list(properties) if required is None else required,
            'additionalProperties': False}


SECTION = obj({'id': {'type': 'string', 'pattern': '^[a-z][a-z0-9_-]*$'},
               'title': TEXT, 'paragraphs': {'type': 'array', 'minItems': 1, 'items': TEXT},
               'links': {'type': 'array', 'minItems': 1,
                         'items': obj({'href': TEXT, 'label': TEXT})}},
              ['id', 'title', 'paragraphs'])
SECTIONS = {'type': 'array', 'minItems': 1, 'items': SECTION}
SCHEMA = obj({'version': {'const': 1}, 'id': {'const': 'framework-application'},
              'economic': obj({'status_ref': {'const': 'core'}, 'sections': SECTIONS}),
              'hypotheses': obj({'sections': SECTIONS}), 'market': obj({'sections': SECTIONS})})


def compile_application(document, glossary, routes, documents):
    errors = sorted(Draft202012Validator(SCHEMA).iter_errors(document), key=lambda error: str(error.path))
    if errors:
        error = errors[0]
        raise ValueError(f'{ERROR}:{list(error.path)}:{error.message}')
    allowed = {'#' + route for route in routes} | set(documents)
    for group in ('economic', 'hypotheses', 'market'):
        sections = document[group]['sections']
        ids = [section['id'] for section in sections]
        if len(ids) != len(set(ids)):
            raise ValueError(f'{ERROR}:{group}:duplicate section')
        if set(ids) != SECTION_IDS[group]:
            raise ValueError(f'{ERROR}:{group}:missing or unknown application section')
        for section in sections:
            hrefs = [link['href'] for link in section.get('links', [])]
            if len(hrefs) != len(set(hrefs)) or any(href not in allowed for href in hrefs):
                raise ValueError(f'{ERROR}:{group}/{section["id"]}:invalid reading link')
    validate_glossary_literals(document, glossary, path=SOURCE)
    resolve_text_tree(document, glossary, path=SOURCE)
    result = deepcopy(document)
    status = load_status(document['economic']['status_ref'])
    if status['active_source'] not in documents:
        raise ValueError(f'{ERROR}:undeclared active provenance')
    result['economic']['status'] = {key: status[key] for key in ('title', 'summary', 'text')}
    result['economic']['status']['source'] = status['active_source']
    return result


def hydrate_application_framework(ui):
    if ui['essential'].get('application_framework') != {'source': SOURCE}:
        raise ValueError(f'{ERROR}:expected canonical application source')
    essential = ui['essential']
    routes = {item['id'] for item in essential['nav']} & set(essential['pages'])
    value = compile_application(read(ROOT / SOURCE), read(ROOT / 'source/glossaire.yaml'),
                                routes, read(ROOT / 'config/publication.yaml')['documents'])
    result = deepcopy(ui)
    result['essential']['application_framework'] = value
    return result
