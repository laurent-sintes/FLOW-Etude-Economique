# Revue du modèle et impacts applicatifs

Revue du 5 novembre 2026, à partir du modèle 16. Évolution à chiffres retenus constants.

## Critères de sortie

Une estimation renseignée doit produire le même détail par travail, équipe et phase. Les achats gardent leur périodicité et ne deviennent pas des JH. Les propositions hors périmètre confirmé ne participent pas au total. Une donnée inconnue ne devient ni zéro ni une complétude fictive. La projection conserve les centimes des sources après ventilation.

## Constats reproduits

- Des frais inconnus imputés à une équipe rendaient aussi incomplète la charge valorisée d’une autre équipe. Les motifs étaient attachés à toute l’unité, sans distinction de contribution ni de mesure.
- Une consommation mensuelle de 100 € sur six mois initiaux ne produisait aucun montant de phase. Le moteur n’acceptait les périodicités mensuelles et annuelles que dans le fonctionnement annuel.
- La projection à mi-période d’un achat de 1,01 € pouvait donner 0,51 € après partage entre deux équipes, au lieu des 0,50 € produits par le prorata de la source.
- Le reste à estimer d’une couverture n’avait pas de champ explicite.
- Le chiffrage de travail n’était pas propagé au catalogue, à son abaque ni aux fiches d’équipe. Les motifs de complétude n’étaient pas reliés aux travaux à renseigner.
- Les vues ciblées du graphe ne montraient pas tous les objets ajoutés pour la consolidation.

## Corrections du modèle

Les motifs sont portés par les contributions, puis agrégés séparément pour les JH source, bruts, valorisés, les coûts et leur projection. Les trous de périmètre et les reliquats restent visibles au niveau de la phase. Une dépense sans charge humaine est sans objet pour les JH.

La périodicité proposée est normalisée par le moteur Python sur la durée renseignée d’une phase initiale ou sur une année de fonctionnement. Une durée inconnue laisse le montant de phase inconnu. La projection prorate une mesure source ou un composant une seule fois, puis distribue le résultat par cumuls arrondis.

Une couverture exige la revue du reste de périmètre. Les travaux restants doivent appartenir au détail remplaçant. Une liste vide indique l’absence confirmée de reste. Une liste inconnue empêche la confirmation.

Le périmètre déclaré dans le contrat peut compléter les critères de réception d’une référence sans réestimer ses JH ou son prix. Les valeurs inconnues restent null.

Les lectures dérivées par travail et phase relient la sélection de version, la période effective, les règles, les contributions et les données manquantes. Les propositions en attente conservent leur aperçu hors du journal consolidé. Les déclarations de nature incompatibles avec des JH mesurés ou un mode de valorisation sont refusées.

## Mesure et prise en compte des impacts

| Écran | Impact | Traitement |
| --- | --- | --- |
| Charges par équipe | Un même état masquait la distinction charge, frais et période | État de la mesure lue, JH source et valorisés distingués, liste de travaux à compléter avec liens |
| Coûts par équipe | Dépendances de périmètre peu actionnables et projection sensible au partage | Même journal que le détail, projection conservée, reste de couverture visible |
| Catalogue des unités | Contributions proposées absentes du filtre et des montants | Lectures retenue et de travail, contributeurs et montants issus de la sélection effective |
| Contrat d’une unité | Version et traitement de périmètre choisis invisibles | Panneau de scénario, période effective, règles et motifs précis, achats sans faux JH |
| Abaque | Seules les règles de référence étaient visibles | Ventilations versionnées du scénario et règles effectives par travail |
| Fiche d’équipe | Matrices et périmètre restaient sur la référence | Choix de lecture propagé à la liste des travaux, aux matrices et aux liens de détail |
| Graphe du métamodèle | Vues ciblées incomplètes | Attributs enrichis et profils travaux, financement et équipes étendus aux objets de consolidation |
| Comparaison économique, hypothèses et phases retenues | Risque de propagation involontaire des propositions | Référence conservée, égalité des projections, simulations et variante régionale contrôlée |
| Export du modèle et livraison statique | Nouvelles propriétés à transporter | Même métamodèle canonique et lectures dérivées exportés, version lisible vérifiée |

## Données et limites

La revue ne renseigne ni quantités, ni tarifs, ni responsabilités, ni capacités disponibles sans source. Le périmètre exhaustif des phases, les ventilations manquantes et les dates non documentées restent à renseigner. La consolidation des équipes porte sur Java/Spring. Les enveloppes Buy gardent leurs lectures existantes sans ventilation inventée.

Les contrôles ciblés et les cas de navigateur vérifient le fonctionnement du contrat. Ils ne constituent pas une adoption des estimations de travail ni une validation du dimensionnement métier encore absent.
