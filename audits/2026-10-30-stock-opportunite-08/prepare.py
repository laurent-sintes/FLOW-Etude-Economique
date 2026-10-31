"""Freeze Stock opportunity-estimate assumptions before calculating effort.
All allocations and analogy quantities are engineering assumptions, not observed effort.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,math
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tmp/model-deps'),str(ROOT/'tools'),str(ROOT/'tmp/master-data-native-23/parser-deps')]
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def module(name,p):
 s=importlib.util.spec_from_file_location(name,ROOT/p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
scope=module('stock08scope','audits/2026-10-30-stock-perimetres-02/build.py')
counter=module('stock08counter','audits/2026-10-30-master-data-natif/measure.py')
repos=scope.repos
products=['erpnext','odoo','tryton','axelor']

def method_units(repo,path):
 f=ROOT/repos[repo]['root']/path
 raw,methods,_=scope.parse(f)
 if f.suffix=='.java':methods=[m for m in methods if m['name']!=f.stem]
 spans=[(m['start'],m['end']) for m in methods]
 def inside(a,b):return any(s<=a<=b<=e for s,e in spans)
 if f.suffix=='.py':
  result=[dict(kind=type(n).__name__,start=n.lineno,end=n.end_lineno) for n in ast.walk(ast.parse(raw.decode('utf-8-sig')))
   if isinstance(n,ast.stmt) and not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str))
   and inside(n.lineno,n.end_lineno)]
 else:
  tree=scope.JAVA.parse(raw);assert not tree.root_node.has_error
  result=[dict(kind=n.type,start=n.start_point.row+1,end=n.end_point.row+1) for n in counter.walk(tree.root_node)
   if ((n.type.endswith('_statement') and n.type!='empty_statement') or n.type in counter.JAVA_EXTRA)
   and inside(n.start_point.row+1,n.end_point.row+1)]
 return len(result),result

def key(product,path):
 if product!='axelor':return Path(path).name
 if path.startswith('axelor-supplychain/') and path.endswith('.xml'):return 'supplychain/'+Path(path).name
 if '/resources/' in path:return path.split('/resources/')[1]
 return Path(path).name

def prepare():
 OUT.mkdir(exist_ok=True)
 profile=load(str((OUT/'attribution-hypotheses.json').relative_to(ROOT)).replace('\\','/'))
 all_perimeters={p:load(f'audits/2026-10-30-stock-composants-07/{p}-perimetre.json') for p in products}
 decisions=[];scaffolds={};dependencies=set()
 for p,data in all_perimeters.items():
  prior=load(f'audits/2026-10-30-stock-mesures-03/{p}-mesures.json')
  floors={f['path']:(f['program_units'],f['declarative_units']) for f in prior['files']}
  for f in data['files']:
   path=ROOT/repos[f['repo']]['root']/f['path'];assert sha(path)==f['sha256']
   low,central,high=profile[p][key(p,f['path'])]
   assert 0<=low<=central<=high<=1
   pu,du=f['native_program_after_MD'],f['native_declarative_after_MD']
   floor_p,floor_d=floors.get(f['path'],(0,0))
   # Only raw selections already measured in 03 can set a minimum. Shared MD
   # declarations are already removed. No new generic framework assimilation.
   if f['already_funded_MD']['program_units']:
    # Tryton quantity methods were explicitly excluded from prior MD code.
    assert p in ('tryton','odoo')
    if p=='odoo':assert floor_p==0
   floor_d=max(0,floor_d-f['already_funded_MD']['declarative_units'])
   assert floor_p<=pu and floor_d<=du
   bodies,nodes=method_units(f['repo'],f['path']) if path.suffix in ('.py','.java') else (0,[])
   decisions.append(dict(product=p,repo=f['repo'],path=f['path'],sha256=f['sha256'],commit=f['commit'],components=f['components'],
    available_program=pu,available_declarative=du,known_stock_program_floor=floor_p,known_stock_declarative_floor=floor_d,
    attribution=dict(lower=low,central=central,upper=high),
    attribution_status='hypothèse d’ingénierie sur la taille, non mesure d’une proportion réelle ou d’un effort',
    basis=f['scope_notes'],whole_method_program_units=bodies,whole_method_nodes=nodes,
    excludes=f['already_funded_MD'],additional_framework_assimilation=0))
   dependencies.add(str(path.relative_to(ROOT)).replace('\\','/'))
  # Imports + one business service class, or native Java service scaffolding.
  reference=next(f for f in data['files'] if
   (p=='erpnext' and f['path'].endswith('/stock_reservation_entry.py')) or
   (p=='odoo' and f['path'].endswith('/stock_quant.py')) or
   (p=='tryton' and f['path']=='modules/stock/inventory.py') or
   (p=='axelor' and f['path'].endswith('/StockLocationLineFetchServiceImpl.java')))
  path=ROOT/repos[p]['root']/reference['path'];raw=path.read_bytes()
  if path.suffix=='.py':
   tree=ast.parse(raw.decode('utf-8-sig'));n=sum(isinstance(x,(ast.Import,ast.ImportFrom)) for x in tree.body)+1
   note='Imports du module de référence et une classe de service ; métadonnées des modèles comptées séparément.'
  else:
   tree=scope.JAVA.parse(raw)
   n=0
   def visit(node,in_method=False):
    nonlocal n
    if node.type=='method_declaration':return
    if ((node.type.endswith('_statement') and node.type!='empty_statement') or node.type in counter.JAVA_EXTRA):n+=1
    for child in node.named_children:visit(child)
   visit(tree.root_node);note='Structure Java hors méthodes : imports, classe, champs/injection et constructeur.'
  scaffolds[p]=dict(repo=p,path=reference['path'],sha256=reference['sha256'],program_units_per_new_service_module=n,modules=7,note=note)
 # Union of Stock-specific helper bodies not present in the broad component footprint.
 # This avoids silently dropping ERPNext stock/utils.py calls from the native baseline.
 extra={}
 for p in products:
  paths={d['path'] for d in decisions if d['product']==p};fragments={}
  for kind in ['correction','reservation']:
   chain=load(f'audits/2026-10-30-stock-chaines-06/{p}-{kind}.json')
   for f in chain['files']:
    if f['role']=='framework_reused' or f['path'] in paths:continue
    r=fragments.setdefault(f['path'],dict(repo=f['repo'],path=f['path'],sha256=f['sha256'],nodes={}))
    for n in f['counted_nodes']:r['nodes'][(n['kind'],n['start'],n['end'])]=n
    dependencies.add(str((Path(repos[f['repo']]['root'])/f['path'])).replace('\\','/'))
  extra[p]=[dict(repo=f['repo'],path=f['path'],sha256=f['sha256'],program_units=len(f['nodes']),counted_nodes=list(f['nodes'].values()),
    attribution=dict(lower=.6,central=.8,upper=1),reason='Adaptateurs natifs Stock de lecture/création/contexte ; union des chaînes 06, sans framework.') for f in fragments.values()]
 macro_specs=[
  dict(id='STOCK-F01',analogue='correction_chain',lower=.5,central=1,upper=1.5,
    reasoning='Un module nouveau d’admission sémantique/révision des faits, avec soldes externes, filiation et contenu. Hypothèse de taille comparable à une chaîne native complète de correction, après attribution Stock. Les primitives du registre sont appelées, pas réimplémentées ; enveloppe/version génériques déjà financées.'),
  dict(id='STOCK-F02',analogue='positions_component',lower=.25,central=.5,upper=.9,
    reasoning='Extension de composition des provenances, fraîcheur et limites ; les calculs quantitatifs de base sont réutilisés. Hypothèse centrale d’un module moitié aussi volumineux que le comportement de position native attribué.'),
  dict(id='STOCK-F03',analogue='inventory_component',lower=.15,central=.35,upper=.7,
    reasoning='Protocoles, preuve, autorité et rapprochement des mouvements concomitants ; pas nouveau moteur de comptage. Un module compagnon estimé à 35 % du comportement d’inventaire de référence.'),
  dict(id='STOCK-F04',analogue='reservation_chain',lower=.25,central=.5,upper=1,
    reasoning='Identité/version de commande, premier conflit, consommation/libération et expiration. Disponibilité, mutation et transactions sont réutilisées ; module de commande estimé moitié d’une chaîne native de réservation.'),
  dict(id='STOCK-F05',analogue='positions_component',lower=.1,central=.25,upper=.5,
    reasoning='Extraction typée des faits Finance et suivi du résultat, via publication/journal communs. Module estimé au quart du comportement de restitution native ; pas comptabilité ni valorisation.'),
  dict(id='STOCK-F06',analogue='inventory_component',lower=.1,central=.2,upper=.4,
    reasoning='Constat produit, contexte, preuve et correction, via admission/publication communes. Module estimé au cinquième du comportement d’inventaire natif ; aucun PLM ou workflow de résolution.'),
  dict(id='STOCK-F07',analogue='correction_chain',lower=.1,central=.25,upper=.5,
    reasoning='Nouveaux rapprochements Stock faits/engagements/sorties et branchement au coordinateur de reprise existant. Module estimé au quart de la chaîne de correction ; aucun backup, moteur de batch ou provision QA additionnels.')
 ]
 previous=load('audits/2026-10-30-stock-dimensionnement-05/inputs.json')
 templates=previous['native_schema_templates']
 # Count class/meta declarations in program for Python, preserving native syntax.
 templates['odoo']['program_per_new_model']=templates['odoo'].pop('per_new_model');templates['odoo']['per_new_model']=0
 templates['tryton']['program_per_new_model']=templates['tryton'].pop('per_new_model');templates['tryton']['per_new_model']=0
 schemas=[]
 mapped=[]
 for s in previous['schemas']:
  s=dict(s,fields=list(s['fields']))
  for field in list(s['fields']):
   if (s['name'],field) in [('StockFactExtension','eventAt'),('StockCommitmentExtension','originalQuantity')]:
    s['fields'].remove(field)
    mapped.append(dict(model=s['name'],field=field,policy='exposé depuis la date/quantité native déjà comptée ; raccordement inclus dans le module Flow, pas nouveau champ persistant'))
  schemas.append(s)
 c=load('audits/2026-10-30-master-data-spring-flow/inputs.json')['cocomo']
 inputs=dict(id='stock-opportunite-08',date='2026-10-30',status='hypothèses gelées avant calcul des efforts',
  method='COCOMO II, conventions nominales déjà utilisées pour Master Data ; tailles approximatives estimées à partir des composants natifs.',
  model_variant='Équations COCOMO II.2000 utilisées dans le moteur existant ; aucun changement silencieux de coefficients vers Early Design.',
  canonical_rules_ref='source/fondamentaux.yaml#estimation_model',
  cocomo=c,attributions=decisions,stock_dependency_fragments=extra,new_module_scaffolding=scaffolds,
  complement_module_analogies=macro_specs,schemas=schemas,mapped_native_fields=mapped,schema_templates=templates,
  configuration_units=dict(version_mappings=8,stock_indexes=8,model_registrations=sum(s['new_model'] for s in schemas),service_bindings=7),
  functional_contract_ref='audits/2026-10-30-stock-completion-04/cosmic.json',
  scope_ref='audits/2026-10-30-stock-composants-07/components.json',
  complement_boundaries_ref='audits/2026-10-30-stock-composants-07/complements.json',
  native_references=products,
  size_meaning='Proxy logique d’instructions/déclarations, même convention que Master Data. Pondérations de pertinence et tailles nouvelles supposées ; pas SLOC certifiées ni charges historiques.',
  macro_policy='Estimation de modules nouveaux de comportement seulement. Champs/modèles/vues et structure de service comptés séparément ; pas multiplication des 66 petits traitements par une méthode type.',
  reuse_policy='Services et référentiels Master Data déjà financés. Un seul propriétaire ; appels/adaptations Stock dans le dimensionnement nouveau. Aucun second AAM sur l’intégralité du framework.',
  assumptions=[
   dict(id='H1',text='Les 62 fichiers et les compléments définissent une base d’opportunité suffisante ; extensions installables et cas rares non exhaustifs. Les parties mixtes sont attribuées par jugement d’ingénierie, avec minimum déjà mesuré et sensibilité.'),
   dict(id='H2',text='Les nouveaux modules Flow sont de taille comparable aux fractions explicites des composants/chaînes natives. Ces fractions ne sont ni des normes de marché ni des observations d’effort.'),
   dict(id='H3',text='Master Data et ses services génériques sont disponibles et utilisables ; leur coût retenu est conservé, seuls les travaux spécifiques Stock sont ajoutés.'),
   dict(id='H4',text='Un module Stock, une base transactionnelle, architecture standard réutilisant les services Master Data. Pas de réservation distribuée entre bases ; aucun engagement de débit, latence ou RPO/RTO spécifique.'),
   dict(id='H5',text='Équipe nominale maîtrisant son écosystème, PERS=PREX=1 ; conventions 152 h/mois-personne, 7 h/JH, phases 1,18 et délai 1,25. Les essais de sensibilité ne sont pas des probabilités.'),
   dict(id='H6',text='Base commune : mouvements/registre, positions connues, comptages et quantités engagées. Compléments : admission externe, révisions/double date, autorité, filiation/contenu, protocoles, reprise, et contributions typées. Pas intégration Groupe, GL, PLM, promesse ou optimisation.'),
   dict(id='H7',text='Les quatre chiffres sont des charges modélisées du périmètre cible dans chaque écosystème natif, après patrimoine Master Data. Pas coût historique des produits, ni mesure de code Flow existant.'),
   dict(id='H8',text='La projection Java/Spring peut utiliser Axelor comme référence sous l’équivalence de framework déjà posée ; cette équivalence n’est pas une calibration empirique. Les quatre alternatives ne sont pas additionnées.')
  ],
  arithmetic_policy='Addition de tailles avant COCOMO ; compléments valorisés par différence du total et de la base, pas somme de coûts autonomes.',
  author='Codex, analyse assistée par IA',human_review=None,observed_project_effort=None,
  metamodel_change=False,retained_decision_change=False)
 write('inputs.json',inputs)
 write('input-freeze.json',dict(input_sha256=sha(OUT/'inputs.json'),contains_effort_results=False,
  statement='Valeurs de pertinence et analogies fixées avant le premier calcul d’effort ; aucune cible de JH utilisée pour les choisir.'))
 deps=set(['source/fondamentaux.yaml','source/schema-fondamentaux.yaml','source/estimations-core-retenues.yaml',
  'source/referentiel-capacites.yaml','sources/cartographie-scm-2026-10-24.yaml','source/calculs-estimation-core.yaml',
  'audits/2026-10-30-stock-perimetres-02/build.py','audits/2026-10-30-master-data-natif/measure.py',
  'audits/2026-10-30-master-data-comparable-reuse/measurements.json','audits/2026-10-30-master-data-spring-flow/inputs.json',
  'audits/2026-10-30-stock-dimensionnement-05/inputs.json','audits/2026-10-30-stock-completion-04/cosmic.json',
  'audits/2026-10-30-stock-composants-07/components.json','audits/2026-10-30-stock-composants-07/complements.json',
  'audits/2026-10-30-master-data-calcul/repartitions-sources.json','audits/2026-10-30-master-data-consolidation/inputs.json',
  'tools/estimation_calculation.py','tools/model_context.py'])
 for p in products:
  deps.add(f'audits/2026-10-30-stock-composants-07/{p}-perimetre.json')
  deps.add(f'audits/2026-10-30-stock-mesures-03/{p}-mesures.json')
  for kind in ['correction','reservation']:deps.add(f'audits/2026-10-30-stock-chaines-06/{p}-{kind}.json')
 deps.update(dependencies)
 for p in [Path(__file__).resolve(),OUT/'inputs.json',OUT/'attribution-hypotheses.json',OUT/'input-freeze.json']:
  deps.add(str(p.relative_to(ROOT)).replace('\\','/'))
 protected=[p for p in deps if p.startswith('source/') or p.startswith('sources/')]
 write('provenance.json',dict(protected={p:sha(ROOT/p) for p in protected},dependencies=[dict(path=p,sha256=sha(ROOT/p)) for p in sorted(deps)]))
 print(json.dumps(dict(files=len(decisions),schema_fields=sum(len(s['fields']) for s in schemas),mapped_fields=mapped,
  macro_hypotheses=len(macro_specs),scaffolds=scaffolds,input_sha256=sha(OUT/'inputs.json'),effort_calculated=False),ensure_ascii=False,indent=2))
if __name__=='__main__':prepare()
