> **Historique — retiré de la base active le 24 octobre 2026.** Les hypothèses et résultats de cette note sont remplacés par le [modèle YAML actuel](../../source/README.md).

![Logo eXalt](<../../assets/exalt-logo.png>)



**Laurent Sintès** · 21 octobre 2026



---



# FLOW — calcul du budget initial de référence



Le **forfait initial de prestations FLOW est de 24,1 M€ HT** : **32 100 jours de travail à 750 €/jour**, pour construire le logiciel, l'intégrer au SI Beaumanoir et le mettre en service une seule fois. Le prestataire fournit une équipe autonome basée en France : ingénieurs, architectes, responsables techniques, analystes métier, testeurs et pilotage.



Le **budget de référence** est calculé sans options ni réserve de risque, sur les charges retenues pour les fonctions identifiées. Les quantités de travail, la composition d'équipe et les frais fournisseur sont des **hypothèses de l'étude**. Cette annexe en conserve le calcul ; la [note de décision](<04-resultats-etude.md>) présente la comparaison financière. Un seul budget par option est utilisé dans le dossier courant.



## Frontière du calcul



| Inclus dans le forfait nominal | Exclu de ce calcul |

| --- | --- |

| Conception et développement FLOW Make, moteur de configuration, stock/promesse/commandes/optimisation, tests et qualification, documentation et pilotage fournisseur. | Valorisation des équipes internes Beaumanoir en support, expertise, validation ou gouvernance. Leur intervention reste nécessaire à la réalisation, mais n'est pas facturée dans ce poste. |

| Configuration/adaptation initiale, migration des données actives et branchement aux systèmes et à la sécurité du groupe. | Support et exploitation après mise en service, coexistence prolongée avec les anciens SI, hébergement de production et coûts récurrents. |

| Préparation, répétition et exécution **d'une mise en service unique**. | Vagues successives de déploiement, accompagnement additionnel associé à ces vagues. |

| Le périmètre opérationnel **identifié** de FLOW. | Les développements Storeland encore non découverts : **option de périmètre de 15 % du nominal** dans le classeur ; autres majorations et réserve d'exécution. |



## Charge fournisseur : 32 100 jours



Le [modèle de charge courant](<06-premier-ordre-de-grandeur-effort.md>) retient **31 100 JH de réalisation et de préparation**, plus **1 000 JH de mise en service unique** pour répétition, préparation, formation fournie, bascule et démarrage. Les 1 000 JH constituent une hypothèse d’ingénierie, non une productivité mesurée.



Le prestataire prend en charge **tous les travaux de réalisation chiffrés ici** avec une équipe autonome. Les JH couvrent une équipe pluridisciplinaire, métier inclus : le calcul suppose que le prestataire porte l'analyse métier opérationnelle, le PO et la coordination nécessaires à la livraison. Les contributions internes de Beaumanoir ne sont **pas ajoutées** au prix. Ce transfert de responsabilité n'a pas fait l'objet d'une mesure de productivité distincte ; il est une condition du calcul.



| Calcul de charge | JH |

| --- | ---: |

| Réalisation et préparation, hors poste distinct de mise en service | 31 100 |

| Mise en service unique, hypothèse de travail | 1 000 |

| **Charge de référence avec mise en service unique** | **32 100 JH** |

| Option Storeland non découverte : `32 100 × 15 %` | **4 815 JH**, hors nominal |



La charge de **32 100 JH** couvre les postes identifiés avec mise en service unique. Les fonctions Storeland non découvertes sont une option ; l'activer porterait la charge à **36 915 JH** avant les autres majorations. Les charges unitaires n'ont pas été étalonnées sur une réalisation FLOW ; leur qualification reste **À confirmer** par les premières réalisations et par une consultation fournisseur.



### Budget retenu hors options



**32 100 JH × 750 €/JH = 24 075 000 € HT**, soit **24,1 M€ HT**. Le dossier présente cette valeur de référence sous les hypothèses décrites, sans estimation basse/haute ni probabilité attachée. Le passage d'une mise en service à plusieurs livraisons constitue une option séparée.



## Prix d'un dispositif de développement sur mesure



Le prix FLOW correspond à une équipe de développement sur mesure, comprenant architecture, développement, données, qualification et pilotage. La composition diffère de celle d'une équipe d'intégration de progiciel. Les prix SAP et Microsoft sont justifiés séparément dans la [note de comparaison](<15-rapprochement-buy-france.md>).



