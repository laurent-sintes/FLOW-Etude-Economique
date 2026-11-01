# Audit du dossier économique pour une lecture sponsor

**Le dossier peut être ramené de six entrées à trois : Comparer les options, Comprendre les coûts et Hypothèses retenues.** La comparaison doit devenir son entrée. Les montants, les dates de service et les principales limites de périmètre doivent être compris avant les détails de calcul.

L’application actuelle contient les données nécessaires, mais les disperse entre six pages et plusieurs approfondissements. Les trois premières pages représentent environ 10 500 mots avant même l’entrée « Comparer ». La page « Évaluations économiques » dépasse 6 200 mots. La première question du sponsor ne doit pas nécessiter ce parcours.

Audit du 1er novembre 2026, version locale `dca575e134ea039f33041bb1ec389864cc1659ebcc87c9146aa2008646d12800`. Aucun changement de l’application, des hypothèses ou des montants pendant l’audit.

## Cadre demandé

Les hypothèses sont établies pour la référence du dossier et **non modifiables dans l’application**. Le lecteur doit pouvoir connaître les coûts, comprendre leur composition et comparer Java/Spring, Microsoft/K3 et SAP. Le nombre de pages doit diminuer. Le dossier économique est le parcours principal du sponsor.

Le choix d’un horizon, d’une option ou d’un niveau de détail reste un réglage de lecture. Il ne change ni les tarifs, ni les charges, ni les dates, ni les taux retenus. Une hypothèse fixe dans l’interface garde sa provenance et son statut d’hypothèse d’étude. Elle ne devient pas un engagement fournisseur.

## Constats prioritaires

| Priorité | Constat | Conséquence | Recommandation |
| --- | --- | --- | --- |
| Haute | « Simuler » expose encore onze champs numériques modifiables dans le contexte Java observé. Les hypothèses renvoient à ces réglages. | Le dossier ne respecte pas la nouvelle consigne de lecture seule. | Retirer l’édition du parcours et des anciennes routes directes. Présenter les valeurs établies en texte ou tableaux. |
| Haute | Les premiers montants arrivent vers 816 px sur ordinateur dans « Se projeter », et au-delà de 1 100 px sur mobile dans les deux vues comparatives. | Le premier écran du sponsor ne montre aucun coût. | Afficher les trois montants et leurs repères de temps immédiatement après un en-tête compact. |
| Haute | Les durées de service complet diffèrent fortement entre les options. | Un classement par dépenses seules peut être interprété comme une comparaison de services équivalents. | Placer date de service complet et années de service au même niveau visuel que le cumul. |
| Haute | La comparaison à trois ans contient un bloc de coût total de construction, indépendant de l’horizon. | Deux périmètres monétaires se côtoient dans une même fiche. | Retirer ce bloc de la comparaison et le conserver dans les détails du budget complet. |
| Haute | Les budgets, justifications, hypothèses et cumuls sont séparés entre trop d’entrées. | Le lecteur doit reconstruire le raisonnement et revenir entre les pages. | Trois pages avec un passage direct du montant à son explication. |
| Moyenne | Les détails Core, les matrices de méthodes et les projets de référence occupent la lecture économique principale. | L’information déjà disponible dans les charges et préétudes ralentit la lecture financière. | Conserver les conclusions financières et les preuves contextualisées, avec renvois ciblés vers leurs propriétaires. |

## Ce qui fonctionne

Les trois options visibles sont cohérentes avec le périmètre actuel. Les montants sont affichés en k€ HT sans décimales. Les pages distinguent budget initial, base annuelle et dépenses cumulées. Les hypothèses détaillées sont déjà consultables sans saisie directe sur leur propre page.

« Se projeter » expose les trois cumuls au même horizon et depuis le même début de projet. Les dates de service complet, les années de service et les financements initiaux restant à engager sont disponibles. Ces informations doivent être rapprochées des chiffres, pas recalculées selon une autre convention.

Les montants examinés se réconcilient entre l’évaluation économique, la comparaison et les projections. L’audit ne met pas en évidence une erreur arithmétique sur ces contrôles. Le problème principal est la présentation des périmètres, du temps et des hypothèses.

## Parcours proposé : trois pages

### 1. Comparer les options

