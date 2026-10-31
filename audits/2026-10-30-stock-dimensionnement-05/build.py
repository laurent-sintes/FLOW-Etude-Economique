"""Dimension Stock residual work from pinned native code analogies.
Proposal only. Does not change retained effort, capability inputs or app.
"""
from pathlib import Path
import ast, hashlib, importlib.util, json, sys, math, subprocess
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tmp/model-deps'),str(ROOT/'tools'),str(ROOT/'tmp/master-data-native-23/parser-deps')]
from model_context import model_session
from estimation_calculation import formula,alignment
import yaml

def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,x):(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def module(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path)
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
scope=module('stock_scope','audits/2026-10-30-stock-perimetres-02/build.py')
counter=module('native_counter','audits/2026-10-30-master-data-natif/measure.py')
products=['erpnext','odoo','tryton','axelor']
bank_specs={}
def bank(kind,rows):
 assert len(rows)==4
 bank_specs[kind]=dict(zip(products,rows))
E='erpnext/stock/'
O='addons/stock/models/'
T='modules/stock/'
A='axelor-stock/src/main/java/com/axelor/apps/stock/service/'
Q='axelor-quality/src/main/java/com/axelor/apps/quality/service/'
R='axelor-supplychain/src/main/java/com/axelor/apps/supplychain/service/ReservedQtyServiceImpl.java'
# Similar operations, not a claim of equal product functionality or productivity.
bank('guard',[
 ('erpnext',E+'doctype/stock_ledger_entry/stock_ledger_entry.py','StockLedgerEntry.validate_mandatory'),
 ('odoo',O+'stock_quant.py','StockQuant._compute_is_outdated'),
 ('tryton',T+'move.py','Move.check_origin'),
 ('axelor',R,'checkBeforeUpdatingQties')])
bank('query',[
 ('erpnext',E+'stock_ledger.py','get_sle_entries_by_names'),
 ('odoo',O+'stock_quant.py','StockQuant._get_quants_by_products_locations'),
 ('tryton',T+'location.py','Location.search_quantity'),
 ('axelor',A+'StockLocationLineFetchServiceImpl.java','getStockLocationLineListForAProduct')])
bank('compose',[
 ('erpnext',E+'stock_ledger.py','make_entry'),
 ('odoo',O+'stock_move_line.py','StockMoveLine._synchronize_quant'),
 ('tryton',T+'inventory.py','Inventory.confirm'),
 ('axelor',A+'StockLocationLineServiceImpl.java','createLocationLine')])
bank('reconcile',[
 ('erpnext',E+'stock_ledger.py','get_stock_reco_qty_shift'),
 ('odoo',O+'stock_quant.py','StockQuant._clean_reservations'),
 ('tryton',T+'inventory.py','InventoryLine.get_move'),
 ('axelor',A+'inventory/InventoryStockLocationUpdateServiceImpl.java','buildTrackedMap')])
bank('lock',[
 ('erpnext',E+'doctype/stock_reservation_entry/stock_reservation_entry.py','get_available_qty_to_reserve'),
 ('odoo',O+'stock_quant.py','StockQuant._update_available_quantity'),
 ('tryton',T+'move.py','Move._assign_try_lock'),
 ('axelor',R,'updateReservedQty@777')])
bank('state',[
 ('frappe','frappe/integrations/doctype/integration_request/integration_request.py','IntegrationRequest.handle_success'),
 ('odoo',O+'stock_quant.py','StockQuant.action_clear_inventory_quantity'),
 ('tryton',T+'inventory.py','InventoryLine.cancel_move'),
 ('axelor',R,'updateRequestedReservedQty@828')])
bank('observation',[
 ('erpnext',E+'doctype/quality_inspection/quality_inspection.py','QualityInspection.set_child_row_reference'),
 ('odoo',O+'stock_quant.py','StockQuant._get_inventory_move_values'),
 ('tryton','modules/quality/quality.py','Inspection.get_alert'),
 ('axelor',Q+'QualityImprovementCreateServiceImpl.java','createQualityImprovementFromControlEntry')])
bank('context',[
 ('erpnext',E+'report/stock_balance/stock_balance.py','StockBalanceReport.get_group_by_key'),
 ('odoo',O+'product.py','ProductProduct._get_dates_info'),
 ('tryton',T+'move.py','StockMixin._quantity_context'),
 ('axelor',A+'StockLocationLineFetchServiceImpl.java','getStockLocationLine')])
bank_notes={
 'guard':'Validation locale ou détection de contexte incohérent. Nombre de règles Stock distinctes proposé, non observé.',
 'query':'Lecture filtrée/groupée. Aucun moteur de requêtes générique refacturé.',
 'compose':'Commande qui coordonne validations et écritures natives. Les effets élémentaires déjà dans le noyau ne sont pas recopiés.',
 'reconcile':'Rapprochement/correction de quantités ou de listes. Ne démontre pas la correction temporelle Flow complète.',
 'lock':'Analogue de section transactionnelle sur quantités. Axelor ne prouve pas de verrou exclusif ; sa taille ne qualifie pas la garantie.',
 'state':'Petit traitement de résultat/transition. Le transport et le journal génériques Master Data sont réutilisés.',
 'observation':'Rattachement/création de données de constat. Odoo est un analogue de construction de valeurs de mouvement, pas une preuve de Product Feedback livré.',
 'context':'Construction d’une clé, de dates ou d’un contexte. Les structures plus riches de Flow restent une hypothèse.'
}

# Each item is a different residual behavior. Quantity=1, never based on occurrence volume.
# Operations already measured in the native seed are identified separately below.
work=[]
def items(pkg,kind,text):
 for label in text.split('|'):
  work.append(dict(id=f'{pkg}-T{sum(w["package"]==pkg for w in work)+1:02d}',package=pkg,kind=kind,quantity=1,work=label,
   sizing_status='analogie de taille ; existence/quantité de ce traitement cible supposée',
   funding_owner='stock-candidate',native_primitive_implementation_charged_again=False))
items('STOCK-F01','guard','Valider la clé sémantique producteur/identité du fait|Refuser le réemploi de clé avec une quantité différente|Vérifier les deux dates et la relation de correction|Valider la portion de stock et l’autorité événement/solde|Interdire un cycle de correction ou de filiation|Vérifier la conservation des quantités de filiation/contenu')
items('STOCK-F01','query','Retrouver l’effet Stock d’une admission générique|Rechercher les versions visibles à date de connaissance|Chercher le solde autoritatif couvrant la période')
items('STOCK-F01','compose','Composer admission générique et effet Stock dans une transaction|Admettre un solde externe et marquer sa frontière de couverture|Enregistrer une correction liée sans écraser son origine|Enregistrer liens de filiation et contenu connu')
items('STOCK-F01','reconcile','Sélectionner les effets reconnus entre solde externe et date de vue|Composer correction et filiation sans double effet')
items('STOCK-F02','guard','Vérifier la couverture du producteur et les ruptures de séquence|Valider les apports attendus sans les assimiler à des faits réalisés')
items('STOCK-F02','context','Qualifier la fraîcheur et les limites d’une position|Former un contexte commun de provenance et de dates')
items('STOCK-F02','query','Lire les dépendances et corrections d’une généalogie|Lire les références de propriété fournies sans tenir leur registre')
items('STOCK-F02','compose','Admettre/réviser un apport attendu fourni|Composer position et réservations avec leurs limites|Fournir une coupe immuable à la planification via publication commune')
items('STOCK-F02','state','Enregistrer la version de coupe effectivement fournie')
items('STOCK-F03','guard','Valider le protocole et les tolérances de comptage|Vérifier l’habilitation à décider une correction|Refuser un constat hors campagne ou hors portion autorisée')
items('STOCK-F03','compose','Préparer la campagne et son instant de référence|Enregistrer un constat et sa preuve|Appliquer une décision autorisée à travers le service de faits')
items('STOCK-F03','reconcile','Rapprocher le comptage et les mouvements concomitants|Réviser la décision lorsque la base de rapprochement a changé')
items('STOCK-F03','query','Consulter protocole/campagne/constats/décisions avec leurs liens')
items('STOCK-F04','guard','Valider identité et durée de l’engagement|Vérifier la version attendue pour une révision|Interdire consommation ou libération au-delà du restant')
items('STOCK-F04','lock','Ordonner les portions verrouillées d’un engagement multiple|Protéger la première création par unicité et traitement du conflit|Réaliser contrôle et modification sous la même transaction')
items('STOCK-F04','compose','Créer/réviser l’engagement avec les primitives natives|Consommer une réservation sur commande distincte du fait|Libérer/expirer une réservation sur commande distincte')
items('STOCK-F04','state','Enregistrer un conflit explicite et sa clé de reprise bornée|Enregistrer le résultat Stock d’une commande rejouée')
items('STOCK-F05','context','Construire la contribution Finance typée avec faits/propriété/provenance|Construire la correction Finance liée à la contribution originale')
items('STOCK-F05','guard','Valider auteur, référence et version du retour Finance|Refuser une transition de retour incompatible ou périmée')
items('STOCK-F05','compose','Fournir les faits à Finance par le service de publication commun')
items('STOCK-F05','state','Enregistrer acceptation/rejet et référence externe de prise en compte')
items('STOCK-F05','query','Consulter les contributions et leur état de retour')
items('STOCK-F06','observation','Relier fait produit contexte et preuve à un constat|Construire une correction de constat liée à son origine')
items('STOCK-F06','guard','Valider le responsable produit et la portée du constat')
items('STOCK-F06','compose','Fournir le constat au responsable par le service de publication commun')
items('STOCK-F06','state','Conserver la version de constat fournie et son résultat')
items('STOCK-F07','query','Lire les faits/soldes/engagements dans une même coupe de reprise|Lire les curseurs de contributions et consommateurs déclarés')
items('STOCK-F07','reconcile','Rapprocher les positions restaurées et les faits reconnus|Rapprocher réservations restantes et consommations/libérations|Rapprocher les sorties Finance/planification/produit après reprise')
items('STOCK-F07','compose','Brancher le blocage/reprise Stock sur le coordinateur Master Data|Exécuter une reconstruction Stock bornée et contrôlée')
items('STOCK-F07','guard','Empêcher réouverture sur invariants Stock non vérifiés|Configurer les limites et alertes propres aux traitements Stock')

schemas=[]
def schema(pkg,name,fields,view=False,existing=None):
 schemas.append(dict(package=pkg,name=name,new_model=existing is None,extends_native_model=existing,fields=fields.split(),view=view,
  generic_fields_not_recharged=['identifiant technique','auteur/date ORM','organisation et portée','identité/version d’enveloppe','journal générique admission'],
  status='schéma proposé, pas spécification validée'))
schema('STOCK-F01','StockFactExtension','sourceFactKey eventAt knownAt revisionOf effectKey authorityScope authorityMode provenanceRef',False,'native movement/ledger')
schema('STOCK-F01','ExternalStockBalance','productRef siteRef partyRef unitRef quantity asOf knownAt sourceRef authorityScope coversFrom coversTo revisionOf')
schema('STOCK-F01','StockEffectReceipt','admissionRef semanticKey effectRef resultKind appliedAt')
schema('STOCK-F01','StockLineageEdge','fromFactRef toFactRef quantity unitRef relationKind knownAt revisionOf',True)
schema('STOCK-F01','StockHandlingLink','containerRef contentRef quantity unitRef factRef knownAt revisionOf',True)
schema('STOCK-F02','ProducerCoverage','producerRef stockScope sequenceRef lastEventAt lastReceivedAt coverageFrom coverageTo limitReason',True)
schema('STOCK-F02','ExpectedSupplyExtension','sourceRef sourceVersion expectedAt knownAt revisionOf limitation',False,'native planned quantity')
schema('STOCK-F02','PlanningStockProvision','cutRef knownAt effectiveAt scopeRef payloadVersion contentHash limitation publicationRef',True)
schema('STOCK-F03','VerificationProtocol','scopeRef allowedMethod toleranceKind toleranceValue approvalRole validFrom validTo',True)
schema('STOCK-F03','CountExtension','observedAt baseFactCut proofRef observerRef protocolRef',False,'native inventory/count')
schema('STOCK-F03','StockAdjustmentDecision','countRef decisionVersion decisionKind reason authorRef authorizedAt baseFactCut correctionFactRef',True)
schema('STOCK-F04','StockCommitmentExtension','commitmentKey expectedVersion expiresAt originalQuantity consumedQuantity releasedQuantity lastCommandRef',False,'native reservation')
schema('STOCK-F04','StockConflictResult','commandRef commitmentRef expectedVersion currentVersion conflictKind recoveryKey resolvedAt',True)
schema('STOCK-F05','FinanceContribution','factRef ownershipRef version correctionOf payloadHash provisionRef consumerRef',True)
schema('STOCK-F05','FinanceReceipt','contributionRef consumerRef resultCode reason externalRef receivedAt version',True)
schema('STOCK-F06','ProductObservation','productRef factRef contextRef proofRef observedAt reason receiverRef correctionOf version provisionRef',True)
schema('STOCK-F07','StockRecoveryCheckpoint','epochRef cutRef lastFactRef lastCommitmentRef lastProvisionRef validationState discrepancyCount',True)

# Missing native caller responsibilities are replaced by explicit target coordination, not
# charged as full WMS/financial/optimization callers. Each residual entry gets a disposition.
boundary_package={
 'StockLedgerEntry.validate':'STOCK-F01','StockLedgerEntry.on_submit':'STOCK-F01',
 'StockReconciliation.validate_data':'STOCK-F03','StockReconciliation.update_stock_ledger':'STOCK-F03',
 'StockReconciliation.get_previous_ledger_entry':'STOCK-F03','update_entries_after.process_sle':'STOCK-F01',
 'StockReservationEntry.validate_reserved_entries':'STOCK-F04','StockReservation.make_stock_reservation_entry':'STOCK-F04',
 'StockBalanceReport.run':'STOCK-F02','StockBalanceReport.prepare_sle_query':'STOCK-F02','StockBalanceReport.get_item_warehouse_balance':'STOCK-F02',
 'make_sl_entries':'STOCK-F01','repost_future_sle':'STOCK-F01',
 'StockQuant.create':'STOCK-F04','StockQuant._get_reserve_quantity':'STOCK-F04',
 'Inventory.check_tolerance':'STOCK-F03','Move.assign_try':'STOCK-F04',
 'createInventoryLine':'STOCK-F03','updateInventoryLine':'STOCK-F03','storeLastInventoryData':'STOCK-F03','processPage':'STOCK-F03'
}
# One command/query adapter per functional process, operating generic public interfaces.
# Generic routing/security/serialization/ORM and reusable quantity algorithms are excluded.
api_package={1:'STOCK-F01',2:'STOCK-F01',3:'STOCK-F01',4:'STOCK-F01',5:'STOCK-F02',6:'STOCK-F02',7:'STOCK-F02',
8:'STOCK-F03',9:'STOCK-F03',10:'STOCK-F03',11:'STOCK-F03',12:'STOCK-F03',13:'STOCK-F04',14:'STOCK-F04',
15:'STOCK-F04',16:'STOCK-F04',17:'STOCK-F02',18:'STOCK-F05',19:'STOCK-F05',20:'STOCK-F06',21:'STOCK-F05'}

assumptions=[
 dict(id='H01',text='Même contrat proposé de 21 processus / 169 CFP dans quatre écosystèmes natifs ; les compléments sont des développements cibles par analogie, pas du code déjà fourni par les quatre produits.'),
 dict(id='H02',text='Master Data est construite et ses huit mécanismes génériques peuvent servir Stock. C’est une réutilisation de conception financée, pas un composant Flow livré et mesuré. Aucun nouveau pourcentage sur la totalité du framework.'),
 dict(id='H03',text='Une base transactionnelle avec verrouillage/unicité, transactions courtes, ordre déterministe des portions, refus explicite des conflits et rejeu par clé. Pas de réservation distribuée entre bases ni garantie de progrès sans attente.'),
 dict(id='H04',text='Deux dates, une couverture autoritative explicite par portion ; on conserve les corrections et les liens. Pas de fusion automatique de sources contradictoires ni reconstitution de faits jamais reçus.'),
 dict(id='H05',text='API métier et écrans génériques administratifs. Pas de WMS mobile, capture de terminaux, valeur financière, moteur d’allocation, optimisation ou PLM.'),
 dict(id='H06',text='Reprise cohérente de la base et rapprochement Stock avant réouverture, à partir des services Master Data. RPO/RTO, débits, volumétrie et plafond de latence ne sont pas engagés ; leur impact de dimensionnement reste inconnu.'),
 dict(id='H07',text='Chaque traitement listé vaut une instance de l’analogue mesuré de sa technologie ; analogie et quantité sont des hypothèses d’ingénierie, pas une calibration de productivité. Les unités AST/déclarations sont le proxy de taille utilisé pour Master Data, pas des SLOC physiques certifiées COCOMO.'),
 dict(id='H08',text='Le coût est une unité Stock autonome au sens du modèle retenu ; le cumul de décisions n’est pas un COCOMO intégré de tout Flow. Aucune réduction 0,8 ni gain IA.'),
 dict(id='H09',text='Les requêtes, mutations de quantités, arrondis/conversions et présentations sélectionnés restent dans le noyau mesuré ; les nouveaux traitements orchestrent ces primitives, sans les réimplémenter. Les champs hérités ne sont pas recomptés.'),
 dict(id='H10',text='Une commande ou consultation distincte par processus proposé. Les branchements de sécurité, enveloppe, références et publication sont dimensionnés une fois par processus, pas une fois par mouvement COSMIC ou consommateur.'),
]
def measure_analogue(product,kind,row):
 repo,path,selector=row
 root=ROOT/scope.repos[repo]['root'];f=root/path
 raw,methods,_=scope.parse(f)
 found=[m for m in methods if scope.matches(m,selector)];assert len(found)==1,(product,kind,found)
 m=found[0];text=raw.decode('utf-8-sig');nodes=[]
 if f.suffix=='.py':
  for n in ast.walk(ast.parse(text)):
   if not isinstance(n,ast.stmt):continue
   if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):continue
   if m['start']<=n.lineno<=n.end_lineno<=m['end']:nodes.append(dict(kind=type(n).__name__,start=n.lineno,end=n.end_lineno))
 else:
  tree=scope.JAVA.parse(raw);assert not tree.root_node.has_error
  for n in counter.walk(tree.root_node):
   if not ((n.type.endswith('_statement') and n.type!='empty_statement') or n.type in counter.JAVA_EXTRA):continue
   a,b=n.start_point.row+1,n.end_point.row+1
   if m['start']<=a<=b<=m['end']:nodes.append(dict(kind=n.type,start=a,end=b))
 assert nodes
 return dict(id=f'{product}:{kind}',product=product,repo=repo,path=path,commit=scope.repos[repo]['commit'],
  sha256=digest(f),symbol=m['name'],start=m['start'],end=m['end'],program_units=len(nodes),counted_nodes=nodes,
  usage='gabarit mesuré pour un nouveau traitement ; pas ajout une seconde fois de ce code source natif',
  limitation=bank_notes.get(kind,'Validation alternative, diagnostic du choix de gabarit.'))

