# Audit complet de l’application FLOW

Date : 5 novembre 2026. Référence examinée : modèle n° 17, commit `519b5da4dd43b0d98d26c64188b0a5f8bdd3770b`, application statique locale.

L’application fonctionne sur les parcours examinés, mais **la lecture des résultats manque encore de cohérence entre les écrans**. Les principaux risques concernent le statut des charges d’intégration, le périmètre Make ou Buy des chiffres et la distinction entre données inconnues et données sans objet. La chaîne de validation bloque également une prochaine livraison.

**Neuf constats sont retenus : trois P1 et six P2.** P1 signifie à corriger avant une prochaine livraison ou présentation des résultats. P2 signifie à traiter pour rendre la consultation fiable et utilisable. L’audit n’a modifié ni le code de l’application, ni les données, ni les hypothèses, ni les charges et coûts retenus.

## Résultats des vérifications

| Contrôle | Résultat | Portée |
| --- | --- | --- |
| Suite Python complète | 567 tests réussis sur 569, un échec et une erreur | Les deux défauts concernent des assertions de contrat devenues obsolètes |
| Tests JavaScript | 89 sur 89 | Contrats du client, navigation, transport et scénarios |
| TypeScript et contrôle éditorial | Réussis | Compilation des types et règles de contenu automatisées |
| Parcours ordinateur et mobile | 48 adresses dans deux formats | 1 440 × 1 000 et 390 × 844, alias compris, sans erreur JavaScript ou HTTP relevée ni débordement horizontal du document |
| Moteur Python dans le navigateur | Six scénarios et deux cas limites conformes à l’oracle Python | Référence isolée, version incompatible refusée |
| Métamodèle | 70 objets, 111 relations et sept domaines affichés | Sélection d’Unité de travail : 55 objets et 87 relations du lineage mis en évidence, traits à 3,5 px |
| Interactions principales | Onze équipes, trois modes, aucun trait fléché ni filtre | Sélection d’une interaction et affichage de son contrat vérifiés |
| Unités de travail | 104 travaux, filtres et fiche consultables | Passage aux 19 travaux de construction, recherche Master Data, ouverture, onglet équipe et retour avec filtre conservé |
| Téléchargements | Quatorze liens locaux accessibles | Empreinte du modèle exporté et des sept pièces originales vérifiée, archive de scénarios conservée et exportée à l’identique |
| Menu mobile | Ouverture au clavier et fermeture par Échap réussies | Retour du focus au déclencheur |
| Dépendances | Aucune alerte retournée par les audits pnpm | Dépendances de production et de développement, à la date de l’audit |

Le contrôle navigateur officiel échoue avant ses parcours à cause de son inventaire de navigation obsolète. Les parcours et preuves ci-dessus proviennent donc de vérifications indépendantes, sans neutraliser les assertions dans les tests du dépôt. Le graphe a été revérifié après chargement complet sur les deux formats, car les premières captures générales montraient son état de chargement.

Les tests réussis contrôlent des propriétés du logiciel. Ils ne valident pas à eux seuls la pertinence des hypothèses d’estimation.

## Constats prioritaires

| ID | Priorité | Constat | Conséquence |
| --- | --- | --- | --- |
| A01 | P1 | La validation complète ne passe plus | Une prochaine livraison est bloquée par les contrôles du dépôt |
| A02 | P1 | Les anciens JH d’intégration paraissent encore dimensionnés | Le lecteur peut prendre une estimation à reprendre pour une charge validée |
| A03 | P1 | Une fiche d’équipe ouverte en Buy affiche des montants Make | Le même contexte produit des lectures financières incompatibles |
| A04 | P2 | Des composantes inconnues sont affichées Sans objet | Le détail paraît exclure des dépenses dont la nature reste inconnue |
| A05 | P2 | Un livrable peut être déduit de commentaires de chiffrage | La complétude du contrat de travail est surestimée |
| A06 | P2 | Deux vues des interactions utilisent des notations différentes | La convention du livre n’est pas appliquée de façon cohérente |
| A07 | P2 | Les consolidations imposent un long détail avant une exploration ciblée | La synthèse par équipe reste difficile à exploiter |
| A08 | P2 | Le clavier traverse tout le menu au premier chargement | L’accès au contenu exige 33 tabulations sur ordinateur |
| A09 | P2 | Des informations utiles descendent sous le minimum typographique prévu | Les unités, statuts et repères deviennent difficiles à lire |

