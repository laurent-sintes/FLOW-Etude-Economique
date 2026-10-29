import {ArrowDown,ArrowRight,ChartNoAxesCombined,FileCheck2,ListTree} from 'lucide-react';
import {useStudy,type Data} from './context';
import {SourceLink} from './components';
import {MethodText} from './MethodDocument';
import './frameworkVision.css';

const stepIcons={besoin:ListTree,investissement:ChartNoAxesCombined};
function VisionStep({step}:{step:Data}){
 const Icon=stepIcons[step.id as keyof typeof stepIcons];
 return <article className={`vision-step vision-step-${step.id}`}>
  <div className="vision-step-title"><Icon size={23} aria-hidden="true"/><h3>{step.title}</h3></div>
  <p><MethodText>{step.text}</MethodText></p>
 </article>;
}

export function FrameworkVisionPage(){
 const {data}=useStudy(),V=data.ui.essential.framework_vision;
 const [need,investment]=V.approach.steps,M=V.approach.matrix;
 return <div className="essential-page framework-vision">
  <section className="vision-opening" aria-labelledby="vision-opening-title">
   <h2 id="vision-opening-title">{V.opening.title}</h2>
   <p><MethodText>{V.opening.text}</MethodText></p>
  </section>
  <aside className="vision-adaptation" aria-labelledby="vision-adaptation-title">
   <h2 id="vision-adaptation-title">{V.adaptation.title}</h2>
   <p><MethodText>{V.adaptation.text}</MethodText></p>
   <a className="text-button" href={V.adaptation.href}>{V.adaptation.label}<ArrowRight size={15} aria-hidden="true"/></a>
  </aside>
  <section className="vision-section" aria-labelledby="vision-approach-title">
   <h2 id="vision-approach-title">{V.approach.title}</h2>
   <div className="vision-path">
    <VisionStep step={need}/>
    <div className="vision-path-connector" aria-hidden="true"><ArrowDown size={21}/></div>
    <div className="vision-matrix-scroll" tabIndex={0} role="region" aria-labelledby="vision-matrix-caption">
     <table className="vision-matrix"><caption id="vision-matrix-caption">{M.caption}</caption>
      <thead><tr><th scope="col">{M.activity_label}</th><th scope="col">{M.make_label}</th><th scope="col">{M.buy_label}</th></tr></thead>
      <tbody>{M.rows.map((row:Data)=><tr key={row.id}>
       <th scope="row">{row.title}</th>
       {[row.make,row.buy].map((paragraphs:string[],index:number)=><td key={index}>{paragraphs.map((text:string,paragraph:number)=><p key={paragraph}><MethodText>{text}</MethodText></p>)}</td>)}
      </tr>)}</tbody>
     </table>
    </div>
    <div className="vision-matrix-notes">{M.notes.map((text:string,index:number)=><p key={index}><MethodText>{text}</MethodText></p>)}</div>
    <div className="vision-path-connector" aria-hidden="true"><ArrowDown size={21}/></div>
    <VisionStep step={investment}/>
   </div>
  </section>
  <section className="vision-section" aria-labelledby="vision-evidence-title">
   <h2 id="vision-evidence-title">{V.evidence.title}</h2>
   <div className="vision-evidence">{V.evidence.items.map((item:Data)=><article key={item.id}>
    <FileCheck2 className="vision-evidence-icon" size={21} aria-hidden="true"/>
    <div><h3>{item.title}</h3><p><MethodText>{item.text}</MethodText></p>
     {item.href.startsWith('#')?<a className="text-button" href={item.href}>{item.label}<ArrowRight size={15} aria-hidden="true"/></a>:<SourceLink path={item.href}>{item.label}</SourceLink>}
    </div>
   </article>)}</div>
  </section>
  <section className="vision-section" aria-labelledby="vision-dimensions-title">
   <h2 id="vision-dimensions-title">{V.dimensions.title}</h2>
   <div className="vision-dimensions">{V.dimensions.items.map((item:Data,index:number)=><article key={item.title}>
    <span className="vision-dimension-number" aria-hidden="true">{index+1}</span>
    <div><h3>{item.title}</h3><p><MethodText>{item.text}</MethodText></p></div>
   </article>)}</div>
  </section>
  <section className="vision-section vision-confidence" aria-labelledby="vision-confidence-title">
   <h2 id="vision-confidence-title">{V.confidence.title}</h2>
   <p><MethodText>{V.confidence.text}</MethodText></p>
   <ol className="vision-proof-levels">{V.confidence.levels.map((level:Data)=><li key={level.id} data-proof-level={level.id}>
    <h3>{level.title}</h3><p><MethodText>{level.text}</MethodText></p>
    <a className="text-button" href={level.href}>{level.label}<ArrowRight size={15} aria-hidden="true"/></a>
   </li>)}</ol>
   <div className="vision-confidence-links">{V.confidence.links.map((link:Data)=><a className="text-button" href={link.href} key={link.href}>{link.label}<ArrowRight size={17} aria-hidden="true"/></a>)}</div>
   <div className="vision-limits"><h3>{V.confidence.limits_title}</h3>
    <ul>{V.confidence.limits.map((text:string)=><li key={text}><MethodText>{text}</MethodText></li>)}</ul>
   </div>
  </section>
  <a className="text-button essential-structure-next" href={V.next.href}>{V.next.label}<ArrowRight size={17} aria-hidden="true"/></a>
 </div>;
}
