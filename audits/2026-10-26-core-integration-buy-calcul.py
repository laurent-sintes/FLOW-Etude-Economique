"""Read-only economic audit; isolated scenarios, never writes active model files."""
from pathlib import Path
from copy import deepcopy
import collections, csv, hashlib, json
import yaml
import calculate_costs as cc
import project_investment as pi

root=Path.cwd()
out=root/'audits'; out.mkdir(exist_ok=True)
stem='2026-10-26-core-integration-buy'
def load(p): return yaml.safe_load(Path(p).read_text(encoding='utf-8'))
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
paths=[p for directory in ['source','sources','config','app/src','tools'] for p in (root/directory).rglob('*') if p.is_file() and p.suffix in ('.yaml','.md','.py','.tsx','.ts')]
before={str(p.relative_to(root)).replace('\\','/'):digest(p) for p in paths}
cal,docs=cc.validate_inputs()
economic=cc.calculate()
print('Reference economic model recalculated',flush=True)
assert load(root/'source/couts-15-ans.yaml')==economic, 'Saved economic output differs from recalculation'
original_calculate=pi.calculate
original_active_doc=pi.active_doc
pi.calculate=lambda:deepcopy(economic)
baseline=pi.prepare()
base_projection=pi.project(baseline)
print('Reference projection recalculated',flush=True)
assert base_projection==load(root/'source/investissements-10-ans.yaml'), 'Saved sponsor projection differs'
business=load(root/'source/recalibration-metier.yaml')
grid=load(root/'source/grille-complexite.yaml')
capture=load(root/'sources/cartographie-scm-2026-10-24.yaml')
nodes={n['id']:n for n in capture['nodes']}
rows=[]
for b in [*business['blocs'],business['transverse']]:
    bid=b.get('bloc',b.get('id'))
    g=next((x for x in grid['blocs'] if x['id']==bid),None)
    node=nodes.get(b.get('capacite'),{})
    for slug in ['microsoft','sap']:
        a=b['stacks'][slug]; lot=business['lots'][a['travaux_ref']]
        e=next(x for x in economic['options'] if x['stack']==slug)
        f=next(x for x in e['features'] if x['feature']==bid)
        rows.append(dict(stack=slug,bloc=bid,capacite=b.get('capacite'),nom=node.get('fields',{}).get('name',bid),
          chemin=g['chemin'] if g else [],fonctions=g['fonctions'] if g else [],
          traitement=a['traitement'],lot=a['travaux_ref'],couverture=business['couvertures'][a['couverture_ref']],
          travail=lot['travail'],jh_bruts=sum(lot['central']),cout_eur_ht=f['cout_eur_ht']))
def horizons(projection):
    return {o['stack']:{str(h):round(sum(a['total'] for a in o['annees'][:h]),2) for h in (3,5,7,10)} for o in projection['options']}
scenarios={}
for key,remove_maintenance in [('sans_provisions_fonctionnelles',False),('sans_provisions_et_entretien_associe',True)]:
    changed=deepcopy(docs)
    for slug in ['microsoft','sap']:
        # Sensitivity only: keep treatment and references; set conditional work to zero.
        for f in changed[slug]['core']:
            if f['traitement']!='complement_integration': continue
            f['jh_backend_avant_ia']={k:0 for k in f['jh_backend_avant_ia']}
            f['jh_frontend_avant_ia']=0
            f['plages_jh']={case:{k:0 for k in values} for case,values in f['plages_jh'].items()}
        if remove_maintenance: changed[slug]['maintenance']['maintenance_complements_buy_jh_annuels']=0
    revised=deepcopy(economic)
    revised['options']=[cc.calculate_option(slug,doc,cal) for slug,doc in changed.items()]
    pi.calculate=lambda:deepcopy(revised)
    pi.active_doc=lambda slug:deepcopy(changed[slug])
    prepared=pi.prepare()
    projected=pi.project(prepared)
    for old,new in zip(economic['options'],revised['options']):
        assert old['stack']==new['stack']
        assert old['synthese_eur_ht']['build_core']==new['synthese_eur_ht']['build_core']
        assert old['detail_integration']['base_rfi']==new['detail_integration']['base_rfi']
        for field in ['preparation','support_microsoft_premiere_annee','reserve_ecart_sap']:
            assert old['detail_integration'][field]==new['detail_integration'][field]
    assert prepared['bonus_continuite_make']==baseline['bonus_continuite_make']
    hs=horizons(projected); hb=horizons(base_projection)
    scenarios[key]=dict(nature='Sensibilité isolée, ne constitue pas une nouvelle estimation retenue',
      horizons_eur_ht=hs,ecarts_a_la_reference_eur_ht={s:{h:round(hs[s][h]-hb[s][h],2) for h in hs[s]} for s in hs},
      ancre=prepared['sensibilite_finance_sap'],bonus=prepared['bonus_continuite_make'],
      economies={o['stack']:o['synthese_eur_ht'] for o in revised['options']},
      projection=projected['options'])
    print('Isolated scenario checked: '+key,flush=True)
