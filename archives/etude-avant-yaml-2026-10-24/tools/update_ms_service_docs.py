"""Update the study from recalculated results; preserve the previous estimate."""
from pathlib import Path
import json, shutil
root=Path(__file__).resolve().parent.parent
archive=root/"archives/methodes-remplacees/2026-10-20/avant-recalibrage-service-microsoft"
archive.mkdir(parents=True,exist_ok=True)
names=["README.md","02-methode-estimation.md","04-resultats-etude.md","09-abaques-repartition.md",
       "10-audit-estimabilite-et-incertitude.md","11-cout-nominal-minimum.md","12-modele-tco-buy-make.md",
       "13-audit-classeur-excel.md","14-audit-inflation-run-et-comparaison.md",
       "15-rapprochement-buy-france.md","16-methodes-et-presentation-comparaison-make-buy.md",
       "18-corrections-services-et-tracabilite.md"]
for n in names:
    if not (archive/n).exists():shutil.copy2(root/n,archive/n)
data=json.loads((root/"tmp/service_audit_results.json").read_text(encoding="utf-8"))
ms=data["headlines"][2]
assert abs(ms[6]-37.08658043460488)<1e-8
header="![Logo eXalt](assets/exalt-logo.png)\n\n**Laurent Sintès** · 20 octobre 2026\n\n---\n\n"
def read(n):return (root/n).read_text(encoding="utf-8-sig")
def write(n,t):(root/n).write_text(t,encoding="utf-8")
def paragraph(t,start,new):
    parts=t.split("\n\n")
    found=False
    for i,p in enumerate(parts):
        if p.startswith(start):parts[i]=new;found=True
    if not found:raise ValueError(start)
    return "\n\n".join(parts)
summary=("Microsoft est estimé par **activités et compétences** : **472 JH / 401 200 € de maintenance-pilotage**, "
         "**443,5 JH / 376 975 € d’exploitation**, **440 JH / 374 000 € d’évolutions** par an, au tarif moyen France conservé de 850 €/JH. "
         "Les fréquences et efforts sont des hypothèses explicites, pas des mesures Beaumanoir ni un devis Microsoft.")
drivers=("Le dimensionnement retient six domaines opérationnels et un repère de 40 interfaces issu du pilote Avanade, utilisé comme hypothèse de patrimoine cible. "
         "Il comprend 288 diagnostics fonctionnels, dont 72 analyses techniques additionnelles, 36 correctifs, quatre campagnes de versions et l’entretien des 120 scénarios automatisés déjà provisionnés au build. "
         "Les vingt marques partagent ces domaines ; aucun multiplicateur de CA, de volume vendu, de marque ou de coût Make n’est appliqué.")
competence=("Les mêmes jours sont ventilés entre fonctionnel, technique/intégration, développement, tests/versions et pilotage. "
            "**1 355,5 JH/an, évolutions comprises**, représentent **6,78 personnes-années** à 200 JH par personne-an. "
            "Ce contrôle de capacité n’ajoute aucun budget d’équipe. Le fournisseur est mutualisé, en heures ouvrées, sans engagement de présence dédiée ni astreinte.")
conclusion=("**Sur quinze ans, FLOW atteint 36,31 M€, Microsoft 37,09 M€ et SAP 49,85 M€.** "
            "L’écart FLOW–Microsoft est d’environ **0,78 M€**, faible au regard des hypothèses d’activité et de couverture. "
            "Microsoft reste moins coûteux aux horizons de trois, cinq et dix ans et livre plus tôt. "
            "Le classement à quinze ans est conditionnel ; il ne démontre ni un ROI ni une économie garantie à service identique.")
