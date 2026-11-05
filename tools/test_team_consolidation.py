"""Working estimates, coverage, versioned contributions and nullable consolidation."""
from copy import deepcopy
from decimal import Decimal
import unittest
from jsonschema import ValidationError
from validate_stacks import ROOT, read
from test_support import reference_study
from work_estimation import quantity_estimate
from work_units import build_work_units
from team_consolidation import consolidate, SOURCE, project


class TeamConsolidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study=reference_study();cls.org=cls.study.content['delivery_organisation']

    def fixture(self):
        units=[];selections=[];assignments=[]
        for i,phase in enumerate(('acquisition','integration','fonctionnement')):
            uid='test/'+phase
            inputs=dict(deliverable='Livrable de contrôle',acceptance=['Recette'],quantity=2,count_unit='objets',counting_rule='Une fois',quantity_basis='Inventaire',roles=[dict(id='dev',label='Développement',fixed_jh=1,unit_jh=2,gain_pct=20,rate_ref=None,rate_eur_jh=500)],expenses_eur_ht=100,assumptions=['Contrôle'],evidence_refs=['test'],cost_mode='human',unit_price_eur_ht=None,billing_period='year' if i==2 else 'once',included_in_ref=None)
            units.append(dict(id=uid,label=phase,phase_ref=phase,recurrence='annual' if i==2 else 'initial',measurements=[],estimation=dict(version=1,scope=dict(deliverable='Contrôle',acceptance=['Contrôle']),proposal=dict(inputs=inputs,result=quantity_estimate(inputs)),reference=dict(roles=[]),cost_bridge=[])))
            selections.append(dict(work_unit_ref=uid,estimate_source='proposal',estimate_version=1,work_kind='mixed',accounting='additional',basis='Périmètre nouveau confirmé',period=dict(start_month=i*12,end_month=(i+1)*12,billing_period=None)))
            for measure,component in [('effort','dev'),('cost','expense:non-labour')]:
                assignments.append(dict(id=uid+'/'+measure,work_unit_ref=uid,phase_ref=phase,measure=measure,component_ref=component,shares=[dict(team_ref='master-data',share_pct=100,contribution_kind='technical',basis='Contrôle')],basis='Contrôle',estimate_source='proposal',estimate_version=1))
        org=dict(teams=[dict(id='master-data')],reading=dict(service_start_month=24),work_catalog=dict(units=units,abaque=read(ROOT/'source/abaque-ventilation.yaml')))
        scenario=dict(version=1,id='test',option_ref='java-spring',selections=selections,assignments=assignments,coverage_groups=[],scope_reviews=[dict(phase_ref=p,complete=True,basis='Inventaire complet') for p in ('acquisition','integration','fonctionnement')],projection=dict(start_month=0,end_month=36,price_basis='source_constant'))
        return org,scenario

    def reprice(self,u):
        u['estimation']['proposal']['result']=quantity_estimate(u['estimation']['proposal']['inputs'])

    def test_matrix_detail_conservation_and_immutable_reference(self):
        org=deepcopy(self.org);before=deepcopy(org)
        result=consolidate(org)
        self.assertEqual(org,before)
        for row in result['reference']['rows']:
            retained=next(r for r in org['allocation_table']['rows'] if r['phase_ref']==row['phase_ref'] and (r['owner_kind']=='governance' if row['team_ref']=='governance' else r['owner_kind']=='unallocated' if row['team_ref'] is None else r['team_ref']==row['team_ref']))
            self.assertEqual(row['source_jh'],retained['jh'])
            self.assertEqual(row['cost_eur_ht'],retained['cost_eur_ht'])
        for mode in ('reference','working'):
            for row in result[mode]['rows']:
                pieces=[r for r in result[mode]['contributions'] if r['id'] in row['contribution_ids']]
                self.assertEqual(len(pieces),len(row['contribution_ids']))
                for f in ('source_jh','gross_jh','net_jh','cost_eur_ht'):
                    known=[Decimal(str(p[f])) for p in pieces if p[f] is not None]
                    self.assertEqual(row[f],float(sum(known)) if known else None)
        self.assertTrue(all(r['status']=='partial' for r in result['working']['rows']))
        self.assertTrue(all('scope' in r['missing'] for r in result['working']['rows']))

    def test_three_phases_complete_from_the_same_versioned_contributions(self):
        org,s=self.fixture();before=deepcopy((org,s));r=consolidate(org,s)
        self.assertEqual((org,s),before)
        for row in r['working']['rows']:
            if row['team_ref']=='master-data':
                self.assertEqual(row['status'],'complete');self.assertEqual(row['missing'],[])
                self.assertEqual(row['gross_jh'],5);self.assertEqual(row['net_jh'],4)
                self.assertEqual(row['cost_eur_ht'],2100)
        self.assertEqual([t['projected_cost_eur_ht'] for t in r['working']['totals']],[2100]*3)
        self.assertTrue(all(r['estimate_version']==1 for r in r['working']['contributions']))

    def test_proposal_only_integration_accepts_versioned_role_assignment(self):
        org,s=self.fixture();r=consolidate(org,s)
        integration=[p for p in r['working']['contributions'] if p['phase_ref']=='integration']
        self.assertEqual(sum(p['net_jh'] or 0 for p in integration),4)
        self.assertEqual(sum(p['cost_eur_ht'] for p in integration),2100)
        s['assignments'][2]['estimate_version']=2
        with self.assertRaisesRegex(ValueError,'version mismatch'):consolidate(org,s)

    def test_unpriced_assigned_roles_keep_null_and_actor(self):
        org,s=self.fixture();u=org['work_catalog']['units'][1]
        u['estimation']['proposal']['inputs']['roles'][0]['unit_jh']=None;self.reprice(u)
        r=consolidate(org,s)
        row=next(r for r in r['working']['rows'] if r['team_ref']=='master-data' and r['phase_ref']=='integration')
        self.assertIsNone(row['net_jh']);self.assertEqual(row['cost_eur_ht'],100)
        self.assertIn('effort',row['missing']);self.assertIn('valuation',row['missing']);self.assertEqual(row['status'],'partial')

    def test_role_split_gross_net_fees_and_cents(self):
        org,s=self.fixture();org['teams'].append(dict(id='paas'))
        share=s['assignments'][0]['shares'][0];share['share_pct']=33.33
        share2=dict(share,team_ref='paas',share_pct=66.67);s['assignments'][0]['shares'].append(share2)
        r=consolidate(org,s);rows=[r for r in r['working']['rows'] if r['phase_ref']=='acquisition']
        self.assertEqual(sum(Decimal(str(r['cost_eur_ht'])) for r in rows if r['cost_eur_ht'] is not None),Decimal('2100'))
        md=next(r for r in rows if r['team_ref']=='master-data')
        self.assertAlmostEqual(md['gross_jh'],5*.3333);self.assertAlmostEqual(md['net_jh'],4*.3333)
        self.assertEqual(md['cost_eur_ht'],766.6)

    def test_shared_reference_details_follow_contributions_instead_of_owner(self):
        org=deepcopy(self.org);a=read(ROOT/'source/abaque-ventilation.yaml')
        a['overrides']=[dict(id='shared',work_unit_ref='maintenance/MAI-003',phase_ref='fonctionnement',measure='effort',component_ref='developpement',shares=[dict(team_ref='master-data',share_pct=50,contribution_kind='technical',basis='Test')],basis='Test')]
        org['work_catalog']=build_work_units(self.study.economic,org,abaque=a)
        r=consolidate(org);pieces=[p for p in r['reference']['contributions'] if p['work_unit_ref']=='maintenance/MAI-003' and p['team_ref']=='master-data']
        self.assertEqual(sum(p['source_jh'] or 0 for p in pieces),120)
        self.assertEqual(sum(p['net_jh'] or 0 for p in pieces),108)
        self.assertEqual(sum(p['cost_eur_ht'] or 0 for p in pieces),59400)

    def test_confirmed_replacement_excludes_envelope_pending_is_quarantined(self):
        org,s=self.fixture();parent=deepcopy(org['work_catalog']['units'][0]);parent['id']='test/envelope';parent['estimation']['proposal']['inputs']['expenses_eur_ht']=900;self.reprice(parent)
        org['work_catalog']['units'].append(parent)
        sel=deepcopy(s['selections'][0]);sel['work_unit_ref']=parent['id'];s['selections'].append(sel)
        for assignment in deepcopy(s['assignments'][:2]):
            assignment['id']+='parent';assignment['work_unit_ref']=parent['id'];s['assignments'].append(assignment)
        s['coverage_groups']=[dict(id='replacement',replaced_refs=[parent['id']],replacing_refs=[s['selections'][0]['work_unit_ref']],confirmed=None,basis=None,remaining_work_refs=[])]
        r=consolidate(org,s)
        self.assertEqual(r['working']['totals'][0]['cost_eur_ht'],2900)
        self.assertEqual(sum(p['cost_eur_ht'] or 0 for p in r['working']['pending_contributions']),2100)
        s['coverage_groups'][0].update(confirmed=True,basis='Détail exhaustif accepté')
        r=consolidate(org,s)
        self.assertEqual(r['working']['totals'][0]['cost_eur_ht'],2100)
        self.assertEqual(r['working']['excluded_work_units'],[parent['id']])
        s['coverage_groups'].append(deepcopy(s['coverage_groups'][0]))
        with self.assertRaisesRegex(ValueError,'Overlapping'):consolidate(org,s)

    def test_coverage_rejects_cross_phase_unknown_and_self(self):
        for replaced,replacing in [('test/acquisition','test/integration'),('test/acquisition','unknown'),('test/acquisition','test/acquisition')]:
            org,s=self.fixture();s['coverage_groups']=[dict(id='bad',replaced_refs=[replaced],replacing_refs=[replacing],confirmed=True,basis='Test',remaining_work_refs=[])]
            with self.assertRaises(ValueError):consolidate(org,s)

    def test_nonhuman_purchase_and_monthly_resource_usage(self):
        org,s=self.fixture();u=org['work_catalog']['units'][2];p=u['estimation']['proposal']['inputs']
        s['selections'][2]['work_kind']='expense'
        p.update(cost_mode='resource_usage',roles=[],quantity=10,unit_price_eur_ht=3,expenses_eur_ht=2,billing_period='month');self.reprice(u)
        s['assignments']=s['assignments'][:4]+[dict(s['assignments'][5],component_ref='expense:total')]
        r=consolidate(org,s);total=r['working']['totals'][2]
        self.assertEqual(total['cost_eur_ht'],384);self.assertIsNone(total['net_jh']);self.assertEqual(total['projected_cost_eur_ht'],384)
        p.update(cost_mode='fixed_purchase',expenses_eur_ht=150,billing_period='year');self.reprice(u)
        self.assertEqual(consolidate(org,s)['working']['totals'][2]['cost_eur_ht'],150)
        p['expenses_eur_ht']=None;self.reprice(u)
        self.assertIsNone(consolidate(org,s)['working']['totals'][2]['cost_eur_ht'])

    def test_period_incompatible_billing_and_horizon_stay_unknown(self):
        org,s=self.fixture();s['projection']['end_month']=None
        self.assertTrue(all(t['projected_cost_eur_ht'] is None for t in consolidate(org,s)['working']['totals']))
        s['selections'][2]['period']['billing_period']='once'
        r=consolidate(org,s)
        self.assertIsNone(r['working']['totals'][2]['cost_eur_ht'])
        self.assertIn('billing',r['working']['issues']['test/fonctionnement'])
        self.assertEqual(project(100,dict(start_month=0,end_month=12),'initial',dict(start_month=0,end_month=6)),50)
        self.assertEqual(project(120,dict(start_month=12,end_month=36),'annual',dict(start_month=18,end_month=30)),120)

    def test_inclusion_no_fake_jh_or_second_cost_and_cycles_rejected(self):
        org,s=self.fixture();included=deepcopy(org['work_catalog']['units'][0]);included['id']='test/included'
        included['estimation']['proposal']['inputs'].update(cost_mode='included',roles=[],included_in_ref='test/acquisition');self.reprice(included)
        org['work_catalog']['units'].append(included);sel=deepcopy(s['selections'][0]);sel.update(work_unit_ref=included['id'],accounting='included',work_kind='expense');s['selections'].append(sel)
        r=consolidate(org,s);self.assertEqual(r['working']['totals'][0]['cost_eur_ht'],2100)
        p=next(p for p in r['working']['contributions'] if p['component_kind']=='included');self.assertIsNone(p['net_jh']);self.assertIsNone(p['cost_eur_ht'])
        included['estimation']['proposal']['inputs']['included_in_ref']=included['id'];self.reprice(included)
        with self.assertRaisesRegex(ValueError,'Invalid inclusion'):consolidate(org,s)

    def test_scope_and_unallocated_are_not_complete(self):
        org,s=self.fixture();s['scope_reviews'][0]['complete']=None;s['assignments'][0]['shares'][0]['share_pct']=50
        r=consolidate(org,s)
        md=next(r for r in r['working']['rows'] if r['phase_ref']=='acquisition' and r['team_ref']=='master-data')
        self.assertIn('scope',md['missing']);self.assertIn('assignment',md['missing']);self.assertEqual(md['status'],'partial')
        remainder=next(r for r in r['working']['rows'] if r['phase_ref']=='acquisition' and r['team_ref'] is None)
        self.assertEqual(remainder['net_jh'],2);self.assertEqual(remainder['cost_eur_ht'],1000)

    def test_scenario_schema_unknown_selection_component_and_versions(self):
        org,s=self.fixture();s['selections'][0]['estimate_version']=2
        with self.assertRaisesRegex(ValueError,'version'):consolidate(org,s)
        org,s=self.fixture();s['assignments'][0]['component_ref']='absent'
        with self.assertRaisesRegex(ValueError,'Unknown assignment component'):consolidate(org,s)
        org,s=self.fixture();s['selections'].pop()
        with self.assertRaisesRegex(ValueError,'Select every'):consolidate(org,s)


    def test_reference_monetary_components_reconcile_each_piece(self):
        c=consolidate(self.org)
        for row in c['reference']['contributions']:
            if row['cost_eur_ht'] is not None:
                self.assertAlmostEqual(sum(row.get(k) or 0 for k in ('labour_eur_ht','non_labour_eur_ht','unclassified_eur_ht')),row['cost_eur_ht'],places=2)

    def test_component_applicability_never_turns_an_unknown_envelope_into_not_applicable(self):
        c=consolidate(self.org)
        unknown=next(r for r in c['reference']['contributions'] if r['work_unit_ref']=='funding/travaux_communs' and r['unclassified_eur_ht'] is not None)
        self.assertIsNone(unknown['labour_eur_ht']);self.assertIsNone(unknown['non_labour_eur_ht'])
        self.assertTrue(all(unknown['component_applicability'].values()))
        core=next(r for r in c['reference']['contributions'] if r['work_unit_ref']=='core/master-data-java-spring')
        self.assertIsNone(core['unclassified_eur_ht'])
        self.assertFalse(core['component_applicability']['unclassified_eur_ht'])
        self.assertIsNotNone(core['labour_eur_ht']);self.assertIsNotNone(core['non_labour_eur_ht'])

    def test_bootstrap_snapshot_export_and_canonical_graph(self):
        from study_snapshot import ENGINE_FILES,candidate
        from team_consolidation import dependencies
        self.assertIn('team_consolidation.py',ENGINE_FILES)
        self.assertTrue(dependencies()<=self.study.files)
        self.assertIn(SOURCE,candidate(self.study)['payload']['documents'])
        self.assertEqual(self.study.organisation_reading()['delivery_organisation']['team_consolidations'],self.org['team_consolidations'])
        ids={o['id'] for o in self.study.fundamentals['estimation_model']['objects']}
        self.assertTrue({'estimate_selection','scope_coverage','work_expense','team_estimation_reading'}<=ids)


    def test_enabling_and_nonfinite_period_guards(self):
        org,s=self.fixture();org['teams'][0]['type']='enabling'
        with self.assertRaisesRegex(ValueError,'Enabling contribution'):consolidate(org,s)
        org,s=self.fixture();s['selections'][0]['period']['start_month']=float('nan')
        with self.assertRaises(ValueError):consolidate(org,s)

    def test_full_catalog_proposal_flows_into_working_without_adoption(self):
        org=deepcopy(self.org);source=read(ROOT/'source/unites-travail.yaml')
        uid='integration-detail/authority';unit=next(u for u in source['units'] if u['id']==uid)
        unit['estimation_contract']['proposal']=self.fixture()[0]['work_catalog']['units'][1]['estimation']['proposal']['inputs']
        org['work_catalog']=build_work_units(self.study.economic,org,source=source)
        spec=read(ROOT/SOURCE);sel=next(s for s in spec['selections'] if s['work_unit_ref']==uid)
        sel.update(accounting='additional',basis='Nouveau périmètre confirmé',period=dict(start_month=12,end_month=24,billing_period='once'))
        spec['assignments']=[dict(a,id='full/'+a['id'],work_unit_ref=uid) for a in self.fixture()[1]['assignments'][2:4]]
        result=consolidate(org,spec)
        rows=[r for r in result['working']['contributions'] if r['work_unit_ref']==uid]
        self.assertEqual(sum(r['cost_eur_ht'] for r in rows),2100)
        self.assertEqual(sum(r['net_jh'] or 0 for r in rows),4)
        self.assertEqual(org['allocation_table'],self.org['allocation_table'])
        self.assertEqual(result['reference']['totals'],self.org['team_consolidations']['reference']['totals'])


    def test_expense_contributor_needs_no_fake_workload(self):
        org=deepcopy(self.org);spec=read(ROOT/SOURCE)
        unit=next(u for u in org['work_catalog']['units'] if u['id'].startswith('core/') and u['measurements'])
        uid=unit['id']
        base=dict(work_unit_ref=uid,phase_ref=unit['phase_ref'],basis='Test',estimate_source='reference',estimate_version=1)
        spec['assignments']=[dict(base,id='all-roles',measure='effort',component_ref='*',shares=[dict(team_ref='master-data',share_pct=100,contribution_kind='technical',basis='Test')]),dict(base,id='fees',measure='cost',component_ref='expense:non-labour',shares=[dict(team_ref='paas',share_pct=100,contribution_kind='platform',basis='Test')])]
        result=consolidate(org,spec)
        row=next(r for r in result['working']['contributions'] if r['work_unit_ref']==uid and r['team_ref']=='paas')
        self.assertFalse(row['human_applicable']);self.assertIsNone(row['net_jh'])
        self.assertEqual(row['labour_eur_ht'],0)
        self.assertNotIn('effort',result['working']['issues'][uid])

    def test_separate_effort_and_funding_records_are_not_missing_prices(self):
        result=consolidate(self.org)
        unit=next(u for u in self.org['work_catalog']['units'] if u['id'].startswith('governance/') and u['phase_ref']=='acquisition' and len(u['measurements'])>1)
        self.assertNotIn('valuation',result['working']['issues'][unit['id']])
        self.assertNotIn('kind',result['working']['issues'][unit['id']])
        effort=next(r for r in result['working']['contributions'] if r['work_unit_ref']==unit['id'] and r['source_jh'] is not None)
        self.assertFalse(effort['cost_applicable'])


if __name__=='__main__':unittest.main()
