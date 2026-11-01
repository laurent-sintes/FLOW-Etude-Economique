# Réorganisation des études préalables

La section **Études préalables** dispose d’une [vue d’ensemble](http://127.0.0.1:8766/#preetudes), d’un menu gauche à un seul niveau et d’un fil de navigation. Les rubriques sont accessibles par les intercalaires en haut des pages. Les sous-menus imbriqués ont été retirés à la demande de l’utilisateur. Chaque sujet présente un encart « Ce qu’on en retient ». Les panneaux génériques de provenance sont retirés. Les dates et les sources restent près des faits.

La comparaison des solutions de marché regroupe les 28 Business Areas sous leurs neuf sous-domaines natifs. Elle conserve un seul filtre de sous-domaine et propose une lecture en cartes sur mobile. Les six fiches présentent les fonctions et les mesures de code, sans effort, conversion COCOMO ni prix calculé. Les références de méthode restent dans le Framework. OSS est expliqué au premier usage et défini dans le glossaire.

Les tarifs et achats se lisent sans filtre, avec des liens directs par technologie et par sujet. L’adresse [Tarifs Java](http://127.0.0.1:8766/#preetude-couts?focus=rates-java-spring) ouvre la section correspondante. Les projets gardent leurs plages de référence et disposent d’un sommaire des fiches. La [productivité du développement](http://127.0.0.1:8766/#preetude-productivite) a sa propre entrée. Son ancienne adresse reste compatible.

**Java/Spring est la seule voie Make visible. Microsoft et SAP restent les alternatives Buy.** .NET et Rust sont retirés des choix, des tarifs spécifiques et des comparaisons courantes. Le moteur conserve les paramètres historiques des sauvegardes. Une session sélectionnant une option retirée reste récupérable, sans transformation en scénario Java.

## Vérifications

Les budgets et paramètres de référence complets sont identiques au témoin conservé avant les changements. Une simulation dans le navigateur a retrouvé les résultats du moteur Python pour les trois options visibles. Le paramètre utilisé pour cette vérification a été rétabli.

Le contrôle initial a exécuté 392 tests Python en 576.3 secondes au total. Un lien de source du glossaire manquait dans le catalogue des documents. Le catalogue a été corrigé. Le contrôle concerné et les invariants touchés ont ensuite passé dans un lot de 57 tests Python. Les 65 tests du client, TypeScript et le contrôle des textes passent également. Ce dernier lot a duré 96.5 secondes.

Le navigateur a été vérifié sur ordinateur et en largeur mobile de 390 px : navigation, focus, accès au tarif Java, regroupement métier, six fiches sans estimations et ancien lien de productivité. Les contrôles sont ceux du développement local, sans certification complète de release.

Version statique vérifiée : `652f7c37611a8d8131923063e0b50431c7d94cde48afef179e35b7828d7e38ee`.

Le [compte rendu technique](C:/Dev/FLOW-Etude-Economique/tmp/prestudy-reorg/report.json) conserve les résultats et la parité. L’[audit initial](C:/Dev/FLOW-Etude-Economique/audits/2026-11-01-etudes-prealables-ui-ux/audit.md) décrit l’état observé avant cette réorganisation.

Le retrait des sous-menus a passé une nouvelle vérification : 49 tests Python, 65 tests du client, TypeScript et contrôle du contenu, en 83,7 secondes. Le menu gauche sans liens enfants et les intercalaires ont été contrôlés sur ordinateur et mobile.
