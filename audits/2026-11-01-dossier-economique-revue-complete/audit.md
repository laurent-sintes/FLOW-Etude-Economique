# Audit complet du dossier économique

**Conserver les trois pages actuelles.** Leur découpage et leur première lecture sont adaptés au sponsor. Quatre corrections prioritaires restent nécessaires : une hypothèse remplacée encore affichée, une définition trop large du reste à financer, des passages vers le coût total insuffisamment expliqués et la perte de l’horizon au retour des justifications.

Les **340 contrôles arithmétiques et rapprochements de prix exécutés passent**. Les principaux défauts relevés concernent la fidélité de la présentation au modèle, la compréhension des assiettes et la continuité de lecture. Aucun changement de l’application ou des hypothèses n’est appliqué dans cet audit.

## Périmètre vérifié

- Version du modèle : **01/11/2026 · n° 1**. Livraison locale : `f765e1c1f71b8133f34056f331d05ae618673442bbbc17b6f46af1811baa8c45`.
- Comparer les options, Comprendre les coûts et Hypothèses retenues, avec Java/Spring, Microsoft et SAP.
- Horizons 3, 5, 7 et 10 ans dans les données. Parcours réel à trois ans, approfondissement, puis retour.
- Budgets initiaux, annuités, postes annuels, lots et rôles Java, prix retenus et sources, financements transitoires et abonnements Buy.
- Rendu à **1280 × 720** et **390 × 844**, avec détails par rôle et toutes les rubriques des hypothèses ouvertes.
- Approfondissements des financements, des projets comparables et des offres d’intégration. Lecture du code des états de chargement et d’erreur.

La référence servie a été comparée à un chargement frais des sources : **la projection est identique**. Les contrôles ne constituent ni une validation contractuelle des offres, ni une réévaluation des charges, ni une certification de couverture fonctionnelle. Aucun prix de marché n’a été actualisé.

## Ce qui fonctionne

Les trois options sont immédiatement identifiables. Sur ordinateur, les cumuls apparaissent vers **434 pixels de hauteur**, avec les dates de service complet dans les cartes. La comparaison ne demande plus de traverser un long exposé méthodologique.

Les hypothèses sont consultables sans saisie. Aucun champ de modification n’a été trouvé dans les trois pages principales, y compris dans les détails des hypothèses et du lot contrôlé. Les noms .NET et Rust n’apparaissent pas dans ces vues. Les conventions distinguent le cumul, les budgets de travaux et l’année de fonctionnement de référence.

Les principaux montants se réconcilient. Les forfaits éditeur restent groupés, sans ventilation artificielle. Les valeurs nulles et les zéros ne sont pas confondus. Les preuves tarifaires et d’indexation restent accessibles. Le lien direct vers un lot ouvre son détail et lui donne le focus.

Aucun débordement horizontal global n’a été observé dans les vues principales, ni dans les détails mobiles contrôlés. La palette, les grands montants et les icônes des phases donnent des repères cohérents.

## Les quatre corrections prioritaires

### DE 01 Une hypothèse remplacée reste présentée comme retenue

**P1 — fidélité au modèle.** Dans « Achats et provisions retenus », la ligne **Accompagnement initial Make — 120 JH** est encore affichée.

Le modèle fournit pourtant `framework.other[].status: replaced`. La substitution Groupe porte `accompagnement_retire: true` et précise que les paquets de déploiement remplacent les anciennes formations, l’accompagnement, la bascule et leur coordination. Cette charge n’est pas un supplément à financer dans la référence actuelle.

`EconomicAssumptionsPage` restitue toutes les lignes de `F.other` sans utiliser leur statut. Le lecteur peut donc intégrer mentalement ces 120 JH au budget ou chercher une ligne de coût qui n’existe plus sous cette forme.

**Correction :** présenter uniquement les valeurs actives parmi les hypothèses retenues. Garder la trace des remplacements dans les preuves ou un historique identifié. Vérifier également les pourcentages conservés pour d’autres cas, comme la coordination de construction hors lots adoptés : leur présence ne doit pas laisser croire qu’ils s’ajoutent au budget actuel des lots.

