# Audit global de lecture du framework d’évaluation

Audit du 28 octobre 2026, sur les sources courantes et le rendu de l’application locale.

**Le framework possède une logique méthodologique solide. Sa restitution oblige encore le lecteur à reconstruire certaines frontières : méthode cible et chiffres actuels, programme et périmètre chiffré, construction du Core et Build, fonctionnement et Run.** Plusieurs intitulés raccourcissent leur objet au point de changer ce qu’ils semblent désigner. La confiance d’un expert dépend en priorité de la correction de ces ambiguïtés.

Le cas « Développeur et extensions » est confirmé. Il révèle un problème plus large de libellés composés à partir du vocabulaire interne, alors que les sources contiennent souvent une formulation métier plus claire.

L’audit porte sur les sept pages du Framework, leurs tableaux et formules, les six fiches produit, les définitions et les pièces utiles à leur interprétation. Les formules présentant une ambiguïté ont été rapprochées de leur calcul exécuté. Il ne constitue pas une nouvelle calibration ni une vérification exhaustive de chaque référence externe. Aucun fichier de production, chiffre ou paramètre de simulation n’a été modifié.

## Ce qui fonctionne déjà

- La Vue d’ensemble pose correctement l’étude d’opportunité avant le cadrage applicatif détaillé et rend le paramétrage visible comme moyen de discuter les scénarios.
- La cartographie sert aux deux démarches. Synvance est bien identifié comme l’entrée principale du Buy ; les écarts de périmètre, notamment Finance SAP, sont signalés.
- La méthode Core suit un raisonnement compréhensible : besoin métier, fonctions, travaux restants, charges, consolidation. Chaque étape explique sa raison d’être et son résultat.
- Brut, net, effort humain et budget en euros sont distingués. La réutilisation déjà prise en compte ne reçoit pas une seconde remise. Les forfaits ne sont pas artificiellement convertis en charges observées.
- Le classement Build/Run est présenté comme une convention de l’étude. Le choix de classer le MCO Core en Build n’est pas une anomalie à corriger.
- Les sources et les calculs préservent les financements uniques, les inclusions et les périodes. L’audit n’a pas établi d’erreur arithmétique dans les formules examinées.
- Les limites du diagnostic COCOMO, l’origine historique des charges et l’absence de total humain complet sont effectivement visibles. Il faut améliorer leur articulation, sans accumuler de nouvelles réserves.
- Aucun accordéon ne subsiste dans le parcours examiné. Les titres, le gras, les formules et les sommaires ont une présentation cohérente.

## Priorité 1 — Clarifier ce que le lecteur peut déduire des chiffres et des preuves

### 1. Montrer les deux chaînes qui coexistent aujourd’hui

Dans les Fondamentaux, la charge brute est décrite comme les « JH développeur restant à réaliser après réutilisation ». La provenance des chiffres précise ensuite que la base active comprend plusieurs natures de travaux, dont la qualification indépendante. Les deux informations sont présentes, mais le lecteur doit réconcilier leurs périmètres.

La source de statut possède déjà le libellé « Méthode cible : estimation par le skill ». Ce repère n’est plus rendu dans la carte des charges. L’encart de la page Core s’intitule parallèlement « Une méthode appliquée par un skill ».

**Effet sur la lecture :** croire que les JH affichés proviennent déjà de la méthode détaillée, puis devoir réviser cette compréhension à la lecture de la réserve.

**Correction recommandée :** deux repères courts, côte à côte ou successifs, au même endroit dans les Fondamentaux :

- **Méthode cible :** développement brut estimé par le skill, avec tests développeur et sans QA indépendante.
- **Calcul actuel :** travaux enregistrés par nature, qualification indépendante comprise ; la nouvelle méthode ne les a pas encore recalibrés.

Relier la seconde ligne à sa provenance active. Remplacer « appliquée par un skill » par **« outillée par un skill »** et définir brièvement le skill comme une procédure exécutée à la demande par un assistant IA pour préparer un dossier d’estimation traçable. Ne pas laisser entendre que la simulation invoque ce skill.

Références : [source/fondamentaux.yaml:211](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/fondamentaux.yaml:211>), [source/statut-evaluation.yaml:7](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/statut-evaluation.yaml:7>), [app/src/ModelPage.tsx:40](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/ModelPage.tsx:40>), [source/methode-evaluation-core.yaml:14](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-evaluation-core.yaml:14>).

