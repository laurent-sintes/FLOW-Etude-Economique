import {useStudy,type Data} from './context';
import {MethodText} from './MethodDocument';
import './economicJourney.css';

export function EconomicContext({page}:{page:string}){
 const {data}=useStudy(),E=data.ui.essential,C=E.economic_context;
 return <section className="economic-context">
  <h2>{C.questions[page]}</h2>
  <p><MethodText>{E.proofs.scope.text}</MethodText></p>
  <nav aria-label={C.proof_title}>{C.links.map((link:Data)=><a key={link.href} href={link.href}>{link.label}</a>)}</nav>
 </section>;
}

export function EconomicNext({page}:{page:string}){
 const {data}=useStudy(),C=data.ui.essential.economic_context,next=C.next[page];
 return <section className="economic-next">
  <h2>{C.journey_title}</h2>
  <a className="text-button economic-next-main" href={next.href}>{next.label} →</a>
  <nav aria-label={C.journey_title}>{C.decision_links.filter((link:Data)=>link.href!==next.href).map((link:Data)=><a key={link.href} href={link.href}>{link.label}</a>)}</nav>
 </section>;
}
