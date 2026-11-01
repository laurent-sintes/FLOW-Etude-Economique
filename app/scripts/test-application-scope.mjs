import test from 'node:test';
import assert from 'node:assert/strict';
import {scopeBootstrap,visibleProjection} from '../src/applicationScope.ts';
import {encodeSession,restoreSession} from '../src/reloadSession.ts';
const ids=['java-spring','dotnet','rust','microsoft','sap'];
function fixture(){return {ui:{essential:{active_options:['java-spring','microsoft','sap']},horizons:[3,5],default_horizon:5,labels:{default_scenario_name:'Example'}},glossary:{options:Object.fromEntries(ids.map(id=>[id,{libelle:id}]))},baseline:{parameters:{common:{rate:2},options:Object.fromEntries(ids.map((id,i)=>[id,{build:i+10}]))},options:ids.map((stack,i)=>({stack,cost:i+100}))},content:{core_evaluation:ids.map(stack=>({stack})),core_product_scope:{options:ids.map(stack=>({stack}))},framework:{tariffs:ids.map(key=>({key})),sources:{annual_gains:ids.map(key=>({key,path:key}))}}},model_version:'v1',simulation_contract:'c1'};}
test('active scope preserves financial values and all historical parameters',()=>{
 const source=fixture(),before=structuredClone(source),shown=scopeBootstrap(source);
 assert.deepEqual(shown.baseline.options.map(o=>o.stack),['java-spring','microsoft','sap']);
 assert.deepEqual(shown.content.framework.tariffs.map(o=>o.key),['java-spring','microsoft','sap']);
 assert.deepEqual(shown.content.core_product_scope.options.map(o=>o.stack),['java-spring','microsoft','sap']);
 assert.deepEqual(shown.glossary.options,Object.fromEntries(Object.entries(before.glossary.options).filter(([id])=>shown.ui.essential.active_options.includes(id))));
 assert.equal(shown.baseline.parameters,source.baseline.parameters);
 assert.deepEqual(source,before);
 assert.deepEqual(visibleProjection(source.ui,source.baseline).options,source.baseline.options.filter(o=>source.ui.essential.active_options.includes(o.stack)));
});
test('a historical session selecting a withdrawn option remains recoverable',async()=>{
 const previous=fixture();delete previous.ui.essential.active_options;
 const raw=encodeSession(previous,{draft:previous.baseline.parameters,chosen:'rust',horizon:5,name:'Legacy'});
 const next=scopeBootstrap(fixture());let calls=0;
 const resumed=await restoreSession(next,raw,async()=>{calls++;return next.baseline;});
 assert.equal(resumed.recovery,raw);assert.equal(resumed.restored,false);assert.equal(calls,0);
 assert.deepEqual(JSON.parse(raw).parameters,previous.baseline.parameters);
});
test('an active session preserves overrides for historical options without remapping',async()=>{
 const previous=fixture(),draft=structuredClone(previous.baseline.parameters);draft.options.rust.build=99;
 const raw=encodeSession(previous,{draft,chosen:'java-spring',horizon:5,name:'Active'});
 const next=scopeBootstrap(fixture());let received;
 const resumed=await restoreSession(next,raw,async p=>{received=p;return visibleProjection(next.ui,{...next.baseline,parameters:p});});
 assert.equal(resumed.recovery,null);assert.equal(received.options.rust.build,99);assert.equal(received.options['java-spring'].build,10);
});
