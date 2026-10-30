const fs=require('fs'),path=require('path'),{pathToFileURL,fileURLToPath}=require('url');
const {chromium}=require('C:/Users/laure/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const dir=__dirname,checks=[],errors=[],R=JSON.parse(fs.readFileSync(path.join(dir,'resultats.json'),'utf8'));
 const close=(a,b)=>{if(Math.abs(a-b)>1e-8)throw Error('Mismatch '+a+' '+b);};
 const E=.91+.01*18.97;
 for(const p of R.products)for(const v of p.scenarios){
  const size=p.logical_units+v.declaration_weight*p.declarative_units;
  const pm=2.94*Math.pow(size/1000,E),jh=pm*152/7;
  close(v.jh_elaboration_construction,jh);close(v.jh_full_lifecycle_hypothesis,jh*1.18);
  close(v.months_elaboration_construction,3.67*Math.pow(pm,.28+.2*(E-.91)));
 }
 close(R.isbsg_java_witness_jh[1],26*20*1.2/7);
 const a=R.phase_alignment_previous_master_data;close(a.full_lifecycle_cocomo_hypothesis_jh,a.previous_cocomo_ec_jh*1.18);
 close(R.full_lifecycle_activity_allocation.reduce((s,x)=>s+x.jh_previous_scenario_aligned,0),a.full_lifecycle_cocomo_hypothesis_jh);
 if(Object.values(R.retained).some(v=>v!==null))throw Error('An unknown total became a number');
 fs.writeFileSync(path.join(dir,'independent-arithmetic.json'),JSON.stringify({status:'passed',implementation:'Independent JavaScript formulas',native_scenarios_verified:16,common_phase_extension_verified:true,cosmic_java_reference_verified:true,activity_total_conserved:true,unknown_budgets_preserved:true},null,2));
 const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
 for(const vp of [{name:'desktop',width:1440,height:1080},{name:'mobile',width:390,height:844}]){
  const page=await browser.newPage({viewport:{width:vp.width,height:vp.height}});
  page.on('pageerror',e=>errors.push(e.message));const url=pathToFileURL(path.join(dir,'index.html')).href;
  await page.goto(url);const r=await page.evaluate(()=>{const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);return {overflow:document.documentElement.scrollWidth>innerWidth,duplicates:ids.filter((v,i)=>ids.indexOf(v)!==i),links:[...document.querySelectorAll('a[href]')].map(e=>e.getAttribute('href')),empty:[...document.querySelectorAll('a')].filter(e=>!e.textContent.trim()).length};});
  if(r.overflow||r.duplicates.length||r.empty)throw Error(JSON.stringify(r));
  for(const href of r.links){if(/^https?:/.test(href))continue;const t=new URL(href,url);if(!fs.existsSync(fileURLToPath(t)))throw Error('Missing '+href);if(t.hash&&t.pathname===new URL(url).pathname&&!await page.locator('[id="'+decodeURIComponent(t.hash.slice(1))+'"]').count())throw Error('Missing anchor '+href);}
  await page.screenshot({path:path.join(dir,'bilan-'+vp.name+'.png')});
  if(vp.name==='desktop')for(const id of ['cocomo','activites','socle'])await page.locator('#'+id).screenshot({path:path.join(dir,id+'-desktop.png')});
  checks.push({viewport:vp.name,overflow:false,links:r.links.length,duplicate_ids:0});await page.close();
 }
 await browser.close();if(errors.length)throw Error(errors.join('\n'));
 fs.writeFileSync(path.join(dir,'browser-check.json'),JSON.stringify({status:'passed',checks,page_errors:errors},null,2));console.log(JSON.stringify({status:'passed',checks,independent_scenarios:16}));
})().catch(e=>{console.error(e);process.exit(1)});