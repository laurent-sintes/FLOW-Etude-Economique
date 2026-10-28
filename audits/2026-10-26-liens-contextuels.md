# Audit des liens de lecture — 26 octobre 2026

## Conclusion

Le parcours entre les neuf pages est relié. En revanche, les liens **dans les explications** ne couvrent pas encore toutes les questions du sponsor. Le glossaire était surtout accessible depuis le menu et les « Notions utiles » du parcours Synvance. Une définition présente dans la base ne signifie donc pas qu’elle est accessible au moment où le lecteur rencontre son terme.

Le correctif demandé pour Supply Chain Management est appliqué. L’audit général ci-dessous distingue ce qui fonctionne des liens restant à ajouter ; il ne prétend pas que tout le maillage est désormais complet.

## Périmètre et méthode

Relecture des neuf pages, des sections détaillées, de leurs composants React, du menu et des transitions YAML ; inventaire des renvois explicites et des définitions. Contrôle des destinations du parcours et des identifiants de notions. Les liens Internet documentaires ne font pas l’objet d’un contrôle réseau exhaustif : cet audit porte sur le maillage interne de l’application, pas sur la disponibilité de tous les sites tiers.

Avant correction : 61 notions dans le glossaire, dont 16 référencées par les séquences Synvance. SCM ne disposait d’aucune entrée dédiée. Après correction : 62 notions. Les neuf transitions de bas de page renvoient vers une destination du menu. Les liens directs existants vers les sections `decision`, `architecture`, `work`, `rates` et `enveloppe` correspondent aux sections actives. Les liens vers architecture et tarifs depuis Estimations conservent la stack.

## Correction appliquée : Supply Chain Management

- Ajout de la notion canonique, définition courte et sens dans FLOW, avec source dans la capture de Cartographie Beaumanoir. Recherche possible par SCM et par le nom développé.
- Dans les textes de lecture pris en charge, le sigle métier devient Supply Chain Management et renvoie à sa fiche. Une infobulle donne la définition au survol ou au focus ; Échap la ferme. Son placement tient compte des bords de la fenêtre.
- Les boutons existants développent le sigle sans contenir un second lien imbriqué ; leur détail donne accès à la notion. Le nom officiel Dynamics 365 Supply Chain Management reste un nom de produit, sans lien trompeur vers le domaine métier.
- Les textes des pièces sources, identifiants, chemins et synonymes historiques sont préservés. Les libellés et définitions viennent du YAML ; les valeurs économiques restent inchangées.

## Diagnostic par page

| Page | Liens utiles déjà présents | Manques à traiter |
|---|---|---|
| Synthèse sponsor | Simulation, comparaison hors coûts, passage des offres Buy aux budgets ; Supply Chain Management désormais expliqué. | Donner accès aux définitions de Core System, Make/Buy, années de service complet et reste à financer au voisinage de leur première lecture. |
| Périmètre et options | Détails des frontières, preuves, architecture ; lien de la grille de complexité vers les charges. | Relier OMS/DOM/ATP, PaaS/iPaaS et responsabilités Core/Intégration à leurs définitions. Créer les définitions manquantes de capacité et Business Area à partir de la cartographie. Prévoir un passage vers les charges de la capacité consultée, pas seulement la page entière. |
| Offres Synvance | 16 notions contextuelles, six étapes, pièces localisées, lien final vers Marché. | Ajouter Supply Chain Management aux notions de la demande quand utile. Relier les compléments à la couverture fonctionnelle et le Run & MCO au détail annuel, au moment où ces sujets sont expliqués. |
| Références de marché | Fiches des projets, sources originales, tarifs par profil ; passage final vers Estimations. | Relier TJM, JH, ESN et prix normalisé au glossaire. Depuis les tarifs, proposer le détail des charges qui les utilisent ; depuis les repères d’intégration, proposer directement l’explication du budget Make. |
| Estimations | Tarifs et architecture avec stack conservée, passage Buy, méthode ; charges détaillées par capacité. | Relier JH, gains de productivité, ancre, provision, pleine capacité et Run & MCO à une définition courte. Ajouter le retour d’une capacité chiffrée à sa définition métier et à ses niveaux de complexité. |
| Mes hypothèses | Sources des paramètres, navigation commune, liste des modifications et transition vers les résultats. | Depuis une explication de paramètre, donner accès à la notion puis à la section d’estimation correspondante, en conservant le scénario. |
| Comparer les résultats | Hypothèses, dépenses annuelles, trois postes et horizons. | Expliquer au point de lecture « années de service », « reste à financer » et « écart à la référence » par des liens ciblés. |
| Dépenses annuelles | Détails par poste, conventions et retour à la synthèse distinguant référence et simulation. | Relier les postes aux hypothèses correspondantes et aux définitions des dépenses initiales et annuelles. |
| Glossaire | Familles, recherche avec anciens noms, URL par notion, sources et retour à la synthèse. | Ajouter, pour les notions majeures, un « Voir dans l’étude » menant à leur usage principal. Le menu seul ne remplace pas ce retour contextuel. |

