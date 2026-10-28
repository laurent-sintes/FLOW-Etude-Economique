"""Measure pinned public ERP source selections for the FLOW market study.

This is a physical source-size inventory, not a functional-size measure or an
estimate of historical development effort. XML and Python module manifests
are reported separately from executable-source PNCLOC.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

from oss_flow_code_audit import strip_js_comments, strip_python_comments


CODE_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".vue", ".java", ".groovy"}
DECLARATIVE_EXTENSIONS = {".xml", ".csv"}
EXCLUDED_PARTS = {
    "test", "tests", "__tests__", "testing", "testdata", "fixtures", "fixture", "doc", "docs",
    "locale", "locales", "i18n", "node_modules", "vendor", "third_party",
    "build", "dist", "target", "generated", "gen", "patches", "migrations",
    "demo", "demos", "examples", "samples",
}
TEST_NAME = re.compile(r"(^tests?_|_test\.|[.]test[.]|[.]spec[.]|[.]min[.]|^demo_|_demo\.|^demo\.)", re.I)

ODOO_COMMIT = "299075f17026b830a9755f3c43f3e83143995946"
ODOO_SPREADSHEET_COMMIT = "a3fe2e1792d3159d11a14536c90d58a5affa2013"
ODOO_SHARED_BUSINESS = "product uom resource".split()
ODOO_OPERATIONS = """
    stock purchase purchase_stock purchase_requisition sale sale_management
    sale_stock mrp repair mrp_repair
""".split()
ODOO_AUTOMATION = "base_automation".split()
ODOO_ANALYTICS = "spreadsheet spreadsheet_dashboard spreadsheet_dashboard_sale".split()
ODOO_FINANCE_DIRECT = "account account_payment stock_account".split()

TRYTON_COMMIT = "e011222dc305c431677e586706fd241dffe02236"
TRYTON_MODULES = """
    company currency country party product stock purchase sale production stock_supply
    stock_supply_production stock_forecast stock_supply_forecast purchase_request
    purchase_request_quotation sale_stock_quantity sale_supply sale_supply_production
    sale_complaint stock_lot stock_assign_manual quality production_routing
    production_work dashboard
""".split()
TRYTON_FINANCE_DIRECT = "account account_invoice account_invoice_stock account_product".split()

AXELOR_SUITE_COMMIT = "e7cbea53bae88d2540f59a70b09bf0f326f1022e"
AXELOR_PLATFORM_COMMIT = "96caf51eb97fbab7750b7dadf10a371a55a490a3"
AXELOR_WEBAPP_COMMIT = "dc50bc5a5c4006c607579bafa18c48564a951d6e"
AXELOR_STUDIO_COMMIT = "06d8c6dffa1f78a72009b560be53ba6e7b4047be"
AXELOR_UTILS_COMMIT = "69ce513f37a06a23fa3724a1f3f40a473034b02a"
AXELOR_MESSAGE_COMMIT = "9046cf975a5db9fb45da9c5bb5066d4327cd6435"
AXELOR_SUITE_MODULES = """
    axelor-base axelor-purchase axelor-sale axelor-stock axelor-supplychain
    axelor-production axelor-quality axelor-intervention axelor-helpdesk
""".split()
AXELOR_MAINTENANCE_OUTSIDE_FLOW = "axelor-maintenance"
AXELOR_DEPENDENCIES = """
    axelor-account axelor-crm axelor-contract axelor-human-resource
    axelor-project axelor-bank-payment
""".split()
AXELOR_PLATFORM_MODULES = """
    axelor-common axelor-core axelor-web axelor-tomcat
""".split()
AXELOR_STUDIO_FRONTENDS = """
    bpm bpm-merge-split generic-builder mapper studio timer-builder
    webservices-builder
