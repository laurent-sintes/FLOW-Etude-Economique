# FLOW et offres RFI — différences de périmètre

Preuves commerciales du 22 octobre 2026 ; lecture économique et rattachements métier mis à jour le 27 octobre 2026.

## Conclusions à retenir

- **Le RFI porte sur les opérations.** Finance et Comptabilité hors ADV sont explicitement exclues du choix de solution. Design & Development est exclu du périmètre FLOW comparé, conformément au cadrage de l’utilisateur. Une licence Finance dans un panier commercial ne change pas ce besoin. En revanche, la macro-estimation de réalisation SAP chiffre effectivement des travaux Finance hors périmètre FLOW : upgrade Finance Beaumanoir, core model Boardriders et domaines Finance/FP&A dans les lots 2 et 3 [S1]. Le budget SAP repris dans l'étude n'est donc pas encore ramené au périmètre métier commun.
- **Microsoft propose aussi Dynamics 365 Finance dans son panier de licences** [M1, p. 38], et son questionnaire prévoit une interface avec SAP FICO [M2, onglet « 2. Interfaces », ligne 12]. Son budget de réalisation ne détaille pas une transformation comptable comparable à celle de SAP. Les flux ADV et Finance nécessaires aux opérations restent à qualifier ; l'absence de cette transformation chiffrée n'implique pas l'absence de fonctions Finance dans le produit.
- **Les stocks magasin étaient prévus chez Microsoft et SAP.** La connaissance du stock par site, les mouvements, le réassort et la disponibilité ne constituent donc pas des fonctions intégralement absentes des offres Buy.
- **Microsoft proposait Dynamics 365 Commerce**, qui comporte des fonctions d’OMS/DOM et de gestion magasin. Il existe un recouvrement réel avec NewStore et SoCloz ; le remplacement complet de ces solutions n’est cependant pas établi par l’offre.
- **SAP OMSA était inclus.** Il fournit disponibilité, réservations et choix des sites de préparation. Son périmètre documenté est plus étroit que celui d’un OMS complet tel que Manhattan Active Order Management. SAP dispose aussi d’Order Management foundation ; son inclusion dans le panier RFI examiné n’est pas démontrée.
- **La cible FLOW reprend les responsabilités OMS de NewStore et SoCloz**, selon la directive de l’utilisateur. Cela ne vaut pas décision de remplacer toutes leurs fonctions POS, paiement, clienteling ou interfaces magasin.
- L’écart à évaluer concerne **les mécanismes nécessaires pour atteindre cette cible**, après crédit des fonctions réellement fournies par chaque offre. Ni « absence de stock unifié dans le Buy », ni « équivalence OMS complète acquise » ne sont démontrées globalement.

## Trois niveaux à distinguer

1. **Stock magasin connu de l’ERP** : quantités et mouvements par magasin, alimentation par les systèmes de caisse ou de logistique, transferts et réassort.
2. **Disponibilité omnicanale** : quantités vendables, réservations, stock de sécurité, fraîcheur des données et choix du lieu d’exécution.
3. **OMS complet dans la cible FLOW** : cycle de vie des commandes multicanales, coordination des exécutants, gestion des changements et des exceptions, réorientation, suivi et interventions humaines.

Une fonction présente dans le catalogue d’un éditeur n’est pas nécessairement déployée ou intégrée dans le prix proposé. Inversement, l’absence d’une preuve détaillée ne démontre pas l’absence de la fonction.

## Microsoft Dynamics 365 + K3

### Ce qui est documenté dans l’offre

- La proposition Avanade inclut **Dynamics 365 Commerce, Commerce Scale Unit Standard, E-commerce Tiers 3, Supply Chain et K3 Fashion** dans le panier de licences : [M1], page PDF 38.
- La présentation décrit un magasin associé à un entrepôt, les assortiments, statuts de stock et allocations, puis l’équilibrage du stock entre magasins : [M1], pages 20–21.
- Le questionnaire annonce une réception des mouvements WMS et magasins presque en temps réel pour une vue consolidée. **Inventory Visibility est évoqué comme une option d’architecture à discuter**, pas comme une mise en œuvre définitivement retenue : [M2], feuille `1. Besoins fonctionnels`, cellules E302 et G302.
- Des interfaces avec Cegid Y2 et Univers Retail sont prévues. Leurs flux entrants comportent ventes consolidées, valeurs de stocks magasin et demandes de réassort. L’emploi du Commerce Scale Unit pour intégrer POS et e-commerce reste une possibilité à analyser : [M2], feuille `2. Interfaces`, lignes 7–8, colonnes C à G.

