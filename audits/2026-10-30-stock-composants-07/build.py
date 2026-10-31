"""Four component-level Stock perimeters and bounded Flow complements.
The broad native footprint is evidence, never silently a Flow cost base.
"""
from pathlib import Path
from collections import defaultdict
import ast,hashlib,importlib.util,json,sys,subprocess,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tmp/model-deps'),str(ROOT/'tmp/master-data-native-23/parser-deps'),str(ROOT/'tools')]
import yaml
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def module(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
counter=module('counter07','audits/2026-10-30-master-data-natif/measure.py')
md=load('audits/2026-10-30-master-data-comparable-reuse/measurements.json');repos=md['repos']
products=['erpnext','odoo','tryton','axelor']
components=[
 dict(id='K1',label='Registre et effets des mouvements',capabilities=['BC-009','BC-010'],common_outcome='Enregistrer un mouvement ou delta reconnu, son origine et sa date d’effet, et produire la quantité courante corrigée.',
  common_boundary='Identités produit/lieu/unité déjà disponibles ; faits connus, pas de mouvements inventés. Le protocole d’admission externe, la double date et les corrections liées Flow restent des compléments.',
  processes=['S01','S02','S03','S04'],dependencies=['master-data-common-domain','java-spring-framework-services']),
 dict(id='K2',label='Positions et apports attendus connus',capabilities=['BC-011'],common_outcome='Calculer une quantité courante ou à date et une position issue des mouvements planifiés déjà connus.',
  common_boundary='Une projection de quantité ne vaut ni promesse ni décision d’allocation. Les sources restent maîtres des commandes/plans ; leur création n’est pas reconstruite.',
  processes=['S05','S06','S07'],dependencies=['K1','K4','master-data-common-domain']),
 dict(id='K3',label='Comptages et ajustements',capabilities=['BC-013'],common_outcome='Comparer quantité attendue et comptage, puis générer un ajustement autorisé.',
  common_boundary='Pas de WMS mobile, orchestration de tournée ou moteur de valorisation. Les protocoles et rapprochements temporels Flow restent explicites.',
  processes=['S08','S09','S10','S11','S12'],dependencies=['K1','K2','master-data-protection']),
 dict(id='K4',label='Engagements de quantité',capabilities=['BC-018'],common_outcome='Contrôler le disponible, modifier une quantité réservée et protéger les écritures concurrentes dans une transaction.',
  common_boundary='Pas de choix optimal de ressource, routage ou allocation commerciale. Quantité/portion demandées fournies ; expiration et rejeu métier Flow à adapter.',
  processes=['S13','S14','S15','S16'],dependencies=['K1','K2','java-spring-framework-services']),
 dict(id='K5',label='Contrats de fourniture aux autres fonctions',capabilities=['BC-012','BC-016','BC-017'],common_outcome=None,
  common_boundary='Contrats Flow de planification, Finance et constats produit. Pas quatre implémentations natives équivalentes revendiquées ; aucune comptabilité générale, aucun PLM.',
  processes=['S17','S18','S19','S20','S21'],dependencies=['K1','K2','master-data-admission','master-data-versions'])]
files=defaultdict(dict)
def add(product,component,paths,note):
 for path in paths:
  row=files[product].setdefault(path,dict(product=product,repo=product,path=path,components=[],scope_notes=[]))
  if component not in row['components']:row['components'].append(component)
  if note not in row['scope_notes']:row['scope_notes'].append(note)
E='erpnext/stock/'
add('erpnext','K1',[E+'stock_ledger.py',E+'doctype/stock_ledger_entry/stock_ledger_entry.py',E+'doctype/stock_ledger_entry/stock_ledger_entry.json',E+'doctype/stock_ledger_entry/stock_ledger_entry.js'],
 'Composants entiers du registre ; quantités, prix et serial/batch sont mêlés dans le code natif.')
add('erpnext','K2',[E+'doctype/bin/bin.py',E+'doctype/bin/bin.json',E+'report/stock_balance/stock_balance.py',E+'report/stock_balance/stock_balance.js'],
 'Positions et états natifs complets ; colonnes de valeur et dépendances aux commandes restent visibles.')
add('erpnext','K3',[E+'doctype/stock_reconciliation/stock_reconciliation.py',E+'doctype/stock_reconciliation/stock_reconciliation.json',E+'doctype/stock_reconciliation/stock_reconciliation.js',E+'doctype/stock_reconciliation_item/stock_reconciliation_item.json'],
 'Comptage et ajustements natifs, avec prix et logique serial/batch ; pas supposés équivalents gratuitement au protocole Flow.')
add('erpnext','K4',[E+'doctype/stock_reservation_entry/stock_reservation_entry.py',E+'doctype/stock_reservation_entry/stock_reservation_entry.json',E+'doctype/stock_reservation_entry/stock_reservation_entry.js',E+'doctype/bin/bin.py'],
 'Réservations et maintien du Bin ; liens Sales Order, Pick List, fabrication et transfert natifs excédentaires.')
O='addons/stock/'
add('odoo','K1',[O+'models/stock_move.py',O+'models/stock_move_line.py',O+'views/stock_move_views.xml'],
 'Modèles de mouvement et hooks entiers ; incluent opérations, colis, backorders et réaffectation.')
add('odoo','K2',[O+'models/stock_quant.py',O+'models/product.py',O+'models/stock_lot.py',O+'models/stock_location.py',O+'views/stock_quant_views.xml',O+'views/stock_location_views.xml'],
 'Quants, requêtes à date et dimensions ; le patrimoine de lieux Master Data est déduit exactement, sans financer deux fois les mêmes déclarations.')
add('odoo','K3',[O+'models/stock_quant.py',O+'views/stock_quant_views.xml',O+'wizard/stock_inventory_conflict.py',O+'wizard/stock_inventory_warning.py',O+'wizard/stock_inventory_adjustment_name.py'],
 'Même modèle quant que K2, avec assistants de contrôle ; une seule occurrence dans le périmètre total.')
add('odoo','K4',[O+'models/stock_move.py',O+'models/stock_move_line.py',O+'models/stock_quant.py'],
 'Partage les modèles K1/K2 ; sélection de quants et prélèvement natifs à distinguer de la protection d’une portion fournie.')
T='modules/stock/'
add('tryton','K1',[T+'move.py',T+'view/move_form.xml',T+'view/move_tree.xml'],
 'Mouvement complet, état, dates et requêtes ; coûts et exécution restent mêlés à plusieurs méthodes.')
add('tryton','K2',[T+'product.py',T+'location.py',T+'view/product_quantities_warehouse_list.xml',T+'view/location_quantity_form.xml',T+'view/location_quantity_tree.xml'],
 'Quantités et vues de lieux ; déduction des blocs/vues déjà comptés dans Master Data.')
add('tryton','K3',[T+'inventory.py',T+'view/inventory_form.xml',T+'view/inventory_line_form.xml',T+'view/inventory_tree.xml',T+'view/inventory_line_list.xml',T+'move.py'],
 'Inventaire et mouvement correctif partagent Move ; la tolérance de valeur et les coûts ne sont pas retirés par un ratio.')
add('tryton','K4',[T+'move.py',T+'product.py'],
 'Réservation/assignation, verrou et calcul partagé ; le choix/split des mouvements est un excédent natif à isoler.')
A='axelor-stock/src/main/'
J=A+'java/com/axelor/apps/stock/service/'
D=A+'resources/domains/'
V=A+'resources/views/'
add('axelor','K1',[J+'StockMoveServiceImpl.java',J+'StockMoveLineServiceImpl.java',J+'StockLocationLineServiceImpl.java',J+'StockLocationLineHistoryServiceImpl.java',J+'batch/BatchRecomputeStockLocationLines.java',D+'StockMove.xml',D+'StockMoveLine.xml',D+'StockLocationLine.xml',D+'StockLocationLineHistory.xml',V+'StockMove.xml'],
 'Mouvements, lignes de stock et reconstruction entiers ; prix moyen, valeurs, réapprovisionnement et exécution sont des couplages natifs documentés.')
add('axelor','K2',[J+'StockLocationLineFetchServiceImpl.java',J+'StockLocationLineServiceImpl.java',D+'StockLocationLine.xml',V+'StockLocationLine.xml'],
 'Lectures et lignes partagées avec K1 ; aucun nouveau composant indépendant inventé.')
add('axelor','K3',[J+'inventory/InventoryLineServiceImpl.java',J+'inventory/InventoryValidateServiceImpl.java',J+'inventory/InventoryStockLocationUpdateServiceImpl.java',J+'inventory/InventoryService.java',D+'Inventory.xml',D+'InventoryLine.xml',V+'Inventory.xml',J+'StockMoveServiceImpl.java',J+'StockMoveLineServiceImpl.java'],
 'Composant d’inventaire avec appels aux mouvements K1 ; le recalcul physique et les prix restent des excédents identifiés.')
S='axelor-supplychain/src/main/'
add('axelor','K4',[S+'java/com/axelor/apps/supplychain/service/ReservedQtyServiceImpl.java',S+'resources/domains/StockLocationLine.xml',S+'resources/domains/StockMoveLine.xml',J+'StockLocationLineServiceImpl.java',J+'StockLocationLineFetchServiceImpl.java',D+'StockLocationLine.xml'],
 'Quantités réservées et extensions de modèle ; allocations aux ventes et mouvements natifs excédentaires.')

# Exact funding overlap, reconstructing the prior named exclusions without importing
# its top-level executable measurement script or rewriting its immutable outputs.
def py_nodes(path,exclusions=()):
 lines=path.read_text(encoding='utf-8-sig').splitlines();inside=False
 for i,line in enumerate(lines):
  if '# begin: auto-generated types' in line:inside=True
  if inside:lines[i]=''
  if '# end: auto-generated types' in line:inside=False
 tree=ast.parse('\n'.join(lines));out=set()
 excluded={(e['kind'],e['name'],e['line']) for e in exclusions if e.get('line') is not None}
 def visit(n):
  if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and ('method',n.name,n.lineno) in excluded:return
  if isinstance(n,ast.ClassDef) and ('class',n.name,n.lineno) in excluded:return
  if isinstance(n,(ast.Assign,ast.AnnAssign)):
   targets=n.targets if isinstance(n,ast.Assign) else [n.target]
   name=','.join(t.id for t in targets if isinstance(t,ast.Name))
   if ('field',name,n.lineno) in excluded:return
  if isinstance(n,ast.stmt) and not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str)):
   out.add((type(n).__name__,n.lineno,n.end_lineno))
  for c in ast.iter_child_nodes(n):visit(c)
 visit(tree);return out
