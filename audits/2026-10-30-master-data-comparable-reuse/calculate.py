from pathlib import Path
import json,hashlib,math
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def calc(size,scenario,c):
    n=size["new"];u=size["reused"];w=scenario["declarative_weight"]
    ns=n["program_units"]+w*n["declarative_units"];us=u["program_units"]+w*u["declarative_units"]
    aam=(scenario["AA"]+.3*scenario["IM"])/100
    equivalent=ns+aam*us
    E=c["B"]+.01*c["SF_sum"];F=c["D"]+.2*(E-c["B"])
    em=scenario["PERS"]*scenario["PREX"]*c["other_EM"]
    pm=c["A"]*(equivalent/1000)**E*em
    base_jh=pm*c["month_hours"]/c["day_hours"]
    base_duration=c["C"]*pm**F
    return {"scenario":scenario["id"],"new_logical_units":ns,"reused_logical_units":us,"AAM":aam,"reused_equivalent_units":aam*us,"equivalent_KSLOC":equivalent/1000,"E":E,"F":F,"EM":em,"base_person_months":pm,"base_jh":base_jh,"total_jh":base_jh*c["effort_phase_factor"],"base_schedule_months":base_duration,"total_schedule_months":base_duration*c["schedule_phase_factor"]}
i=load(OUT/"inputs.json");m=load(OUT/"measurements.json");assert not m["errors"]
dist=load(ROOT/"audits/2026-10-30-master-data-calcul/repartitions-sources.json")["cocomo"]
results=[]
for p in i["products"]:
    scenarios={s["id"]:calc(m["summary"][p["id"]],s,i["cocomo"]) for s in i["scenarios"]}
    activities=[]
    for a in dist["activities"]:
        ratio=sum(x*y for x,y in zip(dist["phase_effort_percent_of_base"],a["percent_by_phase"]))/10000
        activities.append({"id":a["id"],"label":a["label"],"jh":scenarios["central"]["base_jh"]*ratio,"share":ratio/i["cocomo"]["effort_phase_factor"]})
    assert math.isclose(sum(a["jh"] for a in activities),scenarios["central"]["total_jh"])
    # One-parameter sensitivity isolates why the envelope broadens.
    central=next(s for s in i["scenarios"] if s["id"]=="central")
    sensitivity={}
    for axis,values in {"declarative_weight":[.5,2],"AA":[0,4],"IM":[0,15],"PERS":[.83,1.26],"PREX":[.87,1.12]}.items():
        sensitivity[axis]=[calc(m["summary"][p["id"]],{**central,axis:value},i["cocomo"])["total_jh"] for value in values]
    results.append({**p,"sizes":m["summary"][p["id"]],"scenarios":scenarios,"activities_central":activities,"single_parameter_sensitivity":sensitivity,"observed_effort":None,"probability":None,"role_allocation":None,"flow_projection":None})
out={"id":i["id"],"results":results,"inputs_sha256":hashlib.sha256((OUT/"inputs.json").read_bytes()).hexdigest(),"measurements_sha256":hashlib.sha256((OUT/"measurements.json").read_bytes()).hexdigest(),"progress":{**i["progress"],"measured_files":len(m["files"]),"new_files":sum(x["new"]["files"] for x in m["summary"].values()),"reused_files":sum(x["reused"]["files"] for x in m["summary"].values()),"excluded_blocks":sum(x["new"]["excluded_blocks"] for x in m["summary"].values())}}
(OUT/"results.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"results":[{"id":r["id"],"jh":{k:round(v["total_jh"]) for k,v in r["scenarios"].items()},"months":{k:round(v["total_schedule_months"],1) for k,v in r["scenarios"].items()},"central_equivalent_KSLOC":r["scenarios"]["central"]["equivalent_KSLOC"]} for r in results],"progress":out["progress"]},ensure_ascii=False))
