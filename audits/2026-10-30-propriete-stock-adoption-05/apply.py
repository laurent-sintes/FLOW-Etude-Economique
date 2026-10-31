"""Adopt the authorised Ownership decision without rewriting earlier evidence."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,sys
ROOT=Path.cwd();OUT=ROOT/'audits/2026-10-30-propriete-stock-adoption-05'
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
import yaml
from estimation_inputs import digest,historical_dependencies
def jr(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def yr(p):return yaml.safe_load((ROOT/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def js(p,v):(ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ys(p,v):(ROOT/p).write_text(yaml.safe_dump(v,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
def replace(path,a,b):
 p=ROOT/path;s=p.read_text(encoding='utf-8');assert a in s,(path,a);p.write_text(s.replace(a,b),encoding='utf-8',newline='\n')
reg=yr('source/calculs-estimation-core.yaml');decision=yr('source/estimations-core-retenues.yaml');before=jr('audits/2026-10-30-propriete-stock-adoption-05/baseline.json')
assert decision['units'][:2]==before['retained_units'] and len(decision['units']) in (2,3)
prior=jr('audits/2026-10-30-propriete-stock-consolidation-04/results.json')
allocation=jr('audits/2026-10-30-propriete-stock-consolidation-04/inputs.json')
ni=jr('audits/2026-10-30-propriete-stock-calcul-02/inputs.json')
stock=next(c for c in reg['calculations'] if c['unit_id']=='stock-java-spring')
caps=prior['scope']['capabilities'];blocs=[b for b in yr('source/analyse-perimetre-core.yaml')['blocs'] if b['id'] in caps]
caprefs=[dict(id=b['id'],native_id=b['capacite_id']) for b in blocs]
reused=['java-spring-framework-services','master-data-common-domain','master-data-admission','master-data-semantique',
 'master-data-protection','master-data-reprise','master-data-versions','master-data-service',
 'stock-common-domain','stock-stock-f01','stock-stock-f02','stock-stock-f03','stock-stock-f04','stock-stock-f05','stock-stock-f06','stock-stock-f07']
calc_id='inventory-ownership-java-spring-v1';unit_id='inventory-ownership-java-spring'
inputs=dict(specification='audits/2026-10-30-propriete-stock-adoption-05/inputs.json',
 native_inputs='audits/2026-10-30-propriete-stock-calcul-02/inputs.json',baseline='audits/2026-10-30-propriete-stock-calcul-02/results.json',
 allocation='audits/2026-10-30-propriete-stock-consolidation-04/inputs.json',
 cosmic='audits/2026-10-30-propriete-stock-calcul-02/cosmic.json',
 cosmic_refinement='audits/2026-10-30-propriete-stock-calcul-02/cosmic-refinement.json',
 productivity_source='audits/2026-10-30-master-data-calcul/entrees.json',
 activities='audits/2026-10-30-master-data-calcul/repartitions-sources.json',
 decision_evidence='audits/2026-10-30-propriete-stock-consolidation-04/results.json')
manifest=dict(id=calc_id,recipe='native_new_module_analogies_v1',capabilities=caps,cocomo=ni['cocomo'],
 role_labels={r['id']:r['label'] for r in decision['units'][0]['roles']},modules=[m['id'] for m in ni['hypotheses']['modules']],
 analogue_calculation_id=stock['id'],analogue_contract_sha256=digest(stock),reused_mechanisms=reused,
 input_hashes={p:sha(p) for p in set(inputs.values())-{inputs['specification']}})
js(inputs['specification'],manifest)
rates={r['id']:r for r in decision['units'][1]['roles']}
roles=[dict(id=r['id'],label=r['label'],jh=r['jh'],rate_ref=deepcopy(rates[r['id']]['rate_ref']),
 rate_assumption='Tarif existant utilisé par analogie de profil ; pas de devis spécifique. Les rôles sont mutualisés, sans neuf postes à plein temps.') for r in prior['roles']]
assumptions=[]
for a in prior['assumptions']:
 effect=a['impact']
 if a['id']=='ledger':effect='Sensibilité isolée du registre et des deux dates : environ 78 à 135 JH pour la famille, contre 98,92 JH au point de calcul. Ni enveloppe budgétaire ni intervalle de confiance.'
 if a['id']=='team':effect='Sensibilité isolée PERS : environ −17 / +26 JH autour des 98,92 JH non arrondis. Disponibilité des rôles et dépendances non confirmée.'
 assumptions.append(dict(id=a['id'],hypothesis=a['hypothesis'],trigger=a['trigger'],effect=effect))
assumptions.append(dict(id='comparison',hypothesis='COCOMO II reste la référence ; 80 CFP et 20 h/CFP restent le contrôle COSMIC × ISBSG.',
 trigger='Nouvelle mesure de taille ou donnée de productivité applicable.',effect='Le contrôle donne 228,57 JH, soit 129,66 JH et 131,08 % au-dessus des 98,92 JH Java. Désaccord conservé, sans moyenne ni correction automatique.'))
unit=dict(id=unit_id,stack='java-spring',label='Propriété du stock Java/Spring',status='retained',decision_date='2026-10-30',
 capabilities=caprefs,total_jh=100,months=7,method='COCOMO II',roles=roles,
 provenance=dict(path=inputs['decision_evidence'],sha256=sha(inputs['decision_evidence']),
 explanation='Calcul Java/Axelor à 98,92 JH, arrondi à 100 JH. Six modules nouveaux par analogie, après réutilisation de Master Data et Stock. Analogue du registre et des deux dates partiel ; la décision ne démontre pas une productivité Flow ni une convergence des méthodes.'),
 role_assumption=prior['role_allocation_status'],
 schedule=dict(unrounded_months=prior['schedule']['calculated_months_on_proposed_jh'],
 capacity_ref=deepcopy(decision['units'][0]['schedule']['capacity_ref']),
 explanation='Délai local calculé à 7,07 mois sur les 100 JH retenus, arrondi à 7 mois. Services Master Data et Stock nécessaires disponibles ; intervenants mutualisés, compétences nominales et disponibilité à confirmer. Les délais locaux ne s’additionnent pas et ne remplacent pas le calendrier global.',
 rule_ref='cocomo_schedule'),
 uncertainty=dict(confidence_level=None,low_jh=None,high_jh=None,status='unquantified',
 explanation='Les analogues sont partiels. Fractions de nouveau code et productivité non calibrées ; les écarts et sensibilités ne sont ni une confiance ni des probabilités.'),
 includes=['détermination générique des transferts de propriété et quantités, conditions reçues et passages entre parties',
 'actes éventuels, résultats et transferts reconnus ailleurs sans seconde décision',
 'registre autonome de propriété avec preuves, date d’effet et date de connaissance',
 'annulations, corrections expliquées et lectures aux deux dates',
 'rapprochement avec les faits et positions Stock, fourniture des positions de propriété',
 'analyse, conception, réalisation, tests développeur, QA et revue de sécurité',
 'coordination logicielle locale et préparation de mise en service'],
 excludes=prior['scope_exclusions'],assumptions=assumptions,
 crosscheck=dict(method='COSMIC × ISBSG',jh=prior['crosscheck']['jh'],
 explanation='80 CFP × 20 h/CFP ÷ 7 h/JH = 228,57 JH. Rendement historique non calibré sur le composant et sa réutilisation. Écart de +131,08 % par rapport aux 98,92 JH COCOMO non arrondis, non réconcilié.'),
 no_extra_ai_discount=True,no_extra_coordination=True,calculation={'id':calc_id})
assert sum(r['jh'] for r in roles)==100
p=ROOT/'source/estimations-core-retenues.yaml'
if len(decision['units'])==2:p.write_text(p.read_text(encoding='utf-8').rstrip()+'\n'+yaml.safe_dump([unit],allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
else:assert decision['units'][2]==unit
for m in ni['hypotheses']['modules']:
 reg['mechanisms'].append(dict(id='ownership-'+m['id'].lower(),label=m['name'],stack='java-spring',funding_owner=unit_id,
 basis=dict(kind='complement_family',family=m['id']),note='Nouveau comportement de propriété uniquement. Services génériques Master Data et Stock consommés, sans second financement.'))
def row(id,label,classification,cocomo,cosmic,note):
 return dict(id=id,label=label,classification=classification,cocomo=cocomo,cosmic=cosmic,
 evidence=[inputs['native_inputs'],inputs['cosmic'],inputs['decision_evidence']],decision=note)
contract=dict(id=calc_id,unit_id=unit_id,stack='java-spring',recipe=manifest['recipe'],
 scope=dict(level='business_area',native_id='ba-inventory-ownership-management',capabilities=caprefs,
 native_source=yr('source/referentiel-capacites.yaml'),analysis_sha256=digest(blocs),
 decision_scope_sha256=digest({k:unit[k] for k in ('capabilities','includes','excludes')})),
 inputs=inputs,funding_claims=[dict(mechanism='ownership-'+m['id'].lower(),mode='funded') for m in ni['hypotheses']['modules']]+[dict(mechanism=id,mode='consumed') for id in reused],
 comparison=dict(activity_status='conventional',
 activity_note='Sept activités COCOMO rapprochées des six activités ISBSG normalisées. Clés de rôles proposées ; spécialistes et mise en service imparfaitement appariés. Le rendement historique ne calibre pas la réutilisation Master Data et Stock.',
 service_status='unverified',service_note='Les garanties temporelles, de volume, de concurrence et de latence ne sont pas appariées aux projets historiques ; aucun engagement de service déduit des JH.',
 scope_rows=[
 row('new','Fonctions génériques de propriété','flow_specific','Six modules nouveaux par analogies de chaînes natives, modèles et vues spécifiques.','Neuf processus proposés, 80 CFP après distinction des passages de propriété.','Estimation d’opportunité, sans coût OSS observé.'),
 row('reuse','Patrimoine Master Data et Stock','shared','Construction déjà financée par les familles adoptées ; zéro JH supplémentaire de reconstruction, adaptations de propriété incluses.','80 CFP décrivent les services cibles ; le taux de 20 h/CFP ne calibre pas cette réutilisation.','Les analogues servent de règle de taille, pas de nouveau Stock livré.'),
 row('journal','Registre et lectures aux deux dates','unknown','Analogue Java partiel ; fractions de nouveau code de 1 et 0,75 chaîne de correction.','Corrections et lectures déjà comptées ; deux dates sont des attributs, pas deux copies des processus.','Pas d’équivalent natif complet démontré. Taille supposée maintenue comme hypothèse de décision.'),
 row('excess','Comptabilité et exécution logistique','native_excess','Témoins de journal comptable et chaînes Stock utilisés comme analogies ; pas une construction financière ou WMS.','Frontière de propriété, sans valorisation, facturation ni exécution physique.','Ces fonctions ne sont pas financées dans cette famille.')]),
 recipe_parameters=dict(scenario='central',structure_units_per_group=0))
reg['calculations'].append(contract)
def register(path):
 if path in reg['proofs']:return
 v=(ROOT/path).read_text(encoding='utf-8') if path.endswith('.py') else (yr(path) if path.endswith(('.yaml','.yml')) else jr(path))
 deps=historical_dependencies(path,v)
 reg['proofs'][path]=dict(sha256=sha(path),kind='historical_code' if path.endswith('.py') else 'calculation_evidence',
 dependencies=[dict(path=p,sha256=h) for p,h in deps.items()])
 for p,h in deps.items():
  assert sha(p)==h,p
  register(p)
for p in inputs.values():register(p)
ys('source/calculs-estimation-core.yaml',reg)
schema=yr('source/schema-calculs-estimation-core.yaml')
cs=schema['properties']['calculations']['items'];cs['properties']['recipe']['enum'].append(manifest['recipe'])
shape=dict(type='object',properties={k:dict(type='string',minLength=1) for k in inputs},required=list(inputs),additionalProperties=False)
cs['properties']['inputs']['oneOf'].append(shape)
cs['allOf'].append({'if':{'properties':{'recipe':{'const':manifest['recipe']}}},'then':{'properties':{'inputs':deepcopy(shape)}}})
ys('source/schema-calculs-estimation-core.yaml',schema)
meta=yr('source/fondamentaux.yaml');em=meta['estimation_model']
em['rules'].append(dict(id='funded_module_preparation',title='Dimensionner de nouveaux modules sur des analogues déjà financés',
 expression='Reconstruire les analogues du calcul propriétaire référencé, appliquer les fractions de modules nouveaux et leurs modèles ; ne pas ajouter le code déjà financé à la nouvelle famille.',
 variables={'inputs':'Contrat propre à la famille, preuves et contrat figé du fournisseur des analogues'},unit='contrôle',kind='algorithm',
 note='La dépendance au fournisseur et le propriétaire de financement sont explicites. Le contrôle de taille ne valide pas la suffisance des fractions ni la productivité.'))
em['implementations'].append(dict(rules=['funded_module_preparation'],path='tools/estimation_ownership.py'))
ys('source/fondamentaux.yaml',meta)
replace('tools/estimation_preparation.py',"    if contract['recipe'] == 'native_component_analogies_v1':","    if contract['recipe'] == 'native_new_module_analogies_v1':\n        from estimation_ownership import prepare_ownership\n        return prepare_ownership(documents, contract, registry, formula)\n    if contract['recipe'] == 'native_component_analogies_v1':")
for path in ['tools/study_snapshot.py','tools/retained_core.py']:
 replace(path,"'estimation_stock.py'" if path.endswith('study_snapshot.py') else "'tools/estimation_stock.py'",
 "'estimation_stock.py','estimation_ownership.py'" if path.endswith('study_snapshot.py') else "'tools/estimation_stock.py', 'tools/estimation_ownership.py'")
status=yr('source/statut-evaluation.yaml')
status['core']['summary']='**Master Data, Stock et Propriété du stock Java/Spring sont retenus.** Les autres capacités Java, .NET et Rust restent à réestimer. Les totaux Make sont incomplets.'
status['core']['text']=status['core']['text'].replace('Les familles Master Data et Stock Java/Spring','Les familles Master Data, Stock et Propriété du stock Java/Spring')
ys('source/statut-evaluation.yaml',status)
for p in ['config/application.yaml','source/lecture-evaluations-economiques.yaml']:
 replace(p,'Master Data et Stock Java/Spring','Master Data, Stock et Propriété du stock Java/Spring')
replace('AGENTS.md','Stock Java/Spring est retenu à 340 JH et 10 mois,','Stock Java/Spring est retenu à 340 JH et 10 mois ; Propriété du stock Java/Spring à 100 JH et 7 mois,')
note='\nLa préparation de nouveaux modules de propriété suit native_new_module_analogies_v1 dans tools/estimation_ownership.py. Elle reconstruit les analogues du contrat Stock figé, puis calcule uniquement le nouveau comportement de propriété. La propriété consomme les financements Master Data et Stock ; les clauses de réutilisation et les limites des lectures aux deux dates restent visibles. Les décisions adoptées et la somme des JH sont dérivées de leurs instances, sans somme des délais locaux.\n'
for p in ['source/README.md','tools/README.md']:
 f=ROOT/p;f.write_text(f.read_text(encoding='utf-8').rstrip()+'\n'+note,encoding='utf-8')
skill_paths=[Path('C:/Users/laure/.codex/skills/flow-evaluer-core-system/SKILL.md'),ROOT/'skills/flow-evaluer-core-system/SKILL.md']
for p in skill_paths:
 if not p.is_file():continue
 s=p.read_text(encoding='utf-8')
 s=s.replace('ou attribution de composants et analogies de modules via estimation_stock.py.',
 'attribution de composants et analogies de modules via estimation_stock.py, ou nouveaux modules de propriété via estimation_ownership.py. Cette dernière préparation reconstruit les analogues du contrat Stock figé, sans refacturer le patrimoine Master Data/Stock.')
 p.write_text(s,encoding='utf-8',newline='\n')
print(json.dumps(dict(adopted_jh=100,months=7,proofs=len(reg['proofs']),mechanisms=len(reg['mechanisms'])),ensure_ascii=False))
