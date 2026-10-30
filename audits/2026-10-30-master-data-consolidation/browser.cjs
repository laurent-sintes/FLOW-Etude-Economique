const {chromium}=require(process.cwd()+'/app/node_modules/playwright');
const {pathToFileURL}=require('node:url');const fs=require('node:fs');const path=require('node:path');
(async()=>{
 const dir=path.resolve('audits/2026-10-30-master-data-consolidation');
 const d=JSON.parse(fs.readFileSync(path.join(dir,'results.json'),'utf8'));
 if(d.roles.reduce((s,r)=>s+r.jh,0)!==1500)throw Error('role total');
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
 const page=await browser.newPage({reducedMotion:'reduce',viewport:{width:1440,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(dir,'index.html')).href);
 const tables=await page.locator('table').count();if(tables!==3)throw Error('tables '+tables);
 const roleRows=await page.locator('#roles table').first().locator('tbody tr').count();if(roleRows!==10)throw Error('role rows '+roleRows);
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:1000});
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('viewport overflow '+width);
  await page.screenshot({path:path.join(dir,width===1440?'desktop.png':'mobile.png')});
 }
 await page.setViewportSize({width:1440,height:1000});await page.locator('#roles table').first().screenshot({path:path.join(dir,'roles.png')});
 for(const a of await page.locator('nav a').all()){
  const href=await a.getAttribute('href');if(await page.locator(href).count()!==1)throw Error('missing '+href);
 }
 if(errors.length)throw Error(JSON.stringify(errors));
 fs.writeFileSync(path.join(dir,'browser-check.json'),JSON.stringify({passed:true,tables,roleRows,roleSum:1500,viewports:[1440,390],errors},null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
