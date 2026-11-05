import {useEffect,useState,type ReactNode} from 'react';
import {StudyContext,useStudy,request,type Data} from './context';

/** Read the versioned organisation only when a detailed screen needs it. */
export function OrganisationData({children,graph=false}:{children:ReactNode;graph?:boolean}){
 const context=useStudy(),version=context.data.model_version;
 const [loaded,setLoaded]=useState<Data|null>(null),[error,setError]=useState(false),[attempt,setAttempt]=useState(0);
 const incoming=loaded?.model_version===version?loaded:null;
 const content={...context.data.content};
 if(!content.delivery_organisation.work_catalog&&incoming)content.delivery_organisation=incoming.delivery_organisation;
 if(!content.framework_graph.objects&&incoming)content.framework_graph=incoming.framework_graph;
 const ready=Boolean(content.delivery_organisation.work_catalog&&(!graph||content.framework_graph.objects));
 useEffect(()=>{
  if(ready)return;
  let live=true;setError(false);
  request<Data>('/api/organisation-model?model_version='+encodeURIComponent(version)).then(value=>{
   if(value.model_version!==version||!value.delivery_organisation?.work_catalog||!value.framework_graph?.objects)throw Error('ERR_VERSION');
   if(live)setLoaded(value);
  }).catch(()=>{if(live)setError(true);});
  return()=>{live=false;};
 },[version,ready,attempt]);
 if(!ready)return <section className="organisation-loading"><p role={error?'alert':'status'}>{error?context.data.ui.errors.network:context.data.ui.labels.loading}</p>{error&&<button className="secondary" onClick={()=>setAttempt(i=>i+1)}>{context.data.ui.labels.retry}</button>}</section>;
 return <StudyContext.Provider value={{...context,data:{...context.data,content}}}>{children}</StudyContext.Provider>;
}
