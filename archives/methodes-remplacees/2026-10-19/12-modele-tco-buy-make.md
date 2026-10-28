> **ARCHIVE — version remplacée le 19 octobre 2026.** Les tarifs, bornes et cumuls de cette copie ne servent pas à la décision actuelle. Voir la [version courante](../../../12-modele-tco-buy-make.md).

![Logo eXalt](../../../assets/exalt-logo.png)

**Laurent Sintès** · 19 octobre 2026

# Prix FLOW et références Buy rapprochées sur 15 ans

Le [classeur](../../../outputs/01a1530f-f378-7fd1-9654-468c9b2141b6/FLOW_Make_abaques_et_prix_France.xlsx) distingue désormais **les prix RFI conservés**, **leur réévaluation sur une base de réalisation en France**, **les retraits hors périmètre FLOW** et **les prestations supposées manquantes**. L'onglet **Passage Buy France** détaille le pont ; **Comparaison** en présente les montants, les cumuls fournisseur et les années de Run équivalentes. Les trois paires **Prix / Prix unitaire** exposent les hypothèses propres à FLOW, SAP et Microsoft. Les données brutes demeurent dans **Références** et **Sources**.

Les prix SAP/Microsoft recalibrés sont des **estimations conditionnelles de périmètre rapproché**, pas des offres intégrateur révisées. Ils ne donnent pas aux solutions Buy l'indépendance éditeur et la propriété du produit recherchées par FLOW. Les hypothèses détaillées sont conservées dans [le pont Buy](../../../tools/flow_buy_comparable.json) et [les abaques de Run](../../../tools/flow_run_rationale.json).

## Coût de réalisation initiale et Build Core system

Le **Coût de réalisation initiale** désigne l'ensemble des prestations fournisseur nécessaires jusqu'à la première mise en service : construction éventuelle du produit, paramétrage, développements propres au projet, intégration, migration, qualification et accompagnement. Il se distingue des souscriptions et du Run comptés dans la projection.

La ligne **Build Core system** isole le coût de création du logiciel cœur :

- **FLOW Make** : construire le produit appartient au projet et doit être payé une fois. Cette ligne est une composante du Coût de réalisation initiale, jamais un supplément à son total.
- **SAP et Microsoft Buy** : **0 € de construction du logiciel éditeur facturée comme projet Beaumanoir**. Le droit d'usage et la maintenance standard sont traités dans la souscription. Ce zéro ne signifie pas absence de coûts de mise en œuvre.
- Le paramétrage, les interfaces et les développements spécifiques Buy restent des prestations de réalisation initiale distinctes du Build Core system. Un spécifique répondant à une fonction manquante ne constitue pas la reconstruction de tout le produit éditeur.

Le chiffrage des fonctions supplémentaires suit les réponses fonctionnelles : une capacité déjà proposée ne reçoit pas un second coût de développement. Une couverture non démontrée reste une question à qualifier ; **elle ne prouve pas l'absence de la fonction**. Le montant de **1,26 M€** de travail IT Microsoft initialement client repris au forfait appartient déjà à la mise en œuvre, hors Build Core system ; il ne doit pas être réintroduit dans les fonctions supplémentaires.

## Pourquoi ne pas comparer directement les prix RFI ?

Le **COPIL 5 du 17 septembre 2025, page PDF 8**, qualifie le coût projet Microsoft de faible et écrit « Semble sous évaluée au vu des expériences ! ». Il qualifie le coût SAP d'élevé. Le COPIL 5 est postérieur à la clôture de Synvance du **4 juillet 2025** : la réserve de septembre appartient au suivi Beaumanoir, pas à une conclusion signée Synvance. Le **COPIL 4 du 2 juillet, slide 11**, signalait déjà des estimations approximatives et disparates et la conservation des hypothèses fournisseurs avec peu de retraitements.

Les deux périmètres RFI couvrent déjà des commandes, du stock, de la disponibilité et de l'allocation. SAP propose notamment **S/4 et OMSA** ; Microsoft propose **D365 Supply Chain / Commerce et K3 Fashion**. Les preuves de standard et de customisation dans les réponses fonctionnelles sont conservées : elles interdisent de financer une seconde fois un OMS, un moteur d'allocation ou un moteur de workflow. Les différences avec les exigences FLOW doivent être décrites au niveau d'une fonction ciblée et assorties de leur statut de couverture.

Le courriel Microsoft/Avanade transmis le **16 septembre 2025** documente trois réserves concrètes : automatisation des tests exclue par défaut, conduite du changement exclue sauf formation des utilisateurs clés/formateurs, tarifs influencés par un mix Onshore/Nearshore/Offshore. SAP documente davantage ses charges mais comporte un total financier contradictoire, des efforts internes importants et des calendriers non rapprochés. Le dossier ne démontre aucun coefficient universel de sous-évaluation de ×1,5 ou ×2.

