> **MÉTHODE HISTORIQUE — remplacée le 20 octobre 2026. Ne pas utiliser pour établir un budget. Consulter les méthodes courantes 11 et 12 dans le dossier principal.**

![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 19 octobre 2026

---

# Audit du dossier estimatif FLOW Make et de son incertitude

**19 octobre 2026 — audit de l'ensemble des pièces de cette étude.** Objectif : savoir si le dossier permet de présenter un coût bas, un coût central le plus plausible et un coût haut, sans transformer l'ordre de grandeur en engagement. L'[étude de méthode](02-methode-estimation.md), le [modèle de charge](06-premier-ordre-de-grandeur-effort.md), les [abaques](09-abaques-repartition.md), l'[analyse Buy](08-pont-charges-buy-make.md), les [références de marché](03-references-marche.md) et les [fiches de soutenabilité](05-fiches-entreprises-et-criteres-investissement.md) ont été examinés.

**Suite de l'audit :** Laurent a ensuite retenu un objet plus restreint : le **coût nominal minimum** d'un forfait externe autonome, avec mise en service unique, sans coûts internes, support, coexistence ou réserve de risque. Ce calcul figure dans le [document dédié](11-cout-nominal-minimum.md). Les besoins ci-dessous concernent toujours une estimation **centrale probabilisée ou complète**, pas ce minimum nominal simplifié.

## Verdict

**Oui, les éléments suffisent pour monter maintenant un dossier d'ordre de grandeur conditionnel.** Le périmètre opérationnel, les exclusions, l'architecture Make de référence, les postes de chiffrage, deux bornes de charge et une option explicite pour les fonctions Storeland non découvertes sont disponibles. Il n'est pas nécessaire de connaître toutes les règles de chaque marque ni le lotissement final pour bâtir ce dossier.

**Non, les pièces actuelles ne suffisent pas encore à défendre un montant central en euros comme « le plus probable » ni à lui attribuer une probabilité.** Les **33 100–63 600 JH identifiés**, ou **38 065–73 140 JH avec l'option Storeland**, sont deux jugements de charge par poste, pas une distribution ; les [clés d'imputation](09-abaques-repartition.md) répartissent les JH identifiés, sans les étalonner. Le coût unitaire, le mix interne/externe et les dépenses non exprimées en JH ne sont pas établis pour FLOW. La simulation historique **35–75 M€** du [fichier de résultats](04-resultats-etude.md) ne doit pas combler ce vide : elle repose sur un autre profil de moyens et des tarifs supposés.

Le dossier peut donc être produit en deux états : **version estimative provisoire**, avec un coût central explicitement *jugé* sous hypothèses de tarif et de charge ; puis **version étalonnée**, après remplacement des hypothèses les plus influentes par quelques observations. Il ne faut pas retarder la première version pour un cadrage exhaustif. En revanche, publier dès maintenant un chiffre central sans afficher ces hypothèses donnerait une précision trompeuse.

## Audit par composante

