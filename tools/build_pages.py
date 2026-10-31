"""Build a coherent GitHub Pages delivery from the current study and compiled UI."""
import argparse
from copy import deepcopy
import gzip
import hashlib
import html
import io
import json
import os
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import quote, urlsplit
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from market_reading import build_market_reading
from study_app import Study
from study_snapshot import candidate, encode, ENGINE_FILES
from validate_stacks import ROOT
from export_business_model import export as export_business_model, ASSET as MODEL_DOWNLOAD_ASSET


PYODIDE_VERSION = '314.0.7'
PYODIDE_BASE = f'https://cdn.jsdelivr.net/pyodide/v{PYODIDE_VERSION}/full/'
GENERATED = ('data', 'documents', 'site-manifest.json', '.nojekyll')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def deployment_commit():
    value = os.environ.get('FLOW_DEPLOYMENT_COMMIT', '')
    if value and not re.fullmatch(r'[0-9a-fA-F]{40}|[0-9a-fA-F]{64}', value):
        raise ValueError('Invalid deployment commit')
    return value.lower() or None


def normalize_base(value):
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or '\\' in value:
        raise ValueError('Pages base must be an absolute URL path')
    if not value.startswith('/') or any(part in ('.', '..') for part in value.split('/')):
        raise ValueError('Pages base must stay within one site path')
    return value.rstrip('/') + '/'


