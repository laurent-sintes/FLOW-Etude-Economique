# Audit de cohérence de l’organisation du delivery FLOW et de ses impacts

Date : **5 novembre 2026**. Base lisible constatée : modèle du **3 novembre 2026, n° 11**.

**Principe directeur : constituer des équipes produit durables, responsables de leur périmètre pendant la construction du produit générique, son intégration chez Beaumanoir et sa vie en service.** Le modèle doit permettre de lire les charges et les coûts par équipe, par phase et dans le temps pour dimensionner cette continuité.

La cible discutée comprend **onze équipes de delivery et une instance de gouvernance hors typologie Team Topologies**. Le parcours proposé est Études préalables → Organisation du delivery → Évaluation des charges → Dossier économique → Framework et méthodes. Les deux changements sont liés : montrer les responsabilités, puis les travaux et les moyens nécessaires, avant les résultats économiques.

Cet audit consolide les orientations exprimées dans la conversation. Il distingue les constats sur les fichiers courants, les orientations métier convenues et les propositions d’implémentation. Il ne met en œuvre aucune modification du modèle, du logiciel, des charges, des coûts ou du calendrier. La seule création autorisée à ce stade est ce fichier d’audit.

## Orientations consolidées

| Sujet | Orientation issue des échanges | Conséquence à instruire |
| --- | --- | --- |
| Équipes produit durables | Principe qui doit guider l’étude et apparaître explicitement dans son parcours. | Relier responsabilité produit, continuité des compétences, charges, coûts et capacité dans le temps. |
| Team Topologies | Cadre d’organisation du delivery, avec quatre types d’équipes et trois modes d’interaction. | Introduire la théorie avant la cible FLOW, avec référence au livre et loi de Conway. |
| Transformation Office | Instance de gouvernance hors du périmètre de classification retenu pour les équipes de delivery. | Aucun tag Enabling. Réconcilier cette définition avec les missions opérationnelles et le financement actuels. |
| Master Data | Produit MDM envisagé comme base de vérité de Business Operations. Type Stream-aligned retenu dans la cible discutée. | Instruire l’évolution depuis les références locales actuellement décrites et ses effets sur le périmètre estimé. |
| Ancien Core Engine | Séparer Master Plan avec Supply Policy, et Inventory avec Availability. | Deux équipes. Leurs noms définitifs et la justification du type Complicated-subsystem restent à préciser. |
| Portal | Un même produit d’accès à FLOW, associant XP APIs, sécurité applicative et portail UI pour accueillir des clients sur la plateforme. Type Stream-aligned. | Définir l’onboarding, les consommateurs, les API d’expérience et la frontière avec PaaS et les API de domaine. |
| Continuité des phases | Les mêmes équipes prennent en charge le générique, l’intégration Beaumanoir puis le MCO et les évolutions de leur périmètre. | Éviter un transfert systématique de responsabilité entre équipes successives de construction, d’intégration et de maintenance. |
| Couverture des travaux | Le dispositif d’équipes doit porter la construction Make et les travaux d’intégration. | Affecter les travaux existants, identifier les contributions externes et détailler les charges encore insuffisamment instruites. |
| Navigation | Organisation immédiatement après les études préalables, charges ensuite, puis économie. Framework à la fin du parcours principal. | Redistribuer les contenus, liens de suite, routes et contextes de lecture. |
| AGENTS.md | Les chiffres métier et économiques appartiennent à leurs sources propriétaires. | Retirer les résumés chiffrés d’AGENTS.md et conserver les règles et renvois. Ne pas y maintenir une copie actualisée des valeurs. |
| Portée de la présente demande | Créer un audit de cohérence et d’impacts. | Aucun changement d’application, de source active, de révision du modèle, de commit ou de publication. |

Les onze équipes ne sont pas onze lots de financement. Le nombre d’équipes envisagées ne détermine ni leur effectif, ni leur date de mobilisation, ni un budget additionnel.

## Diagnostic de l’existant

### Parcours et responsabilités

La configuration courante place le Framework avant les charges, puis l’organisation et le dossier économique. La section Organisation comprend trois pages : Transformation Office FLOW, Équipes produit et Intégration transverse des livraisons. Elle décrit cinq regroupements produit : Référentiels, Stocks, Commandes et prestations, Planification Supply et Services partagés.

Les missions des regroupements sont dans la configuration de présentation. Les équipes n’ont pas de type Team Topologies, de responsabilité métier structurée, de services fournis ou d’interactions modélisées. La page Intégration transverse décrit une coordination de livraisons avec un repère SAFe. Elle ne définit pas les trois modes Team Topologies.

Constat vérifié dans [la configuration](../config/application.yaml), [le composant delivery](../app/src/DeliveryOrganisationPage.tsx) et les trois pages locales lors de l’audit initial de cette conversation.

### Modèle métier et économie

Le [métamodèle canonique](../source/fondamentaux.yaml) définit déjà les capacités, fonctions, unités de travaux, rôles, financements et calendriers. Il ne définit pas encore les équipes de delivery et leurs interactions. Une collection de fiches dans React ou dans la configuration ne suffirait donc pas à porter la cible.

La distinction entre produit générique et intégration Beaumanoir existe dans les sources. [L’intégration](../source/integration.yaml) part d’un produit générique sans données ni configuration Beaumanoir et décrit les travaux jusqu’à une première version exploitée et stabilisée. Le [cycle de vie composable](../source/modele-composable.yaml) distingue aussi maintenance du Core et maintenance des adaptations client.

