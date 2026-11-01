# Audit de cohérence des études préalables

Mise en œuvre terminée. Voir le [compte rendu des changements](C:/Dev/FLOW-Etude-Economique/audits/2026-11-01-etudes-prealables-ui-ux/mise-en-oeuvre.md). Les constats ci-dessous décrivent l’état avant réorganisation.

Le lecteur doit pouvoir comprendre ce qu’apporte chaque étude et retrouver directement une information précise. L’organisation actuelle masque des sujets différents derrière les mêmes entrées de menu. Elle mélange aussi des données documentaires et des résultats d’estimation dans les fiches des solutions.

**Priorité : sortir tous les chiffres d’estimation de la comparaison, rendre chaque sujet accessible dans le menu et remplacer les longues introductions par une synthèse courte. La seule voie Make visible sera Java/Spring.** Une page d’ensemble est utile pour orienter la lecture, à condition de ne pas recopier les dossiers.

Audit du 1er novembre 2026. Périmètre éditorial : les trois nouvelles préétudes. Repères Synvance et Cartographie métier conservent leur contenu. Le changement de nom du groupe les concerne. Ce document porte les constats et la proposition de réorganisation. Il ne modifie pas l’application.

## Constats prioritaires

| Priorité | Constat vérifié | Conséquence pour le lecteur | Correction cible |
| --- | --- | --- | --- |
| Haute | Les fiches des solutions affichent un effort COCOMO, des JH par composant et une conversion en mois-personne. | Une préétude semble déjà produire l’estimation. | Conserver les observations et mesures techniques. Déplacer les résultats calculés vers les évaluations. |
| Haute | Trois entrées de menu donnent accès à dix rubriques locales. Le menu ne représente que la page parente. | Productivité, achats et services sont difficiles à retrouver lors d’un retour dans l’application. | Afficher les sujets différents comme sous-entrées du menu. Réserver les onglets aux variantes d’un même sujet. |
| Haute | 103 des 168 cellules de la comparaison affichent « À rapprocher ». Les 168 couvertures complètes restent inconnues. | Le lecteur confond revue fonctionnelle et utilisation d’une référence pour estimer. | Expliquer ce qui a été rapproché, ce qui reste à vérifier et ce qui relève d’une décision de chiffrage. |
| Haute | Les 28 Business Areas sont rendues à plat. | La grille manque de structure et devient difficile à parcourir. | Regrouper selon la hiérarchie métier native, sans nouveau classement. |
| Moyenne | La synthèse des projets précède les onglets sur les trois rubriques. | L’accès aux services et aux programmes arrive après une longue introduction répétée. | Mettre les accès avant le détail et limiter la synthèse initiale à un encart court. |
| Moyenne | Les prix sont filtrés par défaut sur Java. Le choix du profil et de la technologie reste dans l’état local du composant. | Une partie du contenu est masquée. Une sélection ne dispose pas d’un lien propre à conserver. | Présenter les tarifs regroupés en lecture continue, avec des ancres stables. |
| Moyenne | « Provenance et état de la préétude » occupe un panneau répété. | Le préambule retarde l’accès aux informations utiles. | Retirer le panneau. Garder les dates et sources près des faits qu’elles documentent. |
| Moyenne | « OSS » apparaît sans explication et sans notion dédiée dans le glossaire. | Le sens de la comparaison peut être mal compris. | Définir le terme à sa première apparition et ajouter une entrée canonique. |

Les volumes de cellules décrivent l’état documentaire actuel. Ils ne constituent ni une mesure de qualité ni un score de couverture.

## Périmètre actif centré sur Java

**Demande du 1er novembre 2026 : retirer .NET et Rust de l’application et se concentrer sur Java pour la construction Make.** Microsoft et SAP restent les deux alternatives Buy de la comparaison. Le parcours économique cible donc Java/Spring, Microsoft et SAP.

La suppression concerne les choix visibles, les tableaux et graphiques de comparaison, les tarifs spécifiques, les composants techniques, les paramètres et les simulations. Les coûts transverses utiles à Java restent documentés. Les mentions techniques factuelles des produits Microsoft et SAP ne sont pas réécrites comme si ces produits utilisaient Java.

Les quatre logiciels à code source ouvert restent des références documentaires comparées. ERPNext, Odoo, Tryton et Axelor ne deviennent pas quatre voies Make supplémentaires. Leur rôle documentaire est distinct du choix de la technologie de construction de FLOW.

