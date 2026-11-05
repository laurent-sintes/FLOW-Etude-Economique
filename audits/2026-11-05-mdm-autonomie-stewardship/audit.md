# Master Data FLOW — autonomie des administrateurs et data stewards

**Proposition par livrable.** L’autonomie sur le redressement des données, les règles de qualité et l’enrichissement entre dans le scénario de base. Le périmètre couvre la construction générique Java/Spring. Le chiffrage retenu reste à **2 670 JH et 1 736 160 € HT**.

## Périmètre de l’autonomie

- **Administrateur MDM.** Définir le cadre d’action, les portées par famille, les opérateurs disponibles, les droits et la validation exigée. Configurer et activer les règles selon les délégations.
- **Data steward.** Corriger une fiche ou un lot, qualifier et affecter les anomalies, demander une correction à la source quand elle détient l’autorité, puis déclencher le recontrôle. Configurer et prévisualiser les règles de qualité et d’enrichissement dans son périmètre.
- **Équipe produit.** Maintenir les schémas structurels, les nouveaux opérateurs et les contrats d’échange. Le scénario central permet d’activer les règles métier depuis le portail, avec version, justification et circuit de validation selon l’impact.

Le redressement en masse couvre la sélection des lignes et champs autorisés, l’aperçu avant/après, le suivi des rejets et la relance sans double application. Les règles de qualité portent sur une population, des critères, une sévérité et des seuils. Les règles d’enrichissement s’appuient sur un catalogue borné d’opérateurs et conservent la provenance de chaque valeur. Une règle peut être prévisualisée sans modifier les données. Les corrections préservent les versions certifiées antérieures.

## Charges supplémentaires

| Composant | Proposition précédente | Autonomie | Nouvelle proposition |
|---|---:|---:|---:|
| Registre de modèles et d’autorités | 155 | +55 | 210 |
| Écriture des fiches sources et consolidées | 180 | +35 | 215 |
| Consolidation, survivance et enrichissement | 195 | +45 | 240 |
| Qualité et correction à la source | 180 | +55 | 235 |
| Administration des modèles, sources et règles | 105 | +90 | 195 |
| Écrans de rapprochement et historique | 125 | +25 | 150 |
| Écrans d’anomalies, certification et publication | 135 | +35 | 170 |
| Écran d’import et d’export en masse | 80 | +40 | 120 |

Le moteur passe de **1 810 à 2 000 JH** et les écrans de **595 à 785 JH**. Avec **730 JH** d’adaptation aux huit familles et **200 JH** de qualification transverse, la proposition passe de **3 335 à 3 715 JH**, soit **1 045 JH** au-dessus du chiffrage retenu.

Le studio de modification des schémas, le mappage libre des imports et la recherche avancée sur les relations restent des extensions distinctes. Avec les trois, la proposition est de **4 165 JH**. L’aperçu des corrections en masse appartient au scénario de base. Le mappage libre porte sur la configuration des entrées, au-delà des gabarits et des sélections déjà prévus.

Les nouvelles charges sont des hypothèses d’ingénierie. Les volumes, le catalogue de règles et les délégations restent à préciser. Le calcul utilise les mécanismes existants de formulaires, tâches, habilitations, journal et traitements de fond. Le coût du socle générique conserve son propriétaire. Les adaptations et les contrôles métier sont chiffrés dans les travaux MDM.

[Hypothèses et charges par activité](engineering.json) · [Proposition précédente](../2026-11-05-mdm-construction-cible/audit.md)
