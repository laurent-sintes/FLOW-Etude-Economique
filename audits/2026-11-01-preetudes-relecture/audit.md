# Audit des études préalables après réorganisation

**Le parcours et l’identité visuelle sont devenus cohérents. Le principal travail restant consiste à faire ressortir les enseignements avant les preuves.** Les pages rassemblent beaucoup de matière utile, mais plusieurs synthèses décrivent leur contenu et leurs limites sans dire assez clairement ce que l’étude a appris.

Il faut conserver le menu gauche à un seul niveau, les onglets, le fil de navigation et les nouvelles icônes. La prochaine passe devrait se concentrer sur les conclusions, la comparaison des six solutions sur un même écran et la séparation entre lecture courte et dossier détaillé.

Audit du 1er novembre 2026 sur l’application locale. Version contrôlée : `ebbba9d802a29f65b2846483b2dd05f158eac3955c3e1d595d956f95b928c545`. L’application n’a pas été modifiée pendant cet audit.

## Ce qui fonctionne et doit rester

- **La vue d’ensemble remplit son rôle d’orientation.** Ses six questions permettent de trouver le bon dossier. Elle reste courte, autour de 200 mots.
- **Le menu plat, les onglets proches du titre et le fil de navigation donnent des repères stables.** Il ne faut pas réintroduire les sous-menus de gauche.
- **Les icônes et la palette ont maintenant une logique commune.** Une nouvelle refonte graphique générale n’est pas nécessaire.
- **La comparaison reprend la hiérarchie métier native.** Le filtre de sous-domaine sert à une vraie recherche. Les cartes mobiles gardent les six solutions identifiées.
- **L’accès direct au tarif Java fonctionne.** Les tarifs sont présentés comme des observations, avec leur segment, leur date et leur source. Les montants inconnus restent inconnus.
- **La séparation avec les évaluations est maintenue.** La fiche documentaire ERPNext examinée affiche sa mesure de code, sans JH COCOMO ni prix FLOW calculé.
- **Synvance et la cartographie apportent des faits concrets dès leur entrée.** Par exemple, Synvance expose les deux finalistes et l’absence de décision d’achat définitive documentée. Ce niveau de précision constitue un bon repère pour les nouvelles synthèses.

## Corrections prioritaires

| Priorité | Problème observé | Effet sur la lecture | Correction proposée |
| --- | --- | --- | --- |
| Haute | Neuf tableaux de comparaison défilent horizontalement séparément. | Le lecteur ne peut pas garder les six solutions sous les yeux et doit répéter le défilement pour chaque sous-domaine. | Raccourcir les en-têtes aux noms des produits et ajuster les largeurs. Garder versions et assemblages dans le détail. Si un défilement reste nécessaire, utiliser un seul tableau regroupé. |
| Haute | Les encarts « Ce qu’on en retient » restent souvent génériques. | Le lecteur sait ce que contient la page, mais pas ce qu’elle lui apprend. | Écrire une conclusion propre à chaque sujet, suivie de deux ou trois constats sourcés. |
| Haute | Projets, services et catalogue technique sont très longs. | L’information utile se retrouve au même niveau que les preuves, les répétitions et les cas peu exploitables. | Présenter une synthèse comparative courte, puis ouvrir les fiches et les preuves selon le besoin. |
| Haute | Les cartes IA ne donnent pas les résultats observés des études citées. | Elles permettent de lire des réserves, sans comprendre la conclusion des recherches ni les différences entre expériences. | Extraire les résultats des publications primaires avec tâche, population et limite déterminante. Garder les gains retenus pour FLOW dans les hypothèses. |
| Moyenne | Le catalogue de licences provient des stacks de travail envisagées. | Des composants proposés pour FLOW peuvent être compris comme un état neutre et exhaustif du marché. | Rendre explicite le statut du composant. Séparer condition de licence observée et choix d’architecture envisagé. |
| Moyenne | Des champs d’offre sont présentés pour des références OSS sans offre reçue dans cette étude. | « Périmètre de l’offre : information insuffisante » peut laisser croire qu’une offre attendue est simplement mal documentée. | Adapter la fiche à sa nature. Réserver la lecture des offres reçues aux dossiers concernés, sans inventer un prix ni une absence commerciale générale. |

## Revue par page

### Vue d’ensemble

