"""Independent reconciliation and readable audit reports; no active model changes."""
from pathlib import Path
import json,hashlib,sys,html,ast
ROOT=Path(__file__).resolve().parents[2]
A=Path(__file__).resolve().parent
OLD=ROOT/'audits/2026-10-29-experimentation-estimation'
sys.path.insert(0,str(ROOT/'tmp/model-deps'))
import yaml
sys.stdout.reconfigure(encoding='utf-8')
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
esc=lambda s:html.escape(str(s))
def fmt(v):
 return f'{v:,.1f}'.replace(',',' ').replace('.',',').removesuffix(',0')
def write(name,data):
 (A/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
checks=[]
def check(ok,msg):
 if not ok:raise AssertionError(msg)
 checks.append(msg)
its=list(range(9,15))+list(range(16,21))
data={i:load((OLD if i<15 else A)/f'iteration-{i:02}-resultats.json') for i in its}
final=data[20]; roles=final['roles']
baseline=load(A/'baseline.json')
for p,h in baseline['active_files'].items():check(sha(ROOT/p)==h,'Unchanged active file: '+p)
v15=OLD/'iteration-15-verification.json'
check(sha(v15)==baseline['previous15_verification_sha256'],'Historical verification15 unchanged')
for p,h in load(v15)['artifacts_sha256'].items():check(sha(OLD/p)==h,'Historical15 artifact unchanged: '+p)
grid=yaml.safe_load((ROOT/'source/grille-complexite.yaml').read_text(encoding='utf-8'))['blocs']
universe=load(OLD/'iteration-07-resultats.json')['coverage']
native={c['block']:c for c in universe}
gridmap={g['id']:g for g in grid}
allpk=[]; allcaps=[]; sums={r:[0,0,0] for r in roles}
for i,d in data.items():
 for p in d['packages']:
  check(all(r in roles for r in p['effort']),'Known roles '+p['id'])
  check(all(0<=vs[0]<=vs[1]<=vs[2] for vs in p['effort'].values()),'Ordered effort '+p['id'])
  check([sum(v[j] for v in p['effort'].values()) for j in range(3)]==p['total'],'Lot total '+p['id'])
  for r,vs in p['effort'].items():
   for j,v in enumerate(vs):sums[r][j]+=v
  allpk.append({'iteration':i,**p})
 for c in d['coverage']:
  bc=c['block'];g=gridmap[bc];n=native[bc]
  check(c['id']==g['capacite_id']==n['id'],'Native identity '+bc)
  funcs=c.get('native_functions',c.get('functions',[]))
  fids=[x if isinstance(x,str) else x['id'] for x in funcs]
  check(set(fids)=={f['id'] for f in g['fonctions']},'Native functions reconciled '+bc)
  owners=c.get('own_packages',[c['own_package']] if c.get('own_package') else list({x['owner'] for x in c.get('function_funding',[])}))
  check(owners and all(x in {p['id'] for p in d['packages']} for x in owners),'Direct funding owners '+bc)
  shared=c.get('shared_dependencies',c.get('shared_owners',c.get('function_funding',[{}])[0].get('shared_owners',[])))
  allcaps.append({'block':bc,'id':c['id'],'name':n['name'],'path':n['path'],'path_names':n['path_names'],'iteration':i,
   'native_functions':g['fonctions'],'source_boundary':g['frontiere'],'direct_owners':owners,'shared_owners':shared,
   'direct_effort':[sum(p['total'][j] for p in d['packages'] if p['id'] in owners) for j in range(3)],
   'class':'C','structural_reserve':bc in final['structural_reserve_ids'],'analogy_type':c.get('analogy_type','partielle'),
   'meaning':'Fonctions instruites et charge proposée sous hypothèses ; ni implémentation ni équivalence intégrale à un ERP démontrée.'})
check(len(allpk)==len({p['id'] for p in allpk})==152,'152 unique funding lots')
check(len(allcaps)==len({c['block'] for c in allcaps})==88,'88 unique capabilities')
check({c['block'] for c in allcaps}==set(gridmap),'Exact native coverage universe')
check(sums==final['cumulative_estimated']['roles'],'Independent sum09–14 and16–20 equals final role totals')
totals=[sum(v[j] for v in sums.values()) for j in range(3)]
check(totals==final['full_core_jh'],'Independent full Core totals')
check(len(final['structural_reserve_ids'])==21,'21 named structural reserves')
function_count=sum(len(c['native_functions']) for c in allcaps)
check(function_count==sum(len(g['fonctions']) for g in grid),'Every native function assigned to a direct funding owner')
for i in range(16,21):
 d=data[i];check(d['input_sha256']==sha(A/f'iteration-{i}-entrees.json'),'Input hash '+str(i))
 check(all(t['passed'] for t in d['witnesses']),'Illustrative boundary checks '+str(i))
 for c in d['coverage']:
  check(c['scenario_estimated'] and c['comparatively_studied'],'No stale pilot status '+c['block'])
 for p in load(A/d['proofs_file'])['evidence']:
  check(all(e['text'] for e in p['excerpts']),'Source excerpts present '+p['id'])
meta=load(A/'or-tools-routing-source.json')
check(sha(A/meta['local'])==meta['sha256'],'OR-Tools frozen example hash')
for p in A.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'));check(True,'Python syntax '+p.name)
for p in A.glob('*.json'):load(p);check(True,'JSON parse '+p.name)
allcaps.sort(key=lambda c:c['block'])
write('couverture-complete.json',{'coverage_count':88,'native_function_count':function_count,'class':'C','capabilities':allcaps})
write('financements-complets.json',{'meaning':'152 lots comptés une seule fois ; les charges directes par capacité excluent les lots communs. Aucun prix unitaire appliqué.','roles':roles,'totals':totals,'role_totals':sums,'packages':allpk})
css="""*{box-sizing:border-box}html{scroll-behavior:smooth}body{overflow-wrap:anywhere;margin:0;background:#FAF8F4;color:#182632;font:16px/1.55 Aptos,'Segoe UI',Arial,sans-serif}main{max-width:1200px;margin:auto;padding:28px}header{background:#D9F2EA;padding:30px;border-radius:16px;border-top:5px solid #236159}h1{font-size:2.25rem;line-height:1.15;margin:8px 0 18px}h2{font-size:1.65rem;margin:0 0 16px}h3{font-size:1.2rem}a{color:#236159;text-decoration:underline;text-underline-offset:3px;overflow-wrap:anywhere}a:focus-visible{outline:3px solid #C24F00;outline-offset:3px}nav{background:white;padding:18px 24px;margin:22px 0;border-radius:12px}nav a{display:block;padding:3px 0}section{margin:26px 0;background:white;padding:28px;border-radius:12px;scroll-margin-top:18px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:22px}.metric{background:white;border-radius:10px;padding:18px}.metric strong{font-size:2rem;display:block;color:#236159}.note{background:#FFF0DB;border-left:4px solid #C24F00;padding:18px;margin:18px 0}.muted,small{color:#45525A}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;font-size:.95rem}th{background:#F4F8F6;text-align:left}td,th{padding:12px;border-bottom:1px solid #dbe3df;vertical-align:top}td.num,th.num{white-space:nowrap;text-align:right}tr.total{font-weight:700;background:#D9F2EA}.tag{display:inline-block;background:#FFF0DB;color:#763400;padding:2px 7px;border-radius:5px;font-weight:650}.cap{font-size:.88rem}.cap td{min-width:90px}.cap td:nth-child(2){min-width:280px}.lot{border-top:2px solid #D9F2EA;padding-top:16px;margin-top:28px}ul{padding-left:24px}li{margin:6px 0}code{overflow-wrap:anywhere}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.85rem;background:#f4f8f6;padding:16px}footer{padding:12px 0 30px;color:#45525A}@media(max-width:650px){main{padding:12px}header,section{padding:20px}h1{font-size:1.8rem}.grid{grid-template-columns:1fr}.metric strong{font-size:1.7rem}}@media print{body{background:white}main{max-width:none}section{break-inside:auto}.scroll{overflow:visible}nav{display:none}}"""
def table(headers,rows,cls=''):
 return '<div class="scroll"><table class="'+cls+'"><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(c)+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def role_table(d):
 rows=[[esc(label),*[fmt(x)+' JH' for x in d[r]]] for r,label in roles.items()]
 rows.append(['<strong>Total tous rôles</strong>',*[f'<strong>{fmt(sum(v[j] for v in d.values()))} JH</strong>' for j in range(3)]])
 return table(['Rôle','Bas','Central','Haut'],rows)
def sec(id,title,body):return f'<section id="{id}"><h2>{title}</h2>{body}</section>'
def doc(name,title,intro,sections,metrics=''):
 nav='<nav aria-label="Sommaire"><strong>Dans ce rapport</strong>'+''.join(f'<a href="#{id}">{esc(t)}</a>' for id,t,b in sections)+'</nav>'
 body=''.join(sec(*s) for s in sections)
 s='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+'</title><style>'+css+'</style></head><body><main><header><div>FLOW · Étude d’opportunité · Audit du 30 octobre 2026</div><h1>'+esc(title)+'</h1>'+intro+metrics+'</header>'+nav+body+'<footer>Estimation assistée par IA, sans revue humaine attribuée. Dossier expérimental distinct du modèle économique courant.</footer></main></body></html>'
 (A/name).write_text(s,encoding='utf-8',newline='\n')
def link_it(i):
 return f'iteration-{i:02}.html' if i>=16 else f'../{OLD.name}/iteration-{i:02}.html'
mechanisms=[
 ('09','Socle, références et données de référence','Identités, versions, imports, droits et stockage documentaire ; réutilisés sans second socle.'),
 ('10','Stock et faits physiques','Journal et effets de stock ; une prestation reconnue ne produit pas un second mouvement.'),
 ('11','Processus durables','Définitions et exécution, reprise, exceptions ; les coordinations spécialisées consomment ce moteur.'),
 ('12–15','Plans, commandes, promesses et optimisation','Décisions et propositions distinctes des engagements ; calculs et modèles spécialisés financés à leur niveau.'),
 ('16','Politiques et capacité','Versions de politiques et capacité sourcée ; pas de réserve implicite ni de disponibilité inventée.'),
 ('17','Coordination des prestations','Besoins, choix, plan de transport, faits et résultats ; les engagements restent portés par les ordres.'),
 ('18','Ordres de service','Cycle partagé et variantes ; métadonnées de pièces réutilisent le stockage09. Les raccords sont qualifiés côté ordre.'),
 ('19','Facturation et paiement','Demandes et rapprochement ; document, autorisation et règlement restent distincts.'),
 ('20','Analyse et qualification entre familles','Mesures et vues ; E201 finance 12 parcours entre familles, distincts des QA locales déjà comptées.')
]
progress=[]
for i in range(16,21):
 d=data[i];progress.append([f'<a href="{link_it(i)}">Itération {i}</a> — '+esc(d['title']),str(d['progress']['new_compared']),f"{d['progress']['compared_cumulative']}/88 · {fmt(round(d['progress']['percent'],1))} %",fmt(d['incremental']['total'][1]),fmt(d['cumulative_estimated']['total'][1])])
caprows=[]
for c in allcaps:
 path=' → '.join(c['path_names'][:-1])
 caprows.append([esc(c['block']),'<strong>'+esc(c['name'])+'</strong><br><small>'+esc(path)+'</small>',f'<a href="{link_it(c["iteration"])}">{c["iteration"]}</a>',esc(', '.join(c['direct_owners']))+'<br>'+fmt(c['direct_effort'][1])+' JH directs',('<span class="tag">Réserve importante</span>' if c['structural_reserve'] else 'Périmètre borné, classe C')])
reserve_rows=[]
for c in allcaps:
 if c['structural_reserve']:reserve_rows.append([c['block'],esc(c['name']),f'<a href="{link_it(c["iteration"])}">Hypothèses et limites · {c["iteration"]}</a>'])
trans=[c for c in allcaps if c['analogy_type']=='transversale']
calendar=[]
for i in range(16,21):
 d=data[i];calendar.append([f'<a href="{link_it(i)}">{i} · {esc(d["title"])}</a>',*[fmt(v)+' mois' for v in d['calendar']['incremental_public_months']]])
intro='<p><strong>Les 88 capacités de la cartographie sont instruites et disposent désormais d’une proposition de charge sous hypothèses.</strong> Cette couverture décrit le travail d’étude. Elle ne prouve ni une équivalence intégrale aux produits du marché, ni la précision des JH.</p>'
metrics='<div class="grid"><div class="metric"><strong>88 / 88</strong>capacités étudiées · 100 %</div><div class="metric"><strong>'+fmt(totals[1])+' JH</strong>charge centrale, tous rôles</div><div class="metric"><strong>Classe C</strong>estimation non calibrée</div></div>'
sections=[
('lecture','Ce que permet ce résultat','<p>On peut maintenant discuter d’un ordre de grandeur pour construire le Core System générique sur une stack Java/Spring, première étape de la plateforme de marques. Les règles de marque, interfaces et déploiements Beaumanoir, activités physiques et systèmes financiers ou réglementaires spécialisés restent hors de cette construction.</p><div class="note"><strong>Fourchette : '+fmt(totals[0])+' à '+fmt(totals[2])+' JH.</strong> Ce sont des scénarios d’ingénierie bas / central / haut, pas des percentiles. Les bornes résultent des travaux proposés et de facteurs de sensibilité par lot. Elles ne proviennent pas de temps mesurés dans les trois ERP.</div><p>Les volumes, niveaux de service et restrictions fonctionnelles des fiches sont des hypothèses proposées. Une exigence plus large peut changer les travaux et dépasser cette enveloppe. 100 % signifie que chaque fonction native a été examinée et rattachée à un financement ; cela ne signifie pas que ses garanties sont réalisées ou démontrées.</p>'),
('progres','Les cinq itérations et leur cumul',table(['Itération / famille','Capacités ajoutées','Cumul du périmètre','Ajout central · JH','Cumul central · JH'],progress)+'<p>Point de départ : 56/88 capacités et 8 935 JH centraux. Ajout de 32 capacités et 6 840 JH. Les 978 JH de l’itération20 comprennent 620 JH pour les deux capacités analytiques et 358 JH pour la qualification entre familles (E201).</p>'),
('roles','JH bruts cumulés par rôle',role_table(sums)+'<p><strong>Développement Java + interface : '+fmt(final['cumulative_developer_gross_jh'][1])+' JH</strong>, compris dans le total, avec une fourchette de '+fmt(final['cumulative_developer_gross_jh'][0])+' à '+fmt(final['cumulative_developer_gross_jh'][2])+' JH. Les tests des développeurs y figurent ; la QA indépendante possède sa propre ligne. Aucun TJM ni abattement de productivité n’est appliqué ici. La coordination technique ne représente pas le pilotage complet du programme de transformation.</p>'),
('fiabilite','Ce qui devient moins incertain','<ul><li>La délimitation des politiques, capacités, décisions, engagements et faits empêche de confondre leurs responsabilités.</li><li>Les mécanismes communs ont un financement identifié : on ne recrée pas quinze systèmes d’ordres, un second moteur de processus ou un second journal de stock.</li><li>Les réponses inconnues, corrections, partiels et adaptations après engagement sont désormais des travaux explicites.</li><li>Les comparaisons purement transversales sont identifiées, notamment pour certaines prestations et le Process Mining.</li></ul><p><strong>La précision numérique n’est pas démontrée meilleure.</strong> Le rapport haut/bas du cumul passe d’environ 2,9 à 3,2 avec l’ajout des familles. L’incertitude totale ne diminue donc pas mécaniquement avec la couverture. L’ancien périmètre n’a pas été resserré artificiellement.</p><p>67/88 capacités (76,1 %) n’ont pas de réserve structurelle majeure nommée dans ce registre, sous les restrictions retenues ; 21/88 (23,9 %) en ont une. Ce classement est un jugement d’analyse, pas une mesure statistique de fiabilité. Toutes restent de classe C. Aucune charge n’est calibrée par des bilans de projets.</p>'+table(['Capacité','Libellé natif','Détail de la réserve'],reserve_rows)),
('marche','Portée réelle des comparaisons marché','<p>Odoo, Tryton et Axelor ont été lus dans leurs sources à des révisions figées. Les extraits montrent des mécanismes et leurs différences ; ils ne fournissent ni coût historique ni productivité mesurée. Le code de ces ERP n’est pas supposé réutilisé directement dans Spring. Les travaux restant à construire sont estimés par décomposition.</p><p>Parmi les nouvelles capacités, les suivantes reposent explicitement sur une analogie transversale : '+esc(', '.join(c['block'] for c in trans))+'. Une comparaison de cycles, pièces ou historiques ne prouve pas une fonctionnalité métier équivalente.</p><p>COCOMO, COSMIC et ISBSG n’ont pas produit trois estimations indépendantes calibrées dans cette série. Il serait incorrect de présenter leur convergence comme une validation. Les essais OR-Tools / Timefold de15 éclairent des choix algorithmiques sur des cas synthétiques ; ils ne mesurent pas des JH de réalisation. Le modèle de tournées Java OR-Tools étudié en17 utilise une autre API et n’a pas été exécuté ici.</p>'),
('partage','Un seul financement par mécanisme',table(['Itération','Propriétaire','Frontière retenue'],[[esc(x) for x in row] for row in mechanisms])+'<p>La vérification arithmétique additionne 152 lots uniques des itérations09–14 et16–20. L’itération15 n’ajoute aucune charge. Les anciennes explorations01–08 et les cumuls intermédiaires ne sont pas additionnés. L’unicité des identifiants est vérifiée ; l’absence de recouvrement fonctionnel repose aussi sur les frontières décrites, qui restent à relire en architecture.</p>'),
('delai','Délais conservés, programme à organiser',table(['Famille','Bas','Central','Haut'],calendar)+'<p>Hypothèse commune aux nouvelles familles : 2 développeurs Java, 1 développeur interface, 1 QA ; analyse 0,8 personne, architecture 0,5, UX 0,3, plateforme 0,4, sécurité 0,3, coordination 0,3 et optimisation 0,5, selon les phases. Convention : 18 JH productifs/personne/mois. Les trois phases se succèdent ; leurs charges et contraintes de séquence sont conservées dans chaque fiche.</p><div class="note">Ces délais sont des scénarios locaux avec dépendances supposées disponibles. Ils ne sont ni additionnables comme un engagement programme, ni divisibles librement par un effectif. La somme séquentielle historique est conservée pour diagnostic ('+' / '.join(fmt(x) for x in final['calendar']['sequential_public_months'])+' mois, bas / central / haut). <strong>Ce n’est pas le délai estimé du programme FLOW.</strong> Le parallélisme, les équipes et le chemin critique global restent à construire.</div>'),
('inventaire','Cumul des 88 capacités',f'<p>{function_count} fonctions natives sont rattachées à un propriétaire de financement. Les JH directs ci-dessous excluent les lots communs : leur addition seule ne reconstitue pas le budget total. Les charges communes sont conservées au niveau de leur famille, sans allocation arbitraire à chaque BC. Les noms natifs sont conservés ; les fiches expliquent les mécanismes en français.</p>'+table(['BC','Capacité / hiérarchie','Itération','Lot et charge directs','Incertitude'],caprows,'cap')),
('suite','Décision proposée','<p><strong>Arrêter les itérations destinées à élargir la couverture : l’objectif 88/88 est atteint.</strong> Une nouvelle passe générale aurait peu de valeur. La suite utile consiste à organiser des équipes produit et une trajectoire de livraison, puis à arbitrer les 21 réserves les plus sensibles. Un essai technique supplémentaire doit répondre à une question capable de changer une décision, par exemple la faisabilité du routage ou la corrélation des traces.</p><p>Cette suite peut s’appuyer sur les sources de marché disponibles et des hypothèses assumées ; elle n’exige pas au préalable des bilans de projets inexistants. En revanche, sans preuve nouvelle, on ne doit pas réduire les fourchettes pour donner une impression de progrès.</p>'),
('preuves','Pièces, contrôles et reproduction','<ul><li><a href="couverture-complete.json">Inventaire complet et propriétaires de financement</a></li><li><a href="financements-complets.json">152 lots et efforts par rôle</a></li><li><a href="verification.json">Vérification indépendante</a></li><li><a href="build_report.py">Générateur et rapprochement</a> · <a href="run.py">Calcul des itérations</a> · <a href="witnesses.py">Illustrations de frontières</a></li><li><a href="../'+OLD.name+'/iteration-15.html">Essais comparatifs OR-Tools / Timefold conservés</a></li></ul><p>Reproduire avec Python et PyYAML : exécuter run.py pour16,17,18,19,20 dans cet ordre, puis build_report.py. Les 30 vérifications synthétiques de frontière sont des illustrations analytiques ; elles ne testent pas un Core System développé ni l’exécution des trois ERP.</p><p>Le modèle actif, ses données d’entrée et les pièces de l’itération15 restent inchangés par cet audit. Aucun commit ou push n’a été réalisé pour ces nouvelles itérations.</p>')
]
doc('index.html','Core System — couverture complète sous hypothèses',intro,sections,metrics)
for i in range(16,21):
 d=data[i];proofs=load(A/d['proofs_file'])['evidence']
 lots=''
 for p in d['packages']:
  lots+=f'<article class="lot" id="lot-{esc(p["id"])}"><h3>{esc(p["id"])} · {esc(p["label"])}</h3><p>{esc(p["work"])}</p><p><strong>Réutilisation déjà financée :</strong> {esc(" · ".join(p["reuse"]))}</p><p><strong>Incertitude :</strong> {esc(p["risk"])}</p>'+role_table(p['effort'])
  actions=p['java']+p['ui']
  lots+='<p>Décomposition des actions de développement (durées proposées, non observées) :</p>'+table(['Action','JH centraux'],[[esc(x),fmt(v)] for x,v in actions])
  lots+='<p>Sources : '+', '.join(f'<a href="#preuve-{esc(x)}">{esc(x)}</a>' for x in p['evidence'])+'.</p></article>'
 caps=''
 for c in d['coverage']:
  caps+=f'<article class="lot"><h3>{esc(c["block"])} · {esc(c["name"])}</h3><p>{esc(c["generic_contract"])}</p><p><strong>Frontière native :</strong> {esc(c["native_boundary"])}</p>'+table(['Fonction native','Résultat attendu'],[[esc(f['id']),esc(f['resultat'])] for f in c['native_functions']])+'<p>'+esc(c['market_analogy'])+'</p></article>'
 evid=''
 for p in proofs:
  evid+=f'<article class="lot" id="preuve-{esc(p["id"])}"><h3>{esc(p["id"])} · {esc(p["repository"])}</h3><p>{esc(p["observation"])}</p><p><strong>Limite :</strong> {esc(p["limit"])}</p><p><a href="{esc(p["url"])}">Source à la révision figée</a> · <code>{esc(p["commit"])}</code></p>'
  for e in p['excerpts']:evid+=f'<p>Lignes {e["start"]}–{e["end"]}</p><pre>{esc(e["text"])}</pre>'
  evid+='</article>'
 if d['supplemental_sources']:
  evid+='<article class="lot"><h3>OR-Tools · exemple Java de tournées</h3><p><a href="or-tools-routing-source.json">Provenance et empreinte</a> · <a href="or-tools-VrpTimeWindows.java.txt">Source figée</a> · <a href="https://developers.google.com/optimization/routing/vrptw">Documentation officielle</a>. Source lue, API RoutingModel distincte de CP-SAT ; aucune exécution de ce modèle dans cet audit.</p></article>'
 phases=table(['Phase','Bas · mois','Central · mois','Haut · mois'],[[esc(p['name']),*[fmt(round(x,1)) for x in p['months']]] for p in d['calendar']['phases']])
 sect=[
 ('resultat','Résultat de cette itération',f'<p>Ajout :<strong>{fmt(d["incremental"]["total"][1])} JH</strong> ({fmt(d["incremental"]["total"][0])}–{fmt(d["incremental"]["total"][2])}). Cumul :<strong>{fmt(d["cumulative_estimated"]["total"][1])} JH</strong> ({fmt(d["cumulative_estimated"]["total"][0])}–{fmt(d["cumulative_estimated"]["total"][2])}). {d["progress"]["compared_cumulative"]}/88 capacités étudiées.</p><p>{esc(d["contract"])}</p><div class="note">'+esc(d['profile'])+'</div>'),
 ('roles','Charges nouvelles par rôle',role_table(d['incremental']['roles'])+'<p>Tous rôles ; les charges Java/interface sont incluses, les lots communs comptés une fois. Estimation de classe C, aucune calibration par des temps observés.</p>'),
 ('incertitude','Progrès et limites','<p><strong>Moins incertain :</strong> '+esc(d['uncertainty']['reduced'])+'</p><p><strong>Reste incertain :</strong> '+esc(d['uncertainty']['remaining'])+'</p><p><strong>Itération suivante :</strong> '+esc(d['next_iteration'])+'</p>'),
 ('capacites','Capacités et fonctions natives',caps),
 ('lots','Travaux, rôles et réutilisation',lots),
 ('calendrier','Scénario de délai',phases+'<p>Délais arrondis : '+' / '.join(fmt(x) for x in d['calendar']['incremental_public_months'])+' mois (bas / central / haut). 18 JH/personne/mois ; dépendances supposées disponibles. Ces durées ne sont pas un calendrier de programme.</p>'+table(['Rôle','Personnes mobilisables'],[[esc(roles[r]),fmt(v)] for r,v in d['calendar']['phases'][0]['staff'].items()])),
 ('sources','Preuves source et limites',evid),
 ('audit','Traçabilité',f'<p><a href="iteration-{i}-entrees.json">Hypothèses et vecteurs de charge</a> · <a href="iteration-{i}-resultats.json">Calcul complet</a> · <a href="iteration-{i}-preuves.json">Extraits et empreintes</a></p><p>{len(d["witnesses"])} illustrations analytiques de frontières vérifiées. Ce ne sont pas des tests d’un produit réalisé. Chaque fichier actif surveillé est resté identique.</p>')
 ]
 doc(f'iteration-{i}.html',f'Itération {i} — '+d['title'],'<p><a href="index.html">Retour au bilan des 88 capacités</a></p>',sect)
artifacts={p.name:sha(p) for p in sorted(A.iterdir()) if p.is_file() and p.name not in ('verification.json','browser-check.json') and p.suffix not in ('.png',)}
write('verification.json',{'status':'passed','date':'2026-10-30','checks':checks,'lot_count':len(allpk),'capability_count':len(allcaps),'native_function_count':function_count,'totals':totals,'role_totals':sums,'structural_reserve_count':21,'active_files_unchanged':len(baseline['active_files']),'previous15_unchanged':True,'class':'C','empirical_calibration':False,'visual_review':'separate browser-check.json and screenshots','artifacts_sha256':artifacts})
print(json.dumps({'checks':len(checks),'lots':len(allpk),'capabilities':len(allcaps),'functions':function_count,'totals':totals},ensure_ascii=False))
