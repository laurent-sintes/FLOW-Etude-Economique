"""Common contracts, explicit role valuation, pending inputs and retained figures."""
from copy import deepcopy
from decimal import Decimal
import unittest
from jsonschema import ValidationError, Draft202012Validator
from test_support import reference_study
from validate_stacks import ROOT,read
from work_estimation import quantity_estimate, SCHEMA, dependencies
from work_units import build_work_units


class WorkEstimationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study=reference_study();cls.org=cls.study.content['delivery_organisation'];cls.catalog=cls.org['work_catalog']

    def test_all_phases_reconcile_sources_without_adopting_proposals(self):
        seen=[]
        self.assertEqual({u['estimation']['phase_ref'] for u in self.catalog['units']},{'acquisition','integration','fonctionnement'})
        for u in self.catalog['units']:
            e=u['estimation'];self.assertEqual(e['work_unit_ref'],u['id'])
            self.assertEqual(e['reference']['source_jh'],u['totals']['jh'])
            self.assertEqual(e['reference']['cost_eur_ht'],u['totals']['cost_eur_ht'])
            self.assertTrue(all(v is None for v in e['proposal']['inputs'].values()))
            self.assertIsNone(e['proposal']['result']['cost_eur_ht'])
            source={r['id']:r for r in u['measurements']}
            values=[]
            for b in e['cost_bridge']:
                seen.append(b['record_ref']);values.append(Decimal(str(b['retained_eur_ht'])))
                self.assertEqual(b['retained_eur_ht'],source[b['record_ref']]['cost_eur_ht'])
                if b['status']=='reconciled':
                    self.assertLessEqual(abs(Decimal(str(b['calculated_eur_ht']))+Decimal(str(b['rounding_eur_ht']))-Decimal(str(b['retained_eur_ht']))),Decimal('.0000001'))
                    self.assertTrue(all(r['net_jh'] is not None and r['rate_eur_jh'] is not None for r in b['roles']))
                else:self.assertIsNone(b['calculated_eur_ht'])
            self.assertEqual(float(sum(values)) if values else None,u['totals']['cost_eur_ht'])
        self.assertEqual(len(seen),len(set(seen)))
        self.assertEqual(set(seen),{r['id'] for r in self.org['reading']['records'] if r['cost_eur_ht'] is not None})

    def test_core_comments_never_supply_a_missing_deliverable(self):
        units=[u for u in self.catalog['units'] if u['nature']=='core_build']
        self.assertTrue(units)
        for u in units:
            self.assertIsNone(u['estimation']['scope']['deliverable'])
            self.assertIn('deliverable',u['estimation']['missing'])
            self.assertTrue(u['included_activities'])
            self.assertEqual(u['estimation']['reference']['cost_eur_ht'],u['totals']['cost_eur_ht'])
        source=read(ROOT/'source/unites-travail.yaml');unit=next(u for u in source['units'] if u['id']==units[0]['id'])
        unit['estimation_contract']['scope']['deliverable']='Résultat explicite à réceptionner'
        catalog=build_work_units(self.study.economic,self.org,source=source)
        after=next(u for u in catalog['units'] if u['id']==unit['id'])
        self.assertEqual(after['estimation']['scope']['deliverable'],unit['estimation_contract']['scope']['deliverable'])
        self.assertNotIn('deliverable',after['estimation']['missing'])
        self.assertEqual(after['totals'],units[0]['totals'])

    def test_maintenance_gross_net_and_prices_are_distinct(self):
        u=next(u for u in self.catalog['units'] if u['id']=='maintenance/MAI-003');e=u['estimation'];r=e['reference']
        work=next(a for a in self.study.data['options'][0]['composable']['inputs']['work']['maintenance']['activites'] if a['activite']=='MAI-003')
        self.assertEqual(r['source_jh'],r['gross_jh'])
        self.assertAlmostEqual(r['net_jh'],r['gross_jh']*(1-work['gain_ia_pct']/100))
        b=e['cost_bridge'][0]
        expected=sum(Decimal(str(x['net_jh']))*Decimal(str(x['rate_eur_jh'])) for x in b['roles'])+Decimal(str(b['non_labour_eur_ht']))
        self.assertAlmostEqual(float(expected),b['retained_eur_ht'],places=2)

    def test_maintenance_role_override_carries_its_net_cost_and_keeps_totals(self):
        a=read(ROOT/'source/abaque-ventilation.yaml');uid='maintenance/MAI-003'
        a['overrides']=[dict(id='audit-role',work_unit_ref=uid,phase_ref='fonctionnement',measure='effort',component_ref='developpement',shares=[dict(team_ref='master-data',share_pct=50,contribution_kind='technical',basis='Test only')],basis='Test only')]
        before=deepcopy((self.study.economic,self.org,a))
        result=build_work_units(self.study.economic,self.org,abaque=a)
        u=next(u for u in result['units'] if u['id']==uid);role=next(r for r in u['estimation']['reference']['roles'] if r['id']=='developpement')
        p=next(c for c in u['contributions'] if c['team_ref']=='master-data')
        self.assertAlmostEqual(p['jh'],role['gross_jh']*.5)
        self.assertAlmostEqual(p['cost_eur_ht'],role['net_jh']*.5*role['rate_eur_jh'])
        self.assertEqual(sum(Decimal(str(c['cost_eur_ht'])) for c in u['contributions']),Decimal(str(u['totals']['cost_eur_ht'])))
        self.assertEqual((self.study.economic,self.org,a),before)

    def test_integration_never_infers_days_from_its_envelopes(self):
        for u in self.catalog['units']:
            e=u['estimation']
            if u['phase_ref']!='integration':continue
            self.assertIsNone(e['reference']['source_jh']);self.assertIsNone(e['reference']['net_jh'])
            if u['totals']['cost_eur_ht'] is None:self.assertEqual(e['decision_status'],'to_establish')
            self.assertTrue(all(b['status']=='amount_only' for b in e['cost_bridge']))
            if u['integration_unit_ref']:
                self.assertIn('quantity',e['missing']);self.assertIn('unit_effort',e['missing'])
                self.assertTrue(all(r['net_jh'] is None for r in e['reference']['roles']))
                self.assertTrue(all(r['rate_eur_jh'] is not None for r in e['reference']['roles']))

    def proposal(self):
        return dict(deliverable='Test result',acceptance=['Acceptance'],quantity=2,count_unit='cases',counting_rule='Count once',quantity_basis='Evidence',roles=[dict(id='a',label='A',fixed_jh=1,unit_jh=3,gain_pct=10,rate_eur_jh=500,rate_ref=None)],expenses_eur_ht=25,assumptions=['Test basis'],evidence_refs=['source/maintenance.yaml'])

    def test_proposals_calculate_separately_and_partial_values_stay_unknown(self):
        p=self.proposal();before=deepcopy(p);r=quantity_estimate(p)
        self.assertEqual(p,before);self.assertEqual(r['status'],'proposal')
        self.assertEqual(r['gross_jh'],7);self.assertEqual(r['net_jh'],6.3);self.assertEqual(r['cost_eur_ht'],3175)
        for field in ('quantity','expenses_eur_ht'):
            partial=deepcopy(p);partial[field]=None
            self.assertIsNone(quantity_estimate(partial)['cost_eur_ht'])
        for field in ('fixed_jh','unit_jh','gain_pct','rate_eur_jh'):
            partial=deepcopy(p);partial['roles'][0][field]=None
            self.assertIsNone(quantity_estimate(partial)['cost_eur_ht'])
        p['quantity']=0;p['roles'][0]['fixed_jh']=0;p['expenses_eur_ht']=0
        self.assertEqual(quantity_estimate(p)['cost_eur_ht'],0)

    def test_a_completed_proposal_does_not_enter_retained_figures(self):
        source=read(ROOT/'source/unites-travail.yaml');u=next(u for u in source['units'] if u['id']=='integration-detail/authority');u['estimation_contract']['proposal']=self.proposal()
        before=deepcopy(self.org['allocation_table'])
        result=build_work_units(self.study.economic,self.org,source=source)
        e=next(u for u in result['units'] if u['id']=='integration-detail/authority')['estimation']
        self.assertEqual(e['proposal']['result']['cost_eur_ht'],3175)
        self.assertIsNone(e['reference']['cost_eur_ht']);self.assertIsNone(e['reference']['source_jh'])
        self.assertEqual(self.org['allocation_table'],before)
        self.assertEqual(result['allocations'],self.catalog['allocations'])

    def test_contract_rejects_unknown_fields_bad_numbers_and_ambiguous_rates(self):
        s=read(ROOT/'source/unites-travail.yaml')['units'][0]['estimation_contract'];bad=deepcopy(s);bad['extra']=1
        with self.assertRaises(ValidationError):Draft202012Validator(read(ROOT/SCHEMA)).validate(bad)
        for field,value in [('quantity',float('nan')),('quantity',-1),('expenses_eur_ht',float('inf'))]:
            p=self.proposal();p[field]=value
            with self.assertRaises(ValueError):quantity_estimate(p)
        p=self.proposal();p['roles'][0]['rate_ref']={'path':'source/tarifs-projet.yaml','pointer':'roles.backend.reference'}
        with self.assertRaisesRegex(ValueError,'Ambiguous'):quantity_estimate(p)
        p['roles'][0]['rate_eur_jh']=None
        self.assertIsNotNone(quantity_estimate(p)['cost_eur_ht'])

    def test_fractional_role_costs_conserve_the_source_cent_exactly(self):
        from work_units import split_record
        r=dict(id='fractional',phase='fonctionnement',team_ref=None,jh=None,cost_eur_ht=100,roles=[],basis='Reference')
        v=dict(status='reconciled',roles=[dict(id='a',net_jh=1/7,rate_eur_jh=500),dict(id='b',net_jh=1/7,rate_eur_jh=100)])
        parts=split_record(r,'fixture',read(ROOT/'source/abaque-ventilation.yaml'),valuation=v)
        self.assertEqual(sum(Decimal(str(p['cost_eur_ht'])) for p in parts),Decimal(100))
        self.assertTrue(all(p['jh'] is None for p in parts))

    def test_bootstrap_export_and_graph_share_the_contract(self):
        self.assertTrue(dependencies()<=self.study.files)
        self.assertEqual(self.study.organisation_reading()['delivery_organisation']['work_catalog']['units'][0]['estimation'],self.catalog['units'][0]['estimation'])
        from study_snapshot import ENGINE_FILES,candidate
        self.assertIn('work_estimation.py',ENGINE_FILES)
        self.assertIn(SCHEMA,candidate(self.study)['payload']['documents'])
        model=self.study.fundamentals['estimation_model']
        self.assertTrue({'work_estimate','work_cost_bridge'}<={o['id'] for o in model['objects']})
        self.assertIn('common_work_estimation_contract',{r['id'] for r in model['rules']})


if __name__=='__main__':unittest.main()
