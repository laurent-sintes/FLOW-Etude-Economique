import {RetainedCoreFamilies} from './CoreEvaluationPage';
import {useEffect,useRef,useState,type ReactNode} from 'react';
import {ArrowLeft,ArrowUpRight} from 'lucide-react';
import {useStudy,useFormat,type Data} from './context';
import {Drawer,Section,SourceLink} from './components';
import {GlossaryText} from './GlossaryText';
import {useReadingState} from './readerNavigation';
import {BusinessAtlas} from './BusinessAtlas';
import {BusinessCalibration} from './BusinessCalibration';
import {Architecture,EconomicCosts,EconomicResponsibilities} from './StudyReading';
import {IntegrationEstimates} from './IntegrationEstimates';
import {FundingTable} from './ComposableCosts';
import {MarketReferences} from './ReadingPages';
import {Estimations,Perimetres} from './views';

function Evidence({items}:{items:Data[]}){
 return <div className="journey-evidence">{items.map(item=><SourceLink key={item.path} path={item.path}>{item.label||item.title}</SourceLink>)}</div>;
}

/** A long reading appears only on request, while its route and anchors remain linkable. */
function JourneyDetail({children,clear=[]}:{children:ReactNode;clear?:string[]}){
 const {data}=useStudy(),state=useReadingState();const ref=useRef<HTMLDivElement>(null),focus=state.get('focus'),section=state.get('section');
 useEffect(()=>{
  let second=0;const first=requestAnimationFrame(()=>{second=requestAnimationFrame(()=>{
   const target=(focus?document.getElementById('estimate-'+section+'-'+focus):null)||ref.current;
   if(target&&!document.querySelector('dialog[open]')){target.tabIndex=-1;target.focus({preventScroll:true});target.scrollIntoView({block:'start'});}
  });});
  return()=>{cancelAnimationFrame(first);cancelAnimationFrame(second);};
 },[focus,section]);
 const close=()=>{
  state.set(Object.fromEntries(['detail','focus',...clear].map(key=>[key,''])),true);
  requestAnimationFrame(()=>requestAnimationFrame(()=>{
   const heading=document.querySelector('.page-heading')?.querySelector<HTMLElement>('h1');
   if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true});heading.scrollIntoView({block:'start'});}
  }));
 };
 return <div ref={ref} className="journey-detail" tabIndex={-1}>
  <button className="text-button journey-back" onClick={close}><ArrowLeft size={17}/>{data.content.journey.labels.back}</button>
  {children}
 </div>;
}

export function ComparisonLogic(){
 const {data}=useStudy(),state=useReadingState();const J=data.content.journey.logic;
 if(state.get('detail')==='responsibilities')return <JourneyDetail><EconomicResponsibilities/></JourneyDetail>;
 return <div className="sponsor-journey">
  <div className="journey-two journey-routes">{J.routes.map((route:Data)=><article key={route.id}>
   <span className="eyebrow">{route.eyebrow}</span><h2><GlossaryText>{route.title}</GlossaryText></h2><p><GlossaryText>{route.text}</GlossaryText></p>
  </article>)}</div>
  <Section title={J.map_title} action={<SourceLink path={J.map_source.path}>{J.map_source.label}</SourceLink>}>
   <BusinessAtlas mode="scope" compact/>
   <p className="journey-note">{J.map_note}</p>
  </Section>
  <div className="journey-platform"><div><strong><GlossaryText>{J.platform.title}</GlossaryText></strong><p>{J.platform.text}</p></div><button className="text-button" onClick={()=>state.set({detail:'responsibilities'},true)}>{J.platform.link}<ArrowUpRight size={15}/></button></div>
  <div className="journey-two journey-costs">{J.costs.map((cost:Data)=><article key={cost.notion}><h3><GlossaryText>{data.glossary.notions[cost.notion].libelle}</GlossaryText></h3><small>{cost.timing}</small><p>{cost.text}</p></article>)}</div>
  <a className="source-link" href="#synvance?section=demande">{J.offers_link}<ArrowUpRight size={14}/></a>
 </div>;
}

