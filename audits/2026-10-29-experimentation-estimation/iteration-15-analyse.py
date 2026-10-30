"""Independent enumeration, validation and comparison; never transforms runtime into human effort."""
from pathlib import Path
import json,itertools,statistics,hashlib,datetime,re
A=Path(__file__).resolve().parent
load=lambda name:json.loads((A/name).read_text(encoding='utf-8'))
batch=load('iteration-15-cases.json');raw=load('iteration-15-raw.json');previous=load('iteration-14-resultats.json')
cases={c['id']:c for c in batch['cases']}
checks=[]
def ck(ok,label):
 if not ok:raise AssertionError(label)
 checks.append(label)
def evaluate(c,a):
 if len(a)!=len(c['tasks']) or any(j<0 or j>=len(c['tasks'][i]['options']) for i,j in enumerate(a)):return None
 chosen=[t['options'][j] for t,j in zip(c['tasks'],a)]
 if any(not o['admissible'] for o in chosen):return None
 for resource,cap in c['capacity'].items():
  if sum(o['uses'].get(resource,0) for o in chosen)>cap:return None
 if any(chosen[i]['end']>chosen[j]['start'] for i,j in c['precedence']):return None
 return sum(o['cost'] for o in chosen)+sum(c['fixed'].get(g,0) for g in {o['group'] for o in chosen})
oracles={}
for c in cases.values():
 if not c['exact']:continue
 best=None;count=0;enumerated=0;winner=None
 for a in itertools.product(*(range(len(t['options'])) for t in c['tasks'])):
  enumerated+=1;v=evaluate(c,a)
  if v is None:continue
  count+=1
  if best is None or v<best:best=v;winner=list(a)
 oracles[c['id']]={'minimum':best,'feasible_assignments':count,'enumerated':enumerated,'one_optimum':winner}
rows=[r for r in raw['rows'] if r['engine'] in ['greedy','ortools','timefold','hybrid'] and r['case'] in cases]
ck(len(rows)==len(cases)*len(batch['seeds'])*4,'Complete matrix:23 cases x3 seeds x4 strategies')
ck(len({(r['case'],r['seed'],r['engine']) for r in rows})==len(rows),'Unique experiment identity')
for r in rows:
 c=cases[r['case']];v=evaluate(c,r['assignment']);prefix=f"{r['case']}/{r['seed']}/{r['engine']}"
 ck((v is not None)==r['valid'],prefix+' independent validity')
 ck(v==r['cost'],prefix+' independent cost')
 if r['engine']=='timefold' and r.get('score','').startswith('0hard/'):
  ck(r['valid'] and int(r['score'].split('/')[1][:-4])==-v,prefix+' serialized choice matches Timefold feasible score')
 if r['status']=='OPTIMAL':
  ck(r['valid'],prefix+' optimum must be feasible')
  if c['exact']:ck(v==oracles[c['id']]['minimum'],prefix+' claimed optimum verified by enumeration')
 if r['status']=='INFEASIBLE' and c['exact']:ck(oracles[c['id']]['minimum'] is None,prefix+' claimed infeasibility verified')
 if c['exact'] and r.get('best_bound') is not None and oracles[c['id']]['minimum'] is not None:
  ck(r['best_bound']<=oracles[c['id']]['minimum']+1e-6,prefix+' bound does not exceed exact optimum')
 for stage in r.get('stages',[]):
  vstage=evaluate(c,stage['assignment'])
  ck(vstage==stage['cost'] and (vstage is not None)==stage['valid'],prefix+'/'+stage['engine']+' independent stage validation')
 r['exact_minimum']=oracles[c['id']]['minimum'] if c['exact'] else None
 r['gap_to_exact']=r['cost']-r['exact_minimum'] if r['valid'] and r['exact_minimum'] is not None else None
top=next(r for r in raw['rows'] if r['engine']=='ortools_top1')
ck(top['status']=='INFEASIBLE' and oracles['ATP_TRAP']['minimum']==3,'Top1 loses the only feasible full-domain assignment')
timeout=next(r for r in raw['rows'] if r['case']=='ZERO_BUDGET')
ck(timeout['status']=='UNKNOWN' and not timeout['valid'],'Zero solver budget remains UNKNOWN, never infeasible')
ck(raw['guards']['unknown_resource_rejected'],'Unknown resource rejected before optimization')
ck(raw['spring_context_ok'],'Java solver harness instantiated by Spring')
ck(oracles['PTP_FIXED']['minimum']==16,'Shared fixed cost independent optimum16')
# Deliberate corruptions must not pass the independent validator.
ck(evaluate(cases['ATP_TRAP'],[0,0]) is None,'Validator rejects duplicate resource')
ck(evaluate(cases['MANDATORY_FILTER'],[0]) is None,'Validator rejects forbidden option')
ck(evaluate(cases['CTP_CHAIN'],[1,0]) is None,'Validator rejects broken precedence')
ck(evaluate(cases['ATP_TRAP'],[-1,0]) is None,'Validator rejects incomplete assignment')
summaries={}
for engine in ['greedy','ortools','timefold','hybrid']:
 rr=[r for r in rows if r['engine']==engine];small=[r for r in rr if cases[r['case']]['exact']]
 feasible_small=[r for r in small if oracles[r['case']]['minimum'] is not None]
 summaries[engine]={'runs':len(rr),'valid':sum(r['valid'] for r in rr),'small_runs':len(small),
 'small_feasible_instances_runs':len(feasible_small),'small_exact_optimum_hits':sum(r['gap_to_exact']==0 for r in feasible_small),
 'small_no_solution_runs':sum(oracles[r['case']]['minimum'] is None for r in small),
 'infeasibility_proofs_small':sum(r['status']=='INFEASIBLE' for r in small),
 'wall_ms_median':statistics.median(r['wall_ms'] for r in rr),'wall_ms_max':max(r['wall_ms'] for r in rr)}
