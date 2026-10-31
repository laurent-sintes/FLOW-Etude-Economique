"""Prepare the same browser-only delivery locally and on Pages, with a verified cache."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from validation_changes import snapshot
from build_pages import normalize_base


def hashes(folder):
    return {p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob('*')) if p.is_file()}


def inputs(root):
    result={name:item['sha256'] for name,item in snapshot(root)['files'].items()}
    for name,digest in hashes(root/'app/public').items():
        if not name.startswith('exports/'):
            result['app/public/'+name]=digest
    return result


def build(output,base):
    from study_app import Study
    from export_business_model import export
    from build_pages import build_pages
    study=Study()
    # Vite reuses this validated export instead of loading the model again.
    export(study=study)
    node=shutil.which('node')
    if not node:
        bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
        if bundled.is_file():node=str(bundled)
    if not node:raise RuntimeError('Node.js is required to build the static application')
    subprocess.run([node,'node_modules/vite/bin/vite.js','build','--outDir',str(output),'--base',base],cwd=ROOT/'app',check=True)
    return build_pages(output,base,study=study)


def prepare(output=None,base='/',root=ROOT,builder=None,force=False):
    output=Path(output or root/'app/dist').resolve()
    root=root.resolve()
    if output not in {(root/'app/dist').resolve(),(root/'app/dist-pages').resolve()}:
        raise ValueError('Static application output must be app/dist or app/dist-pages')
    base=normalize_base(base)
    directory=root/'tmp/static-app'
    directory.mkdir(parents=True,exist_ok=True)
    state=directory/(hashlib.sha256(str(output).encode()).hexdigest()[:16]+'.json')
    before=inputs(root)
    try:
        cached=json.loads(state.read_text(encoding='utf-8'))
        if not force and cached['format']==1 and cached['base']==base and cached['inputs']==before and cached['outputs']==hashes(output):
            manifest=json.loads((output/'site-manifest.json').read_text(encoding='utf-8'))
            return dict(cached=True,output=str(output),revision=manifest['server_revision'])
    except (OSError,ValueError,KeyError):pass
    manifest=(builder or build)(output,base)
    if inputs(root)!=before:raise ValueError('Sources changed during static application preparation')
    record=dict(format=1,base=base,inputs=before,outputs=hashes(output))
    pending=state.with_suffix('.pending')
    pending.write_text(json.dumps(record,ensure_ascii=False),encoding='utf-8')
    pending.replace(state)
    return dict(cached=False,output=str(output),revision=manifest['server_revision'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'app/dist')
    parser.add_argument('--base',default='/')
    parser.add_argument('--force',action='store_true')
    args=parser.parse_args()
    print(json.dumps(prepare(args.output,args.base,force=args.force),ensure_ascii=False))


if __name__=='__main__':main()
