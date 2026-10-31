"""Review boundaries/guarantees and freeze iteration 7; no effort coefficients adjusted."""
from pathlib import Path
import json,hashlib,copy
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 d=read(OUT/'iteration-06/inputs.json');r=read(OUT/'iteration-06/results.json')
 findings=[
 dict(id='R6-01',finding='Premier chiffrage complet sur six unités cohérentes. La part commune est intégrée dans leurs tailles, jamais ajoutée une seconde fois.',result=r['cumulative']),
 dict(id='R6-02',finding='Les contrôles COSMIC précédents avaient des frontières par famille ; il faut rétablir celles des six unités et fusionner les effets du même événement reçu.',action='Fusion ciblée de deux paires de processus, groupes de données et mouvements explicites ; pas de moyenne avec COCOMO.'),
 dict(id='R6-03',finding='Le préremplissage d’un contrôle qualité chez un exécutant n’est pas une construction native de la décision de devenir.',action='Consommer le code natif qualité comme analogue seulement ; la nouvelle décision reste financée par son module de contribution.'),
 dict(id='R6-04',finding='Disponibilité, réservation physique, admission, journal métier et historique moteur ont des propriétaires distincts.',action='Matrice de garanties transversales explicitant consommation et adaptations nouvelles ; aucun poste global de risque ou de pilotage ajouté.'),
 dict(id='R6-05',finding='Les rôles Stock sont une hypothèse d’organisation ; les travaux de calcul exigent une compétence optimisation et les travaux de processus une compétence moteur.',action='Identifier ces spécialités à l’intérieur des JH Java/architecture/QA, sans créer un second budget ni présumer les ressources disponibles.')
 ]
 save(OUT/'iteration-06/analysis.json',dict(results_sha256=sha(OUT/'iteration-06/results.json'),decision='Continuer : revue des frontières et garanties',findings=findings))
 for f in d['families']:
  for b in f['bindings']:
   if '/axelor-quality/' in '/'+b['path'] or 'quality_inspection' in b['path'] or b['path'].endswith('modules/quality/quality.py'):b['provided_kernel']=True
 aliases={'GoodsServiceRequirement':'ServiceRequirement','GoodsServiceCommitment':'ServiceCommitment','GoodsServiceResult':'ServiceResult','OperationFact':'ServiceFact'}
 merging={'services':[('goods-orders-P03','assurance-P01','service-result-received','Enregistrer et qualifier le résultat reçu de prestation','ServiceResult')],'processes':[('workflow-P03','supervision-P04','case-event-received','Historiser le fait métier et qualifier la réaction autorisée','CaseEvent')]}
 def norm(name):return aliases.get(name,name)
 for unit in d['economic_units']:
  processes=[];groups={}
  for family in unit['families']:
   c=read(ROOT/f'audits/2026-10-30-familles-restantes/{family}/cosmic-2.json')
   for g in c['groups']:
    name=norm(g['id'])
    if name not in groups:groups[name]=dict(id=name,object_of_interest=name,attributes=[])
    groups[name]['attributes']=sorted(set(groups[name]['attributes']+g['attributes']))
   for p in c['processes']:
    p=copy.deepcopy(p);p['origin_processes']=[p['id']]
    for m in p['movements']:m['group']=norm(m['group'])
    processes.append(p)
  for a,b,new,label,trigger in merging.get(unit['id'],[]):
   pair=[p for p in processes if p['id'] in [a,b]];assert len(pair)==2
   merged=copy.deepcopy(pair[0]);merged.update(id=new,label=label,origin_processes=[a,b],trigger='Réception du fait métier unique à la frontière de cette unité.',capabilities=sorted(set(sum([p['capabilities'] for p in pair],[]))))
   pairs={(m['type'],m['group']) for p in pair for m in p['movements'] if m['type']!='E'};pairs.add(('E',trigger))
   merged['movements']=[dict(type=t,group=g,cfp=1) for t,g in sorted(pairs)]
   if trigger not in groups:groups[trigger]=dict(id=trigger,object_of_interest=trigger,attributes=['reference','scope','businessAttributes'])
   processes=[p for p in processes if p['id'] not in [a,b]]+[merged]
  for p in processes:
   distinct={(m['type'],m['group']) for m in p['movements']}
   p['movements']=[dict(id=p['id']+'-'+t+'-'+g,type=t,group=g,cfp=1) for t,g in sorted(distinct)]
   p['functional_user']='Producteur autorisé, opérateur ou composant extérieur à cette unité cohérente.'
  ref=f'audits/2026-10-30-chiffrage-complet/iteration-07/cosmic-{unit["id"]}.json'
  save(ROOT/ref,dict(id=unit['id'],boundary=unit['name'],groups=list(groups.values()),processes=processes,CFP=sum(len(p['movements']) for p in processes),unit='CFP',hours_per_CFP=20,factor=1,day_hours=7,review='Revue statique proposée ; pas certification ni calibration historique de Flow.',merge_reasons='Deux événements ne sont pas comptés deux fois parce qu’ils alimentent plusieurs modules internes.',not_global_core_count=True))
  unit['cosmic_ref']=ref
 d['guarantees']=[
 dict(id='admission-authority',scope='Droits, autorité, version attendue, admission causale/idempotente',owner='Master Data retenu',consumers='Toutes les unités',funding='consommé ; adaptations des contrats incluses dans les modules métier'),
 dict(id='physical-stock',scope='Mouvements, corrections, concurrence et réservation physique',owner='Stock retenu',consumers='Commandes, promesse, allocation, prestations',funding='aucune reconstruction des mouvements ; décision et demande de réservation financées dans décisions'),
 dict(id='ownership-history',scope='Propriété et lectures aux deux dates',owner='Propriété du stock retenue',consumers='Consignation, devenir et commandes',funding='consommé ; pas second registre de quantité'),
 dict(id='business-case-history',scope='Faits et corrections des dossiers aux deux dates, origine et reconstitution',owner='Processus/supervision',consumers='Vues, intelligence, interventions',funding='case-ledger de la part commune et projection locale incluses ; distinct de l’historique technique moteur'),
 dict(id='reaction-recovery',scope='Déclenchement causal, reprise et preuve de l’effet métier',owner='Processus',consumers='Prestations, coordination et travail humain',funding='ReactiveDispatch, contrats du moteur et admission commune ; livraison technique répétable, effet métier dédupliqué'),
 dict(id='solver-contract',scope='Entrées figées, objectifs/contraintes, arrêt, résultat et limites de faisabilité',owner='Décisions/optimisation',consumers='Plan, affectation, promesse, transport',funding='un adaptateur de calcul + modèles métier énumérés ; noyaux externes non reconstruits'),
 dict(id='scenario-application',scope='Isolation des scénarios et application sous autorité sans effets de simulation',owner='Préparation/pilotage du plan',consumers='Décisions et coordination',funding='module de scénarios + PlanApplication ; admission générique consommée'),
 dict(id='UI-observability',scope='Écrans métier de consultation/édition, explications, instrumentation et tests',owner='Chaque unité pour ses modules',consumers='Opérateurs et développeurs',funding='modèles/vues des schémas et rôles frontend/QA/plateforme ; aucun second studio UI universel'),
 dict(id='integration-boundary',scope='API génériques de prestataire ; ni connecteurs Beaumanoir, ni paramètres propres au Groupe',owner='Core pour contrats génériques ; intégration Beaumanoir séparée',consumers='Prestations et systèmes aval',funding='contrats génériques inclus ; intégration Groupe préservée, non utilisée comme budget caché du Core')
 ]
 d['role_specialties']={'decisions':{'dev_java':'Développement Java incluant modélisation d’optimisation et algorithmes ; compétence à réunir.','architecture':'Architecture des calculateurs et de leurs contrats.','qa':'Tests d’invariants, faisabilité et cas sans solution, dans le budget QA.'},'processes':{'dev_java':'Développement Java incluant adaptation Flowable et projections de journal.','qa':'Reprise, duplication, corrections temporelles et droits dans le budget QA.'}}
 save(OUT/'iteration-07/inputs.json',d)
 save(OUT/'iteration-07/freeze.json',dict(inputs_sha256=sha(OUT/'iteration-07/inputs.json'),analysis6_sha256=sha(OUT/'iteration-06/analysis.json'),cosmic_sha256={u['id']:sha(ROOT/u['cosmic_ref']) for u in d['economic_units']},before_effort=True))
 print('Iteration 7 frozen: rebased functional counts, funding and guarantees reviewed.')
if __name__=='__main__':main()
