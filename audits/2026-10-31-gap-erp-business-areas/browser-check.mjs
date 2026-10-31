import {createRequire} from 'node:module';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {performance} from 'node:perf_hooks';
const require=createRequire(import.meta.url),{chromium}=require('C:/Dev/FLOW-Etude-Economique/app/node_modules/playwright');
const started=performance.now(),dir='audits/2026-10-31-gap-erp-business-areas',browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),views=[];
try{
 for(const width of [1440,390]){
  const page=await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce'});const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto('file:///C:/Dev/FLOW-Etude-Economique/'+dir+'/rapport.html');
  assert.equal(await page.locator('.matrix tbody tr').count(),28);assert.equal(await page.locator('.cell').count(),168);
  assert.equal(await page.locator('.gap').count(),9);assert.equal(await page.locator('#sources article').count(),53);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
  await page.screenshot({path:'tmp/gap-report-top-'+width+'.png'});
  await page.locator('#columns').selectOption('buy');
  assert.equal(await page.locator('.matrix thead [data-col]:visible').count(),2);
  await page.locator('#search').fill('BC-049');
  assert.equal(await page.locator('.matrix tbody tr:visible').count(),1);
  await page.getByRole('button',{name:'Service Planning — Microsoft + K3',exact:true}).click();
  await page.locator('#inspector').waitFor({state:'visible'});
  assert.match(await page.locator('#inspector').innerText(),/répartition à adapter/);
  assert.match(await page.locator('#inspector').innerText(),/G03/);
  assert.match(await page.locator('#inspector').innerText(),/non établie/);
  await page.locator('#matrice').scrollIntoViewIfNeeded();
  await page.screenshot({path:'tmp/gap-report-matrix-'+width+'.png'});
  await page.locator('#columns').selectOption('oss');
  assert.equal(await page.locator('.matrix thead [data-col]:visible').count(),4);
  await page.locator('#search').fill('Customs Services');
  await page.getByRole('button',{name:'Customs Services — Tryton',exact:true}).click();
  assert.match(await page.locator('#inspector').innerText(),/pas dossier complet/);
  const missing=await page.locator('a[href^="#"]').evaluateAll(links=>links.map(a=>a.getAttribute('href').slice(1)).filter(id=>!document.getElementById(id)));
  assert.deepEqual(missing,[]);assert.deepEqual(errors,[]);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
  views.push({width,status:'passed',rows:28,cells:168,filters:true,inspection:true,fragment_links:true,page_errors:0});await page.close();
 }
 const result={status:'passed',seconds:Math.round(performance.now()-started)/1000,views};
 await fs.writeFile(dir+'/browser-verification.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{await browser.close();}
