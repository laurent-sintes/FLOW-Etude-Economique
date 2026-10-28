# Audit de l’application FLOW — décision d’investissement

25 octobre 2026. Audit de la version `2d2d94c58e61c3ae75f2fbdb987579192dbaebb79b51443266238f28b048d2b9`.

## Avis au sponsor

**L’application permet de comprendre et de challenger les dépenses. Elle ne constitue pas encore un dossier suffisant pour autoriser l’investissement complet.** Elle prépare une décision de cadrage, dont le budget, le délai, les responsables et les critères de sortie restent à préciser.

Le sponsor connaît la cartographie et le périmètre en cours de validation. La priorité n’est donc pas de lui réexpliquer les capacités SCM, mais de montrer quelles différences entre les options changent la décision, quelle valeur elles produisent, quelles responsabilités elles imposent et quelles preuves manquent.

Les avantages non financiers existent par fragments, surtout comme bénéfices possibles du Make. Il manque une comparaison équilibrée avec Microsoft et SAP. Posséder le code ne prouve ni l’autonomie réelle, ni la rapidité des évolutions ; acheter un produit ne prouve ni la couverture contractuelle, ni une intégration rapide.

Cet audit ne modifie ni le modèle, ni les budgets, ni l’application. Ses recommandations ne sont pas des hypothèses économiques actives. Les chiffres ci-dessous sont un instantané de contrôle, conservé dans [les preuves](2026-10-25-application-sponsor-preuves.json).

## Périmètre et vérifications

Lecture des cinq espaces dans l’application locale, rapprochement avec les YAML, revue du moteur et de l’adaptateur, contrôle des parcours de sources et d’une capacité détaillée, simulation d’un allongement du build. Revue des conventions de couverture, de coût, de calendrier, de reprise de session et de restitution.

Contrôles exécutés : 43 tests Python et 7 tests Node réussis ; TypeScript, contrôle de contenu, `calculate_costs.py --check` et `project_investment.py --check` réussis. Ces contrôles vérifient l’implémentation et la cohérence des données, pas la validité économique des JH, des gains IA ou de l’ancre d’intégration Make. Ce travail n’est ni un audit contractuel, ni un test de pénétration, ni une certification des performances.

## Ce qui fonctionne déjà

- Les cinq options sont comparables simultanément, avec séparation Build Core System, Intégration et migration, MCO & run.
- La grille est rattachée à la hiérarchie SCM : 88 capacités, 258 fonctionnalités proposées et un socle transverse. Elle constitue une base de discussion ; les fonctionnalités et charges dérivées restent à valider.
- Les paramètres et horizons 3, 5, 7 et 10 ans permettent de tester des hypothèses. Les années de service complet et le reste à réaliser rendent visible l’effet du calendrier.
- Le modèle distingue prix documentés, provisions, inclusions et hypothèses. Les sources et explications sont accessibles ; les résultats ne sont pas recalculés indépendamment dans React.
- Les limites du repère d’intégration Make et des comparaisons publiques sont exposées. Les tests et empreintes rendent les évolutions contrôlables.

## Constats prioritaires avant un engagement complet

### 1. Relier l’investissement à des résultats métier vérifiables

La synthèse expose des raisons possibles de construire, sans plan de bénéfices comportant une situation initiale, une cible, un propriétaire et une date. Le sponsor doit pouvoir comprendre quel résultat supplémentaire justifie de posséder le Core : réduction du délai d’évolution, intégration d’une enseigne, qualité des promesses, réduction d’interventions manuelles, par exemple. Ce sont des pistes à qualifier, pas des bénéfices démontrés de FLOW.

**À obtenir :** quelques objectifs mesurables, leur lien avec les capacités décisives et la contribution attendue de chaque option. Une capacité critique pour l’activité n’est pas nécessairement différenciante au point de justifier un développement propre.

### 2. Comparer les responsabilités et compromis hors prix

Les bénéfices possibles du Make sont plus lisibles que les bénéfices et contraintes propres aux deux Buy. La maturité produit, l’organisation nécessaire, la dépendance, la réversibilité et le délai de valeur ne forment pas une grille de décision commune.

**À produire :** une matrice Make / Microsoft / SAP avec avantage recherché, contrepartie, preuve et responsable de validation. Pas de note globale inventée ni d’affirmation générale « Buy plus rapide » ou « Make plus autonome ».

### 3. Rendre explicite la part conditionnelle des comparaisons

