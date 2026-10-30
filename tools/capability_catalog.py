"""Faithful native input, distinct from the study's functional interpretations."""
from copy import deepcopy
import hashlib
from validate_stacks import ROOT, read
from model_context import model_memo
SOURCE='source/referentiel-capacites.yaml'
ANALYSIS='source/analyse-perimetre-core.yaml'

@model_memo
def native():
    spec=read(ROOT/SOURCE)
    assert set(spec)=={'version','source','sha256','domain_id'} and spec['version']==1
    assert hashlib.sha256((ROOT/spec['source']).read_bytes()).hexdigest()==spec['sha256'], 'Native source changed'
    snapshot=read(ROOT/spec['source'])
    assert snapshot['domaine_id']==spec['domain_id']
    return snapshot

@model_memo
def analysis():
    doc=read(ROOT/ANALYSIS);snapshot=native()
    assert set(doc)=={'version','status','blocs'} and doc['version']==1 and doc['status']=='analyse_etude'
    nodes={n['id']:n for n in snapshot['nodes']}
    caps={i for i,n in nodes.items() if n['kind']=='capability'}
    assert {b['capacite_id'] for b in doc['blocs']}==caps
    assert len(doc['blocs'])==len(caps)
    assert len({b['id'] for b in doc['blocs']})==len(caps)
    edges={(r['source_id'],r['target_id']) for r in snapshot['relations']}
    for b in doc['blocs']:
        assert set(b)=={'id','capacite_id','chemin','fonctions','variantes_source','frontiere'}
        assert b['chemin'][-1]==b['capacite_id']
        assert all(pair in edges for pair in zip(b['chemin'],b['chemin'][1:]))
    return doc

@model_memo
def catalog():
    snapshot=native();doc=analysis()
    nodes={n['id']:n for n in snapshot['nodes']}
    def node(i):
        n=nodes[i];f=n['fields']
        # Keep native text and links byte-for-byte in the projection.
        return dict(id=i,kind=n['kind'],nom=f['name'],definition=f.get('definition'),
                    perimetre=f.get('scope'),comparaisons=deepcopy(f.get('market_comparisons',[])),native=deepcopy(n))
    rows=[dict(**b,capacite=node(b['capacite_id']),hierarchie=[node(i) for i in b['chemin'][:3]],
               variantes=[node(i) for i in b['variantes_source']]) for b in doc['blocs']]
    order={n['id']:i for i,n in enumerate(snapshot['nodes'])}
    rows.sort(key=lambda r:tuple(order[i] for i in r['chemin']))
    return dict(rows=rows,source=read(ROOT/SOURCE)['source'],source_contract=SOURCE,
                analysis_source=ANALYSIS,method={'axes':{}},reprise={},changed_fields=len(snapshot.get('relecture',{}).get('champs_modifies',[])))

def dependencies():
    return {SOURCE,ANALYSIS,read(ROOT/SOURCE)['source'],'tools/capability_catalog.py'}
