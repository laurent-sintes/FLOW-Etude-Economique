"""Canonical projection and fault-injected model/financial audit checks."""
from copy import deepcopy
import unittest
from framework_graph import build_graph
from audit_delivery_model import audit
from delivery_organisation import build_organisation, partition, validate
from test_support import reference_study
from validate_stacks import ROOT, read


class FrameworkGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.study=reference_study()

    def test_graph_contains_only_canonical_objects_and_relations(self):
        G=self.study.content['framework_graph'];M=self.study.fundamentals['estimation_model']
        self.assertEqual({n['id'] for n in G['objects']},{o['id'] for o in M['objects']})
        self.assertEqual({r['id'] for r in G['relations']},{r['id'] for r in M['relations']})
        for r,canonical in zip(G['relations'],M['relations']):
            for key in ('source','target','cardinality','meaning'):self.assertEqual(r[key],canonical[key])
        self.assertEqual({r['id'] for r in G['interactions']},{r['id'] for r in self.study.content['delivery_organisation']['interactions']})
        self.assertFalse(any(r['source']=='transformation-office' or r['target']=='transformation-office' for r in G['interactions']))
        self.assertEqual(G,self.study.bootstrap(essential=True)['content']['framework_graph'])

    def test_domains_are_canonical_and_every_object_has_one_domain(self):
        g=self.study.content['framework_graph'];m=self.study.fundamentals['estimation_model']
        self.assertEqual({d['id'] for d in g['domains']},{d['id'] for d in m['domains']})
        self.assertEqual(len(g['domains']),len({d['id'] for d in g['domains']}))
        self.assertTrue(all(n['domain_ref'] in {d['id'] for d in g['domains']} for n in g['objects']))
        settings=read(ROOT/'config/schema-modele.yaml')
        bad=deepcopy(m);bad['objects'][0]['domain_ref']='missing'
        with self.assertRaisesRegex(ValueError,'Unknown object domain'):build_graph(bad,self.study.content['delivery_organisation'],settings)
        bad=deepcopy(settings);bad['domain_colors'].pop(next(iter(bad['domain_colors'])))
        with self.assertRaisesRegex(ValueError,'Domain colour scope'):build_graph(m,self.study.content['delivery_organisation'],bad)
        from estimation_calculation import metamodel
        bad=read(ROOT/'source/fondamentaux.yaml');bad['estimation_model']['domains'].append(deepcopy(bad['estimation_model']['domains'][0]))
        with self.assertRaisesRegex(ValueError,'duplicate metamodel domain'):metamodel(bad)

    def test_every_rule_has_one_execution_edge_and_shared_modules_are_unique(self):
        G=self.study.content['framework_graph'];M=self.study.fundamentals['estimation_model']
        self.assertEqual(len(G['rule_relations']),len(M['rules']))
        self.assertEqual(len(G['rules']),len({n['id'] for n in G['rules']}))
        self.assertEqual({r['source'] for r in G['rule_relations']},{'rule:'+r['id'] for r in M['rules']})
        ids={n['id'] for n in G['rules']}
        self.assertTrue(all(r['source'] in ids and r['target'] in ids for r in G['rule_relations']))

    def test_unknown_profiles_and_broken_endpoints_fail_before_rendering(self):
        settings=read(ROOT/'config/schema-modele.yaml');M=self.study.fundamentals['estimation_model'];D=self.study.content['delivery_organisation']
        bad=deepcopy(settings);bad['profiles'][0]['object_refs'].append('missing')
        with self.assertRaisesRegex(ValueError,'Unknown profile object'):build_graph(M,D,bad)
        bad=deepcopy(M);bad['relations'][0]['target']='missing'
        with self.assertRaisesRegex(ValueError,'Unknown relation endpoint'):build_graph(bad,D,settings)
        before=deepcopy((M,D,settings));build_graph(M,D,settings)
        self.assertEqual((M,D,settings),before)

    def test_independent_audit_detects_role_price_ledger_and_horizon_corruption(self):
        s=self.study
        self.assertEqual(audit(s)['status'],'passed')
        for kind in ('role','price','ledger','horizon'):
            bad=deepcopy(s)
            if kind=='role':bad.economic['options'][0]['core_units'][0]['roles'][0]['jh']+=1
            elif kind=='price':bad.economic['options'][0]['core_units'][0]['cost_eur_ht']+=1
            elif kind=='ledger':bad.baseline['options'][0]['funding_ledger'].append(deepcopy(bad.baseline['options'][0]['funding_ledger'][0]))
            else:bad.baseline['options'][0]['horizons'][0]['totals']['total']+=1
            with self.subTest(kind=kind):self.assertEqual(audit(bad)['status'],'failed')

    def test_enabling_may_contribute_to_coaching_but_not_own_a_core_product(self):
        doc=read(ROOT/'source/organisation-delivery.yaml')
        row=next(r for r in doc['work_owners'] if r['kind']=='integration_activity' and r['ref']=='INT-001')
        row.update(team_ref='integration',candidate_refs=['integration'])
        validate(doc)
        row=next(r for r in doc['work_owners'] if r['kind']=='core_unit')
        row.update(team_ref='integration',candidate_refs=['integration'])
        with self.assertRaisesRegex(ValueError,'maintained software'):validate(doc)

    def test_crossing_funding_period_and_ambiguous_attribution_are_rejected(self):
        s=self.study;bad=deepcopy(s.baseline)
        option=next(o for o in bad['options'] if o['stack']=='java-spring')
        next(r for r in option['funding_ledger'] if r['id'].startswith('hebergement_build/'))['end']=option['initial_months']+1
        with self.assertRaisesRegex(ValueError,'crosses build boundary'):build_organisation(s.economic,bad,s.content)
        doc=read(ROOT/'source/organisation-delivery.yaml')
        doc['work_owners'].append(dict(kind='funding',ref='hebergement_build/developpement_initial',team_ref='portal',candidate_refs=['portal'],basis='Contradiction volontaire pour le contrôle.'))
        with self.assertRaisesRegex(ValueError,'Conflicting funding attribution'):build_organisation(s.economic,s.baseline,s.content,doc)
        for ids in (['same','same'],['governance']):
            with self.assertRaisesRegex(ValueError,'partition teams'):partition([],ids)


if __name__=='__main__':unittest.main()
