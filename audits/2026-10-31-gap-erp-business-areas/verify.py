"""Integrity checks for this audit, not a functional ERP certification."""
from pathlib import Path
import json,hashlib,time,collections
import yaml
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
read=lambda p:yaml.safe_load((ROOT/p).read_text(encoding='utf-8'))
def main():
 start=time.perf_counter();a=json.loads((OUT/'audit.json').read_text(encoding='utf-8'));checks=[]
 capture=read('sources/cartographie-scm-2026-10-24.yaml');an=read('source/analyse-perimetre-core.yaml');m=read('source/references-couts-integration.yaml')['reperes_build_core'];nodes={n['id']:n for n in capture['nodes']}
 bas={n['id'] for n in capture['nodes'] if n['id'].startswith('ba-')};prods=set(m['fiches_produit']);ex=set(m['etude_oss']['perimetre']['bc_exclus']);rows=a['business_areas']
 assert {r['business_area_ref'] for r in rows}==bas and len(rows)==len(bas);checks.append('native-business-area-universe')
 assert len(bas)==28;assert set(a['scope']['excluded_bc_refs'])==ex;checks.append('four-explicit-scope-exclusions')
 bcs={b['id']:b for b in an['blocs']};bycap={b['capacite_id']:b for b in an['blocs']};scopes=[]
 sources={s['id']:s for s in a['sources']};assert len(sources)==len(a['sources']);checks.append('unique-source-identifiers')
 for s in a['sources']:
  if not s['source_ref'].startswith('https:'):
   p=ROOT/s['source_ref'];assert p.is_file();assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256']
 checks.append('original-local-source-digests')
 for r in rows:
  bid=r['business_area_ref'];expected=[b for b in an['blocs'] if b['chemin'][-2]==bid]
  assert r['business_area_name']==nodes[bid]['fields']['name']
  assert r['native_capability_refs']==[b['capacite_id'] for b in expected]
  assert r['retained_capability_refs']==[b['capacite_id'] for b in expected if b['id'] not in ex]
  scopes+=r['native_capability_refs'];checks.append('native-scope:'+bid)
  assert len(r['cells'])==len(prods) and {c['product_ref'] for c in r['cells']}==prods
  for c in r['cells']:
   assert c['complete_ba_coverage'] is None and c['review'] is None
   assert set(c['evidence_refs'])<=set(sources)
   if c['reading_status'] not in ['non_etabli','hors_perimetre']:assert c['evidence_refs']
   if not r['retained_capability_refs']:assert c['reading_status']=='hors_perimetre'
 assert len(scopes)==len(set(scopes))==88;checks.append('capability-partition-no-duplicates')
 assert sum(len(r['retained_capability_refs']) for r in rows)==84;checks.append('84-retained-capabilities')
 assert sum(len(r['cells']) for r in rows)==168;checks.append('168-pairs-without-false-full-coverage')
 mechanisms={m['id'] for m in read('source/calculs-estimation-core.yaml')['mechanisms']};gids={g['id'] for g in a['gaps']}
 assert len(gids)==len(a['gaps'])==9
 for g in a['gaps']:
  assert set(g['business_area_refs'])<=bas and set(g['evidence_refs'])<=set(sources)
  assert set(g['funding_owner_refs_to_reconcile'])<=mechanisms
  assert all(g[x] is None for x in ['incremental_jh','incremental_initial_eur_ht','incremental_annual_eur_ht'])
  assert g['adopted'] is False;checks.append('gap-no-invented-budget:'+g['id'])
 for x in a['proposed_rfi_crosswalk']:
  b=bycap[x['capability_ref']]
  assert set(x['proposed_need_refs'])<= {f['id'] for f in b['fonctions']}
  assert x['business_area_ref']==b['chemin'][-2] and x['gap_ref'] in gids
  assert set(x['evidence_refs'])<=set(sources) and x['mapping_status']=='propose_non_revu'
  checks.append('proposed-crosswalk:'+x['bc_ref'])
 assert a['economics']['adopted_java_spring_jh']==sum(u['total_jh'] for u in read('source/estimations-core-retenues.yaml')['units'])==6660
 assert a['economics']['net_extra_jh'] is None and a['economics']['revised_total_jh'] is None and not a['economics']['adoption'];checks.append('adopted-total-preserved-no-recalibration')
 for p,h in a['active_source_fingerprints'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 checks.append('all-active-source-config-python-digests-unchanged')
 # Guard against conflating contradictory declarations into product coverage.
 for sid,row in [('ms-season',110),('sap-backlog',248)]:
  assert any(x['row']==row and x['answer'].startswith('YES') for x in sources[sid]['original_answer_locators'])
 checks.append('contradictory-yes-declarations-retained')
 result=dict(status='passed',seconds=round(time.perf_counter()-start,3),checks=checks,checked_active_files=len(a['active_source_fingerprints']),scope='References, source integrity and no economic mutation. No ERP runtime test, functional certification or full application regression.')
 (OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(status='passed',checks=len(checks),active_files=result['checked_active_files'],seconds=result['seconds'])))
if __name__=='__main__':main()
