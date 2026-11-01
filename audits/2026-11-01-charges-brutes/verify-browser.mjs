import {createRequire} from 'node:module';
import fs from 'node:fs';
import assert from 'node:assert/strict';
import path from 'node:path';
const require=createRequire(import.meta.url),{chromium}=require('C:/Dev/FLOW-Etude-Economique/app/node_modules/playwright');
const folder=path.dirname(new URL(import.meta.url).pathname).replace(/^\/(?:([A-Za-z]):)/,'$1:');
const started=performance.now(),browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
const results=[],errors=[],apiRequests=[];
try{
 for(const width of [1440,390]){
  const context=await browser.newContext({viewport:{width,height:1000},reducedMotion:'reduce'}),page=await context.newPage();
  page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(new URL(r.url()).pathname.startsWith('/api/'))apiRequests.push(r.url());});
  const requests=[];page.on('request',r=>requests.push(r.url()));
  await page.goto('http://127.0.0.1:8766/#vision');await page.locator('.framework-vision').waitFor();
  assert.ok(!requests.some(u=>u.endsWith('/gross-evaluations.json')));
  for(const phase of ['acquisition','integration','fonctionnement'])for(const option of ['java-spring','microsoft','sap']){
   await page.evaluate(hash=>{location.hash=hash},`charges-${phase}?option=${option}`);
   const view=page.locator(`[data-gross-phase="${phase}"]`);await view.waitFor();
   await view.locator(`.journey-option-navigation a[data-open="true"][href$="option=${option}"]`).waitFor();
   assert.equal(await view.locator('.framework-phase-track [aria-current="step"]').count(),1);
   assert.equal(await view.locator('.dossier-content h2').count(),1);
   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);assert.ok(!overflow,`${width}/${phase}/${option} overflow`);
   const text=(await view.innerText()).replace(/\s/g,'');
   if(phase==='acquisition'&&option==='java-spring'){
    assert.ok(text.includes('6660')&&text.includes('5950')&&text.includes('-710'));
    assert.equal(await view.locator('.gross-lots tbody tr').count(),11);
    assert.equal(await view.locator('.gross-references tbody tr').count(),11);
    assert.equal(await view.locator('[data-core-status="proposal_not_adopted"]').count(),1);
    if(width===1440)await page.screenshot({path:path.join(folder,'desktop.png')});
    else{await view.locator('.dossier-content h2').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(folder,'mobile.png')});}
   }
   if(phase==='fonctionnement'&&option==='java-spring')assert.ok(text.includes('JH/an'));
   if(phase==='fonctionnement'&&option!=='java-spring')assert.ok(text.includes('Annéetarifaire5'));
   results.push({width,phase,option,overflow});
  }
  await page.locator('.gross-method-link').click();await page.locator('[data-framework-phase="fonctionnement"]').waitFor();
  assert.ok(page.url().endsWith('#fonctionnement?option=sap'));
  await page.locator('[data-framework-phase] a.framework-primary-link').click();await page.locator('[data-gross-phase="fonctionnement"]').waitFor();
  assert.ok(page.url().endsWith('#charges-fonctionnement?option=sap'));
  await page.locator('.gross-evaluations .framework-phase-track a').first().click();
  await page.locator('[data-gross-phase="acquisition"]').waitFor();assert.ok(page.url().endsWith('option=sap'));
  await page.reload();await page.locator('[data-gross-phase="acquisition"]').waitFor();
  assert.equal(await page.locator('.gross-evaluations .journey-option-navigation a[data-open="true"][href$="option=sap"]').count(),1);
  const java=page.locator('.gross-evaluations .journey-option-navigation a').first();await java.focus();await page.keyboard.press('Enter');
  await page.locator('[data-core-status="proposal_not_adopted"]').waitFor();
  assert.equal(await page.locator('.dossier-content').evaluate(e=>getComputedStyle(e).animationName),'none');
  assert.equal(requests.filter(u=>u.endsWith('/gross-evaluations.json')).length,2); // One fetch in each loaded session.
  await context.close();
 }
 assert.deepEqual(errors,[]);assert.deepEqual(apiRequests,[]);
 fs.writeFileSync(path.join(folder,'browser-checks.json'),JSON.stringify({status:'passed',seconds:(performance.now()-started)/1000,views:results,reciprocal_navigation:true,option_retained_on_reload:true,keyboard:true,reduced_motion:true,apiRequests,errors},null,2));
 console.log(JSON.stringify({status:'passed',views:results.length,seconds:(performance.now()-started)/1000,apiRequests,errors}));
}finally{await browser.close();}
