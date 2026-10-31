"""Frozen source inventory for an audit; no writes to active model or old evidence."""
from pathlib import Path
import json,hashlib,base64,gzip,re,sys,importlib.util
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent;T=R/'tmp/cocomo-count-audit'
def load(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def product(repo):return 'erpnext' if repo=='frappe' else 'axelor' if repo in ('platform','studio') else repo
def main():
 md=load('audits/2026-10-30-master-data-comparable-reuse/measurements.json');ar=load('audits/2026-10-30-core-adoption-09/archives.json')
 docs={n:json.loads(gzip.decompress(base64.b64decode(e['data']))) for n,e in ar['documents'].items()};repos=docs['common_measures']['specification']['repos'];inventory={}
 def add(row,why):
  repo=row.get('repo');path=row.get('root_path') or (str(Path(repos[repo]['root'])/row['path']).replace('\\','/'))
  if path in inventory:inventory[path]['uses'].add(why);return
  f=R/path;raw=f.read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha==row['sha256'],path
  inventory[path]=dict(path=path,repo=repo,product=row.get('product',product(repo)),sha256=sha,uses={why})
 for f in md['files']:add(f,'master-data/'+f['treatment'])
 for f in docs['catalog']['sources']+docs['common_measures']['sources']:add(f,'remaining-components')
 stock=load('audits/2026-10-30-stock-adoption-10/inputs.json')
 for p,path in stock['perimeters'].items():
  for f in load(path)['files']:add(f,'stock/native')
 for p,chains in stock['chains'].items():
  for kind,path in chains.items():
   for f in load(path)['files']:add(dict(f,product=p),'stock/'+kind)
 for s in load('audits/2026-10-30-master-data-spring-flow/analogues.json')['samples']+load('audits/2026-10-30-master-data-spring-reprise/method-measures.json'):
  path=s['path'];repo=next(k for k,v in repos.items() if path.startswith(v['root']+'/'));add(dict(s,root_path=path,repo=repo),'master-data/analogue')
 staged=T/'sources';staged.mkdir(exist_ok=True);rows=[];files=[]
 for i,(path,row) in enumerate(sorted(inventory.items())):
  p=R/path;text=p.read_text(encoding='utf-8-sig');row['uses']=sorted(row['uses']);row['extension']=p.suffix
  if p.suffix=='.py':
   inside=False;lines=text.splitlines()
   for j,line in enumerate(lines):
    if '# begin: auto-generated types' in line:inside=True
    if inside:lines[j]=''
    if '# end: auto-generated types' in line:inside=False
   text='\n'.join(lines)+'\n'
  ext='.js' if p.suffix in ('.jsx','.ts','.tsx') else p.suffix
  dest=staged/(f'f{i:04d}'+ext);row['staged']=str(dest.relative_to(R)).replace('\\','/');row['staged_sha256']=hashlib.sha256(text.encode()).hexdigest()
  dest.write_text(text,encoding='utf-8');rows.append(row)
  if ext in ('.py','.java','.js','.xml','.html'):files.append(str(dest))
 save(O/'source-inventory.json',dict(repos=repos,files=rows,policy='Only generated Python type blocks removed, same as baseline. No generated Java added. TS/JSX tokenized by legacy JavaScript counter; review required. JSON/CSV not supported by UCC and retain local directive convention.'))
 (T/'fileList.txt').write_text('\n'.join(files)+'\n',encoding='utf-8');print(json.dumps(dict(unique_sources=len(rows),ucc_files=len(files),by_product={p:sum(r['product']==p for r in rows) for p in ['erpnext','odoo','tryton','axelor']})))
if __name__=='__main__':main()
