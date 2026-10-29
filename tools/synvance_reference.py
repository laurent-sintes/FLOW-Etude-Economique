"""Read the Synvance input dossier without creating or changing a FLOW budget."""
from copy import deepcopy
from decimal import Decimal
import math
from pathlib import PurePosixPath

from jsonschema import Draft202012Validator
from content_model import resolve_text_tree, validate_glossary_literals
from validate_stacks import ROOT, read

SOURCE = 'source/reperes-synvance.yaml'
ERROR = 'ERR_SYNVANCE_REFERENCE'
PROVIDERS = ('microsoft', 'sap')


def _object(properties):
    return dict(type='object', properties=properties, required=list(properties), additionalProperties=False)


def _array(items, minimum=1):
    return dict(type='array', minItems=minimum, items=items)


TEXT = dict(type='string', minLength=1, pattern=r'\S')
ID = dict(type='string', pattern='^[a-z][a-z0-9-]*$')
PROOFS = dict(type='array', minItems=1, uniqueItems=True, items=TEXT)
SCHEMA = _object(dict(
    version=dict(const=1), id=dict(const='reperes-synvance'), title=TEXT, navigation=TEXT, introduction=TEXT,
    labels=_object({key: TEXT for key in ('amount', 'period', 'status', 'scope', 'source', 'year',
        'annual_amount', 'price_year', 'open', 'download_pdf', 'download_xlsx',
        'back_to_overview', 'provider_navigation', 'overview_link', 'reading_note', 'provider_note')}),
    overview=_object(dict(title=TEXT, introduction=TEXT, warning=TEXT,
        inputs=_array(_object(dict(piece_ref=TEXT, label=TEXT, text=TEXT))),
        proposals_title=TEXT, proposals_introduction=TEXT, cards=_array(_object(dict(
        id=dict(enum=list(PROVIDERS)), title=TEXT, description=TEXT,
        highlights=_array(_object(dict(row_ref=ID, label=TEXT))), note=TEXT, link_label=TEXT))))),
    passages=_array(_object(dict(id=ID, piece_ref=TEXT, page=dict(type=['integer', 'null'], minimum=1), location=TEXT))),
    synthesis=_object(dict(title=TEXT, introduction=TEXT, integration_title=TEXT, integration_note=TEXT,
        annual_title=TEXT, annual_note=TEXT, providers=_array(_object(dict(
            id=dict(enum=list(PROVIDERS)), title=TEXT,
            context=_object(dict(title=TEXT, lead=TEXT, items=_array(TEXT))),
            integration=_object(dict(intro=TEXT, rows=_array(_object(dict(id=ID, label=TEXT,
                binding=dict(enum=['post:0', 'post:1', 'post:2', 'sum', 'printed', 'difference']),
                period=TEXT, status=TEXT, scope=TEXT, proof_refs=PROOFS))))),
            annual=_object(dict(intro=TEXT, rows=_array(_object(dict(id=ID, label=TEXT,
                post_ref=TEXT, period=TEXT, scope=TEXT, proof_refs=PROOFS)))))
        ))))),
    documents=_object(dict(title=TEXT, introduction=TEXT)),
    usage=_object(dict(title=TEXT, introduction=TEXT, paragraphs=_array(TEXT), links=_array(_object(dict(
        href=dict(enum=['#vision', '#marche', '#etude-marche', '#evaluation-core']), label=TEXT, text=TEXT)))))
))


def require(condition, message):
    if not condition:
        raise ValueError(ERROR + ':' + message)


def number(value, path):
    require(isinstance(value, (int, float)) and not isinstance(value, bool)
        and math.isfinite(value) and value >= 0, 'invalid source number:' + path)
    return value


def index(rows, path):
    values = {row['id']: row for row in rows}
    require(len(values) == len(rows), 'duplicate id:' + path)
    return values


