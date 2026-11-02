"""Adopt measured OSS selections while replaying the immutable previous contracts."""
from copy import deepcopy
from estimation_inputs import require
from estimation_preparation import close, number


def prepare_revision(documents, contract, registry, formula, use_cache=False):
    from estimation_preparation import prepare
    from estimation_calculation import rounded
    from core_product_estimate import apportioned
    basis = documents[contract['inputs']['revision_basis']]
    proposal = documents[contract['inputs']['revision_proposal']]
    hypotheses = documents[contract['inputs']['revision_hypotheses']]
    require(basis['id'] == 'oss-reference-adoption', 'Invalid revision basis')
    old_registry = basis['registry']
    original = next(c for c in old_registry['calculations'] if c['unit_id'] == contract['unit_id'])
    require(original['scope'] == contract['scope'] and original['funding_claims'] == contract['funding_claims'], 'Revision scope or funding changed')
    require(original['recipe'] != 'oss_reference_revision_v1', 'Recursive revision basis')
    prior = prepare(documents, original, old_registry, formula, use_cache=use_cache)
    row = next(r for r in proposal['units'] if r['id'] == contract['unit_id'])
    unit = next(u for u in basis['units'] if u['id'] == contract['unit_id'])
    require(row['capabilities'] == unit['capabilities'] and row['professional_functions'] == unit.get('professional_functions', []), 'Revision functional scope changed')
    close(row['adopted_jh'], unit['total_jh'], 'Revision original decision')
    details = row['calculation_details']
    audit = documents[hypotheses['baseline']]
    audited = next(u for u in audit['units'] if u['id'] == unit['id'])
    if original['recipe'] == 'native_new_module_analogies_v1':
        native = documents[original['inputs']['native_inputs']]
        h = native['hypotheses']; template = native['schema_templates']['axelor']
        scaffold = native['new_module_scaffolding']['axelor']['program_units_per_new_service_module']
        blocks = []
        require(set(hypotheses['ownership']) == {m['id'] for m in h['modules']}, 'Ownership selection scope')
        for module in h['modules']:
            choice = hypotheses['ownership'][module['id']]
            bank = native['banks'][choice['product']]['central'][choice['bank']]['program_units']
            program = formula('module_analogy', reference_units=bank, fraction=module['central'], scaffold_units=scaffold)
            declarative = 0
            for schema in h['schemas']:
                if schema['package'] != module['id']: continue
                n = len(schema['fields']); view = int(schema['view'])
                program += n * template['program_per_field'] + template.get('program_per_new_model', 0)
                declarative += n * template['declarations_per_field'] + template['per_new_model'] + view * (n * template['view_field'] + template['view_model'])
            blocks.append(program + declarative)
        size = sum(blocks) + sum(h['configuration'].values())
    elif original['recipe'] == 'coherent_components_v1':
        pieces = []
        require({r['family'] for r in details['families']} == set(audited['families']), 'Revision family scope')
        for part in details['families']:
            family = part['family']; old = audited['families'][family]['axelor']
            close(part['baseline_size'], old['total'], 'Revision family baseline')
            close(part['old_bank'], old['analogue'], 'Revision original analogue')
            choice = hypotheses['families'].get(family)
            bank = old['analogue']
            if choice and choice['kind'] == 'native_bank': bank = audited['families'][family][choice['product']]['analogue']
            elif choice and choice['kind'] == 'selected_methods':
                selection = proposal['measured_analogue_selections'][choice['selector']]
                atoms = [(f['repo'], f['path'], a) for f in selection['files'] for a in f['atoms']]
                require(len(atoms) == len(set(atoms)) == selection['units'], 'Revision measured atom count')
                require(selection['product'] == part['product'], 'Revision selected product')
                bank = len(atoms)
            elif choice and choice['kind'] == 'stock_bank':
                ownership = documents['audits/2026-10-30-propriete-stock-calcul-02/inputs.json']
                bank = ownership['banks'][choice['product']]['central'][choice['bank']]['program_units']
            close(bank, part['new_bank'], 'Revision selected analogue')
            value = old['total'] + (bank - old['analogue']) * number(part['fraction'], 'module fraction') * number(part['module_count'], 'module count')
            number(value, 'revised family size', positive=True); close(value, part['candidate_size'], 'Revision family size')
            pieces.append(value)
        close(sum(p['baseline_size'] for p in details['families']), prior['trace']['component_sizes']['axelor']['equivalent_units'], 'Revision baseline size')
        size = sum(pieces)
    elif original['recipe'] == 'professional_components_v1':
        inputs = documents[original['inputs']['proposal_inputs']]
        banks = {}
        for group in original['recipe_parameters']['module_groups']:
            patterns = hypotheses['professional'].get({'admin-security':'admin_supplied_patterns','operations-lifecycle':'operations_supplied_patterns'}.get(group, ''), [])
            removed = hypotheses['professional']['removed_studio_files'] if group == 'process-studio' else []
            files = [f for f in inputs['measurements']['files'] if f['group'] == group and f['product'] == 'axelor' and f['path'] not in removed and not any(p in '/'+f['path'] for p in patterns)]
            bank = sum(f['program_units'] + f['declarative_units'] - f['existing_MD_credit_units'] for f in files)
            if group == 'analytics-mining':
                bank = max(sum(f['program_units'] + f['declarative_units'] - f['existing_MD_credit_units'] for f in inputs['measurements']['files'] if f['group'] == group and f['product'] == product) for product in ('erpnext','odoo','tryton','axelor'))
            close(bank, proposal['professional_cleaned_banks'][group], 'Revision professional bank')
            banks[group] = bank * inputs['groups'][group]['fraction']
        require(set(banks) == {g['group'] for g in details['groups']}, 'Revision professional groups')
        base = prior['trace']['component_sizes']['axelor']['native_base_units']
        size = base + sum(banks.values())
    else:
        raise ValueError('Unsupported revision baseline recipe')
    close(size, row['equivalent_units'], 'Revision equivalent size')
    c = prior['cocomo']; exponent = formula('cocomo_exponent', B=c['B'], SF_sum=c['SF_sum'])
    effort = formula('cocomo_effort', A=c['A'], KSLOC=size/1000, E=exponent, EM=c['other_EM'], SCED=c['SCED'], month_hours=c['month_hours'], day_hours=c['day_hours'], effort_phase_factor=c['effort_phase_factor'])
    close(effort, row['raw_proposal_jh'], 'Revision COCOMO effort')
    allocation = prior['allocation']; total = rounded(effort, allocation['rounding_jh'])
    close(total, row['proposal_jh'], 'Revision rounding')
    if 'role_effort_jh' in allocation:
        allocation['role_effort_jh'] = apportioned(total, {r['id']:r['jh'] for r in unit['roles']})
    allocation['selected_reference'] = 'selected-oss'
    common = next(r for r in prior['rows'] if r['id'] == 'axelor')['common_jh']
    prior['rows'].append(dict(id='selected-oss', label='Assemblage des références retenues', jh=effort, common_jh=common, complements_jh=effort-common))
    prior['trace']['revision'] = dict(equivalent_units=size, previous_jh=unit['total_jh'], selected_analogues=deepcopy(details))
    if 'component_allocations' in prior['trace']:
        amounts = apportioned(total, {p['family']:p['candidate_size'] for p in details['families']})
        for part in prior['trace']['component_allocations']: part['jh'] = amounts[part['id']]
    return prior


