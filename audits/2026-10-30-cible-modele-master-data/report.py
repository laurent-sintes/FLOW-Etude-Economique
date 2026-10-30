from pathlib import Path
import json,html,hashlib
OUT=Path('audits/2026-10-30-cible-modele-master-data')
d=json.loads((OUT/'cible.json').read_text(encoding='utf-8'));facts=json.loads((OUT/'constats.json').read_text(encoding='utf-8'))
previous=json.loads(Path('audits/2026-10-30-master-data-spring-reprise/results.json').read_text(encoding='utf-8'))
anchor=next(r for r in previous['rows'] if r['id']=='axelor')['total_jh']
rows=[]
for r in previous['rows']:
 rows.append(dict(id=r['id'],label=r['label'],common_jh=r['common_jh'],complements_jh=r['flow_complements_jh'],jh=r['total_jh'],
 delta_jh=r['total_jh']-anchor,delta_pct=100*(r['total_jh']-anchor)/anchor))
functional=facts['numbers']['crosscheck_jh']
alignment=dict(reference_id='axelor',reference_jh=anchor,unit='JH projet',scope='Master Data Flow BC-002 à BC-007, périmètre commun et compléments Flow, réutilisation comprise',
 rows=rows,spread_jh=max(r['jh'] for r in rows)-min(r['jh'] for r in rows),
 spread_pct=100*(max(r['jh'] for r in rows)-min(r['jh'] for r in rows))/anchor,
 crosscheck=dict(jh=functional,delta_jh=functional-anchor,delta_pct=100*(functional-anchor)/anchor),
 adoption=dict(jh=1500,rounding_delta_jh=1500-anchor),confidence=None,
 interpretation='Écarts arithmétiques entre estimations ; aucune probabilité, aucun intervalle de risque ni score de confiance.',
 shared_hypothesis_share_axelor_pct=100*rows[-1]['complements_jh']/anchor)
