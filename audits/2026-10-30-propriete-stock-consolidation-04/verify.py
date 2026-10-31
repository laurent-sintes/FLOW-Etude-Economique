"""Contrôles indépendants des tailles, efforts, activités, rôles, délai et cumul proposés."""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal,ROUND_HALF_UP
import hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tmp/model-deps'))
import yaml
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def halfup(x,step):return float((Decimal(str(x))/Decimal(str(step))).quantize(Decimal('1'),rounding=ROUND_HALF_UP)*Decimal(str(step)))
def main():
 d=read(OUT/'inputs.json');r=read(OUT/'results.json')
 assert sha(OUT/'inputs.json')==read(OUT/'input-freeze.json')['inputs_sha256']
 for group in ['input_hashes','protected_active_inputs']:
  for p,h in d[group].items():assert sha(ROOT/p)==h,p
 ni=read(ROOT/'audits/2026-10-30-propriete-stock-calcul-02/inputs.json')
 old=read(ROOT/'audits/2026-10-30-propriete-stock-calcul-02/results.json')
 # Reconstruct all native sizes independently, rather than trust the old effort outputs.
 c=ni['cocomo'];exponent=c['B']+.01*c['SF_sum']
 native=[]
 for p in ni['hypotheses']['native_references']:
  template=ni['schema_templates'][p];pu=du=0
  for module in ni['hypotheses']['modules']:
   pu+=ni['banks'][p]['central'][module['analogue']]['program_units']*module['central']
   pu+=ni['new_module_scaffolding'][p]['program_units_per_new_service_module']
   for sc in ni['hypotheses']['schemas']:
    if sc['package']!=module['id']:continue
    n=len(sc['fields'])
    pu+=n*template['program_per_field']+template.get('program_per_new_model',0)
    du+=n*template['declarations_per_field']+template['per_new_model']
    if sc['view']:du+=n*template['view_field']+template['view_model']
  du+=sum(ni['hypotheses']['configuration'].values());size=pu+du
  effort=c['A']*(size/1000)**exponent*c['other_EM']*c['SCED']*c['month_hours']/c['day_hours']*c['effort_phase_factor']
  row=next(x for x in old['rows'] if x['id']==p)
  assert math.isclose(size,row['detail']['equivalent_units'],rel_tol=1e-12)
  assert math.isclose(effort,row['jh'],rel_tol=1e-12)
  assert math.isclose(effort,next(x for x in r['native_comparisons'] if x['id']==p)['jh'],rel_tol=1e-12)
  native.append(dict(id=p,jh=effort))
 exact=next(x['jh'] for x in native if x['id']==d['selected_reference'])
 total=halfup(exact,d['rounding_jh']);assert total==r['proposed_jh']==100
 a=read(ROOT/'audits/2026-10-30-master-data-calcul/repartitions-sources.json')['cocomo']
 assert len(a['activities'])==7 and sum(a['phase_effort_percent_of_base'])==118
 fractions={x['id']:Fraction(0) for x in r['roles']}
 for act in a['activities']:
  share=sum(Fraction(p*q) for p,q in zip(a['phase_effort_percent_of_base'],act['percent_by_phase']))/sum(a['phase_effort_percent_of_base'])/100
  value=Fraction(int(total))*share
  actual=next(x for x in r['activities'] if x['id']==act['id'])
  assert math.isclose(float(value),actual['jh'],abs_tol=1e-10)
  weights=d['activity_role_weights'][act['id']]
  assert sum(Fraction(str(v)) for v in weights.values())==1
  for role,w in weights.items():fractions[role]+=value*Fraction(str(w))
 assert sum(fractions.values())==total
 step=d['role_rounding_jh'];assigned={k:int(v//step)*step for k,v in fractions.items()}
 order=sorted(fractions,key=lambda k:(-(fractions[k]/step-int(fractions[k]//step)),k))
 for k in order[:int((total-sum(assigned.values()))/step)]:assigned[k]+=step
 assert assigned=={x['id']:x['jh'] for x in r['roles']} and sum(assigned.values())==100
 for role in r['roles']:assert math.isclose(float(fractions[role['id']]),role['unrounded_jh'],abs_tol=1e-10)
 F=c['D']+.2*(exponent-c['B'])
 months=c['C']*(total/c['effort_phase_factor']*c['day_hours']/c['month_hours']/c['SCED'])**F*c['schedule_phase_factor']
 assert math.isclose(months,r['schedule']['calculated_months_on_proposed_jh'],rel_tol=1e-12)
 assert halfup(months,d['schedule_rounding_months'])==r['schedule']['proposed_months']==7
 assert math.isclose(total/7/18,r['schedule']['average_people'])
 control=80*20/7;assert math.isclose(control,r['crosscheck']['jh'])
 assert math.isclose((control-exact)/exact*100,r['crosscheck']['alignment_vs_unrounded_java']['gap_pct'])
 assert math.isclose((control-total)/total*100,r['crosscheck']['alignment_vs_proposed_total']['gap_pct'])
 decisions=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))['units']
 caps={x['id'] for u in decisions for x in u['capabilities']}
 assert len(caps)==14 and len(caps|set(d['scope']['capabilities']))==16
 assert not caps.intersection(d['scope']['capabilities'])
 assert sum(u['total_jh'] for u in decisions)==r['cumulative']['adopted_jh']==1840
 assert sum(x['cumulative_proposed_jh'] for x in r['roles'])==r['cumulative']['proposed_java_cumulative_jh']==1940
 capture=ROOT/'sources/cartographie-scm-2026-10-24.yaml'
 assert sha(capture)=='a1fc16bac87e206124485aee8fa51b49b774a4352e36721731662e868dbe6976'
 nodes=yaml.safe_load(capture.read_text(encoding='utf-8'))['nodes']
 assert sum(n['kind']=='capability' for n in nodes)==r['progress']['total_capabilities']==88
 assert math.isclose(sum(x['allocated_jh_from_proposed_total'] for x in r['module_allocation']),100)
 assert r['cumulative']['combined_months'] is None and not r['cumulative']['schedules_added']
 assert not r['active_model_changed'] and not r['conclusion']['predictive_validation']
 raw=dict(ni['raw_source_hashes'])
 review=read(ROOT/'audits/2026-10-30-propriete-stock-java-03/inputs.json')
 for x in review['code']:raw[x['root_path']]=x['sha256']
 for p,h in raw.items():assert sha(ROOT/p)==h,p
 v=dict(passed=True,native_sizes_and_efforts_reconstructed=4,published_activities_checked=7,
  role_weights_and_rounding_checked_with_exact_fractions=True,roles=assigned,roles_sum=100,
  schedule_formula_independently_checked=True,calculated_months=months,proposed_months=7,
  CFP=80,control_jh=control,adopted_jh=1840,proposed_cumulative_jh=1940,
  captured_capabilities=88,adopted_capabilities=14,proposed_or_adopted_capabilities=16,
  immutable_capability_capture_verified=True,raw_source_files_verified=len(raw),
  earlier_proofs_unchanged=True,active_sources_unchanged=True,adoption=False)
 save('verification.json',v)
 save('provenance.json',dict(files={p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='provenance.json'},
  dependencies=d['input_hashes'],protected_active_inputs=d['protected_active_inputs'],raw_source_hashes=raw))
 print(json.dumps(v,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
