from pathlib import Path
import re, shutil, hashlib, json, zipfile

ROOT=Path(__file__).resolve().parent.parent
names=['README.md']+[next(ROOT.glob(n+'-*.md')).name for n in ['01','02','03','04','05','06','07','09','11','12','13','15','16']]
backup=ROOT/'archives/methodes-remplacees/2026-10-21/avant-envoi-client'
backup.mkdir(parents=True,exist_ok=True)
for name in names:
    if not (backup/name).exists(): shutil.copy2(ROOT/name,backup/name)
def read(name): return (backup/name).read_text(encoding='utf-8')
def save(name,text): (ROOT/name).write_text(text.strip()+'\n',encoding='utf-8')
def cut(text,start,end=None):
    a=text.index(start); b=text.index(end,a) if end else len(text)
    return text[:a]+text[b:]
head='![Logo eXalt](assets/exalt-logo.png)\n\n**Laurent Sintès** · 21 octobre 2026\n\n---\n\n'
service='''## Services annuels retenus

| Prestations humaines en année pleine | FLOW | Microsoft | SAP |
| --- | ---: | ---: | ---: |
| Maintien, exploitation et pilotage | 7 × 200 JH × 750 € = **1,05 M€** | 6 × 200 JH × 850 € = **1,02 M€** | Maintenance 250 k€ + supervision 450 k€ = **0,70 M€** |
| Évolutions fonctionnelles | 2 × 200 JH × 750 € = **0,30 M€** | 2 × 200 JH × 850 € = **0,34 M€** | Forfait **0,35 M€** |
| **Total services humains** | **1,35 M€/an** | **1,36 M€/an** | **1,05 M€/an** |

Les capacités FLOW et Microsoft sont des hypothèses de dispositif fournisseur, en heures ouvrées françaises. Les forfaits SAP proviennent du RFI Delaware ; la supervision comprend des horaires étendus et la couverture de la cible reste à confirmer. Une personne-an représente 200 jours de travail pour le contrat. Les effectifs peuvent être partagés entre plusieurs intervenants.

Le maintien finance les corrections, les versions techniques courantes, l'exploitation et le pilotage. Les évolutions financent les nouvelles fonctions, y compris les versions fonctionnelles du Core FLOW. Aucune deuxième enveloppe d'exploitation n'est ajoutée. La capacité d'évolution ne garantit pas un même nombre de fonctions livrées selon la solution.

Les ressources FLOW de **400 k€/an**, hors personnel, portent son fonctionnement complet à **1,75 M€/an**. Les licences, le support et les ressources Buy sont calculés séparément. Avec indexation, le fonctionnement complet moyen des années 6 à 15 atteint **2,54 M€/an SAP** et **2,56 M€/an Microsoft**. Ces moyennes ne sont pas les tarifs d'une année de départ.

Le service complet commence après le mois des premiers usages : M60 FLOW et M18 SAP/Microsoft, soit respectivement 10 et 13,5 années de service sur quinze ans. Les interventions de stabilisation financées au projet sont distinctes du service courant. Astreinte et migrations majeures sont des options inactives.

La [méthode](02-methode-estimation.md) justifie les compétences et capacités. Le [guide](13-audit-classeur-excel.md) indique les cellules modifiables. L'équivalence contractuelle des services n'est pas démontrée.
'''

