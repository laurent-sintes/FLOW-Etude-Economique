from pathlib import Path
import json,html,re
A=Path(__file__).resolve().parent
load=lambda n:json.loads((A/n).read_text(encoding='utf-8'))
I=load('entrees.json');R=load('resultats.json');S=load('socle-et-fonctions.json');M=load('mesures-code.json')
h=lambda v:html.escape(str(v))
def n(v,d=1):return f'{v:,.{d}f}'.replace(',',' ').replace('.',',')
def table(head,rows):
 return '<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+h(c)+'</th>' for c in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(c)+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def ul(items):return '<ul>'+''.join('<li>'+x+'</li>' for x in items)+'</ul>'
sections=[]
def add(id,title,body):sections.append((id,title,body))
src_co='https://www.rose-hulman.edu/class/csse/csse372/201310/Homework/CII_modelman2000.pdf'
src_is='https://cosmic-sizing.org/wp-content/uploads/2015/07/Performance-of-Business-Application-Real-Time-and-Component-Software-Projects-2012.pdf'
add('decision','Résultat : la structure est mieux comprise, le budget reste incertain',
'<p><strong>COCOMO a été appliqué aux quatre enveloppes de code natives. Aucune ne constitue une estimation complète de Master Data FLOW.</strong> Le témoin porte sur les unités et les coefficients de conversion ; il ne couvre ni toutes les références métier ni les garanties multi-source de FLOW.</p>'+
'<p>Cette confrontation diminue le risque d’oublier le socle et clarifie les phases financées. Elle ne démontre pas une meilleure précision des JH. Les langages, les déclarations, les comportements et les services déjà fournis par les frameworks restent différents.</p>'+
'<p>La demande du sponsor est conservée comme hypothèse d’architecture : <strong>Flow = un socle commun + des fonctions + leurs raccordements</strong>. Les propriétaires du financement sont définis dans ce dossier, mais leurs tailles Spring résiduelles restent à construire.</p>')
rows=[]
for p in I['products']:
 rows.append([h(p['name']),h(p['language']),'<code>'+p['commit'][:12]+'</code>',h(p['differences'])])
add('perimetre','Un témoin Master Data borné et quatre produits',
'<p>ERPNext/Frappe était la référence initiale, complétée historiquement par Odoo, Tryton et Axelor. Les quatre sont conservés. L’analyse est statique : les produits ne sont pas exécutés et aucune charge historique n’est observée. Le rattachement FLOW concerne des parties de F06–F07 du contrat Master Data, liées à BC-004 et BC-005. Il ne signifie pas que ces deux capacités sont entièrement couvertes.</p>'+
table(['Produit','Technologie native','Révision','Différences qui restent visibles'],rows)+
'<p><strong>Comparable ne signifie pas identique.</strong> Le coefficient est un document distinct dans ERPNext et Axelor, mais un attribut de l’unité dans Odoo et Tryton. Tryton interdit de modifier certains facteurs déjà définis. Les processus candidats ne se retrouvent donc pas un pour un dans tous les produits.</p>'+
'<p>Les unités initiales livrées en données, comme mètre ou kilogramme, sont exclues du comptage de code. Les imports de langage, commentaires, types autogénérés et code généré ne sont pas assimilés à du code spécifique écrit manuellement.</p>'+
'<p><a href="entrees.json">Contrat, exclusions et conventions de comptage</a> · <a href="sources-erpnext.json">Provenance ERPNext</a></p>')
rows=[]
for p in R['products']:
 rows.append([h(p['name']),str(p['logical_units']),str(p['declarative_units']),n(p['main']['jh_elaboration_construction']),n(p['main']['jh_full_lifecycle_hypothesis']),n(p['scenarios'][1]['jh_full_lifecycle_hypothesis'])+' – '+n(p['scenarios'][3]['jh_full_lifecycle_hypothesis'])])
