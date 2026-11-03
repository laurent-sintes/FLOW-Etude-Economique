import {useEffect,useState,type ReactNode} from 'react';
import {StudyContext,useStudy,request,type Data} from './context';
import {economicHash,type EconomicRoute} from './economicNavigation';

export function FinancialZoneChoice({route}:{route:EconomicRoute}){
 const {data}=useStudy(),T=data.ui.essential.market_costs;
 return <nav className="financial-zone-choice" aria-label={T.price_zone}><span>{T.price_zone}</span>{['paris','province'].map(zone=><a key={zone} href={economicHash({...route,zone})!} aria-current={(route.zone||'paris')===zone?'true':undefined}>{T.price_zones[zone]}</a>)}</nav>;
}
export function FinancialZone({route,children}:{route:EconomicRoute;children:ReactNode}){
 const context=useStudy(),[variant,setVariant]=useState<Data|null>(null),[error,setError]=useState(false),[attempt,setAttempt]=useState(0);
 const province=route.zone==='province',T=context.data.ui.essential.market_costs;
 useEffect(()=>{let live=true;if(province){setError(false);request<Data>('/api/financial-province').then(value=>{if(value.source_model_version!==context.data.model_version)throw Error('ERR_VERSION');if(live)setVariant(value);}).catch(()=>{if(live)setError(true);});}return()=>{live=false;};},[province,context.data.model_version,attempt]);
 if(!province)return <>{children}</>;
 if(!variant)return <><FinancialZoneChoice route={route}/><p role={error?'alert':'status'}>{error?context.data.ui.errors.network:context.data.ui.labels.loading}</p>{error&&<button className="text-button" onClick={()=>setAttempt(i=>i+1)}>{context.data.ui.labels.retry}</button>}</>;
 const data={...context.data,baseline:variant.baseline,content:{...context.data.content,framework:variant.framework,economic_zone_reading:variant.reading,gross_zone_reading:variant.gross}};
 return <StudyContext.Provider value={{...context,data}}><p className="eco-caption">{T.price_zone_scope}</p>{children}</StudyContext.Provider>;
}
