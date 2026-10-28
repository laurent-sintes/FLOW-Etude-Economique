# Proposition — cycle du Core, Run et MCO client

27 octobre 2026 · **Proposition isolée, non appliquée à la référence.**

Le modèle sépare ce qui est financé, le service rendu, sa période et le contrat qui le finance. Il permet de distinguer le cycle de vie du Core, le Run et le MCO client sans décomposer artificiellement les offres Microsoft et SAP.

**Proposition centrale : ajouter 102 k€ HT d'hébergement pour les 48 mois de build Make.** La séparation des responsabilités conserve les autres montants de la proposition Groupe. L'hébergement porte son total hors construction logicielle à **4 232 k€ HT pour Java/Spring Boot, 4 518 k€ HT pour .NET et 5 491 k€ HT pour Rust**. Ces sommes couvrent le passage au Groupe et l'hébergement du build, pas un TCO sur dix ans.

Les hypothèses et calculs sont consultables dans la [définition YAML](2026-10-27-modele-composable.yaml), le [calcul reproductible](2026-10-27-modele-composable-calcul.py) et ses [preuves numériques](2026-10-27-modele-composable-preuves.json). Le budget d'hébergement est une provision d'ingénierie proposée, **pas une cotation fournisseur ni une fourchette de marché démontrée**.

## 1. Trois responsabilités, des calendriers distincts

| Responsabilité | Objet et prestation | Déclenchement | Make / Buy |
|---|---|---|---|
| **Cycle de vie du Core** | Construire, corriger et faire évoluer le produit générique ; produire ses releases | Construction puis cycle produit, indépendamment du lotissement client | Producteur FLOW en Make ; éditeur Microsoft ou SAP en Buy, financement généralement inclus dans le produit acheté |
| **Run** | Consommer les moyens et les droits d'usage ; exploiter, surveiller, assister et diagnostiquer | Dès qu'un environnement ou service est consommé, y compris pendant le build | Hébergement et exploitation propres en Make ; certaines ressources incluses dans les abonnements Buy |
| **MCO client** | Maintenir en état les configurations, extensions et interfaces réceptionnées ; assurer leur compatibilité | Après réception et stabilisation du périmètre concerné | Responsabilité client/intégrateur dans les cinq options, selon les contrats |

L'intégration conserve la première réalisation, la migration, la réception, la formation, la bascule et la stabilisation. Une **évolution fonctionnelle client** relève d'un portefeuille de nouveaux besoins, séparé du maintien en état. Une correction due au titre de la conformité initiale reste dans le financement initial : elle ne devient pas une facture de MCO ou de cycle produit supplémentaire.

« Après l'intégration » signifie après l'intégration **du périmètre réceptionné**. Le MCO d'une première unité peut ainsi commencer pendant le déploiement des suivantes. Une release générique du Core et la qualification de cette release dans le contexte Beaumanoir sont deux livrables différents.

## 2. Un financement unique, plusieurs lectures

Chaque financement conserve son identifiant, sa source, son montant et sa période. Ses allocations peuvent être lues par objet, responsabilité ou phase. **On additionne les allocations ou leur financement parent, jamais les deux.**

Un prix groupé reste un financement unique. Ses services sont décrits sans leur inventer une part monétaire. Une inclusion renvoie au financement parent ; un prix inconnu reste `null`. Le modèle n'impose donc pas une ventilation financière Core / Run / MCO lorsque le fournisseur ne la donne pas.

La cartographie métier garde sa hiérarchie native. Exemples de rattachements proposés :

| Sujet | Appui sur la carte | Ce que ce lien permet d'expliquer |
|---|---|---|
| Produit générique | `D03.i`, fonctions de calcul quantité/date et d'explication de la réponse ATP | Une correction de l'algorithme générique appartient au cycle du Core |
| Adaptations et raccordements | `master-data-ingestion`, `accounting-data-provision`, `D04.i`, `D04.k`, `D06.d` | Distinguer la réalisation initiale des contrats client, leur maintien et un nouveau besoin |
| Exploitation des usages | `BHV082`, `human-task-management` | Relier le service aux usages sans distribuer artificiellement l'hébergement entre capacités |