### 2. Relier le périmètre du programme aux capacités effectivement chiffrées

Les Fondamentaux annoncent des capacités retenues dans « Business Operations », puis qualifient d’indicatif le positionnement de Flow dans la chaîne logistique. Le glossaire rattache le périmètre métier FLOW au domaine de la chaîne logistique. Le guide explique que la micro-cartographie illustrative ne remplace pas la cartographie financée ; cette articulation manque au lecteur public.

**Il n’y a pas de contradiction économique démontrée.** La capture active et la grille portent bien sur les descendants de `supply-chain-orchestration`. L’ambiguïté concerne le passage du périmètre large du programme au périmètre de la charge de construction.

**Correction recommandée :** « Le programme s’inscrit dans Business Operations. La construction Make chiffrée aujourd’hui porte sur les capacités retenues de la chaîne logistique ; le schéma situe cette cible dans un ensemble plus large. » Maintenir séparément les écarts de périmètre des offres Buy.

Références : [source/fondamentaux.yaml:189](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/fondamentaux.yaml:189>), [source/fondamentaux.yaml:202](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/fondamentaux.yaml:202>), [source/glossaire.yaml:15](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/glossaire.yaml:15>), [source/grille-complexite.yaml:22](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/grille-complexite.yaml:22>), [source/README.md:56](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/README.md:56>).

### 3. Empêcher une fonction documentée de devenir visuellement une inclusion commerciale acquise

La fiche SAP affiche « Statut de l’offre : Inclus » pour l’analyse des événements et des indicateurs. La phrase voisine précise pourtant : « Fonctionnalités documentées du S/4 Private Edition proposé, à confirmer sur l’édition et les droits précis ».

**Effet sur la lecture :** le statut synthétique affirme davantage que sa justification. C’est particulièrement sensible puisque le framework demande de distinguer disponibilité au catalogue, droits acquis et financement.

**Correction recommandée :** distinguer le produit proposé de l’inclusion de la fonction : « Produit proposé : S/4 Private Edition » et « Inclusion des fonctions analytiques : à confirmer ». Réexaminer les autres statuts avec la même règle. Une correction de qualification documentaire ne crée aucun budget supplémentaire.

Références : [source/references-couts-integration.yaml:1091](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/references-couts-integration.yaml:1091>), [source/glossaire.yaml:272](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/glossaire.yaml:272>).

### 4. Donner au lecteur accès aux appuis annoncés et préciser les prix inconnus

La page Marché explique trois volets — construction, intégration, fonctionnement — mais son accès final aux références conduit essentiellement aux six fiches produit. Les références de projets et les prix normalisés existent dans le registre, sans accès direct structuré depuis cette page.

Dans les fiches Microsoft et SAP, « Prix observé : Non renseigné » et « Prix retraité au périmètre FLOW : Non renseigné » peuvent faire croire que les prix Synvance manquent. Les champs visent en réalité un prix isolé ou transposé pour le périmètre de la fiche ; les offres économiques ont d’autres propriétaires.

**Corrections recommandées :**

- Donner trois accès visibles aux données existantes : **fonctions et composants**, **projets et prix d’intégration**, **services et coûts de fonctionnement**.
- Pour les fiches Buy, préciser : « Aucun prix isolé pour le périmètre fonctionnel de cette fiche. Les prix et inclusions des offres Synvance sont présentés dans le dossier des offres. » Ajouter le lien correspondant.
- Conserver séparément « Estimation transposée à FLOW : non établie ». Ne pas remplir un champ inconnu en recopiant un budget de périmètre différent.
- Remplacer les liens génériques « Preuve 1 / Preuve 2 » par leur nature réelle : documentation produit, code figé, proposition fournisseur, cas client publié. Ne pas inventer les métadonnées absentes.

Références : [app/src/MarketMethodPage.tsx:11](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/MarketMethodPage.tsx:11>), [source/references-couts-integration.yaml:1346](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/references-couts-integration.yaml:1346>), [config/application.yaml:1631](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/config/application.yaml:1631>), [source/references-couts-integration.yaml:969](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/references-couts-integration.yaml:969>), [source/references-couts-integration.yaml:1049](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/references-couts-integration.yaml:1049>), [app/src/EssentialViews.tsx:155](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/EssentialViews.tsx:155>).

