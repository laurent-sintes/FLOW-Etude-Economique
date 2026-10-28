> **Historique — retiré de la base active le 24 octobre 2026.** Les hypothèses et résultats de cette note sont remplacés par le [modèle YAML actuel](../../source/README.md).

![Logo eXalt](<../../assets/exalt-logo.png>)



**Laurent Sintès** · 19 octobre 2026



---



# Périmètre de l'étude Synvance 2025 et des offres RFI : comparaison avec FLOW Make



Les montants sont des estimations RFI de 2025, non des offres contractuelles. Les pièces sont accessibles dans le [registre des sources](<20-registre-sources.md>). La mission Synvance a été clôturée le 4 juillet 2025 ; l'offre SAP/Delaware de septembre est une poursuite du RFI par Beaumanoir.



Le [rapprochement France](<15-rapprochement-buy-france.md>) distingue les prestations déjà proposées, les compléments conditionnels et les hypothèses de transfert des tâches techniques. La construction du Core éditeur reste à zéro pour les deux options Buy. Les développements et interfaces du RFI ne sont pas ajoutés une seconde fois.



## Ce que l'étude mesurait



Le dossier de consultation daté du **28 mai 2025** portait sur le choix d'un **ERP Achat/Vente** commun aux marques historiques et à Boardriders, connecté aux applications spécialistes du SI. Il visait à remplacer Storeland et le SAP de Boardriders et précisait que les applications à conserver dans l'architecture cible n'étaient pas encore arrêtées. La consultation de trois semaines était une **sélection de logiciel**, non d'intégrateur, avec des premières estimations de mise en œuvre et de coûts récurrents.



**Deux trajectoires Buy ont été comparées à la fin du RFI :** SAP S/4 Fashion intégré par Delaware et **Microsoft Dynamics 365 avec K3 Fashion**, intégré par Avanade. K3 est un éditeur indépendant avec une souscription propre. Le COPIL 4 de juillet comparait Microsoft aux autres candidats. Après la clôture de Synvance le 4 juillet, Beaumanoir a poursuivi directement les échanges avec Delaware et Avanade ; le COPIL 5 du 17 septembre présente les deux trajectoires côte à côte.



**Correction de la première lecture :** il est faux d'affirmer sans nuance que « l'OMS était hors du périmètre chiffré » ou que « le Retail était flou ». La séparation entre **étude d'un OMS spécialisé**, **fonctions de gestion des commandes demandées à l'ERP**, et **composants proposés par un candidat** est déterminante.



| Étape et pièce | Ce qu'elle dit réellement | Portée de la preuve |

| --- | --- | --- |

| COPIL 1 du 1er avril, **slide 8** | « L'OMS et le fulfillment » sont placés hors de l'étude ERP, avec les activités POS. En revanche, stock magasin et moteur simple de réassort sont à étudier. | Intention de délimitation **initiale** ; elle ne suffit pas à définir le contenu du RFI ultérieur. |

| Synthèse des besoins cibles du 21 mai, **slides 3–4** | La liste se limite à ce qui doit être porté par l'ERP ; applications périphériques présumées reconnectées. Le schéma place dans l'ERP les commandes magasins et B2C, le Wholesale, les stocks et les allocations. | Périmètre cible de l'ERP, encore itératif ; le sort exact des satellites n'est pas fixé. |

| Dossier RFI du 28 mai, **pages 5–8** | Achats, D2C (magasins et e-commerce), Wholesale, stocks, allocations, distribution/livraison et retours sont demandés. La page 8 souligne que les besoins « évidents » d'un ERP ne sont pas tous détaillés. | Le RFI contient déjà une part substantielle des capacités de gestion de commandes et de stock de FLOW. |

| Synthèse des besoins jointe au RFI, **pages 24–27, 31–40** | Disponibilité et date promise à la prise de commande ; réservation sur stock ou commande d'achat ; allocation multicritère, immédiate/différée, par canal ; recalcul et simulation ; commande B2C détaillée ; réassort magasin ; ordres de préparation, expéditions partielles, suivi et retours. | Fonctions proches de l'OMS et de l'orchestration de fulfillment **explicitement demandées à l'ERP**, même si un OMS autonome n'était pas étudié comme produit séparé. |

| Q&A candidats du 10 juin, **slides 6, 19, 27** | Lotissement et architecture cible non arbitrés ; WMS, TMS, CRM et comptabilité hors choix ERP ; les commandes B2C détaillées sont enregistrées dans l'ERP. | Les responsabilités d'exécution logistique sont séparées ; la cible B2C n'est pas absente. |

