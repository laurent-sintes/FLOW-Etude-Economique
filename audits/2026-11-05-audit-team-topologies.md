# Audit de la présentation Team Topologies — 5 novembre 2026

> Mise à jour de présentation : à la demande de l’utilisateur, la notation du livre remplace ensuite les symboles numériques des interactions. Voir [la décision et sa vérification](2026-11-05-notation-livre-interactions.md). Les constats ci-dessous conservent la trace de l’audit initial.

## Conclusion

Le dossier employait « équipes produit » comme intitulé commun alors que le modèle distingue déjà 6 équipes Stream-aligned, 2 Platform, 2 Complicated-subsystem et 1 Enabling. Ce raccourci effaçait la différence entre propriété d’un périmètre logiciel et accompagnement temporaire. Les responsabilités, charges et financements existants ne sont pas réestimés par cet audit.

## Écarts constatés et corrections

| Constat dans l’application | Correction |
| --- | --- |
| « Équipes produit » comme intitulé universel | « Équipes et missions ». Le principe commun devient celui des équipes durables de delivery. La route historique reste compatible. |
| Assimilation de la stabilité d’Enabling à la propriété d’un produit sur trois phases | Équipe stable, interventions temporaires orientées vers l’autonomie. Le texte conserve les missions et les critères de sortie existants. |
| Couleurs approximatives, Enabling rouge | Couleurs relevées directement dans le XML diagrams.net du dépôt officiel. |
| Sous-systèmes dessinés comme des rectangles | Repère octogonal. Stream-aligned horizontal arrondi, Enabling vertical arrondi, plateforme rectangulaire pointillée. |
| Modes représentés par des flèches colorées | Formes distinctes du kit numérique : collaboration en parallélogramme, service en triangle vers le consommateur, facilitation en cercle. Opacité des formes à 50 %. |
| Schéma SVG figé avec lignes croisées et sans lecture du contrat | React Flow, positions stables, zoom, cadrage, filtres, sélection d’équipe et inspecteur de relation. Tableau textuel complet conservé. |
| Sélecteur natif isolé pour les fiches | Répertoire visible regroupé par type, sélection explicite et liens partageables. Filtres natifs regroupés, stylés et utilisables au clavier. |
| Accompagnement placé à droite des flux | Accompagnement et services à gauche. Les équipes Stream-aligned restent à droite. |
| Aucune attribution du kit | Attribution et lien CC BY-SA 4.0 visibles. Adaptations graphiques identifiées dans les fichiers concernés. |

## Conventions retenues

Référence : kit numérique officiel, distinct des illustrations historiques du livre. Les coordonnées et dimensions servent à organiser la lecture. Elles ne constituent pas une mesure de charge cognitive, d’effectifs ou de budget. Les relations sont des hypothèses de travail et non des appels logiciels ni une hiérarchie de commandement. La gouvernance reste hors typologie.

Palette extraite du fichier `diagrams.net/TeamTopologies.xml` : Stream-aligned `#FFEDB8`, Platform `#BBD2F6`, Complicated-subsystem `#FBDBBA`, Enabling `#C9DFBE`. Collaboration `#E3E0EE`, X-as-a-Service `#B4B4B4`, Facilitating `#E3EFDE`.

React Flow utilise du HTML pour les équipes et les marqueurs interactifs, et son moteur SVG pour tracer les liens. Le remplacement porte sur le diagramme artisanal et ses interactions, sans prétendre supprimer SVG de la pile de rendu.

## Points de fond à instruire

Ces points empêchent de considérer la cible comme une organisation Team Topologies validée.

- **Frontières des flux.** Les noms de plusieurs équipes désignent des composants ou des domaines. Décrire pour chaque Stream-aligned ses utilisateurs, le résultat attendu et son autonomie jusqu’à la production. Vérifier notamment les frontières de Portal et Master Data, sans reclasser automatiquement ces équipes.
- **Charge cognitive.** Les effectifs et capacités sont inconnus dans la source. Une équipe unique par nom de domaine ne démontre pas qu’elle peut porter ce périmètre. Évaluer complexité, compétences nécessaires, interruptions et dépendances avec les équipes concernées.
- **Deux sous-systèmes spécialisés.** Leurs types sont explicitement proposés et à éprouver. Vérifier que leur expertise justifie une équipe distincte plutôt qu’un découpage en silos de composants.
- **Plateformes.** Case Management et PaaS fournissent des mécanismes communs. Il reste à décrire leurs consommateurs, leur expérience de service, leur autonomie de consommation et leurs contrats. Une API partagée ne prouve pas cette qualité de service.
- **Enabling Intégration.** Les critères de sortie existent. Définir la fenêtre de chaque accompagnement et le propriétaire durable de chaque flux. Une dépendance permanente à cette équipe contredirait la mission déclarée.
- **Interactions dans le temps.** Les phases et critères de sortie sont documentés, mais les dates de début, les durées et les transitions de modes ne sont pas dimensionnées. Les contrats de collaboration et de facilitation sont des propositions à planifier.
- **Photo de la cible.** Le modèle présente une cible, pas un état actuel observé. La confrontation aux équipes existantes, à leurs compétences et à leurs interactions reste nécessaire avant constitution.

Aucune règle budgétaire, valeur de charge, affectation, capacité ou interaction n’est modifiée. Les identifiants et les routes sont conservés. Les modifications de sources sont éditoriales et graphiques, sans création d’objet métier ni nouvelle révision lisible.

## Références consultées

- [Kit officiel et principes de représentation](https://github.com/TeamTopologies/Team-Shape-Templates)
- [Fichier diagrams.net officiel utilisé pour les couleurs](https://raw.githubusercontent.com/TeamTopologies/Team-Shape-Templates/main/diagrams.net/TeamTopologies.xml)
- [Guide officiel de modélisation des interactions](https://teamtopologies.com/key-concepts-content/team-interaction-modeling-with-team-topologies)
- [Ressources et kits](https://teamtopologies.com/resources)
- [Licence du kit](https://github.com/TeamTopologies/Team-Shape-Templates/blob/main/LICENCE.md)

## Vérifications

- `tools.check_dev` sur les 16 fichiers du périmètre final : **69 tests Python réussis**, TypeScript, **86 tests JavaScript réussis** et contrôle éditorial. Durée totale **105,6 s**. Rapport conservé dans `tmp/validation/20261105T094557Z-7408550d`.
- Livraison statique reconstruite dans `app/dist`, sans publication ni commit. Export du modèle conservant la révision lisible du 5 novembre 2026, numéro 13.
- **30 vérifications Chromium réussies en 3,9 s** sur la livraison finale du port 8766. Elles couvrent les 11 équipes, les 29 interactions, le clic sur tous les marqueurs, les filtres et leur intersection, l’état vide, les positions stables, le zoom, le cadrage, la sélection au clavier, les fiches, les liens conservant le contexte et trois vues mobiles à 390 px sans débordement de page.
- Aucun défaut JavaScript observé dans ces parcours. Compte rendu : [contrôle navigateur](2026-11-05-team-topologies-browser.json).
- `git diff --check` réussi sur les fichiers suivis du périmètre. Les changements préexistants sont conservés.

Ces contrôles ciblés ne valent pas certification de l’organisation, du dimensionnement ni de l’ensemble du projet.
