# Mise en œuvre de l’audit final du Framework

28 octobre 2026 — corrections locales sur `main`, à partir du commit `094a9354d3a0d7ae53a415fda036dcda4a85dafd`.

**Les préconisations sont appliquées dans l’ordre de l’audit. QA est conservé, conformément à la décision de l’utilisateur. Les chiffres, hypothèses et contrats de simulation sont inchangés. Aucun bloc à déplier n’a été ajouté.**

## Corrections réalisées

1. **Intégration Make.** La page « Des charges au budget » distingue les travaux communs, les déploiements et leurs deux assiettes de coordination. La formule complète inclut le programme et les prestations partagées avant réception. Le texte explique le dimensionnement des interfaces, la migration, les substitutions et la différence entre le poste budgétaire d’intégration et toutes les dépenses consommées pendant cette période.
2. **MCO du Core System pendant la transition.** La page de fonctionnement présente les corrections et campagnes de qualification, leur valorisation, leur coordination et les facteurs de service. La période commence au début de l’intégration. Les services partagés et locaux gardent leurs fenêtres propres ; les prestations avant réception et les règles de financement unique sont explicitées. Le classement Build/Run reste distinct du calcul.
3. **Accessibilité.** Le menu mobile reçoit le focus à l’ouverture, gère Échap, restitue le focus et se ferme lorsque le clavier le quitte. Il reste non modal. Le choix d’une page conduit à son titre. Le passage entre les largeurs mobile et ordinateur conserve un focus visible. Les fenêtres documentaires sont nommées par leur titre. Les régressions correspondantes sont intégrées au contrôle navigateur de la version statique.
4. **Buy et glossaire.** Les descriptions deviennent des règles conditionnelles : un contrat groupé compte une fois et une part non documentée reste inconnue. La définition canonique et son export sont alignés.
5. **COCOMO.** Le coefficient `a` et l’exposant `E` sont expliqués. Les coefficients retenus et les résultats restent dans le dossier économique.
6. **Lien vers les analyses.** Les Fondamentaux annoncent explicitement le passage au dossier économique, chapitre « Offres reçues ». La pièce d’analyse reste accessible depuis ce dossier. Synvance et la cartographie restent des entrants du Framework.
7. **Finition rédactionnelle.** Le libellé de la Vue d’ensemble est corrigé. QA est maintenu dans les pages ; cette préférence est inscrite dans `AGENTS.md`.

## Vérifications

- **247 tests Python réussis** dans la suite complète avec le témoin capturé avant modification : six scénarios préservés, aucun écart sur les cinq options. Les contrôles couvrent les projections et les contrats de reprise.
- Après les derniers ajustements de focus, **44 tests JavaScript**, TypeScript, contrôle de contenu et constructions locale/statique réussis. Les tests économiques complets restent valables : aucun contenu économique ni moteur n’a changé après leur passage.
- **Neuf réconciliations indépendantes** des formules explicitées sur les trois options Make et trois jeux de facteurs de service. Les contrôles ciblés de vocabulaire et du glossaire passent également.
- Les **sept pages** ont été relues à 1440 et 390 pixels : aucun accordéon ni débordement de page ou d’encart de formule. Les 35 destinations de sommaire, 17 tableaux défilables au clavier et 14 encarts de formule ont été contrôlés. Les captures des sections complétées ont été relues.
- **Treize contrôles d’accessibilité réussis** : ouverture, sortie, fermeture, navigation, redimensionnement et lecteur documentaire. Aucune erreur JavaScript ou HTTP dans ces parcours locaux.
- La version statique a passé les **treize routes à deux largeurs**, les six simulations exécutées par Python dans le navigateur, l’isolation de la référence, la sauvegarde et la reprise de session, les pièces YAML/Markdown/PDF et le traitement d’une preuve indisponible. Seule requête accessoire signalée : le favicon absent à la racine du serveur de prévisualisation.
- Les champs numériques et booléens des sources modifiées sont identiques à ceux du départ. Les moteurs économiques et le contrat de session sont inchangés octet pour octet.

## État livré

Le serveur local est actualisé et reste actif depuis `C:\Dev\FLOW-Etude-Economique`, sur [l’application locale](http://127.0.0.1:8766/#vision). Son état confirme le chargement des sources courantes. Le modèle économique conserve son identifiant `57d2e719ef05f5a653e7df1f0fa2ed37a0a05f5f8cc5fa05e509d807d5a45c79`.

La version statique a été construite et vérifiée localement. **Aucun commit, push ou déploiement GitHub Pages n’a été effectué.** L’instantané technique de release n’a pas été remplacé.

Les résultats détaillés sont conservés dans [le relevé des contrôles](2026-10-28-audit-final-framework-controles.json), avec [le témoin de parité initial](2026-10-28-final-framework-parite.json). L’[audit initial](2026-10-28-audit-final-framework.md) reste inchangé comme trace de la revue ; sa proposition de remplacement de QA est annulée par la décision utilisateur ci-dessus.
