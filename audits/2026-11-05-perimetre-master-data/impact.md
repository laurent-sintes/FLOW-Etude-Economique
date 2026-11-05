# Impact du périmètre Master Data + Supply Chain Management

Le périmètre cible de Flow Core System réunit désormais les deux domaines. La carte, le positionnement applicatif d’Atlas, les définitions, le métamodèle et les écrans de l’étude économique reflètent cette instruction. Les domaines et leurs responsabilités restent distincts.

La capture native couvre 33 capacités Master Data et 83 capacités Supply Chain Management. Operational References conserve Reference Ingestion et ses trois comportements de provenance. Les cinq anciennes capacités locales de stewardship ne font plus partie de la cible. La capture des décisions financières antérieures reste intacte.

## Proposition de build, sans adoption

Estimation d’ingénierie par livrable, avec analyse, conception, développement, tests, QA, coordination et mise en service inclus. Aucun comptage nouveau de code, de points COSMIC ou de productivité observée n’est déclaré. Les comparaisons antérieures portent sur l’ancien périmètre.

| Ensemble | Charge proposée |
| --- | ---: |
| Réception des références côté Supply Chain Management | 400 JH |
| Services communs du Master Data | 1 940 JH |
| Adaptations aux familles de données | 730 JH |
| **Sous-total Master Data, nouveau domaine** | **2 670 JH** |
| **Total Master Data + Operational References** | **3 070 JH** |

Le lot cible remplace les **1 600 JH** et **1 040 450 € HT** du lot historique. Il ne s’ajoute pas intégralement à ce financement. Les neuf livrables historiques sont rapprochés des 26 livrables cibles dans la source versionnée.

Les 3 070 JH comprennent déjà les 400 JH d’Operational References. Les deux lots sont affichés séparément dans les écrans. La conception des modèles de lecture, des correspondances MDM et des règles d’actualisation est explicitement incluse dans OR02, sans nouveau supplément ni correction silencieuse de la donnée maître.

La valorisation reprend les proportions de rôles par ensemble et leurs tarifs sources actuels. Les JH sont répartis une fois par la règle existante d’apportionnement. L’outillage suit le paramètre existant de 8 € HT/JH. Le résultat proposé est **1 996 410 € HT**, soit **1 470 JH et 955 960 € HT supplémentaires**.

Les autres lots restent inchangés. Le build générique total proposé passe de **7 630 à 9 100 JH**, et de **4 944 790 à 5 900 750 € HT**. Ce résultat ne constitue pas un coût complet des trois phases. Il ne remplace aucune décision retenue et n’entre pas dans les scénarios financiers actuels.

## Impacts encore ouverts

- Intégration : SI producteurs et consommateurs, interfaces spécifiques, reprises, migration, rapprochement et nettoyage des données par famille.
- Fonctionnement : MCO du produit, évolutions des règles, remédiation, stewardship métier, exploitation et support.
- Équipes : responsabilités fonctionnelles et techniques, ventilation de la réception opérationnelle, capacité disponible et contributions aux services communs.
- Calendrier : dépendances de publication, chemin critique et disponibilité des équipes. Aucun nouveau délai n’est déduit de l’ancienne durée du lot.
- Buy : couverture réelle des nouvelles fonctions, droits d’usage, licences et services additionnels Microsoft / SAP. Les documents fonctionnels cités ne démontrent pas leur inclusion dans les offres reçues.
- Moyens techniques : volumes, stockage, flux, rapprochement, sauvegardes, environnements et niveaux de service.
- Trajectoire : coût complet des trois phases et position comparative à recalculer après dimensionnement des postes ouverts.

Ces données restent `null`, avec un statut à renseigner. Aucun supplément automatique n’est appliqué aux enveloppes d’intégration, aux prix Buy, au MCO ou au cloud.

## Écrans et cartes

L’étude économique propose une carte SVG téléchargeable, une exploration des deux domaines et une synthèse des impacts. Le détail des 26 livrables et de leur valorisation est accessible depuis l’unité de travail Master Data. Les pages rappellent que les montants retenus portent encore sur le périmètre antérieur. La fiche de l’équipe Master Data décrit son nouveau périmètre, sans inventer sa capacité.

Atlas place Master Data au-dessus de son consommateur Supply Chain Management, et propose un export SVG généré depuis la hiérarchie courante. Le produit cible Flow Core System référence les deux domaines en couverture prévue, sans réalisation installée présumée. U1172 conserve le verbatim et la portée de l’instruction. La nouvelle déclaration de livraison remplace explicitement les obligations de champs concernés, sans réécrire les anciennes preuves.

## Contrôles

- 94 tests Python ciblés réussis, TypeScript et contrôles éditoriaux réussis. Le contrôle de publication a été complété par l’enregistrement explicite des nouvelles sources.
- 20 tests JavaScript Atlas réussis, validation du modèle courant et du glossaire sans erreur, contrôles de code et builds réussis.
- 50 contrôles de placement Atlas, téléchargement SVG, décompte des capacités, échappement XML et absence de débordement des textes SVG vérifiés dans Chromium.
- Parcours Cartographie, Fondamentaux et unité de travail sur 1 440 et 390 px. Présence des avertissements de périmètre sur les trois phases, les équipes et le graphe du métamodèle.
- Huit scénarios antérieurs reproduits exactement dans Python et dans le moteur Python du navigateur, en tenant compte du nouvel identifiant technique du modèle. Les paramètres et tous les montants sont conservés.

Sources propriétaires : `source/revision-master-data.yaml`, `source/fondamentaux.yaml`, la capture native datée et les preuves d’adoption antérieures. Les inconnus sont déclarés avec leurs propriétaires dans la matrice d’impact. Le modèle lisible porte la version du 5 novembre 2026, numéro 19.

Aucun commit, push ou déploiement distant effectué.
