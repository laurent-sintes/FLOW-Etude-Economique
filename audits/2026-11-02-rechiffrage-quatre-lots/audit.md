# Proposition de rechiffrage de quatre lots

**Proposition non adoptée. Les simulations conservent les 7 030 JH validés.**

## Résultats

| Lot | Retenu JH | Proposition JH | Variation JH | Proposition k€ HT |
|---|---:|---:|---:|---:|
| Master Data | 1500 | 1600 | +100 | 1007 |
| Process Management, studios et portail | 1960 | 2060 | +100 | 1297 |
| Ateliers visuels métier | 160 | 400 | +240 | 251 |
| Administration, robustesse et services IT | 380 | 540 | +160 | 344 |

En remplaçant ces quatre lots, le Core passerait à **7630 JH et 4808 k€ HT**, soit **+600 JH et +378 k€ HT**. Ce montant concerne la construction du produit, avant projection dans le temps.

## Nature du chiffrage

Hypothèses de charge projet par livrable. Analyse, conception, développement, QA, pilotage de l’équipe produit et mise en service inclus dans chaque montant. Aucun temps de réalisation observé ni mesure nouvelle de code. Ne remplace pas les calculs COCOMO/COSMIC actifs.

Cette passe apporte une décomposition explicite en livrables et une frontière de financement. Les valeurs en JH sont proposées par estimation d’ingénierie. Elles ne sont ni déduites de la taille des fichiers ni observées dans un projet comparable. Une liste détaillée ne valide pas à elle seule la productivité. Les anciennes voies COCOMO II et COSMIC restent exposées ci-dessous comme repères, avec leurs écarts de périmètre. Ce contre-chiffrage n’est pas une troisième formule exécutée par le modèle actif.

Les montants incluent les activités projet et le pilotage de l’équipe produit. Les QA de composants sont comprises dans chaque livrable. Les lignes de qualification croisée financent uniquement les interactions entre ces livrables. Aucun pilotage de programme ou Transformation Office n’est ajouté.

## Édition de redressement dans Master Data

L’édition fait partie du produit. La ligne MD09 finance des formulaires de correction pour les six familles, avec motif, validation, provenance et gestion des conflits avec les contributions suivantes. Une correction crée une version et conserve les états publiés. Les différences de priorité entre sources et corrections doivent être rendues explicites. Le retour éventuel de la correction au système source et les règles propres à chaque marque appartiennent à l’intégration.

Le montant Master Data ne résulte donc pas d’une suppression forfaitaire des fonctions d’édition. La consultation MD05, la correction MD09, le versionnement MD03 et le rejeu MD06 ont des livrables distincts.

## Comparaison avec les calculs existants

| Lot | COCOMO retenu avant arrondi JH | COSMIC actuel CFP | COSMIC actuel JH | Contre-chiffrage JH |
|---|---:|---:|---:|---:|
| Master Data | 1496.9 | 420 | 1200.0 | 1600 |
| Process Management, studios et portail | 1959.6 | 216 | 617.1 | 2060 |
| Ateliers visuels métier | 162.3 | 5 | 14.3 | 400 |
| Administration, robustesse et services IT | 381.3 | 68 | 194.3 | 540 |

Les 5 CFP des ateliers portent sur la sauvegarde d’une vue et ne dimensionnent pas les trois interfaces nouvelles. Les 216 CFP de Process Management et les 68 CFP IT ne représentent pas tout le travail graphique et technique retenu. Les 420 CFP Master Data ne sont pas recomptés dans cette passe. Il ne faut ni sommer ces voies ni augmenter artificiellement les CFP pour atteindre le contre-chiffrage.

Les références OSS et leurs quatre résultats sont conservés dans results.json avec les mesures et versions de la base figée. Aucun nouveau téléchargement ni rescan de dépôt distant n’a été réalisé pour cette passe.

## Master Data — 1600 JH

