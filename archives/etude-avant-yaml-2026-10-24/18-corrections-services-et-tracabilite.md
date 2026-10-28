> **Historique — retiré de la base active le 24 octobre 2026.** Les hypothèses et résultats de cette note sont remplacés par le [modèle YAML actuel](../../source/README.md).

> **Historique conservé.** Les montants, abaques de service et noms d’onglets ci-dessous décrivent les versions antérieures. Depuis le 21 octobre 2026, la [méthode](<02-methode-estimation.md>), la [note de décision](<04-resultats-etude.md>) et le [guide des trois onglets](<13-audit-classeur-excel.md>) portent le calcul courant.



![Logo eXalt](<../../assets/exalt-logo.png>)



**Laurent Sintès** · 20 octobre 2026



---



# Base SAP rétablie et hypothèses Microsoft



> **Historique :** cette note décrit la version précédant le recalibrage Microsoft. Les forfaits SAP restent actifs ; les anciens montants Microsoft ci-dessous sont remplacés par le [recalibrage par activités et compétences](<19-recalibrage-service-microsoft.md>). La note de décision et le classeur portent les résultats courants.



## Décision de méthode



SAP utilise les forfaits Delaware : **250 k€/an de MCO, 450 k€/an de supervision en horaires étendus et 350 k€/an d’évolutions**. FLOW et Microsoft restent estimés par activité en heures ouvrées. Les volumes des forfaits SAP ne sont pas documentés : **l’équivalence des niveaux de service et des capacités d’évolution n’est pas démontrée**.



Le précédent remplacement de la supervision SAP de 450 à 198,9 k€/an supposait une économie de service non démontrée. Il est annulé. Les abaques restent utiles pour Microsoft, dont le forfait de 450 k€ était une transposition SAP et non une offre Microsoft.



## Réconciliation annuelle



| Poste SAP | Avant cette correction | Base retenue | Variation |

| --- | ---: | ---: | ---: |

| MCO | 260 100 € | 250 000 € | −10 100 € |

| Supervision | 198 900 € | 450 000 € | +251 100 € |

| Évolutions | 357 000 € | 350 000 € | −7 000 € |

| **Total hors abonnements/plateformes** | **816 000 €** | **1 050 000 €** | **+234 000 €** |



Ces forfaits se substituent aux abaques SAP abandonnés ; ils ne s’y ajoutent pas. La TMA de 350 k€ ne s’additionne ni à 357 k€ ni à un supplément en pourcentage.



## Comparaison recalculée



| Cumul fournisseur à quinze ans | Version précédente | Version corrigée | Variation |

| --- | ---: | ---: | ---: |

| FLOW | 36,306 M€ | 36,306 M€ | 0 |

| SAP | 46,881716 M€ | 49,853516 M€ | +2,971800 M€ |

| Microsoft | 33,075615 M€ | 33,075615 M€ | 0 |



Le delta SAP se réconcilie : **234 000 €/an × 12,7 années équivalentes de Run = 2 971 800 €**. Les coûts initiaux, licences, plateformes, indexations et dates de livraison restent inchangés. Les forfaits sont proratisés au périmètre livré par convention ; cette montée en charge n’est pas un échéancier contractuel.



Par rapport à la version antérieure à la normalisation (SAP 50,119886 M€), le nouveau total reste inférieur de 0,266370 M€ : retrait du supplément MCO estimé de 13 974 €/an et retour de 357 à 350 k€/an de TMA, sur 12,7 années. Ce choix de budget ne prouve pas que la maintenance des compléments serait gratuite.



## Microsoft : ce qui est estimé



Microsoft est une **hypothèse d’ingénierie en France**, pas un devis de services : **306 JH × 850 € = 260,1 k€ de maintenance/pilotage**, **234 JH × 850 € = 198,9 k€ d’exploitation**, **440 JH × 850 € = 374 k€ d’évolutions**. Les quantités et efforts sont modifiables ; ils ne proviennent pas d’un historique d’incidents Beaumanoir. Aucun forfait SAP n’est transposé.



Les diagnostics reprennent une hypothèse commune avec FLOW. Les 30 corrections couvrent toutes les adaptations, interfaces et compléments OMS ; les quatre campagnes de tests et douze revues de pilotage sont des conventions d’activité. L’exploitation chiffre sept activités distinctes ; les évolutions chiffrent 40 règles, 10 fonctions et 4 changements structurants. Aucun de ces volumes n’est présenté comme mesuré ou confirmé par Avanade.



Le passage antérieur de 450 à 198,9 k€ de supervision Microsoft ne représente pas une remise. Le classement Microsoft/FLOW est conditionnel à la suffisance de ces charges, aux prestations couvertes par les abonnements et aux tarifs français retenus.



## Limites conservées



Aucun supplément automatique de 3 %/5 % des développements n’est ajouté. Microsoft suppose que ses 30 correctifs annuels couvrent toutes les extensions et interfaces, compléments OMS compris. Pour SAP, le budget conserve les forfaits source ; **la couverture des compléments OMS/interfaces reste à confirmer**. L’absence de supplément ne démontre pas leur gratuité.



Astreinte FLOW et migrations majeures restent des options désactivées. Le monitoring SAP en horaires étendus reste financé dans le forfait de 450 k€ ; ce libellé ne prouve pas une couverture 24/7. FLOW et Microsoft sont estimés en heures ouvrées. Les prestations ne sont pas présentées comme contractuellement équivalentes.



Les budgets ne sont ni des devis révisés ni une preuve d’économie à prestation identique. Les sources restent dans Références ; les hypothèses et formules sont visibles dans Service annuel et les prix unitaires.



Les [contrôles](<14-audit-inflation-run-et-comparaison.md>) portent sur le calcul et la traçabilité. La [version précédente](<../methodes-remplacees/2026-10-20/avant-retablissement-forfaits-sap/18-corrections-services-et-tracabilite.md>) est conservée comme historique, sans valeur de budget courant.

