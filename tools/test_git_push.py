"""Push real commits to isolated bare repositories. GitHub/Pages are fixtures."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from git_commit import CommitError, Git, REPOSITORY, digest, file_proofs, write_json
from git_push import SITE, PushError, bound_inputs, committed_validation, prepare, push, remote_head, tree, watch
from validate_stacks import ROOT


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
        for name,value in {'.gitignore':'/tmp/\n/empty-hooks/\n','.github/workflows/pages.yml':'FLOW_DEPLOYMENT_COMMIT: source-sha\n','tools/build_pages.py':'# FLOW_DEPLOYMENT_COMMIT\n','file.txt':'initial'}.items():
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
        self.original=remote_head(self.git)
        (self.root/'file.txt').write_text('committed',encoding='utf-8')
        self.git.raw('add','--','file.txt')
        self.git.raw('commit','-m','Outgoing fixture')
        self.head=self.git.text('rev-parse','HEAD')
        self.api=API(self.head)
        self.report=self.root/'tmp/proof.json'
        write_json(self.report,dict(status='passed'))

    def validation(self,git,sha):
        return dict(reports=file_proofs([self.report]),commit=sha)
    def oracle(self,git,sha):
        path=self.root/'tmp/oracle.json'
        write_json(path,dict(commit=sha))
        return path
    def plan(self,**kwargs):
        return prepare(self.root,git=self.git,api=self.api,validator=self.validation,oracle_builder=self.oracle,**kwargs)
    def watch(self,path,**kwargs):
        ticks=[0]
        def sleep(seconds):ticks[0]+=max(seconds,.01)
        with patch('sys.stdout',io.StringIO()):
            return watch(self.root,path,timeout=2,poll=1,git=self.git,api=self.api,
                manifest_reader=kwargs.pop('manifest_reader',lambda url:dict(deployment_commit=self.head)),
                browser=kwargs.pop('browser',lambda git,data,site:'fixture-browser.json'),clock=lambda:ticks[0],sleep=sleep,**kwargs)

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

    def test_proof_or_oracle_change_blocks_push(self):
        path,_=self.plan()
        self.report.write_text('{"status":"failed"}',encoding='utf-8')
        with self.assertRaises(CommitError):push(self.root,path,git=self.git)
        self.assertEqual(remote_head(self.git),self.original)
        write_json(self.report,dict(status='passed'))
        path,_=self.plan()
        (self.root/'tmp/oracle.json').write_text('changed',encoding='utf-8')
        with self.assertRaisesRegex(PushError,'simulations'):push(self.root,path,git=self.git)

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

    def test_site_changing_during_browser_check_cannot_be_marked_verified(self):
        path,_=self.plan()
        reads=[0]
        def published(url):
            reads[0]+=1
            return dict(deployment_commit=self.head if reads[0]==1 else self.original)
        with self.assertRaisesRegex(PushError,'Délai'):self.watch(path,manifest_reader=published)
        report=json.loads((self.root/'tmp/git-push/result.json').read_text())
        self.assertFalse(report['deployment_verified'])

    def test_failed_live_browser_remains_a_failed_verification(self):
        path,_=self.plan()
        def failed(*args):raise PushError('Browser failed')
        with self.assertRaisesRegex(PushError,'Browser failed'):self.watch(path,browser=failed)
        report=json.loads((self.root/'tmp/git-push/result.json').read_text())
        self.assertFalse(report['deployment_verified'])
        self.assertEqual(report['status'],'verification_failed')

    def test_validation_binds_committed_sources_not_dirty_workspace(self):
        expected={name:digest(self.git.raw('cat-file','blob',blob)) for name,blob in tree(self.git,self.head).items()}
        (self.root/'file.txt').write_text('uncommitted',encoding='utf-8')
        self.assertTrue(bound_inputs(self.git,self.head,expected))
        expected['file.txt']='0'*64
        self.assertFalse(bound_inputs(self.git,self.head,expected))

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

    def test_full_validation_receipt_is_bound_to_commit_and_rejects_unproved_code(self):
        expected={name:dict(sha256=digest(self.git.raw('cat-file','blob',blob))) for name,blob in tree(self.git,self.head).items()}
        expected['app/tsconfig.tsbuildinfo']=dict(sha256='generated-cache')
        expected['tools/syntax-check/node_modules/tool/package.json']=dict(sha256='installed-package')
        write_json(self.report,dict(status='passed',mode='full'))
        write_json(self.root/'tmp/validation-full-manifest.json',dict(files=expected,report=str(self.report)))
        (self.root/'file.txt').write_text('pending work',encoding='utf-8')
        self.assertEqual(committed_validation(self.git,self.head)['commit'],self.head)
        (self.root/'tools/unproved.py').write_text('new code',encoding='utf-8')
        self.git.raw('add','--','tools/unproved.py')
        self.git.raw('commit','-m','Unproved code fixture')
        with self.assertRaisesRegex(PushError,'Aucune validation'):
            committed_validation(self.git,self.git.text('rev-parse','HEAD'))

    def test_watching_a_sent_commit_does_not_require_freezing_local_head(self):
        path,_=self.plan()
        self.git.raw('commit','--allow-empty','-m','Work continues locally')
        self.assertEqual(self.watch(path)['commit'],self.head)

    def test_behind_branch_and_failed_validation_never_send_anything(self):
        self.git.raw('push','origin',self.head+':refs/heads/main')
        ahead=self.advance_remote()
        with self.assertRaisesRegex(PushError,'retard'):self.plan()
        self.assertEqual(remote_head(self.git),ahead)
