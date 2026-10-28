![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 20 octobre 2026

---

# Validation — forfaits SAP et comparaison recalculée

## Base de calcul corrigée

SAP reprend **250 k€/an de MCO, 450 k€/an de supervision en horaires étendus et 350 k€/an de TMA**, issus de Delaware septembre 2025, page 37, et du questionnaire onglet 8. Les trois forfaits sont distincts ; aucun double compte source n’est démontré. Ils remplacent les abaques SAP de la version précédente, sans cumul.

Microsoft conserve une estimation par activités en heures ouvrées : **260,1 k€ de maintenance/pilotage, 198,9 k€ d’exploitation et 374 k€ d’évolutions par an**. Aucun forfait SAP ne lui est transposé. Les volumes et efforts ne sont pas issus d’une mesure Beaumanoir ou d’un devis Microsoft.

Les niveaux de service ne sont pas démontrés équivalents. La différence de couverture horaire apparaît dès la première page. Le budget ne présente aucune économie de renégociation SAP.

## Réconciliation des résultats

| Cumul à quinze ans | Version précédente | Version corrigée | Variation |
| --- | ---: | ---: | ---: |
| FLOW | 36,306 M€ | 36,306 M€ | 0 |
| SAP | 46,881716 M€ | 49,853516 M€ | +2,971800 M€ |
| Microsoft | 33,075615 M€ | 33,075615 M€ | 0 |

SAP : **(1 050 000 − 816 000) €/an × 12,7 années équivalentes = 2 971 800 €**. La maintenance diminue de 10 100 €/an, la supervision augmente de 251 100 €/an et la TMA diminue de 7 000 €/an. Ce sont des changements de base d’estimation, pas des économies fournisseur démontrées.

Les coûts initiaux, plateformes, abonnements et dates de livraison restent inchangés. Les forfaits SAP annoncés après stabilisation sont projetés au prorata livré par convention ; cette convention ne garantit pas un prix contractuel progressif.

## Frontières et hypothèses

| Point | Traitement |
| --- | --- |
| Sources SAP | Les forfaits de Références alimentent le budget une seule fois. Aucun panier en JH ne s’y ajoute. |
| Compléments OMS SAP | Réalisation initiale financée ; couverture dans les forfaits de service à confirmer. Aucun supplément automatique en pourcentage. |
| Corrections Microsoft | 30 correctifs/an supposés couvrir toutes les adaptations et interfaces. Standard dans la souscription ; capacité non mesurée. |
| Diagnostics FLOW/Microsoft | 240/an en plus de la prévention ; diagnostic distinct du développement des correctifs. |
| Maintenance / évolutions | Rétablissement du service séparé de la création de capacités. Tests ciblés et pilotage des évolutions déjà inclus dans leurs charges. |
| Exploitation / plateforme | Prestations humaines séparées des ressources. Couverture technique SaaS supposée selon les offres, détails contractuels à confirmer. |
| Core FLOW | 72 k€ de versions techniques et 90 k€ de versions fonctionnelles financés ; les 90 k€ sont compris dans les 240 k€ d’évolutions. |
| Options | Astreinte additionnelle et migrations majeures inactives. Le monitoring SAP en horaires étendus reste financé. |

## Calendrier, inflation et horizons

FLOW : livraison M60 ; SAP : premiers usages M18, fin M30 ; Microsoft : premiers usages M18, fin M38. Les années équivalentes de fonctionnement sur quinze ans sont **10 / 12,7 / 12,5667**.

Les services suivent les parts livrées. Les licences suivent leur calendrier propre, y compris pendant les travaux. Les ressources de construction FLOW cessent à la livraison. Prestations et ressources : **0 % d’inflation** ; licences : **4 % après gel**, CPI : **4 %** ; quantités constantes. L’indexation des forfaits SAP reste une hypothèse, sans clause contractuelle confirmée.

La comparaison conserve réalisation initiale, annuel moyen des années 6 à 15 et cumuls 3/5/10/15 ans, ainsi qu’un graphique commun avec jalons d’usage. Elle ne valorise pas les bénéfices et ne représente pas un ROI.

## Contrôles du fichier livré

Le [journal des contrôles](tmp/audit_sap_forfaits_restore.log) vérifie :

- la réconciliation indépendante des quatre horizons et des catégories de coûts ;
- la propagation de chacun des trois forfaits SAP vers le seul budget SAP, une seule fois ;
- l’absence d’effet des quantités Microsoft sur les forfaits SAP ;
- le rejet d’une source SAP manquante, sans conversion silencieuse en zéro ;
- les douze décompositions des charges initiales et l’effet d’une charge unitaire ;
- la séparation des indexations de prestations et de ressources ;
- les unités, liens internes, formules et absence de données masquées.

**19 contrôles réussis sur 19.** Le [rapport de recalcul Excel natif](tmp/FLOW_native_sap_forfaits.xlsx.native-report.json) associe les résultats à l’empreinte exacte du fichier contrôlé. Recalcul Excel 16 terminé : **zéro cellule d’erreur dans les 19 onglets**, aucune défaillance des contrôles de saisie ni des unités vérifiées.

Les vues modifiées sont vérifiées visuellement : comparaison avec graphique et unités, forfaits SAP, prix unitaires et hypothèses Microsoft. Les preuves précédentes sont conservées dans les [archives](archives/methodes-remplacees/2026-10-20/avant-retablissement-forfaits-sap/14-audit-inflation-run-et-comparaison.md).

Les tests valident le calcul et sa traçabilité. Ils ne valident ni le volume réel de demandes, ni la capacité contractuelle des forfaits, ni un prix futur de fournisseur. Les [abaques](09-abaques-repartition.md) et la [note de correction](18-corrections-services-et-tracabilite.md) explicitent ces limites.
