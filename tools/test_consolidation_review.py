"""Adversarial review of three-phase consolidation and screen-facing lineage."""
from copy import deepcopy
from decimal import Decimal
import unittest
from team_consolidation import consolidate,SOURCE
import test_team_consolidation as baseline_cases
from test_support import reference_study
from validate_stacks import ROOT,read


class ConsolidationReviewTests(unittest.TestCase):
    def fixture(self):return baseline_cases.TeamConsolidationTests().fixture()
    def reprice(self,u):baseline_cases.TeamConsolidationTests().reprice(u)
    def expense(self,org,s,index=0,mode='resource_usage',price=100,billing='month'):
        u=org['work_catalog']['units'][index];p=u['estimation']['proposal']['inputs']
        p.update(cost_mode=mode,roles=[],quantity=1,unit_price_eur_ht=price,expenses_eur_ht=0 if mode=='resource_usage' else price,billing_period=billing)
        s['selections'][index]['work_kind']='expense';self.reprice(u)
        rule=dict(s['assignments'][index*2+1],component_ref='expense:total')
        s['assignments']=[r for r in s['assignments'] if r['work_unit_ref']!=u['id']]+[rule]
        return u,rule
    def cell(self,r,phase='acquisition',actor='master-data'):
        return next(x for x in r['working']['rows'] if x['phase_ref']==phase and x['team_ref']==actor)

    def test_expense_gap_does_not_invalidate_another_teams_priced_work(self):
        org,s=self.fixture();org['teams'].append(dict(id='paas'));s['assignments'][1]['shares'][0]['team_ref']='paas'
        u=org['work_catalog']['units'][0];u['estimation']['proposal']['inputs']['expenses_eur_ht']=None;self.reprice(u)
        r=consolidate(org,s);human=self.cell(r);expense=self.cell(r,actor='paas')
        self.assertEqual(human['net_jh'],4);self.assertEqual(human['metric_states']['net_jh']['status'],'complete')
        self.assertEqual(human['metric_states']['cost_eur_ht']['status'],'complete')
        self.assertNotIn('valuation',human['missing'])
        self.assertIsNone(expense['cost_eur_ht']);self.assertIn('valuation',expense['metric_states']['cost_eur_ht']['missing'])
        self.assertEqual(expense['metric_states']['net_jh']['status'],'not_applicable')
        self.assertEqual(r['working']['phase_readings'][0]['gaps'][0]['work_unit_refs'],[u['id']])

    def test_monthly_and_yearly_purchases_during_initial_phase(self):
        for billing,price in [('month',100),('year',1200)]:
            org,s=self.fixture();u,_=self.expense(org,s,price=price,billing=billing)
            s['selections'][0]['period'].update(start_month=0,end_month=6)
            r=consolidate(org,s);row=self.cell(r)
            self.assertEqual(row['cost_eur_ht'],600);self.assertIsNone(row['net_jh'])
            self.assertEqual(row['metric_states']['cost_eur_ht']['status'],'complete')
            self.assertEqual(row['metric_states']['net_jh']['status'],'not_applicable')

    def test_unknown_subscription_duration_cannot_create_phase_budget(self):
        org,s=self.fixture();self.expense(org,s);s['selections'][0]['period']['end_month']=None
        row=self.cell(consolidate(org,s));self.assertIsNone(row['cost_eur_ht'])
        self.assertIn('period',row['missing']);self.assertIn('valuation',row['metric_states']['cost_eur_ht']['missing'])

    def test_projection_prorates_once_before_splitting_the_cent(self):
        org,s=self.fixture();org['teams'].append(dict(id='paas'));u,rule=self.expense(org,s,mode='fixed_purchase',price=1.01,billing='once')
        rule['shares']=[dict(rule['shares'][0],share_pct=50),dict(rule['shares'][0],team_ref='paas',share_pct=50)]
        s['projection']['end_month']=6;r=consolidate(org,s)
        self.assertEqual(r['working']['totals'][0]['projected_cost_eur_ht'],.50)
        self.assertEqual(sum(Decimal(str(p['projected_cost_eur_ht'])) for p in r['working']['contributions'] if p['phase_ref']=='acquisition'),Decimal('.50'))
        self.assertEqual(r['working']['totals'][0]['cost_eur_ht'],1.01)

    def test_unconfirmed_scope_is_outside_ledger_but_keeps_its_preview(self):
        org,s=self.fixture();s['selections'][0].update(accounting=None,basis=None)
        r=consolidate(org,s);uid=s['selections'][0]['work_unit_ref']
        self.assertFalse(any(p['work_unit_ref']==uid for p in r['working']['contributions']))
        u=next(u for u in r['working']['unit_readings'] if u['work_unit_ref']==uid)
        self.assertEqual(u['status'],'pending');self.assertEqual(u['contribution_ids'],[])
        self.assertEqual(u['pending_cost_eur_ht'],2100);self.assertIsNone(u['cost_eur_ht'])
        self.assertIn('coverage',self.cell(r)['metric_states']['cost_eur_ht']['missing'])

    def test_remaining_scope_is_explicit_and_must_belong_to_detail(self):
        org,s=self.fixture();old=deepcopy(org['work_catalog']['units'][0]);old['id']='test/envelope';org['work_catalog']['units'].append(old)
        sel=dict(deepcopy(s['selections'][0]),work_unit_ref=old['id']);s['selections'].append(sel)
        group=dict(id='cover',replaced_refs=[old['id']],replacing_refs=['test/acquisition'],confirmed=True,basis='Périmètre revu',remaining_work_refs=None);s['coverage_groups']=[group]
        with self.assertRaisesRegex(ValueError,'remaining scope review'):consolidate(org,s)
        group['remaining_work_refs']=['unknown']
        with self.assertRaisesRegex(ValueError,'Remaining work'):consolidate(org,s)
        group['remaining_work_refs']=[]
        self.assertIn(old['id'],consolidate(org,s)['working']['excluded_work_units'])

    def test_unit_team_and_phase_details_share_the_same_rows(self):
        org,s=self.fixture();r=consolidate(org,s)
        for u in r['working']['unit_readings']:
            detail=[p for p in r['working']['contributions'] if p['work_unit_ref']==u['work_unit_ref']]
            self.assertEqual(u['contribution_ids'],[p['id'] for p in detail])
            self.assertEqual(u['cost_eur_ht'],sum(p['cost_eur_ht'] for p in detail))
            self.assertEqual(u['team_contributions'][0]['net_jh'],u['net_jh'])
            self.assertEqual(u['effective_period'],{k:s['selections'][r['working']['unit_readings'].index(u)]['period'][k] for k in ('start_month','end_month')})
        self.assertTrue(all(p['complete_units']==p['units'] for p in r['working']['phase_readings']))

    def test_scope_and_projection_gaps_do_not_turn_into_known_zero(self):
        org,s=self.fixture();s['scope_reviews'][0]['complete']=None;s['projection']['end_month']=None
        r=consolidate(org,s)
        self.assertIn('scope',self.cell(r)['metric_states']['cost_eur_ht']['missing'])
        self.assertIsNone(self.cell(r)['projected_cost_eur_ht'])
        self.assertIn('horizon',self.cell(r)['metric_states']['projected_cost_eur_ht']['missing'])
        self.assertEqual(self.cell(r)['cost_eur_ht'],2100)

    def test_initial_and_annual_bases_cannot_be_silently_summed(self):
        org,s=self.fixture();org['work_catalog']['units'][0]['recurrence']='annual'
        with self.assertRaisesRegex(ValueError,'phase basis'):consolidate(org,s)

    def test_reference_reading_is_independent_from_proposal_classification(self):
        org=deepcopy(reference_study().content['delivery_organisation']);before=consolidate(org)['reference']
        u=next(u for u in org['work_catalog']['units'] if u['id']=='funding/travaux_communs')
        p=deepcopy(self.fixture()[0]['work_catalog']['units'][0]['estimation']['proposal']['inputs']);p.update(cost_mode='fixed_purchase',roles=[],expenses_eur_ht=1000,billing_period='once')
        u['estimation']['proposal']['inputs']=p;self.reprice(u)
        s=read(ROOT/SOURCE);sel=next(x for x in s['selections'] if x['work_unit_ref']==u['id']);sel.update(estimate_source='proposal',work_kind='expense',accounting='additional',basis='Test')
        self.assertEqual(consolidate(org,s)['reference'],before)
        s=read(ROOT/SOURCE);sel=next(x for x in s['selections'] if x['work_unit_ref'].startswith('core/'));sel['work_kind']='expense'
        with self.assertRaisesRegex(ValueError,'erase measured human effort'):consolidate(org,s)


    def test_scope_can_complete_retained_work_without_reestimating_its_price(self):
        from work_units import build_work_units
        study=reference_study();org=deepcopy(study.content['delivery_organisation'])
        source=read(ROOT/'source/unites-travail.yaml')
        unit=next(u for u in org['work_catalog']['units'] if u['id'].startswith('core/') and u['contributions'][0]['team_ref'] is not None)
        raw=next(u for u in source['units'] if u['id']==unit['id'])
        raw['estimation_contract']['scope']=dict(deliverable=None,acceptance=['Critères documentés pour le contrôle'],boundary=None)
        org['work_catalog']=build_work_units(study.economic,org,source=source)
        revised=next(u for u in org['work_catalog']['units'] if u['id']==unit['id'])
        self.assertEqual(revised['estimation']['reference'],unit['estimation']['reference'])
        self.assertNotIn('acceptance',revised['estimation']['missing'])
        self.assertNotIn('estimate',consolidate(org)['working']['issues'][unit['id']])
        self.assertTrue(all(v is None for v in revised['estimation']['proposal']['inputs'].values()))


if __name__=='__main__':unittest.main()
