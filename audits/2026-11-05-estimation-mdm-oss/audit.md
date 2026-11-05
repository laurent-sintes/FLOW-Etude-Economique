# Estimation COCOMO du domaine Master Data — 5 novembre 2026

**Proposition non adoptée.** L’estimation est conditionnelle à la transposition des composants sélectionnés vers Java/Spring et aux compléments décrits ci-dessous. Les 2 670 JH et 1 736 k€ HT retenus pour Master Data restent la référence de l’application. Les 400 JH d’Operational References appartiennent à la SCM et sont exclus de cette estimation.

| Référence de code | Taille équivalente, milliers d’unités | Charge, JH | Coût indicatif, k€ HT | Délai local, mois |
| --- | ---: | ---: | ---: | ---: | ---: |
| AtroCore | 17,078 | 1 710 | 1 112 | 17,4 |
| Unidata CE · code Java | 48,845 | 5 420 | 3 524 | 25,2 |
| Pimcore 11 · composition GPL | 35,226 | 3 780 | 2 458 | 22,5 |

Le repère Java Unidata est de **5 420 JH**, soit **2 750 JH de plus** que la charge retenue. Le choix de cette référence a été fixé avant le calcul, sur la proximité du langage et les services métier présents. Il s’agit de code historique et non d’une recommandation de déploiement. Les résultats ne sont ni moyennés, ni interprétés comme un intervalle de confiance.

## Frontière et qualification

La cartographie native fournit les 33 capacités MDM. Les 14 capacités transverses sont rapprochées de cinq ensembles de composants. Les 19 capacités de familles sont représentées par huit adaptations à des modèles génériques. Le fichier scope.json conserve chaque identifiant, le rattachement et les compléments associés. Cette correspondance ne démontre pas une couverture complète des fonctionnalités, ni la compatibilité des trois produits avec FLOW.

Les sources retenues incluent la modélisation, les contributions, la qualité, le rapprochement, la gestion des données et des versions et l’accès aux consommateurs. Les workflows génériques, l’authentification, l’ORM, la base de données, les bibliothèques et la plateforme technique ne sont pas reconstruits. Les routines et adaptateurs métier d’un produit peuvent toutefois dépendre de ces composants. Les CMS, DAM, données d’exemple, tests, code généré et migrations historiques sont exclus. Le corpus Unidata conserve des requêtes et huit extraits de routines de données résolus statiquement. La mesure ne constitue pas une reconstitution ou une exécution de sa base.

### Versions mesurées

**AtroCore** — Noyau public actuel. Identités, consolidation, lignage et pipelines mesurés. Les modules Premium et les connecteurs dédiés sont hors mesure.

