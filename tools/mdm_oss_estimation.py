"""Replay the MDM-specific COCOMO proposal from pinned, scoped code evidence."""
from base64 import b64decode
from copy import deepcopy
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import PurePosixPath
from statistics import median

from jsonschema import Draft202012Validator
from capability_catalog import catalog, dependencies as native_dependencies
from content_model import resolve_text_tree, validate_glossary_literals
from core_product_estimate import apportioned
from estimation_calculation import formula, rounded
from model_context import CURRENT, model_memo, scoped_model
from validate_stacks import ROOT, read

SOURCE='source/estimation-mdm-oss.yaml'
SCHEMA='source/schema-estimation-mdm-oss.yaml'
NATIVE='source/referentiel-capacites.yaml'
REVISION='source/revision-master-data.yaml'
FUNDING='source/calculs-estimation-core.yaml'
UNIT='master-data-java-spring'
GROUPS=('model','ingestion','identity','lifecycle','distribution')


def require(ok, text):
    if not ok:
        raise ValueError('ERR_MDM_OSS_ESTIMATION: '+text)


def dependencies():
    spec=read(ROOT/SOURCE)
    return {SOURCE,SCHEMA,REVISION,FUNDING,'tools/mdm_oss_estimation.py','source/glossaire.yaml',spec['method_ref'],spec['report_ref'],spec['refinement_report_ref'],spec['engineering_report_ref'],*(r['path'] for r in spec['proofs'].values())}|native_dependencies()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def proof(ref, frozen=None):
    path=PurePosixPath(ref['path'])
    require(not path.is_absolute() and '..' not in path.parts and path.parts[0]=='audits' and path.suffix in ('.json','.py'),'Unsafe proof path')
    if frozen is not None:
        raw=frozen[ref['path']]
        raw=raw.encode('utf-8') if isinstance(raw,str) else raw
        require(sha(raw)==ref['sha256'],'Proof hash changed: '+ref['path'])
        return raw.decode('utf-8') if path.suffix=='.py' else json.loads(raw)
    file=(ROOT/path).resolve()
    require(file.is_relative_to(ROOT.resolve()),'Proof outside project')
    snap=CURRENT.get()
    doc=(snap.read(file,lambda text:text) if snap else file.read_text(encoding='utf-8')) if path.suffix=='.py' else read(file)
    require((snap.digests[file] if snap else sha(file.read_bytes()))==ref['sha256'],'Proof hash changed: '+ref['path'])
    return doc


def file_key(row):
    return row['repo']+'/'+row['path']+('#'+row['fragment'] if row.get('fragment') else '')


def scope_evidence(spec,scope,measures,code,native_rows,native_source):
    """Validate the partition, native scope, license/commit evidence and analogue references."""
    require(scope['status']==spec['status']=='proposal_not_adopted' and scope['unit_ref']==UNIT and scope['domain_ref']=='domain-master-data','Scope or adoption status drift')
    require(scope['native_source']==native_source,'Native capture changed')
    caps={r['id']:r['capacite_id'] for r in native_rows if r['hierarchie'][0]['id']==scope['domain_ref']}
    coverage=scope['coverage']
    require(len({r['id'] for r in coverage})==len(coverage) and {r['id']:r['native_id'] for r in coverage}==caps,'Incomplete or duplicated MDM scope')
    require(set(r['group'] for r in coverage)==set(GROUPS)|{'families'},'Unexpected functional grouping')
    family_caps={r['native_id'] for r in coverage if r['group']=='families'}
    adapters=scope['family_adapters'];refs=[c for a in adapters for c in a['capability_refs']]
    require(len({a['id'] for a in adapters})==len(adapters) and set(refs)==family_caps and len(refs)==len(set(refs)),'Family adaptation boundary drift')
    require(scope['confidence_interval'] is None and scope['completeness']=='conditional_on_declared_scope_and_size_assumptions','Unsupported confidence or coverage claim')
    products={p['id']:p for p in spec['products']}
    require(len(products)==len(spec['products']) and scope['anchor'] in products,'Duplicate or unknown product')
    repos=[r for p in products.values() for r in p['repos']]
    require(len(repos)==len(set(repos)) and set(repos)==measures['repos'].keys(),'Repository attribution drift')
    require(all(len(r['commit'])==40 and r['origin'].startswith('https://') for r in measures['repos'].values()),'No pinned source')
    require(measures['version']==1 and not measures['rejected'],'Unresolved parser errors')
    require(code['format']==1 and code['encoding']=='gzip-base64-json-raw-base64','Invalid archive format')
    archive=json.loads(gzip.decompress(b64decode(code['data'],validate=True)))
    require(len(archive)==code['files'],'Archive index drift')
    require(all(any(repo+'/'+name in archive for name in ('LICENSE','LICENSE.md','LICENSE.txt')) for repo in repos),'Missing license evidence')
    measured={file_key(f):f for f in measures['files']}
    require(len(measured)==len(measures['files']),'Duplicate measurement identity')
    for key,f in measured.items():
        path=PurePosixPath(f['path'])
        require(f['repo'] in repos and not path.is_absolute() and '..' not in path.parts and f['group'] in {*GROUPS,'family_prototype'},'Unsafe file or group')
        require(not f['parse_errors'] and all(type(f[k]) is int and f[k]>=0 for k in ('program_units','declarative_units')),'Unusable measurement')
        raw=b64decode(archive[key],validate=True)
        require(sha(raw)==f['sha256'],'Source digest drift: '+key)
        if f.get('fragment'):
            original=b64decode(archive[f['repo']+'/'+f['path']],validate=True)
            require(sha(original)==f['source_sha256'] and f['start_line']>0,'Stored routine provenance drift')
            try:text=original.decode('utf-8-sig')
            except UnicodeDecodeError:text=original.decode('cp1251')
            require(raw.decode('utf-8') in text.replace('\r\n','\n').replace('\r','\n'),'Stored routine does not match its source')
    def samples(rows, group=None):
        require(len(rows)==3 and len({file_key(r) for r in rows})==3,'Three distinct analogues required')
        for row in rows:
            m=measured.get(file_key(row))
            require(m is not None and all(row[k]==m[k] for k in ('sha256','program_units','declarative_units')),'Analogue is not bound to a measurement')
            require(group is None or m['group']==group,'Invalid prototype treatment')
    samples(scope['family_prototypes'],'family_prototype')
    completions=scope['completions']
    require(len({c['id'] for c in completions})==len(completions),'Duplicate projected service')
    for c in completions:
        require(set(c['capability_refs'])<=set(caps.values()) and c['capability_refs'] and c['basis'],'Service outside MDM scope')
        require(type(c['quantity']) is int and c['quantity']>0 and c['applies_to'] and set(c['applies_to'])<=products.keys(),'Invalid projected service')
        samples(c['samples'])
    for row in coverage:
        require(set(row['completion_refs'])=={c['id'] for c in completions if row['native_id'] in c['capability_refs']},'Broken capacity crosswalk')
    return products


