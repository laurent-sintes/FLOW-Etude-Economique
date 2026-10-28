# Audit du référentiel fonctionnel de Flow Core System

Audit du 24 octobre 2026. Objet : vérifier la base fonctionnelle qui sert à estimer la réalisation Make du socle, depuis les capacités SCM de Cartographie Beaumanoir jusqu’aux fonctionnalités, points de complexité et charges.

## Conclusion pour le sponsor

**La liste a bien une origine dans la cartographie SCM, mais sa transformation en catalogue de réalisation n’est pas suffisamment justifiée pour défendre le chiffrage Make.** Les 39 fonctionnalités couvrent formellement les 88 capacités de l’extrait retenu, chacune une fois. Les noms, regroupements et points ont cependant été proposés pour l’étude : ils ne constituent ni les capacités natives de la cartographie ni une spécification approuvée.

L’audit n’identifie **aucune reprise directe des offres Synvance dans la définition des 39 fonctionnalités**. Le générateur historique retrouvé contient les regroupements et les points saisis explicitement, avec les identifiants de capacités SCM ; il n’importe pas les propositions commerciales. Le registre cite la cartographie et quatre appuis techniques publics. Cela ne permet pas d’exclure toute influence intellectuelle antérieure, mais ne justifie pas d’attribuer cette liste à Synvance. L’influence des offres est en revanche explicite dans les prix Buy et l’ancre d’intégration Make ; ces postes sont distincts du build Make audité ici.

**La bonne base de reprise est la hiérarchie métier existante : Domaine → Sous-domaine → Business Area → Capacité.** Les fonctionnalités à réaliser doivent être déduites sous ces capacités, avec leurs résultats, variantes et frontières. Les composants techniques et leurs possibilités de réemploi viennent ensuite. Il faut conserver les correspondances utiles de l’étude, réexaminer ses regroupements et recalibrer les charges concernées ; aucun nouveau prix ne découle automatiquement de cet audit.

## Ce qui est effectivement traçable

| Élément contrôlé | Résultat | Portée du constat |
|---|---|---|
| Domaine source | Supply Chain Management, identifiant `supply-chain-orchestration` | Le domaine demandé est bien celui utilisé. |
| Hiérarchie | 9 sous-domaines, 28 Business Areas | Les identifiants et relations hiérarchiques du périmètre capturé sont encore identiques dans la cartographie courante. |
| Capacités | 88 | Toutes ont un rattachement principal unique aux 39 fonctionnalités. Aucune capacité ajoutée ou retirée dans le périmètre comparé. |
| Autres objets de l’extrait | 74 comportements, 20 références | Présents dans la pièce justificative, mais sans matrice explicite de prise en charge dans les fonctionnalités et leur chiffrage. |
| Décomposition de l’étude | 39 fonctionnalités | Traduction et regroupement proposés par l’étude, retrouvés dans le script historique. |
| Complexité | 3 axes par fonctionnalité | Les 117 notes sont des jugements d’ingénierie ; la formule vérifie leur agrégation, pas leur pertinence. |
| Références marché dans la cartographie courante | Les 88 capacités en possèdent | L’extrait de l’étude ne conserve pas les champs `market_comparisons`. Les rapprochements doivent être récupérés avec leurs limites. |

Le fichier [Core System Features](../source/core-system-features.yaml) dit lui-même que les regroupements sont une interprétation produit de la cartographie, sans approbation du modèle source. Le [script historique](../tmp/yaml-stacks/create_features.py) confirme cette construction : noms, capacités et valeurs des trois axes sont saisis fonction par fonction. Les appellations intermédiaires F01 à F39 y sont converties en CSF-001 à CSF-039 ; elles ne prouvent pas une reprise des anciens identifiants Excel.

## Les problèmes à corriger

### 1 La structure métier disparaît dans les regroupements

Le champ `groupe` du référentiel emploie dix catégories propres à l’étude — stocks, plans, prestations, processus, services financiers, etc. — au lieu des neuf sous-domaines et vingt-huit Business Areas. Le schéma impose cette liste de groupes sans imposer le chemin métier. Les écrans de détail montrent les travaux et les composants, mais ne restituent pas le chemin des capacités : le lecteur ne peut pas reconnaître simplement la carte qui fonde le coût.

Plusieurs regroupements franchissent les frontières utiles à la lecture :

| Fonctionnalité | Regroupement constaté | Conséquence |
|---|---|---|
| CSF-003, vues de référence | 5 capacités appartenant à 5 Business Areas | Parties et accords, marchandises, emballages, fournitures internes et services deviennent un seul bloc de charge. |
| CSF-014 à 016 et CSF-023, plans | Préparation des plans et Master Plan Management sont mêlés | Recevoir, construire, interpréter et rapprocher des plans ne sont plus rattachables à leur responsabilité métier. |
| CSF-027, commandes de prestations | 15 capacités de 3 Business Areas | Prestations sur biens, transport et douane sont aplatis dans une seule fonction. Leur cycle commun peut être partagé, sans effacer leurs différences. |
| CSF-032, finance | Billing et Payment sont associés à Accounting Data Provision | Les deux premières capacités relèvent de Service Management ; la troisième relève d’Inventory State Management et prépare les faits des registres de stock et de propriété. Elle n’est pas une collecte centrale de tous les faits financiers. |
| CSF-010 et CSF-039 | Classés stocks et services transverses | Inventory Disposition est dans Fulfilment Orchestration ; Product Feedback est dans Inventory State Management. Le classement masque leurs rattachements. |

**Priorité : rétablir les chemins métier avant de modifier les scores.** Une fonction partagée peut contribuer à plusieurs capacités ; son coût doit rester identifié une seule fois. On ne peut pas répartir les forfaits actuels entre Business Areas par un simple prorata du nombre de capacités.

### 2 L’extrait conserve les capacités mais perd des explications utiles

