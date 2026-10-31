"""Iteration 2: explicit conditional sizing and proposed COSMIC counts, separate from adoption."""
from pathlib import Path
from collections import Counter
import hashlib,importlib.util,json,math,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
from model_context import model_session
from estimation_calculation import formula,rounded
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sp=importlib.util.spec_from_file_location('iteration1_support',OUT/'iteration1.py');support=importlib.util.module_from_spec(sp);sp.loader.exec_module(support)
def source(ref,plan):
 repo=plan['repos'][ref['repo']];p=ROOT/repo['root']/ref['path'];resolved=False
 if not p.is_file():
  candidates=list((ROOT/repo['root']).rglob(Path(ref['path']).name))
  if len(candidates)!=1:return dict(**ref,missing=True)
  p=candidates[0];ref=dict(ref,path=p.relative_to(ROOT/repo['root']).as_posix());resolved=True
 raw=p.read_bytes();pin=subprocess.run(['C:/Program Files/Git/cmd/git.exe','-C',str(ROOT/repo['root']),'show',repo['commit']+':'+ref['path']],capture_output=True,check=True).stdout
 assert raw.replace(b'\r\n',b'\n')==pin.replace(b'\r\n',b'\n')
 return dict(**ref,root_path=p.relative_to(ROOT).as_posix(),sha256=sha(p),commit=repo['commit'],pinned_blob_verified=True,
  path_resolved_by_unique_filename=resolved,whole_file=support.m.measure(p),methods=support.symbols(p))