Le [registre d’intégration](../source/unites-integration.yaml) indique pour Java/Spring que les familles de travaux ont des financements actifs, mais que les quantités, critères de recette et frontières de réutilisation demandent encore du détail. Cela justifie une instruction plus fine. Cela ne prouve pas que tous ces travaux seraient absents des budgets.

### Base chiffrée constatée

Lecture directe des champs `total_jh` des onze unités de [la source des estimations retenues](../source/estimations-core-retenues.yaml), au 5 novembre 2026 :

| Lot courant | JH déclarés |
| --- | ---: |
| Master Data | 1 600 |
| Stock | 340 |
| Propriété du stock | 190 |
| Politiques, éligibilité et devenir des biens | 610 |
| Gestion des commandes | 420 |
| Préparation et pilotage du Master Plan | 330 |
| Promesse, affectation et optimisation Supply | 710 |
| Prestations et reconnaissance des résultats | 430 |
| Process Management avec studios, portail, formulaires et pilotage | 2 060 |
| Ateliers visuels de planification et de décision | 400 |
| Administration, robustesse et services IT complémentaires | 540 |
| **Total des onze lots** | **7 630** |

Ce total est un constat sur les valeurs déclarées des lots courants. Il ne représente ni une nouvelle estimation, ni une ventilation par équipe, ni un recalcul du budget ou des charges nettes.

**Un résumé chiffré d’AGENTS.md diverge de ces instances.** L’action à prévoir est de retirer ce résumé et de renvoyer au propriétaire des décisions. AGENTS.md conserve les règles de travail et les autorités, sans chiffres métier ou économiques recopiés. Les valeurs présentes dans cet audit constituent une base datée de comparaison.

## Principe des équipes produit durables

Une équipe conserve la connaissance de son produit, la responsabilité de ses résultats et la maîtrise de ses interfaces à travers les étapes du projet. Sa composition et sa capacité peuvent évoluer. Une responsabilité durable ne signifie pas un effectif constant.

Ce principe doit apparaître dès l’introduction de l’étude, dans l’ouverture du dossier Organisation et dans le Framework. Une seule définition canonique doit alimenter ces présentations. Elle doit relier continuité des compétences, autonomie, qualité, maintenabilité et capacité à faire évoluer le produit.

L’ambition est de construire FLOW comme un produit générique pouvant être proposé à d’autres clients. Beaumanoir apporte un contexte d’intégration concret. Chaque besoin doit être qualifié comme comportement générique, configuration supportée ou extension client. La construction d’un produit commercialisable ne crée pas, à elle seule, une hypothèse de revenus ou de mutualisation financière entre clients.

La continuité constitue un levier à rendre vérifiable. Aucun gain de productivité, réduction de charge ou bonus économique supplémentaire ne doit être déduit du seul principe. Les mécanismes de continuité déjà présents dans le modèle doivent être identifiés avant toute nouvelle hypothèse.

### Exemple B2C

| Étape | Travail porté par la même équipe B2C | Résultat attendu |
| --- | --- | --- |
| Build Core System | Définir et réaliser les comportements standard des Orders B2C, leurs états, contrats et mécanismes d’extension. | Un produit générique utilisable dans plusieurs contextes clients. |
| Intégration Beaumanoir | Rapprocher les pratiques du Groupe, paramétrer, connecter les systèmes, réaliser les extensions nécessaires et qualifier les parcours réels. | Des parcours Beaumanoir opérationnels et acceptés. |
| MCO du produit générique | Corriger les mécanismes partagés, maintenir la compatibilité et faire évoluer les comportements standard. | Des versions produit maîtrisées. |
| MCO des adaptations Beaumanoir | Corriger et faire évoluer les configurations, extensions et flux propres au Groupe. | La continuité du service client et la compatibilité avec les versions produit. |

La présentation conserve trois grandes étapes. Le MCO est détaillé en deux objets de responsabilité pour préserver le sens des travaux et de leur financement.

Un besoin découvert pendant l’intégration peut conduire à enrichir le produit générique. Il faut alors décider du périmètre, du financement et de la version de livraison. La date de découverte du besoin ne détermine pas seule sa catégorie financière.

## Référence Team Topologies

