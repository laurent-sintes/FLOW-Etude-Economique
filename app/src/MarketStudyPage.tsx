import {useState,type ReactNode} from 'react';
import {MarketProductDrawer} from './EssentialViews';
import {useStudy,type Data} from './context';
import {MethodText} from './MethodDocument';
import {SourceLink} from './components';
import {isModelDataReference} from './documentVisibility';
import {MarketReferenceDrawer} from './MarketReferenceDrawer';
import {MarketInstruction} from './MarketInstruction';
import {MarketSourceList} from './MarketSources';
import {useMarketReading} from './marketReading';
import './marketMethod.css';

const sectionId=(id:string)=>'market-study-section-'+id;
function StudySection({id,title,children}:{id:string;title:string;children:ReactNode}){
 return <li><section className="core-method-section market-study-section" data-kind="method" aria-labelledby={sectionId(id)}>
  <h2 id={sectionId(id)} tabIndex={-1}>{title}</h2>{children}
 </section></li>;
}
function ApplicationNote({section}:{section:Data|undefined}){
 if(!section)return null;
 const links=(section.links||[]).filter((link:Data)=>!isModelDataReference(link.href));
 return <aside className="core-method-notice market-study-application-note">
  <h3>{section.title}</h3>{section.paragraphs.map((text:string,index:number)=><p key={index}><MethodText>{text}</MethodText></p>)}
  {links.length>0&&<ul>{links.map((link:Data)=><li key={link.href}>{link.href.startsWith('#')?<a className="text-button" href={link.href}>{link.label}</a>:<SourceLink path={link.href}>{link.label}</SourceLink>}</li>)}</ul>}
 </aside>;
}
export function MarketStudyPage(){
 const {data}=useStudy(),T=data.ui.essential.market_study,M=data.content.market_method;
 const notes=data.ui.essential.application_framework.market.sections as Data[];
 const [open,setOpen]=useState<'products'|'projects'|'services'|null>(null);
 const {reading,error,retry}=useMarketReading();
 const sections=[
  {id:'instruction',title:T.instruction.title},
  {id:'produits',title:T.products_title},
  {id:'offres',title:T.offers.title},
  {id:'references',title:T.evidence_title},
  {id:'axes',title:T.axes_title},
 ];
 const goToSection=(id:string)=>{const heading=document.getElementById(sectionId(id));heading?.focus({preventScroll:true});heading?.scrollIntoView({block:'start',behavior:'auto'});};
 const referenceEntry=(view:'products'|'projects'|'services')=><article key={view}>
  <h3>{T.references[view].title}</h3><p><MethodText>{T.references[view].text}</MethodText></p>
  <button type="button" className="secondary" onClick={()=>setOpen(view)}>{T.references[view].action}</button>
 </article>;
 const loading=!reading&&(error?<p role="alert">{T.references.error} <button className="text-button" onClick={retry}>{T.references.retry}</button></p>:<p role="status">{T.references.loading}</p>);
 return <>
  <div className="essential-page core-method-page market-study-page">
   <nav className="core-method-navigation" aria-label={T.navigation}><h2>{T.navigation}</h2><ol>{sections.map(section=><li key={section.id}><button type="button" aria-controls={sectionId(section.id)} onClick={()=>goToSection(section.id)}>{section.title}</button></li>)}</ol></nav>
   <div className="market-study-introduction">
    <p><MethodText>{T.introduction}</MethodText></p>
    <div className="market-study-findings"><h2>{T.findings_title}</h2><ul>{T.findings.map((text:string)=><li key={text}><MethodText>{text}</MethodText></li>)}</ul></div>
    <p><a className="text-button" href={T.method.href}>{T.method.label} <span aria-hidden="true">→</span></a></p>
   </div>
   <ol className="core-method-sections">
    <StudySection id="instruction" title={T.instruction.title}>
     <p className="core-method-lead"><MethodText>{T.instruction.note}</MethodText></p>
     <div className="market-study-progress-summary"><p><strong>{M.instruction.summary.capabilities}</strong> {T.instruction.unit}</p><p><strong>{M.instruction.summary.detailed_qualifications}</strong> {T.instruction.engaged}</p><p><strong>{M.instruction.summary.retained_qualifications}</strong> {T.instruction.retained}</p></div>
     {reading&&<div className="market-study-scope"><p><strong>{T.instruction.scope_title} : </strong>{T.instruction.scope_note.replace('{total}',reading.comparison_scope.bc_total).replace('{compared}',M.instruction.summary.capabilities)}</p><ul>{reading.comparison_scope.bc_exclus.map((id:string)=>{const row=data.content.complexity.rows.find((item:Data)=>item.id===id);return <li key={id}>{id} · {row?.name||row?.capacite?.nom||id}</li>;})}</ul><a href="#complexite" className="text-button">{T.instruction.scope_link}</a></div>}
     <div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={T.instruction.caption}><table className="core-method-table"><caption>{T.instruction.caption}</caption>
      <thead><tr><th scope="col">{T.instruction.product}</th>{Object.entries(M.instruction.status_labels).map(([key,label])=><th scope="col" key={key}>{String(label)}</th>)}</tr></thead>
      <tbody>{M.instruction.progress.map((row:Data)=><tr key={row.product_ref}><th scope="row">{row.label}</th>{Object.keys(M.instruction.status_labels).map(key=><td className="number" key={key}>{row[key]}</td>)}</tr>)}</tbody>
     </table></div>
     {loading}{reading?.instruction&&<MarketInstruction reading={reading}/>}
     <ApplicationNote section={notes.find(section=>section.id==='evidence_status')}/>
    </StudySection>
    <StudySection id="produits" title={T.products_title}>
     <p className="core-method-lead"><MethodText>{T.effort_intro}</MethodText></p>
     {reading&&<>
      <p><MethodText>{reading.effort.introduction}</MethodText></p>
      <div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={T.effort_caption}><table className="core-method-table market-effort-table"><caption>{T.effort_caption}</caption><thead><tr>{Object.values(reading.effort.colonnes).map((label,index)=><th key={index} scope="col">{String(label)}</th>)}</tr></thead><tbody>{reading.effort.lignes.map((row:Data)=><tr key={row.composant}><th scope="row">{row.composant}</th><td>{row.mesure}</td><td>{row.portee}</td></tr>)}</tbody></table></div>
      <p className="market-reference-limit"><MethodText>{reading.effort.conclusion}</MethodText></p><MarketSourceList paths={reading.effort_sources} label={T.references.source}/>
     </>}
     <ApplicationNote section={notes.find(section=>section.id==='cocomo')}/>
     <div className="market-method-reference-entries">{referenceEntry('products')}</div>
    </StudySection>
    <StudySection id="offres" title={T.offers.title}>
     <p className="core-method-lead"><MethodText>{T.offers.text}</MethodText></p>
     <div className="market-study-offer-sources">{T.offers.sources.map((source:Data)=><article key={source.path}><h3>{source.title}</h3><p><MethodText>{source.text}</MethodText></p><SourceLink path={source.path}>{source.label}</SourceLink></article>)}</div>
    </StudySection>
    <StudySection id="references" title={T.evidence_title}>
     <p className="core-method-lead"><MethodText>{T.references.intro}</MethodText></p>
     <div className="market-method-reference-entries">{referenceEntry('projects')}{referenceEntry('services')}</div>
     <div className="market-reference-freshness"><h3>{T.freshness_title}</h3><p><MethodText>{T.freshness_note}</MethodText></p>{reading&&<SourceLink path={reading.review_source}>{T.freshness_source}</SourceLink>}</div>
    </StudySection>
    <StudySection id="axes" title={T.axes_title}>
     <p className="core-method-lead"><MethodText>{M.introduction}</MethodText></p>
     <div className="market-method-axes">{M.axes.map((axis:Data)=><article key={axis.id} aria-labelledby={'market-study-axis-'+axis.id}><header><h3 id={'market-study-axis-'+axis.id}>{axis.titre}</h3><small>{axis.bc_refs.join(' · ')}</small></header><div className="market-method-axis-content"><div><h4>{T.axis_target}</h4><p><MethodText>{axis.cible_flow}</MethodText></p></div><div className="market-method-axis-test"><h4>{T.axis_test}</h4><p><MethodText>{axis.essai}</MethodText></p></div></div></article>)}</div>
    </StudySection>
   </ol>
   <a className="text-button essential-structure-next" href={T.next.href}>{T.next.label} <span aria-hidden="true">→</span></a>
  </div>
  {open==='products'&&<MarketProductDrawer onClose={()=>setOpen(null)}/>}
  {(open==='projects'||open==='services')&&<MarketReferenceDrawer view={open} onClose={()=>setOpen(null)}/>}
 </>;
}
