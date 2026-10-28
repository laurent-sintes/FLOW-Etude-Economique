> **Historique — retiré de la base active le 24 octobre 2026.** Les hypothèses et résultats de cette note sont remplacés par le [modèle YAML actuel](../../source/README.md).

![Logo eXalt](<../../assets/exalt-logo.png>)



**Laurent Sintès** · 21 octobre 2026



---



# Coûts sur quinze ans



## Convention de comparaison



Le modèle calcule les dépenses fournisseur HT en euros courants depuis un lancement commun. Il ne valorise ni les bénéfices métier ni les coûts internes client, et ne calcule pas de valeur actualisée. Les horizons 3, 5, 10 et 15 ans restent visibles ensemble. Le fonctionnement annuel moyen porte sur les années 6 à 15 et comprend les indexations ; ce n'est pas le cumul divisé par quinze.



## Réalisation et calendrier



| Option | Réalisation initiale | Premiers usages | Périmètre complet | Service financé sur 15 ans |

| --- | ---: | ---: | ---: | ---: |

| FLOW | 24,461 M€ | M60 | M60 | 10 ans |

| SAP | 17,133 M€ | M18 | M30 | 13,5 ans |

| Microsoft | 5,736 M€ | M18 | M38 | 13,5 ans |



Les budgets initiaux sont expliqués dans Sources, lignes 130–176. FLOW comprend 32 100 JH à 750 € et 386 k€ de ressources pendant la construction. Les budgets Buy associent références RFI et hypothèses d'adaptation à la cible ; les abonnements sont comptés séparément dans le calendrier. Les dates sont des hypothèses de comparaison ; les bénéfices des usages plus précoces ne sont pas monétisés.



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



## Indexation et souscriptions



Les prestations et ressources hors CPI SAP sont à 0 % d'indexation. CPI SAP, plateforme d'échange de données, est indexé de 4 % par an. Les licences sont indexées de 4 % après un gel supposé d'un an SAP et de cinq ans Microsoft. Ces hypothèses ne sont pas des engagements contractuels.



Les paniers de licence RFI sont conservés dans Sources. Le retrait Finance appliqué est une hypothèse de panier commercial réduit, à confirmer : 400 000 / 1 270 879 pour SAP et 10 % pour Microsoft. Unified suit son taux de 7,5 %, le minimum source de 50 000 USD et les paramètres visibles de part D365 et de conversion ; l'année initiale conserve 90 000 €.



L'hébergement standard Buy est déjà dans les souscriptions. Les ressources additionnelles sont la recette et production CPI SAP, et une provision Microsoft de 12 k€/an de recette puis jusqu'à 33 k€/an de production externe. Le tenant CPI de production démarre aux premiers usages ; les messages et ressources Microsoft suivent le périmètre livré. Le détail technique figure dans [l'annexe des plateformes](<16-methodes-et-presentation-comparaison-make-buy.md>).



## Options et limites



Storeland non découvert, lotissement additionnel, risque, astreinte et migrations majeures sont désactivés. Le temps interne client est hors total fournisseur ; une provision de co-construction peut être affichée séparément. La coexistence prolongée et le remplacement des anciens SI pendant la transition ne sont pas valorisés dans cette comparaison nominale. Aucune sortie de solution à la fin de l'horizon n'est supposée.



## Calcul et traçabilité



Sources porte les références et les budgets initiaux expliqués. Hypothèses porte les capacités, prix, dates et indexations, ainsi que les calculs annuels. Comparaison reprend les résultats, les jalons et les principales limites. Il n'y a pas d'autre onglet.



Les frontières de coût excluent une seconde imputation des mêmes activités au projet, au maintien et aux évolutions. Les contrôles mathématiques ne démontrent pas l'équivalence contractuelle des services ni la productivité des équipes. La [note de décision](<04-resultats-etude.md>) présente les résultats et leur portée.

