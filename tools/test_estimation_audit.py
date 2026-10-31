"""Regression cases from the business-model / dual-estimator audit."""
from copy import deepcopy
import unittest
from unittest.mock import patch
from jsonschema import ValidationError
from model_context import model_session
from estimation_inputs import registry, contract, load_proofs, validate_binding
from estimation_preparation import prepare
from estimation_calculation import formula, calculate, evaluate_rule
from retained_core import validate, coverage
from export_business_model import compose
from validate_stacks import ROOT, read


class AuditCorrectionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with model_session() as snapshot:
            cls.unit=validate()['units'][0]
            cls.spec,cls.registry=contract(cls.unit['calculation'])
            cls.proofs=load_proofs(cls.registry)
            cls.result=calculate(cls.unit['calculation'])
            cls.bundle=compose(snapshot.documents,snapshot.digests)

    def prepared(self, change=None):
        docs=deepcopy(self.proofs)
        inputs={key:docs[path] for key,path in self.spec['inputs'].items()}
        if change:change(inputs)
        with model_session():
            return prepare(docs,self.spec,self.registry,formula)

    def test_reconstructed_counts_and_costs(self):
        p=self.prepared()
        self.assertEqual(p['trace']['recorded_files'],2060)
        self.assertEqual(p['trace']['CFP'],420)
        self.assertEqual(p['trace']['processes'],29)
        self.assertEqual(p['trace']['groups'],42)
        self.assertAlmostEqual(p['trace']['complement_units'],8286.5)
        self.assertAlmostEqual(p['trace']['reuse_factor'],.035)
        self.assertEqual((self.result['total_jh'],self.result['months']),(1500,17))
        self.assertEqual(self.result['alignment']['functional']['jh'],1200)
        self.assertAlmostEqual(sum(self.result['roles'].values()),1500)
        self.assertTrue(all(abs(r['common_jh']+r['complements_jh']-r['jh'])<1e-9 for r in p['rows']))

    def test_clone_or_reassignment_cannot_reuse_master_data_calculation(self):
        for change in (
            lambda u:u.update(id='another-family'),
            lambda u:u.update(stack='rust'),
            lambda u:u.update(capabilities=[dict(id='BC-008',native_id='policy-scope-and-rollout')]),
            lambda u:u['includes'].append('new scope'),
        ):
            unit=deepcopy(self.unit);change(unit)
            with self.assertRaises(ValueError):validate_binding(unit)
        doc=registry();doc['calculations'][0]['scope']['native_id']='invented'
        with self.assertRaisesRegex(ValueError,'hierarchy'):validate_binding(self.unit,doc)
        doc=registry();doc['calculations'][0]['scope']['analysis_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'scope changed'):validate_binding(self.unit,doc)

    def test_shared_mechanism_cannot_be_funded_twice(self):
        doc=registry();clone=deepcopy(doc['calculations'][0]);clone.update(id='other',unit_id='another-family')
        doc['calculations'].append(clone)
        with self.assertRaisesRegex(ValueError,'already owned'):registry(doc)
        doc=registry();alias=deepcopy(doc['mechanisms'][0]);alias['id']='alias'
        doc['mechanisms'].append(alias)
        with self.assertRaisesRegex(ValueError,'multiple mechanism'):registry(doc)
        doc=registry();doc['calculations'][0]['funding_claims'].append(deepcopy(doc['calculations'][0]['funding_claims'][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate funding'):registry(doc)
        doc=registry();doc['consolidation']['integrated_core_estimate']=True
        with self.assertRaisesRegex(ValueError,'not implemented'):registry(doc)

    def test_invalid_numeric_and_activity_inputs_are_rejected(self):
        def phase(d):
            d['activities']['cocomo']['activities'][0]['percent_by_phase'].append(999)
            d['baseline']['activity_source']=deepcopy(d['activities']['cocomo'])
        changes=[
            lambda d:d['allocation']['activity_role_weights']['environment'].update(plateforme=-.1,dev_java=1.1),
            phase,
            lambda d:d['baseline']['functional'].update(day_hours=8),
            lambda d:d['baseline']['rows'][0].update(common_jh=1,flow_complements_jh=1),
            lambda d:d['native_measures']['files'][0].update(program_units=-1),
            lambda d:d['native_measures']['files'].append(deepcopy(d['native_measures']['files'][0])),
            lambda d:d['refinements'][0].update(proposed_units=999),
            lambda d:d['allocation'].update(role_rounding_jh=0),
            lambda d:d['complement_inputs']['configuration'][0].update(quantity=float('nan')),
        ]
        for change in changes:
            with self.subTest(change=change):
                with self.assertRaises((ValueError,ValidationError)):self.prepared(change)
        with self.assertRaises((ValueError,ValidationError)):formula('cosmic_effort',CFP=-420,hours_per_CFP=20,factor=1,day_hours=7)
        with self.assertRaises((ValueError,ValidationError)):formula('cosmic_effort',CFP=420,hours_per_CFP=20,factor=1,day_hours=0)

    def test_cosmic_structure_and_counts_are_recomputed(self):
        for change in (
            lambda d:d['cosmic']['processes'][0]['movements'][0].update(group='absent'),
            lambda d:d['cosmic']['processes'][0]['movements'].append(deepcopy(d['cosmic']['processes'][0]['movements'][0])),
            lambda d:d['cosmic']['processes'][0]['count'].update(cfp=999),
        ):
            with self.assertRaises(ValueError):self.prepared(change)

    def test_evidence_hashes_and_dependency_graph_are_enforced(self):
        doc=registry();path=self.spec['inputs']['native_measures'];doc['proofs'][path]['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'evidence changed'):load_proofs(doc)
        doc=registry();doc['proofs'][self.spec['inputs']['baseline']]['dependencies']=[]
        with self.assertRaisesRegex(ValueError,'dependency declaration'):load_proofs(doc)

    def test_download_is_sufficient_for_both_calculations_preparation(self):
        bundle=self.bundle
        self.assertEqual(bundle['format_version'],2)
        self.assertEqual(set(self.proofs),set(bundle['evidence']))
        self.assertFalse(any(p.startswith('audits/') for p in bundle['model']))
        rules={r['id']:r for r in bundle['metamodel']['estimation_model']['rules']}
        reg=bundle['model']['source/calculs-estimation-core.yaml']
        def evaluate(id,**values):return evaluate_rule(rules[id],**values)
        with patch('validate_stacks.read',side_effect=AssertionError('No disk input allowed')):
            p=prepare(bundle['evidence'],reg['calculations'][0],reg,evaluate)
        self.assertEqual(p['trace']['CFP'],420)
        self.assertAlmostEqual(p['rows'][3]['jh'],1496.947499268186)
        self.assertTrue(set(self.registry['proofs'])<=set(bundle['evidence']))

    def test_comparability_and_consolidation_are_not_probabilities(self):
        a=self.result['alignment']
        self.assertEqual(a['comparability_status'],'partial_scope_conventional_activities_unverified_service')
        self.assertIn('native_excess',{r['classification'] for r in a['comparison']['scope_rows']})
        self.assertEqual(a['comparison']['service_status'],'unverified')
        self.assertGreater(a['shared_complements_pct'],58)
        self.assertEqual(self.result['consolidation']['schedule_aggregation'],'none')
        self.assertFalse(self.result['consolidation']['integrated_core_estimate'])

    def test_full_coverage_propagates_to_application_status(self):
        from test_support import study_copy
        study=study_copy()
        option=next(x for x in study.economic['options'] if x['stack']=='java-spring')
        option['core_units'][0]['capabilities']=[dict(id=x['id']) for x in study.content['complexity']['rows']]
        row=next(x for x in study._essential_core_evaluation() if x['stack']=='java-spring')
        self.assertEqual(row['estimation_status'],'fully_estimated')
        self.assertEqual(row['coverage']['status'],'fully_estimated')

    def test_coverage_states_include_full_and_empty(self):
        ids=[f'BC-{i:03}' for i in range(1,89)]
        self.assertEqual(coverage([],[])['status'],'not_applicable')
        self.assertEqual(coverage([],ids)['status'],'pending_reestimation')
        self.assertEqual(coverage([self.unit],ids)['status'],'partially_estimated')
        all_units=[dict(capabilities=[dict(id=x) for x in ids])]
        self.assertEqual(coverage(all_units,ids)['status'],'fully_estimated')
        self.assertEqual(coverage(all_units,ids)['covered_pct'],100)


if __name__=='__main__':unittest.main()
