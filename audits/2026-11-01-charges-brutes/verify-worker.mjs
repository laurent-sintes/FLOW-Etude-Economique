import {createRequire} from 'node:module';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url),{chromium}=require('C:/Dev/FLOW-Etude-Economique/app/node_modules/playwright');
const assets='C:/Dev/FLOW-Etude-Economique/app/dist/assets',workerPath='/assets/'+fs.readdirSync(assets).find(f=>f.startsWith('pages.worker-')&&f.endsWith('.js'));
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),start=performance.now();
try{
 const page=await browser.newPage();await page.goto('http://127.0.0.1:8766/#charges-acquisition');await page.locator('[data-core-status]').waitFor();
 const result=await page.evaluate(async(workerPath)=>{
  const manifestUrl=new URL('site-manifest.json',location.href).href,manifest=await(await fetch(manifestUrl)).json(),bootstrap=await(await fetch(new URL(manifest.bootstrap,manifestUrl))).json();
  const worker=new Worker(workerPath,{type:'module'});
  try{
   const response=await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('worker timeout')),60000);worker.onerror=error=>{clearTimeout(timer);reject(Error(error.message));};worker.onmessage=event=>{clearTimeout(timer);resolve(event.data);};worker.postMessage({id:1,manifest,manifestUrl,path:'/api/simulate',body:JSON.stringify({parameters:bootstrap.baseline.parameters,model_version:manifest.model_version})});});
   return {response,expected:bootstrap.baseline};
  }finally{worker.terminate();}
 },workerPath);
 assert.equal(result.response.reply?.status,200,JSON.stringify(result.response));assert.deepEqual(result.response.reply.data,result.expected);
 const report={status:'passed',seconds:(performance.now()-start)/1000,actual_browser_worker:true,python_engine:'Pyodide',options:result.expected.options.length,horizons:result.expected.options.reduce((n,o)=>n+o.horizons.length,0),adopted_baseline_identical:true};
 fs.writeFileSync('C:/Dev/FLOW-Etude-Economique/audits/2026-11-01-charges-brutes/worker-parity.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
