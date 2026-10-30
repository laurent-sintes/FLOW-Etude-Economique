"""Projection annuelle depuis les YAML économiques et le scénario sponsor."""
import json
import math
import sys
from pathlib import Path
import yaml
from decimal import Decimal, ROUND_HALF_EVEN
from calculate_costs import valuation, sha, mixed_cost, role_rates, volume
from validate_stacks import ROOT, read
from model_inputs import annual_scenario, funding_inputs, buy_selection_inputs
from content_model import resolve_text_tree
from current_cost_inputs import active_doc
from composable_costs import annual_split, initial_ledger, service_parts, RESPONSIBILITIES, load_funding_model
from model_context import scoped_model

OUTPUT = ROOT/'source/investissements-15-ans.yaml'


def phase_expense(budget, start, duration, lo, hi):
    """Difference of rounded cumulative spend, conserving the initial budget exactly."""
    if not duration:
        return 0.0
    amount=Decimal(str(budget)); begin=Decimal(str(start)); length=Decimal(str(duration))
    def accrued(month):
        fraction=max(Decimal(0),min(Decimal(1),(Decimal(str(month))-begin)/length))
        return (amount*fraction).quantize(Decimal('0.01'),rounding=ROUND_HALF_EVEN)
    return float(accrued(hi)-accrued(lo))

def split_services(slug, total, cal):
    """Deux objets. Seuls les travaux Make identifiables sont ventilés.

    Les prestations Buy restent groupées : pas de prorata d'une offre fournisseur.
    Les coûts unitaires et gains IA sont ceux du calcul économique existant.
    """
    if slug in ('microsoft', 'sap'):
        return dict(core=None, integration=None, groupes=total)
    core=round(sum(core_service_costs(slug,cal).values())*(1+cal['pilotage']['maintenance_pct']/100),2)
    assert 0<=core<=total
    return dict(core=core,integration=round(total-core,2),groupes=0)


def core_service_costs(slug, cal):
    """Existing Make Core maintenance and evolution costs, before shared oversight."""
    doc=active_doc(slug)
    maint=read(ROOT/f'source/maintenance/maintenance-{slug}.yaml')
    roles={a['id']:a['roles'] for a in maint['activites']}
    rates=role_rates(read(ROOT/f'source/stacks/{slug}.yaml'))
    scenario=annual_scenario()
    costs={}
    for a in doc['maintenance']['activites']:
        if a['activite'] not in ('MAI-003','MAI-009'):
            continue
        assert a['traitement']=='estimation'
        charges=a['charges'] if a['activite']=='MAI-003' else [c for c in a['charges'] if c['volume_ref']=='evolutions_fonctionnelles_an.core_generique']
        gross=(a['jh_fixes_avant_ia'] if a['activite']=='MAI-003' else 0)+sum(volume(scenario,c['volume_ref'])*c['jh_unitaire'] for c in charges)
        net=gross*(1-a['gain_ia_pct']/100)
        costs[a['activite']]=mixed_cost(net,roles[a['activite']],rates,cal['couts_communs']['outillage_realisation_eur_par_jh'])
    return costs

