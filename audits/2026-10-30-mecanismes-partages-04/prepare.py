"""Measure native atoms with the adopted counter and assign common base work once."""
from pathlib import Path
from collections import defaultdict
import ast,hashlib,importlib.util,json,re,subprocess,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
from model_context import model_session
from estimation_calculation import calculate
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sp=importlib.util.spec_from_file_location('native_counter',ROOT/'audits/2026-10-30-master-data-natif/measure.py');counter=importlib.util.module_from_spec(sp);sp.loader.exec_module(counter)
def load_file(repo,path,spec):
 root=ROOT/spec['repos'][repo]['root'];original=path
 if '/' not in path:
  choices=[p for p in root.rglob(path) if '/src/test/' not in p.as_posix()]
  if len(choices)!=1:raise ValueError(('Ambiguous source',repo,path,[p.as_posix() for p in choices]))
  path=choices[0].relative_to(root).as_posix()
 p=root/path;raw=p.read_bytes();pin=spec['repos'][repo]['commit']
 frozen=subprocess.run(['C:/Program Files/Git/cmd/git.exe','-C',str(root),'show',pin+':'+path],check=True,capture_output=True).stdout
 assert raw.replace(b'\r\n',b'\n')==frozen.replace(b'\r\n',b'\n'),path
 text=raw.decode('utf-8-sig');lines=text.splitlines();atoms=[];methods=[]
 def add(k,start,end,col,endcol,name='',struct=False):
  atoms.append(dict(key=f'{k}:{start}:{end}:{col}:{endcol}',kind=k,start=start,end=end,col=col,end_col=endcol,name=name,structural=struct))
 if p.suffix=='.py':
  inside=False;norm=[]
  for line in lines:
   if '# begin: auto-generated types' in line:inside=True
   norm.append('' if inside else line)
   if '# end: auto-generated types' in line:inside=False
  normalized=re.sub(r'(?m)^(\s*)except ([\w.]+(?:,\s*[\w.]+)+):',r'\1except (\2):','\n'.join(norm))
  tree=ast.parse(normalized)
  def visit(parent,owner=''):
   for child in ast.iter_child_nodes(parent):
    if isinstance(child,ast.ClassDef):visit(child,owner+child.name+'.')
    elif isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef)):
     methods.append(dict(name=owner+child.name,simple=child.name,start=child.lineno,end=child.end_lineno,source='\n'.join(lines[child.lineno-1:child.end_lineno]),node=child))
    else:visit(child,owner)
  visit(tree)
  for n in ast.walk(tree):
   if not isinstance(n,ast.stmt):continue
   if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):continue
   name=''
   if isinstance(n,(ast.Assign,ast.AnnAssign)):
    targets=n.targets if isinstance(n,ast.Assign) else [n.target]
    name=' '.join(t.id for t in targets if isinstance(t,ast.Name))
   add(type(n).__name__,n.lineno,getattr(n,'end_lineno',n.lineno),n.col_offset,getattr(n,'end_col_offset',n.col_offset),name,
    isinstance(n,(ast.ClassDef,ast.Import,ast.ImportFrom)))
 elif p.suffix=='.java':
  blob=text.encode();tree=counter.PARSERS['.java'].parse(blob);assert not tree.root_node.has_error,path
  for n in counter.walk(tree.root_node):
   if n.type=='method_declaration':
    field=n.child_by_field_name('name')
    methods.append(dict(name=blob[field.start_byte:field.end_byte].decode(),simple=blob[field.start_byte:field.end_byte].decode(),
     start=n.start_point.row+1,end=n.end_point.row+1,source='\n'.join(lines[n.start_point.row:n.end_point.row+1]),node=n))
   if (n.type.endswith('_statement') and n.type!='empty_statement') or n.type in counter.JAVA_EXTRA:
    field_names=[]
    if n.type=='field_declaration':
     for v in n.named_children:
      if v.type=='variable_declarator':
       field=v.child_by_field_name('name')
       if field:field_names.append(blob[field.start_byte:field.end_byte].decode())
    add(n.type,n.start_point.row+1,n.end_point.row+1,n.start_point.column,n.end_point.column,' '.join(field_names),
        n.type in ('class_declaration','interface_declaration','package_declaration','import_declaration'))
 count=counter.measure(p)
 if p.suffix in ('.py','.java'):assert len(atoms)==count['program_units'],(path,len(atoms),count)
 return dict(repo=repo,product='erpnext' if repo=='frappe' else 'axelor' if repo in ('studio','platform') else repo,path=path,
  root_path=p.relative_to(ROOT).as_posix(),sha256=sha(p),commit=pin,
  url='https://github.com/'+spec['repos'][repo]['repository']+'/blob/'+pin+'/'+path,
  whole_measure=count,methods=methods,atoms=atoms,text=text,pinned_blob_equal=True)
