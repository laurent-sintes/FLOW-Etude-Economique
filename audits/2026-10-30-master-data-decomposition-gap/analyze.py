from pathlib import Path
import json,sys,math,hashlib,collections,html,importlib.util,re
sys.stdout.reconfigure(encoding="utf-8")
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
P=ROOT/"audits/2026-10-30-master-data-spring-flow"
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
r=read(P/"results.json");i=read(P/"inputs.json");a=read(P/"analogues.json");cos=read(P/"cosmic-candidate.json")
native=read(ROOT/"audits/2026-10-30-master-data-comparable-reuse/inputs.json")
if not (OUT/"baseline.json").exists():
 paths=[p for d in ["source","config","app/src","app/scripts"] for p in (ROOT/d).rglob("*") if p.is_file()]
 save("baseline.json",{"files":{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)}})
names={"erpnext":"ERPNext + Frappe","odoo":"Odoo","tryton":"Tryton","axelor":"Axelor"}
family_names={"ADMISSION":"Contributions, autorité et publication","SEMANTIQUE":"Accords, assortiments, conditionnements et services","PROTECTION":"Accès, usages protégés, audit et purge","REPRISE":"Rejeu et rapprochement après restauration","VERSIONS":"Compatibilité des versions canoniques","SERVICE":"Automatisation de mise en service"}
descriptions={
"ADMISSION":"Identifier les sources et leurs droits sur les champs, rapprocher les identités, traiter les conflits, figer des versions et publier un ensemble cohérent.",
"SEMANTIQUE":"Représenter les accords et engagements reçus, les assortiments figés, les contextes, les structures de conditionnement, les prestations et conditions typées.",
"PROTECTION":"Restituer les données à date et selon la portée, enregistrer les usages des consommateurs, protéger les versions, exporter, consulter le journal et contrôler la purge.",
"REPRISE":"Reconstruire les identités après rejeu, invalider les anciens curseurs et rapprocher les usages déclarés avant de réautoriser la purge.",
"VERSIONS":"Accepter deux versions canoniques, transformer les différences bornées et refuser les conversions ambiguës.",
"SERVICE":"Assembler les commandes de livraison, migration, sauvegarde/restauration et supervision sur des composants gérés disponibles."}
proof_notes={
"ADMISSION":"CSVImporter montre un import transactionnel et la gestion d'erreurs ; DataSharingReferentialLineServiceImpl montre des requêtes filtrées. Ils ne fournissent pas une mesure d'une publication Flow atomique multi-source.",
"SEMANTIQUE":"ProductPackagingServiceImpl et UnitConversionServiceImpl montrent des calculs et validations concrets. Pas de mesure dédiée des accords/assortiments/conditions Flow ; le nombre de traitements et de champs est proposé.",
"PROTECTION":"Les contrôleurs de jetons et le service de filtrage sont observés. Le protocole d'usages protégés et de purge Flow n'est pas mesuré dans une réalisation comparable complète.",
"REPRISE":"Le code de reprise de ligne CSV est un analogue partiel. La restauration cohérente des versions et des déclarations consommateurs est un mécanisme proposé ; sa taille n'est pas démontrée par cet extrait.",
"VERSIONS":"Aucun convertisseur canonique équivalent mesuré. Quatre transformateurs, deux traitements communs et 26 règles déclarées sont des hypothèses explicites.",
"SERVICE":"Aucun corpus comparable de scripts de déploiement/backup restauré n'est mesuré. Les 14 ressources, trois configurations d'environnement et huit règles de supervision sont proposées."}
cfp=r["functional_crosscheck"]["size_CFP"];h=20;factor=1;functional_jh=cfp*h*factor/7
assert cfp==420
def cocomo(k):return 2.94*k**1.0997*152/7*1.18
families=r["size_delta"]["central"]["families"];delta_units=r["size_delta"]["central"]["delta_equivalent_units"]
rows=[]
for old in r["reference_sensitivities"]:
 s=old["scenarios"]["central"];acc=0;prev=0;allocation=[]
 for fam,v in families.items():
  exact=s["incremental_flow_jh"]*v["equivalent"]/delta_units
  acc+=exact;display=round(acc)-prev;prev=round(acc)
  allocation.append({"id":fam,"jh":exact,"display_jh":display})
 service_delta=s["total_jh"]-cocomo(s["equivalent_KSLOC"]-families["SERVICE"]["equivalent"]/1000)
 rows.append({"id":old["id"],"label":names[old["id"]],"common_jh":s["common_reference_jh"],"complements_jh":s["incremental_flow_jh"],"total_jh":s["total_jh"],"complement_allocation":allocation,
 "cosmic_isbsg_jh":functional_jh,"remaining_difference_jh":s["total_jh"]-functional_jh,
 "old_difference_jh":s["total_jh"]-cfp*20*.8/7,
 "implied_hours_per_CFP":s["total_jh"]*7/cfp,
 "explicit_service_code_marginal_jh":service_delta,
 "residual_after_removing_explicit_service_jh":s["total_jh"]-service_delta-functional_jh,
 "complements_share":s["incremental_flow_jh"]/s["total_jh"]})
