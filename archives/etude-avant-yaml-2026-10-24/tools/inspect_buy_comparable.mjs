import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
const require=createRequire('C:/Users/laure/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {FileBlob,SpreadsheetFile}=require('@oai/artifact-tool');
const dir='outputs/01a1530f-f378-7fd1-9654-468c9b2141b6';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(`${dir}/FLOW_Make_abaques_et_prix_France_v4.xlsx`));
for(const [sheet,range,key]of [
 ['Comparaison','B1:I39','comparaison_achat'],
 ['Comparaison','B41:I88','comparaison_detail'],
 ['Plateforme et exploitation','B1:H42','plateforme_flow'],
 ['Run Flow','B1:I49','run_flow'],
 ['Run Flow','B52:I95','run_options'],
 ['Run Flow','B97:I143','run_justifications'],
 ['Plateforme et exploitation','B44:H90','plateforme_buy'],
 ['Structure coûts','B1:H80','structure_couts'],
 ['Trajectoire mensuelle','B193:F198','jalons'],
 ['Passage Buy France','B6:K43','pont_sap'],
 ['Passage Buy France','B56:K93','pont_ms'],
 ['Prix unitaire SAP','B113:H153','france_sap'],
 ['Prix unitaire Microsoft','B113:H153','france_ms'],
 ['Prix SAP','B1:H87','synthese_sap'],
 ['Prix Microsoft','B1:H87','synthese_ms'],
 ['Prix Flow','B1:H70','core_flow'],
 ['Prix SAP','B7:D12','prix_sap_titre'],
 ['Passage Buy France','B113:K122','ms_standard'],
 ['Passage Buy France','B123:K130','ms_fonctions'],
 ['Passage Buy France','B140:K148','ms_hypotheses'],
 ['Passage Buy France','B153:K163','sap_standard'],
 ['Passage Buy France','B164:K171','sap_fonctions'],
 ['Passage Buy France','B180:K186','sap_hypotheses']
 ,['Prix Flow','B1:H70','flow_decision']
 ,['Prix SAP','B1:H87','sap_decision']
 ,['Prix Microsoft','B1:H87','ms_decision']
 ,['Prix unitaire Flow','B1:H103','unitaire_flow']
 ,['Prix unitaire SAP','B1:H48','unitaire_sap']
 ,['Prix unitaire Microsoft','B1:H48','unitaire_ms']
 ,['Charges Flow','B1:I27','charges_vue']
 ,['Calculs 15 ans','B26:R44','calculs_vue']
 ,['Licences mensuelles','B1:L16','licences_vue']
 ,['Références','B14:H23','references_vue']
 ,['Sources','B21:D36','sources_vue']
 ,['Prix unitaire Flow','B93:H103','versions_core']
 ,['Paramètres','B1:F55','parametres']
 ,['Coûts techniques mensuels','B1:O17','technique_mensuel']
 ,['Charges Flow','B28:I52','charges_detail']
]){
 if(process.argv.length>2&&!process.argv.slice(2).includes(key))continue;
 const blob=await wb.render({sheetName:sheet,range,scale:1,format:'png'});
 await fs.writeFile(`${dir}/preview_${key}.png`,new Uint8Array(await blob.arrayBuffer()));
}
for(const n of ['Prix Flow','Prix SAP','Prix Microsoft']){
 const s=wb.worksheets.getItem(n),c=a=>s.getRange(a).values[0][0];
 console.log(JSON.stringify({sheet:n,base:c('D7'),france:c('D8'),comparable:c('D9'),initial:c('D12'),tco3:wb.worksheets.getItem('Comparaison').getRange('F'+(n==='Prix Flow'?9:n==='Prix SAP'?10:11)).values[0][0],tco5:c('H7'),tco10:c('H8'),tco15:c('H9')}));
}