**À conserver, avec une retouche légère.** Les questions d’entrée sont compréhensibles et les destinations sont identifiables. La vue d’ensemble n’a pas besoin d’un tableau supplémentaire de chiffres ou d’un nouveau niveau de menu.

Les cartes reprennent cependant les mêmes textes que les synthèses des pages. Pour cette vue, préférer une phrase courte sur ce que le lecteur trouvera. Garder les conclusions détaillées dans leur dossier. Le lecteur qui cherche un tarif doit atteindre rapidement « Tarifs des prestations », celui qui cherche une étude IA doit reconnaître directement cette destination.

### Intégration et déploiement

**Les références sont utiles, mais leur lecture doit être hiérarchisée.** La page regroupe environ 4 000 mots et 17 400 px de hauteur sur l’écran de bureau contrôlé. Le premier projet commence vers 880 px, après les titres, la synthèse, les plages de référence et le sommaire.

Les plages SAP et Dynamics apportent une information concrète. Leur périmètre et la différence entre contrat, estimation publiée et entreprise composite doivent rester visibles près des montants. En revanche, les quinze fiches complètes n’ont pas besoin d’être lues pour comprendre le résultat de la préétude.

Présenter d’abord quelques références structurantes dans un tableau : nature du cas, périmètre, prix publié, éléments comparables et enseignement. Le sommaire donne ensuite accès aux quinze fiches. Choisir les références structurantes selon leur proximité et leurs preuves, sans favoriser une option Make ou Buy.

Le titre « Projets d’intégration de référence » distinguerait mieux cette page de la phase d’intégration du Framework. Les noms, chiffres et preuves des cas resteraient inchangés.

### Services et exploitation

**C’est l’une des pages à reprendre en priorité.** Elle reprend les quinze projets, alors que onze comportent des observations de fonctionnement chiffrées. Les autres fiches rappellent notamment des prix de mise en œuvre puis indiquent qu’aucun montant annuel n’est isolé.

Les descriptions de convergence, de Finance ou de migration, déjà présentes dans les projets d’intégration, occupent trop de place ici. Elles n’aident pas directement à comparer support, mises à jour, hébergement et licences.

Organiser la première lecture par prestation et période : montant d’origine, durée financée, inclusions et exclusions. Ne pas transformer une dépense pluriannuelle en annuité. Les quatre cas sans prix isolé restent dans les références contextuelles, avec accès à leur fiche complète.

### Construction de produits

**Le volume est raisonnable. L’enseignement positif reste à expliciter.** Les trois programmes sont décrits avec leur devise, leur période et leur périmètre. Mais l’encart initial puis le paragraphe suivant répètent que la part du logiciel n’est pas isolée.

Dire ce que chaque cas apporte : existence préalable d’un produit, refonte, pilotes, communauté ou mise en production. Conserver la limite qui interdit de confondre financement de programme et prix de construction d’un logiciel.

W-RESPONSE est une référence historique de 2004–2007. Si aucun enseignement précis utile à FLOW ne ressort, le garder dans les références historiques détaillées. « Programmes de développement documentés » décrirait mieux le contenu que le titre très général « Construction de produits ».

### Comparaison métier

**La hiérarchie est un progrès, la comparaison simultanée reste difficile sur ordinateur.** Chaque tableau mesure environ 1 239 px pour une zone visible de 913 px. La dernière colonne est hors de la zone visible. Il faut déplacer horizontalement chacun des neuf tableaux pour retrouver la même solution.

Utiliser des noms courts en colonnes : ERPNext, Odoo, Tryton, Axelor, Microsoft et SAP. Les versions et composants restent accessibles dans la fiche. Conserver les groupes de sous-domaines et le seul filtre existant.

La grille contient 103 états « Analogie proposée » sur 168 cellules. Ce constat décrit l’état de l’analyse, pas un score de couverture. Il renforce le besoin d’une synthèse qui distingue les fonctions effectivement documentées, les différences identifiées et les vérifications ouvertes. Ne pas rendre ces états artificiellement positifs.

La première ligne, centrée sur l’éligibilité des prestataires, comporte surtout des informations insuffisantes. Une conclusion métier sourcée doit donc précéder la matrice. Elle pourrait exposer la distinction entre fonctions ERP documentées et scénarios FLOW spécifiques restant à examiner, à partir des constats réels. Aucun JH, coût ou délai d’estimation ne doit être ajouté.

### Fiches des solutions et détail des capacités

