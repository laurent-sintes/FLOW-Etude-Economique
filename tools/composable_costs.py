"""Funding ledger for the active Core / Run / client MCO model.

Initial funding is allocated by rounded cumulative spend by the projector.
Annual services retain the engine's prices, inclusions and inflation conventions.
No audit results are imported into the active calculation.
"""
from decimal import Decimal, ROUND_HALF_UP
from validate_stacks import ROOT, read
from calculate_costs import mixed_cost, role_rates, volume
from business_calibration import active_doc
from model_inputs import annual_scenario, funding_inputs, RESPONSIBILITIES

PATH = 'source/modele-composable.yaml'
GROUP = 'source/deploiement-groupe.yaml'


def money(value):
    return float(Decimal(str(value)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))


def allocate(total, weights):
    """Cent-conserving distribution; weights describe already priced work."""
    denominator = sum(Decimal(str(v)) for v in weights)
    assert denominator > 0
    previous = cumulative = Decimal(0)
    result = []
    for weight in weights:
        cumulative += Decimal(str(weight))
        current = (Decimal(str(total))*cumulative/denominator).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        result.append(float(current-previous)); previous = current
    return result


def annual_split(slug, economic, service_total, core_total, cal):
    """Split Make work; supplier bundles remain indivisible in the projection."""
    p = economic['maintenance_annuelle'][0]['postes_eur_ht']
    rows = {r['activite']: r['cout_diagnostique_eur_ht'] for r in economic['maintenance_activites']}
    doc = active_doc(slug)
    rates = role_rates(read(ROOT/f'source/stacks/{slug}.yaml'))
    roles = {a['id']: a['roles'] for a in read(ROOT/f'source/maintenance/maintenance-{slug}.yaml')['activites']}
    scenario = annual_scenario()
    a = next(r for r in doc['maintenance']['activites'] if r['activite']=='MAI-009')
    days = sum(volume(scenario,c['volume_ref'])*c['jh_unitaire'] for c in a['charges'] if c['volume_ref']=='evolutions_fonctionnelles_an.core_generique')
    core_evolution = mixed_cost(days*(1-a['gain_ia_pct']/100),roles['MAI-009'],rates,cal['couts_communs']['outillage_realisation_eur_par_jh'])
    flux = next(r for r in doc['maintenance']['activites'] if r['activite']=='MAI-005')
    gross = flux['jh_fixes_avant_ia']+sum(volume(scenario,c['volume_ref'])*c['jh_unitaire'] for c in flux['charges'])
    fixed, variable = allocate(rows['MAI-005'],[flux['jh_fixes_avant_ia'],gross-flux['jh_fixes_avant_ia']])
    extra = money(p['prestations_estimees']-sum(rows.values()))
    assert extra >= -.02
    classes=funding_inputs()[0]['classification_make']
    buckets=dict(run=max(0,extra),mco_client=0,client_evolutions=max(0,rows['MAI-009']-core_evolution))
    for aid in ('MAI-001','MAI-002','MAI-004','MAI-006','MAI-007','MAI-008'):
        buckets[classes[aid]['responsabilite']]+=rows[aid]
    buckets[classes['MAI-005']['fixe_responsabilite']]+=fixed
    buckets[classes['MAI-005']['charges_responsabilite']]+=variable
    weights=[buckets[k] for k in ('run','mco_client','client_evolutions')]
    # Oversight follows the activities; the known support purchase remains Run.
    client = money(service_total-core_total)
    parts = allocate(money(client-p['outillage_audits']),weights)
    return dict(core_lifecycle=core_total,run=money(parts[0]+p['outillage_audits']),mco_client=parts[1],client_evolutions=parts[2])


def load_funding_model(slug):
    """Compile source inputs once. The ledger itself performs no file access."""
    work=active_doc(slug)
    config,group=funding_inputs()
    return dict(config=config, group=group,
        calibration=read(ROOT/'source/calibration-couts.yaml'),
        rates=role_rates(read(ROOT/f'source/stacks/{slug}.yaml')),
        work={key:work[key] for key in ('integration','maintenance')},
        integration_roles={r['id']:r['roles'] for r in read(ROOT/f'source/integration/integration-{slug}.yaml')['activites']},
        maintenance_roles={r['id']:r['roles'] for r in read(ROOT/f'source/maintenance/maintenance-{slug}.yaml')['activites']},
        volumes=annual_scenario())


