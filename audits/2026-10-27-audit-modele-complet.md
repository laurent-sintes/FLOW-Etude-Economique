# Audit du modèle FLOW — simplification, dépendances et documentation

27 octobre 2026 — audit en lecture seule. Aucun changement d’hypothèse, de calcul, de simulation ou de release ; aucun retrait de fichier. L’interface n’est pas auditée.

## Conclusion

**Le modèle peut être sensiblement simplifié. Le principal problème est la coexistence de plusieurs générations de données, et non le nombre de fichiers en lui-même.**

La simplification précédente a accéléré les chargements et installé brouillon / release. Elle n’a pas achevé le nettoyage du modèle : anciens chiffrages encore obligatoires, paramètres remplacés à l’exécution, règles déclaratives non exécutées, conventions économiques dépassées et documentation partiellement alignée.

Le calcul courant est reproductible : les cinq options donnent les mêmes dépenses dans le brouillon et dans la release aux horizons 3, 5, 7 et 10 ans. Cela ne démontre ni la justesse de toutes les hypothèses ni l’absence de champs trompeurs. **On peut aujourd’hui modifier certaines informations présentées comme des hypothèses sans modifier leur calcul.**

Je recommande de conserver le fond métier et les preuves, de retirer les données économiques remplacées, puis de supprimer les dérivés historiques sans utilité restante. Une seule version éditable et une seule release suffisent. Aucun nouveau mécanisme d’historisation n’est nécessaire.

## Périmètre et preuves de l’audit

L’examen couvre la cartographie, les charges Make, les offres et exceptions Buy, les activités client, les services annuels, le déploiement Groupe, les calendriers, l’indexation, les dépendances de calcul, les états brouillon / release, les archives et les documents de référence.

Il combine lecture du code et des YAML, inventaire, empreintes SHA-256, recherche des références explicites, observation d’un chargement économique et essais sur des copies en mémoire. Le collecteur et ses résultats sont conservés avec ce rapport :

- [Script reproductible](2026-10-27-audit-modele-complet.py).
- [Inventaire, consommateurs, doublons et essais](2026-10-27-audit-modele-complet.json).

Repères relevés :

| Ensemble | Observation |
|---|---|
| `source/` | 69 fichiers, dont 64 YAML ; données éditables et résultats générés y cohabitent. |
| Chargement économique | 36 documents YAML effectivement lus, auxquels s’ajoutent des dépendances vérifiées par empreinte. Ce nombre n’inclut pas toutes les lectures éditoriales. |
| Ancien chiffrage Core | 195 lignes, soit 39 pour chacune des cinq options, encore obligatoires. |
| Chiffrage Core effectif | 88 capacités et un transverse pour chaque Make ; aucun développement générique Buy additionnel dans la référence actuelle. |
| Archives / audits existants | 186 fichiers / 61 fichiers, avant les livrables du présent audit. |
| Livrables `output/` et `outputs/` | 160 fichiers, environ 145 Mo ; ce n’est pas le volume supprimable. |
| Doublons exacts | 19 groupes, représentant 49,4 Mo de copies supplémentaires. Leur utilité documentaire reste à qualifier. |
| Release | Un seul `release/current.json`, 99 documents référencés, dont une analyse historique Synvance. |

Les recherches de références sont une borne basse : chemins construits en Python, liens relatifs et usages externes ne sont pas tous identifiables par recherche littérale. L’absence de référence n’autorise donc pas une suppression. Les caches de dépendances sont exclus du rapprochement ; les temporaires sont inventoriés sans lecture exhaustive de leur contenu.

L’audit ne requalifie pas les capacités produit Microsoft/SAP sur Internet, ne reconstitue pas tous les devis originaux et ne mesure pas la validité terrain des hypothèses de charge. Il ne relance pas la suite application, le navigateur ou le build.

## Constats et corrections recommandées

### 1. Les anciens blocs CSF sont inutiles au montant, mais obligatoires au modèle — priorité haute

Dans les cinq `source/chiffrage/chiffrage-*.yaml`, la section `core` conserve 39 blocs CSF. `tools/calculate_costs.py#validate_inputs` valide leur structure et leurs empreintes avant que `tools/business_calibration.py#apply` remplace intégralement ces charges par la calibration métier actuelle.

