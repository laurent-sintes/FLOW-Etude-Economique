import {useStudy} from './context';
import {DossierNavigation,DossierSheet} from './Dossier';
import {navigationPages,selectDossierPage} from './dossierNavigation';
import {MethodText} from './MethodDocument';
import {ReadingNote} from './ReadingNote';
import {MarketComparison} from './MarketComparison';
import {MarketReferences} from './MarketReferenceDrawer';
import {FrameworkStackReading} from './FrameworkJourneyPage';
import {useMarketReading} from './marketReading';
import './marketMethod.css';

export function MarketStudyPage({view,focus}:{view?:string;focus?:string}){
 const {data}=useStudy(),T=data.ui.essential.market_study,E=T.economic,N=data.ui.essential.dossiers.market;
 const pages=navigationPages('etude-marche',N.pages),current=selectDossierPage(pages,view),{reading,error,retry}=useMarketReading();
 const stack=data.ui.essential.framework_vision.journey.phases[0].providers[0].stack_reading;
 const loading=error?<p role="alert">{T.references.error} <button type="button" className="text-button" onClick={retry}>{T.references.retry}</button></p>:<p role="status">{T.references.loading}</p>;
 return <div className="essential-page core-method-page market-study-page dossier-page">
  <p className="core-method-lead"><MethodText>{E.intro}</MethodText></p>
  <DossierNavigation pages={pages} current={current.id} label={N.navigation}/>
  <DossierSheet view={current.id}>
   {current.id==='comparison'&&(reading?.comparison?<MarketComparison comparison={reading.comparison} focus={focus}/>:loading)}
   {current.id==='construction'&&<><p><MethodText>{E.construction}</MethodText></p><FrameworkStackReading reading={stack}/></>}
   {current.id==='references'&&<><ReadingNote>{E.transposition}</ReadingNote><MarketReferences view="projects"/></>}
  </DossierSheet>

 </div>;
}
