"""Current phase workload presentation conserves the existing accounting sources."""
from copy import deepcopy
import unittest
from test_support import reference_study
from charge_dossier import build_dossier, compact_scope

class ChargeDossierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = reference_study()
        cls.org = cls.study.content['delivery_organisation']
        cls.dossier = cls.org['charge_dossier']

    def test_compact_scope_is_exact_and_never_exaggerates_partial_coverage(self):
        def node(id,kind):return dict(id=id,kind=kind,fields=dict(name=id))
        nodes=[node('D','domain'),node('S','area'),node('T','area')]
        relations=[dict(type='presents',source_id='D',target_id=s) for s in ('S','T')]
        for a in ('a','b','c','d'):
            nodes += [node(a,'business_area'),node(a+'1','capability'),node(a+'2','capability')]
            relations += [dict(type='contains',source_id='S' if a!='d' else 'T',target_id=a)]
            relations += [dict(type='contains',source_id=a,target_id=a+i) for i in ('1','2')]
        snapshot=dict(nodes=nodes,relations=relations)
        def summary(ids):return compact_scope([dict(id=i) for i in ids],snapshot)
        self.assertEqual(summary([]),[])
        all_caps=[a+i for a in 'abcd' for i in ('1','2')]
        self.assertEqual([r['kind'] for r in summary(all_caps)],['domain'])
        self.assertEqual([r['kind'] for r in summary(all_caps[:6])],['subdomain'])
        result=summary(all_caps[:4])
        self.assertEqual([(r['kind'],r['excluded']) for r in result],[('except','c')])
        # A partly covered excluded area must still be listed, never omitted.
        self.assertEqual([r['kind'] for r in summary(all_caps[:5])],['area']*3)
        self.assertEqual([r['kind'] for r in summary(['a1'])],['area'])
        nodes.append(node('empty','business_area'))
        relations.append(dict(type='contains',source_id='T',target_id='empty'))
        self.assertNotIn('domain',[r['kind'] for r in summary(all_caps)])

    def test_current_phases_conserve_without_integration(self):
        for phase in self.dossier['phases']:
            if phase['id'] == 'integration':
                self.assertIsNone(phase['total_jh'])
                self.assertEqual(phase['rows'], [])
                self.assertTrue(phase['pending'])
                continue
            expected = sum(u['totals']['jh'] or 0 for u in self.org['work_catalog']['units'] if u['phase_ref']==phase['id'] and u['nature']!='governance')
            self.assertAlmostEqual(expected, phase['total_jh'])
            self.assertAlmostEqual(sum(r['jh'] for r in phase['rows'] if r['kind']!='governance'), expected)
            for row in phase['rows']:
                self.assertAlmostEqual(sum(c['jh'] for c in row['contributions']),row['jh'])
                self.assertAlmostEqual(sum(c['share_pct'] for c in row['contributions']),100)
        for team in self.dossier['teams']:
            self.assertIsNone(team['totals']['integration'])
            for phase in self.dossier['phases']:
                contributions=[c['jh'] for r in phase['rows'] for c in r['contributions'] if c['team_ref']==team['id']]
                if contributions:
                    self.assertAlmostEqual(team['totals'][phase['id']],sum(contributions))
        self.assertEqual(self.dossier['phases'][-1]['unit'],'JH/an')

    def test_function_natures_justifications_and_financing(self):
        rows={r['id']:r for r in self.dossier['phases'][0]['rows'] if r['kind']=='core_build'}
        for row in rows.values():
            self.assertTrue(row['summary'])
            self.assertTrue(set(row['natures']) <= {'business','it'})
            for field in ('choice','reuse','exclusions','calculation'):
                self.assertTrue(row['justification'][field])
            self.assertAlmostEqual(sum(c['jh'] for c in row['contributions']),row['jh'])
        ateliers=rows['core/supply-workbenches-java-spring']
        self.assertEqual(ateliers['natures'],['business'])
        self.assertEqual(ateliers['capabilities'],[])
        technical=rows['core/professional-it-java-spring']
        self.assertEqual(technical['natures'],['it'])
        self.assertTrue(technical['product_functions'])
        mdm=rows['core/master-data-java-spring']
        self.assertEqual(next(m['jh'] for m in mdm['methods'] if m['id']=='cosmic-isbsg'),mdm['cosmic']['jh'])
        self.assertEqual(mdm['jh'],self.org['mdm_oss_assessment']['retained']['jh'])

    def test_native_scope_and_buy_are_separate(self):
        from capability_catalog import catalog
        native = {r['capacite_id']: tuple(n['id'] for n in r['hierarchie']) for r in catalog()['rows']}
        for phase in self.dossier['phases']:
            for row in phase['rows']:
                self.assertEqual({tuple(n['id'] for n in path) for path in row['scope_paths']},
                                 {native[c['id']] for c in row['capabilities']})
        gross=self.study.content['gross_evaluations']['phases']
        for option, phases in self.dossier['option_summaries'].items():
            for p in phases:
                values=[r['value'] for g in gross[p['id']]['options'][option]['groups'] for r in g['rows'] if r['unit'].startswith('JH') and r['value'] is not None]
                self.assertEqual(p['jh'],None if p['id']=='integration' or not values else sum(values))

    def test_governance_is_annual_and_independent_of_build_schedule(self):
        from validate_stacks import ROOT, read
        office=read(ROOT/'source/modele-composable.yaml')['equipe_transformation']
        expected=sum(r['etp']*office['jours_par_an'] for r in office['roles'])
        self.assertEqual(self.dossier['governance']['annual_jh'],expected)
        self.assertEqual(self.dossier['governance']['horizons'],[dict(years=y,jh=expected*y) for y in (2,3,4,5)])
        org=deepcopy(self.org)
        org['reading']['build_months']=None
        result=build_dossier(org,self.study.content['gross_evaluations']['phases'])
        self.assertEqual(result,self.dossier)
        self.assertTrue(self.dossier['governance']['rows'])
        self.assertEqual(sum(r['jh'] for r in self.dossier['governance']['rows']),expected)
        self.assertFalse(any(r['kind']=='governance' for p in self.dossier['phases'] for r in p['rows']))
        for row in self.dossier['governance']['rows']:
            if row['kind']=='governance':
                self.assertEqual(row['unit'],'JH/an')
                self.assertEqual(sum(r['jh'] for r in row['roles']),row['jh'])
        mdm=next(r for r in self.dossier['phases'][0]['rows'] if r['id']=='core/master-data-java-spring')
        self.assertNotIn('engineering',[m['id'] for m in mdm['methods']])
        self.assertEqual(mdm['exclusions'],self.org['mdm_oss_assessment']['unidata_review']['exclusions'])
        self.assertEqual(sum(p['jh'] for p in mdm['bridge']['parts']),mdm['jh'])
        self.assertEqual(mdm['bridge']['reference_jh'],next(m['jh'] for m in mdm['methods'] if m['id']=='unidata'))

    def test_global_charge_uses_each_option_and_explicit_governance_horizon(self):
        for option, summary in self.dossier['acquisition_summaries'].items():
            product = self.dossier['phases'][0]['total_jh'] if option=='java-spring' else next(p['jh'] for p in self.dossier['option_summaries'][option] if p['id']=='acquisition')
            self.assertEqual(summary['product_jh'],product)
            for h in summary['horizons']:
                self.assertEqual(h['jh'],product+self.dossier['governance']['annual_jh']*h['years'])
        self.assertNotEqual(self.dossier['acquisition_summaries']['java-spring']['product_jh'], self.dossier['acquisition_summaries']['sap']['product_jh'])

    def test_explicit_breakdowns_and_allocation_bases(self):
        for row in self.dossier['phases'][0]['rows']:
            if row['packages']:
                self.assertAlmostEqual(sum(p['jh'] for p in row['packages']),row['jh'])
            if row['kind']=='governance':
                self.assertAlmostEqual(sum(t['quantity']*t['unit_jh'] for t in row['terms']),row['jh'])
        common=next(r for r in self.dossier['phases'][0]['rows'] if r['id']=='core/process-management-java-spring')
        self.assertTrue(all(c['basis'] for c in common['contributions']))

    def test_methods_and_capability_shares_come_from_owners(self):
        rows=self.dossier['phases'][0]['rows']
        mdm=next(r for r in rows if r['id']=='core/master-data-java-spring')
        self.assertEqual([m['jh'] for m in mdm['methods'] if m['id'] not in ('engineering','cosmic-isbsg')],[p['jh'] for p in self.org['mdm_oss_assessment']['products']])
        for phase in self.dossier['phases']:
            for row in phase['rows']:
                for cap in row['capabilities']:
                    self.assertEqual(cap['share_pct'],100)
        # No financial calculations enter the current workload projection.
        def keys(value):
            if isinstance(value,dict):
                for k,v in value.items():
                    self.assertNotIn(k,('cost_eur_ht','rate','cost','unit_cost'))
                    keys(v)
            elif isinstance(value,list):
                for item in value: keys(item)
        keys(self.dossier)
