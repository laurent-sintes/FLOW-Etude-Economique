# Simplification du modèle FLOW — réalisation

27 octobre 2026. Référence publiée : `be3bc9218528`. Serveur local redémarré en mode release sur le même port, sans modification du stockage des simulations.

## Résultat

Les chiffres sont conservés. Les neuf scénarios témoins donnent strictement les mêmes résultats, hors identifiant technique du modèle : cinq options, quatre horizons, annuités, responsabilités, reste à financer et paramètres. Les objets `options` des deux exports YAML, diagnostic à quinze années de service et projection sur dix ans, sont également identiques à ceux sauvegardés avant la refonte.

Les preuves fournisseur et les captures métier sont conservées. Les questionnaires Microsoft et SAP restent accessibles. Les copies retirées ont été comparées par SHA-256 à leur exemplaire conservé.

## Changements du modèle

- Retrait des 195 lignes Core CSF remplacées, des six anciennes données Core et des schémas/validateurs associés. La grille métier n’exige plus leur correspondance historique.
- Retrait des anciens scores dans les catalogues de cycle. Conservation des activités, rôles, livrables, prix, inclusions et preuves ; contrôles utiles regroupés dans `validate_cycle.py`, sans registre de noms dans AGENTS.
- Remplacement des unités de maintenance écrasées par des références à leur propriétaire. Les mêmes travaux compilés alimentent transition et service stabilisé.
- Volumes N1 et escalades dérivés des entrées ; contexte du déploiement référencé, nombre d’unités dérivé. Contrôle des parts, rôles, longueurs, jalons et valeurs ; refus des clés YAML de classification inconnues.
- Classification des responsabilités et choix du niveau d’hébergement effectivement lus depuis le modèle. Correction de la preuve MAI-008 mal structurée. Les offres Buy restent groupées.
- Séparation du calcul sponsor et du diagnostic historique : `valuation()` prépare une annuité Make, cinq positions commerciales Microsoft et deux SAP. `calculate()` conserve le diagnostic à quinze ans pour les exports explicites, avec les mêmes formules.
- Publication fondée sur une liste explicite dans `config/publication.yaml`, complétée par les dépendances économiques. Déposer un ancien fichier dans un dossier ne l’ajoute plus automatiquement à la release.
- Alignement d’AGENTS et des README racine, modèle, outils et application : mêmes propriétaires, deux états, parcours Comparer / Simuler / Modèle, séparation référence/simulations, preuves et commandes.

Les deux exports YAML conservent leur adresse documentaire pour préserver les liens. Ils sont explicitement non éditables et ne sont pas lus comme entrées du calcul sponsor. Aucun nouveau système d’historisation n’a été créé.

## Retraits

| Catégorie | Fichiers retirés |
|---|---:|
| Anciens exports Excel de l’étude | 99 |
| Copies identiques de preuves | 20 |
| Ancien modèle CSF et contrôles associés | 10 |
| Paramètres et journaux de l’ancienne chaîne Excel | 16 |
| Historiques sans référence conservée | 104 |
| Ancien paquet ZIP, contenu retrouvé ou déjà retiré explicitement | 1 |
| **Total** | **250** |

Ces fichiers représentent **142 610 209 octets**, soit 142,6 Mo de fichiers retirés ; ce n’est pas une mesure de gain net sur disque. Le ZIP contenait notamment une copie d’un ancien export Excel ; ses 37 membres ont été rapprochés avant suppression.

Les archives encore citées sont conservées, dont l’analyse Synvance. Les classeurs reçus comme sources et les références publiques ne sont pas assimilés aux exports de l’étude. Certains répertoires vides peuvent rester lorsque Windows refuse leur retrait ; ils ne contiennent plus les fichiers supprimés.

## Vérification et publication

La suite finale a validé **111 tests Python**, les tests JavaScript de formats, navigation et reprise, le typage, le contenu et la construction de l’application. Les neuf scénarios ont été contrôlés avant publication puis directement sur la release figée. L’écart à dix ans est nul pour chacune des cinq options.

Les échecs initiaux des tests HTTP venaient des restrictions d’accès aux connexions locales et au répertoire temporaire système. Les tests de serveur utilisent maintenant un temporaire dans le workspace ; les tests HTTP ont été exécutés avec l’accès local requis, sans exclusion de tests.

Le [relevé de contrôles](2026-10-27-refonte-modele-controles.json) conserve le premier passage complet enregistré, à 110 tests, puis les vérifications directes de la release finale : identité, empreinte, neuf scénarios et égalité des exports. Le passage final à 111 tests inclut le contrôle ajouté du manifeste ; son résultat a été observé lors de la commande complète de publication. Le fichier partagé `tmp/check-model-last.json` peut être remplacé par un contrôle ultérieur et ne sert pas de preuve stable de cette opération.

## Pièces de contrôle et récupération

- [Témoin des neuf scénarios](2026-10-27-refonte-modele-parite.json).
- [Reçu détaillé des retraits](2026-10-27-refonte-modele-retraits.json) : chemins, tailles, empreintes, motifs et exemplaires conservés.
- [Contrôles et vérification de la release](2026-10-27-refonte-modele-controles.json).
- `tmp/model-refactor-recovery.zip` : sauvegarde ponctuelle des fichiers textuels avant refonte. Elle ne contient aucun ancien export Excel. Une récupération éventuelle porte sur un fichier choisi, sans réactiver tout l’ancien modèle.

Les audits précédents décrivent leur état daté. Leurs scripts et anciens chemins ne sont pas des contrôles du modèle courant. Aucun commit ni push n’a été réalisé.
