"""Proposed COSMIC measurement under an explicit Stock opportunity-study contract."""
from pathlib import Path
import json,hashlib,sys
from collections import Counter
import yaml
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
from model_context import model_session
from estimation_calculation import formula
from capability_catalog import catalog
groups={
'FACT':('Fait de stock reconnu','Identité, produit, lieu, quantité, unité, date du fait et de connaissance, origine, correction liée.'),
'BALANCE':('État externe de stock','Source, périmètre, date, quantités connues et limite de connaissance ; pas de mouvements inventés.'),
'LINEAGE':('Lien de filiation','Biens ou lots source/destination, fait reconnu, quantité et dates.'),
'HANDLING':('Unité de manutention','Identité physique, contenant/contenu communiqués, versions et dates.'),
'RESERVATION':('Engagement de quantité','Besoin, référence de ressource, quantité réservée/consommée/libérée, période et statut.'),
'EXPECTED':('Apport attendu','Référence de commande/plan, quantité, échéance, réalisation, reliquat, fraîcheur.'),
'OWNERSHIP':('Changement de propriété reconnu','Fait détenu par le registre de propriété, sans recalcul de la décision de transfert.'),
'POSITION':('Position de stock','Produit, lieu, propriétaire, détenteur, état, date, quantités présentes/projetées et limites.'),
'VERIFICATION':('Vérification de stock','Périmètre de campagne ou contrôle, protocole, échéance, responsable et statut.'),
'COUNT':('Constat de comptage','Ligne vérification/produit/lieu, quantités attendues/constatées, dates, preuves et écart.'),
'CHECK_POLICY':('Protocole de vérification','Périmètre, campagne/tournant/ponctuel, seuils et règles déclarées ; pas moteur universel.'),
'ADJUSTMENT':('Décision de correction','Autorité, constat justifiant la correction, quantité décidée et lien au fait résultant.'),
'PLAN_DATA':('Fourniture de positions au plan','Périmètre, date, version, données de stock et limites de connaissance.'),
'FIN_DATA':('Contribution de faits à Finance','Faits transmis, justificatifs, version/corrections et état réception/acceptation/rejet.'),
'FEEDBACK':('Constat produit documenté','Produit, contexte, faits connus, preuves, corrections et destinataire ; pas cause inférée.'),
'PRODUCT':('Référence produit','Identité et caractéristiques utiles, déjà sous responsabilité Master Data.'),
'SITE':('Référence de lieu','Identité et périmètre de lieu, déjà sous responsabilité Master Data.'),
'PARTY':('Référence de partie','Identité des propriétaire/détenteur, déjà sous responsabilité Master Data.'),
'UNIT':('Référence d’unité','Unité et conversion déclarée, déjà sous responsabilité Master Data.'),
'OUTCOME':('Résultat de la demande','Acceptation/refus/erreur motivée ; un seul type de sortie de statut par processus.')}
processes=[]
def add(id,label,caps,user,trigger,E,R,W,X,assumptions=()):
 movements=[]
 for kind,names in zip('ERWX',(E,R,W,X)):
  names=names.split();assert len(names)==len(set(names)),(id,kind)
  for group in names:
   assert group in groups
   movements.append(dict(id=f'{id}-{kind}-{group}',type=kind,group=group,cfp=1))
 processes.append(dict(id=id,label=label,capabilities=caps.split(),functional_user=user,trigger=trigger,
   movements=movements,count={**{k:sum(m['type']==k for m in movements) for k in 'ERWX'},'CFP':len(movements)},
   status='processus proposé dans les hypothèses déclarées, non mesure certifiée',
   assumptions=list(assumptions)))
add('S01','Admettre des faits de stock et leurs liens','BC-009 BC-010','Source de faits autorisée','La source transmet un ensemble de faits réalisés avec liens explicitement fournis.',
 'FACT LINEAGE HANDLING','FACT PRODUCT SITE PARTY UNIT HANDLING LINEAGE','FACT LINEAGE HANDLING','OUTCOME',['H01','H02','H03'])
add('S02','Admettre un état externe daté','BC-009 BC-010','Source de stock autorisée','La source transmet un solde connu et sa portée sans historique complet.',
 'BALANCE','PRODUCT SITE PARTY UNIT BALANCE FACT','BALANCE','OUTCOME',['H01','H02'])
add('S03','Admettre une correction liée à un fait reconnu','BC-009 BC-010','Source de faits autorisée','La source corrige explicitement un fait déjà reconnu.',
 'FACT LINEAGE HANDLING','FACT BALANCE RESERVATION LINEAGE HANDLING','FACT LINEAGE HANDLING','OUTCOME',['H02','H03'])
add('S04','Consulter le registre à date','BC-010','Lecteur autorisé','Le lecteur demande les faits selon date et portée.',
 'FACT','FACT','', 'FACT OUTCOME',['H02'])
