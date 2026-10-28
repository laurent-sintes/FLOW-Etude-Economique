# Audit global de lecture sponsor — 25 octobre 2026

## Relecture du parcours après la refonte du menu

Le menu était organisé, mais plusieurs pages restituaient encore les mêmes blocs. La synthèse reproduisait la matrice non financière de Périmètre et le passage des offres aux budgets de Synvance. Architecture apparaissait trois fois ; tarifs et charges deux fois. Dans Estimations, les trois indicateurs Make répétaient immédiatement la ligne du tableau comparatif. Enfin, les liens de sortie proposaient plusieurs directions, sans suite de lecture privilégiée.

| Question du sponsor | Emplacement principal après correction |
| --- | --- |
| Dans quelles conditions choisir Make, SAP ou Microsoft ? | Synthèse : conditions de choix, valeur métier, dépenses et durée de service, décision suivante |
| Qu’est-ce qui distingue les options ? | Périmètre : couverture, matrice non financière détaillée, responsabilités, référentiel métier et architecture |
| Que proposent les fournisseurs et comment arrive-t-on au budget Buy ? | Synvance : six étapes avec pièces localisées et tableau de passage aux budgets |
| Les prix ont-ils des points de comparaison externes ? | Marché : projets publics, nature des prix et tarifs de prestation |
| Comment l’enveloppe FLOW est-elle construite ? | Estimations : budgets des cinq options, plage du build, intégration Make, détail annuel et charges par capacité |
| Que se passe-t-il si je change une hypothèse ? | Simulations : paramètres et projections aux quatre horizons |

Les blocs détaillés ont un seul point de lecture. Les liens contextuels conduisent directement à la section concernée et conservent la stack. Le tableau Socle / Intégration / Run & MCO de Périmètre décrit maintenant les responsabilités ; sa ventilation financière annuelle est dans Estimations. Les années de service et la différence de périmètre SAP restent rappelées près des écarts de dépenses : elles changent leur interprétation.

Le parcours Synvance ne répète plus en ouverture sa conclusion ni en dernière étape l’arbitrage général Make/Buy. Il explique les deux trajectoires Buy. Les comparaisons en texte qui répétaient les tableaux de prix ou les points du cadrage sont retirées de ces étapes. Marché ne répète plus l’ancre Make ni une nouvelle liste de travaux de cadrage.

Une transition explicite relie Synthèse → Périmètre → Synvance → Marché → Estimations → Simulations. Synvance possède des boutons étape précédente/suivante. Les anciens liens vers les charges de Périmètre et les achats techniques de Marché sont redirigés. Le retour depuis Simulations annonce que la synthèse utilise la référence et que la simulation reste conservée.

Les contenus, les transitions et les intitulés restent dans les YAML. La nouvelle répartition est inscrite dans AGENTS.md pour éviter de recréer les doublons. Aucun paramètre économique n’est modifié.

Contrôles réalisés : TypeScript, build Vite, absence de contenu métier codé dans React, 30 tests applicatifs et 11 tests de recherche/navigation/reprise. Relecture navigateur de la synthèse, des responsabilités, des six étapes Synvance, du marché, des quatre lectures d’Estimations et de la transition vers Simulations. Les cinq options, les quatre horizons, les paramètres, le passage des offres aux budgets Buy et le contrat de reprise sont exactement identiques dans les réponses API avant/après (`tmp/study-app/journey-before.json`, `journey-after.json`). La part des compléments Buy est conservée dans le tableau Synvance. Capture de contrôle : `tmp/study-app/journey-estimations.png`.

## Objet et décision éditoriale

L’application sert à estimer une enveloppe et à décider de l’opportunité de poursuivre FLOW. Le sponsor connaît la cartographie SCM et le stade de l’étude. Le cadrage détaillé vient après un Go. La présence d’hypothèses fortes est normale à ce stade ; elle ne doit pas devenir le sujet principal de chaque écran.