def funding_overlap(row,path,units):
 hits=[f for f in md['files'] if f['repo']==row['repo'] and f['path']==row['path']]
 if not hits:return dict(program_units=0,declarative_units=0,rule='pas de même fichier dans la mesure Master Data',owner=None)
 assert len(hits)==1;prior=hits[0];assert prior['sha256']==sha(path)
 if path.suffix=='.py':
  full=py_nodes(path);already=py_nodes(path,prior['excluded_blocks'])
  assert len(full)==units['program_units'] and len(already)==prior['program_units']
  assert already<=full
  return dict(program_units=len(already),declarative_units=0,rule='Intersection exacte des instructions après les exclusions nommées Master Data ; pas de pourcentage.',owner='master-data-java-spring',
   prior_ref='audits/2026-10-30-master-data-comparable-reuse/measurements.json',excluded_from_MD=prior['excluded_blocks'])
 if path.suffix=='.xml':
  assert prior['program_units']==0
  # The shared XML files have explicit named exclusions; reconstruct the same traversal.
  exclusions={e['name'] for e in prior['excluded_blocks'] if e['kind']=='field_or_widget'}
  count=0
  def visit(n):
   nonlocal count
   tag=n.tag.split('}')[-1];model=n.get('model','')
   if tag=='record' and model and (not model.startswith(('ir.','res.groups','res.group')) or model=='ir.message'):return
   if n.get('name','') in exclusions:return
   if tag not in counter.XML_WRAPPERS:count+=1
   for c in n:visit(c)
  visit(ET.fromstring(path.read_text(encoding='utf-8-sig')))
  assert count==prior['declarative_units'],(row['path'],count,prior['declarative_units'])
  assert count<=units['declarative_units']
  return dict(program_units=0,declarative_units=count,rule='Déclarations déjà comptées dans Master Data, après ses exclusions nommées.',owner='master-data-java-spring',
   prior_ref='audits/2026-10-30-master-data-comparable-reuse/measurements.json')
 raise AssertionError(('unhandled overlap',row['path']))

