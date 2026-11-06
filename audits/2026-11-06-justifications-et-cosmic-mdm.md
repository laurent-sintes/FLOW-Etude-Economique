# Justifications des charges et comparatif COSMIC du MDM

Date : 6 novembre 2026. Les charges adoptées et leurs affectations sont conservées.

## Périmètre

Les douze lots de construction disposent d’une justification structurée : choix, composants réutilisés, exclusions et construction de la charge. Leur nature Métier / IT est indépendante de Core Domain / Support. Les ateliers Supply restent métier malgré l’absence de capacités natives directement rattachées. Les fonctions transverses sont reliées aux lots propriétaires des mécanismes puis aux contributions d’équipes. Elles ne créent pas un second financement.

## Comptage MDM

La feuille `source/comptage-cosmic-mdm.yaml` décrit 49 processus hypothétiques avec utilisateurs, déclencheurs, capacités et groupes de données E (entrée), R (lecture), W (écriture), X (sortie). Les 33 capacités du périmètre courant sont représentées. Ce comptage est établi à partir des exigences et postes déclarés, sans mesure d’un projet réalisé ni déduction depuis la charge adoptée.

Le moteur commun et les services représentent 191 CFP, le studio et les plugins 28 CFP et les groupes de données propres aux familles 179 CFP. Total : 398 CFP. Chaque famille énumère ses objets distincts. Les opérations génériques de certification, publication, distribution et gestion du studio ne sont pas multipliées par famille. Créer et corriger une même famille sont regroupés sous l’hypothèse d’un traitement de maintenance commun. Si leurs traitements ou mouvements diffèrent, le comptage devra être scindé. Les appels internes, attributs, volumes de données, marques et canaux ne sont pas comptés comme mouvements supplémentaires.

La convention existante est reprise de `audits/2026-10-30-master-data-decomposition-gap/benchmark-decision.json` : 20 h/CFP et facteur 1. À 7 h/JH, le comparatif donne 1 137,142857 JH. Aucun ajout de QA ou coordination n’est appliqué à ce benchmark projet. Sa provenance ISBSG et la décision de ne pas appliquer le facteur de taille sont conservées, sans prétendre à une nouvelle calibration MDM.

## Lecture de l’écart

Les 4 145 JH adoptés financent les composants du moteur, les écrans, les adaptations de familles et la qualification. Les 1 137,1 JH du comparatif COSMIC valorisent les mouvements fonctionnels énumérés. Ils ne mesurent pas directement la complexité ergonomique d’un studio graphique, les algorithmes de rapprochement ou les garanties de performance. L’écart n’est ni une remise à appliquer, ni une charge complémentaire à ajouter. Aucun ajustement du comptage n’est fait pour rejoindre la décision actuelle.

Les tâches et processus génériques d’Unidata et l’ancien import XML restent exclus. Les vues Operational References, l’intégration spécifique Beaumanoir et le MCO restent en dehors de cette frontière de construction MDM.

## Reproduction

`tools/mdm_cosmic.py` compte les groupes de données de la feuille et exécute la règle canonique `cosmic_effort`. Les tests rejettent les doublons, les capacités étrangères ou absentes et les paramètres invalides. La projection se rejoue depuis les documents exportés sans checkout logiciel. Les tests de conservation contrôlent que les décisions, JH, contributions et paramètres économiques ne sont pas remplacés par ce comparatif.

Sources méthodologiques : https://cosmic-sizing.org/cosmic-sizing/intro/measurement-process/ et https://cosmic-sizing.org/publications/non-functional-requirements-and-cosmic-sizing-practitioners-guide/.
