# Affinage de la référence Unidata pour le MDM de FLOW

**Proposition COCOMO du 5 novembre 2026.** Le calcul porte sur la construction générique Java/Spring du domaine Master Data. Il utilise le code public Unidata CE figé au commit `6fbf732942ace0dfc49eaf58a5f17d10e43c77f0`. Les 33 capacités de la cartographie restent couvertes par le rapprochement. La décision active reste à **2 670 JH et 1 736 160 € HT**. Les vues Operational References relèvent de la SCM.

## Retraits du code mesuré

| Retrait | Unités logiques | Motif et frontière |
|---|---:|---|
| Ancien assistant d’import direct du métamodèle XML d’Unidata et traitement REST dédié | 67 | Le wizard `IMPORT_OLD` envoie le fichier XML à `internal/meta/model`. Le besoin FLOW porte sur ses modèles et sur les apports de données des SI. Aucun déploiement d’Unidata ni reprise de son format n’est prévu dans ce scénario. L’éditeur, l’import/export moderne du modèle et les contrats d’ingestion de données restent comptés. |
| Affectation et désaffectation génériques de tâches, génération PNG du diagramme d’instance, déploiement et export BPMN | 68 | Le lot Process Management finance le moteur, les définitions et le portail de tâches. Les méthodes retirées délèguent l’affectation et le rendu à Activiti ou installent/copient ses fichiers de processus. Les liens entre fiches, décisions MDM, certificats et tâches restent dans le calcul. |

Le fichier [selection.json](selection.json) identifie chaque fichier et chaque méthode avec l’empreinte des octets et les lignes d’origine. L’ancien assistant représente 34 unités côté écran. L’API XML en représente 33 et les méthodes liées au workflow en représentent 68 côté serveur. Seules les méthodes indiquées sont retranchées dans les fichiers mixtes. Les appels et déclarations partagés sont conservés.

## Données et écrans vérifiés

| Parcours | Éléments examinés | Rattachement à FLOW |
|---|---|---|
| Administration du modèle, des règles et des sources | Éditeur d’entités et de schémas, définitions des attributs et des relations, versions et brouillons, systèmes sources | BC-089–090, BC-093, BC-098 et BC-118 |
| Consultation, recherche, saisie et historique des fiches | Écrans steward `dataentity`, attributs simples et complexes, relations et classifications. Services d’origines, de fiches consolidées, de relations et d’historique | BC-094–098 et familles BC-103–121 |
| Qualité et correction | Configuration du rapprochement, groupes de doublons, écran de fusion et services d’identité. Complément FLOW pour le suivi de la correction à la source | BC-091–092, BC-095–097 |
| Certification, accès et diffusion | Changements et dates d’effet, publication et retrait, suivi de livraison. Les compléments FLOW couvrent notamment la certification et la reprise | BC-098–102 |

Les fichiers examinés constituent une analogie de taille. Certains services nécessaires à un parcours peuvent se trouver en dehors de la sélection initiale. L’ampleur des adaptations par écran, l’usage des assistants XLSX et le degré d’autonomie du studio de modèle restent à instruire. Ils n’entraînent aucune déduction à ce stade.

## Recalcul

| Assiette ou résultat | Mesure initiale | Périmètre affiné |
|---|---:|---:|
| Unités logiques mesurées | 47 217 | 47 082 |
| Compléments FLOW | 948 | 948 |
| Adaptateurs des huit familles | 680 | 680 |
| Taille équivalente en milliers d’unités | 48,845 | 48,710 |
| Charge avant arrondi, en JH | 5 422,1 | 5 405,7 |
| Charge arrondie à 10 JH | 5 420 | **5 410** |

L’écart avant arrondi est d’environ 16,5 JH. La taille équivalente baisse de 0,28 %. Le même calcul COCOMO II, les mêmes paramètres, les mêmes compléments et les mêmes tarifs sont utilisés. Les mesures AtroCore et Pimcore restent celles de la comparaison initiale. Le rapprochement COSMIC reste à instruire sur le MDM élargi.

## Reproduction

Le moteur vérifie l’empreinte de la sélection, son rattachement à la mesure initiale, l’appartenance des extraits au code archivé et l’absence de chevauchement. Il rejoue le calcul avec les mêmes fonctions COCOMO pour la base initiale et l’assiette affinée. Le test `test_replay_from_frozen_documents_has_no_source_checkout_dependency` vérifie le rejeu sans accès au dépôt Unidata.

Pour revérifier les comptages, utiliser le [mesureur d’origine](../2026-11-05-estimation-mdm-oss/measure.py) et ses dépendances. Décoder l’archive `code.json` comme dans `verify_archive`. Pour chaque extrait Java, parser le fichier entier avec le parseur d’origine, sélectionner le nœud `method_declaration` dont les bornes correspondent à `start_byte` et `end_byte`, puis appeler `measure(node.text, ".java")`. Pour le fichier JavaScript, utiliser le comptage de la mesure initiale.

### Sources de décision

- [Cartographie et livrables Master Data](../../source/revision-master-data.yaml)
- [Process Management adopté et propriétaires des financements](../../source/estimations-core-retenues.yaml)
- [Audit COCOMO initial, paramètres et provenances](../2026-11-05-estimation-mdm-oss/audit.md)
- [Révision du code Unidata](https://gitlab.com/unidata-community-group/unidata-platform-5/-/tree/6fbf732942ace0dfc49eaf58a5f17d10e43c77f0)
