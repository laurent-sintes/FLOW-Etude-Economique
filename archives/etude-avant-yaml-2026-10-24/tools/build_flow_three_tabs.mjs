import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
const require=createRequire('C:/Users/laure/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {Workbook,SpreadsheetFile}=require('@oai/artifact-tool');
const old=JSON.parse(await fs.readFile('tmp/three_tabs_source.json','utf8'));
const val=(sheet,cell)=>old[sheet][cell].v;
const out='outputs/01a1530f-f378-7fd1-9654-468c9b2141b6/FLOW_Make_abaques_et_prix_France_v4.xlsx';
const wb=Workbook.create();
const comp=wb.worksheets.add('Comparaison'), hyp=wb.worksheets.add('Hypothèses'), src=wb.worksheets.add('Sources');
const colors={ink:'#19344C',purple:'#6554FF',sap:'#354F68',ms:'#CD890A',pale:'#EFEDFF',grey:'#EDF2F6',muted:'#65788B',input:'#FFF2CE',blue:'#2854D9',green:'#08775F'};
const money='#,##0 "€";(#,##0) "€";"— €"', meur='0.00,, "M€";(0.00,,) "M€";"— M€"', annual='0.00,, "M€/an"';
const set=(s,a,v)=>s.getRange(a).values=[[v]];
// All numerical calculation conventions are visible cells too; no price,
// quantity, rate or technical numeric constant is embedded in a formula.
const f=(s,a,v)=>{v=v.split(/("(?:[^"]|"")*")/).map((part,i)=>i%2?part:part.replace(/(?<![A-Za-z0-9_$])(?:0|1|2)(?![A-Za-z0-9_.])/g,x=>x==='0'?"'Hypothèses'!$K$39":x==='1'?"'Hypothèses'!$K$40":"('Hypothèses'!$K$40+'Hypothèses'!$K$40)")).join('');s.getRange(a).formulas=[[v]];s.getRange(a).format.font.color=v.includes('!')?colors.green:colors.ink;};
const note=(s,r,t,last='I',height=34)=>{s.getRange(`B${r}:${last}${r}`).merge();set(s,`B${r}`,t);s.getRange(`B${r}:${last}${r}`).format={wrapText:true,rowHeight:height,font:{name:'Arial',size:10,color:colors.muted}};};
const band=(s,r,t,last='I')=>{s.getRange(`B${r}:${last}${r}`).merge();set(s,`B${r}`,t);s.getRange(`B${r}:${last}${r}`).format={fill:colors.ink,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:25};};
const header=(s,r,labels,start='B')=>{const col=start.charCodeAt(0)-65; const rg=s.getRangeByIndexes(r-1,col,1,labels.length);rg.values=[labels];rg.format={fill:colors.ink,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:40,horizontalAlignment:'center'};};
const input=(s,a,fmt=money,min=0,max=1e10)=>{s.getRange(a).format.fill=colors.input;s.getRange(a).format.font.color=colors.blue;s.getRange(a).setNumberFormat(fmt);s.getRange(a).dataValidation={rule:{type:'decimal',operator:'between',formula1:min,formula2:max}};};
const total=(s,r,last='I')=>{s.getRange(`B${r}:${last}${r}`).format.fill=colors.pale;s.getRange(`B${r}:${last}${r}`).format.font.bold=true;};
const logo='data:image/png;base64,'+(await fs.readFile('assets/exalt-logo.png')).toString('base64');
for(const [s,title,last,rows]of [[comp,'FLOW — Comparaison économique','I',99],[hyp,'FLOW — Hypothèses et calculs','M',239],[src,'FLOW — Sources et explications','I',188]]){
 s.showGridLines=false;s.getRange(`A1:${last}${rows}`).format={font:{name:'Arial',size:10,color:colors.ink},rowHeight:23,verticalAlignment:'center'};
 s.getRange('A:A').format.columnWidth=3;s.getRange('B:B').format.columnWidth=34;s.getRange(`C:${last}`).format.columnWidth=15;
 set(s,'B2',title);s.getRange('B2').format.font={name:'Arial',size:15,bold:true,color:colors.ink};
 s.getRange('B3:I3').format.borders={bottom:{style:'thin',color:colors.purple}};
 note(s,4,'Laurent Sintès · eXalt · 21 octobre 2026 · Coûts fournisseur HT', 'I',23);
 s.images.add({dataUrl:logo,anchor:{from:{row:0,col:7},extent:{widthPx:110,heightPx:48}}});
 s.tabColor=s===comp?colors.ink:s===hyp?colors.purple:'#B9C6CF';
}

// Sources are kept distinct from estimation choices and from the projection.
header(src,7,['Donnée RFI','Valeur','Unité','Pièce / portée']);src.getRange('E7:I7').merge();src.getRange('E:E').format.columnWidth=57;
const sourceRows=[
 [8,'SAP — maintenance',250000,'€/an','Delaware sept. 2025, PDF p.37 ; questionnaire onglet 8 C14.'],
 [9,'SAP — supervision',450000,'€/an','Même source, C13 : monitoring des flux en horaires étendus.'],
 [10,'SAP — évolutions',350000,'€/an','Même source, C15 : enveloppe, capacité non détaillée.'],
 [14,'SAP licences — année 1',790633,'€/an','Delaware PDF p.45 : panier brut Finance comprise, hors CPI.'],
 [15,'SAP licences — année 2',765823,'€/an','Même source.'],[16,'SAP licences — année 3',973480,'€/an','Même source.'],
 [17,'SAP licences — année 4',1270879,'€/an','Même source.'],[18,'SAP licences — année 5',1270879,'€/an','Même source ; panier reconduit après cinq ans par hypothèse.'],
 [20,'Écart Finance SAP',400000,'€/an','COPIL 5 : écart de panier ; retrait proportionnel estimé dans l’étude.'],
 [22,'Microsoft / K3 — panier',979001.51,'€/an','Questionnaire Microsoft / offre Avanade p.38 ; panier après remise.'],
 [23,'Unified / PQA — année 1',90000,'€','Questionnaire Microsoft C13.'],
 [24,'Unified — taux',0.075,'','Questionnaire Microsoft : taux du Product Spend.'],
 [25,'Unified — minimum',50000,'USD/an','Questionnaire Microsoft ; conversion budgétaire dans Hypothèses.'],
 [27,'SAP projet RFI',13462352,'€','Delaware PDF p.38 : coût externe exact, périmètre RFI.'],
 [28,'Microsoft projet COPIL',4240000,'€','COPIL 5 p.7 : pilote et quatre pôles ; projection non engageante.']
];
for(const[r,label,v,u,why]of sourceRows){src.getRange(`B${r}:E${r}`).values=[[label,v,u,why]];src.getRange(`B${r}:E${r}`).format.wrapText=true;src.getRange(`B${r}:E${r}`).format.rowHeight=42;src.getRange('C'+r).setNumberFormat(r===24?'0.0%':'#,##0');}
note(src,12,'Les forfaits SAP alimentent le total. Le contrôle d’équipe SAP, en fin d’onglet, ne les remplace pas et ne s’y ajoute pas.','I',34);
band(src,31,'Budgets initiaux repris de l’étude précédente — estimations, pas prix RFI');
header(src,33,['Poste initial','FLOW','SAP','Microsoft']);
const initialLabels=['Core system','Flux et sécurité','Configuration métier / Business','Spécifiques Buy','Pilotage, tests, reprises et bascule','Ressources de construction'];
for(let i=0;i<6;i++){const r=34+i;set(src,'B'+r,initialLabels[i]);for(const[c,oc]of [['C','C'],['D','D'],['E','E']])set(src,c+r,val('Structure coûts',oc+(8+i))*1e6);}
for(const c of ['C','D','E'])f(src,c+'40',`=SUM(${c}34:${c}39)`);set(src,'B40','TOTAL INITIAL');total(src,40,'E');src.getRange('C34:E40').setNumberFormat(money);src.getRange('B34:B40').format.wrapText=true;src.getRange('B34:E40').format.rowHeight=32;
note(src,42,'Budgets et ventilation conservés : 32 100 JH FLOW à 750 €/JH, plus 386 k€ de ressources. Buy : rapprochement de périmètre et tarifs France de l’étude. Ces montants sont des entrées de budget, sans nouvelle estimation de détail.','I',50);
note(src,44,'Traçabilité initiale : étude 06 (charges), 09 (répartition), 11 (France), 15 (compléments Buy). La version détaillée précédente est conservée en archive du 21/10/2026.','I',38);
band(src,48,'Calendrier de référence — jalons et répartition du budget initial');
header(src,49,['Solution / phase','Début mois','Fin mois','Budget €','Part production','Premiers usages','Fin groupe']);
const phases=[];
for(const [id,sheet,first,full,count]of [['flow','Prix Flow',60,60,1],['sap','Prix SAP',18,30,3],['ms','Prix Microsoft',18,38,5]]){
 for(let i=0;i<count;i++){const o=21+i,r=50+phases.length;const p={id,r,label:val(sheet,'B'+o),start:val(sheet,'C'+o),end:val(sheet,'D'+o),amount:val(sheet,'E'+o)*1e6,weight:val(sheet,'F'+o),first,full};phases.push(p);src.getRange(`B${r}:H${r}`).values=[[p.label,p.start,p.end,p.amount,p.weight,first,full]];}
}
src.getRange('E50:E58').setNumberFormat(money);src.getRange('F50:F58').setNumberFormat('0%');src.getRange('B50:H58').format.rowHeight=29;src.getRange('B50:B58').format.wrapText=true;src.getRange('E:E').format.columnWidth=24;
// Put long source descriptions in a wider merged area without obscuring numeric inputs.
for(const[r,,,,why]of sourceRows){src.getRange(`E${r}:I${r}`).merge();set(src,'E'+r,why);}
note(src,60,'FLOW M60 : hypothèse utilisateur. Buy : pilote M18, fin SAP M30 et Microsoft M38 au COPIL. Dates intermédiaires, poids de production et répartition des budgets : hypothèses conservées.','I',42);
band(src,63,'Pourquoi ces équipes');
const explanations=[
 ['Service et exploitation','Trois personnes-an : deux interlocuteurs fonctionnel et technique sur 250 jours (500 JH), plus 100 JH de prévention/configuration. Diagnostics et reprises sont dans cette capacité.'],
 ['Entretien logiciel','FLOW : deux capacités d’ingénierie et une de qualification pour tout le produit. Microsoft : une d’ingénierie et une de qualification pour la solution intégrée, interfaces et extensions.'],
 ['Architecture et pilotage','Une personne-an : architecture et pilotage partagés, coordination des partenaires comprise. Aucun pourcentage additionnel.'],
 ['Évolutions','Deux personnes-an : conception, réalisation et tests. Capacité financée, sans promesse de livrer le même nombre de fonctions. Les nouvelles versions fonctionnelles du Core FLOW sont incluses.'],
 ['Service retenu','Heures ouvrées françaises, solution stabilisée et automatisée. L1 et décisions métier client exclus. SAP conserve ses horaires étendus RFI ; équivalence contractuelle non démontrée.'],
 ['Frontière avec le projet','Convention : support de bascule/stabilisation affecté au projet ; service courant affecté au Run dès les premiers usages. Pas de double imputation d’une même intervention. La relève contractuelle reste à vérifier.'],
 ['Tarifs','750 €/JH FLOW et 850 €/JH Microsoft : hypothèses de prix France de l’étude, frais et marge compris. Aucun surcoût automatique par marque ou par chiffre d’affaires.'],
 ['Plateformes','FLOW 400 k€/an de ressources. SAP CPI : recette 59 195 € + production 92 027 €, avant crédit BTP non valorisé. Microsoft : 12 k€ recette + 33 k€ production externes conditionnels ; standard déjà souscrit.'],
 ['Périmètre et limites','Les compléments Buy et retraits Finance restent des hypothèses. Les forfaits SAP ne prouvent pas la couverture complète de la cible. La comparaison est indicative, sans économies garanties.']
];
for(let i=0;i<explanations.length;i++){const r=65+i*2;set(src,'B'+r,explanations[i][0]);src.getRange('B'+r).format.font.bold=true;src.getRange(`C${r}:I${r}`).merge();set(src,'C'+r,explanations[i][1]);src.getRange(`B${r}:I${r}`).format.wrapText=true;src.getRange(`B${r}:I${r}`).format.rowHeight=48;}
band(src,85,'Références et statut des données');
const links=[
 ['Méthode de l’étude','02-methode-estimation.md — capacités proposées et limites.'],
 ['Organisation D365','https://learn.microsoft.com/en-us/dynamics365/guidance/implementation-guide/transition-to-support-team'],
 ['Responsabilités D365','https://learn.microsoft.com/en-us/dynamics365/guidance/implementation-guide/service-solution'],
 ['Versions D365','https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/get-started/public-preview-releases'],
 ['Responsabilités SAP','https://learning.sap.com/courses/sap-s-4hana-cloud-interaction-with-sap-for-administrations/describing-roles-and-responsibilities-for-sap-s-4hana-cloud-private-edition'],
 ['Repères France','Malt Java ; Silkhom coût projet ERP. Consultation 20/10/2026. Les baromètres ne chiffrent pas ce contrat fournisseur.'],
 ['Pièces RFI','Archive Synvance : Delaware septembre 2025, Avanade réponse #1, questionnaires et COPIL 5. Références complètes dans 07-analyse-synvance.md.']
];
for(let i=0;i<links.length;i++){const r=87+i*2;set(src,'B'+r,links[i][0]);src.getRange(`C${r}:I${r}`).merge();set(src,'C'+r,links[i][1]);src.getRange(`B${r}:I${r}`).format.wrapText=true;src.getRange(`B${r}:I${r}`).format.rowHeight=i===4?58:40;}
band(src,104,'Ressources de construction FLOW — échéancier conservé');
header(src,106,['Période','Début relatif','Fin relative','Budget de référence']);
for(let i=0;i<5;i++){const r=107+i;src.getRange(`B${r}:E${r}`).values=[[`Année ${i+1}`,i/5,(i+1)/5,val('Plateformes et sortie','H'+(35+i))]];}
src.getRange('C107:D111').setNumberFormat('0%');src.getRange('E107:E111').setNumberFormat(money);
note(src,113,'Parts de la durée de construction ; le budget total est lié à Sources E107:E111. Même répartition que dans la version précédente.','I',35);
f(src,'C39','=SUM(E107:E111)');
band(src,116,'CPI SAP — part fixe et consommation, hors crédit BTP');
for(const [r,label,v,fmt] of [[119,'Tenant de production / mois',4635,money],[120,'Bloc et messages inclus',10000,'#,##0 "messages"'],[121,'Prix du bloc / mois',6.08,'0.00 "€"'],[122,'Messages de production / mois',5000000,'#,##0 "messages"']]){set(src,'B'+r,label);set(src,'C'+r,v);src.getRange('C'+r).setNumberFormat(fmt);}
set(src,'B123','Part indépendante du volume / an');f(src,'C123',"='Hypothèses'!C40*(C119-C121)");
set(src,'B124','Production complète / an');f(src,'C124',"=C123+C122/C120*C121*'Hypothèses'!C40");src.getRange('C123:C124').setNumberFormat(money);
src.getRange('B119:B124').format.wrapText=true;src.getRange('B119:C124').format.rowHeight=35;
note(src,126,'Prix catalogue EUR SAP Integration Suite Standard repris de l’étude (20/10/2026) ; tenant et volumes hypothétiques. La part fixe commence au premier usage ; les messages suivent le périmètre livré. L’abattement de messages inclus est déduit dans la part fixe.','I',55);
band(src,130,'Du prix RFI au budget initial retenu — mêmes montants, explication des écarts');
header(src,132,['Poste','FLOW','SAP','Microsoft','Nature / justification']);src.getRange('F132:I132').merge();
const bridgeLabels=['Référence RFI / COPIL','Valorisation France / prestations FLOW','Travaux Finance retirés','Compléments fonctionnels ciblés','Tests automatisés additionnels','Accompagnement additionnel','Tâches techniques confiées au fournisseur','Ressources de construction','TOTAL INITIAL EXPLIQUÉ','Écart au budget retenu'];
for(let i=0;i<bridgeLabels.length;i++){const r=133+i;set(src,'B'+r,bridgeLabels[i]);src.getRange(`B${r}:I${r}`).format.rowHeight=40;src.getRange(`B${r}:I${r}`).format.wrapText=true;src.getRange(`F${r}:I${r}`).merge();}
const bridgeForms={C:['=0','=C163*C164','=0','=0','=0','=0','=0','=C39'],D:['=C27','=C165*C167-D133','=-C168*C167','=C170','=0','=C173','=C175','=0'],E:['=C28','=C166*C167-E133','=-C169*C167','=C171','=C172','=C174','=C176','=0']};
for(const[c,forms]of Object.entries(bridgeForms)){forms.forEach((v,i)=>f(src,c+(133+i),v));f(src,c+'141',`=SUM(${c}133:${c}140)`);f(src,c+'142',`=ROUND(${c}141-${c}40,0)`);}
const bridgeNotes=['SAP : somme externe RFI ; Microsoft : pilote et pôles COPIL. Périmètres initiaux différents de FLOW.','FLOW : charge × prix. Buy : écart entre valorisation des jours retenus à prix France et référence RFI/COPIL.','Retrait estimé de 1 967 JH SAP et 390 JH Microsoft, à 1 000 €/JH.','Exceptions de commande, promesse et configuration : adaptations conditionnelles, pas un OMS reconstruit.','Microsoft : automatisation supplémentaire, hors tests déjà financés.','Supports et adoption, hors prestations déjà comprises.','Responsabilités techniques initialement prévues côté Beaumanoir, transférées au fournisseur autonome.','FLOW : ressources du projet. Les abonnements Buy et CPI sont déjà dans la trajectoire de coûts.','Total égal au budget courant. Aucune nouvelle majoration.','Doit rester nul. Le rapprochement explique le budget et ne s’ajoute pas à celui-ci.'];
bridgeNotes.forEach((x,i)=>set(src,'F'+(133+i),x));src.getRange('C133:E142').setNumberFormat(money);total(src,141);src.getRange('B133:I142').format.rowHeight=44;
note(src,144,'Lecture : référence sourcée + ajustements estimés = budget de comparaison. Une hypothèse de complément ne démontre pas une absence du produit. Détail : annexe 15, sections 1 à 5.','I',45);
band(src,160,'Entrées du rapprochement — reprises de l’étude, sans recalibrage');
for(const[r,label,x,unit,why]of [[163,'Charge initiale FLOW',32100,'JH','Hypothèse d’ingénierie, annexe 06.'],[164,'Prix réalisation FLOW',750,'€/JH','Hypothèse fournisseur autonome France, annexe 11.'],[165,'Charge initiale SAP',14640,'JH','Source RFI Delaware, avant retrait Finance.'],[166,'Charge initiale Microsoft',3900,'JH','Pilote 2 300 JH + hypothèse 4 pôles × 400 JH.'],[167,'Prix réalisation intégrateur',1000,'€/JH','Hypothèse France, distincte du prix des services annuels.'],[168,'Finance SAP hors FLOW',1967,'JH','Retrait estimé, annexe 15.'],[169,'Finance Microsoft hors FLOW',390,'JH','Retrait estimé, annexe 15.'],[170,'Fonctions complémentaires SAP',465800,'€','548 JH à 850 €/JH ; hypothèses conditionnelles.'],[171,'Fonctions complémentaires Microsoft',543150,'€','639 JH à 850 €/JH ; hypothèses conditionnelles.'],[172,'Automatisation Microsoft',315000,'€','420 JH à 750 €/JH ; hypothèse.'],[173,'Accompagnement SAP',360000,'€','360 JH à 1 000 €/JH ; hypothèse.'],[174,'Accompagnement Microsoft',360000,'€','360 JH à 1 000 €/JH ; hypothèse.'],[175,'Transfert technique SAP',val('Passage Buy France','I29')*1e6,'€','Estimation précédente, Passage Buy France I29 ; annexe 15.'],[176,'Transfert technique Microsoft',1008000,'€','1 008 JH à 1 000 €/JH ; annexe 15.']]){src.getRange(`B${r}:E${r}`).values=[[label,x,unit,why]];src.getRange(`E${r}:I${r}`).merge();src.getRange(`B${r}:I${r}`).format.wrapText=true;src.getRange(`B${r}:I${r}`).format.rowHeight=33;src.getRange('C'+r).setNumberFormat('#,##0');}
band(src,179,'SAP — contrôle de plausibilité hors total');
for(const[r,label,v,fmt]of [[181,'Maintien théorique',6,'0.0 "pers.-an"'],[182,'Évolutions théoriques',2,'0.0 "pers.-an"'],[183,'Prix théorique',850,'#,##0 "€/JH"']]){set(src,'B'+r,label);set(src,'C'+r,v);input(src,'C'+r,fmt);}
set(src,'B184','Budget théorique SAP');f(src,'C184',"=SUM(C181:C182)*'Hypothèses'!$C$39*C183");src.getRange('C184').setNumberFormat(money);
note(src,186,'Ce repère ne remplace pas les 1,05 M€/an de forfaits SAP et ne s’y ajoute pas. L’écart ne constitue pas un coût manquant démontré. Les volumes, horaires et responsabilités restent à rapprocher du contrat.','I',48);

// Main control panel: only the service choices are exposed first.
header(hyp,7,['Services annuels','FLOW','SAP','Microsoft','Explication']);hyp.getRange('F7:I7').merge();
const explain=(r,t)=>{hyp.getRange(`F${r}:I${r}`).merge();set(hyp,'F'+r,t);hyp.getRange(`B${r}:I${r}`).format.wrapText=true;hyp.getRange(`B${r}:I${r}`).format.rowHeight=36;};
set(hyp,'B8','Base de calcul');hyp.getRange('C8:E8').values=[['Équipe estimée','Forfaits RFI','Équipe estimée']];explain(8,'SAP : trois forfaits source. Le contrôle d’équipe théorique est dans Sources, hors total.');
for(const[r,label,flow,sap,ms]of [[9,'Maintien en service',7,'Forfaits',6],[10,'Capacité d’évolution',2,'Forfait',2],[11,'Prix moyen fournisseur',750,'Non utilisé',850]]){set(hyp,'B'+r,label);hyp.getRange(`C${r}:E${r}`).values=[[flow,sap,ms]];for(const c of ['C','E'])input(hyp,c+r,r===11?'#,##0 "€/JH"':'0.0 "pers.-an"');}
explain(9,'Maintenance, exploitation, qualification et pilotage. Une seule équipe financée.');explain(10,'Nouvelles fonctions, conception et tests compris. Capacité, pas nombre garanti de fonctionnalités.');explain(11,'Hypothèses France, frais et marge compris. Prix du service, distinct du prix du projet initial.');
for(const c of ['C','E']){f(hyp,c+'12',`=IF(AND(ISNUMBER(${c}9),ISNUMBER(${c}11),ISNUMBER($C$39)),${c}9*$C$39*${c}11,NA())`);f(hyp,c+'13',`=IF(AND(ISNUMBER(${c}10),ISNUMBER(${c}11),ISNUMBER($C$39)),${c}10*$C$39*${c}11,NA())`);}
f(hyp,'D12',"=IF(COUNT('Sources'!C8:C9)=ROWS('Sources'!C8:C9),SUM('Sources'!C8:C9),NA())");f(hyp,'D13',"=IF(ISNUMBER('Sources'!C10),'Sources'!C10,NA())");
for(const[r,label]of [[12,'Maintien en service €/an'],[13,'Évolutions €/an'],[14,'TOTAL SERVICES €/an']]){set(hyp,'B'+r,label);if(r===14)for(const c of ['C','D','E'])f(hyp,c+r,`=SUM(${c}12:${c}13)`);}
hyp.getRange('C12:E14').setNumberFormat(money);total(hyp,14);explain(12,'SAP : 250 k€ MCO + 450 k€ supervision en horaires étendus.');explain(13,'SAP : 350 k€ d’évolutions, capacité non documentée.');
note(hyp,16,'Jaune / bleu : hypothèse modifiable. Vert : lien à une source. SAP : prix RFI conservés ; aucune équipe supplémentaire ajoutée.','I',32);
header(hyp,18,['Ressources seules','FLOW','SAP','Microsoft','Explication']);hyp.getRange('F18:I18').merge();
for(const[r,label,vs,why]of [[19,'Recette / ressources avant usages',[0,59195.04,12000],'SAP CPI et extensions Microsoft dès le début du projet. FLOW : ressources de construction déjà dans le budget initial.'],[20,'Production / ressources en plus',[400000,92027.04,33000],'FLOW dès M60. Buy selon les périmètres livrés. Hébergement standard Buy déjà dans les licences.']]){set(hyp,'B'+r,label);hyp.getRange(`C${r}:E${r}`).values=[vs];for(const c of ['C','D','E'])input(hyp,c+r);explain(r,why);hyp.getRange(`B${r}:I${r}`).format.rowHeight=46;}
f(hyp,'D20',"='Sources'!C124");hyp.getRange('D20').format.fill=colors.grey;
header(hyp,22,['Calendrier depuis le lancement','FLOW','SAP','Microsoft','Convention']);hyp.getRange('F22:I22').merge();
for(const[r,label,vs,why]of [[23,'Premiers usages',[60,18,18],'Date du pilote Buy ou de la livraison unique FLOW. Début de la capacité complète de service.'],[24,'Périmètre complet',[60,30,38],'Jalons intermédiaires recalés proportionnellement à la durée de déploiement.']]){set(hyp,'B'+r,label);hyp.getRange(`C${r}:E${r}`).values=[vs];for(const c of ['C','D','E'])input(hyp,c+r,'0 "mois"',1,180);explain(r,why);}
note(hyp,26,'Convention de budget : service complet dès les premiers usages, sans réduction au pourcentage de fonctions déployées. Run après fin du mois de livraison ; coût des ressources Buy conservé selon le périmètre livré.','I',42);
f(hyp,'C24','=C23');hyp.getRange('C24').format.fill=colors.grey;
for(const c of ['D','E'])hyp.getRange(c+'24').dataValidation={rule:{type:'decimal',operator:'between',formula1:c+'23',formula2:180}};
note(hyp,28,'Les calculs annuels restent visibles plus bas. Les justifications, le rapprochement des prix initiaux et le contrôle d’équipe SAP sont dans Sources.','I',32);
hyp.getRange('B29:M36').format.rowHeight=3;
band(hyp,37,'Conventions communes et abonnements');
const globals=[[39,'Jours par personne-an',200,'0 "JH/an"'],[40,'Mois par an',12,'0 "mois"'],[41,'Horizon de projection',15,'0 "ans"'],[42,'Indexation des prestations',0,'0.0%'],[43,'Indexation des ressources',0,'0.0%'],[44,'Indexation des licences',.04,'0.0%'],[45,'Indexation CPI SAP',.04,'0.0%'],[51,'Euros par million',1000000,'#,##0']];
set(hyp,'J39','Zéro technique');set(hyp,'K39',0);set(hyp,'J40','Unité de calcul');set(hyp,'K40',1);hyp.getRange('J39:K40').format.fill=colors.grey;
set(hyp,'J41','Euros par millier');set(hyp,'K41',1000);
for(const[r,label,v,fmt]of globals){set(hyp,'B'+r,label);set(hyp,'C'+r,v);if([42,43,44,45].includes(r))input(hyp,'C'+r,fmt,-.5,1);else hyp.getRange('C'+r).setNumberFormat(fmt);}
explain(39,'Convention de capacité, pas une durée de présence individuelle de 250 jours.');explain(44,'Hypothèse de projection, après gel. Pas une clause d’augmentation garantie.');explain(45,'Provision CPI avant crédit BTP non valorisé.');
for(const[r,label,vs]of [[46,'Prix licences stable pendant',[0,1,5]],[47,'Retrait licences hors FLOW',[0,null,.10]],[48,'Part D365 pour Unified',[0,0,.7]],[49,'Conversion USD vers EUR',[0,0,1]]]){set(hyp,'B'+r,label);for(let i=0;i<3;i++){const c=['C','D','E'][i];if(vs[i]!==null)set(hyp,c+r,vs[i]);if(i&&vs[i]!==null)input(hyp,c+r,r===46?'0 "ans"':r===49?'0.00 "€/USD"':'0.0%',0,r===46?15:r===49?5:1);}}
f(hyp,'D47',"='Sources'!C20/'Sources'!C18");hyp.getRange('D47').setNumberFormat('0.0%');explain(46,'SAP : un an supposé ; Microsoft : cinq ans, clause K3 à confirmer.');explain(47,'Retraits hypothétiques conservés de l’étude, pas remises confirmées : Finance SAP et 10 % Microsoft.');explain(48,'70 % supposés dans le panier D365/K3 ; minimum et taux Unified dans Sources.');
band(hyp,53,'Options — zéro signifie non financé');
for(const[r,label,fmt]of [[54,'Storeland non découvert','0.0%'],[55,'Lotissement additionnel','0.0%'],[56,'Réserve de risque','0.0%'],[57,'Co-construction client','0.0%'],[58,'Astreinte annuelle',money],[59,'Migrations majeures annuelles',money]]){set(hyp,'B'+r,label);for(const c of ['C','D','E']){set(hyp,c+r,0);input(hyp,c+r,fmt,0,r<58?1:1e7);}}
explain(54,'Option FLOW évoquée : 15 % si activée. Assiette : prestations initiales, hors ressources.');explain(57,'Provision du coût client, séparée et exclue du total fournisseur. Les autres contributions internes restent non chiffrées.');explain(59,'Provision annuelle facultative, distincte des versions techniques courantes déjà financées.');
band(hyp,63,'Budget initial conservé — aucune nouvelle estimation du projet');
for(const[r,label]of [[65,'Prestations initiales'],[66,'Ressources de construction'],[67,'Options fournisseur initiales'],[68,'TOTAL INITIAL'],[69,'Provision client distincte']]){set(hyp,'B'+r,label);for(const c of ['C','D','E']){const form=r===65?`=SUM('Sources'!${c}34:${c}38)`:r===66?`='Sources'!${c}39`:r===67?`=${c}65*SUM(${c}54:${c}56)`:r===68?`=SUM(${c}65:${c}67)`:`=${c}65*${c}57`;f(hyp,c+r,form);}}hyp.getRange('C65:E69').setNumberFormat(money);total(hyp,68);explain(69,'Provision optionnelle, pas coût client complet. Ne modifie pas les totaux fournisseur.');
band(hyp,73,'Calcul du calendrier — lié aux deux dates de chaque solution');
header(hyp,75,['Phase','Début mois','Fin mois','Budget €','Part production']);
for(let i=0;i<phases.length;i++){const p=phases[i],r=76+i,c={flow:'C',sap:'D',ms:'E'}[p.id];p.hr=r;set(hyp,'B'+r,p.label);
 for(const[dest,sc]of [['C','C'],['D','D']]){const ref=`'Sources'!${sc}${p.r}`;f(hyp,dest+r,p.id==='flow'?`=${ref}/'Sources'!H${p.r}*$${c}$24`:`=IF(${ref}<='Sources'!G${p.r},${ref}/'Sources'!G${p.r}*$${c}$23,$${c}$23+(${ref}-'Sources'!G${p.r})/('Sources'!H${p.r}-'Sources'!G${p.r})*($${c}$24-$${c}$23))`);}
 f(hyp,'E'+r,`='Sources'!E${p.r}/SUM('Sources'!${c}34:${c}38)*SUM($${c}$65,$${c}$67)`);f(hyp,'F'+r,`='Sources'!F${p.r}`);
}hyp.getRange('E76:E84').setNumberFormat(money);hyp.getRange('F76:F84').setNumberFormat('0%');hyp.getRange('B76:F84').format.rowHeight=29;hyp.getRange('B76:B84').format.wrapText=true;
note(hyp,86,'Les dépenses initiales sont réparties linéairement dans chaque phase, comme dans l’étude précédente. Déplacer une date déplace la dépense et le démarrage des services, sans changer le budget initial à prix constants.','I',42);

// One annual schedule per explicitly requested solution, all visible on Hypothèses.
const cases=[{id:'flow',label:'FLOW',col:'C',row:92,color:colors.purple},{id:'sap',label:'SAP',col:'D',row:115,color:colors.sap},{id:'ms',label:'Microsoft',col:'E',row:138,color:colors.ms}];
const overlap=(r,p)=>`MAX(0,MIN(B${r}*$C$40,$D$${p.hr})-MAX((B${r}-1)*$C$40,$C$${p.hr}))/($D$${p.hr}-$C$${p.hr})`;
for(const c of cases){const b=c.row;band(hyp,b-2,`${c.label} — projection annuelle en euros`,'M');header(hyp,b-1,['Année','Réalisation','Mois Run','Maintien','Évolutions','Licences','Plateforme','Support éditeur','Options Run','Total annuel','Cumul','Part production']);
 for(let y=0;y<=15;y++){const r=b+y;set(hyp,'B'+r,y);if(y===0){hyp.getRange(`C${r}:M${r}`).values=[Array(11).fill(0)];continue;}
 const cp=phases.filter(p=>p.id===c.id);let build=cp.map(p=>`$E$${p.hr}*${overlap(r,p)}`).join('+');
 const construction=c.id==='flow'?'+'+[107,108,109,110,111].map(sr=>`'Sources'!$E$${sr}*MAX(0,MIN(B${r}*$C$40,'Sources'!$D$${sr}*$C$24)-MAX((B${r}-1)*$C$40,'Sources'!$C$${sr}*$C$24))/(('Sources'!$D$${sr}-'Sources'!$C$${sr})*$C$24)*(1+$C$43)^(B${r}-1)`).join('+'):'';
 f(hyp,'C'+r,`=(${build})*(1+$C$42)^(B${r}-1)${construction}`);
 f(hyp,'D'+r,`=MAX(0,MIN($C$40,B${r}*$C$40-$${c.col}$23))`);
 f(hyp,'E'+r,`=$${c.col}$12*(1+$C$42)^(B${r}-1)*D${r}/$C$40`);
 f(hyp,'F'+r,`=$${c.col}$13*(1+$C$42)^(B${r}-1)*D${r}/$C$40`);
 const licbase=c.id==='sap'?`INDEX('Sources'!$C$14:$C$18,MIN(B${r},ROWS('Sources'!$C$14:$C$18)))`:c.id==='ms'?"'Sources'!$C$22":'0';
 f(hyp,'G'+r,`=${licbase}*(1-$${c.col}$47)*(1+$C$44)^MAX(0,B${r}-MAX(1,$${c.col}$46))`);
 f(hyp,'M'+r,'='+cp.map(p=>`$F$${p.hr}*MAX(0,MIN($C$40,B${r}*$C$40-$D$${p.hr}))/$C$40`).join('+'));
 f(hyp,'H'+r,c.id==='sap'?`=($D$19+'Sources'!$C$123*D${r}/$C$40+($D$20-'Sources'!$C$123)*M${r})*(1+$C$45)^(B${r}-1)`:`=($${c.col}$19+$${c.col}$20*M${r})*(1+$C$43)^(B${r}-1)`);
 f(hyp,'I'+r,c.id==='ms'?`=IF(B${r}=1,'Sources'!$C$23,MAX('Sources'!$C$25*$E$49,'Sources'!$C$24*$E$48*G${r}))`:'=0');
 f(hyp,'J'+r,`=SUM($${c.col}$58:$${c.col}$59)*(1+$C$42)^(B${r}-1)*D${r}/$C$40`);
 f(hyp,'K'+r,`=SUM(C${r},E${r}:J${r})`);f(hyp,'L'+r,`=L${r-1}+K${r}`);
 }
 hyp.getRange(`C${b}:L${b+15}`).setNumberFormat(money);hyp.getRange(`D${b}:D${b+15}`).setNumberFormat('0.0 "mois"');hyp.getRange(`M${b}:M${b+15}`).setNumberFormat('0%');hyp.getRange(`B${b}:M${b+15}`).format.rowHeight=25;
 for(const y of [3,5,10,15])total(hyp,b+y,'M');
}
note(hyp,156,'Cumul = réalisation + services + licences + plateforme + support éditeur + options fournisseur. Le Run concerne les services après mise en service ; des abonnements et ressources peuvent être payés dès le projet.','M',40);
band(hyp,160,'Lecture des résultats — calculs de synthèse');
header(hyp,162,['Solution','Initial payé','Annuel moyen 6–15','Années de Run à 15 ans']);
for(const c of cases){const r=163+cases.indexOf(c),b=c.row;set(hyp,'B'+r,c.label);f(hyp,'C'+r,`=SUM(C${b+1}:C${b+15})`);f(hyp,'D'+r,`=(SUM(E${b+6}:J${b+15}))/(B${b+15}-B${b+5})`);f(hyp,'E'+r,`=SUM(D${b+1}:D${b+15})/$C$40`);}hyp.getRange('C163:C165').setNumberFormat(money);hyp.getRange('D163:D165').setNumberFormat('#,##0 "€/an"');hyp.getRange('E163:E165').setNumberFormat('0.0 "ans"');
band(hyp,169,'Données du graphique — trajectoire annuelle');header(hyp,171,['Année','FLOW M€','SAP M€','Microsoft M€']);
for(let y=0;y<=15;y++){const r=172+y;set(hyp,'B'+r,y);for(const c of cases)f(hyp,c.col+r,`=L${c.row+y}/$C$51`);}hyp.getRange('C172:E187').setNumberFormat('0.00 "M€"');
header(hyp,190,['Jalon','Mois','Année','Coût sur la courbe M€']);
const marks=[['FLOW en service','C',23],['SAP premiers usages','D',23],['SAP déployé','D',24],['Microsoft premiers usages','E',23],['Microsoft déployé','E',24]];
for(let i=0;i<marks.length;i++){const[label,c,dr]=marks[i],r=191+i;set(hyp,'B'+r,label);f(hyp,'C'+r,`=$${c}$${dr}`);f(hyp,'D'+r,`=C${r}/$C$40`);f(hyp,'E'+r,`=INDEX($${c}$172:$${c}$187,INT(D${r})+1)+(D${r}-INT(D${r}))*(INDEX($${c}$172:$${c}$187,MIN(INT(D${r})+2,ROWS($${c}$172:$${c}$187)))-INDEX($${c}$172:$${c}$187,INT(D${r})+1))`);}
hyp.getRange('E191:E195').setNumberFormat('0.00 "M€"');note(hyp,197,'Les jalons sont placés sur une trajectoire interpolée entre les coûts annuels. Leur date est exacte selon les hypothèses ; la courbe ne prétend pas représenter une facturation mensuelle.','I',38);

// Compact decision view: unchanged headline cell locations support native QA.
comp.getRange('B:B').format.columnWidth=21;comp.getRange('C:C').format.columnWidth=12;comp.getRange('D:I').format.columnWidth=16;
note(comp,5,'Cible commune : achats, ventes, retours, stock et orchestration des commandes / fulfillment. Hors finance, gestion commerciale, conception produit, planification stratégique et exécution logistique. Couverture Buy à confirmer.','I',34);
header(comp,7,['Solution','Base du service','Réalisation initiale','Fonctionnement moyen années 6–15','3 ans','5 ans','10 ans','15 ans']);comp.getRange('B7:I7').format.rowHeight=56;
for(let i=0;i<cases.length;i++){const c=cases[i],r=9+i,b=c.row;set(comp,'B'+r,c.label);set(comp,'C'+r,c.id==='sap'?'Forfaits RFI':'Équipe');f(comp,'D'+r,`='Hypothèses'!C${163+i}`);f(comp,'E'+r,`='Hypothèses'!D${163+i}`);for(const[col,y]of [['F',3],['G',5],['H',10],['I',15]])f(comp,col+r,`='Hypothèses'!L${b+y}`);comp.getRange(`D${r}:I${r}`).setNumberFormat(meur);comp.getRange('E'+r).setNumberFormat(annual);comp.getRange(`B${r}:I${r}`).format={rowHeight:31,font:{name:'Arial',size:11,bold:true,color:colors.ink},fill:i%2?colors.grey:colors.pale};comp.getRange('B'+r).format.font.color=c.color;}
note(comp,12,'Cumuls depuis le lancement, réalisation incluse. Fonctionnement : services, évolutions, licences, support et plateforme, indexation comprise. Coûts fournisseur HT ; temps interne client exclu.','I',31);
const mln=(r,d=1)=>`ROUND((${r})/'Hypothèses'!$C$51,${d})`;
const signed=(r,d=1)=>`IF((${r})>=0,"+","")&${mln(r,d)}`;
const story=(r,formula,height=27)=>{note(comp,r,'','I',height);f(comp,'B'+r,formula);comp.getRange(`B${r}:I${r}`).format.font={name:'Arial',size:10,color:colors.ink};};
story(13,`="Investissement FLOW : "&${mln('D9')}&" M€ ; écart à Microsoft : "&${signed('D9-D11')}&" M€ ; dont construction du Core FLOW : "&${mln("'Sources'!C34")}&" M€."`);
story(14,`="Fonctionnement moyen : FLOW "&${mln('E9',2)}&" M€/an, Microsoft "&${mln('E11',2)}&" M€/an ; écart FLOW – Microsoft : "&${signed('E9-E11',2)}&" M€/an."`);
story(15,`="À quinze ans : FLOW – Microsoft "&${signed('I9-I11')}&" M€ ; SAP – FLOW "&${signed('I10-I9')}&" M€. "&IF(ABS(I9-I11)<'Hypothèses'!C39*'Hypothèses'!C11*'Hypothèses'!E163,"L’écart FLOW–Microsoft ne démontre pas un avantage économique robuste.","Classement conditionné aux hypothèses et à la couverture des services.")`,40);
story(16,`="Premiers usages : FLOW au mois "&'Hypothèses'!C23&", Microsoft au mois "&'Hypothèses'!E23&". Une personne supplémentaire de maintien FLOW chaque année = "&${mln("'Hypothèses'!C39*'Hypothèses'!C11*'Hypothèses'!E163")}&" M€ sur l’horizon."`,32);
story(17,`="SAP / Microsoft : réalisation "&${mln('D10',2)}&" / "&${mln('D11',2)}&" M€ ; fonctionnement "&${mln('E10',2)}&" / "&${mln('E11',2)}&" M€/an. L’écart vient surtout de la réalisation initiale (Sources, lignes 130–144)."`,34);
band(comp,18,'Hypothèses qui expliquent les coûts');
story(19,`="FLOW : "&'Hypothèses'!C9&" personnes-an de maintien + "&'Hypothèses'!C10&" d’évolutions, "&'Hypothèses'!C39&" JH/personne-an, "&'Hypothèses'!C11&" €/JH. Plateforme : "&${mln("'Hypothèses'!C20")}&" M€/an (cloud, stockage, sauvegardes, outils ; hors personnel)."`,34);
story(20,`="SAP : forfaits issus de la consultation fournisseur (RFI) : "&ROUND('Sources'!C8/'Hypothèses'!K41,0)&" k€ de maintenance, "&ROUND('Sources'!C9/'Hypothèses'!K41,0)&" k€ de supervision et "&ROUND('Sources'!C10/'Hypothèses'!K41,0)&" k€ d’évolutions."`);
story(21,`="Microsoft : "&'Hypothèses'!E9&" personnes-an de maintien + "&'Hypothèses'!E10&" d’évolutions, "&'Hypothèses'!C39&" JH/personne-an, "&'Hypothèses'!E11&" €/JH. Hébergement standard Buy compris dans les licences."`);
story(22,`="Indexation annuelle : prestations "&TEXT('Hypothèses'!C42,"0%")&", ressources hors CPI "&TEXT('Hypothèses'!C43,"0%")&", CPI SAP "&TEXT('Hypothèses'!C45,"0%")&". CPI = Cloud Platform Integration, plateforme d’échange de données SAP. Licences "&TEXT('Hypothèses'!C44,"0%")&" après gel supposé de "&'Hypothèses'!D46&" an SAP / "&'Hypothèses'!E46&" ans Microsoft."`,45);
story(23,`=IF(SUM('Hypothèses'!C54:E56,'Hypothèses'!C58:E59)=0,"Non financés : Storeland non découvert, lotissement additionnel, risque, astreinte et migrations majeures.","Options fournisseur activées : voir Hypothèses, lignes 54 à 59.")&" Contributions internes client exclues."`,34);
const chart=comp.charts.add('scatter',[hyp.getRange('B171:B187'),hyp.getRange('C171:C187'),hyp.getRange('D171:D187'),hyp.getRange('E171:E187')]);
for(let i=0;i<marks.length;i++){const series=chart.series.add(marks[i][0]);series.formula=`'Hypothèses'!$E$${191+i}`;series.categoryFormula=`'Hypothèses'!$D$${191+i}`;}
chart.setPosition('B24','I37');chart.title='Coûts cumulés et mises en service';chart.titleTextStyle.typeface='Arial';chart.titleTextStyle.fontSize=12;chart.hasLegend=false;
chart.xAxis={min:0,max:15,majorUnit:3,numberFormatCode:'0 "ans"',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};chart.yAxis={min:0,numberFormatCode:'0 "M€"',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};
const chartColors=[colors.purple,colors.sap,colors.ms,colors.purple,colors.sap,colors.sap,colors.ms,colors.ms];chart.series.items.forEach((s,i)=>{s.line={fill:chartColors[i],style:'solid',width:i<3?2.5:0};s.fill=chartColors[i];if(i>=3)chart.applyDataLabels({scope:'series',seriesIndex:i},{showSeriesName:true,showValue:false,position:'right',textStyle:{typeface:'Arial',fontSize:10}});});
for(let i=0;i<cases.length;i++){const c=cases[i],s=chart.series.add(c.label);s.formula=`'Hypothèses'!$${c.col}$187`;s.categoryFormula="'Hypothèses'!$B$187";s.fill=c.color;s.line={fill:c.color,style:'solid',width:0};chart.applyDataLabels({scope:'series',seriesIndex:8+i},{showSeriesName:true,showValue:true,position:['top','left','bottom'][i],textStyle:{typeface:'Arial',fontSize:10}});}
header(comp,39,['Mises en service','', 'Premiers usages','Périmètre complet','Run à 15 ans','Règle de démarrage']);comp.getRange('B39:C39').merge();comp.getRange('G39:I39').merge();
for(let i=0;i<cases.length;i++){const c=cases[i],r=40+i;comp.getRange(`B${r}:C${r}`).merge();set(comp,'B'+r,c.label);f(comp,'D'+r,`='Hypothèses'!${c.col}23`);f(comp,'E'+r,`='Hypothèses'!${c.col}24`);f(comp,'F'+r,`='Hypothèses'!E${163+i}`);comp.getRange(`D${r}:E${r}`).setNumberFormat('0 "mois"');comp.getRange('F'+r).setNumberFormat('0.0 "ans"');comp.getRange(`G${r}:I${r}`).merge();set(comp,'G'+r,'Service complet dès les premiers usages');comp.getRange(`B${r}:I${r}`).format.rowHeight=27;}
note(comp,43,'Licences et recette payées pendant le projet. Run après le mois de première livraison. Jalons = usages métier ; bénéfices et gains financiers non valorisés.','I',31);
band(comp,45,'Portée de la comparaison — ce qui est établi et ce qui reste estimé');
for(const[r,label,text]of [[46,'FLOW','Périmètre cible défini. Charge, prix, équipe et ressources estimés ; absence de devis et de productivité mesurée. Propriété du produit recherchée.'],[47,'SAP','Base : RFI Delaware et forfaits annuels sourcés. France, retrait Finance, compléments et transferts estimés. Couverture complète et horaires à confirmer.'],[48,'Microsoft','Base : pilote RFI et déploiements COPIL. France, compléments, transferts et équipe annuelle estimés. Couverture et gel des licences à confirmer.']]){set(comp,'B'+r,label);comp.getRange(`C${r}:I${r}`).merge();set(comp,'C'+r,text);comp.getRange(`B${r}:I${r}`).format.wrapText=true;comp.getRange(`B${r}:I${r}`).format.rowHeight=37;}
note(comp,49,'FLOW et Microsoft : équipes en heures ouvrées. SAP : supervision étendue au RFI. L’équivalence contractuelle et la capacité d’évolution ne sont pas démontrées.','I',32);
band(comp,51,'Structure des coûts — réalisation initiale');header(comp,53,['Poste','','FLOW','SAP','Microsoft']);comp.getRange('B53:C53').merge();
for(let i=0;i<6;i++){const r=54+i;comp.getRange(`B${r}:C${r}`).merge();set(comp,'B'+r,initialLabels[i]);comp.getRange(`B${r}:C${r}`).format.wrapText=true;for(const[dc,sc]of [['D','C'],['E','D'],['F','E']])f(comp,dc+r,`='Sources'!${sc}${34+i}`);comp.getRange(`D${r}:F${r}`).setNumberFormat(meur);comp.getRange(`B${r}:F${r}`).format.rowHeight=29;}
note(comp,61,'Core Buy : zéro construction du progiciel. Spécifiques FLOW : compris dans le Core. Origine des budgets : rapprochement RFI / hypothèses dans Sources, lignes 130 à 144.','I',32);
band(comp,63,'Structure annuelle moyenne — années 6 à 15');header(comp,65,['Poste','','FLOW','SAP','Microsoft']);comp.getRange('B65:C65').merge();
for(const[r,label,cols]of [[66,'Maintien en service',['E']],[67,'Évolutions fonctionnelles',['F']],[68,'Licences, standard hébergé',['G']],[69,'Plateforme hors standard',['H']],[70,'Support éditeur distinct',['I']],[71,'Options Run',['J']]]){comp.getRange(`B${r}:C${r}`).merge();set(comp,'B'+r,label);for(const c of cases){const dc={flow:'D',sap:'E',ms:'F'}[c.id];f(comp,dc+r,`=SUM('Hypothèses'!${cols[0]}${c.row+6}:${cols[0]}${c.row+15})/('Hypothèses'!B${c.row+15}-'Hypothèses'!B${c.row+5})`);}comp.getRange(`D${r}:F${r}`).setNumberFormat(annual);comp.getRange(`B${r}:F${r}`).format.rowHeight=27;}
note(comp,73,'Maintien = maintenance, exploitation humaine et pilotage. Évolutions = nouvelles fonctions, Core FLOW compris. Plateforme = ressources. Une même activité n’est pas financée deux fois.','I',35);
comp.getRange('B75:C75').merge();set(comp,'B75','Provision client hors total');for(const[dc,sc]of [['D','C'],['E','D'],['F','E']])f(comp,dc+'75',`='Hypothèses'!${sc}69`);comp.getRange('D75:F75').setNumberFormat(meur);note(comp,77,'Une provision client n’est affichée que si l’option de co-construction est renseignée. Un zéro ne signifie pas absence de travail interne.','I',32);
// Practical width and input styles; no fixed panel on Comparaison.
hyp.getRange('B:B').format.columnWidth=33;hyp.getRange('C:E').format.columnWidth=16;hyp.getRange('F:M').format.columnWidth=16;
src.getRange('B:B').format.columnWidth=36;src.getRange('C:D').format.columnWidth=16;src.getRange('E:I').format.columnWidth=17;
for(const s of [comp,hyp,src]){for(const r of [1,3,5,6])s.getRange(`B${r}:I${r}`).format.rowHeight=r===1?8:5;s.getRange('B2:I2').format.rowHeight=26;}
comp.getRange('B8:I8').format.rowHeight=5;comp.getRange('B5:I5').format.rowHeight=34;comp.getRange('B17:I17').format.rowHeight=34;
for(const s of [hyp,src])s.freezePanes.freezeRows(7);
comp.freezePanes.unfreeze();
wb.recalculate();
const results={};for(const c of cases){const r=9+cases.indexOf(c);results[c.id]={headline:comp.getRange(`D${r}:I${r}`).values[0],service:hyp.getRange(`${c.col}12:${c.col}14`).values.map(x=>x[0])};}
await fs.writeFile('tmp/three_tabs_results.json',JSON.stringify(results,null,2));
console.log((await wb.inspect({kind:'table',range:'Comparaison!B7:I13',include:'values,formulas',tableMaxRows:7,tableMaxCols:8,maxChars:3500})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!',options:{useRegex:true,maxResults:25},summary:'Errors'})).ndjson);
await (await SpreadsheetFile.exportXlsx(wb)).save(out);
for(const[id,sheetName,range]of [['comparison','Comparaison','B1:I23'],['decision','Comparaison','B24:I49'],['structure','Comparaison','B51:I77'],['inputs','Hypothèses','B1:I49'],['sources','Sources','B130:I144'],['explanations','Sources','B179:I186']]){const b=await wb.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(`tmp/three_tabs_${id}.png`,new Uint8Array(await b.arrayBuffer()));}
console.log(JSON.stringify({out,results}));

