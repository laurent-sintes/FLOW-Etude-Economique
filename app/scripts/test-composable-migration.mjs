import assert from 'node:assert/strict';
import {test} from 'node:test';
import {readFileSync} from 'node:fs';
import {encodeSession,initialSession,restoreSession} from '../src/reloadSession.ts';
import {createSavedScenario,restoreSavedScenario,prepareSavedScenario} from '../src/savedScenarios.ts';

const fixture=JSON.parse(readFileSync(new URL('../../audits/2026-10-27-modele-composable-migration-fixture.json',import.meta.url),'utf8'));
const old=fixture.old,current=process.env.FLOW_TEST_BOOTSTRAP?JSON.parse(readFileSync(process.env.FLOW_TEST_BOOTSTRAP,'utf8')):fixture.current;

test('actual previous session keeps overrides, horizon, chosen option and name under the composable contract',async()=>{
 const session=initialSession(old);
 session.draft.options['java-spring'].build_mois=60;
 session.draft.common.bonus_continuite_pct=17;
 session.horizon=7;session.chosen='rust';session.name='Hypothèses avant migration';
 const raw=encodeSession(old,session);
 let request;
 const restored=await restoreSession(current,raw,async parameters=>{request=structuredClone(parameters);return {...current.baseline,parameters};});
 assert.equal(restored.restored,true);assert.equal(restored.recovery,null);
 assert.equal(request.options['java-spring'].build_mois,60);
 assert.equal(request.common.bonus_continuite_pct,17);
 assert.equal(restored.session.horizon,7);assert.equal(restored.session.chosen,'rust');assert.equal(restored.session.name,session.name);
 assert.equal(raw,encodeSession(old,session));
});

test('actual previous named export retains assumptions with the explicit Buy preparation transfer',async()=>{
 const parameters=structuredClone(old.baseline.parameters);
 parameters.options.dotnet.services_core+=12345;
 const item=createSavedScenario(old,'Conservé',parameters),original=JSON.stringify(item);
 const expected=structuredClone(parameters);
 if(current.ui.buy_selection_migration&&old.simulation_contract!==current.simulation_contract){
  for(const slug of current.ui.buy_selection_migration.options)expected.options[slug].integration-=current.ui.buy_selection_migration.preparation_eur;
 }
 const loaded=await restoreSavedScenario(current,item,async(p,version)=>{
  assert.deepEqual(p,expected);assert.equal(version,current.model_version);
  return {...current.baseline,parameters:p};
 });
 assert.deepEqual(loaded.projection.parameters,expected);assert.equal(JSON.stringify(item),original);
 assert.throws(()=>prepareSavedScenario({...current,ui:{...current.ui,compatible_simulation_contracts:[]}},item),{code:'version'});
});
