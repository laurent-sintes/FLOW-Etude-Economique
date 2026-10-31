"""Freeze transparent opportunity assumptions; no adopted decision is changed."""
from pathlib import Path
import collections,hashlib,json,sys,yaml
R=Path.cwd();O=R/'audits/2026-10-30-audit-fonctions-transverses';sys.path[:0]=[str(R/'tools'),str(R/'tmp/model-deps')]
def j(p):return json.loads((R/p).read_text(encoding='utf-8'))
m=j(str(O.relative_to(R)/'components-measured.json'));impact=j('audits/2026-10-30-audit-comptage-cocomo/impact.json');md=j('audits/2026-10-30-master-data-comparable-reuse/measurements.json');mdidx={(x['repo'],x['path']):x for x in md['files']}
# Only documented Master Data reuse is credited here; an analogue consulted elsewhere is not a paid implementation.
for f in m['files']:
 old=mdidx.get((f['repo'],f['path']));f['existing_MD_credit_units']=0 if not old else min(f['program_units']+f['declarative_units'],old['program_units']+old['declarative_units'])*(0.035 if old['treatment']=='reused' else 1)
# Classify actual Master Data complement blocks for a work-based attribution, independent of project roles.
p=j('audits/2026-10-30-master-data-spring-flow/inputs.json');bank=j('audits/2026-10-30-master-data-spring-flow/analogues.json')['unit_bank'];revised={x['block']:x['proposed_units'] for x in j('audits/2026-10-30-master-data-spring-reprise/treatment-mapping.json')};itblocks=[]
for b in p['blocks']:
 if b['id'].startswith(('C01/','AUDIT/','API_AUDIT/','SERVICE/','ui_protection/','REPRISE/','API_REPRISE/','ui_reprise/')) or 'purge' in b['id'].lower():itblocks.append(dict(id=b['id'],logical_units=revised.get(b['id'],b['quantity']*bank[b['kind']]['range'][1])))
# The attribution is proportional to tagged implementation size, not a measured activity mix.
md_size=next(x for u in impact['units'] if u['id']=='master_data' for x in u['rows'] if x['id']=='axelor')['old_units'];md_it_fraction=sum(x['logical_units'] for x in itblocks)/md_size
c=p['cocomo'];params={k:c[k] for k in ['A','B','SF_sum','C','D','month_hours','day_hours','effort_phase_factor','schedule_phase_factor','other_EM','SCED']}
group_params={
 'process-studio':dict(fraction=.5,test_values=[.3,.7],basis='Un studio autonome à langage borné avec publication/versions et adaptation Temporal ; analogue complet Axelor, dont API, validation et UI. Moitié de module équivalent proposée pour les liaisons Flow ; bibliothèques graphiques et moteur fournis. Ce coefficient est une hypothèse de taille, pas une observation de charge ni une norme COCOMO.'),
 'human-forms':dict(fraction=.5,test_values=[.3,.7],basis='Un portail de tâches, modèles de formulaires, rendu, affectation et suivi. Réutilisation du contrat de tâche déjà financé ; moitié du composant complet comme analogue du travail nouveau de composition. Le bloc ancien human-work sera remplacé, pas cumulé.'),
 'analytics-mining':dict(fraction=.75,test_values=[.5,1.25],basis='Couche Flow de collecte/corrélation, modèle de données, variantes, durées, conformité et tableaux de bord. Bibliothèques PM4JS et moteur Superset fournis. Le code de graphe le plus complet des quatre suites sert de minimum de taille de la couche spécifique, jamais de preuve de Process Mining natif.'),
 'supply-workbenches':dict(fraction=2.4,test_values=[1.6,3.2],basis='Trois ateliers réutilisant le même cadre : planifier, comparer/expliquer les décisions, suivre l’exécution des prestations. Trois compositions à 0,8 module visuel chacune ; commandes/calculs métier déjà financés et non refacturés. Taille supposée, pas preuve de réalisation de ces ateliers.'),
 'admin-security':dict(fraction=.5,test_values=[.3,.7],basis='Consoles produit pour droits contextualisés, configuration, navigation et contrôles ; Keycloak/Spring Security fournissent les noyaux. Fonctions Master Data déjà financées déduites. Moitié du composant comme taille de composition/adaptation à Flow.'),
 'operations-lifecycle':dict(fraction=.65,test_values=[.4,.9],basis='Console de traitements/reprise, politiques de purge avec dépendances, audit, migrations et contrôle de restauration. DB, sauvegarde, CI et métriques fournis ; travail produit nouveau estimé à 0,65 composant, après crédit Master Data.'),
 'data-services':dict(fraction=.4,test_values=[.25,.6],basis='Interfaces génériques d’import/export, pièces et notifications, langues et contrôles de livraison. Conservation des traitements métier et reprises Master Data ; 0,4 composant pour l’administration/composition restante.')}
