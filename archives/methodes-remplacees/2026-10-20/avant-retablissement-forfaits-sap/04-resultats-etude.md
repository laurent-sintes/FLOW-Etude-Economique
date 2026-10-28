![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 20 octobre 2026

---

# FLOW — note de décision

## Les chiffres pour décider

**Construire FLOW représente 24,5 M€ HT de réalisation initiale et 1,18 M€ HT de fonctionnement par année pleine**, sous les hypothèses retenues. Le prestataire fournit une équipe autonome en France ; FLOW est livré une seule fois au bout de cinq ans. Le fonctionnement finance maintenance, exploitation, versions courantes, évolutions et ressources techniques.

Les références SAP et Microsoft viennent de l'étude Synvance de 2025. Les compléments nécessaires au périmètre FLOW sont estimés à part. Le fonctionnement est recalculé sur une **base de service commune en heures ouvrées**, avec des responsabilités propres à chaque solution. **Les montants comparés sont des estimations de l'étude, pas de nouvelles propositions des éditeurs.**

| Coûts fournisseur HT | FLOW | SAP | Microsoft |
| --- | ---: | ---: | ---: |
| **Réalisation initiale** | **24,5 M€** | **17,1 M€** | **5,7 M€** |
| **Fonctionnement annuel moyen, années 6 à 15** | **1,2 M€/an** | **2,3 M€/an** | **2,0 M€/an** |
| Cumul à 3 ans | 14,6 M€ | 19,8 M€ | 9,0 M€ |
| Cumul à 5 ans | 24,5 M€ | 23,8 M€ | 12,7 M€ |
| Cumul à 10 ans | 30,4 M€ | 34,6 M€ | 22,3 M€ |
| **Cumul à 15 ans** | **36,3 M€** | **46,9 M€** | **33,1 M€** |

**Hypothèses actives :** fournisseur en France ; service humain en heures ouvrées ; 240 diagnostics/an pour chaque option ; prestations et ressources à prix constants ; licences et CPI à 4 % selon les gels ; options et contributions internes exclues. Les quantités restent constantes. Les tâches déjà financées par les souscriptions Buy sont identifiées dans le calcul.

Les cumuls partent d'un lancement commun, réalisation comprise. La moyenne annuelle porte sur les **années 6 à 15**, avec l'indexation ; ce n'est pas le total divisé par quinze. La réalisation FLOW comprend **24,075 M€ de prestations et 0,386 M€ de ressources techniques de construction**, soit **24,461 M€**. Le [classeur](outputs/01a1530f-f378-7fd1-9654-468c9b2141b6/FLOW_Make_abaques_et_prix_France_v4.xlsx) conserve les entrées, formules et unités.

### Quand les systèmes deviennent utilisables

| Jalon depuis le lancement | FLOW | SAP | Microsoft |
| --- | ---: | ---: | ---: |
| Première mise en service métier | Mois 60 | Mois 18 | Mois 18 |
| Déploiement complet | Mois 60 | Mois 30 | Mois 38 |
| Années équivalentes de fonctionnement dans l'horizon de quinze ans | 10,0 ans | 12,7 ans | 12,57 ans |

Les jalons figurent sur le graphique. Ils indiquent le début des usages ; aucun gain financier n'est déduit des dépenses. La mise à niveau technique SAP à M6 n'est pas considérée comme un nouveau service métier.

## Ce que finance le fonctionnement

| Services humains, année pleine avant inflation | FLOW | SAP | Microsoft |
| --- | ---: | ---: | ---: |
| Maintenance et pilotage applicatifs | 252,0 k€ | 260,1 k€ | 260,1 k€ |
| Versions techniques du Core FLOW | 72,0 k€ | Standard dans la souscription ; tests dans la maintenance | Standard dans la souscription ; tests dans la maintenance |
| Exploitation humaine | 220,5 k€ | 198,9 k€ | 198,9 k€ |
| **Maintenance et exploitation** | **544,5 k€** | **459,0 k€** | **459,0 k€** |
| **Évolutions métier, total comparable** | **240,0 k€** | **357,0 k€** | **374,0 k€** |
| Dont versions fonctionnelles du Core FLOW | 90,0 k€ | — | — |

Les 90 k€ de versions fonctionnelles FLOW sont **compris dans les 240 k€ d'évolutions**. Avec 400 k€ de ressources techniques, le fonctionnement FLOW atteint **1,1845 M€/an**. Les souscriptions Buy et leurs compléments de plateforme s'ajoutent aux prestations humaines et sont inclus dans les cumuls présentés plus haut.

La feuille **Service annuel** contient une seule ligne de calcul par activité et responsabilité. Les trois options conservent 240 diagnostics, en plus de la prévention. Les correctifs du standard Buy sont dans la souscription ; les corrections des adaptations et interfaces, compléments RFI compris, sont financées dans un seul panier. Les anciens suppléments de MCO à 3 %/5 % sont retirés.

FLOW porte davantage de responsabilités techniques : son exploitation ajoute la configuration du runtime et la vérification des sauvegardes/restauration. Ces activités sont supposées couvertes par le cloud managé Buy. Les contrôles applicatifs et le PRA métier restent comptés dans les trois solutions. L'inclusion contractuelle est à confirmer.

## Ce que la comparaison permet de conclure

**FLOW demande plus d'investissement initial et rend le service plus tard.** Le groupe finance son produit, maîtrise son code et évite une souscription de progiciel. Son panier annuel d'évolutions coûte moins cher dans les hypothèses retenues.

**Le Buy fournit des usages plus tôt et réduit la réalisation initiale.** Les souscriptions, adaptations et services spécialisés restent à financer. Les licences augmentent de 4 % par an après les périodes de prix maintenu ; les prestations françaises restent à prix constant.

**Microsoft reste moins cher que FLOW sur les quinze années présentées : environ 33,1 M€ contre 36,3 M€.** Les courbes FLOW/Microsoft ne se croisent plus dans cet horizon. La correction retire un forfait de supervision Microsoft qui ne provenait pas de son offre, supprime un recouvrement possible des corrections et conserve les 240 diagnostics FLOW. Elle ne remet pas en cause le différentiel de prix des évolutions ; ce différentiel ne suffit simplement pas à compenser l'investissement initial dans la période retenue.

SAP atteint environ **46,9 M€**. Le choix FLOW ne repose donc pas sur une économie garantie face à toutes les alternatives : il faut apprécier la maîtrise du produit, la facilité de modification et la dépendance éditeur. Ces bénéfices ne sont pas monétisés ici. Les dépenses cumulées ne constituent pas un calcul de retour sur investissement.

## Conditions et exclusions

| Compris | Hors budget de référence |
| --- | --- |
| Achats, ventes, retours, déstockage, stock/promesse et orchestration du fulfillment ; près de vingt marques, international et intercompany. | Finance, contrôle de gestion, conformité, design et planification stratégique ; gestion commerciale dédiée ; exécution WMS/TMS. |
| Fournisseur autonome : architecture, conception, réalisation, tests, pilotage, configuration, données actives, interfaces, sécurité et mise en service. | Temps interne Beaumanoir, reprise exhaustive des historiques, coexistence prolongée et options inactives. |
| Service humain en heures ouvrées ; plateformes, évolutions et licences retenues. | Astreinte/horaire étendu, garantie de capacité ou de SLA ; engagement de prix ou de délai. |

Tarifs France retenus : **750 €/JH FLOW**, **1 000 €/JH pour la réalisation SAP/Microsoft**, **850 €/JH pour les services spécialisés Buy**. Les volumes et tarifs restent des hypothèses d'achat. Les forfaits SAP RFI de **250/450/350 k€** sont conservés comme références documentaires ; ils ne sont plus utilisés pour imposer le même prix à des services de périmètre différent.

L'astreinte et les migrations majeures sont des **options désactivées**, ainsi que les 15 % de fonctions Storeland non découvertes, le lotissement additionnel, le risque et la sortie. Les versions courantes restent financées. Activer une couverture horaire supplémentaire pour une solution demanderait de chiffrer aussi le service comparable des autres solutions.

Les **400 k€/an de ressources FLOW** sont une provision détaillée par quantités et prix. L'hébergement standard Buy est déjà dans les abonnements. CPI SAP et les extensions Microsoft exécutées à l'extérieur sont des provisions conditionnelles. Le crédit BTP SAP reste à déduire lorsqu'il sera valorisé ; zéro signifie ici « montant non imputé faute d'information ».

### Pour vérifier

[Abaques et responsabilités](09-abaques-repartition.md) · [Budget initial FLOW](11-cout-nominal-minimum.md) · [Règles TCO](12-modele-tco-buy-make.md) · [Lecture du classeur](13-audit-classeur-excel.md) · [Validation](14-audit-inflation-run-et-comparaison.md) · [Détail SAP/Microsoft](15-rapprochement-buy-france.md)