"""Adopted study rates and isolated regional valuation with the existing engine."""
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP
import math
from contextvars import ContextVar
from statistics import median
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read
from model_context import scoped_model, model_memo, SourceSnapshot, CURRENT

SOURCE = 'source/tarifs-projet.yaml'
SCHEMA = 'source/schema-tarifs-projet.yaml'
OBSERVATIONS = 'source/preetude-couts-marche.yaml'
RATE_ZONE = ContextVar('flow_rate_zone', default='paris')
RATE_REFERENCE = ContextVar('flow_rate_reference', default=None)


def rounded(value, step=25):
    return int((Decimal(str(value))/Decimal(step)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)*step)


def province_price(paris, ratio, step=25):
    return rounded(paris*ratio, step)


def observed_ratio(role):
    for observation in role['observations']:
        areas = observation['areas']
        capital = [a for a in areas if a['label'] in ('Paris', 'Île-de-France')]
        regional = [a for a in areas if a['label'] not in ('Paris', 'Île-de-France', 'France, non ventilée')]
        if capital and regional:
            denominator = (capital[0]['min'] + capital[0]['max']) / 2
            numerator = sum((a['min'] + a['max']) / 2 for a in regional) / len(regional)
            if denominator <= 0 or numerator <= 0:
                raise ValueError('ERR_RATE_GEOGRAPHY')
            return dict(ratio=numerator/denominator, numerator=numerator, denominator=denominator,
                        source_id=observation['source_id'], segment=observation['segment'])
    return None


def reference(ref):
    value = read(ROOT/ref['path'])
    for part in ref['pointer'].split('.'):
        value = value[part]
    if 'role_id' in ref:
        value = next(r for r in value if r['id'] == ref['role_id'])[ref['field']]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError('ERR_RATE_REFERENCE')
    return value


def compile_rates(policy, study, values):
    roles = {r['id']:r for r in study['roles']}
    decisions = {r['id']:r for r in policy['roles']}
    if len(decisions) != len(policy['roles']) or set(roles) != set(decisions):
        raise ValueError('ERR_RATE_ROLE_COVERAGE')
    pools = {}
    for group, peers in policy['regional_peers'].items():
        if not peers or len(peers) != len(set(peers)) or any(p not in roles for p in peers):
            raise ValueError('ERR_RATE_PEERS')
        ratios = [dict(role=id, **observed_ratio(roles[id])) for id in peers]
        pools[group] = ratios
    output = []
    for id, decision in decisions.items():
        role = roles[id]
        paris = values[id]
        if isinstance(paris, bool) or not isinstance(paris, (int,float)) or not math.isfinite(paris) or paris <= 0:
            raise ValueError('ERR_RATE_VALUE')
        target = decision['ratio_role']
        if target not in roles:
            raise ValueError('ERR_RATE_ANALOGY')
        observed = observed_ratio(roles[target])
        if observed:
            peers = [dict(role=target, **observed)]
            kind = 'same_profile' if target == id else 'role_analogy'
        else:
            peers = pools[role['group']]
            kind = 'family_analogy'
        ratio = median(p['ratio'] for p in peers)
        province = province_price(paris, ratio, policy['rounding_eur'])
        if province <= 0:
            raise ValueError('ERR_RATE_VALUE')
        output.append(dict(id=id, title=role['title'], group=role['group'], mission=role['mission'],
            funding=role['funding'], paris=paris, province=province,
            ratio=ratio, geography_method=kind, peers=peers, rationale=decision['rationale'],
            observations=deepcopy(role['observations']), status=decision['status']))
    return dict(date=policy['date'], default_zone=policy['default_zone'], method=deepcopy(policy['method']),
                groups=deepcopy(study['groups']), roles=output, sources=deepcopy(study['sources']))


@scoped_model
@model_memo
def load_rates():
    if RATE_REFERENCE.get() is not None:
        return deepcopy(RATE_REFERENCE.get())
    policy = read(ROOT/SOURCE)
    Draft202012Validator(read(ROOT/SCHEMA)).validate(policy)
    study = read(ROOT/OBSERVATIONS)['rate_study']
    values = {r['id']:reference(r['paris_ref']) if 'paris_ref' in r else r['paris_value'] for r in policy['roles']}
    return compile_rates(policy, study, values)


def regional_study(base, zone):
    if zone == 'paris':
        return base
    if zone != 'province':
        raise ValueError('ERR_RATE_ZONE')
    policy = read(ROOT/SOURCE)
    rates = base.content['framework']['project_rates']
    prices = {r['id']:r for r in rates['roles']}
    snapshot = SourceSnapshot()
    token = CURRENT.set(snapshot)
    zone_token = RATE_ZONE.set(zone)
    rate_token = RATE_REFERENCE.set(rates)
    try:
        def edit(name, transform):
            path = (ROOT/name).resolve()
            value = read(path)
            transform(value)
            snapshot.documents[path] = value
        for slug, bindings in policy['stack_bindings'].items():
            def stack(doc, bindings=bindings):
                for key, id in bindings.items():
                    row = doc['interventions']['tarifs'][key]
                    if row['reference'] != prices[id]['paris']:
                        raise ValueError('ERR_RATE_FINANCIAL_BINDING')
                    ratio = prices[id]['province']/prices[id]['paris']
                    for field in ('bas','reference','haut'):
                        row[field] = round(row[field]*ratio, 2)
                    row['justification'] = prices[id]['rationale']
            edit('source/stacks/'+slug+'.yaml', stack)
        def transformation(doc):
            for role in doc['equipe_transformation']['roles']:
                role['tarif_eur_jh'] = prices[policy['transformation_bindings'][role['id']]]['province']
        edit('source/modele-composable.yaml', transformation)
        def selection(doc):
            for row in doc['travaux']:
                row['tarif_eur_ht_jh'] = prices[policy['selection_bindings'][row['id']]]['province']
        edit('source/selection-buy.yaml', selection)
        from study_app import Study
        variant = Study()
        variant.content['framework']['project_rates'] = deepcopy(rates)
        snapshot.verify()
        if variant.simulation_contract() != base.simulation_contract():
            raise ValueError('ERR_RATE_SIMULATION_CONTRACT')
        for option in variant.data['options']:
            original = next(o for o in base.data['options'] if o['stack'] == option['stack'])
            if option['prix_abonnements'] != original['prix_abonnements']:
                raise ValueError('ERR_RATE_VENDOR_PRICE')
        return variant
    finally:
        CURRENT.reset(token)
        RATE_ZONE.reset(zone_token)
        RATE_REFERENCE.reset(rate_token)


def financial_variant(base):
    variant = regional_study(base, 'province')
    return dict(zone='province', source_model_version=base.version, baseline=variant.baseline,
        framework=variant.content['framework'], reading=variant.content['economic_evaluations'],
        gross=variant.content['gross_evaluations'])


def adopted_price(id):
    rows = load_rates()['roles']
    return next(r for r in rows if r['id'] == id)[RATE_ZONE.get()]


@scoped_model
@model_memo
def financial_role_rates(slug):
    mappings = read(ROOT/SOURCE)['activity_bindings']
    return {key:adopted_price(id) for key,id in mappings.get(slug, {}).items()}
