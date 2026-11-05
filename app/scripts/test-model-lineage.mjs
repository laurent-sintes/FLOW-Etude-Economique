import test from 'node:test';
import assert from 'node:assert/strict';
import {modelLineage} from '../src/modelLineage.ts';
const edges=[{id:'ab',source:'a',target:'b'},{id:'bc',source:'b',target:'c'},{id:'cd',source:'c',target:'d'},{id:'ax',source:'a',target:'x'},{id:'yd',source:'y',target:'d'},{id:'uv',source:'u',target:'v'}];
test('lineage spans all directed ancestors and descendants without unrelated siblings',()=>{
 const l=modelLineage(edges,'c');
 assert.deepEqual([...l.nodes].sort(),['a','b','c','d']);
 assert.deepEqual([...l.relations].sort(),['ab','bc','cd']);
});
test('cycles, self links and parallel relations are preserved and terminate',()=>{
 const cyclic=[...edges,{id:'ca',source:'c',target:'a'},{id:'cc',source:'c',target:'c'},{id:'bc2',source:'b',target:'c'}];
 const l=modelLineage(cyclic,'c');
 assert.deepEqual([...l.relations].sort(),['ab','ax','bc','bc2','ca','cc','cd']);
 assert.ok(!l.nodes.has('y')&&!l.nodes.has('u'));
});
test('no selection highlights nothing and never changes the input graph',()=>{
 const before=structuredClone(edges);
 assert.equal(modelLineage(edges).nodes.size,0);
 assert.deepEqual(edges,before);
 assert.deepEqual([...modelLineage(edges,'isolated').nodes],['isolated']);
});
