import type {ReactNode} from 'react';
import {Bot} from 'lucide-react';
import Markdown from 'react-markdown';
import {useStudy,type Data} from './context';
import {isModelDataReference} from './documentVisibility';
import './coreEvaluation.css';

export function MethodText({children}:{children:string}){
 const {data}=useStudy();
 return <Markdown allowedElements={['strong','em','code','a']} unwrapDisallowed components={{a:({href,children})=>{
  const match=/^#glossaire\?term=([a-z0-9_]+)$/.exec(href||'');
  return match&&data.glossary.notions[match[1]]?<a className="method-glossary-link" href={href}>{children}</a>:<>{children}</>;
 }}}>{children}</Markdown>;
}

type MethodBlock =
 | {kind:'paragraphs'|'bullets';items:string[]}
 | {kind:'table';caption:string;columns:string[];rows:string[][]}
 | {kind:'callout';title:string;text:string}
 | {kind:'formula';text:string}
 | {kind:'links';items:{href:string;label:string}[]}
 | {kind:'example';ref:string};

type MethodExample = {
 id:string;title:string;note:string;columns:string[];
 rows:{id:string;label:string;basis:string;quantity:number;unit_jh:number;jh:number}[];
 total_label:string;unit:string;total_jh:number;
 uncertainty:{down_pct:number;up_pct:number;label:string;explanation:string;lower_jh:number;upper_jh:number};
};

function MethodExampleTable({example,format,prefix}:{example:MethodExample;format:(value:number)=>string;prefix:string}){
 const titleId=`${prefix}-example-${example.id}`,U=example.uncertainty;
 return <figure className="core-method-example" aria-labelledby={titleId}>
  <figcaption><h3 id={titleId}>{example.title}</h3><p className="core-method-example-note"><MethodText>{example.note}</MethodText></p></figcaption>
  <div className="core-method-table-scroll" tabIndex={0} role="region" aria-labelledby={titleId}>
   <table className="core-method-table core-method-example-table" aria-labelledby={titleId}>
    <thead><tr>{example.columns.map(column=><th key={column} scope="col">{column}</th>)}</tr></thead>
    <tbody>{example.rows.map(row=><tr key={row.id}><th scope="row">{row.label}</th><td><span className="core-method-basis-values">{format(row.quantity)} × {format(row.unit_jh)} {example.unit}</span><MethodText>{row.basis}</MethodText></td><td className="core-method-number">{format(row.jh)} {example.unit}</td></tr>)}</tbody>
    <tfoot><tr><th scope="row" colSpan={2}>{example.total_label}</th><td className="core-method-number">{format(example.total_jh)} {example.unit}</td></tr></tfoot>
   </table>
  </div>
  <div className="core-method-uncertainty"><h4>{U.label}</h4><p className="core-method-uncertainty-values"><strong>−{format(U.down_pct)} % / +{format(U.up_pct)} %</strong><span>{format(U.lower_jh)} {example.unit} – {format(U.upper_jh)} {example.unit}</span></p><p><MethodText>{U.explanation}</MethodText></p></div>
 </figure>;
}

function MethodContent({block,examples,format,prefix}:{block:MethodBlock;examples:MethodExample[];format:(value:number)=>string;prefix:string}){
 switch(block.kind){
  case 'paragraphs':return <div className="core-method-paragraphs">{block.items.map((text,index)=><p key={index}><MethodText>{text}</MethodText></p>)}</div>;
  case 'bullets':return <ul className="core-method-bullets">{block.items.map((text,index)=><li key={index}><MethodText>{text}</MethodText></li>)}</ul>;
  case 'table':return <div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={block.caption}><table className="core-method-table"><caption>{block.caption}</caption><thead><tr>{block.columns.map(column=><th key={column} scope="col">{column}</th>)}</tr></thead><tbody>{block.rows.map((row,index)=><tr key={index}>{row.map((cell,column)=>column===0?<th key={column} scope="row"><MethodText>{cell}</MethodText></th>:<td key={column}><MethodText>{cell}</MethodText></td>)}</tr>)}</tbody></table></div>;
  case 'callout':return <aside className="core-method-callout"><h3>{block.title}</h3><p><MethodText>{block.text}</MethodText></p></aside>;
  case 'formula':return <p className="core-method-formula">{block.text}</p>;
  case 'links':{
   const links=block.items.filter(link=>!isModelDataReference(link.href));
   return links.length?<ul className="core-method-bullets">{links.map(link=><li key={link.href}><a className="text-button" href={link.href}>{link.label} <span aria-hidden="true">→</span></a></li>)}</ul>:null;
  }
  case 'example':{
   const example=examples.find(item=>item.id===block.ref);
   if(!example)throw new Error('ERR_METHOD_EXAMPLE');
   return <MethodExampleTable example={example} format={format} prefix={prefix}/>;
  }
 }
}

