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
