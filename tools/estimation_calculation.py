"""Reproduce retained calculations and alignment from the canonical business metamodel."""
import ast
import math
import operator
from decimal import Decimal, ROUND_HALF_UP
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read
from model_context import model_memo, scoped_model

META = 'source/fondamentaux.yaml'
SCHEMA = 'source/schema-fondamentaux.yaml'
ARITHMETIC = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
              ast.Div: operator.truediv, ast.Pow: operator.pow}


@model_memo
def metamodel(document=None):
    doc = document if document is not None else read(ROOT / META)
    Draft202012Validator(read(ROOT / SCHEMA)).validate(doc)
    model = doc['estimation_model']
    for collection in ('objects', 'relations', 'rules'):
        ids = [r['id'] for r in model[collection]]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate metamodel ' + collection)
    ids = {o['id'] for o in model['objects']}
    for r in model['relations']:
        if r['source'] not in ids or r['target'] not in ids:
            raise ValueError('Unknown metamodel relationship endpoint')
    rules = {r['id'] for r in model['rules']}
    implemented = []
    for item in model['implementations']:
        if not (ROOT / item['path']).is_file() or not set(item['rules']) <= rules:
            raise ValueError('Unknown rule implementation')
        implemented.extend(item['rules'])
    if len(implemented) != len(set(implemented)) or set(implemented) != rules:
        raise ValueError('Every rule requires exactly one implementation owner')
    for o in model['objects']:
        if not (ROOT / o['owner']).is_file():
            raise ValueError('Unknown object owner: ' + o['owner'])
    return model


def formula(rule_id, **values):
    rule = next(r for r in metamodel()['rules'] if r['id'] == rule_id)
    return evaluate_rule(rule, **values)


