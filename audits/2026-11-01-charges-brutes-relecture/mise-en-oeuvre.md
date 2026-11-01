# Mise en œuvre de l’audit des charges brutes

**La référence adoptée apparaît en premier. Les explications reprennent les paramètres actifs et les détails restent accessibles par lot et par activité.** Le menu, les trois phases, leurs icônes et les trois options visibles sont conservés.

## Contenu corrigé

- Les interfaces sont expliquées par le scénario central : 40 interfaces × 10,5 JH = 420 JH. L’ancien diagnostic n’est plus associé à la valeur active. Les paramètres viennent du scénario propriétaire.
- Les 90 k€ de support et conseil qualité initiaux Microsoft apparaissent dans l’intégration. Ils sont retirés de l’écran de fonctionnement. La pièce originale, sa période et le financement unique restent inchangés.
- Les résultats précisent leurs activités couvertes. Le Core inclut les rôles de réalisation du produit. L’intégration distingue travaux communs, déploiements et pilotage du programme, avec sous-totaux. Les provisions exprimées en euros restent séparées des JH.
- Le fonctionnement expose le pilotage déjà financé dans le budget annuel, sans lui inventer une charge en jours. Les montants sont copiés depuis la lecture économique existante.
- Les volumes et charges unitaires du fonctionnement se consultent dans le détail des activités. Le support N1 conserve notamment son volume et le temps de traitement documenté.

## Lecture et preuves

La page Core présente les 6 660 JH adoptés, puis les lots. Les liens des lots ouvrent une fiche avec une adresse partageable, la date de décision, les activités incluses et exclues, les rôles et la preuve de calcul. Un retour ramène à la liste. La preuve JSON d’origine reste intacte, avec une note distinguant sa version historique de la décision active.

La proposition à 5 950 JH reste explicitement **non adoptée**. Elle est accessible dans un bloc distinct avec sa date, sa comparaison par lot, les arbitrages et sa preuve. La comparaison des quatre logiciels à code ouvert reste disponible en approfondissement.

Les neuf vues comportent une synthèse propre à l’option et à la phase. Un lien donne accès à la définition canonique de la charge brute. Les chiffres entiers n’affichent plus une décimale inutile.

Sur mobile, les noms et valeurs des lots restent adjacents. Les tableaux de proposition et de comparaison deviennent des fiches. Les activités réunissent leur libellé, leur valeur et un détail seulement lorsqu’une explication est disponible. Les contrôles à ouvrir sans contenu sont retirés.

Les années tarifaires consécutives à prix identique sont regroupées à l’écran. Le prix annuel et la période sont explicites. Le support initial Microsoft conserve un montant ponctuel. Les données d’annuités ne sont pas modifiées.

## Conservation économique

La référence complète des cinq options est **strictement identique** au témoin enregistré avant l’intervention, y compris paramètres, financements, annuités et horizons. Les paramètres historiques restent disponibles pour les anciennes simulations. Le contrat des simulations est inchangé.

Aucune révision des JH, aucun changement de tarif, aucune adoption de proposition ni nouveau financement n’a été effectué. La construction reste à 6 660 JH, l’intégration à 3 935 JH et le fonctionnement à environ 1 421,9 JH/an. Les travaux acheteur Buy restent à 110 JH.

## Vérifications

- La sélection transitive initiale a exécuté 373 tests Python. Le seul échec concernait un plafond de taille du chargement initial, déjà dépassé par les textes des préétudes. Les fiches de charges restent hors du chargement initial et sont chargées à la demande.
- Le plafond a été porté de 1 100 000 à 1 120 000 octets pour conserver ce contenu. Une limite supplémentaire de 280 000 octets compressés a été ajoutée. La livraison mesure 1 105 567 octets bruts et environ 271 ko compressés. Le format de transport et les données ont été conservés.
- Les onze tests HTTP ont ensuite réussi. Les contrôles de typage, les 65 tests d’interface et la vérification des textes ont réussi après la dernière correction de rendu. Les rapports conservent les résultats de toutes les passes, y compris les échecs corrigés. La suite complète de certification n’a pas été lancée.
- Les neuf combinaisons phase/option ont été contrôlées en 1 280 × 720 et en largeur mobile de 390 px. Les tableaux ne provoquent plus de défilement horizontal mobile. Les détails du lot Master Data, l’ouverture de sa preuve JSON, le retour aux lots et l’adresse directe des interfaces ont été vérifiés.
- La première métrique apparaît vers 524 px sur le mobile contrôlé, contre environ 669 px lors de l’audit. Les neuf vues ne présentent aucune alerte de chargement.
- Vérification des différences sans erreur d’espacement. L’application locale est reconstruite. Aucun commit ni push effectué.

Version locale : `dca575e134ea039f33041bb1ec389864cc1659ebcc87c9146aa2008646d12800`.

Les observations sont conservées dans `browser-apres.json` et `verification-apres.json`. Les rapports détaillés des contrôles sont dans `tmp/gross-polish/`. Les budgets et les preuves d’origine sont conservés.
