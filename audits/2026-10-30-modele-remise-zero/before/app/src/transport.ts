import {createStaticTransport,type RuntimeWorker} from './runtime/staticTransport';

let staticClient:ReturnType<typeof createStaticTransport>|undefined;
function pagesClient(){
 if(staticClient)return staticClient;
 const element=document.getElementById('app-config');
 if(!element)return undefined;
 const config=JSON.parse(element.textContent||'{}');
 if(!config.static_site?.manifest)return undefined;
 staticClient=createStaticTransport({
  manifestUrl:new URL(config.static_site.manifest,document.baseURI).href,
  fetch:(...args)=>fetch(...args),
  createWorker:()=>new Worker(new URL('./runtime/pages.worker.ts',import.meta.url),{type:'module'}) as unknown as RuntimeWorker,
 });
 return staticClient;
}

export async function request<T>(path:string,body?:unknown,options?:{signal?:AbortSignal}):Promise<T>{
 const client=pagesClient();if(client)return client.request<T>(path,body,options);
 const response=await fetch(path,{...(body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),signal:options?.signal,...(path==='/api/health'?{cache:'no-store' as const}:{})});
 const data=await response.json();
 if(!response.ok)throw Object.assign(new Error(data.error),{code:data.error,field:data.field});
 return data;
}

export function fileHref(reference:string){
 const client=pagesClient();if(client)return client.fileHref(reference);
 const [path,...fragments]=reference.split('#');
 return '/api/file?path='+encodeURIComponent(path)+(fragments.length?'#'+fragments.join('#'):'');
}
