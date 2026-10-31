"""Reproduce adopted professional components from the frozen, pre-adoption estimate."""
from copy import deepcopy
from estimation_inputs import require

def prepare_professional(documents,contract,registry,formula,use_cache=False):
 from core_product_estimate import calculate,functional_forecast
 d=documents[contract['inputs']['proposal_inputs']];basis=documents[contract['inputs']['adoption_basis']]
 require(basis['id']=='professional-product-adoption-basis','Invalid adoption basis')
 kind=contract['recipe_parameters']['professional_component']
 require(contract['recipe_parameters']['scenario']=='central' and contract['recipe_parameters']['structure_units_per_group']==0,'Unsupported professional parameters')
 require(len(contract['recipe_parameters']['module_groups'])==len(set(contract['recipe_parameters']['module_groups'])),'Duplicate professional group')
 mapping={'process-management':('process_size','process_raw_jh','process_base_units',['process-studio','human-forms','analytics-mining']),'supply-workbenches':('workbench_size','workbench_raw_jh',None,['supply-workbenches']),'professional-it':('it_size','it_raw_jh',None,['admin-security','operations-lifecycle','data-services'])}
 require(kind in mapping,'Unknown professional component')
 if contract['scope']['level']=='professional_function_group':require(contract['scope']['professional_group_id']==kind,'Professional group identity mismatch')
 from estimation_preparation import validate_allocation
 original=next(u for u in basis['baseline_units'] if u['id']=='process-management-java-spring')
 check=dict(role_labels={r['id']:r['label'] for r in original['roles']},activity_role_weights={a['id']:a['role_weights'] for a in original['activities']},rounding_jh=10,role_rounding_jh=1)
 validate_allocation(basis['activity_source'],check,d['cocomo'])
 result=calculate(d,basis['baseline_units'],rule_function=formula);index={'process-management':0,'supply-workbenches':1,'professional-it':2};selected=result['rows'][index[kind]]
 size_key,jh_key,base_key,groups=mapping[kind];c=d['cocomo'];E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum'])
 def effort(size):return formula('cocomo_effort',A=c['A'],KSLOC=size/1000,E=E,EM=c['other_EM'],SCED=c['SCED'],month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor']) if size else 0
 rows=[];sizes={}
 for row in result['comparative_rows']:
  base=row[base_key] if base_key else 0;common=effort(base)
  rows.append(dict(id=row['id'],label=dict(erpnext='ERPNext + Frappe',odoo='Odoo Community',tryton='Tryton + Sao',axelor='Axelor + Platform + Studio')[row['id']],jh=row[jh_key],common_jh=common,complements_jh=row[jh_key]-common))
  sizes[row['id']]=dict(equivalent_units=row[size_key],native_base_units=base,new_equivalent_units=row[size_key]-base)
 f=functional_forecast(d);cfp=f['process_CFP'] if kind=='process-management' else sum(f['CFP_by_group'][g] for g in groups)
 processes=f['process_count'] if kind=='process-management' else sum(f['process_counts'][g] for g in groups)
 functional=dict(CFP=cfp,hours_per_CFP=d['cosmic']['hours_per_CFP'],factor=1,day_hours=d['cosmic']['day_hours'])
 require(functional['day_hours']==c['day_hours'],'Professional JH convention mismatch')
 funcs=sorted({f for g in groups for f in d['measurements']['groups'][g]['functions']})
 require(funcs==sorted(contract['scope']['professional_functions']),'Professional function scope mismatch')
 require(set(groups)==set(contract['recipe_parameters']['module_groups']),'Professional group boundary mismatch')
 funded={x['mechanism'] for x in contract['funding_claims'] if x['mode']=='funded'}
 actual={m['basis']['scope'] for m in registry['mechanisms'] if m['id'] in funded and m['basis']['kind']=='professional_group'}
 require(actual==set(groups),'Professional funding boundary mismatch')
 require(sum(selected['roles'].values())==selected['jh'],'Professional role conservation')
 selected_sizes=sizes['axelor'];allocation=dict(selected_reference='axelor',rounding_jh=10,role_rounding_jh=1,schedule_rounding_months=.1,role_labels={r['id']:r['label'] for r in result['roles']},role_effort_jh=selected['roles'],role_allocation_basis='Répartition organisationnelle de la proposition adoptée ; distincte des distributions publiées d’activités COCOMO.')
 return dict(cocomo=c,allocation=allocation,rows=rows,functional=functional,activity_source=deepcopy(basis['activity_source']),trace=dict(recorded_files=len(d['measurements']['files']),blocks=len(groups),refined_blocks=0,method_samples=0,complement_units=selected_sizes['new_equivalent_units'],complement_parts=selected_sizes,processes=processes,groups=len(groups),CFP=cfp,movements={},reuse_factor=0,component_sizes=sizes,professional_component=kind,module_groups=groups,role_allocation_basis=allocation['role_allocation_basis']),work_items=[('professional_group',g,g,result['groups_equivalent_units'][g]['axelor']) for g in groups])
