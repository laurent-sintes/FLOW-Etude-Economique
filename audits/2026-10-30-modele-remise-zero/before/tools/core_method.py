"""Compile shared method documents, never the economic evaluation itself."""
from copy import deepcopy
import math

from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read
from evaluation_status import status_notice

METHOD_SOURCE = 'source/methode-evaluation-core.yaml'
MARKET_METHOD_SOURCE = 'source/methode-evaluation-marche.yaml'
NET_METHOD_SOURCE = 'source/methode-calcul-net.yaml'
RUN_METHOD_SOURCE = 'source/methode-calcul-run.yaml'
LEVERS_METHOD_SOURCE = 'source/leviers-calcul.yaml'


def _object(properties, required=None):
    return dict(type='object', properties=properties,
                required=list(properties) if required is None else required,
                additionalProperties=False)


TEXT = dict(type='string', minLength=1)
IDENTIFIER = dict(type='string', pattern='^[a-z][a-z0-9-]*$')
TEXTS = dict(type='array', items=TEXT, minItems=1)
TITLE_TEXT = _object(dict(title=TEXT, text=TEXT))
READING_ROUTES = ['#vision', '#modele', '#marche', '#complexite', '#calcul-net', '#calcul-run',
                  '#leviers', '#etude-marche', '#parametres', '#evaluation-core', '#comparer', '#se-projeter', '#simuler']
BLOCK = dict(oneOf=[
    _object(dict(kind=dict(enum=['paragraphs', 'bullets']), items=TEXTS)),
    _object(dict(kind=dict(const='table'), caption=TEXT, columns=TEXTS,
                 rows=dict(type='array', minItems=1, items=TEXTS))),
    _object(dict(kind=dict(const='callout'), title=TEXT, text=TEXT)),
    _object(dict(kind=dict(const='formula'), text=TEXT)),
    _object(dict(kind=dict(const='links'), items=dict(type='array', minItems=1,
                 items=_object(dict(href=dict(enum=READING_ROUTES), label=TEXT))))),
    _object(dict(kind=dict(const='example'), ref=IDENTIFIER)),
])
SCHEMA = _object(dict(
    schema_version=dict(const=1), id=dict(const='core-evaluation-opportunity'),
    principle=TITLE_TEXT, notice=TITLE_TEXT, navigation_label=TEXT,
    sections=dict(type='array', minItems=1, items=_object(dict(
        id=IDENTIFIER, title=TEXT, lead=TEXT,
        blocks=dict(type='array', minItems=1, items=BLOCK)))),
    examples=dict(type='array', items=_object(dict(
        id=IDENTIFIER, title=TEXT, note=TEXT,
        columns=dict(type='array', minItems=3, maxItems=3, items=TEXT),
        rows=dict(type='array', minItems=1, items=_object(dict(
            id=IDENTIFIER, label=TEXT, basis=TEXT,
            quantity=dict(type='number', exclusiveMinimum=0),
            unit_jh=dict(type='number', minimum=0)))),
        total_label=TEXT, unit=TEXT,
        uncertainty=_object(dict(down_pct=dict(type='number', minimum=0, maximum=100),
                                 up_pct=dict(type='number', minimum=0),
                                 label=TEXT, explanation=TEXT))))),
    next=_object(dict(href=dict(enum=['#marche', '#evaluation-core', '#calcul-net']), label=TEXT)),
))
SCHEMA['properties']['tooling'] = _object(dict(
    label=TEXT, title=TEXT, skill=TEXT, text=TEXT, items=TEXTS, note=TEXT),
    required=['label','title','skill','text'])
SECTION_SCHEMA=SCHEMA['properties']['sections']['items']
SECTION_SCHEMA['properties'].update(kind=dict(enum=['method','example']),eyebrow=TEXT)


def _compile_document(document, schema, source, error_code):
    """Validate teaching content and derive only explicitly fictional examples."""
    document = deepcopy(document)
    if isinstance(document.get('notice'), dict) and set(document['notice']) == {'status_ref'}:
        document['notice'] = status_notice(document['notice']['status_ref'])
    errors=sorted(Draft202012Validator(schema).iter_errors(document), key=lambda e:str(e.path))
    if errors:
        error=errors[0]
        raise ValueError(f'{error_code}:{source}:{list(error.path)}:{error.message}')
    value=deepcopy(document)

    def unique(rows, location):
        identifiers=[row['id'] for row in rows]
        if len(identifiers)!=len(set(identifiers)):
            raise ValueError(f'{error_code}:{source}:{location}:duplicate id')

    unique(value['sections'], 'sections')
    unique(value['examples'], 'examples')
    references=set()
    for section in value['sections']:
        if section.get('kind')=='example' and not section.get('eyebrow'):
            raise ValueError(f'{error_code}:{source}:{section["id"]}:example requires an explicit label')
        if source==METHOD_SOURCE and any(block['kind']=='example' for block in section['blocks']) and section.get('kind')!='example':
            raise ValueError(f'{error_code}:{source}:{section["id"]}:illustration must be separate from method steps')
        for block in section['blocks']:
            if block['kind']=='links':
                hrefs=[item['href'] for item in block['items']]
                if len(hrefs)!=len(set(hrefs)):
                    raise ValueError(f"{error_code}:{source}:{section['id']}:duplicate reading link")
            if block['kind']=='table' and any(len(row)!=len(block['columns']) for row in block['rows']):
                raise ValueError(f"{error_code}:{source}:{section['id']}:table width")
            if block['kind']=='example':
                references.add(block['ref'])
    if references!={example['id'] for example in value['examples']}:
        raise ValueError(f'{error_code}:{source}:examples:unresolved or unused reference')
    for example in value['examples']:
        unique(example['rows'], example['id'])
        uncertainty=example['uncertainty']
        numbers=[number for row in example['rows'] for number in (row['quantity'],row['unit_jh'])]+[uncertainty['down_pct'],uncertainty['up_pct']]
        if not all(math.isfinite(number) for number in numbers):
            raise ValueError(f"{error_code}:{source}:{example['id']}:non-finite number")
        for row in example['rows']:
            row['jh']=round(row['quantity']*row['unit_jh'],2)
        total=round(sum(row['jh'] for row in example['rows']),2)
        example['total_jh']=total
        uncertainty['lower_jh']=round(total*(1-uncertainty['down_pct']/100),2)
        uncertainty['upper_jh']=round(total*(1+uncertainty['up_pct']/100),2)
    return value


