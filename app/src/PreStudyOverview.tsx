import {useStudy,type Data} from './context';
import {MethodText} from './MethodDocument';
import {EffortReferences} from './MarketCostsPage';
import {useMarketReading} from './marketReading';
import './preStudies.css';
import {PreStudySummary} from './PreStudySummary';

export function PreStudyOverview(){
 const {data}=useStudy(),E=data.ui.essential,P=E.prestudies;
 return <div className="essential-page prestudy-overview"><h2>{P.overview.question}</h2><div className="prestudy-overview-grid">{P.overview.entries.map((entry:Data)=><article key={entry.page}><h3><a href={'#'+entry.page}>{entry.question}</a></h3><p><MethodText>{entry.description}</MethodText></p><a className="text-button" href={'#'+entry.page}>{E.nav.find((item:Data)=>item.id===entry.page).label} <span aria-hidden="true">→</span></a></article>)}</div></div>;
}
export function ProductivityPage(){
 const {data}=useStudy(),P=data.ui.essential.prestudies,R=data.ui.essential.market_study.references,{reading,error,retry}=useMarketReading();
 return <div className="essential-page core-method-page prestudy-productivity" data-prestudy="productivity"><PreStudySummary topic="productivity"/>{reading?<EffortReferences reading={reading} kind="productivity"/>:error?<p role="alert">{R.error} <button className="text-button" onClick={retry}>{R.retry}</button></p>:<p role="status">{R.loading}</p>}<a className="text-button essential-structure-next" href={P.productivity_next.href}>{P.productivity_next.label} <span aria-hidden="true">→</span></a></div>;
}
