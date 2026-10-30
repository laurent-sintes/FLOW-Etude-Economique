"""Regression gates for the approved composable reference and funding boundaries."""
from copy import deepcopy
from pathlib import Path
import json
import unittest
from project_investment import prepare, project, phase_expense
from composable_costs import initial_ledger, allocate
from test_support import reference_study
from audit_cost_separation import independent_projection, cents
from validate_stacks import ROOT


class ComposableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=deepcopy(reference_study().data);cls.result=project(deepcopy(cls.data))

    def test_active_inputs_do_not_import_audit_prices(self):
        for path in ('tools/composable_costs.py','source/modele-composable.yaml','source/deploiement-groupe.yaml'):
            self.assertNotIn('audits/',(ROOT/path).read_text(encoding='utf-8'))

    def test_buy_schedule_matches_independent_monthly_calculation(self):
        for option,result in zip(self.data['options'][3:],self.result['options'][3:]):
            expected=independent_projection(option,self.data['taux'])
            for row,want in zip(result['annees'],expected):
                for key in ('build','integration','mco_run','total'):
                    self.assertEqual(cents(row[key]),want[key])

    def test_funding_once_and_all_horizons_reconcile(self):
        for option in self.result['options']:
            ids=[r['id'] for r in option['financements_initiaux']]
            self.assertEqual(len(ids),len(set(ids)))
            for horizon in (3,5,7,10):
                years=option['annees'][:horizon]
                total=round(sum(y['total'] for y in years),2)
                self.assertEqual(total,round(sum(sum(y['responsibilities'].values()) for y in years),2))
            for row in option['annees']:
                self.assertEqual(row['total'],round(sum(row[k] for k in ('build','integration','mco_run')),2))

    def test_build_and_transition_hosting_do_not_overlap(self):
        for o,r in zip(self.data['options'][:3],self.result['options'][:3]):
            ledger=r['financements_initiaux'];b=o['build_mois']
            before=[l for l in ledger if l['id'].startswith('hebergement_build/')]
            after=[l for l in ledger if l['id'].startswith('moyens_transition/')]
            self.assertEqual(before[0]['start'],0)
            self.assertEqual(before[-1]['end'],b)
            self.assertTrue(all(l['start']==b for l in after))
            self.assertTrue(all(l['end']<=b+o['integration_mois'] for l in ledger))
            # Three-year Run is the first two hosting phases, not a production annuity.
            self.assertEqual(sum(y['responsibilities']['run'] for y in r['annees'][:3]),60000)

    def test_mco_follows_acceptance_and_core_is_separate(self):
        ledger=self.result['options'][0]['financements_initiaux']
        client=[r for r in ledger if r['responsibility']=='mco_client']
        self.assertTrue(all(r['start']>=66 for r in client))
        self.assertTrue(all('core' not in r['id'] for r in client))
        self.assertEqual(next(r['start'] for r in ledger if r['id']=='cycle_core_transition'),48)
        self.assertEqual(sum(r['amount'] for r in ledger if r['id'] in ('MAI-005/reception','MAI-006/reception')),18079.2)

    def test_durations_and_zero_service_assumptions(self):
        for b,d in ((36,6),(37.5,33.5),(60,60)):
            data=deepcopy(self.data);o=data['options'][0];o.update(build_mois=b,integration_mois=d)
            result=project(data)['options'][0]
            ledger=result['financements_initiaux']
            shared=next(l for l in ledger if l['id']=='MAI-006/reception')
            self.assertAlmostEqual(shared['end']-shared['start'],2)
            self.assertAlmostEqual(max(l['end'] for l in ledger),b+d)
            self.assertEqual(round(sum(l['amount'] for l in ledger if l['id'].startswith('hebergement_build/')),2),102000*b/48)
            for line in ledger:
                paid=sum(phase_expense(line['amount'],line['start'],line['end']-line['start'],m,m+1) for m in range(120))
                self.assertAlmostEqual(paid,line['amount'],places=2)
        data=deepcopy(self.data);o=data['options'][0]
        o['ventilation_services'].update(core=0,integration=0);o['base_annuelle']['services_mco']=0
        r=project(data)['options'][0]
        self.assertEqual(next(l['amount'] for l in r['financements_initiaux'] if l['id']=='cycle_core_transition'),0)
        self.assertEqual(allocate(.01,[1,1,1]),[0,.01,0])


if __name__=='__main__':unittest.main()
