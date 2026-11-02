# Proposition de charge après revue des scénarios

**Proposition de construction : 7 030 JH et 4,429,190 euros HT**, contre 5 950 JH et 3 749 300 euros HT adoptés. Le complément proposé est de 1 080 JH et 679 890 euros HT. Les simulations et les budgets continuent à utiliser les décisions adoptées.

Cinq lots sont remplacés sur leur périmètre entier. Les anciens processus sont retirés avant le nouveau comptage. Les six autres montants sont conservés sous les bornes fonctionnelles précisées ci-dessous. La proposition à 610 JH pour politiques, éligibilité et devenir remplace celle à 430 JH. Aucun des deux montants ne s’ajoute aux 50 JH adoptés.

## Charges proposées

| Lot | JH adoptés | JH proposés | Euros HT proposés |
| --- | ---: | ---: | ---: |
| Master Data Java/Spring | 1500 | 1500 | 944000 |
| Stock Java/Spring | 340 | 340 | 213970 |
| Propriété du stock Java/Spring | 190 | 190 | 119970 |
| Politiques, éligibilité et devenir des biens Java/Spring | 50 | 610 | 383630 |
| Gestion des commandes Java/Spring | 170 | 420 | 264760 |
| Préparation et pilotage du Master Plan Java/Spring | 250 | 330 | 208140 |
| Promesse, affectation et optimisation Supply Java/Spring | 530 | 710 | 447330 |
| Prestations et reconnaissance des résultats Java/Spring | 420 | 430 | 271040 |
| Process Management avec studios, portail, formulaires et pilotage | 1960 | 1960 | 1233730 |
| Ateliers visuels de planification et de décision | 160 | 160 | 100630 |
| Administration, robustesse et services IT complémentaires | 380 | 380 | 241990 |

Les coûts utilisent les mêmes proportions de rôles, tarifs et outillage que le lot actuel, avec une répartition entière des nouveaux JH. Ils incluent les activités projet déjà retenues, pas seulement le développement. Aucun directeur de programme ni Office FLOW supplémentaire n’est ajouté ici.

## Pourquoi le chiffrage change

Le comptage prévisionnel distingue 123 demandes et résultats métier dans les cinq lots. COSMIC compte chaque groupe de données une fois par type de mouvement et par processus. Une marque, une société, un prestataire ou un type de traitement ne multiplie pas un même service. Le périmètre détaillé remplace les 69 anciens processus de ces lots. Les étapes internes d’un algorithme ne sont pas déclarées comme des commandes externes supplémentaires.

La formule reste **CFP × 20 h/CFP ÷ 7 h/JH**, puis arrondi à la dizaine de JH par lot. Les 20 h/CFP sont la référence historique de l’étude, non une productivité observée sur FLOW. Ce sont des besoins prévisionnels proposés, non une mesure COSMIC certifiée. Les algorithmes, l’ergonomie et les garanties de performance ne se dimensionnent pas par leurs seuls échanges de données.

Les anciens COCOMO et les quatre colonnes OSS restent les preuves du périmètre antérieur. Les petits analogues de règle, réservation, qualité ou calendrier ne couvrent pas le périmètre complet révisé. Leur moyenne ne justifierait pas le nouveau montant. Faute de panier de code équivalent établi, la proposition retient le comptage fonctionnel explicite pour ces cinq lots et conserve les hypothèses COCOMO des six autres. Il ne s’agit pas d’une nouvelle estimation COCOMO intégrée du Core.

## Fonctions comptées par lot

### Politiques, éligibilité et devenir des biens Java/Spring

Configuration et résolution des règles, application atomique des droits collectifs et devenir des biens. Stock fournit transactions, positions, réservations individuelles et filiation. Décisions fournit recommandations et affectations. Aucun second moteur commun. Le lot remplace aussi la proposition antérieure à 430 JH.

64 → **214 CFP**, soit **610 JH** proposés.

