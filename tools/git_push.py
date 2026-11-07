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
MIRROR_SITE = 'https://solution-ai-flow-etude-economique.pages.beaumanoir.ghe.com/'
WORKFLOW = '.github/workflows/pages.yml'
MIRROR_REMOTE = 'beaumanoir'
MIRROR_HOST = 'beaumanoir.ghe.com'
MIRROR_REPOSITORY = 'solution-ai/FLOW-Etude-Economique'
MIRROR_URLS = {
    'https://' + MIRROR_HOST + '/' + MIRROR_REPOSITORY + '.git',
    'https://' + MIRROR_HOST + '/' + MIRROR_REPOSITORY,
    'git@' + MIRROR_HOST + ':' + MIRROR_REPOSITORY + '.git',
    'ssh://git@' + MIRROR_HOST + '/' + MIRROR_REPOSITORY + '.git',
}


class PushError(CommitError):
    pass


class GitHub:
    def __init__(self,host='github.com',repository=REPOSITORY):
        self.host,self.repository = host,repository
        self.binary = shutil.which('gh')
        if not self.binary:
            candidate = Path('C:/Program Files/GitHub CLI/gh.exe')
            if candidate.is_file():self.binary = str(candidate)
        if not self.binary:raise PushError('GitHub CLI est requis pour suivre le déploiement')
        result = subprocess.run([self.binary,'auth','status','--hostname',self.host],capture_output=True)
        if result.returncode:raise PushError('La connexion GitHub CLI à '+self.host+' doit être disponible')

    def __call__(self, path):
        result = subprocess.run([self.binary,'api','--hostname',self.host,'--method','GET','repos/'+self.repository+('/'+path if path else '')],capture_output=True)
        if result.returncode:raise PushError('Lecture GitHub impossible : '+path)
        return json.loads(result.stdout)


def remote_head(git,remote='origin',allow_empty=False):
    rows = git.text('ls-remote','--heads',remote,'refs/heads/main').splitlines()
    if not rows and allow_empty:return None
    if len(rows)!=1:raise PushError('La branche distante main doit exister et être unique')
    return rows[0].split()[0]


def origins(git,remote='origin'):
    return dict(fetch=git.text('remote','get-url','--all',remote),push=git.text('remote','get-url','--push','--all',remote))


def mirror_origins(git):
    urls = origins(git,MIRROR_REMOTE)
    if any(url not in MIRROR_URLS for values in urls.values() for url in values.splitlines()):
        raise PushError('Le remote beaumanoir doit cibler exclusivement '+MIRROR_HOST+'/'+MIRROR_REPOSITORY)
    return urls


def verify_mirror_repository(api):
    metadata = api('')
    if metadata.get('full_name')!=MIRROR_REPOSITORY or metadata.get('visibility')!='internal':
        raise PushError('Le dépôt Beaumanoir attendu doit être interne, sans changement automatique de visibilité')


def sign(data):
    data['sha256'] = digest(json.dumps(data,ensure_ascii=False,sort_keys=True).encode())
    return data


