# Application des préconisations de l’audit

Les deux simplifications encore proposées dans [l’audit](audit.md) sont implémentées. Aucun montant, tarif, calendrier ou périmètre métier n’est modifié par cette intervention.

## Une commande pour intégrer une décision

`python -m tools.adopt_core run --proposal tmp/proposition-core.json --decision-note "Validation métier" --refresh`

La commande prépare les décisions, contrats, rôles, finalités Core Domain / Support, preuves, références de lecture et version dans une copie isolée. Elle charge le vrai moteur, contrôle les cinq options et vingt horizons, puis applique les fichiers validés. Les paramètres autres que le coût de construction Java/Spring et les tarifs doivent rester identiques. Une proposition sans changement ne réécrit pas les sources et n’incrémente pas la version.

Les lots détaillés utilisent leur recette existante. Les révisions successives retrouvent le contrat initial de comparaison sans cumuler les charges anciennes. Les paquets déclaratifs `prepared_contracts` permettent de réutiliser les autres recettes COCOMO ou COSMIC déjà implémentées. Aucun ajout de code Python n’est nécessaire pour une simple évolution de leurs données préparées.

Le plan conserve les octets avant/après et les empreintes des entrants. Un verrou évite deux adoptions simultanées. Un entrant modifié invalide le plan. Les fichiers sont remplacés individuellement de manière atomique, avec journal et restauration en cas d’échec. L’ensemble de plusieurs fichiers n’est pas une opération atomique du système de fichiers. Un marqueur bloque donc tout nouveau chargement du modèle pendant l’application ou après une interruption. `python -m tools.adopt_core recover` restaure l’état précédent, sans écraser une modification étrangère. Les simulations déjà chargées restent utilisables.

La livraison est reconstruite une seule fois après une adoption réussie avec `--refresh`. Son éventuel échec reste distinct de l’adoption déjà appliquée. Aucun commit ni push implicite. Les commandes et le format des paquets sont décrits dans [tools/README.md](../../tools/README.md#adopter-une-estimation-core).

## Références de tests regroupées

Treize modules de tests lisent désormais les valeurs courantes par `test_support.active_reference()`. Un pointeur unique lie la référence figée à la décision adoptée par empreinte. La commande met à jour ce pointeur et sa référence dans la même transaction. Les valeurs attendues ne sont pas recalculées à chaque test. Les décisions historiques et exemples arithmétiques indépendants restent séparés.

Les montants, charges par unité, rôles, finalités, méthodes et livrables courants sont regroupés. Les contrôles propres à un périmètre métier peuvent encore évoluer lorsqu’une nouvelle fonction est adoptée.

## Mesures et vérifications

- 126 tests ciblés réussis en 468,244 secondes, dont le parcours complet de préparation et d’application dans une copie isolée. Ce passage teste la nouvelle automatisation et ses consommateurs. Son périmètre diffère de la campagne historique de 424 tests. Il ne constitue donc pas une mesure comparative de vitesse.
- Préparation isolée mesurée à 70,08 secondes : chargement 27,84 s, projection 1,97 s, copie 2,55 s, validation 36,61 s. Cette mesure exclut la reconstruction de l’application. Le poste exécutait aussi les autres contrôles de la tâche. Ce n’est pas une durée garantie.
- Le test augmente temporairement un livrable de 10 JH dans sa copie, valide le candidat et applique le plan dans cette seule copie. Les sources réelles restent identiques. Les tests couvrent également les plans obsolètes ou altérés, l’échec au milieu des écritures, l’interruption, les modifications étrangères, le verrou et le refus d’un paquet qui modifie le code.
- Comparaison indépendante avec `profile-before.json` : tous les paramètres et résultats financiers sont identiques sur les cinq options, vingt horizons et annuités. Seule l’empreinte technique du moteur évolue. Référence conservée : **7 630 JH, 4 807 640 € HT**, modèle **02/11/2026 n° 5**.
- Les rapports détaillés et temps par test figurent dans [application.json](application.json). Les erreurs du premier essai de staging, corrigées ensuite, restent dans les rapports sous `tmp/validation/`.

Les optimisations déjà appliquées pendant l’audit restent en place : lecteur JSON strict, projection légère de la cartographie, sélection explicite et dédupliquée des tests, cache de livraison insensible aux fichiers de travail non publiés. Le gain de chargement mesuré pendant cet audit reste de 23,4 %. Aucun nouveau benchmark comparable n’a été réalisé ici.

Le dernier contrôle de comptage des livrables, désormais lu dans la même référence figée, a été rejoué seul après son ajustement : un test réussi en 31,298 secondes. Les 125 autres tests inchangés n’ont pas été répétés.

Livraison locale reconstruite une seule fois après les contrôles, en 113.44 secondes pour le lanceur complet. Cette mesure isolée n’est pas comparable au benchmark de chargement. Le manifeste servi correspond à cette livraison. Après rechargement du navigateur, la page des charges affiche 7 630 JH et le modèle du 02/11/2026 n° 5.
