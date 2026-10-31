"""Recompute the complete proposal from the single downloadable YAML, without repository reads."""
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import hashlib,json,sys,yaml
R=Path.cwd();O=R/'audits/2026-10-30-audit-fonctions-transverses';sys.path[:0]=[str(R/'tools'),str(R/'tmp/model-deps')]
from core_product_estimate import calculate
from estimation_calculation import evaluate_rule
path=R/'app/dist/exports/flow-modele-metier.yaml';raw=path.read_bytes();doc=yaml.load(raw,Loader=getattr(yaml,'CSafeLoader',yaml.SafeLoader));models=doc['model'];spec=models['source/proposition-produit-core.yaml'];inputs=doc['evidence'][spec['inputs']['path']];rules={r['id']:r for r in doc['metamodel']['estimation_model']['rules']}
def calc(id,**values):return evaluate_rule(rules[id],**values)
def reference(ref):
 value=models[ref['path']]
 for part in ref['pointer'].split('.'):value=value[part]
 return value
units=[];tooling=models['source/calibration-couts.yaml']['couts_communs']['outillage_realisation_eur_par_jh']
for u in models['source/estimations-core-retenues.yaml']['units']:
 if u['stack']!='java-spring':continue
 unit=deepcopy(u)
 for r in unit['roles']:r['rate_eur_jh']=reference(r['rate_ref'])
 unit['tooling_eur_jh']=tooling;unit['cost_eur_ht']=round(sum(calc('role_price',JH=r['jh'],rate=r['rate_eur_jh']) for r in unit['roles'])+u['total_jh']*tooling,2);units.append(unit)
with patch('pathlib.Path.read_bytes',side_effect=AssertionError('Repository reads forbidden')),patch('pathlib.Path.read_text',side_effect=AssertionError('Repository reads forbidden')),patch('core_product_estimate.formula',side_effect=AssertionError('External metamodel forbidden')):
 result=calculate(inputs,units,rule_function=calc)
assert result['total_jh']==6660 and result['eur_ht']==4198680
assert sum(u['total_jh'] for u in units)==4160 and sum(u['cost_eur_ht'] for u in units)==2620030
record=dict(status='passed',file=path.relative_to(R).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),source_fingerprint=doc['source_fingerprint'],model_objects=['source/fonctions-produit-core.yaml','source/proposition-produit-core.yaml'],canonical_rule='complete_product_proposal',proposal_jh=result['total_jh'],proposal_eur_ht=result['eur_ht'],adopted_jh=sum(u['total_jh'] for u in units),filesystem_reads_during_replay=0,grouping_sensitivity=result['grouping_sensitivity'])
(O/'download-replay.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(record,ensure_ascii=False))
