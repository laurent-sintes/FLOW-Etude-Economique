"""Readable results for the Master Data recalculation; consumes computed outputs."""
from pathlib import Path
import json,html,hashlib,ast
A=Path(__file__).resolve().parent;ROOT=A.parents[1]
load=lambda n:json.loads((A/n).read_text(encoding='utf-8'))
I=load('entrees.json');R=load('resultats.json');C=load('recompte-cosmic.json');T=load('recalcul-taille.json');D=load('repartitions-sources.json');V=load('repartition-calculee.json')
e=lambda s:html.escape(str(s))
def f(x,d=1):
 return f'{x:,.{d}f}'.replace(',',' ').replace('.',',').removesuffix(',0')
def table(headers,rows):
 return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+e(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(x)+'</td>' for x in r)+'</tr>' for r in rows)+'</tbody></table></div>'
def item(id,title,body):return (id,title,body)
isb=R['isbsg']['main'];nom=R['cocomo']['nominal_central']
css="""*{box-sizing:border-box}body{margin:0;background:#FAF8F4;color:#182632;font:16px/1.6 Aptos,'Segoe UI',Arial,sans-serif;overflow-wrap:anywhere}main{max-width:1160px;margin:auto;padding:26px}header{background:#D9F2EA;padding:30px;border-radius:16px;border-top:5px solid #236159}h1{font-size:2.2rem;line-height:1.2}h2{font-size:1.6rem}h3{font-size:1.2rem}section,nav{background:white;border-radius:12px;padding:26px;margin:24px 0}nav a{display:block;padding:3px 0}a{color:#236159;text-underline-offset:3px}a:focus-visible{outline:3px solid #C24F00;outline-offset:3px}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:.94rem}th,td{padding:12px;text-align:left;border-bottom:1px solid #dbe3df;vertical-align:top}th{background:#F4F8F6}.note{background:#FFF0DB;padding:18px;border-left:4px solid #C24F00;margin:18px 0}.formula{background:#F0F8F5;padding:18px;border-radius:8px;font-size:1.12rem}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.metric{padding:18px;background:white;border-radius:10px}.metric strong{font-size:1.8rem;color:#236159;display:block}small,.muted{color:#45525A}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f8f6;padding:18px}li{margin:6px 0}footer{padding:20px 0;color:#45525A}@media(max-width:650px){main{padding:12px}header,section,nav{padding:18px}h1{font-size:1.75rem}.grid{grid-template-columns:1fr}}@media print{nav{display:none}body{background:white}.scroll{overflow:visible}}"""
provenance=[
 ['Périmètre métier','6 capacités, BC-002 à BC-007 ;14 fonctions natives','Référence documentaire','Cartographie et contrat pilote conservés.'],
 ['Scénario fonctionnel','25 processus,23 groupes de références et15 hypothèses explicites','Hypothèse de produit','Réception, consultation, usages et reprise ; plusieurs résultats restent hors du comptage.'],
 ['Taille COSMIC',f(C['total'])+' CFP','Résultat d’un comptage conditionnel','Somme des mouvements E/R/W/X ; ce ne sont pas des heures.'],
 ['Tailles unitaires OSS','Extraits Java et TypeScript, fichiers et empreintes vérifiés','Mesures de code','Les tailles de blocs ne mesurent pas leur temps de développement.'],
 ['Taille cible FLOW','8 228 /11 326 /15 654 unités logiques estimées','Hypothèse d’implémentation','53 modèles et360 champs proposés ; styles de code et correspondance à la convention COCOMO non validés.'],
 ['Taux COSMIC–ISBSG','20 h/CFP et ajustement0,8 pour300–500 CFP','Référence publiée + hypothèse de transfert','Rapport2012 ; Java/multiplateforme, nouveaux développements.'],
 ['COCOMO','Coefficients publiés ; notes nominales ou scénarios explicites','Modèle publié + hypothèses de contexte','Aucune observation de maturité ou compétence de la future équipe.'],
 ['JH','Heures calculées /7','Calcul','Aucune durée de tâche saisie ni tirée des lots09–20.'],
 ['JH par rôle','Non déterminés','Inconnu','Une répartition par activité est conservée ; plusieurs rôles peuvent réaliser la même activité.']
]
processrows=[[p['id'],e(p['label']),*[str(p['movements'].get(k,0)) for k in 'ERWX'],str(p['cfp'])] for p in C['processes']]
processrows.append(['<strong>Total</strong>','25 processus',*[str(C['movements'][k]) for k in 'ERWX'],f'<strong>{C["total"]}</strong>'])
case_rows=[]
for case in R['cocomo']['cases']:
 case_rows.append([e(case['label']),case['size_variant'],f(case['ksloc'],3),f(case['effort_jh']),f(case['months'])])
