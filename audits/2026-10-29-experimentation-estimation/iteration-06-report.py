"""Render the documentary iteration-06 report, without changing its results.

Uses only the Python standard library. The input JSONs own every count,
estimate and decision. This script formats those data and checks display
invariants; it performs no effort estimation or budget allocation.
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
    "status": "Statut", "verdict": "Verdict", "reason": "Motif",
    "reasons": "Motifs", "meaning": "Interprétation", "next": "Décision suivante",
    "next_step": "Étape suivante", "next_gate": "Prochain jalon",
    "priority_decisions": "Décisions prioritaires", "priorities": "Priorités",
    "priority_choices": "Choix prioritaires", "conditions": "Conditions",
    "condition": "Condition", "limits": "Limites", "limitations": "Limites",
    "stop_condition": "Condition d'arrêt", "continuation": "Poursuite",
    "investigation_rule": "Règle d'investigation", "full_core_jh": "Effort complet du Core",
    "global_estimate_condition": "Condition d'une estimation globale",
    "question": "Question", "effort_effect": "Incidence possible sur le travail",
    "text": "Énoncé", "source": "Source", "origin": "Origine", "name": "Nom",
    "label": "Libellé", "description": "Description", "decision": "Décision",
    "id": "Identifiant", "result": "Résultat", "resultat": "Résultat",
    "passed": "Contrôle satisfait", "ok": "Contrôle satisfait",
    "details": "Détails", "count": "Nombre", "expected": "Attendu",
    "actual": "Constaté", "value": "Valeur", "basis": "Fondement",
    "source_refs": "Références", "detail_ref": "Analyse détaillée",
    "utilisateurs_nominatifs": "Utilisateurs nominatifs",
    "utilisateurs_simultanes_pointe": "Utilisateurs simultanés en pointe",
    "messages_metier_mois": "Messages métier par mois", "contrats_flux": "Contrats de flux",
    "applications_externes": "Applications externes", "latence_cible": "Latence cible",
    "fraicheur_cible": "Fraîcheur cible", "disponibilite_cible_pct": "Disponibilité cible (%)",
    "exploitation": "Exploitation", "support_humain": "Support humain",
    "perte_maximale_cible_heures": "Perte maximale cible (heures)",
    "retablissement_cible_heures": "Rétablissement cible (heures)",
    "exercices_restauration_annuels": "Exercices de restauration annuels",
    "production_scope": "Portée en production", "history_granularity": "Granularité historique",
    "clock_semantics": "Sens des dates", "isolation_cible": "Séparation cible des périmètres",
    "configuration_boundary": "Frontière de configuration",
    "external_delivery_guarantee": "Garantie d'effet externe",
    "donnees_actives_to": "Données actives (To logiques)",
    "donnees_archives_to": "Archives (To logiques)",
    "environnements_logiques": "Environnements logiques", "production": "Production",
    "recette": "Recette", "developpement": "Développement",
    "equipe_confirmee": "Équipe confirmée",
    "reference_effort_observe_disponible": "Référence d'effort observé disponible",
    "generic_core": "Core générique", "integration_or_external_authority": "Intégration et autorités externes",
    "scope": "Périmètre", "need": "Besoin", "financing": "Frontière de financement",
    "target": "Cible", "why": "Pourquoi ce choix", "steps": "Travaux prévus",
    "success": "Critère de réussite", "potential_progress": "Progrès possible, non promis",
    "stop_or_redirect": "Arrêt ou réorientation", "method_status": "Situation des méthodes",
}

METRIC_LABELS = {
    "inventory": "Capacités dans le périmètre",
    "framed": "Capacités cadrées : résultat, frontière, garanties et inconnues",
    "partial_comparative": "Cumul distinct des capacités comparées avec hypothèses de JH",
    "not_comparative": "Capacités sans étude comparative avec hypothèses de JH",
    "complete": "Capacités intégralement estimées",
    "reasonable": "Capacités complètes à l'incertitude jugée acceptable pour l'opportunité",
    "admitted_groups": "Estimations de groupe jugées suffisantes pour une décision d'investissement",
    "proposed_groups": "Ensembles proposés pour la future estimation",
    "local_conditional": "Ensembles localement estimables sous hypothèses",
    "prior_choice": "Ensembles avec choix structurant à borner",
    "guarantees": "Domaines de garanties documentés",
    "bounded_groups": "Groupes fonctionnels bornés avec hypothèses de JH",
    "roles": "Contributions par groupe et rôle dimensionnées",
}

METRIC_MEANINGS = {
    "inventory": "Inventaire natif stable.",
    "framed": "Nouvel indicateur : niveau précédent non mesuré. Il ne mesure ni comparaison de marché ni chiffrage complet.",
    "partial_comparative": "Toutes sont partielles. Ce nombre d'identifiants n'est pas le pourcentage des fonctions ou du coût couvert.",
    "not_comparative": "Le cadrage de cette itération ne remplace pas l'étude comparative.",
    "complete": "Aucune couverture intégrale de la portée native et de ses garanties n'est revendiquée.",
    "reasonable": "Aucune nouvelle admission ; une classe C seule n'accorde pas ce statut.",
    "admitted_groups": "Critère de décision de l'itération 05 conservé.",
    "proposed_groups": "Propositions analytiques ; la cartographie reste inchangée.",
    "local_conditional": "Avis de préparation ; dépendances communes, garanties et estimation restent à instruire.",
    "prior_choice": "Des variantes peuvent suffire ; ni architecture finale ni inventaire exhaustif des cas d'usage requis.",
    "guarantees": "Attentes documentaires, hypothèses et questions distinctes ; aucune validation contractuelle déduite.",
    "bounded_groups": "REF, STOCK, ORCH et PLAN dans leurs contrats partiels, avec deux lots communs séparés.",
    "roles": "Contributions antérieures toutes de classe C ; aucune nouvelle calibration.",
}

STATUS_LABELS = {
    "conditional": "Estimation sous hypothèses envisageable",
    "choice": "Choix structurant à borner",
    "cadree_documentairement": "Cadrée documentairement",
    "partielle_avec_hypotheses_JH": "Étude partielle avec hypothèses de JH",
    "non_etudiee_par_comparaison": "Sans étude comparative avec hypothèses de JH",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def number(value: object, signed: bool = False) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "Oui" if value else "Non"
    if isinstance(value, (int, float)):
        s = f"{value:,.3f}".rstrip("0").rstrip(".")
        s = s.replace(",", "\u202f").replace(".", ",")
        return ("+" if signed and value > 0 else "") + s
    return esc(value)


def prose(value: object) -> str:
    if value is None:
        return '<span class="muted">Non fixé / inconnu</span>'
    if isinstance(value, bool):
        return "Oui" if value else "Non"
    if isinstance(value, (int, float)):
        return number(value)
    if isinstance(value, str):
        return "<br>".join(esc(STATUS_LABELS.get(value, value)).splitlines())
    if isinstance(value, list):
        if not value:
            return '<span class="muted">Aucun élément renseigné</span>'
        return '<ul class="plain-list">' + "".join(f"<li>{prose(v)}</li>" for v in value) + "</ul>"
    if isinstance(value, dict):
        return '<dl class="data-list">' + "".join(
            f"<dt>{esc(LABELS.get(str(k), str(k).replace('_', ' ')))}</dt><dd>{prose(v)}</dd>"
            for k, v in value.items()
        ) + "</dl>"
    return esc(value)


def ref_link(ref: object, label: str = "Analyse détaillée") -> str:
    """Link to audit JSONs safely; do not expose raw source YAML downloads."""
    if isinstance(ref, dict):
        ref = ref.get("ref") or ref.get("path") or ref.get("url") or ref.get("detail_ref")
    if not isinstance(ref, str) or not ref:
        return '<span class="muted">Référence non renseignée</span>'
    if ref.split("#", 1)[0].lower().endswith((".yaml", ".yml")):
        return esc(label)
    if urlsplit(ref).scheme in ("http", "https"):
        target = ref
    elif urlsplit(ref).scheme or ref.startswith("//"):
        return esc(label)
    else:
        path, marker, fragment = ref.partition("#")
        if path.startswith(("audits/", "source/", "sources/", "app/")):
            path = os.path.relpath(ROOT / path, HERE).replace("\\", "/")
        target = quote(path, safe="/.-_") + ("#" + quote(fragment, safe="/.-_~") if marker else "")
    return f'<a href="{esc(target)}">{esc(label)}</a>'


def anchor(prefix: str, identifier: object) -> str:
    return prefix + "-" + quote(str(identifier), safe="-_.")


def table(headers: list[str], rows: list[str], caption: str, extra: str = "") -> str:
    return (
        f'<div class="table-wrap {extra}" tabindex="0" role="region" aria-label="{esc(caption)}">'
        f'<table><caption>{esc(caption)}</caption><thead><tr>'
        + "".join(f'<th scope="col">{esc(h)}</th>' for h in headers)
        + "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
    )


def section(identifier: str, title: str, body: str) -> str:
    return f'<section id="{esc(identifier)}"><h2>{esc(title)}</h2>{body}</section>'


def dependencies(value: object, caps: dict, groups: dict) -> str:
    items = value if isinstance(value, list) else [value]
    rows = []
    for item in items:
        identifier = item.get("id", "") if isinstance(item, dict) else str(item)
        if identifier in groups:
            label = f'<a href="#{esc(anchor("group", identifier))}">{esc(groups[identifier]["name"])}</a>'
        elif identifier in caps:
            label = f'<a href="#{esc(anchor("cap", identifier))}">{esc(caps[identifier]["name"])}</a>'
        else:
            label = esc(identifier)
        if isinstance(item, dict) and item.get("need"):
            label += " — " + esc(item["need"])
        rows.append("<li>" + label + "</li>")
    return '<ul class="plain-list">' + ''.join(rows) + '</ul>'


def unknowns(value: object) -> str:
    if isinstance(value, list):
        items = [v.get("question", v) if isinstance(v, dict) else v for v in value]
        return prose(items)
    return prose(value)


def decision_html(d: dict, caps: dict, groups: dict) -> str:
    body = '<div class="card decision"><h3>' + esc(d.get("verdict", "Décision à lire")) + '</h3>'
    for key in ("progress", "unchanged", "readiness_rule", "uncertainty_rule"):
        if d.get(key):
            body += '<p>' + prose(d[key]) + '</p>'
    body += '</div>'
    if d.get("next_iteration"):
        n = d["next_iteration"]
        body += '<h3 style="margin-top:1.7rem">Prochaine itération proposée</h3><div class="card">'
        for key in ("target", "why", "steps", "success", "potential_progress", "stop_or_redirect"):
            if key in n:
                body += '<p><strong>' + esc(LABELS[key]) + '</strong></p>' + prose(n[key])
        body += '<p><strong>Capacités concernées</strong></p>' + dependencies(n.get("scope_ids", []), caps, groups) + '</div>'
    if d.get("priorities"):
        body += '<h3 style="margin-top:1.7rem">Décisions prioritaires</h3><div class="cards">'
        for p in d["priorities"]:
            body += '<article class="card"><div class="id">' + esc(p["id"]) + '</div><h3>' + esc(p["title"]) + '</h3>'
            for key, label in (("question", "Question"), ("proposed_action", "Action proposée"), ("new_evidence", "Résultat attendu de l'investigation")):
                body += '<p><strong>' + label + '</strong><br>' + prose(p.get(key)) + '</p>'
            body += '<p><strong>Ensembles concernés</strong></p>' + dependencies(p.get("groups", []), caps, groups) + '</article>'
        body += '</div>'
    if d.get("dependency_resolutions"):
        rows = []
        for r in d["dependency_resolutions"]:
            rows.append('<tr><td><span class="id">' + esc(r["alias"]) + '</span><br>' + prose(r.get("status")) + '</td><td>' + dependencies(r.get("owners", []), caps, groups) + '</td><td><p>' + prose(r.get("meaning")) + '</p><p>' + prose(r.get("rule")) + '</p></td></tr>')
        body += '<h3 style="margin-top:1.7rem">Rattachement des mécanismes partagés</h3><p>' + prose(d.get("dependency_warning")) + '</p>'
        body += table(["Référence de dépendance", "Propriétaires proposés", "Sens et règle de financement"], rows, "Résolution des dépendances repérées, sans budgets supplémentaires")
    if d.get("examples_of_conditional_dependencies"):
        rows = []
        for e in d["examples_of_conditional_dependencies"]:
            rows.append('<tr><td>' + dependencies([e["group"]], caps, groups) + '</td><td>' + dependencies(e["depends_on"], caps, groups) + '</td><td>' + prose(e["meaning"]) + '</td></tr>')
        body += table(["Avis local conditionnel", "Choix ou moyens dont il dépend", "Conséquence"], rows, "Pourquoi un avis local favorable ne suffit pas à admettre l'estimation")
    body += '<h3>Situation des trois méthodes de référence</h3>' + prose(d.get("method_status"))
    return body


def validate(data: dict, registry: dict) -> None:
    required = ["metrics", "capabilities", "groups", "subdomains", "cumulative_comparative_ids",
                "previous_partial_jh", "full_core_jh", "decision", "checks"]
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError("Résultat incomplet : " + ", ".join(missing))
    caps, groups = data["capabilities"], data["groups"]
    ids = [c["id"] for c in caps]
    gids = {g["id"] for g in groups}
    if len(ids) != 88 or len(set(ids)) != 88:
        raise ValueError("L'itération06 doit contenir 88 capacités natives uniques.")
    if len(groups) != 38 or len(gids) != 38:
        raise ValueError("L'itération06 doit contenir 38 ensembles candidats uniques.")
    if any(c["group_id"] not in gids for c in caps):
        raise ValueError("Rattachement de capacité absent des ensembles.")
    membership = [cid for g in groups for cid in g["capability_ids"]]
    if sorted(membership) != sorted(ids):
        raise ValueError("Les appartenances doivent conserver chacune des 88 capacités une fois.")
    studied = data["cumulative_comparative_ids"]
    if len(studied) != 16 or len(set(studied)) != 16 or not set(studied) <= set(ids):
        raise ValueError("Le cadrage06 ne doit pas promouvoir le compteur comparatif au-delà des 16 capacités partielles.")
    if data["full_core_jh"] is not None:
        raise ValueError("Le Core complet reste non estimé dans cette itération documentaire.")
    if any(c["full_estimate_jh"] is not None or c["opportunity_admitted"] is not False for c in caps):
        raise ValueError("Aucune capacité complète ni admission économique nouvelle ne peut être déclarée ici.")
    if len(registry.get("areas", [])) != 12:
        raise ValueError("Le registre doit contenir les 12 domaines de garantie.")


STYLE = """
:root{--green:#236159;--mint:#D9F2EA;--ivory:#FAF8F4;--ink:#182632;--muted:#45525A;--orange:#FF7A1A;--peach:#FFF0DB;--line:#CBD7D2;--head:#F4F8F6;--lavender:#F4F5FB}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:1.5rem}body{margin:0;background:var(--ivory);color:var(--ink);font-family:Aptos,"Segoe UI",Arial,sans-serif;font-size:16px;line-height:1.55}a{color:var(--green);text-underline-offset:3px}a:hover{color:#16443d}a:focus-visible,[tabindex]:focus-visible{outline:3px solid var(--green);outline-offset:4px}p{margin:.65rem 0 1rem}h1,h2,h3{font-family:"Aptos Display",Aptos,"Segoe UI",Arial,sans-serif;line-height:1.2}h1{font-size:clamp(2rem,4vw,3rem);max-width:24ch;margin:.55rem 0 1rem}h2{font-size:1.7rem;margin:0 0 1.2rem}h3{font-size:1.15rem;margin:0 0 .7rem}small,.small{font-size:.82rem}.muted{color:var(--muted)}.eyebrow{text-transform:uppercase;letter-spacing:.08em;font-size:.8rem;font-weight:700}.skip{position:absolute;left:1rem;top:-10rem;background:white;padding:.75rem}.skip:focus{top:1rem;z-index:5}.hero{background:var(--mint);border-top:7px solid var(--green);padding:2.5rem max(2rem,calc((100vw - 1320px)/2)) 2.5rem}.hero p{max-width:85ch}.marker{display:inline-block;width:.55rem;height:.55rem;background:var(--orange);border-radius:50%;margin-right:.5rem}.layout{display:grid;grid-template-columns:190px minmax(0,1fr);gap:2.5rem;max-width:1440px;margin:auto;padding:2.4rem 2rem 5rem}.toc{position:sticky;top:1rem;align-self:start;font-size:.9rem}.toc strong{display:block;margin-bottom:.6rem}.toc a{display:block;padding:.45rem .65rem;border-left:2px solid var(--line);text-decoration:none}.toc a:hover{background:var(--mint);border-left-color:var(--green)}main{min-width:0}section{margin-bottom:3rem;scroll-margin-top:1rem}section+section{padding-top:1.6rem;border-top:1px solid var(--line)}.note{padding:1rem 1.2rem;border-left:4px solid var(--orange);background:var(--peach);margin:1rem 0 1.5rem}.note p:last-child{margin-bottom:0}.table-wrap{overflow:auto;margin:1rem 0 1.8rem;border:1px solid var(--line);border-radius:4px;background:#fff}table{border-collapse:collapse;width:100%;font-size:.9rem;text-align:left}caption{text-align:left;padding:.85rem 1rem;background:#fff;font-size:.9rem;color:var(--muted)}th{background:var(--head);font-size:.78rem;font-weight:650;vertical-align:bottom;color:var(--ink)}td,th{padding:.8rem .85rem;border-bottom:1px solid var(--line);vertical-align:top}tbody tr:last-child td{border-bottom:0}td p{margin:0 0 .55rem}td p:last-child{margin-bottom:0}td.num{white-space:nowrap;font-variant-numeric:tabular-nums;font-weight:650}.id{font-size:.76rem;color:var(--muted);overflow-wrap:anywhere}.tag{display:inline-block;padding:.15rem .45rem;background:var(--lavender);border-radius:3px;font-size:.77rem;line-height:1.4;margin:.2rem 0}.plain-list{padding-left:1.15rem;margin:.25rem 0 .65rem}.plain-list li+li{margin-top:.3rem}.data-list{display:grid;grid-template-columns:minmax(140px,1fr) 3fr;column-gap:1rem;row-gap:.45rem;margin:.4rem 0 1rem}.data-list dt{font-weight:650;font-size:.88rem}.data-list dd{margin:0}.data-list .data-list{display:block;margin:0}.data-list .data-list dt{margin:.3rem 0}.cards{display:grid;gap:1rem}.card{background:white;border:1px solid var(--line);border-top:3px solid var(--green);padding:1.3rem}.card .columns{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem}.compact p{margin:.3rem 0 .6rem}.wide-cap td:first-child{min-width:190px}.wide-cap td:nth-child(3){min-width:260px}.wide-cap td:nth-child(4){min-width:220px}.report-source{overflow-wrap:anywhere}footer{max-width:1320px;margin:auto;padding:0 2rem 3rem;font-size:.82rem;color:var(--muted)}.checksum{font-size:.7rem;overflow-wrap:anywhere}.decision{background:var(--peach);border-top-color:var(--orange)}
@media(max-width:1000px){.layout{grid-template-columns:1fr;padding:1.5rem 1rem}.toc{position:static;display:flex;flex-wrap:wrap;gap:.2rem}.toc strong{width:100%}.toc a{border:0;padding:.35rem .55rem}.hero{padding:2rem 1.2rem}.card .columns{grid-template-columns:1fr;gap:0}.data-list{grid-template-columns:1fr}.data-list dd{margin-bottom:.5rem}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{body{background:white;font-size:10pt}.hero{padding:1cm 0;background:white;border-top-width:3px}.layout{display:block;padding:0}.toc,.skip{display:none}h1{font-size:25pt}h2{font-size:18pt}section{break-before:auto}.card{break-inside:avoid;border-top-width:2px}.table-wrap{overflow:visible;border:0}table{font-size:8pt}thead{display:table-header-group}tr{break-inside:avoid}td,th{padding:5pt}a{color:var(--ink)}footer{padding:0}.wide-cap td{min-width:0!important}.note{background:white;border:1px solid var(--line);border-left:3px solid var(--orange)}}
"""


def render(data: dict, registry: dict, result_path: Path, registry_path: Path) -> str:
    caps = {c["id"]: c for c in data["capabilities"]}
    groups = {g["id"]: g for g in data["groups"]}
    sections = []
    rows = []
    for m in data["metrics"]:
        denominator = m.get("denominator")
        current = number(m.get("current"))
        if denominator is not None:
            current += " / " + number(denominator)
        rows.append(f'<tr><td><strong>{esc(METRIC_LABELS.get(m["id"], m["label"]))}</strong></td><td class="num">{number(m.get("previous"))}</td><td class="num">{current}</td><td class="num">{number(m.get("delta"), True)}</td><td>{prose(METRIC_MEANINGS.get(m["id"], m.get("meaning")))}</td></tr>')
    sections.append(section("progres", "Ce que cette itération fait progresser",
        '<p>Le cadrage fonctionnel décrit les résultats, frontières et garanties à instruire. Une étude comparative partielle examine un périmètre borné ; elle ne chiffre pas toute la capacité.</p>'
        + table(["Indicateur", "Avant", "À cette étape", "Variation", "Portée de l'indicateur"], rows, "Compteurs distincts de progression")
        + '<div class="note"><strong>Le Core complet reste non estimé.</strong><p>Le classement documentaire ne crée aucune charge et ne démontre pas qu’un chiffrage complet soit suffisamment solide pour la décision d’opportunité.</p></div>'))
    rows = []
    for s in data["subdomains"]:
        rows.append('<tr><td><strong>' + esc(s["name"]) + '</strong><br><span class="id">' + esc(s["id"]) + '</span></td>' + ''.join(f'<td class="num">{number(s[k])}</td>' for k in ["total", "framed", "partial_comparative", "full_estimate", "opportunity_admitted"]) + '</tr>')
    totals = {key: sum(s[key] for s in data["subdomains"]) for key in ("total", "framed", "partial_comparative", "full_estimate", "opportunity_admitted")}
    rows.append('<tr class="total-row"><th scope="row">Total des capacités distinctes</th>' + ''.join(f'<td class="num">{number(totals[key])}</td>' for key in totals) + '</tr>')
    sections.append(section("perimetre", "Cumul par sous-domaine",
        table(["Sous-domaine", "Capacités", "Cadrées", "Comparées et partiellement estimées", "Entièrement estimées", "Incertitude acceptable pour l’opportunité"], rows, "Couverture native — chaque capacité compte une seule fois")
        + '<p class="muted">Les rattachements secondaires et les dépendances ne créent pas une deuxième capacité. Les garanties transverses restent visibles séparément.</p>'))
    rows = []
    for cid in data["cumulative_comparative_ids"]:
        c = caps[cid]
        path_names = c.get("path_names", [])
        parent = path_names[1] if isinstance(path_names, list) and len(path_names) > 1 else ""
        refs = c.get("prior_financing_refs") or []
        refs_html = prose(refs)
        rows.append(f'<tr><td><a href="#{esc(anchor("cap",cid))}">{esc(c["name"])}</a><br><span class="id">{esc(cid)}</span></td><td>{esc(parent)}</td><td>{prose(c.get("comparative_status"))}</td><td class="report-source">{refs_html}</td></tr>')
    previous = data["previous_partial_jh"]
    effort = table(["Bas", "Central", "Haut"], ["<tr>" + "".join(f'<td class="num">{number(previous[k])} JH</td>' for k in ("low", "central", "high")) + "</tr>"], "Charges brutes conservées du panier partiel — tous rôles")
    sections.append(section("comparaisons", "Les 16 capacités déjà étudiées sur un périmètre partiel",
        table(["Capacité native", "Sous-domaine", "Portée comparative", "Financements antérieurs"], rows, "Liste nominative cumulée, sans extension de couverture")
        + '<h3>Effort conservé du panier partiel</h3>' + prose(previous.get("meaning")) + effort
        + '<p class="muted">Les bornes décrivent une sensibilité au travail nécessaire à périmètre constant. Ce ne sont pas des percentiles et elles ne permettent pas d’extrapoler un coût par capacité.</p>'))
    cards = []
    for g in data["groups"]:
        members = ' · '.join(f'<a href="#{esc(anchor("cap",cid))}">{esc(caps[cid]["name"])}</a>' for cid in g["capability_ids"])
        cards.append(f'<article class="card compact" id="{esc(anchor("group",g["id"]))}"><div class="id">{esc(g["id"])}</div><h3>{esc(g["name"])}</h3><p>{prose(g.get("result"))}</p><div class="columns"><div><p><strong>Avis local de préparation</strong></p>{prose(g.get("local_readiness"))}<p><strong>Conditions et choix</strong></p>{prose(g.get("condition"))}</div><div><p><strong>Dépendances</strong></p>{dependencies(g.get("dependencies", []), caps, groups)}</div></div><p><strong>Capacités rattachées</strong> — {members}</p><p>{ref_link(g.get("detail_ref"))}</p></article>')
    sections.append(section("ensembles", "38 ensembles candidats et leurs conditions",
        '<div class="note"><strong>Un avis local conditionnel ne suffit pas à autoriser une estimation complète.</strong><p>Les dépendances peuvent porter des choix encore ouverts. Les ensembles organisent les travaux à instruire ; ils ne prescrivent pas une architecture finale, une équipe distincte ou un nouveau budget par groupe.</p></div>'
        + '<div class="cards">' + ''.join(cards) + '</div>'))
    cards = []
    for a in registry["areas"]:
        cards.append(f'<article class="card" id="{esc(anchor("garantie",a["id"]))}"><div class="id">{esc(a["id"])}</div><h3>{esc(a["label"])}</h3><p class="muted"><strong>Origine :</strong> {esc(a["origin"])}</p><div class="columns"><div><p><strong>Éléments disponibles, selon cette qualification</strong></p>{prose(a.get("known"))}<p><strong>Garantie à cadrer</strong></p>{prose(a.get("expected"))}</div><div><p><strong>Questions ouvertes</strong></p>{prose(a.get("open"))}<p><strong>Incidence possible</strong></p>{prose(a.get("impact"))}</div></div><p><strong>Prochaine décision :</strong> {prose(a.get("next"))}</p><p class="small"><strong>Propriétaire technique proposé :</strong> {esc(a.get("owner"))}</p></article>')
    owners = []
    for o in registry.get("technical_work_owners", []):
        owners.append(f'<tr><td><strong>{esc(o["label"])}</strong><br><span class="id">{esc(o["id"])}</span></td><td>{prose(o.get("scope"))}</td><td>{prose(o.get("rule"))}</td></tr>')
    sections.append(section("garanties", "12 domaines de garantie à qualifier",
        '<div class="note">' + prose(registry.get("status")) + '<p>' + prose(registry.get("quantification_rule")) + '</p></div>'
        + '<div class="cards">' + ''.join(cards) + '</div><h3 style="margin-top:1.7rem">Propriétaires des moyens communs</h3>'
        + '<p>' + prose(registry.get("funding_status")) + '</p>'
        + table(["Propriétaire proposé", "Travaux partagés", "Frontière de financement"], owners, "Responsabilités techniques proposées, sans budget nouveau")))
    sections.append(section("decisions", "Décisions de poursuite et priorités",
        decision_html(data["decision"], caps, groups)))
    rows = []
    for c in data["capabilities"]:
        path = c.get("path_names") or c.get("path") or []
        path_text = ' › '.join(str(p) for p in path) if isinstance(path, list) else str(path)
        gid = c["group_id"]
        rows.append(f'<tr id="{esc(anchor("cap",c["id"]))}"><td><strong>{esc(c["name"])}</strong><br><span class="id">{esc(c.get("block", ""))} · {esc(c["id"])}</span><p class="small muted">{esc(path_text)}</p><p>{ref_link(c.get("detail_ref"))}</p></td><td><a href="#{esc(anchor("group",gid))}">{esc(groups[gid]["name"])}</a><br><span class="id">{esc(gid)}</span><p><strong>Cadrage</strong><br>{prose(c.get("framing_status"))}</p><p><strong>Étude comparative</strong><br>{prose(c.get("comparative_status"))}</p></td><td><p><strong>Résultat générique</strong><br>{prose(c.get("result"))}</p><p><strong>Frontière</strong><br>{prose(c.get("boundary"))}</p><p><strong>Fonctions documentées</strong></p>{prose(c.get("functions"))}</td><td><p><strong>Inconnues pouvant changer le travail</strong></p>{unknowns(c.get("unknowns"))}<p><strong>Décision suivante</strong><br>{prose(c.get("next_decision"))}</p></td></tr>')
    sections.append(section("capacites", "Les 88 capacités et leur analyse de périmètre",
        '<p>Chaque ligne conserve le rattachement natif, le résultat générique, la frontière et la prochaine décision. Les analyses détaillées distinguent garanties déduites des sources et hypothèses proposées.</p><p><strong>Pour chacune des 88 capacités : estimation du périmètre entier inconnue ; aucun chiffrage complet jugé suffisant pour l’opportunité.</strong></p>'
        + table(["Capacité et rattachement natif", "Ensemble et états distincts", "Résultat, frontière et fonctions", "Incertitude et décision"], rows, "Inventaire exhaustif de cadrage fonctionnel, sans chiffrage supplémentaire", "wide-cap")))
    failed_checks = [c for c in data["checks"] if c.get("passed") is not True]
    check_summary = '<p><strong>' + number(len(data["checks"]) - len(failed_checks)) + ' contrôles satisfaits sur ' + number(len(data["checks"])) + '.</strong> La liste complète reste dans les résultats consolidés.</p>'
    if failed_checks:
        check_summary += '<div class="note"><strong>Contrôles à résoudre</strong>' + prose(failed_checks) + '</div>'
    sections.append(section("controles", "Contrôles documentaires et traçabilité",
        '<p>Ces contrôles vérifient les identifiants, rattachements et conservations de données. Ils ne valident pas la précision des estimations ni la réalisation des garanties.</p>'
        + check_summary + '<p>' + ref_link(result_path.name, "Résultats consolidés JSON") + ' · ' + ref_link(registry_path.name, "Registre des garanties JSON") + '</p>'))
    nav_items = [("progres", "Progression"), ("perimetre", "Sous-domaines"), ("comparaisons", "16 capacités comparées"), ("ensembles", "38 ensembles candidats"), ("garanties", "12 garanties"), ("decisions", "Décisions prioritaires"), ("capacites", "88 capacités"), ("controles", "Contrôles et sources")]
    nav = '<nav class="toc" aria-label="Sommaire du rapport"><strong>Dans ce rapport</strong>' + ''.join(f'<a href="#{key}">{esc(label)}</a>' for key, label in nav_items) + '</nav>'
    hashes = ' · '.join(f'{esc(p.name)} : {hashlib.sha256(p.read_bytes()).hexdigest()}' for p in (result_path, registry_path))
    return '<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FLOW — Itération 06 : périmètre et garanties</title><style>' + STYLE + '</style></head><body><a class="skip" href="#main">Aller au contenu</a><header class="hero"><div class="eyebrow"><span class="marker" aria-hidden="true"></span>FLOW · Étude d’opportunité · Itération 06</div><h1>Du périmètre métier aux travaux à estimer</h1><p>Relier les capacités aux résultats attendus, aux garanties et aux dépendances permet de préparer une estimation globale du Core. Cette étape est un cadrage fonctionnel ; elle ne transforme pas les pilotes en estimation du produit complet.</p><p class="small muted">' + esc(data.get("date", "")) + ' · Rapport continu · Aucun nouveau JH</p></header><div class="layout">' + nav + '<main id="main">' + ''.join(sections) + '</main></div><footer><p>Rapport généré uniquement à partir des résultats consolidés et du registre de garanties. Sources et estimations figées inchangées.</p><p class="checksum">Empreintes des entrées : ' + hashes + '</p></footer></body></html>\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=HERE / "iteration-06-resultats.json")
    parser.add_argument("--guarantees", type=Path, default=HERE / "iteration-06-garanties.json")
    parser.add_argument("--output", type=Path, default=HERE / "iteration-06.html")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.parent != HERE:
        raise ValueError("Le générateur écrit uniquement dans le dossier de cet audit.")
    data = json.loads(args.results.read_text(encoding="utf-8-sig"))
    registry = json.loads(args.guarantees.read_text(encoding="utf-8-sig"))
    validate(data, registry)
    output.write_text(render(data, registry, args.results, args.guarantees), encoding="utf-8")
    print(json.dumps({"output": str(output), "capabilities": len(data["capabilities"]),
                      "groups": len(data["groups"]), "comparative_partial": len(data["cumulative_comparative_ids"]),
                      "guarantee_areas": len(registry["areas"]), "new_jh": False}, ensure_ascii=True))


if __name__ == "__main__":
    main()