## Priorité 2 — Faire correspondre les mots aux périmètres calculés

### 5. Corriger les profils du tableau des tarifs

| Libellé visible | Problème | Formulation recommandée |
|---|---|---|
| Développeur et extensions | Mélange une personne et un type de réalisation. | **Ingénieur de développement** |
| Intégrateur de flux | Réduit le rôle aux interfaces, alors qu’il couvre aussi paramétrage, règles et données. | **Expert intégration et configuration** |
| QA indépendante | Désigne une activité dans une colonne « Profil ». | **Spécialiste de la qualification indépendante**, avec « QA » explicité si conservé |
| Architecte transverse | « Transverse » ne dit pas à lui seul ce qui est couvert. | **Architecte technique**, avec une courte définition de son périmètre transverse |

Les deux premiers noms sont déjà ceux des rôles canoniques. Le développeur couvre conception applicative, code, plugins et tests locaux, avec les extensions client en Buy. L’expert intégration couvre paramétrage, règles, données, flux et industrialisation applicative.

Les deux dernières propositions sont des améliorations éditoriales à confirmer contre le périmètre des tarifs ; elles ne justifient aucune modification de rôle ou de montant. La règle actuelle de tarif commun à qualification équivalente doit rester explicite.

Ajouter avant la grille son régime d’achat : **références France, freelance en direct** ; tarif applicatif pour un intervenant autonome expérimenté, avec tarifs propres pour qualification et architecture. Les lecteurs ne doivent pas déduire ces conditions d’une réserve « hors marge ESN » située plus bas.

Références : [config/application.yaml:1300](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/config/application.yaml:1300>), [source/integration.yaml:19](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/integration.yaml:19>), [source/maintenance.yaml:19](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/maintenance.yaml:19>), [app/src/FrameworkPage.tsx:57](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/FrameworkPage.tsx:57>), [source/stacks/java-spring.yaml:255](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/stacks/java-spring.yaml:255>).

### 6. Nommer exactement l’assiette dans les formules

Trois corrections sont nécessaires sans toucher aux calculs :

| Formulation actuelle | Lecture possible | Formulation précise |
|---|---|---|
| JH du rôle = mobilisation mensuelle × durée du programme | Construction du Core et intégration cumulées. | **JH du rôle = JH mobilisés par mois × durée de l’intégration Groupe en mois.** |
| Build Make — Budget du build | Ensemble des activités classées Build, dont l’intégration. | **Construction initiale du Core System Make** ; budget de construction = prestations techniques de construction + provision de coordination technique. |
| Outillage « ajouté aux JH techniques » | Addition de coûts à des journées. | **Ajouté au tarif de chaque JH technique concerné.** |

Le moteur utilise `integration_mois` pour le pilotage du programme décrit ici. La ligne « Budget du build » correspond à la construction du Core. Le sens large de Build reste inchangé.

Références : [source/methode-calcul-net.yaml:114](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-calcul-net.yaml:114>), [tools/composable_costs.py:80](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/composable_costs.py:80>), [tools/composable_costs.py:129](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/composable_costs.py:129>), [source/methode-calcul-net.yaml:149](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-calcul-net.yaml:149>), [tools/calculate_costs.py:174](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/calculate_costs.py:174>), [config/application.yaml:1347](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/config/application.yaml:1347>), [config/application.yaml:1381](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/config/application.yaml:1381>).

### 7. Annoncer que la méthode annuelle couvre aussi des activités classées Build

La page « Méthode de calcul du Run » annonce l’exploitation, les moyens techniques et la part Run du MCO de l’intégration. Les calculs annuels expliqués couvrent aussi le maintien du produit générique, classé Build. La dernière étape effectue précisément cette distinction.

**Effet sur la lecture :** le lecteur cherchant comment est calculé le MCO Core ne sait pas immédiatement où trouver sa méthode. Il peut aussi interpréter les bases annuelles comme des totaux Run.

