"""Read the Synvance input dossier without creating or changing a FLOW budget."""
from copy import deepcopy
from decimal import Decimal
from datetime import date
import math
from pathlib import PurePosixPath

from jsonschema import Draft202012Validator
from content_model import resolve_text_tree, validate_glossary_literals
from validate_stacks import ROOT, read

SOURCE = 'source/reperes-synvance.yaml'
ERROR = 'ERR_SYNVANCE_REFERENCE'
PROVIDERS = ('microsoft', 'sap')


def _object(properties, optional=()):
    return dict(type='object', properties=properties, required=[key for key in properties if key not in optional], additionalProperties=False)


def _array(items, minimum=1):
    return dict(type='array', minItems=minimum, items=items)


TEXT = dict(type='string', minLength=1, pattern=r'\S')
ISO_DATE = dict(type='string', pattern=r'^\d{4}-\d{2}-\d{2}$')
EDITORIAL_NOTE = _object(dict(title=TEXT, text=TEXT))
ID = dict(type='string', pattern='^[a-z][a-z0-9-]*$')
PROOFS = dict(type='array', minItems=1, uniqueItems=True, items=TEXT)
SOURCE_CELL = _object(dict(status=TEXT, scope=TEXT,
    entries=_array(_object(dict(row_ref=TEXT, label=TEXT)), 0),
    proof_refs=dict(type='array', uniqueItems=True, items=TEXT)))
