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
 assert.ok(['--url','--cases','--output','--allow-root'].includes(key)&&process.argv[index+1],`Unknown or incomplete argument: ${key}`);
 flags.set(key,process.argv[index+1]);
}
const address=flags.get('--url')||process.env.FLOW_PAGES_URL;
const casesPath=flags.get('--cases')||process.env.FLOW_PAGES_CASES;
assert.ok(address&&casesPath,'Provide --url and --cases (or FLOW_PAGES_URL / FLOW_PAGES_CASES).');
const site=new URL(address);site.hash='';site.search='';if(!site.pathname.endsWith('/'))site.pathname+='/';
if(flags.get('--allow-root')!=='true')assert.notEqual(site.pathname,'/','Test the GitHub Pages project subpath, not the origin root.');
const output=path.resolve(flags.get('--output')||'tmp/pages-validation-report.json');
await fs.mkdir(path.dirname(output),{recursive:true});
const oracle=JSON.parse((await fs.readFile(casesPath,'utf8')).replace(/^\uFEFF/,''));
assert.equal(Object.keys(oracle.cases).length,6,'Six current model scenarios are required.');
const navRoutes=['preetudes','preetude-projets','preetude-solutions','preetude-couts','preetude-productivite','charges-acquisition','charges-integration','charges-fonctionnement','synvance','cartographie','vision','modele','conditions-realisation','marche','complexite','calcul-net','calcul-run','leviers','acquisition','integration','fonctionnement','scenarios','methodes','capacite-realisation','etude-marche','parametres','evaluation-core','comparer','se-projeter','simuler','glossaire','telechargements'];
const synvanceProviders=['microsoft','sap'];
const routes=[navRoutes[0],...['business','oms','costs',...synvanceProviders].map(page=>'synvance-'+page),...navRoutes.slice(1)];
const report={url:site.href,status:'running',routes:{},worker:{},proofs:{},storage:{},errors:[],warnings:[]};
const started=performance.now();
const browser=await chromium.launch({headless:true,...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE?{executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE}:{})});
const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
let page,workerPage;
const httpApiRequests=[];
context.on('request',request=>{if(new URL(request.url()).pathname.includes('/api/'))httpApiRequests.push(request.url());});
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