## Horizon, calendrier et comparaison fournisseur

Les quinze ans sont comptés **depuis le lancement commun**, année 0. Les montants sont HT, courants, sans actualisation. Le coût nominal FLOW est désormais **actif**, pour comparer les trois options sans réserver des aléas uniquement au Make. Aucun risque forfaitaire n'est ajouté aux prix centraux Buy.

- **FLOW** : construction décaissée linéairement sur cinq ans, livraison unique **M60**, puis dix années pleines de Run. Livraison unique ne signifie pas facture unique.
- **SAP** : calendrier simplifié COPIL de **18 mois de pilote puis 12 mois de déploiement**, livraison finale **M30**. Upgrade M0–M6 en parallèle ; poids de Run 20 % pilote / 80 % déploiement : hypothèses. Les matrices Delaware indiquent **21 + 17 mois**, divergence conservée dans les réserves.
- **Microsoft** : **18 mois de pilote puis 20 mois pour quatre pôles**, livraison finale **M38**. Vagues M18–26, M22–30, M26–34 et M30–38 et poids égaux de 20 % : hypothèses cohérentes avec le total COPIL, sans échéancier fournisseur détaillé.

Les coûts de réalisation initiale recalibrés sont répartis sur ces trajectoires. **Le calendrier Buy n'est pas recalculé malgré les prestations ajoutées : une capacité fournisseur accrue est supposée.** C'est une hypothèse de projection, pas un délai réalisable démontré. L'enveloppe de Run stabilisé est appliquée au prorata des livraisons ; la stabilisation initiale est supposée dans le Coût de réalisation initiale. Pour SAP, l'offre chiffre les services après stabilisation : cette application précoce reste conventionnelle.

Les courbes et la première synthèse présentent les **coûts fournisseur**. Les coûts client disposent d'un bloc séparé. Le soutien métier interne, les participants aux ateliers et les arbitrages restent exclus des trois factures fournisseur ; un zéro technique client ne signifie pas absence de coût de programme.

## Coût de réalisation initiale FLOW

Le nominal reste **32 100 JH × 750 €/JH = 24,075 M€**. Les quatorze postes et leurs activités figurent dans **Charges Flow**. Les subdivisions expliquent les hypothèses de charge ; elles ne mesurent pas une productivité observée.

| Composition du nominal FLOW | JH selon les clés d'imputation | Coût HT |
| --- | ---: | ---: |
| **Build Core system** | **20 345** | **15,258750 M€** |
| Configuration initiale | 5 295 | 3,971250 M€ |
| Flux et sécurité | 6 460 | 4,845000 M€ |
| **Coût de réalisation initiale nominal** | **32 100** | **24,075000 M€** |

Cette ventilation conserve les clés hypothétiques de l'[abaque de répartition](../../../09-abaques-repartition.md) et le déploiement unique ; elle n'ajoute aucun coût. La ligne **Build Core system** porte le **cœur identifié du nominal**, hors options non ventilées. L'option Storeland peut nécessiter du code supplémentaire, mais sa composition n'est pas connue : elle reste hors de ce cœur identifié sans être retirée du coût total lorsqu'elle est activée. Dans les options Buy, la ligne **Build Core system = 0 €** : les dépenses initiales restantes financent la mise en œuvre, le spécifique et les raccordements du progiciel existant.

**Prix Flow!D14 = 1** active le nominal. Le choix **2** permet d'activer les majorations fournisseur : **15 % Storeland**, **10 % aléas** et **0 % lotissement additionnel**, soit **30,09375 M€** de fournisseur avec les valeurs de départ. La provision client de **10 %**, soit **2,4075 M€**, est alors isolée. Ces options restent disponibles mais **inactives dans la comparaison actuelle**. Elles sont calculées une fois sur le nominal et ne représentent pas une espérance statistique.

## Du prix RFI au prix Buy comparable en France

### Sources conservées et tarifs retenus

| Élément | SAP / Delaware | Microsoft / K3 / Avanade | Statut |
| --- | ---: | ---: | --- |
| Prix projet RFI / COPIL conservé | **13,462352 M€** | **4,24 M€** | Source ; périmètres distincts de FLOW |
| Charge fournisseur source | **14 640 JH** | **2 300 JH pilote** | Source ; pas de charge groupe Microsoft publiée |
| Charge de socle utilisée au central | 14 640 JH | **2 300 + 4 × 400 = 3 900 JH** | Microsoft : recomposition hypothétique |
| Tarif de dispositif France | **1 100 €/JH** | **1 250 €/JH** | Hypothèses de mix de profils vendus en France |
| Développement / extensions / TMA France | **1 050 €/JH** | **1 050 €/JH** | Hypothèses de prix distinctes du dispositif complet |

