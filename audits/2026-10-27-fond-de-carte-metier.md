# Audit du fond de carte métier — contre-revue du 27 octobre 2026

La contre-revue remplace les conclusions du premier audit du même jour. Elle porte sur les sources, les contrats de données, les validateurs, le moteur et les vues React. Les contrôles ont été exécutés sur le dépôt local ; les sondes de défaut utilisent des copies en mémoire. Aucun périmètre, montant, taux ou résultat économique n’a été modifié.

## Conclusion révisée

**Le premier audit sous-estimait le refactoring du modèle.** Il avait identifié une rupture de lecture réelle, mais déduisait trop vite de la présence d’identifiants communs que les données étaient prêtes pour une simple projection unifiée.

La cartographie fournit déjà un fond métier utilisable : la capture des 88 capacités, neuf sous-domaines et 28 Business Areas correspond encore au fichier Beaumanoir courant, vérifié par empreinte. Les captures métier et scénarios proviennent de la même révision. Il n’y a donc pas de dérive de version détectée sur ce point.

En revanche, **les relations techniques ne constituent pas une chaîne complète de justification**. La couverture Buy mélange hypothèse économique, appréciation produit et travaux client ; des descriptions du besoin sont copiées dans plusieurs sources ; des explications anciennes restent actives ; les unités de financement sont différentes des objets de la carte. Il faut clarifier ces relations avant de les afficher comme une lecture commune.

Le bon objectif est un **modèle de traçabilité ancré dans la cartographie des domaines**, avec plusieurs lectures cohérentes et des financements identifiés. Les formules économiques peuvent rester les mêmes. La structure des faits, leurs sources, leurs jointures et certaines dépendances doivent être revues.

## Ce que le premier audit doit corriger

| Conclusion initiale | Résultat de la contre-revue |
| --- | --- |
| « Le problème est surtout dans la restitution. » | Trop restrictif. L’interface révèle aussi un problème de sens des données, de responsabilités des sources et de continuité des preuves. |
| « Les dix thèmes sont une autre taxonomie. » | Formulation excessive : ces thèmes se chevauchent et ne forment pas une partition métier. Plusieurs synthèses sont légitimes. Le défaut est l’absence de rattachements explicites à la carte, combinée au mélange de grains. |
| « Les 178 revues Buy sont disponibles et contrôlées. » | Exact pour les identités ; insuffisant pour la couverture. Elles utilisent trois textes de décision génériques et treize profils d’apport produit. Elles ne prouvent pas 178 adéquations fonctionnelles. |
| « Une projection par capacité suffit. » | Une projection aidera, après clarification des faits qu’elle assemble. Sinon elle donnera une apparence de précision à des hypothèses globales. |
| « Trois Make et deux Buy constituent cinq couvertures comparables. » | Ils visent un besoin commun, mais le Make décrit une réalisation future et des apports techniques ; le Buy décrit un produit existant, une offre et son adéquation à qualifier. Ces niveaux doivent être nommés. |
| « Préserver le contrat de simulation suffit. » | Faux pour les sauvegardes nommées et fichiers exportés : ils dépendent encore de l’empreinte complète du modèle. La session automatique utilise déjà un contrat sémantique distinct. |
| « Conserver les nombres 88 / 178 garantit le fond de carte. » | Ces comptes sont des témoins de cette référence, pas le contrat métier durable. Le contrôle doit porter sur les identités et le périmètre de la capture sélectionnée, avec gestion explicite des évolutions. |

## Constats prioritaires et preuves

### 1. La qualification Buy n’est pas encore une Gap Analysis démontrée

Le comptage exécuté donne **81 lignes `standard_retenu`, 75 `integration_client` et 22 `point_cible`**, pour 178 couples bloc/option. Chaque catégorie utilise exactement le même texte de décision pour toutes ses lignes. Les 22 lignes ciblées renvoient à sept sujets ouverts ; le portefeuille de développements additionnels est vide.

La ligne `integration_client` explique notamment le traitement économique d’un lot antérieur. Elle ne répond pas, par elle-même, à « quelles fonctions du besoin cette édition du produit réalise-t-elle ? ». De même, `standard_retenu` est un parti pris du scénario central ; ce libellé ne vaut pas démonstration de toute la capacité.

Les apports et limites produit ne sont pas absents : ils sont mutualisés dans treize profils de `source/recalibration-metier.yaml#couvertures`. Cette mutualisation est utile, mais elle ne doit pas être présentée comme une revue spécifique et complète de chaque capacité.

