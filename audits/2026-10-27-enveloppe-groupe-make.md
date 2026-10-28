# FLOW Make — enveloppe proposée pour le passage au Groupe

27 octobre 2026. **Proposition d’opportunité non appliquée à la référence.** Prix de travail constants du modèle, k€ HT sans décimales. Hors construction du Flow Core System, déjà financée séparément.

## La proposition sponsor

**Retenir comme scénario central de travail 4 130 k€ HT pour Java / Spring Boot, 4 416 k€ HT pour .NET et 5 389 k€ HT pour Rust**, pour préparer, déployer et stabiliser le périmètre SCM Groupe après réception du Core. Ces enveloppes financent **Intégration & Migration**, pilotage compris, le **cycle de vie du Core System** et le **Run et MCO client** sur cette période.

**Le MCO client exclut le cycle de vie du Core System.** La lecture sépare ce qui est entretenu de sa période de financement : le produit générique a son cycle propre, réalisé en Make ou acheté auprès de l’éditeur en Buy. Le Run finance les moyens et leur exploitation ; le MCO client finance le maintien des adaptations et raccordements réceptionnés. Les agrégats historiques Build Core System / Intégration & Migration / Run & MCO du moteur restent inchangés à ce stade. Le build est hors de cette enveloppe ; une nouvelle lecture ne crée aucune dépense supplémentaire.

Elles reposent sur quatre unités de déploiement, 34 mois, 40 contrats de flux, une disponibilité explicite du pilotage externe et un service Core acheté séparément. Ce sont des hypothèses proposées et réfutables, **pas un devis ni un périmètre validé**. Les tarifs techniques hérités sont des hypothèses de prestation directe, sans marge intégrateur inventée ; les différences de tarifs entre stacks ne prouvent pas un surcoût du langage pour tous les métiers.

| Enveloppe centrale — k€ HT | Java / Spring Boot | .NET | Rust |
|---|---:|---:|---:|
| Intégration & Migration Groupe, pilotage compris | **2 756** | **2 920** | **3 330** |
| Cycle de vie du Core System pendant l’intégration | **512** | **595** | **1 014** |
| Run et MCO client pendant l’intégration, ventilation à préciser | **862** | **901** | **1 045** |
| **Total du passage au Groupe** | **4 130** | **4 416** | **5 389** |

**Périmètre externe IT uniquement** : les contributions internes IT/métier, la transformation organisationnelle, les systèmes historiques conservés et leur décommissionnement restent hors budget, conformément à l’étude. Le Run après la dernière stabilisation reste distinct. Le total ci-dessus n’est donc ni le coût complet de FLOW, ni un coût sur dix années de service.

## Des hypothèses explicites, avec une preuve de ce qu’elles permettent d’affirmer

