"""Validate measured stock chain dossiers and qualify what they prove."""
from pathlib import Path
from collections import defaultdict
import ast,hashlib,importlib.util,json,sys,math
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tmp/model-deps'),str(ROOT/'tools'),str(ROOT/'tmp/master-data-native-23/parser-deps')]
import yaml
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
scope=mod('scope06verify',ROOT/'audits/2026-10-30-stock-perimetres-02/build.py')
counter=mod('counter06verify',ROOT/'audits/2026-10-30-master-data-natif/measure.py')

def main():
 provenance=load(OUT/'provenance.json')
 # README is a descriptive guide modified in parallel, not a sizing input.
 provenance['dependencies']=[d for d in provenance['dependencies'] if d['path']!='source/README.md']
 for d in provenance['dependencies']:assert sha(ROOT/d['path'])==d['sha256'],d['path']
 for p,h in provenance['protected'].items():assert sha(ROOT/p)==h,p
 chains=[load(OUT/(p+'-'+k+'.json')) for p in ['erpnext','odoo','tryton','axelor'] for k in ['correction','reservation']]
 unique_files={};nodes_by_product=defaultdict(set);methods=set();framework_by_product=defaultdict(set)
 for c in chains:
  seen=set()
  for f in c['files']:
   path=ROOT/scope.repos[f['repo']]['root']/f['path'];raw=path.read_bytes()
   assert sha(path)==f['sha256'];assert f['commit']==scope.repos[f['repo']]['commit']
   unique_files[str(path)]=sha(path)
   spans=[(m['start'],m['end']) for m in f['methods']]
   text=raw.decode('utf-8-sig');lines=text.splitlines()
   if path.suffix=='.py':
    tree=ast.parse(text)
    counted=[(type(n).__name__,n.lineno,n.end_lineno) for n in ast.walk(tree) if isinstance(n,ast.stmt)
      and not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str))
      and any(a<=n.lineno<=n.end_lineno<=b for a,b in spans)]
   else:
    tree=scope.JAVA.parse(raw);assert not tree.root_node.has_error
    counted=[(n.type,n.start_point.row+1,n.end_point.row+1) for n in counter.walk(tree.root_node)
      if ((n.type.endswith('_statement') and n.type!='empty_statement') or n.type in counter.JAVA_EXTRA)
      and any(a<=n.start_point.row+1<=n.end_point.row+1<=b for a,b in spans)]
   assert len(counted)==f['program_units']
   assert set(counted)=={(n['kind'],n['start'],n['end']) for n in f['counted_nodes']}
   for m in f['methods']:
    assert '\n'.join(lines[m['start']-1:m['end']])==m['source_fragment']
    methods.add((f['repo'],f['path'],m['start'],m['end']))
   for n in f['counted_nodes']:
    key=(f['repo'],f['path'],n['start'],n['end'],n['kind']);assert key not in seen;seen.add(key)
    target=framework_by_product if f['role']=='framework_reused' else nodes_by_product
    target[c['product']].add(key)
   if f['role']=='framework_reused':assert f['stock_additional_generic_framework_units']==0
  assert c['runtime_executed'] is False
  assert c['effort']['receivable_jh'] is None and c['effort']['COCOMO_executed'] is False
 unions=load(OUT/'mesures-union.json')
 for p in unions:
  assert unions[p]['native_domain_program_units']==len(nodes_by_product[p])
  assert unions[p]['framework_program_units_observed_not_recharged']==len(framework_by_product[p])
  assert unions[p]['domain_overlap_between_chains']>=0
 # Bind each path edge to exact measured source methods; distinguish an actual call from hooks and queries.
 graph=[]
 def node(chain,file_end,symbol):
  found=[dict(repo=f['repo'],path=f['path'],symbol=m['name'],start=m['start'],end=m['end'],source_url=f['source_url'])
   for c in chains if c['id']==chain for f in c['files'] if f['path'].endswith(file_end)
   for m in f['methods'] if scope.matches(m,symbol)]
  assert len(found)==1,(chain,file_end,symbol,len(found))
  return found[0]
 def edge(chain,source,target,kind='appel',note=None):
  graph.append(dict(chain=chain,source=node(chain,*source),target=node(chain,*target),kind=kind,note=note))
 c='erpnext-correction'
 edge(c,('stock_ledger.py','make_sl_entries'),('stock_ledger.py','make_entry'))
 edge(c,('stock_ledger.py','make_entry'),('document.py','Document.submit'))
 edge(c,('document.py','Document.submit'),('document.py','Document._submit'))
 edge(c,('document.py','Document._submit'),('document.py','Document.save'))
 edge(c,('document.py','Document.run_before_save_methods'),('stock_ledger_entry.py','StockLedgerEntry.validate'),'hook natif')
 edge(c,('stock_ledger.py','make_sl_entries'),('stock_ledger.py','repost_current_voucher'))
 edge(c,('stock_ledger.py','repost_current_voucher'),('stock_ledger.py','update_entries_after.__init__'),'construction de composant')
 edge(c,('stock_ledger.py','repost_current_voucher'),('stock_ledger.py','update_qty_in_future_sle'))
 edge(c,('stock_ledger.py','update_qty_in_future_sle'),('stock_ledger.py','get_next_stock_reco'))
 edge(c,('stock_ledger.py','update_qty_in_future_sle'),('stock_ledger.py','validate_negative_qty_in_future_sle'))
 edge(c,('app.py','application'),('app.py','sync_database'),'frontière transactionnelle','Après succès du handler ; rollback en erreur dans application.')
 c='erpnext-reservation'
 edge(c,('document.py','Document.run_before_save_methods'),('stock_reservation_entry.py','StockReservationEntry.before_submit'),'hook natif')
 edge(c,('stock_reservation_entry.py','StockReservationEntry.before_submit'),('stock_reservation_entry.py','StockReservationEntry.validate_reservation_based_on_qty'))
 edge(c,('stock_reservation_entry.py','StockReservationEntry.validate_reservation_based_on_qty'),('stock_reservation_entry.py','StockReservationEntry.validate_with_allowed_qty'))
 edge(c,('stock_reservation_entry.py','StockReservationEntry.validate_with_allowed_qty'),('stock_reservation_entry.py','get_available_qty_to_reserve'))
 edge(c,('stock_reservation_entry.py','get_available_qty_to_reserve'),('utils.py','_get_stock_balance'))
 edge(c,('stock_reservation_entry.py','StockReservationEntry.on_submit'),('stock_reservation_entry.py','StockReservationEntry.update_reserved_stock_in_bin'))
 edge(c,('stock_reservation_entry.py','StockReservationEntry.update_reserved_stock_in_bin'),('bin.py','Bin.update_reserved_stock'))
 edge(c,('document.py','Document.run_post_save_methods'),('stock_reservation_entry.py','StockReservationEntry.on_submit'),'hook natif')
 edge(c,('app.py','application'),('app.py','sync_database'),'frontière transactionnelle')
 c='odoo-correction'
 edge(c,('stock_quant.py','StockQuant.action_apply_inventory'),('stock_quant.py','StockQuant._apply_inventory'))
 edge(c,('stock_quant.py','StockQuant._apply_inventory'),('stock_move.py','StockMove._action_done'))
 edge(c,('stock_move.py','StockMove._action_done'),('stock_move_line.py','StockMoveLine._action_done'))
 edge(c,('stock_move_line.py','StockMoveLine._action_done'),('stock_move_line.py','StockMoveLine._synchronize_quant'))
 edge(c,('stock_move_line.py','StockMoveLine._synchronize_quant'),('stock_quant.py','StockQuant._update_available_quantity'))
 edge(c,('stock_quant.py','StockQuant._update_available_quantity'),('models.py','BaseModel.try_lock_for_update'),'appel ORM')
 edge(c,('stock_quant.py','StockQuant._update_available_quantity'),('product.py','ProductProduct._compute_quantities_dict'),'lecture ultérieure','La consultation passée exploite les quants et lignes datées ; ce n’est pas un appel direct dans la commande.')
 edge(c,('retrying.py','retrying'),('models.py','BaseModel._flush'),'frontière transactionnelle','env.cr.flush déclenche le flush ORM ; boucle de reprise avant commit.')
 c='odoo-reservation'
 edge(c,('stock_move.py','StockMove._update_reserved_quantity'),('stock_move.py','StockMove._update_reserved_quantity_vals'))
 edge(c,('stock_move.py','StockMove._update_reserved_quantity_vals'),('stock_quant.py','StockQuant._get_reserve_quantity'))
 edge(c,('stock_move.py','StockMove._update_reserved_quantity'),('stock_move_line.py','StockMoveLine.create'),'hook ORM')
 edge(c,('stock_move_line.py','StockMoveLine.create'),('stock_quant.py','StockQuant._update_reserved_quantity'))
 edge(c,('stock_quant.py','StockQuant._update_reserved_quantity'),('stock_quant.py','StockQuant._update_available_quantity'))
 edge(c,('stock_quant.py','StockQuant._update_available_quantity'),('models.py','BaseModel.try_lock_for_update'),'appel ORM')
 edge(c,('retrying.py','retrying'),('models.py','BaseModel._flush'),'frontière transactionnelle')
 c='tryton-correction'
 edge(c,('inventory.py','Inventory.confirm'),('inventory.py','InventoryLine.get_move'))
 edge(c,('inventory.py','Inventory.confirm'),('move.py','Move.do'))
 edge(c,('move.py','Move.do'),('move.py','Move.set_effective_date'))
 edge(c,('workflow.py','Workflow.transition'),('modelsql.py','ModelSQL.write'),'décorateur de transition','Écrit l’état via cls.write après la méthode.')
 edge(c,('product.py','Product.products_by_location'),('move.py','Move.compute_quantities_query'),'lecture de quantité')
 edge(c,('dispatcher.py','_dispatch'),('inventory.py','Inventory.confirm'),'frontière transactionnelle','Appel RPC dynamique puis commit, rollback/retry conditionnel.')
 c='tryton-reservation'
 edge(c,('move.py','Move.assign_try'),('move.py','Move._assign_try_lock'))
 edge(c,('move.py','Move.assign_try'),('product.py','Product.products_by_location'))
 edge(c,('move.py','Move.assign_try'),('move.py','Move.assign'))
 edge(c,('move.py','Move._assign_try_lock'),('modelsql.py','ModelSQL.lock'),'repli conditionnel selon backend')
 edge(c,('workflow.py','Workflow.transition'),('modelsql.py','ModelSQL.write'),'décorateur de transition')
 edge(c,('dispatcher.py','_dispatch'),('move.py','Move.assign_try'),'frontière transactionnelle','Appel RPC dynamique ; erreur opérationnelle → rollback/retry configuré.')
 c='axelor-correction'
 edge(c,('InventoryValidateServiceImpl.java','validate'),('InventoryValidateServiceImpl.java','generateStockMoves'))
 edge(c,('InventoryValidateServiceImpl.java','stockMoveRealize'),('StockMoveServiceImpl.java','realize@531'))
 edge(c,('StockMoveServiceImpl.java','realize@531'),('StockMoveServiceImpl.java','realizeStockMove'))
 edge(c,('StockMoveLineServiceImpl.java','updateLocationForStockMoveLine'),('StockLocationLineServiceImpl.java','updateLocation@137'),'mutation via surcharges updateLocations')
 edge(c,('StockLocationLineServiceImpl.java','updateHistory'),('StockLocationLineHistoryServiceImpl.java','saveHistory'))
 edge(c,('BatchRecomputeStockLocationLines.java','process'),('BatchRecomputeStockLocationLines.java','resetStockLocations'))
 edge(c,('BatchRecomputeStockLocationLines.java','process'),('BatchRecomputeStockLocationLines.java','recomputeStockMoves'),'itération sur groupes réalisés')
 edge(c,('BatchRecomputeStockLocationLines.java','recomputeStockMoves'),('StockMoveLineServiceImpl.java','updateLocations@692'))
 edge(c,('BatchRecomputeStockLocationLines.java','resetStockLocations'),('JPA.java','runInTransaction'),'transaction de remise à zéro')
 c='axelor-reservation'
 edge(c,('ReservedQtyServiceImpl.java','updateReservedQty@767'),('StockLocationLineServiceImpl.java','getOrCreateStockLocationLine'))
 edge(c,('ReservedQtyServiceImpl.java','updateReservedQty@767'),('ReservedQtyServiceImpl.java','updateReservedQty@777'))
 edge(c,('ReservedQtyServiceImpl.java','updateReservedQty@777'),('ReservedQtyServiceImpl.java','checkBeforeUpdatingQties'))
 edge(c,('ReservedQtyServiceImpl.java','updateReservedQty@777'),('ReservedQtyServiceImpl.java','updateReservedQty@995'),'branche sans SaleOrderLine')
 edge(c,('ReservedQtyServiceImpl.java','updateReservedQty@995'),('JPA.java','flush'),'frontière de flush','Setter d’une entité gérée : contrôle de version au flush Hibernate. Pas un appel explicite à JPA.flush dans cette méthode ; pas de garantie runtime attribuée.')
 write('graphe-chemins.json',dict(edges=graph,
  boundary='Chemins critiques de quantité, hooks et frontières de transaction. Les autres appels restent visibles dans chaque méthode ; ce graphe ne prétend pas fermer toutes les extensions installables.',
  runtime_tested=False))
 # Observable criteria, no numeric score or confidence class.
 matrix=[]
 statuses={
 'effect_date':['observé','observé, date de ligne liée au mouvement','observé par effective_date et filtre de requête','correction courante et reconstruction observées ; équivalent rétroactif en ligne non établi'],
 'current_position':['observé']*4,
 'knowledge_date_revision':['non établi dans cette chaîne']*4,
 'concurrency_primitive':['FOR UPDATE sur agrégat ; contexte moteur/première réservation non qualifié','verrou quants + transaction REPEATABLE READ + retry identifiés','verrou des mouvements avant lecture + retry RPC identifiés','@Version hérité identifié ; protection conditionnelle de la même ligne gérée'],
 'new_command_replay':['non établi par la reprise transactionnelle']*4,
 'automatic_transaction_retry':['non attribué au handler inspecté','cinq tentatives au maximum','nombre configuré pour erreurs opérationnelles','non attribué au service inspecté']}
 labels={'effect_date':'Correction/restitution selon date d’effet','current_position':'Actualisation de la quantité courante','knowledge_date_revision':'Historique selon date de connaissance et révisions','concurrency_primitive':'Protection de concurrence native','new_command_replay':'Rejeu d’une nouvelle commande sans second effet','automatic_transaction_retry':'Reprise automatique de transaction avortée'}
 for i,p in enumerate(['erpnext','odoo','tryton','axelor']):
  for k,values in statuses.items():
   matrix.append(dict(product=p,criterion=k,label=labels[k],status=values[i],
    evidence=[p+'-correction.json',p+'-reservation.json','preuves-complementaires.json'],
    means_complete_Flow_guarantee=False))
 write('comparaison-garanties.json',dict(criteria=matrix,
   interpretation='Présence d’un mécanisme observé ou limite explicitement établie. Ne pas convertir ces statuts en pourcentage de confiance ou de couverture fonctionnelle.'))
 report=yaml.safe_load((OUT/'bilan.yaml').read_text(encoding='utf-8'))
 report['measurements_summary']=dict(unique_source_files=len(unique_files),unique_source_methods=len(methods),
  unique_native_domain_instructions_declarations=sum(len(v) for v in nodes_by_product.values()),
  newly_measured_native_domain_instructions_declarations=sum(v['additional_domain_nodes_measured'] for v in unions.values()),
  critical_path_edges=len(graph),comparison_criteria=len(statuses),product_criterion_observations=len(matrix),
  sizes_are_not_a_product_complexity_ranking=True)
 report['evidence']=list(dict.fromkeys(report['evidence']+['graphe-chemins.json','comparaison-garanties.json','verification.json']))
 (OUT/'bilan.yaml').write_text(yaml.safe_dump(report,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
 # Update hashes of generated artifacts and add verifier and the new graph/matrix.
 depmap={d['path']:d['sha256'] for d in provenance['dependencies']}
 for p in [OUT/'bilan.yaml',OUT/'graphe-chemins.json',OUT/'comparaison-garanties.json',Path(__file__).resolve()]:
  depmap[str(p.relative_to(ROOT)).replace('\\','/')]=sha(p)
 provenance['dependencies']=[dict(path=p,sha256=h) for p,h in sorted(depmap.items())]
 write('provenance.json',provenance)
 retained=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))
 md=next(u for u in retained['units'] if u['id']=='master-data-java-spring')
 assert md['total_jh']==1500 and md['months']==17 and sum(r['jh'] for r in md['roles'])==1500
 assert not any('stock' in u['id'] for u in retained['units'])
 verification=dict(consistent=True,source_files_recounted=len(unique_files),unique_methods=len(methods),chains=8,
  critical_path_edges_validated=len(graph),dependency_hashes=len(provenance['dependencies']),retained_jh=1500,retained_months_master_data=17,
  stock_jh_receivable=False,OSS_tests_executed=False,application_modified=False,
  result='Mesures et liens vérifiés ; les limites de comparabilité empêchent de produire des JH Flow défendables.')
 write('verification.json',verification)
 print(json.dumps(verification,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
