# Audit de la page Fondamentaux du modèle

Audit du 28 octobre 2026. Périmètre : contenu, logique de lecture et présentation de la première page du Framework d’évaluation. Les deux précisions sur Synvance et l’usage de la cartographie pour challenger le Buy sont intégrées. La page et les données économiques ne sont pas modifiées.

**La page rassemble des distinctions essentielles, mais leur accumulation masque le raisonnement.** Le problème principal est la hiérarchie des contenus, puis leur répétition. Un espacement plus généreux aidera après cette réorganisation.

**Recommandation : une lecture continue en six chapitres, avec un sommaire par concepts et des détails consultables à la demande.** Le carrousel est déconseillé pour les notions centrales, qui doivent rester faciles à rapprocher. La présentation doit aussi rétablir un entrant aujourd’hui absent : **l’étude Synvance pour le Buy**, confrontée au même besoin métier que le Make.

## Constats prioritaires

### F1 Les fondements du Buy ne sont pas présentés

**Priorité 1 — complétude de l’explication.** La cartographie est présentée comme point de départ de l’estimation. Les deux cartes Make et Buy expliquent ensuite construire ou acquérir, sans dire sur quelles pièces repose l’évaluation Buy. Le lecteur ne peut pas comprendre pourquoi les montants Buy sont crédibles ni comment ils sont confrontés au besoin.

L’étude Synvance est pourtant déjà utilisée : expression des besoins, offres Avanade / Microsoft et Delaware / SAP, questionnaires et projection COPIL. Ces pièces apportent des périmètres, des déclarations de couverture, des prestations, des prix et des durées. Les budgets courants distinguent ces apports et les compléments de l’étude FLOW. Ce constat porte donc sur **une explication manquante**, pas sur un budget manquant.

Présenter les rôles suivants dès les deux premiers chapitres :

| Entrant | Rôle dans le raisonnement |
|---|---|
| **Cartographie métier commune** | Délimiter les capacités retenues. Structurer les travaux Make et challenger le périmètre des propositions Buy. |
| **Fonctions produit et patrimoine logiciel** | Éclairer les mécanismes nécessaires et la réutilisation dans la méthode d’estimation Make. Le statut de la calibration actuelle reste explicite. |
| **Étude et consultation Synvance** | Fournir la base documentaire et commerciale des options Buy étudiées : offres, prestations, prix, inclusions et trajectoires de déploiement. |
| **Analyse FLOW** | Rapprocher les périmètres, expliciter les écarts et les compléments retenus, puis comparer les options en conservant leurs limites. |

Deux distinctions doivent rester visibles : **une couverture déclarée ne prouve pas son intégration dans le prix** ; **un besoin commun ne signifie pas que les offres ont déjà un périmètre identique**. Le budget SAP conserve notamment des travaux Finance hors du périmètre FLOW commun. Cette revue éditoriale ne doit ni les supprimer ni présenter la normalisation comme déjà réalisée.

Ajouter un lien direct « Comprendre les offres Synvance ». Garder le détail des pièces et des retraitements dans son parcours propriétaire. La consultation passée n’est pas une nouvelle dépense à ajouter : la sélection-contractualisation réutilise ce dossier.

Preuves : [entrants et pièces Synvance](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/offres-synvance.md:3>), [construction des prix et de l’enveloppe](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/parcours-synvance.yaml:157>), [écarts de périmètre](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/ecarts-perimetre-flow-rfi.md:7>), [réutilisation du dossier en sélection Buy](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/selection-buy.yaml:31>).

### F2 Les concepts se succèdent sans fil de lecture

**Priorité 1 — structure.** La page juxtapose contexte, cartographie, Make/Buy, Build/Run, niveaux de charge, structures de coût et calendrier. Elle n’annonce pas la question à laquelle chaque distinction répond. « Contexte » est trop général pour orienter le lecteur. Aucun sommaire local ne permet de retrouver une notion.

Réunir objet et périmètre, puis expliquer les démarches Make et Buy avec leurs entrants. Chaque chapitre doit commencer par **une idée essentielle et sa raison d’être**. Les six chapitres sont des dimensions complémentaires du modèle, pas six opérations successives de calcul.

