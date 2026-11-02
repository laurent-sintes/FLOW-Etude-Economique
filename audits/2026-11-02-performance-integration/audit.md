# Audit de performance de l’intégration FLOW

Le coût principal observé vient du processus d’intégration et de sa validation trop large. Le chargement du modèle ajoute une lenteur réelle. Les corrections ci-dessous sont appliquées sans modification du chiffrage ni des règles économiques.

## Mesures

| Opération | Mesure avant | Mesure après / constat |
|---|---:|---:|
| Chargement complet Study, médiane locale | 12.26 s | 9.39 s, soit −23.4 % |
| Dernière campagne d’intégration | 424 tests, 694,188 s | Plan ciblé proposé : 137 tests, durée non mesurée |
| Préparation d’une livraison inchangée | Une modification de tests pouvait invalider le cache | 1.35 s avec cache vérifié |
| Reconstruction complète pendant cet audit | Pas de mesure comparable avant | 41.05 s observées, avec un contrôle ciblé exécuté en parallèle |

Les deux mesures de chargement par version sont exécutées dans un même processus, dans l’ordre avant/après/après/avant. Chaque Study recharge une session indépendante. L’ancien lecteur JSON via YAML et l’ancienne projection de la cartographie sont restaurés uniquement par des substitutions temporaires dans le processus de mesure. Les sources sur disque ne sont pas réécrites. Les résultats financiers et paramètres sont comparés à la référence à chaque passage. Voir [benchmark.py](benchmark.py) et [benchmark.json](benchmark.json).

Ces mesures portent sur le poste local, pas sur le démarrage Pyodide du navigateur. Elles ne donnent pas une durée garantie d’intégration complète. Le plan de 137 tests n’a pas été chronométré et ne remplace pas la validation complète de CI ou de Git.

## Causes et corrections

1. **Sélection de tests trop large.** La propagation par imports sélectionnait presque tout le projet, dont les tests Git et HTTP. La dernière campagne a consommé 11 min 34 s, dont 681 s dans Python. Ajout de `check_dev --targeted --tests ...` : sélection explicite des domaines concernés, maintien des contrats financiers obligatoires pour les changements dans source/config et rapport du mode réellement utilisé. Le mode exige des tests nommés. Le comportement par défaut et les validations complètes restent disponibles.

2. **Exécution en doublon.** Un module et une de ses méthodes pouvaient être sélectionnés ensemble. Le sélecteur retire maintenant les méthodes déjà comprises dans un module ou une classe sélectionnée. Des régressions vérifient cette déduplication.

3. **Lecture des JSON par un parseur YAML.** Les grosses preuves JSON passaient dans la construction générale YAML. Utilisation du lecteur JSON natif pour ces fichiers, avec rejet des clés dupliquées, y compris imbriquées, et des valeurs non finies. Les documents YAML gardent leur lecteur existant. Les 92 preuves JSON actives ont été comparées aux résultats de l’ancien lecteur : données égales.

4. **Copies répétées de la cartographie complète.** Les contrôles de rattachement avaient besoin des seuls identifiants et types, mais demandaient régulièrement le document natif entier. Ajout d’une petite projection mémorisée pour ces contrôles. Les copies isolées des données publiques, les empreintes et le cloisonnement par session restent conservés.

5. **Cache de livraison trop sensible.** Les modifications de tests, de compétences, de configuration CI ou des instructions de travail pouvaient déclencher une reconstruction du site. Ces fichiers sont exclus des entrées de livraison lorsqu’ils ne sont pas publiés explicitement. Un fichier de test explicitement déclaré dans les sources ou la publication reste suivi. Les changements de code, données, preuves, interface et ressources restent invalidants. Les cas de corruption, de disparition de fichiers et de modification concurrente restent contrôlés.

6. **Conduite des opérations.** J’ai lancé une construction avant d’avoir terminé les modifications, ce qui a provoqué son rejet puis une relance. Ce rejet de cohérence était correct. Je conserve désormais l’ordre suivant : terminer les modifications, vérifier le plan de tests, exécuter les contrôles ciblés, puis construire une seule livraison cohérente et vérifier le navigateur. Une modification des seuls tests après cette étape ne nécessite plus de reconstruire l’application.

7. **Témoins historiques mal rattachés.** Deux contrôles attendaient que la décision Master Data active reste identique à son ancienne version. Ils ont été adaptés pendant l’adoption précédente pour comparer les anciennes décisions à leurs preuves figées et préserver les contrôles du référentiel courant. Les modifications métier autorisées ne doivent pas être traitées comme une régression historique.

## Vérifications effectuées

- Paramètres et résultats financiers identiques à la référence avant optimisation, pour les cinq options et tous leurs horizons et annuités. Seule l’empreinte technique du moteur change.
- 92 preuves JSON équivalentes à celles produites par le lecteur précédent.
- Tests ciblés du sélecteur, des caches, des refus de données incohérentes, de l’isolation, de l’adoption des livrables et de la préparation des calculs. 42 tests réussis dans le premier passage en 57,3 s. Une erreur de nom de test dans la commande a été rectifiée puis le contrôle exact du cache d’export a réussi séparément en 11,8 s. Aucun échec fonctionnel restant dans ce périmètre.
- Le contrôle des sources modifiées et des fichiers corrompus reste actif. Les simulations ne lisent toujours aucun fichier et les sessions chargées restent isolées.
- Livraison locale reconstruite. La révision servie au navigateur correspond à celle de delivery.json. Affichage vérifié : 7 630 JH, modèle du 2 novembre 2026 n° 5.
- Les budgets, tarifs, calendriers, capacités métier et preuves de calcul historiques ne sont pas modifiés. Aucun commit ni push.

## Limites et prochaine simplification

Le chargement complet reste d’environ neuf secondes sur ce poste. Les copies de grandes structures et le volume documentaire restent visibles dans le profil. Leur suppression générale mettrait en jeu l’isolation et n’a pas été tentée sans besoin mesuré supplémentaire.

L’adoption reste répartie entre décisions, contrats, ventilation des rôles, classement des fonctions et preuves. Une commande transactionnelle unique d’adoption, avec préparation et vérifications avant écriture, permettrait de supprimer les scripts ponctuels et une partie des erreurs manuelles. Elle n’est pas implémentée dans cet audit. Les méthodes déjà présentes doivent être réutilisées pour les prochaines modifications de montants, sans nouvelle logique Python si la méthode ne change pas.

Les assertions de montants actifs restent dispersées dans plusieurs tests. Les regrouper autour de décisions figées clairement identifiées réduirait les retouches manuelles, en conservant séparément des exemples arithmétiques indépendants.

## Pièces

- [Profil avant](profile-before.json), [profil après](profile-after.json), [attribution des copies](copy-before.json).
- [Mesures comparables de chargement](benchmark.json), [analyse du processus précédent](workflow.json), [livraison et cache](delivery.json).
- Profils cProfile bruts : study-before.prof et study-after.prof.