def compile_synvance_reference(editorial, guide, prices, annual, glossary, document_path):
    """Project only recorded offer amounts, keeping originals and source periods distinct."""
    errors = sorted(Draft202012Validator(SCHEMA).iter_errors(editorial), key=lambda e: str(e.path))
    if errors:
        raise ValueError(ERROR + ':editorial:' + str(list(errors[0].path)) + ':' + errors[0].message)
    require([row['id'] for row in editorial['synthesis']['providers']] == list(PROVIDERS), 'provider order')
    require(set(prices) == set(annual) == set(PROVIDERS), 'source providers')
    validate_glossary_literals(editorial, glossary, path=SOURCE)
    result = resolve_text_tree(deepcopy(editorial), glossary, path=SOURCE)
    pieces = index(guide['pieces'], 'pieces')
    require(set(pieces) == {'demande', 'besoins', 'microsoft', 'sap', 'copil',
        'questionnaire_microsoft', 'questionnaire_sap'}, 'original document coverage')
    documents = []
    for item in pieces.values():
        document_path(item['path'])
        path = item['path'].split('#')[0]
        suffix = PurePosixPath(path).suffix.lower()
        require(suffix in ('.pdf', '.xlsx'), 'original document format:' + path)
        documents.append(dict(id=item['id'], title=item['titre'], author=item['auteur'], path=item['path'],
            location=item['localisation'], scope=item['objet'], format=suffix[1:]))
    result['documents']['items'] = documents
    input_refs = [row['piece_ref'] for row in result['overview']['inputs']]
    require(len(input_refs) == len(set(input_refs)) and set(input_refs) == {
        'demande', 'besoins', 'questionnaire_microsoft', 'questionnaire_sap'}, 'input evidence coverage')
    for row in result['overview']['inputs']:
        row['path'] = pieces[row.pop('piece_ref')]['path']

    passages = index(result.pop('passages'), 'passages')
    for key, passage in passages.items():
        require(passage['piece_ref'] in pieces, 'unknown source piece:' + key)
        piece = pieces[passage['piece_ref']]
        path = piece['path'].split('#')[0]
        is_pdf = PurePosixPath(path).suffix.lower() == '.pdf'
        require((passage['page'] is not None) == is_pdf, 'page must name a PDF passage:' + key)
        passage['path'] = path + ('#page=' + str(passage['page']) if is_pdf else '')
        document_path(passage['path'])

    def proofs(refs):
        require(set(refs) <= set(passages), 'unknown proof')
        return [dict(path=passages[key]['path'], label=pieces[passages[key]['piece_ref']]['titre'],
            location=passages[key]['location']) for key in refs]

    for provider in result['synthesis']['providers']:
        slug = provider['id']
        initial = prices[slug]
        amounts = initial['postes_eur']
        require(len(amounts) == (2 if slug == 'microsoft' else 3), 'source lot count:' + slug)
        for position, value in enumerate(amounts):
            number(value, slug + '/initial/' + str(position))
        printed = number(initial['total_imprime_eur'], slug + '/initial/printed')
        total = float(sum((Decimal(str(value)) for value in amounts), Decimal(0)))
        rows = provider['integration']['rows']
        index(rows, slug + '/integration')
        for row in rows:
            binding = row.pop('binding')
            row['reading_role'] = 'detail' if binding.startswith('post:') else {
                'sum': 'sum', 'printed': 'published', 'difference': 'difference'}[binding]
            if binding.startswith('post:'):
                position = int(binding.split(':')[1])
                require(position < len(amounts), 'unknown lot:' + slug)
                value = amounts[position]
            elif binding == 'sum':
                value = total
            elif binding == 'printed':
                value = printed
            else:
                # A documentary difference, never a new cost or a correction of the original.
                value = float(Decimal(str(printed)) - Decimal(str(total)))
            row['amount_eur'] = value
            row['proofs'] = proofs(row.pop('proof_refs'))
        posts = index(annual[slug]['postes'], slug + '/annual')
        rows = provider['annual']['rows']
        index(rows, slug + '/annual editorial')
        expected_posts = ({'MAI-010/licences', 'MAI-013/outillage-support'} if slug == 'microsoft'
            else {'MAI-010/licences', 'rfi-mco', 'rfi-monitoring', 'rfi-evolutions'})
        require({row['post_ref'] for row in rows} == expected_posts and len(rows) == len(expected_posts),
            'documented annual post coverage:' + slug)
        for row in rows:
            key = row.pop('post_ref')
            require(key in posts, 'unknown annual post:' + key)
            post = posts[key]
            require(post['methode'] in ('prix_documentes', 'prix_reference_indexe'),
                'annual row is not a documented price:' + key)
            year = post['annee_prix']
            require(isinstance(year, int) and not isinstance(year, bool), 'source price year:' + key)
            sequence = post['montants_documentes_eur_ht']
            require(bool(sequence), 'missing annual price:' + key)
            years = [entry['annee'] for entry in sequence]
            require(all(isinstance(y, int) and not isinstance(y, bool) and y > 0 for y in years)
                and years == sorted(set(years)), 'source year sequence:' + key)
            row['source_year'] = year
            row['amounts'] = [dict(year=entry['annee'], amount_eur=number(entry['montant'], slug + '/' + key))
                for entry in sequence]
            row['proofs'] = proofs(row.pop('proof_refs'))
    cards = result['overview']['cards']
    require([card['id'] for card in cards] == list(PROVIDERS), 'overview provider order')
    providers = {row['id']: row for row in result['synthesis']['providers']}
    for card in cards:
        rows = {row['id']: row for row in providers[card['id']]['integration']['rows']}
        references = [highlight['row_ref'] for highlight in card['highlights']]
        require(len(references) == len(set(references)) and set(references) <= set(rows),
            'unknown or repeated overview row:' + card['id'])
        card['highlights'] = [dict(deepcopy(rows[item['row_ref']]), label=item['label'])
            for item in card['highlights']]
        card['href'] = '#synvance-' + card['id']
    return result


def build_synvance_reference(guide, glossary, document_path):
    prices = {slug: read(ROOT / f'source/chiffrage/chiffrage-{slug}.yaml')['integration']['prix_rfi']
              for slug in PROVIDERS}
    annual = {slug: read(ROOT / f'source/maintenance/maintenance-{slug}.yaml')['valorisation_annuelle']
              for slug in PROVIDERS}
    return compile_synvance_reference(read(ROOT / SOURCE), guide, prices, annual, glossary, document_path)