**Question : quelles dépenses, pour quelle trajectoire de mise en service ?**

Cette page devient l’entrée du dossier économique. Elle présente les trois options ensemble, avec dix ans sélectionnés initialement, conformément à la référence actuelle. Les horizons 3, 5, 7 et 10 ans peuvent rester disponibles comme filtres de lecture.

Le premier bloc doit rapprocher trois données : cumul à l’horizon, mois de service complet et années de service complet à cet horizon. Une conclusion courte explique les principaux écarts. La décomposition résumée permet ensuite d’ouvrir le détail du coût d’une option.

Exemple de contenu avec les chiffres courants, à dix ans depuis le début du projet :

| Repère | Java/Spring | Microsoft/K3 | SAP |
| --- | ---: | ---: | ---: |
| Dépenses cumulées | 12 069 k€ HT | 21 627 k€ HT | 37 697 k€ HT |
| Service complet à partir du mois | 78 | 44 | 36 |
| Années de service complet à dix ans | 3,5 | 6,3 | 7,0 |

Ces chiffres décrivent les hypothèses courantes. Ils ne suffisent pas à établir qu’une option est le meilleur choix. Les ouvertures progressives doivent rester visibles dans le calendrier détaillé. Le service complet ne doit pas être confondu avec la première ouverture.

À cinq ans, Java affiche environ 5 677 k€ de dépenses, aucun service complet et encore 2 494 k€ de financements initiaux et transitoires estimés. Microsoft et SAP ont respectivement 1,3 et 2 ans de service complet. Ce cas montre pourquoi le calendrier doit accompagner le prix.

Il ne faut pas fabriquer un coût « par année de service » en divisant simplement le cumul : le cumul contient des investissements et des dépenses de transition. Une comparaison à durée d’exploitation identique demanderait une convention de calcul supplémentaire.

### 2. Comprendre les coûts

**Question : que couvre chaque montant et comment est-il constitué ?**

Une option à sélectionner, puis une lecture courte de ses coûts :

- Construction ou sélection, intégration et déploiement.
- Dépenses techniques et services pendant le projet.
- Fonctionnement à pleine capacité et contrats fournisseurs.
- Échéancier et cumul, avec une période explicitement annoncée.

Les regroupements doivent venir des natures de coût existantes. Une composante inconnue d’un contrat groupé reste incluse ou non ventilée, sans faux zéro ni ventilation inventée.

Pour un montant, le lecteur doit trouver ce qui est financé, son origine et son passage dans le temps. Une explication contextualisée peut relier travaux retenus, valorisation et dépense projetée. Les charges par rôle ne doivent pas être ramenées artificiellement à un tarif Java unique.

Les détails monétaires ont leur place ici. Les matrices COCOMO/COSMIC, les hypothèses de taille de code et les justifications fonctionnelles restent dans les charges brutes ou le Framework. Les prix observés et les études de projets restent dans les préétudes. Les montants des pièces reçues restent distingués des montants retenus par le modèle.

L’échéancier doit répondre à la question « combien pendant les prochaines années du projet ? ». Le graphique actuel présente quinze ans pour une seule option même lorsque l’horizon supérieur est changé. La note l’explique, mais cette double portée est peu naturelle. La future page doit annoncer et contrôler clairement la période affichée, puis proposer le plan complet en approfondissement.

### 3. Hypothèses retenues

**Question : sur quelles valeurs repose la comparaison ?**

Cette page devient une fiche de référence lisible, sans champ de saisie, bouton de modification ou invitation à tester un autre réglage.

Mettre en avant les hypothèses qui déterminent les dépenses ou le service : périmètre financé, calendriers des trois options, volumes d’intégration et de fonctionnement, tarifs et coordination, achats techniques, séquences fournisseurs et indexation.

Chaque hypothèse donne sa valeur, son périmètre, sa provenance et sa date utile. La justification courte indique pourquoi elle est retenue. Les preuves détaillées restent accessibles à la demande. Les prix de marché observés dans les préétudes ne doivent pas être présentés comme les tarifs choisis pour le modèle sans expliquer ce choix.

Le calendrier mérite une place prioritaire. Les 48 mois de construction Make et les dates de service complet à 78, 44 et 36 mois influencent fortement la comparaison, mais ne figurent pas clairement dans la synthèse actuelle des hypothèses. Le caractère provisoire du calendrier global reste identifiable. Le verrouillage de l’interface ne le transforme pas en calendrier validé de réalisation.