def refine_unidata(spec, measures, code, selection):
    require(selection['version']==1 and selection['repo']=='unidata', 'Invalid Unidata selection')
    require(selection['measurements_sha256']==spec['proofs']['measures']['sha256'], 'Selection refers to a different measurement')
    archive=json.loads(gzip.decompress(b64decode(code['data'],validate=True)))
    measured={r['path']:r for r in measures['files'] if r['repo']=='unidata' and not r.get('fragment')}
    adjustments={}
    exclusions=[]
    for decision in selection['exclusions']:
        units=0
        for item in decision['files']:
            path=item['path']
            row=measured.get(path)
            require(row is not None and row['group'] in GROUPS and row['sha256']==item['sha256'], 'Unbound Unidata component: '+path)
            require(path not in adjustments, 'Unidata component selected twice: '+path)
            segments=item.get('segments')
            if segments is None:
                adjustments[path]=None
                units+=row['program_units']+row['declarative_units']
                continue
            raw=b64decode(archive[file_key(row)],validate=True)
            end=0
            count=0
            require(segments and path.endswith('.java'), 'Invalid partial Unidata component: '+path)
            for segment in sorted(segments,key=lambda s:s['start_byte']):
                start,stop=segment['start_byte'],segment['end_byte']
                require(end<=start<stop<=len(raw) and sha(raw[start:stop])==segment['sha256'], 'Invalid or overlapping Unidata excerpt: '+path)
                require(type(segment['program_units']) is int and segment['program_units']>0, 'Invalid Unidata excerpt size: '+path)
                count+=segment['program_units']
                end=stop
            require(count<row['program_units'], 'Partial Unidata component exceeds measured size: '+path)
            adjustments[path]=count
            units+=count
        require(units>0, 'Empty Unidata exclusion')
        exclusions.append({**{k:decision[k] for k in ('id','label','boundary','preserved')},'units':units})
    require(exclusions and len({d['id'] for d in exclusions})==len(exclusions), 'Missing or duplicate Unidata decision')
    selected=[]
    for row in measures['files']:
        if row['repo']!='unidata' or row.get('fragment') or row['path'] not in adjustments:
            selected.append(row)
        elif (count:=adjustments[row['path']]) is not None:
            selected.append(dict(row,program_units=row['program_units']-count))
    review=dict(exclusions=exclusions,retained=selection['retained'],open_questions=selection['open_questions'],report_ref=spec['refinement_report_ref'])
    return dict(measures,selected_files=selected,unidata_review=review)


