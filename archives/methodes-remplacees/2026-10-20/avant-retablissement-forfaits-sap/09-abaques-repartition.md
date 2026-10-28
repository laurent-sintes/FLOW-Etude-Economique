![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 20 octobre 2026

---

# Répartition des charges et des coûts

## Ce que les clés font

Les clés ci-dessous répartissent **32 100 JH et 24,075 M€ HT** entre natures de travaux. Ce sont des **hypothèses de l'étude**, pas des ratios de productivité mesurés. Elles ne changent ni les quantités totales ni les tarifs. Les catégories ne sont pas des lots : les lots correspondent aux jalons de déploiement.

Le **Core** inclut tout code métier du produit FLOW et les mécanismes réutilisables de configuration. **Business** désigne les données, politiques, règles et paramètres initiaux Beaumanoir. **Flux** couvre les interfaces et le raccordement à la sécurité. Les **Spécifiques** sont utiles pour classer les extensions d'un progiciel Buy ; dans FLOW, ils sont compris dans le Core.

## Clés des quatorze postes FLOW

| Poste de chiffrage | JH | Core | Business | Flux | Reprises et mise en service distinctes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Références opérationnelles | 1 400 | 30 % | 35 % | 35 % | 0 % |
| Politiques de supply chain | 1 000 | 45 % | 55 % | 0 % | 0 % |
| Gestion du stock | 3 000 | 80 % | 10 % | 10 % | 0 % |
| Disponibilité et promesse | 1 700 | 85 % | 10 % | 5 % | 0 % |
| Gestion des commandes | 3 500 | 75 % | 15 % | 10 % | 0 % |
| Dossiers et processus | 1 800 | 80 % | 20 % | 0 % | 0 % |
| Orchestration du fulfillment | 1 800 | 70 % | 15 % | 15 % | 0 % |
| Prestations et documents | 1 400 | 70 % | 20 % | 10 % | 0 % |
| Plan opérationnel et carnet | 3 500 | 75 % | 20 % | 5 % | 0 % |
| Configuration gouvernée | 4 000 | 100 % | 0 % | 0 % | 0 % |
| Interfaces et contrats SI | 3 000 | 15 % | 0 % | 85 % | 0 % |
| Reprise des données actives | 2 000 | 0 % | 0 % | 0 % | 100 % |
| Plateforme technique et qualification | 3 000 | 75 % | 5 % | 20 % | 0 % |
| Mise en service unique | 1 000 | 0 % | 0 % | 0 % | 100 % |
| **Charges par catégorie** | **32 100** | **20 345** | **3 795** | **4 960** | **3 000** |
| **Coût à 750 €/JH, M€ HT** | **24,075** | **15,25875** | **2,84625** | **3,72000** | **2,25000** |

Pour chaque poste, les coefficients totalisent 100 %. Les responsabilités propres au produit, comme le stock et la disponibilité, sont principalement classées en Core ; les politiques initiales portent davantage de configuration ; les adaptateurs sont principalement classés en Flux. Construire le moteur de configuration relève intégralement du Core.

**Les tests et le pilotage propres à chaque fonction restent dans sa charge.** La dernière catégorie isole les postes distincts de reprise et de mise en service ; ses 2,25 M€ ne recensent pas tout l'effort qualité et pilotage FLOW. Ce regroupement retire 1,125 M€ des anciennes clés Business et autant des Flux, sans changer le Core ni le total.

Les clés historiques de ces deux postes restent dans le calcul détaillé du classeur pour traçabilité ; leur reclassement de présentation est appliqué une seule fois. L'option Storeland n'est pas ventilée tant que les fonctions manquantes ne sont pas connues.

## Clés SAP et Microsoft

Le [modèle de répartition](tools/flow_cost_structure.json) décrit chaque groupe de travaux, sa quantité, son prix, sa source et ses clés. Les jours d'interfaces et de spécifiques identifiés dans le RFI sont classés directement. Ils restent compris dans le budget source.

- **SAP :** les 1 467 JH d'interfaces et 1 319 JH de spécifiques sont sourcés. Conversions et mise à niveau initiale sont classées avec les reprises et la mise en service. Le solde RFI utilise une hypothèse de **70 % Business / 30 % pilotage, tests et mise en service**.
- **Microsoft :** la ventilation du pilote retenu suit ses lignes documentées. Les déploiements utilisent une hypothèse de **20 % Flux / 55 % Business / 25 % tests et mise en service**.
- **Travaux techniques confiés au prestataire :** clé estimée commune de **40 % Flux / 20 % Business / 40 % qualification, reprises et bascule**.

Les retraits hors FLOW reprennent la répartition des travaux concernés par convention de présentation. Les compléments fonctionnels vont dans Spécifiques, l'accompagnement dans Business et l'automatisation supplémentaire des tests dans le poste de qualification. Le [tableau financier](15-rapprochement-buy-france.md) donne les résultats. Aucune part du coût Make ne sert à estimer un complément Buy.

## Services annuels : un abaque par activité

La feuille **Service annuel** regroupe les activités de maintenance, d'exploitation et d'évolution des trois solutions. Les autres feuilles reprennent ces résultats. Une activité appartient à une seule catégorie de coût ; les vues de synthèse ne constituent pas des suppléments.

### Même besoin de service, responsabilités identifiées

Le service de référence est fourni **en heures ouvrées par une équipe mutualisée en France**. Le modèle conserve **240 diagnostics applicatifs/an pour les trois options**, en plus de la prévention. Il ne suppose aucun gain de capacité FLOW lié à la surveillance préventive. Le support L1, les contributions internes et l'exécution WMS/TMS restent exclus.

| Activité annuelle | FLOW | SAP | Microsoft | Frontière du calcul |
| --- | ---: | ---: | ---: | --- |
| Diagnostics applicatifs | 240 × 0,5 = 120 JH | 120 JH | 120 JH | Analyse d'incident, hors surveillance courante et correction du code. |
| Corrections | 60 × 3 = 180 JH | 30 × 3 = 90 JH | 30 × 3 = 90 JH | Produit FLOW complet ; adaptations/interfaces Buy dans un panier unique, compléments RFI compris. Maintenance du standard Buy dans la souscription. |
| Pilotage du service | 12 × 3 = 36 JH | 36 JH | 36 JH | Priorités d'incidents et revues de service ; conduite des évolutions comprise dans leurs charges. |
| Versions techniques et régression | 96 JH | 4 × 15 = 60 JH | 4 × 15 = 60 JH | Dépendances et livraisons FLOW ; tests/adaptations de version Buy, hors fabrication du standard éditeur. |
| Exploitation | 294 JH | 234 JH | 234 JH | Alertes, rétablissements, flux, procédures et reprise ; tâches de plateforme managée Buy déjà financées dans les abonnements. |
| **Maintenance et exploitation** | **726 JH** | **540 JH** | **540 JH** | **Activités distinctes, sans forfait supplémentaire.** |
| Tarif de prestation | 750 €/JH | 850 €/JH | 850 €/JH | Hypothèses d'achat France. |
| **Coût annuel maintenance et exploitation** | **544 500 €** | **459 000 €** | **459 000 €** | **Avant inflation et hors options.** |

Les volumes de demandes constituent des **hypothèses de l'étude**, pas des mesures Beaumanoir. Le nombre inférieur de corrections Buy suppose que les correctifs du produit standard sont fournis par l'éditeur dans la souscription. Il ne suppose pas que le progiciel rencontre moins d'incidents : les 240 diagnostics sont conservés.

La maintenance applicative et le pilotage représentent **336 JH / 252 k€ FLOW**. Les versions techniques FLOW représentent **96 JH / 72 k€**. Pour le Buy, tests de versions compris, la maintenance et le pilotage représentent **306 JH / 260,1 k€**. L'exploitation représente **220,5 k€ FLOW** et **198,9 k€ pour chaque option Buy**. Les responsabilités financées par le cloud managé Buy sont explicitées dans le classeur ; elles ne sont pas assimilées à un service gratuit.

Les **234 JH d'exploitation communs** financent 50 JH de contrôles préventifs, 20 de rétablissement, 24 de paramètres/sécurité applicative, 72 de reprises d'interfaces, 24 de fiabilité des flux, 24 de procédures et 20 de PRA métier. FLOW ajoute **24 JH de configuration du runtime et 36 JH de vérification des sauvegardes/restauration**. Ces deux activités techniques sont supposées couvertes par le cloud managé Buy ; les contrôles et PRA métier restent comptés dans les trois options. Cette inclusion est à vérifier contractuellement.

### Évolutions : même panier de demandes

| Demande annuelle | Quantité commune | FLOW | SAP | Microsoft |
| --- | ---: | ---: | ---: | ---: |
| Règles et paramètres métier | 40 | 80 JH | 140 JH | 120 JH |
| Fonctions ou API | 10 | 120 JH | 140 JH | 160 JH |
| Changements structurants | 4 | 120 JH | 140 JH | 160 JH |
| **Total** | | **320 JH** | **420 JH** | **440 JH** |
| **Coût annuel** | | **240 000 €** | **357 000 €** | **374 000 €** |

Les 120 JH de changements structurants FLOW financent les versions fonctionnelles du Core. Ils sont un **« dont » des 320 JH**, pas un supplément. Les tests ciblés et la conduite de chaque changement sont compris dans sa charge ; la régression transverse reste dans la maintenance. Les différences de JH par changement et de tarif sont des hypothèses, pas des gains de productivité mesurés.

### Ce qui remplace les anciens forfaits et pourcentages

Les forfaits Delaware de **250 k€/an de MCO, 450 k€ de monitoring et 350 k€ de TMA évolutive** restent lisibles dans les références RFI. Ils ne pilotent plus le nominal comparé : leur couverture horaire et leur décomposition ne permettent pas de les assimiler au panier en heures ouvrées. Le modèle ne reprend plus les 450 k€ SAP comme prix Microsoft.

Les corrections Buy couvrent désormais tout le patrimoine retenu, y compris les compléments fonctionnels de 548 JH SAP et 639 JH Microsoft. **Aucun ajout de 3 % des développements ou de 5 % des interfaces n'est appliqué au panier annuel.** Les 350 k€ de TMA SAP ne s'ajoutent pas aux 357 k€ du panier d'évolutions et ne servent plus de plancher.

### Options et ressources distinctes

Astreinte et migrations majeures restent des options désactivées. Aucune présence humaine hors heures ouvrées n'est financée pour les trois options. Activer l'astreinte FLOW isolément ne constituerait plus une comparaison de services identiques ; les services Buy équivalents devraient alors être chiffrés. Les versions techniques courantes et les tests de mise à jour sont financés dans le service nominal. Lorsqu'une migration est provisionnée annuellement, aucune seconde facture de campagne n'est ajoutée.

Les **400 k€/an de ressources FLOW** financent calcul, données, stockage, réseau et outils propres au produit. Ils sont séparés des interventions humaines. Les **386 k€ de ressources de construction** cessent à la livraison ; le panier de production commence ensuite. L'hébergement standard Buy est dans les souscriptions. CPI SAP et le runtime externe Microsoft restent des provisions conditionnelles détaillées dans [le modèle TCO](12-modele-tco-buy-make.md).

## Des abaques recalculables dans Excel

Les huit charges auparavant saisies comme totaux — 55, 107, 99, 90 JH Microsoft et 42, 100, 100, 54 JH SAP — sont détaillées en sous-activités : **quantité × JH/unité**, puis somme. Quatre autres charges Microsoft sont également décomposées, soit **douze décompositions recalculables**. Les notes expliquent la fonction et le périmètre ; elles ne contiennent plus l'unique version du calcul. Les 548/639 JH initiaux restent inchangés.

Le détail se trouve dans **Passage Buy France, lignes 190 à 266** : quantité en colonne C, JH par unité en E et total calculé en G. Les lignes de budget reprennent ces sous-totaux ; modifier une composante actualise le prix initial et les cumuls une seule fois.

Les sources réutilisées renvoient à une cellule propriétaire. La convention de **200 JH par personne et par an** est identifiée comme convention de l'étude, et non comme donnée COPIL. Les unités JH, €/JH, €/an et coefficients sont visibles au bon endroit.

Les contrôles vérifient les clés à 100 %, les sommes d'activités, les options, la propagation des entrées et les résultats aux horizons demandés. Leur réussite confirme la cohérence du modèle ; elle ne transforme pas les volumes estimés en engagements de service.
