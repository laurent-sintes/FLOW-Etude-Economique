---
name: flow-economie-git
description: Exécuter commit, push ou commit et push pour l’Étude économique FLOW et vérifier son déploiement GitHub Pages. Cible exclusivement laurent-sintes/FLOW-Etude-Economique, distinct du projet Etude-d-opportunite-FLOW.
---

# Git de l’Étude économique FLOW

Le dépôt est `https://github.com/laurent-sintes/FLOW-Etude-Economique`, public, avec un site GitHub Pages public autorisé. Le checkout habituel est `C:/Dev/FLOW-Etude-Economique`. Lire `AGENTS.md`, `README.md`, `tools/README.md` et le workflow `.github/workflows/pages.yml` du checkout courant. Ne pas appliquer le workflow d’un autre projet FLOW.

## Choisir l’action demandée

- **commit** : examiner et valider les changements concernés, puis créer un commit local. Ne pas pousser.
- **push** : envoyer les commits existants et vérifier leur déploiement. Ne pas créer de commit implicite ; signaler les modifications locales qui restent hors envoi.
- **commit et push** : enchaîner les deux actions.

La demande de l’action autorise son exécution dans le périmètre indiqué, sans confirmation systématique. Une invocation sans action identifiable nécessite seulement de préciser l’action. Une demande de diagnostic ou de modification du skill n’exécute pas Git.

Le flux courant est `main`, sans branche de brouillon ni release métier. Un push sur `main` déclenche le workflow Pages. Il n’autorise pas un changement de visibilité, de droits ou de domaine. `release/current.json` reste distinct ; ne pas ajouter `--publish` aux contrôles.

## Vérifier le bon dépôt

Lire la racine Git, le statut, la branche, l’upstream et toutes les URL de lecture et d’envoi d’`origin`. Elles doivent cibler exclusivement le dépôt ci-dessus, en HTTPS ou SSH. Ne pas remplacer un remote pour rendre un autre checkout compatible. Une autre branche ou une HEAD détachée doit être résolue selon la demande avant l’envoi sur `main`.

Plusieurs hôtes GitHub sont configurés sur ce poste. Pour `gh api` et `gh auth status`, utiliser explicitement `--hostname github.com`. Pour les commandes qui acceptent `--repo`, fournir `https://github.com/laurent-sintes/FLOW-Etude-Economique`. Ne jamais laisser la sélection basculer vers `beaumanoir.ghe.com`, afficher un jeton ou modifier l’identité Git globale. Vérifier le dépôt public par l’API ; un état différent doit être expliqué par une instruction utilisateur, sans changement automatique de visibilité.

## Valider et committer

Examiner l’index, les différences et les nouveaux fichiers du périmètre. Préserver les changements étrangers et l’index existant ; ne pas les inclure ou les désindexer silencieusement. Respecter `.gitignore` et `.gitattributes` : sources et preuves utiles sont conservées, dépendances et caches restent locaux, les originaux fournisseur ne sont pas réencodés.

Appliquer les contrôles proportionnés de `tools/README.md`, ou réutiliser leurs résultats si les fichiers concernés sont inchangés :

- `python -m tools.check_model --content` pour textes et références.
- `python -m tools.check_model --quick` pour contrats, financements et calendriers.
- `python -m tools.check_model --full` pour le candidat stabilisé, notamment après modification du moteur ou du transport des simulations.

Pour les changements de l’application ou de Pages, suivre aussi les commandes du workflow : construction Vite avec la base `/FLOW-Etude-Economique/`, puis `python -m tools.build_pages --output app/dist-pages --base /FLOW-Etude-Economique/`. Vérifier les parcours affectés et, si le moteur ou son transport change, les simulations dans le navigateur statique face au moteur Python. Les calculs économiques restent dans le même moteur, exécuté par Pyodide sur Pages. Ne pas recalibrer pour faire passer un test et ne pas modifier le contrat de stockage personnel. Un témoin `--preserve` ne s’applique qu’à l’opération à chiffres constants concernée.

Sous Codex Windows, utiliser le runtime et les dépendances isolées décrits dans le guide. Les restrictions de socket ou de dossier temporaire de `--full` se résolvent par les permissions d’exécution adaptées, sans désactiver les tests.

Vérifier `git var GIT_AUTHOR_IDENT`. Indexer les chemins examinés, puis contrôler `git diff --cached --stat` et `git diff --cached --check`. Créer un message français décrivant le résultat ; un fichier UTF-8 sous `tmp/` et `git commit -F` évitent les erreurs PowerShell. Ne pas réécrire un historique ni créer un commit vide. Si rien n’a changé, le signaler et poursuivre l’envoi des commits existants si demandé.

## Pousser et vérifier Pages

Faire `git fetch origin`, examiner les commits à envoyer et la relation avec `origin/main`. Si le dépôt est seulement en retard et propre, avancer en fast-forward. En cas de divergence, intégrer en préservant les commits et les règles du projet ; résoudre les conflits techniques dans le périmètre autorisé et revalider les parties touchées. Une décision métier inconnue nécessite un arbitrage. Ne pas forcer, supprimer une branche distante, envoyer tous les tags ou contourner une protection.

Depuis `main`, pousser explicitement vers `refs/heads/main`. Définir l’upstream si nécessaire. Vérifier que le SHA distant correspond au SHA envoyé, puis suivre le workflow `pages.yml` de ce commit précis. Après déploiement réussi, vérifier l’URL retournée par Pages, son chargement et un parcours utile. Ne pas confondre succès du push et succès du déploiement. En cas d’état réseau incertain, lire la référence distante avant toute relance ; en cas d’échec persistant, conserver le travail local et donner le diagnostic.

Répondre brièvement : action exécutée, commit et sujet, résultat distant, contrôles utiles, état du déploiement et lien du site lorsqu’il est confirmé. Mentionner les modifications restantes sans annoncer une sauvegarde ou un déploiement non vérifié.