Les anciens liens .NET et Rust doivent conduire à une destination compréhensible. Une sauvegarde historique ne doit pas être silencieusement transformée en scénario Java. Lors de l’implémentation, conserver les fichiers personnels et expliciter les possibilités de consultation ou de reprise. La conservation des données historiques dans la base ne doit pas réintroduire ces choix dans le parcours courant.

Le retrait des options est une modification de périmètre de l’interface. Il ne justifie pas de recalculer Java ni de supprimer les sources et preuves historiques. Les règles actuelles du dépôt qui exigent cinq options devront être mises en cohérence avec les trois options visibles demandées.

## Frontière entre observations et estimations

**La comparaison des solutions de marché ne doit contenir aucun chiffre d’estimation.** Cela inclut les diagnostics nominaux calculés sur un logiciel tiers, même lorsqu’ils ne sont pas utilisés dans le budget FLOW.

| Contenu | Études préalables | Autre emplacement |
| --- | --- | --- |
| Fonctions documentées, versions, éditions et différences avec les besoins métier | Oui | Les évaluations peuvent y renvoyer. |
| Taille du code effectivement mesurée, fichiers et périmètre de la mesure | Oui, dans le détail technique expliqué | Aucun effort ne doit être déduit sur cette page. |
| Observations publiées de productivité ou de temps passé sur des travaux réels | Oui, dans Productivité du développement | La valeur choisie et sa transposition appartiennent aux évaluations. |
| Prix publiés de prestations, dépenses et financements de projets de référence | Oui, dans les études de coûts et de projets, avec leur nature et leur période | Ils ne deviennent pas automatiquement un budget FLOW. |
| Effort COCOMO, JH calculés, délais modélisés, charges retenues et gains adoptés | Non | Évaluations des charges brutes, méthodes et dossier économique selon leur rôle. |
| Traitement des écarts et décision de financement | Non dans la comparaison documentaire | Des préétudes aux budgets et évaluations. |

Le navigateur confirme le mélange : la fiche ERPNext présente **44 301 JH** de diagnostic COCOMO et **2 040,2 mois-personne**, avec des JH par composant. Le volume de **415 947 lignes de code mesurées** est une donnée d’entrée distincte. Retirer uniquement la valeur de synthèse ne suffirait pas : le tableau, la conversion, les formules et les cartes méthodologiques sont aussi concernés.

Le correctif doit séparer la projection documentaire de la projection d’estimation. Les données conservées pour le moteur restent disponibles à leurs consommateurs. Aucun recalcul, changement de tarif ou modification de budget n’est nécessaire.

## Arborescence proposée

Le groupe **Études préalables** réunirait les entrées suivantes. Les enfants sont visibles lorsque leur dossier est ouvert. Les autres dossiers restent compacts. Sur mobile, le menu indique aussi le sujet actif.

| Entrée du menu | Accès aux sujets | Traitement des variantes |
| --- | --- | --- |
| Vue d’ensemble des études | Orientation par question et accès directs | Aucun onglet nécessaire. |
| Repères Synvance | Organisation existante conservée | Hors refonte éditoriale de cet audit. |
| Cartographie métier | Organisation existante conservée | Hors refonte éditoriale de cet audit. |
| Projets comparables | Intégration et déploiement, Construction de produits, Services et exploitation | Chaque sujet possède une adresse et une entrée de menu. |
| Comparaison des solutions de marché | Comparaison métier, Fiches des solutions | Produit et capacité sont des variantes de la comparaison. Leurs détails restent reliés à la grille. |
| Tarifs et achats | Tarifs des prestations, Cloud licences et outils, Change et indices | Java, Microsoft et SAP deviennent des sections explicites, pas des contenus masqués. Les choix .NET et Rust sont retirés du parcours actif. |
| Productivité du développement | Études de productivité, Assistance IA dans une même page avec sommaire | Les études IA ne restent plus cachées sous la comparaison des produits. |

Le menu reste organisé par sujet. Il ne faut pas transformer les dix rubriques actuelles en dix liens au même niveau ni ajouter un lien pour chaque source ou chaque ligne de tarif.

Les liens existants doivent rester compatibles. Les anciennes adresses des rubriques déplacées conduisent au nouveau sujet en conservant produit, capacité ou cible lorsque cette information existe.

## Rôle de la page d’ensemble