**Conséquence :** rendre séparément lisibles, lorsqu’ils influencent la décision, le besoin visé, l’apport documenté du produit, son inclusion dans l’offre et les travaux retenus dans le budget. Une inconnue sur l’un de ces sujets ne permet de conclure ni à une absence de fonction ni à un coût nul. Éviter une note ou couleur unique qui fusionnerait ces dimensions. Il n’est pas nécessaire de créer une matrice exhaustive de cinq options par 258 fonctions : approfondir les écarts matériels au grain utile.

**Preuves :** `source/qualification-buy.yaml#revues`, `source/schema-qualification-buy.yaml`, `source/recalibration-metier.yaml#couvertures` ; comptes dans le JSON de preuves.

### 2. Une faille de contrôle des preuves Buy est reproductible

Dans une copie en mémoire, remplacer la source du profil Buy `ms_reference` par `AUDIT_MISSING_SOURCE` est **accepté par `business_calibration.validate()`**. Le même contrôle rejette bien un composant inexistant, une capacité inexistante et une revue Buy dupliquée.

La cause est localisée : la validation des sources dans `business_calibration.py` parcourt les affectations Make ; `buy_qualification.py` vérifie les composants Buy et les exceptions, sans vérifier les identifiants de sources des profils de couverture Buy.

Les **31 identifiants de sources utilisés par les profils Buy existent actuellement** dans le registre fusionné de sources techniques. Il n’y a donc pas 31 preuves perdues. En revanche, ils sont tous absents de `qualification-buy.yaml#sources`, et `Study._buy_review()` ne joint pas ce registre technique aux profils qu’il transmet. La vue actuelle ne révèle pas ce problème, car elle affiche les sept exceptions et leurs propres sources. Une nouvelle vue par capacité devra résoudre explicitement ces références.

**Conséquence :** renforcer la validation et la projection des preuves avant d’exposer les 178 lignes. Un contrôle de complétude des identités ne suffit pas pour déclarer les preuves contrôlées.

### 3. Le besoin métier et certaines explications ont plusieurs propriétaires

Les contrôles ont trouvé **88 copies exactes des fonctions sous forme de texte `scenario` et 88 copies des frontières** entre la grille et la calibration. Ces copies sont cohérentes aujourd’hui. Leur égalité n’est pas contrôlée par le validateur de calibration. Les identifiants des 258 fonctions ne sont référencés explicitement ni par les affectations de travaux ni par les revues Buy : la jointure s’arrête au bloc/capacité.

Le grain par capacité est adapté à une étude d’opportunité ; il ne justifie pas de décomposer automatiquement tous les JH par fonction. En revanche, une variation du besoin doit pouvoir être rapprochée des travaux et appréciations concernés sans modifier silencieusement une copie indépendante.

Une contradiction éditoriale est déjà présente : `source/ecarts-perimetre-flow-rfi.md`, annoncé actualisé au 26 octobre, décrit encore deux anciennes provisions CSF de CTP et de Case Management comme restant à qualifier. Son paragraphe économique renvoie pourtant à la qualification courante, dont le portefeuille de développements additionnels est vide. Le détail « Dossiers / exceptions » dans `explications-modele.yaml` évoque lui aussi des provisions à revoir. Le modèle courant n’ajoute aucun supplément pour les sept points ciblés ouverts. Cette contradiction est visible au fil des sources et explications ; elle n’établit pas une erreur de total du moteur.

**Conséquence :** choisir un propriétaire pour chaque fait. Dériver les rappels du besoin depuis la grille ou porter une différence explicite et justifiée ; dater et isoler les explications historiques ; conserver les pièces d’origine. L’unification des écrans doit suivre cette réconciliation.

### 4. Un exemple montre pourquoi les jointures ne peuvent pas être seulement techniques

La ligne « Réassort magasin » de la matrice décrit les besoins de réapprovisionnement et de redistribution. L’exception Buy `reassort-sap` pointe vers :

- BC-034 — Planning Scenario Reconciliation ;
- BC-037 — Supply Assignment ;
- BC-040 — Physical Stock Target Optimization.

Elle ne pointe pas vers **BC-043 — Replenishment** et **BC-044 — Stock Redistribution**, tous deux marqués `standard_retenu` pour SAP, sans exception liée.