def finance_sensitivity(scenario, economic):
    """Pont du prix SAP Buy aux seules prestations Delaware retraitées."""
    spec=scenario['sensibilite_finance_sap']
    prices=read(ROOT/'source/chiffrage/chiffrage-sap.yaml')['integration']['prix_rfi']['postes_eur']
    sap=next(o for o in economic['options'] if o['stack']=='sap')
    assert sum(prices)==sap['detail_integration']['base_rfi']
    lots=[]
    for lot in spec['lots']:
        n=lot['numero']
        assert 1<=n<=len(prices) and 0<lot['jh_finance_fpa']<=lot['jh_externes']
        retrait=lot['jh_finance_fpa']*prices[n-1]/lot['jh_externes']
        lots.append(dict(numero=n,libelle=lot['libelle'],jh_externes=lot['jh_externes'],
                         jh_finance_fpa=lot['jh_finance_fpa'],prix_lot_eur_ht=prices[n-1],
                         retrait_indicatif_eur_ht=round(retrait,2)))
    assert len({lot['numero'] for lot in lots})==len(lots)
    retrait=round(sum(lot['jh_finance_fpa']*lot['prix_lot_eur_ht']/lot['jh_externes'] for lot in lots),2)
    sap_central=sap['synthese_eur_ht']['integration']
    additions=sap['detail_integration']
    complements_generiques=round(sum(f['cout_eur_ht'] for f in sap['features']
                                    if f['traitement']=='complement_integration'),2)
    supplement=round(additions['complements_flow']+additions['pilotage']+additions['preparation'],2)
    assert abs(sap_central-sum(prices)-supplement)<0.05
    assert complements_generiques<=additions['complements_flow']
    # New generic functional provisions are already financed by the Make build.
    excluded=round(complements_generiques*(1+read(ROOT/'source/calibration-couts.yaml')['pilotage']['complements_buy_pct']/100),2)
    return dict(statut=spec['statut'],methode=spec['methode'],lots=lots,
                jh_finance_fpa=sum(lot['jh_finance_fpa'] for lot in lots),
                jh_externes_tous_lots=spec['jh_lot_1_finance_ccm_mixte_non_retires']+sum(lot['jh_externes'] for lot in lots),
                jh_lot_1_mixte_non_retires=spec['jh_lot_1_finance_ccm_mixte_non_retires'],
                retrait_indicatif_eur_ht=retrait,
                base_delaware_apres_retrait_eur_ht=round(sum(prices)-retrait,2),
                integration_sap_apres_retrait_eur_ht=round(sap_central-retrait-excluded,2),
                complements_generiques_exclus_ancre_make_eur_ht=excluded,
                complements_generiques_sap_eur_ht=complements_generiques,
                qualification_automation_sap_eur_ht=round(additions['complements_flow']-complements_generiques,2),
                complements_sap_pilotage_preparation_retenus_dans_ancre_make_eur_ht=round(supplement-excluded,2),
                limite=spec['limite'])