def evaluate_rule(rule, **values):
    rule_id = rule['id']
    if rule['kind'] != 'arithmetic' or set(values) != set(rule['variables']):
        raise ValueError('Invalid arithmetic rule inputs: ' + rule_id)
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values.values()):
        raise ValueError('Nonfinite rule input')
    if set(rule.get('domains', {})) != set(values):
        raise ValueError('Missing arithmetic input domain')
    for key, value in values.items():
        Draft202012Validator(rule['domains'][key]).validate(value)
    if rule_id in ('spread','spread_pct') and values['maximum'] < values['minimum']:
        raise ValueError('Reversed spread bounds')
    if rule_id == 'coverage' and values['covered'] > values['total']:
        raise ValueError('Coverage above scope')
    def visit(node):
        if isinstance(node, ast.Expression): return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float): return node.value
        if isinstance(node, ast.Name): return values[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in ARITHMETIC:
            return ARITHMETIC[type(node.op)](visit(node.left), visit(node.right))
        raise ValueError('Unsupported arithmetic expression')
    result = visit(ast.parse(rule['expression'], mode='eval'))
    if not math.isfinite(result): raise ValueError('Nonfinite rule result')
    return result


def alignment(candidate, reference):
    if candidate is None or reference is None:
        return dict(gap_jh=None, gap_pct=None, reason='missing_result')
    if reference <= 0:
        return dict(gap_jh=candidate-reference, gap_pct=None, reason='nonpositive_reference')
    return dict(gap_jh=formula('signed_gap',candidate=candidate,reference=reference),
                gap_pct=formula('signed_gap_pct',candidate=candidate,reference=reference),reason=None)


def rounded(value, step):
    if step <= 0: raise ValueError('Invalid rounding step')
    result=(Decimal(str(value))/Decimal(str(step))).quantize(Decimal('1'),rounding=ROUND_HALF_UP)*Decimal(str(step))
    return int(result) if result==result.to_integral_value() else float(result)


@scoped_model
def calculate(binding):
    if set(binding) != {'id'}:
        raise ValueError('A calculation requires exactly one identifier')
    return _calculate(binding['id'])


@model_memo
def _calculate(calculation_id):
    binding = {'id': calculation_id}
    from estimation_inputs import contract, _frozen_calculation_proofs
    from estimation_preparation import prepare
    specification, registry = contract(binding)
    prepared = prepare(_frozen_calculation_proofs(registry), specification, registry, formula, use_cache=True)
    c, inputs = prepared['cocomo'], prepared['allocation']
    E = formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum'])
    F = formula('schedule_exponent',D=c['D'],E=E,B=c['B'])
    rows = prepared['rows']
    anchor=next(r for r in rows if r['id']==inputs['selected_reference'])
    total=rounded(anchor['jh'],inputs['rounding_jh'])
    functional=formula('cosmic_effort',**{k:prepared['functional'][k] for k in ('CFP','hours_per_CFP','factor','day_hours')})
    for r in rows:r.update(alignment(r['jh'],anchor['jh']))
    months=formula('cocomo_schedule',C=c['C'],JH=total,effort_phase_factor=c['effort_phase_factor'],
        day_hours=c['day_hours'],month_hours=c['month_hours'],SCED=c['SCED'],F=F,schedule_phase_factor=c['schedule_phase_factor'])
    if 'role_effort_jh' in inputs:
        allocated=dict(inputs['role_effort_jh'])
        if set(allocated)!=set(inputs['role_labels']) or any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in allocated.values()) or sum(allocated.values())!=total:
            raise ValueError('Explicit professional role allocation drift')
        phases=prepared['activity_source']['phase_effort_percent_of_base']
        activities=[dict(id=a['id'],label=a['label'],jh=total*sum(x*y for x,y in zip(phases,a['percent_by_phase']))/100/sum(phases),role_weights={},published_percent_by_phase=a['percent_by_phase'],role_allocation_basis=inputs['role_allocation_basis']) for a in prepared['activity_source']['activities']]
    else:
        activities=[]; roles={key:0. for key in inputs['role_labels']}
        phases=prepared['activity_source']['phase_effort_percent_of_base']
        for a in prepared['activity_source']['activities']:
            weights=inputs['activity_role_weights'][a['id']]
            if not math.isclose(sum(weights.values()),1) or not set(weights)<=set(a['possible_flow_roles']):
                raise ValueError('Invalid activity to role allocation')
            effort=total*sum(x*y for x,y in zip(phases,a['percent_by_phase']))/100/sum(phases)
            activities.append(dict(id=a['id'],label=a['label'],jh=effort,role_weights=weights,
                                   published_percent_by_phase=a['percent_by_phase']))
            for role,weight in weights.items():roles[role]+=effort*weight
        if not math.isclose(sum(roles.values()),total):raise ValueError('Activity total drift')
        step=inputs['role_rounding_jh']
        allocated={k:math.floor(v/step)*step for k,v in roles.items()}
        order=sorted(roles,key=lambda k:(-(roles[k]/step-math.floor(roles[k]/step)),k))
        for role in order[:round((total-sum(allocated.values()))/step)]:allocated[role]+=step
        if sum(allocated.values())!=total:raise ValueError('Role rounding total drift')
    comparison = dict(specification['comparison'])
    comparison['scope_status'] = 'partial_scope' if any(r['classification'] in ('native_excess','unknown') for r in comparison['scope_rows']) else 'declared_scope'
    comparison_status = comparison['scope_status'] + '_' + comparison['activity_status'] + '_activities_' + comparison['service_status'] + '_service'
    maximum,minimum=max(r['jh'] for r in rows),min(r['jh'] for r in rows)
    return dict(method='COCOMO II',total_jh=total,months=rounded(months,inputs.get('schedule_rounding_months',1)),unrounded_months=months,
        roles=allocated,activities=activities,activity_source=prepared['activity_source'],
        trace=prepared['trace'],funding=[dict(m,funding_mode=next(x['mode'] for x in specification['funding_claims'] if x['mechanism']==m['id'])) for m in registry['mechanisms'] if m['id'] in {x['mechanism'] for x in specification['funding_claims']}],
        consolidation=registry['consolidation'],
        alignment=dict(reference_id=anchor['id'],reference_label=anchor['label'],reference_jh=anchor['jh'],
            rows=rows,functional=dict(id='cosmic-isbsg',label='COSMIC × ISBSG',jh=functional,**alignment(functional,anchor['jh'])),
            spread_jh=formula('spread',maximum=maximum,minimum=minimum),
            spread_pct=formula('spread_pct',maximum=maximum,minimum=minimum,reference=anchor['jh']),
            rounding_delta_jh=total-anchor['jh'],
            implied_hours_per_CFP=formula('implied_productivity',JH=anchor['jh'],day_hours=c['day_hours'],CFP=prepared['functional']['CFP']),
            comparability_status=comparison_status,
            comparison=comparison,
            shared_complements_pct=100*anchor['complements_jh']/anchor['jh'],
            limitations=' '.join([specification['comparison']['activity_note'],specification['comparison']['service_note']]),
            labels=metamodel()['labels']))
