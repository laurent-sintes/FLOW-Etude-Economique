> **MÉTHODE HISTORIQUE — remplacée le 20 octobre 2026. Ne pas utiliser pour établir un budget. Consulter les méthodes courantes 11 et 12 dans le dossier principal.**

![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 19 octobre 2026

---

# FLOW Make : utiliser les charges Buy pour estimer l'intégration

**Version de travail — 19 octobre 2026.** Ce pont conserve un seul scénario cible : **FLOW Make**. Il utilise comme référence d'effort la proposition SAP/Delaware de septembre 2025 pour Beaumanoir, postérieure à la mission Synvance. Voir l'[analyse de périmètre](07-analyse-synvance.md). La source originale est dans l'archive `C:\Users\laure\OneDrive\Documents\Beaumanoir\OneDrive\00 - Etude Synvance.zip`, dossier `2-Etude/1. Benchmark ERP/2. Réponses RFI/SAP/20250915 - Présentation Delaware soutenance du 09092025/`, PDF `38319288909-Groupe-Beaumanoir-AO-Soutenance Processus Achats Ventes V2.pdf`, pages 37–41.

## 1. Définition du Build et des deux charges d'intégration FLOW Make

`Effort programme FLOW Make = Build du produit + Configuration/adaptation + Flux de données/sécurité`

| Poste exclusif | À compter dans ce poste |
| --- | --- |
| **Build** | Architecture et réalisation du logiciel FLOW : modèle de commandes, stock, promesse, allocation, optimisation, moteur de configuration gouvernée, écrans, API de référence, sécurité du produit, tests et documentation du produit. Il comprend aussi **tout développement métier propre à Beaumanoir** qui ne peut pas être exprimé par configuration. Dans un Make, ce code est une partie du produit à maintenir ; il ne constitue pas une troisième charge d'intégration. La construction d'un logiciel aussi **paramétrable qu'un progiciel du marché** est une hypothèse de qualité du produit, pas un simple nombre de tables de configuration. |
| **Intégration A — configurer et adapter au contexte Beaumanoir** | Définir le modèle opérationnel du groupe dans FLOW ; renseigner les entités, marques, enseignes, lignes produit et partenaires ; configurer les données maîtres opérationnelles, politiques, règles, priorités, habilitations métier et exceptions ; préparer et vérifier leurs valeurs initiales, simulations, validations et mises en production. Le modèle de données et les mécanismes de configuration sont du Build ; leurs instances et valeurs Beaumanoir sont ici. Une règle propre à une marque reste dans ce poste si le moteur sait l'exprimer sans code. |
| **Intégration B — développer les flux de données et brancher la sécurité** | Contrats, adaptateurs, événements/API, transformations, rejets, rejeu et rapprochement avec PLM, Commerce, finance, canaux et logisticiens ; pipelines techniques de reprise et de synchronisation ; fédération des identités, SSO/IAM, rôles et attributs d'entreprise, comptes de service, secrets et traces de sécurité. Le cadre générique de sécurité et les API standard de FLOW restent dans le Build. |

Les tests, le pilotage, la migration, le déploiement et le change traversent ces postes. Pour chiffrer, leurs JH doivent être **affectés au poste qui les cause** ou répartis explicitement avec une clé documentée ; ils ne forment pas une enveloppe supplémentaire à ajouter plusieurs fois. La migration se partage notamment entre préparation/qualité des données maîtres (A) et outillage/flux de reprise (B). Une exigence métier particulière va en configuration si le moteur sait l'exprimer ; sinon, son développement va au Build.

Les environnements, matériels, prestations d'hébergement, licences/support éventuels et coûts de fonctionnement après projet sont des **coûts non-JH ou récurrents**, à ajouter en euros ; ils ne se confondent pas avec ces deux masses de jours.

## 2. Ce que quantifient les deux propositions Buy

La poursuite du RFI a comparé **deux options Buy** : SAP/Delaware et Dynamics 365 + K3 Fashion avec Avanade. Le détail Delaware ci-dessous est le plus complet en JH pour le programme entier. La réponse Avanade fournit un **second point d'ancrage**, mais seulement pour le pilote ; le coût Microsoft full scope du COPIL est une extrapolation non ventilée par activité. Le [dossier de périmètre](07-analyse-synvance.md) distingue ces deux niveaux de preuve.

| Observation de la proposition SAP/Delaware de septembre | JH | Source / lecture |
| --- | ---: | --- |
| Lot 1 : upgrade du socle SAP existant | 421 intégrateur + 218 internes = **639** | Page 38. Travail propre à la trajectoire SAP, sans équivalent direct dans FLOW. |
| Lot 2 : core model Boardriders | 8 446 intégrateur + 8 034 internes = **16 480** | Page 38. Configure et adapte un produit SAP ; contient aussi des modules hors FLOW. |
| Lot 3 : déploiement Beaumanoir avec gaps | 5 773 intégrateur + 5 741 internes = **11 514** | Page 38. Déploiement et adaptations, notamment Retail back office. |
| **Total Buy proposé** | **14 640 intégrateur + 13 393 internes imprimés = 28 033**, mais **13 993 internes et 28 633 combinés par somme des lignes** | Page 38. Écart interne de **600 JH** à clarifier ; effort **proposé**, non consommé. Repère brut d'implémentation programme, pas mesure pure des interfaces. |

### Second point d'ancrage : pilote Microsoft/Avanade/K3

| Poste Avanade du pilote | JH proposés | Transposition prudente vers FLOW Make |
| --- | ---: | --- |
| Analyse et configuration du standard | 520–630 | Signal de configuration/adaptation, mêlé à l'analyse d'un produit Buy. |
| Intégration de 40 interfaces identifiées | 380–460 | Signal d'interfaces du pilote ; le nombre d'interfaces et les contrats FLOW ne sont pas établis par cette ligne. |
| Provision développement et customisation | 190–230 | Spécifique au produit Buy ; dans FLOW, les fonctions codées relèvent du Build. |
| Gouvernance et architecture | 320–380 | Inclut des activités de programme et d'architecture ; répartition Make à vérifier. |
| Tests, go-live et support | 490–600 | Seulement le pilote ; coexistence et support de la cible Make ne sont pas mesurés. |
| **Total du pilote Avanade** | **1 900–2 300** | Réponse Avanade, page 39 : **1,90 M€** affiché pour le pilote, ROM non engageant. |

Le COPIL 5 du 17 septembre, page 7, projette **2,64 M€ pour le pilote** et **1,60 M€ pour quatre autres pôles**, soit **4,24 M€ de coûts projet Microsoft**, hors abonnements et équipes internes. C'est une réestimation de Beaumanoir : les **1,90 M€** du pilote Avanade ne s'y ajoutent pas. Les JH des quatre pôles ne sont pas détaillés dans l'offre Avanade. Le COPIL considère l'offre Microsoft susceptible d'être sous-évaluée ; aucun multiplicateur automatique n'en est déduit. La solution regroupe Dynamics 365 et le vertical **K3 Fashion, éditeur indépendant** ; les **77 % de standard** du RFI concernent ce questionnaire, et non une fraction de FLOW.

Le total intégrateur est cohérent avec ses trois lignes (421 + 8 446 + 5 773 = 14 640 JH). Le total interne imprimé ne l'est pas : **218 + 8 034 + 5 741 = 13 993 JH**, contre **13 393 JH affichés**. La suite conserve cette incertitude au lieu de choisir silencieusement l'un des deux totaux.

### Rapprocher les prix sans confondre les unités

La proposition Delaware de septembre, **page 38 du PDF**, chiffre l'upgrade à **395 000 €**, le Core Model Boardriders à **7 768 577 €** et le déploiement Beaumanoir à **5 298 775 €**. La somme exacte est **13 462 352 € HT** ; les 13,463 M€ précédemment utilisés étaient un arrondi. Le total imprimé de **15 462 352 €** comporte exactement **2 M€ d'écart**. Le modèle retient la somme des composantes et conserve l'anomalie signalée, sans présumer l'explication de l'intégrateur.

Cette somme, divisée par les **14 640 JH externes**, donne **919,56 €/JH** pour le dispositif SAP. Pour Microsoft, le couple pilote haut du COPIL et charges hautes Avanade donne **2 640 000 € / 2 300 JH = 1 147,83 €/JH**. Le **1 000 €/JH** des seules lignes interfaces et développement/customisation Avanade, page 39, n'est pas le prix moyen du dispositif avec configuration, gouvernance, architecture et tests. Ces prix d'intégration de progiciel doivent être distincts du prix de réalisation FLOW. Une transposition de JH de configuration ou d'interfaces vers FLOW se fait d'abord en effort comparable, puis au prix du dispositif Make retenu ; reprendre le prix Buy dans le produit des JH Make confondrait les deux stratégies.

### Séparer effort d'intégration, fonctionnement et calendrier

Les coûts suivants complètent la comparaison économique mais **ne s'ajoutent pas aux JH d'intégration** :

| Source | Montant observé | Traitement dans une projection |
| --- | ---: | --- |
| Delaware septembre, PDF p.45, licences SAP selon la roadmap, Finance comprise | Années 1 à 5 : **790 633 ; 765 823 ; 973 480 ; 1 270 879 ; 1 270 879 € HT** | Les licences sont prévues dès la construction. Ne pas remplacer cette montée en charge par 1,27 M€ dès la première année. Les indexations de simulation se distinguent de cette base source « hors CPI ». |
| Delaware septembre, PDF p.37 ; questionnaire SAP, onglet 8, lignes 13–15 | **250 k€/an de MCO + 450 k€/an de monitoring des flux en horaires étendus + 350 k€/an de TMA évolutive**, après stabilisation | Trois services distincts. Si une enveloppe d'évolution en JH remplace les 350 k€, ne pas les compter une seconde fois. |
| Microsoft #1 p.38 et #2 p.22, panier de 950 utilisateurs Dynamics + K3 | **979 001,51 €/an**, identique dans les cinq colonnes annuelles | Aucun split tarifaire Dynamics/K3 trouvé. Protection des prix Dynamics sur contrat de cinq ans ; engagement K3 maximal de cinq ans. Le gel du panier est cohérent avec la table, sans clause de gel K3 isolée. |
| Questionnaire Microsoft, onglet 8 C13/D13 | **90 k€ en année 1** pour Unified + Project Quality Advisory, dont 200 h d'ingénierie Microsoft, Build/Run | Provision de première année distincte des licences et du MCO applicatif. La traiter comme ponctuelle dans le modèle est une convention ; sa récurrence n'est pas établie dans la source. Les zéros MCO/TMA du questionnaire ne démontrent pas un coût nul. |

Le calendrier de référence du **COPIL 5, page 7**, est **SAP 18 + 12 = 30 mois** et **Microsoft 18 + 20 = 38 mois**. Le questionnaire SAP de juillet, onglet 8 C20/C21, confirme 18 mois pour le premier socle et 30 mois au total. La proposition SAP de septembre, PDF p.39/p.40, affiche néanmoins **21 mois pour le lot 2 et 17 mois pour le lot 3**, sans expliciter les chevauchements permettant de rejoindre le COPIL ; la durée du lot upgrade n'est pas donnée. Le graphique de coût peut retenir les 30 mois simplifiés du COPIL, avec cette réserve.

Pour Microsoft, les quatre pôles représentent 20 mois au total, avec 6 à 9 mois par pôle dans le COPIL. Les dates exactes de démarrage, les chevauchements et les montants par pôle ne sont pas fournis. Tout échéancier de vagues ou division des **1,60 M€ en quatre enveloppes** est donc une hypothèse de projection, à afficher comme telle. Ces hypothèses servent à répartir les dépenses sur quinze ans ; elles ne modifient pas le périmètre fonctionnel documenté ni les charges comparables à FLOW.

Les pièces et chemins d'archive de ces compléments sont détaillés dans l'[analyse Synvance](07-analyse-synvance.md), sections « Abonnements et services de fonctionnement » et « Calendriers sources et échéancier de simulation ». Le calendrier, les prix unitaires, les abonnements et le monitoring doivent rester traçables dans le modèle sans être incorporés artificiellement aux seuls postes de configuration ou de flux.

Les deux matrices de charges détaillées (pages 39–40) répartissent les charges d'intégrateur des lots 2 et 3 ainsi :

| Lecture par étape | JH intégrateur | Ce que le chiffre peut apporter à FLOW |
| --- | ---: | --- |
| Étapes hors « réalisation » : préparation, analyse, blueprint, SIT, UAT, final prep, go-live et stabilisation | **8 860** | Repère observable pour la mobilisation d'implémentation, mais inclut aussi des domaines hors FLOW et du paramétrage SAP au fil de ces étapes. |
| Étape « réalisation » | **5 360** | Mélange configuration, extensions, écrans, rapports, interfaces et migration : ne pas traiter la totalité comme Build ou Intégration sans ventilation. |
| **Lots 2 + 3, somme des phases** | **14 220** | Les totaux imprimés des lots sont **14 219 JH** (8 446 + 5 773) ; écart d'un JH avec les phases, probablement dû aux arrondis. Les lignes de total des lots font foi pour le total programme. |

À la page 41, Delaware présente **2 990 JH de WRICEF** sur les lots 2 et 3 : conversions **204**, entrées **755**, sorties **712**, enhancements **303**, rapports **218**, formulaires **277**, Fiori **521**. Ces JH sont un **focus de réalisation**, pas une enveloppe à ajouter automatiquement aux 14 640 JH. Une lecture par nature de travaux donne :

| Nature de travail dans le Buy | Signal observable dans le WRICEF Delaware | Transposition au Make FLOW |
| --- | ---: | --- |
| Développements spécifiques au progiciel Buy | **1 319 JH** : enhancements 303 + rapports 218 + formulaires 277 + Fiori 521 | Dans le Make, les fonctions à développer vont au **Build FLOW**, qu'elles soient communes ou propres à Beaumanoir ; d'autres peuvent devenir de la configuration ou sortir du périmètre. Ces 1 319 JH SAP ne sont pas une estimation du Build correspondant. |
| Configuration/adaptation du contexte | **Aucun sous-total isolé** | Incluse avec la conception et les tests dans les lignes fonctionnelles et les phases ; impossible de l'extraire en JH de la proposition. Les **10 640 JH** par domaines fonctionnels constituent un contenant mixte, pas un chiffrage de configuration. |
| Flux de données | **1 467 JH** : entrées 755 + sorties 712 ; plus **204 JH** de conversions à examiner séparément | Repère d'interfaces SAP et de conversion technique sur ce périmètre Buy ; les contrats FLOW, les partenaires et les reprises peuvent différer. |
| Branchement à la sécurité du groupe | **Aucun sous-total isolé** | Ne pas interpréter l'absence de ligne comme un effort nul : SSO, IAM, autorisations et comptes de service restent à identifier. |

Les **1 319 + 1 467 + 204 JH** reconstituent les **2 990 JH** de ce seul détail WRICEF. Ils ne couvrent ni tout le Build Make, ni toute la configuration, ni tous les tests/déploiements, ni la sécurité ; ils sont déjà compris dans la proposition.

Les pages 39–40 montrent également, sur les lots 2 et 3, **717 JH** dans la ligne « reprise des données / tests spécifiques », **2 861 JH** de gouvernance, coordination et support infrastructure, et **10 640 JH** ventilés par domaines fonctionnels. Cette dernière masse comprend conception, paramétrage et tests de domaines SAP, pas du développement de plateforme Make. Ces sous-totaux sont **dans** les 14 219 JH des lots : ils ne s'y ajoutent pas.

## 3. Corrections de périmètre avant transposition

**Données observées à retrancher ou reclasser :**

- **639 JH** pour l'upgrade SAP (421 externes + 218 internes), sans équivalent direct dans la trajectoire FLOW Make.
- **2 810 JH d'intégrateur** affectés aux lignes « Manage Financial Process » et « Manage Financial Planning and Analysis » des lots 2 et 3. La finance est exclue de FLOW, mais la contribution interne correspondante n'est pas ventilée ; les interfaces vers FI/CO restent nécessaires. Ce chiffre est un **poste à examiner**, pas une déduction intégrale automatique.
- Une partie des **548 JH d'intégrateur** « Retail Store Operations » peut concerner le canal Retail maintenu autonome ; une autre recoupe les commandes et stocks communs. Même examen pour SAP IBP, les prix/conditions et la valorisation des stocks.
- Certaines extensions WRICEF correspondent à l'adaptation du standard SAP. Elles ne sont pas directement réutilisables, mais les **besoins métier** et les **interfaces** qu'elles servent peuvent rester dans FLOW.

**Travaux FLOW absents ou non démontrés dans cette proposition :** développements métier Make non exprimables par configuration (**Build**) ; sorties d'UR, Socloz et NewStore ; contrats exacts des canaux Retail/B2C/Wholesale ; éventuelles interfaces particulières des logisticiens et partenaires étrangers ; initialisation et gouvernance des règles et policies dans FLOW ; raccordement au dispositif de sécurité du groupe ; stratégie de bascule depuis Storeland/ECC vers un produit nouveau. Ne pas additionner automatiquement ces postes : le RFI contenait déjà des commandes B2C, stocks, allocations et même SAP OMSA dans la proposition de septembre.

Le calcul de départ est donc :

`Intégration FLOW Make (A + B) = charges Buy comparables de configuration et de flux/sécurité - fonctions hors FLOW + travaux d'intégration propres à FLOW ± écarts de complexité et de déploiement`

Ce calcul exige d'abord une **répartition** des charges Buy — **28 033 JH imprimés ou 28 633 JH par somme des lignes** — entre développements propres au Buy, configuration, flux/sécurité, fonctions hors FLOW et travaux transverses. Le WRICEF repère une partie des développements et des flux, mais ne donne pas une clé pour le reste. Les charges de configuration et de sécurité exigent une hypothèse indépendante ou une ventilation complémentaire de la proposition ; aucun solde arithmétique du Buy ne peut leur être attribué automatiquement. Les développements métier nécessaires dans le Make sont estimés avec le Build FLOW, **sans reprendre mécaniquement** les JH de spécifique SAP.

À ce stade, le Buy total est un **point d'ancrage brut documenté mais contradictoire**, pas une estimation corrigée d'Intégration FLOW Make. Le retrait de l'upgrade SAP (639 JH combinés selon les lignes) laisserait **27 394 JH sur le total imprimé ou 27 994 JH par somme des lignes**, avant les autres corrections. Ces soustractions n'isolent ni la configuration, ni les flux/sécurité, ni l'effort Make ; elles ne créent pas une fourchette d'intégration FLOW.

## 4. Conséquence pour le modèle d'effort FLOW existant

Le [premier modèle de 33 100–63 600 JH identifiés](06-premier-ordre-de-grandeur-effort.md) additionne déjà des postes métier et des postes d'intégration/migration/déploiement ; l'option Storeland est séparée. **Ajouter le total Buy à son total compterait deux fois** l'analyse métier, les interfaces, les reprises, les tests, les déploiements et l'implication interne. Il faut le **reclasser** en Build, configuration/adaptation et flux/sécurité avant de substituer, poste par poste, des charges Delaware aux hypothèses non calibrées du modèle. Un [abaque de répartition](09-abaques-repartition.md) rend cette première imputation vérifiable.

Un recalage court suffit pour l'ordre de grandeur :

1. Prendre dans la matrice Delaware les **lots 2 et 3**, les phases et les domaines, puis identifier les fonctions Finance, IBP, Commerce, Retail canal et upgrade à écarter ou réduire.
2. Ventiler les tâches Buy réellement comparables entre **développements spécifiques du Buy**, **configuration/adaptation**, **flux et sécurité** ; affecter aussi les tests, migrations, déploiements, pilotage et contributions internes à ces postes, sans double compte.
3. Dans le Make, classer **tout développement métier nécessaire** au Build FLOW ; une règle portée par le moteur va dans la configuration et un développement d'interface propre à un partenaire va dans les flux.
4. Ajouter les sorties d'applications et les contraintes nouvelles **seulement lorsqu'elles ne sont pas déjà couvertes** par les charges communes.
5. Présenter séparément le **Build**, les **deux postes d'intégration** et leur somme, avec une plage d'incertitude propre à chacun. L'option de 15 % pour le périmètre Storeland inconnu reste **hors nominal** et ne s'applique qu'une fois à la base identifiée.

Cette méthode permet d'utiliser l'effort Buy comme **référence de mobilisation du programme** tout en gardant un Build Make explicite. Elle évite de prétendre que le total Buy est la charge d'intégration FLOW déjà calculée.

