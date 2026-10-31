"""Exercise the commit wrapper against disposable native Git repositories."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from git_commit import CommitError, Git, REPOSITORY, commit, digest, file_proofs, prepare, source_hashes, validate, write_json
from validate_stacks import ROOT


class GitCommitTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(dir=ROOT/'tmp')
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        (self.root/'app').mkdir()
        self.git = Git(self.root)
        self.git.raw('init', '-b', 'main')
        self.git.raw('config', 'user.name', 'FLOW Test')
        self.git.raw('config', 'user.email', 'flow-test@example.invalid')
        self.git.raw('config', 'commit.gpgsign', 'false')
        # Only these disposable test repositories bypass globally configured hooks.
        (self.root/'empty-hooks').mkdir()
        self.git.raw('config', 'core.hooksPath', str(self.root/'empty-hooks'))
        (self.root/'audits').mkdir()
        (self.root/'selected.txt').write_text('before', encoding='utf-8')
        (self.root/'audits/other.txt').write_text('before', encoding='utf-8')
        self.git.raw('add', '--', 'selected.txt', 'audits/other.txt')
        self.git.raw('commit', '-m', 'Initial fixture')
        self.git.raw('remote', 'add', 'origin', 'https://github.com/'+REPOSITORY+'.git')
        self.old_head = self.git.text('rev-parse', 'HEAD')
        (self.root/'selected.txt').write_text('after', encoding='utf-8')
        self.report = self.root/'tmp/fixture-validation.json'
        write_json(self.report, {'status':'passed','mode':'full'})
        self.validation_calls = 0

    def metadata(self, root):
        return dict(full_name=REPOSITORY, visibility='public', private=False)

    def validator(self, root, inputs):
        self.validation_calls += 1
        return dict(inputs=inputs, reports=file_proofs([self.report]), reused=True)

    def plan(self, paths=None, **kwargs):
        return prepare(self.root, paths or ['selected.txt'], 'Clarifier le résultat', validator=self.validator, metadata=self.metadata, **kwargs)

    def test_prepare_is_read_only_and_commit_preserves_unrelated_staging(self):
        (self.root/'audits/other.txt').write_text('foreign change', encoding='utf-8')
        self.git.raw('add', '--', 'audits/other.txt')
        outside_before = self.git.entries()['audits/other.txt']
        before = self.git.entries()
        path, plan = self.plan()
        self.assertTrue(plan['ready'])
        self.assertEqual(self.git.entries(), before)
        self.assertEqual(self.git.text('rev-parse','HEAD'), self.old_head)
        result = commit(self.root, path)
        self.assertFalse(result['pushed'])
        self.assertEqual(self.git.names('diff-tree','--no-commit-id','--name-only','-r','-z','HEAD'), ['selected.txt'])
        self.assertEqual(self.git.entries()['audits/other.txt'], outside_before)
        self.assertEqual(self.git.text('show','HEAD:audits/other.txt'), 'before')
        self.assertIn('audits/other.txt', result['remaining'])
        self.assertEqual(self.git.text('log','-1','--format=%s'), 'Clarifier le résultat')

    def test_additions_deletions_and_literal_paths_are_supported(self):
        tricky = 'note $() [draft].txt'
        (self.root/tricky).write_text('literal content',encoding='utf-8')
        (self.root/'selected.txt').unlink()
        path,_ = self.plan(['selected.txt',tricky])
        commit(self.root,path)
        self.assertEqual(self.git.text('show','HEAD:'+tricky),'literal content')
        self.assertNotIn('selected.txt',self.git.names('ls-files','-z'))

    def test_partial_index_inside_scope_is_never_overwritten(self):
        self.git.raw('add','--','selected.txt')
        (self.root/'selected.txt').write_text('unstaged edit',encoding='utf-8')
        before = self.git.entries()
        with self.assertRaisesRegex(CommitError,'Index partiel'):self.plan()
        self.assertEqual(self.git.entries(),before)

    def test_external_paths_generated_files_and_ignored_files_are_rejected(self):
        for path in ('../outside.txt','tmp/cache.txt','app/dist/index.html','.git/config'):
            with self.subTest(path=path),self.assertRaises(CommitError):self.plan([path])
        (self.root/'.gitignore').write_text('ignored.txt\n',encoding='utf-8')
        (self.root/'ignored.txt').write_text('ignored',encoding='utf-8')
        with self.assertRaisesRegex(CommitError,'ignoré'):self.plan(['ignored.txt'])

    def test_wrong_repository_branch_or_visibility_cannot_commit(self):
        self.git.raw('remote','set-url','origin','https://github.com/another/project.git')
        with self.assertRaisesRegex(CommitError,'Origin'):self.plan()
        self.git.raw('remote','set-url','origin','https://github.com/'+REPOSITORY+'.git')
        self.git.raw('checkout','-b','other')
        with self.assertRaisesRegex(CommitError,'branche main'):self.plan()
        self.git.raw('checkout','main')
        with self.assertRaisesRegex(CommitError,'doit être public'):
            prepare(self.root,['selected.txt'],'Message',validator=self.validator,metadata=lambda root:dict(full_name=REPOSITORY,visibility='private',private=True))

    def test_preview_never_validates_stages_or_commits(self):
        before = self.git.entries()
        path,plan = self.plan(plan_only=True)
        self.assertFalse(plan['ready'])
        self.assertEqual(self.validation_calls,0)
        with self.assertRaisesRegex(CommitError,'prévisualisation'):commit(self.root,path)
        self.assertEqual(self.git.entries(),before)
        self.assertEqual(self.git.text('rev-parse','HEAD'),self.old_head)

    def test_changed_content_index_head_or_proof_invalidates_plan(self):
        path,_ = self.plan()
        (self.root/'selected.txt').write_text('changed again',encoding='utf-8')
        with self.assertRaisesRegex(CommitError,'ont changé'):commit(self.root,path)
        (self.root/'selected.txt').write_text('after',encoding='utf-8')
        path,_ = self.plan()
        self.git.raw('add','--','audits/other.txt')
        (self.root/'audits/other.txt').write_text('index changes',encoding='utf-8')
        self.git.raw('add','--','audits/other.txt')
        with self.assertRaisesRegex(CommitError,'ont changé'):commit(self.root,path)
        path,_ = self.plan()
        self.report.write_text('{"status":"failed"}',encoding='utf-8')
        with self.assertRaisesRegex(CommitError,'preuve de validation'):commit(self.root,path)
        self.assertEqual(self.git.text('rev-parse','HEAD'),self.old_head)

    def test_changed_selected_audit_during_validation_is_rejected(self):
        (self.root/'selected.txt').write_text('before',encoding='utf-8')
        name='audits/new.txt'
        (self.root/name).write_text('original',encoding='utf-8')
        def validator(root,inputs):
            (root/name).write_text('concurrent edit',encoding='utf-8')
            return self.validator(root,inputs)
        with self.assertRaisesRegex(CommitError,'sélectionné a changé'):
            prepare(self.root,[name],'Message',validator=validator,metadata=self.metadata)

    def test_changed_plan_and_failed_validation_cannot_commit(self):
        path,_ = self.plan()
        data=json.loads(path.read_text(encoding='utf-8'))
        data['message']='Unreviewed message'
        write_json(path,data)
        with self.assertRaisesRegex(CommitError,'plan a été modifié'):commit(self.root,path)
        def invalid(root,inputs):raise CommitError('Validation failed')
        with self.assertRaisesRegex(CommitError,'Validation failed'):
            prepare(self.root,['selected.txt'],'Message',validator=invalid,metadata=self.metadata)
        self.assertEqual(self.git.text('rev-parse','HEAD'),self.old_head)

    def test_working_inputs_outside_scope_and_empty_scope_are_rejected(self):
        (self.root/'another-input.txt').write_text('outside scope',encoding='utf-8')
        with self.assertRaisesRegex(CommitError,'hors périmètre'):self.plan()
        (self.root/'another-input.txt').unlink()
        (self.root/'selected.txt').write_text('before',encoding='utf-8')
        with self.assertRaisesRegex(CommitError,'Aucun changement'):self.plan()

    def test_exact_validation_receipt_is_reused_without_commands(self):
        from git_commit import runtime_signature
        inputs=source_hashes(self.root)
        write_json(self.root/'tmp/git-commit/validation.json',dict(inputs=inputs,runtime=runtime_signature(),reports=file_proofs([self.report])))
        with patch('git_commit.command',side_effect=AssertionError('Checks must not be repeated')):
            self.assertTrue(validate(self.root,inputs)['reused'])

    def test_head_changed_after_prepare_is_rejected(self):
        path,_=self.plan()
        self.git.raw('commit','--allow-empty','-m','Another commit')
        expected=self.git.text('rev-parse','HEAD')
        with self.assertRaisesRegex(CommitError,'ont changé'):commit(self.root,path)
        self.assertEqual(self.git.text('rev-parse','HEAD'),expected)

    def test_a_failed_hook_preserves_foreign_staging_and_creates_no_commit(self):
        (self.root/'audits/other.txt').write_text('foreign change',encoding='utf-8')
        self.git.raw('add','--','audits/other.txt')
        outside=self.git.entries()['audits/other.txt']
        hook=self.root/'empty-hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 1\n',encoding='utf-8',newline='\n')
        hook.chmod(0o755)
        path,_=self.plan()
        with self.assertRaises(CommitError):commit(self.root,path)
        self.assertEqual(self.git.text('rev-parse','HEAD'),self.old_head)
        self.assertEqual(self.git.entries()['audits/other.txt'],outside)
        self.assertEqual((self.root/'selected.txt').read_text(encoding='utf-8'),'after')

    def test_failed_or_stale_validation_receipts_are_not_reused(self):
        from git_commit import runtime_signature
        inputs=source_hashes(self.root)
        self.report.write_text('{"status":"failed"}',encoding='utf-8')
        write_json(self.root/'tmp/git-commit/validation.json',dict(inputs=inputs,runtime=runtime_signature(),reports=file_proofs([self.report])))
        with patch('git_commit.command',side_effect=CommitError('Fresh checks required')) as checks:
            with self.assertRaisesRegex(CommitError,'Fresh checks required'):validate(self.root,inputs)
            checks.assert_called_once()
