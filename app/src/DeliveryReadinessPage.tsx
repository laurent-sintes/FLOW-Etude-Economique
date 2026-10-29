import {useMemo,useState} from 'react';
import {ArrowLeft,Search} from 'lucide-react';
import {useStudy,type Data} from './context';
import {MethodDocument,MethodText} from './MethodDocument';
import {SourceLink} from './components';
import './deliveryReadiness.css';

export function DeliveryConditionsPage(){
 const {data}=useStudy();
 return <MethodDocument method={data.content.delivery_method} prefix="delivery-conditions" className="delivery-conditions-page"/>;
}

export function DeliveryReadinessPage(){
 const {data}=useStudy();
 return <MethodDocument method={data.content.delivery_readiness} prefix="delivery-readiness" className="delivery-readiness-page"/>;
}

const searchable=(text:string)=>text.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr');
export function RetainedScopePage(){
 const {data}=useStudy(),S=data.content.delivery_readiness.scope,L=S.labels;
 const [query,setQuery]=useState('');
 const rows=useMemo(()=>{
  const needle=searchable(query.trim());
  return S.rows.filter((row:Data)=>searchable([row.name,row.capability_id,...row.path,row.boundary].join(' ')).includes(needle));
 },[S.rows,query]);
 return <div className="essential-page core-method-page delivery-scope-page">
  <p className="core-method-lead"><MethodText>{S.introduction}</MethodText></p>
  <dl className="delivery-scope-provenance"><div><dt>{L.capture_date}</dt><dd><time dateTime={S.source.date}>{new Intl.DateTimeFormat(data.ui.locale,{dateStyle:'long'}).format(new Date(S.source.date))}</time></dd></div><div><dt>{L.version}</dt><dd>{S.source.version}</dd></div></dl>
  <div className="delivery-scope-source"><SourceLink path={S.link.href}>{S.link.label}</SourceLink></div>
  <aside className="core-method-callout"><p><MethodText>{S.note}</MethodText></p></aside>
  <div className="delivery-scope-toolbar"><label htmlFor="delivery-scope-search"><Search size={18} aria-hidden="true"/><span>{L.search}</span></label><input type="search" id="delivery-scope-search" value={query} onChange={event=>setQuery(event.target.value)}/><p role="status">{L.results.replace('{count}',String(rows.length))}</p></div>
  <div className="delivery-scope-list">{rows.map((row:Data)=><article className="delivery-scope-capability" key={row.capability_id} data-capability={row.capability_id} aria-labelledby={'scope-capability-'+row.capability_id}>
   <header><p className="delivery-scope-path">{row.path.join(' / ')}</p><h2 id={'scope-capability-'+row.capability_id}>{row.name}</h2><p className="delivery-scope-id">{row.capability_id}</p></header>
   <div className="delivery-scope-boundary"><h3>{L.boundary}</h3><p><MethodText>{row.boundary}</MethodText></p></div>
   <dl className="delivery-scope-axes">{S.axes.map((axis:Data)=>{const value=row.complexity[axis.id];return <div key={axis.id}><dt><span>{axis.label}</span><strong>{value.niveau}</strong></dt><dd><MethodText>{value.justification}</MethodText></dd></div>;})}</dl>
   <SourceLink path={row.href}>{L.native_reference}</SourceLink>
  </article>)}</div>
  <a className="text-button essential-structure-next" href="#modele"><ArrowLeft size={17} aria-hidden="true"/>{L.back_label}</a>
 </div>;
}