| Livrable | JH |
|---|---:|
| MD01 · Admission et diagnostic des contributions | 150 |
| MD02 · Six familles de références | 180 |
| MD03 · Versions, dépendances et publication | 250 |
| MD04 · Portées, validité et conflits de références | 180 |
| MD05 · Consultation et diagnostic de la référence | 160 |
| MD06 · Rejeu et rapprochement après correction | 140 |
| MD07 · Qualification des flux et des volumes | 170 |
| MD08 · Protection, audit, purge et restauration du noyau | 160 |
| MD09 · Édition de redressement autorisée | 210 |

**MD01 — Admission et diagnostic des contributions.** Admission, rejet motivé et suivi des contributions. Interface générique, sans connecteur spécifique de marque.
Réutilisation et frontière : Transport, identité et persistance standards disponibles.
Financement : `master-data-admission`. Cas : reference-plan-correction, product-quality-feedback.

**MD02 — Six familles de références.** Six adaptations de schémas et contrôles communs à 30 JH chacune.
Réutilisation et frontière : Même cadre pour partenaires, marchandises, conditionnements, fournitures, services et accords. Aucun PIM ou PLM complet.
Financement : `master-data-semantique`. Cas : fashion-launch, reference-plan-correction.

**MD03 — Versions, dépendances et publication.** Publication atomique, compatibilité des deux versions canoniques, identités et dépendances stables.
Réutilisation et frontière : Les corrections utilisent ce service sans reconstruire leur propre versionnement.
Financement : `master-data-versions`. Cas : reference-plan-correction, workflow-version-change.

**MD04 — Portées, validité et conflits de références.** Portées et validités des données reçues. Détection des conflits et provenance source ou correction locale.
Réutilisation et frontière : Saisons opérationnelles et droits de stock restent financés dans politiques. Pas de second moteur de politiques.
Financement : `master-data-semantique`. Cas : fashion-launch, seasonal-order-backlog.

**MD05 — Consultation et diagnostic de la référence.** Recherche, consultation à date, différences de versions et liens vers usages.
Réutilisation et frontière : Cadre CRUD, recherche et composants de présentation réutilisés. Les formulaires de correction sont MD09.
Financement : `master-data-common-domain`. Cas : reference-plan-correction, trace-accessory-kits.

**MD06 — Rejeu et rapprochement après correction.** Rejeu sémantique et réconciliation des consommateurs après correction ou restauration.
Réutilisation et frontière : Ne facture pas les écrans de correction MD09 ni les réactions métier des autres lots.
Financement : `master-data-reprise`. Cas : reference-plan-correction, product-quality-feedback.

**MD07 — Qualification des flux et des volumes.** Qualification transversale des transformations, rejets, reprise et lot de 100 000 lignes selon la cible S1 existante.
Réutilisation et frontière : Tests de composants inclus dans MD01 à MD06 et MD09. Ici uniquement parcours croisés et performances du service Master Data.
Financement : `master-data-service`. Cas : reference-plan-correction, last-item-concurrency.

**MD08 — Protection, audit, purge et restauration du noyau.** Contrôles des accès et usages protégés, journal sensible, purge et restauration propres au noyau Master Data.
Réutilisation et frontière : Les consoles transverses IT consomment ces services. Les noyaux identité, sauvegarde et bases de données ne sont pas développés.
Financement : `master-data-protection`. Cas : reference-plan-correction, product-quality-feedback.

**MD09 — Édition de redressement autorisée.** Éditer une donnée canonique erronée sur les six familles. Motif, aperçu de changement, droits, validation, nouvelle version, provenance et conflit avec une contribution source ultérieure. Une correction ne réécrit pas une ancienne version publiée.
Réutilisation et frontière : Réutilise versions MD03, portées MD04, audit MD08 et composants CRUD. Ne remplace ni conception produit, ni assortiment commercial, ni les systèmes sources. Les règles de priorité par marque restent dans l’intégration.
Financement : `master-data-admission`. Cas : reference-plan-correction, product-quality-feedback, fashion-launch.
## Process Management, studios et portail — 2060 JH

