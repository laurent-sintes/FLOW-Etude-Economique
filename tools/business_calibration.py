"""Validate the SCM calibration and adapt its residual work to the existing cost engine."""
from copy import deepcopy
import hashlib
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read
from buy_qualification import validate as validate_buy, coverage_sources, PATH as BUY_PATH
from model_context import model_memo

PATH='source/recalibration-metier.yaml'
SLUGS=('java-spring','dotnet','rust','microsoft','sap')

@model_memo
def validate(doc=None):
    # The editable calibration owns work; the grid owns the need and boundaries.
    d=deepcopy(doc) if doc is not None else read(ROOT/PATH)
    Draft202012Validator(read(ROOT/'source/schema-recalibration-metier.yaml')).validate(d)
    for p,expected in d['dependances'].items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==expected, ('stale calibration',p)
    grid=read(ROOT/'source/grille-complexite.yaml')
    expected={b['capacite_id']:b for b in grid['blocs']}
    by_capability={b['capacite']:b for b in d['blocs']}
    assert len(by_capability)==len(d['blocs']), 'Duplicate capability assignment'
    assert set(by_capability)==set(expected), 'Capability assignment coverage'
    assert len({b['bloc'] for b in d['blocs']})==len(d['blocs']), 'Duplicate funding alias'
    for capability,row in by_capability.items():
        block=expected[capability]
        assert row['bloc']==block['id'], ('Capability funding alias',capability)
        derived=dict(scenario=' ; '.join(f['resultat'] for f in block['fonctions']),frontiere=block['frontiere'])
        for key,value in derived.items():
            assert key not in row or row[key]==value, ('Stale derived need',capability,key)
        row.update(derived)
    # Source ordering must not alter aggregation order or calculated cents.
    d['blocs']=[by_capability[b['capacite_id']] for b in grid['blocs']]
    sources=coverage_sources(d)
    ids={b['bloc'] for b in d['blocs']}
    components={s:{e['id'] for e in read(ROOT/f'source/stacks/{s}.yaml')['elements']} for s in SLUGS}
    used=set()
    for row in [*d['blocs'],d['transverse']]:
        assert set(row['stacks'])==set(SLUGS[:3])
        fronts=[]
        for s,assignment in row['stacks'].items():
            lot=d['lots'][assignment['travaux_ref']]; c=d['couvertures'][assignment['couverture_ref']]
            used.add(assignment['travaux_ref'])
            assert set(c['composants'])<=components[s] and set(c['sources'])<=set(sources)
            assert (assignment['traitement']=='build_core')==(s in SLUGS[:3])
            if s in SLUGS[:3]: fronts.append(tuple(lot[k][-1] for k in ('bas','central','haut')))
            else: assert all(lot[k][-1]==0 for k in ('bas','central','haut'))
        assert len(set(fronts))==1, ('React must be common',row.get('bloc'))
        for reuse in row.get('reemploi',[]):
            assert reuse['proprietaire'] in ids and reuse['proprietaire']!=row['bloc']
    assert used==set(d['lots']), ('unused residual packages',set(d['lots'])-used)
    for lot in d['lots'].values():
        assert all(0<=lo<=mid<=hi for lo,mid,hi in zip(lot['bas'],lot['central'],lot['haut']))
    assert d['methode']['natures']==['configuration','extension','developpement','assemblage','qualification','frontend']
    required={'source/grille-complexite.yaml','source/methode-complexite.yaml','sources/recalibration-metier-2026-10-25.yaml'}|{f'source/stacks/{s}.yaml' for s in SLUGS}
    assert required<=set(d['dependances'])
    validate_buy(d)
    return d

def apply(docs, calibration=None, buy=None):
    d=calibration if calibration is not None else validate()
    q=validate_buy(d,buy)
    result=deepcopy(docs)
    for slug,doc in result.items():
        core=[]
        for row in [*d['blocs'],d['transverse']] if slug in SLUGS[:3] else []:
            a=row['stacks'][slug]; lot=d['lots'][a['travaux_ref']]
            natures=d['methode']['natures']
            core.append(dict(feature=row.get('bloc',row.get('id')),traitement=a['traitement'],
                jh_backend_avant_ia=dict(zip(natures[:-1],lot['central'][:-1])),jh_frontend_avant_ia=lot['central'][-1],
                plages_jh={case:dict(zip(natures,lot[case])) for case in ('bas','central','haut')},
                reste_ref=PATH,justification=lot['travail'],couverture=d['couvertures'][a['couverture_ref']]))
        for work in (w for w in q['developpements'] if w['stack']==slug):
            natures=d['methode']['natures']
            core.append(dict(feature=work['id'],traitement='complement_integration',
                jh_backend_avant_ia=dict(zip(natures[:-1],work['central'][:-1])),jh_frontend_avant_ia=work['central'][-1],
                plages_jh={case:dict(zip(natures,work[case])) for case in ('bas','central','haut')},
                reste_ref=BUY_PATH,justification=work['fonction_absente']))
        doc['core']=core
        m=d['maintenance']['par_stack'][slug]
        for a in doc['maintenance']['activites']:
            for c in a['charges']:
                key=c.get('jh_unitaire_ref')
                if key: c['jh_unitaire']=m[key];c['travail']=m['justification']
        doc['maintenance']['maintenance_complements_buy_jh_annuels']=(m['entretien_complements_buy_jh'] if slug in SLUGS[:3]
            else sum(w['entretien_jh_annuels'] for w in q['developpements'] if w['stack']==slug))
        doc['maintenance']['justification_complements']=m['justification']
    return result

@model_memo
def active_doc(slug):
    return apply({slug:read(ROOT/f'source/chiffrage/chiffrage-{slug}.yaml')})[slug]

if __name__=='__main__':
    d=validate()
    print(f"Validated {len(d['blocs'])} SCM capabilities, five stacks, shared mechanisms and explicit residual ranges.")
