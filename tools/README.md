# Modèle FLOW : commandes courantes

Un seul flux de travail : les sources courantes sont dans `source/` et `config/`. La construction statique les fige pour le navigateur, sans choix de mode ni publication intermédiaire. En local comme sur GitHub Pages, le serveur expose uniquement les fichiers. Les calculs sont exécutés dans un Web Worker avec Python/Pyodide, sans API HTTP métier. Les simulations personnelles restent dans le navigateur ; aucune commande ci-dessous ne les efface. `release/current.json` reste un instantané technique facultatif.

## Développement local ciblé

Commande habituelle après une modification locale :

```powershell
python -m tools.check_dev --paths app/src/App.tsx app/src/styles.css
python -m tools.check_dev --paths tools/estimation_stock.py --plan-only
python -m tools.check_dev --paths tools/estimation_stock.py
python -m tools.check_dev --paths tools/test_model_inputs.py --tests test_model_inputs.ModelInputTests
```

Fournir tous les fichiers de la tâche, y compris les nouveaux. Le plan sélectionne les tests Python par imports directs et transitifs, y compris ceux placés dans les fonctions. Les imports construits dynamiquement ne sont pas détectés. Compléter avec `--tests module.Classe.methode` lorsque nécessaire. Si les imports transitifs sélectionnent des suites sans rapport avec la tâche, utiliser `--targeted --tests ...` avec les tests métier explicitement choisis. Ce mode conserve les contrôles financiers obligatoires des modifications de données. Il exige une sélection explicite et ne certifie jamais une validation complète. Les modules et méthodes qui se recouvrent ne sont exécutés qu’une fois. Les données déclenchent le chargement validé et les invariants des entrées, financements et calculs. Pour une évolution métier, ajouter les tests du domaine concerné.

CSS et documentation ne déclenchent aucune suite Python. TypeScript lance les types, les tests JavaScript et les règles de contenu, sans livraison Pages ni régression Python. Un fichier non reconnu bloque avec une demande de contrôles ciblés, sans relancer toute la suite. Le sélecteur travaille sur le périmètre de la tâche, pas sur les changements accumulés depuis une ancienne validation complète.

Contrôler visuellement la page et le parcours touchés sur le serveur local. La reconstruction nécessaire à leur affichage est distincte des tests. Utiliser le lanceur habituel pour actualiser la livraison statique. `--browser` est optionnel et demande explicitement la régression navigateur complète existante. Pour une retouche visuelle, privilégier l'inspection du parcours touché. Ne pas annoncer une vérification visuelle sur la seule réussite du script.

Les rapports chronométrés sont dans `tmp/validation/` et `tmp/check-dev-last.json`. Ils portent `mode: dev` et `certification: false`. Ils ne remplacent ni le manifeste complet ni les preuves des scripts de commit et push. La CI et les validations complètes existantes restent inchangées.

## Contrôler au jalon de validation

Depuis la racine, dans l’environnement Python du projet :

```powershell
python -m tools.check_model --auto
python -m tools.check_model --quick
python -m tools.check_model --content
python -m tools.check_model --full
python -m tools.check_model --full --browser
```

- **auto** : comparer les empreintes et les champs YAML au dernier contrôle complet réussi. Une modification numérique, structurelle, du métamodèle, du moteur, des preuves ou non reconnue déclenche la suite complète. Seules les modifications de champs éditoriaux existants et du client React/TypeScript/CSS autorisent les contrôles de présentation avec chargement, contrats, interface, reprise et vrai navigateur. Ce passage ne remplace pas une certification complète. Sans témoin complet valide, lancer la suite complète.
- **quick** : contrats des entrées, volumes dérivés, calendriers, rôles, prix et inclusions Buy, invariants financiers, isolation du modèle et de la release. Un seul chargement partagé, aucune ouverture de port.
- **content** : vérifier les textes et références avec le modèle courant, sans modifier les hypothèses ni les résultats enregistrés. Aucun instantané préalable requis.
- **full** : tous les tests Python, compatibilité HTTP historique, JavaScript, formats, navigation, reprise des anciennes simulations, compilation TypeScript, contenu et livraison statique de l’application. `--release` reste un alias compatible. Aucun instantané remplacé sans `--publish`.

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

