"""Validate the editable YAML model, with identical rules for Make and Buy."""
from pathlib import Path
import sys
import yaml
from jsonschema import Draft202012Validator
from model_context import CURRENT

ROOT = Path(__file__).resolve().parents[1]

class UniqueKeyLoader(getattr(yaml, 'CSafeLoader', yaml.SafeLoader)):
    """Reject duplicate keys instead of silently replacing values."""

def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f'Duplicate YAML key: {key}')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result

UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)

def read(path):
    load = lambda text: yaml.load(text, Loader=UniqueKeyLoader)
    session = CURRENT.get()
    return session.read(path, load) if session is not None else load(path.read_text(encoding='utf-8-sig'))

def validate():
    schema = read(ROOT/'source/schema-stack.yaml')
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    paths = sorted((ROOT/'source/stacks').glob('*.yaml'))
    expected = {'microsoft-buy','sap-buy','java-spring-make','rust-make','dotnet-make'}
    found = set()
    counts = []
    for path in paths:
        model = read(path)
        validator.validate(model)
        if model['id'] in found:
            raise ValueError(f'Duplicate stack: {model["id"]}')
        found.add(model['id'])
        assert model['id'].endswith('-'+model['strategie']), path
        source_ids = set(model['sources'])
        ids = [e['id'] for e in model['elements']]
        assert len(set(ids)) == len(ids), f'Duplicate element in {path}'
        graph = {}
        used_sources = set()
        for element in model['elements']:
            assert set(element['sources']) <= source_ids, element['id']
            used_sources.update(element['sources'])
            cost = element['tarification']
            assert set(cost['inclus_dans']) <= set(ids), element['id']
            assert element['id'] not in cost['inclus_dans'], element['id']
            assert bool(cost['inclus_dans']) == (cost['regime']=='inclus'), element['id']
            if cost['regime']=='sans_redevance':
                assert element['licence'] and 'Propriétaire' not in element['licence'], element['id']
            graph[element['id']] = cost['inclus_dans']
        def visit(node, trail):
            assert node not in trail, f'Inclusion cycle: {trail} -> {node}'
            for parent in graph[node]: visit(parent, trail+[node])
        for node in graph: visit(node, [])
        rates = model['interventions']['tarifs']
        for rate in rates.values():
            assert rate['bas'] <= rate['reference'] <= rate['haut'], path
            assert set(rate['sources']) <= source_ids, path
            used_sources.update(rate['sources'])
        for activity in model['interventions']['activites'].values():
            assert activity['tarif'] in rates, path
        assert set(model['interventions']['repere_esn']['sources']) <= source_ids, path
        used_sources.update(model['interventions']['repere_esn']['sources'])
        for source in model['sources'].values():
            ref = source['reference']
            if not ref.startswith(('https://','http://')):
                assert (ROOT/ref).is_file(), f'Missing source: {ref}'
        counts.append((model['id'],len(ids),rates['expert']['reference']))
    assert found == expected, f'Stacks missing or unexpected: {found ^ expected}'
    print('VALID: 5 stacks, one schema, source references and inclusions, comparable rate structure.')
    for stack, count, rate in counts:
        print(f'{stack}: {count} elements, expert reference {rate} EUR HT/JH')

def validate_inflation():
    """Check the shared inflation model and its links to all five stacks."""
    schema_path = ROOT/'source/schema-inflation.yaml'
    schema = read(schema_path)
    Draft202012Validator.check_schema(schema)
    model = read(ROOT/'source/inflation.yaml')
    Draft202012Validator(schema).validate(model)
    expected = {p.relative_to(ROOT).as_posix() for p in (ROOT/'source/stacks').glob('*.yaml')}
    dependencies = model['dependances']
    assert set(dependencies['stacks']) == expected, 'Inflation must reference all five stacks'
    assert (ROOT/dependencies['schema']).is_file(), 'Missing inflation schema'
    for path in dependencies['stacks']:
        stack = read(ROOT/path)
        assert stack['interventions']['marche'] == 'France', path
        assert set(stack['interventions']['activites']) == set(model['rattachement']['prestations']), path
    source_ids = set(model['sources'])
    for category, value in model['categories'].items():
        assert set(value['sources']) <= source_ids, f'Unknown source: {category}'
        rates = value['taux_annuel_pct']
        assert rates['bas'] <= rates['central'] <= rates['haut'], category
        factors = [(1 + rates['central']/100)**n for n in model['horizons_analyse_ans']]
        print(f'Inflation {category}: central {rates["central"]}%/year; price factors at 10/15 years: {factors[0]:.3f}/{factors[1]:.3f}')
    print('VALID: inflation France, three categories, source references and five stack dependencies.')


if __name__ == '__main__':
    validate()
    validate_inflation()