# Forecast COSMIC: explicit triggering events and data groups. These are requirements assumptions, not certified counts.
processes={}
def cp(g,id,label,E,Rd,W,X,overlap='new'):
 processes.setdefault(g,[]).append(dict(id=id,label=label,E=E,R=Rd,W=W,X=X,scope=overlap))
for id,label,E,rd,W,X in [
 ('edit','Enregistrer un modèle de processus',['modele'],['version','catalogue_actions','droits'],['brouillon','audit'],['resultat']),
 ('validate','Valider un parcours',['demande'],['brouillon','schemas','contraintes_execution'],['diagnostic'],['rapport']),
 ('publish','Publier une version exécutable',['publication'],['modele','droits','contrats_actions'],['version','liaison_runtime','audit'],['resultat','notification']),
 ('preview','Prévisualiser un parcours',['demande'],['modele','formulaires','catalogue_actions'],[],['parcours','diagnostic']),
 ('migrate','Préparer une migration des instances',['demande'],['versions','instances','points_attente'],['plan_migration'],['impact','rejets']),
 ('apply-migration','Appliquer une migration autorisée',['accord'],['plan_migration','droits','instances'],['etat_migration','audit'],['resultat']),
 ('rollback','Retirer ou restaurer une version',['demande'],['versions','instances','droits'],['etat_publication','audit'],['resultat'])]:cp('process-studio',id,label,E,rd,W,X)
for id,label,E,rd,W,X in [
 ('design','Enregistrer un modèle de formulaire',['modele'],['types_champs','droits'],['version_formulaire','audit'],['resultat']),
 ('preview','Prévisualiser un formulaire',['demande'],['modele','donnees_exemple'],[],['rendu','diagnostic']),
 ('publish','Publier un formulaire lié à une tâche',['demande'],['version','contrat_tache','droits'],['liaison_version','audit'],['resultat']),
 ('inbox','Consulter la corbeille de travail',['filtres'],['taches','affectations','droits'],[],['liste','indicateurs']),
 ('claim','Prendre ou déléguer une tâche',['commande'],['tache','droits','identites'],['affectation','audit'],['resultat']),
 ('complete','Soumettre le résultat et pièces',['resultat','pieces'],['contrat_tache','version_formulaire','droits'],['resultat_tache','audit'],['reponse']),
 ('history','Consulter le parcours d’une tâche',['demande'],['tache','journal','droits'],[],['parcours'])]:cp('human-forms',id,label,E,rd,W,X)
