> **Historique — retiré de la base active le 24 octobre 2026.** Les hypothèses et résultats de cette note sont remplacés par le [modèle YAML actuel](../../source/README.md).

![Logo eXalt](<../../assets/exalt-logo.png>)



**Laurent Sintès** · 21 octobre 2026



---



# FLOW — charges de réalisation retenues



## Référence : 32 100 JH



L'estimation retient **32 100 JH pour réaliser FLOW et le mettre en service une fois**, avec un prestataire autonome en France. À 750 €/JH, les prestations initiales valent **24,075 M€ HT**. Les ressources techniques consommées pendant la construction représentent **386 k€**, distincts des JH ; la réalisation initiale totale atteint donc **24,461 M€ HT**. Le calcul est détaillé dans la [méthode du budget initial](<11-cout-nominal-minimum.md>).



Un JH représente une journée de travail d'une personne. La convention de 200 JH par personne et par an donne **160,5 ETP-années**, soit une capacité arithmétique moyenne de **32,1 ETP sur cinq ans**. Ce quotient ne définit pas l'effectif nécessaire à chaque phase : il ne traite ni les dépendances, ni la montée en charge, ni les pics.



Les postes ci-dessous sont des **postes de chiffrage**, pas des lots de roadmap. Leurs charges sont des hypothèses d'ingénierie sur le périmètre identifié. Elles couvrent la conception, la réalisation, les écrans opérationnels nécessaires, les tests et le pilotage propres à chaque fonction. Les activités distinctes de reprise et de mise en service ne sont pas répétées dans ces fonctions.



## Détail des quatorze postes



| Poste de chiffrage | JH retenus | Ce qui est réalisé |

| --- | ---: | --- |

| Références opérationnelles | 1 400 | Références locales et ingestion des maîtres externes ; PLM et Commerce restent maîtres des produits et prix. |

| Politiques de supply chain | 1 000 | Politiques initiales, protection et éligibilité ; moteur de configuration commun distinct. |

| Gestion du stock | 3 000 | Positions, propriété, réservations, mouvements, corrections et rapprochement. |

| Disponibilité et promesse | 1 700 | ATP/CTP/PTP, explication de la promesse et engagements concurrents. |

| Gestion des commandes | 3 500 | Achats, ventes, transferts, retours, versions, exceptions et intercompany. |

| Gestion des dossiers et processus | 1 800 | Cas d'exception, tâches, interventions et supervision. |

| Orchestration du fulfillment | 1 800 | Plan de fulfillment, coordination, suivi et adaptation ; exécution WMS/TMS exclue. |

| Commandes de prestation et documents | 1 400 | Commandes aux partenaires et documents opérationnels, sans comptabilité ni paiement. |

| Plan opérationnel et carnet de commandes | 3 500 | Optimisation, contraintes, arbitrage du carnet et traitements d'allocation. |

| Configuration gouvernée | 4 000 | Héritage, dérogations, versions, simulation, publication, activation, audit et provenance. |

| Interfaces et contrats entre systèmes | 3 000 | Adaptateurs, transformations, contrôles, rejeu et observabilité des échanges. |

| Reprise des données opérationnelles | 2 000 | Références nécessaires, commandes ouvertes, stock de départ et rapprochement ; reprise exhaustive des historiques exclue. |

| Plateforme technique et qualification | 3 000 | Environnements, CI/CD, sécurité, résilience, performance et qualification entre domaines. |

| Mise en service unique | 1 000 | Préparation, répétition, formation fournisseur, bascule et démarrage. |

| **Total de référence** | **32 100** | |



## Frontière et options



Le modèle de référence est le domaine [Supply Chain Management publié](<../../sources/client/cartographie-2026-10-17.1.yaml>), complété par les exigences de [configuration](<../../sources/Gestion de la configuration.pdf>). Les capacités du modèle servent à contrôler la couverture ; aucun nombre fixe de jours par capacité n'est appliqué.



Le périmètre est opérationnel. Finance, contrôle de gestion, conformité, design, planification stratégique, gestion commerciale et exécution logistique restent dans les outils ou entreprises dédiés. FLOW doit les raccorder pour piloter commandes, stock, promesse et fulfillment.



Les développements Storeland non découverts restent une **option de 15 %, soit 4 815 JH et 3,61125 M€ HT**, hors référence. L'option n'est pas ventilée entre Core, configuration et interfaces tant que ces fonctions ne sont pas identifiées. Les contributions internes Beaumanoir, le fonctionnement après livraison, la coexistence prolongée et les lots additionnels restent séparés.



## Lecture de l'effort



Les principaux facteurs susceptibles de modifier la charge sont la profondeur des règles configurables, la cohérence du stock sous concurrence et les interfaces/reprises effectivement nécessaires. Les volumes annuels de pièces ne multiplient pas le développement ; les pics servent à confirmer les exigences de performance.



La [répartition par nature de travaux](<09-abaques-repartition.md>) explique la structure du budget. Les propositions SAP et Microsoft permettent de comparer des fonctions et des activités d'intégration ; elles ne constituent pas une mesure directe de l'effort de construction FLOW.