| Offre SAP/Delaware de septembre, **pages 21–28** | Le tableau précise que « inclus » signifie chiffré dans la macro-estimation. Il coche **SAP OMSA**, **S/4 Fashion SD Wholesale**, **S/4 Allocation Management**, **S/4 Back Office Management** magasin, **S/4 FICO** et **SAP IBP** ; il exclut SAP CAR Allocation Management, S/4 TM et Basic EWM. | La proposition SAP a **étendu ou précisé** le périmètre par rapport à la délimitation initiale. Un composant OMS est explicitement inclus, mais le détail de couverture et de charge de chaque fonction n'est pas isolé. |

| Réponse Microsoft/Avanade, **pages 13, 22, 38–40** | Solution proposée : Dynamics 365 Finance, Supply Chain et Commerce, complétée par **K3 Fashion**. La matrice Avanade indique **77 % de couverture standard**, 18 % par customisation et 4 % par développement sur le questionnaire RFI (arrondis). Elle chiffre **1 900–2 300 JH et 1,9 M€ pour un pilote**, dont 380–460 JH d'intégration de 40 interfaces identifiées et 190–230 JH de développement/customisation. | Le 77 % porte sur les **besoins du RFI**, qui dépassent et diffèrent de FLOW ; ce n'est ni un taux de couverture de FLOW, ni une fraction du coût Make. Le chiffrage Avanade est limité au pilote et explicitement non engageant. |

| COPIL 5 du 17 septembre, **pages 6–8** | Comparaison de SAP/Delaware et Microsoft/Avanade/K3 : **83 % et 77 % de couverture standard du RFI** ; budget projet Microsoft **2,64 M€ pour le pilote + 1,60 M€ pour quatre autres pôles = 4,24 M€**, hors abonnements présentés séparément. | Les 4,24 M€ sont une **projection de COPIL**, plus large que les 1,9 M€ du seul pilote Avanade. Les deux prix SAP et Microsoft reposent sur des hypothèses et périmètres différents ; l'offre Microsoft est jugée susceptible d'être sous-évaluée. |



### Comparaison de périmètre, après vérification



| Dimension | Étude Synvance 2025 — Buy | FLOW — Make |

| --- | --- | --- |

| Architecture | **Un ERP commun** Achat/Vente/Opérations, connecté à des applications spécialistes. L'architecture cible et le maintien des satellites restent ouverts au RFI. Le Wholesale est une fonction de l'ERP ; SAP inclut S/4 Fashion SD, tandis que Microsoft propose Dynamics 365 et K3 Fashion. Les pièces examinées ne démontrent pas un « module Wholesale » autonome séparé du backbone. | Un cœur opérationnel unique de commandes, stock, disponibilité et décisions de flux ; systèmes Retail, B2C et Wholesale autonomes par canal. |

| Commandes et OMS | L'étude d'un OMS spécialisé est écartée au départ. Pourtant le RFI impose déjà commandes B2C détaillées, promesse, réservation, priorités, allocation et carnet ; l'offre SAP de septembre **inclut SAP OMSA**. Sa couverture exacte et la charge associée ne sont pas ventilées. | FLOW reprend ces capacités dans un produit Make et doit en outre déterminer précisément quelles fonctions d'UR, Socloz et NewStore seront décommissionnées. Les pièces RFI examinées ne constituent pas un inventaire de sortie de ces trois outils. |

| Stock et disponibilité | ERP maître des stocks théoriques, vue des physiques, allocations et protections par canal ; consultations de disponibilité et dates promises demandées. Le niveau de garantie transactionnelle omnicanale de FLOW n'est pas spécifié de façon assez précise pour déclarer les deux cibles identiques. | Stock physique unifié, engagements/réservations cohérents entre canaux, availability, ATP/CTP/PTP, protection et décision globale. |

| Retail | Activités POS et encaissement exclus, mais stock magasin, commandes de réassort, retours et certaines opérations back office sont dans le RFI ; l'offre SAP inclut S/4 Back Office Management. | Le système de canal Retail reste autonome ; FLOW pilote les commandes, stocks et flux communs. |

| Fulfillment et logistique | WMS/TMS d'exécution exclus ; l'ERP devait néanmoins créer des ordres de préparation/expédition, suivre des jalons, traiter partiels et retours, et communiquer avec les prestataires. | FLOW pilote le plan et les commandes de fulfillment ; les partenaires exécutent la logistique. Il existe donc un **recouvrement significatif** à comparer par fonction. |