La demande ne consiste pas à supprimer les précautions. Elle demande de les transmettre avec parcimonie, au moment où elles aident à interpréter une dépense ou un choix. Une durée de service différente, une dépense exclue, un périmètre fournisseur différent ou une inclusion incertaine ont leur place près du résultat concerné. Une déclaration répétée « non validé / à confirmer / pas un devis » n’apporte rien de plus.

## Diagnostic global

La restitution avait hérité de la structure du travail de production : recalibration, validation, preuve attendue, limites de méthode et comparaisons avec les versions précédentes. Plusieurs règles du dépôt prescrivaient encore un tableau avant/après dans Estimations et l’affichage de réserves. Leur accumulation avait pris le pas sur la règle générale « lecteur sponsor ».

Cela produisait trois défauts : les résultats arrivaient après leur justification ; des hypothèses ordinaires semblaient être des anomalies ; la décision d’opportunité se transformait en demande de compléter un mandat de cadrage. L’exactitude des données n’exige pas cette présentation.

## Revue par espace et corrections appliquées

| Espace | Problème de lecture | Correction |
| --- | --- | --- |
| Accueil | Verdict conditionnel suivi de l’impossibilité de trancher, double rappel du stade de l’étude, empreinte technique très visible. | Positionnement explicite Make / Buy, statut d’enveloppe posé une fois, décision de poursuivre FLOW. Empreinte dans méthode et sources. |
| Comparaison hors coûts | Mélange d’apports, de responsabilités et de demandes de preuve ; badges « à démontrer » répétés. | Apports et contreparties concrets ; preuves et risques accessibles en approfondissement, sans badge systématique. |
| Lecture économique sponsor | Long avertissement avant les résultats ; répétition de l’absence de devis et de validation ; détail de construction Buy au même niveau que les totaux. | Totaux, horizon, années de service et reste à financer d’abord. Décomposition Buy et financement complémentaire dépliables. Différences de périmètre Microsoft/SAP gardées près de leurs écarts. |
| Valeur métier et suite | Neuf champs de bénéfices « à définir », critères d’arrêt et mandat incomplet dominants. | Leviers de valeur visibles ; indicateurs et moyens de cadrage en détail. Une section « Après le Go » accueille les livrables du cadrage. Aucun objectif chiffré inventé. |
| Estimations | « Effet de la recalibration », montants précédents et écarts ; avertissement général ; deux estimations d’intégration au même niveau. | Suppression du tableau historique. Comparaison actuelle build / intégration / Run & MCO des cinq options. Budget Make retenu au premier niveau ; chiffrage par activités dans l’explication du budget. |
| Estimations détaillées | Tarifs, productivité, charges de toutes les capacités et architecture allongent la page avant que la question budgétaire soit résolue. | Plage de build visible. Charges, tarifs et productivité regroupés dans un détail ; architecture accessible séparément. |
| Périmètres et responsabilités | Introduction tournée vers le travail à établir ; commentaire économique mentionnant encore l’audit et une recalibration à venir. | Description des capacités et du travail à réaliser. Lecture Make actualisée : capacités SCM et mécanismes partagés ; repère SAP excluant les mécanismes génériques déjà financés. |
| Référentiel métier | Statut général de validation, statut répété par capacité, correspondances historiques CSF présentées comme aide à la lecture actuelle. | Suppression des statuts génériques et de l’ancien parcours de calibration ; lien vers les charges actives. Frontières et qualifications propres à une capacité conservées. |
| Simulations | Bandeau sur la nouvelle grille, confirmation future et absence de budget d’engagement ; explication du proxy répétée dans le tableau et les paramètres. | Phrase de lecture sur les horizons et le service. Explication du lien SAP / Make au moment de modifier les paramètres. Erreurs de saisie et reprise de session conservées. |
| Sources | Carte d’historique avant recalibration, titres de production (« preuves de la recalibration »), descriptions centrées sur les réserves. | Carte historique retirée ; archive conservée. Titres et descriptions orientés sur offres, charges, hypothèses et documentation technique. |
| Références de marché | Conclusion utile noyée dans les interdictions de transposition, variance non calculable et protocole de future justification. | Conclusion et repères en premier. Contexte des projets conservé près des plages ; comparabilité statistique et formule en méthode. Actions de rapprochement raccourcies. |
| Glossaire | Définitions et synonymes historiques restent nombreux. | Pas de suppression de définitions pour raccourcir artificiellement le dictionnaire. Les améliorations d’organisation relèvent de l’audit navigation déjà établi. |
| FAQ et note Synvance | Anciennes erreurs de classement, libellés remplacés et avant/après expliqués comme si le lecteur suivait la fabrication du modèle. | Questions reformulées autour des dépenses actuelles ; décision d’opportunité avant cadrage ; renvois vers la grille active et correction de la description du repère Make. |