def select(file,pattern,exclude):
 selected={m['name']+'@'+str(m['start']):m for m in file['methods'] if re.search(pattern,m['name'],re.I) and not re.search(exclude,m['name'],re.I)}
 # Resolve same-class or module-local helper calls; no cross-module completeness is implied.
 for _ in range(10):
  prior=len(selected)
  for m in list(selected.values()):
   owner=m['name'].rsplit('.',1)[0] if '.' in m['name'] else ''
   calls=set(re.findall(r'\b(?:self\.|cls\.|this\.)?(\w+)\s*\(',m['source']))
   for n in file['methods']:
    other=n['name'].rsplit('.',1)[0] if '.' in n['name'] else ''
    if n['simple'] in calls and (other==owner or other=='') and not re.search(exclude,n['name'],re.I):
     selected[n['name']+'@'+str(n['start'])]=n
  if len(selected)==prior:break
 chosen=[];source='\n'.join(m['source'] for m in selected.values());ranges=[(m['start'],m['end']) for m in selected.values()]
 for a in file['atoms']:
  within=any(m['start']<=a['start'] and a['end']<=m['end'] for m in file['methods'])
  inside=any(x<=a['start'] and a['end']<=y for x,y in ranges)
  context=not within and bool(selected) and (a['structural'] or (a['name'] and any(re.search(r'\b'+re.escape(n)+r'\b',source) for n in a['name'].split())))
  if inside or context:chosen.append(dict(a,selection='business_method' if inside else 'source_context'))
 return chosen,[{k:v for k,v in m.items() if k!='node'} for m in selected.values()]
def declaration_atoms(file,pattern):
 p=ROOT/file['root_path'];rows=[];selected=[]
 if p.suffix=='.json':
  d=read(p);assert d.get('doctype')=='DocType'
  rows=[dict(key='doctype',kind='DocType',name=d.get('name',''),keep=True)]
  for tag in ('fields','permissions','actions','links','states'):
   for i,item in enumerate(d.get(tag,[])):
    name=item.get('fieldname',item.get('label','')) if isinstance(item,dict) else str(item)
    rows.append(dict(key=f'{tag}:{i}',kind=tag,name=name,keep=tag!='fields' or bool(re.search(pattern,name,re.I))))
 elif p.suffix=='.xml':
  xml=ET.fromstring(p.read_text(encoding='utf-8-sig'))
  for i,n in enumerate(xml.iter()):
   tag=n.tag.split('}')[-1]
   if tag in counter.XML_WRAPPERS:continue
   name=n.attrib.get('name','')
   keep=tag in ('module','entity','index','extra-code') or not name or bool(re.search(pattern,name,re.I))
   rows.append(dict(key=f'{tag}:{i}',kind=tag,name=name,keep=keep))
 assert len(rows)==file['whole_measure']['declarative_units'],(file['path'],len(rows),file['whole_measure'])
 return [dict(r,selection='native_declaration') for r in rows if r['keep']],rows