| Configurabilité | Règles multicritères, saison, priorité, simulation et ajout de critères déjà demandés, notamment pour le réassort et l'allocation. | Produit de configuration plus transversal et gouverné : applicabilité, héritage, versions, simulation, publication, audit et explication de chaque décision. La différence précise est à mesurer, pas à présumer totale. |

| Autres frontières | RFI : matières/capacités fournisseurs, prix/conditions, valorisation des stocks ; Finance et comptabilité exclues du choix ERP. **Offre SAP de septembre : FICO et IBP inclus. Offre Microsoft : licences Dynamics 365 Finance, Supply Chain, Commerce et K3 Fashion listées.** Les inclusions de licences ne démontrent pas à elles seules la profondeur de mise en œuvre de chaque domaine. | Finance, contrôle de gestion, commercial amont et planification stratégique exclus ; certains composants Sourcing/Commerce nécessaires à la sortie de Storeland restent à découvrir. |

| Nature de l'effort | Installer, configurer, adapter et déployer un logiciel existant, avec souscriptions. | Concevoir, développer, tester, déployer et maintenir le logiciel cœur sous maîtrise Beaumanoir. |



**Lecture :** la différence d'architecture et de mode de réalisation est nette. La différence **fonctionnelle** est plus nuancée que supposé : commandes, stock, allocation, Retail back office et une partie de l'orchestration étaient déjà présents dans la consultation, puis parfois dans une offre chiffrée. Les écarts à isoler sont la profondeur du produit FLOW, la gouvernance des règles, la propriété des décisions et le décommissionnement de satellites, en retranchant les fonctions SAP proposées hors FLOW.



## Pièces qui établissent le périmètre



Le [registre des sources](<20-registre-sources.md>) donne accès aux pièces suivantes : COPIL 1, slide 8 (S10) ; synthèse des besoins cibles, slides 3–4 (S14) ; présentation RFI, pages 3–8 et 13 (S11) ; besoins métier RFI, pages 24–27 et 31–40 (S12) ; questions-réponses, slides 6, 19 et 27 (S13). Le COPIL 5, pages 4, 7 et 8 (S05), présente les budgets et limites. La soutenance Delaware, pages 21–28 et 37–45 (S01), la réponse Avanade, pages 13, 22 et 38–42 (S03), et la note Microsoft/K3 (S15) documentent les offres. Les références de juillet et septembre correspondent à des étapes différentes du RFI de 2025.



## Chiffres effectivement observés



| Observation 2025 | Valeur | Lecture correcte |

| --- | ---: | --- |

| SAP/Delaware, intégrateur, total des trois lots | **14 640 JH** | Upgrade, core model Boardriders, puis Beaumanoir ; source Delaware septembre, page 38. |

| SAP/Delaware, équipe interne Beaumanoir | **13 393 JH imprimés au total ; 13 993 JH par somme des trois lignes** | Page 38 : 218 + 8 034 + 5 741 = 13 993 JH. Écart de **600 JH** à clarifier avec Delaware. |

| **SAP/Delaware, effort combiné** | **28 033 JH selon le total imprimé ; 28 633 JH par somme des lignes** | La charge intégrateur de 14 640 JH se recalcule ; la charge interne est contradictoire. Référence Buy indicative, postérieure à la mission Synvance. |

| SAP/Delaware, prestations d'intégration, somme des trois lignes | **13 462 352 € HT** | 395 000 + 7 768 577 + 5 298 775 €. La ligne « Total » affiche **15 462 352 €**, soit exactement **2 000 000 € de plus** que ses composantes. Les précédents 13,463 M€ étaient un arrondi ; la somme exacte est retenue pour le modèle, sous réserve de clarification du total imprimé. |

| SAP/Delaware, pilote Boardriders puis déploiement Beaumanoir | **18 + 12 = 30 mois** | Trajectoire indicative du COPIL 5, page 7, confirmée par le questionnaire SAP de juillet ; les tableaux détaillés de septembre donnent toutefois 21 et 17 mois. Voir la distinction ci-dessous. Elle ne donne pas un délai Make. |

| Avanade/Microsoft, pilote, intégrateur | **1 900 à 2 300 JH** | Périmètre pilote uniquement ; analyse du standard, 40 interfaces identifiées, provision limitée de développement, tests et gouvernance. Pas comparable au total SAP ni au total FLOW. |

