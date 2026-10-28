"""Conditional Group proposal. Writes only its audit evidence; no active model writes."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from copy import deepcopy
import hashlib, json, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from validate_stacks import read

HERE=Path(__file__).resolve().parent
DEFINITION=HERE/'2026-10-27-enveloppe-groupe-make.yaml'
cfg=read(DEFINITION)
glossary_path=ROOT/cfg['lecture_couts']['glossaire']
notions=read(glossary_path)['notions']
cost_groups=cfg['lecture_couts']['natures']
assert set(cost_groups)=={'integration_migration','mco_run'}
assert cfg['lecture_couts']['build_core_system_hors_enveloppe'] is True
assert cfg['transition']['nature_cout_ref']=='mco_run'
for nature in cost_groups:assert nature in notions
base_path=ROOT/cfg['base']
base=json.loads(base_path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def active_hashes():
    return {p.relative_to(ROOT).as_posix():sha(p) for folder in ['source','sources','config','tools','app/src']
            for p in sorted((ROOT/folder).rglob('*')) if p.is_file() and p.suffix in ['.yaml','.py','.tsx','.ts','.css','.md','.json','.pdf','.xlsx','.pptx','.docx']}
before=active_hashes()
for path,digest in base['make']['source_hashes'].items():
    assert sha(ROOT/path)==digest, f'Stale base input: {path}'
for name,digest in base['audit_dependencies_hashes'].items():
    assert sha(HERE/name)==digest, f'Stale base audit: {name}'

cal=read(ROOT/'source/calibration-couts.yaml')
business=read(ROOT/'source/recalibration-metier.yaml')
annual=read(ROOT/'source/maintenance.yaml')['scenario_annuel']
grid=read(ROOT/'source/grille-complexite.yaml')
bycap={b['capacite_id']:b for b in grid['blocs']}
assert set(cfg['deploiement']['cartographie']) <= set(bycap)
assert sum(cfg['perimetre']['repartition_usagers_par_unite'])==1
assert cfg['perimetre']['unites_deploiement']==len(cfg['perimetre']['poles_candidats'])==len(cfg['perimetre']['repartition_usagers_par_unite'])
assert cfg['perimetre']['utilisateurs']==annual['perimetre']['utilisateurs_nominatifs']
for key in ['applications_externes','donnees_actives_to','donnees_archives_to']:
    assert cfg['perimetre'][key]==annual['perimetre'][key], f'Recalibrate the retained work before changing {key}'
assert cfg['substitution']['accompagnement_retire'] is True
assert cfg['substitution']['preparation_retiree'] is True
assert cfg['core']['activite']=='MAI-003' and cfg['core']['debut_mois']==0
assert cfg['transition']['infrastructure_debut_mois']==0
assert set(cfg['substitution']['activites_conservees']).isdisjoint(cfg['substitution']['activites_retirees'])
assert set(cfg['substitution']['activites_conservees']+cfg['substitution']['activites_retirees'])=={f'INT-{i:03}' for i in range(1,14)}
assert set(cfg['transition']['services_partages']).isdisjoint(cfg['transition']['services_variables'])
for key in ['services_partages','services_variables','infrastructure_annuelle_refs']:
    assert len(cfg['transition'][key])==len(set(cfg['transition'][key]))
assert 'MAI-003' not in cfg['transition']['services_partages']+cfg['transition']['services_variables']
assert sum(cfg['deploiement']['roles_pct'].values())==100
assert all(s['interfaces']>=30 for s in cfg['scenarios'].values())
def money(x): return float(Decimal(str(x)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
def sum_money(items): return float(sum((Decimal(str(x)) for x in items),Decimal()))

common=cal['couts_communs']
tool=common['outillage_realisation_eur_par_jh']
expert=common['tarif_expert_transverse_eur_jh']
maintenance_pilot=cal['pilotage']['maintenance_pct']/100
technical_pilot=cal['pilotage']['integration_make_pct']/100
infrastructure_annual=sum(sum(common[key].values()) if isinstance(common[key],dict) else common[key] for key in cfg['transition']['infrastructure_annuelle_refs'])
slugs=['java-spring','dotnet','rust']
loaded={}
for slug in slugs:
    loaded[slug]={key:read(ROOT/path) for key,path in {
        'chiffrage':f'source/chiffrage/chiffrage-{slug}.yaml',
        'integration':f'source/integration/integration-{slug}.yaml',
        'maintenance':f'source/maintenance/maintenance-{slug}.yaml',
        'stack':f'source/stacks/{slug}.yaml'}.items()}

def compute(slug, scenario, price_case='reference', user_shares=None, purchased_core=True):
    docs=loaded[slug]
    stack=docs['stack']
    rates={r:stack['interventions']['tarifs'][v['tarif']][price_case] for r,v in stack['interventions']['activites'].items()}
    roles={a['id']:a['roles'] for a in docs['integration']['activites']}
    maint_roles={a['id']:a['roles'] for a in docs['maintenance']['activites']}
    maint_rows={a['activite']:a for a in docs['chiffrage']['maintenance']['activites']}
    model=business['maintenance']['par_stack'][slug]
    duration=scenario['duree_mois']
    opens=scenario['ouvertures_mois']
    stabilization=cfg['transition']['stabilisation_mois']
    shares=user_shares or cfg['perimetre']['repartition_usagers_par_unite']
    assert len(opens)==len(shares)==len(scenario['deploiement_jh_par_unite'])==cfg['perimetre']['unites_deploiement']
    assert sum(shares)==1 and all(0<=o<=duration-stabilization for o in opens)
    def role_rate(mix):return sum(spec['part_pct']/100*(rates[role]+tool) for role,spec in mix.items())
    def annual_rate(activity):return role_rate(maint_roles[activity])
    retained={}
    for row in docs['chiffrage']['integration']['activites']:
        aid=row['activite']
        if aid not in cfg['substitution']['activites_conservees']:continue
        days=row['jh_avant_ia']
        if aid=='INT-006':days=scenario['interfaces']*scenario['jh_par_interface']
        if aid=='INT-007':days+=scenario['migration_jh_supplementaires']
        specialist=row['jh_expertise_transverse']
        retained[aid]={'jh':days,'raw_eur':(days-specialist)*role_rate(roles[aid])+specialist*(expert+tool)}
    retained_work=money(sum(r['raw_eur'] for r in retained.values()))
    retained_tech=money(retained_work*technical_pilot)
    dep_days=sum(scenario['deploiement_jh_par_unite'])
    dep_rate=sum(share/100*(rates[role]+tool) for role,share in cfg['deploiement']['roles_pct'].items())
    dep_work=money(dep_days*dep_rate)
    dep_tech=money(dep_work*cfg['deploiement']['coordination_technique_pct']/100)
    gov=cfg['pilotage'];day_month=gov['jours_par_etp_mois']
    director_days=duration*day_month*scenario['direction_etp']
    coordination_days=duration*day_month*scenario['coordination_etp']
    programme=money(director_days*gov['tarif_direction_eur_jh']+coordination_days*gov['tarif_coordination_eur_jh'])
    core_days=scenario['corrections_core_par_an']*model['correction_core']+scenario['releases_par_an']*model['qualification_release']
    core_cost=money(core_days*annual_rate('MAI-003')*(1+maintenance_pilot)*duration/12) if purchased_core else 0
    core_evolution_option=money(annual['volumes']['evolutions_fonctionnelles_an']['core_generique']*model['evolution_core']*annual_rate('MAI-009')*(1+maintenance_pilot)*duration/12)
    shared_months=duration-min(opens)
    variable_months=sum(share*(duration-o-stabilization) for share,o in zip(shares,opens))
    # Only volume-linked services follow cohorts. Platform activities run once.
    def annual_days(aid):
        row=maint_rows[aid]
        total=row['jh_fixes_avant_ia']
        for charge in row['charges']:
            ref=charge['volume_ref']
            quantity=1 if ref=='un_service_annuel' else annual['volumes'][ref]
            unit=charge['jh_unitaire']
            if aid=='MAI-004':unit=model['correction_extension']
            if aid=='MAI-006':quantity=scenario['releases_par_an'];unit=model['qualification_client']
            total+=quantity*unit
        return total
    services={}
    for category,months in [('services_partages',shared_months),('services_variables',variable_months)]:
        for aid in cfg['transition'][category]:
            days=annual_days(aid)
            services[aid]={'exposure_months':months,'annual_jh_no_gain':days,'cost_eur':money(days*annual_rate(aid)*(1+maintenance_pilot)*months/12)}
    transient=sum_money(r['cost_eur'] for r in services.values())
    infrastructure=money(infrastructure_annual*duration/12)
    items={
        'travaux_communs_conserves':retained_work,'coordination_technique_commune':retained_tech,
        'deploiements_locaux':dep_work,'coordination_technique_deploiements':dep_tech,
        'direction_coordination_programme':programme,
        'maintien_core':core_cost,'moyens_techniques_pendant_deploiement':infrastructure,
        'exploitation_transitoire_client':transient}
    assigned=[key for group in cost_groups.values() for key in group]
    assert len(assigned)==len(set(assigned)) and set(assigned)==set(items)
    cost_totals={nature:sum_money(items[k] for k in keys) for nature,keys in cost_groups.items()}
    integration=cost_totals['integration_migration']
    mco_run=cost_totals['mco_run']
    total=sum_money(items.values())
    assert total==sum_money(cost_totals.values())
    responsibility_totals={'integration_migration':integration,'cycle_vie_core_system':core_cost,
        'run_et_mco_client_a_ventiler':sum_money([infrastructure,transient])}
    assert sum_money(responsibility_totals.values())==total
    base_option=base['make']['options'][slug]['variants']['proposal_flow_central']
    removed_work=sum(base_option['rows'][aid]['cost_eur'] for aid in cfg['substitution']['activites_retirees'])+base_option['extra_eur']
    removed=money(removed_work*(1+technical_pilot)+base_option['preparation_eur'])
    changed_common=money(retained_work+retained_tech-(base_option['total_eur']-removed))
    bridge={'base_v1':base_option['total_eur'],'retrait_formation_bascule_accompagnement_preparation_et_coordination':-removed,
            'variation_travaux_communs':changed_common,
            'nouveaux_deploiements_coordination_comprise':sum_money([dep_work,dep_tech]),
            'programme':programme,'core':core_cost,'moyens':infrastructure,'service_transitoire':transient}
    assert abs(sum_money(bridge.values())-total)<=0.01
    # Each cohort is first in its deployment package, then in variable service;
    # no overlapping or negative durations, and no service after the project.
    cohorts=[{'unit':i+1,'go_live_month':o,'stabilization_end':o+stabilization,
              'share':s,'variable_service_months':duration-o-stabilization,
              'deployment_jh':scenario['deploiement_jh_par_unite'][i]} for i,(s,o) in enumerate(zip(shares,opens))]
    # Independent month-by-month check of exposures, including the handover month.
    # Relative month m denotes [m, m+1); at duration the full Run takes over.
    chronology=[]
    for month in range(duration+1):
        during=month<duration
        hyper=[during and o<=month<o+stabilization for o in opens]
        live=[during and o+stabilization<=month for o in opens]
        full=not during
        for i,o in enumerate(opens):
            assert not(hyper[i] and live[i])
            if month>=o:assert int(hyper[i])+int(live[i])+int(full)==1
        chronology.append({'month_from_integration_start':month,
            'core':int(during and purchased_core),'technical_purchases':int(during),
            'shared_run':int(during and month>=min(opens)),
            'local_stabilization_units':[i+1 for i,v in enumerate(hyper) if v],
            'local_run_units':[i+1 for i,v in enumerate(live) if v],
            'variable_run_share':sum(s for s,v in zip(shares,live) if v),
            'full_run_handover_not_priced':full})
    observed={'core':sum(m['core'] for m in chronology),
        'technical_purchases':sum(m['technical_purchases'] for m in chronology),
        'shared_run':sum(m['shared_run'] for m in chronology),
        'variable_run':sum(m['variable_run_share'] for m in chronology)}
    assert observed['core']==(duration if purchased_core else 0)
    assert observed['technical_purchases']==duration and observed['shared_run']==shared_months
    assert abs(observed['variable_run']-variable_months)<1e-9
    assert all(chronology[-1][k]==0 for k in ['core','technical_purchases','shared_run','variable_run_share'])
    for aid,row in services.items():
        months=observed['shared_run'] if aid in cfg['transition']['services_partages'] else observed['variable_run']
        assert row['cost_eur']==money(annual_days(aid)*annual_rate(aid)*(1+maintenance_pilot)*months/12)
    return {'items_eur_ht':items,'integration_migration_eur_ht':integration,'mco_run_during_integration_eur_ht':mco_run,
            'responsibility_totals_eur_ht':responsibility_totals,
            'chronology_check':{'observed_months':observed,'monthly_ledger':chronology,'handover_has_no_second_charge':True},
            'total_eur_ht':total,'bridge_eur_ht':bridge,'retained_activities':retained,'deployment_jh':dep_days,
            'deployment_rate_eur_jh_including_tools':dep_rate,'programme_jh':director_days+coordination_days,
            'programme_detail':{'direction_jh':director_days,'coordination_jh':coordination_days},
            'core_gross_jh_per_year':core_days,'core_evolutions_option_not_in_total_eur_ht':core_evolution_option,
            'transient_services':services,'shared_service_months':shared_months,'weighted_variable_service_months':variable_months,
            'cohorts':cohorts,'duration_months':duration,'price_case':price_case,'rates':rates}

result={'nature':cfg['statut'],'definition':cfg,'cost_nature_labels':{key:notions[key]['libelle'] for key in cost_groups},'scenarios':{},'sensitivities':{},'map_links':[]}
for sid,scenario in cfg['scenarios'].items():
    result['scenarios'][sid]={slug:compute(slug,scenario) for slug in slugs}
for slug in slugs:
    central=cfg['scenarios']['central'];c=result['scenarios']['central'][slug]
    variants={}
    def sensitivity(name,scen=None,**kwargs):
        outcome=compute(slug,scen or central,**kwargs)
        variants[name]={'total_eur_ht':outcome['total_eur_ht'],'delta_to_central_eur_ht':money(outcome['total_eur_ht']-c['total_eur_ht'])}
    sensitivity('tarifs_techniques_hauts_existants',price_case='haut')
    sensitivity('core_inclus_dans_autre_financement',purchased_core=False)
    sensitivity('usagers_concentres_premiere_unite',user_shares=[0.5,0.2,0.2,0.1])
    sensitivity('usagers_concentres_derniere_unite',user_shares=[0.1,0.2,0.2,0.5])
    v=deepcopy(central);v['interfaces']=50;sensitivity('dix_flux_supplementaires',v)
    v=deepcopy(central);v['direction_etp']=1;sensitivity('direction_temps_plein',v)
    v=deepcopy(central);v['deploiement_jh_par_unite']=[400]*4;sensitivity('quatre_unites_complexes',v)
    v=deepcopy(central);v['duree_mois']+=6;v['ouvertures_mois']=[o+6 for o in v['ouvertures_mois']];sensitivity('retard_global_six_mois',v)
    v=deepcopy(central);v['duree_mois']+=6;sensitivity('prolongation_programme_six_mois_apres_ouvertures',v)
    for name,outcome in variants.items():
        if name in ['core_inclus_dans_autre_financement','usagers_concentres_derniere_unite']:
            assert outcome['delta_to_central_eur_ht']<0,name
        else:
            assert outcome['delta_to_central_eur_ht']>0,name
    expected_delay=money((c['items_eur_ht']['direction_coordination_programme']+c['items_eur_ht']['maintien_core']+c['items_eur_ht']['moyens_techniques_pendant_deploiement'])/central['duree_mois']*6)
    assert abs(expected_delay-variants['retard_global_six_mois']['delta_to_central_eur_ht'])<=0.02
    result['sensitivities'][slug]=variants
    assert result['scenarios']['resserre'][slug]['total_eur_ht']<c['total_eur_ht']<result['scenarios']['renforce'][slug]['total_eur_ht']
    # The four generalisation packages replace all local work, not four extras.
    assert len(c['cohorts'])==4 and c['deployment_jh']==1200
    assert c['shared_service_months']==16 and c['weighted_variable_service_months']==6.75
    assert c['programme_jh']==918

for cid in cfg['deploiement']['cartographie']:
    result['map_links'].append({'capacite_id':cid,'chemin':bycap[cid]['chemin'],'nature':'Used for acceptance and handover, no monetary allocation.'})
after=active_hashes()
assert before==after,'Active sources or implementation changed during calculation'
reference=read(ROOT/'source/investissements-10-ans.yaml')['bonus_continuite_make']['budget_apres_bonus_eur_ht']
assert reference==base['reference']['integration_make_eur']
result['checks']={'active_files_count':len(before),'active_hashes_unchanged':True,'base_dependencies_verified':True,
 'reference_make_integration_eur_ht':reference,'reference_changed':False,'substitution_and_bridge_valid':True,
 'shared_services_not_scaled_by_users':True,'cohorts_disjoint_hypercare_and_service':True,'totals_equal_sum_published_cents':True,
 'native_capability_ids_valid':True,'sensitivity_directions_valid':True,
 'single_canonical_cost_nature_per_item':True,'monthly_exposures_independently_checked':True,
 'no_full_run_annuity_added_during_integration':True,'contractual_inclusions_verified':False,
 'business_scope_validated':False,'supplier_quote':False}
result['source_hashes']={**base['make']['source_hashes'],DEFINITION.relative_to(ROOT).as_posix():sha(DEFINITION),
 base_path.relative_to(ROOT).as_posix():sha(base_path),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
 glossary_path.relative_to(ROOT).as_posix():sha(glossary_path)}
(HERE/'2026-10-27-enveloppe-groupe-make-preuves.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'scenarios':{sid:{s:{k:v for k,v in o.items() if k in ['integration_migration_eur_ht','mco_run_during_integration_eur_ht','total_eur_ht']} for s,o in vals.items()} for sid,vals in result['scenarios'].items()},'checks':result['checks']},ensure_ascii=False,indent=2))
