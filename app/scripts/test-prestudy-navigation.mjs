import test from 'node:test';
import assert from 'node:assert/strict';
import {preStudyDestination} from '../src/preStudyNavigation.ts';

test('legacy solution links preserve the selected capability or Business Area',()=>{
 assert.deepEqual(preStudyDestination('etude-marche',new URLSearchParams('focus=ba-stock~sap')),{page:'preetude-solutions',view:'comparison',focus:'ba-stock~sap'});
 assert.deepEqual(preStudyDestination('etude-marche',new URLSearchParams('view=qualification&focus=D02.c~erpnext')),{page:'preetude-solutions',view:'qualification',focus:'D02.c~erpnext'});
 assert.deepEqual(preStudyDestination('etude-marche',new URLSearchParams('view=products')),{page:'preetude-solutions',view:'products',focus:undefined});
});
test('funding and transposition links remain in the economic dossier',()=>{
 for(const query of ['', 'focus=G01','focus=budgets','focus=CB-JAVA-SERVICES','focus=G01-detail','view=references','view=construction'])assert.equal(preStudyDestination('etude-marche',new URLSearchParams(query)),null);
});
test('original offers still lead to their source dossier',()=>{
 assert.deepEqual(preStudyDestination('etude-marche',new URLSearchParams('view=offers')),{page:'synvance'});
 assert.equal(preStudyDestination('preetude-solutions',new URLSearchParams()),null);
});

test('moved productivity and retired technology links have stable destinations',()=>{
 assert.deepEqual(preStudyDestination('preetude-solutions',new URLSearchParams('view=productivity')),{page:'preetude-productivite'});
 for(const id of ['dotnet','rust'])assert.deepEqual(preStudyDestination('acquisition',new URLSearchParams('option='+id)),{page:'preetudes'});
});
