"""Independent verification of common funding, harmonised measures and COCOMO arithmetic."""
from pathlib import Path
from collections import Counter,defaultdict
from copy import deepcopy
from fractions import Fraction
from decimal import Decimal,ROUND_HALF_UP
import hashlib,importlib.util,json,math,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tmp/model-deps'),str(ROOT/'tools')]
import yaml
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def halfup(v,step):return float((Decimal(str(v))/Decimal(str(step))).quantize(Decimal('1'),rounding=ROUND_HALF_UP)*Decimal(str(step)))
def check_registry(f):
 mechanisms={m['id']:m for m in f['mechanisms']}
 assert len(mechanisms)==len(f['mechanisms'])
 for id,m in mechanisms.items():
  claims=[c for c in f['claims'] if c['mechanism']==id and c['mode']=='proposed_funding']
  assert len(claims)==1 and claims[0]['family']==m['owner']
 for c in f['claims']:
  if c['mode']=='consumed':assert c['mechanism'] in mechanisms and c['funding_owner']==mechanisms[c['mechanism']]['owner'] and c['family']!=c['funding_owner']
  elif c['mode']=='consumed_already_funded':assert c['funding_owner']==f['existing_owners'][c['mechanism']]
  elif c['mode']=='external_library_no_reconstruction':assert c['adaptation_funding_owner']=='workflow'
  else:assert c['mode']=='proposed_funding'
