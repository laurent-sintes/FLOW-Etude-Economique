import {useEffect,useState} from 'react';
import {request} from './transport';

export function useServerUpdate(revision:string|undefined,appId:string|undefined){
 const [available,setAvailable]=useState(false);
 useEffect(()=>{
  if(!revision||!appId)return;
  let stopped=false,pending=false;
  let controller:AbortController|undefined;
  const check=async()=>{
   if(stopped||pending||document.hidden)return;
   pending=true;controller=new AbortController();
   const timeout=window.setTimeout(()=>controller?.abort(),5000);
   try{
    const current=await request<{id:string;server_revision:string}>('/api/health',undefined,{signal:controller.signal});
    if(!stopped&&current.id===appId&&typeof current.server_revision==='string'&&current.server_revision&&current.server_revision!==revision)setAvailable(true);
   }catch{
    // A server restart or a network interruption must leave the current view intact.
   }finally{clearTimeout(timeout);pending=false;}
  };
  void check();
  const timer=window.setInterval(check,30000);
  document.addEventListener('visibilitychange',check);
  window.addEventListener('focus',check);
  window.addEventListener('online',check);
  return()=>{stopped=true;controller?.abort();clearInterval(timer);document.removeEventListener('visibilitychange',check);window.removeEventListener('focus',check);window.removeEventListener('online',check);};
 },[revision,appId]);
 return available;
}
