"""Push real commits to isolated bare repositories. GitHub/Pages are fixtures."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from git_commit import CommitError, Git, REPOSITORY, write_json
from git_push import SITE, PushError, prepare, push, remote_head, watch, MIRROR_REMOTE, MIRROR_REPOSITORY, MIRROR_SITE, enterprise_deployment
from validate_stacks import ROOT


class WorkflowTests(unittest.TestCase):
    def test_push_runs_full_and_browser_checks_before_deployment(self):
        import yaml
        workflow = yaml.load((ROOT/'.github/workflows/pages.yml').read_text(encoding='utf-8'), Loader=yaml.BaseLoader)
        self.assertIn('main', workflow['on']['push']['branches'])
        jobs = workflow['jobs']
        self.assertNotIn('if',jobs['build'])
        self.assertIn("'/FLOW-Etude-Economique/' || '/'",jobs['build']['env']['FLOW_PAGES_BASE'])
        self.assertEqual(jobs['deploy']['needs'], 'build')
        steps = jobs['build']['steps']
        commands = [step.get('run', '') for step in steps]
        self.assertTrue(any('python -m tools.check_model --full' in command for command in commands))
        browser = next(i for i, command in enumerate(commands) if 'node app/scripts/verify-pages.mjs' in command)
        artifact = next(i for i, step in enumerate(steps) if step.get('uses', '').startswith('actions/upload-pages-artifact@'))
        self.assertLess(browser, artifact)
        self.assertTrue(any('--base "$FLOW_PAGES_BASE"' in c for c in commands))
        self.assertIn('8777${FLOW_PAGES_BASE}', commands[browser])
        for step in steps:
            if step.get('run'):
                self.assertNotEqual(step.get('continue-on-error'), 'true')


class NativeGit(Git):
    # Only test fixtures replace the target-repository check for their private bare remote.
    def repository(self):
        if self.text('branch','--show-current')!='main':raise PushError('branche main attendue')
        return dict(root=str(self.root),branch='main',head=self.text('rev-parse','HEAD'),upstream='origin/main',author='Fixture')


class API:
    def __init__(self,sha):
        self.sha=sha
        self.conclusion='success'
        self.deploy='success'
        self.runs=[]
    def __call__(self,path):
        if path=='':return dict(full_name=REPOSITORY,private=False,visibility='public')
        if path.startswith('actions/workflows/'):
            return {'workflow_runs':self.runs or [dict(id=1,head_sha=self.sha,head_branch='main',event='push',status='completed',conclusion=self.conclusion,html_url='https://github.com/'+REPOSITORY+'/actions/runs/1')]}
        if path.startswith('actions/runs/'):return {'jobs':[dict(name='deploy',conclusion=self.deploy)]}
        if path=='pages':return {'html_url':SITE}
        raise AssertionError(path)


class EnterpriseAPI(API):
    def __call__(self,path):
        if path=='':return dict(full_name=MIRROR_REPOSITORY,visibility='internal')
        if path=='pages':return dict(html_url=MIRROR_SITE,public=False,build_type='workflow')
        if path.startswith('deployments?'):return [dict(id=10,sha=self.sha,environment='github-pages')]
        if path.startswith('deployments/'):return [dict(id=11,state='success',environment_url=MIRROR_SITE)]
        return super().__call__(path)


class EnterpriseDeploymentTests(unittest.TestCase):
    def test_private_deployment_proof_is_distinct_from_live_read(self):
        result=enterprise_deployment(EnterpriseAPI('abc'),'abc')
        self.assertTrue(result['deployment_verified'])
        self.assertFalse(result['live_manifest_verified'])
        self.assertEqual(result['commit'],'abc')

    def test_other_sha_does_not_confirm_deployment(self):
        self.assertFalse(enterprise_deployment(EnterpriseAPI('old'),'new')['deployment_verified'])

    def test_failed_enterprise_workflow_cannot_pass(self):
        api=EnterpriseAPI('abc');api.conclusion='failure'
        with self.assertRaisesRegex(PushError,'Beaumanoir'):enterprise_deployment(api,'abc')
        api.conclusion='success';api.deploy='skipped'
        with self.assertRaisesRegex(PushError,'deploy'):enterprise_deployment(api,'abc')

    def test_wrong_visibility_and_deployment_status_are_rejected(self):
        original=EnterpriseAPI('abc')
        for endpoint,value in [('pages',dict(html_url=MIRROR_SITE,public=True,build_type='workflow')),
            ('deployments/10/statuses?per_page=100',[dict(id=12,state='failure')]),
            ('deployments/10/statuses?per_page=100',[dict(id=12,state='success',environment_url='https://wrong.invalid/')])]:
            def api(path):return value if path==endpoint else original(path)
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(PushError):enterprise_deployment(api,'abc')


class PushTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(dir=ROOT/'tmp')
        self.addCleanup(self.folder.cleanup)
        self.base=Path(self.folder.name)
        self.root=self.base/'checkout'
        self.root.mkdir()
        self.git=NativeGit(self.root)
        self.git.raw('init','-b','main')
        self.git.raw('config','user.name','FLOW test')
        self.git.raw('config','user.email','flow-test@example.invalid')
        self.git.raw('config','commit.gpgsign','false')
        (self.root/'empty-hooks').mkdir()
        self.git.raw('config','core.hooksPath',str(self.root/'empty-hooks'))
        for name,value in {'.gitignore':'/tmp/\n/empty-hooks/\n','.github/workflows/pages.yml':"FLOW_DEPLOYMENT_COMMIT: source-sha\nFLOW_PAGES_BASE: /\n",'tools/build_pages.py':'# FLOW_DEPLOYMENT_COMMIT\n','file.txt':'initial'}.items():
            path=self.root/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(value,encoding='utf-8')
        self.git.raw('add','-A')
        self.git.raw('commit','-m','Initial fixture')
        self.remote=self.base/'remote.git'
        self.remote.mkdir()
        Git(self.remote).raw('init','--bare','--initial-branch=main')
        self.git.raw('remote','add','origin',str(self.remote))
        self.git.raw('push','origin','HEAD:refs/heads/main')
        self.mirror=self.base/'enterprise.git'
        self.mirror.mkdir()
        Git(self.mirror).raw('init','--bare','--initial-branch=main')
        self.git.raw('remote','add',MIRROR_REMOTE,str(self.mirror))
        self.allowed_mirrors=patch('git_push.MIRROR_URLS',{str(self.mirror)})
        self.allowed_mirrors.start()
        self.addCleanup(self.allowed_mirrors.stop)
        self.original=remote_head(self.git)
        (self.root/'file.txt').write_text('committed',encoding='utf-8')
        self.git.raw('add','--','file.txt')
        self.git.raw('commit','-m','Outgoing fixture')
        self.head=self.git.text('rev-parse','HEAD')
        self.api=API(self.head)
        self.report=self.root/'tmp/proof.json'
        write_json(self.report,dict(status='passed'))

    def plan(self,**kwargs):
        return prepare(self.root,git=self.git,api=self.api,mirror_api=lambda _:dict(full_name=MIRROR_REPOSITORY,visibility='internal'),**kwargs)
    def watch(self,path,**kwargs):
        for remote in ('origin',MIRROR_REMOTE):self.git.raw('push',remote,self.head+':refs/heads/main')
        ticks=[0]
        def sleep(seconds):ticks[0]+=max(seconds,.01)
        with patch('sys.stdout',io.StringIO()):
            return watch(self.root,path,timeout=2,poll=1,git=self.git,api=self.api,
                manifest_reader=kwargs.pop('manifest_reader',lambda url:dict(deployment_commit=self.head)),
                clock=lambda:ticks[0],sleep=sleep,mirror_api=EnterpriseAPI(self.head),**kwargs)

    def test_prepare_and_push_preserve_pending_work_and_use_exact_sha(self):
        (self.root/'file.txt').write_text('pending work',encoding='utf-8')
        self.git.raw('add','--','file.txt')
        before=self.git.entries()
        path,data=self.plan()
        self.assertEqual(len(data['commits']),1)
        self.assertIn('file.txt',data['pending'])
        self.assertEqual(remote_head(self.git),self.original)
        result=push(self.root,path,git=self.git)
        self.assertEqual(remote_head(self.git),self.head)
        self.assertTrue(result['remote_verified'])
        self.assertEqual(remote_head(self.git,MIRROR_REMOTE),self.head)
        self.assertEqual(set(result['remotes']),{'origin',MIRROR_REMOTE})
        self.assertFalse(result['deployment_verified'])
        self.assertEqual((self.root/'file.txt').read_text(encoding='utf-8'),'pending work')
        self.assertEqual(self.git.entries(),before)
        self.assertEqual(self.watch(path)['status'],'verified')

    def test_preview_cannot_send(self):
        path,data=self.plan(plan_only=True)
        self.assertFalse(data['ready'])
        with self.assertRaisesRegex(PushError,'prévisualisation'):push(self.root,path,git=self.git)
        self.assertEqual(remote_head(self.git),self.original)

    def advance_remote(self):
        other=self.base/'other'
        other.mkdir()
        foreign=Git(other)
        foreign.raw('clone',str(self.remote),'.')
        foreign.raw('config','user.name','Other test')
        foreign.raw('config','user.email','other@example.invalid')
        foreign.raw('config','commit.gpgsign','false')
        foreign.raw('config','core.hooksPath',str(self.root/'empty-hooks'))
        (other/'foreign.txt').write_text('foreign commit',encoding='utf-8')
        foreign.raw('add','--','foreign.txt')
        foreign.raw('commit','-m','Remote advance')
        foreign.raw('push','origin','HEAD:refs/heads/main')
        return foreign.text('rev-parse','HEAD')

    def test_advanced_remote_is_never_overwritten(self):
        path,_=self.plan()
        foreign=self.advance_remote()
        with self.assertRaisesRegex(PushError,'a avancé'):push(self.root,path,git=self.git)
        self.assertEqual(remote_head(self.git),foreign)
        status=json.loads((self.root/'tmp/git-push/result.json').read_text())
        self.assertEqual(status['status'],'push_failed')

    def test_divergent_prepare_and_stale_head_are_rejected(self):
        path,_=self.plan()
        self.git.raw('commit','--allow-empty','-m','Another local commit')
        with self.assertRaisesRegex(PushError,'HEAD ou origin'):push(self.root,path,git=self.git)
        self.advance_remote()
        with self.assertRaisesRegex(PushError,'divergé'):self.plan()

    def test_push_is_idempotent_and_recovers_uncertain_send(self):
        path,_=self.plan()
        original=self.git.raw
        def uncertain(*args,**kwargs):
            value=original(*args,**kwargs)
            if args[0]=='push':raise CommitError('Simulated timeout after successful send')
            return value
        with patch.object(self.git,'raw',side_effect=uncertain):
            self.assertTrue(push(self.root,path,git=self.git)['remote_verified'])
        self.assertFalse(push(self.root,path,git=self.git)['sent'])
        self.assertEqual(remote_head(self.git),self.head)

    def test_push_requires_no_local_test_receipt_or_simulation(self):
        self.report.unlink()
        import subprocess
        original = subprocess.run
        def git_only(args, **kwargs):
            self.assertIn(Path(args[0]).name.lower(), ('git', 'git.exe'))
            return original(args, **kwargs)
        with patch('git_push.subprocess.run', side_effect=git_only):
            path, data = self.plan()
            self.assertEqual(data['validation_location'], 'github')
            self.assertNotIn('oracle', data)
            self.assertNotIn('validation', data)
            self.assertTrue(push(self.root, path, git=self.git)['remote_verified'])
            self.assertEqual(self.watch(path)['validation_location'], 'github')

    def test_exact_ci_success_and_deployment_are_required(self):
        path,_=self.plan()
        self.api.conclusion='failure'
        with self.assertRaisesRegex(PushError,'workflow'):self.watch(path)
        self.api.conclusion='success'
        self.api.deploy='skipped'
        with self.assertRaisesRegex(PushError,'job deploy'):self.watch(path)

    def test_wrong_sha_workflows_and_old_site_cannot_pass(self):
        path,_=self.plan()
        self.api.runs=[dict(id=2,head_sha=self.original,head_branch='main',event='push',status='completed',conclusion='success',html_url='wrong-run')]
        with self.assertRaisesRegex(PushError,'Délai'):self.watch(path)
        self.api.runs=[]
        with self.assertRaisesRegex(PushError,'Délai'):
            self.watch(path,manifest_reader=lambda url:dict(deployment_commit=self.original))

    def test_site_changing_during_manifest_check_cannot_be_marked_verified(self):
        path,_=self.plan()
        reads=[0]
        def published(url):
            reads[0]+=1
            return dict(deployment_commit=self.head if reads[0]==1 else self.original)
        with self.assertRaisesRegex(PushError,'Délai'):self.watch(path,manifest_reader=published)
        report=json.loads((self.root/'tmp/git-push/result.json').read_text())
        self.assertFalse(report['deployment_verified'])

    def test_real_guard_refuses_an_unapproved_repository(self):
        with self.assertRaisesRegex(CommitError,'Origin'):
            prepare(self.root,plan_only=True,api=self.api)

    def test_tampered_plan_and_missing_provenance_are_rejected(self):
        path,_=self.plan()
        data=json.loads(path.read_text(encoding='utf-8'));data['head']=self.original
        write_json(path,data)
        with self.assertRaisesRegex(PushError,'plan de push'):push(self.root,path,git=self.git)
        (self.root/'tools/build_pages.py').write_text('# Old generator',encoding='utf-8')
        self.git.raw('add','--','tools/build_pages.py')
        self.git.raw('commit','-m','Old provenance fixture')
        with self.assertRaisesRegex(PushError,'provenance'):self.plan()

    def test_watching_a_sent_commit_does_not_require_freezing_local_head(self):
        path,_=self.plan()
        self.git.raw('commit','--allow-empty','-m','Work continues locally')
        self.assertEqual(self.watch(path)['commit'],self.head)

    def test_behind_branch_and_failed_validation_never_send_anything(self):
        self.git.raw('push','origin',self.head+':refs/heads/main')
        ahead=self.advance_remote()
        with self.assertRaisesRegex(PushError,'retard'):self.plan()
        self.assertEqual(remote_head(self.git),ahead)

    def test_partial_push_resumes_only_the_missing_destination(self):
        path,_=self.plan()
        raw=self.git.raw
        def fail_mirror(*args,**kwargs):
            if args[:2]==('push',MIRROR_REMOTE):raise CommitError('enterprise unavailable')
            return raw(*args,**kwargs)
        with patch.object(self.git,'raw',side_effect=fail_mirror):
            with self.assertRaisesRegex(PushError,'non confirmé'):push(self.root,path,git=self.git)
        self.assertEqual(remote_head(self.git),self.head)
        self.assertIsNone(remote_head(self.git,MIRROR_REMOTE,True))
        receipt=json.loads((self.root/'tmp/git-push/result.json').read_text())
        self.assertTrue(receipt['remotes']['origin']['verified'])
        result=push(self.root,path,git=self.git)
        self.assertFalse(result['remotes']['origin']['sent'])
        self.assertTrue(result['remotes'][MIRROR_REMOTE]['sent'])
        self.assertEqual(remote_head(self.git,MIRROR_REMOTE),self.head)

    def test_changed_mirror_blocks_both_pushes(self):
        path,_=self.plan()
        # A separately approved remote advance must never be overwritten.
        self.git.raw('commit','--allow-empty','-m','foreign tip')
        foreign=self.git.text('rev-parse','HEAD')
        self.git.raw('push',MIRROR_REMOTE,foreign+':refs/heads/main')
        self.git.raw('reset','--soft',self.head)
        with self.assertRaisesRegex(PushError,'a avancé'):push(self.root,path,git=self.git)
        self.assertEqual(remote_head(self.git),self.original)
        self.assertEqual(remote_head(self.git,MIRROR_REMOTE),foreign)
        with self.assertRaisesRegex(PushError,'divergé'):self.plan()

    def test_mirror_url_change_and_visibility_are_rejected(self):
        path,_=self.plan()
        with patch('git_push.MIRROR_URLS',{'https://unexpected.invalid/repo.git'}):
            with self.assertRaisesRegex(PushError,'exclusivement'):push(self.root,path,git=self.git)
        with self.assertRaisesRegex(PushError,'interne'):
            prepare(self.root,git=self.git,api=self.api,mirror_api=lambda _:dict(full_name=MIRROR_REPOSITORY,visibility='public'))
        self.assertEqual(remote_head(self.git),self.original)

    def test_existing_mirror_catches_up_without_changing_origin(self):
        self.git.raw('push',MIRROR_REMOTE,self.original+':refs/heads/main')
        self.git.raw('push','origin',self.head+':refs/heads/main')
        path,data=self.plan()
        self.assertEqual(data['commits'],[])
        self.assertEqual(data['mirror']['remote_head'],self.original)
        result=push(self.root,path,git=self.git)
        self.assertFalse(result['remotes']['origin']['sent'])
        self.assertEqual(remote_head(self.git,MIRROR_REMOTE),self.head)

    def test_enterprise_workflow_guard_must_be_committed(self):
        workflow=self.root/'.github/workflows/pages.yml'
        workflow.write_text('FLOW_DEPLOYMENT_COMMIT',encoding='utf-8')
        self.git.raw('add','--','.github/workflows/pages.yml')
        self.git.raw('commit','-m','Missing enterprise guard')
        with self.assertRaisesRegex(PushError,'workflow Pages'):self.plan()
        _,data=self.plan(plan_only=True)
        self.assertFalse(data['mirror_ready'])
        self.assertFalse(data['ready'])
