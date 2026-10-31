import {ArrowDown,ArrowRight} from 'lucide-react';
import {useStudy,type Data} from './context';
import {MethodText} from './MethodDocument';
import {ReadingNote} from './ReadingNote';
import './frameworkVision.css';
import './frameworkJourney.css';
export function FrameworkVisionPage(){
 const {data}=useStudy(),V=data.ui.essential.framework_vision,J=V.journey,M=V.approach.matrix;
 return <div className="essential-page framework-vision framework-journey">
  <section className="vision-opening"><h2>{V.opening.title}</h2><p><MethodText>{V.opening.text}</MethodText></p></section>
  <ol className="framework-story">{J.flow.map((step:string)=><li key={step}>{step}</li>)}</ol>
  <section className="vision-section"><h2>{V.approach.steps[0].title}</h2><p><MethodText>{V.approach.steps[0].text}</MethodText></p><div className="journey-evidence vision-evidence">{V.evidence.items.map((item:Data)=><a className="text-button" key={item.id} href={item.href}>{item.label}<ArrowRight size={15} aria-hidden="true"/></a>)}</div></section>
  <section className="vision-section"><h2>{V.approach.title}</h2><div className="vision-matrix-scroll vision-phase-desktop" tabIndex={0} role="region" aria-label={M.caption}><table className="vision-matrix"><caption>{M.caption}</caption><thead><tr><th scope="col">{M.activity_label}</th><th scope="col">{M.make_label}</th><th scope="col">{M.buy_label}</th></tr></thead><tbody>{M.rows.map((row:Data)=><tr key={row.id}><th scope="row"><a href={'#'+row.id}>{row.title}</a></th>{[row.make,row.buy].map((paragraphs:string[],i:number)=><td key={i}>{paragraphs.map(text=><p key={text}><MethodText>{text}</MethodText></p>)}</td>)}</tr>)}</tbody></table></div><div className="vision-phase-mobile">{M.rows.map((row:Data)=><article key={row.id}><h3><a href={'#'+row.id}>{row.title}</a></h3>{[['make',M.make_label],['buy',M.buy_label]].map(([key,label])=><section key={key}><h4>{label}</h4>{row[key].map((text:string)=><p key={text}><MethodText>{text}</MethodText></p>)}</section>)}</article>)}</div></section>
  <section className="vision-section vision-consolidation"><h2>{J.consolidation.title}</h2><p><MethodText>{J.consolidation.text}</MethodText></p></section>
  <section className="vision-section"><h2>{J.title}</h2><div className="journey-options">{J.options.map((o:Data)=><article key={o.id}><h3>{o.label}</h3><p>{o.status}</p></article>)}</div><ReadingNote>{J.pending}</ReadingNote></section>
  <div className="vision-path-connector" aria-hidden="true"><ArrowDown size={21}/></div>
  <section className="vision-step vision-step-investissement"><h2>{V.approach.steps[1].title}</h2><p><MethodText>{V.approach.steps[1].text}</MethodText></p></section>
  <nav className="vision-reading-paths" aria-label={J.labels.next}><a className="journey-overview-next text-button" href="#acquisition">{J.labels.next+' · '+J.phases[0].title}<ArrowRight size={18} aria-hidden="true"/></a></nav>
 </div>;
}