texts={n:read(n) for n in names}
t=texts['04-resultats-etude.md']
t=cut(t,'## Ce qui a changé depuis la version précédente','## Lecture pour le décideur')
t=cut(t,'## Vérification')+'''## Contrôles de cohérence

Les totaux ont été rapprochés des calculs annuels du classeur. Le recalcul Excel confirme les montants et les unités, sans erreur de formule détectée. Ces contrôles valident le calcul ; ils ne constituent ni un engagement fournisseur ni une validation de la suffisance des moyens.

[Méthode](02-methode-estimation.md) · [Guide du classeur](13-audit-classeur-excel.md) · [Pièces et références](20-registre-sources.md)
'''
t=re.sub(r'Les budgets initiaux, équipes, taux et calendriers sont inchangés.*?\n\n','',t)
t=t.replace('Elle n’est plus réduite en proportion du périmètre déployé. ','')
t=t.replace('Les 32 100 JH et budgets initiaux ne sont pas réestimés dans cette refonte. Les abaques de réalisation restent documentés dans les annexes et la version détaillée archivée ; les trois onglets utilisent ces budgets comme entrées expliquées.','Les 32 100 JH FLOW sont détaillés dans l’annexe de charge. Les budgets initiaux sont des entrées expliquées dans Sources ; les hypothèses annuelles et leur projection sont recalculables dans Hypothèses.')
texts['04-resultats-etude.md']=t
t=texts['09-abaques-repartition.md'].split('## Services annuels :')[0]+service
t=t.replace('Ce regroupement retire 1,125 M€ des anciennes clés Business et autant des Flux, sans changer le Core ni le total.','')
t=re.sub(r'Les clés historiques.*?\n\n','L’option Storeland n’est pas ventilée tant que les fonctions manquantes ne sont pas connues.\n\n',t)
texts['09-abaques-repartition.md']=t
t=texts['11-cout-nominal-minimum.md'].split('### Après la première version du Core')[0]+service
t=re.sub(r'Ce dernier poste remplace.*?hypothèse d.ingénierie explicite\*\*, non une économie observée ou un ratio de marché\.','Les 1 000 JH constituent une hypothèse d’ingénierie, non une productivité mesurée.',t,flags=re.S)
t=t.replace('Les JH antérieurs représentaient une équipe pluridisciplinaire, métier inclus : leur réinterprétation en jours de forfait fournisseur suppose que','Les JH couvrent une équipe pluridisciplinaire, métier inclus : le calcul suppose que')
t=t.replace('Les modifier actualise le budget de référence.','Leur modification nécessite d’actualiser le budget initial dans Sources et sa répartition ; le calcul annuel reprend ensuite ces entrées.')
texts['11-cout-nominal-minimum.md']=t
t=texts['15-rapprochement-buy-france.md']
a=t.index('## 8. Fonctionnement, licences et contrôles');b=t.index('### Plateforme d\'exécution et exploitation',a)
t=t[:a]+service.replace('## Services annuels retenus','## 8. Fonctionnement et services')+'\n'+t[b:]
t=t.replace('**376,975 k€/an**, activités et compétences en heures ouvrées ; aucune reprise du forfait SAP.','**Compris dans les 1,02 M€/an de maintien**, avec maintenance et pilotage ; aucune enveloppe supplémentaire.')
t=re.sub(r'Archive originale :.*?Les pièces sont confidentielles ; les repères suivants permettent de contrôler les calculs\.','Les [pièces sources jointes](20-registre-sources.md) sont confidentielles. Le registre donne accès aux fichiers et les repères suivants permettent de contrôler les calculs.',t)
t=t.split('### Référence financière courante')[0]
t=t.replace('la page de décision retient 0,1 M€','la page de décision affiche deux décimales en M€')
t=re.sub(r'Leurs anciennes contributions sont retirées de Flux et Business\.\s*','',t)
texts['15-rapprochement-buy-france.md']=t
t=texts['16-methodes-et-presentation-comparaison-make-buy.md']
t=t[:t.index('## Services financés et nouveaux compléments')]+t[t.index('## FLOW : ressources, construction et exploitation'):]
a=t.index('### Un seul abaque');b=t.index('## SAP : CPI',a)
t=t[:a]+service+'\n'+t[b:]
t=t.split('## Présentation')[0]
t=t.replace("L'audit a mis en évidence une différence de couverture :",'La comparaison distingue les dépenses techniques des prestations humaines :')
texts['16-methodes-et-presentation-comparaison-make-buy.md']=t
texts['12-modele-tco-buy-make.md']=head+'''# Coûts sur quinze ans

## Convention de comparaison

Le modèle calcule les dépenses fournisseur HT en euros courants depuis un lancement commun. Il ne valorise ni les bénéfices métier ni les coûts internes client, et ne calcule pas de valeur actualisée. Les horizons 3, 5, 10 et 15 ans restent visibles ensemble. Le fonctionnement annuel moyen porte sur les années 6 à 15 et comprend les indexations ; ce n'est pas le cumul divisé par quinze.

## Réalisation et calendrier

| Option | Réalisation initiale | Premiers usages | Périmètre complet | Service financé sur 15 ans |
| --- | ---: | ---: | ---: | ---: |
| FLOW | 24,461 M€ | M60 | M60 | 10 ans |
| SAP | 17,133 M€ | M18 | M30 | 13,5 ans |
| Microsoft | 5,736 M€ | M18 | M38 | 13,5 ans |

Les budgets initiaux sont expliqués dans Sources, lignes 130–176. FLOW comprend 32 100 JH à 750 € et 386 k€ de ressources pendant la construction. Les budgets Buy associent références RFI et hypothèses d'adaptation à la cible ; les abonnements sont comptés séparément dans le calendrier. Les dates sont des hypothèses de comparaison ; les bénéfices des usages plus précoces ne sont pas monétisés.

'''+service+'''
## Indexation et souscriptions

Les prestations et ressources hors CPI SAP sont à 0 % d'indexation. CPI SAP, plateforme d'échange de données, est indexé de 4 % par an. Les licences sont indexées de 4 % après un gel supposé d'un an SAP et de cinq ans Microsoft. Ces hypothèses ne sont pas des engagements contractuels.

Les paniers de licence RFI sont conservés dans Sources. Le retrait Finance appliqué est une hypothèse de panier commercial réduit, à confirmer : 400 000 / 1 270 879 pour SAP et 10 % pour Microsoft. Unified suit son taux de 7,5 %, le minimum source de 50 000 USD et les paramètres visibles de part D365 et de conversion ; l'année initiale conserve 90 000 €.

L'hébergement standard Buy est déjà dans les souscriptions. Les ressources additionnelles sont la recette et production CPI SAP, et une provision Microsoft de 12 k€/an de recette puis jusqu'à 33 k€/an de production externe. Le tenant CPI de production démarre aux premiers usages ; les messages et ressources Microsoft suivent le périmètre livré. Le détail technique figure dans [l'annexe des plateformes](16-methodes-et-presentation-comparaison-make-buy.md).

## Options et limites

Storeland non découvert, lotissement additionnel, risque, astreinte et migrations majeures sont désactivés. Le temps interne client est hors total fournisseur ; une provision de co-construction peut être affichée séparément. La coexistence prolongée et le remplacement des anciens SI pendant la transition ne sont pas valorisés dans cette comparaison nominale. Aucune sortie de solution à la fin de l'horizon n'est supposée.

## Calcul et traçabilité

Sources porte les références et les budgets initiaux expliqués. Hypothèses porte les capacités, prix, dates et indexations, ainsi que les calculs annuels. Comparaison reprend les résultats, les jalons et les principales limites. Il n'y a pas d'autre onglet.

Les frontières de coût excluent une seconde imputation des mêmes activités au projet, au maintien et aux évolutions. Les contrôles mathématiques ne démontrent pas l'équivalence contractuelle des services ni la productivité des équipes. La [note de décision](04-resultats-etude.md) présente les résultats et leur portée.
'''
t=texts['02-methode-estimation.md']
t=re.sub(r'> \*\*Reprise.*?\n\n','',t)
t=re.sub(r'Cette reprise concerne le fonctionnement.*?\n\n','',t)
t=re.sub(r'Les anciennes quantités.*?cessent de justifier le budget\.','',t)
t=re.sub(r'La révision de présentation.*?\n\n','',t)
t=re.sub(r'\*\*État :.*','',t,flags=re.S)
t=t.replace('Les prix moyens sont conservés pour isoler l\'effet du dimensionnement :','Les prix moyens retenus sont :')
texts['02-methode-estimation.md']=t
t=texts['13-audit-classeur-excel.md'].split('## Contrôle de la révision')[0]
t=re.sub(r'Les références aux annexes détaillées.*?\n\n','Les annexes détaillent l’origine des budgets initiaux et les pièces sont accessibles dans le [registre des sources](20-registre-sources.md).\n\n',t)
t=t.replace('est désormais','est')
texts['13-audit-classeur-excel.md']=t
t=texts['07-analyse-synvance.md']
a=t.index('**Statut :');b=t.index('## Ce que l\'étude mesurait')
t=t[:a]+'''Les montants sont des estimations RFI de 2025, non des offres contractuelles. Les pièces sont accessibles dans le [registre des sources](20-registre-sources.md). La mission Synvance a été clôturée le 4 juillet 2025 ; l'offre SAP/Delaware de septembre est une poursuite du RFI par Beaumanoir.

Le [rapprochement France](15-rapprochement-buy-france.md) distingue les prestations déjà proposées, les compléments conditionnels et les hypothèses de transfert des tâches techniques. La construction du Core éditeur reste à zéro pour les deux options Buy. Les développements et interfaces du RFI ne sont pas ajoutés une seconde fois.

'''+t[b:]
t=re.sub(r' La première version de cette analyse.*?(?=\n\n)','',t)
texts['07-analyse-synvance.md']=t
t=texts['README.md']
t=t.replace('**Version du 21 octobre 2026 : le classeur comprend trois onglets, Comparaison, Hypothèses et Sources.** La méthode par capacités fournisseur est appliquée. Les budgets initiaux et les abonnements sont conservés ; le dimensionnement des services et leur démarrage sont explicites.','**Étude d’ordre de grandeur sous hypothèses — 21 octobre 2026.** Le dossier compare les dépenses fournisseur de FLOW, SAP et Microsoft sur un périmètre opérationnel cible. Les budgets ne sont pas des offres engageantes.')
t=t.replace('désormais ','').replace('La présentation est revue **sans changement des coûts**. ','').replace('Résultats et écarts avant/après expliqués.','Résultats, hypothèses et limites de décision.')
t=t.split('Les annexes d’audit et de recalibrage')[0]+'\n[Pièces justificatives et références accessibles](20-registre-sources.md).\n'
texts['README.md']=t

