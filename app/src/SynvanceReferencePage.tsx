import type {ReactNode} from 'react';
import {ArrowLeft,ArrowRight,Download,FileText} from 'lucide-react';
import {useStudy,useFormat,type Data} from './context';
import {SourceLink} from './components';
import {MethodText} from './MethodDocument';
import {fileHref} from './transport';
import './synvanceReference.css';

const sectionId=(id:string)=>'synvance-reference-'+id;
function Chapter({id,title,lead,children}:{id:string;title:string;lead:string;children:ReactNode}){
 return <li><section className="core-method-section" data-kind="method" aria-labelledby={sectionId(id)}>
  <h2 id={sectionId(id)} tabIndex={-1}>{title}</h2>
  <p className="core-method-lead"><MethodText>{lead}</MethodText></p>
  <div className="core-method-blocks">{children}</div>
 </section></li>;
}
function Proofs({items}:{items:Data[]}){
 return <ul className="synvance-proof-links">{items.map((proof:Data)=><li key={proof.path}>
  <SourceLink path={proof.path}>{proof.label}<span className="synvance-sr-only">{' — '+proof.location}</span></SourceLink>
  <span className="synvance-proof-location">{proof.location}</span>
 </li>)}</ul>;
}
function Contents({sections,label}:{sections:{id:string;title:string}[];label:string}){
 const goTo=(id:string)=>{const heading=document.getElementById(sectionId(id));heading?.focus({preventScroll:true});heading?.scrollIntoView({block:'start',behavior:'auto'});};
 return <nav className="core-method-navigation" aria-label={label}><h2>{label}</h2><ol>{sections.map(section=><li key={section.id}><button type="button" aria-controls={sectionId(section.id)} onClick={()=>goTo(section.id)}>{section.title}</button></li>)}</ol></nav>;
}
function Documents({reference:R}:{reference:Data}){
 const L=R.labels;
 return <Chapter id="documents" title={R.documents.title} lead={R.documents.introduction}>
  <div className="synvance-documents">{R.documents.items.map((doc:Data)=>{const download=fileHref(doc.path.split('#')[0]);const label=doc.format==='pdf'?L.download_pdf:L.download_xlsx;return <article key={doc.id} className="synvance-document">
   <div className="synvance-document-copy"><div className="synvance-document-heading"><FileText aria-hidden="true" size={22}/><h3>{doc.title}</h3></div><p className="synvance-document-author">{doc.author}</p><p><MethodText>{doc.scope}</MethodText></p><p className="synvance-period">{doc.location}</p></div>
   <div className="synvance-document-actions"><SourceLink path={doc.path}>{L.open}<span className="synvance-sr-only">{' — '+doc.title}</span></SourceLink>{download&&<a className="secondary synvance-download" href={download} download={doc.path.split('#')[0].split('/').pop()} aria-label={label+' — '+doc.title}><Download size={16} aria-hidden="true"/>{label}</a>}</div>
  </article>;})}</div>
 </Chapter>;
}
function Usage({reference:R}:{reference:Data}){
 return <Chapter id="usage" title={R.usage.title} lead={R.usage.introduction}>
  <div className="core-method-paragraphs">{R.usage.paragraphs.map((text:string,index:number)=><p key={index}><MethodText>{text}</MethodText></p>)}</div>
  <ul className="synvance-usage-links">{R.usage.links.map((link:Data)=><li key={link.href}><a className="text-button" href={link.href}>{link.label}<ArrowRight size={17} aria-hidden="true"/></a><p><MethodText>{link.text}</MethodText></p></li>)}</ul>
 </Chapter>;
}
function Integration({reference:R,provider:P}:{reference:Data;provider:Data}){
 const {amount}=useFormat(),L=R.labels,rows=P.integration.rows as Data[];
 // Common evidence is shown once below the table; row-specific evidence stays beside its amount.
 const firstProofs=rows[0].proofs as Data[];
 const shared=rows.every(row=>row.proofs.length===firstProofs.length&&row.proofs.every((proof:Data,index:number)=>proof.path===firstProofs[index].path&&proof.location===firstProofs[index].location));
 return <Chapter id="integration" title={R.synthesis.integration_title} lead={P.integration.intro}>
  <div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={P.title+' · '+R.synthesis.integration_title}>
   <table className="core-method-table synvance-integration-table"><caption>{P.title+' · '+R.synthesis.integration_title}</caption><thead><tr><th scope="col">{L.scope}</th><th scope="col">{L.amount}</th></tr></thead><tbody>
    {rows.map((row:Data)=><tr key={row.id} data-row={row.id} data-reading-role={row.reading_role}><th scope="row"><strong>{row.label}</strong><span className="synvance-row-status">{row.status}</span><p><MethodText>{row.scope}</MethodText></p><p className="synvance-period">{row.period}</p>{!shared&&<Proofs items={row.proofs}/>}</th><td className="core-method-number">{amount(row.amount_eur)}</td></tr>)}
   </tbody></table>
  </div>
  {shared&&<Proofs items={firstProofs}/>}
  <p className="synvance-source-note"><MethodText>{R.synthesis.integration_note}</MethodText></p>
 </Chapter>;
}
function AnnualPrices({reference:R,provider:P}:{reference:Data;provider:Data}){
 const {amount}=useFormat(),L=R.labels;
 return <Chapter id="annual" title={R.synthesis.annual_title} lead={P.annual.intro}>
  <aside className="core-method-callout"><h3>{L.provider_note}</h3><p><MethodText>{R.synthesis.annual_note}</MethodText></p></aside>
  <div className="synvance-annual-list">{P.annual.rows.map((row:Data)=><section className="synvance-annual-item" key={row.id} data-row={row.id} aria-labelledby={'synvance-annual-'+P.id+'-'+row.id}>
   <h3 id={'synvance-annual-'+P.id+'-'+row.id}>{row.label}</h3><p><MethodText>{row.scope}</MethodText></p><p className="synvance-period">{row.amounts.length>1?row.period+' · ':''}{L.price_year} : {row.source_year}</p>
   {row.amounts.length===1?<dl className="synvance-single-price"><div><dt>{row.period}</dt><dd>{amount(row.amounts[0].amount_eur)}</dd></div></dl>:<div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={row.label}>
    <table className="core-method-table synvance-annual-table"><caption>{L.annual_amount}</caption><thead><tr>{row.amounts.map((item:Data)=><th scope="col" key={item.year}>{L.year} {item.year}</th>)}</tr></thead><tbody><tr>{row.amounts.map((item:Data)=><td className="core-method-number" key={item.year}>{amount(item.amount_eur)}</td>)}</tr></tbody></table>
   </div>}
   <Proofs items={row.proofs}/>
  </section>)}</div>
 </Chapter>;
}
function ProviderDetails({reference:R,provider:P}:{reference:Data;provider:Data}){
 const L=R.labels,sections=[{id:'context',title:P.context.title},{id:'integration',title:R.synthesis.integration_title},{id:'annual',title:R.synthesis.annual_title}];
 return <>
  <nav className="synvance-provider-navigation" aria-label={L.provider_navigation}><a href="#synvance"><ArrowLeft size={17} aria-hidden="true"/>{L.back_to_overview}</a>{R.synthesis.providers.map((provider:Data)=><a key={provider.id} href={'#synvance-'+provider.id} aria-current={P.id===provider.id?'page':undefined}>{provider.title}</a>)}</nav>
  <Contents sections={sections} label={R.navigation}/>
  <article className="synvance-provider" data-provider={P.id}>
   <ol className="core-method-sections">
    <Chapter id="context" title={P.context.title} lead={P.context.lead}>
     <ul className="core-method-bullets">{P.context.items.map((text:string,index:number)=><li key={index}><MethodText>{text}</MethodText></li>)}</ul>
     <aside className="core-method-callout"><h3>{L.reading_note}</h3><p><MethodText>{R.synthesis.introduction}</MethodText></p></aside>
    </Chapter>
    <Integration reference={R} provider={P}/>
    <AnnualPrices reference={R} provider={P}/>
   </ol>
  </article>
  <a className="text-button essential-structure-next synvance-return" href="#synvance"><ArrowLeft size={17} aria-hidden="true"/>{L.back_to_overview}</a>
 </>;
}
export function SynvanceReferencePage({providerId}:{providerId?:'microsoft'|'sap'}){
 const {data}=useStudy(),{amount}=useFormat(),R=data.content.synvance_reference;
 const provider=providerId?R.synthesis.providers.find((item:Data)=>item.id===providerId):null;
 const sections=[{id:'overview',title:R.overview.title},{id:'documents',title:R.documents.title},{id:'usage',title:R.usage.title}];
 return <div className="essential-page core-method-page synvance-reference-page" data-synvance-page={providerId||'overview'}>{provider?<ProviderDetails reference={R} provider={provider}/>:<>
  <Contents sections={sections} label={R.navigation}/>
  <div className="core-method-introduction synvance-introduction"><p className="core-method-lead"><MethodText>{R.introduction}</MethodText></p></div>
  <ol className="core-method-sections">
   <Chapter id="overview" title={R.overview.title} lead={R.overview.introduction}>
    <ul className="synvance-usage-links synvance-inputs">{R.overview.inputs.map((input:Data)=><li key={input.path}><SourceLink path={input.path}>{input.label}</SourceLink><p><MethodText>{input.text}</MethodText></p></li>)}</ul>
    <section aria-labelledby="synvance-proposals"><h3 id="synvance-proposals">{R.overview.proposals_title}</h3><p><MethodText>{R.overview.proposals_introduction}</MethodText></p></section>
    <div className="synvance-overview-cards">{R.overview.cards.map((card:Data)=><article key={card.id} className="synvance-overview-card">
     <h3>{card.title}</h3><p><MethodText>{card.description}</MethodText></p>
     {card.highlights.map((row:Data)=><div className="synvance-highlight" key={row.id}><span>{row.label}</span><strong>{amount(row.amount_eur)}</strong></div>)}
     <p className="synvance-overview-note"><MethodText>{card.note}</MethodText></p><a className="text-button" href={card.href}>{card.link_label}<ArrowRight size={17} aria-hidden="true"/></a>
    </article>)}</div>
    <aside className="core-method-callout"><p><MethodText>{R.overview.warning}</MethodText></p></aside>
   </Chapter>
   <Documents reference={R}/>
   <Usage reference={R}/>
  </ol>
 </>}</div>;
}
