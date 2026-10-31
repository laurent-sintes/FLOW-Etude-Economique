"""Freeze the Ownership sizing contract before any effort calculation."""
from pathlib import Path
import json,hashlib,importlib.util,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
import yaml
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def module(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 h=read((OUT/'hypotheses.json').relative_to(ROOT).as_posix())
 ni=read('audits/2026-10-30-stock-opportunite-08/inputs.json')
 old=read('audits/2026-10-30-stock-opportunite-08/results.json')
 own=read('audits/2026-10-30-propriete-stock-cadrage-01/preuves-code.json')
 repos=read('audits/2026-10-30-master-data-comparable-reuse/measurements.json')['repos']
 # This historical module only defines functions on import. Its main never runs.
 native=module('ownership02_stock_rulers','audits/2026-10-30-stock-opportunite-08/calculate.py')
 banks={};source_files={}
 for p in h['native_references']:
  banks[p]={}
  for level in ['lower','central','upper']:
   b=native.bank_for(p,level)
   banks[p][level]={k:b[k] for k in ['reservation_chain','correction_chain']}
   for name,bank in banks[p][level].items():
    if level=='central':
     previous=next(r for r in old['rows'] if r['id']==p)['detail']['analogue_bank'][name]['program_units']
     assert abs(bank['program_units']-previous)<1e-8
    for part in bank['source_slices']:
     path=(Path(repos[p]['root'])/part['path']).as_posix()
     assert sha(ROOT/path)==part['source_sha256'],path
     source_files[path]=part['source_sha256']
 for f in own['files']:
  path=(Path(repos[f['repo']]['root'])/f['path']).as_posix()
  assert sha(ROOT/path)==f['sha256'],path
  source_files[path]=f['sha256']
 for sc in h['schemas']:
  assert sc['package'] in {m['id'] for m in h['modules']}
  assert len(sc['fields'])==len(set(sc['fields']))
 assert len(h['schemas'])==10 and sum(len(x['fields']) for x in h['schemas'])==86
 protected={p:sha(ROOT/p) for p in ['source/estimations-core-retenues.yaml','source/calculs-estimation-core.yaml',
  'source/fondamentaux.yaml','source/schema-fondamentaux.yaml','source/referentiel-capacites.yaml','sources/cartographie-scm-2026-10-24.yaml']}
 deps=['audits/2026-10-30-propriete-stock-cadrage-01/cadrage.yaml','audits/2026-10-30-propriete-stock-cadrage-01/preuves-code.json',
  'audits/2026-10-30-stock-opportunite-08/inputs.json','audits/2026-10-30-stock-opportunite-08/results.json',
  'audits/2026-10-30-stock-opportunite-08/calculate.py','audits/2026-10-30-master-data-calcul/repartitions-sources.json',
  'audits/2026-10-30-master-data-calcul/entrees.json','audits/2026-10-30-master-data-comparable-reuse/measurements.json',
  'audits/2026-10-30-stock-adoption-10/measurements.json']
 for p in h['native_references']:
  deps.append(f'audits/2026-10-30-stock-mesures-03/{p}-mesures.json')
  for k in ['correction','reservation']:deps.append(f'audits/2026-10-30-stock-chaines-06/{p}-{k}.json')
 # All selected rulers are measured source behaviors. Their reuse is analogical,
 # not a second claim on the existing family funding.
 result=dict(id=h['id'],hypotheses=h,cocomo=ni['cocomo'],banks=banks,
  schema_templates=ni['schema_templates'],new_module_scaffolding=ni['new_module_scaffolding'],
  activities=read('audits/2026-10-30-master-data-calcul/repartitions-sources.json')['cocomo'],
  native_reference_labels=dict(erpnext='ERPNext avec Frappe',odoo='Odoo',tryton='Tryton',axelor='Axelor avec Open Platform'),
  rules_ref='source/fondamentaux.yaml#estimation_model',
  input_hashes={p:sha(ROOT/p) for p in deps},raw_source_hashes=source_files,
  protected_active_inputs=protected,
  rule_basis='Les instructions des chaînes natives servent à dimensionner du nouveau comportement de propriété. Les analogues ne sont pas ajoutés comme nouveau code Stock livré.',
  existing_foundation=dict(additional_framework_construction_jh=0,additional_physical_stock_construction_jh=0,
   no_free_work_claim='Déjà financé dans le contexte comparé. Les adaptations nouvelles sont intégralement portées par OWN-F01 à OWN-F06.',
   native_context='Patrimoine Master Data et Stock disponible dans chaque technologie native ; contexte de comparaison, pas quatre budgets actifs.'))
 save('inputs.json',result)
 freeze=dict(input_sha256=sha(OUT/'inputs.json'),hypotheses_sha256=sha(OUT/'hypotheses.json'),cosmic_sha256=sha(OUT/'cosmic.json'),
  policy='Contrat de taille et comptage gelés avant le premier calcul des JH ; aucun objectif de convergence ou budget cible.',
  calibrated_effort_data=None)
 save('input-freeze.json',freeze)
 print(json.dumps(dict(frozen=freeze,rulers={p:{k:v['program_units'] for k,v in b['central'].items()} for p,b in banks.items()},
  schemas=len(h['schemas']),specific_fields=sum(len(x['fields']) for x in h['schemas']),verified_raw_sources=len(source_files)),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