Preuves : [capture de la ligne](audit-economique-hypothese-remplacee.png), `financial-checks.json#other`, `group_substitutions`, et boucle `F.other.map` dans `app/src/EconomicDossier.tsx`.

### DE 02 Le reste à financer doit porter son assiette exacte

**P1 — compréhension du financement.** Le champ représente le solde du **journal des financements initiaux et transitoires**. Les abonnements Buy sont projetés séparément.

À trois ans pour Microsoft :

| Élément | Montant exact en € HT |
| --- | ---: |
| Solde initial affiché | 929 864,42 |
| Abonnements entre les mois 36 et 44, hors de ce solde | 652 667,67 |

Le service complet Microsoft est prévu au mois 44. Le texte actuel décrit des travaux, services de transition et achats jusqu’au service complet, puis exclut le fonctionnement après cette date. Il ne rend pas assez visible que des abonnements **avant** cette date sont eux aussi hors du solde affiché.

En Make, le journal intègre plusieurs services et moyens de transition. En Buy, les abonnements suivent leur propre séquence. Le même champ demande donc une explication de son assiette pour être correctement comparé.

**Correction :** nommer explicitement le solde des financements initiaux et transitoires et préciser le traitement des abonnements. Si une lecture « dépenses nécessaires jusqu’au service complet » est souhaitée, la dériver séparément depuis les dépenses réellement projetées. Conserver le sens historique du champ utilisé par les sauvegardes.

Preuves : `microsoft_remaining_example` dans [les contrôles financiers](financial-checks.json), `Study.simulate` pour le solde et `project_financing` pour les abonnements.

### DE 03 Les passages vers le coût total sont encore opaques

**P1 — objectif principal de Comprendre les coûts.** Deux rapprochements utiles sont déjà disponibles dans le moteur, mais ne sont pas montrés.

**Des références reçues au budget Buy.** Les charges brutes indiquent que les compléments se lisent dans le dossier économique. Le détail économique affiche seulement une ligne « Offre d’intégration et compléments retenus ».

| Élément, en € HT | Microsoft | SAP |
| --- | ---: | ---: |
| Référence reçue | 4 240 000 | 13 462 352 |
| Compléments FLOW | 78 960 | 80 640 |
| Pilotage des compléments | 7 896 | 8 064 |
| Support Microsoft initial, ponctuel | 90 000 | 0 |
| Budget d’intégration retenu | **4 416 856** | **13 551 056** |

Le lecteur voit donc deux montants différents entre dossiers sans disposer du rapprochement qui explique leur différence. Le support initial Microsoft doit rester identifiable comme ponctuel. La base Microsoft est une **projection Groupe du COPIL 5**. La base SAP est la **somme des trois lots de la proposition Delaware**. Ces deux natures de référence doivent être conservées dans la lecture.

**De l’année de référence au cumul Java.** À dix ans, Java affiche 5 193 331,20 € de services et achats. L’année de référence à 932 007,08 € ne suffit pas à expliquer ce cumul : le calendrier, les dépenses pendant les travaux et l’indexation interviennent.

| Composition du poste services et achats Java à dix ans | Montant exact en € HT |
| --- | ---: |
| Financements pendant la construction et la transition | 1 294 824,15 |
| Dépenses après service complet | 3 898 507,05 |
| Total du poste affiché | **5 193 331,20** |

Le journal permet aussi de lire 8 170 877,10 € de financements Java jusqu’au service complet, dont la construction, l’intégration et ces dépenses de transition. Cette lecture dépend du calendrier de référence provisoire. Elle n’est pas directement comparable à la seule somme des journaux Buy, qui exclut leurs abonnements projetés séparément.

**Correction :** faire de ces rapprochements le cœur de la page. Ajouter les contributions par poste dans la projection annuelle, actuellement limitée au total de chaque année. Utiliser les données déjà calculées, avec une trace explicite des périodes. Les forfaits sans ventilation documentée restent groupés.

