"""Reproduce the isolated iteration 04 report from estimates and recorded test evidence."""
from pathlib import Path
from collections import Counter
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit
import argparse, hashlib, json, xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def read(name): return json.loads((HERE/name).read_text(encoding="utf-8"))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true");args=ap.parse_args()
 names=["iteration-03-resultats.json","iteration-04-contrat.json","iteration-04-incertitude.json","iteration-04-contexte.json","iteration-04-methode-candidate.json","iteration-04-interpretation.json","iteration-04-parcours-qa.json","iteration-04-execution-journal.json","iteration-04-run-initial.json","iteration-04-run-ref-final.json"]
 docs={n:read(n) for n in names};prior=docs[names[0]];inc=docs[names[2]];ctx=docs[names[3]]
 checks=[]
 def check(label,cond):
  checks.append({"label":label,"passed":bool(cond)})
  if not cond:raise AssertionError(label)
 cells=inc["assessments"];roles=list(prior["estimates"]["M1"]["by_role"])
 check("27 cellules ensemble × rôle uniques",len(cells)==len({(c["ensemble"],c["role"]) for c in cells})==27)
 for c in cells:
  v=prior["estimates"]["M1"]["lots"][c["ensemble"]]["by_role"][c["role"]]
  check(c["ensemble"]+"/"+c["role"]+" : JH03 conservés",c["jh"]==v)
  check(c["ensemble"]+"/"+c["role"]+" : justification et suite présentes",bool(c["justification"] and c["uncertainty_cause"] and c["next_evidence"]))
 check("25 contributions C ; deux états sans classe",Counter(c["solidity_class"] for c in cells)=={"C":25,None:2})
 check("Les contributions non nulles gardent une classe distincte des zéros",all((c["solidity_class"]=="C") if c["jh"][1]>0 else c["solidity_class"] is None for c in cells))
 check("Pas de modification des chiffres ni resserrement automatique",inc["numeric_estimates_changed"] is False and inc["automatic_range_tightening"] is False)
 check("Totaux de qualification conservés",inc["preserved_m1_totals"]["total_jh"]==prior["estimates"]["M1"]["total_jh"])
 check("Variante sécurité STOCK inconnue et hors M1",inc["variants"][0]["jh"] is None and inc["variants"][0]["state"]=="ouverte_hors_M1")
 check("Sources des qualifications inchangées",all(sha(HERE/n)==h for n,h in inc["input_sha256"].items()))
 check("Sources actives et cartographie inchangées",all(sha(ROOT/n)==h for n,h in ctx["source_hashes"].items()))
 check("Le total du Core reste inconnu",prior["native_reporting"]["full_core_jh"] is None)
 records={k:docs["iteration-04-run-"+k+".json"] for k in ["initial","ref-final"]}
 check("Les deux exécutions ont arrêté leur base dédiée",all(r["database_stopped"] for r in records.values()))
 check("Le second passage ne rejoue que REF",records["ref-final"]["test_filter"]=="RefProbeTest")
 expected={"REF":5,"STOCK":6}
 suites=[]
 chosen={"REF":("ref-final","RefProbeTest"),"STOCK":("initial","StockProbeTest")}
 for family,(run,cls) in chosen.items():
  path=HERE/("iteration-04-test-results-"+run)/("TEST-flow.audit4."+cls+".xml")
  root=ET.fromstring(path.read_bytes())
  cases=[]
  for c in root.findall("testcase"):
   issue=c.find("failure")
   if issue is None:issue=c.find("error")
   cases.append({"name":c.attrib["name"],"seconds":float(c.attrib.get("time","0")),
                 "passed":issue is None and c.find("skipped") is None,
                 "issue":None if issue is None else issue.attrib.get("message",issue.text)})
  check(family+" : essais attendus présents, sans oubli silencieux",len(cases)==expected[family] and int(root.attrib["skipped"])==0)
  suites.append({"family":family,"run":run,"report":str(path.relative_to(HERE)).replace("\\","/"),
                 "tests":int(root.attrib["tests"]),"failures":int(root.attrib["failures"]),"errors":int(root.attrib["errors"]),
                 "seconds":float(root.attrib.get("time","0")),"cases":cases,"report_sha256":sha(path)})
 check("Les sources Java correspondent au dernier passage",all(sha(HERE/n)==h for n,h in records["ref-final"]["source_sha256"].items()))
 # The second run changed only the REF harness. STOCK and implementation proofs remain tied to their original source.
 stable=["StockProbe.java","StockProbeTest.java","RefProbe.java","RefProbeWorker.java","TestSupport.java"]
 check("Implémentations et STOCK non modifiés entre passages",all(
  records["initial"]["source_sha256"][n]==records["ref-final"]["source_sha256"][n]
  for n in records["initial"]["source_sha256"] if Path(n).name in stable))
 check("Aucune correction fonctionnelle non déclarée",all(v==0 for v in docs["iteration-04-execution-journal.json"]["functional_corrections"].values()))
 check("Base temporaire arrêtée à la génération",not (ROOT/"tmp/iteration04-runtime/cluster/postmaster.pid").exists())
 all_passed=all(c["passed"] for s in suites for c in s["cases"])
 elapsed=[{"run":k,"started_utc":r["started_utc"],"finished_utc":r["finished_utc"],"interpretation":"Durée d'investigation technique ; aucun équivalent JH humain."} for k,r in records.items()]
 result={"id":"iteration-04-resultats","date":"2026-10-29","source_estimation":"iteration-03-resultats.json",
         "m1_jh":prior["estimates"]["M1"]["total_jh"],"m2_jh":prior["estimates"]["M2"]["total_jh"],
         "class_counts":{"C":25,"non_classe":2},"jh_changed":False,"percentiles":None,
         "source_files_unchanged":len(ctx["source_hashes"]),"checks":checks,
         "technical_tests":{"all_passed":all_passed,"selected_suites":suites,"distinct_tests":sum(s["tests"] for s in suites),
                            "initial_failure_retained":"iteration-04-test-results-initial/TEST-flow.audit4.RefProbeTest.xml",
                            "counts_are_not_probability":True},
         "run_timing":elapsed,"runtime":records["ref-final"]["versions"],
         "candidate_method":"iteration-04-methode-candidate.json","native_reporting":prior["native_reporting"],
         "recommendation":docs["iteration-04-interpretation.json"]["next_iteration"],
         "limits":"Résultats techniques bornés, pas de productivité mesurée ni validation de précision. C reste C.",
         "input_sha256":{n:sha(HERE/n) for n in names}}
 from iteration04_render import render
 html=render(result,docs)
 class Links(HTMLParser):
  def __init__(self):super().__init__();self.ids=[];self.links=[]
  def handle_starttag(self,tag,attrs):
   a=dict(attrs)
   if "id" in a:self.ids.append(a["id"])
   if tag=="a" and "href" in a:self.links.append(a["href"])
 p=Links();p.feed(html)
 if len(p.ids)!=len(set(p.ids)):raise AssertionError("Duplicate HTML ID")
 for link in p.links:
  u=urlsplit(link)
  if u.scheme in ["http","https"]:continue
  if not u.path and u.fragment not in p.ids:raise AssertionError("Unknown anchor "+link)
  if u.path and u.path not in ["iteration-04-resultats.json","iteration-04.html"] and not (HERE/u.path).is_file():raise AssertionError("Missing local link "+link)
 if "\ufffd" in html:raise AssertionError("Unicode replacement character")
 encoded=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
 if args.check:
  if (HERE/"iteration-04-resultats.json").read_text(encoding="utf-8")!=encoded:raise AssertionError("Result is not reproducible")
  if (HERE/"iteration-04.html").read_text(encoding="utf-8")!=html:raise AssertionError("Report is not reproducible")
 else:
  (HERE/"iteration-04-resultats.json").write_text(encoded,encoding="utf-8")
  (HERE/"iteration-04.html").write_text(html,encoding="utf-8")
 print(json.dumps({"consistency_checks":len(checks),"technical_tests":result["technical_tests"]["distinct_tests"],"technical_tests_passed":all_passed,"class_counts":result["class_counts"],"active_files_unchanged":result["source_files_unchanged"],"html_links":len(p.links),"mode":"check" if args.check else "write"}))
if __name__=="__main__":main()