SAP : la somme **395 000 + 7 768 577 + 5 298 775 = 13 462 352 €** est conservée. Le total imprimé de **15 462 352 €** comporte un écart de **2 M€** non réconcilié, sans ajout automatique dans le modèle. Le prix implicite est **919,56 €/JH**. Microsoft : le pilote haut vaut **2,64 M€ / 2 300 = 1 147,83 €/JH** ; les lignes interfaces et développement sont à 1 000 €/JH, avec une réalisation géographique mixte.

Le dispositif France combine des profils fonctionnels, développement, architecture, pilotage et qualification. Les prix vendus et les parts de profils sont modifiables dans les onglets Prix unitaire. **Les 1 100 / 1 250 / 1 050 €/JH ne sont ni des tarifs RFI France engagés ni des médianes de marché démontrées.** Ils constituent une construction explicite de prix de forfait.

L'abaque Avanade fournit jusqu'à **400 JH par unité géographique complexe**. Le modèle retient **un pôle = une unité complexe**, soit quatre fois 400 JH au central, sans affirmer que chaque pôle correspond réellement à une seule unité. Les bornes 250–650 JH par pôle testent cette simplification. Le pont Microsoft intitulé « effet France » comprend donc **un effet de recomposition des charges et un effet de tarif**, contrairement au SAP dont la charge globale RFI reste constante.

### Fonctions Microsoft : lire la couverture avant de chiffrer les écarts

L'[abaque fonctionnel Microsoft](../../../tools/flow_ms_functional_gaps.json) et son détail dans **Passage Buy France** remplacent entièrement les anciennes fractions de coûts Make. Chaque ligne conserve la fonction cible, la couverture déclarée, la référence du questionnaire, la différence précise, les exclusions de l'effort et une activation **0/1**.

Les commandes, stock, réservations, ATP et retours, l'allocation multicritère/multisource, les recalculs, les workflows, les droits et les traces standards restent à **0 JH supplémentaires**. Les arbres de réassort, workflows d'allocation, substitutions et cockpits déjà déclarés CUS/DEV restent dans le socle RFI, dont la provision de **190–230 JH de spécifiques du pilote**. L'abaque ne prouve pas que cette provision suffit ; il ne la suppose pas non plus disponible pour de nouveaux besoins.

| Complément Microsoft conditionnel actif | Unités hypothétiques | JH par unité retenus | JH supplémentaires |
| --- | ---: | ---: | ---: |
| Parcours d'exception entre applications | 6 | 18 | **108** |
| Branches de repli entre prestataires/canaux | 4 | 25 | **100** |
| Explication ciblée des alternatives de promesse | 1 ensemble | 55 | **55** |
| Lien décision / faits / politiques / versions | 4 types | 20 | **80** |
| Applicabilité et dérogations entre familles de politiques | 1 ensemble | 107 | **107** |
| Release cohérente et activation datée des politiques | 1 ensemble | 99 | **99** |
| Vérification d'impact avant activation | 1 ensemble | 90 | **90** |
| **Total conditionnel retenu** | | | **639 JH** |

Les ensembles sont décomposés dans l'abaque. Par exemple, l'applicabilité comprend **quatre familles × 18 JH + un résolveur ciblé de 35 JH = 107 JH** ; la release **quatre objets × 16 + un mécanisme commun de 35 = 99 JH**. Il s'agit d'adaptations ciblées sur les frameworks disponibles, avec tests locaux et documentation. Aucun moteur standard complet n'est reconstruit.

**Toutes ces lignes actives sont conditionnelles**, car la différence cible n'est pas démontrée comme déjà financée dans les pièces. Cela ne démontre pas une absence du produit ou une exclusion de l'offre. Si le standard, le paramétrage ou une customisation RFI couvre la différence, son activation passe à 0. Une ligne d'objectifs supplémentaires d'optimisation reste **inactive** : les réponses positives sur les stratégies, simulations et allocations ne justifient pas de facturer une deuxième optimisation par défaut. Les quantités de parcours et les efforts sont des hypothèses d'ingénierie, pas un inventaire Beaumanoir ni une productivité observée.

La plage active est **371 / 639 / 1 026 JH**, issue des mêmes unités et d'efforts unitaires bas/retenus/hauts. Ce n'est pas une distribution de probabilité. L'ancienne simulation **6 690 JH / 7,0245 M€ de complément Microsoft**, fondée sur des fractions du Make, est **retirée**. Son ancien Coût de réalisation initiale de **13,941 M€** et son TCO de **49,759 M€** ne sont plus des valeurs actives.

### Fonctions SAP : même méthode ascendante, sans fractions de Make

L'[abaque fonctionnel SAP](../../../tools/flow_sap_functional_gaps.json) remplace les anciens pourcentages de FLOW. Il confronte les exigences au questionnaire de juillet et à la proposition Delaware de septembre : cette seconde itération inclut ou précise **S/4 Fashion, OMSA, Allocation Management, IBP et Back Office**. Une exclusion de juillet ne prouve pas l'exclusion de la proposition de septembre. Les couvertures standard **83 % SAP / 77 % Microsoft** du questionnaire RFI ne servent pas à calculer une fraction de FLOW.

