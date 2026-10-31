"""Measure stock selections and record the resolved responsibility of critical calls."""
from pathlib import Path
import json,ast,sys,hashlib,importlib.util,subprocess
import yaml
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tmp/master-data-native-23/parser-deps'))
spec=importlib.util.spec_from_file_location('stock_scope_builder',ROOT/'audits/2026-10-30-stock-perimetres-02/build.py')
scope=importlib.util.module_from_spec(spec);spec.loader.exec_module(scope)
spec=importlib.util.spec_from_file_location('native_counter',ROOT/'audits/2026-10-30-master-data-natif/measure.py')
counter=importlib.util.module_from_spec(spec);spec.loader.exec_module(counter)
repos=scope.repos
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
additions={
'erpnext':[
('erpnext/stock/stock_ledger.py','make_entry get_args_for_future_sle get_next_stock_reco validate_negative_qty_in_future_sle get_future_sle_with_negative_qty get_future_sle_with_negative_batch_qty get_sle_against_current_voucher get_previous_sle_of_current_voucher get_sle_entries_by_names validate_cancellation set_as_cancel'),
('erpnext/stock/doctype/stock_reservation_entry/stock_reservation_entry.py','get_available_qty_to_reserve StockReservationEntry.validate_with_allowed_qty StockReservationEntry.get_from_voucher_reservation_entries'),
('erpnext/stock/doctype/bin/bin.py','update_qty update_bin_columns get_last_sle_values')],
'odoo':[
('addons/stock/models/stock_quant.py','StockQuant._apply_inventory StockQuant._clean_reservations StockQuant._unlink_zero_quants'),
('addons/stock/models/stock_move_line.py','StockMoveLine._synchronize_quant')],
'tryton':[
('modules/stock/inventory.py','Inventory.confirm InventoryLine.on_change_with_tolerance_quantity_variation'),
('modules/stock/move.py','Move.set_effective_date Move.check_origin')],
'axelor':[
('axelor-stock/src/main/java/com/axelor/apps/stock/service/StockLocationLineServiceImpl.java','updateLocation@137 updateDetailLocation updateHistory'),
('axelor-stock/src/main/java/com/axelor/apps/stock/service/StockLocationLineHistoryServiceImpl.java','saveHistory'),
('axelor-stock/src/main/java/com/axelor/apps/stock/service/inventory/InventoryLineServiceImpl.java','compute'),
('axelor-stock/src/main/java/com/axelor/apps/stock/service/inventory/InventoryStockLocationUpdateServiceImpl.java','updateLine'),
('axelor-supplychain/src/main/java/com/axelor/apps/supplychain/service/ReservedQtyServiceImpl.java','updateReservedQty@767 updateReservedQty@776 updateRequestedReservedQty@817 updateRequestedReservedQty@826 checkAvailabilityRequest')]}
# Excluded source statements/branches. These are source measurements, not rewritten executable forks.
prunes={
('axelor','StockLocationLineServiceImpl.java','updateLocation',137):[(181,183,'Déclenchement de règle de réapprovisionnement'),(196,196,'Alerte/règle minimum hors noyau quantité')],
('axelor','StockLocationLineServiceImpl.java','updateDetailLocation',255):[(0,0,'placeholder')],
}
# Store exact source-line decisions below after validating them against method boundaries.
all_results={};proofs=[];residuals=[]
def measure():
 for product in ('erpnext','odoo','tryton','axelor'):
  base=load(ROOT/f'audits/2026-10-30-stock-perimetres-02/{product}-perimetre.json')
  root=ROOT/repos[product]['root']
  commit=subprocess.check_output(['C:/Program Files/Git/cmd/git.exe','-C',str(root),'rev-parse','HEAD'],text=True).strip();assert commit==repos[product]['commit']
  selected={ (m['file'],m['start'],m['end']):dict(m,origin='iteration_02') for m in base['methods']}
  for path,names in additions[product]:
   raw,methods,fields=scope.parse(root/path)
   for name in names.split():
    found=[m for m in methods if scope.matches(m,name)];assert found,(product,path,name)
    for m in found:selected.setdefault((path,m['start'],m['end']),dict(file=path,**m,origin='critical_call_resolution'))
  # Declarations have their own source spans in Python and exact owner/name in JSON/XML.
  declarations=base['declarations']
  by_path={}
  for m in selected.values():by_path.setdefault(m['file'],[]).append(m)
  for d in declarations:by_path.setdefault(d['file'],[])
  measured=[];program=declarative=0;excluded_program=0
  for path,methods in sorted(by_path.items()):
   f=root/path;raw=f.read_bytes();text=raw.decode('utf-8-sig');lines=text.splitlines()
   expected=next((p['sha256'] for p in base['file_proofs'] if p['path']==path),None)
   if expected:assert expected==sha(raw)
   spans=[(m['start'],m['end']) for m in methods]
   fields=[d for d in declarations if d['file']==path]
   removed=[]
   if product=='axelor' and path.endswith('StockLocationLineServiceImpl.java'):
    for m in methods:
     if m['name']=='updateLocation' and 135<=m['start']<=139:
      removed.extend([(181,183,'Réapprovisionnement'),(196,196,'Règle minimum')])
   if product=='axelor' and path.endswith('/InventoryLineServiceImpl.java'):
    # compute: keep quantity rounding and gap, drop the price choice and monetary values.
    for m in methods:
     if m['name']=='compute':
      begin=next(i for i in range(m['start'],m['end']+1) if lines[i-1].strip()=='BigDecimal price;')
      end=next(i for i in range(begin,m['end']+1) if lines[i-1].strip()=='return inventoryLine;')-1
      removed.append((begin,end,'Valorisation et écarts monétaires'))
   def inside(a,b):return any(start<=a and b<=end for start,end in spans)
   def dropped(a,b):return any(start<=a and b<=end for start,end,_ in removed)
   pu=du=cut=0;nodes=[]
   if f.suffix=='.py':
    tree=ast.parse(text)
    field_spans={(d['start'],d['end']) for d in fields}
    for n in ast.walk(tree):
     if not isinstance(n,ast.stmt):continue
     if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):continue
     a,b=n.lineno,n.end_lineno
     if not (inside(a,b) or (a,b) in field_spans):continue
     if dropped(a,b):cut+=1;continue
     pu+=1;nodes.append(dict(kind=type(n).__name__,start=a,end=b))
   elif f.suffix=='.java':
    tree=scope.JAVA.parse(raw);assert not tree.root_node.has_error
    for n in counter.walk(tree.root_node):
     if not ((n.type.endswith('_statement') and n.type!='empty_statement') or n.type in counter.JAVA_EXTRA):continue
     a,b=n.start_point.row+1,n.end_point.row+1
     if not inside(a,b):continue
     if dropped(a,b):cut+=1;continue
     pu+=1;nodes.append(dict(kind=n.type,start=a,end=b))
   elif f.suffix in ('.xml','.json'):
    # A selected source field is one declaration; parent model wrapper once per selected owner.
    owners={d['owner'] for d in fields};du=len(fields)+len(owners)
   else:raise ValueError(path)
   # Known residual coupling retained explicitly, not mistaken for financial algorithms.
   for m in methods:
    snippet='\n'.join(lines[m['start']-1:m['end']])
    if product=='erpnext' and m['name'] in ('update_qty','get_last_sle_values'):
     residuals.append(dict(product=product,path=path,symbol=m['name'],reason='Accès aux colonnes de solde et valeur dans le même objet ; aucune méthode de valorisation FIFO/LIFO ajoutée.'))
    if product=='axelor' and m['name']=='saveHistory':
     residuals.append(dict(product=product,path=path,symbol=m['name'],reason='Snapshot de prix natifs conservé dans la même construction de ligne historique ; pas moteur de valorisation.'))
    m['slice_sha256']=sha(snippet.encode())
    m['excluded_ranges']=[dict(start=a,end=b,reason=r) for a,b,r in removed if m['start']<=a<=b<=m['end']]
   measured.append(dict(repo=product,path=path,sha256=sha(raw),program_units=pu,declarative_units=du,excluded_program_units=cut,selected_methods=methods,declarations=fields,excluded_ranges=[dict(start=a,end=b,reason=r) for a,b,r in removed],counted_nodes=nodes))
   program+=pu;declarative+=du;excluded_program+=cut
   proofs.append(dict(repo=product,path=path,sha256=sha(raw)))
  # Previous mixed-method entries now promoted into an explicitly measured selection.
  promoted=sum((b['file'],b['start'],b['end']) in selected for b in base['boundary_methods'])
  result=dict(product=product,repository=repos[product]['repository'],commit=commit,
   status='measured_partial_core_not_complete_family',summary=dict(program_units=program,declarative_units=declarative,program_plus_declarative_at_weight_1=program+declarative,source_files=len(measured),methods=len(selected),excluded_program_units=excluded_program,mixed_methods_promoted=promoted,remaining_mixed_method_entries=len(base['boundary_methods'])-promoted),
   files=measured,excluded_from_measurement=['Tests et code généré','Runtimes et services génériques déjà financés avec Master Data','14 fichiers de présentation repérés mais pas encore sélectionnés par fragments','Algorithmes de valorisation, commandes physiques, planification et méthodes mixtes non retenues'],
   measured_size_meaning='Taille du noyau de sélection, pas taille totale du projet Stock. Les méthodes conteneurs/imports non sélectionnés ne sont pas ajoutés implicitement.',
   cocomo_jh=None,cosmic_cfp=None,stock_family_jh=None)
  (OUT/(product+'-mesures.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
  all_results[product]=result['summary']
 (OUT/'mesures.json').write_text(json.dumps(dict(summary=all_results,known_native_excess=residuals,proofs=proofs,
 counter_reference='audits/2026-10-30-master-data-natif/measure.py',counter_sha256=sha((ROOT/'audits/2026-10-30-master-data-natif/measure.py').read_bytes()),
 convention='Même convention AST/instructions/déclarations que Master Data. Python : champs déclarés comptés en instructions, pas une seconde fois en déclaratif. JSON/XML : champs sélectionnés plus un conteneur par modèle. Source originale inchangée ; coupes enregistrées pour la mesure uniquement.',
 probability=None),ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(all_results,indent=2))
if __name__=='__main__':measure()
