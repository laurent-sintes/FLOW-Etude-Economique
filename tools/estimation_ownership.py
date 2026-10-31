"""New Ownership modules sized from already-funded Stock analogues; no checkout or duplicate funding."""
from copy import deepcopy
from collections import Counter
from estimation_inputs import require,digest
from estimation_preparation import number,unique,close,validate_allocation
from estimation_stock import prepare_stock


def prepare_ownership(documents,contract,registry,formula):
    d={k:deepcopy(documents[path]) for k,path in contract['inputs'].items()}
    spec,ni,allocation=d['specification'],d['native_inputs'],d['allocation']
    h=ni['hypotheses'];caps=[c['id'] for c in contract['scope']['capabilities']]
    require(spec['id']==contract['id'] and spec['recipe']==contract['recipe'],'Ownership recipe mismatch')
    require(h['capabilities']==spec['capabilities']==caps,'Ownership capability scope mismatch')
    require(allocation['scope']['capabilities']==caps and allocation['scope']['stack']==contract['stack'],
            'Ownership allocation scope mismatch')
    source=[c for c in registry['calculations'] if c['id']==spec['analogue_calculation_id']]
    require(len(source)==1 and digest(source[0])==spec['analogue_contract_sha256'],'Ownership analogue contract changed')
    stock_contract=source[0]
    require(stock_contract['recipe']=='native_component_analogies_v1' and stock_contract['stack']==contract['stack'],
            'Ownership analogue recipe or stack mismatch')
    require(stock_contract['unit_id'] in {m['funding_owner'] for m in registry['mechanisms']
            if m['id'] in spec['reused_mechanisms']},'Ownership analogue has no consumed funding owner')
    stock=prepare_stock(documents,stock_contract,registry,formula)
    c=ni['cocomo']
    require(c==spec['cocomo']==stock['cocomo'],'Ownership COCOMO parameter mismatch')
    products=h['native_references']
    require(len(set(products))==len(products)==4,'Ownership native references')
    require(products==list(ni['banks']) and allocation['selected_reference'] in products,'Ownership native coverage')
    require(ni['activities']==d['activities']['cocomo'],'Ownership activity source mismatch')
    allocation['role_labels']=spec['role_labels']
    validate_allocation(d['activities']['cocomo'],allocation,c)
    require(contract['recipe_parameters']==dict(scenario='central',structure_units_per_group=0),
            'Unsupported Ownership preparation parameters')
    modules=unique(h['modules'],'id','Ownership module')
    schemas=unique(h['schemas'],'name','Ownership model')
    require(set(modules)==set(spec['modules']),'Ownership module scope mismatch')
    mechanisms={m['id']:m for m in registry['mechanisms']}
    funded={mechanisms[x['mechanism']]['basis'].get('family') for x in contract['funding_claims'] if x['mode']=='funded'}
    consumed={x['mechanism'] for x in contract['funding_claims'] if x['mode']=='consumed'}
    require(funded==set(modules),'Ownership funding scope mismatch')
    require(consumed==set(spec['reused_mechanisms']),'Ownership reuse owner mismatch')
    for sc in schemas.values():
        require(sc['package'] in modules and sc['fields'] and len(sc['fields'])==len(set(sc['fields']))
                and type(sc['view']) is bool,'Invalid Ownership schema')
    for module in modules.values():
        for k in ('lower','central','upper'):number(module[k],'Ownership module fraction')
        require(module['lower']<=module['central']<=module['upper'],'Ownership fraction order')
    E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum'])
    def effort(units):
        return formula('cocomo_effort',A=c['A'],KSLOC=units/1000,E=E,EM=c['other_EM'],SCED=c['SCED'],
            month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor'])
    baseline=unique(d['baseline']['rows'],'id','Ownership baseline')
    require(set(baseline)==set(products),'Ownership baseline coverage')
    rows=[];details={};work=[];files=set()
    for p in products:
        bank=stock['trace']['stock_sizes'][p]['bank']
        for kind in ('reservation_chain','correction_chain'):
            close(bank[kind],ni['banks'][p]['central'][kind]['program_units'],'Ownership analogue reconstruction')
            for f in ni['banks'][p]['central'][kind]['source_slices']:
                files.add((p,f['path']))
        stock_ni=documents[stock_contract['inputs']['native_inputs']]
        require(ni['schema_templates'][p]==stock_ni['schema_templates'][p]
                and ni['new_module_scaffolding'][p]==stock_ni['new_module_scaffolding'][p],
                'Ownership declaration or scaffold provenance mismatch')
        t=ni['schema_templates'][p];scaffold=ni['new_module_scaffolding'][p]['program_units_per_new_service_module']
        number(scaffold,'Ownership scaffold')
        for value in t.values():
            if type(value) in (int,float):number(value,'Ownership declaration template')
        blocks=[]
        for m in modules.values():
            require(m['analogue'] in ('reservation_chain','correction_chain'),'Unknown Ownership analogue')
            pu=formula('module_analogy',reference_units=bank[m['analogue']],fraction=m['central'],scaffold_units=scaffold)
            du=0
            for sc in schemas.values():
                if sc['package']!=m['id']:continue
                n=len(sc['fields']);view=int(sc['view'])
                pu+=n*t['program_per_field']+t.get('program_per_new_model',0)
                du+=n*t['declarations_per_field']+t['per_new_model']+view*(n*t['view_field']+t['view_model'])
            blocks.append(dict(id=m['id'],program_units=pu,declarative_units=du,
                analogue_units=bank[m['analogue']],fraction=m['central']))
        config=sum(number(v,'Ownership configuration') for v in h['configuration'].values())
        pu=sum(b['program_units'] for b in blocks);du=sum(b['declarative_units'] for b in blocks)+config
        units=formula('equivalent_size',new_program=pu,new_declarative=du,w=1,AAM=0,reused_program=0,reused_declarative=0)
        total=effort(units);old=baseline[p]
        close(units,old['detail']['equivalent_units'],'Ownership size baseline')
        close(total,old['jh'],'Ownership effort baseline')
        rows.append(dict(id=p,label=ni['native_reference_labels'][p],jh=total,common_jh=0,complements_jh=total))
        details[p]=dict(program_units=pu,declarative_units=du,equivalent_units=units,blocks=blocks,configuration=config)
        work.extend(('ownership_module',p+'/'+b['id'],b['id'],b['program_units']+b['declarative_units']) for b in blocks)
    cosmic=d['cosmic'];ref=d['cosmic_refinement']
    require(ref['base_sha256']==registry['proofs'][contract['inputs']['cosmic']]['sha256']
            and ref['unchanged_effort_inputs'] is True,'Ownership COSMIC refinement provenance')
    groups=unique(cosmic['groups'],'id','Ownership COSMIC group')
    require(ref['group']['id'] not in groups and ref['updated_group']['id'] in groups,'Ownership COSMIC refinement group')
    groups[ref['updated_group']['id']]=ref['updated_group'];groups[ref['group']['id']]=ref['group']
    processes=unique(cosmic['processes'],'id','Ownership COSMIC process')
    for addition in ref['add_movements']:
        require(addition['process'] in processes,'Unknown Ownership refinement process')
        processes[addition['process']]['movements'].append(dict(id=addition['process']+'-'+addition['type']+'-'+addition['group'],
            type=addition['type'],group=addition['group'],cfp=1))
    ids=set();moves=Counter();covered=set()
    for p in processes.values():
        require(p['functional_user'] and p['trigger'] and set(p['capabilities'])<=set(caps),'Ownership functional boundary')
        covered.update(p['capabilities']);keys=set();counts=Counter()
        for movement in p['movements']:
            key=(movement['type'],movement['group'])
            require(key not in keys and movement['id'] not in ids,'Duplicate Ownership COSMIC movement')
            keys.add(key);ids.add(movement['id'])
            require(movement['type'] in ('E','R','W','X') and movement['group'] in groups
                    and movement['cfp']==1,'Invalid Ownership COSMIC movement')
            counts[movement['type']]+=1
        require(counts['E']>0 and counts['W']+counts['X']>0,'Incomplete Ownership functional process')
        moves.update(counts)
    require(covered==set(caps),'Ownership COSMIC capability coverage')
    cfp=sum(moves.values());expected=d['baseline']['functional_control']
    close(cfp,expected['CFP'],'Ownership functional total')
    for k in ('E','R','W','X'):close(moves[k],expected['movements'][k],'Ownership movement total')
    rate=cosmic['productivity'];source=d['productivity_source']
    close(rate['hours_per_CFP'],source['benchmark']['main']['hours_per_cfp'],'Ownership benchmark')
    close(rate['day_hours'],source['units']['jh_hours'],'Ownership JH convention')
    close(rate['day_hours'],c['day_hours'],'Ownership COCOMO/COSMIC JH')
    require(rate['factor']==1,'Ownership benchmark size factor')
    functional=dict(CFP=cfp,hours_per_CFP=rate['hours_per_CFP'],factor=1,day_hours=c['day_hours'])
    selected=details[allocation['selected_reference']]
    return dict(cocomo=c,allocation=allocation,rows=rows,functional=functional,activity_source=d['activities']['cocomo'],
        work_items=work,trace=dict(recorded_files=len(files),blocks=len(modules),refined_blocks=0,method_samples=0,
        complement_units=selected['equivalent_units'],complement_parts=selected,processes=len(processes),groups=len(groups),
        CFP=cfp,movements=dict(moves),reuse_factor=0,ownership_sizes=details,
        analogue_calculation_id=stock_contract['id'],all_new_behavior_after_existing_funding=True))
