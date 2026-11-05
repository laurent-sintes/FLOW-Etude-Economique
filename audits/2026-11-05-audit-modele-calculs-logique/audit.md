# Audit du modèle métier, des calculs et de la logique

Actualisé le 5 novembre 2026 sur la révision 28 du modèle.

Le chiffrage de construction du MDM est **délimité et adopté**. Le dossier Team Topologies présente désormais les équipes durables de delivery, leurs périmètres et leurs interactions dans un graphe consultable. La ventilation des **4 130 JH de Build communs est adoptée**. La priorité suivante est d’affecter le MCO aux équipes et de dimensionner la capacité nécessaire pour tenir leurs responsabilités dans le temps.

L’estimation de l’intégration est mise de côté dans les priorités de cette revue. Ses jours restent au statut « Non évalué » dans la ventilation et ses totaux.

## Constats traités

| Sujet | État sur la révision 27 |
| --- | --- |
| Construction du MDM | Le scénario Java/Spring adopté couvre l’autonomie des administrateurs et des data stewards, le studio de schéma et les plugins JAR. Le lot Master Data est retenu à **4 145 JH et 2 695 410 € HT**. Le mappage libre des imports et la recherche avancée restent des options distinctes. [Décision et valorisation](../2026-11-05-adoption-core-923b1e9a7b857870/audit.md) |
| Frontière Master Data et SCM | Les **400 JH** d’Operational References constituent un lot séparé dans le domaine SCM. L’équipe Master Data porte le producteur et ce composant de lecture opérationnelle. Les consommateurs conservent leurs décisions et leurs usages. [Affectations et frontières](../../source/organisation-delivery.yaml) |
| Organisation et présentation Team Topologies | La cible distingue six équipes Stream-aligned, deux Platform, deux Complicated-subsystem et une Enabling. L’équipe Intégration est durable et ses accompagnements sont temporaires. Le Transformation Office est présenté comme instance de gouvernance. Les fiches par type et le graphe React Flow donnent accès aux contrats proposés. Les interactions utilisent la notation du livre. [Audit Team Topologies](../2026-11-05-audit-team-topologies.md) · [Notation des interactions](../2026-11-05-notation-livre-interactions.md) |
| Ventilation dans le modèle | La table calculée `team_phase_allocation` est affichée dans « Comprendre les coûts » et figure dans l’export du modèle métier. Le catalogue relie les unités de travail à leurs contributions. L’abaque accepte des clés documentées par unité ou rôle et conserve les reliquats. Les responsabilités sources connues sont déjà reprises. [Unités de travail](../../source/unites-travail.yaml) · [Abaque](../../source/abaque-ventilation.yaml) |
| Contrôles du modèle | Les corrections de la révision 13 autorisent les contributions Enabling compatibles avec leur mission, refusent une période de financement qui franchit la limite Build / intégration sans découpage explicite, et détectent les affectations contradictoires ou les doublons de partition. [Preuves de la révision 13](verification.json) |

## Ventilation adoptée des lots Make communs

La décision du 5 novembre 2026 attribue les **4 130 JH** des cinq lots partagés. Les clés reprennent le ratio entre les JH validés de chaque équipe et le total du lot, appliqué aux rôles retenus. Les deux lots COSMIC utilisent les groupes de processus adoptés. Les trois autres utilisent les livrables chiffrés. [Abaque adopté](../../source/abaque-ventilation.yaml) · [Comptages COSMIC](../2026-11-02-adoption-perimetre-scenarios/scope.json) · [Livrables chiffrés](../2026-11-02-adoption-quatre-lots/scope.json)

| Lot | Affectation retenue | JH |
| --- | --- | ---: |
| Commandes | Sourcing & Procurement 266, B2C 74, Wholesale 80 | 420 |
| Décisions Supply | Master Plan et Supply Policy 334, Inventory et Availability 122, Services 254 | 710 |
| Process Management | Case Management 1 890, Portal 170 | 2 060 |
| Ateliers Supply | Master Plan et Supply Policy 190, Portal 130, Services 80 | 400 |
| IT transverse | PaaS 290, Portal 250 | 540 |
| **Total** | | **4 130** |

Les coûts de rôle suivent les mêmes clés, aux tarifs retenus. Les **33 040 € HT** d’outillage de ces lots restent à ventiler. Leur attribution relève d’une clé de frais distincte.

## Charges et financements vérifiés

