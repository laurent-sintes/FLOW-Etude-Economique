# Mise en œuvre de l’audit de lecture du Framework

Le 28 octobre 2026, les recommandations de l’[audit global](2026-10-28-audit-lecture-framework.md) ont été appliquées dans l’ordre validé. L’application locale sert les sources courantes et la nouvelle compilation. Aucun commit, push ni remplacement de `release/current.json` n’a été effectué.

## Changements réalisés

| Étape | Résultat |
|---|---|
| 1. Périmètres et affirmations | Méthode cible du skill distinguée de la base de charges active. Programme et capacités financées distingués. Inclusion SAP analytique présentée comme non démontrée. Prix isolés des fiches Buy distingués des prix des offres Synvance. |
| 2. Libellés et formules | Rôles métier repris depuis les catalogues. Durée du pilotage explicitement rattachée à l’intégration Groupe. Assiette de construction initiale, outillage par JH et périmètre du fonctionnement précisés. Deux formules de consolidation Make ajoutées. Plafond et coefficients de l’expertise annuelle exposés depuis leurs propriétaires. |
| 3. Preuves accessibles | Trois accès depuis Marché : produits, projets et prix d’intégration, services de fonctionnement. Les vues présentent 15 projets et 15 références de fonctionnement, dont 15 observations monétaires. Les sources sont nommées et les pièces tarifaires accessibles. Le diagnostic conditionnel Tryton est distingué du registre actif, sans injection de JH. |
| 4. Parcours | Vision → Fondamentaux → Marché → Estimation du développement Make → Des charges au budget → Fonctionnement et part Run → Paramètres. Titres, numérotation et transitions cohérents ; routes existantes conservées. |
| 5. Lecture et lexique | Méthode Marché condensée ; Paramètres organisé en six familles actives puis diagnostics. Possibilités de modification personnelle dérivées du contrat réel de Simuler. Glossaire enrichi et régénéré. Termes métier harmonisés, notamment rôles, MCO, promesse, dossiers, commerce de gros, PNCLOC et statut d’analyse. |
| 6. Vérification | Contrôles ciblés, suite complète, comparaison économique et relecture visuelle sur trois largeurs. Lecture continue sans accordéon ; les lecteurs de sources restent des accès documentaires. |

## Conservation des chiffres et simulations

- Témoin : [six scénarios avant intervention](2026-10-28-lecture-framework-parite.json).
- **35 521 valeurs numériques, booléennes et inconnues préexistantes inchangées** dans le bootstrap complet. Les 16 valeurs ajoutées sont des métadonnées dérivées de lecture, sans nouvel effet économique.
- Résultats de référence identiques, hors identifiant de contenu.
- Six simulations identiques et contrat de simulation inchangé.
- Écart à dix ans : **0 € pour chacune des cinq options**.
- Les sources tarifaires, les taux, volumes, forfaits, horizons et calendriers n’ont pas été recalibrés.
- Le renommage de MAI-003 est purement terminologique. Les empreintes des catalogues et des dépendances de leurs cinq chiffrages ont été synchronisées ; leurs nombres restent identiques. Les exports économiques historiques n’ont pas été régénérés.

Le rapport détaillé de comparaison est dans `tmp/lecture-framework-parity-report.json`.

## Contrôles

La commande `check_model --full --preserve audits/2026-10-28-lecture-framework-parite.json`, sans `--publish`, passe : **231 tests Python**, tests d’interface, TypeScript, contrôle de contenu, build et chargement du candidat autonome. Un premier passage a signalé un libellé non canonique ; il a été remplacé par la notion du glossaire avant le passage complet réussi.

Les sept pages ont été examinées à **1 440, 768 et 390 px** : aucun accordéon de contenu, aucun débordement de page, aucune erreur JavaScript applicative. Les sommaires déplacent le focus vers les titres ; les tableaux larges restent défilables au clavier. Les définitions de glossaire sont des aides ponctuelles, pas des chapitres repliés.

Les six fiches et les deux nouvelles vues documentaires ont été examinées sur ordinateur et mobile : prix, périodes et assiettes identiques aux données chargées ; fermeture Échap, retour de focus, source YAML ciblée et ouverture PDF vérifiés. Les preuves longues restent consultables sans être ajoutées au chargement essentiel de l’application.

Captures et rapports : `tmp/lecture-framework-after/` et `tmp/lecture-framework-market/`. Le serveur local annonce `mode=current` et `sources_current=true` après actualisation.

## Limites conservées et explicitées

La méthode du skill n’a pas recalibré la base historique. Les références de marché ne démontrent pas à elles seules une charge FLOW. Le total humain projet reste incomplet en JH et la comparaison monétaire Build/Run reste à constituer. Ces limites, déjà présentes dans le modèle, sont rendues visibles sans changement de calcul.
