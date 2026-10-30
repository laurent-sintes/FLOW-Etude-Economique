"""Calcul reproductible d'ordre de grandeur : build + intégration + 15 années de service.

Les prix RFI priment. Aucun calendrier ou effectif de projet n'est déduit des JH.
"""
import argparse
import hashlib
import json
import math
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read
from model_context import scoped_model
from retained_core import value_units, dependencies as retained_dependencies
from model_inputs import annual_scenario
from content_model import resolve_text_tree
from current_cost_inputs import apply as apply_business_calibration, validate as validate_business_calibration, PATH as BUSINESS_PATH, dependencies as current_dependencies

SLUGS = ('java-spring', 'dotnet', 'rust', 'microsoft', 'sap')
SCENARIOS = ('bas', 'central', 'haut')
CAL = 'source/calibration-couts.yaml'
OUTPUT = 'source/couts-15-ans.yaml'


def money_round(value):
    return float(Decimal(str(value)).quantize(Decimal('0.01'),rounding=ROUND_HALF_EVEN))


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def role_rates(stack):
    rates={r: stack['interventions']['tarifs'][a['tarif']]['reference']
           for r,a in stack['interventions']['activites'].items()}
    rates.update({role:stack['interventions']['tarifs'][role]['reference'] for role in ('qa','architecte')})
    return rates


def mixed_cost(jh, roles, rates, tools):
    return sum(jh * spec['part_pct']/100 * (rates[role]+tools) for role,spec in roles.items())


def volume(scenario, ref):
    if ref == 'un_service_annuel':
        return 1
    value = scenario['volumes']
    for part in ref.split('.'):
        value = value[part]
    return value


def maintenance_specialist_adjustment(doc, maintenance, cal, rates, scenario, sensitivity='central'):
    """Reprice an inherited subset of funded N3 days, without adding any effort."""
    spec=cal['specialisation_maintenance_make']
    assert set(spec)=={'statut','activites_refs','profil_base','profil_cible',
                       'plafond_jh_avant_sensibilite','origine','assiette','calcul'}, 'Specialist allowance fields'
    assert spec['statut']=='hypothese_heritee_non_observee', 'Specialist allowance provenance'
    for key in ('origine','assiette','calcul'):
        assert isinstance(spec[key],str) and spec[key].strip(), ('Specialist allowance explanation',key)
    refs=spec['activites_refs']
    assert isinstance(refs,list) and refs and all(isinstance(a,str) for a in refs), 'Specialist activity references'
    assert len(refs)==len(set(refs)), 'Duplicate specialist activity reference'
    # Only these services form the current cloud/security perimeter; flux maintenance
    # and generic Core work are not implicitly used to make up a missing allowance.
    assert set(refs)<= {'MAI-007','MAI-008'}, 'Incompatible cloud/security activity'
    assert spec['profil_base']=='support_n3' and spec['profil_cible']=='architecte', 'Specialist profile contract'
    limit=spec['plafond_jh_avant_sensibilite']
    assert isinstance(limit,(int,float)) and not isinstance(limit,bool) and math.isfinite(limit) and limit>=0, 'Invalid specialist day ceiling'
    assert sensitivity in SCENARIOS, 'Unknown sensitivity'
    if doc['strategie']!='make':
        return dict(jh=0,cout_eur_ht=0,jh_disponibles=0,activites_jh={})
    work={row['activite']:row for row in doc['maintenance']['activites']}
    activities={row['id']:row for row in maintenance['activites']}
    assert set(refs)<=set(work) and set(refs)<=set(activities), 'Unknown specialist activity'
    factor=1 if sensitivity=='central' else cal['sensibilite']['jh_'+sensitivity]
    available={}
    for ref in refs:
        row=work[ref];roles=activities[ref]['roles']
        assert roles is not None and spec['profil_base'] in roles, ('Missing funded specialist base profile',ref)
        gross=row['jh_fixes_avant_ia']+sum(volume(scenario,c['volume_ref'])*c['jh_unitaire'] for c in row['charges'])
        gain=0 if sensitivity=='haut' else row['gain_ia_pct']
        funded=gross*factor*(1-gain/100) if row['traitement']=='estimation' else 0
        available[ref]=funded*roles[spec['profil_base']]['part_pct']/100
    basis=min(limit*factor,sum(available.values()))
    return dict(jh=basis,cout_eur_ht=basis*max(0,rates[spec['profil_cible']]-rates[spec['profil_base']]),
                jh_disponibles=sum(available.values()),activites_jh=available)


