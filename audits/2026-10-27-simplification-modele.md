# Audit — rapidité, simplification et états brouillon / release

**Conclusion : oui, le modèle s’est construit par sédimentation. Mais le premier ralentissement mesuré vient des relectures YAML, davantage que des formules économiques.** Ajouter une nouvelle suite de tests sans corriger le chargement reproduirait ce problème. La cible recommandée est un modèle chargé et validé une fois, un calcul sans accès aux fichiers et deux états métier : brouillon et release.

Audit sans modification des données, calculs actifs, serveur ni interface. L’essai de cache a été limité à un processus Python distinct. Aucun contrôle général ni nouvelle recherche externe n’était nécessaire pour établir ces constats.

## 1. Ce qui prend réellement du temps

Mesure locale d’un chargement complet, d’une simulation de référence et de la sérialisation de la réponse initiale. Même code économique, mêmes données ; seconde variante avec mémorisation des fichiers YAML et retour de copies indépendantes.

| Opération | Actuel | Cache expérimental | Observation |
|---|---:|---:|---|
| Construire `Study` | 70,35 s | 12,60 s | Environ 82 % de temps en moins |
| Simuler sur l’étude chargée | 2,088 s | 0,026 s | Environ 81 fois plus rapide dans cet essai |
| Sérialiser le bootstrap | 0,228 s | 0,167 s | Ce n’est pas le premier coût serveur |

Le chargement appelle **807 fois** le lecteur YAML pour **58 fichiers distincts**. Ces lectures et leur décodage absorbent **67,27 s**, soit environ **96 %** du chargement mesuré. La calibration métier est relue 30 fois, la grille 26 fois, la qualification Buy 39 fois. Chaque simulation relit encore 27 fois 17 fichiers.

Les empreintes SHA-256 du bootstrap complet et du résultat simulé sont identiques entre les deux variantes. Ce résultat prouve un gain possible sans modification des chiffres ; il ne valide pas encore une implémentation de cache pour tous les cas d’édition et de concurrence.

**Limites de mesure :** un passage par variante, séquentiel, sans garantie de cache disque froid ; durées instrumentées, pas un benchmark statistique. Le temps total du travail précédent inclut aussi les analyses, corrections, builds, reprises de tests et manipulations du navigateur. Il serait incorrect de l’attribuer entièrement à ces 70 secondes.

Preuves : [mesures](2026-10-27-performance-modele-mesures.json), [script reproductible](2026-10-27-performance-modele-mesure.py), [inventaire](2026-10-27-performance-modele-inventaire.json).

## 2. Constats et priorités

### P1 — Charger, valider et calculer sont aujourd’hui entremêlés

`Study.__init__` appelle `prepare()`, qui appelle `calculate()`, puis appelle à nouveau `calculate()`. Ce calcul produit les cinq options et leurs sensibilités basse/haute. `active_doc()` reconstruit et valide la calibration ; plusieurs fonctions l’appellent pour une seule option. `business_calibration.validate()` contrôle déjà Buy, puis `apply()` le contrôle encore.

La fonction commune `validate_stacks.read()` relit et analyse intégralement chaque fichier, sans réutilisation. Elle utilise un chargeur Python dérivé de `SafeLoader`, alors que LibYAML est disponible dans l’environnement observé. Un chargeur C avec rejet des clés dupliquées pourrait compléter l’amélioration ; son gain n’a pas été mesuré ici et sa compatibilité doit être testée.

**Action :** construire un objet de modèle une seule fois, avec ses index et tarifs. Valider cet objet au chargement. Réutiliser le résultat économique pour préparer la projection et les lectures. Les variations de scénario ne doivent exécuter que les formules et contrôles des paramètres.

### P1 — Une simulation peut mélanger l’étude chargée et des fichiers modifiés ensuite

`Study` mémorise sa version et une partie de ses données au démarrage. Mais `project()` appelle `initial_ledger()`, qui relit directement les YAML pendant chaque simulation. Une modification de ces fichiers entre deux requêtes peut donc influencer un calcul sans changer la version déjà mémorisée par le serveur.

Ce risque est établi par le chemin de code ; aucune modification concurrente des sources n’a été provoquée pendant l’audit. C’est aussi une raison de **ne pas ajouter seulement un cache global implicite**.