Les commandes, stocks, réservations, aATP/BOP, ARun, protections par canal, simulations, règles BRF+, workflows et autorisations standards restent à **0 JH supplémentaires**. Les adaptations CUS/DEV identifiées et les **2 990 JH WRICEF** de la proposition demeurent dans le coût RFI, sans supplément automatique ni crédit supposé disponible. OMSA est proposé pour sourcing et disponibilité ; sa présence ne suffit pas à prouver tout le cycle de vie FLOW, mais elle interdit de compter une seconde construction complète. Les fonctions laissées à un WMS/TMS, à un canal, à un réassort externe ou à un portail fournisseur ne deviennent pas automatiquement des manques du cœur FLOW. L'IBP opérationnel requis par des fonctions proposées n'est pas retiré au seul motif que Finance/FP&A est hors cible.

Les mêmes unités de besoin cible sont conservées que pour Microsoft ; les adaptations locales et leur charge sont hypothétiques :

| Complément SAP conditionnel actif | Unités hypothétiques | JH par unité retenus | JH supplémentaires |
| --- | ---: | ---: | ---: |
| Parcours d'exception entre applications | 6 | 18 | **108** |
| Branches de repli entre prestataires/canaux | 4 | 18 | **72** |
| Explication ciblée des alternatives de promesse | 1 ensemble | 42 | **42** |
| Lien décision / faits / politiques / versions | 4 types | 18 | **72** |
| Applicabilité et dérogations entre familles de politiques | 1 ensemble | 100 | **100** |
| Release cohérente et activation datée des politiques | 1 ensemble | 100 | **100** |
| Vérification d'impact avant activation | 1 ensemble | 54 | **54** |
| **Total conditionnel retenu** | | | **548 JH** |

Les ensembles sont décomposés : **un contrat interne de faisabilité/coût de 18 JH + trois explications de 8 JH = 42 JH** ; applicabilité **quatre familles × 18 + un résolveur ciblé de 28 = 100 JH** ; release **quatre objets × 18 + un assemblage de 28 = 100 JH** ; impact **deux jeux × 18 + une validation de 18 = 54 JH**. Les mécanismes existants sont réutilisés ; aucun moteur SAP, OMSA, BRF+ ou solveur complet n'est reconstruit.

Les **548 JH × 1 050 = 575,4 k€** constituent une provision fonctionnelle **conditionnelle**, pas une absence confirmée de l'offre. Chaque ligne passe à 0 si le standard, le paramétrage, une adaptation RFI ou un composant inclus couvre la différence ciblée. L'optimisation supplémentaire reste inactive faute d'objectif nouveau établi. La plage active **311 / 548 / 854 JH** résulte d'efforts unitaires bas/retenus/hauts, sans distribution de probabilité. La différence d'effort SAP/Microsoft ne démontre pas une productivité différente des éditeurs.

**Réserve sur les unités du RFI SAP :** la feuille « Abaques besoins fonctionnels » contient **10 / 18 / 28** pour Low/Medium/High. Ces nombres alimentent une colonne d'**estimation de coûts supplémentaires**, sans unité établie dans l'en-tête, le format ou les commentaires examinés. **Ce ne sont pas des JH fournisseur sourcés démontrés.** Les charges de **10 / 18 / 28 JH** retenues dans certaines lignes de notre abaque sont des hypothèses locales d'ingénierie non calibrées ; elles ne constituent ni une conversion prouvée des valeurs source ni une productivité Delaware observée.

L'ancienne hypothèse SAP **4 960 JH / 5,208 M€**, calculée en fractions de Make, est **retirée**. Son ancien Coût de réalisation initiale de **24,234567 M€** et son TCO de **60,682755 M€** ne sont plus les valeurs actives.

### Prestations transverses : distinguer exclusion prouvée et provision

| Prestation transverse supplémentaire | SAP | Microsoft | Assiette / limite |
| --- | ---: | ---: | --- |
| Automatisation initiale des tests | **0 JH** | **420 JH** | SAP : aucune exclusion précise retrouvée ; Microsoft : exclusion par défaut documentée, 60 + 120 × 3 JH hypothétiques |
| Supports et accompagnement d'adoption | **360 JH** | **360 JH** | 160 JH communs + 20 marques × 10 JH ; SAP : provision conditionnelle, Microsoft : change exclu sauf utilisateurs clés/formateurs |
| Nouveaux contrats d'interface OMS | **0 JH** | **0 JH** | Aucun inventaire additionnel établi au-delà des interfaces des propositions |
| Sécurité des compléments | **0 JH** | **0 JH** | Réemploi du raccordement et des autorisations ; aucun IAM supplémentaire établi |
| Recette des nouveaux parcours de bout en bout | **0 JH** | **0 JH** | SIT/UAT et tests déjà prévus ; tests locaux des compléments dans leurs unités |
| Migration supplémentaire | **0 JH** | **0 JH** | Pas de provision générique en plus de la migration RFI |

