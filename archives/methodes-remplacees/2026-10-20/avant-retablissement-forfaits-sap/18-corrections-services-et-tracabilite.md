![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 20 octobre 2026

---

# Corrections de l'étude et du classeur

Cette note répond à l'[audit de la version précédente](17-audit-version-v4.md). L'audit est conservé comme photographie datée ; la [note de décision](04-resultats-etude.md) et le classeur courant portent les budgets à utiliser.

## Ce qui change

| Réserve de l'audit | Correction appliquée | Limite conservée |
| --- | --- | --- |
| FLOW en heures ouvrées, SAP en horaires étendus, Microsoft avec un prix SAP copié | Base commune en heures ouvrées en France. Maintenance et exploitation Buy calculées par activités. Les forfaits RFI restent des références distinctes. | Pas un devis de service ni un SLA contractuel. |
| Prévention FLOW financée en réduisant les diagnostics à 100/an | 240 diagnostics/an pour les trois options, en plus de la prévention. FLOW augmente de 70 JH / 52,5 k€/an. | Nombre de demandes estimé, pas mesuré chez Beaumanoir. |
| Panier de corrections Buy plus supplément de 3 %/5 % du développement | Un seul panier couvre toutes les adaptations/interfaces, compléments RFI compris. Suppléments proportionnels supprimés. | Le standard est supposé maintenu par la souscription ; les tests et adaptations restent financés. |
| Huit sous-totaux en valeurs, détail seulement dans les notes | Douze décompositions : les huit charges de l'audit et quatre charges Microsoft supplémentaires. Quantités, JH/unités et sommes Excel ; charges initiales 548/639 JH inchangées. | Les efforts unitaires restent des hypothèses. |
| Données source dupliquées | Cellule propriétaire et renvois. Les 200 JH/an sont une convention de l'étude, pas une donnée COPIL. | Une source RFI reste indicative et limitée à son périmètre. |
| MCO ambigu et évolutions FLOW présentées partiellement | Maintenance, exploitation et évolutions séparées ; total des évolutions avec versions fonctionnelles FLOW en « dont ». | Les responsabilités diffèrent entre construction du Core et entretien d'un standard éditeur. |
| Synthèses répétées et navigation difficile | Comparaison seule page de décision ; Prix… limités au budget initial, calendrier et options ; Service annuel et Plateformes et sortie explicites ; unités et renvois harmonisés. | Le détail demeure visible pour permettre la vérification et la modification. |

## Pourquoi le classement change

FLOW conserve un prix annuel d'évolutions inférieur : **240 k€**, contre **357 k€ SAP et 374 k€ Microsoft**. En revanche, le modèle ne finance plus 450 k€/an de supervision pour Microsoft sur la base d'une offre SAP sans couverture commune. L'exploitation Buy calculée en heures ouvrées représente **198,9 k€/an** par solution. Les forfaits SAP 250/450/350 k€ ne sont ni effacés des sources ni présentés comme des offres renégociées.

Le nouveau budget FLOW est **1,1845 M€/an**, après maintien des 240 diagnostics. Le financement des versions techniques et fonctionnelles du Core reste compris. Les budgets Buy couvrent **459 k€/an de maintenance et d'exploitation** avant évolutions, abonnements et plateformes complémentaires.

| Cumul fournisseur à quinze ans | Avant correction | Après correction | Variation |
| --- | ---: | ---: | ---: |
| FLOW | 35,781 M€ | **36,306 M€** | **+0,525 M€** |
| SAP | 50,119886 M€ | **46,881716 M€** | **−3,238170 M€** |
| Microsoft | 36,564052 M€ | **33,075615 M€** | **−3,488438 M€** |

Sur quinze ans, Microsoft reste moins cher que FLOW d'environ **3,230 M€** dans les hypothèses retenues. Les changements annuels sont appliqués aux durées pondérées de fonctionnement : 10 ans FLOW, 12,7 ans SAP et 12,5667 ans Microsoft. Les réalisations initiales et les calendriers restent inchangés. Les résultats détaillés proviennent du [recalcul du modèle](tmp/service_audit_results.json).

Aucun croisement n'est recherché artificiellement. L'étude chiffre les dépenses ; la valeur de l'autonomie, de la configurabilité et des années de service plus tôt reste à apprécier séparément.

## Ce que cette correction ne prétend pas établir

Les horaires, volumes et responsabilités sont des **hypothèses de comparaison cohérentes**, pas une démonstration que les trois prestataires fourniront des contrats identiques. Les tâches de configuration du runtime et de sauvegarde/restauration sont supposées couvertes par le cloud managé Buy ; les contrôles applicatifs et PRA métier restent comptés.

Astreinte, migrations majeures, Storeland non découvert, lotissement additionnel, risque et sortie restent inactifs. Activer des horaires étendus pour FLOW demanderait de chiffrer aussi la couverture Buy correspondante. Les coûts internes Beaumanoir restent exclus.

Les preuves de calcul du nouveau fichier sont réunies dans [le journal de validation](14-audit-inflation-run-et-comparaison.md). Les anciennes valeurs et preuves sont conservées dans les [archives](archives/methodes-remplacees/2026-10-20/avant-services-comparables/LIRE-AVANT-UTILISATION.md).
