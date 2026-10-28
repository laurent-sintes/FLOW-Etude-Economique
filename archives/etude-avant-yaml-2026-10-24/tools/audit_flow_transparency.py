"""Read-only OOXML audit of calculation transparency in the delivered workbook.

This script never saves or recalculates the workbook. It deliberately examines
the exported formulas, rather than the builder's JavaScript calculations.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
DOUBLE_QUOTED = re.compile(r'"(?:[^"]|"")*"')
QUOTED_SHEET = re.compile(r"'(?:[^']|'')*'!")
CELL_REFERENCE = re.compile(r"(?<![A-Za-z0-9_])\$?[A-Za-z]{1,3}\$?[0-9]+(?![A-Za-z0-9_])")
NUMERIC_LITERAL = re.compile(r"(?<![A-Za-z0-9_.])(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[Ee][+-]?[0-9]+)?(?![A-Za-z0-9_.])")


def numeric_literals(formula: str) -> list[str]:
    """Ignore strings, sheet names and A1 addresses, preserving numeric tokens."""
    cleaned = DOUBLE_QUOTED.sub("", formula)
    cleaned = QUOTED_SHEET.sub("", cleaned)
    cleaned = CELL_REFERENCE.sub("", cleaned)
    return NUMERIC_LITERAL.findall(cleaned)


def audit(path: pathlib.Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {item.get("Id"): item.get("Target") for item in relationships.findall(f"{{{PACKAGE_REL}}}Relationship")}
        styles = ET.fromstring(archive.read("xl/styles.xml"))
        protected_formula_styles = []
        for index, style in enumerate(styles.findall("m:cellXfs/m:xf", NS)):
            protection = style.find("m:protection", NS)
            if protection is not None and protection.get("hidden") in {"1", "true"}:
                protected_formula_styles.append(index)
        sheets = []
        for item in workbook.findall("m:sheets/m:sheet", NS):
            target = targets[item.get(f"{{{REL}}}id")]
            worksheet_path = target.lstrip("/") if target.startswith("/") else str(pathlib.PurePosixPath("xl") / target)
            root = ET.fromstring(archive.read(worksheet_path))
            formulas = []
            constants = []
            errors = []
            hidden_formulas = []
            for cell in root.findall(".//m:sheetData/m:row/m:c", NS):
                formula = cell.find("m:f", NS)
                if cell.get("t") == "e":
                    errors.append({"cell": cell.get("r"), "error": cell.findtext("m:v", default="", namespaces=NS)})
                if formula is None:
                    continue
                expression = formula.text or ""
                formulas.append({"cell": cell.get("r"), "formula": expression})
                literals = numeric_literals(expression)
                if literals:
                    constants.append({"cell": cell.get("r"), "literals": literals, "formula": expression})
                if int(cell.get("s", "0")) in protected_formula_styles:
                    hidden_formulas.append(cell.get("r"))
            sheets.append({
                "name": item.get("name"),
                "state": item.get("state", "visible"),
                "hidden_rows": [row.get("r") for row in root.findall("m:sheetData/m:row", NS) if row.get("hidden") in {"1", "true"}],
                "hidden_columns": [dict(col.attrib) for col in root.findall("m:cols/m:col", NS) if col.get("hidden") in {"1", "true"}],
                "hidden_formulas": hidden_formulas,
                "formula_count": len(formulas),
                "formulas_with_literals": constants,
                "literal_counts": dict(collections.Counter(literal for entry in constants for literal in entry["literals"])),
                "formula_errors": errors,
                "external_formula_references": [entry for entry in formulas if "[" in entry["formula"] and "]" in entry["formula"]],
            })
        # Excel writes xl/charts; Artifact Tool may place the same OOXML chart
        # under xl/drawings/charts. Both package layouts are valid.
        chart_files = [name for name in archive.namelist() if re.fullmatch(r"xl/(?:drawings/)?charts/chart[0-9]+\.xml", name)]
        return {
            "workbook": str(path.resolve()),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper(),
            "sheet_count": len(sheets),
            "formula_count": sum(sheet["formula_count"] for sheet in sheets),
            "numeric_literal_formula_count": sum(len(sheet["formulas_with_literals"]) for sheet in sheets),
            "hidden_sheet_count": sum(sheet["state"] != "visible" for sheet in sheets),
            "hidden_row_count": sum(len(sheet["hidden_rows"]) for sheet in sheets),
            "hidden_column_count": sum(len(sheet["hidden_columns"]) for sheet in sheets),
            "hidden_formula_count": sum(len(sheet["hidden_formulas"]) for sheet in sheets),
            "formula_error_count": sum(len(sheet["formula_errors"]) for sheet in sheets),
            "external_formula_reference_count": sum(len(sheet["external_formula_references"]) for sheet in sheets),
            "chart_count": len(chart_files),
            "sheets": sheets,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=pathlib.Path)
    parser.add_argument("--report", type=pathlib.Path)
    parser.add_argument("--strict-literals", action="store_true", help="Fail if any numeric literal remains in an exported formula.")
    parser.add_argument("--expected-charts", type=int, help="Require the specified number of non-duplicated native charts.")
    args = parser.parse_args()
    result = audit(args.workbook)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {key: value for key, value in result.items() if key != "sheets"}
    summary["status"] = "PASS"
    failures = [name for name in ["hidden_sheet_count", "hidden_row_count", "hidden_column_count", "hidden_formula_count", "formula_error_count", "external_formula_reference_count"] if result[name]]
    if args.strict_literals and result["numeric_literal_formula_count"]:
        failures.append("numeric_literal_formula_count")
    if args.expected_charts is not None and result["chart_count"] != args.expected_charts:
        failures.append("chart_count")
    if failures:
        summary["status"] = "FAIL"
        summary["failed_checks"] = failures
    print(json.dumps(summary, ensure_ascii=True))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
