"""G02 experimental acceptance model. Not Axelor, not production software or sizing evidence."""
from copy import deepcopy
from dataclasses import dataclass,field
import json,unittest,time
from pathlib import Path

@dataclass
class Experiment:
    planned:int=100
    eta:int=30
    physical:int=0
    version:int=0
    assignments:dict=field(default_factory=dict)
    seen_receipts:dict=field(default_factory=dict)
    # These quotas are fixture assumptions, not approved Beaumanoir policy.
    quotas:dict=field(default_factory=lambda:{'web':60,'wholesale':40})
    def commit(self,expected,demand,channel,qty,due,*,frozen=False,season='SS'):
        if expected!=self.version:raise ValueError('stale')
        if qty<0 or due<self.eta or season!='SS':raise ValueError('ineligible')
        old=self.assignments.get(demand)
        if old and old['frozen'] and old['qty']!=qty:raise ValueError('frozen')
        other={k:v for k,v in self.assignments.items() if k!=demand}
        physical=old['physical'] if old else 0
        if qty<physical:raise ValueError('below_physical_reservation')
        if sum(x['qty']-x['physical'] for x in other.values())+qty-physical>self.planned:raise ValueError('supply_exceeded')
        if sum(x['qty'] for x in other.values() if x['channel']==channel)+qty>self.quotas[channel]:raise ValueError('quota')
        self.assignments[demand]=dict(channel=channel,qty=qty,physical=physical,due=due,frozen=frozen,season=season)
        self.version+=1
    def receipt(self,key,qty):
        if key in self.seen_receipts:
            if self.seen_receipts[key]!=qty:raise ValueError('receipt_payload_conflict')
            return
        if not 0<=qty<=self.planned:raise ValueError('receipt_quantity')
        # Proposed receipt conversion, preserving source link and total commitment.
        self.planned-=qty;self.physical+=qty;left=qty
        for x in sorted(self.assignments.values(),key=lambda x:not x['frozen']):
            converted=min(left,x['qty']-x['physical']);x['physical']+=converted;left-=converted
        self.seen_receipts[key]=qty;self.version+=1
    def delay(self,new_eta):
        self.eta=new_eta;self.version+=1
        return [k for k,v in self.assignments.items() if v['qty']>v['physical'] and v['due']<new_eta]
    def reduce_supply(self,remaining):
        if remaining<0:raise ValueError('negative')
        self.planned=remaining;self.version+=1
        # External truth is accepted, even when commitments become infeasible.
        return max(0,sum(x['qty']-x['physical'] for x in self.assignments.values())-self.planned)
    def release(self,demand):
        self.assignments.pop(demand);self.version+=1