**Correction recommandée :** titrer **« Calculer le fonctionnement et sa part Run »**. Annoncer dès l’ouverture que les règles de services récurrents couvrent le MCO Core, les adaptations Beaumanoir, l’exploitation et les moyens techniques, puis que la convention Build/Run classe ces dépenses. Conserver les dates de consommation pendant la réalisation et la limite actuelle sur l’agrégation monétaire.

Références : [source/methode-calcul-run.yaml:9](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-calcul-run.yaml:9>), [source/methode-calcul-run.yaml:96](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-calcul-run.yaml:96>), [source/methode-calcul-run.yaml:164](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-calcul-run.yaml:164>).

### 8. Rendre toutes les formules explicables et leurs variables retrouvables

La formule d’expertise cloud et sécurité contient « plafond hérité × facteur de sensibilité JH ». Ni la valeur du plafond ni la définition du facteur ne figurent sur Paramètres, alors qu’elles existent dans les sources. La formule est affichée, mais le lecteur ne peut pas la reconstruire depuis le parcours proposé.

**Correction recommandée :** employer « plafond annuel d’expertise retenu », expliquer le coefficient des scénarios bas, central et haut, afficher les valeurs dérivées de leur propriétaire et proposer un lien depuis la formule. L’origine historique du plafond reste dans sa justification.

La méthode Core annonce une consolidation et des bornes sans formule visible. Ajouter les deux relations réellement décrites :

- **Charge centrale du périmètre = somme des charges centrales des lots retenus, comptés une seule fois.**
- **Borne basse ou haute du périmètre = somme des bornes correspondantes des mêmes lots.**

Préserver la règle de total partiel lorsque des charges manquent. Ne pas introduire de taux universel d’incertitude : le contrat conserve directement les bornes et leurs justifications. Leur somme reste une enveloppe de sensibilité, sans interprétation statistique ajoutée.

Références : [source/methode-calcul-run.yaml:82](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-calcul-run.yaml:82>), [source/calibration-couts.yaml:137](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/calibration-couts.yaml:137>), [source/calibration-couts.yaml:164](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/calibration-couts.yaml:164>), [tools/study_app.py:276](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/study_app.py:276>), [source/methode-evaluation-core.yaml:142](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-evaluation-core.yaml:142>), [source/schema-evaluation-core.yaml:154](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/schema-evaluation-core.yaml:154>).

## Priorité 2 — Simplifier le parcours sans cacher les informations

### 9. Présenter les preuves avant les méthodes qu’elles alimentent

L’ordre actuel présente Core, budget et Run avant l’évaluation de marché. La page Marché décrit pourtant les critères de recevabilité des références et les éléments à transmettre à ces trois calculs. Cet ordre reste praticable, mais fait découvrir tardivement les critères qui fondent les estimations.

**Parcours recommandé :**

| Ordre | Page | Question à laquelle elle répond |
|---|---|---|
| 1 | Vue d’ensemble | Pourquoi cette démarche permet-elle de préparer une décision d’investissement ? |
| 2 | Fondamentaux du modèle | Quels objets, périmètres et conventions compare-t-on ? |
| 3 | Évaluation de marché | Quelles références utilise-t-on et que démontrent-elles ? |
| 4 | Estimation du développement Make | Comment passer du besoin métier aux travaux et aux JH ? |
| 5 | Des charges au budget | Comment traiter les gains, les autres efforts et la valorisation ? |
| 6 | Calculer le fonctionnement et sa part Run | Comment dimensionner les services récurrents et leurs périodes ? |
| 7 | Paramètres du modèle | Quelles valeurs sont retenues, pourquoi et lesquelles peut-on faire varier ? |

Le titre actuel de la méthode Core couvre linguistiquement Make et Buy, puisque Core System est une notion commune. La restriction à Make doit apparaître dans le titre ou le sous-titre, sans attendre le résultat de la première étape.

Les transitions doivent expliquer le résultat transmis à la page suivante. Le dossier détaillé des six produits reste consultable par liens ; sa lecture intégrale ne devient pas un préalable à la suite du framework. Aucun carrousel ni accordéon n’est nécessaire.

Références : [config/application.yaml:1144](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/config/application.yaml:1144>), [source/methode-evaluation-marche.yaml:204](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-evaluation-marche.yaml:204>), [source/methode-evaluation-core.yaml:40](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-evaluation-core.yaml:40>).