Preuve : [enchaînement de la page](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/EssentialViews.tsx:166>).

### F3 Les charges cumulent définition et reformulations

**Priorité 1 — rédaction.** Chaque carte affiche la définition du glossaire puis une explication spécifique. Les relations et la note générale répètent une partie du contenu. Ce bloc atteint environ 440 mots.

Conserver une formulation courte par niveau, puis un enchaînement **brut → net → total projet**. Présenter une seule fois les règles décisives : pas de double gain de réutilisation, total humain encore incomplet en JH, inconnus distincts de zéro, achats et licences normalement exprimés en euros. Résumer la provenance actuelle en deux phrases visibles, avec accès au détail.

Ce chemin de calcul concerne les efforts estimés. **Les forfaits Buy conservent leur prix documenté** : les JH diagnostiques ne les remplacent pas et les gains de productivité ne constituent pas une remise automatique sur une offre fournisseur.

Les définitions canoniques du glossaire restent disponibles. Une version courte d’affichage doit avoir un propriétaire explicite, sans créer une seconde définition métier divergente.

Preuves : [double rendu définition et explication](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/EssentialViews.tsx:176>), [contenus des charges](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/fondamentaux.yaml:170>).

### F4 Les structures de coût donnent le détail avant la vue d’ensemble

**Priorité 1 — hiérarchie visuelle.** Le bloc combine sept couches d’architecture, sept structures de coût, leurs périmètres, les tags Build/Run, les règles, les descriptions et des exemples. Sur ordinateur, les lignes partagées de la grille étirent certaines cartes : le poste exploitation/support occupe environ 1 314 px pour 48 mots. Sur mobile, les couches sont rappelées dans chaque carte et le bloc atteint environ 3 585 px.

Montrer d’abord **les sept postes, ce qu’ils financent et leurs tags**, sous une forme compacte et lisible. Proposer ensuite le rapprochement détaillé avec les couches d’architecture. Conserver visibles le financement unique, les inclusions des offres Buy et les parts inconnues des contrats groupés. Le schéma détaillé reste utile pour approfondir ; il ne doit plus porter toute l’explication introductive.

Preuves : [composition des cartes](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/ArchitectureLayers.tsx:35>), [grille et règles mobiles](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/architectureLayers.css:4>).

### F5 La mise en valeur est inégale et les paragraphes restent compacts

**Priorité 2 — style et rendu.** La plupart des chapitres utilisent des paragraphes uniformes, alors que les structures de coût permettent déjà le gras. Les charges et les coûts représentent environ **62 % des mots de la page**. Augmenter seulement les espacements allongerait une page déjà très haute sans résoudre cette concentration.

Adopter le style des pages revues : **une phrase clé**, des phrases courtes, des listes pour les éléments réellement parallèles et une exergue lorsqu’une règle change l’interprétation. Réduire les répétitions avant d’espacer les chapitres. Viser, à titre de réglage de conception, 48 à 64 px entre chapitres, 16 à 24 px entre blocs internes et une largeur de prose proche de 70 caractères. Ces valeurs sont à apprécier au rendu, pas des normes d’accessibilité.

Point d’implémentation : plusieurs textes sont rendus directement dans un élément `<p>`. Écrire `**texte**` dans leur YAML ne produirait pas de gras. Réutiliser le rendu inline limité de `MethodText`, sans HTML libre. Les titres de l’architecture doivent aussi retrouver une hiérarchie H2 → H3, au lieu de passer directement de H2 à H4.

Preuves : [paragraphes actuels](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/EssentialViews.tsx:167>), [rendu inline existant](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/MethodDocument.tsx:7>), [titres de l’architecture](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/ArchitectureLayers.tsx:22>).

### F6 Le calendrier répète les postes au lieu de privilégier les déclencheurs

**Priorité 2 — simplification.** Après les sept structures détaillées, les cartes de phases affichent à nouveau treize occurrences de postes avec leurs tags. Le message chronologique se perd dans ce second inventaire.

