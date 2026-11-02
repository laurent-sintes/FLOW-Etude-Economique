# Revue du périmètre estimé à partir des scénarios FLOW

**Les 88 capacités sont présentes dans les neuf lots métier. Le risque principal est leur profondeur fonctionnelle, pas l’oubli d’un intitulé.** Les deux lots supplémentaires portent les ateliers visuels et les fonctions IT du produit. Le total adopté reste à **5 950 JH**. Aucun supplément global n’est calculé par cet audit.

La lecture porte sur les **88 capacités, 74 comportements, 43 scénarios et 50 parcours** du backlog courant Beaumanoir Cartographie. Les noms, définitions, périmètres, exemples et descriptions pédagogiques des capacités ne diffèrent pas de la capture du 24 octobre utilisée pour l’étude. Les scénarios ne figuraient pas dans cette capture. Ils servent ici à éprouver les fonctions et hypothèses de taille. Leurs statuts de revue sont conservés dans la preuve.

## Ce qui doit être repris en priorité

Le correctif des politiques est une omission déjà établie. Six sujets demandent en priorité un examen de leur profondeur : consommation des enveloppes de groupe, arbitrage collectif du carnet, promesse à capacité finie, optimisation multi-échelon, chargements/tournées et engagements entre sociétés. Les migrations de parcours et les ateliers visuels demandent aussi une justification détaillée. Une fonction décrite dans un schéma est prévue, mais sa présence ne démontre ni l’adéquation de l’analogue ni la suffisance de la charge.

**Le correctif à 430 JH du lot politiques n’épuise pas la question.** Il conserve le comptage éligibilité/disposition et laisse à vérifier le financement de l’application des droits collectifs aux consommations. Il ne doit pas devenir le financement implicite de tous les sujets voisins.

## Lecture des onze lots

| Lot | JH adoptés | Points à examiner |
| --- | ---: | --- |
| Master Data Java/Spring | 1500 | R09, R14 |
| Stock Java/Spring | 340 | R02, R08, R09, R13, R14 |
| Propriété du stock Java/Spring | 190 | R08, R14 |
| Politiques, éligibilité et devenir des biens Java/Spring | 50 | R01, R02, R10 |
| Gestion des commandes Java/Spring | 170 | R07, R08, R10, R13 |
| Préparation et pilotage du Master Plan Java/Spring | 250 | R03, R07, R12 |
| Promesse, affectation et optimisation Supply Java/Spring | 530 | R02, R03, R04, R05, R06, R07, R12 |
| Prestations et reconnaissance des résultats Java/Spring | 420 | R06, R08, R09, R10, R13, R14 |
| Process Management avec studios, portail, formulaires et pilotage | 1960 | R08, R11, R13 |
| Ateliers visuels de planification et de décision | 160 | R12 |
| Administration, robustesse et services IT complémentaires | 380 | R11, R14 |

Les JH indiqués sont ceux des lots entiers. Les allocations de 63 JH au carnet, 39 JH à la promesse, 228 JH à l’optimisation et 85 JH à la planification de services ne sont pas des estimations indépendantes. Les recalculer exige de reprendre le lot cohérent de décisions et ses réutilisations.

## Écarts et contrôles par sujet

### R01 Gouvernance des politiques

**omission confirmee — priorité 1.** Les trois fonctions génériques de BC-008 ont été ramenées à un module d’activation et explication, fraction 0,5. L’audit des politiques a déjà établi le manque de configuration et de contrôle croisé.

**Périmètre à vérifier.** Stratégie, périmètres marque/canal/usage, paramètres, dérogations, incompatibilités et mise en vigueur contrôlée.

**Financement à préserver.** Le lot actif de 50 JH porte aussi éligibilité et devenir. La proposition à 430 JH remplace ce lot entier. Elle ne s’ajoute pas aux 50 JH.

**Travail demandé.** Conserver la proposition séparée et examiner ses frontières avec R02 et R05 avant adoption.

**Cas d’acceptation.** Deux protections incompatibles sont refusées ou soumises à une dérogation autorisée. Le changement ne modifie pas silencieusement les engagements existants.

Capacités : BC-008. Scénarios : Rééquilibrer et consolider des stocks sous protections (`redistribute-protected-stock`), Piloter le carnet de commandes au fil de la saison (`seasonal-order-backlog`).

### R02 Consommation des enveloppes de stock par groupe

**financement a localiser — priorité 1.** D02.b décrit les quantités allouées, consommées et restantes des groupes. Les fonctions Stock portent engagements individuels, consommation/libération et concurrence. Les preuves consultées ne désignent pas explicitement un compteur de droits collectifs.