La première page Organisation présente l’esprit du cadre : accélérer le flux de valeur, limiter la charge cognitive et organiser l’autonomie. Le livre de référence est *Team Topologies: Organizing Business and Technology Teams for Fast Flow*, de Matthew Skelton et Manuel Pais, publié en 2019, avec une seconde édition en 2025. [Livre officiel](https://teamtopologies.com/book)

| Type | Finalité |
| --- | --- |
| Stream-aligned | Porter les résultats d’un flux de valeur de bout en bout. |
| Platform | Réduire la complexité des équipes consommatrices grâce à des services de plateforme. |
| Complicated-subsystem | Concentrer une expertise spécialisée dans un sous-système. |
| Enabling | Développer les compétences et l’autonomie d’autres équipes. |

| Interaction | Usage |
| --- | --- |
| Collaboration | Explorer ou construire ensemble pendant une période définie. |
| X-as-a-Service | Fournir et consommer un service avec des responsabilités explicites. |
| Facilitating | Accompagner temporairement une équipe pour lever un obstacle ou acquérir une compétence. |

Un type qualifie une équipe. Un mode qualifie une interaction, pour un objet et une période donnés. Une équipe durable peut mener des interventions temporaires et employer plusieurs modes selon ses interlocuteurs. [Concepts officiels](https://teamtopologies.com/key-concepts)

La loi de Conway relie la structure des systèmes aux structures de communication des organisations qui les conçoivent. Pour FLOW, elle invite à construire ensemble les frontières de responsabilité et les contrats logiciels. [Source de Melvin Conway](https://www.melconway.com/Home/Conways_Law.html)

Le dessin représente une configuration datée et évolutive. Une collaboration permanente ou un passage obligé par une équipe transverse doit conduire à examiner la dépendance créée. Les API et les échanges de données ne suffisent pas à qualifier les interactions humaines. [Guide de modélisation](https://teamtopologies.com/key-concepts-content/team-interaction-modeling-with-team-topologies)

## Cible des équipes de delivery

Les noms des deux équipes issues du Core Engine ci-dessous servent de libellés de travail. Le nom Flow Core System Portal est conservé. Aucun renommage de produit n’est décidé par cet audit.

| Équipe | Type dans la cible discutée | Responsabilité et frontière déterminante |
| --- | --- | --- |
| Case Management | Platform | Socle de case management, moteur de règles générique, process mining et analytics engine. Les équipes métier possèdent leurs règles et processus spécifiques. |
| PaaS | Platform | Outils de développement, IA, harnais, CI/CD et services techniques de delivery. Distinguer les moyens consommés des produits qu’elle fournit. |
| Master Plan et Supply Policy | Complicated-subsystem, à justifier | Plans, politiques Supply, arbitrages et décisions de planification. Séparer les politiques métier des mécanismes génériques du moteur de règles. |
| Inventory et Availability | Complicated-subsystem, à justifier | Faits de stock, propriété, réservations et possibilités de promesse. Contractualiser les relations entre disponibilité, affectation et engagement. |
| Services | Stream-aligned | Service Management et Fulfilment Orchestration. Possède l’exécution métier des prestations, en consommant les moteurs génériques. |
| Master Data | Stream-aligned | Produit MDM cible de Business Operations. Définir les objets maîtrisés, les autorités, la qualité et la publication. |
| Sourcing & Procurement | Stream-aligned | Parcours et Orders du monde achat. Préciser les frontières entre accords fournisseur, engagements et décisions Supply. |
| B2C | Stream-aligned | Comportements et parcours des Orders B2C, du standard générique aux usages Beaumanoir. |
| Wholesale | Stream-aligned | Comportements et parcours des Orders B2B/Wholesale, avec leurs engagements spécifiques. |
| Flow Core System Portal | Stream-aligned | Produit d’accès à FLOW : XP APIs, sécurité applicative et portail UI. Les équipes de domaine conservent les règles de leurs API et contrôles d’autorisation. |
| Intégration | Enabling | Facilite l’intégration des composants et les flux SI, accompagne les équipes et coordonne les contributions iPaaS. La propriété durable des flux et de leur exploitation doit être identifiée. |

La cible comprend six équipes Stream-aligned, deux Platform, deux Complicated-subsystem et une Enabling. La qualification des deux sous-systèmes doit s’appuyer sur l’expertise nécessaire et la réduction de complexité pour leurs consommateurs. Un domaine volumineux ne suffit pas à établir cette qualification.

### Gouvernance hors typologie

Le Transformation Office est représenté comme une instance de gouvernance, avec des liens de décision et d’arbitrage distincts des interactions de delivery.

La source actuelle finance des fonctions de direction de projet, PMO, synchronisation, changement et architecture transverse. **Qualifier l’instance cible de board ne transforme pas automatiquement ces postes en missions de board et ne supprime pas leur financement.** Il faudra distinguer instance de décision, missions opérationnelles transverses et responsabilités locales, puis décider de leur organisation.

### Ambition MDM et périmètre financé

L’ambition MDM a été exprimée comme une évolution vraisemblable. La source actuelle [d’analyse du périmètre](../source/analyse-perimetre-core.yaml) décrit des références locales et exclut notamment le remplacement des maîtres PLM ou MDM.

Le passage à une source de vérité de Business Operations doit préciser les domaines de données, les processus de création et correction, les autorités, la migration, la distribution et les engagements de qualité. Le lot Master Data existant ne démontre pas à lui seul le financement de ce périmètre élargi. Cette évolution doit être instruite séparément de la redistribution des charges à périmètre constant.

La même vérification s’applique aux formulations « tous les Orders du monde achat » et « du monde Commerce ». Une équipe peut porter une ambition plus large que les fonctions actuellement couvertes par l’étude. Le rapprochement doit conserver les identifiants métier natifs et expliciter les extensions envisagées.

## Participation aux trois étapes

La matrice ci-dessous décrit des responsabilités candidates. Elle ne vaut ni affectation chiffrée ni mobilisation de toutes les équipes à temps plein pendant chaque phase.

| Équipe | Build Core System générique | Intégration Beaumanoir | MCO et évolutions |
| --- | --- | --- | --- |
| Case Management | Construire les moteurs, contrats, studios et mécanismes génériques. | Accompagner leur configuration, leur assemblage et la qualification des usages client. | Maintenir les moteurs et la compatibilité, contribuer aux diagnostics. |
| PaaS | Fournir les moyens de construction et la chaîne industrielle générique. | Fournir les moyens de livraison et les environnements nécessaires au contexte client. | Maintenir l’outillage et ses services, avec exploitation et achats identifiés. |
| Master Plan et Supply Policy | Réaliser les mécanismes de planification, d’arbitrage et de politique. | Configurer et éprouver les politiques et contraintes du Groupe. | Maintenir les calculs et faire évoluer les règles, selon leur objet générique ou client. |
| Inventory et Availability | Réaliser les mécanismes de stock, réservation et promesse. | Intégrer les faits des systèmes, règles et engagements du Groupe. | Maintenir la cohérence des mécanismes et traiter les incidents de leur périmètre. |
| Services | Réaliser les comportements standard de gestion et d’orchestration des prestations. | Intégrer prestataires, contrats et parcours d’exécution du Groupe. | Maintenir le produit et les adaptations d’exécution. |
| Master Data | Construire les fonctions génériques du produit de références ou du MDM retenu. | Migrer, rapprocher et distribuer les données selon les autorités décidées. | Maintenir le produit et ses adaptations, avec gouvernance métier des données identifiée. |
| Sourcing & Procurement | Construire les comportements standard des Orders achat. | Adapter les parcours et échanges avec les systèmes et fournisseurs concernés. | Maintenir les parcours et échanges, en distinguant standard et spécifique. |
| B2C | Construire les comportements standard des Orders B2C. | Intégrer les spécificités et canaux Beaumanoir. | Maintenir et faire évoluer le produit et les adaptations B2C. |
| Wholesale | Construire les comportements standard B2B/Wholesale. | Intégrer les spécificités et partenaires Beaumanoir. | Maintenir et faire évoluer le produit et les adaptations Wholesale. |
| Flow Core System Portal | Construire l’accès standard, les XP APIs, la sécurité applicative et l’UI transverse. | Intégrer identités, accès, parcours et politiques de sécurité du contexte client. | Maintenir l’expérience d’accès et la compatibilité des interfaces. |
| Intégration | Aider à concevoir les contrats d’intégration et les pratiques de tests des composants. | Faciliter les raccordements au SI et les contributions iPaaS. | Accompagner les évolutions d’intégration et transférer les compétences nécessaires. |

Les onze équipes et trois étapes forment **33 croisements possibles** avant découpage temporel. Ce nombre décrit la grille de lecture. Une cellule peut être sans objet, non dimensionnée ou mobilisée seulement à certaines périodes.

Les travaux réalisés par les métiers, les équipes SI, les prestataires iPaaS ou d’autres acteurs doivent rester visibles. La responsabilité d’une équipe sur un résultat ne signifie pas qu’elle fournit seule toutes les contributions.

## Charges et coûts par équipe et par phase

### Chaîne de traçabilité

Le lien à construire est : **besoin ou fonction → travail → rôles et charges → affectation aux équipes → valorisation → financement → période**.

Les dimensions doivent rester indépendantes :

| Dimension | Question |
| --- | --- |
| Équipe | Qui porte le résultat et qui contribue au travail ? |
| Phase | Le travail relève-t-il de la construction initiale, de l’intégration initiale ou du MCO et des évolutions ? |
| Objet maintenu ou réalisé | Produit générique, adaptation Beaumanoir, service technique ou moyen consommé ? |
| Rôle | Quelles compétences réalisent les JH ? |
| Période | Quand la capacité est-elle nécessaire et quels travaux sont simultanés ? |
| Financement | Quelle ligne existante ou décision future finance le travail ? |
| Type Team Topologies | Quel rôle organisationnel l’équipe joue-t-elle ? |
| Build/Run et Core Domain/Support | Comment le travail se lit-il dans les conventions métier existantes ? |

MCO n’est pas synonyme de Run. Le modèle classe le MCO du Core comme Build et distingue la convention applicable aux adaptations Beaumanoir. Make désigne une voie d’obtention et ne doit pas devenir un synonyme de la seule phase de construction.

### Règles de ventilation proposées

1. Une responsabilité principale est identifiable pour chaque périmètre de résultat. Les contributions partagées sont explicites.
2. Les JH d’un même travail et d’un même rôle se répartissent une seule fois. Une équipe responsable et une équipe contributrice ne reçoivent pas chacune la totalité des mêmes JH.
3. La somme des parts affectées et du reliquat non ventilé restitue la charge source. Un partage doit avoir un motif et une preuve adaptés à sa précision.
4. Les charges brutes, nettes et totales projet gardent leur définition. La ventilation utilise une base identifiée et ne mélange pas ces bases.
5. Les rôles plateforme, architecture, UX et sécurité déjà financés dans les lots sont rapprochés avant toute attribution aux équipes transverses.
6. Les coûts par équipe sont dérivés des JH par rôle, des tarifs applicables et des montants déjà produits par le moteur. Un tarif moyen par équipe ne remplace pas cette valorisation.
7. Les forfaits, licences, achats et coûts cloud restent en euros. Ils sont attribués directement ou partagés selon une règle documentée. La notion de coût d’équipe doit distinguer son coût humain et les moyens qu’elle consomme.
8. Un coût de plateforme est compté une fois dans la vue consolidée. Une éventuelle réallocation aux consommateurs remplace sa présentation directe dans cette vue, sans créer une seconde dépense.
9. Les contrats Buy non ventilés et les financements non dimensionnés conservent leur état. Inconnu, non ventilé, sans objet et zéro restent distincts.
10. Les correctifs encore dus au titre d’une réalisation initiale ne deviennent pas artificiellement du MCO. Les périodes de stabilisation et de réception conservent leurs règles.

Les onze lots actuels et les onze équipes cibles ont le même nombre par coïncidence. La correspondance réelle est multiple. Les charges des lots doivent être ventilées à partir des travaux, pas en renommant les lots.

### Rapprochements à effectuer

| Lot ou groupe actuel | Équipes principalement concernées | Travail d’allocation nécessaire |
| --- | --- | --- |
| Master Data | Master Data, contributions de plateformes à identifier | Distinguer fonctions du produit, intégration des sources et ambition MDM supplémentaire. |
| Stock et propriété du stock | Inventory et Availability | Préserver les rôles et vérifier les frontières des faits, protections et réservations. |
| Politiques, éligibilité et devenir | Master Plan et Supply Policy, autres consommateurs métier | Séparer politique, décision et application dans les parcours. |
| Gestion des commandes | Sourcing & Procurement, B2C, Wholesale | Détailler les variantes et désigner le propriétaire des mécanismes communs. Aucun partage forfaitaire par trois. |
| Master Plan, promesse, affectation et optimisation | Les deux équipes issues du Core Engine, Services selon les travaux | Séparer plan, calcul de disponibilité, décisions d’affectation et exécution. |
| Prestations et reconnaissance | Services | Rapprocher les fonctions communes et les contributions d’intégration. |
| Process Management | Case Management, Portal et équipes métier selon les fonctions | Répartir moteurs, studios, formulaires, UI transverse et configurations métier. |
| Ateliers visuels | Équipes de planification et de stock, Portal selon les composants | Distinguer expérience métier et composants UI réutilisables. |
| Services IT complémentaires | PaaS, Portal, Case Management selon les travaux | Identifier les services possédés et retirer les doubles affectations de rôles. |
| Intégration et déploiement | Ensemble des équipes concernées et contributeurs SI | Partir des activités INT et paquets Groupe actifs, puis détailler volumes, responsabilités et vagues. |
| Maintenance | Équipes propriétaires des produits et adaptations | Rapprocher activités MAI, objets maintenus, récurrence et charge de support. |

### Durabilité et dimensionnement

Les vues doivent donner les JH par équipe, phase, rôle et période, puis les comparer à la capacité disponible selon les conventions du calendrier. Le coût dans le temps complète cette lecture avec tarifs, achats et séquences applicables.

Il faut pouvoir voir qu’une équipe maintient une première mise en service, intègre une marque supplémentaire et enrichit le produit générique au même moment. La somme annuelle ne permet pas de détecter seule un pic ou une indisponibilité de compétence.

Une capacité durable minimale peut conduire à un coût différent de la seule valorisation des tâches. Le modèle devra distinguer **travail estimé, capacité prévue et coût financé**. Toute hypothèse de capacité réservée, sous-utilisation, renfort temporaire ou recrutement sera explicite, avec sa source et son financement. Aucune taille standard d’équipe ni nombre systématique de PO n’est déduit de la typologie.

Le calendrier actuel reste la référence jusqu’à une évolution décidée séparément. Une modification des dates de réception, des chevauchements ou des vagues peut changer les annuités et le MCO. Elle doit alors être réconciliée avec le moteur économique.

### Indicateurs à produire

| Indicateur | Définition et usage |
| --- | --- |
| Charges affectées et non ventilées | JH des travaux connus affectés aux équipes, et reliquat, par phase et base de charge. |
| Coûts affectés et non ventilés | Montants du même périmètre rattachés aux équipes, gouvernance, moyens partagés ou reliquat. |
| Couverture de ventilation | Part des JH connus effectivement ventilés, avec dénominateur explicite par phase. Ne mesure pas la complétude du périmètre fonctionnel. |
| Charge simultanée | Travaux et JH par équipe, rôle et période pour repérer les pics. |
| Capacité et charge | Besoin et disponibilité par rôle, avec éventuel déficit ou capacité réservée. |
| Réconciliation financière | Écart entre somme des affectations, reliquats, postes hors équipes et total de référence, au même périmètre et à la même précision. |
| Continuité de responsabilité | Produits et adaptations ayant un propriétaire identifié sur les étapes applicables. Aucun score de productivité n’en est déduit. |

Les indicateurs sont à construire. L’audit ne calcule pas une ventilation fictive pour remplir la matrice.

## Évolution du modèle métier

Le métamodèle unique reste [source/fondamentaux.yaml](../source/fondamentaux.yaml). Les instances organisationnelles pourraient avoir un propriétaire dédié dans `source/`, à nommer lors de l’implémentation. Le schéma structurel, le compilateur Python, les exports et l’interface doivent consommer cette même autorité.

| Concept à définir ou à relier | Contenu métier |
| --- | --- |
| Principe directeur | Équipes produit durables, définition et conséquences attendues sur l’étude. |
| Équipe de delivery | Identifiant, mission, type, consommateurs, statut de proposition ou adoption. |
| Instance de gouvernance | Décisions, arbitrages et responsabilités hors typologie des équipes. |
| Responsabilité produit | Capacités natives, fonctions professionnelles, composants et frontières possédés. |
| Service fourni | Propriétaire, consommateurs, contrat et support. |
| Interaction | Équipes, mode, objet, phase ou période, sens si pertinent et critère de sortie. |
| Configuration organisationnelle | Cible datée et étapes de transition. |
| Affectation de travail | Références aux travaux, rôles, charges, équipe et justification de la répartition. |
| Attribution économique | Lien avec les coûts déjà valorisés et règle de partage éventuelle. |
| Capacité d’équipe | Période, disponibilités par rôle, besoins et contributions externes. |
| Scénario d’organisation | Hypothèses de mobilisation ou de capacité, distinctes du scénario économique de référence. |

Les concepts de travail, rôle, financement, phase et calendrier déjà présents doivent être réutilisés. Un nouvel objet n’est utile que s’il apporte une relation ou une responsabilité absente.

Les contrôles devront refuser références inconnues, types invalides, doubles affectations et répartitions dépassant leur assiette. Ils devront permettre de restituer explicitement un reliquat. Les travaux d’une équipe peuvent couvrir plusieurs capacités et plusieurs lots, sans altérer la hiérarchie native reçue.

## Parcours de lecture proposé

L’accueil présente l’ambition FLOW, le principe des équipes produit durables et le parcours. Il donne aussi un accès direct aux méthodes pour le lecteur expert.

| Ordre | Dossier | Contenu et rôle |
| --- | --- | --- |
| 1 | Études préalables | Besoins, cartographie, acquis Synvance, solutions, projets, tarifs et productivité documentaire. |
| 2 | Organisation du delivery | Principes, cible, équipes, interactions, gouvernance et trajectoire de constitution. |
| 3 | Évaluation des charges | Matrice par équipe et phase, travaux, rôles, sources et charges non ventilées. |
| 4 | Dossier économique | Coûts par équipe et phase, comparaison des options, annuités, hypothèses et scénarios. |
| 5 | Framework et méthodes | Concepts, métamodèle, méthodes d’évaluation, passage au net, valorisation, MCO et règles de calcul. |
| Repère permanent | Glossaire et téléchargements | Définitions partagées, modèle et preuves accessibles. |

Le dossier Organisation pourrait comprendre cinq rubriques : principes et Team Topologies, organisation cible, équipes et périmètres, interactions, gouvernance et trajectoire. Les fiches d’équipe donnent leur participation aux étapes et un accès à leurs charges.

Le dossier Charges commence par une synthèse équipes × phases. Les lectures Construction, Intégration et MCO conservent leurs détails, avec sélection d’une équipe et adresse partageable. Le dossier économique propose les mêmes axes sur les coûts. Les synthèses d’organisation donnent accès à ces résultats sans recopier des montants.

Déplacer le Framework demande une redistribution des contenus. Les résultats, hypothèses financières et scénarios restent près de la décision économique. Les critères méthodologiques et les formules rejoignent le dossier de référence. Le dossier de capacité de réalisation conserve les preuves de mobilisation, de compétences et de transfert à réunir.

Le menu gauche garde un seul niveau. Les rubriques locales utilisent les intercalaires et le fil de navigation. Les anciennes adresses doivent rester résolues avec option, horizon, contexte et focus utiles.

Les équipes décrites ici portent la cible Make. Les pages de charges et d’économie doivent conserver Java/Spring, Microsoft et SAP. Buy garde ses responsabilités éditeur, intégrateur et client, sans recevoir fictivement des charges de construction éditeur ni les mêmes équipes internes.

## Représentation des interactions et de la cible

Le schéma doit être produit depuis les équipes, responsabilités et interactions du modèle. Les choix de disposition graphique ne créent aucune donnée métier supplémentaire.

La convention visuelle à reprendre est jaune pour Stream-aligned, bleu pour Platform, rouge pour Enabling et orange pour Complicated-subsystem, avec formes distinctes et légende textuelle. Les ressources officielles permettent de préparer les gabarits. [Ressources Team Topologies](https://teamtopologies.com/resources)

La vue d’ensemble montre les utilisateurs ou clients servis, le flux de valeur et les équipes. La gouvernance apparaît dans un espace distinct. Les relations de décision, les dépendances logicielles et les trois modes d’interaction ne doivent pas être confondus.

Des vues par étape ou période montrent l’évolution des interactions sans créer trois copies d’une même équipe. Une vue centrée sur une équipe limite les croisements. La lecture doit rester possible au clavier, sur petit écran et à l’impression, avec accès aux fiches et une alternative tabulaire.

Les liens suivants sont des hypothèses à instruire, pas un graphe adopté :

| Interaction candidate | Objet | Mode envisagé |
| --- | --- | --- |
| PaaS avec équipes consommatrices | Chaîne de livraison, environnements et outillage | X-as-a-Service, avec collaboration initiale ciblée. |
| Case Management avec équipes consommatrices | Contrats de case, règles et moteurs génériques | Collaboration de découverte puis X-as-a-Service lorsque les contrats sont établis. |
| Les deux équipes issues du Core Engine avec leurs consommateurs | Services spécialisés de planification, stock et disponibilité | X-as-a-Service et collaborations bornées sur les contrats. |
| Intégration avec équipes produit et iPaaS | Compétences, contrats, raccordements et tests | Facilitating, avec objet et fin d’intervention explicites. |
| Portal avec équipes de domaine | XP APIs, parcours et contrôles d’accès | Collaboration ciblée à préciser. Les appels API ne déterminent pas seuls le mode. |

La publication des services et données des produits Stream-aligned, notamment MDM et Portal, doit être articulée à une plateforme d’exposition sans transférer leur responsabilité métier ni imposer un goulot central. [Principes de représentation](https://teamtopologies.com/how-to-use-shapes)

## Impacts et priorités

La portée ci-dessous qualifie le travail à préparer. Elle n’est ni une estimation en JH ni un budget.

| Priorité | Sujet | Portée | Effet attendu et dépendances |
| --- | --- | --- | --- |
| P1 | Principe des équipes produit durables | Structurante | Introduire l’orientation dans les fondamentaux et le parcours, puis la relier aux charges, coûts et capacités. |
| P1 | Métamodèle et propriétaire organisationnel | Structurante | Définir équipes, gouvernance, responsabilités, interactions et affectations avant les écrans. |
| P1 | Ventilation des lots Make | Forte | Repartir des travaux et rôles existants. Les lots commandes, process, décisions Supply et IT demandent un partage documenté. |
| P1 | Détail de l’intégration | Forte | Préciser volumes, scénarios, critères de recette, responsabilités, réutilisation et vagues à partir des financements actifs. |
| P1 | Coûts par équipe et phase | Forte | Dériver les affectations depuis la valorisation et le journal unique, avec contrôle des reliquats et partages. |
| P1 | Capacité dans le temps | Forte | Établir les hypothèses de disponibilité et de mobilisation avant de conclure à la faisabilité des équipes durables. |
| P1 | MDM cible | Forte, évolution de périmètre | Instruire source de vérité et responsabilités de données avant toute adoption d’un complément. |
| P1 | Transformation Office | Forte, réconciliation des missions | Séparer board, fonctions opérationnelles et responsabilités locales sans déduction budgétaire implicite. |
| P2 | Navigation et contenus | Moyenne à forte | Réordonner les dossiers, redistribuer les textes et préserver les anciennes routes et contextes. |
| P2 | Schéma et interactions | Moyenne à forte | Produire la représentation depuis le modèle avec vues temporelles et accessibilité. |
| P2 | MCO par équipe | Forte | Relier objets maintenus, activités annuelles et propriétaires. Distinguer produit, client et support. |
| P2 | Comparabilité Make/Buy | Forte | Conserver les responsabilités et contrats propres aux options, et réconcilier leurs résultats. |
| P2 | Exports et documentation | Moyenne | Embarquer les instances et contrats dans le téléchargement sans second métamodèle. |
| P2 | Contrôles et compatibilité | Transverse | Vérifier conservation des charges et montants, navigation et sauvegardes selon le périmètre touché. |
| P2 | Nettoyage d’AGENTS.md | Ciblée | Retirer les chiffres métier et économiques recopiés. Conserver les règles et renvois vers les propriétaires. |

### Composants à examiner lors de l’implémentation

| Ensemble | Fichiers ou familles concernés | Intervention à prévoir |
| --- | --- | --- |
| Contrats métier | `source/fondamentaux.yaml`, `source/glossaire.yaml`, `source/README.md`, futur propriétaire organisationnel et son schéma | Définitions, autorités, relations et règles de conservation. |
| Travaux Core | `source/estimations-core-retenues.yaml`, `source/fonctions-produit-core.yaml`, `source/calculs-estimation-core.yaml` | Rattachements traçables aux travaux, rôles et fonctions. Pas de recalibration automatique. |
| Intégration | `source/integration.yaml`, `source/unites-integration.yaml`, `source/parcours-integration.yaml`, `source/deploiement-groupe.yaml` et propriétaires de chiffrage | Volumes, responsabilités, affectations et calendrier. |
| MCO et financements | `source/maintenance.yaml`, `source/unites-maintenance.yaml`, `source/modele-composable.yaml`, `source/architecture.yaml` et propriétaires annuels | Attribution des coûts et charges, objets maintenus, gouvernance et moyens partagés. |
| Projection Python | `tools/fundamentals_model.py`, `tools/study_app.py`, `tools/gross_evaluations.py`, `tools/integration_units.py`, `tools/economic_reading.py`, `tools/composable_costs.py` selon les contrats retenus | Compilation et agrégation depuis les propriétaires. Aucun calcul économique parallèle dans React. |
| Écrans et navigation | `config/application.yaml`, `app/src/App.tsx`, `DeliveryOrganisationPage.tsx`, `GrossEvaluationsPage.tsx`, `economicNavigation.ts`, `readerNavigation.ts`, `dossierNavigation.ts`, `ReadingScopeContext.ts` | Parcours, sélecteurs équipe/phase, schémas et contextes conservés. |
| Export et livraison | `tools/export_business_model.py`, dépendances et manifestes de publication, `source/version-modele.yaml` | Inclusion cohérente des nouvelles instances actives. Révision du modèle seulement lors de l’évolution autorisée. |
| Documentation de travail | `AGENTS.md`, guides du modèle, de l’application et des commandes | Règles sans chiffres métier recopiés et documentation conforme à la nouvelle organisation. |
| Contrôles | Tests des fondamentaux, des charges, de l’intégration, des coûts composables, de l’export et de la navigation | Sélection ciblée selon les fichiers effectivement modifiés. |

Ces chemins désignent des consommateurs à examiner. Ils ne constituent pas une liste de fichiers à modifier systématiquement.

### Mesure des effets économiques

La redistribution d’une référence inchangée entre équipes doit restituer exactement ses charges et ses coûts, avec reliquats explicites. Elle ne crée pas un budget d’équipe supplémentaire.

Un changement de périmètre MDM, une capacité durable réservée, un travail d’intégration nouvellement démontré ou une évolution de calendrier peuvent modifier l’économie. Chacun exige une instruction et une décision propres.

L’effet économique net de la cible reste **à déterminer**. Les données disponibles ne permettent pas de chiffrer honnêtement un supplément global, une économie globale, l’effectif des onze équipes ou leur calendrier de constitution. La prochaine étape utile est de rapprocher les travaux existants avant d’estimer les écarts.

## Ordre de mise en œuvre proposé

| Étape | Résultat concret attendu | Critère de passage |
| --- | --- | --- |
| 1 | Principe directeur, périmètres et contrats de responsabilité | Ambition MDM, board, API, Orders communs et flux distingués des périmètres déjà estimés. |
| 2 | Extension du métamodèle et instances organisationnelles | Onze équipes cibles référencées, gouvernance séparée, types et statuts contrôlés. |
| 3 | Rapprochement des travaux et charges | Chaque travail connu est affecté ou explicitement non ventilé, par phase et rôle. |
| 4 | Attribution des coûts et projection temporelle | Totaux réconciliés, postes partagés et contributions externes visibles, capacités proposées séparément des charges. |
| 5 | Parcours, fiches et schéma | Lecture continue études → organisation → charges → économie → méthodes, avec anciennes routes conservées. |
| 6 | Instruction des écarts et scénarios de mobilisation | Évolutions de périmètre et moyens nouveaux justifiés avant adoption économique. |

Les niveaux 3 et 4 doivent conserver une première lecture à référence économique inchangée. Ils peuvent révéler un financement déjà présent, une affectation manquante ou un besoin nouveau. Ces trois résultats doivent rester distincts.

## Décisions encore à préciser

- Noms définitifs et contrats des deux équipes issues du Core Engine, dont la séparation entre affectation du plan, disponibilité, réservation et engagement.
- Périmètre MDM cible, domaines de vérité et transition depuis les systèmes maîtres actuels.
- Propriétaire des mécanismes communs d’Orders et frontières entre Sourcing & Procurement, B2C, Wholesale et Services.
- Frontières entre moteurs génériques, configurations métier, XP APIs, API de domaine et services techniques PaaS.
- Propriété durable des flux et de leur exploitation, contributions iPaaS et critère de sortie des interventions Enabling.
- Missions opérationnelles actuellement portées par le Transformation Office et organisation cible du board.
- Hypothèses de capacité, composition, recrutement, partenaires, transfert et continuité des compétences.
- Volumes d’intégration et besoins de MCO détaillés par équipe, puis règles de partage des coûts communs.

Ces décisions permettent de construire une cible examinable sans préjuger des charges nouvelles ou d’un engagement de réalisation.

## Critères de vérification pour une évolution future

- Le principe des équipes produit durables est visible dans l’étude et défini une seule fois.
- La cible comprend les onze équipes discutées et un Transformation Office sans type Team Topologies.
- Les mêmes identifiants d’équipe sont utilisés sur les trois étapes et les vues temporelles.
- Fiches, schémas, charges, coûts et export proviennent des mêmes données métier.
- Les charges et coûts par équipe et phase se rapprochent de la référence, avec reliquats et postes hors équipes.
- Les vues MCO distinguent produit générique, adaptations Beaumanoir et moyens techniques.
- La capacité disponible et la charge simultanée sont lisibles sans transformer les JH en effectifs implicites.
- Les évolutions de périmètre et de financement sont identifiées séparément de la redistribution.
- Java/Spring, Microsoft et SAP conservent leurs responsabilités, contextes, horizons et règles propres.
- Les sauvegardes personnelles et anciennes adresses restent compatibles.
- Le schéma respecte les conventions Team Topologies, dispose d’une légende, d’un accès clavier et d’une alternative textuelle.
- AGENTS.md contient des instructions et des références d’autorité, sans résumés chiffrés métier ou économiques.
- Les contrôles sont proportionnés aux fichiers touchés. La révision du modèle intervient une seule fois lors de son évolution autorisée.

## Sources de référence

Les orientations métier proviennent des échanges du 5 novembre 2026 dans cette conversation. Les types des équipes, l’ambition MDM et le principe de durabilité sont des orientations de cible, distinctes des instances actives.

Les constats courants s’appuient sur les fichiers liés dans l’audit, notamment le métamodèle, les estimations retenues, l’intégration, la maintenance, le financement du Transformation Office et la configuration de navigation. [Guide des propriétaires](../source/README.md) · [Guide de l’application](../app/README.md) · [Charte FLOW](../app/BRANDING.md) · [Règles de travail](../AGENTS.md).

Les références Team Topologies et Conway sont citées près des concepts qu’elles soutiennent. Elles fondent le cadre théorique et graphique. Elles ne valident ni le découpage FLOW proposé, ni ses charges, ni sa capacité de réalisation.