**Oui à une vue d’ensemble courte.** Son utilité est de répondre à « Où trouver cette information ? » et « À quoi sert cette étude ? ». Elle ne remplace ni le menu détaillé ni les synthèses des pages.

Une table ou six cartes compactes suffisent : besoin recherché, étude correspondante, apport concret et lien direct. Exemples de questions : comprendre les offres reçues, connaître le périmètre métier, comparer les fonctions des produits, retrouver un tarif de développeur, comprendre un repère de productivité, examiner un projet comparable.

La page ne reprend ni chiffres d’estimation ni inventaire des preuves. Les synthèses réutilisées viennent des mêmes propriétaires que les pages détaillées. L’accueil du Framework et le lien du logo restent distincts de cette orientation documentaire.

## Synthèse utile pour chaque sujet

Chaque page commence par un encart **Ce qu’on en retient**, de deux ou trois phrases. Une seule conclusion principale précède les détails et les sources.

| Sujet | Proposition de synthèse |
| --- | --- |
| Intégration et déploiement | Les projets SAP et Dynamics donnent des repères de coût d’intégration. Les différences de périmètre, de déploiement et de travail conservé par le client expliquent les écarts entre ces références. |
| Services et exploitation | Les publications couvrent des prestations et des durées différentes. Pour comparer les cas, il faut identifier le support, les mises à jour, l’hébergement et les licences réellement compris dans chaque prix. |
| Construction de produits | Les programmes publiés réunissent développement, pilotes et autres livrables. Ils donnent des repères d’ampleur et de financement, sans isoler systématiquement la dépense de logiciel. |
| Comparaison métier | La grille met en regard les fonctions documentées des six solutions et les besoins métier FLOW. Elle permet de repérer les fonctions existantes, les différences et les vérifications à mener. |
| Fiches des solutions | Chaque fiche explique ce que propose le produit, ses particularités et les éléments documentés pour la version étudiée. Les mesures de code restent un détail technique sourcé. |
| Tarifs des prestations | Les prix varient selon le profil, l’expérience, le produit et le mode d’achat. Les relevés permettent de comparer ces segments et de comprendre leurs différences. |
| Cloud licences et outils | Une licence sans redevance ne couvre pas les dépenses d’hébergement, d’intégration et d’exploitation. Les fiches précisent ce qui est facturé et selon quelle unité. |
| Change et indices | Les dates, devises et indices permettent de relire les prix publiés dans leur contexte. Les observations historiques et les hypothèses futures restent séparées. |
| Productivité du développement | Les études observent des tâches et des populations différentes. Les résultats sur l’assistance IA ne justifient pas un gain uniforme pour toutes les activités. |

Ces propositions fixent le niveau de langage et l’utilité attendue. Les conclusions plus précises par produit doivent être rattachées aux preuves correspondantes, sans inventer un vainqueur ni un score.

## Lecture de la comparaison métier

### Donner un sens aux états

« À rapprocher » correspond à la clé `analogie_a_qualifier`. Cet état ne décrit pas à lui seul l’usage de la référence dans une estimation. Les décisions adoptées Java/Axelor existent séparément dans le modèle. Par ailleurs, les 17 qualifications détaillées conservées dans `instruction-marche.yaml` sont encore `a_qualifier`, sans revue renseignée. L’estimation adoptée et la qualification fonctionnelle complète sont donc deux objets différents.

Remplacer le libellé par **Analogie proposée**, puis préciser dans le détail la fonction rapprochée et l’écart concret à vérifier. Ne pas remplacer globalement cet état par « Validé ». Les fonctions documentées, les déclarations fournisseur, les écarts constatés et l’absence d’information doivent conserver des significations distinctes.

La page doit expliquer cette distinction une fois, en langage simple : **Une fonction comparable a été identifiée. Les différences indiquées restent à examiner pour le besoin FLOW.** Lorsque le lien n’est pas établi, afficher **Information insuffisante**. Lorsque seul le fournisseur le déclare, afficher **Déclaré par le fournisseur**. Une documentation publique n’établit pas l’inclusion dans l’offre reçue.

L’utilisation chiffrée de la référence se consulte dans les évaluations via un lien explicite, sans charge, coût ni délai repris dans la comparaison.

### Reprendre la hiérarchie métier existante

Les chemins natifs fournissent déjà **Domaine → Sous-domaine → Business Area → Capacité**. Les 28 Business Areas de la comparaison se répartissent sous neuf sous-domaines. La projection actuelle conserve leur identité mais n’en restitue pas les parents.