L’extrait daté conserve les identifiants, noms, définitions, périmètres, liens hiérarchiques, références d’origine et hotspots. Il ne reprend pas les champs de comparaison avec les produits du marché, ni les autres champs pédagogiques aujourd’hui disponibles. Par exemple, la cartographie rapproche le réassort de fonctions documentées SAP et Dynamics, le CTP de Dynamics et SAP aATP/PP/DS, et le transport de fonctions de constitution de chargements et de planification. Les limites de ces rapprochements sont explicites dans la source.

Ces exemples de marché peuvent aider à décrire des fonctionnalités concrètes et usuelles. **Ils ne démontrent ni que tout le périmètre FLOW est un standard unique, ni qu’un composant choisi le fournit intégralement, ni le coût de le reconstruire.** La source précise souvent un recouvrement partiel et garde un statut proposé. Les références commerciales Synvance et la documentation produit doivent rester distinguées.

**Priorité : enrichir le prochain extrait avec les comparaisons, exemples et frontières utiles, avec date, origine et statut.** Les conserver comme preuves rattachées aux capacités ; ne pas recopier leur contenu dans les générateurs ou en faire de nouvelles exigences implicites.

### 3 La cartographie a évolué sans changement de ses identifiants

L’empreinte du fichier courant diffère de celle enregistrée lors de la capture. La hiérarchie et les 88 identifiants de capacités restent identiques, mais **36 périmètres de nœuds ont évolué, dont 23 capacités**, ainsi que la définition du domaine. Une partie des changements ajoute des liens vers les principes ; d’autres précisent réellement le contenu, notamment l’intercompany, les liens entre commandes, les faits de propriété, la facturation et les contextes de planification.

Ce constat ne signifie pas que 23 fonctions doivent être ajoutées ou que leurs coûts doivent augmenter. Il signifie que les fonctionnalités et leurs hypothèses doivent être relues sur ces différences. Les dates et versions déclarées du modèle n’ont pas suffi à signaler ces évolutions.

**Priorité : comparer les champs et empreintes lors d’une reprise, qualifier l’impact, puis seulement actualiser l’extrait et les évaluations dépendantes.** Les différences textuelles sont conservées dans le relevé d’audit. Aucun remplacement silencieux de l’extrait n’est effectué.

### 4 Une capacité métier ne suffit pas à imposer le mécanisme le plus complexe

Les fonctions principales ne sont pas inventées : l’ATP, le CTP, le réassort, l’affectation, le plan de transport et Process Management figurent bien dans la carte. Les difficultés de réalisation sont plausibles. **La profondeur retenue reste toutefois à établir**, particulièrement sur les blocs suivants :

| Bloc | Ce que la cartographie établit | Choix de réalisation à justifier avant calibration |
|---|---|---|
| Priorisation et affectation, CSF-018 | Choisir les demandes et ressources, préserver les engagements, expliquer les manques | Règles déterministes, heuristique ou solveur ; objectifs, taille des problèmes, stabilité et délai attendu. Le palier algorithmique 2100 n’est pas démontré par le seul mot affectation. |
| Optimisation des stocks, CSF-021/022 | Recommander cibles, protections, réservations et apports | Formules et stratégies réellement attendues, couplage entre décisions et modalités humaines ou automatisées. Un calcul par besoin ou par cible n’est pas automatiquement une optimisation globale. |
| CTP, CSF-025 | Vérifier les apports et capacités nécessaires à une promesse conditionnelle | Profondeur de contrôle des capacités et réemploi d’un calculateur ; ne pas présumer un ordonnanceur industriel complet. |
| Transport, CSF-029 | Construire le plan des transports confiés, chargements et trajets | Mandat du Core face au logisticien, règles de groupage et qualité de solution attendue. Les frontières de la carte excluent déjà un second plan local concurrent. |
| Process Management, CSF-033 à 038 | Définir, conduire, superviser et analyser les parcours et dossiers | Profondeur de configuration, interfaces, durabilité, interventions et analyse. CMMN, un studio de composition ou un algorithme d’alignement ne deviennent pas des exigences par simple proximité de vocabulaire. |

Les sources techniques citées dans le référentiel décrivent les familles de mécanismes. Elles ne fournissent pas les notes 800, 1300 ou 2100. La référence « autoriser ou suspendre un prestataire = 100 » est un choix relatif cohérent pour classer ; elle n’est pas un étalon de productivité observé. Les poids égaux et l’arrondi à 25 sont aussi des conventions de l’étude.

**Priorité : décrire, à la maille d’une étude d’opportunité, les quelques fonctions et variantes qui expliquent matériellement chaque difficulté.** Ne pas produire de fausses spécifications détaillées. Les choix d’architecture restent séparés des exigences métier, et les variantes de réalisation doivent être comparées avant de retenir leur charge.

### 5 Le passage aux JH est le maillon le moins étayé

Le moteur ne multiplie pas les points par un prix. Il lit les JH de configuration, extension, développement, assemblage, qualification et frontend, applique les hypothèses IA, puis les TJM, l’outillage et le pilotage. Modifier uniquement les points ne recalibrerait donc pas automatiquement les charges.

Les 39 vecteurs de JH de chacune des trois stacks Make correspondent aux tableaux saisis dans le [script historique de chiffrage](../tmp/yaml-stacks/create_cost_inputs.py). Le champ `travail_restant` décrit des travaux propres à chaque fonction, mais le champ `justification` répète **le même texte général pour les 39 lignes d’une même stack**. Les quatre ancres de la calibration décrivent le travail et annoncent des JH ; elles n’apportent pas de mesure indépendante ni de décomposition suffisante pour reproduire le choix de ces valeurs.

| Charges actuelles avant IA, backend et frontend | Java / Spring | .NET | Rust |
|---|---:|---:|---:|
| Ensemble des 39 fonctionnalités | 17 460 JH | 18 966 JH | 25 745 JH |
| Process Management, CSF-033 à 038 | 3 340 JH | 3 985 JH | 5 950 JH |
| Part de Process Management | 19,1 % | 21,0 % | 23,1 % |

Ces chiffres sont repris des entrées actives, **hors pilotage, intégration et MCO**, pour montrer l’importance de la revue. Ce ne sont ni de nouvelles estimations ni des économies identifiées. La profondeur des mécanismes et leur réemploi peuvent déplacer matériellement les écarts entre stacks ; l’audit ne permet pas d’en calculer le sens ou le montant.

