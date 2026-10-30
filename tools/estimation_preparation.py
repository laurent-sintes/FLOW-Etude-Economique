"""Reconstruct size, reuse and COSMIC counts from recorded evidence (no OSS checkout required)."""
from collections import Counter
from copy import deepcopy
import math
from estimation_inputs import require


def number(value, name, minimum=0, positive=False, maximum=None):
    require(type(value) in (int, float) and math.isfinite(value), 'Nonfinite/non-numeric ' + name)
    require(value > minimum if positive else value >= minimum, 'Invalid domain: ' + name)
    require(maximum is None or value <= maximum, 'Invalid upper bound: ' + name)
    return value


def unique(rows, field, name):
    values = [r[field] for r in rows]
    require(len(values) == len(set(values)), 'Duplicate ' + name)
    return {r[field]: r for r in rows}


def close(a, b, name):
    number(a, name); number(b, name)
    require(math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-9), 'Reconciliation failed: ' + name)


def prepare(documents, contract, registry, formula):
    """Pure adapter; documents and formulas may come from the single YAML export."""
    d = {k: deepcopy(documents[path]) for k, path in contract['inputs'].items()}
    baseline, ni, m, p = (d[k] for k in ('baseline', 'native_inputs', 'native_measures', 'complement_inputs'))
    require({x['id'] for x in contract['scope']['capabilities']} == set(ni['scope']['capabilities_in_family']), 'Native evidence belongs to a different capability scope')
    c = ni['cocomo']
    require(c == p['cocomo'] == baseline['formula']['cocomo'], 'COCOMO parameter mismatch')
    for key in ('A','B','C','D','month_hours','day_hours','effort_phase_factor','schedule_phase_factor','other_EM','SCED'):
        number(c[key], key, positive=True)
    number(c['SF_sum'], 'SF_sum'); require(c['SCED'] == 1 and c['REVL'] == 0, 'Only nominal SCED / REVL supported')
    scenario = unique(ni['scenarios'], 'id', 'scenario')[contract['recipe_parameters']['scenario']]
    for k in ('PERS','PREX'): number(scenario[k],k,positive=True)
    number(scenario['AA'],'AA',maximum=8);number(scenario['IM'],'IM',maximum=100)
    w=number(scenario['declarative_weight'],'declarative_weight')
    reuse=ni['reuse']
    for key in ('DM','CM','SU','AT'):
        require(reuse[key] == 0, 'Unsupported reuse modification: ' + key)
    aam=formula('reuse_assimilation',AA=scenario['AA'],IM=scenario['IM'])
    products=unique(ni['products'],'id','product')
    require(set(products)==set(m['summary']), 'Native product coverage mismatch')
    identities=set(); sizes={key:{kind:dict(program_units=0,declarative_units=0,files=0) for kind in ('new','reused')} for key in products}
    for f in m['files']:
        identity=(f['product'], f['repo'], f['path'])
        require(identity not in identities,'Duplicate measured file');identities.add(identity)
        require(f['product'] in sizes and f['repo'] in m['repos'] and f['treatment'] in ('new','reused'),'Unknown file classification')
        require(len(f['sha256'])==64 and m['repos'][f['repo']]['commit'],'Missing code provenance')
        target=sizes[f['product']][f['treatment']]; target['files']+=1
        for key in ('program_units','declarative_units'):target[key]+=number(f[key],key)
    for product in sizes:
        for treatment in sizes[product]:
            for key,value in sizes[product][treatment].items():close(value,m['summary'][product][treatment][key],'native file summary')
    mechanisms={x['id']:x for x in registry['mechanisms']}
    funded=[mechanisms[x['mechanism']] for x in contract['funding_claims'] if x['mode']=='funded']
    kinds={x['basis']['kind'] for x in funded}
    families={x['basis']['family'] for x in funded if x['basis']['kind']=='complement_family'}
    claimed={mechanisms[x['mechanism']]['basis'].get('family') for x in contract['funding_claims']}
    require(set(p['families']) <= claimed,'Complement family without funding declaration')
    bank=d['analogues']['unit_bank']
    blocks=unique(p['blocks'],'id','complement block')
    schemas=unique(p['schemas'],'name','schema')
    configs=unique(p['configuration'],'id','configuration')
    def central(values):
        require(len(values)==3,'Expected three recorded analogue measures')
        for value in values:number(value,'analogue size')
        require(values==sorted(values),'Unordered analogue measures')
        return values[1]
    parts=dict(blocks=0.,schemas=0.,configuration=0.,structure=0.,method_refinement=0.)
    work=[];group_families={}
    for b in blocks.values():
        require(b['family'] in p['families'],'Unknown block family')
        units=number(b['quantity'],'quantity')*central(bank[b['kind']]['range'])
        work.append(('block',b['id'],b['family'],units))
        group=b['id'].split('/')[0]
        require(group not in group_families or group_families[group]==b['family'],'Structure group shared across funding families')
        group_families[group]=b['family']
        if b['family'] in families:parts['blocks']+=units
    u={k:central(v) for k,v in p['schema_units'].items()}
    for sc in schemas.values():
        require(len(sc['fields'])==len(set(sc['fields'])) and type(sc['new_model']) is bool,'Invalid schema fields')
        units=len(sc['fields'])*u['program_per_field']+w*(len(sc['fields'])*(u['declarative_per_field']+u['ui_declarative_per_field'])+int(sc['new_model'])*(u['declarative_per_new_model']+u['ui_declarative_per_new_model']))
        require(sc['family'] in p['families'], 'Unknown schema family')
        work.append(('schema',sc['name'],sc['family'],units))
        if sc['family'] in families:parts['schemas']+=units
    for x in configs.values():
        units=number(x['quantity'],'configuration quantity')*central(x['unit_range'])*w
        require(x['family'] in p['families'], 'Unknown configuration family')
        work.append(('configuration',x['id'],x['family'],units))
        if x['family'] in families:parts['configuration']+=units
    structure=number(contract['recipe_parameters']['structure_units_per_group'],'structure units')
    for group,family in group_families.items():
        work.append(('structure',group,family,structure))
        if family in families:parts['structure']+=structure
    methods=unique(d['method_measures'],'id','method')
    samples=unique(d['analogues']['samples'],'id','analogue sample')
    for method in methods.values():
        sample=samples[method['sample']]
        require(all(method[k]==sample[k] for k in ('path','sha256','commit')),'Method code provenance mismatch')
        number(method['program_units'],'method size')
    changes=unique(d['refinements'],'block','refined block')
    for key,x in changes.items():
        require(key in blocks and x['family']==blocks[key]['family'],'Unknown refined block')
        previous=number(blocks[key]['quantity'],'quantity')*central(bank[blocks[key]['kind']]['range'])
        close(previous,x['previous_units'],'refinement original size')
        require(len(x['method_refs'])==len(set(x['method_refs'])),'Duplicate refinement method')
        proposed=sum(methods[k]['program_units'] for k in x['method_refs'])
        close(proposed,x['proposed_units'],'refinement method size')
        if x['family'] in families:parts['method_refinement']+=proposed-previous
    complements=sum(parts.values())
    close(complements,baseline['size']['proposed_complements_units'],'complement total')
    E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum'])
    def effort(k):
        return formula('cocomo_effort',A=c['A'],KSLOC=k,E=E,EM=c['other_EM']*scenario['PERS']*scenario['PREX'],SCED=c['SCED'],
            month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor'])
    oldrows=unique(baseline['rows'],'id','baseline reference')
    require(set(oldrows)==set(products),'Baseline product mismatch')
    rows=[]
    for key,product in products.items():
        n=sizes[key]['new']; r=sizes[key]['reused']
        k=formula('equivalent_size',new_program=n['program_units'] if 'native_new' in kinds else 0,
            new_declarative=n['declarative_units'] if 'native_new' in kinds else 0,
            reused_program=r['program_units'] if 'native_reuse' in kinds else 0,
            reused_declarative=r['declarative_units'] if 'native_reuse' in kinds else 0,w=w,AAM=aam)/1000
        common=effort(k);total=effort(k+complements/1000);old=oldrows[key]
        for actual,expected,name in ((common,old['common_jh'],'common effort'),(total,old['total_jh'],'total effort'),
            (total-common,old['flow_complements_jh'],'complement effort'),(k+complements/1000,old['equivalent_KSLOC'],'equivalent size')):
            close(actual,expected,name)
        rows.append(dict(id=key,label=product['label'],jh=total,common_jh=common,complements_jh=total-common))
    cosmic=d['cosmic'];groups=unique(cosmic['groups'],'id','COSMIC group');processes=unique(cosmic['processes'],'id','COSMIC process')
    movements=Counter();movement_ids=set()
    for process in processes.values():
        require(bool(process['functional_user']) and bool(process['trigger']),'Missing functional boundary')
        keys=set();counts=Counter()
        for movement in process['movements']:
            key=(movement['type'],movement['group'])
            require(key not in keys and movement['id'] not in movement_ids,'Duplicate COSMIC movement')
            keys.add(key);movement_ids.add(movement['id'])
            require(movement['type'] in ('E','R','W','X') and movement['group'] in groups and movement['cfp']==1,'Invalid COSMIC movement')
            counts[movement['type']]+=1
        require(counts['E']>0 and counts['W']+counts['X']>0,'Incomplete COSMIC process')
        for kind in ('E','R','W','X'):close(counts[kind],process['count'][kind],'COSMIC movement subtotal')
        close(sum(counts.values()),process['count']['cfp'],'COSMIC process count')
        movements.update(counts)
    cfp=sum(movements.values());benchmark=d['productivity'];source=d['productivity_source']
    close(cfp,baseline['functional']['CFP'],'COSMIC total')
    close(cfp,benchmark['CFP'],'benchmark size')
    close(benchmark['retained_hours_per_CFP'],source['benchmark']['main']['hours_per_cfp'],'productivity source')
    for day in (source['units']['jh_hours'],d['allocation']['day_hours'],baseline['functional']['day_hours']):
        close(day,c['day_hours'],'JH conversion convention')
    functional=dict(CFP=cfp,hours_per_CFP=number(benchmark['retained_hours_per_CFP'],'productivity',positive=True),
        factor=number(benchmark['retained_factor'],'productivity factor',positive=True),day_hours=c['day_hours'])
    for key,value in functional.items():close(value,baseline['functional'][key],'functional input '+key)
    activities=d['activities']['cocomo'];require(activities==baseline['activity_source'],'Activity evidence mismatch')
    validate_allocation(activities,d['allocation'],c)
    return dict(cocomo=c,allocation=d['allocation'],rows=rows,functional=functional,activity_source=activities,
        trace=dict(recorded_files=len(m['files']),blocks=len(blocks),refined_blocks=len(changes),method_samples=len(methods),
            complement_parts=parts,complement_units=complements,processes=len(processes),groups=len(groups),CFP=cfp,
            movements=dict(movements),reuse_factor=aam),work_items=work)


def validate_allocation(source, inputs, c):
    phases=source['phase_effort_percent_of_base'];count=len(source['phase_order'])
    require(count>0 and len(set(source['phase_order']))==count,'Invalid phase order')
    for key,factor in (('phase_effort_percent_of_base','effort_phase_factor'),('phase_schedule_percent_of_base','schedule_phase_factor')):
        values=source[key];require(len(values)==count,'Phase column mismatch')
        for value in values:number(value,key)
        close(sum(values)/100,c[factor],'phase extension')
    activities=unique(source['activities'],'id','activity')
    require(set(activities)==set(inputs['activity_role_weights']),'Activity allocation coverage')
    for a in activities.values():
        require(len(a['percent_by_phase'])==count,'Activity phase column mismatch')
        for value in a['percent_by_phase']:number(value,'activity percentage',maximum=100)
        weights=inputs['activity_role_weights'][a['id']]
        require(set(weights)<=set(a['possible_flow_roles']) and set(weights)<=set(inputs['role_labels']),'Unknown role allocation')
        for value in weights.values():number(value,'role weight',maximum=1)
        close(sum(weights.values()),1,'role weight sum')
    for index in range(count):close(sum(a['percent_by_phase'][index] for a in activities.values()),100,'activity phase total')
    number(inputs['rounding_jh'],'decision rounding',positive=True);number(inputs['role_rounding_jh'],'role rounding',positive=True)