def price_comparison(scenario, economic, cal, sap_anchor):
    """Contrepoint ESN par profils : aucun effet sur les budgets actifs."""
    spec=scenario['comparaison_prix_integration_miroir_sap']
    shares=spec['repartition_jh_base_pct']
    expected={'integration_metier','integration_it_donnees_qualification','developpement_java_react','pilotage'}
    assert set(shares)==expected and sum(shares.values())==100 and all(v>=0 for v in shares.values())
    assert spec['mode_achat']=='integrateur_esn'
    rates={}
    for role,info in spec['tarifs_eur_ht_jh'].items():
        rate=info['reference']
        assert role in expected and info['bas']<=rate<=info['haut'] and info['source'].startswith('https://')
        rates[role]=rate
    assert set(rates)==expected
    base_jh=sap_anchor['jh_externes_tous_lots']-sap_anchor['jh_finance_fpa']
    assert base_jh>0
    base_profils={role:dict(part_pct=share,jh=round(base_jh*share/100,2),tjm_eur_ht=rates[role],
                            cout_eur_ht=round(base_jh*share/100*rates[role],2))
                  for role,share in shares.items()}
    base_labour=round(sum(v['cout_eur_ht'] for v in base_profils.values()),2)
    sap_doc=active_doc('sap')
    map_nature=spec['complementation_par_nature']
    assert set(map_nature)==set(cal['natures'])|{'automatisation'}
    comp_nature={k:0.0 for k in map_nature}
    for f in sap_doc['core']:
        if f['traitement']!='complement_integration': continue
        for nature,jh in f['jh_backend_avant_ia'].items():
            comp_nature[nature]+=jh*(1-cal['ia']['taux_pct']['sap'][nature]/100)
    comp_nature['automatisation']=sap_doc['integration']['complement_qualification_automation_jh']
    comp_rows={nature:dict(profil=map_nature[nature],jh=round(jh,2),
                            tjm_eur_ht=rates[map_nature[nature]],cout_eur_ht=round(jh*rates[map_nature[nature]],2))
               for nature,jh in comp_nature.items()}
    comp_jh=round(sum(v['jh'] for v in comp_rows.values()),2)
    assert comp_jh>0
    sap=next(o for o in economic['options'] if o['stack']=='sap')
    tooling=cal['couts_communs']['outillage_realisation_eur_par_jh']
    assert abs(comp_jh*(role_rates(read(ROOT/'source/stacks/sap.yaml'))['developpement']+tooling)
               -sap['detail_integration']['complements_flow'])<0.05
    assert spec['pilotage_complements_ref']=='source/calibration-couts.yaml#pilotage/complements_buy_pct'
    assert spec['preparation_ref']=='source/calibration-couts.yaml#couts_communs/preparation_buy'
    comp_labour=round(sum(v['cout_eur_ht'] for v in comp_rows.values()),2)
    base_tools=0;comp_tools=0
    comp_pilot=round(comp_labour*cal['pilotage']['complements_buy_pct']/100,2)
    prep=cal['couts_communs']['preparation_buy']
    # The Make counterpart retains client automation, not the generic functions already built.
    automation_labour=comp_rows['automatisation']['cout_eur_ht']
    total=round(base_labour+base_tools+automation_labour*(1+cal['pilotage']['complements_buy_pct']/100)+prep,2)
    sap=next(o for o in economic['options'] if o['stack']=='sap')
    sap_esn=round(sap['detail_integration']['base_rfi']+comp_labour+comp_pilot+prep,2)
    esn=spec['contrepoint_integrateur_eur_jh']
    assert 0<esn['bas']<=esn['haut'] and esn['source'].startswith('https://')
    return dict(statut=spec['statut'],mode_achat=spec['mode_achat'],jh_base_sap_proxy=base_jh,
                pilotage_base_inclus_dans_parts=True,profils_base=base_profils,
                prix_delaware_moyen_eur_jh=round(sap['detail_integration']['base_rfi']/sap_anchor['jh_externes_tous_lots'],2),
                prix_grille_esn_pondere_eur_jh=round(base_labour/base_jh,2),
                cout_base_profils_eur_ht=base_labour,outillage_base_eur_ht=base_tools,
                complements_jh_par_nature=comp_rows,complements_jh_total=comp_jh,
                cout_complements_profils_eur_ht=comp_labour,outillage_complements_eur_ht=comp_tools,
                pilotage_complements_pct=cal['pilotage']['complements_buy_pct'],
                pilotage_complements_eur_ht=comp_pilot,preparation_eur_ht=prep,
                cout_esn_par_profils_indicatif_eur_ht=total,
                ecart_avec_ancre_sap_eur_ht=round(total-sap_anchor['integration_sap_apres_retrait_eur_ht'],2),
                sap_buy_avec_complements_esn_indicatif_eur_ht=sap_esn,
                ecart_avec_sap_buy_actif_eur_ht=round(sap_esn-sap['synthese_eur_ht']['integration'],2),
                contrepoint_integrateur_avec_pilotage_eur_ht={
                    'bas':round((base_jh+comp_nature['automatisation'])*esn['bas']+prep,2),
                    'haut':round((base_jh+comp_nature['automatisation'])*esn['haut']+prep,2)},
                limite=spec['limite'])

