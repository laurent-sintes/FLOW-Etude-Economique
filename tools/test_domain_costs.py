"""Business domain ownership, missing keys and exact conservation of adopted budgets."""
from copy import deepcopy
from decimal import Decimal
import hashlib
import unittest
from domain_costs import core_reading, context, classify, summarize, SOURCE
from test_support import active_reference, reference_study
from validate_stacks import ROOT, read


class DomainCostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study=reference_study()
        cls.units=next(o for o in cls.study.economic['options'] if o['stack']=='java-spring')['core_units']

    def test_domain_totals_conserve_and_shared_remains_pending(self):
        before=deepcopy(self.units)
        result=core_reading(self.units)
        self.assertEqual(self.units,before)
        b={r['id']:r for r in result['buckets']}
        ref=active_reference()
        md=ref['units']['master-data-java-spring']
        self.assertEqual((b['domain-master-data']['measures']['jh']['total'],b['domain-master-data']['measures']['cost_eur_ht']['total']),(md['jh'],md['cost_eur_ht']))
        self.assertEqual((b['supply-chain-orchestration']['measures']['jh']['total'],b['supply-chain-orchestration']['measures']['cost_eur_ht']['total']),(5890,3804095))
        self.assertEqual((b['unallocated']['measures']['jh']['total'],b['unallocated']['measures']['cost_eur_ht']['total']),(540,360495))
        self.assertFalse(result['domain_totals_complete'])
        self.assertIsNone(b['domain-master-data']['full_totals']['cost_eur_ht'])
        self.assertIsNone(b['supply-chain-orchestration']['full_totals']['cost_eur_ht'])
        self.assertEqual(result['pending_unit_refs'],['core/professional-it-java-spring'])
        self.assertEqual(result['measures']['cost_eur_ht']['total'],ref['cost_eur_ht'])
        self.assertEqual(sum(Decimal(str(r['measures']['cost_eur_ht']['total'])) for r in b.values()),Decimal(str(ref['cost_eur_ht'])))
        refs=[r for bucket in b.values() for r in bucket['unit_refs']]
        self.assertEqual(len(refs),len(set(refs)))
        self.assertEqual(len(refs),len(self.units))
        self.assertIn('core/operational-references-java-spring',b['supply-chain-orchestration']['unit_refs'])
        self.assertIn('core/supply-workbenches-java-spring',b['supply-chain-orchestration']['unit_refs'])
        self.assertEqual(b['domain-master-data']['unit_refs'],['core/master-data-java-spring'])

    def test_native_hierarchy_is_exhaustive_and_cannot_be_overridden(self):
        ctx=context()
        self.assertEqual(len(ctx['capabilities']),116)
        self.assertEqual(sum(d=='domain-master-data' for d in ctx['capabilities'].values()),33)
        self.assertEqual(sum(d=='supply-chain-orchestration' for d in ctx['capabilities'].values()),83)
        self.assertEqual(hashlib.sha256((ROOT/'sources/cartographie-scm-2026-10-24.yaml').read_bytes()).hexdigest(),'a1fc16bac87e206124485aee8fa51b49b774a4352e36721731662e868dbe6976')
        ctx['overrides']['core/master-data-java-spring']=dict(work_unit_ref='core/master-data-java-spring',status='direct',domain_refs=['supply-chain-orchestration'])
        with self.assertRaisesRegex(ValueError,'cannot be overwritten'):
            classify('core/master-data-java-spring',[next(c for c,d in ctx['capabilities'].items() if d=='domain-master-data')],ctx)
        doc=read(ROOT/SOURCE);doc['overrides'][0]['domain_refs']=['invented']
        with self.assertRaisesRegex(ValueError,'Unknown native domain'):core_reading(self.units,doc)
        doc=read(ROOT/SOURCE);doc['overrides'][0]['work_unit_ref']='missing'
        with self.assertRaisesRegex(ValueError,'Unknown classification work'):core_reading(self.units,doc)

    def test_missing_and_cross_domain_values_are_not_zero_or_duplicated(self):
        ctx=context();caps=ctx['capabilities']
        md=next(c for c in caps if caps[c]=='domain-master-data');scm=next(c for c in caps if caps[c]=='supply-chain-orchestration')
        rows=[dict(id='shared',jh=10,cost_eur_ht=.01,domain_classification=classify('shared',[md,scm],ctx)),dict(id='unknown',jh=None,cost_eur_ht=None,domain_classification=classify('unknown',[],ctx))]
        result=summarize(rows,ctx)
        pending=result['buckets'][-1]
        self.assertEqual(pending['unit_refs'],['shared','unknown'])
        self.assertEqual(pending['measures']['cost_eur_ht'],dict(known=.01,missing=1,total=None))
        self.assertIsNone(result['measures']['jh']['total'])
        with self.assertRaisesRegex(ValueError,'Duplicate source amount'):summarize(rows+[rows[0]],ctx)
        with self.assertRaisesRegex(ValueError,'Unknown native capability'):classify('x',['invented'],ctx)

    def test_all_readings_share_classification_and_keep_economics(self):
        s=self.study;expected=core_reading(self.units)
        gross=s.content['gross_evaluations']['phases']['acquisition']['options']['java-spring']['core']['domain_reading']
        economic=next(o for o in s.content['economic_evaluations']['options'] if o['stack']=='java-spring')['core']['domain_reading']
        self.assertEqual(gross,expected);self.assertEqual(economic,expected)
        catalog=s.content['delivery_organisation']['work_catalog']
        for unit in catalog['units']:
            if unit['id'] in expected['classifications']:
                self.assertEqual(unit['domain_classification'],expected['classifications'][unit['id']])
        for phase,reading in catalog['domain_readings'].items():
            rows=[u for u in catalog['units'] if u['phase_ref']==phase]
            for field in ('jh','cost_eur_ht'):
                known=sum(Decimal(str(u['totals'][field])) for u in rows if u['totals'][field] is not None)
                actual=reading['measures'][field]['known']
                if actual is None:self.assertFalse(any(u['totals'][field] is not None for u in rows))
                elif field=='jh':self.assertAlmostEqual(actual,float(known),places=8)
                else:self.assertEqual(Decimal(str(actual)),known)
        self.assertFalse(catalog['domain_readings']['integration']['domain_totals_complete'])
        self.assertFalse(catalog['domain_readings']['fonctionnement']['domain_totals_complete'])