| Composante | Éléments déjà disponibles | Solidité pour l'ordre de grandeur | Reste à expliciter pour le coût central |
| --- | --- | --- | --- |
| Périmètre | [Cahier des charges](01-cahier-des-charges.md) : cœur SCM, frontières des canaux, finance/commerce amont/WMS/TMS exclus, remplacement des applications citées. | **Suffisant sous hypothèses.** Le modèle métier publié n'est pas une liste de modules à coder. | Tenir visibles les fonctions Storeland inconnues ; les 15 % sont une option de périmètre hors nominal, pas une mesure de ces fonctions. |
| Configurabilité | Cahier fourni et exigences d'héritage, version, simulation, approbation, traçabilité. | **Suffisant pour un poste explicite** de Build. | Nombre et difficulté des familles de règles initiales ; au minimum un petit échantillon représentatif pour situer le coût central du poste. |
| Build et intégration | [14 postes en JH](06-premier-ordre-de-grandeur-effort.md) ; [abaques](09-abaques-repartition.md) entre Build, configuration et flux/sécurité. | **Structure exploitable**, sans double compte apparent après séparation. | Une charge *la plus plausible* par poste ou groupe de postes ; justificatif des clés mixtes les plus influentes. |
| Référence Buy | Delaware : **14 640 JH d'intégrateur** ; WRICEF, domaines et phases visibles. | **Contrôle utile**, à périmètre et mode de réalisation différents. | Ne pas convertir le total Buy en Intégration Make. Total interne contradictoire de **600 JH** ; budget externe imprimé supérieur de **2 M€** à la somme de ses lignes. |
| Références externes | Inditex, Zalando, Fast Retailing, logiciels ouverts, ABOUT YOU, Apec et Malt. | **Contrôles de cohérence**, pas coût isolé d'un FLOW comparable. | Aucun benchmark public ne remplace la charge par poste ou le tarif propre au programme. Les lignes de code ne donnent pas un coût constaté. |
| Tarifs et moyens | Simulation historique **110–155 k€ par ETP-an**, repère public Malt, budget d'intégrateur Buy. | **Insuffisant pour un coût FLOW central.** | Coût complet interne et prix externe **par famille de rôles**, jours productifs/an et part interne/externe. Avec la convention actuelle de 200 JH/ETP-an, l'ancien 110–155 k€ correspondrait à **550–775 €/JH** ; ce calcul ne valide aucun de ces tarifs. |
| Dépenses non-JH | Simulation historique de **4–10 M€** pour moyens techniques et coexistence. | **Hypothèse non étalonnée.** | Enveloppe basse/centrale/haute pour environnements, hébergement, support OSS éventuel, outillage, migration/coexistence et prestations non comptées dans les JH ; éviter les doublons. |
| Délai et effectifs | Dépendances décrites ; ancienne trajectoire **48–54 mois**, **75–105 personnes au pic**. | **Plausibilité qualitative**, sans chemin critique ni disponibilité validée. | Choisir une capacité d'équipe et quelques jalons de bascule de référence ; ne pas dériver le délai de la seule division des JH. |
| Soutenabilité | Indices publics de profitabilité, fonds propres et trésorerie Beaumanoir ; critères d'investissement formalisés. | **Suffisant pour dire que le sujet mérite instruction**, pas pour approuver un budget. | Flux de trésorerie disponibles, engagements et décaissements FLOW par année seulement au stade de la décision d'investissement. |

### Deux corrections de lecture importantes

