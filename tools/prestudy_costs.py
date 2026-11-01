"""Project stored market observations, without selecting prices or valuing FLOW work."""
from copy import deepcopy
from urllib.parse import urlsplit
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read

SOURCE = 'source/preetude-couts-marche.yaml'
SCHEMA = 'source/schema-preetude-couts-marche.yaml'
PROOFS = 'sources/calibration-couts-2026-10-22.yaml'
INFLATION = 'source/inflation.yaml'
ERROR = 'ERR_PRESTUDY_COSTS'


def compile_cost_evidence(spec, schema, stacks, market, inflation, proofs):
    errors = list(Draft202012Validator(schema).iter_errors(spec))
    if errors:
        raise ValueError(f'{ERROR}:{list(errors[0].path)}:{errors[0].message}')
    def require(ok, message):
        if not ok:
            raise ValueError(ERROR + ':' + message)
    def source(record):
        path = record.get('reference', record.get('url'))
        require(bool(path) and (urlsplit(path).scheme in ('https', 'http') or (path.startswith(('sources/', 'source/')) and '..' not in path.split('/'))), 'invalid evidence path')
        return dict(title=record.get('titre', ''), path=path, kind=record['nature'],
                    locator=record.get('repere', ''))
    identifiers = [row['id'] for row in spec['rates']]
    require(len(identifiers) == len(set(identifiers)), 'duplicate observation')
    rates = []
    for original in spec['rates']:
        row = deepcopy(original)
        require(set(row['stacks']) <= set(stacks), 'unknown stack')
        require(row['source_stack'] in stacks, 'unknown source owner')
        model = stacks[row['source_stack']]['model']
        node = model
        for key in row['basis_ref'].split('/'):
            require(isinstance(node, dict) and key in node, 'unknown observation provenance')
            node = node[key]
        require((row['min'] is None) == (row['max'] is None), 'partial observed range')
        require(row['min'] is None or row['min'] <= row['max'], 'reversed observed range')
        require(set(row['source_ids']) <= set(model['sources']), 'unknown market evidence')
        row['evidence'] = [source(model['sources'][key]) for key in row['source_ids']]
        row['basis_ref'] = 'source/stacks/' + row['source_stack'] + '.yaml#' + row['basis_ref']
        rates.append(row)
    def proof_rows(key):
        result = []
        for entry in spec[key]:
            require(entry['id'] in proofs['sources'], 'unknown proof')
            proof = proofs['sources'][entry['id']]
            result.append(dict(**deepcopy(entry), evidence=source(dict(proof, titre=entry['title'])),
                               scope=proof['portee'] if key == 'ai_refs' else entry['observation']))
        return result
    inputs = market['reperes_build_core']
    rows = {row['composant']: row for row in inputs['lignes']}
    groups = {}
    for key, names in spec['effort_groups'].items():
        require(set(names) <= set(rows), 'unknown effort reference')
        groups[key] = [deepcopy(rows[name]) for name in names]
    for programme in spec['programmes']:
        require(urlsplit(programme['url']).scheme == 'https', 'invalid programme evidence')
        require(programme['basis_ref'] == market['dependances']['preuve_build_core'], 'invalid programme provenance')
    products = []
    for slug, stack in stacks.items():
        model = stack['model']
        for element in model['elements']:
            products.append(dict(id=slug + '/' + element['id'], stack=slug, name=element['nom'],
                edition=element['edition'], licence=element['licence'], status=element['fondement'],
                pricing=deepcopy(element['tarification']),
                evidence=[source(model['sources'][key]) for key in element['sources']
                          if urlsplit(model['sources'][key]['reference']).scheme in ('https', 'http')]))
    # Exclude selected rates, provisions, gains and projections from this input reading.
    return dict(recorded_on=spec['recorded_on'], provenance=spec['provenance'], rates=rates,
        options=[dict(id=slug, label=stack['model']['nom']) for slug, stack in stacks.items()],
        purchases=proof_rows('purchase_refs'), products=products, ai=proof_rows('ai_refs'),
        programmes=deepcopy(spec['programmes']),
        indices=[dict(id=key, **deepcopy(value)) for key, value in inflation['sources'].items()],
        effort_groups=groups,
        effort_sources=[market['dependances']['preuve_build_core'], market['dependances']['revue_referentiel']],
        source_ref=SOURCE)


def build_cost_evidence(stacks, market):
    return compile_cost_evidence(read(ROOT / SOURCE), read(ROOT / SCHEMA), stacks, market,
                                 read(ROOT / INFLATION), read(ROOT / PROOFS))
