const {chromium}=require(process.cwd()+'/app/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const dir=path.resolve('audits/2026-10-30-stock-adoption-10');
 const site=new URL(process.argv[2]||'http://127.0.0.1:8766/');site.hash='';if(!site.pathname.endsWith('/'))site.pathname+='/';
 const isStatic=site.pathname!=='/';const errors=[];
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
 const context=await browser.newContext({reducedMotion:'reduce',viewport:{width:1440,height:1000}});
 const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
 page.setDefaultTimeout(60000);await page.goto(site.href+'#evaluation-core');
 const md=page.locator('[data-family="master-data-java-spring"]'),stock=page.locator('[data-family="stock-java-spring"]');
 await stock.waitFor();assert.equal(await md.count(),1);assert.equal(await stock.count(),1);
 const value=async(el)=>el.locator('.economic-value-summary').first().locator('dd').allTextContents();
 const clean=x=>x.replace(/[\s\u00a0\u202f]/g,'');
 const mdValues=await value(md),stockValues=await value(stock);
 assert.ok(clean(mdValues[0]).startsWith('1500'));assert.ok(clean(mdValues[1]).startsWith('17'));
 assert.ok(clean(stockValues[0]).startsWith('340'));assert.ok(clean(stockValues[1]).startsWith('10'));
 const rows=stock.locator('table').first().locator('tbody tr');assert.equal(await rows.count(),9);
 const roles=await rows.locator('td:nth-child(2)').allTextContents();
 assert.equal(roles.reduce((s,t)=>s+Number(t.replace(/[^0-9]/g,'')),0),340);
 assert.match(await stock.innerText(),/Master Data Java\/Spring/);
 assert.match(await stock.innerText(),/Réutilisé/);
 const heading=await page.locator('main').innerText();assert.match(clean(heading),/1840JH/);
 assert.match(clean(heading),/14\/88/);
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:1000});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'page overflow '+width);
  await stock.scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(dir,(isStatic?'static-':'local-')+(width===1440?'desktop':'mobile')+'.png')});
 }
 await page.setViewportSize({width:1440,height:1000});
 await stock.locator('table').first().screenshot({path:path.join(dir,(isStatic?'static-':'local-')+'roles.png')});
 const download=await page.request.get(new URL('exports/flow-modele-metier.yaml',site).href);
 assert.ok(download.ok());const raw=await download.body();const text=raw.toString('utf8');
 assert.ok(text.includes('stock-java-spring-v1')&&text.includes('master-data-java-spring-v1'));
 const report={passed:true,url:site.href,roles:9,stockJH:340,stockMonths:10,masterDataJH:1500,masterDataMonths:17,
  retainedCumulativeJH:1840,coveredCapabilities:14,viewports:[1440,390],downloadBytes:raw.length,errors};
 if(isStatic){
  const config=await page.evaluate(()=>JSON.parse(document.getElementById('app-config').textContent));
  const manifestUrl=new URL(config.static_site.manifest,site).href;
  const manifest=await (await page.request.get(manifestUrl)).json();
  const bootstrap=await (await page.request.get(new URL(manifest.bootstrap,manifestUrl).href)).json();
  const oracle=JSON.parse(fs.readFileSync(path.resolve('tmp/pages-validation.json'),'utf8'));
  const withoutVersion=x=>{const d=structuredClone(x);delete d.model_version;return d;};
  assert.deepEqual(withoutVersion(bootstrap.baseline),withoutVersion(oracle.cases.reference.result));
  const name=fs.readdirSync('app/dist-pages/assets').find(n=>/^pages\.worker-.*\.js$/.test(n));assert.ok(name);
  const workerURL=new URL('assets/'+name,site).href;
  await page.evaluate(workerURL=>{window.__stockWorker=new Worker(workerURL,{type:'module'});},workerURL);
  let sequence=100000;
  const request=body=>page.evaluate(({id,manifest,manifestUrl,body})=>new Promise((resolve,reject)=>{
   const worker=window.__stockWorker,timer=setTimeout(()=>reject(Error('Python worker timeout')),180000);
   const receive=e=>{if(e.data.id===id){clearTimeout(timer);worker.removeEventListener('message',receive);resolve(e.data);}};
   worker.addEventListener('message',receive);worker.postMessage({id,manifest,manifestUrl,path:'/api/simulate',body:JSON.stringify(body)});
  }),{id:++sequence,manifest,manifestUrl,body});
  const checked=[];
  for(const [key,test] of Object.entries(oracle.cases)){
   const answer=await request({parameters:test.parameters,model_version:bootstrap.model_version});
   assert.ok(!answer.error,JSON.stringify(answer.error));assert.equal(answer.reply.status,200,key);
   assert.deepEqual(withoutVersion(answer.reply.data),withoutVersion(test.result),key);checked.push(key);
  }
  const stale=await request({parameters:oracle.cases.reference.parameters,model_version:'obsolete'});
  assert.equal(stale.reply.status,422);assert.equal(stale.reply.data.error,'version');
  report.pythonBrowserParity=checked;report.staleVersionRejected=true;
 }
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(dir,isStatic?'browser-static.json':'browser-local.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify(report));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
