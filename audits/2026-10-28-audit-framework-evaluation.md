# Audit de complétude et de cohérence du framework d’évaluation FLOW

Audit du 28 octobre 2026, sur les sources courantes du projet et les deux skills installés.

**Le framework est cohérent dans ses concepts et ses principaux calculs, mais la chaîne de qualification et d’estimation promise par les skills n’est pas encore complète.** Il permet de comparer les hypothèses économiques actuelles. Il ne permet pas encore d’attribuer à chaque JH une chaîne structurée et vérifiable allant de la fonction observée au lot estimé, ni de présenter les coûts comme intégralement calibrés par le marché.

Les priorités sont de **raccorder les résultats des skills au modèle de données** et de renforcer les contrôles avant d’automatiser leur intégration. Les constats ci-dessous ne démontrent pas une erreur des montants actuels. Ils identifient des lacunes de traçabilité et des configurations incohérentes que les contrôles acceptent.

## Périmètre et niveau de complétude

L’audit couvre le glossaire, les Fondamentaux, l’architecture, les quatre méthodes documentées, les paramètres, les skills Core System et marché, leurs propriétaires de données et les traitements de calcul concernés. Il porte sur la cohérence interne et la traçabilité de l’estimation. Les tarifs fournisseur et la réalité fonctionnelle des produits n’ont pas été réévalués auprès de sources externes.

| Élément | État constaté | Limite déterminante |
|---|---|---|
| Modèle métier | Concepts principaux présents et cohérents | Quelques relations sémantiques ne sont pas protégées par les validateurs. |
| Estimation du Core par le skill | Méthode documentée, source partagée avec la page | Sortie détaillée encore sans contrat de données ni adaptateur complet vers le moteur actif. |
| Calcul du brut au budget | Calcul exécuté et assiettes explicites | La base active couvre plusieurs natures, dont la qualification ; elle n’est pas la nouvelle sortie purement développeur du skill. |
| Fonctionnement et lecture Run | Activités, moyens, contrats et annuités calculés | Calibration externe partielle ; agrégation monétaire Build/Run volontairement différée. |
| Étude de marché | Six fiches, six axes communs, quinze références de projets | Instruction fonctionnelle sélective et aucune transposition de projet au périmètre FLOW établie. |
| Paramètres | Valeurs de référence, formules et diagnostics distingués | Une indication de remplacement peut diverger du traitement exécuté si son descriptif est modifié. |
| Skills | Responsabilités bien séparées, règles de preuve explicites | Consignes opératoires partiellement antérieures au flux de travail courant. |

Le référentiel de calibration rattache **88 capacités à 36 modèles de lots**, déclinés selon les trois Make. Les six axes des fiches de marché référencent **25 capacités distinctes sur les 84 du périmètre comparatif déclaré**. Les 59 autres ne figurent pas dans cette grille commune : cela ne signifie ni absence produit, ni absence de toute preuve ailleurs. Ce décompte mesure l’instruction représentée, **pas un taux de couverture fonctionnelle**. [Périmètre comparatif](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/references-couts-integration.yaml:94>) ; [axes communs](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/references-couts-integration.yaml:226>).

## Constats prioritaires

P1 désigne un prérequis à l’application complète de la nouvelle méthode. P2 désigne une lacune de fiabilité ou de traçabilité à corriger avant d’étendre l’automatisation. P3 désigne un alignement documentaire ou de représentation.

### F1 Le contrat de sortie du skill Core reste à construire

**P1 — Complétude opérationnelle.** La méthode demande des fonctions identifiées, des lots par écosystème, une origine de charge, des preuves ou hypothèses, des conditions de réalisation et une incertitude justifiée. Le contrat actif enregistre des descriptions de travail et trois vecteurs de six charges, avec des références de couverture et de travaux. Il ne porte pas les objets et relations nécessaires à toute cette chaîne.