Les chemins et fonctions sont repris de la [grille métier](../source/grille-complexite.yaml) dans les preuves. Ils étayent la nature des livrables ; ils ne prouvent ni un tarif cloud, ni un volume de maintenance, ni la couverture d'un forfait.

## 3. Application aux activités Make existantes

| Activité | Affectation proposée | Frontière à préserver |
|---|---|---|
| MAI-001, MAI-002 | Run : assistance et diagnostic | La correction durable n'est pas comprise dans le diagnostic |
| MAI-003 | Cycle de vie du Core | Corrections génériques et releases, hors obligations initiales déjà financées |
| MAI-004 | MCO client | Corrections d'extensions réceptionnées ; déclenchement par unité |
| MAI-005 | Surveillance fixe → Run ; modifications de compatibilité → MCO client | Le chiffrage distingue les deux travaux. Un nouveau besoin fonctionnel doit rejoindre les évolutions client |
| MAI-006 | MCO client : qualification et promotion des versions suivantes | Première réception et stabilisation dans l'intégration, notamment INT-010 |
| MAI-007, MAI-008 | Run : opérations de plateforme, contrôles de sécurité, sauvegarde/restauration | Correctifs de code en MAI-003/004 ; nouvelles fonctionnalités d'outillage à qualifier séparément |
| MAI-009 | Cycle Core pour le générique ; évolutions client pour le paramétrage et les extensions | Les évolutions ne sont pas commandées dans la proposition centrale ; la référence active conserve son portefeuille |

**Décomposition MAI-005 :** les fichiers de chiffrage distinguent 40 JH annuels fixes de surveillance et dix modifications de contrats par an, valorisées selon la stack. La répartition utilise ces travaux, avec leur valorisation et leur pilotage existants. Elle n'utilise pas un pourcentage arbitraire. Les modifications sont ici supposées nécessaires au maintien de compatibilité ; le catalogue ne prouve pas que chacune relève de ce cas. Un besoin nouveau changerait l'affectation vers « évolutions client », sans justifier automatiquement une dépense supplémentaire.

Le libellé des alertes doit aussi être rapproché de MAI-007 : surveillance des contrats d'échange en MAI-005, exploitation de plateforme en MAI-007. La distinction est une frontière de travail proposée, pas la preuve de contrats déjà distincts.

**Réception des services communs :** la proposition Groupe les finançait dès la première ouverture, au mois 18 d'intégration. Le modèle composable retient la fin de sa stabilisation, au mois 20, pour le MCO commun. Les deux mois déjà financés de modifications/qualification sont classés en intégration initiale ; ils ne sont ni supprimés ni ajoutés aux paquets de déploiement. Ce reclassement représente **18 k€ HT en Java, 20 k€ HT en .NET et 27 k€ HT en Rust**, sans variation du total. Si les livrables sont reçus par lots différents, il faudra déplacer ce jalon par livrable.

Sources de calcul : [proposition Groupe et frontières de remplacement](2026-10-27-enveloppe-groupe-make.md), [chiffrage Java — maintenance](../source/chiffrage/chiffrage-java-spring.yaml), [volumes annuels](../source/maintenance.yaml), [calibration métier](../source/recalibration-metier.yaml). Les déclinaisons .NET et Rust sont référencées et contrôlées dans les preuves.

Ce reclassement ne démontre pas que les prestations des deux mois initiaux sont distinctes de la réception INT-010 ou des paquets de déploiement. Leur financement reste conservé par prudence dans cette proposition ; une inclusion démontrée conduirait à retirer la part correspondante, pas à la facturer deux fois.

## 4. Hébergement pendant le build : provision centrale de 102 k€ HT

Les [48 mois de build](../source/plan-investissement.yaml) servent d'assiette temporelle. Les profils ci-dessous sont de nouvelles hypothèses explicites, communes aux trois stacks faute de mesure justifiant des ressources différentes.

