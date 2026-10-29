/* Audit rendering verification only. */
const fs = require("fs");
const path = require("path");
const {pathToFileURL,fileURLToPath} = require("url");
const {chromium} = require("C:/Users/laure/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");
const base=__dirname;
(async()=>{
 const browser=await chromium.launch({executablePath:"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",headless:true});
 const checks=[];
 const screenshots=[];
 try{
  for(const [name,viewport] of [["desktop",{width:1440,height:1080}],["mobile",{width:390,height:844}]]){
   const page=await browser.newPage({viewport,deviceScaleFactor:1});
   const errors=[];page.on("pageerror",e=>errors.push(String(e)));
   await page.goto(pathToFileURL(path.join(base,"iteration-11.html")).href,{waitUntil:"load"});
   const state=await page.evaluate(()=>{
    const ids=Array.from(document.querySelectorAll("[id]"),e=>e.id);
    return {title:document.title,documentWidth:document.documentElement.scrollWidth,viewportWidth:innerWidth,
     duplicateIds:ids.filter((id,i)=>ids.indexOf(id)!==i),
     anchorFailures:Array.from(document.querySelectorAll('a[href^="#"]'),a=>a.getAttribute("href")).filter(h=>h.length>1&&!document.getElementById(h.slice(1))),
     links:Array.from(document.querySelectorAll("a[href]"),a=>a.href),
     accordions:document.querySelectorAll("details").length,
     tableCount:document.querySelectorAll("table").length,
     text:document.body.innerText};
   });
   const localMissing=state.links.filter(h=>h.startsWith("file:")).filter(h=>{
    const u=new URL(h);u.hash="";return !fs.existsSync(fileURLToPath(u));
   });
   const yamlLinks=state.links.filter(h=>/\.ya?ml(?:#|$)/i.test(h));
   if(state.documentWidth>state.viewportWidth||state.duplicateIds.length||state.anchorFailures.length||localMissing.length||errors.length||yamlLinks.length||state.accordions)throw Error(JSON.stringify({name,state:{...state,text:undefined,links:undefined},localMissing,errors,yamlLinks}));
   const file="iteration-11-"+name+".png";
   await page.screenshot({path:path.join(base,file)});screenshots.push(file);
   if(name==="desktop"){
    await page.evaluate(()=>{document.documentElement.style.scrollBehavior="auto";const e=document.querySelector("#roles");if(!e)throw Error("Missing roles section");window.scrollTo(0,e.getBoundingClientRect().top+scrollY)});
    await page.screenshot({path:path.join(base,"iteration-11-roles.png")});screenshots.push("iteration-11-roles.png");
   }
   checks.push({name,viewport,documentWidth:state.documentWidth,title:state.title,tableCount:state.tableCount,
    duplicateIds:state.duplicateIds,anchorFailures:state.anchorFailures,localMissing,pageErrors:errors,yamlLinks,accordions:state.accordions,passed:true});
   await page.close();
  }
 }finally{await browser.close()}
 const result={id:"iteration-11-browser-check",checks,screenshots,visual_review:"Required separately; automated checks do not establish visual quality."};
 fs.writeFileSync(path.join(base,"iteration-11-browser-check.json"),JSON.stringify(result,null,2)+"\n");
 process.stdout.write(JSON.stringify({checks,screenshots})+"\n");
})().catch(e=>{process.stderr.write(String(e)+"\n");process.exitCode=1});
