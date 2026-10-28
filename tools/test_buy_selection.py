"""Buy procurement funding, commercial annuities and compatibility boundaries."""
from copy import deepcopy
from decimal import Decimal
import unittest
from test_support import reference_study
from project_investment import subscription_expense,project_financing
from audit_cost_separation import independent_projection,cents
from validate_stacks import read,ROOT

class BuySelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.study=reference_study()

    def test_selection_is_once_and_preparation_is_zero(self):
        self.assertEqual(read(ROOT/'source/calibration-couts.yaml')['couts_communs']['preparation_buy'],0)
        for o in self.study.baseline['options'][3:]:
            self.assertEqual(o['selection_buy'],103200)
            self.assertEqual(o['build'],0)
            self.assertEqual(o['obtention'],103200)
            selection=[l for l in o['funding_ledger'] if l['id']=='selection_contractualisation']
            self.assertEqual(len(selection),1)
            self.assertEqual((selection[0]['start'],selection[0]['end']),(0,6))
            self.assertEqual(next(l['start'] for l in o['funding_ledger'] if l['id']=='integration_initiale'),6)
        self.assertEqual([o['service_start_month'] for o in self.study.baseline['options'][3:]],[44,36])

    def test_contractual_annuity_keeps_exact_cents_after_shift(self):
        prices=[100.01,120.03,130.07]
        for start in (0,6,6.5):
            self.assertEqual(subscription_expense(prices,.04,start,0,start),0)
            for year,price in enumerate(prices):
                self.assertEqual(subscription_expense(prices,.04,start,start+year*12,start+(year+1)*12),price)
            parts=[subscription_expense(prices,.04,start,m,m+1) for m in range(48)]
            self.assertEqual(sum(cents(v) for v in parts),cents(subscription_expense(prices,.04,start,0,48)))

    def test_buy_matches_independent_projection_and_all_horizons(self):
        for o,r in zip(self.study.data['options'][3:],self.study.baseline['options'][3:]):
            expected=independent_projection(o,self.study.data['taux'])
            for row,want in zip(r['annual'],expected):
                for key in ('build','integration','mco_run','total'):self.assertEqual(cents(row[key]),want[key])
            for horizon in r['horizons']:
                self.assertEqual(horizon['totals']['build'],103200)
                self.assertEqual(horizon['service_years'],max(0,horizon['years']*12-r['service_start_month'])/12)

    def test_buy_duration_excludes_selection_and_does_not_move_make(self):
        p=deepcopy(self.study.parameters);p['options']['microsoft']['integration_mois']=42
        result=self.study.simulate(p)
        self.assertEqual(result['options'][3]['service_start_month'],48)
        self.assertEqual(result['options'][:3],self.study.baseline['options'][:3])

if __name__=='__main__':unittest.main()
