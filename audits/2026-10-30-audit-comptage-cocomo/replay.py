"""Audit-only replay of sizes with USC statement weights. Fractions, scope, reuse and COCOMO parameters are unchanged."""
from pathlib import Path
from collections import defaultdict
import json,gzip,base64,sys,statistics,math,importlib.util
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent;T=R/'tmp/cocomo-count-audit';sys.path[:0]=[str(R/'tools'),str(R/'tmp/model-deps')]
from estimation_calculation import formula,rounded
from estimation_components import unpack_archives
P=('erpnext','odoo','tryton','axelor')
def load(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
MAPS=json.loads(gzip.decompress((O/'node-maps.json.gz').read_bytes()));AR=unpack_archives(load('audits/2026-10-30-core-adoption-09/archives.json'));REPOS=AR['common_measures']['specification']['repos'];checks=[]
def fullpath(repo,path):return (Path(REPOS[repo]['root'])/path).as_posix()
def prod(repo):return 'erpnext' if repo=='frappe' else 'axelor' if repo in ('platform','studio') else repo
def close(a,b,label):
 if not math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-7):raise AssertionError((label,a,b))
 checks.append(label)
def node3(n):return n['kind'],n['start'],n['end']
I3={path:{node3(n):n for n in d['nodes']} for path,d in MAPS.items()}
IKEY={path:{f"{n['kind']}:{n['start']}:{n['end']}:{n['col']}:{n['end_col']}":n for n in d['nodes']} for path,d in MAPS.items()}
def weight(path,node,new):
 if not new or not MAPS[path]['ucc_supported']:return 1
 if isinstance(node,str):
  if not node.split(':',1)[0] in {n['kind'] for n in MAPS[path]['nodes']}:return 1
  assert node in IKEY[path],(path,node)
  return IKEY[path][node]['ucc_weight']
 k=node3(node) if isinstance(node,dict) else node
 assert k in I3[path],(path,k)
 return I3[path][k]['ucc_weight']
def amount(path,nodes,new):return sum(weight(path,n,new) for n in nodes)
def ns(nodes):return {node3(n) for n in nodes}
C=load('audits/2026-10-30-stock-opportunite-08/inputs.json')['cocomo'];E=formula('cocomo_exponent',B=C['B'],SF_sum=C['SF_sum'])
def effort(size):return formula('cocomo_effort',A=C['A'],KSLOC=size/1000,E=E,EM=C['other_EM'],SCED=C['SCED'],month_hours=C['month_hours'],day_hours=C['day_hours'],effort_phase_factor=C['effort_phase_factor']) if size else 0

