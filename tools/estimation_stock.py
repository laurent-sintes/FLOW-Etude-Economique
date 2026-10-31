"""Pure Stock size preparation from recorded source measures and explicit analogies."""
from copy import deepcopy
from collections import Counter
from estimation_inputs import require
from estimation_preparation import number,unique,close,validate_allocation

def node_set(nodes):
 values=[(n['kind'],n['start'],n['end']) for n in nodes]
 require(len(values)==len(set(values)),'Duplicate recorded source node')
 require(all(isinstance(k,str) and type(a) is int and type(b) is int and 0<a<=b for k,a,b in values),'Invalid recorded node')
 return set(values)

def prepare_stock(documents,contract,registry,formula):
 d={k:deepcopy(documents[path]) for k,path in contract['inputs'].items()}
 spec=d['specification'];ni=d['native_inputs'];baseline=d['baseline'];allocation=d['allocation']
 require(spec['capabilities']==[c['id'] for c in contract['scope']['capabilities']],'Stock capability scope mismatch')
 require(spec['recipe']==contract['recipe'],'Stock recipe mismatch')
 require(spec['cocomo']==ni['cocomo'],'Stock parameter mismatch')
 c=ni['cocomo']
 for k in ('A','B','C','D','month_hours','day_hours','effort_phase_factor','schedule_phase_factor','other_EM','SCED'):
  number(c[k],k,positive=True)
 number(c['SF_sum'],'SF_sum')
 require(c['SCED']==1 and c['REVL']==0,'Only nominal Stock SCED / REVL supported')
 products=ni['native_references']
 require(len(set(products))==len(products)==4,'Stock native reference coverage')
 require(allocation['selected_reference'] in products,'Stock allocation reference')
 allocation['role_labels']=spec['role_labels']
 validate_allocation(d['activities']['cocomo'],allocation,c)
 mechanisms={m['id']:m for m in registry['mechanisms']}
 funded={mechanisms[x['mechanism']]['basis'].get('family',mechanisms[x['mechanism']]['basis']['kind'])
   for x in contract['funding_claims'] if x['mode']=='funded'}
 require(funded=={'component_domain'}|{m['id'] for m in ni['complement_module_analogies']},'Stock funding scope mismatch')
 consumed={x['mechanism'] for x in contract['funding_claims'] if x['mode']=='consumed'}
 require(consumed==set(spec['reused_mechanisms']),'Stock generic reuse owner mismatch')
 md={ (m['product'],m['path']):node_set(m['nodes']) for m in d['native_measures']['files']}
 measured_MD=documents[spec['master_data_measures']]['files']
 indices={};known={};chains={}
 for p in products:
  per=documents[spec['perimeters'][p]]
  prior=documents[spec['known_stock'][p]]
  indices[p]=unique([x for x in ni['attributions'] if x['product']==p],'path','Stock file')
  originals=unique(per['files'],'path','native component file')
  require(set(originals)==set(indices[p]),'Stock native component coverage')
  prior_index=unique(prior['files'],'path','known Stock file')
  known[p]={name:node_set(f['counted_nodes']) for name,f in prior_index.items()}
  for path,f in indices[p].items():
   origin=originals[path]
   require(f['repo']==origin['repo'] and f['sha256']==origin['sha256'] and f['commit']==origin['commit'],'Stock source provenance mismatch')
   require(f['components']==origin['components'],'Stock component assignment changed')
   for k in ('program_units','declarative_units'):
    close(f['available_'+('program' if k=='program_units' else 'declarative')],origin['native_'+('program' if k=='program_units' else 'declarative')+'_after_MD'],'Stock source size')
    close(origin['native_'+('program' if k=='program_units' else 'declarative')+'_after_MD'],origin[k]-origin['already_funded_MD'][k],'MD source deduction')
   require(f['excludes']==origin['already_funded_MD'],'Stock MD deduction metadata')
   if f['excludes']['program_units'] or f['excludes']['declarative_units']:
    paid=[x for x in measured_MD if x['product']==p and x['path']==path and x['repo']==f['repo']]
    require(len(paid)==1 and paid[0]['sha256']==f['sha256'],'Master Data overlap provenance')
    close(paid[0]['program_units'],f['excludes']['program_units'],'MD program overlap')
    close(paid[0]['declarative_units'],f['excludes']['declarative_units'],'MD declaration overlap')
   close(len(md.get((p,path),set())),f['excludes']['program_units'],'MD node exclusion count')
   source=prior_index.get(path,{})
   close(f['known_stock_program_floor'],source.get('program_units',0),'Stock program floor')
   close(f['known_stock_declarative_floor'],max(0,source.get('declarative_units',0)-f['excludes']['declarative_units']),'Stock declarative floor')
   for k in ('program','declarative'):
    number(f['available_'+k],'available '+k);number(f['known_stock_'+k+'_floor'],'Stock floor')
    require(f['known_stock_'+k+'_floor']<=f['available_'+k],'Stock floor exceeds source')
   weights=f['attribution']
   require(set(weights)=={'lower','central','upper'},'Stock attribution levels')
   for w in weights.values():number(w,'Stock attribution',maximum=1)
   require(weights['lower']<=weights['central']<=weights['upper'],'Stock attribution order')
   nodes=node_set(f['whole_method_nodes'])
   close(len(nodes),f['whole_method_program_units'],'Stock whole-method count')
   require(f['additional_framework_assimilation']==0,'Generic framework funded twice')
  for kind,path in spec['chains'][p].items():chains[p,kind]=documents[path]
 # All recorded MD deductions must belong to a selected native file.
 require(set(md)<= {(p,path) for p in products for path in indices[p]},'Unknown MD node exclusion')
 def bank_for(p):
  index=indices[p];extras={f['path']:f for f in ni['stock_dependency_fragments'][p]};bank={}
  for label,kind in [('correction_chain','correction'),('reservation_chain','reservation')]:
   pieces=[];seen={}
   for f in chains[p,kind]['files']:
    if f['role']=='framework_reused':continue
    row=index.get(f['path']) or extras[f['path']]
    require(f['sha256']==row['sha256'],'Stock chain source mismatch')
    nodes=node_set(f['counted_nodes'])
    require(not nodes & seen.get(f['path'],set()),'Duplicate Stock chain instruction')
    seen.setdefault(f['path'],set()).update(nodes)
    if f['path'].endswith('.java'):
     stem=f['path'].split('/')[-1][:-5]
     ctors=[m for m in f['methods'] if m['name']==stem]
     nodes={n for n in nodes if not any(m['start']<=n[1]<=n[2]<=m['end'] for m in ctors)}
    nodes-=md.get((p,f['path']),set())
    floor=len(nodes & known[p].get(f['path'],set()))
    pieces.append(max(floor,len(nodes)*row['attribution']['central']))
   bank[label]=sum(pieces)
  for label,component in [('positions_component','K2'),('inventory_component','K3')]:
   bank[label]=0
   for path,f in index.items():
    if component not in f['components']:continue
    nodes=node_set(f['whole_method_nodes'])-md.get((p,path),set())
    floor=len(nodes & known[p].get(path,set()))
    bank[label]+=max(floor,len(nodes)*f['attribution']['central'])
  return bank
 E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum'])
 def effort(units):
  return formula('cocomo_effort',A=c['A'],KSLOC=units/1000,E=E,EM=c['other_EM'],SCED=c['SCED'],
   month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor'])
 macros=unique(ni['complement_module_analogies'],'id','Stock complement')
 schemas=unique(ni['schemas'],'name','Stock schema')
 for sc in schemas.values():
  require(sc['package'] in macros and len(sc['fields'])==len(set(sc['fields'])) and type(sc['new_model']) is bool and type(sc['view']) is bool,'Stock schema contract')
 oldrows=unique(baseline['rows'],'id','Stock baseline')
 require(set(oldrows)==set(products),'Stock baseline references')
 rows=[];detail={};work=[]
 for p in products:
  core_p=sum(max(f['available_program']*f['attribution']['central'],f['known_stock_program_floor']) for f in indices[p].values())
  core_d=sum(max(f['available_declarative']*f['attribution']['central'],f['known_stock_declarative_floor']) for f in indices[p].values())
  # Dependency fragments are a union of native business methods, not entire framework files.
  extras=unique(ni['stock_dependency_fragments'][p],'path','Stock dependency fragment')
  for path,x in extras.items():
   require(path not in indices[p],'Stock fragment counted twice')
   nodes=set()
   for kind in ('correction','reservation'):
    for f in chains[p,kind]['files']:
     if f['path']==path and f['role']!='framework_reused':
      require(f['sha256']==x['sha256'],'Stock fragment source')
      nodes|=node_set(f['counted_nodes'])
   require(nodes==node_set(x['counted_nodes']),'Stock fragment union')
   close(len(nodes),x['program_units'],'Stock fragment measure')
   for w in x['attribution'].values():number(w,'fragment attribution',maximum=1)
   core_p+=len(nodes)*x['attribution']['central']
  bank=bank_for(p);template=ni['schema_templates'][p];blocks=[]
  for v in template.values():
   if type(v) in (int,float):number(v,'native declaration template')
  for macro in macros.values():
   for key in ('lower','central','upper'):number(macro[key],'Stock module fraction')
   require(macro['lower']<=macro['central']<=macro['upper'],'Stock module fraction order')
   pu=0;du=0
   scaffold=ni['new_module_scaffolding'][p]
   require(scaffold['path'] in indices[p] and scaffold['sha256']==indices[p][scaffold['path']]['sha256'],'Stock scaffold provenance')
   number(scaffold['program_units_per_new_service_module'],'service scaffold')
   pu=formula('module_analogy',reference_units=bank[macro['analogue']],fraction=macro['central'],scaffold_units=scaffold['program_units_per_new_service_module'])
   for sc in schemas.values():
    if sc['package']!=macro['id']:continue
    n=len(sc['fields']);new=int(sc['new_model']);view=int(sc['view'])
    pu+=n*template['program_per_field']+new*template.get('program_per_new_model',0)
    du+=n*template['declarations_per_field']+new*template['per_new_model']+view*(n*template['view_field']+template['view_model'])
   blocks.append(dict(id=macro['id'],program_units=pu,declarative_units=du,analogue_units=bank[macro['analogue']]))
  config=sum(number(x,'Stock configuration') for x in ni['configuration_units'].values())
  cp=sum(x['program_units'] for x in blocks);cd=sum(x['declarative_units'] for x in blocks)+config
  base=formula('equivalent_size',new_program=core_p,new_declarative=core_d,w=1,AAM=0,reused_program=0,reused_declarative=0)
  extra=formula('equivalent_size',new_program=cp,new_declarative=cd,w=1,AAM=0,reused_program=0,reused_declarative=0)
  common=effort(base);total=effort(base+extra);old=oldrows[p]
  for actual,expected,name in [(base,old['base_equivalent_units'],'Stock base size'),(extra,old['Flow_complements_equivalent_units'],'Stock complement size'),
    (common,old['base_common_jh'],'Stock base effort'),(total,old['total_stock_jh'],'Stock total effort'),(total-common,old['Flow_complements_marginal_jh'],'Stock marginal effort')]:
   close(actual,expected,name)
  for name,units in bank.items():close(units,old['detail']['analogue_bank'][name]['program_units'],'Stock analogue reconstruction')
  rows.append(dict(id=p,label=spec['reference_labels'][p],jh=total,common_jh=common,complements_jh=total-common))
  detail[p]=dict(core_program=core_p,core_declarative=core_d,complement_program=cp,complement_declarative=cd,
   bank=bank,blocks=blocks,configuration=config)
  work.extend(('stock_module',p+'/'+x['id'],x['id'],x['program_units']+x['declarative_units']) for x in blocks)
 cosmic=d['cosmic'];groups=unique(cosmic['groups'],'id','Stock COSMIC group')
 processes=unique(cosmic['processes'],'id','Stock COSMIC process');moves=Counter();ids=set()
 require(set(cosmic['capability_coverage'])==set(spec['capabilities']),'Stock COSMIC capability coverage')
 for process in processes.values():
  require(process['functional_user'] and process['trigger'],'Missing Stock functional boundary')
  keys=set();counts=Counter()
  require(set(process['capabilities'])<=set(spec['capabilities']),'Stock COSMIC scope')
  for movement in process['movements']:
   key=(movement['type'],movement['group'])
   require(key not in keys and movement['id'] not in ids,'Duplicate Stock COSMIC movement')
   keys.add(key);ids.add(movement['id'])
   require(movement['type'] in ('E','R','W','X') and movement['group'] in groups and movement['cfp']==1,'Invalid Stock COSMIC movement')
   counts[movement['type']]+=1
  require(counts['E']>0 and counts['W']+counts['X']>0,'Incomplete Stock functional process')
  for k in ('E','R','W','X'):close(counts[k],process['count'][k],'Stock movement subtotal')
  close(sum(counts.values()),process['count']['CFP'],'Stock functional subtotal')
  moves.update(counts)
 cfp=sum(moves.values());close(cfp,cosmic['result']['CFP'],'Stock functional total')
 for k in ('E','R','W','X'):close(moves[k],cosmic['result']['movements'][k],'Stock movement total')
 source=d['productivity_source']
 close(cosmic['result']['hours_per_CFP'],source['benchmark']['main']['hours_per_cfp'],'Stock benchmark rate')
 close(cosmic['result']['day_hours'],source['units']['jh_hours'],'Stock benchmark convention')
 close(cosmic['result']['day_hours'],c['day_hours'],'Stock JH convention')
 require(cosmic['result']['factor']==1,'Stock benchmark size factor')
 functional=dict(CFP=cfp,hours_per_CFP=cosmic['result']['hours_per_CFP'],factor=1,day_hours=c['day_hours'])
 selected=detail[allocation['selected_reference']]
 return dict(cocomo=c,allocation=allocation,rows=rows,functional=functional,activity_source=d['activities']['cocomo'],work_items=work,
  trace=dict(recorded_files=sum(len(v) for v in indices.values())+sum(len(v) for v in ni['stock_dependency_fragments'].values()),
   component_files=sum(len(v) for v in indices.values()),blocks=len(macros),refined_blocks=0,method_samples=0,
   complement_units=selected['complement_program']+selected['complement_declarative'],
   complement_parts=selected,processes=len(processes),groups=len(groups),CFP=cfp,movements=dict(moves),
   reuse_factor=0,stock_sizes=detail))