for n in names:
    if n in ["14-audit-inflation-run-et-comparaison.md","18-corrections-services-et-tracabilite.md"]:continue
    t=read(n)
    # Current numerical statements; the historical correction is preserved separately.
    for a,b in [
        ("306 JH / 260 100 €","472 JH / 401 200 €"),("234 JH / 198 900 €","443,5 JH / 376 975 €"),
        ("540 JH / 459 000 €","915,5 JH / 778 175 €"),
        ("306 JH × 850 € = **260 100 €**","472 JH × 850 € = **401 200 €**"),
        ("234 JH × 850 € = **198 900 €**","443,5 JH × 850 € = **376 975 €**"),
        ("260,1 k€","401,2 k€"),("198,9 k€","376,975 k€"),("459,0 k€","778,175 k€")]:
        t=t.replace(a,b)
    t=t.replace("ses 30 correctifs annuels","ses 36 correctifs annuels")
    t=t.replace("ses 30 corrections annuelles","ses 36 corrections annuelles")
    t=t.replace("ses 30 correctifs","ses 36 correctifs")
    t=t.replace("Microsoft suppose que ses 36 correctifs annuels", "Microsoft retient six correctifs par domaine/an, soit 36 correctifs, qui")
    if n in ["README.md","04-resultats-etude.md"]:
        for a,b in [("**2,0 M€/an**","**2,4 M€/an**"),("| 9,0 M€ |","| 9,2 M€ |"),("| 12,7 M€ |","| 13,5 M€ |"),
                    ("| 22,3 M€ |","| 24,7 M€ |"),("**33,1 M€**","**37,1 M€**")]:t=t.replace(a,b)
        t=paragraph(t,"**Microsoft reste",conclusion)
        if n=="04-resultats-etude.md":
            t=paragraph(t,"**Hypothèses actives", "**Hypothèses actives :** réalisation en France ; FLOW et Microsoft en heures ouvrées, dimensionnés séparément ; SAP aux forfaits source. Prestations et ressources à prix constants ; licences et CPI à 4 % selon les gels ; options et contributions internes exclues. "+drivers)
            t=paragraph(t,"La feuille **Service annuel**", "La feuille **Service annuel** expose les forfaits SAP et les activités propres à FLOW et Microsoft. "+summary+" "+competence)
        else:
            t=t.replace("[suivi de l'audit](18-corrections-services-et-tracabilite.md)","[recalibrage Microsoft](19-recalibrage-service-microsoft.md)")
            t=paragraph(t,"L'[audit v4]", "L’[audit v4](17-audit-version-v4.md) et le [rétablissement des forfaits SAP](18-corrections-services-et-tracabilite.md) sont historiques. Le [recalibrage Microsoft](19-recalibrage-service-microsoft.md) explique la version courante.")
    if n=="02-methode-estimation.md":
        t=t.replace("FLOW et Microsoft retiennent 240 diagnostics/an ; la prévention ne réduit pas ce nombre.",drivers)
    if n=="11-cout-nominal-minimum.md":
        t=paragraph(t,"FLOW et Microsoft conservent", "FLOW conserve 240 diagnostics/an. Microsoft utilise un abaque distinct par domaine et interface, explicité dans le [recalibrage](19-recalibrage-service-microsoft.md). Les volumes des forfaits SAP restent inconnus.")
    if n=="12-modele-tco-buy-make.md":
        t=paragraph(t,"Les 234 JH",summary+" "+drivers)
        t=paragraph(t,"Microsoft est une **hypothèse",summary+" "+competence)
    if n in ["15-rapprochement-buy-france.md","16-methodes-et-presentation-comparaison-make-buy.md"]:
        start="SAP utilise les forfaits source. Microsoft est une **hypothèse" if n.startswith("15") else "Microsoft est une **hypothèse"
        t=paragraph(t,start,summary+" "+drivers+" Les forfaits SAP demeurent inchangés.")
        t=t.replace("**376,975 k€/an**, hypothèse par activité en heures ouvrées","**376,975 k€/an**, activités et compétences en heures ouvrées")
    if n=="13-audit-classeur-excel.md":
        t+="\n\n## Recalibrage Microsoft\n\nLes entrées sont dans **Service annuel, lignes 202–220**, les activités détaillées en **232–293**, et la ventilation par compétence en **301–307**. Les sous-totaux alimentent les prix unitaires, puis les calendriers et la comparaison. La ventilation ne crée pas de deuxième coût. Les forfaits SAP restent directement reliés aux sources.\n"
    write(n,t)

