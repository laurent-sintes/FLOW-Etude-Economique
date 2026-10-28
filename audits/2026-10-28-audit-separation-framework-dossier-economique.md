# Audit de la séparation entre Framework et dossier économique

28 octobre 2026

**La progression des méthodes est cohérente, mais le Framework mélange encore la démarche et son application à FLOW.** Le problème dépasse les montants : il concerne aussi les choix de scénario, les analyses d’offres, les références sélectionnées et l’avancement de leur qualification.

La dernière révision a amélioré les formules, les termes et l’accès aux preuves. Elle a aussi rendu les dossiers d’application plus visibles dans le Framework, notamment les fiches marché et les valeurs de référence. Il faut corriger cette architecture de lecture avant une nouvelle passe de simplification rédactionnelle.

La règle demandée est désormais inscrite dans [AGENTS.md](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/AGENTS.md:50>) :

> Les entrants et leur traitement restent dans le Framework ; les analyses réalisées, hypothèses retenues et résultats chiffrés vont dans le dossier économique.

Synvance et la cartographie restent donc des entrants nommés, avec leur rôle, leur contenu attendu et leur exploitation par la méthode. Le Framework peut rester ancré dans le contexte FLOW.

## Une frontière fondée sur le rôle du contenu

| Nature du contenu | Dans le Framework | Dans le dossier économique |
|---|---|---|
| Entrants récupérés | Cartographie, étude Synvance, offres, questionnaires, contexte métier, contraintes et volumes à recueillir ; rôle et contrôles attendus ; accès aux pièces | Analyse effectivement menée sur ces entrants, écarts constatés et décisions prises |
| Méthode | Étapes, sorties attendues, critères de preuve, formules, unités, assiettes et contrôles | Application de la méthode aux options et travaux étudiés |
| Conventions du modèle | Définition du JH, règles Build/Run, financement unique, périodes, indexation et traitement des inconnues | Valeurs choisies pour appliquer les conventions et exceptions propres au dossier |
| Paramètres | Sens du levier, unité, effet, provenance attendue et conditions de variation | Valeur retenue, justification, statut, scénario et éventuel réglage personnel |
| Références de marché | Types de références recherchés et conditions de comparaison | Produits analysés, observations, prix collectés, diagnostics et transpositions réalisées |
| Résultats et maturité | Conditions pour annoncer un résultat recevable | Charges, coûts, projections, couverture analysée, état de qualification et limites effectives |

**La présence d’un nombre n’est pas le critère de tri.** Les parts totalisant 100 %, les douze mois d’une année et les conversions nécessaires aux formules restent dans la méthode. À l’inverse, « aucun gain IA sur l’intégration Make » est une hypothèse actuelle même sans affichage de « 0 % ».

Les observations d’origine sont conservées avec leur preuve. Adapter une hypothèse ou négocier une offre ne réécrit pas rétroactivement le prix reçu ou le fait observé.

## Les constats prioritaires

### La page Marché contient une étude réalisée

La page ajoute aux six étapes méthodologiques les axes FLOW, les essais proposés, les comptes de capacités par état d’analyse et les accès aux fiches produit, projets et services. Ces contenus constituent le dossier de marché réalisé. Les prix qui y figurent ne sont pas tous des cibles FLOW : certains sont des observations externes ou des diagnostics. Ils appartiennent néanmoins à l’application de l’étude.

**À faire :** conserver une page « Méthode de l’étude de marché » dans le Framework et placer l’étude réalisée dans le dossier économique. Préserver les trois distinctions prix d’origine, prix normalisé et estimation transposée, avec leurs sources et leurs limites.

La notice « Ce que les références disponibles établissent aujourd’hui » doit accompagner le dossier réalisé. La définition des pièces Synvance à recueillir et de leur usage reste dans le Framework.

Preuves : [app/src/MarketMethodPage.tsx](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/MarketMethodPage.tsx:12>), [source/methode-evaluation-marche.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-evaluation-marche.yaml:10>).

### La page Paramètres est principalement une page d’hypothèses retenues

Elle affiche les gains par activité et option, les tarifs, le régime d’achat retenu, les taux de coordination, la mobilisation du programme, les enveloppes techniques, l’indexation, la clé Build/Run et les diagnostics historiques. Le plafond d’expertise de 40 JH et ses coefficients sont également des choix de référence.

**À faire :** déplacer la restitution actuelle sous « Hypothèses retenues », avec ses sources et ses statuts. Garder dans le Framework une page courte « Leviers et conventions de calcul » qui explique les variables et leurs effets sans recopier leurs valeurs.