| Phase | Moyens proposés | Durée | Budget central |
|---|---|---:|---:|
| Développement initial | Un environnement partagé, runners éphémères, base simple | 12 mois | 12 k€ HT |
| Développement et qualification | Deux environnements partagés persistants, tests réguliers, sauvegardes | 24 mois | 48 k€ HT |
| Qualification et performance | Deux environnements et capacité de charge temporaire, données d'essai et traces renforcées | 12 mois | 42 k€ HT |
| **Total** | **Consommations de fabrication du Core** | **48 mois** | **102 k€ HT** |

Le YAML détaille chaque budget mensuel en calcul/runners, bases, stockage/sauvegardes et réseau/traces. Les hypothèses supposent l'arrêt des ressources inutilisées, des données synthétiques ou anonymisées, des essais de performance intermittents et **aucun environnement persistant par développeur**. La proposition dimensionne des enveloppes de consommation ; elle ne constitue pas encore une nomenclature de ressources cloud avec prix unitaires vérifiés.

| Sensibilité, mêmes 48 mois | Hypothèse | Total |
|---|---|---:|
| Sobre | Consommations et capacité de test réduites | 67 k€ HT |
| Centrale | Profils ci-dessus | 102 k€ HT |
| Soutenue | Capacité, bases et traces renforcées | 150 k€ HT |

Ces cas ne sont pas des bornes garanties. Avec les mêmes profils dilatés dans le temps, 36 mois conduiraient à **77 k€ HT**, 60 mois à **128 k€ HT**. Le calendrier de référence reste de 48 mois.

**Pourquoi c'est un ajout :** le build actif valorise les travaux et leur pilotage ; le calendrier courant ne finance pas explicitement l'hébergement avant la fin de l'intégration. Les outils à 8 € HT/JH ne démontrent pas la couverture de ces consommations cloud. La nouvelle provision suppose que ces ressources sont achetées séparément : si un contrat les inclut déjà, seule la part non couverte doit être retenue. Preuves : [valorisation du build](../tools/calculate_costs.py), [projection des dépenses](../tools/project_investment.py), [coûts communs et outillage](../source/calibration-couts.yaml).

Le budget exclut les licences/dépôts déjà financés par l'outillage au JH, les postes de travail, la main-d'œuvre de construction du socle/CI-CD, l'iPaaS de production et la haute disponibilité de production. Les services tiers payants de test restent à qualifier. **Ce n'est donc pas l'affirmation que tout le Run possible du build est couvert.** Avant d'en faire une base ferme, vérifier concurrence des tests, volumes, besoins de disponibilité et devis cloud ; si ces besoins dépassent les profils, revoir la provision.

## 5. Enveloppe centrale recomposée

Montants en k€ HT, arrondis à l'affichage. Calculs conservés au centime. L'intégration dure 34 mois après les 48 mois de build ; aucun service au-delà de la stabilisation Groupe n'est ajouté à ce tableau.

| Financement | Java / Spring Boot | .NET | Rust |
|---|---:|---:|---:|
| Intégration client, déploiements et pilotage, y compris prestations initiales reclassées | 2 775 | 2 940 | 3 356 |
| Cycle du Core pendant l'intégration, hors construction initiale | 512 | 595 | 1 014 |
| Run pendant l'intégration | 697 | 721 | 806 |
| MCO client après réception des périmètres, pendant le déploiement Groupe | 147 | 160 | 213 |
| **Sous-total : enveloppe Groupe précédente conservée** | **4 130** | **4 416** | **5 389** |
| Run : hébergement pendant le build | 102 | 102 | 102 |
| **Proposition complétée, hors construction logicielle** | **4 232** | **4 518** | **5 491** |

Les arrondis de chaque ligne peuvent différer d'un k€ de la somme affichée. Les seules évolutions optionnelles non commandées restent hors de ce total. Les 374 k€ HT de moyens techniques déjà proposés pendant l'intégration sont compris dans le Run : ils ne s'ajoutent pas une seconde fois.

