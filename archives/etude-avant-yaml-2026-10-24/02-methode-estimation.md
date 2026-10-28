> **Historique — retiré de la base active le 24 octobre 2026.** Les hypothèses et résultats de cette note sont remplacés par le [modèle YAML actuel](../../source/README.md).

![Logo eXalt](<../../assets/exalt-logo.png>)



**Laurent Sintès** · 21 octobre 2026



---



# Méthode d'estimation FLOW



## Objet et conventions



L'étude présente **un budget de référence par option, sous hypothèses**. FLOW est construit en Make ; SAP et Microsoft servent de références de coût. L'unité de charge est le **jour de travail d'une personne (JH)**. Les ETP expriment une capacité sur une durée : la convention de 200 JH par personne et par an sert uniquement aux conversions de moyens.



Le chiffre d'affaires et les 120 millions de pièces vendues par an situent l'entreprise. Ils ne multiplient pas le coût logiciel. Les pics de transactions, la concurrence entre réservations et la taille des problèmes d'allocation déterminent les travaux de performance et de fiabilité.



## 1. Partir du périmètre à réaliser



La [cartographie SCM](<../../sources/client/cartographie-2026-10-17.1.yaml>), le [cahier des charges FLOW](<01-cahier-des-charges.md>), les exigences de [gestion de la configuration](<../../sources/Gestion de la configuration.pdf>) et les interfaces annoncées permettent une estimation globale. Le détail des marques, règles et vagues n'est pas un préalable à cet ordre de grandeur.



Les fonctions sont regroupées en quatorze **postes de chiffrage**, distincts des lots de déploiement. Chaque charge couvre les métiers nécessaires à sa réalisation par un prestataire autonome : conception, ingénierie, architecture, analyse métier, qualité et pilotage. Les contributions internes Beaumanoir restent hors budget fournisseur.



La facilité de changement est une fonction à construire : héritage des règles, dérogations, versions, simulation, approbation, activation, retour arrière et explication des décisions. Construire ces mécanismes et configurer les règles initiales sont deux travaux distincts.



## 2. Calculer une charge de référence



Le [détail des postes](<06-premier-ordre-de-grandeur-effort.md>) retient **32 100 JH**, avec reprise des données opérationnelles actives et mise en service unique au mois 60. Les quantités sont des hypothèses d'ingénierie ; elles ne viennent pas d'une mesure de productivité FLOW.



Les développements métier propres à Beaumanoir appartiennent au **Core FLOW**. Les [clés de répartition](<09-abaques-repartition.md>) distinguent le Core, les interfaces et la sécurité, la configuration métier, ainsi que les postes distincts de reprise et de mise en service. Elles répartissent le budget sans l'augmenter.



Les composants Storeland non identifiés restent une **option de 15 %**, hors budget affiché. Le lotissement additionnel, les risques et la co-construction éventuelle restent des paramètres séparés du classeur.



## 3. Valoriser le travail et le fonctionnement



Les prestations initiales FLOW valent **32 100 JH × 750 €/JH = 24,075 M€ HT**. Les **386 k€ de ressources techniques de construction**, distincts des JH, portent la réalisation initiale totale à **24,461 M€ HT**. Le tarif correspond à une hypothèse d'équipe autonome en France, comprenant les métiers de réalisation et les frais du prestataire. Sa composition est détaillée dans le [calcul du budget initial](<11-cout-nominal-minimum.md>).



### Trois entrées pour les prestations récurrentes



1. **Capacité de maintien en service** : maintenance, exploitation, versions techniques courantes et pilotage.

2. **Capacité annuelle réservée aux évolutions fonctionnelles.**

3. **Prix journalier moyen vendu par le fournisseur**, comprenant ses compétences, frais et marge.



Une personne-année représente 200 JH disponibles pour le contrat, convention conservée de l'étude. Les effectifs sont des capacités, pas nécessairement des personnes dédiées. Les remplacements s'organisent dans le collectif fournisseur, sans deuxième majoration de congés.



## 4. Un service commun



| Dimension | Hypothèse commune |

| --- | --- |

| Périmètre | Même cible opérationnelle : commandes, achats, retours, stock, promesse et allocation, orchestration, documents, interfaces et règles des marques. |

| Couverture humaine | Huit heures par jour, cinq jours par semaine, heures françaises. Convention de 250 jours d'ouverture par an. Un interlocuteur fonctionnel et un interlocuteur technique mobilisables sur cette plage. |