Mettre au premier plan les trois phases et les règles de passage : consommation des moyens pendant la réalisation, réception locale, début du MCO client et relais annuel sans chevauchement. **Le calendrier Make reste autonome ; les trajectoires Buy reprennent les durées documentées du COPIL**, après sélection-contractualisation. Rendre la liste exhaustive des postes par phase consultable en complément. L’indexation et les sauts de prix peuvent renvoyer aux pages Run et Paramètres.

Preuves : [rappels des postes par phase](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/app/src/EssentialViews.tsx:181>), [textes du calendrier](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/fondamentaux.yaml:93>).

## Choix de navigation

| Option | Avis et raison |
|---|---|
| **Carrousel des concepts essentiels** | Déconseillé. Il cache les notions voisines alors que Programme/Core/Beaumanoir, Make/Buy et brut/net/total se comprennent par leurs relations. Il ajoute des actions de navigation pour lire un contenu nécessaire à tous. |
| **Espacement seul** | Utile mais insuffisant. Il ne corrige ni les répétitions ni les cartes artificiellement étirées. |
| **Lecture continue et sommaire par ancres** | Recommandé. Le lecteur parcourt l’ensemble ou rejoint une notion, garde les comparaisons visibles et retrouve les mêmes repères à la relecture. |
| **Détails dépliables ciblés** | Adaptés aux couches d’architecture, à la cartographie complète et aux listes exhaustives. Les règles qui conditionnent le sens des chiffres restent affichées. |

