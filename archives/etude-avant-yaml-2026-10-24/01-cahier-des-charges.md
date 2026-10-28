> **Historique — retiré de la base active le 24 octobre 2026.** Les hypothèses et résultats de cette note sont remplacés par le [modèle YAML actuel](../../source/README.md).

![Logo eXalt](<../../assets/exalt-logo.png>)



**Laurent Sintès** · 19 octobre 2026



---



# Cahier des charges FLOW — plateforme opérationnelle Make



**Statut :** périmètre de référence pour estimation, 21 octobre 2026. **Destinataires :** responsables métier, architecture, produit et estimation FLOW.



FLOW doit permettre au groupe Beaumanoir de piloter les commandes et les flux de supply chain de Beaumanoir et Boardriders, avec une vision commune du stock physique et de la disponibilité promise. Le code métier et les règles opérationnelles doivent rester maîtrisés par Beaumanoir. La souplesse de configuration par marque, enseigne, ligne produit et autres axes pertinents est une exigence centrale : ajouter ou modifier une règle courante ne doit pas nécessiter systématiquement une évolution du code applicatif.



## Contexte et hypothèses confirmées



- Deux systèmes d'information et deux ERP historiques sont à remplacer ou à rapprocher pour les fonctions concernées : SAP ECC AFS côté Boardriders et Storeland côté marques historiques Beaumanoir.

- Les fonctions concernées dans UR pour la prise de commandes B2C, Socloz et NewStore sont à remplacer dans le périmètre défini ci-dessous.

- La cible combine un cœur opérationnel commun et des systèmes de canal autonomes : Retail, EComm B2C et Wholesale.

- Environ 20 marques, des flux internationaux et intercompany, une centrale d'achat, plusieurs fournisseurs logistiques et des partenariats à l'étranger structurent la complexité métier.

- Volumes communiqués : environ 120 millions de pièces vendues par an et plusieurs centaines de milliers de commandes de vente. Le nombre de tickets Retail, de commandes B2C, de lignes de commandes, de mouvements de stock et les pics ne sont pas encore connus.

- Données économiques communiquées : Beaumanoir 2,2 Md€ de chiffre d'affaires, dont 10 % en Wholesale ; Boardriders 500 M€, dont 60 % en Wholesale. Le chiffre d'affaires indique l'importance économique des domaines, mais ne sert pas de multiplicateur de charge de développement.



## Périmètre fonctionnel de FLOW



**Référence de périmètre pour l'ordre de grandeur :** le domaine *Supply Chain Management* de la publication `2026-10-17.1` du projet [Beaumanoir Cartographie](<../../sources/client/cartographie-2026-10-17.1.yaml>). Ses capacités sont un modèle métier, pas une liste de modules à coder un pour un. FLOW reprend les responsabilités opérationnelles pertinentes de ce domaine. Les fonctions complémentaires de *Sourcing and Procurement* et *Commerce* requises pour sortir de Storeland ne sont pas encore identifiées : elles figurent provisoirement en **option de périmètre de 15 % de l'effort identifié**, hors nominal, sans prétendre qu'elles sont définies.



1. **Achats opérationnels :** commandes d'achat et leur suivi, engagements, modifications, annulations et événements de réception transmis par les partenaires concernés. La définition précise des achats couverts reste à faire.

2. **Ventes et retours :** enregistrement et suivi des commandes de vente des canaux concernés, modifications, annulations, retours et déstockage.

3. **Stock unifié :** consolidation du stock physique déclaré par les systèmes d'exécution, gestion de la protection du stock, des réservations et de la disponibilité utilisable par canal.

4. **Carnet de commandes :** allocation du stock, traitements de type AllocationRun et Backorder Processing, arbitrage entre demandes concurrentes et traçabilité des décisions.

5. **Promesse et optimisation :** ATP, CTP, PTP selon les définitions métier qui seront validées ; plan de fulfillment et optimisation des flux, avec contraintes de stock, lieu, date, coût et priorité.

