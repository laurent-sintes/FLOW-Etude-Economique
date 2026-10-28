# Modèle FLOW : commandes courantes

Un seul flux de travail : les sources courantes sont dans `source/` et `config/`. L’application locale les charge directement, sans choix de mode ni publication intermédiaire. Les simulations personnelles restent dans le navigateur ; aucune commande ci-dessous ne les efface. `release/current.json` reste un instantané technique facultatif.

## Contrôler

Depuis la racine, dans l’environnement Python du projet :

```powershell
python -m tools.check_model --quick
python -m tools.check_model --content
python -m tools.check_model --full
```

- **quick** : contrats des entrées, volumes dérivés, calendriers, rôles, prix et inclusions Buy, invariants financiers, isolation du modèle et de la release. Un seul chargement partagé, aucune ouverture de port.
- **content** : vérifier les textes et références avec le modèle courant, sans modifier les hypothèses ni les résultats enregistrés. Aucun instantané préalable requis.
- **full** : tous les tests Python, HTTP, JavaScript, formats, navigation, reprise des anciennes simulations, compilation TypeScript, contenu et build de l’application. `--release` reste un alias compatible. Aucun instantané remplacé sans `--publish`.

### Repli Codex Windows / bac à sable

L'alias `python` de `WindowsApps` peut échouer avant même le lancement. Dans Codex, appeler `load_workspace_dependencies` et utiliser le chemin Python retourné à la place de `python` dans les commandes ci-dessus. Sur ce poste, le runtime se trouve dans `C:\Users\laure\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` ; vérifier ce chemin à chaque session. Le runtime embarqué peut ne pas contenir `PyYAML` et `jsonschema`. Les installer de façon isolée dans `tmp/model-deps` avec les versions de `requirements-model.txt`, puis définir `PYTHONPATH` sur ce dossier pour le processus de contrôle. `openpyxl` est déjà présent dans le runtime observé ; vérifier avant installation. Ne pas déplacer les dépendances dans les sources du modèle.

```powershell
$studyPython = 'C:\Users\laure\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' # remplacer par le chemin découvert
& $studyPython -m pip install --disable-pip-version-check --no-cache-dir --target tmp/model-deps -r tools/requirements-model.txt
$env:PYTHONPATH = (Resolve-Path -LiteralPath 'tmp/model-deps').Path
& $studyPython -m tools.check_model --quick
```

Sur ce poste, lancer l'installation isolée depuis PyPI directement avec `exec_command` et `sandbox_permissions="require_escalated"` : la résolution de `pypi.org` est bloquée dans le bac à sable ordinaire. Réutiliser `tmp/model-deps` lorsque les versions attendues y sont déjà présentes.

La suite `--full` doit pouvoir ouvrir son serveur HTTP sur `127.0.0.1` et écrire dans le dossier temporaire Windows. Dans le bac à sable Codex de ce poste, lancer **cette commande de contrôle** avec `exec_command` et `sandbox_permissions="require_escalated"` (justification : tests HTTP locaux et dossiers temporaires). Les erreurs `WinError 10013` pour le socket ou `WinError 5` dans `Temp` viennent de cette restriction ; relancer la même suite sous ces permissions, sans changer le code. `--quick` fonctionne dans le bac à sable ordinaire. Les contrôles courants restent utilisables après modification du moteur, sans actualiser l’ancien instantané.

Le dernier relevé remplace `tmp/check-model-last.json`. Il n’y a pas de série de rapports automatiques. Pour une correction CSS, utiliser directement le build et la vérification visuelle ciblée ; ne pas lancer une recalibration économique.

La grille est validée une fois par chargement ; un nouveau processus ou chargement revalide ses propres sources. Le relevé indique le poids du bootstrap essentiel. Les rapports de performance distinguent temps de calcul, transport et temps de rendu, sans déduire ce dernier des seuls timings HTTP.

## Instruire les sorties des skills

```powershell
python tools/core_qualification.py
python tools/market_instruction.py
python tools/market_instruction.py --details
python tools/analyze_cost_references.py
```

Ces commandes sont en lecture seule. La première présente les qualifications, inconnues et références historiques du pilote Core ; la deuxième résume la progression marché, et `--details` restitue tous les couples capacité/produit. Le diagnostic de marché partage sa validation monétaire avec le chargement courant.

