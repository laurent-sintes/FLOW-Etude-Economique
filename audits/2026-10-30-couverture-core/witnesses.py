"""Small synthetic invariants, not an execution of ERP or FLOW production services."""
from decimal import Decimal
from collections import defaultdict
import itertools
def run_witnesses(it):
 out=[]
 def witness(id,question,expected,actual,meaning):
  if expected!=actual:raise AssertionError(id+': '+repr(actual))
  out.append(dict(id=id,question=question,expected=expected,actual=actual,passed=True,meaning=meaning))
 if it==16:
  def activate(current,expected,new):return new if current==expected else current
  witness('P1','Deux activations fondées sur v4 ; la première produit v5.',5,activate(5,4,6),'La seconde activation doit être rejetée/rebasée, pas écraser silencieusement.')
  def overlap(a,b):return max(a[0],b[0])<min(a[1],b[1])
  witness('P2','Deux règles incompatibles de même priorité se recouvrent.',True,overlap((0,10),(5,15)),'Contrôle structurel de portée/période ; ne démontre pas toute cohérence sémantique.')
  def available(ceiling,used):return None if ceiling is None or used is None else max(0,ceiling-used)
  witness('C1','Plafond100, charge inconnue.',None,available(100,None),'Inconnu ne devient pas100.')
  witness('C2','Plafond100, charge explicitement nulle.',100,available(100,0),'Zéro explicite distinct de la valeur absente.')
  cells=[dict(pool='A',version=1,available=70),dict(pool='A',version=2,available=80)]
  latest={c['pool']:c for c in sorted(cells,key=lambda c:c['version'])}
  witness('C3','Deux révisions du même pool :70 puis80.',80,sum(c['available'] for c in latest.values()),'Ne pas additionner les révisions ; les pools réellement disjoints restent séparés.')
  witness('C4','2,5 heures transformées en minutes avec conversion explicite.',150,int(Decimal('2.5')*60),'Toute conversion exige dimension, facteur et période compatibles.')
 if it==17:
  suspended=True;existing_order='accepted'
  witness('E1','Suspension du prestataire : nouvelle sollicitation et ordre engagé.',[False,'accepted'],[not suspended,existing_order],'L’éligibilité interdit une nouvelle demande, ne résilie pas un engagement existant.')
  def cyclic(edges):
   nodes=set(sum(([a,b] for a,b in edges),[]));done=set()
   while True:
    nxt={n for n in nodes-done if all(a in done for a,b in edges if b==n)}
    if not nxt:break
    done|=nxt
   return len(done)!=len(nodes)
  witness('F1','Un parcours de prestations se boucle A→B→A.',True,cyclic([('A','B'),('B','A')]),'Le déclenchement durable ne corrige pas un graphe métier contradictoire.')
  distances={(0,1):2,(0,2):2,(0,3):6,(1,2):2,(1,3):4,(2,3):4}
  def dist(a,b):return 0 if a==b else distances[tuple(sorted((a,b)))]
  routes=[(sum(dist(a,b) for a,b in zip((0,)+p,p+(0,))),p) for p in itertools.permutations([1,2,3])]
  witness('T1','Trois arrêts : comparer toutes les tournées aller/retour.',12,min(x[0] for x in routes),'Oracle minuscule ; ne valide ni RoutingModel Java, ni un SLA de100arrêts.')
  witness('T2','Charges6+6, capacité10 sur un trajet commun.',False,sum([6,6])<=10,'Un itinéraire court ne prouve pas la faisabilité du chargement.')
  facts=[('e1',6),('e1',6),('e2',3)];unique=dict(facts)
  witness('R1','Attendu10, faits reconnus6 et3, dont un doublon.',1,10-sum(unique.values()),'Le reliquat est calculé sur des faits uniques reconnus, pas sur le nombre de notifications.')
  disposition='scrap_authorized';physical='not_reported'
  witness('D1','Autorisation de rebut sans preuve de destruction.','not_reported',physical,'Disposition et réalisation physique restent distinctes.')
  witness('A1','Acte déjà exécuté : une adaptation n’est pas une annulation physique.',False,'executed' in ['draft','proposed'],'Refus ou compensation explicite ; aucune réversibilité présumée.')
 if it==18:
  witness('S1','Ordre10, réalisé6 conforme et2 non conforme.',[6,2,2],[6,2,10-6-2],'Ne pas clore toute la quantité après une notification partielle.')
  packed={'P1':['u1','u2'],'P2':['u3']}
  witness('S2','Deux colis contiennent trois unités.',[2,3],[len(packed),sum(map(len,packed.values()))],'Unités logistiques et quantités de biens ne sont pas la même mesure.')
  witness('S3','Kit exige2A+1B ; disponibles5A+1B.',1,min(5//2,1//1),'La filiation des composants est nécessaire ; ce n’est pas un ordre de fabrication industriel.')
  witness('S4','Inspection conclut non conforme ; réparation non demandée.',False,False,'Le résultat d’inspection n’autorise ni ne réalise une réparation.')
  witness('S5','Réservation de transport confirmée sans déplacement.',[True,False],[True,False],'Booking et Transport Order sont deux engagements distincts.')
  customs={'technical_ack':True,'released':False}
  witness('S6','Accusé technique douanier reçu.',False,customs['released'],'Ne pas libérer les marchandises sur le seul accusé.')
  witness('S7','Autorisation de rebut sans preuve d’exécution.',False,False,'L’autorisation, la réalisation et l’acceptation du résultat ont des états distincts.')
 if it==19:
  payments={'tx1':Decimal('60.00'),'tx2':Decimal('25.00')}
  witness('M1','À encaisser100, résultats reconnus60 et25.',15,float(Decimal('100')-sum(payments.values())),'Reste monétaire sur résultats uniques reconnus.')
  witness('M2','Capture distante peut avoir eu lieu, réponse perdue.','query_or_manual_reconcile','query_or_manual_reconcile','L’inconnu ne justifie pas une seconde opération financière.')
  witness('M3','Encaissé85, remboursé20, nouvelle demande70.',False,Decimal('70')<=Decimal('85')-Decimal('20'),'Ne pas dépasser le montant remboursable autorisé.')
  currencies=['EUR','USD']
  witness('M4','Deux montants de devises différentes sans taux autorisé.',False,len(set(currencies))==1,'Pas de somme ni de change implicite.')
  witness('M5','Avoir émis, aucun remboursement reconnu.',0,0,'Le document de crédit ne prouve pas le paiement.')
 if it==20:
  records=[('e1',1,'A'),('e2',1,'B'),('e2',2,'C')]
  events={}
  for id,v,name in records:
   if id not in events or v>events[id][0]:events[id]=(v,name)
  witness('I1','Une trace B est corrigée en C.', ['A','C'],[v[1] for v in events.values()],'Conserver correction et provenance sans compter deux transitions.')
  closed=[10,20];opened=[None]
  witness('I2','Deux dossiers terminés et un encore ouvert.',[15,2,1],[sum(closed)/len(closed),len(closed),len(opened)],'Publier population, dossiers censurés et durée ; ouvert ne vaut pas zéro.')
  intervals=[(0,10),(5,15)]
  union=len(set(t for a,b in intervals for t in range(a,b)))
  witness('I3','Deux branches parallèles de10 avec5 de recouvrement.',15,union,'Durée écoulée15, somme des temps de branches20 ; mesures distinctes.')
  witness('I4','Trace incomplète : comparaison au parcours attendu.','indeterminate','indeterminate','Absence de trace ne démontre pas saut d’étape ou causalité.')
  visible=[x for x in [{'tenant':'A','n':2},{'tenant':'B','n':3}] if x['tenant']=='A']
  witness('I5','Indicateur du tenantA.',2,sum(x['n'] for x in visible),'Les périmètres d’accès doivent aussi filtrer les agrégats.')
 return out
