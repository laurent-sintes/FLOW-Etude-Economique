# Audit approfondi — Sources et glossaire

## Mise en œuvre du parcours — 25 octobre 2026

La refonte demandée est appliquée : Synthèse sponsor, bloc Comprendre (Périmètre et options, Offres Synvance, Références de marché, Estimations), Simulations, puis Glossaire. Cet ordre affine la proposition initiale ci-dessous à la demande du sponsor.

- Six séquences Synvance, réponse d’abord, comparaison Microsoft/SAP, conséquence pour FLOW, notions contextuelles et pièces avec émetteur/localisateur. Les tableaux reprennent les postes du moteur en k€ HT, comme les autres vues budgétaires ; aucune copie économique éditoriale.
- Références de marché autonome : conclusions, projets avec nature de prix et unité M€ 2026, fiches de périmètre/preuves, puis tarifs comparables et achats techniques. Les familles Forrester et les alternatives Halifax sont explicites. Les provisions ne deviennent pas des prix observés.
- Glossaire : 61 notions canoniques, familles, alphabet, synonymes recherchables mais repliés, distinction définition/application FLOW et liens directs. RFI, RISE, BTP, OMSA, DOM, ATP/CTP, TMA et K3 ajoutés ; renvois historiques de complexité remplacés par le référentiel métier actif.
- Routes distinctes, reprise des recherches/filtres/sections, retour navigateur, position de lecture et anciens liens `#sources`. Les fragments PDF restent dans l’URL du visualiseur. Le contrat de reprise des simulations reste identique.
- Suppression de la bibliothèque de cartes comme point d’entrée et des tableaux fournisseur répétés dans Périmètre. Estimations renvoie aux références de marché et au guide de méthode. `source/parcours-synvance.yaml` porte le parcours ; `source/offres-synvance.md` devient un index des pièces.

Contrôles : TypeScript, build Vite et absence de contenu métier codé dans React ; 29 tests applicatifs et 10 tests de recherche/navigation/reprise. Les 3 024 valeurs numériques du calcul et les 362 valeurs numériques de la projection sont inchangées. Comparaison des réponses API avant/après : cinq options et quatre horizons, paramètres et contrat de reprise identiques. Références locales du glossaire et du parcours valides.

Contrôle navigateur : menu, prix Microsoft/SAP, passage aux budgets, pièces PDF localisées, notion RISE en volet puis lien direct, retour à la bonne étape, références de marché et fiche AP-HP reprise après rechargement, tarifs et architectures. Un ancien lien `#sources?tab=glossary&q=RISE` conduit au glossaire avec la recherche conservée. Dans une session de test isolée, l’horizon 5 ans et un gain de continuité modifié à 12 % ont survécu au bouton de rechargement après redémarrage du serveur ; la session a ensuite été fermée. La recherche RISE ne remonte plus les sous-chaînes « entreprise » ou « comprises ». Les preuves de travail locales sont dans `tmp/study-app/navigation-*.json` et la capture `tmp/study-app/navigation-synvance.png` ; elles ne calibrent pas le modèle.

La suite du document conserve le diagnostic initial et sa proposition, comme trace d’audit.

25 octobre 2026. Application locale, modèle `fc35406832c0b1c1c55ba58cce4af808a5054469a4e460fa175cdc68b0062bc9`.

## Conclusion

**Le dernier item du menu est organisé comme un répertoire de travail, pas comme une aide à la compréhension.** Il réunit trois besoins de lecture autonomes et plusieurs niveaux d’autorité documentaire. Le lecteur doit choisir un fichier avant de savoir quelle question ce fichier résout.

La séparation en **Comprendre les offres Synvance**, **Références de marché** et **Glossaire** est justifiée. Elle ne suffit pas à elle seule : le contenu de la bibliothèque n’est pas entièrement une explication de Synvance. Les hypothèses Make, la calibration et la simulation relèvent de l’étude FLOW et doivent rejoindre leurs espaces d’usage.

Le sponsor connaît la cartographie SCM. Le parcours doit lui expliquer ce que les propositions apportent, comment leurs prix ont été lus, ce que notre étude ajoute et ce qu’il faut encore faire confirmer. Les pièces originales doivent soutenir cette explication, sans devenir le parcours principal.