## Précautions conservées à leur point d’usage

- Les dépenses IT externes excluent équipes internes, transformation et décommissionnement : indiqué avec le tableau économique sponsor, financement complémentaire accessible en détail.
- Les horizons ont un départ commun et des années de service différentes : expliqué avec les totaux et les comparaisons ; le test de décalage conserve sa limite de coût du retard non valorisé.
- L’offre SAP conserve des travaux Finance et Microsoft extrapole au-delà d’un pilote : indiqué près des comparaisons correspondantes.
- Les compléments Buy doivent être retirés s’ils sont déjà financés : indiqué dans leur décomposition, sans prétendre qu’une absence de preuve est une absence de fonction.
- L’intégration Make utilise un repère SAP retraité : expliqué dans le détail de l’estimation et dans les paramètres qui font évoluer ce repère.
- Les références de marché couvrent des périmètres différents de FLOW ; les composites Forrester sont des modèles d’entreprise : indiqué auprès des références.
- Les offres groupées ne sont pas ventilées arbitrairement : précisé avec les responsabilités annuelles.

## Ce qui reste de la traçabilité

Les audits et archives sont préservés. Les scénarios bas/central/haut, sources de produits, méthodes, hypothèses de gains et qualifications détaillées restent consultables. Les inconnues restent inconnues ; aucun statut n’est transformé en validation, aucun montant n’est remplacé par une certitude.

Les contenus affichés restent dans `config/application.yaml`, `source/synthese-sponsor.yaml`, `source/decision-make-buy.yaml`, `source/recalibration-metier.yaml`, `source/lecture-comparative.yaml`, `source/explications-modele.yaml` et `source/references-couts-integration.yaml`. Les documents explicatifs existants restent en Markdown. React organise leur affichage sans porter la prose métier ni une nouvelle formule financière. L’impression conserve les détails que le lecteur a ouverts ; elle ne réexpose plus automatiquement toutes les justifications.

`AGENTS.md` porte désormais un contrat éditorial prioritaire. Les prescriptions contradictoires d’avant/après dans Estimations et les descriptions périmées du README ont été corrigées. Il faut évaluer chaque ajout par sa contribution à une question du sponsor, et non par sa capacité à documenter le travail de l’auteur.

La refonte du dernier item du menu en parcours Synvance, Références de marché et Glossaire demeure décrite dans l’[audit navigation](2026-10-25-navigation-sources.md). Cette intervention allège les contenus existants ; elle n’anticipe pas la réalisation complète de cette refonte.

## Vérification

La compilation TypeScript/Vite et le contrôle d’absence de contenu en dur passent. Les 26 tests de l’adaptateur et des scénarios passent : 25 au premier lancement et le test HTTP après relance avec accès localhost autorisé (le premier essai était bloqué par le bac à sable).

Comparaison exhaustive du bootstrap avec un instantané pris avant les modifications : paramètres, cinq options, dépenses annuelles, cumuls à 3/5/7/10 ans, reste à financer et années de service identiques. Seule l’identité de version documentaire change. Le contrat de reprise de simulation reste identique. Les empreintes des résultats YAML générés sont synchronisées ; leurs valeurs restent inchangées.

