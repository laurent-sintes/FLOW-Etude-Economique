import {useStudy,type Data} from './context';
import {MethodText} from './MethodDocument';
import {EffortReferences} from './MarketCostsPage';
import {useMarketReading} from './marketReading';
import './preStudies.css';
import {PreStudySummary} from './PreStudySummary';

export function PreStudyOverview(){
 const {data}=useStudy(),P=data.ui.essential.prestudies;
 return <div className="essential-page prestudy-overview"><h2>{P.overview.question}</h2><div className="prestudy-overview-grid">{P.overview.entries.map((entry:Data)=><article key={entry.page}><h3><a href={'#'+entry.page}>{entry.question}</a></h3><p><MethodText>{entry.description}</MethodText></p></article>)}</div></div>;
}
export function ProductivityPage(){
 const {data}=useStudy(),R=data.ui.essential.market_study.references,{reading,error,retry}=useMarketReading();
 return <div className="essential-page core-method-page prestudy-productivity" data-prestudy="productivity"><PreStudySummary topic="productivity"/>{reading?<EffortReferences reading={reading} kind="productivity"/>:error?<p role="alert">{R.error} <button className="text-button" onClick={retry}>{R.retry}</button></p>:<p role="status">{R.loading}</p>}</div>;
}