**Priorité : justifier les JH par quelques blocs résiduels observables et une fourchette, après cadrage des fonctions et du réemploi.** Conserver une seule réalisation pour les mécanismes partagés. Revoir ensuite les trois Make et la couverture Buy sur le même besoin, sans chercher à préserver les totaux ou leur classement.

### 6 Les contrôles structurels ne vérifient pas la fidélité métier

Le validateur confirme les identifiants, l’unicité de rattachement des capacités, l’existence des références, les paliers et l’arithmétique des scores. Il n’établit pas que les comportements sont effectivement traités, que la formulation respecte toutes les frontières, que les fonctions partagées ne sont pas chiffrées deux fois ou que les JH sont calibrés.

La vérification de l’empreinte de provenance porte sur son format ; le validateur ne relit pas le fichier de cartographie courant pour comparer son contenu. Il n’existe pas non plus, dans ce contrat de données, de justification explicite de chaque regroupement, de statut de revue métier par fonction ou de séparation structurée entre exigence et choix de réalisation.

**Priorité : compléter les contrôles de traçabilité et prévoir une revue sémantique.** Un test logiciel peut contrôler les chemins, les références et les dépendances ; il ne peut pas approuver à lui seul la portée métier d’une fonctionnalité ou la suffisance de sa charge.

## Référentiel cible conforme à la cartographie

La navigation et la base doivent conserver **Domaine / Sous-domaine / Business Area**. Les capacités portent leurs identifiants, noms, définitions et frontières d’origine. Sous chacune, une ou plusieurs fonctionnalités décrivent les résultats logiciels nécessaires. Plusieurs capacités peuvent utiliser un mécanisme commun, sans fusionner leurs responsabilités ni compter ce mécanisme plusieurs fois.

Exemple de lecture, sans nouveau chiffrage :

| Niveau | Exemple |
|---|---|
| Domaine | Supply Chain Management |
| Sous-domaine | Inventory Management |
| Business Area | Inventory State Management |
| Capacité | Reservation (`D02.c`) |
| Fonctionnalités à préciser | Établir une réservation, la réviser, consommer ou libérer la quantité et traiter son expiration lorsqu’elle est prévue. |
| Frontières | L’affectation choisit la ressource ; la réservation porte l’engagement de quantité. Le calcul ATP et les politiques restent sous leurs responsabilités. |
| Réalisation puis estimation | Définir les garanties et variantes nécessaires, identifier les mécanismes disponibles par stack, puis chiffrer le travail restant. |

Le nombre de fonctionnalités n’est pas imposé à 39, ni à 88. La carte constitue une base exploitable : il est possible de retrouver des blocs SCM familiers sans inventer un nouveau découpage technique. Ce qui demande encore un travail d’estimation est la profondeur des fonctions, leurs interactions et le réemploi réellement possible.

Ordre de reprise proposé :

1. Actualiser de manière explicite l’extrait de preuve SCM, avec hiérarchie, périmètres, comportements, exemples et rapprochements marché utiles ; qualifier les différences recensées.
2. Reprendre la liste sous les Business Areas, garder les capacités reconnaissables et justifier les regroupements ou fonctions partagées. Traiter en priorité CSF-003, 014–016, 023, 027 et 032.
3. Décrire les résultats et variantes déterminants, puis distinguer besoin, réalisation générique du Core, configuration Beaumanoir et raccordements. Revoir en priorité les décisions d’optimisation et Process Management.
4. Réévaluer les apports des cinq stacks et les blocs de travaux résiduels. Documenter les charges et leurs plages ; ne pas conserver automatiquement les JH actuels par simple changement de nom.
5. Recalculer les budgets et présenter les différences par rapport au modèle précédent. Conserver les anciennes valeurs comme historique et indiquer les effets de périmètre, de réemploi et de calibration séparément.

L’audit n’autorise pas à annoncer un build moins cher, ni à supprimer une capacité parce que son estimation est fragile. Il établit que **les capacités SCM sont une base traçable, alors que leur traduction actuelle en fonctions et en charges doit être revue avant de défendre les montants Make**.

## Correspondance des 39 fonctionnalités

Tous les rattachements ci-dessous existent dans la cartographie. Les observations distinguent la légitimité de la capacité de la profondeur de réalisation et du montant encore à justifier. Les JH sont les charges actuellement saisies, backend et frontend réunis, **avant IA et hors pilotage** ; ce ne sont pas de nouvelles estimations.

