"""Migration checks: canonical identities, proof resolution and unchanged economics."""
from copy import deepcopy
from decimal import Decimal
import json
import unittest
from validate_stacks import ROOT, read
from business_map import validate
from test_support import study_copy
from study_app import Study


def projection(value):
    return {k:v for k,v in value.items() if k != 'model_version'}


def numbers(value, path=()):
    if isinstance(value, dict):
        return {p:n for k,v in value.items() for p,n in numbers(v,path+(k,)).items()}
    if isinstance(value, list):
        return {p:n for k,v in enumerate(value) for p,n in numbers(v,path+(str(k),)).items()}
    return {path:value} if isinstance(value,(int,float)) and not isinstance(value,bool) else {}


class BusinessMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = study_copy()

    def test_map_is_exact_source_projection_with_joined_work_and_buy_proofs(self):
        m=self.study.content['business_map']
        snapshot=read(ROOT/m['source']['path'])
        expected={n['id'] for n in snapshot['nodes'] if n['kind']=='capability'}
        self.assertEqual({r['capacite_id'] for r in m['rows']},expected)
        self.assertEqual(len(m['rows']),len(expected))
        for r in m['rows']:
            self.assertEqual(r['work']['capacite_id'],r['capacite_id'])
            self.assertEqual(r['work']['scenario'],' ; '.join(f['resultat'] for f in r['fonctions']))
            self.assertEqual(r['work']['frontiere'],r['frontiere'])
            self.assertEqual(set(r['buy']),{'microsoft','sap'})
            for review in r['buy'].values():
                self.assertEqual(review['capacite'],r['capacite_id'])
                self.assertEqual({p['id'] for p in review['proofs']},set(review['coverage']['sources']))
                self.assertTrue(all(p['reference'] for p in review['proofs']))

    def test_funding_instances_remain_distinct_from_reused_templates(self):
        m=self.study.content['business_map']
        self.assertFalse(m['funding'])
        self.assertEqual(len(m['family_funding']),1)
        self.assertEqual(len(m['family_funding'][0]['beneficiaries']),6)
        for o in self.study.economic['options']:
            if o['stack'] not in ('java-spring','dotnet','rust'):continue
            family=sum(Decimal(str(f['cout_eur_ht'])) for f in m['family_funding'] if f['stack']==o['stack'])
            self.assertEqual(family,Decimal(str(o['detail_build']['prestations'])))

    def test_scenarios_and_boundary_subjects_do_not_add_capabilities(self):
        m=self.study.content['business_map'];refs={s['id'] for r in m['rows'] for s in r['scenarios']}
        self.assertEqual(refs,{s['scenario'] for s in self.study.content['integration_paths']['scenarios']})
        tech=next(t for t in m['themes'] if t['id']=='hebergement-ipaas')
        self.assertEqual(tech['capabilities'],[])
        finance=next(t for t in m['themes'] if t['id']=='finance-conception')
        self.assertIn('domain-finance',{n['id'] for n in finance['neighbors']})
        for cap in ('D05.e','D05.c'):
            row=next(r for r in m['rows'] if r['capacite_id']==cap)
            self.assertIn('reassort-sap',{e['id'] for e in row['buy']['sap']['exceptions']})
            self.assertTrue(all(e['cout_initial_eur_ht'] is None for e in row['buy']['sap']['exceptions']))

    def test_untraceable_subject_and_source_revision_rejected(self):
        spec=read(ROOT/'source/lecture-metier.yaml')
        wrong=deepcopy(spec);wrong['sujets'][0]['capacites']=['invented-capability']
        with self.assertRaises(AssertionError):validate(wrong)
        wrong=deepcopy(spec);wrong['frontieres_empreinte']='0'*64
        with self.assertRaises(AssertionError):validate(wrong)


if __name__=='__main__': unittest.main(verbosity=2)
