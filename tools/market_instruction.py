"""Complete instruction inventory, distinct from functional product coverage.

The cross-product is derived, never maintained as a second list of capabilities
or evidence. Existing axis observations remain owned by the market fiches.
Detailed qualifications are editorial inputs, with no economic adapter.
"""
from collections import Counter
from copy import deepcopy

from jsonschema import Draft202012Validator, FormatChecker

from market_oss import _reference
from validate_stacks import ROOT, read
from capability_catalog import analysis

SOURCE = 'source/instruction-marche.yaml'
SCHEMA = 'source/schema-instruction-marche.yaml'


def _fail(path, reason):
    raise ValueError(f'ERR_MARKET_INSTRUCTION {path}: {reason}')


def build_market_instruction(market, *, grid=None, instruction=None, core_functions=None):
    """Return all retained capability/product pairs and a separate progress count.

    `reperes_axes` means only that an existing selective axis cites the capability.
    It is deliberately not a functional coverage or parity assertion.
    """
    grid = analysis() if grid is None else grid
    instruction = read(ROOT / SOURCE) if instruction is None else instruction
    errors = sorted(Draft202012Validator(read(ROOT / SCHEMA), format_checker=FormatChecker()).iter_errors(instruction), key=lambda e: str(e.path))
    if errors:
        error = errors[0]
        _fail('.'.join(map(str, error.path)), error.message)
    reperes = market['reperes_build_core']
    scope = reperes['etude_oss']['perimetre']
    excluded = set(scope['bc_exclus'])
    blocks = [block for block in grid['blocs'] if block['id'] not in excluded]
    if len(blocks) != scope['bc_total'] - len(excluded):
        _fail('scope', 'retained grid differs from the declared comparison scope')
    by_native = {block['capacite_id']: block for block in blocks}
    if len(by_native) != len(blocks):
        _fail('scope', 'duplicate native capability')
    fiches = reperes['fiches_produit']
    axes = reperes['cadre_comparaison']['axes']
    axis_by_bc = {block['id']: [] for block in blocks}
    for axis in axes:
        if any(axis['id'] not in fiche['evaluations'] for fiche in fiches.values()):
            _fail('axis.' + axis['id'], 'axis observation missing from a product fiche')
        for bc_ref in axis['bc_refs']:
            if bc_ref not in axis_by_bc:
                _fail('axis.' + axis['id'], 'unknown or excluded capability')
            axis_by_bc[bc_ref].append(axis['id'])
    records = instruction['qualifications']
    if core_functions is None and any(row['evaluation_function_ref'] is not None for row in records):
        from core_qualification import validate
        core_functions = validate()['functions']
    functions = {row['id']: row for row in core_functions or []}
    qualified_by_pair = {}
    seen = set()
    for record in records:
        path = record['id']
        if path in seen:
            _fail(path, 'duplicate qualification id')
        seen.add(path)
        capability, product = record['capability_ref'], record['product_ref']
        if capability not in by_native or product not in fiches:
            _fail(path, 'unknown capability or product')
        block = by_native[capability]
        needs = {item['id'] for item in block['fonctions']}
        if not set(record['need_refs']) <= needs:
            _fail(path, 'function needs must belong to the named native capability')
        function_ref = record['evaluation_function_ref']
        if function_ref is not None:
            function = functions.get(function_ref)
            if not function or capability not in function['capability_refs'] or not set(record['need_refs']) <= set(function['need_refs']):
                _fail(path, 'Core evaluation function does not match capability and needs')
        for proof in record['evidence_refs']:
            _reference(proof['source_ref'], path + '.evidence_refs')
        if record['classification'] != 'inconnu' and not record['evidence_refs']:
            _fail(path, 'observation, analogy or engineering assumption requires evidence')
        if record['status'] == 'non_etudie' and record['classification'] != 'inconnu':
            _fail(path, 'unstudied qualification must retain unknown classification')
        if record['status'] == 'qualifie':
            if (record['classification'] == 'inconnu' or record['unknowns'] or
                    not record['review'] or record['review']['decision'] != 'retenu'):
                _fail(path, 'qualified record requires evidence, resolved unknowns and retained review')
        if record['classification'] == 'inconnu' and not record['unknowns']:
            _fail(path, 'unknown qualification must explain its unknowns')
        qualified_by_pair.setdefault((capability, product), []).append(record)
    rows = []
    for block in blocks:
        for product in fiches:
            pair_records = qualified_by_pair.get((block['capacite_id'], product), [])
            linked_axes = axis_by_bc[block['id']]
            status = 'qualification_detaillee' if pair_records else 'reperes_axes' if linked_axes else 'non_etudie'
            need_ids = {item['id'] for item in block['fonctions']}
            retained_needs = {need for record in pair_records if record['status'] == 'qualifie' for need in record['need_refs']}
            rows.append(dict(capability_ref=block['capacite_id'], bc_ref=block['id'], product_ref=product,
                status=status, axis_refs=linked_axes[:], qualification_refs=[item['id'] for item in pair_records],
                functional_status='besoins_instruits' if retained_needs == need_ids else 'instruction_partielle' if pair_records else 'non_qualifie',
                pending_need_refs=sorted(need_ids - retained_needs),
                observation_refs=[f"source/references-couts-integration.yaml#reperes_build_core/fiches_produit/{product}/evaluations/{axis}" for axis in linked_axes]))
    counts = Counter(row['status'] for row in rows)
    progress = []
    for product, fiche in fiches.items():
        product_rows = [row for row in rows if row['product_ref'] == product]
        product_counts = Counter(row['status'] for row in product_rows)
        progress.append(dict(product_ref=product, label=fiche['nom'], total=len(product_rows),
            non_etudie=product_counts['non_etudie'], reperes_axes=product_counts['reperes_axes'],
            qualification_detaillee=product_counts['qualification_detaillee'],
            besoins_instruits=sum(row['functional_status'] == 'besoins_instruits' for row in product_rows)))
    return dict(id=instruction['id'], interpretation=instruction['interpretation'], source_ref=SOURCE,
        status_labels=deepcopy(instruction['status_labels']),
        capabilities=[dict(bc_ref=block['id'], capability_ref=block['capacite_id'], path=list(block['chemin']), need_refs=[item['id'] for item in block['fonctions']], proposed_functions=deepcopy(block['fonctions']), analysis_source='source/analyse-perimetre-core.yaml') for block in blocks],
        products=[dict(id=key, label=fiche['nom']) for key, fiche in fiches.items()], rows=rows, progress=progress,
        qualifications=deepcopy(records),
        summary=dict(capabilities=len(blocks), products=len(fiches), pairs=len(rows),
            capabilities_with_axis_references=sum(bool(value) for value in axis_by_bc.values()),
            pairs_by_status={key: counts[key] for key in ('non_etudie', 'reperes_axes', 'qualification_detaillee')},
            detailed_qualifications=len(records), retained_qualifications=sum(row['status'] == 'qualifie' for row in records)))


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--details', action='store_true', help='Print the full instruction matrix, without editing sources')
    args = parser.parse_args()
    matrix = build_market_instruction(read(ROOT / 'source/references-couts-integration.yaml'))
    result = matrix if args.details else {key: matrix[key] for key in ('interpretation', 'summary', 'progress')}
    print(json.dumps(result, ensure_ascii=False, indent=2))
