> **MÉTHODE HISTORIQUE — remplacée le 20 octobre 2026. Ne pas utiliser pour établir un budget. Consulter les méthodes courantes 11 et 12 dans le dossier principal.**

![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 19 octobre 2026

---

# FLOW Make — premier ordre de grandeur d'effort en jours.homme

**Version de travail, 19 octobre 2026. Un seul scénario : Make.** Cette estimation vise la réalisation et le déploiement de FLOW sur le périmètre opérationnel décrit dans le [cahier des charges](01-cahier-des-charges.md). L'unité de calcul est le **jour.homme (JH)**. Pour exprimer une capacité, **1 ETP pendant un an = 200 JH affectés au projet** est une convention de conversion, non une définition de l'ETP ni un tarif. Ainsi, 40 000 JH correspondent à 200 ETP-années ; ils ne donnent pas seuls une durée calendaire.

## Résultat conditionnel

**33 100 à 63 600 JH identifiés**, avant ajustement pour une mise en service unique. L'option Storeland non découverte de **15 % de cette base** porte la plage à **38 065–73 140 JH**, soit approximativement **40 000 à 75 000 JH** et **190 à 366 ETP-années** avec la convention de 200 JH/an. C'est un premier modèle de charge construit par **postes de chiffrage** à partir de la cartographie publiée, du mini cahier des charges de configuration et des interfaces annoncées. Les charges unitaires par poste sont des **hypothèses d'ingénierie**, non des charges constatées chez Beaumanoir ou un coût de marché observé. La plage est donc révisable ; elle ne vaut pas engagement, planning ou prix. Un poste regroupe ici des travaux à estimer ; les **lots de la roadmap** seront définis séparément.

Le modèle de référence est le domaine [Supply Chain Management de la release 2026-10-17.1](<C:/Dev/Beaumanoir Cartographie/modeles/release/2026-10-17.1/model.yaml>) du projet Beaumanoir Cartographie. Il comprend **9 sous-ensembles, 28 Business Areas, 88 capacités et 74 comportements**. Ces nombres servent à contrôler la couverture : une capacité métier peut nécessiter plusieurs composants, tandis que plusieurs capacités peuvent partager un seul composant. **Aucun tarif en JH par capacité n'est appliqué.** La cartographie ne prouve pas qu'une capacité est déjà réalisée ou doit être codée intégralement dans FLOW.

## Hypothèses de périmètre retenues

- FLOW porte les commandes d'achat, vente, transfert et retour, le stock logique et ses engagements, Availability/ATP/CTP/PTP, le carnet et les décisions d'allocation, le plan opérationnel, l'orchestration du fulfillment, les commandes de prestation et les documents opérationnels. Les priorités Wholesale, Retail et B2C partagent un socle.
- Les systèmes de canal restent autonomes. Les WMS/TMS et les prestataires réalisent l'exécution logistique ; FLOW commande les prestations et rapproche leurs retours. La finance, le contrôle de gestion, les maîtres produit/prix et la planification stratégique restent hors du cœur développé.
- Certaines capacités de la cartographie sont **partiellement** reprises : les références d'entreprise, produit et prix sont ingérées, pas recréées comme maîtres ; la facturation opérationnelle produit des documents et données, sans comptabilité ; le paiement, les douanes, le process mining et l'exécution de chaque prestation logistique ne sont pas présumés à développer.
- Le mini cahier des charges [Gestion de la configuration](sources/Gestion%20de%20la%20configuration.pdf) est une exigence du produit. Il ajoute un sous-produit transverse de configuration autonome et gouvernée : hiérarchie non figée, héritage, priorités et dérogations, décisions croisant demande longue, état de la supply chain et politiques, gouvernance par objets métier, versions et releases, simulation, approbation, activation, habilitations, retour arrière, audit et provenance des décisions. Les agents IA ne sont pas inclus dans l'effort.
- L'inventaire d'interfaces annoncé couvre PLM + Commerce (produit, article, prix), contrôle de gestion (credit check), SAP FI/CO (structures juridiques et partenaires), prestataires logistiques (API de commandes de fulfillment et retours). Des contrats avec les canaux Retail, B2C et Wholesale sont également nécessaires pour que la cible omnicanale fonctionne ; leur nombre de connecteurs n'est pas encore connu.
- Faute de lotissement, la charge de déploiement suppose un pilote puis plusieurs bascules réutilisant le même cœur. Elle n'impose pas de nombre de vagues ou d'ordre des marques. La migration vise les données opérationnelles actives, commandes ouvertes, stocks de départ et références nécessaires, pas tous les historiques.

## Construction de l'effort identifié

Les intervalles suivants couvrent, dans chaque poste fonctionnel, analyse, conception, réalisation, écrans opérationnels nécessaires, tests de composant et tests fonctionnels du poste. Ils représentent des équipes pluridisciplinaires, métier inclus pour leur contribution au projet. Les travaux transverses ci-dessous ne sont pas répétés dans les postes fonctionnels. Les bornes sont un jugement de charge fondé sur la largeur et la difficulté des responsabilités cartographiées ; aucune productivité par fonction n'a encore été mesurée.

| Poste tiré du domaine Supply Chain Management | Basse JH | Haute JH | Principal moteur de charge |
| --- | ---: | ---: | --- |
| Operational References | 1 400 | 2 600 | Références locales et ingestion des maîtres externes, sans recréer le PLM ni le Commerce. |
| Supply Policy Management | 1 000 | 2 000 | Politiques métier initiales, protection et éligibilité ; moteur de configuration commun compté séparément. |
| Inventory Management | 3 000 | 5 200 | Ledger, positions, propriété, réservations, correction et rapprochement des faits. |
| Availability | 1 700 | 3 200 | ATP, CTP, PTP et explication de la promesse avec engagements concurrents. |
| Order Management | 3 500 | 6 500 | Plusieurs familles de commandes, versions, exceptions, retours, intercompany et structuration. |
| Process Management | 1 800 | 3 600 | Cases, tâches, interventions et supervision ; process mining exclu. |
| Fulfilment Orchestration | 1 800 | 3 200 | Décision de plan de fulfillment, coordination, suivi et adaptation sans WMS/TMS. |
| Service Management et documents | 1 400 | 2 800 | Commandes de prestation et documents opérationnels ; paiement et exécution logistique exclus. |
| Master Plan et Order Backlog | 3 500 | 6 500 | Calcul opérationnel, optimisation, arbitrage du carnet et runs d'allocation. |
| **Sous-total fonctionnel identifié** | **19 100** | **35 600** | |

| Travaux transverses | Basse JH | Haute JH | Inclus / frontière |
| --- | ---: | ---: | --- |
| Plateforme de configuration gouvernée | 4 000 | 8 000 | Modèle d'applicabilité, éditeur, conflits, cycle de vie, simulation, provenance et audit ; les règles métier initiales sont dans les postes fonctionnels. |
| Interfaces et contrats inter-systèmes | 3 000 | 6 000 | Contrats des quatre familles annoncées et des canaux ; adaptateurs, rejeu, erreurs, observabilité. |
| Migration et coexistence | 2 000 | 4 000 | Reprise des objets actifs des systèmes remplacés, rapprochement et double fonctionnement temporaire. |
| Plateforme technique et qualification de bout en bout | 3 000 | 6 000 | Environnements, CI/CD, sécurité, résilience, performance, tests inter-domaines et exploitation initiale. |
| Déploiement et accompagnement | 2 000 | 4 000 | Pilote, préparation des bascules réutilisables, formation et support de démarrage ; vagues détaillées non requises pour ce modèle. |
| **Sous-total transverse identifié** | **14 000** | **28 000** | |

**Effort identifié : 33 100 à 63 600 JH.** Les bornes hautes ne sont pas des « risques » ajoutés deux fois ; elles reflètent une complexité plus élevée pour chaque poste. Les montants doivent être remplacés par des charges observées si des références internes comparables deviennent disponibles.

## Option de 15 % pour le périmètre Storeland non découvert

Les composants de *Sourcing and Procurement* et de *Commerce* nécessaires au décommissionnement de Storeland ne sont pas encore identifiés. Ils sont chiffrés en **option de 15 % de l'effort identifié**, hors nominal. Cette option est **distincte** du moteur de configuration et des interfaces déjà comptés :

`effort avec option Storeland = effort identifié × (1 + 0,15)`

| Calcul | Basse | Haute |
| --- | ---: | ---: |
| Effort identifié | 33 100 JH | 63 600 JH |
| Option Storeland 15 % de l'effort identifié | 4 965 JH | 9 540 JH |
| **Total avec option** | **38 065 JH** | **73 140 JH** |
| **Ordre de grandeur exprimé** | **40 000 JH** | **75 000 JH** |

Cette option n'affirme pas que les capacités manquantes seront exactement 15 %. Elle rend visible leur place dans l'ordre de grandeur. Si elles représentaient plutôt 25 % de l'effort identifié, le total avec option deviendrait environ **41 000 à 80 000 JH**. Ce test montre l'effet de la seule hypothèse de périmètre, sans ajouter un second scénario d'architecture.

## Ce que l'ordre de grandeur permet et ne permet pas

- Il fournit une **charge de réalisation** à comparer aux ressources mobilisables ; le pic d'ETP et le délai dépendent de la parallélisation, des dépendances et de la séquence de bascule. Aucun nombre de vagues n'est demandé pour retenir cette première plage.
- Il ne fixe pas le coût en euros. La conversion utilisera des coûts journaliers par rôle et la part interne/externe, plus les coûts non salariaux et l'exploitation après programme. Les données de santé financière de Beaumanoir jugent la soutenabilité du coût, pas la charge en JH.
- Les trois facteurs qui peuvent déplacer le plus la plage sont la difficulté réelle du **stock/réservation sous concurrence**, celle du **socle de configuration avec provenance et versions**, et le nombre réel de **connecteurs/migrations**. Un échantillon de flux ou une mesure de charge interne sur ces trois points suffira à réviser le modèle ; il n'est pas nécessaire de cadrer toutes les marques et vagues avant d'énoncer cet ordre de grandeur.
- Les **120 millions de pièces par an** ne multiplient pas le travail fonctionnel. Les pics de transactions serviront à confirmer la part performance/résilience des postes concernés, sans bloquer ce premier calcul.

## Traçabilité des hypothèses

| Élément | Origine | Statut |
| --- | --- | --- |
| Périmètre SCM et hiérarchie | [Publication Beaumanoir Cartographie 2026-10-17.1](<C:/Dev/Beaumanoir Cartographie/modeles/release/2026-10-17.1/model.yaml>) | Modèle métier publié ; implémentation non démontrée. |
| Configuration autonome et gouvernée | [Mini cahier des charges fourni](sources/Gestion%20de%20la%20configuration.pdf) | Exigence exprimée, à réaliser. |
| Interfaces et option Storeland de 15 % | Précisions de Laurent dans cette conversation | Hypothèses de périmètre de l'étude. |
| JH par poste, 200 JH/ETP-an, migration active, pilote et bascules | Construction de l'estimation | Hypothèses d'ingénierie, non mesures ni engagements Beaumanoir. |

## Contrôle avec l'étude Synvance 2025

La [proposition SAP/Delaware de septembre 2025 analysée ici](07-analyse-synvance.md) affiche **28 033 JH** en comptant intégrateur et équipe interne pour l'implémentation d'une solution Buy dans le même groupe, mais la somme de ses lignes est **28 633 JH** (écart de **600 JH** sur la charge interne). Elle apporte une comparaison de **charge proposée**, pas une charge effectivement consommée. La lecture des pièces corrige la première hypothèse de périmètre : le RFI demandait déjà commandes B2C et magasins, stock, promesse, allocation et flux d'expédition ; la proposition SAP **incluait SAP OMSA**, S/4 Allocation Management et un back office magasin. Elle incluait aussi FICO et IBP, hors cible FLOW actuelle. FLOW construit en Make un cœur dont certaines **fonctions** recoupent donc l'offre Buy, avec d'autres exigences et un autre mode de réalisation. La plage **40 000–75 000 JH** n'est ni recalculée ni déclarée validée par ce seul chiffre. Le prochain recalage consiste à rapprocher les responsabilités et charges **fonction par fonction**, puis à estimer l'écart de construction du produit, d'intégration, de migration, de tests et de déploiement.

L'autre option du RFI, **Dynamics 365 + K3 Fashion / Avanade**, donne **1 900–2 300 JH** pour son **pilote uniquement**. Le COPIL 5 projette **4,24 M€ de coûts projet** pour le pilote et quatre pôles, sans charge full scope détaillée en JH. Ce second repère documente surtout la configuration, les interfaces et les tests d'une solution Buy ; les **77 % de couverture standard du RFI** ne représentent pas un pourcentage du périmètre FLOW.

Le [pont de charges Buy → Make](08-pont-charges-buy-make.md) explicite la séparation **Build + Intégration Make** et la ventilation observable de l'offre SAP/Delaware. Un [premier abaque](09-abaques-repartition.md) répartit les postes identifiés ci-dessus entre **Build**, **configuration/adaptation** et **flux/sécurité**, sans y inclure l'option Storeland de 15 %. Ajouter le total Buy à la plage existante serait un double compte. La plage actuelle reste une hypothèse de travail jusqu'à la substitution des charges d'intégration comparables.

Le [minimum nominal en euros](11-cout-nominal-minimum.md) est un **calcul dérivé de la borne basse**, sous des hypothèses différentes pour le déploiement et le mode d'achat : prestataire autonome et mise en service unique. Il ne change pas rétrospectivement la plage de JH de ce document.