### 10. Organiser Paramètres autour des décisions du lecteur

La page compte environ **3 562 mots**, contre 882 pour la Vision et 1 406 pour la méthode budget. À 1 440 px de largeur, son contenu occupe environ 11 108 px de hauteur. La longueur est surtout due aux justifications détaillées, aux limites répétées et à la coexistence de paramètres actifs et de diagnostics historiques.

La phrase « Tous les paramètres présentés ici ne sont pas exposés à la simulation personnelle » est déjà explicite. Le problème restant est de retrouver, pour chaque valeur, son rôle dans le calcul et la possibilité de la modifier.

**Réorganisation recommandée, toujours en lecture continue :**

- Commencer chaque famille par les valeurs, leur effet et leur périmètre d’application.
- Identifier les états utiles : valeur active, repère diagnostique sans effet budgétaire, valeur remplacée. Pour la modification personnelle, dériver l’information du contrat réel de Simuler.
- Conserver une règle commune lorsque plusieurs options partagent la même justification ; rendre immédiatement visibles les différences qui expliquent un écart.
- Donner accès aux pièces tarifaires existantes. Les noms Silkhom, ForTeam et TJMètre ne sont actuellement que du texte dans cette partie, malgré les références disponibles.
- Regrouper les diagnostics historiques en fin de lecture ou dans une annexe accessible par lien. Préserver leur traçabilité ; ne pas les présenter comme des leviers actifs.

La Vision doit conserver le raisonnement et la décision ; les Fondamentaux, les définitions et frontières ; les méthodes, les transformations et formules ; Paramètres, les valeurs, leur origine et leurs effets. Un rappel bref près d’un calcul est utile. Une nouvelle explication complète de la même convention alourdit la lecture.

Références : [config/application.yaml:1241](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/config/application.yaml:1241>), [config/application.yaml:1281](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/config/application.yaml:1281>), [app/src/FrameworkPage.tsx:123](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/FrameworkPage.tsx:123>), `tmp/audit-framework-global/parametres.txt`.

## Priorité 3 — Achever l’harmonisation des termes et des pièces

### Lexique de correction

| Expression rencontrée | Formulation ou traitement recommandé |
|---|---|
| Taux de construction par activité et option | **Gains de productivité retenus pour les travaux de construction**, puis périmètre Make/compléments Buy précisé. |
| Taux annuels par activité | **Gains de productivité des activités annuelles**. « Annuel » décrit les activités, pas une amélioration cumulée chaque année. |
| Interface commune Make | **Interface utilisateur commune aux options Make**, pour éviter la confusion avec les interfaces entre systèmes. |
| Maintenir le Core générique : correctifs, releases et patchs | **Maintenir la Plateforme Core System : correctifs et versions**. |
| Provision annuelle hors socle de l’offre | **Provision pour ressources non comprises dans l’offre**, afin de distinguer produit générique, services inclus et poste Socle technique et cloud. |
| Réservation et Availability ATP/CTP/PTP | **Réserver et promettre une quantité et une date** ; expliquer les sigles à proximité. |
| Case Management et automatisation | **Gestion des dossiers et automatisation**. |
| Business Capabilities retenues | **Capacités métier retenues** ; conserver les identifiants natifs. |
| Wholesale et B2B | **Commerce de gros et interentreprises**, avec les termes anglais seulement si utiles pour les produits. |
| PNCLOC | **Lignes physiques de code hors commentaires et lignes vides**, puis le sigle. |
| Aucun débit/p95 comparable | **Aucune mesure comparable de débit et de temps de réponse au 95e percentile**, avec l’intérêt de la mesure expliqué. |
| Situation vérifiée, incluant « Réutilisation non démontrée » | **État de la réutilisation**. |
| Qualification | Distinguer **qualification logicielle** et **analyse des références ou correspondances fonctionnelles**, selon le contexte. |
| Preuve 1 / Preuve 2 | Nommer la nature et l’origine disponibles de la pièce. |