| Fonction sur demande ou événement explicite | Capacités | CFP |
| --- | --- | ---: |
| Définir et réviser une stratégie | BC-008 | 7 |
| Configurer les bénéficiaires et périmètres | BC-008 | 8 |
| Configurer protections quotas et plafonds | BC-008 | 8 |
| Configurer priorités et marges de réarbitrage | BC-008 | 8 |
| Configurer les dérogations autorisées | BC-008 | 7 |
| Contrôler les paramètres et leurs combinaisons | BC-008 | 8 |
| Détecter les incompatibilités entre politiques | BC-008 | 9 |
| Contrôler la compatibilité avec les engagements | BC-008 | 9 |
| Exécuter un jeu de tests de politique | BC-008 | 8 |
| Planifier et autoriser une activation | BC-008 | 9 |
| Résoudre les règles applicables à un contexte | BC-008 | 8 |
| Expliquer une règle appliquée ou écartée | BC-008 | 6 |
| Suspendre ou retirer une politique | BC-008 | 8 |
| Tenir une restriction de prestataire | BC-001 | 6 |
| Contrôler une nouvelle sollicitation | BC-001 | 5 |
| Exposer les engagements touchés par une désactivation | BC-001 | 5 |
| Créer ou corriger une enveloppe de droits collectifs | BC-008 | 8 |
| Consommer atomiquement les droits des groupes admissibles | BC-008 | 8 |
| Restituer les droits après annulation ou correction | BC-008 | 7 |
| Réviser les droits entre bénéficiaires sous autorité | BC-008 | 9 |
| Consulter alloué consommé et restant | BC-008 | 5 |
| Rapprocher consommation des droits et effets reconnus | BC-008 | 6 |
| Définir le contexte opérationnel article usage marché saison | BC-008 | 6 |
| Préparer une bascule partielle en permanent | BC-008 | 7 |
| Autoriser la bascule opérationnelle retenue | BC-008 | 7 |
| Qualifier les biens et quantités concernés par un devenir | BC-019 | 7 |
| Déterminer les usages et traitements autorisés | BC-019 | 6 |
| Comparer valeur récupérable coûts délais et risques | BC-019 | 7 |
| Autoriser une destination pour les quantités retenues | BC-019 | 7 |
| Rapprocher les effets du devenir et maintenir les restes | BC-019 | 5 |

### Promesse, affectation et optimisation Supply Java/Spring

Comptage des demandes métier distinctes, sur modèles bornés et solveurs réutilisés. Aucun optimum global ni temps de réponse garanti sans mesure. Politiques et droits collectifs sont configurés et consommés dans contrôles. Les réservations restent dans Stock, les engagements dans Orders, le calcul net dans Master Plan.

166 → **249 CFP**, soit **710 JH** proposés.

| Fonction sur demande ou événement explicite | Capacités | CFP |
| --- | --- | ---: |
| Classer collectivement les demandes sur un contexte commun | BC-036 | 6 |
| Affecter les ressources en préservant les liens protégés | BC-037 | 9 |
| Réexaminer les liens autorisés et leurs effets collectifs | BC-037 | 9 |
| Décider livraison complète ou partiel admissible | BC-038 | 9 |
| Expliquer les réponses non admissibles et le réexamen | BC-036, BC-037, BC-038 | 7 |
| Recommander les objectifs de stock magasin ou centre | BC-040 | 8 |
| Recommander conjointement les cibles multi-échelon | BC-040 | 9 |
| Recommander droits et plafonds entre bénéficiaires | BC-041 | 7 |
| Recommander les conditions de réservation selon service et risque | BC-042 | 7 |
| Proposer un apport pour besoin daté ou cible | BC-043 | 9 |
| Proposer une révision des apports déjà attendus | BC-043 | 7 |
| Proposer rééquilibrage ou consolidation physique | BC-044 | 8 |
| Soumettre la recommandation à l’autorité compétente | BC-040, BC-041, BC-042, BC-043, BC-044 | 6 |
| Calculer sur stock courant ou projeté admissible | BC-046 | 9 |
| Établir la faisabilité d’un nouvel apport | BC-047 | 8 |
| Vérifier la faisabilité à capacité finie | BC-047 | 10 |
| Construire une possibilité commune à plusieurs lignes | BC-046, BC-047 | 8 |
| Évaluer les coûts comparables et coûts inconnus | BC-048 | 8 |
| Choisir la possibilité économiquement admissible | BC-048 | 8 |
| Réexaminer la possibilité avant sa confirmation | BC-046, BC-047, BC-048 | 8 |
| Qualifier une offre de capacité avec ses réserves | BC-049 | 6 |
| Demander une capacité fournisseur avant achat ferme | BC-049, BC-051 | 7 |
| Reconnaître confirmation révision ou libération de capacité | BC-049, BC-051 | 8 |
| Déterminer prestations et résultats nécessaires | BC-050 | 6 |
| Choisir prestation et exécutant admissibles | BC-051 | 8 |
| Construire les chargements sous contraintes | BC-052 | 9 |
| Déterminer trajets arrêts et horaires compatibles | BC-052 | 9 |
| Réviser le plan local ou signaler la promesse intenable | BC-052, BC-054 | 8 |
| Définir les dépendances de prestations du besoin | BC-053 | 6 |
| Reconnaître progression et impact d’un aléa | BC-053, BC-054 | 7 |
| Autoriser puis demander une adaptation locale | BC-054 | 7 |
| Décider lot ou regroupement utile des prestations | BC-055 | 8 |

