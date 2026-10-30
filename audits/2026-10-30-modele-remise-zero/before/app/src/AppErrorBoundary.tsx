import {Component,type ReactNode} from 'react';
import type {Data} from './context';

export class AppErrorBoundary extends Component<{initial:Data;children:ReactNode},{failed:boolean}>{
 state={failed:false};
 static getDerivedStateFromError(){return {failed:true};}
 componentDidCatch(error:Error){console.error('ERR_APP_RENDER',error);}
 private restartFresh=()=>{
  const {initial}=this.props,key=initial.reload_storage_key;
  if(key){
   try{
    const raw=sessionStorage.getItem(key);
    if(raw){
     const url=URL.createObjectURL(new Blob([raw],{type:'application/json'}));
     const link=document.createElement('a');link.href=url;link.download=(initial.id||'flow-study')+'-session-recovery.json';link.click();
     setTimeout(()=>URL.revokeObjectURL(url),1000);
    }
    sessionStorage.removeItem(key);
   }catch{/* A blocked storage API must not block recovery. */}
  }
  location.hash='#comparer';
  location.reload();
 };
 render(){
  if(!this.state.failed)return this.props.children;
  const {initial}=this.props;
  return <main className="boot" role="alert"><div className="boot-mark"/><p>{initial.errors?.render||initial.errors?.network||document.title}</p><div className="actions"><button className="primary" onClick={()=>location.reload()}>{initial.labels?.retry||document.title}</button>{initial.reload_storage_key&&<button className="secondary" onClick={this.restartFresh}>{initial.errors?.reset_session}</button>}</div></main>;
 }
}