| Avanade/Microsoft/K3, pilote, prestation indiquée par Avanade | **1,90 M€** | Réponse Avanade, page 39 ; ROM non engageant, correspondant au seul pilote et à la **somme des bornes basses** des cinq phases. |

| Microsoft/Avanade/K3, pilote dans le COPIL 5 | **2,64 M€** | Hypothèse réévaluée de Beaumanoir, page 7, égale à la **somme des bornes hautes** des cinq phases Avanade ; ne pas l'additionner aux 1,90 M€ de la borne basse. |

| Microsoft/Avanade/K3, quatre autres pôles dans le COPIL 5 | **1,60 M€** | Extrapolation de déploiement ; les JH équivalents ne sont pas détaillés dans la réponse Avanade. |

| **Microsoft/Avanade/K3, projet total projeté dans le COPIL 5** | **4,24 M€** | 2,64 + 1,60 M€ de coûts projet, hors abonnements et valorisation de l'équipe interne. **Projection COPIL**, pas devis Avanade full scope. |

| Microsoft/Avanade/K3, calendrier du COPIL 5 | **18 + 20 = 38 mois** | Page 7 : pilote de 18 mois puis quatre autres pôles sur 20 mois ; durée de 6 à 9 mois par pôle. Les dates des quatre vagues ne sont pas précisées. |

| D365/K3, couverture standard du RFI | **77 %** | Même questionnaire que le **83 % SAP** ; indicateur de couverture des besoins RFI, **pas de FLOW**. |

| Avanade/Microsoft, pilote, estimation d'équipe interne dans le COPIL | **8 ETP pendant 18 mois** | Environ 2 400 JH *si* l'on applique rétrospectivement la convention FLOW de 200 JH/ETP-an ; le support ne donne pas des JH internes mesurés. |



La proposition SAP de **juillet 2025** donnait **16 536 JH intégrateur** et **15 723 JH internes** (32 259 JH combinés), avant révision de septembre. Cette baisse prouve que les chiffres RFI évoluent déjà avec les hypothèses ; elle ne mesure pas la sous-estimation finale. Le COPIL de juillet signalait explicitement une possible sous-estimation de charge/durée pour SEI et des incertitudes générales de comparaison. Le retour oral rapporté par le porteur de FLOW — les RFI sous-estiment généralement la réalisation et le scope n'était pas complet — est retenu comme **alerte qualitative**, sans coefficient automatique de majoration.



Les coûts projet ci-dessus visent les **prestations et déploiements Buy** ; ils excluent la valorisation des équipes internes, les souscriptions, l'exploitation et les ajouts de périmètre. Pour SAP/Delaware, les **13 393 JH internes imprimés, ou 13 993 JH par somme des lignes** ne sont pas valorisés. Pour Microsoft, le COPIL 5 projette 8 ETP internes sur le pilote, puis 4 sur les autres pôles, sans coût interne. Le même COPIL présente séparément un abonnement Microsoft de **1,4 M€/an hors remise** et **0,98 M€/an après remise de 30 %** ; ces montants ne s'ajoutent pas au coût de construction FLOW Make. Les chiffres RFI ne sont pas des prix effectivement dépensés.



La version de juillet du COPIL 4 présentait pour Microsoft un **coût projet pilote de 1,90 M€** et **1,44 M€ pour les autres pôles**, soit **3,34 M€ hors abonnements** ; son « full scope » de **6,523 M€** y ajoutait des abonnements proratisés et remisés. Le COPIL 5 de septembre porte le projet hors abonnements à **4,24 M€**. Le changement d'hypothèses et de stade interdit de prendre ces montants comme trois devis alternatifs équivalents.



### Prix des prestations : distinguer dispositif et développement



Le prix moyen recalculé SAP/Delaware est **919,56 €/JH** : 13 462 352 € divisés par 14 640 JH externes. Pour Microsoft, le pilote haut retenu au COPIL correspond à **1 147,83 €/JH** : 2 640 000 € divisés par 2 300 JH, sommes des bornes hautes de la réponse Avanade, page 39. Les lignes « intégration » et « développement/customisation » de cette même page sont à **1 000 €/JH**, mais ce tarif ne représente pas le dispositif complet comprenant configuration, architecture, gouvernance, tests et go-live. Ces prix constatés d'intégration de progiciel ne sont pas le prix d'un développeur FLOW. Les JH du déploiement Microsoft des quatre pôles ne sont pas détaillés : lui appliquer le prix moyen du pilote est une convention du modèle, pas un tarif source pour ces pôles.



