> **Historique — retiré de la base active le 24 octobre 2026.** Les hypothèses et résultats de cette note sont remplacés par le [modèle YAML actuel](../../source/README.md).

![Logo eXalt](<../../assets/exalt-logo.png>)



**Laurent Sintès** · 21 octobre 2026



---



# Répartition des charges et des coûts



## Ce que les clés font



Les clés ci-dessous répartissent **32 100 JH et 24,075 M€ HT** entre natures de travaux. Ce sont des **hypothèses de l'étude**, pas des ratios de productivité mesurés. Elles ne changent ni les quantités totales ni les tarifs. Les catégories ne sont pas des lots : les lots correspondent aux jalons de déploiement.



Le **Core** inclut tout code métier du produit FLOW et les mécanismes réutilisables de configuration. **Business** désigne les données, politiques, règles et paramètres initiaux Beaumanoir. **Flux** couvre les interfaces et le raccordement à la sécurité. Les **Spécifiques** sont utiles pour classer les extensions d'un progiciel Buy ; dans FLOW, ils sont compris dans le Core.



## Clés des quatorze postes FLOW



| Poste de chiffrage | JH | Core | Business | Flux | Reprises et mise en service distinctes |

| --- | ---: | ---: | ---: | ---: | ---: |

| Références opérationnelles | 1 400 | 30 % | 35 % | 35 % | 0 % |

| Politiques de supply chain | 1 000 | 45 % | 55 % | 0 % | 0 % |

| Gestion du stock | 3 000 | 80 % | 10 % | 10 % | 0 % |

| Disponibilité et promesse | 1 700 | 85 % | 10 % | 5 % | 0 % |

| Gestion des commandes | 3 500 | 75 % | 15 % | 10 % | 0 % |

| Dossiers et processus | 1 800 | 80 % | 20 % | 0 % | 0 % |

| Orchestration du fulfillment | 1 800 | 70 % | 15 % | 15 % | 0 % |

| Prestations et documents | 1 400 | 70 % | 20 % | 10 % | 0 % |

| Plan opérationnel et carnet | 3 500 | 75 % | 20 % | 5 % | 0 % |

| Configuration gouvernée | 4 000 | 100 % | 0 % | 0 % | 0 % |

| Interfaces et contrats SI | 3 000 | 15 % | 0 % | 85 % | 0 % |

| Reprise des données actives | 2 000 | 0 % | 0 % | 0 % | 100 % |

| Plateforme technique et qualification | 3 000 | 75 % | 5 % | 20 % | 0 % |

| Mise en service unique | 1 000 | 0 % | 0 % | 0 % | 100 % |

| **Charges par catégorie** | **32 100** | **20 345** | **3 795** | **4 960** | **3 000** |

| **Coût à 750 €/JH, M€ HT** | **24,075** | **15,25875** | **2,84625** | **3,72000** | **2,25000** |



Pour chaque poste, les coefficients totalisent 100 %. Les responsabilités propres au produit, comme le stock et la disponibilité, sont principalement classées en Core ; les politiques initiales portent davantage de configuration ; les adaptateurs sont principalement classés en Flux. Construire le moteur de configuration relève intégralement du Core.



**Les tests et le pilotage propres à chaque fonction restent dans sa charge.** La dernière catégorie isole les postes distincts de reprise et de mise en service ; ses 2,25 M€ ne recensent pas tout l'effort qualité et pilotage FLOW. 



L’option Storeland n’est pas ventilée tant que les fonctions manquantes ne sont pas connues.



## Clés SAP et Microsoft



Les clés de répartition ci-dessous et les quantités de l’annexe Buy décrivent les travaux retenus. Les jours d'interfaces et de spécifiques identifiés dans le RFI sont classés directement. Ils restent compris dans le budget source.



- **SAP :** les 1 467 JH d'interfaces et 1 319 JH de spécifiques sont sourcés. Conversions et mise à niveau initiale sont classées avec les reprises et la mise en service. Le solde RFI utilise une hypothèse de **70 % Business / 30 % pilotage, tests et mise en service**.

- **Microsoft :** la ventilation du pilote retenu suit ses lignes documentées. Les déploiements utilisent une hypothèse de **20 % Flux / 55 % Business / 25 % tests et mise en service**.

- **Travaux techniques confiés au prestataire :** clé estimée commune de **40 % Flux / 20 % Business / 40 % qualification, reprises et bascule**.



Les retraits hors FLOW reprennent la répartition des travaux concernés par convention de présentation. Les compléments fonctionnels vont dans Spécifiques, l'accompagnement dans Business et l'automatisation supplémentaire des tests dans le poste de qualification. Le [tableau financier](<15-rapprochement-buy-france.md>) donne les résultats. Aucune part du coût Make ne sert à estimer un complément Buy.



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