L'abaque de prix ci-dessous est une **hypothèse de composition d'équipe autonome en France**, non une ventilation constatée des JH FLOW. Les taux sont situés à partir des baromètres français primaires [Malt Java 2026](https://www.malt.fr/t/barometre-tarifs/tech/developpeur-backend/developpeur-java), [Malt chefs de projet 2026](https://www.malt.fr/t/barometre-tarifs/gestion-de-projets-coaching/chef-de-projet), [Silkhom TJM 2025](https://www.silkhom.com/barometre-des-tjm-informatique-electronique-digital/) et [Freeland 2026](https://barometre.freeland.com/tjm). Malt observe notamment **579 €/jour** en France pour les développeurs Java expérimentés ; Silkhom situe un lead Java à **600–700 €/jour à Paris**, et Freeland affiche **650 €/jour** de médiane française pour les architectes, avec des profils plus chers selon leur responsabilité. Ces baromètres décrivent surtout des tarifs **de freelances affichés ou observés**, pas un prix signé pour une équipe au forfait.



| Fonction dans l'équipe externe | Part des JH, hypothèse | Taux de référence €/JH, hypothèse | Contribution au taux pondéré |

| --- | ---: | ---: | ---: |

| Ingénieurs de développement Java, front et intégration logicielle | 45 % | 580 | 261,0 € |

| Lead developers | 15 % | 650 | 97,5 € |

| Architectes logiciel, données et décisions de plateforme | 12 % | 800 | 96,0 € |

| PO, analystes métier et pilotage de livraison | 10 % | 650 | 65,0 € |

| Ingénieurs QA et automatisation des tests | 8 % | 475 | 38,0 € |

| DevOps, sécurité, data et performance | 10 % | 680 | 68,0 € |

| **Moyenne pondérée des profils** | **100 %** | — | **625,5 €/JH** |



Les **37 % de lead, architecture et spécialités plateforme** de cet abaque rendent visible la part technologique plus forte d'un produit construit sur mesure. Les **JH Make** utilisés au calcul comprennent déjà le développement du moteur de configuration, la plateforme technique, l'architecture du stock, les interfaces et la qualification ; on ne rajoute donc pas un deuxième poste « architecture » aux JH.



Pour estimer le prix vendu d'une **équipe fournisseur autonome**, le calcul ajoute **20 % de frais de structure, gestion et marge commerciale** : `625,5 × 1,20 = 750,6 €/JH`, arrondis à **750 €/JH**. **Hypothèse de l'étude :** les 20 % ne viennent pas d'un baromètre ni d'une offre reçue. Ils ne constituent pas une réserve de risque. **À confirmer :** un prestataire devra proposer un prix pour l'équipe et les responsabilités décrites ; la marge réelle et la répartition des métiers pourront différer.



## Résultat



`32 100 JH × 750 €/JH = 24 075 000 € HT`, soit **24,1 M€ HT de budget de référence** pour les postes identifiés de construction et d'intégration initiale FLOW Make, **sous les hypothèses ci-dessus**. L'option Storeland de `15 % × 24 075 000 € = 3 611 250 € HT` est affichée séparément dans le classeur.



Ce montant de prestations reste un **ordre de grandeur sous hypothèses**, avant consultation au forfait. Il ne compte pas le développement Storeland inconnu, le support, la coexistence, les coûts récurrents ni le travail interne. La livraison en une fois réduit l'enveloppe de déploiement, sans démontrer qu'elle réduit la difficulté de la bascule. L'ordre de grandeur de **24,1 M€ HT** est un point de départ pour juger une offre fournisseur répondant au périmètre écrit.



Le calcul repose principalement sur **trois paramètres visibles** : les charges retenues par poste, les **1 000 JH** choisis pour la mise en service unique et le prix complet moyen de **750 €/JH** issu d'une composition d'équipe et d'une hypothèse de frais fournisseur. Leur modification nécessite d’actualiser le budget initial dans Sources et sa répartition ; le calcul annuel reprend ensuite ces entrées.



### Factures techniques pendant la construction



Le forfait de **24,075 M€** finance les prestations de réalisation. Les factures cloud propres à la construction sont ajoutées séparément : **24 k€ en année 1, 36 k€ en année 2, 76 k€ en année 3, 94 k€ en année 4 et 156 k€ en année 5**, soit **386 k€** sur cinq ans.



Le calcul retient de deux à six environnements allégés, une capacité mensuelle croissante et des campagnes temporaires de charge. Les consommations s'arrêtent à la livraison et laissent place au panier de production. Il s'agit d'une **hypothèse de consommation** ; ce supplément ne rémunère pas une seconde fois les 3 000 JH de plateforme et qualification. Les outils de travail génériques du fournisseur restent dans son forfait.



La charge et son tarif restent donc lisibles à part des ressources techniques achetées. Les totaux par horizon sont calculés dans le classeur et présentés dans la [note de décision](<04-resultats-etude.md>).



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

