import {useId} from 'react';
import {useStudy,type Data} from './context';
import {MethodText} from './MethodDocument';
import {SourceLink} from './components';
import './modelMap.css';

export function ModelMap(){
 const {data}=useStudy(),M=data.ui.essential.model_map,S=data.content.delivery_readiness.scope,id=useId();
 if(!M)return null;
 return <section className="model-map" aria-labelledby={id}>
  <h3 id={id}>{M.title}</h3>
  <div className="model-map-overview">
   <figure><div className="model-map-systems">{M.systems.map((system:Data)=><div key={system.id} data-map-id={system.id} className={'model-map-system model-map-'+system.position+(system.program_scope?' model-map-program':'')}>
    {system.program_scope&&<p className="model-map-program-label">{M.program_scope}</p>}
    <h4>{system.label}</h4>
    {system.outside_scope&&<p className="model-map-outside">{M.outside_scope}</p>}
    {system.domains&&<div className="model-map-domains">{system.domains.map((domain:Data)=><div key={domain.id} data-domain-id={domain.id} className={domain.flow?'model-map-domain model-map-flow':'model-map-domain'}>
     <span>{domain.label}</span>
     {domain.flow&&<span className="model-map-product">{M.flow}</span>}
    </div>)}</div>}
   </div>)}</div><figcaption>{M.caption}<p><MethodText>{M.scope}</MethodText></p></figcaption></figure>
  </div>
  <div className="model-reading-links"><a className="text-button" href="#perimetre-retenu">{S.title} <span aria-hidden="true">→</span></a><SourceLink path={S.link.href}>{S.link.label}</SourceLink></div>
 </section>;
}
