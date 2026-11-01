# Audit de la rubrique Évaluation des charges brutes

**Le parcours est cohérent, mais la lecture doit mieux distinguer les efforts humains, les prix des pièces reçues et les propositions.** Les priorités sont une justification devenue fausse, une prestation classée dans une autre phase que son financement et des tableaux difficiles à comparer sur mobile.

Audit du 1er novembre 2026 sur la version locale `acc90cc525dadf892a9f8ca6c8949054cc1c4206ea107e18d9768d8f226e6250`. L’application, les sources économiques et les estimations n’ont pas été modifiées pendant cet audit.

## Corrections prioritaires

| Priorité | Constat vérifié | Conséquence | Correction recommandée |
| --- | --- | --- | --- |
| Haute | Les interfaces affichent 420 JH, avec une justification qui parle encore de 30 contrats à 10 JH. | Le lecteur ne peut pas reproduire le chiffre avec l’explication donnée. | Expliquer le calcul actif, 40 interfaces × 10,5 JH. Garder le repère antérieur dans les preuves historiques. |
| Haute | Les 90 k€ de support initial Microsoft sont affichés en fonctionnement, alors que le modèle les finance dans l’intégration. | La phase d’apparition à l’écran contredit la phase de financement et peut faire croire à une dépense de fonctionnement. | Présenter ce montant ponctuel avec l’intégration, en conservant son périmètre et son origine. |
| Haute | Sur mobile, les tableaux font 590 à 760 px pour 279 px disponibles. | Le nom du lot et les valeurs adoptée/proposée ne restent pas visibles ensemble. | Passer à des fiches de lot ou d’activité sur mobile, avec les valeurs adjacentes. Conserver les matrices de bureau. |
| Moyenne | Les JH affichés ne précisent pas assez leurs activités incluses et leurs exclusions. | 6 660 JH peuvent être lus comme du développement seul. 3 935 JH peuvent être lus comme un total humain complet. | Donner près du résultat les activités couvertes, les efforts non dimensionnés et les postes financés en euros. |
| Moyenne | Les preuves Make sont accessibles essentiellement par le téléchargement global. | L’expert ne peut pas vérifier un lot ou une charge sans chercher dans le modèle complet. | Relier les lignes à une justification lisible et à leurs preuves, en gardant le téléchargement unique. |
| Moyenne | Le Core System juxtapose référence adoptée, proposition et écart, puis déroule les onze arbitrages et la matrice OSS. | La première lecture donne beaucoup de place à la proposition et peu au sens de la référence utilisée dans les budgets. | Mettre d’abord la référence et son périmètre, puis la comparaison proposée dans une profondeur de lecture explicite. |

## Ce qui fonctionne

Le menu gauche reste plat. Les trois phases, leurs icônes et les onglets Java/Spring, Microsoft et SAP reprennent les mêmes repères que le Framework. Le passage vers une autre phase conserve le choix. Le lien vers la méthode conserve aussi Microsoft lors du parcours contrôlé, avec un retour vers les charges de la même option.

Le statut de la proposition est **explicitement non adopté**. La référence à 6 660 JH et la proposition à 5 950 JH sont séparées dans les données. La proposition ne remplace pas les budgets. Le tableau précise que les estimations des quatre OSS ne s’additionnent pas.

Les montants des pièces Synvance conservent leurs périodes. Le lot SAP « dont Upgrade Finance » reste présenté comme une partie du total. Les contrats groupés restent groupés. Les JH Buy inconnus ne sont pas inventés en divisant les forfaits par un tarif journalier.

Sur ordinateur, les tableaux contrôlés tiennent dans les 865 px disponibles. Le problème de largeur est localisé aux tableaux mobiles, sans débordement global de la page.

## Sens de la rubrique

La rubrique présente aujourd’hui trois natures de contenu :

