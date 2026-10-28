# Étude économique FLOW — contrat de travail courant

## Communication

- Tutoyer l’utilisateur dans les échanges.

## Autorités et finalité

- Étude d’opportunité pour un Go / No Go, sans engagement forfaitaire. Présenter les résultats et partis pris actuels ; les récits de correction restent dans les audits.
- Appuyer autant que possible les hypothèses sur la cartographie métier native : Domaine / Sous-domaine / Business Area / Capacité. Conserver identifiants et preuves. La complexité ordinale ne calcule pas les JH ; chaque mécanisme réutilisé a un propriétaire de financement.
- `source/README.md` définit les propriétaires des données ; `tools/README.md` porte les commandes ; `app/README.md` décrit l’application et `app/BRANDING.md` sa charte. AGENTS porte les règles de travail, sans registre exhaustif ni copie des paramètres.
- Une absence de preuve ne démontre pas une absence produit. Inconnu (`null`), inclus, sans objet et zéro sont distincts. Les prix conservent date, périmètre, régime et séquence.
- Une simplification ne modifie pas chiffres, hypothèses ou contrats de simulation. Une évolution économique autorisée réconcilie cinq options et horizons 3/5/7/10 ans.

## Économie courante

- Core System désigne la plateforme cœur générique : Plateforme Flow construite en Make, solution Microsoft ou SAP achetée en Buy, ou une autre solution. Plateforme Beaumanoir désigne le Core System retenu avec les spécificités du Groupe intégrées ; elle vise à réunir les SI des marques historiques et de Boardriders. Le glossaire est canonique ; `flow_core_system` désigne Plateforme Flow. « Socle technique et cloud » regroupe les moyens techniques dans la présentation, sans fusionner leurs lignes de calcul. Ne pas étendre le périmètre financé au-delà de la cartographie retenue.
- La phase commune est « Obtenir le Core System ». « Build Core System » reste le poste de construction Make. La sélection-contractualisation Buy est financée par `source/selection-buy.yaml` avant intégration ; Synvance passé n’est pas recompté.
- Build Core System finance les travaux génériques des trois Make. Les produits Buy existent déjà ; un supplément exige écart démontré, preuve et financement distinct. Les points Buy ouverts ne créent pas de budget automatique.
- Le calendrier Make est autonome : source unique dans `deploiement-groupe.yaml`, ouvertures explicites et stabilisation locale fixe ; aucune dépendance aux durées Buy.
- L’intégration Make repose sur les activités et déploiements Groupe. SAP retraité et son bonus restent un contrepoint ; ne pas les ajouter à cette base ni leur attribuer son calcul.
- Séparer les trois phases chronologiques des natures de coûts : obtention initiale, intégration initiale, MCO et évolutions du Core System, MCO et évolutions Beaumanoir, Run cloud, exploitation/support/outillage, achats techniques et contrats Buy groupés. Le poste global Core System comprend aussi sa construction ; celle-ci ne relève pas de la nature annuelle. Les parts Buy inconnues restent non ventilées.
- `cost_natures` dérive les mêmes dépenses du journal et des annuités, sans nouveau budget. Le compartiment historique `run` et le paramètre `services_integration` gardent leur sens large pour les simulations ; ne pas les rebaptiser Run cloud. Les champs historiques `phase` sont des agrégats budgétaires, pas des périodes étanches.
- Build/Run est une convention de pilotage portée par le modèle métier, distincte de Make/Buy, des phases et de la récurrence. Le MCO du Core System est Build ; le MCO des adaptations Beaumanoir est Run sauf interventions importantes en projet, selon la clé de répartition paramétrable de sa structure. Les contrats mixtes sans ventilation restent inconnus. Les tags ne permettent jamais de compter deux fois un montant ; ne pas confondre le Run transversal avec la notion historique `run` du glossaire, qui désigne le Run cloud.
- Le Run comprend l’hébergement du build et les moyens consommés en intégration. Le MCO client suit la réception ; la stabilisation préalable reste en intégration. Le régime annuel prend le relais sans chevauchement. Préserver les séquences Buy et le support Microsoft initial non récurrent.
- Un financement compte une fois. Répartir les budgets par différences de cumuls arrondis, en conservant les centimes. Le journal commun alimente annuités, responsabilités, horizons et reste à financer. Aucun calcul économique autonome dans React.
- Une donnée a un propriétaire. Référencer ou dériver ses autres usages ; refuser valeurs écrasées silencieusement, champs inconnus, parts incohérentes et jalons invalides. Aucun ancien score CSF ni ancien chiffrage Core requis.
- Identifier les lignes diagnostiques par `usage_reference` et leur remplacement par `remplacement_ref`. Les anciennes ancres CSF restent dans `source/diagnostics/`, hors calibration active. Les champs descriptifs du calendrier ne sont pas des paramètres exécutables ; voir `source/README.md`.
- Les exports sont des résultats non éditables. Le calcul sponsor consomme les travaux valorisés, une base annuelle Make et les séquences Buy ; le diagnostic historique à quinze ans reste séparé.