def project_engineering(spec, engineering, revision, funding):
    require(engineering['version']==1 and engineering['status']==spec['status'], 'Invalid engineering proposal')
    require(engineering['work_unit_ref']==revision['work_unit_ref']==spec['work_unit_ref'], 'Engineering proposal refers to another work unit')
    require(engineering['kept_groups']==['families'] and engineering['kept_packages']==['MDM12'], 'Unexpected unchanged packages in engineering proposal')
    packages={p['id']:p for p in revision['packages'] if p['group'] in ('common','families')}
    family_jh=sum(p['jh'] for p in packages.values() if p['group']=='families')
    qualification=packages['MDM12']
    require(qualification['group']=='common', 'Missing transverse qualification')
    replaced={key for key,p in packages.items() if p['group']=='common'}-{'MDM12'}
    mechanisms={m['id']:m for m in funding['mechanisms'] if m['stack']=='java-spring'}
    groups=engineering['groups']
    require([g['id'] for g in groups]==['engine','interfaces'], 'Unexpected engineering group')
    components=[c for g in groups for c in g['components']]
    require(all(g['components'] for g in groups) and len({c['id'] for c in components})==len(components), 'Empty group or duplicate engineering component')
    require({key for c in components for key in c['package_refs']}==replaced, 'Engineering component mapping does not cover the common packages')

    def with_effort(row):
        activities=row['activities']
        require(set(activities)=={'design','delivery','qa'} and all(type(v) is int and v>0 for v in activities.values()), 'Invalid engineering activity estimate')
        return dict(row,jh=sum(activities.values()))

    projected=[]
    for group in groups:
        items=[]
        for row in group['components']:
            refs=row['funding_refs']
            require(row['package_refs'] and refs and set(refs)<=mechanisms.keys() and len(refs)==len(set(refs)), 'Unknown or duplicated reuse mechanism')
            items.append(dict(with_effort(row),funding=[{k:mechanisms[key][k] for k in ('id','label','funding_owner')} for key in refs]))
        projected.append(dict(group,components=items,jh=sum(item['jh'] for item in items)))
    variants=[with_effort(row) for row in engineering['variants']]
    require(variants and len({v['id'] for v in variants})==len(variants), 'Empty or duplicate engineering option')
    replaced_jh=sum(packages[key]['jh'] for key in replaced)
    central=sum(g['jh'] for g in projected)+family_jh+qualification['jh']
    work_jh={f"MDM-{r['id']}":r['jh'] for group in projected for r in group['components']}
    work_jh.update({key:p['jh'] for key,p in packages.items() if p['group']=='families' or key=='MDM12'})
    return dict(status=engineering['status'],assumption=engineering['assumption'],activity_basis=engineering['activity_basis'],
                groups=projected,variants=variants,unknowns=engineering['unknowns'],decision_gate=engineering['decision_gate'],
                family_jh=family_jh,qualification_jh=qualification['jh'],retained_jh=replaced_jh+family_jh+qualification['jh'],
                central_jh=central,extended_jh=central+sum(v['jh'] for v in variants),gap_jh=central-replaced_jh-family_jh-qualification['jh'],
                work_jh=work_jh,report_ref=spec['engineering_report_ref'])


@model_memo
def prepared():
    spec=read(ROOT/SOURCE)
    Draft202012Validator(read(ROOT/SCHEMA)).validate(spec)
    docs={k:proof(ref) for k,ref in spec['proofs'].items()}
    products=scope_evidence(spec,docs['scope'],docs['measures'],docs['code'],catalog()['rows'],read(ROOT/NATIVE))
    historical=read(ROOT/spec['method_ref'])['cocomo']
    require(all(historical[k]==v for k,v in spec['cocomo'].items()),'Unapproved parameter recalibration')
    glossary=read(ROOT/'source/glossaire.yaml')
    validate_glossary_literals(spec['labels'],glossary,path=SOURCE)
    spec['labels']=resolve_text_tree(spec['labels'],glossary,path=SOURCE)
    measures=refine_unidata(spec,docs['measures'],docs['code'],docs['unidata_selection'])
    measures['engineering']=project_engineering(spec,docs['engineering'],read(ROOT/REVISION),read(ROOT/FUNDING))
    return spec,docs['scope'],measures,products


def _cost(unit, days):
    roles=apportioned(days,{r['id']:r['jh'] for r in unit['roles']})
    return float(sum((Decimal(roles[r['id']])*Decimal(str(r['rate_eur_jh'])) for r in unit['roles']),Decimal(0))+Decimal(days)*Decimal(str(unit['tooling_eur_jh'])))


@scoped_model
def build_mdm_assessment(units):
    spec,scope,measures,products=prepared()
    return project_assessment(spec,scope,measures,products,next(u for u in units if u['id']==UNIT))


