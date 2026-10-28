> **MÉTHODE HISTORIQUE — remplacée le 20 octobre 2026. Ne pas utiliser pour établir un budget. Consulter les méthodes courantes 11 et 12 dans le dossier principal.**

![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 19 octobre 2026

---

# FLOW Make — abaques de répartition des charges

**Version de travail, 19 octobre 2026. Un seul scénario : Make.** L'objectif est de répartir sans double compte les **JH identifiés** du [modèle par postes de chiffrage](06-premier-ordre-de-grandeur-effort.md), puis de confronter cette ventilation à la [proposition SAP/Delaware](08-pont-charges-buy-make.md). Les pourcentages du second abaque sont des **clés de travail proposées**, pas des ratios de marché observés. Ils n'ajoutent **aucun JH** aux **33 100–63 600 JH identifiés** et ne valident pas l'option Storeland.

La réponse **Dynamics 365 + K3 Fashion / Avanade** du même RFI complète ce contrôle pour le **pilote seulement** : 520–630 JH d'analyse/configuration et 380–460 JH d'intégration de 40 interfaces identifiées. Ces signaux ne calibrent pas à eux seuls les clés de tout FLOW.

## Terminologie du classeur courant

**Coût de réalisation initiale** désigne toutes les prestations fournisseur nécessaires à la mise en service. Il comprend développement, configuration, interfaces, migration, architecture, qualification et déploiement. Il remplace le libellé générique « Build » dans les synthèses comparant Make et Buy.

**Build Core system** désigne la création du produit logiciel FLOW, avec son code métier, ses mécanismes de configuration et son socle technique. C'est une composante du coût initial, sans montant à ajouter au total. Pour SAP et Microsoft, cette ligne vaut **0 €** : le projet client ne reconstruit pas le produit éditeur. Les développements spécifiques du Buy restent dans les autres coûts de réalisation initiale ; les souscriptions sont comptées séparément dans le TCO.

Avec le nominal de **32 100 JH** et la livraison unique, les clés existantes donnent **20 345 JH × 750 €/JH = 15,25875 M€** de Core FLOW. Les autres coûts initiaux valent **8,81625 M€**, dont **5 295 JH de configuration = 3,97125 M€** et **6 460 JH de flux/sécurité = 4,845 M€**. Le total reste **24,075 M€**. Les clés sont des hypothèses de ventilation ; elles ne servent plus à estimer les compléments SAP ou Microsoft, calculés par fonctions ciblées.

## Abaque 1 — règle d'imputation d'une tâche

`Effort FLOW Make = Build + Intégration A (configuration/adaptation) + Intégration B (flux de données/sécurité) + réserve de périmètre non ventilée`

| Travail élémentaire | Poste Make | Critère de classement |
| --- | --- | --- |
| Fonction métier, écran, document ou traitement codé, commun ou propre à Beaumanoir | **Build** | Tout code qui réalise une fonction du produit FLOW. Le « développement spécifique » est une catégorie utile dans un projet Buy pour modifier un progiciel ; dans le Make, il fait partie du produit construit. |
| Moteur de règles/DMN, modèle d'héritage, éditeur, versionnement, simulation, API canonique, contrôle d'accès générique | **Build** | Capacité technique et métier réutilisable, indépendamment des valeurs initiales Beaumanoir. |
| Définition et saisie des politiques, règles, priorités et exceptions par marque/enseigne/ligne produit ; structure opérationnelle et valeurs des données maîtres | **Intégration A** | Décrit l'usage de FLOW par le groupe sans modifier son code. Inclut les ateliers, essais et validation de ces valeurs. |
| Nettoyage, rapprochement et validation métier des données à reprendre | **Intégration A** | Qualité et sens des données Beaumanoir ; distinguer de l'outillage technique de reprise. |
| Adaptateurs, contrats concrets, transformations, événements, API partenaires, synchronisation, contrôles/rejeu, pipelines de reprise | **Intégration B** | Connecte FLOW aux systèmes et partenaires effectivement présents. L'API canonique générique reste au Build. |
| SSO/IAM d'entreprise, fédération des identités, comptes de service, mappage des droits et secrets | **Intégration B** | Raccorde la sécurité générique de FLOW aux services, acteurs et politiques du SI Beaumanoir. |
| Tests, pilotage, bascule, formation et contribution interne | **Imputation à la tâche servie** | Affecter au Build, à A ou à B avec le livrable concerné ; si une ligne sert plusieurs postes, utiliser une clé indiquée dans l'abaque 2. Ne pas créer une quatrième enveloppe à additionner. |

## Abaque 2 — première répartition des postes de chiffrage FLOW

Chaque ligne reprend **exactement** la charge basse et haute du [modèle d'effort](06-premier-ordre-de-grandeur-effort.md). Les trois coefficients totalisent 100 % sur chaque ligne. Ils représentent une lecture du contenu décrit dans ce modèle, à remplacer par une mesure de tâches ou de livrables dès qu'elle existe. Ils incluent les contributions internes prévues dans les postes ; ils ne sont pas comparables tels quels aux seuls JH de l'intégrateur Delaware.

| Poste du modèle FLOW | JH bas–haut | Build | A : configuration | B : flux/sécurité | Motif principal de la clé |
| --- | ---: | ---: | ---: | ---: | --- |
| Operational References | 1 400–2 600 | 30 % | 35 % | 35 % | Modèle local, valeurs maîtres et ingestion d'autres SI. |
| Supply Policy Management | 1 000–2 000 | 45 % | 55 % | 0 % | Décisions métier codées et politiques initiales ; moteur commun chiffré ailleurs. |
| Inventory Management | 3 000–5 200 | 80 % | 10 % | 10 % | Ledger/réservation dominants, avec paramètres et faits externes. |
| Availability | 1 700–3 200 | 85 % | 10 % | 5 % | Calcul et cohérence du stock dominants. |
| Order Management | 3 500–6 500 | 75 % | 15 % | 10 % | Modèle et états des commandes, variantes puis échanges de canal. |
| Process Management | 1 800–3 600 | 80 % | 20 % | 0 % | Cases et outils communs ; dossiers et processus initiaux configurés. |
| Fulfilment Orchestration | 1 800–3 200 | 70 % | 15 % | 15 % | Décision de plan, policies et échanges avec les exécutants. |
| Service Management et documents | 1 400–2 800 | 70 % | 20 % | 10 % | Fonction et production documentaire, variantes, destinataires. |
| Master Plan et Order Backlog | 3 500–6 500 | 75 % | 20 % | 5 % | Solveur/carnet, contraintes et données nécessaires aux runs. |
| Plateforme de configuration gouvernée | 4 000–8 000 | 100 % | 0 % | 0 % | Construction du mécanisme ; règles initiales déjà dans les postes métier. |
| Interfaces et contrats inter-systèmes | 3 000–6 000 | 15 % | 0 % | 85 % | Contrats canoniques du produit puis adaptateurs et tests de flux. |
| Migration et coexistence | 2 000–4 000 | 0 % | 40 % | 60 % | Qualité/règles de reprise puis outillage, chargement et rapprochement technique. |
| Plateforme technique et qualification de bout en bout | 3 000–6 000 | 75 % | 5 % | 20 % | Plateforme et tests du produit ; environnements métier et raccordement de sécurité/flux. |
| Déploiement et accompagnement | 2 000–4 000 | 0 % | 70 % | 30 % | Préparation des acteurs et paramètres puis bascule des connexions. |
| **Total identifié** | **33 100–63 600** | **20 345–38 790** | **5 995–11 585** | **6 760–13 225** | Sommes des produits `JH du poste × clé`. |

Ainsi, l'**Intégration Make identifiée** par cet abaque est **12 755–24 810 JH** (A + B). Ce résultat dépend des clés ci-dessus : il ne constitue pas encore une charge observée. L'option de **15 % de la base identifiée** pour les composants Storeland non découverts reste **4 965–9 540 JH non ventilés**, hors nominal. Le contrôle arithmétique est `20 345 + 5 995 + 6 760 = 33 100 JH` en borne basse et `38 790 + 11 585 + 13 225 = 63 600 JH` en borne haute ; avec l'option, les totaux deviennent **38 065–73 140 JH**. Affecter cette option à A, B ou au Build avant découverte créerait une précision fictive.

Une variation de **10 points** dans une clé transfère `10 % × JH du poste` entre catégories sans changer le total. Elle représenterait par exemple **400–800 JH** pour la plateforme de configuration, **350–650 JH** pour Order Management ou Master Plan, et **300–600 JH** pour les interfaces. Les clés les plus déterminantes à challenger sont donc celles des grands postes mixtes.

## Abaque 3 — repères Buy observés, sans conversion automatique en Make

La page 41 de Delaware détaille **2 990 JH d'intégrateur WRICEF** dans les lots 2 et 3. Rapportés aux **14 219 JH d'intégrateur** imprimés pour ces deux lots, ces postes forment le contrôle suivant :

| Poste observé dans le Buy | JH intégrateur | Part des 14 219 JH | Usage pour l'abaque Make |
| --- | ---: | ---: | --- |
| Enhancements, rapports, formulaires, Fiori | **1 319** | **9,3 %** | Spécifiques du projet SAP ; examiner les **besoins** un à un. Ceux à coder en Make vont au Build, sans reprendre cette charge SAP comme tarif de développement FLOW. |
| Entrées et sorties | **1 467** | **10,3 %** | Repère partiel d'interfaces Buy pour questionner les adaptateurs et tests du poste B. |
| Conversions | **204** | **1,4 %** | Repère technique partiel de migration, à rapprocher du poste B ; la préparation des données du poste A n'est pas isolée. |
| Reste des lots 2 et 3, non ventilable par nature avec ce détail | **11 229** | **79,0 %** | Comprend notamment conception, paramétrage, tests, gouvernance et autres tâches ; **ne pas assimiler ce reste à la configuration**. |
| **Total lots 2 et 3** | **14 219** | **100 %** | Charges proposées de l'intégrateur, pas charge consommée. |

Les pages 39–40 montrent aussi **10 640 JH** par domaines fonctionnels, **717 JH** de reprise/tests et **2 861 JH** de gouvernance, coordination et infrastructure, soit **14 218 JH** par addition des sous-totaux affichés ; l'écart d'**1 JH** avec 14 219 vient des arrondis du tableau. Le WRICEF est **inclus** dans ces charges et ne s'y ajoute pas. Aucun sous-total de **configuration** ou de **raccordement à la sécurité** n'est publié. L'abaque 2 ne doit donc pas être présenté comme un ratio calibré par Delaware.

**Contrôle de source à résoudre avant une comparaison de l'effort programme :** la page 38 indique **14 640 JH intégrateur** et **13 393 JH internes** en total, soit **28 033 JH**. Mais ses trois lignes internes affichent **218 + 8 034 + 5 741 = 13 993 JH**, et les lignes combinées conduisent à **28 633 JH**. La différence est de **600 JH**. La somme des lignes intégrateur (421 + 8 446 + 5 773) confirme 14 640 JH. Tant que la charge interne n'est pas clarifiée, conserver **les deux lectures** et ne pas utiliser 28 033 JH comme mesure exacte de répartition.

## Mode d'emploi pour la prochaine itération

1. Pour chacun des grands postes mixtes de l'abaque 2, décrire quelques livrables représentatifs et les classer avec l'abaque 1 ; remplacer la clé provisoire par la part de JH estimée pour ces livrables.
2. Pour la configuration, compter séparément les familles de règles et politiques initiales, les axes de variation et les opérations de gouvernance ; pour B, compter les contrats/objets/sens, reprises, partenaires et le branchement IAM/SSO.
3. Rapprocher les **postes Buy homologues** de A et B, après retrait des fonctions hors FLOW ; traiter les développements spécifiques Buy comme des **indices de besoins**, pas comme une troisième enveloppe Make.
4. Garder l'option Storeland hors nominal et non ventilée jusqu'à identification des composants ; ne pas additionner le Buy brut au total FLOW.

Les deux abaques servent déjà à discuter de façon concrète **où se trouvent les JH**. Ils ne transforment pas, à eux seuls, la plage initiale en estimation de coût ou de délai validée.

