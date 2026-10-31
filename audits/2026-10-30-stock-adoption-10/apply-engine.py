from pathlib import Path
from copy import deepcopy
import sys
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'tmp/model-deps'))
import yaml
def read(p):return yaml.safe_load((ROOT/p).read_text(encoding='utf-8'))
def save(p,v):(ROOT/p).write_text(yaml.safe_dump(v,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
def replace(p,a,b):
 f=ROOT/p;s=f.read_text(encoding='utf-8');assert a in s,(p,a);f.write_text(s.replace(a,b),encoding='utf-8',newline='\n')
replace('tools/estimation_preparation.py','    d = {k: deepcopy(documents[path]) for k, path in contract[\'inputs\'].items()}',
"""    if contract['recipe'] == 'native_component_analogies_v1':
        from estimation_stock import prepare_stock
        return prepare_stock(documents, contract, registry, formula)
    require(contract['recipe'] == 'native_reuse_plus_complements_v1', 'Unsupported preparation recipe')
    d = {k: deepcopy(documents[path]) for k, path in contract['inputs'].items()}""")
replace('tools/retained_core.py',"'tools/estimation_preparation.py'}","'tools/estimation_preparation.py', 'tools/estimation_stock.py'}")
replace('tools/estimation_stock.py',"pu=bank[macro['analogue']]*macro['central'];du=0","pu=0;du=0")
replace('tools/estimation_stock.py',"pu+=scaffold['program_units_per_new_service_module']","pu=formula('module_analogy',reference_units=bank[macro['analogue']],fraction=macro['central'],scaffold_units=scaffold['program_units_per_new_service_module'])")
m=read('source/fondamentaux.yaml');model=m['estimation_model']
model['objects'].append(dict(id='component_attribution',label='Taille attribuée à un composant métier',owner='source/calculs-estimation-core.yaml',attributes=['référence et révision','mesures source et exclusions','part de taille supposée','plancher métier déjà mesuré','propriétaire du mécanisme réutilisé']))
model['relations'].extend([
 dict(id='attribution_evidence',source='component_attribution',target='calculation_evidence',cardinality='many-to-many',meaning='Les mesures source sont distinctes des parts de pertinence supposées.'),
 dict(id='attribution_input',source='component_attribution',target='cocomo_input',cardinality='many-to-one',meaning='Produit une taille équivalente, pas un effort observé.')])
model['rules'].extend([
 dict(id='component_attribution',title='Attribuer une taille métier au code mixte',expression='max(taille source après retrait du patrimoine déjà financé × part supposée, plancher métier mesuré)',variables={'inputs':'Mesures sources, déductions du financement existant, part de pertinence et plancher par fichier'},unit='unités logiques équivalentes',kind='algorithm',note='Union des fichiers et des instructions avant calcul ; attribution d’ingénierie, sans score de complexité ni proportion observée.'),
 dict(id='module_analogy',title='Dimensionner un module nouveau par analogie',expression='reference_units * fraction + scaffold_units',variables={'reference_units':'Comportement natif après déduction du patrimoine déjà financé','fraction':'Fraction de comportement nouveau supposée, pas norme de marché','scaffold_units':'Structure du service nouveau mesurée dans la technologie native'},domains={'reference_units':{'minimum':0},'fraction':{'minimum':0},'scaffold_units':{'minimum':0}},unit='unités logiques équivalentes',kind='arithmetic',note='Schémas, vues et configurations ajoutés séparément. Les fractions et les partages du code restent des hypothèses explicites.')])
model['implementations'].append(dict(rules=['component_attribution'],path='tools/estimation_stock.py'))
next(x for x in model['implementations'] if x['path']=='tools/estimation_calculation.py')['rules'].append('module_analogy')
model['labels'].update(common_effort='Base commune',complement_effort='Compléments Flow',funding_consumed='Réutilisé',funding_funded='Financé dans cette famille')
model['labels']['shared_assumptions_note']='Les références partagent des hypothèses de périmètre, de fractions des modules Flow et de COCOMO. La taille des analogues peut différer selon le produit ; leur proximité ne fournit pas quatre validations indépendantes.'
model['labels']['shared_assumptions']='Part des compléments Flow dans la référence COCOMO'
save('source/fondamentaux.yaml',m)
s=read('source/schema-fondamentaux.yaml')
for key in ['common_effort','complement_effort','funding_consumed','funding_funded']:s['properties']['estimation_model']['properties']['labels']['properties'][key]={'type':'string','minLength':1}
save('source/schema-fondamentaux.yaml',s)
s=read('source/schema-calculs-estimation-core.yaml');item=s['properties']['calculations']['items'];props=item['properties']
props['recipe']={'enum':['native_reuse_plus_complements_v1','native_component_analogies_v1']}
old=deepcopy(props['inputs']);keys=['specification','native_inputs','native_measures','allocation','baseline','cosmic','productivity_source','activities','decision_evidence']
stock={'type':'object','properties':{k:{'type':'string','minLength':1} for k in keys},'required':keys,'additionalProperties':False}
props['inputs']={'oneOf':[old,stock]}
item['allOf']=[{'if':{'properties':{'recipe':{'const':recipe}}},'then':{'properties':{'inputs':inputs}}} for recipe,inputs in [('native_reuse_plus_complements_v1',old),('native_component_analogies_v1',stock)]]
s['properties']['mechanisms']['items']['properties']['basis']['oneOf'].append({'type':'object','properties':{'kind':{'const':'component_domain'},'scope':{'type':'string','minLength':1}},'required':['kind','scope'],'additionalProperties':False})
save('source/schema-calculs-estimation-core.yaml',s)
print('Contrats et préparation mis à jour')