def md_sizes(new):
 m=load('audits/2026-10-30-master-data-comparable-reuse/measurements.json');native=defaultdict(float);issues=[]
 for f in m['files']:
  path=fullpath(f['repo'],f['path']);d=MAPS[path];program=f['program_units']
  if new and d['ucc_supported']:
   excluded=[]
   for x in f.get('excluded_blocks',[]):
    kinds={'method':{'FunctionDef','AsyncFunctionDef','method_declaration'},'class':{'ClassDef','class_declaration'},'field':{'Assign','AnnAssign','field_declaration'},'field_handler':{'pair'}}.get(x['kind'],set())
    candidates=[n for n in d['nodes'] if n['start']==x.get('line') and n['kind'] in kinds]
    if not candidates and x['kind']=='field_handler':
     candidates=[n for n in load(O/'scope-exclusions.json')[path] if n['start']==x['line']]
     assert candidates,(path,x)
    for n in candidates:excluded.append((n['start'],n['end']))
   selected=[n for n in d['nodes'] if not any(a<=n['start'] and n['end']<=b for a,b in excluded)]
   # Compare the old exact scope before using its recount. Non-program exclusions are not added.
   if len(selected)!=f['program_units']:
    issues.append(dict(path=path,old=f['program_units'],selected=len(selected)));program=f['program_units']
   else:program=amount(path,selected,True)+len([x for x in d['orphans'] if not any(a<=x['line']<=b for a,b in excluded)])
  native[f['product']]+=(program+f['declarative_units'])*(0.035 if f['treatment']=='reused' else 1)
 a=load('audits/2026-10-30-master-data-spring-flow/analogues.json');p=load('audits/2026-10-30-master-data-spring-flow/inputs.json');base=load('audits/2026-10-30-master-data-spring-reprise/results.json');samples={}
 for s in a['samples']:
  path=s['path'];nodes=[n for n in MAPS[path]['nodes'] if any(x<=n['start']<=y for x,y in s['ranges'])];close(len(nodes),s['program_units'],'MD sample '+s['id']);samples[s['id']]=amount(path,nodes,new)
 banks={k:statistics.median(samples[id] for id in b['sample_ids']) for k,b in a['unit_bank'].items()}
 if not new:
  for k,v in banks.items():close(v,a['unit_bank'][k]['range'][1],'MD bank '+k)
 complement=base['size']['proposed_complements_units'];original_blocks=sum(b['quantity']*a['unit_bank'][b['kind']]['range'][1] for b in p['blocks']);new_blocks=sum(b['quantity']*banks[b['kind']] for b in p['blocks']);complement+=new_blocks-original_blocks
 methods={x['id']:x for x in load('audits/2026-10-30-master-data-spring-reprise/method-measures.json')}
 for x in load('audits/2026-10-30-master-data-spring-reprise/treatment-mapping.json'):
  block=next(b for b in p['blocks'] if b['id']==x['block']);now=0
  for id in x['method_refs']:
   mth=methods[id];nodes=[n for n in MAPS[mth['path']]['nodes'] if mth['start_line']<=n['start'] and n['end']<=mth['end_line']];close(len(nodes),mth['program_units'],'MD refined '+id);now+=amount(mth['path'],nodes,new)
  complement+=(now-x['proposed_units'])-(block['quantity']*banks[block['kind']]-x['previous_units'])
 sizes={r:native[r]+complement for r in P}
 if not new:
  for r in base['rows']:close(sizes[r['id']]/1000,r['equivalent_KSLOC'],'MD native '+r['id'])
 return sizes,dict(complements=complement,scope_fallbacks=issues)

def stock_sizes(new):
 spec=load('audits/2026-10-30-stock-adoption-10/inputs.json');ni=load('audits/2026-10-30-stock-opportunite-08/inputs.json');baseline={r['id']:r for r in load('audits/2026-10-30-stock-opportunite-08/results.json')['rows']};paid=load('audits/2026-10-30-stock-adoption-10/measurements.json')['files'];deduct={(r['product'],r['path']):ns(r['nodes']) for r in paid};sizes={};banks={};details={}
 for p in P:
  idx={f['path']:f for f in ni['attributions'] if f['product']==p};extras={f['path']:f for f in ni['stock_dependency_fragments'][p]};per={f['path']:f for f in load(spec['perimeters'][p])['files']};known={f['path']:ns(f.get('counted_nodes',[])) for f in load(spec['known_stock'][p])['files']};chains={k:load(v) for k,v in spec['chains'][p].items()}
  def val(path,nodes):return amount(fullpath(p,path),nodes,new)
  core=0
  for path,f in idx.items():
   if new:
    d=MAPS[fullpath(p,path)];available=d['ucc_program'] if d['ucc_supported'] else d['old_program'];available-=val(path,deduct.get((p,path),set()));floor=val(path,known.get(path,set()));program=max(available*f['attribution']['central'],floor)
   else:program=max(f['available_program']*f['attribution']['central'],f['known_stock_program_floor'])
   core+=program+max(f['available_declarative']*f['attribution']['central'],f['known_stock_declarative_floor'])
  for path,f in extras.items():
   nodes=set()
   for chain in chains.values():
    for file in chain['files']:
     if file['path']==path and file['role']!='framework_reused':nodes|=ns(file['counted_nodes'])
   close(len(nodes),f['program_units'],'Stock dependency '+p+'/'+path);core+=val(path,nodes)*f['attribution']['central']
  bank={}
  for label,kind in [('correction_chain','correction'),('reservation_chain','reservation')]:
   bank[label]=0
   for f in chains[kind]['files']:
    if f['role']=='framework_reused':continue
    path=f['path'];row=idx.get(path) or extras[path];nodes=ns(f['counted_nodes'])
    if path.endswith('.java'):
     ctors=[m for m in f['methods'] if m['name']==Path(path).stem];nodes={n for n in nodes if not any(m['start']<=n[1]<=n[2]<=m['end'] for m in ctors)}
    nodes-=deduct.get((p,path),set());bank[label]+=max(val(path,nodes & known.get(path,set())),val(path,nodes)*row['attribution']['central'])
  for label,kind in [('positions_component','K2'),('inventory_component','K3')]:
   bank[label]=0
   for path,f in idx.items():
    if kind not in f['components']:continue
    nodes=ns(f['whole_method_nodes'])-deduct.get((p,path),set());bank[label]+=max(val(path,nodes & known.get(path,set())),val(path,nodes)*f['attribution']['central'])
  old=baseline[p];scaffold=ni['new_module_scaffolding'][p]['program_units_per_new_service_module'];extra=old['Flow_complements_equivalent_units']
  for mod in ni['complement_module_analogies']:
   before=old['detail']['analogue_bank'][mod['analogue']]['program_units'];extra+=(bank[mod['analogue']]-before)*mod['central']
  if not new:
   close(core,old['base_equivalent_units'],'Stock base '+p)
   for k,v in bank.items():close(v,old['detail']['analogue_bank'][k]['program_units'],'Stock bank '+p+'/'+k)
   close(extra,old['Flow_complements_equivalent_units'],'Stock extra '+p)
  sizes[p]=core+extra;banks[p]=bank;details[p]=dict(base=core,complements=extra)
 return sizes,banks,details

