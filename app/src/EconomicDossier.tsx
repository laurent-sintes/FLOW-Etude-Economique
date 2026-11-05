import {TeamAllocationCosts} from './TeamPhasePage';
import {FinancialZone,FinancialZoneChoice} from './FinancialZone';
import {ProjectRateStudy} from './ProjectRateStudy';
import {useContext,useEffect,useState,type CSSProperties,type ReactNode} from 'react';
import {ArrowRight,CalendarDays,LockKeyhole} from 'lucide-react';
import {request,useStudy,useFormat,type Data,type Option} from './context';
import {visibleOptions,visibleBudgetReview} from './applicationScope';
import {PhaseIcon} from './StudyIcons';
import {SourceLink} from './components';
import {MethodText} from './MethodDocument';
import {useDossierFocus} from './Dossier';
import {MarketComparison} from './MarketComparison';
import {useMarketReading} from './marketReading';
import {economicHash,economicPeriod,economicReadingContext,readingOrigin,shownOptions,type EconomicPage,type EconomicRoute} from './economicNavigation';
import {completionRelation,comparisonTakeaways} from './economicPresentation';
import {ReadingScopeContext} from './ReadingScopeContext';
import {ReadingScope,ReadingPeriodNote} from './ReadingScope';
import './economicDossier.css';

const period=economicPeriod;
function useDossier(){
 const {data}=useStudy(),readingRoute=useContext(ReadingScopeContext),allOptions=visibleOptions(data.ui,data.baseline.options);
 const options=readingRoute.page==='comparer'?allOptions.filter((o:Option)=>shownOptions(readingRoute).includes(o.stack)):allOptions;
 const link=(page:EconomicPage,option?:string,view?:string,extra:Data={})=>economicHash({page,option:option||(page==='evaluation-core'?shownOptions(readingRoute)[0]:undefined),...economicReadingContext(readingRoute),...(/^(?:[1-9]|1[0-5])$/.test(view||'')?{horizon:view}:{view}),...extra})!;
 return {data,T:data.ui.essential.economic_dossier,options,allOptions,link,readingRoute};
}
function periodOption(option:Option,reading:Data,route:{origin?:string}):Option|null{
 const selected=reading.periods.find((row:Data)=>row.stack===option.stack)?.periods.find((row:Data)=>row.anchor===readingOrigin(route));
 return selected?{...option,horizons:selected.horizons,annual:selected.annual}:null;
}
function Dossier({route,children}:{route:EconomicRoute;children:ReactNode}){
 const {options}=useDossier();
 return <div className="essential-page economic-dossier" style={{'--eco-options':options.length} as CSSProperties}><div className="eco-toolbar"><Reference/><FinancialZoneChoice route={route}/></div><ReadingScope route={route}/>{route.page!=='parametres'&&<ReadingPeriodNote route={route}/ >}{children}</div>;
}
function Reference(){const {T}=useDossier();return <p className="eco-reference"><LockKeyhole size={14} aria-hidden="true"/>{T.reference}</p>;}
function OptionChoice({route}:{route:EconomicRoute}){
 const {T,options,link}=useDossier();return <nav className="eco-options" aria-label={T.option}>{options.map((o:Option)=><a key={o.stack} href={link(route.page,o.stack,String(period(route)))} aria-current={(route.option||options[0].stack)===o.stack?'true':undefined}>{o.name}</a>)}</nav>;
}
function Note({title,children}:{title:string;children:ReactNode}){return <aside className="eco-note"><h2>{title}</h2>{children}</aside>;}
function Matrix({label,values}:{label:string;values:ReactNode[]}){return <tr><th scope="row">{label}</th>{values.map((value,i)=><td key={i}>{value}</td>)}</tr>;}
function ComparisonTable({names,label,children}:{names:string[];label:string;children:ReactNode}){const {T}=useDossier();return <table className="eco-table"><caption className="sr-only">{label}</caption><thead><tr><th scope="col">{T.option}</th>{names.map(name=><th scope="col" key={name}>{name}</th>)}</tr></thead><tbody>{children}</tbody></table>;}
function ReadingContext({option}:{option:Option}){const {T}=useDossier();return <p className="eco-option-context">{T.option_notes[option.stack].status}</p>;}
function ProofLink({phase,route,focus,children}:{phase:string;route:EconomicRoute;focus?:string;children:ReactNode}){
 const query=new URLSearchParams({option:route.option||'java-spring',...economicReadingContext(route),returnTo:route.page});
 if(focus)query.set('focus',focus);if(route.family||focus)query.set('family',focus||route.family!);
 return <a href={'#charges-'+phase+'?'+query.toString()}>{children} →</a>;
}
function CalendarValue({option}:{option:Option}){const {T}=useDossier(),{n}=useFormat();return <span>{T.month} <b>{n(option.service_start_month,0)}</b></span>;}
function DetailReturn({to,label}:{to:string;label:string}){return <a className="text-button" href={to}>{label}<ArrowRight size={18} aria-hidden="true"/></a>;}

