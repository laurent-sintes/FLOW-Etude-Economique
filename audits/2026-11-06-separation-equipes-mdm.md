# Séparation des équipes MDM

Décision validée par l’utilisateur le 6 novembre 2026.

Plateforme MDM (Platform) possède le moteur et les outils génériques. Référentiels (Stream-aligned, identifiant conservé `master-data`) possède les familles, leurs règles et Operational References. Les deux équipes restent propriétaires de leurs composants pendant la construction, l’intégration et le MCO.

## Ventilation du build

| Poste | Plateforme MDM | Référentiels |
| --- | ---: | ---: |
| Moteur | 2 275 JH | 0 |
| Interfaces génériques, studio et administration | 940 JH | 0 |
| Familles | 0 | 730 JH |
| Qualification transverse | 100 JH | 100 JH |
| Operational References | 0 | 400 JH |
| Total | 3 315 JH | 1 230 JH |

Sources des postes : `audits/2026-11-05-mdm-studio-plugins/engineering.json` et `source/revision-master-data.yaml`. Le partage égal de la qualification est la nouvelle clé validée : robustesse technique, résilience et performance côté plateforme, cohérence inter-familles côté référentiels. La QA des composants reste dans leurs postes.

La clé `build-master-data` de `source/abaque-ventilation.yaml` ventile 3 315 / 4 145 et 830 / 4 145. Les pourcentages sont conservés à la précision du modèle, sans appliquer les pourcentages d’affichage arrondis. Les rôles et leurs tarifs restent inchangés. Le moteur existant valorise leurs parts et conserve les centimes. Operational References reste affecté intégralement à Référentiels. Aucun nouveau budget.

## Responsabilités et interactions

Les capacités natives restent immuables. La contribution de Plateforme MDM est indirecte et technique, la responsabilité métier de Référentiels est directe. Le périmètre de capacités ne constitue pas une clé de ventilation.

La plateforme est placée dans les moteurs partagés, Référentiels dans les données et services métier. Le mode cible est X-as-a-Service. La collaboration est temporaire pour les premières familles et les besoins structurants, jusqu’à l’autonomie de Référentiels. PaaS fournit les outils communs. Intégration accompagne temporairement les contrats et tests intégrés.

L’intégration n’est pas chiffrée ni ventilée. Aucune clé de build n’est propagée automatiquement au MCO ou aux autres enveloppes. Les responsabilités durables ne constituent pas une estimation de capacité ou d’effectifs.
