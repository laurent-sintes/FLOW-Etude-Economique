"""Active cost adaptation: retained Make families, Buy complements and annual work."""
from copy import deepcopy
from jsonschema import Draft202012Validator
from validate_stacks import ROOT,read
from model_context import model_memo
from capability_catalog import analysis,dependencies as catalog_dependencies
from buy_qualification import validate as validate_buy,PATH as BUY_PATH

PATH='source/couvertures-produits.yaml'
NATURES=['configuration','extension','developpement','assemblage','qualification','frontend']
SLUGS=('java-spring','dotnet','rust','microsoft','sap')

@model_memo
def validate():
    doc=read(ROOT/PATH)
    Draft202012Validator(read(ROOT/'source/schema-couvertures-produits.yaml')).validate(doc)
    maintenance=read(ROOT/'source/unites-maintenance.yaml')
    Draft202012Validator(read(ROOT/'source/schema-unites-maintenance.yaml')).validate(maintenance)
    doc['blocs']=[dict(bloc=b['id'],capacite=b['capacite_id']) for b in analysis()['blocs']]
    doc['transverse']={'id':'TRANSVERSE','nom':'Travaux transverses'}
    doc['maintenance']=maintenance['maintenance']
    doc['date']='2026-10-30'
    doc['dependances']={}
    validate_buy(doc)
    return doc

def dependencies():
    return catalog_dependencies()|{PATH,'source/schema-couvertures-produits.yaml','source/schema-unites-maintenance.yaml','source/unites-maintenance.yaml','tools/current_cost_inputs.py',BUY_PATH,'source/schema-qualification-buy.yaml'}

def apply(docs):
    model=validate();buy=validate_buy(model);result=deepcopy(docs)
    for slug,doc in result.items():
        # No synthetic zero-cost Make feature or legacy funding assignment.
        doc['core']=[]
        for w in (w for w in buy['developpements'] if w['stack']==slug):
            doc['core'].append(dict(feature=w['id'],traitement='complement_integration',
                jh_backend_avant_ia=dict(zip(NATURES[:-1],w['central'][:-1])),jh_frontend_avant_ia=w['central'][-1],
                plages_jh={c:dict(zip(NATURES,w[c])) for c in ('bas','central','haut')},
                reste_ref=BUY_PATH,justification=w['fonction_absente']))
        m=model['maintenance']['par_stack'][slug]
        for a in doc['maintenance']['activites']:
            for c in a['charges']:
                if c.get('jh_unitaire_ref'):
                    c['jh_unitaire']=m[c['jh_unitaire_ref']];c['travail']=m['justification']
        doc['maintenance']['maintenance_complements_buy_jh_annuels']=(m['entretien_complements_buy_jh'] if slug in SLUGS[:3]
            else sum(w['entretien_jh_annuels'] for w in buy['developpements'] if w['stack']==slug))
        doc['maintenance']['justification_complements']=m['justification']
    return result

@model_memo
def active_doc(slug):
    return apply({slug:read(ROOT/f'source/chiffrage/chiffrage-{slug}.yaml')})[slug]