def main():
 spec=read(OUT/'specification.json');cache={}
 # Resolve model names explicitly to avoid silently choosing an extension in another module.
 model_paths={n:f'axelor-{mod}/src/main/resources/domains/{n}' for mod,names in [('sale',['SaleOrder.xml','SaleOrderLine.xml']),('purchase',['PurchaseOrder.xml','PurchaseOrderLine.xml'])] for n in names}
 for key,items in spec['declarations'].items():
  for item in items:
   if item[0]=='axelor' and item[1] in model_paths:item[1]=model_paths[item[1]]
 def get(repo,path):
  key=repo,path
  if key not in cache:cache[key]=load_file(repo,path,spec)
  return cache[key]
 atom_owners={};bindings=[];banks={};declbanks={};base={}
 for mech in spec['mechanisms']:
  id=mech['id'];banks[id]={p:0. for p in ['erpnext','odoo','tryton','axelor']};declbanks[id]=dict.fromkeys(banks[id],0.);base[id]=dict.fromkeys(banks[id],0.)
  seen={p:set() for p in banks[id]}
  for repo,path,pattern in spec['bindings'].get(id,[]):
   file=get(repo,path);product=file['product'];atoms,methods=select(file,pattern,spec['exclusion_pattern'])
   chosen=[]
   for a in atoms:
    identity=(repo,file['path'],a['key'])
    if identity in seen[product]:continue
    seen[product].add(identity);basis_owner=atom_owners.get(identity)
    # Only actual base work is assigned; analogue reuse may reference the same source without buying it twice.
    if mech['base'] and basis_owner is None:atom_owners[identity]=id;basis_owner=id;base[id][product]+=1
    chosen.append(dict(a,base_owner=basis_owner))
   banks[id][product]+=len(chosen)
   bindings.append(dict(mechanism=id,repo=repo,product=product,path=file['path'],sha256=file['sha256'],kind='program',
    method_pattern=pattern,selected_methods=methods,atoms=chosen,selected_program_units=len(chosen),
    whole_program_units=file['whole_measure']['program_units'],excluded_program_units=file['whole_measure']['program_units']-len(chosen)))
  for repo,path in spec['declarations'].get(id,[]):
   file=get(repo,path);product=file['product'];atoms,universe=declaration_atoms(file,spec['field_pattern'])
   chosen=[]
   for a in atoms:
    identity=(repo,file['path'],'D:'+a['key']);basis_owner=atom_owners.get(identity)
    if mech['base'] and basis_owner is None:atom_owners[identity]=id;basis_owner=id;base[id][product]+=1
    chosen.append(dict(a,base_owner=basis_owner))
   declbanks[id][product]+=len(chosen)
   bindings.append(dict(mechanism=id,repo=repo,product=product,path=file['path'],sha256=file['sha256'],kind='declarative',
    atoms=chosen,selected_declarative_units=len(chosen),whole_declarative_units=len(universe),excluded_declarative_units=len(universe)-len(chosen)))
 with model_session():
  stock=calculate({'id':'stock-java-spring-v1'})
  stock_bank={p:v['bank']['correction_chain'] for p,v in stock['trace']['stock_sizes'].items()}
 for mech in spec['mechanisms']:
  if mech.get('provider')=='stock_correction':
   banks[mech['id']]=stock_bank.copy()
  assert all(v>0 for v in banks[mech['id']].values()),('Empty reference',mech['id'],banks[mech['id']])
 sources=[{k:v for k,v in f.items() if k not in ('text','methods','atoms')} for f in cache.values()]
 dependencies={p:sha(ROOT/p) for p in [spec['metrics_ref'],spec['allocation_ref'],spec['activity_ref'],'audits/2026-10-30-propriete-stock-calcul-02/inputs.json','audits/2026-10-30-stock-adoption-10/inputs.json']}
 record=dict(specification=spec,specification_sha256=sha(OUT/'specification.json'),sources=sources,bindings=bindings,
  bank_program_units=banks,bank_declarative_units=declbanks,base_units_owned_once=base,
  stock_correction_reference=stock_bank,adopted_metric_counter=spec['metrics_ref'],
  rule_refs='source/fondamentaux.yaml#estimation_model',dependency_hashes=dependencies,
  source_node_ownership=[dict(repo=r,path=p,atom=k,mechanism=m) for (r,p,k),m in atom_owners.items()],
  interpretation='Un atome de base a un propriétaire unique. Réutiliser un analogue pour un comportement nouveau distinct ne refacture pas le code de cet analogue. Les fractions de nouveau code restent des hypothèses.')
 save('measurements.json',record)
 save('input-freeze.json',dict(measurements_sha256=sha(OUT/'measurements.json'),specification_sha256=sha(OUT/'specification.json'),no_new_effort_computed=True,
  policy='Périmètre, choix des méthodes, attribution des structures et fractions de compléments figés avant calcul des nouveaux JH.'))
 print(json.dumps(dict(files=len(sources),mechanisms=len(spec['mechanisms']),java_banks={m:dict(program=banks[m]['axelor'],declarative=declbanks[m]['axelor'],base_owned=base[m]['axelor']) for m in banks}),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