export function ScopeComparison(){
 const {data}=useStudy(),state=useReadingState();const S=data.content.journey.scope;
 if(['decision','economics','architecture'].includes(state.get('section')))return <JourneyDetail clear={['section']}><Perimetres/></JourneyDetail>;
 return <div className="sponsor-journey">
  <BusinessAtlas mode="scope"/>
  <p className="journey-note">{S.note}</p>
  <div className="journey-links"><a href="#synvance?section=propositions">{S.offers_link}<ArrowUpRight size={15}/></a><a href="#perimetres?section=decision">{S.strategy_link}<ArrowUpRight size={15}/></a><a href="#perimetres?section=economics">{S.responsibilities_link}<ArrowUpRight size={15}/></a></div>
 </div>;
}

function BuildProof({stack,onClose}:{stack:string;onClose:()=>void}){
 const {data}=useStudy();const {amount,n}=useFormat(),B=data.content.journey.build,L=data.content.journey.labels,T=data.content.journey.metrics.work_totals[stack];
 const option=data.baseline.options.find(o=>o.stack===stack)!;
 return <Drawer title={B.charges_title} onClose={onClose} wide>
  <p className="eyebrow">{option.name}</p><p>{B.charges_note}</p>
  <RetainedCoreFamilies units={T.units}/>
  {!T.units.length&&<p>{data.ui.essential.core_results.pending}</p>}
  <div className="journey-calculation"><div><span>{L.before_gains}</span><strong>{n(T.raw_jh.central,0)+' '+L.jh_short}</strong></div><div><span>{L.after_gains}</span><strong>{n(T.net_jh)+' '+L.jh_short}</strong></div><div><span>{B.prestations}</span><strong>{amount(T.prestations_eur_ht)}</strong></div><div><span>{B.pilotage}</span><strong>{amount(T.pilotage_eur_ht)}</strong></div><div className="journey-total"><span>{B.total}</span><strong>{amount(T.build_eur_ht)}</strong></div></div>
  <p className="journey-note">{B.raw_note}</p><p className="journey-note">{B.range_note}</p><Evidence items={[B.source_work,B.source_prices,{...B.source_costs,path:B.source_costs.path+'#options/'+stack+'/detail_build'}]}/>
  <a className="source-link" href={'#market?detail=references&section=rates&stack='+encodeURIComponent(stack)}>{B.rates_link}<ArrowUpRight size={14}/></a>
 </Drawer>;
}

export function CoreBuild(){
 const {data}=useStudy(),state=useReadingState(),{amount,n}=useFormat();const [proof,setProof]=useState(false);const B=data.content.journey.build,L=data.content.journey.labels;
 const options=data.baseline.options.filter(o=>o.mode==='Make'),stack=options.some(o=>o.stack===state.get('stack'))?state.get('stack'):options[0].stack;
 const detail=state.get('detail');
 if(detail==='work')return <JourneyDetail><div id="estimate-build-work" className="estimation-anchor"><BusinessCalibration/></div></JourneyDetail>;
 if(detail==='method')return <JourneyDetail><Estimations focusOnly/><div className="journey-links"><a href={'#build?detail=work&section=build&focus=work&stack='+encodeURIComponent(stack)}>{B.work_detail}<ArrowUpRight size={15}/></a></div></JourneyDetail>;
 if(detail==='architecture')return <JourneyDetail><p className="eyebrow">{options.find(o=>o.stack===stack)!.name}</p><Architecture stack={stack} title={B.architecture_detail}/></JourneyDetail>;
 return <div className="sponsor-journey">
  <p className="journey-note">{data.ui.essential.core_results.make_note}</p><div className="journey-three journey-stack-cards">{options.map(o=>{const totals=data.content.journey.metrics.work_totals[o.stack];return <button key={o.stack} className={stack===o.stack?'active':''} aria-pressed={stack===o.stack} onClick={()=>state.set({stack:o.stack},true)}>
   <span className="journey-stack-name">{o.name}</span><strong>{n(totals.raw_jh.central,0)} <small>{L.jh}</small></strong><span className="journey-stack-range">{totals.units.length?data.ui.essential.core_results.unknown_uncertainty:data.ui.essential.core_results.pending}</span><b>{amount(totals.build_eur_ht)}</b><span className="journey-stack-caption">{B.budget_note}</span>
  </button>;})}</div>
  <p className="journey-note">{B.raw_note}</p><div className="journey-build-actions"><button className="text-button" onClick={()=>setProof(true)}>{B.decomposition}<ArrowUpRight size={14}/></button><a href={'#build?detail=method&section=build&focus=method&stack='+encodeURIComponent(stack)}>{B.method_detail}<ArrowUpRight size={14}/></a></div>
  <div className="journey-platform"><div><strong>{data.ui.composable.hosting_label}</strong><p>{data.ui.composable.hosting_note}</p></div><strong>{amount(options.find(o=>o.stack===stack)!.hosting_build)}</strong><SourceLink path="source/modele-composable.yaml#hebergement_build"/></div>
  <BusinessAtlas mode="build" architecture={<Architecture stack={stack} title={B.architecture_detail}/>}/>
  <div className="journey-links"><a href={'#build?detail=work&section=build&focus=work&stack='+encodeURIComponent(stack)}>{B.work_detail}<ArrowUpRight size={15}/></a></div>
  {proof&&<BuildProof stack={stack} onClose={()=>setProof(false)}/>}
 </div>;
}

