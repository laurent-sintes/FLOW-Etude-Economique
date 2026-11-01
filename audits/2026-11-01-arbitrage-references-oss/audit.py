"""Read-only audit of the adopted OSS references. Writes only into this audit folder."""
from pathlib import Path
import sys,json,hashlib,math,subprocess
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from validate_stacks import read
from model_context import model_session
from estimation_calculation import calculate,formula
from estimation_inputs import contract,_frozen_calculation_proofs,registry
from estimation_preparation import prepare
from estimation_stock import prepare_stock
from estimation_components import compile_components,unpack_archives
HERE=Path(__file__).resolve().parent
PRODUCTS=('erpnext','odoo','tryton','axelor')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(name,value): (HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def protected():
    paths=[ROOT/'AGENTS.md',ROOT/'package.json',ROOT/'app/package.json',ROOT/'app/dist/site-manifest.json']
    for prefix in ('source','config','tools','app/src','app/public'):
        paths.extend(p for p in (ROOT/prefix).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc',))
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(paths)) if p.is_file()}
before=protected()
if (HERE/'protected-before.json').exists():
    assert before==json.loads((HERE/'protected-before.json').read_text(encoding='utf-8')),'Protected project files changed since audit started'
else:dump('protected-before.json',before)
with model_session():
    retained=read(ROOT/'source/estimations-core-retenues.yaml')['units'];reg=registry();units=[];details=None
    for unit in retained:
        c=calculate(unit['calculation']);spec,reg=contract(unit['calculation']);docs=_frozen_calculation_proofs(reg)
        pp=prepare(docs,spec,reg,formula,use_cache=True)
        if spec['recipe']=='coherent_components_v1' and details is None:
            inputs={k:docs[v] for k,v in spec['inputs'].items()};sp=inputs['specification'];supplier=next(x for x in reg['calculations'] if x['id']==sp['analogue_calculation_id'])
            st=prepare_stock(docs,supplier,reg,formula);details=compile_components(inputs['archives'],inputs['native_inputs'],st,formula)
        record=dict(id=unit['id'],label=unit['label'],adopted_jh=unit['total_jh'],capabilities=unit['capabilities'],professional_functions=unit.get('professional_functions',[]),calculation_id=unit['calculation']['id'],recipe=spec['recipe'],inputs=spec['inputs'],parameters=spec['recipe_parameters'],selected_reference=c['alignment']['reference_id'],comparisons=c['alignment']['rows'],spread_jh=c['alignment']['spread_jh'],spread_pct_of_selected=c['alignment']['spread_pct'],comparison_scope=spec['comparison'],size_trace=c['trace'],rounding_jh=pp['allocation']['rounding_jh'],historical_selection_rationale=docs.get(spec['inputs'].get('allocation'),{}).get('selection_rationale'),cocomo=pp['cocomo'])
        if spec['recipe']=='coherent_components_v1':
            group=next(g for g in details['groups'].values() if g['id']==pp['trace']['coherent_unit'])
            record['families']={f:details['details'][f] for f in group['families']}
        units.append(record)
    assert len(units)==11 and sum(u['adopted_jh'] for u in units)==6660
    caps=[c['id'] for u in units for c in u['capabilities']];assert len(caps)==len(set(caps))==88
    for u in units:
        assert {r['id'] for r in u['comparisons']}==set(PRODUCTS)
        assert calculate({'id':u['calculation_id']})['total_jh']==u['adopted_jh']
    frozen=unpack_archives(read(ROOT/'audits/2026-10-30-core-adoption-09/archives.json'))
    families=frozen['proposal_inputs']['families']
    family_sources={f['slug']:dict(name=f['name'],scope=f['scope'],modules=f['module_names'],quantity=f['quantity'],fraction=f['extension_fraction'],schemas=f['schemas'],analogue_provider=f.get('analogue_provider'),additional_modules=f.get('additional_modules'),bindings={p:[dict(repo=b['repo'],path=b['path'],sha256=b['sha256'],provided_kernel=b['provided_kernel'],atoms=len(b['atoms']),structural_atoms=sum(bool(a['structural']) for a in b['atoms']),selected_names=sorted({a.get('name','') for a in b['atoms'] if a.get('name') and not a['structural']})) for b in f['bindings'] if b['product']==p] for p in PRODUCTS}) for f in families}
    prof=read(ROOT/'audits/2026-10-30-audit-fonctions-transverses/proposal-inputs.json')
    coherent_verified=set()
    for family in families:
        for binding in family['bindings']:
            source=ROOT/prof['measurements']['repos'][binding['repo']]['root']/binding['path']
            assert source.is_file() and sha(source)==binding['sha256'],str(source)
            coherent_verified.add((binding['repo'],binding['path']))
    raw={g:dict.fromkeys(PRODUCTS,0.) for g in prof['groups']};credits={g:dict.fromkeys(PRODUCTS,0.) for g in prof['groups']};physical={g:dict.fromkeys(PRODUCTS,0) for g in prof['groups']}
    file_groups={g:{p:[] for p in PRODUCTS} for g in prof['groups']};verified=0;missing=[]
    for f in prof['measurements']['files']:
        g,p=f['group'],f['product'];raw[g][p]+=f['program_units']+f['declarative_units']-f['existing_MD_credit_units'];credits[g][p]+=f['existing_MD_credit_units'];physical[g][p]+=f['physical_lines'];file_groups[g][p].append({k:f[k] for k in ('repo','path','sha256','commit','program_units','declarative_units','existing_MD_credit_units')})
        local=ROOT/prof['measurements']['repos'][f['repo']]['root']/f['path']
        if local.is_file():assert sha(local)==f['sha256'],str(local);verified+=1
        else:missing.append(str(local.relative_to(ROOT)))
    assert max(raw['analytics-mining'],key=raw['analytics-mining'].get)=='odoo'
    for path,proof in reg['proofs'].items():assert sha(ROOT/path)==proof['sha256'],path
    result=dict(date='2026-11-01',mode='audit_only_no_adoption',units=units,ranking=sorted([dict(id=u['id'],spread_pct=u['spread_pct_of_selected'],maximum_to_minimum=max(r['jh'] for r in u['comparisons'])/min(r['jh'] for r in u['comparisons'])) for u in units],key=lambda r:-r['spread_pct']),families=family_sources,professional=dict(groups=prof['groups'],raw_equivalent_units=raw,credits=credits,physical_lines=physical,files=file_groups,repos=prof['measurements']['repos'],local_files_verified=verified,local_files_unavailable=missing),schema_templates=read(ROOT/'audits/2026-10-30-propriete-stock-calcul-02/inputs.json')['schema_templates'],coherent_source_files_verified=len(coherent_verified),proofs_verified=len(reg['proofs']),checks=dict(lots=11,oss_results=44,unique_capabilities=88,adopted_jh=6660,coherent_source_files_verified=len(coherent_verified),raw_alignment_reproduced=True,adopted_amounts_untouched=True))
    dump('results.json',result)
after=protected();assert before==after,'Audit modified protected project files'
dump('checks.json',dict(status='passed',protected_files=len(before),protected_unchanged=True,**result['checks']))
print(json.dumps(dict(status='passed',protected_files=len(before),proofs_verified=result['proofs_verified'],local_professional_files_verified=verified,local_professional_files_unavailable=len(missing),ranking=result['ranking']),ensure_ascii=False))
