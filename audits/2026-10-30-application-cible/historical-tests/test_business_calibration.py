import unittest
from copy import deepcopy
from business_calibration import validate,apply,SLUGS
from calculate_costs import validate_inputs,calculate_option
from buy_qualification import validate as validate_buy,integration_paths,coverage_sources
from validate_stacks import ROOT,read

class CalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=validate();cls.cal,cls.docs=validate_inputs()
    def test_ranges_reject_reversal(self):
        d=deepcopy(self.model);d['lots']['controle']['bas'][0]=999
        with self.assertRaises(AssertionError):validate(d)
    def test_missing_or_duplicate_capacity_rejected(self):
        d=deepcopy(self.model);d['blocs'][0]=deepcopy(d['blocs'][1])
        with self.assertRaises(AssertionError):validate(d)
    def test_unknown_canonical_capability_is_rejected(self):
        d=read(ROOT/'source/recalibration-metier.yaml');d['blocs'][0]['capacite']='missing-canonical-capability'
        with self.assertRaises(AssertionError):validate(d)
    def test_component_from_another_stack_rejected(self):
        d=deepcopy(self.model);d['couvertures']['rust_process']['composants'].append('flowable')
        with self.assertRaises(AssertionError):validate(d)
    def test_need_is_derived_from_the_map_without_editable_copies(self):
        raw=read(ROOT/'source/recalibration-metier.yaml')
        self.assertTrue(all(not {'scenario','frontiere','verification_buy'} & row.keys() for row in raw['blocs']))
        result=validate(raw)
        grid={b['capacite_id']:b for b in read(ROOT/'source/grille-complexite.yaml')['blocs']}
        for row in result['blocs']:
            block=grid[row['capacite']]
            self.assertEqual(row['scenario'],' ; '.join(f['resultat'] for f in block['fonctions']))
            self.assertEqual(row['frontiere'],block['frontiere'])
        self.assertNotIn('scenario',raw['blocs'][0])
        result['blocs'][0]['scenario']='Une copie divergente du besoin métier'
        with self.assertRaises(AssertionError):validate(result)
    def test_source_reordering_preserves_each_assignment_and_calculated_cost(self):
        raw=read(ROOT/'source/recalibration-metier.yaml');raw['blocs'].reverse()
        reordered=validate(raw)
        self.assertEqual(reordered['blocs'],self.model['blocs'])
        docs=apply(self.docs,reordered)
        for slug in SLUGS:
            self.assertEqual(calculate_option(slug,docs[slug],self.cal),calculate_option(slug,self.docs[slug],self.cal))
    def test_buy_coverage_proofs_resolve_and_missing_proof_is_rejected(self):
        q=validate_buy(self.model);sources=coverage_sources(self.model)
        for row in q['revues']:
            for key in self.model['couvertures'][row['couverture_ref']]['sources']:
                self.assertTrue(sources[key]['reference'])
                self.assertTrue(sources[key]['portee'])
        d=deepcopy(self.model);d['couvertures']['ms_reference']['sources']=['MISSING_PROOF']
        with self.assertRaises(AssertionError):validate(d)
    def test_replenishment_context_is_qualified_without_new_development(self):
        q=validate_buy(self.model)
        for block in ('BC-043','BC-044'):
            row=next(r for r in q['revues'] if r['bloc']==block and r['stack']=='sap')
            self.assertEqual(row['exceptions'],['reassort-sap'])
            self.assertEqual(row['statut'],'point_cible')
        exception=next(e for e in q['exceptions'] if e['id']=='reassort-sap')
        self.assertEqual(exception['statut'],'a_qualifier')
        self.assertIsNone(exception['cout_initial_eur_ht'])
        self.assertFalse(q['developpements'])
    def test_common_frontend_and_explicit_differing_mechanisms(self):
        for rows in zip(*(self.docs[s]['core'] for s in SLUGS[:3])):
            self.assertEqual(len({r['jh_frontend_avant_ia'] for r in rows}),1)
        r={s:{f['feature']:f for f in self.docs[s]['core']} for s in SLUGS[:3]}
        self.assertEqual(r['java-spring']['BC-001']['jh_backend_avant_ia'],r['rust']['BC-001']['jh_backend_avant_ia'])
        if self.model['statut']=='a_reestimer':
            self.assertTrue(all(not any(f['jh_backend_avant_ia'].values()) and f['jh_frontend_avant_ia']==0 for s in SLUGS[:3] for f in self.docs[s]['core']))
        else:
            self.assertLess(sum(r['dotnet']['BC-052']['jh_backend_avant_ia'].values()),sum(r['java-spring']['BC-052']['jh_backend_avant_ia'].values()))
    def test_buy_product_is_not_automatically_rebuilt_per_capability(self):
        for s in SLUGS[3:]:
            self.assertEqual(self.docs[s]['core'],[])
            self.assertEqual(self.docs[s]['maintenance']['maintenance_complements_buy_jh_annuels'],0)
            result=calculate_option(s,self.docs[s],self.cal)
            self.assertEqual(result['synthese_eur_ht']['build_core'],0)
            self.assertEqual(result['detail_integration']['base_rfi'],sum(self.docs[s]['integration']['prix_rfi']['postes_eur']))

    def test_included_buy_diagnostics_are_never_billed_twice(self):
        for slug in ('microsoft','sap'):
            doc=deepcopy(self.docs[slug]);before=calculate_option(slug,doc,self.cal)
            for a in doc['integration']['activites']:
                self.assertEqual(a['traitement'],'inclus_rfi')
                a['jh_avant_ia']*=100
            for a in doc['maintenance']['activites']:
                if a['traitement'].startswith('inclus_'):
                    a['jh_fixes_avant_ia']+=10000
                    for c in a['charges']:c['jh_unitaire']*=100
            after=calculate_option(slug,doc,self.cal)
            self.assertEqual(after['synthese_eur_ht'],before['synthese_eur_ht'])
            self.assertEqual(after['maintenance_annuelle'],before['maintenance_annuelle'])
    def test_residual_ranges_do_not_receive_second_global_multiplier(self):
        c=deepcopy(self.cal);c['sensibilite']['jh_haut']=9
        for s in SLUGS:
            before=calculate_option(s,self.docs[s],self.cal,'haut')
            after=calculate_option(s,self.docs[s],c,'haut')
            self.assertEqual(before['features'],after['features'])
    def test_buy_exception_requires_evidence_and_has_one_charge_and_maintenance(self):
        q=validate_buy(self.model)
        q['developpements']=[dict(id='BUY-test',exception='transport-sap',stack='sap',preuve='sap-tm',
            fonction_absente='Test isolé de fonction absente',financement_distinct='Test hors prestations déjà payées',
            bas=[1,1,1,1,1,0],central=[2,2,2,2,2,0],haut=[3,3,3,3,3,0],entretien_jh_annuels=2)]
        with self.assertRaises(AssertionError):validate_buy(self.model,q)
        next(e for e in q['exceptions'] if e['id']=='transport-sap')['statut']='ecart_demontre'
        changed=apply(self.docs,self.model,q)
        before=calculate_option('sap',self.docs['sap'],self.cal);after=calculate_option('sap',changed['sap'],self.cal)
        self.assertEqual(len(after['features']),1)
        self.assertAlmostEqual(after['detail_integration']['complements_flow']-before['detail_integration']['complements_flow'],after['features'][0]['cout_eur_ht'],places=2)
        self.assertEqual(before['detail_integration']['base_rfi'],after['detail_integration']['base_rfi'])
        self.assertGreater(after['synthese_eur_ht']['maintenance_premiere_annee'],before['synthese_eur_ht']['maintenance_premiere_annee'])
    def test_buy_unknown_is_not_zero_and_duplicate_review_rejected(self):
        q=validate_buy(self.model)
        self.assertTrue(all(e['cout_initial_eur_ht'] is None for e in q['exceptions']))
        q['revues'][0]=deepcopy(q['revues'][1])
        with self.assertRaises(AssertionError):validate_buy(self.model,q)
    def test_scenarios_are_traceable_without_a_cost_multiplier(self):
        d,c=integration_paths()
        self.assertEqual(len(d['scenarios']),43)
        self.assertEqual(len(c['paths']),50)
        self.assertEqual(len({a for l in d['lots'] for a in l['activites']}),13)
    def test_shared_cycles_charged_at_one_owner(self):
        rows={b['bloc']:b for b in self.model['blocs']}
        for s in SLUGS[:3]:
            self.assertEqual(sum(b['stacks'][s]['travaux_ref']=='commande_noyau' for b in rows.values()),1)
            self.assertEqual(sum(b['stacks'][s]['travaux_ref']=='prestation_noyau' for b in rows.values()),1)
        for i in range(60,74):self.assertIn('BC-059',[r['proprietaire'] for r in rows[f'BC-{i:03}']['reemploi']])

if __name__=='__main__':unittest.main(verbosity=2)