| Fonctionnalité actuelle | Capacités source | Points | JH Java / .NET / Rust | Constat et suite |
|---|---|---:|---:|---|
| CSF-001 — Autoriser ou suspendre la sollicitation d’un prestataire | Service Provider Eligibility Control (`cap-service-provider-eligibility-control`) | 100 | 40 / 41 / 50 | Correspondance directe avec Service Provider Eligibility Control. La fonction est bornée ; le choix de 100 points et les JH restent des hypothèses, pas un étalon observé. |
| CSF-002 — Recevoir et rapprocher les référentiels sources | Reference Ingestion (`master-data-ingestion`) | 525 | 210 / 250 / 318 | Correspondance directe avec Reference Ingestion. Distinguer le contrat et les contrôles génériques des connecteurs et du nettoyage Beaumanoir. Qualifier les modes de réception nécessaires. |
| CSF-003 — Tenir les vues de référence opérationnelles | Partner & Agreement Reference Stewardship (`cap-partner-agreement-reference-stewardship`) ; Merchandise Reference Stewardship (`cap-merchandise-reference-stewardship`) ; Packaging Reference Stewardship (`cap-packaging-reference-stewardship`) ; Internal Supplies Reference Stewardship (`cap-internal-supplies-reference-stewardship`) ; Service Reference Stewardship (`cap-service-reference-stewardship`) | 800 | 380 / 385 / 465 | Cinq capacités de cinq Business Areas sont fusionnées. Conserver chacune comme entrée métier et décrire les fonctions partagées de référence ; le forfait de 380 JH Java ne permet pas de lire leur poids séparé. |
| CSF-004 — Définir et rendre applicables les politiques Supply | Demand Fulfilment Policy Management (`demand-fulfilment-policy-management`) | 1025 | 460 / 625 / 835 | Demand Fulfilment Policy Management justifie les politiques. Choisir la profondeur de versionnement, publication et interface de configuration avant de retenir un environnement de règles générique. |
| CSF-005 — Intégrer les faits de stock et tenir leur registre | Inventory Tracking (`D01.f`) ; Inventory Ledger (`D01.g`) | 975 | 485 / 495 / 625 | Inventory Tracking et Inventory Ledger justifient captation et registre. Séparer leurs fonctions de réception et de tenue des faits ; prouver que reprises et journaux ne sont pas recomptés dans les moteurs transverses. |
| CSF-006 — Restituer le stock présent, attendu et traçable | Inventory Visibility (`D01.c`) ; Planning Data Provision (`planning-data-provision`) | 875 | 340 / 345 / 433 | Inventory Visibility et Planning Data Provision justifient vue et fourniture. Conserver les deux résultats métier ; une même projection technique peut être réutilisée. |
| CSF-007 — Organiser et rapprocher les inventaires | Stocktaking (`D01.d`) | 400 | 220 / 225 / 283 | Stocktaking justifie les inventaires. Décliner campagne, tournant et ponctuel sans absorber les terminaux ou le geste physique des exécutants. |
| CSF-008 — Reconnaître et historiser la propriété des biens | Inventory Ownership Transfer Decision (`D01.h`) ; Inventory Ownership Ledger (`inventory-ownership-ledger`) | 800 | 350 / 375 / 465 | Décision et registre de propriété sont regroupés dans la bonne Business Area. Ajouter à la revue les chaînes intercompany précisées dans la cartographie courante ; ne pas absorber la valorisation comptable. |
| CSF-009 — Réserver, consommer et libérer les quantités | Reservation (`D02.c`) | 1025 | 485 / 500 / 640 | Reservation est directement reconnue. Expiration et concurrence sont pertinentes mais leurs volumes, délais et garanties doivent justifier le niveau de tests et de réalisation. |
| CSF-010 — Décider du devenir des biens | Inventory Disposition Decision (`D05.i`) | 525 | 250 / 285 / 370 | Inventory Disposition Decision appartient à Fulfilment Orchestration / Inventory Disposition. Le groupe actuel stocks masque ce rattachement. La fonction de décision est justifiée, sans exécution de réparation ou rebut. |
| CSF-011 — Gérer ventes, achats, transferts et consignations | Sales Order (`D04.i`) ; Purchase Order (`D04.j`) ; Transfer Order (`D04.k`) ; Consignment Fill-up Order (`D04.r`) ; Consignment Pick-up Order (`D04.t`) | 1225 | 650 / 670 / 825 | Les cinq familles de commandes sont présentes dans Order Lifecycle Management. Les distinguer en lecture métier tout en partageant les fonctions de cycle ; reprendre les précisions intercompany et plans sans multiplier cinq fois le socle. |
| CSF-012 — Gérer les retours clients et fournisseurs | Return Order (`D04.l`) ; Supplier Return Order (`D04.m`) | 975 | 425 / 440 / 555 | Les retours client et fournisseur sont bien présents. Séparer les parcours et leurs résolutions ; conserver les frontières avec avoir, remboursement, propriété et gestes physiques. |
| CSF-013 — Scinder, regrouper et recomposer les commandes | Order Structuring (`D04.n`) | 775 | 390 / 410 / 528 | Order Structuring justifie scission, regroupement et fusion. La cartographie courante ajoute les liens réciproques intercompany ; leur profondeur doit être rapprochée du forfait actuel. |
| CSF-014 — Recevoir et qualifier les contributions de planification | Plan Ingestion (`plans-ingestion`) ; Demand Forecast Qualification (`demand-forecast-development`) | 525 | 220 / 265 / 328 | Plan Ingestion et Demand Forecast Qualification relèvent de deux Business Areas. Séparer réception d’une contribution et qualification de la prévision, sans recréer le moteur de prévision produit. |
| CSF-015 — Construire et lire le plan de demande | Demand Plan Development (`demand-plan-development`) ; Demand Plan Visibility (`demand-plan-visibility`) | 875 | 380 / 410 / 510 | Demand Plan Development et Demand Plan Visibility relèvent de deux Business Areas. Calculer le plan et interpréter une contribution externe sont des fonctions différentes ; maintenir leur visibilité. |
| CSF-016 — Construire et lire le plan d’approvisionnement | Supply Plan Development (`supply-plan-development`) ; Supply Plan Visibility (`plans-visibility`) | 875 | 405 / 425 / 540 | Supply Plan Development et Supply Plan Visibility relèvent de deux Business Areas. Distinguer projection et interprétation, sans déduire une planification amont complète de leur regroupement. |
| CSF-017 — Calculer et tenir le Master Plan | Master Planning (`D05.f`) | 975 | 540 / 565 / 705 | Master Planning justifie le calcul net et la cohérence du plan. Le score ne doit pas recomptabiliser affectation, ATP, CTP et simulation ; formaliser les interfaces de réemploi. |
| CSF-018 — Prioriser la demande et affecter les ressources | Demand Prioritization (`D03.m`) ; Supply Assignment (`D03.o`) | 1825 | 640 / 670 / 965 | Demand Prioritization et Supply Assignment sont explicites. La recherche combinatoire est une hypothèse de réalisation ; préciser les règles, objectifs et volumes qui la rendent nécessaire avant de retenir le palier 2100. |
| CSF-019 — Décider la libération en livraison | Delivery Release Decision (`delivery-release-decision`) | 875 | 340 / 380 / 465 | Delivery Release Decision correspond directement. Conserver la séparation entre décider, modifier la commande et libérer une prestation ; l’automatisation de toutes les décisions n’est pas démontrée. |
| CSF-020 — Appliquer les décisions du plan et constater leurs effets | Plan Application (`D02.e`) | 1125 | 470 / 460 / 650 | Plan Application est explicite. Distinguer le protocole générique d’application des raccordements réels ; les derniers ajouts de contexte de plan et de validité doivent être examinés. |
| CSF-021 — Optimiser les cibles, protections et conditions de réservation | Physical Stock Target Optimization (`D05.a`) ; Logical Stock Protection Optimization (`D05.d`) ; Reservation Rule Optimization (`D05.h`) | 1575 | 565 / 625 / 835 | Trois optimisations distinctes sont regroupées. Définir pour chacune le résultat, les règles et la profondeur attendue ; les références ne prouvent pas qu’un solveur commun ou une optimisation couplée maximale soit requis. |
| CSF-022 — Décider les réapprovisionnements et redistributions | Replenishment (`D05.e`) ; Stock Redistribution (`D05.c`) | 1575 | 580 / 640 / 855 | Replenishment et Stock Redistribution sont explicites. Conserver séparément leurs décisions et montrer leurs coopérations ; les calculs par besoin et par cible ne justifient pas à eux seuls une optimisation globale. |
| CSF-023 — Simuler et rapprocher les scénarios de plan | Simulation & Analysis (`BHV006`) ; Planning Scenario Reconciliation (`planning-scenario-reconciliation`) | 1125 | 530 / 540 / 660 | Simulation & Analysis et Planning Scenario Reconciliation relèvent de deux Business Areas. Séparer simulation et choix de version ; démontrer la réutilisation des calculateurs déjà financés. |
| CSF-024 — Calculer la disponibilité promettable — ATP | Available-to-Promise (ATP) (`D03.i`) | 1400 | 570 / 610 / 700 | ATP est une capacité native de la cartographie. Distinguer stock présent et projeté, puis qualifier les règles de promesse et exigences de cohérence ; le caractère standard de la notion ne prouve pas les JH. |
| CSF-025 — Vérifier la faisabilité d’une promesse — CTP | Capable-to-Promise (CTP) (`D03.j`) | 1825 | 635 / 585 / 1005 | CTP est explicite, avec faisabilité par apports et par capacités. Le besoin ne prescrit pas un ordonnanceur d’usine. Revoir le palier combinatoire et l’achat ou le développement du calculateur sur un mandat concret. |
| CSF-026 — Comparer économiquement les promesses — PTP | Profitable-to-Promise (PTP) (`D03.k`) | 975 | 390 / 435 / 550 | PTP est une décision économique explicite, pas une simple restitution de coûts. Le titre Comparer réduit cette intention ; préciser choix, autorité et données tout en réutilisant ATP et CTP. |
| CSF-027 — Gérer les commandes de prestations | Picking Order (`service-order-picking`) ; Packing Order (`service-order-packing`) ; Cross-Docking Order (`service-order-cross-docking`) ; Transport Order (`service-order-transport`) ; Labeling Order (`service-order-labeling`) ; Kitting Order (`service-order-kitting`) ; Garment Finishing Order (`service-order-garment-finishing`) ; Cleaning Order (`service-order-cleaning`) ; Repair & Alteration Order (`service-order-repair-alteration`) ; Personalization Order (`service-order-personalization`) ; Inspection Order (`service-order-inspection`) ; Transport Booking Order (`service-order-transport-booking`) ; Customs Clearance Order (`service-order-customs-clearance`) ; Receiving Order (`service-order-receiving`) ; Scrapping Order (`service-order-scrapping`) | 1225 | 555 / 575 / 735 | Quinze capacités de trois Business Areas sont fusionnées. Conserver prestations sur biens, transport et douane dans leur structure ; distinguer le cycle partagé des exigences propres. Aucune reconstruction WMS/TMS/douane complète n’est justifiée. |
| CSF-028 — Établir les besoins de prestation et choisir les exécutants | Service Capacity Visibility (`D06.b`) ; Service Requirements Decision (`D07.a`) ; Service Selection Decision (`D06.e`) | 1125 | 425 / 455 / 605 | Trois capacités de Service Planning sont présentes. Séparer connaissance des capacités, détermination du besoin et sélection ; aucun planning interne d’exécutant ne doit être ajouté. |
| CSF-029 — Décider des regroupements et trajets de transport | Transport Plan Decision (`transport-plan-decision`) | 1675 | 680 / 600 / 1160 | Transport Plan Decision existe réellement, avec chargement et routage. Le mandat exact reste ouvert ; le recours retenu à des solveurs ou heuristiques et ses 680 à 1160 JH avant IA doivent être justifiés par les fonctions confiées. |
| CSF-030 — Coordonner et adapter la réalisation des prestations | Fulfilment Coordination (`D06.d`) ; Fulfilment Adaptation Decision (`D06.f`) ; Service Order Release Decision (`service-order-release-decision`) | 1400 | 540 / 610 / 800 | Coordination, adaptation et décision de libération sont explicites. Distinguer les règles métier de la conduite générique des dossiers, financée dans Process Management. |
| CSF-031 — Rapprocher et restituer les faits d’exécution | Operations Tracking (`D07.d`) ; Service Reconciliation (`D07.c`) ; Operations Visibility (`operations-visibility`) | 1025 | 395 / 455 / 565 | Tracking, Reconciliation et Visibility sont présents. Conserver trois résultats identifiables et un seul traitement des faits ; le reçu technique n’est pas une preuve métier. |
| CSF-032 — Porter facturation, paiements et échanges de faits avec Finance | Billing (`service-order-billing`) ; Payment (`service-order-payment-collection`) ; Accounting Data Provision (`accounting-data-provision`) | 1225 | 455 / 505 / 620 | Regroupement à corriger : Billing et Payment sont dans Service Management / Financial Services ; Accounting Data Provision est dans Inventory Management / Inventory State Management et ne centralise pas tous les faits financiers. Distinguer ces contrats avant toute ventilation. |
| CSF-033 — Définir et adapter les parcours réutilisables | Process Definition Management (`workflow-definition-management`) ; Process Planning (`order-workflow-planning`) | 1400 | 640 / 750 / 1270 | Définition et planification des processus existent. La capacité ne prescrit aucun studio ou langage ; qualifier le niveau d’interface et de composition générique réellement nécessaire. |
| CSF-034 — Exécuter les dossiers et réagir aux événements — Case Management | Process Sentry (`order-workflow-sentry`) ; Process Orchestration (`order-workflow-orchestration`) | 1825 | 500 / 750 / 1400 | Sentry et Orchestration existent dans Reactive Workflow Management. Case Management est une interprétation de réalisation cohérente avec les dossiers source ; CMMN et le choix du moteur restent des décisions d’architecture, pas des exigences déduites automatiquement. |
| CSF-035 — Gérer le travail humain, les files et les échéances | Human Task Management (`human-task-management`) ; Work Assignment (`work-assignment`) ; Work Deadline Management (`work-deadline-management`) | 1025 | 490 / 630 / 930 | Les trois capacités Human Task Management, Work Assignment et Work Deadline Management sont présentes. Décrire le résultat de travail humain avant de choisir files, formulaires et outillage ; réutiliser l’exécution durable. |
| CSF-036 — Intervenir sur les dossiers et résoudre les exceptions | Process Intervention (`process-intervention`) ; Process Exception Management (`process-exception-management`) | 1300 | 520 / 580 / 720 | Intervention et Exception Management sont explicites. Qualifier les interventions permises et les garanties attendues ; ne pas promettre une compensation universelle des actes irréversibles. |
| CSF-037 — Historiser et restituer dossiers, tâches et décisions | Process Ledger (`process-ledger`) ; Process, Tasks & Order Visibility (`BHV082`) | 1400 | 570 / 635 / 820 | Process Ledger et Process, Tasks & Order Visibility sont présents. Séparer la capture sous responsabilité de chaque producteur, la conservation et les vues ; examiner les précisions intercompany récentes. |
| CSF-038 — Analyser les parcours et partager les indicateurs | Process Mining (`process-mining`) ; Operational Analysis & Reporting (`operational-analysis-reporting`) | 1300 | 620 / 640 / 810 | Process Mining et Operational Analysis & Reporting sont présents. Les métriques et parcours sont justifiés ; un article sur les alignements optimaux n’établit pas le coût d’une analyse bornée. Définir le niveau de découverte et de conformité attendu. |
| CSF-039 — Partager les constats terrain sur les produits | Product Feedback (`product-feedback`) | 200 | 120 / 125 / 150 | Product Feedback est dans Inventory Management / Inventory State Management. Le groupe services_transverses en masque l’origine ; conserver le retour terrain vers le domaine produit, sans reconstruire le PLM. |

