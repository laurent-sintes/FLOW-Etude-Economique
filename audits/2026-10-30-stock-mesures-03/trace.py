"""Static evidence for twelve critical stock paths, with explicit shared ownership."""
from pathlib import Path
import json,sys,hashlib,importlib.util
import yaml
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tmp/master-data-native-23/parser-deps'))
spec=importlib.util.spec_from_file_location('scope',ROOT/'audits/2026-10-30-stock-perimetres-02/build.py')
scope=importlib.util.module_from_spec(spec);spec.loader.exec_module(scope)
md=json.loads((ROOT/'audits/2026-10-30-master-data-comparable-reuse/measurements.json').read_text(encoding='utf-8'))
nodes={};traces=[]
def node(repo,path,name,required=()):
 key=repo+'/'+path+'#'+name
 if key in nodes:return key
 f=ROOT/md['repos'][repo]['root']/path;raw,methods,fields=scope.parse(f)
 exact=[m for m in methods if scope.matches(m,name)]
 if not exact:exact=[m for m in methods if m['name'].endswith('.'+name)]
 assert exact,(repo,path,name)
 # overloads are retained as distinct evidence, not all charged to the stock scope.
 evidence=[]
 for m in exact:
  text='\n'.join(raw.decode('utf-8-sig').splitlines()[m['start']-1:m['end']])
  for token in required:assert token in text,(name,token)
  evidence.append(dict(name=m['name'],start=m['start'],end=m['end'],slice_sha256=hashlib.sha256(text.encode()).hexdigest()))
 matches=[r for r in md['files'] if r['repo']==repo and r['path']==path]
 shared=any(r['treatment']=='reused' for r in matches)
 nodes[key]=dict(repo=repo,path=path,sha256=hashlib.sha256(raw).hexdigest(),commit=md['repos'][repo]['commit'],symbols=evidence,
 funding_owner='master-data-java-spring' if shared else 'stock_candidate_or_external_boundary',
 measured_in_stock=False if shared else 'only_if_explicit_in_measured_selection',
 master_data_proof='audits/2026-10-30-master-data-comparable-reuse/measurements.json' if shared else None)
 return key
E='erpnext/stock/';O='addons/stock/models/';T='modules/stock/';A='axelor-stock/src/main/java/com/axelor/apps/stock/service/';R='axelor-supplychain/src/main/java/com/axelor/apps/supplychain/service/'
F='frappe/model/document.py';M='odoo/orm/models.py';W='trytond/trytond/model/workflow.py';SQL='trytond/trytond/model/modelsql.py';J='axelor-core/src/main/java/com/axelor/db/'
def n(repo,path,sym,*tokens):return node(repo,path,sym,tokens)
def trace(product,kind,steps,conclusion,limit):
 traces.append(dict(id=product+'-'+kind,product=product,kind=kind,steps=steps,status='statique_chemin_et_frontieres_qualifies',conclusion=conclusion,limit=limit,runtime_executed=False))
trace('erpnext','ecriture',[
 n('erpnext',E+'stock_ledger.py','make_entry','sle.submit()'),
 n('frappe',F,'Document.submit','self._submit()'),n('frappe',F,'Document._submit','self.save()'),
 n('frappe',F,'Document.save','self._save('),n('frappe',F,'Document._save','self.db_update()'),
 n('frappe',F,'Document.db_update','frappe.db.sql','UPDATE')],
 'Le document métier délègue la persistance au framework Frappe déjà qualifié.',
 'Les hooks de validation/serial-batch et la transaction complète ne sont pas exécutés. Les paramètres de valorisation transmis ne sont pas un moteur financier.')
trace('erpnext','correction',[
 n('erpnext',E+'stock_ledger.py','update_qty_in_future_sle','.set(sle.qty_after_transaction','query.run()'),
 n('erpnext',E+'stock_ledger.py','get_stock_reco_qty_shift'),
 n('erpnext',E+'stock_ledger.py','get_next_stock_reco'),
 n('erpnext',E+'stock_ledger.py','validate_negative_qty_in_future_sle')],
 'La correction de quantité se propage dans les écritures futures avec une borne au prochain inventaire.',
 'Le recalcul financier séparé reste exclu. Le code natif ne démontre pas le contrat Flow complet de double date et de rejeu.')
trace('erpnext','concurrence',[
 n('erpnext',E+'doctype/stock_reservation_entry/stock_reservation_entry.py','get_available_qty_to_reserve','.for_update()'),
 n('erpnext',E+'doctype/stock_reservation_entry/stock_reservation_entry.py','StockReservationEntry.validate_with_allowed_qty','get_available_qty_to_reserve('),
 n('erpnext',E+'doctype/stock_reservation_entry/stock_reservation_entry.py','StockReservationEntry.get_from_voucher_reservation_entries','.for_update()')],
 'Requêtes de verrouillage explicites repérées dans le calcul et le transfert des réservations.',
 'Pas de preuve de sérialisation complète du stock et des réservations, notamment premier enregistrement, ordre des verrous et retries.')
