"""Reconcile every declared gap and keep unique, unpriced reserves outside adopted budgets."""
from copy import deepcopy
from content_model import resolve_text_tree
from jsonschema import Draft202012Validator,FormatChecker
from validate_stacks import ROOT,read
from model_context import model_memo

SOURCE='source/complements-budgetaires.yaml'
SCHEMA='source/schema-complements-budgetaires.yaml'

def require(ok,message):
    if not ok:raise ValueError('ERR_BUDGET_SUPPLEMENT '+message)

def index(rows,key):
    result={r[key]:r for r in rows}
    require(len(result)==len(rows),'duplicate '+key)
    return result

def refs(values,known,meaning):
    require(len(values)==len(set(values)) and set(values)<=set(known),'invalid '+meaning)

@model_memo
def baseline(calculation_ref):
    from estimation_calculation import calculate
    from estimation_components import unpack_archives
    registry=read(ROOT/'source/calculs-estimation-core.yaml')
    contract=next((c for c in registry['calculations'] if c['id']==calculation_ref),None)
    require(contract is not None,'unknown baseline calculation')
    unit=next((u for u in read(ROOT/'source/estimations-core-retenues.yaml')['units'] if u['id']==contract['unit_id']),None)
    require(unit is not None and unit['stack']==contract['stack'],'invalid baseline owner')
    result=calculate({'id':calculation_ref})
    require(result['total_jh']==unit['total_jh'],'baseline does not reproduce adopted decision')
    families={};processes=[]
    if contract['recipe']=='coherent_components_v1':
        frozen=unpack_archives(read(ROOT/contract['inputs']['archives']))
        selected=set(read(ROOT/contract['inputs']['specification'])['families'])
        families={f['slug']:f for f in frozen['proposal_inputs']['families'] if f['slug'] in selected}
        processes=read(ROOT/contract['inputs']['cosmic'])['processes']
    return dict(calculation_ref=calculation_ref,unit_id=unit['id'],label=unit['label'],adopted_jh=unit['total_jh'],
        families=families,processes=processes,allocations=result['trace'].get('component_allocations',[]),
        evidence_paths=list(contract['inputs'].values()))