## Défauts de navigation documentaire

**Priorité haute : les ancres ne sont pas réellement suivies dans le lecteur intégré.** `SourceLink` transmet un chemin et son fragment, mais `DocumentViewer` n’effectue pas de défilement vers le paragraphe après chargement. Les liens Markdown commençant par `#` sont même rendus comme du texte. Un renvoi tel que `source/calibration-couts.yaml#ia` ouvre donc la source, sans garantir l’arrivée à l’hypothèse annoncée. Recommandation : gérer les ancres Markdown et les chemins YAML de manière distincte, ou renvoyer vers une section de lecture dédiée si le format ne permet pas une localisation fiable.

**Priorité moyenne : les routes inconnues échouent silencieusement.** Une page inconnue retombe sur la vue initiale ; une notion inconnue produit une recherche sans résultat. Aucun des liens éditoriaux inspectés n’a présenté ce défaut, mais ce comportement masque une future faute de frappe. Ajouter un contrôle systématique des routes, sections et notions déclarées, plus un message explicite pour les liens importés ou anciens devenus invalides.

## Ordre de mise en œuvre proposé

1. Réparer la localisation dans les sources et créer les notions métier manquantes.
2. Relier les premières occurrences utiles des notions de décision et de coût : Core/Intégration, Make/Buy, Run & MCO, JH/TJM, ancre et années de service.
3. Compléter les renvois croisés entre capacité, complexité, charges et paramètres, en transportant l’identifiant de capacité ou la stack.
4. Ajouter les retours « Voir dans l’étude » depuis les définitions principales.

Ne pas transformer chaque occurrence en lien : privilégier la première explication utile, un en-tête de tableau ou un détail contextuel. Éviter les liens dans les boutons, les liens vers une fiche déjà ouverte et les renvois répétés qui domineraient le contenu. Tous les renvois doivent identifier une destination précise et rester dans le YAML.

## Validation

Compilation TypeScript et contrôle d’absence de contenu métier en dur exécutés. Le générateur du glossaire Markdown reprend la nouvelle notion. Les empreintes des résultats calculés sont actualisées après les changements explicatifs ; les options économiques, comparaisons et annuités sont strictement identiques avant et après. Le contrôle visuel du lien, du retour navigateur et de l’infobulle est consigné après vérification.


Vérifications finales : build réussi ; les deux tests existants des notions/pièces Synvance et de la continuité des pages passent. Dans le navigateur : nom développé dans la synthèse, définition au focus, fermeture par Échap, activation du lien par Entrée, fiche canonique ouverte, retour navigateur à la synthèse ; distinction avec le produit Microsoft dans la matrice ; infobulle visible dans un panneau modal, placée sous le lien lorsqu’il est près du haut de la fenêtre. Capture : `tmp/study-app/supply-chain-management-tooltip.png`. Le serveur local a été relancé.