## Flux courant et simulations

- Un seul flux de travail (« main stream ») dans `source/` et `config/`, hors résultats générés listés dans le guide du modèle. L’application charge toujours les sources courantes ; aucun mode brouillon/release ni publication à demander pour voir les modifications.
- Après une modification, appliquer les contrôles proportionnés, reconstruire l’interface si nécessaire et actualiser le serveur avec le lanceur courant. Données, textes, paramètres et preuves textuelles sont figés ensemble en mémoire au chargement. Les pièces binaires restent originales et vérifiées par empreinte. `release/current.json` reste un instantané technique facultatif, remplacé atomiquement seulement sur demande explicite ; il ne pilote pas l’application locale.
- Un chargement forme un objet cohérent. Les simulations ne relisent pas les YAML ; modifier les sources ne change pas les sessions chargées. Actualiser le serveur après les contrôles, puis recharger l’application au moment utile.
- Les simulations personnelles sont des paramètres, pas des versions du modèle. Garder clés de stockage, sens des paramètres et adaptateurs existants. Un changement de prix ou de présentation ne rompt pas le contrat.
- La session réapplique ses modifications à la référence ; les scénarios nommés/importés conservent leurs valeurs absolues. Garder les originaux sur erreur ou incompatibilité. Reprise réussie silencieuse.
- La référence reste distincte des hypothèses personnelles. La projection annuelle porte sur quinze ans, indépendamment des horizons de comparaison 3/5/7/10 ans.

## Contrôles proportionnés

- Contrôles ciblés pendant le travail ; une suite complète sur le candidat stabilisé. Ne pas recalibrer après une correction de style ni répéter une suite sans nouveau risque.
- `check_model --quick` contrôle contrats, financements et calendriers ; `--content` les contenus et références courants ; `--full` la suite complète et la reprise (`--release` reste un alias technique compatible). Commandes exactes dans `tools/README.md`.
- Dans le bac à sable Codex sous Windows, l'alias `python.exe` de `WindowsApps` peut être inexécutable. Découvrir le runtime avec `load_workspace_dependencies` puis employer son chemin explicite. Si `PyYAML` ou `jsonschema` manque, installer les versions de `tools/requirements-model.txt` dans `tmp/model-deps` et ajouter ce dossier à `PYTHONPATH` pour les seuls contrôles ; ne pas installer globalement. Sur ce poste, le téléchargement PyPI exige `exec_command` avec `sandbox_permissions=require_escalated`.
- La suite `check_model --full` ouvre un serveur HTTP sur loopback et crée des dossiers temporaires. Dans ce bac à sable, l'exécuter avec `exec_command` et `sandbox_permissions=require_escalated` ; les erreurs `WinError 10013` ou `WinError 5` sur `Temp` signalent une restriction d'exécution, pas un échec du modèle. L'escalade ne vaut pas autorisation de créer un instantané : conserver l'absence de `--publish` sauf demande explicite.
- Les contrôles et le démarrage courant ne dépendent pas de l’ancien instantané. Un moteur modifié se contrôle avec `--full`, sans publication intermédiaire.
- Utiliser `--preserve` et un témoin de simulations pour une refactorisation à chiffres constants. Ce témoin concerne l’opération ; il ne devient pas une contrainte sur les évolutions économiques futures.
- Conserver les contrôles indépendants d’annuités et d’arrondis. Valider données et références, jamais la présence d’une liste de fichiers dans AGENTS.
- Cache borné au chargement, copies isolées, vérification des modifications de sources ; pas de cache global mutable. Tests partageant un chargement avec copies pour les modifications.
- La grille métier est validée une fois par chargement via le mémo isolé existant. Le bootstrap public essentiel ne transporte pas les lectures documentaires ; elles restent intégrales dans la release, accessibles via les preuves et le bootstrap complet compatible. La compression HTTP est négociée, mise en cache avec une borne pour les réponses figées ; ne pas mettre les paramètres personnels en cache global.

