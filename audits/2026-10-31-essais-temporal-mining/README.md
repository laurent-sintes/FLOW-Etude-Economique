# Essais ciblés Temporal / PM4JS / Superset — 31 octobre 2026

La conclusion et le cumul sont dans [le rapport](rapport.html). Le modèle actif référence `technical-evidence.json` par empreinte. Cette preuve est aussi incluse dans le téléchargement unique du modèle métier ; son archive gzip/base64 conserve les programmes, les contrôles et les historiques. Les captures PNG servent à la relecture visuelle dans ce dossier.

Les 78 contrôles sont des exécutions sur des données fictives, dont certaines répétées avec cache. Ils ne constituent ni un taux de couverture des exigences ni un indicateur de confiance du chiffrage. Aucun JH ne vient de la durée ou du nombre de lignes de ce prototype. Les décisions adoptées restent distinctes de la proposition.

## Environnement isolé utilisé

- Java 21 ; Spring 6.2.12 avec BOM Spring Boot 3.5.7.
- Temporal SDK et temporal-testing 1.36.0 ; CLI officielle 1.9.1, serveur local de développement avec SQLite persistant.
- PM4JS au commit indiqué dans `runtime-provenance.json`.
- Apache Superset 6.1.0 sur Python 3.12, avec les contraintes officielles conservées dans `sources/superset-base-requirements.txt`.
- SDK embarqué Superset 0.4.0, provenance et empreinte dans `sources/superset-embedded-sdk.json`.
- Chrome piloté avec Playwright ; aucun navigateur utilisateur ni aucune sauvegarde personnelle n’est effacé.

Les runtimes, bases locales et secrets sont sous `tmp/targeted-runtime`, hors des sources et du téléchargement. Ne pas copier la configuration réelle de Superset dans les preuves. Les versions déployables en production restent à qualifier ; ces témoins n’imposent pas une version globale de la stack.

## Rejouer les témoins

Toutes les commandes partent de la racine `C:/Dev/FLOW-Etude-Economique`. Les programmes du dossier utilisent les chemins locaux isolés. Une reproduction ailleurs doit les adapter.

1. Installer les versions épinglées dans un environnement isolé et conserver les empreintes. Pour Superset, employer les versions de son fichier officiel de contraintes : une installation avec les toutes dernières dépendances transitives a échoué avant ces essais.
2. Configurer Superset avec une base de métadonnées SQLite locale, des clés aléatoires locales conservées entre processus, `EMBEDDED_SUPERSET` et `DASHBOARD_RBAC` activés, le rôle invité `Gamma`, CSRF activé, les caches locaux `SimpleCache`, et les seules origines de cadrage `http://127.0.0.1:18980` et `http://127.0.0.1:18989`. Le mode HTTP local et la base SQLite sont propres au témoin. Initialiser ses migrations et rôles avec les commandes officielles `superset db upgrade` puis `superset init`.
3. Compiler et tester le projet Maven `temporal/pom.xml` ; construire aussi son classpath avec `dependency:build-classpath`. Les 11 tests déterministes et de rejeu doivent passer.
4. Démarrer la CLI Temporal sur `127.0.0.1:18973` avec `server start-dev --headless --db-filename ...`, puis `flow.trial.TrialPortal` sur `127.0.0.1:18980`.
5. Exécuter `live-temporal.py`. Puis arrêter uniquement les deux processus du témoin et les relancer sur les mêmes fichiers. `durable-restart.py` vérifie le dossier en attente et la conservation du début de son historique. Il ne démontre pas un basculement de cluster.
6. `mining.cjs` projette les historiques de `results/live`, exerce les vrais algorithmes PM4JS et produit `mining-events.json` et `mining-metrics.json`. Les historiques enregistrés A et B permettent de rejouer cette étape sans serveur Temporal actif.
7. Avec `SUPERSET_CONFIG_PATH` défini vers la configuration locale, exécuter `superset-trial.py` dans le venv. Le programme crée les jeux fictifs, les graphiques et le tableau, puis appelle les vraies API de Superset via son client HTTP intégré. Il contrôle aussi les mesures PM4JS restituées exactement, les accès et le cache.
8. Lancer `superset-http.py`, puis `browser.mjs`. Le navigateur publie un parcours, valide une tâche et vérifie l’iframe réelle, les deux organisations et le renouvellement du jeton avec le SDK officiel. Le fournisseur d’identité est une simulation explicite, pas une implémentation SSO.

Les résultats archivés sont ceux des essais réellement exécutés. Rejouer écrit de nouveaux résultats. `compose-evidence.py` fige une nouvelle preuve ; changer sa référence dans le modèle constitue une nouvelle révision à contrôler, pas une modification silencieuse de l’ancienne preuve.

## Résultats qui ont guidé les itérations

Le premier remplacement du worker avec le service de test en mémoire est resté en attente. Le résultat en échec est conservé dans `results/temporal-iteration-02.txt`. L’exigence de reprise a ensuite été éprouvée sur le vrai serveur officiel persistant ; le test unitaire porte désormais sur le rejeu d’un historique encore en attente. Le passage sur serveur réel ne transforme pas l’échec initial en succès rétroactif.

Temporal réessaie une activité ; le récepteur doit donc traiter les doublons. PM4JS fournit les algorithmes ; la projection métier et les modèles de conformité restent à Flow. Un graphe de successions ne caractérise pas à lui seul les tâches parallèles. Superset applique les filtres associés aux jetons et sépare leur cache ; Flow doit imposer ces filtres côté serveur et exposer des jeux de données autorisés. Les essais comportent des contrôles négatifs montrant les conséquences de leur absence.

Les studios complets, l’ergonomie métier, les migrations arbitraires d’instances ouvertes, l’authentification réelle, la haute disponibilité et les objectifs de volume restent à éprouver. Le désaccord COCOMO / COSMIC × ISBSG et les fractions de code par analogie ne sont pas calibrés par ces essais.
