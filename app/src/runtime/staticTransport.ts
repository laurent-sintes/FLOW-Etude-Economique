export type StaticManifest={format:1;id:string;model_version:string;simulation_contract:string;server_revision:string;base:string;bootstrap:string;routes:Record<string,string>;documents:Record<string,{url:string;sha256:string}>;python:{archive:string;archive_sha256:string;model:string;model_sha256:string;pyodide:string}};
export type RuntimeReply={status:number;data:Record<string,unknown>};
export type RuntimeJob={id:number;manifest:StaticManifest;manifestUrl:string;path:string;body:string};
export type RuntimeWorker={postMessage:(message:RuntimeJob)=>void;terminate:()=>void;onmessage:((event:MessageEvent<{id:number;reply?:RuntimeReply;error?:{code:string;field?:string}}>)=>void)|null;onerror:((event:Event)=>void)|null};
type Dependencies={manifestUrl:string;fetch:typeof fetch;createWorker:()=>RuntimeWorker};

export function transportError(code:string,field?:string){return Object.assign(new Error(code),{code,field});}

export function siteAssetUrl(reference:string,manifestUrl:string){
 const root=new URL('./',manifestUrl),value=new URL(reference,root);
 if(value.origin!==root.origin||!value.pathname.startsWith(root.pathname))throw transportError('missing_document');
 return value.href;
}

function assertManifest(value:StaticManifest){
 if(value?.format!==1||value.id!=='flow-study'||!value.model_version||!value.simulation_contract||!value.server_revision||!value.bootstrap||!value.routes||!value.documents||!value.python)throw transportError('network');
 return value;
}

export function createStaticTransport(dependencies:Dependencies){
 const manifestUrl=new URL(dependencies.manifestUrl).href;
 let manifest:StaticManifest|undefined,loading:Promise<StaticManifest>|undefined,worker:RuntimeWorker|undefined,sequence=0;
 const resources=new Map<string,Promise<unknown>>();
 const jobs=new Map<number,{resolve:(value:unknown)=>void;reject:(error:unknown)=>void}>();
 const readJson=async(url:string,init?:RequestInit)=>{
  const response=await dependencies.fetch(url,init);
  if(!response.ok)throw transportError('network');
  return response.json();
 };
 const loadManifest=()=>loading??=(readJson(manifestUrl).then(assertManifest).then(value=>manifest=value).catch(error=>{loading=undefined;throw error;}));
 const readResource=async(reference:string)=>{
  const url=siteAssetUrl(reference,manifestUrl);
  if(!resources.has(url))resources.set(url,readJson(url).catch(error=>{resources.delete(url);throw error;}));
  return structuredClone(await resources.get(url));
 };
 const stopWorker=(error:unknown)=>{
  worker?.terminate();worker=undefined;
  for(const job of jobs.values())job.reject(error);
  jobs.clear();
 };
 const invoke=(snapshot:StaticManifest,path:string,body:unknown)=>new Promise<unknown>((resolve,reject)=>{
  if(!worker){
   worker=dependencies.createWorker();
   worker.onmessage=({data})=>{
    const job=jobs.get(data.id);if(!job)return;
    jobs.delete(data.id);
    if(data.error){job.reject(transportError(data.error.code,data.error.field));return;}
    const reply=data.reply;
    if(!reply){job.reject(transportError('network'));return;}
    if(reply.status>=400)job.reject(transportError(String(reply.data.error||'network'),typeof reply.data.field==='string'?reply.data.field:undefined));
    else job.resolve(reply.data);
   };
   worker.onerror=()=>stopWorker(transportError('network'));
  }
  const id=++sequence;
  jobs.set(id,{resolve,reject});
  worker.postMessage({id,manifest:snapshot,manifestUrl,path,body:body===undefined?'':JSON.stringify(body)});
 });
 return {
  async request<T>(path:string,body?:unknown,options?:{signal?:AbortSignal}):Promise<T>{
   const url=new URL(path,'http://reference');
   if(url.origin!=='http://reference')throw transportError('missing_document');
   if(url.pathname==='/api/health'){
    const latest=assertManifest(await readJson(manifestUrl,{cache:'no-store',signal:options?.signal}));
    return {id:latest.id,version:latest.model_version,server_revision:latest.server_revision,mode:'current',sources_current:true} as T;
   }
   const snapshot=await loadManifest();
   if(['/api/capability','/api/market-build','/api/market-references','/api/economic-evaluations'].includes(url.pathname)&&url.searchParams.get('model_version')!==snapshot.model_version)throw transportError('version');
   if(url.pathname==='/api/simulate'||url.pathname==='/api/document')return invoke(snapshot,path,body) as Promise<T>;
   if(body!==undefined)throw transportError('invalid');
   if(url.pathname==='/api/bootstrap'){
    const value=await readResource(snapshot.bootstrap) as {model_version:string;simulation_contract:string;server_revision:string};
    if(value.model_version!==snapshot.model_version||value.simulation_contract!==snapshot.simulation_contract||value.server_revision!==snapshot.server_revision)throw transportError('version');
    return value as T;
   }
   const reference=snapshot.routes[url.pathname];
   if(!reference)throw transportError('missing_document');
   const value=await readResource(reference);
   if(url.pathname==='/api/capability'){
    const proof=(value as Record<string,unknown>)[url.searchParams.get('id')||''];
    if(!proof)throw transportError('missing_document');
    return proof as T;
   }
   return value as T;
  },
  fileHref(reference:string){
   const [path,...fragments]=reference.split('#'),entry=manifest?.documents[path];
   if(!entry)return undefined;
   const url=new URL(siteAssetUrl(entry.url,manifestUrl));
   url.hash=fragments.join('#');
   return url.href;
  },
  dispose(){stopWorker(transportError('network'));resources.clear();},
 };
}