## Lecture selon la hiérarchie métier

**Domaine : Supply Chain Management.** Les neuf sous-domaines et les vingt-huit Business Areas ci-dessous gardent les noms et les rattachements de la cartographie courante. Sous chaque Business Area, les capacités renvoient aux fonctionnalités actuelles. Une fonctionnalité peut apparaître dans plusieurs Business Areas : ce renvoi ne duplique ni travail ni coût. Une future décomposition doit identifier le mécanisme partagé et ses usages plutôt que répartir forfaitairement son prix.

### Master Plan

#### Master Plan Management

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Plan Application (`D02.e`) | CSF-020 — Appliquer les décisions du plan et constater leurs effets |
| Master Planning (`D05.f`) | CSF-017 — Calculer et tenir le Master Plan |
| Simulation & Analysis (`BHV006`) | CSF-023 — Simuler et rapprocher les scénarios de plan |
| Plan Ingestion (`plans-ingestion`) | CSF-014 — Recevoir et qualifier les contributions de planification |
| Supply Plan Visibility (`plans-visibility`) | CSF-016 — Construire et lire le plan d’approvisionnement |
| Demand Plan Visibility (`demand-plan-visibility`) | CSF-015 — Construire et lire le plan de demande |

#### Stock Optimization

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Physical Stock Target Optimization (`D05.a`) | CSF-021 — Optimiser les cibles, protections et conditions de réservation |
| Logical Stock Protection Optimization (`D05.d`) | CSF-021 — Optimiser les cibles, protections et conditions de réservation |
| Replenishment (`D05.e`) | CSF-022 — Décider les réapprovisionnements et redistributions |
| Stock Redistribution (`D05.c`) | CSF-022 — Décider les réapprovisionnements et redistributions |
| Reservation Rule Optimization (`D05.h`) | CSF-021 — Optimiser les cibles, protections et conditions de réservation |

