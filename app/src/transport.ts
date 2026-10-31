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
 throw Object.assign(new Error('network'),{code:'network'});
}

export function fileHref(reference:string){
 const client=pagesClient();if(client)return client.fileHref(reference);
 throw Object.assign(new Error('network'),{code:'network'});
}