Afficher le domaine en contexte, des sections par sous-domaine et les Business Areas à l’intérieur. Exemple existant : Supply Chain Management → Inventory Management → Inventory State Management → Reservation. Les noms et identifiants natifs restent inchangés. Une courte explication en français peut accompagner les noms anglais.

La table peut rester utile sur ordinateur, avec des groupes clairement titrés. Sur mobile, présenter les solutions côte à côte par petits groupes ou les constats dans une lecture verticale. La grille actuelle mesure environ 1 218 px dans une zone de 309 px : le défilement contenu protège la page, mais ne rend pas la comparaison facile.

### Réserver le filtre à la comparaison

Conserver au maximum un choix de **Sous-domaine** au-dessus de la grille, avec « Tous ». Il répond à un vrai besoin d’orientation dans les 28 Business Areas. Une recherche libre et un deuxième filtre OSS / Microsoft / SAP ne sont pas nécessaires au premier niveau.

Les variantes produit et capacité peuvent rester des sélections dans une fiche de détail. Leur état doit avoir une adresse partageable et un titre précis. Dans les autres études, utiliser des titres de section, un sommaire et des ancres. Les treize relevés de tarifs ne justifient pas une interface de recherche.

## Présentation et vocabulaire

| État actuel | Cible |
| --- | --- |
| Données d’entrée | Études préalables |
| Comparaison des solutions | Comparaison des solutions de marché |
| Provenance et état de la préétude | Panneau supprimé. Date et source près du contenu concerné. |
| Stack ou écosystème | Technologie ou solution |
| Assiettes des services techniques | Ce qui est facturé |
| Régime de tarification | Mode de facturation |
| Normalisation monétaire | Prix ramenés à une même année et une même devise |
| Qualification et instruction | Analyse ou vérification selon l’action réelle |
| Les quatre OSS | Les quatre logiciels à code source ouvert |

À la première apparition utile : **logiciels à code source ouvert, ou OSS pour Open Source Software**. Ajouter au glossaire canonique une notion dédiée : logiciels dont la licence permet de consulter, modifier et redistribuer le code source selon ses conditions. Cette ouverture ne signifie ni gratuité de tous les services ni absence de coûts de fonctionnement. Garder QA, connu du lecteur.

Les fiches produit contiennent aussi PNCLOC, ATP, CTP, PTP, RFI, ORM et BPMN/DMN. Définir les termes nécessaires au niveau de lecture concerné. Déplacer les détails techniques dans une section identifiée. Éviter les mentions de mécanique interne du modèle dans le parcours du sponsor.

### Largeur et emplacement des onglets

Sur les vues contrôlées, la navigation principale du dossier et la feuille ont la même largeur : environ **973 px sur ordinateur** et **339 px sur mobile**. Les quatre onglets de la comparaison se répartissent sur cette largeur. Le défaut de largeur générale n’est donc pas reproduit sur cette version.

L’audit confirme en revanche deux défauts : une navigation des projets située trop bas et des libellés mobiles réduits à « Grille », « Constats », « Fiches » et « Effort ». Le contexte du sujet devient peu visible. Les fiches produit disposent en plus d’un second niveau d’onglets à l’intérieur de la feuille, naturellement plus étroit.

Cible : aligner les accès locaux sur la largeur de la feuille, les placer avant le contenu long et utiliser des noms compréhensibles. Les onglets qui comparent les six produits peuvent rester. Les sujets différents passent dans le menu.

## Parcours à vérifier après réorganisation

| Intention du lecteur | Parcours cible | Résultat attendu |
| --- | --- | --- |
| Retrouver le tarif d’un développeur Java | Études préalables → Tarifs et achats → Tarifs des prestations → Java | Profil, fourchette publiée, mode d’achat, date et source visibles sans filtre. |
| Retrouver le prix choisi pour chiffrer FLOW | Hypothèses retenues → Tarifs | La valeur adoptée reste distincte du relevé de marché. |
| Comprendre ce que propose Axelor | Comparaison des solutions de marché → Fiches des solutions → Axelor | Fonctions, édition, particularités et sources. Aucun JH calculé. |
| Comparer la réservation entre produits | Comparaison métier → Inventory Management → Inventory State Management → Reservation | Même besoin visible, écarts et preuves par produit. |
| Retrouver l’étude sur les gains IA | Productivité du développement → Assistance IA | Observation et périmètre de l’expérience. Les gains retenus restent dans les hypothèses. |
| Retrouver un contrat de support | Projets comparables → Services et exploitation | Prestations incluses, période, montant publié et source. |