Les hypothèses d’abonnement doivent être compréhensibles. Par exemple, la référence SAP utilise les prix des années fournisseur 4 et 5, puis les conventions de prolongation. Ce choix n’est pas équivalent au premier palier tarifaire de la pièce d’origine. Il doit être annoncé avec son périmètre et sa justification.

La répartition Build/Run, qui ne modifie pas le montant du poste, et les anciens diagnostics n’ont pas à occuper la synthèse sponsor. Ils restent dans les explications méthodologiques ou les preuves concernées.

## Sort des pages actuelles

| Page actuelle | Destination proposée |
| --- | --- |
| Des préétudes aux budgets | Conclusions utiles dans les coûts et points de périmètre à confirmer. Les rapprochements détaillés restent accessibles comme preuves. |
| Hypothèses retenues | Conservée, raccourcie et entièrement en lecture seule. |
| Évaluations économiques | Devient la matière de « Comprendre les coûts ». Les détails de charges et de méthodes renvoient vers leurs dossiers. |
| Comparer | Fusionnée avec la comparaison des cumuls pour former l’entrée « Comparer les options ». |
| Se projeter | Cumuls comparatifs dans « Comparer ». Échéancier et détails annuels dans « Comprendre les coûts ». |
| Simuler | Retirée du parcours économique et désactivée pour l’édition du lecteur. |

Les anciennes adresses doivent conduire à la bonne destination. Les simulations et fichiers personnels existants ne doivent pas être effacés pour retirer l’édition. Les hypothèses et résultats du dossier lisible restent ceux de la référence établie.

Retirer seulement l’entrée « Simuler » du menu serait insuffisant : les liens « Modifiable », les appels à tester les hypothèses et les anciennes routes restent aujourd’hui actifs. Le composant Simulations est aussi monté, masqué, sur les autres pages. Cette dépendance doit être traitée dans la mise en œuvre du parcours fixe, sans supprimer les contrats de données nécessaires à la compatibilité historique.

## Clarté des montants et du périmètre

Trois notions doivent rester immédiatement distinguées : **budget initial**, **base annuelle** et **dépenses cumulées à une date**. Elles répondent à des questions différentes et ne s’additionnent pas librement.

Le bloc Core Domain/Support illustre le problème actuel. À trois ans, Java affiche 3 209 k€ de dépenses cumulées, dont 3 149 k€ de construction déjà engagés. La même fiche insère ensuite 2 441 et 1 758 k€ de construction totale, soit 4 199 k€, avec une note sur le périmètre complet. Les valeurs se réconcilient chacune sur leur objet, mais leur juxtaposition demande un effort inutile. Cette ventilation relève du détail de construction, avec le budget complet clairement identifié.

La base annuelle actuelle est d’environ 932 k€ pour Java, 1 986 k€ pour Microsoft et 2 583 k€ pour SAP. Elle ne doit pas être multipliée simplement par dix pour retrouver les cumuls. Les activations, transitions, séquences commerciales et indexations interviennent dans le calendrier.

La convention monétaire est composite : prix des pièces 2025 conservés et tarifs/provisions des sources courantes. La présentation doit expliquer l’application des indexations. Elle ne doit pas laisser croire à des prix tous normalisés en euros constants de la même année.

Les exclusions matérielles restent proches de la comparaison : temps interne, transformation organisationnelle, maintien des SI historiques et décommissionnement ne sont pas chiffrés. Leurs coûts peuvent dépendre du calendrier. Le montant affiché ne constitue donc pas, à lui seul, le coût complet de toute la transformation du Groupe. SAP conserve aussi un périmètre Finance à signaler dans sa lecture.

Les qualifications fonctionnelles restant ouvertes et les compléments non dimensionnés gardent leur statut. Une donnée inconnue ne devient pas zéro. Les conclusions du rapprochement des financements doivent distinguer les travaux déjà financés et les écarts encore ouverts, sans la formule générique « tout reste à rapprocher ».

## Exigences visuelles

Le langage graphique FLOW, les icônes de phase et les logos existants constituent une base cohérente. La priorité est la hiérarchie de l’information.

