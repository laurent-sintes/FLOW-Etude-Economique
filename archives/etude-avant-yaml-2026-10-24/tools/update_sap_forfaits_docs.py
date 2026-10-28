"""Synchronise study prose with the sourced SAP service basis; no workbook writes."""
from pathlib import Path
import json, shutil

root=Path(__file__).resolve().parent.parent
archive=root/"archives/methodes-remplacees/2026-10-20/avant-retablissement-forfaits-sap"
archive.mkdir(parents=True,exist_ok=True)
names=["README.md","02-methode-estimation.md","04-resultats-etude.md","09-abaques-repartition.md",
       "10-audit-estimabilite-et-incertitude.md","11-cout-nominal-minimum.md",
       "12-modele-tco-buy-make.md","13-audit-classeur-excel.md","14-audit-inflation-run-et-comparaison.md",
       "15-rapprochement-buy-france.md","16-methodes-et-presentation-comparaison-make-buy.md",
       "18-corrections-services-et-tracabilite.md"]
for name in names:
    if not (archive/name).exists(): shutil.copy2(root/name,archive/name)
common=("SAP utilise les forfaits Delaware : **250 k€/an de MCO, 450 k€/an de supervision en horaires étendus et 350 k€/an d’évolutions**. "
        "FLOW et Microsoft restent estimés par activité en heures ouvrées. Les volumes des forfaits SAP ne sont pas documentés : "
        "**l’équivalence des niveaux de service et des capacités d’évolution n’est pas démontrée**.")
ms=("Microsoft est une **hypothèse d’ingénierie en France**, pas un devis de services : "
    "**306 JH × 850 € = 260,1 k€ de maintenance/pilotage**, **234 JH × 850 € = 198,9 k€ d’exploitation**, "
    "**440 JH × 850 € = 374 k€ d’évolutions**. Les quantités et efforts sont modifiables ; "
    "ils ne proviennent pas d’un historique d’incidents Beaumanoir. Aucun forfait SAP n’est transposé.")
coverage=("Aucun supplément automatique de 3 %/5 % des développements n’est ajouté. Microsoft suppose que ses 30 correctifs annuels "
          "couvrent toutes les extensions et interfaces, compléments OMS compris. Pour SAP, le budget conserve les forfaits source ; "
          "**la couverture des compléments OMS/interfaces reste à confirmer**. L’absence de supplément ne démontre pas leur gratuité.")
options=("Astreinte FLOW et migrations majeures restent des options désactivées. Le monitoring SAP en horaires étendus reste financé "
         "dans le forfait de 450 k€ ; ce libellé ne prouve pas une couverture 24/7. FLOW et Microsoft sont estimés en heures ouvrées. "
         "Les prestations ne sont pas présentées comme contractuellement équivalentes.")
data=json.loads((root/"tmp/service_audit_results.json").read_text(encoding="utf-8"))
sap=data["headlines"][1]
def fr(v,n=1): return f"{v:.{n}f}".replace(".",",")
def read(name): return (root/name).read_text(encoding="utf-8")
def write(name,text): (root/name).write_text(text,encoding="utf-8")
def paragraph(text,start,new):
    parts=text.split("\n\n")
    found=False
    for i,p in enumerate(parts):
        if p.startswith(start):
            parts[i]=new;found=True
    if not found: raise ValueError(f"paragraph not found: {start}")
    return "\n\n".join(parts)