# Explicit scope bounds. Quantities describe a proposed architecture, not a guaranteed
# upper effort bound and not an accepted specification.
BOUNDS={
 'STOCK-F01':dict(included=['Une identité sémantique stable par fait et un résultat d’application Stock.','Deux dates conservées : fait et connaissance ; corrections reliées à leur origine.','Un solde externe autoritatif par portion et intervalle déclaré, sans inventer de mouvements.','Filiations et contenus reçus, quantités et limites explicitement fournis.'],
   excluded=['Moteur de résolution automatique de sources contradictoires.','Généalogie déduite de faits absents ou décision de rappel/usage.','Règles et correspondances propres à Beaumanoir.'],
   reuse=['master-data-common-domain','master-data-admission','master-data-versions'],components=['K1','K2']),
 'STOCK-F02':dict(included=['Positions avec provenance, fraîcheur et limites connues.','Apports fournis par leurs producteurs ; leur réalisation cesse de compter comme attente pour la même quantité.','Une coupe versionnée fournie à la planification par le mécanisme commun.'],
   excluded=['Construction du plan ou des commandes sources.','Promesse ATP/CTP/PTP ou optimisation d’allocation.'],
   reuse=['master-data-common-domain','master-data-protection','master-data-versions'],components=['K2','K5']),
 'STOCK-F03':dict(included=['Protocole et tolérance déclarés, comptage daté et preuve.','Rapprochement avec les mouvements concomitants et décision autorisée liée au correctif.'],
   excluded=['Moteur générique de règles métier spécifique au Groupe.','Pilotage des opérateurs et terminaux d’entrepôt.','Calcul de valorisation financière.'],
   reuse=['java-spring-framework-services','master-data-protection'],components=['K3','K1']),
 'STOCK-F04':dict(included=['Engagement d’une quantité sur une portion fournie, avec identité et version attendue.','Contrôle et mutation atomiques sur une seule base transactionnelle.','Consommation/libération/expiration explicites, conflit retourné et rejeu par clé.'],
   excluded=['Sélection optimale des ressources, allocation commerciale ou solveur.','Réservation distribuée entre bases autonomes.','Garantie de succès sans attente sous contention.'],
   reuse=['java-spring-framework-services','master-data-admission'],components=['K4']),
 'STOCK-F05':dict(included=['Un contrat canonique Finance de faits, corrections liées et versions.','Retours acceptation/rejet/référence de prise en compte.','Publication et journal communs réutilisés.'],
   excluded=['Écritures de comptabilité générale, valorisation, fiscalité.','Connecteurs et mapping de chaque application Beaumanoir.'],
   reuse=['master-data-admission','master-data-versions'],components=['K5']),
 'STOCK-F06':dict(included=['Un contrat canonique de constat produit : fait, produit, contexte, preuve, destinataire et correction.','Fourniture via les services communs.'],
   excluded=['PLM, workflow de résolution qualité et diagnostic causal.','Connecteurs des applications du Groupe.'],
   reuse=['master-data-common-domain','master-data-admission'],components=['K5']),
 'STOCK-F07':dict(included=['Coordinateur de reprise et chaîne de livraison Master Data réutilisés.','Rapprochement Stock spécifique : faits, quantités, engagements et sorties déclarées avant réouverture.','Objectifs de service conservés comme paramètres à définir ; aucune durée de reprise inventée.'],
   excluded=['Reconstruction du moteur de backup, de CI/CD ou des transactions du framework.','Haute disponibilité multi-région et consensus distribué présumés gratuits.'],
   reuse=['master-data-reprise','master-data-service'],components=['K1','K2','K3','K4','K5'])}