trace('odoo','ecriture',[
 n('odoo',O+'stock_move_line.py','StockMoveLine._synchronize_quant','._update_available_quantity('),
 n('odoo',O+'stock_quant.py','StockQuant._update_available_quantity','quant.write(vals)'),
 n('odoo',M,'write','field.write(self, value)'),n('odoo','odoo/orm/fields.py','Field.write','dirty=True'),n('odoo',M,'flush_model','self._flush()'),n('odoo',M,'_flush','._write_multi(vals_list)'),n('odoo',M,'_write_multi','UPDATE')],
 'Les champs sont modifiés en cache puis écrits lors du flush ORM ; ce chemin est distinct de la construction des opérations physiques.',
 'Les extensions de modèle et triggers natifs ne sont pas exécutés ; seuls les traitements explicitement sélectionnés sont mesurés.')
trace('odoo','correction',[
 n('odoo',O+'stock_quant.py','StockQuant._apply_inventory','._action_done()'),
 n('odoo',O+'stock_move.py','StockMove._action_done'),
 n('odoo',O+'stock_move_line.py','StockMoveLine._action_done','._synchronize_quant('),
 n('odoo',O+'stock_move_line.py','StockMoveLine._synchronize_quant')],
 'Un ajustement crée un mouvement qui synchronise les quantités ; le chemin appelant est distingué du noyau mesuré.',
 'Le workflow complet, les emballages et déclencheurs d’affectation ne sont pas tous inclus ; pas d’équivalence automatique avec ingestion d’un fait externe.')
trace('odoo','concurrence',[
 n('odoo',O+'stock_quant.py','StockQuant._update_available_quantity','try_lock_for_update('),
 n('odoo',M,'try_lock_for_update','SKIP LOCKED')],
 'Verrouillage natif observé sur les quants existants avant modification.',
 'La branche de création, les contraintes d’unicité et les retries doivent être testés ; SKIP LOCKED ne prouve pas à lui seul toutes les garanties Flow.')
trace('tryton','ecriture',[
 n('tryton',T+'move.py','Move.assign'),n('tryton',W,'Workflow.transition','cls.write(to_update'),
 n('tryton',SQL,'ModelSQL.write','table.update(')],
 'La transition écrit son état via le modèle SQL : le corps assign seul ne représente pas toute la persistance.',
 'Le décorateur et le modèle SQL sont des dépendances partagées. Les validations automatiques restent à qualifier hors de la mesure locale.')
trace('tryton','correction',[
 n('tryton',T+'inventory.py','Inventory.confirm','Move.save(moves)','Move.do(moves)'),
 n('tryton',T+'inventory.py','InventoryLine.get_move'),
 n('tryton',T+'move.py','Move.do',"move.state = 'done'"),
 n('tryton',W,'Workflow.transition')],
 'L’inventaire construit les mouvements correctifs ; leur état participe au calcul des quantités.',
 'Move.do mêle les coûts et le stock : il est documenté mais pas compté intégralement. Les prix et le recalcul financier sont hors périmètre.')
trace('tryton','concurrence',[
 n('tryton',T+'move.py','Move.assign_try','cls._assign_try_lock('),
 n('tryton',T+'move.py','Move._assign_try_lock',"for_=For('UPDATE'",'cls.lock()'),
 n('tryton',SQL,'ModelSQL.lock')],
 'Verrouillage SQL ou de modèle observé dans le chemin d’affectation natif.',
 'La politique de choix de ressource de assign_try reste hors du noyau de réservation. Pas de test de contention exécuté.')
trace('axelor','ecriture',[
 n('axelor',A+'StockLocationLineServiceImpl.java','updateLocation@137','stockLocationLineRepo.save('),
 n('axelor',A+'StockLocationLineServiceImpl.java','updateLocation@392','setCurrentQty('),
 n('platform',J+'JpaRepository.java','save','JPA.save('),
 n('platform',J+'JPA.java','save','persist(')],
 'La mise à jour des quantités est identifiée jusqu’à la frontière de persistance JPA.',
 'Les branches min/max de réapprovisionnement sont retranchées du comptage ; l’injection des extensions et la transaction effective ne sont pas testées.')
trace('axelor','correction',[
 n('axelor',A+'inventory/InventoryValidateServiceImpl.java','generateStockMoves'),
 n('axelor',A+'inventory/InventoryValidateServiceImpl.java','realizeGeneratedStockMoves'),
 n('axelor',A+'StockMoveServiceImpl.java','realize'),
 n('axelor',A+'StockMoveLineServiceImpl.java','updateLocations')],
 'La validation produit des mouvements correctifs ; leur réalisation actualise les positions.',
 'Ce chemin passe par le service de mouvement et ses extensions. Le workflow complet et la valorisation restent en frontière, pas facturés automatiquement.')
trace('axelor','concurrence',[
 n('axelor',R+'ReservedQtyServiceImpl.java','updateReservedQty@767','@Transactional'),
 n('axelor',R+'ReservedQtyServiceImpl.java','updateReservedQty@776','availableQtyToBeReserved'),
 n('axelor',R+'ReservedQtyServiceImpl.java','updateReservedQty@994','setReservedQty(')],
 'Transaction et contrôles de quantité repérés ; le code examiné ne suffit pas à établir un verrou exclusif sur la réservation.',
 'Garantie concurrente non démontrée : inspecter contraintes, verrouillage fourni par le runtime et éventuel protocole de retry. Ne pas déclarer Axelor dépourvu de mécanisme global.')
result=dict(traces=traces,nodes=nodes,trace_count=len(traces),static_only=True,shared_platform_code_recharged=False)
(OUT/'chemins-critiques.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(traces=len(traces),evidence_nodes=len(nodes),shared_nodes=sum(v['funding_owner']=='master-data-java-spring' for v in nodes.values())),ensure_ascii=False))
