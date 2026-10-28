> **ARCHIVE — remplacée le 20 octobre 2026. Ne pas utiliser pour une décision budgétaire. Les estimations basse/haute de cette version ont été retirées du dossier courant. Consulter la note de décision dans le dossier principal.**

![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 19 octobre 2026

---

# FLOW — hypothèses du coût initial nominal

Le **coût initial nominal de FLOW est de 24,1 M€ HT** : **32 100 jours de travail à 750 €/jour**, pour construire le logiciel, l'intégrer au SI Beaumanoir et le mettre en service une seule fois. Le prestataire fournit une équipe autonome basée en France : ingénieurs, architectes, responsables techniques, analystes métier, testeurs et pilotage.

Le terme « nominal minimum » désigne ici le **calcul sans options ni réserve de risque**, sur les charges basses retenues pour les fonctions identifiées. Il ne constitue pas un minimum de marché observé. Les quantités de travail, la composition d'équipe et les frais fournisseur sont des **hypothèses de l'étude**. Cette annexe en conserve le calcul ; la [note de décision](04-resultats-etude.md) présente la comparaison financière.

## Frontière du calcul

| Inclus dans le forfait nominal | Exclu de ce calcul |
| --- | --- |
| Conception et développement FLOW Make, moteur de configuration, stock/promesse/commandes/optimisation, tests et qualification, documentation et pilotage fournisseur. | Valorisation des équipes internes Beaumanoir en support, expertise, validation ou gouvernance. Leur intervention reste nécessaire à la réalisation, mais n'est pas facturée dans ce poste. |
| Configuration/adaptation initiale, migration des données actives et branchement aux systèmes et à la sécurité du groupe. | Support et exploitation après mise en service, coexistence prolongée avec les anciens SI, hébergement de production et coûts récurrents. |
| Préparation, répétition et exécution **d'une mise en service unique**. | Vagues successives de déploiement, accompagnement additionnel associé à ces vagues. |
| Le périmètre opérationnel **identifié** de FLOW. | Les développements Storeland encore non découverts : **option de périmètre de 15 % du nominal** dans le classeur ; autres majorations et réserve d'exécution. |

## Charge fournisseur : 32 100 jours

Le [premier modèle de charge](06-premier-ordre-de-grandeur-effort.md) donne une borne basse de **33 100 JH identifiés**, dont **2 000 JH** pour « déploiement et accompagnement » sous une hypothèse de pilote puis de bascules. Pour la mise en service unique, on remplace provisoirement cette ligne par **1 000 JH** pour répétition, préparation, formation fournie, bascule et démarrage. Cette réduction de moitié est une **hypothèse d'ingénierie explicite**, non une économie observée ou un ratio de marché. Les autres bornes basses des postes sont conservées.

Le prestataire prend en charge **tous les travaux de réalisation chiffrés ici** avec une équipe autonome. Les JH antérieurs représentaient une équipe pluridisciplinaire, métier inclus : leur réinterprétation en jours de forfait fournisseur suppose que le prestataire porte l'analyse métier opérationnelle, le PO et la coordination nécessaires à la livraison. Les contributions internes de Beaumanoir ne sont **pas ajoutées** au prix. Ce transfert de responsabilité n'a pas fait l'objet d'une mesure de productivité distincte ; il est une condition du calcul.

| Calcul de charge | JH |
| --- | ---: |
| Borne basse identifiée du modèle existant | 33 100 |
| Retrait de l'ancien poste « déploiement et accompagnement » | –2 000 |
| Mise en service unique, hypothèse de travail | +1 000 |
| **Charge nominale minimale ajustée** | **32 100 JH** |
| Option Storeland non découverte : `32 100 × 15 %` | **4 815 JH**, hors nominal |

La charge de **32 100 JH** couvre les postes identifiés avec mise en service unique. Les fonctions Storeland non découvertes sont une option ; l'activer porterait la charge à **36 915 JH** avant les autres majorations. Les charges unitaires n'ont pas été étalonnées sur une réalisation FLOW ; leur qualification reste **À confirmer** par les premières réalisations et par une consultation fournisseur.

### Plage de coût initial hors options

La borne haute des mêmes postes de charge est de **63 600 JH**, dont **4 000 JH** de déploiement/accompagnement. Pour conserver la même hypothèse de mise en service unique, ce dernier poste est remplacé par **1 000 JH**, comme à la borne basse : **63 600 − 4 000 + 1 000 = 60 600 JH**.

| Valeur de travail | Charge avec mise en service unique | Coût à 750 €/JH, hors options |
| --- | ---: | ---: |
| **Nominal retenu = borne basse** | **32 100 JH** | **24 075 000 € HT** |
| Borne haute | 60 600 JH | 45 450 000 € HT |

La plage **24,1–45,5 M€ HT** traduit les bornes de charge des postes existants, au même tarif et avant options ou inflation. Le nominal reste à la borne basse ; il n'est pas présenté comme une médiane. Il s'agit d'une plage conditionnelle, sans probabilité ni réserve de risque additionnelle. Le passage d'une mise en service à plusieurs livraisons constitue une option séparée.

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

`32 100 JH × 750 €/JH = 24 075 000 € HT`, soit **environ 24 M€ HT de coût nominal minimum** pour les postes identifiés de construction et d'intégration initiale FLOW Make, **sous les hypothèses ci-dessus**. L'option Storeland de `15 % × 24 075 000 € = 3 611 250 € HT` est affichée séparément dans le classeur.

Ce montant n'est **pas** l'espérance, la médiane, le prix garanti d'un forfait ni le coût complet de possession. Il ne compte pas le développement Storeland inconnu, le support, la coexistence, les coûts récurrents ni le travail interne. La livraison en une fois réduit l'enveloppe nominale de déploiement, sans démontrer qu'elle réduit la difficulté de la bascule. Le prochain prix réellement opposable serait celui d'une offre fournisseur répondant au périmètre écrit ; l'ordre de grandeur de **24 M€ HT** est un point de départ pour juger cette offre.

Les calculs remplacés sont conservés dans l'[archive de méthode](archives/methodes-remplacees/2026-10-19/11-cout-nominal-minimum.md). Ils ne servent pas de référence de prix pour la version actuelle.

Le calcul ne requiert ni lotissement des marques ni autre liste de risques. Il repose principalement sur **trois paramètres visibles** : la borne basse de charge du Make, les **1 000 JH** choisis pour la mise en service unique et le prix complet moyen de **750 €/JH** issu d'un mix de métiers et d'une hypothèse de frais fournisseur. Si l'un change, le nominal minimum change proportionnellement ; aucune probabilité n'est attachée au résultat.

