"""Normalize Python f-string literal contents for the legacy USC lexer, preserving statements and line positions."""
from pathlib import Path
import ast,json,hashlib,subprocess,os,time,re
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent;T=R/'tmp/cocomo-count-audit'
def count(tree):return sum(isinstance(n,ast.stmt) and not(isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str)) for n in ast.walk(tree))
def main():
 inv=json.loads((O/'source-inventory.json').read_text(encoding='utf-8'));changes=[]
 for row in inv['files']:
  p=R/row['staged']
  if p.suffix!='.py':continue
  text=p.read_text(encoding='utf-8');text=re.sub(r'(?m)^(\s*)except ([\w.]+(?:,\s*[\w.]+)+):',r'\1except (\2):',text)
  tree=ast.parse(text);ranges=[]
  def visit(n):
   if isinstance(n,ast.JoinedStr):ranges.append(n);return
   for ch in ast.iter_child_nodes(n):visit(ch)
  visit(tree)
  if not ranges:continue
  lines=text.encode().splitlines(keepends=True);offset=[0]
  for l in lines:offset.append(offset[-1]+len(l))
  blob=bytearray(text.encode())
  for n in ranges:
   a=offset[n.lineno-1]+n.col_offset;b=offset[n.end_lineno-1]+n.end_col_offset;replacement=bytearray(32 if c not in (10,13) else c for c in blob[a:b]);replacement[:3]=b'"x"';blob[a:b]=replacement
  changed=blob.decode();assert len(changed.splitlines())==len(text.splitlines());assert count(ast.parse(changed))==count(tree)
  p.write_text(changed,encoding='utf-8');changes.append(dict(path=row['path'],fstrings=len(ranges),before_sha256=hashlib.sha256(text.encode()).hexdigest(),after_sha256=hashlib.sha256(blob).hexdigest(),ast_statement_counts_unchanged=True))
 (O/'lexer-normalizations.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
 out=T/'ucc-normalized';out.mkdir(exist_ok=True);trace=T/'ucc-normalized-trace.tsv';assert not trace.exists();env=dict(os.environ,FLOW_UCC_TRACE=str(trace));t=time.perf_counter()
 args=[str(T/'UCC.exe'),'-i1',str(T/'fileList.txt'),'-outdir',str(out),'-unified','-nodup','-nocomplex','-trunc','0','-noheader'];r=subprocess.run(args,cwd=T,env=env,capture_output=True,text=True,input='\n',timeout=360)
 (T/'ucc-normalized-run.log').write_text(r.stdout+r.stderr,encoding='utf-8');print('NORMALIZED_FILES',len(changes),'EXIT',r.returncode,'SECONDS',round(time.perf_counter()-t,2));print((r.stdout+r.stderr)[-550:]);assert r.returncode==0
if __name__=='__main__':main()
