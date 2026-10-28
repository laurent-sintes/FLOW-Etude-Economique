# Mise en œuvre — Framework et dossier économique

28 octobre 2026

Les préconisations de l’[audit de séparation](2026-10-28-audit-separation-framework-dossier-economique.md) sont appliquées. **Synvance et la cartographie restent des entrants du Framework. Les analyses réalisées, les hypothèses retenues et les résultats chiffrés se lisent dans le dossier économique.** Cette règle reste inscrite dans [AGENTS.md](../AGENTS.md).

## Mise en œuvre dans l’ordre de l’audit

| Étape | Résultat |
|---|---|
| 1. Affecter les contenus | Méthodes, conventions et entrants restent dans le Framework. Les constats sur l’application actuelle sont regroupés dans `source/application-framework.yaml`, sans duplication des paramètres ni du statut canonique. |
| 2. Préparer le dossier économique | Les destinations Étude de marché, Hypothèses retenues et Évaluations économiques précèdent Comparer, Se projeter et Simuler. |
| 3. Déplacer les applications Marché et Paramètres | L’étude réalisée conserve les axes, états d’instruction, offres Synvance, six fiches produit, projets et services. Hypothèses retenues conserve toutes les valeurs, justifications et possibilités de simulation existantes. |
| 4. Recentrer le Framework | Les sept pages décrivent la démarche, les notions, les entrants, les formules, les unités, les assiettes et les contrôles. Les tags Build/Run restent dans les Fondamentaux ; la valeur de répartition du MCO Beaumanoir se lit dans les hypothèses. La page Leviers et conventions de calcul décrit les variables sans reprendre leurs valeurs choisies. |
| 5. Clarifier les termes et les liens | Le taux de gain est défini comme une réduction de l’effort à périmètre et qualité constants. Traçabilité et contrôle sont distingués de validation empirique. COCOMO reste un diagnostic nominal de reconstruction, sans calibration FLOW. Les bornes restent des hypothèses sans probabilité. Le glossaire, les titres et les guides sont harmonisés. |
| 6. Vérifier la lecture et la conservation | Suite complète, parité des simulations, contrôle des données affichées, navigation, sources, clavier et rendus sur ordinateur et mobile. |

## Parcours livré

**Framework d’évaluation — sept pages :** Vue d’ensemble, Fondamentaux du modèle, Méthode de l’étude de marché, Estimation du développement Make, Des charges au budget, Calculer le fonctionnement et sa part Run, Leviers et conventions de calcul.

**Dossier économique — six pages :** Étude de marché, Hypothèses retenues, Évaluations économiques, Comparer, Se projeter, Simuler.

La page Évaluations économiques présente la construction Make, la sélection-contractualisation Buy, l’intégration des cinq options et leur base annuelle de fonctionnement. Elle réutilise les montants calculés, avec leurs propriétaires et leurs limites. Aucune nouvelle charge ni ventilation monétaire Build/Run n’est créée.

Les routes existantes restent compatibles. `#marche` conserve la méthode, `#parametres` désigne les hypothèses et `#evaluation-core` accueille les évaluations élargies. Les routes `#leviers` et `#etude-marche` complètent ce parcours. Les pages revues restent en lecture continue, sans accordéon ajouté.

## Vérifications

- **240 tests Python réussis**, puis tests d’interface, contrôle TypeScript, contrôle éditorial et compilation réussis.
- **Six scénarios strictement conservés**, sur le témoin enregistré avant l’opération. Contrat de simulation inchangé. Écart nul pour les cinq options à dix ans ; la parité porte aussi sur les résultats complets et les autres horizons des six scénarios.
- **13 routes contrôlées à 1440 et 390 pixels**, avec groupes de navigation de sept et six pages, sommaires au clavier et tableaux défilables.
- **2 365 champs numériques ou états élémentaires de la référence conservés**, ainsi que les projections des hypothèses, du marché et de la complexité.
- Conservation de **six fiches produit, quinze références de projets, quinze références de services et quinze observations**. Affichages comparés aux données du témoin, sans recalibration.
- Tableaux économiques vérifiés contre leurs propriétaires : trois constructions Make, deux sélections Buy, cinq intégrations et cinq postes annuels par option.
- Consultation des preuves YAML et PDF et retours de focus vérifiés. Aucune erreur JavaScript. Une requête de favicon absente, déjà existante, reste sans incidence sur les pages.

La commande complète a été exécutée sans publication :

```text
python -m tools.check_model --full --preserve audits/2026-10-28-separation-framework-parite.json
```

Le [témoin de parité](2026-10-28-separation-framework-parite.json) et le [relevé des contrôles](2026-10-28-separation-framework-controles.json) documentent cette opération. Les scripts et captures de vérification sont dans `tmp/separation-framework/`. Le témoin protège cette refonte ; il ne fige pas les futures évolutions économiques autorisées.

L’application locale a été reconstruite et actualisée sur son port habituel. Le contrôle de santé confirme des sources courantes et une empreinte de compilation identique au fichier servi. Aucun commit, push ou nouvel instantané de release n’a été produit.
