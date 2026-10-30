import {useEffect,useState} from 'react';
import {request,useStudy,type Data} from './context';

/** The complete documentary reading is loaded separately from the essential bootstrap. */
export function useMarketReading(){
 const {data}=useStudy();
 const [reading,setReading]=useState<Data|null>(null),[error,setError]=useState(false),[retry,setRetry]=useState(0);
 useEffect(()=>{
  let current=true;setReading(null);setError(false);
  request<Data>('/api/market-references?model_version='+encodeURIComponent(data.model_version))
   .then(value=>{if(current){if(Array.isArray(value.projects)&&Array.isArray(value.services))setReading(value);else setError(true);}})
   .catch(()=>{if(current)setError(true);});
  return()=>{current=false;};
 },[data.model_version,retry]);
 return {reading,error,retry:()=>setRetry(value=>value+1)};
}