function OperationProof({stack,kind,onClose}:{stack:string;kind:'integration'|'run';onClose:()=>void}){
 const {data}=useStudy(),{amount,annualAmount,n}=useFormat();const O=data.content.journey.operations,U=data.ui.integration_reading;
 const option=data.baseline.options.find(o=>o.stack===stack)!,reading=data.content.journey.metrics.options.find((o:Data)=>o.stack===stack);
 return <Drawer title={kind==='integration'?O.budget_detail:O.run_detail} onClose={onClose} wide>
  <p className="eyebrow">{option.name}</p>
  {kind==='integration'?<><p className="journey-proof-value">{amount(reading.integration_eur_ht)}</p><p>{n(reading.integration_months,0)+' '+data.content.journey.labels.months}</p><h3>{U.rows.basis}</h3><p>{option.mode==='Make'?U.make_basis:U.buy_basis[stack]}</p><h3>{U.rows.scope}</h3><p>{option.mode==='Make'?U.make_scope:U.buy_scope}</p>{option.mode==='Make'&&<p className="journey-note">{O.bases_note}</p>}<p className="journey-note">{O.unknown_note}</p><Evidence items={option.mode==='Make'?[O.sources[0]]:[O.sources[stack==='microsoft'?1:2]]}/>{option.mode!=='Make'&&<><p>{O.buy_proof_note}</p><a className="source-link" onClick={onClose} href="#synvance?section=enveloppe">{O.buy_bridge}<ArrowUpRight size={14}/></a></>}<a className="source-link" onClick={onClose} href={'#exploitation?detail=integration&section=integration&focus=basis&stack='+stack}>{O.integration_detail}<ArrowUpRight size={14}/></a></>:<>
   <p className="journey-proof-value">{annualAmount(reading.annual_eur_ht)}</p><p>{O.annual_detail_note}</p>
   <FundingTable options={[option]} values={o=>o.annual_responsibilities} annual/>
   <Evidence items={O.annual_sources}/><a className="source-link" onClick={onClose} href={'#exploitation?detail=run&section=annual&stack='+stack}>{O.annual_detail}<ArrowUpRight size={14}/></a>
  </>}
 </Drawer>;
}

