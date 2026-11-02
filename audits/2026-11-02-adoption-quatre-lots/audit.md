# Adoption des quatre lots détaillés

**Décision utilisateur du 2 novembre 2026 : « Je valide ».**

Estimation retenue : **7 630 JH et 4 807 640 € HT de construction**, soit **+600 JH et +378 450 € HT**. Les quatre lots remplacent leurs anciens montants. Les sept autres lots et les 88 capacités sont conservés.

| Lot | JH retenus | Coût k€ HT |
|---|---:|---:|
| Master Data Java/Spring | 1600 | 1007 |
| Process Management avec studios, portail, formulaires et pilotage | 2060 | 1297 |
| Ateliers visuels de planification et de décision | 400 | 251 |
| Administration, robustesse et services IT complémentaires | 540 | 344 |

L’édition corrective Master Data est comprise : 210 JH dans le lot de 1 600 JH, avec motif, autorité, validation, provenance, version et conflit avec une nouvelle contribution. Les 34 livrables sont dans [scope.json](scope.json).

La méthode retenue pour ces quatre lots est la somme de livrables détaillés validés. Les JH sont des hypothèses d’ingénierie, pas des temps observés ni une nouvelle mesure du code. Les comparaisons COCOMO et COSMIC historiques restent disponibles. Deux autres lots restent COCOMO II et cinq lots COSMIC × ISBSG.

Les activités projet sont incluses. Chaque mécanisme partagé garde son propriétaire. La ventilation des rôles conserve les proportions précédentes pour valoriser les efforts, sans constituer un plan de recrutement. Master Data attribue 160 JH à son noyau générique de protection, audit et restauration, les autres livrables à son domaine produit.

Le calendrier global, l’intégration, les bases annuelles et le Transformation Office restent inchangés dans cette adoption. Les délais locaux sont des projections indicatives, sans somme. L’effet d’un futur changement de délai sur les coûts transverses devra être recalculé.

| Option | Total à dix ans k€ HT |
|---|---:|
| java-spring | 18338 |
| microsoft | 25195 |
| sap | 40609 |

Les cinq options sont réconciliées aux horizons 3, 5, 7 et 10 ans. Microsoft, SAP, .NET et Rust restent inchangés. La hausse Make suit la dépense de construction. Les paramètres des simulations personnelles restent conservés.

Preuves : [décision](decision.json), [contrats antérieurs](basis.json), [économie avant](before-financial.json), [économie après](after-financial.json), [réconciliation](verification.json). Le recalcul utilise les règles du métamodèle et le même moteur Python dans l’application.