for id,label,E,rd,W,X in [
 ('trace-contract','Déclarer les correspondances des événements',['correspondances'],['schemas','droits'],['version_contrat','audit'],['diagnostic']),
 ('ingest','Charger et corréler un lot de traces',['lot_traces'],['contrat','positions','droits'],['traces_correlees','rejets'],['resultat']),
 ('discover','Lancer une analyse de variantes',['demande'],['traces','configuration','droits'],['execution','resultat_analyse'],['variante','mesures']),
 ('conformance','Vérifier la conformité à un modèle',['demande'],['modele','traces','droits'],['analyse_conformite'],['ecarts','mesures']),
 ('dashboard','Configurer et partager un tableau',['configuration'],['mesures','droits','modeles'],['tableau','partage','audit'],['resultat']),
 ('drilldown','Consulter indicateurs et dossiers liés',['filtres'],['indicateurs','droits','liens_dossiers'],[],['tableau','detail']),
 ('export','Exporter un résultat d’analyse',['demande'],['resultat_analyse','droits'],['audit'],['export'])]:cp('analytics-mining',id,label,E,rd,W,X)
for id,label,E,rd,W,X in [
 ('layout','Enregistrer une vue et ses filtres',['vue'],['droits','champs'],['preferences'],['resultat']),
 ('plan','Composer visuellement un plan et examiner les conflits',['commande'],['plan','contraintes','resultats'],['brouillon'],['visualisation','conflits']),
 ('compare','Comparer des propositions de décision',['selection'],['propositions','contraintes','justifications'],[],['comparaison','explication']),
 ('service','Consulter une exécution de prestation',['filtres'],['prestations','plans','alertes'],[],['calendrier','dossier']),
 ('act','Confirmer une modification depuis l’atelier',['commande'],['version','droits','resultat_controle'],['commande_admise','audit'],['resultat'])]:cp('supply-workbenches',id,label,E,rd,W,X)
for g,items in {
 'admin-security':[('rights','Administrer et tester des droits contextualisés',['politique'],['identites','modeles','droits'],['politique_version','audit'],['resultat','simulation']),('config','Modifier des paramètres validés',['configuration'],['schema','droits'],['version_configuration','audit'],['diagnostic']),('sessions','Consulter et révoquer des sessions',['demande'],['identites','sessions','droits'],['revocation','audit'],['resultat']),('nav','Configurer les espaces de travail',['espace'],['menus','droits'],['espace_version'],['resultat']),('security','Examiner et traiter une alerte sécurité',['action'],['alertes','droits','contexte'],['traitement','audit'],['resultat'])],
 'operations-lifecycle':[('jobs','Consulter et relancer un traitement',['action'],['execution','droits','contrat_rejeu'],['relance','audit'],['resultat']),('purge','Préparer puis confirmer une purge',['commande'],['politique','dependances','droits'],['plan_purge','preuve'],['impact','resultat']),('restore','Vérifier et clôturer une restauration',['commande'],['sauvegarde','manifeste','droits'],['controle_reprise','audit'],['rapport']),('upgrade','Exécuter et contrôler une migration',['demande'],['version','droits','etat_schema'],['execution_migration','audit'],['diagnostic']),('diagnose','Consulter les diagnostics de santé',['filtres'],['sante','metriques','droits'],[],['diagnostic']),('audit','Rechercher et exporter l’audit',['filtres'],['audit','droits'],['preuve_export'],['resultat'])],
 'data-services':[('import','Configurer et lancer un import administré',['lot','correspondances'],['schema','droits'],['execution','diagnostic'],['resultat']),('export','Enregistrer et exécuter un export',['definition'],['schema','donnees','droits'],['definition_export','audit'],['fichier']),('files','Administrer une pièce protégée',['fichier','commande'],['droits','politique_stockage'],['metadonnees','etat_scan'],['resultat']),('delivery','Examiner et relancer une notification',['action'],['file_envoi','droits'],['etat_livraison','audit'],['resultat']),('templates','Modifier un modèle de notification',['modele'],['variables','droits'],['version_modele'],['previsualisation']),('language','Configurer langue et formats',['configuration'],['langues','droits'],['preferences'],['resultat'])]
}.items():
 for args in items:cp(g,*args)
