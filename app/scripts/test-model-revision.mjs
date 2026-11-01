import test from 'node:test';
import assert from 'node:assert/strict';
import {validModelRevision,modelRevisionLabel} from '../src/modelRevision.ts';

test('the application and download use the same date and global revision number',()=>{
 assert.equal(modelRevisionLabel({date:'2026-11-01',number:17},'fr-FR','n° {number}'),'01/11/2026 · n° 17');
 assert.equal(modelRevisionLabel(undefined,'fr-FR','n° {number}'),null);
});
test('invalid or ambiguous revision metadata cannot be shown as a valid model version',()=>{
 for(const value of [{date:'2026-02-30',number:1},{date:'2026-1-1',number:1},{date:'2026-11-01',number:0},{date:'2026-11-01',number:true},{date:'2026-11-01',number:1.5}])assert.equal(validModelRevision(value),false);
 assert.throws(()=>modelRevisionLabel({date:'2026-02-30',number:1},'fr-FR','n° {number}'));
});
