"""Complete native chart caches omitted by the Artifact Tool XLSX exporter.

All workbook content and formulas are authored by build_flow_estimate.mjs.
This export compatibility step keeps every live chart reference and reads only
the already calculated worksheet values. It does not calculate financial data.
"""
import json
import math
import os
from pathlib import Path
import posixpath
import re
import sys
import zipfile
from copy import deepcopy
from lxml import etree as ET

C = 'http://schemas.openxmlformats.org/drawingml/2006/chart'
W = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
P = 'http://schemas.openxmlformats.org/package/2006/relationships'
NS = {'c': C, 's': W, 'r': R}

def tag(ns, name):
    return '{' + ns + '}' + name

def column_number(value):
    result = 0
    for ch in value:
        result = result * 26 + ord(ch) - 64
    return result

def column_name(value):
    result = ''
    while value:
        value, digit = divmod(value - 1, 26)
        result = chr(65 + digit) + result
    return result

def finalize(path, navigation_path=None):
    path = Path(path)
    with zipfile.ZipFile(path) as archive:
        parts = {i.filename: archive.read(i.filename) for i in archive.infolist()}
        infos = archive.infolist()
    shared = []
    if 'xl/sharedStrings.xml' in parts:
        root = ET.fromstring(parts['xl/sharedStrings.xml'])
        shared = [''.join(x.itertext()) for x in root.findall(tag(W, 'si'))]
    workbook = ET.fromstring(parts['xl/workbook.xml'])
    relationships = ET.fromstring(parts['xl/_rels/workbook.xml.rels'])
    targets = {x.get('Id'): x.get('Target') for x in relationships.findall(tag(P, 'Relationship'))}
    sheets = {}
    sheet_parts = {}
    for sheet in workbook.findall('s:sheets/s:sheet', NS):
        target = targets[sheet.get(tag(R, 'id'))]
        target = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
        root = ET.fromstring(parts[target])
        values = {}
        for cell in root.findall('.//s:sheetData/s:row/s:c', NS):
            kind = cell.get('t')
            value = cell.find('s:v', NS)
            value = value.text if value is not None else None
            if kind == 's' and value is not None:
                value = shared[int(value)]
            elif kind == 'inlineStr':
                value = ''.join(cell.find('s:is', NS).itertext())
            elif kind == 'e':
                value = None  # Invalid mandatory inputs must not become chart zeros.
            values[cell.get('r')] = value
        sheets[sheet.get('name')] = values
        sheet_parts[sheet.get('name')] = target

    def referenced_values(formula):
        match = re.fullmatch(r"(?:'((?:[^']|'')+)'|([^!]+))!\$?([A-Z]+)\$?(\d+)(?::\$?([A-Z]+)\$?(\d+))?", formula)
        if not match:
            raise ValueError('Unsupported chart source reference: ' + formula)
        quoted, plain, col1, row1, col2, row2 = match.groups()
        name = quoted.replace("''", "'") if quoted else plain
        col2, row2 = col2 or col1, int(row2 or row1)
        row1 = int(row1)
        return [sheets[name].get(column_name(col) + str(row))
                for row in range(row1, row2 + 1)
                for col in range(column_number(col1), column_number(col2) + 1)]

    report = []
    for name, source in list(parts.items()):
        if not re.fullmatch(r'xl/(?:drawings/)?charts/chart\d+\.xml', name):
            continue
        root = ET.fromstring(source)
        # The exporter keeps categoryFormula for preview but omits scatter xVal
        # on individually added series. Bind each milestone to its actual year.
        for series in root.xpath('//c:scatterChart/c:ser', namespaces=NS):
            y_formula = series.find('c:yVal/c:numRef/c:f', NS)
            if y_formula is None or not y_formula.text:
                continue
            match = re.fullmatch(r"'(Trajectoire mensuelle|Hypothèses)'!\$?E\$?(19[1-8])", y_formula.text)
            endpoint = re.fullmatch(r"'Hypothèses'!\$?([CDE])\$?187", y_formula.text)
            if match is None and endpoint is None:
                continue
            x_values = series.find('c:xVal', NS)
            if x_values is None:
                x_values = ET.Element(tag(C, 'xVal'))
                y_values = series.find('c:yVal', NS)
                series.insert(list(series).index(y_values), x_values)
            for child in list(x_values):
                x_values.remove(child)
            reference = ET.SubElement(x_values, tag(C, 'numRef'))
            ET.SubElement(reference, tag(C, 'f')).text = "'Hypothèses'!$B$187" if endpoint is not None else "'" + match.group(1) + "'!$D$" + match.group(2)
            if endpoint is not None:
                labels = series.find('c:dLbls', NS)
                if labels is not None:
                    prior_format = labels.find('c:numFmt', NS)
                    if prior_format is not None:
                        labels.remove(prior_format)
                    labels.insert(0, ET.Element(tag(C, 'numFmt'), formatCode='0.0 "M€"', sourceLinked='0'))
        count, live_points = 0, 0
        for reference in root.xpath('//c:numRef | //c:strRef', namespaces=NS):
            formula = reference.find('c:f', NS)
            if formula is None or not formula.text:
                continue
            values = referenced_values(formula.text)
            numeric = reference.tag == tag(C, 'numRef')
            cache_tag = tag(C, 'numCache' if numeric else 'strCache')
            old = reference.find(cache_tag)
            if old is not None:
                reference.remove(old)
            cache = ET.SubElement(reference, cache_tag)
            if numeric:
                ET.SubElement(cache, tag(C, 'formatCode')).text = 'General'
            ET.SubElement(cache, tag(C, 'ptCount'), val=str(len(values)))
            for index, value in enumerate(values):
                if value is None:
                    continue
                if numeric:
                    try:
                        if not math.isfinite(float(value)):
                            continue
                    except (TypeError, ValueError):
                        continue
                point = ET.SubElement(cache, tag(C, 'pt'), idx=str(index))
                ET.SubElement(point, tag(C, 'v')).text = str(value)
                live_points += 1
            count += 1
        # Scatter supports actual single-point milestones, with no NA() helpers.
        milestone_series = 0
        for scatter in root.xpath('//c:scatterChart', namespaces=NS):
            style = scatter.find('c:scatterStyle', NS)
            if style is not None:
                style.set('val', 'lineMarker')
        for series in root.xpath('//c:scatterChart/c:ser', namespaces=NS):
            formula = series.find('c:yVal/c:numRef/c:f', NS)
            if formula is None or not formula.text or not any(s in formula.text for s in ['Trajectoire mensuelle', 'Hypothèses']):
                continue
            milestone = re.search(r'!\$?E\$?19[1-8](?::\$?E\$?19[1-8])?$', formula.text) is not None
            marker = series.find('c:marker', NS)
            if marker is None:
                marker = ET.Element(tag(C, 'marker'))
                anchor = next((x for x in series if ET.QName(x).localname in
                               ['dPt', 'dLbls', 'trendline', 'errBars', 'xVal', 'yVal']), None)
                if anchor is None:
                    series.append(marker)
                else:
                    series.insert(list(series).index(anchor), marker)
            symbol = marker.find('c:symbol', NS)
            if symbol is None:
                symbol = ET.SubElement(marker, tag(C, 'symbol'))
            symbol.set('val', 'circle' if milestone else 'none')
            size = marker.find('c:size', NS)
            if size is None:
                size = ET.SubElement(marker, tag(C, 'size'))
            size.set('val', '5')
            if milestone:
                # Excel otherwise picks a new theme colour for each marker,
                # even when the series line/fill already has the solution colour.
                marker_shape = marker.find('c:spPr', NS)
                if marker_shape is not None:
                    marker.remove(marker_shape)
                series_shape = series.find('c:spPr', NS)
                if series_shape is not None:
                    marker.append(deepcopy(series_shape))
                milestone_series += 1
        parts[name] = ET.tostring(root, encoding='UTF-8', xml_declaration=True, standalone=True)
        report.append({'part': name, 'references': count, 'cached_points': live_points, 'milestones': milestone_series})
    if len(report) != 1 or sum(x['milestones'] for x in report) != 5:
        raise ValueError('Expected one comparison chart and five live milestone series: ' + json.dumps(report))
    calculation = workbook.find(tag(W, 'calcPr'))
    if calculation is None:
        calculation = ET.Element(tag(W, 'calcPr'))
        ext = workbook.find(tag(W, 'extLst'))
        if ext is None:
            workbook.append(calculation)
        else:
            workbook.insert(list(workbook).index(ext), calculation)
    calculation.set('calcMode', 'auto')
    calculation.set('fullCalcOnLoad', '1')
    calculation.set('forceFullCalc', '0')
    parts['xl/workbook.xml'] = ET.tostring(workbook, encoding='UTF-8', xml_declaration=True, standalone=True)
    # Navigation is a native XLSX feature missing from this authoring engine.
    # Labels and destinations are authored in JS. No financial data or formula
    # is created or recalculated by this compatibility step.
    if navigation_path:
        navigation = json.loads(Path(navigation_path).read_text(encoding='utf-8'))
        for sheet_name in {link['sheet'] for link in navigation}:
            part = sheet_parts[sheet_name]
            root = ET.fromstring(parts[part])
            links = root.find(tag(W, 'hyperlinks'))
            if links is None:
                links = ET.Element(tag(W, 'hyperlinks'))
                following = {'printOptions', 'pageMargins', 'pageSetup', 'headerFooter',
                             'rowBreaks', 'colBreaks', 'customProperties', 'cellWatches',
                             'ignoredErrors', 'smartTags', 'drawing', 'legacyDrawing',
                             'legacyDrawingHF', 'picture', 'oleObjects', 'controls',
                             'webPublishItems', 'tableParts', 'extLst'}
                anchor = next((x for x in root if ET.QName(x).localname in following), None)
                if anchor is None:
                    root.append(links)
                else:
                    root.insert(list(root).index(anchor), links)
            for item in (x for x in navigation if x['sheet'] == sheet_name):
                if item['target'] not in sheet_parts:
                    raise ValueError('Unknown hyperlink destination: ' + item['target'])
                for old in list(links):
                    if old.get('ref') == item['cell']:
                        links.remove(old)
                ET.SubElement(links, tag(W, 'hyperlink'), ref=item['cell'], location=item['location'])
            parts[part] = ET.tostring(root, encoding='UTF-8', xml_declaration=True, standalone=True)
        print('NATIVE_LINKS', len(navigation))
    temporary = path.with_suffix('.chart-cache.tmp')
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for info in infos:
                archive.writestr(info, parts[info.filename])
        with zipfile.ZipFile(temporary) as archive:
            assert archive.testzip() is None
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
    print('NATIVE_CHART_CACHES', json.dumps(report))

if __name__ == '__main__':
    finalize(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