add('cocomo','COCOMO sur les quatre OSS : sorties mécaniques, non budgets retenus',
'<p>Les tailles ci-dessous sont mesurées dans les sources. Pour le scénario central, une déclaration XML/JSON est pondérée à 1 unité logique. Cette équivalence n’est pas calibrée ; les poids 0,5 et 2 rendent sa sensibilité visible. Les instructions Python et Java ne sont pas converties entre langages.</p>'+
'<div class="formula">E = 0,91 + 0,01 × 18,97 = 1,0997<br>PM = 2,94 × (unités logiques / 1 000)<sup>1,0997</sup><br>JH élaboration + construction = PM × 152 / 7<br>JH quatre phases = JH précédents × (1 + 0,06 + 0,12)</div>'+
table(['Implémentation native','Code logique','Déclarations','JH E+C','JH quatre phases, poids 1','JH poids déclaratif 0,5 à 2'],rows)+
'<p><strong>Ces petits nombres ne chiffrent ni le socle ni le produit complet.</strong> Ils décrivent une hypothèse de réalisation des extensions spécifiques alors que le framework natif existe déjà. Les services partagés ne sont pas gratuits : leur construction est hors de cette assiette. Les enveloppes mesurées contiennent aussi des comportements supplémentaires propres à chaque produit.</p>'+
'<p>La taille très petite du témoin, les conventions de comptage et les services implicites rendent ces résultats impropres à une extrapolation à FLOW. La colonne de sensibilité n’est ni une fourchette de charge complète, ni un intervalle de confiance. La référence nominale des facteurs de contexte est supposée commune ; elle n’a pas été observée sur les équipes de ces produits.</p>'+
'<p><a href="mesures-code.json">Mesures, empreintes, sélections et contrôles Git</a> · <a href="'+src_co+'">Manuel COCOMO, taille et formules</a></p>')
rows=[]
for f in M['frappe_direct_dependencies']:
 rows.append(['<a href="'+h(f['url'])+'#L'+str(f['start_line'])+'">'+h(f['file'])+'</a>',h(f['name']),str(f['start_line'])+'–'+str(f['end_line']),str(f['logical_units'])])
