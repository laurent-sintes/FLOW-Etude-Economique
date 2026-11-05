"""Proposed MDM estimates replay from code evidence and never enter retained economics."""
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

from capability_catalog import catalog
from estimation_calculation import evaluate_rule
from mdm_oss_estimation import SOURCE, NATIVE, UNIT, REVISION, FUNDING, build_mdm_assessment, dependencies, prepared, project_assessment, project_engineering, proof, refine_unidata, scope_evidence
from model_context import model_session
from test_support import active_reference, reference_study
from validate_stacks import ROOT, read

class MdmOssTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study=reference_study()
        cls.units=next(o['core_units'] for o in cls.study.economic['options'] if o['stack']=='java-spring')
        cls.unit=next(u for u in cls.units if u['id']==UNIT)
        cls.assessment=cls.study.content['delivery_organisation']['mdm_oss_assessment']
        cls.spec=read(ROOT/SOURCE)
        cls.frozen={v['path']:(ROOT/v['path']).read_bytes() for v in cls.spec['proofs'].values()}
        cls.docs={k:proof(v,cls.frozen) for k,v in cls.spec['proofs'].items()}
        cls.native=catalog()['rows'];cls.source=read(ROOT/NATIVE)
        cls.revision=read(ROOT/REVISION);cls.funding=read(ROOT/FUNDING)

    def test_pinned_measurements_and_conditional_estimate_reconcile(self):
        d=self.assessment;rows={p['id']:p for p in d['products']}
        self.assertEqual(d['status'],'proposal_not_adopted')
        self.assertEqual(d['anchor'],'unidata')
        retained=active_reference()['units'][UNIT]
        self.assertEqual(d['retained'],{k:retained[k] for k in ('jh','cost_eur_ht')})
        self.assertEqual({r['id'] for r in d['coverage']},{c['id'] for c in self.unit['capabilities']})
        self.assertEqual(len(d['coverage']),33);self.assertNotIn('BC-002',{r['id'] for r in d['coverage']})
        self.assertEqual(len(d['family_adapters']),8)
        self.assertIsNone(d['confidence_interval']);self.assertIsNone(d['cosmic_jh'])
        expected={'atrocore':(15450,948,17.078,1710), 'unidata':(47082,948,48.710,5410), 'pimcore':(33524,1022,35.226,3780)}
        for id,p in rows.items():
            self.assertEqual((p['measured_units'],p['additional_units'],p['ksloc'],p['jh']),expected[id])
            self.assertEqual(sum(g['units'] for g in p['groups']),p['measured_units'])
            self.assertEqual(p['family_units'],680)
            self.assertAlmostEqual(p['raw_jh'],2.94*expected[id][2]**1.0997*152/7*1.18)
            self.assertLess(p['sensitivity'][0]['jh'],p['jh']);self.assertGreater(p['sensitivity'][1]['jh'],p['jh'])
        self.assertEqual(sum(p['file_count'] for p in rows.values()),1654)
        review=d['unidata_review']
        self.assertEqual((review['initial']['jh'],review['initial']['ksloc'],review['removed_units']),(5420,48.845,135))
        self.assertEqual({r['id']:r['units'] for r in review['exclusions']},{'legacy-model-xml':67,'shared-process':68})
        self.assertTrue(any('Excel' in r['label'] for r in review['open_questions']))

    def test_readings_use_the_adopted_financial_reference(self):
        s=self.study;reference=active_reference()
        before=deepcopy(reference['before']['parameters'])
        before['options']['java-spring']['build']=reference['cost_eur_ht']
        self.assertEqual(s.parameters,before)
        gross=s.content['gross_evaluations']['phases']['acquisition']['options']['java-spring']['core']
        self.assertEqual(gross['mdm_oss_assessment'],self.assessment)
        self.assertEqual(gross['adopted_jh'],reference['total_jh'])
        self.assertEqual(gross['domain_reading']['measures']['cost_eur_ht']['total'],reference['cost_eur_ht'])
        self.assertTrue(set(dependencies())<=s.files)

    def test_replay_from_frozen_documents_has_no_source_checkout_dependency(self):
        rules={r['id']:r for r in self.study.fundamentals['estimation_model']['rules']}
        with model_session():spec,_,_,_=prepared()
        with patch.object(Path,'read_bytes',side_effect=AssertionError('unexpected file read')):
            docs={k:proof(v,self.frozen) for k,v in spec['proofs'].items()}
            products=scope_evidence(spec,docs['scope'],docs['measures'],docs['code'],self.native,self.source)
            measures=refine_unidata(spec,docs['measures'],docs['code'],docs['unidata_selection'])
            measures['engineering']=project_engineering(spec,docs['engineering'],self.revision,self.funding)
            result=project_assessment(spec,docs['scope'],measures,products,self.unit,lambda key,**kwargs:evaluate_rule(rules[key],**kwargs))
        self.assertEqual(result,self.assessment)

    def test_duplicate_files_scope_drift_and_tampered_analogue_fail(self):
        for mode,pattern in [('duplicate','Duplicate measurement'),('scope','Incomplete or duplicated MDM scope'),('analogue','Analogue is not bound')]:
            docs=deepcopy(self.docs)
            if mode=='duplicate':docs['measures']['files'].append(deepcopy(docs['measures']['files'][0]))
            if mode=='scope':docs['scope']['coverage'][0]['native_id']='master-data-ingestion'
            if mode=='analogue':docs['scope']['completions'][0]['samples'][0]['program_units']+=1
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,pattern):
                scope_evidence(self.spec,docs['scope'],docs['measures'],docs['code'],self.native,self.source)
        ref=self.spec['proofs']['scope'];bad=dict(self.frozen);bad[ref['path']]+=b' '
        with self.assertRaisesRegex(ValueError,'Proof hash changed'):proof(ref,bad)

    def test_unidata_selection_rejects_duplicate_or_changed_excerpts(self):
        for mode, pattern in [('duplicate','selected twice'),('excerpt','overlapping Unidata excerpt'),('base','different measurement')]:
            selection=deepcopy(self.docs['unidata_selection'])
            first=selection['exclusions'][0]['files']
            if mode=='duplicate':
                first.append(deepcopy(first[0]))
            elif mode=='excerpt':
                first[1]['segments'][0]['start_byte']+=1
            else:
                selection['measurements_sha256']='0'*64
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,pattern):
                refine_unidata(self.spec,self.docs['measures'],self.docs['code'],selection)

    def test_engineering_work_replaces_common_packages_without_refunding_shared_services(self):
        proposal=self.assessment['engineering']
        self.assertEqual(proposal['status'],'adopted')
        self.assertEqual({g['id']:g['jh'] for g in proposal['groups']},{'engine':2275,'interfaces':940})
        self.assertEqual([len(g['components']) for g in proposal['groups']],[12,7])
        self.assertEqual((proposal['family_jh'],proposal['qualification_jh']),(730,200))
        self.assertEqual((proposal['central_jh'],proposal['extended_jh'],proposal['retained_jh'],proposal['gap_jh']),(4145,4375,2670,1475))
        self.assertEqual(proposal['work_jh'],active_reference()['units'][UNIT]['work'])
        owners={item['funding_owner'] for g in proposal['groups'] for c in g['components'] for item in c['funding']}
        self.assertEqual(owners,{UNIT,'process-management-java-spring','professional-it-java-spring'})
        bad=deepcopy(self.docs['engineering'])
        bad['groups'][0]['components'][0]['funding_refs'].append('absent-mechanism')
        with self.assertRaisesRegex(ValueError,'Unknown or duplicated reuse mechanism'):
            project_engineering(self.spec,bad,self.revision,self.funding)