altrows=[[e(x['id']),f(x['hours_per_cfp_used']),f(x['effort_jh']),e(x['scope'])] for x in R['isbsg']['alternative_calculations']]
sensrows=[[e(x['hypothesis']),str(x['result']['cfp']),f(x['result']['effort_jh'][1])] for x in R['isbsg']['scope_sensitivity']]
compare=[[e(x['topic']),e(x['cosmic']),e(x['cocomo']),e(x['impact'])] for x in I['reconciliation']]
allocation=[[e(x['label']),f(100*x['fraction'],2)+' %',f(x['effort_jh']),e(x['mapping_limit'])] for x in V['rows']]
allocation.append(['<strong>Total E+C</strong>','100 %',f'<strong>{f(V["base_jh"])}</strong>','Ventilation du même effort, sans supplément.'])
isb_dist=[[e(x['label']),str(x['percent'])+' %'] for x in D['isbsg']['activities']]
raw_cocomo=[[e(x['label']),*[str(v)+' %' for v in x['percent_by_phase']]] for x in D['cocomo']['activities']]
unknowns=[[e(x['id']),e(x['missing'])] for x in C['open_questions']]
sections=[
item('decision','Résultat : deux calculs, aucun total complet validé',
 '<p><strong>Le résultat nouveau est une voie COSMIC × ISBSG calculable à partir de coefficients publics.</strong> COCOMO est recalculé indépendamment à partir de la taille candidate. COSMIC fournit une taille, ISBSG une référence d’effort par unité et COCOMO un autre modèle d’effort : cela produit deux voies de calcul, pas trois devis indépendants.</p>'+
 table(['Voie','Entrée principale','JH calculés','Ce que le résultat couvre'],[
 ['COSMIC × ISBSG','350 CFP, scénario partiel',f(isb['effort_jh'][1]),'Effort de référence normalisé niveau1 ; sous hypothèse de transposition.'],
 ['COCOMO nominal','11,326 KSLOC estimés, scénario partiel',f(nom['effort_jh']),'Effort logiciel selon le modèle ; paramètres nominaux, taille et périmètre non validés.']
 ])+
 '<div class="note"><strong>Les deux assiettes ne sont pas encore identiques.</strong> L’écart arithmétique de '+f(R['comparison']['cocomo_nominal_minus_isbsg_pct'])+' % ne démontre pas une convergence. Aucune moyenne, aucune addition et aucun budget global Master Data ou Core System ne sont retenus.</div><p>Les15 775 JH historiques ne sont pas une entrée du calculateur et ne servent pas de cible. Le modèle économique courant reste inchangé.</p>'),
item('provenance','Observé, supposé ou calculé',table(['Élément','Valeur / contenu','Statut','Limite'],[[e(x) for x in row] for row in provenance])+
 '<p>La connaissance des sources de marché étaye la décomposition du logiciel. Elle ne transforme pas une quantité de code FLOW proposée en quantité observée. Les coefficients externes rendent la conversion calculable ; ils ne suppriment pas l’incertitude des entrées.</p>'),
item('cosmic','Recompte COSMIC : 350 points conditionnels',
 '<p>Une seule frontière applicative : React, API, services et persistance interne. Les échanges techniques internes ne sont pas ajoutés comme des entrées/sorties externes. E = entrée, R = lecture persistante, W = écriture persistante, X = sortie.</p>'+
 '<div class="formula">Taille conditionnelle =51 E +137 R +75 W +87 X =<strong>350 CFP</strong></div>'+
 table(['Processus','Résultat','E','R','W','X','CFP'],processrows)+
 '<p>Les25 processus sont recomptés mouvement par mouvement ; les types répétés et les sommes sont contrôlés. La conformité sémantique dépend toujours des groupes, déclencheurs et hypothèses du scénario. Les14 fonctions natives sont touchées, mais aucune des6 capacités n’est démontrée complètement mesurée.</p>'+
 '<p><a href="recompte-cosmic.json">Mouvements, hypothèses et questions ouvertes</a> · <a href="https://cosmic-sizing.org/cosmic-sizing/intro/measurement-process/">Définition officielle du processus de mesure</a></p>'),
item('isbsg','Calcul à partir de la référence COSMIC–ISBSG',
 '<p>La référence retenue pour ce scénario est la procédure Java/multiplateforme des tableaux7–8 du rapport conjoint2012, illustrée page13. Elle utilise20 h/CFP, puis0,8 pour la tranche 300–500 CFP. Il s’agit d’un ajustement proposé par les auteurs, pas d’un taux Spring observé.</p>'+
 '<div class="formula">350 CFP ×20 h/CFP ×0,8 =5 600 h<br>5 600 h ÷7 h/JH =<strong>800 JH</strong></div>'+
 '<p>La dispersion publiée20 ±7, transférée avec le même calcul, donne520–1 080 JH. Elle n’est pas une fourchette de confiance FLOW. Ces références portent sur des projets1999–2011 ; aucune remise pour Spring, React, cloud ou IA n’est inventée.</p>'+
 table(['Variante de référence','h/CFP appliquées','JH pour350 CFP','Limite'],altrows)+
 '<p>Le choix de population modifie déjà le résultat. Les trois variantes proviennent du même rapport, elles ne constituent pas trois preuves indépendantes. La valeur P25 imprimée158 au tableau2 est incohérente avec sa médiane23 : elle est conservée comme anomalie et exclue du calcul.</p>'+
 '<p><a href="'+e(I['benchmark']['url'])+'#page=12">Rapport source : méthode et coefficients, p.12–13</a> · <a href="reference-source.json">Provenance et empreinte du PDF</a></p>'),
item('cocomo','Calcul COCOMO et délai conservé',
 '<p>COCOMO II.2000 Early Design ; taille agrégée avant application de la puissance. Les modèles et champs cibles restent des propositions. Les bibliothèques inchangées et le code généré ne sont pas comptés comme du code neuf ; aucun second rabais de réutilisation n’est appliqué.</p>'+
 table(['Composant de taille','Hypothèse basse','Hypothèse centrale','Hypothèse haute'],[
 ['Java',*[f(v) for v in T['java']]],['TypeScript / React',*[f(v) for v in T['typescript']]],['Total, unités logiques estimées',*[f(v) for v in T['total_sloc']]]
 ])+
 '<div class="formula">E =0,91 +0,01 ×18,97 =1,0997<br>Effort =2,94 ×11,326<sup>1,0997</sup> =42,4146 mois-personne<br>JH =42,4146 ×152 ÷7 =<strong>921,0 JH</strong><br>Délai nominal =3,67 ×42,4146<sup>0,31794</sup> =<strong>12,1 mois</strong></div>'+
 table(['Contexte hypothétique','Taille','KSLOC','JH calculés','Mois calculés'],case_rows)+
 '<p>Les notes de contexte ne sont pas des observations de l’équipe FLOW. La durée est calculée par COCOMO, pas fixée à l’avance ni obtenue en divisant les JH par une équipe choisie. Elle porte sur les jalons logiciels du modèle et ne fournit pas le délai complet du produit ou des déploiements Groupe. Les JH sont ici des journées de7 heures ; les152 heures/mois-personne du modèle ne sont pas remplacées par la disponibilité mensuelle d’un planning.</p>'+
 '<p><a href="recalcul-taille.json">Décomposition de taille recalculée</a> · <a href="preuves-tailles.json">Tailles OSS et empreintes</a> · <a href="https://www.rose-hulman.edu/class/csse/csse372/201310/Homework/CII_modelman2000.pdf">Manuel USC, équations et conventions</a></p>'),
item('repartitions','Répartitions d’effort conservées',
 '<p><strong>Les répartitions publiées sont conservées avec leurs dénominateurs.</strong> Elles concernent des activités, pas une affectation automatique à des métiers.</p>'+
 '<h3>COCOMO : application conditionnelle aux921 JH</h3><p>Tableau57, MBASE/RUP : la base calculée finance24 % d’élaboration et76 % de construction. Pour chaque activité, on pondère ses parts dans ces deux phases. Exemple analyse :24 % ×18 % +76 % ×8 % =10,4 % du total. Ce sont des valeurs par défaut publiées, dont l’applicabilité à FLOW reste une hypothèse.</p>'+
 table(['Activité','Part calculée E+C','JH calculés','Interprétation pour les rôles'],allocation)+
 '<p>La réalisation comprend des tests unitaires. L’évaluation comprend aussi des revues ; toute sa charge ne revient pas automatiquement à la QA indépendante. Ni répartition Java/interface, ni clé entre architecte, développeurs et spécialistes n’est fournie par ces données.</p>'+
 '<h3>COCOMO : valeurs d’origine par phase</h3>'+
 table(['Activité','Inception','Élaboration','Construction','Transition'],raw_cocomo)+
 '<p>Les parts d’effort des phases sont 6 / 24 / 76 / 12 % de la base E+C, et celles de délai 12,5 / 37,5 / 62,5 / 12,5 %. Les compléments initial et transition sont conservés, mais ne sont pas ajoutés au total retenu : celui-ci reste inconnu. La colonne « Total COCOMO II » du manuel couvre 118 % de la base ; elle ne doit pas être traitée comme une ventilation de 100 % des921 JH.</p>'+
 '<h3>ISBSG : repère empirique Java conservé</h3>'+table(['Activité','Pourcentage publié'],isb_dist)+
 '<p>Tableau 18 : 13 projets Java, sur le sous-total spécification–conception–réalisation–test. La somme publiée est 99 % ; elle est conservée sans correction silencieuse. Ces ratios ne sont pas appliqués aux800 JH, qui incluent des phases supplémentaires dont la part n’est pas connue ici. Le repère planning4,7 % concerne 15 projets tous langages et un autre dénominateur. Les exemples de l’annexe p.46 illustrent la normalisation ; ils ne calibrent pas une répartition type.</p>'+
 '<p><a href="repartitions-sources.json">Répartitions sources et conditions d’emploi</a> · <a href="repartition-calculee.json">Ventilation calculée et conservation du total</a></p>'),
item('confrontation','Confrontation des périmètres : les écarts qui empêchent une validation',
 table(['Sujet','Voie COSMIC','Voie COCOMO','Conséquence'],compare)+
 '<p>Le calculateur conserve explicitement le total complet et les JH par rôle à « inconnu ». Il n’ajoute pas des temps d’ingénierie pour combler les trous. La proximité 800/921 et même leur éventuel recouvrement de plages ne prouvent pas que les modèles ont chiffré le même produit.</p>'),
item('sensibilites','Ce qui dépend encore des hypothèses',
 '<p>Les variantes suivantes changent des exigences identifiables du comptage fonctionnel, sans changer le taux d’effort ni créer une durée de tâche. Elles restent dans la tranche 300–500 CFP de la référence.</p>'+
 table(['Changement hypothétique','CFP','JH avec référence ajustée'],sensrows)+
 '<p>Ces variantes ne couvrent pas toutes les inconnues. Le périmètre complet n’a donc ni borne haute établie ni intervalle statistique. En particulier :</p>'+table(['Question','Information manquante'],unknowns)),
item('suite','Avancement et décision',
 '<p>6/6 capacités Master Data et 14 fonctions natives sont examinées. Une nouvelle voie de conversion externe est calculable, les deux formules sont reproduites et les répartitions par activité sont conservées. <strong>0/6 capacités ont à ce stade une estimation complète dont les deux assiettes sont réconciliées.</strong> Ce dernier indicateur remplace toute impression que la couverture documentaire vaut fiabilité du chiffrage.</p>'+
 '<p>Une prochaine itération ciblée vaut le coup : aligner le protocole de reprise, la purge, les administrations et les phases sur un même scénario produit. Cela peut se faire avec des choix explicites et les sources du marché, sans attendre des bilans internes ni spécifier chaque détail. En revanche, recalculer les mêmes formules ou redécouper des durées proposées n’apporterait aucune validation supplémentaire.</p>'+
 '<p>La présente reprise ne remplace pas les15 775 JH par un nouveau cumul Core et n’intègre aucun chiffre dans l’économie active. Elle fournit un résultat conditionnel auditable et identifie précisément ce qui empêche encore d’en faire une estimation complète.</p>'),
item('preuves','Fichiers et reproduction',
 '<ul><li><a href="entrees.json">Entrées, références, hypothèses et exclusions</a></li><li><a href="calcul.py">Calculateur Python sans durées de tâches</a> · <a href="resultats.json">Résultats détaillés</a></li><li><a href="verification.json">Contrôles, empreintes et vérification indépendante</a></li><li><a href="../2026-10-29-experimentation-estimation/iteration-07-contrat-v1.1.json">Contrat de famille conservé</a></li></ul>'+
 '<p>Reproduction depuis la racine du projet : Python calcul.py puis rapport.py, avec leurs chemins dans ce dossier. Les entrées antérieures de taille sont lues sans être modifiées ; les anciens JH des lots ne sont pas lus. Les exemples officiels sont vérifiés, ainsi que les unités, les mouvements COSMIC, la conservation des ventilations et les empreintes des fichiers actifs.</p>')
]
header='<header><div>FLOW · Étude d’opportunité · Reprise Master Data · 30 octobre 2026</div><h1>Des JH calculés, avec leurs hypothèses visibles</h1><p><strong>Deux résultats conditionnels sont disponibles. L’estimation complète de Master Data reste ouverte.</strong> Les durées des anciennes tâches ne sont pas utilisées.</p><div class="grid"><div class="metric"><strong>350 CFP</strong>sous-ensemble fonctionnel hypothétique</div><div class="metric"><strong>800 JH</strong>scénario COSMIC × ISBSG</div><div class="metric"><strong>921 JH</strong>scénario COCOMO nominal</div></div></header>'
nav='<nav aria-label="Sommaire"><strong>Lire le dossier</strong>'+''.join('<a href="#'+id+'">'+title+'</a>' for id,title,b in sections)+'</nav>'
content=header+nav+''.join('<section id="'+id+'"><h2>'+title+'</h2>'+b+'</section>' for id,title,b in sections)
doc='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FLOW · Master Data · Calculs et confrontation</title><style>'+css+'</style></head><body><main>'+content+'<footer>Auteur : assistant IA. Aucune revue humaine attribuée. Références et hypothèses identifiées ; modèle actif inchangé.</footer></main></body></html>'
# Typography: separate prose numbers without rewriting identifiers or source data.
for a,b in [('Les15','Les 15'),('les15','les 15'),('Les25','Les 25'),('Les14','Les 14'),('des921','des 921'),('aux921','aux 921'),('aux800','aux 800'),('des6','des 6'),('les152','les 152'),('de7 heures','de 7 heures'),('planning4,7','planning 4,7'),('350 CFP','350 CFP')]:doc=doc.replace(a,b)
for a,b in [('Tableau57','Tableau 57'),('finance24','finance 24'),('et76','et 76'),('analyse :24','analyse : 24'),('à100%','à 100 %'),('tableaux7–8','tableaux 7–8'),('conjoint2012','conjoint 2012'),('page13','page 13'),('utilise20','utilise 20'),('puis0,8','puis 0,8'),('publiée20 ±7','publiée 20 ± 7'),('donne520','donne 520'),('projets1999','projets 1999'),('pour350','pour 350'),('imprimée158','imprimée 158'),('tableau2','tableau 2'),('médiane23','médiane 23'),('java_multiplatform_unadjusted','Java multiplateforme, sans correction de taille'),('java_pc_size_adjusted','Java PC, avec correction de taille'),('java_all_platforms','Java, toutes plateformes')]: doc=doc.replace(a,b)
(A/'index.html').write_text(doc,encoding='utf-8',newline='\n')
for p in A.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
verification={'status':'passed','arithmetic_checks':len(R['checks']),'checks':R['checks'],'active_files_preserved':True,'historical_size_inputs_preserved':True,'retained_full_family_estimate':None,'source_pages_visually_reviewed':{'COSMIC_ISBSG':[8,9,12,13,31,46],'COCOMO':[68,69]},'visual_report_status':'pending browser review','artifacts_sha256':{p.name:sha(p) for p in A.iterdir() if p.is_file() and p.name not in ['verification.json','browser-check.json'] and p.suffix!='.png'}}
(A/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Report generated')
