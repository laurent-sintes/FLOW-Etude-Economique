"""Opportunity proposal only. Reads active inputs; writes this audit folder only."""
from pathlib import Path
from collections import Counter
import hashlib,json,sys

ROOT=Path(__file__).resolve().parents[1];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
from validate_stacks import read

def active_hashes():
    paths=[]
    for directory in ['source','sources','config','tools','app/src']:
        paths.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and p.suffix in ['.yaml','.py','.tsx','.ts','.css','.md','.pdf','.xlsx','.pptx','.docx'])
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
ACTIVE_BEFORE=active_hashes()
SLUGS=('java-spring','dotnet','rust')
DEFINITION=read(HERE/'2026-10-27-integration-make-rapprochement.yaml')
BLOCKS=DEFINITION['blocs']
PROPOSAL=DEFINITION['proposition']
# These boundaries are intentional: no undisclosed deduction or extra service.
assert PROPOSAL['continuity_gain_pct']==0
assert PROPOSAL['removed_overlap_eur']==0
assert PROPOSAL['core_transition_included_in_base'] is False
assert PROPOSAL['programme_governance_eur'] is None
assert all(value is None for value in DEFINITION['non_chiffre'].values())
inputs=['source/calibration-couts.yaml','source/maintenance.yaml','source/recalibration-metier.yaml',
        'source/parcours-integration.yaml','source/grille-complexite.yaml','source/plan-investissement.yaml',
        'source/inflation.yaml','source/couts-15-ans.yaml','source/investissements-10-ans.yaml',
        'sources/client/microsoft-1.pdf','sources/client/delaware-septembre.pdf',
        'sources/client/rfi-presentation.pdf','sources/client/copil-5.pdf',
        'sources/client/microsoft-questionnaire.xlsx']
cal=read(ROOT/inputs[0]);common=cal['couts_communs'];scenario=read(ROOT/'source/maintenance.yaml')['scenario_annuel']
business=read(ROOT/'source/recalibration-metier.yaml');grid=read(ROOT/'source/grille-complexite.yaml')
plan=read(ROOT/'source/plan-investissement.yaml');inflation=read(ROOT/'source/inflation.yaml')['categories']['tjm_ingenierie']['taux_annuel_pct']['central']/100
saved={o['stack']:o for o in read(ROOT/'source/couts-15-ans.yaml')['options']}
investment={o['stack']:o for o in read(ROOT/'source/investissements-10-ans.yaml')['options']}
capture=grid['dependances']['cartographie'];inputs.append(capture)
nodes={n['id']:n for n in read(ROOT/capture)['nodes']};bycap={b['capacite_id']:b for b in grid['blocs']}
paths=read(ROOT/'source/parcours-integration.yaml')
assigned=[a for b in BLOCKS for a in b['activities']]
assert Counter(assigned)==Counter(f'INT-{n:03}' for n in range(1,14))
for block in BLOCKS:
    block['capability_links']=[dict(id=c,name=nodes[c]['fields']['name'],path=bycap[c]['chemin'],
        source=f'{capture}#{c}',status='Rapprochement proposé sans allocation monétaire') for c in block['capabilities']]
    block['scenario_examples']=[s['scenario'] for s in paths['scenarios']
        if s['scenario'] in ['transfer-replenishment-order-driven','b2b-partial-stock','last-item-concurrency','return-fashion-recovery','workflow-version-change']
        and set(s['capacites'])&set(block['capabilities'])]
report={'nature':'Proposition d’assiette technique partielle pour opportunité, non appliquée au modèle',
    'source_precision':'Les volumes et tarifs de cadrage existants restent des hypothèses. Les pièces fournisseur ne prouvent pas leur transposition FLOW.',
    'blocks':BLOCKS,'programme_governance_eur':None,'total_programme_eur':None,
    'proposal':DEFINITION['proposition'],
    'options':{}}
