"""Verify the exported model and trial evidence without checkout reads during calculation."""
from pathlib import Path
from unittest.mock import patch
from copy import deepcopy
import json,yaml,hashlib,base64,gzip
from core_product_estimate import calculate
from estimation_calculation import evaluate_rule
R=Path.cwd();A=R/'audits/2026-10-31-essais-temporal-mining'
path=R/'tmp/model-download/flow-modele-metier.yaml';raw=path.read_bytes();doc=yaml.load(raw,Loader=getattr(yaml,'CSafeLoader',yaml.SafeLoader));model=doc['model'];rules={r['id']:r for r in doc['metamodel']['estimation_model']['rules']}
proposal=model['source/proposition-produit-core.yaml'];inputs=doc['evidence'][proposal['inputs']['path']];units=deepcopy([u for u in model['source/estimations-core-retenues.yaml']['units'] if u['stack']==proposal['stack']])
for u in units:
 u['tooling_eur_jh']=model['source/calibration-couts.yaml']['couts_communs']['outillage_realisation_eur_par_jh']
 for r in u['roles']:
  value=model[r['rate_ref']['path']]
  for part in r['rate_ref']['pointer'].split('.'):value=value[part]
  r['rate_eur_jh']=value
ref=proposal['technical_trials']['evidence'];proof=doc['evidence'][ref['path']];assert doc['sources'][ref['path']]==ref['sha256'];assert proof['proposal_inputs_sha256']==proposal['inputs']['sha256']
payload=gzip.decompress(base64.b64decode(proof['archive']['payload']));assert hashlib.sha256(payload).hexdigest()==proof['archive']['uncompressed_sha256'];files=json.loads(payload);assert len(files)==proof['archive']['files']
for name,item in files.items():
 assert name.startswith('audits/2026-10-31-essais-temporal-mining/') and '..' not in Path(name).parts
 assert hashlib.sha256(item['text'].encode('utf8')).hexdigest()==item['sha256']
def rule(id,**values):return evaluate_rule(rules[id],**values)
with patch('pathlib.Path.read_bytes',side_effect=AssertionError('Checkout read forbidden')),patch('pathlib.Path.read_text',side_effect=AssertionError('Checkout read forbidden')),patch('core_product_estimate.formula',side_effect=AssertionError('Disk formula access forbidden')):r=calculate(inputs,units,rule_function=rule)
expected=proof['financial_reference'];assert (r['total_jh'],r['eur_ht'])==(expected['total_jh'],expected['eur_ht']);assert r['purposes']==expected['purposes'];role_total=sum(v['jh'] for v in r['roles']) if isinstance(r['roles'],list) else sum(r['roles'].values());assert role_total==r['total_jh']
result=dict(status='passed',download_sha256=hashlib.sha256(raw).hexdigest(),download_bytes=len(raw),source_files=len(doc['sources']),checks_in_export=sum(len(g['checks']) for g in proof['check_groups']),archived_trial_files=len(files),total_jh=r['total_jh'],adopted_jh=r['adopted_jh'],eur_ht=r['eur_ht'],calculation_with_checkout_reads_forbidden=True)
(A/'results/download-replay.json').write_text(json.dumps(result,indent=2),'utf8');print(json.dumps(result))