### Abonnements et services de fonctionnement : données sources



L'offre Delaware de septembre, **page 45 du PDF** (page imprimée 53), présente les « budgets annuels licences tenant compte de la roadmap hors CPI », **Finance comprise**. Les années sont celles de la montée en charge du projet ; les licences ne commencent donc pas seulement à la fin du déploiement.



| Année de la roadmap SAP | 1 | 2 | 3 | 4 | 5 |

| --- | ---: | ---: | ---: | ---: | ---: |

| Budget licences HT, avant inflation ajoutée par la simulation | 790 633 € | 765 823 € | 973 480 € | 1 270 879 € | 1 270 879 € |



La page 37 du même PDF présente séparément, après stabilisation, **250 000 €/an de MCO**, **450 000 €/an de monitoring des flux en horaires étendus** et **350 000 €/an de TMA évolutive**, en plus de RISE arrondi à 1,27 M€/an. Le questionnaire SAP du 23 juillet, onglet « 8. Estimations budgétaires », lignes 13 à 15, confirme la distinction entre monitoring, MCO hors évolutions et enveloppe d'évolutions. Supprimer le monitoring ou le fondre dans les 250 k€ sous-estimerait la proposition. Si la simulation remplace les 350 k€ par une enveloppe d'évolution en JH, elle doit le faire explicitement sans addition des deux bases.



Pour Microsoft, la réponse **#1 page 38** et la version **#2 page 22** affichent **979 001,51 €/an pour chacune des cinq premières années**, pour un panier de **950 utilisateurs** incluant Dynamics 365 et **K3 Fashion**. Aucun découpage tarifaire Dynamics/K3 n'a été trouvé dans les deux PDF ni le questionnaire. Le contrat Dynamics est annoncé pour cinq ans avec protection des prix pendant le contrat ; K3 indique une durée maximale d'engagement de cinq ans. Le tableau justifie un panier constant sur cinq ans, mais ne démontre pas une clause de gel propre à K3. La version #2 mentionne une signature et activation au **12 décembre 2025**, avec conditions commerciales ; cette date d'offre n'est pas un début de projet FLOW ni un calendrier réel d'exécution.



Le questionnaire Microsoft, onglet « 8. Estimations budgétaires », **C13/D13**, chiffre **90 000 € en année 1** pour « Unified + Project Quality advisory », dont 200 heures d'ingénierie Microsoft, sur les phases Build/Run. C'est un service distinct de la souscription et d'une TMA/MCO applicative. Les cellules MCO et autres coûts à zéro ne prouvent pas un service gratuit : ces prestations ne sont pas chiffrées dans la réponse. Le modèle peut retenir les 90 k€ comme provision ponctuelle de première année, en indiquant que la récurrence n'est pas établie par la source. Les indexations ajoutées au-delà des périodes documentées sont des hypothèses de simulation, pas des clauses RFI vérifiées.



### Calendriers sources et échéancier de simulation



Le **COPIL 5, page 7**, retient **30 mois SAP** (18 mois pilote + 12 mois de déploiement des quatre autres pôles) et **38 mois Microsoft** (18 + 20). Le questionnaire SAP du 23 juillet, onglet « 8. Estimations budgétaires », **C20/C21**, donne bien 18 et 30 mois. Cependant, la proposition Delaware de septembre, **pages 39 et 40 du PDF**, additionne **21 mois pour le lot 2** et **17 mois pour le lot 3** dans ses tableaux par phase. Les chevauchements et le rapprochement avec les 30 mois du COPIL ne sont pas décrits. Ni ces tableaux ni les slides de cinématique 14–16 ne donnent une durée ou une date pour le lot 1 d'upgrade.



Un graphique peut donc utiliser la trajectoire simplifiée du COPIL, en la nommant, mais les mois exacts de chaque vague, les chevauchements, le calendrier de l'upgrade et la répartition des budgets par vague restent **des hypothèses éditables**. Pour Microsoft, les 1,60 M€ ne sont pas ventilés par pôle dans la source ; 400 k€ par pôle serait une répartition conventionnelle. Il ne faut pas transformer une date choisie pour la projection sur quinze ans en engagement de l'intégrateur.