Ce choix est une recommandation appliquée aux dépendances entre les concepts de cette page. Le [W3C WAI](https://www.w3.org/WAI/tutorials/carousels/) souligne les difficultés de découverte du contenu dans les carrousels et les exigences de clavier, de focus et de contrôle du mouvement. Le [GOV.UK Design System](https://design-system.service.gov.uk/components/accordion/) recommande de simplifier et structurer le contenu, notamment par sommaire, avant de masquer des sections ; le contenu nécessaire à tous doit rester visible. Ses [recommandations sur les onglets](https://design-system.service.gov.uk/components/tabs/) déconseillent également de répartir ainsi un contenu qui doit être lu dans son ensemble ou comparé entre panneaux.

## Organisation proposée

| Chapitre | Message essentiel | Pourquoi cette distinction aide |
|---|---|---|
| **Ce que nous évaluons** | Le programme vise une Plateforme Beaumanoir composée du Core System retenu et des spécificités du Groupe. La cartographie délimite le besoin commun. | Distinguer la transformation, le produit générique et son adaptation ; éviter d’étendre implicitement le périmètre. |
| **Sur quoi reposent les évaluations Make et Buy** | Make estime les travaux à construire ; Buy part des offres et projections issues de Synvance. La cartographie sert à challenger les deux. | Expliquer l’origine différente des estimations et rendre visibles les écarts de périmètre. |
| **Quelles activités relèvent du Build et du Run** | Build et Run classent les activités indépendamment des phases. Le MCO Core est Build ; le MCO Beaumanoir suit sa répartition paramétrable. | Éviter d’assimiler annuel à Run, ou initial à Build. |
| **Que mesurent le brut, le net et le total projet** | Le brut estime les travaux ; le net applique les gains de productivité sur ce même périmètre ; le total projet ajoute les autres efforts humains retenus. | Comprendre ce que couvrent les JH et empêcher une lecture du développement net comme total complet du projet. |
| **Quels postes sont financés** | Sept structures identifient l’objet financé ; une dépense compte une seule fois. | Lire les budgets sans déduire des montants de la seule position dans un schéma. |
| **Quand les dépenses interviennent** | Les trois phases organisent les dépenses selon la consommation, les réceptions et le relais annuel. | Comprendre comment les natures de coût traversent le calendrier. |

Le sommaire suit cet ordre en une seule colonne. Les schémas de relation restent visibles ; les cartes exhaustives et détails documentaires viennent après leur explication courte. La composition de la Plateforme Beaumanoir est une relation métier, pas une formule de coût. Les formules de calcul détaillées restent dans leurs pages propriétaires, accessibles par lien.

## Extraits rédactionnels proposés

**Entrants communs et démarches distinctes**

> **La cartographie métier fixe le besoin à examiner dans toutes les options.** En Make, elle structure les travaux à estimer. En Buy, elle sert à confronter les offres au besoin et à identifier les écarts.

> **L’évaluation Buy s’appuie d’abord sur l’étude Synvance.** Les offres fournisseurs, les questionnaires et la projection COPIL documentent les prestations, les prix et les trajectoires de déploiement. L’étude FLOW explicite les compléments retenus et les différences de périmètre.

**Charges**

> **Le brut estime le développement restant après réutilisation. Le net applique les gains de productivité aux mêmes travaux.** La charge totale projet ajoute les autres efforts humains retenus.

> **Le total humain reste incomplet en JH.** Une composante inconnue ne vaut pas zéro. Les achats, licences et forfaits fournisseur restent normalement exprimés en euros.

**Provenance actuelle**

> La base de charge actuelle du Core System provient des hypothèses de travaux déjà enregistrées. La nouvelle méthode du skill n’a pas encore recalibré cette base.

**Calendrier**

> **Les dépenses suivent la consommation et les réceptions.** Le Run peut commencer pendant la réalisation ; le MCO client commence après réception.

## Ordre de mise en œuvre et critères de réussite

1. **Réorganiser le contenu et compléter les entrants.** Faire apparaître Synvance, le rôle transversal de la cartographie et les liens vers les explications propriétaires. Dédupliquer les charges et les rappels de postes.
2. **Installer le sommaire et les deux niveaux de lecture.** Conserver les règles essentielles visibles ; réserver les dépliages aux détails.
3. **Harmoniser le style et la mise en page.** Rendu du gras, titres, largeur de prose, espacements, suppression des étirements inutiles et allègement mobile.
4. **Vérifier la compréhension et la navigation.** Lecture ordinateur/mobile, clavier, focus après navigation, titres, recherche dans la page et impression. Préserver la charte et l’animation d’en-tête, avec réduction des mouvements.

Le lecteur doit pouvoir expliquer d’où viennent les hypothèses Make et Buy, comment elles sont confrontées au besoin, ce que couvrent les JH, ce que financent les postes et quand les dépenses interviennent. Les cinq options, les sources, les valeurs, les contrats de simulation et les limites économiques restent inchangés. Aucun exemple chiffré fictif n’est nécessaire pour expliquer ce parcours.

## Vérification du rendu

Inspection des sources et du rendu courant avec un navigateur isolé, sans modification des simulations. Deux tailles observées : 1 440 × 1 050 px et 390 × 844 px. Il s’agit d’une revue experte, pas d’un test de compréhension avec des lecteurs.

| Indicateur | Ordinateur | Mobile |
|---|---:|---:|
| Mots affichés dans le contenu de la page | 1 843 | 1 838 |
| Hauteur totale de la page | 4 562 px | 10 039 px |
| Hauteur du bloc charges | 727 px | 1 681 px |
| Hauteur du bloc structures de coût | 1 474 px | 3 585 px |
| Débordement horizontal global observé | Aucun | Aucun |

Les mesures de hauteur dépendent de la largeur et des polices. Elles objectivent la concentration du contenu sans fixer un objectif arbitraire de longueur. La cartographie mobile conserve notamment une grille de trois colonnes et de petits libellés : un traitement mobile spécifique sera nécessaire si le schéma détaillé est conservé.

Pièces de contrôle : [mesures du rendu](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/tmp/audit-fondamentaux-rendu.json>), [haut de page sur ordinateur](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/output/audit-fondamentaux-desktop-haut.png>), [structures de coût sur ordinateur](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/output/audit-fondamentaux-desktop-couts.png>), [haut de page sur mobile](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/output/audit-fondamentaux-mobile-haut.png>), [structures de coût sur mobile](</C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/output/audit-fondamentaux-mobile-couts.png>).