Lecture dans le navigateur : Estimations sans tableau historique et avec détails repliés ; synthèse avec résultats et précautions localisées ; Simulations à trois ans avec construction en cours et reste à financer ; Sources sans carte historique ; références de marché avec méthode repliée. Les liens locaux des documents explicatifs modifiés ont été vérifiés. La revue du tableau fonctionnel a conduit à raccourcir les résumés sans supprimer les analyses détaillées.

Le démarrage local dépassait parfois le délai de 45 secondes du lanceur pendant les contrôles. Le délai a été porté à 120 secondes, sans modification du serveur ni de son exposition réseau. L’identité du processus a été vérifiée avant redémarrage.

Version finale contrôlée : `69f2ab2b4b208bbec32e6ff8cc7f96a1fadcc8c3584319358bfde8a6993a1dcf`. Vérification finale des empreintes des deux résultats YAML : synchronisées. Aperçu temporaire : `tmp/study-app/estimations-lecture-sponsor.png`. Les détails de charges ont été ouverts puis repliés pour vérifier leur accessibilité.


## Lecture en deux minutes et bloc Simuler

La Synthèse présente désormais trois réponses avant les détails : maîtrise des règles SCM et responsabilité produit, dépenses/écarts avec le Make de référence nommé, puis trois conditions de Go. Les années de service sont visibles auprès des montants ; aux horizons où la réalisation se poursuit, les dépenses restantes apparaissent dans chaque carte. Le détail des cinq options, les engagements, les bénéfices et le cadrage sont fermés par défaut. Aucun montant ni algorithme économique n’est ajouté à React.

La simulation mêlait réglage, comparaison et calendrier annuel sur un écran très long ; les paramètres étaient cachés dans un panneau latéral. Le bloc Simuler sépare maintenant trois usages : Hypothèses du scénario, Comparer les résultats, Dépenses par année. Un seul composant garde les saisies et le dernier résultat, sans dupliquer le moteur. Les imports, exports et scénarios enregistrés restent accessibles depuis chaque page. Le plan annuel est explicitement sur dix ans ; l’horizon partagé s’applique à la comparaison. Le lien historique vers la simulation continue d’ouvrir les résultats.

Un chargement de scénario restaure également son nom après réussite. Un import refusé ne renomme plus le scénario courant. Les résultats affichés après une erreur de saisie sont identifiés comme le dernier calcul valide.


Contrôles de cette reprise : TypeScript, contrôle des contenus et build Vite réussis. Les 30 tests d’adaptation/calcul et 11 tests de reprise sont satisfaits ; les attentes sur l’ancien menu ont été actualisées puis les deux tests de parcours concernés relancés. Comparaison des instantanés API `journey-after.json` et `brief-after.json` : paramètres, budgets, annuités, horizons, ancre et contrat de simulation inchangés.

Contrôle navigateur : synthèse aux quatre horizons, ouverture du détail des cinq options ; scénario Java avec build de 60 mois conservé entre paramètres/comparaison/annuel, sélection de .NET et horizon de 7 ans repris après rechargement ; sauvegarde puis restauration réussies ; durée hors limites signalée et résultats antérieurs identifiés. Le scénario temporaire de contrôle a été retiré et son onglet fermé. Aperçus : `tmp/study-app/sponsor-two-minutes.png` et `tmp/study-app/sponsor-go-details.png`.


## Mes hypothèses : comparaison éditable des cinq options

Le sélecteur de stack est remplacé par une grille commune : chaque ligne représente un paramètre et chaque colonne une option. Les contrôles existants conservent leurs unités, bornes et conversions. Les montants/durées d’intégration Make en lecture seule viennent du résultat de simulation ; les services Buy restent groupés sans ventilation inventée. Les états non éditables et leurs explications sont dans la configuration YAML, avec accès aux sources depuis chaque ligne. Les hypothèses communes sont saisies une seule fois sous la grille.