def initial_ledger(option, reference):
    inputs=option['composable']['inputs']
    cfg=inputs['config']; group=inputs['group']
    classes=cfg['classification_make']
    slug=option['stack']; b=option['build_mois']; duration=option['integration_mois']; end=b+duration
    spec=group['scenarios']['central']
    stabilization=group['transition']['stabilisation_mois']
    assert duration>stabilization and spec['duree_mois']>stabilization
    ratio=(duration-stabilization)/(spec['duree_mois']-stabilization)
    openings=[x*ratio for x in spec['ouvertures_mois']]
    shares=group['perimetre']['repartition_usagers_par_unite']
    accept=[x+stabilization for x in openings]
    rows=[]
    def add(id,amount,start,stop,responsibility,phase='mco_run',source=GROUP):
        if stop<=start:
            assert abs(amount)<.01
            return
        obj=('core_system' if responsibility=='core_lifecycle' else
             'programme' if id=='programme' or id.startswith('coordination') else
             'plateforme' if responsibility=='run' and not id.startswith(('MAI-001','MAI-002','MAI-005')) else 'adaptations_client')
        service=('construction' if phase=='build' else 'pilotage' if obj=='programme' else
                 'integration' if phase=='integration' else 'exploitation' if responsibility=='run' else 'maintien')
        rows.append(dict(id=id,financement_id=id.split('/')[0],amount=money(amount),start=start,end=stop,
                         objet=obj,prestation=service,responsibility=responsibility,phase=phase,source=source))
    add('construction_core',option['build'],0,b,'core_lifecycle','build','source/recalibration-metier.yaml')
    cursor=0
    for stage in cfg['hebergement_build']['phases']:
        months=b*stage['part_duree']
        monthly=sum(stage['couts_mensuels_eur_ht'][cfg['hebergement_build']['cas_central']].values())
        add('hebergement_build/'+stage['id'],monthly*months,cursor,cursor+months,'run',source=PATH)
        cursor+=months
    assert abs(cursor-b)<1e-8
    cal=inputs['calibration']; common=cal['couts_communs']
    tool=common['outillage_realisation_eur_par_jh']; pilot=1+cal['pilotage']['maintenance_pct']/100
    rates=inputs['rates']; raw=inputs['work']
    activities={r['activite']:r for r in raw['maintenance']['activites']}
    int_roles=inputs['integration_roles']; maint_roles=inputs['maintenance_roles']
    def cost(days,roles): return mixed_cost(days,roles,rates,tool)
    retained=0
    for row in raw['integration']['activites']:
        aid=row['activite']
        if aid not in group['substitution']['activites_conservees']: continue
        days=spec['interfaces']*spec['jh_par_interface'] if aid=='INT-006' else row['jh_avant_ia']
        if aid=='INT-007': days+=spec['migration_jh_supplementaires']
        expert=row['jh_expertise_transverse']
        retained+=cost(days-expert,int_roles[aid])+expert*(rates['architecte']+tool)
    retained=money(retained)
    add('travaux_communs',retained,b,end,'integration_client','integration')
    add('coordination_commune',retained*cal['pilotage']['integration_make_pct']/100,b,end,'integration_client','integration')
    deploy=money(sum(spec['deploiement_jh_par_unite'])*sum(share/100*(rates[role]+tool) for role,share in group['deploiement']['roles_pct'].items()))
    add('deploiements',deploy,b,end,'integration_client','integration')
    add('coordination_deploiements',deploy*group['deploiement']['coordination_technique_pct']/100,b,end,'integration_client','integration')
    gov=group['pilotage']
    add('programme',duration*gov['jours_par_etp_mois']*(spec['direction_etp']*gov['tarif_direction_eur_jh']+spec['coordination_etp']*gov['tarif_coordination_eur_jh']),b,end,'integration_client','integration')
    core_factor=option['ventilation_services']['core']/reference['core']
    client_factor=option['ventilation_services']['integration']/reference['integration']
    core_units={c['volume_ref']:c['jh_unitaire'] for c in activities['MAI-003']['charges']}
    days=spec['corrections_core_par_an']*core_units['corrections_core_an']+spec['releases_par_an']*core_units['campagnes_qualification_versions_an']
    add('cycle_core_transition',cost(days,maint_roles['MAI-003'])*pilot*duration/12*core_factor,b,end,'core_lifecycle')
    for key,value in [('hebergement',option['base_annuelle']['hebergement']),('ipaas',option['base_annuelle']['ipaas']),
                      ('outillage',common['outillage_support_annuel']*client_factor),('droits',option['base_annuelle']['licences_complementaires'])]:
        add('moyens_transition/'+key,value*duration/12,b,end,'run')
    scenario=inputs['volumes']
    for aid in group['transition']['services_partages']+group['transition']['services_variables']:
        row=activities[aid]; days=row['jh_fixes_avant_ia']
        for charge in row['charges']:
            quantity=volume(scenario,charge['volume_ref']);unit=charge['jh_unitaire']
            if aid=='MAI-006':quantity=spec['releases_par_an']
            days+=quantity*unit
        annual=cost(days,maint_roles[aid])*pilot*client_factor
        if aid in group['transition']['services_variables']:
            exposures=[s*(duration-a) for s,a in zip(shares,accept)]
            total=money(annual*sum(exposures)/12)
            for index,(a,part) in enumerate(zip(accept,allocate(total,exposures))):
                add(aid+'/'+str(index),part,b+a,end,classes[aid]['responsabilite'])
        else:
            first=min(openings);accepted=min(accept)
            total=money(annual*(duration-first)/12)
            if aid=='MAI-005':
                fixed,total=allocate(total,[row['jh_fixes_avant_ia'],days-row['jh_fixes_avant_ia']])
                add(aid+'/surveillance',fixed,b+first,end,classes[aid]['fixe_responsabilite'])
            if aid in ('MAI-005','MAI-006'):
                pre,post=allocate(total,[accepted-first,duration-accepted])
                add(aid+'/reception',pre,b+first,b+accepted,'integration_client','integration')
                add(aid+'/maintien',post,b+accepted,end,classes[aid]['charges_responsabilite'] if aid=='MAI-005' else classes[aid]['responsabilite'])
            else: add(aid,total,b+first,end,classes[aid]['responsabilite'])
    assert len({r['id'] for r in rows})==len(rows)
    return rows


def service_parts(option):
    """Current annual services scaled by their existing simulation assumptions."""
    if option['mode']=='Buy':
        return {'grouped_buy': option['base_annuelle']['services_mco']}
    ref=option['composable']['annual_reference']
    core=option['ventilation_services']['core']; client=option['ventilation_services']['integration']
    weights=[ref[k] for k in ('run','mco_client','client_evolutions')]
    parts=allocate(client,weights)
    return dict(core_lifecycle=core,run=parts[0],mco_client=parts[1],client_evolutions=parts[2])