**Périmètre à vérifier.** Hiérarchies et chevauchements de groupes, consommation atomique d’une enveloppe, restitution après annulation et contrôle du plafond. Une réservation individuelle ne démontre pas ce service.

**Financement à préserver.** Configuration dans R01. Recommandation dans optimisation. Réservation et protections transactionnelles dans Stock. L’activation proposée des politiques ne suffit pas à financer leur application à toutes les consommations.

**Travail demandé.** Rattacher ce service à un propriétaire unique puis rechercher les traitements déjà dimensionnés avant de compter un résiduel.

**Cas d’acceptation.** Deux commandes de canaux différents consomment le même stock sans dépasser leurs droits ni décompter deux fois une protection commune.

Capacités : BC-008, BC-011, BC-018, BC-037, BC-041, BC-046. Scénarios : Deux clients veulent le dernier pull (`last-item-concurrency`), Rééquilibrer et consolider des stocks sous protections (`redistribute-protected-stock`), Piloter le carnet de commandes au fil de la saison (`seasonal-order-backlog`).

### R03 Arbitrage collectif du carnet et stabilité des affectations

**analogie insuffisante — priorité 1.** La famille backlog comporte bien trois modules et des schémas DemandPriority, SupplyAssignment et DeliveryRelease. La révision a retenu une banque ERPNext de 118 unités, issue de disponibilité et quantités réservées, à 3 × 0,6.

**Périmètre à vérifier.** Arbitrer plusieurs carnets sur les mêmes ressources, conserver les liens protégés, revoir les autres, expliquer les perdants et respecter assortiment et contraintes de livraison.

**Financement à préserver.** Les fonctions existent dans les lots décisions et Master Plan. Les 63 JH attribués au backlog sont une allocation interne du lot de 530 JH, pas un budget indépendant à compléter forfaitairement.

**Travail demandé.** Recompter les décisions élémentaires et qualifier un analogue de réaffectation collective. Recalculer ensuite le lot cohérent en déduisant Stock et politiques.

**Cas d’acceptation.** Deux carnets de 80 partagent 100 pièces. Le calcul ne promet pas 160, préserve les engagements protégés et expose les 60 non couverts.

Capacités : BC-035, BC-036, BC-037, BC-038, BC-039, BC-045. Scénarios : D’une prévision à l’arbitrage d’une pénurie (`forecast-to-shortage-arbitration`), Piloter le carnet de commandes au fil de la saison (`seasonal-order-backlog`), Réagir à une pénurie sans confondre promesse et affectation (`shortage-reassessment`).

### R04 Promesse cohérente et faisabilité à capacité finie

**analogie insuffisante — priorité 1.** Les trois modules ATP, CTP et valorisation sont prévus. La banque ERPNext retenue de 145 unités concerne surtout disponibilité et engagements. Les schémas portent conditions, capacité et coûts inconnus, mais ne détaillent pas le problème de faisabilité.

**Périmètre à vérifier.** Promesse commune à plusieurs lignes, fraîcheur jusqu’à confirmation, capacités finies et calendriers, matières, minimums et conditionnements, approvisionnement offshore/nearshore et résultat sans solution.

**Financement à préserver.** Les 39 JH attribués à promising font partie des 530 JH. Stock fournit les positions. Service planning fournit les capacités. PTP consomme les prix autorisés sans construire un moteur de pricing.

**Travail demandé.** Séparer les exigences On-Hand/Projected ATP, Supply-Based/Capacity-Constrained CTP et PTP. Vérifier chaque fonction contre un analogue pertinent avant réévaluation.

**Cas d’acceptation.** Les vestes disponibles vendredi et pantalons lundi ne donnent pas une commande complète vendredi. Un apport non confirmé reste conditionnel. Aucune option admissible produit un résultat motivé, sans promesse fictive.

Capacités : BC-046, BC-047, BC-048, BC-049. Scénarios : Approvisionner une vente et traiter une confirmation fournisseur partielle (`additional-purchase-partial`), Promettre une commande complète à plusieurs lignes (`complete-order-multiline`), Expliquer l’absence de promesse admissible (`no-admissible-promise`), Précommander avant disponibilité et préparer la réalisation (`preorder-future-availability`), Comparer une substitution, un autre site et un transport express (`substitution-price-service`).

### R05 Optimisation multi-échelon et recommandations de règles

