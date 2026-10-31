"""Conservative semantic selection against a successful complete validation."""
import hashlib
import json
from pathlib import Path
from validate_stacks import UniqueKeyLoader
import yaml

EDITORIAL_KEYS = {'label', 'title', 'subtitle', 'description', 'note', 'caption', 'heading', 'text', 'body', 'explanation'}
PROTECTED = {'estimation_model', 'rules', 'domains', 'variables', 'expression', 'implementations', 'objects', 'relations', 'schema', 'properties', '$defs', 'parameters'}


def identical(before, after):
    if type(before) is not type(after):
        return False
    if isinstance(before, dict):
        return before.keys() == after.keys() and all(identical(before[k], after[k]) for k in before)
    if isinstance(before, list):
        return len(before) == len(after) and all(identical(a,b) for a,b in zip(before,after))
    return before == after


def editorial_change(before, after, path=()):
    if identical(before, after):
        return True
    if any(str(key) in PROTECTED for key in path):
        return False
    if isinstance(before, dict) and isinstance(after, dict) and before.keys() == after.keys():
        return all(editorial_change(before[key], after[key], path + (key,)) for key in before)
    if isinstance(before, list) and isinstance(after, list) and len(before) == len(after):
        return all(editorial_change(a, b, path + (i,)) for i, (a, b) in enumerate(zip(before, after)))
    return bool(path and path[-1] in EDITORIAL_KEYS and isinstance(before, str) and isinstance(after, str))


def strings(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from strings(key)
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, str):
        yield value


def snapshot(root):
    files = set()
    for directory in ('source', 'sources', 'config', 'tools', 'app/src', 'app/scripts', 'skills', '.github'):
        files.update(p for p in (root / directory).rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix not in ('.pyc', '.log'))
    files.update(p for p in root.iterdir() if p.is_file())
    files.update(p for p in (root / 'app').iterdir() if p.is_file())
    result = {}
    pending = list(files)
    while pending:
        path = pending.pop()
        name = path.relative_to(root).as_posix()
        if name in result:
            continue
        raw = path.read_bytes()
        item = {'sha256': hashlib.sha256(raw).hexdigest()}
        if path.suffix in ('.yaml', '.yml') and name.startswith(('source/', 'config/')):
            value = yaml.load(raw.decode('utf-8-sig'), Loader=UniqueKeyLoader)
            if name.startswith(('source/', 'config/')) and 'schema' not in path.name:
                item['document'] = value
            # Follow explicit evidence paths, including archived calculation proofs.
            for text in strings(value):
                if len(text) < 240 and text.startswith(('source/', 'sources/', 'audits/', 'config/', 'tools/')):
                    reference = root / text
                    if reference.is_file():
                        pending.append(reference)
        result[name] = item
    return {'format': 1, 'files': result}


def classify(previous, current):
    before, after = previous['files'], current['files']
    changes = []
    full = False
    for name in sorted(before.keys() | after.keys()):
        old, new = before.get(name), after.get(name)
        if old is not None and new is not None and old['sha256'] == new['sha256']:
            continue
        if old is None or new is None:
            reason = 'added_or_deleted'
        elif Path(name).suffix in ('.css','.ts','.tsx') and name.startswith('app/src/'):
            reason = 'presentation_client'
        elif 'document' in old and 'document' in new and editorial_change(old['document'], new['document']):
            reason = 'editorial_fields_only'
        else:
            reason = 'business_engine_schema_or_unknown'
        full |= reason not in ('presentation_client', 'editorial_fields_only')
        changes.append({'path': name, 'reason': reason})
    return {'mode': 'full' if full else 'presentation', 'changes': changes,
            'policy': 'Unknown, structural, numeric, metamodel and engine changes require the full suite. Presentation checks include a real browser and are not a full certification.'}


def plan(root):
    manifest = root / 'tmp/validation-full-manifest.json'
    if not manifest.exists():
        return {'mode': 'full', 'reason': 'no_successful_full_baseline'}
    try:
        previous = json.loads(manifest.read_text(encoding='utf-8'))
        report = json.loads(Path(previous['report']).read_text(encoding='utf-8'))
        if previous.get('format') != 1 or report.get('status') != 'passed' or report.get('mode') != 'full':
            raise ValueError('Invalid complete baseline')
        return classify(previous, snapshot(root))
    except (ValueError, KeyError, OSError):
        return {'mode': 'full', 'reason': 'baseline_or_sources_invalid'}
