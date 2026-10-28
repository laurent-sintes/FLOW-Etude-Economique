export async function applyAuditRevision({fs,SpreadsheetFile,FileBlob,outPath,outDir,require}){
 const backup='tmp/FLOW_before_service_audit.xlsx';
 try{await fs.access(backup);}catch{await fs.copyFile(outPath,backup);}
 const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(backup));
 console.log('STAGE imported');
 if(process.argv.includes('--help-service')){
  console.log(wb.help('worksheet.name',{include:'index,examples,notes',maxChars:2500}).ndjson);
  return;
 }
 const S=Object.fromEntries(wb.worksheets.items.map(s=>[s.name,s]));
 const C={navy:'#1A324A',ink:'#263746',muted:'#64788A',line:'#D9E2E8',pale:'#EAF0F4',flow:'#5953FF',sap:'#203850',ms:'#C98719',input:'#FFF1D3',blue:'#514BC7',green:'#1E6A55',red:'#B83A3A'},font='Arial';
 const fmtJH='#,##0 "JH"',fmtPct='0.0%',fmtEuro='#,##0 "€"',fmtRate='#,##0 "€/JH"';
 const set=(s,a,v)=>s.getRange(a).values=[[v]];
 const f=(s,a,v)=>{s.getRange(a).formulas=[[v]];s.getRange(a).format.fill=C.pale;s.getRange(a).format.font={name:font,size:10,color:v.includes('!')?C.green:C.ink};};
 const inp=(s,a,fmt,min=0,max=100000000,type='decimal')=>{s.getRange(a).format.fill=C.input;s.getRange(a).format.font={name:font,size:10,color:C.blue};if(fmt)s.getRange(a).setNumberFormat(fmt);s.getRange(a).dataValidation={rule:{type,operator:'between',formula1:min,formula2:max}};};
 const band=(s,a,t,head=false)=>{s.getRange(a).format={fill:head?C.navy:C.pale,font:{name:font,size:10,bold:true,color:head?'#FFFFFF':C.navy},rowHeight:head?36:28,verticalAlignment:'center',wrapText:true};if(t)set(s,a.split(':')[0],t);};
 const note=(s,a,t,last='H',height=44)=>{const r=a.match(/\d+/)[0],range=s.getRange(`${a}:${last}${r}`);range.unmerge();range.merge();set(s,a,t);range.format={font:{name:font,size:10,color:C.muted},rowHeight:height,wrapText:true,verticalAlignment:'center'};};
 const borders=(s,a)=>s.getRange(a).format.borders={insideHorizontal:{style:'thin',color:C.line}};
 const total=(s,a)=>s.getRange(a).format={fill:'#EFEEFF',font:{name:font,size:10,bold:true,color:C.navy},rowHeight:30};
 const ctx={wb,S,set,f,inp,band,note,borders,total,C,font,fmtJH,fmtPct,fmtEuro,fmtRate,formulaRegistry:new Map(),inputRegistry:new Set()};
 const {applyAbaqueCorrections}=await import('./flow_abaque_corrections.mjs');
 const {applyServiceCorrections}=await import('./flow_service_corrections.mjs');
 await applyAbaqueCorrections(ctx);
 console.log('STAGE abaques');
 await applyServiceCorrections(ctx);
 console.log('STAGE services');
 const comp=S['Comparaison'],calc=S['Calculs 15 ans'],units=['Prix unitaire Flow','Prix unitaire SAP','Prix unitaire Microsoft'];
 // Human operations use the France services inflation; resources retain their own index.
 for(const start of [29,50])for(let y=1;y<=15;y++){
  const a='F'+(start+y),old=calc.getRange(a).formulas[0][0];
  f(calc,a,old.replaceAll('$D$45','$D$43'));
 }
 // Functional Core upgrades are included in the comparable evolution basket.
 for(const col of ['E','F','G','H','I'])for(const row of [44,62]){
  const old=comp.getRange(col+row).formulas[0][0];
  f(comp,col+row,old.replace(/[+-]SUM\('Calculs 15 ans'!T\d+:T\d+\)/g,''));
 }
 set(comp,'B44','Core system — création et entretien technique');
 set(comp,'B59','Maintenance applicative et pilotage');
 set(comp,'B62','Évolutions fonctionnelles, Core compris');
 set(comp,'B74','Exploitation et supervision');
 note(comp,'B13','Service commun en heures ouvrées • 240 diagnostics/an • Astreinte et migrations majeures exclues du nominal • Appui interne client exclu.','I',30);
 note(comp,'B14','Prestations et ressources : prix constants. Licences et CPI : +4 %/an après gel. Montants estimés ; gains métier non valorisés.','I',30);
 note(comp,'B84','Le panier Service annuel couvre maintenance, exploitation et évolutions. Les forfaits SAP du RFI restent des repères distincts ; aucun forfait de supervision SAP n’est appliqué à Microsoft.','I',42);
 note(comp,'B88','Les quantités sont communes lorsque le service est commun. FLOW finance son produit et son runtime ; le standard SaaS est entretenu dans les souscriptions Buy. Couverture SaaS retenue comme hypothèse.','I',42);
 for(const [idx,name] of ['Prix Flow','Prix SAP','Prix Microsoft'].entries()){
  const s=S[name];
  s.getRange('F6:H14').unmerge();s.getRange('F6:H14').clear({applyTo:'all'});
  band(s,'F6:H6','Repères du projet');
  set(s,'F7','Livraison finale');f(s,'H7',`=MAX(D21:D${idx===0?21:idx===1?23:25})`);s.getRange('H7').setNumberFormat('0 "mois"');
  set(s,'F8','Prix journalier');f(s,'H8',`='${units[idx]}'!${idx===0?'D20':'D8'}`);s.getRange('H8').setNumberFormat(fmtRate);
  note(s,'F10','Cumuls 3 / 5 / 10 / 15 ans : onglet Comparaison.','H',46);
  set(s,'F14','Contrôle des saisies');
  const zero="'Paramètres'!$D$18";
  f(s,'H14',`=IF(NOT(ISNUMBER(D12)),"À compléter",${idx===0?`IF(COUNTIF('Charges Flow'!I8:I21,"<>OK")>${zero},"Clés à corriger","Renseigné")`:'"Renseigné"'})`);
  s.getRange('F:F').format.columnWidth=23;s.getRange('H:H').format.columnWidth=23;s.getRange('F14:H14').format.rowHeight=34;
 }
 note(S['Prix SAP'],'B34','Nominal : activités annuelles estimées en heures ouvrées. Forfaits RFI de 250 / 450 / 350 k€ conservés dans Références ; ils ne sont pas additionnés au panier annuel.','H',52);
 note(S['Prix Microsoft'],'B34','Exploitation : panier commun en heures ouvrées, calculé par activité dans Service annuel. Maintenance des extensions et évolutions séparées. Le forfait SAP de supervision n’est plus utilisé.','H',52);
 for(const [name,cells] of [['Prix unitaire Flow',['B30','B31','B32']],['Prix unitaire SAP',['B30','B31','B32']],['Prix unitaire Microsoft',['B30','B31','B32']]]){
  const s=S[name],flow=name.endsWith('Flow');
  set(s,cells[0],flow?'Maintenance et exploitation : charge':'Maintenance applicative : charge');
  set(s,cells[1],'Prix journalier du service');
  set(s,cells[2],'Forfait ajouté au panier');
 }
 const structure=S['Structure coûts'];
 structure.getRange('C34:C46').setNumberFormat(fmtJH);
 for(const r of [22,25,28,31,48])structure.getRange('C'+r).setNumberFormat('0.00 "×"');
 structure.getRange('B46:H46').format.rowHeight=44;
 structure.getRange('B46').format.wrapText=true;
 const {applySourcedSapBase}=await import('./flow_service_corrections.mjs');
 applySourcedSapBase(ctx);
 const {applyMicrosoftServiceCalibration}=await import('./flow_ms_service_calibration.mjs');
 applyMicrosoftServiceCalibration(ctx);
 // Navigation links point to owning inputs, not copies of headline results.
 const nativeLinks=[];
 function link(s,a,target,label){
  // HYPERLINK is not calculated by this engine. Author the visible label here;
  // the export compatibility step adds an ordinary native Excel hyperlink.
  set(s,a,label);nativeLinks.push({sheet:s.name,cell:a,target,location:`'${target}'!B2`});
  s.getRange(a).format.font={name:font,size:10,color:C.blue,underline:'single'};s.getRange(a).format.fill='#FFFFFF';
 }
 // Documented rename is applied below; formulas and text are rewritten together.
 const renames=[['Run Flow','Service annuel'],['Plateforme et exploitation','Plateformes et sortie']];
 const snapshots=wb.worksheets.items.map(s=>{const used=s.getUsedRange(true);return {s,used,values:used.values,forms:used.formulas};});
 console.log('STAGE rename snapshots');
 const replaceNames=t=>renames.reduce((a,[oldName,newName])=>a.replaceAll(oldName,newName),t);
 for(const [oldName,newName]of renames){const target=S[oldName];target.name=newName;S[newName]=target;}
 for(const {s,used,values,forms}of snapshots){
  for(let r=0;r<values.length;r++){
   const row=forms[r]||[];
   if(row.some(x=>typeof x==='string'&&replaceNames(x)!==x)){
    // Batch each contiguous formula group; avoid reevaluating on individual reads.
    for(let c=0;c<row.length;){
     if(!row[c]){c++;continue;}
     const start=c,items=[];while(c<row.length&&row[c])items.push(replaceNames(row[c++]));
     used.getRangeByIndexes(r,start,1,items.length).formulas=[items];
    }
   }
   for(let c=0;c<(values[r]||[]).length;c++){
    const v=values[r][c];if(!row[c]&&typeof v==='string'&&replaceNames(v)!==v)used.getCell(r,c).values=[[replaceNames(v)]];
   }
  }
  console.log('STAGE renamed refs',s.name);
 }
 set(S['Service annuel'],'B2','Service annuel — maintenance, exploitation et évolutions');
 note(S['Service annuel'],'B4','SAP : forfaits fournisseur, monitoring en horaires étendus. FLOW / Microsoft : hypothèses par activité en heures ouvrées.','I',36);
 set(S['Plateformes et sortie'],'B2','Plateformes et sortie');
 for(const s of wb.worksheets.items)if(s.name!=='Comparaison')link(s,'B1','Comparaison','← Comparaison');
 comp.getRange('B86:I86').unmerge();comp.getRange('B86:I86').clear({applyTo:'all'});
 for(const [a,target,label]of [['B86','Service annuel','Service annuel →'],['D86','Passage Buy France','Compléments Buy →'],['F86','Plateformes et sortie','Plateformes →'],['H86','Références','Sources RFI →']])link(comp,a,target,label);
 // Output values have a common dark colour regardless of upstream sheet.
 comp.getRange('D9:I11').format.font={name:font,size:10,color:C.ink,bold:true};
 comp.getRange('D44:I82').format.font={name:font,size:10,color:C.ink};
 wb.recalculate();
 console.log('STAGE recalculated');
 const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:80},summary:'service audit final errors'});
 console.log('ERROR_SCAN',errors.ndjson);
 console.log('HEADLINES',JSON.stringify(comp.getRange('C9:I11').values));
 console.log('RUN',JSON.stringify(S['Service annuel'].getRange('B42:I49').values));
 await fs.writeFile('tmp/service_audit_results.json',JSON.stringify({headlines:comp.getRange('C9:I11').values,runYears:comp.getRange('D35:F37').values,run:S['Service annuel'].getRange('B42:I49').values,msServices:S['Prix unitaire Microsoft'].getRange('D26:D35').values,msSkills:S['Service annuel'].getRange('B301:I307').values},null,2));
 await fs.writeFile('tmp/flow_native_links.json',JSON.stringify(nativeLinks,null,2));
 const file=await SpreadsheetFile.exportXlsx(wb);await file.save(outPath);
 const {execFileSync}=require('node:child_process');
 console.log(execFileSync('C:/Users/laure/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',['tools/finalize_flow_chart_export.py',outPath,'tmp/flow_native_links.json'],{encoding:'utf8'}).trim());
 if(!process.argv.includes('--skip-preview')){
  const views=[['Comparaison','B1:I39'],['Comparaison','B41:I88'],['Prix Flow','B1:H39'],['Prix SAP','B1:H40'],['Prix Microsoft','B1:H40'],['Service annuel','B1:I49'],['Service annuel','B145:I194'],['Prix unitaire Flow','B24:H47'],['Prix unitaire SAP','B24:H47'],['Prix unitaire Microsoft','B24:H47'],['Passage Buy France','B190:K230'],['Passage Buy France','B231:K268'],['Structure coûts','B18:H48'],['Plateformes et sortie','B1:H42'],['Paramètres','B7:F39']];
  for(const [i,[sheetName,range]]of views.entries()){
   const img=await wb.render({sheetName,range,scale:1,format:'png'});
   await fs.writeFile(`${outDir}/audit_revision_${i}.png`,new Uint8Array(await img.arrayBuffer()));
  }
 }
 console.log('SAVED',outPath);
}
