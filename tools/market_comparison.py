"""Qualify ERP comparisons by native Business Area, without economic mutation."""
from copy import deepcopy
from urllib.parse import urlsplit
from pathlib import PurePosixPath
from jsonschema import Draft202012Validator, FormatChecker
from validate_stacks import ROOT, read
from capability_catalog import native, analysis
from model_context import scoped_model

SOURCE='source/comparaison-solutions.yaml'
SCHEMA='source/schema-comparaison-solutions.yaml'

def _fail(path,reason):
    raise ValueError('ERR_MARKET_COMPARISON '+path+': '+reason)

def _index(rows,key,path):
    result={r[key]:r for r in rows}
    if len(result)!=len(rows):_fail(path,'duplicate identity')
    return result

def _refs(values,known,path):
    if len(values)!=len(set(values)) or not set(values)<=set(known):_fail(path,'duplicate or unknown reference')

@scoped_model
def build_market_comparison(market, *, spec=None, snapshot=None, grid=None, mechanisms=None, retained=None):
    spec=read(ROOT/SOURCE) if spec is None else deepcopy(spec)
    errors=sorted(Draft202012Validator(read(ROOT/SCHEMA),format_checker=FormatChecker()).iter_errors(spec),key=lambda e:str(e.path))
    if errors:_fail('.'.join(map(str,errors[0].path)),errors[0].message)
    snapshot=native() if snapshot is None else snapshot
    grid=analysis() if grid is None else grid
    mechanisms=read(ROOT/'source/calculs-estimation-core.yaml')['mechanisms'] if mechanisms is None else mechanisms
    retained=read(ROOT/'source/estimations-core-retenues.yaml')['units'] if retained is None else retained
    frame=market['reperes_build_core'];fiches=frame['fiches_produit'];excluded=set(frame['etude_oss']['perimetre']['bc_exclus'])
    _refs(spec['context']['product_refs'],fiches,'context.product_refs')
    if set(spec['context']['product_refs'])!=set(fiches):_fail('context','all compared products required')
    nodes={n['id']:n for n in snapshot['nodes']}
    bas={b['chemin'][-2]:nodes[b['chemin'][-2]] for b in grid['blocs']}
    specs=_index(spec['business_areas'],'business_area_ref','business_areas')
    if set(specs)!=set(bas):_fail('business_areas','native Business Area universe required')
    sources=_index(spec['sources'],'id','sources')
    for s in sources.values():
        value=s['source_ref'];u=urlsplit(value)
        # A citation can refer to an original that is intentionally not served.
        # Availability of its link is resolved separately by the static manifest.
        if u.scheme:
            if u.scheme!='https' or not u.netloc:_fail(s['id'],'HTTPS source required')
        elif ('\\' in value or '..' in PurePosixPath(value).parts or not value.startswith(('source/','sources/','tools/'))):
            _fail(s['id'],'repository source path required')
    mechanisms_by_id=_index(mechanisms,'id','mechanisms')
    gaps=_index(spec['gaps'],'id','gaps')
    for g in gaps.values():
        _refs(g['business_area_refs'],bas,g['id']+'.business_areas')
        _refs(g['product_refs'],fiches,g['id']+'.products')
        _refs(g['evidence_refs'],sources,g['id']+'.evidence')
        _refs(g['funding_owner_refs_to_reconcile'],mechanisms_by_id,g['id']+'.funding')
        if not g['evidence_refs'] or not g['business_area_refs'] or not g['product_refs']:_fail(g['id'],'gap requires scope and evidence')
        if g['treatment_status']=='traite':_fail(g['id'],'treatment requires a separately reviewed funding decision, not this documentary comparison')
    by_cap={b['capacite_id']:b for b in grid['blocs']}
    crosswalk=_index(spec['rfi_crosswalk'],'id','rfi_crosswalk')
    for x in crosswalk.values():
        if x['capability_ref'] not in by_cap:_fail(x['id'],'unknown capability')
        b=by_cap[x['capability_ref']]
        if x['bc_ref']!=b['id'] or x['business_area_ref']!=b['chemin'][-2] or b['id'] in excluded:_fail(x['id'],'crosswalk scope mismatch')
        _refs(x['proposed_need_refs'],[n['id'] for n in b['fonctions']],x['id']+'.needs')
        _refs(x['evidence_refs'],sources,x['id']+'.evidence')
        if not x['proposed_need_refs'] or x['gap_ref'] not in gaps or x['rfi_source_ref'] not in sources:_fail(x['id'],'crosswalk gap or source missing')
        if x['business_area_ref'] not in gaps[x['gap_ref']]['business_area_refs']:_fail(x['id'],'gap must include mapped Business Area')
    instruction=market.get('instruction',{})
    pair_index={(x['capability_ref'],x['product_ref']):x for x in instruction.get('rows',[])}
    rows=[]
    for bid,n in bas.items():
        r=specs[bid];blocks=[b for b in grid['blocs'] if b['chemin'][-2]==bid]
        included=[b for b in blocks if b['id'] not in excluded]
        assessments=_index(r['assessments'],'product_ref',bid+'.assessments')
        if set(assessments)!=set(fiches):_fail(bid,'one assessment per product required')
        cells=[]
        for pid in fiches:
            c=deepcopy(assessments[pid]);_refs(c['evidence_refs'],sources,bid+'.evidence')
            if c['reading_status'] not in ('non_etabli','hors_perimetre') and not c['evidence_refs']:_fail(bid,'documented assessment requires evidence')
            if (c['reading_status']=='hors_perimetre')!= (not included):_fail(bid,'excluded scope cannot be assessed as covered')
            pairs=[pair_index.get((b['capacite_id'],pid)) for b in included]
            if c['complete_ba_coverage'] is not None:
                if c['complete_ba_coverage'] is False:_fail(bid,'unknown is null, not a proven absence')
                if (not included or c['reading_status'] in ('ecart_explicite','non_etabli','hors_perimetre') or not c['review'] or c['review']['decision']!='retenu' or any(not p or p['pending_need_refs'] for p in pairs) or any(bid in g['business_area_refs'] and pid in g['product_refs'] for g in gaps.values())):
                    _fail(bid,'full coverage requires reviewed qualification of every included need')
            c['qualification_refs']=[q for p in pairs if p for q in p['qualification_refs']]
            c['gap_refs']=[g['id'] for g in gaps.values() if bid in g['business_area_refs'] and pid in g['product_refs']]
            cells.append(c)
        rows.append(dict(id=bid,name=n['fields']['name'],target=r['target'],next_qualification=r['next_qualification'],
            hierarchy=[dict(id=k,name=nodes[k]['fields']['name'],kind=nodes[k]['kind']) for k in blocks[0]['chemin'][:-2]],
            capabilities=[dict(id=b['capacite_id'],bc_ref=b['id'],name=nodes[b['capacite_id']]['fields']['name'],included=b['id'] not in excluded,needs=deepcopy(b['fonctions'])) for b in blocks],
            included=bool(included),cells=cells,crosswalk_refs=[x['id'] for x in crosswalk.values() if x['business_area_ref']==bid]))
    from gap_instruction import compile_gap_instruction
    for g in gaps.values():
        if 'instruction' in g:
            g['instruction']=compile_gap_instruction(g['instruction'],g,grid,sources,mechanisms_by_id,retained)
            g['instruction']['buy_product_labels']={pid:fiches[pid]['nom'] for pid in g['product_refs']}
    # Only the adopted owner supplies this value. Gaps carry no monetary adapter.
    for g in gaps.values():
        g['funding_candidates']=[dict(id=k,label=mechanisms_by_id[k]['label'],owner=mechanisms_by_id[k]['funding_owner']) for k in g['funding_owner_refs_to_reconcile']]
    result=dict(id=spec['id'],date=spec['date'],source_ref=SOURCE,reading=deepcopy(spec['reading']),context=deepcopy(spec['context']),
        products=[dict(id=pid,label=f['nom'],family=f['famille'],version=f['version_edition'],components=deepcopy(f['composition']['produits'])) for pid,f in fiches.items()],
        sources=list(sources.values()),rows=rows,gaps=list(gaps.values()),rfi_crosswalk=list(crosswalk.values()),
        summary=dict(business_areas=len(rows),compared_business_areas=sum(r['included'] for r in rows),products=len(fiches),
            compared_capabilities=sum(b['id'] not in excluded for b in grid['blocs']),excluded_bc_refs=sorted(excluded),
            open_gaps=len(gaps),reviewed_business_area_pairs=sum(c['complete_ba_coverage'] is True for r in rows for c in r['cells']),
            adopted_java_spring_jh=sum(u['total_jh'] for u in retained if u['stack']=='java-spring'),net_extra_jh=None,
            functional_qualification='partial',funding_reconciliation='not_established'))

    from budget_supplements import compile_budget_review
    result['budget_review']=compile_budget_review(result,grid,list(mechanisms_by_id.values()))
    return result