**SAP : seul le changement/adoption reste actif**, soit **360 JH × 1 100 = 396 k€**. Les lignes dédiées « Formations » sont à zéro dans les matrices, mais cela ne prouve pas l'exclusion de toute conduite du changement : la provision est clairement hypothétique. L'automatisation TNR SAP reste non démontrée, ce qui ne permet pas d'affirmer qu'elle est absente ou gratuite ; son supplément peut être activé après identification d'un écart. Les **705 JH de migration**, les interfaces, SIT/UAT et la gouvernance déjà prévus ne sont pas additionnés de nouveau ; les deux vues des interfaces, questionnaire juillet et WRICEF septembre, ne sont pas deux budgets cumulables.

**Microsoft : les suppléments transverses actifs sont l'automatisation TNR et le changement**, exclusions documentées du courriel, soit **891 k€**. Les 40 interfaces identifiées, l'architecture et les tests RFI ne sont pas majorés faute de différence supplémentaire établie. Les abaques fonctionnels excluent ces prestations transverses de leurs efforts unitaires. L'automatisation initiale se distingue des campagnes récurrentes du MCO. Le changement complète l'adoption et les supports, hors temps client et formations d'utilisateurs clés déjà couvertes. Les **1,26 M€ de travaux IT Microsoft transférés** sont dans une ligne distincte du pont et ne sont pas réajoutés à ces fonctions ou prestations.

### Retraits hors FLOW et autonomie fournisseur

SAP détaille **2 810 JH Finance / FP&A** dans les lots 2 et 3. Le modèle en retire **70 % = 1 967 JH** : les 30 % restants préservent les données, interfaces et besoins opérationnels qui ne disparaissent pas avec la Finance. Microsoft n'a pas de ventilation comparable : **10 % de 3 900 JH = 390 JH** sont retirés pour Finance et Commerce hors cible. **Les deux fractions sont hypothétiques** ; elles ne prouvent pas une réduction commerciale disponible.

Le modèle FLOW suppose un dispositif fournisseur autonome. Pour rapprocher les responsabilités, le pont réaffecte une partie du travail IT initialement prévu côté client :

**JH transférés = JH internes × 50 % IT × 60 % transférés × part du socle conservée après retrait hors FLOW.**

Le COPIL documente **50 % IT / 50 % métier**. Les **13 993 JH SAP** sont la somme des lignes internes Delaware, différente du total imprimé de 13 393 JH. Pour Microsoft, **(8 personnes × 18 mois + 4 × 20 mois) / 12 × 200 JH/an = 3 733,33 JH** : conversion conventionnelle des équipes COPIL, pas charge observée. La fraction transférée de 60 % est une hypothèse. Il en résulte **3 633,88 JH SAP** et **1 008 JH Microsoft**, valorisés au tarif de dispositif. Sont exclus du transfert les PO et architectes déjà facturés par l'intégrateur, les nouveaux compléments déjà chiffrés et le soutien métier interne.

### Pont financier central

| Coût de réalisation initiale fournisseur HT, M€ | FLOW nominal | SAP | Microsoft |
| --- | ---: | ---: | ---: |
| Prix RFI / nominal conservé | 24,075 | 13,462352 | 4,240000 |
| Réalisation France / recomposition du socle | — | +2,641648 | +0,635000 |
| Retrait hors FLOW | — | −2,163700 | −0,487500 |
| Compléments fonctionnels ciblés / configuration | — | +0,575400 | +0,670950 |
| Prestations transverses supplémentaires | — | +0,396000 | +0,891000 |
| Travaux IT client repris au forfait | — | +3,997267 | +1,260000 |
| **Coût de réalisation initiale fournisseur comparable, retenu** | **24,075000** | **18,908967** | **7,209450** |
| **Dont Build Core system**, inclus dans le total | **15,258750** | **0** | **0** |

Les plages de Coût de réalisation initiale conditionnelles sont **14,343 à 24,581 M€ SAP** et **4,400 à 11,200 M€ Microsoft**. Elles combinent les prix, les efforts supplémentaires, les retraits et l'autonomie des hypothèses basse/haute. Chaque borne applique le retrait Finance à sa propre assiette de charge. Elles ne sont pas des quantiles et la valeur retenue n'est pas une médiane probabiliste. Les bornes ne constituent pas une réserve forfaitaire de risque. Le passage des anciennes simulations **24,234567 M€ SAP / 13,941 M€ Microsoft** aux coûts initiaux **18,908967 / 7,209450 M€** résulte du retrait des fractions Make et des suppléments transverses non démontrés ; les prix unitaires et les paniers licences ne sont pas recalibrés par cette correction fonctionnelle.

