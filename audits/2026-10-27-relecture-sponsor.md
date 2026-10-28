# Contrelecture du parcours sponsor — 27 octobre 2026

## Objet et méthode

Relire la Synthèse, les cinq lectures Comprendre / Estimer, leurs approfondissements et leurs preuves du point de vue du sponsor. Trois contrelectures indépendantes du code et des sources complètent la lecture dans le navigateur local. Cette revue modifie la restitution, sans nouvelle hypothèse métier ou économique.

## Constats corrigés

| Obstacle | Correction |
| --- | --- |
| La nomenclature métier précède l’explication du choix. | Make et Buy apparaissent avant la carte d’introduction. Cette carte ouvre le domaine dans Périmètres comparés ; elle ne duplique plus son explorateur. |
| Le résultat du choix Finance / OMS / réassort / stocks est loin de sa commande. | L’argument et sa preuve apparaissent immédiatement sous les quatre sujets, avant la carte. La mention « Cible métier à construire » est commune, plutôt que répétée neuf fois. |
| « Hypothèses de valorisation » réaffiche budgets, méthode et 89 lignes de charges. | Lecture ciblée de la méthode ; plage budgétaire accessible séparément, charges par leur lien propre. Environ 2 683 mots auparavant, environ 245 après ; six lignes de gains au lieu de 98 lignes de tableaux. |
| La construction de l’intégration déroule aussi les 43 situations métier. | Quatre lectures exclusives : budgets, construction, travaux, situations. La construction passe d’environ 4 266 mots à environ 260. Les 43 situations restent recherchables puis lisibles intégralement une par une. |
| Les justifications de complexité encombrent aussi le détail des JH et coûts. | Leur affichage est réservé à la couche Complexité. Le détail des fonctions et preuves reste accessible dans les autres couches. |
| La liste des projets de marché répète la synthèse déjà lue. | Accès direct aux quinze références, avec leurs appréciations et pièces ; les conclusions Build et Run distinguent le constat courant de la vérification restante. |
| Les liens YAML / Markdown annoncent un passage mais ouvrent le fichier entier. | Extraits ciblés par clé, identité ou chemin YAML, et par section Markdown ; emplacement explicite, accès à la source complète, choix en cas d’ambiguïté. |
| Le lien « Questionnaires » sur les stocks ouvre une analyse. | Deux liens vers les questionnaires Microsoft et SAP originaux, avec les cellules citées. L’analyse reste distincte. |
| La preuve d’un budget Buy renvoie seulement au fournisseur. | Lien direct vers le passage de l’offre au budget FLOW, avec distinction entre base achetée et compléments de l’étude. |
| Des renvois FAQ génériques rejoignent une seule partie du nouveau parcours. | Deux accès explicites Build / Intégrer et exploiter, puis routes canoniques ciblées ; aucune réponse ni liaison numérique modifiée. |

Le fort écart entre le repère d’intégration Make et le chiffrage par activités reste visible. La lecture précise qu’il reste à instruire sur un périmètre et des responsabilités communs, et ne constitue pas une économie démontrée. Aucun des deux montants n’a changé.

## Preuves et vérifications

- Contrôle documentaire statique : 432 références distinctes ; 344 passages uniques et 88 références de capacité partagées entre les deux revues Buy, proposées explicitement au choix. Aucun repère introuvable dans cet inventaire. Les identifiants contenant un point restent prioritaires sur la notation de chemin pointée.
- Résolution directe contrôlée pour les lots de travaux, les trois résultats Build, les gains, le repère Make et les situations métier. Les fichiers originaux restent accessibles ; PDF et XLSX restent servis sans transformation.
- Navigateur : retour de source complète vers extrait, fermeture par Échap et retour du focus au bouton d’origine ; sélection d’un lot depuis une capacité ; navigation entre couches ; recherche « magasin », ouverture d’une situation et retour conservant les sept résultats filtrés.
- La carte d’introduction rejoint le sous-domaine choisi dans Périmètres comparés. Les différences de périmètre sont visuellement avant la carte. Les cinq lectures ont été vérifiées à 390 px de largeur, sans débordement horizontal de page ; les grandes comparaisons gardent leur défilement horizontal local.
- Les tests du fond métier et du parcours sponsor conservent les résultats, les identités de financement, les quatre horizons et les sensibilités. Les tests de navigation, reprise, scénarios nommés et formatage passent. Le test HTTP, bloqué initialement par la restriction de socket du bac à sable, passe après relance avec accès local autorisé. Au total : 61 tests Python distincts (dont 13 sur les extraits) et 29 tests JavaScript réussis.
- TypeScript, contrôle des contenus et compilation de production vérifiés. Les avertissements Vite existants sur Lucide et la taille du paquet ne bloquent pas la compilation.

## Fichiers concernés

Contenus : `source/parcours-sponsor.yaml`, `source/atlas-sponsor.yaml`, `source/parcours-integration.yaml`, `source/faq-sponsors.yaml`, `config/application.yaml`.

Lectures : `SponsorJourney.tsx`, `BusinessAtlas.tsx`, `businessAtlas.css`, `views.tsx`, `IntegrationEstimates.tsx`, `ReadingPages.tsx`, `components.tsx` dans `app/src`.

Preuves : `tools/document_excerpt.py`, `tools/test_document_excerpt.py`, route documentaire de `tools/serve_study_app.py`, inventaire autorisé de `tools/study_app.py`. Le moteur, les paramètres et le contrat de simulation restent inchangés.
