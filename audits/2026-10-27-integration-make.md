# Intégration Make : expliquer l’écart avec le repère SAP

Audit du 27 octobre 2026. Budgets en k€ HT, sans décimales ; calculs exacts conservés dans le fichier de preuves. Aucun paramètre, budget actif ou scénario enregistré n’a été modifié.

**Conclusion : l’écart arithmétique est reconstitué, mais son explication économique ne permet pas encore de choisir un prix central FLOW validé.** Les deux calculs ne démontrent pas qu’ils couvrent les mêmes travaux, quantités et responsabilités. Pour apprécier l’opportunité, je recommande de donner priorité au test SAP retraité **sans gain de continuité : 10 988 k€ HT**. La référence actuelle de **9 889 k€ HT** reste une hypothèse avec un gain conditionnel de 10 %. Les **1 345 à 1 822 k€ HT** constituent un catalogue de travaux Make à redimensionner, pas une économie démontrée ni une borne basse validée.

Cette recommandation ne transforme pas 10 988 k€ en devis, prix central ou plafond prudent. Elle retire seulement un avantage non observé du test de décision.

## Les deux constructions, reconstituées

| Lecture de l’intégration | Java / Spring Boot | .NET | Rust |
| --- | ---: | ---: | ---: |
| Repère SAP retraité actuellement retenu — k€ HT | 9 889 | 9 889 | 9 889 |
| Estimation par activités — k€ HT | 1 345 | 1 459 | 1 822 |
| Écart — k€ HT | 8 544 | 8 430 | 8 067 |
| Rapport des budgets | × 7,35 | × 6,78 | × 5,43 |
| Treize activités, JH avant gains | 2 105 | 2 120 | 2 265 |
| JH après gains, accompagnement de 120 JH compris | 2 063 | 2 077 | 2 276 |

Les montants par stack ne forment pas une plage d’incertitude : ils représentent trois options techniques. Les jours ci-dessus ne comprennent pas de JH de pilotage autonomes ; le modèle ajoute un pourcentage monétaire de pilotage.

Le passage SAP → Make est le suivant :

| Étape | k€ HT | Nature de la preuve |
| --- | ---: | --- |
| Somme des trois lots Delaware | 13 462 | Prix détaillés du document fournisseur |
| Retrait indicatif Finance / FP&A | −2 583 | 2 810 JH valorisés au prix moyen de leur lot : calcul de l’étude |
| Qualification client, pilotage associé et préparation | +109 | Compléments de l’étude, dont inclusion à rapprocher des prestations fournisseur |
| Repère avant gain de continuité | **10 988** | Analogie SAP retraitée |
| Gain de continuité retenu, 10 % | −1 099 | Hypothèse non observée |
| Référence actuelle Make | **9 889** | Résultat du scénario courant |

