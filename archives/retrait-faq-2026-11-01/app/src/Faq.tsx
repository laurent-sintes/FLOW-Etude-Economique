import {useEffect} from 'react';
import {ArrowUpRight,Link as LinkIcon} from 'lucide-react';
import {useStudy,useFormat,type Data} from './context';
import {Empty,SearchField,SourceLink} from './components';
import {GlossaryText} from './GlossaryText';
import {matchesReadingText,useReadingState} from './readerNavigation';

export function Faq(){
 const {data}=useStudy();const F=data.content.faq,L=F.presentation,U=data.ui.labels;
 const {money,n}=useFormat();const state=useReadingState();
 const query=state.get('q'),topic=state.get('topic'),question=state.get('question');
 const visible=F.questions.filter((q:Data)=>(!topic||q.category===topic)&&matchesReadingText(query,q.title,q.answer,q.paragraphs));
 // An explicit question takes precedence over the page's remembered scroll position.
 useEffect(()=>{if(!question)return;let frame=requestAnimationFrame(()=>{frame=requestAnimationFrame(()=>document.getElementById('faq-'+question)?.scrollIntoView({block:'start'}));});return()=>cancelAnimationFrame(frame);},[question]);
 const figures=(q:Data)=>q.figures?.length>0&&<div className="faq-figures"><p>{L.reference}</p><div className="table-scroll"><table><thead><tr><th>{L.item}</th><th>{L.value}</th></tr></thead><tbody>{q.figures.map((f:Data)=>{
  const value=f.format==='money'||f.format==='annual_money'?money(f.value):n(f.value);
  const unit=f.format==='money'?U.money_unit:f.format==='annual_money'?U.annual_money_unit:f.format==='percent'?U.percent_unit:U.duration_unit;
  return <tr key={f.binding}><th scope="row">{f.label}</th><td>{value+' '+unit}</td></tr>;
 })}</tbody></table></div></div>;
 return <div className="faq-page">
  <SearchField label={L.search} value={query} onChange={q=>state.set({q,question:''})}/>
  <nav className="faq-topics" aria-label={L.topics}><button aria-pressed={!topic} onClick={()=>state.set({topic:'',question:''})}>{L.all}</button>{F.categories.map((c:Data)=><button key={c.id} aria-pressed={topic===c.id} onClick={()=>state.set({topic:c.id,question:''},true)}>{c.label}</button>)}</nav>
  <div className="filter-summary"><span role="status">{visible.length+' / '+F.questions.length+' · '+L.results}</span>{(query||topic)&&<button className="text-button" onClick={()=>state.set({q:'',topic:'',question:''})}>{L.clear}</button>}</div>
  {F.categories.map((c:Data)=>{const rows=visible.filter((q:Data)=>q.category===c.id);return rows.length>0&&<section key={c.id} className="faq-category" aria-labelledby={'faq-category-'+c.id}><h2 id={'faq-category-'+c.id}>{c.label}</h2>{rows.map((q:Data)=><article key={q.id} id={'faq-'+q.id} className="faq-answer">
   <h3><a href={'#faq?question='+q.id} title={L.permalink}><span>{q.title}</span><LinkIcon size={16} aria-hidden="true"/></a></h3>
   <p className="faq-answer-lead"><GlossaryText>{q.answer}</GlossaryText></p>
   {q.paragraphs.map((p:string,i:number)=><p key={i}><GlossaryText>{p}</GlossaryText></p>)}
   {figures(q)}
   <nav className="faq-related" aria-label={L.related}>{q.links.map((link:Data)=><a key={link.route} href={'#'+link.route}>{link.label}<ArrowUpRight size={14}/></a>)}</nav>
   <div className="source-row"><span>{L.sources}</span>{q.sources.map((source:Data)=><SourceLink key={source.path} path={source.path}>{source.label}</SourceLink>)}</div>
  </article>)}</section>;})}
  {!visible.length&&<Empty/>}
 </div>;
}