- Des efforts Make estimés en JH et des travaux acheteur Buy dimensionnés en JH.
- Des forfaits et abonnements Buy documentés dans les pièces Synvance.
- Une proposition d’évolution des estimations du Core System, non adoptée.

Ces éléments sont utiles, mais le titre « Résultat de l’évaluation » ne suffit pas à expliquer leur différence. Chaque option devrait annoncer clairement **ce qui est évalué, son statut et ce qui reste inconnu**. En Buy, le lecteur doit comprendre immédiatement qu’un forfait documenté ne renseigne pas la charge humaine correspondante.

La définition canonique de la charge brute est cohérente : effort sur des activités déclarées, après réutilisation et avant les réductions explicites. Il manque un rappel accessible depuis le résultat. Les onze lots du Core incluent aussi analyse, architecture, QA, pilotage et autres rôles. Ils ne constituent pas 6 660 JH de développeurs.

Une courte synthèse en haut de chaque phase suffit. Une nouvelle page de synthèse ou un nouveau niveau de menu n’est pas nécessaire à ce stade.

## Obtenir le Core System

### Java/Spring

La décomposition adoptée est cohérente avec les onze décisions et totalise 6 660 JH. La proposition totalise 5 950 JH, soit 710 JH de moins. Son statut est visible et doit rester explicite.

La première lecture devrait expliquer ce que couvrent les 6 660 JH. Les rôles existent déjà chez le propriétaire des décisions. La page peut en proposer une lecture courte, puis ouvrir les inclusions et exclusions de chaque lot. Une ventilation par rôle ne doit pas inventer un effort supplémentaire.

La proposition n’a pas besoin d’être supprimée. Elle mérite un bloc identifié : changements proposés, raisons et effet sur les lots. Les arbitrages et la matrice des quatre OSS peuvent venir ensuite. Sa date et sa preuve devraient être accessibles directement. La date est déjà conservée dans la lecture technique, mais n’est pas affichée dans cette page.

Les expressions « ancre », « analogue », « fractions de transposition », « MFA », « LDAP » et « Pac4j » arrivent dans la lecture courante. Les noms techniques ont leur place dans les preuves. La synthèse peut expliquer simplement quels composants sont fournis, quels travaux restent propres à FLOW et pourquoi le lot proposé change.

### Microsoft et SAP

Les 110 JH décrivent l’assistance de l’acheteur à la sélection et à la contractualisation. Ce ne sont ni la construction de la solution éditeur ni la charge d’intégration. La note de périmètre le précise, mais cette distinction devrait apparaître avec le total.

Les deux options reprennent les mêmes travaux acheteur. Ils sont à financer pour l’option retenue, sans additionner deux fois le même dispositif. Le prix initial d’obtention non isolé dans les pièces reste inconnu. Le bloc documentaire peut être compacté en conservant ce fait.

## Intégrer, migrer et déployer

### Java/Spring

Le total affiché de **3 935 JH** se décompose en :

- 1 925 JH de travaux communs.
- 1 200 JH de déploiements sur les quatre pôles.
- 810 JH de direction et de coordination du programme.

Ces sous-totaux aideraient davantage le lecteur que la succession immédiate de quatre tableaux. La page montre également environ 110 k€ et 65 k€ de provisions de coordination technique. Ces provisions ne sont pas converties en JH. Le total de 3 935 JH doit donc rester présenté comme les **JH dimensionnés**, avec cette frontière visible près du chiffre.

**La justification des interfaces doit être corrigée en priorité.** Le moteur utilise le scénario central, 40 interfaces à 10,5 JH, soit 420 JH. La note affichée vient du diagnostic antérieur : 30 contrats à 10 JH, avec la mention « Diagnostic uniquement » et « remplacé ». Elle explique un autre calcul et un autre statut. Le problème vient de la projection documentaire qui associe la nouvelle valeur à l’ancienne justification. Le calcul courant n’est pas à recalibrer pour résoudre ce problème.