Validation : TypeScript, contrôle de contenu et build réussis ; quatre tests ciblés sur la grille, la conservation de référence et les liens SAP/durées Buy vers Make passent. Vérification navigateur de cinq modifications distinctes, reprise après rechargement et lecture des cellules calculées : 36 mois et 10 081,9 k€ dans les trois colonnes Make pour le scénario temporaire de contrôle. Ces valeurs de test ne modifient pas les hypothèses de référence.


## Dépenses annuelles : comparaison des cinq options

Les cinq colonnes sont maintenant permanentes dans la lecture annuelle. Chaque ligne présente le total d’une année ; le bouton de l’année déplie les trois postes dans les mêmes colonnes, sans isoler une stack. Plusieurs années peuvent rester ouvertes. Le tableau est placé avant le graphique cumulé, accessible à la demande. Le build Buy est présenté sans objet, avec explication dans les conventions ; les annuités et leur calendrier restent ceux du moteur.

Le contrôle des cumuls vérifie aussi que les cinq options partagent les dix années et que les trois composantes de chaque annuité reconstituent son total. Aucun calcul économique ni scénario de référence n’est modifié par cette restitution.


Validation de cette lecture annuelle : compilation TypeScript, contrôle des contenus et build Vite réussis ; tests des annuités/cumuls et de non-mutation de la référence réussis. Dans le navigateur, les années 1 et 7 ont été ouvertes simultanément. Une variation temporaire du build Java à 10 000 k€ a actualisé les totaux et le détail Build des quatre premières années à 2 500 k€/an, sans modifier les autres options ; la référence a ensuite été rétablie. Aperçu : `tmp/study-app/depenses-annuelles-cinq-options.png`.

## Total sur dix ans dans le tableau annuel

Une ligne de pied de tableau reprend les cumuls sur dix ans du moteur pour les cinq options. Son bouton déplie les trois postes dans les mêmes colonnes, indépendamment des années ouvertes. Le libellé et les explications restent dans le YAML. Le total suit le scénario courant et conserve sa fenêtre de dix ans quand la comparaison utilise un horizon plus court.

Validation : TypeScript, contrôle des contenus et build Vite réussis. Le test de rapprochement des horizons vérifie désormais chaque poste et le total avec les annuités, pour les cinq options et les quatre horizons. Dans le navigateur, dépliage/repli vérifiés ; le build Java porté temporairement à 10 000 k€ fait passer son total à 23 430,9 k€, sans changer les quatre autres options. Après restauration de la référence et sélection de trois ans dans la comparaison, le tableau annuel conserve les cinq cumuls sur dix ans. Aperçu : `tmp/study-app/depenses-annuelles-total-dix-ans.png`.

Le pied du tableau annuel reste maintenant fixé au bas de sa zone de défilement, avec ses trois postes lorsqu’ils sont ouverts. Le même élément de tableau conserve les cinq colonnes, sans copie des montants ni calcul supplémentaire. La fixation est désactivée à l’impression. Build Vite et contrôle de contenu réussis ; vérification navigateur du total replié et déplié au début, au milieu et en fin de défilement. Aperçu : `tmp/study-app/depenses-annuelles-total-fixe.png`.

## Commande globale des détails annuels

Le bouton au-dessus du tableau ouvre les dix années ensemble et les replie lorsqu’elles sont toutes ouvertes. Son action suit les ouvertures individuelles : un état partiel propose de tout ouvrir. Le détail du total fixe reste indépendant. Les libellés sont dans le YAML, les relations accessibles pointent vers les groupes de lignes existants ; aucune valeur ni méthode économique ne change.

TypeScript, contrôle des contenus et compilation Vite réussis. Contrôle navigateur : ouverture des dix années avec Entrée, fermeture individuelle de la deuxième année puis réouverture globale, repli global avec Espace, indépendance du total ouvert, alignement des cinq colonnes et lecture pendant le défilement. Serveur relancé pour charger les libellés. Aperçu : `tmp/study-app/depenses-annuelles-toutes-annees.png`. La règle de finition autonome du périmètre demandé est inscrite dans AGENTS.md.

