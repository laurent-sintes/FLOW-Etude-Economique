"""Independent manual examples, USC instrumentation parity and exact scoped replay checks."""
from pathlib import Path
import subprocess,os,csv,json,hashlib,gzip,sys
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent;T=R/'tmp/cocomo-count-audit'
def csvrows(path):
 result={}
 for row in csv.reader(path.read_text(encoding='utf-8-sig').splitlines()):
  if len(row)==11 and row[0].isdigit() and row[9]=='CODE':result[Path(row[10]).name]=int(row[7])
  if len(row)==49 and row[0].isdigit() and row[47]=='CODE':result[Path(row[48].replace('\\\\','\\')).name]=int(row[45])
 return result

def main():
 cases=[('ForAndIf.java','package demo;\nimport java.util.List;\nclass Sample {\n int x;\n void run(boolean flag) {\n  if(flag) {x++;} else {x--;}\n  for(int i=0;i<2;i++) {x+=i;}\n }\n}\n',10,'USC Java rules R01,R03,R04,R05, pp.6-11'),('EmptyStatement.java','class Empty { void run() { ; } }\n',3,'USC Java R03 includes an empty semicolon statement'),('Comments.java','// ignored\n\nclass Demo {} // ignored\n',1,'COCOMO checklist excludes comments and blanks'),('TryExcept.py','import os\nclass Demo:\n @staticmethod\n def run(value):\n  try:\n   if value:\n    return 1\n   else:\n    return 0\n  except ValueError:\n   return -1\n',9,'USC 2018 Python implementation: decorator counted, try prefix grouped with following statement; explicit local profile'),('Model.xml','<?xml version="1.0"?>\n<domain-models>\n <module name="test"/>\n <entity name="Case">\n  <string name="reference"/>\n  <integer name="version"/>\n </entity>\n</domain-models>\n',6,'USC XML R01,R02,R03: directive, root, module, entity, two fields')]
 folder=T/'fixtures';folder.mkdir(exist_ok=True);paths=[]
 for name,code,expect,ref in cases:p=folder/name;p.write_text(code,encoding='utf-8');paths.append(str(p))
 fl=T/'fixtures.txt';fl.write_text('\n'.join(paths)+'\n',encoding='utf-8');runs=[]
 for exe in ['UCC-original.exe','UCC.exe']:
  out=T/('fixtures-'+exe);out.mkdir(exist_ok=True);r=subprocess.run([str(T/exe),'-i1',str(fl),'-outdir',str(out),'-unified','-nodup','-nocomplex','-noheader'],cwd=T,input='\n',capture_output=True,text=True,timeout=45);assert r.returncode==0;runs.append(csvrows(out/'TOTAL_outfile.csv'))
 assert runs[0]==runs[1],'Instrumentation changed USC counts'
 results=[dict(file=name,expected=expect,observed=runs[0][name],reference=ref,passed=runs[0][name]==expect) for name,code,expect,ref in cases]
 impact=json.loads((O/'impact.json').read_text(encoding='utf-8'));assert impact['master_data_scope_fallbacks']==[];assert impact['totals']['axelor']['old_rounded_jh']==4160
 totals=csvrows(T/'ucc-normalized/TOTAL_outfile.csv');totals.update(csvrows(T/'ucc-single/TOTAL_outfile.csv'));counts={}
 for line in (T/'ucc-final-trace.tsv').open(encoding='utf-8'):name=Path(line.split('\t',1)[0]).name;counts[name]=counts.get(name,0)+1
 inventory=json.loads((O/'source-inventory.json').read_text(encoding='utf-8'))['files'];matched=0;mismatches=[]
 for f in inventory:
  if f['extension'] not in ('.py','.java','.js'):continue
  name=Path(f['staged']).name
  if totals.get(name,0)!=counts.get(name,0):mismatches.append(dict(file=f['path'],csv=totals.get(name),trace=counts.get(name)))
  else:matched+=1
 data=dict(fixtures=results,original_and_instrumented_counter_equal=True,program_file_trace_totals_matched=matched,trace_mismatches=mismatches,exact_baseline_replay_checks=impact['replay_baseline_checks'],MD_scope_fallbacks=0,retained_total_unchanged_in_replay=4160,passed=all(r['passed'] for r in results) and not mismatches)
 (O/'verification.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(data,ensure_ascii=False));assert data['passed']
if __name__=='__main__':main()
