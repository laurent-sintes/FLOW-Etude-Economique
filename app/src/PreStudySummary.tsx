import {useStudy} from './context';
import {MethodText} from './MethodDocument';

export function PreStudySummary({topic}:{topic:string}){
 const {data}=useStudy(),P=data.ui.essential.prestudies,T=P.topics[topic];
 return <aside className="prestudy-takeaway"><h2>{P.summary_title}</h2><p><MethodText>{T.summary}</MethodText></p></aside>;
}
