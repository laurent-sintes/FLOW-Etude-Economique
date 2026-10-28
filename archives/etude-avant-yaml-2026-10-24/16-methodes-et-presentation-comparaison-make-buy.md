> **Historique — retiré de la base active le 24 octobre 2026.** Les hypothèses et résultats de cette note sont remplacés par le [modèle YAML actuel](../../source/README.md).

![Logo eXalt](<../../assets/exalt-logo.png>)



**Laurent Sintès** · 21 octobre 2026



---



# Comparer les coûts de FLOW SAP et Microsoft



## Résultat de la recherche



Des modèles réutilisables existent pour organiser les calculs et présenter les résultats. Pour FLOW, la combinaison la plus utile est **Should Cost Modelling pour la méthode et la synthèse comparative**, **Smartsheet pour la grille des postes**, et **Thoughtworks / FinOps pour vérifier la couverture des services**.



La comparaison distingue les dépenses techniques des prestations humaines : **400 k€/an de moyens techniques FLOW ne désignent pas la même prestation que 450 k€/an de supervision des flux SAP**. La comparaison distingue la plateforme d'exécution, l'intégration récurrente et l'exploitation, puis rattache chaque dépense à son enveloppe. Une inclusion dans un abonnement ne constitue pas une gratuité.



Les recommandations sont traduites en postes de coût et en abaques dans le [modèle de comparaison](<12-modele-tco-buy-make.md>). Les coûts déjà financés sont reclassés ; seuls les besoins supplémentaires identifiés donnent lieu à des provisions. Les prix catalogue, les données fournisseur et les hypothèses restent séparés.



## Modèles et méthodes réutilisables



| Référence | Ressource disponible | Usage pour FLOW | Limite |

| --- | --- | --- | --- |

