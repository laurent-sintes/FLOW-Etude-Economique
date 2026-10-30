"""Compose the one downloadable business model from validated, active inputs only."""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import yaml
from model_context import model_session
from study_app import Study
from validate_stacks import ROOT, read

METAMODEL = 'source/fondamentaux.yaml'
ASSET = 'exports/flow-modele-metier.yaml'
DEFAULT_OUTPUT = ROOT / 'tmp/model-download' / Path(ASSET).name


def compose(documents, digests, root=ROOT):
    """Use the actual dependency closure, without scanning retired source files."""
    model, schemas, provenance, evidence = {}, {}, {}, {}
    metamodel = None
    for path in sorted(documents, key=lambda p: p.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.suffix not in ('.yaml', '.yml', '.json', '.py') or relative.split('/')[0] not in ('source', 'sources', 'audits'):
            continue
        provenance[relative] = digests[path]
        value = deepcopy(documents[path])
        if relative == METAMODEL:
            metamodel = value
        elif relative.startswith('audits/'):
            evidence[relative] = value
        elif path.name.startswith('schema-'):
            schemas[relative] = value
        else:
            model[relative] = value
    if metamodel is None or not model:
        raise ValueError('Missing business model or metamodel')
    fingerprint = hashlib.sha256(json.dumps(provenance, sort_keys=True).encode()).hexdigest()
    return dict(format='flow-business-model', format_version=2,
        description='Modèle métier courant et métamodèle. Export généré, non éditable. Les chemins sont ceux des sources d’origine.',
        scope='Instances actives dans model ; pièces historiques utilisées par les calculs dans evidence, distinctes des décisions adoptées. La chaîne des mesures, paramètres, dépendances et empreintes est incluse. Les dépôts OSS complets et PDF externes restent référencés ; les scénarios personnels ne sont pas inclus.',
        source_fingerprint=fingerprint, sources=provenance,
        metamodel=metamodel, model=model, schemas=schemas, evidence=evidence)


def encode(document):
    return yaml.dump(document, Dumper=getattr(yaml, 'CSafeDumper', yaml.SafeDumper), allow_unicode=True, sort_keys=False, width=110).encode('utf-8')


def write_if_changed(path, raw):
    """Content comparison also repairs missing/corrupt exports; atomic replacement."""
    path = Path(path)
    if path.is_file() and path.read_bytes() == raw:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.model-', suffix='.yaml', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return True


def hashes(names):
    result = {}
    for name in sorted(names):
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise ValueError('Missing or invalid export dependency: ' + name)
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def generator_signature():
    # Include discovery logic as well as currently loaded data. A new engine module
    # invalidates the cache even if the previous dependency closure did not know it.
    import importlib.metadata
    names = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'tools').glob('*.py') if not p.name.startswith('test_')}
    names.add('tools/requirements-model.txt')
    return dict(files=hashes(names), python=sys.version, yaml=yaml.__version__,
                jsonschema=importlib.metadata.version('jsonschema'))


def cached_export(output, signature, study=None):
    cache = Path(str(output) + '.cache.json')
    try:
        record = json.loads(cache.read_text(encoding='utf-8'))
        if record['version'] != 1 or record['generator'] != signature:
            return None
        dependencies = record['dependencies']
        if hashes(dependencies) != dependencies:
            return None
        if study is not None:
            for path, expected in study.source_digests.items():
                name = Path(path).relative_to(ROOT).as_posix()
                if dependencies.get(name) != expected:
                    raise ValueError('Source changed since application loading: ' + name)
        raw = Path(output).read_bytes()
        if hashlib.sha256(raw).hexdigest() != record['sha256'] or len(raw) != record['bytes']:
            return None
        # As with SourceSnapshot.verify, reject a change during the cache check.
        if hashes(dependencies) != dependencies:
            return None
        return dict(path=str(output), changed=False, cache_hit=True,
                    sha256=record['sha256'], bytes=len(raw), sources=record['sources'])
    except (OSError, KeyError, TypeError, json.JSONDecodeError):
        return None


def export(output=DEFAULT_OUTPUT, study=None):
    output = Path(output)
    signature = generator_signature()
    cached = cached_export(output, signature, study)
    if cached is not None:
        return cached
    # Hold one snapshot through validation and serialization; reject concurrent edits.
    with model_session() as snapshot:
        if study is None:
            loaded = Study()
        else:
            loaded = study
            for name, expected in study.source_digests.items():
                path = Path(name)
                if path.suffix == '.py':
                    snapshot.read(path, lambda text: text)
                else:
                    read(path)
                if snapshot.digests[path.resolve()] != expected:
                    raise ValueError('Source changed since application loading: ' + name)
        document = compose(snapshot.documents, snapshot.digests)
        raw = encode(document)
        names = {p.relative_to(ROOT).as_posix() for p in snapshot.digests}
        names.update(loaded.files)
        dependencies = hashes(names)
        for path, expected in snapshot.digests.items():
            if dependencies[path.relative_to(ROOT).as_posix()] != expected:
                raise ValueError('Source changed during export: ' + str(path))
    changed = write_if_changed(output, raw)
    result = dict(path=str(output), changed=changed, cache_hit=False,
                  sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw), sources=len(document['sources']))
    if hashes(dependencies) != dependencies or generator_signature() != signature:
        raise ValueError('Dependencies changed during export')
    record = dict(version=1, generator=signature, dependencies=dependencies,
                  **{key: result[key] for key in ('sha256','bytes','sources')})
    write_if_changed(Path(str(output)+'.cache.json'), json.dumps(record,sort_keys=True).encode())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(export(args.output)))


if __name__ == '__main__':
    main()