`python tools/core_qualification.py --candidate` prépare uniquement un candidat retenu pour relecture. **Le pilote historique courant est volontairement refusé**, même si l’on y renseigne des chiffres. Une nouvelle évaluation doit déclarer son périmètre de qualification, ses preuves et ses décisions dans le contrat dédié. La proposition conserve les références de provenance et sépare les types de JH ; elle n’écrit jamais dans les hypothèses actives et ne constitue pas une charge totale projet complète.

Les contrats sont décrits dans `source/README.md`. Aucune de ces commandes ne recalcule les charges historiques à partir d’observations de marché, ne publie d’instantané ni ne modifie les simulations.

## Démarrer ou actualiser l’application locale

```powershell
powershell -ExecutionPolicy Bypass -File tools/start_study_app.ps1 -NoOpen
```

Le lanceur recharge le serveur suivi si les sources, le moteur ou le build ont changé. `-Restart` permet de forcer ce rechargement. Après une modification React ou CSS, reconstruire l’interface avant de relancer le lanceur. Chaque mise à jour de l’étude se termine par les contrôles adaptés et cette actualisation.

Le serveur sur `http://127.0.0.1:8766` présente « Étude en cours ». Il charge un ensemble cohérent de données, paramètres, preuves textuelles et assets. Les simulations ne relisent pas les YAML. Les PDF et classeurs originaux restent vérifiés par empreinte. Garder le même port conserve le stockage navigateur et les simulations personnelles.

## Créer un instantané technique sur demande

```powershell
python -m tools.check_model --full --publish
```

Cette commande facultative contrôle le candidat, actualise les exports et remplace atomiquement `release/current.json`. Un échec conserve l’instantané précédent. Elle ne sélectionne aucun mode de l’application et n’est pas nécessaire pour travailler au quotidien. Les formats historiques de gel et de reprise restent compatibles.

## Reproduire le relevé de code OSS

Le diagnostic de la [fiche ERPNext/Frappe/Insights](../sources/fiche-marche-frappe-erpnext-flow-2026-10-28.md) utilise trois commits publics figés. Les [fiches Microsoft](../sources/fiche-marche-microsoft-flow-2026-10-28.md) et [SAP](../sources/fiche-marche-sap-flow-2026-10-28.md) reprennent le cadre FLOW commun, mais ne disposent d'aucun relevé de code complet. Depuis la racine, cloner les tags ci-dessous puis exécuter le compteur en lecture seule :

```powershell
git clone --depth 1 --branch v16.54.0 https://github.com/frappe/frappe.git tmp/oss-audit/frappe
git clone --depth 1 --branch v16.52.1 https://github.com/frappe/erpnext.git tmp/oss-audit/erpnext
git clone --depth 1 --branch v3.15.1 https://github.com/frappe/insights.git tmp/oss-audit/insights
python tools/oss_flow_code_audit.py tmp/oss-audit
```

Le script refuse un autre commit et affiche fichiers, octets, PNCLOC et un calcul COCOMO II nominal simplifié sur la sélection de code retenue. Il ne modifie ni les dépôts clonés ni les calculs économiques FLOW. Les règles d'inclusion, de comptage et les limites figurent dans la fiche.

Les [fiches Odoo Community](../sources/fiche-marche-odoo-community-flow-2026-10-28.md), [Tryton](../sources/fiche-marche-tryton-flow-2026-10-28.md) et [Axelor](../sources/fiche-marche-axelor-flow-2026-10-28.md) utilisent le [compteur commun des trois candidats](oss_candidates_code_audit.py). Après avoir préparé les checkouts aux tags et SHA indiqués dans chaque fiche, reproduire les inventaires par ces commandes :

```powershell
python tools/oss_candidates_code_audit.py odoo tmp/odoo20-audit --spreadsheet tmp/o-spreadsheet20-audit
python tools/oss_candidates_code_audit.py tryton tmp/tryton-code-audit-2026-10-28
python tools/oss_candidates_code_audit.py axelor tmp/oss-audit-axelor --platform tmp/oss-audit-axelor-platform --webapp tmp/oss-audit-axelor-webapp --studio tmp/oss-audit-axelor-studio --utils tmp/oss-audit-axelor-utils --message tmp/oss-audit-axelor-message
```