Cette page méthodologique doit couvrir aussi les variables qui ne figurent pas dans les six familles actuelles : périmètre, travaux restants, volumes, fréquences, efforts unitaires, composition des profils, durées, ouvertures et réceptions. Le paramétrage du modèle est plus large que les seuls contrôles actuellement exposés dans Simuler.

Preuves : [app/src/FrameworkPage.tsx](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/FrameworkPage.tsx:110>), [app/src/FrameworkPage.tsx](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/FrameworkPage.tsx:172>), [tools/framework_parameters.py](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/framework_parameters.py:78>).

### Les Fondamentaux affichent déjà une hypothèse chiffrée

Les tags du MCO Beaumanoir affichent la clé de référence **50 % Build / 50 % Run**. La convention « poste mixte avec répartition paramétrable » appartient au modèle métier. La valeur retenue appartient aux hypothèses économiques.

La même page mélange aussi définition des charges et provenance de la base actuelle. Les définitions doivent rester ; le statut de la calibration et les résultats actuellement incomplets doivent accompagner les évaluations économiques.

Preuves : [source/architecture.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/architecture.yaml:111>), [app/src/ModelPage.tsx](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/ModelPage.tsx:40>), [app/src/ModelPage.tsx](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/ModelPage.tsx:50>), [app/src/ArchitectureLayers.tsx](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/ArchitectureLayers.tsx:7>).

### Les choix non chiffrés doivent également être relocalisés

Le Framework présente actuellement l’absence de gains IA sur l’intégration et la transition Make, le scénario haut sans gains, l’origine historique du plafond d’expertise ou le traitement particulier de services SAP.

Il faut conserver les traitements et leurs conditions dans la méthode : appliquer un gain justifié aux activités éligibles, remplacer un tarif sur des journées déjà financées, respecter une séquence contractuelle. Les choix effectivement retenus pour FLOW vont dans le dossier économique.

Preuves : [source/methode-calcul-net.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-calcul-net.yaml:78>), [source/methode-calcul-run.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-calcul-run.yaml:60>), [source/methode-calcul-run.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-calcul-run.yaml:83>), [source/methode-calcul-run.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-calcul-run.yaml:162>).

### Le dossier économique doit expliquer davantage que le seul Core

Son menu comporte actuellement l’évaluation Core, Comparer, Se projeter et Simuler. La première page détaille surtout les charges de construction Make. Comparer montre aussi les budgets d’intégration et de fonctionnement, mais ne déroule pas leur construction.

**À faire :** donner un emplacement continu aux évaluations des trois ensembles : obtenir le Core System, intégrer chez Beaumanoir, financer le fonctionnement. L’obtention doit inclure la sélection-contractualisation Buy, sans ajouter une construction générique aux produits achetés.

Des données et vues détaillées existent déjà pour l’intégration et le fonctionnement. Leurs projections peuvent être réutilisées ; certains anciens composants comportent toutefois des blocs à déplier et ne doivent pas être remontés tels quels.

Preuves : [config/application.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/config/application.yaml:1153>), [app/src/CoreEvaluationPage.tsx](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/CoreEvaluationPage.tsx:10>), [app/src/EssentialViews.tsx](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/EssentialViews.tsx:63>), [app/src/IntegrationEstimates.tsx](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/IntegrationEstimates.tsx:12>), [app/src/SponsorJourney.tsx](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/SponsorJourney.tsx:102>).

## Traitement des sept pages

| Page | À conserver dans le Framework | À relocaliser ou scinder |
|---|---|---|
| Vue d’ensemble | Problématique d’opportunité, entrants cartographie/Synvance, logique Make/Buy, dimensions de comparaison, adaptabilité et exigences de justification | Conclusion sur Finance SAP, diagnostic ERPNext effectivement réalisé, état actuel de calibration et d’avancement |
| Fondamentaux | Objets métier, périmètres d’entrée, conventions, phases, structures de coût, brut/net/total et cartographie de contexte | Clé 50/50, provenance des chiffres actifs, conclusions propres aux offres, état actuel des agrégations |
| Méthode de l’étude de marché | Six étapes, critères de preuve et de transposition, trois types de prix, formules et sorties attendues | Axes et essais sélectionnés pour l’analyse FLOW, progression, fiches, projets, services et diagnostics exécutés |
| Estimation du développement Make | Contrat du skill, cinq étapes, périmètre des JH, lots partagés, qualification attendue et consolidation | Notice sur la base historique et état réel de qualification ; lien vers l’application et ses réserves |
| Des charges au budget | Formules, assiettes, profils, conditions des gains, valorisation et financement unique | Gains ou absences de gains retenus, scénario haut courant, dimensionnement effectif du programme et incomplétude actuelle des efforts |
| Fonctionnement et part Run | Services, volumes, interventions, contrats, périodes, indexation et classement Build/Run | Plafond choisi, coefficients, particularités contractuelles appliquées et état réel de l’agrégation |
| Paramètres du modèle | Catalogue des leviers, unités, effets, origine attendue, règles de variation et de comparaison | La page actuelle de valeurs, justifications et diagnostics rejoint « Hypothèses retenues » |

