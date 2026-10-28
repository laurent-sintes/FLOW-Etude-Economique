import {createRequire} from 'node:module';

// Read-only audit: mutations occur only in the imported in-memory workbook.
// There is deliberately no export, save, or write operation in this script.
const require=createRequire('C:/Users/laure/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {FileBlob,SpreadsheetFile}=require('@oai/artifact-tool');
const msFunctions=JSON.parse(require('node:fs').readFileSync('tools/flow_ms_functional_gaps.json','utf8'));
const sapFunctions=JSON.parse(require('node:fs').readFileSync('tools/flow_sap_functional_gaps.json','utf8'));
const platformCosts=JSON.parse(require('node:fs').readFileSync('tools/flow_platform_costs.json','utf8'));
const operationsCosts=JSON.parse(require('node:fs').readFileSync('tools/flow_ops_costs.json','utf8'));
const unifiedRun=JSON.parse(require('node:fs').readFileSync('tools/flow_run_unified.json','utf8'));
const path='outputs/01a1530f-f378-7fd1-9654-468c9b2141b6/FLOW_Make_abaques_et_prix_France_v4.xlsx';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path));
const physical=(s,a)=>wb.worksheets.getItem(s).getRange(a);
// The final presentation removes duplicate output tables and compacts the
// supporting sheets. Preserve the independent audit's logical coordinates;
// every read or mutation below resolves to the actual exported cell.
function auditAddress(sheet,address){
  return address.replace(/\$?[A-Z]+\$?\d+/g,reference=>{
    const match=reference.match(/^(\$?)([A-Z]+)(\$?)(\d+)$/),row=Number(match[4]);let destination=row;
    if(sheet==='Prix Flow'&&row>=111)destination=row-50;
    else if(['Prix Flow','Prix SAP','Prix Microsoft'].includes(sheet)&&row>=51)destination=row-33;
    else if(sheet==='Prix unitaire Flow'){
      if(row>=74)destination=row-21;
      else if(row>=52&&row<=66&&match[2]==='C')return '$D$24';
    }
    else if(sheet==='Structure coûts'&&row>=79)destination=row-61;
    else if(sheet==='Plateforme et exploitation'){
      if(row>=63&&row<=100)destination=row-19;
      else if(row>=113&&row<=121)destination=row-31;
    }
    return match[1]+match[2]+match[3]+destination;
  });
}
const cell=(s,a)=>physical(s,auditAddress(s,a));
const val=(s,a)=>cell(s,a).values[0][0];
const set=(s,a,x)=>cell(s,a).values=[[x]];
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const assert=(ok,message)=>{if(!ok)throw new Error(message);};
// One cent in M EUR: presentation number formats never round source formulas.
const near=(actual,expected,message,tolerance=1e-8)=>assert(finite(actual)&&Math.abs(actual-expected)<=tolerance,`${message}: ${actual} / expected ${expected}`);
const cases=[
  {name:'FLOW',s:'Prix Flow',u:'Prix unitaire Flow',start:8,count:1,col:'C',structureOffset:0},
  {name:'SAP',s:'Prix SAP',u:'Prix unitaire SAP',start:29,count:3,col:'D',structureOffset:21,bridge:8},
  {name:'Microsoft',s:'Prix Microsoft',u:'Prix unitaire Microsoft',start:50,count:5,col:'E',structureOffset:42,bridge:58}
];
const expectedSheets=['Comparaison','Prix Flow','Prix unitaire Flow','Prix SAP','Prix unitaire SAP','Prix Microsoft','Prix unitaire Microsoft','Passage Buy France','Charges Flow','Structure coûts','Plateforme et exploitation','Run Flow','Paramètres','Calculs 15 ans','Trajectoire mensuelle','Coûts techniques mensuels','Licences mensuelles','Références','Sources'];
const functionalModel=c=>c.name==='SAP'?{data:sapFunctions,start:157}:c.name==='Microsoft'?{data:msFunctions,start:117}:null;
for(const n of expectedSheets)assert(wb.worksheets.getItem(n),`Missing sheet ${n}`);
const snapshot=()=>({
  nominal:val('Prix Flow','D7'),withOptions:val('Prix Flow','D8'),
  cases:cases.map(c=>({name:c.name,project:val(c.s,'D12'),tco15:val(c.s,'H9'),status:val(c.s,'H14'),supplier:val('Calculs 15 ans','L'+(c.start+15)),client:val('Calculs 15 ans','O'+(c.start+15)),total:val('Calculs 15 ans','P'+(c.start+15))}))
});
const inputsSnapshot=()=>JSON.stringify({
  units:cases.map(c=>cell(c.u,'D7:D149').values),
  runAbaques:cases.map(c=>cell(c.u,'C76:H149').values),
  bridge:cell('Passage Buy France',`C8:O${Math.max(116+msFunctions.items.length,156+sapFunctions.items.length)}`).values,
  prices:cases.map(c=>({controls:cell(c.s,'D10:D14').values,dates:cell(c.s,`C54:F${53+c.count}`).values,client:cell(c.s,'D81:D84').values})),
  options:cell('Prix Flow','C66:C69').values,activities:cell('Charges Flow','D32:D32').values,keys:cell('Charges Flow','F8:H21').values,
  technical:cell('Plateforme et exploitation','B1:I220').values,
  reconciledRun:cell('Run Flow','B1:I80').values
});
const originalCell=(s,a)=>({values:cell(s,a).values,formula:cell(s,a).formulas?.[0]?.[0]});
function restoreCell(s,a,original){
  if(typeof original.formula==='string'&&original.formula.startsWith('='))cell(s,a).formulas=[[original.formula]];
  else cell(s,a).values=original.values;
}
function mutate(s,a,newValue,verify){
  // Shared evolution demand has one editable owner. The unit-price cells are
  // transparent links retained for downstream compatibility, never extra inputs.
  if(s==='Prix unitaire Flow'&&/^[CD]9[567]$/.test(a)){s='Run Flow';a=a[0]+(Number(a.slice(1))-62);}
  const original=originalCell(s,a);
  try{set(s,a,newValue);wb.recalculate();verify();}
  finally{restoreCell(s,a,original);wb.recalculate();}
}
function mutateMany(changes,verify){
  changes=changes.map(([s,a,x])=>s==='Prix unitaire Flow'&&/^[CD]9[567]$/.test(a)?['Run Flow',a[0]+(Number(a.slice(1))-62),x]:[s,a,x]);
  const original=changes.map(([s,a])=>[s,a,originalCell(s,a)]);
  try{for(const [s,a,x]of changes)set(s,a,x);wb.recalculate();verify();}
  finally{for(const [s,a,x]of original)restoreCell(s,a,x);wb.recalculate();}
}
function unavailable(c,label){
  assert(!finite(val(c.s,'H9')),`${label}: TCO remains a plausible number`);
  assert(val(c.s,'H14')!=='Paramètres renseignés',`${label}: status still says Paramètres renseignés`);
}
const passed=[],failures=[];
const test=(name,fn)=>{
  try{fn();passed.push(name);console.log('PASS',name);}
  catch(error){failures.push({name,error:String(error?.message??error)});console.log('FAIL',name,String(error?.message??error));}
};
wb.recalculate();
const baseline=snapshot();
const baselineInputs=inputsSnapshot();
console.log('BASELINE',JSON.stringify(baseline));

const sumCalc=(c,column,fromYear=1,toYear=15)=>Array.from({length:toYear-fromYear+1},(_,i)=>val('Calculs 15 ans',column+(c.start+fromYear+i))).reduce((a,b)=>a+b,0);
const runColumns=['D','E','F','G','H','W','X','Z','AA'];
const annualRunMean=c=>runColumns.reduce((a,col)=>a+sumCalc(c,col,6,15),0)/10;
const operationalDeliveries=c=>Array.from({length:c.count},(_,i)=>({month:val(c.s,'D'+(54+i)),weight:val(c.s,'F'+(54+i))})).filter(x=>x.weight>0).sort((a,b)=>a.month-b.month);
const deliveryMilestones=c=>{
  const deliveries=operationalDeliveries(c);let weight=0,full=null;
  for(const delivery of deliveries){weight+=delivery.weight;if(weight>=1-1e-8){full=delivery.month;break;}}
  return {first:deliveries[0]?.month,full};
};
const structure=(c,row,col='C')=>{
  const costIndex=row-9,optionIndex=cases.indexOf(c);
  if(col==='C'){
    const sourceRow={0:8,1:9,2:10,3:11,4:12,8:13,12:14,13:15}[costIndex];
    return sourceRow?physical('Structure coûts',String.fromCharCode(67+optionIndex)+sourceRow).values[0][0]:val('Comparaison','D'+matrixRow(c,costIndex));
  }
  const sourceCol={D:'E',E:'F',F:'G',G:'H',H:'I'}[col];
  assert(sourceCol,`Unknown comparison period ${col}`);
  return val('Comparaison',sourceCol+matrixRow(c,costIndex));
};
// The executive page shows every horizon together. The adapter preserves the
// semantic summary assertions used throughout the independent financial audit.
const comp=(c,row)=>{
  const optionIndex=cases.indexOf(c);
  if(row===31)return val('Comparaison','F'+(35+optionIndex));
  const column={22:'D',23:'E',26:'F',27:'G',28:'H',29:'I'}[row];
  assert(column,`Unknown executive comparison summary ${row}`);
  return val('Comparaison',column+(9+optionIndex));
};
const matrixRow=(c,costIndex)=>(costIndex===13?9:44+costIndex*3)+cases.indexOf(c);

test('Lower and upper estimate bounds are absent from the client calculation model',()=>{
  for(const c of cases){
    for(const a of ['D104','D105'])assert(!finite(val(c.s,a)),`${c.name}: removed bound remains at ${a}`);
    const visible=cell(c.s,'B94:H108').values.flat().filter(x=>typeof x==='string').join('\n');
    assert(!/borne\s+(basse|haute)|fourchette/i.test(visible),`${c.name}: retired bound heading remains visible`);
    if(c.name!=='FLOW')for(const a of ['D124','D125','D126','D127'])assert(!finite(val(c.u,a)),`${c.name}: retired bound tariff remains at ${a}`);
  }
  for(let r=8;r<=23;r++)for(const col of ['C','D'])assert(!finite(val('Charges Flow',col+r)),`FLOW retired bound effort remains at ${col+r}`);
  for(const c of cases.slice(1)){
    const b=c.bridge,model=functionalModel(c);
    for(const row of [b+32,b+33])assert(!finite(val('Passage Buy France','I'+row)),`${c.name}: retired bridge bound remains`);
    for(let i=0;i<model.data.items.length;i++)for(const col of ['D','F','L','M','N','O'])assert(!finite(val('Passage Buy France',col+(model.start+i))),`${c.name}: retired functional bound remains ${col+(model.start+i)}`);
  }
  for(const [sheet,range]of [['Comparaison','B1:I74'],['Charges Flow','B7:I26'],['Passage Buy France','B7:O172'],['Prix unitaire SAP','B113:H132'],['Prix unitaire Microsoft','B113:H132']]){
    const text=cell(sheet,range).values.flat().filter(x=>typeof x==='string').join('\n');
    assert(!/borne\s+(basse|haute)/i.test(text),`${sheet}: a retired bound label remains in the client model`);
  }
});

test('No unsupported spreadsheet function is exposed as visible text',()=>{
  for(const name of expectedSheets){
    const unsupported=cell(name,'B1:O220').values.flat().filter(x=>typeof x==='string'&&x.toLowerCase().includes('is not implemented'));
    assert(unsupported.length===0,`${name}: unsupported spreadsheet function remains visible: ${unsupported[0]}`);
  }
});