La construction logicielle initiale reste distincte. Le journal de preuve la reprend une fois depuis le résultat actif afin de rendre le financement complet traçable ; ce rapprochement ne constitue pas un nouveau scénario de référence. Les tarifs et hypothèses de productivité du build sont conservés, tandis que la proposition Groupe suit ses hypothèses explicites sans gains de productivité. **Pas de conclusion d'économie face à SAP à partir de cette seule enveloppe.**

## 6. Ce que les pièces Microsoft et SAP permettent réellement

| Financement Buy | Lecture composable | Traitement financier conservé |
|---|---|---|
| Microsoft : abonnement produit | Cycle standard + droits/ressources Run, avec services inclus | Un prix groupé ; les cinq années sources sont préservées. Pas de part Core/Run/MCO inventée |
| Microsoft : support initial | Accompagnement et services dont la portée doit être rapprochée | Les 90 k€ HT restent initiaux ; aucune annuité de MCO implicitement renouvelée |
| SAP : panier logiciel / RISE | Cycle standard + droits/ressources Run | Séquence BOM intacte. Le RISE arrondi du récapitulatif n'est pas un achat supplémentaire |
| SAP : forfait MCO | Rapprochement proposé de services Run et MCO client | 250 k€ HT/an après stabilisation, indivisible faute de détail contractuel |
| SAP : monitoring | Run en horaires étendus | 450 k€ HT/an ; ne démontre pas que toutes les modifications de flux sont incluses |
| SAP : TMA évolutions | Portefeuille d'évolutions client | 350 k€ HT/an ; ne finance pas par déduction la roadmap générique SAP |

Preuves : [Microsoft, PDF p. 38](../sources/client/microsoft-1.pdf#page=38), [questionnaire Microsoft, onglet « 8. Estimations budgétaires », C13:D13](../sources/client/microsoft-questionnaire.xlsx), [SAP, PDF p. 37](../sources/client/delaware-septembre.pdf#page=37) et BOM p. 43–45. Les transcriptions et projections courantes restent dans [maintenance Microsoft](../source/maintenance/maintenance-microsoft.yaml) et [maintenance SAP](../source/maintenance/maintenance-sap.yaml).

Les forfaits remplacent les estimations des services qu'ils financent ; leurs JH diagnostiques ne s'ajoutent pas. Le registre de preuve conserve intégralement prix, séquences, dates sources, projections, `couvre` et `finance_par`. Un rapprochement `couvre` ne constitue pas une ventilation contractuelle démontrée. Les compléments de capacité, iPaaS, stockage ou DRP non confirmés ne sont pas ajoutés automatiquement. Les estimations actives de prestations client restent intactes : le registre des seuls prix publiés n'est pas présenté comme un budget Buy complet.

**Conclusion sur la comparabilité :** les responsabilités se comparent pour les cinq options ; leur séparation en montants autonomes n'est possible que lorsque les travaux ou les prix la permettent. Les forfaits groupés restent visibles comme tels.

## 7. Contrôles et décision possible

Le calcul contrôle les neuf cas (trois scénarios Groupe × trois stacks), la conservation de chaque financement au centime, les dates de réception du MCO, la séparation temporelle hébergement build/intégration et l'identité de tous les postes Buy. Sept cas volontairement invalides sont rejetés : ligne dupliquée, financement ajouté deux fois, Core classé en MCO client, MCO avant réception, hébergements superposés, ventilation Buy inventée et prix Buy altéré. Les **2 193 fichiers actifs contrôlés sont inchangés**.

Le journal s'arrête à la stabilisation Groupe. À cette frontière, un régime annuel complet devra prendre le relais une seule fois, avec ses propres calendriers Core / Run / MCO. La proposition ne modifie ni les horizons 3/5/7/10 ans, ni les paramètres, ni la reprise des simulations.

**Base utilisable devant le sponsor :** une provision d'hébergement de 102 k€ HT sous les hypothèses d'environnement décrites, une enveloppe de déploiement conservée et des responsabilités explicites. Restent à qualifier les ressources cloud, les réceptions des services partagés, la nature des modifications de flux et les inclusions des contrats. Les contrôles démontrent la cohérence comptable de la proposition ; ils ne démontrent pas la suffisance du budget ni l'absence de recouvrement contractuel non documenté.
