# Master Data FLOW — studio de schéma et plugins JAR

**Proposition d’ingénierie.** Le studio de schéma et le chargement de plugins Java JAR font partie du scénario de base, avec l’autonomie sur le redressement, la qualité et l’enrichissement. Les 2 670 JH et 1 736 160 € HT retenus restent la référence active.

## Travail à réaliser

- **Studio de schéma.** Les administrateurs créent et modifient les familles, champs et relations en brouillon, prévisualisent les impacts et activent les changements compatibles. L’équipe produit traite les migrations incompatibles. Le studio consomme le registre MDM déjà chiffré.
- **Plugins JAR.** Les administrateurs déposent et activent les plugins autorisés. Le scénario chiffre un contrat Java versionné, le contrôle de la signature et de la compatibilité, le registre des versions, l’exécution isolée et le suivi des règles utilisatrices. Les data stewards sélectionnent les opérateurs activés dans les règles de qualité et d’enrichissement de leur périmètre. Les parcours de redressement, l’aperçu et le recontrôle restent dans le calcul. [Vérification de signature dans le JDK](https://docs.oracle.com/en/java/javase/21/docs/specs/man/jarsigner.html)

Le choix d’un processus isolé avec droits et ressources limités est une hypothèse de chiffrage. Les changements activables sans migration, les signataires et les dépendances autorisés restent à préciser.

## Recalcul

| Composant ajouté au scénario de base | Moteur | Écrans | Total JH |
|---|---:|---:|---:|
| Studio de schéma, repris de l’option précédente | 125 | 95 | 220 |
| Chargement et administration des plugins JAR | 150 | 60 | 210 |
| **Supplément** | **275** | **155** | **430** |

| Bloc | JH |
|---|---:|
| Moteur de données | 2 275 |
| Écrans d’administration et de gestion | 940 |
| Adaptation des huit familles | 730 |
| Qualification transverse | 200 |
| **Proposition de base** | **4 145** |

La proposition passe de **3 715 à 4 145 JH**, soit **1 475 JH** de plus que la référence. Le mappage libre des imports et la recherche avancée sur les relations restent des options distinctes à **230 JH** au total. Avec les deux, la proposition atteint **4 375 JH**.

Le repère COCOMO de **5 410 JH** conserve sa sélection actuelle. Son inventaire compte l’éditeur de modèles et des services contenant le chargement de fonctions Java, dont `CleanseFunctionServiceImpl` et `MetaIEServiceImpl`. L’API dédiée `CleanseFunctionRestService` et la fenêtre de dépôt JAR ne figurent pas dans cet inventaire. Les **210 JH** dimensionnent le parcours FLOW complet à partir des travaux décrits ci-dessus. [Mesures Unidata](../2026-11-05-estimation-mdm-oss/measurements.json)

[Composants et charges par activité](engineering.json) · [Scénario précédent](../2026-11-05-mdm-autonomie-stewardship/audit.md)