def compile_method(document):
    return _compile_document(document, SCHEMA, METHOD_SOURCE, 'ERR_CORE_METHOD')


def compile_market_method(document):
    schema=deepcopy(SCHEMA)
    schema['properties']['id']={'const':'market-evaluation-opportunity'}
    schema['properties']['next']['properties']['href']={'const':'#complexite'}
    schema['properties']['examples']={'type':'array','maxItems':0}
    return _compile_document(document, schema, MARKET_METHOD_SOURCE, 'ERR_MARKET_METHOD')


def compile_net_method(document):
    schema=deepcopy(SCHEMA)
    schema['properties']['id']={'const':'net-calculation'}
    schema['properties']['next']['properties']['href']={'const':'#calcul-run'}
    schema['properties']['examples']={'type':'array','maxItems':0}
    return _compile_document(document, schema, NET_METHOD_SOURCE, 'ERR_NET_METHOD')


def compile_run_method(document):
    schema=deepcopy(SCHEMA)
    schema['properties']['id']={'const':'run-calculation'}
    schema['properties']['next']['properties']['href']={'const':'#leviers'}
    schema['properties']['examples']={'type':'array','maxItems':0}
    return _compile_document(document, schema, RUN_METHOD_SOURCE, 'ERR_RUN_METHOD')


def compile_levers_method(document):
    schema=deepcopy(SCHEMA)
    schema['properties']['id']={'const':'levers-calculation'}
    schema['properties']['next']['properties']['href']={'const':'#etude-marche'}
    schema['properties']['examples']={'type':'array','maxItems':0}
    return _compile_document(document, schema, LEVERS_METHOD_SOURCE, 'ERR_LEVERS_METHOD')


def hydrate_levers_method(ui):
    if ui['essential'].get('levers_method')!={'source':LEVERS_METHOD_SOURCE}:
        raise ValueError('ERR_LEVERS_METHOD:config/application.yaml:expected canonical source')
    value=deepcopy(ui)
    value['essential']['levers_method']=compile_levers_method(read(ROOT/LEVERS_METHOD_SOURCE))
    return value


def hydrate_net_method(ui):
    if ui['essential'].get('net_method')!={'source':NET_METHOD_SOURCE}:
        raise ValueError('ERR_NET_METHOD:config/application.yaml:expected canonical source')
    value=deepcopy(ui)
    value['essential']['net_method']=compile_net_method(read(ROOT/NET_METHOD_SOURCE))
    return value


def hydrate_run_method(ui):
    if ui['essential'].get('run_method')!={'source':RUN_METHOD_SOURCE}:
        raise ValueError('ERR_RUN_METHOD:config/application.yaml:expected canonical source')
    value=deepcopy(ui)
    value['essential']['run_method']=compile_run_method(read(ROOT/RUN_METHOD_SOURCE))
    return value


def hydrate_core_method(ui):
    """Resolve the single method owner inside the existing frozen UI contract."""
    reference=ui['essential']['core_method']
    if reference!={'source':METHOD_SOURCE}:
        raise ValueError('ERR_CORE_METHOD:config/application.yaml:expected canonical source')
    value=deepcopy(ui)
    value['essential']['core_method']=compile_method(read(ROOT/METHOD_SOURCE))
    return value


def hydrate_market_method(ui):
    reference=ui['essential']['market_method']
    if set(reference)!={'source','application'} or reference['source']!=MARKET_METHOD_SOURCE:
        raise ValueError('ERR_MARKET_METHOD:config/application.yaml:expected canonical source and application link')
    link_schema=_object(dict(href=dict(const='#etude-marche'),label=TEXT))
    if not Draft202012Validator(link_schema).is_valid(reference['application']):
        raise ValueError('ERR_MARKET_METHOD:config/application.yaml:invalid application link')
    value=deepcopy(ui)
    value['essential']['market_method']={'application':deepcopy(reference['application'])}
    value['essential']['market_method']['document']=compile_market_method(read(ROOT/MARKET_METHOD_SOURCE))
    return value
