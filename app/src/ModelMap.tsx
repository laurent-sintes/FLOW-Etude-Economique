import {useId,type ReactNode} from 'react';
import {useStudy,type Data} from './context';
import {MethodText} from './MethodDocument';
import {SourceLink} from './components';
import './modelMap.css';

export function ScopeDiagram({heading='h3',children}:{heading?:'h2'|'h3';children?:ReactNode}){
 const {data}=useStudy(),M=data.ui.essential.model_map,id=useId(),Heading=heading,SystemHeading=heading==='h2'?'h3':'h4';
 if(!M)return null;
 return <section className="model-map" aria-labelledby={id}>
  <Heading id={id}>{M.title}</Heading>
  <div className="model-map-overview">
   <figure><div className="model-map-systems">{M.systems.map((system:Data)=><div key={system.id} data-map-id={system.id} className={'model-map-system model-map-'+system.position+(system.program_scope?' model-map-program':'')}>
    {system.program_scope&&<p className="model-map-program-label">{M.program_scope}</p>}
    <SystemHeading>{system.label}</SystemHeading>
    {system.outside_scope&&<p className="model-map-outside">{M.outside_scope}</p>}
    {system.domains&&<div className="model-map-domains">{system.domains.map((domain:Data)=><div key={domain.id} data-domain-id={domain.id} className={domain.flow?'model-map-domain model-map-flow':'model-map-domain'}>
     <span>{domain.label}</span>
     {domain.flow&&<span className="model-map-product">{M.flow}</span>}
    </div>)}</div>}
   </div>)}</div><figcaption>{M.caption}<p><MethodText>{M.scope}</MethodText></p></figcaption></figure>
  </div>
  {children}
 </section>;
}

export function ModelMap(){
 const {data}=useStudy();
 return <ScopeDiagram><p><a className="text-button" href="#cartographie">{data.ui.essential.cartography.input_link} →</a></p></ScopeDiagram>;
}

export function BusinessAreaSummary({heading='h3',provenance=true}:{heading?:'h2'|'h3';provenance?:boolean}){
 const {data}=useStudy(),S=data.content.delivery_readiness.scope,R=data.ui.essential.model_reading,id=useId(),Heading=heading;
 return (
  <section className="model-scope-summary" aria-labelledby={id+'-areas'}>
   <Heading id={id+'-areas'}>{R.scope_areas_title}</Heading>
   <p>{R.scope_areas_note}</p>
   <dl className="model-scope-areas">{S.hierarchy.flatMap((domain:Data)=>domain.subdomains.map((subdomain:Data)=><div key={subdomain.id} data-subdomain={subdomain.id}>
    <dt>{subdomain.label}</dt><dd><ul>{subdomain.areas.map((area:Data)=><li key={area.id} data-area={area.id}>{area.label}</li>)}</ul></dd>
   </div>))}</dl>
   {provenance&&<><p className="model-scope-provenance">{R.scope_source_label} <time dateTime={S.source.date}>{new Intl.DateTimeFormat(data.ui.locale,{dateStyle:'long',timeZone:'UTC'}).format(new Date(S.source.date))}</time></p>
   <div className="model-reading-links"><SourceLink path={S.link.href}>{S.link.label}</SourceLink></div></>}
  </section>
 );
}