Les frontières stables du coût modélisé peuvent rester explicites dans les Fondamentaux. Les exclusions propres à l’offre ou au scénario courant vont avec le dossier. La cartographie reçue et le périmètre transmis à l’évaluation restent des entrants ; une sélection ou un écart que l’étude produit à partir de cette cartographie doit être identifié comme son analyse.

Sources complémentaires : [source/vision-framework.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/vision-framework.yaml:45>), [source/vision-framework.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/vision-framework.yaml:78>), [source/vision-framework.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/vision-framework.yaml:131>), [source/fondamentaux.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/fondamentaux.yaml:165>), [source/fondamentaux.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/fondamentaux.yaml:203>), [source/methode-evaluation-core.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-evaluation-core.yaml:10>), [source/methode-calcul-run.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-calcul-run.yaml:13>).

## Clarté et solidité de la méthode

### Définir précisément le gain utilisé dans les formules

La formule de passage au net emploie un pourcentage de **réduction de l’effort**. Il faut le définir comme tel, à périmètre et qualité constants. « Gain de productivité » seul peut aussi être compris comme une hausse du débit de production, ce qui ne conduit pas à la même convention de calcul.

Cette précision ne change aucun taux. Elle aligne le vocabulaire visible sur la définition existante du modèle.

Source : [source/calibration-couts.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/calibration-couts.yaml:48>).

### Distinguer une preuve traçable d’une calibration validée

La phrase « Une référence étaye une estimation si sa portée est connue » est trop affirmative : connaître la portée est nécessaire, mais la comparabilité et les ajustements doivent aussi être justifiés. Préférer : **« Pour étayer une estimation, une référence doit avoir une portée connue et une transposition justifiée. »**

Les validations contrôlent les contrats, unités, références et financements. Elles ne démontrent pas empiriquement la justesse des hypothèses. Le Framework doit expliquer les conditions de recevabilité ; le dossier expose les preuves, la revue et la calibration effectivement réalisées.

Sources : [source/methode-evaluation-marche.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-evaluation-marche.yaml:6>), [tools/core_qualification.py](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/core_qualification.py:199>).

### Donner à COCOMO sa portée exacte

La formule actuellement montrée est celle d’un diagnostic nominal simplifié sur une sélection de code ERPNext/Frappe/Insights. La retirer du cas concret sans préciser ses hypothèses risquerait de la présenter comme une application complète et universelle de COCOMO II.

Le Framework peut conserver les conditions d’utilisation d’un modèle paramétrique et la formule du diagnostic, explicitement qualifiée. Sélection de code, coefficients, calcul exécuté et résultats restent dans le dossier. Les références OSS apportent des observations sur les fonctions et les composants ; elles ne prouvent pas seules une charge FLOW.

Source : [source/methode-evaluation-marche.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-evaluation-marche.yaml:85>).

### Distinguer invariants, conventions et hypothèses adaptables

Les chiffres sont adaptables au contexte. Les contrôles de cohérence restent obligatoires : unités compatibles, parts cohérentes, inconnue distincte de zéro, financement unique et conservation des montants.

Les conventions sont explicites, notamment le classement Build/Run, les règles temporelles et le périmètre du JH. Les hypothèses sont discutables : charges, volumes, gains, tarifs, délais et provisions. Les observations d’origine conservent leur date et leur valeur.

Il faut aussi distinguer **source observée**, **hypothèse retenue** et **scénario de référence**. Le seul mot « référence » ne suffit pas à identifier le statut d’un tarif ou d’une charge.

La convention monétaire doit être définie dans la méthode puis déclarée dans le dossier. Les sources FLOW indiquent actuellement une base composite datée, qui n’est pas normalisée en euros constants ; cela ne se confond pas avec les prix de projets normalisés par l’étude de marché.

Source : [source/calibration-couts.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/calibration-couts.yaml:10>).

### Garder les limites près des résultats et les scénarios sans probabilité inventée

La somme des bornes des lots est une enveloppe, pas un intervalle statistique. D’autres calculs utilisent des coefficients et des choix de gains. Le Framework doit expliquer ces constructions et leurs différences ; les paramètres des scénarios retenus vont dans le dossier.