| Livrable | JH |
|---|---:|
| PM01 · Catalogue des actions et des contrats | 120 |
| PM02 · Éditeur graphique des processus | 300 |
| PM03 · Validation et prévisualisation | 180 |
| PM04 · Publication et retrait des versions | 180 |
| PM05 · Migration des dossiers engagés et interventions | 220 |
| PM06 · Studio et rendu des formulaires | 230 |
| PM07 · Portail des tâches et attribution | 170 |
| PM08 · Adaptation du runtime et corrélation | 190 |
| PM09 · Journal, supervision et projections | 140 |
| PM10 · Analyses et tableaux de bord | 180 |
| PM11 · Qualification des parcours croisés | 150 |

**PM01 — Catalogue des actions et des contrats.** Catalogue borné des actions, types d’événements et contrats utilisables par les studios.
Réutilisation et frontière : Les services métier restent dans leurs lots propriétaires.
Financement : `flow-process-definitions`. Cas : workflow-version-change, order-structuring-engaged.

**PM02 — Éditeur graphique des processus.** Graphe, propriétés, branchements, délais, sélection des actions et diagnostic dans le studio.
Réutilisation et frontière : Bibliothèque graphique fournie. Pas de nouveau moteur graphique ni langage de programmation libre.
Financement : `professional-process-studio`. Cas : workflow-version-change, process-approval-bottleneck.

**PM03 — Validation et prévisualisation.** Contrôles statiques, prévisualisation des parcours et diagnostics de contrat.
Réutilisation et frontière : Réutilise le catalogue PM01 et les schémas des actions. Aucun optimiseur métier.
Financement : `professional-process-studio`. Cas : workflow-version-change, service-policy-deactivation.

**PM04 — Publication et retrait des versions.** Publication, retrait, accès et association entre modèle et version exécutable.
Réutilisation et frontière : Identités et audit technique fournis. Les versions Master Data ne sont pas reconstruites.
Financement : `flow-process-definitions`. Cas : workflow-version-change.

**PM05 — Migration des dossiers engagés et interventions.** Préparer et appliquer une migration autorisée, bloquer les changements incompatibles et constater les effets des interventions.
Réutilisation et frontière : Temporal fournit la persistance et les reprises techniques. Pas de rejeu des paiements acquis.
Financement : `flow-process-intervention`. Cas : workflow-version-change, remote-payment-ambiguous.

**PM06 — Studio et rendu des formulaires.** Types de champs bornés, dispositions, validations de formulaire, versions et rendu.
Réutilisation et frontière : Composants de champs fournis. Les écritures métier passent par les services propriétaires.
Financement : `professional-human-forms`. Cas : process-approval-bottleneck, return-credit-refund.

**PM07 — Portail des tâches et attribution.** Files, contexte du dossier, affectation, échéances et résultat du travail humain.
Réutilisation et frontière : Réutilise PM06 et le contrat de tâche. Aucun recalcul de promesse ou d’allocation.
Financement : `flow-human-task`. Cas : process-approval-bottleneck, b2b-release-deadline.

**PM08 — Adaptation du runtime et corrélation.** Liaisons moteur, corrélation des événements, délais, pauses et résultats reconnus.
Réutilisation et frontière : Moteur et ordonnanceur fournis. Aucune nouvelle construction de Temporal.
Financement : `flow-process-runtime`. Cas : remote-payment-ambiguous, transport-missed-connection.

**PM09 — Journal, supervision et projections.** Journal métier à date, suivi d’exécution et rapprochement des événements tardifs.
Réutilisation et frontière : Infrastructure de logs et stockage fournis. Les projections Supply spécialisées restent aux services métier.
Financement : `flow-case-ledger`. Cas : remote-payment-ambiguous, workflow-version-change.

**PM10 — Analyses et tableaux de bord.** Modèle de traces FLOW, variantes, durées, conformité et tableaux de bord bornés.
Réutilisation et frontière : PM4JS et Superset disponibles. Pas d’outil universel de BI, ni de découverte généralisée ou apprentissage.
Financement : `professional-analytics-mining`. Cas : process-approval-bottleneck, workflow-version-change.