**analogie insuffisante — priorité 1.** Cinq modules sont financés à 0,75 composant chacun. BC-040 porte explicitement Store, Distribution Center et Multi-Echelon Optimization. Les analogues de règles et MRP ne démontrent pas le modèle conjoint service/stock/risque.

**Périmètre à vérifier.** Objectifs par échelon, dépendances entre sites, protection logique entre bénéficiaires, choix des conditions de réservation selon jalon, horizon, service et risque. Le calcul recommandé ne se réduit pas à saisir des seuils.

**Financement à préserver.** 228 JH sont attribués à l’ensemble des cinq familles de décision dans le lot de 530 JH. Le solveur réutilisé ne fournit pas automatiquement les modèles métier. Paramétrage et activation des règles restent dans R01.

**Travail demandé.** Définir les modèles réellement attendus, entrées, contraintes et sorties. Mesurer formulation et adaptation, sans refaire le solveur ni financer deux fois les règles actives.

**Cas d’acceptation.** Comparer deux cibles locales à une cible réseau et expliquer les effets de dépendance. Un changement recommandé de réservation ne libère pas les engagements existants.

Capacités : BC-040, BC-041, BC-042, BC-043, BC-044. Scénarios : Préparer une capsule pour l’ouverture de magasins (`fashion-launch`), Rééquilibrer et consolider des stocks sous protections (`redistribute-protected-stock`), Réagir à une pénurie sans confondre promesse et affectation (`shortage-reassessment`).

### R06 Chargements et tournées sous contraintes

**analogie insuffisante — priorité 1.** La famille service-planning emploie trois modules à 0,65 et une banque Odoo de calendriers de ressources de 305 unités. TransportPlan a arrêts, fenêtres et capacité. La présence de ces champs ne mesure pas la construction du calcul.

**Périmètre à vérifier.** Consolidation des chargements, compatibilités, arrêts, temps de trajet, créneaux et recalcul local. Un calendrier ne constitue ni un modèle de chargement ni une tournée réalisable.

**Financement à préserver.** 85 JH sont attribués à service-planning dans les 530 JH. Transport orders finance demandes et engagements. La libération groupée reste distincte du plan. Le mandat du TMS/exécutant ne doit pas être reconstruit dans FLOW.

**Travail demandé.** Préciser ce qui est calculé par FLOW et ce qui est retourné par un exécutant. Chiffrer les seuls modèles, appels et contrôles de résultat propres au mandat FLOW.

**Cas d’acceptation.** Douze palettes pour six magasins donnent deux chargements et des horaires admissibles. Une correspondance manquée déclenche une adaptation qui préserve la promesse ou un réexamen explicite.

Capacités : BC-049, BC-050, BC-051, BC-052, BC-055, BC-071, BC-072. Scénarios : Libérer une préparation B2B à l’approche de sa limite d’attente (`b2b-release-deadline`), Planifier deux chargements pour six magasins (`transport-loads-six-stores`), Sauver une livraison après une correspondance manquée (`transport-missed-connection`).

### R07 Plans et passage du planifié au ferme

**couverture a eprouver — priorité 2.** Qualification, consommation de prévision, projection, rapprochement et scénarios sont explicitement financés par sept modules du lot Master Plan de 250 JH. DemandPlan contient residualDemand. Leur présence interdit de les déclarer tous absents.

**Périmètre à vérifier.** Maille et fenêtre de consommation, filiation d’un achat planifié regroupé en achats fermes, remplacement sans double apport, versions des faits et recalcul après correction. La réduction de la banque plan-preparation de 679 à 274 unités n’éprouve pas ces cas.

**Financement à préserver.** Prévision statistique source hors Core. Calculs internes et ingestion externe distincts. Les appels aux calculateurs spécialisés ne doivent pas être recomptés ici.

**Travail demandé.** Déplier les mouvements des processus COSMIC et les traitements des sept modules sur les scénarios. Recompter seulement les fonctions distinctes qui n’y sont pas déjà représentées.

**Cas d’acceptation.** Prévision 100 et commandes 60 donnent 40 résiduelles selon la règle. L’affermissement remplace le même apport planifié. Une correction de stock relance le calcul sans se transformer en ingestion de plan externe.

Capacités : BC-021, BC-028, BC-029, BC-030, BC-031, BC-032, BC-033, BC-034, BC-035, BC-039, BC-045, BC-046. Scénarios : D’une prévision à l’arbitrage d’une pénurie (`forecast-to-shortage-arbitration`), Réviser un plan à partir de faits corrigés (`planning-actuals-feedback`), Précommander avant disponibilité et préparer la réalisation (`preorder-future-availability`), Réexaminer une préparation après correction des données sources (`reference-plan-correction`).