6. **Documents opérationnels :** production des documents nécessaires aux flux, dont factures et bons de livraison, avec transmission aux systèmes financiers et aux partenaires. Le calcul comptable, le contrôle de gestion et le pilotage financier sont exclus.

7. **Exceptions et interventions humaines :** dossiers opérationnels, tâches, décisions, escalades et historique nécessaires aux cas qui ne suivent pas un traitement entièrement automatique.



## Hors périmètre et frontières



| Domaine hors FLOW | Responsabilité de FLOW à l'interface |

| --- | --- |

| Finance, contrôle de gestion, performance d'entreprise et conformité | Produire et transmettre les données et documents opérationnels convenus ; recevoir les retours nécessaires au suivi des commandes. Les obligations applicables à l'émission des documents restent à préciser. |

| Design, développement produit et planification stratégique | Consommer les références, variantes et plans approuvés nécessaires aux opérations. |

| WMS, TMS et exécution logistique délégués à des entreprises tierces | Envoyer les instructions et plans de fulfillment, recevoir les confirmations, mouvements et écarts ; réconcilier ces événements. |

| Gestion commerciale des clients, assortiments, prix, primes, promotions et soldes dans des outils dédiés | Recevoir les données ou décisions commerciales applicables et conserver la version effectivement utilisée pour chaque commande. |

| Expériences propres aux canaux Retail, EComm B2C et Wholesale | Exposer des contrats de commande, disponibilité, réservation et suivi communs, sans imposer une interface utilisateur unique à tous les canaux. |



## Exigence centrale : configurabilité maîtrisée



Le mini cahier des charges fourni par Laurent est conservé comme [source de configuration](<../../sources/Gestion de la configuration.pdf>). Il formalise les exigences métier retenues dans cette étude.



La configuration doit être un **composant transverse** de FLOW, au-delà de tables de paramètres : découpage organisationnel non figé, héritage et dérogations, résolution explicite des priorités lorsque plusieurs périmètres se croisent, objets de gouvernance (notamment plan commercial et saison), gestion des dépendances, versions, brouillons, validations, releases cohérentes, publication, activation datée et retour à une version antérieure. Les demandes en cours doivent conserver un comportement défini lors d'un changement de version. Les droits de consultation, modification, validation, publication et activation dépendent du périmètre et du rôle.



La décision doit combiner le contexte d'une **demande longue** (état, engagements, échéances et historique), l'état présent et futur de la supply chain et les politiques applicables. La sélection d'une règle ne peut donc pas se réduire à la lecture d'une ligne de table selon la marque.



Chaque décision importante doit garder sa **provenance** : faits et contexte pris en compte, version des politiques appliquées, origine organisationnelle, héritages, dérogations, arbitrages humains et motif. Une décision passée doit rester explicable après changement de configuration. L'historique des changements est lié aux décisions produites. La structure explicite vise aussi à faciliter des usages futurs de l'IA sous les mêmes habilitations ; elle ne présume pas la construction d'un agent IA dans FLOW.



Les règles courantes doivent pouvoir varier par **marque, enseigne, pays, entité juridique, canal, ligne produit, saison, partenaire et période de validité**, selon les besoins effectivement observés. L'héritage et la priorité entre ces niveaux doivent être explicites : une règle commune peut être spécialisée pour une marque ou un pays sans duplication intégrale. Les conflits entre règles doivent être détectés avant publication.



Une modification autorisée d'une règle doit pouvoir suivre ce cycle : rédaction, simulation sur des cas représentatifs, comparaison avec la règle active, approbation, date d'entrée en vigueur, publication, suivi et retour arrière. Toute décision opérationnelle doit conserver l'identifiant et la version de la règle appliquée, ses données d'entrée utiles et son résultat. Les habilitations doivent distinguer auteur, approbateur et opérateur.



**Critère de réussite à éprouver :** des utilisateurs habilités ajoutent une variante d'allocation ou de protection de stock pour une marque et une ligne produit, la testent, la publient et la retirent sans recompilation ni déploiement du cœur applicatif. Le temps, le coût et les compétences nécessaires à cette opération doivent être mesurés. Une interface de paramétrage est nécessaire si la cible d'autonomie des métiers l'exige ; un simple fichier de configuration manipulé par les développeurs ne suffit pas à démontrer cette autonomie.