Cet audit propose une architecture de lecture et un plan de reprise. Il ne modifie pas l’application, les sources économiques ni les montants.

## Vérifications réalisées

Lecture du composant `Sources`, de la navigation, du visualiseur documentaire et de leurs données ; inventaire des 22 cartes ; lecture de la note Synvance, de la structure de la FAQ, du glossaire et du registre des références. Vérification dans le navigateur des trois sous-espaces, de recherches, d’une note de lecture, d’une fiche de marché et d’un aller-retour de navigation.

Les références de code sont [views.tsx](../app/src/views.tsx), [components.tsx](../app/src/components.tsx), [App.tsx](../app/src/App.tsx), [StudyReading.tsx](../app/src/StudyReading.tsx) et [application.yaml](../config/application.yaml). L’audit porte sur la restitution et son adéquation au besoin sponsor ; il ne constitue pas une nouvelle vérification des prix des pièces fournisseur ou des publications externes. Aucun test de calcul n’a été relancé pour cet audit de lecture.

## Diagnostic factuel

| Constat | Preuve observée | Conséquence |
| --- | --- | --- |
| Trois destinations sous une seule entrée | Bibliothèque, Glossaire et Références de marché partagent `#sources` et le même titre « Vérifier les fondements de l’étude ». | Le menu ne révèle ni le benchmark ni le dictionnaire ; le titre ne décrit pas la tâche courante. |
| Bibliothèque sans progression | 22 cartes : 5 PDF originaux, 6 Markdown et 11 YAML, dont un témoin historique. Même présentation et action « Consulter ». | Une proposition, une convention de calcul et une archive semblent être des lectures de même nature. |
| Recherche limitée aux métadonnées | `views.tsx:37` filtre titre, description et chemin. « RISE » ne retourne rien ; « Synvance » ne retrouve que la note de lecture, sans les propositions Microsoft et SAP. | Une absence de résultat donne une impression trompeuse d’absence d’information. |
| Perte du contexte de lecture | Après Références de marché → Estimations → Sources et glossaire, retour à Bibliothèque avec recherche vide. L’état est local au composant. | Impossible de transmettre un lien vers un sous-espace ou de reprendre naturellement sa lecture. |
| Ouverture technique | Les YAML sont rendus dans un bloc de code ; les pièces PDF s’ouvrent à part. Les cartes n’annoncent ni le format ni une question précise. | Le sponsor passe de la comparaison à la structure interne du modèle. |
| Preuves peu ciblées | Le visualiseur ne navigue pas vers les ancres YAML ; les liens internes Markdown commençant par `#` sont rendus comme du texte. | Un renvoi vers une section ne garantit pas d’arriver à la preuve attendue. |
| Unités différentes dans les références | Synthèse en M€ 2026 ; fiche Forrester ouverte en k€ HT pour la normalisation. | Le lecteur doit convertir mentalement des chiffres de la même page. L’assiette fiscale doit être justifiée par source avant d’ajouter « HT ». |
| Libellé de recherche inadapté | Le bouton d’effacement de recherche porte le nom accessible « Rétablir la référence ». | Une action locale est confondue avec la remise à zéro d’un scénario financier. |

Les fonds documentaires sont utiles et assez riches. Le défaut principal est leur mise en scène : la source est présentée avant l’explication et le statut de la conclusion.

## 1. Comprendre les offres issues de la consultation Synvance

### Ce qui manque aujourd’hui

La note [offres-synvance.md](../source/offres-synvance.md) contient déjà les distinctions essentielles : consultation, réponses fournisseur, projection de comité et hypothèses FLOW. Mais elle reste une carte parmi 22 et débouche rapidement sur des fichiers de chiffrage ou de maintenance.

Il faut également distinguer les rôles : **consultation Synvance**, **proposition Avanade / Microsoft**, **proposition Delaware / SAP**, **projection COPIL** et **interprétation de l’étude FLOW**. Le titre de navigation peut reprendre « offres Synvance » pour être reconnaissable ; la page doit expliciter ces auteurs et objets, sans attribuer à Synvance tous les chiffres calculés aujourd’hui.

### Parcours proposé : des questions, puis les preuves

Les six séquences ci-dessous doivent être navigables librement, avec une synthèse initiale et un sommaire. Ce n’est pas un assistant qui impose six clics avant de montrer une réponse.