def ownership_sizes(new,banks):
 ni=load('audits/2026-10-30-propriete-stock-calcul-02/inputs.json');base={r['id']:r for r in load('audits/2026-10-30-propriete-stock-calcul-02/results.json')['rows']};sizes={}
 for p in P:
  size=base[p]['detail']['equivalent_units']
  for m in ni['hypotheses']['modules']:
   size+=(banks[p][m['analogue']]-ni['banks'][p]['central'][m['analogue']]['program_units'])*m['central']
  sizes[p]=size
 return sizes

def component_sizes(new,stock_banks):
 d=AR['proposal_inputs'];m=AR['common_measures'];adjust=AR['common_adjustment'];ni=load('audits/2026-10-30-propriete-stock-calcul-02/inputs.json');specs={s['id']:s for s in m['specification']['mechanisms']};counts={id:dict.fromkeys(P,0.) for id in specs};owners={};banks={id:dict.fromkeys(P,0.) for id in specs}
 for x in m['source_node_ownership']:
  k=(x['repo'],x['path'],x['atom']);owners[k]=x['mechanism'];counts[x['mechanism']][prod(x['repo'])]+=weight(fullpath(x['repo'],x['path']),x['atom'],new)
 for b in m['bindings']:
  if b['kind']=='program':banks[b['mechanism']][b['product']]+=sum(weight(fullpath(b['repo'],b['path']),a['key'],new) for a in b['atoms'])
 for id,s in specs.items():
  if s.get('provider')=='stock_correction':banks[id]={p:stock_banks[p]['correction_chain'] for p in P}
 sourceowners={k:specs[v]['owner'] for k,v in owners.items() if prod(k[0]) not in adjust['base_exclusions'].get(v,[])}
 families={f['slug']:f for f in d['families']};priority=['orders','master-plan','plan-preparation','optimization','service-planning'];priority += [f for f in families if f not in priority];localbank={};localbase={}
 for slug in priority:
  f=families[slug];localbank[slug]=dict.fromkeys(P,0.);localbase[slug]=dict.fromkeys(P,0.);seen=set()
  for b in f['bindings']:
   for a in b['atoms']:
    k=(b['repo'],b['path'],a['key'])
    if k in seen:continue
    seen.add(k);w=weight(fullpath(b['repo'],b['path']),a['key'],new);localbank[slug][b['product']]+=w
    if not b['provided_kernel'] and k not in sourceowners:sourceowners[k]=slug;localbase[slug][b['product']]+=w
 def schemas(models,p):
  t=ni['schema_templates'][p];total=0
  for fields in models:
   n=len(fields);total+=n*t['program_per_field']+t.get('program_per_new_model',0)+n*t['declarations_per_field']+t['per_new_model']+n*t['view_field']+t['view_model']
  return total
 common={s:dict.fromkeys(P,0.) for s in families}
 for id,s in specs.items():
  for p in P:
   base=0 if p in adjust['base_exclusions'].get(id,[]) else counts[id][p];scaffold=ni['new_module_scaffolding'][p]['program_units_per_new_service_module'];schema=schemas([x.split(':',1)[1].split(',') for x in s['schemas']],p)
   common[s['owner']][p]+=base+banks[id][p]*s['fraction']+scaffold+schema
 details={}
 for slug,f in families.items():
  details[slug]={}
  for p in P:
   bank=localbank[slug][p]
   if 'analogue_provider' in f:bank=localbank['master-plan'][p] if f['analogue_provider']['id']=='net-planning-component' else stock_banks[p]['correction_chain']
   scaffold=ni['new_module_scaffolding'][p]['program_units_per_new_service_module'];extra=bank*f['extension_fraction']*f['quantity']+scaffold*f['quantity']+schemas([x['fields'] for x in f['schemas']],p)
   for mod in f.get('additional_modules',[]):
    analogue=localbank['service-planning'][p] if mod['id']=='solver-run-contract' else stock_banks[p]['correction_chain'];extra+=analogue*mod['fraction']+scaffold*mod.get('scaffolds',1)
   details[slug][p]=common[slug][p]+localbase[slug][p]+extra
 groups={g['id']:{p:sum(details[f][p] for f in g['families']) for p in P} for g in d['economic_units']}
 if not new:
  for g in AR['proposal_results']['economic_units']:
   for row in g['rows']:close(groups[g['id']][row['id']],row['equivalent_units'],'Component '+g['id']+'/'+row['id'])
 return groups,dict(local_banks=localbank,common_banks=banks,details=details)

