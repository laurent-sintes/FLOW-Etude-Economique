# Audit UX/UI — repartir de l’essentiel

Date : 27 octobre 2026. Périmètre : application locale FLOW servie sur `127.0.0.1:8766`, interface React, navigation et contenus YAML actifs. Cet audit décrit une cible d’interface ; il ne modifie pas le modèle économique ni ses sources.

## Verdict

L’application fait parcourir la documentation du modèle avant de permettre une comparaison simple. Elle mélange trois tâches : décider, vérifier le calcul et explorer le périmètre métier. Les données et la traçabilité sont riches, mais leur forme actuelle demande trop de navigation et trop de lecture pour obtenir une réponse. La cartographie doit sortir du parcours courant de l’outil de coûts. Elle peut rester une source de traçabilité interne et être proposée plus tard comme outil spécialisé.

Le premier produit doit répondre à trois questions, dans cet ordre : **combien coûtent les options ?**, **qu’est-ce qui change si je modifie une hypothèse ?**, **que contient le calcul ?**

## Constats observés

| Priorité | Constat | Effet concret | Preuve dans la version locale |
| --- | --- | --- | --- |
| Bloquant | La carte est présentée dès « Comprendre », puis devient le contenu principal de « Périmètres comparés » et revient dans « Build ». | Le lecteur doit comprendre domaine, sous-domaine, Business Area, capacité, offre, sujet et couche de lecture avant d’arriver au coût. | `ComparisonLogic`, `ScopeComparison`, `CoreBuild` dans `app/src/SponsorJourney.tsx` ; `app/src/BusinessAtlas.tsx`. |
| Bloquant | Un clic sur « Master Plan » quitte « Logique de comparaison » et mène à « Périmètres comparés » avec un filtre ; un clic sur « Replenishment » ajoute une fiche dans la page ; « Fonctions, hypothèses et preuves » ouvre une fenêtre longue avec d’autres vues et renvois. | Un clic n’a pas un résultat prévisible. Le détail masque l’objectif initial. | Parcours observé `#logique` → `#perimetres?domain=domain-plan` → `#perimetres?...&capability=D05.e` → `atlas_proof=capability`. |
| Bloquant | Des liens ouvrent un contenu qui n’a pas d’entrée dans le menu, notamment « Offres Synvance ». D’autres remplacent le contenu d’une page du menu par une lecture interne, tout en conservant son titre général. | Le lecteur ne sait plus où il est ni comment revenir au résultat. | `context_pages: synvance` dans `config/application.yaml`, rendu de la navigation dans `app/src/App.tsx`, `JourneyDetail` dans `app/src/SponsorJourney.tsx`. |
| Majeur | Le menu contient onze entrées en quatre groupes, dont trois pages pour une seule simulation. | La structure ressemble à un dossier documentaire ; elle oblige à choisir une page avant de choisir une action. | `config/application.yaml#nav` et `#navigation_groups`. |
| Majeur | « Comprendre » réunit Make/Buy, cartographie, plateforme technique et plusieurs responsabilités financières. | La page d’introduction exige un effort de lecture disproportionné pour une décision de coût. | Écran `#logique` et `ComparisonLogic`. |
| Majeur | Les pages de calcul réexposent la carte, les commentaires de méthode et des renvois vers de longues lectures. Le résultat à cinq options est déjà présent mais se trouve aussi en Synthèse, dans Estimer et dans Simuler. | Les mêmes notions changent de contexte, sans progression claire. | `#synthese`, `#build`, `#exploitation`, `#simulations`. |
| Majeur | À une largeur d’environ 785 px, les grilles à cinq options montrent quatre colonnes d’options ; SAP se trouve hors du cadre visible. | Une comparaison présentée comme simultanée ne l’est pas réellement à cette largeur. | Écrans `#simulation-hypotheses` et `#simulation-depenses` observés dans le navigateur local. |
| Majeur | Le menu mémorise la dernière URL détaillée de chaque page. Une entrée du menu peut rouvrir une fiche ou une lecture profonde au lieu de la page d’accueil attendue. | Le menu cesse d’être un point de retour fiable. | `navigation.href()` dans `app/src/App.tsx`, mémoire de route dans `app/src/readerNavigation.ts` ; liens du menu observés avec `capability`, `focus` et `detail`. |
| Moyen | Les liens sur les termes du glossaire changent de page. Les preuves détaillées demandent parfois de traverser d’autres lectures avant d’atteindre la pièce. | Une simple définition ou justification rompt le fil de lecture. | `#glossaire?term=...`, `SourceLink`, `JourneyDetail`, liens vers Synvance. |

Les contrôles de traçabilité, les sources et les calculs sont des acquis à conserver. Le problème est le niveau auquel ils sont exposés, ainsi que le nombre de destinations qui leur sont consacrées.

## Cible V1 : trois destinations, une tâche par écran

1. **Comparer** — page d’arrivée. Horizon 3/5/7/10 ans ; trois options visibles par défaut : Make de référence, Microsoft et SAP. Une action « Voir les cinq options » ajoute .NET et Rust sans changer de page. Tableau compact : dépenses cumulées, date ou années de service complet, reste à financer. Une représentation courte des trois postes du modèle accompagne le total. Une seule phrase signale les limites qui peuvent fausser la comparaison (périmètres et montants non chiffrés), avec accès à leur justification.
2. **Simuler** — même comparaison et même horizon, avec une action « Modifier les hypothèses ». Choisir d’abord une option ou un poste, puis ne montrer que ses paramètres modifiables ; les valeurs calculées sont lisibles dans le résultat, pas présentées comme des cases à remplir. Les paramètres communs sont regroupés à la fin. Les résultats se mettent à jour dans le même écran. Enregistrer/importer/exporter restent disponibles. Le calendrier annuel et le détail par poste s’ouvrent depuis le résultat ; ils ne constituent pas des pages du menu.
3. **Modèle** — une page courte, consultable à tout moment : deux phrases sur Make et Buy ; les trois postes visibles (Build Core System, Intégration & Migration, Services et abonnements) ; un schéma ou trois étapes de calendrier (build, intégration, service complet) ; les règles de lecture de l’horizon. Cette page explique l’assiette des chiffres. Les distinctions cycle du Core, Run, MCO client, évolutions client et contrats Buy groupés sont accessibles depuis les postes, sans former un cours préalable.

