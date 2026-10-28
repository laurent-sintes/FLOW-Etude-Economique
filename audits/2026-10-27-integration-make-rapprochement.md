# Intégration Make : rapprochement des six blocs et base proposée

27 octobre 2026 — proposition d’opportunité, **non appliquée au scénario de référence**.

## Proposition à retenir

**Retenir une base technique V1 de 1 453 / 1 570 / 1 894 k€ HT pour Java / .NET / Rust, avec un complément de programme encore non chiffré.** Cette base permet d’instruire le chiffrage Make ; elle ne constitue pas le budget de déploiement du Groupe et ne remplace pas les 9 889 k€ HT de la référence.

Le rapprochement explique pourquoi les deux estimations divergent sans démontrer une économie de plusieurs millions : SAP finance un dispositif de programme, dont plusieurs contextes de mise en œuvre ; le catalogue Make chiffre une V1 technique complète en un lot, sans dimensionnement démontré des vagues ni de la direction de programme. Les travaux client ne disparaissent pas parce que le Flow Core System est déjà construit. Réciproquement, les prestations de transformation SAP ne se transfèrent pas intégralement à FLOW.

La proposition comporte trois choix explicites :

- conserver les treize activités, les expertises, l’accompagnement et la préparation, **sans gain de productivité anticipé** ; aucun recouvrement potentiel n’est retiré sans preuve ;
- utiliser **30 contrats de flux × 10,5 JH = 315 JH**, communs aux trois Make. Les 30 contrats restent une hypothèse du modèle. Les 10,5 JH sont le milieu de la plage Avanade de 9,5–11,5 JH/interface : une convention de travail, pas une moyenne observée ni une équivalence de contrats démontrée ;
- garder les travaux complémentaires non dimensionnés à **non chiffré**, notamment le pilotage de programme, les variantes et déploiements additionnels, les écarts d’inventaire et la prise en charge distincte du Core pendant l’intégration. Le total du programme reste `null`, jamais la somme des seuls postes connus.

| Base technique, k€ HT | Java / Spring Boot | .NET | Rust |
|---|---:|---:|---:|
| Catalogue actuel | 1 345 | 1 459 | 1 822 |
| Même catalogue, sans gains | 1 444 | 1 567 | 1 906 |
| **Proposition, sans gains et avec 315 JH de flux** | **1 453** | **1 570** | **1 894** |
| Variation des seuls flux, 285–345 JH | 1 434–1 471 | 1 550–1 590 | 1 871–1 918 |
| Programme Groupe complet | **Non chiffré** | **Non chiffré** | **Non chiffré** |

La dernière plage chiffrée ne fait varier que l’effort unitaire des 30 flux. Elle ne couvre ni l’incertitude du nombre de contrats, ni celle du programme. Les tarifs restent ceux du modèle de prestation existant, notamment du freelance direct ; ces montants ne constituent pas un prix eXalt ni un forfait intégrateur. Le rapprochement n’établit pas une préférence de stack : les différences de tarifs des métiers communs demeurent une hypothèse de sourcing à préciser.

