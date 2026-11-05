# Audit du modèle métier, des calculs et de la logique

Date : 5 novembre 2026. Modèle examiné : révision 13. Audit local, sans publication distante.

## Conclusion

Les contrôles arithmétiques effectués ne font apparaître aucun écart dans les charges retenues du Core, leur valorisation, les annuités et les cumuls des options. Les défauts de validation repérés dans l’organisation ont été corrigés sans changer les budgets ni les hypothèses économiques.

**La charge d’intégration reste à reprendre. À la demande du porteur de l’étude, ses jours sont exclus de la ventilation et de ses totaux.** Les anciens calculs et financements sont conservés pour la traçabilité. Leur présence dans le moteur ne valide ni leur dimensionnement ni leur répartition entre équipes.

L’organisation cible constitue une proposition cohérente de responsabilités durables. Elle ne constitue pas encore un plan de capacité ni une preuve de disponibilité des équipes. Les postes partagés et les travaux restant à affecter sont conservés comme reliquats explicites.

## Périmètre et preuves

L’examen porte sur le métamodèle canonique `source/fondamentaux.yaml#estimation_model`, ses propriétaires d’instances, les contrôles structurels, le moteur de calcul Python et les écrans correspondants.

- Identité et références des unités retenues, rôles, tarifs et coût des lots.
- Unicité des financements, périodes, annuités, natures et responsabilités.
- Cumuls des horizons configurés pour les options actives et historiques conservées.
- Types d’équipes, interactions, affectations, reliquats et conservation des financements.
- Différence entre charge, coût financé et capacité disponible.
- Concordance du métamodèle avec sa représentation graphique et avec l’export téléchargeable.

`avant.json` conserve les contrôles indépendants antérieurs aux corrections. `apres.json` contient leur reprise sur le modèle final. Les conclusions de méthode sont distinctes de ces contrôles arithmétiques.

## Constats et impacts

| Priorité | Constat | Traitement et impact |
| --- | --- | --- |
| Haute | Les jours d’intégration ne sont pas suffisamment instruits et sont récusés par le porteur de l’étude. | Exclusion explicite dans le modèle d’organisation. Aucune affectation ni total de JH d’intégration dans la ventilation. Affichage « Non évalué — étude d’intégration à reprendre ». Coûts existants conservés, sans validation implicite des jours. |
| Haute | Plusieurs lots couvrent plusieurs équipes. Une clé de partage justifiée manque, notamment pour les commandes. | Aucun partage arbitraire entre B2C, Wholesale et Sourcing & Procurement. Les équipes candidates restent des hypothèses de responsabilité, distinctes des affectations. |
| Haute | Le MCO humain n’est pas réparti entre équipes. | Maintien du reliquat annuel. Aucun zéro fictif dans les équipes. Les disponibilités et contributions simultanées Build / intégration / Run restent à dimensionner. |
| Haute | La cible Master Data vise un MDM de référence pour Business Operations, plus large que le périmètre local déjà estimé. | La cible organisationnelle reste visible. Une instruction de périmètre et de financement est nécessaire avant de conclure que le budget actuel la couvre. |
| Moyenne | Le validateur interdisait toute contribution d’une équipe Enabling, même à une activité d’accompagnement. | Correction : l’interdiction concerne la propriété d’un produit logiciel maintenu. Une contribution d’accompagnement devient modélisable. Aucune charge supplémentaire affectée. |
| Moyenne | Une future ligne de financement traversant la frontière Build / intégration aurait été affectée entièrement à la seconde phase. | Rejet de cette entrée ambiguë. Les périodes financées doivent être explicitement séparées. Aucun financement courant ne traversait cette frontière. |
| Moyenne | Une affectation particulière et son alias de financement partagé pouvaient se contredire silencieusement. | Rejet des propriétaires contradictoires. Contrôle des identités d’équipes réservées et des doublons de partition. |
| Moyenne | Les seuls objets d’affectation ne rendaient pas la table de ventilation et ses valeurs explicites dans le modèle exporté. | Ajout de `team_phase_allocation`, de ses relations, de son contrat structurel et de sa table calculée. Les cellules, unités, références sources et valeurs figurent dans l’export. |
| Moyenne | La gouvernance cible et les rôles opérationnels déjà financés sous Transformation Office ne sont pas équivalents. | La gouvernance reste hors typologie Team Topologies. Les moyens financés restent conservés et isolés. Leur rapprochement organisationnel reste à instruire. |

## Cohérence des calculs

La charge du Core System retenue est de **7 630 JH**. Chaque coût de lot est rapproché de la somme des JH par rôle multipliés par leur tarif, augmentée de l’outillage explicitement financé.

Les contrôles indépendants reconstruisent les identités suivantes, avec contrôle des euros au centime et des charges à la précision de calcul :

- Somme des rôles = charge de l’unité.
- Somme des JH × tarifs + outillage = coût retenu de l’unité.
- Annuité = somme des agrégats budgétaires = somme des natures = somme des responsabilités.
- Cumul d’un horizon = somme des annuités correspondantes.
- Équipes + gouvernance + reliquat = total de la phase, pour chaque mesure disponible.
- Cellule de ventilation = somme des postes sources référencés, avec absence de valeur conservée.

