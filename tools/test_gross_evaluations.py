"""Phase readers preserve adopted economics and isolate the OSS proposal."""
from copy import deepcopy
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gross_evaluations import build_gross_evaluations, dependencies, validate_proposal, SOURCE
from study_snapshot import candidate, pack_content, unpack_content
from test_support import reference_study
from validate_stacks import ROOT, read


class GrossEvaluationsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = reference_study()
        cls.reading = cls.study.content['gross_evaluations']
        cls.spec = read(ROOT/SOURCE)
        cls.proof = read(ROOT/cls.spec['proposal']['path'])
        cls.units = cls.study.economic['options'][0]['core_units']

    def test_three_phase_nine_option_readings_and_mirrored_navigation(self):
        phases = ('acquisition','integration','fonctionnement')
        self.assertEqual(tuple(self.reading['phases']),phases)
        for phase in phases:
            self.assertEqual(tuple(self.reading['phases'][phase]['options']),('java-spring','microsoft','sap'))
            self.assertEqual(self.study.ui['essential']['pages']['charges-'+phase],self.study.ui['essential']['pages'][phase])
        groups=[g for g in self.study.ui['essential']['nav_groups'] if not g.get('hidden')]
        i=next(i for i,g in enumerate(groups) if g['label']=='Framework d’évaluation')
        self.assertEqual(groups[i+1]['items'],['charges-'+p for p in phases])

    def test_proposal_is_distinct_and_all_lots_reconcile(self):
        core=self.reading['phases']['acquisition']['options']['java-spring']['core']
        self.assertEqual((core['adopted_jh'],core['proposal_jh'],core['delta_jh']),(6660,5950,-710))
        self.assertEqual([r['proposal_jh'] for r in core['rows']],[1500,340,190,50,170,250,530,420,1960,160,380])
        self.assertEqual(core['status'],'proposal_not_adopted')
        for row in core['rows']:
            self.assertEqual(len(row['references']),4)
            self.assertEqual(row['rationale'],self.spec['unit_arbitrations'][row['id']])
        self.assertEqual(sum(u['total_jh'] for u in self.units),6660)

    def test_malformed_or_obsolete_proposal_is_rejected(self):
        for kind in ('adopted','duplicate','negative','nonfinite','total','difference','scope','decision'):
            proof=deepcopy(self.proof)
            if kind=='adopted':proof['status']='adopted'
            if kind=='duplicate':proof['units'][1]=deepcopy(proof['units'][0])
            if kind=='negative':proof['units'][0]['proposal_jh']=-1
            if kind=='nonfinite':proof['units'][0]['proposal_jh']=float('nan')
            if kind=='total':proof['proposal_jh']+=1
            if kind=='difference':proof['units'][0]['delta_jh']+=1
            if kind=='scope':proof['units'][0]['capabilities']=[]
            if kind=='decision':proof['units'][0]['adopted_jh']+=1
            with self.subTest(kind=kind),self.assertRaisesRegex(ValueError,'ERR_GROSS_EVALUATIONS'):
                validate_proposal(proof,self.units,self.spec)

    def test_proof_fingerprints_and_download_dependencies(self):
        files=dependencies()
        self.assertTrue(files<=self.study.files)
        self.assertIn(self.spec['proposal']['path'],files)
        altered=deepcopy(self.spec);altered['proposal']['sha256']='0'*64
        original=read
        with patch('gross_evaluations.read',side_effect=lambda p:altered if p==ROOT/SOURCE else original(p)):
            with self.assertRaisesRegex(ValueError,'fingerprint mismatch'):dependencies()

    def test_buy_selection_not_mistaken_for_free_or_a_supplier_price(self):
        for slug in ('microsoft','sap'):
            reading=self.reading['phases']['acquisition']['options'][slug]
            self.assertEqual(reading['total_jh'],110)
            self.assertEqual(len(reading['groups'][0]['rows']),6)
            self.assertEqual(reading['quotes'][0]['entries'],[])
            self.assertIsNone(self.reading['phases']['integration']['options'][slug]['total_jh'])

    def test_integration_uses_retained_work_and_replacements_once(self):
        reading=self.reading['phases']['integration']['options']['java-spring']
        groups={g['id']:g for g in reading['groups']}
        work={r['id']:r['value'] for r in groups['common']['rows']}
        self.assertEqual(work['INT-006'],420)
        self.assertEqual(work['INT-007'],280)
        self.assertNotIn('INT-012',work)
        self.assertNotIn('INT-013',work)
        self.assertEqual(sum(r['value'] for r in groups['deployment']['rows']),1200)
        self.assertEqual(sum(r['value'] for r in groups['programme']['rows']),810)
        self.assertEqual(reading['total_jh'],3935)
        self.assertEqual([r['unit'] for r in groups['coordination']['rows']],['€ HT','€ HT'])
        ledger={r['id']:r['amount'] for r in self.study.baseline['options'][0]['funding_ledger']}
        for row in groups['coordination']['rows']:self.assertEqual(row['value'],ledger[row['id']])

    def test_annual_services_and_source_years_preserve_their_periods(self):
        annual=self.reading['phases']['fonctionnement']['options']
        self.assertAlmostEqual(annual['java-spring']['total_jh'],1421.857142857143)
        self.assertEqual(annual['java-spring']['total_unit'],'JH/an')
        for slug in ('microsoft','sap'):
            quote=next(q for q in annual[slug]['quotes'] if q['id']=='grouped_buy')
            self.assertEqual([y['year'] for y in quote['entries'][0]['amounts']],[1,2,3,4,5])
            self.assertIsNone(annual[slug]['total_jh'])
            self.assertEqual(len({q['id'] for q in annual[slug]['quotes']}),len(annual[slug]['quotes']))
        self.assertNotIn('operations_support',[q['id'] for q in annual['microsoft']['quotes']])
        support=next(q for q in self.reading['phases']['integration']['options']['microsoft']['quotes'] if q['id']=='operations_support')['entries'][0]
        self.assertEqual(len(support['amounts']),1)
        self.assertIn('seulement',support['period'])
        self.assertEqual(annual['java-spring']['groups'][-1]['rows'][2]['value'],0)

    def test_frozen_content_survives_snapshot_and_is_not_in_initial_payload(self):
        packed=pack_content(self.study.content)
        self.assertEqual(unpack_content(packed)['gross_evaluations'],self.reading)
        self.assertNotIn('gross_evaluations',self.study.bootstrap(essential=True)['content'])
        before=deepcopy(self.study.baseline)
        bundle=candidate(self.study)
        restored=type(self.study).from_release(bundle)
        with patch.object(Path,'read_bytes',side_effect=AssertionError('unexpected disk read')):
            self.assertEqual(restored.content['gross_evaluations'],self.reading)
            self.assertEqual(restored.simulate(restored.parameters),before)
        self.assertEqual(self.study.baseline,before)

    def test_current_interface_basis_and_detailed_scope_remain_traceable(self):
        row=next(r for r in self.reading['phases']['integration']['options']['java-spring']['groups'][0]['rows'] if r['id']=='INT-006')
        self.assertEqual([f['value'] for f in row['factors']],[40,10.5])
        self.assertEqual(row['value'],40*10.5)
        self.assertNotIn('Diagnostic uniquement',row['note'])
        core=self.reading['phases']['acquisition']['options']['java-spring']['core']
        self.assertEqual(sum(r['jh'] for r in core['roles']),core['adopted_jh'])
        for row in core['rows']:
            self.assertEqual(sum(r['jh'] for r in row['detail']['roles']),row['adopted_jh'])
            self.assertTrue(row['detail']['includes'] and row['detail']['excludes'])
            self.assertIn(row['detail']['proof']['path'],self.study.files)

    def test_annual_pilotage_is_copied_without_inventing_human_effort(self):
        annual=self.reading['phases']['fonctionnement']['options']['java-spring']
        row=next(g for g in annual['groups'] if g['id']=='annual-coordination')['rows'][0]
        source=next(o for o in self.study.content['economic_evaluations']['options'] if o['stack']=='java-spring')['annual']['breakdown']
        expected=next(r['montant'] for g in source for r in g['items'] if r['id']=='pilotage')
        self.assertEqual(row['value'],expected)
        self.assertEqual(row['unit'],'€ HT/an')
        self.assertAlmostEqual(annual['total_jh'],1421.857142857143)
        terms=annual['groups'][0]['rows'][0]['terms']
        self.assertAlmostEqual(sum(r['quantity']*r['unit_jh'] for r in terms),annual['groups'][0]['rows'][0]['value'])

    def test_no_editorial_semicolons_in_new_reader(self):
        def texts(v):
            if isinstance(v,str):yield v
            elif isinstance(v,dict):
                for value in v.values():yield from texts(value)
            elif isinstance(v,list):
                for value in v:yield from texts(value)
        self.assertFalse([s for s in texts(self.reading) if ';' in s])