Les commandes Dev et modèle affichent en direct la phase, le temps écoulé, les tests terminés sur le total planifié et le nombre de tests en échec. Une ligne revient toutes les 15 secondes même si un test est long. Les compteurs concernent la suite Python, pas l'ensemble du processus. Aucun pourcentage global ni délai restant n'est extrapolé de tests de durées inégales. Les états lisibles pendant l'exécution sont `tmp/check-dev-progress.json`, `tmp/check-model-progress.json` et `progress.json` dans le dossier de la session. Après une interruption brutale, un état `running` peut rester présent, vérifier aussi le processus. Pour suivre sans attendre le rapport final :

```powershell
Get-Content tmp/check-model-progress.json
Get-Content tmp/check-dev-progress.json
```

Chaque exécution conserve `tmp/validation/<identifiant>/report.json`, `junit.xml` et les journaux des contrôles de l’interface. `tmp/check-model-last.json` pointe sur le dernier résultat, même en échec. Les rapports incluent les durées par phase et par test, les erreurs immédiates, les tests planifiés et la traçabilité des règles vers les tests effectivement réussis. La CI conserve ces rapports comme artefacts.

`business_contract.py` relie chaque règle du métamodèle canonique à un test réel. Une règle nouvelle ou un test supprimé sans mise à jour de ce contrat fait échouer le contrôle. Les 18 règles arithmétiques ont des exemples indépendants avec résultats littéraux et rejets des entrées invalides. Cette traçabilité ne constitue pas une mesure de couverture des lignes ou branches du code. Les tests existants continuent de vérifier financements uniques, capacités natives, rôles, finalités, annuités au centime, horizons, inconnus, exports et calcul sans lecture disque.

```powershell
python -m tools.check_model --full --preserve tmp/validation-optimization-parity.json --compare audits/2026-10-31-optimisation-controles-avant.json
```

`--compare` conserve l’inventaire des tests du relevé précédent et mesure le temps gagné. Aucun test historique de cet inventaire ne peut disparaître ou être ignoré. `--preserve` compare exactement les projections, hors identifiant technique du moteur, pour les six simulations et les cas limites du témoin choisi. Ce témoin ponctuel ne fige pas les futures évolutions économiques autorisées.

La grille est validée une fois par chargement ; un nouveau processus ou chargement revalide ses propres sources. Le relevé indique le poids du bootstrap essentiel. Les rapports de performance distinguent temps de calcul, transport et temps de rendu, sans déduire ce dernier des seuls timings HTTP.

## Contrôler dans un vrai navigateur

`check_model --auto` est réservé au jalon de validation et inclut le vrai navigateur pour les modifications de présentation. En Dev, utiliser `check_dev` et le parcours touché. `--full --browser` l’ajoute explicitement au contrôle complet. La CI utilise Playwright avec Chromium sur la livraison Pages. Le contrôle échoue si une requête HTTP vers une API est émise. Il vérifie toutes les vues en mobile et en bureau, les huit scénarios du témoin, la reprise des sauvegardes, les originaux téléchargeables et le clavier.

```powershell
node app/scripts/verify-pages.mjs --url http://127.0.0.1:8766/ --allow-root true --cases tmp/validation-optimization-parity.json --output tmp/local-browser-report.json
```

Le scénario local utilise la même architecture statique que Pages. Aucun navigateur personnel ni stockage existant n’est effacé. Les adresses internes `/api/...` du moteur sont des messages vers le Worker, pas des appels réseau. Le serveur local n’expose ni `/api/health` ni `/api/simulate`.

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

