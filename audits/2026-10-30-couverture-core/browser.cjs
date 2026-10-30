
const fs=require('fs'),path=require('path'),{pathToFileURL,fileURLToPath}=require('url');
const {chromium}=require('C:/Users/laure/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const dir=__dirname,checks=[],errors=[];
 const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
 for(const vp of [{name:'desktop',width:1440,height:1080},{name:'mobile',width:390,height:844}]){
  const page=await browser.newPage({viewport:{width:vp.width,height:vp.height},deviceScaleFactor:1});
  page.on('pageerror',e=>errors.push(e.message));
  for(const name of ['index.html',...Array.from({length:5},(_,i)=>'iteration-'+(i+16)+'.html')]){
   const url=pathToFileURL(path.join(dir,name)).href;await page.goto(url);
   const result=await page.evaluate(()=>{
    const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
    return {title:document.title,overflow:document.documentElement.scrollWidth>innerWidth,
      duplicateIds:ids.filter((v,i)=>ids.indexOf(v)!==i),
      links:[...document.querySelectorAll('a[href]')].map(e=>e.getAttribute('href')),
      emptyLinks:[...document.querySelectorAll('a')].filter(e=>!e.textContent.trim()).length};
   });
   if(result.overflow||result.duplicateIds.length||result.emptyLinks)throw Error(name+' bad layout '+JSON.stringify(result));
   for(const href of result.links){
    if(/^https?:/.test(href))continue;
    const target=new URL(href,url),file=fileURLToPath(target);
    if(!fs.existsSync(file))throw Error('Missing '+file);
    if(target.hash && target.pathname===new URL(url).pathname){
     if(!await page.locator('[id="'+decodeURIComponent(target.hash.slice(1))+'"]').count())throw Error('Missing anchor '+href);
    }
   }
   checks.push({viewport:vp.name,file:name,links:result.links.length,overflow:false,duplicateIds:0});
   if(name==='index.html'){
    await page.screenshot({path:path.join(dir,'bilan-'+vp.name+'.png')});
    await page.locator('#roles').screenshot({path:path.join(dir,'roles-'+vp.name+'.png')});
    if(vp.name==='desktop')await page.locator('#progres').screenshot({path:path.join(dir,'progres-desktop.png')});
   }
   if(name==='iteration-16.html'&&vp.name==='desktop')await page.screenshot({path:path.join(dir,'iteration16-desktop.png')});
  }
  await page.close();
 }
 await browser.close();
 if(errors.length)throw Error(errors.join('\n'));
 fs.writeFileSync(path.join(dir,'browser-check.json'),JSON.stringify({status:'passed',checks,page_errors:errors,visual_review:'Screenshots generated; manual visual inspection separately'},null,2));
 console.log(JSON.stringify({status:'passed',pages:checks.length}));
})().catch(e=>{console.error(e);process.exit(1)});