## Interface et contenus

- Les entrants et leur traitement restent dans le Framework ; les analyses réalisées, hypothèses retenues et résultats chiffrés vont dans le dossier économique. Synvance et la cartographie restent présentés comme des données d’entrée, avec leur rôle, leur contenu attendu et leur exploitation par la méthode.
- Parcours public : **Framework d’évaluation** (Vue d’ensemble / Fondamentaux du modèle / Méthode de l’étude de marché / Estimation du développement Make / Des charges au budget / Calculer le fonctionnement et sa part Run / Leviers et conventions de calcul), puis **Dossier économique** (Étude de marché / Hypothèses retenues / Évaluations économiques / Comparer / Se projeter / Simuler). Les anciennes routes restent compatibles. La Vue d’ensemble raconte la démarche d’opportunité, ses appuis et leurs limites ; les pages suivantes détaillent les notions, entrants et formules. Brut, net et charge totale projet sont présentés dès les Fondamentaux. La méthode du skill explique uniquement l’estimation des JH développeur bruts ; les pages complémentaires expliquent le budget Build et le fonctionnement annuel avant classement Build/Run. Les limites de l’application courante accompagnent les résultats dans le dossier économique. Ne pas présenter les JH nets développeur ni les budgets en euros comme une charge totale projet complète, ni les postes annuels comme une agrégation analytique Run déjà exécutée.
- Comparer présente les cinq options par phase. Se projeter présente les cumuls par horizon et les annuités. Simuler réunit résultats, paramètres, calendrier et sauvegardes. Structure des coûts place le vocabulaire en tête, puis explique Make/Buy, les postes et les périodes. Complexité présente les trois niveaux ordinals par capacité, leurs justifications et la source native, sans convertir les niveaux en JH. Les justifications proches des chiffres donnent explication, extrait et pièce complète.
- Textes dans les YAML, dont `config/application.yaml#essential`. Les montants viennent du moteur, sans copie économique dans la prose. Une explication détaillée a un emplacement principal.
- Les pages de méthode expliquent la raison d’être, le traitement et le résultat de chaque étape. Afficher les formules de calcul applicables avec leurs unités et assiettes ; distinguer les calculs exécutés des définitions et des éléments restant à dimensionner.
- Les pages du Framework d’évaluation et leurs fiches se lisent en continu, sans accordéon ni bloc à déplier. Utiliser un sommaire vertical, des messages clés en gras, des formules visibles et des sections espacées. Les choix de produit et les liens vers les pièces restent des moyens de consultation distincts.
- Présenter les efforts humains en JH. Les capacités historiques en ETP sont converties dans le moteur de présentation avec la durée et la convention de jours existantes ; conserver leurs identifiants et les contrats de simulation. Les licences, achats et forfaits fournisseur conservent normalement leurs montants en euros. La coordination des travaux techniques est distincte du pilotage du programme ; sa provision actuelle en pourcentage ne devient pas des JH sans dimensionnement explicite du rôle et des missions.
- Rédiger les énumérations en puces plutôt qu'avec des points-virgules. Donner des exemples courts et visibles pour les structures de coût, sans leur attribuer automatiquement un budget.
- Traduire « SCM » par « gestion de la chaîne logistique » dans les textes destinés au lecteur. Conserver les identifiants techniques et les noms officiels des produits tiers.
- Employer « Réutilisation du patrimoine logiciel », ou « réutilisation » en contexte, selon le glossaire. Le patrimoine couvre aussi bibliothèques, frameworks, programmes, automatisations et skills, internes ou tiers. La capitalisation constitue ce patrimoine ; la réutilisation le mobilise. Conserver les clés techniques historiques et les preuves originales.
- Appliquer `app/BRANDING.md`. Budgets en k€ sans décimales, tarifs en € HT / JH, unités près des valeurs ; calculs en euros à leur précision actuelle.
- Préserver contrastes, clavier, cinq options, défilement continu, détails et retours de focus. Animations brèves respectant `prefers-reduced-motion`. La présentation ne change pas l’économie.