Deux essais sur une copie confirment cette frontière : ajouter une provenance structurée au lot est refusé comme champ inconnu ; une charge inconnue est refusée, car le vecteur impose des nombres. **Le moteur peut recevoir une estimation complète, mais le modèle ne sait pas encore conserver tout son processus de qualification.** La notice de la méthode reconnaît que les charges actives n’ont pas été recalibrées par ce skill.

Prévoir un contrat d’instruction reliant capacité, fonction observée, composant réutilisable, lot propriétaire, estimation et preuve. L’inconnu doit être représentable pendant la qualification ; seules les estimations explicitement retenues et calculables doivent entrer dans le calcul. L’adaptateur doit préserver la distinction entre JH développeur et autres efforts, sans convertir une inconnue en zéro.

Preuves : [exigences de provenance](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-evaluation-core.yaml:119>), [chaîne de consolidation](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-evaluation-core.yaml:145>), [contrat des lots](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/schema-recalibration-metier.yaml:79>), [adaptateur actuel](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/business_calibration.py:69>), [statut d’application](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-evaluation-core.yaml:14>).

### F2 La complétude de l’instruction marché ne peut pas être démontrée

**P2 — Couverture des preuves.** Les contrôles vérifient que les capacités citées appartiennent au périmètre, mais pas que chaque capacité ou fonction possède une observation ou un statut explicite « non étudié ». Les quinze références de projets comportent douze prix normalisés et **aucune transposition établie vers FLOW**. La normalisation ne constitue donc pas une validation indépendante du budget d’intégration.

Créer une matrice de progression de l’instruction, avec capacité, fonction, produit, preuve, différences, statut et inconnues. Pour les charges et les services, distinguer référence observée, analogie et hypothèse d’ingénierie. La complétude du dossier doit être contrôlée séparément de la confiance dans les produits et les prix.

Preuves : [contrôle des axes](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/market_oss.py:193>), [transpositions et éligibilité](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/references-couts-integration.yaml:1158>), [statut de l’étude de marché](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-evaluation-marche.yaml:12>).

### F3 Le contrat Groupe laisse passer des entrées silencieusement ignorées

**P2 — Robustesse du calcul.** La validation des activités conservées vérifie leur séparation d’avec les activités retirées, sans contrôler leur appartenance au catalogue. Le calcul filtre ensuite les lignes selon cette liste. Certains champs inconnus de scénario sont également acceptés.

**Essai sur copie :** remplacer `INT-001` par `INT-999` est accepté et retire environ **55 k€** du financement Java central, sans signalement. Le montant exact de l’essai est de 55 242 €. Aucune activité actuelle erronée n’a été identifiée.

Fermer le contrat des champs exécutables, contrôler toutes les références contre leurs catalogues et rejeter les identifiants inconnus ou les substitutions incomplètes. Ajouter les tests de rejet correspondants.

Preuves : [validation du Groupe](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/model_inputs.py:64>), [listes de substitution](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/model_inputs.py:81>), [filtre de financement](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/composable_costs.py:117>).

### F4 Le complément cloud et sécurité repose sur une assiette non rattachée

**P2 — Traçabilité d’une hypothèse.** Le moteur revalorise **40 JH codés dans le programme**, présentés comme déjà comptés, à partir de l’écart entre tarifs architecte et support N3. Des charges fixes de 40 JH existent dans les activités annuelles, mais aucun lien ne désigne les journées et profils précisément concernés par ce supplément.

**Essai sur copie :** ramener toutes les charges annuelles concernées à zéro laisse **14 k€** de prestations estimées pour Java. Cela démontre l’absence de rattachement du supplément aux charges sous-jacentes, sans établir que le financement courant est injustifié.

Donner à cette assiette un propriétaire dans les sources, la rattacher aux activités et profils concernés, puis vérifier qu’elle ne dépasse pas les journées déjà financées et qu’elle suit leur variation.

Preuve : [complément de tarif cloud et sécurité](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/calculate_costs.py:189>).

