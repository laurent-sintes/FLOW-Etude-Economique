"""Render estimate09 from audit JSON; no economic calculations."""
import json, html, importlib.util, sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def read(n):return json.loads((HERE/n).read_text(encoding="utf-8"))
spec=importlib.util.spec_from_file_location("report07",HERE/"iteration-07-report.py")
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
esc=html.escape
def n(x):
 return f"{x:,.1f}".rstrip("0").rstrip(".").replace(","," ").replace(".",",")
def trip(v):return " / ".join(n(x) for x in v)
def p(s):return "<p>"+s+"</p>"
def ul(v):return "<ul>"+"".join("<li>"+esc(x)+"</li>" for x in v)+"</ul>"
def link(file,label):return '<a href="'+file+'">'+label+'</a>'
def tbl(headers,rows,caption):
 return old.table(headers,["<tr>"+"".join("<td>"+str(c)+"</td>" for c in row)+"</tr>" for row in rows],caption)
def main():
 d=read("iteration-09-resultats.json");h=read("iteration-09-hypotheses.json");proof=read("iteration-07-marche-preuves.json")
 roles=d["roles"];sections=[]
 body=old.note(p("<strong>Proposition centrale : "+n(d["total"]["total"][1])+" JH bruts — environ 1 000 JH.</strong>")+
 p("Scénarios bas / central / haut : <strong>"+trip(d["total"]["total"])+" JH</strong>. Délai de l’ensemble : <strong>"+trip(d["calendar"]["public_months_ceiling"])+" mois</strong>, sous l’organisation indiquée ci-dessous."))
 body+=p("Cette estimation couvre la construction initiale des six capacités de référentiels opérationnels, leur socle, leurs mécanismes communs et leur qualification. <strong>Ce n’est pas le total du Core System.</strong> Les travaux génériques restent séparés des adaptations Beaumanoir.")
 body+=p("Classe C : estimation d’ingénierie assistée par IA, utilisable comme proposition conditionnelle pour l’étude d’opportunité. Les charges ne sont pas observées. Le centre est un scénario de travail, sans probabilité associée. Les demi-journées servent seulement à conserver les sommes ; elles ne décrivent pas la précision réelle.")
 body+=p("<strong>Origine des chiffres :</strong> les lots et centres M1 de l’itération07 sont repris et réexaminés. Onze lots sont amendés explicitement : le centre passe de 904 à "+n(d["total"]["total"][1])+" JH, soit +"+n(d["central_delta_vs_m1"])+" JH. Les bornes sont reconstruites par lot avec des causes de variation différentes. Il ne s’agit ni d’une nouvelle mesure, ni d’une moyenne M1/M2.")
 sections.append(("synthese","Estimation proposée",body))
 body=p("Chaque ligne possède son financement. Les travaux propres ne sont pas des coûts autonomes de capacités livrables : ils utilisent les trois ensembles communs. La ligne BC-002 porte ses parcours ; le moteur d’import et de rejet est financé dans les mécanismes communs et sert les cinq familles de données.")
 body+=tbl(["Périmètre financé","Bas JH","Central JH","Haut JH"],[[esc(g["label"])]+[n(v) for v in g["total"]] for g in d["groups"]]+[["TOTAL"]+[n(v) for v in d["total"]["total"]]],"Financement unique des six capacités et de leurs communs")
 body+=ul(["Socle technique : architecture, projet, SQL et migrations, identité et autorisations, livraison des trois environnements, sauvegarde/restauration, composants d’interface et outillage.",
 "Mécanismes communs des référentiels : réception API/CSV, compatibilité de deux versions, identité et autorité des contributions, cohérence et publication, rejets/rejeu, historique/export/usages/purge et réconciliation après restauration.",
 "Conception et qualification transverses : contrats génériques, cohérence des parcours et états de reprise, QA fonctionnelle et de charge, sécurité, corrections associées, documentation et coordination. Ce sont des activités partagées, pas seulement des composants de code."])
 body+=p("Les communs totalisent <strong>"+n(d["common"]["total"][1])+" JH centraux</strong> et les travaux propres <strong>"+n(d["direct"]["total"][1])+" JH</strong>. Ils ne sont pas répartis en six parts égales. Lors de l’extension à d’autres familles, on reprendra seulement les extensions nécessaires et on financera une seule fois le socle déjà retenu. La réutilisation exacte devra rester explicitée.")
 sections.append(("financement","Capacités et mécanismes communs",body))
 body=tbl(["Rôle","Bas / central / haut JH","Dont communs, central","Dont propres, central"],[[esc(label),trip(d["total"]["roles"][r]),n(d["common"]["roles"][r][1]),n(d["direct"]["roles"][r][1])] for r,label in roles.items()]+[["TOTAL",trip(d["total"]["total"]),n(d["common"]["total"][1]),n(d["direct"]["total"][1])]],"JH bruts de tous les rôles")
 body+=p("Développement Java + interface : <strong>"+trip(d["developer_gross_jh"])+" JH</strong>, tests développeur et revues de code inclus. La QA indépendante, l’architecture et les autres rôles sont ajoutés une seule fois dans le total tous rôles. Aucun tarif ni gain IA n’est appliqué.")
 body+=tbl(["Unité"]+[esc(x) for x in roles.values()]+["Total"],[[esc(g["id"])]+[n(g["roles"][r][1]) if g["roles"][r][1] else "—" for r in roles]+[n(g["total"][1])] for g in d["groups"]],"Matrice centrale par unité et rôle — les tirets renvoient aux travaux communs lorsque le rôle y est financé")
 body+=p("La QA métier, la conception UX des vues et la coordination sont financées transversalement ; leur absence dans une ligne propre ne signifie pas que la capacité est livrée sans ces activités. Aucun prorata de ces charges n’est inventé par capacité.")
 sections.append(("roles","Charges par rôle et par unité",body))
 body=ul(h["assumptions"])
 body+=p("<strong>Exclusions :</strong>")+ul(h["exclusions"])
 body+=p("Les moyens SQL, de livraison et de reprise laissés indéterminés dans le comptage de code08 sont ici estimés directement en travail humain, sous ces hypothèses. Leur taille en lignes de code n’est pas nécessaire au calcul09. Les garanties sont des cibles à qualifier pendant les travaux financés, pas des résultats déjà obtenus.")
 sections.append(("hypotheses","Hypothèses qui rendent le chiffrage possible",body))
 body=p("La fourchette provient des reprises techniques et des cycles de correction supposés, pas d’un score de complexité métier. Le scénario bas conserve les fonctions et la qualification, avec peu de reprises. Le haut anticipe plusieurs corrections des mécanismes sensibles.")
 body+=p("<strong>Formule par lot et rôle :</strong> central = jugement d’ingénierie décrit ; bas = central × facteur bas ; haut = central × facteur haut, arrondis à la demi-journée. Les facteurs ci-dessous sont eux-mêmes des hypothèses de l’analyste. Total = somme des lots financés une seule fois. Les scénarios restent corrélés ; aucune réduction de marge par indépendance supposée.")
 body+=tbl(["Lot","Objet","Bas / central / haut JH","Facteurs bas / haut","Cause principale"],[[x["id"],esc(x["label"]),trip(x["total"]),str(x["uncertainty"]["low_factor"]).replace(".",",")+" / "+str(x["uncertainty"]["high_factor"]).replace(".",","),esc(x["uncertainty"]["cause"])] for x in d["packages"]],"Sensibilité par lot — facteurs explicites de jugement")
 body+=p("Une nouvelle exigence — règles libres, volumes nettement supérieurs, reprise sans participation des sources ou multi-région — constitue une variante de périmètre à chiffrer, pas un risque automatiquement couvert par la borne haute.")
 body+=p("La classe C est conservée pour toutes les charges. Aucun P50, P80 ou pourcentage de probabilité n’est déduit de cette enveloppe. La sensibilité reste forte, principalement sur la publication, la reprise et la qualification.")
 sections.append(("incertitude","Fourchette et causes d’incertitude",body))
 cal=d["calendar"];body=p("Le calendrier est construit à partir des charges par rôle et de quatre phases successives. Les travaux d’une phase peuvent être parallélisés selon les capacités ci-dessous. Le scénario central représente environ <strong>"+n(cal["average_contribution_people"][1])+" personnes en contribution moyenne</strong>, avec davantage de spécialistes ponctuels.")
 body+=old.note(p("<strong>"+trip(cal["public_months_ceiling"])+" mois</strong> pour les scénarios bas / central / haut. Délais calculés avant arrondi : "+trip(cal["total_months"])+" mois. Les arrondis au mois supérieur évitent de promettre une date à la semaine."))
 body+=tbl(["Phase séquentielle","Bas / central / haut, mois","Facteur limitant central"],[[esc(x["label"]),trip(x["duration_months"]),esc(roles.get(x["limiting_role"][1],"Durée minimale de phase"))] for x in cal["phases"]],"Planning de capacité, pas engagement de livraison")
 body+=tbl(["Rôle"]+[x["id"] for x in cal["phases"]],[[esc(label)]+[n(ph["staff"][r]) for ph in cal["phases"]] for r,label in roles.items()],"Capacité mobilisable par rôle et phase — 0,5 signifie une demi-disponibilité ; ne pas additionner les colonnes")
 body+=p("<strong>Formule :</strong> durée de phase = maximum du plancher de phase et de JH du rôle ÷ (personnes mobilisables × 18 JH/mois). Délai total = somme des quatre phases. Les planchers bas/central/haut sont P1 1,5/2/2,5 mois, P2 2/2,5/3, P3 1,5/2/2,5 et P4 1,5/2/3 : conventions de séquencement et validation, sans mesure historique.")
 body+=p("Les quatre séquences de coordination par phase P2, P3 et P4 sont financées une seule fois dans Q704, puis réparties dans le calendrier. Il faut pouvoir mobiliser jusqu’à trois développeurs Java en P2/P3, deux développeurs d’interface en P3 et deux QA en P4 ; les autres compétences interviennent selon leur charge. Les capacités indiquées sont des plafonds de disponibilité, pas des recrutements ni des jours facturés à plein temps pendant toute la phase.")
 body+=ul(h["schedule"]["limits"])
 body+=p("Les 18 JH/mois sont une convention de disponibilité du planning09. Le délai COCOMO08, fondé sur du code partiel et une convention différente, reste conservé dans son audit ; il n’est pas ajouté ni utilisé pour ajuster ce planning. Un scénario avec moins de personnes doit être recalculé.")
 sections.append(("delai","Délai et organisation de réalisation",body))
 body=p("Les comparaisons existantes avec Odoo, Tryton et Axelor sont réutilisées. Les fichiers de code référencés ont été contrôlés par empreinte. Il n’y a pas de nouvelle observation de productivité. Les fonctions et écarts ci-dessous expliquent les travaux ; les temps restent estimés.")
 rows=[]
 pd={x["id"]:x for x in proof["proofs"]}
 for c in d["coverage"]:
  pr=sorted({pid for f in c["functions"] for pid in f["proof_ids"]})
  refs=" ".join('<a href="'+esc(pd[pid]["url"])+'">'+esc(pid)+'</a>' for pid in pr)
  notes="<br>".join(esc(f["native_result"]+" : "+f["conclusion"]) for f in c["functions"])
  rows.append([esc(c["block"]+" — "+c["name"]),notes,refs])
 body+=tbl(["Capacité","Fonctions et limites de la comparaison","Preuves de code"],rows,"Marché → différences FLOW → travaux financés")
 body+=p("Spring apporte les moyens techniques de base : API, sécurité, persistance, transactions et exécution des traitements. Les protocoles métier d’autorité, de version, de publication et de reprise restent à composer. Aucun code ERP n’est déclaré directement réutilisé dans Spring, aucune remise générique supplémentaire n’est appliquée.")
 body+=ul(list(d["crosschecks"].values()))
 sections.append(("preuves","Appui sur le marché et limites",body))
 body=p("<strong>Cumul : 20 capacités comparées sur 88, sans nouvelle capacité dans cette itération.</strong> Les six de la famille disposent maintenant d’une proposition complète de JH par rôle sous hypothèses. Les 14 autres étudiées restent partielles et 68 restent sans estimation comparative.")
 body+=p("Les six propositions conditionnelles ne sont pas six calibrations nouvellement acquises : le niveau de preuve reste C. Le progrès est une base de décision explicitement assumée, une séparation des communs et un calendrier chargé par rôle ; aucune amélioration statistique de précision n’est revendiquée.")
 body+=p("<strong>Suite utile :</strong> poursuivre sur une autre famille avec cette méthode. Réitérer sur ces six seulement pour une omission, un double compte ou une hypothèse majeure nouvelle. Le JH global du Core demeure inconnu ; aucun montant antérieur n’est ajouté à cette famille.")
 body+=tbl(["Lot amendé","Motif et nouvelle base"],[[pid,esc(v["reason"])] for pid,v in h["central_revisions"].items()],"Amendements explicites de M1 — les nouveaux centres remplacent les anciens")
 body+=ul(["Sources et paramètres actifs inchangés. Aucun commit, publication ou application économique.",
 str(len(d["checks"]))+" contrôles de sommes, couverture, financement unique, capacité par phase et intégrité. Ils ne prouvent ni productivité ni atteinte des garanties."])
 body+=p("Pièces : "+link("iteration-09-resultats.json","résultats détaillés")+" · "+link("iteration-09-hypotheses.json","hypothèses et facteurs exacts")+" · "+link("iteration-09-estimation.py","calcul reproductible")+" · "+link("iteration-07-contrat-v1.1.json","contrat de référence")+" · "+link("iteration-07.html","estimations07")+" · "+link("iteration-08.html","sensibilités08"))
 sections.append(("suite","Avancement et suite",body))
 nav="".join('<a href="#'+i+'">'+esc(t)+'</a>' for i,t,b in sections)
 page='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FLOW — Estimation des six capacités de référence — Itération09</title><style>'+old.STYLE+'</style></head><body><a class="skip" href="#synthese">Aller au contenu</a><header class="hero"><div class="eyebrow">FLOW · Étude d’opportunité · Itération09</div><h1>Six capacités, leurs communs et leur charge</h1><p>Une estimation d’ingénierie par rôle, fondée sur les comparaisons marché existantes et des hypothèses explicites de réalisation.</p><p class="small">29 octobre 2026 · Proposition conditionnelle · Sources actives inchangées</p></header><div class="layout"><nav class="toc"><strong>Dans ce rapport</strong>'+nav+'</nav><main>'+''.join(old.section(i,t,b) for i,t,b in sections)+'</main></div><footer>Les chiffres de cette famille ne constituent pas le budget du Core System complet.</footer></body></html>'
 (HERE/"iteration-09.html").write_text(page,encoding="utf-8")
 print(json.dumps({"report":"iteration-09.html","sections":len(sections)}))
if __name__=="__main__":main()
