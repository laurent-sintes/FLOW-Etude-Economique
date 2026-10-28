"""Reproduce the FLOW market study's source-code size proxy.

Read-only audit of pinned upstream checkouts. The figures are physical
nonblank, noncomment lines (PNCLOC), not COCOMO logical source statements.
"""

from __future__ import annotations

import argparse
import io
import json
import subprocess
import tokenize
from functools import lru_cache
from pathlib import Path


COMMITS = {
    "frappe": "2fcb9397a1f1da353b21e53d2f97ec56653acd02",
    "erpnext": "ade850bbd6a7412e9994a9637d2c5c713771632a",
    "insights": "c7dc954d8275756deb5ad24f7c35c3f3c2ca1a6c",
}
EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".vue"}
ERP_MODULES = {
    "stock", "buying", "selling", "support", "quality_management",
    "subcontracting", "maintenance", "utilities",
}
ERP_CONTROLLERS = {
    "stock_controller.py", "subcontracting_controller.py",
    "buying_controller.py", "sales_and_purchase_return.py",
    "selling_controller.py", "subcontracting_inward_controller.py",
    "status_updater.py", "queries.py", "mapper.py",
}
FRAPPE_EXCLUDED_MODULES = {
    "website", "printing", "mcp", "contacts", "geo", "pulse", "www",
}


def tracked_files(repo: Path) -> list[str]:
    head = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()
    if head != COMMITS[repo.name]:
        raise ValueError(f"{repo.name}: expected {COMMITS[repo.name]}, got {head}")
    raw = subprocess.check_output(["git", "-C", str(repo), "ls-files", "-z"])
    return [p.decode("utf-8") for p in raw.split(b"\0") if p]


def is_source(path: str) -> bool:
    p = Path(path)
    parts = p.parts
    name = p.name.lower()
    if p.suffix.lower() not in EXTENSIONS:
        return False
    if any(part.lower() in {"tests", "test", "patches", "fixtures", "node_modules"} for part in parts):
        return False
    if name.startswith("test_") or name.endswith((".test.js", ".test.ts", ".spec.js", ".spec.ts", ".spec.tsx")):
        return False
    return True


def frappe_scope(path: str, wide: bool = False) -> bool:
    parts = Path(path).parts
    if not parts or parts[0] not in {"frappe", "ui", "realtime"}:
        return False
    if parts[0] == "frappe":
        if len(parts) > 1 and parts[1] == "public" and not path.startswith("frappe/public/js/frappe/"):
            return False
        if not wide and len(parts) > 1 and parts[1] in FRAPPE_EXCLUDED_MODULES:
            return False
    return True


def erp_scope(path: str, manufacturing: str = "none") -> bool:
    parts = Path(path).parts
    if len(parts) < 3 or parts[0] != "erpnext":
        return False
    if parts[1] in ERP_MODULES:
        return True
    if parts[1] == "controllers" and len(parts) == 3 and parts[2] in ERP_CONTROLLERS:
        return True
    if parts[1] == "manufacturing":
        if manufacturing == "all":
            return True
        if manufacturing == "planning":
            return any(f"/{slug}/" in path for slug in (
                "bom", "production_plan", "master_production_schedule",
                "workstation", "manufacturing_settings",
                "material_requirements_planning_report",
            ))
        if manufacturing == "execution":
            return any(f"/{slug}/" in path for slug in (
                "bom", "production_plan", "master_production_schedule",
                "workstation", "manufacturing_settings",
                "material_requirements_planning_report", "work_order", "job_card",
            ))
    return False


def insights_scope(path: str) -> bool:
    if path.startswith("insights/"):
        return "/migrator/" not in path
    if path.startswith("frontend/src2/"):
        return "/migration/" not in path
    return False


def automation_flow_scope(path: str) -> bool:
    if path.startswith("frappe/automation_engine/"):
        return True
    return path.startswith("frappe/automation/doctype/automation_")


def strip_python_comments(source: str) -> str:
    lines = source.splitlines(keepends=True)
    chars = [list(line) for line in lines]
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for token in tokens:
            if token.type == tokenize.COMMENT:
                row, start = token.start
                _, end = token.end
                for index in range(start, end):
                    chars[row - 1][index] = " "
    except (tokenize.TokenError, IndentationError) as exc:
        raise ValueError(f"cannot tokenize Python source: {exc}") from exc
    return "".join("".join(line) for line in chars)