Les deux Buy comportent chacun 41 lignes présumées incluses et 48 lignes de compléments dans la calibration, socle transverse compris. Les compléments et leur pilotage représentent environ **3,96 M€ sur 8,31 M€ pour Microsoft (47,6 %)** et **6,30 M€ sur 19,79 M€ pour SAP (31,9 %)**. Ce sont des provisions importantes pour le classement, pas des prix fournisseurs confirmés.

Exemple consulté : *Transport Plan Decision*. Le standard Microsoft est présumé financé dans l’offre ; une provision SAP couvre des travaux complémentaires. La documentation produit ne prouve pas à elle seule le périmètre vendu. Une absence de preuve ne démontre pas une absence de fonction.

Autre différence : le budget SAP conserve les travaux Finance présents dans l’offre, tandis qu’un retrait indicatif de 2,58 M€ participe au calcul du repère Make. Les lots ne permettent pas une ventilation contractuelle certaine. Il ne faut pas retrancher silencieusement ce montant de l’offre SAP.

**À produire :** un rapprochement entre prix de l’offre, périmètre retenu, ajustements documentables, provisions conditionnelles et inconnues. Garder séparés prix réellement proposé et comparaison indicative à périmètre rapproché. La projection Microsoft au-delà du pilote et la transférabilité des travaux SAP vers FLOW restent à confirmer.

### 4. Ne pas confondre dépense moindre et investissement meilleur

| Option | Dépenses sur dix ans | Années équivalentes de service complet |
| --- | ---: | ---: |
| Java / Spring | 23,36 M€ | 3,17 |
| .NET | 24,59 M€ | 3,17 |
| Rust | 29,75 M€ | 3,17 |
| Microsoft / K3 | 27,88 M€ | 6,83 |
| SAP | 47,77 M€ | 7,50 |

Le calendrier part d’une même date, pas d’une même mise en service. **Passer le build Java de 48 à 60 mois fait baisser les dépenses sur dix ans de 1,09 M€**, de 23,36 à 22,27 M€, car une année de MCO sort de la fenêtre. Le service complet passe de 3,17 à 2,17 ans. Le moteur applique correctement la convention ; cette baisse ne démontre aucune création de valeur.

**À ajouter :** dates de résultats métier, coût de coexistence et effet des retards lorsque les données existent ; lecture complémentaire à durée de service comparable. Ne pas diviser simplement les dépenses par les années de service pour fabriquer un coût unitaire : build, abonnements et intégration ont des temporalités différentes.

### 5. Passer du coût IT acheté au financement du programme

Les contributions internes, la transformation organisationnelle et le décommissionnement sont exclus ou non calibrés. Leur exclusion est explicite, mais le sponsor ne dispose pas du financement complet du programme. Les besoins de trésorerie IT ne suffisent pas à établir un ROI.

Le mode d’achat doit aussi être rapproché : build et services Make valorisés avec des références freelance, prix Buy issus de dispositifs fournisseurs ; l’intégration Make utilise un repère SAP. Une différence de tarif ou de responsabilité contractuelle ne doit pas être attribuée à la seule technologie.

**À obtenir :** besoins internes, capacité disponible, coexistence, coûts de transition, bénéfices et mode d’achat réellement envisagé. Les inconnues restent inconnues. Une VAN nécessite des flux et un taux validés par la finance ; aucun taux générique n’est proposé ici.

### 6. Formuler une décision réellement approuvable

La synthèse donne une direction de cadrage, mais ne précise pas encore l’enveloppe demandée pour ce cadrage, sa durée, ses responsables, ses livrables probants et ses critères d’arrêt.

**À produire :** une demande de décision courte : autorisation recherchée, moyens, échéance, incertitudes à lever, preuves attendues et décision suivante. Le sponsor doit pouvoir approuver une étape concrète sans que cela vaille engagement implicite sur la totalité du Make.

## Grille non financière proposée

Les lignes suivantes sont des questions d’évaluation FLOW, pas des classements déjà démontrés. Microsoft et SAP doivent avoir des réponses distinctes.