## Run : données sourcées et abaques par solution

Les anciens volumes uniformes de **2 400 JH de MCO et 1 600 JH d'évolutions** restent retirés : ils ne provenaient pas d'un dimensionnement. La version actuelle distingue les forfaits RFI, leurs conventions de normalisation France et les charges d'activité hypothétiques.

| Année pleine, avant indexation | FLOW | SAP | Microsoft |
| --- | ---: | ---: | ---: |
| MCO applicatif | **450 k€** | **302,5881 k€** | **354,0285 k€** |
| Évolutions | **240 k€** | **441 k€** | **462 k€** |
| Technique / supervision des flux | **400 k€** | **540 k€** | **540 k€** |
| Support / upgrades | 0 | **137,5 k€**, provision lissée S/4 | **50 k€**, provision Unified de base après l'année 1 |
| **Run plein hors licences** | **1,090 M€** | **1,4210881 M€** | **1,4060285 M€** |
| Service spécifique année 1 | 0 | 0 | **90 k€ Unified / PQA**, source année 1 uniquement |

Le support Unified dépend ensuite du panier facturé et de son indexation ; le montant de base n'est pas une constante contractuelle sur quinze ans. Sa provision est indépendante de la fraction applicative livrée. Le tableau annuel plein ne décrit donc pas les dépenses d'une année partiellement livrée.

### FLOW : entretien d'un produit maîtrisé

| Activité MCO | Occurrences/an, hypothèse | JH/occurrence, hypothèse | JH/an |
| --- | ---: | ---: | ---: |
| Diagnostics L2/L3 | 240 | 0,5 | 120 |
| Correctifs du produit | 60 | 3 | 180 |
| Entretien du socle logiciel | 12 | 6 | 72 |
| Régression transverse et livraisons | 12 | 6 | 72 |
| Reprises et fiabilité des flux | 48 | 2 | 96 |
| Pilotage du service | 12 | 5 | 60 |
| **Total** | | | **600** |

Les **600 JH × 750 € = 450 k€** représentent trois équivalents annuels à 200 JH, sans équipe exclusivement dédiée ni garantie de service. Le panier d'évolutions **40 règles × 2 JH + 10 fonctions/API × 12 JH + 4 évolutions structurantes × 30 JH = 320 JH**, soit **240 k€**, comprend qualification, réalisation, tests ciblés et documentation. La régression transverse reste dans le MCO.

Ces hypothèses supposent un produit stabilisé, une configuration gouvernée opérationnelle, des tests automatisés, un dispositif mutualisé en heures ouvrées, un support L1 client non valorisé et aucune astreinte dédiée. Les incidents et changements ne sont pas des volumes Beaumanoir mesurés. La provision technique de 400 k€/an reste distincte des personnels de maintenance.

### SAP : sources RFI conservées, compléments explicités

Delaware **page PDF 37** et questionnaire SAP **onglet 8 C13:C15 / D13:D15** séparent **250 k€/an MCO hors évolutions**, **350 k€/an TMA évolutive** et **450 k€/an monitoring des flux en horaires étendus**, après stabilisation. Le COPIL 5 page 7 reprend le MCO et la TMA. Les prestations standard de produit et infrastructure dans RISE ne sont pas refacturées en plus.

**Réserve de périmètre Run :** ces forfaits portent sur la proposition RFI, plus large que les seules opérations FLOW et comprenant Finance/FP&A. Le dossier ne ventile ni les JH, ni le panier d'incidents ou d'évolutions, ni une offre de service réduite. Retirer des coûts de réalisation initiale et des licences Finance ne démontre donc pas une baisse identique de ces forfaits de prestations. Les prix unitaires et conventions de normalisation France restent inchangés ; aucune réduction de Run n'est inventée à partir d'un pourcentage Finance. Seule la charge d'entretien des fonctions supplémentaires suit leur nouvel abaque.

