/** Browser validation against a current Python oracle; no historical amounts in CI. */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {performance} from 'node:perf_hooks';
import {chromium} from 'playwright';

const flags=new Map();
for(let index=2;index<process.argv.length;index+=2){
 const key=process.argv[index];
 assert.ok(['--url','--cases','--output'].includes(key)&&process.argv[index+1],`Unknown or incomplete argument: ${key}`);
 flags.set(key,process.argv[index+1]);
}
const address=flags.get('--url')||process.env.FLOW_PAGES_URL;
const casesPath=flags.get('--cases')||process.env.FLOW_PAGES_CASES;
assert.ok(address&&casesPath,'Provide --url and --cases (or FLOW_PAGES_URL / FLOW_PAGES_CASES).');
const site=new URL(address);site.hash='';site.search='';if(!site.pathname.endsWith('/'))site.pathname+='/';
assert.notEqual(site.pathname,'/','Test the GitHub Pages project subpath, not the origin root.');
const output=path.resolve(flags.get('--output')||'tmp/pages-validation-report.json');
await fs.mkdir(path.dirname(output),{recursive:true});
const oracle=JSON.parse((await fs.readFile(casesPath,'utf8')).replace(/^\uFEFF/,''));
assert.equal(Object.keys(oracle.cases).length,6,'Six current model scenarios are required.');
const navRoutes=['synvance','cartographie','vision','modele','conditions-realisation','marche','complexite','calcul-net','calcul-run','leviers','capacite-realisation','etude-marche','parametres','evaluation-core','comparer','se-projeter','simuler','glossaire'];
const synvanceProviders=['microsoft','sap'];
const routes=[navRoutes[0],...['business','oms','costs',...synvanceProviders].map(page=>'synvance-'+page),...navRoutes.slice(1)];
const report={url:site.href,status:'running',routes:{},worker:{},proofs:{},storage:{},errors:[],warnings:[]};
const started=performance.now();
const browser=await chromium.launch({headless:true,...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE?{executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE}:{})});
const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
let page;
const clean=value=>String(value).replace(/\s+/g,' ').trim();
const cloneWithoutVersion=value=>{const result=structuredClone(value);delete result.model_version;return result;};
const equalProjection=(actual,expected,name)=>assert.deepEqual(cloneWithoutVersion(actual),cloneWithoutVersion(expected),name);
let sequence=1000000;

