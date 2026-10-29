"""Published COCOMO II.2000 Early Design equations, conditional audit only."""
from __future__ import annotations
import json, math
from pathlib import Path
HERE=Path(__file__).resolve().parent
METHOD=json.loads((HERE/"iteration-08-methode.json").read_text(encoding="utf-8"))

def raw(size_ksloc, exponent, multiplier_ns=1.0, multiplier_sced=1.0, sced_pct=100.0):
    assert size_ksloc>0 and exponent>0 and multiplier_ns>0 and multiplier_sced>0 and sced_pct>0
    c=METHOD["constants"]
    pm_ns=c["A"]*size_ksloc**exponent*multiplier_ns
    pm=pm_ns*multiplier_sced
    f=c["D"]+0.2*(exponent-c["B"])
    months=c["C"]*pm_ns**f*sced_pct/100
    return {"size_ksloc":size_ksloc,"E":exponent,"F":f,"multiplier_ns":multiplier_ns,
            "multiplier_sced":multiplier_sced,"sced_pct":sced_pct,"person_months_ns":pm_ns,
            "person_months":pm,"effort_jh":pm*c["person_month_hours"]/c["jh_hours"],
            "development_months":months,"staffing_average":pm/months}

def evaluate(size_ksloc, scenario):
    c=METHOD["constants"]
    assert set(scenario["sf"])==set(METHOD["scale_factors"])
    assert set(scenario["em"])==set(METHOD["effort_multipliers"])
    sfs={key:METHOD["scale_factors"][key][rating] for key,rating in scenario["sf"].items()}
    ems={key:METHOD["effort_multipliers"][key][rating] for key,rating in scenario["em"].items()}
    e=c["B"]+0.01*sum(sfs.values())
    out=raw(size_ksloc,e,math.prod(v for k,v in ems.items() if k!="SCED"),
            ems["SCED"],METHOD["schedule_percent"][scenario["em"]["SCED"]])
    out.update({"scenario_id":scenario["id"],"scenario_label":scenario["label"],"sf_values":sfs,"em_values":ems})
    return out

def sensitivity(size_ksloc):
    base=METHOD["scenarios"][0]
    center=evaluate(size_ksloc,base)
    rows=[]
    for kind,table in [("sf","scale_factors"),("em","effort_multipliers")]:
        for factor in METHOD[table]:
            for rating in ["L","H"]:
                if rating not in METHOD[table][factor]:continue
                scenario=json.loads(json.dumps(base))
                scenario[kind][factor]=rating
                scenario["id"]=f"{factor}-{rating}"
                scenario["label"]=METHOD[table][factor]["label"]+" / "+rating
                r=evaluate(size_ksloc,scenario)
                rows.append({"factor":factor,"rating":rating,"kind":kind,
                             "effort_change_pct":100*(r["effort_jh"]/center["effort_jh"]-1),
                             "schedule_change_pct":100*(r["development_months"]/center["development_months"]-1),
                             "result":r})
    return rows

def verify():
    checks=[]
    def check(label,ok):
        checks.append({"check":label,"passed":bool(ok)})
        assert ok,label
    example=raw(100,1.15)
    check("Published manual example effort",abs(example["person_months"]-586.61)<0.01)
    check("Published manual example calendar",abs(example["development_months"]-29.7)<0.1)
    nom=evaluate(10,METHOD["scenarios"][0])
    check("Nominal exponent",math.isclose(nom["E"],1.0997,abs_tol=1e-12))
    compressed=json.loads(json.dumps(METHOD["scenarios"][0]));compressed["em"]["SCED"]="L"
    x=evaluate(10,compressed)
    check("SCED effort",math.isclose(x["effort_jh"]/nom["effort_jh"],1.14))
    check("SCED calendar uses PM_NS",math.isclose(x["development_months"]/nom["development_months"],0.85))
    check("JH conversion",math.isclose(x["effort_jh"]*7,x["person_months"]*152))
    check("Aggregate size before project exponent",evaluate(3+7,METHOD["scenarios"][0])["effort_jh"]>evaluate(3,METHOD["scenarios"][0])["effort_jh"]+evaluate(7,METHOD["scenarios"][0])["effort_jh"])
    check("Schedule is not person-months",not math.isclose(nom["development_months"],nom["person_months"]))
    return {"checks":checks,"manual_example":example}

if __name__=="__main__":
    print(json.dumps(verify(),ensure_ascii=True))
