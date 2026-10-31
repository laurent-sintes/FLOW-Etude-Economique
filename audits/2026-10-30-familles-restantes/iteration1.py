"""Iteration 1: pinned code portfolios, native scope and measured symbols; no effort from raw size."""
from pathlib import Path
from collections import Counter
import ast,hashlib,importlib.util,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=importlib.util.spec_from_file_location('measure_native',ROOT/'audits/2026-10-30-master-data-natif/measure.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def nodes_for_method(n):
 if isinstance(n,ast.AST):
  return [dict(kind=type(x).__name__,start=x.lineno,end=getattr(x,'end_lineno',x.lineno),col=x.col_offset,end_col=getattr(x,'end_col_offset',x.col_offset)) for x in ast.walk(n) if isinstance(x,ast.stmt) and not (isinstance(x,ast.Expr) and isinstance(x.value,ast.Constant) and isinstance(x.value.value,str))]
 return [dict(kind=x.type,start=x.start_point.row+1,end=x.end_point.row+1,col=x.start_point.column,end_col=x.end_point.column) for x in m.walk(n) if (x.type.endswith('_statement') and x.type!='empty_statement') or x.type in m.JAVA_EXTRA]
def symbols(path):
 text=path.read_text(encoding='utf-8-sig');lines=text.splitlines();out=[]
 if path.suffix=='.py':
  norm=re.sub(r'(?m)^(\s*)except ([\w.]+(?:,\s*[\w.]+)+):',r'\1except (\2):',text)
  tree=ast.parse(norm)
  def visit(node,owner=''):
   for child in ast.iter_child_nodes(node):
    if isinstance(child,ast.ClassDef):visit(child,owner+child.name+'.')
    elif isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef)):
     out.append(dict(name=owner+child.name,start=child.lineno,end=child.end_lineno,nodes=nodes_for_method(child),
      source='\n'.join(lines[child.lineno-1:child.end_lineno])))
    else:visit(child,owner)
  visit(tree)
 else:
  raw=text.encode();tree=m.PARSERS['.java'].parse(raw)
  assert not tree.root_node.has_error,str(path)
  for node in m.walk(tree.root_node):
   if node.type!='method_declaration':continue
   name=node.child_by_field_name('name')
   out.append(dict(name=raw[name.start_byte:name.end_byte].decode(),start=node.start_point.row+1,end=node.end_point.row+1,
    nodes=nodes_for_method(node),source='\n'.join(lines[node.start_point.row:node.end_point.row+1])))
 return sorted(out,key=lambda x:x['start'])
def main():
 plan=read(OUT/'plan.json');cache={};total=set()
 for f in plan['families']:
  for ref in f['source_candidates']:
   if ref['path']=='modules/res_user_role/user.py':ref['path']='modules/user_role/res.py'
  folder=OUT/f['slug'];folder.mkdir(exist_ok=True)
  refs=[]
  for ref in f['source_candidates']:
   key=(ref['repo'],ref['path'])
   if key not in cache:
    repo=plan['repos'][ref['repo']];p=ROOT/repo['root']/ref['path'];raw=p.read_bytes()
    pin=subprocess.run(['C:/Program Files/Git/cmd/git.exe','-C',str(ROOT/repo['root']),'show',repo['commit']+':'+ref['path']],capture_output=True,check=True).stdout
    assert raw.replace(b'\r\n',b'\n')==pin.replace(b'\r\n',b'\n'),str(p)
    cache[key]=dict(repo=ref['repo'],path=ref['path'],root_path=p.relative_to(ROOT).as_posix(),sha256=sha(p),
     commit=repo['commit'],url='https://github.com/'+repo['repository']+'/blob/'+repo['commit']+'/'+ref['path'],
     pinned_blob_verified=True,whole_file=m.measure(p),methods=symbols(p))
   r=dict(cache[key],prior_evidence=ref.get('prior_evidence'),prior_observed=ref.get('observed'),prior_limit=ref.get('limit'))
   if key not in {(x['repo'],x['path']) for x in refs}:refs.append(r)
   total.add(key)
  result=dict(family=f['id'],slug=f['slug'],iteration=1,status='sources_et_frontiere_instruites',
   scope=f['native_capabilities'],sources=refs,raw_counts_are_not_effort=True,proposed_jh=None,adopted_cumulative_jh=1940,
   source_note='Lecture statique des sources figées, mesures syntaxiques reproductibles. Les méthodes déléguées et les comportements hors périmètre restent à isoler.')
  save(folder/'iteration-1.json',result)
  print(json.dumps(dict(family=f['slug'],files=len(refs),java_methods=[dict(name=x['name'],units=len(x['nodes'])) for r in refs if r['repo']=='axelor' for x in r['methods'] if re.search(f['method_pattern'],x['name'],re.I)][:9]),ensure_ascii=False))
 plan['status']='iteration_1_complete'
 save(OUT/'plan.json',plan)
 save(OUT/'sources-iteration-1.json',dict(unique_files=len(total),files=[{k:v for k,v in r.items() if k!='methods'} for r in cache.values()],no_historical_effort_reused=True))
 print('UNIQUE_PINNED_FILES',len(total))
if __name__=='__main__':main()
