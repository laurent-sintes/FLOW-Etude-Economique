import { createRequire } from 'node:module';
import fs from 'node:fs';
import crypto from 'node:crypto';

// Read-only audit. All sensitivity changes are made in an imported in-memory
// workbook and restored. There is deliberately no export/save operation.
const require = createRequire('C:/Users/laure/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const { FileBlob, SpreadsheetFile } = require('@oai/artifact-tool');
const { execFileSync } = require('node:child_process');
const path = process.argv[2] || 'outputs/01a1530f-f378-7fd1-9654-468c9b2141b6/FLOW_Make_abaques_et_prix_France_v4.xlsx';
const sha = () => crypto.createHash('sha256').update(fs.readFileSync(path)).digest('hex').toUpperCase();
const originalHash = sha();
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(path));
const cell = (sheet, address) => wb.worksheets.getItem(sheet).getRange(address);
const value = (sheet, address) => cell(sheet, address).values[0][0];
const formula = (sheet, address) => cell(sheet, address).formulas?.[0]?.[0] || '';
const set = (sheet, address, x) => { cell(sheet, address).values = [[x]]; };
const finite = x => typeof x === 'number' && Number.isFinite(x);
const assert = (ok, message) => { if (!ok) throw new Error(message); };
const near = (actual, expected, message, tolerance = 1e-8) =>
  assert(finite(actual) && Math.abs(actual - expected) <= tolerance,
    `${message}: ${actual}; expected ${expected}`);
const cases = [
  { name: 'FLOW', unit: 'Prix unitaire Flow', price: 'Prix Flow', outputRow: 9, runRow: 35, start: 8 },
  { name: 'SAP', unit: 'Prix unitaire SAP', price: 'Prix SAP', outputRow: 10, runRow: 36, start: 29 },
  { name: 'Microsoft', unit: 'Prix unitaire Microsoft', price: 'Prix Microsoft', outputRow: 11, runRow: 37, start: 50 },
];
const tco = c => value('Comparaison', `I${c.outputRow}`);
const initial = c => value('Comparaison', `D${c.outputRow}`);
const runYears = c => value('Comparaison', `F${c.runRow}`);
const passed = [], failures = [];
const test = (name, fn) => {
  try { fn(); passed.push(name); console.log('PASS', name); }
  catch (error) { failures.push({ name, error: String(error?.message || error) }); console.log('FAIL', name, error?.message || error); }
};
function mutate(changes, check) {
  const originals = changes.map(([sheet, address]) => ({
    sheet, address, values: cell(sheet, address).values, formula: formula(sheet, address),
  }));
  try {
    for (const [sheet, address, x] of changes) set(sheet, address, x);
    wb.recalculate();
    check();
  } finally {
    for (const saved of originals) {
      if (saved.formula) cell(saved.sheet, saved.address).formulas = [[saved.formula]];
      else cell(saved.sheet, saved.address).values = saved.values;
    }
    wb.recalculate();
  }
}
const allCells = () => JSON.stringify(wb.worksheets.items.map(sheet => ({
  name: sheet.name, values: sheet.getUsedRange(true).values, formulas: sheet.getUsedRange(true).formulas,
})));
wb.recalculate();
const baseline = cases.map(c => ({ ...c, tco: tco(c), initial: initial(c), runYears: runYears(c) }));
const baselineCells = allCells();
console.log('BASELINE', JSON.stringify(baseline));

