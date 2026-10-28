> **ARCHIVE — remplacée le 20 octobre 2026. Ne pas utiliser pour une décision budgétaire. Les estimations basse/haute de cette version ont été retirées du dossier courant. Consulter la note de décision dans le dossier principal.**

![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 19 octobre 2026

# Coûts sur quinze ans — hypothèses et calculs

Cette annexe explique le calcul du [classeur FLOW](outputs/01a1530f-f378-7fd1-9654-468c9b2141b6/FLOW_Make_abaques_et_prix_France.xlsx). La [note de décision](04-resultats-etude.md) en présente les conclusions. Les coûts couvrent la réalisation initiale, le fonctionnement, les évolutions et les souscriptions, en euros HT courants depuis un lancement commun.

## Résultats retenus

| Coûts fournisseur HT | FLOW | SAP | Microsoft |
| --- | ---: | ---: | ---: |
| **Réalisation initiale retenue** | **24,1 M€** | **17,1 M€** | **5,7 M€** |
| Plage de réalisation initiale, hors options | 24,1–45,5 M€ | 12,2–22,5 M€ | 3,3–9,1 M€ |
| Fonctionnement et licences en année 6 | 1,1 M€ | 2,3 M€ | 2,1 M€ |
| **Cumul à 3 ans** | **14,4 M€** | **19,8 M€** | **9,1 M€** |
| **Cumul à 5 ans** | **24,1 M€** | **24,2 M€** | **13,3 M€** |
| **Cumul à 10 ans** | **29,5 M€** | **35,9 M€** | **24,1 M€** |
| **Cumul à 15 ans** | **35,0 M€** | **48,9 M€** | **36,0 M€** |
| Années de fonctionnement prises en compte à 15 ans, pondérées par périmètre livré | 10,0 | 12,7 | 12,6 |

Les montants sont arrondis pour la lecture. Les calculs complets restent dans le classeur. L'année 6 est la première année commune après livraison totale ; son coût inclut l'indexation des licences à cette date. Ce n'est pas une enveloppe annuelle constante sur quinze ans. Le nominal FLOW retenu est **la borne basse de sa plage**, pas une médiane.

**Lecture :** FLOW est livré en une fois à la fin de la cinquième année. Les offres SAP et Microsoft prévoient des livraisons plus précoces. Leur coût sur quinze ans comprend donc davantage d'années de fonctionnement. La comparaison ne valorise pas financièrement cet avantage de calendrier.

## Ce que les montants comprennent

| Compris dans les coûts fournisseur | Non compris |
| --- | --- |
| Équipe de réalisation autonome en France ; construction FLOW ou adaptation des progiciels ; interfaces et sécurité ; données ; tests ; mise en service ; accompagnement fournisseur estimé. | Temps métier et gouvernance internes Beaumanoir, sauf les travaux techniques explicitement confiés au prestataire dans les estimations Buy. |
| Maintenance applicative, enveloppe d'évolutions, exploitation technique et support ou mises à niveau retenus dans le modèle. | Coût de coexistence prolongée avec les anciens SI ; coût complet de programme côté Beaumanoir ; financement et bénéfices économiques. |
| Abonnements SAP et Microsoft/K3 pendant le projet et après mise en service, avec hypothèses de réduction du périmètre et d'indexation. | Engagement commercial confirmant les réductions de licences, les compléments et les prix de prestation estimés. |

La valeur FLOW affichée est le **nominal sans options**. Les 15 % de fonctions Storeland non découvertes, la réserve de risque et le lotissement additionnel restent des options séparées. Les prix Buy ne comportent pas non plus de réserve globale de risque.

Trois statuts sont utilisés dans les justifications : **Source fournisseur** pour une donnée explicitement proposée ; **Hypothèse de l'étude** pour un tarif, un volume ou une convention estimés ; **À confirmer** pour une couverture, une responsabilité ou un engagement commercial restant à vérifier. Un calcul utilisant une hypothèse n'est pas un nouveau prix proposé par le fournisseur.

## Livraison et démarrage des coûts de fonctionnement

| Solution | Calendrier retenu depuis le lancement | Démarrage du fonctionnement | Statut |
| --- | --- | --- | --- |
| FLOW | Construction pendant 60 mois ; mise en service unique à M60. | Année 6 ; dix années pleines sur l'horizon. | Hypothèse de l'étude. |
| SAP | Pilote sur 18 mois, puis déploiement sur 12 mois ; dernière livraison M30. Upgrade initial M0–M6 en parallèle. | 20 % de l'enveloppe après le pilote, puis 80 % après le déploiement. | Durées simplifiées du COPIL ; pondérations hypothétiques. Les matrices Delaware indiquent 21 + 17 mois : divergence à confirmer. |
| Microsoft | Pilote sur 18 mois, puis quatre pôles sur 20 mois ; dernière livraison M38. | Cinq parts de 20 %, au pilote puis aux quatre livraisons M26/M30/M34/M38. | Durées globales du COPIL ; chevauchement des pôles et pondérations hypothétiques. |

Les coûts de réalisation sont étalés sur les périodes de travaux. Pour SAP et Microsoft, les compléments chiffrés n'allongent pas le calendrier dans la projection : **une équipe plus nombreuse est supposée**. Ce calendrier reste une convention budgétaire à confirmer, et non un engagement de délai.

Le fonctionnement est calculé au prorata du périmètre livré. La stabilisation de démarrage est supposée comprise dans la réalisation initiale. Le forfait SAP source est annoncé après stabilisation : son application dès les premières livraisons est une convention. Les abonnements et le support Microsoft Unified suivent leur propre calendrier contractuel et ne sont pas conditionnés par ces pondérations.

## Coût initial FLOW : 24,1 M€

Le calcul nominal est **32 100 JH × 750 €/JH = 24 075 000 € HT**. Les quatorze postes de chiffrage sont détaillés dans **Charges Flow** et dans la [note du nominal](11-cout-nominal-minimum.md).

| Travaux financés | JH, selon les clés de répartition retenues | M€ HT |
| --- | ---: | ---: |
| **Build Core system — construction du logiciel cœur** | 20 345 | 15,25875 |
| Configuration initiale | 5 295 | 3,97125 |
| Interfaces et sécurité | 6 460 | 4,84500 |
| **Total nominal** | **32 100** | **24,07500** |

Les clés de répartition sont des hypothèses ; elles ne modifient pas le total. L'option Storeland ne dispose pas encore de ventilation entre développement, configuration et interfaces.

Dans SAP et Microsoft, **Build Core system = 0 €** : le logiciel éditeur existe. L'adaptation, les développements complémentaires, l'intégration et la mise en service restent à financer. Les licences sont comptées séparément.

Les options FLOW sont calculées une fois sur le nominal : **15 % Storeland**, **10 % risque**, **0 % lotissement additionnel** aux valeurs de départ. Les activer porte le fournisseur à **30,09375 M€**, avant frais récurrents. La contribution client optionnelle de **10 %, soit 2,4075 M€**, reste séparée. Ces pourcentages sont des paramètres de simulation ; ils ne constituent pas une espérance statistique.

## Prix de prestation en France

| Prestation | Prix retenu HT | Justification et statut |
| --- | ---: | --- |
| Équipe de réalisation FLOW | **750 €/JH** | Hypothèse de l'étude : profils à 625,5 € en moyenne, +20 % de structure et marge, arrondi. |
| Équipe intégrateur SAP ou Microsoft | **1 000 €/JH** | Hypothèse commune aux deux éditeurs, avec plage 850–1 150 €. Composition d'équipe détaillée dans la [note SAP/Microsoft](15-rapprochement-buy-france.md). |
| Extensions et maintenance spécialisées progiciel | **850 €/JH** | Hypothèse d'achat, plage de travail 750–1 000 €. |
| Automatisation des tests Microsoft | **750 €/JH** | Hypothèse de l'étude : prix d'équipe de développement FLOW réutilisé pour cette prestation. |

Les [repères de marché](03-references-marche.md) distinguent tarifs freelance, salaires et prix vendus d'intégrateurs. Ils ne constituent pas des devis pour Beaumanoir. Les forfaits SAP de maintenance et de supervision sont conservés à leur prix source : **aucune majoration France automatique** n'est appliquée à une prestation dont la localisation, les effectifs et le contenu ne sont pas connus.

Le [détail de la réalisation SAP/Microsoft](15-rapprochement-buy-france.md) conserve les prix RFI, les volumes de travaux, les retraits Finance, les compléments fonctionnels, les tests, l'accompagnement et les travaux techniques confiés au prestataire. Aucune fraction du coût Make ne sert à chiffrer ces compléments.

## Maintenance, évolutions et exploitation : une année pleine

Montants avant inflation, hors souscriptions. Le support Unified Microsoft dépend du montant annuel de licences ; la valeur de base de 50 k€ ne constitue pas un tarif fixe sur quinze ans.

| Activité annuelle | FLOW | SAP | Microsoft |
| --- | ---: | ---: | ---: |
| Maintenance applicative | 450 000 € | 263 974 € | 286 594,50 € |
| Évolutions | 240 000 € | 357 000 € | 374 000 € |
| Exploitation technique / supervision des flux | 400 000 € | 450 000 € | 450 000 € |
| Support / provision de mises à niveau | 0 € | 125 000 € | 50 000 € à la base, dès l'année 2 |
| **Total hors licences, année pleine à la base** | **1 090 000 €** | **1 195 974 €** | **1 160 594,50 €** |
| Service distinct de première année | 0 € | 0 € | 90 000 € Unified / PQA |

Ces enveloppes ne décrivent pas une même prestation technique démontrée : SAP chiffre une supervision en horaires étendus ; FLOW comprend une provision technique ; Microsoft utilise la référence SAP comme hypothèse de supervision, sans doubler l'hébergement Azure déjà compris dans l'abonnement.

### FLOW

**Hypothèse de l'étude — maintenance :** 240 diagnostics × 0,5 JH, 60 correctifs × 3 JH, 12 entretiens techniques × 6 JH, 12 campagnes de régression/livraison × 6 JH, 48 reprises de flux × 2 JH et 12 revues de service × 5 JH, soit **600 JH × 750 € = 450 k€/an**.

**Hypothèse de l'étude — évolutions :** 40 règles × 2 JH + 10 fonctions/API × 12 JH + 4 changements structurants × 30 JH = **320 JH × 750 € = 240 k€/an**. Les tests ciblés sont compris dans chaque évolution ; la régression générale reste dans la maintenance.

Ces volumes supposent un produit stabilisé, une configuration gouvernée, des tests automatisés et une équipe mutualisée en heures ouvrées. Le support de premier niveau client est exclu ; aucune astreinte dédiée ni garantie de service n'est chiffrée. La provision technique de **400 k€/an** est distincte des jours de maintenance.

### SAP

**Source fournisseur — Delaware, page PDF 37 et questionnaire onglet 8 :** **250 k€/an de maintenance hors évolutions**, **350 k€/an d'évolutions**, **450 k€/an de supervision des flux**, après stabilisation. Le dossier ne ventile pas ces forfaits entre Finance et opérations ; aucun retrait Finance n'est appliqué automatiquement.

**Hypothèses de l'étude ajoutées :**

- Entretien des fonctions complémentaires : **548 JH × 3 % × 850 € = 13 974 €/an** ; maintenance totale **263 974 €**. Les 3 % sont une hypothèse de charge annuelle.
- Évolutions : 40 règles × 3,5 JH + 10 fonctions/API × 14 JH + 4 changements structurants × 35 JH = **420 JH × 850 € = 357 k€/an**. Le modèle retient **MAX(350 k€ source ; 357 k€ estimés)**, sans addition.
- Mises à niveau S/4 : **500 JH × 1 000 € / 4 ans = 125 k€/an**, soit 150 techniques + 100 adaptations + 150 tests + 50 bascule + 50 pilotage. La cadence recommandée de 2–4 ans, au moins tous les 7 ans, vient du questionnaire ; la charge de 500 JH reste hypothétique. OMSA cloud est exclu de cette provision. L'annualisation ne prédit pas l'année de facturation.

### Microsoft

**Source fournisseur :** la maintenance du produit standard, l'hébergement, les sandbox et services managés décrits page PDF 38 sont dans la souscription. Le dossier ne chiffre pas la maintenance des adaptations ni une enveloppe annuelle d'évolutions.

**Hypothèse de l'étude — maintenance :** diagnostics 120 JH, correctifs des extensions/interfaces 90 JH, tests et adaptation aux mises à jour 60 JH, coordination 24 JH, revues de configuration/sécurité 24 JH = **318 JH**. S'y ajoutent **639 × 3 % = 19,17 JH** d'entretien des nouveaux compléments, soit **337,17 JH × 850 € = 286 594,50 €/an**.

**Hypothèse de l'étude — évolutions :** 40 règles × 3 JH + 10 fonctions/API × 16 JH + 4 changements structurants × 40 JH = **440 JH × 850 € = 374 k€/an**. Les différences de charge entre les trois solutions ne sont pas des productivités mesurées. La supervision de **450 k€/an** est une hypothèse reprise de SAP. Les 60 JH annuels de tests couvrent déjà les mises à jour ; aucun second forfait de montée de version Microsoft n'est ajouté.

**Source fournisseur et hypothèses — support :** **90 k€ Unified + PQA, 200 heures d'ingénierie**, comptés une fois en année 1. Dès l'année 2 : **MAX(50 000 USD convertis ; 7,5 % × part D365 × licences Microsoft/K3 facturées)**. Le taux et le plancher viennent du questionnaire ; **70 % de D365** et **1 €/USD** sont des hypothèses. Le renouvellement reste **À confirmer** commercialement.

## Abonnements et inflation

| Paramètre | Valeur retenue | Statut |
| --- | ---: | --- |
| Inflation des prestations françaises | **0 %/an** | Hypothèse de l'étude ; modifiable. |
| Inflation technique / supervision | **0 %/an** | Hypothèse de l'étude ; modifiable. |
| Inflation des licences SAP | **4 %/an**, après un an sans hausse | Hypothèse de l'étude pour l'indexation future. |
| Inflation des licences Microsoft/K3 | **4 %/an**, après cinq ans sans hausse | Gel Dynamics documenté ; application à K3 et indexation ultérieure à confirmer. |

**Sources fournisseur :** licences SAP **790 633 / 765 823 / 973 480 / 1 270 879 / 1 270 879 €** les cinq premières années, puis dernier montant conservé avant inflation ; Microsoft/K3 **979 001,51 €/an**. Les souscriptions commencent pendant la réalisation.

**Hypothèses de réduction du périmètre commercial :**

- SAP : le COPIL distingue un écart Finance de **400 k€/an** sur un abonnement mature de **1 270 879 €**. Le ratio de **31,4743 %** est appliqué aussi aux premières années : cette extension est hypothétique.
- Microsoft : retrait de **10 % Finance**, faute de ventilation source.

Les paniers réduits restent **À confirmer** par les fournisseurs. Ces réductions ne sont pas des remises acquises. Les bases sources sont conservées dans le classeur.

Le calcul couvre **180 mois**. Les augmentations interviennent aux anniversaires du contrat, avec prorata mensuel : première hausse à M12 pour un gel de zéro ou un an, à M60 pour cinq ans. Les niveaux annuels SAP suivent les années du projet. Il n'y a pas de revalorisation automatique des prix sources 2025 vers 2026 ni de prévision de change futur.

## Incertitude et contrôles

Les plages de coût initial combinent des hypothèses de volume, de tarif et de responsabilités ; elles ne sont ni des quantiles ni des intervalles de confiance. Le point retenu est une valeur de travail. Les principales incertitudes portent sur la couverture exacte de la configuration et des exceptions, la correspondance d'un pôle Microsoft à une unité de déploiement, les tâches techniques à confier au prestataire et les licences réellement évitables.

Les **187 contrôles sur 187 réussis** vérifient formules, dates, pondérations, activations et séparation fournisseur/client, avec un échéancier mensuel recalculé indépendamment. Leur résultat est consigné dans le [journal d'audit](tools/audit_flow_workbook.log). Ils ne valident pas les charges, les tarifs ou les réductions commerciales. Une exécution dans Excel natif n'est pas affirmée.

Les versions de calcul remplacées sont conservées dans l'[archive de méthode](archives/methodes-remplacees/2026-10-19/12-modele-tco-buy-make.md). Elles ne servent pas à la décision actuelle. Les sources détaillées et les règles de non double compte figurent dans la [note SAP/Microsoft](15-rapprochement-buy-france.md).

