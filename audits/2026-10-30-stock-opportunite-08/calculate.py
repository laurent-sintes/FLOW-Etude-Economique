"""Reproduce four conditional native Stock estimates using canonical COCOMO rules."""
from pathlib import Path
from collections import defaultdict
import ast,hashlib,importlib.util,json,sys,math,copy
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tmp/model-deps'),str(ROOT/'tools')]
from estimation_calculation import formula,rounded,alignment
from model_context import model_session
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inputs=load(str((OUT/'inputs.json').relative_to(ROOT)).replace('\\','/'))
frozen=load(str((OUT/'input-freeze.json').relative_to(ROOT)).replace('\\','/'))
assert sha(OUT/'inputs.json')==frozen['input_sha256'],'Frozen assumptions changed'
repos=load('audits/2026-10-30-master-data-comparable-reuse/measurements.json')['repos']
products=inputs['native_references']
prior={p:load(f'audits/2026-10-30-stock-mesures-03/{p}-mesures.json') for p in products}
known={p:{f['path']:{(n['kind'],n['start'],n['end']) for n in f['counted_nodes']} for f in prior[p]['files']} for p in products}
chains={(p,k):load(f'audits/2026-10-30-stock-chaines-06/{p}-{k}.json') for p in products for k in ['correction','reservation']}
def nk(n):return (n['kind'],n['start'],n['end'])
def md_nodes(d):
 if not d['excludes'].get('program_units'):return set()
 path=ROOT/repos[d['repo']]['root']/d['path'];text=path.read_text(encoding='utf-8-sig')
 excluded={(e['kind'],e['name'],e['line']) for e in d['excludes']['excluded_from_MD'] if e.get('line') is not None}
 lines=text.splitlines();inside=False
 for i,line in enumerate(lines):
  if '# begin: auto-generated types' in line:inside=True
  if inside:lines[i]=''
  if '# end: auto-generated types' in line:inside=False
 result=set()
 def walk(n):
  if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and ('method',n.name,n.lineno) in excluded:return
  if isinstance(n,ast.ClassDef) and ('class',n.name,n.lineno) in excluded:return
  if isinstance(n,(ast.Assign,ast.AnnAssign)):
   targets=n.targets if isinstance(n,ast.Assign) else [n.target]
   name=','.join(t.id for t in targets if isinstance(t,ast.Name))
   if ('field',name,n.lineno) in excluded:return
  if isinstance(n,ast.stmt) and not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str)):
   result.add((type(n).__name__,n.lineno,n.end_lineno))
  for child in ast.iter_child_nodes(n):walk(child)
 walk(ast.parse('\n'.join(lines)));assert len(result)==d['excludes']['program_units']
 return result
md_maps={(d['product'],d['path']):md_nodes(d) for d in inputs['attributions']}
def bank_for(p,level):
 index={d['path']:d for d in inputs['attributions'] if d['product']==p}
 extra={d['path']:d for d in inputs['stock_dependency_fragments'][p]}
 bank={}
 for label,kind in [('correction_chain','correction'),('reservation_chain','reservation')]:
  slices=[]
  for f in chains[(p,kind)]['files']:
   if f['role']=='framework_reused':continue
   d=index.get(f['path']) or extra[f['path']]
   nodes={nk(n) for n in f['counted_nodes']}
   # Constructors belong to service scaffolding, not the new behavioral module.
   if f['path'].endswith('.java'):
    constructors=[m for m in f['methods'] if m['name']==Path(f['path']).stem]
    nodes={n for n in nodes if not any(m['start']<=n[1]<=n[2]<=m['end'] for m in constructors)}
   nodes-=md_maps.get((p,f['path']),set())
   direct=nodes & known[p].get(f['path'],set())
   weight=d['attribution'][level];size=max(len(direct),weight*len(nodes))
   slices.append(dict(path=f['path'],source_sha256=f['sha256'],raw_behavior_units=len(nodes),
    direct_stock_floor=len(direct),attribution=weight,equivalent_program_units=size))
  bank[label]=dict(program_units=sum(s['equivalent_program_units'] for s in slices),source_slices=slices,
   meaning='Taille estimée de comportement Stock dans une chaîne native complète ; utilisée comme analogue d’un nouveau module, pas comme seconde implémentation du noyau.')
 for label,component in [('positions_component','K2'),('inventory_component','K3')]:
  slices=[]
  for d in index.values():
   if component not in d['components'] or not d['whole_method_nodes']:continue
   nodes={nk(n) for n in d['whole_method_nodes']}-md_maps[(p,d['path'])]
   direct=nodes & known[p].get(d['path'],set());weight=d['attribution'][level]
   size=max(len(direct),weight*len(nodes))
   slices.append(dict(path=d['path'],source_sha256=d['sha256'],raw_behavior_units=len(nodes),direct_stock_floor=len(direct),
    attribution=weight,equivalent_program_units=size))
  bank[label]=dict(program_units=sum(s['equivalent_program_units'] for s in slices),source_slices=slices,
   meaning='Méthodes du composant natif cohérent, sans schémas/imports/constructeurs ; recouvrements du socle MD retirés. Les composants se partagent du code, ils ne sont pas additionnés comme projets autonomes.')
 return bank

