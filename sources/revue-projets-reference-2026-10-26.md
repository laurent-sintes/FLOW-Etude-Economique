# Revue des projets : Build Core System, intégration, MCO & Run

Revue du 26 octobre 2026. Référence structurée : [registre des quinze cas](../source/references-couts-integration.yaml), blocs `utilite_flow` et `references[].lecture_flow`. Cette revue complète le [benchmark initial](benchmark-integration-2026-10-23.md), sans changer ses prix d’intégration ni calibrer le moteur FLOW.

## Conclusions retenues

- Les quinze cas déploient un progiciel. Le développement d’extensions client, parfois appelé « build », ne constitue pas un prix de réalisation d’une release générique Make. Le corpus ne calibre donc pas directement ce poste.
- Tous publient un montant de mise en œuvre, mais avec des périmètres et des niveaux de preuve différents. Forrester propose des modèles composites ; Halifax compare des options ; Velrada fournit des retours commerciaux ; les marchés publics distinguent estimations et contrats attribués.
- Onze cas documentent des coûts récurrents distincts du montant initial. AP-HP décrit des évolutions dans ses lots sans annuité séparée. MTC, Club Assist et Hinkler ne donnent pas de coût annuel isolé dans les pièces retenues.
- Les postes récurrents ne couvrent pas tous la même chose : licences seules, support partenaire, service applicatif géré ou ensemble cloud/exploitation. Les évolutions sont explicitement en supplément chez Halifax. Il n’existe donc pas de ratio universel MCO/intégration à appliquer à FLOW.

## Preuves approfondies

| Référence | Localisation primaire | Apport de la relecture |
|---|---|---|
| Forrester Finance & Operations 2018 | [PDF Microsoft](https://info.microsoft.com/rs/157-GQE-382/images/EN-CNTNT-eBook-Forrester-TEI-Microsoft-Dynamics-365-For-Finance-Operations.pdf), p. 35–36, H1/H2/H7 | Mises à jour externes, support partenaire et équipes internes séparés ; H2 est calculé sur des licences déjà majorées du risque. |
| Forrester Commerce 2020 | [Étude originale hébergée par Folio3](https://dynamics.folio3.com/wp-content/uploads/2025/05/the-total-economic-impact-of-microsoft-dynamics-365-commerce.pdf), p. 23–24, F8/Gt | Licences distinctes de l’entretien interne ; conserver la valeur F8 publiée, la formule imprimée de remise étant incohérente. |
| Forrester Supply Chain Management 2021 | [Étude originale hébergée par Sunrise](https://sunrise.co/wp-content/uploads/2023/08/Dynamics365SupplyChainManagementTEI_FINAL.pdf), p. 26–27, Gt/H9 | Abonnement, support Premier et partenaire distincts ; le total support/management comprend aussi l’ancien système. |
| Forrester Finance 2022 | [Étude originale hébergée par Folio3](https://dynamics.folio3.com/wp-content/uploads/2025/04/tei-microsoft-dynamics-365-finance.pdf), p. 19–20, Et/Ft | Support partenaire dégressif ; entretien interne séparé. |
| Forrester ERP 2026 | [Publication Forrester](https://tei.forrester.com/go/Microsoft/Dynamics365ERPforEnterprises/index.html), Subscription Fees, Gt | Abonnement annuel isolé ; pas de budget complet de MCO partenaire autonome. |
| AP-HP | [BOAMP 26-8999](https://www.boamp.fr/telechargements/FILES/PDF/2026/01/26-8999.pdf), lots 1–2 | Évolutions, recette et assistance sur 48 mois ; pas de forfait annuel séparé. |
| Southwark | [Attribution du lot éditeur](https://moderngov.southwark.gov.uk/documents/s124063/Report%20Gateway%202%20Contract%20Award%20Approval%20Replacement%20of%20the%20Enterprise%20Resource%20Planning%20System.pdf), p. 1 et §76–78 | Contrat SAP sur dix ans, support et archivage dans d’autres lots. |
| EWEB | [Contrat SAP](https://www.eweb.org/documents/board-meetings/2022/11-01-22/cc4_sap.pdf), p. 1–2 | Cloud, supervision, exploitation, tests et montées de version ; durée de 6,5 ans, distincte de l’intégration Deloitte. |
| Halifax — deux options | [Dossier du conseil](https://halifaxwater.ca/sites/default/files/2020-09/Board%20Meeting%20Package%20-%20September%2024%2C%202020_0.pdf), p. 58–61 du PDF, note KPMG p. 18–21 | Même besoin, services N1–N3/hébergement/sauvegarde définis. Évolutions payées en plus. Cinq années de licences, quatre de services après déploiement ; aucune annuité artificielle issue du TCO. |
| Velrada — trois clients | [Dossier G-Cloud 13](https://assets.applytosupply.digitalmarketplace.service.gov.uk/g-cloud-13/documents/715243/114078871087067-service-definition-document-2022-05-17-1420.pdf), p. 6, 7, 9 | J.T. Johnson : service applicatif annuel publié ; Club Assist et Hinkler : pas de forfait annuel dans les fiches. |

Les accès directs aux avis TfL et MTC renvoient HTTP 403 le 26 octobre. Leurs lectures antérieures sont conservées et ne sont pas présentées comme de nouvelles attributions vérifiées. Le repère TfL de maintenance et hébergement était déjà documenté dans `projet.exclus_du_prix` ; il est désormais visible comme observation distincte. Le dossier Halifax a été téléchargé depuis sa source primaire et ses tableaux ont été extraits ; il s’agit de deux options d’un même dossier, jamais de deux observations indépendantes.

## Appréciation de l’utilité

L’ancienne note affichée mesurait exclusivement la possibilité de chiffrer une transposition complète à FLOW. Son zéro signifiait « prix FLOW non reconstitué », et non « référence inutile ». Ce niveau strict et les critères statistiques restent inchangés.

L’utilité est désormais une appréciation éditoriale, motivée cas par cas : analogie éloignée, repère partiel ou repère métier proche. Le seuil de mise en avant est dans le YAML ; il ne rend aucun prix directement comparable à FLOW et ne change pas sa qualité de preuve. Les fonctions Supply Chain Management, les travaux identifiés et la répartition des responsabilités motivent les évaluations. La Finance seule, Commerce centré sur les caisses et MTC peu détaillé restent des analogies éloignées.

## Conservation et contrôles

Les quinze prix initiaux, conversions, plages SAP/Dynamics et valeurs nulles de transposition sont conservés. Les coûts complémentaires sont stockés séparément, avec devise, période, assiette, localisation et qualité de preuve. Aucun montant n’entre automatiquement dans les budgets ou la simulation FLOW.

Les contrôles couvrent les trois postes par référence, les sources liées, la présence d’une observation pour un coût récurrent chiffré, et l’indépendance entre utilité et prix FLOW. Le contrôle visuel porte sur la liste, les fiches de détail, le clavier et le retour à la lecture.

Contrôles exécutés : analyse des références, deux tests applicatifs ciblés, TypeScript, contrôle d’externalisation des textes et compilation Vite réussis. Dans le navigateur : quinze fiches, trois analogies grisées, montants annuels J.T. Johnson et Halifax, liens localisés, fermeture par Échap et retour du focus vérifiés ; aucune erreur console ni débordement horizontal à 1280 px. Les montants Velrada non normalisés restent lisibles en AUD. Aperçu : `tmp/study-app/references-trois-postes.png`.
