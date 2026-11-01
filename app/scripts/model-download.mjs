import {execFileSync} from 'node:child_process';
import {existsSync,readFileSync} from 'node:fs';
import {homedir} from 'node:os';
import {delimiter,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root=fileURLToPath(new URL('../../',import.meta.url));
const asset='exports/flow-modele-metier.yaml';
const output=resolve(root,'tmp/model-download/flow-modele-metier.yaml');
function compose(){
 const candidates=[process.env.FLOW_PYTHON,process.env.PYTHON,
  resolve(root,process.platform==='win32'?'.venv/Scripts/python.exe':'.venv/bin/python'),
  resolve(homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/python',process.platform==='win32'?'python.exe':'bin/python3')];
 const python=candidates.find(p=>p&&existsSync(p))||'python';
 const deps=resolve(root,'tmp/model-deps');
 const env={...process.env,PYTHONPATH:[existsSync(deps)?deps:'',resolve(root,'tools'),process.env.PYTHONPATH||''].filter(Boolean).join(delimiter)};
 execFileSync(python,['-B','-m','tools.export_business_model'],{cwd:root,env,stdio:'inherit'});
 const record=JSON.parse(readFileSync(output+'.cache.json','utf8'));
 const metadata=Object.fromEntries(['sha256','bytes','sources','source_fingerprint','model_revision'].map(key=>[key,record[key]]));
 return {raw:readFileSync(output),metadata:JSON.stringify({...metadata,format_version:2,asset})};
}
export function modelDownload(){
 let building=false;
 return {name:'business-model-download',
  configResolved(config){building=config.command==='build';},
  buildStart(){if(!building)return;const result=compose();this.emitFile({type:'asset',fileName:asset,source:result.raw});this.emitFile({type:'asset',fileName:asset.replace('.yaml','.json'),source:result.metadata});},
  configureServer(server){
   // Compose on demand in Vite development, too. Errors must not serve an old file.
   server.middlewares.use((req,res,next)=>{
    const path=(req.url||'').split('?')[0],metadata=path===server.config.base+asset.replace('.yaml','.json');
    if(path!==server.config.base+asset&&!metadata)return next();
    try{const result=compose();res.setHeader('Content-Type',metadata?'application/json':'application/yaml; charset=utf-8');if(!metadata)res.setHeader('Content-Disposition','attachment; filename="flow-modele-metier.yaml"');res.setHeader('Cache-Control','no-store');res.end(metadata?result.metadata:result.raw);}
    catch(error){next(error);}
   });
  }
 };
}