def sizes(p,attribution='central',modules='central',override=None):
 override=override or {};core=[];bank=bank_for(p,attribution)
 for d in inputs['attributions']:
  if d['product']!=p:continue
  w=d['attribution'][attribution]
  pu=max(d['known_stock_program_floor'],d['available_program']*w)
  du=max(d['known_stock_declarative_floor'],d['available_declarative']*w)
  core.append(dict(path=d['path'],program_units=pu,declarative_units=du,attribution=w,
    known_stock_program_floor=d['known_stock_program_floor'],known_stock_declarative_floor=d['known_stock_declarative_floor'],
    after_exact_MD_deduction=True))
 for d in inputs['stock_dependency_fragments'][p]:
  core.append(dict(path=d['path'],program_units=d['program_units']*d['attribution'][attribution],
    declarative_units=0,attribution=d['attribution'][attribution],source='union des dépendances métier des chaînes'))
 blocks=[]
 template=inputs['schema_templates'][p]
 for spec in inputs['complement_module_analogies']:
  pid=spec['id'];q=override.get(pid,spec[modules]);a=bank[spec['analogue']]
  program=a['program_units']*q;declarative=0;models=[]
  for schema in inputs['schemas']:
   if schema['package']!=pid:continue
   fields=len(schema['fields']);new=int(schema['new_model']);view=int(schema['view'])
   pu=fields*template['program_per_field']+new*template.get('program_per_new_model',0)
   du=fields*template['declarations_per_field']+new*template['per_new_model']+view*(fields*template['view_field']+template['view_model'])
   program+=pu;declarative+=du
   models.append(dict(name=schema['name'],fields=schema['fields'],program_units=pu,declarative_units=du))
  scaffold=inputs['new_module_scaffolding'][p]['program_units_per_new_service_module']
  program+=scaffold
  blocks.append(dict(id=pid,analogue=spec['analogue'],reference_behavior_units=a['program_units'],
    assumed_new_module_fraction=q,new_behavior_program_units=a['program_units']*q,
    service_scaffold_program_units=scaffold,models=models,program_units=program,declarative_units=declarative,
    assumed_not_measured=True,reason=spec['reasoning']))
 # Explicit declarations for registration, mappings, indexes and bindings, once for Stock.
 config=sum(inputs['configuration_units'].values())
 return dict(core=core,analogue_bank=bank,complements=blocks,configuration_declarative_units=config,
  core_program=sum(r['program_units'] for r in core),core_declarative=sum(r['declarative_units'] for r in core),
  complements_program=sum(r['program_units'] for r in blocks),
  complements_declarative=sum(r['declarative_units'] for r in blocks)+config)

