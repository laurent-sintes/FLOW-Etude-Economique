# Audit UX — densité, cadres et défilement

Date : 26 octobre 2026. Application locale FLOW, version du modèle affichée `a2f71c154f`.

## Conclusion

Le problème est confirmé. Trois règles CSS plafonnent des tableaux à 70 ou 72 % de la hauteur de fenêtre, sans distinguer leur rôle ni leur longueur. Elles imposent au lecteur de gérer le défilement de la page puis celui du tableau. Le composant `Section` ajoute systématiquement un cadre et des marges, y compris lorsque le tableau constitue le sujet principal de la vue.

La cible recommandée est une lecture verticale continue par défaut. Les tableaux larges gardent un défilement horizontal local lorsque nécessaire. Une grande grille de travail peut disposer d'un espace dédié, mais doit alors occuper réellement la place disponible. Les panneaux modaux restent une exception utile pour consulter un détail sans quitter la comparaison.

Il ne faut ni interdire tous les cadres, ni réduire les polices pour faire tenir davantage de texte. La priorité est de récupérer la place prise par les conteneurs, les retraits et les commandes répétées.

## Méthode et portée

- Lecture de `styles.css`, `brand.css`, des composants communs, des vues, de la Synthèse, du bloc Simuler et des composants de comparaison.
- Inspection dans le navigateur des neuf pages principales à 1280 × 720 pixels CSS ; examen des cinq lectures de Périmètre et des vues Run & MCO et Charges par capacité d'Estimations.
- Ouverture du détail supplémentaire de la comparaison hors coûts ; dépliage des dix années et du total annuel ; déplacement au clavier dans la zone annuelle.
- Mesures DOM des hauteurs et largeurs des conteneurs et du contenu. Les descendants d'un accordéon fermé peuvent conserver des dimensions dans l'outil : ils ne sont pas comptés comme des zones visibles avant ouverture.
- Revue documentaire W3C et systèmes de conception ci-dessous.

Il s'agit d'un audit ergonomique et d'une revue ciblée d'accessibilité, pas d'une certification WCAG. Les petits écrans, le zoom à 200/400 %, tous les parcours clavier et toutes les combinaisons de détails ouverts restent à vérifier lors de la mise en œuvre. Aucun calcul, paramètre ou texte métier n'a été modifié par cet audit.

## Ce que disent les normes et recommandations

### Exigences d'accessibilité