Preuves : [détail Buy actuel](audit-economique-detail-integration.png), `buy_integration_trace` et `java_ten_year_bridge` dans les contrôles financiers.

### DE 04 L’horizon est perdu au retour d’un approfondissement

**P1 — continuité de lecture.** Le défaut est reproduit dans le navigateur :

1. Microsoft à **trois ans**, cumul **6 038 k€ HT**.
2. Ouvrir « Vérifier les financements et les écarts de couverture ».
3. Revenir aux coûts.
4. L’option Microsoft est conservée, mais l’horizon revient à **dix ans**, avec **21 627 k€ HT**.

Le même paramètre `view` porte soit un horizon, soit un type d’approfondissement. Le lien de retour ne restitue pas l’horizon précédent. Le changement de montant donne une rupture importante dans la lecture.

**Correction :** conserver séparément option, horizon, type de détail et point de retour. Le retour doit retrouver le contexte qui a conduit à ouvrir la justification. Vérifier également les liens de preuve vers les charges et les références externes.

Preuves : [avant](audit-economique-horizon-avant.png), [après](audit-economique-horizon-apres.png), `horizonJourney` dans [les observations navigateur](browser-observations.json), fonctions `period`, `ExpertReading` et liens de `EconomicCostsPage`.

## Améliorations complémentaires

| ID | Priorité | Constat | Correction recommandée |
| --- | --- | --- | --- |
| DE 05 | P2 | Les premiers montants sont proches des dates de service complet, mais les conditions structurantes arrivent plus bas. Sur ordinateur, le calendrier Make provisoire est signalé vers y = 1038 et le périmètre Finance SAP vers y = 1750. La page Coûts Java ne rappelle pas le caractère provisoire du calendrier. | Accoler aux résultats les repères déterminants : service complet sur l’horizon, calendrier à confirmer et périmètre. Qualifier aussi la nature des prix : TJM techniques de cadrage en achat freelance direct, projection Groupe du COPIL pour Microsoft et proposition intégrateur pour SAP. |
| DE 06 | P2 | Les tarifs et taux sont visibles, mais plusieurs hypothèses qui donnent leur sens aux dépenses restent ailleurs : volumes de service, réductions d’effort réellement appliquées, lissage des travaux, date de départ des abonnements et relais de l’indexation. Les achats sont listés sans leur périmètre détaillé. | Résumer les quelques hypothèses déterminantes, avec leur assiette et leur statut, puis pointer vers la démonstration propriétaire. Distinguer valeur retenue, provision, inclusion et remplacement. Les abonnements Buy commencent après sélection, avant service complet. Les financements Make de transition et les récurrents stabilisés n’ont pas le même traitement temporel. Le support Microsoft de première année est agrégé au budget initial lissé sur la durée d’intégration : cette convention de répartition doit être explicitée et rapprochée du calendrier de paiement à confirmer. |
| DE 07 | P2 | « Relire les transpositions des projets comparables » ouvre quinze projets, avec quinze montants FLOW « Non établi ». Le détail mesure environ 18 035 pixels et 4 276 mots sur ordinateur. | Conserver le catalogue général dans les études préalables. Dans le dossier économique, présenter l’utilisation précise des références qui explique un budget, ou nommer clairement l’absence de transposition chiffrée. |
| DE 08 | P2 | Le comparateur ignore `error` et `retry` de sa lecture économique. Le fonctionnement annuel peut disparaître silencieusement si cette lecture échoue. Dans les hypothèses, la durée d’intégration dépend du même chargement, avec un état de lecture situé en bas de page. | Placer les états de chargement et d’échec auprès du contenu concerné, avec une relance visible. Ce scénario est établi par lecture du code. Aucune panne n’a été provoquée. |
| DE 09 | P2 | Les matrices de comparaison sont des blocs `div` et des titres. Elles ne déclarent pas les associations entre critères, options et valeurs d’un tableau accessible. | Ajouter une structure sémantique adaptée en conservant la présentation mobile. Vérifier ensuite la lecture avec une technologie d’assistance. L’audit a inspecté le DOM et l’arbre d’accessibilité, pas un lecteur d’écran complet. |
| DE 10 | P2 | Les synthèses reprennent surtout les distinctions Make/Buy et cumul/budget/année type. La date de version est visible, mais la base de prix composite est principalement expliquée dans les hypothèses. | Donner une synthèse propre à l’option et aux facteurs qui expliquent son coût. Présenter clairement des dépenses prévisionnelles aux prix et conventions retenus. Relier le cumul à dix ans aux décisions progressives, sans inventer de retour sur investissement ou d’enveloppe supplémentaire. |

