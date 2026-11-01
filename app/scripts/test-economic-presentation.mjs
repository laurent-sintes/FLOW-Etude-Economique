import assert from 'node:assert/strict';
import test from 'node:test';
import {hasUnestimatedConstruction,isPartialMake,completionRelation,comparisonTakeaways} from '../src/economicPresentation.ts';
const rows=[{stack:'dotnet',estimation_status:'pending_reestimation'},{stack:'java-spring',estimation_status:'partially_estimated'},{stack:'sap',estimation_status:'not_applicable'},{stack:'complete',estimation_status:'fully_estimated'}];
test('an unknown construction zero differs from a Buy zero and a personal budget',()=>{
 assert.equal(hasUnestimatedConstruction(rows,'dotnet',0),true);
 assert.equal(hasUnestimatedConstruction(rows,'sap',0),false);
 assert.equal(hasUnestimatedConstruction(rows,'dotnet',500000),false);
 assert.equal(hasUnestimatedConstruction(rows,'java-spring',0),false);
});
test('partial-reference labels follow coverage without qualifying complete or Buy budgets',()=>{
 assert.equal(isPartialMake(rows,'dotnet'),true);
 assert.equal(isPartialMake(rows,'java-spring'),true);
 assert.equal(isPartialMake(rows,'sap'),false);
 assert.equal(isPartialMake(rows,'complete'),false);
});

const visible=['java-spring','microsoft','sap'];
const published=(stack,offsets,total,month)=>({stack,comparison:{reference:'java-spring',horizons:Object.entries(offsets).map(([years,difference_eur_ht])=>({years:Number(years),difference_eur_ht}))},service_completion:{total_eur_ht:total,month}});
const current=()=>[published('java-spring',{3:0,10:0},8170877.1,78),published('microsoft',{3:2828685.36,10:9558015.65},7620227.45,44),published('sap',{3:13641506.68,10:25627758.54},16850516.68,36)];
test('completion wording follows published period stages including the exact service boundary',()=>{
 assert.equal(completionRelation('stage_service'),'included');
 assert.equal(completionRelation('stage_build'),'beyond');
 assert.equal(completionRelation('stage_integration'),'beyond');
 assert.equal(completionRelation('unknown'),null);
});
test('the current published comparison distinguishes cumulative and completion spending',()=>{
 for(const year of [3,10])assert.deepEqual(comparisonTakeaways(visible,current(),year),{java:'lowest',sap:'highest',microsoft:{spending:'lower',timing:'earlier'}});
});
test('the conclusion follows the selected horizon instead of a fixed preference',()=>{
 const rows=current();rows[1].comparison.horizons[0].difference_eur_ht=-10;
 assert.equal(comparisonTakeaways(visible,rows,3).java,'other');
 assert.equal(comparisonTakeaways(visible,rows,10).java,'lowest');
 rows[1].comparison.horizons[1].difference_eur_ht=30000000;
 assert.equal(comparisonTakeaways(visible,rows,10).sap,'other');
});
test('completion wording changes when the published spending and timing order changes',()=>{
 const rows=current();rows[1].service_completion={total_eur_ht:9000000,month:90};
 assert.deepEqual(comparisonTakeaways(visible,rows,10).microsoft,{spending:'higher',timing:'later'});
 rows[1].service_completion=structuredClone(rows[0].service_completion);
 assert.deepEqual(comparisonTakeaways(visible,rows,10).microsoft,{spending:'same',timing:'same'});
});
test('ties are described without inventing an exclusive cheapest or most expensive option',()=>{
 const rows=current();for(const row of rows)for(const h of row.comparison.horizons)h.difference_eur_ht=0;
 const result=comparisonTakeaways(visible,rows,10);
 assert.equal(result.java,'shared_lowest');assert.equal(result.sap,'shared_highest');
});
test('missing or inconsistent published results do not produce a ranking claim',()=>{
 const rows=current();rows[1].comparison.reference='another-reference';
 assert.equal(comparisonTakeaways(visible,rows,10).java,null);
 assert.equal(comparisonTakeaways(visible,rows,10).sap,null);
 rows[1].service_completion.total_eur_ht=NaN;
 assert.equal(comparisonTakeaways(visible,rows,10).microsoft,null);
 assert.equal(comparisonTakeaways(visible,current(),7).java,null);
});
test('only visible options affect the wording and published values remain untouched',()=>{
 const rows=current();rows.push(published('dotnet',{10:-99999999},0,1));const before=structuredClone(rows);
 assert.equal(comparisonTakeaways(visible,rows,10).java,'lowest');
 assert.deepEqual(rows,before);
});