La somme exacte des lots vaut 13 462 352 €, contre 15 462 352 € imprimés. Le modèle utilise bien les prix détaillés, pas le total imprimé. L’écart de 2 000 k€ est donc déjà écarté de la base centrale ; il n’explique pas l’écart restant avec les activités Make. [Delaware, page PDF 38, folio 46](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Fdelaware-septembre.pdf#page=38).

Le retrait Finance représente 2 036 JH du lot 2 et 774 JH du lot 3, valorisés aux prix moyens propres à ces lots. Delaware ne fournit pas cette ventilation monétaire. Le lot d’upgrade Finance/CCM de 421 JH demeure dans le reste. Certaines liaisons comptables utiles aux achats, ventes et stocks peuvent aussi être nécessaires à FLOW. [Delaware, pages PDF 39–40](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Fdelaware-septembre.pdf#page=39) ; [convention de retrait](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/plan-investissement.yaml:32>).

L’exclusion des compléments génériques Buy vaut actuellement **0 k€** : aucun développement additionnel générique démontré n’est chiffré dans ce portefeuille. Le mécanisme de calcul ne retire donc pas une fraction connue des travaux des lots SAP au motif qu’elle serait déjà financée par le build FLOW. L’absence de complément Buy chiffré ne prouve pas l’absence de recouvrement entre les travaux des deux trajectoires. [Résultat du retrait](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/investissements-10-ans.yaml:72>).

## Ce qui explique l’ordre de grandeur — et ce qui ne le prouve pas

**L’écart porte principalement sur les charges retenues ; leur différence d’étendue reste à expliquer.** Après retrait Finance, le proxy SAP conserve 11 830 JH de programme. Le catalogue Java prévoit 2 225 JH bruts, accompagnement compris. Le rapport est de 5,32, mais ce n’est pas une mesure de productivité : les travaux, responsabilités et JH de gouvernance ne sont pas normalisés.

Le document SAP décrit un Core Model groupe sur Boardriders puis un déploiement Beaumanoir, et non la création du logiciel générique SAP. Le lot 2 ne peut donc pas être retiré intégralement au motif que le build FLOW finance déjà un produit. Le document recense 142 puis 82 processus, 32 puis 31 objets de reprise, 41 puis 37 interfaces. Il s’agit de volumes par lot, pas nécessairement d’objets uniques. [Delaware, pages PDF 15–16](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Fdelaware-septembre.pdf#page=15) et [page PDF 33](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Fdelaware-septembre.pdf#page=33).

Le Make décrit lui aussi une réalisation complète. Migration, recette, formation et bascule sont présentes dans ses treize activités. Le point faible est leur dimensionnement : 30 contrats de flux, 10 applications externes et trois environnements sont des hypothèses, sans inventaire validé ni nombre de vagues. Les JH d’intégration sont saisis par activité ; ils ne sont pas recalculés automatiquement depuis ces volumes. [Catalogue et limites](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/integration.yaml:46>) ; [volumes du scénario](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/maintenance.yaml:447>).

Le seul rapprochement quantitatif externe explicite sur les flux est utile mais limité : Avanade chiffre 380–460 JH pour 40 interfaces identifiées, soit 9,5–11,5 JH/interface. Le Make Java suppose 30 × 10 JH. Cela soutient un abaque de contrôle pour les interfaces, pas les 30 contrats eux-mêmes ni l’ensemble du programme. L’estimation Avanade porte sur un pilote et reste non engageante. Son total de 1 900–2 300 JH, proche numériquement du catalogue Make complet, invite à vérifier les périmètres ; il ne valide ni n’invalide à lui seul ce catalogue. [Microsoft, page PDF 39](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Fmicrosoft-1.pdf#page=39) ; [hypothèse INT-006](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/chiffrage/chiffrage-java-spring.yaml:839>).

**Dans les diagnostics testés, les changements de tarifs et de gains ne comblent pas l’écart.** Les diagnostics suivants conservent les volumes Java ; ils ne constituent pas de nouveaux devis :

| Diagnostic Java | k€ HT | Ce qu’il montre |
| --- | ---: | --- |
| Catalogue courant | 1 345 | Base des treize activités, accompagnement, pilotage et préparation |
| Même catalogue sans gains de productivité | 1 444 | Les gains expliquent 98 k€, pas 8 544 k€ |
| Même volume brut, au prix moyen du dispositif SAP retraité, pilotage non recomposé | 2 106 | Diagnostic mécanique, sans équivalence des rôles ni du dispositif |
| Même diagnostic, avec maintien hypothétique du taux de pilotage Make | 2 311 | L’ajout du taux de 10 % ne reconstitue pas davantage le budget de programme SAP |
| Sensibilité haute existante du catalogue | 2 027 | Le facteur générique de charge ne couvre pas une différence d’étendue non identifiée |

Le diagnostic à 2 106 k€ applique environ 920 € HT/JH aux 2 225 JH bruts, plus la préparation Make. Le ratio SAP comprend la gouvernance au numérateur et dans ses JH au dénominateur ; l’appliquer aux JH de réalisation Make ne prouve pas qu’il finance une gouvernance équivalente. Le pilotage n’est donc pas recomposé dans ce premier diagnostic. Le second conserve hypothétiquement le taux Make de 10 %, sans prétendre qu’il remplace le dispositif SAP. Aucun supplément d’outillage n’est appliqué au prix moyen fournisseur. Ces tests ne sont ni un TJM individuel observé ni une normalisation des rôles. La sensibilité ESN déjà présente dans le modèle, en conservant au contraire les 11 830 JH SAP, donne 10 715 k€ avant gain de continuité : changer les tarifs sans changer les volumes conserve l’ordre de grandeur SAP. Ses prix et parts de profils restent hypothétiques. [Sensibilité existante](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/investissements-10-ans.yaml:108>) ; [calcul reproductible](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/audits/2026-10-27-integration-make-calcul.py>).

## Les principales frontières à rapprocher

| Travaux | Preuve SAP | Hypothèse Make / contrôle requis |
| --- | --- | --- |
| Paramètres et adaptations client | Processus des lots Boardriders et Beaumanoir ; Core Model client | INT-001 à 005 : 605 JH Java. Identifier les variantes client et les mécanismes génériques déjà livrés. |
| Flux et données | Interfaces et objets de reprise par lot ; 705 JH sur les lignes de reprise | INT-006 : 300 JH ; INT-007 : 280 JH Java. Rapprocher les contrats et objets, leur complexité, qualité et répétitions de migration. |
| Recette | 3 278 JH de phases SIT/UAT sur les lots 2–3 | INT-010 : 250 JH Java, plus tests locaux ailleurs. Périmètres, campagnes et responsabilités à rapprocher ; les deux nombres ne sont pas directement équivalents. |
| Bascule et stabilisation | 1 727 JH dans les phases Final Prep/Go Live, puis 368 JH Operate de projet | INT-013 : 180 JH Java, sans nombre de vagues. Identifier les sites/entités, répétitions et support transitoire. |
| Gouvernance et coordination | 1 319 JH de gouvernance, plus 557 de coordination fonctionnelle et 495 liés au GDC | Le Make ajoute 10 % de coordination technique. Ce taux ne démontre pas la couverture du même dispositif de programme. |
| Socle, formation et transition | Dispositifs projet et interfaces avec l’exploitation | Clarifier les livrables communs Build / INT-009, INT-012 / accompagnement et maintien du Core pendant l’intégration. |

Sources SAP : [pages PDF 39–40](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Fdelaware-septembre.pdf#page=39). Sources Make : [treize charges](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/chiffrage/chiffrage-java-spring.yaml:808>) et [règles communes](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/calibration-couts.yaml:149>).

Le catalogue conserve par ailleurs un `pilotage_global` non chiffré, distinct de l’abaque de coordination technique. Aucune ligne de direction de programme tarifée ne démontre aujourd’hui l’équivalence avec le dispositif SAP. Ce poste inconnu n’est pas nul ; il ne doit pas non plus être ajouté mécaniquement sans rapprocher les responsabilités déjà financées. [Frontière du pilotage](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/integration.yaml:482>).

**Ces lignes ne s’additionnent pas entre elles pour recalculer SAP.** Les phases SIT/UAT et Go Live recoupent les lignes métier et transverses. De même, le focus WRICEF de 2 990 JH est contenu dans les lots ; il ne faut ni l’ajouter au programme, ni le retirer intégralement comme du build générique. Il contient notamment interfaces, conversions, formulaires et adaptations client qui peuvent rester nécessaires en Make. [Delaware, page PDF 41](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Fdelaware-septembre.pdf#page=41).

Trois points plus ciblés méritent correction de frontière avant toute nouvelle estimation :

- INT-009 décrit une industrialisation initiale entièrement financée en intégration, alors que le socle transverse du build actif comprend déjà CI/CD et tests transverses. Distinguer fabrique du produit et déploiement client ; aucun double compte chiffré n’est démontré. [Build transverse](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/recalibration-metier.yaml:930>).
- INT-012 prévoit formation/transfert aux utilisateurs clés, puis 120 JH d’accompagnement sont ajoutés pour supports et transfert. Les deux livrables peuvent être distincts, mais leur frontière textuelle ne le prouve pas. Retirer tout l’accompagnement diminuerait Java de 74 k€ seulement : ce point ne résout pas l’écart principal et n’autorise aucun retrait automatique.
- Les mêmes justifications de flux produisent 300 / 310 / 330 JH, et les tarifs intégration/N3 suivent 550 / 600 / 700 € HT/JH selon la stack. Les besoins communs de mapping, migration ou recette ne requièrent pas systématiquement un spécialiste du langage backend. Ce choix de sourcing doit être explicité ; il ne prouve pas une surcharge technique globale de Rust.

Le repère SAP n’est pas pour autant une borne supérieure : son périmètre contient Finance mais laisse certains processus Supply et le moteur de réassort magasin hors chiffrage. Inversement, la maturité et le maintien du nouveau produit FLOW pendant l’intégration ne sont pas tarifés par Delaware. [Frontières SAP, pages PDF 19 et 26](http://127.0.0.1:8766/api/file?path=sources%2Fclient%2Fdelaware-septembre.pdf#page=19) ; [audit de transition du Core](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/audits/2026-10-26-coherence-couts.yaml:93>).

## Le fond métier aide à réconcilier ; il ne donne pas un multiplicateur

Les 43 situations sont reliées à 82 des 88 capacités, dans les neuf sous-domaines natifs. Toutes portent le statut de rapprochement proposé et les quatre mêmes lots : paramètres, parcours, flux, recette. Le déploiement est déclaré mutualisé à part. Aucun de ces rapprochements ne contient un volume, une charge ou un nombre de vagues qui explique le facteur d’écart. [Source des rapprochements](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/parcours-integration.yaml:1>).

Il faut conserver ces identifiants pour relier les livrables aux capacités, sans compter un forfait par scénario. Par exemple, le réapprovisionnement mobilise Inventory Tracking, Plan Application, Supply Assignment, Sales Order, Transfer Order, Stock Redistribution et Replenishment. Un contrat de flux ou un mécanisme partagé doit avoir un propriétaire de financement unique, même s’il sert plusieurs situations.

À ce stade d’opportunité, un bordereau limité aux six blocs ci-dessus suffit : objets et volumes plausibles, responsable externe/interne, réemploi du build démontré, charges résiduelles et plage motivée. Le détail par tâche ou écran n’est pas nécessaire. Les quantités inconnues restent inconnues. Il ne faut ni moyenner 1 345 et 9 889 k€, ni multiplier le catalogue par 7,35 pour fabriquer une convergence.

La méthode est cohérente avec le [guide GAO-20-195G, pages imprimées 124–128](https://www.gao.gov/assets/gao-20-195g.pdf#page=136) : rapprocher les bases techniques et hypothèses, puis documenter les différences ; une analogie exige des ajustements justifiés, tandis qu’une estimation détaillée exige des quantités et prix auditables. Ce guide valide une démarche, pas un prix FLOW.

## Base défendable devant le sponsor

Je présenterais les trois chiffres avec des rôles explicites : **10 988 k€ HT pour tester l’opportunité sans créditer le gain de continuité ; 9 889 k€ HT comme scénario conditionnel actuel ; 1 345 à 1 822 k€ HT comme contrepoint des activités, dont le dimensionnement de programme reste à établir.** Aucun de ces trois rôles ne vaut engagement forfaitaire.

Le gain de continuité suppose que l’équipe connaissant le produit reste effectivement mobilisée et réduise le travail client chantier par chantier. Le modèle le qualifie déjà de paramètre non observé. Tester 0 % est une convention de décision plus exigeante sur ce seul facteur, pas une estimation globalement prudente. [Hypothèse de continuité](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/source/plan-investissement.yaml:15>).

À calendrier, build et services annuels inchangés, retirer ce gain ajoute **1 099 k€ HT** à chaque Make une fois l’intégration financée. À dix ans :

| Option | Dépenses de référence, k€ HT | Sans gain de continuité, k€ HT |
| --- | ---: | ---: |
| Java / Spring Boot | 23 360 | 24 458 |
| .NET | 24 593 | 25 692 |
| Rust | 29 750 | 30 849 |
| Microsoft | 22 653 | 22 653 |
| SAP | 39 108 | 39 108 |

Le classement financier ne change pas à cet horizon. L’écart Java au-dessus de Microsoft passe de 707 à 1 806 k€ HT. Ce sont des dépenses sur dix années depuis un départ commun, avec 3,17 années de service complet Make, 6,83 Microsoft et 7,50 SAP ; le périmètre SAP demeure différent. Cette comparaison n’est pas un coût de dix années de service identique. À trois ans, l’intégration Make n’est pas encore financée dans le calendrier ; à cinq ans, le surcroît est de 388 k€ HT ; à sept et dix ans, il est entièrement financé.

Formulation proposée : « Nous disposons d’un repère externe de programme et d’un catalogue de travaux Make. Leurs périmètres ne sont pas encore suffisamment rapprochés pour affirmer une économie d’intégration. Nous testons l’opportunité sur 10 988 k€ HT, sans anticiper un gain d’équipe non démontré. La poursuite du cadrage doit rapprocher les livrables, volumes et responsabilités sur la carte métier avant de remplacer cette hypothèse par une estimation FLOW. »

## Contrôles et reproductibilité

Le [script d’audit](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/audits/2026-10-27-integration-make-calcul.py>) reconstruit les trois contrepoints par JH et profils, vérifie leur égalité au centime avec le moteur, reconstitue le retrait SAP et calcule les sensibilités et horizons sans écrire dans les sources. Les [preuves JSON](<C:/Users/laure/OneDrive/Documents/ChatGPT/Estimation coût délai ERP 2/audits/2026-10-27-integration-make-preuves.json>) contiennent les treize lignes par option, hypothèses, rapprochements métier et empreintes des entrées. Le recalcul économique actif complet est identique aux résultats sauvegardés ; seule l’empreinte documentaire du glossaire diffère du témoin historique.

La lecture des tableaux Delaware a été contrôlée sur les pages PDF rendues ; les numéros de page de ce rapport sont les pages PDF, différents des folios imprimés. Une seconde divergence de source existe sur les JH internes : 13 393 imprimés contre 13 993 par somme des lignes. Elle n’a pas été utilisée pour inventer un coût interne ; ces contributions demeurent hors du budget externe comparé. Les sources et résultats actifs ont été préservés.
