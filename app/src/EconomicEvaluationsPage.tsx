import {useEffect,useState} from 'react';
import type {ReactNode} from 'react';
import {SourceLink} from './components';
import {CoreEvaluationResults} from './CoreEvaluationPage';
import {MethodText} from './MethodDocument';
import {request,useStudy,useFormat,type Data} from './context';
import './economicEvaluations.css';

type EconomicOption={stack:string;name:string;mode:'Make'|'Buy';selection:null|{budget_eur_ht:number;months:number;source:string};integration:{budget_eur_ht:number;months:number;source:string};annual:{items:Record<string,number|null>;total_eur_ht:number;source:string}};
type EconomicReading={model_version:string;editorial:Data;options:EconomicOption[];price_convention:{text:string;source:string}};

function ReadingLinks({links}:{links:{href:string;label:string}[]}){
 return <ul className="economic-reading-links">{links.map(link=><li key={link.href}>{link.href.startsWith('#')?<a className="text-button" href={link.href}>{link.label} <span aria-hidden="true">→</span></a>:<SourceLink path={link.href}>{link.label}</SourceLink>}</li>)}</ul>;
}

function ApplicationNote({section}:{section?:Data}){
 if(!section)return null;
 return <aside className="economic-application-note"><h3>{section.title}</h3>{section.paragraphs.map((text:string,index:number)=><p key={index}><MethodText>{text}</MethodText></p>)}{section.links&&<ReadingLinks links={section.links}/>}</aside>;
}

function EvidenceLinks({links}:{links:{path:string;label:string}[]}){
 return <ul className="economic-reading-links">{links.map(link=><li key={link.path}><SourceLink path={link.path}>{link.label}</SourceLink></li>)}</ul>;
}

