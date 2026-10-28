import fs from 'node:fs';

/**
 * Apply to the delivered v4 layout, after its original parameterization.
 * The parent authoring process owns workbook import/export and recalculation.
 * No workbook is opened or saved by this helper.
 */
export function applyAbaqueCorrections(ctx) {
  const { S, set, f, inp, band, note, borders, total, C, font } = ctx;
  const bridge = S['Passage Buy France'];
  const parameters = S['Paramètres'];
  const references = S['Références'];
  const msUnit = S['Prix unitaire Microsoft'];
  const fmtJH = ctx.fmtJH || '#,##0 "JH"';
  const models = [
    { name: 'Microsoft', first: 117, noteFirst: 139, firstNoteItem: 123,
      data: JSON.parse(fs.readFileSync('tools/flow_ms_functional_gaps.json', 'utf8')) },
    { name: 'SAP', first: 157, noteFirst: 179, firstNoteItem: 164,
      data: JSON.parse(fs.readFileSync('tools/flow_sap_functional_gaps.json', 'utf8')) },
  ];
  const assert = (condition, message) => { if (!condition) throw new Error(message); };
  const cellValue = (sheet, address) => sheet.getRange(address).values[0][0];

  // These are existing, explicitly labelled technical conventions in final v4.
  for (const [address, expected] of [['D18', 0], ['D20', 1], ['D23', 2]]) {
    assert(cellValue(parameters, address) === expected,
      `Unexpected parameter layout at Paramètres!${address}`);
  }
  const zero = "'Paramètres'!$D$18";
  const one = "'Paramètres'!$D$20";
  const two = "'Paramètres'!$D$23";

  // Three per-unit decompositions previously existed only in narrative notes.
  // The optional optimizer already has its decomposition in the JSON model.
  const additionalTasks = {
    123: [
      { label: 'Analyse des états et des actions du parcours', quantity: 1, effort: [3, 5, 8] },
      { label: 'Paramétrage ou adaptation et vue ciblée', quantity: 1, effort: [5, 9, 15] },
      { label: 'Tests locaux et documentation', quantity: 1, effort: [2, 4, 7] },
    ],
    124: [
      { label: 'Comportement attendu et traitement des exceptions', quantity: 1, effort: [4, 7, 10] },
      { label: 'Séquence et états de compensation', quantity: 1, effort: [7, 12, 20] },
      { label: 'Tests locaux, reprise et documentation', quantity: 1, effort: [4, 6, 10] },
    ],
    127: [
      { label: 'Mapping des preuves et des références', quantity: 1, effort: [3, 5, 8] },
      { label: 'Capture et restitution ciblées', quantity: 1, effort: [6, 10, 16] },
      { label: 'Tests locaux de reconstitution', quantity: 1, effort: [3, 5, 8] },
    ],
  };
  const lastReservedRow = 285;
  bridge.getRange(`B190:K${lastReservedRow}`).unmerge();
  bridge.getRange(`B190:K${lastReservedRow}`).clear({ applyTo: 'all' });
  bridge.getRange(`B190:K${lastReservedRow}`).format = {
    font: { name: font, size: 10, color: C.ink },
    rowHeight: 34, verticalAlignment: 'center', wrapText: true,
  };
  band(bridge, 'B190:K190', 'Charges unitaires des compléments — détail modifiable');
  note(bridge, 'B191',
    'Les quantités et les JH par sous-activité ci-dessous sont des hypothèses de cette étude. ' +
    'Chaque total alimente la charge par unité du tableau fonctionnel ; la quantité de fonctions ' +
    'et leur activation restent dans ce tableau. Aucune charge supplémentaire n’est ajoutée.',
    'K', 52);

  let row = 193;
  const mapping = [];
  for (const model of models) {
    for (const [index, item] of model.data.items.entries()) {
      const parentRow = model.first + index;
      const tasks = item.tasks || additionalTasks[parentRow];
      if (!tasks) continue;
      const computed = tasks.reduce((sum, task) => sum + task.quantity * task.effort[1], 0);
      assert(computed === item.effort[1],
        `Source decomposition does not reconcile at Passage Buy France!E${parentRow}`);
      const blockStart = row;
      band(bridge, `B${row}:K${row}`, `${model.name} — ${item.label}`);
      bridge.getRange(`B${row}:K${row}`).format.rowHeight = 42;
      row += 1;
      // D and F remain the narrow, intentionally blank spacer columns used by
      // the upper functional tables. Put detailed inputs in their wide columns.
      for (const [column, label] of [
        ['B', 'Sous-activité par unité fonctionnelle'], ['C', 'Quantité'],
        ['E', 'JH par unité'], ['G', 'Charge calculée'],
      ]) set(bridge, `${column}${row}`, label);
      band(bridge, `B${row}:G${row}`, null, true);
      set(bridge, `H${row}`, 'Nature');
      set(bridge, `K${row}`, 'Source / périmètre');
      band(bridge, `H${row}:K${row}`, null, true);
      bridge.getRange(`B${row}:K${row}`).format.rowHeight = 42;
      row += 1;
      const firstActivity = row;
      for (const task of tasks) {
        set(bridge, `B${row}`, task.label);
        set(bridge, `C${row}`, task.quantity);
        set(bridge, `E${row}`, task.effort[1]);
        inp(bridge, `C${row}`, '0 "unités"', 0, 10000, 'whole');
        inp(bridge, `E${row}`, '0.0 "JH/unité"', 0, 10000);
        f(bridge, `G${row}`,
          `=IF(AND(COUNT(C${row},E${row})=${two},MIN(C${row},E${row})>=${zero},MOD(C${row},${one})=${zero}),C${row}*E${row},NA())`);
        bridge.getRange(`G${row}`).setNumberFormat(fmtJH);
        set(bridge, `H${row}`, 'Hypothèse d’effort');
        set(bridge, `K${row}`,
          `Décomposition de la ligne ${parentRow}. Hypothèse d’ingénierie de l’étude, ` +
          'pas une charge communiquée par le fournisseur. Les exclusions restent décrites au-dessus.');
        bridge.getRange(`B${row}:K${row}`).format.rowHeight = 66;
        row += 1;
      }
      const lastActivity = row - 1;
      set(bridge, `B${row}`, `Total par unité — renvoi vers E${parentRow}`);
      f(bridge, `G${row}`, `=SUM(G${firstActivity}:G${lastActivity})`);
      bridge.getRange(`G${row}`).setNumberFormat(fmtJH);
      total(bridge, `B${row}:G${row}`);
      f(bridge, `E${parentRow}`, `=G${row}`);
      bridge.getRange(`E${parentRow}`).format.fill = C.pale;
      bridge.getRange(`E${parentRow}`).setNumberFormat('0.0 "JH/unité"');
      borders(bridge, `B${firstActivity}:K${row}`);

      // Replace static arithmetic in the narrative, so it cannot contradict edits.
      const noteRow = model.noteFirst + parentRow - model.firstNoteItem;
      note(bridge, `B${noteRow}`,
        `Ligne ${parentRow} — ${item.label}. ` +
        `Décomposition modifiable : lignes ${firstActivity} à ${lastActivity}, total G${row}. ` +
        `Quantité fonctionnelle : ${item.quantity_basis || item.unit}. ` +
        `Hors poste : ${item.exclusions.join(' ')}. ${item.reason_activation}`,
        'K', 100);
      mapping.push({
        solution: model.name, parentCell: `E${parentRow}`,
        firstActivity, lastActivity, totalCell: `G${row}`,
        quantityCells: tasks.map((_, i) => `C${firstActivity + i}`),
        unitEffortCells: tasks.map((_, i) => `E${firstActivity + i}`),
        unchangedNominal: item.effort[1], noteRow, blockStart,
      });
      row += 2;
    }
  }
  const lastRow = row - 2;
  assert(lastRow <= lastReservedRow, 'Abaque corrections exceed their reserved range');

  // Source values have one owner; no projection or calculation feeds these links.
  const sourceLinks = [
    ['D25', 'C30', 'Base SAP : configurations et spécifiques'],
    ['D37', 'C29', 'SAP : développements spécifiques'],
    ['D38', 'C27', 'SAP : entrées et sorties WRICEF'],
    ['D39', 'C28', 'SAP : conversions WRICEF'],
  ];
  for (const [target, source, label] of sourceLinks) {
    const sourceFormula = references.getRange(source).formulas?.[0]?.[0];
    assert(!sourceFormula || !sourceFormula.includes("'Paramètres'!"),
      `Circular source ownership risk at Références!${source}`);
    f(parameters, target, `='Références'!${source}`);
    parameters.getRange(target).setNumberFormat(fmtJH);
    parameters.getRange(target).format.fill = C.pale;
    const r = target.slice(1);
    set(parameters, `B${r}`, label);
    set(parameters, `C${r}`, 'Donnée source liée');
    set(parameters, `E${r}`, `Références!${source} — offre SAP / Delaware`);
    set(parameters, `F${r}`, 'La donnée propriétaire est dans Références. Ce renvoi évite une seconde saisie indépendante.');
  }
  for (const r of [52, 53, 54, 55, 56]) {
    f(msUnit, `C${r}`, "='Références'!$C$88");
    msUnit.getRange(`C${r}`).format.fill = C.pale;
  }

  set(parameters, 'C11', 'Convention de l’étude');
  set(parameters, 'E11', 'Méthode de conversion de l’étude');
  set(parameters, 'F11',
    'Conversion des personnes-années en JH. Le COPIL source les effectifs et les durées, ' +
    'pas ce nombre de jours travaillés. Appui métier client exclu du nominal.');
  set(parameters, 'B17', 'Cardinalité des validations à quatre champs');
  set(parameters, 'E17', 'Règles de contrôle du classeur');
  set(parameters, 'F17',
    'Constante de structure utilisée par les validations. Les effectifs client ont leurs ' +
    'propres hypothèses en D9 et D10 ; le nombre de vagues est calculé sur le calendrier.');
  set(parameters, 'B31', 'Précision des arrondis de calcul');
  set(parameters, 'E31', 'Convention de calcul du classeur');
  set(parameters, 'F31',
    'Nombre de décimales de la fonction ROUND pour limiter les écarts binaires en M€. ' +
    'Cette précision ne détermine aucun effectif client.');
  set(S.Sources, 'D8', 'Charges retenues par poste de chiffrage ; hypothèses d’ingénierie détaillées.');

  return { bridgeLastRow: lastRow, mapping, sourceLinks };
}