""".split()


def git_head(repo: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()


def tracked_paths(repo: Path) -> list[str]:
    raw = subprocess.check_output(["git", "-C", str(repo), "ls-files", "-z"])
    return [value.decode("utf-8") for value in raw.split(b"\0") if value]


def selected_type(path: str) -> str | None:
    parts = [part.lower() for part in Path(path).parts]
    name = parts[-1]
    if any(part in EXCLUDED_PARTS or part.startswith(("test_", "tests_")) for part in parts) or "/static/lib/" in path or "/static/libs/" in path:
        return None
    if path.startswith("odoo/upgrade_code/") or path in {
        "addons/spreadsheet/static/src/o_spreadsheet/o_spreadsheet.js",
        "addons/web/static/src/core/emoji_picker/emoji_data.js",
        "addons/web/icons.py",
    }:
        return None
    if TEST_NAME.search(name) or name.startswith("test") and name.endswith(".java"):
        return None
    if name == "__manifest__.py":
        return "manifest"
    suffix = Path(name).suffix
    if suffix in CODE_EXTENSIONS:
        return "code"
    if suffix in DECLARATIVE_EXTENSIONS:
        return suffix[1:]
    return None


def stripped_lines(source: str, kind: str, suffix: str) -> int:
    if kind == "xml":
        cleaned = re.sub(
            r"<!--.*?-->",
            lambda match: "".join("\n" if char == "\n" else " " for char in match.group()),
            source,
            flags=re.S,
        )
    elif kind == "csv":
        cleaned = source
    elif suffix == ".py":
        cleaned = strip_python_comments(source)
    else:
        # The same lexical proxy as the pinned Frappe/ERPNext audit. It is not
        # a Java/Groovy parser and cannot normalize language density.
        cleaned = strip_js_comments(source)
    return sum(bool(line.strip()) for line in cleaned.splitlines())


def measure(repo: Path, paths: list[str]) -> dict[str, object]:
    by_kind: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "bytes": 0, "lines": 0})
    by_extension: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "bytes": 0, "lines": 0})
    used: list[str] = []
    missing: list[str] = []
    for relative in paths:
        kind = selected_type(relative)
        if kind is None:
            continue
        path = repo / relative
        if not path.is_file():
            missing.append(relative)
            continue
        suffix = path.suffix.lower()
        source = path.read_text(encoding="utf-8-sig", errors="replace")
        size = path.stat().st_size
        lines = stripped_lines(source, kind, suffix)
        for bucket in (by_kind[kind], by_extension[suffix]):
            bucket["files"] += 1
            bucket["bytes"] += size
            bucket["lines"] += lines
        used.append(relative)
    if missing:
        raise ValueError(f"{repo}: {len(missing)} selected sparse files missing, e.g. {missing[:5]}")
    return {
        "by_kind": dict(sorted(by_kind.items())),
        "by_extension": dict(sorted(by_extension.items())),
        "path_manifest_sha256": hashlib.sha256("\n".join(used).encode("utf-8")).hexdigest(),
        "first_paths": used[:8],
    }


def audit(repo: Path, expected_commit: str, groups: dict[str, list[str]]) -> dict[str, object]:
    repo = repo.resolve()
    actual = git_head(repo)
    if actual != expected_commit:
        raise ValueError(f"{repo}: expected commit {expected_commit}, got {actual}")
    tracked = tracked_paths(repo)
    out = {"commit": actual, "tracked_files": len(tracked), "groups": {}}
    for group, prefixes in groups.items():
        selected = [path for path in tracked if any(path.startswith(prefix) for prefix in prefixes)]
        if not selected:
            raise ValueError(f"{repo}: empty selection {group} ({prefixes})")
        out["groups"][group] = {"prefixes": prefixes, **measure(repo, selected)}
    return out


def totals(*groups: dict[str, object]) -> dict[str, int]:
    result = {
        "code_files": 0, "code_pncloc": 0,
        "xml_files": 0, "xml_noncomment_lines": 0,
        "csv_files": 0, "csv_nonblank_lines": 0,
        "manifest_files": 0, "manifest_noncomment_lines": 0,
    }
    for group in groups:
        kinds = group["by_kind"]
        result["code_files"] += kinds.get("code", {}).get("files", 0)
        result["code_pncloc"] += kinds.get("code", {}).get("lines", 0)
        result["xml_files"] += kinds.get("xml", {}).get("files", 0)
        result["xml_noncomment_lines"] += kinds.get("xml", {}).get("lines", 0)
        result["csv_files"] += kinds.get("csv", {}).get("files", 0)
        result["csv_nonblank_lines"] += kinds.get("csv", {}).get("lines", 0)
        result["manifest_files"] += kinds.get("manifest", {}).get("files", 0)
        result["manifest_noncomment_lines"] += kinds.get("manifest", {}).get("lines", 0)
    return result


def java_module_prefixes(modules: list[str]) -> list[str]:
    """Keep the Java runtime and declarations, not bundled webapp libraries."""
    return [f"{name}/src/main/{layer}/" for name in modules for layer in ("java", "resources")]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("product", choices=("odoo", "tryton", "axelor"))
    parser.add_argument("root", type=Path, help="Checkout root; Axelor Suite when product=axelor")
    parser.add_argument("--platform", type=Path, help="Axelor Open Platform checkout")
    parser.add_argument("--webapp", type=Path, help="Axelor assembly webapp checkout")
    parser.add_argument("--studio", type=Path, help="Axelor Studio/BPM checkout")
    parser.add_argument("--utils", type=Path, help="Axelor Utils checkout")
    parser.add_argument("--message", type=Path, help="Axelor Message checkout")
    parser.add_argument("--spreadsheet", type=Path, help="Odoo o-spreadsheet checkout")
    args = parser.parse_args()
    if args.product == "tryton":
        groups = {
            "framework": ["trytond/trytond/"],
            "web_client": ["sao/src/"],
            "operations": [f"modules/{name}/" for name in TRYTON_MODULES],
            "finance_direct_outside_flow": [f"modules/{name}/" for name in TRYTON_FINANCE_DIRECT],
        }
        result = audit(args.root, TRYTON_COMMIT, groups)
        result["selected_totals"] = totals(*(result["groups"][key] for key in ("framework", "web_client", "operations")))
    elif args.product == "odoo":
        if args.spreadsheet is None:
            parser.error("--spreadsheet is required for Odoo")
        groups = {
            "framework": ["odoo/"],
            "web_ui": ["addons/web/"],
            "mail_case": ["addons/mail/"],
            "shared_business": [f"addons/{name}/" for name in ODOO_SHARED_BUSINESS],
            "operations": [f"addons/{name}/" for name in ODOO_OPERATIONS],
            "automation": [f"addons/{name}/" for name in ODOO_AUTOMATION],
            "analytics": [f"addons/{name}/" for name in ODOO_ANALYTICS],
            "finance_direct_outside_flow": [f"addons/{name}/" for name in ODOO_FINANCE_DIRECT],
        }
        result = audit(args.root, ODOO_COMMIT, groups)
        result["selected_totals"] = totals(*(result["groups"][key] for key in (
            "framework", "web_ui", "mail_case", "shared_business", "operations", "automation", "analytics",
        )))
        spreadsheet = audit(args.spreadsheet, ODOO_SPREADSHEET_COMMIT, {"editor_source": ["src/"]})
        result["spreadsheet"] = spreadsheet
        result["selected_totals_with_editor"] = totals(
            *(result["groups"][key] for key in (
                "framework", "web_ui", "mail_case", "shared_business", "operations", "automation", "analytics",
            )), spreadsheet["groups"]["editor_source"],
        )
    elif args.product == "axelor":
        if any(value is None for value in (args.platform, args.webapp, args.studio, args.utils, args.message)):
            parser.error("--platform, --webapp, --studio, --utils and --message are required for Axelor")
        suite = audit(args.root, AXELOR_SUITE_COMMIT, {
            "operations": java_module_prefixes(AXELOR_SUITE_MODULES),
            "equipment_maintenance_outside_flow": java_module_prefixes([AXELOR_MAINTENANCE_OUTSIDE_FLOW]),
            "direct_dependencies_outside_flow": java_module_prefixes(AXELOR_DEPENDENCIES),
        })
        platform = audit(args.platform, AXELOR_PLATFORM_COMMIT, {
            "server_runtime": java_module_prefixes(AXELOR_PLATFORM_MODULES),
            "web_client": ["axelor-front/src/"],
        })
        webapp = audit(args.webapp, AXELOR_WEBAPP_COMMIT, {"assembly": ["src/main/resources/"]})
        studio = audit(args.studio, AXELOR_STUDIO_COMMIT, {
            "backend": ["src/main/java/", "src/main/resources/"],
            "frontend": [f"react/{name}/src/" for name in AXELOR_STUDIO_FRONTENDS],
        })
        utils = audit(args.utils, AXELOR_UTILS_COMMIT, {
            "runtime": ["src/main/java/", "src/main/resources/"],
        })
        message = audit(args.message, AXELOR_MESSAGE_COMMIT, {
            "runtime": ["src/main/java/", "src/main/resources/"],
        })
        result = {"suite": suite, "platform": platform, "webapp": webapp, "studio": studio,
                  "utils": utils, "message": message}
        result["selected_totals_without_studio"] = totals(
            suite["groups"]["operations"], platform["groups"]["server_runtime"],
            platform["groups"]["web_client"], webapp["groups"]["assembly"],
        )
        result["selected_totals_with_studio"] = totals(
            suite["groups"]["operations"], platform["groups"]["server_runtime"],
            platform["groups"]["web_client"], webapp["groups"]["assembly"],
            studio["groups"]["backend"], studio["groups"]["frontend"],
        )
        result["selected_totals_with_studio_utils_message"] = totals(
            suite["groups"]["operations"], platform["groups"]["server_runtime"],
            platform["groups"]["web_client"], webapp["groups"]["assembly"],
            studio["groups"]["backend"], studio["groups"]["frontend"],
            utils["groups"]["runtime"], message["groups"]["runtime"],
        )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