def calculate(p,attribution='central',modules='central',override=None,w=1,pers=1,prex=1):
 s=sizes(p,attribution,modules,override);c=inputs['cocomo']
 E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum'])
 F=formula('schedule_exponent',D=c['D'],E=E,B=c['B'])
 base_size=formula('equivalent_size',new_program=s['core_program'],new_declarative=s['core_declarative'],
  w=w,AAM=0,reused_program=0,reused_declarative=0)
 extra_size=formula('equivalent_size',new_program=s['complements_program'],new_declarative=s['complements_declarative'],
  w=w,AAM=0,reused_program=0,reused_declarative=0)
 def effort(n):return formula('cocomo_effort',A=c['A'],KSLOC=n/1000,E=E,EM=c['other_EM']*pers*prex,
  SCED=c['SCED'],month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor'])
 base=effort(base_size);total=effort(base_size+extra_size);extra=total-base
 months=formula('cocomo_schedule',C=c['C'],JH=total,effort_phase_factor=c['effort_phase_factor'],
  day_hours=c['day_hours'],month_hours=c['month_hours'],SCED=c['SCED'],F=F,schedule_phase_factor=c['schedule_phase_factor'])
 rows=[]
 for block in s['complements']:
  n=block['program_units']+w*block['declarative_units']
  rows.append(dict(id=block['id'],equivalent_units=n,
    allocated_marginal_jh=extra*n/extra_size,
    allocation_meaning='Répartition descriptive du supplément COCOMO proportionnelle à la taille ; pas sept calculs indépendants.'))
 rows.append(dict(id='configurations-stock',equivalent_units=w*s['configuration_declarative_units'],
  allocated_marginal_jh=extra*w*s['configuration_declarative_units']/extra_size))
 assert math.isclose(sum(x['allocated_marginal_jh'] for x in rows),extra)
 return dict(id=p,base_common_jh=base,Flow_complements_marginal_jh=extra,total_stock_jh=total,local_schedule_months=months,
  base_equivalent_units=base_size,Flow_complements_equivalent_units=extra_size,total_equivalent_KSLOC=(base_size+extra_size)/1000,
  E=E,F=F,EM=c['other_EM']*pers*prex,declarative_weight=w,detail=s,complement_allocation=rows)

def main():
 with model_session():
  rows=[calculate(p) for p in products]
  functional=load('audits/2026-10-30-stock-completion-04/cosmic.json')['result']
  cfp=formula('cosmic_effort',CFP=functional['CFP'],hours_per_CFP=functional['hours_per_CFP'],
    factor=functional['factor'],day_hours=functional['day_hours'])
  activity=load('audits/2026-10-30-master-data-calcul/repartitions-sources.json')['cocomo']
  for r in rows:
   p=r['id'];total=r['total_stock_jh'];base=r['base_common_jh']
   rb=rounded(base,10);rt=rounded(total,10)
   r['display']=dict(base_common_jh=rb,Flow_complements_jh=rt-rb,total_stock_jh=rt,rounding_step_jh=10,
     local_schedule_months=round(r['local_schedule_months'],1))
   r['activities']=[]
   phases=activity['phase_effort_percent_of_base']
   for a in activity['activities']:
    share=sum(x*y for x,y in zip(phases,a['percent_by_phase']))/100/sum(phases)
    r['activities'].append(dict(id=a['id'],label=a['label'],jh=total*share,published_percent_by_phase=a['percent_by_phase'],
     source=activity['source'],table=activity['table'],printed_pages=activity['printed_pages']))
   assert math.isclose(sum(a['jh'] for a in r['activities']),total)
   r['hypothesis_impacts']=[]
   cases=[
    ('attribution-du-code-mixte',dict(attribution='lower'),dict(attribution='upper'),
      'Attribution source sur base et analogues dépendants, avec plancher des instructions Stock déjà mesurées.'),
    ('volume-des-sept-modules-Flow',dict(modules='lower'),dict(modules='upper'),
      'Quantité de comportement nouveau par rapport aux analogues ; champs/structure maintenus. Variations conjointes explicites, pas intervalle probabiliste.'),
    ('F01-admission-et-revisions',dict(override={'STOCK-F01':.5}),dict(override={'STOCK-F01':1.5}),
      'Un demi-module à un module et demi de correction de référence, au lieu d’un module central.'),
    ('F04-commandes-et-expiration',dict(override={'STOCK-F04':.25}),dict(override={'STOCK-F04':1}),
      'Un quart à une chaîne de réservation de référence, au lieu d’une moitié.'),
    ('F07-rapprochement-apres-reprise',dict(override={'STOCK-F07':.1}),dict(override={'STOCK-F07':.5}),
      'Taille du nouveau module de rapprochement ; ne promet aucun RPO/RTO.'),
    ('capacite-equipe-PERS',dict(pers=.83),dict(pers=1.26),
      'Valeurs de sensibilité reprises des hypothèses COCOMO Master Data, équipe nominale au centre.'),
    ('experience-ecosysteme-PREX',dict(prex=.87),dict(prex=1.12),
      'Valeurs de sensibilité reprises de Master Data ; maîtrise de l’écosystème nominale au centre.'),
    ('poids-declaratif',dict(w=.5),dict(w=2),
      'Convention du proxy XML/JSON/vues, pas multiplicateur direct de productivité.')
   ]
   for hid,lower,upper,note in cases:
    lo=calculate(p,**lower)['total_stock_jh'];hi=calculate(p,**upper)['total_stock_jh']
    r['hypothesis_impacts'].append(dict(id=hid,lower_total_jh=lo,upper_total_jh=hi,
      lower_change_jh=lo-total,upper_change_jh=hi-total,
      lower_change_pct=100*(lo-total)/total,upper_change_pct=100*(hi-total)/total,
      direction='Une seule famille d’hypothèses modifiée à la fois ; impacts non additionnables.',
      note=note))
   r['COSMIC_ISBSG_control']=dict(CFP=functional['CFP'],hours_per_CFP=functional['hours_per_CFP'],factor=functional['factor'],
      jh=cfp,descriptive_alignment=alignment(cfp,total),
      interpretation='Comparaison indicative du même contrat fonctionnel et des activités projet. Le repère de productivité non calibré ne prouve pas la justesse de COCOMO ; la sévérité des garanties et la composition des projets ne sont pas appariées empiriquement.')
  anchor=next(r for r in rows if r['id']=='axelor')
  for r in rows:r['alignment_vs_java_reference']=alignment(r['total_stock_jh'],anchor['total_stock_jh'])
  spread=formula('spread',maximum=max(r['total_stock_jh'] for r in rows),minimum=min(r['total_stock_jh'] for r in rows))
  spread_pct=formula('spread_pct',maximum=max(r['total_stock_jh'] for r in rows),minimum=min(r['total_stock_jh'] for r in rows),reference=anchor['total_stock_jh'])
  result=dict(id='stock-opportunite-08',status='quatre_estimations_conditionnelles_non_adoptees',
    input_sha256=frozen['input_sha256'],rows=rows,
    reference_dispersion=dict(jh=spread,pct=spread_pct,denominator='Axelor total Stock non arrondi',reference=anchor['total_stock_jh'],
      meaning='Dispersion des quatre modèles, pas un intervalle de confiance. Hypothèses de périmètre, ratios de compléments, paramètres COCOMO et conventions sont communs.'),
    cumulative=dict(retained_gross_jh=1500,retained_master_data_months=17,stock_adopted_jh=None,
      candidate_java_reference='axelor',candidate_stock_jh=anchor['display']['total_stock_jh'],
      candidate_java_master_data_plus_stock_jh=1500+anchor['display']['total_stock_jh'],
      meaning='Projection candidate Java/Spring sous équivalence des frameworks et référence Axelor. Pas adoption, pas cumul des quatre alternatives, pas COCOMO intégré de tout Flow.',
      schedules_are_not_added=True),
    method_status=dict(size_estimation='hypothèses de pertinence et analogies de modules, acceptées pour étude amont',
      observed_project_effort=None,human_review=None,confidence_probability=None,
      conditional_estimation_available=True,uncertainty_narrowing_measured=False,parameters_fitted_to_COSMIC=False))
  write('results.json',result)
  print(json.dumps(dict(rows=[dict(id=r['id'],**r['display'],base_units=r['base_equivalent_units'],extra_units=r['Flow_complements_equivalent_units'],
    impacts=[dict(id=x['id'],minus=x['lower_change_jh'],plus=x['upper_change_jh']) for x in r['hypothesis_impacts']]) for r in rows],
    cumulative=result['cumulative'],spread=result['reference_dispersion']),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