| Dimension | Make : avantage recherché et contrepartie | Buy : avantage recherché et contrepartie | Preuve attendue |
| --- | --- | --- | --- |
| Adéquation métier | Maîtrise des mécanismes spécifiques ; conception et qualification à assumer | Réemploi d’un produit ; adaptation des processus ou extensions | Scénarios métier décisifs démontrés |
| Évolution | Priorisation directe ; capacité produit durable nécessaire | Évolutions mutualisées ; cadence et limites de l’éditeur | Exemple d’évolution et cycle de mise en production |
| Délai de valeur | Progression possible si la trajectoire le permet ; Core à réaliser | Standard déjà disponible ; configuration, migration et adoption demeurent | Plan de livraison crédible et dépendances |
| Harmonisation Groupe | Modèle commun maîtrisé ; arbitrage entre enseignes à organiser | Standard partagé ; adéquation aux différences métier à vérifier | Règles communes, variantes et gouvernance |
| Organisation | Équipe produit, architecture, sécurité, qualité et exploitation à maintenir | Responsabilité client sur processus, données, intégration et fournisseurs | Rôles, capacité, recrutement et continuité |
| Dépendances | Code détenu, mais dépendance aux compétences, composants et prestataires | Dépendance à l’éditeur, ses extensions et intégrateurs | Droits, compétences transférables et alternatives |
| Résilience et sécurité | Mécanismes à construire et opérer | Services disponibles selon les offres et contrats | Objectifs de service et essais communs |
| Intégration et données | Interfaces maîtrisables ; sémantique et migration à réaliser | Connecteurs possibles ; adaptation au SI et données toujours nécessaire | Flux, responsabilités et tests de bout en bout |
| Adoption | Expérience adaptable ; recherche utilisateur et accompagnement à financer | Parcours existants ; changements de pratiques à assumer | Essais utilisateurs et plan de changement |
| Réversibilité | Code accessible ; transfert de connaissance et remplacement à préparer | Sortie soumise aux formats, contrats et couplages | Exercice d’export/transfert, délai et coût de sortie |

Comparer d’abord les stratégies Make et Buy ; approfondir ensuite Java / .NET / Rust si l’organisation et la valeur du Make sont justifiées. Une option hybride peut être examinée, sans présumer de son coût ni modifier le périmètre. Les options actuelles utilisent déjà un mélange de composants achetés et développés ; un hybride métier serait un choix supplémentaire à définir explicitement.

## Apport des références de méthode

Les références initiales figurent dans [la note historique](../archives/etude-avant-yaml-2026-10-24/16-methodes-et-presentation-comparaison-make-buy.md). Leur intérêt méthodologique demeure ; aucun ancien prix n’est réintroduit.

