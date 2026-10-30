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
 const groups=useMemo(()=>{
  const visible=new Map<string,Data>(rows.map((row:Data)=>[row.capability_id,row]));
  return S.hierarchy.map((domain:Data)=>({...domain,subdomains:domain.subdomains.map((subdomain:Data)=>({...subdomain,
   areas:subdomain.areas.map((area:Data)=>({...area,rows:area.capability_ids.map((id:string)=>visible.get(id)).filter(Boolean)})).filter((area:Data)=>area.rows.length)
  })).filter((subdomain:Data)=>subdomain.areas.length)})).filter((domain:Data)=>domain.subdomains.length);
 },[S.hierarchy,rows]);
 const subdomainCount=S.hierarchy.reduce((sum:number,domain:Data)=>sum+domain.subdomains.length,0);
 const areaCount=S.hierarchy.reduce((sum:number,domain:Data)=>sum+domain.subdomains.reduce((total:number,subdomain:Data)=>total+subdomain.areas.length,0),0);
 const count=(value:number)=>(value===1?L.capability_count_one:L.capability_count).replace('{count}',String(value));
 const subdomainSize=(subdomain:Data)=>subdomain.areas.reduce((sum:number,area:Data)=>sum+area.rows.length,0);
 const goTo=(id:string)=>{const target=document.getElementById(id);target?.focus({preventScroll:true});target?.scrollIntoView({block:'start'});};
 const summary=L.hierarchy_summary.replace('{capabilities}',String(S.rows.length)).replace('{subdomains}',String(subdomainCount)).replace('{areas}',String(areaCount));
 return <div className="essential-page core-method-page delivery-scope-page">
  <p className="core-method-lead"><MethodText>{S.introduction}</MethodText></p>
  <dl className="delivery-scope-provenance"><div><dt>{L.capture_date}</dt><dd><time dateTime={S.source.date}>{new Intl.DateTimeFormat(data.ui.locale,{dateStyle:'long'}).format(new Date(S.source.date))}</time></dd></div><div><dt>{L.version}</dt><dd>{S.source.version}</dd></div></dl>
  <div className="delivery-scope-source"><SourceLink path={S.link.href}>{S.link.label}</SourceLink></div>
  <aside className="core-method-callout"><p><MethodText>{S.note}</MethodText></p></aside>
  <p className="delivery-scope-summary"><MethodText>{summary}</MethodText></p>
  <div className="delivery-scope-direct"><button type="button" className="text-button" aria-controls="scope-capabilities" onClick={()=>goTo('scope-capabilities')} disabled={!rows.length}>{L.open_capabilities}</button><button type="button" className="text-button" aria-controls="scope-scale-title" onClick={()=>goTo('scope-scale-title')}>{L.scale_title}</button></div>
  <div className="delivery-scope-toolbar"><label htmlFor="delivery-scope-search"><Search size={18} aria-hidden="true"/><span>{L.search}</span></label><input type="search" id="delivery-scope-search" value={query} onChange={event=>setQuery(event.target.value)}/><p role="status">{(rows.length===1?L.results_one:L.results).replace('{count}',String(rows.length))}</p>{!rows.length&&<p>{L.no_results}</p>}</div>
  {groups.length>0&&<nav className="core-method-navigation delivery-scope-navigation" aria-labelledby="scope-navigation-title">
   <h2 id="scope-navigation-title" tabIndex={-1}>{L.navigation_title}</h2>
   {groups.map((domain:Data)=><div key={domain.id}><h3>{domain.label}</h3><ol>{domain.subdomains.map((subdomain:Data)=><li key={subdomain.id}>
    <button type="button" aria-controls={'scope-subdomain-'+subdomain.id} onClick={()=>goTo('scope-subdomain-'+subdomain.id)}><span>{subdomain.label}</span><span className="delivery-scope-count">{count(subdomainSize(subdomain))}</span></button>
    <ul className="delivery-scope-area-links">{subdomain.areas.map((area:Data)=><li key={area.id}><button type="button" aria-controls={'scope-area-'+area.id} onClick={()=>goTo('scope-area-'+area.id)}><span>{area.label}</span><span className="delivery-scope-count">{count(area.rows.length)}</span></button></li>)}</ul>
   </li>)}</ol></div>)}
  </nav>}
  <section className="delivery-scope-scale" aria-labelledby="scope-scale-title">
   <h2 id="scope-scale-title" tabIndex={-1}>{L.scale_title}</h2>
   <p className="delivery-scope-scale-unit"><strong>{S.scale.unit}</strong></p>
   <p><MethodText>{S.scale.aggregation}</MethodText></p>
   <div className="delivery-scope-scale-axes">{S.axes.map((axis:Data)=><section key={axis.id} aria-labelledby={'scope-scale-'+axis.id}>
    <h3 id={'scope-scale-'+axis.id}>{axis.label}</h3>
    <ol>{axis.levels.map((level:Data)=><li key={level.level} value={level.level}><MethodText>{level.definition}</MethodText></li>)}</ol>
   </section>)}</div>
  </section>
  <div id="scope-capabilities" tabIndex={-1} className="delivery-scope-groups">{groups.map((domain:Data)=>domain.subdomains.map((subdomain:Data)=><section className="delivery-scope-subdomain" key={subdomain.id} aria-labelledby={'scope-subdomain-'+subdomain.id}>
   <header><p className="delivery-scope-path">{domain.label} / {L.subdomain}</p><h2 id={'scope-subdomain-'+subdomain.id} tabIndex={-1}>{subdomain.label}</h2><p className="delivery-scope-count">{count(subdomainSize(subdomain))}</p></header>
   {subdomain.areas.map((area:Data)=><section className="delivery-scope-area" key={area.id} aria-labelledby={'scope-area-'+area.id}>
    <header><p className="delivery-scope-path">{L.business_area}</p><h3 id={'scope-area-'+area.id} tabIndex={-1}>{area.label}</h3><p className="delivery-scope-count">{count(area.rows.length)}</p></header>
    <div className="delivery-scope-list">{area.rows.map((row:Data)=><article className="delivery-scope-capability" key={row.capability_id} data-capability={row.capability_id} aria-labelledby={'scope-capability-'+row.capability_id}>
     <header><h4 id={'scope-capability-'+row.capability_id}>{row.name}</h4><p className="delivery-scope-id">{row.capability_id}</p></header>
     <div className="delivery-scope-boundary"><h5>{L.boundary}</h5><p><MethodText>{row.boundary}</MethodText></p></div>
     <dl className="delivery-scope-axes">{S.axes.map((axis:Data)=>{const value=row.complexity[axis.id];return <div key={axis.id}><dt><span>{axis.label}</span><strong aria-label={`${S.scale.unit} : ${value.niveau}`}>{value.niveau} / {axis.levels[axis.levels.length-1].level}</strong></dt><dd><MethodText>{value.justification}</MethodText></dd></div>;})}</dl>
     <SourceLink path={row.href}>{L.native_reference}</SourceLink>
    </article>)}</div>
    <button type="button" className="text-button delivery-scope-return" aria-controls="scope-navigation-title" onClick={()=>goTo('scope-navigation-title')}>{L.back_to_navigation}</button>
   </section>)}
  </section>))}</div>
  <a className="text-button essential-structure-next" href="#modele"><ArrowLeft size={17} aria-hidden="true"/>{L.back_label}</a>
 </div>;
}
