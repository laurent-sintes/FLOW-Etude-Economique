"""Coherent opportunity units from frozen code evidence, with shared work funded once."""
from collections import Counter,defaultdict
import base64,gzip,hashlib,json
from model_context import CURRENT
from estimation_inputs import require,digest
from estimation_preparation import number,unique,close,validate_allocation
from estimation_stock import prepare_stock

PRODUCTS=('erpnext','odoo','tryton','axelor')
def product(repo):
    return 'erpnext' if repo=='frappe' else 'axelor' if repo in ('studio','platform') else repo

def unpack_archives(archive):
    require(archive['format']=='flow-estimation-evidence-archive-v1','Unknown evidence archive')
    result={}
    for name,entry in archive['documents'].items():
        require(entry['encoding']=='gzip+base64','Unknown evidence encoding')
        raw=gzip.decompress(base64.b64decode(entry['data'],validate=True))
        require(hashlib.sha256(raw).hexdigest()==entry['sha256'],'Archived evidence changed')
        result[name]=json.loads(raw.decode('utf-8-sig'))
    require(set(result)=={'proposal_inputs','proposal_results','common_measures','common_adjustment','funding','catalog'},'Incomplete evidence archive')
    return result

def compile_components(archive,ni,stock,formula):
    raw=unpack_archives(archive);d=raw['proposal_inputs'];m=raw['common_measures'];adjust=raw['common_adjustment']
    require(d['cocomo']==ni['cocomo']==stock['cocomo'],'Component COCOMO parameters')
    specs=unique(m['specification']['mechanisms'],'id','common mechanism')
    owned={};counts={k:dict.fromkeys(PRODUCTS,0) for k in specs}
    for x in m['source_node_ownership']:
        key=(x['repo'],x['path'],x['atom'])
        require(key not in owned,'Duplicate common base atom')
        owned[key]=x['mechanism'];counts[x['mechanism']][product(x['repo'])]+=1
    require(counts==m['base_units_owned_once'],'Common base count mismatch')
    banks={k:dict.fromkeys(PRODUCTS,0) for k in specs}
    for binding in m['bindings']:
        if binding['kind']=='program':banks[binding['mechanism']][binding['product']]+=len(binding['atoms'])
    correction={p:stock['trace']['stock_sizes'][p]['bank']['correction_chain'] for p in PRODUCTS}
    for id,spec in specs.items():
        if spec.get('provider')=='stock_correction':banks[id]=correction.copy()
        for p in PRODUCTS:close(banks[id][p],m['bank_program_units'][id][p],'Common analogue count')
    sourceowners={}
    for key,mechanism in owned.items():
        if product(key[0]) not in adjust['base_exclusions'].get(mechanism,[]):
            sourceowners[key]=specs[mechanism]['owner']
    families=unique(d['families'],'slug','component family')
    priority=['orders','master-plan','plan-preparation','optimization','service-planning']
    priority += [x for x in families if x not in priority]
    localbank={};localbase={}
    files={};all_sources=raw['catalog']['sources']+m['sources']
    for src in all_sources:
        key=(src['repo'],src['path'])
        if key in files:require(files[key]==src['sha256'],'Source file provenance mismatch')
        files[key]=src['sha256']
    for slug in priority:
        f=families[slug];localbank[slug]=dict.fromkeys(PRODUCTS,0);localbase[slug]=dict.fromkeys(PRODUCTS,0);seen=set()
        require(f['quantity']==len(f['module_names']) and f['quantity']>0,'Component module quantity')
        require(len(set(f['module_names']))==f['quantity'],'Duplicate component module')
        number(f['extension_fraction'],'component fraction')
        unique(f['schemas'],'name','component model')
        for binding in f['bindings']:
            require(binding['product']==product(binding['repo']),'Source ecosystem mismatch')
            require(files[(binding['repo'],binding['path'])]==binding['sha256'],'Source selection provenance')
            require(type(binding['provided_kernel']) is bool,'Supplied kernel status')
            keys=[a['key'] for a in binding['atoms']]
            require(len(keys)==len(set(keys)),'Duplicate selected source atom')
            for atom in keys:
                key=(binding['repo'],binding['path'],atom)
                if key in seen:continue
                seen.add(key);localbank[slug][binding['product']]+=1
                if not binding['provided_kernel'] and key not in sourceowners:
                    sourceowners[key]=slug;localbase[slug][binding['product']]+=1
    common={slug:dict.fromkeys(PRODUCTS,0.) for slug in families}
    commonbase={slug:dict.fromkeys(PRODUCTS,0.) for slug in families}
    for id,spec in specs.items():
        for p in PRODUCTS:
            t=ni['schema_templates'][p];scaffold=ni['new_module_scaffolding'][p]['program_units_per_new_service_module']
            base=0 if p in adjust['base_exclusions'].get(id,[]) else counts[id][p]
            schemas=0
            for schema in spec['schemas']:
                fields=schema.split(':',1)[1].split(',');require(len(fields)==len(set(fields)),'Duplicate common model field')
                n=len(fields)
                schemas+=n*t['program_per_field']+t.get('program_per_new_model',0)+n*t['declarations_per_field']+t['per_new_model']+n*t['view_field']+t['view_model']
            size=base+formula('module_analogy',reference_units=banks[id][p],fraction=spec['fraction'],scaffold_units=scaffold)+schemas
            common[spec['owner']][p]+=size;commonbase[spec['owner']][p]+=base
    details={}
    for slug,f in families.items():
        details[slug]={}
        for p in PRODUCTS:
            bank=localbank[slug][p]
            if 'analogue_provider' in f:
                provider=f['analogue_provider']
                expected=localbank['master-plan'][p] if provider['id']=='net-planning-component' else correction[p]
                close(provider['units'][p],expected,'Named component analogue');bank=expected
            require(bank>0,'Missing native component analogue')
            t=ni['schema_templates'][p];scaffold=ni['new_module_scaffolding'][p]['program_units_per_new_service_module']
            new=formula('module_analogy',reference_units=bank,fraction=f['extension_fraction']*f['quantity'],scaffold_units=scaffold*f['quantity'])
            schemas=0
            for model in f['schemas']:
                require(model['fields'] and len(model['fields'])==len(set(model['fields'])),'Invalid component model fields')
                n=len(model['fields']);schemas+=n*t['program_per_field']+t.get('program_per_new_model',0)+n*t['declarations_per_field']+t['per_new_model']+n*t['view_field']+t['view_model']
            additional=0
            for mod in f.get('additional_modules',[]):
                expected=localbank['service-planning'][p] if mod['id']=='solver-run-contract' else correction[p]
                close(mod['units'][p],expected,'Additional module analogue')
                additional+=formula('module_analogy',reference_units=expected,fraction=mod['fraction'],scaffold_units=scaffold*mod.get('scaffolds',1))
            size=common[slug][p]+localbase[slug][p]+new+schemas+additional
            details[slug][p]=dict(total=size,base=commonbase[slug][p]+localbase[slug][p],analogue=bank,new=new+schemas+additional,common=common[slug][p])
    target=unique(raw['funding']['mechanisms'],'id','target funding')
    groups=unique(d['economic_units'],'id','coherent unit')
    require(sorted(f for g in groups.values() for f in g['families'])==sorted(families),'Coherent unit family coverage')
    return dict(details=details,groups=groups,families={k:dict(name=f['name'],capabilities=f['capabilities'],scope=f['scope']) for k,f in families.items()},
                target=target,baseline=unique(raw['proposal_results']['economic_units'],'id','adopted baseline'),recorded_files=len(files),cocomo=d['cocomo'])