| Sujet | Hypothèse centrale proposée | Appui et limite de la preuve |
|---|---|---|
| Déploiements | **Quatre unités**, candidates Boardriders, Vibs, Premium, La Halle. Deux paquets de 400 JH et deux de 200 JH, soit **1 200 JH**. La classification précise des pôles reste ouverte. | Le COPIL cite cinq pôles en précisant que Sarenza n’est pas dans le périmètre et la volumétrie initiaux. Avanade publie 200/400 JH par unité géographique à RACI comparable. Assimiler ces pôles à quatre unités est notre hypothèse, pas une validation fournisseur. [COPIL p.7–8](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Fcopil-5.pdf#page=7), [Avanade p.40](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Fmicrosoft-1.pdf#page=40). |
| Durée et ouvertures | **34 mois** après réception du Core ; ouvertures aux mois **18, 23, 28 et 32**, chacune suivie de deux mois de stabilisation. Les travaux des unités se chevauchent. | 34 mois est la durée de simulation actuelle, pas une roadmap validée. Le premier jalon de 18 mois est cohérent avec le repère COPIL ; les autres jalons sont proposés. Dernière stabilisation au mois 34. |
| Flux et données | **40 contrats × 10,5 JH = 420 JH** ; migration conservée à **280 JH**, avec deux répétitions par unité supposées dans cette charge. | Avanade détaille 40 interfaces et 380–460 JH sur son pilote ; les inventaires ne sont pas identiques. Le RFI mentionne deux SI, huit instances Storeland au total et l’absence de MAP/CBS du questionnaire d’interfaces. Retenir 40 contrats FLOW est une nouvelle hypothèse, pas un inventaire exhaustif. [Avanade p.39](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Fmicrosoft-1.pdf#page=39), [RFI p.4 et 7](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Frfi-presentation.pdf#page=4). |
| Pilotage externe | **0,5 ETP de direction + 1 ETP de coordination fonctionnelle/PMO**, pendant 34 mois, à 18 JH/ETP/mois : **918 JH**. Tarifs proposés de **1 000 et 850 € HT/JH**, soit **826 k€ HT**. | Le besoin d’organisation et d’équipes dédiées est documenté ; ni ces effectifs Make ni ces prix ne sont fournis par le COPIL. Ce sont des provisions d’opportunité à contractualiser. Les 2 371 JH de gouvernance/coordination SAP sont un contrôle de portée, pas un multiplicateur. |
| Maintien du Core | **12 corrections génériques et quatre releases/an pendant 34 mois**, sans gain de productivité, en capacité achetée séparément. | Volumes et charges unitaires repris du modèle de maintenance. Leur application pendant l’intégration est notre convention contractuelle proposée. Les corrections encore dues au titre de la garantie du build ne doivent pas être facturées une seconde fois. |
| Run & MCO pendant l’intégration | Moyens techniques communs dès le début ; exploitation partagée dès la première production ; support courant d’une unité après sa stabilisation. | Les prix et unités proviennent du modèle. La montée des usagers est supposée égale entre unités ; elle ne réduit pas artificiellement les coûts fixes. Le service humain 24/7 n’est pas ajouté. |

Le cas Avanade à 100 JH correspond à du **support seul avec davantage de travail client** : il n’est pas utilisé comme borne basse d’un service équivalent. Les abaques 200/400 portent sur des paquets fournisseur plus larges ; les reprendre comme capacité de déploiement Make, avec le contenu borné ci-dessous, est une hypothèse de travail et non une transposition démontrée.

Les 950 utilisateurs, dix applications externes et volumes de données restent les hypothèses existantes. Les 950 utilisateurs du RFI ERP ne sont pas un effectif SCM vérifié. Les huit instances ne deviennent ni huit nouveaux systèmes à construire, ni huit copies du Core, ni huit vagues imposées.

## Les responsabilités qui rendent les postes additionnables

Le passage de la base V1 à l’enveloppe Groupe constitue une **nouvelle proposition de répartition du travail**. Il ne prétend pas révéler une ventilation déjà validée du catalogue historique.

| Travail et rattachement métier | Financement retenu | Frontière proposée |
|---|---|---|
| Règles, parcours et adaptations — Replenishment `D05.e`, ATP `D03.i`, Process Definition Management | INT-001 à INT-005, conservés une fois | Fonctions génériques déjà livrées par le build ; variantes client mutualisées entre unités. Aucun forfait par capacité. |
| Flux, données et recettes communes — Reference Ingestion, Inventory Ledger `D01.g`, Sales/Transfer Orders `D04.i`/`D04.k`, Fulfilment Coordination `D06.d` | INT-006/007/010, conservés une fois | Contrats, mappings, scripts, répétitions de migration et recette transverse. Les paquets locaux n’ajoutent pas une seconde conception, une seconde répétition déjà prévue ni une seconde campagne transverse. |
| Formation, acceptation locale, bascule et stabilisation — Human Task Management, visibilité `BHV082`, registres et engagements | **Quatre paquets Groupe remplacent intégralement INT-012, INT-013 et les 120 JH d’accompagnement** | Matériel commun préparé une fois, adaptation locale, rejeu d’acceptation, formation des relais, bascule et deux mois de démarrage. Les corrections du produit générique restent hors de ces paquets. |
| Gouvernance | Coordination technique aux taux existants + direction/coordination de programme dimensionnée en ETP | Les leads techniques réalisent le suivi technique. Direction et PMO traitent risques, dépendances, fournisseurs, budget et préparation des arbitrages. Les décisions et validations métier internes restent à Beaumanoir. |
| Environnements et préparation du Run | INT-008/009/011 ; consommations techniques sur la durée | Les **60 k€ de préparation sont retirés** avant l’ajout des achats consommés sur 34 mois. Les travaux de configuration ne sont pas assimilés à l’achat des ressources. La fabrique produit reste dans le build. |
| Maintien et exploitation | MAI-003 pour le Core ; services client ciblés pendant les ouvertures | Produire une release générique et la qualifier/déployer dans le contexte client (MAI-006) sont deux livrables. Pendant les deux mois de stabilisation locale, assistance et défauts de démarrage sont dans le paquet ; ensuite seulement dans le service variable. |

Les liens réutilisent la [cartographie native et la grille](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/grille-complexite.yaml>). Les 43 situations servent aux critères d’acceptation ; elles ne déterminent ni 43 forfaits ni 43 interfaces. Ces frontières empêchent les doublons **dans la proposition** ; elles doivent devenir des responsabilités de livraison explicites dans le cadrage et les contrats.

Les charges communes héritées restent des hypothèses d’ingénierie : notamment les 280 JH de migration et les 250 JH de recette transverse Java ne sont pas validés par un nouvel inventaire. La carte justifie les responsabilités à couvrir, pas ces durées. Le calendrier proposé suppose une disponibilité suffisante des équipes ; la somme des JH ne démontre pas à elle seule sa faisabilité.

## Construction du budget central

| Poste — k€ HT | Java / Spring Boot | .NET | Rust |
|---|---:|---:|---:|
| Travaux communs conservés, coordination technique incluse | 1 210 | 1 314 | 1 605 |
| Quatre déploiements, coordination technique incluse | 720 | 779 | 898 |
| Direction et coordination de programme | 826 | 826 | 826 |
| **Intégration & Migration** | **2 756** | **2 920** | **3 330** |
| Maintien du Core pendant 34 mois | 512 | 595 | 1 014 |
| Moyens techniques pendant 34 mois | 374 | 374 | 374 |
| Exploitation et support transitoires client | 488 | 527 | 671 |
| **Regroupement historique Run & MCO pendant l’intégration** | **1 374** | **1 496** | **2 059** |
| **Enveloppe totale** | **4 130** | **4 416** | **5 389** |

Le total est calculé au centime avant affichage ; des lignes arrondies au k€ peuvent différer d’un k€ de leur somme visible. Le sous-total historique **Run & MCO** ci-dessus réunit encore cycle produit, Run et entretien client dans le moteur. La lecture sponsor en tête de document isole le cycle produit : **512 k€ pour le Core et 862 k€ pour Run/MCO client en Java**, soit les mêmes 1 374 k€. Ces lectures alternatives ne s’additionnent pas ; aucun sous-total n’est ajouté à ses détails.

Pour Java, le passage depuis la proposition V1 est entièrement réconcilié : **1 453 − 307 + 64 + 720 + 826 + 512 + 374 + 488 = 4 130 k€ HT** à l’arrondi près. Les **307 k€ retirés** comprennent formation, bascule, accompagnement, préparation et leur coordination ; les **64 k€** correspondent au passage de 30 à 40 contrats de flux. Les nouveaux paquets ne viennent donc pas simplement s’ajouter à toutes les provisions précédentes.

Le maintien Core utilise les unités génériques actives : 10/10/14 JH par correction et 45/50/75 JH par campagne de release pour Java/.NET/Rust, avec les profils et le pilotage de maintenance existants. Le scénario finance une capacité hors garantie et les releases ; il n’établit pas que douze corrections payantes seront effectivement nécessaires chaque année. Si tout ce service est déjà financé ailleurs, son retrait vaut **512 / 595 / 1 014 k€** ; ce retrait exige une inclusion démontrée, pas une garantie présumée.

Les **six évolutions fonctionnelles génériques annuelles ne sont pas commandées dans le central** : le Core est supposé conforme au périmètre à sa réception. Les commander pendant 34 mois ajouterait, séparément, **225 / 268 / 416 k€ HT**. Il s’agit d’une option de changement fonctionnel, pas d’un maintien obligatoire.

Les moyens communs représentent **72 k€ de cloud + 36 k€ d’iPaaS + 24 k€ d’outillage/support acheté par an**, soit 374 k€ sur 34 mois, sans économie de montée en charge supposée et sans multiplication par pôle. Le travail d’exploitation humaine est distinct.

L’exploitation partagée des flux, des déploiements de releases, de la plateforme et de la sécurité (MAI-005/006/007/008) fonctionne **une fois pendant 16 mois**, de la première ouverture à la fin du programme. Support N1/N3 et corrections d’extensions (MAI-001/002/004) suivent les cohortes stabilisées : **6,75 mois équivalents de périmètre complet**, sous l’hypothèse de quatre parts égales. Les nouveaux flux encore livrés par le projet ne sont pas refacturés comme entretien ; le service porte les contrats acceptés. Pas de prorata des prestations fixes par nombre d’utilisateurs.

## Contrôle du regroupement historique : une seule facturation par travail et période

Les mois ci-dessous sont relatifs au début de l’intégration, après le build. Les intervalles excluent leur borne de fin : au mois 34, le régime à pleine capacité prend le relais ; aucune dépense postérieure n’est ajoutée dans cette proposition.

| Composante du Run & MCO central | Période financée ici | Vérification |
|---|---|---|
| Maintien du Core et achats techniques communs | Début de l’intégration → mois 34 | Une fois pour le Groupe ; ni une fois par pôle ni une annuité complète supplémentaire. |
| Exploitation partagée | Mois 18 → mois 34 | 16 mois, même pendant la stabilisation locale : exploitation de la plateforme et des contrats acceptés, distincte des défauts de démarrage locaux. |
| Support courant et corrections d’extensions, unité 1 | Mois 20 → mois 34 | 14 mois après les deux mois de stabilisation financés dans son paquet d’intégration. |
| Même service, unité 2 | Mois 25 → mois 34 | 9 mois après stabilisation. |
| Même service, unité 3 | Mois 30 → mois 34 | 4 mois après stabilisation. |
| Même service, unité 4 | À partir du mois 34 | Aucun mois courant ajouté avant la fin de sa stabilisation ; relais par le Run & MCO à pleine capacité, hors de cette enveloppe. |

Les 25 % par unité donnent bien **(14 + 9 + 4 + 0) / 4 = 6,75 mois** de service variable à périmètre complet. Le contrôle mensuel confirme que stabilisation et service courant d’une même unité ne sont jamais facturés simultanément dans la proposition.

Les autres frontières ont également été vérifiées :

- **Préparation :** les 60 k€ initiaux sont retirés avant de financer les consommations techniques sur la durée. Configuration et préparation du Run (INT-008/009/011) restent des travaux distincts de l’hébergement et de l’exploitation récurrente.
- **Bascule et accompagnement :** INT-012, INT-013, les 120 JH complémentaires et leur coordination sont retirés ; les paquets Groupe les remplacent.
- **Core et releases client :** MAI-003 finance le produit générique hors garantie ; MAI-006 finance les mises à jour ultérieures dans le contexte client. La réception initiale déjà dans INT-010 n’est pas reprise en maintenance. Les paquets de stabilisation ne financent pas une seconde correction générique.
- **Pilotage :** chaque prestation de Run & MCO comprend son pilotage technique une seule fois ; aucun taux supplémentaire ne s’applique au sous-total Run & MCO. Direction et coordination de programme ont des responsabilités distinctes.
- **Relais à pleine capacité :** aucune annuité du Run de référence n’est ajoutée aux mois déjà financés ici. Lors d’une éventuelle application, la projection devra remplacer les périodes concernées, pas additionner cette enveloppe au plan existant.

**Aucun double compte identifié dans le calcul et les frontières proposées ; les montants restent inchangés.** Les inclusions réelles des contrats et de la garantie restent à confirmer : le contrôle ne prouve pas qu’une prestation doit être achetée si elle est déjà due par un fournisseur.

## Run, MCO client et cycle du Core : compatibilité avec Microsoft et SAP

**Le découpage est pertinent pour les responsabilités ; il n’est pas intégralement disponible dans les prix fournisseurs.** La date ne définit pas la nature : le Run commence à la consommation des environnements ; le MCO client prend le relais de la réalisation et de la stabilisation du périmètre réceptionné ; le Core garde son calendrier de produit. Si les unités sont réceptionnées successivement, du MCO client peut commencer alors que d’autres unités sont encore en intégration.

| Entrée | Ce que la pièce permet de distinguer | Traitement proposé |
|---|---|---|
| Trois Make | Corrections et releases génériques MAI-003 ; hébergement et exploitation ; corrections client MAI-004 et compatibilité MAI-005/006 | Isoler le cycle produit du MCO client. Ventiler les activités mixtes sur leurs travaux, pas par un pourcentage forfaitaire. Dans le présent central, **512 / 595 / 1 014 k€** sont déjà isolables pour le Core ; le solde **862 / 901 / 1 045 k€** reste à détailler entre Run et MCO client. |
| Microsoft, abonnement **979 k€ HT/an** dans les cinq années sources | La page PDF 38 indique explicitement droits, maintenance du standard, infrastructure Azure, sandbox et services managés dans la souscription | Le cycle du Core éditeur et une partie du Run sont achetés ensemble. Un seul prix, des inclusions décrites ; **parts financières non ventilées**, pas un prorata Run/MCO inventé. L’abonnement ne démontre pas la prise en charge des adaptations client. |
| Microsoft, **90 k€ HT initiaux** | Support Unified / Project Quality advisory, année 1 ; aucune récurrence établie | Garder l’affectation initiale unique du modèle ; ne pas créer une maintenance annuelle ni une seconde ligne Run du même montant. |
| SAP, RISE et BOM | Abonnement produit groupé ; le RISE arrondi **1 270 k€** de la synthèse est déjà représenté par la BOM précise, notamment **1 271 k€** en années sources 4–5 | Cycle produit et inclusions de plateforme gardés dans un seul achat. Aucun ajout du RISE à la BOM ; aucune ventilation financière forcée entre Run et cycle du Core. |
| SAP, monitoring **450 k€ HT/an** | Surveillance des flux en horaires étendus, après stabilisation | Lecture Run cohérente avec la prestation annoncée. Ce prix ne prouve pas l’inclusion des modifications des contrats de flux. |
| SAP, forfait appelé MCO **250 k€ HT/an** | MCO hors évolutions, après stabilisation ; détail contractuel insuffisant | Le rattacher au maintien client sans en déduire une séparation financière exacte des éventuelles tâches d’exploitation. Conserver le forfait et les inclusions ; ne pas ajouter les JH qu’il remplace. |
| SAP, TMA évolutive **350 k€ HT/an** | Enveloppe distincte d’évolutions, après stabilisation | Distinguer les évolutions commandées du maintien en état et de la roadmap normale du Core éditeur ; périmètre à qualifier, pas un second entretien du standard. |

Preuves : [Microsoft, page PDF 38](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Fmicrosoft-1.pdf#page=38), [Delaware, page PDF 37 et BOM pages 43–45](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Fdelaware-septembre.pdf#page=37), [qualification des prix et inclusions Microsoft](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/maintenance/maintenance-microsoft.yaml:697>), [qualification SAP](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/maintenance/maintenance-sap.yaml:582>). Les périodes sources des offres ne sont pas automatiquement les années du calendrier FLOW.

Pour rendre le modèle composable, séparer **objet financé** (Core produit, adaptations client, moyens), **prestation** (construire, exploiter, maintenir, faire évoluer), **période** et **financement**. Un achat groupé peut financer plusieurs prestations mais n’est compté qu’une fois. Les inconnues de ventilation restent non chiffrées ; cela n’empêche pas de connaître le prix global. Le total reste comparable, même lorsqu’on ne peut pas produire deux totaux Run/MCO parfaitement séparés pour chaque Buy.

### Hébergement pendant le build

L’hébergement des environnements de fabrication est du **Run pendant le build**. Aucun budget explicite correspondant n’a été identifié dans le calcul actif : le build valorise les prestations et leur pilotage ; les **8 € par JH** couvrent assistance de développement, dépôts et outillage, sans preuve d’inclusion du cloud. Le projecteur actif ne déclenche l’hébergement annuel Make qu’après l’intégration.

Cette dépense demeure **non chiffrée et hors de l’enveloppe présente**, qui commence après réception du Core. Il faut dimensionner les environnements de développement, tests et qualification sur leur période d’usage ; on ne peut pas appliquer automatiquement les 72 k€ annuels du socle complet. Une même consommation ou un même abonnement devra être réparti entre périodes sans double facture. Sources : [coûts communs](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/calibration-couts.yaml:112>), [calcul du build](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/calculate_costs.py:150>), [déclenchement actuel du Run](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/project_investment.py:228>).

## Plage d’opportunité et facteurs qui la font varier

| Scénario conditionnel — k€ HT | Java / Spring Boot | .NET | Rust |
|---|---:|---:|---:|
| Bonne adhérence : quatre unités à 200 JH, 30 flux, coordination de programme à mi-temps, 34 mois | 3 566 | 3 826 | 4 748 |
| **Central : deux unités à 400 JH et deux à 200 JH, 40 flux, coordination à plein temps, 34 mois** | **4 130** | **4 416** | **5 389** |
| Renforcé : quatre unités à 400 JH, 50 flux à 11,5 JH, 140 JH de migration supplémentaires, direction et coordination à plein temps, 42 mois, 18 corrections et six releases/an | 5 834 | 6 242 | 7 706 |

Ce sont **trois scénarios de travail**, pas un intervalle statistique, une borne garantie ou un plafond commercial. Le scénario renforcé explicite chaque supplément ; aucun pourcentage général d’aléas n’est ajouté pour masquer des travaux inconnus. Les tarifs de pilotage, la qualité des données, le contenu des paquets et la capacité de réalisation restent déterminants.

Sensibilités isolées autour du central Java, sans les cumuler mécaniquement :

| Modification | Effet sur l’enveloppe, k€ HT |
|---|---:|
| Dix contrats de flux supplémentaires, autres charges conservées | +64 |
| Quatre unités complexes au lieu de deux | +240 |
| Tarifs techniques hauts déjà présents dans les stacks | +252 |
| Direction de programme à plein temps | +306 |
| Six mois de retard avant toutes les ouvertures, trajectoire ensuite décalée | +302 |
| Six mois de présence programme et de service supplémentaires après les ouvertures prévues, hors reprises de travaux | +566 |
| Moitié des usagers dans la première unité ouverte | +67 |

Le retard avant production et la prolongation après ouverture n’ont pas le même coût : le premier prolonge direction, Core et moyens ; la seconde prolonge aussi les services client. Ces tests ne financent pas une reprise fonctionnelle complète ni des journées additionnelles de déploiement causées par un échec de recette.

## Ce qui est défendable devant le sponsor

La proposition devient une enveloppe Groupe conditionnelle parce que **les responsabilités jusque-là ouvertes sont désormais dimensionnées**, et que le Run & MCO démarrant pendant l’intégration est inclus. Elle reste une estimation d’opportunité : elle permet de discuter un ordre de grandeur et ses conditions, pas d’engager un forfait.

Formulation proposée : « Pour le périmètre SCM actuel, après livraison d’un Core conforme, nous proposons une enveloppe de passage au Groupe de **4 130 k€ HT en Java**, dont **2 756 k€ d’Intégration & Migration**, **512 k€ pour le cycle de vie du Core** et **862 k€ de Run et MCO client** pendant le déploiement. Elle suppose quatre unités, 40 contrats de flux et 34 mois. Notre scénario renforcé porte cette enveloppe à **5 834 k€ HT**. Le cadrage devra confirmer en priorité les unités et variantes métier, la qualité des données et le partage entre garantie du produit, entretien du Core et maintien des adaptations client. »

Le chiffrage doit être rouvert si ces hypothèses d’étendue ou de service changent. Le besoin d’une équipe métier interne dédiée est une condition de livraison, pas une économie du budget externe. Les trois stacks partagent le même périmètre ; ce dossier ne recommande pas une stack sur la seule base de ces montants.

**Aucune économie par rapport aux 9 889 k€ SAP retraités n’est annoncée.** L’analogie SAP contient encore des différences de processus, de lots, de profils et de maturité ; elle ne valide pas les volumes Make. De plus, notre total inclut maintenant des services dont les Buy portent une partie dans leurs annuités. Comparer directement 4 130 à 9 889 k€ serait une comparaison d’assiettes différentes.

Le remplacement éventuel de la référence devra modifier ensemble le budget d’intégration, la montée du Run, le calendrier et les dépenses aux horizons 3/5/7/10 ans. **Aucune de ces modifications n’est appliquée ici.** La référence Make reste **9 889 k€ HT d’intégration**, avec ses durées et simulations existantes.

## Traçabilité et vérifications

La [définition YAML](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/audits/2026-10-27-enveloppe-groupe-make.yaml>) est l’emplacement des hypothèses nouvelles. Elle dépend du [rapprochement précédent](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/audits/2026-10-27-integration-make-rapprochement.md>), des pièces localisées ci-dessus et des sources actives de charges, tarifs et maintenance. Les hypothèses proposées sont distinguées des faits documentés.

Le [calcul reproductible](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/audits/2026-10-27-enveloppe-groupe-make-calcul.py>) écrit uniquement les [preuves d’audit](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/audits/2026-10-27-enveloppe-groupe-make-preuves.json>). Contrôles : empreintes de la base vérifiées ; activités conservées et remplacées disjointes ; rapprochement du budget V1 au centime ; sommes des postes publiés ; chronologie des cohortes sans simultanéité de stabilisation et de support courant ; maintien Core séparé des services client ; coûts fixes non divisés par les usagers ; sens des sensibilités ; identifiants métier natifs valides ; **2 193 fichiers actifs suivis identiques avant et après calcul**. Ces contrôles prouvent la cohérence du calcul proposé, pas la validation terrain des hypothèses.
