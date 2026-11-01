"""Download inventory rejects hidden sources and duplicates without changing originals."""
from copy import deepcopy
import hashlib
import unittest
from download_catalog import compile_catalog
from test_support import reference_study
from validate_stacks import ROOT,read

class DownloadCatalogTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.study=reference_study();cls.catalog=cls.study.content['downloads'];cls.document=read(ROOT/'source/telechargements.yaml');cls.originals=cls.study.content['synvance_reference']['documents']['items']
 def compile(self,document=None,originals=None):
  return compile_catalog(document or self.document,self.study.ui['documents'],originals or self.originals,self.study.files)
 def test_unique_catalog_preserves_original_bytes_formats_and_dates(self):
  c=self.catalog;self.assertEqual(len(c['originals']),7);self.assertEqual(sum(x['format']=='PDF' for x in c['originals']),5);self.assertEqual(sum(x['format']=='XLSX' for x in c['originals']),2)
  all_rows=c['originals']+c['documents'];self.assertEqual(len(all_rows),len({x['path'] for x in all_rows}))
  originals={o['path'].split('#')[0]:o for o in self.originals}
  for row in all_rows:
   self.assertNotIn(row['format'],['YAML','YML']);raw=(ROOT/row['path']).read_bytes();self.assertEqual(row['sha256'],hashlib.sha256(raw).hexdigest());self.assertEqual(row['bytes'],len(raw))
   if row['path'] in originals:self.assertEqual(row['date'],originals[row['path']]['date'])
  self.assertEqual(c['personal_route'],'#comparer');self.assertNotIn('scenarios',c)
 def test_unknown_yaml_and_duplicate_paths_are_rejected(self):
  for path in ['source/estimations-core-retenues.yaml','../secret.md','source/missing.md']:
   with self.subTest(path=path):
    d=deepcopy(self.document);d['reading_document_refs']=[path]
    with self.assertRaisesRegex(ValueError,'ERR_DOWNLOAD_CATALOG'):self.compile(d)
  originals=deepcopy(self.originals);originals.append(originals[0])
  with self.assertRaisesRegex(ValueError,'duplicate'):self.compile(originals=originals)
 def test_model_metadata_contract_and_menu_order(self):
  from export_business_model import ASSET,METADATA_ASSET
  c=self.catalog;self.assertEqual(c['model_package']['asset'],ASSET);self.assertEqual(c['model_package']['metadata_asset'],METADATA_ASSET)
  nav=[x['id'] for x in self.study.ui['essential']['nav']];self.assertEqual(nav[nav.index('glossaire')+1],'telechargements')
  groups=self.study.ui['essential']['nav_groups'];self.assertEqual(groups[-1]['items'],['glossaire','telechargements'])
  self.assertEqual(self.study.bootstrap(essential=True)['content']['downloads'],c)
