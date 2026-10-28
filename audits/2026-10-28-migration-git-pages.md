# Déplacement, initialisation Git et GitHub Pages

Le projet actif est `C:/Dev/FLOW-Etude-Economique`. Les 675 fichiers utiles (157 143 056 octets) ont été comparés par SHA-256 à l’original avant les adaptations Pages : aucune absence ni différence. Les sources, preuves, archives et résultats existants sont conservés. Les dépendances pnpm ont été réinstallées avec le verrou existant afin de reconstruire leurs liens au nouveau chemin.

L’ancien emplacement ne contient plus le projet. Il conserve uniquement un `AGENTS.md` de renvoi pour la conversation Codex qui était déjà ouverte. Les chemins des deux skills d’évaluation ont été actualisés. L’ancien serveur de prévisualisation sur 8767, qui retenait les journaux du dossier, a été identifié et arrêté ; le serveur courant a été relancé et vérifié sur 8766 depuis C:/Dev.

Le dépôt est [laurent-sintes/FLOW-Etude-Economique](https://github.com/laurent-sintes/FLOW-Etude-Economique). L’utilisateur a explicitement choisi de rendre **le dépôt complet et l’application publics**, après le refus de GitHub Pages sur le dépôt privé par son offre GitHub. La branche est `main`.

## Application statique

La version Pages utilise les mêmes données et le même moteur Python que le serveur local. Les lectures sont exportées, et les calculs ainsi que les extraits documentaires s’exécutent dans un Web Worker Pyodide. Aucun calcul économique divergent n’est introduit en JavaScript. Les pièces déclarées conservent leurs octets et empreintes ; les données et le moteur sont servis sous des URLs versionnées.

Le build Pages va dans `app/dist-pages/`, séparément du build local `app/dist/`. La publication passe par `.github/workflows/pages.yml` après tests du modèle, de l’interface et du vrai navigateur statique. Les cas de parité en CI sont dérivés des hypothèses courantes ; aucune valeur historique n’est érigée en contrainte économique permanente.

## Contrôles avant initialisation

- Suite complète : 245 tests Python réussis, tests JavaScript, TypeScript, contenu et build réussis.
- Six scénarios historiques préservés et écart nul pour les cinq options.
- Navigateur statique : 13 routes en desktop et mobile, six cas frais strictement identiques au moteur Python, isolation de la référence et erreurs de version contrôlées.
- Preuves YAML, Markdown et PDF, clavier, paramètres personnels, sauvegarde et rechargement vérifiés.
- Aucun paramètre, montant, contrat ou clé de stockage personnel modifié. Le changement d’origine entre localhost et GitHub Pages implique un transfert des scénarios par l’import/export existant.

Le [relevé de contrôle](2026-10-28-migration-git-pages-controles.json) conserve les résultats locaux. La réussite du push et du déploiement est vérifiée séparément sur le commit envoyé.

## Skill Git

Le skill versionné `skills/flow-economie-git/` est installé dans les skills personnels et validé. **commit** reste local, **push** transmet les commits existants et suit Pages, **commit et push** enchaîne les deux. Les sources et preuves sont versionnées, les caches/dépendances/artefacts restent locaux. `.gitattributes` préserve les octets sans conversion de fin de ligne.

## Adaptation au premier checkout GitHub

Le premier run a identifié deux prérequis masqués par le poste local : les tests HTTP nécessitent une compilation locale préalable, et la vérification de la cartographie vivante référence un autre projet Windows. Le workflow construit désormais l’interface avant les tests. La capture versionnée reste contrôlée partout ; la comparaison avec le fichier d’origine s’exécute lorsque ce fichier est disponible. Ces ajustements portent sur la validation et ne changent aucune donnée économique.
