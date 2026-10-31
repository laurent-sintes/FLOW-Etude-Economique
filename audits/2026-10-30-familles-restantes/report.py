"""Readable report of the three-pass campaign and its final audit."""
from pathlib import Path
from html import escape as e
import hashlib,json
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
a=read(OUT/'audit-final.json');v=a['progress']
names=dict(zip([f['slug'] for f in a['families']],[
'Contrôle des prestataires','Politiques de satisfaction','Devenir du stock','Cycle des commandes','Master Plan',
'Préparation des plans','Gestion du carnet','Optimisation du stock','Promesse ATP / CTP / PTP','Planification des prestations',
'Coordination des prestations','Suivi et rapprochement des prestations','Ordres de traitement des biens','Ordres de transport',
'Prestation douanière','Prestations financières','Processus réactifs','Travail humain','Supervision des processus','Analyse des processus']))
def txt(n):return f'{n:,.0f}'.replace(',',' ') if n is not None else '—'
def table(headers,rows):
 return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+e(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
out=['<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FLOW — campagne des familles restantes</title>',
'<style>body{font:16px/1.6 system-ui,sans-serif;color:#163b3a;background:#f6f7f5;margin:0}main{max-width:1200px;margin:auto;padding:32px}h1,h2,h3{line-height:1.25}section{background:white;border:1px solid #d8e2df;border-radius:8px;padding:24px;margin:24px 0}.notice{border-left:6px solid #d36a25;background:#fff6eb;padding:18px}a{color:#176159}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:10px;border-bottom:1px solid #d8e2df;text-align:left;vertical-align:top}th{background:#e7f0ed}small{color:#455b59}li{margin:8px 0}.metrics{display:flex;gap:24px;flex-wrap:wrap}.metrics b{display:block;font-size:26px}.risk{color:#9b4308}code{font-size:13px}nav a{margin:0 12px 6px 0;display:inline-block}@media(max-width:600px){main{padding:14px}section{padding:14px}}</style><main>',
'<h1>Familles restantes Java/Spring</h1><p>Trois itérations par famille, deux analyses intermédiaires et audit final — 30 octobre 2026.</p>',
'<div class="notice"><strong>100 % du périmètre examiné ne signifie pas 100 % du logiciel chiffré de façon consolidée.</strong> Les montants ci-dessous sont des calculs d’essai. Aucun n’a été ajouté aux décisions adoptées.</div>',
'<section class="metrics"><div><b>60 / 60</b>itérations réalisées</div><div><b>40 / 40</b>analyses intermédiaires</div><div><b>88 / 88</b>capacités examinées</div><div><b>1 940 JH</b>cumul adopté inchangé</div><div><b>16 / 88</b>capacités avec estimation adoptée</div></section>',
'<section><h2>Ce qui a progressé</h2><p>Les vingt familles disposent de sources figées, d’un premier examen de périmètre, de comptages fonctionnels proposés et d’un troisième passage élargi aux composants et appels métier. Les mesures trop courtes des seuls points d’entrée ont été identifiées. Les rôles et délais nominaux ont été calculés sur chaque diagnostic, sans additionner les délais.</p>',
f'<p>{v["distinct_native_sources"]} fichiers natifs distincts ont été vérifiés. {v["native_effort_calculations_independently_reproduced"]} calculs natifs et vingt comptages COSMIC ont été contrôlés indépendamment. Les quatre technologies utilisent les conventions COCOMO déjà présentes dans le modèle ; les parts de code et de compléments restent des hypothèses.</p>',
'<p><strong>Aucun nouveau chiffre n’est prêt à être adopté à l’issue de cet audit.</strong> Douze familles ont un candidat conditionnel ; huit restent non consolidables. Les dépendances et la continuité de la mesure doivent être fermées avant une proposition budgétaire globale.</p></section>',
'<section><h2>Vue des familles</h2><p>JH calculés à l’itération 3, arrondis à dix JH. Ils ne constituent pas un coût OSS observé. COSMIC × ISBSG utilise le comptage proposé et 20 h/CFP, avec facteur 1 et 7 h/JH. La proximité de deux résultats ne valide pas leur justesse.</p>']
rows=[]
for f in a['families']:
 n=f['native_rounded_jh'];status='Candidat conditionnel, non adopté' if f['candidate_java_jh'] is not None else 'Non consolidable'
 rows.append(['<a href="#'+f['slug']+'">'+e(names[f['slug']])+'</a>',e(', '.join(f['capabilities'])),txt(n['erpnext']),txt(n['odoo']),txt(n['tryton']),txt(n['axelor']),txt(f['COSMIC_jh']),'<span class="risk">'+status+'</span>'])
out.append(table(['Famille','Capacités','ERPNext + Frappe','Odoo','Tryton','Axelor Java','COSMIC × ISBSG','Statut'],rows))
out.append('<p><strong>Pas de total global de ces colonnes :</strong> les mécanismes partagés ne sont pas encore réconciliés. Le cumul des décisions adoptées reste 1 940 JH.</p></section>')
out.append('<section><h2>Audit : reprises nécessaires</h2>')
for f in a['findings']:
 out.append('<h3>'+e(f['id']+' — '+f['subject'])+'</h3><p>'+e(f['observation'])+'</p><p><strong>Conséquence :</strong> '+e(f['consequence'])+'</p><p><strong>Travail à conduire :</strong> '+e(f['missing_iteration'])+'</p>')
out.append('</section><section><h2>Ordre de reprise recommandé</h2><ol><li>Fermer le cycle Order et les contrats de prestations partagés, puis attribuer leur financement une seule fois.</li><li>Fermer composition des processus, tâches, journal métier et interventions ; mesurer les adaptations Flowable et les consommateurs.</li><li>Reprendre les calculs de planification, promesse et optimisation sur leurs services communs ; vérifier le modèle de contraintes et l’adaptation OR-Tools/Timefold.</li><li>Réconcilier tailles, compléments, rôles et comptages des familles consommatrices, puis soumettre des chiffres à adoption.</li></ol></section>')
for f in a['families']:
 folder=OUT/f['slug'];one=read(folder/'iteration-1.json');an1=read(folder/'analyse-1.json');two=read(folder/'iteration-2.json');an2=read(folder/'analyse-2.json');three=read(folder/'iteration-3.json')
 task=next(x['task'] for x in a['missing_or_additional_iterations'] if x['slug']==f['slug'])
 out.append('<section id="'+f['slug']+'"><h2>'+e(names[f['slug']])+'</h2><small>'+e(f['name'])+' · '+e(', '.join(f['capabilities']))+'</small>')
 out.append('<h3>Itération 1 : sources et frontière</h3><p>'+e(an1['observation'])+'</p>')
 out.append('<p><strong>Analyse orientant la suite :</strong> '+e(an1['next_iteration_objective'])+'</p>')
 out.append('<h3>Itération 2 : premier dimensionnement</h3><p>'+e(an2['conclusion'])+'</p>')
 out.append('<p><strong>Analyse orientant la suite :</strong> '+e(an2['next_iteration_objective'])+'</p>')
 change=three['measured_change']
 out.append('<h3>Itération 3 : composants et délégations</h3><p>Pour Java, la mesure passe de '+txt(change['java_units_iteration_2'])+' à '+txt(change['java_units_iteration_3'])+' unités logiques. '+txt(change['additional_source_files'])+' sources supplémentaires et '+txt(change['resolved_direct_calls'])+' appels directs vérifiés. Le coefficient de pertinence et la fraction de complément sont conservés pour distinguer l’effet du changement de périmètre.</p>')
 out.append('<p><strong>Reprise identifiée par l’audit :</strong> '+e(task)+'</p>')
 out.append('<p><strong>Rôles sur le diagnostic :</strong> hypothèse d’organisation, non budget adopté.</p>')
 out.append(table(['Rôle','JH du diagnostic'],[[e(r['label']),txt(r['jh'])] for r in three['roles']]))
 out.append('<p>Délai local calculé sur ce diagnostic : '+txt(three['delay']['rounded_months'])+' mois. Ne pas l’additionner aux délais des autres familles. Ce délai ne constitue pas un engagement.</p>')
 out.append('<p>Limites : '+e(' '.join(three['limits']))+'</p>')
 out.append('<p>Preuves et calculs : '+''.join('<a href="'+f['slug']+'/'+p+'">'+e(label)+'</a> · ' for p,label in [('iteration-1.json','Itération 1'),('analyse-1.json','Analyse 1'),('iteration-2.json','Itération 2'),('analyse-2.json','Analyse 2'),('iteration-3.json','Itération 3')])+'</p></section>')
out.append('<section><h2>Conservation et vérification</h2><p>Master Data 1 500 JH / 17 mois, Stock 340 JH / 10 mois et Propriété du stock 100 JH / 7 mois sont conservés. Le référentiel métier reçu et les paramètres actifs n’ont pas été modifiés. Les vérifications de cette campagne portent sur ses preuves, son calcul et son périmètre ; elles ne sont pas une validation prédictive.</p><p><a href="audit-final.json">Audit complet</a> · <a href="verification.json">Contrôles indépendants</a> · <a href="bilan.yaml">Bilan structuré</a></p></section></main></html>')
(OUT/'synthese.html').write_text('\n'.join(out),encoding='utf-8')
print('Rapport lisible : '+str(OUT/'synthese.html'))