# Replace the old Microsoft service table, keeping FLOW, SAP and build sections.
n="09-abaques-repartition.md";t=read(n)
a=t.index("### Hypothèses Microsoft");b=t.index("### FLOW et évolutions")
detail="""### Microsoft : activités, compétences et frontières

"""+summary+"\n\n"+drivers+"""

| Maintenance et pilotage | Calcul principal | JH/an |
| --- | --- | ---: |
| Diagnostics fonctionnels et techniques | 6 domaines × 12 mois × (4 × 0,5 JH + 1 × 0,75 JH) | 198 |
| Correctifs | 6 domaines × 6 correctifs × (0,5 JH fonctionnel + 2 JH développement + 0,5 JH tests) | 108 |
| Versions et tests automatisés | 4 × 6 domaines × 2 JH + 4 × 40 interfaces × 0,125 JH + 120 scripts × 0,25 JH + 4 livraisons × 2 JH | 106 |
| Pilotage du service | 12 × (2 JH pilotage + 2 JH fonctionnel + 1 JH technique) | 60 |
| **Total maintenance** | | **472** |

Les 72 analyses techniques sont un sous-ensemble des 288 dossiers : elles interviennent après qualification fonctionnelle, sans compter un deuxième ticket. Les correctifs financent un travail distinct de diagnostic. Les 36 correctifs couvrent toutes les adaptations et interfaces, OMS compris ; les corrections du produit standard relèvent de l’éditeur.

| Exploitation | Calcul principal | JH/an |
| --- | --- | ---: |
| Contrôles quotidiens techniques et métier | 250 × (0,3 + 0,2 JH) | 125 |
| Cohérence des commandes, stocks et partenaires | 250 × 0,25 JH | 62,5 |
| Rétablissements techniques | 12 × 2 JH | 24 |
| Accès, paramètres et capacité | 12 × 2 JH | 24 |
| Reprises d’interfaces | 40 × 2 épisodes/an × (0,75 JH technique + 0,25 JH métier) | 80 |
| Fiabilité préventive des interfaces | 40 × 4 revues/an × 0,25 JH | 40 |
| Procédures métier et techniques | 6 domaines × 2 revues × (1 + 1 JH) | 24 |
| Exercices de reprise | 4 × (3 JH technique + 2 JH métier) | 20 |
| Environnements et données de recette | 4 × 2 JH | 8 |
| Préparation des pics | 4 campagnes × 6 domaines × (1 JH métier + 0,5 JH technique) | 36 |
| **Total exploitation** | | **443,5** |

Une reprise est un épisode pouvant regrouper plusieurs messages. La surveillance lit les alertes ; le contrôle de cohérence qualifie les écarts de données ; le rejeu rétablit les échanges. Les postes ne refacturent ni le diagnostic détaillé ni un développement.

Les quatre campagnes de pics représentent deux saisons et deux pics commerciaux pour le groupe. Les vingt marques ne sont pas multipliées par chaque tâche. Les fréquences restent des hypothèses ; elles ne sont déduites ni du CA ni des 120 millions de pièces.

Les tâches de recette préparent des environnements existants ; leurs ressources et licences sont ailleurs. L’entretien des tests couvre le patrimoine déjà construit. Les nouveaux tests et le pilotage de réalisation propres à une évolution restent dans l’évolution.

### Capacité par compétence

"""+competence+"""

| Compétence | Maintenance JH | Exploitation JH | Évolutions JH | Total JH |
| --- | ---: | ---: | ---: | ---: |
| Fonctionnel | 198 | 176,5 | 122 | 496,5 |
| Technique / intégration | 74 | 267 | 16 | 357 |
| Développement | 72 | 0 | 220 | 292 |
| Tests / versions | 104 | 0 | 64 | 168 |
| Pilotage du service | 24 | 0 | 18 | 42 |
| **Total** | **472** | **443,5** | **440** | **1 355,5** |

Le tarif moyen reste 850 €/JH. La table ne transforme pas les fractions en équipes dédiées ni en engagement de disponibilité. La couverture en jours ouvrés suppose un prestataire disposant de remplaçants et de compétences mutualisées. Aucune réserve de risque ou astreinte n’est ajoutée.

"""
t=t[:a]+detail+t[b:]
t=t.replace("Microsoft suppose que ses 30 correctifs annuels","Microsoft suppose que ses 36 correctifs annuels")
write(n,t)

# Retain previous correction as historical evidence, with an explicit current pointer.
t=read("18-corrections-services-et-tracabilite.md")
t=t.replace("# Base SAP rétablie et hypothèses Microsoft",
"""# Base SAP rétablie et hypothèses Microsoft

> **Historique :** cette note décrit la version précédant le recalibrage Microsoft. Les forfaits SAP restent actifs ; les anciens montants Microsoft ci-dessous sont remplacés par le [recalibrage par activités et compétences](19-recalibrage-service-microsoft.md). La note de décision et le classeur portent les résultats courants.""",1)
write("18-corrections-services-et-tracabilite.md",t)

