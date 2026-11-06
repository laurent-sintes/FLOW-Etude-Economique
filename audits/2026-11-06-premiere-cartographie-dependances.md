# Première cartographie des dépendances

6 novembre 2026. Construction Java/Spring de la première release majeure complète. Le périmètre de chaque équipe est celui de ses contributions de build actuelles. Aucun supplément de charge. Intégration est Enabling et ne fournit pas de release bloquante. Aucun calendrier, aucune charge d’intégration et aucune répartition MCO ne sont créés.

## Méthode d’évaluation

Les liens sont évalués à partir des missions, des contrats partagés, des postes MDM, des fonctions transverses et des propriétaires de financement. Les pièces OSS éclairent les mécanismes réutilisables et les frontières, pas le pourcentage de disponibilité. Les contraintes sont des hypothèses explicites de séquencement.

PaaS : 20 % suppose dépôt, CI minimale, environnement et moyens de test utilisables. Autres fournisseurs : 30 % suppose contrats versionnés, simulateurs et données de test. Ces conditions autorisent seulement les travaux concernés. La conception indépendante peut précéder ce seuil. Les taux ne sont ni du temps écoulé ni des JH consommés. Leur répartition précise par livrable restera à décomposer pour calculer une roadmap.

Production : la première version utilise 100 % de la release initiale complète du fournisseur, qualifiée et disponible en production, conformément à la définition de release validée. Toutes les conditions entrantes se cumulent. La disponibilité des seuls sous-services nécessaires pourra faire l’objet d’une décomposition ultérieure, sans déplacer silencieusement le dénominateur.

## Choix structurants

- PaaS fournit les moyens de réalisation à toutes les équipes produit.
- Plateforme MDM consomme les mécanismes communs de Case Management pour ses parcours de stewardship. Son stockage peut être développé indépendamment.
- Référentiels consomme le MDM et fournit les contrats de références aux traitements de stock, de planification, d’achat et de services.
- Inventory / Availability fournit les faits et contrats de disponibilité à la planification et aux commandes des canaux.
- Sourcing & Procurement porte le socle partagé des commandes typées consommé par B2C et Wholesale.
- Services fournit les contrats de fulfillment aux deux canaux.
- Portal consomme les tâches de Case Management et les contrats des canaux pour ses XP APIs et parcours UI.

Les dépendances opérationnelles de planification vers offres de services ou commandes ne deviennent pas automatiquement des blocages de démarrage. Les contrats peuvent être conçus ensemble. Cette première carte n’ajoute pas une réciprocité à chaque interaction métier. Les dépendances de sécurité des domaines vers Portal ne sont pas ajoutées sans distinguer bibliothèques, contrôles de domaine et passerelle d’accès, ce qui évite de confondre responsabilité de sécurité et obligation de livrer tout Portal avant les domaines.

## Contrôles

Références d’équipes et de releases, pourcentages, pièces, doublons et dépendances réflexives contrôlés. Les cycles de mise en production à 100 % sont rejetés : il faudrait expliciter une livraison groupée ou scinder les releases. Les cycles de contrats partiels ne sont pas assimilés automatiquement à un blocage. Les charges sont dérivées des contributions courantes et conservées, sans conversion JH/délai.

Autorité : `source/dependances-release.yaml`. Métamodèle : `source/fondamentaux.yaml`. Projection Python : `tools/release_dependencies.py`. Les critères précis et preuves sont accessibles depuis chaque relation.