**Traçabilité des compléments :** offre Delaware de septembre déjà référencée ci-dessus, pages PDF 37–40 et 43–45 ; `2-Etude/1. Benchmark ERP/2. Réponses RFI/SAP/20250723 - Réponse budget planning références/RFI GBM - Questionnaire - Sap-delaware-V2-Complete - livraison-2025-07-23.xlsx`, onglet 8 ; `2-Etude/1. Benchmark ERP/2. Réponses RFI/MICROSOFT/RFI GBM - Réponse MICROSOFT FULL - NE PAS MODIFIER.xlsx`, onglet 8 ; réponses PDF Microsoft #1, pages 38–40, et #2, page 22 ; COPIL 5 du 17 septembre, page 7. La pagination PDF est utilisée pour éviter la confusion avec la numérotation imprimée Delaware.



Le détail Delaware de septembre attribue **2 810 JH d'intégrateur** aux lignes « Manage Financial Process » et « Manage Financial Planning and Analysis » des lots Boardriders et Beaumanoir (1 323 + 713 + 341 + 433 JH). C'est un exemple chiffré de **non-recouvrement avec FLOW**, dont la finance et le contrôle de gestion sont exclus ; il ne faut cependant pas soustraire mécaniquement ces 2 810 JH, car certaines interfaces ou données financières restent nécessaires et la charge interne correspondante n'est pas isolée. Le même détail compte 548 JH de « Retail Store Operations » sur le lot Beaumanoir : selon le partage des responsabilités, une partie de ce back office peut recouper les commandes et stocks communs de FLOW, une autre les fonctions de canal qui restent autonomes. L'offre inclut aussi SAP OMSA ; la charge dédiée à ce composant n'est pas isolée. **Le programme Buy n'est donc pas une simple implantation sans fonctions de cœur omnicanal.**



## Réserves documentées et compléments OMS à estimer



### Qui exprime la réserve de sous-évaluation ?



Le **COPIL 5 du 17 septembre 2025, page PDF 8**, porte dans la colonne Microsoft la réserve « Coûts projet faibles (Semble sous évaluée au vu des expériences !) ». La colonne SAP qualifie ses coûts projet d'élevés. La même page demande de préciser les complexités, les spécifiques, l'organisation et le budget. **Cette réserve figure dans le dossier, mais la mission Synvance était terminée depuis le 4 juillet : elle relève du COPIL Beaumanoir.** Elle ne constitue pas une preuve d'un facteur de sous-estimation commun à SAP et Microsoft.



Le **COPIL 4 Synvance du 2 juillet, slide 11**, signalait déjà les approximations de l'exercice et les estimations disparates des déploiements et des coûts récurrents. Les hypothèses des éditeurs avaient été conservées avec un minimum de retraitement ; certains coûts, dont les montées de version, restaient hors calcul. Le retour oral rapporté par Laurent Sintès sur la sous-évaluation des RFI est conservé comme un signal complémentaire, distinct de ces pièces écrites.



### Le courriel Microsoft révèle des limites concrètes



Le courriel transmis par Microsoft le **16 septembre 2025**, dans le fil `RE_ Etude ERP Groupe Beaumanoir RFI.msg`, précise les conditions de la proposition Avanade. Il complète les slides génériques qui pourraient autrement laisser croire à une couverture intégrale :



| Sujet | Fait établi par le courriel | Conséquence pour le chiffrage |

| --- | --- | --- |

| TNR automatisés | La prestation d'automatisation n'est pas incluse par défaut. RSAT est disponible, mais le choix des outils et la gouvernance restent à définir. | Un outil licencié ne finance pas la construction, les données et la maintenance des tests. Ajouter une prestation d'automatisation, sous hypothèses explicites de volume. |

| Change | La conduite du changement n'est pas incluse à ce stade, hormis la formation des utilisateurs clés et des formateurs. | Ajouter l'accompagnement fournisseur nécessaire, sans facturer deux fois les formations déjà incluses ni valoriser les contributions métier internes exclues de notre convention. |

| Réalisation | Une contribution nearshore/offshore influence les tarifs journaliers, en complément des équipes onshore. | Le prix du pilote ne constitue pas un prix de dispositif entièrement réalisé en France. La transposition France est une hypothèse de tarif et de répartition des rôles ; aucune part offshore exacte n'est fournie. |

| Déploiements | Effort dépendant des écarts au core model, RICEW locaux, entités, langues, localisations et RACI. | Les 1,60 M€ pour quatre pôles restent une projection conditionnelle. Les nouvelles fonctions communes sont chiffrées séparément des adaptations locales pour éviter les doubles comptes. |