Le compteur refuse les commits différents et sépare code, XML, CSV et manifestes. Les totaux sont des **sélections physiques de code source**, avec certains modules encore plus larges que FLOW et des dépendances Finance hors total. Ils ne sont ni des points de fonction ni des JH de reconstruction. Aucun COCOMO comparatif n'est dérivé pour ces trois produits.

## Vérifier une refactorisation sans changement économique

```powershell
python -m tools.check_model --full --preserve audits/2026-10-27-refonte-modele-parite.json
```

`--preserve` vérifie la référence et les scénarios du témoin explicitement choisi. Ce témoin est pertinent pour cette simplification ; ne pas l’imposer à une évolution économique ultérieure autorisée. Les tests permanents vérifient les invariants et les sources courantes, pas toutes les anciennes versions.

## Organisation du code

| Module | Responsabilité |
|---|---|
| `model_context.py`, `validate_stacks.py` | Chargement YAML sûr, rejet des doublons, cache limité à un chargement, détection des modifications concurrentes. |
| `business_calibration.py`, `buy_qualification.py`, `business_map.py` | Travaux, couverture Buy et cartographie canonique. |
| `model_inputs.py` | Volumes dérivés, contrats composables, réceptions, parts et références de déploiement. |
| `calculate_costs.py` | `valuation()` fournit les travaux, bases annuelles et séquences Buy au calendrier. `calculate()` conserve le diagnostic historique complet pour les seuls exports explicites. |
| `validate_cycle.py` | Catalogues, rôles, volumes, prix et inclusions ; aucun score historique ni registre AGENTS. |
| `composable_costs.py` | Compilation des données requises et journal de financement ; calcul sans lecture disque. |
| `project_investment.py` | Calendrier pur, annuités, responsabilités et horizons. Le contrepoint SAP reste séparé du coût Make. |
| `study_app.py`, `sponsor_reading.py` | Paramètres, lectures sponsor et simulations. |
| `market_oss.py` | Validation du cadre FLOW, des fiches produit comparables et de la liste OSS à étudier ; dérivation du calcul COCOMO nominal pour la seule sélection ERPNext/Frappe/Insights, hors calcul des cinq options. |
| `core_method.py` | Validation et compilation des méthodes `methode-evaluation-core.yaml`, `methode-calcul-net.yaml`, `methode-calcul-run.yaml` et `methode-evaluation-marche.yaml`. Rendu commun des explications et formules, sans calcul économique. Le support des exemples fictifs reste compatible, mais les pages courantes n’en présentent pas. Les skills `flow-evaluer-core-system` et `flow-etude-marche` lisent chacun la source de leur méthode. |
| `framework_vision.py` | Validation et hydratation de la Vue d’ensemble depuis `vision-framework.yaml` : contrat fermé, glossaire et liens documentaires ou routes courantes. Texte pédagogique uniquement, figé avec les autres sources. |
| `framework_parameters.py` | Projection de lecture des paramètres depuis les rôles, tarifs, preuves, calibration et contrat personnel existants. Conserve tous les champs, refuse les surcharges contradictoires et distingue modification directe, agrégat et référence. Aucun calcul économique. |
| `application_framework.py` | Validation des remarques sur l’application actuelle et des liens du dossier économique. Référence le statut canonique, sans recopier les paramètres. |
| `economic_reading.py` | Lecture figée des montants existants : sélection Buy, intégration et fonctionnement annuel des cinq options. Vérifie leurs propriétaires et la réconciliation des postes. `/api/economic-evaluations` sert cette lecture versionnée sans relire les sources ni ajouter de calcul. |
| `market_reading.py` | Projection documentaire des projets, prix et services du registre déjà chargé. Servie à la demande par `/api/market-references`, avec contrôle de version et sans lecture disque ni ajout au bootstrap essentiel. Aucun prix transposé ou annualisé supplémentaire. |
| `study_snapshot.py` | Carte transportée par identifiants, sources figées et publication atomique d’une release. |
| `serve_study_app.py` | Serveur local sur les sources courantes, ensemble figé en mémoire et bootstrap préparé une fois. |
| `check_model.py`, `test_support.py` | Contrôles gradués, fixture partagée avec copies isolées et dernier relevé des durées. |
| `oss_flow_code_audit.py` | Comptage reproductible du code public Frappe/ERPNext/Insights pour la fiche et les mesures du modèle de marché ; aucun calcul actif des cinq options. |
| `oss_candidates_code_audit.py` | Comptage reproductible, par dépôt et couche, des sélections Odoo Community, Tryton et Axelor ; résultats de code et déclarations distincts, sans JH ni calcul économique actif. |