La navigation primaire se limite à **Comparer / Simuler / Modèle**. Le logo rejoint Comparer. Un libellé de page et un lien de retour restent visibles dans tout contenu secondaire. Aucun lien ordinaire ne doit mener à une destination absente du menu et se présenter comme une nouvelle page. Les anciens liens directs restent résolus vers l’écran V1 pertinent, avec ouverture éventuelle du détail associé.

## Règle unique pour les justifications

Le chiffre, sa réserve décisive et l’accès à sa preuve restent ensemble. Les explications ne forment ni des pages supplémentaires ni des paragraphes répétés dans la page principale.

| Besoin | Interaction V1 | Contenu maximal à l’ouverture |
| --- | --- | --- |
| Définir un terme | Infobulle accessible au clic, au clavier et au toucher | Une définition courte. |
| Comprendre un montant, un paramètre ou une limite | Fenêtre « D’où vient ce chiffre ? » ouverte depuis le montant ou l’icône adjacente | Valeur, assiette, formule ou règle de calcul en langage simple, hypothèse, limite, source datée. |
| Vérifier une pièce | Lien « Voir la source » dans cette même fenêtre | Extrait ciblé, puis pièce complète à la demande. |
| Examiner une analyse longue | Action explicitement nommée depuis la fenêtre, hors parcours V1 | Document complet séparé, avec retour au montant et au scénario conservés. |

La fenêtre doit avoir un titre précis, une fermeture évidente, un retour du focus au déclencheur et une profondeur unique : aucune fenêtre sur une fenêtre, aucun renvoi vers une « page détail » intermédiaire. Un tooltip ne porte jamais seul une information essentielle ; la fenêtre peut contenir plusieurs lignes et rester lisible au clavier et sur mobile.

## Ce qui sort du parcours de départ

- Cartographie interactive, exploration par capacité, couches de complexité et architecture : conserver les identifiants et rattachements comme preuves du modèle, sans les afficher dans la V1.
- Parcours Synvance en six étapes, quinze fiches de marché, quarante-trois situations d’intégration et tableaux de charges par capacité : conserver les sources et les restituer seulement depuis une justification ciblée ou un document de travail distinct.
- Pages autonomes FAQ et Glossaire : convertir les réponses réellement nécessaires en aides contextuelles ; conserver les URL anciennes comme redirections.
- Bloc « Continuer la lecture », répétition des conclusions, comparaison des quatre horizons sous une seconde forme, trois pages Simuler et trois pages Estimer : retirer du flux principal.

Ce retrait porte sur la présentation. `source/modele-composable.yaml`, `source/deploiement-groupe.yaml`, les prix Buy, les cinq options, les horizons et la mécanique de simulation restent la référence. Les montants groupés Buy demeurent non ventilés ; aucune répartition artificielle sur la carte ou les capacités n’est introduite.

## Ordre de réalisation recommandé

1. Faire un prototype statique de **Comparer**, **Simuler** et **Modèle**, alimenté par les résultats actuels, pour valider l’ordre de lecture, les libellés et la largeur mobile avant de déplacer les composants existants.
2. Construire la fenêtre de justification commune et relier d’abord les trois postes, les totaux, les dates de service et les paramètres de simulation à leurs preuves courtes. Prévoir l’accès à la source complète dans la fenêtre.
3. Unifier les pages de simulation et retirer les cartes du flux principal. Conserver l’état du scénario, les imports/exports et les contrats de reprise.
4. Rediriger les anciens liens vers une destination V1 identifiable ; remettre les entrées du menu sur des URL de tête, sans restaurer automatiquement un ancien détail depuis le menu.
5. Vérifier le parcours au clavier et aux largeurs 375, 768 et 1440 px, puis vérifier la parité des cinq options, des quatre horizons, du calendrier, des centimes internes et des scénarios enregistrés.

## Critères d’acceptation UX

- Un nouveau lecteur trouve la comparaison des options sans ouvrir une autre page ou une justification.
- Il peut modifier une hypothèse et voir son effet au même endroit, sans traverser trois pages.
- Chaque montant majeur a une justification à un clic ; sa source complète est à un clic supplémentaire au plus.
- Le menu ramène toujours au début d’un des trois écrans V1. Aucun lien de contenu ne mène à une page « fantôme ».
- La V1 ne présente aucune cartographie interactive. Le modèle conserve sa traçabilité métier.
- À 375 et 768 px, aucune option de comparaison n’est invisible sans indication explicite ; la solution de préférence est une sélection de deux ou trois options plutôt qu’une grille latérale de cinq colonnes.
- Fermer une justification ramène au montant et conserve l’horizon, les options et les hypothèses en cours.

## Limite de l’audit

Revue de l’interface locale, des principales routes et d’un parcours réel par la carte vers une capacité et ses charges ; inspection du code de navigation et des composants concernés. Il ne s’agit pas d’un test utilisateur ni d’une validation des montants économiques.
