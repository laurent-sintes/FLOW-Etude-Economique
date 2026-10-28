import assert from 'node:assert/strict';
import {test} from 'node:test';
import {createFormat} from '../src/formatting.ts';

const f=createFormat('fr-FR',{scale:1000,decimals:0,rate_scale:1,rate_decimals:0,quantity_decimals:1},{money_unit:'k€ HT',annual_money_unit:'k€ HT / an',price_unit:'€ HT / JH'});
const readable=value=>value.replace(/[\u202f\u00a0]/g,' ');
test('budgets and differences share the same thousands scale at every magnitude',()=>{
 for(const [value,expected] of [[0,'0'],[36000,'36'],[23359650.56,'23 360'],[-706918,'-707']]){
  assert.equal(readable(f.money(value)),expected);
 }
});
test('daily rates display whole euros independently of budget scale',()=>{
 assert.equal(f.rate(750),'750');
 assert.equal(f.rate(925),'925');
 assert.equal(readable(f.amount(23359650.56)),'23 360 k€ HT');
 assert.equal(readable(f.annualAmount(1270931.5)),'1 271 k€ HT / an');
 assert.equal(readable(f.dailyRate(925)),'925 € HT / JH');
 assert.equal(readable(f.rate(1250)),'1 250');
});
test('formatting keeps raw calculation values and non-monetary quantities intact',()=>{
 const value=23359650.56;
 f.money(value);
 assert.equal(value,23359650.56);
 assert.equal(f.n(34), '34,0');
 assert.equal(f.pct(0.15),'15');
});