Le lanceur utilise `prepare_static_app` pour vérifier les empreintes des sources et des fichiers livrés. Une livraison inchangée est réutilisée. Sinon, les sources courantes et l’interface sont reconstruites ensemble, puis servies par `python -m http.server`. Le serveur historique d’API locale est arrêté lors de la migration du processus suivi. `-Restart` permet de forcer ce rechargement. Le lanceur reconstruit aussi les modifications React ou CSS si nécessaire. Chaque mise à jour de l’étude se termine par les contrôles adaptés et cette actualisation.

Le serveur sur `http://127.0.0.1:8766` présente « Étude en cours ». Le navigateur charge un ensemble cohérent de données, paramètres, preuves textuelles et assets. Le serveur ne calcule aucun montant. Les simulations ne relisent pas les YAML. Les PDF et classeurs originaux restent vérifiés par empreinte. Garder le même port conserve le stockage navigateur et les simulations personnelles.

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

Le compteur refuse les commits différents et sépare code, XML, CSV et manifestes. Les totaux sont des **sélections physiques de code source**, avec certains modules encore plus larges que FLOW et des dépendances Finance hors total. Ils ne sont ni des points de fonction ni des JH de reconstruction. Le compteur et le registre actif ne dérivent aucun COCOMO pour ces trois produits. La pièce Tryton conserve un diagnostic nominal conditionnel distinct, sans reprise dans les cinq options économiques.

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
| `delivery_readiness.py` | Validation et compilation des conditions de réalisation et du dossier de capacité : rôles, liens aux capacités natives, preuves et jalons. Aucun calcul ni paramètre économique. |
| `framework_parameters.py` | Projection de lecture des paramètres depuis les rôles, tarifs, preuves, calibration et contrat personnel existants. Conserve tous les champs, refuse les surcharges contradictoires et distingue modification directe, agrégat et référence. Aucun calcul économique. |
| `application_framework.py` | Validation des remarques sur l’application actuelle et des liens du dossier économique. Référence le statut canonique, sans recopier les paramètres. |
| `economic_reading.py` | Lecture figée des montants existants : sélection Buy, intégration et fonctionnement annuel des cinq options. Vérifie leurs propriétaires et la réconciliation des postes. `/api/economic-evaluations` sert cette lecture versionnée sans relire les sources ni ajouter de calcul. |
| `market_reading.py` | Projection documentaire des projets, prix et services du registre déjà chargé. Servie à la demande par `/api/market-references`, avec contrôle de version et sans lecture disque ni ajout au bootstrap essentiel. Aucun prix transposé ou annualisé supplémentaire. |
| `study_snapshot.py` | Carte transportée par identifiants, sources figées et publication atomique d’une release. |
| `prepare_static_app.py`, `start_study_app.ps1` | Construction statique vérifiée et serveur de fichiers local. |
| `serve_study_app.py` | Adaptateur HTTP historique conservé pour les contrôles de compatibilité. Le lancement courant ne l’utilise plus. |
| `check_model.py`, `test_support.py` | Contrôles gradués, fixture partagée avec copies isolées et dernier relevé des durées. |
| `oss_flow_code_audit.py` | Comptage reproductible du code public Frappe/ERPNext/Insights pour la fiche et les mesures du modèle de marché ; aucun calcul actif des cinq options. |
| `oss_candidates_code_audit.py` | Comptage reproductible, par dépôt et couche, des sélections Odoo Community, Tryton et Axelor ; résultats de code et déclarations distincts, sans JH ni calcul économique actif. |

Les adresses `source/couts-15-ans.yaml` et `source/investissements-10-ans.yaml` sont conservées pour les liens documentaires. `source/investissements-15-ans.yaml` exporte la projection courante depuis le début du projet ; ces fichiers sont des résultats non éditables, actualisés lors de la création explicite d’un instantané. Le diagnostic `couts-15-ans.yaml` reste distinct et n’est pas lu par le calcul courant. L’application sert les sources courantes. Les anciens exports Excel sont supprimés à la demande de l’utilisateur ; les classeurs fournisseur restent des preuves. Le générateur Excel ne s’exécute que sur demande explicite.

## Retraits et récupération

