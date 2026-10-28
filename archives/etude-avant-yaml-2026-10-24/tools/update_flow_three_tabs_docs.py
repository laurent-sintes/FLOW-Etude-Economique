from pathlib import Path
import json

root = Path(__file__).resolve().parent.parent
results = json.loads((root / 'tmp/three_tabs_results.json').read_text(encoding='utf-8'))
assert abs(results['flow']['headline'][-1] - 41961000) < .01
assert abs(results['sap']['headline'][-1] - 50693516.43702403) < .01
assert abs(results['ms']['headline'][-1] - 40967581.26793822) < .01
head = '![Logo eXalt](assets/exalt-logo.png)\n\n**Laurent Sintès** · 21 octobre 2026\n\n---\n\n'
book = 'outputs/01a1530f-f378-7fd1-9654-468c9b2141b6/FLOW_Make_abaques_et_prix_France_v4.xlsx'
table = '''| Coûts fournisseur HT | FLOW | SAP | Microsoft |
| --- | ---: | ---: | ---: |
| Réalisation initiale | 24,46 M€ | 17,13 M€ | 5,74 M€ |
| Fonctionnement annuel moyen, années 6–15 | 1,75 M€/an | 2,54 M€/an | 2,56 M€/an |
| Cumul à 3 ans | 14,58 M€ | 20,82 M€ | 10,53 M€ |
| Cumul à 5 ans | 24,46 M€ | 25,26 M€ | 15,34 M€ |
| Cumul à 10 ans | 33,21 M€ | 37,25 M€ | 27,59 M€ |
| **Cumul à 15 ans** | **41,96 M€** | **50,69 M€** | **40,97 M€** |
'''
(root / 'README.md').write_text(head + '''# FLOW — estimation économique

**Version du 21 octobre 2026 : le classeur comprend trois onglets, Comparaison, Hypothèses et Sources.** La méthode par capacités fournisseur est appliquée. Les budgets initiaux et les abonnements sont conservés ; le dimensionnement des services et leur démarrage sont explicites.

''' + table + f'''
**FLOW : 7 personnes-an de maintien en service et 2 d’évolutions à 750 €/JH. Microsoft : 6 + 2 à 850 €/JH.** Une personne-an représente 200 JH. SAP conserve les forfaits RFI : 250 k€ de MCO, 450 k€ de supervision et 350 k€ d’évolutions. Son équipe théorique n’alimente pas le total.

Sur quinze ans, l’écart FLOW–Microsoft est d’environ **1,0 M€ en faveur de Microsoft dans ces hypothèses**. Ce calcul ne démontre pas une économie à service contractuellement équivalent : les périmètres des forfaits SAP et les capacités supposées restent à confirmer. Aucun croisement de courbes n’est imposé.

## Accès au dossier

| Document | Usage |
| --- | --- |
| **[Classeur à trois onglets]({book})** | Comparaison 3/5/10/15 ans, graphique, hypothèses modifiables et calculs visibles. |
| [Note de décision](04-resultats-etude.md) | Résultats et écarts avant/après expliqués. |
| [Méthode](02-methode-estimation.md) | Service, responsabilités, choix d’équipe et limites. |
| [Guide du classeur](13-audit-classeur-excel.md) | Où lire, modifier et vérifier. |
| [Cahier des charges](01-cahier-des-charges.md) | Périmètre et configurabilité de FLOW. |
| [Effort FLOW](06-premier-ordre-de-grandeur-effort.md), [budget France](11-cout-nominal-minimum.md) | Origine du budget initial conservé. |
| [Synvance](07-analyse-synvance.md), [compléments Buy](15-rapprochement-buy-france.md) | Prix RFI, différences de périmètre et estimations de compléments. |
| [Références de marché](03-references-marche.md), [entreprises](05-fiches-entreprises-et-criteres-investissement.md) | Comparables et capacité d’investissement. |

Les annexes d’audit et de recalibrage conservent l’historique. **Les résultats actuels sont ceux de la note de décision et du classeur à trois onglets.** La version précédente est préservée dans `archives/methodes-remplacees/2026-10-21/avant-trois-onglets/`.
''', encoding='utf-8')
(root / '04-resultats-etude.md').write_text(head + '''# FLOW — note de décision

## Ordre de grandeur retenu

**Construire FLOW représente 24,46 M€ HT de réalisation initiale, puis 1,75 M€ HT par année pleine de fonctionnement**, dans les hypothèses retenues. Le fournisseur est autonome en France. La livraison unique intervient au mois 60.

''' + table + '''
Les cumuls partent du lancement du projet et comprennent la réalisation, les services humains, licences, support éditeur et ressources techniques. La moyenne annuelle porte sur les années 6 à 15 ; elle inclut les indexations. Ce sont des dépenses, sans actualisation ni valorisation des bénéfices métier.

## Ce qui finance les services

| Services humains, année pleine | FLOW | SAP | Microsoft |
| --- | ---: | ---: | ---: |
| Base | Équipe estimée | Forfaits RFI Delaware | Équipe estimée |
| Maintien en service, exploitation et pilotage | 7 × 200 JH × 750 € = **1,05 M€** | 250 k€ MCO + 450 k€ supervision = **0,70 M€** | 6 × 200 JH × 850 € = **1,02 M€** |
| Évolutions fonctionnelles | 2 × 200 JH × 750 € = **0,30 M€** | **0,35 M€**, forfait | 2 × 200 JH × 850 € = **0,34 M€** |
| **Total services** | **1,35 M€/an** | **1,05 M€/an** | **1,36 M€/an** |

Les équipes FLOW/Microsoft couvrent les heures ouvrées françaises : trois capacités de service/exploitation, trois d’entretien et qualification FLOW contre deux Microsoft, une d’architecture et pilotage. Les deux capacités d’évolutions sont distinctes. Les [justifications](02-methode-estimation.md) décrivent les responsabilités et conditions de suffisance ; aucun volume fictif de tickets n’entre dans le calcul.

**Pas de deuxième enveloppe MCO ou exploitation.** Corrections, versions techniques et pilotage sont dans le maintien. Nouvelles fonctions, y compris nouvelles versions fonctionnelles du Core FLOW, sont dans les évolutions. Les ressources informatiques sont des factures distinctes des personnes. Les mêmes interventions ne doivent pas être imputées au projet et au Run.

SAP conserve ses forfaits source, avec supervision en horaires étendus. L’équipe SAP théorique de 6 + 2 personnes-an à 850 €/JH vaut 1,36 M€/an, mais **ne remplace pas et ne complète pas automatiquement les forfaits**. Leurs volumes et leur couverture de toute la cible FLOW ne sont pas établis. Les capacités d’évolution ne garantissent pas un nombre identique de fonctions livrées.

## Quand les systèmes rendent le service

| Depuis le lancement | FLOW | SAP | Microsoft |
| --- | ---: | ---: | ---: |
| Premiers usages | Mois 60 | Mois 18 | Mois 18 |
| Périmètre complet | Mois 60 | Mois 30 | Mois 38 |
| **Années de services financées à 15 ans** | **10** | **13,5** | **13,5** |

**Convention retenue : capacité complète de service dès les premiers usages**, à partir du mois suivant la livraison. Elle n’est plus réduite en proportion du périmètre déployé. Les abonnements et ressources de recette commencent pendant le projet. Le tenant CPI de production commence au premier usage ; ses messages et les ressources Microsoft suivent la montée du périmètre.

Le graphique montre les trois courbes et les jalons. Les coûts annuels sont interpolés pour placer ces dates ; ils ne constituent pas un échéancier mensuel de factures. Les gains métier restent non chiffrés.

## Ce qui a changé depuis la version précédente

| Écart sur 15 ans | FLOW | SAP | Microsoft |
| --- | ---: | ---: | ---: |
| Total précédent | 36,306 M€ | 49,854 M€ | 37,087 M€ |
| Effet du nouveau démarrage, aux anciens prix annuels | 0 | +0,840 M€ | +1,075 M€ |
| Effet des nouvelles capacités, sur la nouvelle durée de service | +5,655 M€ | 0 | +2,806 M€ |
| **Nouveau total** | **41,961 M€** | **50,694 M€** | **40,968 M€** |

FLOW passe de 0,7845 M€ à 1,35 M€/an de services humains, soit +0,5655 M€ pendant dix ans. Microsoft passe de 1,152175 M€ à 1,36 M€/an ; la différence de 0,207825 M€ porte sur 13,5 ans. SAP garde ses 1,05 M€/an ; seuls 0,8 an supplémentaire de service sont financés. L’ancienne durée Microsoft était 12,5667 ans, SAP 12,7 ans, pondérées par le périmètre.

**Aucun changement des budgets initiaux, des trajectoires de licences, du support éditeur ni des ressources dans le cas de référence.** Les écarts sont réconciliés par année. La simplification ne sert pas à créer une économie.

## Lecture pour le décideur

FLOW demande davantage d’investissement et rend les premiers services plus tard. Il donne la maîtrise du produit et de ses règles. Le prix journalier et le budget d’évolutions sont inférieurs dans les hypothèses retenues, mais le groupe finance aussi l’entretien de tout le Core.

Le Buy réduit l’investissement initial et livre plus tôt. Les souscriptions et services subsistent. La projection retient 4 % d’indexation des licences après le gel : un an SAP et cinq ans Microsoft, hypothèses contractuelles à confirmer. Les prestations françaises et ressources hors CPI restent à 0 % ; CPI à 4 %. Aucun croisement n’est forcé : **FLOW reste environ 1,0 M€ au-dessus de Microsoft à quinze ans** dans le calcul courant.

L’écart ne suffit pas à choisir une solution : les bénéfices de maîtrise, la couverture contractuelle et les fonctions réellement livrées ne sont pas monétisés. SAP et Microsoft gardent leurs différences de périmètre et les compléments estimés dans l’étude.

## Conditions et options

Le nominal comprend les fournisseurs ; les contributions internes Beaumanoir sont exclues. Storeland non découvert, lotissement additionnel, risque, co-construction client, astreinte et migrations majeures sont à zéro par défaut. La co-construction est affichée hors total fournisseur. Un zéro client ne signifie pas absence de travail interne.

Les 400 k€/an de ressources FLOW, CPI et extensions externes Microsoft sont des budgets d’hypothèse repris de l’étude. L’hébergement standard Buy est déjà dans les licences. Le crédit BTP reste non imputé faute de valeur ; les compléments de plateforme doivent être rapprochés des souscriptions.

Les 32 100 JH et budgets initiaux ne sont pas réestimés dans cette refonte. Les abaques de réalisation restent documentés dans les annexes et la version détaillée archivée ; les trois onglets utilisent ces budgets comme entrées expliquées.

## Vérification

Le recalcul natif Excel ne relève aucune erreur et confirme les unités. Les contrôles vérifient les budgets initiaux, les trajectoires conservées, le démarrage du service, l’indexation, les effets des capacités/options et l’exclusion de l’équipe SAP théorique. Ils valident les calculs, pas la suffisance contractuelle des moyens.

[Méthode](02-methode-estimation.md) · [Guide du classeur](13-audit-classeur-excel.md) · [Synvance](07-analyse-synvance.md) · [Compléments Buy](15-rapprochement-buy-france.md)
''', encoding='utf-8')
(root / '13-audit-classeur-excel.md').write_text(head + '''# Lire et ajuster le classeur

Le fichier comprend **exactement trois onglets visibles**, sans synthèses supplémentaires.

## Comparaison

- En haut : initial, annuel moyen et cumuls **3/5/10/15 ans** sur une seule ligne par option.
- Un graphique commun, avec premiers usages et fin des déploiements.
- Dates et années de service financées.
- Plus bas : structure initiale et structure annuelle moyenne ; provision client séparée.

Les valeurs sont en M€ et M€/an. Aucun volet n’est figé sur cette page. SAP est identifié « Forfaits RFI », FLOW/Microsoft « Équipe ».

## Hypothèses

| Zone | Usage |
| --- | --- |
| Lignes 9–11 | Les trois choix de service : maintien, évolutions, prix journalier. |
| Lignes 12–14 | Budget annuel résultant ; SAP lié aux forfaits dans Sources. |
| Lignes 19–24 | Ressources et dates de mise en service. FLOW a une seule date. |
| Lignes 30–33 | Équipe SAP théorique **hors total**. |
| Lignes 39–49 | Convention de capacité, indexations, gels et retraits de licences. |
| Lignes 54–59 | Options inactives ; co-construction client hors fournisseur. |
| Lignes 65–84 | Budgets initiaux et calendrier liés aux entrées. |
| Lignes 90–153 | Calculs annuels détaillés des trois solutions en euros. |
| Lignes 160–197 | Synthèse calculée et données du graphique. |

Les hypothèses modifiables sont jaunes avec chiffres bleus. Les cellules liées aux sources et les formules sont distinctes. Toutes les conventions numériques sont visibles, y compris les constantes techniques ; aucun calcul financier n’est masqué.

Changer l’effectif de maintien FLOW de 7 à 8 ajoute 150 k€/an, donc 1,5 M€ sur les dix années de service. Changer l’équipe SAP théorique ne change aucun total ; changer son forfait source agit sur son coût. Les budgets initiaux sont des entrées conservées, pas des charges réestimées par le présent modèle.

## Sources

Les forfaits et paniers RFI sont séparés des budgets estimés et des hypothèses. Les références indiquent la pièce et la page. Les raisons du choix d’équipe, les inclusions/exclusions, les échéanciers et le calcul CPI sont visibles dans cet onglet.

Les références aux annexes détaillées préservent l’origine des budgets initiaux. La précédente version complète est archivée dans `archives/methodes-remplacees/2026-10-21/avant-trois-onglets/`. Les anciens montants de service ne constituent plus le calcul courant.

## Frontières à conserver

Une seule capacité finance le maintien, l’exploitation et le pilotage. Les évolutions fonctionnelles ont leur capacité propre. Les ressources et souscriptions financent les plateformes ; elles ne sont pas du temps d’exploitation. Les options d’astreinte et migrations majeures ne financent pas à nouveau les versions courantes.

L’inflation des prestations s’applique depuis le lancement. Les licences suivent leur gel puis leur indexation. Le service complet commence après le mois de première livraison ; seules les ressources variables suivent les parts de production. Les coûts client restent hors total fournisseur.

Les limites de couverture des forfaits SAP sont affichées : la cohérence du tableur ne prouve pas l’équivalence de service. Les hypothèses d’équipe restent un ordre de grandeur fournisseur.
''', encoding='utf-8')
p = root / '02-methode-estimation.md'
t = p.read_text(encoding='utf-8').replace('**Laurent Sintès** · 20 octobre 2026','**Laurent Sintès** · 21 octobre 2026')
t = t.replace('Les hypothèses ci-dessous sont proposées avant modification de l\'Excel. Les cumuls et le classement actuels du classeur restent provisoires.', 'Les hypothèses ci-dessous sont appliquées au classeur à trois onglets le 21 octobre 2026. Les résultats recalculés figurent dans la [note de décision](04-resultats-etude.md). La couverture contractuelle des forfaits SAP reste distincte des hypothèses d’équipe.')
t = t.replace('Trois onglets suffisent pour le futur classeur :', 'Le classeur comprend trois onglets :').replace('**Sources et explications**', '**Sources**')
t = t.replace('Cet échéancier n\'est pas recalculé dans la présente reprise.', 'Cet échéancier est appliqué : capacité complète dès les premiers usages, sans pondération par le périmètre. Les interventions de stabilisation du projet et celles du service courant doivent être attribuées séparément ; la relève contractuelle reste à vérifier.')
t = t.replace('**État : méthode et dispositif proposés ; Excel inchangé.** Le classement économique reste suspendu jusqu\'à une comparaison appliquant la même définition de service. Cette étape ne demande ni backlog détaillé ni nouveau lotissement.', '**État : méthode appliquée au classeur le 21 octobre 2026.** Les budgets initiaux sont conservés. Le résultat est un ordre de grandeur sous hypothèses ; l’équivalence contractuelle des niveaux de service reste à établir. Cette étape ne demande ni backlog détaillé ni nouveau lotissement.')
p.write_text(t,encoding='utf-8')
for name in ['12-modele-tco-buy-make.md','14-audit-inflation-run-et-comparaison.md','17-audit-version-v4.md','18-corrections-services-et-tracabilite.md','19-recalibrage-service-microsoft.md']:
    p = root/name
    t = p.read_text(encoding='utf-8')
    banner = '> **Historique conservé.** Les montants, abaques de service et noms d’onglets ci-dessous décrivent les versions antérieures. Depuis le 21 octobre 2026, la [méthode](02-methode-estimation.md), la [note de décision](04-resultats-etude.md) et le [guide des trois onglets](13-audit-classeur-excel.md) portent le calcul courant.\n\n'
    if not t.startswith(banner):
        t = banner+t
    t = t.replace('Les montants ci-dessous restent dans l\'Excel inchangé ; ils ne valident pas la suffisance du service et le classement à quinze ans est suspendu.', 'Les montants ci-dessous sont historiques et ne sont plus ceux du classeur courant.')
    p.write_text(t,encoding='utf-8')
print('Updated current study, guide and historical status banners.')