La construction générique Java/Spring représente **10 575 JH et 6 860 000 € HT**. La lecture par phase ajoute au Build les travaux de gouvernance et les moyens financés pendant la période. Le MCO est une base annuelle complète. Les montants ci-dessous utilisent la référence tarifaire Paris, avant projection sur un horizon.

| Destination | Build · JH | Build · € HT | MCO et évolutions · JH/an | MCO et évolutions · € HT/an |
| --- | ---: | ---: | ---: | ---: |
| Équipes, affectations justifiées | 10 575 | 6 928 960 | — | 96 000 |
| Gouvernance financée | 4 320 | 3 931 200 | — | — |
| Travaux et moyens à ventiler | — | **33 040** | **1 421,9** | **881 562,88** |
| Total connu | 14 895 | 10 893 200 | 1 421,9 | 977 562,88 |

Le tiret signale une valeur absente. Les 96 000 € annuels affectés à PaaS correspondent à des moyens techniques. Les charges humaines du MCO figurent intégralement dans le reliquat. Les JH annuels sont arrondis pour la lecture. [Sources d’affectation](../../source/organisation-delivery.yaml) · [Décisions retenues](../../source/estimations-core-retenues.yaml)

## Priorités restantes

1. **Répartir le MCO et les évolutions.** Distinguer les travaux annuels du produit générique, les adaptations Beaumanoir et les moyens transverses. Rattacher les activités aux propriétaires durables, dont les responsabilités annuelles sur le MDM et les vues consommatrices. [Activités de maintenance](../../source/maintenance.yaml) · [Périmètres des équipes](../../source/organisation-delivery.yaml)
2. **Éprouver les contrats Team Topologies.** Les 29 interactions sont documentées au statut proposé. Confirmer les consommateurs, les conditions de service des plateformes et les fenêtres d’accompagnement Enabling. Vérifier si l’expertise et la charge cognitive justifient deux équipes Complicated-subsystem distinctes. [Points de fond de l’audit Team Topologies](../2026-11-05-audit-team-topologies.md)
3. **Rapprocher la gouvernance et les fonctions financées.** Définir qui porte la direction de projet, le PMO, la synchronisation, la conduite du changement et l’architecture transverse dans la cible. Relier ces missions aux décisions du board et aux responsabilités des équipes. [Gouvernance et rôles](../../source/organisation-delivery.yaml) · [Financement des rôles](../../source/modele-composable.yaml)
4. **Dimensionner la capacité des équipes durables.** À partir des travaux affectés, établir les besoins et disponibilités par rôle et période, les renforts et la trajectoire de transfert. Distinguer charge estimée, capacité réservée et coût financé. La capacité des équipes reste à renseigner dans le modèle. [Capacités déclarées](../../source/organisation-delivery.yaml)

## Vérifications et traçabilité

L’instantané de la révision 28 a réussi **560 contrôles indépendants** avec `tools.audit_delivery_model`. Ils couvrent les JH par rôle, la valorisation des lots, l’unicité des financements, les annuités et cumuls, ainsi que la conservation des charges, coûts et tarifs lors de la ventilation. Le contrôle réconcilie chaque cellule avec ses contributions et ses mesures sources. Les hypothèses de périmètre, de productivité et de capacité relèvent d’une validation métier distincte. [Commande et contrôles](../../tools/audit_delivery_model.py)

La vérification de livraison a comparé les clés et les valeurs de ventilation entre l’instantané, l’export YAML et les données de l’application. La référence financière se réconcilie à l’identique avec la révision 27. Les **95 tests ciblés** passent après la reprise du scénario de test de consolidation. Les tableaux de charges et de coûts ont été vérifiés dans le navigateur local. Les rapports des deux passes sont conservés dans `tmp/validation/20261105T214208Z-778ad1a4` et `tmp/validation/20261105T214538Z-cb7ab172`.

Le métamodèle canonique alimente « Modèle et relations » dans le Framework. Les objets et leurs relations, les règles et leurs implémentations, et les interactions d’équipes se lisent dans des vues distinctes. [Métamodèle](../../source/fondamentaux.yaml) · [Source des interactions](../../source/organisation-delivery.yaml)

Les fichiers [avant.json](avant.json), [apres.json](apres.json) et [verification.json](verification.json) retracent la révision 13 et ses vérifications navigateur. Les chiffres Master Data actifs proviennent de la décision d’adoption. Les rapports d’ingénierie antérieurs retracent les propositions qui l’ont précédée.
