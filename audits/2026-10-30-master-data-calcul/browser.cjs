const fs=require('fs'),path=require('path'),{pathToFileURL,fileURLToPath}=require('url');
const {chromium}=require('C:/Users/laure/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
const dir=__dirname,checks=[],errors=[];
const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
for(const vp of [{name:'desktop',width:1440,height:1080},{name:'mobile',width:390,height:844}]){
const page=await browser.newPage({viewport:{width:vp.width,height:vp.height},deviceScaleFactor:1});
page.on('pageerror',e=>errors.push(e.message));
const url=pathToFileURL(path.join(dir,'index.html')).href;await page.goto(url);
const r=await page.evaluate(()=>{const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);return {overflow:document.documentElement.scrollWidth>innerWidth,duplicates:ids.filter((v,i)=>ids.indexOf(v)!==i),links:[...document.querySelectorAll('a[href]')].map(e=>e.getAttribute('href')),emptyLinks:[...document.querySelectorAll('a')].filter(e=>!e.textContent.trim()).length};});
if(r.overflow||r.duplicates.length||r.emptyLinks)throw Error(JSON.stringify(r));
for(const href of r.links){if(/^https?:/.test(href))continue;const t=new URL(href,url);if(!fs.existsSync(fileURLToPath(t)))throw Error('Missing '+href);if(t.hash&&t.pathname===new URL(url).pathname&&!await page.locator('[id="'+decodeURIComponent(t.hash.slice(1))+'"]').count())throw Error('Missing anchor '+href);}
await page.screenshot({path:path.join(dir,'bilan-'+vp.name+'.png')});
for(const id of ['repartitions','isbsg','cocomo'])if(vp.name==='desktop')await page.locator('#'+id).screenshot({path:path.join(dir,id+'-desktop.png')});
checks.push({viewport:vp.name,links:r.links.length,overflow:false,duplicateIds:0,emptyLinks:0});
await page.close();}
await browser.close();if(errors.length)throw Error(errors.join('\n'));
const R=JSON.parse(fs.readFileSync(path.join(dir,'resultats.json'),'utf8')),D=JSON.parse(fs.readFileSync(path.join(dir,'repartition-calculee.json'),'utf8'));
const E=.91+.01*18.97,pm=2.94*Math.pow(11.326,E),jh=pm*152/7,months=3.67*Math.pow(pm,.28+.2*(E-.91));
const expected=[.24*12+.76*10,.24*8+.76*5,.24*18+.76*8,.24*36+.76*16,.24*13+.76*34,.24*10+.76*24,.24*3+.76*3];
const close=(a,b)=>{if(Math.abs(a-b)>1e-8)throw Error('Arithmetic mismatch '+a+' / '+b);};
close(jh,D.base_jh);D.rows.forEach((row,i)=>{close(row.fraction*100,expected[i]);close(row.effort_jh,jh*expected[i]/100);});close(expected.reduce((a,b)=>a+b,0),100);
close(350*20*.8/7,R.isbsg.main.effort_jh[1]);close(350*13*.8/7,R.isbsg.main.effort_jh[0]);close(350*27*.8/7,R.isbsg.main.effort_jh[2]);
fs.writeFileSync(path.join(dir,'independent-arithmetic.json'),JSON.stringify({status:'passed',implementation:'Independent JavaScript expressions from published constants',cocomo:{E,pm,jh,months},activity_percent:expected,activity_total_jh:D.rows.reduce((a,b)=>a+b.effort_jh,0),isbsg:{low_jh:520,central_jh:800,high_jh:1080},isbsg_published_activity_sum:9+16+54+20},null,2));
fs.writeFileSync(path.join(dir,'browser-check.json'),JSON.stringify({status:'passed',checks,page_errors:errors,visual_review:'Screenshots generated; manual visual inspection separately'},null,2));console.log(JSON.stringify({status:'passed',checks,independent_arithmetic:'passed'}));
})().catch(e=>{console.error(e);process.exit(1)});