- MCO RFI revalorisé : **250 000 × 1 050 / 920 = 285 326,09 €/an**. Ce ratio est une convention de normalisation tarifaire ; les JH réellement couverts par le forfait source restent inconnus.
- MCO des extensions nouvelles : **548 JH × 3 % = 16,44 JH × 1 050 = 17 262 €/an**. Les 3 % sont une fraction de travail annuelle hypothétique, pas un ratio de marché. Aucun supplément d'interface n'étant actif, sa maintenance additionnelle reste à zéro. Total : **285 326,09 + 17 262 = 302 588,09 €/an**.
- Évolutions : le panier commun **40 / 10 / 4 changements** à **3,5 / 14 / 35 JH** représente **420 JH × 1 050 = 441 k€/an**. Il remplace l'enveloppe RFI revalorisée de **399 456,52 €** lorsqu'il est supérieur : **MAX(forfait France ; panier métier)**, sans addition des deux.
- Supervision : **450 k€ source × 1,20 = 540 k€/an**. Le coefficient France de 1,20 est une hypothèse distincte : ni la localisation ni les effectifs de ce forfait ne sont établis par le RFI.
- Upgrades S/4 : **500 JH × 1 100 / 4 ans = 137 500 €/an**, réserve annualisée. Les 500 JH sont construits par **150 techniques + 100 adaptations + 150 tests + 50 bascule + 50 pilotage**. Le questionnaire onglet 8 C28/D28 recommande un upgrade tous les 2–4 ans, au moins tous les 7 ans ; les charges ne sont pas sourcées. OMSA cloud est exclu de cette réserve. Le modèle lisse les dépenses : il ne prédit pas les années de facturation d'un upgrade.

La réserve d'upgrade n'est pas ventilée entre le socle Finance existant et les opérations ajoutées. Elle ne démontre pas le coût marginal des seules opérations. De même, le monitoring en horaires étendus n'est pas une prestation mesurée équivalente à la provision technique FLOW. Ces différences de périmètre restent visibles, sans modifier les forfaits, les tarifs ou les licences au seul motif d'une couverture fonctionnelle révisée.

### Microsoft : extensions, campagnes récurrentes et Unified

Le COPIL 5 page 7 affiche « ? » pour MCO et TMA Microsoft. Les zéros du questionnaire ne prouvent pas la gratuité. La réponse Avanade **n° 1 page PDF 38** décrit maintenance du produit standard, infrastructure, hébergement Azure, sandbox et services managés dans la souscription ; ces postes ne sont pas ajoutés une seconde fois.

L'abaque initial est **318 JH** : diagnostics **240 × 0,5 = 120**, correctifs d'extensions/interfaces **30 × 3 = 90**, tests et adaptation aux mises à jour **4 × 15 = 60**, coordination éditeurs/intégrateur **12 × 2 = 24**, revues configuration/sécurité **12 × 2 = 24**. La charge ne mesure pas des incidents réels. À **1 050 €/JH**, elle vaut **333,9 k€**. L'entretien du seul complément fonctionnel actif représente **639 × 3 % = 19,17 JH × 1 050 = 20,1285 k€**, portant le MCO à **337,17 JH / 354,0285 k€/an**. Aucun MCO supplémentaire d'interfaces n'est activé puisque la provision de nouveaux connecteurs est à zéro. La fraction annuelle de 3 % reste une hypothèse.

Le même panier de **40 / 10 / 4 évolutions**, avec **3 / 16 / 40 JH** propres au progiciel, donne **440 JH × 1 050 = 462 k€/an**. Les différences d'effort avec FLOW et SAP sont des hypothèses de réalisation, pas une productivité comparée observée. Le tarif France remplace le proxy historique de 1 000 €/JH des développements du pilote. Supervision : proxy **450 k€ SAP × 1,20 = 540 k€/an**, sans ajouter un second hébergement Azure.

Le questionnaire Microsoft onglet 8 C28/D28 exclut un coût spécifique de montée de version, sauf les tests de non-régression et le paramétrage restant à réaliser. Les **60 JH de campagnes annuelles** figurent déjà dans le MCO : **aucun second forfait d'upgrade Microsoft n'est ajouté**.

Les **90 k€ Unified + Project Quality Advisory avec 200 heures d'ingénierie** restent comptés une fois en année 1, conformément à l'onglet 8 C13/D13. Le renouvellement dès l'année 2 est estimé par :

**MAX(50 000 USD × conversion budgétaire ; 7,5 % × part D365 × licences annuelles Microsoft/K3 facturées).**

Le taux de 7,5 % et le plancher USD figurent à l'onglet Support **E11/E14/E16/E17**. La part D365 **70 %** et la conversion **1 €/USD** sont hypothétiques : le panier Dynamics/K3 n'est pas ventilé. Après le retrait de 10 % Finance, le plancher de **50 k€** domine à la base. Le coût suit ensuite le panier effectivement facturé, sans être conditionné par le démarrage du Run applicatif. Ce renouvellement provisionnel n'est pas une clause commerciale renouvelée.

## Licences et inflation

Les taux initiaux sont **0 % prestations France**, **0 % technique/supervision**, **4 % licences SAP** et **4 % licences Microsoft après cinq ans**. Ce sont des paramètres modifiables, pas des prévisions ou clauses d'indexation vérifiées au-delà des engagements documentés.

Les souscriptions sont comptées pendant la construction. Les assiettes RFI brutes restent **790 633 / 765 823 / 973 480 / 1 270 879 / 1 270 879 € SAP**, puis dernière assiette conservée, et **979 001,51 €/an Microsoft/K3**. SAP inclut Finance et, en année 1, la maintenance Boardriders. Le gel Dynamics de cinq ans est documenté ; son application à K3 reste à confirmer.