## Preuves et ménage

- Conserver les originaux fournisseur, captures métier et registres de preuves, même datés. Une preuve datée n’est pas une ancienne version du modèle.
- Les anciens exports Excel de l’étude sont supprimés à la demande de l’utilisateur ; questionnaires et classeurs reçus comme sources restent conservés. Ne pas régénérer d’Excel sans demande explicite.
- Retirer les doublons après comparaison des octets, les historiques après revue des références. Un nom ancien ou l’absence de mention littérale ne suffisent pas. Protéger runtimes, sessions, preuves et derniers livrables utiles.
- Une demande de ménage autorise les retraits correspondants. Conserver un reçu des chemins, empreintes et motifs ; une sauvegarde ponctuelle de récupération n’est pas un troisième état métier.
- `config/publication.yaml` déclare les documents et preuves de release. Les dépendances économiques restent explicites dans le modèle ; aucun balayage de dossier ne réintroduit automatiquement une ancienne donnée.
- Git et release métier sont distincts. Ne pas supposer qu’un fichier non suivi est récupérable ; aucun commit ou push implicite.

## Git, localisation et GitHub Pages

- Projet actif : `C:/Dev/FLOW-Etude-Economique`, dépôt `https://github.com/laurent-sintes/FLOW-Etude-Economique`, branche courante `main`. Le dépôt complet et l’application Pages sont publics par décision explicite de l’utilisateur. Ne pas appliquer les workflows d’un autre projet FLOW.
- Le skill `skills/flow-economie-git/SKILL.md` distingue commit local, push des commits existants et leur enchaînement. Un push sur `main` déploie le site après contrôles ; aucune release métier ni modification économique implicite.
- GitHub personnel est `github.com` / `laurent-sintes`. Les commandes `gh api` ciblent explicitement `--hostname github.com` ; ne pas utiliser le compte professionnel `beaumanoir.ghe.com` par défaut ni modifier l’identité Git globale.
- Pages livre un ensemble technique figé depuis les sources courantes. Les calculs restent dans le même moteur Python, exécuté via Pyodide ; aucune formule économique parallèle en JavaScript. Préserver erreurs, contrats, stockage et import/export des simulations.
- Vérifier le vrai navigateur statique et la parité avec le moteur Python lorsque le transport ou le calcul change. Les cas de CI sont dérivés des hypothèses courantes ; un témoin historique ne doit pas figer les futures évolutions économiques autorisées.
- `app/dist/` sert l’application locale à la racine ; `app/dist-pages/` sert Pages sous `/FLOW-Etude-Economique/`. Ne pas remplacer l’un par l’autre. Le serveur local se lance depuis `C:/Dev/FLOW-Etude-Economique`, sur le port habituel 8766.
- Les simulations du site et celles de localhost ont des stockages d’origine distincts. Les fichiers personnels restent exportables et importables ; ne jamais vider les sauvegardes pour un déplacement ou un déploiement.