Ce constat est une **ambiguïté de correspondance à instruire**, pas une preuve d’absence de fonction SAP. Le réassort magasin peut mobiliser plusieurs mécanismes et produits ; son rapprochement avec ces capacités doit préciser ce qui est concerné par le standard, le moteur externe et les modules non établis dans le panier. La validation actuelle vérifie que les revues reproduisent les liens de l’exception ; elle ne vérifie pas la pertinence métier de ces liens.

**Conséquence :** réaliser la correspondance des thèmes avec les responsabilités de la carte sur quelques cas matériels avant de généraliser la nouvelle vue. Une grille complète aux bonnes dimensions peut rester trompeuse.

### 5. Un fond métier commun ne signifie pas une unité de coût commune

Les trois Make utilisent **267 affectations chiffrées**, soit 88 capacités plus un transverse, pour chacune des trois stacks. Elles réutilisent **36 modèles de charge**. Par exemple, le modèle `decision` est utilisé 42 fois. Un identifiant de modèle de charge n’est donc pas l’identifiant d’une prestation financée une fois.

Deux erreurs de refactoring seraient possibles : dédupliquer les montants par modèle de charge et sous-compter les travaux ; ou répéter le coût d’un mécanisme partagé à chaque capacité bénéficiaire. La propriété et la consommation de mécanismes communs sont déjà décrites dans `reemploi`, mais doivent rester distinctes de la réutilisation d’un modèle d’estimation.

Le build comprend en outre le **transverse et le pilotage**, en plus des coûts rattachés aux 88 capacités. Les budgets d’intégration et les achats Buy restent des enveloppes ; les 43 situations ne sont pas des unités de facturation. Ces situations mobilisent 82 des 88 capacités. L’absence de scénario pour les six autres ne signifie ni exclusion du périmètre ni absence de besoin.

**Conséquence :** conserver une identité de financement par affectation et ses relations vers les capacités. Une capacité peut montrer un coût porté, un bénéfice d’un travail financé ailleurs ou un forfait non ventilé. Il faut indiquer la nature du lien ; aucun prorata automatique n’est justifié. Le Run & MCO conserve ses activités et ses assiettes.

### 6. La dette historique reste dans les dépendances exécutées

`calculate_costs.validate_inputs()` lit encore les 39 CSF et valide les sections historiques des fichiers de chiffrage avant que `business_calibration.apply()` remplace en mémoire leurs travaux fonctionnels. `validate_complexity_grid.py` utilise également le registre CSF pour vérifier les correspondances historiques. L’adaptateur lit encore la méthode et les frontières de `core-system-features.yaml`.

Cela ne démontre pas que les anciens JH calculent les montants actuels : l’adaptation active est bien appliquée. Cela montre que **ces fichiers ne sont pas tous de simples archives débranchées**. Les retirer au nom d’un modèle unique pourrait empêcher le calcul ou supprimer un contenu encore consommé.

Les schémas imposent aussi exactement 88 blocs et 178 revues, et la calibration impose l’ordre des couples bloc/capacité de la grille. Ces contraintes sécurisent la référence actuelle, mais l’évolution future d’une carte appelle une sélection versionnée et des contrôles d’identité explicites.

**Conséquence :** inventorier les consommateurs et garder un adaptateur de transition. La suppression des dépendances historiques vient après la démonstration de leur remplacement. Les formules du moteur peuvent être conservées.

### 7. La compatibilité des sauvegardes constitue un risque concret de migration

`reloadSession.ts` restaure la session automatique avec `simulation_contract`. En revanche, `Simulations.tsx` sauvegarde et exporte `model_version`, puis refuse le chargement d’un scénario nommé dont cette empreinte a changé. `Study.simulate()` refuse également une version différente.

La sonde ajoute seulement un commentaire à une copie en mémoire du YAML de configuration : **l’empreinte globale change, le contrat sémantique reste identique**. Les scénarios nommés sont donc exposés à un refus après une évolution purement éditoriale, même lorsque la reprise automatique de session reste possible.

**Conséquence :** intégrer la migration des scénarios nommés et des exports au chantier, avec revalidation des paramètres contre le contrat courant. La seule vérification de la session au rechargement ne couvre pas ce risque. La sonde démontre le comportement de version et de rejet côté serveur ; le refus côté interface est constaté dans le code, sans manipulation d’un scénario utilisateur.

## Modèle cible proposé

Le centre du modèle est **l’objet métier identifié dans une version de la cartographie**, avec la sélection de périmètre de l’étude. Le domaine et les regroupements métier restent reconnaissables dans chaque lecture. Une entrée synthétique par domaine ou Business Area doit rester possible : imposer d’emblée une table de 88 lignes ne garantit pas une lecture sponsor claire.