function CompletionInclusion({stage}:{stage:string}){
 const {T,readingRoute}=useDossier(),relation=completionRelation(stage);
 if(readingOrigin(readingRoute)!=='project')return <small className="eco-inclusion">{T.reading_scope.initial_separate}</small>;
 return relation?<small className="eco-inclusion">{T.reading_notes.completion[relation]}</small>:null;
}
function ComparativeConclusion({reading,horizon}:{reading:Data;horizon:number}){
 const {T,options}=useDossier(),labels=T.reading_notes,facts=comparisonTakeaways(options.map((o:Option)=>o.stack),reading.options,horizon);
 if(options.length<2)return null;
 const name=(stack:string)=>options.find((o:Option)=>o.stack===stack)?.name;
 return <Note title={reading.editorial.sponsor.insight}><p className="eco-caption">{labels.summary_scope}</p>{facts.java&&<p><b>{name('java-spring')}</b> {labels.java[facts.java]}</p>}{facts.microsoft&&<p><b>{name('microsoft')}</b> {labels.microsoft_spending[facts.microsoft.spending]} {labels.microsoft_timing[facts.microsoft.timing]}</p>}{facts.sap&&<p><b>{name('sap')}</b> {labels.sap[facts.sap]} {labels.sap_scope}</p>}</Note>;
}
function ScopeForDecision({reading,option}:{reading:Data;option?:string}){
 const {options}=useDossier(),S=reading.editorial.sponsor;
 return <section className="eco-section eco-decision-scope"><h2>{S.scope_title}</h2><div>{S.scope_rows.filter((row:Data)=>row.id!=='sap'||(option?option==='sap':options.some((o:Option)=>o.stack==='sap'))).map((row:Data)=><article key={row.id}><h3>{row.title}</h3><p>{row.text}</p><small>{row.action}</small></article>)}</div></section>;
}
function FundingDecision({reading}:{reading:Data}){
 const S=reading.editorial.sponsor.decision;
 return <aside className="eco-decision"><h2>{S.title}</h2><p><b>{S.intro}</b></p><ul>{S.items.map((item:string)=><li key={item}>{item}</li>)}</ul><p>{S.budget}</p><a href={S.href}>{S.link} →</a></aside>;
}
function AnnualTrajectory({option,horizon,reading}:{option:Option;horizon:number;reading:Data}){
 const {T}=useDossier(),{amount}=useFormat(),S=reading.editorial.sponsor,detail=reading.options.find((o:Data)=>o.stack===option.stack);
 const rows=option.annual.filter(row=>row.annee<=horizon),max=Math.max(...rows.map(row=>row.total));
 const parts=[['build',T.initial_duration],['integration',T.integration],['mco_run',T.ongoing]] as const;
 return <section className="eco-section"><h2>{S.trajectory}</h2><p>{S.trajectory_note}</p><p className="eco-caption"><b>{T.service_start} <CalendarValue option={option}/></b></p><div className="eco-chart-legend">{parts.map(([key,label])=><span key={key}><i className={'eco-segment-'+key} aria-hidden="true"/>{label}</span>)}</div><ol className="eco-year-chart">{rows.map(row=><li key={row.annee} data-stage={detail.annual.projected_stages.find((stage:Data)=>stage.year===row.annee).stage}><span>{T.year} {row.annee}<small className="eco-period-bounds">{T.month} {(row as Data).start_month}–{(row as Data).end_month}</small></span><div role="img" aria-label={parts.map(([key,label])=>label+' · '+amount(row[key])).join(' · ')} style={{width:row.total/max*100+'%'}}>{parts.map(([key])=><i key={key} className={'eco-segment-'+key} style={{width:row.total?row[key]/row.total*100+'%':'0%'}}/>)}</div><strong>{amount(row.total)}</strong></li>)}</ol></section>;
}
function Determinants({reading}:{reading:Data}){
 const {T,options}=useDossier(),{n}=useFormat(),S=reading.editorial.sponsor,java=options.find((o:Option)=>o.stack==='java-spring')!,core=reading.options.find((o:Data)=>o.stack===java.stack).core;
 return <section className="eco-section eco-determinants"><h2>{S.determinant_title}</h2><p>{S.determinant_note}</p><div>{S.determinants.map((row:Data)=><article key={row.id}><header><h3>{row.title}</h3><span>{row.status}</span></header>{row.id==='calendar'&&<strong><CalendarValue option={java}/></strong>}{row.id==='core'&&<strong>{n(core.total_jh,0)} {T.jh} · {core.units.length} {S.lots}</strong>}{row.id==='service'&&<strong>{n(reading.drivers.perimeter.utilisateurs_nominatifs,0)} {S.users}</strong>}<p>{row.text}</p></article>)}</div></section>;
}
function EconomicComparisonPageContent({route}:{route:EconomicRoute}){
 const {T,data,options:originalOptions,link}=useDossier(),{amount,money,n,annualAmount}=useFormat(),{reading,error,retry}=useEconomicReading(),horizon=period(route),S=reading?.editorial.sponsor;
 const options=reading?originalOptions.map((o:Option)=>periodOption(o,reading,route)!).filter(Boolean):[];
 const result=(o:Option)=>o.horizons.find(h=>h.years===horizon)!;
 const detail=(o:Option)=>reading!.options.find((row:Data)=>row.stack===o.stack);
 if(!reading)return <Dossier route={route}><Loading error={error} retry={retry}/></Dossier>;
 return <Dossier route={route}>
 <div className="eco-comparison-cards eco-summary-cards">{options.map((o:Option)=><article key={o.stack} className={'eco-option-card eco-'+o.stack} data-economic-option={o.stack}><header><span className="eco-mode">{o.mode}</span><h2>{o.name}</h2></header><p className="eco-total-label">{T.reading_scope.period_costs} · {horizon} {horizon===1?T.reading_scope.one_year:T.years}</p><strong className="eco-total"><span>{money(result(o).totals.total)}</span><small>{data.ui.labels.money_unit}</small></strong>{S&&reading&&<div className="eco-card-funding"><span>{S.completion}</span><b>{money(detail(o).service_completion.total_eur_ht)}<small>{data.ui.labels.money_unit}</small></b><CompletionInclusion stage={result(o).stage}/></div>}<p className="eco-service"><CalendarDays size={16} aria-hidden="true"/><span>{T.service_start}<br/><CalendarValue option={o}/><small>{T.service_years} · {n(result(o).service_years,1)} {T.years}</small></span></p><PeriodBounds option={o} horizon={horizon}/><ReadingContext option={o}/><a href={link('evaluation-core',o.stack,String(horizon))}>{T.read_costs}<ArrowRight size={15} aria-hidden="true"/></a></article>)}</div>
 {S?<><aside className="eco-reading-rule"><b>{T.reading_notes.non_additive}</b><p>{S.completion_note}</p></aside><p className="eco-caption">{S.scope_short}</p><ComparativeConclusion reading={reading!} horizon={horizon}/>
 <section className="eco-section"><h2>{S.funding_and_annual}</h2><ComparisonTable names={options.map((o:Option)=>o.name)} label={S.funding_and_annual}><Matrix label={S.annual_base} values={options.map((o:Option)=>annualAmount(detail(o).annual.total_eur_ht))}/><Matrix label={T.reading_scope.period_year+' '+horizon} values={options.map((o:Option)=><><b>{amount(o.annual.find(row=>row.annee===horizon)!.total)}</b><small>{S.stages[detail(o).annual.projected_stages.find((row:Data)=>row.year===horizon).stage]}</small><small className="eco-inclusion">{T.reading_notes.annual}</small></>)}/></ComparisonTable><p className="eco-caption">{T.reading_notes.annual_base}</p><p className="eco-caption">{S.annual_pair_note}</p></section>
 <section className="eco-section"><h2>{S.compare_parts} · {horizon} {T.years}</h2><p>{S.compare_parts_note}</p><ComparisonTable names={options.map((o:Option)=>o.name)} label={S.compare_parts}>{[['build',S.acquisition],['integration',T.integration],['mco_run',T.ongoing]].map(([key,label])=><Matrix key={key} label={label} values={options.map((o:Option)=>amount(result(o).totals[key as 'build'|'integration'|'mco_run']))}/>)}<Matrix label={S.difference} values={options.map((o:Option)=>o.stack==='java-spring'?<small>{S.reference_option}</small>:<><b>{amount(detail(o).comparison.horizons.find((row:Data)=>row.years===horizon).amount_eur_ht)}</b><small>{S.difference_labels[detail(o).comparison.horizons.find((row:Data)=>row.years===horizon).direction]}</small></>)}/></ComparisonTable><div className="eco-option-drivers">{options.map((o:Option)=><article key={o.stack}><h3>{o.name}</h3><p>{S.drivers[o.stack]}</p></article>)}</div></section>
 <details className="eco-detail"><summary>{S.budgets_detail}</summary><p>{T.initial_note}</p><ComparisonTable names={options.map((o:Option)=>o.name)} label={T.initial_title}><Matrix label={T.initial_duration} values={options.map((o:Option)=>amount(o.obtention))}/><Matrix label={T.integration} values={options.map((o:Option)=>amount(o.integration))}/><Matrix label={T.remaining} values={options.map((o:Option)=>amount(result(o).remaining))}/></ComparisonTable><p>{T.remaining_note}</p></details>
 <ScopeForDecision reading={reading!}/><p className="eco-caption">{T.price_basis}</p><FundingDecision reading={reading!}/></>:<Loading error={error} retry={retry}/>}
 </Dossier>;
}
function useEconomicReading(){
 const {data,readingRoute}=useDossier();const [reading,setReading]=useState<Data|null>(null),[error,setError]=useState(''),[attempt,setAttempt]=useState(0);
 useEffect(()=>{let live=true;if(data.content.economic_zone_reading){setReading(data.content.economic_zone_reading);setError('');return()=>{live=false;};}setReading(null);setError('');request<Data>('/api/economic-evaluations?model_version='+encodeURIComponent(data.model_version)).then(value=>{if(value.model_version!==data.model_version)throw Error('ERR_VERSION');if(live)setReading(value);}).catch(reason=>{if(live)setError(reason?.message==='ERR_VERSION'?'version':'network');});return()=>{live=false;};},[data.model_version,data.content.economic_zone_reading,attempt]);
 const scoped:Data|null=reading?{...reading,options:reading.options.map((option:Data)=>{
  const selected=reading.periods.find((row:Data)=>row.stack===option.stack).periods.find((row:Data)=>row.anchor===readingOrigin(readingRoute));
  return {...option,spending_bridge:selected.horizons,comparison:{reference:'java-spring',horizons:selected.horizons.map((row:Data)=>({years:row.years,...row.comparison}))},annual:{...option.annual,projected_stages:selected.annual.map((row:Data)=>({year:row.annee,stage:row.stage}))}};
 })}:null;
 return {reading:scoped,error,retry:()=>setAttempt(i=>i+1)};
}
function Loading({error,retry}:{error:boolean|string;retry:()=>void}){const {data}=useDossier(),version=error==='version';return <div className="eco-loading" role={error?'alert':'status'}><p>{version?data.ui.server_update.message:error?data.ui.errors.network:data.ui.labels.loading}</p>{error&&<button className="text-button" onClick={version?()=>window.location.reload():retry}>{version?data.ui.server_update.action:data.ui.labels.retry}</button>}</div>;}
function Breakdown({option,horizon}:{option:Option;horizon:number}){
 const {T}=useDossier(),{amount}=useFormat(),result=option.horizons.find(h=>h.years===horizon)!;
 const rows=[['build','acquisition',T.initial_duration],['integration','integration',T.integration],['mco_run','fonctionnement',T.ongoing]];
 return <div className="eco-breakdown">{rows.map(([key,phase,label])=><div key={key}><div className="eco-breakdown-label"><PhaseIcon phase={phase} size={20}/><span>{label}</span></div><strong>{amount(result.totals[key as 'build'|'integration'|'mco_run'])}</strong><div className={'eco-bar eco-bar-'+phase} style={{width:Math.max(0,result.totals[key as 'build'|'integration'|'mco_run']/result.totals.total*100)+'%'}}/></div>)}</div>;
}
function InitialDetails({option,reading,route}:{option:Option;reading:Data;route:EconomicRoute}){
 const {T,link}=useDossier(),{amount,n,dailyRate}=useFormat(),units=reading.core?.units||[];
 const selected=route.family?units.find((u:Data)=>u.id===route.family):null;
 return <section className="eco-section"><h2>{T.initial_detail}</h2><div className="eco-initial-grid"><article><h3>{T.initial_duration}</h3><strong>{amount(option.obtention)}</strong><p>{n(option.initial_months,0)} {T.months}</p><ProofLink phase="acquisition" route={{...route,option:option.stack}}>{T.proof}</ProofLink></article><article><h3>{T.integration}</h3><strong>{amount(reading.integration.budget_eur_ht)}</strong><p>{n(reading.integration.months,0)} {T.months}</p><ProofLink phase="integration" route={{...route,option:option.stack}}>{T.proof}</ProofLink></article><article className="eco-transformation-budget"><h3>{T.transformation_title}</h3><strong>{amount(reading.transformation.budget_eur_ht)}</strong><p>{T.transformation_included}</p><a href={link('parametres',option.stack,String(period(route)),{focus:'programme'})}>{T.transformation_details} →</a></article></div><p className="eco-caption">{T.initial_note}</p>
  {option.mode==='Buy'?<p>{T.selection_note}</p>:<details className="eco-detail" open={selected?true:undefined}><summary>{T.core_detail}</summary><p>{T.units_note}</p>{(selected?[selected]:units).map((unit:Data)=><details className="eco-unit" key={unit.id} open={selected?true:undefined}><summary id={"economic-lot-"+unit.id}><span>{unit.label}</span><b>{amount(unit.cost_eur_ht)}</b></summary><dl className="eco-unit-facts"><div><dt>{T.effort}</dt><dd>{n(unit.total_jh,0)} {T.jh}</dd></div><div><dt>{T.labour}</dt><dd>{amount(unit.labour_eur_ht)}</dd></div><div><dt>{T.tooling}</dt><dd>{amount(unit.tooling_eur_ht)}</dd></div></dl><div className="eco-role-head" aria-hidden="true"><span>{T.roles}</span><span>{T.effort}</span><span>{T.rate}</span><span>{T.amount}</span></div>{unit.roles.map((role:Data)=><dl className="eco-role-row" key={role.id}><dt>{role.label}</dt><dd><span className="eco-mobile-label">{T.effort}</span>{n(role.jh,0)} {T.jh}</dd><dd><span className="eco-mobile-label">{T.rate}</span>{dailyRate(role.rate_eur_jh)}</dd><dd><span className="eco-mobile-label">{T.amount}</span>{amount(role.labour_eur_ht)}</dd></dl>)}<ProofLink phase="acquisition" route={{...route,option:option.stack}} focus={unit.id}>{T.proof}</ProofLink></details>)}</details>}
  <details className="eco-detail"><summary>{T.integration_detail}</summary>{reading.integration.offer_bridge&&<><h3>{T.bridge}</h3><p>{T.bridge_sources[option.stack]}</p><dl className="eco-money-lines">{Object.entries(reading.integration.offer_bridge).filter(([,value])=>value!==0).map(([key,value])=><div key={key}><dt>{T.bridge_labels[key]}</dt><dd>{amount(value as number)}</dd></div>)}</dl><p>{T.bridge_note}</p></>}<h3>{T.period}</h3><dl className="eco-money-lines">{reading.integration.detail.map((row:Data)=><div key={row.id}><dt>{row.label}<small>{T.month} {n(row.start,0)}–{n(row.end,0)}</small></dt><dd>{amount(row.amount)}</dd></div>)}</dl><p className="eco-caption">{T.timing_note}{option.stack==='microsoft'&&<> {T.microsoft_support_timing}</>}</p></details>
 </section>;
}
function AnnualDetails({option,reading,route}:{option:Option;reading:Data;route:EconomicRoute}){
 const {T}=useDossier(),{annualAmount}=useFormat();
 return <section className="eco-section"><h2>{T.annual}</h2><strong className="eco-annual-total">{annualAmount(reading.annual.total_eur_ht)}</strong><p className="eco-caption">{T.reading_notes.annual_base}</p><p>{T.annual_note}</p><details className="eco-detail"><summary>{reading.sponsor.annual_parts}</summary><dl className="eco-money-lines">{reading.rows.map((row:Data)=><div key={row.id}><dt>{row.label}<small>{row.explanation}</small></dt><dd>{reading.annual.items[row.id]===null?T.not_applicable:annualAmount(reading.annual.items[row.id])}</dd></div>)}</dl>{option.mode==='Buy'&&<p className="eco-caption">{T.buy_note}</p>}<details className="eco-detail"><summary>{T.annual_detail}</summary>{reading.annual.breakdown.filter((group:Data)=>group.items.length).map((group:Data)=><section key={group.id}><h3>{group.titre}</h3><p>{group.explication}</p><dl className="eco-money-lines">{group.items.map((row:Data)=><div key={row.id}><dt>{row.nom}</dt><dd>{annualAmount(row.montant)}</dd></div>)}</dl><p className="eco-subtotal"><b>{annualAmount(group.total)}</b></p></section>)}</details></details><ProofLink phase="fonctionnement" route={{...route,option:option.stack}}>{T.proof}</ProofLink></section>;
}
function ExpertReading({view,focus}:{view:string;focus?:string}){
 const {T}=useDossier(),context=useContext(ReadingScopeContext);if(view==='transpositions')return <><Note title={T.summary_compare}><p>{T.projects_note}</p></Note><p>{T.projects_use}</p><div className="eco-evidence-links"><a href="#preetude-projets">{T.projects_link} →</a><a href={'#charges-integration?'+new URLSearchParams({option:'java-spring',...economicReadingContext(context)}).toString()}>{T.proof} →</a></div></>;
 return <FundingReading focus={focus}/>;
}
function FundingReading({focus}:{focus?:string}){
 const {data}=useDossier(),{reading,error,retry}=useMarketReading();
 return reading?.comparison?<MarketComparison comparison={{...reading.comparison,budget_review:visibleBudgetReview(data.ui,reading.comparison.budget_review)}} focus={focus}/>:<Loading error={error} retry={retry}/>;
}
function EconomicCostsPageContent({route}:{route:EconomicRoute}){
 const {T,options,link}=useDossier(),{amount,n}=useFormat(),{reading,error,retry}=useEconomicReading(),original=options.find((o:Option)=>o.stack===route.option)||options[0],option=reading?periodOption(original,reading,route)!:original,horizon=period(route),result=reading?option.horizons.find((h:Data)=>h.years===horizon)!:null;
 const detail=reading?.options.find((o:Data)=>o.stack===option.stack);
 useEffect(()=>{if(!detail||['financements','transpositions'].includes(route.view||''))return;const id=route.family?'economic-lot-'+route.family:route.focus==='economic-expert'?'economic-expert':null;if(!id)return;const target=document.getElementById(id);target?.focus({preventScroll:true});target?.scrollIntoView({block:'start',behavior:'auto'});},[route.family,route.focus,route.view,Boolean(detail)]);
 const expert=['financements','transpositions'].includes(route.view||'');
 const S=reading?.editorial.sponsor,annual=option.annual.find(row=>row.annee===horizon)!;
 if(!reading||!result)return <Dossier route={route}><Loading error={error} retry={retry}/></Dossier>;
 return <Dossier route={route}>{expert?<><DetailReturn to={link('evaluation-core',option.stack,String(horizon),{family:route.family,focus:route.focus})} label={T.back}/><section className="eco-section"><h2>{route.view==='transpositions'?T.transpositions:T.funding}</h2><ExpertReading view={route.view!} focus={route.focus}/></section></>:<><OptionChoice route={route}/><PeriodBounds option={option} horizon={horizon}/><ReadingContext option={option}/>
 <section className="eco-cost-overview"><article><h2>{T.reading_scope.period_costs} · {horizon} {horizon===1?T.reading_scope.one_year:T.years}</h2><strong>{amount(result.totals.total)}</strong><small>{T.service_years} · {n(result.service_years,1)} {T.years}</small></article>{detail&&S?<><article><h2>{S.completion}</h2><strong>{amount(detail.service_completion.total_eur_ht)}</strong><small>{T.service_start} <CalendarValue option={option}/></small><CompletionInclusion stage={result.stage}/></article><article><h2>{T.reading_scope.period_year} {horizon}</h2><strong>{amount(annual.total)}</strong><small>{S.stages[detail.annual.projected_stages.find((row:Data)=>row.year===horizon).stage]}</small><small className="eco-inclusion">{T.reading_notes.annual}</small></article></>:<Loading error={error} retry={retry}/>}</section>
 {S&&<><aside className="eco-reading-rule"><b>{T.reading_notes.non_additive}</b><p>{S.completion_note}</p></aside><p className="eco-caption">{S.scope_short}</p></>}
 <TeamAllocationCosts option={option.stack}/>
 <section className="eco-section"><h2>{T.decomposition}</h2><Breakdown option={option} horizon={horizon}/>{S&&<p>{S.drivers[option.stack]}</p>}</section>
 {detail&&S&&reading?<><AnnualTrajectory option={option} horizon={horizon} reading={reading}/><details className="eco-detail" open={route.family?true:undefined}><summary>{S.budgets_detail}</summary><InitialDetails option={option} reading={detail} route={route}/><dl className="eco-money-lines"><div><dt>{T.remaining}</dt><dd>{amount(result.remaining)}</dd></div></dl><p className="eco-caption">{T.remaining_note}</p></details>
 <details className="eco-detail"><summary>{S.completion_detail}</summary><dl className="eco-money-lines"><div><dt>{S.initial_ledger}</dt><dd>{amount(detail.service_completion.initial_eur_ht)}</dd></div><div><dt>{S.subscriptions}</dt><dd>{amount(detail.service_completion.subscriptions_eur_ht)}</dd></div></dl><p>{S.completion_note}</p></details>
 <details className="eco-detail"><summary>{T.ongoing_bridge}</summary><dl className="eco-money-lines"><div><dt>{T.transition_cost}</dt><dd>{amount(detail.spending_bridge.find((h:Data)=>h.years===horizon).transition_eur_ht)}</dd></div><div><dt>{T.recurring_cost}</dt><dd>{amount(detail.spending_bridge.find((h:Data)=>h.years===horizon).recurring_eur_ht)}</dd></div></dl><p>{T.ongoing_bridge_note}</p></details>
 <AnnualDetails route={route} option={option} reading={{...detail,sponsor:S,rows:reading.editorial.sections.annual.rows}}/>
 <details className="eco-detail"><summary>{T.spending}</summary><p>{T.spending_note}</p><table className="eco-annual-table"><caption className="sr-only">{T.spending}</caption><thead><tr><th scope="col">{T.year}</th><th scope="col">{T.initial_duration}</th><th scope="col">{T.integration}</th><th scope="col">{T.ongoing}</th><th scope="col">{T.year_total}</th></tr></thead><tbody>{option.annual.filter(row=>row.annee<=horizon).map(row=><tr key={row.annee}><th scope="row">{row.annee}<small className="eco-period-bounds">{T.month} {(row as Data).start_month}–{(row as Data).end_month}</small></th><td>{amount(row.build)}</td><td>{amount(row.integration)}</td><td>{amount(row.mco_run)}</td><td><b>{amount(row.total)}</b></td></tr>)}</tbody></table><p className="eco-caption">{S.annual_pair_note}</p></details><ScopeForDecision reading={reading} option={option.stack}/><p className="eco-caption">{T.price_basis}</p></>:!detail&&<Loading error={error} retry={retry}/>}
 <section className="eco-section" id="economic-expert" tabIndex={-1}><h2>{T.expert}</h2><div className="eco-evidence-links"><a href={link('evaluation-core',option.stack,'financements',{horizon:String(horizon),family:route.family,focus:route.focus||'economic-expert'})}>{T.funding} →</a><a href={link('evaluation-core',option.stack,'transpositions',{horizon:String(horizon),family:route.family,focus:route.focus||'economic-expert'})}>{T.transpositions} →</a></div></section></>}</Dossier>;
}
function EconomicAssumptionsPageContent({route}:{route:EconomicRoute}){
 const {T,data,options,link}=useDossier(),{n,amount,dailyRate,annualAmount}=useFormat(),F=data.content.framework,{reading,error,retry}=useEconomicReading();
 const rates=F.tariffs.filter((row:Data)=>options.some((o:Option)=>o.stack===row.key));
 const selected=route.option||options[0].stack;
 const governance=data.ui.essential.application_framework.hypotheses.sections.find((section:Data)=>section.id==='coordination');
 useDossierFocus(route.focus==='programme'?'economic-programme':undefined);
 return <Dossier route={route}><p className="eco-caption">{T.fixed}</p>
 <section className="eco-section" id="economic-programme" tabIndex={-1}><h2>{governance.title}</h2>{governance.paragraphs.map((text:string)=><p key={text}><MethodText>{text}</MethodText></p>)}
 <table className="eco-table"><caption>{F.transformation.nom}</caption><thead><tr><th>{T.transformation_role}</th><th>{T.transformation_daily}</th><th>{T.transformation_annual}</th></tr></thead><tbody>{F.transformation.roles.map((role:Data)=><tr key={role.id}><th scope="row">{role.nom}<small>{role.mission}</small></th><td>{dailyRate(role.tarif_eur_jh)}</td><td>{annualAmount(role.annuel_eur_ht)}</td></tr>)}<tr><th scope="row">{T.transformation_total}</th><td></td><td><b>{annualAmount(F.transformation.annuel_eur_ht)}</b></td></tr></tbody></table><p>{F.transformation.calendrier}</p><a href="#preetude-couts?focus=rates-transformation">{data.ui.essential.market_costs.transformation_title} →</a>
 <details className="eco-detail"><summary>{T.coordination}</summary><p>{T.coordination_note}</p><dl className="eco-money-lines">{Object.keys(T.coordination_labels).filter(key=>key!=='build_pct').map(key=><div key={key}><dt>{T.coordination_labels[key]}</dt><dd>{n(F.pilotage.rates[key],0)} %</dd></div>)}</dl><p>{F.pilotage.rates.assiette}</p></details>
 <ProofLink phase="acquisition" route={route} focus={selected==='java-spring'?'roles':undefined}>{T.governance_charges}</ProofLink></section>
 {reading?<Determinants reading={reading}/>:<Loading error={error} retry={retry}/>}
 <section className="eco-section"><h2>{T.calendars}</h2><ComparisonTable names={options.map((o:Option)=>o.name)} label={T.compare}><Matrix label={T.initial_duration} values={options.map((o:Option)=>n(o.initial_months,0)+' '+T.months)}/><Matrix label={T.integration_duration} values={options.map((o:Option)=>reading?n(reading.options.find((r:Data)=>r.stack===o.stack).integration.months,0)+' '+T.months:data.ui.labels.loading)}/><Matrix label={T.service_start} values={options.map((o:Option)=><CalendarValue option={o}/>)}/></ComparisonTable>{!reading&&<Loading error={error} retry={retry}/>}<p>{T.calendar_fixed}</p><p className="eco-caption">{T.service_note}</p></section>
 <section className="eco-section" id="economic-tariffs"><h2>{T.tariffs}</h2><p>{data.ui.essential.market_costs.price_financial_intro}</p><ProjectRateStudy financial zone={route.zone||'paris'} focus={route.focus?.startsWith('prices-')?route.focus:undefined}/></section>
 <section className="eco-section"><h2>{T.indexation}</h2><p>{T.indexation_note}</p><p>{T.indexation_timing}</p><div className="eco-indexation">{F.inflation.map((row:Data)=><article key={row.key}><h3>{row.label}</h3><strong>{n(row.value*100,1)} %</strong><p>{row.influence}</p><details className="eco-detail"><summary>{T.source_method}</summary><p>{row.method.split(';').join('. ')}</p><p>{row.limit.split(';').join('. ')}</p><ul className="eco-evidence-links">{row.evidence.map((e:Data)=><li key={e.id}><SourceLink path={e.path}>{e.title}</SourceLink></li>)}</ul></details></article>)}</div></section>
 <section className="eco-section"><h2>{T.dimensions}</h2><p>{T.dimensions_note}</p>{reading?<dl className="eco-driver-grid">{Object.entries(T.dimension_labels).map(([key,label])=><div key={key}><dt>{label as string}</dt><dd>{n(reading.drivers.perimeter[key]??reading.drivers.annual_volumes[key],0)}</dd></div>)}</dl>:<Loading error={error} retry={retry}/>}<p className="eco-caption">{T.service_scope}</p></section>
 <details className="eco-detail"><summary>{T.gains}</summary><p>{T.gains_note}</p><ComparisonTable names={options.map((o:Option)=>o.name)} label={T.gains}>{F.workload.maintenance_ia[selected].map((activity:Data)=><Matrix key={activity.id} label={activity.label} values={options.map((o:Option)=>{const row=F.workload.maintenance_ia[o.stack].find((r:Data)=>r.id===activity.id);return row.traitement==='estimation'?n(row.taux_pct,0)+' %':T.gains_included;})}/>)}</ComparisonTable></details>
 <details className="eco-detail"><summary>{T.purchases}</summary><p>{T.purchase_note}</p><dl className="eco-money-lines">{F.other.filter((row:Data)=>row.status==='retained').map((row:Data)=><div key={row.key}><dt>{T.purchase_labels[row.key]||row.key}<small>{T.purchase_scopes[row.key]}</small></dt><dd>{row.unit==='daily'?dailyRate(row.value):row.unit==='annual'?annualAmount(row.value):n(row.value,0)+' '+T.jh}</dd></div>)}</dl></details>
 <details className="eco-detail"><summary>{T.licences}</summary><p>{T.licences_note}</p>{options.filter((o:Option)=>o.mode==='Buy').map((o:Option)=><section key={o.stack}><h3>{o.name}</h3><p>{T.subscription_start} · {T.month} {n(o.selection_months,0)}</p><dl className="eco-money-lines">{o.editor_prices.map((value:number,i:number)=><div key={i}><dt>{T.sequence} {i+1}</dt><dd>{amount(value)}</dd></div>)}</dl></section>)}</details>
 <details className="eco-detail" open={route.detail==='diagnostics'?true:undefined}><summary>{T.technical}</summary><p>{T.technical_note}</p><div className="eco-evidence-links">{['acquisition','integration','fonctionnement'].map(phase=><a key={phase} href={'#charges-'+phase+'?'+new URLSearchParams({option:selected,...economicReadingContext(route),returnTo:'parametres'}).toString()}>{data.ui.essential.nav.find((nav:Data)=>nav.id==='charges-'+phase).label} →</a>)}</div></details>
 </Dossier>;
}

function PeriodBounds({option,horizon}:{option:Option;horizon:number}){
 const {T}=useDossier(),result=option.horizons.find(row=>row.years===horizon) as Data;
 return <small className="eco-period-bounds">{T.reading_scope.period_span} · {T.month} {result.start_month}–{result.end_month}</small>;
}

export function EconomicComparisonPage({route}:{route:EconomicRoute}){return <FinancialZone route={route}><EconomicComparisonPageContent route={route}/></FinancialZone>;}

export function EconomicCostsPage({route}:{route:EconomicRoute}){return <FinancialZone route={route}><EconomicCostsPageContent route={route}/></FinancialZone>;}

export function EconomicAssumptionsPage({route}:{route:EconomicRoute}){return <FinancialZone route={route}><EconomicAssumptionsPageContent route={route}/></FinancialZone>;}
