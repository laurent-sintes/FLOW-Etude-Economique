"""Adopt six disjoint coherent units, preserving the existing three decisions and contracts."""
from pathlib import Path
from copy import deepcopy
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
import yaml
from estimation_inputs import digest,historical_dependencies
from capability_catalog import analysis,native
def read(p):return yaml.safe_load(p.read_text(encoding='utf-8-sig'))
def js(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def write(p,d):p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
def main():
 old=js(OUT/'baseline.json');retained=read(ROOT/'source/estimations-core-retenues.yaml');reg=read(ROOT/'source/calculs-estimation-core.yaml')
 require=lambda ok,msg:None if ok else (_ for _ in ()).throw(ValueError(msg))
 require(retained['units']==old['units'],'Existing decisions changed before adoption')
 require(reg['calculations']==old['calculations'],'Existing contracts changed before adoption')
 source=ROOT/'audits/2026-10-30-chiffrage-complet';d=js(source/'iteration-08/inputs.json');r=js(source/'iteration-08/results.json');fund=js(source/'iteration-08/funding.json')
 ids={'controls':'supply-controls-java-spring','orders':'orders-java-spring','planning':'master-plan-java-spring','decisions':'supply-decisions-java-spring','services':'service-fulfilment-java-spring','processes':'process-management-java-spring'}
 rates={x['id']:x for x in retained['units'][0]['roles']}
 labels={k:v['label'] for k,v in rates.items()}
 blocks=analysis()['blocs'];bycap={x['id']:x for x in blocks};nodes={x['id']:x for x in native()['nodes']}
 decision=dict(date='2026-10-30',status='retained',authorization='Adoption explicite par l’utilisateur des 4 160 JH Java/Spring, en conservant les trois décisions existantes.',
  total_jh=4160,existing_units={u['id']:dict(jh=u['total_jh'],months=u['months']) for u in old['units']},
  adopted_new_units=[dict(group=g['id'],id=ids[g['id']],total_jh=g['proposed_java_jh'],months=g['nominal_months'],roles=g['roles']) for g in r['economic_units']],
  archived_proposal_sha256=sha(source/'iteration-08/results.json'),common_280_included_not_added=True,no_global_schedule_inference=True)
 save(OUT/'decision.json',decision)
 # Register all new target mechanisms. Existing owners and mechanisms are unchanged.
 for m in fund['mechanisms']:
  reg['mechanisms'].append(dict(id='flow-'+m['id'],label=m['scope'],stack='java-spring',funding_owner=ids[m['economic_owner']],
   basis=dict(kind='complement_family',family=m['id']),note='Inclus dans l’unité propriétaire ; les consommateurs ne reconstruisent pas ce mécanisme. '+('Part commune de l’itération 4 intégrée, sans ajout des 280 JH.' if m['mode']=='included_common_work' else 'Comportement nouveau dimensionné par analogie, fraction supposée.')))
 owners={m['id']:m['funding_owner'] for m in reg['mechanisms']}
 old_common=js(ROOT/'audits/2026-10-30-mecanismes-partages-04/funding.json')
 family_groups={f:g['id'] for g in d['economic_units'] for f in g['families']}
 allocation_source=js(ROOT/'audits/2026-10-30-stock-consolidation-09/inputs.json')
 supplier=next(c for c in reg['calculations'] if c['id']=='stock-java-spring-v1')
 ni='audits/2026-10-30-propriete-stock-calcul-02/inputs.json';activities='audits/2026-10-30-master-data-calcul/repartitions-sources.json';productivity='audits/2026-10-30-master-data-calcul/entrees.json'
 dependency_names=set()
 for g in r['economic_units']:
  gid=g['id'];unitid=ids[gid];calcid=unitid+'-v1'
  caprows=[dict(id=c,native_id=bycap[c]['capacite_id']) for c in g['capabilities']]
  selected=[x for x in blocks if x['id'] in set(g['capabilities'])]
  common_path=[p for p in selected[0]['chemin'] if all(p in x['chemin'] for x in selected)]
  hierarchy=common_path[-1]
  roles=[]
  for role in g['roles']:
   roles.append(dict(role,rate_ref=deepcopy(rates[role['id']]['rate_ref']),rate_assumption='Tarif existant par analogie de profil ; compétence et devis à confirmer. Spécialités optimisation ou moteur comprises dans les rôles concernés.'))
  unit=dict(id=unitid,stack='java-spring',label=g['name']+' Java/Spring',status='retained',decision_date='2026-10-30',capabilities=caprows,total_jh=g['proposed_java_jh'],months=g['nominal_months'],method='COCOMO II',roles=roles,
   provenance=dict(path=(OUT/'decision.json').relative_to(ROOT).as_posix(),sha256=sha(OUT/'decision.json'),explanation='Décision issue de l’itération 8 ; tailles natives et modules Flow reconstruits au niveau de l’ensemble cohérent. Quatre références natives, contrôle COSMIC × ISBSG.'),
   role_assumption='Répartitions d’activités publiées conservées ; clés activités/rôles proposées. Les spécialités métier, optimisation et moteur sont à réunir dans ces budgets ; aucune équipe confirmée.',
   schedule=dict(unrounded_months=g['raw_months'],capacity_ref=deepcopy(old['units'][0]['schedule']['capacity_ref']),explanation='Délai nominal local COCOMO du seul ensemble cohérent. Il ne s’ajoute pas aux autres délais et ne remplace pas le calendrier global provisoire.',rule_ref='cocomo_schedule'),
   uncertainty=dict(confidence_level=None,low_jh=None,high_jh=None,status='unquantified',explanation='Stabilité de calcul après deux revues, sans calibration sur des charges réelles. Les indicateurs comparent les calculs ; ils ne mesurent pas une confiance ni un percentile. Fractions de modules, contraintes et garanties restent des hypothèses.'),
   includes=[g['reason']]+[f['scope'] for f in d['families'] if f['slug'] in g['families']]+['Tous rôles projet, tests développeur, QA, pilotage produit et adaptation technique inclus. Part commune financée ici intégrée dans les tailles.'],
   excludes=['Reconstruction du patrimoine Master Data, Stock et Propriété déjà financé.','Adaptations et connecteurs propres à Beaumanoir, financés dans l’intégration.','Reconstruction des noyaux de framework, solveurs ou moteur de processus disponibles.','Engagement de performance ou de calendrier global, réglementation douanière et comptabilité complètes, exécution physique chez les prestataires.'],
   assumptions=[
    dict(id='reuse',hypothesis='Réutiliser le patrimoine adopté et les bibliothèques ; réaliser les adaptations et contrôles Flow.',trigger='Un mécanisme fourni manque ou une autre architecture est retenue.',effect='Requalifier les analogues et le financement ; aucun rabais forfaitaire supplémentaire.'),
    dict(id='size',hypothesis='Modules, fractions et modèles issus des preuves figées de l’itération 8.',trigger='Un comportement distinct ou des contraintes changent significativement les volumes de code.',effect='Recalculer les tailles avant les JH ; aucune durée proposée ne sert d’entrée à l’effort.'),
    dict(id='grouping',hypothesis='Une estimation COCOMO pour cet ensemble cohérent, puis allocation entre ses familles.',trigger='Le découpage produit ou les dépendances changent.',effect='Recalcul non linéaire au nouveau niveau ; ne pas additionner des fragments et leur ensemble.'),
    dict(id='benchmark',hypothesis='Rendement COSMIC × ISBSG de 20 h/CFP non calibré à la réutilisation.',trigger='Un prototype ou un bilan réel comparable fournit une mesure de productivité.',effect='Réexaminer le contrôle ; les écarts actuels ne sont pas une précision prédictive.')
   ]+[dict(id='modules-'+f['slug'],hypothesis=f['slug']+' : '+str(f['quantity'])+' modules ('+' ; '.join(f['module_names'])+'), fraction '+str(f['extension_fraction'])+' du composant de référence par module.',trigger='Nombre ou taille des comportements nouveaux différents.',effect='Recalculer l’unité cohérente avec les nouveaux volumes.') for f in d['families'] if f['slug'] in g['families']],
   crosscheck=dict(method='COSMIC × ISBSG',jh=g['COSMIC']['jh'],explanation='Comptage à la frontière de cette unité, événements internes fusionnés ; 20 h/CFP, 7 h/JH, mêmes activités. Pas d’addition des CFP entre unités comme taille du Core complet.'),
   no_extra_ai_discount=True,no_extra_coordination=True,calculation=dict(id=calcid))
  funded=[dict(mechanism='flow-'+m['id'],mode='funded') for m in fund['mechanisms'] if m['economic_owner']==gid]
  consumed={'java-spring-framework-services','master-data-common-domain','master-data-admission','master-data-versions'}
  for claim in old_common['claims']:
   if family_groups.get(claim['family'])!=gid:continue
   mid=claim['mechanism'];mid=mid if mid in owners else 'flow-'+mid
   if mid in owners and owners[mid]!=unitid:consumed.add(mid)
  if gid in ('orders','planning','decisions','services'):consumed.add('stock-common-domain')
  if gid in ('controls','orders'):consumed.add('ownership-own-f04')
  claims=funded+[dict(mechanism=m,mode='consumed') for m in sorted(consumed) if owners[m]!=unitid]
  allocation=dict(id=calcid,selected_reference='axelor',rounding_jh=10,role_rounding_jh=1,day_hours=7,activity_role_weights=allocation_source['activity_role_weights'],scope=dict(unit=unitid,stack='java-spring',capabilities=g['capabilities']))
  allocation_path=(OUT/(gid+'-allocation.json')).relative_to(ROOT).as_posix();save(ROOT/allocation_path,allocation)
  cosmic_path=next(x['cosmic_ref'] for x in d['economic_units'] if x['id']==gid)
  specpath=(OUT/(gid+'-specification.json')).relative_to(ROOT).as_posix()
  inputs=dict(specification=specpath,archives=(OUT/'archives.json').relative_to(ROOT).as_posix(),native_inputs=ni,allocation=allocation_path,cosmic=cosmic_path,productivity_source=productivity,activities=activities,decision_evidence=(OUT/'decision.json').relative_to(ROOT).as_posix())
  spec=dict(id=calcid,recipe='coherent_components_v1',group_id=gid,families=next(x['families'] for x in d['economic_units'] if x['id']==gid),role_labels=labels,mechanism_prefix='flow-',
    native_labels=dict(erpnext='ERPNext + Frappe',odoo='Odoo Community',tryton='Tryton',axelor='Axelor + Open Platform / Studio'),
    analogue_calculation_id=supplier['id'],analogue_contract_sha256=digest(supplier),reused_mechanisms=sorted(consumed),
    input_hashes={p:sha(ROOT/p) for k,p in inputs.items() if k!='specification'})
  save(ROOT/specpath,spec)
  ev=[specpath,cosmic_path,inputs['archives'],inputs['decision_evidence']]
  comp=dict(activity_status='conventional',activity_note='Mêmes activités projet et conventions 152 h/mois, 7 h/JH ; phases COCOMO publiées et clés de rôle proposées conservées. Le taux historique ne calibre pas la réutilisation.',
   service_status='unverified',service_note='Volume, latence, concurrence et reprise ne sont pas appariés à des bilans réels. Les adaptations et garanties sont dimensionnées par analogie ; pas un engagement de service.',
   scope_rows=[
    dict(id='native',label='Composants natifs et périmètre métier',classification='shared',cocomo='Même compteur logique, base attribuée une seule fois puis calcul au niveau de l’ensemble.',cosmic='Processus et mouvements à la frontière de cet ensemble.',evidence=ev,decision='Comparaison descriptive ; aucun coût historique OSS observé.'),
    dict(id='new',label='Modules et contrats Flow nouveaux',classification='flow_specific',cocomo='Fractions et quantités explicites, structure des services et modèles/vues ajoutés.',cosmic='Les mouvements ne mesurent pas directement la difficulté des algorithmes ni chaque variante de contrat.',evidence=ev,decision='COCOMO II en référence, sans moyenne forcée avec le contrôle fonctionnel.'),
    dict(id='reuse',label='Patrimoine et mécanismes partagés',classification='shared',cocomo='Construction déjà financée consommée ; adaptations nouvelles financées une fois dans leur lot propriétaire.',cosmic='20 h/CFP ne sont pas calibrées au patrimoine fourni.',evidence=ev,decision='Les 280 JH communs sont absorbés dans les ensembles, sans ajout.'),
    dict(id='guarantees',label='Garanties sans équivalent natif complet',classification='unknown',cocomo='Dimensions nouvelles estimées par analogies de code.',cosmic='Deux dates et contraintes ne multiplient pas automatiquement les mouvements.',evidence=ev,decision='Hypothèses conservées et révision sur preuve ou changement significatif.'),
    dict(id='excess',label='Fonctions des exécutants et systèmes externes',classification='native_excess',cocomo='Analogues utilisés sans reconstruire leur WMS, moteur comptable ou réglementaire.',cosmic='Contrats de prestation et résultats, pas système complet de l’exécutant.',evidence=ev,decision='Hors du périmètre de construction du Core System retenu.')
   ])
  c=dict(id=calcid,unit_id=unitid,stack='java-spring',recipe='coherent_components_v1',
    scope=dict(level=nodes[hierarchy]['kind'],native_id=hierarchy,capabilities=caprows,native_source=read(ROOT/'source/referentiel-capacites.yaml'),analysis_sha256=digest(selected),decision_scope_sha256=digest({k:unit[k] for k in ('capabilities','includes','excludes')})),
    inputs=inputs,funding_claims=claims,comparison=comp,recipe_parameters=dict(scenario='central',structure_units_per_group=0))
  reg['calculations'].append(c);retained['units'].append(unit);dependency_names.update(inputs.values())
 # Evidence closure only includes actual calculation documents. Complete archived inputs are inside archives.json.
 todo=list(dependency_names)
 while todo:
  p=todo.pop()
  if p in reg['proofs']:continue
  value=js(ROOT/p) if p.endswith('.json') else read(ROOT/p)
  deps=historical_dependencies(p,value)
  reg['proofs'][p]=dict(sha256=sha(ROOT/p),kind='calculation_evidence',dependencies=[dict(path=k,sha256=h) for k,h in deps.items()])
  for dep,h in deps.items():
   require(sha(ROOT/dep)==h,'Evidence hash mismatch: '+dep)
   if dep not in reg['proofs']:todo.append(dep)
 require(sum(u['total_jh'] for u in retained['units'])==4160,'Adoption total')
 write(ROOT/'source/calculs-estimation-core.yaml',reg);write(ROOT/'source/estimations-core-retenues.yaml',retained)
 # Extend the typed preparation contract and canonical metamodel; formulas and previous instances are unchanged.
 schema=read(ROOT/'source/schema-calculs-estimation-core.yaml');cal=schema['properties']['calculations']['items']
 cal['properties']['recipe']['enum'].append('coherent_components_v1')
 names=['specification','archives','native_inputs','allocation','cosmic','productivity_source','activities','decision_evidence']
 inp=dict(type='object',properties={k:dict(type='string',minLength=1) for k in names},required=names,additionalProperties=False)
 cal['properties']['inputs']['oneOf'].append(inp)
 cal['allOf'].append({'if':{'properties':{'recipe':{'const':'coherent_components_v1'}}},'then':{'properties':{'inputs':inp}}})
 write(ROOT/'source/schema-calculs-estimation-core.yaml',schema)
 meta=read(ROOT/'source/fondamentaux.yaml');m=meta['estimation_model']
 m['rules'].append(dict(id='coherent_component_preparation',title='Préparer une unité de composants cohérents',expression='Reconstruire les atomes et analogues natifs, attribuer la base une seule fois, sommer les tailles des modules de l’unité puis appliquer COCOMO II une fois. Recompter COSMIC à la même frontière.',
  variables=dict(inputs='Contrat d’unité, archives complètes figées, mesures, modules, gabarits, allocations et comptage fonctionnel'),unit='contrôle',kind='algorithm',
  note='Les archives gzip/base64 sont des preuves complètes de stockage. Les fractions restent des hypothèses. Les allocations entre familles ne sont pas des estimations indépendantes par capacité.'))
 m['implementations'].append(dict(rules=['coherent_component_preparation'],path='tools/estimation_components.py'))
 m['invariants'].append('Les ensembles fortement liés sont estimés une fois sur leur taille totale ; ne pas cumuler leur charge et celle de leurs composants ou mécanismes communs.')
 write(ROOT/'source/fondamentaux.yaml',meta)
 print('Adopted 9 units, 4160 JH; previous three decisions and contracts unchanged.')
if __name__=='__main__':main()