- **Thoughtworks, Build versus buy (2022).** Le guide invite à partir des besoins décisifs, évaluer avec plusieurs métiers et vérifier les exigences techniques, l’intégrabilité et les évolutions futures. Voir notamment les pages imprimées 13–19 et 29–31. Application proposée à FLOW : conserver la cartographie détaillée en référence, mais centrer l’arbitrage sur quelques scénarios et preuves communs. [Guide](https://www.thoughtworks.com/content/dam/thoughtworks/documents/e-book/tw_ebook_build_vs_buy_2022.pdf).
- **Cabinet Office, Should Cost Modelling**, déjà retenu : méthode de construction et de traçabilité des coûts. Le **Green Book**, relu en complément, élargit la décision aux objectifs, alternatives, bénéfices non monétisés, risques et sensibilités. Application FLOW : une synthèse de décision comportant valeur, faisabilité et conditions, au-delà du total financier. Ce cadre public britannique n’impose aucune règle de gestion ni aucun taux à Beaumanoir. [Should Cost](https://www.gov.uk/government/publications/should-cost-modelling-tools-and-templates), [Green Book](https://www.gov.uk/government/publications/the-green-book--2/the-green-book-2026).
- **FinOps Foundation, SaaS.** Examiner droits effectivement utilisés, engagements, renouvellements et consommation. Application FLOW : vérifier les unités de capacité et les conditions contractuelles derrière les enveloppes annuelles, sans inventer une ventilation des offres groupées. [Cadre SaaS](https://www.finops.org/framework/technology-categories/saas/).
- **River, Build vs Buy Decision Pack.** La présentation publique associe entretien par tâches, coûts de sortie des deux options et hypothèse qui ferait basculer la recommandation. Application FLOW : renforcer la réversibilité et les seuils de décision. Le pack téléchargé n’a pas été audité ; son exemple fictif n’est pas un benchmark. [Présentation](https://meetriver.com/templates/vendor-and-build-decision-pack).
- **Gregor Hohpe / AWS**, complément de recherche : la frontière entre acheter et construire peut être située au niveau des composants, et la responsabilité d’exploitation est une question distincte. Application FLOW : expliciter ce que Beaumanoir veut posséder, acheter et opérer. Perspective d’un fournisseur cloud, sans preuve qu’un hybride serait plus économique ici. [Essai](https://d1.awsstatic.com/executive-insights/en_US/ebook-why-build-or-buy-might-be-the-wrong-question.pdf).
- **Brandon Byars, Thoughtworks, publié sur MartinFowler.com**, complément : les outils commerciaux facilitent certaines tâches d’intégration mais ne remplacent pas la conception des interfaces métier. Application FLOW : maintenir une responsabilité d’intégration explicite dans les deux stratégies. Cela n’interdit pas d’acheter des prestations d’intégration. [You Can’t Buy Integration](https://martinfowler.com/articles/cant-buy-integration.html).

Smartsheet et TBM Council, présents dans la recherche initiale, restent surtout utiles à la présentation et au classement des dépenses. Leurs ressources n’ont pas été réauditées ici. Aucune de ces références ne démontre que Make, SAP ou Microsoft est le meilleur choix pour Beaumanoir.

## Revue des espaces et du logiciel

| Espace | Utilité actuelle | Évolution prioritaire |
| --- | --- | --- |
| Synthèse sponsor | Résultats, réserves et conditions Make | Décision demandée, comparaison non financière, valeur et responsabilités ; déplacer le détail avant/après recalibration vers les estimations |
| Périmètres et responsabilités | Couverture, écarts et lecture Core / Intégration / Run & MCO | Mettre en avant les écarts qui changent la décision ; distinguer documenté, présumé et conditionnel |
| Stacks | Composition et apports techniques | Relier les choix aux compétences, exigences de service et dépendances ; éviter que le langage précède le choix de stratégie |
| Estimations et sources | Charges, méthode et traçabilité | Rapprocher provisions et contrats ; scénarios complets plutôt que seule plage du build |
| Simulations | Paramètres et horizons interactifs | Montrer les effets sur délai et valeur ; conserver une version approuvée exportable du dossier |

Points techniques et d’usage secondaires :

1. **Traçabilité lisible.** La source « Calibration des coûts » ouvre un YAML conservant des ancres CSF historiques, alors que les travaux actifs viennent de la recalibration métier. Le README l’explique, mais le parcours peut créer une ambiguïté. Signaler localement les sections historiques et ouvrir la preuve ciblée. Les ancres documentaires ne conduisent pas toujours à la section demandée : le lecteur reçoit le fichier entier.
2. **Scénarios et preuve de décision.** L’export JSON est utile à la simulation mais ne constitue pas un dossier de comité figé et lisible. Prévoir hypothèses, version, résultats, sources et décision. Les scénarios nommés restent liés à l’empreinte globale ; la reprise automatique de session possède un contrôle sémantique plus fin. Distinguer archivage fidèle et migration explicitement revue.
3. **Volume initial.** L’instantané JSON du bootstrap représente 11 639 139 octets ; la grille de complexité répète beaucoup de définitions de hiérarchie. Dédupliquer et charger le détail à la demande. Cette mesure porte sur le fichier JSON observé, pas sur un temps réseau ni une mesure de compression.
4. **Usage partagé.** Le serveur local n’est pas un dispositif d’approbation multiutilisateur : authentification, rôles, historique de validation et déploiement partagé demanderaient une conception dédiée. Ce n’est pas un défaut bloquant de l’usage local actuel.

## Ordre de traitement recommandé

**Première priorité :** améliorer la lecture sponsor avec les preuves disponibles : comparaison non financière équilibrée, part conditionnelle des budgets, différences de calendrier et décision de cadrage explicite. Conserver les cinq espaces et la cartographie connue.

**Deuxième priorité :** obtenir les éléments qui ne peuvent pas être inventés dans le logiciel : objectifs métier, responsables, capacité des équipes, niveau de service, périmètre contractuel et coûts internes. Faire confirmer ou retirer les provisions Buy ; qualifier la transférabilité du repère SAP utilisé pour Make.

**Troisième priorité :** construire des scénarios cohérents et leurs seuils de bascule, puis figer un dossier de décision. Les plages du build sont déjà très larges — Java environ 5,98 à 19,98 M€ autour de 9,93 M€ — et ne sont pas des probabilités. Tester notamment achats ESN, gains IA, bonus de continuité, retards et compléments réellement nécessaires, sans additionner arbitrairement tous les cas extrêmes.

**Quatrième priorité :** traiter la navigation des preuves, l’export de comité et le volume du bootstrap. Aucun de ces perfectionnements techniques ne remplace les validations métier et économiques.
