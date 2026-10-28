> **ARCHIVE — version remplacée le 19 octobre 2026.** Les montants et conclusions de cette copie ne servent pas à la décision actuelle. Voir la [version courante](../../../11-cout-nominal-minimum.md).

![Logo eXalt](../../../assets/exalt-logo.png)

**Laurent Sintès** · 19 octobre 2026

---

# FLOW Make — coût nominal minimum du forfait autonome

**Hypothèses demandées le 19 octobre 2026.** Ce calcul répond à une question précise : combien coûterait **au minimum nominal** un dispositif externe autonome **basé et facturé en France**, chargé de construire FLOW et de le mettre en service **une seule fois** ? Il n'utilise aucune hypothèse d'offshore ou de nearshore. Il ne s'agit ni d'un devis ferme ni d'une nouvelle architecture. Le forfait comprend les capacités Build, la configuration initiale, les flux de données et le raccordement à la sécurité, avec ses propres ingénieurs, architectes, leads, PO/analystes, testeurs et pilotage.

## Frontière du calcul

| Inclus dans le forfait nominal | Exclu de ce calcul |
| --- | --- |
| Conception et développement FLOW Make, moteur de configuration, stock/promesse/commandes/optimisation, tests et qualification, documentation et pilotage fournisseur. | Valorisation des équipes internes Beaumanoir en support, expertise, validation ou gouvernance. Leur intervention reste nécessaire à la réalisation, mais n'est pas facturée dans ce poste. |
| Configuration/adaptation initiale, migration des données actives et branchement aux systèmes et à la sécurité du groupe. | Support et exploitation après mise en service, coexistence prolongée avec les anciens SI, hébergement de production et coûts récurrents. |
| Préparation, répétition et exécution **d'une mise en service unique**. | Vagues successives de déploiement, accompagnement additionnel associé à ces vagues. |
| Le périmètre opérationnel **identifié** de FLOW. | Les développements Storeland encore non découverts : **option de périmètre de 15 % du nominal** dans le classeur ; autres majorations et réserve d'exécution. |

## Charge fournisseur retenue pour le minimum

Le [premier modèle de charge](../../../06-premier-ordre-de-grandeur-effort.md) donne une borne basse de **33 100 JH identifiés**, dont **2 000 JH** pour « déploiement et accompagnement » sous une hypothèse de pilote puis de bascules. Pour la mise en service unique, on remplace provisoirement cette ligne par **1 000 JH** pour répétition, préparation, formation fournie, bascule et démarrage. Cette réduction de moitié est une **hypothèse d'ingénierie explicite**, non une économie observée ou un ratio de marché. Les autres bornes basses des postes sont conservées.

Le prestataire prend en charge **tous les travaux de réalisation chiffrés ici** avec une équipe autonome. Les JH antérieurs représentaient une équipe pluridisciplinaire, métier inclus : leur réinterprétation en jours de forfait fournisseur suppose que le prestataire porte l'analyse métier opérationnelle, le PO et la coordination nécessaires à la livraison. Les contributions internes de Beaumanoir ne sont **pas ajoutées** au prix. Ce transfert de responsabilité n'a pas fait l'objet d'une mesure de productivité distincte ; il est une condition du calcul.

| Calcul de charge | JH |
| --- | ---: |
| Borne basse identifiée du modèle existant | 33 100 |
| Retrait de l'ancien poste « déploiement et accompagnement » | –2 000 |
| Mise en service unique, hypothèse de travail | +1 000 |
| **Charge identifiée ajustée** | **32 100** |
| **Charge nominale minimale ajustée** | **32 100 JH** |
| Option Storeland non découverte : `32 100 × 15 %` | **4 815 JH**, hors nominal |

Le niveau de charge **32 100 JH** est la borne basse *conditionnelle* du travail fournisseur sur les postes identifiés, avec mise en service unique. Les fonctions Storeland non découvertes sont traitées séparément comme option ; les inclure porterait cette charge à **36 915 JH** avant les autres majorations. Ces valeurs ne signifient pas qu'un appel d'offres produira nécessairement un prix à ce niveau et conservent le caractère non calibré des charges unitaires.

## Prix d'un dispositif de développement sur mesure

Le prix moyen **919,56 €/JH** calculable dans l'offre **SAP/Delaware** correspond à l'intégration d'un **progiciel spécialisé**. Il ne doit **pas** servir de taux moyen au Make. FLOW sur mesure mobilise davantage de développement, d'architecture, de plateforme et de qualification, à des tarifs différents. La [proposition Buy analysée](../../../08-pont-charges-buy-make.md) reste un contrôle externe de programme, sans fournir le prix de FLOW Make.

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

Pour passer de ces repères de professionnels indépendants à un **dispositif fournisseur autonome**, le calcul pose **20 % de frais de structure, gestion du dispositif et marge commerciale** sur la moyenne pondérée : `625,5 × 1,20 = 750,6 €/JH`, arrondis à **750 €/JH**. Ce **20 % est une hypothèse de prix**, pas une statistique de marché vérifiée ni une réserve de risque. Le prix de forfait réel dépendra de l'offre d'un prestataire ; le taux de **750 €/JH** sert de référence de calcul pour l'ordre de grandeur demandé.

## Résultat

`32 100 JH × 750 €/JH = 24 075 000 € HT`, soit **environ 24 M€ HT de coût nominal minimum** pour les postes identifiés de construction et d'intégration initiale FLOW Make, **sous les hypothèses ci-dessus**. L'option Storeland de `15 % × 24 075 000 € = 3 611 250 € HT` est affichée séparément dans le classeur.

Ce montant n'est **pas** l'espérance, la médiane, le prix garanti d'un forfait ni le coût complet de possession. Il ne compte pas le développement Storeland inconnu, le support, la coexistence, les coûts récurrents ni le travail interne. La livraison en une fois réduit l'enveloppe nominale de déploiement, sans démontrer qu'elle réduit la difficulté de la bascule. Le prochain prix réellement opposable serait celui d'une offre fournisseur répondant au périmètre écrit ; l'ordre de grandeur de **24 M€ HT** est un point de départ pour juger cette offre.

L'ancienne simulation **35–75 M€** reposait sur un autre profil de moyens, d'autres coûts annuels et une réserve globale de 20 %. Elle n'est pas validée par le calcul présent. Le **35 M€** annoncé dans la version précédente du minimum nominal provenait de l'application erronée du taux SAP/Delaware de **920 €/JH** à tout le Make ; cette hypothèse de prix est **retirée**.

Le calcul ne requiert ni lotissement des marques ni autre liste de risques. Il repose principalement sur **trois paramètres visibles** : la borne basse de charge du Make, les **1 000 JH** choisis pour la mise en service unique et le prix complet moyen de **750 €/JH** issu d'un mix de métiers et d'une hypothèse de frais fournisseur. Si l'un change, le nominal minimum change proportionnellement ; aucune probabilité n'est attachée au résultat.