### Lisibilité et look and feel

La présentation principale est courte : environ **481 mots** pour Comparer, **545** pour Comprendre les coûts et **387** pour Hypothèses retenues, détails fermés. Les grands montants, le blanc et les intercalaires fonctionnent bien.

Sur mobile, les prix des cartes commencent vers y = 471, 652 et 833. Le prix SAP est donc partiellement sous le premier écran de 844 pixels. Une synthèse plus compacte des trois valeurs améliorerait la comparaison immédiate. Ce point est moins prioritaire que les quatre défauts majeurs.

Les détails du lot contrôlé restent lisibles à 390 pixels, avec neuf rôles et sans débordement horizontal global. Les huit rubriques des hypothèses ouvertes représentent environ 1576 mots et 7052 pixels sur mobile. Cette profondeur est acceptable pour les preuves, avec une relecture éditoriale ciblée : neuf points-virgules réapparaissent dans ces détails et certains acronymes et formulations techniques demandent une explication. Préserver les citations et pièces originales.

## Réconciliation des chiffres contrôlés

Les 340 contrôles couvrent les cumuls par horizon, leurs annuités et leurs composantes, les postes annuels, les budgets de lots, les sommes de rôles, les produits JH × tarif, l’outillage et la concordance des tarifs avec leurs propriétaires. Les contrôles des quatre horizons portent sur les trois options du parcours courant.

| Option | Cumul à dix ans, k€ HT | Année de référence, k€ HT | Service complet, mois | Années de service complet à dix ans |
| --- | ---: | ---: | ---: | ---: |
| Java / Spring | 12 069 | 932 | 78 | 3,5 |
| Microsoft / K3 | 21 627 | 1 986 | 44 | 6,3 |
| SAP | 37 697 | 2 583 | 36 | 7,0 |

Ces valeurs de synthèse sont arrondies comme dans l’application. Les preuves conservent les euros et centimes. Elles n’établissent pas une équivalence des périmètres ou des modes d’achat.

## Ordre de correction proposé

1. **Fiabiliser la lecture du modèle** : retirer les hypothèses remplacées des valeurs retenues et préciser l’assiette du reste à financer.
2. **Expliquer les montants** : montrer les passages offre → budget et transition → régime stabilisé, ainsi que leur contribution annuelle.
3. **Sécuriser le parcours** : conserver le contexte des approfondissements, puis rapprocher les conditions de comparaison des premiers résultats.
4. **Alléger et rendre robuste** : recentrer les liens de justification, compléter les hypothèses déterminantes, traiter les erreurs de lecture et améliorer les associations accessibles des tableaux.

Ces corrections tiennent dans les **trois pages existantes**, avec des preuves ciblées à la demande. Elles peuvent être traitées à hypothèses financières constantes. Toute évolution ultérieure d’un montant ou d’une convention économique doit rester une décision distincte et contrôlée.

## Pièces de l’audit

- [Constats structurés](findings.json).
- [Contrôles financiers et traces de prix](financial-checks.json).
- [Observations et parcours navigateur](browser-observations.json).
- Captures des vues [Comparer sur ordinateur](audit-economique-comparer-desktop.png), [Comparer sur mobile](audit-economique-comparer-mobile.png), [Coûts sur ordinateur](audit-economique-evaluation-core-desktop.png) et [Hypothèses sur mobile](audit-economique-parametres-mobile.png).

L’application, ses données, sa version et les sauvegardes restent inchangées. Seuls les livrables de cet audit ont été ajoutés.
