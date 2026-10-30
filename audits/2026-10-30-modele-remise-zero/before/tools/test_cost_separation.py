"""Cent-level conservation of budgets, phase boundaries and displayed totals."""
from copy import deepcopy
import unittest
from project_investment import phase_expense,project_financing
from audit_cost_separation import independent_projection,cents


class MonetaryAllocationTests(unittest.TestCase):
    def test_cumulative_rounding_conserves_budget(self):
        for budget in (0,0.01,100.01,9928747.11,10843244.02):
            for start,duration in ((0,48),(48,34),(36.25,38.5),(0,38)):
                parts=[phase_expense(budget,start,duration,(y-1)*12,y*12) for y in range(1,11)]
                self.assertEqual(sum(cents(v) for v in parts),cents(budget))
                self.assertTrue(all(v>=0 for v in parts))

    def test_zero_build_and_phase_boundaries(self):
        self.assertEqual(phase_expense(0,0,0,0,12),0)
        self.assertEqual(phase_expense(100,48,34,0,48),0)
        self.assertEqual(phase_expense(100,48,34,82,120),0)
        self.assertEqual(phase_expense(100,48,34,48,82),100)

    def test_fractional_timing_against_independent_monthly_ledger(self):
        from validate_stacks import ROOT,read
        data=dict(scenario=read(ROOT/'source/plan-investissement.yaml'),
            explications=read(ROOT/'source/explications-modele.yaml'),glossaire=read(ROOT/'source/glossaire.yaml'),
            taux=dict(tjm_ingenierie=.025,cloud=.03,licences_logiciels=.04),empreintes={},
            sensibilite_finance_sap={},comparaison_prix_integration={},bonus_continuite_make={'taux_pct':10})
        option=dict(stack='test',mode='Make',build=100.01,integration=300.03,build_mois=36.25,integration_mois=38.5,
            base_annuelle=dict(services_mco=120.01,hebergement=24,ipaas=36,licences_complementaires=0),
            prix_abonnements=[],ipaas_indexation_logiciel=False,ventilation_services={})
        for mode in ('Make','Buy'):
            o=deepcopy(option)
            if mode=='Buy':o.update(mode=mode,build=0,build_mois=0,prix_abonnements=[100,120])
            data['options']=[o]
            b=o['build_mois'];end=b+o['integration_mois']
            ledger=[dict(id='integration_initiale',amount=o['integration'],start=b,end=end,phase='integration',responsibility='integration_client')]
            if mode=='Make': ledger.append(dict(id='construction_core',amount=o['build'],start=0,end=b,phase='build',responsibility='core_lifecycle'))
            rows=project_financing(o,ledger,{'run':o['base_annuelle']['services_mco']},data['taux'])
            expected=independent_projection(o,data['taux'])
            for row,want in zip(rows,expected):
                for key in ('build','integration','mco_run','total'):
                    self.assertEqual(cents(row[key]),want[key])
                self.assertEqual(cents(row['total']),sum(cents(row[k]) for k in ('build','integration','mco_run')))


if __name__=='__main__':unittest.main()
