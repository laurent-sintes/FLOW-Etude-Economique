![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 20 octobre 2026

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

La première ligne vaut **(14 640 − 1 967) JH × 1 000 €** pour SAP et **(3 900 − 390) JH × 1 000 €** pour Microsoft. Les volumes et retraits sont expliqués plus bas. Ce sont des estimations de travaux, pas des offres fournisseurs révisées.

Le dossier utilise **un seul budget de référence par option**, avec ses hypothèses explicites. Les calendriers et le fonctionnement sont détaillés dans la [note sur quinze ans](12-modele-tco-buy-make.md).

### Répartition pour la comparaison

Le tableau de comparaison distingue les activités suivantes :

- **Flux :** interfaces, raccordement à la sécurité et échanges avec les autres systèmes.
- **Business :** données de référence, règles, politiques et configuration Beaumanoir.
- **Spécifiques :** extensions du progiciel nécessaires au besoin opérationnel.
- **Pilotage du projet et mise en service :** conduite du projet, tests, reprise des données et bascule.

Les lignes suffisamment détaillées des propositions sont classées directement. Les prestations regroupées sont réparties sous **hypothèse de l'étude**, tracée dans le classeur ; cette ventilation conserve le coût total. Les fonctions métier spécifiques de FLOW restent dans son **Build Core System**, sans ajout en intégration. Le pilotage, les tests et la mise en service déjà financés dans les charges de chaque solution ne sont pas ajoutés une seconde fois.

| Prestations de réalisation initiale, M€ HT fournisseur | FLOW | SAP | Microsoft |
| --- | ---: | ---: | ---: |
| **Build Core System** | **15,259** | **0,000** | **0,000** |
| Intégration — Flux et sécurité | 3,720 | 2,723 | 1,105 |
| Intégration — Business : configuration et accompagnement | 2,846 | 7,891 | 1,921 |
| Intégration — Spécifiques | Compris dans Core | 1,608 | 0,750 |
| Pilotage du projet, tests, reprises et mise en service — postes distincts | 2,250 | 4,911 | 1,960 |
| **Prestations, total** | **24,075** | **17,133** | **5,736** |
| Ressources techniques de construction hors souscriptions | 0,386 | CPI compté à part dans le calendrier | Runtime externe compté à part dans le calendrier |
| **Réalisation initiale retenue** | **24,461** | **17,133** | **5,736** |

Les montants sont arrondis à 0,001 M€ dans cette annexe ; la page de décision retient 0,1 M€. Les totaux exacts restent ceux des budgets initiaux. Pour FLOW, la dernière ligne isole les **2 000 JH de reprise des données** et les **1 000 JH de mise en service unique**, soit **2,25 M€**. Leurs anciennes contributions sont retirées de Flux et Business. **Les tests et le pilotage propres à chaque fonction restent dans le coût de cette fonction** : la rubrique distincte ne recense donc pas tout l'effort qualité et pilotage FLOW. Le [modèle de répartition](tools/flow_cost_structure.json) conserve les clés, les classements sources et les conventions estimées.

**SAP :** les 1 467 JH d'interfaces et les 1 319 JH de spécifiques sont identifiés dans la proposition ; les conversions et la mise à niveau initiale sont classées avec les reprises et la mise en service. Les autres travaux RFI sont répartis à **70 % en Business et 30 % en pilotage/tests/mise en service**, sous hypothèse. **Microsoft :** la ventilation du pilote reprend les lignes documentées ; les déploiements sont répartis à **20 % en Flux, 55 % en Business et 25 % en tests/mise en service**, sous hypothèse. Dans les deux offres, les tâches techniques transférées au prestataire utilisent une clé estimée de **40 % Flux, 20 % Business et 40 % qualification/reprises/bascule**. Ces répartitions rendent les budgets lisibles ; elles ne constituent pas de nouveaux devis par métier.

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

Le repère [Silkhom du 9 octobre 2026](https://www.silkhom.com/cout-projet-erp/) situe les intégrateurs de programmes ERP d'ETI entre **850 et 1 150 €/JH**. Il s'agit d'un ordre de grandeur publié par le cabinet, non d'une statistique de contrats signés. Ce repère documente le prix moyen retenu de 1 000 €/JH ; il ne devient pas une variante budgétaire basse/haute.

Les **extensions et la maintenance spécialisées** sont valorisées à **850 €/JH** : **hypothèse d'achat**, distincte du prix de l'équipe complète. Les [800 €/JH freelance F&O publiés par Dynalink](https://www.dynalink.io/etude) apportent un repère de spécialité, sans démontrer le futur prix vendu à Beaumanoir. L'automatisation des tests Microsoft utilise **750 €/JH**, tarif d'équipe de développement retenu pour FLOW ; il reste à confirmer pour cette prestation.

Le prix implicite du RFI SAP est **919,56 €/JH** : 13 462 352 € / 14 640 JH. Le pilote haut Microsoft correspond à **1 147,83 €/JH** : 2 640 000 € / 2 300 JH ; les lignes interfaces et développement sont à 1 000 €/JH. Ces prix dépendent des responsabilités et de la localisation proposées. Le courriel Microsoft mentionne une contribution nearshore/offshore ; les documents SAP ne permettent pas d'établir la localisation de toutes les journées.

La réalisation en France est donc chiffrée à partir des **jours et des rôles retenus**. Elle ne justifie pas un coefficient automatique ajouté aux forfaits de maintenance ou de supervision, dont les effectifs et la localisation sont inconnus.

## 3. Ce que les propositions RFI chiffrent

| Référence | Donnée documentée | Statut / point à confirmer |
| --- | ---: | --- |
| SAP : upgrade, programme Boardriders et déploiement Beaumanoir | **13 462 352 € HT**, somme de 395 000 + 7 768 577 + 5 298 775 ; **14 640 JH externes**. | Source fournisseur, indicative, septembre 2025. Total imprimé 15 462 352 € : écart de 2 M€ non expliqué, non ajouté. |
| Microsoft : pilote retenu pour la comparaison | **2 300 JH et 2,64 M€**. | Valeurs de l'estimation fournisseur retenues par le COPIL ; estimation sans engagement. Les propositions complètes restent dans les pièces sources. |
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
| **Coût retenu à 850 €/JH** | | **465 800 €** | **543 150 €** |

La feuille Passage Buy France expose les efforts par unité et les sous-activités ; tous les sous-totaux sont calculés dans Excel. Les huit charges relevées par l'audit et quatre autres charges Microsoft sont décomposées, soit douze calculs détaillés aux lignes 190 à 266. Le [détail SAP](tools/flow_sap_functional_gaps.json) et le [détail Microsoft](tools/flow_ms_functional_gaps.json) conservent aussi les commentaires du fournisseur et les exclusions. Le cahier de [gestion de la configuration](sources/Gestion%20de%20la%20configuration.pdf), pages 1–4, établit les besoins cible d'héritage, de publication, d'activation et de traçabilité.

**À confirmer :** chaque complément est désactivé si le standard, le paramétrage ou une adaptation déjà incluse fournit la capacité. Aucun moteur ERP, OMS, workflow générique ou solveur complet n'est reconstruit. L'optimisation supplémentaire reste inactive faute d'objectif nouveau établi.

**SAP — non double compte :** les adaptations déclarées et les **2 990 JH WRICEF** restent dans les 14 640 JH source : **1 319 spécifiques, 1 467 interfaces, 204 conversions**. L'offre de septembre précise ou inclut OMSA, IBP et Back Office ; les réponses de juillet mentionnant un composant tiers ne justifient pas un second achat. Les exclusions de WMS/TMS, réassort externe ou portail ne deviennent pas automatiquement des manques FLOW.

**Réserve sur l'unité SAP :** les valeurs source 10/18/28 de Low/Medium/High alimentent une colonne de coût supplémentaire sans unité établie. Elles ne sont pas assimilées à des JH fournisseur. Les charges en jours de cette étude sont des hypothèses locales ; elles ne démontrent pas une productivité Delaware.

**Microsoft — non double compte :** les commandes, allocations, workflows, substitutions et simulations déclarés standard ou custom restent dans le RFI, notamment les **230 JH de développement/customisation retenus pour le pilote**. Cette enveloppe n'est ni ajoutée à nouveau ni supposée disponible pour des besoins supplémentaires.

## 6. Tests, accompagnement et interfaces

| Prestation supplémentaire | SAP | Microsoft | Statut et calcul |
| --- | ---: | ---: | --- |
| Automatisation initiale des tests | 0 € | **315 000 €** | Exclusion Microsoft documentée ; hypothèse de 60 JH d'installation + 120 chaînes × 3 JH = 420 JH, à 750 €. SAP : exclusion non établie, pas de provision supplémentaire. |
| Supports et accompagnement des équipes | **360 000 €** | **360 000 €** | Hypothèse : 160 JH communs + 20 marques × 10 JH = 360 JH à 1 000 €. Microsoft : change exclu sauf utilisateurs clés/formateurs ; SAP : lignes formations à zéro, couverture globale à confirmer. |
| Nouvelles interfaces, sécurité supplémentaire, recette générale additionnelle et migration supplémentaire | 0 € | 0 € | Aucun besoin distinct assez identifié au-delà des prestations existantes. |
| **Total supplémentaire** | **360 000 €** | **675 000 €** | Hypothèses de volumes et de prix ; exclusions documentées seulement là où précisées. |

SAP prévoit déjà **705 JH de migration**, des tests d'intégration et de recette par domaine, de la gouvernance et du support infrastructure. Les 204 JH de conversions peuvent recouper la migration : ils ne sont pas automatiquement additionnés. Les interfaces de juillet et les tableaux de septembre ne sont pas deux budgets cumulables. Microsoft prévoit **460 JH retenus pour 40 interfaces du pilote**, de l'architecture, des tests et des outils de migration.

Les tests locaux des compléments sont compris dans leurs unités de développement. Les campagnes annuelles de tests sont dans la maintenance. La formation des utilisateurs clés déjà couverte et le temps métier interne sont exclus des suppléments d'accompagnement.

## 7. Travaux Finance retirés et tâches techniques confiées au prestataire

**Retraits — hypothèses de l'étude :** SAP détaille **2 810 JH Finance/FP&A** ; le calcul en retire **70 %, soit 1 967 JH**, en conservant 30 % pour les données juridiques, partenaires et échanges opérationnels. Microsoft n'a pas de ventilation équivalente : retrait de **10 % des 3 900 JH, soit 390 JH**, pour Finance et Commerce hors FLOW. Ces fractions ne constituent pas des économies commerciales confirmées. Les fonctions IBP opérationnelles et le Retail stock/retours restent conservés lorsqu'ils contribuent à FLOW.

**Tâches techniques confiées au prestataire — hypothèses de l'étude :**

`JH internes documentés ou convertis × 50 % IT × 60 % confiés au prestataire × part des travaux conservée après retrait Finance.`

La répartition **50 % IT / 50 % métier** vient du COPIL ; son application aux charges et le transfert de **60 %** restent hypothétiques. Le calcul donne **3 633,88 JH SAP** et **1 008 JH Microsoft**, à 1 000 €/JH. Il vise préparation technique, coordination SI, intégration, données et bascule. Les nouveaux compléments et les rôles déjà facturés par l'intégrateur en sont exclus. Le soutien métier, les arbitrages et la gouvernance internes restent hors facture fournisseur.

**Microsoft — volume de déploiement :** l'abaque Avanade fournit 100/200/400 JH selon la complexité d'une unité géographique. Le budget retient **un pôle = une unité complexe de 400 JH**, soit 2 300 + 4 × 400 = **3 900 JH**. Seuls le pilote et les abaques unitaires sont documentés : l'équivalence pôle/unité reste à confirmer. L'écart avec les 4,24 M€ historiques comprend ainsi une différence de volume supposé et de tarif, qui doivent se lire séparément.

## 8. Fonctionnement, licences et contrôles

SAP utilise les forfaits Delaware : **250 k€/an de MCO, 450 k€/an de supervision en horaires étendus et 350 k€/an d’évolutions**. FLOW et Microsoft restent estimés par activité en heures ouvrées. Les volumes des forfaits SAP ne sont pas documentés : **l’équivalence des niveaux de service et des capacités d’évolution n’est pas démontrée**.

Aucun supplément automatique de 3 %/5 % des développements n’est ajouté. Microsoft suppose que ses 30 correctifs annuels couvrent toutes les extensions et interfaces, compléments OMS compris. Pour SAP, le budget conserve les forfaits source ; **la couverture des compléments OMS/interfaces reste à confirmer**. L’absence de supplément ne démontre pas leur gratuité.

| Services retenus, année pleine avant inflation | SAP | Microsoft |
| --- | ---: | ---: |
| Maintenance applicative, tests de versions et pilotage | Forfait Delaware **250 000 €** | 306 JH × 850 € = **260 100 €** |
| Exploitation / supervision | Forfait Delaware **450 000 €**, horaires étendus | 234 JH × 850 € = **198 900 €** |
| Évolutions métier, budget retenu | Forfait Delaware **350 000 €** | 440 JH × 850 € = **374 000 €** |

SAP utilise les forfaits source. Microsoft est une **hypothèse d’ingénierie en France**, pas un devis de services : **306 JH × 850 € = 260,1 k€ de maintenance/pilotage**, **234 JH × 850 € = 198,9 k€ d’exploitation**, **440 JH × 850 € = 374 k€ d’évolutions**. Les quantités et efforts sont modifiables ; ils ne proviennent pas d’un historique d’incidents Beaumanoir. Aucun forfait SAP n’est transposé. La souscription couvre le produit standard ; les responsabilités exactes et la capacité des forfaits SAP restent à confirmer.

**FLOW entretient aussi son Core après livraison.** Le nominal retient **726 JH de maintenance/exploitation à 750 € = 544,5 k€**, **320 JH d'évolutions = 240 k€** et **400 k€ de ressources**, soit **1,1845 M€/an**. Les 162 k€/an de versions courantes sont compris dans ces enveloppes ; les 90 k€ de versions fonctionnelles sont un « dont » des évolutions. L'astreinte et les migrations majeures restent des options désactivées. Le [modèle TCO](12-modele-tco-buy-make.md) donne les frontières, calculs et dates de démarrage.
### Plateforme d'exécution et exploitation

| Service | SAP | Microsoft |
| --- | --- | --- |
| Hébergement du standard et environnements prévus dans l'offre | Compris dans le panier RISE proposé ; mémoire, stockage et PRA apparaissent déjà dans les lignes source. | Compris dans la souscription D365/K3 décrite par Avanade, avec les environnements prévus. |
| Plateforme d'intégration / exécution externe | CPI est annoncé hors budget source. Provision brute **151 222,08 €/an** à pleine charge, avant crédit BTP. | Provision conditionnelle **45 k€/an** pour des extensions externes ciblées ; à annuler si couvertes par les droits et capacités de l'offre. |
| Exploitation et supervision humaines | **450 k€/an**, forfait Delaware de monitoring en horaires étendus. | **198,9 k€/an**, hypothèse par activité en heures ouvrées ; aucune reprise du forfait SAP. |

La provision CPI utilise un repère catalogue SAP européen de **4 635 €/tenant/mois**, deux tenants cloud de production/recette et **6,08 €/mois par bloc additionnel de 10 000 messages**. Les volumes retenus — 5 millions de messages de production et 0,5 million de recette par mois — sont des hypothèses de trafic, distinctes des pièces vendues. **151 222,08 €** est le coût brut d'une année complète à pleine charge ; la recette seule coûte **59 195,04 €/an** et commence au chantier. Le tenant de production démarre aux premiers usages, ses messages suivent les livraisons.

**Le voucher BTP est inclus mais non valorisé dans Delaware p.43–45.** Le paramètre crédit imputable démarre à **0 € faute de montant**, sans affirmer une absence de crédit. Le coût brut doit être diminué de la part réellement utilisable pour CPI, après les autres consommations BTP. Le [contrat RISE private edition v10/2023, §1.4](https://assets.cdn.sap.com/agreements/product-use-and-support-terms/cls/en/rise-with-sap-s4hana-cloud-private-edition-supplement-english-v10-2023.pdf) renvoie au bon de commande ; il ne fixe pas un montant de crédit Beaumanoir. La provision reste conditionnelle à cette vérification et aux droits de souscription.

Microsoft ajoute **12 k€/an de recette externe dès le chantier**, puis jusqu'à **33 k€/an de production et services API/messages/logs** selon les livraisons. Ce panier finance uniquement l'exécution de compléments externes et reste une hypothèse de budget. L'hébergement du produit, le développement des interfaces et le traitement humain de leurs alertes ne sont pas ajoutés une seconde fois.

Les [abaques de ressources](tools/flow_platform_costs.json) distinguent prix catalogue, hypothèses de quantités et dépenses incluses. La [note de comparaison des services](16-methodes-et-presentation-comparaison-make-buy.md) présente leur couverture et les méthodes de référence. Les quantités sont stables dans le cas de référence (**croissance 0 %**) ; l'inflation modifie seulement le prix unitaire.

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
| Plateformes et exploitation | [Abaques plateforme](tools/flow_platform_costs.json), [abaque unique maintenance/exploitation](tools/flow_run_unified.json) ; [méthodes et grille de couverture](16-methodes-et-presentation-comparaison-make-buy.md). |
| Repères de prix | [Sources marché](03-references-marche.md) : dates, catégories de prix et limites. |

L'[archive de méthode](archives/methodes-remplacees/2026-10-20/15-rapprochement-buy-france.md) conserve les versions remplacées. Les anciennes fractions de coût Make, les majorations tarifaires retirées et les calculs de bornes ne servent pas au budget de référence actuel.

### Référence financière courante

Les charges initiales et compléments fonctionnels restent inchangés. SAP revient aux forfaits Delaware ; FLOW et Microsoft conservent leurs abaques. Les résultats recalculés figurent dans la [note de décision](04-resultats-etude.md).

Les budgets combinent sources et hypothèses explicitement distinguées. Les écarts ne démontrent ni une remise commerciale, ni une équivalence des services. Le service SAP en horaires étendus n’est pas réduit arbitrairement à une capacité en heures ouvrées.