Le reçu `audits/2026-10-27-refonte-modele-retraits.json` décrit les chemins retirés, empreintes, motifs et exemplaires conservés. `tmp/model-refactor-recovery.zip` est une sauvegarde ponctuelle des fichiers textuels avant refonte, distincte des deux états métier. Elle ne conserve pas les anciens exports Excel supprimés. Restaurer uniquement un fichier explicitement choisi, après comparaison avec sa version courante ; ne pas restaurer tout l’ancien modèle par défaut.

## Environnement

`tools/requirements-model.txt` fixe PyYAML, jsonschema et openpyxl. Utiliser de préférence `.venv`. Le lanceur accepte le cache local existant `tmp/yaml-stacks/deps` si PyYAML n’est pas installé ; ce cache n’est pas une source économique. Node.js et les dépendances déjà installées dans `app/node_modules` sont requis pour la vérification release.

Les tests HTTP utilisent uniquement la boucle locale. Dans un environnement isolé interdisant ces ports, utiliser `--quick` pendant le développement puis autoriser l’exécution locale de `--release` pour la vérification finale. Une erreur réseau ne valide pas un test.

## Préparer et créer un commit local

Le script `tools/git_commit.py` automatise les vérifications du dépôt, de l’identité et du périmètre, la réutilisation des contrôles, les tests nécessaires et la création du commit. Il cible exclusivement `laurent-sintes/FLOW-Etude-Economique` sur `main`.

```powershell
python -m tools.git_commit prepare --paths app/src/SynvanceReferencePage.tsx app/src/synvanceReference.css --message "Clarifier la lecture du dossier Synvance"
python -m tools.git_commit commit
```

`prepare` produit `tmp/git-commit/plan.json` et ne modifie ni les fichiers ni les entrées de l’index. Les chemins sont des fichiers explicites, sans balayage automatique du dossier. Le plan contient leurs empreintes, le message, HEAD, l’état de l’index, le périmètre et les preuves des contrôles. `--message-file chemin.txt` accepte un message UTF-8 multiligne.

Une preuve de validation est réutilisée si les sources, l’environnement et les rapports correspondants sont identiques. Un contrôle complet déjà réussi peut être réutilisé. Sinon, le script appelle `check_model --auto --browser`. Il construit et vérifie également la version Pages avec son vrai préfixe. Les reçus restent dans `tmp/git-commit/`.

`commit` relit le plan, vérifie les empreintes, puis enregistre uniquement les fichiers sélectionnés avec `git commit --only`. Les fichiers hors périmètre déjà indexés restent indexés. Un fichier partiellement indexé dans le périmètre bloque la préparation, pour préserver ce choix. Une modification des sources, de HEAD, de l’index, du message ou des preuves impose une nouvelle préparation.

Pour examiner le périmètre sans lancer les contrôles :

```powershell
python -m tools.git_commit prepare --paths tools/git_commit.py tools/test_git_commit.py --message "Automatiser les commits locaux" --plan-only
```

Cette prévisualisation ne peut pas créer de commit. Le résultat d’un commit réussi est enregistré dans `tmp/git-commit/result.json`. En cas d’échec d’un hook ou du commit, les fichiers sélectionnés peuvent rester indexés pour examen. Les hooks existants sont respectés. Le script ne pousse aucun commit, ne publie aucun instantané et ne modifie pas les remotes.

## Préparer, envoyer et suivre un push

```powershell
python -m tools.git_push prepare
python -m tools.git_push push
```

`prepare` vérifie `main`, les URL de lecture et d’envoi d’`origin`, le dépôt GitHub public et la relation avec `origin/main` après un fetch sans tags. Le plan `tmp/git-push/plan.json` contient le SHA exact, la référence distante observée, les commits à envoyer et les modifications locales qui resteront hors envoi. Un retard ou une divergence bloque la préparation et demande une intégration préalable. Aucun commit n’est créé.

Les preuves de validation doivent correspondre aux fichiers du commit. Elles ne sont pas déduites de l’état courant du dossier. Le témoin des simulations est généré par le moteur de ce commit, extrait dans un dossier temporaire isolé. Les modifications et l’index en cours sont préservés.