function EconomicReadingContent({reading}:{reading:EconomicReading}){
 const {data}=useStudy(),{amount,annualAmount,n}=useFormat();
 const E=reading.editorial,L=E.labels,S=E.sections,R=data.ui.essential.core_results;
 const application=data.ui.essential.application_framework.economic;
 const note=(id:string)=>(application.sections as Data[]).find(section=>section.id===id);
 const headingId=(id:string)=>`economic-evaluation-section-${id}`;
 const chapters=[{id:'core',title:R.make_title},...['selection','integration','annual','limits'].map(id=>({id,title:S[id].title}))];
 const goTo=(id:string)=>{const heading=document.getElementById(headingId(id));heading?.focus({preventScroll:true});heading?.scrollIntoView({block:'start',behavior:'auto'});};
 const chapter=(id:string,children:ReactNode)=><section className="economic-chapter" aria-labelledby={headingId(id)}><h2 id={headingId(id)} tabIndex={-1}>{chapters.find(chapter=>chapter.id===id)?.title}</h2>{children}</section>;
 const annualValue=(value:number|null)=>value===null?L.not_applicable:annualAmount(value);
 return <div className="essential-page core-method-page economic-evaluations-page">
  <nav className="core-method-navigation" aria-label={E.navigation_label}><h2>{E.navigation_label}</h2><ol>{chapters.map(chapter=><li key={chapter.id}><button type="button" aria-controls={headingId(chapter.id)} onClick={()=>goTo(chapter.id)}>{chapter.title}</button></li>)}</ol></nav>
  <section className="economic-introduction" aria-labelledby="economic-evaluation-intro"><h2 id="economic-evaluation-intro">{E.intro.title}</h2><p className="core-method-lead"><MethodText>{E.intro.text}</MethodText></p><ApplicationNote section={note('scope')}/><div className="economic-price-convention"><h3>{L.price_convention}</h3><p><MethodText>{reading.price_convention.text}</MethodText></p><SourceLink path={reading.price_convention.source}>{L.source}</SourceLink></div></section>
  {chapter('core',<CoreEvaluationResults status={application.status}/>)}
  {chapter('selection',<>
   <p className="core-method-lead"><MethodText>{S.selection.lead}</MethodText></p>
   <div className="core-method-table-scroll" role="region" tabIndex={0} aria-label={S.selection.caption}><table className="core-method-table economic-evaluation-table" data-evaluation="selection"><caption>{S.selection.caption}</caption><thead><tr><th scope="col">{L.option}</th><th scope="col">{L.budget}</th><th scope="col">{L.duration}</th></tr></thead><tbody>{reading.options.filter(option=>option.selection!==null).map(option=><tr key={option.stack} data-option={option.stack}><th scope="row">{option.name}</th><td className="core-method-number">{amount(option.selection!.budget_eur_ht)}</td><td className="core-method-number">{n(option.selection!.months,0)} {L.months}</td></tr>)}</tbody></table></div>
   <p className="economic-reading-note"><MethodText>{S.selection.note}</MethodText></p><EvidenceLinks links={S.selection.sources}/>
  </>)}
  {chapter('integration',<>
   <p className="core-method-lead"><MethodText>{S.integration.lead}</MethodText></p>
   <div className="core-method-table-scroll" role="region" tabIndex={0} aria-label={S.integration.caption}><table className="core-method-table economic-evaluation-table" data-evaluation="integration"><caption>{S.integration.caption}</caption><thead><tr><th scope="col">{L.option}</th><th scope="col">{L.budget}</th><th scope="col">{L.duration}</th><th scope="col">{L.source}</th></tr></thead><tbody>{reading.options.map(option=><tr key={option.stack} data-option={option.stack}><th scope="row">{option.name}</th><td className="core-method-number">{amount(option.integration.budget_eur_ht)}</td><td className="core-method-number">{n(option.integration.months,0)} {L.months}</td><td><SourceLink path={option.integration.source}>{L.source}</SourceLink></td></tr>)}</tbody></table></div>
   <dl className="economic-basis-list">{['Make',...reading.options.filter(option=>option.mode==='Buy').map(option=>option.stack)].map(key=><div key={key}><dt>{key==='Make'?key:reading.options.find(option=>option.stack===key)?.name}</dt><dd><MethodText>{S.integration.explanations[key]}</MethodText></dd></div>)}</dl>
   <p className="economic-reading-note"><MethodText>{S.integration.note}</MethodText></p><ApplicationNote section={note('calendar')}/><EvidenceLinks links={S.integration.sources}/>
  </>)}
  {chapter('annual',<>
   <p className="core-method-lead"><MethodText>{S.annual.lead}</MethodText></p>
   <div className="core-method-table-scroll" role="region" tabIndex={0} aria-label={S.annual.caption}><table className="core-method-table economic-annual-table" data-evaluation="annual"><caption>{S.annual.caption}</caption><thead><tr><th scope="col">{L.annual_item}</th>{reading.options.map(option=><th key={option.stack} scope="col" data-option={option.stack}>{option.name}</th>)}</tr></thead><tbody>{S.annual.rows.map((row:Data)=><tr key={row.id} data-post={row.id}><th scope="row">{row.label}<span className="economic-item-explanation">{row.explanation}</span></th>{reading.options.map(option=><td className="core-method-number" key={option.stack} data-option={option.stack}>{annualValue(option.annual.items[row.id])}</td>)}</tr>)}</tbody><tfoot><tr data-post="total"><th scope="row">{L.annual_total}</th>{reading.options.map(option=><td key={option.stack} className="core-method-number" data-option={option.stack}>{annualAmount(option.annual.total_eur_ht)}</td>)}</tr></tfoot></table></div>
   <p className="economic-reading-note"><MethodText>{S.annual.note}</MethodText></p>
   <div className="economic-annual-sources"><h3>{L.annual_sources}</h3><EvidenceLinks links={reading.options.map(option=>({path:option.annual.source,label:option.name}))}/></div><EvidenceLinks links={S.annual.sources}/>
  </>)}
  {chapter('limits',<><p className="core-method-lead"><MethodText>{S.limits.lead}</MethodText></p><ApplicationNote section={note('maturity')}/><ReadingLinks links={E.links}/></>)}
 </div>;
}

export function EconomicEvaluationsPage(){
 const {data}=useStudy();
 const [reading,setReading]=useState<EconomicReading|null>(null),[error,setError]=useState(''),[retry,setRetry]=useState(0);
 useEffect(()=>{
  let current=true;setReading(null);setError('');
  request<EconomicReading>(`/api/economic-evaluations?model_version=${encodeURIComponent(data.model_version)}`).then(result=>{
   if(result.model_version!==data.model_version)throw Object.assign(new Error('version'),{code:'version'});
   if(current)setReading(result);
  }).catch(reason=>{if(current)setError(reason.code==='version'?'version':'network');});
  return ()=>{current=false;};
 },[data.model_version,retry]);
 if(error)return <div className="essential-page economic-evaluation-state" role="alert"><p>{error==='version'?data.ui.server_update.message:data.ui.errors.network}</p><button type="button" className="text-button" onClick={()=>error==='version'?window.location.reload():setRetry(value=>value+1)}>{error==='version'?data.ui.server_update.action:data.ui.labels.retry}</button></div>;
 if(!reading)return <p className="economic-evaluation-state" role="status">{data.ui.labels.loading}</p>;
 return <EconomicReadingContent reading={reading}/>;
}