Les arrondis de présentation en k€ restent distincts des calculs en euros HT. La table des phases repose sur le calendrier réel des financements. Elle n’est pas une reprise directe des anciens tags budgétaires « obtention », « intégration » et « mco_run ».

### Lecture des coûts conservés

Montants HT exacts pour la référence tarifaire Paris, avant projection temporelle :

| Destination | Build Core System | Intégration Beaumanoir | MCO et évolutions, par an |
| --- | ---: | ---: | ---: |
| Équipes, affectations justifiées | 2 370 400 € | 240 000 € | 96 000 € |
| Gouvernance financée | 3 931 200 € | 2 457 000 € | Non renseigné |
| Travaux et moyens à ventiler | 2 676 390 € | 3 108 865,44 € | 881 562,88 € |
| Total connu | 8 977 990 € | 5 805 865,44 € | 977 562,88 € |

La colonne d’intégration décrit les financements historiques, **sans ventilation de ses jours ni certification de son estimation**. Un coût attaché à des moyens techniques ne produit pas des JH. Les charges brutes et les charges valorisées peuvent avoir des assiettes différentes, notamment par l’application explicite des gains retenus.

La troisième colonne est une **base annuelle complète**, tandis que les deux premières portent sur leurs périodes initiales. Les trois colonnes ne se somment pas sans horizon, calendrier de service et indexation. Les vues Paris et Province reprennent les mêmes charges autorisées et revalorisent les coûts par le moteur existant.

## Table de ventilation du modèle métier

La table `team_phase_allocation` est un résultat calculé du modèle. Elle contient une cellule par phase et destination, soit les équipes produit, la gouvernance ou le reliquat non affecté. Elle comporte les références d’option et de zone tarifaire, les JH autorisés, les euros HT, la base de période et les identifiants des postes sources.

Les règles et les instances d’affectation restent respectivement dans le métamodèle canonique et `source/organisation-delivery.yaml`. Les valeurs sont produites par `tools/delivery_organisation.py`, contrôlées par `source/schema-ventilation-equipes.yaml`, affichées dans « Comprendre les coûts » et « Coûts par équipe et par phase », et exportées dans `derived.team_phase_allocation` avec les postes qui permettent de les retracer.

Une valeur absente reste `null`. Une cellule sans affectation justifiée n’est pas un zéro. Pour l’intégration, tous les JH de la table et de son total restent absents. Les euros ne sont ni recalculés à partir de ces JH exclus ni complétés automatiquement.

## Schéma interactif du framework

React Flow est retenu pour la navigation dans un modèle riche. La version utilisée reprend celle du projet Beaumanoir Cartographie, avec ELK pour le placement automatique. L’application charge ces composants à l’ouverture de la page « Modèle et relations », dans « Framework et méthodes ».

Les vues permettent d’explorer la chaîne d’évaluation, les charges, les financements, les concepts d’organisation, les interactions des équipes, les règles et leurs implémentations, puis le métamodèle complet. Le détail d’un objet présente ses attributs, son propriétaire et ses relations. Recherche, voisinage et filtre d’étape limitent la densité. Une liste textuelle conserve l’accès au clavier et à l’impression.

Les objets et relations viennent directement du métamodèle. Les interactions d’équipes viennent du modèle d’organisation avec ses couleurs Team Topologies. Les flèches de gouvernance non documentées ne sont pas inventées. Les règles affichent leur implémentation déclarée sans assimiler ce lien à une validation de méthode.

Références techniques : [React Flow](https://reactflow.dev/api-reference/react-flow), [commandes de navigation](https://reactflow.dev/api-reference/components/controls) et [accessibilité](https://reactflow.dev/learn/advanced-use/accessibility), consultées le 5 novembre 2026. Le choix repose aussi sur l’examen local des composants du projet Beaumanoir Cartographie.

## Travaux restant à instruire

1. Reprendre l’estimation de l’intégration avec ses activités, livrables, périmètres et preuves. Adopter cette base avant toute ventilation de JH.
2. Rapprocher les lots communs de leurs contributeurs et propriétaires durables, avec des clés de partage justifiées.
3. Répartir les travaux annuels entre produit générique, adaptations client et moyens transverses.
4. Dimensionner la capacité par rôle et période, en tenant compte de la coexistence des évolutions produit, des intégrations et du MCO.
5. Instruire le périmètre MDM cible et clarifier les rôles de gouvernance opérationnelle.

Les tests de calcul ne permettent pas de conclure à la pertinence d’une hypothèse de productivité, à la validité d’une transposition de marché ou à la disponibilité d’une équipe. Les résultats du présent audit portent sur les propriétés effectivement vérifiées.

## Vérifications de livraison

Les preuves finales de contrôles ciblés, de conservation des résultats économiques et de vérification navigateur sont référencées dans `verification.json` à côté de cet audit.

Validation finale : **98 tests Python ciblés, 86 tests JavaScript et 226 contrôles indépendants réussis**. Types TypeScript et règles de contenu validés. Construction statique réussie. Vérification navigateur bureau et mobile, recherche, filtres, inspection, sélection au clavier et variantes tarifaires réussies sans erreur console. La table exportée est identique à la table affichée en référence Paris. La comparaison intégrale des résultats économiques avant et après est identique.
