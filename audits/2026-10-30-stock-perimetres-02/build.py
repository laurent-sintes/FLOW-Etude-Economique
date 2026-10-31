"""Build four reproducible, method-scoped stock code perimeters; no effort adoption."""
from pathlib import Path
import ast,json,hashlib,sys,subprocess,re,xml.etree.ElementTree as ET
import yaml
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tmp/master-data-native-23/parser-deps'))
from tree_sitter import Parser,Language
import tree_sitter_java
JAVA=Parser(Language(tree_sitter_java.language()))
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
md=load('audits/2026-10-30-master-data-comparable-reuse/measurements.json');repos=md['repos']
spec={}
def add(product,path,methods,contracts,mixed=()):
 spec.setdefault(product,[]).append(dict(path=path,methods=methods.split(),contracts=contracts.split(),mixed=list(mixed)))
add('erpnext','erpnext/stock/stock_ledger.py','get_previous_sle get_stock_ledger_entries get_prior_ledger_condition validate_item_warehouse update_qty_in_future_sle get_stock_reco_qty_shift get_next_reco_datetime_condition get_datetime_limit_condition','C1 C2',('make_entry','make_sl_entries','repost_future_sle','update_entries_after.process_sle'))
add('erpnext','erpnext/stock/doctype/stock_ledger_entry/stock_ledger_entry.py','StockLedgerEntry.autoname StockLedgerEntry.set_posting_datetime StockLedgerEntry.get_dimension_sle_query StockLedgerEntry.get_future_dimension_qty StockLedgerEntry.validate_mandatory StockLedgerEntry.block_transactions_against_group_warehouse','C1',('StockLedgerEntry.on_submit','StockLedgerEntry.validate'))
add('erpnext','erpnext/stock/doctype/bin/bin.py','Bin.set_projected_qty Bin.update_reserved_stock get_bin_details get_projected_qty_term get_actual_qty','C2 C4 C5',('Bin.recalculate_values','Bin.set_stock_values_from_ledger'))
add('erpnext','erpnext/stock/doctype/stock_reservation_entry/stock_reservation_entry.py','StockReservationEntry.update_reserved_stock_in_bin StockReservationEntry.update_status StockReservationEntry.get_total_reserved_qty StockReservationEntry.get_row_reserved_qty get_sre_reserved_qty_for_item_and_warehouse get_sre_reserved_qty_for_items_and_warehouses get_status','C4',('StockReservation.make_stock_reservation_entry','StockReservationEntry.validate_reserved_entries','StockReservationEntry.validate_with_allowed_qty'))
add('erpnext','erpnext/stock/doctype/stock_reconciliation/stock_reconciliation.py','StockReconciliation.get_item_warehouses_changing_qty StockReconciliation.get_balance_before_reconciliation StockReconciliation.get_current_qty_from_ledger StockReconciliation.is_adjustment_row','C3',('StockReconciliation.get_previous_ledger_entry','StockReconciliation.validate_data','StockReconciliation.update_stock_ledger','StockReconciliation.on_submit'))
add('erpnext','erpnext/stock/report/stock_balance/stock_balance.py','StockBalanceReport.get_group_by_key StockBalanceReport.apply_inventory_dimensions_filters StockBalanceReport.apply_warehouse_filters StockBalanceReport.apply_items_filters StockBalanceReport.apply_date_filters','C2',('StockBalanceReport.prepare_sle_query','StockBalanceReport.run','StockBalanceReport.get_item_warehouse_balance'))
add('odoo','addons/stock/models/stock_quant.py','StockQuant._compute_available_quantity StockQuant._compute_inventory_diff_quantity StockQuant._compute_inventory_quantity_set StockQuant._compute_is_outdated StockQuant._search_is_outdated StockQuant._get_gather_domain StockQuant._gather StockQuant._get_available_quantity StockQuant._get_quants_by_products_locations StockQuant._update_available_quantity StockQuant._update_reserved_quantity StockQuant._get_inventory_move_values StockQuant.action_clear_inventory_quantity','C1 C2 C3 C4',('StockQuant._apply_inventory','StockQuant._get_reserve_quantity','StockQuant.create'))
add('odoo','addons/stock/models/product.py','ProductProduct._compute_quantities ProductProduct._compute_quantities_dict ProductProduct._get_domain_locations ProductProduct._get_domain_locations_new ProductProduct._search_qty_available ProductProduct._search_free_qty ProductProduct._search_field_by_quants ProductProduct._get_dates_info ProductProduct._get_only_qty_available','C2 C5')
add('odoo','addons/stock/models/stock_move.py','StockMove._compute_quantity_product_uom StockMove._compute_product_qty StockMove._get_available_quantity StockMove._get_quantity_field StockMove._get_product_uom_field','C1 C2',('StockMove._action_done','StockMove._action_assign','StockMove._action_cancel'))
add('odoo','addons/stock/models/stock_lot.py','StockLot._product_qty StockLot._search_product_qty','C2')
add('tryton','modules/stock/move.py','StockMixin._quantity_context StockMixin._get_quantity StockMixin._search_quantity Move.assign Move.cancel Move._assign_try_lock Move.compute_quantities_query Move.compute_quantities _location_children','C1 C2 C4 C5',('Move.do','Move.assign_try'))
add('tryton','modules/stock/product.py','Product._quantity_locations Product.get_quantity Product.search_quantity Product.products_by_location ProductQuantitiesByWarehouse.get_quantity ProductQuantitiesByWarehouseMove.get_cumulative_quantity','C2 C5')
add('tryton','modules/stock/inventory.py','Inventory.default_date Inventory.default_state Inventory.complete_lines Inventory.grouping InventoryLine.default_expected_quantity InventoryLine.on_change_with_quantity_variation InventoryLine.unique_key InventoryLine.get_move InventoryLine.cancel_move InventoryLine.update_for_complete','C3',('Inventory.confirm','Inventory.check_tolerance','InventoryLine.on_change_with_tolerance_quantity_variation'))
add('tryton','modules/stock/location.py','Location._get_quantity_grouping Location.get_quantity Location.search_quantity Location.get_quantity_uom','C2')
A='axelor-stock/src/main/java/com/axelor/apps/stock/service/'
add('axelor',A+'StockLocationLineServiceImpl.java','updateLocation@392 getOrCreateStockLocationLine getOrCreateDetailLocationLine createLocationLine createDetailLocationLine convertToProductUnit convertFromProductUnit productUnit convert computeFutureQty getCompany','C1 C2 C5',('updateHistory','updateLocation@137','updateDetailLocation','getStockLocationLineValue'))
add('axelor',A+'StockLocationLineFetchServiceImpl.java','getAvailableQty getStockLocationLine getStockLocationLines getStockLocationLineListForAProduct getAvailableStockForAProduct getRequestedReservedQtyForAProduct getTrackingNumberAvailableQty getDetailLocationLine getDetailLocationLines getTrackingNumberAvailableQtyIncludingSubLocations','C2 C4')
add('axelor',A+'StockLocationLineHistoryServiceImpl.java','getStockLineHistoryLines','C1 C2',('saveHistory',))
add('axelor',A+'inventory/InventoryLineServiceImpl.java','getCurrentQty getCurrentQtyInProductUnit missingUnitException isPresentInStockLocation','C3',('compute','createInventoryLine','updateInventoryLine'))
add('axelor',A+'inventory/InventoryValidateServiceImpl.java','computeDiff checkMissingStockLocation getStockMoveLinesCount','C3',('validate','generateStockMove','generateStockMoveLines','realizeGeneratedStockMoves'))
add('axelor',A+'inventory/InventoryStockLocationUpdateServiceImpl.java','fetchDistinctProductIdsPage fetchInventoryLinesForProducts fetchStockLocationLinesForProducts buildTrackedMap sumRealQty','C3',('storeLastInventoryData','processPage','updateLine'))
add('axelor','axelor-supplychain/src/main/java/com/axelor/apps/supplychain/service/ReservedQtyServiceImpl.java','computeRealReservedQty convertUnitWithProduct updateRequestedReservedQty@936 updateReservedQty@994 checkBeforeUpdatingQties','C4',('updateReservedQuantity','updateReservedQty@777','allocateAll','requestQty'))
# Explicit declaration allowlists. Other fields (including finance and operations) are excluded.
fields={
'erpnext':{
'erpnext/stock/doctype/stock_ledger_entry/stock_ledger_entry.json':'item_code warehouse actual_qty stock_uom qty_after_transaction company posting_date posting_time posting_datetime voucher_type voucher_no voucher_detail_no serial_no batch_no is_cancelled is_adjustment_entry serial_and_batch_bundle',
'erpnext/stock/doctype/bin/bin.json':'warehouse item_code actual_qty reserved_qty reserved_stock ordered_qty planned_qty indented_qty projected_qty stock_uom company',
'erpnext/stock/doctype/stock_reservation_entry/stock_reservation_entry.json':'item_code warehouse company stock_uom reserved_qty delivered_qty consumed_qty transferred_qty status voucher_type voucher_no voucher_detail_no amended_from available_qty',
'erpnext/stock/doctype/stock_reconciliation/stock_reconciliation.json':'naming_series company posting_date posting_time items amended_from',
'erpnext/stock/doctype/stock_reconciliation_item/stock_reconciliation_item.json':'item_code warehouse qty stock_uom current_qty quantity_difference serial_no batch_no serial_and_batch_bundle current_serial_and_batch_bundle'},
'odoo':{'addons/stock/models/stock_quant.py':'product_id location_id lot_id package_id owner_id company_id quantity reserved_quantity available_quantity inventory_quantity inventory_diff_quantity inventory_date in_date',
'addons/stock/models/stock_move.py':'reference product_id location_id location_dest_id product_uom_qty quantity uom_id date state move_orig_ids move_dest_ids origin'},
'tryton':{'modules/stock/move.py':'product quantity internal_quantity unit from_location to_location effective_date planned_date state company origin',
'modules/stock/inventory.py':'location date company state lines product quantity expected_quantity inventory moves',
'modules/stock/product.py':'quantity forecast_quantity'},
'axelor':{
'axelor-stock/src/main/resources/domains/StockLocationLine.xml':'stockLocation product unit currentQty futureQty lastFutureStockMoveDate trackingNumber detailsStockLocation lastInventoryRealQty lastInventoryDateT',
'axelor-stock/src/main/resources/domains/StockLocationLineHistory.xml':'stockLocationLine typeSelect dateT origin qty unit',
'axelor-stock/src/main/resources/domains/StockMove.xml':'stockMoveSeq fromStockLocation toStockLocation estimatedDate realDate statusSelect company stockMoveLineList origin isReversion reversionOriginStockMove',
'axelor-stock/src/main/resources/domains/StockMoveLine.xml':'stockMove fromStockLocation toStockLocation product qty realQty oldQty unit trackingNumber',
'axelor-stock/src/main/resources/domains/Inventory.xml':'inventorySeq stockLocation statusSelect plannedStartDateT plannedEndDateT company inventoryLineList validatedBy validatedOn',
'axelor-stock/src/main/resources/domains/InventoryLine.xml':'inventory product currentQty realQty unit trackingNumber gap stockLocation',
'axelor-supplychain/src/main/resources/domains/StockLocationLine.xml':'reservedQty requestedReservedQty',
'axelor-supplychain/src/main/resources/domains/StockMoveLine.xml':'reservedQty requestedReservedQty'}}
views={
'erpnext':['erpnext/stock/doctype/stock_ledger_entry/stock_ledger_entry.js','erpnext/stock/doctype/stock_reconciliation/stock_reconciliation.js','erpnext/stock/doctype/stock_reservation_entry/stock_reservation_entry.js'],
'odoo':['addons/stock/views/stock_quant_views.xml','addons/stock/views/stock_move_views.xml','addons/stock/security/ir.access.csv'],
'tryton':['modules/stock/view/inventory_form.xml','modules/stock/view/inventory_line_form.xml','modules/stock/view/move_form.xml','modules/stock/view/product_quantities_warehouse_list.xml','modules/stock/stock.xml'],
'axelor':['axelor-stock/src/main/resources/views/StockLocationLine.xml','axelor-stock/src/main/resources/views/Inventory.xml','axelor-stock/src/main/resources/views/StockMove.xml']}
def parse(file):
 raw=file.read_bytes();text=raw.decode('utf-8-sig');methods=[];declarations=[]
 if file.suffix=='.py':
  tree=ast.parse(text)
  def visit(node,parent=''):
   for n in ast.iter_child_nodes(node):
    if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
     start=min([n.lineno]+[d.lineno for d in n.decorator_list])
     calls=[]
     for c in ast.walk(n):
      if isinstance(c,ast.Call):calls.append(ast.unparse(c.func))
     methods.append(dict(name=parent+n.name,start=start,end=n.end_lineno,calls=sorted(set(calls))))
    elif isinstance(n,ast.ClassDef):visit(n,n.name+'.')
    elif isinstance(n,(ast.Assign,ast.AnnAssign)):
     targets=n.targets if isinstance(n,ast.Assign) else [n.target]
     for t in targets:
      if isinstance(t,ast.Name):declarations.append(dict(name=t.id,owner=parent.rstrip('.'),start=n.lineno,end=n.end_lineno))
    else:visit(n,parent)
  visit(tree)
 elif file.suffix=='.java':
  tree=JAVA.parse(raw);assert not tree.root_node.has_error,file
  def visit(n):
   if n.type in ('method_declaration','constructor_declaration'):
    key=n.child_by_field_name('name');calls=[]
    def find(c):
     if c.type=='method_invocation':
      nm=c.child_by_field_name('name');obj=c.child_by_field_name('object')
      if nm:calls.append(((raw[obj.start_byte:obj.end_byte].decode()+'.') if obj else '')+raw[nm.start_byte:nm.end_byte].decode())
     for child in c.named_children:find(child)
    find(n)
    methods.append(dict(name=raw[key.start_byte:key.end_byte].decode(),start=n.start_point.row+1,end=n.end_point.row+1,calls=sorted(set(calls))))
   else:
    for c in n.named_children:visit(c)
  visit(tree.root_node)
 elif file.suffix=='.json':
  doc=json.loads(text);declarations=[dict(name=f['fieldname'],owner=doc.get('name')) for f in doc.get('fields',[])]
 elif file.suffix=='.xml':
  tree=ET.fromstring(text)
  for entity in tree.iter():
   if entity.tag.split('}')[-1]=='entity':
    for child in entity:
     if child.get('name') and child.tag.split('}')[-1] not in ('finder-method','extra-code','index'):declarations.append(dict(name=child.get('name'),owner=entity.get('name')))
 return raw,methods,declarations
