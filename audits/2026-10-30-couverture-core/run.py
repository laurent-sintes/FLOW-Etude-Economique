"""Opportunity-estimate iterations16–20. Audit only; no source/config/app mutations."""
from pathlib import Path
import sys,json,math,hashlib,subprocess,os,copy,html
ROOT=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent
OLD=ROOT/'audits/2026-10-29-experimentation-estimation'
sys.path.insert(0,str(ROOT/'tmp/model-deps'))
import yaml
from witnesses import run_witnesses
sys.stdout.reconfigure(encoding='utf-8')
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,data):(A/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main(it):
 inp=load(A/f'iteration-{it}-entrees.json');checks=[]
 def check(ok,s):
  if not ok:raise AssertionError(s)
  checks.append(s)
 prev=load(OLD/'iteration-15-resultats.json') if it==16 else load(A/f'iteration-{it-1}-resultats.json')
 old14=load(OLD/'iteration-14-resultats.json');roles=list(old14['roles'])
 allcaps=load(OLD/'iteration-07-resultats.json')['coverage'];bybc={c['block']:c for c in allcaps}
 native={}
 for letter in 'abc':
  for c in load(OLD/f'iteration-06-perimetre-{letter}.json')['capabilities']:native[c['id']]=c
 grid=yaml.safe_load((ROOT/'source/grille-complexite.yaml').read_text(encoding='utf-8'))
 check(len(grid['blocs'])==88,'Native universe88')
 gridmap={b['id']:b for b in grid['blocs']}
 bas=load(A/'baseline.json')
 for p,h in bas['active_files'].items():check(sha(ROOT/p)==h,'Active file preserved '+p)
 env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
 proofs=[]
 for eid,repo,path,ranges,obs,limit in inp['proofs']:
  repo_root,repository,commit=inp['repositories'][repo]
  head=subprocess.check_output(['git','-C',str(ROOT/repo_root),'rev-parse','HEAD'],text=True,env=env).strip()
  check(head==commit,'Frozen repository '+eid)
  p=ROOT/repo_root/path;committed=subprocess.check_output(['git','-C',str(ROOT/repo_root),'show',commit+':'+path],env=env)
  check(p.read_bytes().replace(b'\r\n',b'\n')==committed.replace(b'\r\n',b'\n'),'Committed source '+eid)
  lines=p.read_text(encoding='utf-8').splitlines()
  check(all(1<=lo<=hi<=len(lines) for lo,hi in ranges),'Source ranges '+eid)
  proofs.append({'id':eid,'repository':repository,'commit':commit,'path':path,'sha256':sha(p),'url':'https://github.com/'+repository+'/blob/'+commit+'/'+path,'observation':obs,'limit':limit,
  'excerpts':[{'start':lo,'end':hi,'text':'\n'.join(lines[lo-1:hi])} for lo,hi in ranges]})
 proofids={p['id'] for p in proofs}
 ps=[]
 for raw in inp['packages']:
  p=copy.deepcopy(raw)
  check(len(p['v'])==len(roles),'Roles '+p['id'])
  p['central']=dict(zip(roles,p.pop('v')))
  check(sum(v for _,v in p['java'])==p['central']['dev_java'],'Java work sum '+p['id'])
  check(sum(v for _,v in p['ui'])==p['central']['dev_frontend'],'UI work sum '+p['id'])
  check(set(p['evidence'])<=proofids and p['evidence'],'Evidence '+p['id'])
  check(len(p['reuse'])>0 and p['risk'] and p['work'],'Boundary and owners '+p['id'])
  lo,hi=p['f'];check(0<lo<=1<=hi,'Envelope factors '+p['id'])
  p['effort']={r:[math.floor(v*lo*2+1e-8)/2,v,math.ceil(v*hi*2-1e-8)/2] for r,v in p['central'].items()}
  p['total']=[sum(v[i] for v in p['effort'].values()) for i in range(3)]
  p['origin']='Estimation d’ingénierie assistée IA, non mesurée, sans revue humaine. Les actions et durées sont proposées, pas observées dans les ERP.'
  ps.append(p)
 check(len({p['id'] for p in ps})==len(ps),'Unique new funding packages')
 incroles={r:[sum(p['effort'][r][i] for p in ps) for i in range(3)] for r in roles}
 inc={'roles':incroles,'total':[sum(v[i] for v in incroles.values()) for i in range(3)]}
 cumulative={'roles':{r:[prev['cumulative_estimated']['roles'][r][i]+incroles[r][i] for i in range(3)] for r in roles}}
 cumulative['total']=[sum(v[i] for v in cumulative['roles'].values()) for i in range(3)]
 for i in range(3):check(abs(cumulative['total'][i]-prev['cumulative_estimated']['total'][i]-inc['total'][i])<1e-8,'Cumulative conservation '+str(i))
 coverage=[]
 for num in inp['capabilities']:
  bc=f'BC-{num:03}';c=bybc[bc];n=native[c['id']];g=gridmap[bc]
  check(g['capacite_id']==c['id'] and g['fonctions']==n['native_functions'],'Native identity/functions '+bc)
  direct=[p for p in ps if p['cap']==num];check(len(direct)==1,'One direct owner '+bc)
  p=direct[0]
  c={k:v for k,v in c.items() if k not in ('comparatively_studied','scenario_estimated','opportunity_admitted','status','framed')}
  coverage.append({**c,'comparatively_studied':True,'scenario_estimated':True,'status':'estimation_conditionnelle_classe_C','native_functions':n['native_functions'],'native_boundary':n.get('native_boundary',n.get('native_frontier',n.get('boundary'))),
   'boundaries':n.get('boundaries',n.get('core_integration',n.get('boundary'))),'source_refs':n['source_refs'],'generic_contract':p['work'],'market_analogy':p.get('analogy',inp['contract']),
   'function_funding':[{'function':f['id'],'owner':p['id'],'shared_owners':p['reuse'],'evidence':p['evidence'],'match_status':'analogie partielle ; développements restants explicités dans le lot'} for f in n['native_functions']],
   'analogy_type':p.get('analogy_type','partielle'),'estimate_class':'C','structural_reserve':num in inp['strong_reserves'],'range_reason':p['risk'],'full_native_scope_under_contract':True})
 oldids={c['id'] for c in prev['cumulative_coverage']};newids={c['id'] for c in coverage}
 check(not oldids&newids,'No duplicate capability')
 cumulative_coverage=sorted(prev['cumulative_coverage']+coverage,key=lambda c:c['block'])
 count=len(cumulative_coverage)
 check(count==len({c['id'] for c in cumulative_coverage}) and count<=88,'Cumulative unique count')
 beforestrong=prev.get('structural_reserve_ids',['BC-025','BC-026','BC-027','BC-040','BC-041','BC-042','BC-044','BC-047','BC-048'])
 strong=sorted(set(beforestrong)|{f'BC-{n:03}' for n in inp['strong_reserves']})
 # Three sequential engineering stages, no productivity reduction. Every role-day allocated once.
 shares={'analyse_produit':[.7,.2,.1],'architecture':[.5,.4,.1],'dev_java':[0,.85,.15],'dev_frontend':[0,.85,.15],'ux':[.6,.3,.1],'qa':[.1,.2,.7],'plateforme':[.2,.5,.3],'securite':[.3,.4,.3],'coordination':[.2,.6,.2],'expert_optimisation':[.4,.5,.1]}
 staff=dict(zip(roles,inp.get('staff',[.8,.5,2,1,.3,1,.4,.3,.3,.5])))
 phases=[]
 for j,label in enumerate(['Définition et contrats','Réalisation et raccords','Qualification et stabilisation']):
  work={r:[v*shares[r][j] for v in incroles[r]] for r in roles}
  floors=[[.5,1,1.5],[2,3,5],[.5,1,2]][j]
  duration=[max(floors[i],max(work[r][i]/(staff[r]*18) if staff[r] else 0 for r in roles)) for i in range(3)]
  check(all(staff[r]>0 or all(x==0 for x in work[r]) for r in roles),'Staff capacities '+label)
  phases.append({'name':label,'roles':work,'staff':staff,'months':duration,'minimum_sequence_months':floors})
 months=[sum(p['months'][i] for p in phases) for i in range(3)]
 for r in roles:
  for i in range(3):check(abs(sum(p['roles'][r][i] for p in phases)-incroles[r][i])<1e-8,'Calendar preserves role '+r+str(i))
 prevmonths=prev['calendar_preserved']['sequential_total_months'] if it==16 else prev['calendar']['sequential_total_months']
 witnesses=run_witnesses(it)
 check(witnesses and all(x['passed'] for x in witnesses),'Synthetic boundary checks')
 result={'id':f'iteration-{it}-resultats','date':'2026-10-30','title':inp['title'],'roles':old14['roles'],'contract':inp['contract'],'profile':inp['profile'],
 'packages':ps,'incremental':inc,'previous_cumulative':prev['cumulative_estimated'],'cumulative_estimated':cumulative,
 'developer_gross_jh':[incroles['dev_java'][i]+incroles['dev_frontend'][i] for i in range(3)],
 'cumulative_developer_gross_jh':[cumulative['roles']['dev_java'][i]+cumulative['roles']['dev_frontend'][i] for i in range(3)],
 'coverage':coverage,'cumulative_coverage':cumulative_coverage,'progress':{'compared_before':len(oldids),'new_compared':len(newids),'compared_cumulative':count,'total_native':88,'percent':100*count/88,'not_compared':88-count,'empirically_calibrated':0,'meaning':'Couverture documentaire et estimation conditionnelle, pas part budgétaire ni précision mesurée.'},
 'structural_reserve_ids':strong,'bounded_without_named_structural_reserve_count':count-len(strong),
 'full_core_jh':cumulative['total'] if count==88 else None,'full_core_status':'ordre de grandeur conditionnel sur les88 capacités, réserve de contrat et d’intégration des modules' if count==88 else 'partiel',
 'calendar':{'phases':phases,'incremental_months':months,'incremental_public_months':[math.ceil(x) for x in months],
 'sequential_total_months':[prevmonths[i]+months[i] for i in range(3)],
 'sequential_public_months':[math.ceil(prevmonths[i]+months[i]) for i in range(3)],
 'meaning':'18JH/personne/mois, contributions fractionnées. Dépendances supposées disponibles. Somme des familles diagnostique : pas un plan programme ni une preuve COCOMO. Les raccords17/18 et clôture20 sont inclus sans délai de programme validé.'},
 'supplemental_sources':inp.get('supplemental_sources',[]),
 'uncertainty':{'class':'C','percentiles':None,'reduced':inp['reduced'],'remaining':inp['remaining'],'ranges':'Jugements bas/central/haut sur même contrat, pas distribution statistique ; durées d’actions non calibrées.'},
 'next_iteration':inp['next'],'active_model_changed':False,'proofs_file':f'iteration-{it}-preuves.json','witnesses':witnesses,'checks':checks,
 'input_sha256':sha(A/f'iteration-{it}-entrees.json'),'method':'market-code-informed engineering estimate; no direct reuse of ERP code assumed, no measured productivity or numeric COSMIC/COCOMO/ISBSG triangulation'}
 write(f'iteration-{it}-preuves.json',{'evidence':proofs,'method':'Source code inspected at frozen revisions; these excerpts do not prove whole-product coverage or observed human effort.'})
 write(f'iteration-{it}-resultats.json',result)
 print(json.dumps({'iteration':it,'incremental':inc['total'],'cumulative':cumulative['total'],'coverage':count,'months':result['calendar']['incremental_public_months'],'witnesses':len(witnesses)},ensure_ascii=False))
if __name__=='__main__':main(int(sys.argv[1]))
