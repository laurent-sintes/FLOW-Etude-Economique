export type ServerStatus={available:boolean;unreachable:boolean;checking:boolean};
type Health={id:string;server_revision:string};
type Host=Pick<Window,'setTimeout'|'clearTimeout'|'setInterval'|'clearInterval'|'addEventListener'|'removeEventListener'>;
type Page=Pick<Document,'hidden'|'addEventListener'|'removeEventListener'>;
export const INITIAL_SERVER_STATUS:ServerStatus={available:false,unreachable:false,checking:false};
export const SERVER_CHECK_INTERVAL=5000;
export const SERVER_CHECK_TIMEOUT=3000;

/** One bounded health request; failures never replace loaded data or reload the page. */
export function monitorServer({revision,appId,readHealth,onChange,window:host,document:page}:{
 revision:string;appId:string;readHealth:(signal:AbortSignal)=>Promise<Health>;
 onChange:(status:ServerStatus)=>void;window:Host;document:Page;
}){
 let stopped=false,pending=false,status=INITIAL_SERVER_STATUS;
 let controller:AbortController|undefined;
 const publish=(change:Partial<ServerStatus>)=>{
  if(stopped)return;
  const next={...status,...change};
  if(next.available===status.available&&next.unreachable===status.unreachable&&next.checking===status.checking)return;
  status=next;onChange(next);
 };
 const check=async(force=false)=>{
  if(stopped||pending||(!force&&page.hidden))return;
  pending=true;
  if(status.unreachable)publish({checking:true});
  const active=new AbortController();controller=active;
  const timeout=host.setTimeout(()=>active.abort(),SERVER_CHECK_TIMEOUT);
  try{
   const current=await readHealth(active.signal);
   if(current?.id!==appId||typeof current.server_revision!=='string'||!current.server_revision)throw Error('ERR_SERVER_HEALTH');
   publish({unreachable:false,checking:false,available:current.server_revision!==revision});
  }catch{
   publish({unreachable:true,checking:false});
  }finally{
   host.clearTimeout(timeout);pending=false;
  }
 };
 const resume=()=>{void check();};
 void check();
 const timer=host.setInterval(resume,SERVER_CHECK_INTERVAL);
 page.addEventListener('visibilitychange',resume);
 host.addEventListener('focus',resume);
 host.addEventListener('online',resume);
 host.addEventListener('offline',resume);
 return {
  check:()=>check(true),
  stop(){
   stopped=true;controller?.abort();host.clearInterval(timer);
   page.removeEventListener('visibilitychange',resume);
   host.removeEventListener('focus',resume);
   host.removeEventListener('online',resume);
   host.removeEventListener('offline',resume);
  },
 };
}