class AcceptanceTests(unittest.TestCase):
    def test_future_supply_does_not_create_physical_stock(self):
        m=Experiment();m.commit(0,'A','web',60,30);self.assertEqual(m.physical,0);self.assertEqual(m.planned,100)
    def test_no_promise_before_eta(self):
        m=Experiment()
        with self.assertRaisesRegex(ValueError,'ineligible'):m.commit(0,'A','web',60,10)
    def test_scalar_future_balance_is_not_an_atp_by_date(self):
        # Counterexample to using an undated balance as the only availability check.
        aggregate=0+100-60;self.assertEqual(aggregate,40)
        m=Experiment()
        with self.assertRaisesRegex(ValueError,'ineligible'):m.commit(0,'A','web',60,10)
    def test_two_channels_can_share_supply_under_proposed_quotas(self):
        m=Experiment();m.commit(0,'A','web',60,30);m.commit(1,'B','wholesale',40,30)
        self.assertEqual(sum(x['qty'] for x in m.assignments.values()),100)
    def test_cannot_overbook_source(self):
        m=Experiment(quotas={'web':100,'wholesale':100});m.commit(0,'A','web',80,30)
        with self.assertRaisesRegex(ValueError,'supply_exceeded'):m.commit(1,'B','wholesale',30,30)
    def test_cannot_bypass_channel_quota(self):
        m=Experiment()
        with self.assertRaisesRegex(ValueError,'quota'):m.commit(0,'A','web',70,30)
    def test_wrong_season_is_rejected(self):
        m=Experiment()
        with self.assertRaisesRegex(ValueError,'ineligible'):m.commit(0,'A','web',10,30,season='AW')
    def test_late_supply_preserves_commitment_and_exposes_breach(self):
        m=Experiment();m.commit(0,'A','web',60,30,frozen=True)
        self.assertEqual(m.delay(40),['A']);self.assertEqual(m.assignments['A']['qty'],60)
    def test_partial_receipt_does_not_double_count_supply(self):
        m=Experiment();m.receipt('R1',40)
        self.assertEqual((m.physical,m.planned),(40,60));self.assertEqual(m.physical+m.planned,100)
    def test_receipt_replay_has_no_second_effect(self):
        m=Experiment();m.receipt('R1',40);v=m.version;m.receipt('R1',40)
        self.assertEqual((m.physical,m.planned,m.version),(40,60,v))
    def test_frozen_assignment_is_not_silently_reallocated(self):
        m=Experiment();m.commit(0,'A','web',60,30,frozen=True)
        with self.assertRaisesRegex(ValueError,'frozen'):m.commit(1,'A','web',20,30)
    def test_cancellation_accepts_reduced_supply_and_reports_shortfall(self):
        m=Experiment();m.commit(0,'A','web',60,30,frozen=True)
        self.assertEqual(m.reduce_supply(20),40);self.assertEqual(m.assignments['A']['qty'],60)
    def test_competing_commands_need_a_shared_version_gate(self):
        m=Experiment();m.commit(0,'A','web',60,30)
        with self.assertRaisesRegex(ValueError,'stale'):m.commit(0,'B','wholesale',40,30)
        self.assertNotIn('B',m.assignments)
    def test_receipt_converts_assignment_without_a_second_commitment(self):
        m=Experiment();m.commit(0,'A','web',60,30);m.commit(1,'B','wholesale',40,30);m.receipt('R1',40)
        self.assertEqual(sum(x['qty']-x['physical'] for x in m.assignments.values()),60)
        self.assertEqual(sum(x['physical'] for x in m.assignments.values()),40)
        self.assertEqual(sum(x['qty'] for x in m.assignments.values()),100)
    def test_completed_assignment_is_not_breached_by_remaining_supply_delay(self):
        m=Experiment();m.commit(0,'A','web',40,30);m.receipt('R1',40)
        self.assertEqual(m.delay(40),[])
    def test_replayed_receipt_with_changed_payload_is_rejected(self):
        m=Experiment();m.receipt('R1',40)
        with self.assertRaisesRegex(ValueError,'receipt_payload_conflict'):m.receipt('R1',50)
    def test_release_frees_future_assignment(self):
        m=Experiment();m.commit(0,'A','web',60,30);m.release('A');m.commit(2,'C','web',60,30)
        self.assertNotIn('A',m.assignments)
    def test_simulation_is_isolated_and_stale_application_rejected(self):
        m=Experiment();scenario=deepcopy(m);scenario.commit(0,'A','web',60,30)
        self.assertFalse(m.assignments);m.delay(40)
        with self.assertRaisesRegex(ValueError,'stale'):m.commit(0,'A','web',60,40)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path.cwd()/'tmp/g02-acceptance-latest.json')
    args=parser.parse_args()
    start=time.perf_counter();suite=unittest.defaultTestLoader.loadTestsFromTestCase(AcceptanceTests)
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    report=dict(status='passed' if result.wasSuccessful() else 'failed',tests=result.testsRun,seconds=round(time.perf_counter()-start,4),scope='Experimental acceptance model on synthetic fixtures. No Axelor runtime, database, concurrency stress or effort calibration.',test_ids=unittest.defaultTestLoader.getTestCaseNames(AcceptanceTests),fixture_policy='Quotas, season and timing are illustrative assumptions, not approved business rules.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    raise SystemExit(0 if result.wasSuccessful() else 1)