`push` envoie le SHA préparé vers `refs/heads/main`, sans force ni tags. Il relit la référence distante après l’envoi, y compris après une erreur réseau. Si le SHA est déjà présent, il ne renvoie pas les commits. Une avancée distante non prévue bloque l’opération.

Le suivi attend le workflow `pages.yml` du bon SHA sur `main`, puis la réussite du job `deploy`. Il contrôle l’URL Pages autorisée, le champ `deployment_commit` du manifeste publié et les parcours réels dans Chrome/Chromium contre les simulations du commit. La CI renseigne `FLOW_DEPLOYMENT_COMMIT` avec `github.sha`. Cette provenance est une métadonnée technique, sans effet économique.

```powershell
python -m tools.git_push prepare --plan-only
python -m tools.git_push push --no-wait
python -m tools.git_push watch
```

La prévisualisation ne peut pas envoyer de commits. `--no-wait` confirme seulement l’envoi, sans prétendre que le site est déployé. `watch` reprend le suivi après une interruption ou un dépassement de délai, sans refaire de push. GitHub CLI doit être connecté à `github.com`. Les lectures API utilisent explicitement cet hôte. Le délai de suivi est réglable par `--timeout` en secondes, avec 30 minutes par défaut.

Le dernier résultat est écrit dans `tmp/git-push/result.json`. Il distingue l’envoi confirmé, le déploiement vérifié et les échecs. Un ancien commit sans provenance Pages doit être complété par un commit contenant le workflow et le générateur mis à jour pour utiliser cette vérification stricte.

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

Garder `app/dist/` pour le serveur local sur 8766. Après modification, relancer `tools/start_study_app.ps1 -NoOpen` depuis `C:/Dev/FLOW-Etude-Economique`, puis vérifier le manifeste `site-manifest.json` et le chargement de l’application. Le serveur statique ne fournit pas de route HTTP `/api/health`.

## Calcul des familles et métamodèle

Le contrat métier unique est `source/fondamentaux.yaml`, avec les règles dans `estimation_model`. `estimation_calculation.py` reproduit les références, calcule les écarts avant arrondi et la ventilation par rôle ; `retained_core.py` vérifie la concordance avec la décision puis valorise les rôles. `capability_catalog.py` restitue la capture native ; `current_cost_inputs.py` conserve les unités annuelles et compléments Buy sans les anciennes affectations Make.

Le pilote `core_qualification.py --candidate` demeure un diagnostic historique et n’alimente plus le flux courant. Pour une évolution : modifier le contrat métier si nécessaire, ses instances et contrôles, puis les projections et le skill. Exécuter `python -B -m tools.check_model --full` ; ne pas publier d’instantané sans demande.

## Téléchargement du modèle métier

`python -B -m tools.export_business_model` compose `tmp/model-download/flow-modele-metier.yaml` depuis les dépendances structurées réellement chargées et validées par `Study`. Le fichier regroupe le métamodèle canonique, les données métier, les entrées auditées de calcul, les schémas et les empreintes des sources. Les pièces externes restent référencées. Aucun balayage des anciens fichiers ni scénario personnel.

Le plugin `app/scripts/model-download.mjs` appelle ce programme à chaque construction Vite, y compris les commandes directes de CI. La comparaison du contenu évite une réécriture inutile ; les exports manquants ou altérés sont régénérés, par remplacement atomique. Une erreur bloque la construction. L’export est livré sous `exports/flow-modele-metier.yaml`, à la racine locale ou sous le préfixe Pages. En développement Vite, la route compose le fichier à la demande. `FLOW_PYTHON` permet de choisir le runtime ; les dépendances sont celles de `requirements-model.txt`.

## Préparation contrôlée des deux voies

`estimation_inputs.py` valide identité, stack, périmètre, financements et chaîne de preuves. `estimation_preparation.py` recompose tailles natives, réutilisation, compléments et mouvements COSMIC depuis les mesures enregistrées, sans dépendre de clones OSS dans `tmp/`. Les règles arithmétiques et leurs domaines viennent du métamodèle. Les tests `test_estimation_audit.py` rejouent les incohérences de l’audit et reproduisent les préparations depuis le téléchargement sans lecture disque.

