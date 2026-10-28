# Refonte des Fondamentaux du modèle

Le 28 octobre 2026, mise en œuvre des recommandations validées de l’audit de la première page du Framework d’évaluation. La précision ultérieure de l’utilisateur est appliquée : **aucune zone à déplier**.

La page présente six chapitres en lecture continue, précédés d’un sommaire vertical accessible au clavier. Chaque chapitre commence par un message clé en gras. Les définitions canoniques restent consultables par les termes du glossaire.

- Objet et périmètre commun : programme, Core System et plateforme Beaumanoir, avec cartographie visible et frontières explicites.
- Entrants Make et Buy : travaux à construire et patrimoine réutilisable en Make ; étude Synvance, offres, questionnaires et projection COPIL en Buy. La cartographie sert à confronter les deux démarches au besoin. Les écarts de périmètre des offres restent visibles.
- Build et Run : nature des activités, convention MCO du Core et répartition paramétrable du MCO Beaumanoir.
- Brut, net et total projet : même périmètre de travaux entre brut et net, autres efforts humains dans le total, limites de complétude et provenance actuelle conservées.
- Sept postes de coût : présentation en lignes, tags et couches concernées directement visibles. Les inclusions Buy et les parts inconnues sont explicites.
- Calendrier : trois phases et leurs déclencheurs, sans répétition de l’inventaire des postes. L’autonomie Make et les durées Buy documentées sont conservées.

Les deux liens de consultation ouvrent les documents Synvance et les écarts de périmètre dans le lecteur documentaire. Leurs anciennes redirections vers une preuve générique ont été retirées. Le sommaire conserve la route de page et transfère le focus au titre rejoint.

Les contenus courts sont portés par `source/fondamentaux.yaml`, validés par son schéma et compilés dans `model_reading`. Le résumé de provenance demeure dans `source/statut-evaluation.yaml`. Les valeurs de répartition Build/Run proviennent de la structure existante ; aucune valeur économique n’est recopiée dans la prose.

## Conservation des résultats

Témoin préalable : `audits/2026-10-28-fondamentaux-parite.json`.

La suite complète avec `--preserve` réussit : **216 tests Python**, tests JavaScript de simulation et de reprise, TypeScript, contrôle des contenus et build. **Six scénarios** conservent exactement leurs résultats et le sens des paramètres : cinq options, horizons 3/5/7/10 ans et quinze annuités. Le candidat figé en mémoire conserve également cette parité.

La commande n’utilise pas `--publish`. Aucun instantané publié, commit ou push. Les sauvegardes personnelles du navigateur n’ont pas été ouvertes ou modifiées par la vérification.

## Contrôle du rendu

Vérification dans un navigateur isolé à 1 440 × 1 050 px et 390 × 844 px : six entrées de sommaire, six chapitres, sept postes, navigation clavier, ouverture du document Synvance et retour du focus, impression, absence de `details` et `summary`, absence de débordement horizontal et d’erreur JavaScript. Une seconde relecture visuelle n’a relevé aucun défaut bloquant.

Le contenu affiché passe de 1 843 à 1 501 mots sur ordinateur. La page conserve tous ses contenus principaux visibles ; l’augmentation de l’espacement et de la lisibilité n’est pas mesurée par une réduction systématique de sa hauteur. La hauteur mobile passe de 10 039 à 9 343 px.

Pièces : `tmp/verification-fondamentaux-rendu.json`, captures `output/fondamentaux-desktop-*.png` et `output/fondamentaux-mobile-*.png`. Le serveur local est actualisé sur le port habituel 8766.
