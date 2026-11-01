/** Reading qualifiers only; all amounts and coverage come from Python. */
export function coreQualification(rows:readonly {stack:string;estimation_status:string}[],stack:string){
 return rows.find(row=>row.stack===stack)?.estimation_status||'not_applicable';
}
export function isPartialMake(rows:readonly {stack:string;estimation_status:string}[],stack:string){
 return ['pending_reestimation','partially_estimated'].includes(coreQualification(rows,stack));
}
export function hasUnestimatedConstruction(rows:readonly {stack:string;estimation_status:string}[],stack:string,amount:number){
 return amount===0&&coreQualification(rows,stack)==='pending_reestimation';
}

/** Select inclusion wording from the period stage already supplied by Python. */
export function completionRelation(stage:string){
 return stage==='stage_service'?'included':stage==='stage_build'||stage==='stage_integration'?'beyond':null;
}
type PublishedReading={stack:string;comparison:{reference:string;horizons:readonly {years:number;difference_eur_ht:number}[]};service_completion:{total_eur_ht:number;month:number}};
/** Wording only: order existing published results, without calculating or changing amounts. */
export function comparisonTakeaways(visible:readonly string[],readings:readonly PublishedReading[],years:number){
 const scoped=visible.map(stack=>readings.find(row=>row.stack===stack));
 const java=scoped.find(row=>row?.stack==='java-spring'),microsoft=scoped.find(row=>row?.stack==='microsoft');
 const differences=scoped.map(row=>row?.comparison.reference==='java-spring'?row.comparison.horizons.find(h=>h.years===years)?.difference_eur_ht:undefined);
 const known=scoped.length>1&&scoped.every(Boolean)&&differences.every(value=>typeof value==='number'&&Number.isFinite(value));
 const javaOthers=visible.flatMap((stack,i)=>stack==='java-spring'?[]:[differences[i]!]);
 const javaResult=java&&known?javaOthers.every(value=>value>0)?'lowest':javaOthers.every(value=>value>=0)?'shared_lowest':'other':null;
 const sapIndex=visible.indexOf('sap'),sapValue=differences[sapIndex];
 const sapOthers=differences.filter((_,i)=>i!==sapIndex) as number[];
 const sapResult=sapIndex>=0&&known?sapOthers.every(value=>sapValue!>value)?'highest':sapOthers.every(value=>sapValue!>=value)?'shared_highest':'other':null;
 const pair=java&&microsoft?[java.service_completion.total_eur_ht,microsoft.service_completion.total_eur_ht,java.service_completion.month,microsoft.service_completion.month]:[];
 const microsoftResult=pair.length===4&&pair.every(Number.isFinite)?{spending:pair[1]<pair[0]?'lower':pair[1]>pair[0]?'higher':'same',timing:pair[3]<pair[2]?'earlier':pair[3]>pair[2]?'later':'same'} as const:null;
 return {java:javaResult,sap:sapResult,microsoft:microsoftResult};
}
