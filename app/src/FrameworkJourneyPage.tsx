import {useEffect,useRef} from 'react';
import {ArrowRight} from 'lucide-react';
import {useStudy,type Data} from './context';
import {MethodText} from './MethodDocument';
import {DossierSheet,useDossierFocus} from './Dossier';
import {contextualEconomicLink,phaseReadingHash} from './economicNavigation';
import {PhaseOptionNavigation} from './PhaseOptionNavigation';
import {ReadingNote} from './ReadingNote';
import {FrameworkMakeAudit} from './FrameworkMakeAudit';
import './frameworkJourney.css';

const Text=({text}:{text:string})=><p><MethodText>{text}</MethodText></p>;
export function FrameworkJourneyPage({page,option,horizon,focus,onChoose}:{page:string;option?:string;horizon?:string;focus?:string;onChoose:(id:string)=>void}){
 const {data}=useStudy(),V=data.ui.essential.framework_vision,J=V.journey,L=J.labels;
 const current=J.options.find((o:Data)=>o.id===option)||J.options[0];
 const phase=J.phases.find((p:Data)=>p.id===page),heading=useRef<HTMLHeadingElement>(null),previous=useRef(current.id);
 const target=(part:string)=>'framework-'+page+'-'+current.id+'-'+part;
 useDossierFocus(focus==='method'||focus==='summary'?target(focus):undefined);
 useEffect(()=>{if(previous.current!==current.id){heading.current?.focus({preventScroll:true});previous.current=current.id;}},[current.id]);
 if(page==='scenarios')return <div className="essential-page framework-journey">
  <Text text={J.scenario.intro}/><h2>{L.steps}</h2>
  <ol className="journey-scenario-steps">{J.scenario.steps.map((step:Data)=><li key={step.title}><h3>{step.title}</h3><Text text={step.text}/></li>)}</ol>
  <section className="journey-example"><h2>{J.scenario.example.title}</h2><Text text={J.scenario.example.text}/></section>
  <ReadingNote title={L.future}>{J.scenario.future}</ReadingNote>
  <a className="framework-primary-link" href={contextualEconomicLink(J.scenario.primary.href,current.id,horizon)}>{J.scenario.primary.label}<ArrowRight size={18} aria-hidden="true"/></a>
  <nav className="journey-links journey-secondary-links" aria-label={L.secondary}>{J.scenario.links.map((link:Data)=><a className="text-button" key={link.href} href={contextualEconomicLink(link.href,current.id,horizon)}>{link.label}<ArrowRight size={15} aria-hidden="true"/></a>)}</nav>
 </div>;
 if(page==='methodes')return <div className="essential-page framework-journey">
  <div className="journey-methods">{J.method_groups.map((group:Data)=><section key={group.id}><h2>{group.title}</h2><div className="journey-method-group">{J.methods.filter((method:Data)=>method.group===group.id).map((method:Data)=><article key={method.href}><h3><a href={method.href}>{method.label}</a></h3><Text text={method.text}/></article>)}</div></section>)}</div>
  <section className="journey-evidence"><h2>{V.evidence.title}</h2>{V.evidence.items.map((item:Data)=><a className="text-button" key={item.id} href={item.href}>{item.label}<ArrowRight size={15} aria-hidden="true"/></a>)}</section>
  <section className="vision-confidence"><h2>{V.confidence.title}</h2><Text text={V.confidence.text}/><ol className="journey-scenario-steps vision-proof-levels">{V.confidence.levels.map((level:Data)=><li key={level.id}><h3>{level.title}</h3><Text text={level.text}/><a href={contextualEconomicLink(level.href,current.id,horizon)}>{level.label}</a></li>)}</ol><div className="vision-confidence-links">{V.confidence.links.map((link:Data)=><a className="text-button" key={link.href} href={contextualEconomicLink(link.href,current.id,horizon)}>{link.label}</a>)}</div></section>
 </div>;
 if(!phase)return null;
 const provider=phase.providers.find((p:Data)=>p.option_ref===current.id),index=J.phases.findIndex((p:Data)=>p.id===page);
 const next=J.phases[index+1],nextHref=next?phaseReadingHash({page:next.id,option:current.id,horizon})!:phaseReadingHash({page:'scenarios',option:current.id,horizon})!,nextLabel=L.next+' · '+(next?next.title:data.ui.essential.pages.scenarios.title),resultHref=phaseReadingHash({page:'charges-'+page,option:current.id,horizon})!;
 return <div className="essential-page framework-journey" data-framework-phase={page}>
  <Text text={phase.intro}/>
  <nav className="journey-links" aria-label={data.ui.essential.prestudies.input_label}>{data.ui.essential.prestudies.phase_links[page].map((link:Data)=><a className="text-button" href={link.href} key={link.href}>{link.label}</a>)}</nav>
  <PhaseOptionNavigation journey={J} phase={page} option={current.id} onChoose={onChoose} horizon={horizon}/>
  <DossierSheet view={current.id}><h2 ref={heading} id={target('summary')} tabIndex={-1}>{current.label}</h2><section className="journey-result"><h3>{L.output}</h3><Text text={provider.output}/></section>
   <p className="journey-option-status"><strong>{L.state+' : '}</strong>{provider.status}</p>
   <nav className="journey-reading-shortcuts" aria-label={L.secondary}><a href={resultHref}>{data.ui.essential.gross_evaluations.results}<ArrowRight size={16} aria-hidden="true"/></a><a href={nextHref}>{nextLabel}<ArrowRight size={16} aria-hidden="true"/></a>{current.id==='java-spring'&&<a href={phaseReadingHash({page,option:current.id,horizon,focus:'method'})!}>{L.audit}</a>}</nav>
   <p className="journey-phase-principle"><strong>{current.id==='java-spring'?V.approach.matrix.make_label:V.approach.matrix.buy_label}{' · '}</strong><MethodText>{current.id==='java-spring'?phase.make:phase.buy}</MethodText></p>

   <div className="journey-treatment">{['inputs','treatment'].map(key=><section key={key}><h3>{L[key]}</h3>{key==='treatment'?<ol>{provider[key].map((text:string)=><li key={text}><MethodText>{text}</MethodText></li>)}</ol>:<ul>{provider[key].map((text:string)=><li key={text}><MethodText>{text}</MethodText></li>)}</ul>}</section>)}</div>
   <aside className="journey-example"><h3>{L.example}</h3><Text text={provider.example}/></aside>
   <section className="journey-limits"><h3>{L.limits}</h3><ul>{provider.limits.map((text:string)=><li key={text}><MethodText>{text}</MethodText></li>)}</ul></section>
   {current.id==='java-spring'&&<section className="journey-detailed-method" id={target('method')} tabIndex={-1}><FrameworkMakeAudit plan={phase.make_audit}/><a className="text-button" href={phaseReadingHash({page,option:current.id,horizon,focus:'summary'})!}>{'↑ '+L.output}</a></section>}
   <nav className="journey-links" aria-label={L.references}>{provider.links.map((link:Data)=><a className="text-button" key={link.href} href={contextualEconomicLink(link.href,current.id,horizon)}>{link.label}<ArrowRight size={15} aria-hidden="true"/></a>)}</nav>
   <a className="framework-primary-link" href={resultHref}>{data.ui.essential.gross_evaluations.results}<ArrowRight size={18} aria-hidden="true"/></a>
  </DossierSheet>
  <a className="framework-phase-next text-button" href={nextHref}>{nextLabel}<ArrowRight size={18} aria-hidden="true"/></a>
 </div>;
}

export function FrameworkStackReading({reading}:{reading:Data}){
 return <section className="journey-stack" aria-labelledby="journey-stack-title"><h3 id="journey-stack-title">{reading.title}</h3><Text text={reading.intro}/><div className="journey-stack-groups">{reading.groups.map((group:Data)=><section key={group.title}><h4>{group.title}</h4><dl>{group.elements.map((element:Data)=><div key={element.id}><dt>{element.name}</dt><dd>{element.description}</dd></div>)}</dl></section>)}</div><ReadingNote>{reading.choices}</ReadingNote></section>;
}
