# Classement du périmètre par domaine métier — 5 novembre 2026

La séparation native est respectée : Master Data comprend 33 capacités et la gestion de la chaîne logistique 83. Operational References reste dans le domaine SCM, même si son équipe contributrice est Master Data.

La présentation des charges, des coûts et des travaux est maintenant classée par domaine. Le métamodèle distingue domaine métier, équipe contributrice et Core Domain / Support. Les rattachements directs suivent la hiérarchie native. Le classement fonctionnel documenté des ateliers logistiques complète les travaux sans capacités natives.

| Construction générique Java/Spring | JH affectés | Coût affecté, euros HT |
| --- | ---: | ---: |
| Master Data | 2 670 | 1 736 160 |
| Gestion de la chaîne logistique, dont Operational References et ateliers logistiques | 5 890 | 3 804 095 |
| Socle technique commun à ventiler | 540 | 360 495 |
| Total retenu | 9 100 | 5 900 750 |

Le coût complet des deux domaines exige une clé documentée pour répartir le socle commun. Le modèle conserve ces coûts complets à null tant que cette clé manque. Aucune répartition selon le nombre de capacités ou selon le nom de l’équipe n’est présumée.

L’intégration, le fonctionnement et les contrats Buy conservent leurs enveloppes. Leur ventilation par domaine reste à renseigner. Les totaux annuels et initiaux ne sont pas additionnés sans horizon.

La cartographie des préétudes garde sa présentation métier, actualisée et regroupée par domaine, sans coûts ni analyse financière. Les anciennes captures et les preuves d’adoption restent intactes.

Les comparaisons de Master Data et d’Operational References sur l’ancien périmètre sont conservées comme preuves historiques. Elles ne sont plus additionnées deux fois dans le total comparatif courant. Les charges retenues et les simulations ne changent pas.

Les contrôles ciblés couvrent 175 tests Python distincts, tous passants après reprises ciblées des assertions de l’ancien périmètre. TypeScript, contrôles JavaScript et règles de contenu passent. Le navigateur est vérifié à 1440 et 390 pixels. Les huit simulations exécutées avec Python/Pyodide sont identiques à l’oracle Python. Les reçus, y compris les essais en échec, sont référencés dans verification.json. Il ne s’agit pas d’une certification de la suite complète.