def matches(m,selector):
 name,_,line=selector.partition('@')
 return m['name']==name and (not line or abs(m['start']-int(line))<=3)
def build():
 evidence=[];overlaps=[];totals={};fail=[]
 for product,files in spec.items():
  root=ROOT/repos[product]['root'];commit=subprocess.check_output(['C:/Program Files/Git/cmd/git.exe','-C',str(root),'rev-parse','HEAD'],text=True).strip();assert commit==repos[product]['commit']
  result=dict(product=product,repository=repos[product]['repository'],commit=commit,scope_status='comparable_outcomes_partial_native_coverage',charge_status='not_costable_until_dependency_and_mixed_boundaries_resolved',methods=[],declarations=[],boundary_methods=[],excluded_methods=[],presentation_dependencies=[],file_proofs=[])
  paths=sorted(set([f['path'] for f in files])|set(fields[product]))
  for path in paths:
   file=root/path;raw,methods,decl=parse(file);digest=sha(raw);proof=dict(repo=product,path=path,sha256=digest);result['file_proofs'].append(proof);evidence.append(proof)
   conf=next((f for f in files if f['path']==path),None)
   selected=[]
   if conf:
    for selector in conf['methods']:
     found=[m for m in methods if matches(m,selector)]
     assert found,(product,path,selector)
     selected.extend(found)
    unique={(m['start'],m['end']):m for m in selected};assert len(unique)==len(selected),(path,'overlapping selectors')
    for m in selected:
     lines=raw.decode('utf-8-sig').splitlines();snippet='\n'.join(lines[m['start']-1:m['end']])
     entry=dict(file=path,**m,contracts=conf['contracts'],slice_sha256=sha(snippet.encode()),type='stock_specific_candidate')
     result['methods'].append(entry)
    for m in methods:
     if m in selected:continue
     entry=dict(file=path,name=m['name'],start=m['start'],end=m['end'])
     if any(matches(m,x) for x in conf['mixed']):
      entry['reason']='Traitement mêlé à une responsabilité exclue ou appel critique non isolé ; non ajouté au périmètre mesurable.'
      result['boundary_methods'].append(entry)
     else:
      entry['reason']='Non retenu dans cette sélection, sans affirmer son absence fonctionnelle.';result['excluded_methods'].append(entry)
   if path in fields[product]:
    names=fields[product][path].split();found={d['name'] for d in decl}
    missing=set(names)-found;assert not missing,(product,path,missing)
    for d in decl:
     if d['name'] in names:result['declarations'].append(dict(file=path,**d))
   mdrows=[r for r in md['files'] if r['product']==product and r['repo']==product and r['path']==path]
   for old in mdrows:
    assert old['sha256']==digest,'OSS source changed since Master Data'
    previous_excluded={x['name'] for x in old['excluded_blocks'] if x['kind']=='method'}
    old_excluded_classes={x['name'] for x in old['excluded_blocks'] if x['kind']=='class'}
    for m in selected:
     name=m['name'].split('.')[-1];cl=m['name'].split('.')[0]
     status='stock_method_previously_excluded_from_master_data' if name in previous_excluded or cl in old_excluded_classes else 'already_funded_in_master_data' if old['treatment']=='new' else 'generic_reuse_already_qualified'
     overlaps.append(dict(product=product,file=path,method=m['name'],start=m['start'],status=status,master_data_measurement='audits/2026-10-30-master-data-comparable-reuse/measurements.json'))
     next(x for x in result['methods'] if x['file']==path and x['start']==m['start'])['type']=status
  selected_names={m['name'].split('.')[-1] for m in result['methods']}
  # This is a syntactic first-level inventory, explicitly not dynamic dispatch resolution.
  calls=[]
  for m in result['methods']:
   for target in m['calls']:
    tail=target.split('.')[-1]
    status='selected_symbol_name_match_requires_dispatch_review' if tail in selected_names else 'framework_or_external_dependency_to_classify'
    calls.append(dict(caller=m['file']+':'+str(m['start']),call=target,status=status))
  result['dependencies']=calls
  for path in views[product]:
   file=root/path;assert file.is_file(),file
   result['presentation_dependencies'].append(dict(path=path,sha256=sha(file.read_bytes()),status='context_only_not_counted',selection_rule='Retenir seulement écrans/permissions des objets et champs sélectionnés ; exclure valorisation, picking, terminaux et actions de workflow non retenues.'))
  assert all(any(cid in m['contracts'] for m in result['methods']) for cid in ('C1','C2','C3','C4','C5'))
  totals[product]=dict(source_files=len(result['file_proofs']),methods=len(result['methods']),declarations=len(result['declarations']),mixed_boundary_methods=len(result['boundary_methods']),presentation_context_files=len(result['presentation_dependencies']),dependency_calls=len(calls))
  (OUT/(product+'-perimetre.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 (OUT/'recoupements-master-data.json').write_text(json.dumps(overlaps,ensure_ascii=False,indent=2),encoding='utf-8')
 (OUT/'verification.json').write_text(json.dumps(dict(status='selection_verified_not_effort_adoption',summary=totals,code_proofs=evidence,method='Qualified methods and explicit declarations; excluded-by-default residual symbols; mixed methods kept as boundary evidence; no code modification or JH conversion.'),ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(dict(summary=totals,master_data_overlaps=overlaps),ensure_ascii=False,indent=2))
if __name__=='__main__':build()