**Preuve expérimentale :** doubler les charges backend et frontend des 195 lignes laisse les entrées effectives strictement identiques. Vider cette section provoque néanmoins `[] is too short`, car `source/schema-chiffrage.yaml`, lignes 37–38, impose exactement 39 entrées.

Les six fichiers `source/core-system-features.yaml` et `source/solutions/core-system-solution-*.yaml` sont également des dépendances de l’économie par empreinte, sans lecture de leur contenu dans le chargement observé. La grille et les catalogues conservent d’autres renvois à cette génération.

**Correction :** retirer les anciennes sections Core des chiffrages, leurs obligations de schéma et leurs dépendances de calcul ; supprimer les anciens scores et correspondances devenus inutiles après revue des renvois. Conserver seulement les alias historiques nécessaires pour retrouver une preuve ou un ancien lien. Ne pas supprimer les parties intégration, maintenance et prix encore utilisées dans ces mêmes fichiers.

Le rapport précédent indiquait une « suppression des contrôles actifs portant sur les anciens blocs Core ». Cette formulation était trop large : les contrôles de cardinalité et d’empreinte subsistent. Le présent constat précise ce qui reste à faire.

### 2. Le modèle composable déclaré et le modèle exécuté ne coïncident pas entièrement — priorité haute

`source/modele-composable.yaml#classification_make` décrit les responsabilités des activités. Le moteur les affecte à nouveau dans `tools/composable_costs.py#annual_split` et `#initial_ledger`. Modifier en mémoire la responsabilité de MAI-001 de Run vers MCO client ne change pas le journal initial. Il existe donc deux expressions de la règle, dont une seule commande le calcul.

Même problème pour `hebergement_build.cas_central` : le passer de `central` à `soutenu` n’a aucun effet, car le code lit explicitement `couts_mensuels_eur_ht['central']`.

Le contrat décrit aussi des champs français (`montant_eur_ht`, `debut_mois`, `source_refs`) différents des champs réels (`amount`, `start`, `source`). Les cinq responsabilités déclarées ne décrivent pas le compartiment technique `grouped_buy` utilisé par le projecteur. Celui-ci préserve bien le groupement fournisseur ; il faut le nommer comme un montant non ventilé, sans prétendre connaître ses parts Core / Run / MCO.

**Correction :** choisir une seule autorité pour chaque règle. Les classifications simples peuvent être lues depuis le YAML ; les décompositions particulières restent des fonctions nommées et testées. Supprimer les sélecteurs inutilisés ou les rendre effectifs. Décrire exactement les objets réellement calculés, sans construire un moteur générique de règles.

### 3. Les nouveaux contrats laissent passer des données incohérentes — priorité haute

Une erreur concrète existe dans `modele-composable.yaml#classification_make.MAI-008` : la preuve est coupée après « Contrôles opérationnels sécurité » ; la suite devient une clé YAML supplémentaire, de valeur `null`. Le document est valide pour le parseur, mais incorrect pour le modèle attendu. Le chargement économique l’accepte.

Dans le déploiement, nombre d’unités, ouvertures, charges par unité et parts d’usagers ne sont pas contrôlés ensemble. Un essai avec trois parts au lieu de quatre est accepté. Il ne change pas ici le total, car la dernière cohorte atteint la fin de transition ; cette coïncidence ne valide pas la donnée. Le `zip` du moteur peut laisser de côté une entrée sans signalement.

**Correction :** valider les deux documents récents au chargement : clés autorisées, types, responsabilités, sommes de parts, sommes des rôles, longueurs des listes, ordre des jalons, montants positifs ou nuls et références existantes. Dériver le nombre d’unités de leur liste plutôt que le ressaisir. Ces vérifications simples coûtent peu et ciblent un risque réel.

### 4. Les volumes ont plusieurs propriétaires et des résultats dérivés sont saisis — priorité haute

`deploiement-groupe.yaml#perimetre` et `maintenance.yaml#scenario_annuel.perimetre` répètent notamment les 950 utilisateurs, 10 applications, 2 To actifs et 5 To archivés. Le second document conserve à la fois les utilisateurs, demandes par utilisateur, taux d’escalade et les résultats 5 700 / 1 140.