| [Cabinet Office — Should Cost Modelling](https://www.gov.uk/government/publications/should-cost-modelling-tools-and-templates) | Guides et exemple Excel public ; modèle de construction, registre des hypothèses et contrôles. | Organiser les données, hypothèses, calculs et résultats ; conserver la justification de chaque montant. | Cadre général de comparaison de modes de prestation, à alléger pour les décideurs. |

| [Smartsheet — TCO et ROI](https://www.smartsheet.com/roi-calculation-templates) | Modèle Excel public présentant des catégories de dépenses par année et des totaux. | Reprendre les postes et la grille pluriannuelle, avec hébergement explicitement séparé. | Trois années et aucun graphique dans ce fichier ; le ROI reste distinct du TCO. |

| [Thoughtworks — Build versus buy](https://www.thoughtworks.com/content/dam/thoughtworks/documents/e-book/tw_ebook_build_vs_buy_2022.pdf) | Guide de 37 pages, notamment infrastructure p.21 et TCO p.30–31. | Comparer des services à disponibilité, résilience et reprise équivalentes ; vérifier les environnements et les dépendances. | Guide de décision, sans tableur à remplir ni abaque de coût transférable. |

| [FinOps Foundation — SaaS](https://www.finops.org/framework/technology-categories/saas/) | Cadre de gestion des coûts SaaS. | Vérifier abonnement, consommation, support, capacité contractuelle et frais connexes. | Les montants dépendent des contrats et des usages propres à Beaumanoir. |

| [TBM Council — Taxonomy](https://www.tbmcouncil.org/taxonomy/) | Classification des dépenses technologiques et des services rendus. | Distinguer la facture achetée — logiciel, cloud, services — du service financé — application, calcul, stockage, réseau, exploitation. | Référentiel de classement ; aucun prix ni pourcentage de répartition imposé. |

| [River — Build vs Buy Decision Pack](https://meetriver.com/templates/vendor-and-build-decision-pack) | Pack annoncé de deux documents Word et trois CSV, avec exemple fictif. | Vérification de la maintenance par tâches et de la sortie de chaque solution. | Exemple sur trois ans, sans valeur de benchmark pour FLOW ; téléchargement du pack non examiné ici. |



La [méthode GAO](https://www.gao.gov/products/gao-20-195g) complète ces ressources pour la traçabilité des estimations. Son annexe logiciel rappelle la nécessité d'inclure les tests, l'infrastructure et le maintien après déploiement, au-delà du code initial.



### Fichiers de référence conservés dans le projet



- [Modèle TCO et ROI Smartsheet](<../../sources/recherche-tco-2026-10-20/smartsheet-tco-roi-template.xlsx>), obtenu depuis le [lien de téléchargement de l'auteur](https://www.smartsheet.com/sites/default/files/IC-Total-Cost-of-Ownership-TCO-ROI-Calculator-Template-9436.xlsx).

- [Exemple Should Cost Modelling du Cabinet Office](<../../sources/recherche-tco-2026-10-20/cabinet-office-illustrative-scm.xlsx>), obtenu depuis le [lien officiel](https://assets.publishing.service.gov.uk/media/60a4f096e90e07356e2bbc83/SCM_Case_Study_Illustrative_SCM_V1_May_2021.xlsx).

- [Guide Thoughtworks](<../../sources/recherche-tco-2026-10-20/thoughtworks-build-vs-buy-2022.pdf>).



Ces fichiers sont des références de méthode et de forme. Leurs éventuels exemples chiffrés ne constituent pas des données de coût FLOW. Le modèle Cabinet Office de construction au format XLSM n'est pas nécessaire pour reprendre ces principes.



### Ce que contiennent les deux classeurs examinés



Le modèle **Smartsheet** comporte un exemple, une grille vierge et un avertissement, soit trois onglets. Il présente trois années, le total du cycle de vie et la part de chaque poste. L'hébergement figure explicitement en **B16**, à côté des licences, de la maintenance et du développement. Il ne comporte aucun graphique ni comparaison simultanée de plusieurs solutions.



L'exemple **Cabinet Office** comporte dix-huit onglets et trois options : construire/exploiter, louer/exploiter, externaliser. Il sépare les entrées, les calculs et les sorties. **oFinancials** présente les coûts annuels et cumulés ; **oDashboard** contient trois graphiques : coût nominal total, coûts annuels avec inflation et valeur actualisée. Les trente et une périodes annuelles et le cas de centre de contacts sont à remplacer par le périmètre FLOW.



Le dashboard du Cabinet Office est donc la référence de comparaison la plus proche parmi ces fichiers. Sa mise en page et ses petits caractères doivent être adaptés à la lecture décideur. Aucun des deux fichiers n'intègre directement les horizons 3/5/10/15 ans et les jalons requis pour FLOW. Les modèles consultés sont joints dans le registre des sources.



## Plateforme d'exécution et services inclus



### Ce que les propositions Synvance couvrent



**Microsoft Dynamics / K3 :** la proposition Avanade n°1, page PDF 38, décrit une souscription comprenant licences, maintenance produit, infrastructure, hébergement Azure, sandbox et services managés. Le questionnaire, onglet 8 C26/D26, confirme l'inclusion des environnements sandbox/UAT prévus. Il ne démontre pas une capacité ou des environnements supplémentaires illimités.



**SAP :** la proposition repose sur RISE et S/4HANA Cloud private edition, avec une infrastructure managée. Les pages PDF 43–45 contiennent déjà mémoire de production et hors production, stockage additionnel et une ligne DRP. Le questionnaire budget C12/D12 décrit licences et infrastructures ; C26/D26 rattache les environnements supplémentaires au panier proposé. Le contenu de ce cloud privé managé se vérifie à partir de l'offre, plutôt que par assimilation à un SaaS public uniforme.



**CPI signifie Cloud Platform Integration**, nom historique de l'outil d'intégration cloud de SAP, aujourd'hui associé à **Cloud Integration dans SAP Integration Suite**. Il assure les échanges et transformations de données entre systèmes. Le développement d'une interface et l'abonnement à sa plateforme d'exécution sont deux dépenses distinctes. La [documentation SAP](https://userapps.support.sap.com/sap/support/knowledge/en/3133030) rapproche ces appellations. DRP désigne ici le plan de reprise d'activité, ou PRA.



Les documents publics confortent ces principes sans remplacer les offres : [Microsoft décrit les environnements du cloud managé](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/organization-administration/architecture-overview), tandis que le [guide de service SAP](https://www.sap.com/docs/download/agreements/product-use-and-support-terms/service-description-guides/rise-with-sap-s4hana-cloud-private-edition-service-description-guide-english-v6-2024.pdf) distingue capacités, environnements et options de reprise selon les souscriptions.



## FLOW : ressources, construction et exploitation



### Les 400 k€/an financent une plateforme



Cette enveloppe reste inchangée. Sa ventilation budgétaire est rendue modifiable :



| Ressources, après livraison | Hypothèse de quantité et de prix | Coût annuel |

| --- | --- | ---: |

| Calcul applicatif | 20 nœuds équivalents × 250 €/mois | 60 000 € |

| Bases transactionnelles répliquées | 4 services × 2 000 €/mois | 96 000 € |

| Stock/disponibilité en mémoire et index | 3 clusters × 1 000 €/mois | 36 000 € |

| Files et événements | 2 clusters × 1 000 €/mois | 24 000 € |

| Solveur et traitements batch | 4 nœuds équivalents × 250 €/mois | 12 000 € |

| Documents, archives et sauvegardes | 80 To moyens × 25 €/mois | 24 000 € |

| Réseau, frontal et sécurité | 1 ensemble × 2 000 €/mois | 24 000 € |

| Métriques, logs et alertes | 1 ensemble × 2 000 €/mois | 24 000 € |

| Site de reprise, ressources et données | 1 ensemble × 4 000 €/mois | 48 000 € |

| Environnements permanents hors production | 3 × 1 000 €/mois | 36 000 € |

| Outils techniques propres au produit | 40 comptes ou équivalents × 400 €/an | 16 000 € |

| **Provision existante ventilée** | | **400 000 €/an** |



Ces prix et quantités sont des **hypothèses de budget**, pas un devis cloud ni un dimensionnement testé. Les [tarifs OVHcloud France](https://www.ovhcloud.com/fr/public-cloud/prices/) servent seulement de contrôle de plausibilité de ressources : le coût d'une VM isolée ne prouve pas le prix d'une plateforme complète. L'exploitation humaine n'est dans aucune des lignes ci-dessus.



### Les factures de construction sont distinctes



Les JH d'ingénierie plateforme sont compris dans les prestations. Les ressources consommées pendant le chantier sont estimées séparément :



| Année de construction | Environnements allégés | Campagnes temporaires de charge | Coût annuel |

| --- | --- | --- | ---: |

| 1 | 2 × 1 000 €/mois × 12 | — | 24 000 € |

| 2 | 3 × 1 000 €/mois × 12 | — | 36 000 € |

| 3 | 4 × 1 500 €/mois × 12 | 2 mois × 2 000 € | 76 000 € |

| 4 | 5 × 1 500 €/mois × 12 | 2 mois × 2 000 € | 94 000 € |

| 5 | 6 × 2 000 €/mois × 12 | 6 mois × 2 000 € | 156 000 € |

| **Total** | | | **386 000 €** |



Les ressources de construction s'arrêtent à la livraison ; le panier de production démarre ensuite. Aucun mois ne finance deux fois le même service. Les outils génériques du fournisseur restent dans son forfait et ne donnent lieu à aucun supplément.



## Services annuels retenus



| Prestations humaines en année pleine | FLOW | Microsoft | SAP |

| --- | ---: | ---: | ---: |

| Maintien, exploitation et pilotage | 7 × 200 JH × 750 € = **1,05 M€** | 6 × 200 JH × 850 € = **1,02 M€** | Maintenance 250 k€ + supervision 450 k€ = **0,70 M€** |

| Évolutions fonctionnelles | 2 × 200 JH × 750 € = **0,30 M€** | 2 × 200 JH × 850 € = **0,34 M€** | Forfait **0,35 M€** |

| **Total services humains** | **1,35 M€/an** | **1,36 M€/an** | **1,05 M€/an** |



Les capacités FLOW et Microsoft sont des hypothèses de dispositif fournisseur, en heures ouvrées françaises. Les forfaits SAP proviennent du RFI Delaware ; la supervision comprend des horaires étendus et la couverture de la cible reste à confirmer. Une personne-an représente 200 jours de travail pour le contrat. Les effectifs peuvent être partagés entre plusieurs intervenants.



Le maintien finance les corrections, les versions techniques courantes, l'exploitation et le pilotage. Les évolutions financent les nouvelles fonctions, y compris les versions fonctionnelles du Core FLOW. Aucune deuxième enveloppe d'exploitation n'est ajoutée. La capacité d'évolution ne garantit pas un même nombre de fonctions livrées selon la solution.



Les ressources FLOW de **400 k€/an**, hors personnel, portent son fonctionnement complet à **1,75 M€/an**. Les licences, le support et les ressources Buy sont calculés séparément. Avec indexation, le fonctionnement complet moyen des années 6 à 15 atteint **2,54 M€/an SAP** et **2,56 M€/an Microsoft**. Ces moyennes ne sont pas les tarifs d'une année de départ.



Le service complet commence après le mois des premiers usages : M60 FLOW et M18 SAP/Microsoft, soit respectivement 10 et 13,5 années de service sur quinze ans. Les interventions de stabilisation financées au projet sont distinctes du service courant. Astreinte et migrations majeures sont des options inactives.



La [méthode](<02-methode-estimation.md>) justifie les compétences et capacités. Le [guide](<13-audit-classeur-excel.md>) indique les cellules modifiables. L'équivalence contractuelle des services n'est pas démontrée.



## SAP : CPI hors budget, crédit BTP à imputer



La [page officielle SAP Integration Suite](https://www.sap.com/products/technology-platform/integration-suite/pricing.html) présente les offres et leurs unités de facturation, dont les 10 000 messages mensuels inclus dans Standard. Les montants retenus dans cette étude restent **4 635 €/tenant/mois** et **6,08 €/mois par bloc additionnel de 10 000 messages**. **Ces montants sont conservés comme hypothèses de calcul : la page accessible ne permet pas de les reconfirmer en euros.** Ils ne constituent ni un devis France ni un prix négocié pour Beaumanoir. Standard est retenu pour les API, flux tiers/B2B et événements ; le Starter décrit sur cette page est limité à dix iFlows personnalisés. Référence vérifiée le 21 octobre 2026.



Le panier retient **deux tenants cloud distincts**, production et recette. Le [guide contractuel SAP BTP v8/2024, §68](https://assets.cdn.sap.com/agreements/product-use-and-support-terms/service-description-guides/sap-business-technology-platform-service-description-guide-english-v8-2024.pdf) distingue le tenant Standard et le runtime Edge Integration Cell inclus ; ce dernier ne prouve pas un deuxième cloud de recette gratuit. L'architecture à deux tenants reste une hypothèse simplifiée ; le [Discovery Center SAP](https://discovery-center.cloud.sap/serviceCatalog/f810c887-8d25-4942-9849-354837951066?tab=service_plan) recommande d'aligner les environnements d'intégration sur ceux de l'ERP, idéalement trois niveaux.



### Volumes payants estimés



| Échanges mensuels de production, hypothèses | Calcul | Messages |

| --- | --- | ---: |

| Commandes et événements de cycle de vie | 50 000 commandes × 20 échanges | 1 000 000 |

| Stock/disponibilité, mises à jour agrégées | 200 000 lots d'opérations × 10 échanges | 2 000 000 |

| Achats, retours, intercompany et exceptions | 100 000 opérations × 10 échanges | 1 000 000 |

| Référentiels et contrôles périodiques | 100 000 opérations × 10 échanges | 1 000 000 |

| **Production** | | **5 000 000/mois** |

| Recette | Hypothèse séparée | **500 000/mois** |



Les 600 000 commandes annuelles implicites sont une hypothèse ; ce n'est pas un volume Beaumanoir confirmé. Les pièces vendues ne sont pas converties en commandes. Le traitement par lots, la taille des messages et les exemptions contractuelles modifieront la métrique facturable ; le modèle retient la taille unitaire de référence et des volumes déjà considérés payants.



**Coût brut annuel à pleine charge : 2 × 4 635 × 12 + (499 + 49) × 6,08 × 12 = 151 222,08 €.** La recette seule vaut **59 195,04 €/an** et commence dès le chantier. Le tenant de production commence aux premiers usages ; son trafic suit le périmètre livré. La recette reste ensuite active.



**Le voucher BTP est inclus dans l'offre source, mais son montant n'est pas indiqué.** **Aucun crédit n’est imputé au budget, faute de valeur documentée** ; cela ne signifie pas absence de crédit disponible. Le [contrat RISE private edition v10/2023, §1.4](https://assets.cdn.sap.com/agreements/product-use-and-support-terms/cls/en/rise-with-sap-s4hana-cloud-private-edition-supplement-english-v10-2023.pdf) renvoie au bon de commande. Aucun montant de voucher n'est inventé à partir des utilisateurs ou de l'abonnement.



Le complément à payer est **MAX(0 ; CPI brut − crédit réellement imputable)**. Seule la part disponible après les autres usages BTP doit être déduite. Le brut constitue une provision conservatoire et conditionnelle tant que les crédits et les remises ne sont pas valorisés. Aucun coût d'hébergement RISE ou de supervision humaine n'est ajouté dans ce panier.



## Microsoft : une provision externe conditionnelle



Les environnements prévus pour D365/K3 restent financés dans la souscription. La [documentation Microsoft sur le déploiement cloud](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/deployment/cloud-deployment-overview) distingue les environnements prévus et les environnements additionnels achetables ; elle ne démontre pas une capacité illimitée.



Une provision de **45 k€/an** couvre uniquement les compléments qui seraient exécutés hors du standard : **12 k€ de développement/recette**, **24 k€ de production** et **9 k€ de messages, frontal API et journaux**. Elle démarre avec la recette pendant le chantier, puis ajoute les 33 k€ de production selon les livraisons. Les coûts unitaires sont des hypothèses d'ingénierie : les pages de [tarification Azure Logic Apps](https://azure.microsoft.com/fr-fr/pricing/details/logic-apps/) décrivent les compteurs, mais n'ont pas fourni ici de prix régionaux exploitables.



Les budgets de recette et de production externes sont modifiables dans Hypothèses. Si les droits et capacités D365/K3 couvrent ces besoins, ces budgets peuvent être annulés. Aucun nouvel hébergement du progiciel, moteur d'allocation ou OMS complet n'est acheté dans cette provision.



## Hypothèses communes et limites



- **Quantités constantes, croissance 0 %.** L'inflation modifie le prix d'une unité ; elle n'achète pas de nouveaux utilisateurs, messages, To ou environnements. Les coefficients de capacité et de licences restent distincts.

- **Inflation des prestations et ressources techniques : 0 %** dans le cas de référence. L'intégration CPI SAP utilise **4 %/an de prix**, séparément du crédit non valorisé. Les souscriptions standard gardent leurs propres gels et indexations.

- **Distinguer sources et hypothèses de service.** SAP conserve les forfaits Delaware et leur monitoring en horaires étendus. FLOW/Microsoft sont estimés en heures ouvrées. Les capacités et SLA ne sont pas démontrés équivalents ; les écarts de budget ne sont pas des remises prouvées.

- **Sortie de solution non financée.** Aucune sortie automatique n’est supposée en année 15 ; une estimation de sortie nécessiterait de préciser la cible et les données à transférer.

- **Contributions internes, support L1 et coexistence** suivent les exclusions décidées pour l'étude. Ils ne deviennent pas implicitement des coûts nuls du programme complet.



Les tableaux de ressources de cette annexe et la méthode de service documentent les quantités, prix et frontières. Les cumuls à 3/5/10/15 ans résultent du calendrier et de l’indexation du classeur.

