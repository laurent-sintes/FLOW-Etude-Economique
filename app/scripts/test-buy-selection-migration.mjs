import assert from 'node:assert/strict';
import {test} from 'node:test';
import {prepareSavedScenario,createSavedScenario} from '../src/savedScenarios.ts';
import {initialSession,encodeSession,restoreSession} from '../src/reloadSession.ts';
const old={model_version:'old-model',simulation_contract:'old',ui:{default_horizon:10,horizons:[3,5,7,10],labels:{default_scenario_name:'test'}},baseline:{parameters:{common:{},options:{microsoft:{integration:100000},sap:{integration:200000}}},options:[{stack:'microsoft'},{stack:'sap'}]}};
const current={...old,model_version:'new-model',simulation_contract:'new',ui:{...old.ui,compatible_simulation_contracts:['old'],buy_selection_migration:{from_contracts:['old'],legacy_versions:[],options:['microsoft','sap'],preparation_eur:20000}},baseline:{...old.baseline,parameters:{common:{},options:{microsoft:{integration:80000},sap:{integration:180000}}}}};
test('named imports transfer preparation once and keep the original recoverable',()=>{
 const item=createSavedScenario(old,'kept',old.baseline.parameters),original=JSON.stringify(item);
 const migrated=prepareSavedScenario(current,item);
 assert.deepEqual(migrated.parameters,current.baseline.parameters);
 assert.equal(migrated.simulation_contract,'new');assert.equal(migrated.name,'kept');
 assert.deepEqual(prepareSavedScenario(current,migrated),migrated);
 assert.equal(JSON.stringify(item),original);
});
test('sessions migrate only overridden amounts, not new reference defaults',async()=>{
 const session=initialSession(old);session.draft.options.microsoft.integration=150000;session.horizon=5;session.chosen='sap';
 const raw=encodeSession(old,session);
 const restored=await restoreSession(current,raw,async parameters=>({parameters}));
 assert.equal(restored.restored,true);assert.equal(restored.session.draft.options.microsoft.integration,130000);
 assert.equal(restored.session.draft.options.sap.integration,180000);assert.equal(restored.session.horizon,5);assert.equal(restored.session.chosen,'sap');
 const again=await restoreSession(current,encodeSession(current,restored.session),async parameters=>({parameters}));
 assert.deepEqual(again.session,restored.session);
});
test('amounts too small to transfer are recoverable rather than clipped to zero',async()=>{
 const session=initialSession(old);session.draft.options.microsoft.integration=10000;
 const raw=encodeSession(old,session);
 const restored=await restoreSession(current,raw,async()=>assert.fail('invalid migration must not calculate'));
 assert.equal(restored.recovery,raw);assert.equal(restored.restored,false);
 assert.throws(()=>prepareSavedScenario(current,createSavedScenario(old,'small',session.draft)),{code:'invalid_number'});
});