**Preuve expérimentale :** porter les utilisateurs Groupe de 950 à 1 900, ou le nombre déclaré d’unités de 4 à 8, ne change pas le journal initial. Ces champs décrivent le contexte ; les volumes et listes réellement consommés sont ailleurs. Cela ne justifie pas de doubler automatiquement tous les coûts : cela impose de distinguer clairement description, hypothèse calculante et résultat dérivé.

Les égalités utilisateurs → demandes → escalades sont contrôlées dans `tools/validate_cycle.py`, lignes 163–166, mais ce validateur ancien n’est pas appelé par le parcours courant `check_model`.

**Correction :** un propriétaire unique pour chaque volume ; références depuis les autres documents. Calculer les demandes et escalades à partir de leurs paramètres, ou documenter explicitement une estimation indépendante si tel est le choix. Ne pas linéariser automatiquement licences, capacité cloud et charges projet. Les phases transitoire et stabilisée peuvent avoir des cadences différentes : les conserver lorsqu’elles ont un sens explicite.

### 5. Des conventions actives racontent encore l’ancienne économie — priorité haute

| Emplacement | Texte ou état contradictoire | Règle à retenir |
|---|---|---|
| `recalibration-metier.yaml#methode.integration` | Le repère SAP retraité reste la base macro du Make. | La base active est activités + déploiement Groupe ; SAP est un contrepoint. |
| `plan-investissement.yaml#sensibilite_finance_sap.statut` | `utilise_comme_ancre_make` | Contrepoint uniquement ; le bonus ne réduit pas le budget Make actif. |
| `calibration-couts.yaml#convention.lots` | « Make en un lot » | Distinguer construction du produit et quatre unités proposées de déploiement client. |
| `calibration-couts.yaml#convention.preparation` | Forfait sans durée et impossibilité de chiffrer le décalage. | Le calendrier composable finance désormais les consommations pendant build et intégration. |
| `maintenance.yaml#pilotage_global` | Non chiffré, aucun rôle de direction tarifé disponible. | Des taux de pilotage existent dans la calibration et le programme Groupe dispose de rôles tarifés ; préciser les assiettes. |

**Correction :** réécrire ces conventions autour de la référence actuelle et de ses exclusions. Retirer les passages remplacés, sans ajouter une nouvelle série de paragraphes « avant / après ». Les propositions non validées restent identifiées comme hypothèses d’opportunité.

### 6. Les charges annuelles sont encore corrigées par superposition — priorité moyenne

Les chiffrages conservent des valeurs de maintenance que `business_calibration.py#apply` remplace, notamment correction Core, correction extension, qualification client et évolution Core. `load_funding_model` charge pour sa part les activités brutes et une autre copie de la calibration ; `initial_ledger` réapplique certains remplacements pour la transition.

**Risque :** modifier la première valeur visible et ne constater aucun effet, ou faire diverger la transition et le service stabilisé.

**Correction :** compiler une seule fois les travaux annuels effectifs. Les calendriers transitoire et stabilisé consomment ces travaux avec leurs volumes et périodes propres. Remplacer les champs écrasés par des références, puis les retirer du schéma éditable. Ne pas confondre cette unification avec l’égalisation des coûts entre phases.

### 7. Le calcul à quinze années de service reste un passage obligatoire — priorité moyenne

`project_investment.prepare()` appelle `calculate_costs.calculate()`. Celui-ci construit cinq options, leurs sensibilités basse/haute et quinze annuités ; `validate_inputs` impose `maintenance_ans == 15`. La projection sponsor réutilise les prix, charges et premières annuités avant de calculer son propre calendrier sur dix ans.

Le fichier généré `source/couts-15-ans.yaml` n’est pas relu comme source par ce chemin. En revanche, **le calcul intermédiaire à quinze ans reste obligatoire**. Dire simplement « les quinze ans sont un export » masque cette dépendance.

**Correction :** isoler la valorisation des travaux, les services annuels et les séquences contractuelles ; faire consommer ces données par le calendrier courant. Conserver le quinze ans comme export facultatif seulement s’il a encore un lecteur identifié. Préserver les conventions d’indexation et d’annuités Buy, qui ne sont pas des historiques inutiles.

