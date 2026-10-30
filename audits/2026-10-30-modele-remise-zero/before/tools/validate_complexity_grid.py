"""Validate the reviewed business hierarchy and the independent complexity grid."""
import hashlib
import sys
from collections import Counter
from pathlib import Path
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(grid=None, check_current=False):
    grid=grid if grid is not None else read(ROOT/'source/grille-complexite.yaml')
    schema=read(ROOT/grid['dependances']['schema'])
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(grid)
    for p,h in grid['empreintes'].items():
        assert digest(ROOT/p)==h, f'Stale dependency: {p}'
    assert set(grid['empreintes'])=={grid['dependances'][k] for k in ('methode','cartographie')}
    snapshot=read(ROOT/grid['dependances']['cartographie'])
    method=read(ROOT/grid['dependances']['methode'])
    nodes={n['id']:n for n in snapshot['nodes']}
    assert len(nodes)==len(snapshot['nodes'])
    assert snapshot['domaine_id']==grid['domaine_id']
    edges={(r['source_id'],r['target_id']) for r in snapshot['relations']}
    caps={i for i,n in nodes.items() if n['kind']=='capability'}
    assigned=Counter(b['capacite_id'] for b in grid['blocs'])
    assert set(assigned)==caps and all(n==1 for n in assigned.values()), 'Capability coverage'
    block_ids=[b['id'] for b in grid['blocs']]
    function_ids=[f['id'] for b in grid['blocs'] for f in b['fonctions']]
    assert len(set(block_ids))==len(block_ids) and len(set(function_ids))==len(function_ids), 'Duplicate identity'
    variants=[]
    for b in grid['blocs']:
        path=b['chemin']
        assert path[0]==grid['domaine_id'] and path[-1]==b['capacite_id']
        assert [nodes[i]['kind'] for i in path]==['domain','area','business_area','capability']
        assert all(pair in edges for pair in zip(path,path[1:])), f'Broken path: {b["id"]}'
        assert all(f['id'].startswith(b['id']+'.') for f in b['fonctions'])
        for axis,value in b['complexite'].items():
            assert value['niveau'] in method['axes'][axis]['niveaux']
        expected={r['target_id'] for r in snapshot['relations'] if r['source_id']==b['capacite_id'] and nodes[r['target_id']]['kind']=='behavior'}
        assert set(b['variantes_source'])==expected, f'Behavior coverage: {b["id"]}'
        variants+=b['variantes_source']
        assert nodes[b['capacite_id']]['fields'].get('market_comparisons'), 'Missing preserved comparisons'
    assert set(variants)=={i for i,n in nodes.items() if n['kind']=='behavior'}
    assert len(variants)==len(set(variants)), 'Duplicated behavior'
    for m in method['mecanismes_partages']:
        assert m['capacite_responsable'] in caps
        assert set(m['usages'])<=caps and m['capacite_responsable'] not in m['usages']
        assert len(m['usages'])==len(set(m['usages']))
    for m in method['familles_reemploi_a_qualifier']:
        assert set(m['capacites'])<=caps and len(set(m['capacites']))==len(m['capacites'])
    assert set(method['qualifications_ciblees'])<=caps
    if check_current:
        assert digest(Path(snapshot['provenance']['fichier']))==snapshot['provenance']['sha256'], 'Current cartography differs: review changes before recapture'
    return grid,snapshot,method

if __name__=='__main__':
    grid,snapshot,method=validate(check_current='--check-current' in sys.argv)
    print(f'VALID: {len(grid["blocs"])} capability blocks; {sum(len(b["fonctions"]) for b in grid["blocs"])} functions; {sum(len(b["variantes_source"]) for b in grid["blocs"])} source variants; three independent ordinal axes.')