| Traitement | Qualification, diagnostic, contournement ou correction, reprise des flux et vérification du retour au service. Priorisation des demandes, sans nombre illimité d'incidents simultanés ni délai garanti de résolution. |

| Prévention et qualité | Santé applicative, cohérence des données, entretien des interfaces et composants, tests, préparation des pics et exercices de reprise. Quatre fenêtres annuelles de maintenance planifiée ; correctifs urgents au fil de l'eau dans la même capacité. |

| Pilotage | Responsable fournisseur, cohérence technique, suivi du service et des changements, coordination des partenaires et éditeurs. |

| Évolutions | Capacité annuelle protégée, avec priorités arbitrées dans cette enveloppe. |



Ce **nominal en heures ouvrées** ne couvre pas les nuits et week-ends du commerce international. Astreinte et horaires étendus restent des options communes. Le forfait SAP historique inclut des horaires étendus dont l'amplitude n'est pas précisée.



Le L1 métier, les décisions de priorité et la validation métier restent chez Beaumanoir, hors coût fournisseur. L'analyse fonctionnelle et le pilotage nécessaires au prestataire sont financés. Les systèmes sont supposés stabilisés, instrumentés, documentés et dotés de tests automatisés à la sortie du projet ; ces conditions appartiennent à la réalisation initiale.



## 5. Un dispositif fournisseur plausible



Les trois blocs ci-dessous expliquent le choix d'équipe. Ils ne sont pas des paramètres supplémentaires ni des effectifs observés chez un comparable Fashion.



| Responsabilités | FLOW | Microsoft | SAP |

| --- | ---: | ---: | ---: |

| Service fonctionnel et exploitation technique | 3 personnes-an | 3 personnes-an | 3 personnes-an |

| Entretien logiciel et qualification | 3 personnes-an | 2 personnes-an | 2 personnes-an |

| Architecture et pilotage fournisseur | 1 personne-an | 1 personne-an | 1 personne-an |

| **Maintien en service proposé** | **7 personnes-an / 1 400 JH** | **6 personnes-an / 1 200 JH** | **6 personnes-an / 1 200 JH** |

| **Évolutions distinctes** | **2 personnes-an / 400 JH** | **2 personnes-an / 400 JH** | **2 personnes-an / 400 JH** |



### Service et exploitation



Les deux interlocuteurs nécessitent **2 × 250 = 500 jours de couverture**. Trois personnes-années apportent 600 JH : les 100 JH restants permettent des travaux planifiés de configuration existante, de prévention et de préparation métier en dehors de la permanence.



La surveillance, les diagnostics et les reprises ordinaires se font pendant ces jours de service. Ils ne s'ajoutent pas sous forme d'un coût par ticket. Le collectif fournisseur organise la rotation et le partage des connaissances ; une seule personne n'est pas supposée connaître tous les processus du groupe.



Ce choix finance une disponibilité. Sa suffisance dépend de la stabilité et de l'automatisation : une saturation durable des permanences ou le report systématique de la prévention signaleraient un besoin supérieur. Aucun nombre fictif d'incidents n'est nécessaire au calcul.



### Entretien du logiciel et tests



**FLOW :** deux capacités d'ingénierie couvrent les transactions/commandes/stock d'une part, la configuration/décision et les composants techniques d'autre part. Une capacité de qualification entretient les tests transverses et prépare les versions. Tout le produit reste à entretenir, même si ses composants sont open source.



**Microsoft :** Microsoft et K3 maintiennent leurs produits standard selon leurs contrats. Une capacité d'ingénierie entretient les configurations, interfaces et développements Beaumanoir, compléments d'orchestration compris. Une capacité de qualification assure la régression et les livraisons de la solution intégrée.



**SAP :** les spécialités concernent S/4 Fashion, allocations, OMSA et intégration. Le dispositif réserve également une capacité d'ingénierie pour les adaptations/extensions et une de qualification. Cette égalité avec Microsoft vient du service retenu ; elle n'est pas tirée des forfaits SAP. Les éléments disponibles ne justifient pas une différence chiffrée d'équipe entre les deux Buy.



La qualification correspond à environ 50 JH par fenêtre trimestrielle, préparation, entretien des tests et livraison compris. C'est une allocation de capacité, sans promesse de couvrir un nombre prédéfini de scénarios. Les compétences rares peuvent intervenir ponctuellement dans cette capacité, sans être des postes supplémentaires.



### Architecture et pilotage



L'autonomie du fournisseur demande une responsabilité technique et un suivi du service : un mi-temps d'architecture et un mi-temps de pilotage représentent une personne-année. Ce rôle coordonne aussi les évolutions ; aucun second pourcentage de pilotage ne s'ajoute.



