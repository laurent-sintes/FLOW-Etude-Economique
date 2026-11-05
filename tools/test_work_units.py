"""Generic work scope, role-aware contributions and unchanged retained values."""
from copy import deepcopy
from decimal import Decimal
import unittest
from jsonschema import ValidationError
from work_units import SOURCE, ABAQUE, build_work_units, split_record, validate_abaque, dependencies
from delivery_organisation import partition
from test_support import reference_study
from validate_stacks import ROOT, read
from audit_delivery_model import audit


class WorkUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study=reference_study()
        cls.org=cls.study.content['delivery_organisation']
        cls.catalog=cls.org['work_catalog']

    def rule(self, component, shares, measure='effort', unit='fixture', phase='acquisition', id=None):
        return dict(id=id or component,work_unit_ref=unit,phase_ref=phase,measure=measure,component_ref=component,
                    shares=[dict(team_ref=t,share_pct=s,contribution_kind=k,basis='Documented contribution') for t,s,k in shares],basis='Explicit fixture')

    def test_role_shares_preserve_effort_rates_costs_and_remainder(self):
        r=dict(id='source',phase='acquisition',team_ref=None,jh=100,cost_eur_ht=55013.37,basis='Reference',roles=[dict(id='functional',label='Functional',jh=90,rate_eur_jh=500),dict(id='technical',label='Technical',jh=10,rate_eur_jh=1000)])
        a=read(ROOT/ABAQUE)
        a['overrides']=[self.rule('functional',[('a',100,'functional')]),self.rule('technical',[('b',50,'technical')])]
        validate_abaque(a,{'a','b'},{'fixture'})
        before=deepcopy((r,a));parts={p['team_ref']:p for p in split_record(r,'fixture',a)}
        self.assertEqual((r,a),before)
        self.assertEqual((parts['a']['jh'],parts['a']['cost_eur_ht']),(90,45000))
        self.assertEqual((parts['b']['jh'],parts['b']['cost_eur_ht']),(5,5000))
        self.assertEqual((parts[None]['jh'],parts[None]['cost_eur_ht']),(5,5013.37))
        self.assertEqual(sum(Decimal(str(p['cost_eur_ht'])) for p in parts.values()),Decimal('55013.37'))
        self.assertEqual(parts['b']['roles'][0]['rate_eur_jh'],1000)
        self.assertNotEqual(parts['a']['jh']/100,parts['a']['cost_eur_ht']/55013.37)

    def test_fractional_expense_keys_preserve_every_cent(self):
        a=read(ROOT/ABAQUE);a['overrides']=[self.rule('expense:total',[('a',33.33,'platform'),('b',33.33,'technical')],measure='cost')]
        r=dict(id='cost',phase='acquisition',team_ref=None,jh=None,cost_eur_ht=.01,roles=[],basis='Purchase')
        parts=split_record(r,'fixture',a)
        self.assertTrue(all(p['jh'] is None for p in parts))
        self.assertEqual(sum(Decimal(str(p['cost_eur_ht'])) for p in parts),Decimal('.01'))
        self.assertEqual([p['cost_eur_ht'] for p in parts],[0,.01,0])

    def test_each_measure_bound_once_and_core_roles_unchanged(self):
        c=self.catalog;records=self.org['reading']['records']
        refs=[r for u in c['units'] for r in u['record_refs']]
        self.assertEqual(len(refs),len(set(refs)))
        self.assertEqual(set(refs),{r['id'] for r in records})
        for unit in next(o for o in self.study.economic['options'] if o['stack']=='java-spring')['core_units']:
            u=next(u for u in c['units'] if u['id']=='core/'+unit['id'])
            self.assertEqual(u['totals'],dict(jh=unit['total_jh'],cost_eur_ht=unit['cost_eur_ht']))
            self.assertEqual(u['measurements'][0]['roles'],[{k:r[k] for k in ('id','label','jh','rate_eur_jh')} for r in unit['roles']])
        original=partition(records,[t['id'] for t in self.org['teams']])
        actual=partition(c['allocations'],[t['id'] for t in self.org['teams']])
        for p,q in zip(original,actual):
            self.assertEqual(p['totals'],q['totals'])
            self.assertEqual([{k:v for k,v in r.items() if k!='record_ids'} for r in p['buckets']], [{k:v for k,v in r.items() if k!='record_ids'} for r in q['buckets']])

    def test_candidates_capabilities_and_details_do_not_allocate_budget(self):
        u=next(u for u in self.catalog['units'] if u['id']=='core/orders-java-spring')
        self.assertIn('b2c',u['candidate_refs'])
        self.assertEqual([c['team_ref'] for c in u['contributions']],[None])
        details=[u for u in self.catalog['units'] if u['integration_unit_ref']]
        self.assertEqual(len(details),len(read(ROOT/'source/unites-integration.yaml')['units']))
        self.assertTrue(all(u['totals']==dict(jh=None,cost_eur_ht=None) and not u['contributions'] for u in details))
        self.assertTrue(all(r['jh'] is None for r in self.catalog['allocations'] if r['phase']=='integration'))
        self.assertEqual({s['team_ref'] for s in self.catalog['team_scopes']},{t['id'] for t in self.org['teams']})
        self.assertEqual(next(s for s in self.catalog['team_scopes'] if s['team_ref']=='master-plan-supply-policy')['scope_kind'],'direct')
        self.assertEqual(next(s for s in self.catalog['team_scopes'] if s['team_ref']=='inventory-availability')['scope_kind'],'direct')
        shared={c['id'] for s in self.catalog['team_scopes'] if s['team_ref']=='master-data' for c in s['capabilities']}
        self.assertTrue(shared & {c['id'] for s in self.catalog['team_scopes'] if s['team_ref']=='paas' for c in s['capabilities']})

    def test_invalid_shares_and_ambiguous_keys_fail(self):
        base=self.rule('*',[('a',70,'technical'),('b',40,'functional')])
        for mutate in [lambda a:None,lambda a:a['overrides'][0]['shares'][0].update(share_pct=-1),lambda a:a['overrides'][0]['shares'][0].update(share_pct=float('nan')),lambda a:a['overrides'][0]['shares'][0].update(team_ref='missing'),lambda a:a['overrides'].append(deepcopy(a['overrides'][0]))]:
            a=read(ROOT/ABAQUE);a['overrides']=[deepcopy(base)];mutate(a)
            with self.assertRaises((ValueError,ValidationError)):validate_abaque(a,{'a','b'},{'fixture'})
        a=read(ROOT/ABAQUE);a['overrides']=[self.rule('technical',[('a',100,'technical')],measure='cost')]
        with self.assertRaises(ValidationError):validate_abaque(a,{'a'},{'fixture'})

    def test_known_zero_and_unknown_are_distinct(self):
        a=read(ROOT/ABAQUE)
        for value in (None,0):
            r=dict(id='r',phase='acquisition',team_ref='a',jh=value,cost_eur_ht=None,roles=[],basis='Reference')
            parts=split_record(r,'fixture',a)
            self.assertEqual(parts[0]['jh'],value)
            self.assertIsNone(parts[0]['cost_eur_ht'])

    def test_live_override_changes_distribution_without_changing_sources(self):
        a=read(ROOT/ABAQUE);uid='core/master-data-java-spring';role='analyse_produit'
        a['overrides']=[self.rule(role,[('master-data',60,'functional'),('b2c',30,'functional')],unit=uid)]
        before=deepcopy((self.study.economic,self.org))
        c=build_work_units(self.study.economic,self.org,abaque=a)
        self.assertEqual((self.study.economic,self.org),before)
        old=next(u for u in self.catalog['units'] if u['id']==uid);new=next(u for u in c['units'] if u['id']==uid)
        self.assertEqual(new['totals'],old['totals'])
        source_role=next(r for r in old['measurements'][0]['roles'] if r['id']==role)
        parts={p['team_ref']:p for p in c['allocations'] if p['work_unit_ref']==uid}
        self.assertAlmostEqual(parts['b2c']['jh'],source_role['jh']*.3)
        self.assertAlmostEqual(parts['b2c']['cost_eur_ht'],source_role['jh']*.3*source_role['rate_eur_jh'])
        self.assertAlmostEqual(parts[None]['jh'],source_role['jh']*.1)
        self.assertEqual(sum(Decimal(str(p['cost_eur_ht'])) for p in parts.values()),Decimal(str(old['totals']['cost_eur_ht'])))

    def test_bad_bindings_cycles_unused_keys_and_enabling_ownership_fail(self):
        for mode in ('duplicate','cycle','unused','enabling'):
            source=read(ROOT/SOURCE);a=read(ROOT/ABAQUE)
            if mode=='duplicate':source['units'][1]['record_refs'].append(source['units'][0]['record_refs'][0])
            if mode=='cycle':source['units'][0]['parent_ref']=source['units'][1]['id'];source['units'][1]['parent_ref']=source['units'][0]['id']
            if mode=='unused':a['overrides']=[self.rule('missing',[('b2c',100,'functional')],unit=source['units'][0]['id'])]
            if mode=='enabling':a['overrides']=[self.rule('*',[('integration',100,'responsibility')],unit=source['units'][0]['id'])]
            with self.subTest(mode=mode),self.assertRaises(ValueError):build_work_units(self.study.economic,self.org,source,a)

    def test_full_graph_bootstrap_export_and_portable_dependencies(self):
        g=self.study.content['framework_graph'];m=self.study.fundamentals['estimation_model']
        self.assertEqual(g['profiles'][0]['id'],'complete')
        self.assertEqual({d['id'] for d in g['domains']},{d['id'] for d in m['domains']})
        self.assertEqual({n['id']:n['domain_ref'] for n in g['objects']},{o['id']:o['domain_ref'] for o in m['objects']})
        self.assertTrue(all(n['color']==next(d['color'] for d in g['domains'] if d['id']==n['domain_ref']) for n in g['objects']))
        self.assertEqual(g['profiles'][0]['object_refs'],[])
        self.assertEqual({n['id'] for n in g['objects']},{o['id'] for o in m['objects']})
        self.assertEqual({r['id'] for r in g['relations']},{r['id'] for r in m['relations']})
        self.assertEqual(self.study.organisation_reading()['delivery_organisation']['work_catalog'],self.catalog)
        self.assertTrue(dependencies()<=self.study.files)
        from study_snapshot import ENGINE_FILES,candidate,load
        self.assertIn('work_units.py',ENGINE_FILES)
        bundle=candidate(self.study)
        self.assertIn(SOURCE,bundle['payload']['documents'])
        from export_business_model import compose
        from model_context import model_session
        with model_session() as snapshot:
            for path in (SOURCE,ABAQUE,'source/fondamentaux.yaml'):read(ROOT/path)
            doc=compose(snapshot.documents,snapshot.digests,derived={'work_catalog':self.catalog})
        self.assertEqual(doc['derived']['work_catalog'],self.catalog)
        self.assertIn(ABAQUE,doc['model'])

    def test_independent_audit_detects_lost_contribution(self):
        self.assertEqual(audit(self.study)['status'],'passed')
        bad=deepcopy(self.study)
        bad.content['delivery_organisation']['work_catalog']['allocations'][0]['jh']+=1
        self.assertEqual(audit(bad)['status'],'failed')


if __name__=='__main__':unittest.main()