def project_source(post, year, source_years, inflation_pct):
    prices = {p['annee']:p['montant'] for p in post['montants_documentes_eur_ht']}
    sequence = [prices[y] for y in source_years]
    assert sequence and year >= 1
    if year <= len(sequence):
        return sequence[year-1]
    return sequence[-1] * (1+inflation_pct/100)**(year-len(sequence))


def validate_inputs():
    from validate_cycle import validate as validate_cycle
    validate_cycle()
    cal = read(ROOT/CAL)
    assert cal['convention']['sap_licences_annees_sources'] == [4,5]
    assert cal['convention']['microsoft_licences_annees_sources'] == [1,2,3,4,5]
    for gains in cal['ia']['taux_pct'].values():
        assert set(gains) == set(cal['natures']) and all(0 <= g <= 30 for g in gains.values())
    assert all(0 <= v <= 30 for v in cal['ia']['integration_pct'].values())
    assert cal['sensibilite']['jh_bas'] <= 1 <= cal['sensibilite']['jh_haut']
    assert cal['sensibilite']['achats_bas'] <= 1 <= cal['sensibilite']['achats_haut']
    assert all(0 <= cal['pilotage'][k] <= 30 for k in ['build_pct','integration_make_pct','maintenance_pct','complements_buy_pct'])
    proof = read(ROOT/'sources/calibration-couts-2026-10-22.yaml')
    for key,p in proof['sources'].items():
        assert p['portee'] and p['nature']
        if not p['reference'].startswith('https://'):
            assert (ROOT/p['reference']).is_file()
        if p.get('sha256'):
            assert sha(p['reference']) == p['sha256'], key
    schema = read(ROOT/'source/schema-chiffrage.yaml')
    Draft202012Validator.check_schema(schema)
    check = Draft202012Validator(schema)
    scenario = annual_scenario()
    result = {}
    for slug in SLUGS:
        path = f'source/chiffrage/chiffrage-{slug}.yaml'
        doc = read(ROOT/path)
        check.validate(doc)
        assert doc['stack'] == slug and doc['id'] == 'chiffrage-'+slug
        assert doc['strategie'] == ('make' if slug in SLUGS[:3] else 'buy')
        for dep in doc['dependances'].values():
            assert sha(dep['fichier']) == dep['sha256'], f'{slug}: dependency changed: {dep["fichier"]}; review before recalculation'
        integ = read(ROOT/doc['dependances']['integration']['fichier'])
        maint = read(ROOT/doc['dependances']['maintenance']['fichier'])
        assert [a['activite'] for a in doc['integration']['activites']] == [a['id'] for a in integ['activites']]
        assert [a['activite'] for a in doc['maintenance']['activites']] == [a['id'] for a in maint['activites'] if a['nature']=='travail']
        for a in doc['integration']['activites']:
            assert a['jh_expertise_transverse'] <= a['jh_avant_ia']
            assert a['traitement'] == ('estimation' if doc['strategie']=='make' else 'inclus_rfi')
        for a in doc['maintenance']['activites']:
            for c in a['charges']:
                assert volume(scenario,c['volume_ref']) >= 0
            if a['traitement']=='inclus_forfait_rfi':
                assert slug=='sap'
            if a['traitement']=='inclus_abonnement':
                assert slug in ('microsoft','sap') and a['activite']=='MAI-003'
        if doc['strategie']=='buy':
            assert doc['integration']['prix_rfi']['postes_eur']
        else:
            assert not doc['integration']['prix_rfi']['postes_eur']
        result[slug] = doc
    return cal, apply_business_calibration(result)


