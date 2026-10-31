"""Readable result and audit closure of iteration 4, without changing active decisions."""
from pathlib import Path
from html import escape as e
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r=read(OUT/'results.json');m=read(OUT/'measurements.json');fund=read(OUT/'funding.json');v=read(OUT/'verification.json')
names={'orders':'Commandes — cycle et filiation','goods-orders':'Prestations — contrat commun','assurance':'Prestations — résultats reconnus',
 'workflow':'Processus — définitions et adaptateurs','human-work':'Travail humain — contexte et échéances','supervision':'Supervision — journal et interventions',
 'transport-orders':'Transport','customs':'Douane','financial-services':'Finance','coordination':'Coordination métier'}
raw={p:sum(next(row['jh'] for row in owner['rows'] if row['id']==p) for owner in r['owners'].values()) for p in r['common_native_subtotals']}
spread=max(raw.values())-min(raw.values())
closing=dict(id='iteration-04-closure',status='common_mechanisms_clarified_proposal',
 progress=r['progress'],cumulative=r['cumulative'],common_java_jh=280,
 four_native_common_totals=r['common_native_subtotals'],raw_native_common_totals=raw,
 numeric_dispersion=dict(jh=spread,pct_of_unrounded_java=100*spread/raw['axelor'],denominator=raw['axelor'],not_confidence=True,
  note='Sommes des six unités économiques disjointes, pas estimation COCOMO intégrée du Core. Hypothèses de nouveaux volumes partagées.'),
 audit_items=[
 dict(id='A02',status='closed_for_common_scope',result='Onze mécanismes ont un propriétaire unique et leurs consommateurs. Les fonctions propres aux familles restent distinctes et inconnues.'),
 dict(id='A03',status='closed_for_measured_scope',result='Même compteur d’instructions/déclarations que les mesures adoptées ; sélection métier, contexte et sources réutilisées distincts. Quarante-six fichiers contrôlés, sans passage automatique à un compteur de méthodes.'),
 dict(id='A01',status='improved_not_closed',result='Huit vraies sources BPM Java ajoutées, contre un simple cycle d’achat auparavant. La portée Camunda/Axelor et sa transposition vers Flowable restent partielles.'),
 dict(id='A04',status='open_for_specific_work',result='Composition réactive avancée, journal de Case temporel, contrats typés, booking et dossiers spécifiques restent à compléter hors du sous-total commun.'),
 dict(id='A05',status='recounted_for_common_components',result='Six comptages proposés à frontières explicites. Pas de somme des CFP des composants, ni calibration du rendement historique.'),
 dict(id='A06',status='open',result='Rôles et délais conservés comme diagnostics nominaux ; pas d’équipe ni de calendrier de programme validés.'),
 dict(id='A07',status='outside_current_iteration',result='L’alignement du catalogue OR-Tools et les adaptations de solveurs relèvent de la suite de la planification/optimisation.')
 ],
 what_progressed=['Financement unique explicite du périmètre partagé.',
 'Suppression de la reconstruction supposée de noyaux déjà fournis ; calcul initial conservé, correction Java de 290 à 280 JH.',
 'Référence BPM Java observée dans Axelor Studio, incluant instances et tâches ; moteur Camunda identifié sans le présenter comme Flowable.',
 'Calcul des six lots communs, des quatre références natives et de leurs contrôles fonctionnels.'],
 residual_uncertainty=['Fractions de nouveau code et déclarations supplémentaires restent des hypothèses, pas des charges observées.',
 'Proximité des totaux natifs non indépendante : patrons et compléments partagés.',
 'Le registre de Case utilise une analogie de forme technique ; pas d’équivalent natif complet démontré.',
 'Les compléments locaux des dix familles et les autres familles ne sont pas chiffrés par cette itération.'],
 measurement_vs_confidence='La cohérence du financement et de la mesure progresse. Aucune diminution probabiliste de l’incertitude de charge n’est démontrée.',
 additional_common_reconstruction_for_consumers_jh=0,specific_work_for_consumers_jh=None,
 adoption_note='Une adoption éventuelle du seul financement commun ne devra pas marquer 42 capacités comme entièrement estimées. Conserver séparément le financement partiel et la couverture complète.',
 next_iteration_worthwhile=True,
 next_iteration='Chiffrer les compléments typés commandes/prestations après consommation des onze mécanismes, puis tester les adaptations communes Flowable et les garanties de journal de Case qui peuvent encore changer le résultat.',
 active_model_changed=False,no_new_adoption=True)