def prepare_scenario_adoption(documents, contract, registry, formula, use_cache=False):
    """Recount the adopted scope and replay the earlier OSS comparison separately."""
    from estimation_preparation import prepare
    from estimation_calculation import rounded
    from core_product_estimate import apportioned
    basis=documents[contract['inputs']['revision_basis']]
    proposal=documents[contract['inputs']['revision_proposal']]
    decision=documents[contract['inputs']['revision_hypotheses']]
    require(basis['id']=='scenario-scope-adoption-basis' and decision['decision_status']=='adopted','Invalid scenario adoption')
    old_registry=basis['registry'];original=next(c for c in old_registry['calculations'] if c['unit_id']==contract['unit_id'])
    for key in ('level','native_id','capabilities','native_source','analysis_sha256'):
        require(original['scope'][key]==contract['scope'][key],'Scenario adoption native scope changed')
    require(original['funding_claims']==contract['funding_claims'],'Scenario adoption funding changed')
    require(original['recipe']!='scenario_scope_adoption_v1','Recursive scenario adoption')
    prior=prepare(documents,original,old_registry,formula,use_cache=use_cache)
    row=deepcopy(next(r for r in proposal['units'] if r['unit_id']==contract['unit_id']))
    unit=next(u for u in basis['units'] if u['id']==contract['unit_id'])
    require(row['baseline_jh']==unit['total_jh'] and row['baseline_CFP']==prior['functional']['CFP'],'Stale scenario basis')
    ids=row['removed_process_ids']
    old_cosmic=documents[row['basis_path']]
    require(not row['kept_process_ids'] and len(ids)==len(set(ids)) and set(ids)=={p['id'] for p in old_cosmic['processes']},'Scenario scope overlaps old processes')
    require(row['benchmark']=={k:old_cosmic[k] for k in ('hours_per_CFP','factor','day_hours')},'Scenario benchmark changed')
    processes=row['processes'];allowed={c['id'] for c in unit['capabilities']}
    require(bool(processes) and len({p['id'] for p in processes})==len(processes),'Duplicate scenario process')
    for p in processes:
        require(bool(p['capabilities']) and set(p['capabilities'])<=allowed and p['trigger'] and p['E'] and (p['W'] or p['X']),'Invalid scenario functional boundary')
        for key in ('E','R','W','X'):require(len(set(p[key]))==len(p[key]) and all(isinstance(v,str) and v for v in p[key]),'Duplicate scenario movement')
    cfp=sum(len(p[k]) for p in processes for k in ('E','R','W','X'))
    raw=formula('cosmic_effort',CFP=cfp,**row['benchmark']);days=rounded(raw,row['rounding_jh'])
    close(cfp,row['CFP'],'Adopted scenario count');close(raw,row['raw_jh'],'Adopted scenario effort');close(days,row['proposal_jh'],'Adopted scenario rounding')
    selected=next(r for r in decision['units'] if r['id']==unit['id'])
    close(days,selected['proposal_jh'],'Adoption decision effort')
    allocation=prior['allocation'];allocation.update(role_effort_jh=apportioned(days,{r['id']:r['jh'] for r in unit['roles']}),role_allocation_basis='Proportions de rôles antérieures conservées sur le nouveau périmètre fonctionnel.',rounding_jh=row['rounding_jh'])
    prior['method']='COSMIC × ISBSG';prior['retained_effort_jh']=raw
    prior['functional']={'CFP':cfp,**row['benchmark']}
    prior['trace']['CFP']=cfp;prior['trace']['processes']=len(processes)
    prior['trace']['scope_adoption']=dict(previous_jh=unit['total_jh'],previous_CFP=row['baseline_CFP'],CFP=cfp,processes=processes,comparison_scope='historical_oss_scope',unit_id=unit['id'])
    def family(p):
        id=p['id'];unit_id=unit['id']
        if unit_id=='supply-controls-java-spring':return 'eligibility' if id.startswith('eligibility') else 'disposition' if id.startswith('disposition') else 'policies'
        if unit_id=='orders-java-spring':return 'orders'
        if unit_id=='master-plan-java-spring':return 'plan-preparation' if id in ('plan-qualify','plan-consume','plan-supply','plan-reconcile') else 'master-plan'
        if unit_id=='supply-decisions-java-spring':
            if id.startswith('backlog'):return 'backlog'
            if id.startswith('opt-'):return 'optimization'
            if id.startswith('promise'):return 'promising'
            if id.startswith('coordination') or id=='service-release':return 'coordination'
            return 'service-planning'
        if id.startswith('goods'):return 'goods-orders'
        if id.startswith('transport'):return 'transport-orders'
        if id.startswith('customs'):return 'customs'
        if id.startswith(('billing','payment')):return 'financial-services'
        return 'assurance'
    weights={}
    for p in processes:
        p['family']=family(p);weights[p['family']]=weights.get(p['family'],0)+sum(len(p[k]) for k in ('E','R','W','X'))
    prior['trace']['scope_adoption']['family_CFP']=weights
    if 'component_allocations' in prior['trace']:
        parts=prior['trace']['component_allocations'];require({p['id'] for p in parts}==set(weights),'Scenario family partition mismatch');amounts=apportioned(days,weights)
        for part in parts:part['jh']=amounts[part['id']]
    return prior