Sources : [Avanade, page PDF 39](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Fmicrosoft-1.pdf#page=39), [hypothèses courantes](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/calibration-couts.yaml>), [volumes](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/maintenance.yaml:447>). Paramètres de la proposition et frontières dans le [YAML d’audit](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/audits/2026-10-27-integration-make-rapprochement.yaml>).

## Six blocs rapprochés, sans compter deux fois les phases SAP

Les six blocs sont des **natures de travaux sur la carte métier commune**, pas de nouveaux domaines. Les treize activités Make n’apparaissent chacune qu’une fois. Les 120 JH complémentaires d’accompagnement et les 60 k€ de préparation sont dans le sixième bloc ; la coordination technique est isolée dans le cinquième.

Pour SAP, les lignes et les phases du même tableau ne doivent pas s’additionner. La lecture applique cette priorité : retirer Finance/FP&A selon la convention actuelle ; isoler les lignes entières de gouvernance, coordination, reprise, infrastructure, formation et tests ; découper ensuite les seules lignes métier restantes entre conception/réalisation, recette et mise en service. Les petites discordances entre cellules et totaux imprimés restent dans une ligne documentaire distincte.

| Bloc de travaux | SAP hors Finance, lots 2–3 : JH isolés / k€ analytiques | Make Java proposé : JH / k€ HT | Ce qui explique ou limite la comparaison |
|---|---:|---:|---|
| Paramètres et adaptations client | 4 853 / 4 460 | 605 / 338 | Le résidu SAP comprend aussi des interfaces non isolables et des responsabilités voisines du SCM. Le Make suppose disponibles les mécanismes génériques, puis chiffre les variantes client. Les 605 JH restent une hypothèse d’ingénierie. |
| Flux et données | 705 / 648 | 595 / 332 | SAP : **reprise isolable seulement**. Make : 315 JH de flux + 280 de migration. Les deux cellules ne portent donc pas sur le même sous-ensemble. |
| Recette intégrée | 1 696 / 1 559 | 250 / 145 | SAP : SIT/UAT des lignes restantes, plus la ligne Tests ; tests des travaux transverses déjà laissés dans leur bloc. Make : INT-010, avec tests locaux dans les autres activités. Campagnes, données et acteurs ne sont pas normalisés. |
| Bascule et stabilisation | 1 298 / 1 193 | 180 / 98 | SAP : préparation finale, Go Live et Operate des lignes restantes. Make : INT-013 sur la V1, sans inventaire des vagues. Aucune multiplication par cinq n’est justifiée. |
| Gouvernance et coordination | 2 371 / 2 179 | JH non ventilés / 127 | SAP finance gouvernance et coordinations fonctionnelle/GDC. Make finance 10 % de coordination technique ; la direction de programme reste non chiffrée. Ce sont des responsabilités différentes. |
| Socle, formation et transition | 490 / 450 | 610 / 413 | SAP : infrastructure isolée seulement ; formation à zéro dans ces lignes, sans preuve d’absence de travail client. Make : environnements, déploiement logiciel, préparation du Run, formation et accompagnement, plus préparation achetée. |

**Limite immédiate : les 1 467 JH Input/Output du focus WRICEF ne sont pas localisés par ligne, phase et Finance.** Ils ne peuvent pas être ajoutés aux 705 JH de reprise, ni déplacés arbitrairement du premier bloc vers le deuxième. Le focus WRICEF totalise 2 990 JH déjà contenus dans les lots. De même, les 3 278 JH SIT/UAT et 2 095 JH Final Prep/Go Live/Operate du tableau brut ne constituent pas des suppléments aux lignes ci-dessus.

Les prix SAP du tableau sont une allocation **analytique au prix moyen propre à chaque lot**, sans ventilation commerciale disponible. Ils servent à lire le poids des travaux, pas à fabriquer des devis par bloc ni des tarifs individuels. Les écarts ligne à ligne ne sont pas des économies prouvées. Source et transcription : [Delaware, pages PDF 39–41](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Fdelaware-septembre.pdf#page=39), [cellules conservées](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/audits/2026-10-27-integration-make-rapprochement-sap.json>).

La réconciliation complète conserve **11 413 JH dans les six blocs, −4 JH de discordance documentaire, soit 11 409 JH** des lots 2–3 hors Finance. L’upgrade Finance/CCM reste séparé : **421 JH et 395 k€**, sans retrait automatique. On retrouve les **11 830 JH et 10 879 k€** du repère fournisseur retraité. Les 109 k€ de compléments de l’étude conduisent à 10 988 k€, puis le gain de continuité de 10 % à la référence de 9 889 k€. Les arrondis d’affichage en k€ ne remplacent pas les réconciliations exactes du calcul.

## Ce que la cartographie permet réellement de rapprocher

Les rattachements reposent sur la capture Beaumanoir du 24 octobre 2026, issue du backlog daté du 22 octobre : **88 capacités, neuf sous-domaines**. Les 43 situations proposées en mobilisent 82. Ni les 43 situations ni les 88 capacités ne sont des unités de facturation. Le [YAML de proposition](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/audits/2026-10-27-integration-make-rapprochement.yaml>) conserve les chemins natifs Domaine / Sous-domaine / Business Area / Capacité et les liens de preuve de chaque bloc.

| Ancrage métier | Déjà financé par le build du Flow Core System | Travaux client à conserver dans les six blocs |
|---|---|---|
| Master Plan → Stock Optimization → **Replenishment (`D05.e`)**, avec Plan Application (`D02.e`) et Transfer Order (`D04.k`) | Mécanismes de décision, application autorisée et cycle de commande génériques | Règles par contexte, données de stock, liens aux systèmes conservés ; recette du scénario `transfer-replenishment-order-driven` et bascule des engagements. Sept capacités participantes ne signifient pas sept interfaces. |
| Inventory Management → **Inventory Ledger (`D01.g`)**, Inventory Tracking (`D01.f`) et Inventory Visibility (`D01.c`) | Registres, traitements de faits et exposition génériques | Reprise et rapprochement des stocks, règles de qualité, flux WMS/POS conservés, réconciliation de bascule. Un moteur disponible n’exécute pas le nettoyage des données client. |
| Availability → **ATP (`D03.i`)**, avec Reservation (`D02.c`), Sales Order (`D04.i`) et Fulfilment Coordination (`D06.d`) | Disponibilité, réservation, engagement et coordination génériques | Paramétrage des priorités, contrats externes, données de recette ; qualification de `b2b-partial-stock` et des exceptions. Les tests génériques ne remplacent pas la recette des systèmes Beaumanoir. |
| Operational References → Reference Maintenance → **Reference Ingestion (`master-data-ingestion`)** et Inventory Management → **Accounting Data Provision (`accounting-data-provision`)** | Réception de références et fourniture des données opérationnelles | Mappings, identifiants, rejets et sorties vers Finance. Une Finance hors périmètre produit n’annule pas les raccordements comptables. |
| Process Management → **Process Definition Management (`workflow-definition-management`)**, Human Task Management (`human-task-management`) et Process, Tasks & Order Visibility (`BHV082`) | Mécanismes de processus, tâches et visibilité | Parcours client, habilitations, aides et formation ; promotion dans les environnements Beaumanoir. L’usine du produit et ses artefacts réutilisables restent distincts de la chaîne de déploiement client. |

Ces liens qualifient la **nature du livrable**, pas sa durée. Aucun prix n’est réparti sur les capacités. Les six capacités absentes des situations actuelles — contrôle d’éligibilité des prestataires et cinq capacités de gestion des références — restent dans le périmètre de la grille ; cette absence de rapprochement ne les exclut pas et ne justifie aucun forfait supplémentaire.

SAP utilise un autre découpage : sa ligne « Execute Supply Chain » vaut zéro alors que des travaux SCM sont chiffrés dans Sell, Procure, Plan Supply et Retail Store Operations. « Manage Product Lifecycle » et « Market Goods & Services » peuvent aussi traverser Design, Commerce ou Procurement. **On ne peut donc pas assimiler une ligne SAP à un domaine FLOW, ni supprimer une ligne entière parce que son intitulé semble voisin.** La Finance a été retirée par une convention existante ; le reste n’est pas un périmètre SCM automatiquement normalisé.

Sources : [grille native](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/grille-complexite.yaml>), [situations proposées](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/parcours-integration.yaml>), [travaux du Core](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/recalibration-metier.yaml>), [frontières des offres](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/ecarts-perimetre-flow-rfi.md>).

## Les volumes de déploiement : des preuves, mais pas encore une addition

La consultation décrit **deux ensembles SI et huit instances Storeland au total, une par marque** ; les applications conservées ne sont pas toutes arrêtées. MAP/CBS sont volontairement absents du questionnaire d’interfaces. Les 30 contrats FLOW et les 40 interfaces Avanade ne constituent donc pas un inventaire exhaustif rapproché. Huit instances ne signifient pas huit vagues. [Présentation RFI, pages PDF 3–5 et 7](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Frfi-presentation.pdf#page=4).

Le COPIL projette **un pilote et quatre lots supplémentaires**, mais l’organisation pôle/pays reste à affiner ; Sarenza est signalé hors du périmètre fonctionnel et de la volumétrie initiale. Cette projection Microsoft ne devient pas un plan Make et n’autorise pas à élargir silencieusement FLOW. [COPIL, pages PDF 7–8](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Fcopil-5.pdf#page=7).

Avanade publie un abaque par **unité géographique** : 100 JH pour du support seul avec responsabilité client plus forte ; 200 JH avec bonne adhérence et RACI du pilote ; 400 JH avec adhérence moyenne et ce même RACI. Le cas 100 JH n’est pas la borne basse d’un service identique. [Avanade, page PDF 40](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Fmicrosoft-1.pdf#page=40). Le questionnaire conditionne l’abaque aux hypothèses, tâches et kit de déploiement : [feuille « 8. Estimations budgétaires », D22 et B23:C23](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/sources/client/microsoft-questionnaire.xlsx>).

On peut tester **quatre unités distinctes et additionnelles**, si chacune correspond effectivement à l’abaque : 400 / 800 / 1 600 JH. Au mix de travail V1 Java, cela représente respectivement **226 / 452 / 904 k€ HT isolés**, sans ajout automatique de pilotage. C’est un diagnostic de staffing : le mix d’un déploiement n’est pas fourni par Avanade, et un pôle COPIL n’est pas démontré égal à une unité géographique.

**Ces paquets ne sont pas additionnés à la base proposée.** Le catalogue Make finance déjà une V1 complète, pas seulement un pilote. Les paquets peuvent recouvrir paramètres, flux, données, recette, formation et bascule. Il faut identifier ce qui s’ajoute réellement ; ajouter quatre paquets puis répéter les activités de recette et de migration compterait potentiellement deux fois le même travail.

## Maintien du Core : un service possible, pas une surcharge acquise

La période d’intégration de référence couvre 34 mois après le build. Les unités de maintenance existantes permettent de tester un service de correctifs et de qualification des releases : 12 corrections et quatre campagnes par an. **Sans gain de productivité et à prix constants**, ce candidat représente **512 / 595 / 1 014 k€ HT** sur 34 mois pour Java / .NET / Rust. La variante suivant l’indexation du calendrier courant donne 579 / 673 / 1 146 k€ ; ce sont deux lectures exclusives du même service, pas deux postes.

Ces montants restent **hors de la base proposée**. Si la responsabilité est déjà comprise dans la garantie du produit, le build ou la stabilisation, il n’y a pas ce supplément. Si une prestation distincte est nécessaire, seuls ses travaux non déjà financés doivent être retenus. La prise en charge supplémentaire effective demeure non chiffrée.

Les six évolutions génériques annuelles de MAI-009 sont une commande distincte : **225 / 268 / 416 k€ HT** sur 34 mois à prix constants et sans gain. Elles ne sont pas une obligation de maintien ni une roadmap automatiquement achetée. Le calcul conserve séparément corrections, releases, évolutions et variantes ; aucune annuité complète de Run n’est ajoutée à l’intégration. [Unités actives](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/recalibration-metier.yaml>) et [règles de service](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/maintenance.yaml>).

## Base défendable devant le sponsor

La base proposée est une **assiette technique d’opportunité**, dont les JH hérités restent des hypothèses. Les rapprochements apportent des frontières et quelques abaques vérifiables ; ils ne valident pas rétrospectivement toutes les charges. La carte permet de garder le même périmètre métier, mais ne prouve ni le nombre de vagues ni la capacité de livraison.

Pour disposer d’une enveloppe programme, trois décisions suffisent à structurer la prochaine estimation, sans spécification détaillée :

1. **Nommer les unités de déploiement et les écarts à la V1 commune** : pôles/instances concernés, règles et contrats partagés ou nouveaux, reprises, campagnes de recette et bascules. Ne pas multiplier le Core ni les mécanismes communs.
2. **Fixer les responsabilités externes et internes** : pilotage technique, direction de programme, coordination fonctionnelle, qualité des données, acceptation et formation. Un transfert de travail vers Beaumanoir ne constitue pas une économie totale ; aucun temps interne n’est ajouté ici.
3. **Attribuer la prise en charge du produit pendant l’intégration** : garantie/correctifs, qualification des releases et éventuelles évolutions commandées, en rapprochant chaque prestation de son financement existant.

Formulation sponsor : « Nous pouvons expliquer une base technique d’intégration FLOW de 1 453 k€ HT en Java, avec deux variantes de réalisation. Nous ne la présentons pas comme le prix de généralisation au Groupe. Les pièces montrent des contextes SI et des responsabilités de programme plus étendus que les seules activités chiffrées. Nous conservons donc le repère macro séparément jusqu’à ce que les lots et les responsabilités complètent cette base. »

**La référence reste 9 889 k€ HT pour les trois Make.** Le test de décision à **10 988 k€ HT sans gain de continuité** conserve son rôle de repère SAP retraité, pas de prix FLOW validé ni de borne haute. Il n’est pas additionné à la proposition technique. Je ne recommande pas de remplacer maintenant la référence par 1 453–1 894 k€, ni de choisir un montant intermédiaire sans travaux identifiés.

## Vérification et pièces de calcul

Le [calcul reproductible](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/audits/2026-10-27-integration-make-rapprochement-calcul.py>) lit les sources courantes et la [définition de proposition](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/audits/2026-10-27-integration-make-rapprochement.yaml>), puis écrit uniquement les [preuves d’audit](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/audits/2026-10-27-integration-make-rapprochement-preuves.json>). La [transcription SAP](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/audits/2026-10-27-integration-make-rapprochement-sap.json>) conserve les cellules, totaux et empreinte du PDF ; pages vérifiées visuellement.

Contrôles réalisés : unicité des treize activités ; identifiants et chemins métier valides ; conservation des six blocs Make au centime ; égalité du catalogue courant avec les résultats actifs ; partition SAP sans double compte ligne/phase et conservation des prix en fractions exactes ; reproduction des 11 830 JH et du retrait Finance ; distinction des coûts inconnus ; empreintes identiques des **1 809 fichiers suivis** dans les sources, la configuration, les outils et les vues avant/après le travail. Les résultats, annuités, horizons, paramètres et fichiers de simulation actifs n’ont pas été modifiés. Aucun changement de l’application n’est nécessaire pour consulter cette proposition d’audit.