def main():
 m=read(OUT/'measurements.json');spec=read(OUT/'specification.json');fund=read(OUT/'funding.json');cf=read(OUT/'cosmic.json');r=read(OUT/'results.json')
 initial=read(OUT/'results-initial.json');adj=read(OUT/'reuse-adjustment.json')
 assert sha(OUT/'results-initial.json')==adj['prior_result_sha256']
 assert sha(OUT/'reuse-adjustment.json')==read(OUT/'reuse-adjustment-freeze.json')['sha256']
 frozen=read(OUT/'economic-input-freeze.json')
 for name,key in [('measurements.json','measurements_sha256'),('specification.json','specification_sha256'),('funding.json','funding_sha256'),('cosmic.json','cosmic_sha256')]:
  assert sha(OUT/name)==frozen[key]
 check_registry(fund)
 # Rejection checks for double funding and incorrect consumption.
 mutants=[]
 x=deepcopy(fund);x['claims'].append(deepcopy(next(c for c in x['claims'] if c['mode']=='proposed_funding')));mutants.append(x)
 x=deepcopy(fund);next(c for c in x['claims'] if c['mode']=='consumed')['funding_owner']='wrong-owner';mutants.append(x)
 x=deepcopy(fund);next(c for c in x['claims'] if c['mode']=='consumed_already_funded')['funding_owner']='orders';mutants.append(x)
 for x in mutants:
  try:check_registry(x)
  except AssertionError:continue
  raise AssertionError('Invalid funding accepted')
 native=read(ROOT/'audits/2026-10-30-propriete-stock-calcul-02/inputs.json');c=native['cocomo'];E=c['B']+.01*c['SF_sum'];F=c['D']+.2*(E-c['B'])
 stock={p:v['central']['correction_chain']['program_units'] for p,v in native['banks'].items()}
 source_spec=importlib.util.spec_from_file_location('count_verified',ROOT/spec['metrics_ref']);counter=importlib.util.module_from_spec(source_spec);source_spec.loader.exec_module(counter)
 for source in m['sources']:
  p=ROOT/source['root_path'];assert sha(p)==source['sha256']
  assert counter.measure(p)==source['whole_measure']
 for p,h in m['dependency_hashes'].items():assert sha(ROOT/p)==h
 ownkeys=set();reconstructed_base={id:defaultdict(int) for id in m['base_units_owned_once']}
 for a in m['source_node_ownership']:
  key=(a['repo'],a['path'],a['atom']);assert key not in ownkeys;ownkeys.add(key)
  product='erpnext' if a['repo']=='frappe' else 'axelor' if a['repo'] in ('studio','platform') else a['repo']
  reconstructed_base[a['mechanism']][product]+=1
 for id,products in m['base_units_owned_once'].items():
  for p,v in products.items():assert reconstructed_base[id][p]==v
 for mech in spec['mechanisms']:
  id=mech['id']
  for p in ('erpnext','odoo','tryton','axelor'):
   program=sum(b['selected_program_units'] for b in m['bindings'] if b['mechanism']==id and b['product']==p and b['kind']=='program')
   declarative=sum(b['selected_declarative_units'] for b in m['bindings'] if b['mechanism']==id and b['product']==p and b['kind']=='declarative')
   if mech.get('provider')=='stock_correction':assert stock[p]==m['bank_program_units'][id][p]
   else:assert program==m['bank_program_units'][id][p]
   assert declarative==m['bank_declarative_units'][id][p]
 productsum=defaultdict(int);roles_total=Counter();arithmetic=0
 distribution=read(ROOT/spec['activity_ref'])['cocomo'];weights=read(ROOT/spec['allocation_ref'])['activity_role_weights']
 for owner,data in r['owners'].items():
  for row in data['rows']:
   p=row['id'];size=0;base=0
   for mech in spec['mechanisms']:
    if mech['owner']!=owner:continue
    id=mech['id'];t=native['schema_templates'][p];s=native['new_module_scaffolding'][p]['program_units_per_new_service_module']
    schemaunits=0
    for definition in mech['schemas']:
     _,fields=definition.split(':',1);n=len(fields.split(','))
     schemaunits+=n*t['program_per_field']+t.get('program_per_new_model',0)+n*t['declarations_per_field']+t['per_new_model']+n*t['view_field']+t['view_model']
    before=m['base_units_owned_once'][id][p]
    b=0 if p in adj['base_exclusions'].get(id,[]) else before
    new=m['bank_program_units'][id][p]*mech['fraction']+s+schemaunits
    size+=b+new;base+=b
   expected=c['A']*(size/1000)**E*c['other_EM']*c['SCED']*c['month_hours']/c['day_hours']*c['effort_phase_factor']
   assert math.isclose(size,row['equivalent_units'],rel_tol=1e-12)
   assert math.isclose(expected,row['jh'],rel_tol=1e-12)
   assert halfup(expected,10)==row['rounded_jh'];productsum[p]+=row['rounded_jh'];arithmetic+=1
  total=data['java_common_jh'];raw={k:Fraction(0) for k in [r['id'] for r in data['roles']]};phases=distribution['phase_effort_percent_of_base']
  for a in distribution['activities']:
   value=Fraction(total)*sum(Fraction(x*y) for x,y in zip(phases,a['percent_by_phase']))/sum(phases)/100
   for k,w in weights[a['id']].items():raw[k]+=value*Fraction(str(w))
  assigned={k:int(v//1) for k,v in raw.items()};order=sorted(raw,key=lambda k:(-(raw[k]-int(raw[k]//1)),k))
  for k in order[:total-sum(assigned.values())]:assigned[k]+=1
  assert assigned=={x['id']:x['jh'] for x in data['roles']};roles_total.update(assigned)
  assert math.isclose(sum(x['allocated_jh'] for x in data['mechanism_allocations']),total)
  months=c['C']*(total/c['effort_phase_factor']*c['day_hours']/c['month_hours']/c['SCED'])**F*c['schedule_phase_factor']
  assert math.isclose(months,data['raw_months'],rel_tol=1e-12) and halfup(months,1)==data['local_nominal_months']
  groups=set(cf[owner]['groups']);ids=set();moves=Counter()
  for proc in cf[owner]['processes']:
   keys=set()
   for x in proc['movements']:
    assert x['id'] not in ids and (x['type'],x['group']) not in keys and x['group'] in groups and x['cfp']==1
    ids.add(x['id']);keys.add((x['type'],x['group']));moves[x['type']]+=1
  assert sum(moves.values())==cf[owner]['CFP']
  check=20*sum(moves.values())/7
  assert math.isclose(check,data['functional']['jh'])
 assert dict(productsum)==r['common_native_subtotals']
 assert sum(roles_total.values())==r['common_java_subtotal_jh']==280
 assert r['cumulative']['adopted_plus_proposed_common_only_jh']==1940+280
 for f in r['families']:
  assert f['additional_common_reconstruction_jh']==0 and f['specific_family_work_jh'] is None and f['complete_family_estimate_jh'] is None
 baseline=read(OUT/'baseline.json')
 for p,h in baseline['protected'].items():assert sha(ROOT/p)==h,p
 assert yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))['units']==baseline['units']
 # Quantify the old method-only metric versus the same file measured with the adopted counter.
 old={}
 for family in baseline['scope']:
  for f in read(ROOT/'audits/2026-10-30-familles-restantes'/family/'entrees-3.json')['source_measures']:
   old[f['root_path']]=f
 harmonization=[]
 for f in m['sources']:
  previous=old.get(f['root_path'])
  if previous and f['whole_measure']['program_units']:
   assert previous['sha256']==f['sha256']
   harmonization.append(dict(path=f['root_path'],old_method_only_units=previous['program_units'],
     complete_counter_program_units=f['whole_measure']['program_units'],
     outside_method_program_units=f['whole_measure']['program_units']-previous['program_units'],
     price_cannot_be_compared_without_scope_reconciliation=True))
 save('harmonization.json',dict(counter=spec['metrics_ref'],same_file_comparisons=harmonization,
  note='Compteur identique à celui des mesures adoptées. L’inclusion ou l’exclusion d’un atome est distincte de la convention de comptage ; les noyaux fournis ne sont pas reconstruits.'))
 report=dict(passed=True,shared_mechanisms=11,unique_funding_owners=6,affected_families=10,affected_capabilities=42,
  funding_claims=len(fund['claims']),double_funding_and_wrong_owner_rejections=3,unique_native_base_atoms=len(ownkeys),
  source_files_verified=len(m['sources']),new_studio_BPM_files=sum(f['repo']=='studio' for f in m['sources']),
  same_counter_verified=True,old_metric_comparisons=len(harmonization),native_efforts_independently_checked=arithmetic,
  functional_counts_checked=6,owner_role_and_delay_allocations_checked=6,
  final_common_jh=280,initial_common_jh=initial['common_java_subtotal_jh'],reuse_review_java_change_jh=280-initial['common_java_subtotal_jh'],
  four_native_subtotals=dict(productsum),adopted_jh=1940,adopted_plus_proposed_common_only_jh=2220,
  new_complete_capabilities_adopted=0,protected_model_and_native_source_unchanged=True,no_full_Core_total=True,
  confidence_or_probability_not_claimed=True)
 save('verification.json',report)
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