### R08 Engagements entre sociétés et variantes de commandes

**couverture a eprouver — priorité 1.** Les fonctions Orders et trois modules supplémentaires couvrent consignation, résolution des retours et rapprochement. Le comportement Intercompany Sales est natif. Les schémas complémentaires ne décrivent pas explicitement les liens de lignes et réponses réciproques entre sociétés.

**Périmètre à vérifier.** Engagements vente/achat distincts, refus et réponses partielles, changements synchronisés, prix de cession reçu, livraison directe sans fausse réception, avoirs réciproques et dossiers ouverts après livraison.

**Financement à préserver.** Orders 170 JH, propriété 190 JH, facturation/encaissement dans service-fulfilment et dossiers dans Process Management. Ni une relation de référence ni un moteur de workflow ne finance à elle seule ces règles métier.

**Travail demandé.** Attribuer chaque transition et contrôle de cohérence à son lot existant, puis identifier les compléments génériques réels. Conserver les interfaces propres aux SI du Groupe en intégration.

**Cas d’acceptation.** A vend au client et achète à B. Une livraison B–client ne crée pas de réception chez A. Un retour de six pièces ne prouve ni six crédits ni un remboursement.

Capacités : BC-014, BC-015, BC-016, BC-020, BC-021, BC-022, BC-023, BC-024, BC-025, BC-026, BC-027, BC-074, BC-075, BC-079, BC-085. Scénarios : Livrer un client avec le stock d’une autre société du groupe (`intercompany-direct-delivery`), Retourner une partie des biens livrés par une autre société du groupe (`intercompany-partial-return`), Approvisionner le [stock](glossary:TER005) d’une autre société du groupe (`intercompany-stock-transfer`), Scinder, regrouper ou fusionner sans perdre les engagements (`order-structuring-engaged`), Suivre trois issues contractuelles d’un retour fournisseur (`supplier-return-outcomes`).

### R09 Unités logistiques et filiation des biens

**couverture a eprouver — priorité 2.** La filiation des biens est explicite dans BC-009 et Stock. Les douze contrats de prestation partagent neuf champs génériques dont requirementsRef et resultContractRef. Cette structure ne décrit pas encore le contenu des unités logistiques et ses corrections.

**Périmètre à vérifier.** Contenus annoncés versus constatés, assemblage/décomposition, composants non interchangeables, recherche amont/aval et rupture de lien. Une spécification de carton n’est pas son contenu réel.

**Financement à préserver.** Références de conditionnement dans Master Data, faits/filiation dans Stock, demandes dans Service Orders et rapprochement dans assurance. Pas de moteur WMS ni de gestes atelier à ajouter au Core.

**Travail demandé.** Vérifier schémas et traitements Stock contre ces parcours et détailler les contrats de résultat typés. Ne compter que les adaptations absentes après cette réconciliation.

**Cas d’acceptation.** 120 demandées, 120 annoncées et 118 reçues restent trois faits distincts. Un accessoire A17 permet de retrouver les coffrets et destinations concernés, avec les limites de connaissance.

Capacités : BC-005, BC-009, BC-010, BC-011, BC-056, BC-057, BC-060, BC-063, BC-067, BC-069. Scénarios : Composer des coffrets personnalisés puis traiter les reliquats (`gift-kits-crossdock`), Distinguer la consigne de conditionnement, l’annonce et la réception (`packaging-receipt-variance`), Retrouver les coffrets contenant un accessoire défectueux (`trace-accessory-kits`).

### R10 Devenir des biens et récupération de valeur

**couverture a eprouver — priorité 2.** DispositionCase, DispositionOption et DispositionDecision représentent bien les usages, coûts, valeur et conditions. L’analogue Axelor est issu du contrôle qualité. L’allocation de 21 JH n’est pas une estimation indépendante.

**Périmètre à vérifier.** Comparaison coût/délai/risque des devenirs autorisés, décision partielle, application du blocage et suivi des preuves. Contrôler une qualité ne démontre pas la comparaison économique des devenirs.

**Financement à préserver.** Les 430 JH proposés conservent les 47 CFP éligibilité/disposition. Ils ne réévaluent donc pas la profondeur de BC-019. Les prestations de réparation et rebut sont financées ailleurs.

**Travail demandé.** Revoir les deux comportements Policy-based Disposition et Value Recovery Optimization séparément. Ne pas intégrer une nouvelle marge de disposition dans le seul correctif de politique.