# Replaced functional counts: former human-work and intelligence, retrieved from adopted archive, below.
from estimation_components import unpack_archives
ar=unpack_archives(j('audits/2026-10-30-core-adoption-09/archives.json'))
(O/'archive-topology.json').write_text(json.dumps({k:type(v).__name__ for k,v in ar.items()},indent=2),encoding='utf-8')
inputs=dict(version=1,id='professional-product-java-spring',status='proposal_not_adopted',stack='java-spring',measurements=m,code_audit=impact,cocomo=params,groups=group_params,cosmic=dict(processes=processes,hours_per_CFP=20,day_hours=7,factor=1,status='forecast_requirements_assumptions_not_certified',deduplication='Les anciennes fonctions human-work et intelligence sont remplacées en entier. Les demandes déjà incluses en Master Data doivent être retirées des ajouts ; seules les nouvelles consoles sont comptées ici.',ISBSG_limit='20 h/CFP est le benchmark historique général déjà utilisé, non calibré sur ces interfaces, la réutilisation, Temporal ou Flow. Les JH couvrent les mêmes activités projet ; pas une mesure indépendante de productivité.'),md_partition=dict(tagged_blocks=itblocks,tagged_units=sum(x['logical_units'] for x in itblocks),denominator_units=md_size,fraction=md_it_fraction,basis='Hypothèse de ventilation de travaux : taille des blocs Master Data de sécurité/audit/purge/reprise technique divisée par la taille totale qui a fondé les 1 500 JH. Répartir proportionnellement chaque rôle conserve ses JH ; cette part n’est pas une mesure de coût historique. Les autres unités consomment ces mécanismes et ne les financent pas à nouveau.'),roles_business={'coordination':.11,'analyse_produit':.11,'architecture':.09,'dev_java':.21,'dev_frontend':.25,'qa':.14,'plateforme':.04,'ux':.03,'securite':.02},roles_it={'coordination':.10,'analyse_produit':.06,'architecture':.10,'dev_java':.28,'dev_frontend':.12,'qa':.16,'plateforme':.12,'ux':.02,'securite':.04},assumptions=[
 'Produit générique à base transactionnelle commune ; architecture modulaire, deux instances applicatives et services de base de données/CI/sauvegarde disponibles. Intégration spécifique Beaumanoir et exploitation annuelle restent dans leurs budgets distincts.',
 'Temporal OSS exécute les workflows ; langage métier borné (séquence, choix, attente, parallélisme borné, temporisation, tâche humaine et appels de services). Aucune conformité complète BPMN 2.0 ni nouveau moteur de workflow construit.',
 'PM4JS réutilisé pour découverte/conformité, Superset pour tableaux de bord ; leur noyau est disponible. UI des analyses, traces métier, autorisations, adaptateurs et vérification sont financés. PM4Py est une alternative, sans cumul.',
 'Les studios servent à composer des comportements permis, pas à générer librement une application ni du code arbitraire ; catalogue de types de formulaires et d’actions borné.',
 'Les rôles, tests développeur, QA, sécurité, préparation de livraison et pilotage produit sont dans les JH. Les proportions entre rôles sont des clés d’organisation proposées, distinctes des distributions d’activité publiées.',
 'Les fractions de composants sont des hypothèses de dimensionnement par analogie ; elles n’ont pas été calibrées sur des bilans de projets. Les mesures de code sont réelles, les tailles Flow sont estimées.',
 'Les garanties Master Data existantes sont conservées. Pas d’architecture multirégion active-active, certification réglementaire ou objectifs supplémentaires de volume/latence supposés gratuits.',
 'Le périmètre couvre les capacités reçues et les fonctions professionnelles inventoriées, avec limites explicites. Il ne démontre pas l’exhaustivité de toutes les exigences futures.'])
(O/'proposal-inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2),encoding='utf-8');print('MD IT fraction',md_it_fraction,'CFP per group',{g:sum(len(x[k]) for x in rr for k in ('E','R','W','X')) for g,rr in processes.items()});print('archive keys',list(ar))
