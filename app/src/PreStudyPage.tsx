import {useStudy,useFormat,type Data} from './context';
import {DossierNavigation,DossierSheet} from './Dossier';
import {navigationPages,selectDossierPage} from './dossierNavigation';
import {MethodText} from './MethodDocument';
import {PreStudySummary} from './PreStudySummary';
import {MarketComparison} from './MarketComparison';
import {MarketInstruction} from './MarketInstruction';
import {MarketProducts} from './EssentialViews';
import {MarketReferences} from './MarketReferenceDrawer';
import {useMarketReading} from './marketReading';
import {EffortReferences} from './MarketCostsPage';
import './marketMethod.css';

export function PreStudyPage({kind,view,focus}:{kind:'projects'|'solutions';view?:string;focus?:string}){
 const {data}=useStudy(),{amount}=useFormat(),P=data.ui.essential.prestudies,T=P[kind],R=data.ui.essential.market_study.references;
 const N=data.ui.essential.dossiers[kind==='projects'?'prestudy_projects':'prestudy_solutions'];
 const base=kind==='projects'?'preetude-projets':'preetude-solutions',pages=navigationPages(base,N.pages),current=view==='qualification'?{id:'qualification'}:selectDossierPage(pages,view);
 const {reading,error,retry}=useMarketReading();
 const loading=error?<p role="alert">{R.error} <button type="button" className="text-button" onClick={retry}>{R.retry}</button></p>:<p role="status">{R.loading}</p>;
 return <div className="essential-page core-method-page market-study-page dossier-page" data-prestudy={kind}>
  <DossierNavigation pages={pages} current={current.id==='qualification'?'comparison':current.id} ancestor={current.id==='qualification'} label={N.navigation}/>
  <DossierSheet view={current.id}>
   {current.id!=='qualification'&&!focus?.startsWith('market-reference-')&&<PreStudySummary topic={current.id}/>}
   {kind==='projects'&&current.id==='projects'&&!focus&&reading?.phase_summary&&<section className="prestudy-project-ranges"><h2>{T.ranges_title}</h2><p>{T.ranges_note}</p><div className="market-cost-cards">{reading.phase_summary.phases.find((phase:Data)=>phase.id==='integration').groups.map((group:Data)=><article key={group.id}><h3>{group.titre}</h3><p><strong>{amount(group.min_eur,data.ui.labels.normalized_money_unit)+' – '+amount(group.max_eur,data.ui.labels.normalized_money_unit)}</strong></p><p>{group.limite}</p></article>)}</div></section>}
   {kind==='projects'?<>{current.id==='programmes'?(reading?<EffortReferences reading={reading} kind="programmes"/>:loading):<><MarketReferences key={current.id} view={current.id==='services'?'services':'projects'} focus={focus} evidenceOnly/></>}</>:<>
    {current.id==='comparison'&&(reading?.documentary_comparison?<><p><MethodText>{P.oss_intro}</MethodText></p><MarketComparison comparison={reading.documentary_comparison} focus={focus} mode="evidence"/></>:loading)}
    {current.id==='qualification'&&(reading?.instruction?<MarketInstruction reading={reading} focus={focus}/>:loading)}
    {current.id==='products'&&(reading?.documentary_products?<MarketProducts documentaryStudy={reading.documentary_products} focus={focus}/>:loading)}
   </>}
  </DossierSheet>

 </div>;
}
