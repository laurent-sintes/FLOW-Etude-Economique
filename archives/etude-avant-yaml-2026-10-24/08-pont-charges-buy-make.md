> **Historique — retiré de la base active le 24 octobre 2026.** Les hypothèses et résultats de cette note sont remplacés par le [modèle YAML actuel](../../source/README.md).

![Logo eXalt](<../../assets/exalt-logo.png>)



**Laurent Sintès** · 20 octobre 2026



---



# Utiliser les propositions Buy dans l'estimation FLOW



## Ce qui est comparable



Les réponses SAP/Delaware et Dynamics 365 + K3/Avanade de 2025 sont des références d'**implémentation de produits existants**. FLOW construit un produit opérationnel configurable puis l'intègre au SI. Les deux approches financent des activités communes : configuration des règles et données, interfaces, sécurité, tests, reprise et mise en service.



Les produits proposés couvrent déjà achats, commandes, stock, promesse et allocation. Le RFI ne correspond cependant pas exactement au périmètre FLOW. Il inclut des fonctions hors cible et n'établit pas la couverture détaillée de toutes les exceptions et exigences de configuration. L'[analyse des pièces](<07-analyse-synvance.md>) distingue les déclarations fournisseur des points à confirmer.



## Règles de rapprochement



| Nature de travail | FLOW Make | Références Buy |

| --- | --- | --- |

| Construire le cœur logiciel | Core FLOW, y compris les développements métier propres au groupe. | 0 € de construction du produit éditeur dans le projet. |

| Configurer le contexte métier | Règles, politiques, données et paramètres initiaux. | Configuration du progiciel et adaptations sans code. |

| Raccorder flux et sécurité | API, événements, transformations, contrôles et raccordements SI. | Interfaces et raccordements autour du progiciel. |

| Développer les spécifiques | Compris dans le Core ; pas de supplément. | Extensions codées du produit acheté. |

| Qualifier et mettre en service | Tests, reprise, préparation et bascule. | Tests, reprise, préparation et déploiements. |



Les tests et le pilotage propres à une fonction restent dans sa charge. Les postes distincts sont isolés pour la présentation, sans ajouter une seconde enveloppe. Les coûts de fonctionnement et les licences sont calculés séparément.



## Données de référence retenues



**SAP : 14 640 JH intégrateur**, dont 1 319 JH de spécifiques et 1 467 JH d'interfaces, déjà compris dans le total. Les 204 JH de conversions et les 421 JH de mise à niveau initiale sont également inclus. Les propositions regroupent le reste des travaux de conception, configuration, tests et pilotage : ce solde ne peut pas être appelé configuration sourcée.



**Microsoft : 2 300 JH pour le pilote retenu**, répartis en 630 JH de configuration, 460 d'interfaces, 230 de spécifiques, 380 de gouvernance et 600 de tests/mise en service. L'hypothèse de quatre autres pôles de 400 JH donne 3 900 JH avant retrait hors FLOW. L'équivalence entre un pôle et une unité de déploiement reste une hypothèse.



Les contributions internes ne sont pas incluses automatiquement dans les prix comparés. Seules les tâches techniques explicitement transférées au prestataire par le modèle sont ajoutées au budget fournisseur. Le soutien métier et la gouvernance internes Beaumanoir restent non chiffrés.



## Application au dossier courant



La référence FLOW reste **32 100 JH et 24,075 M€ HT**. Le total d'un projet Buy n'est pas ajouté à cette estimation : les postes FLOW comprennent déjà configuration et intégration.



Pour comparer les budgets SAP/Microsoft à FLOW, la [note détaillée](<15-rapprochement-buy-france.md>) procède dans cet ordre : conserver le prix RFI, calculer les jours aux tarifs France retenus, retirer les travaux hors cible, ajouter seulement les compléments identifiés et les tâches techniques confiées au prestataire. Les sept compléments fonctionnels sont estimés par fonctions et unités, sans pourcentage du Make.



Les [clés de présentation](<../../tools/flow_cost_structure.json>) répartissent ensuite les mêmes coûts entre Flux, Business, Spécifiques et pilotage/tests/reprises/mise en service. Les parties non ventilées par le fournisseur sont des **hypothèses de l'étude**. Les totaux restent **17,132679 M€ SAP** et **5,73615 M€ Microsoft**.



Les pièces sources comportent des contradictions arithmétiques SAP : 2 M€ entre le total budgétaire imprimé et la somme des lignes, et 600 JH sur la contribution interne. Ces écarts sont conservés et expliqués dans la note détaillée ; ils ne deviennent pas des suppléments présumés.



L'ancienne méthode est conservée dans les [archives](<../methodes-remplacees/2026-10-20/08-pont-charges-buy-make.md>). Pour le calcul courant, utiliser les [charges FLOW](<06-premier-ordre-de-grandeur-effort.md>), leur [répartition](<09-abaques-repartition.md>) et le [modèle sur quinze ans](<12-modele-tco-buy-make.md>).

