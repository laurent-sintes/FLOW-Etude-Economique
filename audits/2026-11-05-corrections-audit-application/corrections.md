# Corrections de l’audit de l’application FLOW

Date : 5 novembre 2026. Modèle n° 18. Référence de l’audit initial : commit `519b5da4dd43b0d98d26c64188b0a5f8bdd3770b`.

Les neuf points de l’audit sont corrigés dans le modèle et l’application. **Les huit scénarios financiers témoins sont identiques avant et après les corrections.** Quinze fichiers propriétaires des charges, coûts, ventilations et capacités sont conservés octet pour octet, capture native comprise. Les résultats attendus, critères, quantités et autres informations absentes restent à renseigner.

**La validation locale complète reste en échec sur le contrôle de fraîcheur de la cartographie externe.** Ce garde-fou est conservé. Les assertions de l’application qui échouaient ont été corrigées et leurs reprises sont réussies. Il ne faut donc pas présenter ce bilan comme une nouvelle exécution complète entièrement verte.

## Les neuf corrections

| Point | Sujet | Résultat |
| --- | --- | --- |
| A01 | Contrats de validation et chargement | Assertions obsolètes adaptées à la lecture détaillée versionnée. Les 48 adresses sont couvertes. Le budget initial reste inférieur aux seuils existants. |
| A02 | Statut des JH d’intégration | Le total historique et ses sous-totaux indiquent que l’étude est à reprendre. Les jours restent exclus de la ventilation retenue. |
| A03 | Périmètre Make et Buy | Les fiches Microsoft et SAP affichent leur contexte Buy et leur limite de ventilation. Les matrices et les travaux chiffrés Make ne sont plus affichés dans ces fiches. |
| A04 | Inconnu et sans objet | Le moteur expose l’applicabilité des composants selon les rôles et la nature documentée. Une enveloppe non ventilée garde ses composantes inconnues. Une décomposition connue n’est pas présentée comme restant à renseigner. |
| A05 | Livrable et activités | Les commentaires et activités incluses sont séparés du résultat réceptionnable. Un livrable absent est null, signalé dans le contrat et visible dans les informations à compléter. |
| A06 | Notation des interactions | Les deux vues réutilisent TeamInteractionMap, les trois modes du livre et les couches d’architecture, sans flèche ni filtre. Le graphe du métamodèle conserve ses relations dirigées et leurs cardinalités. |
| A07 | Exploration des consolidations | Une cellule ouvre les contributions de son équipe et de sa phase. Les filtres, les liens, les retours navigateur et les lectures de travail conservent le contexte. Le détail mobile présente les libellés et montants sur toute la largeur. |
| A08 | Accès clavier | Aller au contenu est la première destination au clavier. Son activation place le focus dans le contenu, sans modifier la route. |
| A09 | Lisibilité | Les petits textes concernés respectent un plancher de 11 px. Les six vues du contrôle typographique passent sur ordinateur et mobile. |

## Contrat du modèle et fidélité des chiffres

Le contrat distingue un livrable réceptionnable des activités incluses et des justifications de l’estimation. Les listes historiques du Core sont conservées dans leur rubrique de justification. Elles ne complètent plus implicitement le livrable.

L’applicabilité de chaque composant de coût provient du moteur Python et des informations documentées, sans calcul financier parallèle dans React. Le total connu d’une enveloppe ne rend pas ses parts humaines et ses frais sans objet. Lorsque la décomposition est déjà établie, son absence de part non classée est signalée comme sans objet. Les exemples sont conservés dans [les composants de coût](preuves/composants-couts.json).

Les [preuves de parité](preuves/parite-chiffrages.json) couvrent les six scénarios et les deux cas limites antérieurs. Elles contiennent aussi les empreintes des quinze sources inchangées. Les mesures de référence, tarifs et ventilations ne sont pas remplacés par les propositions de travail.

## Écrans vérifiés

Les 48 adresses sont visitées dans deux formats, soit 96 affichages. La régression finale couvre aussi les trois phases et les trois options, les sources, les documents originaux, les sauvegardes, le clavier et le moteur Python du navigateur. Aucune erreur JavaScript, requête métier HTTP ou erreur HTTP n’est relevée par cette régression.

Les sélections équipe et phase survivent aux retours arrière et avant et au passage entre référence et chiffrage de travail. La variante régionale conserve son organisation valorisée lors du chargement différé. Le métamodèle garde ses 70 objets, ses 111 relations, ses sept domaines et son lineage.

Les consolidations initiales mesurent environ 1 882 px pour les charges et 1 929 px pour les coûts sur ordinateur, contre 12 821 et 14 992 px dans l’audit. Le détail s’ouvre à la demande. La [capture mobile](preuves/detail-equipe-mobile.png) montre les montants avec leurs libellés, sans les repousser à droite dans un tableau comprimé.

Le bootstrap passe d’environ 2,45 Mo à **966,324 octets**, soit environ 0.97 Mo. Sa compression représente 227,614 octets. Les limites de 1 200 000 octets bruts et 280 000 octets compressés sont conservées. Les données d’organisation et du graphe sont servies à l’ouverture par une ressource statique versionnée et mise en cache.

## Résultats des tests

| Vérification | Résultat |
| --- | --- |
| Exécution complète initiale | 571 tests Python exécutés. Quatre assertions de transport à adapter et un écart de source externe ont été relevés |
| Reprise sur la version finale | 135 tests Python réussis, dont les quatre assertions adaptées et le nouveau cas d’applicabilité des composants |
| Couverture des cas dédupliqués | 572 cas couverts entre les deux passages. 571 sont réussis, un contrôle externe reste en échec |
| JavaScript | 90 tests réussis |
| TypeScript et règles éditoriales | Réussis |
| Navigateur final | Réussi sur ordinateur et mobile, avec les neuf régressions et le détail mobile |
| Scénarios financiers et moteur du navigateur | Huit cas conformes |
| Sources de référence protégées | Quinze fichiers identiques à la référence Git |

La [suite initiale](preuves/validation-complete-initiale.json), la [reprise ciblée](preuves/validation-ciblee-finale.json) et la [régression navigateur](preuves/navigateur-final.json) sont distinctes. Le cumul dédupliqué ne masque ni l’échec initial ni l’absence d’une seconde suite complète verte. Le [bilan structuré](verification.json) donne les identifiants des tests et le contrôle restant.

## Écart de la cartographie externe

Le contrôle `test_complexity_grid.GridTests.test_live_capture_when_external_source_is_available` constate que le fichier natif vivant ne correspond plus à l’empreinte enregistrée lors de la capture. **29 objets capturés diffèrent du fichier vivant** au moment de la comparaison.

La source externe a été modifiée le 2026-11-05T14:45:50.445132+00:00. Elle appartient au projet de cartographie distinct. L’étude continue de lire sa capture figée, dont le contenu et l’empreinte restent inchangés. Aucune recapture, reprise de ces évolutions ou recalibration de charges n’a été effectuée. Le test de fraîcheur et le rejet d’une source modifiée sont conservés. Les [empreintes et identifiants concernés](preuves/ecart-cartographie-externe.json) permettent une revue séparée.
