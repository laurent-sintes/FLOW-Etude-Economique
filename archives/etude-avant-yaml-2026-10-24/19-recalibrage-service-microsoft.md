> **Historique — retiré de la base active le 24 octobre 2026.** Les hypothèses et résultats de cette note sont remplacés par le [modèle YAML actuel](../../source/README.md).

> **Historique conservé.** Les montants, abaques de service et noms d’onglets ci-dessous décrivent les versions antérieures. Depuis le 21 octobre 2026, la [méthode](<02-methode-estimation.md>), la [note de décision](<04-resultats-etude.md>) et le [guide des trois onglets](<13-audit-classeur-excel.md>) portent le calcul courant.



![Logo eXalt](<../../assets/exalt-logo.png>)



**Laurent Sintès** · 20 octobre 2026



---



# Microsoft — service annuel recalibré pour Beaumanoir



> **Historique de calcul.** La [reprise de méthode](<02-methode-estimation.md>) remplace le dimensionnement par fréquences d'activité par un dispositif fournisseur expliqué. Les montants ci-dessous sont historiques et ne sont plus ceux du classeur courant.



## Résultat



Microsoft est estimé par **activités et compétences** : **472 JH / 401 200 € de maintenance-pilotage**, **443,5 JH / 376 975 € d’exploitation**, **440 JH / 374 000 € d’évolutions** par an, au tarif moyen France conservé de 850 €/JH. Les fréquences et efforts sont des hypothèses explicites, pas des mesures Beaumanoir ni un devis Microsoft.



**Sur quinze ans, FLOW atteint 36,31 M€, Microsoft 37,09 M€ et SAP 49,85 M€.** L’écart FLOW–Microsoft est d’environ **0,78 M€**, faible au regard des hypothèses d’activité et de couverture. Microsoft reste moins coûteux aux horizons de trois, cinq et dix ans et livre plus tôt. Le classement à quinze ans est conditionnel ; il ne démontre ni un ROI ni une économie garantie à service identique.



| Poste Microsoft, année pleine hors inflation | Avant | Recalibré | Écart |

| --- | ---: | ---: | ---: |

| Maintenance et pilotage | 306 JH / 260 100 € | 472 JH / 401 200 € | +141 100 € |

| Exploitation | 234 JH / 198 900 € | 443,5 JH / 376 975 € | +178 075 € |

| **Maintenance et exploitation** | **540 JH / 459 000 €** | **915,5 JH / 778 175 €** | **+319 175 €** |

| Évolutions | 440 JH / 374 000 € | 440 JH / 374 000 € | 0 |

| **Total services** | **980 JH / 833 000 €** | **1 355,5 JH / 1 152 175 €** | **+319 175 €** |



Les licences, Unified, plateformes, coûts initiaux, forfaits SAP, coûts FLOW et calendriers restent inchangés. Les évolutions Microsoft sont décomposées par compétence sans augmenter leur enveloppe.



## Base de dimensionnement



Le dimensionnement retient six domaines opérationnels et un repère de 40 interfaces issu du pilote Avanade, utilisé comme hypothèse de patrimoine cible. Il comprend 288 diagnostics fonctionnels, dont 72 analyses techniques additionnelles, 36 correctifs, quatre campagnes de versions et l’entretien des 120 scénarios automatisés déjà provisionnés au build. Les vingt marques partagent ces domaines ; aucun multiplicateur de CA, de volume vendu, de marque ou de coût Make n’est appliqué.



Les six domaines regroupent achats ; commandes/retours ; stock ; allocation/promesse ; fulfillment/intercompany ; documents opérationnels. C’est un découpage de travail pour cette estimation, pas un nombre de modules imposé.



Les activités détaillées sont présentées dans [les abaques](<09-abaques-repartition.md>) et entièrement calculées dans Excel. Les récurrences sont exprimées en mois, jours ouvrés, interfaces, campagnes ou domaines ; aucun taux forfaitaire du build n’est appliqué.



## Nature des preuves



| Élément | Statut |

| --- | --- |

| 40 interfaces du pilote | Source Avanade, réponse RFI #1 p. 39. Utilisation comme patrimoine cible : hypothèse, pas inventaire de FLOW. |

