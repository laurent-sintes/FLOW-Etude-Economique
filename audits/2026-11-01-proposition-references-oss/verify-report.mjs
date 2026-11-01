import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url),{chromium}=require('C:/Dev/FLOW-Etude-Economique/app/node_modules/playwright'),folder=path.dirname(fileURLToPath(import.meta.url)),data=JSON.parse(await fs.readFile(path.join(folder,'results.json'),'utf8'));
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),result={status:'passed',proposal_jh:data.proposal_jh,views:[]};
try{for(const width of [1440,390]){const page=await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce'});const errors=[],http=[];page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(/^https?:/.test(r.url()))http.push(r.url())});await page.goto(pathToFileURL(path.join(folder,'rapport.html')).href);
assert.equal(await page.locator('article.unit').count(),11);assert.equal(await page.locator('#comparaison tbody tr').count(),12);assert.match(await page.locator('header').innerText(),/5\s*950/);assert.match(await page.locator('header').innerText(),/-710/);
assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));assert.deepEqual(await page.evaluate(()=>Array.from(document.querySelectorAll('a[href^="#"]')).filter(a=>!document.getElementById(a.getAttribute('href').slice(1))).map(a=>a.getAttribute('href'))),[]);
for(const href of await page.locator('a').evaluateAll(xs=>xs.map(x=>x.getAttribute('href')).filter(h=>h&&!h.startsWith('#')&&!h.startsWith('http'))))await fs.access(path.resolve(folder,href));
await page.screenshot({path:path.join(folder,'rapport-'+width+'.png')});await page.locator('#inventory-ownership-java-spring').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(folder,'propriete-'+width+'.png')});assert.deepEqual(errors,[]);assert.deepEqual(http,[]);result.views.push({width,lots:11,rows_with_total:12,body_overflow:false,links:'passed',page_errors:errors,http_requests:http});await page.close()}
await fs.writeFile(path.join(folder,'browser-checks.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));}finally{await browser.close()}
