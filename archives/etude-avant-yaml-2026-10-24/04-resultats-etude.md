> **Historique — retiré de la base active le 24 octobre 2026.** Les hypothèses et résultats de cette note sont remplacés par le [modèle YAML actuel](../../source/README.md).

![Logo eXalt](<../../assets/exalt-logo.png>)



**Laurent Sintès** · 21 octobre 2026



---



# FLOW — note de décision



**Périmètre cible de la comparaison :** achats, ventes, retours, stock unifié et orchestration du cycle de vie des commandes et du fulfillment. Sont exclus la finance, la gestion commerciale, la conception produit, la planification stratégique et l’exécution logistique déléguée. FLOW est construit sur mesure ; les options SAP Delaware et Microsoft Dynamics 365/K3 s’appuient sur des progiciels complétés et intégrés. Leur couverture de toute la cible reste à confirmer.



## Ordre de grandeur retenu



**Construire FLOW représente 24,46 M€ HT de réalisation initiale, puis 1,75 M€ HT par année pleine de fonctionnement**, dans les hypothèses retenues. Le fournisseur est autonome en France. La livraison unique intervient au mois 60.



| Coûts fournisseur HT | FLOW | SAP | Microsoft |

| --- | ---: | ---: | ---: |

| Réalisation initiale | 24,46 M€ | 17,13 M€ | 5,74 M€ |

| Fonctionnement annuel moyen, années 6–15 | 1,75 M€/an | 2,54 M€/an | 2,56 M€/an |

| Cumul à 3 ans | 14,58 M€ | 20,82 M€ | 10,53 M€ |

| Cumul à 5 ans | 24,46 M€ | 25,26 M€ | 15,34 M€ |

| Cumul à 10 ans | 33,21 M€ | 37,25 M€ | 27,59 M€ |

| **Cumul à 15 ans** | **41,96 M€** | **50,69 M€** | **40,97 M€** |



Les cumuls partent du lancement du projet et comprennent la réalisation, les services humains, licences, support éditeur et ressources techniques. La moyenne annuelle porte sur les années 6 à 15 ; elle inclut les indexations. Ce sont des dépenses, sans actualisation ni valorisation des bénéfices métier.



## Pourquoi les coûts diffèrent



| Lecture de l’arbitrage | Résultat sous les hypothèses retenues |

| --- | --- |

| Effort initial FLOW face à Microsoft | **18,72 M€ de plus**, dont **15,26 M€ de construction du Core FLOW**. Les autres postes expliquent le solde ; le Core n’est pas un supplément ajouté au total. |

| Fonctionnement FLOW face à Microsoft | **0,81 M€/an de moins**, en moyenne sur les années 6 à 15, licences, ressources et services compris. |

| SAP face à Microsoft | L’écart vient principalement de la réalisation initiale : **17,13 contre 5,74 M€**, soit **11,40 M€ de plus pour SAP**. Le fonctionnement moyen est proche : **2,54 contre 2,56 M€/an**. Les bases RFI et les compléments estimés diffèrent ; le rapprochement est détaillé dans Sources, lignes 130–144, et dans [l’analyse des budgets Buy](<15-rapprochement-buy-france.md>). |

| Premiers usages | FLOW au mois 60, Microsoft et SAP au mois 18. **42 mois d’écart** ; les bénéfices des usages anticipés ne sont pas valorisés. |

| Cumul à quinze ans | FLOW reste **0,99 M€ au-dessus de Microsoft** ; SAP dépasse FLOW de **8,73 M€**. |

| Sensibilité simple | Une personne supplémentaire de maintien FLOW chaque année, à raison de 200 JH, coûte **150 k€/an**, donc **1,5 M€ sur dix ans**. Ce repère n’est ni une option activée ni une fourchette de prix. |



**L’écart d’environ 1 M€ entre FLOW et Microsoft à quinze ans ne démontre pas un avantage économique robuste.** Il est inférieur au repère de sensibilité de 1,5 M€ ci-dessus. Ce repère illustre la dépendance du classement aux hypothèses d’équipe ; il ne constitue pas un intervalle statistique d’incertitude.



### Nature des estimations



| Option | Base disponible | Hypothèses conservées | Points restant à confirmer |

| --- | --- | --- | --- |

| FLOW | Périmètre opérationnel et exigences de configuration définis. | Charges, prix fournisseur, équipe, ressources et livraison unique. | Productivité réelle, dimensionnement et engagement fournisseur. |

| SAP | RFI Delaware et forfaits annuels sourcés. | Valorisation France, retrait Finance, adaptations ciblées et tâches transférées au fournisseur. | Couverture de toute la cible, horaires, volumes et capacité d’évolution des forfaits. |

| Microsoft | Pilote RFI et projection COPIL des déploiements. | Valorisation France, compléments, transferts, équipe annuelle et ressources externes. | Couverture de toute la cible et conditions de souscription, dont gel de prix. |



La présence de prix source ne transforme pas les compléments estimés en offres fournisseurs. Aucun taux global de couverture non démontré n’est utilisé. FLOW/Microsoft sont dimensionnés en heures ouvrées ; le forfait SAP comporte une supervision étendue. L’équivalence contractuelle des services reste à établir.



### Hypothèses d’indexation et exclusions visibles



CPI signifie **Cloud Platform Integration** : c’est la plateforme SAP d’échange et de transformation des données entre systèmes, aujourd’hui associée à Cloud Integration dans SAP Integration Suite. Son abonnement finance une ressource technique, distincte du personnel d’exploitation. Les **ressources FLOW** désignent le cloud, le calcul, le stockage, les sauvegardes, les environnements et outils techniques ; les 400 k€/an ne comprennent pas les équipes de maintien et d’évolution. Une **personne-an** représente ici une capacité de 200 jours de travail par an ; plusieurs intervenants peuvent se la partager. RFI désigne la consultation fournisseur préalable.