**La matière est pertinente pour l’audit expert, mais trop détaillée pour une première lecture.** La fiche ERPNext contrôlée représente environ 1 700 mots. Elle enchaîne composition, singularités, déploiements, mesures de code et six axes fonctionnels.

Commencer par quelques constats propres au produit : ce qu’il fournit, son principal intérêt pour les besoins examinés et les différences importantes. Regrouper ensuite les preuves techniques, mesures et scénarios d’essai dans une profondeur de lecture clairement identifiée.

Réduire les répétitions « Sans objet », « pas une offre RFI » et « parité non démontrée » sur chaque axe OSS. Garder les différences concrètes et les limites qui changent l’interprétation. Dans le détail d’Inventory State Management, les deux capacités hors périmètre peuvent être nommées sans recopier tous leurs besoins dans la lecture principale.

La vue détaillée de Reservation conserve actuellement le titre « Comparaison métier » et ajoute les six axes fonctionnels généraux après le constat sélectionné. Un titre tel que « Reservation · ERPNext » et les seuls axes associés orienteraient mieux le lecteur. Le retour à la comparaison devrait retrouver le sous-domaine et le produit consultés.

### Tarifs des prestations

**La page répond à une question concrète. Sa présentation peut être plus directe.** Le tarif Java, son segment et sa date sont présents. Le lien direct arrive à la bonne section. Les fourchettes correspondant à des segments différents ne sont pas moyennées.

Sur ordinateur, les quatre tableaux mesurent 1 080 px dans une zone visible d’environ 913 px. Sur mobile, les cartes évitent le défilement horizontal mais un seul relevé peut occuper presque une hauteur d’écran.

Afficher d’abord profil, prix, date et mode d’achat. Garder la fiscalité inconnue explicite. Les longues précisions et localisations de source peuvent être accessibles dans le détail. Le relevé Java cite aujourd’hui un repère commun comprenant aussi les pages .NET, ERP et support : donner la localisation propre à l’observation réduirait le bruit sans altérer les pièces.

« Relevé structuré le 2026-11-01 » décrit le travail de rangement de la base. Cette date ne renseigne pas la fraîcheur du prix. Les dates des baromètres et offres sont les informations à mettre en avant.

### Cloud licences et outils

**Le catalogue est documenté, mais disproportionné dans le parcours principal.** Il affiche 36 composants pour les trois options visibles. La page atteint environ 11 900 px sur ordinateur et 24 800 px sur mobile. Sur mobile, les trois tableaux mesurent 500 px pour une zone de 307 px, avec défilement horizontal.

La même formule sur l’absence de redevance et l’exclusion de l’hébergement ou du support revient dans de nombreuses lignes. Les éditions inconnues, licences et descriptions techniques occupent le même niveau que les postes payants à comprendre.

Présenter d’abord les familles de dépenses et les unités facturées. Donner ensuite accès au catalogue complet. Une règle commune peut être expliquée une fois, avec les exceptions par composant. Une donnée inconnue ne doit devenir ni zéro ni « sans objet ».

Préciser que la liste porte sur les composants des stacks de travail envisagées pour FLOW. Le champ source les classe en 22 propositions, 13 éléments issus de l’étude client et un élément à préciser. Le compilateur conserve ces statuts, mais la table ne les affiche pas. Le lecteur doit distinguer documentation commerciale observée, composant envisagé et décision d’architecture.

### Change et indices

**Le contenu est utile, mais répond à deux questions différentes.** La page mélange conversion des projets historiques, indices sectoriels, prévisions macroéconomiques et annonces ponctuelles de prix Microsoft ou AWS.

Mettre d’abord les données utilisées pour relire les projets : devise, période, indice et cas concernés. Regrouper ensuite les observations d’évolution des prix. Une annonce commerciale ponctuelle conserve sa date et son périmètre, sans devenir une tendance générale ni une hypothèse future FLOW.

Les nombreux avertissements sur ce que chaque source ne démontre pas peuvent être remplacés par une phrase positive sur son usage précis. Les limites qui changent réellement cet usage doivent rester visibles.

### Productivité du développement

**C’est la page où l’information essentielle manque le plus.** Les références ISBSG, QSM et OpenLMIS montrent des mesures et leurs périmètres. Les deux cartes IA montrent surtout des limites de transposition, sans résultat d’expérience affiché.

