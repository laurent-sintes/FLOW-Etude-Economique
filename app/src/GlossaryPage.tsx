import {useEffect,useState} from 'react';
import {Search} from 'lucide-react';
import {useStudy,type Data} from './context';
import {SourceLink} from './components';
import {isModelDataReference} from './documentVisibility';
import {matchesReadingText} from './readerNavigation';
import './glossaryPage.css';

export function GlossaryPage({term}:{term?:string}){
 const {data}=useStudy(),G=data.glossary,U=data.ui.essential.glossary,R=data.ui.reading;
 const [query,setQuery]=useState(''),[family,setFamily]=useState('');
 const all=(Object.entries(G.notions) as [string,Data][]).sort(([,a],[,b])=>a.libelle.localeCompare(b.libelle,data.ui.locale));
 const terms=all.filter(([,item])=>(!family||item.famille===family)&&matchesReadingText(query,item.libelle,item.forme_courte,item.definition,item.dans_etude,item.synonymes_historiques));
 const letter=(text:string)=>text.normalize('NFD').replace(/[\u0300-\u036f]/g,'').slice(0,1).toLocaleUpperCase(data.ui.locale);
 const letters=Array.from(new Set(terms.map(([,item])=>letter(item.libelle))));
 const goTo=(id:string)=>{const target=document.getElementById(id);target?.focus({preventScroll:true});target?.scrollIntoView({block:'start'});};
 useEffect(()=>{
  if(!term||!G.notions[term])return;
  const frame=requestAnimationFrame(()=>goTo('glossary-term-'+term));
  return()=>cancelAnimationFrame(frame);
 },[term,G.notions]);
 return <div className="essential-page glossary-page">
  <p className="glossary-introduction">{U.introduction}</p>
  {term&&!G.notions[term]&&<p className="glossary-notice" role="status">{U.unknown_term}</p>}
  <div className="glossary-toolbar">
   <label htmlFor="glossary-search"><span><Search size={18} aria-hidden="true"/>{R.search_glossary}</span><input id="glossary-search" type="search" value={query} onChange={event=>setQuery(event.target.value)}/></label>
   <label htmlFor="glossary-family"><span>{R.family}</span><select id="glossary-family" value={family} onChange={event=>setFamily(event.target.value)}><option value="">{U.all_families}</option>{Object.entries(G.familles).map(([id,label])=><option key={id} value={id}>{String(label)}</option>)}</select></label>
  </div>
  <div className="glossary-results"><p role="status">{U.count.replace('{count}',String(terms.length)).replace('{total}',String(all.length))}</p>{(query||family)&&<button className="text-button" onClick={()=>{setQuery('');setFamily('');document.getElementById('glossary-search')?.focus();}}>{U.reset}</button>}</div>
  {letters.length>0&&<nav className="glossary-alphabet" aria-label={R.alphabet}><h2>{R.alphabet}</h2><ul>{letters.map(initial=><li key={initial}><button type="button" aria-controls={'glossary-letter-'+initial} onClick={()=>goTo('glossary-letter-'+initial)}>{initial}</button></li>)}</ul></nav>}
  {!terms.length&&<p className="glossary-notice">{U.empty}</p>}
  {letters.map(initial=><section className="glossary-letter" key={initial} aria-labelledby={'glossary-letter-'+initial}>
   <h2 id={'glossary-letter-'+initial} tabIndex={-1}>{initial}</h2>
   {terms.filter(([,item])=>letter(item.libelle)===initial).map(([id,item])=>{
    const sources=[item.source_ref,...(item.sources_complementaires||[])].filter(source=>source&&!isModelDataReference(source));
    return <article className="glossary-entry" key={id} data-selected={term===id} aria-labelledby={'glossary-term-'+id}>
     <div className="glossary-entry-heading"><h3 id={'glossary-term-'+id} tabIndex={-1}>{item.libelle}</h3><span>{G.familles[item.famille]}</span></div>
     <p className="glossary-definition">{item.definition}</p>
     {item.dans_etude&&<div className="glossary-context"><h4>{R.in_study}</h4><p>{item.dans_etude}</p></div>}
     {item.synonymes_historiques?.length>0&&<div className="glossary-aliases"><h4>{R.aliases}</h4><p>{item.synonymes_historiques.join(' · ')}</p></div>}
     {sources.length>0&&<div className="source-row">{sources.map((source:string,index:number)=><SourceLink key={source} path={source}>{R.term_source+(sources.length>1?' '+(index+1):'')}</SourceLink>)}</div>}
    </article>;
   })}
  </section>)}
 </div>;
}