for slug in SLUGS:
    filenames=[f'source/chiffrage/chiffrage-{slug}.yaml',f'source/integration/integration-{slug}.yaml',
               f'source/stacks/{slug}.yaml',f'source/maintenance/maintenance-{slug}.yaml']
    inputs+=filenames;doc,integ,stack,maint=[read(ROOT/p) for p in filenames]
    originals={a['id']:a for a in integ['activites']}
    def build_variant(gain,flux_jh=None,price_case='reference'):
        rates={role:stack['interventions']['tarifs'][spec['tarif']][price_case] for role,spec in stack['interventions']['activites'].items()}
        rows={}
        for a in doc['integration']['activites']:
            gross=flux_jh if a['activite']=='INT-006' and flux_jh is not None else a['jh_avant_ia']
            expert=a['jh_expertise_transverse'];normal=(gross-expert)*(1-gain/100)
            cost=sum(normal*spec['part_pct']/100*(rates[role]+common['outillage_realisation_eur_par_jh']) for role,spec in originals[a['activite']]['roles'].items())+expert*(common['tarif_expert_transverse_eur_jh']+common['outillage_realisation_eur_par_jh'])
            rows[a['activite']]=dict(gross_jh=gross,net_jh=normal+expert,cost_eur=cost)
        extra_jh=common['accompagnement_applicatif_make_jh'];extra=extra_jh*(rates['integration']+common['outillage_realisation_eur_par_jh'])
        labour=round(sum(r['cost_eur'] for r in rows.values())+extra,2)
        pilot=round((sum(r['cost_eur'] for r in rows.values())+extra)*cal['pilotage']['integration_make_pct']/100,2)
        prep=common['preparation_make'];total=round(labour+pilot+prep,2)
        grouped={}
        for block in BLOCKS:
            ids=block['activities'];is_socle=block['id']=='socle_formation_transition';is_gov=block['id']=='gouvernance'
            raw=sum(rows[i]['cost_eur'] for i in ids)+(extra+prep if is_socle else 0)
            grouped[block['id']]=dict(gross_jh=None if is_gov else sum(rows[i]['gross_jh'] for i in ids)+(extra_jh if is_socle else 0),
                net_jh=None if is_gov else sum(rows[i]['net_jh'] for i in ids)+(extra_jh if is_socle else 0),
                cost_eur=pilot if is_gov else round(raw,2),raw_cost_eur=pilot if is_gov else raw)
        # Reconcile presentation groups by difference of cumulative cents, not an economic adjustment.
        socle=grouped['socle_formation_transition'];socle['cost_eur']=round(total-sum(v['cost_eur'] for k,v in grouped.items() if k!='socle_formation_transition'),2)
        socle['rounding_reconciliation_eur']=round(socle['cost_eur']-round(socle['raw_cost_eur'],2),2)
        assert round(sum(g['cost_eur'] for g in grouped.values()),2)==total
        return dict(gain_pct=gain,flux_gross_jh=rows['INT-006']['gross_jh'],price_case=price_case,rates=rates,
            blocks=grouped,rows=rows,extra_jh=extra_jh,extra_eur=extra,labour_eur=labour,pilot_eur=pilot,
            preparation_eur=prep,total_eur=total,gross_total_jh=sum(r['gross_jh'] for r in rows.values())+extra_jh,
            net_total_jh=sum(r['net_jh'] for r in rows.values())+extra_jh)
    variants={'current':build_variant(cal['ia']['integration_pct'][slug]),'without_ai':build_variant(0)}
    for case,unit in PROPOSAL['days_per_interface'].items():
        variants['proposal_flow_'+case]=build_variant(PROPOSAL['integration_ai_gain_pct'],PROPOSAL['interfaces']*unit)
    proposed_flux=PROPOSAL['interfaces']*PROPOSAL['days_per_interface']['central']
    variants['tariff_only_low']=build_variant(PROPOSAL['integration_ai_gain_pct'],proposed_flux,'bas')
    variants['tariff_only_high']=build_variant(PROPOSAL['integration_ai_gain_pct'],proposed_flux,'haut')
    assert variants['current']['total_eur']==saved[slug]['synthese_eur_ht']['integration']
    annual_roles={a['id']:a['roles'] for a in maint['activites']};maintenance_rows={a['activite']:a for a in doc['maintenance']['activites']}
    rates=variants['current']['rates'];method=business['maintenance']['par_stack'][slug];volumes=scenario['volumes']
    start=plan['build_make_mois'][slug];duration=sum(plan['integration_buy_mois'].values())/len(plan['integration_buy_mois'])
    assert duration==34
    indexed_factor=sum(max(0,min(year*12,start+duration)-max((year-1)*12,start))/12*(1+inflation)**(year-1) for year in range(1,11))
    transition={}
    units=[('corrections','MAI-003',volumes['corrections_core_an'],method['correction_core']),
           ('releases','MAI-003',volumes['campagnes_qualification_versions_an'],method['qualification_release']),
           ('evolutions','MAI-009',volumes['evolutions_fonctionnelles_an']['core_generique'],method['evolution_core'])]
    for label,activity,qty,unit in units:
        gross=qty*unit;rate=sum(r['part_pct']/100*(rates[role]+common['outillage_realisation_eur_par_jh']) for role,r in annual_roles[activity].items())
        transition[label]={'activity':activity,'quantity_per_year':qty,'jh_per_unit':unit,'gross_jh_per_year':gross,'current_gain_pct':maintenance_rows[activity]['gain_ia_pct'],'scenarios':{}}
        for case,gain in [('current_gain',maintenance_rows[activity]['gain_ia_pct']),('no_gain',0)]:
            annual=gross*(1-gain/100)*rate*(1+cal['pilotage']['maintenance_pct']/100)
            transition[label]['scenarios'][case]=dict(annual_cost_eur=round(annual,2),constant_34_month_eur=round(annual*duration/12,2),indexed_34_month_eur=round(annual*indexed_factor,2))
    total_core_current=sum(c['scenarios']['current_gain']['annual_cost_eur'] for c in transition.values())
    assert abs(total_core_current-investment[slug]['services_annuels_reference_eur_ht']['core'])<=0.02
    for case in ('current_gain','no_gain'):
        annual_total=round(sum(c['scenarios'][case]['annual_cost_eur'] for c in transition.values()),2)
        for kind,factor in [('constant_34_month_eur',duration/12),('indexed_34_month_eur',indexed_factor)]:
            # Apply the cent-denominated annual base once, then preserve that amount in component display.
            target=round(annual_total*factor,2)
            transition['evolutions']['scenarios'][case][kind]=round(target-sum(transition[k]['scenarios'][case][kind] for k in ('corrections','releases')),2)
    conditions={}
    for gain in ('current_gain','no_gain'):
        for label,keys in [('correctifs_releases',('corrections','releases')),('evolutions_separees',('evolutions',)),('tous_postes_core',('corrections','releases','evolutions'))]:
            conditions[label+'_'+gain]={kind:round(sum(transition[k]['scenarios'][gain][kind] for k in keys),2) for kind in ['annual_cost_eur','constant_34_month_eur','indexed_34_month_eur']}
    report['options'][slug]={'variants':variants,'core_transition':{'included_in_proposal':False,'start_month':start,'duration_months':duration,
        'inflation_pct':inflation*100,'indexed_factor':indexed_factor,'items':transition,'conditions':conditions},
        'proposal_delta_to_current_eur':round(variants['proposal_flow_central']['total_eur']-variants['current']['total_eur'],2),
        'programme_governance_eur':None,'total_programme_eur':None}
