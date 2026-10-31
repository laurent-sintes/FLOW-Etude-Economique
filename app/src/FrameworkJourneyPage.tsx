import {useEffect,useRef} from 'react';
import {ArrowRight} from 'lucide-react';
import {useStudy,type Data} from './context';
import {MethodText} from './MethodDocument';
import {DossierLabel,DossierSheet} from './Dossier';
import {ReadingNote} from './ReadingNote';
import {FrameworkMakeAudit} from './FrameworkMakeAudit';
import './frameworkJourney.css';

const Text=({text}:{text:string})=><p><MethodText>{text}</MethodText></p>;
export function FrameworkJourneyPage({page,option,onChoose}:{page:string;option?:string;onChoose:(id:string)=>void}){
 const {data}=useStudy(),V=data.ui.essential.framework_vision,J=V.journey,L=J.labels;
 const current=J.options.find((o:Data)=>o.id===option)||J.options[0];
 const phase=J.phases.find((p:Data)=>p.id===page),heading=useRef<HTMLHeadingElement>(null),previous=useRef(current.id);
 useEffect(()=>{if(previous.current!==current.id){heading.current?.focus({preventScroll:true});previous.current=current.id;}},[current.id]);
 if(page==='scenarios')return <div className="essential-page framework-journey">
  <Text text={J.scenario.intro}/><h2>{L.steps}</h2>
  <ol className="journey-scenario-steps">{J.scenario.steps.map((step:Data)=><li key={step.title}><h3>{step.title}</h3><Text text={step.text}/></li>)}</ol>
  <section className="journey-example"><h2>{J.scenario.example.title}</h2><Text text={J.scenario.example.text}/></section>
  <ReadingNote title={L.future}>{J.scenario.future}</ReadingNote>
  <a className="framework-primary-link" href={J.scenario.primary.href}>{J.scenario.primary.label}<ArrowRight size={18} aria-hidden="true"/></a>
  <nav className="journey-links journey-secondary-links" aria-label={L.secondary}>{J.scenario.links.map((link:Data)=><a className="text-button" key={link.href} href={link.href}>{link.label}<ArrowRight size={15} aria-hidden="true"/></a>)}</nav>
 </div>;
 if(page==='methodes')return <div className="essential-page framework-journey">
  <div className="journey-methods">{J.method_groups.map((group:Data)=><section key={group.id}><h2>{group.title}</h2><div className="journey-method-group">{J.methods.filter((method:Data)=>method.group===group.id).map((method:Data)=><article key={method.href}><h3><a href={method.href}>{method.label}</a></h3><Text text={method.text}/></article>)}</div></section>)}</div>
  <section className="journey-evidence"><h2>{V.evidence.title}</h2>{V.evidence.items.map((item:Data)=><a className="text-button" key={item.id} href={item.href}>{item.label}<ArrowRight size={15} aria-hidden="true"/></a>)}</section>
  <section className="vision-confidence"><h2>{V.confidence.title}</h2><Text text={V.confidence.text}/><ol className="journey-scenario-steps vision-proof-levels">{V.confidence.levels.map((level:Data)=><li key={level.id}><h3>{level.title}</h3><Text text={level.text}/><a href={level.href}>{level.label}</a></li>)}</ol><div className="vision-confidence-links">{V.confidence.links.map((link:Data)=><a className="text-button" key={link.href} href={link.href}>{link.label}</a>)}</div></section>
 </div>;
 if(!phase)return null;
 const provider=phase.providers.find((p:Data)=>p.option_ref===current.id),index=J.phases.findIndex((p:Data)=>p.id===page);
 const next=J.phases[index+1];
 return <div className="essential-page framework-journey" data-framework-phase={page}>
  <Text text={phase.intro}/>
  <nav className="framework-phase-track" aria-label={L.phases}>{J.phases.map((p:Data,i:number)=><a href={'#'+p.id+'?option='+current.id} key={p.id} aria-current={p.id===page?'step':undefined}><span aria-hidden="true">{i+1}</span>{p.short_title}</a>)}</nav>
  <nav className="dossier-navigation journey-option-navigation" aria-label={L.option}>{J.options.map((o:Data)=><a key={o.id} href={'#'+page+'?option='+o.id} aria-current={o.id===current.id?'page':undefined} data-open={o.id===current.id} onClick={()=>onChoose(o.id)}><DossierLabel label={o.label} shortLabel={o.short_label}/></a>)}</nav>
  <DossierSheet view={current.id}><h2 ref={heading} tabIndex={-1}>{current.label}</h2><section className="journey-result"><h3>{L.output}</h3><Text text={provider.output}/></section>
   <p className="journey-option-status"><strong>{L.state+' : '}</strong>{provider.status}</p>
   <p className="journey-phase-principle"><strong>{current.id==='java-spring'?V.approach.matrix.make_label:V.approach.matrix.buy_label}{' · '}</strong><MethodText>{current.id==='java-spring'?phase.make:phase.buy}</MethodText></p>
   <div className="journey-treatment">{['inputs','treatment'].map(key=><section key={key}><h3>{L[key]}</h3>{key==='treatment'?<ol>{provider[key].map((text:string)=><li key={text}><MethodText>{text}</MethodText></li>)}</ol>:<ul>{provider[key].map((text:string)=><li key={text}><MethodText>{text}</MethodText></li>)}</ul>}</section>)}</div>
   <aside className="journey-example"><h3>{L.example}</h3><Text text={provider.example}/></aside>
   {current.id==='java-spring'&&<FrameworkMakeAudit plan={phase.make_audit}/>}
   <section className="journey-limits"><h3>{L.limits}</h3><ul>{provider.limits.map((text:string)=><li key={text}><MethodText>{text}</MethodText></li>)}</ul></section>
   <nav className="journey-links" aria-label={L.references}>{provider.links.map((link:Data)=><a className="text-button" key={link.href} href={link.href}>{link.label}<ArrowRight size={15} aria-hidden="true"/></a>)}</nav>
  </DossierSheet>
  <a className="framework-phase-next text-button" href={next?'#'+next.id+'?option='+current.id:'#scenarios'}>{L.next+' · '+(next?next.title:data.ui.essential.pages.scenarios.title)}<ArrowRight size={18} aria-hidden="true"/></a>
 </div>;
}