PRODUCT_URLS = ['https://help.sap.com/docs/SAP_Order_Management_for_Sourcing_and_Availability/b1914f5958b54a148b2b7580550ef9a5/f06cbc74f4c34a9e8e3a74adb8d6d0b9.html', 'https://help.sap.com/doc/08442b9d2cd744f7aecc1e08080c26f3/SHIP/en-US/FSD_SAP_OMSA.pdf', 'https://learning.sap.com/courses/exploring-sap-order-management-foundation-and-sourcing-availability/explaining-the-concept-of-order-submit-and-order-orchestration', 'https://learn.microsoft.com/en-us/dynamics365/commerce/dom', 'https://learn.microsoft.com/en-us/dynamics365/commerce/dev-itpro/commerce-architecture', 'https://learn.microsoft.com/en-us/dynamics365/commerce/dom-processing', 'https://learn.microsoft.com/en-us/dynamics365/commerce/dom-limitations']
SCHEMA = _object(dict(
    version=dict(const=1), id=dict(const='reperes-synvance'), title=TEXT, navigation=TEXT, introduction=TEXT,
    reading=_object(dict(navigation=TEXT, pages=_array(_object(dict(id=dict(enum=['overview','business','oms','costs']),label=TEXT,short_label=TEXT,description=TEXT))),
        evidence_title=TEXT,evidence_intro=TEXT,piece_labels=_object({key:TEXT for key in ('demande','besoins','microsoft','sap','copil','questionnaire_microsoft','questionnaire_sap')}),
        publishers=_array(_object(dict(id=dict(enum=list(PROVIDERS)),name=TEXT,role=TEXT,asset=dict(enum=['assets/microsoft-original.svg','assets/sap-original.svg']),accent=dict(type='string',pattern='^#[0-9A-Fa-f]{6}$')))),
        details_title=TEXT,documents_link=TEXT,business_oms_link=TEXT,cost_navigation=TEXT,acquired_title=TEXT,acquired_text=TEXT,acquired_link=TEXT,architecture_status=TEXT)),
    labels=_object({key: TEXT for key in ('amount', 'period', 'status', 'scope', 'source', 'year',
        'annual_amount', 'price_year', 'open', 'download_pdf', 'download_xlsx',
        'back_to_overview', 'provider_navigation', 'overview_link', 'reading_note', 'provider_note')}),
    brief=_object(dict(title=TEXT, introduction=TEXT,finalists_label=TEXT,
        start=_object(dict(value=ISO_DATE,label=TEXT,proof_refs=PROOFS)),
        questions=_array(_object(dict(id=ID, question=TEXT, answer=TEXT, proof_refs=PROOFS,
            note=EDITORIAL_NOTE,publisher_refs=dict(type='array',minItems=1,uniqueItems=True,items=dict(enum=list(PROVIDERS)))),optional=('note','publisher_refs'))),
        actors=_object(dict(title=TEXT,items=_array(_object(dict(id=ID,name=TEXT,role=TEXT,text=TEXT,proof_refs=PROOFS,
            publisher_ref=dict(enum=list(PROVIDERS))),optional=('publisher_ref',))))),
        highlights=_object(dict(title=TEXT, items=_array(TEXT), proof_refs=PROOFS)))),
    business=_object(dict(title=TEXT, introduction=TEXT,
        architectures=_array(_object(dict(id=dict(enum=['backbone','suite']),title=TEXT, text=TEXT, systems=_array(TEXT)))), architecture_note=TEXT,
        architecture_proof_refs=PROOFS,
        pattern_reading=_object(dict(title=TEXT,note=TEXT,undetermined_label=TEXT,providers=_array(_object(dict(id=dict(enum=list(PROVIDERS)),pattern_ref=dict(type=['string','null']),summary=TEXT,scope=TEXT,proof_refs=PROOFS))))),
        oms=_object(dict(title=TEXT, introduction=TEXT, conclusion=TEXT, note=TEXT, proof_refs=PROOFS,open_points_title=TEXT,open_points=_array(TEXT),
            labels=_object({key:TEXT for key in ('criterion','microsoft','sap','decision')}),
            rows=_array(_object(dict(id=ID, criterion=TEXT, microsoft=TEXT, sap=TEXT, decision=TEXT, proof_refs=PROOFS))),
            product_sources=_array(_object(dict(label=TEXT, href=dict(enum=PRODUCT_URLS)))))),
        comparison_title=TEXT, comparison_note=TEXT,
        labels=_object({key: TEXT for key in ('topic', 'request', 'microsoft', 'sap')}),
        axes=_array(_object(dict(id=ID, topic=TEXT, request=TEXT, microsoft=TEXT, sap=TEXT, proof_refs=PROOFS))),
        others_title=TEXT, others_introduction=TEXT,
        others=_array(_object(dict(id=ID, title=TEXT, text=TEXT, proof_refs=PROOFS))))),
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
    costs=_object(dict(title=TEXT, introduction=TEXT,
        labels=_object({key:TEXT for key in ('structure', 'microsoft', 'sap', 'scope', 'year', 'price_year', 'amount', 'total', 'years', 'horizon', 'bundled', 'model_amount', 'source_amount', 'initial', 'annual', 'annual_total', 'selection', 'integration', 'integration_additions', 'service_start', 'month', 'source_detail', 'source_note', 'model_note')}),
        sources_title=TEXT, sources_note=TEXT,
        rows=_array(_object(dict(structure_ref=TEXT, model_scope=TEXT,
            model_display=dict(enum=['amount','bundled']), comparison=TEXT,
            microsoft=SOURCE_CELL, sap=SOURCE_CELL))),
        bridge_title=TEXT, bridge_note=TEXT,
        annual_rows=_array(_object(dict(id=TEXT, label=TEXT))),
        model_title=TEXT, model_note=TEXT, model_limit=TEXT,
        model_links=_array(_object(dict(href=dict(enum=['#parametres','#se-projeter','#comparer']), label=TEXT))))),
    documents=_object(dict(title=TEXT,date_note=TEXT, date_labels=_object({key:TEXT for key in ('document','file_modified','unknown')}))),
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


def compile_synvance_reference(editorial, guide, prices, annual, glossary, document_path,
                               architecture, baseline, economic_evaluations):
    """Project only recorded offer amounts, keeping originals and source periods distinct."""
    errors = sorted(Draft202012Validator(SCHEMA).iter_errors(editorial), key=lambda e: str(e.path))
    if errors:
        raise ValueError(ERROR + ':editorial:' + str(list(errors[0].path)) + ':' + errors[0].message)
    require([row['id'] for row in editorial['synthesis']['providers']] == list(PROVIDERS), 'provider order')
    require([item['id'] for item in editorial['reading']['pages']] == ['overview','business','oms','costs'], 'reading page order')
    require([item['id'] for item in editorial['reading']['publishers']] == list(PROVIDERS), 'publisher identity order')
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
        dated=item.get('date')
        require(isinstance(dated,dict) and set(dated)=={'value','nature','provenance'},'document date metadata:'+item['id'])
        require(dated['nature'] in ('document','file_modified','unknown') and isinstance(dated['provenance'],str) and dated['provenance'].strip(), 'document date provenance:'+item['id'])
        require((dated['value'] is None)==(dated['nature']=='unknown'),'document date nature:'+item['id'])
        if dated['value'] is not None:
            try:
                require(date.fromisoformat(dated['value']).isoformat()==dated['value'],'invalid document date:'+item['id'])
            except (TypeError,ValueError): raise ValueError(ERROR+':invalid document date:'+item['id'])
        documents.append(dict(id=item['id'], title=item['titre'], author=item['auteur'], path=item['path'],
            location=item['localisation'], scope=item['objet'], format=suffix[1:],date=deepcopy(dated)))
    result['documents']['items'] = sorted(documents,key=lambda item:item['date']['value'] or '9999-12-31')
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
            location=passages[key]['location'],
            short_label=result['reading']['piece_labels'][passages[key]['piece_ref']] +
                (' · p. ' + str(passages[key]['page']) if passages[key]['page'] else '')) for key in refs]

    business = result['business']
    patterns=index(business['architectures'], 'business/architectures')
    require(list(patterns)==['backbone','suite'], 'architecture pattern order')
    require([p['id'] for p in business['pattern_reading']['providers']]==list(PROVIDERS), 'pattern provider order')
    for provider in business['pattern_reading']['providers']:
        require(provider['pattern_ref'] is None or provider['pattern_ref'] in patterns, 'unknown architecture pattern')
        provider['proofs']=proofs(provider.pop('proof_refs'))
    index(business['axes'], 'business/axes')
    index(business['others'], 'business/others')
    business['architecture_proofs'] = proofs(business.pop('architecture_proof_refs'))
    index(business['oms']['rows'], 'business/oms/rows')
    for item in [*business['axes'], *business['others'], business['oms'], *business['oms']['rows']]:
        item['proofs'] = proofs(item.pop('proof_refs'))

    index(result['brief']['questions'], 'brief/questions')
    index(result['brief']['actors']['items'], 'brief/actors')
    try: date.fromisoformat(result['brief']['start']['value'])
    except ValueError: raise ValueError(ERROR+':invalid study start date')
    for item in [*result['brief']['questions'], result['brief']['highlights'],result['brief']['start'],*result['brief']['actors']['items']]:
        item['proofs'] = proofs(item.pop('proof_refs'))

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
    costs = result['costs']
    structures = index(architecture['cost_structures'], 'architecture/cost_structures')
    nature_refs = [ref for structure in structures.values() for ref in structure['cost_nature_refs']]
    require(len(nature_refs) == len(set(nature_refs)), 'duplicate model nature allocation')
    rows = costs['rows']
    ids = [row['structure_ref'] for row in rows]
    require(len(ids) == len(set(ids)) and set(ids) == set(structures), 'cost structure coverage')
    annual_seen = {slug: [] for slug in PROVIDERS}
    for row in rows:
        structure = structures[row['structure_ref']]
        row['title'] = glossary['notions'][structure['notion']]['libelle']
        row['nature_refs'] = deepcopy(structure['cost_nature_refs'])
        for slug in PROVIDERS:
            cell = row[slug]
            attached = proofs(cell.pop('proof_refs'))
            for entry in cell['entries']:
                section, identifier = entry.pop('row_ref').split('/', 1)
                require(section in ('integration','annual'), 'unknown source comparison section')
                source_rows = index(providers[slug][section]['rows'], slug + '/' + section)
                require(identifier in source_rows, 'unknown source comparison row:' + slug + '/' + identifier)
                source = source_rows[identifier]
                entry.update(kind=section, source_id=identifier, period=source['period'])
                if section == 'integration':
                    entry['amount_eur'] = source['amount_eur']
                    entry['reading_role'] = source['reading_role']
                else:
                    entry['amounts'] = deepcopy(source['amounts'])
                    entry['source_year'] = source['source_year']
                    annual_seen[slug].append(identifier)
                attached.extend(deepcopy(source['proofs']))
            cell['proofs'] = list({(proof['path'],proof['location']):proof for proof in attached}.values())
    for slug in PROVIDERS:
        require(len(annual_seen[slug]) == len(set(annual_seen[slug])) and
            set(annual_seen[slug]) == {row['id'] for row in providers[slug]['annual']['rows']},
            'source annual comparison coverage:' + slug)
    options = {row['stack']:row for row in baseline['options'] if row['stack'] in PROVIDERS}
    retained = {row['stack']:row for row in economic_evaluations['options'] if row['stack'] in PROVIDERS}
    require(set(options) == set(retained) == set(PROVIDERS), 'model provider coverage')
    horizons = [row['years'] for row in options[PROVIDERS[0]]['horizons']]
    require(horizons and len(horizons) == len(set(horizons)) and all(
        [row['years'] for row in options[slug]['horizons']] == horizons for slug in PROVIDERS), 'model common horizons')
    require([row['id'] for row in costs['annual_rows']] == list(retained[PROVIDERS[0]]['annual']['items']),
            'retained annual item coverage')
    bridge = []
    for slug in PROVIDERS:
        option = options[slug]
        source_total = next(row['amount_eur'] for row in providers[slug]['integration']['rows']
                            if row['id'] == ('total-copil' if slug == 'microsoft' else 'somme-lots'))
        bridge.append(dict(id=slug, selection_eur=option['selection_buy'], integration_eur=option['integration'],
            source_integration_eur=source_total,
            integration_additions_eur=float(Decimal(str(option['integration']))-Decimal(str(source_total))),
            annual=deepcopy(retained[slug]['annual']), service_start_month=option['service_start_month']))
    compiled_horizons = []
    for position, years in enumerate(horizons):
        horizon = dict(years=years, rows=[], totals={}, service_years={})
        for slug in PROVIDERS:
            source = options[slug]['horizons'][position]
            horizon['totals'][slug] = source['totals']['total']
            horizon['service_years'][slug] = source['service_years']
            expected = {ref for structure in structures.values() for ref in structure['cost_nature_refs']}
            require(set(source['cost_natures']) == expected, 'model nature coverage:' + slug)
        for row in rows:
            amounts = {slug:float(sum((Decimal(str(options[slug]['horizons'][position]['cost_natures'][ref]))
                for ref in row['nature_refs']), Decimal(0))) for slug in PROVIDERS}
            horizon['rows'].append(dict(id=row['structure_ref'], title=row['title'],
                scope=row['model_scope'], display=row['model_display'], amounts=amounts))
        for slug in PROVIDERS:
            total = sum((Decimal(str(row['amounts'][slug])) for row in horizon['rows']), Decimal(0))
            require(abs(total-Decimal(str(horizon['totals'][slug]))) < Decimal('0.005'), 'model total reconciliation:' + slug)
        compiled_horizons.append(horizon)
    costs['model'] = dict(horizons=compiled_horizons, bridge=bridge, model_version=baseline['model_version'])
    return result


def build_synvance_reference(guide, glossary, document_path, baseline, architecture, economic_evaluations):
    prices = {slug: read(ROOT / f'source/chiffrage/chiffrage-{slug}.yaml')['integration']['prix_rfi']
              for slug in PROVIDERS}
    annual = {slug: read(ROOT / f'source/maintenance/maintenance-{slug}.yaml')['valorisation_annuelle']
              for slug in PROVIDERS}
    return compile_synvance_reference(read(ROOT / SOURCE), guide, prices, annual, glossary, document_path,
                                      architecture, baseline, economic_evaluations)