for name in ["README.md","04-resultats-etude.md"]:
    t=read(name)
    for old,val in [("2,3 M€/an",sap[2]),("19,8 M€",sap[3]),("23,8 M€",sap[4]),("34,6 M€",sap[5]),("46,9 M€",sap[6])]:
        t=t.replace(old,fr(val)+(" M€/an" if "/an" in old else " M€"))
    if name=="README.md":
        t=paragraph(t,"Le dossier présente", "Le dossier présente **un budget de référence par option, sous hypothèses**, pas un engagement de prix. FLOW est réalisé par un fournisseur autonome en France, livré une fois à cinq ans. "+common+" Contributions internes et options inactives restent exclues.")
        t=paragraph(t,"**Microsoft reste", "**Microsoft reste moins cher que FLOW dans le modèle à quinze ans**, sous les hypothèses Microsoft indiquées. L’écart ne constitue pas une économie prouvée à service identique. Les forfaits SAP pilotent le budget SAP et ne sont pas transposés à Microsoft. La maîtrise du produit et de ses règles n’est pas monétisée.")
    else:
        t=paragraph(t,"Les références SAP", "Les références initiales SAP et Microsoft viennent de l’étude Synvance de 2025. Les compléments fonctionnels sont estimés à part. "+common)
        t=paragraph(t,"**Hypothèses actives", "**Hypothèses actives :** réalisation en France ; FLOW/Microsoft en heures ouvrées avec 240 diagnostics/an estimés ; SAP aux forfaits source. Prestations et ressources à prix constants ; licences et CPI à 4 % selon les gels ; options et contributions internes exclues. Les volumes et indexations sont des hypothèses.")
        t=t.replace("| 252,0 k€ | 260,1 k€ |","| 252,0 k€ | 250,0 k€ (forfait) |")
        t=t.replace("| 220,5 k€ | 198,9 k€ |","| 220,5 k€ | 450,0 k€ (forfait) |")
        t=t.replace("| **544,5 k€** | **459,0 k€** |","| **544,5 k€** | **700,0 k€** |")
        t=t.replace("| **240,0 k€** | **357,0 k€** |","| **240,0 k€** | **350,0 k€ (forfait)** |")
        t=t.replace("Évolutions métier, total comparable","Évolutions métier, budget retenu")
        t=paragraph(t,"La feuille **Service annuel**", "La feuille **Service annuel** expose les forfaits SAP et les activités FLOW/Microsoft. "+coverage)
        t=paragraph(t,"FLOW porte davantage", "FLOW porte la configuration de son runtime et les vérifications de sauvegarde/restauration. Ces tâches techniques sont supposées couvertes par le cloud managé Buy. Microsoft finance aussi les contrôles applicatifs et le PRA métier ; la décomposition des forfaits SAP est inconnue.")
        t=paragraph(t,"**Microsoft reste", "**Microsoft reste moins cher que FLOW dans le modèle : environ 33,1 M€ contre 36,3 M€ sur quinze ans.** Le forfait de supervision de 450 k€ précédemment transposé de SAP n’était pas un prix Microsoft. Son remplacement par des activités estimées constitue un changement d’hypothèse, pas une économie fournisseur démontrée. Le classement reste conditionnel aux volumes, tarifs et responsabilités retenus.")
        t=t.replace("| Service humain en heures ouvrées ; plateformes, évolutions et licences retenues. | Astreinte/horaire étendu, garantie de capacité ou de SLA ; engagement de prix ou de délai. |",
                    "| Services FLOW/Microsoft en heures ouvrées ; forfaits SAP avec monitoring en horaires étendus ; plateformes et licences retenues. | Astreinte additionnelle, garantie d’équivalence des SLA ; engagement de prix ou de délai. |")
        t=paragraph(t,"Tarifs France retenus", "Tarifs France retenus : **750 €/JH FLOW**, **1 000 €/JH réalisation Buy**, **850 €/JH prestations Microsoft**. Les services SAP utilisent directement les forfaits source, sans division en JH ni revalorisation France faute de composition d’équipe. Aucun tarif n’est appliqué une seconde fois aux forfaits.")
        t=paragraph(t,"L'astreinte et les migrations",options+" Les 15 % Storeland, lotissement additionnel, risque et sortie restent désactivés.")
    write(name,t)

t=read("02-methode-estimation.md")
t=paragraph(t,"Le fonctionnement est estimé", "Le fonctionnement est séparé en maintenance, exploitation, évolutions et ressources techniques. "+common+" FLOW et Microsoft retiennent 240 diagnostics/an ; la prévention ne réduit pas ce nombre.")
t=paragraph(t,"Les corrections des progiciels",coverage+" Les souscriptions financent déjà la maintenance et l’hébergement du standard Buy.")
write("02-methode-estimation.md",t)