| Séquence | Question du sponsor | Restitution attendue |
| --- | --- | --- |
| 1. Ce qui a été demandé | À quelle demande les fournisseurs répondaient-ils ? | Objectif et frontières de la consultation ; écarts matériels avec FLOW. Renvoi à la cartographie connue, sans la redécrire. |
| 2. Ce qui a été proposé | Qu’achète-t-on réellement dans chaque option ? | Microsoft et SAP côte à côte : produits, réalisation client, intégration, services récurrents, inclusions et exclusions. |
| 3. Comment les prix ont été établis | S’agit-il d’un pilote, d’une projection, de lots ou d’un abonnement ? | Origine et portée de chaque montant : pilote Microsoft / projection COPIL ; lots SAP / total imprimé contradictoire ; séquences annuelles documentées. |
| 4. Ce que l’étude FLOW a ajouté ou rapproché | Pourquoi le montant comparé diffère-t-il de la proposition ? | Passage explicite du prix documenté aux compléments, au pilotage applicable et aux achats distincts. Les prestations déjà financées ne sont pas ajoutées. |
| 5. Ce qui reste à confirmer | Quelles incertitudes changent réellement la décision ? | Question précise, effet sur couverture ou budget, preuve attendue et interlocuteur à solliciter. Absence de preuve distincte d’absence de fonction. |
| 6. Ce qu’on peut en conclure | Que permettent ces offres pour décider Make / Buy ? | Conclusions sur le Buy et limites de leur emploi comme repère Make ; liens vers comparaison, estimations et simulations. |

Chaque séquence doit suivre la même chaîne : **réponse courte → comparaison → conséquence pour FLOW → pièce ou extrait probant**. L’explication doit être compréhensible sans ouvrir une source ; la source doit permettre de la vérifier.

Exemples de blocs de lecture utiles :

- « Microsoft : le pilote détaillé ne démontre pas à lui seul le coût et la répétabilité du déploiement Groupe. » Montrer la frontière entre proposition et projection de comité.
- « SAP : le montant retenu correspond aux lignes explicites ; le total imprimé contradictoire reste identifié. » Montrer l’écart sans choisir silencieusement une autre assiette.
- « Un abonnement groupé finance plusieurs services. » Indiquer les inclusions prouvées et les compléments, sans fabriquer de répartition licence / cloud / maintien.
- « Le repère Make est construit par l’étude. » Décrire les retraits et conventions courants en renvoyant à leur calcul ; ne pas le présenter comme une estimation Synvance du développement FLOW.

### Statut visible des informations

Prévoir des mentions compréhensibles : **document fournisseur**, **projection de comité**, **interprétation FLOW**, **hypothèse estimée**, **à confirmer**, **historique**. Une mention doit porter sur une affirmation ou un montant, pas valider globalement un document qui mélange plusieurs statuts.

Pour une preuve : auteur/émetteur, date ou version connue, page PDF et page imprimée si différentes, feuille/cellule pour un questionnaire, ce que la pièce démontre et la limite utile. L’inconnu reste explicite. Les liens « Source 1 » et les chemins de fichiers ne doivent pas être la seule description.

### Corrections éditoriales nécessaires

1. La note Synvance renvoie encore à « Features et Solutions » et aux anciens fichiers de chiffrage. Leur partie fonctionnelle est historique depuis la recalibration. Orienter la lecture active vers la grille SCM et `recalibration-metier.yaml`, en conservant les références fournisseur encore utilisées.
2. La note indique que les compléments « peuvent recouvrir du Core déjà financé ». Elle doit distinguer le retrait des compléments génériques déjà effectué dans le repère Make des incertitudes restantes de transférabilité des lots. Ne pas laisser penser que toutes les conventions antérieures sont encore actives.
3. La FAQ de 30 questions mêle explications actuelles, corrections anciennes, anciens libellés et descriptions d’Excel. Par exemple les questions sur les « Forfaits RFI », les cellules fusionnées ou le statut « OK » relatent l’histoire de la restitution. Extraire leurs explications utiles dans le parcours courant ; conserver le contexte historique en second niveau.
4. Les questionnaires Microsoft et SAP figurent dans `offer_documents` et dans les liens de la note, mais pas parmi les 22 cartes. Le registre de preuves doit donc inventorier les pièces effectivement utilisées, pas seulement les cartes affichées.

