"""Presentation projections for the sponsor journey; the economic engine owns prices.

The atlas sums the existing funding instances owned by a capability. Reusing an
estimate template, or being a beneficiary of shared work, never creates another
funded item. Transverse work stays outside the business map.
"""
from collections import Counter
from copy import deepcopy
from decimal import Decimal

from content_model import resolve_text_tree
from validate_stacks import ROOT, read


MAKE = ('java-spring', 'dotnet', 'rust')
CASES = ('bas', 'central', 'haut')
PATH = 'source/parcours-sponsor.yaml'
ATLAS_PATH = 'source/atlas-sponsor.yaml'


def exact_sum(values):
    """Aggregate published cents without introducing another rounding convention."""
    return float(sum((Decimal(str(value)) for value in values), Decimal(0)))


def aggregate(rows):
    return dict(capabilities=[r['capacite_id'] for r in rows],
        stacks={slug:dict(status='pending_reestimation',raw_jh={'central':None,'bas':None,'haut':None},
            prestations_eur_ht=None,retained_units=[]) for slug in MAKE},
        buy={slug:dict(counts=dict(Counter(r['buy'][slug]['statut'] for r in rows))) for slug in ('microsoft','sap')})

def atlas_metrics(business_map):
    rows = business_map['rows']
    nodes = {node['id']: node for row in rows for node in row['hierarchie']}
    area_ids = list(dict.fromkeys(row['chemin'][1] for row in rows))
    ba_ids = list(dict.fromkeys(row['chemin'][2] for row in rows))

    def node_group(identifier, parent, members):
        node = nodes[identifier]
        return dict(id=identifier, name=node['nom'], parent=parent, definition=node['definition'],
                    **aggregate(members))

    areas = []
    for identifier in area_ids:
        members = [row for row in rows if row['chemin'][1] == identifier]
        areas.append(dict(**node_group(identifier, members[0]['chemin'][0], members),
                          business_areas=list(dict.fromkeys(row['chemin'][2] for row in members))))
    business_areas = []
    for identifier in ba_ids:
        members = [row for row in rows if row['chemin'][2] == identifier]
        business_areas.append(node_group(identifier, members[0]['chemin'][1], members))
    capabilities = {row['capacite_id']: dict(id=row['capacite_id'], block=row['id'],
        name=row['capacite']['nom'], definition=row['capacite']['definition'], parent=row['chemin'][2],
        area=row['chemin'][1], path=row['chemin'], **aggregate([row])) for row in rows}
    neighbors = {node['id']: dict(id=node['id'], name=node['nom'], kind=node['kind'])
                 for theme in business_map['themes'] for node in theme['neighbors']}
    return dict(areas=areas, business_areas=business_areas, capabilities=capabilities,
                neighbors=list(neighbors.values()), source=deepcopy(business_map['source']))


def metrics(content, baseline):
    business_map=content['business_map']
    funds=business_map['family_funding']
    assert len({f['id'] for f in funds})==len(funds), 'Duplicate family funding'
    assert not business_map['funding'], 'Legacy Make funding must not be active'
    options=[];totals={}
    for option in baseline['options']:
        slug=option['stack'];parameters=baseline['parameters']['options'][slug]
        build_months=option.get('initial_months',parameters.get('build_mois',0))
        integration_months=baseline['make_integration_months'] if option['mode']=='Make' else parameters['integration_mois']
        annual=content['stacks'][slug]['economic_reading']['total']
        assert abs(annual-exact_sum([*option['annual_base'].values(),*option['editor_prices'][:1]]))<.000001
        options.append(dict(stack=slug,name=option['name'],mode=option['mode'],
            build_eur_ht=option.get('obtention',option['build']),integration_eur_ht=option['integration'],
            build_months=build_months,integration_months=integration_months,annual_eur_ht=annual))
        if slug not in MAKE:continue
        units=content['stacks'][slug]['economic']['core_units']
        priced=content['stacks'][slug]['economic']['detail_build']
        charge=sum(u['total_jh'] for u in units)
        cost=exact_sum(u['cost_eur_ht'] for u in units)
        assert cost==priced['prestations']==exact_sum(f['cout_eur_ht'] for f in funds if f['stack']==slug)
        assert priced['pilotage']==0
        assert cost==option['build']
        totals[slug]=dict(raw_jh={'central':charge,'bas':None,'haut':None},net_jh=charge,
            prestations_eur_ht=cost,pilotage_eur_ht=0,build_eur_ht=cost,
            build_months=build_months,integration_months=integration_months,
            units=deepcopy(units),family_jh=charge,family_cost_eur_ht=cost)
    atlas=atlas_metrics(business_map)
    for slug,total in totals.items():
        for node in [*atlas['areas'],*atlas['business_areas'],*atlas['capabilities'].values()]:
            units=[dict(id=u['id'],label=u['label']) for u in total['units']
                if set(node['capabilities']) & {c['native_id'] for c in u['capabilities']}]
            node['stacks'][slug]['retained_units']=units
            node['stacks'][slug]['status']='included_in_family' if units else 'pending_reestimation'
    sap=content['stacks']['sap'];lots=sap['economic']['detail_integration']['base_rfi'];printed=sap['pricing']['total_imprime_eur']
    return dict(work_totals=totals,options=options,map=atlas,transverse={},natures=[],
        market=dict(sap=dict(sum_lots_eur_ht=lots,printed_total_eur_ht=printed,discrepancy_eur_ht=exact_sum([printed,-lots])),
            references_count=len(content['market']['references']),
            eligible_count=content['market']['analyse_dispersion']['resultat_actuel']['references_eligibles']))

def validate_editorial(editorial, content, document_path):
    def validate_links(value):
        if isinstance(value, dict):
            for child in value.values():
                validate_links(child)
        elif isinstance(value, list):
            for child in value:
                validate_links(child)
        elif isinstance(value, str) and value.startswith(('source/', 'sources/', 'archives/')):
            document_path(value)

    validate_links(editorial)
    atlas = editorial['atlas']
    themes = {theme['id'] for theme in content['business_map']['themes']}
    neighbors = {node['id'] for theme in content['business_map']['themes'] for node in theme['neighbors']}
    assert set(atlas['focus']) <= themes, 'Unmapped sponsor subject'
    for subject in atlas['focus'].values():
        assert subject['proof'] in atlas['proofs'], 'Missing sponsor proof'
    for neighbor in atlas['neighbors']:
        assert set(neighbor['native']) <= neighbors, 'Unknown neighboring domain'
        assert neighbor['proof'] in atlas['proofs'], 'Missing neighboring domain proof'
    assert editorial['operations']['scenario'] in {row['scenario'] for row in content['integration_paths']['scenarios']}, 'Unknown integration scenario'


def build(content, baseline, glossary, document_path):
    editorial = resolve_text_tree(read(ROOT / PATH), glossary)
    editorial['atlas'] = resolve_text_tree(read(ROOT / ATLAS_PATH), glossary)
    validate_editorial(editorial, content, document_path)
    editorial['metrics'] = metrics(content, baseline)
    return editorial
