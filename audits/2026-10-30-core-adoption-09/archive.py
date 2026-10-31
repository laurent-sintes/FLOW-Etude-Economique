"""Frozen self-contained archives of the adopted opportunity calculation."""
from pathlib import Path
import json,hashlib,gzip,base64
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def main():
 refs={
 'proposal_inputs':'audits/2026-10-30-chiffrage-complet/iteration-08/inputs.json',
 'proposal_results':'audits/2026-10-30-chiffrage-complet/iteration-08/results.json',
 'common_measures':'audits/2026-10-30-mecanismes-partages-04/measurements.json',
 'common_adjustment':'audits/2026-10-30-mecanismes-partages-04/reuse-adjustment.json',
 'funding':'audits/2026-10-30-chiffrage-complet/iteration-08/funding.json',
 'catalog':'audits/2026-10-30-chiffrage-complet/iteration-06/source-catalog.json'
 }
 docs={}
 for name,path in refs.items():
  raw=(ROOT/path).read_bytes()
  docs[name]=dict(path=path,sha256=hashlib.sha256(raw).hexdigest(),encoding='gzip+base64',data=base64.b64encode(gzip.compress(raw,mtime=0)).decode('ascii'))
 out=dict(format='flow-estimation-evidence-archive-v1',documents=docs,note='Contenus complets figés ; compression de stockage sans changement des mesures. Aucun checkout OSS nécessaire au calcul ou à la reprise depuis le téléchargement.')
 (OUT/'archives.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Frozen archive:',(OUT/'archives.json').stat().st_size,'bytes; full original inputs included.')
if __name__=='__main__':main()