## Finition autonome des trois pages Simuler

Relecture sponsor : retrouver les paramètres changés et revenir à une valeur de référence était difficile ; les erreurs indiquaient une saisie invalide sans donner de bornes ni guider vers la cellule ; le bouton global de référence n’avait qu’une icône ; la comparaison donnait les postes par couleur et au survol sans table chiffrée à l’horizon choisi. Le remplacement d’un scénario de même nom était implicite.

Corrections : navigation directe entre les trois pages, repérage des cellules modifiées et récapitulatif repliable référence/scénario avec restauration unitaire ; rétablissement global explicite et annulable ; validation des nombres depuis les bornes YAML avant appel au moteur, erreurs économiques conservées côté moteur, retour au champ concerné ; suppression de l’alerte lorsque la saisie revient au résultat valide. Les résultats antérieurs restent identifiés pendant une erreur. Les écarts nomment leur référence, les postes détaillés utilisent les cumuls du moteur à l’horizon choisi et les mentions d’avancement sont plus lisibles. Le bouton de sauvegarde annonce le remplacement et normalise le nom. Les contenus restent dans la configuration YAML et le moteur économique ne change pas.

Contrôles : TypeScript, contrôle des contenus, build Vite, 11 tests de reprise/navigation et trois tests moteur/adaptateur (saisies invalides, absence de mutation de référence, rapprochement des cumuls par poste) réussis. Vérification dans le navigateur : durée Java à 20 mois refusée avec bornes 36–60, retour au champ depuis Comparer, retour à 48 supprimant l’alerte ; build Java à 10 000 k€, récapitulatif et annulation du rétablissement ; sauvegarde/chargement et reprise après rechargement à trois ans ; horizons 3/5/7/10 et détail par poste ; budget SAP nul refusé par le moteur puis restauration ciblée sans perdre le build Java ; source documentaire accessible ; annuités et total dépliés cohérents, total Java de contrôle 23 430,9 k€. Aucun message console d’erreur ou d’avertissement. Le scénario temporaire a été supprimé et les paramètres de référence rétablis dans l’onglet de contrôle.

Aperçus : `tmp/study-app/simuler-finition-hypotheses.png` (scénario de contrôle) et `tmp/study-app/simuler-finition-comparaison.png` (référence).


## Finition autonome des quatre pages Comprendre — 26 octobre 2026

Relecture dans l’ordre du sponsor : Périmètre et options → Offres Synvance → Références de marché → Estimations. La grille métier affichait trop de justifications au premier niveau ; les repères de marché répétaient leurs précautions ; les budgets initiaux et les montants annuels manquaient de distinction visuelle. Les recherches et le changement d’étape demandaient aussi des manipulations inutiles.

Corrections : grille des capacités compacte (fonctions et trois justifications accessibles dans le détail), filtres de hiérarchie conservés dans l’URL, recherches tolérant accents et préfixes, compteurs et remise à zéro. Explication OMS centrée sur le parcours de commande. Parcours Synvance clarifié sur ce qui est acheté, les compléments et les facteurs de variation ; chaque nouvelle étape revient au début de sa lecture. Marché : enseignements et plages avant la méthode, justification du rapprochement accessible à la demande, distinction entre prix non publié et prix historique non converti, aucune date « null ». Estimations : deux enveloppes initiales et un montant annuel explicitement distingués, explication de la valeur centrale et de sa fourchette, tableaux longs avec en-têtes et première colonne visibles pendant le défilement. Les libellés et contenus métier restent dans les YAML ; AGENTS.md pérennise ces règles.

