![Logo eXalt](assets/exalt-logo.png)

**Laurent Sintès** · 20 octobre 2026

---

# Lire et modifier le classeur

## Une seule synthèse : Comparaison

**Comparaison est la page de décision.** Elle présente les trois options côte à côte, réalisation initiale, fonctionnement annuel moyen des années 6 à 15 et cumuls à 3, 5, 10 et 15 ans. Le graphique commun montre les dépenses cumulées et les jalons d'usage métier. Les hypothèses actives sont placées près des résultats.

Les feuilles **Prix Flow, Prix SAP et Prix Microsoft** sont conservées pour trois usages : justifier le budget initial, régler le calendrier et activer les options. Elles ne reproduisent plus une seconde comparaison des cumuls. Leurs prix annuels renvoient aux abaques propriétaires.

## Parcours de lecture

| Question | Feuille à ouvrir | Ce qu'on peut y modifier |
| --- | --- | --- |
| Combien et à quel horizon ? | **Comparaison** | Résultats liés ; liens vers les justificatifs. |
| Quels travaux initiaux, à quelles dates ? | **Prix Flow / SAP / Microsoft** | Budget initial, calendrier des livraisons et options. |
| Quel tarif et quelle inflation ? | **Prix unitaire Flow / SAP / Microsoft** | Prix par rôle, tarifs vendus, souscriptions et indexations. |
| Quelle activité annuelle est financée ? | **Service annuel** | Forfaits SAP et abaques FLOW/Microsoft, responsabilités et options ; statut des hypothèses explicite. |
| Quelles factures techniques s'ajoutent ? | **Plateformes et sortie** | Ressources FLOW, construction, CPI/crédit BTP, runtime externe Microsoft et option de sortie. |
| Qu'est-ce qui vient des offres ou manque au périmètre ? | **Passage Buy France** | Charges source, retraits hors FLOW, compléments et leur détail recalculable. |
| Quels travaux expliquent FLOW ? | **Charges Flow** | Quatorze postes et leurs charges de réalisation. |
| Comment sont répartis les coûts ? | **Structure coûts** | Clés Core/Flux/Business/Spécifiques/transverse, sans majoration des totaux. |
| Quelles conventions sont utilisées ? | **Paramètres** | Périodes, conversions, horizons et coefficients. |
| Comment passe-t-on du mois au cumul ? | **Calculs 15 ans**, **Trajectoire mensuelle**, **Coûts techniques mensuels**, **Licences mensuelles** | Calculs visibles, formules liées aux entrées ; détail des gels, proratas et jalons. |
| Où est la preuve d'une donnée ? | **Références** et **Sources** | Pièce/page, donnée et statut : source fournisseur, hypothèse ou couverture à confirmer. |

Les feuilles techniques restent visibles pour vérifier les calculs. Elles ne demandent pas au décideur de refaire le chemin complet : les liens depuis les résultats pointent vers les justifications utiles.

## Des mots et des unités stables

- **Réalisation initiale** : création du Core FLOW ou intégration des produits existants, plus travaux de mise en service et ressources de construction identifiées.
- **Maintenance et pilotage** : diagnostics, corrections et suivi du service ; tests de version selon la responsabilité de chaque solution.
- **Exploitation** : surveillance, rétablissement, fiabilité des échanges, procédures et reprise.
- **Évolutions métier** : toutes les demandes de changement du panier annuel. Les versions fonctionnelles FLOW sont un « dont », jamais une ligne supplémentaire au total.
- **Plateforme d'exécution** : ressources et services techniques facturés, séparés du travail humain.

Les quantités en **JH**, les **€/JH**, les **€/an**, les **M€** et les coefficients utilisent des formats distincts. Le terme MCO n'est plus utilisé pour désigner indistinctement toute la maintenance et l'exploitation.

## Modifier un paramètre sans recalcul manuel

Une donnée source a une cellule propriétaire ; ses réutilisations sont des renvois. La convention de 200 JH par personne et par an appartient à l'étude. Les tableaux de compléments Buy détaillent douze charges : les huit sous-totaux relevés par l'audit et quatre charges Microsoft supplémentaires. Dans **Passage Buy France, lignes 190 à 266**, les quantités sont en C, les JH par unité en E et les totaux calculés en G. Modifier une composante actualise le budget.

Les feuilles de prix unitaire reprennent les montants de **Service annuel**. Elles n'ajoutent aucun second forfait MCO. Les prix SAP RFI de 250/450/350 k€ restent des références identifiables, sans piloter le nominal. L'ancienne supervision Microsoft à 450 k€ et les suppléments MCO à 3 %/5 % ne sont plus utilisés.

## Conditions de lecture

SAP utilise les forfaits Delaware : **250 k€/an de MCO, 450 k€/an de supervision en horaires étendus et 350 k€/an d’évolutions**. FLOW et Microsoft restent estimés par activité en heures ouvrées. Les volumes des forfaits SAP ne sont pas documentés : **l’équivalence des niveaux de service et des capacités d’évolution n’est pas démontrée**. Les contributions internes sont exclues ; les options additionnelles restent inactives.

Les contrôles du fichier courant sont consignés dans [le journal de validation](14-audit-inflation-run-et-comparaison.md). L'[audit ayant motivé ces corrections](17-audit-version-v4.md) reste une photographie de la version précédente ; ses anciennes cellules, valeurs et empreintes ne servent pas de recette au nouveau fichier.