## 2. Références de marché : une destination autonome

La synthèse de marché est déjà l’un des contenus les mieux orientés vers une question : elle expose les conclusions avant les projets et refuse d’assimiler les plages publiques à une borne FLOW. **Il faut conserver cette synthèse**, la rendre directement accessible et améliorer les fiches qui l’étayent.

Le registre contient **15 références**, principalement relatives à l’intégration ERP. Ce n’est pas encore une restitution de toute l’étude de marché des coûts du build, des prestations et des moyens techniques. La nouvelle entrée doit annoncer clairement ce que chaque section couvre.

### Structure proposée

1. **Ce que le marché nous apprend**, avec conclusion par sujet et usage autorisé dans l’estimation.
2. **Projets d’intégration**, avec filtres par plateforme, nature du prix, contexte et assiette comparable.
3. **TJM et dispositifs de prestation**, à restituer depuis les références déjà présentes dans les stacks : profil, France/région, expérience, freelance/ESN et date. Ne pas recopier les tarifs dans un nouveau catalogue indépendant.
4. **Achats et services techniques**, à partir des composants et sources déjà documentés : licence, abonnement, cloud, iPaaS, inclusions et provisions. Une source catalogue ne devient pas une facture Beaumanoir.

Les gains IA et plages de JH non étayés par un benchmark doivent rester présentés comme hypothèses d’ingénierie dans Estimations, avec accès à leurs éventuels appuis. Les guides Thoughtworks et autres méthodes de décision ne doivent pas être mélangés aux projets utilisés comme contrepoints de coûts.

### Exploiter les données de qualité déjà présentes

Le YAML distingue nature du prix, qualité de sa source, famille de sources, assiette externe et niveau de transposition FLOW. Les fiches actuelles n’affichent pas ces champs structurés ; certains indices apparaissent seulement dans le nom du projet ou une explication.

Présenter d’abord des catégories explicites : **contrat attribué**, **estimation avant achat**, **entreprise composite**, **option non retenue**, **témoignage sans coût publié**. Un contrat attribué ne démontre pas une dépense finale réalisée. Les cinq composites Forrester ne doivent pas apparaître comme cinq observations clients indépendantes. Les deux options Halifax Water correspondent à un même contexte de sélection, pas à deux déploiements réalisés.

Conserver deux appréciations séparées : qualité du prix publié et possibilité de le rapprocher de FLOW. Le registre indique actuellement **zéro référence éligible** à la variance au périmètre FLOW ; ne pas afficher une moyenne générale ou une note de confiance unique qui masque ce fait.

Choisir **M€ 2026** pour les comparaisons normalisées de projets, en gardant prix historique, devise et date dans le détail. Afficher les calculs et hypothèses de conversion en second niveau. Les valeurs non publiées restent sans montant, jamais zéro. Une section TJM possède naturellement son unité €/JH, annoncée séparément.

## 3. Glossaire : une destination et une aide contextuelle

Le glossaire contient **53 notions** dans l’ordre du YAML, sans classement visible ni accès alphabétique. Il inclut des libellés de tableaux et synonymes historiques utiles à la compatibilité, mais peu de repères sur les produits et sigles rencontrés dans les offres.

### Ce qu’il faut reprendre

- Ajouter une entrée de menu et des liens directs vers chaque notion ; permettre l’ouverture contextuelle depuis une phrase sans perdre la page de départ.
- Proposer un accès alphabétique et quelques familles lisibles : métier SCM, produits et architecture, coûts et contrats, estimation et projection.
- Distinguer **définition générale**, **sens dans l’étude FLOW** et, si utile, **exemple ou confusion fréquente**. La définition actuelle de PaaS est surtout celle du poste d’achat séparé ; ce n’est pas une définition complète de PaaS. Même distinction pour l’iPaaS.
- Actualiser les références de « Feature », « Solution », « Couverture » et « Points » : elles pointent encore vers les anciens Features/Solutions CSF. Les définitions ne doivent pas faire croire que ces anciens pourcentages calibrent les charges actives.
- Vérifier puis compléter les sigles nécessaires au parcours : RFI, RISE, BTP, OMSA, DOM, ATP/CTP, TMA, ainsi que les produits et acteurs utiles, dont K3. Ces entrées sont absentes en tant que notions dédiées dans l’inventaire actuel. Leur définition doit venir des sources appropriées, pas d’une déduction du libellé.
- Masquer par défaut les anciens libellés ; les conserver comme synonymes de recherche. Ne pas présenter chaque intitulé historique comme une notion supplémentaire à apprendre.

