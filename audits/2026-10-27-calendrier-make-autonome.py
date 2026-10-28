"""Read-only opportunity sensitivity; never publishes or changes saved simulations."""
from pathlib import Path
import sys,json,hashlib
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'tmp/yaml-stacks/deps'))
from study_snapshot import load
from study_app import Study
from project_investment import project,phase_expense

def fingerprint(path):return hashlib.sha256(path.read_bytes()).hexdigest()
protected=[ROOT/'release/current.json',*ROOT.glob('source/**/*.yaml'),*ROOT.glob('config/*.yaml')]
before={str(p):fingerprint(p) for p in protected}
bundle=load(ROOT/'release/current.json');study=Study.from_release(bundle)
definitions={
    'reference':None,
    'accelere_26':dict(duration=26,openings=[14,18,21,24]),
    'proposition_30':dict(duration=30,openings=[16,20,24,28]),
    'prudent_36':dict(duration=36,openings=[20,25,30,34]),
}
results={}
for name,spec in definitions.items():
    data=deepcopy(study.data)
    if spec:
        for o in data['options']:
            if o['mode']!='Make':continue
            o['integration_mois']=spec['duration']
            group=o['composable']['inputs']['group']
            group['scenarios']['central']['duree_mois']=spec['duration']
            group['scenarios']['central']['ouvertures_mois']=spec['openings']
            group['transition']['stabilisation_mois']=2
            assert spec['openings'][-1]+2==spec['duration']
    projected=project(data)
    cases={}
    for o,r in zip(data['options'],projected['options']):
        ledger=r['financements_initiaux']
        horizon={}
        for h in (3,5,7,10):
            horizon[h]=dict(total=round(sum(a['total'] for a in r['annees'][:h]),2),
                remaining=round(sum(max(0,line['amount']-phase_expense(line['amount'],line['start'],line['end']-line['start'],0,h*12)) for line in ledger),2),
                service_years=max(0,h*12-o['build_mois']-o['integration_mois'])/12)
        cases[o['stack']]=dict(integration_months=o['integration_mois'],
            initial_by_phase={p:round(sum(x['amount'] for x in ledger if x['phase']==p),2) for p in ('build','integration','mco_run')},
            initial_total=round(sum(x['amount'] for x in ledger),2),
            by_funding={x['id']:x['amount'] for x in ledger},
            annual=r['annees'],horizons=horizon)
    results[name]=cases

for slug,base in results['reference'].items():
    old=next(o for o in study.baseline['options'] if o['stack']==slug)
    assert base['annual']==old['annual']
    for name in definitions:
        if slug in ('microsoft','sap'):assert results[name][slug]==base
        else:
            new=results[name][slug]
            assert new['initial_by_phase']['build']==base['initial_by_phase']['build']
            for key in ('travaux_communs','coordination_commune','deploiements','coordination_deploiements'):
                assert new['by_funding'][key]==base['by_funding'][key]
            new['delta_initial']=round(new['initial_total']-base['initial_total'],2)
            new['delta_integration']=round(new['initial_by_phase']['integration']-base['initial_by_phase']['integration'],2)
            new['delta_transitional_services']=round(new['initial_by_phase']['mco_run']-base['initial_by_phase']['mco_run'],2)
            new['delta_10y']=round(new['horizons'][10]['total']-base['horizons'][10]['total'],2)
work={}
for o in study.data['options']:
    if o['mode']!='Make':continue
    group=o['composable']['inputs']['group'];spec=group['scenarios']['central']
    rows={a['activite']:a['jh_avant_ia'] for a in o['composable']['inputs']['work']['integration']['activites'] if a['activite'] in group['substitution']['activites_conservees']}
    rows['INT-006']=spec['interfaces']*spec['jh_par_interface']
    work[o['stack']]=dict(activities=rows,common_days=sum(rows.values()),deployment_days=sum(spec['deploiement_jh_par_unite']))
assert before=={str(p):fingerprint(p) for p in protected}
report=dict(reference_release=bundle['sha256'][:12],status='proposition_non_appliquee',
    hypotheses=definitions,local_stabilization_months=2,workload=work,results=results,
    checks=dict(reference_reproduced=True,buy_unchanged=True,work_budgets_unchanged=True,source_and_release_hashes_unchanged=True))
(ROOT/'audits/2026-10-27-calendrier-make-autonome.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(work=work,summary={name:{slug:{k:v for k,v in row.items() if k not in ('annual','by_funding')} for slug,row in case.items() if slug not in ('microsoft','sap')} for name,case in results.items()}),ensure_ascii=False,indent=2))