test('Export contains no hidden data, numerical formula literals or cached errors', () => {
  let stdout;
  try {
    stdout = execFileSync(
      'C:/Users/laure/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
      ['tools/audit_flow_transparency.py', path, '--strict-literals', '--expected-charts', '1'],
      { encoding: 'utf8', maxBuffer: 8 * 1024 * 1024 },
    );
  } catch (error) {
    if (!error.stdout) throw error;
    stdout = String(error.stdout);
  }
  const report = JSON.parse(stdout.trim());
  console.log('TRANSPARENCY', JSON.stringify(report));
  assert(report.status === 'PASS', `OOXML transparency inspection failed: ${(report.failed_checks || []).join(', ')}`);
  const linkScript = `
import json, re, sys, zipfile, xml.etree.ElementTree as ET
ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
rid = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
with zipfile.ZipFile(sys.argv[1]) as z:
    rels = {x.attrib['Id']: x.attrib['Target'] for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    sheets = {}
    for entry in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets', ns):
        path = rels[entry.attrib[rid]]
        path = path.lstrip('/') if path.startswith('/') else 'xl/' + path
        sheets[entry.attrib['name']] = ET.fromstring(z.read(path))
    count, invalid = 0, []
    for name, root in sheets.items():
        for link in root.findall('m:hyperlinks/m:hyperlink', ns):
            count += 1
            location = link.attrib.get('location', '').lstrip('#')
            if '!' not in location:
                invalid.append({'sheet': name, 'link': dict(link.attrib)})
                continue
            target, address = location.rsplit('!', 1)
            target = target.strip("'").replace("''", "'")
            address = address.replace('$', '')
            if target not in sheets or not re.fullmatch(r'[A-Z]{1,3}[1-9][0-9]*', address):
                invalid.append({'sheet': name, 'target': location})
            elif sheets[target].find(".//m:c[@r='" + address + "']", ns) is None:
                invalid.append({'sheet': name, 'empty_target': location})
    print(json.dumps({'count': count, 'invalid': invalid}))
`;
  const links = JSON.parse(execFileSync(
    'C:/Users/laure/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
    ['-c', linkScript, path], { encoding: 'utf8' }).trim());
  console.log('NATIVE_LINKS', JSON.stringify(links));
  assert(links.count === 22 && links.invalid.length === 0, 'Expected 22 valid native internal navigation links');
});

test('Recalculation has no spreadsheet errors in any used cell', () => {
  const errorPattern = /^#(?:N\/A|VALUE!|REF!|DIV\/0!|NAME\?|NUM!|SPILL!|CALC!|NULL!)$/;
  for (const sheet of wb.worksheets.items) {
    const values = sheet.getUsedRange(true).values.flat();
    const errors = values.filter(x => typeof x === 'string' && errorPattern.test(x));
    assert(errors.length === 0, `${sheet.name}: ${errors.length} error cells`);
    const unsupported = values.filter(x => typeof x === 'string' && /is not implemented/i.test(x));
    assert(unsupported.length === 0, `${sheet.name}: unsupported spreadsheet function`);
  }
});

test('New totals reconcile independently to prior totals plus service changes', () => {
  // This is the pre-correction read-only snapshot, not any current formula.
  const old = JSON.parse(fs.readFileSync('tmp/audit_v4_relecture_snapshot.json', 'utf8'));
  assert(old.sha256 === 'C3A7DB3E674E5B6B21BE61F706330C2560E5B4F5EB435A5146AD76E323D9B65F',
    'Unexpected prior snapshot: re-establish the independent historical baseline');
  const oldValue = (s, a) => old.sheets[s][a].v;
  for (const c of cases) {
    const oldService = oldValue(c.unit, 'D26') + (c.name === 'FLOW' ? 0 : oldValue(c.unit, 'D33'));
    const newService = c.name === 'FLOW'
      ? (250 * 0.2 + 240 * 0.5 + 10 * 2 + 60 * 3 + 12 * 2 + 12 * 2 + 12 * 2 +
          12 * 6 + 36 * 2 + 12 * 2 + 12 * 3 + 12 * 2 + 12 * 3 + 4 * 5) * 750
      : c.name === 'SAP' ? 250000 + 450000 : (472 + 443.5) * 850;
    const annualDelta = newService - oldService + (c.name === 'SAP' ? 350000 - oldValue(c.unit,'D27') : 0);
    for (const [col, horizon] of [['F', 3], ['G', 5], ['H', 10], ['I', 15]]) {
      const exposure = Array.from({ length: horizon }, (_, y) => oldValue('Calculs 15 ans', `M${c.start + y + 1}`)).reduce((a, b) => a + b, 0);
      const expected = oldValue('Comparaison', `${col}${c.outputRow}`) + annualDelta * exposure / 1e6;
      const actual = value('Comparaison', `${col}${c.outputRow}`);
      near(actual, expected, `${c.name} independent ${horizon}-year budget`);
      near(actual, value('Calculs 15 ans', `L${c.start + horizon}`), `${c.name} ${horizon}-year cumulative trace`);
      const detail = Array.from({ length: 13 }, (_, j) => value('Comparaison', `${col}${44 + j * 3 + cases.indexOf(c)}`)).reduce((a, b) => a + b, 0);
      near(detail, actual, `${c.name} ${horizon}-year cost categories reconcile without duplicated subsets`);
    }
    const matureExposure = Array.from({ length: 10 }, (_, y) => oldValue('Calculs 15 ans', `M${c.start + y + 6}`)).reduce((a, b) => a + b, 0);
    const expectedAnnual = oldValue('Comparaison', `E${c.outputRow}`) + annualDelta * matureExposure / 10 / 1e6;
    near(value('Comparaison', `E${c.outputRow}`), expectedAnnual, `${c.name} annual average of years 6 to 15`);
    const annualCalc = Array.from({ length: 10 }, (_, y) =>
      value('Calculs 15 ans', `I${c.start + y + 6}`) - value('Calculs 15 ans', `C${c.start + y + 6}`)
    ).reduce((a, b) => a + b, 0) / 10;
    near(annualCalc, expectedAnnual, `${c.name} annual summary trace to annual schedules`);
    near(initial(c), oldValue('Comparaison', `D${c.outputRow}`), `${c.name} unchanged initial budget`);
    near(runYears(c), oldValue('Comparaison', `F${c.runRow}`), `${c.name} unchanged exposure to Run`);
  }
});

