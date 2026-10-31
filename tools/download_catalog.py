"""Validated catalog of existing downloads, separate from personal scenario data."""
from copy import deepcopy
import hashlib
from pathlib import PurePosixPath
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read
from model_context import CURRENT

SOURCE = 'source/telechargements.yaml'
SCHEMA = 'source/schema-telechargements.yaml'

def build_download_catalog(ui, originals, allowed_files):
    document = read(ROOT / SOURCE)
    Draft202012Validator(read(ROOT / SCHEMA)).validate(document)
    return compile_catalog(document, ui['documents'], originals['items'], allowed_files)

def compile_catalog(document, documents, originals, allowed_files):
    def require(value, message):
        if not value:
            raise ValueError('ERR_DOWNLOAD_CATALOG:' + message)
    package = document['model_package']
    require(package == dict(asset='exports/flow-modele-metier.yaml', metadata_asset='exports/flow-modele-metier.json', filename='flow-modele-metier.yaml'), 'model package contract')
    index = {item['path']: item for item in documents}
    require(len(index) == len(documents), 'duplicate document')
    seen = set()
    def asset(path):
        path = path.split('#')[0]
        require(path in allowed_files and path not in seen, 'unknown or duplicate download: ' + path)
        suffix = PurePosixPath(path).suffix.lower()
        require(suffix in ('.pdf', '.xlsx', '.md'), 'individual model source is not downloadable')
        file = (ROOT / path).resolve()
        require(file.is_relative_to(ROOT.resolve()) and file.is_file(), 'invalid path')
        raw = file.read_bytes()
        # The source snapshot verifies text documents through the complete build.
        snapshot = CURRENT.get()
        if snapshot is not None and suffix == '.md':
            snapshot.read(file, lambda text: text)
        seen.add(path)
        return dict(path=path, filename=file.name, format=suffix[1:].upper(), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    original_rows = []
    for original in sorted(originals, key=lambda item: (item['date']['value'] is None, item['date']['value'] or '', item['id'])):
        original_rows.append(dict(id=original['id'], title=original['title'], description=original['scope'], author=original['author'], date=deepcopy(original['date']), **asset(original['path'])))
    reading_rows = []
    for path in document['reading_document_refs']:
        require(path in index, 'missing reading document')
        require(PurePosixPath(path).suffix.lower() == '.md', 'reading document must be a declared text document')
        row = index[path]
        reading_rows.append(dict(title=row['title'], description=row['description'], date=None, **asset(path)))
    return dict(reading=deepcopy(document['reading']), model_package=deepcopy(package), originals=original_rows, documents=reading_rows, personal_route=document['personal_route'], source_ref=SOURCE)