# Inspect exact contents of the measured analogue units, to check the granularity of extrapolation.
spec=importlib.util.spec_from_file_location("m",ROOT/"audits/2026-10-30-master-data-natif/measure.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
evidence=[]
for sample in a["samples"]:
 p=ROOT/sample["path"];assert sha(p)==sample["sha256"]
 ext=p.suffix;tree=m.PARSERS[ext].parse(p.read_bytes());cnt=collections.Counter()
 for node in m.walk(tree.root_node):
  if not any(lo<=node.start_point.row+1<=hi for lo,hi in sample["ranges"]):continue
  if (node.type.endswith("_statement") and node.type not in {"empty_statement","export_statement"}) or node.type in (m.JAVA_EXTRA if ext==".java" else m.JS_EXTRA):cnt[node.type]+=1
 repository="axelor/axelor-open-platform" if "oss-audit-axelor-platform" in sample["path"] else "axelor/axelor-open-suite"
 prefix="tmp/oss-audit-axelor-platform/" if "oss-audit-axelor-platform" in sample["path"] else "tmp/oss-audit-axelor/"
 repo_path=sample["path"].removeprefix(prefix)
 evidence.append({**sample,"node_types":dict(cnt),"repository":repository,"url":f"https://github.com/{repository}/blob/{sample['commit']}/{repo_path}#L{sample['ranges'][0][0]}"})
family_evidence=[]
for fam,v in families.items():
 blocks=[b for b in i["blocks"] if b["family"]==fam];schemas=[s for s in i["schemas"] if s["family"]==fam]
 family_evidence.append({"id":fam,"label":family_names[fam],"description":descriptions[fam],"central_equivalent_units":v["equivalent"],
 "blocks":len(blocks),"block_kinds":dict(collections.Counter(x["kind"] for x in blocks)),"fields":sum(len(s["fields"]) for s in schemas),"new_models":sum(s["new_model"] for s in schemas),
 "proof":proof_notes[fam],"block_list":[b["id"] for b in blocks],"schema_list":[{"name":s["name"],"fields":s["fields"],"new_model":s["new_model"]} for s in schemas],
 "unit_bank":{kind:a["unit_bank"][kind] for kind in sorted({b["kind"] for b in blocks})},
 "proof_status":"Taille des analogues mesurée ; décomposition et volume des compléments estimés, sans temps de réalisation observé.",
 "four_oss_independent_gap_audits":False})
decision={"date":"2026-10-30","scope":"Candidat Master Data, sans modification des sources économiques actives.",
 "user_direction":"La Master Data est un composant d'un projet beaucoup plus gros ; retirer le coefficient 0,8.",
 "old_factor":.8,"retained_factor":1,"retained_hours_per_CFP":20,"CFP":cfp,"retained_jh":functional_jh,
 "arithmetic_change_jh":functional_jh-cfp*20*.8/7,
 "justification":"Convention de comparaison demandée par l'utilisateur : ne pas attribuer au composant Master Data une économie de taille issue de projets indépendants. Conserver la base20h/CFP comme référence de travail.",
 "method_status":"Écart documenté à la procédure de correction par taille du rapport2012, et non correction d'une faute de calcul. Le facteur publié reste0,8 pour300–500CFP. Un projet plus gros n'implique pas dans ce tableau un coefficient plus élevé ; le calcul global doit avoir une frontière cohérente.",
 "larger_project_jh":None,"claim_of_better_calibration":False,
 "source":"https://cosmic-sizing.org/wp-content/uploads/2015/07/Performance-of-Business-Application-Real-Time-and-Component-Software-Projects-2012.pdf#page=12"}
findings=[
{"id":"D01","status":"quantified","title":"Le coefficient de taille expliquait240JH","detail":"420×20/7=1200 ;420×20×0,8/7=960. Le retrait demandé relève le comparateur à1200, sans modifier les quatre COCOMO.","amount_jh":240},
{"id":"D02","status":"observed_scope_mismatch_effect_not_quantified","title":"Création/édition natives et contributions Flow ne sont pas réconciliées",
 "detail":"Les contrats MD01–MD07 de l'audit24 comprennent créer/modifier/désactiver et des formulaires de maintenance. Le contrat07 F05/F06 décrit des références reçues ; F11 impose une correction par contribution autorisée. Le COSMIC compte I01/I02 et des consultations, sans processus générique de création/édition humaine de chaque fiche. Une partie du code natif reste nécessaire aux validations et à la persistance ; aucune soustraction automatique de tous les formulaires n'est justifiée. Le résidu fonctionnel n'a pas été isolé dans la taille native avant transposition.",
 "refs":["../2026-10-30-master-data-comparable-reuse/inputs.json#scope/contracts","../2026-10-29-experimentation-estimation/iteration-07-contrat-v1.1.json#functional_contract/F11","../2026-10-30-master-data-spring-flow/cosmic-candidate.json#processes"]},
{"id":"D03","status":"observed_proxy_weakness_effect_not_quantified","title":"L'unité d'analogie peut surdimensionner certains petits traitements",
 "detail":"Le bloc37 utilisé pour chacune des78 règles est constitué d'un extrait de conversion contenant5 déclarations de méthodes. Les deux autres analogues de règle sont une classe de conditionnement de5 méthodes (30unités) et une classe de requêtes de8 méthodes (48unités). Les traitements Flow sont des actions nommées de tailles inconnues. Cela ne démontre pas qu'une règle Flow vaut une méthode, mais invalide l'idée d'un équivalent élémentaire uniforme déjà prouvé. Des déclarations sont en outre présentes dans les analogues et un squelette de190unités est ajouté : risque de recouvrement à rapprocher, pas190unités automatiquement en trop.",
 "refs":["analogues-inspected.json","../2026-10-30-master-data-spring-flow/inputs.json#blocks"]},
{"id":"D04","status":"quantified_diagnostic_only","title":"La seule mise en service explicite n'explique pas l'écart",
 "detail":"Le groupe SERVICE représente355unités supplémentaires. Son retrait mathématique du total change chaque résultat d'environ38JH. D'autres exigences de qualité traversent les traitements ; leur effort n'est pas isolé. Il est incorrect d'attribuer tout l'écart aux seuls travaux techniques absents du comptage CFP.",
 "marginal_jh_by_reference":{x["id"]:x["explicit_service_code_marginal_jh"] for x in rows}},
{"id":"D05","status":"documented_method_difference","title":"COSMIC ne compte pas séparément chaque traitement interne",
 "detail":"Les contrôles d'autorité, calculs et transformations peuvent rester associés aux mêmes mouvements de données. Un enrichissement du traitement sans nouveau mouvement n'ajoute pas automatiquement des CFP. COCOMO dépend ici d'une taille de code proposée. Les20h/CFP doivent représenter la complexité moyenne des traitements ; leur adéquation à Flow n'est pas démontrée. Il serait incorrect d'inventer des CFP pour chaque règle afin d'aligner les totaux.",
 "source":"https://cosmic-sizing.org/wp-content/uploads/2022/11/Combination-of-Parts-v5.0-Sep-2024.pdf#page=35"},
{"id":"D06","status":"excluded_as_blanket_explanation","title":"Les960/1200JH ne sont pas seulement du développement",
 "detail":"ISBSG normalise planning, spécification, conception, réalisation, test et mise en œuvre. COCOMO a été étendu aux quatre phases par1,18. On ne peut ni ajouter18% au chiffre ISBSG pour le faire coïncider, ni enlever18% du COCOMO sans retirer des activités. Les spécialistes externes et l'administration de base exigent encore un alignement explicite ; aucune charge constatée n'est disponible.",
 "sources":["https://cosmic-sizing.org/wp-content/uploads/2015/07/Performance-of-Business-Application-Real-Time-and-Component-Software-Projects-2012.pdf#page=46","https://www.rose-hulman.edu/class/csse/csse372/201310/Homework/CII_modelman2000.pdf#page=70"]},
{"id":"D07","status":"observed_dependence","title":"Les quatre totaux ne sont pas quatre validations indépendantes",
 "detail":"Ils partagent8501,5unités additionnelles, construites avec14extraits issus d'Axelor Suite/Platform. Le périmètre commun vient des quatre OSS ; les compléments ne sont pas quatre audits distincts d'écarts produit. Ils représentent58–64% des totaux. Leur ajout réduit mécaniquement l'écart relatif entre les références.",
 "native_max_min_ratio":max(x["common_jh"] for x in rows)/min(x["common_jh"] for x in rows),
 "final_max_min_ratio":max(x["total_jh"] for x in rows)/min(x["total_jh"] for x in rows)}
]
out={"id":"audit26-master-data-decomposition-gap","date":"2026-10-30","purpose":"Décomposer les quatre résultats annoncés et expliquer l'écart avec COSMIC×ISBSG, sans recalibrer les quatre COCOMO.",
"rows":rows,"families":family_evidence,"functional_benchmark_decision":decision,"findings":findings,
"allocation_rule":"Chaque famille reçoit sa part de la taille additionnelle dans le supplément global (total COCOMO moins référence commune). Arrondi par différences de cumuls. Ce n'est pas une estimation autonome de chaque famille.",
"arithmetic_gap_status":"240JH expliqués et retirés du comparateur par décision. Reste189–353JH non attribuables exactement ; plusieurs différences concrètes de périmètre et de dimensionnement identifiées. Pas de recalage forcé.",
"input_hashes":{p.relative_to(ROOT).as_posix():sha(p) for p in [P/"results.json",P/"inputs.json",P/"analogues.json",P/"cosmic-candidate.json",ROOT/"audits/2026-10-30-master-data-comparable-reuse/inputs.json",ROOT/"audits/2026-10-29-experimentation-estimation/iteration-07-contrat-v1.1.json"]},
"active_economy_changed":False,"human_review":None,"observed_effort":None}
save("results.json",out);save("analogues-inspected.json",evidence);save("benchmark-decision.json",decision)
checks=[]
def ck(test,label):
 assert test,label
 checks.append(label)
for p,h in read(OUT/"baseline.json")["files"].items():ck(sha(ROOT/p)==h,"active "+p)
for p,h in out["input_hashes"].items():ck(sha(ROOT/p)==h,"input "+p)
for x in rows:
 ck(math.isclose(x["common_jh"]+x["complements_jh"],x["total_jh"]),x["id"]+" total")
 ck(sum(y["display_jh"] for y in x["complement_allocation"])==round(x["complements_jh"]),x["id"]+" allocation")
 ck(math.isclose(x["old_difference_jh"]-x["remaining_difference_jh"],240),x["id"]+" coefficient")
 ck(math.isclose(x["remaining_difference_jh"],x["explicit_service_code_marginal_jh"]+x["residual_after_removing_explicit_service_jh"]),x["id"]+" diagnostic")
ck(cfp*20/7==1200,"new benchmark")
ck(len(evidence)==14,"analogue sources")
save("verification.json",{"passed":True,"checks":len(checks),"active_files_unchanged":len(read(OUT/"baseline.json")["files"]),"COCOMO_results_unchanged":True,"new_COSMIC_ISBSG_reference_jh":1200,"limits":"Vérification des calculs et empreintes ; aucun test ne démontre les volumes d'ingénierie proposés."})
# Readable report with only the requested central decompositions.
def e(x):return html.escape(str(x))
def fmt(x,dec=0):return f"{x:,.{dec}f}".replace(","," ").replace(".",",")
def link(label,url):return '<a href="'+html.escape(url,quote=True)+'">'+e(label)+'</a>'
def table(headers,rows):return '<div class="table"><table><thead><tr>'+''.join("<th>"+e(x)+"</th>" for x in headers)+'</tr></thead><tbody>'+''.join("<tr>"+''.join("<td>"+str(x)+"</td>" for x in row)+"</tr>" for row in rows)+'</tbody></table></div>'
parts=['<header><p>FLOW · Audit26 · 30 octobre2026</p><h1>Quatre références : commun, compléments et écart entre méthodes</h1><p>Décomposition des chiffres annoncés. Le coefficient0,8 est retiré du comparateur retenu à ta demande ; les quatre calculs COCOMO restent inchangés.</p></header>']
parts.append('<nav>'+''.join(link(label,"#"+id) for id,label in [("quatre","Les quatre chiffres"),("complements","Les compléments"),("preuves","Les preuves"),("ecart","Pourquoi l’écart"),("decision","Suite utile")])+'</nav><main>')
parts.append('<section id="quatre"><h2>Les quatre résultats annoncés</h2>')
parts.append(table(["Référence","Master Data commune","Compléments Flow","Total","Écart avec1200JH"],[[e(x["label"]),fmt(x["common_jh"])+" JH",fmt(x["complements_jh"])+" JH",'<strong>'+fmt(x["total_jh"])+' JH</strong>',fmt(x["remaining_difference_jh"])+" JH"] for x in rows]))
parts.append('<p>Les charges incluent les activités du projet logiciel initial : analyse, conception, réalisation, tests, gestion et préparation de livraison. Elles ne désignent ni des coûts historiques observés, ni le coût de tout Flow.</p><p>Le périmètre commun comprend partenaires/contacts/adresses, articles/fournitures/services, attributs/variantes, unités/conversions, tarifs de référence, lieux hiérarchisés et administration/import génériques. Les mécanismes réutilisés ne sont pas reconstruits.</p><p><strong>La convergence des références communes est intéressante. Les totaux complets ne sont pas quatre confirmations indépendantes :</strong> ils reçoivent le même volume de compléments Flow, qui représente environ60% de chaque résultat. Les tailles de ces compléments reposent sur des extraits d’Axelor, pas sur quatre analyses séparées de leur réalisation.</p></section>')
parts.append('<section id="complements"><h2>Quels compléments, et combien de JH ?</h2>')
allocrows=[]
for fam in family_evidence:
 allocrows.append([e(fam["label"])]+[str(next(y for y in x["complement_allocation"] if y["id"]==fam["id"])["display_jh"]) for x in rows])
allocrows.append(["<strong>Total des compléments</strong>"]+["<strong>"+fmt(x["complements_jh"])+"</strong>" for x in rows])
parts.append(table(["Complément, JH"]+[names[x["id"]] for x in rows],allocrows))
parts.append('<p><strong>Ces lignes répartissent le supplément calculé :</strong> le modèle calcule d’abord le projet complet, puis retire le calcul du périmètre commun. Le supplément est réparti entre familles au prorata de leur taille proposée. Les lignes ne sont donc pas des estimations COCOMO indépendantes, ni des temps unitaires constatés.</p>')
parts.append(table(["Famille","Résultat attendu","Base de dimensionnement proposée"],[[e(f["label"]),e(f["description"]),f'{f["blocks"]} blocs ; {f["fields"]} champs additionnels ; {f["new_models"]} modèles additionnels ; {fmt(f["central_equivalent_units"],1)} unités équivalentes'] for f in family_evidence]))
parts.append('<p>« Complément » signifie : au-delà du périmètre commun sélectionné dans l’audit24. Cela ne signifie pas que les quatre produits, pris dans leur intégralité, ne savent pas rendre ce service. Cette absence n’a pas été prouvée produit par produit.</p></section>')
parts.append('<section id="preuves"><h2>Ce qui est mesuré et ce qui reste proposé</h2><p><strong>Mesuré :</strong> le périmètre commun est relié à2060fichiers sélectionnés et contrôlés dans les dépôts figés. Pour les compléments,14extraits Java/TypeScript servent de tailles analogues. <strong>Proposé :</strong> le nombre de traitements Flow, les313champs additionnels, les42modèles, les règles de conversion et les configurations. Aucun temps réel de réalisation ne valide leur conversion en JH.</p>')
parts.append(table(["Famille","Preuve disponible et limite"],[[e(f["label"]),e(f["proof"])] for f in family_evidence]))
parts.append('<h3>Exemple révélateur : le bloc de validation</h3><p>Le calcul attribue37unités de code à chacune des78règles proposées. Cette taille vient d’un extrait de conversion d’unités qui contient cinq déclarations de méthodes. Les autres références de cette catégorie sont une classe de conditionnement de cinq méthodes et une classe de requêtes de huit méthodes.</p><p>Une action nommée « vérifier les parties d’un accord » ne vaut pas automatiquement ce groupe de méthodes. Certaines actions peuvent être plus simples, d’autres plus complexes. <strong>L’analogie de taille est donc insuffisamment ajustée.</strong> Je ne divise pas arbitrairement37par5 : cela remplacerait une hypothèse fragile par une autre.</p>')
parts.append(table(["Extrait source mesuré","Unités comptées","Méthodes dans l’extrait"],[[link(s["id"],s["url"]),s["program_units"],s["node_types"].get("method_declaration","—")] for s in evidence]))
parts.append('<p>Les résultats COCOMO du périmètre commun sont fondés sur du code existant sélectionné. Les compléments restent une estimation d’ingénierie à partir de ce code. Les deux niveaux de preuve ne doivent pas être présentés comme équivalents.</p></section>')
parts.append('<section id="ecart"><h2>Pourquoi COSMIC × ISBSG donne moins</h2><h3>Le coefficient0,8 :240JH identifiés</h3><p class="formula">Avant :420 ×20 ×0,8 ÷7 =960JH<br>Calcul retenu désormais :420 ×20 ÷7 =<strong>1200JH</strong></p><p>Le facteur0,8 est bien publié pour la tranche300–500CFP. Il ajuste la référence20heures/CFP issue d’une taille100–200CFP. Il ne correspond ni à Spring, ni à une remise de réutilisation. Les auteurs expliquent que leur échantillon ne permet pas une analyse statistique complète croisant langage, plateforme et taille.</p><p>Le retrait demandé est documenté comme une convention pour ce composant du programme Flow. Il ne démontre pas que20heures/CFP soit la productivité réelle de Flow. Il ne faut pas non plus appliquer le coefficient de taille d’un projet global encore non dimensionné à chacun de ses composants.</p><p>'+link("Rapport COSMIC/ISBSG, tableaux7 et8",decision["source"])+'</p>')
parts.append('<h3>Le reste de l’écart : différences réelles, effet exact encore non mesuré</h3><ol><li><strong>Le périmètre n’est pas parfaitement identique.</strong> La référence OSS conserve la création et modification natives des fiches. Flow reçoit et corrige les données par contribution autorisée (F11). Il faut isoler dans le code natif les fonctions d’édition réellement nécessaires à ce fonctionnement.</li><li><strong>Les tailles de compléments peuvent être trop fortes pour certains traitements.</strong> La granularité des analogues de5à8méthodes ne démontre pas celle des petites actions Flow ; des déclarations existent dans les analogues et dans le squelette ajouté. Aucun retrait forfaitaire n’est effectué.</li><li><strong>Les deux voies valorisent différemment les traitements internes.</strong> COSMIC compte des mouvements de données ; la complexité des contrôles et transformations est représentée indirectement par la productivité. COCOMO reçoit ici un volume de code proposé. Les mêmes entrées/sorties peuvent nécessiter des traitements internes très différents.</li><li><strong>Les activités sont globalement rapprochées, pas strictement identiques.</strong> ISBSG inclut déjà analyse, conception, tests et mise en œuvre. Ajouter une seconde QA ou18%de phases au1200serait injustifié. Les spécialistes hors équipe restent à rapprocher précisément.</li></ol>')
parts.append('<h3>La seule mise en service ne justifie pas plusieurs centaines de JH</h3><p>Test diagnostique : retirer uniquement les355unités du groupe de mise en service, en gardant la formule identique. Ce test ne modifie aucun résultat retenu et ne mesure pas l’ensemble des exigences de qualité.</p>')
parts.append(table(["Référence","Écart total avec1200","Effet des seuls355unités de mise en service","Écart restant après ce retrait diagnostique"],[[e(x["label"]),fmt(x["remaining_difference_jh"])+" JH",fmt(x["explicit_service_code_marginal_jh"])+" JH",fmt(x["residual_after_removing_explicit_service_jh"])+" JH"] for x in rows]))
parts.append('<p><strong>Conclusion de l’audit :</strong>240JH de l’écart précédent avaient une cause arithmétique identifiée. Le reste ne peut pas être attribué honnêtement à une cause unique. Le rapprochement des fonctions et le dimensionnement des compléments sont les priorités ; un changement de coefficients pour forcer l’égalité ne serait pas une validation.</p><p>'+link("COSMIC : traitement des manipulations de données",findings[4]["source"])+" · "+link("ISBSG : activités et effort normalisé",findings[5]["sources"][0])+'</p></section>')
parts.append('<section id="decision"><h2>Ce qui a progressé et la suite utile</h2><ul><li>Les quatre totaux sont décomposés sans consolidation arbitraire.</li><li>Les six familles de compléments ont une traçabilité de leurs quantités et analogues ; leurs preuves insuffisantes sont explicites.</li><li>Le comparateur est désormais1200JH, selon la décision de retrait du coefficient.</li><li>Les écarts concrets d’édition/contribution et de granularité des blocs sont identifiés ; ils remplacent l’explication trop générale par les garanties non fonctionnelles.</li><li>Le cumul reste6capacités Master Data étudiées. Aucun nouveau périmètre n’a été ajouté.</li></ul><p><strong>Une nouvelle itération est utile :</strong> rapprocher les fonctions de création/édition avec le contrat de contribution Flow, puis remesurer les analogues à la granularité des traitements proposés. Pas de transposition ligne à ligne vers Spring et pas de nouvel ajustement statistique pour faire coïncider les chiffres.</p>')
parts.append('<p>'+ " · ".join(link(label,p) for label,p in [("Résultats et constats","results.json"),("Décision sur le coefficient","benchmark-decision.json"),("Extraits vérifiés","analogues-inspected.json"),("Vérification","verification.json"),("Calcul reproductible","analyze.py"),("Périmètre commun antérieur","../2026-10-30-master-data-comparable-reuse/inputs.json"),("Compléments proposés","../2026-10-30-master-data-spring-flow/inputs.json")])+'</p><p>Sources économiques actives inchangées. Pas de commit ni de push. Les contrôles arithmétiques ne valent pas validation des hypothèses d’ingénierie.</p></section></main>')
oldhtml=(P/"index.html").read_text(encoding="utf-8");css=oldhtml.split("<style>",1)[1].split("</style>",1)[0]
body=''.join(parts)
segments=re.split(r'(<[^>]*>)',body)
for ix in range(0,len(segments),2):
 segments[ix]=re.sub(r'(?<=[a-z\u00e0-\u00ff])(?=\d)', ' ',segments[ix])
 segments[ix]=re.sub(r'(?<=\d)(?=[a-z\u00e0-\u00ff]|JH|CFP|%)', ' ',segments[ix])
body=''.join(segments)
page='<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FLOW — Quatre références Master Data et écart entre méthodes</title><style>'+css+'</style><body>'+body+'</body></html>'
(OUT/"index.html").write_text(page,encoding="utf-8")
print(json.dumps({"rows":[{k:x[k] for k in ["label","common_jh","complements_jh","total_jh","remaining_difference_jh"]} for x in rows],"COSMIC_ISBSG_jh":1200,"checks":len(checks),"findings":len(findings)},ensure_ascii=False))