FLOW porte les choix de son produit. Les Buy portent aussi les dépendances aux éditeurs et à leurs versions. Ces responsabilités existent dans les trois options.



## 6. Une enveloppe d'évolution explicite



Les **400 JH annuels** correspondent à un flux de petites et moyennes évolutions : environ une capacité de réalisation et une capacité partagée entre conception fonctionnelle, architecture ponctuelle et tests. Plusieurs personnes peuvent se répartir ce travail.



C'est un **choix d'investissement comparable en capacité**, sans garantie de livrer le même nombre de fonctionnalités. 



Les nouvelles fonctions du Core FLOW consomment cette enveloppe. Les corrections et versions techniques courantes sont dans le maintien en service. Pour les Buy, les nouvelles adaptations et extensions consomment les évolutions ; les nouvelles versions standard relèvent des souscriptions.



La configurabilité de FLOW peut accélérer certains changements. **Ce bénéfice reste une hypothèse de valeur**, distincte de son prix journalier inférieur. Aucun coefficient de productivité global ni gain garanti n'est retenu. Migrations majeures, nouveaux pays, acquisitions et refontes restent hors de cette enveloppe courante.



## 7. L'ordre de grandeur correspondant



Les prix moyens retenus sont : **750 €/JH FLOW et 850 €/JH pour les services spécialisés Buy**. Ils représentent des hypothèses de prix fournisseur France pour toutes les compétences du dispositif, pas des prix de contrats confirmés. Aucune marge supplémentaire ni réserve de risque ne s'y ajoute.



| Prestations annuelles en régime stabilisé | FLOW proposé | Microsoft proposé | SAP comme test de cohérence |

| --- | ---: | ---: | ---: |

| Maintien en service | 1 400 × 750 € = 1,05 M€ | 1 200 × 850 € = 1,02 M€ | 1 200 × 850 € = 1,02 M€ |

| Évolutions | 400 × 750 € = 0,30 M€ | 400 × 850 € = 0,34 M€ | 400 × 850 € = 0,34 M€ |

| **Lecture décideur** | **Environ 1,4 M€/an** | **Environ 1,4 M€/an** | **Environ 1,4 M€/an théorique** |



**Ces montants couvrent les personnes.** Licences, support éditeur payant et ressources d'exécution restent dans leurs lignes propres, après vérification des inclusions. Il ne s'agit ni d'un coût complet de fonctionnement ni d'un nouveau TCO. La proximité des budgets résulte d'une équipe FLOW plus importante à un prix moyen inférieur ; elle ne démontre pas un avantage économique global.



### Conserver la référence commerciale SAP



Delaware chiffre **250 k€ de MCO + 450 k€ de monitoring en horaires étendus + 350 k€ d'évolutions**, soit **1,05 M€/an**, après stabilisation. Ces montants restent la **base commerciale sourcée**, à leur périmètre RFI.



Le dispositif SAP proposé est un contrôle indépendant : **il ne remplace pas les forfaits et ne s'y ajoute pas**. L'écart de 0,31 M€ avec la valorisation théorique ne démontre pas un coût manquant. Mutualisation, volumes, prix, responsabilités client et périmètres peuvent expliquer un écart ; les pièces ne permettent pas de l'attribuer.



La comparaison à service commun demande de rapprocher le forfait des responsabilités décrites ci-dessus. Sans ce rapprochement, 1,05 M€ reste une référence RFI et non un prix confirmé de l'ensemble du service FLOW. Aucune réduction proportionnelle aux horaires ni aucun supplément en pourcentage du Make n'est appliqué.



## 8. Justification des hypothèses



| Source ou choix | Portée |

| --- | --- |

| Cahier des charges FLOW | Justifie les compétences à couvrir et la responsabilité de tout le produit. Les marques et le CA ne multiplient pas les effectifs. |