add('frappe','ERPNext + Frappe : la chaîne observée',
'<p>Les DocTypes UOM et UOM Conversion Factor déclarent les données, les autorisations et des options d’interface. Leurs contrôleurs Python ne contiennent presque aucun traitement propre. La fonction get_uom_conv_factor ajoute la recherche directe, inverse et intermédiaire.</p>'+
'<div class="formula">Déclaration ERPNext → métadonnées Frappe → API / formulaire → permissions → Document.insert ou _save → validation → persistance</div>'+
'<p>Les chemins directs ont été repérés et leurs extraits conservés au commit Frappe <code>2fcb9397a1f1da353b21e53d2f97ec56653acd02</code>. Le formulaire standard utilise les métadonnées et les permissions. Les 18 entrées Python examinées représentent '+str(M['frappe_selected_logical_units'])+' instructions selon le compteur, mais ne constituent pas toute la fermeture des dépendances de Frappe.</p>'+
'<p><strong>Ce volume n’est pas ajouté aux JH du module.</strong> Recréer ces fonctions Frappe et utiliser des composants Spring existants sont deux scénarios différents. La reconstruction complète de Frappe n’est pas retenue.</p>'+
table(['Source','Entrée inspectée','Lignes','Unités observées'],rows)+
'<p><a href="frappe-extraits.json">Extraits Python et identifiants des sources</a> · <a href="frappe-interface-extraits.json">Preuves de l’interface générique Frappe</a> · <a href="socles-natifs-preuves.json">14 entrées équivalentes de lecture du socle Odoo/Tryton/Axelor</a></p>')
add('socle','Le modèle d’estimation retenu : socle, fonctions, raccordements',
table(['Propriétaire unique','Mécanisme','Observation Frappe','Transposition Spring et restant'],[[h(x['id']),h(x['name']),h(x['frappe']),h(x['spring'])] for x in S['owners']])+
'<p>Le socle commun sera financé une seule fois. Chaque famille finance ensuite ses données, comportements propres et raccordements. Une ventilation du socle entre capacités peut servir à la lecture économique, mais doit conserver le total et ne finance pas le socle plusieurs fois.</p>'+
'<p>Pour COCOMO, il faut agréger les tailles nouvelles et les tailles équivalentes d’adaptation selon les règles du modèle avant d’appliquer la puissance. Additionner un calcul COCOMO par écran ou par méthode introduirait un autre biais.</p>'+
'<p><strong>Le chiffrage complet est un objectif atteignable sous hypothèses, pas un résultat disponible ici.</strong> Le dossier distingue les composants réutilisables et les fonctions génériques non encore sélectionnées. La qualification des licences et des versions des futurs composants Spring reste à mener avant de retenir leur réutilisation.</p>'+
'<p><a href="socle-et-fonctions.json">Hypothèse d’architecture et propriétaires</a> · <a href="'+S['spring_sources'][0]+'">Spring MVC</a> · <a href="'+S['spring_sources'][1]+'">Validation Spring</a> · <a href="'+S['spring_sources'][2]+'">Spring Security</a></p>')
P=R['phase_alignment_previous_master_data']
add('activites','Alignement des activités : ce qui est calculé et ce qui reste conventionnel',
'<p>L’assiette visée est l’effort de l’équipe logicielle depuis le cadrage jusqu’à la mise en service initiale. Les déploiements de marques, les métiers contributeurs, l’intégration Beaumanoir, la maintenance et le fonctionnement annuel ne sont pas ajoutés.</p>'+
table(['Activité ou phase','COCOMO','COSMIC × ISBSG','État'],[
['Cadrage initial','Ajout publié : 6 % de la base E+C','Planning/spécification dans l’effort normalisé','Correspondance approximative, pas identité de tâches'],
['Analyse, conception, réalisation, tests','Inclus dans élaboration + construction','Inclus dans les six activités normalisées','Recouvrement établi, distribution non identique'],
['Coordination, environnement et configuration','Activités présentes dans chaque phase','Effort de l’équipe affectée ; pas de ventilation identique démontrée','Ne pas ajouter un forfait de pilotage ou de QA'],
['Mise en service initiale','Transition ajoutée : 12 % de la base E+C','Implement inclus dans la normalisation','Le rapport ISBSG signale des contenus parfois plus larges'],
['Personnes externes à l’équipe affectée','À définir selon périmètre logiciel retenu','Peuvent être exclues du niveau 1','Pas de total tous rôles démontré']
])+
'<div class="formula">'+n(P['previous_cocomo_ec_jh'])+' JH × 1,18 = <strong>'+n(P['full_lifecycle_cocomo_hypothesis_jh'])+' JH</strong><br>Écart avec 800 JH : '+n(P['before_gap_pct'])+' % avant → '+n(P['after_phase_alignment_gap_pct'])+' % après cet alignement conventionnel</div>'+
'<p>Ce calcul porte sur le scénario Master Data précédent, pas sur les quatre micro-modules. Les phases initiale et de transition sont maintenant explicites ; la différence de contenu fonctionnel demeure. Les 12,1 mois de base deviennent mécaniquement environ 15,1 mois avec les deux compléments de calendrier de 12,5 % chacun, mais aucun délai complet de FLOW n’est retenu.</p>'+
table(['Activité COCOMO','Part du cycle élargi','JH du scénario précédent élargi'],[[h(x['label']),n(x['fraction_of_full_lifecycle']*100,2)+' %',n(x['jh_previous_scenario_aligned'])] for x in R['full_lifecycle_activity_allocation']])+
'<p>La ventilation conserve exactement le total avant arrondis. Les tests unitaires sont déjà compris dans la réalisation ; la validation ne revient pas exclusivement au rôle QA. Les répartitions ISBSG publiées restent conservées dans le dossier précédent, avec leurs dénominateurs.</p>'+
'<p><a href="'+src_co+'">COCOMO, tableaux 46 et 57</a> · <a href="'+src_is+'">COSMIC–ISBSG, annexe A</a></p>')
add('cosmic','Confrontation COSMIC–ISBSG du témoin : une limite mesurable',
table(['Processus candidat','E','R','W','X','CFP'],[[h(p['label']),p['E'],p['R'],p['W'],p['X'],sum(p[k] for k in ['E','R','W','X'])] for p in I['cosmic']['processes']])+
'<p>Le contrat candidat totalise <strong>26 CFP</strong>. Avec le repère Java et la correction publiée pour 10–50 CFP, le calcul donne :</p>'+
'<div class="formula">26 × 20 h/CFP × 1,2 ÷ 7 h/JH = <strong>'+n(R['isbsg_java_witness_jh'][1])+' JH</strong></div>'+
'<p>Le transfert mécanique de la dispersion publiée donne '+n(R['isbsg_java_witness_jh'][0])+' à '+n(R['isbsg_java_witness_jh'][2])+' JH. Cette plage ne quantifie pas l’incertitude réelle du témoin sur un framework. Le taux Java n’est pas utilisé comme calibration des trois implémentations Python.</p>'+
'<p><strong>Ce résultat ne valide aucun des quatre montants COCOMO.</strong> Les 26 CFP décrivent un contrat candidat incluant le comportement fourni par le socle, alors que les lignes spécifiques excluent sa construction. Le découpage des opérations n’est pas identique dans les produits : unité et coefficient peuvent être créés ensemble, et la modification d’un facteur est restreinte dans Tryton. Diviser ces CFP par les lignes observées pour fabriquer une conversion serait injustifié.</p>'+
'<p><a href="'+src_is+'">Référence : tableaux 7–8, correction 1,2 et limites de l’échantillon</a></p>')
add('avancement','Avancement cumulé et incertitude',
table(['Indicateur','Résultat','Interprétation'],[
['OSS avec un calcul COCOMO explicite','4 / 4','ERPNext + Frappe réintégré'],
['OSS avec effort réellement consommé disponible','0 / 4','Aucune précision prédictive validée'],
['Entrées directes de frameworks documentées','32','18 Frappe + 14 Odoo/Tryton/Axelor ; pas dépendances exhaustives'],
['Capacités Master Data examinées au cumul','6 / 6','BC-002 à BC-007, acquis antérieurs conservés'],
['Capacités complètement chiffrées sur assiettes réconciliées','0 / 6','Le témoin ne complète aucune capacité entière'],
['Nouvelles capacités couvertes dans cette itération','0','Approfondissement de la méthode et des dépendances'],
['Cumul JH brut Master Data / Core validé','Inconnu','Les alternatives natives ne sont pas additionnées']
])+
'<p><strong>Ce qui progresse :</strong> la provenance des tailles, le traitement du déclaratif, la visibilité du socle et l’assiette des phases. <strong>Ce qui ne progresse pas encore :</strong> une fourchette fiable du budget complet Spring, une allocation par rôle ou un percentile de délai.</p>'+
'<p>Cette itération permet une décision : <strong>modifier la façon de construire l’estimation avant de multiplier les comparaisons.</strong> La prochaine étape utile consiste à définir le socle Flow nécessaire à Master Data, choisir ce qui est fourni par les bibliothèques Java et dimensionner une famille fonctionnelle sur ce socle. Les quatre produits servent de références de mécanismes. Un nouveau tour de comptage de lignes natives, sans cette décision, aurait peu de valeur.</p>'+
'<p>Les 15 775 JH historiques ne sont ni relus pour régler les calculs ni validés par cette confrontation. Les sources économiques actives et l’application restent inchangées.</p>')
add('preuves','Reproduction et preuves',
ul(['<a href="calcul.py">Calculateur Python</a> et <a href="resultats.json">résultats détaillés</a>','<a href="verification.json">Vérifications et empreintes</a>','<a href="entrees.json">Entrées et conventions</a>','<a href="../2026-10-30-master-data-calcul/index.html">Reprise Master Data précédente</a>'])+
'<p>Depuis la racine du projet : exécuter Python calcul.py puis rapport.py avec leurs chemins dans ce dossier. Le calcul n’utilise aucune durée de tâche proposée par l’IA. Les quantités observées, les conventions de taille et les paramètres supposés sont distincts.</p>')
css=re.search(r'<style>([\s\S]*?)</style>',(A.parent/'2026-10-30-master-data-calcul/index.html').read_text(encoding='utf-8')).group(1)
css+='.table-wrap{overflow-x:auto}.formula{padding:18px;background:#edf7f3;border-left:4px solid #236159;line-height:1.8} code{overflow-wrap:anywhere}'
header='<header><div>FLOW · 30 octobre 2026 · Itération 22</div><h1>Quatre OSS, un socle à rendre explicite</h1><p><strong>ERPNext + Frappe · Odoo · Tryton · Axelor</strong></p><p>La confrontation éclaire les différences de périmètre. Elle ne valide pas encore un budget Master Data.</p></header>'
nav='<nav aria-label="Sommaire"><strong>Lire le dossier</strong>'+''.join('<a href="#'+id+'">'+title+'</a>' for id,title,b in sections)+'</nav>'
doc='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FLOW · Master Data · Quatre OSS et socle</title><style>'+css+'</style></head><body><main>'+header+nav+''.join('<section id="'+id+'"><h2>'+title+'</h2>'+b+'</section>' for id,title,b in sections)+'<footer>Analyse et propositions assistées par IA. Pas de revue humaine attribuée. Aucun changement du modèle économique actif.</footer></main></body></html>'
(A/'index.html').write_text(doc,encoding='utf-8',newline='\n')
print('Report generated')
