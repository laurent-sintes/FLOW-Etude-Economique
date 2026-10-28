import {siteAssetUrl,transportError,type RuntimeJob,type RuntimeReply} from './staticTransport';

type PythonRuntime={globals:{set:(name:string,value:unknown)=>void;delete:(name:string)=>void};runPythonAsync:(code:string)=>Promise<unknown>;loadPackage:(names:string[])=>Promise<void>;unpackArchive:(archive:ArrayBuffer,format:string,options:{extractDir:string})=>void};
const scope=globalThis as unknown as {onmessage:((event:MessageEvent<RuntimeJob>)=>void)|null;postMessage:(message:{id:number;reply?:RuntimeReply;error?:{code:string;field?:string}})=>void};
let runtime:Promise<PythonRuntime>|undefined,revision:string|undefined;
let queue=Promise.resolve();

async function checkedBytes(url:string,expected:string){
 const response=await fetch(url);
 if(!response.ok)throw transportError('network');
 const bytes=await response.arrayBuffer();
 const digest=await crypto.subtle.digest('SHA-256',bytes);
 const hash=[...new Uint8Array(digest)].map(value=>value.toString(16).padStart(2,'0')).join('');
 if(hash!==expected)throw transportError('version');
 return bytes;
}

async function initialize(job:RuntimeJob):Promise<PythonRuntime>{
 const {manifest,manifestUrl}=job,python=manifest.python;
 const [engine,compressed,loader]=await Promise.all([
  checkedBytes(siteAssetUrl(python.archive,manifestUrl),python.archive_sha256),
  checkedBytes(siteAssetUrl(python.model,manifestUrl),python.model_sha256),
  import(/* @vite-ignore */ new URL('pyodide.mjs',python.pyodide).href),
 ]);
 const pyodide=await loader.loadPyodide({indexURL:python.pyodide}) as PythonRuntime;
 await pyodide.loadPackage(['pyyaml','jsonschema']);
 pyodide.unpackArchive(engine,'zip',{extractDir:'/flow'});
 const json=await new Response(new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
 pyodide.globals.set('_pages_bundle',json);
 pyodide.globals.set('_pages_version',manifest.model_version);
 pyodide.globals.set('_pages_contract',manifest.simulation_contract);
 await pyodide.runPythonAsync('import sys\nsys.path.insert(0, "/flow/tools")\nfrom pages_runtime import load_runtime\n_pages_runtime = load_runtime(_pages_bundle, _pages_version, _pages_contract)');
 pyodide.globals.delete('_pages_bundle');
 return pyodide;
}

async function run(job:RuntimeJob){
 try{
  if(revision&&revision!==job.manifest.server_revision)throw transportError('version');
  revision=job.manifest.server_revision;
  runtime??=initialize(job).catch(error=>{runtime=undefined;throw error;});
  const python=await runtime;
  python.globals.set('_pages_path',job.path);python.globals.set('_pages_body',job.body);
  const encoded=await python.runPythonAsync('_pages_runtime.request(_pages_path, _pages_body)');
  const reply=JSON.parse(String(encoded)) as RuntimeReply;
  scope.postMessage({id:job.id,reply});
 }catch(error){
  const code=(error as {code?:string}).code||'network';
  scope.postMessage({id:job.id,error:{code}});
 }
}
scope.onmessage=event=>{queue=queue.then(()=>run(event.data));};
