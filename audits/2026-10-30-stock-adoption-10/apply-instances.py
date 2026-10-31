from pathlib import Path
from copy import deepcopy
import json,hashlib,sys
ROOT=Path.cwd();sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
import yaml
from estimation_inputs import historical_dependencies,digest
from capability_catalog import analysis
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def yr(p):return yaml.safe_load((ROOT/p).read_text(encoding='utf-8'))
def jr(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def ys(p,v):(ROOT/p).write_text(yaml.safe_dump(v,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
def js(p,v):(ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def replace(p,a,b):
 f=ROOT/p;s=f.read_text(encoding='utf-8');assert a in s,(p,a);f.write_text(s.replace(a,b),encoding='utf-8',newline='\n')
reg=yr('source/calculs-estimation-core.yaml');md=yr('source/estimations-core-retenues.yaml')['units'][0]
prior=jr('audits/2026-10-30-stock-consolidation-09/results.json');alloc=jr('audits/2026-10-30-stock-consolidation-09/inputs.json');ni=jr('audits/2026-10-30-stock-opportunite-08/inputs.json')
caps=prior['scope']['capabilities'];blocs=[b for b in analysis()['blocs'] if b['id'] in caps]
caprefs=[dict(id=b['id'],native_id=b['capacite_id']) for b in blocs]
reused=['java-spring-framework-services','master-data-common-domain','master-data-admission','master-data-protection','master-data-reprise','master-data-versions','master-data-service'];products=ni['native_references']
manifest=dict(id='stock-java-spring-v1',recipe='native_component_analogies_v1',capabilities=caps,cocomo=ni['cocomo'],
 role_labels={r['id']:r['label'] for r in md['roles']},reference_labels={'erpnext':'ERPNext avec Frappe','odoo':'Odoo','tryton':'Tryton','axelor':'Axelor avec Open Platform'},reused_mechanisms=reused,
 perimeters={p:f'audits/2026-10-30-stock-composants-07/{p}-perimetre.json' for p in products},
 known_stock={p:f'audits/2026-10-30-stock-mesures-03/{p}-mesures.json' for p in products},
 chains={p:{k:f'audits/2026-10-30-stock-chaines-06/{p}-{k}.json' for k in ('correction','reservation')} for p in products},
 master_data_measures='audits/2026-10-30-master-data-comparable-reuse/measurements.json')
inputs=dict(specification='audits/2026-10-30-stock-adoption-10/inputs.json',native_inputs='audits/2026-10-30-stock-opportunite-08/inputs.json',
 native_measures='audits/2026-10-30-stock-adoption-10/measurements.json',allocation='audits/2026-10-30-stock-consolidation-09/inputs.json',
 baseline='audits/2026-10-30-stock-opportunite-08/results.json',cosmic='audits/2026-10-30-stock-completion-04/cosmic.json',
 productivity_source='audits/2026-10-30-master-data-calcul/entrees.json',activities='audits/2026-10-30-master-data-calcul/repartitions-sources.json',
 decision_evidence='audits/2026-10-30-stock-consolidation-09/results.json')
deps=set(inputs.values())-{inputs['specification']}
deps.update(manifest['perimeters'].values());deps.update(manifest['known_stock'].values())
deps.update(v for values in manifest['chains'].values() for v in values.values());deps.add(manifest['master_data_measures'])
manifest['input_hashes']={p:sha(p) for p in sorted(deps)};js(inputs['specification'],manifest)
roles=[]
for r in prior['roles']:
 original=next(x for x in md['roles'] if x['id']==r['id'])
 roles.append({**deepcopy(original),'jh':r['jh'],'rate_assumption':'Tarif existant utilisé par analogie de profil ; aucun devis spécifique Stock. Les rôles ne constituent pas neuf postes à plein temps.'})
unit=dict(id='stock-java-spring',stack='java-spring',label='Stock Java/Spring',status='retained',decision_date='2026-10-30',capabilities=caprefs,total_jh=340,months=10,method='COCOMO II',roles=roles,
 provenance=dict(path=inputs['decision_evidence'],sha256=sha(inputs['decision_evidence']),explanation='Référence Java/Axelor : 339,02 JH, arrondie à 340 JH. Base commune et compléments Flow après réutilisation de Master Data. Les quatre références sont conservées sans moyenne ; leurs désaccords restent visibles.'),
 role_assumption=prior['role_allocation_status'],
 schedule=dict(unrounded_months=prior['schedule']['unrounded_months'],capacity_ref=deepcopy(md['schedule']['capacity_ref']),explanation='Délai local Stock calculé à 10,44 mois, retenu à 10 mois. Travaux engagés avec les services Master Data nécessaires disponibles et une équipe nominale ; environ deux personnes en moyenne avec rôles partagés. Disponibilité non confirmée. Les délais locaux ne s’additionnent pas et ne remplacent pas le calendrier global provisoire.',rule_ref='cocomo_schedule'),
 uncertainty=dict(confidence_level=None,low_jh=None,high_jh=None,status='unquantified',explanation='Les écarts entre produits et méthodes et les sensibilités sont documentés. Ils ne fournissent pas une probabilité de dépassement ni un intervalle calibré.'),
 includes=['registre des mouvements et corrections','positions actuelles et datées et apports connus','inventaires, ajustements et engagements de quantité','compléments Flow de contribution, provenance, autorité, commandes et rapprochement après reprise','analyse, conception, réalisation et tests développeur','QA, revue de sécurité, pilotage local et préparation de mise en service'],
 excludes=prior['scope']['excludes'],
 assumptions=[
 dict(id='source-attribution',hypothesis='La taille Stock est attribuée aux composants natifs mêlés à des fonctions hors périmètre, avec plancher déjà mesuré et déduction du patrimoine Master Data.',trigger='Une part de code mixte sensiblement différente est nécessaire.',effect='Sensibilité isolée calculée : environ −106 / +111 JH autour des 339,02 JH non arrondis. Ni marge ni intervalle de confiance.'),
 dict(id='flow-modules',hypothesis='Les sept compléments Flow restent aux fractions explicites des chaînes et composants natifs ; 17 structures et 124 champs nouveaux ou étendus.',trigger='Protocoles, contributions ou règles de commande plus riches que les analogies retenues.',effect='Variation conjointe des fractions des sept modules : environ −52 / +84 JH, sans modifier les schémas ni cumuler d’autres sensibilités.'),
 dict(id='reuse',hypothesis=alloc['framework_assumption'],trigger='Patrimoine Master Data indisponible ou reconstruction d’un service générique.',effect='Estimation à rouvrir. Les mécanismes communs gardent leur propriétaire Master Data ; aucun coût forfaitaire de framework ajouté au Stock.'),
 dict(id='ui',hypothesis='Composants de consultation, formulaires et administration réutilisables, sans interface WMS sur mesure.',trigger='Poids des modèles et vues différent ou interface métier plus riche.',effect='Sensibilité du poids du déclaratif : environ −49 / +99 JH. Un parcours ajouté modifie le périmètre et demande une nouvelle estimation.'),
 dict(id='architecture',hypothesis='Une base transactionnelle et un module Stock ; protection et reprise communes réutilisées, rapprochements Stock spécifiques inclus.',trigger='Réservation distribuée, plusieurs régions actives ou engagement de débit, latence ou reprise plus exigeant.',effect='Effet non chiffré. Les objectifs Master Data ne démontrent pas les garanties du Stock ; revoir architecture et qualification avant engagement.'),
 dict(id='team',hypothesis='Équipe nominale maîtrisant Java/Spring et le patrimoine réutilisé, décision métier et experts disponibles.',trigger='Compétences ou disponibilité inférieures à l’hypothèse.',effect='Sensibilité isolée de capacité : environ −58 / +88 JH. Le délai dépend aussi des dépendances et de l’affectation réelle des rôles.'),
 dict(id='comparison',hypothesis='COCOMO II reste la référence ; le contrôle COSMIC × ISBSG conserve 169 CFP et 20 h/CFP.',trigger='Nouvelles mesures de taille, de comptage ou référence de productivité applicable.',effect='Le contrôle reste à 482,86 JH, environ 42 % au-dessus de Java. Écart non réconcilié ; pas de moyenne ni correction pour forcer l’accord.')],
 crosscheck=dict(method='COSMIC × ISBSG',jh=prior['functional_control']['jh'],explanation='169 CFP × 20 h/CFP ÷ 7 h/JH. Benchmark général historique, réutilisation Master Data non calibrée et activités imparfaitement appariées ; écart descriptif conservé.'),
 no_extra_ai_discount=True,no_extra_coordination=True,calculation={'id':'stock-java-spring-v1'})
assert sum(r['jh'] for r in roles)==340 and md==jr('audits/2026-10-30-stock-adoption-10/baseline.json')['retained_master_data']
f=ROOT/'source/estimations-core-retenues.yaml';f.write_text(f.read_text(encoding='utf-8').rstrip()+'\n'+yaml.safe_dump([unit],allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
for m in [dict(id='stock-common-domain',label='Fonctions Stock communes aux références',basis=dict(kind='component_domain',scope='ba-inventory-position-management'))]+[dict(id='stock-'+m['id'].lower(),label=m['reasoning'].split('.')[0],basis=dict(kind='complement_family',family=m['id'])) for m in ni['complement_module_analogies']]:
 m.update(stack='java-spring',funding_owner=unit['id'],note='Travaux spécifiques Stock uniquement ; les services génériques Master Data sont réutilisés et leur construction n’est pas financée à nouveau.');reg['mechanisms'].append(m)
def scope_row(id,label,classification,cocomo,cosmic,decision):
 return dict(id=id,label=label,classification=classification,cocomo=cocomo,cosmic=cosmic,evidence=[inputs['native_inputs'],inputs['cosmic'],inputs['decision_evidence']],decision=decision)
contract=dict(id='stock-java-spring-v1',unit_id=unit['id'],stack=unit['stack'],recipe=manifest['recipe'],
 scope=dict(level='area',native_id='ba-inventory-position-management',capabilities=caprefs,native_source=yr('source/referentiel-capacites.yaml'),analysis_sha256=digest(blocs),decision_scope_sha256=digest({k:unit[k] for k in ('capabilities','includes','excludes')})),inputs=inputs,
 funding_claims=[dict(mechanism=m['id'],mode='funded') for m in reg['mechanisms'] if m['funding_owner']==unit['id']]+[dict(mechanism=id,mode='consumed') for id in reused],
 comparison=dict(activity_status='conventional',activity_note='Sept activités COCOMO rapprochées des six activités ISBSG normalisées. Affectation des spécialistes et mise en service imparfaitement appariées ; le benchmark ne calibre pas la réutilisation Master Data.',service_status='unverified',service_note='Les garanties Stock de volume, concurrence, latence et reprise ne sont pas appariées aux projets historiques. Le résultat ne constitue pas un engagement de service.',
 scope_rows=[
 scope_row('common','Mouvements, positions, inventaires et engagements','shared','Composants natifs attribués au Stock après déduction Master Data.','Processus S01 à S16 proposés.','Périmètre rapproché par hypothèses, pas équivalence détaillée certifiée.'),
 scope_row('flow','Compléments de contribution et de cohérence Flow','flow_specific','Sept modules nouveaux par analogies explicites de code.','Processus proposés couvrant les faits, contrôles et fournitures.','Services Master Data réutilisés ; adaptation spécifique Stock incluse.'),
 scope_row('excess','Responsabilités natives mêlées au Stock','native_excess','Parts supposées retirant WMS, prix et autres fonctions. Odoo K2 conserve un analogue plus large.','Frontière du produit Flow, sans exécution physique ni valorisation financière.','Limite conservée ; les 534 JH Odoo ne prouvent pas un supplément Spring.'),
 scope_row('reuse','Réutilisation du patrimoine Master Data','shared','Propriétaire unique Master Data ; aucune seconde assimilation forfaitaire du framework.','169 CFP mesurent les services cibles ; le taux 20 h/CFP ne calibre pas ce patrimoine.','Une différence de productivité liée au patrimoine est plausible mais non quantifiée empiriquement.'),
 scope_row('guarantees','Concurrence, correction et reprise','unknown','Architecture transactionnelle standard et compléments de rapprochement.','Les contraintes internes ne produisent pas seules des CFP supplémentaires.','Écart de garanties non apparié ; pas de probabilité ni correction automatique.')]),
 recipe_parameters=dict(scenario='central',structure_units_per_group=0))
reg['calculations'].append(contract)
def register(path):
 if path in reg['proofs']:return
 v=jr(path) if not path.endswith('.py') else (ROOT/path).read_text(encoding='utf-8');deps=historical_dependencies(path,v)
 reg['proofs'][path]=dict(sha256=sha(path),kind='historical_code' if path.endswith('.py') else 'calculation_evidence',dependencies=[dict(path=p,sha256=h) for p,h in deps.items()])
 for p,h in deps.items():
  assert sha(p)==h,p
  register(p)
for path in inputs.values():register(path)
ys('source/calculs-estimation-core.yaml',reg)
status=yr('source/statut-evaluation.yaml')
status['core']['summary']='**Master Data et Stock Java/Spring sont retenus.** Les autres capacités Java, .NET et Rust restent à réestimer. Les totaux Make sont incomplets.'
status['core']['text']='**Les familles Master Data et Stock Java/Spring sont chiffrées et retenues.** Le reste de Java, .NET et Rust est à réestimer : zéro signifie absence de charge retenue, pas gratuité. Les totaux Make restent incomplets et ne permettent pas de conclure sur le choix Make / Buy. Intégration, maintenance, fonctionnement et offres Buy sont conservés. Les délais des familles ne s’additionnent pas et ne remplacent pas le calendrier provisoire du Core System complet. Les simulations personnelles conservent leurs paramètres.'
ys('source/statut-evaluation.yaml',status)
replace('config/application.yaml','**La charge retenue porte sur Master Data Java/Spring, tous rôles compris.**','**La charge retenue porte sur Master Data et Stock Java/Spring, tous rôles compris.**')
replace('config/application.yaml','Voir l’estimation Master Data et ses hypothèses','Voir les estimations retenues et leurs hypothèses')
replace('AGENTS.md','Master Data Java/Spring conserve 1 500 JH et 17 mois, sans double financement ni remise IA globale. Les autres capacités restent à réestimer','Master Data Java/Spring conserve 1 500 JH et 17 mois ; Stock Java/Spring est retenu à 340 JH et 10 mois, sans double financement ni remise IA globale. Les autres capacités restent à réestimer')
skill=Path('C:/Users/laure/.codex/skills/flow-evaluer-core-system/SKILL.md');s=skill.read_text(encoding='utf-8')
s=s.replace('recompose tailles, réutilisation, compléments et mouvements COSMIC depuis les mesures enregistrées.','sélectionne la préparation liée au contrat : réutilisation native et compléments, ou attribution de composants et analogies de modules via estimation_stock.py. Les tailles et mouvements COSMIC sont reconstruits depuis les mesures enregistrées, sans checkout OSS au chargement. Les parts de code et fractions de modules supposées restent distinctes des mesures observées et des scores de complexité.')
skill.write_text(s,encoding='utf-8',newline='\n')
local=ROOT/'skills/flow-evaluer-core-system/SKILL.md'
if local.is_file():local.write_text(s,encoding='utf-8',newline='\n')
print(json.dumps({'retained_stock':340,'months':10,'proofs':len(reg['proofs']),'mechanisms':len(reg['mechanisms'])}))
