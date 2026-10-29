"""Render iteration 07 from frozen audit inputs; never estimate or allocate effort.

Only standard-library modules are used. Numeric values belong to the consolidated
JSON. This renderer preserves the M1/M2 distinction and refuses a full-Core total.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from pathlib import Path
from urllib.parse import quote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

LABELS = {
    "status":"Statut", "verdict":"Verdict", "reason":"Motif", "meaning":"Interprétation",
    "scope":"Périmètre", "result":"Résultat", "boundary":"Frontière", "limits":"Limites",
    "limitations":"Limites", "why":"Pourquoi", "question":"Question", "next":"Suite",
    "next_step":"Étape suivante", "next_decision":"Décision suivante", "condition":"Condition",
    "conditions":"Conditions", "hypotheses":"Hypothèses", "assumptions":"Hypothèses",
    "source_refs":"Sources", "proof_refs":"Preuves", "detail_ref":"Analyse détaillée",
    "title":"Objet", "label":"Libellé", "name":"Nom", "id":"Identifiant",
    "origin":"Origine", "description":"Description", "method":"Méthode",
    "progress":"Progrès", "unchanged":"Ce qui reste inchangé", "confidence":"Confiance",
    "uncertainty":"Incertitude", "effort":"Effort", "effect":"Incidence", "decision":"Décision",
    "low":"Bas", "central":"Central", "high":"Haut", "total":"Total",
    "target":"Cible", "steps":"Travaux proposés", "success":"Critère de réussite",
    "stop_or_redirect":"Arrêt ou réorientation", "retained":"Retenu", "excluded":"Exclu",
    "known_limits":"Limites connues", "gap":"Écart", "causes":"Causes",
    "evidence":"Preuves", "use":"Usage dans l'étude", "observed":"Constat",
    "compatibility_limit":"Limite de compatibilité", "funding":"Financement",
    "shared_work":"Travaux partagés", "native_function_ids":"Fonctions natives",
    "opportunity_admitted":"Incertitude admise pour l'opportunité",
    "range_is_probabilistic":"Fourchette probabiliste", "meaning_of_ranges":"Sens des fourchettes",
    "subject":"Sujet", "candidate_owners":"Travaux susceptibles de le porter",
    "full_core_jh":"Estimation complète du Core", "new_evidence":"Nouvelle preuve attendue",
    "actions":"Actions", "proposed_action":"Action proposée", "impact":"Incidence",
}

def esc(value: object) -> str:
    # Display-only terminology: frozen audit inputs retain their original wording.
    text = str(value)
    for original, clarified in [
        ("L'incertitude des dur\u00e9es", "L'incertitude des charges de travail"),
        ("dur\u00e9es non calibr\u00e9es", "charges de travail non calibr\u00e9es"),
        ("jugements de dur\u00e9e", "hypoth\u00e8ses de charge"),
        ("hypoth\u00e8ses de dur\u00e9e", "hypoth\u00e8ses de charge"),
        ("preuve de dur\u00e9e", "r\u00e9f\u00e9rence de charge observ\u00e9e"),
        ("attribue des dur\u00e9es", "attribue des charges"),
        ("aujourd'hui sa dur\u00e9e", "aujourd'hui sa charge"),
    ]:
        text = text.replace(original, clarified)
    return html.escape(text, quote=True)

def number(value: object, signed: bool=False) -> str:
    if value is None:
        return "Inconnu"
    if isinstance(value, bool):
        return "Oui" if value else "Non"
    if isinstance(value, (int, float)):
        s = f"{value:,.3f}".rstrip("0").rstrip(".").replace(",", "\u202f").replace(".", ",")
        return ("+" if signed and value > 0 else "") + s
    return esc(value)

def triplet(value: object) -> str:
    if isinstance(value, dict):
        vals = [value[k] for k in ("low", "central", "high")]
    else:
        vals = list(value)
    if len(vals) != 3:
        raise ValueError("Une fourchette doit conserver trois bornes.")
    return '<span class="triplet">' + " / ".join(number(x) for x in vals) + "</span>"

def ref_link(ref: object, label: str | None=None) -> str:
    if isinstance(ref, dict):
        label = label or ref.get("label") or ref.get("title") or ref.get("id")
        ref = ref.get("ref") or ref.get("file") or ref.get("path") or ref.get("url")
    if not isinstance(ref, str) or not ref:
        return '<span class="muted">Référence non renseignée</span>'
    label = label or ref
    scheme = urlsplit(ref).scheme
    if scheme in ("http", "https"):
        target = ref
    elif scheme or ref.startswith("//"):
        return esc(label)
    else:
        path, marker, fragment = ref.partition("#")
        if path.lower().endswith((".yaml", ".yml")):
            return esc(label)
        if path.startswith(("audits/", "source/", "sources/", "app/")):
            path = os.path.relpath(ROOT / path, HERE).replace("\\", "/")
        target = quote(path, safe="/.-_") + ("#" + quote(fragment, safe="/.-_~") if marker else "")
    return f'<a href="{esc(target)}">{esc(label)}</a>'

def prose(value: object) -> str:
    if value is None:
        return '<span class="muted">Non déterminé</span>'
    if isinstance(value, (bool, int, float)):
        return number(value)
    if isinstance(value, str):
        if value.startswith(("http://", "https://")):
            return ref_link(value)
        return "<br>".join(esc(value).splitlines())
    if isinstance(value, list):
        return '<ul class="plain-list">' + "".join("<li>"+prose(v)+"</li>" for v in value) + "</ul>" if value else '<span class="muted">Aucun élément</span>'
    if isinstance(value, dict):
        return '<dl class="data-list">' + "".join(
            "<dt>"+esc(LABELS.get(k,k.replace("_"," ")))+"</dt><dd>"+
            (refs(v) if k in ("source_refs","proof_refs","detail_refs") else ref_link(v) if k in ("detail_ref","url") else prose(v))+
            "</dd>" for k,v in value.items()
        ) + "</dl>"
    return esc(value)

def refs(values: object) -> str:
    items = values if isinstance(values, list) else [values]
    return '<ul class="plain-list sources">' + "".join("<li>"+ref_link(x)+"</li>" for x in items) + "</ul>"

def table(headers: list[str], rows: list[str], caption: str) -> str:
    return '<div class="table-wrap" tabindex="0" role="region" aria-label="'+esc(caption)+'"><table><caption>'+esc(caption)+'</caption><thead><tr>' + "".join('<th scope="col">'+esc(h)+'</th>' for h in headers) + "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"

def section(identifier: str, title: str, body: str) -> str:
    return '<section id="'+esc(identifier)+'"><h2>'+esc(title)+'</h2>'+body+'</section>'

def card(title: str, body: str, identifier: str="") -> str:
    return '<article class="card"'+(' id="'+esc(identifier)+'"' if identifier else '')+'><h3>'+esc(title)+'</h3>'+body+'</article>'

def note(body: str) -> str:
    return '<div class="note">'+body+'</div>'

STYLE = "\n:root{--green:#236159;--mint:#D9F2EA;--ivory:#FAF8F4;--ink:#182632;--muted:#45525A;--orange:#FF7A1A;--peach:#FFF0DB;--line:#CBD7D2;--head:#F4F8F6}\n*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:1rem}body{margin:0;background:var(--ivory);color:var(--ink);font:16px/1.55 Aptos,\"Segoe UI\",Arial,sans-serif}a{color:var(--green);text-underline-offset:3px}a:hover{color:#16443d}a:focus-visible,[tabindex]:focus-visible{outline:3px solid var(--green);outline-offset:4px}\nh1,h2,h3{font-family:\"Aptos Display\",Aptos,\"Segoe UI\",Arial,sans-serif;line-height:1.2}h1{font-size:clamp(2rem,4vw,3rem);max-width:27ch;margin:.6rem 0 1rem}h2{font-size:1.65rem;margin:0 0 1rem}h3{font-size:1.12rem;margin:0 0 .65rem}p{margin:.6rem 0 1rem}small,.small{font-size:.83rem}.muted{color:var(--muted)}.eyebrow{text-transform:uppercase;letter-spacing:.08em;font-size:.8rem;font-weight:700}.hero{background:var(--mint);border-top:7px solid var(--green);padding:2.5rem max(1.5rem,calc((100vw - 1320px)/2))}.hero p{max-width:90ch}.marker{display:inline-block;width:.55rem;height:.55rem;background:var(--orange);border-radius:50%;margin-right:.5rem}.skip{position:absolute;top:-10rem;left:1rem;background:white;padding:.8rem;z-index:10}.skip:focus{top:1rem}\n.layout{display:grid;grid-template-columns:190px minmax(0,1fr);gap:2.2rem;max-width:1440px;margin:auto;padding:2.2rem 2rem 4rem}main{min-width:0}.toc{position:sticky;top:1rem;align-self:start;font-size:.9rem}.toc strong{display:block;margin-bottom:.7rem}.toc a{display:block;padding:.4rem .6rem;border-left:2px solid var(--line);text-decoration:none}.toc a:hover{background:var(--mint);border-left-color:var(--green)}section{margin-bottom:2.8rem;scroll-margin-top:1rem}section+section{border-top:1px solid var(--line);padding-top:1.7rem}\n.cards{display:grid;grid-template-columns:minmax(0,1fr);gap:1rem}.card{min-width:0;background:white;border:1px solid var(--line);border-top:3px solid var(--green);padding:1.25rem}.card p:last-child{margin-bottom:0}.columns{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem}.note{border-left:4px solid var(--orange);background:var(--peach);padding:1rem 1.2rem;margin:1rem 0 1.4rem}.note p:last-child{margin-bottom:0}.tag{display:inline-block;background:#F4F5FB;padding:.15rem .4rem;font-size:.78rem}.id{font-size:.76rem;color:var(--muted);overflow-wrap:anywhere}.strong{font-weight:650}.plain-list{padding-left:1.2rem;margin:.3rem 0 1rem}.plain-list li+li{margin-top:.35rem}\n.table-wrap{max-width:100%;overflow:auto;background:white;border:1px solid var(--line);margin:1rem 0 1.6rem}table{width:100%;border-collapse:collapse;text-align:left;font-size:.9rem}caption{text-align:left;padding:.8rem 1rem;color:var(--muted);font-size:.88rem}th{background:var(--head);font-size:.78rem;font-weight:650;color:var(--ink)}th,td{vertical-align:top;padding:.75rem .85rem;border-bottom:1px solid var(--line)}tbody tr:last-child td{border-bottom:0}td.num{white-space:nowrap;font-variant-numeric:tabular-nums;font-weight:650}td p{margin:.15rem 0 .6rem}.total-row th,.total-row td{background:#F0F8F5;border-top:2px solid var(--green);font-weight:700}.triplet{white-space:nowrap;font-variant-numeric:tabular-nums}.data-list{display:grid;grid-template-columns:minmax(150px,1fr) 3fr;gap:.45rem 1rem;margin:.3rem 0 1rem}.data-list dt{font-weight:650;font-size:.88rem}.data-list dd{margin:0}.data-list .data-list{display:block}.data-list .data-list dt{margin:.4rem 0}.sources{overflow-wrap:anywhere}.checksum{font-size:.72rem;overflow-wrap:anywhere}footer{max-width:1320px;margin:auto;padding:0 2rem 2.5rem;color:var(--muted);font-size:.83rem}\n@media(max-width:1000px){.layout{display:block;padding:1.4rem 1rem}.toc{position:static;display:flex;flex-wrap:wrap;gap:.2rem;margin-bottom:1.7rem}.toc strong{width:100%}.toc a{border:0;padding:.35rem .5rem}.hero{padding:2rem 1.2rem}.columns{grid-template-columns:1fr}.data-list{display:block}.data-list dt{margin-top:.6rem}.data-list dd{margin-bottom:.6rem}}\n@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}\n@media print{body{background:white;font-size:10pt}.hero{background:white;padding:1cm 0;border-top-width:3px}.layout{display:block;padding:0}.toc,.skip{display:none}h1{font-size:25pt}h2{font-size:18pt}section{break-before:auto}.card{break-inside:avoid}.table-wrap{overflow:visible;border:0}table{font-size:8pt}thead{display:table-header-group}tr{break-inside:avoid}td,th{padding:5pt}.note{background:white;border:1px solid var(--line);border-left:3px solid var(--orange)}a{color:var(--ink)}footer{padding:0}.columns{display:block}}\n"

def pct(value: object) -> str:
    if value is None:
        return "Non calculable"
    return f"{float(value):.1f}".replace(".", ",") + " %"

def validate(data: dict) -> None:
    if data["full_core_jh"] is not None or data["cumulative_jh"] is not None:
        raise ValueError("Cette itération ne peut afficher ni total complet du Core ni cumul de contrats différents.")
    if data["comparison"]["selected_estimate"] is not None:
        raise ValueError("Aucune estimation n'a été retenue.")
    studied=data["cumulative_comparative_ids"]
    if len(studied)!=len(set(studied)):
        raise ValueError("Le cumul doit compter des capacités distinctes.")
    if not set(data["new_comparative_ids"]) <= set(studied):
        raise ValueError("Les nouvelles capacités doivent appartenir au cumul.")
    for model in data["models"].values():
        for i in range(3):
            if abs(model["COMMON07"][i]+model["REF07"][i]-model["total"][i])>1e-7:
                raise ValueError("Le socle et la famille ne conservent pas le total.")
            for part in ("COMMON07","REF07","total"):
                if abs(sum(r[part][i] for r in model["by_role"])-model[part][i])>1e-7:
                    raise ValueError("Le total par rôle ne conserve pas "+part)
        for row in model["by_role"]:
            if any(abs(row["COMMON07"][i]+row["REF07"][i]-row["total"][i])>1e-7 for i in range(3)):
                raise ValueError("La ventilation du rôle ne conserve pas son total.")
    if any(c["opportunity_admitted"] for c in data["family"]):
        raise ValueError("Aucune capacité de cette itération n'est déclarée admise pour l'opportunité.")
    for s in data["subdomains"]:
        if not 0 <= s["scenario_estimated"] <= s["comparative"] <= s["total"]:
            raise ValueError("Les états de couverture ne sont pas cohérents.")
    checks=data.get("checks",[])
    if isinstance(checks,list):
        failed=[c for c in checks if isinstance(c,dict) and c.get("passed",c.get("ok",True)) is False]
        if failed:
            raise ValueError("Les résultats consolidés comportent un contrôle non satisfait.")

def load_sidecar(name: str, data: dict) -> dict:
    path=HERE/name
    content=path.read_bytes()
    expected=data.get("input_sha256",{}).get(name)
    if expected and hashlib.sha256(content).hexdigest()!=expected:
        raise ValueError("Une entrée documentaire a changé : "+name)
    return json.loads(content.decode("utf-8-sig"))

def fields_block(value: dict, keys: list[str]) -> str:
    return "".join("<p><strong>"+esc(LABELS.get(k,k.replace("_"," ")))+"</strong></p>"+prose(value[k]) for k in keys if value.get(k) is not None)

def render(data: dict, result_path: Path) -> str:
    validate(data)
    scope=load_sidecar("iteration-07-perimetre.json",data)
    spring=load_sidecar("iteration-07-spring-preuves.json",data)
    market=load_sidecar("iteration-07-marche-preuves.json",data)
    cosmic=load_sidecar("iteration-07-cosmic.json",data)
    schedule=load_sidecar("iteration-07-exigence-delai.json",data)
    if any(schedule["current_iteration"][key] is not None for key in ("cocomo_effort_jh","nominal_development_months","constrained_development_months","average_staffing")):
        raise ValueError("Aucun délai ni effectif COCOMO n'est calculé dans cette itération figée.")
    review=load_sidecar("iteration-07-revue-ecarts-m2.json",data)
    prior=load_sidecar("iteration-06-resultats.json",data)
    functions={f["id"]:f for f in scope["functions"]}
    proof_links={p["id"]:p["url"] for p in market["proofs"]}
    proof_links.update({p["id"]:p["url"] for p in spring["evidence"]})
    decision=data["decision"]
    models=data["models"]
    comparison=data["comparison"]
    sections=[]
    summary=note("<strong>"+esc(decision["verdict"])+"</strong><p>"+esc(decision["estimate_use"]["reason"])+"</p>")
    summary+=card("Délai de développement : sortie à conserver, non calculée à cette itération",
        "<p>La méthode doit restituer la charge en JH par rôle et le délai indicatif en mois calendaires : délai nominal, puis délai contraint si ce scénario est étudié. Les hypothèses d'équipe et les incertitudes de charge et de délai doivent rester explicites.</p>"
        "<p>Le délai de développement couvre des jalons à préciser. Il reste distinct de l'intégration Beaumanoir, du déploiement des marques et du calendrier global du programme. Les JH actuels ne sont pas convertis en mois par simple division.</p>"
        "<p>"+ref_link("iteration-07-exigence-delai.json","Exigence de restitution du délai conservée à la demande de l’utilisateur")+"</p>")
    summary += '<div class="columns">'+card("Ce qui progresse",prose(decision["progress"]))+card("Ce qui ne s'améliore pas",prose(decision["not_improved"]))+"</div>"
    summary += "<p><strong>Prochaine décision.</strong> "+esc(decision["next_iteration"]["recommendation"])+"</p>"
    sections.append(section("synthese","Une famille décrite et chiffrée, des charges de travail encore incertaines",summary))

    rows=[]
    for metric in data["metrics"]:
        current=number(metric["current"])
        if metric.get("denominator") is not None:
            current+=" / "+number(metric["denominator"])
        label="Capacités complètes dont l'incertitude est jugée acceptable pour l'opportunité" if metric["id"]=="opportunity_admitted" else metric["label"]
        rows.append("<tr><td><strong>"+esc(label)+'</strong></td><td class="num">'+number(metric.get("previous"))+'</td><td class="num">'+current+'</td><td class="num">'+number(metric.get("delta"),True)+"</td><td>"+prose(metric["meaning"])+"</td></tr>")
    body=table(["Indicateur","Avant","À cette étape","Variation","Ce que cela signifie"],rows,"Couverture, comparaison et incertitude sont des indicateurs distincts")
    rows=[]
    for item in data["subdomains"]:
        rows.append("<tr><td><strong>"+esc(item["name"])+'</strong><br><span class="id">'+esc(item["id"])+"</span></td>"+''.join('<td class="num">'+number(item[k])+"</td>" for k in ("total","comparative","scenario_estimated","opportunity_admitted"))+"</tr>")
    totals={k:sum(s[k] for s in data["subdomains"]) for k in ("total","comparative","scenario_estimated","opportunity_admitted")}
    rows.append('<tr class="total-row"><th scope="row">Total des capacités distinctes</th>'+''.join('<td class="num">'+number(totals[k])+"</td>" for k in totals)+"</tr>")
    body+=table(["Sous-domaine","Inventaire","Comparées avec hypothèses de JH","Estimation complète d'un scénario","Incertitude acceptable pour l'opportunité"],rows,"Cumul par sous-domaine — aucune extrapolation des JH")
    cap_index={c["id"]:c for c in prior["capabilities"]}
    current_ids={c["id"] for c in data["family"]}
    rows=[]
    for cid in data["cumulative_comparative_ids"]:
        c=cap_index[cid]
        label=c["name"]
        state="Scénario S1 estimé, incertitude non admise" if cid in current_ids else "Étude antérieure partielle"
        label_html=('<a href="#cap-'+esc(cid)+'">'+esc(label)+'</a>') if cid in current_ids else ref_link('iteration-06.html#cap-'+cid,label)
        rows.append('<tr><td>'+label_html+'<br><span class="id">'+esc(cid)+'</span></td><td>'+esc(c.get("path_names",["",""])[1])+'</td><td>'+state+'</td><td>'+("Nouvelle capacité étudiée" if cid in data["new_comparative_ids"] else "Déjà étudiée")+'</td></tr>')
    body+=table(["Capacité native","Sous-domaine","Étendue de l'étude","Progression07"],rows,"Liste nominative cumulée — chaque capacité n'apparaît qu'une fois")
    body+=note("<strong>Le cumul porte sur les capacités distinctes.</strong><p>"+esc(decision["funding"]["old_contracts"])+"</p><p>Le total du Core et le cumul des JH de contrats hétérogènes restent inconnus.</p>")
    sections.append(section("progres","Progression et cumul des capacités",body))

    rows=[]
    for key,label in (("M1","M1 — hypothèse par travaux"),("M2","M2 — estimation de comparaison par rôle")):
        rows.append("<tr><td><strong>"+label+"</strong></td>"+''.join('<td class="num">'+number(n)+" JH</td>" for n in models[key]["total"])+"</tr>")
    body=table(["Approche","Bas","Central","Haut"],rows,"Famille Operational References + socle nécessaire — JH bruts, tous rôles")
    body+=note("<strong>Écart entre les centres : "+number(comparison["total_delta_central"],True)+" JH, soit "+pct(comparison["total_relative_pct"])+" par rapport à M1.</strong><p>Aucune valeur retenue ni moyenne. Les bornes gardent le même périmètre ; elles ne sont pas des percentiles.</p>")
    rows=[]
    owner_labels={"REF07":"Famille de références, hors socle","COMMON07":"Socle commun nécessaire à cette famille"}
    for owner in comparison["owners"]:
        if owner["owner"] not in ("REF07","COMMON07"):
            continue
        rows.append("<tr><td><strong>"+esc(owner_labels[owner["owner"]])+'</strong><br><span class="id">'+esc(owner["owner"])+"</span></td><td>"+triplet(owner["M1"])+"</td><td>"+triplet(owner["M2"])+'</td><td class="num">'+number(owner["delta_central"],True)+"</td><td>"+pct(owner["relative_pct"])+"</td></tr>")
    rows.append('<tr class="total-row"><th scope="row">Total étudié, tous rôles</th><td>'+triplet(models["M1"]["total"])+"</td><td>"+triplet(models["M2"]["total"])+'</td><td class="num">'+number(comparison["total_delta_central"],True)+"</td><td>"+pct(comparison["total_relative_pct"])+"</td></tr>")
    body+=table(["Responsabilité de financement","M1 : bas / central / haut","M2 : bas / central / haut","Écart central (JH)","Écart / M1"],rows,"Séparation du socle et de la famille — toutes les charges en JH")
    body+="<p>"+esc(decision["funding"]["family_and_common"])+"</p><p><strong>Hors total étudié :</strong> "+esc(decision["funding"]["excluded"])+"</p>"
    sections.append(section("estimations","Deux estimations du même scénario S1",body))

    rows=[]
    for r in comparison["by_role"]:
        rows.append("<tr><td><strong>"+esc(r["label"])+'</strong><br><span class="id">'+esc(r["role"])+"</span></td><td>"+triplet(r["M1"])+"</td><td>"+triplet(r["M2"])+'</td><td class="num">'+number(r["delta_central"],True)+"</td><td>"+pct(r["relative_pct"])+"</td></tr>")
    body=table(["Rôle","M1 : bas / central / haut","M2 : bas / central / haut","Écart central (JH)","Écart / M1"],rows,"Contributions au sous-domaine — JH bruts par rôle, famille et socle inclus")
    body+="<p>"+esc(decision["granularity"]["reporting"])+"</p>"
    body+="<p>La ventilation en JH entre ces neuf rôles est une justification distincte : elle n'est pas une sortie automatique de la formule globale COCOMO II.</p>"
    body+="<h3>Pourquoi les écarts restent ouverts</h3><p>"+esc(review["findings"]["dominant_explanation"])+"</p><p>"+esc(review["findings"]["which_estimate_is_right"])+"</p>"
    labels={r["role"]:r["label"] for r in comparison["by_role"]}
    rows=["<tr><td><strong>"+esc(labels[r["role"]])+"</strong></td><td>"+esc(r["classification"])+"<p>"+esc(r["judgment"])+"</p></td><td>"+esc(r["investigation"])+"</td></tr>" for r in review["material_role_reviews"]]
    body+=table(["Rôle","Nature du désaccord, sans lui attribuer de jours","Preuve ou décision utile"],rows,"Revue des écarts matériels — une omission n'est pas déduite d'un chiffre plus élevé")
    for key in ("M1","M2"):
        rows=[]
        for r in models[key]["by_role"]:
            rows.append("<tr><td>"+esc(r["label"])+"</td><td>"+triplet(r["REF07"])+"</td><td>"+triplet(r["COMMON07"])+"</td><td>"+triplet(r["total"])+"</td></tr>")
        body+=table(["Rôle","Famille : bas / central / haut","Socle : bas / central / haut","Total : bas / central / haut"],rows,key+" — ventilation des contributions, sans double compte (JH)")
    sections.append(section("roles","Les neuf rôles et la part commune",body))

    cards=[]
    for capability in data["family"]:
        path=" › ".join(capability.get("path_names",[]))
        function_rows=[]
        for fid in capability["function_ids"]:
            f=functions[fid]
            function_rows.append('<tr><td><strong>'+esc(fid)+'</strong><br>'+esc(f["native_label"])+"</td><td>"+esc(f["minimum"])+"</td></tr>")
        text='<p class="small muted">'+esc(path)+'</p><p class="id">'+esc(capability["block"])+" · "+esc(capability["id"])+"</p>"
        text+=table(["Fonction native","Résultat minimum documenté"],function_rows,"Fonctions représentées dans le scénario S1")
        text+="<p><strong>Travaux propres ou directement rattachés :</strong> "+esc(", ".join(capability["direct_packages"]))+"</p>"
        text+="<p><strong>Travaux partagés :</strong> "+esc(", ".join(capability["shared_packages"]))+"</p>"
        text+="<p>"+ref_link("iteration-07-perimetre.json","Périmètre et frontières détaillés")+" · "+ref_link("iteration-07-revue-perimetre.json","Revue indépendante du périmètre")+"</p>"
        cards.append(card(capability["name"],text,"cap-"+capability["id"]))
    body=note("<strong>Estimation complète du scénario, pas validation des capacités.</strong><p>"+esc(decision["scope_status"]["interpretation"])+"</p>")
    body+="<p><strong>Réserve de traçabilité :</strong> l'interface des états de reprise, de réconciliation et de purge suspendue reste à localiser précisément dans les travaux M1. Cette réserve ne démontre pas une omission ; elle empêche de déclarer la décomposition entièrement validée.</p>"
    body+='<div class="cards">'+"".join(cards)+"</div>"
    body+="<p>"+esc(decision["granularity"]["conclusion"])+"</p>"
    sections.append(section("famille","Six capacités et quatorze fonctions couvertes par le scénario",body))

    s=data["service_scenario"]
    body="<p>"+esc(s["status"])+"</p>"+prose(decision["assumptions_to_keep_visible"])
    context=s["inherited_context"]
    environment_labels=[("nominal_users","Utilisateurs nominatifs"),("simultaneous_users","Utilisateurs simultanés"),("availability_target_pct","Disponibilité mensuelle cible (%)"),("rpo_hours","Perte de données maximale cible (h)"),("rto_hours","Rétablissement cible (h)")]
    rows=["<tr><td>"+label+'</td><td class="num">'+number(context[key])+"</td></tr>" for key,label in environment_labels]
    rows.append("<tr><td>Environnements</td><td>"+esc(", ".join(context["environments"]))+"</td></tr>")
    body+=table(["Hypothèse de service","Valeur proposée"],rows,"Service S1 proposé pour comparer les estimations")
    load=s["qualification_load"]
    load_labels=[("active_objects","Objets actifs"),("active_links","Liens actifs"),("retained_versions","Versions conservées"),("reads_per_second","Lectures / seconde"),("contribution_peak_per_second","Contributions / seconde en pointe"),("peak_minutes","Durée de pointe (minutes)"),("full_batch_records","Enregistrements du lot complet"),("full_batch_target_minutes","Durée cible du lot complet (minutes)"),("p95_read_ms","Temps de réponse au 95e percentile cible (ms)"),("accepted_change_publication_target_minutes","Publication cible des changements acceptés (minutes)")]
    body+=table(["Qualification à réaliser","Hypothèse"],["<tr><td>"+label+'</td><td class="num">'+number(load[key])+"</td></tr>" for key,label in load_labels],"Volumes et objectifs de l'essai — aucune performance démontrée")
    body+="<p>"+esc(load["provenance"])+"</p>"
    for key,title in (("retention","Conservation"),("security","Sécurité"),("availability_limit","Limite de disponibilité"),("delivery","Livraison initiale")):
        body+=card(title,prose(s[key]))
    body+=note("<strong>Reprise : l'amendement v1.1 est une partie du contrat.</strong><p>Les versions stables, la nouvelle époque des curseurs, la redéclaration des usages et la suspension de purge demandent une qualification propre. Le retour du service ne signifie pas que tous les consommateurs ont été rapprochés.</p><p>"+ref_link("iteration-07-clarification-reprise.json","Clarification du scénario de reprise")+"</p>")
    sections.append(section("scenario","Les hypothèses et garanties qui changent le travail",body))

    diagnostic=data["range_diagnostic"]
    body=note("<strong>La confiance n'a pas progressé de manière démontrée.</strong><p>Classe C : ingénierie documentée sans calibration observée. Les enveloppes ne constituent pas des probabilités.</p>")
    body+="<p><strong>"+number(diagnostic["upper_ratio_150_175"])+" contributions sur "+number(diagnostic["contributions"])+"</strong> ont une borne haute entre 1,5 et 1,75 fois leur centre. "+esc(diagnostic["meaning"])+"</p>"
    body+=fields_block(decision["estimate_use"],["meaning_of_ranges"])
    for key in ("traceability_reserve","open_trace","open_traces","review_findings","traceability_open","remaining_trace"):
        if decision.get(key):
            body+=card("Traçabilité encore ouverte",prose(decision[key]))
        elif data.get(key):
            body+=card("Traçabilité encore ouverte",prose(data[key]))
    body+=note(
        "<strong>Charge de travail et délai calendaire sont deux grandeurs différentes.</strong>"
        "<p>Les JH additionnent le travail des personnes mobilisées. Ils ne donnent pas le temps écoulé entre le début et la fin du projet. Les centres de "
        +number(models["M1"]["total"][1])+" et "+number(models["M2"]["total"][1])+" JH sont deux hypothèses de charge d'ingénierie proposées par les agents IA : ce ne sont ni des sorties de COCOMO ni des observations de projets. Le code OSS étaye les travaux à prévoir, pas leur charge.</p>"
        "<p>Dans les analyses figées citées ici, « durées » désigne parfois les charges affectées aux travaux. Cela ne constitue pas une estimation du délai calendaire.</p>"
        "<p><strong>COCOMO II part d'une taille estimée du logiciel, en tenant compte de la réutilisation, et de facteurs du projet pour calculer un effort ; il estime ensuite un délai calendaire.</strong> Le facteur SCED peut augmenter l'effort lorsqu'un délai plus court que le délai nominal est imposé.</p>"
        "<p>Les coefficients publiés permettent d'utiliser le modèle sans bilans de projets locaux ; une calibration locale peut améliorer son adéquation. Le blocage de cette étude est l'absence d'une taille justifiable du contrat complet, pas une impossibilité générale d'utiliser COCOMO sans historique local. "
        +ref_link("https://www.rose-hulman.edu/class/cs/csse372/201310/Homework/CII_modelman2000.pdf","Manuel USC COCOMO II, sections 1.2, 2, 4 et 7")+".</p>"
    )
    body+="<h3>Ce que les méthodes permettent à cette étape</h3>"
    for key in ("engineering","COSMIC","COCOMO_II","ISBSG","triangulation"):
        if key in decision["methods"]:
            body+=card({"engineering":"Estimations d'ingénierie M1 et M2","COSMIC":"COSMIC : taille fonctionnelle partielle","COCOMO_II":"COCOMO II : entrée de taille manquante","ISBSG":"ISBSG : référence d'effort non établie","triangulation":"État de la confrontation des méthodes"}[key],"<p>"+esc(decision["methods"][key])+"</p>")
    cr=cosmic["result"]
    rows=[]
    for process in cosmic["processes"]:
        count=process["count"]
        rows.append("<tr><td>"+esc(process["label"])+"</td>"+''.join('<td class="num">'+number(count[k])+"</td>" for k in ("E","R","X","W","cfp"))+"</tr>")
    body+=table(["Consultation humaine","Entrées","Lectures","Sorties","Écritures","CFP"],rows,"Trois processus complets uniquement sous les hypothèses de restitution H01–H08")
    body+="<p><strong>"+number(cr["conditional_subset_cfp"])+" CFP conditionnels.</strong> "+esc(cr["interpretation"])+"</p><p>"+ref_link("iteration-07-cosmic.json","Hypothèses, mouvements et limites du comptage COSMIC")+"</p>"
    body+="<p>"+esc(cosmic["verdict"]["comparison_use"])+"</p>"
    sections.append(section("incertitude","Incertitude et limites de la comparaison",body))

    next_decision=decision["next_iteration"]
    body=note("<strong>"+esc(next_decision["recommendation"])+"</strong>")
    body+=prose(next_decision["useful_next_conditions"])
    body+="<p><strong>Priorité de la revue :</strong> "+esc(next_decision["priority"])+"</p>"
    body+="<p><strong>Critère de progrès :</strong> "+esc(next_decision["success"])+"</p>"
    body+="<p><strong>Condition d'arrêt :</strong> "+esc(next_decision["stop_condition"])+"</p>"
    body+="<p>"+esc(next_decision["can_progress_without_new_effort_data"])+"</p>"
    sections.append(section("suite","La prochaine étape utile",body))

    cards=[]
    role_labels={r["role"]:r["label"] for r in models["M1"]["by_role"]}
    for package in data["packages"]:
        rows=[]
        for role,effort in package["effort"].items():
            basis=package.get("central_basis",{}).get(role,"Justification dans le fichier M1.")
            rows.append("<tr><td>"+esc(role_labels.get(role,role))+"</td><td>"+triplet(effort)+"</td><td>"+esc(basis)+"</td></tr>")
        body='<p class="id">'+esc(package["id"])+" · "+esc(package["group"])+"</p>"
        body+=table(["Rôle","Bas / central / haut (JH)","Justification du centre"],rows,"M1 — "+package["label"])
        body+="<p><strong>Fonctions du contrat :</strong> "+esc(", ".join(package.get("contract_functions",[])) or "Moyens communs")+"</p>"
        body+="<p><strong>Preuves de mécanismes :</strong> "+" · ".join(ref_link(proof_links[pid],pid) for pid in package.get("proof_ids",[]))+"</p>"
        body+=prose(package.get("uncertainty",{}))
        cards.append(card(package["label"],body,"package-"+package["id"]))
    sections.append(section("travaux","Détail des travaux de M1",'<p>Ces charges de travail sont des hypothèses d’ingénierie. Les preuves de code renseignent les mécanismes ; elles ne mesurent pas les JH.</p><div class="cards">'+"".join(cards)+"</div><p>"+ref_link("iteration-07-m2.json","Plan macro et justifications indépendantes de M2")+"</p>"))

    artifact_links=[
      ("iteration-07-resultats.json","Résultats consolidés et contrôles de conservation"),
      ("iteration-07-contrat-v1.1.json","Contrat S1 v1.1"),
      ("iteration-07-exigence-delai.json","Sorties à conserver : charge, délai, équipe et incertitudes"),
      ("iteration-07-perimetre.json","Périmètre natif et frontières"),
      ("iteration-07-marche-preuves.json","Preuves de code des trois produits OSS"),
      ("iteration-07-spring-preuves.json","Patrimoine Spring et travaux résiduels"),
      ("iteration-07-m1.json","M1 figé : travaux et hypothèses de charge"),
      ("iteration-07-m2.json","M2 figé : estimation de comparaison par rôle"),
      ("iteration-07-decision.json","Décision et limites"),
      ("iteration-07-revue-perimetre.json","Revue documentaire indépendante"),
      ("iteration-07-revue-m1.json","Revue des hypothèses et des bornes de M1"),
      ("iteration-07-revue-ecarts-m2.json","Revue des écarts par l'auteur M2 après gel"),
      ("iteration-07-cosmic.json","Comptage COSMIC partiel"),
    ]
    body='<ul class="plain-list">'+"".join("<li>"+ref_link(file,label)+"</li>" for file,label in artifact_links)+"</ul>"
    body+="<h3>Documentation officielle consultée pour la réutilisation</h3>"
    rows=[]
    for item in spring["evidence"]:
        rows.append("<tr><td>"+ref_link(item["url"],item["id"])+"</td><td>"+esc(item["observed"])+"</td><td>"+esc(item["use"])+"</td></tr>")
    body+=table(["Référence officielle","Constat documentaire","Incidence sur le travail restant"],rows,"Documentation consultée — ni exécution du produit ni preuve de productivité")
    body+="<p>"+esc(spring["compatibility_limit"])+"</p>"
    body+=note("<strong>Les contrôles sont documentaires et arithmétiques.</strong><p>Ils vérifient les identifiants, les liens et la conservation des charges. Leur nombre ne mesure ni la précision des JH, ni la réalisation des garanties. Les sources actives restent inchangées.</p>")
    sections.append(section("sources","Preuves et traçabilité",body))
    nav_items=[("synthese","Résultat"),("progres","Progression et cumul"),("estimations","M1 et M2"),("roles","Neuf rôles"),("famille","Six capacités"),("scenario","Scénario S1"),("incertitude","Incertitude et méthodes"),("suite","Prochaine étape"),("travaux","Travaux détaillés"),("sources","Sources")]
    nav='<nav class="toc" aria-label="Sommaire du rapport"><strong>Dans ce rapport</strong>'+"".join('<a href="#'+key+'">'+esc(label)+"</a>" for key,label in nav_items)+"</nav>"
    result_hash=hashlib.sha256(result_path.read_bytes()).hexdigest()
    return '<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FLOW — Itération 07 : Références opérationnelles</title><style>'+STYLE+'</style></head><body><a class="skip" href="#main">Aller au contenu</a><header class="hero"><div class="eyebrow"><span class="marker" aria-hidden="true"></span>FLOW · Étude d’opportunité · Itération 07</div><h1>Références opérationnelles : un scénario complet, deux estimations</h1><p>Décrire l’investissement initial de cette famille et de ses moyens communs, par rôle. La comparaison progresse sur le périmètre ; elle ne fournit pas encore un montant suffisamment étayé pour être retenu.</p><p class="small muted">'+esc(data["date"])+' · JH bruts · Sources actives inchangées</p></header><div class="layout">'+nav+'<main id="main">'+"".join(sections)+'</main></div><footer><p>Rapport produit à partir des résultats et preuves figés. Aucun total du Core ni cumul automatique de contrats différents.</p><p class="checksum">Résultats : '+result_hash+'</p><p class="checksum">Contrat v1.1 : '+esc(data["contract_sha256"])+"</p></footer></body></html>\n"

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results",type=Path,default=HERE/"iteration-07-resultats.json")
    parser.add_argument("--output",type=Path,default=HERE/"iteration-07.html")
    args=parser.parse_args()
    if args.output.resolve().parent != HERE or not args.output.name.startswith("iteration-07"):
        raise ValueError("Seuls les artefacts de l'itération 07 peuvent être écrits dans cet audit.")
    data=json.loads(args.results.read_text(encoding="utf-8-sig"))
    args.output.write_text(render(data,args.results),encoding="utf-8")
    print(json.dumps({"output":str(args.output.resolve()),"new_estimate":False},ensure_ascii=True))

if __name__=="__main__":
    main()