test('No spreadsheet error is present in the delivered baseline, including chart auxiliaries',()=>{
  for(const name of expectedSheets){
    const errors=cell(name,'B1:AA240').values.flat().filter(x=>typeof x==='string'&&/^#(?:N\/A|VALUE!|REF!|DIV\/0!|NAME\?|NUM!|SPILL!|CALC!|NULL!)$/.test(x));
    assert(errors.length===0,`${name}: ${errors.length} spreadsheet error cells remain in the delivered baseline`);
  }
});

test('Valid allocation keys use unambiguous OK text in native spreadsheet guards',()=>{
  for(let row=8;row<=21;row++)assert(val('Charges Flow','I'+row)==='OK',`FLOW key ${row}: expected the unambiguous OK status`);
  for(const name of ['Prix Flow','Structure coûts']){
    const formulas=cell(name,'B1:T240').formulas.flat().filter(x=>typeof x==='string');
    assert(!formulas.some(x=>x.includes('<>100 %')),`${name}: numeric-looking text criteria can be coerced in native Excel COUNTIF`);
  }
});

test('Initial budgets and FLOW single delivery',()=>{
  near(val('Prix Flow','D7'),24.075,'FLOW nominal');
  near(val('Prix Flow','D8'),30.09375,'FLOW supplier majorations, client excluded');
  near(val('Prix Flow','D69'),2.4075,'FLOW separately valued client contribution');
  near(val('Prix Flow','D14'),1,'FLOW nominal selected for comparison');
  near(val('Prix Flow','D12'),24.461,'FLOW initial realization includes 386 kEUR construction resource bills once');
  near(val('Prix SAP','D12'),17.13267887295082,'SAP initial realization at revised France rates');
  near(val('Prix Microsoft','D12'),5.73615,'Microsoft initial realization at revised France rates');
  near(val('Calculs 15 ans','L23'),35.781,'FLOW supplier 15-year cost contains one reconciled Run abaque and inactive service options');
  near(val('Calculs 15 ans','O23'),0,'FLOW client option inactive in nominal comparison');
  near(val('Calculs 15 ans','P23'),35.781,'FLOW known total with inactive client option');
  const sapTechnical=technicalOracle(cases[1]).years.reduce((a,z)=>a+z[2],0);
  near(val('Calculs 15 ans','L44'),48.850217153392855-1.5875+sapTechnical,'SAP supplier 15-year cost adds only net CPI execution cost, excluding optional major migrations');
  near(val('Calculs 15 ans','L65'),35.96935215127156+.5947,'Microsoft supplier 15-year cost adds only external execution provision');
  near(val('Calculs 15 ans','M13'),0,'FLOW run at year 5');
  near(val('Calculs 15 ans','M14'),1,'FLOW run at year 6');
  near(val('Prix Flow','H11'),60,'FLOW delivery month');
  near(val('Prix SAP','H11'),30,'SAP 18 + 12 months');
  near(val('Prix Microsoft','H11'),38,'Microsoft 18 + 20 months');
  for(const c of cases)assert(val(c.s,'H14')==='Paramètres renseignés',`${c.name}: numeric completeness must be named without suggesting estimate validation`);
});

function technicalOracle(c){
  const u=a=>val(c.u,a),p=a=>val(c.s,a),t=a=>val('Plateforme et exploitation',a);
  const years=Array.from({length:15},()=>Array(7).fill(0));
  const months=[];
  for(let month=0;month<180;month++){
    const yi=Math.floor(month/12),z=Array(7).fill(0),price=Math.pow(1+u('D45'),yi),quantities=Math.pow(1+t('D11'),yi),services=Math.pow(1+u('D43'),yi);
    const run=Array.from({length:c.count},(_,i)=>month>=p('D'+(54+i))?p('F'+(54+i)):0).reduce((a,b)=>a+b,0);
    let cpiGross=0,cpiCredit=0;
    if(c.name==='FLOW'){
      if(month<p('D54'))z[0]=t('H'+(35+Math.min(yi,4)))*price/12/1e6;
      z[1]=t('F30')*t('D12')*price*quantities*run/12/1e6;
      z[3]=val('Run Flow','G68')*val('Run Flow','H68')*services*run/12/1e6;
      z[4]=val('Run Flow','G45')*u('D39')*services*run/12/1e6;
      z[5]=val('Run Flow','G69')*val('Run Flow','H69')*services*run/12/1e6;
    }else if(c.name==='SAP'){
      const unitPrice=t('D65'),included=t('D66'),block=t('D67'),blockPrice=t('D68'),coefficient=t('D13')*quantities;
      const nonprod=month>=t('D73')?t('D69')*unitPrice+Math.ceil(Math.max(0,t('D71')*coefficient-t('D69')*included)/block)*blockPrice:0;
      const prod=month>=t('D74')?t('D70')*unitPrice+Math.ceil(Math.max(0,t('D72')*coefficient*run-t('D70')*included)/block)*blockPrice:0;
      cpiGross=(nonprod+prod)*Math.pow(1+t('D76'),yi)/1e6;
      cpiCredit=Math.min(cpiGross,t('D75')*Math.pow(1+t('D77'),yi)/12/1e6);
      z[2]=cpiGross-cpiCredit;
    }else{
      z[2]=t('D14')*(t('G90')+t('G91')*run)*price*quantities/12/1e6;
    }
    const exitRow=98+cases.indexOf(c);
    if(t('C'+exitRow)===1&&month+1===t('D'+exitRow))z[6]=t('G'+exitRow)*services/1e6;
    years[yi]=years[yi].map((x,i)=>x+z[i]);
    months.push({costs:z,run,cpiGross,cpiCredit});
  }
  return {years,months};
}

function oracle(c){
  const u=a=>val(c.u,a),p=a=>val(c.s,a),years=Array.from({length:15},()=>Array(9).fill(0));
  const technical=technicalOracle(c);
  const clientBuild=p('D81')+(c.name==='FLOW'&&p('D14')===2?p('D7')*p('C69'):0);
  near(p('D85'),clientBuild,`${c.name}: separate client Build base`);
  const lotTotal=Array.from({length:c.count},(_,i)=>p('E'+(54+i))).reduce((a,b)=>a+b,0);
  // Month 0 is the first month of project year 1. Licence price changes
  // at exact contract anniversaries. Source licence bases stay in project years.
  for(let month=0;month<180;month++){
    const yi=Math.floor(month/12),z=years[yi],serviceIndex=Math.pow(1+u('D43'),yi);let run=0;
    for(let l=54;l<54+c.count;l++){
      const begin=p('C'+l),end=p('D'+l);
      if(month>=begin&&month<end){
        z[0]+=p('E'+l)*serviceIndex/(end-begin);
        z[7]+=clientBuild*p('E'+l)/lotTotal*Math.pow(1+p('D83'),yi)/(end-begin);
      }
      if(month>=end)run+=p('F'+l);
    }
    if(month>=u('D38')){
      const age=Math.floor((month-u('D38'))/12),exponent=Math.max(0,age+1-Math.max(1,u('D46')));
      z[1]+=u('C'+(52+yi))*u('D47')*(1-u('D48'))*Math.pow(1+u('D44'),exponent)*Math.pow(1+u('D49'),yi)/12/1e6;
    }
    z[2]+=(u('D30')*u('D31')+u('D32'))*u('D39')*serviceIndex*run/12/1e6;
    z[3]+=c.name==='FLOW'?technical.months[month].costs[1]:u('D33')*Math.pow(1+u('D45'),yi)*run/12/1e6;
    const evo=c.name==='SAP'?Math.max(u('D34')*u('D35'),u('D28')):u('D34')*u('D35')+u('D28');
    z[4]+=evo*u('D39')*serviceIndex*run/12/1e6;
    z[5]+=u('D36')*serviceIndex*run/12/1e6;
    if(month===0)z[5]+=u('D37')/1e6;
    z[6]+=run/12;
    z[8]+=p('D82')*Math.pow(1+p('D83'),yi)*run/12;
  }
  if(c.name==='Microsoft')for(let yi=1;yi<15;yi++){
    const activeMonths=Math.max(0,Math.min(12,(yi+1)*12-u('D38')));
    years[yi][5]+=Math.max(u('D148')*u('D146')*activeMonths/12,u('D147')*u('D145')*years[yi][1]*1e6)/1e6;
  }
  years.forEach((z,yi)=>{z[0]+=technical.years[yi][0];});
  return years;
}
function verifyOracle(c,label){
  let cumBuild=0,cumRun=0,cumClient=0;
  const technical=technicalOracle(c);
  oracle(c).forEach((z,yi)=>{
    const row=c.start+yi+1,annual=z.slice(0,6);
    const extra=technical.years[yi][2]+technical.years[yi][3]+technical.years[yi][5]+technical.years[yi][6];
    cumBuild+=z[0];cumRun+=annual.slice(1).reduce((a,b)=>a+b,0)+extra;
    cumClient+=z[7]+z[8];
    ['C','D','E','F','G','H'].forEach((col,i)=>near(val('Calculs 15 ans',col+row),z[i],`${label} ${c.name} year ${yi+1}, ${col}`));
    ['U','V','W','X','Y','Z','AA'].forEach((col,i)=>near(val('Calculs 15 ans',col+row),technical.years[yi][i],`${label} ${c.name} year ${yi+1}, ${col}`));
    for(const [col,expected]of [['I',annual.reduce((a,b)=>a+b,0)+extra],['J',cumBuild],['K',cumRun],['L',cumBuild+cumRun],['M',z[6]]])near(val('Calculs 15 ans',col+row),expected,`${label} ${c.name} year ${yi+1}, ${col}`);
    for(const [col,expected]of [['N',z[7]+z[8]],['O',cumClient],['P',cumBuild+cumRun+cumClient],['Q',z[7]],['R',z[8]]])near(val('Calculs 15 ans',col+row),expected,`${label} ${c.name} year ${yi+1}, ${col}`);
  });
}
function bridgeOracle(c){
  const b=c.bridge,u=a=>val(c.u,a),q=a=>val('Passage Buy France',a);
  const factor='E',retraitFactor='E';
  const device=u('D8'),dev=u('D14');
  const base=u('D128')+u('D129')*u('D130');
  let gaps=0,transJH=0,transCost=0;
  const functions=functionalModel(c);
  for(let i=0;i<functions.data.items.length;i++)gaps+=q('J'+(functions.start+i))*q('C'+(functions.start+i))*q(factor+(functions.start+i));
  for(let i=0;i<8;i++){
    const row=b+5+i,jh=q('C'+row)*q(factor+row);
    transJH+=jh;transCost+=jh*(i===2||i===3?device:i===0||i===1?u('D15'):dev);
  }
  const removed=(c.name==='SAP'?2810:base)*q(retraitFactor+(b+17));
  const internal=(c.name==='SAP'?13993:(8*18+4*20)/12*200)*q('E'+(b+20));
  const autonomous=internal*q(factor+(b+21))*(1-removed/base);
  return {device,dev,base,gaps,transJH,transCost,removed,autonomous,budget:((base-removed+autonomous)*device+gaps*dev+transCost)/1e6};
}
test('Independent monthly Build, licence and Run recomputation',()=>{
  for(const c of cases){
    verifyOracle(c,'Baseline');
  }
});

test('Execution resources and construction bills remain distinct from the reconciled human-service abaque',()=>{
  const p=a=>val('Plateforme et exploitation',a);
  near(val('Charges Flow','E23'),32100,'FLOW nominal development effort is unchanged');
  near(val('Prix Flow','D7'),24.075,'FLOW labour-only nominal is unchanged');
  near(p('F30'),platformCosts.flow_runtime.annual_existing_eur,'FLOW existing resource provision is only itemised');
  near(p('F30'),400000,'FLOW resources remain 400 kEUR annually');
  for(let i=0;i<platformCosts.flow_runtime.items.length;i++)near(p('F'+(18+i)),p('C'+(18+i))*p('D'+(18+i))*12,`FLOW resource ${i} uses quantity times unit price`);
  for(const [i,amount]of [24000,36000,76000,94000,156000].entries())near(p('H'+(35+i)),amount,`FLOW construction resources project year ${i+1}`);
  near(p('H41'),386000,'FLOW five-year construction resources');
  near(val('Prix Flow','D13'),.386,'FLOW construction resource bills remain separate from JH');
  near(val('Run Flow','E28'),656,'FLOW maintenance and operations are calculated in one abaque');
  near(val('Run Flow','G28'),492000,'FLOW maintenance and operations annual cost');
  near(val('Run Flow','G45'),220500,'FLOW operations, including platform configuration and capacity reviews, are reclassified inside the 492 kEUR envelope');
  near(val('Run Flow','G68'),36000,'FLOW shared on-call availability is explicitly valued');
  near(val('Run Flow','H68'),0,'FLOW on-call option inactive');
  near(val('Run Flow','G69'),50000,'FLOW major migration option annual provision');
  near(val('Run Flow','H69'),0,'FLOW major migration inactive');
  near(val('Run Flow','G70'),125000,'SAP major migration option annual provision');
  near(val('Run Flow','H70'),0,'SAP major migration inactive');
  near(p('G79'),59195.04,'SAP non-production CPI annual base');
  near(p('G80'),92027.04,'SAP full-production CPI annual base');
  near(p('G81'),151222.08,'SAP full two-tenant CPI annual base before credit');
  near(p('G90'),12000,'Microsoft external non-production annual provision');
  near(p('G91'),33000,'Microsoft full external production annual provision');
  near(p('G92'),45000,'Microsoft external platform provision');
  near(p('D11'),0,'Technical quantity growth default is zero');
  for(const c of cases)near(val(c.u,'D49'),0,`${c.name} licence quantity growth default is zero`);
});

function verifyTechnicalMonthly(label){
  const results=cases.map(c=>technicalOracle(c));
  for(let month=0;month<180;month++){
    const row=8+month,flow=results[0].months[month],sap=results[1].months[month],ms=results[2].months[month];
    near(val('Coûts techniques mensuels','B'+row),month,`${label} technical month index`);
    near(val('Coûts techniques mensuels','C'+row),Math.floor(month/12)+1,`${label} technical project year`);
    const expected=[flow.costs[0],flow.costs[1],flow.costs[3],flow.costs[5],flow.costs[4],sap.cpiGross,sap.cpiCredit,sap.costs[2],ms.costs[2],flow.costs[6],sap.costs[6],ms.costs[6]];
    expected.forEach((x,i)=>near(val('Coûts techniques mensuels',String.fromCharCode(68+i)+row),x*1e6,`${label} technical month ${month}, component ${i}`,1e-6));
  }
}

test('New monthly technical owner is independently recomputed in euros and sums into annual costs once',()=>verifyTechnicalMonthly('Baseline'));

test('SaaS or RISE Core hosting is financed in subscriptions and receives no duplicate resource charge',()=>{
  for(const c of cases.slice(1)){
    near(sumCalc(c,'V'),0,`${c.name} has no duplicate standard Core hosting`);
    near(sumCalc(c,'X')+sumCalc(c,'Z'),0,`${c.name} has no generic FLOW operations or major renewal overlay`);
    near(structure(c,17,'C'),0,`${c.name} standard hosting is not added to initial construction`);
    near(structure(c,17,'H'),0,`${c.name} standard hosting is not added to cumulative execution resources`);
  }
  const text=cell('Comparaison','B1:I96').values.flat().filter(x=>typeof x==='string').join('\n');
  assert(/hébergement inclus|hébergement.*abonnement/i.test(text),'The inclusion of Buy standard hosting must remain explicit in the comparison');
});

test('Technical resource growth changes quantities without inflating labour, service forfaits or the explicit construction environment plan',()=>{
  const prior=cases.map(c=>({mco:sumCalc(c,'E'),evo:sumCalc(c,'G'),buildResources:sumCalc(c,'U')}));
  mutate('Plateforme et exploitation','D11',.05,()=>{
    cases.forEach((c,i)=>{
      near(sumCalc(c,'E'),prior[i].mco,`${c.name} technical growth must not inflate MCO JH`);
      near(sumCalc(c,'G'),prior[i].evo,`${c.name} technical growth must not inflate evolution JH`);
      near(sumCalc(c,'U'),prior[i].buildResources,`${c.name} explicit construction environment plan is unchanged`);
      verifyOracle(c,'5% technical quantity growth');verifyCostStructure(c,'5% technical quantity growth');
    });
    verifyTechnicalMonthly('5% technical quantity growth');
  });
});

test('Licence quantity growth is distinct from the contractual price freeze and feeds Microsoft support only through billed spend',()=>mutateMany(cases.map(c=>[c.u,'D49',.05]),()=>{
  for(const c of cases)verifyOracle(c,'5% licence quantity growth');
  const ms=cases[2],base=val(ms.u,'C53')*val(ms.u,'D47')*(1-val(ms.u,'D48'));
  near(val('Calculs 15 ans','D52'),base*1.05/1e6,'Microsoft quantities can grow in year 2 while the licence unit price is frozen');
}));

test('FLOW resource capacity sensitivity affects only post-delivery resource bills',()=>{
  const initial=val(cases[0].s,'D12'),old=val(cases[0].s,'H9'),others=cases.slice(1).map(c=>val(c.s,'H9'));
  mutate('Plateforme et exploitation','D12',.5,()=>{
    near(val(cases[0].s,'D12'),initial,'FLOW capacity does not change initial labour or construction resources');
    near(val(cases[0].s,'H9'),old-2,'Half FLOW resource capacity removes 200 kEUR per operating year');
    cases.slice(1).forEach((c,i)=>near(val(c.s,'H9'),others[i],`${c.name} is independent from FLOW resource capacity`));
    verifyOracle(cases[0],'FLOW half resource capacity');verifyCostStructure(cases[0],'FLOW half resource capacity');
  });
});

test('An extra FLOW construction environment is a resource invoice, outside nominal JH, Core effort and options basis',()=>{
  const initial=val(cases[0].s,'D12'),tco=val(cases[0].s,'H9'),core=val(cases[0].s,'D114'),nominal=val(cases[0].s,'D7');
  mutate('Plateforme et exploitation','C35',3,()=>{
    near(val(cases[0].s,'D12'),initial+.012,'FLOW additional year-1 environment cost');
    near(val(cases[0].s,'H9'),tco+.012,'FLOW additional construction resources counted once');
    near(val(cases[0].s,'D114'),core,'FLOW resource invoice is not Core software development');
    near(val(cases[0].s,'D7'),nominal,'FLOW resource invoice does not inflate the options labour basis');
    verifyOracle(cases[0],'FLOW extra construction environment');verifyCostStructure(cases[0],'FLOW extra construction environment');
  });
});

test('FLOW construction resource invoices stop at an earlier delivery and the operating costs start afterwards',()=>mutate('Prix Flow','D54',54,()=>{
  near(val('Prix Flow','D13'),.308,'FLOW resources stop halfway through the planned fifth year');
  near(sumCalc(cases[0],'M'),10.5,'FLOW earlier delivery provides 10.5 equivalent operating years');
  verifyOracle(cases[0],'FLOW delivery M54');verifyCostStructure(cases[0],'FLOW delivery M54');verifyTechnicalMonthly('FLOW delivery M54');
}));

test('FLOW activity changes propagate once, while maintenance and operations share one annual envelope',()=>{
  const old=val(cases[0].s,'H9');
  mutate('Run Flow','C12',0,()=>{
    near(val(cases[0].s,'H9'),old-.375,'Removing 50 operating JH/year removes 375 kEUR over ten operating years');
    verifyOracle(cases[0],'FLOW operation activity variation');verifyCostStructure(cases[0],'FLOW operation activity variation');
  });
  mutate('Run Flow','C20',60,()=>{
    near(val(cases[0].s,'H9'),old+.36,'Twenty-four extra flow recoveries at 2 JH increase total once, not twice');
    near(structure(cases[0],14,'D'),.1995,'FLOW application MCO is unchanged when operating work varies');
    near(structure(cases[0],19,'D'),.2565,'FLOW operations include the extra flow work exactly once');
    verifyOracle(cases[0],'FLOW flow reliability variation');verifyCostStructure(cases[0],'FLOW flow reliability variation');
  });
});

test('FLOW major renewal is inactive by default, option only, and does not duplicate continuing Core versions',()=>{
  const old=val(cases[0].s,'H9');
  mutate('Run Flow','H69',1,()=>{
    near(val(cases[0].s,'H9'),old+.5,'Enabling major renewal adds 50 kEUR per operating year');
    near(structure(cases[0],9,'D'),.162,'Current Core versions remain funded when exceptional renewal is removed');
    near(structure(cases[0],21,'D'),.05,'Major migration remains separately visible in options');
    verifyOracle(cases[0],'FLOW major renewal option');verifyCostStructure(cases[0],'FLOW major renewal option');
  });
});

test('FLOW on-call and SAP major migrations are independent optional service additions',()=>{
  const flow=val(cases[0].s,'H9'),sap=val(cases[1].s,'H9'),ms=val(cases[2].s,'H9');
  mutate('Run Flow','H68',1,()=>{
    near(val(cases[0].s,'H9'),flow+.36,'FLOW on-call option over ten operating years');
    near(val(cases[1].s,'H9'),sap,'FLOW on-call does not alter SAP');
    near(val(cases[2].s,'H9'),ms,'FLOW on-call does not alter Microsoft');
    verifyOracle(cases[0],'FLOW on-call option');verifyCostStructure(cases[0],'FLOW on-call option');
  });
  mutate('Run Flow','H70',1,()=>{
    near(val(cases[1].s,'H9'),sap+1.5875,'SAP optional major migrations prorated to 12.7 operating years');
    near(val(cases[0].s,'H9'),flow,'SAP migration option does not alter FLOW');
    near(val(cases[2].s,'H9'),ms,'SAP migration option does not alter Microsoft');
    verifyOracle(cases[1],'SAP major migration option');verifyCostStructure(cases[1],'SAP major migration option');
  });
});

test('SAP CPI tenant fixed costs start at first uses while message charges follow the deployed scope',()=>{
  const p=a=>val('Plateforme et exploitation',a);
  near(val('Coûts techniques mensuels','I25'),59195.04/12*1.04,'SAP month 17 funds only the recipe tenant at year-2 prices');
  near(val('Coûts techniques mensuels','I26'),(59195.04/12+4635+99*6.08)*1.04,'SAP month 18 funds the full production tenant and 20% messages');
  mutate('Plateforme et exploitation','D13',0,()=>{
    const expectedFirst=(p('D65')*p('D69'))/1e6;
    near(technicalOracle(cases[1]).months[0].costs[2],expectedFirst,'SAP zero messages still pays the recipe tenant');
    verifyOracle(cases[1],'SAP zero messages');verifyTechnicalMonthly('SAP zero messages');
  });
});

test('SAP imputed BTP credit is deducted once and cannot turn platform cost negative or change the subscription source',()=>{
  const old=val(cases[1].s,'H9'),net=sumCalc(cases[1],'W'),licences=sumCalc(cases[1],'D');
  mutate('Plateforme et exploitation','D75',500000,()=>{
    near(sumCalc(cases[1],'W'),0,'Large imputed credit caps net CPI at zero');
    near(val(cases[1].s,'H9'),old-net,'SAP TCO deducts only the previously added CPI bill');
    near(sumCalc(cases[1],'D'),licences,'BTP credit is not deducted from the RFI subscription a second time');
    verifyOracle(cases[1],'SAP BTP credit');verifyCostStructure(cases[1],'SAP BTP credit');verifyTechnicalMonthly('SAP BTP credit');
  });
});

test('SAP CPI prices, billable messages and BTP credits use separate sensitivity and indexation drivers',()=>mutateMany([['Plateforme et exploitation','D13',.25],['Plateforme et exploitation','D75',50000],['Plateforme et exploitation','D76',.08],['Plateforme et exploitation','D77',.03]],()=>{
  verifyOracle(cases[1],'SAP CPI independent drivers');verifyCostStructure(cases[1],'SAP CPI independent drivers');verifyTechnicalMonthly('SAP CPI independent drivers');
}));

test('Microsoft conditional external platform can be cancelled without changing hosted standard, development or application maintenance',()=>{
  const old=val(cases[2].s,'H9'),initial=val(cases[2].s,'D12'),licences=sumCalc(cases[2],'D'),mco=sumCalc(cases[2],'E');
  mutate('Plateforme et exploitation','D14',0,()=>{
    near(val(cases[2].s,'H9'),old-.5947,'Microsoft conditional external platform removed once');
    near(val(cases[2].s,'D12'),initial,'Microsoft external hosting does not rebuild the standard');
    near(sumCalc(cases[2],'D'),licences,'Microsoft base subscription preserved');
    near(sumCalc(cases[2],'E'),mco,'Microsoft maintenance effort preserved');
    verifyOracle(cases[2],'Microsoft external platform covered by subscription');verifyCostStructure(cases[2],'Microsoft external platform covered by subscription');verifyTechnicalMonthly('Microsoft external platform covered by subscription');
  });
});

for(const [i,c]of cases.entries())test(`${c.name}: exit is inactive by default and an explicit end-of-horizon exit is added only once`,()=>{
  near(sumCalc(c,'AA'),0,`${c.name} exit default`);
  const old=val(c.s,'H9'),initial=val(c.s,'D12'),cost=val('Plateforme et exploitation','G'+(98+i))/1e6;
  mutate('Plateforme et exploitation','C'+(98+i),1,()=>{
    near(val(c.s,'H9'),old+cost,`${c.name} selected exit cost`);
    near(val(c.s,'D12'),initial,`${c.name} selected exit does not change the initial realization cost`);
    near(val('Calculs 15 ans','AA'+(c.start+15)),cost,`${c.name} exit at M180 is charged in project year 15`);
    verifyOracle(c,`${c.name} selected exit`);verifyCostStructure(c,`${c.name} selected exit`);verifyTechnicalMonthly(`${c.name} selected exit`);
  });
});

test('France device prices are derived from explicit role mixes and raw RFI prices are preserved',()=>{
  near(val('Prix SAP','D7'),13.462352,'SAP raw RFI price');
  near(val('Prix Microsoft','D7'),4.24,'Microsoft raw RFI price');
  for(const [c,expected]of [[cases[1],1000],[cases[2],1000]]){
    const mixed=Array.from({length:5},(_,i)=>val(c.u,'C'+(115+i))*val(c.u,'D'+(115+i))).reduce((a,b)=>a+b,0);
    near(val(c.u,'E121'),mixed,`${c.name} role mix weighted rate`);
    near(val(c.u,'D8'),Math.round(mixed/val(c.u,'D122'))*val(c.u,'D122'),`${c.name} rounded France supplier rate`);
    near(val(c.u,'D8'),expected,`${c.name} France baseline device rate`);
    near(mixed,997.5,`${c.name} explicit specialist-team weighted tariff`);
    near(val(c.u,'D14'),850,`${c.name} France software-specialist development rate`);
    near(val(c.u,'D15'),750,`${c.name} generic Java and automated-test development rate`);
    near(val(c.u,'D15'),val('Prix unitaire Flow','D20'),`${c.name} generic technical work uses the same price basis as FLOW`);
  }
});

test('Generic Java and automated-test work uses the FLOW technical rate rather than a software-specialist premium',()=>{
  near(val('Passage Buy France','H63'),750,'Microsoft automated-test foundation generic daily rate');
  near(val('Passage Buy France','H64'),750,'Microsoft automated-test chains generic daily rate');
  near(val('Passage Buy France','I73'),.675,'Microsoft additional tests and adoption cost');
  const sapInitial=val('Prix SAP','D12'),msInitial=val('Prix Microsoft','D12');
  mutate('Prix unitaire Flow','D20',800,()=>{
    for(const c of cases.slice(1)){
      near(val(c.u,'D15'),800,`${c.name} generic rate follows FLOW rate`);
      near(val(c.u,'D14'),850,`${c.name} specialist rate remains independent from generic development`);
    }
    near(val('Prix SAP','D12'),sapInitial,'SAP has no active additional generic service budget');
    near(val('Prix Microsoft','D12'),msInitial+420*50/1e6,'Microsoft only additional generic-test effort is repriced');
    for(const c of cases.slice(1))verifyOracle(c,'Common generic development rate variation');
  });
});

test('Core construction is separate from total initial realization and is zero for the Buy product cores',()=>{
  const coreJH=Array.from({length:14},(_,i)=>val('Charges Flow','E'+(8+i))*val('Charges Flow','F'+(8+i))).reduce((a,b)=>a+b,0);
  near(coreJH,20345,'FLOW Core construction JH');
  near(val('Prix Flow','D114'),coreJH*val('Prix unitaire Flow','D20')/1e6,'FLOW Core cost from weighted work-package attribution');
  near(val('Prix Flow','D114'),15.25875,'FLOW Core baseline');
  near(val('Prix Flow','D115'),8.81625,'FLOW configuration, integration and other initial activities');
  for(const c of cases){
    if(c.name!=='FLOW')near(val(c.s,'D114'),0,`${c.name} vendor Core is not built by the project`);
    near(val(c.s,'D116'),val(c.s,'D9'),`${c.name} Core plus other activities reconcile to initial base cost`);
    near(structure(c,9),val(c.s,'D114'),`${c.name} Core cost in common cost structure`);
    near(structure(c,22),val(c.s,'D12'),`${c.name} structure reconciles to initial realization cost`);
    near(comp(c,22),val(c.s,'D12'),`${c.name} compared full initial realization cost`);
  }
  assert(String(val('Comparaison','B44')).includes('Core'),'Core construction needs its own comparison row');
});

test('Reallocating a valid FLOW attribution key transfers cost between Core and implementation without changing the price',()=>{
  const oldCore=val('Prix Flow','D114'),oldOther=val('Prix Flow','D115'),oldTotal=val('Prix Flow','D9'),oldTco=val('Prix Flow','H9');
  mutateMany([['Charges Flow','F8',.4],['Charges Flow','G8',.25]],()=>{
    const delta=1400*.1*750/1e6;
    near(val('Prix Flow','D114'),oldCore+delta,'More product construction, same total effort');
    near(val('Prix Flow','D115'),oldOther-delta,'Less configuration after attribution transfer');
    near(val('Prix Flow','D9'),oldTotal,'Attribution transfer changed initial total');
    near(val('Prix Flow','H9'),oldTco,'Attribution transfer changed TCO');
  });
});

for(const c of cases)test(`${c.name}: manual project supplement is excluded from Core and reconciles to initial realization`,()=>{
  const core=val(c.s,'D114'),base=val(c.s,'D12')-val(c.s,'D10'),old=val(c.s,'D10');
  mutate(c.s,'D10',old+.5,()=>{
    near(val(c.s,'D114'),core,`${c.name} project supplement inflated Core`);
    near(val(c.s,'D10'),old+.5,`${c.name} manual supplement is separately identified on its budget sheet`);
    near(comp(c,22),base+old+.5,`${c.name} initial realization includes supplement once`);
    near(structure(c,9),core,`${c.name} Core is unchanged by the project supplement`);
  });
});

for(const c of cases.slice(1))test(`${c.name}: bridge from RFI to France reconciles missing activities, deductions and autonomy`,()=>{
  const q=a=>val('Passage Buy France',a),b=c.bridge,expected=bridgeOracle(c);
  for(const [offset,jh]of [[14,expected.gaps],[15,expected.transJH],[17,expected.removed],[19,expected.base],[21,expected.autonomous]])near(q('G'+(b+offset)),jh,`${c.name} bridge JH row ${b+offset}`);
  near(q('I'+(b+14)),expected.gaps*expected.dev/1e6,`${c.name} gap budget`);
  near(q('I'+(b+15)),expected.transCost/1e6,`${c.name} transverse budget with change at device rate`);
  near(q('I'+(b+31)),expected.budget,`${c.name} full comparable Build`);
  near(val(c.s,'D9'),expected.budget,`${c.name} comparable Build reaches summary`);
  for(const [row,off]of [[97,26],[98,27],[99,28],[100,29],[101,30]])near(val(c.s,'D'+row),q('I'+(b+off)),`${c.name} budget sheet links to detailed price explanation row ${row}`);
  near(val(c.s,'D102'),expected.budget,`${c.name} detailed initial price reconciliation total`);
});

for(const c of cases.slice(1))test(`${c.name}: functional effort and maintenance follow explicit units, unit effort and activation`,()=>{
  const model=functionalModel(c),index=model.data.items.findIndex(x=>x.activation===1&&Number.isFinite(x.effort[1]));
  assert(index>=0,`No active ${c.name} function can exercise a one-JH unit effort change`);
  const row=model.start+index,quantity=val('Passage Buy France','C'+row),effort=val('Passage Buy France','E'+row),oldMco=val(c.u,'D136');
  mutate('Passage Buy France','E'+row,effort+1,()=>{
    near(val(c.u,'D136'),oldMco+quantity*val(c.u,'D134'),`${c.name} MCO follows additional functional construction JH`);
    near(val(c.s,'D9'),bridgeOracle(c).budget,`${c.name} functional effort reaches initial realization summary`);
    verifyOracle(c,`${c.name} unit effort variation`);
  });
  mutate('Passage Buy France','J'+row,0,()=>{
    near(val('Passage Buy France','G'+row),0,`${c.name} inactive function costs zero`);
    near(val(c.u,'D136'),oldMco-quantity*effort*val(c.u,'D134'),`${c.name} MCO removes inactive new-function maintenance`);
    near(val(c.s,'D9'),bridgeOracle(c).budget,`${c.name} deactivation reaches initial realization summary`);
    verifyOracle(c,`${c.name} function deactivation`);
  });
});

for(const c of cases.slice(1))test(`${c.name}: functional complements have documented scope and no dependency on percentages of Make effort`,()=>{
  const model=functionalModel(c);
  for(let i=0;i<model.data.items.length;i++){
    const row=model.start+i,item=model.data.items[i];
    for(const field of ['coverage','gap','unit'])assert(typeof item[field]==='string'&&item[field].length>0,`${c.name} function row ${row}: missing ${field}`);
    for(const field of ['source','exclusions'])assert(Array.isArray(item[field])&&item[field].length>0,`${c.name} function row ${row}: missing ${field}`);
    near(val('Passage Buy France','G'+row),val('Passage Buy France','J'+row)*val('Passage Buy France','C'+row)*val('Passage Buy France','E'+row),`${c.name} explicit function JH row ${row}`);
  }
  for(const range of [`C${c.bridge}:O${c.bridge+3}`,`C${model.start}:O${model.start+model.data.items.length-1}`])assert(!cell('Passage Buy France',range).formulas.flat().some(x=>typeof x==='string'&&x.includes('Charges Flow')),`${c.name} functional effort still references Make work packages`);
  const gap=val('Passage Buy France','G'+(c.bridge+14)),initial=val(c.s,'D9'),jh=val('Charges Flow','E10');
  mutate('Charges Flow','E10',jh+1000,()=>{
    near(val('Passage Buy France','G'+(c.bridge+14)),gap,`${c.name} functional complement changed with Make inventory effort`);
    near(val(c.s,'D9'),initial,`${c.name} initial cost changed with Make inventory effort`);
  });
});

test('SAP avoids generic duplicate supplements for migration, interfaces, security, qualification and unproven TNR omissions',()=>{
  for(const row of [13,14,17,18,19,20])near(val('Passage Buy France','C'+row),0,`SAP supplementary activity row ${row} is not proven additional`);
  near(val('Passage Buy France','G23'),360,'SAP remaining conditional change effort');
  near(val('Passage Buy France','I23'),.36,'SAP remaining change provision at device rate');
  for(const [address,jh]of [['C27',1467],['C28',204],['C29',1319]])near(val('Références',address),jh,`SAP source ${address} retains included WRICEF signal`);
});

for(const c of cases.slice(1))test(`${c.name}: deactivating all functional complements preserves the RFI core and removes only new construction and its maintenance`,()=>{
  const model=functionalModel(c),source=val(c.s,'D7'),extraInterfaces=val('Passage Buy France','G'+(c.bridge+9));
  mutateMany(model.data.items.map((_,i)=>['Passage Buy France','J'+(model.start+i),0]),()=>{
    near(val('Passage Buy France','G'+(c.bridge+14)),0,`${c.name} no additional functions`);
    near(val(c.u,'D136'),extraInterfaces*val(c.u,'D135'),`${c.name} only maintenance of genuinely new interfaces remains`);
    near(val(c.s,'D7'),source,`${c.name} functional activation changed historical RFI price`);
    near(val(c.s,'D114'),0,`${c.name} vendor Core became a construction project`);
    near(val(c.s,'D9'),bridgeOracle(c).budget,`${c.name} deactivated initial realization price`);
    if(c.name==='SAP')near(val(c.u,'D26'),250000,'SAP source MCO forfait remains funded without unsupported rate revaluation');
    verifyOracle(c,'All new functional complements deactivated');
  });
});

for(const c of cases.slice(1))test(`${c.name}: explicitly adding new interfaces changes initial effort and maintenance only for the new contracts`,()=>{
  const row=c.bridge+9,previous=val(c.u,'D136');
  mutate('Passage Buy France','C'+row,2,()=>{
    near(val(c.u,'D136'),previous+2*20*.05,`${c.name} new-interface annual maintenance`);
    near(val(c.s,'D9'),bridgeOracle(c).budget,`${c.name} new-interface initial realization`);
    verifyOracle(c,'Explicit additional interfaces');
  });
});

for(const c of cases.slice(1))test(`${c.name}: supplier autonomy is limited to initially client-owned IT on the operational RFI core`,()=>{
  const baseSource=val('Passage Buy France','G'+(c.bridge+19)),internalSource=val('Passage Buy France','C'+(c.bridge+20));
  mutate('Passage Buy France','E'+(c.bridge+21),0,()=>{
    near(val('Passage Buy France','G'+(c.bridge+21)),0,`${c.name} no transferred client IT`);
    near(val(c.s,'D9'),bridgeOracle(c).budget,`${c.name} zero autonomy budget`);
    near(val('Passage Buy France','G'+(c.bridge+19)),baseSource,`${c.name} transfer does not change RFI source JH`);
    near(val('Passage Buy France','C'+(c.bridge+20)),internalSource,`${c.name} transfer does not change source client JH`);
    verifyOracle(c,'Zero autonomy transfer');
  });
});

for(const c of cases.slice(1))test(`${c.name}: higher development and device prices propagate into Build, MCO and evolutions`,()=>mutate(c.u,'D14',1200,()=>{
  near(val(c.s,'D9'),bridgeOracle(c).budget,`${c.name} modified rate reaches full comparable Build`);
  verifyOracle(c,'France development rate variation');
}));

test('Microsoft additional-pole assumptions affect source effort, Finance withdrawal and supplier autonomy consistently',()=>mutate(cases[2].u,'D130',500,()=>{
  near(val('Passage Buy France','G77'),4300,'Microsoft recomposed base JH');
  near(val('Passage Buy France','G75'),430,'Microsoft Finance withdrawal follows base JH');
  near(val('Prix Microsoft','D9'),bridgeOracle(cases[2]).budget,'Microsoft revised comparable Build');
  verifyOracle(cases[2],'Microsoft pole effort variation');
}));

test('Non-zero service and infrastructure indexation',()=>mutateMany(cases.flatMap(c=>[[c.u,'D43',.05],[c.u,'D45',.08]]),()=>{
  for(const c of cases)verifyOracle(c,'5% services / 8% infrastructure');
}));

test('Each solution uses its own MCO and evolution abaque including France and new extensions',()=>{
  for(const [c,jhMco,jhEvo,mco,evo,infra]of [[cases[0],656,320,492000,240000,400000],[cases[1],16.44,420,263974,357000,450000],[cases[2],337.17,440,286594.5,374000,450000]]){
    const u=a=>val(c.u,a);
    near(u('D30'),jhMco,`${c.name}: MCO volume`);
    near(u('D34'),jhEvo,`${c.name}: evolution volume`);
    near(u('D26'),mco,`${c.name}: annual MCO`);
    near(u('D27'),evo,`${c.name}: annual evolutions`);
    near(u('D33'),infra,`${c.name}: infrastructure or monitoring`);
    near(u('D31'),u('D35'),`${c.name}: MCO and development rates aligned`);
    const extra=c.name==='FLOW'?val('Run Flow','G68')*val('Run Flow','H68')+val('Run Flow','G69')*val('Run Flow','H69'):c.name==='SAP'?val('Plateforme et exploitation','G81'):val('Plateforme et exploitation','G92');
    near(val(c.s,'H10'),((mco+evo)*u('D39')+infra+u('D36')+(c.name==='Microsoft'?u('D149'):0)+extra)/1e6,`${c.name}: displayed full annual Run`);
  }
});

test('SAP sourced Run forfaits are kept at quoted values, without unsupported tariff or location uplift',()=>{
  for(const [source,target,amount]of [['C81','D32',250000],['C83','D28',350000],['C82','D33',450000]]){
    near(val('Références',source),amount,`SAP reference ${source}`);
    near(val(cases[1].u,target),amount,`SAP retained source forfait ${target}`);
  }
  for(const address of ['D76','D77','D78'])near(val(cases[1].u,address),1,`SAP ${address}: no unsubstantiated uplift`);
  for(const [address,target,amount]of [['D76','D32',250000],['D77','D28',350000],['D78','D33',450000]])mutate(cases[1].u,address,1.3,()=>{
    near(val(cases[1].u,target),amount*1.3,`SAP ${address} service coefficient`);
    verifyOracle(cases[1],`SAP service coefficient ${address}`);
  });
});

test('Changing specialist prices reprices new work without retroactively repricing sourced SAP Run forfaits',()=>{
  mutate(cases[1].u,'D14',900,()=>{
    near(val(cases[1].u,'D32'),250000,'SAP source MCO stays at the quoted forfait');
    near(val(cases[1].u,'D28'),350000,'SAP source TMA stays at the quoted forfait');
    near(val(cases[1].u,'D33'),450000,'SAP source monitoring stays at the quoted forfait');
    near(val(cases[1].u,'D26'),250000+16.44*900,'Only new functional maintenance is repriced');
    near(val(cases[1].u,'D27'),Math.max(350000,420*900),'Evolution demand and source TMA floor overlap rather than accumulate');
    verifyOracle(cases[1],'Specialist price changed, source forfaits preserved');
  });
  near(val(cases[2].u,'D105'),1,'Microsoft monitoring proxy has no unsupported uplift');
  near(val(cases[2].u,'D33'),450000,'Microsoft monitoring proxy equals the unchanged SAP service reference');
});

test('Common initial cost categories conserve the existing budgets and funded activities',()=>{
  for(const [row,amount]of [[9,15.25875],[10,3.72],[11,2.84625],[12,0],[13,2.25]])near(structure(cases[0],row),amount,`FLOW explicit initial category row ${row}`);
  for(const c of cases.slice(1)){
    const q=a=>val('Passage Buy France',a),b=c.bridge,u=a=>val(c.u,a),base=bridgeOracle(c).base;
    let shares;
    if(c.name==='SAP'){
      const remaining=base-1319-1467-204-421;
      shares=[1467/base,remaining*.7/base,1319/base,(204+421+remaining*.3)/base];
    }else{
      const pilot=u('D128'),rollout=u('D129')*u('D130');
      shares=[(pilot*460/2300+rollout*.2)/base,(pilot*630/2300+rollout*.55)/base,pilot*230/2300/base,(pilot*980/2300+rollout*.25)/base];
    }
    near(shares.reduce((a,x)=>a+x,0),1,`${c.name} RFI cost allocation sums to one`);
    const baseNet=q('I'+(b+19))-q('I'+(b+17)),it=q('I'+(b+21));
    const expected=[
      baseNet*shares[0]+it*.4+q('I'+(b+9))+q('I'+(b+10)),
      baseNet*shares[1]+it*.2+q('I'+(b+7))+q('I'+(b+8)),
      baseNet*shares[2]+q('I'+(b+14)),
      baseNet*shares[3]+it*.4+q('I'+(b+5))+q('I'+(b+6))+q('I'+(b+11))+q('I'+(b+12))
    ];
    near(structure(c,9),0,`${c.name} does not rebuild the vendor product Core`);
    expected.forEach((amount,i)=>near(structure(c,10+i),amount,`${c.name} allocated initial activity row ${10+i}`));
    near(expected.reduce((a,x)=>a+x,0),val(c.s,'D9'),`${c.name} allocation does not add a second implementation`);
  }
});

function verifyCostStructure(c,label){
  const horizons=[['E',3],['F',5],['G',10],['H',15]],initialRows=[9,10,11,12,13,21];
  const recurring=(row,fromYear,toYear)=>{
    const z=col=>sumCalc(c,col,fromYear,toYear);
    if(row===9)return z('S')+z('T');
    if(row===14)return z('E')-z('S')-z('Y');
    if(row===15)return z('G')-z('T');
    if(row===16)return z('D');
    if(row===17)return z('V');
    if(row===18)return z('W');
    if(row===19)return c.name==='FLOW'?z('Y'):z('F');
    if(row===20)return z('H')-z('AB');
    if(row===21)return z('AA')+z('X')+z('Z')+z('AB');
    return 0;
  };
  for(const col of ['C','D','E','F','G','H'])near(Array.from({length:13},(_,i)=>structure(c,9+i,col)).reduce((a,x)=>a+x,0),structure(c,22,col),`${label} ${c.name}: categories reconcile in column ${col}`);
  near(structure(c,22),val(c.s,'D12'),`${label} ${c.name}: initial total`);
  near(structure(c,22,'D'),annualRunMean(c),`${label} ${c.name}: annual mean after complete deployment`);
  near(structure(c,17,'C'),sumCalc(c,'U'),`${label} ${c.name}: initial execution platform bills are separate from supplier labour`);
  for(const row of [14,15,16,18,19,20])near(structure(c,row,'C'),0,`${label} ${c.name}: future recurring cost is excluded from initial realization row ${row}`);
  for(let row=9;row<=21;row++)near(structure(c,row,'D'),recurring(row,6,15)/10,`${label} ${c.name}: mean category row ${row} is counted once`);
  for(const [col,y]of horizons){
    near(structure(c,22,col),val('Calculs 15 ans','L'+(c.start+y)),`${label} ${c.name}: cost structure ${y}-year total`);
    const initialLabour=val(c.s,'D12')-val(c.s,'D13'),initialLabourThroughHorizon=sumCalc(c,'C',1,y)-sumCalc(c,'U',1,y);
    for(let row=9;row<=21;row++){
      const initial=row===17?sumCalc(c,'U',1,y):initialRows.includes(row)?structure(c,row,'C')/initialLabour*initialLabourThroughHorizon:0;
      near(structure(c,row,col),initial+recurring(row,1,y),`${label} ${c.name}: initial and recurring category ${row} at ${y} years without double counting cloud bills`);
    }
  }
  near(comp(c,22),val(c.s,'D12'),`${label} ${c.name}: initial executive summary`);
  near(comp(c,23),annualRunMean(c),`${label} ${c.name}: recurring executive summary`);
  for(const [row,y]of [[26,3],[27,5],[28,10],[29,15]])near(comp(c,row),val('Calculs 15 ans','L'+(c.start+y)),`${label} ${c.name}: ${y}-year executive total`);
  for(let costIndex=0;costIndex<14;costIndex++)for(const [executiveCol,structureCol]of [['D','C'],['E','D'],['F','E'],['G','F'],['H','G'],['I','H']])near(val('Comparaison',executiveCol+matrixRow(c,costIndex)),structure(c,9+costIndex,structureCol),`${label} ${c.name}: all horizons are visible together, cost category ${costIndex}, ${executiveCol}`);
}

test('Cost structure reconciles initial realization, recurring mean and all four cumulative horizons',()=>{
  for(const c of cases)verifyCostStructure(c,'Baseline');
});

test('The first comparison table displays every period side by side for every cost category and option',()=>{
  for(const c of cases)verifyCostStructure(c,'All-period executive matrix');
  const headings=cell('Comparaison','B7:I8').values.flat().filter(x=>typeof x==='string').join('\n');
  assert(/initial/i.test(headings),'Initial realization period is missing from the first table');
  assert(/annuel|moyen/i.test(headings),'Annual recurring average is missing from the first table');
  for(const year of [3,5,10,15])assert(headings.includes(String(year)),`${year}-year cumulative column is missing from the first table`);
});

test('Continuing FLOW Core versions remain financed once while exceptional services are inactive options',()=>{
  near(structure(cases[0],9,'D'),.162,'FLOW mean annual continuing Core excludes optional major renewal and platform operations');
  near(structure(cases[0],14,'D'),.1995,'FLOW mean annual MCO after separate Core and operations presentation');
  near(structure(cases[0],15,'D'),.150,'FLOW mean annual business changes after separate Core presentation');
  near(sumCalc(cases[0],'S',6,15)/10,.072,'FLOW Core technical lifecycle: 96 JH annually at 750 euro');
  near(sumCalc(cases[0],'T',6,15)/10,.09,'FLOW Core functional versions: 120 JH annually at 750 euro');
  near(structure(cases[0],19,'D'),.2205,'FLOW operating services are a category inside the single human-service abaque');
  near(structure(cases[0],22,'D'),1.132,'FLOW annual costs include 656 JH of maintenance and operations, 320 JH of evolutions and 400 kEUR resources');
  for(const c of cases)for(let year=0;year<=15;year++){
    const row=c.start+year,s=val('Calculs 15 ans','S'+row),t=val('Calculs 15 ans','T'+row);
    assert(finite(s)&&finite(t)&&s>=0&&t>=0,`${c.name} year ${year}: invalid Core lifecycle allocation`);
    assert(s<=val('Calculs 15 ans','E'+row)+1e-8&&t<=val('Calculs 15 ans','G'+row)+1e-8,`${c.name} year ${year}: Core exceeds the envelope it is allocated from`);
    if(c.name!=='FLOW')near(s+t,0,`${c.name}: vendor product development is not an extra client Core build`);
  }
});

test('Annual mean includes licence inflation and responds to both service and licence indexation',()=>mutateMany(cases.flatMap(c=>[[c.u,'D43',.03],[c.u,'D44',.07]]),()=>{
  for(const c of cases){verifyOracle(c,'Indexed annual mean');verifyCostStructure(c,'Indexed annual mean');}
}));

test('Executive labels name funded activities and the common averaging period without opaque model language',()=>{
  const text=cell('Comparaison','B1:I86').values.flat().filter(x=>typeof x==='string').join('\n');
  for(const phrase of ['socle recomposé','France / socle','Autonomie du dispositif fournisseur','Autres coûts initiaux','Run équiv.','borne basse','borne haute'])assert(!text.toLowerCase().includes(phrase.toLowerCase()),`Opaque or retired executive label remains: ${phrase}`);
  for(const pattern of [/core/i,/flux/i,/business/i,/spécif|specific/i,/licence/i,/pilotage/i])assert(pattern.test(text),`Funded activity missing from executive comparison: ${pattern}`);
  assert(/6\s*(?:[–-]|à)\s*15/.test(text),'Average annual comparison needs an explicit common averaging period');
  assert(!text.toLowerCase().includes('is not implemented'),'An unsupported function is displayed on the executive comparison');
});

function verifyMonthlyTrajectory(c,label){
  const index=cases.indexOf(c),initialCol=['D','G','J'][index],runCol=['E','H','K'][index],totalCol=['F','I','L'][index];
  let previousInitial=0,previousRun=0;
  near(val('Trajectoire mensuelle',totalCol+'8'),0,`${label} ${c.name}: no expenditure before the launch month`);
  for(let month=0;month<=180;month++){
    const row=8+month;
    near(val('Trajectoire mensuelle','B'+row),month,`${label}: month sequence row ${row}`);
    near(val('Trajectoire mensuelle','C'+row),month/12,`${label}: year coordinate row ${row}`);
    if(month>0){
      const initial=val('Trajectoire mensuelle',initialCol+row),run=val('Trajectoire mensuelle',runCol+row);
      assert(finite(initial)&&initial>=previousInitial-1e-8&&finite(run)&&run>=previousRun-1e-8,`${label} ${c.name}: invalid or decreasing monthly cumulative cost at month ${month}`);
      near(val('Trajectoire mensuelle',totalCol+row),initial+run,`${label} ${c.name}: monthly cumulative cost at month ${month}`);
      previousInitial=initial;previousRun=run;
    }
    if(month%12===0)near(val('Trajectoire mensuelle',totalCol+row),val('Calculs 15 ans','L'+(c.start+month/12)),`${label} ${c.name}: monthly curve reconciles to year ${month/12}`);
  }
  for(let year=1;year<=15;year++){
    const initial=val('Trajectoire mensuelle',initialCol+(8+year*12))-val('Trajectoire mensuelle',initialCol+(8+(year-1)*12));
    const run=val('Trajectoire mensuelle',runCol+(8+year*12))-val('Trajectoire mensuelle',runCol+(8+(year-1)*12));
    near(initial,val('Calculs 15 ans','C'+(c.start+year)),`${label} ${c.name}: annual initial cashflow ${year}`);
    near(run,runColumns.reduce((a,col)=>a+val('Calculs 15 ans',col+(c.start+year)),0),`${label} ${c.name}: annual Run cashflow ${year}`);
  }
}

const markerRows=[{c:cases[0],row:194,key:'full'},{c:cases[1],row:195,key:'first'},{c:cases[1],row:196,key:'full'},{c:cases[2],row:197,key:'first'},{c:cases[2],row:198,key:'full'}];
function verifyMilestoneMarkers(label){
  for(const {c,row,key}of markerRows){
    const month=deliveryMilestones(c)[key],totalCol=['F','I','L'][cases.indexOf(c)];
    near(val('Trajectoire mensuelle','C'+row),month,`${label} ${c.name}: ${key} operational marker month`);
    near(val('Trajectoire mensuelle','D'+row),month/12,`${label} ${c.name}: ${key} marker year coordinate`);
    near(val('Trajectoire mensuelle','E'+row),val('Trajectoire mensuelle',totalCol+(8+month)),`${label} ${c.name}: ${key} marker is placed on the actual cost curve`);
    assert(typeof val('Trajectoire mensuelle','F'+row)==='string'&&val('Trajectoire mensuelle','F'+row).length>0,`${label} ${c.name}: missing milestone label`);
  }
}

test('Monthly cost trajectories reconcile to annual budgets, licences and Run at every year end',()=>{
  for(const c of cases)verifyMonthlyTrajectory(c,'Baseline');
});
test('Operational value milestones follow delivered scope and exclude SAP technical upgrade',()=>{
  near(deliveryMilestones(cases[0]).first,60,'FLOW single first delivery');
  near(deliveryMilestones(cases[1]).first,18,'SAP upgrade at month 6 is not operational scope');
  near(deliveryMilestones(cases[1]).full,30,'SAP full operational delivery');
  near(deliveryMilestones(cases[2]).first,18,'Microsoft first operational delivery');
  near(deliveryMilestones(cases[2]).full,38,'Microsoft full operational delivery');
  verifyMilestoneMarkers('Baseline');
});
for(const [c,address,month]of [[cases[0],'D54',66],[cases[1],'D55',24],[cases[2],'D58',44]])test(`${c.name}: milestones and monthly expenditure respond to delivery changes`,()=>mutate(c.s,address,month,()=>{
  verifyOracle(c,'Delivery variation');verifyMonthlyTrajectory(c,'Delivery variation');verifyMilestoneMarkers('Delivery variation');verifyCostStructure(c,'Delivery variation');
}));

test('Monthly curves and annual means also reconcile with non-zero services, technical and licence inflation',()=>mutateMany(cases.flatMap(c=>[[c.u,'D43',.02],[c.u,'D44',.06],[c.u,'D45',.03]]),()=>{
  for(const c of cases){verifyOracle(c,'Monthly indexed trajectory');verifyMonthlyTrajectory(c,'Monthly indexed trajectory');verifyCostStructure(c,'Monthly indexed trajectory');}
  verifyMilestoneMarkers('Monthly indexed trajectory');
}));

test('Cost presentation does not double count manual supplements or FLOW options',()=>{
  for(const c of cases)mutate(c.s,'D10',.5,()=>verifyCostStructure(c,'Manual supplement'));
  mutate('Prix Flow','D14',2,()=>verifyCostStructure(cases[0],'Active supplier options'));
});

test('The reconciled FLOW abaque contains all maintenance, operations and evolution calculations at the editable owner',()=>{
  for(const [index,activity]of unifiedRun.activities.entries()){
    const row=12+index;
    near(val('Run Flow','C'+row),activity.quantity,`FLOW quantity row ${row}`);
    near(val('Run Flow','D'+row),activity.jh_per_unit,`FLOW unit effort row ${row}`);
    near(val('Run Flow','E'+row),activity.quantity*activity.jh_per_unit,`FLOW derived effort row ${row}`);
    near(val('Run Flow','G'+row),activity.quantity*activity.jh_per_unit*val(cases[0].u,'D20'),`FLOW derived cost row ${row}`);
    const categoryLabel={mco:'Maintenance / pilotage',core_technical:'Versions techniques Core',exploitation:'Exploitation'}[activity.category];
    assert(val('Run Flow','H'+row)===categoryLabel,`FLOW activity owner category row ${row}`);
    assert(typeof val('Run Flow','I'+row)==='string'&&val('Run Flow','I'+row).length>15,`FLOW activity scope and overlap boundary row ${row}`);
  }
  for(const envelope of unifiedRun.legacy_envelopes){
    const charges=envelope.activity_ids.reduce((sum,id)=>{const index=unifiedRun.activities.findIndex(activity=>activity.id===id);assert(index>=0,`Unknown legacy activity ${id}`);return sum+val('Run Flow','E'+(12+index));},0);
    near(charges,envelope.source_quantity*envelope.source_jh_per_unit,`Legacy ${envelope.id} is reallocated, never added twice`);
  }
  near(unifiedRun.legacy_envelopes.reduce((sum,envelope)=>sum+envelope.source_quantity*envelope.source_jh_per_unit,0),600,'Historical maintenance total');
  near(val('Run Flow','E28')-600,56,'Only restoration and PRA are additional nominal human-service activities');
  for(const [row,quantity,effort]of [[33,40,2],[34,10,12],[35,4,30]]){
    near(val('Run Flow','C'+row),quantity,`FLOW evolution quantity row ${row}`);
    near(val('Run Flow','D'+row),effort,`FLOW evolution effort row ${row}`);
    near(val('Run Flow','E'+row),quantity*effort,`FLOW evolution derived effort row ${row}`);
  }
  near(val('Run Flow','E37'),320,'FLOW evolution volume');
});

test('Microsoft MCO derives from own activities and monitoring is explicitly a SAP proxy',()=>{
  for(const [row,quantity,effort]of [[76,240,.5],[77,30,3],[78,4,15],[79,12,2],[80,12,2]]){
    near(val(cases[2].u,'C'+row),quantity,`Microsoft MCO quantity row ${row}`);
    near(val(cases[2].u,'D'+row),effort,`Microsoft MCO effort row ${row}`);
    near(val(cases[2].u,'E'+row),quantity*effort,`Microsoft MCO derived effort row ${row}`);
  }
  near(val(cases[2].u,'D104'),val('Références','C82'),'Microsoft monitoring proxy references SAP monitoring');
  mutate(cases[2].u,'D105',1.4,()=>{
    near(val(cases[2].u,'D33'),630000,'Microsoft monitoring service coefficient');
    verifyOracle(cases[2],'Microsoft monitoring proxy variation');
  });
});

test('Common change demand retains solution-specific efforts and prices',()=>{
  for(const [row,flowEffort,sapEffort,msEffort]of [[95,2,3.5,3],[96,12,14,16],[97,30,35,40]]){
    near(val(cases[1].u,'C'+row),val(cases[0].u,'C'+row),`SAP shared change demand row ${row}`);
    near(val(cases[2].u,'C'+row),val(cases[0].u,'C'+row),`Shared change demand row ${row}`);
    near(val(cases[0].u,'D'+row),flowEffort,`FLOW change effort row ${row}`);
    near(val(cases[1].u,'D'+row),sapEffort,`SAP change effort row ${row}`);
    near(val(cases[2].u,'D'+row),msEffort,`Microsoft change effort row ${row}`);
  }
  const sapBefore=val(cases[1].s,'H9'),flowBefore=val(cases[0].s,'H9'),msBefore=val(cases[2].s,'H9');
  mutate(cases[0].u,'C95',50,()=>{
    near(val(cases[0].u,'D34'),340,'FLOW change demand propagates into JH');
    near(val(cases[1].u,'D34'),455,'SAP shared demand propagates with own JH per change');
    near(val(cases[2].u,'D34'),470,'Microsoft shared demand propagates with own JH per change');
    near(val(cases[0].s,'H9'),flowBefore+10*2*750*10/1e6,'FLOW change demand TCO');
    near(val(cases[2].s,'H9'),msBefore+10*3*850*(377/30)/1e6,'Microsoft change demand TCO');
    near(val(cases[1].s,'H9'),sapBefore+10*3.5*850*12.7/1e6,'SAP shared basket changes the assumed budget above the preserved source floor');
    for(const c of cases)verifyOracle(c,'Change-demand variation');
  });
});

test('Missing common change demand blocks all three options together',()=>mutate(cases[0].u,'C95',null,()=>{
  for(const c of cases){unavailable(c,'Missing common change demand: '+c.name);assert(!finite(val(c.u,'D34')),`Missing shared quantity silently became zero ${c.name} effort`);}
}));

for(const c of cases)test(`${c.name}: common service-volume coefficient scales both MCO and evolutions once`,()=>mutate(c.u,'D39',1.25,()=>verifyOracle(c,'Service volume coefficient')));

test('SAP MCO adds only new maintenance and TMA uses the maximum rather than adding two overlapping envelopes',()=>{
  mutateMany([[cases[1].u,'D134',0],[cases[1].u,'D135',0]],()=>{
    near(val(cases[1].u,'D30'),0,'SAP MCO extensions removed explicitly');
    near(val(cases[1].u,'D26'),250000,'SAP source MCO floor retained once without rate conversion');
    verifyOracle(cases[1],'No supplementary MCO');
  });
  mutateMany([[cases[1].u,'D95',0],[cases[1].u,'D96',0],[cases[1].u,'D97',0]],()=>{
    near(val(cases[1].u,'D27'),350000,'SAP source TMA retained when basket is below it');
    verifyOracle(cases[1],'TMA source floor');
  });
  mutate(cases[1].u,'D97',200,()=>{
    near(val(cases[1].u,'D27'),1080*850,'SAP larger basket replaces rather than adds to TMA forfait');
    verifyOracle(cases[1],'Larger TMA basket');
  });
});

for(const c of cases)test(`${c.name}: client Build, Run and indexation are separately projected`,()=>{
  const supplier=val('Calculs 15 ans','L'+(c.start+15));
  mutateMany([[c.s,'D81',.5],[c.s,'D82',.1],[c.s,'D83',.06]],()=>{
    near(val('Calculs 15 ans','L'+(c.start+15)),supplier,'Client parameters changed supplier cost');
    verifyOracle(c,'Client budget / Run / 6% index');
  });
});

for(const c of cases.slice(1))for(const start of [0,5,18])for(const freeze of [0,1,5])test(`${c.name}: monthly licence anniversary at M${start}, freeze ${freeze}`,()=>mutateMany([[c.u,'D38',start],[c.u,'D46',freeze],[c.u,'D44',.10]],()=>verifyOracle(c,`M${start}, freeze ${freeze}, 10% licences`)));

for(const c of cases)test(`+1 M€ project complement propagates: ${c.name}`,()=>{
  const oldBudget=val(c.s,'D12'),oldTco=val(c.s,'H9'),old=val(c.s,'D10');
  mutate(c.s,'D10',old+1,()=>{
    near(val(c.s,'D12'),oldBudget+1,'Project complement');
    near(comp(c,22),oldBudget+1,'Comparison project complement');
    near(val(c.s,'H9'),oldTco+1,'TCO project complement');
    near(comp(c,29),oldTco+1,'Comparison TCO complement');
  });
});

test('FLOW option and nominal selector feed all summaries',()=>{
  const oldTco=val('Prix Flow','H9'),oldBudget=val('Prix Flow','D12'),nominal=val('Prix Flow','D7');
  const constructionResources=val('Prix Flow','D13');
  near(oldBudget,nominal+constructionResources,'Initial active budget is nominal labour plus construction resource bills');
  mutate('Prix Flow','D14',2,()=>{
    const options=val('Prix Flow','D8'),supplier=val('Calculs 15 ans','L23'),client=val('Calculs 15 ans','O23');
    near(val('Prix Flow','D12'),options+constructionResources,'Majorations selected, construction resource bills funded separately');
    near(val('Prix Flow','H9'),oldTco+options-nominal,'Majorations TCO');
    near(comp(cases[0],22),options+constructionResources,'Majorations comparison');
    near(client,2.4075,'Client provision activated separately');
    mutate('Prix Flow','C67',.20,()=>{
      near(val('Prix Flow','D12'),options+constructionResources+nominal*.10,'Execution option budget');
      near(comp(cases[0],29),supplier+nominal*.10,'Execution option TCO');
    });
    mutate('Prix Flow','C69',.20,()=>{
      near(val('Calculs 15 ans','L23'),supplier,'Client contribution does not change supplier costs');
      near(val('Calculs 15 ans','O23'),client+nominal*.10,'Client contribution kept separately');
      near(val('Calculs 15 ans','P23'),supplier+client+nominal*.10,'Client contribution included once in known total');
    });
  });
  near(val('Prix Flow','D12'),nominal+constructionResources,'Nominal and construction resources restored');
  near(val('Calculs 15 ans','O23'),0,'Nominal excludes client option');
  mutate('Prix Flow','C69',.20,()=>{
    near(val('Calculs 15 ans','L23'),oldTco,'Inactive client option does not change supplier costs');
    near(val('Calculs 15 ans','O23'),0,'Inactive client option remains excluded');
  });
});

test('Supplier, client and known total remain separate in every projected year',()=>{
  for(const c of cases){
    let clientCum=0;
    for(let year=0;year<=15;year++){
      const row=c.start+year,clientAnnual=val('Calculs 15 ans','N'+row);
      assert(finite(clientAnnual)&&clientAnnual>=0,`${c.name} year ${year}: invalid client annual cost`);
      clientCum+=clientAnnual;
      near(val('Calculs 15 ans','O'+row),clientCum,`${c.name} year ${year}: client cumulative`);
      near(val('Calculs 15 ans','P'+row),val('Calculs 15 ans','L'+row)+clientCum,`${c.name} year ${year}: known total`);
    }
    if(c.name!=='FLOW')near(clientCum,0,`${c.name}: unvalued client default is separate zero convention`);
  }
});

test('Supplier, client and years of use remain explicit in the supporting budget sheets',()=>{
  for(const c of cases){
    const end=c.start+15;
    const runYears=Array.from({length:15},(_,i)=>val('Calculs 15 ans','M'+(c.start+i+1))).reduce((a,b)=>a+b,0);
    near(val(c.s,'H83'),runYears,`${c.name}: equivalent years of use displayed`);
    near(comp(c,31),runYears,`${c.name}: comparable equivalent years of use remain visible on the executive page`);
    near(comp(c,29),val('Calculs 15 ans','L'+end),`${c.name}: comparison supplier 15 years`);
    if(val(c.s,'D87')==='Non chiffré')assert(val(c.s,'H81')==='n.c.',`${c.name}: unvalued client should be explicitly marked n.c.`);
    else near(val(c.s,'H81'),val('Calculs 15 ans','O'+end),`${c.name}: separate client contribution`);
    near(val(c.s,'H82'),val('Calculs 15 ans','P'+end),`${c.name}: total known`);
    assert(val(c.s,'H84')===val(c.s,'D87'),`${c.name}: client contribution status missing`);
  }
  near(val(cases[0].s,'H83'),10,'FLOW equivalent Run years');
  near(val(cases[1].s,'H83'),12.7,'SAP equivalent Run years');
  near(val(cases[2].s,'H83'),12.5666666666667,'Microsoft equivalent Run years');
  mutate('Prix Flow','D54',66,()=>{
    near(val('Prix Flow','H83'),9.5,'FLOW delivery delay reduces service years');
    near(comp(cases[0],31),9.5,'FLOW delayed years of use on the executive page');
    near(val('Calculs 15 ans','M14'),.5,'FLOW delayed half-year Run');
  });
});

test('Licences during Build and contractual price freeze',()=>{
  const sapRetention=1-val(cases[1].u,'D48'),msRetention=1-val(cases[2].u,'D48');
  near(val('Calculs 15 ans','D30'),.790633*sapRetention,'SAP year 1 licence after explicit Finance withdrawal');
  near(val('Calculs 15 ans','D51'),.97900151*msRetention,'Microsoft year 1 licence after explicit Finance withdrawal');
  near(val('Calculs 15 ans','H51'),.09,'Microsoft year 1 Unified/PQA');
  const ms=val('Prix unitaire Microsoft','C52')*msRetention;
  for(let r=52;r<=56;r++)near(val('Prix unitaire Microsoft','E'+r),ms,`Microsoft frozen year ${r-51}`);
  near(val('Prix unitaire Microsoft','E57'),ms*1.04,'Microsoft first indexation year 6');
  for(let year=1;year<=5;year++)near(val('Prix unitaire SAP','E'+(51+year)),[790633,765823,973480,1270879,1270879][year-1]*sapRetention*Math.pow(1.04,year-1),`SAP year ${year} base, withdrawal and indexation`);
  mutate('Prix unitaire Microsoft','D44',.08,()=>near(val('Prix unitaire Microsoft','E57'),ms*1.08,'Microsoft changed indexation'));
  mutate('Prix unitaire Microsoft','D38',18,()=>{
    near(val('Calculs 15 ans','D51'),0,'Subscription postponed, year 1');
    near(val('Calculs 15 ans','D52'),ms*.5/1e6,'Subscription postponed, half year 2');
    near(val('Calculs 15 ans','D53'),ms/1e6,'Subscription postponed, full year 3');
  });
});

test('Finance licence withdrawal preserves raw source baskets and cannot produce negative billed licences',()=>{
  const rawSources=[790633,765823,973480,1270879,1270879];
  rawSources.forEach((amount,i)=>near(val(cases[1].u,'C'+(52+i)),amount,`SAP raw licence basket year ${i+1}`));
  near(val(cases[1].u,'D48'),400000/1270879,'SAP Finance licence split hypothesis');
  near(val(cases[2].u,'C52'),979001.51,'Microsoft raw licence basket retained');
  near(val(cases[2].u,'D48'),.1,'Microsoft Finance licence split hypothesis');
  for(const c of cases.slice(1))mutate(c.u,'D48',1,()=>{
    for(let y=1;y<=15;y++)near(val('Calculs 15 ans','D'+(c.start+y)),0,`${c.name} zero billed licences at full withdrawal`);
    verifyOracle(c,'Full licence withdrawal');
  });
});

test('SAP major migration provision is optional, annualised, indexed and prorated without duplicating construction',()=>{
  near(val(cases[1].u,'D36'),0,'SAP major migration is excluded from the nominal comparison');
  const oldBudget=val(cases[1].s,'D12'),oldTco=val(cases[1].s,'H9');
  mutateMany([['Run Flow','H70',1],['Run Flow','D70',1000]],()=>{
    near(val(cases[1].s,'D12'),oldBudget,'SAP upgrade annual provision changed Build');
    near(val(cases[1].s,'H9'),oldTco+250000*12.7/1e6,'SAP enabled major migration provision in TCO');
    near(val('Calculs 15 ans','AB44'),250000/1e6,'SAP annual migration subtotal is a subset of other costs, not an extra invoice');
    verifyOracle(cases[1],'Larger periodic S4 upgrade provision');
    verifyCostStructure(cases[1],'Larger periodic S4 upgrade provision');
  });
});

test('Microsoft Unified renewals start in year 2, follow billed licence spend and do not wait for applicative Run',()=>{
  near(val('Calculs 15 ans','H51'),.09,'Microsoft first-year PQA/Unified budget counted once');
  near(val('Calculs 15 ans','H52'),.05,'Microsoft year-2 minimum Unified budget');
  mutate(cases[2].s,'D54',30,()=>{
    near(val('Calculs 15 ans','M52'),0,'Microsoft Run delayed beyond year 2');
    near(val('Calculs 15 ans','H52'),.05,'Unified is due while contract is active, before Run');
    verifyOracle(cases[2],'Delayed applicative Run with subscription support');
  });
  mutateMany([[cases[2].u,'D145',1],[cases[2].u,'D147',.2],[cases[2].u,'D148',1]],()=>{
    for(let y=2;y<=15;y++)near(val('Calculs 15 ans','H'+(cases[2].start+y)),.2*val('Calculs 15 ans','D'+(cases[2].start+y)),`Microsoft Unified Product Spend branch year ${y}`);
    verifyOracle(cases[2],'Unified Product Spend branch');
  });
  mutate(cases[2].u,'D146',1.2,()=>{
    near(val(cases[2].u,'D149'),60000,'Unified minimum USD converted with explicit budget FX');
    verifyOracle(cases[2],'Unified budget FX variation');
  });
});

for(const [s,a,c]of [['Charges Flow','D32',cases[0]],['Prix unitaire Flow','D8',cases[0]],['Prix unitaire SAP','D14',cases[1]],['Prix unitaire Microsoft','D14',cases[2]],['Prix unitaire Microsoft','D15',cases[2]]])test(`Required entry absent: ${s}!${a}`,()=>mutate(s,a,null,()=>unavailable(c,`${s}!${a}`)));

test('Missing and invalid attribution keys are signalled',()=>{
  mutate('Charges Flow','F8',null,()=>{
    assert(val('Charges Flow','I8')==='Manquant','Missing attribution key label');
    assert(val('Prix Flow','H14')!=='Paramètres renseignés','Missing attribution key not flagged in summary');
  });
  mutate('Charges Flow','F8',.31,()=>{
    assert(val('Charges Flow','I8')==='À corriger','Invalid attribution key label');
    assert(val('Prix Flow','H14')!=='Paramètres renseignés','Invalid attribution key not flagged in summary');
  });
});

for(const c of cases){
  const parts=Array.from({length:c.count},(_,i)=>54+i);
  test(`${c.name}: missing Run weight blocks total`,()=>mutate(c.s,'F54',null,()=>unavailable(c,'Missing Run weight')));
  test(`${c.name}: invalid Run total blocks total`,()=>mutate(c.s,'F54',.5,()=>unavailable(c,'Run weights do not sum to one')));
  if(c.count>1){
    const negative=c.count===3?[-.2,.4,.8]:[-.2,.6,.2,.2,.2];
    test(`${c.name}: negative pasted Run weight with sum one is rejected`,()=>mutateMany(parts.map((row,i)=>[c.s,'F'+row,negative[i]]),()=>unavailable(c,'Negative Run weight')));
    const upper=c.count===3?[1.2,-.2,0]:[1.2,-.2,0,0,0];
    test(`${c.name}: pasted Run weight above 100% with sum one is rejected`,()=>mutateMany(parts.map((row,i)=>[c.s,'F'+row,upper[i]]),()=>unavailable(c,'Run weight above 100%')));
  }
}

for(const c of cases.slice(1))for(const [address,value,label]of [['D38',5.5,'fractional subscription month'],['D46',.5,'fractional price-freeze duration'],['D46',-1,'negative price-freeze duration']])test(`${c.name}: ${label} is rejected after paste`,()=>mutate(c.u,address,value,()=>unavailable(c,label)));
for(const c of cases)for(const [address,value,label]of [['D43',-1,'service indexation at -100%'],['D45',-1,'infrastructure indexation at -100%'],['D34',-1,'negative evolution volume'],['D39',-1,'negative volume coefficient']]){
  if(c.name==='FLOW'&&address==='D34')continue; // Calculated compatibility link; validate the Run Flow owner instead.
  test(`${c.name}: ${label} is rejected after paste`,()=>mutate(c.u,address,value,()=>unavailable(c,label)));
}
for(const c of [cases[2]])for(const [address,value,label]of [['C76',-1,'negative MCO activity quantity'],['D76',-1,'negative MCO activity effort'],['C76',null,'missing MCO activity quantity'],['D95',-1,'negative effort per change'],['D95',null,'missing effort per change']])test(`${c.name}: ${label} blocks Run rather than silently reducing it`,()=>mutate(c.u,address,value,()=>unavailable(c,label)));
for(const [address,value,label]of [['C12',-1,'negative activity quantity'],['D13',-1,'negative activity effort'],['C14',null,'missing activity quantity'],['D33',-1,'negative effort per change'],['D33',null,'missing effort per change']])test(`FLOW: reconciled ${label} blocks Run rather than silently reducing it`,()=>mutate('Run Flow',address,value,()=>unavailable(cases[0],label)));
for(const [c,address,label]of [[cases[1],'D76','SAP MCO service coefficient'],[cases[1],'D77','SAP evolution service coefficient'],[cases[2],'D105','Microsoft monitoring proxy coefficient']])for(const value of [-1,null])test(`${label}: invalid coefficient ${value} blocks Run`,()=>mutate(c.u,address,value,()=>unavailable(c,label)));
for(const c of cases.slice(1))for(const [address,value,label]of [['C115',null,'missing France role share'],['C115',-.1,'negative France role share'],['D115',null,'missing France role price'],['D134',-1,'negative OMS maintenance ratio'],['D135',1.1,'new-interface maintenance ratio above 100%'],['D48',1.1,'licence withdrawal above 100%'],['D48',-.1,'negative licence withdrawal']])test(`${c.name}: ${label} is rejected after paste`,()=>mutate(c.u,address,value,()=>unavailable(c,label)));
for(const c of cases.slice(1))for(const [address,value,label]of [['C'+(c.bridge+5),-1,'negative missing-activity quantity'],['E'+(c.bridge+17),1.1,'Finance workload withdrawal above 100%'],['E'+(c.bridge+20),1.1,'client IT share above 100%'],['E'+(c.bridge+21),1.1,'supplier IT transfer share above 100%']])test(`${c.name}: ${label} in the bridge blocks provider budget`,()=>mutate('Passage Buy France',address,value,()=>unavailable(c,label)));
for(const c of cases.slice(1)){
  const model=functionalModel(c),activeRow=model.start+model.data.items.findIndex(x=>x.activation===1);
  for(const [col,value,label]of [['C',null,'missing functional quantity'],['C',-1,'negative functional quantity'],['C',.5,'fractional functional quantity'],['E',null,'missing functional unit effort'],['E',-1,'negative functional unit effort'],['J',null,'missing function activation'],['J',.5,'fractional function activation'],['J',2,'function activation outside 0/1']])test(`${c.name}: ${label} blocks the functional complement and total cost`,()=>mutate('Passage Buy France',col+activeRow,value,()=>unavailable(c,label)));
}
for(const [c,address,value,label]of [[cases[2],'D145',1.1,'Unified D365 share above 100%'],[cases[2],'D146',-1,'negative Unified FX'],[cases[2],'D147',null,'missing Unified rate'],[cases[2],'D148',-1,'negative Unified minimum'],[cases[2],'D130',-1,'negative Microsoft per-pole JH']])test(`${label} is rejected`,()=>mutate(c.u,address,value,()=>unavailable(c,label)));
for(const [row,c]of [[68,cases[0]],[69,cases[0]],[70,cases[1]]]){
  for(const invalid of [-1,.5,2,null])test(`${c.name}: option ${row} activation ${invalid} is rejected`,()=>mutate('Run Flow','H'+row,invalid,()=>unavailable(c,'Invalid service option activation')));
  test(`${c.name}: enabled option ${row} requires valid pricing quantities`,()=>mutateMany([['Run Flow','H'+row,1],['Run Flow','C'+row,row===68?null:0]],()=>unavailable(c,'Missing or invalid service option quantity')));
}
for(const c of cases)for(const [address,value,label]of [['D81',-.5,'negative client project budget'],['D82',-.1,'negative client annual Run'],['D83',-1,'client indexation at -100%']])test(`${c.name}: ${label} blocks client totals without changing supplier totals`,()=>{
  const supplier=val('Calculs 15 ans','L'+(c.start+15));
  mutate(c.s,address,value,()=>{
    near(val('Calculs 15 ans','L'+(c.start+15)),supplier,'Invalid client entry changed supplier costs');
    assert(!finite(val('Calculs 15 ans','P'+(c.start+15))),`${label}: known total remains a plausible number`);
  });
});

for(const [address,value,c,label]of [
  ['D11',null,cases[0],'missing technical quantity-growth assumption'],
  ['D12',null,cases[0],'missing FLOW resource capacity'],
  ['D12',-1,cases[0],'negative FLOW resource capacity'],
  ['C18',null,cases[0],'missing FLOW resource quantity'],
  ['D18',-1,cases[0],'negative FLOW resource unit price'],
  ['C35',null,cases[0],'missing FLOW construction environment quantity'],
  ['D65',null,cases[1],'missing CPI tenant price'],
  ['D67',0,cases[1],'zero CPI message block size'],
  ['D75',-1,cases[1],'negative imputable BTP credit'],
  ['C86',null,cases[2],'missing Microsoft external environment quantity'],
  ['D87',-1,cases[2],'negative Microsoft external resource price'],
  ['D14',2,cases[2],'Microsoft external coverage coefficient above 100%']
])test(`${c.name}: ${label} is not silently treated as a free service`,()=>mutate('Plateforme et exploitation',address,value,()=>unavailable(c,label)));

for(const c of cases)test(`${c.name}: licence quantity growth at -100% is rejected`,()=>mutate(c.u,'D49',-1,()=>unavailable(c,'Licence quantity growth at -100%')));

test('All edited entries restored',()=>{
  assert(JSON.stringify(snapshot())===JSON.stringify(baseline),'In-memory baseline was not fully restored');
  assert(inputsSnapshot()===baselineInputs,'At least one in-memory input was not restored');
});
if(failures.length){console.log('AUDIT_FAILURES',JSON.stringify({passed:passed.length,failures}));throw new Error(`${failures.length} independent audit checks failed`);}
console.log('AUDIT_PASS',JSON.stringify({tests:passed.length,baseline,readOnly:true}));