#### Order Backlog Management

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Demand Prioritization (`D03.m`) | CSF-018 — Prioriser la demande et affecter les ressources |
| Supply Assignment (`D03.o`) | CSF-018 — Prioriser la demande et affecter les ressources |
| Delivery Release Decision (`delivery-release-decision`) | CSF-019 — Décider la libération en livraison |

#### Demand & Supply Plan Preparation

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Demand Forecast Qualification (`demand-forecast-development`) | CSF-014 — Recevoir et qualifier les contributions de planification |
| Supply Plan Development (`supply-plan-development`) | CSF-016 — Construire et lire le plan d’approvisionnement |
| Planning Scenario Reconciliation (`planning-scenario-reconciliation`) | CSF-023 — Simuler et rapprocher les scénarios de plan |
| Demand Plan Development (`demand-plan-development`) | CSF-015 — Construire et lire le plan de demande |

### Operational References

#### Partner & Agreement References

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Partner & Agreement Reference Stewardship (`cap-partner-agreement-reference-stewardship`) | CSF-003 — Tenir les vues de référence opérationnelles |

#### Merchandise References

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Merchandise Reference Stewardship (`cap-merchandise-reference-stewardship`) | CSF-003 — Tenir les vues de référence opérationnelles |

#### Packaging References

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Packaging Reference Stewardship (`cap-packaging-reference-stewardship`) | CSF-003 — Tenir les vues de référence opérationnelles |

#### Internal Supplies & Equipment References

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Internal Supplies Reference Stewardship (`cap-internal-supplies-reference-stewardship`) | CSF-003 — Tenir les vues de référence opérationnelles |

#### Service References

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Service Reference Stewardship (`cap-service-reference-stewardship`) | CSF-003 — Tenir les vues de référence opérationnelles |

