"""Generate browser parity cases from the current model, never historical budgets."""
import argparse
from copy import deepcopy
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from study_app import Study


def build_cases(study):
    before = deepcopy(study.parameters)
    option_specs = {row['key']: row for row in study.ui['parameters']['option']}
    common_specs = {row['key']: row for row in study.ui['parameters']['common']}
    make = [key for key, option in study.options.items() if option['mode'] == 'Make']
    buy = [key for key, option in study.options.items() if option['mode'] == 'Buy']
    if not make or not buy:
        raise ValueError('Pages validation requires both Make and Buy options')

    def changed(value, spec, direction=1):
        scale = spec['scale']
        step = max(spec['step'] * scale, scale / (10 ** study.ui['input_decimals']))
        minimum, maximum = spec['min'] * scale, spec['max'] * scale
        delta = max(step, abs(value) * 0.05)
        for sign in (direction, -direction):
            raw = value + sign * delta
            candidate = round(min(maximum, max(minimum, round(raw / step) * step)), 8)
            if minimum <= candidate <= maximum and candidate != value:
                return candidate
        raise ValueError(f"No sensitivity available for parameter {spec['key']}")

    scenarios = {'reference': deepcopy(before)}
    parameters = deepcopy(before)
    parameters['options'][make[0]]['build'] = changed(parameters['options'][make[0]]['build'], option_specs['build'])
    scenarios['make_build'] = parameters
    parameters = deepcopy(before)
    for slug in buy:
        parameters['options'][slug]['integration'] = changed(parameters['options'][slug]['integration'], option_specs['integration'])
    scenarios['buy_integration'] = parameters
    parameters = deepcopy(before)
    for slug in make + buy:
        for key in ('services_core', 'services_integration', 'services_grouped'):
            if key in parameters['options'][slug]:
                parameters['options'][slug][key] = changed(parameters['options'][slug][key], option_specs[key])
    scenarios['annual_services'] = parameters
    parameters = deepcopy(before)
    for slug in make + buy:
        key = 'build_mois' if slug in make else 'integration_mois'
        parameters['options'][slug][key] = changed(parameters['options'][slug][key], option_specs[key], -1)
    scenarios['calendar'] = parameters
    parameters = deepcopy(before)
    for key, value in parameters['common'].items():
        parameters['common'][key] = changed(value, common_specs[key])
    for slug in make + buy:
        for key in ('hebergement', 'ipaas', 'licences_complementaires'):
            parameters['options'][slug][key] = changed(parameters['options'][slug][key], option_specs[key])
    scenarios['context_and_means'] = parameters

    cases = {name: {'parameters': parameters, 'result': study.simulate(parameters)} for name, parameters in scenarios.items()}
    if len({json.dumps(case['parameters'], sort_keys=True) for case in cases.values()}) != 6:
        raise ValueError('The six validation scenarios must be distinct')
    if study.parameters != before or cases['reference']['result'] != study.baseline:
        raise ValueError('Validation generation modified the current reference')
    edge_cases = {}
    for name, budget in (('sap_below_counterpoint', 1_000_000), ('sap_zero_integration', 0)):
        parameters = deepcopy(before)
        parameters['options']['sap']['integration'] = budget
        edge_cases[name] = {'parameters': parameters, 'result': study.simulate(parameters)}
    return {'format': 1, 'contract': study.simulation_contract(), 'model_version': study.version,
            'provenance': 'Current Study inputs; generated validation data, not a historical economic constraint',
            'ui_case': 'make_build', 'cases': cases, 'edge_cases': edge_cases}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'tmp/pages-validation.json')
    args = parser.parse_args()
    result = build_cases(Study())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(json.dumps({'path': str(args.output), 'cases': len(result['cases']), 'contract': result['contract']}))


if __name__ == '__main__':
    main()
