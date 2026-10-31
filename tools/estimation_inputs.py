"""Typed calculation contracts, immutable evidence closure and funding ownership."""
from copy import deepcopy
import hashlib
import json
from pathlib import PurePosixPath
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read
from model_context import CURRENT, model_memo, scoped_model
from capability_catalog import analysis, native

SOURCE = 'source/calculs-estimation-core.yaml'
SCHEMA = 'source/schema-calculs-estimation-core.yaml'


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def proof_path(name):
    require(isinstance(name, str) and '\\' not in name, 'Invalid evidence path')
    p = PurePosixPath(name)
    require(not p.is_absolute() and '..' not in p.parts and p.parts[0] == 'audits', 'Evidence outside audit registry')
    return ROOT / name


def historical_dependencies(path, document):
    """Only declared calculation inputs, not unrelated historical source snapshots."""
    if not isinstance(document, dict):
        return {}
    result = {}
    for name, sha in document.get('input_hashes', {}).items():
        name = name.replace('\\', '/')
        if name == 'iteration08':
            name = 'audits/2026-10-29-experimentation-estimation/iteration-08-cosmic.json'
        elif not name.startswith('audits/'):
            name = (ROOT / path).parent.joinpath(name).resolve().relative_to(ROOT).as_posix()
        result[name] = sha
    for key, filename in (('inputs_sha256', 'inputs.json'), ('measurements_sha256', 'measurements.json')):
        if key in document:
            result[(PurePosixPath(path).parent / filename).as_posix()] = document[key]
    return result


@model_memo
def registry(document=None):
    doc = deepcopy(document) if document is not None else read(ROOT / SOURCE)
    Draft202012Validator(read(ROOT / SCHEMA)).validate(doc)
    for key in ('calculations', 'mechanisms'):
        ids = [x['id'] for x in doc[key]]
        require(len(ids) == len(set(ids)), 'Duplicate ' + key)
    mechanisms = {m['id']: m for m in doc['mechanisms']}
    owners, bases = {}, set()
    for m in mechanisms.values():
        basis = (m['stack'], digest(m['basis']))
        require(basis not in bases, 'Same work registered under multiple mechanism identifiers')
        bases.add(basis)
    for c in doc['calculations']:
        claims = c['funding_claims']
        require(len({x['mechanism'] for x in claims}) == len(claims), 'Duplicate funding claim')
        for claim in claims:
            require(claim['mechanism'] in mechanisms, 'Unknown mechanism')
            m = mechanisms[claim['mechanism']]
            require(m['stack'] == c['stack'], 'Mechanism stack mismatch')
            if claim['mode'] == 'funded':
                require(m['funding_owner'] == c['unit_id'], 'Shared mechanism already owned by another unit')
                require(m['id'] not in owners, 'Duplicate mechanism funding')
                owners[m['id']] = c['id']
            else:
                require(m['funding_owner'] != c['unit_id'], 'Owner cannot consume its own funding')
        require(set(c['inputs'].values()) <= set(doc['proofs']), 'Unregistered calculation input')
        for row in c['comparison']['scope_rows']:
            require(set(row['evidence']) <= set(doc['proofs']), 'Unregistered comparison evidence')
    require(set(owners) == set(mechanisms), 'Mechanism without a unique funding calculation')
    for path, proof in doc['proofs'].items():
        proof_path(path)
        for dep in proof['dependencies']:
            require(dep['path'] in doc['proofs'] and doc['proofs'][dep['path']]['sha256'] == dep['sha256'], 'Broken evidence dependency')
    require(doc['consolidation']['mode'] == 'sum_of_adopted_decisions'
            and not doc['consolidation']['integrated_core_estimate']
            and doc['consolidation']['schedule_aggregation'] == 'none', 'Integrated consolidation is not implemented')
    return doc


def contract(binding, document=None):
    require(set(binding) == {'id'}, 'A retained decision must reference a calculation identifier')
    doc = registry(document)
    matches = [c for c in doc['calculations'] if c['id'] == binding['id']]
    require(len(matches) == 1, 'Unknown calculation')
    return matches[0], doc


@scoped_model
def load_proofs(doc):
    documents, visiting = {}, set()
    def visit(name):
        require(name not in visiting, 'Cyclic evidence dependency')
        if name in documents:
            return
        visiting.add(name)
        proof = doc['proofs'][name]
        path = proof_path(name)
        if path.suffix == '.py':
            value = CURRENT.get().read(path, lambda text: text)
        else:
            value = read(path)
        require(CURRENT.get().digests[path.resolve()] == proof['sha256'], 'Calculation input evidence changed: ' + name)
        actual = historical_dependencies(name, value)
        declared = {d['path']: d['sha256'] for d in proof['dependencies']}
        require(actual == declared, 'Evidence dependency declaration differs: ' + name)
        for dependency in declared:
            visit(dependency)
        documents[name] = value
        visiting.remove(name)
    for c in doc['calculations']:
        for name in c['inputs'].values():
            visit(name)
    require(set(documents) == set(doc['proofs']), 'Unreachable evidence in active registry')
    return documents



@scoped_model
def _frozen_calculation_proofs(doc):
    """Private, read-only evidence shared only by preparations in this snapshot.

    Public load_proofs still returns isolated documents and validates explicit inputs.
    Preparations copy any inputs they mutate; calculate returns independent outputs.
    """
    session = CURRENT.get()
    key = ('validated_estimation_proofs', digest(doc))
    if key not in session.memo:
        session.memo[key] = load_proofs(doc)
    return session.memo[key]


def validate_binding(unit, document=None):
    c, doc = contract(unit['calculation'], document)
    require((unit['id'], unit['stack'], unit['capabilities']) ==
            (c['unit_id'], c['stack'], c['scope']['capabilities']), 'Calculation does not belong to this unit, stack or capability scope')
    require(c['scope']['native_source'] == read(ROOT / 'source/referentiel-capacites.yaml'), 'Native scope version changed')
    selected = [b for b in analysis()['blocs'] if b['id'] in {x['id'] for x in unit['capabilities']}]
    nodes = {n['id']: n for n in native()['nodes']}
    scope = c['scope']
    professional=scope.get('professional_functions',[])
    require(unit.get('professional_functions',[])==professional,'Professional function binding mismatch')
    if professional:
        known={f['id'] for f in read(ROOT/'source/fonctions-produit-core.yaml')['functions']}
        require(set(professional)<=known and len(professional)==len(set(professional)),'Unknown professional function')
    if scope['level']=='professional_function_group':
        require(not unit['capabilities'] and bool(professional) and c['recipe']=='professional_components_v1','Professional group cannot invent native capabilities')
    else:
        require(scope['native_id'] in nodes and nodes[scope['native_id']]['kind'] == scope['level'], 'Invalid evaluation hierarchy')
        require(all(scope['native_id'] in b['chemin'] for b in selected), 'Capabilities outside evaluation hierarchy')
    require(digest(selected) == c['scope']['analysis_sha256'], 'Study scope changed without rebinding calculation')
    require(digest({k: unit[k] for k in ('capabilities', 'includes', 'excludes')+ (('professional_functions',) if 'professional_functions' in unit else ())}) == c['scope']['decision_scope_sha256'], 'Decision activity scope changed')
    return c


def validate_funding(units, document=None):
    doc = registry(document)
    adopted = {u['id'] for u in units}
    for unit in units:
        c = validate_binding(unit, doc)
        for claim in c['funding_claims']:
            m = next(m for m in doc['mechanisms'] if m['id'] == claim['mechanism'])
            require(m['funding_owner'] in adopted, 'Consumed mechanism has no adopted funding owner')
    return doc['consolidation']