@scoped_model
def prepare(economic=None, include_presentation=False):
    scenario = read(ROOT/'source/plan-investissement.yaml')
    glossary = read(ROOT/'source/glossaire.yaml')
    assert scenario['horizon_ans'] == 10
    assert scenario['projection_ans'] >= scenario['horizon_ans']
    economic = economic if economic is not None else valuation()
    cal=read(ROOT/'source/calibration-couts.yaml')
    inflation = read(ROOT/'source/inflation.yaml')['categories']
    rates = {k:inflation[k]['taux_annuel_pct']['central']/100 for k in
             ['tjm_ingenierie','cloud','licences_logiciels']}
    sap_anchor=finance_sensitivity(scenario,economic)
    price_challenge=price_comparison(scenario,economic,cal,sap_anchor)
    bonus_pct=scenario['integration_make']['bonus_continuite_build_pct']
    assert isinstance(bonus_pct,(int,float)) and not isinstance(bonus_pct,bool) and 0<=bonus_pct<=50
    ancre_make_avant_bonus=sap_anchor['integration_sap_apres_retrait_eur_ht']
    integration_make=round(ancre_make_avant_bonus*(1-bonus_pct/100),2)
    bonus_make=dict(taux_pct=bonus_pct,ancre_avant_bonus_eur_ht=ancre_make_avant_bonus,
                    reduction_eur_ht=round(ancre_make_avant_bonus-integration_make,2),
                    budget_apres_bonus_eur_ht=integration_make)
    duration_make = funding_inputs()[1]['scenarios']['central']['duree_mois']
    selection=buy_selection_inputs()
    assert cal['couts_communs']['preparation_buy']==0, 'Preparation already transferred to Buy selection'
    options = []
    for o in economic['options']:
        slug=o['stack']; make=o['strategie']=='make'
        name=glossary['options'][slug]['libelle']
        p=o['maintenance_annuelle'][0]['postes_eur_ht']
        # Nature des achats commune aux cinq options. La provenance des prix
        # ne crée pas une catégorie économique. Le prix éditeur reste groupé.
        base = dict(services_mco=p['prestations_estimees']+p['pilotage']+p['outillage_audits']+p['forfaits_rfi'],
                    hebergement=p['cloud_hors_panier'],
                    ipaas=p['ipaas'],
                    licences_complementaires=p['droits_complementaires'])
        n=0 if make else len(cal['convention'][slug+'_licences_annees_sources'])
        prices=[x['postes_eur_ht']['licences_rfi'] for x in o['maintenance_annuelle'][:n]]
        assert abs(sum(base.values())+(prices[0] if prices else 0)-o['synthese_eur_ht']['maintenance_premiere_annee'])<0.05
        options.append(dict(stack=slug,nom=name,mode='Make' if make else 'Buy',
          build=o['synthese_eur_ht']['build_core'],
          integration_source=o['synthese_eur_ht']['integration'],
          integration=0 if make else o['synthese_eur_ht']['integration'],
          build_mois=scenario['build_make_mois'][slug] if make else 0,
          integration_mois=duration_make if make else scenario['integration_buy_mois'][slug],
          selection_buy=0 if make else selection['budget_eur'],
          selection_mois=0 if make else selection['duree_mois'],
          base_annuelle=base,ventilation_services=split_services(slug,base['services_mco'],cal),
          ipaas_indexation_logiciel=(cal['couts_communs']['indexation_ipaas'][slug]=='licences_logiciels'),
          prix_abonnements=prices,
          detail_integration=o['detail_integration'],detail_build=o['detail_build']))
    for o,e in zip(options,economic['options']):
        if o['mode']=='Make':
            ref=dict(o['ventilation_services'])
            o['composable']=dict(reference_services=ref, inputs=load_funding_model(o['stack']),
                annual_reference=annual_split(o['stack'],e,o['base_annuelle']['services_mco'],ref['core'],cal))
            ledger=initial_ledger(o,ref)
            o['integration']=round(sum(r['amount'] for r in ledger if r['phase']=='integration'),2)
    return dict(scenario=scenario,taux=rates,options=options,
                explications=read(ROOT/'source/explications-modele.yaml'),
                glossaire=glossary,**({'presentation':read(ROOT/'config/restitution-investissements.yaml')} if include_presentation else {}),
                sensibilite_finance_sap=sap_anchor,bonus_continuite_make=bonus_make,
                comparaison_prix_integration=price_challenge,
                empreintes={**economic['dependances'],
                'source/plan-investissement.yaml':sha('source/plan-investissement.yaml'),
                'source/explications-modele.yaml':sha('source/explications-modele.yaml'),
                'source/glossaire.yaml':sha('source/glossaire.yaml'),
                'sources/client/copil-5.pdf':sha('sources/client/copil-5.pdf'),
                'source/modele-composable.yaml':sha('source/modele-composable.yaml'),
                'source/deploiement-groupe.yaml':sha('source/deploiement-groupe.yaml'),
                'source/selection-buy.yaml':sha('source/selection-buy.yaml'),
                'tools/composable_costs.py':sha('tools/composable_costs.py'),
                'tools/project_investment.py':sha('tools/project_investment.py')})

