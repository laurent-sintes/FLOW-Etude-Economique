"""Independent arithmetic, lineage, source and coverage audit of the three-pass campaign."""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction
from decimal import Decimal,ROUND_HALF_UP
import hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tmp/model-deps'))
import yaml
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def halfup(v,step):return float((Decimal(str(v))/Decimal(str(step))).quantize(Decimal('1'),rounding=ROUND_HALF_UP)*Decimal(str(step)))
def main():
 plan=read(OUT/'plan.json');baseline=read(OUT/'baseline.json')
 native=read(ROOT/'audits/2026-10-30-propriete-stock-calcul-02/inputs.json')
 source=read(ROOT/'audits/2026-10-30-master-data-calcul/repartitions-sources.json')['cocomo']
 alloc=read(ROOT/'audits/2026-10-30-stock-consolidation-09/inputs.json')
 catalogue=yaml.safe_load((ROOT/'source/analyse-perimetre-core.yaml').read_text(encoding='utf-8'))['blocs']
 paid={c['id'] for u in baseline['units'] for c in u['capabilities']}
 allcaps=set();proofs={};codepaths={};owners=defaultdict(set);findings=[];rows=[];iterations=analyses=0;arithmetic_checks=0
 for f in plan['families']:
  folder=OUT/f['slug'];one=read(folder/'iteration-1.json');two=read(folder/'iteration-2.json');three=read(folder/'iteration-3.json')
  inp2=read(folder/'entrees-2.json');inp3=read(folder/'entrees-3.json');cosmic=read(folder/'cosmic-2.json')
  assert not allcaps.intersection(f['capabilities']);allcaps.update(f['capabilities'])
  assert not paid.intersection(f['capabilities'])
  for num in (1,2,3):
   p=folder/f'iteration-{num}.json';x=read(p);assert x['iteration']==num and x['family']==f['id'];iterations+=1
  for num in (1,2):
   x=read(folder/f'analyse-{num}.json');assert x['after_iteration']==num and x['family']==f['id'];analyses+=1
  for name,key in [('iteration-1.json','iteration_1_sha256'),('analyse-1.json','analysis_1_sha256'),('iteration-2.json','iteration_2_sha256'),('analyse-2.json','analysis_2_sha256'),('entrees-3.json','inputs_3_sha256')]:
   assert sha(folder/name)==three['lineage'][key]
  assert sha(folder/'entrees-2.json')==read(folder/'gel-2.json')['inputs_sha256']
  assert sha(folder/'cosmic-2.json')==read(folder/'gel-2.json')['cosmic_sha256']
  assert sha(folder/'entrees-3.json')==read(folder/'gel-3.json')['inputs_sha256']
  groups={g['id'] for g in cosmic['groups']};assert len(groups)==len(cosmic['groups'])
  ids=set();count=Counter()
  for p in cosmic['processes']:
   keys=set();types=Counter()
   for m in p['movements']:
    assert m['id'] not in ids and (m['type'],m['group']) not in keys
    assert m['group'] in groups and m['type'] in 'ERWX' and m['cfp']==1
    ids.add(m['id']);keys.add((m['type'],m['group']));types[m['type']]+=1
   assert types['E']>0 and types['W']+types['X']>0;count.update(types)
  assert sum(count.values())==cosmic['CFP']==three['functional_control']['CFP']
  assert dict(count)==cosmic['movements']
  assert math.isclose(20*cosmic['CFP']/7,three['functional_control']['jh'])
  c=inp2['cocomo'];E=c['B']+.01*c['SF_sum'];F=c['D']+.2*(E-c['B'])
  for iteration,data,banks,checkrows in [(2,inp2,inp2['native_reference_banks'],two['rows']),(3,inp3,inp3['native_reference_banks'],three['native_estimates'])]:
   for row in checkrows:
    if row.get('jh') is None:continue
    p=row['id'];bank=banks[p];t=native['schema_templates'][p];scaffold=native['new_module_scaffolding'][p]['program_units_per_new_service_module']
    schemas=inp2['schemas']
    models=sum(len(s['fields'])*t['program_per_field']+t.get('program_per_new_model',0)+len(s['fields'])*t['declarations_per_field']+t['per_new_model']+len(s['fields'])*t['view_field']+t['view_model'] for s in schemas)
    size=bank*(inp2['attribution']+inp2['new_complement_fraction'])+scaffold+models
    expected=c['A']*(size/1000)**E*c['other_EM']*c['SCED']*c['month_hours']/c['day_hours']*c['effort_phase_factor']
    assert math.isclose(size,row['equivalent_units'],rel_tol=1e-12)
    assert math.isclose(expected,row['jh'],rel_tol=1e-12)
    assert halfup(expected,10)==row['rounded_jh'];arithmetic_checks+=1
  for s in inp3['source_measures']:
   path=ROOT/s['root_path'];assert sha(path)==s['sha256'];codepaths[s['root_path']]=s['sha256']
   nodes={tuple(x) for x in s['nodes']};assert len(nodes)==len(s['nodes'])==s['program_units']
   owners[(s['product'],s['path'])].add(f['slug'])
  total=three['diagnostic_rounded_jh'];role={r['id']:Fraction(0) for r in three['roles']}
  phases=source['phase_effort_percent_of_base']
  for a in source['activities']:
   share=sum(Fraction(x*y) for x,y in zip(phases,a['percent_by_phase']))/sum(phases)/100
   for key,w in alloc['activity_role_weights'][a['id']].items():role[key]+=Fraction(total)*share*Fraction(str(w))
  assigned={k:int(v//1) for k,v in role.items()};order=sorted(role,key=lambda k:(-(role[k]-int(role[k]//1)),k))
  for k in order[:total-sum(assigned.values())]:assigned[k]+=1
  assert assigned=={r['id']:r['jh'] for r in three['roles']}
  months=c['C']*(total/c['effort_phase_factor']*c['day_hours']/c['month_hours']/c['SCED'])**F*c['schedule_phase_factor'] if total else None
  assert months is None or math.isclose(months,three['delay']['calculated_months'],rel_tol=1e-12)
  if months:assert halfup(months,1)==three['delay']['rounded_months']
  rows.append(dict(family=f['id'],name=f['name'],slug=f['slug'],capabilities=f['capabilities'],
   status=three['status'],native_rounded_jh={r['id']:r.get('rounded_jh') for r in three['native_estimates']},
   candidate_java_jh=three['proposed_java_jh'],diagnostic_java_jh=total,local_months=three['delay']['rounded_months'],
   COSMIC_jh=three['functional_control']['jh'],CFP=cosmic['CFP'],
   targeted_callees_verified=three['measured_change']['resolved_direct_calls'],
   unresolved_delegations=three['measured_change']['remaining_delegations'],
   numeric_agreement_is_not_acceptance=True))
  for p in folder.iterdir():
   if p.is_file():proofs[p.relative_to(ROOT).as_posix()]=sha(p)
 assert len(allcaps)==72 and allcaps|paid=={b['id'] for b in catalogue}
 assert iterations==60 and analyses==40
 for p,h in baseline['source_hashes'].items():assert sha(ROOT/p)==h,p
 assert yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))['units']==baseline['units']
 overlaps=[dict(product=p,path=path,families=sorted(fs)) for (p,path),fs in owners.items() if len(fs)>1]
 candidates=[r for r in rows if r['candidate_java_jh'] is not None]
 blocked=[r for r in rows if r['candidate_java_jh'] is None]
 # Audit findings concern decision usefulness, not just whether 60 report files exist.
 findings=[
 dict(id='A01',priority='haute',subject='Périmètres comparables et délégations',
  observation='La troisième itération élargit les mesures, mais ne ferme que des appels Java directs ; héritage et modules dynamiques Python/Odoo/Tryton restent partiellement isolés.',
  consequence='Les quatre chiffres sont des diagnostics conditionnels ; pas quatre coûts natifs établis sur un périmètre identique.',
  missing_iteration='I4 par famille : remplacer les paquets trop larges ou trop courts par une chaîne métier cohérente et enregistrer les inclusions/exclusions. Ne pas viser un nombre de lignes cible.'),
 dict(id='A02',priority='haute',subject='Financement unique entre familles',
  observation=f'{len(overlaps)} fichiers natifs servent de référence à plusieurs familles. Cela ne prouve pas à lui seul un double compte, car un analogue peut dimensionner du code nouveau distinct.',
  consequence='La campagne ne porte pas encore le registre fermé des nouveaux mécanismes partagés. Une somme globale des diagnostics ne serait pas défendable.',
  missing_iteration='I4 transversale : attribuer un propriétaire aux cycles Order, contrats de prestation, décisions et moteur de Case ; distinguer consommation et adaptation spécifique.'),
 dict(id='A03',priority='haute',subject='Cohérence de la mesure de taille',
  observation='Les diagnostics utilisent une union de méthodes et des modèles proposés. Les décisions adoptées combinent des mesures de composants, des structures et des ajustements de réutilisation différents.',
  consequence='La correspondance avec les unités équivalentes du modèle adopté doit être réconciliée avant de retenir les nouveaux JH. Une formule exacte ne valide pas la taille d’entrée.',
  missing_iteration='I4 transversale : réconcilier corps de méthodes, déclarations, modèles/vues et services réutilisés ; vérifier explicitement la continuité avec les trois décisions adoptées.'),
 dict(id='A04',priority='haute',subject='Compléments Flow non appariés',
  observation='Optimisation, ATP/CTP/PTP, planification de services, coordination, douane, orchestration, supervision temporelle et mining restent insuffisamment appariés.',
  consequence='Huit familles gardent proposed_java_jh = null ; les diagnostics calculés ne sont pas des propositions à retenir.',
  missing_iteration='I4 ciblées : modèle de contraintes local réutilisant OR-Tools/Timefold ; CTP/PTP combinés ; capacités/offres de service ; booking/douane comme ordres confiés ; composition Flowable et journal de Case ; séquences corrigées pour mining.'),
 dict(id='A05',priority='moyenne',subject='Comptage COSMIC',
  observation='Les mouvements sont explicités et recomptés. Les couvertures de variantes et sous-contrats sont proposées, sans validation de leur exhaustivité ; les frontières de composants rendent le cumul des CFP invalide sans retrait des interfaces.',
  consequence='Le rendement historique de 20 h/CFP reste un contrôle non calibré. Son écart ne peut pas trancher seul entre les diagnostics de code.',
  missing_iteration='I4 fonctionnelle : revoir les variantes de consignation/retour, les douze contrats de prestation et les corrections ; contrôler les doubles groupes et les interfaces entre composants.'),
 dict(id='A06',priority='moyenne',subject='Rôles et délais',
  observation='Rôles et délais sont calculés depuis les diagnostics ; les clés Stock sont reprises pour toutes les familles, y compris algorithmes, tâches humaines et processus. Certains diagnostics de 10 JH produisent trois mois locaux : cette extrapolation ne décrit pas le calendrier d’un composant mutualisé dans le programme.',
  consequence='Ces répartitions ne constituent pas encore une organisation consolidée ; certains besoins spécialisés sont insuffisamment distingués.',
  missing_iteration='Après stabilisation des tailles : regrouper les petites unités au bon niveau, répartir expertise optimisation/processus, Java, interface, QA et sécurité, puis vérifier le calendrier d’une équipe mutualisée. Garder les distributions publiées et les diagnostics locaux distincts.'),
 ]
 specific={
  'eligibility':'Fermer le blocage fournisseur/prestataire et son appelant. Remplacer l’avertissement Odoo par un véritable refus ou le classer comme complément.',
  'policies':'Vérifier activation/version/portée et explication de politique ; ne pas reprendre les algorithmes d’application.',
  'disposition':'Isoler la décision sur les usages et la comparaison de récupération de valeur, distinctes de l’inspection et de l’exécution.',
  'orders':'Fermer les lignées de commandes/quantités, consignations et retours ; partager le cycle générique avec les ordres de prestation.',
  'master-plan':'Séparer netting, application autorisée, simulation et calculateurs consommés. Éviter de financer les mêmes calculs dans trois familles.',
  'plan-preparation':'Vérifier consommation de prévision par commandes et réconciliation de versions ; le service de seuils n’est pas cet algorithme.',
  'backlog':'Séparer priorité, choix de ressource et libération ; ne pas reconstruire la réservation Stock.',
  'optimization':'Mesurer l’adaptateur métier OR-Tools/Timefold et la combinaison heuristiques/contraintes sur le périmètre local prévu, sans reconstruire les solveurs.',
  'promising':'Fermer la chaîne de faisabilité CTP et la sélection économique PTP, avec dépendances à ATP, capacité et coût connu/inconnu.',
  'service-planning':'Comparer de vrais contrats de capacité reçue et des possibilités de service/transport, pas seulement un calendrier machine.',
  'coordination':'Distinguer décisions de dépendances métier et orchestration technique durable ; vérifier les actes irréversibles.',
  'assurance':'Isoler la corrélation et la reconnaissance des faits de prestation, sans réutiliser comme coût la réalisation physique Stock.',
  'goods-orders':'Contrôler les douze contrats typés, leurs informations et invariants spécifiques. Ne pas multiplier le cycle Order.',
  'transport-orders':'Fermer booking autonome, changements/libération et instructions de transport distinctes ; exclure la flotte.',
  'customs':'Construire une analogie de dossier confié et de pièces/résultat. Ne pas présenter les expéditions comme une couverture douanière native.',
  'financial-services':'Séparer demande/reconnaissance financière et moteurs fiscal/comptable/bancaire ; vérifier les montants partiels.',
  'workflow':'Mesurer les adaptations des API Flowable OSS pour composition réactive/attentes/reprise ; le cycle d’une demande d’achat ne prouve pas ce moteur.',
  'human-work':'Adapter les clés de rôles à l’interface de tâches, l’affectation contextualisée et les pauses/escalades.',
  'supervision':'Fermer le journal métier aux dates d’effet/connaissance et la remédiation attestée ; audit technique et rollback ne suffisent pas.',
  'intelligence':'Vérifier reconstruction des séquences corrigées, variantes et temps de passage sur Case Ledger ; ne pas assimiler cela à une requête SQL de reporting.'
 }
 # Stack consistency check, without changing the adopted economic model.
 stack_path=ROOT/'source/stacks/java-spring.yaml';stack_text=stack_path.read_text(encoding='utf-8')
 import re
 stack_check=dict(path='source/stacks/java-spring.yaml',sha256=sha(stack_path),
  flowable_declared=bool(re.search('flowable',stack_text,re.I)),timefold_declared=bool(re.search('timefold',stack_text,re.I)),
  ortools_declared=bool(re.search(r'or.tools|ortools',stack_text,re.I)))
 auxiliary=[]
 for e in read(ROOT/'audits/2026-10-29-experimentation-estimation/iteration-14-preuves.json')['evidence']:
  if e.get('repository')=='google/or-tools':
   assert sha(ROOT/e['local_path'])==e['sha256']
   auxiliary.append(dict(path=e['local_path'],sha256=e['sha256'],repository=e['repository'],commit=e['commit'],
    use='API de bibliothèque réutilisable ; pas coût de reconstruction du solveur ni nouvelle exécution de cette campagne.'))
 if not stack_check['ortools_declared']:
  findings.append(dict(id='A07',priority='moyenne',subject='Catalogue Java et bibliothèques de contraintes',
   observation='Flowable et Timefold sont déclarés dans la stack Java ; OR-Tools est présent dans les preuves et essais historiques mais absent de ce catalogue.',
   consequence='Le périmètre des dépendances Java n’est pas complètement aligné avec les références d’optimisation.',
   missing_iteration='Aligner le catalogue Java avec OR-Tools et son packaging natif, puis mesurer le seul adaptateur et les contraintes métier ; ne pas financer une reconstruction du solveur.'))
 backlog=[dict(family=r['family'],slug=r['slug'],next_iteration=4,task=specific[r['slug']],priorities=['A01','A02','A03']+(['A04'] if r['candidate_java_jh'] is None else []),
  candidate_jh_not_adopted=r['candidate_java_jh']) for r in rows]
 verification=dict(passed=True,requested_iterations=60,completed_iterations=iterations,completed_analyses=analyses,
  distinct_native_sources=len(codepaths),native_effort_calculations_independently_reproduced=arithmetic_checks,
  functional_counts_checked=20,role_allocations_and_schedules_checked=20,
  capabilities_reviewed=88,total_capabilities=88,reviewed_pct=100,
  retained_capabilities=16,retained_jh=1940,retained_estimates_and_sources_unchanged=True,
  candidate_families=len(candidates),candidate_capabilities=sum(len(r['capabilities']) for r in candidates),
  not_consolidable_families=len(blocked),not_consolidable_capabilities=sum(len(r['capabilities']) for r in blocked),
  estimates_ready_for_new_adoption=0,
  readiness_reason='Le registre transversal des financements et la continuité des mesures ne sont pas fermés ; aucun candidat promu automatiquement.',
  full_scope_estimated_and_validated=False,probabilistic_confidence=None)
 report=dict(id='audit-final-campagne-trois-iterations',status='audit_termine_travaux_complementaires_identifies',
  progress=verification,families=rows,findings=findings,missing_or_additional_iterations=backlog,
  source_overlap=overlaps,stack_check=stack_check,auxiliary_library_evidence=auxiliary,cumulative=dict(adopted_jh=1940,newly_adopted_jh=0,
   recommended_global_core_jh=None,reason='Pas de total global à partir de diagnostics partiels dont les mécanismes communs ne sont pas réconciliés.'),
  conclusion='Les 100 % portent sur l’examen des capacités et les trois passages demandés, pas sur une estimation consolidée de 100 % du logiciel.',
  next_iteration_worthwhile=True,recommended_next_work='Fermer d’abord le cycle Order partagé et ses contrats de prestation, puis le socle Case/Flowable/registre. Recalculer les familles consommatrices à financement unique.')
 save(OUT/'verification.json',verification);save(OUT/'audit-final.json',report)
 (OUT/'bilan.yaml').write_text(yaml.safe_dump(report,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
 plan['status']='three_iterations_and_final_audit_complete';plan['progress']=verification
 for f in plan['families']:
  f['status']='three_iterations_complete_followups_identified'
 save(OUT/'plan.json',plan)
 save(OUT/'provenance.json',dict(family_proofs=proofs,source_hashes=codepaths,protected_active_sources=baseline['source_hashes'],
  scripts={p.name:sha(p) for p in OUT.glob('*.py')},
  dependencies={p:sha(ROOT/p) for p in ['audits/2026-10-30-propriete-stock-calcul-02/inputs.json','audits/2026-10-30-stock-consolidation-09/inputs.json','audits/2026-10-30-master-data-calcul/repartitions-sources.json']}))
 print(json.dumps(verification,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