### 8. Les validateurs mélangent règles métier et ancien registre documentaire — priorité moyenne

`validate_stacks.py`, `validate_core_features.py`, `validate_core_solutions.py` et `validate_cycle.py` exigent la présence de chemins de fichiers dans `AGENTS.md`. Plusieurs chemins exigés n’y figurent plus. Cette condition documentaire est devenue incompatible avec le rôle actuel d’AGENTS ; elle ne mesure pas la cohérence économique.

À l’inverse, certaines vérifications utiles des volumes sont restées dans cette ancienne chaîne. Supprimer entièrement ces outils sans extraction ferait perdre des contrôles pertinents.

**Correction :** transférer les invariants encore utiles vers le contrôle Python courant ; supprimer les assertions de présence dans AGENTS ; retirer ensuite les validateurs consacrés aux anciens points CSF. Les contrôles doivent porter sur les références structurées et les données, pas sur une liste de noms dans de la prose.

### 9. Le répertoire actif et la release embarquent des données remplacées — priorité moyenne

`source/` mélange hypothèses, textes, anciennes cartes et résultats générés. `Study._files()` inclut globalement tous ses YAML/Markdown dans les documents de la release, même lorsqu’ils ne sont plus nécessaires au calcul courant. Une seule release existe bien ; son contenu reste plus large que le modèle utile.

**Correction :** distinguer données éditables, preuves et résultats produits. Utiliser une liste explicite des documents nécessaires au modèle et à ses preuves, avec résolution des références. Cette liste est un contrat de composition, pas un nouveau système de versions. Ne pas réduire la release aux seuls fichiers lus pour calculer : certaines preuves et explications sont indispensables sans intervenir dans une formule.

### 10. Les anciens outils Excel restent dans le dossier courant — priorité moyenne

Quatorze `tools/flow_*.json` et deux journaux d’exécution appartiennent principalement à l’ancienne chaîne Excel. Les références littérales trouvées pointent vers des scripts archivés, des notes historiques ou d’autres fichiers de cette chaîne. Aucun ne figure parmi les documents du chargement économique observé.

**Correction :** retirer cette chaîne du dossier des outils actifs après revue de ses derniers usages. Conserver un livrable final si nécessaire ; ne pas garder chaque jeu de paramètres intermédiaire pour reconstruire tous les anciens classeurs. Le générateur Excel encore utilisable sur demande est un cas distinct : son existence ne rend pas tous les JSON historiques nécessaires.

### 11. Les archives contiennent des preuves actives et des répétitions évitables — priorité moyenne

`archives/etude-avant-yaml-2026-10-24/07-analyse-synvance.md` reste cité par les stacks Microsoft/SAP et le registre `sources/integration-maintenance-2026-10-22.yaml`. Il est présent dans la release. Le supprimer aujourd’hui retirerait une preuve consultable.

À l’inverse, les 19 groupes de doublons exacts comprennent 18 copies de pièces conservées dans `sources/` et reprises dans `outputs/01a1530f-f378-7fd1-9654-468c9b2141b6/FLOW_Dossier_client_2026-10-21/`, plus deux noms pour un même classeur. Une livraison autonome peut légitimement contenir ces copies : le gain de 49,4 Mo n’est réalisable que si cette autonomie n’est plus utile.

**Correction :** garder les pièces originales et les quelques décisions encore nécessaires ; retirer les copies de travail, sorties successives et anciennes méthodes remplacées après revue des citations. Si une ancienne analyse est la seule preuve d’une hypothèse actuelle, relocaliser son passage utile dans un registre de preuve courant avant retrait. Ne pas transformer chaque ancienne étape de travail en état métier permanent.

### 12. Les documents de référence ne donnent pas la même autorité — priorité haute pour la maintenance