def main():
 plan=read(OUT/'plan.json');functional={r[0]:r for r in read(OUT/'functional-hypotheses.json')}
 native=read(ROOT/'audits/2026-10-30-propriete-stock-calcul-02/inputs.json');c=native['cocomo']
 summary=[]
 for f in plan['families']:
  folder=OUT/f['slug'];one=read(folder/'iteration-1.json');analysis=read(folder/'analyse-1.json')
  sources=list(one['sources']);keys={(s['repo'],s['path']) for s in sources}
  for value in analysis['additional_sources']:
   repo,path=value.split(':',1)
   if (repo,path) not in keys:sources.append(source(dict(repo=repo,path=path),plan))
  _,models,requests=functional[f['slug']];schema=[]
  for definition in models:
   name,attrs=definition.split(':',1);schema.append(dict(name=name,fields=attrs.split(','),hypothesis='Structure proposée du module ; ne constitue pas une spécification approuvée.'))
  if f['slug']=='goods-orders':
   # A common lifecycle is consumed from Orders, while twelve typed contracts are new.
   for cap in f['native_capabilities']:
    schema.append(dict(name=cap['native_id']+'-contract',fields=['serviceOrderRef','goodsRef','quantity','unitRef','requirementsRef','acceptedVersion','resultContractRef'],hypothesis=cap['source']['definition']))
  processes=[];groups={};moves=Counter()
  for i,(label,grammar) in enumerate(requests,1):
   pid=f['slug']+'-P'+str(i).zfill(2);movements=[]
   for clause in grammar.split(';'):
    kind,*names=clause.strip().split()
    for name in names:
     groups.setdefault(name,dict(id=name,object_of_interest=name,attributes=next((s['fields'] for s in schema if s['name']==name),['reference','scope','businessAttributes'])))
     movements.append(dict(id=pid+'-'+kind+'-'+name,type=kind,group=name,cfp=1));moves[kind]+=1
   processes.append(dict(id=pid,label=label,trigger='Réception de la demande ou du fait métier nommé dans le processus.',functional_user='Capacité consommatrice, producteur autorisé ou opérateur extérieur au composant.',capabilities=f['capabilities'],movements=movements))
  cfp=sum(moves.values())
  cf=dict(groups=list(groups.values()),processes=processes,CFP=cfp,movements=dict(moves),
   boundary='Composant logique de la famille ; lectures de données métier explicites et résultats fournis. Ne pas additionner les CFP entre familles sans réconcilier les interfaces.',
   variant_rule='Un type d’ordre ou d’acte ne crée pas à lui seul un second processus identique ; les contrats typés restent à qualifier.',
   certified=False,human_review=False,completeness='Comptage d’opportunité proposé sur ces processus, pas preuve d’exhaustivité des exigences.',hours_per_CFP=20,factor=1,day_hours=7)
  pattern=analysis['method_pattern'];selected=[];banks={p:0 for p in ['erpnext','odoo','tryton','axelor']}
  for s in sources:
   if s.get('missing'):continue
   product='erpnext' if s['repo']=='frappe' else 'axelor' if s['repo']=='platform' else s['repo']
   seen=set()
   for m in s['methods']:
    if not re.search(pattern,m['name'],re.I):continue
    if any(word in m['name'].lower() for word in ['__register__','default_','get_rec_name','search_rec_name']):continue
    nodes={(n['kind'],n['start'],n['end'],n['col'],n['end_col']) for n in m['nodes']}
    fresh=nodes-seen;seen|=nodes
    selected.append(dict(repo=s['repo'],product=product,path=s['path'],sha256=s['sha256'],name=m['name'],start=m['start'],end=m['end'],
     program_units=len(fresh),nodes=[list(n) for n in sorted(fresh)],source=m['source']))
   banks[product]+=len(seen)
  inputs=dict(family=f['id'],iteration=2,analysis_ref='analyse-1.json',capabilities=f['capabilities'],cocomo=c,
   native_reference_banks=banks,source_selection=selected,source_files=[{k:v for k,v in s.items() if k!='methods'} for s in sources],
   attribution=f['attribution'],attribution_basis='Part d’analogie retenue après exclusion supposée des responsabilités natives hors périmètre ; pas proportion observée. '+analysis['observation'],
   new_complement_fraction=f['complement_fraction'],new_complement_basis=analysis['next_iteration_objective'],
   schemas=schema,template_source='audits/2026-10-30-propriete-stock-calcul-02/inputs.json#schema_templates',
   scaffold_source='audits/2026-10-30-propriete-stock-calcul-02/inputs.json#new_module_scaffolding',
   reuse='Services génériques Master Data, Stock et Propriété du stock déjà financés ; autres mécanismes communs de la campagne à réconcilier. Le code natif sert de règle de taille, ce n’est pas une facture historique.',
   no_extra_AI=True,no_generic_rebuild=True,logical_code_not_calibrated_to_physical_SLOC=True)
  save(folder/'entrees-2.json',inputs);save(folder/'cosmic-2.json',cf)
  save(folder/'gel-2.json',dict(inputs_sha256=sha(folder/'entrees-2.json'),cosmic_sha256=sha(folder/'cosmic-2.json'),policy='Hypothèses et comptage écrits avant le premier calcul de cette famille. Aucune convergence cible.'))
  rows=[]
  E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum'])
  for product,bank in banks.items():
   if bank==0:rows.append(dict(id=product,jh=None,reason='Aucune chaîne métier sélectionnée dans le portefeuille.'));continue
   t=native['schema_templates'][product];scaffold=native['new_module_scaffolding'][product]['program_units_per_new_service_module']
   core=bank*f['attribution'];specific=bank*f['complement_fraction']+scaffold
   pu=sum(len(s['fields'])*t['program_per_field']+t.get('program_per_new_model',0) for s in schema)
   du=sum(len(s['fields'])*t['declarations_per_field']+t['per_new_model']+len(s['fields'])*t['view_field']+t['view_model'] for s in schema)
   size=core+specific+pu+du
   def effort(n):return formula('cocomo_effort',A=c['A'],KSLOC=n/1000,E=E,EM=c['other_EM'],SCED=c['SCED'],month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor'])
   jh=effort(size);base=effort(core)
   rows.append(dict(id=product,native_analogue_units=bank,core_behavior_units=core,new_specific_behavior_units=specific,models_program_units=pu,models_declarative_units=du,equivalent_units=size,common_analogy_jh=base,complement_marginal_jh=jh-base,jh=jh,rounded_jh=rounded(jh,10)))
  result=dict(family=f['id'],iteration=2,status='calculs_conditionnels_sur_portefeuilles_partiels',rows=rows,
   functional=dict(CFP=cfp,jh=formula('cosmic_effort',CFP=cfp,hours_per_CFP=20,factor=1,day_hours=7)),
   no_adoption=True,not_a_full_native_cost=True,adopted_cumulative_jh=1940,
   audit_required='Étape 3 : revue ciblée d’une chaîne et de la frontière. Réconciliation des mécanismes entre familles avant cumul global.',
   input_sha256=sha(folder/'entrees-2.json'),CFP_sha256=sha(folder/'cosmic-2.json'))
  save(folder/'iteration-2.json',result)
  summary.append(dict(family=f['slug'],caps=len(f['capabilities']),native={r['id']:r.get('rounded_jh') for r in rows},CFP=cfp,control_jh=result['functional']['jh']))
 save(OUT/'synthese-iteration-2.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':
 with model_session():main()
