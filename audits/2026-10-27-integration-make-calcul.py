"""Reproduce the Make/SAP integration gap; write audit evidence only, never model inputs."""
from pathlib import Path
from collections import Counter
from decimal import Decimal
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from validate_stacks import read
from calculate_costs import calculate_option, role_rates

HERE=Path(__file__).resolve().parent
SLUGS=['java-spring','dotnet','rust']
inputs=['source/calibration-couts.yaml','source/integration.yaml','source/maintenance.yaml',
        'source/parcours-integration.yaml','source/grille-complexite.yaml','source/recalibration-metier.yaml',
        'source/couts-15-ans.yaml','sources/integration-maintenance-2026-10-22.yaml',
        'sources/calibration-couts-2026-10-22.yaml','tools/calculate_costs.py','tools/business_calibration.py']
cal=read(ROOT/inputs[0]);catalog=read(ROOT/'source/integration.yaml')
paths=read(ROOT/'source/parcours-integration.yaml');grid=read(ROOT/'source/grille-complexite.yaml')
saved={r['stack']:r for r in read(ROOT/'source/couts-15-ans.yaml')['options']}
report={'nature':'Audit independent du contrepoint Make par activites; aucune modification du modele.',
        'formula':{'normal_jh':'(gross_jh - expert_jh) * (1 - integration_gain/100)',
                   'net_jh':'normal_jh + expert_jh; no AI gain on experts',
                   'activity_cost':'normal_jh * sum(role_share * (role_rate+8)) + expert_jh * (900+8)',
                   'total':'(sum(activity_cost)+120*(integration_rate+8))*1.10+60000'},
        'options':{},'scenario':read(ROOT/'source/maintenance.yaml')['scenario_annuel']}
for slug in SLUGS:
    names=[f'source/chiffrage/chiffrage-{slug}.yaml',f'source/integration/integration-{slug}.yaml',f'source/stacks/{slug}.yaml']
    inputs+=names
    doc,integ,stack=[read(ROOT/n) for n in names]
    rates=role_rates(stack);gain=cal['ia']['integration_pct'][slug];common=cal['couts_communs'];tool=common['outillage_realisation_eur_par_jh']
    rows=[]
    for a,original,definition in zip(doc['integration']['activites'],integ['activites'],catalog['activites']):
        assert a['activite']==original['id']==definition['id']
        gross,expert=a['jh_avant_ia'],a['jh_expertise_transverse']
        normal=(gross-expert)*(1-gain/100);net=normal+expert
        per_role={r:normal*spec['part_pct']/100 for r,spec in original['roles'].items()}
        costs={r:jh*(rates[r]+tool) for r,jh in per_role.items()}
        expert_cost=expert*(common['tarif_expert_transverse_eur_jh']+tool)
        row=dict(id=a['activite'],name=definition['nom'],gross_jh=gross,expert_jh=expert,normal_net_jh=normal,
            net_jh=net,role_jh=per_role,role_costs=costs,expert_cost_eur=expert_cost,cost_eur=sum(costs.values())+expert_cost,
            jh_justification=a['justification'],catalog_justification=original['justification'],
            sources=original['sources'],tjm_fit=definition['adequation_tjm'],boundary=definition['frontiere'])
        rows.append(row)
    labour=sum(r['cost_eur'] for r in rows)
    extra_jh=common['accompagnement_applicatif_make_jh'];extra_cost=extra_jh*(rates['integration']+tool)
    before_pilot=labour+extra_cost;pilot=before_pilot*cal['pilotage']['integration_make_pct']/100
    total=round(round(before_pilot,2)+round(pilot,2)+common['preparation_make'],2)
    def variant(gain_pct,include_accompaniment):
        labour=sum((r['gross_jh']-r['expert_jh'])*(1-gain_pct/100)*sum(spec['part_pct']/100*(rates[role]+tool) for role,spec in orig['roles'].items())+r['expert_cost_eur'] for r,orig in zip(rows,integ['activites']))
        net=sum((r['gross_jh']-r['expert_jh'])*(1-gain_pct/100)+r['expert_jh'] for r in rows)
        if include_accompaniment:labour+=extra_cost;net+=extra_jh
        pilot=labour*cal['pilotage']['integration_make_pct']/100
        return dict(net_total_jh=net,labour_eur=round(labour,2),pilot_eur=round(pilot,2),preparation_eur=common['preparation_make'],total_eur=round(round(labour,2)+round(pilot,2)+common['preparation_make'],2))
    # Engine reads the raw chiffrage. Its integration tree is unchanged by business_calibration.apply.
    engine=calculate_option(slug,doc,cal)
    assert total==engine['synthese_eur_ht']['integration']==saved[slug]['synthese_eur_ht']['integration'],(slug,total)
    assert engine['detail_integration']==saved[slug]['detail_integration']
    assert engine['integration_activites']==saved[slug]['integration_activites']
    report['options'][slug]=dict(rates=rates,gain_pct=gain,tools_eur_per_jh=tool,expert_rate_eur=common['tarif_expert_transverse_eur_jh'],
        rows=rows,gross_13_jh=sum(r['gross_jh'] for r in rows),expert_jh=sum(r['expert_jh'] for r in rows),
        net_13_jh=sum(r['net_jh'] for r in rows),net_total_jh=sum(r['net_jh'] for r in rows)+extra_jh,
        cost_13_eur=labour,extra_jh=extra_jh,extra_cost_eur=extra_cost,labour_eur=before_pilot,pilot_eur=pilot,
        preparation_eur=common['preparation_make'],total_eur=total,engine_matches=True,
        source_paths=names,
        sensitivities={'sans_gains':variant(0,True),'sans_accompagnement':variant(gain,False),'sans_gains_ni_accompagnement':variant(0,False)},
        catalog_expertise_partial=[r['id'] for r in rows if r['tjm_fit']=='partielle'])