| Document | Écart constaté | Rôle cible |
|---|---|---|
| `AGENTS.md` | Contrat récent, mais ses règles ne sont pas toutes reflétées dans les données ; les anciennes instructions sont très volumineuses. | Règles de travail, frontière économique, définition des deux états et exigences de contrôle. Aucun inventaire exhaustif. |
| `README.md` racine | « périmètre commun », « Excel actif », AGENTS présenté comme registre ; brouillon/release absents. | Point d’entrée court : périmètres comparés, référence publiée, accès au brouillon, liens canoniques. |
| `source/README.md` | Ancre Make et bonus ; tableau omettant déploiement Groupe et modèle composable ; ancienne description des coûts. | Dictionnaire du modèle : propriétaire de chaque donnée, distinction paramètre / dérivé / preuve / contrepoint. |
| `tools/README.md` | Globalement aligné sur les deux états ; exemple de parité lié à un témoin daté particulier. | Commandes uniques, limites des contrôles, témoin choisi pour l’opération en cours. |
| `app/README.md` | Ancien parcours ; redémarrage après YAML sans préciser le mode, alors que le défaut est release. | Renvoi vers le modèle et les commandes canoniques ; pas une autre définition de l’économie. Seuls ces aspects documentaires ont été examinés. |
| Audits antérieurs | Certaines conclusions de simplification sont plus larges que leur mise en œuvre effective. | Preuves datées, jamais instructions concurrentes de la référence courante. |

**Correction :** une information prescriptive a un seul propriétaire ; les autres documents y renvoient. L’alignement ne consiste pas à recopier AGENTS dans chaque README.

## Modèle cible minimal

Conserver six ensembles logiques, sans imposer un fichier unique ni recréer toutes les structures :

| Ensemble | Autorité et contenu à conserver |
|---|---|
| Métier | Capture de cartographie, identifiants natifs, fonctions et frontières de `grille-complexite.yaml`, rapprochement des situations. Les alias BC/anciens liens ne deviennent pas une deuxième carte. |
| Travaux Make | `recalibration-metier.yaml` : lots, plages de JH, réemplois ; travaux client réellement nécessaires. Aucun ancien bloc CSF actif. |
| Achats Buy | Pièces fournisseur, prix et séquences, inclusions, qualification des écarts. Les forfaits restent indivisibles tant que la preuve ne permet pas de les ventiler. |
| Volumes et services | Un jeu de volumes par contexte, activités valorisées une fois, Core / Run / MCO client / évolutions clairement distingués. |
| Déploiement et calendrier | Unités, jalons, réceptions, ressources du programme, hébergement du build et transition ; articulation explicite avec le service stabilisé. |
| Valorisation | Tarifs, gains, pilotage par assiette, inflation, arrondis et projection des financements. Résultats dérivés, jamais ressaisis. |

Les références de marché restent une lecture de confrontation et une justification de tarifs lorsque c’est explicitement prévu ; elles ne deviennent pas une formule automatique de recalibrage. Les différences de périmètre SAP et FLOW restent visibles. Les scénarios de déploiement et sensibilités ne sont pas des versions historiques du modèle.

Conserver les deux états existants : **brouillon unique → contrôle → remplacement de la release courante**. Les simulations sont des paramètres personnels avec leur contrat de reprise, pas des copies du modèle. Les quelques informations historiques utiles à leur compatibilité ne doivent pas être confondues avec les anciens chiffrages à retirer.

## Plan de retrait concret

| Candidats | Action proposée | Condition avant retrait |
|---|---|---|
| `core` dans les cinq chiffrages ; fichier features CSF ; cinq solutions CSF ; schémas/validateurs associés | Retirer du modèle actif. | Migrer obligations de schéma, empreintes, correspondances et preuves encore citées ; parité des résultats. |
| Champs annuels écrasés par `business_calibration.apply` | Remplacer par références puis supprimer les anciennes valeurs. | Même entrée compilée pour transition et régime annuel, avec périodes propres. |
| Scores historiques dans les catalogues intégration/maintenance | Retirer les champs sans lecteur utile ; conserver activités, rôles et preuves. | Inventorier les consommateurs de détail et adapter leurs contrats. |
| `tools/flow_*.json`, `tools/build_flow_estimate.log`, `tools/audit_flow_workbook.log` | Sortir de l’outillage courant puis supprimer les éléments sans usage retenu. | Vérifier la chaîne archivée et choisir les seuls livrables finaux à garder. |
| Copies exactes dans l’ancien dossier client et classeurs identiques | Garder un exemplaire utile. | Préserver les originaux ; décider si l’ancien paquet doit rester autonome. Liste exacte et empreintes dans le JSON. |
| `archives/methodes-remplacees/` et instantanés avant recalibration/cohérence/modèle composable | Supprimer les répétitions de travail sans preuve ou décision unique. | Revue des citations, sauvegarde réelle si nécessaire ; ne pas conserver les variantes par défaut. |
| `archives/etude-avant-yaml-2026-10-24/07-analyse-synvance.md` | Conserver tant que cité ; consolider ensuite ses preuves utiles. | Repointage vérifié des stacks, registre et documents de release. |
| `sources/core-system-solutions-2026-10-22.yaml` | Conserver malgré son nom ancien. | Ce registre est effectivement lu par la calibration actuelle ; ne pas le confondre avec les cinq anciennes solutions. |
| `source/couts-15-ans.yaml`, `source/investissements-10-ans.yaml` | Sortir du périmètre éditable ; produire seulement les exports encore utiles. | Adapter les liens et lecteurs ; ne pas supprimer un livrable en croyant supprimer un calcul. |
| `tmp/` | Ménage séparé des sorties de travail. | Préserver dépendances Python utilisées, serveur, sessions, preuves citées et derniers livrables utiles. Pas de suppression globale. |

