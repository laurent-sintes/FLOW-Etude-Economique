"""Nature reading reconciles existing financing, without inferring Buy splits."""
import unittest
from copy import deepcopy
from test_support import reference_study


class CostNatureTests(unittest.TestCase):
    def test_all_options_reconcile_and_core_excludes_construction(self):
        for option in reference_study().baseline['options']:
            for row in option['annual']:
                n=row['cost_natures']
                self.assertEqual(round(sum(n.values()),2),row['total'])
                self.assertEqual(n['obtention'],row['build'])
                self.assertEqual(n['grouped_buy'],row['responsibilities']['grouped_buy'])
                self.assertEqual(n['core_care'],round(row['responsibilities']['core_lifecycle']-(row['build'] if option['mode']=='Make' else 0),2))
            for h in option['horizons']:
                self.assertEqual(round(sum(h['cost_natures'].values()),2),h['totals']['total'])

    def test_cloud_is_only_explicit_hosting_not_support_or_licences(self):
        study=reference_study()
        p=deepcopy(study.parameters)
        for values in p['options'].values():values['hebergement']=0
        result=study.simulate(p)
        for option in result['options']:
            cloud=round(sum(r['cost_natures']['run_cloud'] for r in option['annual']),2)
            self.assertEqual(cloud,option['hosting_build'])
            if option['mode']=='Make':
                self.assertGreater(sum(r['cost_natures']['operations_support'] for r in option['annual']),0)
            else:
                self.assertEqual(cloud,0)
                self.assertGreater(sum(r['cost_natures']['grouped_buy'] for r in option['annual']),0)

    def test_three_year_cloud_is_hosting_during_build(self):
        for option in reference_study().baseline['options'][:3]:
            h=next(h for h in option['horizons'] if h['years']==3)
            self.assertEqual(h['cost_natures']['run_cloud'],60000)
            self.assertEqual(h['cost_natures']['core_care'],0)

if __name__=='__main__':unittest.main()
