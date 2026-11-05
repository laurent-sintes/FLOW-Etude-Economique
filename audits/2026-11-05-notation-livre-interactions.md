# Notation du livre pour les interactions — 5 novembre 2026

À la demande de l’utilisateur, les interactions suivent désormais les symboles de l’image de référence issue de Team Topologies : zone commune hachurée pour Collaboration, connecteur noir à deux crochets pour X-as-a-Service et zone commune pointillée pour Facilitating.

`InteractionMark` est l’autorité graphique commune. Les exemples pédagogiques montrent deux équipes sous forme de disques orange et bleu. Le schéma React Flow, ses filtres et sa légende reprennent le symbole central sous forme compacte. Les disques des exemples ne désignent pas des types d’équipes. Les types du schéma conservent leurs formes propres.

Les motifs restent distincts en l’absence de couleur. Les définitions et les contrats des relations restent en texte. Les identifiants SVG sont propres à chaque instance, y compris après filtrage et recadrage. Les interactions, phases, critères de sortie, charges et coûts sont conservés.

Cette demande remplace le choix des symboles du kit numérique consigné dans l’audit initial. Les représentations numériques alternatives sont documentées dans la rubrique [Key differences from the shapes in the book](https://github.com/TeamTopologies/Team-Shape-Templates#key-differences-from-the-shapes-in-the-book). Le choix de la notation est graphique et ne modifie pas la révision métier.

## Vérifications

- Contrôle Dev ciblé : 59 tests Python, 86 tests JavaScript, TypeScript et contrôle éditorial réussis en 68,3 s. Rapport : `tmp/validation/20261105T095424Z-86c78503`.
- 27 vérifications Chromium réussies en 3.4 s sur la livraison statique finale. Les 29 marqueurs ouvrent le bon contrat. Les trois modes, le clavier, les identifiants des motifs après filtrage et recadrage, et les vues mobiles sont vérifiés.
- Revue visuelle des exemples à deux disques, des symboles du schéma et de la lecture mobile. Captures dans `tmp/book-interaction-*` et compte rendu dans `tmp/book-notation-browser.json`.
- Livraison locale reconstruite. Révision technique : `8126845238a815d90425f63d145dc532ec5232a0627962fadcaf4ba53d0bb5a6`. Aucune évolution de données économiques ni nouvelle révision métier.

Les contrôles portent sur la présentation et les parcours concernés. Ils ne constituent pas une validation complète du projet ni des hypothèses d’organisation.