Tous les fichiers du dépôt apparaissent actuellement non suivis dans le `git status --short` observé. **Ne pas compter sur Git pour récupérer une suppression** avant d’avoir une sauvegarde effective. L’audit n’en crée pas et ne supprime rien.

## Ordre d’exécution recommandé et critères de réussite

1. **Fixer les autorités et aligner les textes.** Corriger les contradictions Make/SAP, les rôles des README et la documentation des deux états. Distinguer paramètres exécutés et contexte. Aucun montant modifié.
2. **Retirer la génération CSF du chemin actif.** Migrer schémas, dépendances et contrôles ; garder le fond métier et les preuves actuelles. Le calcul doit fonctionner sans les six anciennes données Core.
3. **Unifier les données réellement calculantes.** Volumes, travaux annuels compilés et classification composable ; validation des jalons, parts et clés. Supprimer les valeurs écrasées et les sélecteurs sans effet.
4. **Séparer valorisation et projections.** Les prix et travaux ne doivent plus dépendre d’un horizon historique de quinze années de service. Préserver la cadence commerciale Buy et les centimes.
5. **Retirer les historiques et dérivés sélectionnés.** Après correction des liens, supprimer les éléments identifiés ; conserver les preuves originales, un dossier de décisions utile et les seuls livrables finaux nécessaires. Publier une seule nouvelle release après validation du modèle simplifié.

Critères d’acceptation : mêmes résultats de référence aux vingt couples option/horizon ; mêmes résultats pour un jeu limité de simulations représentatives ; reprise des sauvegardes existantes ; forfaits Buy conservés ; aucune double dépense entre build, transition et service complet ; montant ou classement affecté par chaque paramètre annoncé calculant ; incohérences de volumes et de calendrier refusées ; aucune dépendance active vers les fichiers retirés ; tous les documents désignent la même référence.

Utiliser un témoin de parité pour cette opération, puis les invariants courants. Ne pas instituer un test permanent pour chaque ancienne version. Conserver les contrôles économiques indépendants déjà utiles et ajouter seulement les contrôles de contrat manquants.

## État vérifié à la clôture de l’audit

Les vingt dépenses cumulées brouillon/release concordent au centime ; la projection complète comparée concorde également. Deux documents diffèrent des pièces figées au relevé joint : `config/application.yaml` et `tools/study_app.py`, sans écart économique observé. La release auditée est `7b8e00fdae97`.

L’empreinte du moteur courant diffère également de celle de cette release. Le chargement standard de release prévoit de refuser ce cas jusqu’à une publication contrôlée. La comparaison de l’audit projette directement les données figées et les données du brouillon avec le projecteur courant ; elle ne vaut donc pas validation du démarrage du serveur en release. Ces écarts préexistent aux modifications produites par cet audit ; ils ne sont ni corrigés ni publiés ici.

Les essais n’ont changé que des copies en mémoire. Seuls le présent rapport, son collecteur, ses preuves JSON et une sortie de console temporaire ont été produits. Les tests antérieurs ne sont pas présentés comme réexécutés ; aucune certification exhaustive nouvelle des hypothèses financières n’est déduite de la parité.
