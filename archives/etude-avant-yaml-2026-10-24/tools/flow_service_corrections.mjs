// Applies the audited service assumptions to the imported workbook.
// Input quantities live here once; price sheets link to this shared service build.
export function applyServiceCorrections(ctx) {
  const { S, set, f, inp, band, note, borders, total, C, font, fmtJH, fmtPct, fmtEuro, fmtRate } = ctx;
  const run = S['Run Flow'];
  const uf = S['Prix unitaire Flow'];
  const sap = S['Prix unitaire SAP'];
  const ms = S['Prix unitaire Microsoft'];
  const zero = "'Paramètres'!$D$18";
  const one = "'Paramètres'!$D$20";
  const two = "'Paramètres'!$D$23";
  const three = "'Paramètres'!$D$19";
  const putNote = (sheet, address, text, last = 'I', height = 48) => {
    set(sheet, address, text);
    const row = address.match(/\d+/)[0];
    sheet.getRange(`${address}:${last}${row}`).format.wrapText = true;
    sheet.getRange(`${address}:${last}${row}`).format.rowHeight = height;
  };
  const unit = (sheet, a, value, format = '0.00 "JH/unité"') => {
    set(sheet, a, value); inp(sheet, a, format, 0, 100000);
  };
  const product = (row, quantity = 'C', effort = 'D') =>
    `=IF(AND(COUNT(${quantity}${row},${effort}${row})=${two},MIN(${quantity}${row},${effort}${row})>=${zero}),${quantity}${row}*${effort}${row},NA())`;
  const link = (sheet, address, from) => f(sheet, address, `='Run Flow'!${from}`);
  const numericLink = (sheet, address, from) =>
    f(sheet, address, `=IF(ISNUMBER('Run Flow'!${from}),'Run Flow'!${from},NA())`);

  set(run, 'B2', 'Service annuel — FLOW, SAP et Microsoft');
  set(run, 'B4', 'Même besoin de service en heures ouvrées. Prestations en France. Astreinte et migrations majeures en options.');
  set(run, 'B7', 'FLOW — budget annuel de maintenance et exploitation');
  set(run, 'B8', 'Maintenance et exploitation FLOW');
  set(run, 'B9', 'FLOW — fonctionnement, ressources comprises');
  set(run, 'C13', 240);
  inp(run, 'C13', '0 "diagnostics/an"', 0, 100000, 'whole');
  set(run, 'B18', 'Paramètres, sécurité et capacité applicative');
  set(run, 'B25', 'Exercice de reprise du service métier');
  set(run, 'B52', 'Évolution du panier FLOW par rapport à la première estimation');
  set(run, 'C53', 'Ancienne hypothèse JH');
  set(run, 'D53', 'Charge retenue JH');
  set(run, 'B60', 'Panier de service avant restauration / PRA');
  for (let r = 12; r <= 25; r++) set(run, 'I' + r, 'Hypothèse d’ingénierie — détail ci-dessous');
  putNote(run, 'B64',
    'Le panier retient 240 diagnostics/an pour chaque solution. La prévention et les rétablissements s’ajoutent à ces diagnostics. L’écart FLOW de 70 JH/an rétablit la capacité de support précédemment réduite. Aucun gain de prévention non mesuré n’est déduit.',
    'I', 58);
  putNote(run, 'B99',
    'Contrôle des alertes et du service — revue humaine mutualisée en heures ouvrées, 250 journées de contrôle par an. La surveillance automatisée est permanente. La revue classe les alertes ; le diagnostic détaillé et le rétablissement sont comptés dans leurs activités propres. Même volume pour les trois solutions.',
    'I', 64);
  putNote(run, 'B102',
    'Diagnostic applicatif L2/L3 — 240 problèmes qualifiés par an, à 0,5 JH chacun, pour les trois solutions. Cette analyse précède le correctif. Les tests ciblés et le codage sont dans Corrections. La prévention n’abaisse pas le volume nominal de diagnostics.',
    'I', 58);
  putNote(run, 'B105',
    'Rétablissement technique — dix interventions annuelles de deux JH : disponibilité, connectivité, restauration opérationnelle ou dépendances. Aucun nouveau code, diagnostic applicatif, rejeu de message métier ou test planifié de sauvegarde. Même besoin de rétablissement du service métier pour les trois solutions.',
    'I', 64);
  putNote(run, 'B108',
    'Corrections FLOW — 60 correctifs/an, trois JH par correctif pour conception, code, tests ciblés et documentation. Le propriétaire du produit assure le standard et les particularités. Les solutions Buy retiennent 30 corrections/an sur l’ensemble de leurs extensions et interfaces ; le standard est maintenu dans la souscription. Ce différentiel est une hypothèse.',
    'I', 70);
  putNote(run, 'B111',
    'Dépendances et maintenance logicielle courante — douze interventions de deux JH sur Java/Spring, moteurs et bibliothèques. Changements mineurs et correctifs de sécurité ; migrations majeures en option. Dans les solutions SaaS, la maintenance du produit standard et de ses dépendances est supposée couverte par la souscription.',
    'I', 64);
  putNote(run, 'B114',
    'Configuration technique FLOW — douze interventions de deux JH sur le runtime, certificats, services de données, messagerie et automatisation. Hors fourniture de ressources et tâches déjà assurées par le fournisseur managé. Cette administration de la plateforme standard SaaS est supposée incluse dans les souscriptions Buy.',
    'I', 64);
  putNote(run, 'B117',
    'Paramètres, sécurité et capacité applicative — douze revues de deux JH des droits, paramètres, usages, consommation et points de performance applicative. Même activité cliente pour les trois solutions. Hors administration technique du runtime, diagnostic d’incident et développement de nouvelles fonctions.',
    'I', 58);
  putNote(run, 'B120',
    'Régression et livraisons courantes — FLOW : douze campagnes de six JH. Buy : quatre campagnes de quinze JH sur les paramètres, extensions et interfaces, hypothèse de cadence et non calendrier contractuel. Ces campagnes transverses excluent les tests ciblés déjà compris dans les correctifs et évolutions.',
    'I', 58);
  putNote(run, 'B123',
    'Reprises des interfaces et rejets métier — 36 reprises de deux JH, communes aux trois solutions : rejeu des messages et contrôle de cohérence commande/stock. Hors incident de ressource, diagnostic applicatif, logistique physique et construction de connecteurs.',
    'I', 58);
  putNote(run, 'B126',
    'Fiabilité préventive et revue des flux — douze revues de deux JH sur les rejets récurrents, retards et contrôles d’exhaustivité. Une nouvelle fonction ou un nouveau connecteur relève des évolutions. Même fréquence et charge pour les trois solutions.',
    'I', 52);
  putNote(run, 'B129',
    'Pilotage du service — douze revues de trois JH : priorisation des problèmes, suivi des corrections, qualité de service et coordination produit ou éditeurs/intégrateur. Même charge pour les trois solutions. Le pilotage de réalisation des évolutions est compris dans leurs charges unitaires.',
    'I', 58);
  putNote(run, 'B132',
    'Procédures d’exploitation — douze revues de deux JH sur les accès d’exploitation, runbooks, contrôles et coordination du prestataire. Hors revue des paramètres applicatifs et gestion des demandes de changement. Même charge pour les trois solutions.',
    'I', 52);
  putNote(run, 'B135',
    'Sauvegardes techniques FLOW — douze contrôles/restaurations isolées de trois JH. Les ressources de sauvegarde sont facturées dans la plateforme. Pour les solutions SaaS, ces tâches techniques standard sont supposées incluses dans la souscription ; les exercices de reprise du service métier restent financés séparément dans les trois solutions.',
    'I', 64);
  putNote(run, 'B138',
    'Exercice de reprise du service métier — quatre exercices de cinq JH incluant dépendances, interfaces, contrôles fonctionnels et procédures. Même charge cliente pour les trois solutions. Hors tests techniques de sauvegarde, nouvelle architecture PRA, refonte du code et migration majeure.',
    'I', 58);
  putNote(run, 'B143',
    'Hypothèse commune : service humain en heures ouvrées, produit stabilisé, même panier annuel à périmètre déployé identique. Les tarifs et les activités propres au produit diffèrent. Le panier Buy couvre toutes les extensions prévues, y compris OMS et interfaces. Les forfaits RFI SAP sont conservés comme repères sourcés, sans les ajouter au panier.',
    'I', 64);

  // The common Buy service basket owns its unique corrections/tests assumptions.
  run.getRange('B145:I194').clear({ applyTo: 'all' });
  run.getRange('B145:I194').format.font = { name: font, size: 10, color: C.ink };
  run.getRange('B145:I194').format.wrapText = true;
  run.getRange('B145:I194').format.rowHeight = 36;
  band(run, 'B145:I145', 'SAP et Microsoft — maintenance et exploitation au même niveau de service');
  run.getRange('B147:I147').values = [['Activité', 'Quantité/an', 'JH/unité', 'JH/an', 'SAP €/JH', 'SAP €/an', 'Microsoft €/JH', 'Microsoft €/an']];
  band(run, 'B147:I147', null, true);
  run.getRange('B147:I147').format.rowHeight = 44;
  const maintenance = [
    [148, 'Diagnostic applicatif qualifié', 13],
    [149, 'Corrections de toutes les extensions et interfaces', null],
    [150, 'Tests et adaptation aux mises à jour standard', null],
    [151, 'Pilotage du service et coordination des fournisseurs', 22],
  ];
  const operations = [
    [155, 'Contrôle des alertes et du service', 12],
    [156, 'Rétablissement technique du service', 14],
    [157, 'Paramètres, sécurité et capacité applicative', 18],
    [158, 'Reprises des interfaces et rejets métier', 20],
    [159, 'Fiabilité préventive et revue des flux', 21],
    [160, 'Revues des procédures d’exploitation', 23],
    [161, 'Exercice de reprise du service métier', 25],
  ];
  for (const [row, label, owner] of [...maintenance, ...operations]) {
    set(run, 'B' + row, label);
    if (owner) {
      f(run, 'C' + row, `=IF(ISNUMBER(C${owner}),C${owner},NA())`);
      f(run, 'D' + row, `=IF(ISNUMBER(D${owner}),D${owner},NA())`);
    }
    f(run, 'E' + row, product(row));
    f(run, 'F' + row, "='Prix unitaire SAP'!$D$31");
    f(run, 'G' + row, `=E${row}*F${row}`);
    f(run, 'H' + row, "='Prix unitaire Microsoft'!$D$31");
    f(run, 'I' + row, `=E${row}*H${row}`);
  }
  unit(run, 'C149', 30, '0 "correctifs/an"');
  unit(run, 'D149', 3);
  unit(run, 'C150', 4, '0 "campagnes/an"');
  unit(run, 'D150', 15);
  band(run, 'B154:I154', 'Exploitation — interventions humaines clientes');
  for (const [row, label, first, last] of [
    [152, 'Maintenance et pilotage Buy', 148, 151],
    [162, 'Exploitation Buy', 155, 161],
  ]) {
    set(run, 'B' + row, label);
    for (const col of ['E', 'G', 'I']) f(run, col + row, `=SUM(${col}${first}:${col}${last})`);
    total(run, `B${row}:I${row}`);
  }
  set(run, 'B164', 'Maintenance et exploitation Buy');
  for (const col of ['E', 'G', 'I']) f(run, col + 164, `=SUM(${col}152,${col}162)`);
  total(run, 'B164:I164');
  note(run, 'B166', 'Toutes les quantités communes renvoient au panier FLOW. Le Buy finance le diagnostic, ses extensions, les tests clients et le pilotage. Corrections standard, administration du runtime et sauvegardes techniques standard sont supposées comprises dans les souscriptions. Aucun pourcentage de maintenance supplémentaire.', 'I', 60);
  note(run, 'B168', 'Les 30 corrections Buy couvrent le patrimoine complet de la cible : extensions RFI et compléments OMS/interfaces. Les 240 diagnostics sont conservés pour les trois solutions. Ce panier est une hypothèse d’ingénierie comparable ; il ne décrit pas un engagement des fournisseurs.', 'I', 54);

  // All three evolution baskets share demand volumes, with explicit per-solution effort.
  band(run, 'B170:I170', 'Évolutions — même panier de besoins, efforts propres à chaque solution');
  run.getRange('B171:I171').values = [['Changement', 'Nombre/an', 'FLOW JH/unité', 'FLOW €/an', 'SAP JH/unité', 'SAP €/an', 'Microsoft JH/unité', 'Microsoft €/an']];
  band(run, 'B171:I171', null, true);
  run.getRange('B171:I171').format.rowHeight = 44;
  for (const [row, owner, label, sapEffort, msEffort] of [
    [172, 33, 'Règles et configuration', 3.5, 3],
    [173, 34, 'Fonctions ou API', 14, 16],
    [174, 35, 'Évolutions structurantes / versions fonctionnelles', 35, 40],
  ]) {
    set(run, 'B' + row, label);
    f(run, 'C' + row, `=IF(ISNUMBER(C${owner}),C${owner},NA())`);
    f(run, 'D' + row, `=IF(ISNUMBER(D${owner}),D${owner},NA())`);
    f(run, 'E' + row, `=G${owner}`);
    unit(run, 'F' + row, sapEffort);
    unit(run, 'H' + row, msEffort);
    for (const [costCol, effortCol, priceSheet] of [['G', 'F', 'Prix unitaire SAP'], ['I', 'H', 'Prix unitaire Microsoft']]) {
      const rate = `'${priceSheet}'!$D$35`;
      f(run, costCol + row, `=IF(AND(COUNT(C${row},${effortCol}${row},${rate})=${three},MIN(C${row},${effortCol}${row},${rate})>=${zero}),C${row}*${effortCol}${row}*${rate},NA())`);
    }
  }
  set(run, 'B175', 'Total évolutions : JH/an et €/an');
  for (const effortCol of ['D', 'F', 'H']) {
    f(run, effortCol + 175, `=IF(AND(COUNT(C172:C174,${effortCol}172:${effortCol}174)=${three}*${two},MIN(C172:C174,${effortCol}172:${effortCol}174)>=${zero}),SUMPRODUCT(C172:C174,${effortCol}172:${effortCol}174),NA())`);
  }
  for (const col of ['E', 'G', 'I']) f(run, col + 175, `=SUM(${col}172:${col}174)`);
  total(run, 'B175:I175');
  note(run, 'B177', 'Hypothèses d’effort, pas mesures du RFI. Les charges de chaque évolution incluent analyse, réalisation, tests ciblés, documentation et pilotage de réalisation. Les campagnes transverses de maintenance sont séparées. Les versions fonctionnelles FLOW sont dans ce total, sans ajout au budget.', 'I', 58);
  band(run, 'B180:I180', 'Repères RFI SAP — comparaison documentaire, non ajoutée au nominal');
  run.getRange('B181:I181').values = [['Service', 'RFI €/an', '', '', '', 'Panier SAP €/an', '', 'Écart €/an']];
  band(run, 'B181:I181', null, true);
  for (const [row, label, source, calc] of [
    [182, 'Maintenance applicative', 'C81', 'G152'],
    [183, 'Supervision en horaires étendus', 'C82', 'G162'],
    [184, 'Évolutions / TMA', 'C83', 'G175'],
  ]) {
    set(run, 'B' + row, label);
    f(run, 'C' + row, `='Références'!${source}`);
    f(run, 'G' + row, `=${calc}`);
    f(run, 'I' + row, `=G${row}-C${row}`);
  }
  note(run, 'B186', 'Source : proposition Delaware, septembre 2025, p. 37. Les 250 / 450 / 350 k€ restent intacts dans Références. La supervision RFI porte sur des horaires étendus ; le nominal ci-dessus est en heures ouvrées. Les volumes du forfait ne sont pas connus : aucune conversion fictive du devis en effectifs ni réduction au prorata horaire.', 'I', 66);
  note(run, 'B189', 'Les tâches SaaS supposées incluses concernent la plateforme et le produit standard. Les interventions clientes sur les données, interfaces, extensions et reprise métier restent financées. La couverture des services managés devra être confirmée dans une proposition commerciale ; le modèle affiche une hypothèse commune de comparaison.', 'I', 60);
  note(run, 'B192', 'Astreinte, migrations majeures et appui interne : exclus du nominal. Les options de cette feuille restent désactivées. Une couverture humaine étendue devrait être chiffrée pour chaque solution avant comparaison ; le forfait SAP 450 k€ ne sert pas de proxy Microsoft.', 'I', 54);
  for (const range of ['E148:E164', 'D175', 'F175', 'H175']) run.getRange(range).setNumberFormat(fmtJH);
  for (const range of ['D148:D161', 'D172:D174', 'F172:F174', 'H172:H174']) run.getRange(range).setNumberFormat('0.00 "JH/unité"');
  for (const range of ['C148:C161', 'C172:C174']) run.getRange(range).setNumberFormat('0 "unités/an"');
  for (const range of ['F148:F161', 'H148:H161']) run.getRange(range).setNumberFormat(fmtRate);
  for (const range of ['G148:G164', 'I148:I164', 'E172:E175', 'G172:G175', 'I172:I175', 'C182:C184', 'G182:G184', 'I182:I184']) run.getRange(range).setNumberFormat(fmtEuro);
  borders(run, 'B147:I164'); borders(run, 'B171:I175'); borders(run, 'B181:I184');

  // Price sheets retain tariffs and useful source references, not duplicate editable baskets.
  set(uf, 'B26', 'Maintenance et exploitation annuelles');
  set(uf, 'B30', 'Maintenance et exploitation : JH/an');
  set(uf, 'B31', 'Maintenance et exploitation : €/JH');
  set(uf, 'B32', 'Forfait annuel supplémentaire');
  set(uf, 'H30', 'Panier unique de service annuel, lignes 12 à 25.');
  set(uf, 'H32', 'Aucun forfait supplémentaire dans le nominal.');
  for (const [u, costCol, effortCol] of [[sap, 'G', 'F'], [ms, 'I', 'H']]) {
    set(u, 'B25', 'Prestations récurrentes — renvois au service annuel');
    set(u, 'B26', 'Maintenance et pilotage annuels');
    set(u, 'B27', 'Évolutions annuelles');
    set(u, 'B28', 'Forfait évolutions supplémentaire');
    set(u, 'B30', 'Maintenance et pilotage : JH/an');
    set(u, 'B31', 'Prestations spécialisées : €/JH');
    set(u, 'B32', 'Forfait maintenance supplémentaire');
    set(u, 'B33', 'Exploitation humaine annuelle');
    set(u, 'B34', 'Évolutions : JH/an');
    set(u, 'B45', 'Prix des ressources techniques');
    link(u, 'D26', costCol + 152);
    link(u, 'D27', costCol + 175);
    f(u, 'D28', `=${zero}`);
    link(u, 'D30', 'E152');
    f(u, 'D32', `=${zero}`);
    link(u, 'D33', costCol + 162);
    link(u, 'D34', effortCol + 175);
    set(u, 'H26', 'Diagnostic, corrections spécifiques, tests clients et pilotage.');
    set(u, 'H28', 'Aucun forfait ajouté au panier d’évolutions.');
    set(u, 'H30', 'Panier complet : toutes extensions et interfaces de la cible.');
    set(u, 'H32', 'Aucun forfait ajouté au panier de maintenance.');
    set(u, 'H33', 'Mêmes volumes de service en heures ouvrées, calculés en JH.');
    set(u, 'H34', 'Même demande métier que FLOW ; efforts propres à la solution.');
    set(u, 'H45', 'Les prestations d’exploitation utilisent l’inflation France D43.');
    putNote(u, 'B40', 'Nominal issu du panier commun en heures ouvrées. Le produit standard et sa plateforme SaaS sont supposés couverts par la souscription. Les prestations clientes restent chiffrées. Forfaits RFI conservés en références, aucun supplément automatique de maintenance des compléments.', 'H', 64);
    putNote(u, 'B72', 'Tarifs dans cet onglet. Quantités et efforts annuels dans Service annuel. Ressources techniques dans Plateformes et sortie.', 'H', 40);
    // Existing result schedules keep exactly the same month/year timing.
    for (let r = 52; r <= 66; r++) {
      f(u, 'H' + r, `=($D$26*$D$39+$D$33)*(${one}+$D$43)^(B${r}-${one})`);
    }
    // Historical percentage-based supplements are removed from the active model.
    for (const r of [134, 135, 136]) {
      f(u, 'D' + r, `=${zero}`);
      u.getRange('D' + r).format.fill = C.pale;
    }
    set(u, 'B134', 'Supplément de maintenance OMS');
    set(u, 'B135', 'Supplément de maintenance interfaces');
    set(u, 'B136', 'Supplément annuel retenu');
    set(u, 'H134', 'Compris dans le panier unique de corrections.');
    set(u, 'H135', 'Compris dans le panier unique de corrections.');
    putNote(u, 'B138', 'Toutes les extensions RFI et les compléments fonctionnels sont dans le même panier annuel de corrections. Aucun supplément proportionnel aux JH de construction. Les évolutions produisent une capacité nouvelle ; la maintenance rétablit le service existant.', 'H', 54);
    for (let i = 0; i < 3; i++) {
      const row = 95 + i, owner = 172 + i;
      numericLink(u, 'C' + row, 'C' + owner);
      numericLink(u, 'D' + row, effortCol + owner);
      f(u, 'E' + row, `=C${row}*D${row}`);
      link(u, 'G' + row, costCol + owner);
    }
    link(u, 'E99', effortCol + 175);
    link(u, 'G99', costCol + 175);
    putNote(u, 'B101', 'Renvois du panier unique Service annuel : quantités de besoins communes, efforts unitaires propres à chaque solution. Ces lignes ne constituent pas un second budget.', 'H', 44);
    u.getRange('C95:D97').format.fill = '#FFFFFF';
    u.getRange('D30').setNumberFormat(fmtJH);
    u.getRange('D26:D28').setNumberFormat(fmtEuro);
    u.getRange('D32:D33').setNumberFormat(fmtEuro);
    u.getRange('D34').setNumberFormat(fmtJH);
  }
  set(sap, 'B74', 'Références RFI SAP — non ajoutées au nominal');
  set(sap, 'E75', 'Référence €/an');
  for (const r of [76, 77, 78]) set(sap, 'H' + r, 'Source fournisseur conservée. Le nominal est calculé dans Service annuel.');
  putNote(sap, 'B80', 'Forfaits source conservés : 250 k€ maintenance, 350 k€ évolutions et 450 k€ supervision en horaires étendus. Leur contenu détaillé n’est pas connu. Ils servent de repères, sans remplacer ni compléter le panier commun en heures ouvrées.', 'H', 54);
  putNote(sap, 'B82', 'Le nominal évolutions est le panier de besoins commun, valorisé aux efforts SAP. Le forfait RFI de 350 k€ reste une référence documentaire ; aucun maximum ni cumul avec ce forfait.', 'H', 44);
  putNote(sap, 'B84', 'Licences RISE et infrastructure sont décrites ensemble dans l’offre. La supervision RFI de 450 k€ porte sur des prestations humaines en horaires étendus. Le nominal retient le service commun en heures ouvrées.', 'H', 44);
  putNote(sap, 'B86', 'La migration majeure S/4 reste une option désactivée dans Service annuel. Les charges courantes se lisent dans le panier unique de maintenance, exploitation et évolutions.', 'H', 42);

  // Replace Microsoft's formerly independent MCO inputs with links to shared owners.
  set(ms, 'B74', 'Maintenance et pilotage — renvois au panier de service');
  for (const [row, owner, label] of [
    [76, 148, 'Diagnostic applicatif qualifié'],
    [77, 149, 'Corrections de toutes les extensions et interfaces'],
    [78, 150, 'Tests et adaptation aux mises à jour'],
    [79, 151, 'Pilotage du service et coordination'],
  ]) {
    set(ms, 'B' + row, label);
    for (const col of ['C', 'D', 'E']) numericLink(ms, col + row, col + owner);
    link(ms, 'F' + row, 'H' + owner);
    link(ms, 'G' + row, 'I' + owner);
    set(ms, 'H' + row, 'Hypothèse du service annuel');
  }
  ms.getRange('B80:H80').clear({ applyTo: 'all' });
  link(ms, 'E83', 'E152');
  link(ms, 'G83', 'I152');
  set(ms, 'B83', 'Maintenance et pilotage annuels');
  ms.getRange('C76:D79').format.fill = '#FFFFFF';
  putNote(ms, 'B85', 'Les quantités communes de diagnostics et de service sont pilotées dans Service annuel. Le code standard est maintenu par l’éditeur dans la souscription.', 'H', 42);
  putNote(ms, 'B86', 'Le panier unique de 30 corrections/an couvre les extensions RFI et les nouveaux compléments OMS/interfaces. Aucun supplément en pourcentage de la construction.', 'H', 42);
  putNote(ms, 'B87', 'Quatre campagnes de non-régression par an : hypothèse de charge cliente, modifiable dans Service annuel. Ce n’est pas un calendrier Microsoft affirmé.', 'H', 42);
  putNote(ms, 'B88', 'Pilotage et coordination : même fréquence et même charge que FLOW et SAP. Unified/PQA reste une souscription fournisseur distincte.', 'H', 42);
  putNote(ms, 'B89', 'Les revues de paramètres et de sécurité appartiennent à l’exploitation. Elles ne sont pas également ajoutées à la maintenance.', 'H', 42);
  set(ms, 'B103', 'Exploitation — référence au panier de service');
  set(ms, 'B104', 'Charge d’exploitation annuelle');
  link(ms, 'D104', 'E162');
  ms.getRange('D104').setNumberFormat(fmtJH);
  set(ms, 'H104', 'Activités et quantités communes, en heures ouvrées.');
  set(ms, 'B105', 'Tarif des interventions');
  f(ms, 'D105', '=$D$31');
  ms.getRange('D105').setNumberFormat(fmtRate);
  set(ms, 'H105', 'Tarif de prestation spécialisée française.');
  set(ms, 'B106', 'Exploitation annuelle calculée');
  link(ms, 'D106', 'I162');
  ms.getRange('D106').setNumberFormat(fmtEuro);
  putNote(ms, 'B108', 'Le proxy SAP de 450 k€ est retiré. Les interventions clientes sont calculées en quantité × JH × tarif dans Service annuel. La souscription conserve la maintenance et l’hébergement du standard ; les tâches clientes de reprise métier et d’interface restent financées.', 'H', 54);
  return {
    sheet: 'Run Flow',
    lastRow: 194,
    flow: { maintenanceAndOperationsJH: 726, maintenanceAndOperationsEUR: 544500, evolutionsJH: 320, evolutionsEUR: 240000 },
    sap: { maintenanceJH: 306, operationsJH: 234, maintenanceAndOperationsEUR: 459000, evolutionsJH: 420, evolutionsEUR: 357000 },
    microsoft: { maintenanceJH: 306, operationsJH: 234, maintenanceAndOperationsEUR: 459000, evolutionsJH: 440, evolutionsEUR: 374000 },
  };
}

