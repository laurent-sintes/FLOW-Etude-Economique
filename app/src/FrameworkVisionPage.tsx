import {ArrowRight} from 'lucide-react';
import {useStudy,type Data} from './context';
import {MethodText} from './MethodDocument';
import {ReadingNote} from './ReadingNote';
import {navigationPages,dossierHref} from './dossierNavigation';
import './frameworkVision.css';
import './frameworkJourney.css';
export function SiteIntroductionPage(){
 const {data}=useStudy(),V=data.ui.essential.framework_vision,J=V.journey,F=data.ui.essential.model_reading,D=data.content.delivery_readiness,gate=D.gates[0],deliveryPages=navigationPages('capacite-realisation',data.ui.essential.dossiers.delivery.pages);
 return <div className="essential-page framework-vision framework-journey">
  <section className="vision-opening"><h2>{V.opening.title}</h2><p><MethodText>{F.chapters.find((chapter:Data)=>chapter.id==='scope').lead}</MethodText></p><p><MethodText>{F.composition}</MethodText></p><p><MethodText>{V.opening.text}</MethodText></p></section>
  <nav className="vision-decision-links" aria-label={V.next.title}><a className="eco-home-link" href="#comparer">{data.ui.essential.economic_dossier.open}<ArrowRight size={17} aria-hidden="true"/></a>{V.next.links.filter((link:Data)=>link.href!=='#comparer').map((link:Data)=><a className="text-button" key={link.href} href={link.href}>{link.label}<ArrowRight size={15} aria-hidden="true"/></a>)}</nav>
  <section className="vision-section"><h2>{J.title}</h2><div className="journey-options">{J.options.map((o:Data)=><article key={o.id}><h3>{o.label}</h3><p>{o.status}</p></article>)}</div><ReadingNote>{J.pending}</ReadingNote></section>
  <section className="vision-section vision-readiness" aria-labelledby="vision-readiness-title"><h2 id="vision-readiness-title">{D.principle.title}</h2><p><MethodText>{D.principle.text}</MethodText></p><p className="vision-readiness-date">{D.labels.review_date} <time dateTime={D.date}>{new Intl.DateTimeFormat(data.ui.locale,{dateStyle:'long',timeZone:'UTC'}).format(new Date(D.date))}</time></p><div className="vision-readiness-grid"><article><h3>{D.notice.title}</h3><p><MethodText>{D.notice.text}</MethodText></p><nav className="vision-readiness-links" aria-label={D.navigation_label}>{deliveryPages.map(page=><a className="text-button" key={page.id} href={page.href}>{page.label}<ArrowRight size={14} aria-hidden="true"/></a>)}</nav></article><article><h3>{gate.title}</h3><span className="vision-gate-status">{D.labels.states[gate.status]}</span><p>{gate.expected}</p><a className="text-button" href={dossierHref('capacite-realisation','gates','missions','view','delivery-readiness-gate-'+gate.id)}>{D.labels.gate_label+' · '+gate.title}<ArrowRight size={15} aria-hidden="true"/></a></article></div></section>
  <a className="journey-overview-next text-button" href="#preetudes">{data.ui.essential.introduction.begin}<ArrowRight size={18} aria-hidden="true"/></a>
 </div>;
}

export function FrameworkVisionPage(){
 const {data}=useStudy(),V=data.ui.essential.framework_vision,J=V.journey,A=V.approach,L=A.labels;
 return <div className="essential-page framework-vision framework-journey">
  <section className="vision-section vision-overview-intro"><h2>{A.title}</h2><p><MethodText>{A.intro}</MethodText></p></section>
  <ol className="framework-story">{J.flow.map((step:string)=><li key={step}>{step}</li>)}</ol>
  <ol className="vision-evaluation-steps">{A.steps.map((step:Data,index:number)=><li key={step.id}>
   <article className="vision-evaluation-step" data-evaluation-step={step.id} aria-labelledby={'vision-stage-'+step.id}>
    <header><span className="vision-stage-number" aria-hidden="true">{index+1}</span><div><h2 id={'vision-stage-'+step.id}>{step.title}</h2><p><MethodText>{step.text}</MethodText></p></div></header>
    <dl className="vision-stage-chain">{['inputs','treatment','output'].map(key=><div key={key} className={'vision-stage-'+key}><dt>{L[key]}</dt><dd><MethodText>{step[key]}</MethodText></dd></div>)}</dl>
    <nav className="vision-stage-links" aria-label={L.links+' · '+step.title}>{step.links.map((link:Data)=><a className="text-button" key={link.href} href={link.href}>{link.label}<ArrowRight size={15} aria-hidden="true"/></a>)}</nav>
   </article>
  </li>)}</ol>
  <div className="vision-matrix-notes">{A.matrix.notes.map((text:string)=><p key={text}><MethodText>{text}</MethodText></p>)}</div>
  <section className="vision-section vision-confidence">
   <h2>{V.confidence.title}</h2><p>{V.confidence.text}</p>
   <ol className="vision-proof-levels">{V.confidence.levels.map((level:Data)=><li key={level.id}><h3>{level.title}</h3><p>{level.text}</p><a className="text-button" href={level.href}>{level.label}<ArrowRight size={15} aria-hidden="true"/></a></li>)}</ol>
  </section>
  <nav className="vision-reading-paths" aria-label={J.labels.next}><a className="journey-overview-next text-button" href="#acquisition">{J.labels.next+' · '+J.phases[0].title}<ArrowRight size={18} aria-hidden="true"/></a></nav>
 </div>;
}
