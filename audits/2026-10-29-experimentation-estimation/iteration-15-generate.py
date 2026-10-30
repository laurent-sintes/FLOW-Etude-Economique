"""Synthetic instances, exact oracles produced independently by iteration-15-analyse.py."""
from pathlib import Path
import json,random
A=Path(__file__).resolve().parent
def opt(id,cost,uses,group='none',start=0,end=1,admissible=True):
 return dict(id=id,cost=cost,uses=uses,group=group,start=start,end=end,admissible=admissible)
def case(id,label,caps,tasks,fixed=None,pred=None,exact=True,kind='small'):
 return dict(id=id,label=label,capacity=caps,tasks=[dict(id='L'+str(i),options=o) for i,o in enumerate(tasks)],fixed=fixed or {},precedence=pred or [],exact=exact,kind=kind)
cases=[]
cases.append(case('ATP_TRAP','Un choix flexible prive la ligne contrainte de sa seule ressource',{'A':1,'B':1},[[opt('A',1,{'A':1}),opt('B',2,{'B':1})],[opt('A',1,{'A':1})]]))
cases.append(case('ATP_SHARED','Deux demandes individuellement possibles dépassent le stock commun',{'stock':10},[[opt('serve',0,{'stock':6})],[opt('serve',0,{'stock':6})]]))
cases.append(case('PTP_FIXED','Coût de transport fixe partagé entre trois lignes',{},[[opt('A',6,{},'A'),opt('B',2,{},'B')] for _ in range(3)],{'B':10}))
cases.append(case('CTP_CHAIN','Matière, créneaux exclusifs et précédence entre opérations',{'mat':2,'s0':1,'s1':1,'s2':1},[
 [opt('early',4,{'mat':2,'s0':1},start=0,end=1),opt('late',1,{'mat':2,'s1':1},start=1,end=2)],
 [opt('early',1,{'s1':1},start=1,end=2),opt('late',2,{'s2':1},start=2,end=3)]],pred=[[0,1]]))
cases.append(case('CTP_IMPOSSIBLE','La précédence rend les créneaux incompatibles',{},[[opt('late',1,{},start=2,end=3)],[opt('early',1,{},start=0,end=1)]],pred=[[0,1]]))
cases.append(case('MANDATORY_FILTER','Le coût bas ne dispense pas du respect des exigences',{},[[opt('forbidden',0,{},admissible=False),opt('allowed',8,{})]]))
cases.append(case('ZERO_CAPACITY','Une capacité nulle interdit la consommation',{'slot':0},[[opt('blocked',1,{'slot':1})]]))
cases.append(case('EMPTY_DOMAIN','Aucune option admissible',{},[[opt('forbidden',1,{},admissible=False)]]))
rng=random.Random(1515)
for k in range(12):
 caps={f'R{j}':rng.randint(3,6) for j in range(4)}
 tasks=[]
 for i in range(6):
  tasks.append([opt(str(j),rng.randint(1,15),{f'R{rng.randrange(4)}':rng.randint(1,3)},f'G{j}') for j in range(3)])
 cases.append(case(f'EXACT_{k:02}','Cas généré reproductible, 6 lignes × 3 options',caps,tasks,{f'G{j}':rng.randint(0,10) for j in range(3)}))
for n,m in [(30,8),(60,12),(100,20)]:
 caps={f'R{j}':max(5,n//4) for j in range(12)}
 tasks=[]
 for i in range(n):
  tasks.append([opt(str(j),rng.randint(1,100),{f'R{rng.randrange(12)}':rng.randint(1,3)},f'G{rng.randrange(8)}') for j in range(m)])
 cases.append(case(f'LOAD_{n}','Charge synthétique sans garantie de représentativité',caps,tasks,{f'G{j}':rng.randint(10,50) for j in range(8)},exact=False,kind='load'))
data={'schema':1,'seeds':[17,29,43],'budget_ms':1000,'hybrid_timefold_ms':400,'cases':cases,
'contract':{'choice':'une option admissible par ligne; aucune livraison partielle','capacity':'ressources entières partagées, absence de donnée refusée','precedence':'fin prédécesseur <= début successeur, créneaux déjà énumérés','objective':'somme coûts variables + chaque coût fixe de groupe une seule fois','exclusions':['génération exhaustive des créneaux','unités fractionnaires','profondeur de nomenclature','dates calendaires réelles','stock événementiel','politiques Groupe','engagement concurrent','API et charge multiutilisateur','production']}}
(A/'iteration-15-cases.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(len(cases),'cases created')
