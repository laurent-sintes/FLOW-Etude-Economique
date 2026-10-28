# Simplification appliquée — 27 octobre 2026

La release courante est publiée dans `release/current.json` et servie sur le port local 8766. Le brouillon reste dans `source/` et `config/`. Il n’y a pas de nouvelle chaîne d’historisation.

## Résultat mesuré

| Opération | Audit initial | Après simplification |
|---|---:|---:|
| Charger le modèle éditable | 70,35 s | 1,89 s |
| Contrôle rapide avec parité sur six cas | — | 4,00 s |
| Contrôle éditorial seul | — | 0,93 s |
| Vérification complète, build et publication | — | 31,69 s |
| Réponse initiale, JSON non compressé | 23,54 Mo | 5,83 Mo |

Mesures locales ponctuelles, sans garantie de cache disque froid. Le contrôle complet inclut 101 tests Python, les 33 tests JavaScript, TypeScript, le contrôle de contenu et le build Vite. Les détails sont dans les [preuves de publication](2026-10-27-simplification-application-preuves.json). Le dernier relevé courant remplace `tmp/check-model-last.json`.

## Simplifications réalisées

- Chargement YAML accéléré avec rejet des clés dupliquées, cache borné à un chargement, copies isolées et vérification des modifications concurrentes.
- Calcul économique effectué une seule fois puis réutilisé. Entrées de financement compilées ; les simulations et le calendrier ne lisent plus les fichiers.
- Suppression du chemin Make historique dans la projection active et de l’affectation temporaire du repère SAP au budget Make. Le calendrier pur reçoit le journal de financement courant.
- Suppression des contrôles actifs portant sur les anciens blocs Core remplacés par la calibration métier. Les fichiers originaux utiles aux prix et preuves restent conservés.
- Carte transportée par identifiants ; les lectures résolvent les mêmes nœuds et partagent les mêmes lignes. Les descriptions, variantes, rapprochements et sources restent accessibles.
- Bootstrap préparé une fois côté serveur ; assets portant une empreinte mis en cache. Configuration Excel chargée seulement lorsqu’un export la demande.
- Tests HTTP séparés des tests économiques ; fixture d’étude commune avec copies isolées. Les anciens tests de conservation intégrale de versions obsolètes sont remplacés par des invariants courants. La parité d’une refactorisation est un contrôle explicite, pas une contrainte permanente sur l’économie.
- `AGENTS.md` réécrit comme contrat courant ; l’ancien texte reste une pièce d’audit, sans rôle prescriptif. Les commandes courantes sont documentées dans [tools/README.md](../tools/README.md).

## Brouillon et release

La release contient les entrées nécessaires au calcul des simulations, les résultats de référence, les textes et preuves figés. Les pièces binaires originales sont identifiées par empreinte. Une modification du brouillon ne change ni les calculs ni les preuves de la release. Un moteur incompatible impose une nouvelle publication contrôlée.

La publication remplace un seul fichier atomiquement, après les contrôles. Une erreur ne remplace pas la release précédente. Le serveur démarre par défaut en release ; `-Mode draft` charge le brouillon explicitement. L’en-tête indique le mode. Le passage entre modes sur le même port conserve le stockage navigateur.

```powershell
python -m tools.check_model --quick
python -m tools.check_model --content
python -m tools.check_model --release --publish
powershell -ExecutionPolicy Bypass -File tools/start_study_app.ps1 -Restart -Mode release -NoOpen
```

Pour travailler sur le brouillon, remplacer `release` par `draft` dans la dernière commande. Le serveur garde un modèle cohérent jusqu’au prochain redémarrage explicite.

## Conservation des chiffres et simulations

Le [témoin de parité](2026-10-27-simplification-parite.json) couvre la référence et cinq variantes : durée du build, services Core, inflation cloud, durée Buy et bonus du repère SAP. La comparaison intégrale des résultats, hors identifiant technique de version, est exacte pour les cinq options, les annuités et les quatre horizons. Elle est passée sur le brouillon et sur la release rechargée.

Le contrat sémantique des paramètres est identique. Les tests de session, imports et scénarios nommés utilisent aussi le bootstrap réellement construit par le lanceur ; horizon, option, nom, paramètres modifiés et montants absolus sont conservés. Les anciennes sauvegardes reconnues restent prises en charge ; aucun stockage utilisateur n’a été effacé.

Dans le navigateur : reprise du parcours et de la stack, badge Release, ouverture d’un domaine, d’une capacité et de ses preuves, accès à la comparaison et montants 3/5/7/10 ans vérifiés. La restauration demeure silencieuse. Les chiffres économiques n’ont pas été modifiés.

![Release courante et comparaison conservée](2026-10-27-simplification-release.png)