| [Microsoft, équipe de support](https://learn.microsoft.com/en-us/dynamics365/guidance/implementation-guide/transition-to-support-team) | Décrit les rôles fonctionnels, techniques, développement, architecture, versions et pilotage. Ne chiffre pas une équipe Beaumanoir. |

| [Microsoft, fonctionnement de la solution](https://learn.microsoft.com/en-us/dynamics365/guidance/implementation-guide/service-solution) | Distingue la plateforme maintenue par l'éditeur et la santé de la solution, des environnements et extensions. |

| [Microsoft, mises à jour](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/get-started/public-preview-releases) | Quatre publications annuelles, au moins deux adoptions. Retenir quatre fenêtres communes est un choix d'exploitation, pas une obligation identique pour toutes les solutions. |

| [SAP, responsabilités Private Edition](https://learning.sap.com/courses/sap-s-4hana-cloud-interaction-with-sap-for-administrations/describing-roles-and-responsibilities-for-sap-s-4hana-cloud-private-edition) | Des responsabilités applicatives et métier subsistent ; le contrat distingue services inclus et additionnels. |

| Delaware septembre 2025, PDF p. 37 ; questionnaire SAP onglet 8, lignes 13–15 | Trois forfaits et leurs montants sourcés. Effectifs, volume d'évolutions et couverture de tous les compléments FLOW non établis. |

| Avanade réponse n°1, PDF p. 38–39 | Maintenance et hébergement standard annoncés dans la souscription ; 40 interfaces du pilote. Ce n'est pas l'inventaire cible du Run. |

| [Malt Java](https://www.malt.fr/t/barometre-tarifs/tech/developpeur-backend/developpeur-java) et [Silkhom ERP](https://www.silkhom.com/cout-projet-erp/) | Au 20 octobre 2026 : 579 €/jour Java expérimenté actif sur Malt ; exemple Silkhom d'intégrateur ETI à 850–1 150 €/jour. Ce sont des repères d'achats différents. Les 750/850 € restent des hypothèses de contrat fournisseur. |

| Capacités 7/6/6 et évolution de 2 personnes-an | Choix d'organisation explicités, non certifiés par un benchmark ou un historique d'activité. |



Les pièces locales sont identifiées dans l'[analyse Synvance](<07-analyse-synvance.md>). SAP Private Edition et Dynamics/K3 conservent leurs responsabilités contractuelles propres.



**Un contrôle simple de sensibilité suffit :** une personne-année supplémentaire représente 200 JH, soit 150 k€/an FLOW ou 170 k€/an au tarif Buy retenu. Cet effet d'un choix d'équipe est plus utile qu'une précision au millier d'euros sur quinze ans. Aucune borne min/max ni probabilité n'en est déduite.



## 9. Des frontières de coût stables



Le coût initial conserve ses postes : Core, configuration métier, flux, spécifiques Buy, reprises et mise en service. Les ressources techniques forment un budget distinct : cloud, stockage, sauvegarde, observabilité et environnements. Pour le Buy, seuls les éléments non compris dans les abonnements sont ajoutés.



Une action reçoit un seul financement : contrôles, incidents, reprises et correctifs dans le maintien en service ; nouvelles capacités dans les évolutions ; factures cloud et éditeur dans les ressources et souscriptions. Architecture, tests et pilotage de l'équipe ne sont pas refacturés en supplément.



Les sources, hypothèses et exclusions restent traçables. La réussite d'un contrôle de formule ne prouve pas la suffisance d'une équipe.



## 10. Une présentation courte



Le classeur comprend trois onglets :



- **Comparaison** : coût initial, fonctionnement annuel, cumuls 3/5/10/15 ans, écarts chiffrés expliqués, hypothèses déterminantes, courbes et premières mises en service. Le lecteur dispose aussi de la nature des données et des limites de couverture, sans ouvrir les calculs.

- **Hypothèses** : trois choix de prestations par solution, budgets de plateforme, forfaits et abonnements source, dates, indexations et options. Le calcul annuel sur quinze ans reste visible plus bas et lié à ces entrées.

- **Sources** : raisons des choix d'équipe, périmètres des offres, inclusions et exclusions ; rapprochement calculé des références RFI aux budgets initiaux. Le contrôle d’équipe SAP hors total est placé ici. Le détail initial est conservé dans l'étude, avec accès depuis le classeur.



Les paramètres communs sont saisis une seule fois. Les conventions de 0 % d'indexation des prestations et de 4 % des abonnements restent des hypothèses affichées, avec les gels contractuels ; elles ne sont pas des prévisions certaines. Les options restent distinctes et inactives par défaut.



Le Run commence à la prise en charge effective du service. Pour une estimation simple, une équipe complète peut être budgétée dès cette date : c'est une convention explicite, sans proportion automatique au nombre de fonctions déployées. Le support déjà financé dans le projet doit être rapproché avant d'activer la même prestation en Run. Cet échéancier est appliqué : capacité complète dès les premiers usages, sans pondération par le périmètre. Les interventions de stabilisation du projet et celles du service courant doivent être attribuées séparément ; la relève contractuelle reste à vérifier.

