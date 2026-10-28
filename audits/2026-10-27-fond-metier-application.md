# Application du fond de carte métier — 27 octobre 2026

## Résultat

La cartographie Beaumanoir fournit désormais les identités et la hiérarchie communes aux lectures de couverture, de points à qualifier, de complexité, de charges Make et de situations d’intégration. La migration conserve les 88 capacités, neuf sous-domaines et 28 Business Areas du périmètre SCM. Les fonctions proposées par l’étude restent distinctes des objets issus de la carte.

Les montants et les simulations sont conservés : le test de migration compare la référence complète, ses annuités, les horizons 3/5/7/10 ans et cinq variations de paramètres au témoin enregistré avant intervention. Il vérifie aussi l’égalité de toutes les valeurs numériques du résultat économique. Aucun changement de charge, tarif, durée, provision ou formule n’est introduit.

## Sources réconciliées

- `source/lecture-metier.yaml` référence les dix sujets de lecture par leurs identifiants, leurs ancrages métier et leurs domaines voisins. Il ne recopie ni la hiérarchie ni les montants. Son schéma et `tools/business_map.py` vérifient les identifiants et les empreintes des captures.
- `sources/cartographie-frontieres-2026-10-27.yaml` conserve les domaines voisins issus de la même révision Beaumanoir que la capture SCM. Les correspondances avec les sujets de l’étude sont proposées ; elles ne valent pas validation métier.
- La calibration passe en version 3. Ses 264 champs éditables redondants — scénarios, frontières et anciennes vérifications Buy — sont retirés. Les fonctions et frontières sont dérivées de la grille courante ; les charges et leurs affectations restent identiques.
- Les preuves techniques des revues Buy sont résolues dans le registre fusionné et validées. Les textes courants ne reprennent plus les anciennes provisions CSF devenues inactives ; leurs pièces historiques restent archivées.
- Le point « Réassort magasin et allocation SAP » inclut désormais Replenishment et Stock Redistribution dans son contexte de qualification. Ce rapprochement ne constate aucun manque produit et n’introduit aucun supplément. Les 178 revues, sept points ouverts aux coûts inconnus et zéro développement additionnel financé sont conservés. Deux revues passent de l’hypothèse standard à un point ciblé à qualifier.

## Modèle et financement

`tools/business_map.py` construit un index dérivé par capacité avec les fonctions, frontières, appréciations Buy, preuves résolues, travaux Make, sujets et situations associées. Les identités métier viennent de la capture ; les besoins proposés viennent de la grille ; les charges et les appréciations produit conservent leurs sources propres.

Le financement reste identifié par propriétaire de travaux et option. Les 36 modèles de charges réutilisés correspondent à 267 affectations Make distinctes : 88 capacités et un socle transverse, pour trois stacks. Les liens de réemploi identifient les bénéficiaires, sans recopier ni dédupliquer artificiellement les charges. Le contrôle somme les valorisations par stack et les rapproche des prestations de build au centime.

Les 43 situations d’intégration rejoignent les capacités par les correspondances existantes. Elles ne deviennent pas de nouvelles unités de calcul. Les services transverses et les domaines voisins ne créent aucune capacité SCM supplémentaire.

## Lectures et simulations

Le fond de carte métier présente trois lectures : couverture et responsabilités, points à qualifier, complexité. Elles partagent la hiérarchie, les filtres et le détail de capacité. Les charges restent dans Build Core System ; les liens aller-retour conservent la capacité, les filtres et la lecture. Les situations d’intégration ont une ancre dédiée. Les anciens liens vers la complexité, la couverture Buy et les charges restent reconnus.

Le détail sépare les fonctions attendues, les apports produit documentés, les limites d’adéquation, l’inclusion commerciale et le financement retenu. Un point ouvert ne devient ni une absence produit démontrée ni un montant nul.

Les scénarios nommés et exportés utilisent le format 2 avec le contrat sémantique. Un scénario compatible est revalidé par le serveur courant en conservant ses valeurs absolues. Les formats anciens sont repris seulement pour les versions explicitement reconnues compatibles, dont le témoin avant migration. Les imports incompatibles et les données locales illisibles sont préservés. La reprise automatique garde son contrat existant, inchangé, et reste silencieuse.

## Vérifications

- `tools/test_business_map.py` : six tests réussis, dont parité de la référence et des cinq sensibilités, contrat sémantique, identités, preuves, financement et rejet de références invalides.
- `tools/test_business_calibration.py` : seize tests réussis, dont validation des preuves Buy, ordre des capacités et cohérence des sources dérivées.
- `tools/test_study_app.py` : 35 tests réussis. Le contrôle HTTP, initialement empêché par la restriction réseau locale du bac à sable, a réussi lors de sa reprise autorisée.
- Tests navigateur hors interface : sauvegardes, reprise, navigation du fond métier et format monétaire réussis ; un cas complémentaire vérifie la priorité d’une ancre d’intégration sur la restauration de position.
- TypeScript, contrôle des contenus YAML/React et construction Vite réussis. Vite conserve ses avertissements de bibliothèque et de taille du bundle ; aucune erreur de construction.
- Vérification dans le navigateur local : recherche d’une capacité, couverture et preuves, points SAP, changement de lecture, aller-retour vers les charges, reprise d’un ancien lien, frontières Finance/produit et sujet technique. À 430 px, le détail reste lisible et la grille conserve son défilement horizontal local ; Échap ferme le détail et rend le focus à la commande d’origine.
- Contrôle après correction de navigation : l’ancre de situation reçoit le focus et apparaît en haut de la lecture. Le panneau de capacité possède un seul conteneur de défilement, avec la page immobilisée pendant son ouverture. La source locale s’ouvre depuis le détail ; aucune erreur JavaScript n’a été relevée pendant ce parcours.

Les sorties économiques dérivées `source/couts-15-ans.yaml` et `source/investissements-10-ans.yaml` ont été régénérées après validation de la parité. Les 2 312 valeurs numériques du fichier économique régénéré ont également été comparées au témoin : égalité intégrale.

## Limite structurelle conservée

Les anciens fichiers de chiffrage restent nécessaires à certains contrôles et aux services/prix fournisseurs de l’adaptateur. Les charges métier actives sont remplacées par la calibration courante avant restitution. Leur retrait complet demanderait une migration supplémentaire de ces dépendances ; les supprimer dans cette intervention aurait fragilisé la préservation des calculs. Ils ne redeviennent pas un référentiel métier de lecture.

## Traçabilité

- Audit et contre-revue : `audits/2026-10-27-fond-de-carte-metier.md`.
- Témoin et sources avant intervention : `archives/fond-metier-2026-10-27/` ; `reference.json` conserve les paramètres, résultats, contrat, version et empreintes.
- Règles de maintenance et registre des fichiers : `AGENTS.md`, section « Fond métier commun appliqué ».
- Routes et contrôles de l’application : `app/README.md`.

Ce rapport documente la mise en œuvre ; il ne constitue pas une nouvelle source métier ou économique. Aucun commit ni push n’a été réalisé.
