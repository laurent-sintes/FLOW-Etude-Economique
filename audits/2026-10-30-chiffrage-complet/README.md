# Chiffrage complet Java/Spring — étude d’opportunité
Proposition : 4 160 JH bruts, dont 1 940 déjà retenus et 2 220 nouveaux.
Les 280 JH communs sont intégrés : ne pas les ajouter.
88/88 capacités chiffrées pour l’étude ; 16/88 adoptées dans le modèle actif.
Lire synthese.html, audit-final.json, stability.json et sensitivity.json.
Les rôles et délais des neuf unités figurent dans jh-par-role.csv.

## Reproduction depuis la racine du projet
Avec les dépendances Python du modèle :
1. python audits/2026-10-30-chiffrage-complet/calculate-05.py 5
2. python audits/2026-10-30-chiffrage-complet/calculate-06-07.py 6
3. python audits/2026-10-30-chiffrage-complet/calculate-06-07.py 7
4. python audits/2026-10-30-chiffrage-complet/calculate.py 8
5. python audits/2026-10-30-chiffrage-complet/verify.py
6. python audits/2026-10-30-chiffrage-complet/report.py

prepare.py, review6.py, review7.py et review8.py reconstruisent les entrées séquentiellement depuis les preuves précédentes. Les sorties sont déjà figées ; ne pas les écraser pour modifier une hypothèse.
Les règles sont celles du métamodèle canonique. Le bilan YAML est un résultat d’audit, pas un autre métamodèle.
La stabilité ne prouve pas la précision prédictive : aucun bilan réel n’est disponible.