**Cas d’acceptation.** 80 vestes sont libérables et 20 bloquées. Réparation et rebut sont comparés. La preuve de destruction de 18 laisse deux biens bloqués et un attendu ouvert.

Capacités : BC-019, BC-025, BC-026, BC-068, BC-070. Scénarios : Traiter des vestes abîmées sans retour client (`damaged-stock-disposition`), Remettre en vente une robe retournée (`return-fashion-recovery`), Retrouver les coffrets contenant un accessoire défectueux (`trace-accessory-kits`).

### R11 Parcours engagés et interventions sans double effet

**couverture a eprouver — priorité 1.** Le lot Process Management de 1 960 JH finance studio, formulaires, supervision et analyse. Les essais techniques et fonctions génériques de version/reprise ne démontrent pas la migration métier de dossiers engagés.

**Périmètre à vérifier.** Version applicable par dossier, autorisation de migration, activités déjà réalisées, signaux tardifs, intervention dans le mandat, preuve de son effet et corrélation des exceptions touchant plusieurs parcours.

**Financement à préserver.** Temporal et composants réutilisés portent leurs mécanismes. Les transitions et engagements restent aux lots métier. Journal technique et registres métier ne se substituent pas. Pas de second moteur de processus à ajouter.

**Travail demandé.** Faire porter les critères de migration et de reprise sur les composants déjà financés. Recompter les seuls services de validation ou d’adaptation distincts, et conserver l’écart COSMIC/COCOMO visible.

**Cas d’acceptation.** Changer une définition ne rejoue pas un paiement déjà réalisé. Une reprise acceptée techniquement ne clôt pas le dossier sans effet reconnu. Une absence de réponse ne vaut pas accord financier.

Capacités : BC-076, BC-077, BC-078, BC-079, BC-080, BC-081, BC-082, BC-083, BC-084, BC-085, BC-086, BC-087, BC-088. Scénarios : Contrôler le crédit avant d’avancer dans une vente (`customer-credit-hold`), Comprendre et réduire une attente de validation (`process-approval-bottleneck`), Attendre un encaissement malgré des notifications ambiguës (`remote-payment-ambiguous`), Changer une définition de parcours avec des commandes en cours (`workflow-version-change`).

### R12 Ateliers visuels métier

**controle cosmic incomplet — priorité 1.** 160 JH financent trois compositions visuelles à 0,8 analogue Axelor chacune. Le contrôle COSMIC ne compte que cinq CFP nouveaux pour enregistrer une vue et ses filtres.

**Périmètre à vérifier.** Interactions multi-lignes, comparaison des scénarios, effets sur les autres commandes, visualisation des conflits et des chargements, autorisation puis confirmation du résultat.

**Financement à préserver.** Les services de calcul et de décision appartiennent à leurs lots. Réutiliser ces fonctions ne rend pas gratuite leur interface. Les ateliers ne sont pas une 89e capacité native.

**Travail demandé.** Décrire les trois parcours utilisateurs, leurs états et interactions puis dimensionner la composition visuelle et son raccordement. Éviter un nouveau comptage des moteurs déjà financés.

**Cas d’acceptation.** Un utilisateur compare deux réaffectations, voit les demandes perdantes, fait autoriser un choix et distingue la demande d’application de son effet reconnu.

Capacités : BC-028, BC-029, BC-030, BC-031, BC-032, BC-033, BC-034, BC-035, BC-036, BC-037, BC-038, BC-039, BC-040, BC-041, BC-042, BC-043, BC-044, BC-045, BC-046, BC-047, BC-048, BC-049, BC-050, BC-051, BC-052, BC-053, BC-054, BC-055. Scénarios : D’une prévision à l’arbitrage d’une pénurie (`forecast-to-shortage-arbitration`), Piloter le carnet de commandes au fil de la saison (`seasonal-order-backlog`), Planifier deux chargements pour six magasins (`transport-loads-six-stores`).

### R13 Services financiers et frontières des systèmes externes

**frontiere a confirmer — priorité 2.** Demandes et reconnaissance des factures, avoirs, paiements et remboursements sont explicitement financées. PaymentRecognition contient remaining et correctionOf. Billing ne se réduit pas à transmettre un message.

**Périmètre à vérifier.** Dédoublonnage des résultats, contradiction, remboursement partiel et suites d’échec doivent être éprouvés. Les services externes de crédit, fiscalité, banque et comptabilité restent à attribuer aux réalisations concernées.

