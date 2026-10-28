import assert from 'node:assert/strict';
import {test} from 'node:test';
import {createSavedScenario,prepareSavedScenario,readScenarioCollection,restoreSavedScenario,scenarioRecovery,serializeScenarioCollection} from '../src/savedScenarios.ts';

const fixture=()=>({model_version:'new-reference',simulation_contract:'same-semantics',ui:{saved_scenarios:{compatible_legacy_versions:['known-legacy']}},baseline:{parameters:{common:{inflation:2},options:{java:{build:100,duration:48},sap:{integration:50,duration:24}}}}});
const savedParameters=()=>({common:{inflation:3},options:{java:{build:130,duration:42},sap:{integration:72,duration:22}}});
const legacy=version=>({name:'Mon scénario',model_version:version,parameters:savedParameters()});
const simulate=async(parameters,version)=>({parameters,model_version:version});

test('new saves and exports carry semantic contract and clone all absolute assumptions',()=>{
 const d=fixture(),p=savedParameters(),s=createSavedScenario(d,' Mon scénario ',p);
 assert.equal(s.format,2);assert.equal(s.simulation_contract,d.simulation_contract);assert.equal(s.model_version,d.model_version);
 assert.equal(s.name,'Mon scénario');assert.deepEqual(s.parameters,p);p.options.java.build=0;assert.equal(s.parameters.options.java.build,130);
 assert.deepEqual(prepareSavedScenario(d,JSON.parse(JSON.stringify(s))),s);
});

test('same contract survives reference changes and sends the current model version',async()=>{
 const before=fixture(),s=createSavedScenario(before,'Scénario',savedParameters()),original=structuredClone(s),after=fixture();
 after.model_version='later-reference';after.baseline.parameters.options.java.build=999;
 const r=await restoreSavedScenario(after,s,simulate);
 assert.equal(r.projection.model_version,'later-reference');assert.equal(r.projection.parameters.options.java.build,130);
 assert.deepEqual(r.projection.parameters,savedParameters());assert.deepEqual(s,original);
});

test('legacy current and explicitly compatible revisions are accepted without dropping saved values',async()=>{
 const d=fixture();
 for(const version of [d.model_version,'known-legacy']){
  const s=legacy(version),r=await restoreSavedScenario(d,s,simulate);
  assert.deepEqual(r.projection.parameters,s.parameters);assert.equal(r.projection.model_version,d.model_version);
  assert.equal(s.model_version,version);assert.equal(s.format,undefined);
 }
});

test('unknown legacy revision, changed contract and unsupported format are rejected before calculating',async()=>{
 const d=fixture(),s=createSavedScenario(d,'Scénario',savedParameters());
 for(const input of [legacy('unknown'),{...s,simulation_contract:'changed'},{...s,format:3},{...s,format:undefined},{...legacy(d.model_version),simulation_contract:'same-semantics'}]){
  await assert.rejects(()=>restoreSavedScenario(d,input,()=>assert.fail('must not calculate')),e=>e.code==='version');
 }
});

test('malformed values and unknown parameter shapes are rejected without changing originals',()=>{
 const d=fixture(),s=createSavedScenario(d,'Scénario',savedParameters());
 for(const p of [null,[],{...savedParameters(),extra:1},{common:{},options:savedParameters().options},{common:{inflation:3},options:{java:{build:130,duration:42}}}]){
  assert.throws(()=>prepareSavedScenario(d,{...s,parameters:p}),e=>e.code==='unknown_parameter');
 }
 for(const v of [null,'3',NaN,Infinity]){
  const p=savedParameters();p.common.inflation=v;
  assert.throws(()=>prepareSavedScenario(d,{...s,parameters:p}),e=>e.code==='invalid_number');
 }
 for(const input of [null,[],{parameters:s.parameters},{...s,name:42}])assert.throws(()=>prepareSavedScenario(d,input),e=>e.code==='import');
 assert.deepEqual(s.parameters,savedParameters());
});

test('server constraints and network errors leave the saved scenario recoverable and unmodified',async()=>{
 const d=fixture(),s=createSavedScenario(d,'Scénario',savedParameters()),original=JSON.stringify(s);
 for(const code of ['invalid_number','invalid_anchor','invalid_duration','network']){
  await assert.rejects(()=>restoreSavedScenario(d,s,async()=>{throw {code};}),e=>e.code===code);
  assert.equal(JSON.stringify(s),original);
 }
});

test('collection preserves incompatible and unrecognized entries during another save',()=>{
 const original=legacy('unknown'),unrecognized={unrecognized:true},c=readScenarioCollection(JSON.stringify([original,unrecognized]));
 assert.deepEqual(c.items,[original]);assert.deepEqual(c.unrecognized,[unrecognized]);
 const added=createSavedScenario(fixture(),'Nouveau',savedParameters()),persisted=JSON.parse(serializeScenarioCollection(c,[...c.items,added]));
 assert.deepEqual(persisted,[unrecognized,original,added]);assert.deepEqual(JSON.parse(scenarioRecovery(c)),[unrecognized,original]);
 assert.equal(scenarioRecovery(readScenarioCollection(JSON.stringify([original]))),null);
});

test('malformed storage stays downloadable and cannot be overwritten',()=>{
 for(const raw of ['{broken','null','{}']){
  const c=readScenarioCollection(raw);assert.equal(scenarioRecovery(c),raw);assert.throws(()=>serializeScenarioCollection(c,[]),e=>e.code==='storage');
 }
 assert.deepEqual(readScenarioCollection(null),{items:[],unrecognized:[],recovery:null});
});