def main():
 OUT.mkdir(exist_ok=True)
 protected_paths=['source/referentiel-capacites.yaml','sources/cartographie-scm-2026-10-24.yaml','source/fondamentaux.yaml','source/estimations-core-retenues.yaml','source/calculs-estimation-core.yaml']
 protected={p:sha(ROOT/p) for p in protected_paths}
 # Source witnesses for the unresolved difference between a coherent native
 # component and an economically comparable Flow component. These are observations,
 # not proportions used to remove effort.
 witness_specs={
  'erpnext':('erpnext/stock/stock_ledger.py','update_entries_after.process_sle',
    ['qty_after_transaction','get_moving_average_values'],
    'Le même moteur met à jour les quantités et exécute des calculs de valeur.'),
  'odoo':('addons/stock/models/stock_move.py','StockMove._action_done',
    ['cancel_backorder','move_line_ids'],
    'La réalisation du mouvement intègre l’exécution et le traitement des reliquats, au-delà de la tenue de faits reconnus.'),
  'tryton':('modules/stock/move.py','Move.do',
    ["move.state = 'done'",'cost_values'],
    'La transition du mouvement est mêlée au calcul et à la sauvegarde des coûts.'),
  'axelor':('axelor-stock/src/main/java/com/axelor/apps/stock/service/StockMoveLineServiceImpl.java','updateAveragePriceAndLocationLineHistory',
    ['computeNewAveragePriceLocationLine','updateHistory'],
    'Le même chemin met à jour le prix moyen et l’historique de stock.')
 }
 scope=module('scope07','audits/2026-10-30-stock-perimetres-02/build.py')
 witnesses=[]
 for product,(path,symbol,needles,meaning) in witness_specs.items():
  f=ROOT/repos[product]['root']/path
  raw,methods,_=scope.parse(f)
  found=[m for m in methods if m['name']==symbol];assert len(found)==1,(product,symbol)
  m=found[0];fragment='\n'.join(raw.decode('utf-8-sig').splitlines()[m['start']-1:m['end']])
  assert all(n in fragment for n in needles),(product,needles)
  witnesses.append(dict(product=product,path=path,symbol=symbol,start=m['start'],end=m['end'],
    sha256=sha(f),commit=repos[product]['commit'],source_fragment=fragment,observed_markers=needles,
    scope_difference=meaning,unresolved_for_economic_size=True,
    not_a_proof_of_impossibility=True))
 write('ecarts-natifs-non-normalises.json',dict(witnesses=witnesses,
  interpretation='Couplages positivement observés dans les composants entiers. Leur présence ne prouve pas une impossibilité théorique ; leur normalisation en taille comparable reste non établie dans cet essai.'))
 summaries={};all_records=[];overlaps=[]
 for product in products:
  root=ROOT/repos[product]['root']
  actual=subprocess.check_output(['C:/Program Files/Git/cmd/git.exe','-C',str(root),'rev-parse','HEAD'],text=True).strip()
  assert actual==repos[product]['commit']
  measured=[]
  for path,row in sorted(files[product].items()):
   f=root/path;assert f.is_file(),f
   raw=f.read_bytes()
   obj=subprocess.check_output(['C:/Program Files/Git/cmd/git.exe','-C',str(root),'show',actual+':'+path])
   assert obj.replace(b'\r\n',b'\n')==raw.replace(b'\r\n',b'\n')
   units=counter.measure(f);overlap=funding_overlap(row,f,units)
   record=dict(**row,commit=actual,sha256=sha(f),git_object_sha256=hashlib.sha256(obj).hexdigest(),
     source_url='https://github.com/'+repos[product]['repository']+'/blob/'+actual+'/'+path,
     **units,already_funded_MD=overlap,
     native_program_after_MD=units['program_units']-overlap['program_units'],
     native_declarative_after_MD=units['declarative_units']-overlap['declarative_units'],
     measure_meaning='Empreinte du composant natif entier. Contient des fonctions hors Flow ; pas taille économique Flow validée.',
     economic_eligibility=not any(w['unresolved_for_economic_size'] for w in witnesses if w['product']==product))
   assert record['native_program_after_MD']>=0 and record['native_declarative_after_MD']>=0
   if overlap['program_units']+overlap['declarative_units']:overlaps.append(dict(product=product,path=path,**overlap))
   measured.append(record);all_records.append(record)
  component_rows=[]
  for component in components:
   rows=[r for r in measured if component['id'] in r['components']]
   component_rows.append(dict(component=component['id'],files=[r['path'] for r in rows],
    native_program_units=sum(r['program_units'] for r in rows),native_declarative_units=sum(r['declarative_units'] for r in rows),
    status='composants natifs rapprochés du même résultat fonctionnel, avec excédents explicites' if component['id']!='K5' else 'compléments Flow ; pas quatre équivalents natifs établis',
    economic_jh=None,independent_effort_sum_allowed=False))
  total_program=sum(r['program_units'] for r in measured);total_decl=sum(r['declarative_units'] for r in measured)
  naive=sum(r['native_program_units']+r['native_declarative_units'] for r in component_rows)
  summary=dict(files=len(measured),program_units=total_program,declarative_units=total_decl,
    native_unique_units=total_program+total_decl,
    naive_component_units=naive,duplicate_units_avoided=naive-total_program-total_decl,
    MD_program_units_not_recharged=sum(r['already_funded_MD']['program_units'] for r in measured),
    MD_declarative_units_not_recharged=sum(r['already_funded_MD']['declarative_units'] for r in measured),
    code_units_after_MD=sum(r['native_program_after_MD']+r['native_declarative_after_MD'] for r in measured),
    eligible_Flow_equivalent_size=None,COCOMO_jh=None)
  summaries[product]=summary
  write(product+'-perimetre.json',dict(product=product,technology=product,source_revision=actual,
    functional_contract='components.json#K1..K4 et complementaires.json ; les huit capacités Flow restent dans le périmètre cible.',
    components=component_rows,files=measured,summary=summary,
    code_boundary='Code et modèles/vues des composants métier entiers ; ports d’ORM/framework et référentiels Master Data déjà financés séparés.',
    open_native_dependencies=['Hooks/ports listés dans les dossiers de chaînes 06.','Les composants complets contiennent des fonctions natives excédentaires qui empêchent une taille Flow homogène.'],
    supports_calculation=not any(w['unresolved_for_economic_size'] for w in witnesses if w['product']==product),observed_project_jh=None))
 cosmic=load('audits/2026-10-30-stock-completion-04/cosmic.json')
 by_process={p['id']:p for p in cosmic['processes']}
 for c in components:
  c['contract_CFP']=sum(by_process[p]['count']['CFP'] for p in c['processes'])
  c['CFP_meaning']='Répartition du contrat proposé Flow, pas preuve que ces CFP sont fournis par chaque OSS.'
 assert sum(c['contract_CFP'] for c in components)==cosmic['result']['CFP']==169
 assert len({p for c in components for p in c['processes']})==21
 write('components.json',dict(components=components,unit='Business Area Inventory State Management',
  economic_unit_policy='Les composants partagent état et services. Union des tailles avant toute application de COCOMO ; pas somme de quatre chiffrages autonomes.',
  framework_policy='Mécanismes Master Data à propriétaire unique ; appels et adaptations Stock spécifiques à conserver.',
  scope_is_not_reduced_to_common_subset=True))
 previous=load('audits/2026-10-30-stock-dimensionnement-05/inputs.json')
 complements=[]
 for pid,bounds in BOUNDS.items():
  models=[m for m in previous['schemas'] if m['package']==pid]
  behaviors=[w['work'] for w in previous['work'] if w['package']==pid]
  complements.append(dict(id=pid,**bounds,dimensioning_hypotheses=dict(structures=models,behavior_inventory=behaviors,
    field_count=sum(len(m['fields']) for m in models),new_models=sum(m['new_model'] for m in models),
    extensions=sum(not m['new_model'] for m in models),behavior_count=len(behaviors)),
   status='périmètre de travaux borné sous hypothèses ; charge non bornée en JH',
   unknowns=['Taille équivalente du complément complet, sans chevauchement avec le noyau natif.']+
    (['Volumes, débit, latence, RPO/RTO et qualification du service.'] if pid=='STOCK-F07' else []),
   equivalent_size=None,effort_jh=None,
   hypotheses_are_not_proven_upper_effort_bounds=True))
 assert sum(c['dimensioning_hypotheses']['field_count'] for c in complements)==126
 assert sum(c['dimensioning_hypotheses']['behavior_count'] for c in complements)==66
 write('complements.json',dict(complements=complements,architecture_assumptions=[
  'Un module Stock sur une base transactionnelle ; pas de nouvelle plateforme distribuée.',
  'Références et mécanismes communs Master Data réalisés et utilisables ; ce sont des travaux financés, pas du code Flow livré.',
  'Deux versions canoniques de payload, service de transformation/publication commun réutilisé.',
  'Les hypothèses structurent le périmètre ; elles ne constituent pas des plafonds de taille ou d’effort prouvés.'],
  exclusion='Aucun ratio arbitraire de retrait des prix/WMS, aucune nouvelle extrapolation par catégories de petites méthodes.'))
 write('reutilisation-master-data.json',dict(exact_native_overlaps=overlaps,
   generic_mechanisms=[dict(id=m['id'],funding_owner=m['funding_owner'],additional_generic_component_jh=None,
     interpretation='Déjà financé par Master Data ; aucune seconde ligne de financement. Les interfaces Stock restent à dimensionner.') for m in previous['reuse']],
   zero_is_not_used_for_unknown_adapter_work=True))
 matrix=[]
 for p in products:
  for c in components:
   matrix.append(dict(product=p,component=c['id'],outcome=c['common_outcome'],
     native_source_established=c['id']!='K5',
     exact_functional_equivalence=False,
     common_outcome_does_not_mean_all_Flow_guarantees_covered=True,
     size_chargeable_to_Flow=None,
     reason='Composant complet avec excédents natifs et adaptations Flow séparées.' if c['id']!='K5' else 'Contrats de contribution Flow bornés ; équivalent natif complet non établi.'))
 write('comparaison.json',dict(matrix=matrix,counts=dict(native_component_matches=16,Flow_contract_complements=4,fully_costable_reference_perimeters=0),
    alignment=dict(gap_jh=None,gap_pct=None,reason='Pas de quatre assiettes économiques homogènes pour COCOMO. Le rapprochement fonctionnel et les tailles brutes ne suffisent pas.')))
 report=dict(id='stock-composants-07',status='quatre_perimetres_fonctionnels_proposes_charges_non_recevables',
  outcome='Les quatre périmètres sont rapprochés au niveau de composants cohérents. Les références sont mesurées sans doublons et les compléments Flow bornés en contenu ; aucune nouvelle estimation JH défendable.',
  common_components=[dict(id=c['id'],label=c['label'],common_boundary=c['common_boundary']) for c in components],
  reference_footprints=summaries,
  interpretation_of_footprints='Mesures de composants entiers, incluant leurs excédents natifs ; ni quatre tailles de Flow ni classement de complexité des produits.',
  complementary_scope=dict(packages=7,behavior_hypotheses=66,data_structure_hypotheses=17,new_model_hypotheses=13,extension_hypotheses=4,field_hypotheses=126,
    does_not_bound_JH=True,service_objectives_still_unknown=True),
  what_progressed=[
   'Une même frontière fonctionnelle est déclarée par composant dans les quatre références ; les compléments Flow ne sont plus noyés dans leur code.',
   'Partages entre registre, positions, inventaire et réservation dédupliqués au niveau des fichiers/composants, avant tout effort.',
   'Recouvrements exacts du patrimoine natif Master Data retirés des empreintes supplémentaires, sans remise forfaitaire.',
   'Chaque complément a un contenu inclus/exclu, un inventaire de données, les services réutilisés et les inconnues ; aucun montant n’est déduit de ces seules limites.'],
  what_prevents_JH=[
   'Les composants complets contiennent quantité, prix, opérations physiques, allocation ou commandes dans des proportions différentes selon le produit.',
   'Retirer un pourcentage uniforme serait une hypothèse sans preuve ; isoler seulement les petites méthodes ramènerait au biais déjà mesuré.',
   'Les 66 traitements et 126 champs sont des hypothèses de conception, pas une preuve de taille complète des adaptations Flow.',
   'Les garanties de service restent partiellement ouvertes. Les 169 CFP / 20 h par CFP restent un repère conditionnel, pas quatre calculs COCOMO.'],
  current_estimates=dict(cumulative_adopted_gross_jh=1500,master_data_months=17,stock_adopted_jh=None,stock_native_reference_JH={p:None for p in products},stock_role_JH=None,stock_schedule_months=None),
  progress=dict(total_capabilities=88,campaign_framed=14,campaign_framed_pct=100*14/88,stock_capabilities_studied=8,
    adopted_capabilities=6,adopted_pct=100*6/88,new_capabilities_adopted=0,
    stock_complete_receivable_estimates=0,reference_perimeters_proposed=4,reference_perimeters_costable=0,
    native_component_outcomes_mapped=16,Flow_complement_packages_bounded_in_content=7,
    historical_note='Les 88 capacités ont des repérages historiques. Un périmètre proposé ou un composant rapproché ne vaut pas capacité chiffrée.'),
  progress_verdict=dict(scope_and_reuse_progress=True,decision_ready_effort_progress=False,
   statement='Le contenu et les frontières progressent ; le chiffrage validé stagne. Aucune réduction chiffrée de l’incertitude des JH n’est démontrée.',
   no_confidence_score_or_probability=True),
  decision=dict(repeat_same_code_audit_worthwhile=False,recommendation='Arrêter ce cycle d’affinage par découpage de code : il ne converge pas vers les quatre coûts comparables demandés.',
    alternative_to_discuss='Revoir le rôle du code OSS : preuve des mécanismes et analogies de composants, puis taille fonctionnelle paramétrique comme base de travail, avec productivité explicitement hypothétique. COCOMO reste la référence adoptée pour Master Data ; aucun changement méthodologique ou budget automatique.',
    no_external_project_actuals_or_full_specification_requested=True,
    reason='Changer encore la maille du même code n’apporte pas une règle étayée pour transformer les périmètres mêlés en tailles équivalentes Flow.'),
  evidence=['components.json','erpnext-perimetre.json','odoo-perimetre.json','tryton-perimetre.json','axelor-perimetre.json','complements.json','reutilisation-master-data.json','comparaison.json','ecarts-natifs-non-normalises.json'])
 (OUT/'bilan.yaml').write_text(yaml.safe_dump(report,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
 for p,h in protected.items():assert sha(ROOT/p)==h,p
 deps=set(protected_paths+['audits/2026-10-30-master-data-comparable-reuse/measurements.json',
   'audits/2026-10-30-master-data-natif/measure.py','audits/2026-10-30-stock-perimetres-02/build.py','audits/2026-10-30-stock-dimensionnement-05/inputs.json',
   'audits/2026-10-30-stock-completion-04/cosmic.json','audits/2026-10-30-stock-chaines-06/bilan.yaml'])
 for r in all_records:deps.add(str((Path(repos[r['repo']]['root'])/r['path'])).replace('\\','/'))
 deps.add(str(Path(__file__).resolve().relative_to(ROOT)).replace('\\','/'))
 for name in report['evidence']+['bilan.yaml']:deps.add(str((OUT/name).relative_to(ROOT)).replace('\\','/'))
 write('provenance.json',dict(protected=protected,dependencies=[dict(path=p,sha256=sha(ROOT/p)) for p in sorted(deps)]))
 print(json.dumps(dict(summaries=summaries,MD_overlapping_files=len(overlaps),perimeters_costable=0,cumulative_retained_jh=1500),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
