import {useEffect,useRef,useState} from 'react';
import {request} from './transport';
import {INITIAL_SERVER_STATUS,monitorServer,type ServerStatus} from './serverConnection';

export function useServerUpdate(revision:string|undefined,appId:string|undefined){
 const [status,setStatus]=useState<ServerStatus>(INITIAL_SERVER_STATUS);
 const active=useRef<ReturnType<typeof monitorServer>|null>(null);
 useEffect(()=>{
  setStatus(INITIAL_SERVER_STATUS);
  if(!revision||!appId)return;
  const monitor=monitorServer({revision,appId,window,document,onChange:setStatus,
   readHealth:signal=>request('/api/health',undefined,{signal}),
  });
  active.current=monitor;
  return()=>{monitor.stop();active.current=null;};
 },[revision,appId]);
 return {...status,recheck:()=>{void active.current?.check();}};
}
