import {createContext,useContext,useState,type CSSProperties,type ReactNode} from 'react';
import {ArrowLeft,ArrowRight,Download,FileText} from 'lucide-react';
import {DossierNavigation,DossierSheet} from './Dossier';
import {useStudy,useFormat,type Data} from './context';
import {SourceLink} from './components';
import {MethodText} from './MethodDocument';
import {HorizonFacts} from './EssentialViews';
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
const proofKey=(proof:Data)=>proof.path+'|'+proof.location;
function uniqueProofs(value:unknown):Data[]{
 const found=new Map<string,Data>();
 const visit=(node:unknown)=>{
  if(Array.isArray(node)){node.forEach(visit);return;}
  if(!node||typeof node!=='object')return;
  for(const [key,child] of Object.entries(node)){
   if(key==='proofs')for(const proof of child as Data[])found.set(proofKey(proof),proof);
   else visit(child);
  }
 };
 visit(value);return [...found.values()];
}
const EvidenceContext=createContext<Data[]|null>(null);
function Proofs({items}:{items:Data[]}){
 const registry=useContext(EvidenceContext);
 return <ul className="synvance-proof-refs">{items.map((proof:Data)=><li key={proofKey(proof)} title={proof.label+' — '+proof.location}>
  <SourceLink path={proof.path}>{registry?'['+(registry.findIndex(item=>proofKey(item)===proofKey(proof))+1)+']':proof.short_label}<span className="synvance-sr-only">{' — '+proof.label+' — '+proof.location}</span></SourceLink>
 </li>)}</ul>;
}
function EvidenceRegister({items,reference:R}:{items:Data[];reference:Data}){
 return <section className="synvance-evidence-register" aria-labelledby="synvance-evidence-title"><h2 id="synvance-evidence-title">{R.reading.evidence_title}</h2><p>{R.reading.evidence_intro}</p>
  <ol>{items.map((proof:Data)=><li key={proofKey(proof)}><SourceLink path={proof.path}>{proof.label}</SourceLink><span>{proof.location}</span></li>)}</ol>
 </section>;
}
function ProviderMark({id,detail=false}:{id:string;detail?:boolean}){
 const {data}=useStudy(),publisher=data.content.synvance_reference.reading.publishers.find((item:Data)=>item.id===id);
 return <span className="synvance-publisher" data-publisher={id} style={{'--publisher-accent':publisher.accent} as CSSProperties}>
  <img src={publisher.asset} alt="" aria-hidden="true"/><span><strong>{publisher.name}</strong>{detail&&<small>{publisher.role}</small>}</span>
 </span>;
}
function MobileProvider({id}:{id:string}){return <span className="synvance-mobile-provider"><ProviderMark id={id}/></span>;}
function LocalNavigation({reference:R,current,detail}:{reference:Data;current:string;detail:boolean}){
 const pages=R.reading.pages.map((page:Data)=>({...page,href:page.id==='overview'?'#synvance':'#synvance-'+page.id}));
 return <DossierNavigation pages={pages} current={current} label={R.reading.navigation} ancestor={detail} className="synvance-local-navigation"/>;
}
function SupplierLinks({reference:R}:{reference:Data}){
 return <nav className="synvance-supplier-links" aria-label={R.reading.details_title}>{R.synthesis.providers.map((provider:Data)=><a key={provider.id} href={'#synvance-'+provider.id}><ProviderMark id={provider.id} detail/><span>{provider.id==='microsoft'?R.overview.cards[0].link_label:R.overview.cards[1].link_label}<ArrowRight size={15} aria-hidden="true"/></span></a>)}</nav>;
}
function Contents({sections,label}:{sections:{id:string;title:string}[];label:string}){
 const goTo=(id:string)=>{const heading=document.getElementById(sectionId(id));heading?.focus({preventScroll:true});heading?.scrollIntoView({block:'start',behavior:'auto'});};
 return <nav className="core-method-navigation" aria-label={label}><h2>{label}</h2><ol>{sections.map(section=><li key={section.id}><button type="button" aria-controls={sectionId(section.id)} onClick={()=>goTo(section.id)}>{section.title}</button></li>)}</ol></nav>;
}
function Brief({reference:R}:{reference:Data}){
 const B=R.brief;
 return <Chapter id="brief" title={B.title} lead={B.introduction}>
  <button className="synvance-documents-shortcut" type="button" onClick={()=>{const heading=document.getElementById(sectionId('documents'));heading?.focus({preventScroll:true});heading?.scrollIntoView({block:'start'});}}><FileText size={15} aria-hidden="true"/>{R.reading.documents_link}</button>
  <div className="synvance-brief-questions">{B.questions.map((item:Data)=><section key={item.id} aria-labelledby={'synvance-brief-'+item.id}>
   <h3 id={'synvance-brief-'+item.id}>{item.question}</h3>
   <p><MethodText>{item.answer}</MethodText></p>
   <Proofs items={item.proofs}/>
  </section>)}</div>
  <section className="synvance-brief-highlights" aria-labelledby="synvance-brief-highlights">
   <h3 id="synvance-brief-highlights">{B.highlights.title}</h3>
   <ul className="core-method-bullets">{B.highlights.items.map((text:string,index:number)=><li key={index}><MethodText>{text}</MethodText></li>)}</ul>
   <Proofs items={B.highlights.proofs}/>
  </section>
  <aside className="synvance-acquired"><h3>{R.reading.acquired_title}</h3><p>{R.reading.acquired_text}</p><a href="#etude-marche">{R.reading.acquired_link}<ArrowRight size={15} aria-hidden="true"/></a></aside>
  <SupplierLinks reference={R}/>
 </Chapter>;
}
function BusinessScope({reference:R}:{reference:Data}){
 const B=R.business,L=B.labels,axes=B.axes.filter((row:Data)=>!['oms-b2c','architecture'].includes(row.id));
 return <Chapter id="business" title={B.title} lead={B.introduction}>
  <section className="synvance-pattern-reading" aria-labelledby="synvance-pattern-reading-title">
   <h3 id="synvance-pattern-reading-title">{B.pattern_reading.title}</h3>
   <div className="synvance-pattern-proposals">{B.pattern_reading.providers.map((provider:Data)=><article key={provider.id} data-publisher={provider.id}>
    <ProviderMark id={provider.id} detail/>
    <p className="synvance-pattern-assignment">{provider.pattern_ref?B.architectures.find((pattern:Data)=>pattern.id===provider.pattern_ref).title:B.pattern_reading.undetermined_label}</p>
    <ul><li><MethodText>{provider.summary}</MethodText></li><li><MethodText>{provider.scope}</MethodText></li></ul>
    <Proofs items={provider.proofs}/>
   </article>)}</div>
   <p className="synvance-source-note"><MethodText>{B.pattern_reading.note}</MethodText></p>
  </section>
  <section aria-labelledby="synvance-pattern-definitions"><h3 id="synvance-pattern-definitions">{R.reading.architecture_status}</h3>
   <div className="synvance-pattern-definitions">{B.architectures.map((item:Data)=><section key={item.id}><h4>{item.title}</h4><div className="synvance-architecture-diagram"><p>{item.systems[0]}</p><div className="synvance-architecture-branches">{item.systems.slice(1).map((system:string,position:number)=><p key={position}>{system}</p>)}</div></div><p><MethodText>{item.text}</MethodText></p></section>)}</div>
  </section>
  <aside className="core-method-callout"><p><MethodText>{B.architecture_note}</MethodText></p></aside>
  <Proofs items={B.architecture_proofs}/>
  <section aria-labelledby="synvance-business-comparison"><h3 id="synvance-business-comparison">{B.comparison_title}</h3><p><MethodText>{B.comparison_note}</MethodText></p></section>
  <div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={B.comparison_title}>
   <table className="core-method-table synvance-business-table"><caption>{B.comparison_title}</caption><thead><tr>{['topic','request','microsoft','sap'].map(key=><th scope="col" key={key}>{['microsoft','sap'].includes(key)?<ProviderMark id={key} detail/>:L[key]}</th>)}</tr></thead><tbody>
    {axes.map((row:Data)=><tr key={row.id}><th scope="row">{row.topic}<Proofs items={row.proofs}/></th>{['request','microsoft','sap'].map(key=><td key={key} data-label={L[key]} data-provider={key==='request'?undefined:key}>{key!=='request'&&<MobileProvider id={key}/>}<MethodText>{row[key]}</MethodText></td>)}</tr>)}
   </tbody></table>
  </div>
  <a className="synvance-topic-link" href="#synvance-oms">{R.reading.business_oms_link}<ArrowRight size={17} aria-hidden="true"/></a>
  <section aria-labelledby="synvance-business-others"><h3 id="synvance-business-others">{B.others_title}</h3><p><MethodText>{B.others_introduction}</MethodText></p></section>
  <div className="synvance-business-others">{B.others.map((item:Data)=><section key={item.id}><h4>{item.title}</h4><p><MethodText>{item.text}</MethodText></p><Proofs items={item.proofs}/></section>)}</div>
 </Chapter>;
}
function OmsComparison({reference:R}:{reference:Data}){
 const B=R.business;
 return <Chapter id="oms" title={B.oms.title} lead={B.oms.introduction}>
  <div className="synvance-oms-focus">
   <aside className="synvance-reading-summary"><p><MethodText>{B.oms.conclusion}</MethodText></p></aside>
   <div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={B.oms.title}>
    <table className="core-method-table synvance-oms-table"><caption>{B.oms.title}</caption><thead><tr>{['criterion','microsoft','sap','decision'].map(key=><th scope="col" key={key}>{['microsoft','sap'].includes(key)?<ProviderMark id={key} detail/>:B.oms.labels[key]}</th>)}</tr></thead><tbody>
     {B.oms.rows.map((row:Data)=><tr key={row.id}><th scope="row">{row.criterion}<Proofs items={row.proofs}/></th>{['microsoft','sap','decision'].map(key=><td key={key} data-label={B.oms.labels[key]} data-provider={key==='decision'?undefined:key}>{key!=='decision'&&<MobileProvider id={key}/>}<MethodText>{row[key]}</MethodText></td>)}</tr>)}
    </tbody></table>
   </div>
   <section className="synvance-open-points" aria-labelledby="synvance-open-points-title"><h3 id="synvance-open-points-title">{B.oms.open_points_title}</h3><ul>{B.oms.open_points.map((text:string)=><li key={text}><MethodText>{text}</MethodText></li>)}</ul></section>
   <p className="synvance-source-note"><MethodText>{B.oms.note}</MethodText></p>
   <ul className="synvance-product-links">{B.oms.product_sources.map((source:Data)=><li key={source.href}><a href={source.href} target="_blank" rel="noopener">{source.label}</a></li>)}</ul>
  </div>
 </Chapter>;
}
function priceRanges(amounts:Data[]){
 const ranges:Data[]=[];
 for(const item of amounts){const last=ranges[ranges.length-1];if(last&&last.end+1===item.year&&last.amount_eur===item.amount_eur)last.end=item.year;else ranges.push({start:item.year,end:item.year,amount_eur:item.amount_eur});}
 return ranges;
}
function SourceCostCell({cell,labels:L}:{cell:Data;labels:Data}){
 const {amount}=useFormat();
 return <><strong className="synvance-cost-status">{cell.status}</strong><p><MethodText>{cell.scope}</MethodText></p>
  {cell.entries.map((entry:Data)=><div className="synvance-cost-entry" key={entry.kind+entry.source_id}>
   <strong>{entry.label}</strong>
   {entry.kind==='integration'?<p className="synvance-cost-amount">{amount(entry.amount_eur)}</p>:<>
    <p className="synvance-period">{L.price_year+' '+entry.source_year}</p>
    {entry.amounts.length>1?<dl className="synvance-price-sequence">{priceRanges(entry.amounts).map((item:Data)=><div key={item.start}><dt>{L.year+' '+item.start+(item.end===item.start?'':'–'+item.end)}</dt><dd>{amount(item.amount_eur)}</dd></div>)}</dl>:<p className="synvance-cost-amount">{amount(entry.amounts[0].amount_eur)}</p>}
   </>}
   <p className="synvance-period">{entry.period}</p>
  </div>)}<Proofs items={cell.proofs}/>
 </>;
}
function CostComparison({reference:R}:{reference:Data}){
 const {data}=useStudy(),{amount,annualAmount}=useFormat(),C=R.costs,L=C.labels;
 const [years,setYears]=useState(data.ui.default_horizon);
 const H=C.model.horizons.find((item:Data)=>item.years===years)||C.model.horizons[0];
 const bridgeRows=[['selection_eur',L.selection],['source_integration_eur',L.source_amount+' · '+L.integration],['integration_additions_eur',L.integration_additions],['integration_eur',L.model_amount+' · '+L.integration]];
 return <Chapter id="costs" title={C.title} lead={C.introduction}>
  <section aria-labelledby={sectionId('synvance-source-costs')}><h3 id={sectionId('synvance-source-costs')} tabIndex={-1}>{C.sources_title}</h3><p className="synvance-reading-label">{L.source_note}</p><p><MethodText>{C.sources_note}</MethodText></p></section>
  <div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={C.sources_title}>
   <table className="core-method-table synvance-cost-table synvance-source-costs"><caption>{C.sources_title}</caption><thead><tr>{['structure','microsoft','sap','scope'].map(key=><th scope="col" key={key}>{['microsoft','sap'].includes(key)?<ProviderMark id={key} detail/>:L[key]}</th>)}</tr></thead><tbody>
    {C.rows.map((row:Data)=><tr key={row.structure_ref}><th scope="row">{row.title}</th>{['microsoft','sap'].map(slug=><td key={slug} data-label={L[slug]} data-provider={slug}><MobileProvider id={slug}/><SourceCostCell cell={row[slug]} labels={L}/></td>)}<td data-label={L.scope}><MethodText>{row.comparison}</MethodText></td></tr>)}
   </tbody></table>
  </div>
  <aside className="core-method-callout">{R.synthesis.providers.find((provider:Data)=>provider.id==='sap').integration.rows.filter((row:Data)=>['published','difference'].includes(row.reading_role)).map((row:Data)=><p key={row.id}><strong>{L.sap+' · '+row.label+' : '+amount(row.amount_eur)}</strong><br/><MethodText>{row.scope}</MethodText></p>)}</aside>
  <SupplierLinks reference={R}/>
  <section aria-labelledby={sectionId('synvance-cost-bridge')}><h3 id={sectionId('synvance-cost-bridge')} tabIndex={-1}>{C.bridge_title}</h3><p><MethodText>{C.bridge_note}</MethodText></p></section>
  <div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={C.bridge_title}>
   <table className="core-method-table synvance-bridge-table"><caption>{L.initial}</caption><thead><tr><th scope="col">{L.structure}</th>{C.model.bridge.map((option:Data)=><th scope="col" key={option.id}><ProviderMark id={option.id} detail/></th>)}</tr></thead><tbody>
    {bridgeRows.map(([id,label])=><tr key={id} data-total={id==='integration_eur'||undefined}><th scope="row">{label}</th>{C.model.bridge.map((option:Data)=><td className="core-method-number" key={option.id} data-label={L[option.id]} data-provider={option.id}><MobileProvider id={option.id}/>{amount(option[id])}</td>)}</tr>)}
   </tbody></table>
  </div>
  <div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={L.annual}>
   <table className="core-method-table synvance-bridge-table"><caption>{L.annual}</caption><thead><tr><th scope="col">{L.structure}</th>{C.model.bridge.map((option:Data)=><th scope="col" key={option.id}><ProviderMark id={option.id} detail/></th>)}</tr></thead><tbody>
    {C.annual_rows.map((row:Data)=><tr key={row.id}><th scope="row">{row.label}</th>{C.model.bridge.map((option:Data)=><td className="core-method-number" key={option.id} data-label={L[option.id]} data-provider={option.id}><MobileProvider id={option.id}/>{annualAmount(option.annual.items[row.id])}</td>)}</tr>)}
    <tr data-total="true"><th scope="row">{L.annual_total}</th>{C.model.bridge.map((option:Data)=><td className="core-method-number" key={option.id} data-label={L[option.id]} data-provider={option.id}><MobileProvider id={option.id}/>{annualAmount(option.annual.total_eur_ht)}</td>)}</tr>
    <tr><th scope="row">{L.service_start}</th>{C.model.bridge.map((option:Data)=><td key={option.id} data-label={L[option.id]} data-provider={option.id}><MobileProvider id={option.id}/>{L.month+' '+option.service_start_month}</td>)}</tr>
   </tbody></table>
  </div>
  <section aria-labelledby={sectionId('synvance-model-costs')}><h3 id={sectionId('synvance-model-costs')} tabIndex={-1}>{C.model_title}</h3><p className="synvance-reading-label">{L.model_note}</p><p><MethodText>{C.model_note}</MethodText></p></section>
  <div className="synvance-horizons" role="group" aria-label={L.horizon}>{C.model.horizons.map((h:Data)=><button type="button" key={h.years} aria-pressed={H.years===h.years} onClick={()=>setYears(h.years)}>{h.years+' '+L.years}</button>)}</div>
  <div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={C.model_title}>
   <table className="core-method-table synvance-cost-table synvance-model-costs"><caption>{C.model_title+' · '+H.years+' '+L.years}</caption><thead><tr>{['structure','microsoft','sap','scope'].map(key=><th scope="col" key={key}>{['microsoft','sap'].includes(key)?<ProviderMark id={key} detail/>:L[key]}</th>)}</tr></thead><tbody>
    {H.rows.map((row:Data)=><tr key={row.id}><th scope="row">{row.title}</th>{['microsoft','sap'].map(slug=><td className="synvance-model-amount" key={slug} data-label={L[slug]} data-provider={slug}><MobileProvider id={slug}/>{row.display==='bundled'&&row.amounts[slug]<=0.01?<span>{L.bundled}</span>:<><strong>{amount(row.amounts[slug])}</strong>{row.display==='bundled'&&<span>{L.bundled}</span>}</>}</td>)}<td data-label={L.scope}><MethodText>{row.scope}</MethodText></td></tr>)}
    <tr data-total="true"><th scope="row">{L.total}</th>{['microsoft','sap'].map(slug=><td className="core-method-number" key={slug} data-label={L[slug]} data-provider={slug}><MobileProvider id={slug}/>{amount(H.totals[slug])}</td>)}<td data-label={L.horizon}>{H.years+' '+L.years}</td></tr>
   </tbody></table>
  </div>
  <div className="synvance-cost-horizon-facts">{data.baseline.options.filter(option=>C.model.bridge.some((item:Data)=>item.id===option.stack)).map(option=><section key={option.stack}><h4><ProviderMark id={option.stack} detail/></h4><HorizonFacts option={option} horizon={H.years}/></section>)}</div>
  <aside className="core-method-callout"><p><MethodText>{C.model_limit}</MethodText></p></aside>
  <ul className="synvance-product-links">{C.model_links.map((link:Data)=><li key={link.href}><a href={link.href}>{link.label}</a></li>)}</ul>
 </Chapter>;
}
function Documents({reference:R}:{reference:Data}){
 const L=R.labels;
 return <Chapter id="documents" title={R.documents.title} lead={R.documents.introduction}>
  <div className="synvance-documents">{R.documents.items.map((doc:Data)=>{const download=fileHref(doc.path.split('#')[0]);const label=doc.format==='pdf'?L.download_pdf:L.download_xlsx;return <article key={doc.id} className="synvance-document">
   <div className="synvance-document-copy"><div className="synvance-document-heading"><FileText aria-hidden="true" size={18}/><h3>{doc.title}</h3></div><p className="synvance-document-author">{doc.author}</p></div>
   <div className="synvance-document-actions"><SourceLink path={doc.path}>{L.open}<span className="synvance-sr-only">{' — '+doc.title}</span></SourceLink>{download&&<a className="secondary synvance-download" href={download} download={doc.path.split('#')[0].split('/').pop()} aria-label={label+' — '+doc.title}><Download size={16} aria-hidden="true"/>{doc.format.toUpperCase()}</a>}</div>
  </article>;})}</div>
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
     <ProviderMark id={P.id} detail/>
     <ul className="core-method-bullets">{P.context.items.map((text:string,index:number)=><li key={index}><MethodText>{text}</MethodText></li>)}</ul>
     <aside className="core-method-callout"><h3>{L.reading_note}</h3><p><MethodText>{R.synthesis.introduction}</MethodText></p></aside>
    </Chapter>
    <Integration reference={R} provider={P}/>
    <AnnualPrices reference={R} provider={P}/>
   </ol>
  </article>
 </>;
}
export function SynvanceReferencePage({providerId,view='overview'}:{providerId?:'microsoft'|'sap';view?:'overview'|'business'|'oms'|'costs'}){
 const {data}=useStudy(),R=data.content.synvance_reference;
 const provider=providerId?R.synthesis.providers.find((item:Data)=>item.id===providerId):null;
 const evidence=provider?uniqueProofs(provider):view==='business'?uniqueProofs({architecture:{proofs:R.business.architecture_proofs},patterns:R.business.pattern_reading,axes:R.business.axes.filter((row:Data)=>!['oms-b2c','architecture'].includes(row.id)),others:R.business.others}):view==='oms'?uniqueProofs(R.business.oms):view==='costs'?uniqueProofs(R.costs):[];
 const costSections=[{id:'synvance-source-costs',title:R.costs.sources_title},{id:'synvance-cost-bridge',title:R.costs.bridge_title},{id:'synvance-model-costs',title:R.costs.model_title}];
 return <div className="essential-page core-method-page synvance-reference-page" data-synvance-page={providerId||view} style={{'--publisher-ms':R.reading.publishers[0].accent,'--publisher-sap':R.reading.publishers[1].accent} as CSSProperties}>
  <LocalNavigation reference={R} current={provider?'costs':view} detail={Boolean(provider)}/>
  <DossierSheet view={providerId||view}>
  <EvidenceContext.Provider value={view==='overview'&&!provider?null:evidence}>
   {provider?<ProviderDetails reference={R} provider={provider}/>:<>
    {view==='costs'&&<Contents sections={costSections} label={R.reading.cost_navigation}/>}
    <ol className="core-method-sections">
     {view==='overview'&&<><Brief reference={R}/><Documents reference={R}/></>}
     {view==='business'&&<BusinessScope reference={R}/>}
     {view==='oms'&&<OmsComparison reference={R}/>}
     {view==='costs'&&<CostComparison reference={R}/>}
    </ol>
   </>}
   {(provider||view!=='overview')&&<><EvidenceRegister items={evidence} reference={R}/><a className="synvance-return" href="#synvance"><ArrowLeft size={17} aria-hidden="true"/>{R.labels.back_to_overview}</a></>}
  </EvidenceContext.Provider>
  </DossierSheet>
 </div>;
}