Les hypothèses de déploiement et de pilotage gagneraient aussi à être visibles : quatre pôles, deux niveaux d’effort et une durée de pilotage. Les valeurs viennent déjà du scénario central. Il faut les expliquer depuis leurs propriétaires.

### Microsoft et SAP

La page présente des prix des pièces reçues, pas des JH humains : environ 4 240 k€ pour la projection Groupe Microsoft et 13 462 k€ pour les lots SAP, dont 395 k€ pour Upgrade Finance. Le statut « Projection Groupe du COPIL » n’est pas équivalent à une proposition fournisseur. Cette distinction est déjà affichée et doit rester proche du montant.

Le lecteur doit aussi pouvoir distinguer ces prix d’origine des compléments et traitements du budget économique. Une courte transition vers leur utilisation dans le dossier économique éviterait d’assimiler le montant de la pièce au coût complet retenu.

**Le support initial Microsoft est classé sur le mauvais écran.** La vue de fonctionnement affiche 90 k€ de support et conseil qualité, avec la précision « première année seulement ». Le moteur les ajoute pourtant explicitement à l’intégration. La correction porte sur leur classement dans le dossier de charges, en conservant l’unicité du financement.

## Exploiter et Maintien en Conditions Opérationnelles

### Java/Spring

Les **1 421,9 JH/an** sont une année pleine de référence, avant les réductions explicites. La page présente les neuf activités, mais répète surtout « Année pleine de référence ». Elle donne peu d’éléments pour comprendre leur dimensionnement.

Quelques hypothèses concrètes devraient accompagner les activités : utilisateurs, demandes de support, corrections et campagnes de qualification. Par exemple, le support N1 découle du nombre d’utilisateurs, des demandes annuelles et du temps de traitement. La formule et les paramètres utiles permettraient de vérifier les 203,6 JH/an affichés.

La coordination des prestations annuelles est financée dans le modèle, à hauteur d’environ **59 k€ HT/an** dans la lecture économique courante, sans dimensionnement distinct en JH. Elle n’apparaît pas dans cette page de charges brutes. La frontière du total humain doit donc être explicitée. La même logique que pour les provisions d’intégration peut être utilisée, sans convertir artificiellement ce montant en jours.

Le périmètre de maintenance repose sur les hypothèses de fonctionnement stabilisé de la V1. Leur adéquation au produit professionnel élargi reste à instruire. L’audit ne démontre pas un sous-dimensionnement et ne justifie aucune hausse automatique.

### Microsoft et SAP

Les inclusions et inconnues sont bien conservées : maintenance du standard incluse dans le contrat groupé, maintenance des adaptations Microsoft sans prix récurrent isolé, forfaits SAP documentés, cloud standard inclus avec compléments distincts.

Ces informations peuvent être présentées dans un tableau court de statut plutôt que dans plusieurs grandes fiches. « Inclus », « non chiffré séparément » et « zéro retenu » doivent rester distincts.

Les cinq annuités Microsoft identiques peuvent être regroupées en une séquence courte, avec les périodes conservées. SAP conserve ses variations de capacité et de prix. Les années tarifaires ne doivent devenir ni des années civiles ni une garantie de durée du projet.

Les achats techniques retenus par FLOW et les prix des pièces reçues sont placés dans des sections différentes. Cette séparation est bonne. Une conclusion courte devrait expliquer les services couverts et les coûts restant sans ventilation, au lieu de commencer par des achats complémentaires puis dérouler les contrats.

## Look & feel et parcours

La palette, les icônes et les onglets sont cohérents. Le travail principal porte sur la densité et les points d’appui de lecture.

Sur un mobile de 390 px, la feuille ne laisse que 279 px aux tableaux. Le tableau des lots mesure 590 px, la matrice OSS 760 px et les tableaux d’activités 600 px. Le défilement reste à l’intérieur des tableaux, mais le lecteur ne conserve pas le lot et ses chiffres ensemble. Une fiche par lot, avec référence, proposition et différence côte à côte, serait plus utilisable. Une fiche d’activité pourrait réunir libellé, valeur et justification.

