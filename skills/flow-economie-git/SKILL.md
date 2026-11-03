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

Utiliser le script du projet pour le chemin courant, après examen des fichiers concernés :

```powershell
python -m tools.git_commit prepare --paths <fichiers-examinés> --message-file tmp/commit-message.txt
python -m tools.git_commit commit
```

Le plan conserve le périmètre explicite, les empreintes, HEAD, l’index et les preuves de validation. Une prévisualisation `--plan-only` reste non exécutable pour un commit. Le script réutilise les contrôles strictement valables, conserve l’index hors périmètre et ne pousse rien. Ne pas utiliser un appel ad hoc à `git add -A` pour contourner son contrôle de périmètre. La procédure détaillée ci-dessous reste le repli de diagnostic.


Examiner l’index, les différences et les nouveaux fichiers du périmètre. Préserver les changements étrangers et l’index existant ; ne pas les inclure ou les désindexer silencieusement. Respecter `.gitignore` et `.gitattributes` : sources et preuves utiles sont conservées, dépendances et caches restent locaux, les originaux fournisseur ne sont pas réencodés.

Au commit local, utiliser uniquement `python -m tools.git_commit prepare --paths <fichiers-examinés> --message-file tmp/commit-message.txt`, puis `python -m tools.git_commit commit`. La préparation lance les contrôles incrémentaux légers de `check_dev`. Compléter par `--tests` et éventuellement `--targeted` pour un périmètre inconnu ou une sélection explicite. Aucun test complet, reconstruction Pages ou régression navigateur complète automatique en local. Les contrôles complets sont exécutés sur GitHub au push. En local, `python -m tools.check_model --full` et `--full --browser` restent disponibles sur demande explicite.

Vérifier `git var GIT_AUTHOR_IDENT`. Indexer les chemins examinés, puis contrôler `git diff --cached --stat` et `git diff --cached --check`. Créer un message français décrivant le résultat ; un fichier UTF-8 sous `tmp/` et `git commit -F` évitent les erreurs PowerShell. Ne pas réécrire un historique ni créer un commit vide. Si rien n’a changé, le signaler et poursuivre l’envoi des commits existants si demandé.

## Pousser et vérifier Pages

Utiliser le script pour l’envoi des commits déjà validés :

```powershell
python -m tools.git_push prepare
python -m tools.git_push push
```

Le plan fixe le SHA et la référence distante. Le script conserve les modifications et l’index en attente, envoie uniquement ce SHA sans tests locaux. GitHub produit les témoins et valide ce commit. Il ne crée pas de commit et ne force jamais. Un retard ou une divergence se résout avant de refaire la préparation, selon les règles ci-dessous.

`push --no-wait` confirme uniquement l’envoi. `python -m tools.git_push watch` suit ensuite le workflow exact, le job de déploiement, le SHA publié dans le manifeste après validation complète et simulations navigateur sur GitHub. Aucun navigateur local n’est lancé par le suivi. Après une interruption, reprendre `watch` au lieu de renvoyer les commits. Une demande de scripting seule n’exécute pas le push.


Faire `git fetch origin`, examiner les commits à envoyer et la relation avec `origin/main`. Si le dépôt est seulement en retard et propre, avancer en fast-forward. En cas de divergence, intégrer en préservant les commits et les règles du projet ; résoudre les conflits techniques dans le périmètre autorisé et revalider les parties touchées. Une décision métier inconnue nécessite un arbitrage. Ne pas forcer, supprimer une branche distante, envoyer tous les tags ou contourner une protection.

Depuis `main`, pousser explicitement vers `refs/heads/main`. Définir l’upstream si nécessaire. Vérifier que le SHA distant correspond au SHA envoyé, puis suivre le workflow `pages.yml` de ce commit précis. Après déploiement réussi, vérifier l’URL retournée par Pages et le SHA du manifeste publié. Les tests des parcours et simulations sont exécutés sur GitHub. Ne pas confondre succès du push et succès du déploiement. En cas d’état réseau incertain, lire la référence distante avant toute relance ; en cas d’échec persistant, conserver le travail local et donner le diagnostic.

Répondre brièvement : action exécutée, commit et sujet, résultat distant, contrôles utiles, état du déploiement et lien du site lorsqu’il est confirmé. Mentionner les modifications restantes sans annoncer une sauvegarde ou un déploiement non vérifié.