test('Microsoft diagnostics follow its domains; FLOW and SAP retain their bases', () => {
  near(value('Service annuel', 'C13'), 240, 'FLOW diagnostics');
  near(value('Service annuel', 'D13'), 0.5, 'FLOW effort per diagnostic');
  near(value('Service annuel', 'C232'), 288, 'Microsoft functional diagnostic volume');
  near(value('Service annuel', 'C233'), 72, 'Microsoft technical deep dives');
  near(value('Service annuel', 'E148'), 198, 'Microsoft diagnostic effort');
  for (const c of cases) near(value(c.unit, 'D43'), 0, `${c.name} base service inflation`);
});

test('A FLOW diagnostic does not change the independently calibrated Microsoft service', () => {
  mutate([['Service annuel', 'C13', 241]], () => {
    for (const c of baseline) near(tco(c), c.tco + (c.name !== 'FLOW' ? 0 : 0.5 * value(c.unit, 'D31') * c.runYears / 1e6),
      `${c.name} diagnostic sensitivity`);
  });
});

test('Zero diagnostics is accepted and removes only the corresponding diagnostic cost', () => {
  mutate([['Service annuel', 'C13', 0]], () => {
    for (const c of baseline) near(tco(c), c.tco - (c.name !== 'FLOW' ? 0 : 240 * 0.5 * value(c.unit, 'D31') * c.runYears / 1e6),
      `${c.name} zero diagnostic quantity`);
  });
});

test('A blank FLOW diagnostic invalidates only FLOW', () => {
  mutate([['Service annuel', 'C13', null]], () => {
    assert(!finite(tco(cases[0])), 'FLOW blank quantity silently accepted');
    near(tco(cases[2]),baseline[2].tco,'Microsoft independent');
    near(tco(cases[1]),baseline[1].tco,'SAP remains sourced');
  });
});

test('A blank evolution demand invalidates estimates but not the SAP TMA forfait', () => {
  mutate([['Service annuel', 'C33', null]], () => {
    for (const c of cases.filter(c=>c.name!=='SAP')) assert(!finite(tco(c)), `${c.name}: blank evolution demand silently accepted`);
    near(tco(cases[1]),baseline[1].tco,'SAP TMA remains sourced');
  });
});