loads=[]
for cid,c in cases.items():
 if c['exact']:continue
 runs=[r for r in rows if r['case']==cid]
 best_known=min(r['cost'] for r in runs if r['valid'])
 entry={'id':cid,'lines':len(c['tasks']),'options_per_line':len(c['tasks'][0]['options']),'best_observed':best_known,'engines':{}}
 for engine in summaries:
  rr=[r for r in runs if r['engine']==engine]
  valid=[r for r in rr if r['valid']]
  entry['engines'][engine]={'valid_runs':len(valid),'costs':[r['cost'] for r in rr],'statuses':[r['status'] for r in rr],
  'wall_ms':[r['wall_ms'] for r in rr],'bounds':[r.get('best_bound') for r in rr],
  'relative_gap_to_best_observed_pct':[100*(r['cost']-best_known)/best_known if r['valid'] else None for r in rr]}
 loads.append(entry)
paired=[]
for c in cases.values():
 for seed in batch['seeds']:
  cp=next(r for r in rows if r['case']==c['id'] and r['seed']==seed and r['engine']=='ortools')
  hy=next(r for r in rows if r['case']==c['id'] and r['seed']==seed and r['engine']=='hybrid')
  state='both_no_feasible'
  if cp['valid'] and hy['valid']:state='hybrid_better' if hy['cost']<cp['cost'] else ('ortools_better' if cp['cost']<hy['cost'] else 'equal')
  elif hy['valid']:state='only_hybrid_feasible'
  elif cp['valid']:state='only_ortools_feasible'
  paired.append(dict(case=c['id'],seed=seed,state=state))
counts={s:sum(p['state']==s for p in paired) for s in sorted({p['state'] for p in paired})}
dev=[sum(previous['cumulative_estimated']['roles'][role][i] for role in ['dev_java','dev_frontend']) for i in range(3)]
ck(sum(v[1] for v in previous['cumulative_estimated']['roles'].values())==8935,'Cumulative role sum preserved')
ck(len(previous['progress']['cumulative_ids'])==56,'56 unique native capabilities preserved')
result={'id':'iteration-15-resultats','date':'2026-10-29','scope':'Essais comparatifs des mécanismes ATP/CTP/PTP ; aucune nouvelle capacité',
 'case_count':len(cases),'exact_case_count':len(oracles),'runs':len(rows),'additional_probes':2,'seeds':batch['seeds'],
 'oracles':oracles,'strategies':summaries,'load_results':loads,'hybrid_vs_ortools':counts,'paired_comparison':paired,
 'incremental_new_scope_jh':[0,0,0],'revision_delta_jh':[0,0,0],
 'cumulative_estimated':previous['cumulative_estimated'],'cumulative_developer_gross_jh':dev,
 'availability_family':previous['incremental'],'calendar_preserved':previous['calendar'],
 'progress':dict(previous['progress'],compared_before=56,new_compared=0,new_ids=[],conditional_estimated_before=56),
 'cumulative_coverage':previous['cumulative_coverage'],
 'empirically_calibrated_capabilities':0,'full_core_jh':None,'active_model_changed':False,
 'economic_conclusion':'JH, bornes et calendrier conservés : essais techniques sans observation de productivité, nouveau mécanisme ni suppression de lot. Les travaux de qualification sont déjà financés par E142/B047/B048/S143/Q141 et E121/B037/S122 ; aucun second budget.',
 'uncertainty_class':'C','statistical_percentiles':None,
 'limits':['Jeux synthétiques conçus et exécutés avec assistance IA, sans revue métier humaine.',
 'CTP limité à des alternatives et créneaux déjà énumérés : ni nomenclature complète ni génération réelle des créneaux.',
 'Score Timefold non incrémental (EasyScoreCalculator) : aucun classement général des performances des bibliothèques.',
 'OR-Tools CP-SAT en un worker ; budgets de recherche avec frais de construction supplémentaires ; une JVM locale et trois graines.',
 'Les cas à100 lignes ne prouvent pas20 requêtes/s,10 calculs concurrents ni le profil S6 complet.',
 'Coûts entiers connus, données stables ; aucune preuve du verrouillage, de l’actualisation ou du déploiement multi-OS.',
 'Un optimum du modèle ne prouve pas la validité métier de ses données.',
 'Une comparaison de solveurs ne calibre ni COSMIC, ni COCOMO, ni ISBSG.'],
 'checks':checks,'validated_rows':rows}
(A/'iteration-15-resultats.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['case_count','runs','strategies','load_results','hybrid_vs_ortools','cumulative_developer_gross_jh']},ensure_ascii=False,indent=2))