await context.addInitScript(()=>{
 const OriginalWorker=window.Worker;
 window.__pagesTestWorkers=[];window.__pagesTestJobs=[];window.__pagesTestReplies=[];
 window.Worker=class extends OriginalWorker{
  constructor(...args){
   super(...args);window.__pagesTestWorkers.push(this);
   this.addEventListener('message',event=>window.__pagesTestReplies.push(event.data));
  }
  postMessage(message,...args){window.__pagesTestJobs.push(message);return super.postMessage(message,...args);}
 };
});
function watch(target){
 target.on('pageerror',error=>report.errors.push({kind:'javascript',message:error.message}));
 target.on('console',message=>{if(message.type()==='error'){
  const item={kind:'console',message:message.text(),url:message.location().url};
  (item.url.endsWith('/favicon.ico')?report.warnings:report.errors).push(item);
 }});
 target.on('request',request=>{
  const url=new URL(request.url());
  if(url.origin===site.origin&&!url.pathname.startsWith(site.pathname)&&url.pathname!=='/favicon.ico')report.errors.push({kind:'outside-base',url:url.href});
  if(url.origin===site.origin&&url.pathname.startsWith('/api/'))report.errors.push({kind:'server-api-on-static-site',url:url.href});
 });
 target.on('response',response=>{
  if(response.status()>=400&&!response.url().endsWith('/favicon.ico'))report.errors.push({kind:'http',status:response.status(),url:response.url()});
 });
}
async function route(id){
 await page.evaluate(value=>{location.hash='#'+value;},id);
 const navigationId=id.startsWith('synvance-')?'synvance':id;
 await page.locator(`.essential-nav-group a[href="#${navigationId}"][aria-current="page"]`).waitFor({state:'attached'});
 await page.locator('main .essential-page:visible').first().waitFor();
 if(navigationId==='synvance')await page.locator(`[data-synvance-page="${id==='synvance'?'overview':id.slice('synvance-'.length)}"]`).waitFor();
 if(id==='evaluation-core')await page.locator('[data-evaluation="annual"]').waitFor();
}
async function checkFrameworkNavigation(){
 await page.setViewportSize({width:390,height:844});await route('modele');
 const navigation=page.locator('#study-navigation');
 const opener=page.locator('.topbar button[aria-controls="study-navigation"]');
 const open=async()=>{
  await opener.focus();await page.keyboard.press('Enter');
  await page.waitForFunction(()=>document.querySelector('.topbar button[aria-controls="study-navigation"]')?.getAttribute('aria-expanded')==='true'&&document.querySelector('#study-navigation')?.contains(document.activeElement));
 };
 await open();await page.keyboard.press('Tab');
 assert.equal(await navigation.evaluate(element=>element.contains(document.activeElement)),true,'Tab should enter the open mobile navigation.');
 await page.keyboard.press('Escape');
 await page.waitForFunction(()=>document.querySelector('.topbar button[aria-controls="study-navigation"]')?.getAttribute('aria-expanded')==='false');
 assert.equal(await opener.evaluate(element=>element===document.activeElement),true,'Escape must return focus to the navigation button.');
 await open();await navigation.locator('nav a').last().focus();await page.keyboard.press('Tab');
 await page.waitForFunction(()=>document.querySelector('.topbar button[aria-controls="study-navigation"]')?.getAttribute('aria-expanded')==='false');
 assert.equal(await navigation.evaluate(element=>element.contains(document.activeElement)),false,'Leaving the nonmodal menu should keep focus outside.');
 await open();await navigation.locator('a[href="#marche"]').click();await route('marche');
 await page.waitForFunction(()=>document.querySelector('main h1')===document.activeElement);
 assert.equal(await opener.getAttribute('aria-expanded'),'false','Choosing a page must close the mobile navigation.');
 await open();await page.setViewportSize({width:1440,height:1000});
 await page.waitForFunction(()=>{
  const element=document.activeElement;if(!element||element===document.body)return false;
  const style=getComputedStyle(element),box=element.getBoundingClientRect();
  return style.visibility!=='hidden'&&style.display!=='none'&&box.width>0&&box.height>0;
 });
 await navigation.locator('a[aria-current="page"]').focus();await page.setViewportSize({width:390,height:844});
 await page.waitForFunction(()=>document.activeElement===document.querySelector('.topbar button[aria-controls="study-navigation"]'));
 await page.setViewportSize({width:1440,height:1000});
 report.accessibility={mobileMenuFocus:true,escapeRestoresFocus:true,leavingClosesMenu:true,pageHeadingFocus:true,resizeKeepsFocusVisible:true,reverseResizeRestoresFocus:true};
}
async function workerRequest(manifest,manifestUrl,requestPath,body){
 const id=++sequence;
 return page.evaluate(({id,manifest,manifestUrl,requestPath,body})=>new Promise((resolve,reject)=>{
  const worker=window.__pagesTestWorkers[0];
  if(!worker){reject(new Error('The application did not create its Python worker.'));return;}
  const timer=setTimeout(()=>{worker.removeEventListener('message',receive);reject(new Error('Python worker timed out.'));},180000);
  const receive=event=>{if(event.data.id===id){clearTimeout(timer);worker.removeEventListener('message',receive);resolve(event.data);}};
  worker.addEventListener('message',receive);
  worker.postMessage({id,manifest,manifestUrl,path:requestPath,body:body===undefined?'':JSON.stringify(body)});
 }),{id,manifest,manifestUrl,requestPath,body});
}
try{
 page=await context.newPage();watch(page);page.setDefaultTimeout(30000);
 await page.goto(site.href);
 await page.locator('.app-shell').waitFor();
 const manifestUrl=await page.evaluate(()=>new URL(JSON.parse(document.getElementById('app-config').textContent).static_site.manifest,document.baseURI).href);
 const manifestResponse=await page.request.get(manifestUrl);assert.ok(manifestResponse.ok());
 const manifest=await manifestResponse.json();
 assert.equal(manifest.simulation_contract,oracle.contract,'The browser and Python cases use different simulation contracts.');
 const bootstrapUrl=new URL(manifest.bootstrap,manifestUrl).href;
 const bootstrapResponse=await page.request.get(bootstrapUrl);assert.ok(bootstrapResponse.ok());
 const data=await bootstrapResponse.json();
 equalProjection(data.baseline,oracle.cases.reference.result,'The static reference differs from the Python reference.');
 assert.deepEqual(data.ui.essential.nav.map(item=>item.id),navRoutes);
 assert.equal(navRoutes.length,18);assert.equal(routes.length,23);
 await page.waitForFunction(()=>location.hash==='#vision');
 assert.equal(await page.locator('.brand-home').getAttribute('href'),'#vision','The home link must open the Vision.');
 await route('modele');await page.locator('.brand-home').click();await route('vision');
 assert.equal(await page.locator('.framework-vision').count(),1,'The logo must return to the Vision.');
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:width===390?844:1000});
  report.routes[width]=[];
  for(const id of routes){
   await route(id);
   const state=await page.locator('main .essential-page:visible').first().evaluate(element=>({text:element.innerText,overflow:document.documentElement.scrollWidth-innerWidth}));
   assert.ok(state.text.length>40,`Empty route: ${id}`);
   assert.doesNotMatch(state.text,/\{\{(?:notion|vue)\.|\bundefined\b|\bNaN\b/,`Unresolved content: ${id}`);
   assert.ok(state.overflow<=1,`Viewport overflow on ${width}/${id}: ${state.overflow}`);
   assert.equal(await page.locator('main a[href]').evaluateAll((links,allowed)=>links.filter(link=>/\.ya?ml(?:[?#]|$)/i.test(decodeURIComponent(link.getAttribute('href')||''))&&link.getAttribute('href')!==allowed).length,site.pathname+'exports/flow-modele-metier.yaml'),0,`Model data link on ${id}`);
   assert.equal(await page.locator('main details:visible').count(),0,`Disclosure on ${id}`);
   report.routes[width].push(id);
  }
 }
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:900});
  for(const [base,key] of [['modele','model'],['etude-marche','market'],['capacite-realisation','delivery']]){
   await route(base);
   for(const entry of data.ui.essential.dossiers[key].pages){
    const href='#'+base+(entry===data.ui.essential.dossiers[key].pages[0]?'':'?view='+entry.id);
    await page.locator(`.dossier-navigation a[href="${href}"]`).click();
    assert.equal(await page.locator('.dossier-navigation a[aria-current="page"]').getAttribute('href'),href);
    assert.ok(await page.locator('.dossier-sheet').isVisible());
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth<=1));
   }
  }
 }
 await checkFrameworkNavigation();
 await page.setViewportSize({width:1440,height:1000});
 const assets=await page.locator('img').evaluateAll(images=>images.map(image=>({src:image.src,loaded:image.complete&&image.naturalWidth>0})));
 assert.ok(assets.length>0);
 for(const asset of assets){assert.ok(asset.loaded,`Image did not load: ${asset.src}`);assert.ok(new URL(asset.src).pathname.startsWith(site.pathname),'Asset escaped the project base.');}
 report.assets=assets.length;

 // Professional product proposal stays distinct from adopted financial reference.
 const productProposal=data.content.core_product_scope?.proposal;
 if(productProposal){
  await route('evaluation-core');
  const panel=page.locator('.product-estimate-proposal');await panel.waitFor();
  const displayed=clean(await panel.innerText());
  const number=new Intl.NumberFormat(data.ui.locale,{maximumFractionDigits:0});
  assert.ok(displayed.includes(clean(number.format(productProposal.total_jh))),'Complete proposal effort is missing.');
  assert.equal(productProposal.status,'retained');
  assert.equal(productProposal.adopted_jh,productProposal.total_jh);
  if(productProposal.technical_trials){
   const trials=productProposal.technical_trials,section=panel.locator('.product-technical-trials');await section.waitFor();
   assert.ok(clean(await section.innerText()).includes(clean(trials.reading.conclusion)),'Technical trial conclusion is missing.');
   assert.ok(clean(await section.innerText()).includes(number.format(trials.checks_passed)),'Technical trial count is missing.');
   assert.equal(trials.effort_effect,'unchanged');
  }
  assert.equal(productProposal.total_jh,Object.values(productProposal.purposes).reduce((n,p)=>n+p.jh,0));
  assert.equal(data.baseline.options.find(o=>o.stack==='java-spring').build,oracle.cases.reference.result.options.find(o=>o.stack==='java-spring').build,'Proposal changed reference budget.');
  await panel.locator('h3').scrollIntoViewIfNeeded();await page.screenshot({path:output+'.professional.png'});
  await route('se-projeter');
  assert.equal(await page.locator('.economic-projection-option .economic-budget-parts').count(),data.baseline.options.length,'Projection must explain build/integration/functioning.');
  assert.ok(await page.locator('.economic-projection-option .core-build-partition').count()>0,'Retained business/IT split is missing from financial projection.');
  await page.locator('.essential-projection-panel').first().scrollIntoViewIfNeeded();await page.screenshot({path:output+'.projection.png'});
  report.proofs.completeProductProposal={proposal_jh:productProposal.total_jh,adopted_jh:productProposal.adopted_jh,purposes:productProposal.purposes,referencePreserved:true,projectionBreakdownVisible:true};
 }

 // Economic detail pages retain the full evidence behind their compact summaries.
 await route('evaluation-core');
 const familyLinks=await page.locator('[data-family-summary] a').evaluateAll(links=>links.map(link=>link.getAttribute('href')));
 assert.ok(familyLinks.length>0);
 assert.equal(await page.locator('[data-family]').count(),0,'Family demonstrations belong to detail pages.');
 for(const href of familyLinks){
  await page.locator(`a[href="${href}"]`).click();
  await page.locator('.economic-family-detail').waitFor();
  assert.equal(await page.locator('[data-family]').count(),1);
  assert.ok(await page.locator('.calculation-alignment').isVisible());
  await page.locator('.economic-family-detail a[href="#evaluation-core"]').first().click();
  await page.locator('[data-family-summary]').first().waitFor();
 }
 await route('parametres');
 for(const detail of ['tarifs','diagnostics']){
  await page.locator(`.dossier-navigation a[href="#parametres?detail=${detail}"]`).click();
  await page.locator('.framework-detail').waitFor();
  assert.equal(await page.locator('.framework-detail .core-method-section').count(),1);
  await page.locator('.framework-detail a.text-button[href="#parametres"]').click();
  await page.locator('.dossier-navigation a[href="#parametres?detail=tarifs"]').waitFor();
 }
 report.proofs.economicDetailPages=true;

 // Model YAML is hidden; a readable market note still initializes the real Python worker.
 await route('evaluation-core');
 assert.equal(await page.getByRole('button',{name:data.ui.essential.core_results.source,exact:true}).count(),0);
 assert.equal(await page.locator('.document-code:visible').count(),0);
 report.proofs.yamlHidden=true;
 await route('modele');
 const modelDownload=page.getByRole('link',{name:data.ui.model_download.label,exact:true});
 const downloadHref=await modelDownload.getAttribute('href');
 assert.equal(new URL(downloadHref,site).pathname,site.pathname+'exports/flow-modele-metier.yaml');
 const downloadResponse=await context.request.get(new URL(downloadHref,site).href);
 assert.ok(downloadResponse.ok());
 const downloadBytes=await downloadResponse.body();
 assert.match(downloadBytes.toString('utf8'),/^format: flow-business-model/m);
 assert.match(downloadBytes.toString('utf8'),/^metamodel:/m);
 assert.match(downloadBytes.toString('utf8'),/^model:/m);
 assert.match(downloadBytes.toString('utf8'),/^format_version: 2/m);
 assert.match(downloadBytes.toString('utf8'),/^evidence:/m);
 assert.match(downloadBytes.toString('utf8'),/source\/calculs-estimation-core\.yaml/);
 const downloadEvent=page.waitForEvent('download');
 await modelDownload.click();
 const downloaded=await downloadEvent;
 assert.equal(downloaded.suggestedFilename(),'flow-modele-metier.yaml');
 assert.equal(await downloaded.failure(),null);
 const savedBytes=await fs.readFile(await downloaded.path());
 assert.equal(createHash('sha256').update(savedBytes).digest('hex'),createHash('sha256').update(downloadBytes).digest('hex'));
 report.proofs.businessModelDownload={bytes:downloadBytes.length,sha256:createHash('sha256').update(downloadBytes).digest('hex'),singleFile:true};

 await route('etude-marche');
 const marketNote=data.ui.essential.application_framework.market.sections.find(section=>section.id==='evidence_status').links[0];
 const sourceButton=page.getByRole('button',{name:marketNote.label,exact:true});
 await sourceButton.click();
 await page.locator('dialog[open] .markdown').waitFor({timeout:180000});
 assert.ok((await page.locator('dialog[open] .markdown').innerText()).length>100);
 assert.equal(await page.locator('dialog[open] a[href]').evaluateAll((links,allowed)=>links.filter(link=>/\.ya?ml(?:[?#]|$)/i.test(decodeURIComponent(link.getAttribute('href')||''))&&link.getAttribute('href')!==allowed).length,site.pathname+'exports/flow-modele-metier.yaml'),0);
 const documentTitle=data.ui.documents.find(document=>document.path===marketNote.href)?.title;assert.ok(documentTitle);
 await page.getByRole('dialog',{name:documentTitle,exact:true}).waitFor();report.accessibility.documentDialogNamed=true;
 const sourceDownload=await page.locator('dialog[open] .document-meta a').getAttribute('href');
 assert.ok(new URL(sourceDownload,page.url()).pathname.startsWith(site.pathname));
 await page.locator('dialog[open] header > button.icon-button').focus();await page.keyboard.press('Escape');await page.locator('dialog[open]').waitFor({state:'detached'});
 assert.equal(await sourceButton.evaluate(element=>element===document.activeElement),true,'Document close lost focus.');
 report.proofs.markdown=true;report.proofs.focus=true;

 // Exercise the full engine, not a mock or a projection reconstructed in JavaScript.
 const workerStarted=performance.now();
 for(const [name,testCase] of Object.entries(oracle.cases)){
  const response=await workerRequest(manifest,manifestUrl,'/api/simulate',{parameters:testCase.parameters,model_version:data.model_version});
  assert.ok(!response.error,`${name}: ${JSON.stringify(response.error)}`);
  assert.equal(response.reply.status,200,name);
  equalProjection(response.reply.data,testCase.result,`Python browser parity: ${name}`);
 }
 for(const [name,testCase] of Object.entries(oracle.edge_cases||{})){
  const response=await workerRequest(manifest,manifestUrl,'/api/simulate',{parameters:testCase.parameters,model_version:data.model_version});
  assert.ok(!response.error,`${name}: ${JSON.stringify(response.error)}`);
  assert.equal(response.reply.status,200,name);
  equalProjection(response.reply.data,testCase.result,`Python browser edge-case parity: ${name}`);
  assert.equal(response.reply.data.anchor.budget_apres_bonus_eur_ht,null,'Unavailable counterpoint must remain unknown, not zero.');
 }
 const baselineAgain=await workerRequest(manifest,manifestUrl,'/api/simulate',{parameters:oracle.cases.reference.parameters,model_version:data.model_version});
 equalProjection(baselineAgain.reply.data,oracle.cases.reference.result,'A simulation mutated the reference.');
 const stale=await workerRequest(manifest,manifestUrl,'/api/simulate',{parameters:oracle.cases.reference.parameters,model_version:'obsolete'});
 assert.equal(stale.reply.status,422);assert.equal(stale.reply.data.error,'version');
 report.worker={scenarios:Object.keys(oracle.cases),edgeCases:Object.keys(oracle.edge_cases||{}),referenceIsolation:true,versionRejection:true,seconds:Math.round(performance.now()-workerStarted)/1000};

 await route('glossaire');
 assert.equal(await page.locator('.glossary-entry').count(),Object.keys(data.glossary.notions).length,'The glossary must expose every canonical notion.');
 await page.locator('#glossary-search').fill('JH');
 assert.ok(await page.locator('.glossary-entry').count()>0,'JH must be searchable.');
 assert.ok(await page.locator('.glossary-entry').count()<Object.keys(data.glossary.notions).length,'Search must narrow the glossary.');
 await page.locator('#glossary-search').fill('');
 await page.evaluate(()=>{location.hash='#glossaire?term=cocomo_ii';});
 await page.waitForFunction(()=>document.activeElement?.id==='glossary-term-cocomo_ii');
 assert.equal(await page.evaluate(()=>location.hash),'#glossaire?term=cocomo_ii');
 await route('calcul-run');
 const glossaryLink=page.locator('.method-glossary-link').first();
 const glossaryTarget=await glossaryLink.getAttribute('href');
 await glossaryLink.click();
 await page.waitForFunction(target=>location.hash===target&&document.activeElement?.id==='glossary-term-'+new URLSearchParams(target.split('?')[1]).get('term'),glossaryTarget);
 report.proofs.glossary={canonicalEntries:Object.keys(data.glossary.notions).length,search:true,directTerm:true,methodLink:true};
 await route('vision');
 assert.deepEqual(await page.locator('.vision-reading-paths a').evaluateAll(links=>links.map(a=>a.getAttribute('href'))),['#modele','#comparer','#capacite-realisation']);
 assert.deepEqual(await page.locator('.vision-adaptation a').evaluateAll(links=>links.map(a=>a.getAttribute('href'))),['#parametres','#simuler']);
 assert.deepEqual(await page.locator('.vision-evidence a').evaluateAll(links=>links.map(a=>a.getAttribute('href'))),['#cartographie','#synvance']);
 assert.equal(await page.locator('.vision-matrix tbody tr').count(),2);
 assert.equal(await page.locator('.vision-matrix tbody td').count(),4);
 assert.equal(await page.locator('.vision-proof-levels>li').count(),4,'The Vision should distinguish four levels of evidence.');
 await page.locator('.vision-confidence-links a[href="#conditions-realisation"]').click();await route('conditions-realisation');
 assert.equal(await page.locator('.delivery-conditions-page').count(),1);
 await route('capacite-realisation');assert.equal(await page.locator('.delivery-readiness-page').count(),1);
 const delivery=data.content.delivery_readiness;
 assert.equal(await page.locator('.delivery-review-date time').getAttribute('datetime'),delivery.date);
 await page.locator('[data-proof-ref]').first().click();
 await page.waitForFunction(()=>document.activeElement?.id.startsWith('delivery-readiness-proof-'));
 assert.equal(await page.locator('[data-delivery-proof]').count(),delivery.proofs.length);
 await page.locator('a[href="#capacite-realisation?view=hotspots"]').click();
 assert.equal(await page.locator('[data-hotspot]').count(),delivery.hotspots.length);
 await page.locator('a[href="#capacite-realisation?view=gates"]').click();
 assert.equal(await page.locator('[data-delivery-gate]').count(),delivery.gates.length);
 await route('capacite-realisation');
 await page.locator('main a[href="#conditions-realisation"]:visible').click();await route('conditions-realisation');
 await page.locator('main a[href="#capacite-realisation"]:visible').click();await route('capacite-realisation');
 await page.locator('.sidebar a[href="#cartographie"]').click();await route('cartographie');
 assert.equal(await page.locator('.cartography-page .model-map-systems').count(),1);
 assert.equal(await page.locator('.cartography-page .model-map a').getAttribute('href'),data.content.delivery_readiness.scope.link.href);
 const inputScope=await page.locator('.cartography-page').innerText();
 assert.ok(inputScope.includes(data.content.delivery_readiness.scope.source.version));
 await page.locator('main a[href="#modele?section=scope"]:visible').click();
 await page.waitForFunction(()=>document.activeElement?.id==='model-chapter-scope');
 const scope=data.content.delivery_readiness.scope;
 assert.equal(await page.locator('.delivery-scope-capability').count(),0);
 assert.equal(await page.locator('.sidebar a[href="#perimetre-retenu"]').count(),0);
 assert.equal(await page.locator('.model-map-systems').count(),1);
 assert.equal(await page.locator('.model-scope-areas').count(),0,'The fundamentals keep a short scope reminder.');
 assert.equal(await page.locator('.model-scope-provenance').count(),0);
 assert.equal(await page.locator('.model-map a[href="#cartographie"]').count(),1);
 await page.goto(new URL('#perimetre-retenu',site).href);
 await page.waitForFunction(()=>location.hash==='#cartographie');
 await page.locator('.cartography-page').waitFor();
 assert.equal(await page.locator('.model-scope-areas li').count(),scope.hierarchy.flatMap(domain=>domain.subdomains.flatMap(subdomain=>subdomain.areas)).length);
 assert.equal(await page.locator('.model-scope-areas>div').count(),scope.hierarchy.flatMap(domain=>domain.subdomains).length);
 for(const area of scope.hierarchy.flatMap(domain=>domain.subdomains.flatMap(subdomain=>subdomain.areas)))assert.equal(await page.locator(`[data-area="${area.id}"]`).innerText(),area.label);
 assert.equal(await page.locator('.cartography-provenance time').getAttribute('datetime'),scope.source.date);
 assert.equal(await page.locator('.cartography-page .model-map a').getAttribute('href'),scope.link.href);
 report.proofs.sponsorJourney={visionLanding:true,evidenceLevels:true,realizationCriteria:true,readinessDossier:true,retainedScope:true,nativeCartography:true};
 await route('vision');await page.locator('.vision-evidence a[href="#synvance"]').click();await route('synvance');
 assert.equal(data.ui.essential.nav_groups[0].items[0],'synvance');
 assert.equal(await page.locator('.synvance-provider').count(),0,'The Synvance overview should remain a short synthesis.');
 for(const provider of synvanceProviders){
  const detailRoute='synvance-'+provider;
  const detailLink=page.locator(`main a[href="#${detailRoute}"]`).first();
  await detailLink.click();
  await page.waitForFunction(id=>location.hash==='#'+id,detailRoute);
  await route(detailRoute);
  assert.equal(await page.locator('.synvance-provider').count(),1,'Each supplier page must show only its own detail.');
  assert.equal(await page.locator(`.synvance-provider[data-provider="${provider}"]`).count(),1);
  assert.equal(await page.locator('.synvance-document').count(),0,'Original document cards belong to the overview.');
  const back=page.locator('main a[href="#synvance"]:visible').first();await back.click();
  await page.waitForFunction(()=>location.hash==='#synvance');await route('synvance');
  assert.equal(await page.locator('.synvance-provider').count(),0);
 }
 report.proofs.synvanceSupplierPages=synvanceProviders;
 const documents=data.content.synvance_reference.documents.items;
 assert.equal(documents.filter(doc=>doc.format==='pdf').length,5);
 assert.equal(documents.filter(doc=>doc.format==='xlsx').length,2);
 assert.equal(await page.locator('.synvance-document').count(),documents.length);
 for(let index=0;index<documents.length;index++){
  const doc=documents[index],card=page.locator('.synvance-document').nth(index);
  const link=card.locator('a[download]');await link.waitFor();
  const url=new URL(await link.getAttribute('href'),page.url()).href;
  assert.ok(new URL(url).pathname.startsWith(site.pathname),'Original document escaped project path.');
  const response=await page.request.get(url);assert.ok(response.ok());const bytes=await response.body();
  assert.equal(createHash('sha256').update(bytes).digest('hex'),manifest.documents[doc.path.split('#')[0]].sha256,'Original source bytes differ.');
  if(doc.format==='pdf')assert.equal(bytes.subarray(0,5).toString(),'%PDF-');
 }
 const downloadPromise=page.waitForEvent('download');await page.locator('.synvance-document a[download]').first().click();const download=await downloadPromise;
 assert.ok(download.suggestedFilename().endsWith('.pdf'));assert.equal(await download.failure(),null);
 report.proofs.pdf=true;report.proofs.originalDocuments=documents.length;report.proofs.pdfDownload=true;
 report.proofs.synvanceEntry=true;report.proofs.visionMatrix=true;

 // Apply an oracle scenario through the visible controls, then save and restore it.
 const caseName=oracle.ui_case||Object.keys(oracle.cases).find(name=>name!=='reference');
 const personal=oracle.cases[caseName],base=oracle.cases.reference.parameters;
 await route('simuler');
 assert.equal(await page.locator('.essential-comparison .essential-option').count(),data.baseline.options.length,'All options must be visible without filtering.');
 assert.equal(await page.locator('.essential-simulation details,.essential-simulation [aria-expanded]').count(),0,'The economic workspace must read continuously.');
 for(const spec of data.ui.parameters.common)assert.ok(await page.locator(`[id="simulation-common.${spec.key}"]`).isVisible());
 for(const [key,value] of Object.entries(personal.parameters.common)){
  if(value===base.common[key])continue;
  assert.equal(await page.locator('.essential-common-toggle').count(),0,'Common hypotheses must remain visible without disclosure.');
  const spec=data.ui.parameters.common.find(row=>row.key===key);
  await page.locator(`[id="simulation-common.${key}"]`).fill(String(value/spec.scale));
 }
 for(const [slug,parameters] of Object.entries(personal.parameters.options)){
  const changes=Object.entries(parameters).filter(([key,value])=>value!==base.options[slug][key]);
  if(!changes.length)continue;
  await page.locator('.essential-select select').selectOption(slug);
  for(const [key,value] of changes){
   const spec=data.ui.parameters.option.find(row=>row.key===key);
   await page.locator(`[id="simulation-options.${slug}.${key}"]`).fill(String(value/spec.scale));
  }
 }
 const chosen=await page.locator('.essential-select select').inputValue();
 const horizon=data.ui.default_horizon;
 const expected=personal.result.options.find(option=>option.stack===chosen).horizons.find(row=>row.years===horizon).totals.total;
 const expectedAmount=clean(new Intl.NumberFormat(data.ui.locale,{minimumFractionDigits:data.ui.monetary_display.decimals,maximumFractionDigits:data.ui.monetary_display.decimals}).format(expected/data.ui.monetary_display.scale)+' '+data.ui.labels.money_unit);
 await page.waitForFunction(expected=>document.querySelector('.essential-selected-result strong')?.textContent.replace(/\s+/g,' ').trim()===expected,expectedAmount,{timeout:180000});
 await page.waitForFunction(()=>!document.querySelector('.essential-simulation .result-status'));
 const snapshot=await page.evaluate(key=>JSON.parse(sessionStorage.getItem(key)),data.ui.reload_storage_key);
 assert.deepEqual(snapshot.parameters,personal.parameters,'UI draft differs from the oracle scenario.');
 assert.ok(Object.keys(snapshot.overrides.common).length||Object.keys(snapshot.overrides.options).length,'Personal overrides were not saved.');
 await page.getByRole('button',{name:data.ui.simulation_workspace.saved,exact:true}).click();
 await page.locator('dialog[open] .scenario-name input').fill('Validation Pages');
 await page.locator('dialog[open]').getByRole('button',{name:data.ui.labels.save,exact:true}).click();
 await page.waitForFunction(key=>JSON.parse(localStorage.getItem(key)||'[]').some(item=>item.name==='Validation Pages'),data.ui.storage_key);
 const saved=await page.evaluate(key=>localStorage.getItem(key),data.ui.storage_key);
 const savedScenario=JSON.parse(saved).find(item=>item.name==='Validation Pages');assert.deepEqual(savedScenario.parameters,personal.parameters);
 await page.locator('dialog[open] header > button.icon-button').focus();await page.keyboard.press('Escape');
 await page.reload();await page.locator('.essential-simulation').waitFor({timeout:180000});
 await page.waitForFunction(expected=>document.querySelector('.essential-selected-result strong')?.textContent.replace(/\s+/g,' ').trim()===expected,expectedAmount,{timeout:180000});
 assert.equal(await page.evaluate(key=>localStorage.getItem(key),data.ui.storage_key),saved,'Reload rewrote the saved collection.');
 assert.equal(await page.locator('.session-notice[role="alert"]').count(),0,'Unexpected session recovery failure.');
 await page.getByRole('button',{name:data.ui.essential.simulation.reset,exact:true}).click();
 await page.getByRole('button',{name:data.ui.simulation_workspace.saved,exact:true}).click();
 const savedRow=page.locator('dialog[open] .saved-list>div').filter({has:page.getByText('Validation Pages',{exact:true})});
 await savedRow.getByRole('button',{name:data.ui.labels.load,exact:true}).click();
 await page.locator('dialog[open]').waitFor({state:'detached'});
 await page.waitForFunction(expected=>document.querySelector('.essential-selected-result strong')?.textContent.replace(/\s+/g,' ').trim()===expected,expectedAmount,{timeout:180000});
 report.storage={uiCase:caseName,sessionReload:true,savedCollectionPreserved:true,savedScenarioReload:true,keys:{session:data.ui.reload_storage_key,saved:data.ui.storage_key}};
 // Isolated navigation fixture: expose the published guide through an existing source
 // button, without mocking Python, documents, calculations or their error handling.
 const reader=await context.newPage();watch(reader);reader.setDefaultTimeout(30000);
 const readerData=structuredClone(data);
 const guideHasMissingLink=!manifest.documents['AGENTS.md'];
 readerData.ui.essential.market_study.offers.sources[0]={...readerData.ui.essential.market_study.offers.sources[0],path:guideHasMissingLink?'source/README.md':'source/__pages_missing_proof__.md',label:'Ouvrir le guide de validation'};
 await reader.route(bootstrapUrl,request=>request.fulfill({json:readerData}));
 const offersPage=readerData.ui.essential.dossiers.market.pages.find(entry=>entry.sections?.includes('offres'));
 assert.ok(offersPage,'Market dossier must expose supplier evidence.');
 await reader.goto(site.href+'#etude-marche?view='+encodeURIComponent(offersPage.id));
 await reader.getByRole('button',{name:'Ouvrir le guide de validation',exact:true}).click();
 if(guideHasMissingLink){
  await reader.locator('dialog[open] .markdown').waitFor({timeout:180000});
  await reader.locator('dialog[open]').getByRole('button',{name:'AGENTS.md',exact:true}).click();
 }
 await reader.locator('dialog[open] .notice').filter({hasText:data.ui.errors.missing_document}).waitFor({timeout:180000});
 assert.equal(await reader.locator('.app-shell').count(),1,'An unavailable proof crashed the application.');
 assert.equal(await reader.locator('dialog[open] .document-meta a').count(),0,'An unavailable proof offered a broken download.');
 await reader.locator('dialog[open] header > button.icon-button').focus();await reader.keyboard.press('Escape');
 await reader.locator('dialog[open]').waitFor({state:'detached'});
 await reader.locator('.market-study-page').waitFor();
 report.proofs.unpublishedDocumentHandled=true;
 await reader.close();
 assert.deepEqual(report.errors,[],'Browser or static network errors.');
 report.status='passed';
}catch(error){
 report.status='failed';report.failure=error.stack||String(error);process.exitCode=1;
 if(page)await page.screenshot({path:output+'.png',fullPage:true}).catch(()=>{});
}finally{
 report.seconds=Math.round(performance.now()-started)/1000;
 await fs.writeFile(output,JSON.stringify(report,null,2));
 await browser.close();
 console.log(JSON.stringify({status:report.status,output,routes:report.routes,worker:report.worker,storage:report.storage,proofs:report.proofs,errors:report.errors,failure:report.failure,seconds:report.seconds},null,2));
}