Le déplacement des notices ne doit pas masquer la provenance historique des charges, les efforts humains encore incomplets, les parts Buy inconnues ou l’absence actuelle d’agrégation monétaire Build/Run. Ces réserves doivent accompagner les chiffres qu’elles limitent.

Sources : [source/methode-evaluation-core.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/methode-evaluation-core.yaml:148>), [tools/calculate_costs.py](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/calculate_costs.py:166>), [source/statut-evaluation.yaml](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/statut-evaluation.yaml:5>).

## Cohérence avec les skills

Les deux skills désignent les YAML méthodologiques comme autorités communes. Le skill marché instruit les observations et leurs limites ; le skill Core prépare les travaux et charges avec leur provenance. Le candidat Core reste une proposition pour relecture, sans application automatique aux charges actives.

Cette séparation des responsabilités est cohérente. La réorganisation des pages ne nécessite pas de recopier les règles dans les skills ni de changer le moteur. Il faut préserver leurs accès au dossier courant et au statut d’application, même si ces informations quittent les pages de méthode.

Sources : [skill marché](<C:/Users/laure/.codex/skills/flow-etude-marche/SKILL.md>), [skill Core](<C:/Users/laure/.codex/skills/flow-evaluer-core-system/SKILL.md>), [tools/core_qualification.py](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tools/core_qualification.py:254>).

## Parcours proposé

| Framework d’évaluation | Dossier économique |
|---|---|
| Vue d’ensemble | Étude de marché |
| Fondamentaux du modèle | Hypothèses retenues |
| Méthode de l’étude de marché | Évaluations économiques |
| Estimation du développement Make | Comparer |
| Des charges au budget | Se projeter |
| Fonctionnement et part Run | Simuler |
| Leviers et conventions de calcul | |

L’Étude de marché réunit, en chapitres visibles, offres reçues et analyse, fonctions et produits, projets d’intégration, services de fonctionnement. Les Évaluations économiques réunissent obtention du Core, intégration et fonctionnement. Cette organisation évite de multiplier les entrées de menu.

Chaque méthode propose **« Voir l’application à FLOW »**. Chaque application propose **« Comprendre la méthode »**. Les valeurs renvoient à leur hypothèse propriétaire ; les analyses renvoient à leurs pièces. Les liens Synvance et cartographie restent présents là où leur rôle d’entrant est expliqué.

Les routes actuelles restent compatibles. La route des paramètres peut accompagner le déplacement de sa page dans le dossier économique ; celle de la méthode Marché conserve son sens. Les liens précis vers une fiche ou un chapitre demandent un traitement du routeur, qui normalise actuellement les paramètres d’URL.

Source : [app/src/App.tsx](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/App.tsx:18>).

## Ordre de mise en œuvre

1. Affecter un emplacement principal à chaque contenu selon la règle désormais inscrite dans AGENTS.
2. Préparer les pages d’accueil de l’étude de marché, des hypothèses et des évaluations économiques, à partir des données existantes.
3. Déplacer les applications Marché et Paramètres avec leurs sources, limites et statuts ; conserver les entrants et leurs traitements dans le Framework.
4. Reprendre les cinq autres pages pour séparer mécanismes, conventions et choix actuels, sans effacer les réserves qui doivent accompagner les résultats.
5. Corriger les termes restants, notamment réduction d’effort et statuts de « référence » ; harmoniser titres et liens réciproques.
6. Vérifier le parcours complet et la parité économique, sans recalibration ni rupture de simulation.

## Critères de réception

- Une modification de tarif, de volume ou de gain FLOW change le dossier économique, sans imposer une réécriture de la méthode.
- Le Framework décrit ses entrants, traitements, sorties et contrôles ; Synvance et la cartographie restent clairement identifiés.
- Les formules conservent variables, unités, assiettes et conditions d’application.
- Chaque valeur retenue garde son propriétaire, son statut, sa justification et sa possibilité réelle de modification personnelle.
- La provenance et les limites sont visibles à proximité des résultats.
- Les cinq options, contrats, calendriers, horizons et simulations restent identiques.
- La lecture reste continue, sans accordéon ; les sources restent consultables par liens.

## État de l’intervention

Audit des sept pages, des vues documentaires, du parcours économique et des contrats méthode/skills, à partir des sources courantes et des rendus du candidat local vérifié. Le contrôle `check_model --content` a été rejoué avec succès. La suite économique complète n’a pas été relancée pour cette revue éditoriale.

**Seule la règle demandée a été ajoutée à AGENTS.md.** Les recommandations de cet audit ne sont pas encore appliquées à l’interface. Aucun chiffre, calcul ni simulation n’a été modifié.

