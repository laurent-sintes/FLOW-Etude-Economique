# Parcours visuel sponsor — mise en œuvre du 27 octobre 2026

Le parcours validé remplace les longues lectures obligatoires par deux entrées Comprendre et trois entrées Estimer. La cartographie native devient le support commun du périmètre et du build. Les tableaux, pièces et méthodes restent accessibles à la demande.

[Aperçu de la version livrée](2026-10-27-parcours-visuel.png), capturé dans l'application locale après les vérifications.

## Contenu livré

| Entrée | Lecture principale | Approfondissement |
|---|---|---|
| Logique de comparaison | Carte métier, Make / Buy, Core System / plateforme technique, trois natures de coût | Responsabilités et dossier Synvance |
| Périmètres comparés | Même carte pour FLOW, Microsoft et SAP ; Finance, OMS, réassort et stocks magasin | Capacité, fonctions, hypothèses produit, points ciblés et pièces localisées |
| Build Core System | Trois stacks côte à côte ; JH bruts, coût attribué et complexité par axe sur la carte | Architecture, travaux par capacité, réemplois, valorisation et sources |
| Intégrer et exploiter | Cinq options, intégration initiale et Run & MCO annuel sur deux échelles distinctes | Construction des budgets, activités, achats et 43 situations d'intégration |
| Confronter au marché | Assiettes et hypothèses expliquant les écarts ; divergence documentaire SAP | Quinze projets documentés et tarifs de prestation |

Les contenus sont dans `source/parcours-sponsor.yaml` et `source/atlas-sponsor.yaml`. `tools/sponsor_reading.py` les joint aux données existantes. Les sommes présentées sont des projections des affectations financées et des résultats publiés, sans nouvelle formule de coût. Le transverse et le pilotage restent distincts ; les forfaits Buy ne sont pas distribués aux capacités. La carte conserve les identifiants et les partitions des neuf sous-domaines, 28 Business Areas et 88 capacités.

`SponsorJourney.tsx` et `BusinessAtlas.tsx` consomment ces projections et les unités communes. La carte est une grille interactive en HTML/CSS utilisant les identifiants natifs ; les blocs ont des dimensions stables, indépendantes de leur prix. Les détails d'une capacité restent reliés aux fonctions, preuves et situations existantes. La recherche d'un identifiant exact est prioritaire ; une recherche libre conserve la correspondance par mots.

## Conservation et contrôles

- **41 tests application / fond métier** : 40 passent dans le bac à sable ; le test HTTP local, bloqué par la restriction Windows des sockets, passe ensuite avec l'accès localhost autorisé. Le contrôle de parité compare tous les résultats de référence, les annuités, les quatre horizons, les 2 312 valeurs économiques et cinq sensibilités au témoin `archives/fond-metier-2026-10-27/reference.json`. Contrat de reprise des simulations inchangé.
- **7 tests du nouvel adaptateur** : partition des identifiants, rapprochement des JH et coûts aux capacités puis aux domaines, transverse et pilotage, cinq bases annuelles, axes de complexité distincts, mise à jour du propriétaire et de ses seuls ancêtres, sources et situations valides.
- **29 tests frontend** : routes historiques et nouvelles, paramètres de lecture, ancres explicites, formatage monétaire, reprise de session et scénarios sauvegardés/importés. Les liens historiques Estimations sont dirigés vers Build ou Intégrer et exploiter ; les offres Synvance restent disponibles comme lecture contextuelle.
- TypeScript, contrôle d'absence de texte métier autonome dans React et build Vite réussis. Les avertissements de taille du bundle et les directives Lucide ignorées restent non bloquants.
- Contrôle navigateur sur les cinq lectures, les trois pages Simuler, les quinze références, le détail de Finance SAP, le passage Replenishment vers ses charges et sa reprise après rechargement. Aucune erreur console relevée pendant ce contrôle.
- Vérification à la largeur normale et à **390 px** : carte et trois stacks lisibles ; cinq options accessibles dans une comparaison à défilement horizontal local ; première colonne fixe et opaque. Correction du contenant des libellés masqués pour supprimer un débordement de page. Axe de complexité nommé pour les technologies d'assistance ; ancres et retour de détail replacent le focus. Le mode étroit et les styles d'impression sont conservés.

Les textes et budgets proviennent du modèle courant. La distinction entre coût documenté, hypothèse et point à qualifier reste explicite. Aucun nouveau budget, périmètre ou taux n'est introduit. Aucun commit ni push effectué.

## Dépendances

- Données : `business_map`, grille de complexité, calibration métier, qualification Buy, parcours d'intégration, résultats du moteur et glossaire.
- Restitution : `config/application.yaml`, `App.tsx`, `SponsorJourney.tsx`, `BusinessAtlas.tsx`, `StudyReading.tsx`, `readerNavigation.ts` et styles associés.
- Contrôles : `tools/test_study_app.py`, `tools/test_business_map.py`, `tools/test_sponsor_reading.py` et les quatre scripts de tests frontend cités ci-dessus.

Ce document décrit la livraison et ses vérifications ; il ne constitue pas une source économique indépendante.