Compléter la lecture des publications citées avant de conclure : résultat observé, tâche, population et conditions de l’expérience. La carte METR parle actuellement de la prudence des hypothèses FLOW, ce qui relève des hypothèses plutôt que du résultat de recherche.

Expliquer les méthodes de mesure au niveau nécessaire. Les points de fonction IFPUG/Nesma ne doivent pas être assimilés aux CFP de COSMIC. Les heures tracées dans des tickets OpenLMIS ne décrivent pas à elles seules l’effort d’un projet complet. Ces distinctions doivent accompagner les données sans imposer une méthode d’estimation sur cette page.

## Cohérence du sens et du vocabulaire

Les titres doivent distinguer un **sujet étudié** d’une **phase à exécuter**. Une fiche de projet de référence n’est pas le dossier d’intégration de FLOW. Un catalogue de composants envisagés n’est pas une étude exhaustive du marché.

Les termes « assiette », « parité », « panier », « stack », « abaque », « cohorte », « P25/P75 » et « RFI » restent visibles dans les nouvelles pages. Les noms officiels des produits et les noms natifs de la cartographie doivent rester fidèles. Le texte d’accompagnement peut être simplifié : « périmètre », « différences avec le besoin », « ensemble de composants », « technologie », « groupe de projets » ou une explication de l’indicateur.

La cartographie reçue contient 88 capacités, dont 84 dans le périmètre comparé. Rendre cette frontière lisible à partir des données natives aiderait le lecteur. Il ne faut pas modifier les noms ni inventer un score de couverture.

Les types de preuve méritent d’être reconnaissables près du fait concerné : offre reçue, contrat attribué, étude composite, documentation produit ou programme de recherche. Cela remplace avantageusement les réserves génériques, sans réintroduire le panneau de provenance supprimé.

## Ordre recommandé pour une prochaine passe

1. **Écrire de vraies conclusions par sujet.** Une conclusion, quelques constats et la conséquence utile pour la suite. L’évaluation chiffrée reste dans son dossier.
2. **Rendre les six solutions visibles ensemble sur ordinateur.** Garder la hiérarchie métier et les cartes mobiles.
3. **Séparer synthèses et fiches détaillées.** Commencer par les projets, les services et les 36 composants techniques.
4. **Compléter les résultats des études IA et clarifier les types de données.** Distinguer observation, référence contextuelle, hypothèse de travail et décision.
5. **Terminer par les retouches visuelles.** Réduire les introductions redondantes, les localisations de sources trop longues et la place prise par les métadonnées secondaires.

## Périmètre des vérifications

La revue couvre la vue d’ensemble, les trois rubriques de projets, la comparaison, une fiche produit détaillée, un détail de capacité, les trois rubriques de coûts et la productivité. Les entrées Synvance et Cartographie ont été revues pour la cohérence de l’ensemble. Les pièces d’origine et l’ensemble des sous-pages Synvance n’ont pas fait l’objet d’une nouvelle analyse exhaustive.

Le rendu a été examiné sur un écran de bureau de 1 280 × 720 et en largeur mobile de 390 px. Les hauteurs et volumes de texte sont des repères observés sur ces vues, pas des indicateurs de qualité automatiques. Aucune nouvelle consultation des publications externes, recalibration ou modification de budget n’a été réalisée.

Points d’implémentation utiles pour préparer les corrections :

- [Comparaison par sous-domaine](C:/Dev/FLOW-Etude-Economique/app/src/MarketComparison.tsx:47) pour les neuf zones de défilement indépendantes.
- [Fiches des projets et services](C:/Dev/FLOW-Etude-Economique/app/src/MarketReferenceDrawer.tsx:43) pour la lecture complète des quinze références dans les deux rubriques.
- [Fiches produit](C:/Dev/FLOW-Etude-Economique/app/src/EssentialViews.tsx:181) pour les champs fonctionnels et commerciaux répétés.
- [Tarifs et achats](C:/Dev/FLOW-Etude-Economique/app/src/MarketCostsPage.tsx:42) pour les sections, catalogues et métadonnées affichés.
- [Projection des preuves](C:/Dev/FLOW-Etude-Economique/tools/prestudy_costs.py:44) pour les cartes IA qui reprennent actuellement leur portée et les composants dont le statut est conservé.
- [Synthèses communes](C:/Dev/FLOW-Etude-Economique/config/application.yaml) pour les textes partagés avec la vue d’ensemble.
