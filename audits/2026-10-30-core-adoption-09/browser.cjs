const {chromium}=require(process.cwd()+'/app/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const dir=path.resolve('audits/2026-10-30-core-adoption-09'),site=new URL(process.argv[2]||'http://127.0.0.1:8766/');site.hash='';
 const isStatic=site.pathname!=='/',errors=[],clean=x=>x.replace(/[\s\u00a0\u202f]/g,'');
 const expected=[['master-data-java-spring',1500,17],['stock-java-spring',340,10],['inventory-ownership-java-spring',100,7],['supply-controls-java-spring',40,5],['orders-java-spring',170,8],['master-plan-java-spring',350,11],['supply-decisions-java-spring',630,13],['service-fulfilment-java-spring',690,13],['process-management-java-spring',340,10]];
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
 const context=await browser.newContext({viewport:{width:1440,height:1100},reducedMotion:'reduce'}),page=await context.newPage();
 page.on('pageerror',e=>errors.push(e.message));page.setDefaultTimeout(90000);
 await page.goto(site.href+'#evaluation-core');
 await page.locator('[data-family-summary="process-management-java-spring"]').waitFor();
 assert.equal(await page.locator('[data-family-summary]').count(),9);
 for(const [id,jh,months] of expected){
  const card=page.locator('[data-family-summary="'+id+'"]'),values=await card.locator('.economic-value-summary').first().locator('dd').allTextContents();
  assert.ok(clean(values[0]).startsWith(String(jh)),id);assert.ok(clean(values[1]).startsWith(String(months)),id);
 }
 let body=clean(await page.locator('main').innerText());assert.match(body,/4160JH/);assert.match(body,/88\/88/);
 await page.locator('table[data-evaluation="core"]').scrollIntoViewIfNeeded();
 await page.screenshot({path:path.join(dir,(isStatic?'static':'local')+'-overview.png')});
 for(const [id,jh,months] of expected){
  await page.goto(site.href+'#evaluation-core?family='+id);const unit=page.locator('[data-family="'+id+'"]');await unit.waitFor();
  const values=await unit.locator('.economic-value-summary').first().locator('dd').allTextContents();assert.ok(clean(values[0]).startsWith(String(jh)));assert.ok(clean(values[1]).startsWith(String(months)));
  const roles=unit.locator(':scope > .table-scroll > table tbody tr');assert.equal(await roles.count(),9,id);
  const raw=await roles.locator('td:nth-child(2)').allTextContents();assert.equal(raw.reduce((n,s)=>n+Number(s.replace(/[^0-9]/g,'')),0),jh,id);
  if(id==='supply-decisions-java-spring'){
   await roles.first().scrollIntoViewIfNeeded();
   await unit.locator(':scope > .table-scroll > table').screenshot({path:path.join(dir,(isStatic?'static':'local')+'-roles.png')});
  }
 }
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:1000});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'page overflow '+width);
  const unit=page.locator('[data-family="process-management-java-spring"]');await unit.scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(dir,(isStatic?'static':'local')+'-'+(width===1440?'desktop':'mobile')+'.png')});
 }
 const download=await page.request.get(new URL('exports/flow-modele-metier.yaml',site).href,{timeout:90000});assert.ok(download.ok());
 const text=(await download.body()).toString('utf8');for(const [id] of expected)assert.ok(text.includes(id+'-v1'),id);
 const report={passed:true,url:site.href,units:9,rolesPerUnit:9,totalJH:4160,coveredCapabilities:88,viewports:[1440,390],downloadBytes:Buffer.byteLength(text),downloadEncoding:download.headers()['content-encoding']||'identity',errors};
 if(isStatic){
  const config=await page.evaluate(()=>JSON.parse(document.getElementById('app-config').textContent));
  const manifestUrl=new URL(config.static_site.manifest,site).href,manifest=await(await page.request.get(manifestUrl)).json();
  const bootstrap=await(await page.request.get(new URL(manifest.bootstrap,manifestUrl).href)).json();
  const oracle=JSON.parse(fs.readFileSync('tmp/core-adoption-pages-cases.json','utf8')),strip=x=>{const d=structuredClone(x);delete d.model_version;return d;};
  assert.deepEqual(strip(bootstrap.baseline),strip(oracle.cases.reference.result));
  const workerName=fs.readdirSync('tmp/core-adoption-pages/assets').find(x=>/^pages\.worker-.*\.js$/.test(x));assert.ok(workerName);
  await page.evaluate(url=>{window.__adoptionWorker=new Worker(url,{type:'module'});},new URL('assets/'+workerName,site).href);
  let seq=5000;
  const request=body=>page.evaluate(({id,manifest,manifestUrl,body})=>new Promise((resolve,reject)=>{
   const worker=window.__adoptionWorker,timer=setTimeout(()=>reject(Error('Python worker timeout')),180000);
   const receive=event=>{if(event.data.id===id){clearTimeout(timer);worker.removeEventListener('message',receive);resolve(event.data);}};
   worker.addEventListener('message',receive);worker.postMessage({id,manifest,manifestUrl,path:'/api/simulate',body:JSON.stringify(body)});
  }),{id:++seq,manifest,manifestUrl,body});
  const checks=[];for(const [name,test]of Object.entries(oracle.cases)){
   const answer=await request({parameters:test.parameters,model_version:bootstrap.model_version});assert.ok(!answer.error,JSON.stringify(answer.error));
   assert.equal(answer.reply.status,200,name);assert.deepEqual(strip(answer.reply.data),strip(test.result),name);checks.push(name);
  }
  const stale=await request({parameters:oracle.cases.reference.parameters,model_version:'obsolete'});assert.equal(stale.reply.status,422);assert.equal(stale.reply.data.error,'version');
  report.pythonBrowserParity=checks;report.staleVersionRejected=true;
 }
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(dir,'browser-'+(isStatic?'static':'local')+'.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify(report));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