**WCAG 1.4.10 — redistribution, niveau AA.** Le texte courant doit pouvoir se redistribuer à une largeur équivalente à 320 pixels CSS sans imposer un défilement dans deux directions. Les tableaux et autres objets dont le sens dépend de deux dimensions bénéficient d'une exception. Elle s'applique à ces objets, pas à toute la page. Un conteneur horizontal réservé à un tableau peut donc être une bonne solution. Cette règle ne constitue pas une interdiction du défilement vertical imbriqué. [W3C — Reflow](https://www.w3.org/WAI/WCAG21/Understanding/reflow)

**WCAG 2.1.1 — clavier, niveau A.** Le contenu défilant doit pouvoir être atteint et parcouru au clavier. La règle ACT associée contrôle la présence d'un point de focus permettant de déplacer la zone ; les comportements réels restent à tester. [W3C — zones défilantes et focus](https://www.w3.org/WAI/standards-guidelines/act/rules/0ssw9k/)

**WCAG 2.4.11 — focus non masqué, niveau AA.** Les en-têtes et pieds fixes ne doivent pas cacher entièrement un composant qui reçoit le focus. Viser un focus entièrement visible est préférable et correspond au critère renforcé AAA. Cela concerne particulièrement le total fixe du tableau annuel. [W3C — Focus Not Obscured](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum)

### Recommandations de conception

GOV.UK recommande de commencer par un contenu bien structuré, avec titres et éventuellement liens d'ancrage, avant d'ajouter des accordéons. Les informations nécessaires à tous ne devraient pas y être cachées ; son système déconseille les accordéons imbriqués. C'est une recommandation de ce système de conception, pas une limite universelle imposée par WCAG. [GOV.UK — Accordion](https://design-system.service.gov.uk/components/accordion/)

Les encarts doivent servir à distinguer une information particulière. GOV.UK conseille de les utiliser avec parcimonie, car leur multiplication réduit leur efficacité. Cela soutient le retrait des cadres purement décoratifs, sans rendre toute carte indésirable. [GOV.UK — Inset text](https://design-system.service.gov.uk/components/inset-text/)

Nielsen Norman Group recommande des ascenseurs reconnaissables et un défilement prévisible, et souligne la difficulté de parcourir un contenu selon deux axes. L'article consulté date de 2005 : il sert ici d'appui sur la prévisibilité, pas de prescription actuelle visant à placer toute la page au-dessus du premier écran. [NN/g — Scrolling and Scrollbars](https://www.nngroup.com/articles/scrolling-and-scrollbars/)

**Aucune de ces sources ne fixe un seuil universel à 75 % de hauteur, ni un nombre maximal universel de cadres.** Le choix d'un défilement principal unique est la recommandation de cet audit pour FLOW et son usage sponsor.

## Constats mesurés

Mesures arrondies, à 1280 × 720 ; la hauteur visible est celle du conteneur, pas nécessairement la portion présente dans le premier écran.

| Vue | Hauteur du contenu / zone | Diagnostic | Préconisation |
| --- | --- | --- | --- |
| Mes hypothèses | 746 / 502 px | La grille est tronquée de 244 px ; page et tableau défilent séparément. | Retirer le plafond vertical en lecture courante ; garder les cinq options, les champs et le défilement horizontal si nécessaire. |
| Dépenses annuelles, années et total repliés | 593 / 516 px | Un second ascenseur pour seulement 77 px supplémentaires. | Afficher les dix années dans le flux ; conserver le total visible avec une solution liée à la fenêtre. |
| Dépenses annuelles, tous les détails ouverts | 2 083 / 516 px | En-tête 64 px et pied déplié 179 px : environ 47 % de la zone sont occupés par les éléments fixes. | Prévoir un mode de comparaison réellement étendu ; préserver les cinq colonnes et le détail du total, y compris au clavier. |
| Périmètre — couverture | 1 319 / 502 px | Le tableau principal est une fenêtre dans la page. | Lecture verticale continue avec repères de colonnes persistants. |
| Périmètre — Make / Buy hors coûts | 1 466 / 487 px | Longues phrases dans une zone limitée, avec aussi un ascenseur horizontal. | Étendre la comparaison en hauteur dans le flux ; conserver les colonnes pour comparer directement. |
| Estimations — Run & MCO | 1 037 / 502 px | Le détail annuel est limité arbitrairement par la même classe que les grandes grilles. | Retirer le plafond vertical de cette lecture budgétaire. |
| Estimations — Charges par capacité | 9 203 / 502 px | 89 lignes : cas légitime de grille de travail, mais placée après le comparatif budgétaire et plusieurs niveaux d'introduction. | Donner à cette vue un espace de travail étendu ; rendre le rappel budgétaire compact ou dépliable dans cette sous-vue. |

### Un défilement horizontal parfois créé par quelques pixels

Dans la comparaison hors coûts, le tableau impose une largeur minimale de 920 px. La zone disponible mesure 918 px : le débordement de **2 px** suffit à afficher un ascenseur horizontal et à retirer environ 15 px de hauteur utile.

Dans « Sécurité, adoption, dépendances et réversibilité », le retrait du détail réduit encore la zone à **894 px**, face au même tableau de 920 px. Après ouverture, le lecteur rencontre deux tableaux ayant chacun leurs ascenseurs, en plus du défilement de la page et de celui du menu.

Correction recommandée : supprimer le retrait autour des tableaux de détail, revoir la largeur minimale selon les colonnes et donner au tableau toute la largeur de la section. Ne pas masquer le débordement avec `overflow:hidden`, qui couperait le contenu.

### Des marges qui se cumulent

Sur cette largeur, la surface principale mesure environ 1 045 px après le menu et l'ascenseur de page. Les marges de `main` prennent 64 px ; une `Section` ajoute 44 px de marge intérieure et ses bordures ; l'ascenseur vertical du tableau consomme encore de la largeur. Il reste environ 918 px pour celui-ci.

Le cadre d'une section coûte donc à lui seul environ **46 px de largeur**, récupérables pour une grille dominante. Ce n'est pas énorme sur un écran large, mais cela suffit ici à déclencher des défilements horizontaux évitables. Un détail imbriqué ajoute 24 px de retrait.

Ce problème ne vient pas toujours de composants `Section` littéralement imbriqués. Il vient aussi de la succession page → carte → détail avec retrait → cadre du tableau → cellules. Il faut évaluer l'espace réellement perdu plutôt que compter seulement les balises.

### Le menu latéral défile lui aussi

À 720 px de haut, son contenu mesure environ 795 à 814 px selon les retours à la ligne. Les groupes de navigation restent pertinents, mais l'espacement du logo, des liens et du pied provoque un ascenseur presque permanent. Réduire ces espacements peut rendre le menu stable sur un portable ; conserver son défilement de secours sur les écrans plus petits.

## Relecture de toutes les pages

| Page ou vue | À conserver | À simplifier |
| --- | --- | --- |
| Synthèse sponsor | Trois options rapprochées, chiffres lisibles, trois conditions de Go, approfondissements facultatifs. | Alléger le cadre extérieur du comparatif si les cartes d'options suffisent ; ne pas densifier en réduisant les chiffres. Aucun défilement interne vertical principal observé. |
| Périmètre — couverture | Comparaison simultanée et détails contextuels. | Cadre extérieur et plafond vertical du tableau. |
| Périmètre — hors coûts | Apports et contreparties en regard, détails de décision. | Deux petites fenêtres de lecture : faire défiler les tableaux avec la page ; retirer le retrait du second. |
| Périmètre — responsabilités | Trois colonnes Make/SAP/Microsoft, trois lignes de responsabilité. | Présentation à plat ; pas de raison d'ajouter un ascenseur vertical local. La vue actuelle n'en présente pas à cette taille. |
| Périmètre — référentiel | Hiérarchie métier et filtres, fonctions à la demande. | Page d'environ 12 000 px : proposer un accès rapide aux sous-domaines/Business Areas, sans transformer chaque groupe en fenêtre défilante. Ne pas remplacer la structure métier par des onglets techniques. |
| Périmètre — architecture | Les couches architecturales sont de vrais regroupements ; le détail de composant est utile. | Un cadre par couche suffit ; alléger le cadre extérieur et les retraits internes. Pas d'ascenseur vertical local à ajouter. |
| Offres Synvance | Six étapes, réponse avant les pièces, progression explicite. | Les deux options peuvent être séparées par des titres et filets légers. Pas de besoin de zone défilante interne identifié dans la structure. |
| Références de marché | Enseignements avant liste, badges et fiches à la demande. | Liste de projets à plat, avec séparateurs ; cartes SAP/Dynamics gardées si elles aident à comparer. La liste entière défile déjà avec la page. |
| Estimations | Comparaison des budgets et distinction initial/annuel. | Rappel budgétaire trop encombrant avant une grille longue ; marges et plafond de Run & MCO ; espace dédié aux charges. |
| Mes hypothèses | Cinq colonnes éditables, paramètres communs séparés, aide contextuelle. | Supprimer le plafond de 70vh ; réduire le cadre et regrouper les commandes au-dessus de la grille. |
| Comparer les résultats | Cinq options et horizons, décomposition à la demande. | Un seul cadre autour du résultat ; limiter l'empilement des commandes. Aucun ascenseur vertical interne principal observé. |
| Dépenses annuelles | Dix années, détails individuels/globaux, total fixe indépendant. | Retirer le petit cadre défilant par défaut ; réserver un mode étendu aux comparaisons détaillées, sans perdre la visibilité du total. |
| Glossaire | Recherche, familles, définitions accessibles directement. | Liste à séparateurs ; explications FLOW à la demande. Pas de fenêtre verticale interne nécessaire, même pour une page longue. |
| Panneaux de détail et sources | Retour au contexte, fermeture et restitution du focus. | Un seul défilement vertical dans le panneau ; éviter les cartes décoratives internes. Défilement horizontal local des tableaux admis si nécessaire. |

## Plan de correction proposé

### Priorité 1 — supprimer les frictions avérées

1. Séparer les styles de lecture, de tableau horizontal et de grande grille ; retirer `max-height:70vh` de la classe générique `comparison-scroll`.
2. Retirer le plafond de Mes hypothèses, de Couverture, de la comparaison hors coûts et de Run & MCO.
3. Supprimer les retraits qui déclenchent un défilement horizontal pour quelques pixels ; conserver une largeur minimale seulement si les colonnes en ont réellement besoin.
4. Introduire une présentation de section sans carte, utilisée lorsque la section constitue déjà le contenu principal de la vue. Garder titres, hiérarchie et séparation entre sujets.
5. Réduire les espacements du menu à hauteur de portable, sans diminuer excessivement les cibles de clic.

### Priorité 2 — aménager les deux vrais espaces de comparaison

- **Charges par capacité :** comparaison étendue accessible directement, rappel des budgets compact, titre/recherche proches de la grille. La grille peut devenir le seul défilement vertical actif dans un mode dédié ; la page de lecture courante ne doit pas concurrencer sa molette.
- **Dépenses annuelles :** dix années dans le flux par défaut. Préserver un total attaché à la fenêtre pendant la lecture du tableau et une largeur synchronisée avec les colonnes. Pour tous les détails ouverts, proposer un espace étendu qui garde les en-têtes et le total. Sur faible hauteur, offrir assez de place aux lignes ; ne pas supprimer silencieusement le détail du total demandé par le lecteur.

Ces deux aménagements demandent une adaptation du comportement, pas seulement la suppression d'une règle CSS. Le pied fixe annuel et les en-têtes actuels dépendent de leur conteneur de défilement. Avec un wrapper `overflow-x:auto`, le comportement de `position:sticky` peut également dépendre de ce wrapper : contrôler les repères dans la solution retenue avant de livrer.

### Priorité 3 — densité cohérente

- Réserver les cartes à de vrais objets autonomes ou à une comparaison d'options.
- Utiliser titres, alignements et filets pour les sections d'une même lecture.
- Les détails repliables s'ouvrent dans le flux, sans hauteur maximale. Éviter les accordéons successivement imbriqués.
- Garder de l'espace entre deux sujets ; réduire d'abord les marges répétées d'un même sujet.
- Ne pas ajouter un résumé encadré en tête de toutes les pages : s'il est utile, une phrase sous le titre peut suffire. Le bloc « À retenir » reste une transition, sans cadre supplémentaire autour de son contenu.

## Critères de réception de la correction

- Un défilement vertical principal par vue de lecture ; toute exception identifiée par sa fonction et vérifiée.
- Aucun ascenseur horizontal pour un débordement accidentel de quelques pixels ; aucun débordement horizontal de la page pour du texte courant.
- Cinq options conservées côte à côte, sans diminution de police destinée à les faire tenir.
- Dix années et total toujours consultables ; total et colonnes alignés, y compris pendant le défilement horizontal et avec les trois postes dépliés.
- Vérifier 1280 × 720, 1440 × 900, petit écran et zoom ; dimensions proposées pour le projet, pas seuils normatifs.
- Tester Tab, Maj+Tab, flèches, Page suivante/précédente, début/fin et fermeture des panneaux ; aucun champ ou bouton masqué par un élément fixe.
- Conserver recherche, état des détails, retour à la lecture, paramètres et résultats de simulation.
- Tous les éventuels nouveaux libellés de commande restent dans les YAML ; aucun changement économique.

## Preuves et dépendances

Captures locales : `tmp/study-app/audit-scroll-annuel.png` (toutes années et total ouverts) et `tmp/study-app/audit-scroll-comparaison.png` (deux tableaux de comparaison, détail ouvert). Ce sont des preuves temporaires, pas des sources du modèle.

Points de code : `app/src/styles.css` (`.comparison-scroll`, `.parameter-matrix-scroll`, `.annual-matrix-scroll`, `.section`, `.disclosure-body`, `.sidebar`), `app/src/brand.css`, `app/src/components.tsx`, `app/src/views.tsx`, `app/src/StudyReading.tsx`, `app/src/BusinessCalibration.tsx`, `app/src/SponsorDecision.tsx`, `app/src/SponsorSummary.tsx`, `app/src/Simulations.tsx`, `app/src/ReadingPages.tsx`, `app/src/ComplexityGrid.tsx` et les contrats de parcours dans `AGENTS.md`.

Statut initial : audit et recommandations. Mise en œuvre autorisée et réalisée dans l'intervention suivante, décrite ci-dessous.

## Mise en œuvre — 26 octobre 2026

- Suppression des trois plafonds génériques de hauteur. Couverture, comparaison hors coûts, Run & MCO, paramètres, charges et annuités suivent désormais le défilement de la page.
- Nouveau composant `TableViewport.tsx` : même table en lecture et en mode agrandi ; pas de montants, en-têtes ou totaux clonés. En lecture, les repères suivent la fenêtre ; le total annuel reste visible avec ses détails. En mode agrandi, un dialogue occupe la fenêtre et la page arrière est immobilisée. Fermeture par bouton ou Échap, retour du focus et de la position de page ; conservation du défilement horizontal.
- Commandes d'agrandissement réservées aux Charges par capacité et aux Dépenses annuelles. Recherche et nombre de résultats accessibles dans la grille de charges agrandie ; dépliage global et unité disponibles dans la grille annuelle agrandie. Les changements de recherche ne ferment pas le mode agrandi.
- Sections à plat, retraits autour des tableaux supprimés, cartes autonomes de la synthèse et regroupements architecturaux conservés. Menu compacté à hauteur de portable, sans réduction des polices. Les filtres Sous-domaine / Business Area existants du référentiel restent l'accès rapide aux groupes.
- Rappel budgétaire repliable dans Charges par capacité, pour atteindre la grille plus rapidement.
- `readingLayout.css` centralise ces règles, après la charte ; `config/application.yaml#table_workspace` porte les deux nouveaux libellés. AGENTS.md décrit le contrat à conserver.

### Contrôles réalisés

- TypeScript sans erreur ; contrôle des contenus sans texte métier ajouté en dur ; compilation de production réussie.
- Onze tests de reprise/navigation réussis ; deux tests Python ciblés sur le parcours et la matrice de paramètres réussis.
- À 1280 × 720 : Mes hypothèses occupe 989 px de largeur utile au lieu de 918, avec 746 px de contenu pour 746 px de zone : aucun défilement vertical interne. Couverture suit également la page ; aucun débordement horizontal de page constaté dans les vues principales inspectées. Menu : 720 px de contenu pour 720 px de zone, sans ascenseur.
- Annuités : dix années et total entièrement dépliés, une seule table dans le DOM, agrandissement puis retour par Échap ; détails conservés. Contrôle clavier : le bouton Année 9 reste au-dessus du pied fixe (bas du bouton 503 px, haut du pied 512 px dans le cas contrôlé).
- Contrôle responsive dans des fenêtres de rendu de 320 × 720 et 640 × 480 via une page de test temporaire : texte redistribué, tableau local horizontal. À 320 px, mode annuel agrandi et déplacement jusqu'à SAP vérifiés visuellement ; libellés d'année et total conservés à gauche. Cela contrôle la largeur CSS équivalente au reflow, sans prétendre couvrir tous les réglages de zoom et technologies d'assistance.
- Les modifications sont de présentation : les valeurs de référence et les formules restent celles du moteur. Le total dix ans observé conserve les cinq valeurs de référence de l'audit précédent.
- Contrôle final : les deux matrices hors coûts, dont le détail ouvert, disposent chacune de 989 px utiles sans aucun débordement local horizontal ou vertical. Recherche « Plan Application » en mode agrandi : 2 résultats, dialogue maintenu ; ouverture et fermeture de la fiche métier puis retour au tableau validés. Saisie de durée Java à 49 mois, navigation vers les annuités, agrandissement/retour et retour à la saisie : valeur conservée ; valeur rétablie à 48 après le test. Aucune erreur ou alerte console.
- Captures après correction : `tmp/study-app/lecture-continue-annuelle.png` et `tmp/study-app/lecture-responsive-320.png`. La page HTML de contrôle responsive était temporaire et a été retirée par la compilation finale ; elle ne fait pas partie du livrable.
