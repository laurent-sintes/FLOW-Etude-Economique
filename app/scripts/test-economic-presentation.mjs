import assert from 'node:assert/strict';
import test from 'node:test';
import {hasUnestimatedConstruction,isPartialMake} from '../src/economicPresentation.ts';
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
