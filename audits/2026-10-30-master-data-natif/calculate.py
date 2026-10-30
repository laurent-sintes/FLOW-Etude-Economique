from pathlib import Path
import json,hashlib,math
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def estimate(program,declarative,weight,em,c):
    size=(program+weight*declarative)/1000
    E=c["B"]+.01*c["SF_sum"];F=c["D"]+.2*(E-c["B"])
    pm=c["A"]*size**E*em
    base_jh=pm*c["person_month_hours"]/c["day_hours"]
    base_months=c["C"]*pm**F
    return {"declarative_weight":weight,"EM":em,"size_ksloc_proxy":size,"E":E,"F":F,"person_months_base":pm,"jh_elaboration_construction":base_jh,"jh_full":base_jh*c["full_effort_factor"],"schedule_base_months":base_months,"schedule_full_months":base_months*c["full_schedule_factor"]}
def main():
    inputs=load(OUT/"inputs.json");m=load(OUT/"measurements.json");assert not m["errors"]
    c=inputs["calculation"];source=ROOT/"audits/2026-10-30-master-data-calcul/repartitions-sources.json"
    distribution=load(source)["cocomo"]
    phase_weights=distribution["phase_effort_percent_of_base"]
    results=[]
    for product in inputs["products"]:
        x=m["summary"][product["id"]]
        nominal=estimate(x["program_units"],x["declarative_units"],c["declarative_weight"],c["EM"],c)
        activities=[]
        for a in distribution["activities"]:
            ratio=sum(w*p for w,p in zip(phase_weights,a["percent_by_phase"]))/10000
            activities.append({"id":a["id"],"label":a["label"],"jh":nominal["jh_elaboration_construction"]*ratio,"fraction_of_full_effort":ratio/c["full_effort_factor"],"role_allocation":None})
        assert math.isclose(sum(a["jh"] for a in activities),nominal["jh_full"])
        full_units=x["program_units"]+x["declarative_units"]
        platform_units=x["by_layer"]["platform"]["program_units"]+x["by_layer"]["platform"]["declarative_units"]
        results.append({"id":product["id"],"label":product["label"],"technology":product["technology"],"measured_files":x["files"],"program_units":x["program_units"],"declarative_units":x["declarative_units"],"fraction_units_in_selected_platform":platform_units/full_units,"nominal":nominal,"declarative_sensitivity":[estimate(x["program_units"],x["declarative_units"],w,c["EM"],c) for w in c["declarative_weights_sensitivity"]],"context_illustration":[estimate(x["program_units"],x["declarative_units"],c["declarative_weight"],em,c) for em in [.75,1.5]],"activities":activities,"budget_admitted":False,"historical_observed_effort":None,"cosmic_cfp":None,"isbsg_jh":None,"uncertainty_interval":None})
    out={"id":inputs["id"],"status":inputs["status"],"source_hashes":{p:hashlib.sha256((OUT/p).read_bytes()).hexdigest() for p in ["inputs.json","manifest.json","measurements.json"]},"distribution_source":str(source.relative_to(ROOT)),"distribution_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),"results":results,"progress":inputs["progress"],"no_sum":"Quatre alternatives natives : aucun cumul des quatre ni moyenne. Pas de nouveau JH Flow."}
    (OUT/"results.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps([{"product":r["label"],"jh":round(r["nominal"]["jh_full"]),"months":round(r["nominal"]["schedule_full_months"],1),"platform_share_size":round(r["fraction_units_in_selected_platform"],3)} for r in results],ensure_ascii=False))
if __name__=="__main__":main()