def run(new):
 md,mdinfo=md_sizes(new);stock,banks,stockinfo=stock_sizes(new);own=ownership_sizes(new,banks);groups,components=component_sizes(new,banks)
 sizes=dict(master_data=md,stock=stock,ownership=own,**groups)
 return dict(sizes=sizes,efforts={g:{p:effort(v) for p,v in row.items()} for g,row in sizes.items()},master_data=mdinfo,stock_details=stockinfo,component_details=components)
def main():
 old=run(False);new=run(True);units=[]
 for i,g in enumerate(old['sizes']):
  step=100 if g=='master_data' else 10;rows=[]
  for p in P:
   a=old['efforts'][g][p];b=new['efforts'][g][p];rows.append(dict(id=p,old_units=old['sizes'][g][p],new_units=new['sizes'][g][p],old_jh=a,new_jh=b,delta_jh=b-a,delta_pct=100*(b-a)/a,old_rounded_jh=rounded(a,step),new_rounded_jh=rounded(b,step)))
  units.append(dict(id=g,rows=rows))
 totals={p:dict(old_raw_jh=sum(u['rows'][list(P).index(p)]['old_jh'] for u in units),new_raw_jh=sum(u['rows'][list(P).index(p)]['new_jh'] for u in units),old_rounded_jh=sum(u['rows'][list(P).index(p)]['old_rounded_jh'] for u in units),new_rounded_jh=sum(u['rows'][list(P).index(p)]['new_rounded_jh'] for u in units)) for p in P}
 for p,t in totals.items():t['delta_raw_jh']=t['new_raw_jh']-t['old_raw_jh'];t['delta_raw_pct']=100*t['delta_raw_jh']/t['old_raw_jh']
 close(totals['axelor']['old_rounded_jh'],4160,'Retained Java total')
 data=dict(status='audit_sensitivity_not_adopted',units=units,totals=totals,replay_baseline_checks=len(checks),checks=checks,master_data_scope_fallbacks=new['master_data']['scope_fallbacks'],unchanged=['scope','fractions','module quantities','COCOMO parameters','reuse 0.035','declarative generator profiles','scaffold and configuration assumptions','JSX/TypeScript units','COSMIC counts and benchmark'],old=old,new=new)
 (O/'impact.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(dict(totals=totals,baseline_checks=len(checks),MD_scope_fallbacks=len(data['master_data_scope_fallbacks'])),ensure_ascii=False))
if __name__=='__main__':main()
