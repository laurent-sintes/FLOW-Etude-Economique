"""Retained family estimates: one funding owner, typed project roles, no blanket gains."""
from copy import deepcopy
import hashlib
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read
from model_context import model_memo, scoped_model
from capability_catalog import analysis
from estimation_inputs import validate_binding, validate_funding, registry, SOURCE as INPUTS, SCHEMA as INPUT_SCHEMA
from estimation_calculation import calculate, formula, metamodel, META, SCHEMA as META_SCHEMA

SOURCE = 'source/estimations-core-retenues.yaml'
SCHEMA = 'source/schema-estimations-core-retenues.yaml'


def referenced_value(ref):
    value = read(ROOT / ref['path'])
    for key in ref['pointer'].split('.'):
        value = value[key]
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise ValueError('ERR_RETAINED_CORE_REFERENCE:' + str(ref))
    return value


@scoped_model
@model_memo
def validate(document=None):
    doc = deepcopy(document) if document is not None else read(ROOT / SOURCE)
    Draft202012Validator(read(ROOT / SCHEMA)).validate(doc)
    native = {r['id']: r['capacite_id'] for r in analysis()['blocs']}
    owners, identifiers = set(), set()
    for unit in doc['units']:
        assert unit['id'] not in identifiers, 'Duplicate family owner'
        identifiers.add(unit['id'])
        assert unit['total_jh'] > 0 and unit['months'] > 0, 'Empty retained estimate'
        assert len({r['id'] for r in unit['roles']}) == len(unit['roles']), 'Duplicate role'
        assert sum(r['jh'] for r in unit['roles']) == unit['total_jh'], 'Role effort reconciliation'
        for c in unit['capabilities']:
            assert native.get(c['id']) == c['native_id'], 'Unknown native capability'
            key = unit['stack'], c['id']
            assert key not in owners, 'Duplicate family capability funding'
            owners.add(key)
        validate_binding(unit)
        result = calculate(unit['calculation'])
        assert unit['method'] == result['method'], 'Retained method differs from calculation'
        assert unit['total_jh'] == result['total_jh'], 'Retained effort differs from decision rounding'
        assert unit['months'] == result['months'], 'Retained schedule differs from calculation'
        assert abs(unit['schedule']['unrounded_months'] - result['unrounded_months']) < 1e-9, 'Schedule drift'
        assert {r['id']:r['jh'] for r in unit['roles']} == result['roles'], 'Role allocation drift'
        assert unit['crosscheck']['jh'] == result['alignment']['functional']['jh'], 'Functional calculation drift'
        source = unit['provenance']
        assert hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest() == source['sha256'], 'Retained calculation evidence changed'
        for r in unit['roles']:
            referenced_value(r['rate_ref'])
        referenced_value(unit['schedule']['capacity_ref'])
    validate_funding(doc['units'])
    return doc


def dependencies():
    files = {SOURCE, SCHEMA, META, META_SCHEMA, 'tools/retained_core.py', 'tools/estimation_calculation.py', INPUTS, INPUT_SCHEMA, 'tools/estimation_inputs.py', 'tools/estimation_preparation.py'}
    files.update(registry()['proofs'])
    for unit in validate()['units']:
        files.add(unit['provenance']['path'])
        files.add(unit['schedule']['capacity_ref']['path'])
        files.update(r['rate_ref']['path'] for r in unit['roles'])
    return files


def value_units(slug, legacy_features, tooling):
    units = []
    for original in validate()['units']:
        if original['stack'] != slug:
            continue
        unit = deepcopy(original)
        computed = calculate(unit['calculation'])
        unit['schedule']['formula'] = next(r['expression'] for r in metamodel()['rules'] if r['id']==unit['schedule']['rule_ref'])
        unit['alignment'] = computed['alignment']
        unit['activities'] = computed['activities']
        unit['activity_source'] = computed['activity_source']
        for key in ('trace','funding','consolidation'): unit[key] = computed[key]
        # No active legacy charge can coexist with a retained family for its capabilities.
        members = {c['id'] for c in unit['capabilities']}
        for feature in legacy_features:
            if feature['feature'] in members:
                assert not any(sum(v.values()) for v in feature['plages_jh'].values()), 'Family overlaps legacy funding'
        for role in unit['roles']:
            role['rate_eur_jh'] = referenced_value(role['rate_ref'])
            role['labour_eur_ht'] = round(formula('role_price',JH=role['jh'],rate=role['rate_eur_jh']), 2)
        unit['labour_eur_ht'] = round(sum(r['labour_eur_ht'] for r in unit['roles']), 2)
        unit['tooling_eur_jh'] = tooling
        unit['tooling_eur_ht'] = round(unit['total_jh'] * tooling, 2)
        unit['cost_eur_ht'] = round(unit['labour_eur_ht'] + unit['tooling_eur_ht'], 2)
        unit['schedule']['productive_jh_per_month'] = referenced_value(unit['schedule']['capacity_ref'])
        unit['schedule']['average_fte'] = formula('average_team',JH=unit['total_jh'],months=unit['months'],capacity=unit['schedule']['productive_jh_per_month'])
        units.append(unit)
    return units


def coverage(units, capacity_ids):
    covered = {c['id'] for unit in units for c in unit['capabilities']}
    remaining = sorted(set(capacity_ids) - covered)
    assert covered <= set(capacity_ids), 'Coverage outside input scope'
    return dict(covered=len(covered), total=len(capacity_ids), remaining=len(remaining),
                covered_pct=round(formula('coverage',covered=len(covered),total=len(capacity_ids)),1) if capacity_ids else None,
                remaining_capabilities=remaining,
                status=('not_applicable' if not capacity_ids else 'fully_estimated' if not remaining else 'partially_estimated' if covered else 'pending_reestimation'))
