"""Cloud/security repricing stays within existing funded effort and keeps Buy inclusions."""
from copy import deepcopy
import unittest
from model_context import scoped_model

from calculate_costs import (
    SCENARIOS, calculate_option, maintenance_specialist_adjustment, role_rates, validate_inputs,
)
from model_inputs import annual_scenario
from validate_stacks import ROOT, read


class MaintenanceSpecialisationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cal,cls.docs=validate_inputs()
        cls.scenario=annual_scenario()
        cls.catalogues={slug:read(ROOT/doc['dependances']['maintenance']['fichier']) for slug,doc in cls.docs.items()}
        cls.rates={slug:role_rates(read(ROOT/doc['dependances']['stack']['fichier'])) for slug,doc in cls.docs.items()}

    def adjustment(self,slug='java-spring',doc=None,cal=None,maintenance=None,rates=None,case='central'):
        return maintenance_specialist_adjustment(doc or self.docs[slug],maintenance or self.catalogues[slug],
            cal or self.cal,rates or self.rates[slug],self.scenario,case)

    @scoped_model
    def test_specialisation_reprices_existing_days_and_does_not_add_effort(self):
        disabled=deepcopy(self.cal)
        disabled['specialisation_maintenance_make']['plafond_jh_avant_sensibilite']=0
        for slug in self.docs:
            for case in SCENARIOS:
                with self.subTest(slug=slug,case=case):
                    actual=calculate_option(slug,self.docs[slug],self.cal,case,1)
                    without=calculate_option(slug,self.docs[slug],disabled,case,1)
                    adjustment=self.adjustment(slug,case=case)
                    self.assertEqual(actual['jh'],without['jh'])
                    self.assertEqual(actual['maintenance_activites'],without['maintenance_activites'])
                    self.assertLessEqual(adjustment['jh'],adjustment['jh_disponibles'])
                    difference=actual['maintenance_annuelle'][0]['postes_eur_ht']['prestations_estimees']-without['maintenance_annuelle'][0]['postes_eur_ht']['prestations_estimees']
                    self.assertAlmostEqual(difference,adjustment['cout_eur_ht'],places=2)
                    if self.docs[slug]['strategie']=='buy':self.assertEqual(actual,without)

    def test_reduced_underlying_work_bounds_the_allowance_and_zero_work_removes_it(self):
        for ratio in (.1,0):
            changed=deepcopy(self.docs['java-spring'])
            for row in changed['maintenance']['activites']:
                row['jh_fixes_avant_ia']*=ratio
                for charge in row['charges']:charge['jh_unitaire']*=ratio
            with self.subTest(ratio=ratio):
                adjustment=self.adjustment(doc=changed)
                self.assertLess(adjustment['jh'],self.adjustment()['jh'])
                self.assertEqual(adjustment['jh'],adjustment['jh_disponibles'])
                if ratio==0:
                    output=calculate_option('java-spring',changed,self.cal,service_years=1)
                    self.assertEqual(adjustment['cout_eur_ht'],0)
                    self.assertEqual(output['maintenance_annuelle'][0]['postes_eur_ht']['prestations_estimees'],0)

    def test_only_financed_n3_days_are_eligible_and_their_gain_is_respected(self):
        changed=deepcopy(self.docs['java-spring'])
        for row in changed['maintenance']['activites']:
            if row['activite'] in self.cal['specialisation_maintenance_make']['activites_refs']:
                row['gain_ia_pct']=95
        central=self.adjustment(doc=changed)
        self.assertLess(central['jh'],self.adjustment()['jh'])
        self.assertEqual(central['jh'],central['jh_disponibles'])
        # The high sensitivity still uses the common convention of no productivity gain.
        self.assertGreater(self.adjustment(doc=changed,case='haut')['jh'],central['jh'])
        for row in changed['maintenance']['activites']:
            if row['activite'] in self.cal['specialisation_maintenance_make']['activites_refs']:
                row['traitement']='inclus_forfait_rfi'
        self.assertEqual(self.adjustment(doc=changed)['cout_eur_ht'],0)
        catalogue=deepcopy(self.catalogues['java-spring'])
        for row in catalogue['activites']:
            if row['id'] in self.cal['specialisation_maintenance_make']['activites_refs']:
                row['roles']['integration']['part_pct']+=row['roles']['support_n3']['part_pct']
                row['roles']['support_n3']['part_pct']=0
        self.assertEqual(self.adjustment(maintenance=catalogue)['jh'],0)

    def test_a_lower_specialist_tariff_does_not_create_a_negative_supplement(self):
        rates=deepcopy(self.rates['java-spring']);rates['architecte']=rates['support_n3']-1
        self.assertEqual(self.adjustment(rates=rates)['cout_eur_ht'],0)

    def test_invalid_allowance_contract_is_rejected_before_valuation(self):
        def unknown_field(s):s['jh_autonomes']=40
        def unknown_activity(s):s['activites_refs']=['MAI-999']
        def unrelated_activity(s):s['activites_refs']=['MAI-005']
        def duplicate_activity(s):s['activites_refs']*=2
        def empty_activities(s):s['activites_refs']=[]
        def unsupported_profile(s):s['profil_base']='support_n1'
        def invented_proof(s):s['statut']='charge_observee'
        def missing_provenance(s):s['origine']=''
        changes=[unknown_field,unknown_activity,unrelated_activity,duplicate_activity,empty_activities,
                 unsupported_profile,invented_proof,missing_provenance]
        for invalid in (-1,True,None,'40',float('nan'),float('inf')):
            changes.append(lambda s,value=invalid:s.__setitem__('plafond_jh_avant_sensibilite',value))
        for change in changes:
            cal=deepcopy(self.cal);change(cal['specialisation_maintenance_make'])
            with self.subTest(spec=cal['specialisation_maintenance_make']),self.assertRaises(AssertionError):
                self.adjustment(cal=cal)


if __name__=='__main__':unittest.main()