add('S05','Consulter les positions présentes et projetées','BC-011','Lecteur autorisé','Le lecteur demande une position documentée.',
 'POSITION','FACT BALANCE RESERVATION EXPECTED OWNERSHIP PRODUCT SITE UNIT','','POSITION OUTCOME',['H02','H04'])
add('S06','Consulter le détail des apports attendus','BC-011','Lecteur autorisé','Le lecteur demande échéances, avancement et reliquats des apports.',
 'EXPECTED','EXPECTED FACT RESERVATION','','EXPECTED OUTCOME',['H04'])
add('S07','Rechercher la filiation des biens','BC-011','Lecteur autorisé','Le lecteur demande les liens connus autour d’un bien ou lot.',
 'LINEAGE','LINEAGE FACT HANDLING PRODUCT','','LINEAGE FACT HANDLING OUTCOME',['H03'])
add('S08','Maintenir le protocole de vérification','BC-013','Responsable stock','Le responsable définit ou révise un protocole borné de campagne/contrôle.',
 'CHECK_POLICY','CHECK_POLICY','CHECK_POLICY','CHECK_POLICY OUTCOME',['H05'])
add('S09','Préparer une vérification','BC-013','Responsable stock','Le responsable demande une campagne ou un contrôle ponctuel.',
 'VERIFICATION','CHECK_POLICY FACT BALANCE PRODUCT SITE','VERIFICATION COUNT','VERIFICATION COUNT OUTCOME',['H05'])
add('S10','Recevoir des constats de comptage','BC-013','Exécutant du comptage','L’exécutant transmet ses constats documentés.',
 'COUNT','VERIFICATION COUNT FACT RESERVATION','COUNT VERIFICATION','COUNT OUTCOME',['H05'])
add('S11','Établir une correction justifiée','BC-013 BC-010','Autorité de correction','L’autorité accepte ou refuse un ajustement justifié par les constats.',
 'ADJUSTMENT','COUNT VERIFICATION CHECK_POLICY FACT RESERVATION','ADJUSTMENT FACT COUNT VERIFICATION','ADJUSTMENT FACT OUTCOME',['H05'])
add('S12','Consulter une vérification et ses suites','BC-013','Responsable stock','Le responsable demande constats et décisions liés à une vérification.',
 'VERIFICATION','VERIFICATION COUNT ADJUSTMENT','','VERIFICATION COUNT ADJUSTMENT OUTCOME',['H05'])
add('S13','Établir ou réviser une réservation','BC-018','Responsable du besoin','Le responsable demande un engagement de quantité ou sa révision.',
 'RESERVATION','RESERVATION FACT BALANCE PRODUCT SITE UNIT','RESERVATION','RESERVATION OUTCOME',['H06'])
add('S14','Consommer une réservation','BC-018','Responsable du besoin','Le responsable indique la consommation reliée à une réalisation déjà reconnue.',
 'RESERVATION','RESERVATION FACT','RESERVATION','RESERVATION OUTCOME',['H06'])
add('S15','Libérer ou expirer une réservation','BC-018','Responsable du besoin ou horloge métier','Une libération est demandée ou une échéance métier est atteinte.',
 'RESERVATION','RESERVATION','RESERVATION','RESERVATION OUTCOME',['H06'])
add('S16','Consulter les engagements','BC-018','Lecteur autorisé','Le lecteur demande la situation des réservations.',
 'RESERVATION','RESERVATION FACT BALANCE','','RESERVATION OUTCOME',['H06'])
add('S17','Fournir des positions à la planification','BC-012','Consommateur de planification','Le consommateur demande une fourniture de stock datée/versionnée.',
 'PLAN_DATA','FACT BALANCE RESERVATION EXPECTED OWNERSHIP','PLAN_DATA','PLAN_DATA OUTCOME',['H04','H07'])
add('S18','Fournir les faits à Finance','BC-016','Consommateur Finance','Finance demande les faits et corrections convenus pour un périmètre.',
 'FIN_DATA','FACT OWNERSHIP FIN_DATA','FIN_DATA','FIN_DATA OUTCOME',['H07'])
add('S19','Enregistrer le retour de Finance','BC-016','Consommateur Finance','Finance retourne acceptation, rejet ou référence de prise en compte.',
 'FIN_DATA','FIN_DATA','FIN_DATA','OUTCOME',['H07'])
add('S20','Préparer et transmettre un constat produit ou sa correction','BC-017','Responsable des constats terrain','Le responsable demande de fournir un constat et ses preuves aux responsables produit.',
 'FEEDBACK','FEEDBACK FACT PRODUCT','FEEDBACK','FEEDBACK OUTCOME',['H07'])
add('S21','Consulter le suivi des fournitures Finance','BC-016','Responsable des fournitures','Le responsable demande état, preuves et rejets liés aux faits transmis.',
 'FIN_DATA','FIN_DATA','','FIN_DATA OUTCOME',['H07'])
