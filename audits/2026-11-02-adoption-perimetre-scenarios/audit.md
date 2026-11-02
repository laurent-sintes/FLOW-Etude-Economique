# Adoption des charges après revue des scénarios

**7 030 JH et 4 429 190 euros HT de construction du Core System sont adoptés le 2 novembre 2026.** La décision utilisateur est : « Je valide les 7 030 JH ». Les simulations utilisent ces montants. Le complément par rapport à la référence précédente est de 1 080 JH et 679 890 euros HT.

## Lots retenus

| Lot | JH | Euros HT | Méthode |
| --- | ---: | ---: | --- |
| Master Data Java/Spring | 1500 | 944000 | COCOMO II |
| Stock Java/Spring | 340 | 213970 | COCOMO II |
| Propriété du stock Java/Spring | 190 | 119970 | COCOMO II |
| Politiques, éligibilité et devenir des biens Java/Spring | 610 | 383630 | COSMIC × ISBSG |
| Gestion des commandes Java/Spring | 420 | 264760 | COSMIC × ISBSG |
| Préparation et pilotage du Master Plan Java/Spring | 330 | 208140 | COSMIC × ISBSG |
| Promesse, affectation et optimisation Supply Java/Spring | 710 | 447330 | COSMIC × ISBSG |
| Prestations et reconnaissance des résultats Java/Spring | 430 | 271040 | COSMIC × ISBSG |
| Process Management avec studios, portail, formulaires et pilotage | 1960 | 1233730 | COCOMO II |
| Ateliers visuels de planification et de décision | 160 | 100630 | COCOMO II |
| Administration, robustesse et services IT complémentaires | 380 | 241990 | COCOMO II |

Les cinq lots COSMIC remplacent leur périmètre précédent. Les 610 JH de politiques, éligibilité et devenir remplacent aussi la proposition intermédiaire de 430 JH. Six lots restent inchangés. Les répartitions de rôles sont calculées à partir des proportions antérieures, avec les mêmes tarifs et outillage.

## Preuves et méthode

Le registre actif référence `scenario_scope_adoption_v1`. Le moteur recompte les échanges E/R/W/X des 123 fonctions détaillées, vérifie les processus retirés et la décision adoptée, puis calcule CFP × 20 h/CFP ÷ 7 h/JH et l’arrondi par lot. Les rôles et montants sont réconciliés avec les décisions actives. Chaque mécanisme partagé conserve un seul financement.

Les comparaisons OSS sont rejouées depuis les anciens contrats figés. Elles gardent leur ancien périmètre et ne certifient pas la taille du nouveau périmètre COSMIC. Aucun volume de code ni COCOMO intégré n’est inventé pour le total mixte.

Les 88 capacités, leurs identifiants et la capture métier restent inchangés. La validation concerne les estimations et leurs hypothèses, pas une certification de couverture fonctionnelle ou de productivité. Les 20 h/CFP restent à calibrer sur une réalisation FLOW.

## Calendrier et budgets

Le calendrier global, les durées de l’Office FLOW, l’intégration et les bases annuelles restent inchangés. Les délais locaux COCOMO appliqués aux nouveaux efforts sont des projections indicatives, sans addition ni modification automatique du calendrier du programme. La suffisance du fonctionnement et du MCO pour le produit reste à vérifier dans leur propre étude.

Les cinq options sont réconciliées aux horizons 3, 5, 7 et 10 ans, avec conservation des simulations personnelles. Microsoft, SAP et les options historiques .NET et Rust ne changent pas.

| Option du parcours courant | Coût total à dix ans en euros HT | Variation |
| --- | ---: | ---: |
| java-spring | 17959094.15 | 679890.0 |
| microsoft | 25194599.8 | 0.0 |
| sap | 40609142.69 | 0.0 |

Les valeurs, règles et interfaces propres aux marques et aux SI Beaumanoir restent dans l’intégration. Les contrôles des livraisons devront vérifier contraintes, performances, concurrence et reprises, sans ajouter une seconde fois les fonctions génériques déjà financées.

## Fichiers de preuve

- [Décision et onze lots](decision.json).
- [Fonctions adoptées](scope.json).
- [Contrats et décisions antérieurs figés](basis.json).
- [Réconciliation des vingt horizons](verification.json).
- [Économie avant adoption](before-financial.json).
- [Économie après adoption](after-financial.json).