report['source_hashes']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(set(inputs))}


def reconcile_sap():
    from collections import defaultdict
    from decimal import Decimal, localcontext
    from fractions import Fraction
    from pathlib import Path
    import csv
    import hashlib
    import json
    
    SOURCE = ROOT / 'sources/client/delaware-septembre.pdf'
    TRANSCRIPTION = HERE / DEFINITION['sap']['transcription']
    DATA = json.loads(TRANSCRIPTION.read_text(encoding='utf-8'))
    assert DATA['source_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()==DEFINITION['sap']['sha256']
    BLOCKS = {
        'parametres_adaptations': 'Paramètres / adaptations (conception-réalisation métier résiduelle)',
        'flux_donnees': 'Flux / données (seule reprise isolable, interfaces non isolées)',
        'recette': 'Recette (hors recette affectée aux travaux transverses isolés)',
        'bascule_stabilisation': 'Bascule / stabilisation (hors travaux transverses isolés)',
        'gouvernance_coordination': 'Gouvernance / coordination',
        'socle_formation_transition': 'Socle / formation / transition (infrastructure isolée seulement)',
    }
    PHASE_BLOCK = {
        'prep': 'parametres_adaptations',
        'plan': 'parametres_adaptations',
        'inception': 'parametres_adaptations',
        'blueprint': 'parametres_adaptations',
        'realisation': 'parametres_adaptations',
        'sit': 'recette',
        'uat': 'recette',
        'final_prep': 'bascule_stabilisation',
        'go_live': 'bascule_stabilisation',
        'operate': 'bascule_stabilisation',
    }
    prices=read(ROOT/'source/chiffrage/chiffrage-sap.yaml')['integration']['prix_rfi']['postes_eur']
    PRICES={2:prices[1],3:prices[2]}
    
    
    def price(jh, lot):
        return Fraction(jh * PRICES[lot['lot']], lot['total_printed'])
    
    
    def number(value):
        with localcontext() as context:
            context.prec = 40
            return str(Decimal(value.numerator) / Decimal(value.denominator))
    
    
    def money(value):
        return {'numerator': value.numerator, 'denominator': value.denominator,
                'eur_analytique': number(value),
                'eur_arrondi_2_decimales': str(Decimal(number(value)).quantize(Decimal('0.01')))}
    
    
    lots, ledger = [], []
    for lot in DATA['lots']:
        amounts = dict.fromkeys(BLOCKS, 0)
        excluded_finance = 0
        for row in lot['rows']:
            if row['domain'] in (10, 11):
                excluded_finance += row['total_printed']
                continue
            name = row['name']
            if name.startswith(('Gouvernance', 'Coordination')):
                block = 'gouvernance_coordination'
            elif name.startswith(('Support Infrastructure', 'Formations', 'Copilote IA')):
                block = 'socle_formation_transition'
            elif name.startswith('Reprise des données'):
                block = 'flux_donnees'
            elif name == 'Tests':
                block = 'recette'
            else:
                assert row['domain'] is not None, name
                block = None
            if block:
                amounts[block] += row['total_printed']
                ledger.append(dict(lot=lot['lot'],pdf_page=lot['pdf_page'],row=name,
                                   selection='total_printed',block=block,jh=row['total_printed']))
            else:
                for phase, amount in row['phases'].items():
                    block_for_phase = PHASE_BLOCK[phase]
                    amounts[block_for_phase] += amount
                    ledger.append(dict(lot=lot['lot'],pdf_page=lot['pdf_page'],row=name,
                                       selection=phase,block=block_for_phase,jh=amount))
        target = lot['total_printed'] - excluded_finance
        difference = target - sum(amounts.values())
        lots.append(dict(lot=lot['lot'], pdf_page=lot['pdf_page'],
                         jh_total_printed=lot['total_printed'], jh_finance_excluded=excluded_finance,
                         jh_target_outside_finance=target, jh_six_blocks=sum(amounts.values()),
                         jh_document_reconciliation=difference,
                         price_lot_eur=PRICES[lot['lot']],price_ratio_eur_jh=money(price(1,lot)),
                         blocks={key:dict(jh=value,price_analytique=money(price(value,lot))) for key,value in amounts.items()},
                         reconciliation_price_analytique=money(price(difference,lot)),
                         target_price_analytique=money(price(target,lot))))
    
    identity=[(x['lot'],x['row'],x['selection']) for x in ledger]
    assert len(identity)==len(set(identity))
    for lot in lots:
        assert lot['jh_six_blocks']+lot['jh_document_reconciliation']==lot['jh_target_outside_finance']
        assert lot['jh_target_outside_finance']+lot['jh_finance_excluded']==lot['jh_total_printed']
        whole={x['row'] for x in ledger if x['lot']==lot['lot'] and x['selection']=='total_printed'}
        phased={x['row'] for x in ledger if x['lot']==lot['lot'] and x['selection']!='total_printed'}
        assert not whole.intersection(phased)
        summed_price=sum((Fraction(item['price_analytique']['numerator'],item['price_analytique']['denominator']) for item in lot['blocks'].values()),Fraction())
        difference_price=lot['reconciliation_price_analytique']
        target_price=lot['target_price_analytique']
        assert summed_price+Fraction(difference_price['numerator'],difference_price['denominator'])==Fraction(target_price['numerator'],target_price['denominator'])
    
    totals={key:dict(jh=sum(lot['blocks'][key]['jh'] for lot in lots),
                     price_analytique=money(sum((Fraction(lot['blocks'][key]['price_analytique']['numerator'],
                                                          lot['blocks'][key]['price_analytique']['denominator']) for lot in lots),Fraction())))
            for key in BLOCKS}
    domain_rows=[]
    for domain in sorted({row['domain'] for lot in DATA['lots'] for row in lot['rows'] if row['domain'] is not None}):
        matched={lot['lot']:next((row for row in lot['rows'] if row['domain']==domain),None) for lot in DATA['lots']}
        domain_rows.append(dict(domain_source=domain,name=next(row['name'] for row in matched.values() if row is not None),
                                excluded_finance=domain in (10,11),
                                lot_totals_printed={str(lot):(row['total_printed'] if row is not None else None) for lot,row in matched.items()},
                                total_printed=sum(row['total_printed'] for row in matched.values() if row is not None)))
    finance=sum(lot['jh_finance_excluded'] for lot in lots)
    target=sum(lot['jh_target_outside_finance'] for lot in lots)
    analytical_total=sum((Fraction(lot['target_price_analytique']['numerator'],lot['target_price_analytique']['denominator']) for lot in lots),Fraction())
    result=dict(
        status='audit_analytique_non_retenu_dans_reference',
        source=dict(path=SOURCE.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),pdf_pages=[38,39,40,41]),
        method=dict(priority='Exclure lignes Finance 10/11, isoler lignes transverses entières, puis découper uniquement les autres lignes métier par phases.',
                    row_totals='Les lignes isolées utilisent le total imprimé ; les lignes métier utilisent les cellules affichées. Les écarts restent dans une ligne documentaire distincte.',
                    phase_mapping=PHASE_BLOCK,
                    wricef='Les 2990 JH ne sont pas ajoutés. Les 1467 JH Input/Output ne sont pas retirés arbitrairement des phases ou de Finance : la correspondance manque.',
                    prices='Ventilation analytique au prix moyen de chaque lot, jamais prix commercial par bloc, devis FLOW, estimation de profil ni tarif individuel.'),
        labels=BLOCKS,lots=lots,totals=totals,
        document_reconciliation_jh=sum(lot['jh_document_reconciliation'] for lot in lots),
        document_reconciliation_price_analytique=money(sum((Fraction(lot['reconciliation_price_analytique']['numerator'],lot['reconciliation_price_analytique']['denominator']) for lot in lots),Fraction())),
        lots_2_3_outside_finance=dict(jh=target,price_analytique=money(analytical_total)),
        finance_excluded_jh=finance,
        domain_rows=domain_rows,
        domain_rows_outside_finance_total_printed=sum(row['total_printed'] for row in domain_rows if not row['excluded_finance']),
        upgrade_residual=dict(jh=421,price_source_eur=395000,scope='Lot 1 Finance/CCM mixte, non ventilé, conservé séparément sans suppression automatique.'),
        all_lots_outside_finance=dict(jh=target+421,price_analytique=money(analytical_total+395000)),
        ledger=ledger,
        checks=dict(unique_ledger_selections=True,no_whole_row_also_counted_by_phase=True,
                    conservation_after_explicit_document_reconciliation=True,exact_rational_price_conservation=True,active_files_modified=False),
    )
    # Publish additive cents by differences of rounded cumulative amounts. Keep
    # the exact fraction and isolated rounding for an explicit audit trail.
    def reconcile_published_cents(items, expected):
        cumulative=Fraction();previous=Decimal('0.00')
        for item in items:
            cumulative+=Fraction(item['numerator'],item['denominator'])
            rounded=Decimal(number(cumulative)).quantize(Decimal('0.01'))
            item['eur_arrondi_isole_2_decimales']=item['eur_arrondi_2_decimales']
            item['eur_arrondi_2_decimales']=str(rounded-previous)
            previous=rounded
        assert sum(Decimal(item['eur_arrondi_2_decimales']) for item in items)==Decimal(expected['eur_arrondi_2_decimales'])
    for lot in lots:
        reconcile_published_cents([b['price_analytique'] for b in lot['blocks'].values()]+[lot['reconciliation_price_analytique']],lot['target_price_analytique'])
    reconcile_published_cents([b['price_analytique'] for b in totals.values()]+[result['document_reconciliation_price_analytique']],result['lots_2_3_outside_finance']['price_analytique'])
    result['checks']['published_cents_conserved']=True
    result['method']['published_cents']='Differences of rounded cumulative exact amounts; isolated rounding retained for traceability.'
    assert finance==2810 and target==11409 and target+421==11830
    return result