**Action :** rendre le calcul indépendant des fichiers. Une requête utilise un seul objet de modèle cohérent. En brouillon, le rechargement construit un nouvel objet, le valide, puis remplace l’ancien en une fois. En cas d’erreur, il conserve le dernier objet valide et signale que les dernières modifications ne sont pas chargées. En release, aucun YAML de travail n’est relu pour simuler.

### P1 — Les tests existent, mais certaines vérifications sont devenues historiques

Il existe **98 méthodes de test Python dans neuf modules**, plus les tests JavaScript. Il manque surtout une commande cohérente, des fixtures réutilisables et une séparation des responsabilités.

- Trois classes de tests reconstruisent chacune `Study`. Les autres recréent aussi des préparations économiques. Le coût initial est ainsi payé plusieurs fois.
- `StudyTests.setUpClass()` démarre un serveur HTTP même pour les tests qui ne vérifient que des contenus ou calculs. Cela impose inutilement un port et les permissions réseau locales.
- Deux tests de `test_business_map.py` imposent encore l’égalité intégrale des chiffres et du contrat avec la capture antérieure au modèle composable. La comparaison directe de leurs opérandes renvoie **faux dans les deux cas**. Ces assertions sont incompatibles avec l’évolution autorisée ; leur échec ne signifierait pas que la nouvelle économie est erronée.
- Le contrôle de conservation des centimes et la comparaison à un calcul mensuel indépendant sont utiles. Ils ne doivent pas être remplacés par une simple comparaison de deux sorties du même moteur.

**Action :** distinguer invariants durables, tests de régression de la release courante et tests ponctuels de migration. Sortir les migrations achevées du parcours quotidien, sans supprimer leurs preuves. Les assertions de conservation intégrale ne s’appliquent qu’aux parties qui doivent effectivement rester inchangées.

### P2 — La réponse initiale transporte trop de représentations du même métier

Le bootstrap observé représente environ **23,54 Mo de JSON UTF-8 non compressé**. `content.complexity` occupe 10,10 Mo et `content.business_map` 11,27 Mo : ensemble, environ **91 %** de la réponse. Ce sont des tailles sérialisées, pas une mesure de consommation mémoire ou de latence du navigateur.

La carte métier est devenue une référence commune, mais des structures complètes restent exposées en parallèle pour les anciennes et nouvelles lectures. Le serveur sérialise le bootstrap à chaque requête et annonce `no-store` pour toutes les réponses, y compris les assets Vite portant déjà une empreinte dans leur nom.

**Action :** une seule représentation canonique des capacités et preuves, référencée par identifiants dans les vues. Charger les pièces détaillées à la demande. Préparer la réponse release une fois ; permettre la mise en cache des assets immuables. La compression peut aider au transport, mais elle ne supprime pas les redondances du modèle.

### P2 — Plusieurs générations de modèle coexistent dans la chaîne active

La chaîne actuelle passe par le catalogue économique à quinze années de service, les anciennes structures de chiffrage adaptées par la calibration métier, la projection à dix ans, puis le journal composable. Le repère SAP historique continue à être affecté temporairement au montant d’intégration Make avant d’être remplacé par le journal Groupe. `project()` conserve aussi un chemin Make historique sans modèle composable, notamment pour d’anciens formats d’entrée.

Cela crée des noms et montants intermédiaires ambigus : `mco_run` regroupe désormais plusieurs responsabilités ; `integration_source` ne désigne pas le budget Make courant. `prepare()` charge en outre la configuration de restitution Excel pour une étude servie dans React. Les fichiers anciens contiennent encore des tarifs et offres utiles : les supprimer en bloc casserait la traçabilité et les calculs.

**Action :** conserver les prix, offres et hypothèses nécessaires, mais sortir les anciens formats des fonctions économiques actives. Le journal de financement devient la seule base des cumuls par période et responsabilité. Le repère SAP devient un diagnostic indépendant, sans transit par la variable du budget Make. Le calcul à quinze ans devient un export facultatif, si son utilité est confirmée, pas une étape imposée du démarrage.

### P2 — Les règles de travail portent trop d’historique

`AGENTS.md` contient **535 lignes et environ 168 ko**, avec directives successives, règles remplacées, anciens menus, anciennes unités et anciens flux Excel. `tools/README.md` propose encore une chaîne mêlant contrôles actuels et historiques. Cela augmente le temps d’interprétation et encourage une vérification trop large.

