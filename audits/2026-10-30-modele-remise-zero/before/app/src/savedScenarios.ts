import type {Bootstrap,Parameters,Projection} from './context';
import {migrateBuySelection} from './buySelectionMigration.ts';

export type SavedScenario={name:string;model_version:string;parameters:Parameters;format?:unknown;simulation_contract?:unknown};
export type SavedCollection={items:SavedScenario[];unrecognized:unknown[];recovery:string|null};
type ScenarioContext=Pick<Bootstrap,'model_version'|'simulation_contract'|'baseline'|'ui'>;

function fail(code:string):never{throw Object.assign(new Error(code),{code});}
function record(value:unknown):value is Record<string,unknown>{return value!==null&&typeof value==='object'&&!Array.isArray(value);}
function envelope(value:unknown):value is SavedScenario{return record(value)&&typeof value.name==='string'&&typeof value.model_version==='string'&&value.model_version.length>0&&Object.hasOwn(value,'parameters');}
function sameKeys(actual:Record<string,unknown>,expected:Record<string,unknown>){return Object.keys(actual).length===Object.keys(expected).length&&Object.keys(expected).every(key=>Object.hasOwn(actual,key));}

export function readScenarioCollection(raw:string|null):SavedCollection{
 if(raw===null)return {items:[],unrecognized:[],recovery:null};
 try{
  const values:unknown=JSON.parse(raw);
  if(!Array.isArray(values))return {items:[],unrecognized:[],recovery:raw};
  return {items:values.filter(envelope),unrecognized:values.filter(value=>!envelope(value)),recovery:null};
 }catch{return {items:[],unrecognized:[],recovery:raw};}
}

export function serializeScenarioCollection(collection:SavedCollection,items=collection.items):string{
 // A damaged collection remains recoverable and cannot be overwritten by a save.
 if(collection.recovery!==null)fail('storage');
 return JSON.stringify([...collection.unrecognized,...items]);
}

export function scenarioRecovery(collection:SavedCollection):string|null{
 return collection.recovery??(collection.unrecognized.length?serializeScenarioCollection(collection):null);
}

export function createSavedScenario(data:ScenarioContext,name:string,parameters:Parameters):SavedScenario{
 return {format:2,simulation_contract:data.simulation_contract,model_version:data.model_version,name:name.trim().slice(0,120),parameters:structuredClone(parameters)};
}

export function prepareSavedScenario(data:ScenarioContext,value:unknown):SavedScenario{
 if(!envelope(value))fail('import');
 const hasFormat=Object.hasOwn(value,'format'),hasContract=Object.hasOwn(value,'simulation_contract');
 if(hasFormat||hasContract){
  const compatible=value.simulation_contract===data.simulation_contract||data.ui.compatible_simulation_contracts?.includes(value.simulation_contract);
  if(value.format!==2||!compatible)fail('version');
 }else{
  const legacy:unknown=data.ui.saved_scenarios?.compatible_legacy_versions;
  if(value.model_version!==data.model_version&&!(Array.isArray(legacy)&&legacy.includes(value.model_version)))fail('version');
 }
 const p:unknown=value.parameters,base=data.baseline.parameters;
 if(!record(p)||!sameKeys(p,{common:0,options:0})||!record(p.common)||!record(p.options)||!sameKeys(p.options,base.options))fail('unknown_parameter');
 const checkGroup=(actual:unknown,expected:Record<string,number>)=>{
  if(!record(actual)||!sameKeys(actual,expected))fail('unknown_parameter');
  if(Object.values(actual).some(v=>typeof v!=='number'||!Number.isFinite(v)))fail('invalid_number');
 };
 checkGroup(p.common,base.common);
 for(const [slug,expected] of Object.entries(base.options))checkGroup(p.options[slug],expected);
 const parameters=structuredClone(value.parameters);
 const migrated=migrateBuySelection(data,parameters.options,value.simulation_contract,value.model_version);
 return migrated?{...value,format:2,simulation_contract:data.simulation_contract,model_version:data.model_version,parameters}:{...value,parameters};
}

export async function restoreSavedScenario(data:ScenarioContext,value:unknown,simulate:(parameters:Parameters,modelVersion:string)=>Promise<Projection>){
 const item=prepareSavedScenario(data,value);
 // Saved values are absolute assumptions. Only the server evaluates current bounds.
 const projection=await simulate(item.parameters,data.model_version);
 return {item,projection};
}
