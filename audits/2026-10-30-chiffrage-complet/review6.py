"""Analysis after iteration 5 and the frozen inputs for iteration 6."""
from pathlib import Path
import json,hashlib,copy,importlib.util
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=importlib.util.spec_from_file_location('prep',OUT/'prepare.py');prep=importlib.util.module_from_spec(s);s.loader.exec_module(prep)
def main():
 old=read(OUT/'iteration-05/results.json')
 save(OUT/'iteration-05/analysis.json',dict(result_sha256=sha(OUT/'iteration-05/results.json'),decision='Continuer : pas encore de total complet',findings=[
 dict(id='R5-01',fact='Le filtre vide est interprété comme une exclusion universelle, pas absence de filtre. Corriger la sélection des lectures.',affected=['supervision','intelligence']),
 dict(id='R5-02',fact='Les méthodes confirm/cancel de MrpForecast ne mesurent pas la consommation de prévision ; une décision de devenir ne se réduit pas à préremplir un contrôle qualité.',action='Utiliser un composant de projection/réconciliation cohérent et un journal de décision comme analogues explicites.'),
 dict(id='R5-03',fact='Les fractions héritées dimensionnent des compléments, mais un seul module implicite ne couvre pas plusieurs nouveaux calculateurs distincts.',action='Énumérer les modules de responsabilité et leurs modèles ; ne pas multiplier automatiquement par nombre de capacités.'),
 dict(id='R5-04',fact='Les 20 petites unités et leurs composants communs forment six ensembles couplés.',action='Calcul COCOMO une seule fois par ensemble ; conserver les répartitions par Business Area comme allocations et non calculs indépendants.'),
 dict(id='R5-05',fact='Les sources de facture et paiement appartiennent au système externe ; Flow porte demandes/reconnaissance.',action='Retirer leur construction de la base native, conserver les adaptations Flow dimensionnées.')
 ],no_full_total=old['cumulative']['complete_proposed_jh'] is None,progress=old['progress']))
 d=read(OUT/'iteration-05/inputs.json');catalog=read(OUT/'source-catalog.json');families={f['slug']:f for f in d['families']}
 modules={
 'eligibility':['restrictions et contrôle motivé'],
 'policies':['activation et explication des politiques'],
 'disposition':['options et décision de devenir'],
 'orders':['accords de consignation et reprises','résolution des retours client/fournisseur','rapprochement des engagements et résultats'],
 'master-plan':['contributions qualifiées et contexte net','calcul de couverture et application contrôlée','scénarios isolés et comparaison'],
 'plan-preparation':['qualification de prévision','consommation sans double besoin','projection des apports','rapprochement des plans'],
 'backlog':['priorisation','affectation sous contraintes','libération des livraisons'],
 'optimization':['cibles physiques','protections logiques','politique de réservation','réapprovisionnement','redistribution'],
 'promising':['disponibilité promettable','faisabilité matières/capacités','valorisation des possibilités'],
 'service-planning':['offres de capacité qualifiées','sélection de service sous politique','ordonnancement des transports'],
 'coordination':['dépendances de satisfaction','adaptation des engagements','libération des services'],
 'assurance':['faits et corrections spécialisés','vues de résultat et rapprochements typés'],
 'goods-orders':[s['name'] for s in families['goods-orders']['schemas']],
 'transport-orders':['instructions de déplacement','réservation autonome de capacité'],
 'customs':['dossier de prestation douanière'],
 'financial-services':['facture et avoir demandés/reconnus','encaissement et remboursement demandés/reconnus'],
 'workflow':['composition contextuelle','réaction métier corrélée au moteur'],
 'human-work':['formulaire/résultat contextualisé','politique métier d’attribution'],
 'supervision':['projection croisée des dossiers'],
 'intelligence':['reconstitution et variantes de parcours','indicateurs et vues Supply']
 }
 additional=[]
 def binding(repo,path,pattern,provided=True,exclude=r'(?!)'):
  file=prep.m.load_file(repo,path,catalog);atoms,methods=prep.m.select(file,pattern,exclude)
  if file['root_path'] not in {x['root_path'] for x in catalog['sources']}:
   catalog['sources'].append({k:v for k,v in file.items() if k not in ('text','atoms','methods')})
  return dict(repo=file['repo'],product=file['product'],path=file['path'],root_path=file['root_path'],sha256=file['sha256'],pattern=pattern,excluded_pattern=exclude,provided_kernel=provided,atoms=atoms,methods=methods)
 for f in d['families']:
  for i,b in enumerate(f['bindings']):
   if b['excluded_pattern']=='':f['bindings'][i]=binding(b['repo'],b['path'],b['pattern'],b['provided_kernel'])
   elif f['slug']=='promising':f['bindings'][i]=binding(b['repo'],b['path'],b['pattern'],b['provided_kernel'],'tax|vat|valuation|accounting|analytic|wap|print|pdf|csv|migration|send.*mail')
  f['module_names']=modules[f['slug']];f['quantity']=len(f['module_names']);f['quantity_reason']='Modules de responsabilité distincts énumérés après lecture du périmètre ; les vues et variantes partagent leurs composants.'
  if f['slug']=='financial-services':
   for b in f['bindings']:b['provided_kernel']=True
 def banks(slug):
  f=families[slug];units={p:set() for p in ['erpnext','odoo','tryton','axelor']}
  for b in f['bindings']:
   for a in b['atoms']:units[b['product']].add((b['repo'],b['path'],a['key']))
  return {p:len(x) for p,x in units.items()}
 # Forecast qualification/consumption is compared with the coherent net-planning module, not its 22-unit state service.
 families['plan-preparation']['analogue_provider']=dict(id='net-planning-component',units=banks('master-plan'),basis='Projection/rapprochement de quantités et versions ; bibliothèque de calcul du plan net consommée, quatre adaptations de contexte distinctes.')
 correction=read(ROOT/'audits/2026-10-30-mecanismes-partages-04/measurements.json')['stock_correction_reference']
 families['disposition']['analogue_provider']=dict(id='versioned-decision-journal',units=correction,basis='Une décision avec origine, corrections et rapprochement, comparable à la chaîne de contribution ; aucune exécution Stock reconstruite.')
 # A margin calculation was incorrectly excluded although valuation is in the native scope.
 p=families['promising']
 for b in families['service-planning']['bindings']:p['bindings'].append(dict(b,provided_kernel=True))
 for b in families['master-plan']['bindings']:
  if b['product']=='axelor' and b['path'].endswith('MrpLineServiceImpl.java'):
   p['bindings'].append(binding(b['repo'],b['path'],'generateProposal|generatePurchaseProposal|createOrUpdatePurchaseOrderLine',True))
 families['customs']['additional_modules']=[dict(id='customs-dossier-checks',units=correction,fraction=.8,basis='Suivi des pièces manquantes et corrections du dossier comme une chaîne de contribution ; le stockage de fichiers est fourni.')]
 families['intelligence']['additional_modules']=[dict(id='trace-sequence-analysis',units=correction,fraction=.8,basis='Reconstruction déterministe des séquences et corrections du journal ; pas algorithme de découverte généralisée ni apprentissage.')]
 # Common solver/application execution wrapper is financed once in optimization.
 families['optimization']['additional_modules']=[dict(id='solver-run-contract',units=banks('service-planning'),fraction=1,basis='Contrat entrées/résultats/limites, arrêt et comparaison de solveurs ; pas reconstruction OR-Tools/Timefold.')]
 d['economic_units']=[
 dict(id='controls',name='Politiques, éligibilité et devenir des biens',families=['eligibility','policies','disposition'],reason='Décisions opérationnelles sous règles et autorité, partage de références versionnées.'),
 dict(id='orders',name='Gestion des commandes',families=['orders'],reason='Cycle, filiation, variantes contractuelles et rapprochement des commandes.'),
 dict(id='planning',name='Préparation et pilotage du Master Plan',families=['master-plan','plan-preparation'],reason='Contributions, projections, couverture, scénarios et application partagent le modèle de plan.'),
 dict(id='decisions',name='Promesse, affectation et optimisation Supply',families=['backlog','optimization','promising','service-planning','coordination'],reason='Même contrat de décision et de capacité ; calculateurs distincts, un adaptateur de solveurs.'),
 dict(id='services',name='Prestations et reconnaissance des résultats',families=['assurance','goods-orders','transport-orders','customs','financial-services'],reason='Exigences confiées, engagements, instructions typées et résultats reconnus partagent le même cycle.'),
 dict(id='processes',name='Processus, travail humain et supervision',families=['workflow','human-work','supervision','intelligence'],reason='Même moteur, dossiers, contrats de tâche, journal, projections et analyse de traces.')
 ]
 d['grouping_note']='Les familles reçoivent une allocation du coût de leur unité cohérente. Le total ne somme pas vingt estimations COCOMO de fragments ni les 280 JH de la part commune.'
 d['external_primitives']=[
 dict(id='Flowable-CMMN',url='https://www.flowable.com/open-source/docs/cmmn/ch06-cmmn',observed='Critères/sentries, plan items et événements fournis. Adaptation aux contrats Flow, autorité, corrélation et garanties temporelles à réaliser.',not_a_runtime_test=True),
 dict(id='Flowable-API',url='https://www.flowable.com/open-source/docs/cmmn/ch03-API',observed='Services runtime, tâches et historique. Cet historique ne démontre pas le journal métier à deux dates de Flow.'),
 dict(id='OR-Tools-Java',url='https://developers.google.com/optimization/introduction/java',observed='Primitives de contraintes, affectation et routage disponibles ; objectifs et données Flow non fournis.'),
 dict(id='Timefold-1.x',url='https://docs.timefold.ai/timefold-solver/1.x/using-timefold-solver/modeling-planning-problems',observed='Modèles/variables et contraintes applicatifs requis ; noyau de recherche réutilisé.')
 ]
 save(OUT/'iteration-06/source-catalog.json',catalog)
 save(OUT/'iteration-06/inputs.json',d)
 save(OUT/'iteration-06/freeze.json',dict(inputs_sha256=sha(OUT/'iteration-06/inputs.json'),catalog_sha256=sha(OUT/'iteration-06/source-catalog.json'),analysis5_sha256=sha(OUT/'iteration-05/analysis.json'),before_effort=True))
 print('Iteration 6 inputs frozen; six coherent economic units; no effort calculated.')
if __name__=='__main__':main()
