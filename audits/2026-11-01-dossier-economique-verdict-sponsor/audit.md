# Audit du dossier économique côté sponsor après les clarifications

**Oui, les coûts modélisés et les écarts sont désormais compréhensibles sans explication orale. Le dossier permet de préparer un choix d’option. Le financement complet et la prochaine tranche restent à établir, et cette limite est visible.** Les trois pages ont chacune un rôle clair. Une retouche mobile reste à faire, sans nouvelle réorganisation.

| Question du sponsor | Verdict et réponse disponible |
| --- | --- |
| Combien coûte chaque option sur dix ans ? | Clair. Java 12 069 k€ HT, Microsoft 21 627 k€ HT, SAP 37 697 k€ HT. |
| Pourquoi ces écarts ? | Clair. Trois postes comparés, écarts avec Java et explications par option. Microsoft représente 9 558 k€ HT de plus et SAP 25 628 k€ HT de plus. |
| Quel montant jusqu’au service complet ? | Clair. Java 8 171 k€ HT au mois 78, Microsoft 7 620 au mois 44, SAP 16 851 au mois 36. |
| Faut-il additionner ces montants ? | Clair sur ordinateur. Les inclusions sont explicites. À trois ans, Java et Microsoft signalent une période de service complet plus longue que l’horizon choisi. |
| Que coûte une année ? | Clair. Base annuelle et dépense projetée sont distinctes. Le statut de l’année indique si elle comprend encore le projet. |
| Quelles hypothèses portent les chiffres ? | Clair. Calendrier Java provisoire, charges adoptées, bases fournisseur et volumes de cadrage sont distingués. Aucun champ ne permet de modifier les hypothèses. |
| Que faut-il financer ? | Compréhensible sur le périmètre chiffré. Dépenses de projet, abonnements avant service complet et fonctionnement sont identifiés. Les dépenses hors périmètre sont nommées. |
| Quelle somme autoriser maintenant ? | Pas encore disponible. Le montant et le périmètre de la prochaine tranche ne sont pas établis. L’application le dit explicitement. |

**Les deux constats précédents sont résolus.** La mention « Ces repères ne s’additionnent pas » est placée près des montants. Les dépenses jusqu’au service complet et l’annuité projetée sont reliées au cumul. La définition des dépenses avant service complet est revenue près du bon repère. La base annuelle est présentée comme une référence à ne pas ajouter au cumul.

La conclusion comparative énonce les constats utiles. Java présente le cumul le plus faible dans la référence. Microsoft demande moins de dépenses pour atteindre le service complet, plus tôt que Java. SAP présente le cumul le plus élevé, avec la Finance conservée dans l’offre. Le calendrier explique que dix ans de dépenses ne représentent pas dix ans de service complet pour chaque option. Le dossier n’assimile donc pas automatiquement le moindre cumul à la meilleure option.

**Le financement encore à instruire est un travail de chiffrage et d’arbitrage.** Le temps des équipes internes, la transformation et le maintien ou retrait de l’ancien SI restent à dimensionner selon chaque trajectoire. Il faut distinguer la mobilisation de ressources déjà financées des dépenses supplémentaires. Les périmètres comparables et les contrats finaux restent aussi à confirmer. La prochaine tranche exige un périmètre, des livrables, des critères d’acceptation et un montant. Une amélioration de présentation ne peut pas fournir ces données.

**MOB 01 — Priorité 2 — Retour à la ligne des légendes mobiles.** À 390 × 844, les trois cartes restent adjacentes et leurs principaux montants sont lisibles. Mais « Déjà compris dans le cumul » dépasse de sa colonne. Le texte mesure 125 pixels pour une largeur disponible de 90 pixels, avec `white-space: nowrap`. Cela rapproche les mentions des cartes voisines et tronque visuellement la dernière. La règle `.eco-card-funding small` dans `app/src/economicDossier.css:122` touche aussi ces légendes. Autoriser leur retour à la ligne tout en gardant les montants et unités insécables suffit. Aucun débordement horizontal global n’a été constaté. [Capture mobile](comparaison-mobile.png).

Les vérifications portent sur les trois pages, les trois options dans le détail des coûts et les horizons trois et dix ans dans le navigateur. Les passages entre pages conservent l’horizon et l’option. Les hypothèses présentent zéro champ modifiable. Aucun avertissement ni erreur de console n’a été observé. Les **39 rapprochements arithmétiques passent** sur les données livrées pour les trois options et les horizons trois, cinq, sept et dix ans. Il s’agit d’une relecture experte, sans entretien de compréhension avec le sponsor ni nouvelle validation des devis ou hypothèses.

Modèle **01/11/2026 · n° 1**. Livraison locale `125705565ec11ef3830d20fdc4bff4a47099fbbfd34e8469d39e594a4784c5de`. Application, paramètres et modèle inchangés pendant cet audit. Les données et mesures sont conservées dans [evidence.json](evidence.json).
