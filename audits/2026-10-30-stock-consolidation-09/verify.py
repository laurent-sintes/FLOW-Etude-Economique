"""Independent conservation, arithmetic, provenance and boundary checks."""
from pathlib import Path
from collections import Counter,defaultdict
from decimal import Decimal,ROUND_HALF_UP
from fractions import Fraction
import hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tmp/model-deps')]
import yaml
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def close(a,b):assert math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-9),(a,b)
def rounded(x,step):return int((Decimal(str(x))/Decimal(step)).quantize(Decimal('1'),rounding=ROUND_HALF_UP))*step

def main():
 p=load(OUT/'provenance.json');r=load(OUT/'results.json');d=load(OUT/'inputs.json')
 for s in p['dependencies']:assert sha(ROOT/s['path'])==s['sha256'],s['path']
 for path,h in p['protected'].items():assert sha(ROOT/path)==h,path
 assert sha(OUT/'inputs.json')==load(OUT/'input-freeze.json')['input_sha256']==r['input_sha256']
 old=load(ROOT/d['native_calculation']);i=load(ROOT/'audits/2026-10-30-stock-opportunite-08/inputs.json')
 a=next(x for x in old['rows'] if x['id']=='axelor');o=next(x for x in old['rows'] if x['id']=='odoo')
 c=i['cocomo'];E=c['B']+.01*c['SF_sum'];F=c['D']+.2*(E-c['B'])
 def effort(units):return c['A']*(units/1000)**E*c['other_EM']*c['SCED']*c['month_hours']/c['day_hours']*c['effort_phase_factor']
 close(r['raw_reference_jh'],effort(a['base_equivalent_units']+a['Flow_complements_equivalent_units']))
 total=rounded(r['raw_reference_jh'],d['rounding_jh']);assert total==r['proposed_jh']==340
 assert r['proposed_common_base_jh']+r['proposed_Flow_complements_jh']==total
 assert len(r['native_estimates'])==4 and len(r['roles'])==9 and len(r['activities'])==7
 assert len(r['scope']['capabilities'])==8==len(set(r['scope']['capabilities']))
 # Reconstruct activity and role shares as exact rational fractions from the published table.
 published=load(ROOT/'audits/2026-10-30-master-data-calcul/repartitions-sources.json')['cocomo']
 parts=published['phase_effort_percent_of_base'];raw=defaultdict(Fraction)
 for source,actual in zip(published['activities'],r['activities']):
  assert source['id']==actual['id']
  weight=Fraction(sum(x*y for x,y in zip(parts,source['percent_by_phase'])),100*sum(parts))
  close(actual['jh'],total*float(weight))
  mapping=d['activity_role_weights'][source['id']]
  assert set(mapping)<=set(source['possible_flow_roles'])
  assert sum(Fraction(str(x)) for x in mapping.values())==1
  for role,value in mapping.items():raw[role]+=total*weight*Fraction(str(value))
 step=d['role_rounding_jh']
 allocated={k:(v//step)*step for k,v in raw.items()}
 count=(total-sum(allocated.values()))//step
 order=sorted(raw,key=lambda k:(-(raw[k]%step),k))
 for k in order[:int(count)]:allocated[k]+=step
 for row in r['roles']:
  close(row['unrounded_jh'],float(raw[row['id']]))
  assert row['jh']==allocated[row['id']]
 assert sum(row['jh'] for row in r['roles'])==total
 close(sum(x['jh'] for x in r['activities']),total)
 # Recount the unchanged functional proposal; do not fit a PDR to COCOMO.
 cosmic=load(ROOT/'audits/2026-10-30-stock-completion-04/cosmic.json')
 moves=[m for process in cosmic['processes'] for m in process['movements']]
 assert len({m['id'] for m in moves})==len(moves)==169
 assert Counter(m['type'] for m in moves)==dict(E=25,R=77,W=23,X=44)
 cfp=sum(m['cfp'] for m in moves);close(r['functional_control']['jh'],cfp*20/7)
 control=r['functional_control'];gap=control['jh']-a['total_stock_jh']
 close(control['alignment_vs_unrounded_java']['gap_jh'],gap)
 close(control['alignment_vs_unrounded_java']['gap_pct'],100*gap/a['total_stock_jh'])
 close(control['implied_java_hours_per_CFP'],a['total_stock_jh']*7/cfp)
 assert control['implied_rate_not_used_to_recalibrate'] and control['hours_per_CFP']==20
 og=r['odoo_gap']
 close(og['gap_jh'],o['total_stock_jh']-a['total_stock_jh'])
 close(og['base_difference_jh']+og['Flow_complement_difference_jh'],og['gap_jh'])
 close(sum(s['share_of_size_gap_pct'] for s in og['size_decomposition']),100)
 close(sum(s['descriptive_share_of_jh_gap'] for s in og['size_decomposition']),og['gap_jh'])
 assert len(og['source_witnesses'])==5 and all(w['measured_whole_method_nodes']>0 for w in og['source_witnesses'])
 months=c['C']*(total/c['effort_phase_factor']*c['day_hours']/c['month_hours']/c['SCED'])**F*c['schedule_phase_factor']
 close(months,r['schedule']['unrounded_months'])
 assert r['schedule']['proposed_months']==rounded(months,1)==10
 capacity=yaml.safe_load((ROOT/'source/deploiement-groupe.yaml').read_text(encoding='utf-8'))['calendrier_autonome']['capacite']['jours_productifs_etp_mois']
 close(r['schedule']['average_people'],total/10/capacity)
 retained=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))
 assert len(retained['units'])==1
 md=retained['units'][0];assert md['total_jh']==1500 and md['months']==17
 assert not any('stock' in x['id'] for x in retained['units'])
 assert r['cumulative']['retained_gross_jh']==1500
 assert r['cumulative']['proposed_java_gross_jh']==1840==sum(x['cumulative_proposed_jh'] for x in r['roles'])
 assert r['cumulative']['combined_months'] is None and r['cumulative']['schedules_are_not_added']
 assert r['progress']['retained']==6 and r['progress']['studied_in_current_method']==14 and r['progress']['new_capabilities_this_iteration']==0
 assert not r['active_business_model_changed'] and not r['application_changed']
 result=dict(passed=True,proposed_stock_jh=total,proposed_months=10,roles_total=sum(x['jh'] for x in r['roles']),
  native_estimates_preserved=4,source_witnesses=5,cosmic_movements_recounted=169,activities=7,roles=9,
  dependency_sha_checks=len(p['dependencies']),protected_active_inputs_unchanged=len(p['protected']),
  retained_cumulative_gross_jh=1500,proposed_cumulative_gross_jh=1840,retained_MD_months=17,stock_adopted=False,
  limitations='Contrôle des calculs, sources et frontières ; ne valide pas les tailles supposées, le taux ISBSG, la disponibilité des rôles ou la précision prédictive.')
 (OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