### Équivalent NewStore : oui en capacités, remplacement complet non établi

La documentation de **Commerce DOM** décrit l’optimisation des lieux de préparation selon stocks, distances, coûts et contraintes [W1]. Commerce fournit aussi réception, transferts, inventaires et consultation des stocks magasin [W2]. Ce sont des capacités à créditer ; il serait faux de considérer que Microsoft doit reconstruire tout l’OMS.

Le dossier examiné ne démontre cependant pas une reprise complète des usages NewStore/SoCloz : scénarios multicanaux précis, exceptions, service client, périmètre des écrans de préparation et responsabilités entre systèmes. La présence de Commerce dans les licences ne prouve pas que tous ces parcours sont financés dans l’intégration.

Ne pas ajouter implicitement **Dynamics 365 Intelligent Order Management** comme produit distinct déjà déployé : aucune preuve d’une telle mise en œuvre n’a été identifiée dans les pièces examinées.

## SAP S/4HANA Fashion + OMSA

### Stock magasin : prévu, avec des frontières contradictoires à conserver

- **S/4 Back Office Management est coché inclus** pour les processus magasin, dont stocks et retours : [S1], page PDF 28, numéro de diapositive imprimé 33. La légende de la page PDF 21 explique que la coche signifie inclusion dans la BOM et la macro-estimation projet.
- Le questionnaire confirme les états de stock par site, entrepôt et magasin, ainsi que les paramètres de stock magasin : [S2], feuille `1. Besoins fonctionnels`, cellules E136/H136 et E300/H300.
- Mais la même réponse marque la gestion des stocks physiques multiples en lien avec WMS/magasins **non couverte**, en la rattachant aux WMS externes : [S2], cellules E302/H302.
- Des interfaces Cegid Y2 et Univers Retail, avec remontées de valeurs de stocks magasin, sont décrites : [S2], feuille `2. Interfaces`, lignes 7–8.

**Lecture retenue :** visibilité et gestion ERP des stocks magasin prévues ; étendue exacte des opérations physiques et de leur synchronisation à clarifier. Ne conclure ni « aucun stock magasin dans SAP », ni « toute la gestion magasin remplacée par SAP ».

### OMSA et OMS complet

OMSA est coché inclus : [S1], page PDF 26, diapositive imprimée 31. Sa description officielle couvre stratégies de sourcing, disponibilité par site et agrégée, réservations, simulations et prise en compte des coûts/capacités [W3]. Ces apports sont conservés dans la comparaison.

Manhattan documente une orchestration du cycle de commande de bout en bout, avec coordination des systèmes et suivi des exceptions [W4]. SAP documente séparément l’ingestion et l’orchestration du cycle de commande dans **Order Management foundation** [W5]. L’assemblage S/4 + OMSA peut déjà fournir une partie de ce cycle ; l’équivalence complète avec la cible OMS FLOW reste à démontrer, mécanisme par mécanisme.

### Autres différences explicites

- **Réassort magasin :** les réponses SAP E229/H229 à E231/H231 indiquent un moteur restant externe, avec réception des commandes magasin pour exposer la disponibilité à un OMS [S2]. SAP CAR Allocation Management est non inclus dans la page PDF 26 [S1]. Ne pas assimiler ce moteur absent à l’absence de toute allocation standard SAP.
- **Transport :** S/4 TM est non inclus dans la même page. Les opérations logistiques standard et OMSA ne sont pas, à elles seules, la preuve d’une couverture de toute l’optimisation transport FLOW.
- **iPaaS :** SAP Integration Suite est explicitement non inclus, page PDF 28 [S1]. Son achat et son exploitation doivent être traités dans les coûts, sans reconstruire des interfaces déjà comprises dans les prestations.

### ATP, CTP et dossiers