save('audit-closure.json',closing)
import sys
sys.path.insert(0,str(ROOT/'tmp/model-deps'))
import yaml
(OUT/'bilan.yaml').write_text(yaml.safe_dump(dict(summary=closing,owners=r['owners'],funding=fund,family_remainders=r['families']),allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
def number(x,dec=0):return (f'{x:,.{dec}f}'.replace(',',' ').replace('.',',')) if x is not None else 'Inconnu'
def table(headers,rows):
 return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+e(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(c)+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'
html=['<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FLOW — mécanismes partagés, itération 4</title>',
'<style>body{margin:0;background:#f6f7f5;color:#163b3a;font:16px/1.6 system-ui,sans-serif}main{max-width:1180px;margin:auto;padding:30px}h1,h2,h3{line-height:1.25}section{background:white;border:1px solid #d8e2df;border-radius:8px;padding:24px;margin:22px 0}.notice{border-left:6px solid #d36a25;background:#fff6eb;padding:18px}.metrics{display:flex;flex-wrap:wrap;gap:28px}.metrics strong{display:block;font-size:26px}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:10px;border-bottom:1px solid #d8e2df;text-align:left;vertical-align:top}th{background:#e7f0ed}a{color:#176159}li{margin:7px 0}@media(max-width:600px){main{padding:14px}section{padding:14px}}</style><main>',
'<h1>Mécanismes partagés — quatrième itération</h1><p>Commandes, prestations et processus · Java/Spring · 30 octobre 2026</p>',
'<div class="notice"><strong>280 JH proposés pour la seule part commune.</strong> Ce n’est ni le coût complet des dix familles ni celui du Core System. Le modèle actif conserve les 1 940 JH adoptés.</div>',
'<section class="metrics"><div><strong>11</strong>mécanismes à propriétaire unique</div><div><strong>6</strong>propriétaires proposés</div><div><strong>10</strong>familles concernées</div><div><strong>42 / 88</strong>capacités touchées par cette itération</div></section>',
'<section><h2>Ce qui est à financer une seule fois</h2>']
rows=[]
for owner,x in r['owners'].items():
 mechs=[v['name'] for v in fund['mechanisms'] if v['owner']==owner]
 rows.append([e(names[owner]),e(' ; '.join(mechs)),number(x['java_common_jh'])+' JH'])
html.append(table(['Propriétaire proposé','Travail commun financé ici','JH Java/Spring'],rows))
html.append('<p><strong>Total commun proposé : 280 JH.</strong> Les consommateurs n’ajoutent aucun coût de reconstruction de ces mécanismes. Leurs compléments propres restent à estimer ; ils ne valent pas zéro.</p></section>')
html.append('<section><h2>Les quatre références natives</h2><p>Sommes arrondies des six lots communs, sur des sources et adaptations explicites. Ces résultats sont conditionnels et ne sont pas des coûts OSS réellement consommés.</p>')
html.append(table(['Référence','Part commune'],[[n,number(r['common_native_subtotals'][p])+' JH'] for p,n in [('erpnext','ERPNext + Frappe'),('odoo','Odoo'),('tryton','Tryton'),('axelor','Axelor + Open Platform / Studio')]]))
html.append('<p>Les patrons de nouveaux modules et les hypothèses sont partagés ; une proximité numérique n’est pas une validation indépendante ni un score de confiance.</p></section>')
html.append('<section><h2>Comment la réutilisation est traitée</h2><ul><li>Master Data, Stock et Propriété du stock gardent leurs financements adoptés.</li><li>Les moteurs et minuteurs fournis sont réutilisés ; la nouvelle application ne finance pas leur reconstruction.</li><li>Les adaptations, contrôles métier, contrats et preuves propres à Flow restent financés dans les lots communs.</li><li>Un même code source peut servir d’analogue à plusieurs comportements nouveaux distincts. Il ne devient pas automatiquement un second financement du code natif.</li></ul><p>Le calcul initial de 290 JH est conservé. La revue a retiré des bases supposées reconstruire les noyaux fournis, sans changer les fractions de nouveau code pour obtenir une convergence. Le total Java corrigé est 280 JH.</p></section>')
html.append('<section><h2>Mesure harmonisée</h2><p>Le compteur syntaxique est le même que celui des mesures adoptées : instructions, classes, imports, champs et déclarations. Les atomes sélectionnés pour le domaine, leur contexte et les atomes hors périmètre sont séparés. Chaque atome de base possède un propriétaire unique.</p><p>46 fichiers ont été vérifiés aux révisions figées, dont huit sources BPM Axelor Studio. Cette référence appelle <strong>Camunda</strong>. L’adaptation aux API <strong>Flowable</strong> prévues pour Flow reste une hypothèse, avec les limites associées.</p><p><a href="harmonization.json">Comparaisons avec la mesure précédente</a> · <a href="measurements.json">Mesures et sélection de code</a></p></section>')
html.append('<section><h2>Contrôles fonctionnels par composant commun</h2><p>Frontière propre à chaque propriétaire ; les interfaces entre composants empêchent une simple somme des CFP à l’échelle du Core.</p>')
html.append(table(['Composant commun','CFP proposés','COCOMO Java non arrondi','COSMIC × ISBSG','Écart vs COCOMO non arrondi'],[[e(names[k]),number(x['functional']['CFP']),number(x['java_raw_jh'],2)+' JH',number(x['functional']['jh'],2)+' JH',number(x['functional']['alignment_vs_java']['gap_pct'],1)+' %'] for k,x in r['owners'].items()]))
html.append('<p>Le contrôle utilise toujours 20 h/CFP, facteur 1 et 7 h/JH. Ce rendement historique n’est pas calibré sur la réutilisation de ces composants.</p></section>')
html.append('<section><h2>Ce qui reste propre aux familles</h2>')
html.append(table(['Famille','Construction commune facturée ici','Complément propre, non chiffré ici'],[[e(names[f['family']]),number(f['common_funding_jh'])+' JH',e(f['specific_family_scope'])] for f in r['families']]))
html.append('<p>Pour Transport, Douane, Finance et Coordination, zéro JH de reconstruction commune signifie consommation d’un financement proposé ailleurs. Leur coût complet reste inconnu.</p></section>')
html.append('<section><h2>Avancement et cumul</h2><ul><li>88/88 capacités examinées lors de la campagne précédente.</li><li>Cette quatrième itération clarifie le périmètre commun de dix familles touchant 42 capacités.</li><li>16/88 capacités avec une estimation complète adoptée : 18,2 %, inchangé.</li><li>Cumul adopté : <strong>1 940 JH</strong>.</li><li>Avec la seule proposition commune : <strong>2 220 JH</strong>, soit 1 940 + 280. Ce sous-total ne comprend pas les compléments locaux ni toutes les autres familles.</li></ul><p>Financer une partie commune ne devra pas faire passer automatiquement 42 capacités en couverture complète.</p></section>')
html.append('<section><h2>Audit de cette itération et suite utile</h2><ul>'+''.join('<li><strong>'+e(a['id']+' — '+a['status'])+'</strong> : '+e(a['result'])+'</li>' for a in closing['audit_items'])+'</ul><p><strong>Une autre itération ciblée vaut le coup :</strong> '+e(closing['next_iteration'])+'</p><p>La cohérence du financement et de la mesure progresse. Aucune diminution probabiliste de l’incertitude de charge n’est démontrée.</p></section>')
for owner,x in r['owners'].items():
 html.append('<section><h2>'+e(names[owner])+' — détail du lot commun</h2>'+table(['Rôle','JH proposés'],[[e(v['label']),number(v['jh'])] for v in x['roles']]))
 html.append('<p>'+e(x['role_status'])+' Délai nominal calculé : '+number(x['raw_months'],2)+' mois, sans calendrier de programme ni addition des délais.</p><ul>')
 for mech in fund['mechanisms']:
  if mech['owner']==owner:html.append('<li><strong>'+e(mech['name'])+'</strong> : '+e(mech['basis'])+'</li>')
 html.append('</ul></section>')
html.append('<section><h2>Pièces</h2><p><a href="funding.json">Propriétaires et consommateurs</a> · <a href="results.json">Calculs détaillés</a> · <a href="audit-closure.json">Audit de clôture</a> · <a href="verification.json">Contrôles indépendants</a> · <a href="bilan.yaml">Bilan structuré</a></p></section></main></html>')
(OUT/'synthese.html').write_text('\n'.join(html),encoding='utf-8')
save('provenance.json',dict(files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name!='provenance.json'},
 protected_sources=read(OUT/'baseline.json')['protected'],native_sources={v['root_path']:v['sha256'] for v in m['sources']}))
print(json.dumps(dict(common_jh=280,adopted_jh=1940,adopted_plus_proposed_common_only_jh=2220,unique_mechanisms=11,families=10,capabilities_touched=42,active_model_changed=False),ensure_ascii=False))