pi.calculate=original_calculate
pi.active_doc=original_active_doc
summary={}
for slug in ['microsoft','sap']:
    rs=[r for r in rows if r['stack']==slug]
    supplements=sum(r['cout_eur_ht'] for r in rs if r['traitement']=='complement_integration')
    old=next(o for o in economic['options'] if o['stack']==slug)['synthese_eur_ht']
    alt=scenarios['sans_provisions_et_entretien_associe']['economies'][slug]
    summary[slug]=dict(lignes_par_traitement=dict(collections.Counter(r['traitement'] for r in rs)),
       capacites_avec_complements=sum(r['traitement']=='complement_integration' and r['bloc']!='TRANSVERSE' for r in rs),
       jh_diagnostiques_inclus=sum(r['jh_bruts'] for r in rs if r['traitement']=='inclus_rfi'),
       jh_bruts_complements=sum(r['jh_bruts'] for r in rs if r['traitement']=='complement_integration'),
       complements_eur_ht=round(supplements,2),
       complements_avec_pilotage_eur_ht=round(supplements*(1+cal['pilotage']['complements_buy_pct']/100),2),
       entretien_jh_annuels=business['maintenance']['par_stack'][slug]['entretien_complements_buy_jh'],
       entretien_avec_pilotage_annuel_eur_ht=round(old['maintenance_premiere_annee']-alt['maintenance_premiere_annee'],2))
external=Path('C:/Dev/Beaumanoir Cartographie/modeles/backlog/model.yaml')
ext=load(external)
after={str(p.relative_to(root)).replace('\\','/'):digest(p) for p in paths}
assert before==after, 'Active inputs unexpectedly changed'
proof=dict(date='2026-10-26',nature='Audit en lecture seule et sensibilités non actives',
  empreintes=before,cartographie_courante=dict(fichier=str(external),sha256=digest(external),
  sha256_capture=capture['provenance']['sha256'],identique_a_la_capture=digest(external)==capture['provenance']['sha256']),
  controles=dict(calcul_reference_identique=True,projection_reference_identique=True,aucun_fichier_actif_modifie=True,
  prix_fournisseurs_preserves=True,build_make_et_ancre_make_inchanges=True),
  synthese=summary,reference_horizons_eur_ht=horizons(base_projection),sensibilites=scenarios,inventaire=rows)
(out/(stem+'-preuves.json')).write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
with (out/(stem+'-inventaire.csv')).open('w',encoding='utf-8-sig',newline='') as f:
    fields=['stack','bloc','capacite','nom','traitement','lot','jh_bruts','cout_eur_ht','travail']
    writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',delimiter=';');writer.writeheader();writer.writerows(rows)
print(json.dumps(dict(synthese=summary,reference=horizons(base_projection),
  sensibilites={k:v['ecarts_a_la_reference_eur_ht'] for k,v in scenarios.items()},cartographie=proof['cartographie_courante']),ensure_ascii=False,indent=2))
print('EXCEPTIONS_MOTEURS_PARCOURS',json.dumps([{k:r[k] for k in ('stack','bloc','nom','lot')} for r in rows if r['lot'] in ('buy_moteur','buy_parcours')],ensure_ascii=False))
print('EXTERNAL_SCENARIOS_KEYS',list(ext['scenario_catalog']))
print('EXTERNAL_SAMPLE_NODE',json.dumps(next((n for n in ext['nodes'] if n.get('kind')=='behavior'),{}),ensure_ascii=False)[:1800])