| OMS et Finance | Une réponse générale affirme l'inclusion des fonctionnalités disponibles ; elle précise surtout que l'architecture Finance doit être définie. | Ce passage ne décrit ni le cycle OMS cible complet ni une charge d'implémentation OMS isolée. |



Une [extraction consultable](<../../sources/client/microsoft-mail-2025-09-16.txt>) permet de retrouver les passages TNR lignes 434–440, localisation de réalisation ligne 491, déploiements lignes 509–512 et change lignes 518–529. Les numéros de ligne correspondent à cette extraction, qui contient aussi les en-têtes techniques du message.



### Ce qui manque n'est pas un OMS entier absent des deux offres



**SAP :** Delaware inclut SAP OMSA page PDF 26, S/4 Fashion SD et Allocation Management page 27, et le Back Office magasin page 28. La BOM pages 43–45 identifie la souscription **8012655, SAP Order Management for sourcing and availability**, à **1 020 € la première année puis 21 420 €/an des années 2 à 5**. Ces montants sont déjà dans les licences SAP ; ils ne doivent pas être ajoutés une seconde fois. La proposition ne donne pas de montant de prestation OMS isolé. La présence d'OMSA, dont l'intitulé porte sur sourcing et disponibilité, **ne démontre pas à elle seule** la couverture du cycle de vie, des cases, des aléas et de l'orchestration de fulfillment attendus de FLOW. Il faut examiner l'ensemble OMSA + S/4 + allocations, puis compléter les écarts.



**Microsoft :** la carte applicative page 22 contient ATP, gestion des commandes, allocation priorisée, service providers, livraison et workflow. La page 38 inclut Dynamics 365 Finance, Supply Chain, Commerce et K3 dans les licences. La grille de la page 13 attribue **74 % de standard / 26 % de customisation aux ventes**, **68 % / 31 % / 2 % de développement aux allocations**, **69 % / 8 % / 23 % aux expéditions**, et **67 % / 11 % / 22 % aux livraisons et retours** ; les écarts d'arrondi sont ceux de la source. Elle précise que des demandes très spécifiques de pilotage des flux et d'allocation nécessitent des customisations, voire des contournements ou une inscription dans la roadmap de l'éditeur. Cela confirme un recouvrement fonctionnel réel, et une profondeur d'implémentation encore fragile. **Ces taux portent sur le questionnaire RFI ; ils ne se convertissent pas en pourcentages de couverture ni de coût de FLOW.**



Les compléments du [rapprochement](<15-rapprochement-buy-france.md>) portent donc sur l'effort résiduel de quatre ensembles : transactions/stock/promesse ; cases et orchestration ; carnet et optimisation ; configuration gouvernée. Ils ne consistent pas à ajouter une plateforme OMS complète aux propositions existantes. Ils n'incluent pas une couverture fiscale mondiale, un POS ou l'exécution WMS/TMS, exclus de FLOW.



### Ne pas présenter des coûts déjà inclus comme des omissions



Delaware prévoit **401 + 304 = 705 JH** dans les lignes dédiées de migration des lots 2 et 3. Les **204 JH de conversions WRICEF** sont un autre éclairage de réalisation, avec un recouvrement possible ; ils ne s'additionnent pas automatiquement. Les phases SIT/UAT sont présentes dans tous les domaines : les **12 + 0 JH de la seule ligne “Tests”** ne sont donc pas le total des tests du programme. Gouvernance, coordination et support infrastructure sont également chiffrés. Les formations dédiées sont à zéro dans ces matrices ; cela ne prouve pas l'absence de tout transfert de connaissances.



Chez Avanade, **380–460 JH pour 40 interfaces**, **490–600 JH de tests/go-live/support** et **320–380 JH de gouvernance/architecture** sont déjà dans le pilote. La migration est décrite page 47 sans charge isolée. Les suppléments doivent porter sur les nouvelles extensions, les tests transverses correspondants, l'automatisation explicitement exclue et les responsabilités techniques nécessaires à un dispositif autonome, après retrait des recouvrements.



### Contributions internes et autonomie du dispositif



Les **13 993 JH internes SAP par somme des lignes** restent une source contradictoire avec le total imprimé de 13 393 JH. Pour Microsoft, les **8 ETP sur 18 mois puis 4 ETP sur 20 mois** du COPIL représentent **3 733,33 JH**, en appliquant la convention hypothétique de **200 JH par ETP-an** : 2 400 JH + 1 333,33 JH. Ce sont des conversions d'hypothèses de mobilisation, non des charges consommées ni des JH externes proposés.



