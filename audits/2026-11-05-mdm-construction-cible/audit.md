# Master Data FLOW — construction du moteur et des écrans

**Proposition d’ingénierie du 5 novembre 2026.** Construction générique Java/Spring du MDM et de ses huit adaptations métier. Le périmètre est celui des 33 capacités Master Data. Les 2 670 JH et 1 736 160 € HT retenus restent la référence active. Operational References SCM, intégration Beaumanoir et exploitation sont hors de ce calcul.

## Scénario chiffré

Le scénario suppose des **schémas versionnés et livrés par l’équipe produit**. Les administrateurs gèrent les sources, règles et priorités dans le portail et prévisualisent les évolutions. Les fiches et relations sont accessibles dans un parcours commun aux familles. Le rapprochement et les contrôles utilisent un catalogue borné de règles. La saisie et les échanges tabulaires utilisent des gabarits validés. Les habilitations de lecture et d’écriture sont contrôlées côté serveur.

Le relevé Unidata reste le point de comparaison. Il mesure notamment **6 704 unités** dans les services de modèle, **6 191 unités** dans les écrans du groupe modèle, **4 986 unités** dans les listeners de données et **2 597 unités** dans les implémentations DAO sélectionnées du groupe cycle de vie. Ces ensembles montrent le poids d’un atelier de modélisation et d’un moteur générique. Les travaux FLOW sont estimés par livrable et par critère de réception. Aucune fraction forfaitaire du code Unidata n’est convertie en gain de réutilisation. [Inventaire initial](../2026-11-05-estimation-mdm-oss/measurements.json) · [Sélection Unidata affinée](../2026-11-05-affinage-unidata/audit.md)

## Travail propre au MDM

- **Construire** les règles d’autorité, la conservation des origines, le rapprochement, la fusion et la séparation, le choix des valeurs, la chronologie métier, la certification, le registre des livraisons et le contrôle de cohérence après restauration.
- **Adapter** la persistance et les index, les identités et droits techniques, le portail de tâches, les erreurs de validation, l’outillage d’import, la file de traitements et le transport. Les décisions métier, leur idempotence et leurs preuves restent dans le MDM.
- **Réutiliser** le backoffice, le rendu standard des formulaires, les tâches, l’outillage d’import, les traitements de fond, le stockage et les sauvegardes techniques. La charge couvre les raccordements et essais MDM. Les financements génériques restent chez leurs propriétaires. Le mécanisme Java/Spring d’intégration des frameworks a le lot Master Data pour propriétaire. Sa charge spécifique reste comprise.

Le modèle associe le portail et les tâches à Process Management. Il associe l’administration, les habilitations génériques, les traitements et l’outillage d’import à Support IT. Ce financement indique qui réalise le socle. La disponibilité et l’adéquation aux cas MDM restent à démontrer. Spring Data est un candidat pour les accès aux données. JSON Forms est un candidat pour rendre des schémas et brancher des contrôles spécifiques. [Mécanismes financés](../../source/calculs-estimation-core.yaml) · [Spring Data JPA](https://spring.io/projects/spring-data-jpa/) · [Contrôles personnalisés JSON Forms](https://jsonforms.io/docs/tutorial/custom-renderers/)

## Charges d’ingénierie

La conception comprend analyse, architecture, UX et coordination de lot. La réalisation comprend développement, adaptation, DevOps et tests développeur. La QA du composant couvre les essais ciblés. La qualification transverse existante couvre l’assemblage inter-familles, la résilience et les objectifs de service à préciser.

| Composant | Conception et coordination | Réalisation et adaptation | QA | Total JH |
|---|---:|---:|---:|---:|
| **Moteur de données** | | | | **1 810** |
| Registre de modèles et d’autorités | 35 | 85 | 35 | 155 |
| Écriture des fiches sources et consolidées | 30 | 105 | 45 | 180 |
| Versions, historique et décision de certification | 40 | 110 | 50 | 200 |
| Admission des contributions et reprise | 35 | 85 | 35 | 155 |
| Rapprochement, fusion et séparation | 45 | 120 | 55 | 220 |
| Consolidation, survivance et enrichissement | 40 | 110 | 45 | 195 |
| Qualité et correction à la source | 35 | 100 | 45 | 180 |
| Publication, retrait et livraison | 35 | 120 | 50 | 205 |
| Contrôles d’accès et cohérence après restauration | 35 | 100 | 55 | 190 |
| Recherche et lectures MDM pour les écrans | 25 | 75 | 30 | 130 |
| **Écrans d’administration et de gestion** | | | | **595** |
| Administration des modèles, sources et règles | 25 | 55 | 25 | 105 |
| Recherche et formulaires de fiche | 30 | 85 | 35 | 150 |
| Écrans de rapprochement et historique | 25 | 70 | 30 | 125 |
| Écrans d’anomalies, certification et publication | 30 | 75 | 30 | 135 |
| Écran d’import et d’export en masse | 15 | 45 | 20 | 80 |

Le moteur et les écrans représentent **2 405 JH**. Les **730 JH** d’adaptation métier et les **200 JH** de qualification transverse sont repris de la référence. La proposition centrale totalise **3 335 JH**, soit **665 JH de plus** que la décision active. Les composants remplacent ensemble les 12 livrables communs de **1 740 JH**. Les références de livrables répétées entre moteur et interface décrivent le rattachement fonctionnel. Le calcul ne compte le budget de référence de chaque livrable qu’une fois.

Les hypothèses d’autonomie supplémentaire représentent **220 JH** pour un studio de schéma complet, **100 JH** pour le mappage libre des imports et **130 JH** pour la recherche avancée sur les relations. Si les trois sont demandées, le total de ce scénario atteint **3 785 JH**. Ces montants décrivent des travaux supplémentaires identifiés. Ils ne constituent pas une fourchette de confiance.

## Lecture des 2 670 JH

L’enveloppe de **1 740 JH** pour moteur et interfaces suppose de retrouver **665 JH**, soit environ **28 %** de la proposition sur ces blocs. La réduction doit correspondre à des travaux dont la prise en charge par le socle est démontrée, ou à des parcours explicitement simplifiés. Les gains ne sont pas établis à ce stade. Le scénario à 3 335 JH demeure conditionnel à la qualification des composants partagés et des cibles de volumétrie et de reprise.

Le test de décision peut suivre une fiche et ses deux contributions concurrentes de l’admission à la certification, puis à la livraison et au rejeu. L’essai doit inclure les droits de champ, les relations, un rejet visible, la séparation après fusion et la conservation des preuves. Les mêmes critères, rejoués sur deux familles différentes, permettent de vérifier ce qui est vraiment commun et ce que l’équipe doit adapter.

Le fichier [engineering.json](engineering.json) conserve les hypothèses, l’effort par activité, les propriétaires de financement et les critères de réception. Le moteur somme les JH, recalcule le comparatif depuis les livrables de référence et restitue la proposition en dehors des simulations. Le repère COCOMO de **5 410 JH** reste calculé sur le corpus Unidata affiné. Le COSMIC historique ne qualifie pas ce nouveau découpage. [Référence par livrables](../../source/revision-master-data.yaml) · [Affinage COCOMO](../2026-11-05-affinage-unidata/audit.md)