t=read("09-abaques-repartition.md")
a=t.index("### Même besoin de service");b=t.index("## Des abaques recalculables")
t=t[:a]+"""### Base SAP : trois forfaits sourcés

"""+common+"""

| Poste SAP | Budget annuel | Base |
| --- | ---: | --- |
| MCO hors évolutions | 250 000 € | Delaware p. 37 ; questionnaire onglet 8. |
| Monitoring des flux en horaires étendus | 450 000 € | Même source ; contenu et volumes non détaillés. |
| TMA évolutive | 350 000 € | Enveloppe ; capacité en changements non documentée. |
| **Total prestations SAP** | **1 050 000 €** | Hors abonnements et plateformes complémentaires. |

Les forfaits sont utilisés directement. Aucun abaque en JH ne s’y ajoute et aucune réduction au prorata horaire n’est supposée.

### Hypothèses Microsoft, distinctes des sources SAP

"""+ms+"""

| Activité Microsoft | Quantité × effort | Charge annuelle |
| --- | ---: | ---: |
| Diagnostics | 240 × 0,5 JH | 120 JH |
| Corrections des adaptations/interfaces | 30 × 3 JH | 90 JH |
| Tests de versions | 4 × 15 JH | 60 JH |
| Pilotage du service | 12 × 3 JH | 36 JH |
| **Maintenance et pilotage** | | **306 JH** |
| Revue des alertes | 250 × 0,2 JH | 50 JH |
| Rétablissement technique | 10 × 2 JH | 20 JH |
| Paramètres, sécurité, capacité applicative | 12 × 2 JH | 24 JH |
| Reprises d’interfaces et rejets métier | 36 × 2 JH | 72 JH |
| Fiabilité des flux | 12 × 2 JH | 24 JH |
| Procédures d’exploitation | 12 × 2 JH | 24 JH |
| Exercice de reprise du service métier | 4 × 5 JH | 20 JH |
| **Exploitation** | | **234 JH** |

Ces volumes dimensionnent un service mutualisé en heures ouvrées. Les 250 journées sont une convention de calendrier ; les autres fréquences ne sont pas des observations. Diagnostics, correctifs, rétablissements et reprises d’interfaces sont des activités distinctes. Leurs frontières sont explicitées dans Excel.

### FLOW et évolutions

FLOW conserve **726 JH × 750 € = 544 500 € de maintenance/exploitation** : 72 k€ de versions techniques, 252 k€ de maintenance/pilotage et 220,5 k€ d’exploitation. Les 240 diagnostics sont conservés en plus de la prévention.

| Évolutions estimées | Quantité/an | FLOW JH/unité | Microsoft JH/unité |
| --- | ---: | ---: | ---: |
| Règles métier | 40 | 2 | 3 |
| Fonctions / API | 10 | 12 | 16 |
| Changements structurants | 4 | 30 | 40 |
| **Total JH** | | **320** | **440** |
| **Coût annuel** | | **240 000 €** | **374 000 €** |

Les 120 JH / 90 k€ de versions fonctionnelles FLOW sont compris dans les 320 JH. SAP conserve 350 k€ de TMA ; rien ne prouve que cette enveloppe livre exactement le même panier de changements.

"""+coverage+"""

### Options et ressources

"""+options+"""

Les ressources FLOW restent séparées : **400 k€/an** après livraison, **386 k€** au total pendant la construction. L’hébergement standard Buy est dans les abonnements. CPI SAP et le runtime externe Microsoft sont des provisions conditionnelles détaillées dans le [modèle TCO](12-modele-tco-buy-make.md).

"""+t[b:]
write("09-abaques-repartition.md",t)