#### Reference Maintenance

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Reference Ingestion (`master-data-ingestion`) | CSF-002 — Recevoir et rapprocher les référentiels sources |

### Order Management

#### Order Lifecycle Management

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Sales Order (`D04.i`) | CSF-011 — Gérer ventes, achats, transferts et consignations |
| Purchase Order (`D04.j`) | CSF-011 — Gérer ventes, achats, transferts et consignations |
| Transfer Order (`D04.k`) | CSF-011 — Gérer ventes, achats, transferts et consignations |
| Return Order (`D04.l`) | CSF-012 — Gérer les retours clients et fournisseurs |
| Supplier Return Order (`D04.m`) | CSF-012 — Gérer les retours clients et fournisseurs |
| Order Structuring (`D04.n`) | CSF-013 — Scinder, regrouper et recomposer les commandes |
| Consignment Fill-up Order (`D04.r`) | CSF-011 — Gérer ventes, achats, transferts et consignations |
| Consignment Pick-up Order (`D04.t`) | CSF-011 — Gérer ventes, achats, transferts et consignations |

### Inventory Management

#### Inventory State Management

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Inventory Tracking (`D01.f`) | CSF-005 — Intégrer les faits de stock et tenir leur registre |
| Inventory Ledger (`D01.g`) | CSF-005 — Intégrer les faits de stock et tenir leur registre |
| Inventory Visibility (`D01.c`) | CSF-006 — Restituer le stock présent, attendu et traçable |
| Stocktaking (`D01.d`) | CSF-007 — Organiser et rapprocher les inventaires |
| Reservation (`D02.c`) | CSF-009 — Réserver, consommer et libérer les quantités |
| Accounting Data Provision (`accounting-data-provision`) | CSF-032 — Porter facturation, paiements et échanges de faits avec Finance |
| Planning Data Provision (`planning-data-provision`) | CSF-006 — Restituer le stock présent, attendu et traçable |
| Product Feedback (`product-feedback`) | CSF-039 — Partager les constats terrain sur les produits |

#### Inventory Ownership Management

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Inventory Ownership Transfer Decision (`D01.h`) | CSF-008 — Reconnaître et historiser la propriété des biens |
| Inventory Ownership Ledger (`inventory-ownership-ledger`) | CSF-008 — Reconnaître et historiser la propriété des biens |

### Fulfilment Orchestration

#### Service Planning

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Service Capacity Visibility (`D06.b`) | CSF-028 — Établir les besoins de prestation et choisir les exécutants |
| Service Requirements Decision (`D07.a`) | CSF-028 — Établir les besoins de prestation et choisir les exécutants |
| Service Selection Decision (`D06.e`) | CSF-028 — Établir les besoins de prestation et choisir les exécutants |
| Transport Plan Decision (`transport-plan-decision`) | CSF-029 — Décider des regroupements et trajets de transport |

#### Execution Assurance

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Service Reconciliation (`D07.c`) | CSF-031 — Rapprocher et restituer les faits d’exécution |
| Operations Tracking (`D07.d`) | CSF-031 — Rapprocher et restituer les faits d’exécution |
| Operations Visibility (`operations-visibility`) | CSF-031 — Rapprocher et restituer les faits d’exécution |

#### Execution Coordination

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Fulfilment Coordination (`D06.d`) | CSF-030 — Coordonner et adapter la réalisation des prestations |
| Fulfilment Adaptation Decision (`D06.f`) | CSF-030 — Coordonner et adapter la réalisation des prestations |
| Service Order Release Decision (`service-order-release-decision`) | CSF-030 — Coordonner et adapter la réalisation des prestations |

#### Inventory Disposition

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Inventory Disposition Decision (`D05.i`) | CSF-010 — Décider du devenir des biens |

### Availability

#### Order Promising

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Available-to-Promise (ATP) (`D03.i`) | CSF-024 — Calculer la disponibilité promettable — ATP |
| Capable-to-Promise (CTP) (`D03.j`) | CSF-025 — Vérifier la faisabilité d’une promesse — CTP |
| Profitable-to-Promise (PTP) (`D03.k`) | CSF-026 — Comparer économiquement les promesses — PTP |

### Supply Policy Management

#### Demand & Supply Policies

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Demand Fulfilment Policy Management (`demand-fulfilment-policy-management`) | CSF-004 — Définir et rendre applicables les politiques Supply |

#### Service Provider Controls

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Service Provider Eligibility Control (`cap-service-provider-eligibility-control`) | CSF-001 — Autoriser ou suspendre la sollicitation d’un prestataire |

### Service Management

#### Goods Processing Order Management

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Picking Order (`service-order-picking`) | CSF-027 — Gérer les commandes de prestations |
| Packing Order (`service-order-packing`) | CSF-027 — Gérer les commandes de prestations |
| Cross-Docking Order (`service-order-cross-docking`) | CSF-027 — Gérer les commandes de prestations |
| Labeling Order (`service-order-labeling`) | CSF-027 — Gérer les commandes de prestations |
| Kitting Order (`service-order-kitting`) | CSF-027 — Gérer les commandes de prestations |
| Garment Finishing Order (`service-order-garment-finishing`) | CSF-027 — Gérer les commandes de prestations |
| Cleaning Order (`service-order-cleaning`) | CSF-027 — Gérer les commandes de prestations |
| Repair & Alteration Order (`service-order-repair-alteration`) | CSF-027 — Gérer les commandes de prestations |
| Personalization Order (`service-order-personalization`) | CSF-027 — Gérer les commandes de prestations |
| Inspection Order (`service-order-inspection`) | CSF-027 — Gérer les commandes de prestations |
| Receiving Order (`service-order-receiving`) | CSF-027 — Gérer les commandes de prestations |
| Scrapping Order (`service-order-scrapping`) | CSF-027 — Gérer les commandes de prestations |

#### Transport Order Management

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Transport Order (`service-order-transport`) | CSF-027 — Gérer les commandes de prestations |
| Transport Booking Order (`service-order-transport-booking`) | CSF-027 — Gérer les commandes de prestations |

