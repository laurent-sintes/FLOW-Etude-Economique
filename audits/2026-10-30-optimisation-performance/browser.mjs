import {chromium} from '../../app/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import {performance} from 'node:perf_hooks';
const out=new URL('./',import.meta.url);
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
const report={environment:'Edge headless, localhost 8766, 1440×1000, no network/CPU throttling, fresh browser contexts; server already loaded',open:[],routes:{},simulation_ui:[],errors:[]};
const frame=page=>page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
for(let run=0;run<5;run++){
 const context=await browser.newContext({viewport:{width:1440,height:1000}});
 const page=await context.newPage();
 page.on('pageerror',error=>report.errors.push(error.message));
 await page.addInitScript(()=>{window.__longTasks=[];new PerformanceObserver(list=>window.__longTasks.push(...list.getEntries().map(x=>({start:x.startTime,duration:x.duration})))).observe({type:'longtask',buffered:true});});
 let start=performance.now();
 await page.goto('http://127.0.0.1:8766/#vision');
 await page.locator('.framework-vision').waitFor();await frame(page);
 report.open.push({ms:performance.now()-start,...await page.evaluate(()=>({navigation:performance.getEntriesByType('navigation')[0].toJSON(),paints:performance.getEntriesByType('paint').map(x=>x.toJSON()),longTasks:window.__longTasks,resources:performance.getEntriesByType('resource').map(x=>({name:x.name,ms:x.duration,transferBytes:x.transferSize,decodedBytes:x.decodedBodySize}))}))});
 for(const [route,selector] of [['modele','.model-reading'],['evaluation-core','.calculation-alignment'],['simuler','.essential-simulation']]){
  start=performance.now();await page.evaluate(id=>location.hash=id,route);
  await page.locator(selector).first().waitFor({state:'visible'});await frame(page);
  (report.routes[route]??=[]).push(performance.now()-start);
 }
 const input=page.locator('input[id="simulation-options.java-spring.build"]');
 const original=Number(await input.inputValue());
 const step=Number(await input.getAttribute('step'))||1;
 const response=page.waitForResponse(r=>r.url().endsWith('/api/simulate')&&r.request().method()==='POST');
 start=performance.now();await input.fill(String(original+step));await response;
 await page.locator('.result-status').waitFor({state:'hidden'});await frame(page);
 report.simulation_ui.push(performance.now()-start);
 await context.close();
}
await browser.close();
function stats(values){const s=[...values].sort((a,b)=>a-b);return {n:s.length,min_ms:s[0],median_ms:s[Math.floor(s.length/2)],max_ms:s.at(-1)};}
report.summary={open:stats(report.open.map(x=>x.ms)),routes:Object.fromEntries(Object.entries(report.routes).map(([k,v])=>[k,stats(v)])),simulation_ui:stats(report.simulation_ui)};
await fs.writeFile(new URL('browser.json',out),JSON.stringify(report,null,2));
console.log(JSON.stringify(report.summary,null,2));