def engine_archive():
    """Keep original bytes so the loaded Study verifies the canonical engine hash."""
    folder = ROOT / 'tools'
    names = sorted(path.name for path in folder.glob('*.py') if not path.name.startswith('test_'))
    if not set(ENGINE_FILES) | {'pages_runtime.py', 'document_excerpt.py'} <= set(names):
        raise ValueError('Incomplete browser engine')
    stream = io.BytesIO()
    with ZipFile(stream, 'w', compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name in names:
            info = ZipInfo('tools/' + name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, (folder / name).read_bytes())
    return stream.getvalue()


def _clean_generated(output):
    # Only our four declared build products, inside the checked output directory.
    for name in GENERATED:
        target = (output / name).resolve()
        if not target.is_relative_to(output) or target == output:
            raise ValueError('Unsafe generated output path')
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()


def build_pages(output, base='/', study=None):
    deployed_commit = deployment_commit()
    output = Path(output).resolve()
    allowed = {(ROOT / 'app' / name).resolve() for name in ('dist', 'dist-pages')}
    scratch = (ROOT / 'tmp').resolve()
    if output not in allowed and not (output.is_relative_to(scratch) and output != scratch):
        raise ValueError('Pages output must be app/dist-pages, app/dist or a build directory under tmp')
    index = output / 'index.html'
    if not index.is_file():
        raise ValueError('Build the Vite interface before exporting Pages')
    base = normalize_base(base)
    study = study or Study()
    bundle = candidate(study)
    export_business_model(output / MODEL_DOWNLOAD_ASSET, study=study)
    archive_raw = engine_archive()
    model_raw = gzip.compress(encode(bundle), compresslevel=9, mtime=0)

    # A prior injected marker must not become an input to the next delivery.
    index_text = index.read_text(encoding='utf-8')
    index_text = re.sub(r'<script id="app-config" type="application/json">.*?</script>', '', index_text, flags=re.S)
    asset_hashes = {}
    for path in sorted(output.rglob('*')):
        if not path.is_file() or path.relative_to(output).parts[0] in GENERATED:
            continue
        relative = path.relative_to(output).as_posix()
        raw = index_text.encode('utf-8') if path == index else path.read_bytes()
        asset_hashes[relative] = sha(raw)
    revision = sha(encode(dict(format=1, model=sha(model_raw), base=base, assets=asset_hashes,
                               engine=sha(archive_raw))))

    # Read every allowed document before replacing generated output. No folder scan
    # may introduce sources or proofs that the loaded study did not declare.
    document_bytes = {}
    for source, record in bundle['payload']['documents'].items():
        raw = study.document_bytes(source)
        if sha(raw) != record['sha256']:
            raise ValueError('Document changed since the study was loaded: ' + source)
        document_bytes[source] = raw

    bootstrap = deepcopy(study.bootstrap(essential=True))
    bootstrap['server_revision'] = revision
    bootstrap['edition'] = dict(mode='current', date=study.data['scenario']['date'])
    ui = bootstrap['ui']
    for key, value in ui.get('brand_assets', {}).items():
        if isinstance(value, str) and value.startswith('/'):
            ui['brand_assets'][key] = base + value.lstrip('/')

    market = study.content['market']['reperes_build_core']
    capabilities = {}
    for row in study.content['business_map']['rows']:
        proof = dict(title=row['capacite']['nom'], text=row['capacite']['definition'] + ' ' + row['frontiere'],
                     source=study.content['business_map']['source']['path'])
        for identifier in (row['id'], row['capacite_id']):
            if identifier in capabilities and capabilities[identifier] != proof:
                raise ValueError('Ambiguous capability identifier: ' + identifier)
            capabilities[identifier] = proof
    values = {
        'bootstrap': bootstrap,
        'ui': ui,
        'market-build': {key: deepcopy(market[key]) for key in ('etude_oss', 'cadre_comparaison', 'fiches_produit', 'candidats_a_etudier')},
        'market-references': build_market_reading(study.content['market']),
        'economic-evaluations': deepcopy(study.content['economic_evaluations']),
        'capabilities': capabilities,
    }
    _clean_generated(output)
    data_path = 'data/' + revision
    (output / data_path).mkdir(parents=True)
    for name, value in values.items():
        (output / data_path / f'{name}.json').write_bytes(encode(value))
    (output / data_path / 'engine.zip').write_bytes(archive_raw)
    (output / data_path / 'model.json.gz').write_bytes(model_raw)

    documents = {}
    for source, raw in document_bytes.items():
        name = Path(source).name
        digest = sha(raw)
        destination = output / 'documents' / digest / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        url = '/'.join(quote(part, safe='') for part in destination.relative_to(output).parts)
        documents[source] = dict(url=url, sha256=digest)
    manifest = dict(format=1, id=study.ui['id'], model_version=study.version,
                    simulation_contract=study.simulation_contract(), server_revision=revision,
                    base=base, bootstrap=data_path + '/bootstrap.json',
                    routes={
                        '/api/ui': data_path + '/ui.json', '/api/market-build': data_path + '/market-build.json',
                        '/api/market-references': data_path + '/market-references.json',
                        '/api/economic-evaluations': data_path + '/economic-evaluations.json',
                        '/api/capability': data_path + '/capabilities.json',
                    }, documents=documents,
                    python=dict(archive=data_path + '/engine.zip', model=data_path + '/model.json.gz',
                                pyodide=PYODIDE_BASE, archive_sha256=sha(archive_raw), model_sha256=sha(model_raw)))
    if deployed_commit:
        manifest['deployment_commit'] = deployed_commit
    (output / 'site-manifest.json').write_bytes(encode(manifest))
    (output / '.nojekyll').write_bytes(b'')
    initial = dict(id=ui['id'], reload_storage_key=ui['reload_storage_key'],
                   labels={key: ui['labels'][key] for key in ('loading', 'retry')},
                   errors={key: ui['errors'][key] for key in ('network', 'render', 'reset_session')},
                   server_revision=revision, static_site=dict(manifest='site-manifest.json'))
    index_text = re.sub(r'<title>.*?</title>', '<title>' + html.escape(ui['document_title']) + '</title>', index_text, flags=re.S)
    config = encode(initial).decode('utf-8').replace('<', '\\u003c')
    index.write_text(index_text.replace('</head>', '<script id="app-config" type="application/json">' + config + '</script></head>'), encoding='utf-8')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=str(ROOT / 'app' / 'dist-pages'))
    parser.add_argument('--base', default='/')
    args = parser.parse_args()
    manifest = build_pages(args.output, args.base)
    output = Path(args.output)
    print(json.dumps(dict(output=str(output.resolve()), base=manifest['base'],
                          documents=len(manifest['documents']), version=manifest['model_version'],
                          revision=manifest['server_revision'],
                          bytes=sum(path.stat().st_size for path in output.rglob('*') if path.is_file())), ensure_ascii=False))


if __name__ == '__main__':
    main()