export function IntegrationRun(){
 const {data}=useStudy(),state=useReadingState(),{amount,annualAmount,n}=useFormat();const O=data.content.journey.operations,L=data.content.journey.labels;
 const [proof,setProof]=useState<{stack:string;kind:'integration'|'run'}|null>(null),options=data.content.journey.metrics.options;
 const imax=Math.max(...options.map((o:Data)=>o.integration_eur_ht),1),amax=Math.max(...options.map((o:Data)=>o.annual_eur_ht),1);
 if(state.get('detail')==='integration')return <JourneyDetail clear={['section']}><IntegrationEstimates/></JourneyDetail>;
 if(state.get('detail')==='run')return <JourneyDetail clear={['section']}><EconomicCosts/></JourneyDetail>;
 const scenarioHref='#exploitation?detail=integration&section=integration&focus=scenario-'+encodeURIComponent(O.scenario);
 return <div className="sponsor-journey">
  <div className="journey-comparison-scroll"><table className="journey-comparison"><caption className="sr-only">{O.title}</caption><thead><tr><th>{data.ui.labels.option}</th><th><GlossaryText>{O.integration}</GlossaryText><small>{O.initial_note+' · '+data.ui.labels.money_unit}</small></th><th><GlossaryText>{O.annual}</GlossaryText><small>{O.annual_note+' · '+data.ui.labels.annual_money_unit}</small></th></tr></thead><tbody>{options.map((o:Data)=><tr key={o.stack}>
   <th scope="row">{o.name}<small>{o.mode}</small></th><td><button onClick={()=>setProof({stack:o.stack,kind:'integration'})}><span className="journey-bar-number"><strong>{amount(o.integration_eur_ht)}</strong><small>{n(o.integration_months,0)+' '+L.months}</small></span><span className="journey-bar" aria-hidden="true"><i style={{width:o.integration_eur_ht/imax*100+'%'}}/></span><span className="sr-only">{O.budget_detail}</span></button></td><td><button onClick={()=>setProof({stack:o.stack,kind:'run'})}><span className="journey-bar-number"><strong>{annualAmount(o.annual_eur_ht)}</strong></span><span className="journey-bar journey-bar-annual" aria-hidden="true"><i style={{width:o.annual_eur_ht/amax*100+'%'}}/></span><span className="sr-only">{O.run_detail}</span></button></td>
  </tr>)}</tbody></table></div>
  <p className="journey-note">{O.scales_note+' '+O.unknown_note}</p>
  <div className="journey-three journey-costs">{data.ui.composable.timeline.map((step:Data)=><article key={step.title}><h3>{step.title}</h3><p>{step.text}</p></article>)}</div>
  <p className="journey-note">{data.ui.composable.transition_note}</p>
  <div className="journey-two journey-operation-context"><article><h2>{O.bases_title}</h2><p>{O.bases_text}</p><p className="journey-note">{O.bases_note}</p><a className="source-link" href="#exploitation?detail=integration&section=integration&focus=basis">{O.integration_detail}<ArrowUpRight size={15}/></a></article><article><h2>{O.map_title}</h2><p><GlossaryText>{O.map_text}</GlossaryText></p><p className="journey-note">{O.map_note}</p><a className="source-link" href={scenarioHref}>{O.scenario_link}<ArrowUpRight size={15}/></a></article></div>
  <div className="journey-links"><a href="#exploitation?detail=run&section=annual">{O.annual_detail}<ArrowUpRight size={15}/></a><a href="#simulation-depenses">{O.calendar_link}<ArrowUpRight size={15}/></a></div>
  {proof&&<OperationProof {...proof} onClose={()=>setProof(null)}/>}
 </div>;
}

export function MarketChallenge(){
 const {data}=useStudy(),state=useReadingState(),{amount}=useFormat();const M=data.content.journey.market,S=data.content.journey.metrics.market.sap;
 if(state.get('detail')==='references')return <JourneyDetail clear={['section','ref','q','kind']}><MarketReferences showSummary={false}/></JourneyDetail>;
 return <div className="sponsor-journey">
  <div className="journey-conclusion"><h2>{M.conclusion_title}</h2><p>{M.conclusion}</p><Evidence items={[M.corpus_source]}/></div>
  <div className="journey-arguments">{['build','integration','run'].map(key=>{const row=M[key];return <section className="journey-argument" key={key}><div><h2>{row.title}</h2><span className="journey-status">{row.status}</span></div><div><h3>{row.argument}</h3><p>{row.text}</p>
   {key==='integration'?<><div className="journey-document-difference"><div><span>{row.sum}</span><strong>{amount(S.sum_lots_eur_ht)}</strong></div><div><span>{row.printed}</span><strong>{amount(S.printed_total_eur_ht)}</strong></div><div><span>{row.difference}</span><strong>{amount(S.discrepancy_eur_ht)}</strong></div></div><p className="journey-note">{row.note}</p><Evidence items={row.sources}/></>:<><Evidence items={[row.source]}/><a className="source-link" href={key==='build'?'#build':'#exploitation?detail=run&section=annual'}>{row.link}<ArrowUpRight size={14}/></a></>}
  </div></section>;})}</div>
  <Section title={M.evidence_title}><p className="journey-note">{M.references_note}</p><div className="journey-links"><a href="#market?detail=references&section=projects">{data.content.market.references.length+' · '+M.references_link}<ArrowUpRight size={15}/></a><a href="#market?detail=references&section=rates">{M.rates_link}<ArrowUpRight size={15}/></a></div></Section>
 </div>;
}