**PM11 — Qualification des parcours croisés.** Tester publication, migration, reprise et événements ambigus sur les parcours de bout en bout du moteur.
Réutilisation et frontière : Les tests de composants sont dans PM01 à PM10. Les recettes des interfaces Supply appartiennent aux ateliers.
Financement : `flow-process-exception`. Cas : workflow-version-change, remote-payment-ambiguous, process-approval-bottleneck.
## Ateliers visuels métier — 400 JH

| Livrable | JH |
|---|---:|
| WB01 · Cadre commun des trois ateliers | 60 |
| WB02 · Atelier carnet et Master Plan | 90 |
| WB03 · Atelier de comparaison des décisions | 100 |
| WB04 · Atelier prestations et transport | 80 |
| WB05 · Fraîcheur et modifications simultanées | 40 |
| WB06 · Qualification croisée des trois ateliers | 30 |

**WB01 — Cadre commun des trois ateliers.** Sélection de contexte, disposition, grilles, filtres, vues sauvegardées et navigation commune.
Réutilisation et frontière : Consomme les composants UI standards et les droits. Ce cadre est construit une fois.
Financement : `professional-supply-workbenches`. Cas : fashion-launch, reference-plan-correction.

**WB02 — Atelier carnet et Master Plan.** Voir carnets et plan, modifier les choix autorisés, lire les conflits et suivre la demande d’application.
Réutilisation et frontière : Moteur de planification, consommation des prévisions et calcul des écarts déjà financés.
Financement : `professional-supply-workbenches`. Cas : seasonal-order-backlog, forecast-to-shortage-arbitration, planning-actuals-feedback.

**WB03 — Atelier de comparaison des décisions.** Comparer les options, voir gagnants et perdants, expliquer les contraintes et demander l’application autorisée.
Réutilisation et frontière : Promesse, affectation, optimisation et autorisation métier restent dans décisions et politiques.
Financement : `professional-supply-workbenches`. Cas : shortage-reassessment, substitution-price-service, complete-order-multiline.

**WB04 — Atelier prestations et transport.** Présenter prestations, deux chargements pour six magasins, correspondances et exceptions.
Réutilisation et frontière : Les calculs de tournée, contrats de prestation et preuves de résultat ne sont pas redéveloppés.
Financement : `professional-supply-workbenches`. Cas : transport-loads-six-stores, transport-missed-connection, export-remote-services.

**WB05 — Fraîcheur et modifications simultanées.** Afficher un résultat obsolète, distinguer une demande de son effet et gérer un conflit de modification à l’écran.
Réutilisation et frontière : La cohérence transactionnelle et l’idempotence serveur sont financées dans les services métier.
Financement : `professional-supply-workbenches`. Cas : last-item-concurrency, reference-plan-correction.

**WB06 — Qualification croisée des trois ateliers.** Recette ergonomique et des enchaînements propres aux trois ateliers.
Réutilisation et frontière : Les tests de chaque écran sont compris dans WB01 à WB05. Aucun doublon des tests du moteur métier.
Financement : `professional-supply-workbenches`. Cas : transport-loads-six-stores, shortage-reassessment, fashion-launch.
## Administration, robustesse et services IT — 540 JH

| Livrable | JH |
|---|---:|
| IT01 · Administration des habilitations produit | 70 |
| IT02 · Configuration et publication du paramétrage | 80 |
| IT03 · Traitements et reprises transverses | 60 |
| IT04 · Audit, rétention et purge transverses | 80 |
| IT05 · Consoles des imports et exports | 70 |
| IT06 · Documents, notifications et langues | 50 |
| IT07 · Migrations et restauration du produit | 70 |
| IT08 · Diagnostic et qualification des garanties communes | 60 |

**IT01 — Administration des habilitations produit.** Consoles des habilitations contextualisées, contrôle de portée et diagnostic des refus.
Réutilisation et frontière : Identité, MFA, sessions et contrôles Master Data réutilisés.
Financement : `professional-admin-security`. Cas : reference-plan-correction, customer-credit-hold.