def strip_js_comments(source: str) -> str:
    out: list[str] = []
    state = "code"
    i = 0
    while i < len(source):
        ch = source[i]
        following = source[i:i + 4]
        two = following[:2]
        if state == "code":
            if following == "<!--":
                state = "html_comment"
                out.extend("    ")
                i += 4
                continue
            if two == "//":
                state = "line_comment"
                out.extend("  ")
                i += 2
                continue
            if two == "/*":
                state = "block_comment"
                out.extend("  ")
                i += 2
                continue
            if ch in {"'", '"', "`"}:
                state = ch
            out.append(ch)
        elif state in {"'", '"', "`"}:
            out.append(ch)
            if ch == "\\" and i + 1 < len(source):
                i += 1
                out.append(source[i])
            elif ch == state:
                state = "code"
        elif state == "line_comment":
            if ch == "\n":
                state = "code"
                out.append(ch)
            else:
                out.append(" ")
        elif state == "block_comment":
            if two == "*/":
                state = "code"
                out.extend("  ")
                i += 2
                continue
            out.append("\n" if ch == "\n" else " ")
        elif state == "html_comment":
            if source[i:i + 3] == "-->":
                state = "code"
                out.extend("   ")
                i += 3
                continue
            out.append("\n" if ch == "\n" else " ")
        i += 1
    return "".join(out)


@lru_cache(maxsize=None)
def count_file(path: Path) -> int:
    source = path.read_text(encoding="utf-8-sig", errors="replace")
    without_comments = strip_python_comments(source) if path.suffix.lower() == ".py" else strip_js_comments(source)
    return sum(bool(line.strip()) for line in without_comments.splitlines())


def measure(repo: Path, selected: list[str]) -> dict[str, int]:
    return {
        "files": len(selected),
        "bytes": sum((repo / path).stat().st_size for path in selected),
        "pncloc": sum(count_file(repo / path) for path in selected),
    }


def cocomo_proxy_jh(lines: int) -> float:
    """COCOMO II nominal coefficient on PNCLOC, *not* standard logical SLOC."""
    return 2.94 * (lines / 1000) ** 1.0997 * 152 / 7


def run(root: Path) -> dict[str, object]:
    files = {name: [p for p in tracked_files(root / name) if is_source(p)] for name in COMMITS}
    frappe = root / "frappe"
    erpnext = root / "erpnext"
    insights = root / "insights"
    result = {
        "commits": COMMITS,
        "frappe_retenu": measure(frappe, [p for p in files["frappe"] if frappe_scope(p)]),
        "frappe_elargi": measure(frappe, [p for p in files["frappe"] if frappe_scope(p, wide=True)]),
        "automation_flow_dans_frappe": measure(frappe, [p for p in files["frappe"] if automation_flow_scope(p)]),
        "erp_sans_fabrication": measure(erpnext, [p for p in files["erpnext"] if erp_scope(p)]),
        "erp_planification": measure(erpnext, [p for p in files["erpnext"] if erp_scope(p, "planning")]),
        "erp_execution": measure(erpnext, [p for p in files["erpnext"] if erp_scope(p, "execution")]),
        "erp_fabrication_entiere": measure(erpnext, [p for p in files["erpnext"] if erp_scope(p, "all")]),
        "insights_serveur_v3": measure(insights, [p for p in files["insights"] if insights_scope(p) and p.startswith("insights/")]),
        "insights_interface_v3": measure(insights, [p for p in files["insights"] if insights_scope(p) and p.startswith("frontend/src2/")]),
        "insights_v3": measure(insights, [p for p in files["insights"] if insights_scope(p)]),
    }
    selection = {
        "frappe": "frappe_retenu",
        "erpnext": "erp_execution",
        "insights": "insights_v3",
    }
    sizes = [result[key]["pncloc"] for key in selection.values()]
    exact_jh = sum(cocomo_proxy_jh(size) for size in sizes)
    result["calcul_cocomo"] = {
        "selection": selection,
        "pncloc_total": sum(sizes),
        "mois_personne": round(exact_jh * 7 / 152, 2),
        "jh": round(exact_jh),
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Directory containing frappe/, erpnext/, insights/ checkouts")
    args = parser.parse_args()
    print(json.dumps(run(args.root.resolve()), indent=2, ensure_ascii=False))