lots={l['id']:l for l in paths['lots']};blocks={r['capacite_id']:r for r in grid['blocs']}
report['map']={'scenarios':len(paths['scenarios']),'cartography_capture':paths['capture'],
    'grid_capture':grid['dependances']['cartographie'],'lots':{},'capabilities_per_subdomain':{},'scenario_examples':[]}
allcaps={c for s in paths['scenarios'] for c in s['capacites']}
for lot in paths['lots']:
    scenarios=[s for s in paths['scenarios'] if lot['id'] in s['lots']]
    caps={c for s in scenarios for c in s['capacites']}
    report['map']['lots'][lot['id']]={'activities':lot['activites'],'scenario_count':len(scenarios),
        'capability_count':len(caps),'scenario_ids':[s['scenario'] for s in scenarios]}
report['map']['covered_capabilities']=len(allcaps)
report['map']['not_in_scenarios']=[{'id':c,'subdomain':r['chemin'][1]} for c,r in blocks.items() if c not in allcaps]
report['map']['capabilities_per_subdomain']=dict(Counter(blocks[c]['chemin'][1] for c in allcaps))
report['map']['scenario_examples']=[{'id':s['scenario'],'capabilities':s['capacites'],
    'subdomains':sorted({blocks[c]['chemin'][1] for c in s['capacites']}),'lots':s['lots'],'status':s['statut']}
    for s in paths['scenarios'] if s['scenario'] in ['transfer-replenishment-order-driven','b2b-partial-stock','return-fashion-recovery','consignment-sale-pickup']]

from copy import deepcopy
from project_investment import finance_sensitivity, phase_expense
scenario=read(ROOT/'source/plan-investissement.yaml')
economic=read(ROOT/'source/couts-15-ans.yaml')
investment=read(ROOT/'source/investissements-10-ans.yaml')
anchor=finance_sensitivity(scenario,economic)
assert anchor==investment['sensibilite_finance_sap']
before_bonus=anchor['integration_sap_apres_retrait_eur_ht']
reference=round(before_bonus*(1-scenario['integration_make']['bonus_continuite_build_pct']/100),2)
assert reference==investment['bonus_continuite_make']['budget_apres_bonus_eur_ht']
sap_doc=read(ROOT/'source/chiffrage/chiffrage-sap.yaml')
report['sap_bridge']={
    'supplier_lots_eur':sap_doc['integration']['prix_rfi']['postes_eur'],
    'supplier_sum_eur':sum(sap_doc['integration']['prix_rfi']['postes_eur']),
    'supplier_printed_eur':sap_doc['integration']['prix_rfi']['total_imprime_eur'],
    **anchor,
    'bonus_pct':scenario['integration_make']['bonus_continuite_build_pct'],
    'bonus_eur':round(before_bonus-reference,2),'reference_eur':reference,
    'scope_warning':'SAP residual JH include their own programme scope and governance, not equivalent FLOW JH.'}