L’export YAML version 2 sépare `model` (instances actives), `metamodel`, `schemas` et `evidence` (pièces utilisées, y compris préparation historique). `sources` contient leurs empreintes. Une ancienne proposition incluse comme preuve ne vaut pas adoption ; les dépôts OSS et PDF restent référencés.

Le téléchargement réutilise un cache local uniquement si les empreintes de toutes les dépendances, des modules du générateur et des bibliothèques sont inchangées et si le YAML conserve son empreinte. Le cache est régénérable ; il ne devient pas une source métier. Une construction Pages vérifie aussi la concordance avec le Study déjà chargé. Les validations autonomes ouvrent un chargement isolé, sans cache global ; les variantes sont toujours contrôlées. Le serveur local sert le YAML avec son type explicite pour négocier gzip.


La préparation Stock suit le contrat de calcul distinct native_component_analogies_v1 : attribution des composants mixtes, déduction du code Master Data déjà financé, analogies de modules, modèles et vues. Le module tools/estimation_stock.py est appelé par estimation_preparation.py ; les formules restent dans source/fondamentaux.yaml. Les preuves enregistrées suffisent au calcul et au téléchargement, sans dépôt OSS local. Les consommateurs affichent le propriétaire du financement réutilisé.

La préparation de nouveaux modules de propriété suit native_new_module_analogies_v1 dans tools/estimation_ownership.py. Elle reconstruit les analogues du contrat Stock figé, puis calcule uniquement le nouveau comportement de propriété. La propriété consomme les financements Master Data et Stock ; les clauses de réutilisation et les limites des lectures aux deux dates restent visibles. Les décisions adoptées et la somme des JH sont dérivées de leurs instances, sans somme des délais locaux.

La préparation coherent_components_v1 dans tools/estimation_components.py reconstruit les six ensembles fortement liés depuis les archives complètes figées gzip/base64. Les tailles de leurs modules sont additionnées avant un seul calcul COCOMO par unité. Le téléchargement contient ces archives et permet la reprise sans checkout OSS. Les mécanismes ont un propriétaire unique ; une allocation entre familles ne crée pas de nouveaux JH. Java/Spring couvre les 88 capacités, tandis que .NET et Rust restent à réestimer. Les trois décisions précédentes restent inchangées et aucun délai local n’est additionné.

La lecture des fonctions professionnelles utilise `core_product_scope.py`. La proposition complète séparée est reconstruite par `core_product_estimate.py`, depuis `source/proposition-produit-core.yaml` et ses preuves figées. Elle ne modifie pas les décisions ni les paramètres personnels ; les formules restent dans le métamodèle canonique. Les tests contrôlent remplacement sans cumul, conservation des rôles/coûts et exclusions COSMIC des fonctions consommées.

## Comparaison fonctionnelle des solutions

`source/comparaison-solutions.yaml` porte les lectures par BA, sources, écarts et rapprochements RFI. `tools/market_comparison.py` vérifie leurs liens aux propriétaires existants et dérive la matrice chargée à la demande. Les règles sont définies dans le métamodèle unique. `python -m unittest test_market_comparison` contrôle les rejets de couverture injustifiée, les exclusions et les financements inconnus. Aucun écart documentaire ne modifie les décisions économiques.

Le dossier G02 relie les critères aux préparations et financements existants. `python -m unittest test_gap_instruction` vérifie ses références et interdit de convertir les inconnues ou les essais en chiffrage. `python audits/2026-10-31-g02-allocation-anticipee/acceptance_model.py` rejoue les critères expérimentaux et écrit son résultat dans `tmp/`, sans modifier la preuve figée ni la référence économique.

Les réserves des écarts sont contrôlées par `python -m unittest test_budget_supplements` avec `PYTHONPATH=tools`. Le contrôle rejoue les financements référencés, couvre les couples écart/option/phase et refuse doublons, montants sans contrat et faux totaux. Les procédures de recette du dossier sont des travaux à effectuer, pas des tests ERP exécutés.