**Action :** réécrire `AGENTS.md` en contrat courant court : modèle canonique, invariants, UX, commandes et conditions de release. Les décisions anciennes restent dans les audits existants, sans rôle prescriptif quotidien. Ne pas ajouter une nouvelle couche de directives pour corriger l’ancienne.

## 3. Un module Python de test, oui — comme point d’entrée unique

Préférer un petit lanceur sur les tests existants à un nouveau framework. Interface proposée, **non implémentée** :

| Commande proposée | Quand | Contenu |
|---|---|---|
| `python -m tools.check_model --quick` | Après modification économique ciblée | Charger une fois ; paramètres, prix groupés, financements uniques, sommes, frontières de phases, horizons et quelques sensibilités pertinentes |
| `python -m tools.check_model --content` | Après modification éditoriale ou de références | Liens, sources, glossaire, références numériques et schémas éditoriaux ; pas de recalcul des cinq options si le modèle économique n’a pas changé |
| `python -m tools.check_model --release` | Juste avant remplacement de la release | Ensemble des contrôles applicables, comparaison à la release courante, contrats de simulation et construction de l’artefact candidat |

Les tests HTTP restent une petite suite distincte, avec une seule instance de serveur. Les tests navigateur portent sur les parcours touchés. Les tests des fonctions pures utilisent de petits cas fabriqués : centime réparti sur une durée fractionnaire, chevauchement de phases, offre incluse, coût inconnu, etc. Un contrôle financier d’intégration utilise le modèle complet chargé une fois.

**À préserver :** valeurs inconnues distinctes des zéros, offres Buy indivisibles, exactitude au centime, absence de double financement, horizons, durées de service, rattachements métier et conservation des paramètres utilisateur. **À éviter :** une seconde implémentation complète du modèle dans les tests ; cela doublerait la maintenance.

Objectifs à vérifier après réalisation, pas performances promises : contrôle rapide en quelques secondes, simulation sans lecture disque, démarrage release sans recalibration générale. Publier les temps par étape pour détecter une régression ; ne pas ajouter une chaîne sophistiquée d’optimisation des tests.

## 4. Deux états suffisent : brouillon et release

Il n’existe pas aujourd’hui de véritable workflow métier brouillon/release. Le mot « brouillon » de l’interface désigne principalement la simulation personnelle. Les empreintes et archives ne constituent pas à elles seules un système de publication.

| | Brouillon de l’étude | Release de l’étude |
|---|---|---|
| Usage | Modifier les hypothèses, travaux et textes | Présenter une référence stable au sponsor |
| Données | Sources éditables actuelles | Un instantané autonome validé |
| Calcul | Même moteur, sur un modèle chargé explicitement | Même moteur, sur l’instantané figé |
| Modification | Autorisée dans les sources | Aucune modification en place : remplacer par la prochaine release |
| Contrôles | Ciblés pendant le travail | Complets une fois avant publication |
| Repère visible | « Brouillon » | « Release du … » |

Organisation minimale proposée :

```text
source/ et config/       brouillon éditable unique
release/model.json      toutes les entrées nécessaires au moteur, figées
release/content.json    lecture sponsor et références de preuve figées
release/manifest.json   date, identifiant, version de format et empreintes
```

Il n’y a qu’**une release courante**, sans arbre de versions, journal d’événements, chaîne de migrations ni copies datées à chaque correction. Les anciens audits restent consultables comme documents. L’historique technique peut relever de Git ; le dépôt observé présente actuellement les fichiers comme non suivis, il ne faut donc pas présumer qu’un retour arrière Git fonctionne déjà. La mise en place de cette sauvegarde serait une opération distincte.

Le candidat est préparé dans un répertoire temporaire. Après succès des contrôles, il remplace la release courante en une opération contrôlée ; un échec conserve la release précédente. Ce répertoire temporaire n’est pas un troisième état métier.

L’instantané doit inclure les entrées nécessaires aux simulations, **pas seulement les résultats de référence**. Sinon, l’utilisateur simulerait encore avec les YAML du brouillon. Les preuves doivent rester cohérentes avec la release : passages cités figés ou pièces originales identifiées par empreinte, et signalement d’une pièce remplacée.

