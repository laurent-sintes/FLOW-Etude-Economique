# Audit et réévaluation des politiques de ressources FLOW

Le calcul de 50 JH se reproduit. Il sous-représente cependant le périmètre de stratégie, paramétrage, configuration et contrôle des incompatibilités décrit dans la cartographie et précisé par le sponsor le 2 novembre 2026. La proposition de réévaluation est de **430 JH**, soit **271 k€ HT**. Elle remplace le lot entier de 50 JH, sans s’y ajouter. Les budgets adoptés restent inchangés tant que cette proposition n’est pas adoptée.

## Origine des 50 JH

Le calcul porte sur trois familles. La répartition par taille attribue 10 JH à l’éligibilité des prestataires, 19 JH aux politiques et 21 JH au devenir des biens. Ces parts sont des allocations du total, pas trois estimations indépendantes.

Pour les politiques, la taille est de 272,5 unités logiques équivalentes : 391 unités de règles Odoo × 0,5, plus 77 unités de structures Java. Avec 133,75 unités pour l’éligibilité et 294,35 pour le devenir, le total de 700,6 unités donne 50,9376 JH COCOMO avant arrondi. Le problème porte sur la transposition fonctionnelle et le découpage du travail, pas sur cette addition.

La cartographie définit déjà des stratégies, droits de ressources, portées, périodes, autorités et dérogations. Sa traduction dans le calcul a été comprimée en un seul module « activation et explication des politiques ». Le schéma conserve des champs génériques scope et criteria. Il ne dimensionne pas séparément le modèle des règles, leur configuration, leur composition ni les incompatibilités.

## Résultat du rescan

Le rescan couvre les fichiers de code disponibles dans les versions figées de quatre OSS, avec un dépôt Axelor Studio complémentaire. Les tests, traductions, fichiers statiques et bibliothèques générées sont exclus de la recherche. Un fichier correspondant à un mot clé n’est pas une preuve de couverture fonctionnelle.

| Référence | Fichiers examinés | Fichiers trouvés par mots clés |
|---|---:|---:|
| erpnext | 4722 | 1031 |
| odoo | 1679 | 496 |
| tryton | 3859 | 544 |
| axelor | 5615 | 783 |
| studio | 727 | 173 |

Le code des quatorze fichiers d’analogues retenus est archivé avec ses empreintes et ses commits dans results.json. Leur identité avec les objets Git des commits a été vérifiée après normalisation des fins de ligne Windows. Les rapprochements sont enregistrés comme analogies à qualifier dans source/instruction-marche.yaml.

| OSS | Analogue réellement retrouvé | Limite pour FLOW |
|---|---|---|
| ERPNext | Conditions multidimensionnelles de Pricing Rule, priorités, incompatibilités, conflits de même priorité et génération de règles promotionnelles | Fonction de tarification, pas gestion complète des droits de ressources ni compatibilité avec les engagements Supply |
| Odoo Community | Conditions d’applicabilité, périodes, catégories, contrôle des dates et récursion des listes de prix | Le mécanisme peut inspirer la configuration. Les quotas collectifs et conflits de politiques Supply ne sont pas démontrés |
| Tryton | Formules de listes de prix et règles ordonnées de rapprochement de relevés avec conditions typées | Recouvrement partiel sur les conditions et l’ordre. Pas preuve d’un moteur complet de politiques d’allocation |
| Axelor | PricingRule et PricingComputer, classification et évaluation de règles configurables. DMN et filtres dans Studio | Les noyaux et studios génériques sont à consommer une fois. Le raccordement et la sémantique Supply restent propres à FLOW |

Les lectures COCOMO des paniers de code complets sont conservées comme diagnostics partiels. Ces paniers contiennent aussi des fonctions de prix ou de comptabilité et ne couvrent pas les nouveaux contrôles Supply. Ils ne sont pas retenus comme budgets concurrents complets et ne sont pas moyennés avec COSMIC.

## Périmètre fonctionnel réévalué

Le périmètre reste dans BC-008. Les fonctions de référence et les mécanismes fournis gardent leur propriétaire. Un langage de règles borné est supposé. La vérification formelle d’un programme arbitraire est exclue.

| Fonction de politique | CFP |
|---|---:|
| Définir et réviser une stratégie | 7 |
| Configurer les bénéficiaires et périmètres | 8 |
| Configurer protections quotas et plafonds | 8 |
| Configurer priorités et marges de réarbitrage | 8 |
| Configurer les dérogations autorisées | 7 |
| Contrôler les paramètres et leurs combinaisons | 8 |
| Détecter les incompatibilités entre politiques | 9 |
| Contrôler la compatibilité avec les engagements | 9 |
| Exécuter un jeu de tests de politique | 8 |
| Planifier et autoriser une activation | 9 |
| Résoudre les règles applicables à un contexte | 8 |
| Expliquer une règle appliquée ou écartée | 6 |
| Suspendre ou retirer une politique | 8 |

Les fonctions correspondent à des commandes ou demandes distinctes. Une marque ou un canal supplémentaires ne créent pas automatiquement de points supplémentaires. Les déplacements de données et leurs groupes sont enregistrés dans results.json. Les cas d’impact et de tests consomment les services de calcul déjà financés, sans les reconstruire.