## Version lisible du modèle

`python -m tools.model_revision show` affiche la date et le numéro d’ordre courant. `python -m tools.model_revision bump --date AAAA-MM-JJ` incrémente explicitement le compteur global et écrit la date de cette nouvelle version. Aucun incrément n’a lieu au démarrage, pendant un export, un test ou une reconstruction. Préparer les changements du modèle avant cet incrément et les contrôles. Les empreintes techniques et le contrat des simulations restent distincts.


## Adopter une estimation Core

Après validation métier des nouveaux montants, une seule entrée prépare les documents, vérifie une copie isolée et applique l’ensemble :

```powershell
python -m tools.adopt_core template --output tmp/proposition-core.json
# Modifier la proposition : livrables, JH et répartition Core Domain / Support.
python -m tools.adopt_core run --proposal tmp/proposition-core.json --decision-note "Validation métier du chiffrage" --refresh
```

`template` reprend les lots déjà détaillés par livrable. Il ne crée aucun coût. Pour une simple évolution de charges, réutiliser la méthode en place. La répartition entre finalités doit être explicite lorsque le lot est mixte. Une proposition identique retourne `no_change` sans nouvelle version ni écriture des sources.

Pour examiner le résultat avant application :

```powershell
python -m tools.adopt_core prepare --proposal tmp/proposition-core.json --decision-note "Validation métier du chiffrage"
python -m tools.adopt_core apply --plan tmp/core-adoptions/IDENTIFIANT/plan.json
```

Le plan conserve le détail des fichiers, leurs images avant/après, les empreintes des entrants, le résultat des vérifications, les montants et les temps de chaque phase. La validation charge le vrai modèle dans une copie isolée et réconcilie les cinq options et vingt horizons. Le calendrier, les tarifs et les autres options doivent rester inchangés. La version lisible est incrémentée une fois dans le candidat, puis dans les sources seulement si l’application réussit.

Les propositions COCOMO ou COSMIC déjà préparées peuvent utiliser le même point d’entrée avec `method: prepared_contracts`. Le fichier JSON comprend `format: 1`, `date`, `decision_ref` et `documents` (objets YAML/JSON, texte pour les Markdown). Il fournit les décisions retenues, les contrats de calcul, leurs nouvelles preuves et les ventilations requises. La décision porte `adopted_jh`, `proposal_jh`, `previous_cost_eur_ht`, `construction_cost_eur_ht`, `status: adopted`, `decision_status: adopted`, la date et `user_decision` identique à la note passée en argument. Les calculs doivent utiliser les recettes déjà implémentées. Le moteur valide ces documents avant toute écriture. Aucun code Python, référentiel natif ou ancienne preuve n’est remplacé par un paquet d’adoption. Les liens de lecture, la publication et la version sont mis à jour par la commande.

Une modification concurrente des entrants ou d’un fichier cible bloque l’application. L’écriture utilise un verrou et un journal. En cas d’erreur, les octets précédents sont restaurés. Après une interruption brutale :

```powershell
python -m tools.adopt_core recover
```

Tant qu’un journal est en attente, un nouveau chargement du modèle est bloqué. Les simulations déjà chargées restent utilisables. La récupération refuse d’écraser des modifications étrangères à l’adoption. Le plan et son journal restent disponibles sous `tmp/core-adoptions/`. `--refresh` reconstruit une seule livraison après la validation et l’application. Un échec de livraison est signalé séparément d’une adoption déjà appliquée. Aucune commande ne committe ni ne pousse sur GitHub.

Les tests des montants courants lisent `test_support.active_reference()`. Son pointeur unique est `tools/fixtures/active-adoption.json`, avec l’empreinte d’une référence figée liée à la décision adoptée. La commande renouvelle ce pointeur et sa référence dans la même transaction. Les exemples arithmétiques indépendants et les décisions historiques restent distincts des valeurs actives.