def calculate_option(slug, doc, cal, sensitivity='central', service_years=15):
    make=doc['strategie']=='make'
    scenario=annual_scenario()
    stack=read(ROOT/doc['dependances']['stack']['fichier'])
    integration=read(ROOT/doc['dependances']['integration']['fichier'])
    maintenance=read(ROOT/doc['dependances']['maintenance']['fichier'])
    ma={a['id']:a for a in maintenance['activites']}
    prices={p['id']:p for p in maintenance['valorisation_annuelle']['postes']}
    inflation=read(ROOT/'source/inflation.yaml')['categories']
    rates=role_rates(stack)
    frontend_rate=role_rates(read(ROOT/'source/stacks/java-spring.yaml'))['developpement']
    common=cal['couts_communs']
    tools=common['outillage_realisation_eur_par_jh']
    jhf=1 if sensitivity=='central' else cal['sensibilite']['jh_'+sensitivity]
    buyf=1 if sensitivity=='central' else cal['sensibilite']['achats_'+sensitivity]
    # Le haut conserve la possibilité d'absence de gains IA ; le bas ne crédite pas un second gain.
    def gain(g): return 0 if sensitivity=='haut' else g
    def growth(category,year): return (1+inflation[category]['taux_annuel_pct'][sensitivity]/100)**(year-1)
    backend=frontend=base_jh=0
    core_cost=0
    feature_results=[]
    for f in doc['core']:
        residual=f.get('plages_jh',{}).get(sensitivity)
        gross={n:residual[n] if residual else jhf*j for n,j in f['jh_backend_avant_ia'].items()}
        gross_front=residual['frontend'] if residual else jhf*f['jh_frontend_avant_ia']
        # Included standard work is diagnostic; the grouped supplier price already finances it.
        included=f['traitement']=='inclus_rfi'
        net={n:0 if included else j*(1-gain(cal['ia']['taux_pct'][slug][n])/100) for n,j in gross.items()}
        b=sum(net.values())
        front=0 if included else gross_front*(1-gain(cal['ia']['frontend_pct'])/100)
        cost=sum(j*(rates['qa' if nature=='qualification' else 'developpement']+tools)
                 for nature,j in net.items())+front*(frontend_rate+tools)
        base_jh+=0 if included else sum(gross.values())+gross_front
        backend+=b;frontend+=front;core_cost+=cost
        feature_results.append(dict(feature=f['feature'],traitement=f['traitement'],jh_backend=round(b,2),jh_frontend=round(front,2),cout_eur_ht=round(cost,2),jh_diagnostiques_avant_ia=round(sum(gross.values())+gross_front,2)))
    build_pilot=core_cost*cal['pilotage']['build_pct']/100 if make else 0
    core_units = value_units(slug, doc['core'], tools) if make else []
    retained_jh = sum(u['total_jh'] for u in core_units)
    # Family totals already include QA, architecture and local management.
    # Legacy coordination remains restricted to its original legacy cost base.
    core_cost += sum(u['cost_eur_ht'] for u in core_units)
    base_jh += retained_jh
    build=core_cost+build_pilot if make else 0
    integration_jh=integration_labour=0
    integration_rows=[]
    for a,original in zip(doc['integration']['activites'],integration['activites']):
        net=a['jh_avant_ia']*jhf*(1-gain(cal['ia']['integration_pct'][slug])/100)
        expert=a['jh_expertise_transverse']*jhf  # pas de gain IA sur l'expertise transverse
        normal=(a['jh_avant_ia']-a['jh_expertise_transverse'])*jhf*(1-gain(cal['ia']['integration_pct'][slug])/100)
        net=expert+normal
        cost=mixed_cost(normal,original['roles'],rates,tools)+expert*(rates['architecte']+tools)
        integration_rows.append(dict(activite=a['activite'],jh=round(net,2),traitement=a['traitement'],cout_diagnostique_eur_ht=round(cost,2)))
        if a['traitement']=='estimation': integration_jh+=net;integration_labour+=cost
    if make:
        training=common['accompagnement_applicatif_make_jh']*jhf
        integration_labour+=training*(rates['integration']+tools)
        integration_jh+=training
    # Les compléments génériques Buy sont affectés à l'intégration, jamais au build éditeur.
    gap_cost=0 if make else core_cost
    automation=doc['integration']['complement_qualification_automation_jh']*jhf
    gap_cost+=automation*(rates['integration']+tools)
    source_integration=sum(doc['integration']['prix_rfi']['postes_eur'])
    pilot_integration=(integration_labour*cal['pilotage']['integration_make_pct']/100 if make
                       else gap_cost*cal['pilotage']['complements_buy_pct']/100)
    preparation=common['preparation_make' if make else 'preparation_buy']*buyf
    ms_support=prices['MAI-013/outillage-support']['montants_documentes_eur_ht'][0]['montant'] if slug=='microsoft' else 0
    discrepancy=cal['sensibilite']['sap_ecart_total_integration_haut'] if slug=='sap' and sensitivity=='haut' else 0
    integration_total=source_integration+integration_labour+gap_cost+pilot_integration+preparation+ms_support+discrepancy
    maintenance_rows=[]
    maintenance_labour=maintenance_jh=0
    for a in doc['maintenance']['activites']:
        gross=a['jh_fixes_avant_ia']+sum(volume(scenario,c['volume_ref'])*c['jh_unitaire'] for c in a['charges'])
        net=gross*jhf*(1-gain(a['gain_ia_pct'])/100)
        original=ma[a['activite']]
        cost=mixed_cost(net,original['roles'],rates,tools) if original['roles'] else 0
        maintenance_rows.append(dict(activite=a['activite'],jh=round(net,2),traitement=a['traitement'],cout_diagnostique_eur_ht=round(cost,2)))
        if a['traitement']=='estimation': maintenance_labour+=cost;maintenance_jh+=net
    extra_jh=doc['maintenance']['maintenance_complements_buy_jh_annuels']*jhf
    maintenance_labour+=extra_jh*(rates['developpement']+tools)
    maintenance_jh+=extra_jh
    # Cloud/security reprices a source-owned subset of days already funded by their
    # activities. The inherited ceiling follows sensitivity and cannot exceed them.
    specialist=maintenance_specialist_adjustment(doc,maintenance,cal,rates,scenario,sensitivity)
    maintenance_labour+=specialist['cout_eur_ht']
    # Establish one cent-denominated annual base before inflation and oversight.
    maintenance_labour=money_round(maintenance_labour)
    annual=[]
    # Compatibility diagnostic, not an editable assumption of the sponsor calendar.
    diagnostic_years=service_years
    assert isinstance(diagnostic_years,int) and diagnostic_years>0
    for year in range(1,diagnostic_years+1):
        labour=maintenance_labour*growth('tjm_ingenierie',year)
        pilot=labour*cal['pilotage']['maintenance_pct']/100
        licences=0 if make else project_source(prices['MAI-010/licences'],year,
          cal['convention'][slug+'_licences_annees_sources'],inflation['licences_logiciels']['taux_annuel_pct'][sensitivity])
        forfaits=sum(project_source(prices[id],year,[1],inflation['tjm_ingenierie']['taux_annuel_pct'][sensitivity])
          for id in ['rfi-mco','rfi-monitoring','rfi-evolutions']) if slug=='sap' else 0
        cloud=(sum(common['cloud_make_annuel'].values()) if make else common['capacite_buy_supplementaire_annuel'][slug])*buyf*growth('cloud',year)
        ipaas=(common['ipaas_sap_annuel'] if slug=='sap' else common['ipaas_make_microsoft_annuel'])*buyf*growth(common['indexation_ipaas'][slug],year)
        tooling=common['outillage_support_annuel']*buyf*growth('tjm_ingenierie',year)
        power=common['power_platform_supplementaire_annuel']*buyf*growth('licences_logiciels',year) if slug=='microsoft' else 0
        drp=cal['sensibilite']['sap_drp_annuel_haut']*growth('licences_logiciels',year) if slug=='sap' and sensitivity=='haut' else 0
        pieces=dict(licences_rfi=licences,forfaits_rfi=forfaits,prestations_estimees=labour,pilotage=pilot,
                    cloud_hors_panier=cloud,ipaas=ipaas,outillage_audits=tooling,droits_complementaires=power,reserve_drp_sap=drp)
        pieces={k:money_round(v) for k,v in pieces.items()}
        annual.append(dict(annee_service=year,postes_eur_ht=pieces,total_eur_ht=round(sum(pieces.values()),2)))
    maint15=round(sum(a['total_eur_ht'] for a in annual),2)
    total=round(build+integration_total+maint15,2)
    result=dict(stack=slug,strategie=doc['strategie'],
      synthese_eur_ht=dict(build_core=round(build,2),integration=round(integration_total,2),maintenance_15_ans=maint15,total=total,
        maintenance_premiere_annee=annual[0]['total_eur_ht'],maintenance_moyenne_annuelle=round(maint15/diagnostic_years,2)),
      jh=dict(affectation_fonctionnelle='build_core' if make else 'complements_integration',
              core_avant_ia=round(base_jh,2),core_backend=round(backend,2),core_frontend=round(frontend,2),
              core_project_roles_jh=retained_jh,
              integration_estimee_hors_rfi=round(integration_jh+(backend+frontend+automation if not make else 0),2),maintenance_annuelle_estimee_hors_forfaits=round(maintenance_jh,2)),
      detail_build=dict(prestations=round(core_cost,2) if make else 0,pilotage=round(build_pilot,2)),
      detail_integration=dict(base_rfi=source_integration,prestations_estimees=round(integration_labour,2),complements_flow=round(gap_cost,2),pilotage=round(pilot_integration,2),preparation=preparation,support_microsoft_premiere_annee=ms_support,reserve_ecart_sap=discrepancy),
      core_units=core_units,features=feature_results,integration_activites=integration_rows,maintenance_activites=maintenance_rows,maintenance_annuelle=annual)
    # Published subtotals are the accounting basis; do not round their raw sum separately.
    result['synthese_eur_ht']['build_core']=round(sum(result['detail_build'].values()),2)
    result['synthese_eur_ht']['integration']=round(sum(result['detail_integration'].values()),2)
    result['synthese_eur_ht']['total']=round(sum(result['synthese_eur_ht'][k] for k in ('build_core','integration','maintenance_15_ans')),2)
    if not make: assert build==0
    if service_years!=15:
        # A valuation is not a second TCO. Keep the established monetary fields
        # used by the sponsor; only the optional 15-year diagnostic has totals.
        for key in ('maintenance_15_ans','maintenance_moyenne_annuelle','total'):
            result['synthese_eur_ht'].pop(key)
    return result


