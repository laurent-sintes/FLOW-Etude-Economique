from pathlib import Path
import json,hashlib,datetime,statistics
R=Path.cwd(); D=R/'audits/2026-10-29-experimentation-estimation'
load=lambda f:json.loads((D/f).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
java=load('iteration-08-java-mesures.json'); ts=load('iteration-08-ts-mesures.json'); py=load('iteration-08-python-mesures.json')
# Conception de taille seulement. Aucun code metier FLOW produit ou repris.
models=[]
def model(owner,name,fields,refs):
 models.append(dict(owner=owner,name=name,fields=fields.split(),contract_refs=refs.split(),classification='schema_cible_estime_et_non_implemente'))
for name,fields in [
 ('OrganisationScope','id organisationId scopeType scopeKey'),('Source','id name organisationId enabled authenticationRef'),
 ('SourceContract','id sourceId schemaVersion subjectType mode scope manifestRequired enabled'),
 ('SchemaVersion','id subjectType version previousVersion effectiveFrom schemaChecksum'),
 ('AuthorityGrant','id sourceId subjectType fieldGroup scope validFrom validTo priority'),
 ('ExternalIdentity','id sourceId externalKey subjectType referenceId validFrom validTo'),
 ('ReferenceIdentity','id subjectType organisationId status createdAt'),
 ('ReferenceRevision','id referenceId revision sourceVersion validFrom validTo receivedAt contributionId payloadChecksum status previousId'),
 ('Contribution','id sourceId contractId mode receivedAt fingerprint sourceVersion status recordCount manifestHash scope correctionOf'),
 ('ContributionLine','id contributionId lineNumber externalKey subjectType inputHash status referenceRevisionId'),
 ('Dependency','id fromRevisionId targetReferenceId targetRevisionId linkType status'),
 ('Publication','id organisationId scope revision status createdAt manifestHash previousId'),
 ('Rejection','id contributionLineId field link code message cause status'),
 ('Correction','id sourceId originalContributionId newContributionId reason createdAt'),
 ('ConsumerUse','id consumerId referenceRevisionId createdAt releasedAt purpose'),
 ('ExportReceipt','id publicationId scope format checksum location confirmedAt'),
 ('ChangeEvent','cursor publicationId referenceRevisionId kind occurredAt organisationId'),
 ('RetentionRule','id subjectType versionsYears rejectedDays logsDays')]:model('REF07_IN',name,fields,'F01 F02 F03 F04 F10')
for owner,name,fields,refs in [
('REF07_VIEWS','Party','revisionId kind name registrationId carryingOrganisationId intercompanyStatus','F05'),
('REF07_VIEWS','PartyRole','id partyRevisionId role scope validFrom validTo','F05'),
('REF07_VIEWS','PartyLink','id fromPartyRevisionId toPartyRevisionId linkType validFrom validTo','F05'),
('REF07_VIEWS','Agreement','revisionId code kind scope validFrom validTo frozenAssortmentRevisionId paymentConditions ownershipConditions guarantee','F05'),
('REF07_VIEWS','AgreementParty','id agreementRevisionId partyRevisionId role','F05'),
('REF07_VIEWS','AgreementCommitment','id agreementRevisionId kind quantity unitId value currency conditionId','F05'),
('REF07_VIEWS','CreditProfile','revisionId partyRevisionId payerRevisionId riskClass scope limit currency restrictionConditionId','F05'),
('REF07_VIEWS','Product','revisionId code designation kind unitRevisionId operationalCharacteristics','F06'),
('REF07_VIEWS','Variant','revisionId productRevisionId code attributes','F06'),
('REF07_VIEWS','Unit','revisionId code dimension symbol precision','F06 F07 F08 F09'),
('REF07_VIEWS','UnitConversion','id fromUnitRevisionId toUnitRevisionId numerator denominator rounding validFrom validTo','F06 F07 F08 F09'),
('REF07_VIEWS','Catalog','revisionId code name scope conditionId priceBookRevisionId','F06'),
('REF07_VIEWS','CatalogMember','id catalogRevisionId productRevisionId variantRevisionId offerCode validFrom validTo','F06'),
('REF07_VIEWS','Assortment','revisionId code scope validFrom validTo','F06'),
('REF07_VIEWS','AssortmentMember','id assortmentRevisionId productRevisionId variantRevisionId included validFrom validTo','F06'),
('REF07_VIEWS','PlanningContext','revisionId kind name windowStart windowEnd attributes','F06'),
('REF07_VIEWS','ProductContext','id productRevisionId contextRevisionId validFrom validTo','F06'),
('REF07_VIEWS','PriceBook','revisionId code kind organisationId currency scope validFrom validTo','F06 F09'),
('REF07_VIEWS','PriceLine','id priceBookRevisionId subjectRevisionId unitRevisionId currency base amount conditionId agreementRevisionId offerRevisionId','F06 F09'),
('REF07_VIEWS','PriceTier','id priceLineId lowerInclusive upperExclusive amount basis','F06 F09'),
('REF07_VIEWS','TypedCondition','id ownerRevisionId parentId booleanOperator attribute predicate valueType scalarValue setValues intervalStart intervalEnd','F05 F06 F08 F09'),
('REF07_VIEWS','PackagingMaterial','revisionId code name unitRevisionId dimensions mass capacity attributes','F07'),
('REF07_VIEWS','ContainerType','revisionId materialRevisionId code length width height dimensionUnitId tareMass massUnitId maximumCapacity reusable','F07'),
('REF07_VIEWS','PackagingSpecification','revisionId code productRevisionId instruction maximumDepth','F07'),
('REF07_VIEWS','PackagingNode','id specificationRevisionId parentNodeId materialRevisionId containerRevisionId quantity unitRevisionId level','F07'),
('REF07_VIEWS','Compatibility','id fromRevisionId toRevisionId kind conditionId','F07'),
('REF07_VIEWS','InternalSupply','revisionId code name type unitRevisionId usage operationalAttributes','F08'),
('REF07_VIEWS','UsageRestriction','id supplyRevisionId usage scope conditionId','F08'),
('REF07_VIEWS','NetworkSite','revisionId code name kind address responsiblePartyRevisionId attributes','F09'),
('REF07_VIEWS','NetworkLink','id fromSiteRevisionId toSiteRevisionId kind responsiblePartyRevisionId validFrom validTo','F09'),
('REF07_VIEWS','Service','revisionId code name expectedOutcome unitRevisionId instructions','F09'),
('REF07_VIEWS','ServiceOffer','revisionId serviceRevisionId providerRevisionId eligibilityConditionId referenceLeadTime levelRevisionId','F09'),
('REF07_VIEWS','ServiceAccess','id offerRevisionId use contractVersion address protocol authenticationReference','F09'),
('REF07_VIEWS','ServiceLevel','revisionId name indicators conditions','F09'),
('REF07_VIEWS','ServiceArea','id offerRevisionId originSiteRevisionId destinationSiteRevisionId zone conditionId','F09')]:model(owner,name,fields,refs)
# Banque d'analogies: chaque borne est une mesure, sauf declarations de schema comptables directement.
anchors={
 'controller':{'range':[7,8,19],'unit':'bloc de controleur delegant','evidence':['AXSHARING_CONTROL','AXPACK_CONTROL','AXTOKEN_CREATE'],'reason':'Petits controleurs complets lus; mediane des mesures 7,8,8,15,19=8. Le service appele est dimensionne ailleurs.'},
 'rule':{'range':[30,37,48],'unit':'bloc de validation/requete metier','evidence':['AXPACK_SERVICE','AXUNIT_CONVERSION','AXSHARING_QUERY'],'reason':'Trois ensembles Java de traitement sans infrastructure complete : conditionnement30, unites37, partage/requete48. Classes de taille proposees, aucune regression statistique.'},
 'workflow':{'range':[30,48,74],'unit':'bloc orchestration et erreurs','evidence':['AXCSV_ROW_REPLAY','AXSHARING_QUERY','AXCSV_PROCESS'],'reason':'Du traitement ligne/rejeu30 a la combinaison requete48 et boucle transactionnelle CSV74. FLOW decompose ses garanties en plusieurs blocs distincts; aucun bloc ne vaut garantie acquise.'},
 'ui_action':{'range':[10,28,42],'unit':'callback avec etat et resultat','evidence':['TS-SEARCH:385-401','TS-SEARCH:175-226','TS-SEARCH:227-296','TS-SEARCH:312-384'],'reason':'Callbacks complets de chargement10, ouverture/recherche28 et action contextuelle42. Aucun multiplieur de lignes physiques; les proprietes d objet sont comptees explicitement.'}}
# Inventaire operationnel. Chaque nom represente un bloc de service, pas une capacite ni un ecran.
work=[]
def block(id,owner,refs,kind,names,why):
 names=names.split('|'); a=anchors[kind]['range']; work.append(dict(id=id,owner=owner,contract_refs=refs.split(),kind=kind,blocks=names,quantity=len(names),unit_range=a,size_range=[len(names)*x for x in a],basis=why,classification='estimation_ingenierie_par_analogie_non_calibree',language='Java'))
block('C01','COMMON07','F01 F10 F11','rule','normaliser_identite_oidc|extraire_organisations_et_portees|valider_role_action|construire_predicat_de_portee|masquer_diagnostics_sensibles|normaliser_erreur_API|journaliser_action_sensible|valider_limites_requetes','Glue applicatif et portees; OIDC, cryptographie, HTTP et stockage reutilisent les bibliotheques.')
block('C02','COMMON07','F01 F03 F10','workflow','configurer_transaction_et_timeouts|migrer_schema_et_valider_version|demarrer_et_verifier_dependances|publier_etat_sante_et_metriques|rendre_configuration_fail_closed','Seulement composition applicative, pas taille des frameworks ni scripts fournisseur.')
block('IN01','REF07_IN','F01','rule','valider_enveloppe_et_version|valider_manifeste_complet|valider_colonnes_csv|convertir_types_canoniques|empreinte_canonique|enregistrer_origine_et_resultat','Conversions bornees; les parseurs CSV et JSON restent des dependances.')
block('IN02','REF07_IN','F01 F04','workflow','recevoir_JSON_et_lot|charger_flux_CSV_par_blocs|creer_identite_lot_idempotent|mettre_en_file_et_lancer_job|persister_resultats_par_ligne|finaliser_lot_et_compteurs','Six blocs distincts, au-dela de la boucle import Axelor mesuree.')
block('IN03','REF07_IN','F02','rule','resoudre_cle_externe|valider_correspondance_declaree|valider_groupe_autorite|valider_domaine_source|comparer_versions_sources','Aucun rapprochement probabiliste; contraintes relationnelles partagees.')
block('IN04','REF07_IN','F02','workflow','attribuer_identite_stable|enregistrer_alias_sans_fusion|composer_champs_autorises|mettre_en_quarantaine_conflit_cle|mettre_en_quarantaine_conflit_version_autorite','Concurrence, origine et attribution d identite mises en blocs nouveaux; OSS donne seulement un ordre de taille de leurs operations.')
block('IN05','REF07_IN','F03','rule','verifier_intervalles_dates|resoudre_liens_versions|detecter_cycle_graphe|verifier_limites_profondeur|classifier_absence_ambiguite','Une detection de graphe partagee; SQL/collections standard utilises, preuve Odoo du simple appel cycle non dimensionnee comme algorithme complet.')
block('IN06','REF07_IN','F03','workflow','figer_revision_immutable|mettre_en_attente_dependances|retester_dependances_resolues|assembler_candidat_publication|verifier_coherence_ensemble|commuter_pointeur_atomique|retirer_absents_apres_manifeste|preserver_liens_historiques','Huit blocs nouveaux sur transactions relationnelles; le framework ne les fournit pas.')
block('IN07','REF07_IN','F04','rule','normaliser_rejet_champ_lien|grouper_rejets_par_cause|verifier_filiation_correction|identifier_lignes_deja_acceptees','Journal metier persiste distinct du journal technique Batch.')
block('IN08','REF07_IN','F04','workflow','persister_quarantaine|recevoir_correction_sourcee|relancer_lot_sur_checkpoint|exclure_lancement_concurrent|reprendre_apres_interruption|publier_correction_tardive','Checkpoints Batch reutilises; l etat metier, les cles et effets transactionnels restent nouveaux.')
block('V05','REF07_VIEWS','F05','rule','valider_partie_et_roles|verifier_liens_organisationnels|verifier_parties_accord|valider_portee_accord|valider_engagement_quantite_valeur|verifier_assortiment_fige|valider_profil_credit_recu|selectionner_accords_applicables|restituer_absences_et_conflits','Aucun calcul exposition, autorisation commande ou reliquat; unites/conditions generiques dimensionnees une fois VCOMMON.')
block('V06','REF07_VIEWS','F06','rule','valider_produit_variante|verifier_correspondances_usages|valider_offre_catalogue|verifier_membres_catalogue|valider_assortiment|verifier_membres_assortiment|valider_contexte_planification|verifier_fenetres_produit_contexte|valider_livre_tarif_produit|lier_offre_accord_tarif|restituer_references_marchandise','Contexte de planification absent du comparable direct07: bloc nouveau identifie, modele typé explicitement propose.')
block('V07','REF07_VIEWS','F07','rule','valider_matiere|valider_type_contenant|valider_specification|verifier_quantites_niveaux|verifier_dimensions_capacite|verifier_compatibilites|restituer_conditionnement','Cycles/dependances et unites partages references IN05/VCOMMON; aucun contenu physique.')
block('V08','REF07_VIEWS','F08','rule','valider_type_fourniture_equipement|verifier_usage_restrictions|verifier_correspondances_usages|restituer_fourniture','Validation restriction utilise le moteur type de VCOMMON sans le repayer.')
block('V09','REF07_VIEWS','F09','rule','valider_site|valider_relation_reseau|verifier_responsable_executant|valider_catalogue_prestation|valider_offre_prestataire|verifier_resultat_niveau_service|verifier_metadata_acces_sans_secret|valider_zone_periode|valider_livre_tarif_service|valider_bases_paliers|selectionner_candidats_service|restituer_ambiguite_et_connaissance','Pas de connecteur execute, prix engage ou disponibilite calculee.')
block('VCOMMON','REF07_VIEWS','F05 F06 F07 F08 F09','rule','valider_unite_dimension|valider_ratio_conversion|convertir_quantite_avec_arrondi|valider_devise_base_recue|valider_arbre_condition_type|evaluer_egalite_ensemble|evaluer_intervalle_date|composer_ET_OU_et_inconnu|valider_limites_paliers|restituer_origine_validite_contexte','Petits moteurs bornes explicites. Aucun eval/script libre; comparables Python ne sont pas convertis par multiplicateur.')
block('V10A','REF07_VIEWS','F10','rule','construire_filtres_types|valider_pagination_tri|resoudre_revision_a_date|verifier_contexte_applicable|encoder_curseur_durable|verifier_droit_utilisation_version|verifier_eligibilite_purge','Filtre securite commun C01 injecte sur chaque chemin, pas recopie de son implementation.')
block('V10B','REF07_VIEWS','F10','workflow','rechercher_detail_version|exporter_canonique_par_flux|lire_changements_par_curseur|enregistrer_utilisation_consommateur|liberer_utilisation_consommateur|preparer_export_avant_purge|confirmer_export|purger_sans_liens_proteges','Purge generique controles de liens internes/declarations, limite non-declarations conservee.')
endpoints={
 'F01':['recevoirJSON','recevoirCSV','etatLot','resultatsLot'],
 'F02':['lireSources','lireContrats','majContrat','lireAutorites','majAutorite','declarerCorrespondance'],
 'F03':['etatPublication','publierCandidat','retirerReference'],
 'F04':['listerRejets','detailRejet','soumettreCorrection','relancerLot'],
 'F05-F09':['rechercheReferences','detailReference','versionsReference','validiteContexte','relationsReference','membresReference','candidatsAccords','candidatsServices'],
 'F10':['exporter','lireChangements','declarerUtilisation','libererUtilisation','confirmerExport','demanderPurge']}
for f,names in endpoints.items():block('API_'+f,'REF07_IN' if f in ['F01','F02','F03','F04'] else 'REF07_VIEWS',('F05 F06 F07 F08 F09' if f=='F05-F09' else f),'controller','|'.join(names),'Points d entree minces vers services ci-dessus; types, schema et DTO dimensionnes separement.')
# Couche de persistance specifique: methodes de requete propres, CRUD standard non reimplemente.
block('PERSIST','REF07_IN','F01 F02 F03 F04 F10','rule','chercher_contribution_par_empreinte|verrouiller_identite_source|chercher_versions_conflictuelles|chercher_dependances_en_attente|parcourir_liens_pour_cycle|charger_manifest_et_absents|chercher_revisions_a_date|verifier_liens_proteges_pour_purge|lire_evenements_ordonnes|chercher_rejets_par_cause','Requetes et repository specifiques avec index coherents; transaction generale C02, aucune implementation JPA refaite.')
# Les mappers/classes/types et le format des champs sont dimensionnes explicitement.
field_count=sum(len(m['fields']) for m in models); class_count=len(models)
model_range=[field_count*4+class_count*6,field_count*5+class_count*10,field_count*6+class_count*14]
model_basis={'field_count':field_count,'model_count':class_count,'field_units':[4,5,6],'structure_units_per_model':[6,10,14],
 'explanation':'Par champ: declaration entite + declaration DTO + affectation lecture + affectation ecriture=4; centrale ajoute une annotation de mapping/contrainte, haute deux. Par modele: declaration entite, DTO, mapper, deux methodes et repository=6; centrale quatre lignes de configuration/import, haute huit. Accesseurs, equals/hashCode et constructeurs generes exclus; leurs annotations sont dans la partie structure. Aucune traduction XML ligne pour ligne. Les listes de champs sont une conception candidate, pas un schema fourni par le metier.',
 'range_reason':'Les bornes changent la densite de mapping/annotations et de configuration pour le meme schema, non le perimetre fonctionnel.',
 'measured_comparables':'Les declarations XML ProductPackaging (4 champs) et Unite/Conversion(7 champs) confirment le besoin de distinguer champs et moteur qui les interprete, sans prouver ce nombre cible.'}
# Composants UI communs comptes une seule fois. Squelette recherche/alertes/http/accessibilite comme analogies complètes.
common_ui_units=sum(f['total_logical'] for f in ts['files'])
ui_routes=[
 ('sources_autorites_contrats','F01 F02','selection_source|changer_schema|editer_contrat|verifier_autorite|enregistrer_autorite'),
 ('import_rejets_publication','F01 F03 F04','choisir_fichier|soumettre_import|suivre_lot|filtrer_rejets|soumettre_correction|relancer|publier|confirmer_retrait'),
 ('parties_accords_credit','F05','selectionner_role|consulter_accord|consulter_credit|suivre_assortiment_fige'),
 ('marchandise_catalogues_assortiments_contextes','F06','changer_sujet|choisir_contexte|filtrer_periode|parcourir_membres|consulter_prix_recu'),
 ('conditionnement','F07','ouvrir_arbre|selectionner_niveau|consulter_compatibilites|expliquer_unites'),
 ('fournitures','F08','filtrer_usage|consulter_restrictions|comparer_types'),
 ('services_tarifs','F09','parcourir_reseau|filtrer_eligibilite|consulter_tarif|consulter_metadata_acces|expliquer_ambiguite')]
ui=[]
for name,refs,actions in ui_routes:
 arr=actions.split('|'); u=anchors['ui_action']['range'];ui.append({'id':name,'contract_refs':refs.split(),'actions':arr,'quantity':len(arr),'action_size_range':[len(arr)*x for x in u],'classification':'estimation_ingenierie_par_analogie_TS'})
# Une representation de chaque champ cible; metadata partagee affichee une seule fois via composants, pas par objet.
render_fields=field_count
ui_fields=[render_fields*3,render_fields*4,render_fields*6]
ui_typeglue=[class_count*2,class_count*3,class_count*4]
ui_range=[common_ui_units+sum(x['action_size_range'][i] for x in ui)+ui_fields[i]+ui_typeglue[i] for i in range(3)]
source_annotations=sum(x['quantity']*2 for x in work if x['kind']=='controller')+len(work)
service_scaffold=[len(work)*4,len(work)*8,len(work)*12]
java_range=[sum(x['size_range'][i] for x in work)+model_range[i]+source_annotations+service_scaffold[i] for i in range(3)]
product=[java_range[i]+ui_range[i] for i in range(3)]
refs=['iteration-07-contrat-v1.1.json','iteration-07-perimetre.json','iteration-07-marche-preuves.json','iteration-07-spring-preuves.json','iteration-08-java-mesures.json','iteration-08-ts-mesures.json','iteration-08-python-mesures.json','iteration-08-java-compteur.cjs','iteration-08-compter-ts.cjs','iteration-08-compter-python.py']
result={
 'id':'iteration-08-taille','date':'2026-10-29','status':'taille_gelee_avant_lecture_M1_M2; estimation_d_ingenierie_conditionnelle_non_calibree',
 'scope':'Contrat iteration07 v1.1 complet, 6 capacites et socle commun; taille du logiciel produit estimee sous hypothese de schema, transformations entre versions non decrites et moyens de livraison/deploiement restant inconnus.',
 'contract_sha256':sha(D/'iteration-07-contrat-v1.1.json'),'independence':{'prior_M1_M2_read':False,'prior_results_decisions_read':False,'effort_output_produced':False,'human_review_claimed':False,'assistant_authorship':True,'method':'Nomenclature cible derivee du contrat avant tout acces aux efforts anterieurs. Taille non ajustee pour retrouver un effort.'},
 'measurement':{'type':'tailles de blocs OSS reellement lus et mesures, aucune mesure d effort','java_logical_proxy':sum(s['logical_units_proxy'] for s in java['samples']),'java_annotations_separate':sum(s['annotations_separate'] for s in java['samples']),'typescript_logical':sum(f['total_logical'] for f in ts['files']),'python_ast_statements':sum(f['logical_units'] for f in py['files']),'registries':refs[4:7],'repositories_verified':py['repository_checks'],'no_sum_as_FLOW_size':True},
 'counting_contract':{
 'unit':'ligne_source_logique_livree_estimee; KSLOC = unites/1000',
 'language_policy':'Java et TypeScript separes puis additionnes comme unites livrees selon convention explicite. Pas de ratio Python-vers-Java, pas de conversion de lignes XML en TypeScript; Python sert a examiner fonction/algorithme.',
 'java':'Proxy du compteur joint; declarations et controles inclus, braces seules, commentaires, lignes vides et continuations excludes. Pour champs cible, declarations DTO/entite et annotations explicites comptees, accesseurs generes exclus.',
 'typescript':'Instructions AST + declarations, proprietes d objets, elements et attributs JSX. Toutes categories disponibles; declaratif JSX n est pas cache dans le procedural.',
 'delivered_declarations':'Les declarations Java/TS ecrites par le developpeur sont incluses dans la taille source livree; XML/schema SQL/IaC/CI sont conserves separement et ne sont pas convertis arbitrairement.',
 'excluded':'Tests developpeur/QA, fixtures, donnees de reference, documentation, fichiers generes, bibliotheques tierces intactes et moteur Spring/PostgreSQL/React.',
 'COCOMO_qualification':'Entree de taille estimee possible pour une sensibilite COCOMO, pas une taille SEI certifiee ni une mesure de logiciel FLOW existant. La compatibilite de convention avec la calibration COCOMO choisie doit rester explicite; aucune valeur d effort calculee ici.'},
 'implementation_hypotheses':[
 'Application Spring modulaire et relationnelle; un repertoire de revisions partage et tables de sujets types, DTO et mappers explicites.',
 '53 schemas de donnees candidats au niveau technique; ce compte ne requalifie pas les 13 sujets natifs en 53 fonctions metier.',
 'Identite/provenance/versions portees une fois par le socle; mecanismes unitaires et conditions partages entre familles.',
 'Java21 avec accesseurs/constructeurs generes et annotations source; controller et repository Spring deleguent aux services.',
 'Interface React avec bibliotheque de composants clavier/etats usuels; sept parcours metier, aucun generateur universel de formulaires.',
 'Un fournisseur d identite et un fournisseur cloud, outils usuels; code des dependances intact non dimensionne comme travail neuf.'],
 'reutilisation':{
 'new_product_source':{'status':'estime','size_range':product,'all_business_code_is_new':True},
 'adapted_existing_source':{'status':'zero_justifie','ASLOC':0,'reason':'Aucun composant applicatif Axelor/Odoo/Tryton ni ancien prototype admis ou copie dans cette conception Spring; les analogies ne sont pas des adaptations.'},
 'unmodified_reused_libraries':{'status':'reutilise_sans_modification_hypothese','source_size':None,'included_in_new_source':False,'items':['Spring Boot/Web/Validation','Spring Data JPA/Hibernate','Spring Security OIDC','Spring Batch repository JDBC','PostgreSQL','React et composants UI usuels','parseurs JSON/CSV'],'boundary':'Le raccordement/configuration applicative figure dans C01/C02/IN01/IN02 et UI; ni taille totale des bibliotheques ni deduction ESLOC inventee.'}},
 'analogical_unit_bank':anchors,'schema_inventory':models,'schema_size':dict(model_basis,size_range=model_range),
 'backend_blocks':work,'backend_structure':{'source_annotations':source_annotations,'class_count':len(work),'scaffold_size_range':service_scaffold,'basis':'Une classe de service/controleur par groupe de blocs: package/imports/dependances declaratives 4/8/12 unites, une annotation classe par groupe; 2 annotations HTTP/droits par endpoint. Corps deja dimensionnes dans les blocs. Ce squelette est une hypothese syntaxique, non mesure de code FLOW.'},'ui':{'common_measured_analogy_units':common_ui_units,'common_components':['recherche_et_detail_partages','notifications_et_erreurs','client_http','adaptation_clavier'],'shared_count_once':True,'routes':ui,'field_rendering':{'field_count':render_fields,'units_per_field':[3,4,6],'size_range':ui_fields,'basis':'Syntaxe JSX cible: element + label + valeur=3; centrale ajoute etat=4; haute aide et erreur locales=6. Ce sont decompositions syntaxiques estimees; pas un ratio LOC/champ de productivite. Les composants communs gerent deja clavier/erreurs.'},'type_and_route_glue':{'model_count':class_count,'units_per_model':[2,3,4],'size_range':ui_typeglue,'basis':'Raccordement du type API et du composant detail, route/selection de rendu; types generes OpenAPI non recomptees.'},'size_range':ui_range,'declarative_separation':'Rendu JSX des champs et types/route explicitement separes; les callbacks contiennent des proprietes d objet, comme dans les mesures sources.'},
 'sizes':{'Java_new_product':java_range,'TypeScript_new_product':ui_range,'new_delivered_product_logical_SLOC':product,'new_delivered_product_KSLOC':[round(x/1000,3) for x in product],'adapted_ASLOC':0,'generated_source_included':0,'test_source_included':0,'range_meaning':'Basse/centrale/haute de densite d implementation du meme contrat et de cette conception; somme de bornes dependantes, non intervalle de confiance. Les tailles unitaires sont des analogies de code, la quantite de blocs et de champs une estimation d ingenierie.'},
 'separate_not_sized':[
 {'id':'TESTS','nature':'tests_developpeur_QA_et_charge','status':'exclu_de_la_taille_source_produit','size':None,'reason':'Pas de ratio tests/code invente; les activites de verification restent dans le perimetre d effort approprie du modele utilise, sans multiplier les SLOC de produit.'},
 {'id':'GENERATED','nature':'accesseurs_modeles_types_API','status':'exclu_par_convention','size':None,'reason':'Le code produit automatiquement n est pas du code nouveau ecrit; declarations source deja comptees. Hypothese de generation explicite, pas composant FLOW livre.'},
 {'id':'SCHEMA_SQL','nature':'DDL_migrations_indexes','status':'reste_inconnu_comptage_distinct','size':None,'reason':'53 schemas candidats, contraintes/indexes a etablir apres choix mappings. La logique Java de migration C02 est dimensionnee, pas les instructions SQL/IaC; ne pas affirmer que Java absorbe ce travail.'},
 {'id':'DELIVERY_SUPPORT','nature':'IaC_CI_sauvegarde_restauration_supervision','status':'reste_inconnu_contrat','size':None,'reason':'Fournisseur et modules standard non choisis, absence de corpus comparable lu pour scripts de trois environnements et exercice de restauration. Le contrat inclut leur mise en place; taille produit ne les couvre pas.'},
 {'id':'ADDITIONAL_TUNING','nature':'retravail_code_apres_essais_qualite_charge_securite','status':'incertitude_de_realisation_non_mesuree','size':None,'reason':'Le million d objets et les autres cibles sont inclus dans la conception; aucune execution ne prouve leur atteinte ni nombre d optimisations necessaires. Les bornes ne promettent pas cette atteinte.'}],
 'contract_coverage':{'F01':['IN01','IN02','API_F01'],'F02':['IN03','IN04','API_F02'],'F03':['IN05','IN06','API_F03'],'F04':['IN07','IN08','API_F04'],'F05':['V05','VCOMMON'],'F06':['V06','VCOMMON'],'F07':['V07','IN05','VCOMMON'],'F08':['V08','VCOMMON'],'F09':['V09','VCOMMON'],'F10':['V10A','V10B','C01','PERSIST','API_F10'],'F11':['ui'],'socle':['C01','C02','ui','SCHEMA_SQL','DELIVERY_SUPPORT'],'service_scenario':['C01','C02','IN02','IN06','IN08','PERSIST','TESTS','DELIVERY_SUPPORT','ADDITIONAL_TUNING']},
 'conclusion':{'measured':'Blocs Java, Python et React lus aux commits figes, avec plages et empreintes; ce ne sont pas des tailles FLOW.',
 'estimated':'Taille candidate du code produit decompose sur F01-F11, avec conception explicite; les transformations semantiques entre schemas canoniques non decrits restent en dehors du total de base. Utilisable pour analyser la sensibilite COCOMO du logiciel produit, a condition de conserver son statut non calibre et sa convention logique.',
 'contract_still_unknown':'Taille des transformations semantiques entre les deux versions canoniques, du declaratif SQL et des moyens techniques de livraison/reprise; effort associe non deduit du code produit. Ne pas presenter le calcul sur la seule taille produit comme couverture mesuree de tout le contrat initial.',
 'total_validated_contract_size':None,'conditional_product_size_available':True,'blanket_impossibility_claim':False,
 'no_effort_inference':'Aucun effort humain, ratio LOC/jour, coefficient de productivite ni gain IA calcule.'},
 'input_sha256':{f:sha(D/f) for f in refs},
 'reproduce':'Executer les trois compteurs Java/TS/Python puis ce script depuis C:/Dev/FLOW-Etude-Economique avec runtimes Node/Python explicites; verifier ensuite les hashes. Ce script ne lit aucun M1/M2/resultat/decision.'}
# Remplace references generiques de banque par identifiants effectivement ecrits par le compteur Java.
result['analogical_unit_bank']['java_sample_ids_available']=[x['id'] for x in java['samples']]
result['implementation_hypotheses'][1]=result['implementation_hypotheses'][1].replace('53',str(class_count))
result['separate_not_sized'][2]['reason']=result['separate_not_sized'][2]['reason'].replace('53',str(class_count))

result['separate_not_sized'].insert(0,{'id':'CANONICAL_VERSION_DELTA','nature':'transformations_deux_versions_canoniques','status':'reste_inconnu_contrat','size':None,'reason':'Le contrat requiert deux versions, schemas et conversions annonces; il ne decrit pas les differences semantiques entre vCourante et vPrecedente. Validation du numero/schema, persistance et migrations applicatives sont dans IN01/C02; transformer les contenus de sujets est un travail distinct encore inconnu. Pas de conversion gratuite supposee.'})
result['contract_coverage']['F01'].append('CANONICAL_VERSION_DELTA')
result['sizes']['base_is_complete_contract_size']=False
result['sizes']['functional_scope_same_for_low_central_high']=True
result['sizes']['range_meaning'] += ' Les memes inconnues explicites restent hors des trois bornes; elles ne sont pas supposees nulles.'
result['sensitivities_only']=[{'id':'SENS_VERSION_CONVERTERS','label':'Sensibilite de taille seulement, ne ferme pas l inconnue','actual_size':None,'hypothesis':'13 convertisseurs de sujet, chacun de taille rule (30/37/48 unites) si les ecarts sont des transformations locales bornees; aucune preuve que ce serait suffisant pour les schemas reels.','target_quantity':13,'logical_sloc_addition':[390,481,624],'source_anchor_refs':['AXPACK_SERVICE','AXUNIT_CONVERSION','AXSHARING_QUERY'],'effect_on_base_product_logical_sloc':[product[0]+390,product[1]+481,product[2]+624],'included_in_base':False}]
result['architecture_vs_requirement']={'fixed_contract':['6 capacites','13 sujets natifs','7 parcours','2 versions canoniques','publication coherente','reprise et concurrence','droits par portee','objectifs S1'], 'hypothetical_design':['53 types de donnees','360 champs proposes','167 blocs Java controles et requetes','25 classes/groupes de services-controleurs','34 callbacks UI','DTO et mappers explicites','bibliotheque de composants UI','rendu d un champ une fois via composants partages'], 'meaning':'Ces quantites techniques ne sont pas contenues dans le contrat ni mesurees dans un produit FLOW; elles constituent la conception candidate utilisee pour estimer la taille. Plusieurs architectures satisfaisant le meme contrat donneraient d autres tailles.'}
result['conclusion']['estimated_size_admission']='scenario_de_taille_conditionnel_seulement; ni_budget_valide_ni_garantie_d_atteinte_S1'
# Verification automatique des references, sommes et hashes des sources figees.
known={x['id'] for x in java['samples']}
for name,bank in anchors.items():
 if isinstance(bank,dict):
  for ref in bank.get('evidence',[]):
   if not ref.startswith('TS-'):assert ref in known,ref
for f in py['files']:assert sha(R/f['cache_path'])==f['sha256']
for f in ts['files']:assert sha(R/f['cache_path'])==f['sha256']
for f in java['samples']:assert sha(R/f['path'])==f['sha256']
assert product==[java_range[i]+ui_range[i] for i in range(3)]
assert len({x['name'] for x in models})==len(models)
assert all(v[0]<=v[1]<=v[2] for v in [product,java_range,ui_range])
result['limits_of_transposition']=['Echantillon de code choisi pour pertinence fonctionnelle; non aleatoire et non representatif de tout un ERP. Les tailles des blocs ne sont pas une distribution de productivite.', 'Les analogies Axelor portent des dependances au framework non mesurees; celles-ci sont remplacees par les primitives Spring et par les raccordements cibles explicites. Leur adequation reste une hypothese.', 'Le classement de chacun des blocs cibles en controller/rule/workflow est un jugement d ingenierie assiste par IA, non une mesure ni une regle statistique.', 'La densite logique depend du style Java, des DTO et composants UI. Les conventions Java et TS sont explicites mais non certifiees identiques a la convention du corpus de calibration COCOMO.', 'S1 exige encore essais fonctionnels, concurrence, reprise, charge et securite. Aucun objectif nest declare atteint.']
result['validation']={'arithmetic_checked':True,'source_hashes_checked':True,'proof_ids_checked':True,'duplicate_target_models':False,'prior_estimates_read':False,'human_validation':False,'syntax_and_logic_limits_retained':True}

(D/'iteration-08-taille.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'models':class_count,'fields':field_count,'backend_service_blocks':sum(x['quantity'] for x in work),'UI_actions':sum(x['quantity'] for x in ui),'size':result['sizes'],'sha256':sha(D/'iteration-08-taille.json')},ensure_ascii=False,indent=2))