Les noms canoniques restent dans `glossaire.yaml`. Les prix restent dans leurs sources économiques. Une nouvelle page Glossaire ne doit pas créer son propre dictionnaire dans React ou un deuxième fichier indépendant.

## Menu cible et partage des responsabilités

Ordre proposé :

1. **Synthèse sponsor** — arbitrer et préparer la prochaine décision.
2. **Comprendre les offres Synvance** — comprendre la consultation, les propositions et leur interprétation.
3. **Périmètres et responsabilités** — comparer les cinq options sur la cible FLOW, y compris Make / Buy hors coûts.
4. **Estimations** — comprendre charges, tarifs, hypothèses et plages.
5. **Simulations** — modifier les paramètres et comparer les projections.
6. **Références de marché** — confronter les hypothèses aux éléments externes.
7. **Glossaire** — comprendre les notions et retrouver leur sens commun.

Le chapitre Synvance est propriétaire de l’explication des **offres reçues et de leur retraitement**. Périmètres et responsabilités reste propriétaire de la **comparaison courante des cinq alternatives**. Les deux utilisent les mêmes objets de couverture et de coûts ; il ne faut pas recopier leurs tableaux dans des contenus éditoriaux indépendants.

Les sources deviennent un accès transversal depuis les affirmations, accompagné éventuellement d’un inventaire de pièces en annexe du parcours Synvance. **L’inventaire reste disponible pour vérifier ; il cesse d’être la porte d’entrée.** La méthode FLOW rejoint Estimations et les conventions de projection rejoignent Simulations. Il n’est pas nécessaire d’ajouter une huitième rubrique généraliste « Documentation ».

## Destination des 22 cartes actuelles

Cette table est un plan de navigation, pas une demande de déplacement ou de suppression des fichiers.

| Carte actuelle | Destination de lecture | Rôle restant du fichier |
| --- | --- | --- |
| Périmètre de la consultation | Synvance, séquence 1 | Preuve originale ciblée |
| Expression des besoins | Synvance, séquence 1 | Preuve originale ciblée |
| Lire les propositions Synvance | Parcours Synvance | Base éditoriale à actualiser et structurer |
| Écarts de périmètre | Périmètres ; renvoi Synvance | Justification commune, sans duplication |
| Questions des sponsors | Réponses contextualisées par espace | Référence explicative à réorganiser |
| Projets et benchmarks publics | Références de marché | Registre des preuves publiques |
| Glossaire de référence | Glossaire | Markdown dérivé ; YAML canonique |
| Guide du modèle | Annexe de méthode dans Estimations | Guide technique secondaire |
| Conventions d’investissement | Simulations | Entrées et justification des règles |
| Calibration des coûts | Estimations | Hypothèses courantes ; anciennes ancres signalées |
| Hypothèses d’inflation | Simulations ; appui marché | Paramètres canoniques et sources |
| Comité de pilotage 5 | Synvance, séquence 3 | Projection et durées documentées |
| Proposition Avanade / Microsoft | Synvance, séquences 2–3 | Pièce fournisseur originale |
| Proposition Delaware / SAP | Synvance, séquences 2–3 | Pièce fournisseur originale |
| Lecture Socle / Intégration / Run & MCO | Périmètres et responsabilités | Interprétation commune des achats |
| Référentiel et grille de complexité SCM | Périmètres ; renvoi Estimations | Référence métier active |
| Critères de complexité et réemploi | Estimations | Méthode et limites de calibration |
| Synthèse de décision sponsor | Synthèse sponsor | Contenu de l’accueil, pas carte documentaire |
| Arbitrages Make / SAP / Microsoft | Synthèse et Périmètres | Contenu de comparaison partagé |
| Calibration métier des cinq stacks | Estimations | Source active des travaux résiduels |
| Référence avant recalibration | Historique dans Estimations | Témoin explicitement daté |
| Preuves de la recalibration | Estimations ; références contextuelles | Registre technique, non devis |