Pour rapprocher le périmètre licences :

- SAP : le COPIL 5 page 7 compare **1,270 M€ avec Finance** et **0,870 M€ Finance déduite**, soit **400 k€/an d'écart**. Le ratio **400 000 / 1 270 879 = 31,4743 %** est appliqué à chaque assiette annuelle. L'écart source est documenté, mais **le prorata des premières années est hypothétique**, et non une nouvelle BOM commerciale.
- Microsoft : retrait **10 % Finance**, hypothèse faute de décomposition du panier. Ce retrait ne démontre pas une économie négociable de 10 % sur l'abonnement ; les offres ne fournissent pas de panier opérationnel réduit chiffré.

**Licences mensuelles** calcule 180 mois, avec hausse à l'anniversaire contractuel. Un gel de **0 ou 1 an** conserve le prix initial douze mois, puis hausse à M12 ; un gel de **5 ans** reporte la première hausse à M60. Un contrat commencé en cours d'année est proratisé avec les prix avant/après anniversaire. Les assiettes SAP restent attachées aux **années du projet** ; déplacer le contrat ne déplace pas la roadmap des assiettes.

Les bases licences RFI 2025 et les hypothèses France 2026 ne sont pas automatiquement rebasées à une valeur calendaire commune. L'horizon est relatif au lancement ; les factures ne sont pas converties selon un change futur prédit.

## Résultats avec les valeurs de départ

| Coût fournisseur cumulé depuis lancement | FLOW nominal actif | SAP comparable France | Microsoft comparable France |
| --- | ---: | ---: | ---: |
| 3 ans | **14,445 M€** | **21,713 M€** | **10,686 M€** |
| 5 ans | **24,075 M€** | **26,553 M€** | **15,385 M€** |
| 10 ans | **29,525 M€** | **39,398 M€** | **27,391 M€** |
| 15 ans | **34,975 M€** | **53,485 M€** | **40,527 M€** |

Les valeurs fournisseur à quinze ans sont **34,975000 M€ FLOW**, **53,485453945 M€ SAP** et **40,526939418 M€ Microsoft**. Les durées équivalentes de Run sont **10 / 12,7000 / 12,5667 ans**. La comparaison ne monétise pas l'avantage des livraisons Buy plus précoces. Les contributions client ne sont pas un coût complet de programme ; l'estimation porte sur le fournisseur et les transferts de tâches explicités. Les changements SAP et Microsoft résultent d'une correction de méthode et de périmètre, pas d'une amélioration démontrée de productivité.

Les anciens cumuls **40,994 / 50,918 / 36,630 M€** relevaient du modèle précédent : FLOW avec majorations actives, Buy sans le pont OMS/France/autonomie et sans ces nouveaux paramètres de Run/licences. Ils sont remplacés comme base actuelle ; ils ne doivent pas être lus comme une évolution de prix à périmètre invariant.

La sensibilité de Run demeure distincte des plages de Coût de réalisation initiale. Une variation de quantités ou d'effort ne prouve pas une probabilité. La présence des hypothèses dans un classeur modifiable rend l'ordre de grandeur discutable et révisable ; elle ne transforme pas les charges résiduelles en mesure contractuelle.

## Contrôles et limites

Les gardes du modèle vérifient les données obligatoires, les taux, les clés d'activation, les durées et les parts de Run entre 0 et 100 % avec somme à 100 %. Les coûts de fournisseur et client sont séparés ; les années de Run sont affichées. Les prix RFI restent identifiables et la nouvelle base fournisseur alimente les trajectoires, les licences corrigées et les cumuls.

L'export final du 19 octobre 2026 réussit **181 contrôles sur 181**, consignés dans le [journal](../../../tools/audit_flow_workbook.log). Ils vérifient les formules, le recalcul indépendant, les activations et agrégations des nouveaux abaques fonctionnels SAP et Microsoft, les données sources, la propagation des coûts, les bornes et les saisies invalides. Ils **ne valident pas empiriquement les quantités de fonctions, les JH unitaires ou totaux, les tarifs France, les retraits ou les transferts IT**. En particulier, ces contrôles n'établissent pas l'unité des valeurs 10/18/28 du RFI SAP. Les 169 contrôles de la version précédente ne sont pas le statut de ce nouvel export. Aucune exécution dans un moteur Excel natif n'est affirmée ici.

Les limites structurantes sont la correspondance fonctionnelle résiduelle non mesurée, l'hypothèse pôle/unité Microsoft, le partage des tâches IT, les paniers de licences réduits non devisés, les capacités de déploiement supposées et les enveloppes de Run conditionnelles. Le programme fournisseur peut être comparé sous ces conventions ; le coût complet client et les bénéfices restent à compléter séparément.
