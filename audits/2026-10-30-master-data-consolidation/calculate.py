from pathlib import Path
import json,sys,math,hashlib
from decimal import Decimal,ROUND_HALF_UP
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.stdout.reconfigure(encoding="utf-8")
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def rounded(v,unit):return int((Decimal(str(v))/unit).quantize(Decimal("1"),rounding=ROUND_HALF_UP))*unit
i=read(OUT/"inputs.json")
p=(OUT/i["reference"]).resolve();previous=read(p)
selected=next(x for x in previous["rows"] if x["id"]==i["selected_reference"])
total=rounded(selected["total_jh"],i["rounding_jh"])
checks=[]
def ck(ok,label):
 assert ok,label
 checks.append(label)
if not (OUT/"baseline.json").exists():
 files=[p for d in ("source","config","app/src","tools") for p in (ROOT/d).rglob("*") if p.is_file() and p.suffix in (".yaml",".py",".tsx",".ts",".css",".md")]
 save("baseline.json",{"files":{p.relative_to(ROOT).as_posix():sha(p) for p in files}})
d=previous["activity_source"]
phase_weights=d["phase_effort_percent_of_base"]
activities=[];roles={k:0. for k in i["role_labels"]}
cells=[]
for a in d["activities"]:
 weights=i["activity_role_weights"][a["id"]]
 ck(math.isclose(sum(weights.values()),1),"activity allocation "+a["id"])
 ck(set(weights)<=set(a["possible_flow_roles"]),"roles compatible "+a["id"])
 fraction=sum(x*y for x,y in zip(phase_weights,a["percent_by_phase"]))/100/sum(phase_weights)
 effort=total*fraction
 activities.append({"id":a["id"],"label":a["label"],"published_phase_weights":a["percent_by_phase"],"fraction":fraction,"jh":effort,"proposed_role_weights":weights,"mapping_rationale":i["mapping_rationales"][a["id"]]})
 for role,weight in weights.items():
  effort_role=effort*weight;roles[role]+=effort_role
  cells.append({"activity":a["id"],"role":role,"proposed_share":weight,"jh":effort_role})
ck(math.isclose(sum(roles.values()),total),"unrounded roles preserve total")
ck(math.isclose(sum(a["jh"] for a in activities),total),"activities preserve total")
# Largest remainders: no role is assigned an arbitrary residual to force the total.
unit=i["role_rounding_jh"]
allocation={k:math.floor(v/unit)*unit for k,v in roles.items()}
remaining=round((total-sum(allocation.values()))/unit)
order=sorted(roles,key=lambda k:(-(roles[k]/unit-math.floor(roles[k]/unit)),k))
for role in order[:remaining]:allocation[role]+=unit
ck(sum(allocation.values())==total,"rounded roles preserve total")
c=previous["formula"]["cocomo"];F=previous["formula"]["F"]
pm=(total/c["effort_phase_factor"])*c["day_hours"]/c["month_hours"]
months=c["C"]*pm**F*c["schedule_phase_factor"]
planning_months=rounded(months,1)
sys.path.insert(0,str(ROOT/"tmp/model-deps"))
import yaml
capacity=yaml.safe_load((ROOT/"source/deploiement-groupe.yaml").read_text(encoding="utf-8"))["calendrier_autonome"]["capacite"]["jours_productifs_etp_mois"]
ck(capacity==i["capacity_convention"]["productive_jh_per_fte_month"],"capacity source convention")
role_rows=[{"id":k,"label":label,"jh_unrounded":roles[k],"jh":allocation[k],"average_fte":allocation[k]/planning_months/capacity} for k,label in i["role_labels"].items()]
phases=[]
for label,effort_pct,schedule_pct in zip(d["phase_order"],phase_weights,d["phase_schedule_percent_of_base"]):
 effort=total*effort_pct/sum(phase_weights)
 duration=planning_months*schedule_pct/sum(d["phase_schedule_percent_of_base"])
 phases.append({"phase":label,"jh":effort,"months":duration,"average_fte":effort/duration/capacity,"status":"Projection de la répartition publiée, pas plan de staffing validé."})
