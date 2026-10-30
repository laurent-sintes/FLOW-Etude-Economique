"""Local-only HTTP entry point. No writes to source data and no remote dependencies."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import html
import mimetypes
import os
import hashlib
import uuid
import gzip
from functools import lru_cache
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs, urlsplit
from study_app import Study, ScenarioError
from validate_stacks import ROOT
from document_excerpt import document_excerpt
from study_snapshot import candidate, encode, ENGINE_FILES
from market_reading import build_market_reading


def load_current_study():
    """Load current sources once and freeze their documentary evidence in memory."""
    source = Study()
    study = Study.from_release(candidate(source))
    study.edition = dict(source.edition)
    study.source_digests = dict(source.source_digests)
    return study


def make_handler(study, static_root=None):
    instance = uuid.uuid4().hex
    # Pin the client build to the loaded model. Rebuilding dist while this
    # process is running must not mix old bootstrap data with new JavaScript.
    dist = (Path(static_root) if static_root is not None else ROOT/'app/dist').resolve()
    static_files = {file.relative_to(dist).as_posix():file.read_bytes()
                    for file in dist.rglob('*') if file.is_file()}
    if 'index.html' not in static_files: raise FileNotFoundError(dist/'index.html')
    client_build_sha256=hashlib.sha256(static_files['index.html']).hexdigest()
    source_paths = {Path(path) for path in getattr(study,'source_digests',{})}
    source_paths.update(ROOT/'tools'/name for name in ENGINE_FILES)
    source_paths.update(ROOT/path for path in study.files)
    def signature(path):
        try:
            stat=path.stat()
            return stat.st_mtime_ns,stat.st_size
        except OSError:
            return None
    loaded_signatures = {path:signature(path) for path in source_paths}
    def sources_current():
        return all(signature(path)==expected for path,expected in loaded_signatures.items())
    bootstrap_cache = {}
    bootstrap_lock = Lock()
    # Bound to this immutable loaded study; never cache simulation parameters.
    @lru_cache(maxsize=16)
    def compressed(body):
        return gzip.compress(body,compresslevel=5,mtime=0)

    def accepts_gzip(header):
        encodings={}
        for item in header.lower().split(','):
            name,*parameters=item.strip().split(';')
            quality=1.0
            for parameter in parameters:
                if parameter.strip().startswith('q='):
                    try:quality=float(parameter.strip()[2:])
                    except ValueError:quality=0
            encodings[name]=quality
        return encodings.get('gzip',encodings.get('*',0))>0
    def revision():
        # A restart changes the revision, even with an unchanged model.
        return hashlib.sha256(instance.encode()+study.version.encode()+static_files['index.html']).hexdigest()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def reply(self, body, status=200, content_type='application/json; charset=utf-8', attachment=None, immutable=False, frozen=False):
            if isinstance(body,(dict,list)): body=json.dumps(body,ensure_ascii=False,allow_nan=False).encode('utf-8')
            compressible=len(body)>=1024 and (content_type.startswith('text/') or any(t in content_type for t in ('json','javascript','svg','yaml')))
            zipped=compressible and accepts_gzip(self.headers.get('Accept-Encoding',''))
            if zipped:body=compressed(body) if frozen else gzip.compress(body,compresslevel=5,mtime=0)
            self.send_response(status)
            self.send_header('Content-Type',content_type)
            self.send_header('Vary','Accept-Encoding')
            if zipped:self.send_header('Content-Encoding','gzip')
            self.send_header('Content-Length',str(len(body)))
            self.send_header('Cache-Control','public, max-age=31536000, immutable' if immutable else 'no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Referrer-Policy','no-referrer')
            if attachment: self.send_header('Content-Disposition','attachment; filename="'+attachment.encode('ascii','ignore').decode()+'"')
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            url=urlsplit(self.path)
            try:
                if url.path=='/api/health': return self.reply(dict(id=study.ui['id'],version=study.version,pid=os.getpid(),mode=study.edition['mode'],server_revision=revision(),client_build_sha256=client_build_sha256,sources_current=sources_current()))
                if url.path=='/api/ui': return self.reply(study.ui)
                if url.path=='/api/bootstrap':
                    current=revision()
                    essential=parse_qs(url.query).get('view',[''])[0]=='essential'
                    with bootstrap_lock:
                        key=(current,essential)
                        if key not in bootstrap_cache:
                            for stale in list(bootstrap_cache):
                                if stale[0]!=current:del bootstrap_cache[stale]
                            bootstrap_cache[key]=encode(dict(study.bootstrap(compact=True,essential=essential),server_revision=current))
                        body=bootstrap_cache[key]
                    return self.reply(body,frozen=True)
                if url.path=='/api/capability':
                    query=parse_qs(url.query)
                    if query.get('model_version',[''])[0]!=study.version:return self.reply(dict(error='version'),409)
                    identifier=query.get('id',[''])[0]
                    row=next((r for r in study.content['business_map']['rows'] if identifier in (r['capacite_id'],r['id'])),None)
                    if row is None:raise ScenarioError('missing_document')
                    return self.reply(dict(title=row['capacite']['nom'],text=row['capacite']['definition']+' '+row['frontiere'],source=study.content['business_map']['source']['path']),frozen=True)
                if url.path=='/api/market-build':
                    query=parse_qs(url.query)
                    if query.get('model_version',[''])[0]!=study.version:return self.reply(dict(error='version'),409)
                    build=study.content['market']['reperes_build_core']
                    return self.reply({key:build[key] for key in ('etude_oss','cadre_comparaison','fiches_produit','candidats_a_etudier')},frozen=True)
                if url.path=='/api/market-references':
                    query=parse_qs(url.query)
                    if query.get('model_version',[''])[0]!=study.version:return self.reply(dict(error='version'),409)
                    return self.reply(build_market_reading(study.content['market']),frozen=True)
                if url.path=='/api/economic-evaluations':
                    query=parse_qs(url.query)
                    if query.get('model_version',[''])[0]!=study.version:return self.reply(dict(error='version'),409)
                    return self.reply(study.content['economic_evaluations'],frozen=True)
                if url.path in ('/api/document','/api/file'):
                    reference=parse_qs(url.query).get('path',[''])[0]
                    file=study.document_path(reference)
                    if url.path=='/api/document':
                        if file.suffix not in ('.md','.yaml','.py'): raise ScenarioError('missing_document')
                        excerpt=document_excerpt(study.document_bytes(reference).decode('utf-8-sig'),file.suffix,reference.partition('#')[2])
                        return self.reply(dict(path=file.relative_to(ROOT).as_posix(),format=file.suffix,**excerpt),frozen=study.release_documents is not None)
                    return self.reply(study.document_bytes(reference),content_type=mimetypes.guess_type(file.name)[0] or 'application/octet-stream',attachment=file.name if file.suffix!='.pdf' else None,frozen=study.release_documents is not None)
                if url.path.startswith('/api/'): return self.reply(dict(error='missing_document'),404)
                file=(dist/url.path.lstrip('/')).resolve()
                if not file.is_relative_to(dist): return self.reply(dict(error='missing_document'),404)
                relative=file.relative_to(dist).as_posix()
                if relative not in static_files:
                    if url.path not in ('/','/index.html'): return self.reply(dict(error='missing_document'),404)
                    relative='index.html'
                body=static_files[relative]
                if relative=='index.html':
                    config=json.dumps(dict(id=study.ui['id'],reload_storage_key=study.ui['reload_storage_key'],
                        labels={k:study.ui['labels'][k] for k in ('loading','retry')},
                        errors={k:study.ui['errors'][k] for k in ('network','render','reset_session')},
                        server_revision=revision()),ensure_ascii=False).replace('<','\\u003c')
                    fallback='<div id="root"><p>'+html.escape(study.ui['labels']['loading'])+'</p><a href="">'+html.escape(study.ui['labels']['retry'])+'</a></div>'
                    body=(body.decode('utf-8').replace('<title></title>','<title>'+html.escape(study.ui['document_title'])+'</title>')
                          .replace('<div id="root"></div>',fallback)
                          .replace('</head>','<script id="app-config" type="application/json">'+config+'</script></head>')).encode('utf-8')
                return self.reply(body,content_type=('application/yaml; charset=utf-8' if Path(relative).suffix in ('.yaml','.yml') else mimetypes.guess_type(relative)[0] or 'application/octet-stream'),immutable=url.path.startswith('/assets/'),frozen=True)
            except ScenarioError as e: return self.reply(dict(error=e.code),404)
            except (OSError,ValueError): return self.reply(dict(error='internal'),500)

        def do_POST(self):
            if urlsplit(self.path).path!='/api/simulate': return self.reply(dict(error='missing_document'),404)
            origin=self.headers.get('Origin')
            allowed={f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}',
                     'http://127.0.0.1:5174','http://localhost:5174'}
            if origin and origin not in allowed: return self.reply(dict(error='invalid'),403)
            if not self.headers.get('Content-Type','').startswith('application/json'): return self.reply(dict(error='invalid'),415)
            try:
                length=int(self.headers.get('Content-Length',0))
                if not 0<length<100_000: raise ScenarioError('invalid')
                request=json.loads(self.rfile.read(length))
                if not isinstance(request,dict) or set(request)!={'parameters','model_version'}: raise ScenarioError('invalid')
                if request['model_version']!=study.version: raise ScenarioError('version')
                self.reply(study.simulate(request['parameters'],request['model_version']))
            except ScenarioError as e: self.reply(dict(error=e.code,field=e.field),422)
            except (ValueError,TypeError,KeyError): self.reply(dict(error='invalid'),400)
            except AssertionError: self.reply(dict(error='internal'),500)
    return Handler


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8766)
    args=parser.parse_args()
    study=load_current_study()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),make_handler(study))
    print(json.dumps(dict(url=f'http://127.0.0.1:{args.port}',model_version=study.version)),flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