Le lien copié doit rouvrir le sujet et la variante attendus. Le retour arrière doit conserver le contexte. Le menu, le titre de page et le fil de navigation doivent indiquer le même emplacement. Aucun coût inconnu ne devient zéro.

## Mise en œuvre proposée

1. **Centrer le parcours sur Java.** Retirer .NET et Rust des choix et restitutions de l’application. Conserver Microsoft et SAP comme alternatives Buy. Traiter les anciens liens et sauvegardes sans conversion silencieuse.
2. **Rétablir la frontière des préétudes.** Séparer les fiches documentaires des résultats d’estimation. Retirer de la comparaison les efforts, conversions et cartes de méthode. Préserver leurs consommateurs dans les évaluations.
3. **Rendre les sujets trouvables.** Renommer le groupe, afficher les sous-entrées, isoler la productivité et conserver les anciennes adresses. Ajouter ensuite la vue d’ensemble courte.
4. **Réécrire les synthèses.** Un encart utile par sujet. Supprimer les panneaux de provenance et les introductions redondantes. Garder les preuves locales.
5. **Structurer la comparaison.** Projeter les parents natifs, clarifier les états et limiter le filtre au sous-domaine. Adapter la lecture mobile.
6. **Simplifier les tarifs et achats.** Supprimer les filtres, regrouper les données sous des titres explicites et ajouter des ancres stables. Expliquer OSS et les unités utiles dans le glossaire.

Les données métier et économiques gardent leurs propriétaires. Les regroupements viennent des chemins natifs. Une observation de marché, une hypothèse retenue et un résultat calculé ne deviennent pas trois copies d’une même valeur.

## Preuves de l’audit

Les dix rubriques des trois nouvelles préétudes ont été parcourues dans le navigateur local. La comparaison et les projets ont également été contrôlés en largeur mobile de 390 px. La capture des onglets des projets se situe vers 1 550 px sur ordinateur et 2 730 px sur mobile, avant défilement. Les mesures de position dépendent du rendu et de la taille de fenêtre.

Version statique contrôlée : `20d6459e5c2e05c9008efd7de2b0d9962200581325c04082b7f5652c2de51124`. Audit de lecture et de navigation, sans modification de l’application ni test de recalcul financier.

Les points d’implémentation sont identifiés ici pour préparer les changements :

- [PreStudyPage.tsx](C:/Dev/FLOW-Etude-Economique/app/src/PreStudyPage.tsx:23) place la synthèse avant les onglets et réutilise les fiches mêlant mesures et estimation.
- [EssentialViews.tsx](C:/Dev/FLOW-Etude-Economique/app/src/EssentialViews.tsx:131) rend le détail COCOMO. La fiche produit affiche aussi `effort_jh`.
- [MarketComparison.tsx](C:/Dev/FLOW-Etude-Economique/app/src/MarketComparison.tsx:29) filtre puis affiche les lignes sans regroupement par parent métier.
- [market_comparison.py](C:/Dev/FLOW-Etude-Economique/tools/market_comparison.py:89) projette la Business Area sans son chemin hiérarchique.
- [MarketCostsPage.tsx](C:/Dev/FLOW-Etude-Economique/app/src/MarketCostsPage.tsx:29) initialise le filtre Java et conserve les sélections localement.
- [App.tsx](C:/Dev/FLOW-Etude-Economique/app/src/App.tsx:147) génère un menu à un seul niveau dans chaque groupe.
- [application.yaml](C:/Dev/FLOW-Etude-Economique/config/application.yaml:1186) porte les dix rubriques et les libellés des préétudes.
- [comparaison-solutions.yaml](C:/Dev/FLOW-Etude-Economique/source/comparaison-solutions.yaml:110) porte les états documentaires. `instruction-marche.yaml` porte les qualifications détaillées.
- [estimations-core-retenues.yaml](C:/Dev/FLOW-Etude-Economique/source/estimations-core-retenues.yaml) porte séparément les décisions adoptées et leur provenance.
- [glossaire.yaml](C:/Dev/FLOW-Etude-Economique/source/glossaire.yaml:11) est le propriétaire de la future notion OSS.
