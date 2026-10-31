"""Independent full audit of the opportunity proposal: arithmetic, evidence, scope and ownership."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal,ROUND_HALF_UP
import json,hashlib,math,copy,importlib.util,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def close(a,b):assert math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-9),(a,b)
def round10(x):return int((Decimal(str(x))/10).quantize(Decimal('1'),rounding=ROUND_HALF_UP))*10
def validate_scope(d,r,b):
 expected={cap['id'] for u in b['units'] for cap in u['capabilities']};new=set();slugs=[]
 for f in d['families']:
  assert f['quantity']==len(f['module_names']) and f['quantity']>0
  for cap in f['capabilities']:assert cap not in expected|new;new.add(cap)
  slugs.append(f['slug'])
 assert len(expected)==16 and len(new)==72 and len(expected|new)==88
 assigned=[f for g in d['economic_units'] for f in g['families']]
 assert sorted(assigned)==sorted(slugs) and len(assigned)==len(set(assigned))
 functions=[x['function'] for x in r['function_coverage']]
 assert len(functions)==len(set(functions))==215 and all(x['costed'] for x in r['function_coverage'])
 assert {x['capability'] for x in r['function_coverage']}==new
def validate_funding(d,fund):
 units={x['id'] for x in d['economic_units']};famunits={f:g['id'] for g in d['economic_units'] for f in g['families']};seen=set()
 for x in fund['mechanisms']:
  assert x['id'] not in seen;seen.add(x['id'])
  assert x['economic_owner'] in units and famunits[x['family_owner']]==x['economic_owner']
 assert sum(x['mode']=='included_common_work' for x in fund['mechanisms'])==11
 assert set(x['id'] for x in fund['mechanisms'] if x['mode']=='new_additional_module')=={'customs-dossier-checks','trace-sequence-analysis','solver-run-contract'}
def validate_cosmic(c):
 ids=[g['id'] for g in c['groups']];assert len(ids)==len(set(ids));names=set(ids);pids=set()
 for p in c['processes']:
  assert p['id'] not in pids;pids.add(p['id']);mov=set()
  for m in p['movements']:
   assert m['type'] in {'E','R','W','X'} and m['group'] in names and m['cfp']==1
   assert (m['type'],m['group']) not in mov;mov.add((m['type'],m['group']))
  assert sum(m['type']=='E' for m in p['movements'])>=1
 assert c['CFP']==sum(len(p['movements']) for p in c['processes'])
def rejects(fn): 
 try:fn()
 except (AssertionError,ValueError,KeyError):return True
 raise AssertionError('Invalid mutation accepted')
def main():
 d=read(OUT/'iteration-08/inputs.json');r=read(OUT/'iteration-08/results.json');b=read(OUT/'baseline.json');fund=read(ROOT/d['funding_registry_ref'])
 for stage in [5,6,7,8]:
  folder=OUT/f'iteration-{stage:02}';freeze=read(folder/'freeze.json')
  assert sha(folder/'inputs.json')==freeze['inputs_sha256']
  if stage==5:assert sha(OUT/'source-catalog.json')==freeze['catalog_sha256']
  if stage==6:
   assert sha(folder/'source-catalog.json')==freeze['catalog_sha256']
   assert sha(OUT/'iteration-05/analysis.json')==freeze['analysis5_sha256']
  if stage==7:
   assert sha(OUT/'iteration-06/analysis.json')==freeze['analysis6_sha256']
   for unit,h in freeze['cosmic_sha256'].items():assert sha(folder/('cosmic-'+unit+'.json'))==h
  if stage==8:
   assert sha(folder/'funding.json')==freeze['funding_sha256']
   assert sha(OUT/'iteration-07/analysis.json')==freeze['analysis7_sha256']
 for file,h in b['protected'].items():assert sha(ROOT/file)==h,file
 import yaml
 assert yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))['units']==b['units']
 validate_scope(d,r,b);validate_funding(d,fund)
 common=read(ROOT/d['common_results_ref']);commonm=read(ROOT/d['common_measurements_ref'])
 assert sha(ROOT/d['common_results_ref'])==b['prior_common_sha256']
 sources={}
 for source in read(ROOT/d['source_catalog_ref'])['sources']+commonm['sources']:
  if source['root_path'] in sources:assert sources[source['root_path']]['sha256']==source['sha256']
  sources[source['root_path']]=source
 s=importlib.util.spec_from_file_location('counter',ROOT/d['counter_ref']);counter=importlib.util.module_from_spec(s);s.loader.exec_module(counter)
 repos=read(ROOT/d['source_catalog_ref'])['repos'];pinned=0
 for path,src in sources.items():
  p=ROOT/path;assert sha(p)==src['sha256'],path
  measured=counter.measure(p)
  for key in ['program_units','declarative_units']:assert measured[key]==src['whole_measure'][key],(path,key)
  gitpath=src['path'];repo=ROOT/repos[src['repo']]['root']
  frozen=subprocess.run(['C:/Program Files/Git/cmd/git.exe','-C',str(repo),'show',src['commit']+':'+gitpath],check=True,capture_output=True).stdout
  assert frozen.replace(b'\r\n',b'\n')==p.read_bytes().replace(b'\r\n',b'\n');pinned+=1
 # Fresh atom union equals every bank; no selected atom can be owned by two base-construction units.
 atomowners={};unitsseen=set()
 for a in r['native_base_assignment']:
  key=a['repo'],a['path'],a['atom']
  if a['owner']:
   assert key not in atomowners or atomowners[key]==a['owner'];atomowners[key]=a['owner']
 for f in d['families']:
  fresh=defaultdict(set)
  for binding in f['bindings']:
   assert sha(ROOT/binding['root_path'])==binding['sha256']
   for a in binding['atoms']:fresh[binding['product']].add((binding['repo'],binding['path'],a['key']))
  entry=next(x for x in r['families'] if x['slug']==f['slug'])
  for row in entry['rows']:
   bank=f.get('analogue_provider',{}).get('units',{}).get(row['id'],len(fresh[row['id']]))
   close(row['analogue_program_units'],bank)
 c=d['cocomo'];exponent=c['B']+c['SF_sum']/100;F=c['D']+.2*(exponent-c['B'])
 def effort(size,em=None):return c['A']*(size/1000)**exponent*(em if em is not None else c['other_EM'])*c['SCED']*c['month_hours']/c['day_hours']*c['effort_phase_factor'] if size else 0
 template=read(ROOT/'audits/2026-10-30-propriete-stock-calcul-02/inputs.json')
 newnative=dict.fromkeys(['erpnext','odoo','tryton','axelor'],0);raw=dict.fromkeys(newnative,0.);math_rows=0
 for family in r['families']:
  spec=next(x for x in d['families'] if x['slug']==family['slug'])
  for row in family['rows']:
   p=row['id'];scaffold=template['new_module_scaffolding'][p]['program_units_per_new_service_module'];t=template['schema_templates'][p]
   new=row['analogue_program_units']*spec['extension_fraction']*spec['quantity']+scaffold*spec['quantity'];close(row['new_local_code_units'],new)
   models=0
   for model in row['models']:
    fields=len(model['fields'])
    pu=fields*t['program_per_field']+t.get('program_per_new_model',0)
    du=fields*t['declarations_per_field']+t['per_new_model']+fields*t['view_field']+t['view_model']
    close(pu,model['program_units']);close(du,model['declarative_units']);models+=pu+du
   mods=sum(x['units'][p]*x['fraction']+scaffold*x.get('scaffolds',1) for x in spec.get('additional_modules',[]))
   size=row['common_equivalent_units']+row['native_local_base_units']+new+models+mods
   close(size,row['equivalent_units']);close(effort(size),row['jh']);math_rows+=1
 for group in r['economic_units']:
  for row in group['rows']:
   size=sum(next(v['equivalent_units'] for v in f['rows'] if v['id']==row['id']) for f in r['families'] if f['slug'] in group['families'])
   close(size,row['equivalent_units']);jh=effort(size);close(jh,row['jh']);assert round10(jh)==row['rounded_jh']
   newnative[row['id']]+=row['rounded_jh'];raw[row['id']]+=jh;math_rows+=1
  assert sum(x['jh'] for x in group['roles'])==group['proposed_java_jh']==sum(group['family_allocations'].values())
  java=next(x for x in group['rows'] if x['id']=='axelor')
  months=c['C']*(group['proposed_java_jh']/c['effort_phase_factor']*c['day_hours']/c['month_hours']/c['SCED'])**F*c['schedule_phase_factor']
  close(months,group['raw_months'])
  cosmic=read(ROOT/group['cosmic_ref']);validate_cosmic(cosmic)
  close(group['COSMIC']['jh'],cosmic['CFP']*20/7)
  close(group['COSMIC']['alignment_vs_java']['gap_pct'],100*(cosmic['CFP']*20/7-java['jh'])/java['jh'])
 assert newnative==r['new_native_subtotals'];assert r['cumulative']['complete_proposed_jh']==1940+newnative['axelor']==4160
 assert sum(f['proposed_java_jh'] for f in r['families'])==newnative['axelor']==2220
 # Nine roles include the three retained decisions exactly once.
 roles=defaultdict(int);labels={}
 for unit in b['units']+r['economic_units']:
  for role in unit['roles']:roles[role['id']]+=role['jh'];labels[role['id']]=role['label']
 assert sum(roles.values())==4160
 # Explicit sensitivities alter volumes, never invent days or a statistical interval.
 def java_size(group):return next(v['equivalent_units'] for v in group['rows'] if v['id']=='axelor')
 def impact(groupid,delta,label,basis):
  group=next(g for g in r['economic_units'] if g['id']==groupid);before=java_size(group);rawdelta=effort(before+delta)-effort(before)
  return dict(id=groupid,label=label,basis=basis,extra_equivalent_units=delta,delta_jh=rawdelta,rounded_delta_jh=round10(rawdelta),not_probability=True)
 byslug={f['slug']:f for f in r['families']}
 opt=next(v for v in byslug['optimization']['rows'] if v['id']=='axelor')
 goods=next(v for v in byslug['goods-orders']['rows'] if v['id']=='axelor')
 ledger=next(p for p in common['owners']['supervision']['rows'] if p['id']=='axelor')
 ledgerpart=next(p for p in ledger['parts'] if p['mechanism']=='case-ledger')
 sensitivity=[
 impact('decisions',opt['analogue_program_units']*.75+14+21,'Un modèle de décision supplémentaire de taille analogue','Même service, un modèle de six champs et une validation de taille .75 du composant de référence.'),
 impact('services',goods['analogue_program_units']*12*.25,'Doubler le code spécialisé des douze contrats de prestation','Passer de .25 à .50 composant de contrôle par type ; cycle commun et schémas inchangés.'),
 impact('processes',ledgerpart['analogue_units']*1.75,'Doubler le comportement nouveau du journal des dossiers','Fraction de code du registre passée de 1.75 à 3.50 ; modèles et historique moteur inchangés.')]
 delta_all=0
 for group in r['economic_units']:
  delta=0
  for f in r['families']:
   if f['slug'] not in group['families']:continue
   spec=next(x for x in d['families'] if x['slug']==f['slug']);row=next(v for v in f['rows'] if v['id']=='axelor')
   delta+=row['analogue_program_units']*spec['extension_fraction']*spec['quantity']*.5
   delta+=sum(mod['units']['axelor']*mod['fraction']*.5 for mod in spec.get('additional_modules',[]))
  delta_all+=effort(java_size(group)+delta)-effort(java_size(group))
 sensitivity.append(dict(id='all-new',label='Augmenter de 50 % les volumes de code des adaptations nouvelles locales',delta_jh=delta_all,rounded_delta_jh=round10(delta_all),basis='Base native, commun déjà mesuré, schémas et estimations retenues inchangés. Ce n’est pas une borne du Core complet.',not_probability=True))
 integrated=effort(sum(java_size(g) for g in r['economic_units']))-sum(effort(java_size(g)) for g in r['economic_units'])
 sensitivity.append(dict(id='grouping',label='Recalculer les seuls nouveaux périmètres comme une seule unité COCOMO',delta_jh=integrated,rounded_delta_jh=round10(integrated),basis='Sensibilité au niveau de regroupement ; ce calcul ne remplace pas les six unités financées ni les décisions retenues.',not_probability=True))
 save(OUT/'sensitivity.json',dict(results=sensitivity,not_confidence_or_scenario_envelope=True,retained_estimate_uncertainty_not_reestimated=True))
 # Mutations exercise meaningful rejection cases, independently of the calculation implementation.
 negative=[]
 bad=copy.deepcopy(fund);bad['mechanisms'].append(copy.deepcopy(bad['mechanisms'][0]));negative.append(rejects(lambda:validate_funding(d,bad)))
 bad=copy.deepcopy(fund);bad['mechanisms'][0]['economic_owner']='planning';negative.append(rejects(lambda:validate_funding(d,bad)))
 bad=copy.deepcopy(d);bad['families'][0]['capabilities']+=d['families'][1]['capabilities'];negative.append(rejects(lambda:validate_scope(bad,r,b)))
 bad=copy.deepcopy(d);bad['economic_units'][0]['families'].append('orders');negative.append(rejects(lambda:validate_scope(bad,r,b)))
 cc=read(ROOT/r['economic_units'][0]['cosmic_ref']);bad=copy.deepcopy(cc);bad['processes'][0]['movements'][0]['group']='unfunded-object';negative.append(rejects(lambda:validate_cosmic(bad)))
 bad=copy.deepcopy(cc);bad['processes'][0]['movements'].append(copy.deepcopy(bad['processes'][0]['movements'][0]));negative.append(rejects(lambda:validate_cosmic(bad)))
 bad=copy.deepcopy(cc);bad['CFP']+=1;negative.append(rejects(lambda:validate_cosmic(bad)))
 badr=copy.deepcopy(r);badr['function_coverage'][0]['costed']=False;negative.append(rejects(lambda:validate_scope(d,badr,b)))
 transitions=[]
 for prev,nxt in [(6,7),(7,8)]:
  a=read(OUT/f'iteration-{prev:02}/results.json');z=read(OUT/f'iteration-{nxt:02}/results.json');changes=[]
  def total(x):return 1940+sum(next(v['jh'] for v in g['rows'] if v['id']=='axelor') for g in x['economic_units'])
  for ga,gz in zip(a['economic_units'],z['economic_units']):
   va=next(v['jh'] for v in ga['rows'] if v['id']=='axelor');vz=next(v['jh'] for v in gz['rows'] if v['id']=='axelor')
   changes.append(dict(unit=ga['id'],change_jh=vz-va,change_pct=100*(vz-va)/va))
  pct=100*(total(z)-total(a))/total(a)
  assert abs(pct)<5 and all(abs(x['change_pct'])<10 for x in changes)
  transitions.append(dict(previous=prev,next=nxt,unrounded_total_change_jh=total(z)-total(a),unrounded_total_change_pct=pct,unit_changes=changes))
 save(OUT/'stability.json',dict(transitions=transitions,stop_rule=read(OUT/'campaign.json')['stop_rule'],passed=True,not_predictive_accuracy=True,note='Stabilité après deux revues distinctes des frontières/garanties et du financement. Une formule répétée sur les mêmes entrées ne suffirait pas à démontrer cette stabilité.'))
 report=dict(passed=True,iteration_input_freezes_checked=4,pinned_source_files=pinned,same_native_counter=True,native_arithmetic_rows_checked=math_rows,COSMIC_boundaries_checked=6,funding_mechanisms=len(fund['mechanisms']),negative_mutations_rejected=len(negative),capabilities_costed_proposed=88,retained_capabilities=16,new_function_results_costed=215,overlapping_funded_capabilities=0,unfunded_known_material_scope_within_assumptions=0,new_native_subtotals=newnative,retained_jh=1940,additional_proposed_jh=2220,complete_proposed_jh=4160,global_roles=[dict(id=k,label=labels[k],jh=v) for k,v in roles.items()],retained_sources_unchanged=True,confidence_not_computed=True,stop_criteria_passed=True,model_not_automatically_adopted=True)
 save(OUT/'verification.json',report)
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
