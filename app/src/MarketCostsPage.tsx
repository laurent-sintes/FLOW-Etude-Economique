import {ProjectRateStudy} from './ProjectRateStudy';
import {useStudy,useFormat,type Data} from './context';
import {DossierNavigation,DossierSheet} from './Dossier';
import {navigationPages,selectDossierPage} from './dossierNavigation';
import {MethodText} from './MethodDocument';
import {ReadingNote} from './ReadingNote';
import {MarketSourceLink,MarketSourceList} from './MarketSources';
import {PreStudySummary} from './PreStudySummary';
import {useDossierFocus} from './Dossier';
import {visibleOptions} from './applicationScope';
import {useMarketReading} from './marketReading';
import './marketMethod.css';
import './marketCosts.css';

export function CostEvidence({items}:{items:Data[]}){
 const {data}=useStudy(),T=data.ui.essential.market_costs;
 if(!items.length)return <span>{T.unknown}</span>;
 return <div className="market-cost-evidence">{items.map((item:Data,index:number)=><p key={item.path+'-'+index}><MarketSourceLink path={item.path} label={T.source}>{item.title}</MarketSourceLink>{item.locator&&<small>{item.locator}</small>}</p>)}</div>;
}
export function EffortReferences({reading,kind}:{reading:Data;kind:'productivity'|'programmes'}){
 const {data}=useStudy(),{money}=useFormat(),T=data.ui.essential.market_costs,C=reading.cost_evidence;
 if(!C)return null;
 return <section className="market-effort-inputs"><h2>{kind==='programmes'?T.programmes_title:T.effort_title}</h2><p><MethodText>{kind==='programmes'?T.programmes_intro:T.effort_intro}</MethodText></p>
  {kind==='programmes'?<div className="market-cost-cards">{C.programmes.map((row:Data)=><article key={row.id}><h3>{row.title}</h3><dl><dt>{T.programme_amount}</dt><dd><strong>{money(row.amount)+' '+T.programme_units[row.currency]}</strong></dd><dt>{T.programme_period}</dt><dd>{row.period+' · '+row.status}</dd></dl><p>{row.scope}</p><ReadingNote>{row.limit}</ReadingNote><CostEvidence items={[{path:row.url,title:row.title}]}/></article>)}</div>:<div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={T.effort_title}><table className="core-method-table"><thead><tr>{Object.values(T.effort_columns).map((label,index)=><th scope="col" key={index}>{String(label)}</th>)}</tr></thead><tbody>{C.effort_groups[kind].map((row:Data)=><tr key={row.composant}><th scope="row">{row.composant}</th><td>{row.mesure}</td><td>{row.portee}</td></tr>)}</tbody></table></div>}
  <MarketSourceList paths={C.effort_sources} label={T.source}/>
  {kind==='productivity'&&<><h2>{T.ai_title}</h2><p><MethodText>{T.ai_intro}</MethodText></p><div className="market-cost-cards">{C.ai.map((row:Data)=><article key={row.id}><h3>{row.title}</h3><p className="market-ai-result"><strong>{row.observed_result}</strong></p><p><time dateTime={row.published_on}>{row.published_on}</time></p><p>{row.population}</p><ReadingNote>{row.limit}</ReadingNote><CostEvidence items={[row.evidence]}/></article>)}</div><a className="text-button" href={T.ai_retained.href}>{T.ai_retained.label}</a></>}
 </section>;
}
export function MarketCostsPage({view,focus}:{view?:string;focus?:string}){
 const {data}=useStudy(),{n}=useFormat(),T=data.ui.essential.market_costs,N=data.ui.essential.dossiers.prestudy_costs;
 const pages=navigationPages('preetude-couts',N.pages),current=selectDossierPage(pages,view),{reading,error,retry}=useMarketReading();
 const C=reading?.cost_evidence,R=data.ui.essential.market_study.references,options=C?visibleOptions(data.ui,C.options,'id'):[];
 const active=data.ui.essential.active_options;
 useDossierFocus(C&&current.id!=='services'?focus:undefined);
 return <div className="essential-page core-method-page market-study-page dossier-page" data-prestudy="costs">
  <DossierNavigation pages={pages} current={current.id} label={N.navigation}/>
  <DossierSheet view={current.id}>
   <PreStudySummary topic={current.id==='services'?'rates':current.id}/>
   {!C?(error||reading?<p role="alert">{R.error} <button className="text-button" onClick={retry}>{R.retry}</button></p>:<p role="status">{R.loading}</p>):<>
    {current.id==='services'&&<ProjectRateStudy focus={focus}/>}
    {current.id==='purchases'&&<><h2>{T.purchases_title}</h2><div className="market-cost-cards">{C.purchases.map((row:Data)=><article key={row.id}><h3>{row.title}</h3><p>{row.scope}</p><CostEvidence items={[row.evidence]}/></article>)}</div><h2>{T.components}</h2><p><MethodText>{T.component_note}</MethodText></p>
     <dl className="prestudy-catalogue-status">{Object.entries(T.component_statuses).map(([status,label])=><div key={status}><dt>{String(label)}</dt><dd>{C.products.filter((row:Data)=>active.includes(row.stack)&&row.status===status).length}</dd></div>)}</dl><p>{T.component_short_note}</p>
     {options.map((option:Data)=><details key={option.id} open={focus==='purchases-'+option.id||undefined} id={'purchases-'+option.id} className="prestudy-proof prestudy-price-group" tabIndex={-1}><summary>{option.label+' · '+T.catalogue}</summary><div className="prestudy-component-grid">{C.products.filter((row:Data)=>row.stack===option.id).map((row:Data)=><article key={row.id}><h3>{row.name}</h3><p className="prestudy-component-status">{T.component_statuses[row.status]||T.unknown}</p><dl><div><dt>{T.edition}</dt><dd>{row.edition||T.unknown}</dd></div><div><dt>{T.licence}</dt><dd>{row.licence||T.unknown}</dd></div><div><dt>{T.regime}</dt><dd>{T.regimes[row.pricing.regime]||T.unknown}</dd></div><div><dt>{T.basis}</dt><dd>{row.pricing.assiette||T.unknown}</dd></div></dl><p>{row.pricing.precision}</p><CostEvidence items={row.evidence}/></article>)}</div></details>)}
    </>}
    {current.id==='indices'&&<><h2>{T.monetary}</h2><div className="market-monetary-sources">{Object.entries(reading.monetary_sources).map(([key,value])=>{const row=value as Data;return <article key={key}><h3>{R.monetary_labels[key]}</h3><dl>{Object.entries(row).filter(([field])=>field in R.monetary_fields).map(([field,value])=><div key={field}><dt>{R.monetary_fields[field]}</dt><dd>{typeof value==='number'?n(value,4):value==null?T.unknown:String(value)}</dd></div>)}</dl>{row.limite&&<p>{row.limite}</p>}<CostEvidence items={Object.entries(row).filter(([field])=>field.startsWith('url')).map(([,path])=>({path,title:T.source}))}/></article>;})}</div><a className="text-button" href={T.monetary_link.href}>{T.monetary_link.label}</a><h2>{T.indices_title}</h2><div className="market-cost-cards">{C.indices.map((row:Data)=><article key={row.id}><h3>{row.titre}</h3><p>{row.portee}</p><p>{row.repere}</p><ul>{row.observations.map((text:string)=><li key={text}>{text}</li>)}</ul><p>{row.limite}</p><CostEvidence items={[{path:row.url,title:row.titre}]}/></article>)}</div></>}
   </>}
  </DossierSheet><a className="text-button essential-structure-next" href={T.next.href}>{T.next.label} <span aria-hidden="true">→</span></a>
 </div>;
}