Le comptage passe de 17 à **103 CFP pour les politiques**. Les autres familles conservent **47 CFP**, soit **150 CFP pour le lot complet**. Le rendement de 20 h/CFP et la convention de 7 h/JH sont ceux du modèle actuel. Ils donnent **428.57 JH**, arrondis à **430 JH** au pas existant de 10 JH.

Cette proposition retient COSMIC car le périmètre fonctionnel détaillé est plus explicite que les analogies de code disponibles. Le rendement historique n’est pas calibré sur un moteur de politiques FLOW. À 15 ou 25 h/CFP, le même comptage donne respectivement 321 et 536 JH. Ce sont des sensibilités à une hypothèse, pas une fourchette statistique.

## Doubles comptes évités

| Responsabilité | Traitement |
|---|---|
| Choix des objectifs, règles, droits, périmètres et dérogations | Définition et configuration du produit dans cette réévaluation |
| Optimisation des protections et politique de réservation | Reste dans le lot décisions, dont la famille optimisation de 228 JH couvre cinq décisions |
| Priorisation, affectation et libération des demandes | Reste dans les 63 JH de la famille carnet, dans le lot décisions |
| Compteurs, réservations, consommation, expiration et concurrence | Reste dans Stock. Le contrôle de politique lit ses engagements et ne tient pas un second stock |
| Référentiels et versions génériques | Consommés de Master Data. Seules les structures de politique et règles de compatibilité propres au domaine sont nouvelles |
| Formulaires, éditeurs et approbations génériques | Consommés de Process Management. Pas de second studio ni nouveau moteur DMN complet |
| Paramétrage des politiques réelles des marques et canaux du Groupe | Travail de déploiement et mobilisation métier à rapprocher de l’intégration. La construction du produit configurable ne finance pas toute cette saisie métier |
| Pilotage projet, QA, architecture, sécurité | Compris dans la charge projet valorisée. Pas d’ajout proportionnel ni de second Transformation Office |

Le coût utilise les tarifs actuels et les proportions de rôles du lot existant, répartis sur le nouveau total avec conservation des JH. L’organisation de l’équipe reste à préciser.

## Effet proposé et décisions restantes

| Indicateur | Référence adoptée | Proposition |
|---|---:|---:|
| Lot complet | 50 JH | 430 JH |
| Coût du lot | 31 k€ HT | 271 k€ HT |
| Cumul des lots du Core | 5 950 JH | 6330 JH |

L’écart est de **380 JH et 239 k€ HT**. Ce cumul ne constitue pas une nouvelle estimation COCOMO intégrée du Core. Le calendrier global et les effets de maintenance ne sont pas recalibrés par cet audit.

La prochaine vérification utile porte sur les exemples de politiques, le nombre de commandes réellement distinctes et la frontière des contrôles avec les engagements existants. Il faut aussi établir la profondeur des incompatibilités à détecter, les règles d’activation, les garanties attendues et le rendement applicable. Aucun supplément de licence n’est déduit du seul inventaire fonctionnel.

## SAP et Microsoft

Microsoft documente des groupes d’allocation et leur consommation dans Inventory Visibility, ainsi que des règles DOM de validité, contraintes, protection et priorité. SAP documente Supply Protection, Product Allocation et Supply Assignment. Ces mécanismes confortent la nécessité d’une vraie configuration de stratégie. Leur existence dans les catalogues ne prouve pas leur inclusion complète dans les offres FLOW. Inventory Visibility reste une option dans les pièces reçues. Les droits et activations SAP concernés restent à confirmer.

- [Microsoft Inventory Visibility allocation](https://learn.microsoft.com/en-us/dynamics365/supply-chain/inventory/inventory-visibility-allocation) — consulté le 2 novembre 2026. Pools virtuels et allocation par groupes, protection et consommation. Inventory Visibility reste une option d’architecture dans les pièces FLOW.
- [Microsoft DOM rules](https://learn.microsoft.com/en-us/dynamics365/commerce/dom-rules) — consulté le 2 novembre 2026. Validité, contraintes, protection du stock, priorités de lieux et limitations de fractionnement. Pas preuve d’équivalence de toutes les politiques FLOW.
- [SAP aATP Supply Protection](https://learning.sap.com/courses/exploring-aatp-in-sap-s-4hana/outlining-aatp-with-supply-protection-sup-) — consulté le 2 novembre 2026. Groupes protégés, caractéristiques, périodes et priorités. Activation et droits de l’offre FLOW à confirmer.
- [SAP Fashion Supply Assignment](https://learning.sap.com/courses/exploring-fashion-functions-and-business-processes-in-sap-s-4hana-for-fashion-and-vertical-business/explaining-supply-assignment_af05618d-4954-4f22-9857-3dd12e3940c4) — consulté le 2 novembre 2026. Affectations, pénuries, libération et approvisionnements futurs. La sémantique d’affectation diffère des frontières FLOW.

Les preuves de calcul sont dans [results.json](results.json). Le script [rescan.py](rescan.py) reproduit le rescan et les calculs depuis les dépôts figés.