Les prestations et ressources **hors CPI SAP** sont à prix constants. **CPI SAP est indexé de 4 %/an.** Les licences augmentent de 4 % après les gels supposés d’un an SAP et cinq ans Microsoft. Ces choix sont des hypothèses de projection. Les options Storeland non découvert, lotissement additionnel, risque, astreinte et migrations majeures restent inactives. Le temps interne client reste hors total fournisseur.



## Ce qui finance les services



| Services humains, année pleine | FLOW | SAP | Microsoft |

| --- | ---: | ---: | ---: |

| Base | Équipe estimée | Forfaits RFI Delaware | Équipe estimée |

| Maintien en service, exploitation et pilotage | 7 × 200 JH × 750 € = **1,05 M€** | 250 k€ MCO + 450 k€ supervision = **0,70 M€** | 6 × 200 JH × 850 € = **1,02 M€** |

| Évolutions fonctionnelles | 2 × 200 JH × 750 € = **0,30 M€** | **0,35 M€**, forfait | 2 × 200 JH × 850 € = **0,34 M€** |

| **Total services** | **1,35 M€/an** | **1,05 M€/an** | **1,36 M€/an** |



Les équipes FLOW/Microsoft couvrent les heures ouvrées françaises : trois capacités de service/exploitation, trois d’entretien et qualification FLOW contre deux Microsoft, une d’architecture et pilotage. Les deux capacités d’évolutions sont distinctes. Les [justifications](<02-methode-estimation.md>) décrivent les responsabilités et conditions de suffisance ; aucun volume fictif de tickets n’entre dans le calcul.



**Pas de deuxième enveloppe MCO ou exploitation.** Corrections, versions techniques et pilotage sont dans le maintien. Nouvelles fonctions, y compris nouvelles versions fonctionnelles du Core FLOW, sont dans les évolutions. Les ressources informatiques sont des factures distinctes des personnes. Les mêmes interventions ne doivent pas être imputées au projet et au Run.



SAP conserve ses forfaits source, avec supervision en horaires étendus. L’équipe SAP théorique de 6 + 2 personnes-an à 850 €/JH vaut 1,36 M€/an, mais **ne remplace pas et ne complète pas automatiquement les forfaits**. Leurs volumes et leur couverture de toute la cible FLOW ne sont pas établis. Les capacités d’évolution ne garantissent pas un nombre identique de fonctions livrées.



## Quand les systèmes rendent le service



| Depuis le lancement | FLOW | SAP | Microsoft |

| --- | ---: | ---: | ---: |

| Premiers usages | Mois 60 | Mois 18 | Mois 18 |

| Périmètre complet | Mois 60 | Mois 30 | Mois 38 |

| **Années de services financées à 15 ans** | **10** | **13,5** | **13,5** |



**Convention retenue : capacité complète de service dès les premiers usages**, à partir du mois suivant la livraison. Les abonnements et ressources de recette commencent pendant le projet. Le tenant CPI de production commence au premier usage ; ses messages et les ressources Microsoft suivent la montée du périmètre.



Le graphique montre les trois courbes et les jalons. Les coûts annuels sont interpolés pour placer ces dates ; ils ne constituent pas un échéancier mensuel de factures. Les gains métier restent non chiffrés.



## Lecture pour le décideur



FLOW demande davantage d’investissement et rend les premiers services plus tard. Il donne la maîtrise du produit et de ses règles. Le prix journalier et le budget d’évolutions sont inférieurs dans les hypothèses retenues, mais le groupe finance aussi l’entretien de tout le Core.



Le Buy réduit l’investissement initial et livre plus tôt. Les souscriptions et services subsistent. La projection retient 4 % d’indexation des licences après le gel : un an SAP et cinq ans Microsoft, hypothèses contractuelles à confirmer. Les prestations françaises et ressources hors CPI restent à 0 % ; CPI à 4 %. Aucun croisement n’est forcé : **FLOW reste environ 1,0 M€ au-dessus de Microsoft à quinze ans** dans le calcul courant.



L’écart FLOW–Microsoft ne démontre pas un avantage économique robuste et ne suffit pas à choisir une solution : les bénéfices de maîtrise, la couverture contractuelle et les fonctions réellement livrées ne sont pas monétisés. SAP et Microsoft gardent leurs différences de périmètre et les compléments estimés dans l’étude.



## Conditions et options



Le nominal comprend les fournisseurs ; les contributions internes Beaumanoir sont exclues. Storeland non découvert, lotissement additionnel, risque, co-construction client, astreinte et migrations majeures sont à zéro par défaut. La co-construction est affichée hors total fournisseur. Un zéro client ne signifie pas absence de travail interne.



Les 400 k€/an de ressources FLOW, CPI et extensions externes Microsoft sont des budgets d’hypothèse repris de l’étude. L’hébergement standard Buy est déjà dans les licences. Le crédit BTP reste non imputé faute de valeur ; les compléments de plateforme doivent être rapprochés des souscriptions.



Les 32 100 JH FLOW sont détaillés dans l’annexe de charge. Les budgets initiaux sont des entrées expliquées dans Sources ; les hypothèses annuelles et leur projection sont recalculables dans Hypothèses.



## Contrôles de cohérence



Les totaux ont été rapprochés des calculs annuels du classeur. Le recalcul Excel confirme les montants et les unités, sans erreur de formule détectée. Ces contrôles valident le calcul ; ils ne constituent ni un engagement fournisseur ni une validation de la suffisance des moyens.



[Méthode](<02-methode-estimation.md>) · [Guide du classeur](<13-audit-classeur-excel.md>) · [Pièces et références](<20-registre-sources.md>)