**Financement à préserver.** La construction des contrats génériques est Core. Connecteurs et règles propres au Groupe sont intégration. Le prix d’un service externe ne peut pas être réputé inclus dans les JH ni ajouté sans examen des contrats.

**Travail demandé.** Raccorder les cas aux traitements déjà financés et identifier les dépendances externes et leurs coûts/inclusions. Ne pas ajouter un moteur comptable, fiscal, bancaire ou de crédit complet au Core.

**Cas d’acceptation.** Un avoir de 80 et un remboursement de 50 laissent 30 à traiter. Deux notifications du même 600 ne font pas 1 200. Un paiement reçu ne lève pas seul un blocage de crédit.

Capacités : BC-016, BC-020, BC-025, BC-056, BC-057, BC-074, BC-075, BC-079, BC-084. Scénarios : Contrôler le crédit avant d’avancer dans une vente (`customer-credit-hold`), Exporter des vêtements et attendre la fin des prestations distantes (`export-remote-services`), Attendre un encaissement malgré des notifications ambiguës (`remote-payment-ambiguous`), Suivre un avoir puis un remboursement partiel (`return-credit-refund`), Remplacer un produit sans confondre retour et nouvelle livraison (`return-customer-replacement`).

### R14 Spécialisation Fashion et garanties communes

**couverture a eprouver — priorité 2.** Master Data 1 500 JH, Stock 340 JH, propriété 190 JH et IT professionnel 380 JH financent déjà contrats, références, registres et mécanismes communs. Variantes et assortiments sont explicites dans BC-004.

**Périmètre à vérifier.** Règles sectorielles, grilles et assortiments, périodes de saison et conditionnements doivent être rapprochés des traitements réellement prévus. Volumes, délai de calcul, fraîcheur, concurrence et reprise doivent être fixés pour les mêmes scénarios.

**Financement à préserver.** Définition produit, assortiment commercial et prix restent aux domaines sources. Pas de PIM/PLM ni de pricing à construire par déduction. L’Office FLOW ne finance pas les fonctions logicielles manquantes.

**Travail demandé.** Croiser les cas avec les écarts G01–G09 existants et les hypothèses de service. Déduire les fonctions et moyens déjà financés avant tout résiduel sectoriel ou technique.

**Cas d’acceptation.** La capsule consomme un assortiment autorisé et une version produit identifiée. Le dernier pull ne peut être réservé deux fois. Les volumes cibles n’altèrent pas les engagements ou preuves de reprise.

Capacités : BC-002, BC-003, BC-004, BC-005, BC-006, BC-007, BC-009, BC-010, BC-011, BC-012, BC-013, BC-014, BC-015, BC-017, BC-018, BC-056, BC-057, BC-058. Scénarios : Préparer une capsule pour l’ouverture de magasins (`fashion-launch`), Deux clients veulent le dernier pull (`last-item-concurrency`), Distinguer la consigne de conditionnement, l’annonce et la réception (`packaging-receipt-variance`), Transmettre un défaut récurrent au responsable produit (`product-quality-feedback`), Réexaminer une préparation après correction des données sources (`reference-plan-correction`).

## Ce qui ne constitue pas un nouveau manque

- Consommation de prévision, plan de demande, plan d’approvisionnement et rapprochement sont explicitement prévus dans Master Plan. Les scénarios doivent éprouver leurs règles et leur taille.
- Avoir, remboursement partiel, remplacement et retours fournisseur ont des fonctions et schémas prévus. Leur suivi et leurs résultats doivent être réconciliés entre commandes, prestations et dossiers.
- Les douze contrats de prestation ne sont pas douze moteurs WMS ou ateliers de production. Le Core porte les demandes, engagements, faits et résultats. L’exécutant conserve ses opérations.
- Références produit, variantes et assortiments sont prévues. La conception produit, la décision d’assortiment commercial et la fixation des prix restent dans leurs domaines sources.
- L’Office FLOW finance l’équipe transverse. Il ne remplace pas les fonctions du produit et ne doit pas être ajouté au titre de ces écarts logiciels.

## Contrôle de chaque capacité

Le tableau établit le rattachement, les cas explicitement reliés et les sujets de revue. Une absence de scénario explicite ne signifie ni absence de besoin ni charge nulle. Une contribution à un référentiel est conservée comme telle et n’est pas transformée artificiellement en contribution d’une capacité. Les liens de dépendance ne prouvent pas un financement.

