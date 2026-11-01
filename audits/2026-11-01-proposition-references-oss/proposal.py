"""Reproduce an unadopted proposal from the reference audit and canonical COCOMO rules.
Writes only into this proposal folder. Active model and application are hash-protected.
"""
from pathlib import Path
import sys,json,hashlib,ast,math,collections
ROOT=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
from validate_stacks import read
from model_context import model_session
from estimation_calculation import calculate,formula,rounded
from estimation_components import unpack_archives

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):(P/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(path):return json.loads(path.read_text(encoding='utf-8'))
H=load(P/'hypotheses.json');AUDIT=ROOT/H['baseline'];R=load(AUDIT);U={u['id']:u for u in R['units']}
PREVIOUS_PROTECTED=load(AUDIT.parent/'protected-before.json')
if (P/'protected-before.json').exists():
    PROTECTED=load(P/'protected-before.json')
else:
    PROTECTED={path:sha(ROOT/path) for path in PREVIOUS_PROTECTED}
    save('protected-before.json',PROTECTED)
PREEXISTING_CHANGES=[path for path in PROTECTED if PROTECTED[path]!=PREVIOUS_PROTECTED[path]]
# The project is shared with editorial work. Only valuation dependencies block the
# calculation. Unrelated concurrent changes are recorded, never reverted.
from retained_core import dependencies as retained_dependencies
with model_session(): CORE_PROTECTED={name:sha(ROOT/name) for name in retained_dependencies()}
RUN_PROTECTED={path:sha(ROOT/path) for path in PROTECTED}
INPUTS={H['baseline']:sha(AUDIT),H['arbitrations']:sha(ROOT/H['arbitrations']),'hypotheses.json':sha(P/'hypotheses.json')}
raw=unpack_archives(read(ROOT/'audits/2026-10-30-core-adoption-09/archives.json'));F={f['slug']:f for f in raw['proposal_inputs']['families']}
prof=read(ROOT/'audits/2026-10-30-audit-fonctions-transverses/proposal-inputs.json');repos=prof['measurements']['repos']
own=read(ROOT/'audits/2026-10-30-propriete-stock-calcul-02/inputs.json');oh=own['hypotheses'];jt=own['schema_templates']['axelor'];scaffold=own['new_module_scaffolding']['axelor']['program_units_per_new_service_module']
# Behavioural analogues are transposed in the existing logical-unit convention.
# Java structures, declarations and existing base/shared components are retained.
BANKS={};MEASURES={}
for sid,selection in H['selectors'].items():
    family=F[selection['family']];atoms=set();files=[]
    for suffix,names in selection['files'].items():
        matches=[b for b in family['bindings'] if b['product']==selection['product'] and b['path'].endswith('/'+suffix)]
        assert matches,(sid,suffix)
        found=set()
        for b in matches:
            source=ROOT/repos[b['repo']]['root']/b['path'];assert sha(source)==b['sha256'],str(source)
            tree=ast.parse(source.read_text(encoding='utf-8'));functions=[n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]
            kept=[];counts=collections.Counter()
            for atom in b['atoms']:
                if atom['structural']:continue
                containers=[f for f in functions if f.lineno<=atom['start']<=f.end_lineno]
                fn=min(containers,key=lambda f:f.end_lineno-f.lineno) if containers else None
                if fn is not None and fn.name in names:
                    key=(b['repo'],b['path'],atom['key'])
                    if key not in atoms:counts[fn.name]+=1;kept.append(atom['key']);atoms.add(key)
                    found.add(fn.name)
            files.append(dict(repo=b['repo'],path=b['path'],sha256=b['sha256'],commit=repos[b['repo']]['commit'],methods=dict(counts),atoms=kept))
        assert set(names)<=found,(sid,'unmeasured methods',set(names)-found)
    assert atoms,sid
    BANKS[sid]=len(atoms);MEASURES[sid]=dict(product=selection['product'],family=selection['family'],units=len(atoms),reason=selection['reason'],files=files)

with model_session():
    baseline=read(ROOT/'source/estimations-core-retenues.yaml')['units'];assert len(baseline)==11
    for u in baseline:
        replay=calculate(u['calculation']);old=U[u['id']]
        assert replay['total_jh']==old['adopted_jh']==u['total_jh']
        for row in replay['alignment']['rows']:
            expected=next(x for x in old['comparisons'] if x['id']==row['id']);assert math.isclose(row['jh'],expected['jh'],rel_tol=1e-12)
    assert sum(u['total_jh'] for u in baseline)==6660
    # The same target funding identities are kept. No source analogue creates another budget owner.
    from estimation_inputs import registry
    reg=registry();funded={};claims=[]
    for u in baseline:
        c=next(c for c in reg['calculations'] if c['id']==u['calculation']['id'])
        for claim in c['funding_claims']:
            if claim['mode']=='funded':
                assert claim['mechanism'] not in funded,claim['mechanism'];funded[claim['mechanism']]=u['id']
            claims.append(dict(unit=u['id'],**claim))

def effort(id,size):
    c=U[id]['cocomo'];E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum'])
    return formula('cocomo_effort',A=c['A'],KSLOC=size/1000,E=E,EM=c['other_EM'],SCED=c['SCED'],month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor'])

def ownership_size(overrides,foreign):
    blocks=[]
    for m in oh['modules']:
        choice=overrides.get(m['id'],dict(product='axelor',bank=m['analogue']))
        product=choice['product'];bank=own['banks'][product]['central'][choice['bank']]['program_units']
        factor=foreign if product!='axelor' else 1
        program=formula('module_analogy',reference_units=bank*factor,fraction=m['central'],scaffold_units=scaffold)
        declarations=0
        for schema in oh['schemas']:
            if schema['package']!=m['id']:continue
            n=len(schema['fields']);v=int(schema['view'])
            program+=n*jt['program_per_field']+jt.get('program_per_new_model',0)
            declarations+=n*jt['declarations_per_field']+jt['per_new_model']+v*(n*jt['view_field']+jt['view_model'])
        blocks.append(dict(id=m['id'],name=m['name'],product=product,bank=choice['bank'],reference_units=bank,equivalence_factor=factor,fraction=m['central'],program_units=program,declarative_units=declarations,equivalent_units=program+declarations,reason=choice.get('reason')))
    config=sum(oh['configuration'].values());size=sum(x['equivalent_units'] for x in blocks)+config
    return size,dict(blocks=blocks,configuration_units=config,java_template=jt,java_scaffold=scaffold)

# Check that the separate ownership implementation reproduces the old Java size.
old_own_size=U['inventory-ownership-java-spring']['size_trace']['ownership_sizes']['axelor']['equivalent_units']
assert math.isclose(ownership_size({},1)[0],old_own_size,rel_tol=1e-12)

# Professional baskets use the original per-file measures and existing credits.
raw_groups=R['professional']['raw_equivalent_units'];cleaned={};removed={}
for group,patterns in [('admin-security',H['professional']['admin_supplied_patterns']),('operations-lifecycle',H['professional']['operations_supplied_patterns'])]:
    files=R['professional']['files'][group]['axelor'];excluded=[f for f in files if any(pattern in '/'+f['path'] for pattern in patterns)]
    removed[group]=[dict(path=f['path'],repo=f['repo'],sha256=f['sha256'],net_units=f['program_units']+f['declarative_units']-f['existing_MD_credit_units']) for f in excluded]
    cleaned[group]=raw_groups[group]['axelor']-sum(f['net_units'] for f in removed[group])
    assert cleaned[group]>0
bundle_files=[f for f in R['professional']['files']['process-studio']['axelor'] if f['path'] in H['professional']['removed_studio_files']]
assert len(bundle_files)==len(H['professional']['removed_studio_files'])
bundle_units=sum(f['program_units']+f['declarative_units']-f['existing_MD_credit_units'] for f in bundle_files)
assert bundle_units==897
cleaned['process-studio']=raw_groups['process-studio']['axelor']-bundle_units
for g in ('human-forms','data-services','supply-workbenches'):cleaned[g]=raw_groups[g]['axelor']
cleaned['analytics-mining']=max(raw_groups['analytics-mining'].values())

def proposal(foreign=1,fraction_overrides=None):
    fraction_overrides=fraction_overrides or {};result=[]
    for b in baseline:
        id=b['id'];old=U[id];detail={};size=None
        if id in H['preserved_units']:
            days=b['total_jh'];raw_jh=next(x['jh'] for x in old['comparisons'] if x['id']=='axelor');kind='preserved_active_decision'
        else:
            kind='recalculated_proposal'
            if id=='inventory-ownership-java-spring':size,detail=ownership_size(H['ownership'],foreign)
            elif old['recipe']=='coherent_components_v1':
                size=0;parts=[]
                for family,products in old['families'].items():
                    target=products['axelor'];ref=target['analogue'];newref=ref;product='axelor';choice=H['families'].get(family)
                    if choice:
                        if choice['kind']=='selected_methods':
                            key=choice['selector'];newref=BANKS[key];product=MEASURES[key]['product']
                        elif choice['kind']=='native_bank':product=choice['product'];newref=products[product]['analogue']
                        elif choice['kind']=='stock_bank':product=choice['product'];newref=own['banks'][product]['central'][choice['bank']]['program_units']
                        else:raise AssertionError(choice)
                    factor=foreign if product!='axelor' else 1
                    f=F[family];delta=(newref*factor-ref)*f['extension_fraction']*f['quantity']
                    value=target['total']+delta
                    assert value>0
                    size+=value;parts.append(dict(family=family,modules=f['module_names'],product=product,old_bank=ref,new_bank=newref,equivalence_factor=factor,fraction=f['extension_fraction'],module_count=f['quantity'],baseline_size=target['total'],delta_size=delta,candidate_size=value,java_fixed_size=target['total']-ref*f['extension_fraction']*f['quantity'],basis=choice['reason'] if choice else 'Analogue Java et réutilisations inchangés.'))
                detail=dict(families=parts)
            elif id=='process-management-java-spring':
                base=old['size_trace']['component_sizes']['axelor']['native_base_units'];parts=[]
                for g in ('process-studio','human-forms','analytics-mining'):
                    fraction=fraction_overrides.get(g,prof['groups'][g]['fraction']);parts.append(dict(group=g,bank=cleaned[g],fraction=fraction,size=cleaned[g]*fraction,reference='odoo' if g=='analytics-mining' else 'axelor'))
                size=base+sum(x['size'] for x in parts);detail=dict(base=base,groups=parts,removed_bundle_units=bundle_units)
            elif id=='supply-workbenches-java-spring':
                fraction=fraction_overrides.get('supply-workbenches',prof['groups']['supply-workbenches']['fraction']);size=cleaned['supply-workbenches']*fraction;detail=dict(groups=[dict(group='supply-workbenches',bank=cleaned['supply-workbenches'],fraction=fraction,size=size,reference='axelor')])
            elif id=='professional-it-java-spring':
                parts=[]
                for g in ('admin-security','operations-lifecycle','data-services'):
                    fraction=fraction_overrides.get(g,prof['groups'][g]['fraction']);parts.append(dict(group=g,bank=cleaned[g],fraction=fraction,size=cleaned[g]*fraction,reference='axelor'))
                size=sum(x['size'] for x in parts);detail=dict(groups=parts,removed_supplied_components=removed)
            else:raise AssertionError(id)
            raw_jh=effort(id,size);days=rounded(raw_jh,old['rounding_jh'])
        assert days>0 and math.isfinite(raw_jh)
        result.append(dict(id=id,label=b['label'],status=kind,adopted_jh=b['total_jh'],proposal_jh=days,delta_jh=days-b['total_jh'],delta_pct=100*(days/b['total_jh']-1),raw_proposal_jh=raw_jh,equivalent_units=size,rounding_jh=old['rounding_jh'],calculation_details=detail,capabilities=b['capabilities'],professional_functions=b.get('professional_functions',[])))
    return result
CENTRAL=proposal();total=sum(x['proposal_jh'] for x in CENTRAL);assert sum(x['delta_jh'] for x in CENTRAL)==total-6660
sensitivity=[]
for factor in H['method']['foreign_analogue_sensitivity']:
    rows=proposal(foreign=factor);sensitivity.append(dict(id='new_foreign_analogue_units',value=factor,total_jh=sum(x['proposal_jh'] for x in rows),unit_deltas={x['id']:x['proposal_jh']-next(c['proposal_jh'] for c in CENTRAL if c['id']==x['id']) for x in rows}))
assert sensitivity[0]['total_jh']<=total<=sensitivity[1]['total_jh']
for group in prof['groups']:
    for value in prof['groups'][group]['test_values']:
        rows=proposal(fraction_overrides={group:value});sensitivity.append(dict(id=group,value=value,total_jh=sum(x['proposal_jh'] for x in rows),delta_vs_central=sum(x['proposal_jh'] for x in rows)-total))
for path,expected in CORE_PROTECTED.items():assert sha(ROOT/path)==expected,path
OBSERVED_EXTERNAL_CHANGES={path:dict(before=expected,after=sha(ROOT/path)) for path,expected in PROTECTED.items() if sha(ROOT/path)!=expected}
DURING_RUN_CHANGES=[path for path,expected in RUN_PROTECTED.items() if sha(ROOT/path)!=expected]
save('calculation-inputs-protected.json',CORE_PROTECTED)
result=dict(id=H['id'],date=H['date'],status=H['status'],adopted_jh=6660,proposal_jh=total,delta_jh=total-6660,delta_pct=100*(total/6660-1),inputs_sha256=INPUTS,preexisting_changes_since_audit=PREEXISTING_CHANGES,observed_external_changes_since_proposal_start=OBSERVED_EXTERNAL_CHANGES,unrelated_changes_during_run=DURING_RUN_CHANGES,method=H['method'],units=CENTRAL,measured_analogue_selections=MEASURES,professional_cleaned_banks=cleaned,professional_removed_components=removed,sensitivity=sensitivity,funding_claims=claims,checks=dict(writes_limited_to_proposal_folder=True,calculation_inputs_unchanged=True,protected_calculation_files=len(CORE_PROTECTED),observed_external_content_changes=len(OBSERVED_EXTERNAL_CHANGES),baseline_replayed_units=11,baseline_replayed_oss_results=44,units=11,native_capabilities=88,funding_owners=len(funded),adopted_jh=6660,source_methods_measured=True,ownership_baseline_size_reproduced=True))
save('results.json',result);save('checks.json',dict(status='passed',**result['checks']))
print(json.dumps({k:result[k] for k in ('proposal_jh','adopted_jh','delta_jh','delta_pct')},ensure_ascii=False))
for u in CENTRAL:print(u['id'],u['adopted_jh'],'->',u['proposal_jh'],'delta',u['delta_jh'])
print('selected banks',BANKS);print('cleaned professional banks',cleaned)