test('SAP uses source forfaits and Microsoft uses its estimate, without cumulation', () => {
  near(value('Service annuel', 'E152'), 472, 'Microsoft maintenance and coordination JH');
  near(value('Service annuel', 'E162'), 443.5, 'Microsoft operations JH');
  for (const c of cases.slice(1)) {
    near(value(c.unit, 'D26'), c.name==='SAP'?250000:472 * value(c.unit, 'D31'), `${c.name} maintenance cost`);
    near(value(c.unit, 'D33'), c.name==='SAP'?450000:443.5 * value(c.unit, 'D31'), `${c.name} operations cost`);
    near(value(c.unit, 'D27'), c.name==='SAP'?350000:440 * value(c.unit, 'D35'), `${c.name} evolution cost`);
    for (const a of ['D28', 'D32', 'D134', 'D135', 'D136']) near(value(c.unit, a), 0, `${c.name} removed supplement ${a}`);
  }
});

test('Changing the old 3% / 5% supplements no longer changes any TCO', () => {
  const changes = cases.slice(1).flatMap(c => [[c.unit, 'D134', 0.03], [c.unit, 'D135', 0.05]]);
  mutate(changes, () => {
    for (const c of baseline) near(tco(c), c.tco, `${c.name} removed percentage drivers`);
  });
});

test('Each source SAP forfait changes only SAP TCO once over its Run years', () => {
  for (const address of ['C81', 'C82', 'C83']) {
    mutate([['Références', address, value('Références', address) + 100000]], () => {
      for (const c of baseline) near(tco(c), c.tco+(c.name==='SAP'?100000*c.runYears/1e6:0), `${c.name} source ${address}`);
    });
  }
});

test('Missing SAP source forfaits are not silently treated as zero', () => {
  for(const address of ['C81','C82','C83']){
    mutate([['Références',address,null]],()=>{
      assert(!finite(tco(cases[1])),`Missing SAP ${address} must invalidate total`);
      near(tco(cases[2]),baseline[2].tco,'Microsoft independent of SAP missing source');
    });
  }
});

test('All twelve detailed unit charges are formulas with their original nominal values', () => {
  for (const [a, expected] of [
    ['E123', 18], ['E124', 25], ['E125', 135], ['E126', 55], ['E127', 20],
    ['E128', 107], ['E129', 99], ['E130', 90], ['E167', 42], ['E169', 100], ['E170', 100], ['E171', 54],
  ]) {
    assert(formula('Passage Buy France', a), `${a}: still a typed result`);
    near(value('Passage Buy France', a), expected, `${a} preserved nominal`);
  }
});

test('An edited component of E126 propagates to initial Microsoft cost and TCO once', () => {
  const totalAddress = formula('Passage Buy France', 'E126').replace(/^=/, '').replace(/\$/g, '');
  const totalFormula = formula('Passage Buy France', totalAddress);
  const first = totalFormula.match(/SUM\(G(\d+):G\d+\)/i);
  assert(first, 'E126 total does not expose its component rows');
  const row = Number(first[1]), quantityCell = `C${row}`;
  const effort = value('Passage Buy France', `E${row}`);
  const quantity = value('Passage Buy France', quantityCell);
  const ms = baseline[2], extraJH = effort * value('Passage Buy France', 'C126');
  const extraCost = extraJH * value(ms.unit, 'D14') / 1e6;
  mutate([['Passage Buy France', quantityCell, quantity + 1]], () => {
    near(value('Passage Buy France', 'E126'), 55 + effort, 'E126 decomposition propagation');
    near(initial(ms), ms.initial + extraCost, 'Microsoft initial incremental component');
    near(tco(ms), ms.tco + extraCost, 'Microsoft one-time component, no annual MCO percentage added');
    for (const c of baseline.slice(0, 2)) near(tco(c), c.tco, `${c.name} unaffected by Microsoft component`);
  });
});

test('A blank detailed component is rejected while zero is accepted', () => {
  mutate([['Passage Buy France', 'C215', null]], () => {
    assert(!finite(value('Passage Buy France', 'E126')), 'Blank component became zero');
    assert(!finite(tco(cases[2])), 'Blank component left a plausible Microsoft TCO');
  });
  mutate([['Passage Buy France', 'C215', 0]], () => {
    near(value('Passage Buy France', 'E126'), 30, 'Explicit zero component retains other component');
    assert(finite(tco(cases[2])), 'Explicit zero component rejected');
  });
});

