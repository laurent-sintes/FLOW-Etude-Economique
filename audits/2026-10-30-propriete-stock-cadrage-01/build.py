"""Read-only source evidence for BC-014/015; no effort calculation or adoption."""
from pathlib import Path
import ast,hashlib,importlib.util,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
import yaml
from capability_catalog import analysis,native

def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def module(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def yaml_save(name,value):(OUT/name).write_text(yaml.safe_dump(value,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')

def main():
 protected=['source/estimations-core-retenues.yaml','source/calculs-estimation-core.yaml','source/fondamentaux.yaml',
  'source/schema-fondamentaux.yaml','source/referentiel-capacites.yaml','sources/cartographie-scm-2026-10-24.yaml']
 before={p:sha((ROOT/p).read_bytes()) for p in protected}
 selection=read((OUT/'selection.json').relative_to(ROOT).as_posix())
 scope=module('ownership_scope','audits/2026-10-30-stock-perimetres-02/build.py')
 counter=module('ownership_counter','audits/2026-10-30-master-data-natif/measure.py')
 md=read('audits/2026-10-30-master-data-comparable-reuse/measurements.json')
 stock=read('audits/2026-10-30-stock-opportunite-08/inputs.json')
 git='C:/Program Files/Git/cmd/git.exe';products=list(selection)
 md_index={(f['product'],f['repo'],f['path']):f for f in md['files']}
 stock_index={(f['product'],f['repo'],f['path']):f for f in stock['attributions']}
 known={}
 for p in products:
  old=read(f'audits/2026-10-30-stock-mesures-03/{p}-mesures.json')
  known[p]={f['path']:{(n['kind'],n['start'],n['end']) for n in f['counted_nodes']} for f in old['files']}
 repos=md['repos'];rows=[];witnesses=[];summary={};revisions={}
 for p in products:
  repo=repos[p];root=ROOT/repo['root']
  head=subprocess.check_output([git,'-C',str(root),'rev-parse','HEAD']).decode().strip()
  assert head==repo['commit'],p
  revisions[p]=dict(repository=repo['repository'],commit=head)
  selected_files=set();selected_methods=0;nodes_by_file={}
  for relative,selectors,note in selection[p]:
   assert relative not in selected_files;selected_files.add(relative)
   path=root/relative;raw=path.read_bytes()
   blob=subprocess.check_output([git,'-C',str(root),'show',head+':'+relative])
   assert raw.replace(b'\r\n',b'\n')==blob.replace(b'\r\n',b'\n'),str(path)
   parsed,methods,declarations=scope.parse(path);assert parsed==raw
   size=counter.measure(path);prior_md=md_index.get((p,p,relative));prior_stock=stock_index.get((p,p,relative))
   if prior_md:assert prior_md['sha256']==sha(raw),'Changed Master Data source'
   if prior_stock:assert prior_stock['sha256']==sha(raw),'Changed Stock source'
   if path.suffix=='.py':
    tree=ast.parse(raw.decode('utf-8-sig'))
    allnodes={(type(n).__name__,n.lineno,n.end_lineno) for n in ast.walk(tree)
      if isinstance(n,ast.stmt) and not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str))}
   elif path.suffix=='.java':
    tree=counter.PARSERS['.java'].parse(raw)
    allnodes={(n.type,n.start_point.row+1,n.end_point.row+1) for n in counter.walk(tree.root_node)
     if (n.type.endswith('_statement') and n.type!='empty_statement') or n.type in counter.JAVA_EXTRA}
   else:allnodes=set()
   file_nodes=set()
   for selector in selectors:
    matches=[m for m in methods if scope.matches(m,selector)];assert len(matches)==1,(p,relative,selector)
    m=matches[0];nodes={n for n in allnodes if m['start']<=n[1]<=n[2]<=m['end']}
    assert nodes
    file_nodes|=nodes;paid=nodes&known[p].get(relative,set())
    witnesses.append(dict(product=p,path=relative,sha256=sha(raw),commit=head,method=selector,
     start=m['start'],end=m['end'],program_units=len(nodes),known_Stock_floor_overlap=len(paid),
     calls=m['calls'],note=note,url='https://github.com/'+repo['repository']+'/blob/'+head+'/'+relative+'#L'+str(m['start']),
     nodes=[dict(kind=k,start=a,end=b) for k,a,b in sorted(nodes)]))
    selected_methods+=1
   nodes_by_file[relative]=file_nodes
   rows.append(dict(product=p,repo=p,path=relative,sha256=sha(raw),git_blob_sha256=sha(blob),commit=head,
    git_content_verified_with_CRLF_normalization=True,url='https://github.com/'+repo['repository']+'/blob/'+head+'/'+relative,
    **size,selected_methods=selectors,witness_program_units_union=len(file_nodes),
    witness_known_Stock_floor_overlap=len(file_nodes&known[p].get(relative,set())),
    relevant_declarations=[d for d in declarations if re.search('owner|consign|customer_provided|partner|company|dimension',d['name'],re.I)],
    prior_funding_context=dict(master_data_file=bool(prior_md),stock_component_file=bool(prior_stock),
      meaning='Fichier présent dans une preuve antérieure ; cela ne signifie pas que toutes ses instructions sont financées. Les parts de code mixte restent des hypothèses distinctes.',
      Stock_attribution=prior_stock['attribution'] if prior_stock else None,
      known_Stock_program_floor=prior_stock['known_stock_program_floor'] if prior_stock else None),
    purpose=note,eligible_as_new_ownership_effort=False,
    size_note='Empreinte de recherche et témoins natifs. Ni taille de la propriété Flow ni charge à financer ; contient du patrimoine déjà financé et des fonctions hors périmètre.'))
  subset=[r for r in rows if r['product']==p]
  summary[p]=dict(files=len(subset),witness_methods=selected_methods,
   raw_component_program_units=sum(r['program_units'] for r in subset),
   raw_component_declarative_units=sum(r['declarative_units'] for r in subset),
   witness_program_units_union=sum(len(v) for v in nodes_by_file.values()),
   witness_known_Stock_floor_overlap=sum(len(v&known[p].get(path,set())) for path,v in nodes_by_file.items()),
   files_already_in_Master_Data_measure=sum(r['prior_funding_context']['master_data_file'] for r in subset),
   files_already_in_Stock_measure=sum(r['prior_funding_context']['stock_component_file'] for r in subset),
   ownership_effort_jh=None,not_a_zero_estimate=True)
 # Copy the input content as dated evidence; do not edit the canonical capability source.
 nodes={n['id']:n for n in native()['nodes']}
 selected=[b for b in analysis()['blocs'] if b['id'] in ('BC-014','BC-015')]
 native_scope=[dict(id=b['id'],native_id=b['capacite_id'],path=b['chemin'],
   fields={k:nodes[b['capacite_id']]['fields'].get(k) for k in ('name','definition','finality','scope')},study_analysis=b) for b in selected]
 outputs=[
  dict(id='O1',result='Qualifier une conséquence sur la propriété depuis des faits et une version de conditions reçues.',capacity='BC-014'),
  dict(id='O2',result='Déterminer parties, quantité, date d’effet et fondement ; sinon garder une justification en attente.',capacity='BC-014'),
  dict(id='O3',result='Demander l’acte nécessaire et attendre son résultat, ou intégrer un transfert déjà établi sans nouvelle décision.',capacity='BC-014'),
  dict(id='O4',result='Inscrire chaque passage reconnu de propriété sans mouvement physique artificiel ni double stock.',capacity='BC-015'),
  dict(id='O5',result='Conserver sources, acte, annulations et corrections avec date d’effet et de connaissance.',capacity='BC-015'),
  dict(id='O6',result='Reconstituer les quantités par propriétaire à date, y compris passages entre sociétés.',capacity='BC-015')]
 gaps=[
  dict(id='OWN-F01',name='Conditions de propriété et contexte applicables',work='Référencer conditions/version/portée reçues et rapprocher les faits de Stock et des accords. Pas nouvelle édition des accords ni règles Beaumanoir.',
    candidate_analogue='Évaluation conditionnelle des dimensions ERPNext ; critères de consignation Tryton ; validation de paramètres Java.',reuse='Accords, parties, articles, unités, versions et admission Master Data.'),
  dict(id='OWN-F02',name='Détermination du transfert et quantités',work='Trois familles de déclencheurs : consommation/vente, échéance et jalon reçu ; produire parties, quantité et date ou justification manquante.',
    candidate_analogue='Chaînes de consignation Tryton et propagation Odoo, sans confondre facturation et fait de propriété.',reuse='Faits et positions Stock ; règles métier spécifiques fournies par intégration.'),
  dict(id='OWN-F03',name='Actes requis et transferts reconnus ailleurs',work='État local en attente, référence de demande externe, réception du résultat et admission d’un transfert déjà établi. Pas reconstruction du moteur de processus.',
    candidate_analogue='Transitions et origines natives, protocoles de contribution Master Data/Stock.',reuse='Identité des commandes, admission et journal génériques déjà financés. Familles Orders/processus pas encore estimées : dépendance distincte.'),
  dict(id='OWN-F04',name='Registre autonome de propriété',work='Écritures ancien/nouveau propriétaire, quantité, fondement, preuves et liens ; plusieurs passages pour les mêmes biens sans doubler la position physique.',
    candidate_analogue='Registres/mouvements des quatre OSS déjà étudiés ; la nouvelle écriture de propriété reste à dimensionner.',reuse='Persistance, transactions et registres Stock ; nouveaux invariants métier non assimilés à une simple colonne.'),
  dict(id='OWN-F05',name='Corrections et lectures aux deux dates',work='Annulations/corrections expliquées ; lecture à date d’effet et selon la connaissance disponible.',
    candidate_analogue='Correction de propriétaire Odoo et chaînes de correction Stock ; dates physiques natives ne suffisent pas seules.',reuse='Journal/version/reprise Master Data et correction Stock, sans financer à nouveau leurs moteurs.'),
  dict(id='OWN-F06',name='Rapprochement et fourniture des positions de propriété',work='Rapprocher le registre de propriété et les positions existantes ; rendre les résultats et limites disponibles aux capacités Stock et Finance.',
    candidate_analogue='Restitutions filtrées Odoo, quantités et historiques Java/Tryton/ERPNext.',reuse='Inventory Visibility et Accounting Data Provision déjà financés en Stock. Pas seconde publication Finance ni valorisation comptable.')]
 family=dict(id='propriete-stock-cadrage-01',date='2026-10-30',status='cadrage_et_reperage_code_pas_estimation',
  evaluation_unit=dict(level='business_area',native_id='ba-inventory-ownership-management',label='Gestion de la propriété du stock',capabilities=native_scope),
  outputs=outputs,excludes=['Valorisation comptable, écritures financières et facturation','Négociation des accords et codage des clauses propres à Beaumanoir','Mouvements physiques, réservations et réalisation des prestations','Disposition BC-019, décisions de réparation/rebut et optimisation','Construction des familles Orders et orchestration pas encore financées'],
  shared_funding='Réutilisation Master Data et Stock avec propriétaires inchangés. Adaptations et invariants de propriété à dimensionner séparément.',
  size_policy='La méthode amont autorise des parts de composants et analogies explicites. Les tailles brutes du repérage ne deviennent pas des KSLOC Flow ni une facture de reconstruction.',
  new_Flow_modules_to_size=gaps)
 yaml_save('cadrage.yaml',family)
 findings=[
  dict(product='erpnext',observation='Indicateur de bien fourni par un client ; contrôles de réception et de lieu ; dimensions de stock configurables.',
   limit='Les contrôles étudiés portent aussi sur valeur nulle et sous-traitance ; ils ne démontrent pas un registre autonome de propriété ni un transfert contractuel générique.'),
  dict(product='odoo',observation='Propriétaire dans les quants, lignes et documents ; propagation, filtrage des positions et annulation/rejeu des quantités lors d’une correction.',
   limit='Les mécanismes relus corrigent des mouvements/positions. Ils ne démontrent pas à eux seuls un registre contractuel indépendant avec les deux dates Flow.'),
  dict(product='tryton',observation='Module de consignation fournisseur et client, tiers porté par lieu ; transitions de mouvements liées aux lignes de facture.',
   limit='Le code apporte un analogue de déclenchement et de traçabilité ; sa logique de facturation et ses lieux ne sont pas une équivalence démontrée au registre Flow.'),
  dict(product='axelor',observation='Lieu de consignation dans le module de production et choix de lieu en sous-traitance ; positions et historique de Stock disponibles.',
   limit='Partenaire, société et lieu ne sont pas réputés propriétaires des quantités. Le périmètre exploré ne démontre pas le moteur de transfert ou le registre autonome demandés.') ]
 save('preuves-code.json',dict(revisions=revisions,summary=summary,files=rows,witnesses=witnesses,findings=findings,
  code_execution=False,OSS_tests_executed=False,Git_content_verified=True,
  statement='Lecture statique de révisions figées. Absence de preuve dans cette sélection distincte d’une absence générale dans le produit.'))
 save('documentation.json',dict(consulted_on='2026-10-30',documents=[
  dict(url='https://docs.frappe.io/erpnext/customer-provided-items',status='consulted',meaning='Corrobore le parcours de réception de biens fournis par un client ; pas preuve du registre Flow.'),
  dict(url='https://www.odoo.com/documentation/18.0/applications/inventory_and_mrp/inventory/shipping_receiving/daily_operations/owned_stock.html',status='search_result_only_version_18',meaning='Repère documentaire ; code v20 figé fait foi pour la mesure. Aucune équivalence de version déduite.'),
  dict(path='tmp/tryton-code-audit-2026-10-28/modules/stock_consignment/doc/index.rst',sha256=sha((ROOT/'tmp/tryton-code-audit-2026-10-28/modules/stock_consignment/doc/index.rst').read_bytes()),status='local_pinned_document_consulted',meaning='Lieux et consommation de consignation fournisseur/client, liés aux factures.')]))
 retained=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))['units']
 cumulative=sum(u['total_jh'] for u in retained);covered={c['id'] for u in retained for c in u['capabilities']}
 assert cumulative==1840 and len(covered)==14
 studied=covered|{b['id'] for b in selected}
 progress=dict(retained_gross_jh=cumulative,retained_local_months={u['id']:u['months'] for u in retained},
  total_capabilities=88,retained_capabilities=len(covered),retained_coverage_pct=100*len(covered)/88,
  campaign_capabilities_studied=len(studied),campaign_studied_pct=100*len(studied)/88,
  new_capabilities_framed=2,new_capabilities_estimated=0,new_capabilities_adopted=0,
  ownership_proposed_jh=None,retained_cumulative_not_whole_core_estimate=True,schedules_are_not_added=True,
  source_files=len(rows),witness_methods=len(witnesses),
  progress='Deux nouvelles capacités cadrées, quatre sélections de code révisé, réutilisation et six compléments isolés.',
  uncertain='Taille des invariants de propriété et des compléments de décision/registre ; lectures natives non parfaitement comparables.',
  next_iteration=dict(worthwhile=True,objective='Dimensionner les six modules et la base marginale par analogies de composants, puis compter COSMIC et produire quatre calculs natifs d’opportunité.',
   stop_general_inventory=True,no_external_project_actuals_required=True,no_exhaustive_business_rule_specification_required=True,
   reason='Travail désormais ciblé : les analogues et propriétaires sont identifiés ; la suite produit des tailles et des JH plutôt qu’un nouveau balayage général.'))
 yaml_save('avancement.yaml',progress)
 assert before=={p:sha((ROOT/p).read_bytes()) for p in protected},'Active inputs changed during audit'
 save('verification.json',dict(passed=True,pinned_repositories=4,source_files=len(rows),witness_methods=len(witnesses),
   source_files_verified_against_Git=True,protected_active_inputs_unchanged=before,retained_gross_jh=1840,
   retained_capabilities=14,studied_capabilities=len(studied),ownership_estimate_adopted=False,application_changed=False))
 save('provenance.json',dict(protected_active_inputs=before,outputs={p.name:sha(p.read_bytes()) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='provenance.json'},
  evidence_dependencies={p:sha((ROOT/p).read_bytes()) for p in ['audits/2026-10-30-master-data-comparable-reuse/measurements.json','audits/2026-10-30-stock-opportunite-08/inputs.json','audits/2026-10-30-stock-perimetres-02/build.py','audits/2026-10-30-master-data-natif/measure.py']}))
 print(json.dumps(dict(summary=summary,progress=progress),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
