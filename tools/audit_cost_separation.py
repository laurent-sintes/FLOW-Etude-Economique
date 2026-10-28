"""Reconcile Core build, integration and recurring costs against an independent ledger.

Writes audit evidence only. Does not regenerate results or change assumptions.
"""
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_EVEN
from fractions import Fraction
import argparse
import hashlib
import json
from pathlib import Path

from validate_stacks import ROOT, read
from calculate_costs import calculate, calculate_option, validate_inputs
from study_app import Study


def dec(value):
    return Decimal(str(value))


def cents(value):
    if isinstance(value,Fraction):return round(value*100)
    return int((dec(value)*100).quantize(Decimal('1'), rounding=ROUND_HALF_EVEN))


def monetary_sum(values):
    return sum(cents(v) for v in values)


def independent_projection(option, rates):
    """Monthly phase overlap; cumulatively rounded initial budgets, annual services.

    The monthly loop is deliberately different from project()'s yearly intersection.
    It supports fractional phase boundaries and does not call project().
    """
    b=dec(option['build_mois'])+dec(option.get('selection_mois',0)); end=b+dec(option['integration_mois'])
    cumulative={'build':Fraction(0),'integration':Fraction(0)}
    previous={'build':0,'integration':0}; rows=[]
    prices=option['prix_abonnements']; base=option['base_annuelle']
    for year in range(1,11):
        service=Decimal(0)
        for month in range((year-1)*12,year*12):
            lo=dec(month); hi=lo+1
            if b:
                cumulative['build']+=Fraction(str(option['build']+option.get('selection_buy',0)))*Fraction(max(Decimal(0),min(hi,b)-lo))/Fraction(b)
            cumulative['integration']+=Fraction(str(option['integration']))*Fraction(max(Decimal(0),min(hi,end)-max(lo,b)))/Fraction(end-b)
            service+=max(Decimal(0),hi-max(lo,end))/12
        row={k:cents(v)-previous[k] for k,v in cumulative.items()}
        previous={k:cents(v) for k,v in cumulative.items()}
        recurring=Decimal(0)
        for key,category in [('services_mco','tjm_ingenierie'),('hebergement','cloud'),
                ('ipaas','licences_logiciels' if option['ipaas_indexation_logiciel'] else 'cloud'),
                ('licences_complementaires','licences_logiciels')]:
            recurring+=dec(base[key])*(1+dec(rates[category]))**(year-1)
        licence=Decimal(0)
        for index in range(10) if prices else []:
            price=dec(prices[index]) if index<len(prices) else dec(prices[-1])*(1+dec(rates['licences_logiciels']))**(index+1-len(prices))
            start=dec(option.get('selection_mois',0))+12*index
            f1=max(Decimal(0),min(Decimal(1),(dec(year*12)-start)/12))
            f0=max(Decimal(0),min(Decimal(1),(dec((year-1)*12)-start)/12))
            licence+=dec(cents(price*f1)-cents(price*f0))/100
        row['mco_run']=cents(service*recurring+licence)
        row['total']=sum(row.values());row['annee']=year;rows.append(row)
    return rows


