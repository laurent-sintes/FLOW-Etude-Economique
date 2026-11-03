"""Prepare an exact push, send it explicitly, then verify CI and the deployed site."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from git_commit import CommitError, Git, REPOSITORY, digest, public_repository, write_json

SITE = 'https://laurent-sintes.github.io/FLOW-Etude-Economique/'
WORKFLOW = '.github/workflows/pages.yml'


class PushError(CommitError):
    pass


class GitHub:
    def __init__(self):
        self.binary = shutil.which('gh')
        if not self.binary:
            candidate = Path('C:/Program Files/GitHub CLI/gh.exe')
            if candidate.is_file():self.binary = str(candidate)
        if not self.binary:raise PushError('GitHub CLI est requis pour suivre le déploiement')
        result = subprocess.run([self.binary,'auth','status','--hostname','github.com'],capture_output=True)
        if result.returncode:raise PushError('La connexion GitHub CLI à github.com doit être disponible')

    def __call__(self, path):
        result = subprocess.run([self.binary,'api','--hostname','github.com','--method','GET','repos/'+REPOSITORY+('/'+path if path else '')],capture_output=True)
        if result.returncode:raise PushError('Lecture GitHub impossible : '+path)
        return json.loads(result.stdout)


def remote_head(git):
    rows = git.text('ls-remote','--heads','origin','refs/heads/main').splitlines()
    if len(rows)!=1:raise PushError('La branche distante main doit exister et être unique')
    return rows[0].split()[0]


def origins(git):
    return dict(fetch=git.text('remote','get-url','--all','origin'),push=git.text('remote','get-url','--push','--all','origin'))


def sign(data):
    data['sha256'] = digest(json.dumps(data,ensure_ascii=False,sort_keys=True).encode())
    return data


def load_plan(root, path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    checksum = data.pop('sha256')
    if data.get('format')!=2 or digest(json.dumps(data,ensure_ascii=False,sort_keys=True).encode())!=checksum:
        raise PushError('Le plan de push a été modifié. Refaire la préparation')
    if data['repository']['root']!=str(Path(root).resolve()):raise PushError('Ce plan appartient à un autre checkout')
    return data


def prepare(root, plan_only=False, git=None, api=None):
    root = Path(root).resolve()
    git = git or Git(root)
    api = api or GitHub()
    repository = git.repository()
    urls = origins(git)
    public_repository(api(''))
    git.raw('fetch','--no-tags','origin','refs/heads/main:refs/remotes/origin/main')
    base = git.text('rev-parse','refs/remotes/origin/main')
    head = repository['head']
    common = git.text('merge-base',base,head)
    if common!=base:
        if common==head:
            raise PushError('main est en retard. Effectuer un fast-forward propre avant la préparation')
        raise PushError('Les branches ont divergé. Intégrer les changements avant le push')
    commits = git.text('-c','i18n.logOutputEncoding=UTF-8','log','--reverse','--format=%H %s',base+'..'+head).splitlines()
    provenance = b'FLOW_DEPLOYMENT_COMMIT' in git.raw('show',head+':tools/build_pages.py') and b'FLOW_DEPLOYMENT_COMMIT' in git.raw('show',head+':'+WORKFLOW)
    if not plan_only and not provenance:
        raise PushError('Ce commit ne publie pas encore sa provenance Pages. Committer aussi le workflow et le générateur mis à jour')
    if git.repository()!=repository or origins(git)!=urls or remote_head(git)!=base:
        raise PushError('HEAD ou origin/main a changé pendant la préparation')
    data = dict(format=2,repository=repository,origins=urls,remote_head=base,head=head,commits=commits,
                pending=git.text('status','--short'),provenance_ready=provenance,ready=not plan_only, validation_location='github')
    path = root/'tmp/git-push/plan.json'
    write_json(path,sign(data))
    return path,data


def _push(root, path, git=None):
    git = git or Git(root)
    data = load_plan(root,path)
    if not data['ready']:raise PushError('Ce plan est une prévisualisation non validée')
    if git.repository()!=data['repository'] or origins(git)!=data['origins']:
        raise PushError('HEAD ou origin a changé. Refaire la préparation')
    actual = remote_head(git)
    sent = False
    if actual!=data['head']:
        if actual!=data['remote_head']:raise PushError('origin/main a avancé. Aucun push effectué')
        try:
            git.raw('push','origin',data['head']+':refs/heads/main')
        except CommitError as error:
            # A timeout may follow a successful send. Read before any retry.
            if remote_head(git)!=data['head']:raise PushError('Push non confirmé. Ne pas relancer sans lire la référence distante') from error
        if remote_head(git)!=data['head']:raise PushError('Le SHA distant ne correspond pas au commit préparé')
        sent = True
    result = dict(status='pushed_not_verified',commit=data['head'],sent=sent,remote_verified=True,
                  deployment_verified=False,pending=git.text('status','--short'))
    write_json(Path(root)/'tmp/git-push/result.json',result)
    return result


def push(root,path,git=None):
    try:
        return _push(root,path,git)
    except (CommitError,OSError,ValueError,KeyError) as error:
        write_json(Path(root)/'tmp/git-push/result.json',dict(status='push_failed',error=str(error),deployment_verified=False))
        raise


def live_manifest(url):
    request = Request(url,headers={'Cache-Control':'no-cache','User-Agent':'FLOW-push-verification'})
    with urlopen(request,timeout=15) as response:return json.load(response)


def watch(root,path,timeout=1800,poll=5,git=None,api=None,manifest_reader=None,clock=time.monotonic,sleep=time.sleep):
    root = Path(root).resolve()
    git = git or Git(root)
    data = load_plan(root,path)
    if not data['ready']:raise PushError('La prévisualisation ne peut pas être suivie comme un envoi validé')
    if origins(git)!=data['origins']:raise PushError('Origin a changé')
    api = api or GitHub()
    public_repository(api(''))
    deadline = clock()+timeout
    result = dict(status='waiting_ci',commit=data['head'],deployment_verified=False)
    last = None
    try:
        while clock()<deadline:
            runs = api('actions/workflows/pages.yml/runs?branch=main&event=push&head_sha='+data['head']+'&per_page=30')['workflow_runs']
            runs = [r for r in runs if r['head_sha']==data['head'] and r['head_branch']=='main' and r['event']=='push'
                    and r.get('path',WORKFLOW).split('@')[0]==WORKFLOW]
            if runs:
                run = max(runs,key=lambda r:r['id'])
                result.update(run_id=run['id'],workflow_url=run['html_url'],status='ci_'+run['status'])
                if run['status']=='completed':
                    if run['conclusion']!='success':raise PushError('Le workflow du commit a échoué : '+str(run['conclusion']))
                    jobs = api('actions/runs/'+str(run['id'])+'/jobs?filter=latest&per_page=100')['jobs']
                    deployments = [j for j in jobs if j['name']=='deploy']
                    if len(deployments)!=1 or deployments[0]['conclusion']!='success':raise PushError('La CI est terminée mais le job deploy n’a pas réussi')
                    site = api('pages')['html_url']
                    if site.rstrip('/')+'/'!=SITE:raise PushError('L’URL Pages ne correspond pas au site autorisé')
                    result.update(site=site,status='waiting_site')
                    try:
                        manifest = (manifest_reader or live_manifest)(site.rstrip('/')+'/site-manifest.json?commit='+data['head'])
                    except (OSError,ValueError):manifest = {}
                    if manifest.get('deployment_commit')==data['head']:
                        latest = (manifest_reader or live_manifest)(site.rstrip('/')+'/site-manifest.json?commit='+data['head'])
                        if latest.get('deployment_commit')==data['head']:
                            result.update(status='verified',deployment_verified=True,validation_location='github')
                            write_json(root/'tmp/git-push/result.json',result)
                            return result
            write_json(root/'tmp/git-push/result.json',result)
            if result['status']!=last:
                print(json.dumps(result,ensure_ascii=False),flush=True)
                last = result['status']
            sleep(min(poll,max(0,deadline-clock())))
        raise PushError('Délai de suivi dépassé. Reprendre avec watch, sans renvoyer le commit')
    except (CommitError,OSError,ValueError,KeyError) as error:
        result.update(status='verification_failed',error=str(error))
        write_json(root/'tmp/git-push/result.json',result)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest='action',required=True)
    prep = modes.add_parser('prepare')
    prep.add_argument('--plan-only',action='store_true')
    for action in ('push','watch'):
        sub = modes.add_parser(action)
        sub.add_argument('--plan',type=Path,default=ROOT/'tmp/git-push/plan.json')
        sub.add_argument('--timeout',type=int,default=1800)
        if action=='push':sub.add_argument('--no-wait',action='store_true')
    args = parser.parse_args()
    try:
        if args.action=='prepare':
            path,data = prepare(ROOT,args.plan_only)
            print(json.dumps(dict(plan=str(path),ready=data['ready'],commit=data['head'],commits=data['commits'],pending=data['pending'],provenance_ready=data['provenance_ready']),ensure_ascii=False,indent=2))
        else:
            if args.timeout<=0:raise PushError('Le délai doit être positif')
            if args.action=='push':
                result = push(ROOT,args.plan)
                print(json.dumps(result,ensure_ascii=False,indent=2))
                if args.no_wait:return 0
            result = watch(ROOT,args.plan,args.timeout)
            print(json.dumps(result,ensure_ascii=False,indent=2))
    except (CommitError,OSError,ValueError,KeyError) as error:
        print(str(error),file=sys.stderr)
        return 1
    return 0


if __name__=='__main__':raise SystemExit(main())
