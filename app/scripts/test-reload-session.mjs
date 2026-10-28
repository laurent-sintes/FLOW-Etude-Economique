import assert from 'node:assert/strict';
import {test} from 'node:test';
import {encodeSession,initialSession,restoreSession} from '../src/reloadSession.ts';
import {parseReadingHash,matchesReadingText} from '../src/readerNavigation.ts';

test('acronym search ignores incidental substrings and supports accents, prefixes and punctuation',()=>{
 assert.equal(matchesReadingText('RISE','entreprise, comprises'),false);
 assert.equal(matchesReadingText('RISE','RISE with SAP'),true);
 assert.equal(matchesReadingText('integ','Intégration'),true);
 assert.equal(matchesReadingText('AP-HP','AP-HP, conversion SAP'),true);
 assert.equal(matchesReadingText('.NET','Backend .NET'),true);
});

test('old source bookmarks land on the corresponding reading page with their search',()=>{
 assert.equal(parseReadingHash('#sources').hash,'#synvance');
 assert.equal(parseReadingHash('#sources?tab=market&q=SAP').hash,'#market?q=SAP&detail=references');
 assert.equal(parseReadingHash('#sources?tab=glossary&q=RISE').hash,'#glossaire?q=RISE');
});
test('moved sections retain the selected stack and search at their single destination',()=>{
 assert.equal(parseReadingHash('#market?section=purchases&stack=sap').hash,'#perimetres?section=architecture&stack=sap');
 assert.equal(parseReadingHash('#perimetres?section=features&q=stock').hash,'#build?section=build&q=stock&focus=work&detail=work');
 assert.equal(parseReadingHash('#estimations?section=work&stack=rust&q=stock').hash,'#build?section=build&stack=rust&q=stock&focus=work&detail=work');
});
test('shared reading URLs preserve independent section, search and reference context',()=>{
 const link='#market?section=projects&q=SAP&kind=contrat_attribue_non_depense_finale&ref=ap-hp';
 const route=parseReadingHash(link);
 assert.equal(route.page,'market');assert.equal(route.hash,link+'&detail=references');assert.equal(route.params.get('ref'),'ap-hp');
 assert.equal(parseReadingHash('#glossaire?term=rise').params.get('term'),'rise');
});

const fixture=()=>({simulation_contract:'contract-1',model_version:'old',ui:{default_horizon:10,horizons:[3,5,7,10],labels:{default_scenario_name:'scenario'}},baseline:{parameters:{common:{bonus:10,inflation:2},options:{java:{build:100,duration:48}}},options:[{stack:'java'}]}});
const simulate=async parameters=>({parameters,total:parameters.options.java.build});
test('compatible new defaults are retained, only user edits are reapplied and recalculated',async()=>{
 const before=fixture(),s=initialSession(before);s.horizon=5;s.draft.common.bonus=20;
 const raw=encodeSession(before,s),after=fixture();after.model_version='new';after.baseline.parameters.options.java.build=200;
 const r=await restoreSession(after,raw,simulate);
 assert.equal(r.session.horizon,5);assert.equal(r.session.draft.common.bonus,20);
 assert.equal(r.session.draft.options.java.build,200);assert.equal(r.projection.total,200);assert.equal(r.recovery,null);
 assert.equal(before.baseline.parameters.common.bonus,10);
});
test('latest pending edits survive even before a calculation succeeds',async()=>{
 const d=fixture(),s=initialSession(d);s.draft.options.java.build=135;
 const r=await restoreSession(d,encodeSession(d,s),simulate);assert.equal(r.projection.total,135);
});
test('semantic contract change keeps recoverable draft and does not calculate it',async()=>{
 const d=fixture(),raw=encodeSession(d,initialSession(d));d.simulation_contract='contract-2';
 const r=await restoreSession(d,raw,()=>assert.fail());assert.equal(r.recovery,raw);assert.equal(r.restored,false);
});
test('new bounds or domain constraints reject all overrides instead of silently clipping them',async()=>{
 const d=fixture(),s=initialSession(d);s.draft.common.bonus=40;const raw=encodeSession(d,s);
 const r=await restoreSession(d,raw,async()=>{throw {code:'invalid_number'};});
 assert.equal(r.recovery,raw);assert.equal(r.session.draft.common.bonus,10);
});
test('network failure remains retryable without replacing the saved draft',async()=>{
 const d=fixture(),s=initialSession(d);s.draft.common.bonus=20;const raw=encodeSession(d,s);
 await assert.rejects(()=>restoreSession(d,raw,async()=>{throw Error('offline');}),/offline/);
});
test('reference-only restoration retains reading state without a network calculation',async()=>{
 const d=fixture(),s=initialSession(d);s.horizon=5;s.name='Reference';
 const result=await restoreSession(d,encodeSession(d,s),()=>assert.fail('reference already calculated'));
 assert.equal(result.projection,d.baseline);assert.equal(result.session.horizon,5);assert.equal(result.session.name,'Reference');assert.equal(result.recovery,null);
});
test('invalid numbers and unknown parameters cannot enter a restored calculation',async()=>{
 const d=fixture(),s=initialSession(d);s.draft.common.bonus=NaN;
 for(const raw of [encodeSession(d,s),'{broken',JSON.stringify({...JSON.parse(encodeSession(d,initialSession(d))),overrides:{common:{unknown:1},options:{}}})]){
  const r=await restoreSession(d,raw,()=>assert.fail());assert.equal(r.recovery,raw);
 }
});
test('unsupported horizon falls back to a current choice without discarding valid edits',async()=>{
 const d=fixture(),s=initialSession(d);s.horizon=15;s.draft.common.bonus=20;
 const r=await restoreSession(d,encodeSession(d,s),simulate);assert.equal(r.session.horizon,10);assert.equal(r.session.draft.common.bonus,20);
});
