"""Frozen reading of existing economic evaluations; no new budget calculation."""
from copy import deepcopy
from decimal import Decimal

from jsonschema import Draft202012Validator

from content_model import resolve_text_tree, validate_glossary_literals
from validate_stacks import ROOT, read


SOURCE = 'source/lecture-evaluations-economiques.yaml'
ERROR = 'ERR_ECONOMIC_READING'
ANNUAL_KEYS = ('services_mco', 'hebergement', 'ipaas', 'licences_complementaires', 'offre_editeur')


def _object(fields):
    return dict(type='object', properties=fields, required=list(fields), additionalProperties=False)


TEXT = dict(type='string', minLength=1, pattern=r'\S')
LINK = _object(dict(path=TEXT, label=TEXT))
LINKS = dict(type='array', minItems=1, items=LINK)
SECTION = dict(title=TEXT, lead=TEXT, caption=TEXT, note=TEXT, sources=LINKS)
SCHEMA = _object(dict(
    version=dict(const=1), id=dict(const='economic-evaluations'), navigation_label=TEXT,
    intro=_object(dict(title=TEXT, text=TEXT)),
    labels=_object({key:TEXT for key in ('option', 'budget', 'duration', 'months', 'source',
                                       'price_convention', 'annual_item', 'annual_total',
                                       'not_applicable', 'annual_sources')}),
    sections=_object(dict(
        selection=_object(SECTION),
        integration=_object(dict(**SECTION, explanations=_object({key:TEXT for key in ('Make', 'microsoft', 'sap')}))),
        annual=_object(dict(**SECTION, rows=dict(type='array', minItems=5, maxItems=5,
            items=_object(dict(id=dict(enum=list(ANNUAL_KEYS)), label=TEXT, explanation=TEXT))))),
        limits=_object(dict(title=TEXT, lead=TEXT)),
    )),
    links=dict(type='array', minItems=1, items=_object(dict(href=dict(enum=['#parametres', '#se-projeter', '#comparer']), label=TEXT))),
))


def _require(condition, reason):
    if not condition:
        raise ValueError(f'{ERROR}:{reason}')


def compile_economic_evaluations(baseline, content, editorial, glossary, document_path):
    """Project from one loaded reference, without reading sources or recalculating it."""
    errors = sorted(Draft202012Validator(SCHEMA).iter_errors(editorial), key=lambda error:str(error.path))
    if errors:
        error = errors[0]
        raise ValueError(f'{ERROR}:{list(error.path)}:{error.message}')
    _require([row['id'] for row in editorial['sections']['annual']['rows']] == list(ANNUAL_KEYS), 'annual row contract')
    _require(len({row['href'] for row in editorial['links']}) == len(editorial['links']), 'duplicate reading link')
    validate_glossary_literals(editorial, glossary, path=SOURCE)
    text = resolve_text_tree(editorial, glossary, path=SOURCE)
    for section in text['sections'].values():
        for link in section.get('sources', []):
            document_path(link['path'])

    options = []
    identifiers = [option['stack'] for option in baseline['options']]
    _require(len(identifiers) == len(set(identifiers)), 'duplicate option')
    _require(set(identifiers) == set(content['stacks']), 'inconsistent option coverage')
    for option in baseline['options']:
        slug, mode = option['stack'], option['mode']
        _require(mode in ('Make', 'Buy'), f'unknown mode:{slug}')
        integration_source = ('source/deploiement-groupe.yaml' if mode == 'Make'
                              else f'source/chiffrage/chiffrage-{slug}.yaml#/integration')
        annual_source = f'source/chiffrage/chiffrage-{slug}.yaml#/maintenance'
        document_path(integration_source)
        document_path(annual_source)
        selection = None
        if mode == 'Buy':
            selection = dict(budget_eur_ht=option['selection_buy'], months=option['selection_months'],
                             source='source/selection-buy.yaml')
            document_path(selection['source'])
        duration = (baseline['make_integration_months'] if mode == 'Make'
                    else baseline['parameters']['options'][slug]['integration_mois'])
        ledger = [line for line in option['funding_ledger'] if line['phase'] == 'integration']
        ledger_total = sum((Decimal(str(line['amount'])) for line in ledger), Decimal(0))
        _require(abs(ledger_total - Decimal(str(option['integration']))) < Decimal('0.005'), f'integration ownership:{slug}')

        prices = option['editor_prices']
        _require(bool(prices) == (mode == 'Buy'), f'editor price sequence:{slug}')
        annual_items = {key:deepcopy(option['annual_base'][key]) for key in ANNUAL_KEYS[:-1]}
        annual_items['offre_editeur'] = prices[0] if prices else None
        total = content['stacks'][slug]['economic_reading']['total']
        # Reconcile already calculated amounts; the published total remains the owner.
        parts_total = sum((Decimal(str(value)) for value in annual_items.values() if value is not None), Decimal(0))
        _require(abs(parts_total - Decimal(str(total))) < Decimal('0.005'), f'annual ownership:{slug}')
        options.append(dict(stack=slug, name=option['name'], mode=mode, selection=selection,
            integration=dict(budget_eur_ht=option['integration'], months=duration, source=integration_source),
            annual=dict(items=annual_items, total_eur_ht=total, source=annual_source,
                        service_allocation=deepcopy(option['services']))))

    price_source = 'source/calibration-couts.yaml#convention/prix'
    document_path(price_source)
    return dict(model_version=baseline['model_version'], editorial=text, options=options,
                price_convention=dict(text=content['calibration']['convention']['prix'], source=price_source))


def build_economic_evaluations(baseline, content, glossary, document_path):
    """Compile once during Study loading; endpoints serve the frozen result only."""
    document_path(SOURCE)
    return compile_economic_evaluations(baseline, content, read(ROOT / SOURCE), glossary, document_path)