# Store portable copies of the original pieces. No source contents are edited.
srcdir=ROOT/'sources/client';srcdir.mkdir(parents=True,exist_ok=True)
pieces=[('S01','delaware-septembre.pdf','Delaware septembre 2025','p. 26–28 fonctions ; p. 37 services ; p. 38–41 réalisation ; p. 43–45 licences'),('S02','sap-questionnaire.xlsx','Questionnaire SAP','Onglet 8 et matrice fonctionnelle'),('S03','microsoft-1.pdf','Avanade réponse 1','p. 38 souscriptions ; p. 39 pilote ; p. 40 déploiements'),('S04','microsoft-questionnaire.xlsx','Questionnaire Microsoft','Budget, support et couverture fonctionnelle'),('S05','copil-5.pdf','COPIL Beaumanoir 17 septembre 2025','p. 7 budgets et calendriers ; p. 8 réserves'),('S06','copil-4.pptx','COPIL Synvance 2 juillet 2025','slide 11 réserves sur les estimations'),('S07','microsoft-mail-2025-09-16.txt','Courriel Microsoft 16 septembre 2025','Extraction textuelle ; exclusions tests et accompagnement, localisation et déploiement')]
registry=head+'# Pièces justificatives et références\n\nLes documents ci-dessous accompagnent l’étude. Les offres et questionnaires Beaumanoir sont confidentiels. Les montants RFI restent indicatifs ; les compléments et équipes sont des hypothèses de l’étude.\n\n| Identifiant | Pièce accessible | Repères |\n| --- | --- | --- |\n'
manifest=[]
for id,name,label,pages in pieces:
    source=ROOT/'tmp/synvance-review'/name; dest=srcdir/name;shutil.copy2(source,dest)
    registry+=f'| {id} | [{label}](sources/client/{name}) | {pages} |\n'
    manifest.append({'id':id,'file':str(dest.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
model=Path('C:/Dev/Beaumanoir Cartographie/modeles/release/2026-10-17.1/model.yaml')
shutil.copy2(model,srcdir/'cartographie-2026-10-17.1.yaml')
registry+='| S08 | [Cartographie publiée 2026-10-17.1](sources/client/cartographie-2026-10-17.1.yaml) | Modèle source YAML ; rechercher Supply Chain Management. Le périmètre exploité est décrit dans le cahier des charges. |\n| S09 | [Gestion de la configuration](sources/Gestion%20de%20la%20configuration.pdf) | Exigences de paramétrage fournies par Laurent Sintès. |\n'
with zipfile.ZipFile('C:/Users/laure/OneDrive/Documents/Beaumanoir/OneDrive/00 - Etude Synvance.zip') as z:
    additional=[('S10','COPIL 1','.pptx','copil-1.pptx','COPIL 1','slide 8 : frontières initiales OMS et POS'),('S11','document de présentation','.pdf','rfi-presentation.pdf','Présentation RFI du 28 mai 2025','p. 3–8 et 13 : périmètre et consultation'),('S12','synthèse des besoins métier','.pdf','rfi-besoins.pdf','Besoins métier RFI du 28 mai 2025','p. 24–27 et 31–40 : commandes, stock et flux'),('S13','suite QA','.pptx','rfi-questions-reponses.pptx','Compléments RFI du 13 juin 2025','slides 6, 19, 27 : frontières et architecture'),('S14','besoins cible - avec retours','.pptx','besoins-cible.pptx','Synthèse des besoins cibles du 21 mai 2025','slides 3–4 : cible et applications périphériques')]
    for id,key,ext,name,label,pages in additional:
        found=[n for n in z.namelist() if key.casefold() in n.casefold() and n.endswith(ext) and 'Copie' not in n]
        assert len(found)==1,found
        (srcdir/name).write_bytes(z.read(found[0]))
        registry+=f'| {id} | [{label}](sources/client/{name}) | {pages} |\n'
shutil.copy2(ROOT/'tmp/synvance-review/microsoft-readme.docx',srcdir/'microsoft-readme.docx')
registry+='| S15 | [Note Microsoft et K3](sources/client/microsoft-readme.docx) | K3 est un éditeur indépendant. |\n'
registry+='''
## Sources publiques

Les [références de marché](03-references-marche.md) et les [fiches entreprises](05-fiches-entreprises-et-criteres-investissement.md) donnent les liens directs, dates, unités et limites des publications utilisées. Ces liens nécessitent une connexion Internet ; leur contenu peut évoluer. Ils ne constituent pas des devis Beaumanoir ni une mesure de la productivité FLOW.

## Méthodes et modèles consultés

- [Modèle Should Cost du Cabinet Office](sources/recherche-tco-2026-10-20/cabinet-office-illustrative-scm.xlsx).
- [Modèle TCO et ROI Smartsheet](sources/recherche-tco-2026-10-20/smartsheet-tco-roi-template.xlsx).
- [Guide Thoughtworks Build versus Buy](sources/recherche-tco-2026-10-20/thoughtworks-build-vs-buy-2022.pdf).

Ces fichiers sont des références de méthode. Les budgets applicables à FLOW sont uniquement ceux du classeur de comparaison et de la note de décision.
'''
save('20-registre-sources.md',registry)
for name,t in texts.items():
    t=t.replace('<C:/Dev/Beaumanoir Cartographie/modeles/release/2026-10-17.1/model.yaml>','sources/client/cartographie-2026-10-17.1.yaml')
    t=t.replace('tmp/synvance-review/microsoft-mail-2025-09-16.txt','sources/client/microsoft-mail-2025-09-16.txt')
    t=t.replace('sources/recherche-tco-2026-10-20/)','20-registre-sources.md)')
    t=re.sub(r'\((?:tools/[^)]*|sources/recherche-tco-2026-10-20/template-inventory.json)\)','(20-registre-sources.md)',t)
    t=t.replace('(14-audit-inflation-run-et-comparaison.md)','(12-modele-tco-buy-make.md)').replace('(19-recalibrage-service-microsoft.md)','(02-methode-estimation.md)')
    # Remove superseded-method paragraphs, preserving business history and source caveats.
    t='\n\n'.join(p for p in t.split('\n\n') if 'archives/methodes-remplacees' not in p)
    t=t.replace('**Statut :** cadrage de travail, 19 octobre 2026.','**Statut :** périmètre de référence pour estimation, 21 octobre 2026.')
    t=t.replace('sous-produit transverse','composant transverse')
    t=t.replace('désormais ','').replace('et dans la version détaillée archivée ;',';')
    t=re.sub(r'L’ancienne feuille Passage Buy France.*?Le cahier de ', 'Les compléments fonctionnels sont des hypothèses de charge par famille de besoins, détaillées dans le tableau ci-dessus. Les [questionnaires fournisseurs](20-registre-sources.md) permettent de vérifier les déclarations de couverture et les exclusions. Le cahier de ', t)
    t=t.replace('Les JH d\'ingénierie plateforme étaient compris','Les JH d\'ingénierie plateforme sont compris')
    t=re.sub(r'- \*\*Réversibilité en option désactivée\.\*\*.*?\n','- **Sortie de solution non financée.** Aucune sortie automatique n’est supposée en année 15 ; une estimation de sortie nécessiterait de préciser la cible et les données à transférer.\n',t)
    t=t.replace('Le coefficient d\'exécution externe est modifiable. Si les droits et capacités D365/K3 comprennent les services nécessaires, il passe à zéro.','Les budgets de recette et de production externes sont modifiables dans Hypothèses. Si les droits et capacités D365/K3 couvrent ces besoins, ces budgets peuvent être annulés.')
    t=t.replace('Le paramètre de crédit imputable vaut **0 € par défaut : non imputé faute de valeur**, et non « aucun crédit disponible ».','**Aucun crédit n’est imputé au budget, faute de valeur documentée** ; cela ne signifie pas absence de crédit disponible.')
    t=re.sub(r'Les \[abaques plateforme\].*?calendrier et de l.indexation du classeur\.', 'Les tableaux de ressources de cette annexe et la méthode de service documentent les quantités, prix et frontières. Les cumuls à 3/5/10/15 ans résultent du calendrier et de l’indexation du classeur.', t)
    t=t.replace('Le [modèle de répartition](20-registre-sources.md) décrit chaque groupe de travaux, sa quantité, son prix, sa source et ses clés.','Les clés de répartition ci-dessous et les quantités de l’annexe Buy décrivent les travaux retenus.')
    t=t.replace('Le [modèle de répartition](20-registre-sources.md) conserve les clés, les classements sources et les conventions estimées.','Les [clés de répartition](09-abaques-repartition.md) expliquent ces classements.')
    t=t.replace('[abaque unique maintenance/exploitation](20-registre-sources.md)','[méthode de service](02-methode-estimation.md)').replace('[Abaques plateforme](20-registre-sources.md)','[Détail des plateformes](16-methodes-et-presentation-comparaison-make-buy.md)').replace('[abaques de ressources](20-registre-sources.md)','[tableaux de ressources](16-methodes-et-presentation-comparaison-make-buy.md)')
    t=t.replace('**Laurent Sintès** · 20 octobre 2026','**Laurent Sintès** · 21 octobre 2026')
    t=re.sub(r" L'\[inventaire de lecture seule\].*?fichiers\.",' Les modèles consultés sont joints dans le registre des sources.',t)
    if name=='07-analyse-synvance.md':
        a=t.index('**Sources internes de l\'archive :**');b=t.index('## Chiffres effectivement observés',a)
        t=t[:a]+'''## Pièces qui établissent le périmètre

Le [registre des sources](20-registre-sources.md) donne accès aux pièces suivantes : COPIL 1, slide 8 (S10) ; synthèse des besoins cibles, slides 3–4 (S14) ; présentation RFI, pages 3–8 et 13 (S11) ; besoins métier RFI, pages 24–27 et 31–40 (S12) ; questions-réponses, slides 6, 19 et 27 (S13). Le COPIL 5, pages 4, 7 et 8 (S05), présente les budgets et limites. La soutenance Delaware, pages 21–28 et 37–45 (S01), la réponse Avanade, pages 13, 22 et 38–42 (S03), et la note Microsoft/K3 (S15) documentent les offres. Les références de juillet et septembre correspondent à des étapes différentes du RFI de 2025.

'''+t[b:]
        t=re.sub(r"Le message original est conservé dans l'archive au chemin `[^`]+`\. Une",'Une',t)
    save(name,t)
(ROOT/'tmp/client_source_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('UPDATED',len(texts),'documents; source registry and',len(pieces)+1,'local pieces')