- **ATP :** disponibilité et promesse S/4 et OMSA sont créditées comme fonctions produit. Configuration et recette relèvent de l’intégration ; aucun développement ATP supplémentaire n’est retenu par défaut [S1, p. 26–27 ; W8].
- **CTP :** SAP documente Supply Creation-Based Confirmation, qui combine aATP et PP/DS pour vérifier composants et capacités et confirmer une commande [W9]. Le questionnaire SAP revendique aATP, mais la BOM Delaware ne nomme pas PP/DS et marque S/4 Fashion PP non inclus [S1, p. 24]. IBP inclus ne démontre pas à lui seul la promesse synchrone visée. Le point CTP SAP du registre de qualification porte sur les droits, le moteur et les scénarios à démontrer. Aucun développement générique additionnel ni supplément chiffré n’est retenu pour ce point ; cette absence de supplément ne démontre pas l’inclusion de tous les droits nécessaires.
- **Case Management :** S/4HANA Private Edition documente un Case Management de dossiers, objets liés, étapes, intervenants et autorisations dans Enterprise Management [W10]. La solution SAP du modèle ne doit pas le réduire au seul workflow documentaire. La qualification des dossiers Supply adaptatifs porte sur les parcours, interventions et reprises nécessaires, ainsi que sur leur inclusion dans l’offre. Les travaux client sont portés par l’enveloppe d’intégration ; aucun développement générique additionnel de moteur de dossiers n’est chiffré dans le scénario de référence.

## Correspondance avec le modèle FLOW

Les trois Make partagent la même cible ; Java, .NET et Rust diffèrent dans leur réalisation, pas dans les fonctions attendues.

| Repère métier | Capacités de la cartographie à rapprocher | Conséquence pour la comparaison Buy |
|---|---|---|
| Inventory Management | Inventory Tracking (`D01.f`), Inventory Ledger (`D01.g`), Inventory Visibility (`D01.c`) | Créditer stocks et mouvements ERP. Examiner l’histoire, les faits externes et la cohérence attendue. |
| Reservation et Availability | Reservation (`D02.c`), ATP (`D03.i`), CTP (`D03.j`), PTP (`D03.k`) | Séparer réservation, promesse et choix économique ; vérifier les garanties et l’inclusion des composants nécessaires. |
| Order Management et Fulfilment Orchestration | Les capacités de commande, Fulfilment Coordination (`D06.d`) et leurs contributions de Process Management | Rapprocher les responsabilités OMS des fonctions Commerce ou S/4 + OMSA, puis qualifier les coordinations résiduelles. |
| Réapprovisionnement, redistribution et transport | Replenishment (`D05.e`), Stock Redistribution (`D05.c`), Transport Plan Decision (`transport-plan-decision`) et leurs capacités contributrices | Qualifier les moteurs et modules du paysage retenu. Un raccordement proposé ou une exclusion commerciale ne démontre pas une fonction absente à développer. |
| Process Management | Process Definition Management (`workflow-definition-management`), Process Orchestration (`order-workflow-orchestration`), Human Task Management (`human-task-management`), Process Exception Management (`process-exception-management`) | Examiner les parcours client sans financer une deuxième fois les primitives standard ou les mécanismes partagés. |

Ces repères relient les preuves aux capacités de la [cartographie métier](../sources/cartographie-scm-2026-10-24.yaml). Leur rapprochement avec les offres est proposé ; les fonctions retenues et les frontières se lisent dans la [grille métier](grille-complexite.yaml), puis les points ouverts dans la [qualification Buy](qualification-buy.yaml).

NewStore [W6] et SoCloz [W7] confirment le recouvrement OMS : disponibilité multicanale, routage, préparation magasin et traitement des commandes. Ils ne constituent pas une liste exhaustive de fonctions à ajouter automatiquement à FLOW.

## Conséquences économiques et dépendances

Le standard du Core est acheté dans les options Microsoft et SAP. Les charges par capacité de la [calibration métier](recalibration-metier.yaml) financent uniquement le build Make. La couverture et les points ciblés Buy sont documentés dans le [registre de qualification](qualification-buy.yaml), avec les produits, preuves et décisions de traitement.

Les offres de réalisation Buy restent conservées. La préparation et la qualification client identifiées s’y ajoutent ; aucun forfait de reconstruction générique n’est appliqué par capacité. Les droits et modules non établis dans le panier restent des points à chiffrer, sans être assimilés à une gratuité ou à un développement spécifique.

