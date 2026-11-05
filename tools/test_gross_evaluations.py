"""Phase readers preserve adopted economics and isolate the OSS proposal."""
from test_support import active_reference
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
        charge_group=next(g for g in groups if 'charges-acquisition' in g['items'])
        self.assertTrue({'unites-travail','charges-equipes',*('charges-'+p for p in phases)} <= set(charge_group['items']))
        self.assertTrue(any('schema-modele' in g['items'] for g in groups))

    def test_integration_history_is_explicit_without_changing_retained_amounts(self):
        r=self.reading['phases']['integration']['options']['java-spring']
        self.assertEqual(r['workload_status'],'historical_pending_review')
        self.assertTrue(r['workload_note'])
        self.assertEqual(r['total_jh'],sum(g.get('subtotal_jh',0) for g in r['groups']))
        self.assertNotEqual(r['total_label'],self.reading['labels']['human_total'])
        for phase in ('acquisition','fonctionnement'):
            self.assertEqual(self.reading['phases'][phase]['options']['java-spring']['workload_status'],'current')

    def test_proposal_is_distinct_and_all_lots_reconcile(self):
        core=self.reading['phases']['acquisition']['options']['java-spring']['core']
        self.assertEqual((core['adopted_jh'],core['proposal_jh'],core['delta_jh']),(active_reference()['total_jh'],active_reference()['total_jh'],active_reference()['delta_jh']))
        self.assertEqual([r['proposal_jh'] for r in core['rows']],active_reference()['unit_days'])
        self.assertEqual(core['status'],'adopted')
        for row in core['rows']:
            self.assertEqual(len(row['references']),4)
            self.assertEqual(row['rationale'],self.spec['unit_arbitrations'][row['id']])
        self.assertEqual(sum(u['total_jh'] for u in self.units),active_reference()['total_jh'])
        self.assertAlmostEqual(sum(a['jh'] for a in core['activities']),core['adopted_jh'])
        for activity in core['activities']:
            expected=sum(a['jh'] for unit in self.units for a in unit['activities'] if a['id']==activity['id'])
            self.assertAlmostEqual(activity['jh'],expected)

    def test_five_comparisons_are_priced_without_changing_retained_decisions(self):
        from gross_evaluations import value_unit_comparisons
        unit=dict(total_jh=10,tooling_eur_jh=20,roles=[dict(jh=3,rate_eur_jh=800),dict(jh=7,rate_eur_jh=500)],alignment=dict(rows=[dict(id='erpnext',label='ERPNext',jh=10)],functional=dict(id='cosmic-isbsg',label='COSMIC × ISBSG',jh=5)))
        before=deepcopy(unit);rows=value_unit_comparisons(unit)
        self.assertEqual([r['cost_eur_ht'] for r in rows],[6100,3050])
        self.assertEqual(unit,before)
        core=self.reading['phases']['acquisition']['options']['java-spring']['core']
        self.assertEqual(len(core['rows']),len(active_reference()['units']))
        for row in core['rows']:
            self.assertEqual(len(row['comparisons']),5)
            self.assertEqual({r['id'] for r in row['comparisons']},{'erpnext','odoo','tryton','axelor','cosmic-isbsg'})
        master=next(r for r in core['rows'] if r['id']=='master-data-java-spring')
        self.assertEqual(master['adopted_cost_eur_ht'],active_reference()['units']['master-data-java-spring']['cost_eur_ht'])
        self.assertIsNone(next(r['cost_eur_ht'] for r in master['comparisons'] if r['id']=='cosmic-isbsg'))
        historic=next(r for r in master['detail']['historical_comparisons'] if r['id']=='cosmic-isbsg')
        self.assertEqual(historic['jh'],1200)
        adopted=active_reference()['units']['master-data-java-spring']
        self.assertEqual(historic['cost_eur_ht'],round(1200*adopted['cost_eur_ht']/adopted['jh'],2))
        self.assertEqual(sum(r['adopted_jh'] for r in core['rows']),active_reference()['total_jh'])
        self.assertEqual([t['id'] for t in core['comparison_totals']],[r['id'] for r in core['rows'][0]['comparisons']])
        for total in core['comparison_totals']:
            values=[next(c['jh'] for c in row['comparisons'] if c['id']==total['id']) for row in core['rows']]
            if None in values:self.assertIsNone(total['jh'])
            else:self.assertAlmostEqual(total['jh'],sum(values))

    def test_module_analysis_distinguishes_interface_work_from_incremental_functional_size(self):
        core=self.reading['phases']['acquisition']['options']['java-spring']['core']
        rows={r['id']:r for r in core['rows']}
        self.assertEqual(core['analysis_order'][:3],['process-management-java-spring','supply-workbenches-java-spring','supply-controls-java-spring'])
        self.assertEqual(len(core['analysis_order']),len(set(core['analysis_order'])))
        self.assertEqual(set(core['analysis_order']),set(rows))
        process=rows['process-management-java-spring']['detail']['analysis_metrics']
        visual=rows['supply-workbenches-java-spring']['detail']['analysis_metrics']
        self.assertEqual((process['CFP'],visual['CFP']),(216,5))
        self.assertAlmostEqual(process['cosmic_jh'],617.1428571428571)
        self.assertAlmostEqual(visual['cosmic_jh'],14.285714285714286)
        self.assertAlmostEqual(process['implied_hours_per_CFP'],63.5065119384794)
        self.assertAlmostEqual(visual['implied_hours_per_CFP'],227.26689552639013)
        # The five-point result excludes the four business functions already consumed.
        from core_product_estimate import load_inputs,functional_forecast
        _,inputs=load_inputs()
        visual_processes=inputs['cosmic']['processes']['supply-workbenches']
        self.assertEqual([p['id'] for p in visual_processes if p['scope']=='new'],['layout'])
        self.assertEqual({p['id'] for p in visual_processes if p['scope']=='existing_function_consumed'},{'plan','compare','service','act'})
        f=functional_forecast(inputs)
        self.assertEqual([f['CFP_by_group'][g] for g in ('process-studio','human-forms','analytics-mining')],[49,44,47])
        for row in rows.values():
            self.assertEqual(set(row['detail']['analysis']),{'finding','oss','cosmic','decision','remaining'})
            self.assertTrue(all(row['detail']['analysis'].values()))
            self.assertGreater(row['detail']['analysis_metrics']['CFP'],0)
        self.assertEqual(sum(r['adopted_jh'] for r in rows.values()),active_reference()['total_jh'])
        self.assertEqual((rows['process-management-java-spring']['adopted_cost_eur_ht'],rows['supply-workbenches-java-spring']['adopted_cost_eur_ht']),(active_reference()['units']['process-management-java-spring']['cost_eur_ht'],active_reference()['units']['supply-workbenches-java-spring']['cost_eur_ht']))

    def test_policy_rescan_replaces_the_old_scope_without_adopting_a_budget(self):
        core=self.reading['phases']['acquisition']['options']['java-spring']['core']
        row=next(r for r in core['rows'] if r['id']=='supply-controls-java-spring')
        from gross_evaluations import project_unit_revision
        legacy=read(ROOT/'audits/2026-11-02-audit-politiques-allocation/results.json')
        unit=next(u for u in read(ROOT/'audits/2026-11-02-adoption-perimetre-scenarios/basis.json')['valued_units'] if u['id']==row['id'])
        r=project_unit_revision(legacy,unit)
        r['core_candidate_jh']=5950+r['delta_jh']
        r['proof']={'path':'audits/2026-11-02-audit-politiques-allocation/results.json'}
        self.assertEqual((r['replaced_CFP'],r['policy_CFP'],r['kept_CFP'],r['total_CFP']),(17,103,47,150))
        self.assertAlmostEqual(r['raw_jh'],428.57142857142856)
        self.assertEqual((r['jh'],r['delta_jh'],r['core_candidate_jh']),(430,380,6330))
        self.assertEqual((r['cost_eur_ht'],r['delta_cost_eur_ht']),(270590,239140))
        self.assertEqual(sum(role['jh'] for role in r['roles']),430)
        self.assertEqual(len(r['processes']),13)
        self.assertEqual((row['adopted_jh'],row['adopted_cost_eur_ht'],core['adopted_jh']),(610,active_reference()['units']['supply-controls-java-spring']['cost_eur_ht'],active_reference()['total_jh']))
        self.assertEqual(r['status'],'proposal_not_adopted')
        self.assertIn(r['proof']['path'],self.study.files)
        # Archived rescanned code is the measured code, independent of the checkouts.
        import base64,gzip,hashlib,json
        proof=read(ROOT/r['proof']['path'])
        archive=json.loads(gzip.decompress(base64.b64decode(proof['source_archive']['data'])))
        self.assertEqual(len(archive),14)
        for m in proof['measures']:
            self.assertEqual(hashlib.sha256(base64.b64decode(archive[m['repo']+'/'+m['path']])).hexdigest(),m['sha256'])
        self.assertTrue(all(x['status']=='partial_functional_analogue_not_retained' for x in proof['cocomo_diagnostics']))

    def test_policy_revision_rejects_duplicate_functions_and_double_funding(self):
        from gross_evaluations import project_unit_revision
        core=self.reading['phases']['acquisition']['options']['java-spring']['core']
        row=next(r for r in core['rows'] if r['id']=='supply-controls-java-spring')
        source=read(ROOT/'audits/2026-11-02-audit-politiques-allocation/results.json')
        unit=next(u for u in read(ROOT/'audits/2026-11-02-adoption-perimetre-scenarios/basis.json')['valued_units'] if u['id']==row['id'])
        for kind in ('duplicate','reuse','count','benchmark','adopted','basis'):
            proof=deepcopy(source)
            if kind=='duplicate':proof['processes'].append(deepcopy(proof['processes'][0]))
            if kind=='reuse':proof['kept_process_ids'].append(proof['removed_process_ids'][0])
            if kind=='count':proof['policy_CFP']+=1
            if kind=='benchmark':proof['benchmark']['hours_per_CFP']=30
            if kind=='adopted':proof['status']='adopted'
            if kind=='basis':proof['baseline_jh']=60
            with self.subTest(kind=kind),self.assertRaisesRegex(ValueError,'ERR_GROSS_EVALUATIONS'):
                project_unit_revision(proof,unit)

    def test_adopted_scenario_scope_replaces_the_proposal_panel(self):
        core=self.reading['phases']['acquisition']['options']['java-spring']['core']
        self.assertEqual(core['adopted_jh'],active_reference()['total_jh'])
        self.assertNotIn('revision_summary',core)
        self.assertEqual(self.spec['unit_revisions'],{})
        self.assertTrue(all('revision' not in r['detail'] for r in core['rows']))
        self.assertEqual(sum(r['adopted_cost_eur_ht'] for r in core['rows']),active_reference()['cost_eur_ht'])
        for row in core['rows']:
            if row['id'] in ('supply-controls-java-spring','orders-java-spring','master-plan-java-spring','supply-decisions-java-spring','service-fulfilment-java-spring'):
                self.assertEqual(row['detail']['method'],'COSMIC × ISBSG')

    def test_scenario_prototype_still_rejects_overlap_and_stale_benchmark(self):
        from gross_evaluations import project_unit_revision
        unit=next(u for u in read(ROOT/'audits/2026-11-02-adoption-perimetre-scenarios/basis.json')['valued_units'] if u['id']=='supply-decisions-java-spring')
        source=read(ROOT/'audits/2026-11-02-proposition-perimetre-complete/supply-decisions-java-spring.json')
        for kind in ('duplicate','credit','count','scope','benchmark','status'):
            p=deepcopy(source)
            if kind=='duplicate':p['processes'].append(deepcopy(p['processes'][0]))
            if kind=='credit':p['kept_process_ids']=[p['removed_process_ids'][0]]
            if kind=='count':p['CFP']+=1
            if kind=='scope':p['processes'][0]['capabilities']=['BC-008']
            if kind=='benchmark':p['benchmark']['hours_per_CFP']=30
            if kind=='status':p['status']='adopted'
            with self.subTest(kind=kind),self.assertRaisesRegex(ValueError,'ERR_GROSS_EVALUATIONS'):
                project_unit_revision(p,unit)

    def test_malformed_or_obsolete_proposal_is_rejected(self):
        for kind in ('invalid-status','duplicate','negative','nonfinite','total','difference','scope','decision'):
            proof=deepcopy(self.proof)
            if kind=='invalid-status':proof['status']='invalid'
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
            self.assertEqual(reading['total_jh'],70)
            self.assertEqual(len(reading['groups'][0]['rows']),4)
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
        self.assertEqual(sum(r['value'] for r in groups['programme']['rows']),2700)
        self.assertEqual(reading['total_jh'],5825)
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
            self.assertTrue(row['detail']['includes'] or row['detail']['scope_note'])
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