Contrôles : TypeScript, contrôle des contenus et build Vite réussis ; 11 tests JavaScript de reprise/navigation/recherche et six tests Python ciblés de parcours, sources, références, complexité et rapprochement annuel réussis. Les empreintes des résultats générés ont été actualisées pour les textes explicatifs ; leurs options économiques, comparaisons et annuités sont strictement identiques. Comparaison des instantanés API avant/après : paramètres et résultats inchangés (hors version du modèle), contrat de simulation identique.

Vérification navigateur : explication et exemple OMS, fonctions et niveaux détaillés d’Inventory Tracking, filtre Inventory Management conservé après rechargement, six étapes Synvance et retour au début d’étape, recherche marché vide puis remise à zéro, fiche d’un prix historique sans conversion, tarifs par JH, comparaison des budgets et charges par capacité, recherche « reservation » et détail des cinq options. Les éléments de méthode et les preuves sont conservés à la demande. Aperçu : `tmp/study-app/comprendre-referentiel.png`.


Dernier passage visuel : les cinq colonnes de charges restent visibles à 1 264 px de largeur et leurs en-têtes restent fixes pendant le défilement interne. La fiche Club Assist affiche son prix historique de 2 300 000 AUD et « Non converti en euros 2026 », sans date artificielle. Aucun avertissement ou erreur dans la console navigateur. Aperçus complémentaires : `tmp/study-app/comprendre-charges.png` et `tmp/study-app/comprendre-marche.png`. Serveur local relancé avec les contenus finaux.


## Transitions de lecture — 26 octobre 2026

Chaque bas de page réunit un enseignement court, le lien vers la page suivante et le bénéfice de cette lecture. Le nom du lien est résolu depuis `config/application.yaml#nav` : aucun titre de destination parallèle dans `reading_journey`. Le retour à la synthèse distingue référence et simulation personnelle. Le glossaire propose aussi un retour à la décision ; Synvance rejoint Marché en bas de sa dernière étape, après les pièces repliables. Les contenus restent dans le YAML et AGENTS.md porte la règle de cohérence.

Contrôles : TypeScript, contrôle des contenus, build Vite et test de continuité du parcours réussis. Les neuf transitions sont présentes et leurs destinations appartiennent au menu. Parcours navigateur vérifié, dont activation avec Entrée du lien Mes hypothèses ; aperçu du bloc compact à deux colonnes dans `tmp/study-app/transitions-lecture.png`. Aucun calcul ni paramètre économique modifié.


## Projets de référence : lecture des scores — 26 octobre 2026

Suppression de la recherche, des deux filtres et du compteur de résultats dans la liste des quinze projets. Les anciennes valeurs q/platform/kind de l’URL n’excluent plus de projet. Chaque fiche de liste et son panneau affichent séparément la qualité du prix source et le truth level du rapprochement FLOW, sans moyenne des deux notes. Les échelles restent celles du registre ; leur explication est accessible à la demande.

Le gris est piloté par `analyse_dispersion.criteres.truth_level_minimum`, unique seuil YAML de 4/5 déjà utilisé par l’analyse des références. Les projets inférieurs au seuil gardent leurs prix, sources et fiche accessible et portent « Repère de marché uniquement ». Les quinze projets ont actuellement un truth level de 0/5 : tous sont donc grisés, sans réévaluation opportuniste des notes ni suppression de leur rôle de contrôle d’ordre de grandeur. Les labels sont dans `presentation_references` du registre. Les hypothèses économiques et les prix ne changent pas.

Contrôles : TypeScript, contrôle des contenus et build Vite réussis ; analyse du registre réussie (15 références, 12 conversions, aucun rapprochement éligible) ; test existant de classification/normalisation marché réussi.

Contrôle navigateur : les 15 projets sont visibles depuis l’ancienne URL #market?q=club ; aucun champ de recherche ou filtre ne subsiste. Les 15 lignes sous le seuil sont grisées mais accessibles ; ouverture au clavier de Southwark vérifiée (rapprochement FLOW 0/5, qualité du prix 4/5). Légende des deux échelles ouverte et refermée, aucune erreur ou alerte console. Capture : tmp/study-app/projets-reference-scores.png.
