# Audit des libellés de l’application — 28 octobre 2026

## Périmètre et résultat

Contrôle des six pages publiques, des textes de `config/application.yaml`, du glossaire, du rendu React et des contrôles de contenu. La release locale publiée est `eaeee16df614`. L’audit ne modifie ni le modèle économique ni la release.

Le libellé actif du poste Buy est bien **« Droits d’usage et services associés »**. Les titres des postes de la page Structure des coûts utilisent majoritairement les références `{{notion.*}}`. Le contrôle `node scripts/check-content.mjs` ne trouve aucun texte visible écrit directement dans les composants React (`issues: []`).

## Écarts et risques

### 1. Le contrôle des placeholders ne couvre pas la prose — priorité haute

`tools/content_model.py:31-42` refuse un libellé canonique recopié uniquement lorsque la chaîne entière lui est égale. Il ne voit pas le même libellé dans une phrase. C’est la faille qui a laissé passer l’ancien nom « Offres Microsoft/K3 et SAP » dans la note de la page Modèle avant la correction du jour. Des expressions comme « Core System », « Plateforme Flow » et « Programme Flow » sont encore recopiées dans plusieurs phrases de `essential` au lieu d’utiliser `{{notion.*}}`. Une modification future du glossaire ne les mettrait pas à jour.

**À faire :** étendre la validation aux expressions canoniques distinctives présentes dans une phrase, en excluant les usages techniques et les homonymes courants. Migrer d’abord les phrases concernées vers des placeholders. Ajouter un test de renommage d’une notion qui vérifie titres **et prose** de la page publique.

### 2. Une ancienne désignation reste dans le contenu public chargé — priorité moyenne

`config/application.yaml:1526` contient encore le titre « iPaaS et licences techniques » dans `essential.proofs.technical_purchases`. Aucun composant de la navigation actuelle ne l’affiche, mais ce bloc est transporté dans le bootstrap essentiel et peut réapparaître si une preuve est reliée à une page.

**À faire :** renommer ce titre en fonction de son périmètre réel, puis vérifier les références à cette preuve. Ne pas l’assimiler automatiquement au poste plus large « Socle technique et cloud ».

### 3. Des textes d’anciennes pages conservent les anciens noms — priorité moyenne

`config/application.yaml:277,303,581,615,640,855,886,890,908` contient notamment « Flow Core System » et « Run & MCO ». Ces pages ne figurent plus dans le menu public et les anciennes routes redirigent vers le nouveau parcours. Leurs textes restent chargés et constituent une réserve de termes périmés si une vue est réutilisée.

**À faire :** corriger ou retirer ces textes après revue des consommateurs de compatibilité. Garder les synonymes historiques dans `source/glossaire.yaml` pour la lecture des anciennes pièces ; ils ne sont pas des libellés d’interface.

### 4. Plusieurs titres identiques sont saisis deux fois — priorité moyenne

Dans `essential`, « Structure des coûts », « Paramètres du modèle », « Intégrer et déployer », « Exploiter et faire évoluer » et « Exploitation, support et outillage » sont répétés dans deux emplacements. Une retouche isolée peut désaligner menu, page, calendrier ou preuve.

**À faire :** donner un propriétaire à chaque nom de page et de phase, puis référencer ce nom depuis les autres emplacements lors de la fabrication du site. Les titres de postes économiques doivent continuer à provenir du glossaire.

### 5. Deux définitions du glossaire ont une formulation incorrecte — priorité basse

`source/glossaire.yaml:26` dit « du Plateforme Flow » et `:77` dit « de Plateforme Flow ». La forme correcte est « de la Plateforme Flow ». Ces définitions peuvent être montrées dans les bulles du glossaire.

**À faire :** corriger le YAML canonique, puis régénérer `source/glossaire.md`.

## Contrôles à conserver

- Garder `app/scripts/check-content.mjs` dans la suite de publication pour interdire les libellés JSX en dur.
- Garder la résolution stricte des `{{notion.*}}` : une référence absente doit faire échouer le chargement.
- Ajouter au contrôle de contenu un inventaire des libellés historiques apparaissant dans `essential`, sans traiter les synonymes du glossaire et les preuves originales comme des erreurs.
- Vérifier les libellés sur la release servie, car le brouillon YAML n’est pas automatiquement le contenu affiché par le serveur.

## Mise en œuvre du 28 octobre

- Les noms des pages **Se projeter**, **Structure des coûts** et **Paramètres du modèle** ont un propriétaire unique dans `source/glossaire.yaml#vues`. Les deux noms de phases répétés et **Exploitation, support et outillage** ont chacun une entrée canonique dans `notions`.
- Les phrases de `config/application.yaml` qui citaient directement les notions publiques distinctives utilisent maintenant `{{notion.*}}` ou `{{vue.*}}`, y compris dans les anciennes lectures encore chargées pour compatibilité. Les anciens noms restent uniquement dans les synonymes historiques et leurs correspondances de recherche.
- La preuve auparavant intitulée « iPaaS et licences techniques » est maintenant **Achats techniques séparés**, ce qui décrit son périmètre sans l’assimiler à tout le socle technique.
- Les deux formulations incorrectes du glossaire ont été corrigées et `source/glossaire.md` a été régénéré.
- `tools/content_model.py` contrôle désormais les noms publics distinctifs même au milieu d’une phrase et interdit les anciens libellés identifiés dans la configuration. Les tests vérifient les refus et la propagation d’un renommage jusque dans la prose.

Contrôles ciblés : `check_model --quick --preserve`, `check-content.mjs` et `render_glossary.py --check` réussis. La validation complète a passé **135 tests** et publié la release `9bd61c82b0b2`, avec un écart de coût nul à dix ans pour les cinq options. Le serveur local sur le port 8767 sert cette release ; son bootstrap essentiel contient les nouveaux libellés et aucun des anciens noms interdits.