Les simulations personnelles restent des jeux de paramètres, pas des versions du modèle. Un format simple avec numéro de schéma et identifiant de la référence suffit. Conserver un adaptateur explicite pour les sauvegardes déjà utilisées, puis un seul format courant ; ne pas alimenter indéfiniment une liste de hashes compatibles. Une évolution de sens exige une conversion explicite ou un refus récupérable, jamais une perte silencieuse des valeurs.

## 5. Simplification cible du code

Quatre responsabilités suffisent, sans microservices ni système de plugins :

1. **Charger** les sources et résoudre les références en un objet cohérent.
2. **Valider** structure, métier et preuves une fois pour cet objet.
3. **Calculer** les financements, échéances et horizons avec cet objet et les paramètres ; aucune lecture disque ni validation documentaire à chaque formule.
4. **Présenter** les résultats pour le sponsor et produire la release.

Le modèle économique conserve sa richesse utile : capacités, travaux, réemplois, contrats, taux, volumes, calendrier et preuves. La simplification vise les doublons et les chemins de transformation, pas le remplacement des hypothèses par des forfaits opaques. Les vues coût, complexité, couverture et preuve partagent les identifiants de capacité ; les coûts transverses restent identifiables sans ventilation artificielle.

## 6. Ordre de réalisation recommandé

**Lot 1 — accélérer sans changer l’économie.** Chargement unique avec copies ou objets immuables, réutilisation du calcul économique, suppression des lectures disque en simulation, fixture commune, séparation HTTP, point d’entrée de contrôle. Vérifier les résultats des cinq options aux quatre horizons et quelques scénarios non triviaux. Le cache expérimental indique déjà un gain important ; le cache seul est une étape, pas la cible architecturale.

**Lot 2 — rendre le modèle lisible.** Journal de financement unique, SAP diagnostic séparé, suppression des chemins historiques actifs après transfert de leurs données utiles, carte et preuves référencées par identifiants, réponse API allégée. Consolider les tests historiques en invariants et comparaison à la release courante. Réécrire les règles de travail et les commandes.

**Lot 3 — établir brouillon/release.** Sérialiser l’objet complet et les contenus, vérifier le candidat une fois, remplacer la release, afficher l’état et préserver les simulations. Aucune nouvelle formule économique n’est nécessaire pour ce lot.

**À ne pas faire maintenant :** réécriture totale en une fois, suppression des archives ou pièces originales, création d’un système d’historisation, nouvelle batterie de tests redondants, augmentation des délais d’attente du serveur comme solution au chargement lent.

## 7. Améliorer aussi la façon de travailler

La durée précédente n’était pas seulement un problème de code. Les reconstructions et vérifications intermédiaires ont été trop nombreuses. La règle opérationnelle recommandée est : une mesure initiale, des contrôles ciblés après chaque changement significatif, puis une seule vérification complète du candidat stabilisé. Après une correction, rejouer les contrôles qu’elle peut affecter, pas toute la chaîne par réflexe.

Une modification CSS ne justifie pas de recalibrer le modèle ni de redémarrer le serveur Python. Une modification éditoriale ne justifie pas de recalculer les budgets si les données économiques sont inchangées. Préparer ensemble les changements dépendants avant le build et la relecture navigateur. Cette discipline complète la simplification technique ; elle ne nécessite aucun nouveau mécanisme d’historique.

## Repères dans le code audité

- [Chargement et version de l’étude](../tools/study_app.py) : `__init__`, `_files`, `simulate`, `_content`, `simulation_contract`.
- [Préparation et projection](../tools/project_investment.py) : `prepare`, `project`.
- [Calcul historique et sensibilités](../tools/calculate_costs.py) : `validate_inputs`, `calculate`.
- [Lecteur YAML](../tools/validate_stacks.py) : `UniqueKeyLoader`, `read`.
- [Calibration](../tools/business_calibration.py) : `validate`, `apply`, `active_doc`.
- [Journal composable](../tools/composable_costs.py) : `initial_ledger`.
- [Serveur](../tools/serve_study_app.py) : `reply`, `/api/bootstrap`, `/api/simulate`.
- [Tests de l’application](../tools/test_study_app.py), [anciens tests de migration métier](../tools/test_business_map.py), [tests de reprise](../app/scripts/test-composable-migration.mjs).
