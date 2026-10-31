"""Capture and verify the transitive file dependencies of the opportunity report."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(check=False):
 if check:
  old=read(OUT/'provenance.json')
  for path,h in old['files'].items():
   if sha(ROOT/path)!=h:raise ValueError('Changed evidence: '+path)
  print(str(len(old['files']))+' dependency hashes verified.');return
 d=read(OUT/'iteration-08/inputs.json');catalog=read(ROOT/d['source_catalog_ref']);common=read(ROOT/d['common_measurements_ref'])
 paths={p.relative_to(ROOT).as_posix() for p in OUT.rglob('*') if p.is_file() and p.name!='provenance.json' and '__pycache__' not in p.parts}
 paths|={x['root_path'] for x in catalog['sources']+common['sources']}
 paths|=set(read(OUT/'baseline.json')['protected'])
 paths|=set(common['dependency_hashes'])
 paths|={d['common_results_ref'],d['common_measurements_ref'],d['counter_ref'],'source/fondamentaux.yaml','tools/estimation_calculation.py','tools/model_context.py',
 'audits/2026-10-30-propriete-stock-calcul-02/inputs.json','audits/2026-10-30-stock-consolidation-09/inputs.json',
 'audits/2026-10-30-master-data-calcul/repartitions-sources.json','audits/2026-10-30-familles-restantes/plan.json',
 'audits/2026-10-30-mecanismes-partages-04/specification.json','audits/2026-10-30-mecanismes-partages-04/prepare.py'}
 paths|={f'audits/2026-10-30-familles-restantes/{f["slug"]}/cosmic-2.json' for f in d['families']}
 proof=dict(files={p:sha(ROOT/p) for p in sorted(paths)},rule_authority='source/fondamentaux.yaml#estimation_model',native_revisions=catalog['repos'],scope='Transitive evidence files including active protected sources; dependencies outside the audit are never edited.')
 (OUT/'provenance.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(str(len(paths))+' dependency hashes recorded.')
if __name__=='__main__':main('--check' in sys.argv)