// Keep the supplier's SAP evidence as the active budget. Microsoft has no
// equivalent quoted service forfait; its explicit activity estimate stays active.
export function applySourcedSapBase(ctx) {
  const {S,set,f,note,band,total,fmtEuro}=ctx;
  const run=S['Run Flow'],sap=S['Prix unitaire SAP'],ms=S['Prix unitaire Microsoft'];
  const zero="'Paramètres'!$D$18";
  for(const [cell,text] of Object.entries({
    B64:'FLOW et Microsoft : 240 diagnostics/an estimés, sans gain de prévention déduit. SAP : forfait fournisseur ; nombre de diagnostics non documenté.',
    B143:'Bases retenues : SAP = forfaits Delaware sourcés ; Microsoft = activités estimées en heures ouvrées. Les niveaux de service ne sont pas démontrés équivalents. Aucune économie de renégociation SAP n’est supposée.',
    B166:'Microsoft : les volumes et efforts ci-dessus sont des hypothèses d’ingénierie en France. Le standard est supposé maintenu dans la souscription ; les tâches clientes sont financées ici. Aucun forfait SAP n’est transposé.',
    B168:'Microsoft : 30 correctifs/an pour toutes les extensions et interfaces, y compris les compléments OMS. Capacité supposée suffisante, non mesurée. SAP : périmètre des extensions couvert par le forfait à confirmer ; aucun supplément automatique.',
    B177:'FLOW et Microsoft : même demande estimée (règles, fonctions, changements structurants), efforts propres à chaque solution. SAP : enveloppe fournisseur de TMA ; le nombre de changements financés n’est pas connu. Aucun panier en JH n’est ajouté au forfait.',
    B186:'Source SAP : Delaware, septembre 2025, p. 37 ; questionnaire onglet 8, lignes 13–15. MCO hors évolutions, monitoring en horaires étendus, TMA : trois forfaits distincts. Aucun double compte source démontré. Montants intacts dans Références, utilisés dans le calcul.',
    B189:'Le standard SaaS et son hébergement sont inclus selon les offres ; les responsabilités exactes restent à confirmer. Les quantités Microsoft sont des hypothèses ; les volumes des forfaits SAP ne sont pas documentés. Les compléments OMS SAP ne justifient pas un supplément forfaitaire arbitraire.',
    B192:'Le monitoring SAP en horaires étendus reste financé. FLOW et Microsoft : hypothèses en heures ouvrées, sans astreinte ajoutée. Migrations majeures et appui interne exclus. La comparaison ne garantit pas un service identique.',
  })) note(run,cell,text,'I',60);
  for(const r of [99,102,105,108,117,120,123,126,129,132,135,138]){
    const a='B'+r;
    let text=run.getRange(a).values[0][0];
    text=text.replaceAll('les trois solutions','FLOW et Microsoft').replaceAll('les trois options','FLOW et Microsoft')
      .replaceAll('Les solutions Buy retiennent','Microsoft retient').replaceAll('Buy : quatre','Microsoft : quatre')
      .replaceAll('communes aux trois solutions','estimées pour FLOW et Microsoft');
    set(run,a,text+' SAP : capacité définie par les forfaits fournisseur, non détaillée ici.');
    run.getRange(`${a}:I${r}`).format.rowHeight=78;
  }
  band(run,'B145:I145','Services annuels — SAP sourcé, Microsoft estimé');
  set(run,'F147','SAP : forfait'); set(run,'G147','SAP €/an');
  for(const r of [148,149,150,151,155,156,157,158,159,160,161]){
    run.getRange(`F${r}:G${r}`).clear({applyTo:'all'});
  }
  set(run,'B152','Maintenance et pilotage');
  set(run,'B162','Exploitation / supervision');
  set(run,'B164','Maintenance et exploitation');
  for(const [r,src] of [[152,'C81'],[162,'C82']]){
    set(run,'F'+r,'Forfait RFI');
    f(run,'G'+r,`=IF(ISNUMBER('Références'!${src}),'Références'!${src},NA())`);
  }
  f(run,'G164','=SUM(G152,G162)');
  band(run,'B170:I170','Évolutions — FLOW/Microsoft estimés ; SAP au forfait');
  set(run,'F171','SAP : forfait');
  for(const r of [172,173,174])run.getRange(`F${r}:G${r}`).clear({applyTo:'all'});
  set(run,'F175','Forfait RFI');
  f(run,'G175',"=IF(ISNUMBER('Références'!C83),'Références'!C83,NA())");
  band(run,'B180:I180','SAP — forfaits fournisseur retenus dans le budget');
  for(const r of [145,170,180])run.getRange(`B${r}:I${r}`).merge();
  set(run,'G181','Retenu €/an');set(run,'I181','Ajustement');
  // Existing G182:G184 link to the active service totals. I shows zero adjustment.
  set(sap,'B30','Charge MCO : non détaillée');
  set(sap,'D30','Non détaillée');
  set(sap,'H30','Le forfait sourcé est utilisé directement, sans conversion fictive en JH.');
  set(sap,'B34','Charge évolutions : non détaillée');set(sap,'D34','Non détaillée');
  set(sap,'H34','Enveloppe TMA fournisseur ; capacité en changements non documentée.');
  set(sap,'B32','Supplément MCO retenu');
  set(sap,'B31','Tarif hors forfait / options');
  set(sap,'H31','Repère France pour prestations hors forfait ; sans effet sur les forfaits source.');
  set(sap,'B35','Repère évolution hors forfait');
  set(sap,'H35','Non utilisé pour valoriser la TMA : enveloppe source conservée.');
  set(sap,'B36','Migration majeure — coût si activée');
  set(sap,'H28','Aucun supplément à la TMA source.');
  set(sap,'H32','Aucun supplément au MCO source ; couverture OMS à confirmer.');
  set(sap,'H43','0 % retenu sur les forfaits ; indexation contractuelle inconnue.');
  set(sap,'H26','250 k€/an : forfait MCO Delaware hors évolutions.');
  set(sap,'H27','350 k€/an : enveloppe TMA Delaware.');
  set(sap,'H33','450 k€/an : monitoring des flux en horaires étendus.');
  note(sap,'B40','Base SAP : forfaits MCO, supervision et évolutions Delaware, sans réduction ni ajout du panier Microsoft. Le prorata livré et l’inflation France restent des conventions de projection. Couverture des compléments OMS à confirmer.','H',60);
  // Remove the abandoned SAP activity basket; preserve the source reference links.
  sap.getRange('B74:H101').unmerge();
  sap.getRange('B74:H101').clear({applyTo:'all'});
  band(sap,'B74:H74','Services SAP — source fournisseur, année pleine');
  for(const [r,label,owner] of [[76,'MCO hors évolutions','D26'],[77,'Monitoring des flux — horaires étendus','D33'],[78,'Évolutions / TMA','D27']]){
    note(sap,'B'+r,label,'C',38);f(sap,'D'+r,'='+owner);
    sap.getRange('D'+r).setNumberFormat(fmtEuro);
    note(sap,'E'+r,'Delaware septembre 2025, p. 37 ; Références C81:C83.','H',38);
  }
  note(sap,'B80','Les forfaits sont distincts. Aucun double compte source n’est démontré. Les quantités de service ne sont pas documentées ; aucune baisse de prix ni normalisation horaire n’est appliquée.','H',60);
  note(sap,'B83','Les forfaits ne sont pas cumulés avec un abaque de maintenance. Les compléments OMS/interfaces sont financés en réalisation initiale ; leur couverture en maintenance reste une hypothèse à confirmer. Aucun pourcentage automatique ajouté.','H',60);
  note(sap,'B86','Migrations majeures futures : option désactivée. Le monitoring source en horaires étendus reste dans le budget ; il ne constitue pas une preuve de couverture 24/7.','H',52);
  note(sap,'B138','Aucun supplément proportionnel aux JH initiaux. Maintien des forfaits fournisseur ; couverture exacte des extensions et des nouveaux compléments OMS à confirmer. Une absence de supplément ne prouve pas leur gratuité.','H',58);
  set(sap,'H134','Couverture non détaillée ; pas de supplément arbitraire.');
  set(sap,'H135','Couverture non détaillée ; pas de supplément arbitraire.');
  note(ms,'B40','Estimation Microsoft en heures ouvrées : 306 JH de maintenance, 234 JH d’exploitation, 440 JH d’évolutions. Hypothèses à 850 €/JH, sans devis de service ni transposition des forfaits SAP.','H',60);
  note(ms,'B85','240 diagnostics × 0,5 JH : hypothèse commune avec FLOW. Le nombre réel de demandes Microsoft est inconnu ; il reste modifiable dans Service annuel.','H',48);
  note(ms,'B86','30 correctifs × 3 JH : hypothèse couvrant toutes les extensions/interfaces, compléments OMS compris. La maintenance du code standard relève de la souscription ; ne pas ajouter de pourcentage MCO.','H',52);
  note(ms,'B88','12 revues × 3 JH : hypothèse de coordination du service, distincte du pilotage inclus dans chaque évolution. Unified/PQA reste une souscription fournisseur distincte.','H',48);
  note(ms,'B108','198,9 k€/an = 234 JH estimés × 850 €/JH. Les quantités ne sont pas mesurées chez Beaumanoir. Les anciens 450 k€ étaient une transposition SAP, pas un prix Microsoft : l’écart ne représente pas une économie négociée.','H',64);
  note(S['Prix SAP'],'B34','Fonctionnement SAP : 250 k€ MCO + 450 k€ supervision en horaires étendus + 350 k€ évolutions par an, hors abonnements. Forfaits Delaware conservés ; volumes et couverture des compléments à confirmer.','H',58);
  note(S['Prix Microsoft'],'B34','Fonctionnement Microsoft : hypothèses en heures ouvrées, par activité dans Service annuel. 260,1 k€ maintenance + 198,9 k€ exploitation + 374 k€ évolutions. Aucun forfait SAP transposé.','H',58);
  const comp=S['Comparaison'];
  note(comp,'B13','SAP : forfaits RFI, supervision en horaires étendus. FLOW / Microsoft : hypothèses en heures ouvrées. Niveaux de service non démontrés équivalents.','I',38);
  note(comp,'B84','SAP conserve ses forfaits fournisseur. Microsoft repose sur des volumes estimés. Les écarts de coûts ne démontrent ni une remise commerciale ni une prestation identique.','I',42);
  note(comp,'B88','Options inactives et contributions internes exclues. SAP : couverture des compléments OMS à confirmer. Microsoft : capacité annuelle et couverture SaaS supposées.','I',42);
}
