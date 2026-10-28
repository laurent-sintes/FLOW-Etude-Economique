# Revue ciblée des gains de productivité

## Ce que fait le calcul courant

Le modèle estime d'abord des journées de travail (JH) après réemploi. Il réduit ensuite les JH des travaux concernés selon un taux d'hypothèse, puis valorise les JH restants. Le taux ne réduit ni le tarif journalier ni les prix des offres Buy. L'expertise transverse d'intégration n'est pas réduite. Les activités annuelles de maintenance portent leurs propres taux.

- Construction du Core System et compléments : `source/calibration-couts.yaml#ia.taux_pct`, appliqué dans `tools/calculate_costs.py` à chaque nature de travail.
- Interface commune Make : `source/calibration-couts.yaml#ia.frontend_pct`.
- Intégration : `source/calibration-couts.yaml#ia.integration_pct`, hors expertise transverse.
- Maintenance : `source/chiffrage/chiffrage-*.yaml#gain_ia_pct`, par activité.

Ces taux sont des hypothèses d'ingénierie. La source ne contient pas de mesure de productivité sur les travaux FLOW. Les différences entre technologies sont motivées qualitativement, sans observation locale permettant de les calibrer.

## Limite de la sensibilité existante

Le scénario haut annule les gains, mais augmente aussi les JH et certains achats et utilise ses propres hypothèses de prix. Sa différence avec le scénario central ne mesure donc pas l'effet isolé des gains de productivité.

## Décision pour cette correction d'interface

La page « Paramètres du modèle » explique le mécanisme, signale le statut d'hypothèse et rend les taux détaillés consultables. Aucun taux ni montant économique n'est modifié sans base de recalibration. Pour consolider le Go / No Go, la prochaine revue économique devrait comparer, à paramètres identiques, la référence actuelle à un scénario où seuls ces gains sont mis à zéro, puis confronter les taux à quelques travaux représentatifs mesurés. Ce test doit réconcilier les cinq options et les horizons 3/5/7/10 ans avant toute nouvelle publication économique.

Le tarif de support utilisateur N1 vaut actuellement 425 € HT/JH dans les cinq fiches technologiques, avec la même justification et la même preuve. La page le présente une seule fois, indépendamment des options. Le calcul reste identique ; le support éditeur inclus dans une offre Buy garde son traitement distinct. Une future refactorisation des sources pourra placer ce tarif commun sous un seul propriétaire et en dériver les cinq usages.