t=read("12-modele-tco-buy-make.md")
t=paragraph(t,"La stabilisation initiale", "La stabilisation initiale est supposée financée dans les travaux. Les forfaits SAP, annoncés après stabilisation, sont appliqués au prorata du périmètre livré dès les livraisons par convention d’estimation ; ce prorata ne constitue pas un échéancier contractuel. Les licences et Unified suivent leur calendrier propre.")
t=paragraph(t,"Tarifs vendus France", "Tarifs France : **750 €/JH FLOW**, **1 000 €/JH réalisation Buy**, **850 €/JH services Microsoft**, **750 €/JH tests automatisés**. Les forfaits SAP sont conservés en euros source ; leur composition et localisation inconnues ne permettent pas une revalorisation France justifiée.")
t=paragraph(t,"**Service annuel** est", "**Service annuel** regroupe les forfaits SAP et les abaques FLOW/Microsoft. "+common)
t=t.replace("| 336 JH / 252 000 € | 306 JH / 260 100 € |","| 336 JH / 252 000 € | Forfait 250 000 € |")
t=t.replace("| 294 JH / 220 500 € | 234 JH / 198 900 € |","| 294 JH / 220 500 € | Forfait 450 000 € |")
t=t.replace("| **726 JH / 544 500 €** | **540 JH / 459 000 €** |","| **726 JH / 544 500 €** | **Forfaits 700 000 €** |")
t=t.replace("| **320 JH / 240 000 €** | **420 JH / 357 000 €** |","| **320 JH / 240 000 €** | **Forfait 350 000 €** |")
t=t.replace("Évolutions métier, total comparable","Évolutions métier, budget retenu")
t=paragraph(t,"Les 234 JH d'exploitation", "Les 234 JH d’exploitation estimés Microsoft couvrent alertes, rétablissements, paramètres/sécurité, interfaces, procédures et PRA métier. FLOW ajoute 60 JH de configuration du runtime et de vérification des sauvegardes, supposés couverts par le cloud managé Microsoft. La décomposition SAP est inconnue ; ses forfaits restent utilisés.")
t=paragraph(t,"Le panier de corrections",coverage)
t=paragraph(t,"Le panier d'évolutions", "FLOW et Microsoft partagent une demande estimée de 40 règles, 10 fonctions/API et 4 changements structurants, aux efforts unitaires propres à chaque solution. SAP conserve son enveloppe TMA sans lui attribuer artificiellement un volume de changements. Les tests ciblés et le pilotage des évolutions ne sont pas ajoutés une seconde fois en maintenance.")
t=paragraph(t,"Les interventions P1",options)
a=t.index("## 6. Les forfaits");b=t.index("### Support Microsoft Unified")
t=t[:a]+"""## 6. Bases de prix et limites de comparaison

"""+common+"""

**SAP : 1 050 000 €/an** avant abonnements et plateformes complémentaires. Source : Delaware septembre 2025 p. 37 et questionnaire onglet 8, lignes 13–15. Les trois forfaits sont distincts ; aucun double compte source n’est démontré. La projection conserve leurs montants, sans abaque ajouté, réduction horaire ou conversion en JH. Elle ne prétend pas que le forfait couvre gratuitement les nouveaux compléments OMS.

"""+ms+"""

La charge Microsoft est détaillée dans [les abaques](09-abaques-repartition.md). Les 450 k€ précédemment utilisés étaient une transposition SAP, pas un prix Microsoft : leur remplacement ne démontre aucune économie négociée.

"""+coverage+"""

Les souscriptions maintiennent le code standard ; les services clients restent distincts. SAP inclut un monitoring en horaires étendus ; FLOW et Microsoft restent en heures ouvrées. La différence est affichée dans la comparaison, sans prétendre normaliser un SLA inconnu.

"""+t[b:]
write("12-modele-tco-buy-make.md",t)

