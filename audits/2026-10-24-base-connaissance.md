# Audit de la base de connaissance — 24 octobre 2026

## Périmètre et principe

Audit des YAML et Markdown actifs qui justifient la comparaison FLOW / offres issues de la consultation Synvance. Les pièces originales sont préservées. L’Excel enregistré sert de témoin de rapprochement ; ses simulations locales ne sont pas réimportées comme hypothèses.

## Constats et corrections

| Constat | Conséquence | Correction |
|---|---|---|
| README principal encore centré sur l’ancienne étude et ses anciens budgets | Point d’entrée trompeur malgré un modèle YAML courant | Nouveau README sans budgets recopiés, renvoyant aux données de référence. |
| Notes numérotées et consignes successives mélangées avec la base active | Risque de réutiliser une convention remplacée | 21 notes déplacées dans une archive explicite, liens adaptés, reçu et sauvegarde. |
| Outils d’anciennes restitutions mélangés aux générateurs actifs | Leurs contenus et budgets en dur pouvaient être repris par erreur | 21 scripts historiques archivés, octets préservés et reçu distinct. |
| Aucun doublon exact parmi les 181 YAML/Markdown de l’inventaire initial | Une suppression par nom ou proximité de contenu aurait perdu de l’information | Préservation des sources et historiques ; suppression des reprises redondantes dans les guides actifs. |
| Explications métier et résumés de preuves présents dans le générateur | Connaissance moins visible et montants rappelés susceptibles de vieillir | 75 blocs transférés dans `source/explications-modele.yaml` ; rappels de budgets courants liés aux valeurs du modèle. |
| Libellés et contenus répartis dans le code | Variantes de noms selon les onglets et corrections difficiles à maintenir | Configuration externe, glossaire commun et contrôle syntaxique de non-régression. |
| Consignes héritées annonçant encore l’absence de chiffrage ou d’horizon | Contradiction avec le scénario actuel | Clarification d’AGENTS.md et du guide de la base. |
| Durée de valorisation, nombre d’annuités et catégorie d’indexation iPaaS partiellement repris dans le code | Une modification des YAML pouvait diverger de leur application | Lecture des durées et séquences existantes ; catégorie iPaaS structurée dans la calibration et consommée par les deux calculateurs, sans changement des règles retenues. |

## Organisation de référence

- [Base active](../source/README.md) : données, méthodes et explications.
- [Lecture des offres](../source/offres-synvance.md) : consultation, offre, projection et compléments estimés.
- [Glossaire lisible](../source/glossaire.md), généré depuis [le YAML de référence](../source/glossaire.yaml) : 52 notions avec noms, définitions, formes courtes autorisées et synonymes historiques ; noms communs pour cinq options et six onglets.
- [Configuration de présentation](../config/restitution-investissements.yaml) : libellés, contenus, formules de restitution, formats et charte ; aucune hypothèse économique autonome.
- `sources/` : preuves originales et registres documentaires.
- [Archives des notes remplacées](../archives/etude-avant-yaml-2026-10-24/README.md).

## Rapprochement avec l’Excel

Le contrôle [audit_knowledge_base.py](../tools/audit_knowledge_base.py) rattache chaque constante numérique aux champs du modèle et à leurs unités, y compris les années de Calculs. Il vérifie les dépenses annuelles des cinq options, tous les textes saisis, les formules et les infobulles. Une coïncidence de nombres dans des fichiers n’est pas considérée comme une preuve de traçabilité.

| Contrôle final | Résultat |
|---|---|
| Base active et configuration | 57 YAML/Markdown ; aucun doublon exact, lien local cassé ou encodage suspect détecté. |
| Valeurs saisies dans l’Excel témoin | 171 constantes numériques rattachées ; 194 liaisons explicites, comprenant aussi les vides attendus. |
| Autres rapprochements de cellules | 344 contrôles de valeurs et textes, dont 50 dépenses annuelles. |
| Textes saisis | 386 cellules couvertes ; 40 différences de libellés inventoriées et revues. |
| Formules | 795 correspondances ; seules les apostrophes facultatives autour des noms d’onglets sont normalisées. |
| Infobulles | 1 282 textes identiques après normalisation des espaces ; aucune information propre à une bulle ne reste seulement dans Excel. |
| Générateur actif | Aucun texte métier en dur détecté par le contrôle syntaxique ; six vues assemblées en mémoire, vingt montants de synthèse contrôlés, aucun export Excel. |
| Modèle | Huit commandes de validation et de synchronisation réussies, plus le contrôle JavaScript et l’analyse syntaxique PowerShell. |
| Préservation | Les 10 794 valeurs numériques des 46 YAML préexistants sont identiques à la sauvegarde ; empreinte du classeur identique au témoin. |

Les 40 différences concernent l’harmonisation des noms : Build Flow Core System, Intégration et migration Groupe Beaumanoir, PaaS/iPaaS, services et offre éditeur, gain de continuité, service complet et noms des options. Elles ne signalent pas de chiffres manquants. L’Excel enregistré reste inchangé ; le générateur appliquera ces références lors de la prochaine génération. Les variantes historiques restent dans le glossaire pour relire les anciens fichiers.

Les changements des YAML existants portent sur des chemins documentaires, les empreintes qui en dépendent, l’externalisation des descriptions des résultats et la représentation structurée d’une règle d’indexation déjà appliquée. Aucun TJM, prix, JH, taux ou résultat économique n’a été recalibré. Les trois renvois à l’ancienne analyse Synvance suivent son déplacement en archive ; ils conservent leur statut documentaire historique.

Les JSON détaillés (`controle.json`, `preservation.json`, `validations.json` et `references-deplacees.json`) sont produits sous `tmp/audit-base-connaissance-2026-10-24/`. Les différences de présentation sont inventoriées pour revue : elles ne valent pas autorisation automatique d’un nouveau contenu. Les contrôles informatiques ne démontrent pas la validité économique des JH, gains de productivité, provisions, prix indicatifs ou transpositions de périmètre.

## Limites économiques maintenues

L’ancre Make dérivée de SAP, le bonus de continuité et la durée conventionnelle restent non calibrés pour FLOW. Les compléments SAP peuvent recouvrir du Core déjà financé. La projection Microsoft après pilote est peu détaillée. Les offres groupées restent non ventilées sans preuve, et les inconnues ne valent pas zéro. Les références publiques n’apportent aucune borne FLOW à périmètre comparable démontré.

Les sources publiques n’ont pas fait l’objet d’une nouvelle campagne de recherche marché pendant ce nettoyage. Leurs références, dates et limites ont été conservées ; les pièces locales et leurs empreintes restent contrôlées.

## Reprise et restauration

Le [reçu des notes](../archives/etude-avant-yaml-2026-10-24/deplacements.json) conserve les chemins et empreintes avant/après adaptation des liens. Le [reçu des outils](../archives/etude-avant-yaml-2026-10-24/deplacements-outils.json) enregistre leur conservation exacte. La sauvegarde avant nettoyage est `tmp/audit-base-connaissance-2026-10-24/avant-nettoyage.zip`. Aucun commit ou push n’a été effectué.