| 120 scénarios automatisés | Hypothèse déjà financée dans le build, reprise par formule dans l’entretien annuel. Aucun nouveau build ajouté. |

| Quatre publications D365 par an | Documentation Microsoft Learn ; deux adoptions au minimum. Retenir quatre campagnes et leurs efforts est une hypothèse du modèle. |

| Responsabilités client/intégrateur | Microsoft Learn : santé de la solution, intégrations, configurations, tests et coordination ne disparaissent pas en SaaS. |

| Incidents, correctifs et reprises | Hypothèses de fréquences, pas statistiques Beaumanoir. |

| 850 €/JH | Tarif moyen de prestation France déjà retenu, conservé ; pas un nouveau devis ni un tarif sourcé par compétence. |



Sources consultées le 20 octobre 2026 : [responsabilités de fonctionnement](https://learn.microsoft.com/en-us/dynamics365/guidance/implementation-guide/service-solution), [compétences du support](https://learn.microsoft.com/en-us/dynamics365/guidance/implementation-guide/transition-to-support-team), [mises à jour D365](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/get-started/public-preview-releases).



## Capacité et absence de double compte



Les mêmes jours sont ventilés entre fonctionnel, technique/intégration, développement, tests/versions et pilotage. **1 355,5 JH/an, évolutions comprises**, représentent **6,78 personnes-années** à 200 JH par personne-an. Ce contrôle de capacité n’ajoute aucun budget d’équipe. Le fournisseur est mutualisé, en heures ouvrées, sans engagement de présence dédiée ni astreinte.



Les règles de frontière sont :



- diagnostic fonctionnel puis, pour certains dossiers, analyse technique ; aucune double réception du ticket ;

- correction : conception, code et tests ciblés, séparés de la campagne transverse ;

- contrôle des alertes, cohérence des données et reprise effective sont trois travaux différents ;

- entretien des scripts existants dans la maintenance ; nouveaux scripts dans l’évolution concernée ;

- pilotage du service dans la maintenance ; pilotage de réalisation dans les évolutions ;

- coût des personnes dans le service ; ressources techniques et souscriptions dans leurs propres lignes ;

- tableau de compétences issu des activités, sans coût d’équipe ajouté.



## Comparaison recalculée



| Coûts fournisseur HT depuis le lancement | FLOW | SAP | Microsoft |

| --- | ---: | ---: | ---: |

| Réalisation initiale | 24,46 M€ | 17,13 M€ | 5,74 M€ |

| Fonctionnement moyen, années 6 à 15 | 1,18 M€/an | 2,54 M€/an | 2,36 M€/an |

| Cumul à 3 ans | 14,58 M€ | 19,98 M€ | 9,18 M€ |

| Cumul à 5 ans | 24,46 M€ | 24,42 M€ | 13,53 M€ |

| Cumul à 10 ans | 30,38 M€ | 36,41 M€ | 24,75 M€ |

| Cumul à 15 ans | 36,31 M€ | 49,85 M€ | 37,09 M€ |



Microsoft passe de **33,075615 à 37,086580 M€** à quinze ans. La variation se réconcilie : **319 175 €/an × 12,566667 années équivalentes de Run = 4 010 965,83 €**. Les services gardent une inflation nominale nulle ; licences et CPI conservent leurs indexations propres.



## Limites



Les forfaits SAP couvrent un monitoring en horaires étendus ; Microsoft et FLOW sont en heures ouvrées. L’équivalence contractuelle n’est pas établie. Le modèle suppose des processus stabilisés et une automatisation opérationnelle ; il ne finance pas une crise durable ou une présence 24/7.



Les prestations sont proratisées au périmètre livré selon la convention existante. Une capacité réelle n’est pas nécessairement divisible de cette manière. Les contributions internes et le L1 métier sont exclus ; les tâches applicatives du fournisseur restent bien dans les charges détaillées. Astreinte, migrations majeures et autres options restent inactives.



Le classement est une conséquence de ces hypothèses. Il n’est ni un objectif de calibration ni une économie démontrée. Les [contrôles](<14-audit-inflation-run-et-comparaison.md>) vérifient le calcul, pas la validité commerciale des volumes ou tarifs.