sap_result=reconcile_sap()
investment_all=read(ROOT/'source/investissements-10-ans.yaml')
anchor=investment_all['sensibilite_finance_sap']
assert round(float(sap_result['all_lots_outside_finance']['price_analytique']['eur_analytique']),2)==anchor['base_delaware_apres_retrait_eur_ht']
reference=investment_all['bonus_continuite_make']['budget_apres_bonus_eur_ht']
assert reference==9889142.99
for slug,item in report['options'].items():
    central=item['variants']['proposal_flow_central']
    unit=central['labour_eur']/central['gross_total_jh']
    dep=DEFINITION['deploiements_conditionnels']
    item['deployment_diagnostics_not_added']={key:{'jh':value*dep['nombre_unites_hypothetique'],'cost_eur':round(value*dep['nombre_unites_hypothetique']*unit,2)} for key,value in dep['jh_par_unite'].items()}
    assert item['total_programme_eur'] is None
    assert central['gain_pct']==PROPOSAL['integration_ai_gain_pct']
    assert central['flux_gross_jh']==PROPOSAL['interfaces']*PROPOSAL['days_per_interface']['central']
    assert round(sum(block['cost_eur'] for block in central['blocks'].values()),2)==central['total_eur']
allcaps={c for row in paths['scenarios'] for c in row['capacites']}
report['map_checks']={'native_capabilities':len(bycap),'scenarios':len(paths['scenarios']),'linked_capabilities':len(allcaps),'not_in_scenarios':[{'id':c,'name':nodes[c]['fields']['name'],'path':bycap[c]['chemin']} for c in bycap if c not in allcaps], 'nature':'Partial proposed links, not quantities or cost allocation.'}
ACTIVE_AFTER=active_hashes()
assert ACTIVE_BEFORE==ACTIVE_AFTER,'Active files changed during audit'
baseline=ROOT/'tmp/audit-integration-make/rapprochement-active-before.json'
session_match=None
if baseline.exists():
    session_match=json.loads(baseline.read_text(encoding='utf-8'))==ACTIVE_AFTER
    assert session_match,'Active files changed during this reconciliation task'
result={'definition':DEFINITION,'make':report,'sap':sap_result,
    'reference':{'integration_make_eur':reference,'sap_proxy_without_continuity_eur':anchor['integration_sap_apres_retrait_eur_ht'],'changed':False},
    'controls':{'active_files_count':len(ACTIVE_AFTER),'active_before_after_equal':True,'active_session_equal':session_match,'active_manifest_sha256':hashlib.sha256(json.dumps(ACTIVE_AFTER,sort_keys=True).encode()).hexdigest(),'make_current_matches_saved':True,'all_13_activities_once':True,'native_map_ids_valid':True,'programme_complete_cost_null':True}}
result['audit_dependencies_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),HERE/'2026-10-27-integration-make-rapprochement.yaml',HERE/'2026-10-27-integration-make-rapprochement-sap.json']}
(HERE/'2026-10-27-integration-make-rapprochement-preuves.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'proposed_eur':{s:i['variants']['proposal_flow_central']['total_eur'] for s,i in report['options'].items()},'reference':result['reference'],'controls':result['controls']},ensure_ascii=False,indent=2))