| Objet | Rôle et source de référence | Relation avec la carte |
| --- | --- | --- |
| Objet métier | Identité, nom, définition, hiérarchie et version issus de Beaumanoir. | Référence canonique ; aucune copie éditable de la hiérarchie dans chaque vue. |
| Besoin retenu et complexité | Fonctions proposées, variantes, frontières et niveaux de la grille. | Rattachés à la capacité ; statut de proposition conservé. |
| Appréciation d’une option | Apport produit ou technique, adéquation au besoin, inclusion commerciale et points ouverts, au grain nécessaire. | Capacité, fonction ou parcours visé, avec source et portée explicites. Une appréciation mutualisée reste identifiable comme telle. |
| Travail ou achat financé | Affectation économique, hypothèse de charge ou prix, responsabilité et assiette. | Relation vers les capacités concernées ; propriétaire du coût distinct des bénéficiaires. Aucun financement dupliqué dans les vues. |
| Situation d’intégration | Parcours et contributions issus du catalogue, rapprochements proposés vers les activités. | Plusieurs capacités mobilisées ; conserve l’enveloppe et les travaux mutualisés. |

Ces objets peuvent rester dans plusieurs YAML spécialisés. L’unicité porte sur le propriétaire de chaque fait et les relations contrôlées ; créer un fichier géant ou une base de données nouvelle n’est pas nécessaire.

La distinction Make/Buy doit être visible dans la comparaison : **même cible métier**, trois réalisations Make à construire et deux produits/offres Buy à qualifier. Les composants techniques réutilisables d’une stack ne doivent pas être présentés comme des fonctions métier déjà livrées. Dans la lecture des coûts, les cinq options restent comparées selon les trois postes actuels.

Les sujets « hors SCM » doivent être reliés, lorsqu’ils existent, aux objets de la cartographie complète. La capture actuelle ne contient qu’un domaine : il faudra sélectionner les voisins nécessaires et leurs relations avant de prétendre couvrir leurs identités. Les sujets techniques conservent leur place dans l’architecture et les responsabilités économiques. Un nouveau registre autonome de frontières, proposé trop rapidement dans le premier audit, risquerait de recréer une carte concurrente.

## Correspondance initiale des dix thèmes — proposition à instruire

Ce tableau indique une voie de réconciliation ; il ne constitue pas une validation métier ni une nouvelle définition de couverture.

| Thème actuel | Ancrage ou traitement proposé | Point à vérifier |
| --- | --- | --- |
| Opérations SCM | Le domaine `supply-chain-orchestration` et ses sous-domaines. | Résumé du périmètre, pas une capacité supplémentaire à additionner. |
| Stocks magasin | Inventory Management : suivi, visibilité, registres, inventaire ; contexte magasin. | Séparer la connaissance et décision SCM des gestes réalisés par les applications magasin/WMS. |
| Disponibilité / réservation | Reservation, ATP, CTP, PTP et leurs relations. | Une promesse et une réservation sont des responsabilités distinctes ; conserver leurs preuves et limites. |
| OMS NewStore / SoCloz | Order Management, Fulfilment Orchestration et Process Management ; lien au remplacement applicatif visé. | La reprise d’une application est un ensemble de responsabilités, pas un nouveau domaine métier. |
| Réassort magasin | Capacités pertinentes du Master Plan, dont Replenishment et Stock Redistribution ; rattachement exact à examiner. | Résoudre l’ambiguïté de l’exception SAP décrite plus haut et le périmètre du moteur externe. |
| Optimisation transport | Transport Plan Decision, avec capacités contributrices nécessaires. | Distinguer décision de plan, suivi et exécution transport ; inclusion du module à qualifier séparément. |
| Dossiers / exceptions | Process Management et contributions aux parcours métier. | Réconcilier le texte de provision avec le portefeuille économique courant. |
| Finance / conception produit | Relations vers les domaines voisins de la carte complète ; faits SCM concernés, notamment Accounting Data Provision. | Ne pas assimiler émission de faits comptables et remplacement de la Finance ; vérifier les travaux réellement inclus dans les offres. |
| Caisse / clienteling | Responsabilités voisines et interfaces avec les capacités de commande, stock et service concernées. | Ne pas déduire un remplacement de la caisse de la reprise OMS ; résoudre les nœuds voisins depuis la carte complète. |
| Hébergement / iPaaS | Architecture et financements transverses reliés aux usages métier. | Aucun nœud de capacité SCM artificiel ; assiettes et achats inclus conservés. |