Le paramétrage doit rester borné. Les invariants de stock, l'intégrité des réservations, les transitions irréversibles et les contrôles de sécurité relèvent du code et de tests automatisés. Une règle déclarative ne doit pas pouvoir invalider ces invariants.



## Architecture technique de référence à éprouver



- **Socle :** Java et Spring pour les services de gestion ; PostgreSQL comme hypothèse initiale pour les écritures transactionnelles. Découpage par domaines métier avec contrats d'API et événements explicites, plutôt qu'un découpage par marque.

- **Décisions et dossiers :** règles simples et tables de décision dans un mécanisme versionné ; DMN pour les décisions adaptées à ce format ; Flowable BPMN/CMMN pour les dossiers et parcours humains qui le justifient. Comparer la charge complète de Flowable open source à celle d'un développement ciblé avec ou sans moteur de workflow.

- **Optimisation :** Timefold Solver ou Google OR-Tools à comparer sur des jeux de commandes réels. Le solveur propose une allocation ; FLOW valide et enregistre la décision au regard des règles et de l'état du stock.

- **Availability :** journal durable et contrôles transactionnels pour les mouvements et réservations ; projection de lecture éventuellement en mémoire pour les consultations rapides. Une base colonnaire peut servir l'analyse, mais son rôle dans la promesse transactionnelle n'est pas présumé.

- **Intégration :** interfaces résilientes, événements horodatés, identifiants de corrélation, traitements idempotents et mécanismes de reprise avec les systèmes de canal, de commerce, de logistique et de finance.



**Familles d'interfaces cibles explicitées pour l'estimation :** (1) PLM et outils Commerce pour produit, article et prix ; (2) contrôle de gestion pour le *credit check* ; (3) SAP FI/CO pour les structures juridiques des entreprises et partenaires ; (4) prestataires logistiques via les API de commandes de fulfillment et leurs retours d'exécution. Les contrats de commande, disponibilité et suivi avec les canaux Retail, EComm B2C et Wholesale sont également requis par l'architecture omnicanale décrite plus haut. Le nombre réel de connecteurs et de flux par famille n'est pas encore établi. FLOW consomme le résultat du contrôle de crédit et les références maîtres ; il ne prend pas la responsabilité de leur calcul ou de leur maintenance amont.



Ces composants sont des hypothèses de conception, pas des produits déjà sélectionnés. Leur coût d'intégration, d'exploitation, de montée de version et de maintien en compétence entre dans l'estimation Make.



## Critères d'acceptation structurants



1. Une même pièce ne peut pas être promise deux fois lorsque deux canaux réservent simultanément le même stock.

2. Une disponibilité publiée est traçable jusqu'aux mouvements physiques, engagements et protections qui l'ont produite ; les retards de synchronisation sont visibles.

3. Une décision d'allocation peut être expliquée et rejouée avec les versions de règles et les données pertinentes.

4. Les spécificités de marque, pays et partenaire sont configurables dans les limites définies, sans branche de code par marque.

5. Les erreurs d'un partenaire logistique ou d'un système de canal peuvent être rejouées et réconciliées sans créer de doublon de commande ou de mouvement.

6. Les documents opérationnels reprennent les données et règles en vigueur pour la transaction concernée et sont transmis aux destinataires définis.

7. Les performances sont validées sur les pics observés, y compris les périodes de soldes et les vagues d'allocation Wholesale.



## Points à arbitrer pour figer le périmètre



- Définitions métier exactes de CTP et PTP, puis objectifs de service associés.

- Fonctions précises de NewStore, Socloz, Storeland, SAP ECC AFS et UR à reprendre dans FLOW ou dans un système de canal.

- Système maître de chaque donnée : article, prix, client, stock physique, réservation, commande et facture.

- Nombre de marques réellement distinctes en règles et niveaux d'héritage nécessaires.

- Frontière entre facture opérationnelle produite par FLOW et traitements financiers ou réglementaires réalisés ailleurs.

