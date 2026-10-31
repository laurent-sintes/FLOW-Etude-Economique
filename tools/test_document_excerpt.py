"""Targeted evidence, original-file access and authorization without initializing Study."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import quote

import yaml

from document_excerpt import document_excerpt
from serve_study_app import make_handler
from study_app import Study
from validate_stacks import ROOT


class DocumentExcerptTests(unittest.TestCase):
    def test_no_fragment_preserves_source_exactly(self):
        for suffix in ('.md', '.yaml', '.py'):
            source = 'Some original text\n\n'
            self.assertEqual(document_excerpt(source, suffix, ''), {'content': source})

    def test_yaml_nested_key_and_identity_are_localized(self):
        source = 'outer:\n  items:\n  - id: selected\n    evidence: original\n  - id: other\n    evidence: unrelated\n'
        result = document_excerpt(source, '.yaml', 'selected')
        self.assertEqual(result['focus']['status'], 'matched')
        self.assertEqual(result['focus']['reference'], '/outer/items/0')
        self.assertEqual(yaml.safe_load(result['content']), {'id': 'selected', 'evidence': 'original'})
        key = document_excerpt(source, '.yaml', 'items')
        self.assertEqual(key['focus']['location'], 'outer / items')

    def test_yaml_paths_select_identity_or_index_and_preserve_scalar_key(self):
        source = 'options:\n- stack: java-spring\n  detail_build:\n    budget: 12.34\n- bloc: BC-043\n  detail_build:\n    budget: 56.78\n'
        for selector in ('options/java-spring/detail_build', '/options/0/detail_build'):
            result = document_excerpt(source, '.yaml', selector)
            self.assertEqual(result['focus']['status'], 'matched')
            self.assertEqual(yaml.safe_load(result['content']), {'detail_build': {'budget': 12.34}})
        result = document_excerpt(source, '.yaml', 'options/BC-043/detail_build/budget')
        self.assertEqual(yaml.safe_load(result['content']), {'budget': 56.78})
        escaped = document_excerpt('a/b:\n  c~d: yes\n', '.yaml', '/a~1b/c~0d')
        self.assertEqual(escaped['focus']['reference'], '/a~1b/c~0d')

    def test_ambiguous_and_missing_selectors_do_not_display_a_false_excerpt(self):
        source = 'a:\n  target: first\nb:\n  target: second\n'
        result = document_excerpt(source, '.yaml', 'target')
        self.assertEqual(result['content'], '')
        self.assertEqual(result['focus']['status'], 'ambiguous')
        self.assertEqual([row['reference'] for row in result['focus']['candidates']], ['/a/target', '/b/target'])
        for candidate in result['focus']['candidates']:
            self.assertEqual(document_excerpt(source, '.yaml', candidate['reference'])['focus']['status'], 'matched')
        self.assertEqual(document_excerpt(source, '.yaml', 'absent')['focus']['status'], 'missing')
        duplicates = 'items:\n- id: same\n  value: first\n- id: same\n  value: second\n'
        self.assertEqual(document_excerpt(duplicates, '.yaml', 'items/same')['focus']['status'], 'ambiguous')
        numeric = 'items:\n- id: first\n- id: "0"\n'
        self.assertEqual(document_excerpt(numeric, '.yaml', 'items/0')['focus']['status'], 'ambiguous')
        self.assertEqual(document_excerpt(numeric, '.yaml', '/items/0')['focus']['status'], 'matched')

    def test_historical_dotted_paths_preserve_exact_native_identifiers(self):
        source = 'integration:\n  prix_rfi:\n    postes_eur:\n      module: 123.45\n'
        result = document_excerpt(source, '.yaml', 'integration.prix_rfi.postes_eur')
        self.assertEqual(result['focus']['status'], 'matched')
        self.assertEqual(result['focus']['reference'], '/integration/prix_rfi/postes_eur')
        self.assertEqual(yaml.safe_load(result['content']), {'postes_eur': {'module': 123.45}})
        native = 'capacites:\n- id: D01.c\n  evidence: native\nD01:\n  c: unrelated\n'
        self.assertEqual(yaml.safe_load(document_excerpt(native, '.yaml', 'D01.c')['content']), {'id': 'D01.c', 'evidence': 'native'})
        literal = 'literal.key: exact\nliteral:\n  key: unrelated\n'
        self.assertEqual(yaml.safe_load(document_excerpt(literal, '.yaml', 'literal.key')['content']), {'literal.key': 'exact'})

    def test_yaml_invalid_duplicate_keys_and_unsupported_format_are_explicit(self):
        self.assertEqual(document_excerpt('a: 1\na: 2\n', '.yaml', 'a')['focus']['status'], 'invalid')
        self.assertEqual(document_excerpt('a: [', '.yaml', 'a')['focus']['status'], 'invalid')
        self.assertEqual(document_excerpt('def target(): pass', '.py', 'target')['focus']['status'], 'unsupported')

    def test_markdown_keeps_section_children_and_stops_at_equal_or_parent_heading(self):
        source = '# Document\nIntro\n## Éléments à retenir\nProof\n### Child\nDetails\n## Next\nUnrelated\n'
        result = document_excerpt(source, '.md', '%C3%A9l%C3%A9ments-%C3%A0-retenir')
        self.assertEqual(result['focus']['status'], 'matched')
        self.assertEqual(result['focus']['line_start'], 3)
        self.assertEqual(result['content'], '## Éléments à retenir\nProof\n### Child\nDetails\n')
        child = document_excerpt(source, '.md', 'child')
        self.assertEqual(child['content'], '### Child\nDetails\n')

    def test_markdown_ignores_fenced_headings_and_supports_setext_and_duplicate_anchors(self):
        source = 'Title\n=====\n## Same\nFirst\n```md\n## Fake\n```\n## Same\nSecond\n'
        self.assertEqual(document_excerpt(source, '.md', 'fake')['focus']['status'], 'missing')
        self.assertEqual(document_excerpt(source, '.md', 'same-1')['content'], '## Same\nSecond\n')
        self.assertEqual(document_excerpt(source, '.md', 'title')['content'], source)

    def test_current_sponsor_references_resolve_to_small_precise_excerpts(self):
        references = (
            ('source/plan-investissement.yaml', 'integration_make'),
            ('source/plan-investissement.yaml', 'presentation_achats'),
            ('source/chiffrage/chiffrage-sap.yaml', 'integration.prix_rfi.postes_eur'),
            ('source/references-couts-integration.yaml', 'synthese_decision'),
            ('source/qualification-buy.yaml', 'reassort-sap'),
            ('source/lecture-metier.yaml', 'finance-conception'),
            ('source/couts-15-ans.yaml', 'options/java-spring/detail_build'),
            ('source/recalibration-metier.yaml', 'lots/controle'),
            ('source/parcours-integration.yaml', 'b2b-partial-stock'),
            ('source/ecarts-perimetre-flow-rfi.md', 'conclusions-à-retenir'),
        )
        for filename, fragment in references:
            with self.subTest(reference=f'{filename}#{fragment}'):
                source = (ROOT / filename).read_text(encoding='utf-8')
                result = document_excerpt(source, Path(filename).suffix, fragment)
                self.assertEqual(result['focus']['status'], 'matched')
                self.assertLess(len(result['content']), len(source))


class DocumentRouteTests(unittest.TestCase):
    def setUp(self):
        directory = ROOT / 'tmp'
        directory.mkdir(exist_ok=True)
        self.temp = TemporaryDirectory(prefix='document-excerpt-', dir=directory)
        self.root = Path(self.temp.name)
        assert self.root.resolve().is_relative_to(directory.resolve())
        self.addCleanup(self.temp.cleanup)
        self.client = self.root / 'client'
        self.client.mkdir()
        (self.client / 'index.html').write_text('<div id="root"></div>', encoding='utf-8')
        (self.root / 'proof.yaml').write_text('target:\n  amount: 12.34\nother: excluded\n', encoding='utf-8')
        (self.root / 'private.md').write_text('Not in the library', encoding='utf-8')
        (self.root / 'original.pdf').write_bytes(b'%PDF-original')
        (self.root / 'original.xlsx').write_bytes(b'original-workbook')
        self.study = SimpleNamespace(files={'proof.yaml', 'original.pdf', 'original.xlsx', '../outside.md'},release_documents=None,bootstrap=lambda **kw:{})
        self.study.document_path = lambda reference: Study.document_path(self.study, reference)
        self.study.document_bytes = lambda reference: Study.document_bytes(self.study, reference)

    def get(self, endpoint, reference):
        handler_class = make_handler(self.study, static_root=self.client)
        handler = handler_class.__new__(handler_class)
        handler.path = endpoint + '?path=' + quote(reference, safe='')
        result = {}
        handler.reply = lambda body, status=200, **kwargs: result.update(body=body, status=status, **kwargs)
        with patch('study_app.ROOT', self.root), patch('serve_study_app.ROOT', self.root):
            handler.do_GET()
        return result

    def test_api_extracts_after_authorization_and_full_document_remains_available(self):
        result = self.get('/api/document', 'proof.yaml#target')
        self.assertEqual(result['status'], 200)
        self.assertEqual(result['body']['focus']['status'], 'matched')
        self.assertNotIn('other:', result['body']['content'])
        full = self.get('/api/document', 'proof.yaml')['body']
        self.assertNotIn('focus', full)
        self.assertIn('other: excluded', full['content'])
        self.assertEqual(self.get('/api/file', 'proof.yaml#target')['body'], (self.root / 'proof.yaml').read_bytes())

    def test_missing_fragment_is_explicit_and_full_file_is_not_substituted(self):
        result = self.get('/api/document', 'proof.yaml#absent')['body']
        self.assertEqual(result['focus']['status'], 'missing')
        self.assertEqual(result['content'], '')

    def test_allowlist_and_path_traversal_are_enforced_with_fragments(self):
        for reference in ('private.md#target', '../outside.md#target', '%2e%2e/outside.md#target', str(self.root / 'proof.yaml') + '#target'):
            with self.subTest(reference=reference):
                self.assertEqual(self.get('/api/document', reference)['status'], 404)

    def test_original_pdf_and_workbook_are_unchanged(self):
        self.assertEqual(self.get('/api/file', 'original.pdf#page=7')['body'], b'%PDF-original')
        self.assertEqual(self.get('/api/file', 'original.xlsx')['body'], b'original-workbook')
        self.assertEqual(self.get('/api/document', 'original.pdf#page=7')['status'], 404)


if __name__ == '__main__':
    unittest.main()