### A01 La validation complète bloque la livraison

La commande `python -m tools.check_model --full --browser` termine en échec après 569 tests Python. Le test de navigation cherche encore le groupe « Framework d’évaluation » et impose l’ancien voisinage des rubriques. Le test du bootstrap attend un ensemble de contenus qui ne comprend pas `framework_graph` et `delivery_organisation`.

L’exécution séparée du contrôle navigateur échoue également sur l’égalité de l’ancien inventaire de navigation. Son parcours n’inclut pas les six nouvelles pages d’organisation, de consolidation et de métamodèle, ni `synvance-delays`. La CI exécute ces contrôles avant le déploiement. **Le blocage est reproduit localement et la même assertion déterministe est présente dans le workflow distant.** Aucun déploiement distant n’a été déclenché pour cet audit.

Mettre les assertions à jour avec le contrat actuel, puis intégrer les parcours manquants. Ajouter des contrôles qui confrontent les chiffres entre fiches d’équipe, consolidations et choix Make ou Buy. Ne pas supprimer ces contrôles pour obtenir une validation verte.

Références : [test de navigation](../../tools/test_gross_evaluations.py#L33), [test du bootstrap](../../tools/test_study_http.py#L80), [inventaire navigateur](../../app/scripts/verify-pages.mjs#L24), [assertion bloquante](../../app/scripts/verify-pages.mjs#L166), [workflow](../../.github/workflows/pages.yml).

### A02 Les JH d’intégration gardent une apparence de validation

Ouvrir `#charges-integration?option=java-spring`. Le premier résultat affiche **5 825 JH dimensionnés**, suivi d’un scénario central et de travaux détaillés. Aucun statut de donnée historique à reprendre n’est placé auprès de ce total.

La fiche d’équipe affiche au contraire « Non évalué — étude d’intégration à reprendre ». La source d’organisation exclut explicitement les charges de cette phase de la ventilation retenue. La conservation des anciens calculs est légitime pour la traçabilité, mais leur présentation actuelle ne fait pas comprendre leur statut.

Afficher ce statut au niveau du résultat principal et des sous-totaux. Réserver l’intitulé de charge retenue aux données effectivement retenues. **Conserver les montants et anciens calculs, sans réactiver automatiquement leurs JH dans les équipes.**

Références : [source d’organisation](../../source/organisation-delivery.yaml#L5), [affichage du total](../../app/src/GrossEvaluationsPage.tsx#L158), [preuve](preuves/integration-dimensionnee.png).

### A03 Les fiches Buy exposent des montants Make

Ouvrir `#equipes-produit?option=microsoft&focus=master-data`, puis la même fiche avec `option=sap`. Dans les deux cas, la fiche affiche **1 600 JH et 1 040 k€ de construction**, issus du périmètre Java/Spring.

La note qui explique le périmètre Make se trouve en bas de la page, à environ 4 337 px du haut dans le cas Microsoft testé. Le lien vers les coûts conserve pourtant l’option Buy et mène à une page qui n’affiche pas cette matrice, puisque la ventilation Buy n’existe pas. Un lecteur peut donc attribuer les chiffres Make à Microsoft ou SAP avant d’accéder à la réserve de périmètre.

Conditionner les matrices au périmètre réellement disponible ou afficher leur contexte Make immédiatement auprès des chiffres. Les contrats Buy doivent rester non ventilés lorsque leurs données ne permettent pas une attribution aux équipes.

Références : [matrices inconditionnelles de la fiche](../../app/src/DeliveryOrganisationPage.tsx#L29), [note Buy](../../app/src/DeliveryOrganisationPage.tsx#L32), [consolidation conditionnée](../../app/src/TeamConsolidationPage.tsx#L25), [preuve](preuves/buy-montants-make.png).

### A04 Une ventilation inconnue devient Sans objet

Dans `#couts-equipes?option=java-spring`, consulter le détail de `funding/travaux_communs`. La ligne présente **1 192 k€**, une part à détailler de 1 192 k€, et « Sans objet » dans les colonnes Travail et Frais. Les valeurs de ces deux composantes sont pourtant inconnues dans le modèle. Vingt-neuf contributions d’intégration présentent une part non classée positive et sont concernées par cette règle d’affichage.

Le composant déduit « Sans objet » d’une valeur nulle dès lors que le total est connu. Un total connu ne démontre pas l’inapplicabilité de ses composantes. Cela masque la nature de l’information encore attendue, même si le total financier est conservé.

Utiliser « À détailler » ou « À renseigner » pour la ventilation inconnue. Réserver « Sans objet » aux composants explicitement déclarés inapplicables. Ajouter un cas de contrôle qui distingue enveloppe non ventilée, achat sans JH et exclusion confirmée.

Références : [règle de rendu](../../app/src/TeamConsolidationPage.tsx#L20), [preuve](preuves/inconnu-sans-objet.png), [données de reproduction](preuves/focused-proofs.json).

### A05 Le livrable est parfois un commentaire sur le chiffrage

Ouvrir `#unites-travail?focus=core%2Fmaster-data-java-spring`. « Ce que ce travail doit produire » contient notamment « analyse produit » puis une phrase expliquant que les livrables détaillés adoptés remplacent l’ancien chiffrage. La liste comprend aussi conception, QA et pilotage local. Elle décrit des activités et une décision de chiffrage, sans définir à elle seule un résultat métier réceptionnable.

Le contrat déclaré de cette unité ne renseigne pas son livrable. Le moteur construit néanmoins un résultat à partir du champ historique `includes` et ne remonte que les critères de réception parmi les informations manquantes. Le défaut porte donc aussi sur le diagnostic de complétude.

Présenter les activités incluses et justifications dans leurs rubriques respectives. Ne considérer le livrable comme renseigné qu’à partir d’un résultat explicite et pertinent. Le contrat permet déjà de compléter le périmètre sans réestimer les charges retenues.

Références : [construction du résultat](../../tools/work_units.py#L164), [reprise dans le contrat](../../tools/work_estimation.py#L113), [preuve](preuves/livrable-commentaire.png).

### A06 Les interactions ont encore deux notations

La page `#integration-transverse` respecte les choix demandés : trois symboles du livre, onze équipes placées par couches, aucun filtre et aucune flèche de relation. La sélection ouvre le détail de l’interaction.

La vue `#schema-modele?view=teams` représente les mêmes interactions avec **29 traits fléchés et aucun symbole du livre**. Elle inclut également la gouvernance dans cette vue technique. Le composant du métamodèle applique un marqueur de flèche à tous les profils, y compris celui des interactions d’équipes.

Réutiliser la représentation des interactions ou rendre les symboles propres à chaque mode dans ce profil. Conserver le sens et les cardinalités pour les relations du métamodèle, qui ont une autre fonction. Cette correction ne remet pas en cause le lineage, les domaines colorés ou les courbes du graphe complet, qui fonctionnent dans les cas testés.

Références : [marqueur commun](../../app/src/FrameworkModelMapPage.tsx#L50), [diagramme principal](../../app/src/TeamInteractionMap.tsx#L48), [preuve](preuves/autre-notation-interactions.png).

### A07 Les consolidations restent trop longues et peu explorables

Sans filtre, les pages Charges par équipe et Coûts par équipe mesurent respectivement environ **12 821 et 14 992 px** de haut sur ordinateur, pour plus de 3 200 mots chacune. Leur matrice de synthèse est suivie d’un tableau détaillé sur toutes les phases. Les cellules de la matrice ne permettent pas de rejoindre directement le détail correspondant et aucun filtre de phase ne limite ce tableau. Le filtre d’équipe réduit déjà le volume, mais ne suffit pas à expliquer un montant donné.

Faire de la matrice un point d’entrée vers les contributions de l’équipe et de la phase sélectionnées. Afficher d’abord total, statut et reliquat, puis le détail sur demande. Conserver les liens précis vers les unités et leurs sources. Cela répond aux deux lecteurs du projet sans ajouter de boutons qui répètent le menu général.

Références : [sélection des lignes](../../app/src/TeamConsolidationPage.tsx#L15), [matrice et détail](../../app/src/TeamConsolidationPage.tsx#L30), [mesures des pages](preuves/coverage.json).

### A08 Le premier accès au contenu est trop coûteux au clavier

Sur un chargement neuf de l’accueil en format ordinateur, le premier contrôle du contenu est atteint à la **33e tabulation**, après le logo et les destinations du menu. Aucun lien d’évitement vers le contenu n’est présent. Le déplacement du focus au changement de page et le comportement du menu mobile sont déjà gérés dans les parcours vérifiés.

Ajouter un lien « Aller au contenu » visible au focus dès le début de la page et une cible principale stable. Vérifier son activation au clavier sur un chargement neuf, sans modifier le fonctionnement des liens directs.

Références : [structure de l’application](../../app/src/App.tsx#L144), [séquence de focus](preuves/focused-proofs.json).

### A09 Des textes utiles passent sous le seuil de la charte

Les mesures dans le navigateur trouvent des textes de **10,36 à 10,92 px** : groupes de sélection d’équipe, unités et précisions des matrices, statuts et natures des travaux, notes des paramètres et de l’évaluation. Les six vues concernées dans l’échantillon sont Équipes et missions, Charges par équipe, Coûts par équipe, Unités de travail, Paramètres et Évaluation du Core.

La charte prévoit au moins 11 px pour les unités, familles et identifiants. Les petits textes portent ici des informations utiles, notamment la différence entre état partiel, référence et nature du travail. Les contrastes calculables dans cet échantillon ne présentent pas le même défaut.

Remonter les tailles sous le seuil prévu et vérifier le rendu réel sur mobile et au zoom. Garder les statuts et unités lisibles sans imposer au lecteur de grossir toute la page. L’échantillonnage de contraste ne constitue pas une certification d’accessibilité.

Références : [charte](../../app/BRANDING.md#L20), [styles des travaux](../../app/src/workUnits.css#L1), [mesures typographiques](preuves/typographie.json).

## Complétude des données de chiffrage

Le contrat commun et la consolidation sont en place. **Les données disponibles ne permettent pas encore de produire un chiffrage complet par équipe sur les trois phases.** Ce manque est attendu et ne justifie pas d’inventer des valeurs.

| Phase | Unités présentes | Unités ayant des informations manquantes signalées |
| --- | --- | --- |
| Obtenir le Core System | 19 | 19 |
| Intégrer à Beaumanoir | 71 | 71 |
| Faire fonctionner et évoluer | 14 | 14 |

La lecture de travail classe 78 unités comme partielles et 26 comme en attente. Dans l’intégration, 41 unités signalent notamment des quantités, efforts unitaires, gains et périodes à compléter. Les tarifs manquent pour quinze unités. Ces nombres reprennent le diagnostic actuel du moteur et restent soumis au défaut de livrable décrit en A05.

Les capacités disponibles, les contributions effectives, la revue exhaustive des périmètres et les responsabilités non documentées restent à renseigner. Une enveloppe financière historique ne doit pas suffire à déclarer ces travaux dimensionnés ou affectés. Le fonctionnement annuel doit conserver son assiette annuelle distincte des phases initiales.

## Ordre de traitement

Corriger d’abord les contradictions de périmètre et de statut des montants : A02, A03 et A04. Remettre simultanément la chaîne de contrôle en état avec A01, en y ajoutant ces cas de régression.

Fiabiliser ensuite la définition des résultats attendus et des informations manquantes avec A05, puis harmoniser la notation des équipes avec A06. Terminer par l’exploration des consolidations, l’accès clavier et la typographie avec A07 à A09. Toutes ces corrections peuvent conserver les chiffrages retenus.

## Périmètre et limites

La revue couvre la navigation, les pages courantes et leurs alias, les principaux parcours d’organisation et de chiffrage, les représentations graphiques, les contrats de données, les calculs exercés par la suite complète, le worker Python, les exports et les dépendances. Les détails sont conservés dans [les résultats structurés](findings.json) et [la couverture](preuves/coverage.json).

Le chargement neuf local transfère environ 4,37 Mo de ressources mesurées, dont un bootstrap JSON de 2,45 Mo. Ce relevé sur serveur local sans compression ne prédit pas le temps de chargement de GitHub Pages sur un réseau mobile. Il constitue un point de départ pour mesurer le chargement en conditions de diffusion.

Le déploiement distant, les autres navigateurs, un lecteur d’écran, les réseaux contraints, tous les liens externes et un test d’intrusion ne font pas partie des preuves obtenues. L’audit des dépendances ne remplace pas un audit de sécurité. Les références métier et les prix externes n’ont pas été requalifiés dans cet audit logiciel.