ck(math.isclose(sum(x["jh"] for x in phases),total),"phase effort")
ck(math.isclose(sum(x["months"] for x in phases),planning_months),"phase schedule")
def effort(ks,em=1):
 return c["A"]*ks**previous["formula"]["E"]*em*c["month_hours"]/c["day_hours"]*c["effort_phase_factor"]
# Isolated leverage, not a range and not a reserve.
k=selected["equivalent_KSLOC"];delta=previous["size"]["proposed_complements_units"]/1000
leverage=effort(k+.1*delta)-effort(k)
drivers=[
{"id":"scope","hypothesis":"Six capacités BC-002 à BC-007. Admission de contributions, consultation et administration ; pas de création d’un PIM/MDM complet avec édition collaborative et workflows riches.",
 "trigger":"Ajout d’édition métier, validation multi-acteurs, fusion/dédoublonnage, recherche floue ou arbitrage automatique de données.",
 "effect":"Hausse potentiellement importante. À l’inverse, isoler des fonctions natives non nécessaires à FLOW peut réduire le périmètre commun. Effet non chiffré sans liste d’écarts.",
 "quantified_effect_jh":None},
{"id":"complements","hypothesis":"Les compléments restent dimensionnés par analogie : 172 traitements, 313 champs et 42 modèles supplémentaires, dont seules huit analogies de règle ont été affinées.",
 "trigger":"Modification substantielle des versions, des règles d’autorité, des dépendances ou du protocole de reprise.",
 "effect":"Une hausse isolée de 10 % de la taille complémentaire ajoute environ "+str(round(leverage))+" JH dans le modèle. Ce n’est ni une probabilité ni une marge à ajouter.",
 "quantified_effect_jh":leverage},
{"id":"reuse","hypothesis":"Services comparables disponibles dans Spring, persistance, identité, import et composants UI ; base de données, sauvegardes et chaîne de livraison disponibles.",
 "trigger":"Réécriture d’un mécanisme générique, intégration technique nettement plus difficile ou composants indisponibles.",
 "effect":"Hausse des JH et du délai. La réutilisation ne peut pas être remplacée par une remise forfaitaire ; un mécanisme partagé garde un seul propriétaire de financement.",
 "quantified_effect_jh":None},
{"id":"service","hypothesis":"Objectifs de comparaison S1 conservés : disponibilité 99,9 %, rétablissement après sinistre sous 8 h, perte de données cible au plus 4 h ; qualification d’un lot de 100 000 lignes en 30 min. Ils ne sont pas démontrés.",
 "trigger":"Exigences plus fortes, plusieurs régions actives, reprise automatique sans intervention, volumes très supérieurs ou certification spécifique.",
 "effect":"Hausse possible de l’architecture, de la qualification et de la plateforme. Les achats et l’exploitation récurrente restent hors des 1 500 JH.",
 "quantified_effect_jh":None},
{"id":"organization","hypothesis":"Équipe maîtrisant Spring et les composants réutilisés, décideurs disponibles, environnements accessibles et capacité moyenne voisine de cinq personnes à temps plein.",
 "trigger":"Équipe junior ou instable, attente de décisions, services partagés non disponibles, dépendances externes bloquantes.",
 "effect":"Le délai de 17 mois devient fragile. À effort inchangé, quatre équivalents temps plein à 18 JH/mois requièrent déjà "+str(round(total/4/capacity,1))+" mois de capacité ; les dépendances peuvent ajouter du délai. Ce quotient n’est pas une nouvelle prédiction COCOMO.",
 "quantified_effect_jh":None}
]
result={"id":i["id"],"date":i["date"],"status":i["status"],"total_gross_jh":total,"method_policy":i["method_policy"],
"decision":{"reference":i["selected_reference"],"unrounded_jh":selected["total_jh"],"rounding_jh":i["rounding_jh"],"rounding_delta_jh":total-selected["total_jh"],"rationale":i["selection_rationale"],"statistical_confidence_level":None,"added_risk_reserve_jh":0},
"references":[{"id":r["id"],"label":r["label"],"jh":r["total_jh"],"schedule_months":r["schedule_months"]} for r in previous["rows"]],
"functional_comparison":{**previous["functional"],"gap_jh":total-previous["functional"]["jh"],"gap_pct":100*(total/previous["functional"]["jh"]-1),"interpretation":"Comparaison conservée, pas réconciliation démontrée. Choix de consolidation à 1 500 JH, sans moyenne des méthodes."},
"scope":{"capabilities":["BC-002","BC-003","BC-004","BC-005","BC-006","BC-007"],"includes":["analyse produit","conception et architecture","réalisation et tests développeur","QA et qualification","sécurité ciblée","pilotage local du produit","préparation de la livraison et mise en service initiale"],"excludes":["autres familles du Core System","raccordements et migrations Beaumanoir","décision et acceptation métier côté client","pilotage du programme et conduite du changement Groupe","MCO et évolutions annuelles","exploitation et achats cloud/licences","certification et audits externes spécifiques non définis"],"no_extra_ai_discount":True,"no_extra_qa_or_coordination":True},
"activities":activities,"activity_to_role":cells,"roles":role_rows,
"role_distribution_status":"Proposition d’organisation assistée par IA. Répartitions d’activité publiées ; clés activité/rôle hypothétiques et visibles. Arrondi à 10 JH par plus grands restes, sans perte du total.",
"schedule":{"COCOMO_on_consolidated_effort_months":months,"PM_elaboration_construction":pm,"formula":"3.67 × (JH / 1.18 × 7 / 152)^0.31794 × 1.25","planning_months_proposed":planning_months,"productive_jh_per_fte_month":capacity,"average_fte":total/planning_months/capacity,"average_jh_per_month":total/planning_months,"phase_reading":phases,"role_availability_confirmed":False,"interpretation":"Délai arrondi issu du modèle. Le quotient de capacité vérifie une cohérence, pas une validation indépendante. Les rôles ne représentent pas neuf personnes à temps plein."},
"significant_assumptions":drivers,
"progress":{**previous["progress"],"proposed_consolidated_capabilities":6,"formally_adopted_capabilities":0,"meaning":"Six capacités regroupées pour une décision d’opportunité. Ventilation non imposée par BC ; pas de nouveau pourcentage de certitude."},
"iteration_decision":"Arrêter l’affinage à périmètre et hypothèses constants. Réouvrir uniquement lorsqu’un des déclencheurs significatifs change, ou lors d’un jalon du projet.",
"active_economy_changed":False,
"source_hashes":{p.relative_to(ROOT).as_posix():sha(p) for p in (p,OUT/"inputs.json",ROOT/"audits/2026-10-30-master-data-calcul/repartitions-sources.json",ROOT/"source/deploiement-groupe.yaml")},
"activity_reference":d}
save("results.json",result)
for path,h in read(OUT/"baseline.json")["files"].items():ck(sha(ROOT/path)==h,"active unchanged "+path)
save("verification.json",{"passed":True,"checks":len(checks),"active_files_unchanged":len(read(OUT/"baseline.json")["files"]),"total":total,"roles_total":sum(r["jh"] for r in role_rows),"limits":"Vérifie conservation et calcul. Ne démontre pas les hypothèses ni la disponibilité des rôles."})
print(json.dumps({"total":total,"roles":role_rows,"months":months,"planning_months":planning_months,"average_fte":total/planning_months/capacity,"complement_leverage_jh":leverage,"checks":len(checks)},ensure_ascii=False,indent=2))