test('Historical source references have one owner', () => {
  for (const [target, source] of [['D25', 'C30'], ['D37', 'C29'], ['D38', 'C27'], ['D39', 'C28']]) {
    assert(formula('Paramètres', target).includes(`'Références'!${source}`), `${target}: source duplicate`);
    near(value('Paramètres', target), value('Références', source), `${target} source tie-out`);
  }
  for (const row of [52, 53, 54, 55, 56]) assert(
    formula('Prix unitaire Microsoft', `C${row}`).replace(/\$/g, '').includes("'Références'!C88"),
    `Microsoft C${row}: duplicated licence assumption`);
});

test('Resource inflation does not inflate Buy human operations', () => {
  for (const c of cases.slice(1)) {
    const before = Array.from({ length: 15 }, (_, i) => value('Calculs 15 ans', `F${c.start + i + 1}`));
    mutate([[c.unit, 'D45', 0.07]], () => {
      for (let i = 0; i < 15; i++) near(value('Calculs 15 ans', `F${c.start + i + 1}`), before[i],
        `${c.name} year ${i + 1}: human operations use service inflation`);
    });
  }
});

test('France service inflation applies to Buy human operations over the actual Run calendar', () => {
  for (const c of cases.slice(1)) {
    mutate([[c.unit, 'D43', 0.02]], () => {
      for (let y = 1; y <= 15; y++) {
        const row = c.start + y;
        const expected = value(c.unit, 'D33') * 1.02 ** (y - 1) * value('Calculs 15 ans', `M${row}`) / 1e6;
        near(value('Calculs 15 ans', `F${row}`), expected, `${c.name} human operations year ${y}`);
      }
    });
  }
});

test('Microsoft skill allocation reconciles maintenance, operations and evolutions without added staffing cost', () => {
  near(value('Service annuel','C307'),472,'Maintenance skills');
  near(value('Service annuel','D307'),443.5,'Operations skills');
  near(value('Service annuel','E307'),440,'Evolution skills');
  near(value('Service annuel','F307'),1355.5,'Total days by skill');
  near(value('Service annuel','G307'),1355.5/200,'Capacity convention');
  near(value('Service annuel','H307'),1152175,'Skill budget equals billed activities');
  near(value('Prix unitaire Microsoft','D26')+value('Prix unitaire Microsoft','D27')+value('Prix unitaire Microsoft','D33'),
       value('Service annuel','H307'),'No second budget for capacity');
});

test('One additional reference interface changes only Microsoft annual activities once', () => {
  mutate([['Service annuel','C203',41]],()=>{
    near(value('Références','C118'),40,'Historical pilot reference is not overwritten by target inventory');
    near(tco(cases[2]),baseline[2].tco+3.5*850*baseline[2].runYears/1e6,'Interface lifecycle effort');
    near(initial(cases[2]),baseline[2].initial,'Service perimeter assumption does not invent initial work');
    for(const c of baseline.slice(0,2))near(tco(c),c.tco,`${c.name} independent of Microsoft interfaces`);
  });
});

test('One additional operational domain changes only Microsoft service by the explicit task days', () => {
  mutate([['Service annuel','C202',7]],()=>{
    near(tco(cases[2]),baseline[2].tco+69*850*baseline[2].runYears/1e6,'Domain workload');
    for(const c of baseline.slice(0,2))near(tco(c),c.tco,`${c.name} independent of Microsoft domains`);
  });
});

test('Missing Microsoft drivers and impossible nested diagnostic counts invalidate Microsoft', () => {
  for(const change of [['Service annuel','C208',null],['Service annuel','C203',null],['Service annuel','C209',5]]){
    mutate([change],()=>{
      assert(!finite(tco(cases[2])),'Missing or inconsistent Microsoft driver silently accepted');
      for(const c of baseline.slice(0,2))near(tco(c),c.tco,`${c.name} unchanged`);
    });
  }
});

test('Every sensitivity is restored and the source file is unchanged', () => {
  assert(allCells() === baselineCells, 'In-memory workbook was not restored completely');
  assert(sha() === originalHash, 'Audit modified the workbook on disk');
});

console.log('RESULT', JSON.stringify({ passed: passed.length, failed: failures.length, failures, sha256: sha(), baseline }, null, 2));
if (failures.length) process.exitCode = 1;