Le premier écran doit montrer les trois options et leurs principaux montants. Réduire l’en-tête et les préambules répétés. L’encart global Java et les paragraphes de périmètre ne doivent pas précéder systématiquement tous les résultats. Les points propres à une option se placent auprès de celle-ci, avec un poids visuel comparable.

Sur ordinateur, privilégier une grille alignée avec critères en lignes et options en colonnes. Le prix, son unité, la période et le service complet doivent être rapprochés. Une décomposition visuelle n’est utile que si ses composants portent sur la même période et le même type de montant.

Sur mobile, rapprocher les trois options par critère. Éviter trois longues fiches successives, dont une fiche Java plus haute à cause d’une ventilation architecturale. Les tableaux actuels des hypothèses font jusqu’à 740 px pour 307 px disponibles. Ceux des évaluations atteignent 980 px pour environ 337 px disponibles. La comparaison doit se lire sans défilement horizontal.

Le diagramme annuel actuel déborde aussi dans sa zone mobile. Une vue adaptée peut présenter les dépenses et leurs repères de temps, avec un tableau équivalent accessible. Les informations essentielles ne doivent pas dépendre d’un survol.

Les aides « D’où vient ce chiffre ? » doivent expliquer le montant sélectionné. L’aide annuelle observée décrit seulement la somme des catégories, puis renvoie à trois autres pages. Une bonne aide montre option, période, composition et hypothèses déterminantes avant de proposer les preuves.

Les mots « assiette », « agrégats », « sept structures », « Core Domain » et « transpositions » ne doivent pas structurer la première lecture. Les libellés parlent de dépenses, prestations, achats et périodes. Les unités restent en k€ HT, avec des prix annuels marqués « /an ».

Des résidus Rust apparaissent encore dans la synthèse des moyens, et .NET dans un repère de source commun aux tarifs. Les textes courants doivent rester centrés sur Java, Microsoft et SAP. Les pièces historiques originales ne sont pas à réécrire.

Le menu économique n’a pas besoin de sous-menu imbriqué. Un accès direct à la comparaison depuis la vue d’ensemble faciliterait l’arrivée du sponsor, avec trois destinations stables ensuite.

## Critères de réception de la future refonte

1. Trois entrées économiques principales, avec la comparaison en premier et un accès direct depuis l’accueil existant.
2. Aucune hypothèse numérique modifiable, y compris depuis les liens et anciennes routes. Les sélecteurs de lecture restent autorisés.
3. Trois totaux comparables au même horizon, avec le service complet et la période annoncés au même endroit.
4. Passage direct d’un montant à sa composition et à ses hypothèses, sans téléchargement obligatoire pour le comprendre.
5. Distinction explicite entre budget complet, dépense à date, base annuelle, prix reçu et valeur retenue.
6. Rendu bureau et mobile lisible, sans contenu essentiel uniquement en survol et sans tableaux comparatifs qui débordent.
7. Montants, annuités, calendriers et contrats de simulation conservés pendant la réorganisation. Toute révision économique reste une décision distincte.

## Périmètre des vérifications

Les six pages principales ont été examinées en 1 280 × 720 et en largeur mobile de 390 px. Cinq approfondissements ont été échantillonnés : tarifs, diagnostics, construction Make, transpositions des quinze projets et fiche Master Data. L’aide de la base annuelle a été ouverte. Les horizons 3, 5 et 10 ans ont été contrôlés dans la projection, avec retour à dix ans.

La revue arithmétique des trois options vérifie la concordance des budgets d’intégration, la somme des postes annuels, les totaux par horizon et leur égalité avec les dépenses annuelles cumulées. Aucun écart supérieur au centime n’a été constaté sur ces contrôles. Les hypothèses elles-mêmes et l’équivalence fonctionnelle des solutions n’ont pas fait l’objet d’une nouvelle validation indépendante.

Aucun champ de coût ou d’hypothèse n’a été modifié. Aucune nouvelle recherche de prix ni recalibration n’a été réalisée. Les suites de tests du code inchangé n’ont pas été relancées pour cet audit.

Les observations et captures sont conservées dans `browser-observations.json`, `verification.json`, `bureau-premier-ecran.png` et `mobile-premier-ecran.png`.
