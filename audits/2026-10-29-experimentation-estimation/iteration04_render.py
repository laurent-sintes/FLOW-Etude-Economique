from html import escape
LABELS={"analyse_produit":"Analyse produit","architecture":"Architecture","dev_java":"Développement Java / Spring","dev_frontend":"Développement des interfaces","ux":"Conception des interactions (UX)","qa":"QA indépendante","plateforme":"Environnement et livraison","securite":"Expertise sécurité","coordination":"Coordination technique"}
GROUPS={"COMMON":"Socle commun","REF":"Références produits / variantes","STOCK":"Stock / réservations"}
def e(v):return escape(str(v),quote=True)
def n(v):return f"{v:g}".replace(".",",")
def span(v):return n(v[0])+" – "+n(v[2])
def p(v):return "<p>"+e(v)+"</p>"
def ul(values):return "<ul>"+"".join("<li>"+e(v)+"</li>" for v in values)+"</ul>"
def table(headers,rows):return "<div class='scroll'><table><thead><tr>"+"".join("<th scope='col'>"+e(h)+"</th>" for h in headers)+"</tr></thead><tbody>"+"".join("<tr>"+"".join("<td>"+str(c)+"</td>" for c in row)+"</tr>" for row in rows)+"</tbody></table></div>"
def render(r,d):
 inc=d["iteration-04-incertitude.json"];method=d["iteration-04-methode-candidate.json"];interp=d["iteration-04-interpretation.json"];qa=d["iteration-04-parcours-qa.json"];prior=d["iteration-03-resultats.json"]
 total=r["technical_tests"]["distinct_tests"];passed=sum(c["passed"] for s in r["technical_tests"]["selected_suites"] for c in s["cases"])
 body=["<header><div class='eyebrow'>FLOW · ÉTUDE D’OPPORTUNITÉ · 29 OCTOBRE 2026</div><h1>Itération 04 — qualifier l’incertitude</h1><p>Des classes explicites par ensemble et rôle, des responsabilités précisées et deux témoins techniques bornés.</p></header>"]
 body.append("<section id='conclusion'><h2>Des fondements plus lisibles, des JH encore non calibrés</h2><div class='key'><strong>25 contributions en classe C</strong><p>Deux postes sans contribution distincte restent sans classe. La classe qualifie le fondement de l’estimation ; elle ne note pas la complexité de la capacité métier.</p></div>")
 body.append(f"<p><strong>{n(r['m1_jh'][1])} JH centraux, plage {span(r['m1_jh'])} JH : montants inchangés.</strong> Ce panier couvre partiellement six capacités. Le total du Core System reste inconnu. Le contrepoint M2 demeure {n(r['m2_jh'][1])} JH, conservé séparément.</p>")
 body.append(f"<p><strong>{passed} essais distincts réussis sur {total}</strong> dans les exécutions retenues. Ces essais vérifient des garanties locales de reprise et de cohérence. Ils ne mesurent pas une durée humaine et ne font pas passer une estimation de C à B.</p>")
 body.append("<p>Le gain de cette itération est de relier chaque chiffre à son niveau de preuve, à sa principale inconnue et au travail d’investigation utile. Les garanties examinées précisent les travaux déjà financés ; aucune réduction de charge n’en est déduite.</p>")
 body.append("<p><strong>Recommandation : poursuivre sur les familles réservées.</strong> Clore les prototypes actuels et appliquer la méthode figée à l’orchestration de processus puis à la planification et l’optimisation.</p></section>")
 body.append("<section id='classes'><h2>Lire la classe et la fourchette séparément</h2>")
 body.append(table(["Classe","Fondement de l’estimation"],[
 ["<strong>A — Calibrée et vérifiée</strong>","Efforts mesurés comparables ; calibration confrontée à des réalisations distinctes de celles utilisées pour l’ajustement."],
 ["<strong>B — Étayée par des réalisations</strong>","Transposition explicite d’efforts mesurés, avec périmètre, rôles, stack, équipe et qualité comparables."],
 ["<strong>C — Argumentée</strong>","Travaux et durées proposés par un raisonnement d’ingénierie documenté ; aucune calibration empirique."],
 ["<strong>D — Fragile</strong>","Une estimation numérique existe, mais sa justification est insuffisante."],
 ["<strong>Sans classe</strong>","Inconnu, inclus ailleurs, sans objet ou rôle non mobilisé distinctement : ces états ne constituent pas des classes."]]))
 body.append("<p>Cette grille est une convention FLOW. Elle n’est pas un barème officiel de précision. Une plage étroite n’améliore pas la classe ; un test technique réussi ne prouve pas les jours nécessaires pour construire le produit.</p>")
 body.append("<p>Une estimation totale étayée peut avoir une ventilation par rôle fragile. La classe porte donc sur <strong>ensemble × rôle × périmètre</strong>. Les lettres ne se moyennent pas ; les contributions fragiles et les hypothèses communes restent visibles dans les agrégations.</p>")
 body.append("<p>Aucun P50/P80 n’est calculé. Les bornes actuelles restent des scénarios de sensibilité. Un percentile futur exigerait des distributions et dépendances explicites, avec un statut de validation annoncé. La somme des P80 ne serait généralement pas le P80 du total.</p>")
 body.append("<p>Repères de méthode : <a href='https://www.gao.gov/assets/d20195G.pdf'>GAO, analyse des risques et incertitudes</a> ; <a href='https://library.aacei.org/pgd02/pgd02.shtml'>AACE, maturité et analyse quantitative des risques</a>. Aucun taux de productivité n’en est tiré.</p></section>")
 body.append("<section id='jh'><h2>JH par rôle et qualification</h2>")
 rows=[]
 for role,triplet in prior["estimates"]["M1"]["by_role"].items():
  cells=[next(c for c in inc["assessments"] if c["ensemble"]==g and c["role"]==role) for g in GROUPS]
  values=[]
  for c in cells:
   if c["solidity_class"] is not None:values.append(n(c["jh"][1])+" · "+c["solidity_class"])
   elif c["role"]=="plateforme":values.append("Inclus dans COMMON")
   else:values.append("Pas de revue spécialisée distincte")
  rows.append([e(LABELS[role])]+values+[n(triplet[1]),span(triplet)])
 rows.append(["<strong>Total du panier</strong>"]+[n(prior["estimates"]["M1"]["lots"][g]["total_jh"][1]) for g in GROUPS]+["<strong>"+n(r["m1_jh"][1])+"</strong>",span(r["m1_jh"])])
 body.append(table(["Contribution","Socle · JH / classe","Références · JH / classe","Stock · JH / classe","Total central · JH","Bas – haut · JH"],rows))
 body.append("<p>Neuf contributions possibles, pas neuf personnes. Les tests développeur sont compris dans le développement. QA indépendante, architecture, coordination et revues spécialisées sont identifiées séparément.</p>")
 body.append("<p>La plateforme STOCK est financée dans le commun, avec migrations applicatives dans le développement. Le zéro sécurité STOCK ne signifie pas sécurité gratuite : développement/QA vérifient les contrôles prévus ; aucune revue spécialisée distincte n’est incluse dans M1.</p>")
 body.append("<div class='note'>Variante ouverte : revue spécialisée de sécurité STOCK. Son contenu et ses JH restent inconnus. Les 5 JH du contrepoint M2 ne sont ni adoptés automatiquement ni absorbés dans COMMON.</div>")
 body.append("<p>Restitution métier inchangée : références au sous-domaine Operational References, stock à la Business Area Inventory State Management, socle commun au domaine. Les coûts remontent sans duplication ni prorata par nombre de capacités. <a href='iteration-03.html#maille'>Voir la restitution native de l’itération 03</a>.</p></section>")
 body.append("<section id='incertitudes'><h2>Ce qui rend chaque estimation incertaine</h2><p>Ces causes servent à choisir une investigation utile. Elles ne sont pas transformées en multiplicateurs.</p>")
 for g in GROUPS:
  body.append("<h3>"+e(GROUPS[g])+"</h3>")
  rows=[]
  for c in inc["assessments"]:
   if c["ensemble"]!=g:continue
   state=c["solidity_class"] or ("Inclus COMMON" if c["role"]=="plateforme" else "Non mobilisé distinctement")
   rows.append([e(LABELS[c["role"]]),e(state)+"<br>"+n(c["jh"][1])+" JH · "+span(c["jh"]),
                e(c["justification"]),e(c["uncertainty_cause"]),e(c["next_evidence"])])
  body.append(table(["Rôle","Classe / central / plage","Fondement","Cause dominante","Preuve suivante utile"],rows))
 body.append("<h3>Hypothèses communes</h3>"+ul(x["text"] for x in inc["common_assumptions"]))
 body.append("<h3>Données manquantes</h3>"+ul(x["description"] for x in inc["missing_data"]))
 body.append("<p>Les difficultés communes peuvent déplacer plusieurs estimations dans le même sens. Leur incertitude ne disparaît pas lorsqu’on additionne les rôles ou remonte au domaine.</p></section>")
 body.append("<section id='preuves'><h2>Ce que les essais ont réellement établi</h2>")
 rows=[]
 for s in r["technical_tests"]["selected_suites"]:
  ok=sum(c["passed"] for c in s["cases"])
  rows.append([e(GROUPS[s["family"]]),str(ok)+"/"+str(s["tests"]),e(s["run"]),"<a href='"+e(s["report"])+"'>Rapport d’essais XML</a>"])
 body.append(table(["Témoin","Réussites","Passage retenu","Preuve d’exécution"],rows))
 body.append("<p>Le premier passage a réussi les six tests STOCK et quatre tests REF. Le traitement des 10 000 lignes a dépassé la limite de 180 secondes. Un seul second passage REF a utilisé une limite de 900 secondes et des fichiers de sortie séparés. Le code métier, les données, les transactions par ligne et la durabilité PostgreSQL sont restés identiques.</p>")
 body.append("<p>Le lanceur Windows avait aussi attendu la fermeture d’un canal de sortie hérité par le serveur. Cette capture a été corrigée avant les essais. Ces incidents de harnais sont conservés dans le <a href='iteration-04-execution-journal.json'>journal d’exécution</a> ; ils ne sont pas présentés comme des défauts métier.</p>")
 readable={
 "tenThousandRowsRecoverAcrossRealJvmTermination":"Import de 10 000 lignes : variantes avant parents, arrêt JVM après 211 commits, reprise dans une nouvelle JVM, compteurs et contenu contrôlés.",
 "crashInsideLineRollsBackObjectAndDurableLineTogether":"Arrêt JVM pendant une création : objet/effet absents, lignes en attente puis relance sans double application.",
 "rejectedVariantIsDurableAndOnlyCorrectedContributionIsReplayed":"Rejet conservé et contribution corrigée distincte, sans réappliquer le produit déjà accepté.",
 "versionAuthorityAndAbsentObjectsHaveExplicitOutcomes":"Versions identiques, conflictuelles ou anciennes ; conflit d’autorité ; objets absents du nouveau fichier conservés.",
 "malformedLineDoesNotPreventFollowingValidLine":"Ligne mal formée ou champ obligatoire absent : rejets sans empêcher la ligne valide.",
 "twoRequestsForSevenShareTenWithAnObservedDatabaseLockWait":"Deux demandes concurrentes de 7 sur un physique de 10 : résultats 7 + 3, réconciliation et attente de verrou observée.",
 "concurrentFirstUseMaterializesOneKeyWithoutLosingEitherReceipt":"Première création concurrente d’une clé absente : une seule position, deux apports conservés.",
 "concurrentDuplicateHasOneEffectAndChangedPayloadIsAConflict":"Doublon concurrent : résultat mémorisé, un seul effet ; contenu différent refusé.",
 "technicalFailureBeforeCommitLeavesNoDurableEffectAndCanBeRetried":"Échec technique avant commit : rollback de la position, du journal, de l’engagement et du résultat mémorisé ; nouvelle tentative possible.",
 "lostResponseAfterCommitIsReplayedEvenWhenCurrentStateLaterChanges":"Réponse perdue simulée après commit : la relance renvoie le résultat initial sans effet supplémentaire.",
 "consumeThenRefuseCompensationRetainRefusalAndAcceptNewIntentionAfterRelease":"Consommation : physique/réservé 10/6 → 8/4 ; compensation −5 refusée ; même clé garde le refus ; après libération, nouvelle clé admise."
 }
 for s in r["technical_tests"]["selected_suites"]:
  body.append("<h3>"+e(GROUPS[s["family"]])+"</h3>")
  body.append(table(["Essai","Résultat"],[[e(readable.get(c["name"],c["name"])),"Réussi" if c["passed"] else "Non démontré : "+e(c["issue"])] for c in s["cases"]]))
 body.append("<p>Les durées d’exécution sont archivées pour tracer l’investigation. Elles ne constituent ni une productivité humaine, ni un débit de production, ni une validation des JH. Le nombre de tests réussis ne donne pas une probabilité de succès du projet.</p>")
 body.append("<h3>Environnement effectivement exécuté</h3>"+p(r["runtime"]["java"])+p(r["runtime"]["postgresql"]))
 body.append("<p>Spring JDBC et TransactionTemplate 6.2.12, dépendances du BOM Boot 3.5.7, pilote PostgreSQL 42.7.8. Les tests ne valident ni une application Boot complète ni Spring Batch. Runtimes portables, base isolée, données générées et serveur arrêté après les passages.</p>")
 body.append("<p><a href='iteration-04-runtime.json'>Versions et empreintes des runtimes</a> · <a href='iteration-04-run-initial.log'>Journal du premier passage</a> · <a href='iteration-04-run-ref-final.log'>Journal du second passage REF</a> · <a href='iteration-04-run.py'>Lanceur reproductible</a></p></section>")
 body.append("<section id='limites'><h2>Limites et effet sur les travaux</h2>")
 for proto in interp["prototypes"]:
  body.append("<article><h3>"+e(GROUPS[proto["id"]])+"</h3>"+p(proto["mechanism"])+p(proto["work_impact"])+ul(proto["limitations"]))
  body.append("<p>Travaux concernés : "+e(", ".join(proto["packages"]))+".</p><p>"+" · ".join("<a href='"+e(x)+"'>"+e(x.split("/")[-1])+"</a>" for x in proto["code"])+"</p></article>")
 body.append(p(interp["effort_decision"]["reason"]))
 body.append("<p>La même source imposée au parent et à la variante, les quantités entières et l’unité unique sont des restrictions des témoins. Elles ne réduisent pas silencieusement le périmètre de l’estimation03.</p></section>")
 body.append("<section id='responsabilites'><h2>Un propriétaire pour chaque travail</h2>"+p(inc["responsibility_policy"]))
 body.append(table(["Travail","Financement","Rôle responsable","Frontière"],[[e(x["task"]),e(x["financing_owner"])+" · "+e(", ".join(x["package_refs"])),e(" / ".join(LABELS.get(role,role) for role in x.get("responsible_roles",[x.get("responsible_role", "Non attribue")])) ),e(x["boundary"])] for x in inc["responsibilities"]]))
 body.append("<h3>Les cinq vues restent à réaliser</h3>"+p(qa["status"]))
 body.append(table(["Vue","États à prendre en charge","Actions","Limite actuelle"],[[e(v["name"]),"<br>".join(e(x) for x in v["states"]),"<br>".join(e(x) for x in v["actions"]),e(v["open"])] for v in qa["views"]]))
 body.append(p(qa["interpretation"])+"</section>")
 body.append("<section id='methode'><h2>Version candidate à éprouver sur d’autres familles</h2>"+p(method["status"])+p(method["estimation_unit"])+p(method["decomposition_rule"]))
 body.append(table(["Étape","Règle figée"],[[e(str(x["n"])+". "+x["label"]),e(x["rule"])] for x in method["steps"]]))
 body.append("<h3>Place des trois références de méthode</h3>"+table(["Référence","État actuel"],[[e(k),e(v)] for k,v in method["methods"].items()]))
 body.append("<p>La confrontation numérique COSMIC / COCOMO II / ISBSG demeure incomplète. La réussite technique de ces témoins ne comble pas l’absence de références d’effort admissibles.</p></section>")
 body.append("<section id='suite'><h2>Une nouvelle itération vaut-elle le coût ?</h2><div class='key'><strong>Oui, sur les familles réservées</strong>"+p(r["recommendation"]["value"])+"</div>")
 body.append("<p>Les prototypes références et stock s’arrêtent ici, avec leurs limites documentées. La prochaine expérience porte sur <strong>l’orchestration de processus</strong> et <strong>la planification et l’optimisation</strong>, en appliquant la même règle de regroupement et les mêmes classes.</p>")
 body.append(ul(method["next_gate"]["questions"])+p(method["next_gate"]["limit"]))
 body.append("<p>Ce passage doit montrer si la méthode se transfère à des mécanismes différents. Il ne démontrera une précision de prévision que si des efforts réellement observés et comparables deviennent disponibles.</p></section>")
 body.append("<section id='controles'><h2>Contrôles et traçabilité</h2>")
 body.append(f"<p>{len(r['checks'])} contrôles de cohérence documentaire et arithmétique passent. Les {r['source_files_unchanged']} empreintes des sources actives, paramètres et cartographie sont inchangées. Résultats et rapport sont reproductibles sans rejouer les tests techniques.</p>")
 body.append("<p>La revue indépendante a été réalisée par un autre agent. Elle ne constitue pas une validation humaine. Aucun commit, push ou changement du modèle économique actif.</p>")
 body.append("<p><a href='iteration-04-resultats.json'>Résultats consolidés</a> · <a href='iteration-04-incertitude.json'>Qualification complète des 27 cellules</a> · <a href='iteration-04-methode-candidate.json'>Méthode candidate</a> · <a href='iteration-04-contrat.json'>Contrat des témoins</a> · <a href='iteration-04-experiments.py'>Calcul et contrôle de reproduction</a> · <a href='iteration-03.html'>Itération 03</a></p></section>")
 nav=[("conclusion","Résultat"),("classes","Classes et plages"),("jh","JH par rôle"),("incertitudes","Causes et preuves"),("preuves","Essais exécutés"),("limites","Limites"),("responsabilites","Responsabilités"),("methode","Méthode candidate"),("suite","Suite et arrêt"),("controles","Contrôles")]
 css="""*{box-sizing:border-box}body{margin:0;background:#FAF8F4;color:#182632;font:16px/1.65 Aptos,'Segoe UI',Arial,sans-serif}a{color:#236159;overflow-wrap:anywhere;text-underline-offset:3px}a:focus-visible{outline:3px solid #C24F00;outline-offset:4px}nav{position:fixed;inset:0 auto 0 0;width:205px;padding:30px 20px;background:white;border-right:1px solid #EADFCD}nav strong{font-size:24px;color:#236159}nav a{display:block;margin:13px 0}main{margin-left:205px;max-width:1400px;padding:38px 45px 80px}header{background:#D9F2EA;padding:28px 35px;border-radius:14px;margin-bottom:25px}h1{font-size:35px;line-height:1.2}h2{font-size:27px;line-height:1.3}h3{font-size:21px}.eyebrow{font-size:13px;font-weight:700;letter-spacing:.06em}p{max-width:100ch}section{padding:18px 0 30px;border-bottom:1px solid #EADFCD;scroll-margin-top:20px}.key{background:#FFF0DB;border-left:5px solid #FF7A1A;padding:18px 24px;margin:20px 0}.key>strong{font-size:26px}.key p{margin:6px 0}.note{padding:18px;background:#F4F5FB}article{background:white;border-left:3px solid #D9F2EA;padding:20px 24px;margin:20px 0}li{margin:8px 0}.scroll{overflow-x:auto;margin:20px 0}table{border-collapse:collapse;width:100%;background:white;font-size:14px}th{background:#F4F8F6;text-align:left;font-size:13px}td,th{vertical-align:top;padding:12px 14px;border-bottom:1px solid #EADFCD;min-width:95px}td:first-child{min-width:175px}tr:last-child td{border-bottom:2px solid #D9F2EA}@media(max-width:900px){nav{position:static;width:auto;padding:15px 20px}nav a{display:inline-block;margin:6px 14px 6px 0}main{margin:0;padding:20px}header{padding:24px}h1{font-size:28px}}@media print{nav{display:none}main{margin:0;padding:0}body{font-size:11pt}.scroll{overflow:visible}tr,article{break-inside:avoid}a{color:#182632}}"""
 return "<!doctype html><html lang='fr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>FLOW · Itération 04 · Incertitude</title><style>"+css+"</style></head><body><nav aria-label='Sommaire'><strong>FLOW</strong>"+"".join("<a href='#"+k+"'>"+e(v)+"</a>" for k,v in nav)+"</nav><main>"+"".join(body)+"</main></body></html>\n"