### F5 Le contrôle des normalisations marché reste extérieur au parcours principal

**P2 — Couverture des contrôles.** Le contrôle dédié recalcule les montants normalisés, mais le chargement de l’étude ne l’appelle pas. Le test général de lecture marché contrôle les preuves et observations, sans effectuer cette vérification monétaire.

**Essai sur copie :** augmenter une borne normalisée de 12 345 € est accepté par le chargement de l’étude, mais rejeté par le contrôle dédié. Les valeurs actuelles passent ce dernier. Ce défaut concerne la fiabilité des références documentaires ; ces montants ne deviennent pas directement des budgets actifs.

Extraire une validation réutilisable de la normalisation et de ses unités, puis la raccorder au chargement ou au contrôle commun des contenus. Conserver l’analyse exploratoire séparée.

Preuves : [normalisation contrôlée](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/analyze_cost_references.py:70>), [chargement marché](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/study_app.py:198>), [test actuel de lecture](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/test_study_app.py:105>).

### F6 Les références sont contrôlées plus fortement que leur sens métier

**P2 — Cohérence entre modèle et restitution.** Les contrôles d’architecture protègent l’existence, l’unicité et l’exhaustivité des natures, mais pas toutes les conventions d’association.

**Essais sur copies :** classer `core_care` en Run, ou permuter les natures d’obtention et d’intégration entre leurs structures, passe ces validateurs. Les sources actuelles sont correctement classées.

Un second cas concerne l’accompagnement Make : la page déduit son statut conservé/remplacé de `accompagnement_retire`, alors que ce champ est déclaré descriptif et n’est pas lu par le journal de financement. Passer ce descriptif à faux peut afficher une valeur comme conservée sans la réintroduire dans le budget. **La valeur actuelle est cohérente.**

Ajouter des invariants sur les conventions métier courantes et dériver les statuts économiques du traitement exécuté, ou contrôler explicitement leur concordance. La part Build paramétrable du MCO d’intégration doit rester libre dans son intervalle autorisé.

Preuves : [contrat d’architecture](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/architecture_model.py:46>), [liens économiques](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/architecture_model.py:79>), [statut affiché](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/study_app.py:263>), [statut descriptif du champ](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/README.md:96>).

### F7 Les Fondamentaux peuvent attribuer aux chiffres actuels une provenance future

**P2 — Clarté de la provenance.** La charge brute y est présentée comme « Estimée par le skill ». Cette formulation décrit la méthode cible, mais ne rappelle pas que la base active n’a pas encore été produite selon cette méthode. Les pages suivantes l’indiquent correctement.

Partager un statut d’application entre les Fondamentaux, la méthode et les résultats : méthode définie, données qualifiées, estimation retenue. Dès la première page, distinguer le producteur prévu de la provenance des chiffres courants.

Preuves : [producteur du brut](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/fondamentaux.yaml:176>), [notice de la méthode](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-evaluation-core.yaml:14>), [périmètre du moteur](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-calcul-net.yaml:19>).

### F8 Les consignes des skills doivent être réalignées sur le fonctionnement courant

**P3 — Cohérence opératoire.** Les deux skills emploient encore le couple brouillon/référence publiée, tandis que le projet travaille sur les sources courantes avec un instantané technique facultatif. Ils parlent aussi d’exemples pédagogiques comme s’ils figuraient encore dans les pages. Le guide des commandes contient une phrase affirmant que la référence servie est la release, contradictoire avec son introduction.

Aligner les consignes sur le flux courant, réserver la lecture d’un ancien instantané aux demandes historiques explicites, actualiser le vocabulaire de réutilisation et les descriptions des exemples. Les protections contre les recalibrations implicites doivent rester inchangées.

Preuves : [skill Core](</C:/Users/laure/.codex/skills/flow-evaluer-core-system/SKILL.md:14>), [skill marché](</C:/Users/laure/.codex/skills/flow-etude-marche/SKILL.md:12>), [flux courant](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/README.md:3>), [phrase obsolète](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/README.md:107>).

