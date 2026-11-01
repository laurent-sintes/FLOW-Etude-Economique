"""Documentary observations stay distinct from chosen FLOW tariffs and provisions."""
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import unittest
from validate_stacks import ROOT, read
from prestudy_costs import SOURCE, SCHEMA, INFLATION, PROOFS, compile_cost_evidence

class PreStudyCostsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=read(ROOT/SOURCE);cls.schema=read(ROOT/SCHEMA)
        cls.stacks={slug:dict(model=read(ROOT/('source/stacks/'+slug+'.yaml'))) for slug in ['java-spring','dotnet','rust','microsoft','sap']}
        cls.market=read(ROOT/'source/references-couts-integration.yaml')
        cls.inflation=read(ROOT/INFLATION);cls.proofs=read(ROOT/PROOFS)
    def build(self,spec=None,stacks=None,inflation=None):
        return compile_cost_evidence(self.spec if spec is None else spec,self.schema,self.stacks if stacks is None else stacks,self.market,self.inflation if inflation is None else inflation,self.proofs)
    def test_observed_qa_range_is_not_the_flow_assumption(self):
        row=next(row for row in self.build()['rates'] if row['id']=='qa-senior-paris')
        self.assertEqual((row['min'],row['max']),(530,700))
        self.assertEqual(self.stacks['java-spring']['model']['interventions']['tarifs']['qa']['bas'],500)
        self.assertNotIn('reference',row)
        self.assertEqual(set(row['stacks']),set(self.stacks))
    def test_missing_support_range_is_unknown_and_rust_keeps_its_conflict(self):
        rows={row['id']:row for row in self.build()['rates']}
        self.assertIsNone(rows['support-senior']['min']);self.assertIsNone(rows['support-senior']['max'])
        self.assertEqual(rows['rust-signal']['kind'],'signal_contradictoire')
        self.assertEqual(len(rows['rust-signal']['evidence']),2)
        self.assertEqual(rows['rust-signal']['price_date'],'2026-10-09')
        self.assertIsNone(rows['architecture-confirme']['price_date'])
    def test_freelance_segments_and_supplier_reference_keep_their_identity(self):
        rows={row['id']:row for row in self.build()['rates']}
        self.assertEqual((rows['sap-confirme']['min'],rows['sap-confirme']['max']),(750,950))
        self.assertEqual((rows['sap-senior']['min'],rows['sap-senior']['max']),(950,1250))
        supplier=rows['avanade-pilote-esn']
        self.assertEqual((supplier['purchase_mode'],supplier['tax_status'],supplier['price_date']),('esn','HT','2025'))
        self.assertEqual(supplier['evidence'][0]['path'],'sources/client/microsoft-1.pdf')
    def test_chosen_tariffs_and_future_indexation_cannot_change_observations(self):
        stacks=deepcopy(self.stacks);inflation=deepcopy(self.inflation)
        for stack in stacks.values():
            for row in stack['model']['interventions']['tarifs'].values():
                row.update(reference=999999,bas=999998,haut=999999)
        for category in inflation['categories'].values():category['taux_annuel_pct']['central']=99
        self.assertEqual(self.build(),self.build(stacks=stacks,inflation=inflation))
    def test_projection_is_frozen_isolated_and_retains_original_effort_rows(self):
        before=deepcopy((self.spec,self.stacks,self.market,self.inflation,self.proofs))
        with patch.object(Path,'read_bytes',side_effect=AssertionError('unexpected disk read')):shown=self.build()
        self.assertEqual(shown['effort_groups']['programmes'],[row for row in self.market['reperes_build_core']['lignes'] if row['composant'] in self.spec['effort_groups']['programmes']])
        shown['rates'][0]['min']=-1;shown['indices'][0]['observations'].clear()
        self.assertEqual((self.spec,self.stacks,self.market,self.inflation,self.proofs),before)
    def test_programme_budgets_keep_original_currency_and_period_without_transposition(self):
        programmes={row['id']:row for row in self.build()['programmes']}
        self.assertEqual((programmes['openlmis-programme']['amount'],programmes['openlmis-programme']['currency']),(5112355,'USD'))
        self.assertEqual(programmes['relex-nexgenfscm']['period'],'2016–2018')
        self.assertEqual(programmes['w-response']['period'],'2004–2007')
        self.assertTrue(all('transposed' not in row and 'normalized' not in row for row in programmes.values()))

    def test_ai_results_keep_experimental_context_and_do_not_adopt_a_gain(self):
        rows=self.build()['ai']
        self.assertEqual(len(rows),3)
        self.assertEqual([row['published_on'] for row in rows],['2023-02-13','2025-07-10','2026-02-24'])
        self.assertIn('55,8 %',rows[0]['observed_result'])
        self.assertIn('19 %',rows[1]['observed_result'])
        self.assertIn('fiablement',rows[2]['observed_result'])
        self.assertTrue(all(row['population'] and row['limit'] and row['evidence']['path'].startswith('https://') for row in rows))
        changed=deepcopy(self.spec);changed['ai_refs'][0]['observed_result']='Different observation'
        before=self.build();after=self.build(spec=changed)
        self.assertEqual(before['rates'],after['rates'])
        self.assertEqual(before['products'],after['products'])
        self.assertNotIn('gain',after['ai'][0])

    def test_bad_provenance_and_partial_ranges_fail_before_publication(self):
        for change in ('duplicate','source','owner','basis','partial','order','group','extra'):
            spec=deepcopy(self.spec)
            if change=='duplicate':spec['rates'].append(deepcopy(spec['rates'][0]))
            if change=='source':spec['rates'][0]['source_ids']=['missing']
            if change=='owner':spec['rates'][0]['source_stack']='missing'
            if change=='basis':spec['rates'][0]['basis_ref']='interventions/missing'
            if change=='partial':spec['rates'][0]['min']=None
            if change=='order':spec['rates'][0]['min']=9999
            if change=='group':spec['effort_groups']['programmes']=['missing']
            if change=='extra':spec['rates'][0]['retained_price']=550
            with self.subTest(change=change),self.assertRaisesRegex(ValueError,'ERR_PRESTUDY_COSTS'):self.build(spec=spec)

if __name__=='__main__':unittest.main()
