import assert from 'node:assert/strict';
import {test} from 'node:test';
import {parseReadingHash,capabilityReadingHref,shouldRestoreReadingPosition} from '../src/readerNavigation.ts';

test('legacy complexity and Buy URLs resolve to one map while retaining business context',()=>{
 const complexity=parseReadingHash('#perimetres?section=complexity&grid_q=réassort&domain=domain-plan&area=ba-master-plan-management&stack=sap');
 assert.equal(complexity.params.get('section'),'coverage');
 assert.equal(complexity.params.get('view'),'complexity');
 assert.equal(complexity.params.get('q'),'réassort');
 assert.equal(complexity.params.get('domain'),'domain-plan');
 assert.equal(complexity.params.get('area'),'ba-master-plan-management');
 assert.equal(complexity.params.get('stack'),'sap');
 assert.equal(complexity.params.has('grid_q'),false);
 const buy=parseReadingHash('#perimetres?section=buy-coverage&capability=D05.e');
 assert.equal(buy.params.get('section'),'coverage');
 assert.equal(buy.params.get('view'),'gaps');
 assert.equal(buy.params.get('capability'),'D05.e');
});

test('legacy complexity query wins over unrelated old coverage query',()=>{
 const route=parseReadingHash('#perimetres?section=complexity&q=stocks&grid_q=promesse');
 assert.equal(route.params.get('q'),'promesse');
});

test('a map to work roundtrip preserves capability, facet, hierarchy, theme, search and stack',()=>{
 const original='#perimetres?section=coverage&view=gaps&domain=domain-plan&area=ba-master-plan-management&theme=reassort&q=stock&stack=sap';
 const work=parseReadingHash(capabilityReadingHref('work','D05.e',original));
 assert.equal(work.page,'build');
 assert.equal(work.params.get('detail'),'work');
 assert.equal(work.params.get('section'),'build');
 assert.equal(work.params.get('focus'),'work');
 const map=parseReadingHash(capabilityReadingHref('map','D05.e',work.hash));
 assert.equal(map.page,'perimetres');
 assert.equal(map.params.get('section'),'coverage');
 assert.equal(map.params.get('capability'),'D05.e');
 assert.equal(map.params.has('focus'),false);
 for(const field of ['view','domain','area','theme','q','stack'])assert.equal(map.params.get(field),parseReadingHash(original).params.get(field));
});

test('native capability identities are safely encoded and old charge bookmarks remain canonical',()=>{
 const link=capabilityReadingHref('work','cap/a&b','#perimetres?section=coverage');
 assert.equal(parseReadingHash(link).params.get('capability'),'cap/a&b');
 const old=parseReadingHash('#perimetres?section=features&capability=D05.e&q=réassort');
 assert.equal(old.page,'build');assert.equal(old.params.get('focus'),'work');assert.equal(old.params.get('capability'),'D05.e');
});

test('legacy cost readings preserve their section and scenario in the concise journey',()=>{
 const integration=parseReadingHash('#estimations?section=integration&focus=scenario-transfer-replenishment-order-driven&q=magasin&stack=sap');
 assert.equal(integration.page,'exploitation');
 assert.equal(integration.params.get('detail'),'integration');
 assert.equal(integration.params.get('q'),'magasin');
 assert.equal(integration.params.get('stack'),'sap');
 assert.equal(parseReadingHash('#estimations?section=annual').params.get('detail'),'run');
 assert.equal(parseReadingHash('#estimations').page,'build');
 assert.equal(parseReadingHash('#estimations?section=build&focus=method').params.get('detail'),'method');
 assert.equal(parseReadingHash('#build?section=integration&detail=method').page,'exploitation');
 assert.equal(parseReadingHash('#build?section=annual&detail=method').params.get('detail'),'run');
});

test('canonical journey and contextual routes are idempotent without touching simulation URLs',()=>{
 for(const hash of ['#logique','#perimetres?theme=finance','#build?detail=work&capability=D05.e','#exploitation?detail=run','#market?section=rates&stack=rust','#synvance?section=prix','#simulations','#simulation-hypotheses','#simulation-depenses']){
  const parsed=parseReadingHash(hash);
  assert.equal(parseReadingHash(parsed.hash).hash,parsed.hash);
 }
 assert.equal(parseReadingHash('#market?section=rates&stack=rust').params.get('detail'),'references');
});

test('explicit estimation anchors win over page position restoration after a map drawer link',()=>{
 const scenario='#estimations?section=integration&focus=scenario-transfer-replenishment-order-driven';
 assert.equal(parseReadingHash(scenario).params.get('focus'),'scenario-transfer-replenishment-order-driven');
 assert.equal(shouldRestoreReadingPosition(scenario),false);
 assert.equal(shouldRestoreReadingPosition('#estimations?section=build&focus=work&capability=D05.e'),false);
 assert.equal(shouldRestoreReadingPosition('#estimations?section=integration&focus=basis'),false);
 assert.equal(shouldRestoreReadingPosition('#estimations?section=work'),false);
 assert.equal(shouldRestoreReadingPosition('#estimations?section=integration'),true);
 assert.equal(shouldRestoreReadingPosition('#perimetres?section=coverage&capability=D05.e'),true);
});