assumptions={
'H01':'Frontière mesurée : fonctionnalités du produit Core System pour Stock, au niveau fonctionnel. Interfaces sources et consommateurs externes sont les utilisateurs fonctionnels. Les raccordements propres à Beaumanoir sont exclus.',
'H02':'Faits, états externes et corrections portent identité stable, date du fait et date de connaissance. Les projections sont calculées sur demande ; elles ne sont pas un stockage supplémentaire à lire et écrire fictivement.',
'H03':'Filiations et Handling Units sont des objets reçus explicitement. Leur nombre d’occurrences, profondeur et nombre de lignes ne multiplient pas les mouvements COSMIC.',
'H04':'Les positions composent faits, états externes, engagements et apports attendus. Les données de propriété/commandes/plans sont supposées fournies par leurs producteurs, sans reconstruire ces capacités.',
'H05':'Trois modes de vérification combinables, avec protocoles paramétrés et décisions de correction explicites. Le comptage physique reste externe. Création et modification partageant le même résultat fonctionnel ne sont pas artificiellement doublées.',
'H06':'Consommation et libération sont des commandes métier distinctes de l’admission du fait réalisé. Si elles deviennent de simples étapes internes d’un autre processus, il faut fusionner les processus et recompter. Expiration et libération suivant le même traitement sont réunies.',
'H07':'Un contrat de fourniture typé par destination : planification, Finance et responsables produit. Les états métier de transmission/acceptation sont conservés ; les accusés techniques et le transport générique ne forment pas des processus supplémentaires.'}
refs={r['id']:r for r in catalog()['rows']}
covered={c for p in processes for c in p['capabilities']}
assert covered=={'BC-009','BC-010','BC-011','BC-012','BC-013','BC-016','BC-017','BC-018'}
for p in processes:
 assert p['count']['E']>=1 and p['count']['W']+p['count']['X']>=1
 assert len({(m['type'],m['group']) for m in p['movements']})==len(p['movements'])
 for c in p['capabilities']:assert c in refs
 for h in p['assumptions']:assert h in assumptions
counts=Counter(m['type'] for p in processes for m in p['movements']);CFP=sum(counts.values())
benchmark=json.loads((ROOT/'audits/2026-10-30-master-data-decomposition-gap/benchmark-decision.json').read_text(encoding='utf-8'))
with model_session():
 indicative=formula('cosmic_effort',CFP=CFP,hours_per_CFP=benchmark['retained_hours_per_CFP'],factor=benchmark['retained_factor'],day_hours=7)
doc=dict(status='comptage_propose_sous_hypotheses_non_adopte',scope='Huit capacités de la Business Area Inventory State Management. Pas seulement les fragments de code OSS mesurés.',
measurement_boundary='Produit Core System, fonctions Stock ; persistance logique interne, interfaces sources/consommateurs externes. Les appels internes à Master Data ne sont pas décomposés en sous-processus facturés ; les lectures de références nécessaires restent des R sur données persistantes.',
source_method='https://cosmic-sizing.org/wp-content/uploads/2022/11/Combination-of-Parts-v5.0-Sep-2024.pdf',
rules_applied=['Un mouvement par type et objet d’intérêt dans un processus, sauf exigence distincte explicite.','Aucune multiplication par lignes, occurrences, pagination, retries ou nombre de serveurs.','Résultats normaux et réponses d’erreur inclus ; contrôles techniques internes non séparés en processus.','Les opérations et algorithmes internes n’augmentent pas seuls les CFP ; leurs contraintes restent dans les hypothèses d’effort.'],
groups=[dict(id=k,object=v[0],attributes=v[1]) for k,v in groups.items()],assumptions=assumptions,processes=processes,
capability_coverage={c:dict(native_id=refs[c]['capacite_id'],native_name=refs[c]['capacite']['nom'],processes=[p['id'] for p in processes if c in p['capabilities']]) for c in sorted(covered)},
result=dict(processes=len(processes),groups=len(groups),CFP=CFP,movements=dict(counts),hours_per_CFP=20,factor=1,day_hours=7,indicative_jh=indicative,
meaning='Calcul conditionnel de comparaison sur tout le contrat proposé. Ni quatre coûts natifs ni budget Stock retenu ; le repère ISBSG et le facteur 1 sont des conventions reprises explicitement du pilote Master Data.'),
benchmark_evidence='audits/2026-10-30-master-data-decomposition-gap/benchmark-decision.json',
nonfunctional_not_counted=['Volumes, concurrence, rétention, disponibilité, RPO/RTO, sécurité de la plateforme et sauvegardes.','Composants techniques de transport, protocole générique d’admission et interface générique déjà financés par Master Data.'],
uncertainty='Le comptage peut varier si les groupes et déclencheurs proposés sont regroupés différemment. Aucune certification COSMIC ni validation humaine des exigences revendiquée ; aucune probabilité de dépassement déduite.')
(OUT/'cosmic.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(doc['result'],ensure_ascii=False))
if __name__=='__main__':pass
