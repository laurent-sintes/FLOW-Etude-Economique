from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def load(n):return json.loads((OUT/n).read_text(encoding="utf-8-sig"))
i=load("inputs.json");r=load("results.json");m=load("manifest.json");v=load("verification.json")
def esc(x):return html.escape(str(x))
def num(x,d=0):return f"{x:,.{d}f}".replace(",","\u202f").replace(".",",")
def table(head,rows):
 return '<div class="table-scroll" tabindex="0"><table><thead><tr>'+''.join('<th>'+esc(h)+'</th>' for h in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+c+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'
parts=['''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Master Data — quatre références natives</title><style>
:root{--green:#236159;--ink:#182632;--mint:#D9F2EA;--ivory:#FAF8F4;--peach:#FFF0DB}
*{box-sizing:border-box}body{margin:0;background:var(--ivory);color:var(--ink);font:16px/1.55 Aptos,"Segoe UI",Arial,sans-serif}
header,main,footer{max-width:1150px;margin:auto;padding:28px}header{background:var(--mint);border-bottom:4px solid #FF7A1A}
h1{font-size:clamp(29px,4vw,43px);line-height:1.15;margin:12px 0}h2{font-size:26px;margin:40px 0 12px;color:var(--green)}h3{font-size:20px}
a{color:var(--green);text-underline-offset:3px}a:focus-visible,.table-scroll:focus-visible{outline:3px solid #C24F00;outline-offset:4px}
nav{display:flex;gap:10px 20px;flex-wrap:wrap;margin:18px 0}p{max-width:100ch}.note{background:var(--peach);border-left:4px solid #C24F00;padding:18px;margin:18px 0}
.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.card{background:white;border:1px solid #b4c8c1;border-top:4px solid var(--green);padding:18px;border-radius:6px}.card h3{margin:0;font-size:17px;min-height:3.1em}.value{font-size:32px;font-weight:750;line-height:1.3;margin:14px 0}.small{font-size:14px;color:#45525A}
table{width:100%;border-collapse:collapse;background:white;min-width:650px}th,td{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #cfdbd5}th{background:#F4F8F6}td{font-size:15px}.table-scroll{overflow-x:auto;margin:16px 0}ul{padding-left:22px}li{margin:6px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#F0F8F5;padding:18px;border-radius:6px}code{font-size:14px}
.proof{font-size:13px;overflow-wrap:anywhere}.border{padding:15px 0;border-bottom:1px solid #cfdbd5}footer{font-size:14px;color:#45525A}
@media(max-width:850px){.cards{grid-template-columns:repeat(2,1fr)}}@media(max-width:500px){header,main,footer{padding:20px}.cards{grid-template-columns:1fr}.card h3{min-height:0}.value{font-size:34px}}
@media print{nav{display:none}body{background:white}header,main,footer{max-width:none}.cards{grid-template-columns:repeat(2,1fr)}.table-scroll{overflow:visible}table{min-width:0;font-size:11px}.card,table{break-inside:avoid}}
</style><header><p>ÉTUDE ÉCONOMIQUE FLOW · AUDIT DU 30 OCTOBRE 2026</p><h1>Master Data : quatre références natives</h1><p>Un total par OSS, avant toute transposition à Spring ou consolidation.</p><nav><a href="#resultats">Quatre chiffres</a><a href="#perimetre">Périmètre et preuves</a><a href="#calcul">Calcul</a><a href="#activites">Activités</a><a href="#incertitude">Incertitude</a><a href="#avancement">Avancement</a></nav></header><main>''']
parts.append('<section id="resultats"><h2>Résultats du scénario de reconstruction</h2><div class="note"><strong>Hypothèse déterminante : reconstruire la sélection de code métier et de mécanismes de plateforme natifs, financée intégralement une fois par alternative.</strong> Ces résultats ne mesurent ni le coût historique des OSS, ni leur installation, ni le budget Master Data de Flow. La sélection n’est pas un sous-produit autonome dont toutes les dépendances auraient été fermées.</div><div class="cards">')
for x in r["results"]:
 parts.append('<article class="card"><h3>'+esc(x["label"])+'</h3><p class="value">≈ '+num(round(x["nominal"]["jh_full"]/100)*100)+' JH</p><p>'+esc(x["technology"])+'</p><p class="small">Délai nominal du modèle : '+num(x["nominal"]["schedule_full_months"],1)+' mois.<br>Calendrier théorique, sans équipe validée.</p></article>')
parts.append('</div><p>Les JH couvrent les activités de projet logiciel ci-dessous, y compris analyse, conception, réalisation, QA/évaluation, pilotage et déploiement. Ils ne sont pas des JH développeur seuls. <strong>Les quatre alternatives ne s’additionnent pas.</strong></p></section>')
parts.append('<section id="perimetre"><h2>Ce que les quatre sélections comparent</h2><p>'+esc(i["scope"]["label"])+'. La présence de ces rubriques dans le code ne démontre pas une équivalence complète des comportements.</p>')
rows=[]
for family in i["scope"]["families"]:
 row=[esc(family["label"])]
 for product in i["products"]:
  repo,path=family[product["id"]];rev=m["repos"][repo]
  row.append('<a class="proof" href="https://github.com/'+esc(rev["repository"])+'/blob/'+rev["commit"]+'/'+esc(path)+'">'+esc(Path(path).name)+'</a>')
 rows.append(row)
parts.append(table(["Rubrique","ERPNext / Frappe","Odoo","Tryton","Axelor"],rows))
for fam in i["scope"]["families"]:parts.append('<p><strong>'+esc(fam["label"])+' :</strong> '+esc(fam["limit"])+'</p>')
parts.append('<h3>Limites propres à chaque référence</h3>')
for p in i["products"]:
 parts.append('<article class="border"><h3>'+esc(p["label"])+'</h3><p>'+esc(p["reconstruction"])+'</p><p>'+esc(p["extra_scope"])+'</p><p><strong>Réutilisation conservée :</strong> '+esc(p["external_reuse"])+'</p></article>')
parts.append('<h3>Hors comparaison ou couverture non démontrée</h3><ul>'+''.join('<li>'+esc(s)+'</li>' for s in i["scope"]["out_of_comparison"])+'</ul></section>')
parts.append('<section id="calcul"><h2>Des sources au calcul</h2><p>Les fichiers sont dédupliqués à l’intérieur de chaque alternative. Le comptage distingue instructions/déclarations de programme et déclarations XML, JSON, JSX ou HTML. Les blocs de typage ERPNext/Frappe générés, tests, données préchargées, bundles et bibliothèques exclus ne sont pas convertis en code à reconstruire.</p><p><strong>La taille est un indicateur logique reproductible, pas une mesure SLOC certifiée.</strong> L’hypothèse centrale attribue une unité à chaque déclaration. Les instructions Java/Python/JavaScript/TypeScript sont lues par analyse syntaxique, sans compter les lignes de commentaires.</p>')
rows=[]
for x in r["results"]:
 rows.append([esc(x["label"]),num(x["measured_files"]),num(x["program_units"]),num(x["declarative_units"]),num(x["nominal"]["size_ksloc_proxy"],3),num(x["nominal"]["jh_full"]),num(x["fraction_units_in_selected_platform"]*100,1)+' %'])
parts.append(table(["Référence","Fichiers","Programme","Déclaratif","k unités retenues","JH calculés","Part de taille : plateforme"],rows))
parts.append('<pre>K = (unités programme + poids × unités déclaratives) / 1 000\nE = 0,91 + 0,01 × 18,97 = 1,0997\nPM = 2,94 × K^E × EM ; EM = 1 dans le cas nominal\nJH = PM × 152 heures / 7 heures × 1,18\nDélai = 3,67 × PM^0,31794 × 1,25 mois</pre><p>La base COCOMO correspond à Élaboration + Construction. Les facteurs 1,18 et 1,25 ajoutent les phases initiale et de transition selon la distribution par défaut du manuel. <a href="'+esc(i["calculation"]["source"])+'">Manuel COCOMO II, équations 1–2 et table 57</a>. Paramètres nominaux et extension de phases restent des hypothèses d’application.</p><p><strong>Le délai est une sortie du modèle, pas une durée choisie pour obtenir les JH.</strong> Il n’est pas le délai d’une équipe produit de taille imposée.</p></section>')
parts.append('<section id="activites"><h2>Répartition d’effort conservée</h2><p>Distribution par défaut MBASE/RUP du manuel, appliquée aux quatre phases. Les activités sont comprises dans le total ; ne pas ajouter une seconde fois la QA ou l’architecture. Cette ventilation n’est pas une observation des équipes OSS.</p>')
rows=[]
for index,a in enumerate(r["results"][0]["activities"]):
 label="Préparation et déploiement" if a["id"]=="deployment" else a["label"]
 rows.append([esc(label),num(a["fraction_of_full_effort"]*100,2)+' %']+[num(x["activities"][index]["jh"],1) for x in r["results"]])
rows.append(["<strong>Total JH</strong>","100 %"]+['<strong>'+num(x["nominal"]["jh_full"],1)+'</strong>' for x in r["results"]])
parts.append(table(["Activité","Part","ERPNext / Frappe","Odoo","Tryton","Axelor"],rows))
parts.append('<p><strong>Activités et rôles restent distincts.</strong> Analyse → analyste/produit ; conception → architecture et développeurs ; réalisation → développeurs backend/frontend ; évaluation → développeurs et QA ; environnement/déploiement → plateforme et développeurs ; gestion → pilotage logiciel. Aucune clé numérique par rôle n’est démontrée ici.</p></section>')
parts.append('<section id="incertitude"><h2>Ce qui reste incertain</h2><div class="note"><strong>Incertitude élevée, non calibrée.</strong> Les bornes suivantes testent uniquement le poids des déclarations. Elles ne sont ni un intervalle de confiance, ni des P10/P50/P90, ni l’incertitude totale.</div>')
rows=[]
for x in r["results"]:
 rows.append([esc(x["label"])]+[num(y["jh_full"])+' JH' for y in x["declarative_sensitivity"]])
parts.append(table(["Référence","Poids 0","Poids 1 : nominal","Poids 2"],rows))
parts.append('<p>Ces variations limitées ne rendent pas les estimations précises. À taille fixée, EM = 0,75 ou 1,5 donnerait mécaniquement 75 % ou 150 % des JH nominaux ; aucune de ces valeurs n’est qualifiée pour ces équipes. La principale incertitude demeure la frontière des mécanismes à reconstruire ou à réutiliser.</p><ul>'+''.join('<li>'+esc(x)+'</li>' for x in i["uncertainty"]["unquantified"])+'</ul><h3>Statut de la confrontation des méthodes</h3>')
for k in ["cocomo","cosmic","isbsg"]:parts.append('<p><strong>'+k.upper()+' :</strong> '+esc(i["triangulation"][k])+'</p>')
parts.append('<p><strong>'+esc(i["triangulation"]["conclusion"])+'</strong></p></section>')
parts.append('<section id="avancement"><h2>Avancement et intérêt de la suite</h2><ul><li><strong>4 / 4 références natives calculées</strong>, avec 6 dépôts figés et '+num(len(m["files"]))+' fichiers contrôlés contre Git.</li><li><strong>8 rubriques examinées par référence</strong>, avec 32 liens de preuve. C’est un état d’inventaire, pas un taux de parité fonctionnelle.</li><li>Famille étudiée cumulée : <strong>6 capacités, BC-002 à BC-007</strong>. Les quatre produits ne multiplient pas ce nombre.</li><li><strong>0 nouvelle capacité admise au budget Flow</strong> par cette itération. Aucun nouveau cumul global en JH Flow calculable à ce stade.</li><li>Sources actives : '+num(v["active_source_files_unchanged"])+' fichiers témoins inchangés ; aucun commit ni push effectué.</li></ul><p><strong>Progression réelle :</strong> les tailles sources, les hypothèses, le calcul des JH, les activités et les délais sont traçables. Les durées ne sont plus des propositions libres.</p><p><strong>Limite :</strong> cette traçabilité ne valide pas encore le montant économique ni la parité des périmètres. L’incertitude sur la reconstruction de plateforme reste dominante.</p><div class="note"><strong>Une autre itération vaut le coup.</strong> '+esc(i["next_iteration"])+'</div></section>')
parts.append('<section id="preuves"><h2>Reproduire et vérifier</h2><p>Depuis la racine du projet, avec les parseurs tree-sitter installés dans le cache indiqué dans measure.py :</p><pre>python -B audits/2026-10-30-master-data-natif/selection.py\npython -B audits/2026-10-30-master-data-natif/measure.py\npython -B audits/2026-10-30-master-data-natif/calculate.py\npython -B audits/2026-10-30-master-data-natif/verify.py\npython -B audits/2026-10-30-master-data-natif/report.py</pre><ul>')
for file,label in [("inputs.json","Hypothèses et périmètre"),("manifest.json","Manifeste source et empreintes"),("measurements.json","Mesures détaillées par fichier"),("results.json","Calculs, activités et délais"),("verification.json","Contrôles indépendants")]:
 parts.append('<li><a href="'+file+'">'+label+'</a></li>')
parts.append('</ul><p>Contrôles techniques : '+num(v["check_count"])+' assertions réussies, aucune erreur de lecture syntaxique. Ces contrôles vérifient les calculs et les sources ; ils ne certifient pas la méthode économique.</p></section></main><footer>Préparé avec assistance IA · Références natives conditionnelles · Aucun chiffre appliqué au modèle économique courant.</footer></html>')
(OUT/"index.html").write_text("".join(parts),encoding="utf-8")
print("Rapport généré")
