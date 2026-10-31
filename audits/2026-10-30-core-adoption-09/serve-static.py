from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[2];PREFIX='/FLOW-Etude-Economique/'
class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  url=urlsplit(path)
  if not url.path.startswith(PREFIX):return str(ROOT/'tmp/core-adoption-not-served')
  return super().translate_path('/'+url.path[len(PREFIX):])
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',8791),partial(Handler,directory=str(ROOT/'tmp/core-adoption-pages')))
print('http://127.0.0.1:8791'+PREFIX,flush=True)
server.serve_forever()
