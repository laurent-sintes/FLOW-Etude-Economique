"""Ownership, unknown values, conserved funding and unchanged simulations."""
from copy import deepcopy
from decimal import Decimal
import unittest
from jsonschema import ValidationError

from delivery_organisation import SOURCE, build_organisation, partition, validate
from test_support import reference_study
from validate_stacks import ROOT, read


class DeliveryOrganisationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = reference_study()
        cls.document = read(ROOT / SOURCE)

    def test_partition_conserves_each_phase_and_existing_funding(self):
        org = self.study.content['delivery_organisation']
        phases = {p['id']:p for p in org['reading']['phases']}
        option = next(o for o in self.study.baseline['options'] if o['stack']=='java-spring')
        annual = next(o for o in self.study.content['economic_evaluations']['options'] if o['stack']=='java-spring')['annual']
        self.assertEqual(phases['acquisition']['totals']['cost_eur_ht'],option['obtention']+option['hosting_build'])
        expected_integration=sum(Decimal(str(r['amount'])) for r in option['funding_ledger'] if r['start']>=option['initial_months'])
        self.assertEqual(Decimal(str(phases['integration']['totals']['cost_eur_ht'])),expected_integration)
        self.assertEqual(phases['fonctionnement']['totals']['cost_eur_ht'],annual['total_eur_ht'])
        for phase in phases.values():
            for measure in ('jh','cost_eur_ht'):
                values=[b[measure] for b in phase['buckets'] if b[measure] is not None]
                if phase['totals'][measure] is None:self.assertFalse(values)
                else:self.assertAlmostEqual(sum(values),phase['totals'][measure],places=7)
        records=org['reading']['records']
        self.assertEqual(len(records),len({r['id'] for r in records}))
        self.assertFalse(any(r['id']=='funding/construction_core' for r in records))
        self.assertTrue(any(r['object']=='core_system' and r['phase']=='integration' and r['cost_eur_ht'] for r in records))
        self.assertIsNone(phases['integration']['totals']['jh'])
        self.assertTrue(all(r['jh'] is None and not r['roles'] for r in records if r['phase']=='integration'))

    def test_allocation_table_has_values_sources_and_a_conserved_cell_per_owner_and_phase(self):
        org=self.study.content['delivery_organisation'];table=org['allocation_table']
        self.assertEqual(table['option'],'java-spring')
        self.assertEqual(table['zone'],'paris')
        self.assertEqual(len(table['rows']),3*(len(org['teams'])+2))
        self.assertEqual(table['records'],org['reading']['records'])
        for phase in org['reading']['phases']:
            rows=[r for r in table['rows'] if r['phase_ref']==phase['id']]
            refs=[id for r in rows for id in r['record_ids']]
            self.assertEqual(len(refs),len(set(refs)))
            self.assertEqual(set(refs),{r['id'] for r in table['records'] if r['phase']==phase['id']})
            for field in ('jh','cost_eur_ht'):
                values=[r[field] for r in rows if r[field] is not None]
                if phase['totals'][field] is None:self.assertFalse(values)
                else:self.assertAlmostEqual(sum(values),phase['totals'][field],places=7)
            self.assertTrue(all(r['period_basis']==('annual' if phase['id']=='fonctionnement' else 'phase') for r in rows))
        unallocated=next(r for r in table['rows'] if r['owner_kind']=='unallocated' and r['phase_ref']=='integration')
        self.assertGreater(unallocated['cost_eur_ht'],0)
        self.assertIsNone(unallocated['team_ref'])
        b2c=next(r for r in table['rows'] if r['team_ref']=='b2c')
        self.assertIsNone(b2c['cost_eur_ht'])

    def test_lifecycle_types_and_governance_are_separate(self):
        org=self.study.content['delivery_organisation']
        self.assertEqual(len(org['teams']),11)
        self.assertEqual(sum(t['type']=='stream-aligned' for t in org['teams']),6)
        self.assertNotIn(org['governance']['id'],{t['id'] for t in org['teams']})
        for team in org['teams']:
            self.assertEqual(set(team['responsibilities']),{'acquisition','integration','fonctionnement'})
            self.assertTrue(all(v is None for v in team['capacity'].values()))
        self.assertEqual(org['principle']['id'],'durable-product-teams')

    def test_candidates_do_not_receive_fictitious_shares_or_zero_capacity(self):
        org=self.study.content['delivery_organisation']
        row=next(r for r in org['reading']['records'] if r['id']=='core/orders-java-spring')
        self.assertIsNone(row['team_ref'])
        self.assertEqual(set(row['candidate_refs']),{'b2c','wholesale','sourcing-procurement'})
        for phase in org['reading']['phases']:
            b=next(b for b in phase['buckets'] if b['team_ref']=='b2c')
            self.assertIsNone(b['jh'])
            self.assertIsNone(b['cost_eur_ht'])
        # A known zero remains distinct from an unknown, empty bucket.
        record=dict(id='zero',phase='acquisition',team_ref='known',jh=0,cost_eur_ht=0)
        buckets=partition([record],['known','unknown'])[0]['buckets']
        self.assertEqual(next(b for b in buckets if b['team_ref']=='known')['jh'],0)
        self.assertIsNone(next(b for b in buckets if b['team_ref']=='unknown')['jh'])

    def test_duplicate_sources_unknown_owners_and_invalid_measures_fail(self):
        row=dict(id='one',phase='acquisition',team_ref='team',jh=1,cost_eur_ht=12.5)
        for rows in ([row,row],[dict(row,team_ref='missing')],[dict(row,jh=float('nan'))],[dict(row,cost_eur_ht=-1)],[dict(row,phase='missing')]):
            with self.subTest(rows=rows),self.assertRaises(ValueError):
                partition(rows,['team'])

    def test_model_rejects_undefined_references_and_software_ownership_by_enabling(self):
        for change in [lambda d:d['teams'].append(deepcopy(d['teams'][0])),
                       lambda d:d['teams'][0].update(type='missing'),
                       lambda d:d['work_owners'].append(deepcopy(d['work_owners'][0])),
                       lambda d:d['work_owners'][0].update(team_ref='missing'),
                       lambda d:d['work_owners'][0].update(team_ref='integration',candidate_refs=['integration']),
                       lambda d:d['interactions'][0].update(target='missing'),
                       lambda d:next(r for r in d['interactions'] if r['mode']=='facilitating').update(exit_criterion='')]:
            doc=deepcopy(self.document);change(doc)
            with self.assertRaises((ValueError,ValidationError)):
                validate(doc)

    def test_scope_and_funding_drift_fail_without_mutating_inputs(self):
        before=deepcopy((self.study.economic,self.study.baseline,self.study.content))
        result=build_organisation(self.study.economic,self.study.baseline,self.study.content)
        self.assertEqual((self.study.economic,self.study.baseline,self.study.content),before)
        doc=deepcopy(self.document);doc['work_owners']=[r for r in doc['work_owners'] if r['ref']!='orders-java-spring']
        with self.assertRaisesRegex(ValueError,'scope drift'):
            build_organisation(self.study.economic,self.study.baseline,self.study.content,doc)
        baseline=deepcopy(self.study.baseline)
        next(o for o in baseline['options'] if o['stack']=='java-spring')['build']+=1
        with self.assertRaisesRegex(ValueError,'Core cost'):
            build_organisation(self.study.economic,baseline,self.study.content)
        self.assertEqual(result,self.study.content['delivery_organisation'])

    def test_bootstrap_and_model_export_include_the_same_authority(self):
        bootstrap=self.study.bootstrap(essential=True)
        self.assertTrue(bootstrap['content']['delivery_organisation']['deferred'])
        self.assertEqual(bootstrap['content']['delivery_organisation']['principle'],self.study.content['delivery_organisation']['principle'])
        self.assertEqual(self.study.organisation_reading()['delivery_organisation'],self.study.content['delivery_organisation'])
        self.assertIn(SOURCE,self.study.files)
        self.assertIn('source/schema-organisation-delivery.yaml',self.study.files)
        model=self.study.fundamentals['estimation_model']
        self.assertIn('delivery_team',{o['id'] for o in model['objects']})
        self.assertIn('delivery_allocation_conservation',{r['id'] for r in model['rules']})


if __name__=='__main__':
    unittest.main()