def subscription_expense(prices, inflation, start, lo, hi):
    """Preserve each supplier annuity on its own 12-month contract interval."""
    total=0
    for index in range(math.ceil(hi/12)):
        amount=prices[index] if index<len(prices) else prices[-1]*(1+inflation)**(index+1-len(prices))
        total+=phase_expense(amount,start+12*index,12,lo,hi)
    return round(total,2)


def project_financing(option, ledger, parts, rate, years=10):
    """Pure annual projection of one explicit funding ledger and recurring services."""
    o=option; end=o["build_mois"]+o.get('selection_mois',0)+o["integration_mois"]
    base=o["base_annuelle"]; prices=o["prix_abonnements"]; rows=[]
    for y in range(1,years+1):
        lo=(y-1)*12; hi=y*12
        detail={k:0.0 for k in RESPONSIBILITIES}
        initial={k:0.0 for k in ('build','integration','mco_run')}
        for line in ledger:
            paid=phase_expense(line['amount'],line['start'],line['end']-line['start'],lo,hi)
            detail[line['responsibility']]+=paid; initial[line['phase']]+=paid
        build=round(initial['build'],2);integration=round(initial['integration'],2)
        service=max(0,hi-max(lo,end))/12
        licence=0 if not prices else subscription_expense(prices,rate['licences_logiciels'],o.get('selection_mois',0),lo,hi)
        ipaas_rate=rate['licences_logiciels'] if o['ipaas_indexation_logiciel'] else rate['cloud']
        mco=service*(base['services_mco']*(1+rate['tjm_ingenierie'])**(y-1)
                     +base['hebergement']*(1+rate['cloud'])**(y-1)
                     +base['ipaas']*(1+ipaas_rate)**(y-1)
                     +base['licences_complementaires']*(1+rate['licences_logiciels'])**(y-1))+licence
        recurring={k:0.0 for k in RESPONSIBILITIES}
        for key,value in parts.items(): recurring[key]+=service*value*(1+rate['tjm_ingenierie'])**(y-1)
        recurring['run']+=service*(base['hebergement']*(1+rate['cloud'])**(y-1)+base['ipaas']*(1+ipaas_rate)**(y-1)+base['licences_complementaires']*(1+rate['licences_logiciels'])**(y-1))
        recurring['grouped_buy']+=licence
        recurring={k:round(v,2) for k,v in recurring.items()}
        residual=round(round(mco,2)-sum(recurring.values()),2)
        recurring['grouped_buy' if prices else 'run']+=residual
        detail={k:round(detail[k]+recurring[k],2) for k in RESPONSIBILITIES}
        pieces=dict(build=build,integration=integration,mco_run=round(round(mco,2)+round(initial['mco_run'],2),2))
        total=round(sum(pieces.values()),2)
        assert round(sum(detail.values()),2)==total
        # Orthogonal reading of the same paid amounts. Legacy responsibilities
        # and budget buckets retain their meaning for saved simulations.
        cloud_initial=sum(phase_expense(l['amount'],l['start'],l['end']-l['start'],lo,hi)
            for l in ledger if l['id'].startswith('hebergement_build/') or l['id']=='moyens_transition/hebergement')
        purchases_initial=sum(phase_expense(l['amount'],l['start'],l['end']-l['start'],lo,hi)
            for l in ledger if l['id'] in ('moyens_transition/ipaas','moyens_transition/droits'))
        cloud=round(cloud_initial+service*base['hebergement']*(1+rate['cloud'])**(y-1),2)
        purchases=round(purchases_initial+service*(base['ipaas']*(1+ipaas_rate)**(y-1)
            +base['licences_complementaires']*(1+rate['licences_logiciels'])**(y-1)),2)
        natures=dict(obtention=build,integration=integration,
            core_care=round(detail['core_lifecycle']-(build if o['mode']=='Make' else 0),2),
            client_care=round(detail['mco_client']+detail['client_evolutions'],2),
            run_cloud=cloud,technical_purchases=purchases,
            operations_support=round(detail['run']-cloud-purchases,2),grouped_buy=detail['grouped_buy'])
        assert round(sum(natures.values()),2)==total
        rows.append(dict(annee=y,**pieces,total=total,responsibilities=detail,cost_natures=natures))
    return rows


