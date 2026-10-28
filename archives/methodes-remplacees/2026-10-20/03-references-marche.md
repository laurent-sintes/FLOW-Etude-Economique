> **ARCHIVE — remplacée le 20 octobre 2026. Les paramètres courants sont ceux du document principal ; ne pas reprendre les anciennes variantes de prix.**

![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 19 octobre 2026

---

# Références de marché et sources techniques pour FLOW Make

**Consultation :** 19 octobre 2026. Les références sont séparées entre plateformes Fashion, logiciels dont la taille est observable, dépenses publiées et composants techniques. Leur périmètre est explicité avant toute extrapolation vers FLOW.

Les indicateurs de taille et de santé de chaque entreprise citée, y compris Beaumanoir, ainsi que les critères de soutenabilité d'un investissement FLOW, figurent dans les [fiches entreprises](05-fiches-entreprises-et-criteres-investissement.md).

**Références internes prioritaires :** la [consultation Synvance 2025 et sa poursuite après juillet](07-analyse-synvance.md) comparent **SAP/Delaware** et **Dynamics 365 + K3 Fashion/Avanade** pour Beaumanoir. Leurs besoins recoupent FLOW sur commandes, stock et allocation, mais incluent aussi des fonctions et des modes de réalisation Buy différents. Delaware détaille un programme entier en JH ; Avanade détaille un pilote, tandis que le COPIL projette un budget Microsoft pour le déploiement complet. Ces budgets ne sont pas des coûts FLOW Make ; les rapprocher exige une correspondance de périmètre et de nature de dépense.

## Plateformes Fashion comparables

| Entreprise et source directe | Faits documentés | Proximité avec FLOW | Donnée de coût utilisable |
| --- | --- | --- | --- |
| **Inditex, Inditex Open Platform (IOP)** — [rapport 2019](https://static.inditex.com/annual_report_2021/en/documents/annual-report-2019.pdf), [rapport 2020](https://static.inditex.com/annual_report_2021/en/documents/annual-report-2020.pdf) | Plateforme technologique propre couvrant notamment achats, stocks, distribution et commandes ; lancée en 2018, annoncée 60 % opérationnelle en 2019, déploiement prévu dans le plan 2020–2022. Le groupe décrit un stock intégré entre magasins et en ligne et un développement interne. | **Forte proximité fonctionnelle** pour le cœur commande/stock et l'autonomie technique ; périmètre Inditex plus large, avec commerce et magasins. | Aucun coût isolé de l'IOP dans ces sources. Les investissements généraux dans magasins, logistique et technologie ne sont pas son coût logiciel. |
| **Zalando, ZEOS** — [présentation par son responsable engineering](https://jobs.zalando.com/en/blog/pieces-of-me-how-zeos-is-taking-the-guesswork-out-of-the-european-logistics), [présentation partenaires](https://partner.zalando.com/university/article/zalando-logistics-solutions-overview) | Orchestrateur des commandes entre plusieurs commerçants et réseaux de fulfillment ; 23 pays européens, plus de 40 transporteurs et gestion des retours dans la présentation de 2024. Stock mutualisé pour exécuter des commandes de plusieurs canaux selon la documentation partenaires. | **Forte proximité** pour orchestration et disponibilité multicanales ; Zalando opère aussi des services logistiques, contrairement au périmètre FLOW. | Coût de développement ZEOS non publié dans ces sources. |
| **Fast Retailing, Ariake Project** — [échange investisseurs 2018](https://www.fastretailing.com/eng/ir/library/faq20181011.html), [rapport 2018](https://www.fastretailing.com/eng/ir/library/pdf/ar2018_en.pdf) | Transformation de la supply chain, développement d'algorithmes et des systèmes qui la soutiennent ; horizon pluriannuel. Le groupe décrit également des investissements en automatisation logistique. | **Comparable pour la transformation et l'optimisation**, mais le programme inclut l'amont produit, le commerce et des entrepôts automatisés, tous plus larges que FLOW. | Les investissements systèmes ou entrepôts publiés ne donnent pas le coût du seul logiciel de pilotage. |

**Lecture pour FLOW :** Inditex est la référence fonctionnelle la plus proche pour un cœur interne couvrant achats, distribution, stock et commandes. ZEOS éclaire les contrats entre commandes, stock et réseaux de fulfillment. Fast Retailing éclaire la durée et la continuité d'une transformation supply chain. Aucune de ces trois sources ne livre un coût isolé directement transférable.

## Logiciels dont la complexité peut être mesurée

| Logiciel et sources | Mesures publiques observables | Usage possible pour FLOW | Ce qui manque |
| --- | --- | --- | --- |
| **Odoo Community** — [code source](https://github.com/odoo/odoo), [analyse Open Hub](https://openhub.net/p/odoo/analyses/latest/languages_summary), [historique éditeur](https://www.odoo.com/blog/odoo-news-5/odoo-completes-its-open-source-business-software-beyond-erp-into-digital-marketing-187) | Open Hub compte **1 980 314 lignes de code** dans son analyse du 12 octobre 2026, toutes fonctions de la distribution publique confondues. L'éditeur décrit une construction sur une décennie pour obtenir une suite complète. | Mesurer de façon reproductible les modules achats, ventes, stock et règles pertinents, puis comparer leur surface fonctionnelle et leurs tests à FLOW. | Coût réellement dépensé pour ces seuls modules ; part des contributions communautaires ; code Enterprise non public. |
| **ERPNext** — [code source](https://github.com/frappe/erpnext), [analyse Open Hub](https://openhub.net/p/erpnext/analyses/latest/languages_summary), [histoire de Frappe](https://frappe.io/story) | Open Hub compte **2 101 333 lignes de code** dans son analyse d'août 2026 ; le projet a été lancé à partir d'un développement commencé en 2006, puis commercialisé à partir de 2008–2010 selon Frappe. | Second contrôle de taille pour une application de gestion complète, en séparant les modules pertinents du reste. | Coût réel historique par module ; séparation exacte entre ERPNext et le framework Frappe. |
| **Apache OFBiz** — [dépôt](https://github.com/apache/ofbiz-framework), [historique Apache](https://cwiki.apache.org/confluence/download/attachments/48792051/ApacheconNA2015-final.pdf) | Suite de gestion open source en Java, débutée en 2001, couvrant notamment ERP, commerce et supply chain. La taille pertinente reste à mesurer sur une version figée. | Comparable utile pour la stack Java et le découpage des domaines. | Décompte des lignes de code qualifié et coût de construction ; aucun chiffre n'est imputé ici sans mesure. |

Le [calculateur Open Hub d'Odoo](https://openhub.net/p/odoo/estimated_cost) affiche **564 années-personnes et environ 31 M$** pour la base de code complète selon son modèle **Basic COCOMO**. **Ce n'est pas une dépense constatée.** Open Hub signale lui-même que le modèle peut mal correspondre aux projets open source distribués. Ce chiffre sert uniquement de test de cohérence d'une extrapolation, après avoir isolé les capacités comparables à FLOW ; il ne doit pas être multiplié ou repris tel quel dans le budget.

## Dépense logicielle publiée chez un acteur Fashion

Le [rapport annuel 2024/2025 d'ABOUT YOU](https://corporate.aboutyou.de/app/uploads/2025/05/ABOUT_YOU_FY_24_25_Report_EN_s_v1.pdf) publie **34,1 M€ de coûts de développement propres activés** sur l'exercice, contre **34,7 M€** en 2023/2024. Cela atteste qu'un acteur Fashion investit chaque année des dizaines de millions d'euros dans son infrastructure logicielle. Le montant couvre ses développements internes capitalisés à l'échelle du groupe, dont des fonctions de commerce et de plateforme B2B ; il n'est ni le coût total de toute sa technologie ni le coût d'un système semblable à FLOW. Il fournit un contrôle d'échelle financière, pas un coefficient de conversion.

## Protocole d'extrapolation des logiciels ouverts

1. Figer une version et conserver son identifiant de commit, la date et la licence.
2. Sélectionner les modules réellement comparables : commandes d'achat, commandes de vente, stock, allocation, règles, documents. Écarter finance, CRM, commerce amont, fabrication et autres fonctions hors FLOW.
3. Mesurer avec le même outil les lignes de code de production, de configuration, d'interface et de tests ; écarter code généré et dépendances tierces. Documenter les langues et le ratio tests/code.
4. Relever l'historique de développement des modules, les contributeurs et la cadence de maintenance. Les commits ne sont pas des jours de travail ; ils servent à comprendre la maturité et le rythme d'évolution.
5. Traduire la surface fonctionnelle observée en **cas d'usage et charges par rôle**, puis confronter le résultat aux prototypes FLOW et au modèle d'équipes. Utiliser les lignes de code et un modèle de type COCOMO comme contrôles secondaires ; les langages, frameworks, générateurs et exigences de qualité changent fortement la productivité apparente.

Une référence comportant à la fois **coût réel isolé, calendrier précis, effectifs et lignes de code** serait idéale ; elle n'a pas été trouvée publiquement pour un cœur supply chain Fashion comparable. Il faut donc combiner plusieurs observations sans présenter leur assemblage comme un projet témoin unique.

## Autres références à rechercher dans le dossier Beaumanoir

- **Taille fonctionnelle normalisée :** [COSMIC](https://cosmic-sizing.org/cosmic-sizing/intro/) mesure la taille des fonctions indépendamment du langage. Son [guide pour les applications de gestion](https://cosmic-sizing.org/publications/guideline-sizing-business-application-software-2/) permettrait de mesurer des processus FLOW et les fonctions comparables des logiciels ouverts sans dépendre de leurs lignes de code. Les données [ISBSG](https://www.isbsg.org/2025/02/06/functional-size-measurement/) peuvent ensuite servir à étalonner effort et productivité de projets de taille fonctionnelle comparable, si un jeu de données approprié est obtenu.
- Historique des demandes d'évolution sur SAP ECC AFS, Storeland, UR, Socloz et NewStore : coût, délai, nombre de règles et part des demandes qui auraient été paramétrables dans FLOW. C'est la meilleure mesure du bénéfice recherché.
- Charges d'intégration et d'exploitation déjà observées sur les systèmes de commandes et de stock du groupe : elles étalonnent mieux FLOW que le chiffre d'affaires d'un autre distributeur.
- Coûts de reprise des commandes ouvertes, de nettoyage des données, de tests de bout en bout et de coexistence des anciens systèmes : ces travaux peuvent dépasser la construction de certaines fonctions isolées.
- Coût annuel d'une équipe produit après mise en service : l'objectif d'autonomie exige une capacité durable de maintenance et d'évolution, à distinguer du coût du programme.

## Composants et standards

| Référence primaire | Ce qu'elle établit pour l'étude | Limite d'emploi |
| --- | --- | --- |
| [Flowable Open Source](https://www.flowable.com/open-source) et [intégration Spring Boot](https://www.flowable.com/open-source/docs/bpmn/ch05a-Spring-Boot) | Moteurs BPMN, CMMN et DMN open source sous Apache 2.0, intégrables à Java/Spring. | Ne chiffre pas les écrans, l'administration, la sécurité et le support à construire pour FLOW. |
| [Offres Flowable](https://www.flowable.com/pricing) | Distingue les moteurs open source de la plateforme commerciale et de ses fonctions d'administration et d'interface. | Les fonctions commerciales ne doivent pas être attribuées gratuitement à l'édition open source. |
| [OMG DMN](https://www.omg.org/spec/DMN/) et [OMG CMMN](https://www.omg.org/cmmn/index.htm) | Standards de modélisation des décisions et des dossiers. | Un standard ne garantit pas que toute règle métier s'y exprime simplement. |
| [Timefold Solver](https://docs.timefold.ai/timefold-solver/latest/frequently-asked-questions) et [conseils de performance](https://docs.timefold.ai/timefold-solver/latest/optimization-algorithms/overview) | Solveur open source Apache 2.0, intégré à Spring ; importance des essais sur des problèmes de taille réelle. | Les performances et la qualité des allocations FLOW restent à mesurer ; les offres commerciales ont des fonctions distinctes. |
| [Google OR-Tools](https://developers.google.com/optimization) et [installation Java](https://developers.google.com/optimization/install/java) | Bibliothèque open source d'optimisation utilisable depuis Java ; code sous licence Apache 2.0 selon son [dépôt officiel](https://github.com/google/or-tools/blob/stable/README.md). | Nécessite la modélisation et l'exploitation du problème d'allocation propre à FLOW. |
| [PostgreSQL](https://www.postgresql.org/about/licence/) | Base de données open source à licence permissive, candidate au stockage transactionnel. | La capacité réelle se démontre sur les opérations et pics FLOW. |
| [Valkey](https://valkey.io/topics/introduction/) | Stockage en mémoire open source sous licence BSD, candidat pour une projection de lecture ou un cache. | Ne définit pas à lui seul la vérité du stock ni la politique de réservation. |
| [ClickHouse, stockage colonnaire](https://clickhouse.com/resources/engineering/what-is-columnar-database) | Les bases colonnaires conviennent aux parcours analytiques ; les accès transactionnels par ligne relèvent d'un profil différent. | Guide de choix technique émis par l'éditeur, à valider par mesures FLOW. |

## Coût des compétences et méthode

| Référence primaire | Donnée utilisable | Limite d'emploi |
| --- | --- | --- |
| [Apec, rémunérations des cadres 2025](https://corporate.apec.fr/home/nos-etudes/toutes-nos-etudes/les-remunerations-des-cadres-dans-111-familles-de-metiers-edition-2025.html) | Médiane annuelle brute des cadres de 55 k€ ; détails par famille de métier dans l'étude. | Salaire brut, ni coût complet employeur, ni tarif de prestation, ni moyenne d'une équipe FLOW. |
| [Malt, baromètre développeurs 2026](https://www.malt.fr/t/barometre-tarifs/tech/) | Tarif journalier moyen affiché de 576 € pour les développeurs expérimentés actifs ; 562 € pour les développeurs back-end dans la synthèse consultée. | Tarifs de profils de plateforme, non prix négociés d'une équipe programme ; ne couvre pas tous les rôles ni les frais d'intégration. |
| [Malt, développeurs Java](https://www.malt.fr/t/barometre-tarifs/tech/developpeur-backend/developpeur-java) | **579 €/JH** pour les développeurs Java expérimentés actifs lors de la consultation du 19 octobre 2026. | Tarif freelance de plateforme ; ce n'est pas le prix vendu d'une équipe autonome incluant architecture, pilotage et qualification. |
| [Silkhom, coût d'un programme ERP, 9 octobre 2026](https://www.silkhom.com/cout-projet-erp/) | **850–1 150 €/JH** pour des intégrateurs intervenant sur des programmes d'ETI. | Ordres de grandeur annoncés par le cabinet, sans statistique de contrats signés ; leur périmètre inclut pilotage, consultants, développement, données, architecture et bascules. |
| [Dynalink, étude Dynamics France 2026](https://www.dynalink.io/etude) | **800 €/JH de médiane freelance Finance & Operations** ; enquête publiée en juin 2026, 167 répondants validés au total. | Échantillon déclaratif de freelances, distinct du prix d'une équipe intégrateur ; les 167 répondants ne sont pas tous des freelances F&O. |
| [GAO Cost Estimating and Assessment Guide](https://files.gao.gov/assets/gao-20-195g.pdf) | Décomposition des travaux, estimation par analogie ou construction détaillée, analyse des risques et incertitudes. | Méthode générale ; aucun ratio financier directement transférable à FLOW. |
| [GAO Schedule Assessment Guide](https://www.gao.gov/assets/680/674404.pdf) | Planning fondé sur les dépendances, le chemin critique et les ressources. | Ne donne pas une durée standard pour une transformation comme FLOW. |

## Mode d'emploi des références de coût

Le prix de l'étude est celui d'une **prestation vendue en France**, avec une équipe autonome. Les salaires, tarifs freelance et tarifs intégrateur sont des repères différents : ils ne se substituent pas les uns aux autres. Le prix moyen résulte d'une composition d'équipe explicite dans les onglets **Prix unitaire** du classeur.

| Paramètre retenu le 19 octobre 2026 | Prix central HT | Statut |
| --- | ---: | --- |
| Équipe de réalisation FLOW | **750 €/JH** | **Hypothèse de l'étude** : moyenne des profils de 625,5 €, majorée de 20 % de structure et marge, puis arrondie ; calcul détaillé dans la [note FLOW](11-cout-nominal-minimum.md). |
| Équipe intégrateur SAP ou Microsoft | **1 000 €/JH** | **Hypothèse de l'étude**, identique pour les deux éditeurs ; repère d'intégrateurs de 850–1 150 € ; composition de profils détaillée dans la [note de comparaison](15-rapprochement-buy-france.md). |
| Extensions et maintenance spécialisées SAP ou Microsoft | **850 €/JH** | **Hypothèse d'achat**, avec plage de travail 750–1 000 € ; aucune source publique consultée ne démontre exactement cette plage pour le futur contrat Beaumanoir. |
| Automatisation des tests Microsoft | **750 €/JH** | **Hypothèse de l'étude** : réemploi du prix d'équipe de développement FLOW pour une prestation de développement de tests ; expertise et prix à confirmer à l'achat. |

Ces prix sont des paramètres d'estimation, **pas des minimums de marché ni des devis**. La réalisation en France ne déclenche aucune majoration automatique d'un forfait source dont la localisation, les effectifs et le contenu ne sont pas connus. Les prix de licence et de support des offres Synvance sont traités séparément dans le [modèle sur quinze ans](12-modele-tco-buy-make.md).

