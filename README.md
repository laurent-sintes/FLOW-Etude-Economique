# Étude économique FLOW

L’étude compare trois Make — Java / Spring, .NET, Rust — et deux Buy — Microsoft Dynamics 365 + K3 et SAP. Elle aide à décider des voies et conditions de réalisation du Core System, première étape d’une plateforme de marques, en distinguant périmètres, hypothèses et prix documentés. La Plateforme Flow désigne le produit métier construit en Make. Le calendrier part d’un départ commun, avec comparaisons à 3, 5, 7 et 10 ans.

L’application s’ouvre sur la **Vue d’ensemble** du Framework. Le parcours sponsor relie ambition, entrants, conditions de réalisation et jalons de décision sur dix ans. Le menu distingue **Données d’entrée** (Repères Synvance et pièces originales), **Framework d’évaluation** (concepts, critères, méthodes et formules), **Capacité de réalisation** (organisation, points chauds et preuves à réunir) et **Dossier économique** (analyses, hypothèses, résultats et simulations). Les références eXalt encore absentes sont signalées comme telles. Les simulations personnelles ne changent pas la référence.

| Besoin | Référence |
|---|---|
| Données, propriétaires et calcul | [Guide du modèle](source/README.md) |
| Démarrer, contrôler, actualiser | [Commandes](tools/README.md) |
| Règles de travail | [AGENTS.md](AGENTS.md) |
| Interface et charte | [Application](app/README.md), [charte](app/BRANDING.md) |
| Définitions | [Glossaire](source/glossaire.md) |
| Audit de simplification | [Audit complet](audits/2026-10-27-audit-modele-complet.md) |
| Simplification appliquée et vérifiée | [Réalisation et preuves](audits/2026-10-27-refonte-modele-application.md) |

**Un seul flux de travail :** les sources courantes dans `source/` et `config/` alimentent l’application locale. Après modification et contrôle, relancer `tools/start_study_app.ps1 -NoOpen` pour charger un ensemble cohérent. Aucun choix de mode ni publication intermédiaire. `release/current.json` reste un instantané technique facultatif, sans autorité sur l’application courante.

Les anciens exports Excel sont retirés. Les classeurs fournisseur restent dans `sources/` comme preuves ; aucun Excel ne constitue la référence active. Les anciennes notes encore citées restent des preuves datées, sans autorité sur le calcul courant.

## Projet, Git et application en ligne

- Répertoire de travail : `C:/Dev/FLOW-Etude-Economique`.
- Dépôt public : [laurent-sintes/FLOW-Etude-Economique](https://github.com/laurent-sintes/FLOW-Etude-Economique).
- Application : [GitHub Pages](https://laurent-sintes.github.io/FLOW-Etude-Economique/).
- Branche de travail : `main`. Un push déclenche les contrôles puis le déploiement Pages.

Le skill [flow-economie-git](skills/flow-economie-git/SKILL.md) distingue **commit** (local), **push** (commits existants) et **commit et push**. Les dépendances, caches et artefacts compilés ne sont pas versionnés ; les sources, preuves et audits utiles le sont. Les octets d’origine sont préservés par `.gitattributes`.

GitHub Pages utilise le même moteur Python que l’application locale, exécuté dans le navigateur par Pyodide. Les calculs personnels restent dans le navigateur ; aucune API distante ne reçoit les paramètres de simulation. L’application complète et ses pièces déclarées sont publiques.

Les sauvegardes locales et celles du site sont séparées par l’origine du navigateur. Utiliser l’export/import existant pour transférer un scénario. Le serveur local reste disponible sur `http://127.0.0.1:8766`, lancé depuis ce répertoire :

```powershell
powershell -ExecutionPolicy Bypass -File tools/start_study_app.ps1 -NoOpen
```

La compilation locale reste dans `app/dist/` ; le site publié est construit séparément dans `app/dist-pages/`. Voir [les commandes de construction et de vérification](tools/README.md#github-pages).
