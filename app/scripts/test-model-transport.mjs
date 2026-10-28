import assert from 'node:assert/strict';
import {test} from 'node:test';
import {hydrateBootstrap} from '../src/modelTransport.ts';

test('canonical transport shares nodes and rows without changing the simulation',()=>{
 const original={baseline:{parameters:{value:12}},content:{transport_format:1,complexity:{method:{}},business_map:{nodes:{d:{id:'d',nom:'Domain'},c:{id:'c',nom:'Capability'}},rows:[{capacite:'c',hierarchie:['d'],variantes:[],work:{cost:102000}},{capacite:'c',hierarchie:['d'],variantes:[],work:{cost:0}}]}}};
 const result=hydrateBootstrap(original);
 assert.equal(result.content.complexity.rows,result.content.business_map.rows);
 assert.equal(result.content.business_map.rows[0].hierarchie[0],result.content.business_map.rows[1].hierarchie[0]);
 assert.equal(result.content.business_map.rows[0].work.cost,102000);
 assert.equal(result.baseline.parameters.value,12);
 assert.equal(hydrateBootstrap(result),result);
});

test('unknown content format and missing canonical node fail explicitly',()=>{
 assert.throws(()=>hydrateBootstrap({content:{transport_format:9}}),/ERR_CONTENT_FORMAT/);
 assert.throws(()=>hydrateBootstrap({content:{transport_format:1,business_map:{nodes:{},rows:[{capacite:'missing'}]}}}),/ERR_NODE/);
});