def project_assessment(spec,scope,measures,products,unit,rule_function=formula):
    calc=rule_function
    require({c['native_id'] for c in unit['capabilities']}=={r['native_id'] for r in scope['coverage']},'Proposal does not match the retained unit scope')
    params=spec['cocomo'];E=calc('cocomo_exponent',B=params['B'],SF_sum=params['SF_sum']);F=calc('schedule_exponent',D=params['D'],E=E,B=params['B'])
    def sizes(rows,weight):
        return sum(r['program_units']+weight*r['declarative_units'] for r in rows)
    def estimate(product,weight,files):
        measured=[r for r in files if r['repo'] in product['repos'] and r['group']!='family_prototype']
        groups=[dict(id=g,units=sizes([r for r in measured if r['group']==g],weight),files=sum(r['group']==g for r in measured)) for g in GROUPS]
        native_size=sizes(measured,weight)
        require(native_size>0 and all(g['files'] for g in groups),'Empty comparable component group')
        extra=[dict(id=c['id'],label=c['label'],units=c['quantity']*median([sizes([r],weight) for r in c['samples']]),quantity=c['quantity'],basis=c['basis'],samples=c['samples']) for c in scope['completions'] if product['id'] in c['applies_to']]
        family_size=len(scope['family_adapters'])*median([sizes([r],weight) for r in scope['family_prototypes']])
        ksloc=(native_size+sum(x['units'] for x in extra)+family_size)/1000
        jh=calc('cocomo_effort',A=params['A'],KSLOC=ksloc,E=E,EM=params['other_EM'],SCED=params['SCED'],month_hours=params['month_hours'],day_hours=params['day_hours'],effort_phase_factor=params['effort_phase_factor'])
        months=calc('cocomo_schedule',C=params['C'],JH=jh,effort_phase_factor=params['effort_phase_factor'],day_hours=params['day_hours'],month_hours=params['month_hours'],SCED=params['SCED'],F=F,schedule_phase_factor=params['schedule_phase_factor'])
        days=rounded(jh,spec['rounding_jh'])
        return dict(ksloc=ksloc,raw_jh=jh,jh=days,cost_eur_ht=_cost(unit,days),months=months,measured_units=native_size,additional_units=sum(x['units'] for x in extra),family_units=family_size,groups=groups,completions=extra,file_count=len(measured),program_units=sum(r['program_units'] for r in measured),declarative_units=sum(r['declarative_units'] for r in measured),gap_jh=calc('signed_gap',candidate=jh,reference=unit['total_jh']),gap_pct=calc('signed_gap_pct',candidate=jh,reference=unit['total_jh']))
    results=[]
    selected=measures['selected_files']
    require(scope['anchor']=='unidata' and products[scope['anchor']]['repos']==['unidata'], 'Selection does not match the Unidata reference')
    for product in products.values():
        primary=estimate(product,1,selected)
        primary.update(id=product['id'],label=product['label'],scope=product['scope'],license=product['license'],technology=product['technology'],repositories=[dict(id=r,**measures['repos'][r],url=measures['repos'][r]['origin'].removesuffix('.git')+('/-/tree/' if 'gitlab.com' in measures['repos'][r]['origin'] else '/tree/')+measures['repos'][r]['commit']) for r in product['repos']],sensitivity=[dict(weight=w,jh=estimate(product,w,selected)['jh']) for w in (.5,2)])
        results.append(primary)
    initial=estimate(products[scope['anchor']],1,measures['files'])
    anchor=next(p for p in results if p['id']==scope['anchor'])
    review=dict(measures['unidata_review'],initial={k:initial[k] for k in ('jh','raw_jh','ksloc','measured_units','file_count')},removed_units=initial['measured_units']-anchor['measured_units'])
    engineering=measures['engineering']
    work=unit.get('trace',{}).get('work_package_adoption',{}).get('work',[])
    if engineering['work_jh']=={w['id']:w['jh'] for w in work}:
        require(engineering['central_jh']==unit['total_jh'], 'Adopted engineering effort drift')
        engineering=dict(engineering,status='adopted')
    else:
        engineering=dict(engineering,retained_jh=unit['total_jh'],gap_jh=engineering['central_jh']-unit['total_jh'])
    return dict(engineering=engineering,unidata_review=review,id=spec['id'],date=spec['date'],status=spec['status'],labels=spec['labels'],anchor=scope['anchor'],anchor_basis=scope['anchor_basis'],products=results,retained=dict(jh=unit['total_jh'],cost_eur_ht=unit['cost_eur_ht']),coverage=[{k:row[k] for k in ('id','native_id','label','group','qualification','completion_refs')} for row in scope['coverage']],family_adapters=scope['family_adapters'],family_prototypes=scope['family_prototypes'],assumptions=scope['assumptions'],exclusions=scope['exclusions'],unknowns=scope['unknowns'],cosmic_jh=None,confidence_interval=None,params=dict(params,E=E,F=F),report_ref=spec['report_ref'])
