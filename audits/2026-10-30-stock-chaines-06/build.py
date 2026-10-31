"""Measure complete declared stock chains, including framework/transaction boundaries.
No change to the retained economic model. No method-category extrapolation.
"""
from pathlib import Path
from collections import defaultdict
import ast,hashlib,importlib.util,json,subprocess,sys,math
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tmp/model-deps'),str(ROOT/'tools'),str(ROOT/'tmp/master-data-native-23/parser-deps')]
import yaml
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,x):(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def module(name,p):
 s=importlib.util.spec_from_file_location(name,ROOT/p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
scope=module('scope06','audits/2026-10-30-stock-perimetres-02/build.py')
counter=module('counter06','audits/2026-10-30-master-data-natif/measure.py')
repos=scope.repos
E='erpnext/stock/'
O='addons/stock/models/'
T='modules/stock/'
A='axelor-stock/src/main/java/com/axelor/apps/stock/service/'
R='axelor-supplychain/src/main/java/com/axelor/apps/supplychain/service/ReservedQtyServiceImpl.java'
specs=defaultdict(list)
def add(chain,repo,path,names,role='stock_quantity',why=None):
 specs[chain].append(dict(repo=repo,path=path,selectors=names.split(),role=role,classification_basis=why or 'traitement de quantité/état de stock observé dans la chaîne'))
def erp_framework(chain):
 add(chain,'frappe','frappe/model/document.py',
 'Document.submit Document._submit Document.save Document._save Document.insert Document.db_insert Document.db_update Document.check_if_latest Document.run_before_save_methods Document.run_post_save_methods Document.run_method',
 'framework_reused','Persistance, vérification de version du document et hooks ; propriétaire java-spring-framework-services dans la transposition.')
 add(chain,'frappe','frappe/app.py','application sync_database handle_exception','framework_reused','Frontière HTTP : commit au succès, rollback en erreur, réponse ; pas de retry métier automatique attribué.')
def odoo_framework(chain):
 add(chain,'odoo','odoo/orm/models.py','BaseModel.try_lock_for_update BaseModel.write BaseModel._write_multi BaseModel.flush_model BaseModel._flush BaseModel.create',
 'framework_reused','Verrou SQL, flush et persistance différée de l’ORM ; pas écriture SQL directe à chaque appel write.')
 add(chain,'odoo','odoo/http/retrying.py','retrying','framework_reused','Reprise de toute la transaction sur les erreurs de concurrence autorisées ; commit et rollback.')
def tryton_framework(chain):
 add(chain,'tryton','trytond/trytond/model/workflow.py','Workflow.transition','framework_reused','Le décorateur effectue la transition d’état par le modèle SQL.')
 add(chain,'tryton','trytond/trytond/model/modelsql.py','ModelSQL.create ModelSQL.write ModelSQL.lock','framework_reused','Écritures et verrou de table du framework, non refacturés comme développement Stock.')
 add(chain,'tryton','trytond/trytond/protocols/dispatcher.py','_dispatch','framework_reused','Transaction RPC, rollback, retry configuré des erreurs opérationnelles et commit.')
def ax_framework(chain):
 add(chain,'platform','axelor-core/src/main/java/com/axelor/db/JpaRepository.java','save flush','framework_reused','Repository et flush JPA.')
 add(chain,'platform','axelor-core/src/main/java/com/axelor/db/JPA.java','save persist merge flush checkVersion runInTransaction','framework_reused','Persistance, vérification de version et transaction génériques.')
 # @Version is a field, not a method; captured as exact field evidence below.

# ERPNext: quantity propagation and its actual current-voucher coordinator.
c='erpnext-correction'
add(c,'erpnext',E+'stock_ledger.py','make_sl_entries repost_current_voucher update_entries_after.*','coupled_native','Composant natif complet de recalcul : quantités et valorisation mêlées. Sa taille brute ne constitue pas une assiette Stock Flow.')
add(c,'erpnext',E+'stock_ledger.py','get_args_for_future_sle validate_cancellation set_as_cancel make_entry update_qty_in_future_sle get_stock_reco_qty_shift get_next_reco_datetime_condition get_next_stock_reco get_datetime_limit_condition validate_negative_qty_in_future_sle is_reserved_stock_drawn is_negative_with_precision get_future_sle_with_negative_qty get_future_sle_with_negative_batch_qty get_sle_against_current_voucher get_previous_sle_of_current_voucher get_previous_sle get_stock_ledger_entries get_sle_entries_by_names get_prior_ledger_condition')
add(c,'erpnext',E+'doctype/stock_ledger_entry/stock_ledger_entry.py','StockLedgerEntry.*','coupled_native','Document et validations natifs complets ; fiscalité et serial/batch mêlés aux quantités.')
add(c,'erpnext',E+'doctype/bin/bin.py','update_qty update_bin_columns get_last_sle_values Bin.set_projected_qty','coupled_native','L’objet Bin porte quantité et valeur ; aucune ventilation financière arbitraire.')
add(c,'erpnext',E+'utils.py','get_or_make_bin _create_bin get_combine_datetime validate_warehouse_company validate_disabled_warehouse')
erp_framework(c)
c='erpnext-reservation'
add(c,'erpnext',E+'doctype/stock_reservation_entry/stock_reservation_entry.py',
 'StockReservationEntry.validate StockReservationEntry.before_insert StockReservationEntry.before_submit StockReservationEntry.on_submit StockReservationEntry.on_update_after_submit StockReservationEntry.on_cancel StockReservationEntry.validate_voucher StockReservationEntry.is_row_of_voucher StockReservationEntry.validate_amended_doc StockReservationEntry.validate_mandatory StockReservationEntry.validate_group_warehouse StockReservationEntry.validate_uom_is_integer StockReservationEntry.set_reservation_based_on StockReservationEntry.validate_reservation_based_on_qty StockReservationEntry.validate_with_allowed_qty StockReservationEntry.get_total_reserved_qty StockReservationEntry.get_row_reserved_qty StockReservationEntry.update_reserved_stock_in_bin StockReservationEntry.update_status get_available_qty_to_reserve get_sre_reserved_qty_for_item_and_warehouse get_status')
add(c,'erpnext',E+'doctype/stock_reservation_entry/stock_reservation_entry.py','StockReservationEntry.update_reserved_qty_in_voucher StockReservationEntry.update_reserved_qty_in_pick_list StockReservation.make_stock_reservation_entry','native_integration','Liens de commande, picking et construction sérialisée : contexte natif explicitement mesuré, hors engagement générique seul.')
add(c,'erpnext',E+'utils.py','_get_stock_balance get_or_make_bin _create_bin','coupled_native','Lecture de stock commune et branches optionnelles de valeur/séries ; création concurrente du Bin via savepoint/unicité.')
add(c,'erpnext',E+'stock_ledger.py','get_previous_sle get_stock_ledger_entries get_prior_ledger_condition')
add(c,'erpnext',E+'doctype/bin/bin.py','Bin.update_reserved_stock on_doctype_update')
erp_framework(c)

# Odoo: inventory to done movement to quant; past quantity is reconstructed from dated movement lines.
c='odoo-correction'
add(c,'odoo',O+'stock_quant.py','StockQuant.action_apply_inventory StockQuant._apply_inventory StockQuant._get_inventory_move_values StockQuant._compute_inventory_diff_quantity StockQuant._compute_is_outdated StockQuant.action_clear_inventory_quantity StockQuant._update_available_quantity StockQuant._get_available_quantity StockQuant._gather StockQuant._get_gather_domain StockQuant.create StockQuant.write StockQuant._is_inventory_mode StockQuant._get_inventory_fields_create StockQuant._get_forbidden_fields_write')
add(c,'odoo',O+'stock_move.py','StockMove.create StockMove.write StockMove._action_done StockMove._check_quantity','native_integration','Appelant natif complet : mouvements, backorders, packages et déclenchements de réaffectation ; pas assiette comparable de Flow seul.')
add(c,'odoo',O+'stock_move_line.py','StockMoveLine.create StockMoveLine.write StockMoveLine._action_done StockMoveLine._synchronize_quant StockMoveLine._free_reservation','native_integration','Écritures et hooks complets observés ; réserve, mouvements et traitement des colis sont couplés.')
add(c,'odoo',O+'product.py','ProductProduct._compute_quantities ProductProduct._compute_quantities_dict ProductProduct._get_domain_locations ProductProduct._get_domain_locations_new')
odoo_framework(c)
c='odoo-reservation'
add(c,'odoo',O+'stock_move.py','StockMove._update_reserved_quantity StockMove._update_reserved_quantity_vals StockMove._prepare_move_line_vals StockMove._should_bypass_reservation StockMove._recompute_state StockMove.write')
add(c,'odoo',O+'stock_move_line.py','StockMoveLine.create StockMoveLine.write StockMoveLine._synchronize_quant','native_integration','La réservation effective est déclenchée dans les hooks create/write des lignes, pas seulement dans _get_reserve_quantity.')
add(c,'odoo',O+'stock_quant.py','StockQuant._get_reserve_quantity StockQuant._get_available_quantity StockQuant._gather StockQuant._get_gather_domain StockQuant._update_reserved_quantity StockQuant._update_available_quantity StockQuant.create StockQuant.write StockQuant._is_inventory_mode StockQuant._get_inventory_fields_create StockQuant._get_forbidden_fields_write','stock_quantity')
add(c,'odoo',O+'stock_quant.py','StockQuant._get_removal_strategy StockQuant._get_removal_strategy_order','native_integration','Politique de prélèvement native utilisée par _gather ; pas algorithme d’allocation Flow à reconstruire.')
odoo_framework(c)

# Tryton: correcting inventory creates a dated move; query aggregation and cached periods determine quantities.
c='tryton-correction'
add(c,'tryton',T+'inventory.py','Inventory.confirm Inventory.check_tolerance Inventory.check_modification InventoryLine.get_move InventoryLine.unique_key InventoryLine.check_modification','coupled_native','Tolérances de coût et de quantité réunies dans check_tolerance ; aucun coefficient de ventilation.')
add(c,'tryton',T+'move.py','Move.do Move._do','coupled_native','Move.do met les mouvements à done et porte aussi la valorisation ; _do est la frontière des coûts.')
add(c,'tryton',T+'move.py','Move.set_effective_date Move.check_origin Move.check_period_closed Move.check_modification Move.compute_quantities_query Move.compute_quantities _location_children')
add(c,'tryton',T+'product.py','Product.products_by_location Product._quantity_locations Product.get_quantity Product.search_quantity')
tryton_framework(c)
c='tryton-reservation'
add(c,'tryton',T+'move.py','Move.assign_try Move._assign_try_lock Move.assign Move.sort_quantities Move.pick_product Move.check_period_closed Move.check_modification Move.compute_quantities_query Move.compute_quantities _location_children','stock_quantity')
add(c,'tryton',T+'product.py','Product.products_by_location')
tryton_framework(c)

# Axelor: inventory adjustment, mutation/history, then explicit offline reconstruction component.
c='axelor-correction'
add(c,'axelor',A+'inventory/InventoryValidateServiceImpl.java','validate generateStockMoves generateStockMove realizeGeneratedStockMoves stockMoveRealize generateStockMoveLines computeDiff checkMissingStockLocation getStockMoveLinesCount','native_integration','Chaîne d’inventaire complète par composants, avec génération des mouvements ; valeur et quantités de lignes couplées.')
add(c,'axelor',A+'StockMoveServiceImpl.java','realize realizeStockMove copyQtyToRealQty','native_integration','Réalisation native et effets de service ; realDate prend la date du jour dans la méthode inspectée.')
add(c,'axelor',A+'StockMoveLineServiceImpl.java','updateLocations updateLocationForStockMoveLine updateStockLocationLineHistory updateAveragePriceAndLocationLineHistory getStockLocationLineHistoryTypeSelect','coupled_native','Toutes les surcharges et mutation des emplacements ; prix moyen/historique mêlés, aucune quote-part improvisée.')
add(c,'axelor',A+'StockLocationLineServiceImpl.java','updateLocation updateDetailLocation updateHistory getOrCreateStockLocationLine getOrCreateDetailLocationLine createLocationLine createDetailLocationLine convertToProductUnit convertFromProductUnit productUnit convert getCompany','coupled_native','Quantités actuelles/futures, détails, et réapprovisionnement déclenché par le même composant.')
add(c,'axelor',A+'StockLocationLineHistoryServiceImpl.java','saveHistory getStockLineHistoryLines','coupled_native','Snapshot quantité et prix du même objet.')
add(c,'axelor',A+'batch/BatchRecomputeStockLocationLines.java','*','coupled_native','Composant complet : effacement, remise à zéro, tri des mouvements réalisés, reconstitution et quantités prévues ; pas reprise atomique démontrée.')
ax_framework(c)
c='axelor-reservation'
add(c,'axelor',R,'updateReservedQty@767 updateReservedQty@777 updateRequestedReservedQty@818 updateRequestedReservedQty@828 checkBeforeUpdatingQties checkAvailabilityRequest updateReservedQty@995 updateRequestedReservedQty@937 convertUnitWithProduct computeRealReservedQty requestQty@1120 cancelReservation@1155')
add(c,'axelor',A+'StockLocationLineServiceImpl.java','getOrCreateStockLocationLine createLocationLine')
add(c,'axelor',A+'StockLocationLineFetchServiceImpl.java','getStockLocationLine getStockLocationLines')
ax_framework(c)

SUPPORT=[
 ('odoo','odoo/sql_db.py',[(87,91),(214,242),(786,800)],'REPEATABLE READ et classes de conflits reprises.'),
 ('platform','axelor-core/src/main/java/com/axelor/db/Model.java',[(14,27),(49,56)],'Champ @Version hérité ; pas une absence de contrôle de concurrence.'),
 ('platform','axelor-core/src/main/java/com/axelor/db/JpaModel.java',[(12,27)],'Héritage Model.'),
 ('platform','gradle/libs.gradle',[(1,10),(114,120)],'Hibernate 6.6.58.Final dans la révision native.'),
 ('tryton','trytond/trytond/backend/postgresql/database.py',[(277,289)],'Isolation REPEATABLE READ du backend PostgreSQL.'),
 ('odoo',O+'stock_move_line.py',[(62,64)],'date est liée à move_id.date et stockée ; la date du mouvement se propage aux lignes.'),
 ('erpnext',E+'doctype/bin/bin.py',[(219,220)],'Contrainte unique item/warehouse ; elle ne prouve pas seule l’exclusion entre nouvelles réservations distinctes.'),
 ('axelor','axelor-stock/src/main/resources/domains/StockLocationLine.xml',[(1,36)],'Déclaration du modèle StockLocationLine ; quantité et références.'),
]
TESTS=[
 ('erpnext',E+'doctype/stock_ledger_entry/test_stock_ledger_entry.py','TestStockLedgerEntry.test_update_qty_in_future_sle_shifts_same_timestamp_later_entry','Test source de propagation dans le cas de deux écritures au même instant ; non exécuté.'),
 ('odoo','addons/stock/tests/test_quant.py','TestStockQuant.test_to_date_consignment','Test source de quantité passée et de propriété ; non exécuté.'),
 ('tryton','modules/stock/tests/scenario_stock_inventory.rst',None,'Scénario source de confirmation d’inventaire et de mouvement de delta ; non exécuté.')
]

CHAIN_NOTES={
 'erpnext-correction':dict(
  pattern='Recalcul des soldes après transaction dans les écritures futures, ordonnées par date de fait puis création ; borne au prochain inventaire.',
  native_stages=['make_sl_entries et validations du document','repost_current_voucher et moteur update_entries_after mêlé à la valeur','update_qty_in_future_sle → décalage des quantités suivantes → contrôle du négatif','Bin et registre relus ; commit/rollback Frappe'],
  result='La propagation est identifiée dans une chaîne native réelle. La création du fait et le recalcul courant ne sont pas séparables gratuitement de la valorisation native.',
  gap='Le couple posting_datetime/creation règle l’ordre ; il ne démontre pas une restitution complète selon date de fait ET date de connaissance avant/après correction.',
  unresolved=['Extraction du contrat quantité hors des calculs de valeur et hooks serial/batch natifs.','Unicité de l’effet après nouvelle soumission métier distincte de la reprise SQL.']),
 'erpnext-reservation':dict(
  pattern='Document de réservation → before_submit → quantité autorisée → agrégat des réservations FOR UPDATE → insertion/mise à jour → statut/Bin → commit ou rollback.',
  native_stages=['Construction de StockReservationEntry et validate','before_submit → validate_reservation_based_on_qty → validate_with_allowed_qty','Lecture SLE et agrégat réservé avec for_update','Persistance Frappe → on_submit/on_update → statut et Bin → réponse'],
  result='Le verrou existe sur la requête d’agrégat, et la création concurrente du Bin a un savepoint et une unicité. Ce sont deux mécanismes distincts.',
  gap='L’agrégat verrouillé ne suffit pas à établir le cas de la première réservation sans ligne commune ; la lecture du solde utilise get_previous_sle sans for_update par défaut.',
  unresolved=['Premier engagement et ensembles vides, selon moteur/isolation/index.','Sur PostgreSQL, SUM avec FOR UPDATE pose une restriction SQL à vérifier dans le chemin réellement déployé. Ne pas qualifier toutes les bases à partir de ce seul appel.','Aucun retry métier automatique attribué à Frappe dans application/sync_database inspectés.']),
 'odoo-correction':dict(
  pattern='Correction d’inventaire → création des mouvements → lignes done → synchronisation des quants. Quantité passée = quantité actuelle corrigée des lignes ultérieures à la date.',
  native_stages=['action_apply_inventory détecte un inventaire devenu obsolète','_apply_inventory crée le delta et _action_done le réalise','StockMoveLine._action_done/_synchronize_quant → quantité et réservation des quants','Date liée mouvement/ligne puis requête _compute_quantities_dict ; transaction/retry/commit'],
  result='L’écriture effective, la propagation de date et la lecture passée sont reliées ; la correction est mêlée aux mécanismes de mouvement/colis/réaffectation.',
  gap='Une date d’effet passée et une date de connaissance historique ne sont pas la même restitution. Pas de preuve d’un historique immuable de toutes les révisions dans la chaîne retenue.',
  unresolved=['Portion comparable sans exécution de colis, backorders ou réaffectation.','Complément Flow de correction liée et restitution selon connaissance.']),
 'odoo-reservation':dict(
  pattern='Mouvement → sélection des quantités → création/modification de ligne → hook de réservation → quant verrouillé ou créé → flush → reprise éventuelle de la transaction.',
  native_stages=['StockMove._update_reserved_quantity et _get_reserve_quantity','StockMoveLine.create/write appelle la mutation réservée','StockQuant._update_reserved_quantity → _update_available_quantity → ORM.try_lock_for_update','ORM.flush + retrying : rollback et au plus cinq tentatives puis commit/résultat ou erreur'],
  result='La chaîne complète inclut les hooks et la politique de transaction, absents de l’analogie à une petite méthode. Les doublons de quants sont un cas explicitement traité ; pas de contrainte unique inventée.',
  gap='La sélection native peut réserver partiellement et choisir des quants ; un engagement Flow sur une portion imposée et son identité de commande exigent un contrat explicite.',
  unresolved=['Délimitation de la sélection/prélèvement native par rapport à une quantité et portion imposées.','Idempotence du nouvel appel métier après perte de la réponse, distincte du retry de la transaction avortée.']),
 'tryton-correction':dict(
  pattern='Confirmation d’inventaire → delta expected/count → mouvement à effective_date = date d’inventaire → done → quantités agrégées à la date demandée, avec cache de période.',
  native_stages=['Inventory.confirm et contrôle de tolérance/unicité des lignes','InventoryLine.get_move crée le delta et sa date','Move.do/set_effective_date/check_period_closed puis Workflow/ModelSQL','Product.products_by_location → Move.compute_quantities_query/compute_quantities ; transaction RPC'],
  result='L’effet historique provient de l’agrégation des mouvements datés ; un moteur de propagation identique à ERPNext n’est pas requis dans cette architecture.',
  gap='Move.do porte aussi les coûts. Les dates/états empêchent certaines modifications ; cela ne constitue pas un historique bitemporel Flow complet.',
  unresolved=['Extraction des activités de coût dans Move.do et des tolérances de valeur de Inventory.check_tolerance.','Historique des révisions et autorité des contributions externes.']),
 'tryton-reservation':dict(
  pattern='assign_try → verrouillage des mouvements avant lecture des quantités → choix/répartition → write/copy → transition assigned → commit ; rollback/retry sur conflit opérationnel.',
  native_stages=['assign_try identifie produits, lieux, entreprise, date','_assign_try_lock : SELECT FOR UPDATE NOWAIT, ou verrou de modèle selon backend','products_by_location avec stock_assign → répartition/split → write/copy/assign','Workflow → ModelSQL → dispatcher._dispatch : rollback/retry puis commit'],
  result='Ordre verrou/lecture/écriture et reprise RPC identifiés. La politique de répartition est embarquée dans assign_try et doit être isolée pour comparer Flow.',
  gap='Cache de période et préexistence des lignes verrouillables influencent le cas concurrent. La chaîne native ne démontre pas tout engagement externe rejouable.',
  unresolved=['Premier engagement/ensembles sans ligne commune et cache de période, dans le contexte d’appel exact.','Délimitation du split/choix de lieu et de la simple protection d’une quantité donnée.']),
 'axelor-correction':dict(
  pattern='Inventaire → mouvements réalisés → mutation quantité/historique. Un batch distinct reconstruit stock et historique par groupes de date réelle.',
  native_stages=['InventoryValidateService.validate et génération du delta','StockMoveService.realizeStockMove impose realDate = date du jour dans cette voie','StockMoveLine.updateLocations → StockLocationLine.updateLocation → JPA ; historique lié au prix','BatchRecomputeStockLocationLines : effacer historique/remettre à zéro → groupes réalisés → recalcul → quantités prévues et anomalies'],
  result='La reconstruction complète est un vrai analogue de reprise. Elle utilise plusieurs transactions et trace les anomalies ; elle ne prouve pas une correction rétroactive en ligne atomique.',
  gap='Aucune équivalence complète à l’admission d’une correction rétroactive Flow trouvée dans ces voies. Le batch reconstruit l’état à partir du patrimoine natif ; il ne conserve pas automatiquement toutes les connaissances historiques.',
  unresolved=['Passage de la reconstruction globale native à un recalcul ciblé de la portion corrigée.','Cohérence visible pendant reconstruction, arrêt/reprise, et liens de correction.','Prix moyen, réapprovisionnement et exécution des mouvements mêlés aux méthodes.']),
 'axelor-reservation':dict(
  pattern='Transaction de mise à jour d’une quantité réservée sur StockMoveLine → contrôle disponible → mutation de ligne → recalcul du total réservé de StockLocationLine → flush versionné.',
  native_stages=['updateReservedQty(StockMoveLine, qty), avec ligne de stock existante','checkBeforeUpdatingQties/checkAvailabilityRequest et comparaison currentQty-reservedQty','Setter de quantité puis recalcul des réservés par produit/lieu et état planned','JPA/Hibernate @Version hérité du modèle : conflit de version attendu au flush, rollback transactionnel ; aucun retry automatique attribué'],
  result='Le contrôle de concurrence optimiste du framework existe ; l’absence de FOR UPDATE dans ce service ne démontre pas une absence de protection.',
  gap='Conclusion conditionnelle aux entités gérées et à la mise à jour de la même ligne versionnée. Création de portions concurrentes, branche SalesOrder et effets de flush restent des contextes à distinguer.',
  unresolved=['Confirmer le contexte de flush des entités gérées et le résultat d’un conflit pour l’API d’appel.','Premier enregistrement de la portion et chemin SalesOrder : pas qualifiés par la seule branche sans commande.','Identité/rejeu de commande et expiration Flow non prouvés par @Version.'])
}

def selected_methods(config):
 raw,methods,_=scope.parse(ROOT/repos[config['repo']]['root']/config['path'])
 chosen={}
 for name in config['selectors']:
  found=[m for m in methods if name=='*' or (name.endswith('.*') and m['name'].startswith(name[:-1])) or scope.matches(m,name)]
  assert found,(config['repo'],config['path'],name)
  for m in found:chosen[(m['start'],m['end'])]=m
 return raw,list(chosen.values())

def measure(config):
 raw,methods=selected_methods(config);text=raw.decode('utf-8-sig');lines=text.splitlines()
 nodes=[]
 if config['path'].endswith('.py'):
  for n in ast.walk(ast.parse(text)):
   if not isinstance(n,ast.stmt):continue
   if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):continue
   if any(m['start']<=n.lineno<=n.end_lineno<=m['end'] for m in methods):nodes.append(dict(kind=type(n).__name__,start=n.lineno,end=n.end_lineno))
 else:
  tree=scope.JAVA.parse(raw);assert not tree.root_node.has_error
  for n in counter.walk(tree.root_node):
   if not ((n.type.endswith('_statement') and n.type!='empty_statement') or n.type in counter.JAVA_EXTRA):continue
   a,b=n.start_point.row+1,n.end_point.row+1
   if any(m['start']<=a<=b<=m['end'] for m in methods):nodes.append(dict(kind=n.type,start=a,end=b))
 for m in methods:
  m['source_fragment']='\n'.join(lines[m['start']-1:m['end']])
  m['program_units']=sum(m['start']<=n['start']<=n['end']<=m['end'] for n in nodes)
 root=ROOT/repos[config['repo']]['root'];path=config['path']
 # Byte equality to the pinned Git object after native checkout newline conversion:
 # native .gitattributes may CRLF; compare normalized LF content and keep exact raw SHA too.
 original=subprocess.check_output(['C:/Program Files/Git/cmd/git.exe','-C',str(root),'show',repos[config['repo']]['commit']+':'+path])
 assert original.replace(b'\r\n',b'\n')==raw.replace(b'\r\n',b'\n'),(path,'not pinned Git contents')
 return dict(repo=config['repo'],path=path,commit=repos[config['repo']]['commit'],sha256=hashlib.sha256(raw).hexdigest(),
  git_object_sha256=hashlib.sha256(original).hexdigest(),source_url='https://github.com/'+repos[config['repo']]['repository']+'/blob/'+repos[config['repo']]['commit']+'/'+path,
  role=config['role'],classification_basis=config['classification_basis'],methods=methods,counted_nodes=nodes,program_units=len(nodes),
  size_meaning='instructions/déclarations de méthodes intégrales dans le dossier de chaîne, pas taille de famille ni SLOC certifiées',
  mechanism_ref='java-spring-framework-services' if config['role']=='framework_reused' else None,
  funding_owner='master-data-java-spring' if config['role']=='framework_reused' else 'stock-candidate',
  stock_additional_generic_framework_units=0 if config['role']=='framework_reused' else None)

def main():
 OUT.mkdir(exist_ok=True)
 protected_paths=['source/referentiel-capacites.yaml','sources/cartographie-scm-2026-10-24.yaml','source/estimations-core-retenues.yaml','source/fondamentaux.yaml','source/calculs-estimation-core.yaml']
 protected={p:digest(ROOT/p) for p in protected_paths}
 products=['erpnext','odoo','tryton','axelor']
 chains=[]
 for chain,configs in specs.items():
  records=[measure(c) for c in configs]
  # A source node is counted once in a chain, even through multiple call sites.
  seen=set()
  for f in records:
   for n in f['counted_nodes']:
    key=(f['repo'],f['path'],n['start'],n['end'],n['kind']);assert key not in seen,(chain,key);seen.add(key)
  note=CHAIN_NOTES[chain]
  r=dict(id=chain,product=chain.split('-')[0],kind=chain.split('-')[1],status='dossier natif bout en bout aux frontières déclarées, pas équivalence Flow démontrée',
   **note,files=records,
   units_by_role={role:sum(f['program_units'] for f in records if f['role']==role) for role in ['stock_quantity','coupled_native','native_integration','framework_reused']},
   method_count=sum(len(f['methods']) for f in records),runtime_executed=False,
   closure=dict(main_stages_traced=True,critical_transaction_boundary_identified=True,all_dynamic_hooks_and_installed_extensions_closed=False,
    mixed_native_responsibilities_present=any(f['role'] in ['coupled_native','native_integration'] for f in records),
    complete_Flow_retroactivity_and_command_replay_equivalence=False),
   effort=dict(receivable_jh=None,COCOMO_executed=False,reason='Le dossier mesure les composants natifs et leurs dépendances, pas une assiette homogène neuve/réutilisée du mécanisme Flow complet. Un total de famille ou de projet autonome tiré de ces seules méthodes serait trompeur.'),
   standard_ports_not_counted_as_new_stock=['ORM/repositories et transactions natifs','lecture des identités produit/lieu/unité/partenaire existantes','injection et services de date/configuration/logs'],
   native_domain_ports_requiring_scope_resolution=note['unresolved'])
  write(chain+'.json',r);chains.append(r)
 evidence=[]
 for repo,path,ranges,note in SUPPORT:
  f=ROOT/repos[repo]['root']/path;lines=f.read_text(encoding='utf-8-sig').splitlines()
  evidence.append(dict(repo=repo,path=path,commit=repos[repo]['commit'],sha256=digest(f),ranges=ranges,
    fragments=['\n'.join(lines[a-1:b]) for a,b in ranges],meaning=note,role='framework_or_model_evidence',stock_additional_units=None))
 tests=[]
 for repo,path,symbol,note in TESTS:
  f=ROOT/repos[repo]['root']/path;raw=f.read_bytes();text=raw.decode('utf-8-sig')
  if symbol:
   _,methods,_=scope.parse(f)
   found=[m for m in methods if m['name']==symbol]
   if not found:
    # Test class names can vary; resolve an exact unambiguous method name.
    found=[m for m in methods if m['name'].endswith('.'+symbol.split('.')[-1])]
   assert len(found)==1,(symbol,found)
   a,b=found[0]['start'],found[0]['end']
  else:a,b=145,180
  tests.append(dict(repo=repo,path=path,commit=repos[repo]['commit'],sha256=digest(f),start=a,end=b,
    source_fragment='\n'.join(text.splitlines()[a-1:b]),note=note,executed=False,included_in_production_size=False))
 write('preuves-complementaires.json',dict(support=evidence,tests_read_not_run=tests,external_primary_sources=[
  dict(url='https://docs.hibernate.org/orm/6.6/userguide/html_single/#locking-optimistic',checked_on='2026-10-30',
   interpretation='@Version détecte les mises à jour concurrentes sur la même entité gérée ; cela ne couvre pas toutes les invariants entre lignes ni un nouvel appel métier. Docs de branche 6.6 consultées, pas preuve de test sur 6.6.58.'),
  dict(url='https://www.postgresql.org/docs/18/sql-select.html#SQL-FOR-UPDATE-SHARE',checked_on='2026-10-30',
   interpretation='Une clause de verrouillage ne s’applique pas à un agrégat ; réserve sur la requête SUM/FOR UPDATE observée côté ERPNext, sans déduire le comportement de MariaDB.')
 ]))
 unions={}
 for p in products:
  items=[f for c in chains if c['product']==p for f in c['files']]
  all_nodes=set();domain=set();framework=set();byrole=defaultdict(set);methods=set()
  for f in items:
   for m in f['methods']:methods.add((f['repo'],f['path'],m['start'],m['end']))
   for n in f['counted_nodes']:
    key=(f['repo'],f['path'],n['start'],n['end'],n['kind']);all_nodes.add(key);byrole[f['role']].add(key)
    (framework if f['role']=='framework_reused' else domain).add(key)
  assert domain.isdisjoint(framework)
  old=load(f'audits/2026-10-30-stock-mesures-03/{p}-mesures.json')
  old_nodes={(f['repo'],f['path'],n['start'],n['end'],n['kind']) for f in old['files'] for n in f['counted_nodes']}
  unions[p]=dict(native_domain_program_units=len(domain),framework_program_units_observed_not_recharged=len(framework),
    unique_method_count=len(methods),source_files=len({(f['repo'],f['path']) for f in items}),
    domain_nodes_already_in_iteration03=len(domain&old_nodes),additional_domain_nodes_measured=len(domain-old_nodes),
    per_chain_domain_unit_sum=sum(sum(c['units_by_role'][r] for r in ['stock_quantity','coupled_native','native_integration']) for c in chains if c['product']==p),
    note='Union sans doublon des deux dossiers. Contient des responsabilités natives mêlées et des composants entiers ; aucune conversion automatique en coût Stock.')
  unions[p]['domain_overlap_between_chains']=unions[p]['per_chain_domain_unit_sum']-len(domain)
 write('mesures-union.json',unions)
 report=dict(id='stock-chaines-06',scope='Deux chaînes dans chacun des quatre OSS natifs ; pas toute la famille Stock, pas intégration Beaumanoir.',
  status='huit_dossiers_natifs_mesures_chiffrage_Flow_non_recevable',
  scenarios=dict(
   correction='Delta de quantité pris en compte à une date d’effet passée, actualisation des positions concernées ; distinguer date d’effet et état des connaissances.',
   reservation='Deux demandes portant sur une même portion produit/lieu/unité, contrôle disponible et engagement protégés dans une transaction ; distinguer conflit SQL et nouvel appel métier rejoué.',
   conditions=['Standard des révisions épinglées ; extensions installées non présumées.','Moteur de base et niveau d’isolation sont des conditions de la référence.','La mesure inclut les composants natifs nécessaires même quand une responsabilité excédentaire est mêlée. Cette inclusion est une limite, pas une charge Flow automatique.']),
  results=[dict(product=p,correction=CHAIN_NOTES[p+'-correction']['result'],reservation=CHAIN_NOTES[p+'-reservation']['result'],
   correction_jh=None,reservation_jh=None,stock_family_jh=None,measured_sizes=unions[p]) for p in products],
  what_really_progressed=[
   'Les hooks de persistance et la fin de transaction sont reliés aux traitements métier ; on ne confond plus le corps d’une petite méthode avec le travail complet.',
   'Odoo : le retry couvre la transaction et son flush, avec cinq tentatives ; date de ligne liée à la date du mouvement.',
   'Tryton : verrou avant la lecture des quantités dans assign_try, transition et reprise transactionnelle RPC identifiées.',
   'Axelor : protection de version héritée du framework et reconstruction globale Stock existantes identifiées. Aucune absence de protection déduite de l’absence de FOR UPDATE.',
   'ERPNext : propagation ordonnée et borne au prochain inventaire reliées au moteur courant ; création concurrente du Bin distinguée de la protection des réservations.'],
  remaining_uncertainty=[
   'Les protections transactionnelles natives ne démontrent pas l’idempotence d’un nouvel appel métier après perte de réponse.',
   'Le contrat Flow selon date de fait et date de connaissance n’est pas équivalent aux seules requêtes natives à date d’effet.',
   'Quantités, valorisation et exécution/affectation restent couplées dans plusieurs composants natifs ; leur taille intégrale serait un mauvais coût Flow.',
   'Objectifs de volume/latence/reprise et maîtrise de la stack restent des hypothèses. L’absence de tests OSS exécutés n’est pas, à elle seule, le motif de refus du chiffrage.'],
  uncertainty_assessment=dict(understanding_of_mechanisms_improved=True,effort_interval_narrowing_demonstrated=False,
    numeric_confidence=None,alignment=None,reason='Des dépendances sont résolues et certains travaux génériques ne sont plus supposés absents ; aucune réduction chiffrée de l’incertitude sur les JH n’est démontrée.'),
  cost_decision=dict(COCOMO_executed=False,reason='Pas d’assiette comparable complète après séparation des responsabilités ; aucun total autonome ni extrapolation aux huit capacités.',
    COSMIC_recounted=False,reason_COSMIC='Les deux chaînes sont des mécanismes internes qui recoupent plusieurs processus déjà comptés. Ne pas leur attribuer des CFP additionnels.',
    stock_retained_jh=None,cumulative_retained_gross_jh=1500,master_data_months=17,roles_unchanged=True),
  progress=dict(current_campaign_framed_capabilities=14,total_capabilities=88,framed_pct=100*14/88,
   adopted_capabilities=6,adopted_pct=100*6/88,stock_capabilities_studied=8,stock_capabilities_with_accepted_full_estimate=0,
   chain_dossiers_completed=8,chain_dossiers_target=8,chain_dossiers_pct=100,
   native_complete_stock_family_costs_receivable=0,new_capabilities_adopted=0,remaining_java_not_adopted=82,
   historical_note='Les 88 capacités ont des repérages historiques ; les 14 désignent le cadrage de la méthode actuelle. Huit dossiers de chaîne ne sont pas huit capacités chiffrées.'),
  next_iteration=dict(repeat_reading_same_chains_worthwhile=False,change_approach_worthwhile=True,
    recommendation='Arrêter le raffinement des mêmes chaînes. Chiffrer au niveau de composants Stock cohérents, avec frontières quantitatives/valorisation/exécution explicites, puis borner les compléments Flow ; ne plus multiplier un catalogue de petites méthodes.',
    prerequisite='Choisir et documenter un périmètre natif de référence suffisamment complet. Les compléments temporels et de rejeu restent des adaptations, avec réutilisation de Master Data qualifiée.',
    no_external_project_actuals_required=True,
    stop_condition='Si le périmètre ne peut pas être isolé sans inventer sa taille, annoncer l’échec de cette transposition et conserver le coût inconnu. Pas de nouvelle itération de simple inspection de ces huit dossiers.'),
  evidence=['erpnext-correction.json','erpnext-reservation.json','odoo-correction.json','odoo-reservation.json','tryton-correction.json','tryton-reservation.json','axelor-correction.json','axelor-reservation.json','mesures-union.json','preuves-complementaires.json'])
 (OUT/'bilan.yaml').write_text(yaml.safe_dump(report,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
 for p,h in protected.items():assert digest(ROOT/p)==h,p
 deps=set(protected_paths+['source/README.md','source/statut-evaluation.yaml','audits/2026-10-30-stock-perimetres-02/build.py','audits/2026-10-30-master-data-natif/measure.py','audits/2026-10-30-master-data-comparable-reuse/measurements.json','audits/2026-10-30-stock-dimensionnement-05/bilan.yaml'])
 # source/README belongs to parallel work; keep its read snapshot out of the protected economic set.
 for c in chains:
  for f in c['files']:deps.add(str((Path(repos[f['repo']]['root'])/f['path'])).replace('\\','/'))
 for f in evidence+tests:deps.add(str((Path(repos[f['repo']]['root'])/f['path'])).replace('\\','/'))
 for p in products:deps.add(f'audits/2026-10-30-stock-mesures-03/{p}-mesures.json')
 deps.add(str(Path(__file__).resolve().relative_to(ROOT)).replace('\\','/'))
 for name in report['evidence']+['bilan.yaml']:deps.add(str((OUT/name).relative_to(ROOT)).replace('\\','/'))
 write('provenance.json',dict(protected=protected,dependencies=[dict(path=p,sha256=digest(ROOT/p)) for p in sorted(deps)]))
 print(json.dumps(dict(chains=8,unions=unions,cumulative_jh=1500,stock_receivable_jh=None),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