1. **Borne basse et borne haute ne portent aucune probabilité connue.** Leur écart d'environ **1,92 fois** traduit la largeur du jugement actuel. Un milieu arithmétique, soit environ **56 883 JH**, n'est pas automatiquement la charge la plus plausible et ne devient pas un P50.
2. **« Le plus probable », « médian » et « espérance » sont trois notions différentes.** Pour le dossier simple demandé, nommer le chiffre central **hypothèse centrale la plus plausible** (mode de jugement expert). Réserver **médiane/P50** et **espérance/moyenne** à une distribution de coût réellement construite et documentée. La méthode à trois points *minimum, most likely, maximum* est reconnue dans le [guide GAO d'estimation des coûts](https://www.gao.gov/assets/gao-20-195g.pdf) ; ce guide souligne aussi l'importance des dépendances entre postes quand on quantifie un niveau de confiance.

## Le complément minimal, sans cadrage exhaustif

| Donnée à produire | Format minimal acceptable | Pourquoi elle est décisive |
| --- | --- | --- |
| **Charge centrale par poste** | Pour les 14 lignes du [modèle](06-premier-ordre-de-grandeur-effort.md), ajouter un **M JH** entre L et H, choisi par les responsables du domaine avec une phrase de justification. Concentrer la discussion sur stock/réservation, Order Management, configuration gouvernée, backlog/solveur et interfaces. | Crée une valeur centrale fondée sur le contenu, au lieu d'un simple milieu de fourchette. |
| **Matrice de prix et de mobilisation** | Quelques familles : produit/métier, développement, architecture/data/solveur, intégration, tests, sécurité, pilotage/change ; pour chacune, coût complet interne ou TJM externe et part de charge. | Convertit les JH en euros sans appliquer un tarif unique à tous les travaux. Trois mixes bas/central/haut sont possibles si l'organisation n'est pas décidée. |
| **Coûts non-JH et frontière de calcul** | Bas/central/haut pour infrastructure et environnements, support de composants, outils, coexistence des anciens SI ; préciser HT, années de prix et charges déjà incluses dans les JH. | Évite de présenter un coût de personnel comme coût complet de programme. |
| **Registre court des risques de coût** | Cinq à huit facteurs qui déplacent réellement l'estimation, chacun avec poste touché, effet central/haut et statut déjà inclus ou non : inconnues Storeland, variantes de règles, interfaces partenaires, migration, tenue de stock sous pics, performance du solveur, coexistence. | Permet de distinguer les fourchettes des postes, l'option de périmètre Storeland de **15 %** et une éventuelle réserve d'exécution ; pas de pourcentage global ajouté sans motif. |

Ce complément peut être obtenu par quelques échanges ciblés et une grille de coûts interne. Le nombre exact de vagues, les flux détaillés de tous les partenaires et le catalogue exhaustif des règles servent à **resserrer** le résultat ultérieurement ; ils ne sont pas des préalables au premier dossier.

## Présentation simple de l'incertitude proposée

1. Pour chaque poste et chaque dépense non-JH, écrire **L / M / H**, en explicitant ce qui change entre les trois valeurs. Les trois valeurs doivent porter sur **le même périmètre FLOW identifié** ; l'option Storeland de 15 % reste affichée séparément tant que les fonctions manquantes ne sont pas connues.
2. Calculer le coût des trois colonnes avec `Σ(JH par poste × coût journalier par rôle et par mix) + dépenses non-JH`. Les contributions Beaumanoir et prestataires sont toutes valorisées. Les économies de licences Buy ou les gains métiers restent hors du coût de construction et vont dans l'analyse de valeur séparée.
3. Appeler les résultats **borne basse conditionnelle**, **coût central le plus plausible sous hypothèses** et **borne haute conditionnelle**. Ne pas annoncer de probabilité ou de confiance statistique. L'ensemble des postes peut être sensible au même événement (par exemple une migration difficile) ; les bornes ne doivent donc pas être présentées comme des quantiles indépendants.
4. Faire un test de sensibilité simple sur les **trois plus grands moteurs** : charge Build, tarif/mix interne-externe, nombre de flux et difficulté de migration. Montrer combien chaque changement déplace le coût central. Une réserve de risque supplémentaire n'est ajoutée que pour un risque **non déjà couvert** par les L/M/H et les 15 %.
5. Donner **séparément** la plage de délai et d'effectifs, puis le profil annuel de dépenses si la soutenabilité financière est discutée. Le coût central n'est pas un calendrier.

Le [guide GAO](https://www.gao.gov/products/gao-20-195g) préconise notamment une base technique, une décomposition des travaux, des hypothèses, une analyse de sensibilité et des risques, puis une mise à jour avec des coûts observés. Cette méthode est applicable ici comme discipline de traçabilité ; elle ne fournit pas de coefficient spécifique à FLOW. Une véritable probabilité « le budget a X % de chances d'être tenu » demanderait une distribution et un traitement des corrélations qui ne sont pas encore disponibles.

## Décision d'audit

**Feu vert pour préparer le dossier estimatif à trois valeurs, avec une mention visible de faible maturité.** Les pièces actuelles soutiennent la **structure**, les **bornes de charge conditionnelles** et l'explication des écarts Buy/Make. Le **montant central en euros** reste une case à remplir avec les quatre apports ciblés ci-dessus ; le calculer aujourd'hui à partir du milieu des JH et des anciens tarifs ferait passer des hypothèses non calibrées pour une mesure. La première publication peut être faite dès que ces apports sont posés, puis révisée à mesure que des réalisations FLOW ou des prix négociés deviennent observables.

