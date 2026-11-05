import {ContentLinks} from './ContentLinks';
import {useStudy} from './context';
import {MethodText} from './MethodDocument';
import './economicJourney.css';

export function EconomicContext({page}:{page:string}){
 const {data}=useStudy(),E=data.ui.essential,C=E.economic_context;
 return <section className="economic-context">
  <h2>{C.questions[page]}</h2>
  <p><MethodText>{E.proofs.scope.text}</MethodText></p>
  <ContentLinks links={C.links} label={C.proof_title}/>
 </section>;
}
