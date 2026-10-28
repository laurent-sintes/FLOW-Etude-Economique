# Harmonisation du framework en lecture continue

Le 28 octobre 2026, les cinq pages suivant les Fondamentaux et les six fiches marché ont été vérifiées et harmonisées. **Aucun accordéon ni bloc à déplier ne subsiste dans ce parcours.** La préférence est inscrite dans les consignes du projet et dans le guide de l’application.

Les trois pages de méthode Core, de calcul du budget Build et de calcul du Run ne comportaient déjà aucun accordéon. Leurs sommaires, titres, paragraphes, formules et espacements reprennent désormais les repères des Fondamentaux. Les sommaires verticaux précèdent les introductions et restent utilisables au clavier.

La page Paramètres présentait 55 blocs à déplier, en comptant leurs répétitions par option. Ses six familles sont maintenant entièrement visibles. Les tarifs sont réunis dans un tableau des quatre profils et des cinq options ; les taux de coordination disposent d’un tableau avec leurs assiettes. Les méthodes identiques sont regroupées avec les options auxquelles elles s’appliquent. Les limites et repères diagnostiques restent explicites.

Les six axes de la page Marché et les axes des six fiches produits sont affichés directement. Le relevé et le calcul COCOMO ERPNext sont visibles dans sa fiche. Le sommaire Marché donne aussi accès aux axes, à la progression de l’instruction et aux fiches. Les onglets de sélection des produits, les pièces documentaires et leurs retours de focus sont conservés.

## Contrôles de conservation

- Nouveau témoin préalable : `audits/2026-10-28-framework-continu-parite.json`.
- Les six scénarios conservent exactement leurs résultats pour les cinq options, les horizons 3/5/7/10 ans et les quinze annuités. Le contrat des simulations est identique.
- Les 2 892 chemins numériques du bootstrap sont inchangés. Les données des paramètres, du marché, de l’évaluation Core et la référence sont identiques.
- Toutes les formules et les 18 tableaux préexistants sont conservés cellule par cellule. Les deux nouveaux tableaux reprennent correctement 20 tarifs et 5 taux.
- Les 49 textes de méthode, d’assiette, de justification et de limite recensés dans les données des paramètres restent présents. Les nombres des six fiches marché sont identiques avant et après.
- `check_model --full --preserve audits/2026-10-28-framework-continu-parite.json` réussit : 216 tests Python, tests JavaScript de sauvegarde et de reprise, TypeScript, contenu et build.

La suite n’a pas utilisé `--publish`. Aucun commit ni push. Les simulations personnelles du navigateur n’ont pas été ouvertes ou modifiées.

## Contrôles de présentation

Vérification sur ordinateur 1 440 × 1 050 px et mobile 390 × 844 px : zéro `details` ou `summary`, aucun débordement horizontal de page, aucun marqueur de gras affiché brut, aucune erreur JavaScript. Tous les liens des sommaires transfèrent le focus au titre attendu sans changer de page. Les tableaux larges sont défilables au clavier. Les six onglets produit et le retour de focus à la fermeture du lecteur marché fonctionnent.

Les titres des chapitres utilisent les mêmes tailles que les Fondamentaux, 21 px sur ordinateur et 19 px sur mobile ; le corps de lecture est à 14 px. Les formules restent mises en évidence et visibles à l’impression.

Pièces : `tmp/framework-preservation-report.json`, `tmp/framework-parameter-content-check.json`, `tmp/framework-market-numbers-check.json`, `tmp/framework-reading-verification.json` et captures `output/framework-*.png`. Le serveur local est actualisé sur son port habituel 8766.