**IT02 — Configuration et publication du paramétrage.** Consoles des paramètres techniques produit, validation de leur cohérence et déploiement contrôlé.
Réutilisation et frontière : Les règles métier et studios sont dans leurs lots. Pas de nouveau moteur de politiques.
Financement : `professional-admin-security`. Cas : workflow-version-change, service-policy-deactivation.

**IT03 — Traitements et reprises transverses.** Console inter-lots des traitements, erreurs et demandes de reprise, avec accès aux preuves.
Réutilisation et frontière : Les mécanismes de reprise, les traitements et les garanties d’effet sont financés chez leurs propriétaires.
Financement : `professional-operations-lifecycle`. Cas : remote-payment-ambiguous, reference-plan-correction.

**IT04 — Audit, rétention et purge transverses.** Composition des demandes de purge, dépendances inter-lots et consultation des preuves d’audit.
Réutilisation et frontière : Consomme les services d’audit et purge du noyau Master Data. Ne reconstruit ni les services ni les règles de conservation métier.
Financement : `professional-operations-lifecycle`. Cas : product-quality-feedback, reference-plan-correction.

**IT05 — Consoles des imports et exports.** Déclenchement, suivi et diagnostic inter-lots des échanges génériques.
Réutilisation et frontière : Les noyaux d’import, transformations, admission et adaptateurs propres aux marques restent financés ailleurs.
Financement : `professional-data-services`. Cas : reference-plan-correction, partial-receiving.

**IT06 — Documents, notifications et langues.** Composition et administration des pièces, acheminements et langues du produit.
Réutilisation et frontière : Stockage, transport de messages et bibliothèques de traduction fournis. Les règles métier de notification ne sont pas redéveloppées.
Financement : `professional-data-services`. Cas : export-remote-services, process-approval-bottleneck.

**IT07 — Migrations et restauration du produit.** Enchaîner les opérations par lot et qualifier la restauration cohérente du produit.
Réutilisation et frontière : CI, sauvegarde, base et restauration du noyau Master Data déjà financées. Pas de seconde usine logicielle.
Financement : `professional-operations-lifecycle`. Cas : reference-plan-correction, workflow-version-change.

**IT08 — Diagnostic et qualification des garanties communes.** Raccorder les diagnostics et éprouver les parcours critiques selon les cibles S1 courantes.
Réutilisation et frontière : Ne finance ni exploitation annuelle, ni multi-région actif, ni campagnes de performance de chaque moteur.
Financement : `professional-operations-lifecycle`. Cas : last-item-concurrency, remote-payment-ambiguous.

## Conditions déterminantes

- Les six familles Master Data utilisent un cadre commun et une édition de redressement, pas six éditeurs autonomes.
- Le studio utilise un catalogue d’actions et de champs borné. Un langage libre ou un éditeur universel impose un autre dimensionnement.
- Les trois ateliers consomment les services métier financés. Aucun calcul de promesse, planification, optimisation ou transport supplémentaire.
- Les consoles IT orchestrent les mécanismes déjà financés. Identité, sauvegardes, plateforme et noyaux de reprise ne sont pas reconstruits.
- Le calendrier, le MCO et la durée du Transformation Office doivent être réexaminés séparément si cette proposition est adoptée. Aucun impact automatique de délai n’est déduit des JH.

Périmètre natif inchangé : 88 capacités. Les quatre lots sont étudiés. Aucun nouveau lot n’est adopté par ce document.

## Reproduction

Depuis la racine du dépôt : `python audits/2026-11-02-rechiffrage-quatre-lots/calculate.py` puis `python audits/2026-11-02-rechiffrage-quatre-lots/calculate.py --verify`. Les empreintes des sources, les contrôles et les répartitions de rôles sont dans results.json.

Les contrôles vérifient sommes, cas, propriétaires de financement, provenance et conservation du budget actif. Ils ne certifient pas les hypothèses de charge.
