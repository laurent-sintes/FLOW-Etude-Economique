"""Iteration12 report, derived from frozen results and explicit assumptions."""
import json,html,importlib.util,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def read(n):return json.loads((HERE/n).read_text(encoding="utf-8"))
spec=importlib.util.spec_from_file_location("report07",HERE/"iteration-07-report.py");base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
e=html.escape
def n(x):return f"{x:,.1f}".rstrip("0").rstrip(".").replace(","," ").replace(".",",")
def t(v):return " / ".join(n(x) for x in v)
def p(s):return "<p>"+s+"</p>"
def ul(xs):return "<ul>"+"".join("<li>"+e(x)+"</li>" for x in xs)+"</ul>"
def table(h,rows,caption):return base.table(h,["<tr>"+"".join("<td>"+str(x)+"</td>" for x in row)+"</tr>" for row in rows],caption)
def link(f,label):return '<a href="'+e(f)+'">'+e(label)+'</a>'
def main():
 d=read("iteration-12-resultats.json");h=read("iteration-12-contrat.json");lots=read("iteration-12-lots.json");proof=read("iteration-12-preuves.json");xp=read("iteration-12-experiences.json")
 roles=d["roles"];cal=d["calendar"];pr=d["progress"];sections=[]
 body=base.note(p("<strong>Planification et optimisation : "+n(d["incremental"]["total"][1])+" JH bruts supplémentaires.</strong>")+p("Bas / central / haut : <strong>"+t(d["incremental"]["total"])+" JH</strong>. Délai proposé : <strong>"+t(cal["incremental_public_months"])+" mois</strong>.")+p("Cumul référentiels + stocks + orchestration + planification : <strong>"+n(d["cumulative_estimated"]["total"][1])+" JH centraux</strong>."))
 body+=p("<strong>18 capacités du sous-domaine Plan, BC-028 à BC-045, soit54 fonctions natives.</strong> Le cumul couvre45 capacités avec une proposition de charge sous hypothèses. Ce n’est ni le total du Core System ni un taux de coût couvert.")
 body+=p("Estimation d’ingénierie assistée par IA, <strong>classe C non calibrée</strong>. Les mécanismes observés dans Odoo, Tryton et Axelor éclairent les travaux. Ils ne fournissent pas des JH de réalisation observés. Les chiffres au demi-JH conservent les sommes ; retenir environ2400JH pour l’ordre de grandeur de cette famille.")
 body+=p("<strong>Quatre nouvelles capacités restent particulièrement fragiles :</strong> cibles physiques, protections logiques, règles de réservation et redistribution. Leur comparaison marché est indirecte et leurs plages sont plus larges. Les18 propositions complètes sous hypothèses ne sont pas18 budgets validés.")
 sections.append(("synthese","Résultat et limites",body))
 body=p("<strong>Trois familles de mécanismes :</strong> calculs déterministes de plans, recherche d’affectations admissibles et comparaison de politiques. La présence du mot optimisation n’impose pas un solveur pour chaque capacité.")
 body+=ul(["Odoo/Tryton/Axelor montrent des besoins datés, seuils, minimums/multiples et propositions. Cela ne démontre pas une optimisation globale.","Timefold fournit le moteur de recherche ; le modèle des décisions, contraintes, objectifs et explications reste à construire.","Une première solution déterministe est conservée. Une amélioration n’est retenue que si le validateur indépendant la juge admissible et préférable selon les objectifs déclarés.","Aucune solution trouvée n’est pas une preuve d’impossibilité. Un optimum global ou une probabilité de service ne sont pas promis."])
 body+=p("Référence technique figée : Timefold Solver OSS1.26.0, commit conservé dans les preuves. Le fichier LICENSE examiné est Apache2.0. Le code du gestionnaire conserve ses jobs en mémoire : FLOW finance la persistance des entrées/résultats et une relance depuis instantané. La combinaison cible n’a pas été exécutée ; version supportée et dépendances sont à qualifier dans E121.")
 body+=table(["Propriétaire","Patrimoine réutilisé","Travail supplémentaire"],[[e(x["owner"]),e(x["asset"]),e(x["delta"])] for x in h["reuse"]],"Les financements précédents et les calculateurs métier restent uniques")
 body+=p("Le rôle <strong>Modélisation et optimisation</strong> finance formulation des contraintes, critères, références de contrôle et analyse de qualité. Il est distinct du développement Java et de l’exécution QA. Les règles commerciales Beaumanoir restent un patrimoine d’intégration ; elles ne sont pas toutes inventoriées ni facturées dans ce Core générique.")
 sections.append(("approche","Mécanismes et réutilisation",body))
 body=table(["Financement supplémentaire","Bas JH","Central JH","Haut JH"],[[e(g["id"]+" — "+g["label"])]+[n(v) for v in g["total"]] for g in d["groups"]]+[["TOTAL"]+[n(v) for v in d["incremental"]["total"]]],"Les18 capacités, le moteur et les mécanismes communs")
 body+=p("Travaux propres des capacités : <strong>"+n(d["direct"]["total"][1])+" JH</strong>. Moteur, données/validations communes et qualification/coordination : <strong>"+n(d["common"]["total"][1])+" JH</strong>. Une ligne de capacité seule ne constitue pas un module autonome livrable.")
 body+=p("<strong>Niveau d’évaluation retenu : enveloppe du sous-domaine Plan, décomposition par capacité et lot pour expliquer les écarts.</strong> Les calculs de demande, netting, affectation et simulation sont liés. Les répartir artificiellement en prix indépendants par BC ferait perdre cette dépendance.")
 sections.append(("financement","JH par capacité et mécanisme",body))
 body=table(["Rôle","Planification bas / central / haut JH","Cumul central JH"],[[e(label),t(d["incremental"]["roles"][r]),n(d["cumulative_estimated"]["roles"][r][1])] for r,label in roles.items()]+[["TOTAL",t(d["incremental"]["total"]),n(d["cumulative_estimated"]["total"][1])]],"JH humains bruts, aucun tarif ni gain IA appliqué")
 body+=p("Développement Java + interfaces : <strong>"+t(d["developer_gross_jh"])+" JH</strong>, tests développeur et revues inclus. Modélisation/optimisation : <strong>"+t(d["incremental"]["roles"]["expert_optimisation"])+" JH</strong>, hypothèses de missions détaillées ci-dessous.")
 body+=table(["Unité"]+[e(v) for v in roles.values()]+["Total"],[[e(g["id"])]+[n(g["roles"][r][1]) if g["roles"][r][1] else "—" for r in roles]+[n(g["total"][1])] for g in d["groups"]],"Matrice centrale par unité ; les travaux communs sont présentés séparément")
 body+=table(["Rôle","Base de la charge"],[[e(roles[r]),e(v)] for r,v in lots["role_basis"].items()],"Les rôles décrivent des travaux ; les effectifs ne sont pas supposés interchangeables")
 body+=table(["Lot","Travail du spécialiste modélisation/optimisation"],[[e(x["id"]),e(x["expert_basis"])] for x in d["packages"] if x.get("expert_basis")],"Aucun pourcentage automatique de spécialiste appliqué au développement")
 sections.append(("roles","Charges par rôle",body))
 body=table(["Périmètre","Bas JH","Central JH","Haut JH"],[
 ["Référentiels09"]+[n(v) for v in read("iteration-09-resultats.json")["total"]["total"]],
 ["Stocks10 supplémentaires"]+[n(v) for v in read("iteration-10-resultats.json")["incremental"]["total"]],
 ["Orchestration11 supplémentaire"]+[n(v) for v in read("iteration-11-resultats.json")["incremental"]["total"]],
 ["Planification12 supplémentaire"]+[n(v) for v in d["incremental"]["total"]],
 ["CUMUL PARTIEL"]+[n(v) for v in d["cumulative_estimated"]["total"]]],"Somme des scénarios homogènes, sans ajouter les anciens pilotes partiels")
 body+=p("Les budgets PLAN05/EXEC05 ne sont pas ajoutés. Planning Data Provision10 reste le propriétaire des données de stock publiées ; Process Planning11 reste le propriétaire de la composition des processus. Les algorithmes de décision de cette famille ne refont ni le moteur d’orchestration ni les publications durables.")
 body+=p("Les bornes s’additionnent avec les mêmes hypothèses communes ; aucune indépendance statistique des incertitudes n’est supposée. Le cumul n’inclut pas les43 capacités encore sans comparaison.")
 sections.append(("cumul","Cumul économique",body))
 body=table(["Hypothèse","Contenu retenu"],[[e(a),e(b)] for a,b in h["assumptions"]],"Scénario borné proposé pour estimer ; aucune garantie déjà acquise")
 body+=ul(h["exclusions"])
 body+=p("Les recommandations sont séparées de leur activation. Les contrats des futurs propriétaires Orders/Protection sont simulés par des doubles de test ; leur logiciel réel, les données client et les connecteurs ne sont pas supposés disponibles.")
 sections.append(("hypotheses","Périmètre et garanties attendues",body))
 body=p(e(lots["bounds"]))
 body+=table(["Incertitude","Capacités","Effet"],[[e(x["label"]),e(", ".join(x["caps"])),e(x["effect"])] for x in h["risks"]],"Les fortes réserves viennent du modèle et des données, pas seulement du moteur de recherche")
 body+=table(["Lot","Bas / central / haut JH","Facteurs bas / haut","Travaux et variation"],[[e(x["id"]+" — "+x["label"]),t(x["total"]),e(str(x["factors"][0])+" / "+str(x["factors"][1])),e(x["work"])+"<br><strong>Variation :</strong> "+e(x["range_reason"])] for x in d["packages"]],"26 lots ; les facteurs sont des jugements d’ingénierie, pas des notes de complexité")
 body+=table(["Lot","Actions Java et JH centraux","Actions interface et JH centraux"],[[e(x["id"]),"<br>".join(e(a["action"])+": "+n(a["jh"]) for a in x["java_actions"]),"<br>".join(e(a["action"])+": "+n(a["jh"]) for a in x["frontend_actions"]) or "Sans interface propre"] for x in d["packages"]],"Décomposition révisable ; les durées ne sont pas observées")
 body+=p("Le progrès de couverture ne mesure pas la précision. Aucune capacité nouvelle n’est calibrée empiriquement. Une fourchette de scénario peut éclairer l’investissement, sous réserve de conserver ses limites ; elle ne vaut ni engagement forfaitaire ni P80.")
 sections.append(("incertitude","Fourchettes et provenance des journées",body))
 body=p("<strong>Délai de la famille : "+t(cal["incremental_public_months"])+" mois</strong> (bas / central / haut), après disponibilité des mécanismes réutilisés. Le scénario central représente environ "+n(cal["average_contribution_people"][1])+" personnes de contribution moyenne, avec des pics et spécialités différents.")
 body+=table(["Phase","Bas / central / haut mois","Rôle limitant au centre"],[[e(x["label"]),t(x["duration_months"]),e(roles.get(x["limiting_role"][1],x["limiting_role"][1]))] for x in cal["phases"]],"Durées non arrondies à un mois dans les phases ; arrondi public après somme")
 body+=table(["Phase"]+[e(v) for v in roles.values()],[[e(x["id"])]+[n(x["staff"][r]) for r in roles] for x in cal["phases"]],"Capacité maximale par rôle ; pas effectif plein temps ajouté au budget")
 body+=p("<strong>Durée d’une phase = maximum du plancher de séquence et de la charge de chaque rôle ÷ (capacité du rôle ×18JH/mois).</strong> Les planchers sont proposés, non calibrés ; la coordination est répartie entre phases sans double financement.")
 body+=p(e(lots["schedule"]["dependencies"]))
 body+=p("Enchaînement strict référentiels → stocks → orchestration → planification : <strong>"+t(cal["sequential_public_months"])+" mois</strong>. Ce scénario est une convention de cumul, <strong>pas une prévision optimisée du programme</strong>. Des équipes parallèles et des livraisons progressives nécessiteraient un calendrier distinct. Recrutement, achats et disponibilité effective des sources externes ne sont pas compris.")
 sections.append(("delai","Délais et organisation",body))
 body=p("<strong>Quatre expériences analytiques sur données inventées ont été exécutées.</strong> Elles contrôlent le raisonnement sur les mécanismes, sans mesurer l’effort ni tester Timefold.")
 body+=table(["Question","Résultat et enseignement"],[
 ["Choisir localement le moindre coût suffit-il ?","Deux demandes, deux ressources : le choix local satisfait1 demande ; l’énumération exhaustive des affectations admissibles en satisfait2. La ressource polyvalente doit être gardée pour la demande sans alternative."],
 ["Peut-on déplacer un lien engagé ?","En protégeant le lien deB àS1, A reçoitS2. L’engagement est une contrainte, pas une préférence que le coût peut effacer."],
 ["Prévision100 et commandes60 font-elles160 ?","Sous la règle de consommation testée : résiduel40, besoin total100. Ce n’est pas une politique Beaumanoir déduite."],
 ["Une arrivée au jour5 couvre-t-elle le jour3 ?","20 disponibles au jour3 ; l’arrivée de30 au jour5 ne rend pas50 disponibles plus tôt."]],"Cas explicitement limités, sans extrapolation de performance")
 body+=ul(xp["limits"])
 body+=p("Ces cas distinguent admissibilité, qualité d’une solution et performance. Les campagnes de taille/charge et la qualité réelle des recommandations sont des travaux financés dans Q121/Q122, pas des résultats déjà obtenus.")
 sections.append(("experiences","Ce que les essais ont appris",body))
 lookup={x["id"]:x for x in proof["evidence"]}
 body=table(["Capacité","Fonctions natives","Frontière","Code comparé"],[[e(c["block"]+" — "+c["name"]),"<br>".join(e(f["id"]+" : "+f["resultat"]) for f in c["functions"]),e(c["boundary"])," ".join(link(lookup[k]["url"],k) for k in c["evidence_ids"])] for c in d["coverage"]],"Les54 fonctions sont reliées à un lot propre et à leurs communs ; correspondances partielles, pas couverture ERP totale")
 body+=table(["Preuve","Observation","Limite"],[[link(x["url"],x["id"])+"<br>"+e(x["kind"]),e(x["observed"]),e(x["delta"])] for x in proof["evidence"]],"Code des trois ERP et du solveur, aux versions figées")
 body+=ul(proof["limitations"])
 body+=p("Sources complémentaires : "+link(proof["docs"][0]["url"],"Timefold et Spring")+" ; "+link(proof["docs"][1]["url"],"algorithmes et limites de l’optimisation")+" ; "+link(proof["license"]["url"],"licence du code figé")+".")
 body+=table(["Méthode","Usage effectif"],[[e(k),e(v)] for k,v in d["crosschecks"].items()],"Aucune confrontation chiffrée de trois méthodes prétendue ; pas de nouvelle productivité observée")
 sections.append(("marche","Correspondances marché",body))
 body=table(["Indicateur","Avant","Après"],[
 ["Capacités distinctes comparées","30 /88","45 /88 (+15), soit51%"],
 ["Propositions complètes sous hypothèses","27 /88","45 /88 (+18), soit51%"],
 ["Autres études partielles","3","0"],
 ["Capacités restant à comparer","58","43"],
 ["Capacités calibrées empiriquement","0","0"],
 ["Nouvelles capacités avec fortes réserves explicites","—","4 /18"]],"L’absence d’étude partielle restante ne signifie pas absence d’incertitude")
 old=read("iteration-07-resultats.json");selected=[c for c in old["coverage"] if c["id"] in set(pr["cumulative_ids"])]
 body+=table(["Famille","Capacités étudiées cumulées"],[[name,"<br>".join(e(c["block"]+" — "+c["name"]) for c in selected if c["path_names"][1]==name)] for name in dict.fromkeys(c["path_names"][1] for c in selected)],"Liste cumulative des45 capacités, identifiants uniques")
 body+=p("Master Planning, Supply Assignment et Simulation & Analysis étaient déjà partiellement étudiées ; elles ne sont pas comptées deux fois. Les15 autres capacités apportent une comparaison nouvelle, parfois indirecte et fortement réservée.")
 body+=p("<strong>Progrès :</strong> périmètre Plan couvert par des propositions de charge, réutilisation explicite et rôle d’optimisation dimensionné. <strong>Fragilité persistante :</strong> qualité des entrées, objectifs et recouvrements de droits, qualité des solutions à grande taille, activation des propositions.")
 body+=p("<strong>Une autre itération vaut le coup sur les commandes et engagements.</strong> Elle ajoutera du périmètre et précisera les contrats de destinataires utilisés ici et par l’orchestration. Refaire les mêmes estimations de politiques sans modifier les hypothèses apporterait peu. Une exigence d’optimum global, de planification multi-échelons ou de garantie de service exigerait une autre variante, pas un simple ajustement de coefficient.")
 body+=p(str(len(d["checks"]))+" contrôles de cohérence, couverture, calendrier et empreintes passent. Aucun changement du modèle économique actif, des sources métier ou des audits précédents ; aucun commit ou déploiement.")
 body+=p("Dossier : "+link("iteration-12-resultats.json","résultats")+" · "+link("iteration-12-contrat.json","hypothèses")+" · "+link("iteration-12-lots.json","lots et bases")+" · "+link("iteration-12-preuves.json","preuves")+" · "+link("iteration-12-experiences.json","expériences")+" · "+link("iteration-12-estimation.py","calcul")+" · "+link("iteration-11.html","rapport précédent"))
 sections.append(("avancement","Progression et décision de poursuite",body))
 nav="".join('<a href="#'+i+'">'+e(title)+'</a>' for i,title,_ in sections)
 css=base.STYLE+" main p,main li{overflow-wrap:anywhere}"
 output='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FLOW — Planification et optimisation — Itération12</title><style>'+css+'</style></head><body><a class="skip" href="#synthese">Aller au contenu</a><header class="hero"><div class="eyebrow">FLOW · Étude d’opportunité · Itération12</div><h1>Planification et optimisation : charge supplémentaire et cumul</h1><p>Dix-huit capacités, des calculateurs métier et un solveur réutilisé.</p><p class="small">29 octobre2026 · Proposition de classe C · Sources actives inchangées</p></header><div class="layout"><nav class="toc"><strong>Dans ce rapport</strong>'+nav+'</nav><main>'+''.join(base.section(i,title,body) for i,title,body in sections)+'</main></div><footer>Cumul partiel d’opportunité ; aucune garantie d’optimum ni probabilité de livraison revendiquée.</footer></body></html>'
 # Improve spacing in fixed French prose, without modifying data or calculations.
 for a,z in [("soit54","soit 54"),("couvre45","couvre 45"),("environ2400JH","environ 2 400 JH"),("Les18","Les 18"),("des18","des 18"),("pas18","pas 18"),("OSS1.26.0","OSS 1.26.0"),("Apache2.0","Apache 2.0"),("les43","les 43"),("Les54","Les 54"),("des45","des 45"),("Les15","Les 15"),("soit51%","soit 51%"),("Itération12","Itération 12"),("octobre2026","octobre 2026"),("satisfait1","satisfait 1"),("satisfait2","satisfait 2"),("deB","de B"),("àS1","à S1"),("reçoitS2","reçoit S2"),("Prévision100","Prévision 100"),("commandes60","commandes 60"),("font-elles160","font-elles 160"),("résiduel40","résiduel 40"),("total100","total 100"),("jour5","jour 5"),("jour3","jour 3"),("de30","de 30"),("pas50","pas 50")]:output=output.replace(a,z)
 (HERE/"iteration-12.html").write_text(output,encoding="utf-8")
 print(json.dumps({"report":"iteration-12.html","sections":len(sections)}))
if __name__=="__main__":main()