Les adresses `source/couts-15-ans.yaml` et `source/investissements-10-ans.yaml` sont conservées pour les liens documentaires. `source/investissements-15-ans.yaml` exporte la projection courante depuis le début du projet ; ces fichiers sont des résultats non éditables, actualisés lors de la création explicite d’un instantané. Le diagnostic `couts-15-ans.yaml` reste distinct et n’est pas lu par le calcul courant. L’application sert les sources courantes. Les anciens exports Excel sont supprimés à la demande de l’utilisateur ; les classeurs fournisseur restent des preuves. Le générateur Excel ne s’exécute que sur demande explicite.

## Retraits et récupération

Le reçu `audits/2026-10-27-refonte-modele-retraits.json` décrit les chemins retirés, empreintes, motifs et exemplaires conservés. `tmp/model-refactor-recovery.zip` est une sauvegarde ponctuelle des fichiers textuels avant refonte, distincte des deux états métier. Elle ne conserve pas les anciens exports Excel supprimés. Restaurer uniquement un fichier explicitement choisi, après comparaison avec sa version courante ; ne pas restaurer tout l’ancien modèle par défaut.

## Environnement

`tools/requirements-model.txt` fixe PyYAML, jsonschema et openpyxl. Utiliser de préférence `.venv`. Le lanceur accepte le cache local existant `tmp/yaml-stacks/deps` si PyYAML n’est pas installé ; ce cache n’est pas une source économique. Node.js et les dépendances déjà installées dans `app/node_modules` sont requis pour la vérification release.

Les tests HTTP utilisent uniquement la boucle locale. Dans un environnement isolé interdisant ces ports, utiliser `--quick` pendant le développement puis autoriser l’exécution locale de `--release` pour la vérification finale. Une erreur réseau ne valide pas un test.

## GitHub Pages

Le workflow `.github/workflows/pages.yml` contrôle les sources courantes, construit le site puis le publie après succès. Il ne remplace pas `release/current.json`. Le site complet et le dépôt sont publics, selon le choix de l’utilisateur.

```powershell
pnpm --dir app install --frozen-lockfile --ignore-scripts
pnpm --dir app exec vite build
python -m tools.check_model --full
pnpm --dir app exec vite build --outDir dist-pages --base /FLOW-Etude-Economique/
python -m tools.build_pages --output app/dist-pages --base /FLOW-Etude-Economique/
python -m tools.pages_validation --output tmp/pages-validation.json
```

`build_pages.py` exporte le bootstrap, les lectures documentaires et les preuves déclarées avec leurs empreintes, puis le bundle et les modules du moteur. Les URLs des données sont versionnées. `pages_runtime.py` adapte seulement les requêtes aux fonctions Python existantes. Le worker charge Pyodide à la première simulation ou lecture d’extrait ; aucun serveur de calcul distant n’est nécessaire.

Pour une vérification indépendante, servir `app/dist-pages/` sous le chemin `/FLOW-Etude-Economique/` avec un serveur HTTP statique, puis :

```powershell
node app/scripts/verify-pages.mjs --url http://127.0.0.1:8777/FLOW-Etude-Economique/ --cases tmp/pages-validation.json --output tmp/pages-validation-report.json
```

Le script vérifie les pages, les preuves, les simulations réelles dans Pyodide et la reprise des sauvegardes. Installer Chromium avec `pnpm --dir app exec playwright install chromium`, ou définir `PLAYWRIGHT_CHROMIUM_EXECUTABLE` vers un Chrome installé. Le workflow prépare une prévisualisation isolée et installe les dépendances système du navigateur sur son runner Linux. Les cas de référence de ce contrôle sont recalculés à chaque exécution, sans geler les hypothèses économiques.

Garder `app/dist/` pour le serveur local sur 8766. Après modification, relancer `tools/start_study_app.ps1 -NoOpen` depuis `C:/Dev/FLOW-Etude-Economique` ; contrôler `/api/health`, son PID, l’empreinte du client et `sources_current`.
