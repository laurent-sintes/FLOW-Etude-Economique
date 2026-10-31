"""Readable completed opportunity estimate, with no automatic adoption."""
from pathlib import Path
from html import escape as e
import json,csv,hashlib,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tmp/model-deps'))
import yaml
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def n(x,d=0):return f'{x:,.{d}f}'.replace(',',' ').replace('.',',') if x is not None else 'Non établi'
def table(headers,rows):
 return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+e(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def main():
 r=read(OUT/'iteration-08/results.json');d=read(OUT/'iteration-08/inputs.json');v=read(OUT/'verification.json');b=read(OUT/'baseline.json');st=read(OUT/'stability.json');sens=read(OUT/'sensitivity.json')
 assert v['passed'] and st['passed']
 units=[dict(id=u['id'],name=u['label'],capabilities=[c['id'] for c in u['capabilities']],jh=u['total_jh'],months=u['months'],roles=u['roles'],status='Retenu') for u in b['units']]
 units += [dict(id=u['id'],name=u['name'],capabilities=u['capabilities'],jh=u['proposed_java_jh'],months=u['nominal_months'],roles=u['roles'],status='Proposé') for u in r['economic_units']]
 assumptions=[
 'Fractions et nombre des modules Flow nouveaux ; modèles et vues supposés, pas spécification détaillée.',
 'Six unités de financement cohérentes ; un autre regroupement change le calcul non linéaire.',
 'Réutilisation effective du patrimoine adopté et des moteurs, avec adaptation métier ; pas reconstruction de leurs noyaux.',
 'Objectifs et contraintes comparables aux modèles énumérés ; ni moteur réglementaire douanier, ni comptabilité, ni WMS d’exécutant, ni connecteurs Beaumanoir cachés dans le Core.',
 'Volumes, SLA et ergonomie à préciser en conception. Les budgets prévoient architecture, QA, plateforme et frontend, sans démontrer leurs performances.',
 'Paramètres COCOMO nominaux et rendement COSMIC × ISBSG non calibrés sur des bilans de projet ; stabilité de calcul ne vaut pas précision prédictive.'
 ]
 audit=[
 dict(id='A01',status='fermé sous hypothèses de l’étude',result='Référentiel inchangé ; 72 capacités restantes et 215 résultats fonctionnels affectés aux six unités ; les 16 capacités retenues sont distinctes.'),
 dict(id='A02',status='fermé',result='70 mécanismes/modules ont un propriétaire, dont onze communs. Les 280 JH communs sont intégrés ; capacité et prestation ont des objets nommés distincts.'),
 dict(id='A03',status='fermé',result='148 fichiers vérifiés aux révisions figées avec le même compteur ; 104 calculs reproduits indépendamment.'),
 dict(id='A04',status='chiffré pour opportunité, réalisation non démontrée',result='Mécanismes sans équivalent exact dimensionnés par modules d’analogie nommés ; fractions et quantités supposées. Aucune durée proposée par l’IA ne sert d’entrée aux JH.'),
 dict(id='A05',status='contrôle proposé, pas calibration',result='Six frontières COSMIC recomptées, deux doubles événements fusionnés. Rendement de 20 h/CFP non calibré au réemploi ; pas de moyenne forcée ni somme des CFP du Core.'),
 dict(id='A06',status='chiffrage disponible, organisation à construire',result='Rôles et délais locaux calculés. Spécialités optimisation et moteur incluses dans Java/architecture/QA ; aucun engagement d’équipe ni calendrier global validé.'),
 dict(id='A07',status='financement clarifié dans la proposition',result='OR-Tools et Timefold consommés avec un seul contrat de calcul. Le catalogue actif et les écrans restent hors de cette proposition.')
 ]
 closing=dict(status='chiffrage_opportunite_stabilise_proposition_complete',recommendation='Arrêter les itérations générales avec les connaissances actuelles.',complete_scope_jh=4160,retained_jh=1940,new_proposed_jh=2220,common_280_embedded=True,
 scope=dict(capabilities=88,retained=16,new_proposed=72,new_function_results=215,economic_units=9,new_coherent_units=6,original_remaining_families=20),
 stability=st,audit=audit,residual_assumptions=assumptions,verification_ref='verification.json',rules_ref='source/fondamentaux.yaml#estimation_model',
 not_claimed=['Précision statistique ou percentile','Revue humaine extérieure','Charges réelles observées des quatre OSS','Compatibilité runtime Camunda/Flowable testée','COCOMO intégré du Core complet','Adoption automatique'],
 next_estimation_iteration_worthwhile=False,reopen_if=['Nouveau mécanisme ou garantie de service significative','Défaut de réutilisation ou changement de moteur démontré','Découpage produit/équipes modifiant les unités','Prototype représentatif ou bilan réel permettant une calibration'],
 active_model_changed=False,retained_values_unchanged=True,no_commit_or_push=True)
 save(OUT/'audit-final.json',closing)
 (OUT/'bilan.yaml').write_text(yaml.safe_dump(dict(summary=closing,units=units,family_allocations=r['families'],sensitivities=sens['results']),allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
 ids=[x['id'] for x in v['global_roles']]
 with (OUT/'jh-par-role.csv').open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.writer(f,delimiter=';');writer.writerow(['Unité','Statut','Capacités','JH','Délai nominal local mois']+[x['label'] for x in v['global_roles']])
  for u in units:
   rr={x['id']:x['jh'] for x in u['roles']};writer.writerow([u['name'],u['status'],','.join(u['capabilities']),u['jh'],u['months']]+[rr[k] for k in ids])
  writer.writerow(['TOTAL','Retenu + proposé','88',4160,'Non additionnable']+[x['jh'] for x in v['global_roles']])
 html=['<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FLOW — chiffrage complet Java/Spring</title>',
 '<style>body{margin:0;background:#f6f7f5;color:#173c3a;font:16px/1.6 system-ui,sans-serif}main{max-width:1200px;margin:auto;padding:30px}h1,h2{line-height:1.25}section{background:white;border:1px solid #d7e1df;border-radius:8px;padding:24px;margin:22px 0}.notice{border-left:6px solid #d36924;background:#fff6eb;padding:20px}.metrics{display:flex;flex-wrap:wrap;gap:32px}.metrics strong{display:block;font-size:30px}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:10px;border-bottom:1px solid #d7e1df;text-align:left;vertical-align:top}th{background:#e8f0ed}a{color:#176159}li{margin:8px 0}@media(max-width:600px){main{padding:14px}section{padding:14px}}</style><main>',
 '<h1>Core System Flow — chiffrage Java/Spring</h1><p>Étude d’opportunité · itérations complémentaires 5 à 8 · 30 octobre 2026</p>',
 '<div class="notice"><strong>4 160 JH bruts pour le périmètre complet, en proposition consolidée.</strong><br>1 940 JH déjà retenus + 2 220 JH nouvellement proposés. Les 280 JH communs sont intégrés dans les nouveaux lots, sans ajout. Les décisions actives restent inchangées.</div>',
 '<section class="metrics"><div><strong>88 / 88</strong>capacités chiffrées pour l’étude</div><div><strong>16 / 88</strong>capacités déjà retenues</div><div><strong>148</strong>fichiers sources vérifiés</div><div><strong>9</strong>unités de financement, dont 6 nouvelles</div></section>',
 '<section><h2>Chiffre proposé et décomposition</h2><p>Le calcul conserve les trois décisions adoptées. Les vingt familles restantes sont rassemblées en six ensembles de composants fortement liés : COCOMO II est exécuté une seule fois par ensemble. Les Business Areas reçoivent ensuite une allocation de cette charge.</p>']
 html.append(table(['Unité de financement','Capacités','JH bruts','Statut','Délai nominal local'],[[e(u['name']),str(len(u['capabilities'])),n(u['jh']),u['status'],str(u['months'])+' mois'] for u in units]+[['<strong>Total</strong>','88','<strong>4 160</strong>','Retenu + proposé','Délais non additionnables']]))
 html.append('<p>Le total additionne des financements disjoints ; il ne constitue pas un recalcul COCOMO intégré de tout le Core. Les délais sont locaux et ne définissent pas le calendrier du programme. Master Data 17 mois, Stock 10 mois et Propriété 7 mois sont conservés.</p></section>')
 html.append('<section><h2>Pourquoi arrêter les itérations générales</h2><p>Règle enregistrée avant calcul : couverture, financement unique et même compteur, puis deux revues distinctes avec moins de 5 % de variation globale et moins de 10 % par unité avant arrondi. C’est une règle de pilotage de l’étude, pas une norme de précision COCOMO.</p>')
 rows=[]
 for i in [5,6,7,8]:
  x=read(OUT/f'iteration-{i:02}/results.json');pct=next((s['unrounded_total_change_pct'] for s in st['transitions'] if s['next']==i),None)
  rows.append([str(i),str(x['progress']['complete_proposed_capabilities'])+'/88',n(x['cumulative']['complete_proposed_jh'])+' JH' if x['cumulative']['complete_proposed_jh'] else 'Total complet non défendable',n(pct,3)+' %' if pct is not None else 'Nouveau périmètre'])
 html.append(table(['Itération','Périmètre chiffré','Total complet','Variation avant arrondi'],rows))
 html.append('<p>La revue 7 a retiré de la construction native un préremplissage de contrôle qualité utilisé seulement comme analogue. La revue 8 a contrôlé le financement, les noms d’objets et les interfaces. Le total arrondi reste 4 160 JH. Sans nouvelle mesure de réalisation ou changement déterminant, continuer à lire du code n’améliorerait plus utilement le chiffre.</p><p><strong>Stabilité ne signifie pas validation empirique.</strong> Aucun bilan réel n’est disponible ; la précision prédictive reste inconnue.</p></section>')
 html.append('<section><h2>Répartition globale par rôle</h2>'+table(['Rôle','JH bruts'],[[e(x['label']),n(x['jh'])] for x in v['global_roles']]+[['<strong>Total</strong>','<strong>4 160</strong>']]))
 html.append('<p>Les tables d’activités COCOMO publiées sont conservées ; les clés vers les rôles restent proposées. Java et frontend comprennent leurs tests développeur ; QA porte la qualification indépendante. Les spécialités optimisation et moteur sont à réunir à l’intérieur des budgets Java, architecture et QA ; leur disponibilité n’est pas confirmée.</p><p><a href="jh-par-role.csv">Télécharger les neuf unités avec rôles et délais (CSV)</a></p></section>')
 html.append('<section><h2>Quatre références natives des nouveaux périmètres</h2><p>Ces valeurs concernent les 72 capacités nouvellement évaluées, sans les trois décisions Java/Spring retenues. Ce sont des coûts modélisés dans chaque technologie, pas des bilans réellement consommés.</p>')
 html.append(table(['Unité','ERPNext + Frappe','Odoo','Tryton','Axelor / Platform / Studio'],[[e(g['name'])]+[n(next(x['rounded_jh'] for x in g['rows'] if x['id']==p)) for p in ['erpnext','odoo','tryton','axelor']] for g in r['economic_units']]+[['<strong>Nouveaux périmètres uniquement</strong>']+[n(r['new_native_subtotals'][p]) for p in ['erpnext','odoo','tryton','axelor']]]))
 html.append('<p>Les écarts restent importants en planification : les analogues natifs et leurs chaînes diffèrent. Les quatre résultats ne valident pas une productivité identique entre langages. La référence Java s’appuie sur les analogues Java, sans moyenne des quatre ni supplément de transposition Spring. Les hypothèses de nouveaux modules étant partagées, les résultats ne sont pas indépendants.</p></section>')
 html.append('<section><h2>Confrontation COSMIC × ISBSG</h2><p>Six comptages proposés reprennent les frontières des unités. Deux événements alimentant plusieurs modules internes sont fusionnés. Les interfaces empêchent de présenter la simple somme des CFP comme un comptage certifié du Core.</p>')
 html.append(table(['Unité','CFP','COCOMO Java avant arrondi','COSMIC × ISBSG','Comparaison à COCOMO'],[[e(g['name']),str(g['COSMIC']['CFP']),n(next(x['jh'] for x in g['rows'] if x['id']=='axelor'),2),n(g['COSMIC']['jh'],2),('Plus haut de ' if g['COSMIC']['alignment_vs_java']['gap_pct']>0 else 'Plus bas de ')+n(abs(g['COSMIC']['alignment_vs_java']['gap_pct']),1)+' %'] for g in r['economic_units']]))
 html.append('<p>Le contrôle conserve 20 h/CFP, facteur 1 et 7 h/JH avec les mêmes activités projet. Ce rendement historique n’est pas calibré au réemploi. COSMIC compte les mouvements de données, sans mesurer directement la difficulté des contraintes ni le code spécialisé des contrats ; COCOMO dépend des tailles supposées. Ces différences donnent des explications plausibles, sans prouver leurs amplitudes. ISBSG valorise COSMIC : ce n’est pas une troisième estimation indépendante.</p></section>')
 html.append('<section><h2>Hypothèses qui peuvent encore changer le résultat</h2><p>Impacts calculés par modification explicite de volumes, toutes choses égales par ailleurs. Ni probabilités ni fourchette garantie ; l’incertitude des décisions retenues n’est pas réestimée.</p>')
 html.append(table(['Hypothèse modifiée','Impact brut','Base'],[[e(s['label']),'+'+n(s['rounded_delta_jh'])+' JH',e(s['basis'])] for s in sens['results']]))
 html.append('<ul>'+''.join('<li>'+e(x)+'</li>' for x in assumptions)+'</ul></section>')
 html.append('<section><h2>Financement et garanties partagés</h2><p>Le registre contient 70 mécanismes/modules, chacun avec un propriétaire. Les onze mécanismes communs restent dans les lots qui les portent ; leurs consommateurs ne les reconstruisent pas. Les règles Beaumanoir et ses connecteurs restent dans l’intégration séparée.</p>')
 html.append(table(['Garantie / frontière','Responsable','Financement'],[[e(x['scope']),e(x['owner']),e(x['funding'])] for x in d['guarantees']]))
 html.append('<p>La référence BPM Java observée dans Axelor Studio appelle Camunda. Les primitives CMMN de Flowable sont documentées ; les adaptations Flow sont chiffrées sans prétendre qu’une compatibilité runtime a été testée.</p><ul>'+''.join('<li><a href="'+e(p['url'],quote=True)+'">'+e(p['id'])+'</a> : '+e(p['observed'])+'</li>' for p in d['external_primitives'])+'</ul></section>')
 html.append('<section><h2>Répartition des vingt familles</h2><p>Parts allouées selon les tailles des composants à l’intérieur de leur unité ; ce ne sont pas vingt devis indépendants ni des chiffrages par Business Capacity.</p>')
 html.append(table(['Famille','Capacités','Unité','Part JH','Périmètre'],[[e(f['name']),e(', '.join(f['capabilities'])),e(f['economic_unit']),n(f['proposed_java_jh']),e(f['scope'])] for f in r['families']])+'</section>')
 for group in r['economic_units']:
  specs=[f for f in d['families'] if f['slug'] in group['families']];rows=[]
  html.append('<section><h2>'+e(group['name'])+' — détail</h2><p>'+e(group['reason'])+'</p>')
  for f in specs:
   fr=next(x for x in r['families'] if x['slug']==f['slug']);row=next(x for x in fr['rows'] if x['id']=='axelor')
   rows.append([e(f['slug']),n(row['analogue_program_units'],1),n(f['extension_fraction'],2),str(f['quantity']),n(row['native_local_base_units']),n(row['common_equivalent_units'],1),n(row['equivalent_units'],1)])
  html.append(table(['Composant','Analogue Java','Fraction par module','Modules nouveaux','Base native','Commun intégré','Taille équivalente'],rows))
  html.append('<p>Modèles/vues et structure des services ajoutés via les gabarits mesurés. Nombres de modules et fractions sont supposés, distincts des mesures ; la somme des tailles est passée une fois dans COCOMO.</p><ul>'+''.join('<li><strong>'+e(f['slug'])+'</strong> : '+e(' ; '.join(f['module_names']))+'.</li>' for f in specs)+'</ul>')
  html.append(table(['Rôle','JH'],[[e(x['label']),n(x['jh'])] for x in group['roles']])+'<p>Délai nominal local : '+str(group['nominal_months'])+' mois, sans calendrier intégré.</p></section>')
 html.append('<section><h2>Audit final et décision d’arrêt</h2><ul>'+''.join('<li><strong>'+e(a['id']+' — '+a['status'])+'</strong> : '+e(a['result'])+'</li>' for a in audit)+'</ul><p><strong>Aucune itération générale supplémentaire recommandée avec les connaissances actuelles.</strong> Rouvrir le calcul sur : '+e(' ; '.join(closing['reopen_if']))+'.</p><p>Le modèle actif conserve 1 940 JH retenus. Ce dossier est une proposition complète, sans adoption automatique et sans modifier le référentiel, .NET, Rust ou les autres postes économiques.</p></section>')
 html.append('<section><h2>Pièces</h2><p><a href="iteration-08/results.json">Calculs complets</a> · <a href="iteration-08/inputs.json">Entrées figées</a> · <a href="iteration-08/funding.json">Financements</a> · <a href="verification.json">Contrôles indépendants</a> · <a href="stability.json">Stabilité</a> · <a href="sensitivity.json">Impacts</a> · <a href="audit-final.json">Audit final</a> · <a href="bilan.yaml">Bilan structuré</a></p></section></main></html>')
 (OUT/'synthese.html').write_text('\n'.join(html),encoding='utf-8')
 readme="""# Chiffrage complet Java/Spring — étude d’opportunité
Proposition : 4 160 JH bruts, dont 1 940 déjà retenus et 2 220 nouveaux.
Les 280 JH communs sont intégrés : ne pas les ajouter.
88/88 capacités chiffrées pour l’étude ; 16/88 adoptées dans le modèle actif.
Lire synthese.html, audit-final.json, stability.json et sensitivity.json.
Les rôles et délais des neuf unités figurent dans jh-par-role.csv.

## Reproduction depuis la racine du projet
Avec les dépendances Python du modèle :
1. python audits/2026-10-30-chiffrage-complet/calculate-05.py 5
2. python audits/2026-10-30-chiffrage-complet/calculate-06-07.py 6
3. python audits/2026-10-30-chiffrage-complet/calculate-06-07.py 7
4. python audits/2026-10-30-chiffrage-complet/calculate.py 8
5. python audits/2026-10-30-chiffrage-complet/verify.py
6. python audits/2026-10-30-chiffrage-complet/report.py

prepare.py, review6.py, review7.py et review8.py reconstruisent les entrées séquentiellement depuis les preuves précédentes. Les sorties sont déjà figées ; ne pas les écraser pour modifier une hypothèse.
Les règles sont celles du métamodèle canonique. Le bilan YAML est un résultat d’audit, pas un autre métamodèle.
La stabilité ne prouve pas la précision prédictive : aucun bilan réel n’est disponible.
"""
 (OUT/'README.md').write_text(readme,encoding='utf-8')
 save(OUT/'iteration-08/analysis.json',dict(results_sha256=sha(OUT/'iteration-08/results.json'),verification_sha256=sha(OUT/'verification.json'),decision='Arrêt : couverture, financements et deux revues stables ; impacts explicités.',next_iteration_worthwhile_without_new_evidence=False,remaining_hypotheses=assumptions))
 print(json.dumps(dict(total_jh=4160,adopted_jh=1940,new_proposed_jh=2220,scope='88/88',stop=True)))
if __name__=='__main__':main()