- [atrocore · c174be2ac0c0](https://github.com/atrocore/atrocore/tree/c174be2ac0c0d281f96a03c6c2d3823f4f0901e2) — 2026-11-05.

**Unidata CE · code Java** — Code public de 2020. Services, écrans de gestion des données, schémas et routines de persistance sélectionnés. Les dépendances anciennes et la maintenabilité actuelle ne sont pas validées.

- [unidata · 6fbf732942ac](https://gitlab.com/unidata-community-group/unidata-platform-5/-/tree/6fbf732942ace0dfc49eaf58a5f17d10e43c77f0) — 2020-09-10.

**Pimcore 11 · composition GPL** — Noyau 11.5 et modules GPL. Le rapprochement observé dans CMF cible les clients. GraphQL est un analogue d’accès, sans garantie de livraison. Aucun assemblage en production n’a été validé.

- [pimcore · 2ee6fb538712](https://github.com/pimcore/pimcore/tree/2ee6fb538712ebca80b783f8c10c9641d6425172) — 2026-01-16.
- [pimcore-admin · ab027f03d254](https://github.com/pimcore/admin-ui-classic-bundle/tree/ab027f03d254c574dbcc73cca30540a71622ee33) — 2024-07-02.
- [pimcore-cmf · 441639320548](https://github.com/pimcore/customer-data-framework/tree/441639320548e4febd9eb947a3d42ecf1722b947) — 2024-09-23.
- [pimcore-importer · e82ac153724f](https://github.com/pimcore/data-importer/tree/e82ac153724f45a98d25a1991cb9f092b0dbb06a) — 2024-09-02.
- [pimcore-datahub · 7bd6287ba6de](https://github.com/pimcore/data-hub/tree/7bd6287ba6de475b525e5bebef0a3b97be45c24a) — 2024-12-02.

Les licences des sources sélectionnées sont conservées dans code.json. Pimcore est mesuré sur les versions GPLv3 épinglées, avec Admin UI Classic, CMF, Data Importer et Data Hub. Cela ne vaut pas qualification des éditions courantes sous POCL. Les déclarations de dépendances sont archivées. Aucun assemblage ni test de production du logiciel tiers n’a été exécuté.

## Taille et compléments

| Ensemble mesuré | AtroCore | Unidata CE | Pimcore GPL |
| --- | ---: | ---: | ---: |
| Modèle et autorités | 5 619 | 15 336 | 22 864 |
| Contributions et qualité | 832 | 1 306 | 3 766 |
| Identités et consolidation | 5 805 | 3 234 | 827 |
| Versions et certification | 1 391 | 26 732 | 2 282 |
| Accès et distribution | 1 803 | 609 | 3 785 |
| Total mesuré | 15 450 | 47 217 | 33 524 |
| Compléments FLOW | 948 | 948 | 1 022 |
| Adaptations de familles | 680 | 680 | 680 |

Les différences principales viennent de la chaîne de gestion des données d’Unidata et de la modélisation et des écrans de Pimcore. Les groupes comptent des fichiers entiers dont les frontières techniques diffèrent. Les fonctions partagées entre groupes sont comptées une fois. Une taille plus élevée peut aussi traduire des choix d’architecture, des fonctions natives excédentaires ou une granularité de code différente.

Les mesures de taille utilisent les arbres syntaxiques PHP, Java et JavaScript. Les déclarations JSON sont comptées par feuilles, les XSD par éléments de structure et les requêtes XML par entrée. Les extraits SQL retenus sont comptés par instructions terminées, avec une convention explicite. Une déclaration vaut une unité dans le scénario central. Cette taille logique reproductible est une approximation de taille COCOMO, sans conversion de productivité calibrée entre langages.

Les compléments suivants dimensionnent du code nouveau au moyen d’analogues. La taille par service est la médiane des trois mesures indiquées dans scope.json. Les prototypes ne sont pas recomptés dans le total de base.

- **Certification, remplacement et retrait cohérents** : 297 unités pour 1 service(s). Un service de manifeste et de transitions pour autoriser, remplacer et retirer une version cohérente. Les versions unitaires observées ne démontrent pas ce contrat entre familles.
- **Remédiation clôturée après recontrôle** : 67 unités pour 1 service(s). Un adaptateur vers le processus de correction et un recontrôle. Le moteur générique de workflow déjà financé est réutilisé, sans le reconstruire.
- **Abonnements et livraisons rejouables** : 180 unités pour 2 service(s). Deux services supposés : registre des consommateurs et suivi des livraisons avec accusés, rejets et reprise. Webhooks ou API ne prouvent pas à eux seuls ce protocole.
- **Rapprochement après restauration et protection** : 404 unités pour 1 service(s). Un service de rapprochement des versions et consommations après restauration. Le stockage et la sauvegarde techniques sont fournis par le socle existant. Les performances de reprise restent à qualifier.
- **Pimcore** : 74 unités supplémentaires pour la généralisation du rapprochement au-delà des clients.

Les huit adaptateurs de familles supposent chacun 85 unités déclaratives, médiane des trois définitions de modèle mesurées : 63, 85 et 1 106. Le nombre de champs et de règles propres à FLOW reste à établir. Les différences entre les prototypes montrent la limite de cette hypothèse.

## Calcul et sensibilité

Un calcul COCOMO II est appliqué à l’union de la base mesurée et des compléments, par référence. La formule réutilise les paramètres nominaux du modèle : A = 2,94, E = 1,0997, 152 heures par mois-personne, 7 heures par JH et facteur d’activités 1,18. EM et SCED restent nominaux. Pour Unidata : 47 217 unités mesurées + 948 unités de compléments + 680 unités de familles = 48 845 unités équivalentes. Le calcul donne environ 5 422 JH avant arrondi à la dizaine.

Le délai est un délai indicatif du lot, calculé par la formule COCOMO du modèle. La valorisation applique les proportions de rôles et les tarifs actuels de Master Data, avec le même outillage par JH. Ni ces proportions, ni le calendrier, ni le coût ne sont des observations de projet.

| Poids du déclaratif | AtroCore, JH | Unidata, JH | Pimcore, JH |
| --- | ---: | ---: | ---: |
| 0,5 | 1 480 | 5 340 | 3 740 |
| 2,0 | 2 170 | 5 590 | 3 870 |

Cette sensibilité ne fait varier qu’un paramètre. Elle ne couvre pas les écarts de services, de maturité, de taille des familles ou de productivité. Un écart de taille entre PHP, Java et leurs déclarations ne constitue pas une mesure du rendement des équipes.

## Données encore attendues

- Inventaire détaillé des objets, champs et règles par famille
- Volumes, objectifs de latence, rapprochement et conditions de performance
- Modes d’autorité et responsabilités par famille
- Nombre et contraintes des consommateurs et abonnements
- Mesures de productivité propres à Java/Spring et aux équipes
- Comptage COSMIC comparable du nouveau périmètre

Les connecteurs spécifiques, la migration, le nettoyage Beaumanoir et le fonctionnement sont hors périmètre. Aucune nouvelle mesure COSMIC comparable ni calibration indépendante ne sont ajoutées. L’écart des trois références justifie une qualification des composants les plus lourds et des règles de familles avant toute adoption.

## Reproduction

- `measurements.json` : mesures par fichier ou extrait, composants et révisions.
- `code.json` : archive gzip/base64 des sources sélectionnées et de leurs licences.
- `scope.json` : périmètre, analogues et quantités supposées, fixés avant calcul.
- `measure.py --verify-archive` : remesure des 1 659 entrées avec les versions de parseurs indiquées dans `requirements-measure.txt`, sans accès réseau.
- `tools/mdm_oss_estimation.py` : contrôle des empreintes et calcul avec les règles canoniques.
- `before-financial.json` : témoin des budgets, paramètres et projections avant la proposition.