L’intégration Make est financée par les travaux communs et le [déploiement Groupe](deploiement-groupe.yaml). SAP retraité et le gain de continuité restent un contrepoint décrit dans le [plan](plan-investissement.yaml), sans effet sur cette base. Toute réalisation générique additionnelle retenue en SAP serait exclue de ce repère si son équivalent est déjà financé par le Flow Core System. Les montants de référence sont dans la [projection sur dix ans](investissements-10-ans.yaml) ; le [diagnostic économique](couts-15-ans.yaml) reste une lecture distincte.

Les lots Delaware comprennent déjà des travaux WRICEF, interfaces, reprises et adaptations. La généralisation Microsoft après le pilote reste une projection du COPIL. Le [rapprochement des scénarios d’intégration](parcours-integration.yaml) précise les situations et les travaux à couvrir sans additionner une seconde fois ces prestations.

La maintenance du standard revient à l’éditeur. Les corrections, qualifications et évolutions demandées par Beaumanoir relèvent des services client ou forfaits identifiés. Seul un portefeuille d’extensions additionnelles effectivement retenu justifie un entretien autonome supplémentaire.

Les publications publiques décrivent les produits consultés ; elles ne prouvent pas rétroactivement l’inclusion d’une fonction ou d’un module dans les offres. Les preuves commerciales ci-dessous conservent leurs dates et leurs frontières.

## Sources

Les numéros de page sont ceux du PDF, à partir de 1 ; les numéros imprimés SAP sont précisés lorsqu’ils diffèrent.

- **R1 —** [Présentation du RFI](../sources/client/rfi-presentation.pdf), p. 5 : opérations et exclusion Finance/Comptabilité hors ADV.
- **R2 —** [Besoins du RFI](../sources/client/rfi-besoins.pdf), p. 32 et 36 : réassort, stocks physiques/logiques et liaison aux magasins ; p. 42 : émission des données opérationnelles vers SAP FI/CO.
- **M1 —** [Proposition Microsoft / Avanade](../sources/client/microsoft-1.pdf), p. 20–21, 38–39.
- **M2 —** [Questionnaire Microsoft](../sources/client/microsoft-questionnaire.xlsx), cellules et feuilles indiquées ci-dessus.
- **S1 —** [Proposition SAP / Delaware](../sources/client/delaware-septembre.pdf), p. 15–16, 19, 21–22, 26, 28 et 37–40 ; trajectoire, lots, JH par domaine, coches et exclusions contrôlés.
- **S2 —** [Questionnaire SAP](../sources/client/sap-questionnaire.xlsx), cellules et feuilles indiquées ci-dessus.
- **W1 —** [Microsoft — Distributed order management](https://learn.microsoft.com/en-us/dynamics365/commerce/dom).
- **W2 —** [Microsoft — Commerce inventory management](https://learn.microsoft.com/en-us/dynamics365/commerce/work-with-store-inventory).
- **W3 —** [SAP OMSA — Feature Scope Description, 10 avril 2026](https://help.sap.com/doc/08442b9d2cd744f7aecc1e08080c26f3/SHIP/en-US/FSD_SAP_OMSA.pdf), p. 6–7.
- **W4 —** [Manhattan — Global Order Orchestration](https://www.manh.com/solutions/omnichannel-software-solutions/order-management-system/global-order-orchestration).
- **W5 —** [SAP — Order Submit and Orchestration dans Order Management foundation](https://learning.sap.com/courses/exploring-sap-order-management-foundation-and-sourcing-availability/explaining-the-concept-of-order-submit-and-order-orchestration).
- **W6 —** [NewStore — Order Management](https://www.newstore.com/order-management/).
- **W7 —** [SoCloz — OMS](https://www.socloz.com/plateforme/oms/).
- **W8 —** [SAP — Advanced Available-to-Promise](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/f132c385e0234fe68ae9ff35b2da178c/1346535cf2bc410db7215ae85d8e7534.html?locale=en-US).
- **W9 —** [SAP — Supply Creation-Based Confirmation avec PP/DS](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/f899ce30af9044299d573ea30b533f1c/4c56297de7c33a0de10000000a42189c.html).
- **W10 —** [SAP S/4HANA Cloud Private Edition 2025 — Case Management, p. 139](https://help.sap.com/doc/9f8b1e91e4a442499364d2b49c8d4bdb/2025/en-US/FSD_CLOUD_PE_2025_latest.pdf).