### Gestion des commandes Java/Spring

Remplacement des sept fonctions génériques. Commandes typées mutualisées, engagements réciproques et attentes financières distingués. Stock, propriété, prestations et workflow sont consommés sans les reconstruire. Un type de commande ou une société ne multiplie pas les points.

58 → **147 CFP**, soit **420 JH** proposés.

| Fonction sur demande ou événement explicite | Capacités | CFP |
| --- | --- | ---: |
| Recevoir une commande typée et ses lignes | BC-020, BC-021, BC-022, BC-023, BC-024 | 6 |
| Accepter ou réviser un engagement de commande | BC-020, BC-021, BC-022 | 7 |
| Autoriser une annulation totale ou partielle | BC-020, BC-021, BC-022 | 9 |
| Faire progresser la précommande avec la même identité | BC-020 | 6 |
| Affermir un achat planifié avec filiation et notification au plan | BC-021 | 9 |
| Scinder en préservant quantités liens et engagements | BC-027 | 9 |
| Regrouper sans effacer les identités de commande | BC-027 | 6 |
| Fusionner les commandes compatibles | BC-027 | 8 |
| Rapprocher résultats et reste à satisfaire | BC-020, BC-021, BC-022, BC-023, BC-024 | 6 |
| Appliquer une autorisation aux seules lignes à livrer | BC-020 | 7 |
| Demander apport ou reprise sous accord de consignation | BC-023, BC-024 | 6 |
| Enregistrer un retour et sa résolution autorisée | BC-025, BC-026 | 8 |
| Lier le retour fournisseur à ses attentes propres | BC-026 | 6 |
| Relier la vente de remplacement et son attendu | BC-025, BC-020 | 6 |
| Rapprocher les suites physiques et financières du retour | BC-025, BC-026 | 6 |
| Établir les engagements réciproques par ligne et société | BC-020, BC-021, BC-027 | 7 |
| Recevoir la réponse ou révision de l’autre société | BC-020, BC-021, BC-027 | 8 |
| Rapprocher le même réalisé des engagements distincts | BC-020, BC-021 | 7 |
| Relier retour partiel et autorisations réciproques | BC-025, BC-026, BC-027 | 6 |
| Tenir le traitement acheteur et les attentes financières | BC-021, BC-025, BC-026 | 7 |
| Restituer engagements liens et restes de commande | BC-020, BC-021, BC-022, BC-023, BC-024, BC-025, BC-026, BC-027 | 7 |

### Préparation et pilotage du Master Plan Java/Spring

Calculs internes et ingestion externe distincts. Prévision source et calculateurs spécialisés ne sont pas reconstruits. Les commandes et résultats métier sont comptés, pas chaque étape interne d’un même algorithme. Le moteur de jobs fournit le lancement et la reprise techniques.

74 → **116 CFP**, soit **330 JH** proposés.

| Fonction sur demande ou événement explicite | Capacités | CFP |
| --- | --- | ---: |
| Recevoir une contribution externe de plan | BC-028 | 6 |
| Qualifier la prévision pour son usage opérationnel | BC-029 | 7 |
| Construire la demande et la prévision résiduelle | BC-030 | 8 |
| Construire ou réviser la projection d’approvisionnement | BC-032 | 7 |
| Interpréter les contributions de demande et d’apports | BC-031, BC-033 | 6 |
| Remplacer l’apport planifié par son achat ferme sans doublon | BC-028, BC-033 | 8 |
| Rapprocher les plans et retenir la version autorisée | BC-034 | 8 |
| Définir périmètre horizon et objectifs du calcul net | BC-035 | 6 |
| Définir le lancement métier ponctuel ou récurrent | BC-035 | 6 |
| Lancer le calcul net sur des coupes identifiées | BC-035 | 10 |
| Arrêter le calcul et constater son arrêt | BC-035 | 6 |
| Relancer après correction ou échec avec effets acquis | BC-035 | 7 |
| Exécuter une variante isolée et ses hypothèses | BC-045 | 6 |
| Comparer les variantes sur des indicateurs communs | BC-045 | 6 |
| Transmettre les seuls changements autorisés | BC-039 | 6 |
| Reconnaître acceptation refus et effets partiels | BC-039 | 7 |
| Restituer écarts et besoins de réexamen | BC-035 | 6 |

### Prestations et reconnaissance des résultats Java/Spring