## Ordre de refactoring recommandé

1. **Fixer la propriété des faits et réconcilier les contradictions.** Garder la carte versionnée comme référence du besoin ; distinguer hypothèse, preuve produit, offre et financement. Traiter les textes de provisions anciennes et le cas du réassort. Corriger le contrôle des sources Buy. Ces travaux précèdent une présentation de couverture plus affirmative.
2. **Rendre les relations explicites.** Construire un index dérivé par objet métier, résoudre les preuves et conserver les identités des affectations économiques. Dériver les copies du besoin lorsque leur sens est identique ; documenter toute adaptation. Réutiliser les identifiants de blocs comme alias de migration, sans imposer qu’ils deviennent les identifiants de la carte.
3. **Sécuriser la transition.** Conserver les budgets et associations de financement ; prévoir la reprise des scénarios nommés/exportés, les anciens liens, les filtres et la capacité consultée. Débrancher progressivement les références historiques après identification de chaque consommateur.
4. **Unifier les lectures autour de repères stables.** Même hiérarchie et mêmes objets sélectionnés pour périmètre, écarts, complexité et renvoi au coût. Garder la comparaison financière dans Estimations ; utiliser des liens ciblés vers la même capacité. Vérifier ensuite la lecture sponsor, le clavier et la navigation dans le navigateur.

Le premier incrément devrait couvrir quelques sujets contrastés — réassort, dossiers/processus et un transverse — afin de vérifier ces règles sur des cas réels avant de généraliser aux 88 capacités. Les arbitrages de portée doivent rester explicites dans les sources ; une refonte de présentation ne les tranche pas.

## Contrôles de sortie de la future migration

- Identités métier, chemins et périmètre de référence conservés ; toute évolution de capture donne lieu à une comparaison explicite. Les comptes 88 / 258 / 178 sont des témoins de cette migration, pas une définition universelle de la cartographie.
- Preuves résolues, portée et statut de chaque appréciation explicites ; une source manquante doit être rejetée pour Make et Buy.
- Chaque affectation économique comptée une seule fois, avec le même propriétaire et les mêmes hypothèses ; modèles de charge, bénéficiaires et financements distingués.
- Même composition du build, y compris transverse et pilotage ; mêmes enveloppes d’intégration, achats groupés et règles de Run & MCO. Comparer les montants en euros au centime, les annuités et les horizons 3/5/7/10 ans, puis les sensibilités concernées.
- Inconnues `null`, zéro, sans objet et inclus dans un prix demeurent distincts. Les sept points Buy ouverts n’ajoutent aucune dépense automatiquement.
- Contrôler séparément session automatique, sauvegarde nommée et import/export ; préserver les paramètres qui gardent le même sens.
- Anciens liens `coverage`, `complexity`, `buy-coverage` et liens de la FAQ redirigés vers les bons objets ; pas de perte de contexte entre capacité et coût.

## Vérifications exécutées et limites

- `validate_complexity_grid.py --check-current` : succès ; capture conforme au fichier de cartographie courant.
- `test_business_calibration.py` : **11 tests réussis**, couvrant notamment les identités, plages, réemplois ciblés et traitements Buy inclus. Leur succès n’invalide pas les lacunes sémantiques constatées.
- `2026-10-27-fond-de-carte-metier-controles.py` : chargement effectif de `Study`, comptes, rapprochement des versions, sondes sur copies, composition du build et résultats de référence par horizon. La source Buy inexistante est acceptée ; les trois autres altérations d’identité/composant sont rejetées.
- `2026-10-27-fond-de-carte-metier-preuves.json` conserve les résultats et empreintes des entrées. Les budgets sont stockés en euros avec leur précision, uniquement comme témoin de migration.

Cette contre-revue ne réévalue pas les produits Microsoft/SAP à partir de leurs documentations actuelles, ni les JH d’ingénierie. Elle confronte les affirmations internes, les sources conservées, les contrôles et les effets de structure. La correspondance métier proposée reste à instruire ; aucune observation navigateur ni validation terrain n’est revendiquée.

La directive demandée par l’utilisateur est inscrite en tête de `AGENTS.md` : appuyer autant que possible les hypothèses sur la cartographie des domaines, en distinguant ce qu’elle établit des hypothèses et preuves économiques complémentaires.

