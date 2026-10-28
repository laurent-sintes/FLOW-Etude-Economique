> **Historique — retiré de la base active le 24 octobre 2026.** Les hypothèses et résultats de cette note sont remplacés par le [modèle YAML actuel](../../source/README.md).

> **Historique conservé.** Les montants, abaques de service et noms d’onglets ci-dessous décrivent les versions antérieures. Depuis le 21 octobre 2026, la [méthode](<02-methode-estimation.md>), la [note de décision](<04-resultats-etude.md>) et le [guide des trois onglets](<13-audit-classeur-excel.md>) portent le calcul courant.



![Logo eXalt](<../../assets/exalt-logo.png>)



**Laurent Sintès** · 20 octobre 2026



---



# Validation — activités Microsoft et comparaison recalculée



## Base de calcul corrigée



SAP reprend **250 k€/an de MCO, 450 k€/an de supervision en horaires étendus et 350 k€/an de TMA**, issus de Delaware septembre 2025, page 37, et du questionnaire onglet 8. Les trois forfaits sont distincts ; aucun double compte source n’est démontré. Ils remplacent les abaques SAP de la version précédente, sans cumul.



Microsoft est recalibré par activités et compétences en heures ouvrées : **472 JH / 401 200 € de maintenance-pilotage, 443,5 JH / 376 975 € d’exploitation et 440 JH / 374 000 € d’évolutions par an**. Aucun forfait SAP ne lui est transposé. Les fréquences et efforts restent des hypothèses, sans mesure Beaumanoir ni devis Microsoft. La ventilation des jours par compétence ne crée pas de second budget.



Les niveaux de service ne sont pas démontrés équivalents. La différence de couverture horaire apparaît dès la première page. Le budget ne présente aucune économie de renégociation SAP.



## Réconciliation des résultats



| Cumul à quinze ans | Version précédente | Version corrigée | Variation |

| --- | ---: | ---: | ---: |

| FLOW | 36,306 M€ | 36,306 M€ | 0 |

| SAP | 49,853516 M€ | 49,853516 M€ | 0 |

| Microsoft | 33,075615 M€ | 37,086580 M€ | +4,010966 M€ |



Microsoft : **(778 175 − 459 000) €/an × 12,566667 années équivalentes = 4 010 965,83 €**. La maintenance augmente de 141 100 €/an et l’exploitation de 178 075 €/an. Les évolutions gardent leur enveloppe, avec une ventilation par compétence. L’écart est une révision de l’estimation des activités, pas un prix fournisseur confirmé.



Les coûts initiaux, plateformes, abonnements et dates de livraison restent inchangés. Les forfaits SAP annoncés après stabilisation sont projetés au prorata livré par convention ; cette convention ne garantit pas un prix contractuel progressif.



## Frontières et hypothèses



| Point | Traitement |

| --- | --- |

| Sources SAP | Les forfaits de Références alimentent le budget une seule fois. Aucun panier en JH ne s’y ajoute. |

| Compléments OMS SAP | Réalisation initiale financée ; couverture dans les forfaits de service à confirmer. Aucun supplément automatique en pourcentage. |

| Corrections Microsoft | Six domaines × six correctifs/an = 36 correctifs sur toutes les adaptations/interfaces. Standard dans la souscription ; fréquence estimée. |

| Diagnostics FLOW/Microsoft | FLOW : 240/an. Microsoft : 288 dossiers fonctionnels, dont 72 analyses techniques additionnelles. Pas de deuxième ticket ; travaux distincts. |

| Maintenance / évolutions | Rétablissement du service séparé de la création de capacités. Tests ciblés et pilotage des évolutions déjà inclus dans leurs charges. |

| Exploitation / plateforme | Prestations humaines séparées des ressources. Couverture technique SaaS supposée selon les offres, détails contractuels à confirmer. |

| Core FLOW | 72 k€ de versions techniques et 90 k€ de versions fonctionnelles financés ; les 90 k€ sont compris dans les 240 k€ d’évolutions. |

| Options | Astreinte additionnelle et migrations majeures inactives. Le monitoring SAP en horaires étendus reste financé. |



## Calendrier, inflation et horizons



FLOW : livraison M60 ; SAP : premiers usages M18, fin M30 ; Microsoft : premiers usages M18, fin M38. Les années équivalentes de fonctionnement sur quinze ans sont **10 / 12,7 / 12,5667**.



Les services suivent les parts livrées. Les licences suivent leur calendrier propre, y compris pendant les travaux. Les ressources de construction FLOW cessent à la livraison. Prestations et ressources : **0 % d’inflation** ; licences : **4 % après gel**, CPI : **4 %** ; quantités constantes. L’indexation des forfaits SAP reste une hypothèse, sans clause contractuelle confirmée.



La comparaison conserve réalisation initiale, annuel moyen des années 6 à 15 et cumuls 3/5/10/15 ans, ainsi qu’un graphique commun avec jalons d’usage. Elle ne valorise pas les bénéfices et ne représente pas un ROI.



## Contrôles du fichier livré



Le [journal des contrôles](<../../tmp/audit_ms_service_calibration.log>) vérifie :



- la réconciliation indépendante des quatre horizons et des catégories de coûts ;

- la propagation de chacun des trois forfaits SAP vers le seul budget SAP, une seule fois ;

- l’absence d’effet des quantités Microsoft sur les forfaits SAP ;

- la propagation d’un domaine et d’une interface supplémentaires vers Microsoft seulement ;

- le rejet d’un nombre cible d’interfaces manquant et d’un nombre d’analyses techniques supérieur aux dossiers ;

- la réconciliation des cinq compétences avec les 1 355,5 JH / 1 152 175 € de services, sans deuxième budget ;

- le rejet d’une source SAP manquante, sans conversion silencieuse en zéro ;

- les douze décompositions des charges initiales et l’effet d’une charge unitaire ;

- la séparation des indexations de prestations et de ressources ;

- les unités, liens internes, formules et absence de données masquées.



**23 contrôles réussis sur 23.** Le [rapport de recalcul Excel natif](<../../tmp/FLOW_native_ms_calibration.xlsx.native-report.json>) associe les résultats à l’empreinte exacte du fichier contrôlé. Recalcul Excel 16 terminé : **zéro cellule d’erreur dans les 19 onglets**, aucune défaillance des contrôles de saisie ni des unités vérifiées.



Les vues modifiées sont vérifiées visuellement : comparaison avec graphique et unités, entrées, activités, compétences et prix unitaires Microsoft. Les preuves précédentes sont conservées dans les [archives](<../methodes-remplacees/2026-10-20/avant-recalibrage-service-microsoft/14-audit-inflation-run-et-comparaison.md>).



Les tests valident le calcul et sa traçabilité. Ils ne valident ni le volume réel de demandes, ni la capacité contractuelle des forfaits, ni un prix futur de fournisseur. Les [abaques](<09-abaques-repartition.md>) et le [recalibrage Microsoft](<19-recalibrage-service-microsoft.md>) explicitent ces limites.