| Capacité | Lot | Scénarios explicites | Points de revue |
| --- | --- | ---: | --- |
| BC-001 Service Provider Eligibility Control | supply-controls | 0 | Aucun écart identifié dans cette passe |
| BC-002 Reference Ingestion | master-data | 4 | R14 |
| BC-003 Partner & Agreement Reference Stewardship | master-data | 0 | R14 |
| BC-004 Merchandise Reference Stewardship | master-data | 0 | R14 |
| BC-005 Packaging Reference Stewardship | master-data | 0 | R09, R14 |
| BC-006 Internal Supplies Reference Stewardship | master-data | 0 | R14 |
| BC-007 Service Reference Stewardship | master-data | 0 | R14 |
| BC-008 Demand Fulfilment Policy Management | supply-controls | 1 | R01, R02 |
| BC-009 Inventory Tracking | stock | 11 | R09, R14 |
| BC-010 Inventory Ledger | stock | 13 | R09, R14 |
| BC-011 Inventory Visibility | stock | 16 | R02, R09, R14 |
| BC-012 Planning Data Provision | stock | 1 | R14 |
| BC-013 Stocktaking | stock | 1 | R14 |
| BC-014 Inventory Ownership Transfer Decision | inventory-ownership | 5 | R08, R14 |
| BC-015 Inventory Ownership Ledger | inventory-ownership | 5 | R08, R14 |
| BC-016 Accounting Data Provision | stock | 3 | R08, R13 |
| BC-017 Product Feedback | stock | 1 | R14 |
| BC-018 Reservation | stock | 5 | R02, R14 |
| BC-019 Inventory Disposition Decision | supply-controls | 4 | R10 |
| BC-020 Sales Order | orders | 22 | R08, R13 |
| BC-021 Purchase Order | orders | 10 | R07, R08 |
| BC-022 Transfer Order | orders | 5 | R08 |
| BC-023 Consignment Fill-up Order | orders | 2 | R08 |
| BC-024 Consignment Pick-up Order | orders | 1 | R08 |
| BC-025 Return Order | orders | 5 | R08, R10, R13 |
| BC-026 Supplier Return Order | orders | 2 | R08, R10 |
| BC-027 Order Structuring | orders | 5 | R08 |
| BC-028 Plan Ingestion | master-plan | 3 | R07, R12 |
| BC-029 Demand Forecast Qualification | master-plan | 1 | R07, R12 |
| BC-030 Demand Plan Development | master-plan | 1 | R07, R12 |
| BC-031 Demand Plan Visibility | master-plan | 3 | R07, R12 |
| BC-032 Supply Plan Development | master-plan | 2 | R07, R12 |
| BC-033 Supply Plan Visibility | master-plan | 2 | R07, R12 |
| BC-034 Planning Scenario Reconciliation | master-plan | 1 | R07, R12 |
| BC-035 Master Planning | master-plan | 8 | R03, R07, R12 |
| BC-036 Demand Prioritization | supply-decisions | 4 | R03, R12 |
| BC-037 Supply Assignment | supply-decisions | 12 | R02, R03, R12 |
| BC-038 Delivery Release Decision | supply-decisions | 3 | R03, R12 |
| BC-039 Plan Application | master-plan | 10 | R03, R07, R12 |
| BC-040 Physical Stock Target Optimization | supply-decisions | 1 | R05, R12 |
| BC-041 Logical Stock Protection Optimization | supply-decisions | 2 | R02, R05, R12 |
| BC-042 Reservation Rule Optimization | supply-decisions | 2 | R05, R12 |
| BC-043 Replenishment | supply-decisions | 7 | R05, R12 |
| BC-044 Stock Redistribution | supply-decisions | 5 | R05, R12 |
| BC-045 Simulation & Analysis | master-plan | 3 | R03, R07, R12 |
| BC-046 Available-to-Promise (ATP) | supply-decisions | 18 | R02, R04, R07, R12 |
| BC-047 Capable-to-Promise (CTP) | supply-decisions | 6 | R04, R12 |
| BC-048 Profitable-to-Promise (PTP) | supply-decisions | 7 | R04, R12 |
| BC-049 Service Capacity Visibility | supply-decisions | 3 | R04, R06, R12 |
| BC-050 Service Requirements Decision | supply-decisions | 3 | R06, R12 |
| BC-051 Service Selection Decision | supply-decisions | 5 | R06, R12 |
| BC-052 Transport Plan Decision | supply-decisions | 2 | R06, R12 |
| BC-053 Fulfilment Coordination | supply-decisions | 23 | R12 |
| BC-054 Fulfilment Adaptation Decision | supply-decisions | 4 | R12 |
| BC-055 Service Order Release Decision | supply-decisions | 6 | R06, R12 |
| BC-056 Operations Tracking | service-fulfilment | 12 | R09, R13, R14 |
| BC-057 Service Reconciliation | service-fulfilment | 7 | R09, R13, R14 |
| BC-058 Operations Visibility | service-fulfilment | 2 | R14 |
| BC-059 Picking Order | service-fulfilment | 5 | Aucun écart identifié dans cette passe |
| BC-060 Packing Order | service-fulfilment | 6 | R09 |
| BC-061 Cross-Docking Order | service-fulfilment | 1 | Aucun écart identifié dans cette passe |
| BC-062 Labeling Order | service-fulfilment | 1 | Aucun écart identifié dans cette passe |
| BC-063 Kitting Order | service-fulfilment | 1 | R09 |
| BC-064 Garment Finishing Order | service-fulfilment | 1 | Aucun écart identifié dans cette passe |
| BC-065 Cleaning Order | service-fulfilment | 1 | Aucun écart identifié dans cette passe |
| BC-066 Repair & Alteration Order | service-fulfilment | 1 | Aucun écart identifié dans cette passe |
| BC-067 Personalization Order | service-fulfilment | 1 | R09 |
| BC-068 Inspection Order | service-fulfilment | 4 | R10 |
| BC-069 Receiving Order | service-fulfilment | 4 | R09 |
| BC-070 Scrapping Order | service-fulfilment | 1 | R10 |
| BC-071 Transport Order | service-fulfilment | 7 | R06 |
| BC-072 Transport Booking Order | service-fulfilment | 2 | R06 |
| BC-073 Customs Clearance Order | service-fulfilment | 2 | Aucun écart identifié dans cette passe |
| BC-074 Billing | service-fulfilment | 5 | R08, R13 |
| BC-075 Payment | service-fulfilment | 4 | R08, R13 |
| BC-076 Process Definition Management | process-management | 4 | R11 |
| BC-077 Process Planning | process-management | 6 | R11 |
| BC-078 Process Sentry | process-management | 8 | R11 |
| BC-079 Process Orchestration | process-management | 10 | R08, R11, R13 |
| BC-080 Human Task Management | process-management | 4 | R11 |
| BC-081 Work Assignment | process-management | 3 | R11 |
| BC-082 Work Deadline Management | process-management | 3 | R11 |
| BC-083 Process Intervention | process-management | 3 | R11 |
| BC-084 Process Exception Management | process-management | 1 | R11, R13 |
| BC-085 Process Ledger | process-management | 3 | R08, R11 |
| BC-086 Process, Tasks & Order Visibility | process-management | 7 | R11 |
| BC-087 Process Mining | process-management | 1 | R11 |
| BC-088 Operational Analysis & Reporting | process-management | 1 | R11 |

