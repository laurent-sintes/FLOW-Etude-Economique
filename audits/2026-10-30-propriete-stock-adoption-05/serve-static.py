"""Read-only loopback preview of the compiled GitHub Pages project path."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[2];PREFIX='/FLOW-Etude-Economique/'
class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  url=urlsplit(path)
  if not url.path.startswith(PREFIX):return str(ROOT/'tmp/ownership-preview-path-not-served')
  return super().translate_path('/'+url.path[len(PREFIX):])
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',8782),partial(Handler,directory=str(ROOT/'app/dist-pages')))
print('http://127.0.0.1:8782'+PREFIX,flush=True)
server.serve_forever()