export function MethodDocument({method,children,prefix=method.id,className='',additionalSections=[]}:{method:Data;children?:ReactNode;prefix?:string;className?:string;additionalSections?:{id:string;title:string}[]}){
 const {data}=useStudy();
 const numberFormat=new Intl.NumberFormat(data.ui.locale,{maximumFractionDigits:1});
 const format=(value:number)=>numberFormat.format(value);
 const sectionId=(id:string)=>`${prefix}-section-${id}`;
 const goToSection=(id:string)=>{
  const heading=document.getElementById(sectionId(id));
  heading?.focus({preventScroll:true});
  heading?.scrollIntoView({block:'start',behavior:'auto'});
 };
 const renderSection=(section:Data)=><section key={section.id} className="core-method-section" data-kind={section.kind||'method'} aria-labelledby={sectionId(section.id)}>
  {section.eyebrow&&<p className="core-method-section-label">{section.eyebrow}</p>}
  <h2 id={sectionId(section.id)} tabIndex={-1}>{section.title}</h2><p className="core-method-lead"><MethodText>{section.lead}</MethodText></p>
  <div className="core-method-blocks">{section.blocks.map((block:MethodBlock,index:number)=><MethodContent key={index} block={block} examples={method.examples} format={format} prefix={prefix}/>)}</div>
 </section>;
 return <div className={`essential-page core-method-page ${className}`}>
  <nav className="core-method-navigation" aria-label={method.navigation_label}>
   <h2>{method.navigation_label}</h2>
   <ol>{method.sections.filter((section:Data)=>section.kind!=='example').map((section:Data)=><li key={section.id}><button type="button" aria-controls={sectionId(section.id)} onClick={()=>goToSection(section.id)}>{section.title}</button></li>)}</ol>
   {additionalSections.length>0&&<ul className="core-method-navigation-links">{additionalSections.map(section=><li key={section.id}><button type="button" aria-controls={sectionId(section.id)} onClick={()=>goToSection(section.id)}>{section.title}</button></li>)}</ul>}
   {method.sections.filter((section:Data)=>section.kind==='example').map((section:Data)=><div className="core-method-example-link" key={section.id}><span>{section.eyebrow}</span><button type="button" aria-controls={sectionId(section.id)} onClick={()=>goToSection(section.id)}>{section.title}</button></div>)}
  </nav>
  <section className="core-method-introduction" aria-labelledby={`${prefix}-principle-title`}>
  <div className="core-method-principle"><h2 id={`${prefix}-principle-title`}>{method.principle.title}</h2><p><MethodText>{method.principle.text}</MethodText></p></div>
  {method.tooling&&<div className="core-method-tooling" aria-labelledby={`${prefix}-tooling-title`}>
   <div className="core-method-tooling-header"><span className="core-method-tooling-icon" aria-hidden="true"><Bot size={22}/></span><div><p className="core-method-tooling-label">{method.tooling.label} <code className="core-method-tooling-skill">{method.tooling.skill}</code></p><h3 id={`${prefix}-tooling-title`}>{method.tooling.title}</h3></div></div>
   <p><MethodText>{method.tooling.text}</MethodText></p>
   {method.tooling.items?.length>0&&<ul className="core-method-bullets">{method.tooling.items.map((text:string,index:number)=><li key={index}><MethodText>{text}</MethodText></li>)}</ul>}
   {method.tooling.note&&<p className="core-method-tooling-note"><MethodText>{method.tooling.note}</MethodText></p>}
  </div>}
  <aside className="core-method-notice"><h3>{method.notice.title}</h3><p><MethodText>{method.notice.text}</MethodText></p></aside>
  </section>
  <ol className="core-method-sections">{method.sections.filter((section:Data)=>section.kind!=='example').map((section:Data)=><li key={section.id}>{renderSection(section)}</li>)}</ol>
  {method.sections.filter((section:Data)=>section.kind==='example').map(renderSection)}
  {children}
  <a className="text-button essential-structure-next" href={method.next.href}>{method.next.label} <span aria-hidden="true">→</span></a>
 </div>;
}