def audit():
    study=Study(); cal,docs=validate_inputs()
    checks=[];ledgers={};cases={};variants={}
    def check(name,actual,expected,context=None):
        checks.append(dict(check=name,ok=actual==expected,actual=actual,expected=expected,context=context))
    check('stored_economics_current',read(ROOT/'source/couts-15-ans.yaml'),calculate())
    # Keep evidence compact while still naming stale files.
    for c in checks:
        if isinstance(c['actual'],dict):
            c['actual']={'sha256':hashlib.sha256(json.dumps(c['actual'],sort_keys=True).encode()).hexdigest()}
            c['expected']={'sha256':hashlib.sha256(json.dumps(c['expected'],sort_keys=True).encode()).hexdigest()}
    stored=read(ROOT/'source/investissements-10-ans.yaml')
    check('stored_projection_dependencies',stored['dependances'],study.data['empreintes'])
    checks[-1]['actual']=[p for p,h in stored['dependances'].items() if study.data['empreintes'].get(p)!=h]
    checks[-1]['expected']=[]
    for slug,doc in docs.items():
        stack=read(ROOT/f'source/stacks/{slug}.yaml')
        rates={role:stack['interventions']['tarifs'][a['tarif']]['reference'] for role,a in stack['interventions']['activites'].items()}
        front_stack=read(ROOT/'source/stacks/java-spring.yaml')
        front_rate=front_stack['interventions']['tarifs'][front_stack['interventions']['activites']['developpement']['tarif']]['reference']
        maint=read(ROOT/f'source/maintenance/maintenance-{slug}.yaml')
        roles={a['id']:a['roles'] for a in maint['activites']}
        source_prices={p['id']:p for p in maint['valorisation_annuelle']['postes']}
        scenario=read(ROOT/'source/maintenance.yaml')['scenario_annuel']
        def vol(path):
            if path=='un_service_annuel':return 1
            v=scenario['volumes']
            for part in path.split('.'):v=v[part]
            return v
        make=doc['strategie']=='make'; rows=[]
        for sensitivity in ('bas','central','haut'):
            o=calculate_option(slug,doc,cal,sensitivity)
            cases[slug+'/'+sensitivity]=o['synthese_eur_ht']
            jhf=1 if sensitivity=='central' else cal['sensibilite']['jh_'+sensitivity]
            tools=cal['couts_communs']['outillage_realisation_eur_par_jh']
            work=0
            for f in doc['core']:
                if f['traitement']=='inclus_rfi':continue
                gross=f['plages_jh'][sensitivity]
                work+=sum(gross[n]*(1-(0 if sensitivity=='haut' else cal['ia']['taux_pct'][slug][n])/100)*(rates['qa' if n=='qualification' else 'developpement']+tools) for n in cal['natures'])
                work+=gross['frontend']*(1-(0 if sensitivity=='haut' else cal['ia']['frontend_pct'])/100)*(front_rate+tools)
            check('functional_work_once',cents(o['detail_build']['prestations'] if make else o['detail_integration']['complements_flow']-doc['integration']['complement_qualification_automation_jh']*jhf*(rates['integration']+tools)),cents(work),slug+'/'+sensitivity)
            labour=0
            for a in doc['maintenance']['activites']:
                gross=a['jh_fixes_avant_ia']+sum(vol(c['volume_ref'])*c['jh_unitaire'] for c in a['charges'])
                amount=gross*jhf*(1-(0 if sensitivity=='haut' else a['gain_ia_pct'])/100)*sum(r['part_pct']/100*(rates[k]+tools) for k,r in (roles[a['activite']] or {}).items())
                if a['traitement']=='estimation':labour+=amount
                if sensitivity=='central':rows.append(dict(id=a['activite'],traitement=a['traitement'],diagnostic_eur=round(amount,2),facture_en_plus_eur=round(amount,2) if a['traitement']=='estimation' else 0))
            labour+=doc['maintenance']['maintenance_complements_buy_jh_annuels']*jhf*(rates['developpement']+tools)
            if make:labour+=40*jhf*max(0,rates['architecte']-rates['support_n3'])
            check('annual_labour_excludes_included_work',cents(o['maintenance_annuelle'][0]['postes_eur_ht']['prestations_estimees']),cents(labour),slug+'/'+sensitivity)
            check('integration_detail_sum',monetary_sum(o['detail_integration'].values()),cents(o['synthese_eur_ht']['integration']),slug+'/'+sensitivity)
            check('build_detail_sum',monetary_sum(o['detail_build'].values()),cents(o['synthese_eur_ht']['build_core']),slug+'/'+sensitivity)
            check('economic_total_sum',monetary_sum(o['synthese_eur_ht'][k] for k in ('build_core','integration','maintenance_15_ans')),cents(o['synthese_eur_ht']['total']),slug+'/'+sensitivity)
            if not make:
                check('buy_integration_bundle_once',o['detail_integration']['base_rfi'],sum(doc['integration']['prix_rfi']['postes_eur']),slug+'/'+sensitivity)
                check('buy_no_build',o['synthese_eur_ht']['build_core'],0,slug+'/'+sensitivity)
                check('buy_no_diagnostic_integration_added',o['detail_integration']['prestations_estimees'],0,slug+'/'+sensitivity)
            for annual in o['maintenance_annuelle']:
                check('annual_economic_sum',monetary_sum(annual['postes_eur_ht'].values()),cents(annual['total_eur_ht']),slug+'/'+sensitivity+'/'+str(annual['annee_service']))
            if sensitivity=='central':
                if slug=='sap':check('sap_annual_bundles_once',o['maintenance_annuelle'][0]['postes_eur_ht']['forfaits_rfi'],sum(source_prices[k]['montants_documentes_eur_ht'][0]['montant'] for k in ('rfi-mco','rfi-monitoring','rfi-evolutions')),slug)
                if slug=='microsoft':check('microsoft_support_initial_once',o['detail_integration']['support_microsoft_premiere_annee'],source_prices['MAI-013/outillage-support']['montants_documentes_eur_ht'][0]['montant'],slug)
                check('annual_ui_reconciliation',monetary_sum(b['total'] for b in study.content['stacks'][slug]['economic_reading']['buckets'].values()),cents(o['maintenance_annuelle'][0]['total_eur_ht']),slug)
        ledgers[slug]=rows
    for option in study.data['options']:
        slug=option['stack']; api=next(o for o in study.baseline['options'] if o['stack']==slug)
        independent=independent_projection(option,study.data['taux'])
        disk=next(o for o in stored['options'] if o['stack']==slug)
        check('api_annual_matches_saved',api['annual'],disk['annees'],slug)
        for row,want in zip(api['annual'],independent):
            for k in ('build','integration','mco_run','total'):check('monthly_independent_'+k,cents(row[k]),want[k],slug+'/'+str(row['annee']))
            check('annual_three_posts_sum',monetary_sum(row[k] for k in ('build','integration','mco_run')),cents(row['total']),slug+'/'+str(row['annee']))
        for k in ('build','integration'):
            check('initial_budget_conserved',monetary_sum(row[k] for row in api['annual']),cents(api[k]),slug+'/'+k)
        for h in api['horizons']:
            for k in ('build','integration','mco_run','total'):
                check('horizon_'+k,cents(h['totals'][k]),sum(row[k] for row in independent[:h['years']]),slug+'/'+str(h['years']))
            check('remaining_initial',cents(h['remaining']),max(0,cents(api['build'])+cents(api['integration'])-cents(h['totals']['build'])-cents(h['totals']['integration'])),slug+'/'+str(h['years']))
    for label,change in [('sap_plus_1m',('options','sap','integration',1000000)),('ms_plus_1m',('options','microsoft','integration',1000000)),('java_build_plus_1m',('options','java-spring','build',1000000)),('java_annual_plus_10k',('options','java-spring','services_core',10000))]:
        p=deepcopy(study.parameters);_,slug,key,delta=change;p['options'][slug][key]+=delta
        result=study.simulate(p);variants[label]={}
        for o in result['options']:
            initial=next(x for x in study.baseline['options'] if x['stack']==o['stack'])
            variants[label][o['stack']]={k:round(o[k]-initial[k],2) for k in ('build','integration')}
            if label=='sap_plus_1m':
                expected=delta*(1-p['common']['bonus_continuite_pct']/100) if o['mode']=='Make' else delta if o['stack']=='sap' else 0
                check('sap_anchor_propagates_once',cents(o['integration'])-cents(initial['integration']),cents(expected),o['stack'])
            elif label in ('ms_plus_1m','java_build_plus_1m'):
                changed='integration' if label=='ms_plus_1m' else 'build'
                check('independent_budget_parameter',cents(o[changed])-cents(initial[changed]),cents(delta) if o['stack']==slug else 0,label+'/'+o['stack'])
            else:
                check('annual_parameter_does_not_change_initial',cents(o['build'])+cents(o['integration']),cents(initial['build'])+cents(initial['integration']),o['stack'])
    boundary_sensitivities={}
    for slug in ('microsoft','sap'):
        current=next(o for o in study.economic['options'] if o['stack']==slug)
        # No demonstrated generic developments are currently retained. This amount is
        # exclusively the additional client qualification allowance plus its oversight.
        supplement=round(current['detail_integration']['complements_flow']*(1+cal['pilotage']['complements_buy_pct']/100),2)
        p=deepcopy(study.parameters);p['options'][slug]['integration']-=supplement
        simulated=study.simulate(p)
        boundary_sensitivities['qualification_incluse_'+slug]={'initial_removed':supplement,
            'delta_10_years':{o['stack']:round(o['horizons'][-1]['totals']['total']-next(b for b in study.baseline['options'] if b['stack']==o['stack'])['horizons'][-1]['totals']['total'],2) for o in simulated['options']}}
    transition={}
    for o in study.data['options']:
        if o['mode']!='Make':continue
        # Isolated upper reading: 100% of the current Core annual service between
        # end of build and commissioning; no assumption about an actual ramp-up.
        cost=0
        for y in range(1,11):
            months=max(0,min(y*12,o['build_mois']+o['integration_mois'])-max((y-1)*12,o['build_mois']))
            cost+=o['ventilation_services']['core']*(1+study.data['taux']['tjm_ingenierie'])**(y-1)*months/12
        transition[o['stack']]=round(cost,2)
    boundary_sensitivities['service_core_pendant_integration']=dict(cost_10_years=transition,
        status='Isolated sensitivity, not active; possible inclusion in integration must be checked before adding it.')
    return dict(date='2026-10-26',model_version=study.version,checks=checks,failures=[c for c in checks if not c['ok']],
        totals_10_years={o['stack']:o['horizons'][-1]['totals'] for o in study.baseline['options']},
        ledger=ledgers,sensitivities=cases,parameter_variants=variants,boundary_sensitivities=boundary_sensitivities,
        included_scope='Five options, 15 service years, 10 project years, horizons 3/5/7/10; current hypotheses only.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='audits/2026-10-26-coherence-couts-preuves.json');args=parser.parse_args()
    result=audit();target=ROOT/args.output
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(checks=len(result['checks']),failures=len(result['failures']),output=str(target)),ensure_ascii=False))
    for c in result['failures'][:25]:print(json.dumps(c,ensure_ascii=False))
    raise SystemExit(bool(result['failures']))
