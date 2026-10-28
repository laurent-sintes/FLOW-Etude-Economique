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

### Base SAP : trois forfaits sourcés

SAP utilise les forfaits Delaware : **250 k€/an de MCO, 450 k€/an de supervision en horaires étendus et 350 k€/an d’évolutions**. FLOW et Microsoft restent estimés par activité en heures ouvrées. Les volumes des forfaits SAP ne sont pas documentés : **l’équivalence des niveaux de service et des capacités d’évolution n’est pas démontrée**.

| Poste SAP | Budget annuel | Base |
| --- | ---: | --- |
| MCO hors évolutions | 250 000 € | Delaware p. 37 ; questionnaire onglet 8. |
| Monitoring des flux en horaires étendus | 450 000 € | Même source ; contenu et volumes non détaillés. |
| TMA évolutive | 350 000 € | Enveloppe ; capacité en changements non documentée. |
| **Total prestations SAP** | **1 050 000 €** | Hors abonnements et plateformes complémentaires. |

Les forfaits sont utilisés directement. Aucun abaque en JH ne s’y ajoute et aucune réduction au prorata horaire n’est supposée.

### Hypothèses Microsoft, distinctes des sources SAP

Microsoft est une **hypothèse d’ingénierie en France**, pas un devis de services : **306 JH × 850 € = 260,1 k€ de maintenance/pilotage**, **234 JH × 850 € = 198,9 k€ d’exploitation**, **440 JH × 850 € = 374 k€ d’évolutions**. Les quantités et efforts sont modifiables ; ils ne proviennent pas d’un historique d’incidents Beaumanoir. Aucun forfait SAP n’est transposé.

| Activité Microsoft | Quantité × effort | Charge annuelle |
| --- | ---: | ---: |
| Diagnostics | 240 × 0,5 JH | 120 JH |
| Corrections des adaptations/interfaces | 30 × 3 JH | 90 JH |
| Tests de versions | 4 × 15 JH | 60 JH |
| Pilotage du service | 12 × 3 JH | 36 JH |
| **Maintenance et pilotage** | | **306 JH** |
| Revue des alertes | 250 × 0,2 JH | 50 JH |
| Rétablissement technique | 10 × 2 JH | 20 JH |
| Paramètres, sécurité, capacité applicative | 12 × 2 JH | 24 JH |
| Reprises d’interfaces et rejets métier | 36 × 2 JH | 72 JH |
| Fiabilité des flux | 12 × 2 JH | 24 JH |
| Procédures d’exploitation | 12 × 2 JH | 24 JH |
| Exercice de reprise du service métier | 4 × 5 JH | 20 JH |
| **Exploitation** | | **234 JH** |

Ces volumes dimensionnent un service mutualisé en heures ouvrées. Les 250 journées sont une convention de calendrier ; les autres fréquences ne sont pas des observations. Diagnostics, correctifs, rétablissements et reprises d’interfaces sont des activités distinctes. Leurs frontières sont explicitées dans Excel.

### FLOW et évolutions

FLOW conserve **726 JH × 750 € = 544 500 € de maintenance/exploitation** : 72 k€ de versions techniques, 252 k€ de maintenance/pilotage et 220,5 k€ d’exploitation. Les 240 diagnostics sont conservés en plus de la prévention.

| Évolutions estimées | Quantité/an | FLOW JH/unité | Microsoft JH/unité |
| --- | ---: | ---: | ---: |
| Règles métier | 40 | 2 | 3 |
| Fonctions / API | 10 | 12 | 16 |
| Changements structurants | 4 | 30 | 40 |
| **Total JH** | | **320** | **440** |
| **Coût annuel** | | **240 000 €** | **374 000 €** |

Les 120 JH / 90 k€ de versions fonctionnelles FLOW sont compris dans les 320 JH. SAP conserve 350 k€ de TMA ; rien ne prouve que cette enveloppe livre exactement le même panier de changements.

Aucun supplément automatique de 3 %/5 % des développements n’est ajouté. Microsoft suppose que ses 30 correctifs annuels couvrent toutes les extensions et interfaces, compléments OMS compris. Pour SAP, le budget conserve les forfaits source ; **la couverture des compléments OMS/interfaces reste à confirmer**. L’absence de supplément ne démontre pas leur gratuité.

### Options et ressources

Astreinte FLOW et migrations majeures restent des options désactivées. Le monitoring SAP en horaires étendus reste financé dans le forfait de 450 k€ ; ce libellé ne prouve pas une couverture 24/7. FLOW et Microsoft sont estimés en heures ouvrées. Les prestations ne sont pas présentées comme contractuellement équivalentes.

Les ressources FLOW restent séparées : **400 k€/an** après livraison, **386 k€** au total pendant la construction. L’hébergement standard Buy est dans les abonnements. CPI SAP et le runtime externe Microsoft sont des provisions conditionnelles détaillées dans le [modèle TCO](12-modele-tco-buy-make.md).

## Des abaques recalculables dans Excel

Les huit charges auparavant saisies comme totaux — 55, 107, 99, 90 JH Microsoft et 42, 100, 100, 54 JH SAP — sont détaillées en sous-activités : **quantité × JH/unité**, puis somme. Quatre autres charges Microsoft sont également décomposées, soit **douze décompositions recalculables**. Les notes expliquent la fonction et le périmètre ; elles ne contiennent plus l'unique version du calcul. Les 548/639 JH initiaux restent inchangés.

Le détail se trouve dans **Passage Buy France, lignes 190 à 266** : quantité en colonne C, JH par unité en E et total calculé en G. Les lignes de budget reprennent ces sous-totaux ; modifier une composante actualise le prix initial et les cumuls une seule fois.

Les sources réutilisées renvoient à une cellule propriétaire. La convention de **200 JH par personne et par an** est identifiée comme convention de l'étude, et non comme donnée COPIL. Les unités JH, €/JH, €/an et coefficients sont visibles au bon endroit.

Les contrôles vérifient les clés à 100 %, les sommes d'activités, les options, la propagation des entrées et les résultats aux horizons demandés. Leur réussite confirme la cohérence du modèle ; elle ne transforme pas les volumes estimés en engagements de service.