sap_days=anchor['jh_externes_tous_lots']-anchor['jh_finance_fpa']
sap_all_in_price=anchor['base_delaware_apres_retrait_eur_ht']/sap_days
for slug,o in report['options'].items():
    doc=read(ROOT/f'source/chiffrage/chiffrage-{slug}.yaml')
    # Existing high case: stock engineering factor, no productivity gain, purchase sensitivity.
    high=calculate_option(slug,doc,cal,'haut')['synthese_eur_ht']['integration']
    low=calculate_option(slug,doc,cal,'bas')['synthese_eur_ht']['integration']
    assert high==saved[slug]['sensibilite_eur_ht']['haut']['integration']
    assert low==saved[slug]['sensibilite_eur_ht']['bas']['integration']
    o['sensitivities']['existing_low_high']={'low_eur':low,'high_eur':high,
        'nature':'Existing generic sensitivities, not demonstrated bounds on total programme scope.'}
    o['gap_to_reference_eur']=round(reference-o['total_eur'],2)
    o['reference_ratio']=reference/o['total_eur']
    o['gross_with_accompaniment_jh']=o['gross_13_jh']+o['extra_jh']
    o['sensitivities']['sap_unit_price_only']={
        'nature':'Mechanical diagnostic only. SAP average divides cost including governance by days also including governance. Applying it to Make workdays does not fund equivalent governance volumes. First diagnostics do not recompose oversight; a separate conditional test retains the Make oversight percentage. No extra tooling on this supplier average. Original Make preparation retained. Neither test establishes equivalent scope, roles or programme governance.',
        'supplier_average_eur_per_jh':sap_all_in_price,
        'same_make_net_volume_eur':round(o['net_total_jh']*sap_all_in_price+o['preparation_eur'],2),
        'same_make_gross_volume_eur':round(o['gross_with_accompaniment_jh']*sap_all_in_price+o['preparation_eur'],2),
        'same_make_gross_volume_with_make_oversight_eur':round(o['gross_with_accompaniment_jh']*sap_all_in_price*(1+cal['pilotage']['integration_make_pct']/100)+o['preparation_eur'],2),
        'sap_remaining_days_over_make_gross':sap_days/o['gross_with_accompaniment_jh']}
report['esn_existing_sensitivity']=investment['comparaison_prix_integration']
report['decision_without_continuity_gain']={}
for option in investment['options']:
    slug=option['stack']; current=option['annees']
    if slug in SLUGS:
        start=scenario['build_make_mois'][slug]
        duration=sum(scenario['integration_buy_mois'].values())/len(scenario['integration_buy_mois'])
        for row in current:
            assert row['integration']==phase_expense(reference,start,duration,(row['annee']-1)*12,row['annee']*12)
        changed=[dict(row,integration=phase_expense(before_bonus,start,duration,(row['annee']-1)*12,row['annee']*12)) for row in current]
        for row in changed:row['total']=round(sum(row[k] for k in ['build','integration','mco_run']),2)
        assert round(sum(r['integration'] for r in changed),2)==before_bonus
    else:changed=deepcopy(current)
    report['decision_without_continuity_gain'][slug]={
        'service_years_at_10':option['annees_service_complet'],
        'horizons':{str(y):{'reference_total_eur':round(sum(r['total'] for r in current[:y]),2),
                           'without_gain_total_eur':round(sum(r['total'] for r in changed[:y]),2),
                           'delta_eur':round(sum(r['total'] for r in changed[:y])-sum(r['total'] for r in current[:y]),2)} for y in [3,5,7,10]}}
inputs+=['source/plan-investissement.yaml','source/investissements-10-ans.yaml',
         'source/chiffrage/chiffrage-sap.yaml','tools/project_investment.py','sources/client/delaware-septembre.pdf']
report['stored_economics_hash_checks']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
    for p,h in investment['dependances'].items()}
report['changed_witness_dependencies']=[p for p,ok in report['stored_economics_hash_checks'].items() if not ok]
# A glossary edit can change the dependency fingerprint without changing any budget.
# Verify the full active economic results instead of silently trusting an old hash.
from calculate_costs import calculate
fresh=calculate()
assert fresh['options']==economic['options'],'The active economic results differ from the witness'
assert set(report['changed_witness_dependencies'])<= {'source/glossaire.yaml'},'Review changed non-editorial dependencies'
report['full_active_economic_results_equal_saved']=True
report['source_hashes']={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in sorted(set(inputs))}
output=HERE/'2026-10-27-integration-make-preuves.json'
output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
summary={slug:{k:v for k,v in o.items() if k not in ['rows','source_paths']} for slug,o in report['options'].items()}
print(json.dumps({'options':summary,'sap_bridge':report['sap_bridge'],'decision':report['decision_without_continuity_gain']},ensure_ascii=False,indent=2))