t=read("15-rapprochement-buy-france.md")
t=paragraph(t,"Les forfaits SAP RFI de",common)
t=paragraph(t,"Les trois options conservent",coverage)
t=t.replace("| 306 JH × 850 € = **260 100 €** |","| Forfait Delaware **250 000 €** |",1)
t=t.replace("| 234 JH × 850 € = **198 900 €** |","| Forfait Delaware **450 000 €**, horaires étendus |",1)
t=t.replace("| 420 JH × 850 € = **357 000 €** |","| Forfait Delaware **350 000 €** |")
t=t.replace("Exploitation en heures ouvrées |","Exploitation / supervision |").replace("Évolutions métier, panier de demandes comparable","Évolutions métier, budget retenu")
t=paragraph(t,"Ces montants sont des **hypothèses", "SAP utilise les forfaits source. "+ms+" La souscription couvre le produit standard ; les responsabilités exactes et la capacité des forfaits SAP restent à confirmer.")
t=t.replace("**198,9 k€/an**, calcul par activité en heures ouvrées ; le forfait RFI de 450 k€ reste une référence distincte.","**450 k€/an**, forfait Delaware de monitoring en horaires étendus.")
t=paragraph(t,"Les charges initiales et", "Les charges initiales et compléments fonctionnels restent inchangés. SAP revient aux forfaits Delaware ; FLOW et Microsoft conservent leurs abaques. Les résultats recalculés figurent dans la [note de décision](04-resultats-etude.md).")
t=paragraph(t,"Les budgets représentent", "Les budgets combinent sources et hypothèses explicitement distinguées. Les écarts ne démontrent ni une remise commerciale, ni une équivalence des services. Le service SAP en horaires étendus n’est pas réduit arbitrairement à une capacité en heures ouvrées.")
write("15-rapprochement-buy-france.md",t)

t=read("16-methodes-et-presentation-comparaison-make-buy.md")
t=t.replace("**198,9 k€/an**, panier en heures ouvrées ; forfait RFI distinct conservé en référence.","**450 k€/an**, forfait Delaware en horaires étendus conservé dans le budget.")
t=paragraph(t,"SAP et Microsoft financent",ms)
t=paragraph(t,"Les **60 JH d'exploitation", "Les 60 JH techniques propres à FLOW couvrent configuration du runtime et tests de sauvegarde/restauration. Ils sont supposés pris en charge par le cloud managé Microsoft ; le panier Microsoft garde les contrôles applicatifs/PRA métier. Pour SAP, le contenu détaillé des forfaits reste inconnu.")
t=paragraph(t,"Les forfaits RFI SAP",common+" Aucun abaque n’est ajouté aux forfaits SAP.")
t=t.replace("- **Besoin de service commun, contrats à confirmer.** Heures ouvrées, 240 diagnostics/an et activités opérationnelles comparables. Les responsabilités déjà couvertes par le cloud managé et le standard Buy sont identifiées. Le panier est une hypothèse de l'étude, pas un SLA ni un devis ; les forfaits RFI en horaires étendus restent des références distinctes.",
            "- **Distinguer sources et hypothèses de service.** SAP conserve les forfaits Delaware et leur monitoring en horaires étendus. FLOW/Microsoft sont estimés en heures ouvrées. Les capacités et SLA ne sont pas démontrés équivalents ; les écarts de budget ne sont pas des remises prouvées.")
write("16-methodes-et-presentation-comparaison-make-buy.md",t)

t=read("11-cout-nominal-minimum.md")
t=paragraph(t,"Les trois options conservent", "FLOW et Microsoft conservent 240 diagnostics/an estimés, en plus de la prévention, en heures ouvrées. Les volumes SAP ne sont pas connus ; les forfaits fournisseur restent la base. Voir les [abaques](09-abaques-repartition.md).")
t=paragraph(t,"**L'astreinte FLOW",options)
write("11-cout-nominal-minimum.md",t)
t=read("13-audit-classeur-excel.md").replace("Quantités, JH par unité, responsabilités et options ; trois solutions sur la même base de service.","Forfaits SAP et abaques FLOW/Microsoft, responsabilités et options ; statut des hypothèses explicite.")
t=paragraph(t,"Le nominal compare", common+" Les contributions internes sont exclues ; les options additionnelles restent inactives.")
write("13-audit-classeur-excel.md",t)
t=read("10-audit-estimabilite-et-incertitude.md").replace("Service annuel commun en heures ouvrées, 240 diagnostics/an ; responsabilités standard/extension identifiées, ressources et évolutions séparées.","Forfaits SAP source ; activités FLOW/Microsoft estimées en heures ouvrées. Ressources et évolutions séparées.").replace("Forfaits RFI conservés comme références.","Forfaits SAP conservés dans le budget ; équivalence des services non démontrée.")
write("10-audit-estimabilite-et-incertitude.md",t)

