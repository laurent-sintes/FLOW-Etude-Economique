# Audit de lecture autonome du dossier économique

**Le dossier est désormais compréhensible pour lire les coûts modélisés et leurs écarts. Il ne fournit pas encore une enveloppe complète ni une première tranche chiffrée à autoriser.** Les trois pages sont à conserver. Deux retouches éditoriales ciblées suffisent pour sécuriser la lecture actuelle. Les limites de financement restantes demandent des données et des arbitrages supplémentaires.

| Question du sponsor | Réponse trouvée dans le dossier |
| --- | --- |
| Combien coûte chaque option sur dix ans ? | Oui. Les trois cumuls sont visibles ensemble. |
| Combien dépenser jusqu’au service complet et quand ? | Oui. Montants et mois de service sont associés aux options. |
| D’où viennent les écarts ? | Les trois postes du cumul, les écarts avec Java et les principaux facteurs sont visibles. La conclusion comparative peut être plus directe. |
| Que coûte une année ? | Oui. La base annuelle et une annuité projetée sont distinguées, avec le statut de l’année. |
| Peut-on additionner les montants affichés ? | La relation entre les repères reste insuffisamment explicite près des chiffres. |
| Quelles hypothèses sont retenues ? | Oui. Elles sont fixes et leur statut est présenté avant les détails. |
| Que faut-il encore financer ? | Les sujets sont identifiés. Le budget complet et la prochaine tranche restent à établir. |

**Les améliorations sont acquises**

La comparaison affiche ensemble les cumuls et les dépenses jusqu’au service complet. À dix ans, elle montre **12 069 k€ HT pour Java, 21 627 pour Microsoft et 37 697 pour SAP**. Les dépenses jusqu’au service complet sont respectivement **8 171, 7 620 et 16 851 k€ HT**, aux mois **78, 44 et 36**.

Les postes construction ou sélection, intégration et services sont comparables côte à côte. Les écarts avec Java sont quantifiés. Le fonctionnement distingue sa base aux prix de référence de la dépense d’une année projetée. À trois ans, les annuités sont signalées comme des dépenses de projet avant le service complet. Le graphique annuel aide à situer les travaux et le fonctionnement.

Les hypothèses restent non modifiables. La construction Java est distinguée du calendrier provisoire, des offres et projections Buy, et des volumes de cadrage. Les forfaits fournisseur restent groupés dans le détail annuel. Les exclusions et la Finance SAP sont signalées.

Sur mobile à 390 × 844, les trois cumuls apparaissent à la même hauteur, vers **493 pixels**, et les blocs de dépenses au service complet commencent vers **537 pixels**. Aucun débordement horizontal global n’a été observé dans les vues contrôlées. La présentation ne justifie pas une nouvelle refonte.

**AUT 01 — Priorité 1 — Dire clairement quels montants sont compris dans les autres**

Dans les coûts Java à dix ans, trois montants voisins sont affichés : **12 069 k€ HT** de cumul, **8 171 k€ HT** jusqu’au service complet et **1 147 k€ HT** en année 10. Les deux derniers sont déjà compris dans le premier. Cette relation n’est pas formulée près des trois cartes. Un lecteur peut comprendre qu’il s’agit de budgets successifs à ajouter.

Le titre « cumul » donne un indice et la légende du graphique précise que ses années y sont comprises. Le panneau de périmètre dit aussi que les cumuls utilisent les mêmes dépenses. Ces explications ne remplacent pas une phrase d’inclusion directement associée aux montants.

La formulation doit tenir compte de l’horizon. À trois ans, Java affiche **3 209 k€ HT** de cumul et **8 171 k€ HT** jusqu’au service complet. Ce second montant couvre alors une période plus longue que les trois ans sélectionnés. Il ne faut donc pas écrire systématiquement qu’il est déjà compris dans le cumul choisi.

Préciser que les repères ne s’additionnent pas. Lorsque l’horizon couvre le service complet, afficher que la dépense correspondante est comprise dans le cumul. Pour un horizon plus court, dire qu’elle couvre une période plus longue. L’annuité projetée est une composante du cumul sélectionné, tandis que la base annuelle décrit un régime de référence.

La note « Travaux, moyens de transition et abonnements consommés avant cette date » est actuellement placée sous « Le coût d’une année de fonctionnement », vers **1 201 pixels** sur ordinateur. La date visée est celle du service complet, située plus haut dans les cartes. Replacer cette note près de ce montant supprime une ambiguïté de lecture.

**AUT 02 — Priorité 2 — Formuler la conclusion que les tableaux permettent de tirer**

L’encart « Ce qui change entre les options » explique le rôle des prix, des calendriers et des contrats. Le sponsor peut trouver les chiffres, mais doit encore énoncer lui-même leur conclusion.

La synthèse de la référence peut dire que Java présente le cumul à dix ans le plus faible, que Microsoft atteint le service complet plus tôt et avec une dépense préalable plus faible que Java, et que SAP porte le cumul le plus élevé avec la Finance conservée dans son offre. Ces constats restent rattachés au périmètre chiffré. Ils ne suffisent pas à recommander automatiquement une option.

Cette synthèse doit suivre les données et l’horizon choisi. Elle ne doit pas figer une conclusion indépendante d’une future évolution économique autorisée. Les prix, les durées de service et les périmètres expliquent ensemble la comparaison. Les offres groupées ne doivent pas être assimilées à de pures licences ni ventilées sans preuve.

**Les limites de décision ne sont plus cachées**

Le temps interne, la transformation, le maintien et le retrait de l’ancien SI sont explicitement à établir. Le sponsor sait donc que le chiffre principal représente le périmètre chiffré de l’étude. Une enveloppe complète d’exécution exige leur instruction pour chaque trajectoire. La mobilisation interne doit distinguer les ressources déjà financées d’éventuelles dépenses supplémentaires. Les contrats finaux et le périmètre comparable restent également à confirmer.

La prochaine tranche n’a pas encore de montant ni de périmètre arrêtés. L’application le dit et renvoie au jalon avant engagement. Elle permet de préparer cet arbitrage, mais ne constitue pas une demande de financement immédiatement chiffrée. Cette limite appelle un travail de décision et de dimensionnement. Un montant ne peut pas être ajouté pour compléter visuellement la page.

**Vérifications et portée**

Relecture des trois pages sur ordinateur à 1280 × 720, puis de la comparaison et des coûts sur mobile à 390 × 844. Vérification des horizons trois et dix ans, d’un détail annuel Microsoft et de la présentation des hypothèses. Modèle **01/11/2026 · n° 1**, livraison locale `daff241dadbf27612e6a238b853bcc667f8979a4e2fa429b74785411cbacb35f`.

Les **24 rapprochements arithmétiques exécutés passent**. Les observations sont une relecture experte du contenu affiché. Aucun entretien de compréhension n’a été réalisé avec le sponsor. Les tests techniques antérieurs ne sont pas utilisés comme preuve de compréhension.

Application, paramètres et modèle inchangés pendant cet audit. Les constats et limites sont dans [findings.json](findings.json), les montants et contrôles dans [financial-evidence.json](financial-evidence.json), et les textes observés dans [audit-sponsor-autonome-observations.json](audit-sponsor-autonome-observations.json).
