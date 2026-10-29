"""Consolidation reproducible de l'iteration 06. Ecrit seulement l'audit."""
from __future__ import annotations
import json,sys,hashlib,re
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[2]
AUDIT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"tmp/model-deps"))
import yaml

def read(name):
    return json.loads((AUDIT/name).read_text(encoding="utf-8"))
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name,value):
    (AUDIT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
checks=[]
def check(label,condition):
    checks.append({"check":label,"passed":bool(condition)})
    if not condition:
        raise AssertionError(label)
cache={}
def doc(path):
    path=path.resolve()
    if path not in cache:
        raw=path.read_text(encoding="utf-8")
        cache[path]=json.loads(raw) if path.suffix==".json" else yaml.load(raw,Loader=getattr(yaml,"CSafeLoader",yaml.SafeLoader))
    return cache[path]
def resolve_pointer(ref):
    file,fragment=ref.split("#",1)
    path=ROOT/file
    if not path.exists(): path=AUDIT/file
    obj=doc(path)
    for token in fragment.lstrip("/").split("/"):
        if not token: continue
        token=token.replace("~1","/").replace("~0","~")
        obj=obj[int(token)] if isinstance(obj,list) else obj[token]
    return obj
def strings(value):
    if isinstance(value,str): yield value
    elif isinstance(value,list):
        for item in value: yield from strings(item)
    elif isinstance(value,dict):
        for item in value.values(): yield from strings(item)
def flat(value):
    if value is None:return ""
    if isinstance(value,str):return value
    if isinstance(value,list):return " | ".join(flat(v) for v in value)
    return " | ".join(str(k)+": "+flat(v) for k,v in value.items())
context=read("iteration-06-contexte.json")
protocol=read("iteration-06-protocole.json")
previous=read("iteration-05-resultats.json")
decision=read("iteration-06-decision.json")
guarantees=read("iteration-06-garanties.json")
parts={k:read(f"iteration-06-perimetre-{k}.json") for k in "abc"}
grid=doc(ROOT/"source/grille-complexite.yaml")["blocs"]
native=doc(ROOT/"sources/cartographie-scm-2026-10-24.yaml")["nodes"]
nodes={n["id"]:n for n in native}
native_indices={n["id"]:i for i,n in enumerate(native)}
blocks={b["capacite_id"]:(i,b) for i,b in enumerate(grid)}
old={c["id"]:c for c in previous["coverage"]}
comparative_ids=sorted(c["id"] for c in previous["coverage"] if c["financing_refs"])
check("88 capacites de la grille et du suivi precedent",len(grid)==len(old)==88 and set(blocks)==set(old))
check("Cumul comparatif precedent de 16 identifiants uniques",len(comparative_ids)==16)
check("Aucun total Core anterieur disponible",previous["full_core_jh"] is None)
for path,expected in {**context["source_hashes"],**context["additional_source_hashes"]}.items():
    check("Source inchangee : "+path,digest(ROOT/path)==expected)
check("Methode candidate inchangee",digest(AUDIT/"iteration-04-methode-candidate.json")==context["frozen_method_sha256"])

groups=[]
capabilities=[]
for tag,part in parts.items():
    for idx,g in enumerate(part["groups"]):
        gid=g.get("id",g.get("group_id"))
        ids=g.get("capability_ids",g.get("capabilities"))
        readiness=g.get("readiness",g.get("estimation_readiness",g.get("estimation_opinion")))
        status="choice" if readiness["status"].startswith("choix") else "conditional"
        condition=readiness.get("basis",readiness.get("proposed_hypotheses_or_choice",readiness.get("hypothesis_or_choice")))
        dependencies=g.get("dependencies",[])
        if not dependencies:
            for c in part["capabilities"]:
                if c["group_id"]==gid:
                    dependencies+=c.get("dependencies",c.get("shared_dependencies",[]))
        unique_dependencies=[]
        for dep in dependencies:
            if dep not in unique_dependencies:unique_dependencies.append(dep)
        groups.append({
            "id":gid,"name":g["name"],"capability_ids":ids,
            "local_readiness":status,"local_readiness_label":"Choix structurant a borner" if status=="choice" else "Estimation envisageable sous hypotheses",
            "condition":condition,"result":g.get("result",g.get("rationale")),
            "dependencies":unique_dependencies,
            "detail_ref":f"iteration-06-perimetre-{tag}.json#/groups/{idx}",
            "new_estimate_jh":None,"opportunity_admitted":False,
            "meaning":"Avis de preparation locale uniquement ; dependances et garanties restent a financer et a qualifier."
        })
    for idx,c in enumerate(part["capabilities"]):
        cid=c["id"]
        check("Capacite connue : "+cid,cid in blocks)
        i,b=blocks[cid]
        fields=nodes[cid]["fields"]
        name=c.get("name",c.get("native_name"))
        check("Nom natif : "+cid,name==fields["name"]==old[cid]["name"])
        check("Fonctions natives exactes : "+cid,c["native_functions"]==b["fonctions"])
        boundary=c.get("source_boundary",c.get("native_frontier",c.get("native_boundary")))
        check("Frontiere native exacte : "+cid,boundary==b["frontiere"])
        path=c["native_path"]
        path=[n["id"] if isinstance(n,dict) else n for n in path]
        check("Chemin natif : "+cid,path==old[cid]["path"]==b["chemin"])
        unknowns=c.get("unknowns",c.get("decisive_unknowns",c.get("determining_unknowns")))
        next_decision=c.get("next_decision",c.get("decision_to_enable_estimate"))
        result=c.get("result",c.get("result_expected",c.get("generic_result")))
        bounds=c.get("core_integration",c.get("boundary",c.get("boundaries")))
        check("Cadrage renseigne : "+cid,all([result,bounds,unknowns,next_decision,c.get("guarantees")]))
        if tag=="a":
            check("Aucune nouvelle evaluation comparative : "+cid,c["assessment_06"]["new_comparative_code_study"] is False and c["assessment_06"]["new_jh"] is False)
        elif tag=="b":
            check("Aucune nouvelle evaluation comparative : "+cid,c["progress"]["new_comparative_estimate"] is False and c["progress"]["new_jh"] is False)
        else:
            check("Aucune nouvelle evaluation comparative : "+cid,c["new_market_comparison"] is False and c["effort_jh"] is None)
        canonical_refs=[
            f"sources/cartographie-scm-2026-10-24.yaml#/nodes/{native_indices[cid]}/fields",
            f"source/grille-complexite.yaml#/blocs/{i}/fonctions",
            f"source/grille-complexite.yaml#/blocs/{i}/frontiere"
        ]
        capabilities.append({
            "id":cid,"block":b["id"],"name":name,"path":path,
            "path_names":[nodes[x]["fields"]["name"] for x in path],
            "group_id":c["group_id"],"framing_status":"cadree_documentairement",
            "comparative_status":"partielle_avec_hypotheses_JH" if cid in comparative_ids else "non_etudiee_par_comparaison",
            "prior_financing_refs":old[cid]["financing_refs"],"full_estimate_jh":None,
            "opportunity_admitted":False,"functions":c["native_functions"],
            "source_refs":canonical_refs,"detail_ref":f"iteration-06-perimetre-{tag}.json#/capabilities/{idx}",
            "result":result,"boundary":bounds,"unknowns":unknowns,"next_decision":next_decision,
            "prior_evaluation_ref":"iteration-05-resultats.json#/coverage/"+str(list(old).index(cid))
        })
capabilities.sort(key=lambda c:c["block"])
ids=[c["id"] for c in capabilities]
gids={g["id"] for g in groups}
check("88 capacites cadrees, sans doublon ni oubli",len(ids)==len(set(ids))==88 and set(ids)==set(blocks))
check("38 groupes distincts",len(groups)==len(gids)==38)
memberships=Counter(cid for g in groups for cid in g["capability_ids"])
check("Un seul rattachement principal par capacite",set(memberships)==set(ids) and set(memberships.values())=={1})
gmap={g["id"]:g for g in groups}
for c in capabilities:
    check("Rattachement reciproque : "+c["id"],c["id"] in gmap[c["group_id"]]["capability_ids"])
references=set(s for p in parts.values() for s in strings(p) if re.match(r"^(?:source/|sources/|audits/|iteration-)[^#]+#/",s))
references.update(s for c in capabilities for s in c["source_refs"])
references.update(s for s in strings(guarantees) if re.match(r"^(?:source/|sources/|audits/|iteration-)[^#]+#/",s))
for ref in sorted(references):
    check("Reference resolue : "+ref,resolve_pointer(ref) is not None)

tc={o["id"] for o in guarantees["technical_work_owners"]}
check("12 domaines de garanties",len(guarantees["areas"])==12 and len({g["id"] for g in guarantees["areas"]})==12)
check("9 responsabilites techniques proposees",len(tc)==9)
for g in guarantees["areas"]:
    check("Responsable de garantie : "+g["id"],g["owner"] in tc)
for dep in decision["dependency_resolutions"]:
    check("Proprietaires reconnus : "+dep["alias"],all(o in gids|tc|{"COMMON","EXEC","ORCH","C-SERVICE-COMMON"} for o in dep["owners"]))
for dep in decision["examples_of_conditional_dependencies"]:
    check("Dependance de preparation : "+dep["group"],dep["group"] in gids and all(o in gids|tc|{"C-SERVICE-COMMON"} for o in dep["depends_on"]))
conditionals=[g for g in groups if g["local_readiness"]=="conditional"]
choices=[g for g in groups if g["local_readiness"]=="choice"]
check("Avis locaux 24 conditionnels et 14 choix",len(conditionals)==24 and len(choices)==14)
subdomains=[]
for sid in dict.fromkeys(c["path"][1] for c in capabilities):
    caps=[c for c in capabilities if c["path"][1]==sid]
    subdomains.append({
        "id":sid,"name":nodes[sid]["fields"]["name"],"total":len(caps),"framed":len(caps),
        "partial_comparative":sum(c["id"] in comparative_ids for c in caps),
        "full_estimate":0,"opportunity_admitted":0
    })
check("9 sous-domaines et 28 Business Areas",len(subdomains)==9 and len({c["path"][2] for c in capabilities})==28)
check("Cumul comparatif conserve",sorted(c["id"] for c in capabilities if c["prior_financing_refs"])==comparative_ids)
metrics=[]
def metric(id,label,previous,current,denominator,meaning):
    metrics.append({"id":id,"label":label,"previous":previous,"current":current,
                    "delta":current-previous if previous is not None else None,
                    "denominator":denominator,"meaning":meaning})
metric("inventory","Capacites dans le perimetre",88,88,88,"Inventaire natif stable.")
metric("framed","Capacites cadrees : resultat, frontiere, garanties et inconnues",None,len(capabilities),88,"Nouvel indicateur : precedent non mesure. Ne mesure ni comparaison marche ni chiffrage complet.")
metric("partial_comparative","Cumul distinct des capacites etudiees par comparaison avec hypotheses de JH",16,len(comparative_ids),88,"Toutes partielles. Nombre d'identifiants, pas pourcentage des fonctions ou du cout couvert.")
metric("not_comparative","Capacites sans etude comparative avec hypotheses de JH",72,88-len(comparative_ids),88,"Le cadrage de cette iteration ne remplace pas l'etude comparative.")
metric("complete","Capacites integralement estimees",0,0,88,"Aucune couverture integrale de la portee native et de ses garanties n'est revendiquee.")
metric("reasonable","Capacites completes avec incertitude jugee raisonnable pour l'opportunite",0,0,88,"Aucune nouvelle admission ; une classe C seule n'accorde pas ce statut.")
metric("admitted_groups","Estimations de groupe declarees suffisantes pour une decision d'investissement",0,0,None,"Critere de decision de l'iteration 05 conserve.")
metric("proposed_groups","Ensembles proposes pour la future estimation",None,len(groups),None,"Propositions analytiques, pas modification de la cartographie.")
metric("local_conditional","Ensembles localement estimables sous hypotheses",None,len(conditionals),len(groups),"Avis de preparation ; dependances communes, garanties et estimation restent a instruire.")
metric("prior_choice","Ensembles avec choix structurant a borner",None,len(choices),len(groups),"Des variantes peuvent suffire ; ni architecture finale ni inventaire exhaustif de cas d'usage requis.")
metric("guarantees","Domaines de garanties documentes",None,len(guarantees["areas"]),None,"Attentes documentaires, hypotheses et questions distinctes ; aucune validation contractuelle deduite.")
metric("bounded_groups","Groupes fonctionnels bornes avec hypotheses de JH",4,4,None,"REF, STOCK, ORCH et PLAN dans leurs contrats partiels, et deux lots communs separes.")
metric("roles","Contributions groupe par role dimensionnees",51,51,None,"Contributions anterieures toutes classe C ; pas de nouvelle calibration.")

inputs=["iteration-06-protocole.json","iteration-06-contexte.json","iteration-06-decision.json","iteration-06-garanties.json",
        "iteration-06-perimetre-a.json","iteration-06-perimetre-b.json","iteration-06-perimetre-c.json","iteration-05-resultats.json","iteration-04-methode-candidate.json"]
lo,central,hi=previous["cumulative_evaluated_jh"]
result={
    "id":"iteration-06-resultats","date":protocol["date"],
    "scope":"Cadrage du Core generique Java/Spring ; audit isole, sources du modele inchangees.",
    "metrics":metrics,"subdomains":subdomains,"capabilities":capabilities,"groups":groups,
    "cumulative_comparative_ids":comparative_ids,"new_comparative_capacity_ids":[],
    "readiness_capability_counts":{"conditional_local":sum(len(g["capability_ids"]) for g in conditionals),"prior_choice":sum(len(g["capability_ids"]) for g in choices),"interpretation":"Mesure de preparation locale uniquement ; aucun pourcentage de precision ou de financement."},
    "previous_partial_jh":{"low":lo,"central":central,"high":hi,"meaning":decision["global_jh"],"source_ref":"iteration-05-resultats.json#/cumulative_evaluated_jh","range":"Enveloppe de sensibilite non probabiliste, pas percentiles."},
    "new_jh_estimate":None,"new_jh_work_performed":False,"full_core_jh":None,
    "decision":decision,"reasonableness_criteria":previous["progress"]["reasonableness_criteria"],
    "source_files_checked":len(context["source_hashes"]),
    "additional_source_files_checked":len(context["additional_source_hashes"]),
    "all_source_files_checked":len({**context["source_hashes"],**context["additional_source_hashes"]}),
    "source_count_meaning":"88 fichiers du modele, de configuration et de cartographie ; AGENTS.md est controle separement (89 au total).",
    "input_sha256":{n:digest(AUDIT/n) for n in inputs},
    "checks":checks,
    "limits":["Les 88 fiches sont un cadrage propose, pas une specification validee par les metiers.",
              "Aucune nouvelle lecture de code OSS, execution de test ou mesure d'effort humain dans cette iteration.",
              "Les budgets, notes ordinales de complexite et anciens JH des sources actives ne calibrent pas cet audit.",
              "Le regroupement analytique ne change aucun identifiant ni rattachement de la cartographie d'entree."]
}
save("iteration-06-resultats.json",result)
print(json.dumps({"capabilities":len(capabilities),"groups":len(groups),"conditional_groups":len(conditionals),
                  "structural_choices":len(choices),"cumulative_comparative":len(comparative_ids),
                  "native_functions":sum(len(c["functions"]) for c in capabilities),"source_hashes":len(context["source_hashes"]),
                  "resolved_pointers":len(references),"checks_passed":len(checks)},ensure_ascii=True))
