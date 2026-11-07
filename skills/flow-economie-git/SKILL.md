---
name: flow-economie-git
description: Commit et double push de l’Étude économique FLOW vers GitHub personnel et Beaumanoir, avec vérification des deux CI et déploiements Pages. Pour les demandes Git de FLOW-Etude-Economique uniquement, distinct de FLOW-Program, Urbanisation-SCM et Etude-d-opportunite-FLOW.
---

# Git de l’Étude économique FLOW

Checkout habituel : `C:/Dev/FLOW-Etude-Economique`. Lire les consignes courantes dans `AGENTS.md`, `tools/README.md` et `.github/workflows/pages.yml`. Ce skill s’applique uniquement à cette étude.

## Action autorisée

- **commit** : créer un commit local du périmètre examiné, sans pousser.
- **push** : envoyer systématiquement le même commit aux deux dépôts ci-dessous et vérifier les deux déploiements Pages. Ne pas créer de commit implicite. Signaler les changements locaux hors envoi.
- **commit et push** : enchaîner les deux opérations.

La demande autorise l’action dans son périmètre sans reconfirmation. Une demande de diagnostic, de configuration ou de modification du skill ne déclenche ni commit ni push. Ne pas modifier implicitement le modèle métier, sa release, les droits, les domaines ou les visibilités.

## Deux destinations obligatoires

| Remote | Dépôt | Visibilité | Site Pages |
| --- | --- | --- | --- |
| `origin` | `https://github.com/laurent-sintes/FLOW-Etude-Economique.git` | Public | `https://laurent-sintes.github.io/FLOW-Etude-Economique/` |
| `beaumanoir` | `https://beaumanoir.ghe.com/solution-ai/FLOW-Etude-Economique.git` | Interne | `https://solution-ai-flow-etude-economique.pages.beaumanoir.ghe.com/` (privé) |

Pour chaque push, vérifier la racine Git, le statut, `main`, l’upstream et toutes les URL de lecture et d’envoi des deux remotes. Elles doivent cibler exclusivement ces dépôts, en HTTPS ou SSH. Ne pas remplacer un remote incorrect pour rendre un autre checkout compatible. Ne pas envoyer ce projet à FLOW-Program ou Urbanisation-SCM.

GitHub CLI doit être connecté aux deux hôtes. Utiliser explicitement `--hostname github.com` ou `--hostname beaumanoir.ghe.com` pour `gh api` et `gh auth status`. Pour les commandes `--repo`, fournir l’URL complète du dépôt concerné. Ne pas dépendre du compte par défaut, afficher de jeton ou modifier l’identité Git globale. Vérifier les visibilités par l’API sans les changer automatiquement.

## Commit local

Examiner les différences et l’index. Préserver les changements étrangers et les fichiers hors périmètre. Vérifier `git var GIT_AUTHOR_IDENT`. Utiliser le script du projet avec un message français dans un fichier UTF-8 :

```powershell
python -m tools.git_commit prepare --paths <fichiers-examinés> --message-file tmp/commit-message.txt
python -m tools.git_commit commit
```

Le plan vérifie le périmètre, les empreintes, HEAD, l’index et les preuves de validation. `--plan-only` ne permet pas de committer. Ne pas contourner ces contrôles avec `git add -A` ou un commit ad hoc.

La préparation utilise les contrôles incrémentaux légers de `check_dev`. Ajouter `--tests` et éventuellement `--targeted` lorsque le périmètre le nécessite. Ne pas lancer automatiquement de validation complète, de reconstruction Pages ou de régression navigateur complète en local. Les contrôles complets s’exécutent sur chaque GitHub au push. Ne pas créer de commit vide ni réécrire l’historique.

## Double push et suivi

```powershell
python -m tools.git_push prepare
python -m tools.git_push push
```

Utiliser ce workflow plutôt qu’un simple `git push origin`. La préparation contrôle les deux destinations et fixe le SHA ainsi que les références distantes. Elle ne lance pas de tests locaux. Le script conserve les modifications en attente et envoie ce SHA sur les deux `refs/heads/main`, sans forcer ni envoyer tous les tags. Un dépôt Beaumanoir initialement vide est accepté.

Si une branche distante est en avance ou diverge, résoudre la situation en préservant les commits avant de refaire la préparation. Un retard simple avec un checkout propre peut être résolu en fast-forward. Une décision métier inconnue demande un arbitrage. Ne pas supprimer une branche ni contourner une protection.

Les deux envois ne sont pas atomiques. Si un seul réussit, reprendre `python -m tools.git_push push` avec le même plan tant que HEAD et les remotes sont inchangés : le script vérifie les SHA et complète uniquement l’envoi manquant. Si les deux envois sont confirmés mais le suivi a été interrompu, reprendre :

```powershell
python -m tools.git_push watch
```

`push --no-wait` confirme seulement les envois et ne satisfait pas une demande de push complète : poursuivre avec `watch`, sauf instruction explicite de ne pas attendre.

## Critères de réussite des deux hébergements

Ne déclarer la synchronisation et la publication terminées que lorsque :

- Les deux branches distantes `main` portent le SHA préparé.
- Les deux workflows `pages.yml` de ce SHA ont réussi, notamment leurs jobs `deploy`. Les tests complets du modèle, les parcours navigateur et les simulations s’exécutent sur chaque GitHub.
- Sur le site personnel, l’URL Pages correspond au site autorisé et `site-manifest.json` sert le SHA attendu.
- Chez Beaumanoir, l’API authentifiée confirme l’URL Pages autorisée, `public: false`, et un déploiement `github-pages` réussi du SHA exact. Cette preuve API est distincte d’une lecture du manifeste dans un navigateur authentifié : ne pas prétendre l’avoir effectuée si `live_manifest_verified` vaut `false`.

Le workflow construit le site personnel sous `/FLOW-Etude-Economique/` et le site Beaumanoir sous `/`. Garder Vite, le générateur Python et la prévisualisation navigateur alignés sur `FLOW_PAGES_BASE`. L’option `--allow-root` du contrôle navigateur est activée seulement chez Beaumanoir via `FLOW_PAGES_ALLOW_ROOT`.

En cas d’échec, lire les journaux du bon hôte et diagnostiquer avant de relancer. Corriger les erreurs techniques dans le périmètre autorisé, vérifier le correctif puis le committer et le pousser sur les deux dépôts lorsque cette correction est autorisée par la demande. Suivre le nouveau SHA sur les deux GitHub. Ne pas supprimer de tests pour faire passer la CI. Si un droit manquant, une politique d’entreprise ou une décision hors périmètre bloque la suite, conserver le travail et expliquer précisément le blocage, sans modifier les protections ni annoncer un succès partiel comme complet.

## Compte rendu

Indiquer le commit, l’égalité des deux branches, le résultat des deux CI et déploiements, et les deux liens Pages. Préciser l’accès privé Beaumanoir et la nature de sa vérification. Signaler les fichiers locaux restant hors envoi. Une mise à jour de ce skill seule ne publie aucun commit.
