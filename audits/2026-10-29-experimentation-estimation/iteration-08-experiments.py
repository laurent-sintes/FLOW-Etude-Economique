"""Consolidate iteration08 and reproduce its numerical outputs; audit only."""
from __future__ import annotations
import hashlib, importlib.util, json, math
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
def read(n):return json.loads((HERE/n).read_text(encoding="utf-8"))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(HERE/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
 checks=[]
 def check(name,ok):
  checks.append({"check":name,"passed":bool(ok)})
  if not ok:raise ValueError(name)
 context=read("iteration-08-contexte.json")
 for key in ["source_hashes","additional_source_hashes"]:
  for p,h in context[key].items():check("Source unchanged: "+p,digest(ROOT/p)==h)
 for p,h in context["frozen_audit_inputs"].items():check("Prior audit frozen: "+p,digest(HERE/p)==h)
 check("Protocol frozen",digest(HERE/"iteration-08-protocole.json")=="6d03e12ee817899884b98d50220756a3eb455074092eea6fcead80749ef51873")
 check("Method frozen before size",digest(HERE/"iteration-08-methode.json")=="b0003888913743f6a37db5a5e635c94dca2d322910be0917b8c1e6ce11170444")
 gel=read("iteration-08-taille-gel.json")
 for p,h in gel["sha256"].items():check("Size frozen: "+p,digest(HERE/p)==h)
 size=read("iteration-08-taille.json");cosmic=read("iteration-08-cosmic.json")
 calc=read("iteration-08-calculs.json");method=read("iteration-08-methode.json")
 old=read("iteration-07-resultats.json");decision=read("iteration-08-decision.json")
 empirical=read("iteration-08-references-effort.json")
 for p,h in calc["input_sha256"].items():check("Calculated input frozen: "+p,digest(HERE/p)==h)
 spec=importlib.util.spec_from_file_location("cocomo08",HERE/"iteration-08-cocomo.py")
 cocomo=importlib.util.module_from_spec(spec);spec.loader.exec_module(cocomo)
 recomputed=[]
 for scenario in method["scenarios"]:
  for variant,ksloc in zip(["bas","central","haut"],size["sizes"]["new_delivered_product_KSLOC"]):
   row=cocomo.evaluate(ksloc,scenario);row["size_variant"]=variant;recomputed.append(row)
 check("Nine COCOMO cases reproduced",recomputed==calc["cases"])
 check("24 one-factor cases reproduced",cocomo.sensitivity(size["sizes"]["new_delivered_product_KSLOC"][1])==calc["one_factor_sensitivity"])
 converter=[]
 for variant,sloc in zip(["bas","central","haut"],size["sensitivities_only"][0]["effect_on_base_product_logical_sloc"]):
  row=cocomo.evaluate(sloc/1000,method["scenarios"][0]);row["size_variant"]=variant;converter.append(row)
 check("Three converter sensitivities reproduced",converter==calc["version_converter_sensitivity"])
 check("Published example and unit checks",cocomo.verify()==calc["formula_checks"])
 for a,b,c,k in zip(size["sizes"]["Java_new_product"],size["sizes"]["TypeScript_new_product"],size["sizes"]["new_delivered_product_logical_SLOC"],size["sizes"]["new_delivered_product_KSLOC"]):
  check("Language sum "+str(c),a+b==c and math.isclose(c/1000,k))
 movements=Counter();ids=[]
 for process in cosmic["processes"]:
  pm=Counter()
  for m in process["movements"]:
   ids.append(m["id"]);pm[m["type"]]+=m["cfp"]
  for kind in ["E","R","W","X"]:check(process["id"]+" "+kind,pm[kind]==process["count"][kind])
  check(process["id"]+" total",sum(pm.values())==process["count"]["cfp"])
  movements.update(pm)
 check("COSMIC movement ids unique",len(ids)==len(set(ids)))
 for k in ["E","R","W","X"]:check("COSMIC "+k,movements[k]==cosmic["result"]["movements"][k])
 check("COSMIC 350 conditional",sum(movements.values())==350==cosmic["result"]["conditional_expanded_subset_cfp"])
 check("COSMIC 25 processes",len(cosmic["processes"])==25==cosmic["result"]["functional_processes"])
 coverage=old["coverage"];studied=[r for r in coverage if r["comparatively_studied"]]
 check("88 distinct native capabilities",len(coverage)==len({x["id"] for x in coverage})==88)
 check("20 cumulative studied identities",sorted(r["id"] for r in studied)==old["cumulative_comparative_ids"] and len(studied)==20)
 check("6 historical scenario capabilities",sum(x["scenario_estimated"] for x in coverage)==6)
 check("No opportunity admission",sum(x["opportunity_admitted"] for x in coverage)==0)
 check("No full or retained result",all(calc[k] is None for k in ["full_contract_effort_jh","full_contract_months","full_core_jh","full_core_months","retained_estimate","new_effort_by_role"]))
 check("No complete COSMIC measure or conversion",all(cosmic["result"][k] is None for k in ["full_family_cfp","full_core_cfp","validated_cfp","effort_jh","cfp_to_loc","cfp_to_jh"]))
 check("No new compatible empirical rate",empirical["outcome"]["new_applicable_effort_rates"]==0)
 check("Stop automatic iterations",decision["recommendation"]=="modifier_approche" and decision["next_iteration_worthwhile"] is False)
 metrics=[]
 meanings={
 "comparative":"20 identifiants uniques cumules. Aucune capacite nouvelle en08.",
 "scenario_complete":"Six capacites dont les fonctions sont representees par le scenario07. Aucun passage en budget valide en08.",
 "partial_only":"Les 14 autres capacites etudiees restent partielles.",
 "not_comparative":"68 capacites cadrees sans estimation comparative.",
 "opportunity_admitted":"Aucune nouvelle admission : transposition, travaux manquants et conditions de realisation restent a justifier.",
 "families_scenario":"Une famille avec hypotheses de JH par role heritees de07; aucune ventilation08 calibree."
 }
 for m in old["metrics"]:
  n=dict(m);n["previous"]=m["current"];n["delta"]=0;n["meaning"]=meanings.get(m["id"],m["meaning"]);metrics.append(n)
 central=[x for x in recomputed if x["size_variant"]=="central"]
 nominal=[x for x in recomputed if x["scenario_id"]=="nominal"]
 ratios={
 "context_at_central_size":max(x["effort_jh"] for x in central)/min(x["effort_jh"] for x in central),
 "size_at_nominal_context":max(x["effort_jh"] for x in nominal)/min(x["effort_jh"] for x in nominal),
 "all_sensitivity_cases":max(x["effort_jh"] for x in recomputed)/min(x["effort_jh"] for x in recomputed),
 "meaning":"Rapports de sensibilite entre hypotheses, pas facteurs d incertitude calibres ni probabilites."
 }
 inputs=["iteration-08-protocole.json","iteration-08-contexte.json","iteration-08-methode.json","iteration-08-taille.json","iteration-08-taille-gel.json","iteration-08-cosmic.json","iteration-08-calculs.json","iteration-08-references-effort.json","iteration-08-revue.json","iteration-08-decision.json","iteration-07-resultats.json","iteration-08-experiments.py"]
 result={
 "id":"iteration-08-resultats","date":"2026-10-29","status":"dernier_essai_automatique_avant_decision",
 "recommendation":decision["recommendation"],"metrics":metrics,
 "coverage":coverage,"subdomains":old["subdomains"],
 "cumulative_comparative_ids":old["cumulative_comparative_ids"],"new_comparative_ids":[],
 "scope":{"family":"Operational References","native_capabilities":6,"native_functions":14,"contract_ref":"iteration-07-contrat-v1.1.json","contract_sha256":size["contract_sha256"],"service_scenario":"S1, hypothese non approuvee","current_size_covers_complete_contract":False},
 "size":size["sizes"],"not_sized":size["separate_not_sized"],
 "cocomo":{"cases":recomputed,"sensitivity_ratios":ratios,"new_effort_by_role":None,"lifecycle":"Phase logicielle COCOMO LCO vers IOC (elaboration et construction). Pas le calendrier complet du contrat ni du programme.","staffing":"Moyenne modele implicite, pas une composition d equipe promise ni une allocation par role."},
 "cosmic":cosmic["result"],"empirical":empirical["outcome"],
 "uncertainty":decision["uncertainty"],
 "full_core_jh":None,"full_core_months":None,"full_contract_jh":None,"full_contract_months":None,"cumulative_jh":None,"selected_estimate_jh":None,
 "precision_improvement_demonstrated":False,"source_files_checked":len(context["source_hashes"]),"additional_instruction_files_checked":len(context["additional_source_hashes"]),
 "checks":checks,"input_sha256":{p:digest(HERE/p) for p in inputs}
 }
 write("iteration-08-resultats.json",result)
 print(json.dumps({"checks":len(checks),"passed":all(x["passed"] for x in checks),"capabilities_cumulative":len(studied),"new":0,"full_core_jh":None,"recommendation":result["recommendation"]}))
if __name__=="__main__":main()