write("19-recalibrage-service-microsoft.md",header+"""# Microsoft — service annuel recalibré pour Beaumanoir

## Résultat

"""+summary+"\n\n"+conclusion+"""

| Poste Microsoft, année pleine hors inflation | Avant | Recalibré | Écart |
| --- | ---: | ---: | ---: |
| Maintenance et pilotage | 306 JH / 260 100 € | 472 JH / 401 200 € | +141 100 € |
| Exploitation | 234 JH / 198 900 € | 443,5 JH / 376 975 € | +178 075 € |
| **Maintenance et exploitation** | **540 JH / 459 000 €** | **915,5 JH / 778 175 €** | **+319 175 €** |
| Évolutions | 440 JH / 374 000 € | 440 JH / 374 000 € | 0 |
| **Total services** | **980 JH / 833 000 €** | **1 355,5 JH / 1 152 175 €** | **+319 175 €** |

Les licences, Unified, plateformes, coûts initiaux, forfaits SAP, coûts FLOW et calendriers restent inchangés. Les évolutions Microsoft sont décomposées par compétence sans augmenter leur enveloppe.

## Base de dimensionnement

"""+drivers+"""

Les six domaines regroupent achats ; commandes/retours ; stock ; allocation/promesse ; fulfillment/intercompany ; documents opérationnels. C’est un découpage de travail pour cette estimation, pas un nombre de modules imposé.

Les activités détaillées sont présentées dans [les abaques](09-abaques-repartition.md) et entièrement calculées dans Excel. Les récurrences sont exprimées en mois, jours ouvrés, interfaces, campagnes ou domaines ; aucun taux forfaitaire du build n’est appliqué.

## Nature des preuves

| Élément | Statut |
| --- | --- |
| 40 interfaces du pilote | Source Avanade, réponse RFI #1 p. 39. Utilisation comme patrimoine cible : hypothèse, pas inventaire de FLOW. |
| 120 scénarios automatisés | Hypothèse déjà financée dans le build, reprise par formule dans l’entretien annuel. Aucun nouveau build ajouté. |
| Quatre publications D365 par an | Documentation Microsoft Learn ; deux adoptions au minimum. Retenir quatre campagnes et leurs efforts est une hypothèse du modèle. |
| Responsabilités client/intégrateur | Microsoft Learn : santé de la solution, intégrations, configurations, tests et coordination ne disparaissent pas en SaaS. |
| Incidents, correctifs et reprises | Hypothèses de fréquences, pas statistiques Beaumanoir. |
| 850 €/JH | Tarif moyen de prestation France déjà retenu, conservé ; pas un nouveau devis ni un tarif sourcé par compétence. |

Sources consultées le 20 octobre 2026 : [responsabilités de fonctionnement](https://learn.microsoft.com/en-us/dynamics365/guidance/implementation-guide/service-solution), [compétences du support](https://learn.microsoft.com/en-us/dynamics365/guidance/implementation-guide/transition-to-support-team), [mises à jour D365](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/get-started/public-preview-releases).

## Capacité et absence de double compte

"""+competence+"""

Les règles de frontière sont :

- diagnostic fonctionnel puis, pour certains dossiers, analyse technique ; aucune double réception du ticket ;
- correction : conception, code et tests ciblés, séparés de la campagne transverse ;
- contrôle des alertes, cohérence des données et reprise effective sont trois travaux différents ;
- entretien des scripts existants dans la maintenance ; nouveaux scripts dans l’évolution concernée ;
- pilotage du service dans la maintenance ; pilotage de réalisation dans les évolutions ;
- coût des personnes dans le service ; ressources techniques et souscriptions dans leurs propres lignes ;
- tableau de compétences issu des activités, sans coût d’équipe ajouté.

## Comparaison recalculée

| Coûts fournisseur HT depuis le lancement | FLOW | SAP | Microsoft |
| --- | ---: | ---: | ---: |
| Réalisation initiale | 24,46 M€ | 17,13 M€ | 5,74 M€ |
| Fonctionnement moyen, années 6 à 15 | 1,18 M€/an | 2,54 M€/an | 2,36 M€/an |
| Cumul à 3 ans | 14,58 M€ | 19,98 M€ | 9,18 M€ |
| Cumul à 5 ans | 24,46 M€ | 24,42 M€ | 13,53 M€ |
| Cumul à 10 ans | 30,38 M€ | 36,41 M€ | 24,75 M€ |
| Cumul à 15 ans | 36,31 M€ | 49,85 M€ | 37,09 M€ |

Microsoft passe de **33,075615 à 37,086580 M€** à quinze ans. La variation se réconcilie : **319 175 €/an × 12,566667 années équivalentes de Run = 4 010 965,83 €**. Les services gardent une inflation nominale nulle ; licences et CPI conservent leurs indexations propres.

## Limites

Les forfaits SAP couvrent un monitoring en horaires étendus ; Microsoft et FLOW sont en heures ouvrées. L’équivalence contractuelle n’est pas établie. Le modèle suppose des processus stabilisés et une automatisation opérationnelle ; il ne finance pas une crise durable ou une présence 24/7.

Les prestations sont proratisées au périmètre livré selon la convention existante. Une capacité réelle n’est pas nécessairement divisible de cette manière. Les contributions internes et le L1 métier sont exclus ; les tâches applicatives du fournisseur restent bien dans les charges détaillées. Astreinte, migrations majeures et autres options restent inactives.

Le classement est une conséquence de ces hypothèses. Il n’est ni un objectif de calibration ni une économie démontrée. Les [contrôles](14-audit-inflation-run-et-comparaison.md) vérifient le calcul, pas la validité commerciale des volumes ou tarifs.
""")
print("Microsoft study updated",ms)