def prepare_components(documents,contract,registry,formula,use_cache=False):
    d={k:documents[p] for k,p in contract['inputs'].items()}
    spec=d['specification'];require(spec['id']==contract['id'] and spec['recipe']==contract['recipe'],'Coherent preparation identity')
    require(contract['recipe_parameters']==dict(scenario='central',structure_units_per_group=0),'Unsupported coherent parameters')
    supplier=next(c for c in registry['calculations'] if c['id']==spec['analogue_calculation_id'])
    require(digest(supplier)==spec['analogue_contract_sha256'],'Stock analogue contract changed')
    ni=d['native_inputs'];allocation=dict(d['allocation']);allocation['role_labels']=spec['role_labels']
    validate_allocation(d['activities']['cocomo'],allocation,ni['cocomo'])
    # Cache is private to one frozen model loading. Explicit preparation/test inputs bypass it.
    session=CURRENT.get();key=('coherent_components',digest(d['archives']),digest(ni),digest(supplier))
    if not (use_cache and session is not None and key in session.memo):
        stock=prepare_stock(documents,supplier,registry,formula)
        require(ni['schema_templates']==documents[supplier['inputs']['native_inputs']]['schema_templates'],'Component schema template provenance')
        prepared=compile_components(d['archives'],ni,stock,formula)
        if use_cache and session is not None:session.memo[key]=prepared
    else:prepared=session.memo[key]
    group=prepared['groups'][spec['group_id']]
    require(group['families']==spec['families'],'Coherent unit boundary changed')
    caps=sorted(cap for family in group['families'] for cap in prepared['families'][family]['capabilities'])
    require(caps==sorted(c['id'] for c in contract['scope']['capabilities']),'Coherent capability coverage')
    funded={x['mechanism'] for x in contract['funding_claims'] if x['mode']=='funded'}
    expected={spec['mechanism_prefix']+k for k,x in prepared['target'].items() if x['economic_owner']==spec['group_id']}
    require(funded==expected,'Coherent module funding scope')
    consumed={x['mechanism'] for x in contract['funding_claims'] if x['mode']=='consumed'}
    require(consumed==set(spec['reused_mechanisms']),'Coherent reuse funding scope')
    c=prepared['cocomo'];E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum'])
    def effort(size):return formula('cocomo_effort',A=c['A'],KSLOC=size/1000,E=E,EM=c['other_EM'],SCED=c['SCED'],month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor']) if size else 0
    rows=[];sizes={}
    baseline=prepared['baseline'][spec['group_id']]
    for p in PRODUCTS:
        pieces=[prepared['details'][f][p] for f in group['families']];total=sum(x['total'] for x in pieces);base=sum(x['base'] for x in pieces);jh=effort(total)
        old=next(x for x in baseline['rows'] if x['id']==p)
        close(total,old['equivalent_units'],'Coherent size baseline');close(jh,old['jh'],'Coherent effort baseline')
        rows.append(dict(id=p,label=spec['native_labels'][p],jh=jh,common_jh=effort(base),complements_jh=jh-effort(base)))
        sizes[p]=dict(equivalent_units=total,native_base_units=base,new_equivalent_units=total-base)
    cosmic=d['cosmic'];groups=unique(cosmic['groups'],'id','component COSMIC group');processes=unique(cosmic['processes'],'id','component process')
    ids=set();moves=Counter();covered=set()
    for process in processes.values():
        require(process['functional_user'] and process['trigger'],'Missing component functional boundary')
        covered.update(process['capabilities']);seen=set();local=Counter()
        for movement in process['movements']:
            k=(movement['type'],movement['group'])
            require(k not in seen and movement['id'] not in ids,'Duplicate component COSMIC movement');seen.add(k);ids.add(movement['id'])
            require(movement['type'] in ('E','R','W','X') and movement['group'] in groups and movement['cfp']==1,'Invalid component COSMIC movement')
            local[movement['type']]+=1
        require(local['E']>0 and local['W']+local['X']>0,'Incomplete component functional process');moves.update(local)
    require(covered==set(caps),'Component COSMIC capability coverage')
    cfp=sum(moves.values());close(cfp,cosmic['CFP'],'Component CFP total');close(cfp,baseline['COSMIC']['CFP'],'Component functional baseline')
    benchmark=d['productivity_source'];close(cosmic['hours_per_CFP'],benchmark['benchmark']['main']['hours_per_cfp'],'Component benchmark')
    require(cosmic['factor']==1,'Uncalibrated benchmark modifier');close(cosmic['day_hours'],c['day_hours'],'Component JH convention')
    functional=dict(CFP=cfp,hours_per_CFP=cosmic['hours_per_CFP'],factor=1,day_hours=c['day_hours'])
    from estimation_calculation import rounded
    require(set(baseline['family_allocations'])==set(group['families']),'Component allocation scope')
    require(sum(baseline['family_allocations'].values())==rounded(next(x['jh'] for x in rows if x['id']==allocation['selected_reference']),allocation['rounding_jh']),'Component allocation total')
    selected=sizes[allocation['selected_reference']]
    return dict(cocomo=c,allocation=allocation,rows=rows,functional=functional,activity_source=d['activities']['cocomo'],
        work_items=[('coherent_module',id,prepared['target'][id]['family_owner'],1) for id in prepared['target'] if spec['mechanism_prefix']+id in funded],
        trace=dict(recorded_files=prepared['recorded_files'],blocks=len(funded),refined_blocks=0,method_samples=0,
            complement_units=selected['new_equivalent_units'],complement_parts=selected,processes=len(processes),groups=len(groups),CFP=cfp,movements=dict(moves),reuse_factor=0,component_sizes=sizes,
            component_allocations=[dict(id=f,label=prepared['families'][f]['name'],jh=baseline['family_allocations'][f]) for f in group['families']],coherent_unit=spec['group_id'],no_common_280_added=True))