## Suite du chiffrage

Pour chaque sujet prioritaire, construire la liste des résultats et transactions métier nécessaires, désigner leur lot de financement et vérifier ce qui y est déjà compté. Déplier les processus COSMIC concernés avec leurs échanges de données, puis choisir ou mesurer des analogues couvrant réellement ces mêmes responsabilités. Réévaluer les unités cohérentes après déduction des mécanismes partagés. Cette passe n’applique ni majoration générale ni forfait par scénario.

Les interfaces et règles propres aux SI et aux sociétés Beaumanoir relèvent de l’intégration. Les services génériques, contrôles métier et outils de configuration du produit relèvent de sa construction. Un coût de produit Buy dépend de son inclusion contractuelle et ne se déduit pas de la charge Make.

## Preuves et reproduction

- [Matrice complète, périmètres, comportements et parcours](results.json).
- [Constats et critères de contrôle](findings.json).
- [Script de rapprochement et contrôles](scan.py).
- [Audit et proposition sur les politiques](../2026-11-02-audit-politiques-allocation/audit.md).

Rejouer avec le Python du projet et les dépendances YAML : `python audits/2026-11-02-revue-perimetre-scenarios/scan.py`. Le script lit le projet Cartographie sans le modifier et vérifie que les entrées économiques restent identiques. `--verify` contrôle la preuve enregistrée et ses empreintes sans écrire.

Le rapprochement automatique contrôle les identifiants, rattachements et totaux. Les constats de pertinence sont une analyse de périmètre, pas une certification de couverture ni une nouvelle mesure de productivité. Les quatre OSS ne sont pas rescannés intégralement dans cette passe : leurs preuves de calcul déjà archivées sont confrontées aux scénarios métier.