Le rapprochement France peut externaliser une **fraction technique explicitement hypothétique** de ces contributions : architecture, intégration, qualité, coordination et préparation de la bascule. Il conserve hors prix fournisseur les contributions métier internes Beaumanoir. Il ne transforme pas l'ensemble de la charge interne en facture d'intégrateur et ne doit pas financer une seconde fois les activités des compléments OMS, des interfaces ou du change. L'autonomie de réalisation recherchée ne supprime ni les décisions métier du client ni la dépendance aux éditeurs dans les options Buy.



## Pont d'estimation vers FLOW Make



Le bon usage de Synvance est de **calibrer et challenger des postes de chiffrage**, en conservant les unités :



`Effort FLOW Make = effort commun de transformation + effort de construction du produit + effort des capacités FLOW absentes du RFI - effort des travaux Buy ou hors périmètre FLOW`



1. **Effort commun à tester :** conception du modèle opérationnel, interfaces, migration, tests de bout en bout, pilotage, mobilisation métier et déploiement. Les **380–460 JH d'intégration de 40 interfaces identifiées** chez Avanade forment un second signal, limité au pilote D365/K3. SAP/Delaware prévoit presque autant de jours internes que de jours intégrateur ; le COPIL Microsoft prévoit aussi une équipe interne significative. Il faut comparer les frontières de chaque poste avant de transposer une charge.

2. **À ajouter pour Make :** construction et pérennisation du cœur commandes/stock/disponibilité, moteur de promesse, allocation et optimisation, plateforme de configuration gouvernée, outils métiers, sécurité et exploitation du produit. Le RFI **demandait déjà plusieurs de ces fonctions** et SAP proposait des composants OMS/allocation ; ce qui change ici est surtout leur développement et leur maîtrise par Beaumanoir, plus les exigences FLOW supplémentaires à identifier précisément.

3. **À retirer ou réduire :** paramétrage, conversions et déploiement propres à SAP/D365 ; FICO et IBP proposés par SAP, prix/conditions commerciaux, valorisation ou planification stratégique lorsque ces travaux sortent de FLOW. Les fonctions OMS, stock, allocation et Retail back office de SAP doivent être **rapprochées** de FLOW avant tout écart de charge.

4. **À revoir séparément :** composants Sourcing/Commerce non découverts de Storeland, affichés comme option de 15 % de la base identifiée, hors nominal ; Retail/B2C, flux logistiques, entités internationales et dépendance aux systèmes existants.



**Conséquence immédiate :** les **deux trajectoires Buy** sont des repères de mise en œuvre chez Beaumanoir. SAP/Delaware chiffre un programme plus large avec **14 640 JH externes** et des fonctions FICO/IBP ; Microsoft/Avanade/K3 présente **1 900–2 300 JH pour un pilote**, puis un **budget projet global de 4,24 M€ projeté par le COPIL**, sans ventilation full scope en JH. Ces écarts ne démontrent ni un gain d'effort structurel, ni une borne Make : fonctions, couverture, équipes internes et maturité du chiffrage diffèrent. Les deux offres aident surtout à contrôler configuration, interfaces, tests, mobilisation métier et déploiement, après rapprochement des périmètres.



## Contrôles utiles sans lancer un nouveau cadrage complet



- Reprendre le **détail des 14 640 JH Delaware** par domaine, interfaces, migration, tests et gouvernance ; rapprocher ces postes de ceux du modèle FLOW.

- Vérifier les hypothèses de **40 interfaces** du pilote Avanade : objets, sens, nombre de systèmes réellement distincts et charge de build indiquée. Ce nombre n'est pas le nombre prouvé de connecteurs FLOW.

- Faire préciser l'écart de **2 M€** entre le total affiché et la somme des postes SAP/Delaware avant toute utilisation financière.

- Identifier, dans la matrice Synvance, les exigences « spécifique / tiers / non couvertes » proches du stock, de l'allocation, des saisons et des règles. Elles constituent un indice de complexité métier ; les pourcentages de couverture éditeur ne se convertissent pas en JH de développement.

- Conserver comme fait rapporté par le porteur de FLOW que l'étude Buy a été arrêtée au RFI pour coût jugé trop élevé. Les pièces consultées montrent le stade RFI et les recommandations de poursuite ; elles ne prouvent pas à elles seules la décision d'arrêt ni sa cause.