header="![Logo eXalt](assets/exalt-logo.png)\n\n**Laurent Sintès** · 20 octobre 2026\n\n---\n\n"
write("18-corrections-services-et-tracabilite.md",header+"""# Base SAP rétablie et hypothèses Microsoft

## Décision de méthode

"""+common+"""

Le précédent remplacement de la supervision SAP de 450 à 198,9 k€/an supposait une économie de service non démontrée. Il est annulé. Les abaques restent utiles pour Microsoft, dont le forfait de 450 k€ était une transposition SAP et non une offre Microsoft.

## Réconciliation annuelle

| Poste SAP | Avant cette correction | Base retenue | Variation |
| --- | ---: | ---: | ---: |
| MCO | 260 100 € | 250 000 € | −10 100 € |
| Supervision | 198 900 € | 450 000 € | +251 100 € |
| Évolutions | 357 000 € | 350 000 € | −7 000 € |
| **Total hors abonnements/plateformes** | **816 000 €** | **1 050 000 €** | **+234 000 €** |

Ces forfaits se substituent aux abaques SAP abandonnés ; ils ne s’y ajoutent pas. La TMA de 350 k€ ne s’additionne ni à 357 k€ ni à un supplément en pourcentage.

## Comparaison recalculée

| Cumul fournisseur à quinze ans | Version précédente | Version corrigée | Variation |
| --- | ---: | ---: | ---: |
| FLOW | 36,306 M€ | 36,306 M€ | 0 |
| SAP | 46,881716 M€ | """+fr(sap[6],6)+""" M€ | +2,971800 M€ |
| Microsoft | 33,075615 M€ | 33,075615 M€ | 0 |

Le delta SAP se réconcilie : **234 000 €/an × 12,7 années équivalentes de Run = 2 971 800 €**. Les coûts initiaux, licences, plateformes, indexations et dates de livraison restent inchangés. Les forfaits sont proratisés au périmètre livré par convention ; cette montée en charge n’est pas un échéancier contractuel.

Par rapport à la version antérieure à la normalisation (SAP 50,119886 M€), le nouveau total reste inférieur de 0,266370 M€ : retrait du supplément MCO estimé de 13 974 €/an et retour de 357 à 350 k€/an de TMA, sur 12,7 années. Ce choix de budget ne prouve pas que la maintenance des compléments serait gratuite.

## Microsoft : ce qui est estimé

"""+ms+"""

Les diagnostics reprennent une hypothèse commune avec FLOW. Les 30 corrections couvrent toutes les adaptations, interfaces et compléments OMS ; les quatre campagnes de tests et douze revues de pilotage sont des conventions d’activité. L’exploitation chiffre sept activités distinctes ; les évolutions chiffrent 40 règles, 10 fonctions et 4 changements structurants. Aucun de ces volumes n’est présenté comme mesuré ou confirmé par Avanade.

Le passage antérieur de 450 à 198,9 k€ de supervision Microsoft ne représente pas une remise. Le classement Microsoft/FLOW est conditionnel à la suffisance de ces charges, aux prestations couvertes par les abonnements et aux tarifs français retenus.

## Limites conservées

"""+coverage+"\n\n"+options+"""

Les budgets ne sont ni des devis révisés ni une preuve d’économie à prestation identique. Les sources restent dans Références ; les hypothèses et formules sont visibles dans Service annuel et les prix unitaires.

Les [contrôles](14-audit-inflation-run-et-comparaison.md) portent sur le calcul et la traçabilité. La [version précédente](archives/methodes-remplacees/2026-10-20/avant-retablissement-forfaits-sap/18-corrections-services-et-tracabilite.md) est conservée comme historique, sans valeur de budget courant.
""")
print("Study updated; SAP headlines:",sap)
