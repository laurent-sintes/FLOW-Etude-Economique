"""Verify the four Stock component perimeters and keep unknown effort unknown."""
from pathlib import Path
from collections import Counter
import json,hashlib,sys,math,importlib.util
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tmp/model-deps'),str(ROOT/'tmp/master-data-native-23/parser-deps')]
import yaml
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
counter=module('counter07verify',ROOT/'audits/2026-10-30-master-data-natif/measure.py')
def main():
 provenance=load(OUT/'provenance.json')
 for d in provenance['dependencies']:assert sha(ROOT/d['path'])==d['sha256'],d['path']
 for p,h in provenance['protected'].items():assert sha(ROOT/p)==h,p
 md=load(ROOT/'audits/2026-10-30-master-data-comparable-reuse/measurements.json')
 components=load(OUT/'components.json')['components']
 assert len(components)==5 and sum(c['contract_CFP'] for c in components)==169
 assert len({p for c in components for p in c['processes']})==21
 assert set(cap for c in components for cap in c['capabilities'])=={'BC-009','BC-010','BC-011','BC-012','BC-013','BC-016','BC-017','BC-018'}
 records=[];duplicate_total=MD_total=0;eligible=0
 for p in ['erpnext','odoo','tryton','axelor']:
  d=load(OUT/(p+'-perimetre.json'));s=d['summary']
  assert len({r['path'] for r in d['files']})==len(d['files'])==s['files']
  component_ids={c['component'] for c in d['components']};assert component_ids=={'K1','K2','K3','K4','K5'}
  for f in d['files']:
   path=ROOT/md['repos'][f['repo']]['root']/f['path']
   assert sha(path)==f['sha256']
   current=counter.measure(path)
   assert all(current[k]==f[k] for k in ['program_units','declarative_units','physical_lines'])
   assert f['native_program_after_MD']==f['program_units']-f['already_funded_MD']['program_units']
   assert f['native_declarative_after_MD']==f['declarative_units']-f['already_funded_MD']['declarative_units']
   assert f['native_program_after_MD']>=0 and f['native_declarative_after_MD']>=0
   assert len(f['components'])==len(set(f['components']))
   old=[r for r in md['files'] if r['repo']==f['repo'] and r['path']==f['path']]
   if old:
    assert len(old)==1 and old[0]['sha256']==f['sha256']
    assert f['already_funded_MD']['program_units']==old[0]['program_units']
    assert f['already_funded_MD']['declarative_units']==old[0]['declarative_units']
   records.append(f)
  unique=sum(f['program_units']+f['declarative_units'] for f in d['files'])
  naive=sum(c['native_program_units']+c['native_declarative_units'] for c in d['components'])
  assert unique==s['native_unique_units'] and naive==s['naive_component_units']
  assert naive-unique==s['duplicate_units_avoided']
  paid=sum(f['already_funded_MD']['program_units']+f['already_funded_MD']['declarative_units'] for f in d['files'])
  assert paid==s['MD_program_units_not_recharged']+s['MD_declarative_units_not_recharged']
  assert unique-paid==s['code_units_after_MD']
  assert d['components'][-1]['files']==[] # K5 is a Flow complement, no native equivalence invented.
  assert s['eligible_Flow_equivalent_size'] is None and s['COCOMO_jh'] is None
  eligible+=int(d['supports_calculation']);duplicate_total+=naive-unique;MD_total+=paid
 assert len(records)==62 and eligible==0
 overlaps=load(OUT/'reutilisation-master-data.json')['exact_native_overlaps'];assert len(overlaps)==5
 assert sum(o['program_units']+o['declarative_units'] for o in overlaps)==MD_total
 for w in load(OUT/'ecarts-natifs-non-normalises.json')['witnesses']:
  p=ROOT/md['repos'][w['product']]['root']/w['path'];lines=p.read_text(encoding='utf-8-sig').splitlines()
  assert '\n'.join(lines[w['start']-1:w['end']])==w['source_fragment']
  assert all(s in w['source_fragment'] for s in w['observed_markers'])
  assert sha(p)==w['sha256'] and w['unresolved_for_economic_size'] is True
 complements=load(OUT/'complements.json')['complements'];assert len(complements)==7
 assert sum(c['dimensioning_hypotheses']['field_count'] for c in complements)==126
 assert sum(c['dimensioning_hypotheses']['behavior_count'] for c in complements)==66
 assert sum(c['dimensioning_hypotheses']['new_models'] for c in complements)==13
 assert sum(c['dimensioning_hypotheses']['extensions'] for c in complements)==4
 assert all(c['included'] and c['excluded'] and c['reuse'] and c['unknowns'] for c in complements)
 assert all(c['equivalent_size'] is None and c['effort_jh'] is None for c in complements)
 assert 'RPO/RTO' in ' '.join(complements[-1]['unknowns'])
 retained=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))
 unit=next(u for u in retained['units'] if u['id']=='master-data-java-spring')
 assert unit['total_jh']==1500 and unit['months']==17 and sum(r['jh'] for r in unit['roles'])==1500
 assert not any('stock' in u['id'] for u in retained['units'])
 report=yaml.safe_load((OUT/'bilan.yaml').read_text(encoding='utf-8'))
 report['verification_summary']=dict(files_measured_and_verified=62,component_product_pairs=20,native_components_mapped=16,
  duplicate_native_code_units_avoided=duplicate_total,already_funded_MD_units_not_recharged=MD_total,exact_MD_overlap_files=5,
  source_coupling_witnesses=4,complement_packages=7,retained_model_unchanged=True)
 report['rules_ref']='source/fondamentaux.yaml#estimation_model'
 report['evidence']=list(dict.fromkeys(report['evidence']+['verification.json']))
 (OUT/'bilan.yaml').write_text(yaml.safe_dump(report,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
 deps={d['path']:d['sha256'] for d in provenance['dependencies']}
 for p in [OUT/'bilan.yaml',Path(__file__).resolve()]:
  deps[str(p.relative_to(ROOT)).replace('\\','/')]=sha(p)
 provenance['dependencies']=[dict(path=p,sha256=h) for p,h in sorted(deps.items())]
 write('provenance.json',provenance)
 result=dict(consistency_checks_passed=True,files_recounted=62,perimeters=4,native_component_correspondences=16,
  duplicate_code_units_avoided=duplicate_total,MD_units_already_funded=MD_total,MD_overlap_files=5,source_coupling_witnesses=4,
  bounded_complement_contents=7,complement_JH_bounded=False,stock_complete_estimates_receivable=0,
  cumulative_retained_gross_jh=1500,master_data_months=17,metamodel_and_capabilities_unchanged=True,
  code_audit_repetition_recommended=False,application_rebuilt=False)
 write('verification.json',result)
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
