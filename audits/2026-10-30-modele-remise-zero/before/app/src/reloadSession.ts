import type {Bootstrap,Parameters,Projection} from './context';
import {migrateBuySelection} from './buySelectionMigration.ts';

export type ReaderSession={draft:Parameters;horizon:number;chosen:string;name:string};
type Overrides={common:Record<string,number>;options:Record<string,Record<string,number>>};
type Snapshot={format:1;contract:string;model_version:string;parameters:Parameters;overrides:Overrides;horizon:number;chosen:string;name:string};
export function initialSession(data:Bootstrap):ReaderSession{
 return {draft:structuredClone(data.baseline.parameters),horizon:data.ui.default_horizon,chosen:data.baseline.options[0].stack,name:data.ui.labels.default_scenario_name};
}
export function encodeSession(data:Bootstrap,session:ReaderSession):string{
 const overrides:Overrides={common:{},options:{}};
 const diff=(actual:Record<string,number>,base:Record<string,number>)=>Object.fromEntries(Object.entries(actual).filter(([k,v])=>v!==base[k]));
 overrides.common=diff(session.draft.common,data.baseline.parameters.common);
 for(const [slug,p] of Object.entries(session.draft.options)){
  const delta=diff(p,data.baseline.parameters.options[slug]||{});
  if(Object.keys(delta).length)overrides.options[slug]=delta;
 }
 return JSON.stringify({format:1,contract:data.simulation_contract,model_version:data.model_version,parameters:session.draft,overrides,horizon:session.horizon,chosen:session.chosen,name:session.name} satisfies Snapshot);
}
export async function restoreSession(data:Bootstrap,raw:string|null,simulate:(p:Parameters)=>Promise<Projection>){
 const session=initialSession(data);
 if(!raw)return {session,projection:data.baseline,recovery:null,restored:false};
 let saved:Snapshot;
 try{
  saved=JSON.parse(raw);
  const compatible=saved.contract===data.simulation_contract||data.ui.compatible_simulation_contracts?.includes(saved.contract);
  if(saved.format!==1||!compatible||!saved.overrides||typeof saved.name!=='string')throw Error('ERR_SESSION');
  if(data.ui.horizons.includes(saved.horizon))session.horizon=saved.horizon;
  if(data.baseline.options.some(o=>o.stack===saved.chosen))session.chosen=saved.chosen;
  session.name=saved.name.slice(0,120);
  const apply=(target:Record<string,number>,values:Record<string,number>)=>{
   if(!values||typeof values!=='object'||Array.isArray(values))throw Error('ERR_SESSION');
   for(const [key,value] of Object.entries(values)){
    if(!Object.hasOwn(target,key)||typeof value!=='number'||!Number.isFinite(value))throw Error('ERR_SESSION');
    target[key]=value;
   }
  };
  apply(session.draft.common,saved.overrides.common);
  if(!saved.overrides.options||typeof saved.overrides.options!=='object'||Array.isArray(saved.overrides.options))throw Error('ERR_SESSION');
  migrateBuySelection(data,saved.overrides.options,saved.contract,saved.model_version);
  for(const [slug,p] of Object.entries(saved.overrides.options)){
   if(!Object.hasOwn(session.draft.options,slug))throw Error('ERR_SESSION');
   apply(session.draft.options[slug],p);
  }
 }catch{return {session:initialSession(data),projection:data.baseline,recovery:raw,restored:false};}
 // The validated current reference already carries the matching projection.
 if(JSON.stringify(session.draft)===JSON.stringify(data.baseline.parameters))return {session,projection:data.baseline,recovery:null,restored:true};
 try{
  const projection=await simulate(session.draft);
  return {session,projection,recovery:null,restored:true};
 }catch(e:any){
  // Connectivity and another server change are retryable, never grounds to discard a draft.
  if(!['invalid','invalid_number','unknown_parameter','invalid_anchor','invalid_duration'].includes(e.code))throw e;
  return {session:initialSession(data),projection:data.baseline,recovery:raw,restored:false};
 }
}
