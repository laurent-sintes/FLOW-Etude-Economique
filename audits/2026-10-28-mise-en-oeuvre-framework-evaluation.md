# Mise en œuvre de l’audit du framework d’évaluation

28 octobre 2026 — Recommandations de l’[audit](2026-10-28-audit-framework-evaluation.md) appliquées dans l’ordre prévu : sécurisation, contrat des sorties de skills, puis traçabilité. Aucune recalibration des chiffres actuels. Aucun commit, push ou instantané publié.

## Résultat par constat

| Constat | Mise en œuvre | Propriétaire principal |
|---|---|---|
| F3 — Contrat Groupe | Rejet des champs inconnus, activités inconnues ou dupliquées, omissions et substitutions incohérentes. Contrôle des références de volumes. | `tools/model_inputs.py` |
| F5 — Normalisation marché | Validation monétaire partagée par le chargement courant et le diagnostic autonome : bornes, devise, change sourcé, période d’indice et assiette. | `tools/analyze_cost_references.py`, `tools/study_app.py` |
| F6 — Sens métier et restitution | Associations structure/notion/nature/Build-Run contrôlées. Part Build du MCO Beaumanoir toujours paramétrable de 0 à 100 %. Descriptifs de substitution contrôlés ; statut d’accompagnement dérivé du traitement exécuté. | `tools/architecture_model.py`, `tools/model_inputs.py`, `tools/study_app.py` |
| F7 — Provenance affichée | Statut unique partagé par les Fondamentaux, la méthode Core et les résultats. Les charges courantes restent clairement des hypothèses historiques, non recalibrées par le nouveau skill. | `source/statut-evaluation.yaml` |
| F8 — Skills et flux courant | Les deux skills installés décrivent les sources courantes, les nouveaux contrats et l’absence d’application économique automatique. Les anciennes consignes brouillon/release et exemples affichés sont retirées. | `flow-evaluer-core-system/SKILL.md`, `flow-etude-marche/SKILL.md` |
| F1 — Sortie du skill Core | Schéma strict, validation, résumé des inconnues et préparation d’un candidat pour relecture. Capacités/fonctions, composants, lots partagés, provenance, auteur, conditions, incertitude et revue sont représentables. Les qualifications marché peuvent être référencées directement, sans double saisie. | `source/evaluation-core.yaml`, `source/schema-evaluation-core.yaml`, `tools/core_qualification.py` |
| F2 — Progression marché | Matrice exhaustive des 84 capacités et six produits, statuts explicites et besoins restant à qualifier. Contrat détaillé avec preuves, différences, inconnues et revue. Restitution compacte dans la page marché. | `source/instruction-marche.yaml`, `source/schema-instruction-marche.yaml`, `tools/market_instruction.py` |
| F4 — Assiette d’expertise | Plafond hérité de 40 JH transféré du programme vers sa source. Le complément est limité aux JH nets N3 financés pour le cloud et la sécurité ; il disparaît si son assiette disparaît. | `source/calibration-couts.yaml#specialisation_maintenance_make`, `tools/calculate_costs.py` |

Les deux compléments de l’audit sont aussi traités : interface React/UX générique explicitée dans le Core, et prix de reconstruction des fiches produit autorisés seulement avec leur contrat de preuve, d’unité, de périmètre et de transposition. Aucun prix inconnu n’a été renseigné.

## Qualification et limites conservées

Le pilote Core porte sur BC-002, BC-003 et BC-004, avec un lot de réception partagé et trois écosystèmes. Il référence les anciennes plages sans les recopier comme nouvelles charges développeur. **Ses 18 efforts restent inconnus et aucune revue humaine n’est inventée.**

Un pilote historique ne peut produire de candidat chiffré. Pour une véritable qualification, le candidat exige des fonctions qualifiées et des efforts retenus et calculables. Il inclut leurs dépendances, conserve les références et empreintes des preuves locales, distingue développement, QA et autres efforts et ne finance un mécanisme partagé qu’une fois. Les types d’effort non représentés sont signalés, jamais convertis en zéro. L’adaptateur prépare une proposition ; il n’écrit pas dans la calibration active.

La matrice marché contient **504 couples capacité/produit**. Chaque produit présente actuellement 59 capacités sans instruction détaillée ou repère d’axe, 25 avec repères documentaires par axe et aucune qualification détaillée engagée dans le nouveau contrat. Cela ne mesure ni absence produit ni couverture fonctionnelle. Aucune transposition de prix vers FLOW n’a été inventée.

Le supplément cloud/sécurité reste une hypothèse héritée non observée. Sa nouvelle assiette est :

`JH spécialisés = min(plafond hérité × facteur de sensibilité JH, somme des JH nets N3 financés dans MAI-007 et MAI-008)`

`Complément = JH spécialisés × max(0, tarif architecte − tarif support N3)`

Cette formalisation n’affirme aucune répartition empirique de ces journées entre les deux activités. Elle n’ajoute ni JH ni outillage.

L’agrégation monétaire Build/Run et la charge totale projet complète restent les limites précédemment annoncées. Elles n’ont pas été introduites implicitement dans cette intervention.

## Vérifications

- **215 tests Python réussis** dans la suite complète, avec tests HTTP locaux.
- Tests JavaScript, compilation TypeScript, contrôle des contenus et build réussis.
- **Six simulations témoins préservées exactement** : référence, absence/renforcement d’indexation, budgets personnels, calendriers personnels et moyens personnels. Elles couvrent les cinq options, les horizons 3/5/7/10 et les annuités.
- **Parité exacte des cinq options, trois sensibilités et quinze annuités** pour le changement d’assiette cloud/sécurité, JH et lignes de coûts compris.
- Gel technique en mémoire et rechargement vérifiés par la suite ; aucun remplacement de `release/current.json`.
- Deux skills installés validés ; essai indépendant d’utilisation. Cet essai a permis de compléter l’auteur de la charge et la référence directe Core → qualification marché.
- Vérification navigateur isolé : pages marché, Fondamentaux et résultats Core, ouverture/fermeture des documents, affichage 1440 px et 390 px sans débordement horizontal de page. Les tables gardent leur défilement propre. Seule remarque hors contenu : requête automatique de favicon absente (404).
- Serveur local actualisé sur le même port 8766, sans accès au stockage des simulations personnelles.

Témoins de cette opération : `tmp/framework-audit-parity.json`, `tmp/audit-f4-before.json`, `tmp/audit-f4-parity.json`, `tmp/check-model-last.json`, `tmp/framework-browser-verification.json`. Captures : `output/framework-audit-marche.png`, `output/framework-audit-modele.png`, `output/framework-audit-mobile.png`.

**Les contrats et contrôles sont maintenant en place pour instruire les évaluations sans les confondre avec les hypothèses actives. La qualification empirique et toute recalibration restent des travaux distincts.**