const baseRoute=id=>id.split('?')[0];
const currentRoute=id=>({ 'etude-marche':'evaluation-core','se-projeter':'comparer','simuler':'comparer' }[baseRoute(id)]||baseRoute(id));
const sidebarRoute=id=>{const route=currentRoute(id);return route.startsWith('synvance-')?'synvance':['modele','conditions-realisation','capacite-realisation','marche','complexite','calcul-net','calcul-run','leviers'].includes(route)?'methodes':route;};
async function route(id){
 await page.evaluate(value=>{location.hash='#'+value;},id);
 const expected=sidebarRoute(id);
 await page.waitForFunction(expected=>{
  const selected=document.querySelector('.essential-nav-group a[aria-current="page"]');
  return selected?.getAttribute('href')?.split('?')[0]==='#'+expected;
 },expected);
 await page.locator('main .essential-page:visible').first().waitFor();
 const resolved=currentRoute(id);
 if(resolved.startsWith('charges-'))await page.locator('.gross-evaluations').waitFor();
 if(['comparer','evaluation-core','parametres'].includes(resolved))await page.locator(baseRoute(id)==='etude-marche'||/[?&]view=(financements|transpositions)/.test(id)?'.eco-evidence-links,.market-comparison':'.eco-decision-scope,.eco-determinants').first().waitFor();
 if(resolved==='preetude-solutions')await page.locator('[data-prestudy=solutions] .dossier-sheet :is(.comparison-table,.essential-market-panel,.market-qualification-reading)').first().waitFor();
 if(resolved==='synvance'||resolved.startsWith('synvance-'))await page.locator(`[data-synvance-page="${resolved==='synvance'?'overview':resolved.slice('synvance-'.length)}"]`).waitFor();
}
async function checkFrameworkNavigation(){
 await page.setViewportSize({width:390,height:844});await route('modele');
 const nav=page.locator('#study-navigation'),opener=page.locator('.topbar button[aria-controls="study-navigation"]');
 const open=async()=>{await opener.focus();await page.keyboard.press('Enter');await page.waitForFunction(()=>document.querySelector('.topbar button[aria-controls="study-navigation"]')?.getAttribute('aria-expanded')==='true'&&document.querySelector('#study-navigation')?.contains(document.activeElement));};
 await open();await page.keyboard.press('Tab');assert.ok(await nav.evaluate(el=>el.contains(document.activeElement)));
 await page.keyboard.press('Escape');await page.waitForFunction(()=>document.querySelector('.topbar button[aria-controls="study-navigation"]')?.getAttribute('aria-expanded')==='false');assert.ok(await opener.evaluate(el=>el===document.activeElement));
 await open();await nav.locator('nav a').last().focus();await page.keyboard.press('Tab');await page.waitForFunction(()=>document.querySelector('.topbar button[aria-controls="study-navigation"]')?.getAttribute('aria-expanded')==='false');assert.equal(await nav.evaluate(el=>el.contains(document.activeElement)),false);
 await open();await nav.locator('a[href^="#integration?"]').click();await route('integration');await page.waitForFunction(()=>document.querySelector('main h1')===document.activeElement);assert.equal(await opener.getAttribute('aria-expanded'),'false');
 await open();await page.setViewportSize({width:1440,height:1000});await page.waitForFunction(()=>{const el=document.activeElement;if(!el||el===document.body)return false;const style=getComputedStyle(el),box=el.getBoundingClientRect();return style.visibility!=='hidden'&&style.display!=='none'&&box.width>0&&box.height>0;});
 await nav.locator('a[aria-current="page"]').focus();await page.setViewportSize({width:390,height:844});await page.waitForFunction(()=>document.activeElement===document.querySelector('.topbar button[aria-controls="study-navigation"]'));await page.setViewportSize({width:1440,height:1000});
 report.accessibility={mobileMenuFocus:true,escapeRestoresFocus:true,leavingClosesMenu:true,pageHeadingFocus:true,resizeKeepsFocusVisible:true,reverseResizeRestoresFocus:true};
}
async function checkFrameworkJourney(data){
 const combinations=[];
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:1000});await route('vision');
  assert.deepEqual(await page.locator('.vision-decision-links a').evaluateAll(els=>els.map(el=>el.getAttribute('href'))),['#comparer','#modele','#conditions-realisation']);
  assert.equal(await page.locator('.vision-readiness-links a').count(),4);
  if(width===390){assert.equal(await page.locator('.vision-phase-mobile>article:visible').count(),3);assert.equal(await page.locator('.vision-phase-desktop:visible').count(),0);}
  for(const phase of ['acquisition','integration','fonctionnement'])for(const option of ['java-spring','microsoft','sap']){
   await route(phase+'?option='+option+'&horizon=5');
   assert.equal(await page.locator('.journey-treatment section').count(),2);assert.equal(await page.locator('.journey-example').count(),1);
   assert.equal(await page.locator('.journey-option-navigation a[aria-current="page"]').getAttribute('href'),'#'+phase+'?option='+option+'&horizon=5&origin=project&options=java-spring%2Cmicrosoft%2Csap');
   assert.equal(await page.locator('.journey-reading-shortcuts a').count(),option==='java-spring'?3:2);
   assert.equal(await page.locator('.journey-reading-shortcuts a').first().getAttribute('href'),'#charges-'+phase+'?option='+option+'&horizon=5&origin=project&options=java-spring%2Cmicrosoft%2Csap');
   if(option==='java-spring'){
    assert.ok(await page.locator('.make-audit-steps>li').count()>1);
    for(const element of await page.locator('.make-rule').all()){
     const ref=await element.getAttribute('data-rule-ref'),rule=data.ui.essential.estimation_model.rules.find(item=>item.id===ref);assert.ok(rule);assert.equal(await element.locator('.make-formula code').textContent(),rule.expression);assert.equal(await element.locator('.make-rule-unit').textContent(),rule.unit);
    }
    await page.locator('.journey-reading-shortcuts a').last().click();await page.waitForFunction(()=>document.activeElement?.id.endsWith('-method'));
    await page.locator('.journey-detailed-method>a').click();await page.waitForFunction(()=>document.activeElement?.id.endsWith('-summary'));
   }else assert.equal(await page.locator('.make-audit').count(),0);
   assert.ok(await page.locator('.journey-limits li').count()>0);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));combinations.push({width,phase,option});
  }
  await route('charges-fonctionnement?option=microsoft&horizon=3');await page.locator('a.framework-phase-next').click();await page.waitForURL(/#evaluation-core\?option=microsoft&horizon=3(?:&origin=project&options=java-spring%2Cmicrosoft%2Csap)?$/);
  await page.locator('.eco-options a[aria-current="true"]').waitFor();assert.match(await page.locator('.eco-options a[aria-current="true"]').innerText(),/Microsoft/);
  await route('scenarios?option=sap&horizon=7');assert.equal(await page.locator('.journey-scenario-steps>li').count(),4);assert.equal(await page.locator('a.framework-primary-link').getAttribute('href'),'#comparer?option=sap&horizon=7&origin=project&options=java-spring%2Cmicrosoft%2Csap');
  await route('methodes');assert.equal(await page.locator('.journey-methods article').count(),7);await page.locator('.journey-methods a[href="#modele"]').click();await page.locator('.model-reading').waitFor();await page.locator('a.journey-method-back').click();await page.locator('.journey-methods').waitFor();
 }
 report.frameworkJourney={combinations,optionAndHorizonPreserved:true,methodAnchors:true,legacyMethodsReachable:true};
}
async function workerRequest(manifest,manifestUrl,requestPath,body){
 const id=++sequence;
 return (workerPage||page).evaluate(({id,manifest,manifestUrl,requestPath,body})=>new Promise((resolve,reject)=>{
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
 await page.goto(site.href);await page.locator('.app-shell').waitFor();
 const manifestUrl=await page.evaluate(()=>new URL(JSON.parse(document.getElementById('app-config').textContent).static_site.manifest,document.baseURI).href);
 const manifestResponse=await page.request.get(manifestUrl);assert.ok(manifestResponse.ok());const manifest=await manifestResponse.json();
 assert.equal(manifest.simulation_contract,oracle.contract);
 const bootstrapUrl=new URL(manifest.bootstrap,manifestUrl).href,bootstrapResponse=await page.request.get(bootstrapUrl);assert.ok(bootstrapResponse.ok());const data=await bootstrapResponse.json();
 equalProjection(data.baseline,oracle.cases.reference.result,'Static reference differs from Python');assert.deepEqual(data.ui.essential.nav.map(row=>row.id).sort(),[...navRoutes].sort());
 assert.deepEqual(data.ui.essential.active_options,['java-spring','microsoft','sap']);assert.equal(data.baseline.options.length,5,'Historical options remain in the engine');
 await page.waitForFunction(()=>location.hash==='#vision');assert.equal(await page.locator('.brand-home').getAttribute('href'),'#vision');
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:width===390?844:1000});report.routes[width]=[];
  for(const id of routes){
   await route(id);const state=await page.locator('main .essential-page:visible').first().evaluate(el=>({text:el.innerText,overflow:document.documentElement.scrollWidth-innerWidth}));
   assert.ok(state.text.length>40,'Empty route: '+id);assert.doesNotMatch(state.text,/\{\{(?:notion|vue)\.|\bundefined\b|\bNaN\b/,'Unresolved content: '+id);assert.ok(state.overflow<=1,'Overflow: '+width+'/'+id);
   assert.equal(await page.locator('main a[href]').evaluateAll((links,allowed)=>links.filter(link=>/\.ya?ml(?:[?#]|$)/i.test(decodeURIComponent(link.getAttribute('href')||''))&&link.getAttribute('href')!==allowed).length,site.pathname+'exports/flow-modele-metier.yaml'),0,'Exposed model source: '+id);
   if(['vision','acquisition','integration','fonctionnement','scenarios','methodes','modele','conditions-realisation','complexite','calcul-net','calcul-run','leviers'].includes(id))assert.equal(await page.locator('main details:not(.download-details):visible').count(),0,'Method disclosure: '+id);
   if(id==='parametres')assert.equal(await page.locator('main input,main select,main textarea').count(),0,'Fixed assumptions must be read only');
   if(id==='comparer')assert.equal(await page.locator('.eco-option-card').count(),3);
   if(id==='telechargements'){assert.equal(await page.locator('.download-card').count(),data.content.downloads.originals.length+data.content.downloads.documents.length);assert.equal(await page.locator('.download-personal button').count(),1);}
   report.routes[width].push(id);
  }
 }
 for(const [base,key] of [['modele','model'],['capacite-realisation','delivery'],['preetude-projets','prestudy_projects'],['preetude-solutions','prestudy_solutions']])for(const [index,entry] of data.ui.essential.dossiers[key].pages.entries()){
  await route(base+(index?'?view='+entry.id:''));assert.ok(await page.locator('.dossier-sheet').first().isVisible());assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
 }
 await checkFrameworkNavigation();await page.setViewportSize({width:1440,height:1000});
 const assets=await page.locator('img').evaluateAll(els=>els.map(el=>({src:el.src,loaded:el.complete&&el.naturalWidth>0})));assert.ok(assets.length);for(const asset of assets){assert.ok(asset.loaded);assert.ok(new URL(asset.src).pathname.startsWith(site.pathname));}report.assets=assets.length;
 await route('charges-acquisition?option=java-spring');const grossResponse=await page.request.get(new URL(manifest.routes['/api/gross-evaluations'],manifestUrl).href);assert.ok(grossResponse.ok());const gross=await grossResponse.json();
 const core=gross.phases.acquisition.options['java-spring'].core;assert.equal(core.adopted_jh,data.baseline.options.find(o=>o.stack==='java-spring').obtention?.total_jh??data.content.core_product_scope.proposal.adopted_jh);
 assert.equal(await page.locator('.gross-adopted-lots tbody tr').count(),core.rows.length);assert.equal(await page.locator('.gross-completeness').getAttribute('data-core-status'),core.status);assert.ok((await page.locator('#gross-focus-proposal').innerText()).includes(gross.labels.adoption_note.replaceAll('**','')));assert.equal(await page.locator('.gross-proposal').count(),0);
 for(const row of core.rows){await route('charges-acquisition?option=java-spring&focus='+encodeURIComponent(row.id));assert.equal(await page.locator('#gross-focus-'+row.id).getAttribute('open'),'');assert.ok((await page.locator('#gross-focus-'+row.id).innerText()).length>80);}
 report.proofs.phaseCharges={adopted_jh:core.adopted_jh,units:core.rows.length,adoptionStatus:core.status};
 await route('evaluation-core?option=java-spring&horizon=10');assert.equal(await page.locator('.eco-cost-overview>article').count(),3);assert.equal(await page.locator('.eco-year-chart li').count(),10);
 await route('parametres');assert.equal(await page.locator('.eco-determinants article').count(),4);report.proofs.fixedEconomicDossier=true;
 await route('modele');const modelDownload=page.locator('.model-download a[download]'),downloadHref=await modelDownload.getAttribute('href');assert.equal(new URL(downloadHref,site).pathname,site.pathname+'exports/flow-modele-metier.yaml');
 const downloadResponse=await context.request.get(new URL(downloadHref,site).href);assert.ok(downloadResponse.ok());const downloadBytes=await downloadResponse.body(),metadataResponse=await context.request.get(new URL(data.content.downloads.model_package.metadata_asset,site).href);assert.ok(metadataResponse.ok());const metadata=await metadataResponse.json();
 assert.equal(metadata.bytes,downloadBytes.length);assert.equal(metadata.sha256,createHash('sha256').update(downloadBytes).digest('hex'));assert.deepEqual(metadata.model_revision,data.model_revision);assert.match(metadata.source_fingerprint,/^[a-f0-9]{64}$/);
 for(const pattern of [/^format: flow-business-model/m,/^format_version: 2/m,/^metamodel:/m,/^model:/m,/^evidence:/m,/source\/calculs-estimation-core\.yaml/])assert.match(downloadBytes.toString('utf8'),pattern);
 const downloadEvent=page.waitForEvent('download');await modelDownload.click();const downloaded=await downloadEvent;assert.equal(downloaded.suggestedFilename(),'flow-modele-metier.yaml');assert.equal(await downloaded.failure(),null);assert.equal(createHash('sha256').update(await fs.readFile(await downloaded.path())).digest('hex'),metadata.sha256);report.proofs.businessModelDownload={bytes:metadata.bytes,sha256:metadata.sha256,singleFile:true};
 await route('glossaire');assert.equal(await page.locator('.glossary-entry').count(),Object.keys(data.glossary.notions).length);await page.locator('#glossary-search').fill('JH');assert.ok(await page.locator('.glossary-entry').count()>0);assert.ok(await page.locator('.glossary-entry').count()<Object.keys(data.glossary.notions).length);await page.locator('#glossary-search').fill('');
 await page.evaluate(()=>{location.hash='#glossaire?term=cocomo_ii';});await page.waitForFunction(()=>document.activeElement?.id==='glossary-term-cocomo_ii');
 await route('calcul-run');const glossaryLink=page.locator('.method-glossary-link').first(),glossaryTarget=await glossaryLink.getAttribute('href');await glossaryLink.click();await page.waitForFunction(target=>location.hash===target&&document.activeElement?.id==='glossary-term-'+new URLSearchParams(target.split('?')[1]).get('term'),glossaryTarget);report.proofs.glossary={canonicalEntries:Object.keys(data.glossary.notions).length,search:true,directTerm:true,methodLink:true};
 await route('vision');assert.equal(await page.locator('.vision-matrix tbody tr').count(),3);assert.equal(await page.locator('.vision-matrix tbody td').count(),6);assert.deepEqual(await page.locator('.vision-evidence a').evaluateAll(els=>els.map(el=>el.getAttribute('href'))),data.ui.essential.framework_vision.evidence.items.map(row=>row.href));
 await route('capacite-realisation');const delivery=data.content.delivery_readiness;assert.equal(await page.locator('.delivery-review-date time').getAttribute('datetime'),delivery.date);await page.locator('[data-proof-ref]').first().click();await page.waitForFunction(()=>document.activeElement?.id.startsWith('delivery-readiness-proof-'));assert.equal(await page.locator('[data-delivery-proof]').count(),delivery.proofs.length);
 await route('capacite-realisation?view=hotspots');assert.equal(await page.locator('[data-hotspot]').count(),delivery.hotspots.length);await route('capacite-realisation?view=gates');assert.equal(await page.locator('[data-delivery-gate]').count(),delivery.gates.length);
 await route('cartographie');const scope=delivery.scope;assert.equal(await page.locator('.cartography-page .model-map a').getAttribute('href'),scope.link.href);assert.ok((await page.locator('.cartography-page').innerText()).includes(scope.source.version));
 await page.locator('main a[href="#modele?section=scope"]').click();await page.waitForFunction(()=>document.activeElement?.id==='model-chapter-scope');assert.equal(await page.locator('.model-map-systems').count(),1);assert.equal(await page.locator('.model-scope-areas').count(),0);
 await page.goto(new URL('#perimetre-retenu',site).href);await page.waitForFunction(()=>location.hash==='#cartographie');await page.locator('.cartography-page').waitFor();assert.equal(await page.locator('.model-scope-areas li').count(),scope.hierarchy.flatMap(domain=>domain.subdomains.flatMap(sub=>sub.areas)).length);assert.equal(await page.locator('.cartography-provenance time').getAttribute('datetime'),scope.source.date);report.proofs.sponsorJourney={visionLanding:true,realizationCriteria:true,readinessDossier:true,nativeCartography:true};
 await route('synvance');for(const provider of synvanceProviders){await page.locator(`main a[href="#synvance-${provider}"]`).first().click();await route('synvance-'+provider);assert.equal(await page.locator('.synvance-provider').count(),1);assert.equal(await page.locator(`.synvance-provider[data-provider="${provider}"]`).count(),1);assert.equal(await page.locator('.synvance-document').count(),0);await page.locator('main a[href="#synvance"]').first().click();await route('synvance');}
 const documents=data.content.synvance_reference.documents.items;assert.equal(documents.filter(row=>row.format==='pdf').length,5);assert.equal(documents.filter(row=>row.format==='xlsx').length,2);assert.equal(await page.locator('.synvance-document').count(),documents.length);
 for(let index=0;index<documents.length;index++){const doc=documents[index],link=page.locator('.synvance-document').nth(index).locator('a[download]'),url=new URL(await link.getAttribute('href'),page.url()).href;assert.ok(new URL(url).pathname.startsWith(site.pathname));const response=await page.request.get(url);assert.ok(response.ok());const bytes=await response.body();assert.equal(createHash('sha256').update(bytes).digest('hex'),manifest.documents[doc.path.split('#')[0]].sha256);if(doc.format==='pdf')assert.equal(bytes.subarray(0,5).toString(),'%PDF-');}
 const downloadPromise=page.waitForEvent('download');await page.locator('.synvance-document a[download]').first().click();const originalDownload=await downloadPromise;assert.ok(originalDownload.suggestedFilename().endsWith('.pdf'));assert.equal(await originalDownload.failure(),null);report.proofs.originalDocuments=documents.length;report.proofs.pdfDownload=true;
 // Preserve and export legacy personal data through the current read-only interface.
 const personal=oracle.cases[oracle.ui_case||Object.keys(oracle.cases).find(name=>name!=='reference')];
 const saved=JSON.stringify([{id:'validation-pages',name:'Validation Pages',parameters:personal.parameters,model_version:data.model_version,contract:oracle.contract,horizon:10,chosen:'microsoft'}]);
 const session=JSON.stringify({format:1,contract:oracle.contract,model_version:data.model_version,parameters:personal.parameters,overrides:{common:{},options:{}},horizon:10,chosen:'microsoft',name:'Validation Pages'});
 await page.evaluate(({saved,session,keys})=>{localStorage.setItem(keys.saved,saved);sessionStorage.setItem(keys.session,session);},{saved,session,keys:{saved:data.ui.storage_key,session:data.ui.reload_storage_key}});
 await route('simuler');assert.match(page.url(),/#comparer/);assert.equal(await page.locator('main input,main select,main textarea').count(),0);await page.reload();await page.locator('.eco-option-card').first().waitFor();
 assert.equal(await page.evaluate(key=>localStorage.getItem(key),data.ui.storage_key),saved);assert.equal(await page.evaluate(key=>sessionStorage.getItem(key),data.ui.reload_storage_key),session);
 await route('telechargements');const archiveEvent=page.waitForEvent('download');await page.locator('.download-personal button').click();const archive=await archiveEvent;assert.equal(await archive.failure(),null);assert.equal(await fs.readFile(await archive.path(),'utf8'),saved);report.storage={legacyCollectionPreserved:true,sessionPreserved:true,archiveExportExact:true,retiredEditorRedirect:true};
 // A fixture exposes real published and unavailable Markdown through an existing source control.
 const reader=await context.newPage();watch(reader);const readerData=structuredClone(data),proof=readerData.content.delivery_readiness.proofs.find(row=>row.href);
 proof.href='source/README.md';await reader.route(bootstrapUrl,request=>request.fulfill({json:readerData}));await reader.goto(site.href+'#capacite-realisation?view=proofs');const sourceButton=reader.locator('[data-delivery-proof="'+proof.id+'"]').getByRole('button',{name:delivery.labels.proof_access,exact:true});await sourceButton.click();await reader.locator('dialog[open] .markdown').waitFor({timeout:180000});assert.ok((await reader.locator('dialog[open] .markdown').innerText()).length>100);await reader.getByRole('dialog',{name:data.ui.documents.find(row=>row.path==='source/README.md').title,exact:true}).waitFor();report.accessibility.documentDialogNamed=true;
 await reader.locator('dialog[open] header > button.icon-button').focus();await reader.keyboard.press('Escape');await reader.locator('dialog[open]').waitFor({state:'detached'});assert.ok(await sourceButton.evaluate(el=>el===document.activeElement));
 proof.href='source/__pages_missing_proof__.md';await reader.reload();await reader.locator('[data-delivery-proof="'+proof.id+'"]').getByRole('button',{name:delivery.labels.proof_access,exact:true}).click();await reader.locator('dialog[open] .notice').filter({hasText:data.ui.errors.missing_document}).waitFor({timeout:180000});assert.equal(await reader.locator('.app-shell').count(),1);assert.equal(await reader.locator('dialog[open] .document-meta a').count(),0,'Unavailable proof must not offer a broken download');workerPage=reader;
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


 await reader.close();workerPage=undefined;report.proofs.markdown=true;report.proofs.focus=true;report.proofs.unpublishedDocumentHandled=true;
 await checkFrameworkJourney(data);assert.deepEqual(report.errors,[]);assert.deepEqual(httpApiRequests,[]);report.httpApiRequests=httpApiRequests;report.status='passed';
}catch(error){report.status='failed';report.failure=error.stack||String(error);process.exitCode=1;if(page)await page.screenshot({path:output+'.png',fullPage:true}).catch(()=>{});}
finally{report.seconds=Math.round(performance.now()-started)/1000;await fs.writeFile(output,JSON.stringify(report,null,2));await browser.close();console.log(JSON.stringify({status:report.status,output,worker:report.worker,storage:report.storage,proofs:report.proofs,errors:report.errors,failure:report.failure,seconds:report.seconds},null,2));}
