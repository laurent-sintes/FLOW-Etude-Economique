# Vue d’ensemble du Framework

La page `#vision`, « Comprendre l’étude en une page », ouvre désormais le Framework. Elle explique comment une étude d’opportunité peut produire des ordres de grandeur avant le cadrage détaillé des fonctionnalités applicatives.

Le récit part d’un besoin métier commun, présente Make et Buy en parallèle, puis les relie aux scénarios d’investissement. Il distingue les appuis Synvance, les observations de produits et de code open source, le diagnostic COCOMO II limité à ERPNext/Frappe/Insights et la méthode de justification des charges. Il explicite ensuite effort, gains, valorisation, calendrier et Build/Run. Les limites actuelles restent visibles, notamment l’absence de recalibration des charges actives par le skill.

Un encart placé dès l’ouverture souligne la précision apportée par l’utilisateur : les chiffres constituent une base de discussion adaptable au contexte par le paramétrage. Il conduit aux Paramètres du modèle et rappelle la conservation d’une référence commune pour comparer les scénarios.

## Mise en œuvre

- `source/vision-framework.yaml` est le propriétaire unique des textes et liens.
- `tools/framework_vision.py` valide le contrat, l’ordre des quatre étapes, le vocabulaire et les destinations actives ou documentaires.
- `FrameworkVisionPage.tsx` et `frameworkVision.css` présentent un parcours continu, sans accordéon, avec les repères visuels des autres pages.
- Navigation, manifeste et documentation sont actualisés. Les anciennes routes et l’accueil de l’étude restent compatibles.

## Vérification

- Suite complète : **220 tests Python**, contrôles JavaScript de reprise, types, contenus et compilation réussis.
- Parité : **six scénarios identiques**, avec `2026-10-28-vision-framework-parite.json`. Écart à dix ans nul pour les cinq options.
- Après la précision finale sur le paramétrage : quatre tests ciblés de contrat, isolation du snapshot et neutralité des simulations repassés ; types, contenus et build repassés.
- Vérification visuelle et clavier sur ordinateur (1440 px), tablette (768 px) et mobile (390 px) : aucun débordement horizontal, aucune zone à déplier, titres et gras rendus, liens de navigation fonctionnels, deux pièces consultables et retour de focus conservé. Aucun incident JavaScript. Animation désactivée avec la préférence de réduction des mouvements.
- Application locale actualisée : mode courant et `sources_current: true`.

Le rapport de rendu est dans `tmp/framework-vision-verification.json` et les captures dans `output/framework-vision-*.png`. Aucun chiffre économique, prix, paramètre personnel, stockage de simulation ou calcul financier n’a été modifié. Aucun instantané publié ni opération Git effectuée.