## Contrat de contenu et conséquences techniques

### Contenu YAML, sans nouvelle vérité économique

Pour la mise en œuvre, un fichier de lecture Synvance pourrait porter les séquences, questions, conclusions, statuts, liens vers des objets du modèle et références précises aux pièces. Ce fichier n’est pas créé par cet audit. Les montants viendraient des YAML économiques et du moteur ; les paragraphes feraient référence aux résultats résolus au moment de l’affichage.

Réutiliser `source/lecture-comparative.yaml`, `source/ecarts-perimetre-flow-rfi.md`, les catalogues économiques et les registres de preuves. Si la note Markdown et des réponses FAQ sont converties en contenu structuré, choisir explicitement la source canonique et générer ou référencer les autres restitutions. Ne pas maintenir trois explications éditées séparément du même montant.

Le catalogue `ui.documents` peut subsister comme registre de titres et d’accès ; son ordre ne doit plus définir le parcours sponsor. Enrichir les métadonnées utiles aux preuves et vérifier leurs liens. Les champs de statut, rôles, sections et synonymes viennent également des YAML.

### Navigation et retour aux preuves

Prévoir des routes stables pour les trois destinations, leurs sections, les références et les termes. Conserver recherche et filtres dans l’URL ou un état restaurable. Traiter explicitement les anciens liens `#sources`, le retour navigateur et le bouton de rechargement du serveur. Un retour depuis une preuve doit restituer la question et la position précédentes.

Le visualiseur doit distinguer lecture guidée, document explicatif et source brute. Les ancres doivent conduire à la section voulue ; pour PDF/XLSX, afficher un localisateur lisible même si le visualiseur ne sait pas positionner automatiquement la page ou la cellule. Le texte d’un bouton doit annoncer « Lire l’explication », « Voir la pièce » ou « Télécharger », selon l’action réelle, avec les libellés dans YAML.

## Priorités et critères de réception

**P1 — confiance dans la lecture.** Séparer source, projection et hypothèse ; actualiser les renvois historiques ; construire le parcours Synvance ; afficher la nature des références de marché. C’est ce qui évite une interprétation erronée des montants ou de leur preuve.

**P2 — accès et continuité.** Créer les trois entrées, assurer les liens directs et le retour au contexte, rendre la recherche pertinente, unifier les unités de projets et compléter le glossaire. Le déplacement des cartes seul ne répond pas au besoin.

Vérifications de réception proposées :

1. En arrivant sur Synvance, le sponsor comprend qui a demandé, proposé, projeté et estimé ; il voit une réponse avant une liste de pièces.
2. Il peut distinguer le pilote Microsoft de la projection Groupe sans ouvrir un YAML et retrouver la pièce correspondante.
3. Il peut expliquer le traitement de la contradiction SAP et les inclusions des abonnements, sans ventilation inventée.
4. Il identifie ce que FLOW ajoute aux propositions et ce qui demeure conditionnel ; aucun changement de prix n’est induit par la réorganisation.
5. « RISE » conduit à une explication et ses preuves ; « Synvance » permet de retrouver le parcours et les deux propositions. La recherche précise son périmètre.
6. Une fiche marché distingue contrat, estimation, composite ou absence de prix ; les comparaisons normalisées utilisent une unité cohérente.
7. Les tarifs de marché restent comparables en profil, région, expérience et mode d’achat ; les inconnues ne deviennent pas des moyennes prouvées.
8. Une notion possède un lien stable et une définition actuelle ; les anciens noms restent recherchables sans dominer la page.
9. Retour navigateur et rechargement conservent page, section et contexte, ainsi que les paramètres de simulation compatibles.
10. Les chiffres, règles de calcul et inclusions sont identiques avant/après ; toute nouvelle affirmation est sourcée ou explicitement qualifiée d’interprétation.

La prochaine étape pertinente est donc une **refonte du parcours de compréhension et de la hiérarchie des preuves**, accompagnée de la séparation des deux outils de consultation. La connaissance existe largement ; il faut la rendre lisible dans l’ordre des questions du sponsor.