La première métrique du Core commence vers 669 px sur mobile. L’introduction, le parcours des phases, les onglets, le nom répété de l’option et le titre générique repoussent le résultat. Rapprocher le résultat de l’option et supprimer les répétitions aiderait davantage qu’une nouvelle décoration.

Les titres des groupes sont répétés comme titre puis légende du tableau. Le texte sur les provisions de coordination apparaît aussi dans la note du groupe et dans chaque ligne. L’introduction de l’année pleine revient dans la section puis dans « Construction et hypothèses ». Ces répétitions peuvent être retirées en gardant les précisions nécessaires au bon endroit.

Afficher 3 935 JH et 110 JH évite une décimale inutile sur des quantités entières. Garder une précision cohérente pour les valeurs annuelles fractionnaires. Les suffixes Java/Spring répétés dans les noms des lots alourdissent les colonnes alors que l’option est déjà affichée.

## Ordre de mise en œuvre recommandé

1. Corriger la justification des interfaces et le classement du support initial Microsoft.
2. Déclarer près de chaque résultat les activités couvertes, son statut, sa période et les efforts non dimensionnés.
3. Adapter les tableaux mobiles et réduire les répétitions au-dessus des résultats.
4. Mettre la proposition et la matrice OSS dans une lecture d’approfondissement clairement identifiée.
5. Ajouter les accès ciblés aux justifications et preuves des lots, activités et hypothèses.

Cette passe peut conserver les montants, paramètres, décisions, contrats de simulation, icônes et navigation existants.

## Périmètre et contrôles

Les neuf vues ont été parcourues sur ordinateur en 1 280 × 720. Cinq vues ont été contrôlées en largeur mobile de 390 px : Core Java, intégration Java et fonctionnement Java, Microsoft et SAP. Les mesures sont conservées dans `browser-observations.json`, avec une capture du tableau des lots sur mobile.

Neuf tests ciblés de `test_gross_evaluations` ont réussi en 13,318 secondes. Ils vérifient notamment les décompositions, les périodes, les inconnues Buy, l’isolation de la proposition, les empreintes et la conservation du résultat économique après reprise d’un instantané. Ils ne valident pas la justesse des textes explicatifs ni la pertinence économique de toutes les hypothèses. La suite complète n’a pas été relancée pour cet audit.

La revue du modèle est documentaire et arithmétique sur les points décrits. Elle ne constitue pas une nouvelle calibration COCOMO/COSMIC ni une revue indépendante exhaustive des efforts. Les pièces fournisseurs originales n’ont pas été relues intégralement et aucune nouvelle recherche de marché n’a été réalisée.

## Repères d’implémentation

- [Justification associée au montant des interfaces](C:/Dev/FLOW-Etude-Economique/tools/gross_evaluations.py:137) et [hypothèse centrale](C:/Dev/FLOW-Etude-Economique/source/deploiement-groupe.yaml:158).
- [Ancienne justification projetée](C:/Dev/FLOW-Etude-Economique/source/chiffrage/chiffrage-java-spring.yaml:61).
- [Classement documentaire des prestations](C:/Dev/FLOW-Etude-Economique/tools/gross_evaluations.py:86) et [financement du support Microsoft](C:/Dev/FLOW-Etude-Economique/tools/calculate_costs.py:219).
- [Construction des résultats et des preuves à l’écran](C:/Dev/FLOW-Etude-Economique/app/src/GrossEvaluationsPage.tsx:63).
- [Largeurs minimales des tableaux mobiles](C:/Dev/FLOW-Etude-Economique/app/src/grossEvaluations.css:1).
- [Définition canonique de la charge brute](C:/Dev/FLOW-Etude-Economique/source/glossaire.yaml:709).