def compile_budget_review(comparison,grid,mechanisms,*,spec=None):
    spec=read(ROOT/SOURCE) if spec is None else deepcopy(spec)
    errors=list(Draft202012Validator(read(ROOT/SCHEMA),format_checker=FormatChecker()).iter_errors(spec))
    require(not errors,str(errors[0].message) if errors else '')
    gaps=index(comparison['gaps'],'id');reviews=index(spec['reviews'],'gap_ref');additions=index(spec['additions'],'id')
    require(set(reviews)==set(gaps),'every declared gap requires one review')
    products={p['id']:p for p in comparison['products']}
    needs={n['id']:n for b in grid['blocs'] for n in b['fonctions']}
    sources={s['id']:s for s in comparison['sources']}
    mechanisms=index(mechanisms,'id')
    units=index(read(ROOT/'source/estimations-core-retenues.yaml')['units'],'id')
    meta=read(ROOT/'source/fondamentaux.yaml');phases={p['id'] for p in meta['phases']}
    options={o for s in meta['strategies'] for o in s['option_refs']}
    int_activities=index(read(ROOT/'source/integration.yaml')['activites'],'id')
    mai_activities=index(read(ROOT/'source/maintenance.yaml')['activites'],'id')
    signatures=set()
    for a in additions.values():
        require(a['stack'] in options and a['phase_ref'] in phases,'unknown option or phase')
        refs(a['gap_refs'],gaps,'addition gaps')
        for ref in a['existing_funding_refs']:
            path=(ROOT/ref['source_ref']).resolve()
            require(path.is_relative_to((ROOT/'source').resolve()) and path.is_file(),'invalid existing funding source')
            if ref['source_ref'].startswith(('source/chiffrage/','source/maintenance/')):
                require(path.name.endswith('-'+a['stack']+'.yaml'),'funding source belongs to another option')
            owner=read(path)
            for key in ref['keys']:
                require(isinstance(owner,dict) and key in owner,'missing existing funding locator')
                owner=owner[key]

        signature=(a['stack'],a['phase_ref'],a['work_package_ref'])
        require(signature not in signatures,'duplicate work package funding');signatures.add(signature)
        # No arithmetic adapter: this version records only reserves for which no
        # defensible net estimate exists. Neither zero nor an unsupported price is accepted.
        require(a['estimate_ref'] is None and all(a[k] is None for k in ('net_extra_jh','net_extra_initial_eur_ht','net_extra_annual_eur_ht')),'unsupported estimate')
    rendered=[]
    for gid,r in reviews.items():
        require(set(r['product_actions'])==set(products),'every compared product requires an explicit action')
        refs(r['evidence_refs'],sources,'review evidence')
        refs(r['integration_activity_refs'],int_activities,'integration activities')
        refs(r['maintenance_activity_refs'],mai_activities,'maintenance activities')
        refs(r['addition_refs'],additions,'addition refs')
        require(set(r['addition_refs'])=={a['id'] for a in additions.values() if gid in a['gap_refs']},'bidirectional gap reserve mismatch')
        reserve_pairs={(additions[a]['stack'],additions[a]['phase_ref']) for a in r['addition_refs']}
        no_budget_pairs={(a['stack'],a['phase_ref']) for a in r['non_budget_treatments']}
        require(len(no_budget_pairs)==len(r['non_budget_treatments']) and not reserve_pairs & no_budget_pairs,'incompatible non-budget treatment')
        require(reserve_pairs | no_budget_pairs=={(o,p) for o in options for p in phases},'all economic options and phases must be examined')
        criteria=index(r['criteria'],'id');funding=set()
        for criterion in criteria.values():
            refs(criterion['need_refs'],needs,'native need');refs(criterion['mechanism_refs'],mechanisms,'funding mechanism')
            criterion['funding']=[dict(id=m,label=mechanisms[m]['label'],owner=mechanisms[m]['funding_owner'],owner_label=units[mechanisms[m]['funding_owner']]['label']) for m in criterion['mechanism_refs']]
            funding.update(m['owner'] for m in criterion['funding'])
        traces=[]
        index(r['baseline_refs'],'calculation_ref')
        for b in r['baseline_refs']:
            base=baseline(b['calculation_ref']);refs(b['family_refs'],base['families'],'baseline families')
            require(base['unit_id'] in funding,'baseline unrelated to reviewed mechanisms: '+gid+' '+base['unit_id'])
            families=[base['families'][k] for k in b['family_refs']]
            traces.append(dict(calculation_ref=b['calculation_ref'],unit_id=base['unit_id'],label=base['label'],adopted_jh=base['adopted_jh'],
                allocations=[a for a in base['allocations'] if a['id'] in b['family_refs']],
                family_labels=[f['name'] for f in families],schemas=[s for f in families for s in f['schemas']],
                selected_cfp=sum(len(p['movements']) for p in base['processes'] if any(p['id'].startswith(k+'-') for k in b['family_refs'])) if families else None,
                evidence_paths=base['evidence_paths']))
        r.update(title=gaps[gid]['title'],baselines=traces,funding_owners=[dict(id=k,label=units[k]['label'],adopted_jh=units[k]['total_jh']) for k in sorted(funding)],
            integration_activities=[dict(id=k,label=int_activities[k]['nom']) for k in r['integration_activity_refs']],
            maintenance_activities=[dict(id=k,label=mai_activities[k]['nom']) for k in r['maintenance_activity_refs']],
            product_findings=[dict(id=p['id'],label=p['label'],action=r['product_actions'][p['id']],assessments=[dict(area=x['name'],status=c['reading_status'],summary=c['summary']) for x in comparison['rows'] if x['id'] in gaps[gid]['business_area_refs'] for c in x['cells'] if c['product_ref']==p['id']]) for p in products.values()],
            sources=[sources[k] for k in r['evidence_refs']])
        rendered.append(r)
    return dict(id=spec['id'],date=spec['date'],reading=resolve_text_tree(spec['reading'],read(ROOT/'source/glossaire.yaml'),path=SOURCE),reviews=rendered,additions=list(additions.values()),
        option_labels={o:read(ROOT/('source/stacks/'+o+'.yaml'))['nom'] for o in sorted(options)},
        summary=dict(identified_gaps=len(gaps),reviewed_gaps=len(reviews),reviewed_gap_option_phases=len(reviews)*len(options)*len(phases),
            unique_reserves=len(additions),unpriced_reserves=len(additions),priced_reserves=0,
            net_extra_jh=None,net_extra_initial_eur_ht=None,net_extra_annual_eur_ht=None,
            known_subtotal_initial_eur_ht=None,known_subtotal_annual_eur_ht=None,adopted_amounts_changed=False,functional_qualification='partial'))
