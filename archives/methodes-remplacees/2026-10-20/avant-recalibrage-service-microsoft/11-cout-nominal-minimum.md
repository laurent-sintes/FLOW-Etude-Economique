![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 20 octobre 2026

---

# FLOW — calcul du budget initial de référence

Le **forfait initial de prestations FLOW est de 24,1 M€ HT** : **32 100 jours de travail à 750 €/jour**, pour construire le logiciel, l'intégrer au SI Beaumanoir et le mettre en service une seule fois. Le prestataire fournit une équipe autonome basée en France : ingénieurs, architectes, responsables techniques, analystes métier, testeurs et pilotage.

Le **budget de référence** est calculé sans options ni réserve de risque, sur les charges retenues pour les fonctions identifiées. Les quantités de travail, la composition d'équipe et les frais fournisseur sont des **hypothèses de l'étude**. Cette annexe en conserve le calcul ; la [note de décision](04-resultats-etude.md) présente la comparaison financière. Un seul budget par option est utilisé dans le dossier courant.

## Frontière du calcul

| Inclus dans le forfait nominal | Exclu de ce calcul |
| --- | --- |
| Conception et développement FLOW Make, moteur de configuration, stock/promesse/commandes/optimisation, tests et qualification, documentation et pilotage fournisseur. | Valorisation des équipes internes Beaumanoir en support, expertise, validation ou gouvernance. Leur intervention reste nécessaire à la réalisation, mais n'est pas facturée dans ce poste. |
| Configuration/adaptation initiale, migration des données actives et branchement aux systèmes et à la sécurité du groupe. | Support et exploitation après mise en service, coexistence prolongée avec les anciens SI, hébergement de production et coûts récurrents. |
| Préparation, répétition et exécution **d'une mise en service unique**. | Vagues successives de déploiement, accompagnement additionnel associé à ces vagues. |
| Le périmètre opérationnel **identifié** de FLOW. | Les développements Storeland encore non découverts : **option de périmètre de 15 % du nominal** dans le classeur ; autres majorations et réserve d'exécution. |

## Charge fournisseur : 32 100 jours

Le [modèle de charge courant](06-premier-ordre-de-grandeur-effort.md) retient **31 100 JH de réalisation et de préparation**, plus **1 000 JH de mise en service unique** pour répétition, préparation, formation fournie, bascule et démarrage. Ce dernier poste remplace les 2 000 JH de pilote et bascules du modèle historique, conservé en archive. Cette réduction est une **hypothèse d'ingénierie explicite**, non une économie observée ou un ratio de marché.

Le prestataire prend en charge **tous les travaux de réalisation chiffrés ici** avec une équipe autonome. Les JH antérieurs représentaient une équipe pluridisciplinaire, métier inclus : leur réinterprétation en jours de forfait fournisseur suppose que le prestataire porte l'analyse métier opérationnelle, le PO et la coordination nécessaires à la livraison. Les contributions internes de Beaumanoir ne sont **pas ajoutées** au prix. Ce transfert de responsabilité n'a pas fait l'objet d'une mesure de productivité distincte ; il est une condition du calcul.

| Calcul de charge | JH |
| --- | ---: |
| Réalisation et préparation, hors poste distinct de mise en service | 31 100 |
| Mise en service unique, hypothèse de travail | 1 000 |
| **Charge de référence avec mise en service unique** | **32 100 JH** |
| Option Storeland non découverte : `32 100 × 15 %` | **4 815 JH**, hors nominal |

La charge de **32 100 JH** couvre les postes identifiés avec mise en service unique. Les fonctions Storeland non découvertes sont une option ; l'activer porterait la charge à **36 915 JH** avant les autres majorations. Les charges unitaires n'ont pas été étalonnées sur une réalisation FLOW ; leur qualification reste **À confirmer** par les premières réalisations et par une consultation fournisseur.

### Budget retenu hors options

**32 100 JH × 750 €/JH = 24 075 000 € HT**, soit **24,1 M€ HT**. Le dossier présente cette valeur de référence sous les hypothèses décrites, sans estimation basse/haute ni probabilité attachée. Le passage d'une mise en service à plusieurs livraisons constitue une option séparée.

## Prix d'un dispositif de développement sur mesure

Le prix FLOW correspond à une équipe de développement sur mesure, comprenant architecture, développement, données, qualification et pilotage. La composition diffère de celle d'une équipe d'intégration de progiciel. Les prix SAP et Microsoft sont justifiés séparément dans la [note de comparaison](15-rapprochement-buy-france.md).

L'abaque de prix ci-dessous est une **hypothèse de composition d'équipe autonome en France**, non une ventilation constatée des JH FLOW. Les taux sont situés à partir des baromètres français primaires [Malt Java 2026](https://www.malt.fr/t/barometre-tarifs/tech/developpeur-backend/developpeur-java), [Malt chefs de projet 2026](https://www.malt.fr/t/barometre-tarifs/gestion-de-projets-coaching/chef-de-projet), [Silkhom TJM 2025](https://www.silkhom.com/barometre-des-tjm-informatique-electronique-digital/) et [Freeland 2026](https://barometre.freeland.com/tjm). Malt observe notamment **579 €/jour** en France pour les développeurs Java expérimentés ; Silkhom situe un lead Java à **600–700 €/jour à Paris**, et Freeland affiche **650 €/jour** de médiane française pour les architectes, avec des profils plus chers selon leur responsabilité. Ces baromètres décrivent surtout des tarifs **de freelances affichés ou observés**, pas un prix signé pour une équipe au forfait.

| Fonction dans l'équipe externe | Part des JH, hypothèse | Taux de référence €/JH, hypothèse | Contribution au taux pondéré |
| --- | ---: | ---: | ---: |
| Ingénieurs de développement Java, front et intégration logicielle | 45 % | 580 | 261,0 € |
| Lead developers | 15 % | 650 | 97,5 € |
| Architectes logiciel, données et décisions de plateforme | 12 % | 800 | 96,0 € |
| PO, analystes métier et pilotage de livraison | 10 % | 650 | 65,0 € |
| Ingénieurs QA et automatisation des tests | 8 % | 475 | 38,0 € |
| DevOps, sécurité, data et performance | 10 % | 680 | 68,0 € |
| **Moyenne pondérée des profils** | **100 %** | — | **625,5 €/JH** |

Les **37 % de lead, architecture et spécialités plateforme** de cet abaque rendent visible la part technologique plus forte d'un produit construit sur mesure. Les **JH Make** utilisés au calcul comprennent déjà le développement du moteur de configuration, la plateforme technique, l'architecture du stock, les interfaces et la qualification ; on ne rajoute donc pas un deuxième poste « architecture » aux JH.

Pour estimer le prix vendu d'une **équipe fournisseur autonome**, le calcul ajoute **20 % de frais de structure, gestion et marge commerciale** : `625,5 × 1,20 = 750,6 €/JH`, arrondis à **750 €/JH**. **Hypothèse de l'étude :** les 20 % ne viennent pas d'un baromètre ni d'une offre reçue. Ils ne constituent pas une réserve de risque. **À confirmer :** un prestataire devra proposer un prix pour l'équipe et les responsabilités décrites ; la marge réelle et la répartition des métiers pourront différer.

## Résultat

`32 100 JH × 750 €/JH = 24 075 000 € HT`, soit **24,1 M€ HT de budget de référence** pour les postes identifiés de construction et d'intégration initiale FLOW Make, **sous les hypothèses ci-dessus**. L'option Storeland de `15 % × 24 075 000 € = 3 611 250 € HT` est affichée séparément dans le classeur.

Ce montant de prestations reste un **ordre de grandeur sous hypothèses**, avant consultation au forfait. Il ne compte pas le développement Storeland inconnu, le support, la coexistence, les coûts récurrents ni le travail interne. La livraison en une fois réduit l'enveloppe de déploiement, sans démontrer qu'elle réduit la difficulté de la bascule. L'ordre de grandeur de **24,1 M€ HT** est un point de départ pour juger une offre fournisseur répondant au périmètre écrit.

Les calculs remplacés sont conservés dans l'[archive de méthode](archives/methodes-remplacees/2026-10-20/11-cout-nominal-minimum.md). Ils ne servent pas de référence de prix pour la version actuelle.

Le calcul repose principalement sur **trois paramètres visibles** : les charges retenues par poste, les **1 000 JH** choisis pour la mise en service unique et le prix complet moyen de **750 €/JH** issu d'une composition d'équipe et d'une hypothèse de frais fournisseur. Les modifier actualise le budget de référence.

### Factures techniques pendant la construction

Le forfait de **24,075 M€** finance les prestations de réalisation. Les factures cloud propres à la construction sont ajoutées séparément : **24 k€ en année 1, 36 k€ en année 2, 76 k€ en année 3, 94 k€ en année 4 et 156 k€ en année 5**, soit **386 k€** sur cinq ans.

Le calcul retient de deux à six environnements allégés, une capacité mensuelle croissante et des campagnes temporaires de charge. Les consommations s'arrêtent à la livraison et laissent place au panier de production. Il s'agit d'une **hypothèse de consommation** ; ce supplément ne rémunère pas une seconde fois les 3 000 JH de plateforme et qualification. Les outils de travail génériques du fournisseur restent dans son forfait.

La charge et son tarif restent donc lisibles à part des ressources techniques achetées. Les totaux par horizon sont calculés dans le classeur et présentés dans la [note de décision](04-resultats-etude.md).

### Après la première version du Core

Le [modèle de fonctionnement](12-modele-tco-buy-make.md) repose sur **Service annuel**, qui regroupe les quantités et charges unitaires de maintenance, d'exploitation et d'évolution. FLOW retient **726 JH/an de maintenance et d'exploitation à 750 €/JH, soit 544,5 k€**, **320 JH d'évolutions, soit 240 k€**, et **400 k€ de ressources techniques** : **1,1845 M€/an après livraison**, hors options.

Le maintien en version courante du Core est financé : **96 JH techniques et 120 JH fonctionnels**, soit **162 k€/an**. Ces coûts sont compris dans les enveloppes précédentes. Les 120 JH fonctionnels figurent comme un « dont » du total comparable des évolutions.

FLOW et Microsoft conservent 240 diagnostics/an estimés, en plus de la prévention, en heures ouvrées. Les volumes SAP ne sont pas connus ; les forfaits fournisseur restent la base. Voir les [abaques](09-abaques-repartition.md).

Astreinte FLOW et migrations majeures restent des options désactivées. Le monitoring SAP en horaires étendus reste financé dans le forfait de 450 k€ ; ce libellé ne prouve pas une couverture 24/7. FLOW et Microsoft sont estimés en heures ouvrées. Les prestations ne sont pas présentées comme contractuellement équivalentes.