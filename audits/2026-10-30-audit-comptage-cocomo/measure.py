"""Map independent USC logical statements to the frozen AST scopes; local declarative profiles stay explicit."""
from pathlib import Path
from collections import defaultdict,Counter
import ast,csv,gzip,hashlib,importlib.util,json,re,sys
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent;T=R/'tmp/cocomo-count-audit'
sys.path.insert(0,str(R/'tmp/master-data-native-23/parser-deps'))
spec=importlib.util.spec_from_file_location('old_counter',R/'audits/2026-10-30-master-data-natif/measure.py');counter=importlib.util.module_from_spec(spec);spec.loader.exec_module(counter)
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def atoms(path):
 text=path.read_text(encoding='utf-8-sig');result=[]
 if path.suffix=='.py':
  ls=text.splitlines();inside=False
  for i,line in enumerate(ls):
   if '# begin: auto-generated types' in line:inside=True
   if inside:ls[i]=''
   if '# end: auto-generated types' in line:inside=False
  text=re.sub(r'(?m)^(\s*)except ([\w.]+(?:,\s*[\w.]+)+):',r'\1except (\2):','\n'.join(ls))
 if path.suffix=='.py':
  tree=ast.parse(text)
  for n in ast.walk(tree):
   if not isinstance(n,ast.stmt) or isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):continue
   start=min([n.lineno]+[d.lineno for d in getattr(n,'decorator_list',[])])
   result.append(dict(kind=type(n).__name__,start=n.lineno,end=n.end_lineno,col=n.col_offset,end_col=n.end_col_offset,cover_start=start))
 elif path.suffix in counter.PARSERS:
  blob=text.encode();tree=counter.PARSERS[path.suffix].parse(blob);assert not tree.root_node.has_error,str(path)
  for n in counter.walk(tree.root_node):
   t=n.type;extra=counter.JAVA_EXTRA if path.suffix=='.java' else counter.JS_EXTRA
   if (t.endswith('_statement') and t not in {'empty_statement','export_statement'}) or t in extra:
    result.append(dict(kind=t,start=n.start_point.row+1,end=n.end_point.row+1,col=n.start_point.column,end_col=n.end_point.column,cover_start=n.start_point.row+1))
 return result

def main():
 inv=load(O/'source-inventory.json');ucc=defaultdict(list)
 for line in (T/'ucc-final-trace.tsv').open(encoding='utf-8'):
  file,number,code=line.rstrip('\n').split('\t');ucc[Path(file).name].append(dict(line=int(number),code=bytes.fromhex(code).decode('utf-8',errors='replace')))
 reports=[];maps={};mapping_totals=Counter()
 for row in inv['files']:
  original=R/row['path'];staged=R/row['staged'];ext=row['extension'];text=staged.read_text(encoding='utf-8');entries=ucc.get(staged.name,[])
  if ext in counter.PARSERS or ext=='.py':
   # Parse original syntax with only the same type-block/except normalization as baseline.
   parse_path=original
   nodes=atoms(parse_path);declarative=counter.measure(original)['declarative_units']
   old=len(nodes);owner={};weights=[0]*len(nodes);orphans=[]
   for i,n in enumerate(nodes):
    for line in range(n['cover_start'],n['end']+1):
     score=(n['end']-n['cover_start'],-n['start'],n['col'])
     if line not in owner or score<owner[line][0]:owner[line]=(score,i)
   for e in entries:
    line=e['line']
    if line in owner:weights[owner[line][1]]+=1
    else:orphans.append(e)
   # Unsupported JSX/TS dialects are measured but not silently promoted to COCOMO reference counts.
   supported=ext in ('.py','.java','.js')
   for n,w in zip(nodes,weights):n['ucc_weight']=w
   maps[row['path']]=dict(nodes=nodes,orphans=orphans,old_program=old,ucc_program=len(entries),old_declarative=declarative,ucc_supported=supported)
   mapping_totals['mapped']+=sum(weights);mapping_totals['unmapped']+=len(orphans)
   report=dict(path=row['path'],product=row['product'],extension=ext,sha256=row['sha256'],old_program_units=old,old_declarative_units=declarative,ucc_logical_statements=len(entries),mapped_statements=sum(weights),unmapped_statements=len(orphans),supported_for_impact=supported)
  else:
   if ext=='.csv':old=sum(1 for _ in csv.DictReader(text.splitlines()));declarative=old
   else:
    d=counter.measure(original);old=d['program_units'];declarative=d['declarative_units']
   report=dict(path=row['path'],product=row['product'],extension=ext,sha256=row['sha256'],old_program_units=old,old_declarative_units=declarative,ucc_logical_statements=len(entries),supported_for_impact=False,reason='Local generator/security directive profile retained; raw USC XML/HTML count shown separately.')
   maps[row['path']]=dict(nodes=[],orphans=[],old_program=old,ucc_program=len(entries),old_declarative=declarative,ucc_supported=False)
  reports.append(report)
 with gzip.open(T/'node-maps.json.gz','wt',encoding='utf-8') as f:json.dump(maps,f,ensure_ascii=False,separators=(',',':'))
 totals={}
 for p in ['erpnext','odoo','tryton','axelor']:
  rr=[r for r in reports if r['product']==p and r['supported_for_impact']];totals[p]=dict(files=len(rr),old=sum(r['old_program_units'] for r in rr),ucc=sum(r['ucc_logical_statements'] for r in rr),unmapped=sum(r.get('unmapped_statements',0) for r in rr))
 (O/'measurements.json').write_text(json.dumps(dict(files=reports,totals=totals,mapping=dict(mapping_totals)),ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(dict(totals=totals,mapping=dict(mapping_totals)),ensure_ascii=False))
if __name__=='__main__':main()
