"""Real browser checks of the static application with no HTTP API."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
from threading import Thread
from validate_stacks import ROOT


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass


def check(study,directory,witness=None):
    from pages_validation import build_cases
    cases=directory/'browser-cases.json'
    if witness is None:cases.write_text(json.dumps(build_cases(study),ensure_ascii=False),encoding='utf-8')
    else:cases=Path(witness).resolve()
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT/'app/dist')))
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    env=dict(os.environ)
    if os.name=='nt' and 'PLAYWRIGHT_CHROMIUM_EXECUTABLE' not in env:
        for candidate in (Path('C:/Program Files/Google/Chrome/Application/chrome.exe'),Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')):
            if candidate.is_file():
                env['PLAYWRIGHT_CHROMIUM_EXECUTABLE']=str(candidate)
                break
    try:
        result=subprocess.run([shutil.which('node') or 'node','app/scripts/verify-pages.mjs','--url',f'http://127.0.0.1:{server.server_port}/','--allow-root','true','--cases',str(cases),'--output',str(directory/'browser.json')],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace')
        (directory/'browser.log').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
        if result.returncode:raise RuntimeError('Static browser checks failed. See '+str(directory/'browser.log'))
        return json.loads((directory/'browser.json').read_text(encoding='utf-8'))
    finally:
        server.shutdown();server.server_close();thread.join()