Contrats et reconnaissance des faits sans refaire les opérations des exécutants. Les douze traitements partagent le cycle. Stock tient la filiation et les registres, contrôles décide du devenir, décisions choisit et coordonne, Process Management traite les tâches humaines. Connecteurs Beaumanoir, fiscalité et banque restent hors construction générique.

135 → **152 CFP**, soit **430 JH** proposés.

| Fonction sur demande ou événement explicite | Capacités | CFP |
| --- | --- | ---: |
| Enregistrer une demande de prestation typée | BC-059, BC-060, BC-061, BC-062, BC-063, BC-064, BC-065, BC-066, BC-067, BC-068, BC-069, BC-070, BC-071, BC-072, BC-073, BC-074, BC-075 | 7 |
| Recevoir les engagements et changements du prestataire | BC-059, BC-060, BC-061, BC-062, BC-063, BC-064, BC-065, BC-066, BC-067, BC-068, BC-069, BC-070, BC-071, BC-072, BC-073 | 6 |
| Intégrer un fait ou une estimation avec sa provenance | BC-056 | 6 |
| Rapprocher attendu et résultats partiels reconnus | BC-057 | 7 |
| Qualifier une contradiction ou corriger le reconnu | BC-056, BC-057 | 8 |
| Restituer les perspectives entrepôt transport magasin | BC-058 | 5 |
| Porter les exigences et preuves du traitement typé | BC-059, BC-060, BC-061, BC-062, BC-063, BC-064, BC-065, BC-066, BC-067, BC-068, BC-069, BC-070 | 6 |
| Reconnaître unités logistiques et contenus annoncés | BC-060, BC-063, BC-069, BC-056 | 8 |
| Reconnaître les contenus réellement constatés | BC-060, BC-063, BC-069, BC-056 | 7 |
| Transmettre assemblage décomposition et personnalisation reconnus | BC-063, BC-067, BC-056 | 7 |
| Qualifier l’écart entre demandé annoncé et reçu | BC-057, BC-060, BC-069 | 8 |
| Reconnaître la preuve partielle du traitement de biens | BC-066, BC-068, BC-070 | 7 |
| Porter arrêts étapes rendez-vous et changements autorisés | BC-071 | 6 |
| Demander une réservation autonome de transport | BC-072 | 6 |
| Reconnaître confirmation changement ou libération du booking | BC-072 | 5 |
| Confier le dossier de dédouanement | BC-073 | 6 |
| Reconnaître pièces requises manquantes ou fournies | BC-073 | 7 |
| Reconnaître l’issue douanière et ses réserves | BC-073 | 6 |
| Demander facture ou avoir sur éléments éligibles | BC-074 | 7 |
| Reconnaître facture avoir rejet ou correction | BC-074 | 7 |
| Demander encaissement ou remboursement autorisé | BC-075 | 6 |
| Reconnaître paiement partiel échec ou correction | BC-075 | 7 |
| Autoriser la clôture partielle avec reste expliqué | BC-057, BC-059, BC-060, BC-061, BC-062, BC-063, BC-064, BC-065, BC-066, BC-067, BC-068, BC-069, BC-070, BC-071, BC-072, BC-073, BC-074, BC-075 | 7 |

## Financements et bornes des six autres lots

### Master Data Java/Spring

Six capacités locales reçues, ingestion, cohérence, versions et consultation. Source produit, assortiment commercial et prix externes. Pas de PIM/PLM ni de MDM collaboratif d’entreprise. Les contextes opérationnels et bascules saisonnières sont chiffrés dans contrôles.

### Stock Java/Spring

Registre, faits, filiation, positions, comptage et réservations individuelles dans une base transactionnelle. Les consommations des droits collectifs sont financées par le service propre aux contrôles. Les contenus annoncés/constatés sont interprétés par prestations avant remise des faits à Stock.

### Propriété du stock Java/Spring

Trois catégories de déclencheur déjà prévues, conditions d’accord référencées, registres, corrections et preuve. Les engagements entre sociétés sont dans Orders. Pas de langage libre de clauses juridiques ou de moteur comptable.

### Process Management avec studios, portail, formulaires et pilotage

Catalogue d’actions borné, studio, formulaires, tâches, journal, supervision et analyses. Migration uniquement autorisée et compatible avec les engagements, sans rejeu d’effet déjà acquis. Intervention constatée sur résultat. L’approbation, les minuteurs et la reprise utilisent les composants déjà financés.

### Ateliers visuels de planification et de décision

