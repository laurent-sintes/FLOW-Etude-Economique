from pathlib import Path
import json,hashlib,sys,importlib.util,statistics
sys.stdout.reconfigure(encoding="utf-8")
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
PRE=ROOT/"audits/2026-10-29-experimentation-estimation"
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def save(name,x):(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=read(PRE/"iteration-08-taille.json")
native=read(ROOT/"audits/2026-10-30-master-data-comparable-reuse/results.json")
native_inputs=read(ROOT/"audits/2026-10-30-master-data-comparable-reuse/inputs.json")
if not (OUT/"baseline.json").exists():
 paths=[p for base in ["source","config","app/src","app/scripts"] for p in (ROOT/base).rglob("*") if p.is_file()]
 save("baseline.json",{"files":{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)}})
spec=importlib.util.spec_from_file_location("counter",ROOT/"audits/2026-10-30-master-data-natif/measure.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
samples=[]
for s in read(PRE/"iteration-08-java-mesures.json")["samples"]:
 p=ROOT/s["path"];data=p.read_bytes(); tree=m.PARSERS[".java"].parse(data)
 assert sha(p)==s["sha256"]
 nodes=[n for n in m.walk(tree.root_node) if any(a<=n.start_point.row+1<=b for a,b in s["ranges"])]
 count=sum((n.type.endswith("_statement") and n.type!="empty_statement") or n.type in m.JAVA_EXTRA for n in nodes)
 samples.append({k:s[k] for k in ["id","path","ranges","sha256","commit"]}|{"program_units":count,"declarative_units":0})
ts=read(PRE/"iteration-08-ts-mesures.json")["files"][0];p=ROOT/ts["cache_path"];assert sha(p)==ts["sha256"]
tree=m.PARSERS[".tsx"].parse(p.read_bytes())
for a,b in [(385,401),(175,226),(227,296),(312,384)]:
 nodes=[n for n in m.walk(tree.root_node) if a<=n.start_point.row+1<=b]
 count=sum((n.type.endswith("_statement") and n.type not in {"empty_statement","export_statement"}) or n.type in m.JS_EXTRA for n in nodes)
 samples.append({"id":f"TS-{a}-{b}","path":ts["cache_path"],"ranges":[[a,b]],"sha256":ts["sha256"],"commit":ts["commit"],"program_units":count,"declarative_units":sum(n.type in {"jsx_opening_element","jsx_self_closing_element"} for n in nodes)})
bank={}
for kind,ids in {
 "controller":["AXSHARING_CONTROL","AXPACK_CONTROL","AXTOKEN_LOAD","AXTOKEN_REVOKE","AXTOKEN_CREATE"],
 "rule":["AXPACK_SERVICE","AXUNIT_CONVERSION","AXSHARING_QUERY"],
 "workflow":["AXCSV_ROW_REPLAY","AXSHARING_QUERY","AXCSV_PROCESS"],
 "ui_action":[s["id"] for s in samples if s["id"].startswith("TS-")]
}.items():
 vals=sorted(s["program_units"] for s in samples if s["id"] in ids)
 bank[kind]={"range":[min(vals),statistics.median(vals),max(vals)],"sample_ids":ids}
save("analogues.json",{"samples":samples,"unit_bank":bank,"convention_ref":"../2026-10-30-master-data-natif/measure.py","limitation":"Unités syntaxiques mesurées, et non JH observés. La quantité et le choix des analogies FLOW sont des hypothèses d'ingénierie. Recompte homogène avec audit24, différent du compteur de l'itération08."})
# Only residual behaviours beyond the MD01–MD07 native reference.
excluded={
"C01":["normaliser_identite_oidc","valider_role_action","normaliser_erreur_API","valider_limites_requetes"],
"C02":"ALL",
"IN01":["valider_colonnes_csv","convertir_types_canoniques"],
"IN02":["charger_flux_CSV_par_blocs","mettre_en_file_et_lancer_job","finaliser_lot_et_compteurs"],
"IN08":["relancer_lot_sur_checkpoint","exclure_lancement_concurrent","reprendre_apres_interruption"],
"V05":["valider_partie_et_roles","verifier_liens_organisationnels"],
"V06":["valider_produit_variante","valider_livre_tarif_produit","restituer_references_marchandise"],
"V07":["valider_matiere","valider_type_contenant","verifier_dimensions_capacite"],
"V08":["valider_type_fourniture_equipement","restituer_fourniture"],
"V09":["valider_site","valider_catalogue_prestation"],
"VCOMMON":["valider_unite_dimension","valider_ratio_conversion","convertir_quantite_avec_arrondi","valider_devise_base_recue"],
"V10A":["construire_filtres_types","valider_pagination_tri"],
"API_F01":["recevoirJSON","recevoirCSV","etatLot","resultatsLot"],
"API_F02":["lireSources","lireContrats","majContrat","lireAutorites","majAutorite"],
"API_F04":["listerRejets","detailRejet"],
"API_F05-F09":["rechercheReferences","detailReference"],
}
families={
"C01":"PROTECTION","C02":"PROTECTION","VCOMMON":"SEMANTIQUE","V10A":"PROTECTION","V10B":"PROTECTION",
"API_F10":"PROTECTION","PERSIST":"ADMISSION"
}
rows=[];decisions=[]
for b in old["backend_blocks"]:
 ex=b["blocks"] if excluded.get(b["id"])=="ALL" else excluded.get(b["id"],[])
 keep=[x for x in b["blocks"] if x not in ex]
 family=families.get(b["id"],"SEMANTIQUE" if b["id"].startswith("V") or b["id"]=="API_F05-F09" else "ADMISSION")
 decisions.append({"id":b["id"],"included_residual":keep,"already_in_native_equivalent_reference":ex,
 "reason":"Référence commune équipée pour CRUD, imports, droits et transactions ; seuls les comportements FLOW additionnels sont retenus. Ne prouve pas leur absence de tous les modules du produit."})
 for x in keep:
  rows.append({"id":b["id"]+"/"+x,"family":family,"kind":b["kind"],"contracts":b["contract_refs"],"quantity":1,"basis":"Inventaire08, après retrait des fonctions déjà financées par MD01–MD07."})
def block(id,family,kind,contracts,basis):
 rows.append({"id":id,"family":family,"kind":kind,"contracts":contracts,"quantity":1,"basis":basis})
# The framework restarts a job; Flow owns semantic replay/reconciliation.
for name in ["rejouer_revision_sans_second_effet","reconstruire_identite_semantique_et_dependances","ouvrir_epoque_et_invalider_curseurs","enregistrer_manifeste_consommateurs","rapprocher_usages_avec_identites_stables","controler_cloture_et_suspendre_purge"]:
 block("REPRISE/"+name,"REPRISE","workflow",["F03","F04","F10"],"Amendement07 : protocole métier au-dessus des checkpoints et sauvegardes réutilisés.")
for name in ["ouvrirRapprochement","etatRapprochement","cloreRapprochement"]:
 block("API_REPRISE/"+name,"REPRISE","controller",["F10"],"Trois opérations externes du protocole de rapprochement proposé.")
for name in ["consulter_journal_sensible","exporter_journal_sensible","appliquer_retention_journal"]:
 block("AUDIT/"+name,"PROTECTION","workflow",["F10","F11"],"Accès administrateur au journal et maintenance, distincts de l'écriture de trace déjà dimensionnée.")
for name in ["lireAudit","exporterAudit"]:
 block("API_AUDIT/"+name,"PROTECTION","controller",["F10"],"Accès protégé au journal.")
# A bounded canonical compatibility scenario, not a prediction of unknown future changes.
for name in ["renommer_champ","ajouter_valeur_par_defaut","traduire_enumeration","convertir_unite_declaree"]:
 block("VERSION/"+name,"VERSIONS","rule",["F01"],"Quatre transformateurs typés communs réutilisés pour les treize sujets ; aucune migration métier arbitraire.")
for name in ["dispatcher_version_sujet","refuser_conversion_ambigue"]:
 block("VERSION/"+name,"VERSIONS","workflow",["F01","F04"],"Deux versions canoniques ; incompatibilité sémantique refusée explicitement.")
# Additional relational state and recovery state. Ordinary identity/value fields already represented natively.
common={
"Party":["revisionId","intercompanyStatus"],"PartyRole":["validFrom","validTo"],"PartyLink":["validFrom","validTo"],
"Product":["revisionId"],"Variant":["revisionId","productRevisionId"],
"Unit":["revisionId"],"UnitConversion":["fromUnitRevisionId","toUnitRevisionId","validFrom","validTo"],
"PriceBook":["revisionId","scope","validFrom","validTo"],"PriceLine":["subjectRevisionId","conditionId","agreementRevisionId","offerRevisionId"],
"PackagingMaterial":["revisionId","attributes"],"ContainerType":["revisionId","reusable"],
"InternalSupply":["revisionId","usage"],"NetworkSite":["revisionId","responsiblePartyRevisionId"],
"Service":["revisionId","expectedOutcome","instructions"]}
schemas=[]
for s in old["schema_inventory"]:
 name=s["name"];fields=common.get(name,s["fields"])
 # Organisation scope gets reused from generic authorization; only logical grants are new elsewhere.
 if name=="OrganisationScope":fields=[]
 family="ADMISSION" if s["owner"]=="REF07_IN" else "SEMANTIQUE"
 if name in ["ConsumerUse","ExportReceipt","ChangeEvent","RetentionRule"]:family="PROTECTION"
 schemas.append({"name":name,"fields":fields,"already_in_reference":[x for x in s["fields"] if x not in fields],"new_model":name not in common and name!="OrganisationScope","family":family,"contracts":s["contract_refs"]})
for name,fields in {
"RecoveryEpoch":["id","openedAt","oldEpoch","status"],
"ConsumerManifest":["consumerId","scope","manifestChecksum","confirmedAt"],
"Reconciliation":["id","epochId","consumerId","expectedUses","receivedUses","status","closedAt"],
"CanonicalTransform":["subject","fromVersion","toVersion","field","operation","argument","onConflict"]
}.items():
 schemas.append({"name":name,"fields":fields,"already_in_reference":[],"new_model":True,"family":"VERSIONS" if name=="CanonicalTransform" else "REPRISE","contracts":["F01"] if name=="CanonicalTransform" else ["F10"]})
# Field declarations, mapping and UI configuration; syntax density is a proposed size, not measured Flow code.
schema_units={"program_per_field":[1,2,3],"declarative_per_field":[2,3,4],"declarative_per_new_model":[3,5,8],"ui_declarative_per_field":[1,2,3],"ui_declarative_per_new_model":[1,2,3]}
# Each field has one stored declaration + validation/mapping metadata; Java mappings, if generated, reduce the first axis.
ui_excluded={
"sources_autorites_contrats":["selection_source","editer_contrat"],
"import_rejets_publication":["choisir_fichier","soumettre_import","suivre_lot"],
"parties_accords_credit":["selectionner_role"],
"marchandise_catalogues_assortiments_contextes":["changer_sujet","consulter_prix_recu"],
"conditionnement":["expliquer_unites"],
"fournitures":["comparer_types"],
"services_tarifs":["parcourir_reseau"]}
ui=[]
for r in old["ui"]["routes"]:
 actions=[a for a in r["actions"] if a not in ui_excluded[r["id"]]]
 fam="ADMISSION" if r["id"] in ["sources_autorites_contrats","import_rejets_publication"] else "SEMANTIQUE"
 for a in actions:ui.append({"id":r["id"]+"/"+a,"family":fam,"kind":"ui_action","quantity":1,"contracts":list(set(r["contract_refs"]+["F11"])),"basis":"Action FLOW spécialisée ; widgets, formulaires, tables, routage et transport déjà réutilisés."})
for name in ["ouvrir_reprise","suivre_rapprochement","clore_rapprochement"]:
 ui.append({"id":"ui_reprise/"+name,"family":"REPRISE","kind":"ui_action","quantity":1,"contracts":["F10","F11"],"basis":"Parcours opérateur de reprise."})
for name in ["consulter_audit","exporter_audit","demander_purge"]:
 ui.append({"id":"ui_protection/"+name,"family":"PROTECTION","kind":"ui_action","quantity":1,"contracts":["F10","F11"],"basis":"Contrôle administrateur des protections."})
# SQL definitions and managed deployment are explicit. No provider implementation or annual operations.
config=[
{"id":"versions","family":"VERSIONS","contracts":["F01"],"quantity":26,"unit_range":[1,2,3],"basis":"Treize sujets × deux règles de transformation déclarées dans le scénario (renommage, ajout, enum ou unité). Le moteur est compté une fois. Ni migration future illimitée ni code Beaumanoir."},
{"id":"ddl","family":"PROTECTION","contracts":["F03","F10"],"quantity":sum(s["new_model"] for s in schemas),"unit_range":[1,2,3],"basis":"Un changeset par nouvelle table ; annotations de champs déjà comptées, pas une seconde copie du schéma."},
{"id":"indexes","family":"PROTECTION","contracts":["F01","F02","F03","F04","F10"],"quantity":16,"unit_range":[1,2,3],"basis":"Seize contraintes/index : 4 identité/origine, 4 versions/liens, 3 lots/rejets, 3 usages/export, 2 curseurs/époques ; proposition à vérifier par plans SQL."},
{"id":"delivery","family":"SERVICE","contracts":["S1"],"quantity":14,"unit_range":[4,8,16],"basis":"14 ressources déclaratives paramétrées : application, worker, ingress, secretRefs, DB, backup, restore, migration, monitor, alerts, logs, CI-build, CI-test, CI-deploy ; trois jeux de variables, pas trois copies de moteurs."},
{"id":"environments","family":"SERVICE","contracts":["S1"],"quantity":3,"unit_range":[6,10,16],"basis":"Trois environnements logiques sur un fournisseur géré, variables de capacité/connexion/rétention ; code fournisseur non reconstruit."},
{"id":"metrics","family":"SERVICE","contracts":["S1"],"quantity":8,"unit_range":[1,2,4],"basis":"Huit règles métier de supervision : latence, rejets, attente dépendances, publication, retard curseur, usage non rapproché, sauvegarde, restauration."}]
for name in ["orchestrer_restauration_et_blocage_publication","verifier_coherence_apres_restauration","executer_bascule_et_rollback_deploiement","valider_resultat_migration"]:
 block("SERVICE/"+name,"SERVICE","workflow",["S1"],"Assemblage des commandes fournies par l'hébergeur, CI et outil de migration ; scripts applicatifs livrés, pas construction des moteurs.")
inputs={
"id":"audit25-master-data-spring-equivalence","date":"2026-10-30","status":"estimation_conditionnelle_non_calibree_non_appliquee",
"scope":"Master Data FLOW, BC-002 à BC-007, contrat07 v1.1 et scénario S1. Total de projet initial ; ni ensemble du Core System, ni intégration Beaumanoir, ni exploitation annuelle.",
"framework_policy":{"adjustment_factor":1,"observed_equivalence_of_effort":False,"decision":"Pas de supplément ou remise forfaitaire Spring. Équivalence des services génériques retenue comme hypothèse d'étude d'opportunité, à productivité et maîtrise comparables. Les charges de composition normales sont déjà dans les références natives.","target":"Java 21, Spring Boot 4.1.2 avec Data JPA, Security, Batch à repository JDBC persistant, PostgreSQL géré, interface React équipée de composants CRUD réutilisables (React-admin Community comme candidat). Les exports CRUD sont protégés ; les commandes métier passent par les services, pas par écriture directe des tables.","compatibility":"Capacités documentées, assemblage et BOM non exécutés. Spring seul ne fournit pas le client métier de Frappe/Axelor ; la comparaison inclut les composants UI et API. Aucun produit n'est recopié dans FLOW."},
"reference_choice":{"id":"axelor","reason":"Référence Java parmi les quatre estimations natives ; pas sélection du chiffre le plus proche d'une durée souhaitée. Les trois autres restent des sensibilités de référence, sans moyenne.","equivalent_size_meaning":"La taille équivalente native conserve le travail d'intégration de sa plateforme. Sous l'hypothèse d'équivalence, c'est une ancre de charge équivalente, PAS une mesure ni une traduction des sources Spring. Les nouveaux blocs sont des analogies Java/TS mesurées. Ce pont est une hypothèse, non une preuve de productivité identique."},
"assumptions":[
"Deux versions canoniques ; 26 transformations déclarées utilisant quatre opérations partagées. Une modification sémantique non représentable exige une nouvelle estimation.",
"Un seul stockage transactionnel, monolithe modulaire, deux instances applicatives ; fournisseur DB/backup/CI géré, modules standards existants ; pas de plateforme cloud à reconstruire.",
"Identité/authentification et administration des rôles au fournisseur d'identité. FLOW applique l'organisation/portée sur tous les accès ; pas d'éditeur générique de politique.",
"Le manifeste des consommateurs est conservé hors du point de restauration par l'opérateur ; clôture opérateur après vérification, sans nouveau callback indépendant par consommateur. Usages non déclarés indétectables.",
"Publication sur admission cohérente ; une action manuelle de validation/rejeu utilise le même processus I02 avec les mêmes objets/résultats. Pas de moteur de workflow général.",
"Interfaces humaines et machine utilisent le même contrat de résultats ; pas de double comptage des mêmes processus COSMIC.",
"Les garanties S1 sont des objectifs : ni charge de 100k lignes/30min, ni disponibilité99.9%, ni RTO8h ne sont prouvés par une documentation de framework.",
"Tests développeur, QA, analyse, conception, gestion et préparation initiale inclus dans COCOMO quatre phases ; pas d'ajout de tests LOC ou d'un pourcentage QA. Exploitation, MCO, fournisseur et intégration client exclus.",
"Les défauts ordinaires et optimisations relèvent de l'effort estimé. Une refonte d'architecture ou une exigence au-delà de S1 nécessite une réestimation ; l'enveloppe n'est pas une garantie d'exhaustivité."],
"native_results_ref":"../2026-10-30-master-data-comparable-reuse/results.json","contract_ref":"../2026-10-29-experimentation-estimation/iteration-07-contrat-v1.1.json",
"contract_sha256":sha(PRE/"iteration-07-contrat-v1.1.json"),
"cocomo":native_inputs["cocomo"],"scenarios":native_inputs["scenarios"],
"blocks":rows+ui,"deduplication":decisions,"schemas":schemas,"schema_units":schema_units,"configuration":config,
"families":{"ADMISSION":"Contributions, autorité, versions et publication","SEMANTIQUE":"Accords, assortiments, conditionnements et services","PROTECTION":"Accès contextualisés, usages protégés, audit et purge","REPRISE":"Rejeu sémantique et rapprochement après restauration","VERSIONS":"Compatibilité des versions canoniques","SERVICE":"Mise en service et garanties S1"},
"uncertainty":{"class":"C","meaning":"Estimation conditionnelle d'ingénierie, sans charge projet observée ni productivité Spring calibrée.","percentile":None,"envelope":"Bornes de scénarios dépendants, non intervalle de confiance ; analogue, densité déclarative, compétence et expérience varient ensemble.","framework_gap_effort":None,"framework_gap_treatment":"Aucun supplément démontré. Inconnu résiduel sur la productivité d'assemblage ; facteur1 conventionnel ne signifie pas égalité prouvée."},
"provenance":{"author":"Codex, assistance IA","human_review":None,"observed_flow_code":None,"observed_project_jh":None},
"input_hashes":{str(p.relative_to(ROOT)):sha(p) for p in [PRE/"iteration-08-taille.json",PRE/"iteration-07-contrat-v1.1.json",ROOT/"audits/2026-10-30-master-data-comparable-reuse/results.json",ROOT/"audits/2026-10-30-master-data-comparable-reuse/inputs.json"]}}
save("inputs.json",inputs)
print(json.dumps({"samples":len(samples),"bank":bank,"blocks":len(inputs["blocks"]),"delta_fields":sum(len(s["fields"]) for s in schemas),"new_models":sum(s["new_model"] for s in schemas),"excluded_backend_blocks":sum(len(d["already_in_native_equivalent_reference"]) for d in decisions)},ensure_ascii=False))
