# Revue des profils et du pilotage

Le tarif « expert » de chaque option couvre développement, intégration de flux et support N3. L'intégrateur iPaaS est inclus dans l'activité d'intégration au même tarif. La revue suivante a ajouté un tarif QA et un tarif architecte par option dans `source/stacks/`. Les JH de qualification identifiés dans les travaux du Core System sont valorisés au tarif QA ; les JH d'architecture transverse déjà identifiés sont valorisés au tarif architecte. Aucune journée supplémentaire n'est créée.

L'ancienne provision commune de 900 € HT/JH pour l'architecte a été remplacée par les cinq références propres aux options. Le support utilisateur N1 reste commun aux cinq options à 425 € HT/JH.

| Option | QA, € HT/JH | Architecte, € HT/JH | État de preuve |
|---|---:|---:|---|
| Java / Spring | 550 | 900 | Références généralistes ; pas de prime technologique ajoutée. |
| .NET | 550 | 900 | Même choix que Java faute d'écart établi. |
| Rust | 600 | 1 000 | Majoration de cadrage à confirmer. |
| Microsoft / K3 | 600 | 1 000 | Majoration de cadrage produit à confirmer. |
| SAP | 650 | 1 100 | Références QA généralistes et spécialistes SAP ; périmètre Fashion à confirmer. |

Le [baromètre Silkhom 2025](https://www.silkhom.com/barometre-des-tjm-informatique-electronique-digital/) indique 530–700 € par jour pour un ingénieur QA senior à Paris. La [grille ForTeam](https://www.forteam-it.com/ressources/grille-tjm) donne 850–1 000 € pour Architecture SI / Tech Lead confirmé, 920–1 180 € pour senior/expert et 950–1 250 € pour SAP senior/expert. Ces sources ne publient pas cinq tarifs QA et architecte exactement comparables au périmètre FLOW : les écarts Rust, Microsoft et SAP restent des hypothèses de cadrage, marquées de preuve faible dans les fiches. Les montants sont des références freelance directes, pas des prix ESN ou des devis.

Comparés à la release précédente, les écarts de coût cumulé à 10 ans sont : Java 0 €, .NET −263 602 €, Rust −593 709 €, Microsoft 0 € et SAP 0 €. Les cinq options sont réconciliées aux horizons 3/5/7/10 ans. Java ne change pas car son QA est au même tarif que l'expert et son architecte reste à 900 €. Les offres Buy ne changent pas à ces horizons : les travaux concernés sont inclus dans les prix groupés, et les tarifs QA/architecte servent uniquement aux travaux clients explicitement identifiés hors offre.

Le pilotage technique est déjà paramétré dans `source/calibration-couts.yaml#pilotage` : 8 % de la construction Make, 10 % de l'intégration Make, 8 % de la maintenance estimée et 10 % des compléments Buy. L'assiette est la prestation technique estimée, sans licences, cloud ou forfaits RFI. `source/deploiement-groupe.yaml#deploiement/coordination_technique_pct` ajoute 10 % à la réalisation des paquets locaux Make. Ces paramètres existaient dans le calcul mais manquaient dans la page Méthode.

Une exception est explicite dans le modèle : le pilotage du programme Groupe Make suit la durée centrale de 30 mois, avec 0,5 ETP de direction et 1 ETP de coordination, aux tarifs et à la convention de jours du fichier `source/deploiement-groupe.yaml#pilotage`. Cette charge est distincte des pourcentages de pilotage technique. La convertir en pourcentage changerait les cinq comparaisons et demande une décision de modélisation et une nouvelle réconciliation économique.