def main():
 OUT.mkdir(exist_ok=True)
 protected_paths=['source/estimations-core-retenues.yaml','source/referentiel-capacites.yaml','sources/cartographie-scm-2026-10-24.yaml','source/fondamentaux.yaml','source/calculs-estimation-core.yaml']
 protected={p:digest(ROOT/p) for p in protected_paths}
 for repo in sorted({r[0] for rows in bank_specs.values() for r in rows.values()}):
  root=ROOT/scope.repos[repo]['root']
  actual=subprocess.check_output(['C:/Program Files/Git/cmd/git.exe','-C',str(root),'rev-parse','HEAD'],text=True).strip()
  assert actual==scope.repos[repo]['commit'],repo
 analogues=[measure_analogue(p,k,rows[p]) for k,rows in bank_specs.items() for p in products]
 amap={a['id']:a for a in analogues}
 write('analogues.json',dict(convention_ref='audits/2026-10-30-master-data-natif/measure.py',counter_sha256=digest(ROOT/'audits/2026-10-30-master-data-natif/measure.py'),samples=analogues))
 old=yaml.safe_load((ROOT/'audits/2026-10-30-stock-completion-04/bilan.yaml').read_text(encoding='utf-8'))
 packages=old['missing_work_packages']
 for p in packages:
  if p['id']=='STOCK-F01' and 'S04' not in p['cosmic']:p['cosmic'].append('S04')
  p['size_status']='inventaire dimensionné par analogies de méthodes ; équivalence de mécanisme complet non établie'
 # Generic reuse has a named funding owner and zero new component size. Its Stock adapters are explicit.
 reuse=[
  dict(id=k,funding_owner='master-data-java-spring',additional_generic_component_units=0,
       additional_stock_adapters='interfaces / champs / appels métier dimensionnés ci-dessous')
  for k in ['java-spring-framework-services','master-data-common-domain','master-data-admission','master-data-semantique','master-data-protection','master-data-reprise','master-data-versions','master-data-service']]
 boundary=load('audits/2026-10-30-stock-completion-04/frontieres-classees.json')
 for b in boundary:
  if 'adaptateur' in b['decision']:
   pkg=boundary_package.get(b['name']);assert pkg,(b['product'],b['name'])
   b['target_replacement']=dict(package=pkg,mode='orchestration cible par analogie et interface par processus ; appelant natif complet non repris')
  elif 'appelant' in b['decision']:
   b['target_replacement']=dict(mode='appel par API cible ; exécutant WMS/affectation/valorisation exclu, les primitives quantité restent dans le noyau mesuré')
  else:b['target_replacement']=dict(mode='hors contrat cible, aucun budget nouveau')
 write('frontieres-resolues-pour-la-proposition.json',boundary)
 matrix=load('audits/2026-10-30-stock-completion-04/matrice-native-cosmic.json')
 for r in matrix:
  i=int(r['process'][1:]);pkg=api_package[i]
  r.update(size_coverage='noyau natif partiel + compléments proposés par analogie',
    target_package=pkg,adapter_id='API-'+r['process'],
    native_complete_equivalence_established=False)
 write('couverture-processus.json',matrix)
 inputs=dict(id='stock-dimensionnement-05',status='proposition conditionnelle non adoptée',packages=packages,
  work=work,schemas=schemas,api_package=api_package,reuse=reuse,assumptions=assumptions,
  interfaces=dict(count=21,source='un branchement par processus COSMIC, pas par occurrence',
    per_process_components=['guard','context'],
    excluded='routage / sécurité / ORM / sérialisation / moteur de publication génériques déjà financés'),
  native_schema_templates={
   'erpnext':dict(program_per_field=0,declarations_per_field=1,per_new_model=1,view_field=0,view_model=0,
    rationale='Métadonnées DocType : un champ et un modèle selon compteur natif ; formulaires générés.'),
   'odoo':dict(program_per_field=1,declarations_per_field=0,per_new_model=3,view_field=2,view_model=4,
    rationale='Champ ORM Python ; classe/_name/_description ; champ de liste et formulaire, quatre conteneurs par paire de vues.'),
   'tryton':dict(program_per_field=1,declarations_per_field=0,per_new_model=2,view_field=2,view_model=2,
    rationale='Champ ORM Python ; classe/__name__ ; liste/formulaire, deux conteneurs. Enregistrement supplémentaire du module ci-dessous.'),
   'axelor':dict(program_per_field=0,declarations_per_field=1,per_new_model=1,view_field=2,view_model=2,
    rationale='Champs/entity du modèle XML et paires grid/form. Aucun getter généré ajouté.')},
  schema_template_status='Conventions explicites dérivées du style natif ; attributs et comportements par champ restent supposés.',
  stock_configuration=[
   dict(id='model-registration',quantity=sum(s['new_model'] for s in schemas),meaning='une inscription/configuration par nouveau modèle',units_per_quantity=1),
   dict(id='business-index',quantity=8,meaning='unicité effet, version fait, portion/date, couverture solde, réservation, expiration, contribution, curseur de reprise',units_per_quantity=1),
   dict(id='service-bindings',quantity=7,meaning='un branchement de service par ensemble F01 à F07',units_per_quantity=1),
   dict(id='service-module-structure',quantity=7,meaning='classe/imports/injection d’un module cible par ensemble F01 à F07',kind='context'),
   dict(id='version-mappings',quantity=8,meaning='un mapping déclaratif par type de payload Stock : fait, solde, apport, constat, décision, engagement, Finance, produit',units_per_quantity=1)],
  formulas_ref='source/fondamentaux.yaml#estimation_model.rules',
  native_full_historical_cost=None,
  activity_source='audits/2026-10-30-master-data-calcul/repartitions-sources.json#cocomo')
 write('inputs.json',inputs)
 base=load('audits/2026-10-30-stock-completion-04/tailles-completees.json')
 c=load('audits/2026-10-30-master-data-spring-flow/inputs.json')['cocomo']
 activity=load('audits/2026-10-30-master-data-calcul/repartitions-sources.json')['cocomo']
 rows=[]
 with model_session():
  exponent=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum'])
  def effort(units):return formula('cocomo_effort',A=c['A'],KSLOC=units/1000,E=exponent,EM=1,SCED=c['SCED'],month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor'])
  for p in products:
   lines=[]
   for w in work:
    a=amap[f'{p}:{w["kind"]}']
    lines.append(dict(id=w['id'],package=w['package'],category='traitement',analogue=a['id'],quantity=w['quantity'],unit_program=a['program_units'],program_units=w['quantity']*a['program_units'],declarative_units=0))
   for i in range(1,22):
    for kind in inputs['interfaces']['per_process_components']:
     a=amap[f'{p}:{kind}']
     lines.append(dict(id=f'API-S{i:02d}-{kind}',package=api_package[i],category='branchement',analogue=a['id'],quantity=1,unit_program=a['program_units'],program_units=a['program_units'],declarative_units=0))
   t=inputs['native_schema_templates'][p]
   for s in schemas:
    n=len(s['fields']);new=int(s['new_model']);view=int(s['view'])
    # Field occurrence costs are explicit and native-specific, not a rating of complexity.
    pu=n*t['program_per_field']
    du=n*t['declarations_per_field']+new*t['per_new_model']+view*(n*t['view_field']+t['view_model'])
    lines.append(dict(id='MODEL-'+s['name'],package=s['package'],category='modèle/vue',fields=n,new_model=bool(new),program_units=pu,declarative_units=du))
   for cfg in inputs['stock_configuration']:
    a=amap[f'{p}:{cfg["kind"]}'] if 'kind' in cfg else None
    pu=cfg['quantity']*a['program_units'] if a else 0
    du=0 if a else cfg['quantity']*cfg['units_per_quantity']
    lines.append(dict(id='CFG-'+cfg['id'],package='SHARED-STOCK',category='configuration',quantity=cfg['quantity'],analogue=a['id'] if a else None,program_units=pu,declarative_units=du))
   assert len({l['id'] for l in lines})==len(lines)
   core=base[p]['selected_equivalent_units_at_weight_1']
   extra=sum(l['program_units']+l['declarative_units'] for l in lines)
   total=core+extra
   # Allocate the marginal complement effort by size share; no sum of independent COCOMO jobs.
   common_jh=effort(core);total_jh=effort(total);residual_jh=total_jh-common_jh
   pkg_rows=[]
   for pkg in [x['id'] for x in packages]+['SHARED-STOCK']:
    selected=[l for l in lines if l['package']==pkg]
    size=sum(l['program_units']+l['declarative_units'] for l in selected)
    pkg_rows.append(dict(id=pkg,program_units=sum(l['program_units'] for l in selected),declarative_units=sum(l['declarative_units'] for l in selected),equivalent_units=size,
     jh_share_of_marginal_complements=residual_jh*size/extra,effort_allocation_status='répartition proportionnelle à la taille, pas effort observé par paquet'))
   assert math.isclose(sum(x['jh_share_of_marginal_complements'] for x in pkg_rows),residual_jh)
   acts=[]
   for a in activity['activities']:
    share=sum(x*y for x,y in zip(activity['phase_effort_percent_of_base'],a['percent_by_phase']))/100/sum(activity['phase_effort_percent_of_base'])
    acts.append(dict(id=a['id'],label=a['label'],jh=total_jh*share,share=share,published_percent_by_phase=a['percent_by_phase']))
   assert math.isclose(sum(x['jh'] for x in acts),total_jh)
   f07=next(x for x in pkg_rows if x['id']=='STOCK-F07')['equivalent_units']
   cosine=load('audits/2026-10-30-stock-completion-04/cosmic.json')['result']['indicative_jh']
   row=dict(id=p,technology=scope.repos[p]['repository'],status='essai arithmétique non qualifié comme coût de la famille Stock',
    measured_native_core_units=core,additional_program_units=sum(l['program_units'] for l in lines),additional_declarative_units=sum(l['declarative_units'] for l in lines),
    proposed_complement_units=extra,total_equivalent_units=total,COCOMO=dict(E=exponent,KSLOC=total/1000,EM=1,SCED=c['SCED'],effort_phase_factor=c['effort_phase_factor'],A=c['A'],month_hours=c['month_hours'],day_hours=c['day_hours']),
    measured_core_only_jh=common_jh,trial_complements_marginal_jh=residual_jh,trial_jh=total_jh,
    native_implemented_full_family_jh=None,receivable_stock_family_jh=None,
    package_sizes_and_allocations=pkg_rows,activities=acts,lines=lines,
    functional_comparison=dict(jh=cosine,condition='20 h/CFP et facteur 1 repris du pilote ; pas une productivité Stock calibrée',
      alignment=dict(gap_jh=None,gap_pct=None,reason='analogie native non qualifiée et service Stock non apparié au repère fonctionnel'),comparison_status='comparaison numérique non recevable à ce stade'),
    sensitivities_not_probability=dict(remove_F07_jh=total_jh-effort(total-f07),
      all_residual_treatments_plus_1_unit_jh=effort(total+sum(w['quantity'] for w in work))-total_jh,
      residual_size_share_pct=100*extra/total),
    cumulative_retained_jh=1500,cumulative_with_stock_jh=None)
   rows.append(row)

 # A deliberate change of analogy, with unchanged target behavior count. This is a
 # model diagnostic, NOT an uncertainty interval and not a selection of a preferred result.
 alternative_guard_rows=[
  ('erpnext',E+'doctype/stock_reservation_entry/stock_reservation_entry.py','StockReservationEntry.validate_with_allowed_qty'),
  ('odoo',O+'stock_quant.py','StockQuant._get_available_quantity'),
  ('tryton',T+'inventory.py','InventoryLine.on_change_with_tolerance_quantity_variation'),
  ('axelor',A+'inventory/InventoryValidateServiceImpl.java','checkMissingStockLocation')]
 guard_count=sum(w['quantity'] for w in work if w['kind']=='guard')+21
 checks=[]
 for p,row in zip(products,alternative_guard_rows):
  alt=measure_analogue(p,'guard-alternative',row)
  alt['limitation']='Autre validation native, de contenu différent. Test du caractère trop large de la catégorie, sans équivalence fonctionnelle revendiquée.'
  alt['source_fragment']='\n'.join((ROOT/scope.repos[alt['repo']]['root']/alt['path']).read_text(encoding='utf-8-sig').splitlines()[alt['start']-1:alt['end']])
  native=amap[p+':guard'];r=next(x for x in rows if x['id']==p)
  delta_units=guard_count*(alt['program_units']-native['program_units'])
  changed=effort(r['total_equivalent_units']+delta_units)
  checks.append(dict(product=p,target_scope_and_quantity_unchanged=True,count=guard_count,
    original_analogue=native['id'],alternative=alt,original_trial_jh=r['trial_jh'],alternative_trial_jh=changed,
    change_jh=changed-r['trial_jh'],change_pct=100*(changed-r['trial_jh'])/r['trial_jh'],
    meaning='sensibilité au choix du gabarit ; pas une probabilité, une enveloppe ou une nouvelle estimation'))
  analogues.append(alt)
 for a in analogues:
  f=ROOT/scope.repos[a['repo']]['root']/a['path']
  a['source_fragment']='\n'.join(f.read_text(encoding='utf-8-sig').splitlines()[a['start']-1:a['end']])
  a['source_url']='https://github.com/'+scope.repos[a['repo']]['repository'].removesuffix('.git')+'/blob/'+a['commit']+'/'+a['path']
 write('analogues.json',dict(convention_ref='audits/2026-10-30-master-data-natif/measure.py',
  counter_sha256=digest(ROOT/'audits/2026-10-30-master-data-natif/measure.py'),samples=analogues,
  qualification='Des méthodes complètes sont mesurées ; une méthode complète ne constitue pas nécessairement un mécanisme métier complet.'))
 write('sensibilite-analogies.json',dict(status='contre-épreuve du choix des analogies, non intervalle statistique',checks=checks))
 for r in rows:
  r['eligibility']=dict(full_family_native_cost=False,conditional_target_cost_receivable=False,
   size_counter_reproducible=True,unique_funding_explicit=True,complete_mechanism_equivalence=False,
   activity_distribution_preserved=True,performance_and_recovery_objectives_sized=False,
   reason='Les catégories guard/context/compose appliquées uniformément ne justifient pas la taille des mécanismes complets. Les interfaces et les règles peuvent se recouvrir. Ne pas transformer les quatre essais en coûts de famille.')
 write('results.json',dict(id='stock-dimensionnement-05',rows=rows,formula_source='source/fondamentaux.yaml',
  cumulative_adopted_gross_jh=1500,master_data_months=17,stock_adopted_jh=None,stock_adopted_months=None,
  trial_only_not_receivable=True,probability=None,confidence_class=None))
 for p,h in protected.items():assert digest(ROOT/p)==h,p
 # Full dependency closure for reproduction. Include raw measured file identities and scripts.
 deps=set(protected_paths+[
 'audits/2026-10-30-stock-perimetres-02/build.py','audits/2026-10-30-stock-cadrage-01/avancement.yaml','audits/2026-10-30-master-data-comparable-reuse/measurements.json',
 'audits/2026-10-30-master-data-natif/measure.py','audits/2026-10-30-stock-completion-04/bilan.yaml',
 'audits/2026-10-30-stock-completion-04/frontieres-classees.json','audits/2026-10-30-stock-completion-04/matrice-native-cosmic.json',
 'audits/2026-10-30-stock-completion-04/tailles-completees.json','audits/2026-10-30-stock-completion-04/cosmic.json',
 'audits/2026-10-30-master-data-spring-flow/inputs.json','audits/2026-10-30-master-data-calcul/repartitions-sources.json',
 'source/schema-fondamentaux.yaml','tools/estimation_calculation.py','tools/model_context.py','tools/validate_stacks.py'])
 for p in products:
  deps.add(f'audits/2026-10-30-stock-mesures-03/{p}-mesures.json')
  deps.add(f'audits/2026-10-30-stock-completion-04/{p}-presentation.json')
 for a in analogues:deps.add(str((Path(scope.repos[a['repo']]['root'])/a['path'])).replace('\\','/'))
 deps.add(str(Path(__file__).resolve().relative_to(ROOT)).replace('\\','/'))
 deps.add(str((OUT/'verify.py').relative_to(ROOT)).replace('\\','/'))
 for name in ('inputs.json','results.json','analogues.json','sensibilite-analogies.json','couverture-processus.json','frontieres-resolues-pour-la-proposition.json'):
  deps.add(str((OUT/name).relative_to(ROOT)).replace('\\','/'))
 write('provenance.json',dict(dependencies=[dict(path=p,sha256=digest(ROOT/p)) for p in sorted(deps)],protected=protected))
 print(json.dumps([dict(id=r['id'],core=r['measured_native_core_units'],residual=r['proposed_complement_units'],trial_JH=r['trial_jh'],receivable_stock_jh=r['receivable_stock_family_jh']) for r in rows],ensure_ascii=False,indent=2))
if __name__=='__main__':main()
