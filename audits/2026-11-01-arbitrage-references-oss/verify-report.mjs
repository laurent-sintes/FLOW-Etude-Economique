import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url),{chromium}=require('C:/Dev/FLOW-Etude-Economique/app/node_modules/playwright');
const folder=path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Z]:)/i,'$1'));
const report=path.join(folder,'rapport.html');const url=pathToFileURL(report).href;
const result={status:'passed',views:[]},browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
try{for(const width of [1440,390]){const page=await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce'});const errors=[];page.on('pageerror',e=>errors.push(String(e)));await page.goto(url);
assert.equal(await page.locator('article.unit').count(),11);assert.equal(await page.locator('article.unit .product-grid>section').count(),44);assert.equal(await page.locator('#estimations tbody tr').count(),11);
assert.equal(await page.locator('#arbitrages tbody tr').count(),11);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
assert.deepEqual(await page.evaluate(()=>Array.from(document.querySelectorAll('a[href^="#"]')).filter(a=>!document.getElementById(a.getAttribute('href').slice(1))).map(a=>a.getAttribute('href'))),[]);
for(const href of await page.locator('a[href^="../../"]').evaluateAll(xs=>xs.map(x=>x.getAttribute('href'))))await fs.access(path.resolve(folder,href));
await page.screenshot({path:path.join(folder,'rapport-'+width+'.png')});await page.locator('#master-plan-java-spring').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(folder,'master-plan-'+width+'.png')});assert.deepEqual(errors,[]);result.views.push({width,lots:11,oss_readings:44,links:'passed',body_overflow:false,page_errors:errors});await page.close()}
await fs.writeFile(path.join(folder,'browser-checks.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));}finally{await browser.close()}
