> **MÉTHODE HISTORIQUE — remplacée le 20 octobre 2026. Ne pas utiliser pour établir un budget. Consulter les méthodes courantes 11 et 12 dans le dossier principal.**

![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 19 octobre 2026

---

# Méthode d'estimation du coût, du délai et des moyens FLOW Make

**Statut :** méthode de travail, 19 octobre 2026. **Unité de décision :** un seul scénario d'architecture, Make. **Unité d'effort :** jour.homme (JH) ; les ETP servent à exprimer une capacité par période. Les options Flowable, règles, solveur et stockage sont des décisions techniques internes à ce scénario.

L'estimation part des fonctions et variantes à construire, puis les convertit en charge d'équipes, en calendrier avec dépendances et en coût complet. Chiffre d'affaires et nombre de pièces vendues décrivent l'activité, mais ne sont pas des multiplicateurs du coût logiciel. Les volumes de transactions et les pics servent au dimensionnement et aux tests de performance.

## 1. Décomposer les travaux

| Poste de chiffrage | Contenu à inventorier | Principaux facteurs de charge |
| --- | --- | --- |
| Référentiels opérationnels | Articles et variantes, lieux, entités, partenaires, contrats de données | Nombre de systèmes maîtres, qualité des données, variantes internationales |
| Achats | Commandes, modifications, suivi, réception et écarts | Processus distincts, fournisseurs, intercompany, interfaces |
| Ventes et retours | Commandes B2C et Wholesale, retours, déstockage | États, exceptions, canaux, lignes de commande |
| Stock et availability | Stock physique consolidé, engagements, protection, réservation, ATP/CTP/PTP | Sémantique du stock, concurrence, pics, latence admise |
| Allocation et optimisation | AllocationRun, backorders, plan de fulfillment, solveur | Contraintes, objectifs, taille des problèmes, temps de calcul admis |
| Documents et dossiers | Factures opérationnelles, bons, cas d'exception, tâches | Types de documents, variantes pays, acteurs, durées de conservation |
| Intégrations | Canaux, commerce, logisticiens, finance, partenaires étrangers | Nombre et qualité des interfaces, formats, fréquence, reprises |
| Migration et bascule | Données historiques utiles, commandes ouvertes, stock de départ, coexistence | Sources, qualité, règles de reprise, vagues |
| Plateforme et sécurité | Hébergement, CI/CD, observabilité, habilitations, sauvegarde, reprise | Exigences de service, environnements, exploitation |
| Déploiement et change | Tests métier, formation, support de bascule, adoption | Marques, pays, rôles utilisateurs, vagues |

Pour chaque poste de chiffrage, séparer le **Build du produit**, qui comprend aussi les développements métier propres à Beaumanoir, et les deux charges d'intégration Make : **(A) configuration et adaptation au contexte** (données maîtres, règles, policies, entités, marques et lignes produit), **(B) développement des flux de données et raccordement de la sécurité**. Les tests, migrations, déploiements et contributions métier sont ventilés entre ces postes selon leur objet. Une marque de plus ne crée pas automatiquement un nouveau poste complet ; seule sa différence effective par rapport au socle ajoute de la charge. Une règle de marque exprimée sans code est de la configuration ; si elle requiert du code, sa réalisation appartient au Build.

## 2. Mesurer la complexité de configuration

Établir un catalogue des règles avec, pour chaque entrée : famille de décision, propriétaire métier, axes d'application, priorité, exceptions, fréquence de modification, nombre d'instances actives, données nécessaires, objectif de délai de publication, besoin de simulation et criticité. Classer ensuite la réalisation : paramètre simple, table de décision, règle déclarative, workflow/case, solveur, ou code.

Mesurer séparément le coût de **construction de la capacité de paramétrage** et celui de **saisie des règles initiales**. Le coût d'une nouvelle règle après mise en service devient un indicateur du résultat : jours métier, jours IT, délai de publication et nombre de déploiements de code. Comparer ce coût récurrent à la situation actuelle avec les évolutions éditeur.

## 3. Collecter les données de charge technique

Demander, pour chaque canal et par période de pic : commandes, lignes, tickets, consultations d'availability, tentatives et confirmations de réservation, mouvements de stock, retours et documents produits. Ajouter cardinalité des couples article-variante × lieu, nombre de lieux et de partenaires, temps de réponse attendu, retard maximum admis, disponibilité de service et fenêtre de traitement des allocations.

Les **120 millions de pièces annuelles** sont un contrôle de cohérence, pas un débit de requêtes. Le dimensionnement doit utiliser les pics horaires, la concurrence entre canaux et les tailles des problèmes soumis au solveur. Les commandes Wholesale, tickets Retail et commandes B2C doivent être comptés séparément.

## 4. Calibrer par prototypes et données de marché

1. **Configurabilité :** implémenter trois règles représentatives — protection de stock, priorité d'allocation et exception par marque/ligne produit — avec tests, simulation, publication et retour arrière. Comparer DMN/Flowable à un développement ciblé.
2. **Stock :** rejouer des mouvements et réservations concurrents à la volumétrie de pic, provoquer des pannes et mesurer non-survente, latence, rattrapage et reconstruction des projections.
3. **Solveur :** exécuter les mêmes problèmes d'allocation dans Timefold et OR-Tools, sur des jeux proches de la production. Mesurer qualité de solution, temps, mémoire et effort de modélisation.
4. **Intégration :** réaliser un flux représentatif de bout en bout avec un canal et un logisticien, incluant rejets, doublons et rapprochement.

Les prototypes ne se limitent pas à mesurer la performance : ils donnent une productivité de réalisation observable, la charge d'exploitation et le nombre de rôles nécessaires. Étalonner les coûts de personnel avec les données RH et des tarifs récents pour les profils réellement mobilisés ; les références publiques seules ne constituent pas un devis.

### Triangulation par références de marché

Confronter le modèle de moyens à trois observations distinctes, consignées dans les [références de marché](03-references-marche.md) : **plateformes Fashion comparables** pour la surface fonctionnelle et la durée de transformation ; **logiciels ouverts** pour mesurer le code et les modules correspondant aux capacités FLOW ; **dépenses publiées et tarifs de compétences** pour contrôler l'échelle financière. La comparaison doit conserver les différences de périmètre et de mode d'exploitation. Aucun ratio « euro par ligne de code » ou « pourcentage du chiffre d'affaires » n'entre directement dans le budget.

Le calcul par lignes de code ne devient exploitable qu'après sélection des modules comparables, mesure reproductible sur une version figée et calibration avec des réalisations FLOW. Les coûts théoriques produits par un modèle comme COCOMO restent distincts des coûts effectivement dépensés par l'éditeur du logiciel témoin.

### Point d'ancrage interne Synvance 2025

L'[analyse des pièces Synvance et de la poursuite du RFI](07-analyse-synvance.md) fournit un repère plus proche que les benchmarks publics : la proposition SAP/Delaware de septembre, **postérieure à la mission Synvance**, chiffre **14 640 JH d'intégrateur**. Elle affiche **13 393 JH internes** en total, mais les trois lignes internes somment à **13 993 JH** : le programme Buy représente donc **28 033 JH affichés ou 28 633 JH par somme des lignes**, écart de **600 JH** à clarifier. Comparer les fonctions homologues avant de corriger le modèle FLOW. Le RFI contient déjà des commandes B2C/magasins, du stock et de l'allocation ; l'offre SAP inclut même un composant OMS. La charge de paramétrage de ces fonctions dans un ERP existant ne se convertit pas directement en charge de développement Make ; inversement, l'offre SAP contient FICO et IBP hors FLOW. Le retour oral sur la sous-estimation des RFI justifie un examen des exclusions et de l'incertitude, pas un coefficient de majoration présumé.

La seconde option Buy était **Dynamics 365 + K3 Fashion / Avanade**. Avanade détaille **1 900–2 300 JH pour un pilote**, dont **520–630 JH** d'analyse/configuration et **380–460 JH** d'intégration de 40 interfaces identifiées. Le COPIL de septembre retient **2,64 M€** pour ce pilote à la borne haute des coûts Avanade, plus **1,60 M€** projetés pour quatre autres pôles. Ces **4,24 M€** ne sont pas un devis de réalisation complet en JH et ne se substituent pas aux charges Delaware sans normalisation du périmètre.

Pour calculer FLOW Make, séparer **Build du produit** et les **deux charges d'intégration** définies plus haut. Le [pont de charges Buy → Make](08-pont-charges-buy-make.md) traite le total Buy comme référence brute d'implémentation programme, puis indique les retraits et ajouts à documenter. Les 2 990 JH de WRICEF signalés par Delaware sont un détail des travaux de réalisation, pas une somme à ajouter : ils éclairent une partie des développements spécifiques au Buy et des interfaces, sans isoler la configuration ni la sécurité. Le [premier abaque de répartition](09-abaques-repartition.md) propose des clés explicites pour le modèle FLOW. Le modèle antérieur par postes de chiffrage contient déjà des charges d'intégration ; on doit **substituer** des charges calibrées aux hypothèses comparables, pas additionner le total Buy à l'estimation FLOW.

En complément, sélectionner quelques processus FLOW représentatifs et mesurer leur **taille fonctionnelle** avec une méthode indépendante de Java, comme [COSMIC](https://cosmic-sizing.org/cosmic-sizing/intro/). Cela permet de comparer la productivité du projet à des références de [projets de taille comparable](https://www.isbsg.org/2025/02/06/functional-size-measurement/) sans confondre volume de code, fonctionnalités livrées et effort total d'intégration.

## 5. Calculer les moyens, coûts et délais

Pour chaque poste de chiffrage, établir trois estimations de **jours par rôle** — basse, centrale, haute — justifiées par les fonctions et variantes identifiées. Additionner les postes en tenant compte des ressources partagées et des risques corrélés. Le coût de réalisation est la somme des jours × coût complet interne ou tarif externe, augmentée de l'infrastructure, du support des composants retenus, des migrations, de la coexistence avec les anciens systèmes et d'une réserve de risque identifiée. Éviter d'ajouter un pourcentage de contingence sur un risque déjà chiffré dans un poste.

Le calendrier suit les dépendances : modèle de stock et de commande → règles de promesse → allocation → flux de fulfillment → pilotes et bascules. La durée ne se déduit pas par division de la charge totale par le nombre de personnes. Présenter l'effectif moyen et au pic, par compétence, ainsi que l'équipe permanente nécessaire après la fin du programme.

Le [premier ordre de grandeur d'effort](06-premier-ordre-de-grandeur-effort.md) remplace la trajectoire d'équipes supposées comme point de départ : il décompose le domaine Supply Chain Management publié, le socle de configuration et les interfaces en JH par poste de chiffrage. Le périmètre Storeland non découvert est chiffré séparément comme option de 15 % de cette base identifiée. Les charges unitaires restent des hypothèses d'ingénierie non calibrées ; les coûts et délais ne se déduisent pas mécaniquement du nombre de JH. L'ancienne simulation financière de [résultats](04-resultats-etude.md) reste documentée comme historique, sans validation par la nouvelle estimation d'effort.

Comparer le coût de réalisation au **coût total de possession** sur un horizon fixé par Beaumanoir, par exemple cinq ou sept ans : maintenance évolutive, exploitation, infrastructure, support et montée de version des composants open source. Le caractère gratuit d'une licence n'implique pas un coût d'exploitation nul.

## 6. Restituer une estimation vérifiable

Le dossier final doit contenir une fourchette coût/délai, une courbe d'effectifs, les coûts récurrents, une ventilation par poste de chiffrage, les hypothèses et exclusions, les dix premiers risques, ainsi que les résultats des prototypes. Chaque chiffre doit renvoyer à une charge, un tarif ou un prix observable. Une révision est nécessaire après l'inventaire des variantes et interfaces, puis après les pilotes de performance.

## Données nécessaires au prochain calcul

### Informations qui resserreront l'ordre de grandeur de charge

La cartographie Supply Chain Management, le mini cahier des charges de configuration et les interfaces cibles suffisent pour un **premier ordre de grandeur conditionnel nominal** en JH ; l'option Storeland de 15 % rend visible le périmètre non découvert. La liste suivante n'est pas un préalable imposé à ce calcul : ce sont les informations qui permettraient de remplacer ses hypothèses de charge et de resserrer sa plage, avec des comptes même approximatifs et leur provenance. Le lotissement détaillé des déploiements peut rester inconnu à ce stade.

| Priorité | Information minimale | Ce qu'elle détermine |
| --- | --- | --- |
| 1 | **Capacités et frontière Make** : pour chaque application remplacée et chaque processus achats, ventes, retours, stock, promesse, allocation, documents et fulfillment, indiquer conserver, reconstruire, connecter ou abandonner ; préciser les actifs internes réutilisables. | Nombre de fonctions et de parcours de bout en bout à construire ; évite de compter deux fois ou d'omettre une fonction. |
| 2 | **Variantes réellement distinctes** : échantillon de règles et processus par marque, pays, canal et entité, avec exceptions et fréquence des changements ; nombre de règles simples, décisions, dossiers et traitements optimisés. | Taille du socle de configuration, des règles initiales et des extensions de code ; c'est le principal risque d'effet « vingt ERP ». |
| 3 | **Interfaces et données** : liste des systèmes et partenaires, objets échangés, sens, fréquence, qualité actuelle, nombre d'adaptateurs spécifiques ; données actives et historiques à migrer. | Charge d'intégration, reprise, tests et coexistence, potentiellement aussi importante que le produit central. |
| 4 | **Scénarios de charge et niveau de service** : pics de commandes/lignes, réservations et consultations d'availability par canal ; nombre de couples variante × lieu ; taille d'un run d'allocation, latence et disponibilité attendues. | Architecture de stock, complexité du solveur, résilience et effort de validation ; le volume annuel de pièces ne remplace pas les pics. |
| 5 | **Séquence de déploiement** : entités pilotes, nombre de vagues, magasins/canaux/partenaires concernés, durée de coexistence et fenêtres de bascule. | Durée, effectifs de migration et de change, prolongation éventuelle des anciens SI. |
| 6 | **Étalonnage d'effort** : charge observée sur deux ou trois évolutions internes comparables et sur un flux intégration/migration ; sinon, réalisation d'un court prototype représentatif. | Transformation du nombre de fonctions et d'interfaces en jours par rôle. Sans cette donnée, les années-personnes restent un jugement non calibré. |

**Effort ≠ coût ≠ calendrier.** Les JH se convertissent en ETP-années seulement avec une convention de jours par an ; ils se convertissent en euros avec les coûts par rôle, le mix interne/externe, l'infrastructure et la coexistence. Le délai dépend des dépendances et des capacités réelles de mobilisation ; son premier ordre de grandeur peut utiliser des vagues génériques sans connaître le lotissement final. Les comptes financiers de Beaumanoir servent à juger la soutenabilité du coût obtenu, pas à produire l'effort.

### Liste détaillée pour la collecte

- Carte des fonctions à reprendre de SAP ECC AFS, Storeland, UR, Socloz et NewStore.
- Catalogue des règles actuelles et modifications demandées sur les deux dernières années, avec coût et délai de réalisation lorsqu'ils sont connus.
- Inventaire des marques, pays, entités juridiques, partenaires et écarts de processus.
- Catalogue des interfaces avec source, cible, format, fréquence, volumétrie et qualité.
- Volumes de transactions et pics par canal, lignes de commande et lieux de stock.
- Stratégie de migration, ordre des vagues et niveau de coexistence accepté.
- Coûts internes complets, répartition interne/externe envisagée et niveaux de service cibles.

La décomposition des travaux, les estimations par analogie ou par construction détaillée, et l'analyse de l'incertitude suivent les principes du [GAO Cost Estimating and Assessment Guide](https://files.gao.gov/assets/gao-20-195g.pdf). Leur application à FLOW est décrite ci-dessus ; le guide ne fournit aucun coefficient de coût propre au projet.