(OUT/'alignement.json').write_text(json.dumps(alignment,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
(OUT/'cible.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
def e(x):return html.escape(str(x))
def n(x,digits=0):return f'{x:,.{digits}f}'.replace(',',' ').replace('.',',')
def ul(xs):return '<ul>'+''.join('<li>'+e(x)+'</li>' for x in xs)+'</ul>'
def p(x):return '<p>'+e(x)+'</p>'
def table(headers,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+e(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(v)+'</td>' for v in r)+'</tr>' for r in rows)+'</tbody></table></div>'
body=['<header><p class="eyebrow">FLOW · Audit du 30 octobre 2026</p><h1>Un modèle centré sur les estimations retenues</h1><p>Cartographie source fidèle · Comparaisons calculées · Adoption distincte · Alignement sans interprétation de confiance</p></header>']
body.append('<aside><strong>Conclusion : la base Master Data peut être conservée ; son environnement doit être simplifié.</strong><p>1 500 JH, neuf rôles et 17 mois restent retenus pour Java/Spring. Cet audit ne change ni le modèle actif ni ses écrans ou son skill. Il prépare une migration à économie constante.</p></aside>')
body.append('<nav><a href="#entree">Entrants</a><a href="#alignement">Alignement</a><a href="#incertitude">Incertitude</a><a href="#constats">Constats</a><a href="#cible">Cible et migration</a><a href="#preuves">Contrôles et références</a></nav>')
body.append('<section id="entree"><h2>Le référentiel des capacités reste un entrant</h2>'+p(d['target']['input_contract']['rule']))
body.append(table(['À reprendre fidèlement','À placer dans l’analyse'],[
('Identifiants, libellés, hiérarchie, définitions, périmètres et relations','Sélection pour l’étude, familles de chiffrage, fonctions interprétées, comparaisons OSS'),
('Version, date, empreinte, statut et liens d’origine','Hypothèses FLOW, garanties retenues, JH, rôles, coûts et délai')]))
body.append(p(d['target']['input_contract']['missing_data']))
body.append('<p>Constat quantifié : <strong>88 capacités, 258 fonctions proposées et 264 notes sur 5</strong> cohabitent dans la grille actuelle. Les fonctions proposées et les notes ne doivent pas être présentées comme des données natives. Les appréciations éventuellement reçues dans les sources restent conservées comme telles, sans devenir des multiplicateurs d’effort.</p></section>')
body.append('<section id="alignement"><h2>Un indicateur d’alignement, sans score de confiance</h2><p>La mesure porte sur des résultats comparables avant arrondi. La référence explicite est le calcul COCOMO II fondé sur Axelor : <strong>'+n(anchor,2)+' JH</strong>. Les 1 500 JH sont la décision arrondie, distincte du calcul.</p>')
body.append('<div class="formula">Écart = résultat − référence<br>Écart relatif = 100 × (résultat − référence) / référence</div>')
body.append(table(['Référence du calcul COCOMO','Commun · JH','Compléments · JH','Total · JH','Écart à Axelor · JH','Écart relatif'],[
(r['label'],n(r['common_jh']),n(r['complements_jh']),n(r['jh']),n(r['delta_jh'],1),n(r['delta_pct'],1)+' %') for r in rows]))
body.append('<p>Étendue entre les quatre calculs : <strong>'+n(alignment['spread_jh'],1)+' JH</strong>, soit <strong>'+n(alignment['spread_pct'],1)+' %</strong> de la référence Axelor. Il s’agit d’une dispersion des résultats, pas d’une fourchette d’incertitude.</p>')
body.append(table(['Voie','JH avant arrondi de décision','Écart à la référence COCOMO'],[
('COCOMO II · Axelor',n(anchor,2),'Référence'),
('COSMIC × ISBSG',n(functional),n(functional-anchor,2)+' JH · '+n(alignment['crosscheck']['delta_pct'],1)+' %')]))
body.append('<p>Le passage au chiffre retenu ajoute seulement '+n(1500-anchor,2)+' JH d’arrondi. Il ne doit pas intervenir dans la mesure d’alignement.</p>')
body.append('<p>Les quatre lignes sont des estimations du périmètre Flow à partir des OSS, pas leurs coûts historiques constatés. Les compléments représentent environ '+n(alignment['shared_hypothesis_share_axelor_pct'],1)+' % du total Axelor et reposent largement sur les mêmes hypothèses. Une faible dispersion ne fournit donc pas quatre validations indépendantes.</p>')
body.append('<h3>Conditions de calcul</h3>'+ul(d['target']['alignment_contract']['comparability'])+p(d['target']['alignment_contract']['if_not_comparable']))
body.append('<p>Afficher séparément les écarts entre OSS et entre voies de calcul. Conserver le périmètre commun et les compléments séparés. Pour les rôles et les délais, n’afficher un alignement que s’il existe réellement plusieurs calculs comparables. Aucun seuil de couleur, classement A–E ou pourcentage de confiance n’est proposé.</p></section>')
body.append('<section id="incertitude"><h2>L’incertitude reste une information distincte</h2><p>La grille historique retrouvée définit A à D comme une convention locale de solidité des preuves, et non comme une mesure probabiliste. Elle n’est pas appliquée à Master Data dans le modèle retenu. Recommandation : la retirer du dispositif courant, en conservant son historique.</p>')
body.append(table(['Information','Traitement cible'],[
('Alignement','Écarts calculés en JH et en %, avec référence et assiette.'),
('Qualité des données reçues','Conserver la qualification et sa source, notamment les classes ISBSG A–D.'),
('Hypothèses de taille, réutilisation et garanties','Conserver les valeurs supposées, leurs justifications et leurs effets connus.'),
('Incertitude de sortie','La qualifier seulement si une méthode et des données la justifient ; sinon inconnue.'),
('Décision','Retenue ou à réestimer ; distincte d’une validation empirique.')]))
body.append('<p>COCOMO fournit un effort conditionnel à ses entrées et à ses coefficients. Son manuel recommande une calibration locale ; il ne fournit pas un intervalle garanti pour Flow. Une dispersion ISBSG décrit la cohorte sélectionnée, et COSMIC peut documenter l’incertitude d’une taille approximative. Ces éléments peuvent nourrir une analyse d’incertitude, sans transférer automatiquement une borne au projet.</p>')
body.append('<p>À ce stade : <strong>aucun P50/P80, aucun ±X % de risque et aucune réserve automatique</strong>. Une variation d’hypothèse peut produire une sensibilité chiffrée ; elle n’est pas une probabilité. L’absence de bilans de projets n’empêche pas de poursuivre l’étude d’opportunité.</p></section>')
body.append('<section id="constats"><h2>Dix constats à traiter</h2>')
for f in d['findings']:
 body.append('<article><p class="eyebrow">'+e(f['id']+' · Priorité '+f['priority'])+'</p><h3>'+e(f['title'])+'</h3>'+p(f['fact'])+'<p><strong>Cible.</strong> '+e(f['target'])+'</p><p><strong>Action.</strong> '+e(f['action'])+'</p><p class="refs">'+e('Références : '+' · '.join(f['evidence']))+'</p></article>')
body.append('</section><section id="cible"><h2>Une chaîne unique, de l’entrant au budget</h2><div class="flow">Source reçue → Référentiel fidèle → Périmètre d’analyse → Références et calculs → Alignement → Décision retenue → Rôles, coûts et calendrier</div>')
body.append('<h3>Le skill cible</h3>'+ul(d['target']['skill_target']))
body.append('<h3>Migration en cinq lots</h3>'+table(['Ordre','Travail','Critère de fin'],[(x['order'],x['work'],x['done_when']) for x in d['target']['migration']]))
body.append('<h3>Garde-fous de la cible</h3>'+ul(d['target']['acceptance'])+'</section>')
body.append('<section id="preuves"><h2>Contrôles réalisés et références</h2><p>Lecture des sources, contrats, moteur, composants d’écran, skill et audits de calcul. Chargement du modèle courant, inventaire des financements et essais de validation sur des copies en mémoire. Les sondes ne modifient aucune estimation. Les sources actives, le code et le skill sont contrôlés par empreinte avant et après cet audit.</p><p>Le journal contient un financement Master Data de 944 000 €, mais encore 267 anciennes affectations Make à zéro. La source déclarée du financement construction reste historique. Les 17 mois ne remplacent pas les 48 mois provisoires des annuités ; cette distinction est conservée.</p>')
body.append('<ul><li><a href="https://www.rose-hulman.edu/class/cs/csse372/201310/Homework/CII_modelman2000.pdf">COCOMO II — manuel USC, version 2.1</a>, §1.2 et §7 : coefficients, calibration locale et distributions d’activité.</li><li><a href="https://isbsg.org/wp-content/uploads/2017/05/e.-ISBSG-Release-2017-R1-Field-Descriptions.pdf">ISBSG — description des champs</a>, p.1 : A–D qualifie les données reçues et la mesure de taille ; ce n’est pas un niveau de confiance de l’estimation Flow.</li><li><a href="https://cosmic-sizing.org/wp-content/uploads/2020/02/Early-Sizing-Practitioners-Guide-May-2020-1.pdf">COSMIC — Early Software Sizing, Practitioners Guide</a>, §10 : documenter l’incertitude d’une taille approximative. Références consultées le 30 octobre 2026.</li></ul><p>Pièces de cet audit : constats.json (inventaire et empreintes), cible.json (constats et contrats proposés), alignement.json (calculs non arrondis), verification.json (absence de modifications actives).</p></section>')
css='body{font:16px/1.65 system-ui,sans-serif;color:#153d39;background:#faf8f4;margin:0}main{max-width:1060px;margin:auto;padding:36px 24px}header{border-bottom:4px solid #236159;padding:20px 0}h1{font-size:36px;line-height:1.2}h2{font-size:25px;margin-top:38px}h3{font-size:19px}.eyebrow{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:#526c66}aside,.formula,.flow{background:#d9f2ea;border-left:4px solid #236159;padding:18px 22px;margin:24px 0}nav{display:flex;flex-wrap:wrap;gap:18px}a{color:#236159}article{padding:20px 0;border-bottom:1px solid #d1ded8}article h3{margin:0}.refs{font-size:12px;overflow-wrap:anywhere;color:#526c66}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;background:white;font-size:14px}th,td{padding:12px;text-align:left;border-bottom:1px solid #d1ded8;vertical-align:top}th{background:#eaf3ef}li+li{margin-top:8px}section{scroll-margin:20px}.flow{font-weight:600}@media(max-width:600px){main{padding:16px}h1{font-size:28px}table{min-width:630px}}@media print{nav{display:none}main{max-width:none}h2,h3{break-after:avoid}article,tr{break-inside:avoid}}'
(OUT/'audit.html').write_text('<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FLOW — Audit de la cible du modèle</title><style>'+css+'</style><main>'+''.join(body)+'</main></html>',encoding='utf-8',newline='\n')
changed=[path for path,digest in facts['hashes'].items() if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=digest]
skill=Path('C:/Users/laure/.codex/skills/flow-evaluer-core-system/SKILL.md')
assert not changed,changed
assert hashlib.sha256(skill.read_bytes()).hexdigest()==facts['skill_sha256']
assert abs(sum(r['jh'] for r in rows)/len(rows))>0
verification=dict(status='passed',active_files_checked=len(facts['hashes']),active_files_changed=changed,skill_unchanged=True,classes_origin='Local A-D in iteration-04; no active ABCDE model found',
 adoption_unchanged=dict(jh=1500,months=17),calculation_reference_jh=anchor,scope='Read-only audit and proposed target; only new audit artifacts written')
(OUT/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
print(json.dumps(verification,ensure_ascii=True))
