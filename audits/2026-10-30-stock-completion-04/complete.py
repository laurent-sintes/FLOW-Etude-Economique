"""Select presentation/permissions and classify the remaining native boundaries."""
from pathlib import Path
import json,sys,hashlib,csv,io,xml.etree.ElementTree as ET,importlib.util
import yaml
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('counter',ROOT/'audits/2026-10-30-master-data-natif/measure.py')
counter=importlib.util.module_from_spec(spec);spec.loader.exec_module(counter)
md=json.loads((ROOT/'audits/2026-10-30-master-data-comparable-reuse/measurements.json').read_text(encoding='utf-8'))
def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
js_allow={'stock_ledger_entry.js':{'refresh'},'stock_reservation_entry.js':{'warehouse','has_batch_no','has_serial_no','set_queries','toggle_read_only_fields','make_sb_entries_warehouse_read_only','sb_entries_add'},'stock_reconciliation.js':{'set_warehouse','serial_no','items_add'}}
allowed_models={'stock.quant','stock.move','stock.move.line','stock.lot','stock.inventory','stock.inventory.line','stock.location'}
results={};bounds=[]
for product in ('erpnext','odoo','tryton','axelor'):
 old=load(ROOT/f'audits/2026-10-30-stock-perimetres-02/{product}-perimetre.json')
 measured=load(ROOT/f'audits/2026-10-30-stock-mesures-03/{product}-mesures.json')
 root=ROOT/md['repos'][product]['root']
 allowed={d['name'] for d in old['declarations']}|{'number','company','date','state','lines','expected_quantity','product','stockLocation','inventorySeq','currentQty','realQty','gap','quantity','stock_uom','posting_date','posting_time'}
 pu=du=0;files=[]
 for f in old['presentation_dependencies']:
  path=root/f['path'];raw=path.read_bytes();assert sha(raw)==f['sha256'];entries=[];program=declarative=0
  if path.suffix=='.js':
   tree=counter.PARSERS['.js'].parse(raw);assert not tree.root_node.has_error
   candidates=[]
   for n in counter.walk(tree.root_node):
    name=None
    if n.type=='method_definition':
     key=n.child_by_field_name('name');name=raw[key.start_byte:key.end_byte].decode()
    elif n.type=='pair':
     value=n.child_by_field_name('value');key=n.child_by_field_name('key')
     if value and value.type in ('function_expression','arrow_function'):name=raw[key.start_byte:key.end_byte].decode().strip('"\'')
    if name in js_allow[path.name]:candidates.append((name,n))
   assert {name for name,n in candidates}==js_allow[path.name],path
   spans=[]
   for name,node in candidates:
    a,b=node.start_byte,node.end_byte;assert all(b<=c or d<=a for c,d in spans);spans.append((a,b))
    count=0
    for n in counter.walk(node):
     if n.type.endswith('_statement') and n.type not in ('empty_statement','export_statement') or n.type in counter.JS_EXTRA:count+=1
    entries.append(dict(kind='handler',name=name,start=node.start_point.row+1,end=node.end_point.row+1,program_units=count,sha256=sha(raw[a:b])))
    program+=count
  elif path.suffix=='.csv':
   for index,row in enumerate(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))),2):
    model=row.get('model_id') or row.get('model_id:id','').removeprefix('model_').replace('_','.')
    if model in allowed_models:
     entries.append(dict(kind='permission',line=index,id=row['id'],model=model,source=row));declarative+=1
  else:
   tree=ET.fromstring(raw);parents={c:p for p in tree.iter() for c in p}
   def xpath(n):
    if n not in parents:return '/'+n.tag.split('}')[-1]
    p=parents[n];same=[c for c in p if c.tag==n.tag]
    return xpath(p)+'/'+n.tag.split('}')[-1]+'['+str(same.index(n)+1)+']'
   for node in tree.iter():
    tag=node.tag.split('}')[-1];name=node.get('name')
    # Only concrete UI occurrences of already selected domain fields.
    if tag in ('field','label') and name in allowed:
     ancestors=[];a=node
     while a in parents:a=parents[a];ancestors.append(a)
     if product=='odoo':
      # Drop metadata fields outside the view architecture.
      if not any(a.tag.split('}')[-1]=='field' and a.get('name')=='arch' for a in ancestors):continue
     elif product=='tryton' and path.name=='stock.xml':
      # Registry entries select the view/model; do not count every module record as UI.
      continue
     elif product=='axelor':
      if not any(a.tag.split('}')[-1] in ('grid','form') for a in ancestors):continue
     entries.append(dict(kind=tag,name=name,xpath=xpath(node),attributes=dict(node.attrib)));declarative+=1
   # Keep source wiring as context, separately from fields counted.
  files.append(dict(path=f['path'],sha256=sha(raw),program_units=program,declarative_units=declarative,selection=entries,
    excluded='Comptabilité, valorisation, terminaux, picking, déclenchements d’affectation et conteneurs génériques non sélectionnés.',
    not_complete_executable_ui=True))
  pu+=program;du+=declarative
 selected={(m['file'],m['start'],m['end']) for f in measured['files'] for m in f['selected_methods']}
 for m in old['boundary_methods']:
  if (m['file'],m['start'],m['end']) in selected:continue
  name=m['name']
  if any(s in name.lower() for s in ('value','valuation','price','rate')):decision='hors périmètre : valorisation ou accès mêlé aux valeurs'
  elif name in ('Move.do','StockMove._action_done','StockMove._action_assign','StockMove._action_cancel','realizeGeneratedStockMoves','generateStockMove','generateStockMoveLines','generateStockMoves','validate','updateReservedQuantity','allocateAll','requestQty','StockReconciliation.on_submit'):decision='appelant natif documenté ; inclut exécution/affectation ou valorisation non intégralement mesurée'
  else:decision='adaptateur natif mêlé : branche utile non complètement extraite ; reste une limite de taille'
  bounds.append(dict(product=product,**m,decision=decision,added_to_size=False))
 base=measured['summary']
 results[product]=dict(backend_program_units=base['program_units'],backend_declarative_units=base['declarative_units'],presentation_program_units=pu,presentation_declarative_units=du,
   selected_program_units=base['program_units']+pu,selected_declarative_units=base['declarative_units']+du,selected_equivalent_units_at_weight_1=base['program_units']+base['declarative_units']+pu+du,
   presentation_files=len(files),native_full_family_cocomo_jh=None,
   size_status='sélection élargie mesurée, pas taille de famille complète')
 (OUT/(product+'-presentation.json')).write_text(json.dumps(dict(files=files,summary=results[product]),ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'tailles-completees.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'frontieres-classees.json').write_text(json.dumps(bounds,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(sizes=results,remaining_native_boundary_entries=len(bounds)),ensure_ascii=False,indent=2))
