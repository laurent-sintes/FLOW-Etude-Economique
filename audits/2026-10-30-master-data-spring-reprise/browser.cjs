const {chromium}=require(process.cwd()+'/app/node_modules/playwright');
const {pathToFileURL}=require('node:url');const fs=require('node:fs');const path=require('node:path');
(async()=>{
 const dir=path.resolve('audits/2026-10-30-master-data-spring-reprise');
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
 const page=await browser.newPage({reducedMotion:'reduce',viewport:{width:1440,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(dir,'index.html')).href);
 const tables=await page.locator('table').count();const rows=await page.locator('table').first().locator('tbody tr').allTextContents();
 if(tables!==5||rows.length!==4)throw Error(JSON.stringify({tables,rows}));
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:1000});
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('viewport overflow '+width);
  await page.screenshot({path:path.join(dir,width===1440?'desktop.png':'mobile.png')});
 }
 for(const a of await page.locator('nav a').all()){
  const href=await a.getAttribute('href');if(await page.locator(href).count()!==1)throw Error('missing '+href);
 }
 if(errors.length)throw Error(JSON.stringify(errors));
 fs.writeFileSync(path.join(dir,'browser-check.json'),JSON.stringify({passed:true,tables,rows,viewports:[1440,390],errors},null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