#### Financial Services

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Billing (`service-order-billing`) | CSF-032 — Porter facturation, paiements et échanges de faits avec Finance |
| Payment (`service-order-payment-collection`) | CSF-032 — Porter facturation, paiements et échanges de faits avec Finance |

#### Customs Services

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Customs Clearance Order (`service-order-customs-clearance`) | CSF-027 — Gérer les commandes de prestations |

### Process Management

#### Reactive Workflow Management

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Process Definition Management (`workflow-definition-management`) | CSF-033 — Définir et adapter les parcours réutilisables |
| Process Sentry (`order-workflow-sentry`) | CSF-034 — Exécuter les dossiers et réagir aux événements — Case Management |
| Process Planning (`order-workflow-planning`) | CSF-033 — Définir et adapter les parcours réutilisables |
| Process Orchestration (`order-workflow-orchestration`) | CSF-034 — Exécuter les dossiers et réagir aux événements — Case Management |

#### Process Supervision

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Process, Tasks & Order Visibility (`BHV082`) | CSF-037 — Historiser et restituer dossiers, tâches et décisions |
| Process Intervention (`process-intervention`) | CSF-036 — Intervenir sur les dossiers et résoudre les exceptions |
| Process Exception Management (`process-exception-management`) | CSF-036 — Intervenir sur les dossiers et résoudre les exceptions |
| Process Ledger (`process-ledger`) | CSF-037 — Historiser et restituer dossiers, tâches et décisions |

#### Human Work Management

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Human Task Management (`human-task-management`) | CSF-035 — Gérer le travail humain, les files et les échéances |
| Work Assignment (`work-assignment`) | CSF-035 — Gérer le travail humain, les files et les échéances |
| Work Deadline Management (`work-deadline-management`) | CSF-035 — Gérer le travail humain, les files et les échéances |

#### Process Intelligence

| Capacité de la cartographie | Fonctionnalité actuelle |
|---|---|
| Process Mining (`process-mining`) | CSF-038 — Analyser les parcours et partager les indicateurs |
| Operational Analysis & Reporting (`operational-analysis-reporting`) | CSF-038 — Analyser les parcours et partager les indicateurs |

## Mise en application : référentiel et grille de complexité

La [grille métier](../source/grille-complexite.yaml) reprend les 88 capacités sous leurs neuf sous-domaines et vingt-huit Business Areas, avec 258 fonctions observables et les 74 comportements source comme variantes explicites. La [capture du 24 octobre](../sources/cartographie-scm-2026-10-24.yaml) conserve désormais tous les champs pédagogiques et les comparaisons marché avec leurs limites, ainsi que les 37 changements de champs depuis la capture initiale. L’ancien extrait reste intact.

Les sept regroupements traversant plusieurs Business Areas sont décomposés ; Accounting Data Provision reste dans Inventory State Management, Billing et Payment dans Financial Services. Les fonctions de planification, les quinze prestations et les cinq familles de références sont reconnaissables séparément. Les variations intercompany, propriété et contexte de plan sont prises en compte dans les fonctions et leurs frontières.

La [méthode](../source/methode-complexite.yaml) remplace les anciens points par trois niveaux ordinaux justifiés séparément. Les niveaux proposés qualifient le périmètre décrit, sans présumer un moteur universel, un solveur global, des volumes de production ou une précision de charge. Les familles de réemploi sont explicites, sans prix distribué entre capacités. La grille conserve les identifiants CSF uniquement pour retrouver les évaluations antérieures.

Les étapes 1 à 3 de reprise sont matérialisées dans cette grille, sous statut de proposition à revoir avec le métier. Les contrôles vérifient notamment hiérarchie, capacités, comportements, empreintes et impossibilité d’hériter des JH. Ils ne valent pas validation sémantique. Les étapes 4 et 5 — couverture détaillée des cinq stacks, plages de JH résiduelles et nouveaux budgets — restent à réaliser sur les scénarios retenus. Les anciens coûts sont signalés comme tels dans l’application ; aucun nouveau prix n’est prétendu calibré par cette restructuration.

## Pièces et contrôles de l’audit

- [État des rattachements, références marché, écarts de texte et empreintes](2026-10-24-tracabilite-fonctionnelle.yaml). Ce relevé est une preuve d’audit datée, pas un référentiel concurrent ni une source de prix.
- [Référentiel fonctionnel actif](../source/core-system-features.yaml), [extrait SCM utilisé](../sources/cartographie-scm-2026-10-22.yaml), [schéma commun](../source/schema-core-system-features.yaml).
- [Calibration](../source/calibration-couts.yaml), chiffrages [Java](../source/chiffrage/chiffrage-java-spring.yaml), [.NET](../source/chiffrage/chiffrage-dotnet.yaml) et [Rust](../source/chiffrage/chiffrage-rust.yaml).
- [Validateur fonctionnel](../tools/validate_core_features.py), [validateur des solutions](../tools/validate_core_solutions.py) et [moteur de coût](../tools/calculate_costs.py). Les deux validations structurelles passent : 39 fonctionnalités, 88 capacités attribuées une fois, cinq solutions cohérentes. Cela ne valide pas le choix des mécanismes ni les JH.
- Scripts historiques retrouvés : [construction des fonctionnalités](../tmp/yaml-stacks/create_features.py), [construction des charges](../tmp/yaml-stacks/create_cost_inputs.py). Leur AST est lu sans exécuter les scripts : les 39 noms, rattachements et triplets de points correspondent au référentiel actuel ; les 39 vecteurs backend et frontend de chacune des trois stacks Make correspondent aux charges actuelles. Les empreintes sont conservées dans le relevé pour identifier ces témoins temporaires.

Le contrôle de la cartographie porte sur le fichier local `C:/Dev/Beaumanoir Cartographie/modeles/backlog/model.yaml`, lu le 24 octobre 2026. Sa version déclarée et sa date de modèle restent identiques à celles de la capture, alors que son empreinte diffère. Le contrôle compare donc les identifiants, les relations et les champs, pas seulement ces métadonnées. Aucun YAML fonctionnel, aucune évaluation de solution et aucun budget n’ont été remplacés par cet audit.