def project(data, horizon_years=None):
    years=horizon_years or data['scenario']['projection_ans']
    assert data['scenario']['horizon_ans'] <= years <= data['scenario']['projection_ans']
    results=[]
    for o in data['options']:
        b=o['build_mois']+o.get('selection_mois',0); d=o['integration_mois']; end=b+d
        assert (o['mode']=='Buy' and o['build_mois']==0) or 36<=b<=60
        assert 6<=d<=60 and end<=120

        ledger=initial_ledger(o,o['composable']['reference_services']) if o['mode']=='Make' else [
            dict(id='integration_initiale',financement_id='integration_initiale',amount=o['integration'],start=b,end=end,
                 objet='adaptations_client',prestation='integration',responsibility='integration_client',phase='integration',source=f"source/chiffrage/chiffrage-{o['stack']}.yaml")]
        if o['mode']=='Buy' and o.get('selection_buy',0):
            ledger.insert(0,dict(id='selection_contractualisation',financement_id='selection_contractualisation',amount=o['selection_buy'],start=0,end=b,
                objet='programme',prestation='pilotage',responsibility='integration_client',phase='build',source='source/selection-buy.yaml'))
        o['integration']=round(sum(r['amount'] for r in ledger if r['phase']=='integration'),2)
        parts=service_parts(o)
        rows=project_financing(o,ledger,parts,data["taux"],years)
        totals={k:round(sum(a[k] for a in rows),2) for k in ['build','integration','mco_run','total']}
        assert totals['build']==round(o['build']+o.get('selection_buy',0),2)
        assert totals['integration']==round(o['integration'],2)
        assert totals['total']==round(sum(totals[k] for k in ('build','integration','mco_run')),2)
        results.append(dict(stack=o['stack'],annees_service_complet=(years*12-end)/12,
                            services_annuels_reference_eur_ht=o['ventilation_services'],totaux_eur_ht=totals,annees=rows,
                            responsabilites_eur_ht={k:round(sum(a['responsibilities'][k] for a in rows),2) for k in RESPONSIBILITIES},
                            financements_initiaux=ledger,services_composables=parts))
    return dict(id=f'investissements-{years}-ans',date=data['scenario']['date'],horizon_ans=years,
                nature=resolve_text_tree(data['explications']['resultats_generes']['investissements_10_ans'],data['glossaire'],{'bonus_continuite_pct':data['bonus_continuite_make']['taux_pct']})['nature'],
                statut_integration_make=data['scenario']['integration_make']['statut'],
                dependances=data['empreintes'],conventions=data['scenario']['repartition'],
                sensibilite_finance_sap=data['sensibilite_finance_sap'],
                bonus_continuite_make=data['bonus_continuite_make'],
                comparaison_prix_integration=data['comparaison_prix_integration'],options=results)

if __name__=='__main__':
    data=prepare(include_presentation=True); result=project(data)
    if '--check' in sys.argv:
        assert read(OUTPUT)==result, 'Projection YAML obsolète'
    else:
        OUTPUT.write_text(yaml.safe_dump(result,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
        out=ROOT/'tmp/investissement-15-ans'; out.mkdir(parents=True,exist_ok=True)
        (out/'inputs.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        (out/'expected.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    for o in result['options']: print(o['stack'],o['totaux_eur_ht'])