@scoped_model
def calculate(projection_only=False):
    documentation=resolve_text_tree(read(ROOT/'source/explications-modele.yaml')['resultats_generes']['couts_15_ans'],read(ROOT/'source/glossaire.yaml'))
    cal,docs=validate_inputs()
    business=validate_business_calibration()
    files={'source/glossaire.yaml','source/explications-modele.yaml',CAL,'source/inflation.yaml','sources/calibration-couts-2026-10-22.yaml','tools/calculate_costs.py','tools/content_model.py','source/schema-chiffrage.yaml','source/ecarts-perimetre-flow-rfi.md'}
    for slug,doc in docs.items():
        files.add(f'source/chiffrage/chiffrage-{slug}.yaml')
        files.update(d['fichier'] for d in doc['dependances'].values())
    files.update(current_dependencies())
    files.update(retained_dependencies())
    files.update(('tools/model_inputs.py','tools/validate_cycle.py','source/integration.yaml','source/maintenance.yaml',
                  'source/schema-activites-cycle.yaml','source/schema-valorisation-cycle.yaml','sources/integration-maintenance-2026-10-22.yaml'))
    results=[]
    for slug,doc in docs.items():
        years=(1 if doc['strategie']=='make' else len(cal['convention'][slug+'_licences_annees_sources'])) if projection_only else 15
        central=calculate_option(slug,doc,cal,service_years=years)
        central['sensibilite_eur_ht']={case:calculate_option(slug,doc,cal,case,years)['synthese_eur_ht'] for case in ['bas','haut']}
        for key in central['synthese_eur_ht']:
            assert central['sensibilite_eur_ht']['bas'][key] <= central['synthese_eur_ht'][key] <= central['sensibilite_eur_ht']['haut'][key]
        results.append(central)
    return dict(version_schema=1,id='valorisation' if projection_only else 'couts-15-ans',date_calibration=business['date'],
      nature=documentation['nature'],
      dependances={p:sha(p) for p in sorted(files)},convention=cal['convention'],exclusions=cal['exclusions'],
      limites=documentation['limites'],
      comparaison=[dict(stack=r['stack'],**r['synthese_eur_ht']) for r in results],options=results)


def valuation():
    """Inputs for the sponsor projection: annual base and documented Buy sequences.

    calculate() retains its original complete diagnostic contract for exports.
    Both use the same pricing formulas; the sponsor no longer builds 15 annuities.
    """
    return calculate(projection_only=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Recalculer et comparer sans modifier le résultat enregistré')
    args=parser.parse_args()
    result=calculate()
    if args.check:
        assert read(ROOT/OUTPUT)==result, 'Résultat obsolète : recalculer tools/calculate_costs.py'
    else:
        (ROOT/OUTPUT).write_text(yaml.safe_dump(result,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
    for option in result['options']:
        s=option['synthese_eur_ht']
        print(option['stack'],{k:round(s[k]/1e6,3) for k in ['build_core','integration','maintenance_15_ans','total']})
    print('OK: 5 stacks, prix RFI prioritaires, 15 années de service, inclusions, sommes et dépendances.')


if __name__=='__main__':
    main()
