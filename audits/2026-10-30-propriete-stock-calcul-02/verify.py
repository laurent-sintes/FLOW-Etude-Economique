"""Independent arithmetic, source and frozen-input checks for Ownership."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
from decimal import Decimal,ROUND_HALF_UP
import hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tmp/model-deps')]
import yaml
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def close(a,b):assert math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-9),(a,b)
def rounded(v,step):return int((Decimal(str(v))/Decimal(step)).quantize(Decimal('1'),rounding=ROUND_HALF_UP))*step
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 d=read('inputs.json');h=d['hypotheses'];r=read('results.json');f=read('input-freeze.json')
 for n,k in [('inputs.json','input_sha256'),('hypotheses.json','hypotheses_sha256'),('cosmic.json','cosmic_sha256')]:assert sha(OUT/n)==f[k]
 for collection in ['input_hashes','raw_source_hashes','protected_active_inputs']:
  for path,digest in d[collection].items():assert sha(ROOT/path)==digest,path
 assert len(h['modules'])==6 and len({m['id'] for m in h['modules']})==6
 assert len(h['schemas'])==10 and sum(len(s['fields']) for s in h['schemas'])==86
 assert sum(s['view'] for s in h['schemas'])==8
 c=d['cocomo'];E=c['B']+.01*c['SF_sum'];F=c['D']+.2*(E-c['B'])
 close(E,1.0997);close(F,.31794)
 phase=d['activities'];close(sum(phase['phase_effort_percent_of_base'])/100,c['effort_phase_factor'])
 close(sum(phase['phase_schedule_percent_of_base'])/100,c['schedule_phase_factor'])
 def effort(units,m=1):return c['A']*(units/1000)**E*m*c['SCED']*c['month_hours']/c['day_hours']*c['effort_phase_factor']
 for p,levels in d['banks'].items():
  for level,banks in levels.items():
   for name,bank in banks.items():
    for part in bank['source_slices']:
     close(max(part['direct_stock_floor'],part['raw_behavior_units']*part['attribution']),part['equivalent_program_units'])
    close(bank['program_units'],sum(p['equivalent_program_units'] for p in bank['source_slices']))
  for name in levels['central']:
   assert levels['lower'][name]['program_units']<=levels['central'][name]['program_units']<=levels['upper'][name]['program_units']
 rows=r['rows'];assert {row['id'] for row in rows}==set(h['native_references'])
 exact={}
 for row in rows:
  p=row['id'];template=d['schema_templates'][p];blocks=row['detail']['blocks'];pu_total=du_total=0
  for block in blocks:
   m=next(v for v in h['modules'] if v['id']==block['id'])
   bank=d['banks'][p]['central'][m['analogue']]['program_units']
   close(block['analogue_units'],bank);close(block['fraction'],m['central'])
   pu=bank*m['central']+d['new_module_scaffolding'][p]['program_units_per_new_service_module'];du=0
   for sc in h['schemas']:
    if sc['package']!=m['id']:continue
    n=len(sc['fields'])
    pu+=n*template['program_per_field']+template.get('program_per_new_model',0)
    du+=n*template['declarations_per_field']+template['per_new_model']+int(sc['view'])*(n*template['view_field']+template['view_model'])
   close(pu,block['program_units']);close(du,block['declarative_units'])
   close(pu+du,block['equivalent_units']);pu_total+=pu;du_total+=du
  config=sum(h['configuration'].values());du_total+=config
  close(pu_total,row['detail']['program_units']);close(du_total,row['detail']['declarative_units'])
  close(pu_total+du_total,row['total_equivalent_KSLOC']*1000)
  total=effort(pu_total+du_total);close(total,row['jh']);assert rounded(total,10)==row['rounded_jh']
  close(sum(x['allocated_jh'] for x in row['allocation']),total)
  close(sum(x['jh'] for x in row['activities']),total)
  for act in row['activities']:
   pub=next(a for a in phase['activities'] if a['id']==act['id'])
   fraction=Fraction(sum(x*y for x,y in zip(phase['phase_effort_percent_of_base'],pub['percent_by_phase'])),100*sum(phase['phase_effort_percent_of_base']))
   close(act['jh'],total*float(fraction))
  close(c['C']*(total/c['effort_phase_factor']*c['day_hours']/c['month_hours'])**F*c['schedule_phase_factor'],row['schedule_months'])
  assert len(row['sensitivities'])==6
  for sensitivity in row['sensitivities']:
   close(sensitivity['lower_jh']-total,sensitivity['lower_change_jh'])
   close(sensitivity['upper_jh']-total,sensitivity['upper_change_jh'])
   assert sensitivity['lower_jh']<=total<=sensitivity['upper_jh']
  pers=next(s for s in row['sensitivities'] if s['id']=='capacite-equipe')
  close(pers['lower_jh'],total*.83);close(pers['upper_jh'],total*1.26)
  behavior=sum(d['banks'][p]['central'][m['analogue']]['program_units']*m['central'] for m in h['modules'])
  fixed_program=pu_total-behavior
  def independently_sized(attribution='central',modules='central',override=None,w=1,multiplier=1):
   overrides=override or {}
   new_behavior=sum(d['banks'][p][attribution][m['analogue']]['program_units']*overrides.get(m['id'],m[modules]) for m in h['modules'])
   return effort(fixed_program+new_behavior+w*du_total,multiplier)
  cases={
   'attribution-des-analogues':(dict(attribution='lower'),dict(attribution='upper')),
   'volume-des-six-modules':(dict(modules='lower'),dict(modules='upper')),
   'registre-et-deux-dates':(dict(override={m['id']:m['lower'] for m in h['modules'] if m['id'] in ('OWN-F04','OWN-F05')}),dict(override={m['id']:m['upper'] for m in h['modules'] if m['id'] in ('OWN-F04','OWN-F05')})),
   'poids-declaratif':(dict(w=.5),dict(w=2)),
   'capacite-equipe':(dict(multiplier=.83),dict(multiplier=1.26)),
   'experience-ecosysteme':(dict(multiplier=.87),dict(multiplier=1.12))}
  for sensitivity in row['sensitivities']:
   low,high=cases[sensitivity['id']]
   close(independently_sized(**low),sensitivity['lower_jh'])
   close(independently_sized(**high),sensitivity['upper_jh'])
  exact[p]=total
 cosmic=read('cosmic.json');review=read('cosmic-refinement.json')
 assert sha(OUT/'cosmic-refinement.json')==read('refinement-freeze.json')['cosmic_refinement_sha256']
 assert review['base_sha256']==sha(OUT/'cosmic.json') and review['unchanged_effort_inputs']
 base=[m for p in cosmic['processes'] for m in p['movements']]
 assert sum(m['cfp'] for m in base)==76
 combined=Counter(m['type'] for m in base)
 for m in review['add_movements']:
  assert m['process'] in {p['id'] for p in cosmic['processes']}
  assert not any(m['type']==x['type'] and m['group']==x['group'] for p in cosmic['processes'] if p['id']==m['process'] for x in p['movements'])
  combined[m['type']]+=1
 assert dict(combined)==dict(E=9,R=35,W=15,X=21)
 cf=r['functional_control'];assert cf['CFP']==sum(combined.values())==80 and cf['groups']==21 and cf['processes']==9
 close(cf['jh'],80*20/7);assert cf['factor']==1
 assert sum(p['CFP'] for p in cf['process_counts'])==80
 for row in rows:
  close(row['alignment_COSMIC']['gap_jh'],cf['jh']-row['jh'])
  close(row['alignment_COSMIC']['gap_pct'],100*(cf['jh']-row['jh'])/row['jh'])
  close(row['implied_hours_per_CFP'],row['jh']*7/80)
 retained=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))['units']
 assert [(u['total_jh'],u['months']) for u in retained]==[(1500,17),(340,10)]
 assert len({c['id'] for u in retained for c in u['capabilities']})==14
 assert r['cumulative']['retained_gross_jh']==1840
 assert not r['active_model_changed'] and not r['application_changed'] and not r['adoption']
 assert r['cumulative']['arithmetic_java_candidate_if_adopted_jh']==1940
 report=dict(id=h['id'],status='estimations_natives_proposees_non_adoptees',unit='Gestion de la propriété du stock, BC-014 et BC-015',
  estimates=[dict(reference=row['label'],jh=row['rounded_jh'],unrounded_jh=row['jh'],equivalent_units=row['detail']['equivalent_units'],
    local_COCOMO_months=row['schedule_months'],alignment_COSMIC=row['alignment_COSMIC']) for row in rows],
  meaning='Charges supplémentaires de construction du périmètre cible Flow dans chaque écosystème natif, en supposant le patrimoine Master Data et Stock disponible. Pas coûts historiques observés, pas quatre budgets à additionner.',
  size_basis=dict(modules=h['modules'],schema_count=10,specific_fields=86,viewed_models=8,
   templates=d['schema_templates'],configuration=h['configuration'],
   analogue_banks={p:{name:b['program_units'] for name,b in v['central'].items()} for p,v in d['banks'].items()},
   effort_conversion='Les tailles des six modules, structures, modèles/vues et configurations sont additionnées avant COCOMO. Les budgets existants ne sont pas ajoutés à la taille de cette famille.',
   source_note='Mesures source issues des chaînes figées de Stock, utilisées comme analogies de comportement nouveau. Fractions supposées par ingénierie, pas normes de marché.'),
  module_allocations={row['label']:row['allocation'] for row in rows},
  allocation_note='Répartition descriptive des JH de la famille proportionnelle à sa taille estimée, pas six estimations COCOMO indépendantes.',
  reuse=dict(policy=h['reuse_policy'],funding_context=d['existing_foundation'],
   undelivered_dependency='Orders et orchestration restent à estimer ; seuls les contrats, références d’actes et états locaux de propriété sont chiffrés. Ne pas supposer ces familles déjà financées.'),
  functional_control=cf,
  comparability=dict(activity_note=h['COSMIC_policy']['activity_note'],component_boundary=h['COSMIC_policy']['scope_caveat'],
   native_technology_note='Le repère 20 h/CFP est historique Java ; il ne calibre pas les technologies Python, ni la réutilisation des familles disponibles.',
   algorithm_note='La compacité des chaînes Java et le proxy de code non calibré entre langages expliquent une partie du désaccord ; ce n’est pas une preuve de productivité Spring.',
   guarantees=h['architecture'],no_forced_convergence=True,no_probabilistic_confidence=True),
  sensitivities={row['label']:row['sensitivities'] for row in rows},
  cocomo_parameters=c,activity_source=d['activities'],
  significant_assumptions=[h['rule_policy'],h['sizing_policy'],h['schema_status'],h['architecture'],h['base_policy']],
  cumulative=r['cumulative'],progress=r['progress'],conclusions=r['conclusions'],
  confidence_probability=None,observed_project_effort=None,human_review=None,
  active_business_model_changed=False,retained_master_data_and_stock_preserved=True,
  evidence=['hypotheses.json','inputs.json','input-freeze.json','cosmic.json','cosmic-refinement.json','refinement-freeze.json','results.json','verification.json'])
 (OUT/'bilan.yaml').write_text(yaml.safe_dump(report,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
 result=dict(passed=True,native_estimates=4,native_rounded_jh={row['id']:row['rounded_jh'] for row in rows},
  frozen_effort_inputs_unchanged=True,original_COSMIC_evidence_preserved=True,CFP_before_review=76,CFP_after_review=80,
  movements=dict(combined),functional_control_jh=cf['jh'],six_modules_reconstructed=True,schemas=10,specific_fields=86,
  activities_preserved=7,sensitivity_pairs_checked=24,verified_raw_source_files=len(d['raw_source_hashes']),
  retained_gross_jh=1840,retained_capabilities=14,proposed_or_retained_capabilities=16,
  active_sources_unchanged=True,adoption=False,application_changed=False)
 save('verification.json',result)
 paths=[p for p in OUT.iterdir() if p.is_file() and p.name!='provenance.json']
 save('provenance.json',dict(outputs={p.name:sha(p) for p in sorted(paths)},
  protected_active_inputs=d['protected_active_inputs'],evidence_dependencies=d['input_hashes'],native_source_hashes=d['raw_source_hashes']))
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
