"""One explicit human model revision, independent from calculation fingerprints."""
import argparse
from datetime import date
import os
from pathlib import Path
import tempfile
import yaml
from validate_stacks import ROOT, read

SOURCE = 'source/version-modele.yaml'

def validate_revision(document):
    if not isinstance(document, dict) or set(document) != {'format_version', 'date', 'number'} or type(document['format_version']) is not int or document['format_version'] != 1:
        raise ValueError('ERR_MODEL_REVISION_FIELDS')
    number = document['number']
    if isinstance(number, bool) or not isinstance(number, int) or number < 1:
        raise ValueError('ERR_MODEL_REVISION_NUMBER')
    value = document['date']
    try:
        if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
            raise ValueError('date')
    except (ValueError, TypeError) as error:
        raise ValueError('ERR_MODEL_REVISION_DATE') from error
    return dict(date=value, number=number)

def load_revision():
    return validate_revision(read(ROOT / SOURCE))

def next_revision(document, on):
    current = validate_revision(document)
    candidate = dict(format_version=1, date=on, number=current['number']+1)
    validate_revision(candidate)
    if on < current['date']:
        raise ValueError('ERR_MODEL_REVISION_BACKDATE')
    return candidate

def bump(path=ROOT / SOURCE, on=None):
    path = Path(path)
    document = yaml.safe_load(path.read_text(encoding='utf-8'))
    updated = next_revision(document, on or date.today().isoformat())
    raw = yaml.safe_dump(updated, allow_unicode=True, sort_keys=False).encode('utf-8')
    fd, temporary = tempfile.mkstemp(prefix='.model-revision-', suffix='.yaml', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return validate_revision(updated)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['show', 'bump'])
    parser.add_argument('--date', dest='on')
    args = parser.parse_args()
    import json
    print(json.dumps(bump(on=args.on) if args.command == 'bump' else load_revision()))

if __name__ == '__main__':
    main()
