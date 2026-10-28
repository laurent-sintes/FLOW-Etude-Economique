![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 20 octobre 2026

---

# Validation — service annuel et comparaison

## Correction de la base de comparaison

L'[audit de la version précédente](17-audit-version-v4.md) relevait des horaires de service différents, un proxy de supervision Microsoft sans offre correspondante, un recouvrement possible des corrections Buy et huit sous-totaux calculés uniquement dans du texte.

La version corrigée estime un **service en heures ouvrées en France**, avec 240 diagnostics/an pour chaque solution. Les coûts sont calculés par activité dans **Service annuel**. Les forfaits SAP RFI restent des références, sans être ajoutés au panier nominal. Les [documents précédents](archives/methodes-remplacees/2026-10-20/avant-services-comparables/LIRE-AVANT-UTILISATION.md) sont conservés avec leurs anciennes preuves.

## Variation des charges annuelles

| Poste, année pleine avant inflation | Avant correction | Après correction | Effet annuel |
| --- | ---: | ---: | ---: |
| FLOW — maintenance et exploitation | 492 000 € / 656 JH | 544 500 € / 726 JH | **+52 500 €** : 140 diagnostics supplémentaires × 0,5 JH × 750 €. |
| FLOW — évolutions | 240 000 € | 240 000 € | Aucun changement. |
| FLOW — ressources | 400 000 € | 400 000 € | Aucun changement. |
| SAP — maintenance | 263 974 € | 260 100 € | **−3 874 €** : remplacement forfait source + supplément par activités complètes. |
| SAP — exploitation | 450 000 € | 198 900 € | **−251 100 €** : panier en heures ouvrées au lieu du forfait RFI en horaires étendus. |
| SAP — évolutions | 357 000 € | 357 000 € | Même panier, sans plancher RFI. |
| Microsoft — maintenance | 286 594,50 € | 260 100 € | **−26 494,50 €** : panier unique couvrant toutes les extensions, pilotage harmonisé. |
| Microsoft — exploitation | 450 000 € | 198 900 € | **−251 100 €** : calcul par activité au lieu du prix repris de SAP. |
| Microsoft — évolutions | 374 000 € | 374 000 € | Aucun changement. |

Le delta FLOW rétablit les **240 diagnostics**, sans supprimer la prévention. Le delta Buy ne doit pas être présenté comme une réduction commerciale négociée : c'est un **changement de méthode et de couverture hypothétique**, demandé pour comparer les options sur une base commune.

Les 30 correctifs annuels Buy couvrent tout le patrimoine d'adaptations/interfaces retenu. Les suppléments de 3 % des fonctions et 5 % des interfaces sont retirés. Le standard est maintenu dans la souscription, et les tests de version sont conservés dans les prestations.

## Frontières contrôlées

| Activités | Règle appliquée |
| --- | --- |
| Prévention / diagnostic / correction | Trois activités distinctes ; les 240 diagnostics sont conservés en plus de la prévention. Le diagnostic ne comprend pas le développement du correctif. |
| Tests ciblés / régression transverse | Tests propres au changement dans sa charge unitaire ; campagnes transverses dans la maintenance. |
| Pilotage du service / pilotage des évolutions | Revue de problèmes et du service séparée de la conduite de chaque évolution déjà incluse dans sa charge. |
| Exploitation / cloud | Les JH paient les personnes ; les lignes de plateforme paient les ressources. Les tâches de runtime/sauvegarde déjà couvertes par le cloud managé Buy ne sont pas rachetées. |
| Évolutions / versions fonctionnelles FLOW | Les 120 JH de versions fonctionnelles sont un « dont » des 320 JH, pas un ajout. |
| Options de migration | Provision annuelle ou campagne ponctuelle, jamais les deux pour les mêmes travaux. Options inactives dans le nominal. |
| Sources RFI / estimations courantes | Les 250/450/350 k€ SAP sont documentés dans les références, sans minimum ni supplément automatique. |

## Calendrier, inflation et horizons

Les dates restent inchangées : FLOW M60 ; SAP premiers usages M18 et fin M30 ; Microsoft premiers usages M18 et fin M38. Les années équivalentes de fonctionnement à quinze ans restent **10 / 12,7 / 12,5667**. Le service récurrent suit les parts livrées ; les ressources de construction FLOW s'arrêtent au début de la production.

Les abonnements suivent leurs calendriers contractuels, y compris pendant les travaux. La recette CPI et la recette externe Microsoft démarrent au chantier. Prestations et ressources techniques : **0 % d'inflation** ; licences : **4 % après gel** ; prix CPI : **4 %** ; croissance des quantités : **0 %**, séparée des prix. Les crédits BTP sont déduits une seule fois dans la limite de la facture.

La comparaison conserve initial, annuel moyen années 6–15 et cumuls 3/5/10/15 ans. Elle ne monétise pas les bénéfices, ne garantit pas un croisement et ne représente pas un ROI.

## Recalculabilité et preuves

Les huit sous-totaux Buy relevés par l'audit et quatre autres charges Microsoft sont remplacés par des sommes de sous-activités calculées, soit **douze décompositions**. Les sources réutilisées renvoient à leur cellule propriétaire. La convention de 200 JH/an est qualifiée comme hypothèse de l'étude. Les contrôles ne se limitent plus à chercher des constantes dans les formules : ils vérifient aussi la propagation des entrées unitaires jusqu'aux totaux.

**18 contrôles ciblés réussis sur 18**, selon le [journal de validation final](tmp/audit_service_revision_final.log). Ils vérifient notamment les budgets, le panier commun de diagnostics, les valeurs nulles et les zéros, l'absence d'effet des anciens suppléments MCO, l'indépendance du nominal vis-à-vis des forfaits SAP RFI, les douze décompositions, la propagation d'une charge unitaire et les indexations distinctes des personnes et ressources.

Le contrôle du fichier livré relève **19 onglets visibles, 8 269 formules, un graphique et 22 liens internes valides**. Il ne relève **aucune constante numérique dans les formules, aucune donnée masquée, aucune erreur de formule et aucune référence de calcul externe**. Ces vérifications structurales sont complétées par les tests de propagation des entrées.

Le [recalcul natif final dans Excel 16.0](tmp/FLOW_native_service_final.xlsx.native-report.json) est terminé (`CalculationState = 0`) : **zéro cellule d'erreur dans les 19 onglets**, aucune défaillance des contrôles de saisie ou des unités vérifiées. Les cellules de comparaison affichent **36,31 M€ FLOW, 46,88 M€ SAP et 33,08 M€ Microsoft** à quinze ans, pour les valeurs calculées exactes **36,306 / 46,881716 / 33,075615 M€**.

L'empreinte SHA-256 de la source de ces deux contrôles est **`FFBD0F99676C375753E73C49898B49985A43C403EF9D3DAD7DBB7A7BEAD2CF2E`**. Les 235 contrôles et l'empreinte C3A7… de l'audit17 concernent l'ancien fichier ; ils ne sont pas réutilisés comme preuve de cette version.

La relecture visuelle finale couvre la comparaison, le service annuel, les derniers abaques SAP/Microsoft, les liens et les unités. Les fiches Prix gardent leur rôle de budget initial, calendrier et options ; les cumuls restent sur la page Comparaison.

Le contrôle arithmétique ne valide ni le volume de demandes, ni la couverture contractuelle, ni le prix futur du fournisseur. Les hypothèses de capacité et d'inclusion restent visibles dans [l'abaque](09-abaques-repartition.md) et le [modèle TCO](12-modele-tco-buy-make.md).