def load_plan(root, path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    checksum = data.pop('sha256')
    if data.get('format')!=4 or digest(json.dumps(data,ensure_ascii=False,sort_keys=True).encode())!=checksum:
        raise PushError('Le plan de push a été modifié. Refaire la préparation')
    if data['repository']['root']!=str(Path(root).resolve()):raise PushError('Ce plan appartient à un autre checkout')
    return data


def prepare(root, plan_only=False, git=None, api=None, mirror_api=None):
    root = Path(root).resolve()
    git = git or Git(root)
    api = api or GitHub()
    repository = git.repository()
    urls = origins(git)
    public_repository(api(''))
    mirror_urls = mirror_origins(git)
    verify_mirror_repository(mirror_api or GitHub(MIRROR_HOST,MIRROR_REPOSITORY))
    mirror_base = remote_head(git,MIRROR_REMOTE,allow_empty=True)
    git.raw('fetch','--no-tags','origin','refs/heads/main:refs/remotes/origin/main')
    base = git.text('rev-parse','refs/remotes/origin/main')
    head = repository['head']
    common = git.text('merge-base',base,head)
    if common!=base:
        if common==head:
            raise PushError('main est en retard. Effectuer un fast-forward propre avant la préparation')
        raise PushError('Les branches ont divergé. Intégrer les changements avant le push')
    if mirror_base is not None:
        git.raw('fetch','--no-tags',MIRROR_REMOTE,'refs/heads/main:refs/remotes/'+MIRROR_REMOTE+'/main')
        mirror_base = git.text('rev-parse','refs/remotes/'+MIRROR_REMOTE+'/main')
        if git.text('merge-base',mirror_base,head,allowed=(0,1))!=mirror_base:
            raise PushError('La branche Beaumanoir a divergé ou est en avance. Aucun envoi effectué')
    commits = git.text('-c','i18n.logOutputEncoding=UTF-8','log','--reverse','--format=%H %s',base+'..'+head).splitlines()
    provenance = b'FLOW_DEPLOYMENT_COMMIT' in git.raw('show',head+':tools/build_pages.py') and b'FLOW_DEPLOYMENT_COMMIT' in git.raw('show',head+':'+WORKFLOW)
    mirror_ready = b'FLOW_PAGES_BASE' in git.raw('show',head+':'+WORKFLOW)
    if not plan_only and not mirror_ready:
        raise PushError('Committer le workflow Pages adapté aux deux hébergements avant le double push')
    if not plan_only and not provenance:
        raise PushError('Ce commit ne publie pas encore sa provenance Pages. Committer aussi le workflow et le générateur mis à jour')
    if git.repository()!=repository or origins(git)!=urls or remote_head(git)!=base or mirror_origins(git)!=mirror_urls or remote_head(git,MIRROR_REMOTE,True)!=mirror_base:
        raise PushError('HEAD ou origin/main a changé pendant la préparation')
    data = dict(format=4,mirror=dict(remote=MIRROR_REMOTE,origins=mirror_urls,remote_head=mirror_base),repository=repository,origins=urls,remote_head=base,head=head,commits=commits,
                pending=git.text('status','--short'),provenance_ready=provenance,mirror_ready=mirror_ready,ready=not plan_only, validation_location='github')
    path = root/'tmp/git-push/plan.json'
    write_json(path,sign(data))
    return path,data


def _push(root, path, git=None):
    git = git or Git(root)
    data = load_plan(root,path)
    if not data['ready']:raise PushError('Ce plan est une prévisualisation non validée')
    if git.repository()!=data['repository'] or origins(git)!=data['origins']:
        raise PushError('HEAD ou origin a changé. Refaire la préparation')
    if mirror_origins(git)!=data['mirror']['origins']:
        raise PushError('Le remote Beaumanoir a changé. Refaire la préparation')
    targets = [('origin',data['remote_head']),(MIRROR_REMOTE,data['mirror']['remote_head'])]
    # Inspect both destinations before the first write. Never force either branch.
    for remote,base in targets:
        actual = remote_head(git,remote,remote==MIRROR_REMOTE)
        if actual not in (base,data['head']):
            raise PushError(remote+'/main a avancé. Aucun push effectué')
    results = {}
    for remote,base in targets:
        actual = remote_head(git,remote,remote==MIRROR_REMOTE)
        sent = actual!=data['head']
        if sent:
            if actual!=base:raise PushError(remote+'/main a avancé pendant le push')
            try:
                git.raw('push',remote,data['head']+':refs/heads/main')
            except CommitError as error:
                if remote_head(git,remote,remote==MIRROR_REMOTE)!=data['head']:
                    raise PushError('Push non confirmé sur '+remote+'. Reprendre le même plan pour compléter les envois') from error
        if remote_head(git,remote,remote==MIRROR_REMOTE)!=data['head']:
            raise PushError('Le SHA distant ne correspond pas au commit préparé sur '+remote)
        results[remote] = dict(commit=data['head'],sent=sent,verified=True)
        write_json(Path(root)/'tmp/git-push/result.json',dict(status='push_in_progress',commit=data['head'],remotes=results,deployment_verified=False))
    if any(remote_head(git,remote)!=data['head'] for remote,_ in targets):
        raise PushError('Une branche distante a changé pendant le double push')
    result = dict(status='pushed_not_verified',commit=data['head'],sent=any(r['sent'] for r in results.values()),
                  remote_verified=True,remotes=results,deployment_verified=False,pending=git.text('status','--short'))
    write_json(Path(root)/'tmp/git-push/result.json',result)
    return result


def push(root,path,git=None):
    write_json(Path(root)/'tmp/git-push/result.json',dict(status='push_starting',deployment_verified=False))
    try:
        return _push(root,path,git)
    except (CommitError,OSError,ValueError,KeyError) as error:
        result_path = Path(root)/'tmp/git-push/result.json'
        try:result = json.loads(result_path.read_text(encoding='utf-8'))
        except (OSError,ValueError):result = {}
        result.update(status='push_failed',error=str(error),deployment_verified=False)
        write_json(result_path,result)
        raise


def live_manifest(url):
    request = Request(url,headers={'Cache-Control':'no-cache','User-Agent':'FLOW-push-verification'})
    with urlopen(request,timeout=15) as response:return json.load(response)


def enterprise_deployment(api,head):
    """Verify the private deployment through authenticated GitHub APIs.

    This does not claim an authenticated browser read of the private site.
    """
    pages = api('pages')
    if pages.get('html_url','').rstrip('/')+'/'!=MIRROR_SITE or pages.get('public') is not False or pages.get('build_type')!='workflow':
        raise PushError('Le site Pages Beaumanoir doit correspondre à l’URL privée autorisée')
    result = dict(site=MIRROR_SITE,deployment_verified=False,live_manifest_verified=False,verification='github_api')
    runs = api('actions/workflows/pages.yml/runs?branch=main&event=push&head_sha='+head+'&per_page=30')['workflow_runs']
    runs = [r for r in runs if r['head_sha']==head and r['head_branch']=='main' and r['event']=='push'
            and r.get('path',WORKFLOW).split('@')[0]==WORKFLOW]
    if not runs:return result
    run = max(runs,key=lambda r:r['id'])
    result.update(workflow_url=run['html_url'],run_id=run['id'])
    if run['status']!='completed':return result
    if run['conclusion']!='success':raise PushError('Le workflow Beaumanoir a échoué : '+str(run['conclusion']))
    jobs = api('actions/runs/'+str(run['id'])+'/jobs?filter=latest&per_page=100')['jobs']
    deploys = [j for j in jobs if j['name']=='deploy']
    if len(deploys)!=1 or deploys[0]['conclusion']!='success':raise PushError('Le job deploy Beaumanoir n’a pas réussi')
    deployments = api('deployments?sha='+head+'&environment=github-pages&per_page=100')
    deployments = [d for d in deployments if d.get('sha')==head and d.get('environment')=='github-pages']
    if not deployments:return result
    deployment = max(deployments,key=lambda d:d['id'])
    statuses = api('deployments/'+str(deployment['id'])+'/statuses?per_page=100')
    if not statuses:return result
    status = max(statuses,key=lambda d:d['id'])
    if status.get('state') in ('failure','error','inactive'):raise PushError('Le déploiement Pages Beaumanoir est en échec ou inactif')
    if status.get('state')=='success':
        if status.get('environment_url','').rstrip('/')+'/'!=MIRROR_SITE:raise PushError('URL du déploiement Beaumanoir inattendue')
        result.update(deployment_verified=True,deployment_id=deployment['id'],commit=head)
    return result


def watch(root,path,timeout=1800,poll=5,git=None,api=None,manifest_reader=None,clock=time.monotonic,sleep=time.sleep,mirror_api=None):
    root = Path(root).resolve()
    git = git or Git(root)
    data = load_plan(root,path)
    if not data['ready']:raise PushError('La prévisualisation ne peut pas être suivie comme un envoi validé')
    if origins(git)!=data['origins'] or mirror_origins(git)!=data['mirror']['origins']:raise PushError('Un remote a changé')
    api = api or GitHub()
    public_repository(api(''))
    mirror_api = mirror_api or GitHub(MIRROR_HOST,MIRROR_REPOSITORY)
    verify_mirror_repository(mirror_api)
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
                            if any(remote_head(git,remote)!=data['head'] for remote in ('origin',MIRROR_REMOTE)):
                                raise PushError('Les deux branches distantes doivent correspondre au commit déployé')
                            result['sites'] = {'origin':dict(site=site,deployment_verified=True,live_manifest_verified=True)}
                            enterprise = enterprise_deployment(mirror_api,data['head'])
                            result['sites'][MIRROR_REMOTE] = enterprise
                            if enterprise['deployment_verified']:
                                result['remotes'] = {remote:dict(commit=data['head'],verified=True) for remote in ('origin',MIRROR_REMOTE)}
                                result.update(status='verified',deployment_verified=True,validation_location='github')
                                write_json(root/'tmp/git-push/result.json',result)
                                return result
                            result['status'] = 'waiting_beaumanoir'
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
            print(json.dumps(dict(plan=str(path),ready=data['ready'],commit=data['head'],commits=data['commits'],pending=data['pending'],mirror=data['mirror'],mirror_ready=data['mirror_ready'],provenance_ready=data['provenance_ready']),ensure_ascii=False,indent=2))
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