Références principales : [config/application.yaml:1259](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/config/application.yaml:1259>), [config/application.yaml:1266](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/config/application.yaml:1266>), [config/application.yaml:1280](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/config/application.yaml:1280>), [config/application.yaml:1405](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/config/application.yaml:1405>), [config/application.yaml:1662](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/config/application.yaml:1662>), [source/maintenance.yaml:91](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/maintenance.yaml:91>), [source/references-couts-integration.yaml:234](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/references-couts-integration.yaml:234>), [source/references-couts-integration.yaml:244](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/references-couts-integration.yaml:244>), [source/references-couts-integration.yaml:397](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/references-couts-integration.yaml:397>), [source/methode-evaluation-core.yaml:80](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-evaluation-core.yaml:80>).

Il ne faut pas supprimer les distinctions techniques utiles. **Prix d’origine, prix normalisé et estimation transposée** sont correctement définis et doivent rester séparés. Le vocabulaire doit gagner en clarté sans transformer une fonction documentée en fonction testée, un tarif de référence en offre ferme ou une hypothèse en mesure observée.

### Deux statuts documentaires à préciser

**« Calibration partielle ».** L’expression peut suggérer qu’une partie des charges FLOW a été validée par des références indépendantes comparables. Le registre annonce pourtant zéro référence éligible dans sa comparaison indépendante, et aucune transposition d’intégration retenue. Préférer une description exacte des acquis : fonctions, travaux et prix documentés, dont la transposition aux charges et coûts FLOW reste à consolider. Si une calibration particulière est effectivement établie, nommer son objet et sa preuve.

Références : [source/methode-evaluation-marche.yaml:14](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-evaluation-marche.yaml:14>), [source/references-couts-integration.yaml:1164](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/references-couts-integration.yaml:1164>).

**Diagnostic Tryton.** La pièce liée contient un calcul nominal conditionnel de reconstruction, alors que le registre actif conserve `calcul_ref` et `effort_jh` à `null`. Ce décalage ne démontre aucune erreur de budget. Il faut documenter le statut du calcul de la pièce et, s’il n’est pas retenu dans le registre, son motif. Ne pas inventer une décision de rejet à partir du seul `null` et ne pas injecter automatiquement le diagnostic dans les chiffres.

Références : [sources/fiche-marche-tryton-flow-2026-10-28.md:75](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/sources/fiche-marche-tryton-flow-2026-10-28.md:75>), [source/references-couts-integration.yaml:784](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/references-couts-integration.yaml:784>).

Le vocabulaire actif des méthodes emploie déjà « Réutilisation du patrimoine logiciel ». Les occurrences de « réemploi » dans des pièces datées doivent être traitées selon leur statut documentaire ; elles ne justifient pas la réécriture de preuves ou de citations originales.

## Ordre de mise en œuvre recommandé

1. **Sécuriser les périmètres et les affirmations :** méthode cible/base actuelle, programme/capacités chiffrées, statut SAP « Inclus », portée des champs de prix Buy.
2. **Corriger les libellés et formules :** rôles canoniques, durée d’intégration, construction du Core, coût d’outillage, périmètre annuel/Run et variables actuellement absentes de Paramètres.
3. **Rendre les preuves accessibles :** projets, prix, services, sources tarifaires et noms de liens explicites. Documenter le statut des diagnostics conditionnels.
4. **Réordonner le parcours et ses transitions**, avec une responsabilité claire pour chaque page.
5. **Alléger les répétitions et harmoniser le lexique**, sans accordéons, sans suppression de preuves et sans changement économique.
6. **Relire la chaîne complète sur le rendu final**, puis vérifier la parité des chiffres et des simulations sur le candidat de présentation.

## Contrôles effectués pour cet audit

- Lecture dans Chrome local des sept routes et des six fiches, avec collecte des textes, titres, liens, tableaux et formules.
- Environ **12 776 mots** pour les sept pages et **10 907 mots** pour les six fiches, éléments de navigation et légendes compris. Ces volumes localisent la densité ; ils ne constituent pas une limite éditoriale automatique.
- Aucun accordéon dans les sept pages examinées et aucune erreur JavaScript relevée pendant la capture.
- Contrôle `check_model --content` réussi. Ce contrôle valide des contrats et références ; il ne suffit pas à détecter les ambiguïtés de sens relevées ici.
- Captures et extraits : `tmp/audit-framework-global/`, avec inventaire complet dans `rendered.json`.

**Les recommandations sont préparées pour une révision à chiffres constants. L’audit seul est enregistré ; l’application et ses simulations restent inchangées.**
