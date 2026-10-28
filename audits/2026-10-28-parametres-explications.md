# Contrôle des explications des paramètres

Le contrôle porte sur la page « Paramètres du modèle » et les 14 champs modifiables de « Simuler ». Chaque valeur affichée dans la page Méthode doit indiquer son unité, son effet sur le calcul et l'origine de sa valeur par défaut. Les précisions longues restent dans des sections dépliables ; aucun lien « Voir la source » n'est ajouté à cette page.

| Famille | Valeurs contrôlées | Effet et méthode visibles |
|---|---|---|
| Inflation | 3 taux annuels | Effet sur prix unitaires, méthode et limites par catégorie. |
| Tarifs humains | Expert, QA et architecte pour chacune des 5 options ; interface Make et support N1 communs | Activités financées, tarif applicable, justification et limites. L'intégrateur de flux réemploie le tarif expert ; il n'a pas de prix autonome. |
| Pilotage | 4 taux de phase, coordination des déploiements, ETP et tarifs du programme central | Assiette propre à chaque taux et justification. Le programme Make est l'exception calculée en ETP, explicitement séparée. |
| JH et productivité | Règle de charge, gains de construction, d'intégration et par activité annuelle | Formule, activité concernée, exclusions, statut d'hypothèse et taux détaillés. |
| Moyens techniques et provisions | 12 valeurs unitaires ou annuelles de `couts_communs` utilisées par la référence | Libellé, unité, effet et justification de la provision dans une section dépliable. |
| Simulations personnelles | 4 paramètres communs et 10 paramètres par option | Chaque champ dispose d'un texte d'aide et d'une référence ; les valeurs par défaut viennent du modèle chargé, sans recopie économique dans l'interface. |

Les JH par capacité, le mix de rôles détaillé, les volumes annuels et les séquences contractuelles sont des **entrées de travaux ou d'offres**, pas des coefficients globaux de cette page. Ils restent dans leurs sources propriétaires et dans les lectures de l'étude. La page ne doit pas devenir une copie de la cartographie ou de tous les postes de dépense.

Deux limites demeurent explicites : les cinq tarifs QA/architecte sont des hypothèses de cadrage, sans cinq cotations strictement comparables ; les taux de gains de productivité ne sont pas mesurés sur FLOW. Une nouvelle valeur de ces familles demande une source ou une mesure et une réconciliation économique des cinq options et des horizons 3/5/7/10 ans.