## Compléments à traiter avec les contrats

L’architecture nomme explicitement un frontend spécifique Beaumanoir, mais pas l’interface React/UX générique déjà financée dans le Core. Ajouter cette précision rendrait la frontière générique/spécifique plus lisible sans déplacer de budget. [couche Applications](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/architecture.yaml:13>) ; [interface commune financée](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/calibration-couts.yaml:45>).

Les fiches produit imposent actuellement des prix observés et transposés inconnus. Une extension de ces champs demandera un contrat conditionnel de preuve, de périmètre et d’unité, plutôt que la suppression simple du verrou. **Les prix de projet peuvent déjà être enregistrés ailleurs dans le registre** ; il ne s’agit pas d’une impossibilité générale de conserver des prix de marché. [contrainte des fiches](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/market_oss.py:309>).

## Points cohérents et limites assumées

- Le glossaire, les relations du modèle et les pages distinguent Make/Buy, Build/Run, phases et natures de coûts.
- Le MCO Core System est Build. Le MCO des adaptations et interfaces Beaumanoir a une part Build de référence de 50 %, avec un complément Run calculé.
- Les huit natures calculées appartiennent aux sept structures de coûts. Le journal alimente annuités et horizons sans créer de nouveaux budgets.
- Les mécanismes examinés de calendrier, réception, stabilisation et répartition aux centimes sont cohérents. Les contrats Buy conservent leurs inclusions et leurs parts inconnues.
- Les deux skills renvoient aux méthodes canoniques, séparent faits et hypothèses, et n’autorisent ni recalibration ni budget automatique à partir d’une observation.
- L’absence d’un skill supplémentaire pour le net ou le Run n’est pas un manque en soi : leurs formules sont exécutées par le moteur.
- L’agrégation monétaire Build/Run différée, la charge totale projet en JH encore incomplète et les exclusions de temps interne ou de transformation globale sont **des limites annoncées**, pas des anomalies supplémentaires. Elles doivent rester visibles dans l’usage des résultats.

## Ordre de traitement proposé

1. **Sécuriser les entrées et la restitution** : F3, F5, F6 et F7, puis réaligner les consignes F8.
2. **Construire le contrat des sorties de skills** : F1, avec un premier cas comprenant un lot partagé, plusieurs capacités et plusieurs écosystèmes. Vérifier provenance, inconnues, absence de double compte et distinction développeur/autres efforts.
3. **Étendre l’instruction et la traçabilité** : F2 et F4. Chaque nouvelle donnée doit pouvoir être relue avant de modifier une estimation.
4. **Recalibrer uniquement sur demande explicite**, après validation du contrat et des premières évaluations. Conserver les cinq options, les horizons et les simulations compatibles.

## Contrôles et portée du verdict

Pendant cet audit, le contrôle rapide a réussi **25 tests** avec le témoin de parité des simulations. Le contrôle dédié du marché confirme quinze références, douze normalisations et aucune transposition FLOW éligible. Le dernier contrôle complet du candidat courant, réalisé avant cet audit, avait réussi **174 tests**, ainsi que les contrôles JavaScript, TypeScript, contenus et build.

Les essais négatifs décrits plus haut ont été réalisés sur des copies en mémoire. Ils documentent les frontières des contrats et les incohérences que les contrôles actuels ne rejettent pas, sans modifier les sources. Aucun prix, charge, scénario, skill ni calcul de production n’a été changé.

**Verdict : cohérence conceptuelle satisfaisante, calcul déterministe opérationnel sur les hypothèses courantes, complétude des preuves et des contrats de qualification encore insuffisante pour une évaluation entièrement traçable de bout en bout.** Les tests attestent des invariants vérifiés ; ils ne démontrent pas à eux seuls la justesse des hypothèses de charge, de productivité ou de prix.

