"""Replay all eleven adopted decisions from the single model download with checkout I/O forbidden."""
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import json,yaml,hashlib
from model_context import model_session
from estimation_calculation import calculate,evaluate_rule
from core_product_scope import partition
R=Path.cwd();A=R/'audits/2026-10-31-adoption-produit-professionnel';p=R/'tmp/model-download/flow-modele-metier.yaml';raw=p.read_bytes();d=yaml.load(raw,Loader=getattr(yaml,'CSafeLoader',yaml.SafeLoader));model=d['model'];meta=d['metamodel']['estimation_model'];reg=model['source/calculs-estimation-core.yaml'];units=model['source/estimations-core-retenues.yaml']['units'];proofs=d['evidence'];rules={x['id']:x for x in meta['rules']};specs={c['id']:c for c in reg['calculations']}
def f(id,**v):return evaluate_rule(rules[id],**v)
def contract(binding):return specs[binding['id']],reg
valued=[];results=[]
with model_session(),patch('estimation_inputs.contract',side_effect=contract),patch('estimation_inputs._frozen_calculation_proofs',return_value=proofs),patch('estimation_calculation.formula',side_effect=f),patch('estimation_calculation.metamodel',return_value=meta),patch('core_product_scope.formula',side_effect=f),patch('pathlib.Path.read_text',side_effect=AssertionError('Checkout read forbidden')),patch('pathlib.Path.read_bytes',side_effect=AssertionError('Checkout read forbidden')):
 for u in units:
  r=calculate(u['calculation']);assert (r['total_jh'],r['months'],r['roles'])==(u['total_jh'],u['months'],{r['id']:r['jh'] for r in u['roles']})
  unit=deepcopy(u);unit['tooling_eur_jh']=model['source/calibration-couts.yaml']['couts_communs']['outillage_realisation_eur_par_jh']
  for role in unit['roles']:
   rate=model[role['rate_ref']['path']]
   for key in role['rate_ref']['pointer'].split('.'):rate=rate[key]
   role['rate_eur_jh']=rate
  unit['cost_eur_ht']=round(sum(x['jh']*x['rate_eur_jh'] for x in unit['roles'])+unit['total_jh']*unit['tooling_eur_jh'],2);valued.append(unit);results.append(dict(id=u['id'],jh=r['total_jh'],months=r['months'],CFP=r['trace']['CFP'],four_references=len(r['alignment']['rows'])))
 split=partition(valued,model['source/fonctions-produit-core.yaml']['allocations'])
assert (split['adopted_jh'],split['adopted_eur_ht'])==(6660,4198680);assert (split['purposes']['business-runtime']['jh'],split['purposes']['it-complement']['jh'])==(5886,774)
proposal=model['source/proposition-produit-core.yaml'];assert proposal['status']=='retained';basis=proposal['adoption']['basis'];assert d['sources'][basis['path']]==basis['sha256']
r=dict(status='passed',download_sha256=hashlib.sha256(raw).hexdigest(),download_bytes=len(raw),sources=len(d['sources']),checkout_reads_forbidden=True,units=results,total_jh=split['adopted_jh'],build_eur_ht=split['adopted_eur_ht'],purposes=split['purposes']);(A/'download-replay.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8');print(json.dumps({k:v for k,v in r.items() if k not in ['units','purposes']}))