def prepare_work_package_adoption(documents, contract, registry, formula, use_cache=False):
    """Replay a user-adopted sum of project deliverables, keeping code/CFP comparisons historical."""
    from estimation_preparation import prepare, unique
    from core_product_estimate import apportioned
    basis=documents[contract['inputs']['revision_basis']]
    scope=documents[contract['inputs']['revision_proposal']]
    decision=documents[contract['inputs']['revision_hypotheses']]
    require(basis['id']=='work-package-adoption-basis' and scope['id']=='adopted-work-packages','Invalid work-package basis')
    require(scope['status']==decision['status']==decision['decision_status']=='adopted','Work-package decision is not adopted')
    old_registry=basis['registry'];original=next(c for c in old_registry['calculations'] if c['unit_id']==contract['unit_id'])
    seen=set()
    replay_registry=old_registry
    while original['recipe']=='work_package_adoption_v1':
        name=original['inputs']['revision_basis'];require(name not in seen,'Cyclic work-package adoption');seen.add(name)
        earlier=documents[name];require(earlier['id']=='work-package-adoption-basis','Invalid previous work-package basis')
        replay_registry=earlier['registry']
        original=next(c for c in replay_registry['calculations'] if c['unit_id']==contract['unit_id'])
    for key in ('level','native_id','capabilities','native_source','analysis_sha256'):
        require(original['scope'].get(key)==contract['scope'].get(key),'Work-package native scope changed')
    require(original['funding_claims']==contract['funding_claims'],'Work-package funding changed')
    prior=prepare(documents,original,replay_registry,formula,use_cache=use_cache)
    unit=next(u for u in basis['units'] if u['id']==contract['unit_id'])
    rows=unique(scope['units'],'id','work-package unit');row=rows[unit['id']]
    selected=unique(decision['units'],'id','work-package decision')[unit['id']]
    close(selected['adopted_jh'],unit['total_jh'],'Work-package previous decision')
    all_work=[w for r in rows.values() for w in r['work']]
    unique(all_work,'id','work-package identifier')
    owned={c['mechanism'] for c in contract['funding_claims'] if c['mode']=='funded'}
    allowed=set(scope['scenario_ids']);require(len(allowed)==len(scope['scenario_ids']),'Duplicate scenario identifier')
    for w in row['work']:
        require(type(w['jh']) is int and w['jh']>0,'Invalid work-package effort')
        require(w['funding_ref'] in owned,'Foreign work-package funding')
        require(w['scope'] and w['reuse'] and w['scenario_refs'] and set(w['scenario_refs'])<=allowed,'Incomplete work-package boundary')
        require(w['effort_status']=='engineering_assumption_not_observed','Work-package assumption cannot become observed effort')
    require(bool(row['work']),'Empty work-package scope')
    if unit['id']=='master-data-java-spring':
        require(any(w['id']=='MD09' and w['jh']>0 for w in row['work']),'Missing correction editing')
    days=sum(w['jh'] for w in row['work']);close(days,selected['proposal_jh'],'Adopted work-package sum')
    prior['method']='Estimation détaillée par livrable'
    prior['retained_effort_jh']=days
    prior['allocation'].update(role_effort_jh=apportioned(days,{r['id']:r['jh'] for r in unit['roles']}),rounding_jh=1,role_allocation_basis='Proportions antérieures conservées pour valoriser les livrables adoptés. Hypothèse de répartition, pas un plan de recrutement.')
    prior['trace']['work_package_adoption']=dict(work=deepcopy(row['work']),previous_jh=unit['total_jh'],retained_jh=days,comparison_scope='historical',effort_status='engineering_assumption_not_observed')
    return prior
