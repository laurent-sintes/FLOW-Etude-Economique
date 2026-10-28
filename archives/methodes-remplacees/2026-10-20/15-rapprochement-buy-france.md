> **ARCHIVE — remplacée le 20 octobre 2026. Ne pas utiliser pour une décision budgétaire. Les estimations basse/haute de cette version ont été retirées du dossier courant. Consulter la note de décision dans le dossier principal.**

![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 19 octobre 2026

# SAP et Microsoft — travaux et coûts retenus

Cette annexe explique les estimations SAP/Delaware et Dynamics 365 + K3/Avanade utilisées pour comparer le coût du projet FLOW. Les propositions RFI financent déjà une partie importante de la gestion des commandes, du stock et des allocations. Il faut identifier les **adaptations, interfaces, tests, déploiements et tâches techniques** nécessaires au périmètre FLOW, sans payer une seconde fois ce qui est proposé.

Les prix RFI restent identifiables. Les estimations complètes ci-dessous supposent une **équipe fournisseur autonome en France** et excluent le soutien métier interne Beaumanoir, selon la même convention que FLOW. Les progiciels conservent leur dépendance éditeur : la comparaison financière ne leur attribue pas la propriété du produit recherchée par FLOW.

## 1. Travaux à financer

| Nature de travaux | SAP | Microsoft |
| --- | --- | --- |
| Adapter, intégrer et déployer le progiciel | 14 640 JH externes documentés, avant retrait des travaux Finance hors FLOW. | Pilote jusqu'à 2 300 JH documentés ; hypothèse de 4 × 400 JH pour les autres pôles. |
| Compléter les exceptions de commande et la configuration | 548 JH estimés pour sept adaptations ciblées. | 639 JH estimés pour les mêmes familles de besoin. |
| Automatiser les tests | Aucun supplément activé : une exclusion de cette prestation n'est pas établie dans les pièces SAP. | 420 JH estimés ; exclusion par défaut documentée. |
| Accompagner les équipes | 360 JH de supports et d'adoption estimés ; couverture à confirmer. | 360 JH estimés, hors formation des utilisateurs clés et formateurs déjà prévue. |
| Confier au prestataire des tâches techniques prévues côté Beaumanoir | 3 633,88 JH estimés. | 1 008 JH estimés. |

**Statuts :** **Source fournisseur** = donnée explicitement proposée ; **Hypothèse de l'étude** = volume, tarif, fraction ou activité estimés ; **À confirmer** = couverture ou engagement restant à vérifier. Les 548 et 639 JH sont des provisions conditionnelles : une capacité non décrite précisément dans le RFI n'est pas une absence confirmée du produit. La provision est supprimée si la prestation déjà financée couvre le besoin.

| Travaux de réalisation initiale fournisseur | SAP, € HT | Microsoft, € HT |
| --- | ---: | ---: |
| Adaptation, intégration et mise en service du progiciel, hors travaux Finance retirés | 12 673 000 | 3 510 000 |
| Compléments fonctionnels ciblés | 465 800 | 543 150 |
| Automatisation supplémentaire des tests | 0 | 315 000 |
| Supports et accompagnement des équipes | 360 000 | 360 000 |
| Travaux techniques prévus côté client, confiés au prestataire | 3 633 879 | 1 008 000 |
| **Coût initial retenu, arrondi à l'euro** | **17 132 679** | **5 736 150** |
| **Plage conditionnelle** | **12,2–22,5 M€** | **3,3–9,1 M€** |

La première ligne vaut **(14 640 − 1 967) JH × 1 000 €** pour SAP et **(3 900 − 390) JH × 1 000 €** pour Microsoft. Les volumes et retraits sont expliqués plus bas. Les bornes calculées dans le classeur sont respectivement **12 173 510,24–22 525 792,58 €** et **3 283 050,00–9 078 216,67 €**. Ce sont des estimations de travaux, pas des offres fournisseurs révisées.

Les plages combinent hypothèses de quantité, de tarif et de responsabilités. Elles ne sont pas des probabilités. Les calendriers et le fonctionnement sont détaillés dans la [note sur quinze ans](12-modele-tco-buy-make.md).

## 2. Prix de prestation en France

Le prix moyen retenu pour une **équipe intégrateur complète est de 1 000 €/JH**, identique pour SAP et Microsoft. La composition ci-dessous est une **hypothèse de l'étude**, exprimée en prix vendus. Elle intègre déjà structure et marge du prestataire : aucune majoration supplémentaire n'est appliquée.

| Rôle | Part des jours estimée | Prix vendu HT par jour | Contribution à la moyenne |
| --- | ---: | ---: | ---: |
| Consultants fonctionnels | 40 % | 1 000 € | 400 € |
| Développeurs spécialisés | 25 % | 850 € | 212,50 € |
| Architectes | 15 % | 1 300 € | 195 € |
| Pilotage | 10 % | 1 200 € | 120 € |
| Qualification et tests | 10 % | 700 € | 70 € |
| **Total** | **100 %** | | **997,50 €, arrondis à 1 000 €** |

Le repère [Silkhom du 9 octobre 2026](https://www.silkhom.com/cout-projet-erp/) situe les intégrateurs de programmes ERP d'ETI entre **850 et 1 150 €/JH**. Il s'agit d'un ordre de grandeur publié par le cabinet, non d'une statistique de contrats signés. La fourchette sert à tester le prix moyen d'équipe ; elle ne signifie pas que chaque profil se facture dans cet intervalle.

Les **extensions et la maintenance spécialisées** sont valorisées à **850 €/JH**, avec plage de travail **750–1 000 €** : **hypothèse d'achat**, distincte du prix de l'équipe complète. Les [800 €/JH freelance F&O publiés par Dynalink](https://www.dynalink.io/etude) apportent un repère de spécialité, sans démontrer le futur prix vendu à Beaumanoir. L'automatisation des tests Microsoft utilise **750 €/JH**, tarif d'équipe de développement retenu pour FLOW ; il reste à confirmer pour cette prestation.

Le prix implicite du RFI SAP est **919,56 €/JH** : 13 462 352 € / 14 640 JH. Le pilote haut Microsoft correspond à **1 147,83 €/JH** : 2 640 000 € / 2 300 JH ; les lignes interfaces et développement sont à 1 000 €/JH. Ces prix dépendent des responsabilités et de la localisation proposées. Le courriel Microsoft mentionne une contribution nearshore/offshore ; les documents SAP ne permettent pas d'établir la localisation de toutes les journées.

La réalisation en France est donc chiffrée à partir des **jours et des rôles retenus**. Elle ne justifie pas un coefficient automatique ajouté aux forfaits de maintenance ou de supervision, dont les effectifs et la localisation sont inconnus.

## 3. Ce que les propositions RFI chiffrent

| Référence | Donnée documentée | Statut / point à confirmer |
| --- | ---: | --- |
| SAP : upgrade, programme Boardriders et déploiement Beaumanoir | **13 462 352 € HT**, somme de 395 000 + 7 768 577 + 5 298 775 ; **14 640 JH externes**. | Source fournisseur, indicative, septembre 2025. Total imprimé 15 462 352 € : écart de 2 M€ non expliqué, non ajouté. |
| Microsoft : pilote | **1 900–2 300 JH ; 1,90–2,64 M€** par somme des bornes. | Source fournisseur, estimation sans engagement. Le COPIL retient le haut de 2,64 M€. |
| Microsoft : quatre autres pôles | **1,60 M€**, soit **4,24 M€** avec le pilote haut. | Projection COPIL, sans charge groupe détaillée ni offre Avanade engageante pour tout le déploiement. |
| SAP : contribution interne | **13 993 JH** par somme ; 13 393 JH imprimés. | Source fournisseur ; écart de 600 JH à clarifier. |
| Microsoft : contribution interne | **8 personnes × 18 mois**, puis **4 × 20 mois**. | Source COPIL ; conversion de l'étude à 200 JH/an = 3 733,33 JH. |

Le **COPIL Beaumanoir du 17 septembre 2025, page PDF 8**, juge le coût projet Microsoft susceptible d'être sous-évalué ; SAP y est qualifié de coûteux. Cette réserve appartient au suivi Beaumanoir après la clôture de Synvance le 4 juillet. Le **COPIL Synvance du 2 juillet, slide 11**, signalait déjà des estimations approximatives et des hypothèses fournisseurs peu retraitées. Ces constats invitent à examiner les prestations ; ils ne démontrent aucun coefficient de sous-évaluation uniforme.

Le [courriel Microsoft du 16 septembre](tmp/synvance-review/microsoft-mail-2025-09-16.txt) précise les exclusions d'automatisation des tests et de conduite du changement, ainsi que les conditions de déploiement et de localisation. Ce sont des bases documentées pour des postes identifiés.

## 4. Couverture des fonctions FLOW

**Les offres incluent déjà des fonctions OMS.** Le coût supplémentaire ne correspond donc pas à la construction d'un OMS complet.

| Responsabilité FLOW | SAP proposé | Microsoft proposé | Adaptation à vérifier |
| --- | --- | --- | --- |
| Achats, ventes, retours, documents | S/4 Fashion SD et Back Office. | D365/K3 ; vente déclarée 74 % standard, 26 % customisation. | Variantes opérationnelles et transitions exactes. |
| Stock, réservations et protections | S/4, OMSA, Allocation Management. | Stock omnicanal, réservations, protections et allocations K3 ; Inventory Visibility mentionné. | Engagements cohérents entre canaux et prestataires ; traitement des écarts. |
| Promesse ATP/CTP/PTP | OMSA sourcing/disponibilité et ATP S/4. | ATP dans la carte applicative et réponses sur la promesse. | Explication des alternatives et contraintes ; profondeur de CTP/PTP. |
| Cycle de vie et fulfillment | S/4, Back Office et fonctions OMS proposées. | Service Provider Management, Delivery Scheduling et Workflow. | Exceptions communes entre applications et intervention humaine. |
| Allocation et optimisation | ARun, aATP/BOP, Allocation Management ; fonctions IBP proposées. | Allocation multicritère/multisource, stratégies, réallocation et simulations. | Objectifs supplémentaires réellement nouveaux, s'ils sont identifiés. |
| Configuration par marque, enseigne et ligne produit | Paramétrage, BRF+, workflows et adaptations proposées. | Paramétrage, workflows et adaptations D365/K3. | Héritage des règles, dérogations, publication coordonnée, activation datée et explication des décisions. |

Les taux de couverture RFI ne sont pas des taux de couverture FLOW et ne servent pas à multiplier le coût Make. La présence d'une capacité dans une licence ne démontre pas à elle seule que toute sa mise en œuvre est chiffrée.

**SAP OMSA :** proposé page PDF 26 et déjà inclus dans la souscription, référence 8012655 : **1 020 € en année 1, puis 21 420 €/an en années 2–5**. OMSA couvre sourcing et disponibilité ; le cycle de vie complet s'apprécie avec S/4, les allocations et le Back Office. Aucun second achat OMSA ni reconstruction complète n'est ajouté.

## 5. Sept compléments fonctionnels conditionnels

Les quantités sont communes pour comparer des besoins similaires. Les charges sont des **hypothèses d'ingénierie**, propres à une adaptation limitée des composants proposés. Elles comprennent analyse ciblée, réalisation, tests locaux et documentation ; elles excluent les prestations déjà chiffrées plus bas.

| Besoin cible à vérifier dans les prestations RFI | Unités estimées | SAP, JH retenus | Microsoft, JH retenus |
| --- | ---: | ---: | ---: |
| Exceptions de commande nécessitant une intervention entre applications | 6 parcours | 108 | 108 |
| Réorientation du fulfillment en cas d'échec d'un prestataire ou canal | 4 branches | 72 | 100 |
| Explication d'alternatives de promesse | 1 contrat et 3 explications SAP ; 1 ensemble Microsoft | 42 | 55 |
| Lien entre décision, faits, règles et versions appliquées | 4 types de décision | 72 | 80 |
| Héritage et dérogations entre règles communes et règles locales | 4 familles de règles et mécanisme commun | 100 | 107 |
| Publication coordonnée et activation datée de règles liées | 4 objets versionnés et mécanisme commun | 100 | 99 |
| Comparaison des effets avant activation de nouvelles règles | 2 jeux de comparaison et validation | 54 | 90 |
| **Total retenu** | | **548** | **639** |
| **Plage de charge basse / retenue / haute** | | **311 / 548 / 854** | **371 / 639 / 1 026** |
| **Coût retenu à 850 €/JH** | | **465 800 €** | **543 150 €** |

Le [détail SAP](tools/flow_sap_functional_gaps.json) et le [détail Microsoft](tools/flow_ms_functional_gaps.json) conservent les efforts par unité, les commentaires du fournisseur et les exclusions. Le cahier de [gestion de la configuration](sources/Gestion%20de%20la%20configuration.pdf), pages 1–4, établit les besoins cible d'héritage, de publication, d'activation et de traçabilité.

**À confirmer :** chaque complément est désactivé si le standard, le paramétrage ou une adaptation déjà incluse fournit la capacité. Aucun moteur ERP, OMS, workflow générique ou solveur complet n'est reconstruit. L'optimisation supplémentaire reste inactive faute d'objectif nouveau établi.

**SAP — non double compte :** les adaptations déclarées et les **2 990 JH WRICEF** restent dans les 14 640 JH source : **1 319 spécifiques, 1 467 interfaces, 204 conversions**. L'offre de septembre précise ou inclut OMSA, IBP et Back Office ; les réponses de juillet mentionnant un composant tiers ne justifient pas un second achat. Les exclusions de WMS/TMS, réassort externe ou portail ne deviennent pas automatiquement des manques FLOW.

**Réserve sur l'unité SAP :** les valeurs source 10/18/28 de Low/Medium/High alimentent une colonne de coût supplémentaire sans unité établie. Elles ne sont pas assimilées à des JH fournisseur. Les charges en jours de cette étude sont des hypothèses locales ; elles ne démontrent pas une productivité Delaware.

**Microsoft — non double compte :** les commandes, allocations, workflows, substitutions et simulations déclarés standard ou custom restent dans le RFI, notamment les **190–230 JH de développement/customisation du pilote**. Cette enveloppe n'est ni ajoutée à nouveau ni supposée disponible pour des besoins supplémentaires.

## 6. Tests, accompagnement et interfaces

| Prestation supplémentaire | SAP | Microsoft | Statut et calcul |
| --- | ---: | ---: | --- |
| Automatisation initiale des tests | 0 € | **315 000 €** | Exclusion Microsoft documentée ; hypothèse de 60 JH d'installation + 120 chaînes × 3 JH = 420 JH, à 750 €. SAP : exclusion non établie, pas de provision supplémentaire. |
| Supports et accompagnement des équipes | **360 000 €** | **360 000 €** | Hypothèse : 160 JH communs + 20 marques × 10 JH = 360 JH à 1 000 €. Microsoft : change exclu sauf utilisateurs clés/formateurs ; SAP : lignes formations à zéro, couverture globale à confirmer. |
| Nouvelles interfaces, sécurité supplémentaire, recette générale additionnelle et migration supplémentaire | 0 € | 0 € | Aucun besoin distinct assez identifié au-delà des prestations existantes. |
| **Total supplémentaire** | **360 000 €** | **675 000 €** | Hypothèses de volumes et de prix ; exclusions documentées seulement là où précisées. |

SAP prévoit déjà **705 JH de migration**, des tests d'intégration et de recette par domaine, de la gouvernance et du support infrastructure. Les 204 JH de conversions peuvent recouper la migration : ils ne sont pas automatiquement additionnés. Les interfaces de juillet et les tableaux de septembre ne sont pas deux budgets cumulables. Microsoft prévoit **380–460 JH pour 40 interfaces du pilote**, de l'architecture, des tests et des outils de migration.

Les tests locaux des compléments sont compris dans leurs unités de développement. Les campagnes annuelles de tests sont dans la maintenance. La formation des utilisateurs clés déjà couverte et le temps métier interne sont exclus des suppléments d'accompagnement.

## 7. Travaux Finance retirés et tâches techniques confiées au prestataire

**Retraits — hypothèses de l'étude :** SAP détaille **2 810 JH Finance/FP&A** ; le calcul en retire **70 %, soit 1 967 JH**, en conservant 30 % pour les données juridiques, partenaires et échanges opérationnels. Microsoft n'a pas de ventilation équivalente : retrait de **10 % des 3 900 JH, soit 390 JH**, pour Finance et Commerce hors FLOW. Ces fractions ne constituent pas des économies commerciales confirmées. Les fonctions IBP opérationnelles et le Retail stock/retours restent conservés lorsqu'ils contribuent à FLOW.

**Tâches techniques confiées au prestataire — hypothèses de l'étude :**

`JH internes documentés ou convertis × 50 % IT × 60 % confiés au prestataire × part des travaux conservée après retrait Finance.`

La répartition **50 % IT / 50 % métier** vient du COPIL ; son application aux charges et le transfert de **60 %** restent hypothétiques. Le calcul donne **3 633,88 JH SAP** et **1 008 JH Microsoft**, à 1 000 €/JH. Il vise préparation technique, coordination SI, intégration, données et bascule. Les nouveaux compléments et les rôles déjà facturés par l'intégrateur en sont exclus. Le soutien métier, les arbitrages et la gouvernance internes restent hors facture fournisseur.

**Microsoft — volume de déploiement :** l'abaque Avanade fournit 100/200/400 JH par unité géographique. Le calcul central retient **un pôle = une unité complexe de 400 JH**, soit 2 300 + 4 × 400 = **3 900 JH** ; plage de travail **250–650 JH par pôle**. Seuls le pilote et les abaques unitaires sont documentés : l'équivalence pôle/unité reste à confirmer. L'écart avec les 4,24 M€ historiques comprend ainsi une différence de volume supposé et de tarif, qui doivent se lire séparément.

## 8. Fonctionnement, licences et contrôles

Les forfaits SAP source sont conservés à **250 k€ de maintenance, 350 k€ d'évolutions, 450 k€ de supervision annuelle**. Le modèle ajoute l'entretien des fonctions supplémentaires, compare l'enveloppe d'évolutions à un panier de demandes et provisionne les mises à niveau S/4. Microsoft nécessite des hypothèses de maintenance et d'évolutions ; la supervision utilise la référence SAP. Les abonnements incluent déjà les services standard décrits par les fournisseurs. Le [modèle sur quinze ans](12-modele-tco-buy-make.md) détaille chaque calcul, l'inflation et les dates de démarrage.

Les prix sources de licence sont conservés. Les réductions Finance estimées restent conditionnées à un **panier commercial réellement réduit**, à confirmer. Les contrôles de l'Excel vérifient les formules et la propagation des paramètres ; ils ne valident pas le contenu des futures offres.

## 9. Sources et traçabilité

Archive originale : `C:\Users\laure\OneDrive\Documents\Beaumanoir\OneDrive\00 - Etude Synvance.zip`. Les pièces sont confidentielles ; les repères suivants permettent de contrôler les calculs.

| Pièce | Repères |
| --- | --- |
| COPIL 4 Synvance, 2 juillet 2025 | Slide 11 : estimations et hypothèses fournisseurs peu retraitées. |
| COPIL 5 Beaumanoir, 17 septembre 2025 | PDF p.4 : clôture Synvance ; p.7 : budgets, calendriers, équipes et licences Finance ; p.8 : réserve Microsoft. |
| Delaware, soutenance septembre 2025 | PDF p.26–28 : OMSA, SD, allocations et Back Office ; p.37 : fonctionnement ; p.38 : budget ; p.39–41 : charges et développements ; p.43–45 : licences. |
| Questionnaire SAP | Besoins fonctionnels et commentaires colonne H ; onglet 8 : fonctionnement et cadence de mises à niveau ; abaque Low/Medium/High sans unité JH démontrée. |
| Microsoft/Avanade, réponse PDF n°1 | p.13 : couverture RFI ; p.20–22 : stock et fonctions ; p.38 : souscriptions ; p.39 : pilote ; p.40 : unités géographiques ; p.47 : migration et phases. |
| Questionnaire Microsoft | Fonctions 229–231, 237/240, 242–249, 266–268, 278–287, 425/433/437 ; onglet 8 et Support : Unified, mises à jour et tests. |
| Courriel Microsoft, 16 septembre 2025 | [Extraction](tmp/synvance-review/microsoft-mail-2025-09-16.txt) : lignes 434–440 tests ; 491 localisation ; 509–512 déploiements ; 518–529 accompagnement. |
| Exigences FLOW | [Cahier des charges](01-cahier-des-charges.md), [gestion de la configuration](sources/Gestion%20de%20la%20configuration.pdf), [analyse Synvance](07-analyse-synvance.md). |
| Repères de prix | [Sources marché](03-references-marche.md) : dates, catégories de prix et limites. |

L'[archive de méthode](archives/methodes-remplacees/2026-10-19/15-rapprochement-buy-france.md) conserve les versions remplacées. Les anciennes fractions de coût Make et les majorations tarifaires retirées ne servent ni de prix central ni de borne actuelle.