Trois compositions visuelles : carnet/plan, comparaison des possibilités, prestations/transport. Grilles, filtres, liens, choix et résultat reconnu. Pas de nouveau calculateur ni d’éditeur universel de dashboards ou d’interfaces métier. Les cinq CFP de sauvegarde ne valident toujours pas les 160 JH de composition.

### Administration, robustesse et services IT complémentaires

Mécanismes techniques mutualisés et six lots de consoles/adaptations déjà dimensionnés. Une région transactionnelle, cible de disponibilité 99,9 %, rétablissement 8 h et perte cible 4 h repris des hypothèses S1, lot de 100 000 lignes en 30 min pour qualification des données. Aucun multi-région actif ou langage de code libre.

## Traitement des quatorze écarts

| Écart | Traitement dans la proposition |
| --- | --- |
| R01 Gouvernance des politiques | supply-controls-java-spring |
| R02 Consommation des enveloppes de stock par groupe | supply-controls-java-spring, stock-java-spring |
| R03 Arbitrage collectif du carnet et stabilité des affectations | supply-decisions-java-spring, master-plan-java-spring |
| R04 Promesse cohérente et faisabilité à capacité finie | supply-decisions-java-spring |
| R05 Optimisation multi-échelon et recommandations de règles | supply-decisions-java-spring |
| R06 Chargements et tournées sous contraintes | supply-decisions-java-spring, service-fulfilment-java-spring |
| R07 Plans et passage du planifié au ferme | master-plan-java-spring, orders-java-spring |
| R08 Engagements entre sociétés et variantes de commandes | orders-java-spring, inventory-ownership-java-spring, process-management-java-spring |
| R09 Unités logistiques et filiation des biens | service-fulfilment-java-spring, stock-java-spring |
| R10 Devenir des biens et récupération de valeur | supply-controls-java-spring |
| R11 Parcours engagés et interventions sans double effet | process-management-java-spring |
| R12 Ateliers visuels métier | supply-workbenches-java-spring |
| R13 Services financiers et frontières des systèmes externes | service-fulfilment-java-spring, orders-java-spring |
| R14 Spécialisation Fashion et garanties communes | master-data-java-spring, supply-controls-java-spring, professional-it-java-spring |

Les critères d’acceptation du précédent audit restent à vérifier sur les livraisons. Leur rattachement et le choix de financement sont explicités dans [closure.json](closure.json). Pour les ateliers et les garanties communes, conserver un montant sous ces hypothèses ne démontre pas encore qu’il suffira.

## Sensibilité et travail restant

À périmètre constant, modifier uniquement le rendement des cinq lots recomptés donne 15 h/CFP : 6420 JH pour le Core, 20 h/CFP : 7030 JH pour le Core, 25 h/CFP : 7660 JH pour le Core. Il ne s’agit pas d’un intervalle de confiance.

- Le rendement de 20 h/CFP demeure non calibré sur FLOW. Une sensibilité 15/25 h donne l’effet mécanique, pas une confiance statistique.
- Le nombre de variantes métier, les règles autorisées et les contrats externes doivent être confrontés à un premier lot réalisé. Les modèles de décisions ne garantissent pas un optimum global.
- Les temps de réponse et volumes des calculs du carnet, des capacités et des transports doivent être mesurés. Les cibles techniques S1 ne constituent pas une preuve de performance.
- Les règles et interfaces spécifiques des marques, les référentiels sources et les services contractuels propres au Groupe relèvent de l’intégration.
- Un changement de calendrier, de maintenance ou de durée de l’Office FLOW après adoption exige un recalcul économique distinct. Ces impacts ne sont pas chiffrés dans le coût de construction proposé.

La construction des outils de configuration et des contrats génériques est dans le Core. Le paramétrage des politiques réelles, les interfaces et les adaptations propres aux sociétés du Groupe restent dans l’intégration. Les fonctionnalités des produits Microsoft et SAP et leur inclusion contractuelle doivent être examinées séparément. Ces JH Make ne sont pas appliqués aux deux options Buy.

## Preuves et reproduction

- [Synthèse calculée et prix](summary.json).
- [Rattachement des écarts et bornes](closure.json).
- [Script de préparation](prepare.py).
- [Audit des 88 capacités et scénarios](../2026-11-02-revue-perimetre-scenarios/audit.md).

Les fichiers `scope-*.json` portent les besoins proposés. Les cinq preuves par unité conservent les échanges E/R/W/X, les processus remplacés et les empreintes des entrées. Reproduction : `python audits/2026-11-02-proposition-perimetre-complete/prepare.py`. La projection de la page recompte les mêmes mouvements, contrôle la base et valorise avec les prix courants, sans adopter la proposition.
