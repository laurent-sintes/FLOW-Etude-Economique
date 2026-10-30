"""Validate product coverage separately from Make work and contextual integration."""
import hashlib
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read

PATH='source/qualification-buy.yaml'

def coverage_sources(model):
    """Resolve the evidence registry shared by Make and Buy coverage profiles."""
    sources=read(ROOT/'sources/core-system-solutions-2026-10-22.yaml')['sources']
    for key,source in model.get('preuves',{}).items():
        assert key not in sources or sources[key]==source, ('Conflicting coverage source',key)
        sources[key]=source
    return sources

def validate(model, doc=None):
    d=doc if doc is not None else read(ROOT/PATH)
    Draft202012Validator(read(ROOT/'source/schema-qualification-buy.yaml')).validate(d)
    blocks={b['bloc']:b['capacite'] for b in model['blocs']}
    assert len(blocks)==len(model['blocs']) and len(set(blocks.values()))==len(blocks), 'Duplicate capability identity'
    blocks['TRANSVERSE']=None
    expected={(cap,s) for cap in blocks.values() for s in ('microsoft','sap')}
    assert {(r['capacite'],r['stack']) for r in d['revues']}==expected, 'Buy capability coverage'
    assert len(d['revues'])==len(expected)
    sources=coverage_sources(model)
    exceptions={e['id']:e for e in d['exceptions']}
    assert len(exceptions)==len(d['exceptions'])
    for e in exceptions.values():
        assert set(e['blocs'])<=blocks.keys() and set(e['sources'])<=d['sources'].keys()
        if e['statut']=='a_qualifier':
            assert e['cout_initial_eur_ht'] is None and e['cout_annuel_eur_ht'] is None
    components={s:{c['id'] for c in read(ROOT/f'source/stacks/{s}.yaml')['elements']} for s in ('microsoft','sap')}
    for row in d['revues']:
        assert row['bloc'] in blocks and row['capacite']==blocks[row['bloc']], 'Buy capability alias'
        coverage=model['couvertures'][row['couverture_ref']]
        assert set(coverage['composants'])<=components[row['stack']]
        assert set(coverage['sources'])<=sources.keys(), ('Unknown Buy coverage source',row['couverture_ref'])
        for key in coverage['sources']:
            source=sources[key]
            assert all(isinstance(source.get(field),str) and source[field].strip() for field in ('titre','reference','portee')), ('Incomplete coverage source',key)
        targets={e['id'] for e in exceptions.values() if row['stack'] in e['stacks'] and row['bloc'] in e['blocs']}
        assert set(row['exceptions'])==targets
        assert (row['statut']=='point_cible')==bool(targets)
    ids=set()
    for work in d['developpements']:
        assert work['id'] not in ids;ids.add(work['id'])
        e=exceptions[work['exception']]
        assert e['statut']=='ecart_demontre' and work['stack'] in e['stacks']
        assert work['preuve'] in d['sources'] and work['fonction_absente'] and work['financement_distinct']
        assert all(0<=lo<=mid<=hi for lo,mid,hi in zip(work['bas'],work['central'],work['haut']))
    return d

def integration_paths():
    d=read(ROOT/'source/parcours-integration.yaml')
    assert hashlib.sha256((ROOT/d['capture']).read_bytes()).hexdigest()==d['empreinte']
    catalog=read(ROOT/d['capture'])['scenario_catalog']
    scenarios={s['id']:s for s in catalog['scenarios']};paths={p['id']:p for p in catalog['paths']}
    assert len(scenarios)==len(catalog['scenarios']) and len(paths)==len(catalog['paths'])
    assert len(d['scenarios'])==len(scenarios) and {s['scenario'] for s in d['scenarios']}==scenarios.keys()
    caps={b['capacite_id'] for b in read(ROOT/'source/grille-complexite.yaml')['blocs']}
    activities={a['id'] for a in read(ROOT/'source/integration.yaml')['activites']}
    lots={l['id']:l for l in d['lots']}
    assert len(lots)==len(d['lots'])
    assert {i for l in lots.values() for i in l['activites']}==activities
    assert sum(len(l['activites']) for l in lots.values())==len(activities)
    for row in d['scenarios']:
        assert set(row)=={'scenario','parcours','capacites','lots','statut','justification'}
        assert set(row['lots'])<=lots.keys() and len(row['lots'])==len(set(row['lots']))
        linked={p['id'] for p in paths.values() if p['scenario_id']==row['scenario']}
        assert set(row['parcours'])==linked
        contributions={c['node_id'] for pid in linked for step in paths[pid]['steps'] for c in step['contributions'] if c['node_id'] in caps}
        assert set(row['capacites'])==contributions
    return d,catalog
