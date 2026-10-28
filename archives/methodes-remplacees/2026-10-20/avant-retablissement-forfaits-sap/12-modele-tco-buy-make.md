![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 20 octobre 2026

---

# Coûts sur quinze ans — hypothèses et calculs

Cette annexe explique le [classeur FLOW](outputs/01a1530f-f378-7fd1-9654-468c9b2141b6/FLOW_Make_abaques_et_prix_France_v4.xlsx). La [note de décision](04-resultats-etude.md) présente les résultats. Les dépenses couvrent réalisation, fonctionnement, évolutions et souscriptions, en euros fournisseur HT courants depuis un lancement commun.

## 1. Lire la comparaison

**Initial / Annuel moyen / Cumuls 3, 5, 10 et 15 ans** restent visibles ensemble. La moyenne annuelle porte sur les **années 6 à 15**, après déploiement complet des trois systèmes ; elle inclut l'indexation et n'est pas le TCO divisé par quinze.

FLOW est livré à M60. Les premiers usages Buy arrivent à M18 ; l'horizon commun comprend donc davantage d'années d'usage Buy. Les jalons du graphique signalent les mises en service, sans déduire de bénéfices non mesurés. Les travaux internes Beaumanoir et la coexistence prolongée sont exclus selon les hypothèses de l'étude.

Un budget de référence est actif par solution. Les options Storeland, risque, lotissement additionnel, astreinte, migrations majeures et sortie restent séparées et désactivées. Une option de sortie ne signifie pas que le système est remplacé à la fin de l'horizon.

## 2. Toutes les étapes de calcul dans Excel

Les quantités, charges par unité, prix, pourcentages, périodes, activations et conventions de conversion sont exposés dans des cellules visibles. Les formules reprennent ces paramètres ; les JSON ou le programme de génération ne sont pas nécessaires pour refaire un calcul dans le classeur. Les huit sous-totaux Buy relevés par l'audit et quatre autres charges Microsoft sont désormais des sommes de sous-activités calculées, soit douze décompositions. Les valeurs source réutilisées sont liées à une cellule propriétaire.

Le chemin de lecture est : **hypothèses et prix → charges/ressources → calendrier mensuel → coûts annuels → comparaison**. Les sous-totaux de présentation reprennent les résultats ; ils ne créent pas un deuxième budget. Les entrées modifiables sont signalées, les calculs gardent leurs unités et les sources sont rattachées aux lignes concernées.

Les données sont qualifiées **source fournisseur**, **hypothèse de l'étude** ou **à confirmer**. Une valeur calculée à partir d'une hypothèse ne devient pas une offre commerciale. La feuille de conventions explique les conversions, la moyenne annuelle et le démarrage du fonctionnement.

## 3. Calendriers et démarrage du fonctionnement

| Solution | Travaux depuis le lancement | Déclenchement du fonctionnement |
| --- | --- | --- |
| FLOW | M0–M60 ; livraison unique M60. | 100 % après livraison, dix années pleines. |
| SAP | Pilote M0–M18 ; déploiement M18–M30 ; upgrade initial M0–M6. | 20 % après pilote, 80 % supplémentaires après déploiement. |
| Microsoft | Pilote M0–M18 ; pôles livrés M26/M30/M34/M38. | Cinq parts de 20 %, chacune après sa livraison. |

Les durées globales Buy viennent du COPIL Synvance ; la répartition des dépenses, les chevauchements et les poids de fonctionnement sont des hypothèses. Les matrices Delaware indiquent aussi 21 + 17 mois : divergence conservée dans les références. Les compléments chiffrés n'allongent pas le calendrier, sous hypothèse d'une capacité de réalisation suffisante.

La stabilisation initiale est supposée financée dans les travaux. Le panier de services SAP est appliqué dès les livraisons par convention ; les forfaits RFI restent des références distinctes. Les licences et Unified suivent leur calendrier contractuel ; ils ne sont pas bloqués jusqu'au démarrage métier.

Les consommations techniques de construction FLOW cessent à la livraison. Le panier de production commence ensuite. La recette CPI SAP et la recette externe Microsoft peuvent démarrer dès le chantier ; leurs composants de production suivent les premiers usages et le périmètre livré.

## 4. Réalisation initiale

FLOW : **32 100 JH × 750 €/JH = 24,075 M€**, plus **386 k€ de ressources de construction**, soit **24,461 M€**. Le budget distingue création du Core, Flux/sécurité, Business/configuration, et postes distincts de reprise/mise en service. Les spécifiques métier FLOW sont dans le Core. Les tests locaux et le pilotage propres à une fonction restent dans sa charge.

SAP et Microsoft : **Core initial = 0 €** pour la construction du produit éditeur existant. Les propositions d'intégration, les retraits hors périmètre et les fonctions réellement manquantes sont détaillés dans [la note Buy](15-rapprochement-buy-france.md). Aucune fraction du coût Make ne sert à estimer un complément Buy. Les droits de souscription sont calculés à part, y compris pendant les travaux.

Tarifs vendus France retenus : **750 €/JH FLOW**, **1 000 €/JH réalisation Buy**, **850 €/JH prestations spécialisées Buy**, **750 €/JH tests automatisés**. Les forfaits SAP source de maintenance, TMA et supervision restent dans les références ; ils ne sont ni majorés ni additionnés au panier de services retenu. Les compositions d'équipe, prix et arrondis restent visibles dans les feuilles de prix unitaire.

## 5. Service annuel : maintenance, exploitation et évolutions

**Service annuel** est l'abaque propriétaire des activités des trois options. Le nominal suppose un produit stabilisé, des contrôles automatisés et une équipe fournisseur mutualisée **en heures ouvrées en France**. Les trois options conservent **240 diagnostics/an**, en plus de la prévention. Aucune baisse de demande FLOW n'est déduite d'un gain supposé de prévention.

| Nature, année pleine avant inflation | FLOW | SAP | Microsoft |
| --- | ---: | ---: | ---: |
| Maintenance et pilotage applicatifs | 336 JH / 252 000 € | 306 JH / 260 100 € | 306 JH / 260 100 € |
| Versions techniques FLOW | 96 JH / 72 000 € | Standard dans souscription ; tests dans la maintenance | Standard dans souscription ; tests dans la maintenance |
| Exploitation humaine | 294 JH / 220 500 € | 234 JH / 198 900 € | 234 JH / 198 900 € |
| **Maintenance et exploitation** | **726 JH / 544 500 €** | **540 JH / 459 000 €** | **540 JH / 459 000 €** |
| **Évolutions métier, total comparable** | **320 JH / 240 000 €** | **420 JH / 357 000 €** | **440 JH / 374 000 €** |
| Dont versions fonctionnelles du Core FLOW | 120 JH / 90 000 € | Sans supplément distinct | Sans supplément distinct |
| Ressources FLOW, hors personnes | 400 000 € | Souscriptions et compléments décrits plus bas | Souscriptions et compléments décrits plus bas |
| **Total FLOW, hors options** | **1 046 JH + ressources = 1 184 500 €/an** | | |

La ligne « dont » des versions fonctionnelles ne s'additionne pas au total des évolutions. Les **162 k€ de versions courantes FLOW** sont compris dans les activités précédentes : 72 k€ techniques et 90 k€ fonctionnels. Le développement initial du Core et son maintien après livraison restent donc distingués.

Les 234 JH d'exploitation communs couvrent surveillance, rétablissement, paramètres/sécurité applicative, interfaces, procédures et PRA métier. FLOW ajoute 24 JH de configuration du runtime et 36 JH de vérification des sauvegardes/restauration. Ces deux activités techniques sont supposées financées par le cloud managé Buy. Cette couverture est à confirmer dans les contrats ; les PRA métier restent comptés dans les trois options.

Le panier de corrections comprend **60 correctifs FLOW** et **30 correctifs Buy**, à 3 JH chacun. Le Buy conserve le diagnostic de tous les incidents mais la fabrication des correctifs du standard est financée par la souscription. Les 30 correctifs couvrent toutes les adaptations et interfaces, y compris les compléments RFI. Aucun supplément proportionnel aux JH de construction n'est ajouté.

Le panier d'évolutions contient les mêmes 40 changements de règles, 10 fonctions/API et 4 changements structurants. Les efforts unitaires sont propres à chaque solution. Tests ciblés et pilotage de chaque évolution sont inclus ; la régression transverse est dans la maintenance. Ces volumes sont des hypothèses d'ingénierie ; ils ne garantissent pas une capacité suffisante sous incident majeur.

### Options de disponibilité et migration

| Option | Calcul de référence | Effet activé, année pleine | Valeur initiale |
| --- | --- | ---: | ---: |
| Astreinte P1 FLOW | 12 mois × 3 000 €/mois | 36 000 €/an | Désactivée |
| Migration majeure FLOW | 200 JH × 750 €/JH ÷ 3 ans | 50 000 €/an | Désactivée |
| Migration majeure SAP | 500 JH × 1 000 €/JH ÷ 4 ans | 125 000 €/an | Désactivée |

Les interventions P1 restent dans la capacité de traitement ; l'astreinte finance la disponibilité. Le nominal est sans astreinte pour les trois options. Activer l'option FLOW seule ne fournirait plus une comparaison de couverture identique ; une prestation Buy comparable devrait être chiffrée.

La migration majeure finance un panier exceptionnel au-delà des versions courantes. Les provisions annuelles sont une convention budgétaire : aucune facture supplémentaire aux anniversaires n'est ajoutée. La mise à niveau SAP initiale, prévue par l'offre et comprise dans la réalisation, reste financée. Microsoft conserve ses tests/adaptations de mise à jour dans la maintenance, sans deuxième forfait général.

## 6. Les forfaits RFI restent des références, distinctes du service retenu

**SAP — source :** Delaware p.37 et questionnaire onglet 8 annoncent **250 k€/an de MCO, 350 k€ de TMA évolutive et 450 k€ de monitoring**. Le monitoring décrit des horaires étendus ; le périmètre et les quantités de ces forfaits ne sont pas suffisamment détaillés pour les comparer directement au panier commun en heures ouvrées.

Ces prix sont conservés dans **Références**. Ils ne sont plus des montants minimaux ni des suppléments au nominal. Le budget annuel retenu provient des activités : **260,1 k€ de maintenance/pilotage + 198,9 k€ d'exploitation + 357 k€ d'évolutions** pour SAP, avant souscriptions et ressources complémentaires.

**Microsoft — hypothèses :** **260,1 k€ de maintenance/pilotage + 198,9 k€ d'exploitation + 374 k€ d'évolutions**, avant souscriptions et ressources complémentaires. Le forfait de supervision de 450 k€ copié de SAP est supprimé du calcul. Le supplément de 3 % des compléments fonctionnels est supprimé, pour SAP comme pour Microsoft ; le panier unique de corrections couvre ces extensions.

Les coûts annuels sont des estimations en France, pas des offres révisées des intégrateurs. La distinction standard/extension, la disponibilité en heures ouvrées et les tâches incluses dans le cloud managé sont des hypothèses explicites à confirmer lors d'une consultation. Aucune différence de couverture n'est utilisée implicitement pour faire apparaître un croisement de courbes.
### Support Microsoft Unified

Source : **90 k€ en année 1**, avec PQA/200 heures annoncées. Dès l'année 2, le modèle calcule **MAX(plancher 50 000 USD converti ; 7,5 % × part D365 × licences facturées)**. Les 70 % de part D365 et le taux de change de référence sont des hypothèses visibles. Le plancher suit les mois de contrat, pas les années de fonctionnement métier. Conditions exactes à confirmer.

## 7. Plateformes d'exécution

**FLOW : 400 k€/an existants**, ventilés en calcul, données, stock en mémoire/index, messages, solveur/batch, documents/sauvegardes, réseau/sécurité, observabilité, reprise, hors-production et outils propres au produit. Quantités et prix sont des hypothèses budgétaires, pas un devis cloud. Les factures de construction de **24/36/76/94/156 k€** restent séparées ; les outils génériques du fournisseur sont dans son tarif.

**Hébergement Buy standard :** inclus dans les abonnements décrits par les offres. Aucun cloud FLOW de 400 k€ ni seconde maintenance du Core éditeur n'est appliqué au Buy.

**SAP CPI / Integration Suite :** source Delaware p.45 « hors CPI ». Provision : deux tenants Standard à **4 635 €/mois**, 10 000 messages inclus par tenant, puis **6,08 €/mois par bloc additionnel de 10 000**. Hypothèses : 5 millions de messages mensuels en production et 0,5 million en recette, soit **151 222,08 €/an bruts à pleine charge**. Recette : **59 195,04 €/an** dès le chantier. Production : tenant dès premiers usages et messages au prorata livré.

Le voucher BTP est inclus mais non valorisé par l'offre. Le paramètre déductible vaut zéro faute de montant, sans affirmer une absence de crédit. Le complément est **MAX(0 ; CPI brut − crédit réellement imputable)**. Prix catalogue européen, architecture et trafic restent à confirmer ; aucun volume de pièces vendues n'est converti directement en messages.

**Microsoft externe : 45 k€/an conditionnels**, 12 k€ recette et 33 k€ production/API/messages/logs. Le coefficient passe à zéro si les droits et capacités déjà souscrits couvrent les extensions nécessaires. Aucun nouvel OMS complet ni hébergement du standard n'est acheté.

## 8. Inflation, quantités et contrats

- Prestations françaises et ressources techniques : **0 % d'inflation** dans la référence.
- Souscriptions : **4 %/an après gel**, SAP un an, Microsoft cinq ans. Calcul aux anniversaires contractuels, pas avec des exposants fractionnaires.
- CPI SAP : **4 %/an de prix**, séparé du crédit BTP et des quantités.
- Quantités : croissance **0 %** dans la référence. Les utilisateurs, messages, To et environnements restent des paramètres distincts des prix.
- Les retraits Finance/licences et la durée de protection K3 restent à confirmer commercialement. Des montants du panier proposé sont utilisés pour la projection, sans promesse de remise fournisseur.

Les licences sont facturées pendant la réalisation selon leurs propres assiettes annuelles. Leur somme mensuelle se réconcilie avec les coûts annuels. Aucun démarrage artificiel des abonnements après la livraison n'est supposé.

## 9. Sortie et coûts client

La sortie est une option inactive : **150 JH FLOW à 750 € = 112,5 k€ ; 190 JH SAP à 850 € = 161,5 k€ ; 170 JH Microsoft à 850 € = 144,5 k€** avant indexation. Mois réglable, M180 de référence. Elle ne provoque pas automatiquement l'arrêt des licences ou du fonctionnement.

La prestation couvre extraction, archivage, contrôles, transfert et arrêt. Successeur, chargement chez lui, double exploitation, conservation durable des archives et frais contractuels inconnus sont exclus. Aucun renouvellement complet n'est imposé à la fin des quinze années.

Les contributions internes sont séparées des coûts fournisseur et qualifiées non chiffrées/exclues. Un zéro technique ne signifie pas absence de travail Beaumanoir. L'option de co-construction ne doit pas devenir une facture fournisseur.

## 10. Contrôles et limites

Le classeur permet de contrôler les clés, la réconciliation de l'abaque unique, les activations, le démarrage du fonctionnement, les sommes mensuelles/annuelles, l'inflation et la somme des catégories. Les vérifications du fichier exporté et d'Excel natif sont consignées dans [l'audit](14-audit-inflation-run-et-comparaison.md).

Les contrôles démontrent la cohérence du calcul ; ils ne remplacent ni mesure de charge, ni contrat de services équivalents, ni consultation fournisseur. Les [abaques](09-abaques-repartition.md) et [méthodes de comparaison](16-methodes-et-presentation-comparaison-make-buy.md) explicitent ces limites.
