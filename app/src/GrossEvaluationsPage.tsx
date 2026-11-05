import {ReadingScopeContext,useReadingContext} from './ReadingScopeContext';
import {IntegrationUnits} from './IntegrationUnits';
import {useContext,useEffect,useId,useRef,useState} from 'react';
import {ArrowRight,Info} from 'lucide-react';
import {request,useStudy,useFormat,type Data} from './context';
import {DossierSheet,useDossierFocus} from './Dossier';
import {PhaseOptionNavigation} from './PhaseOptionNavigation';
import {MethodText} from './MethodDocument';
import {Drawer,SourceLink} from './components';
import {economicHash,phaseReadingHash} from './economicNavigation';
import './frameworkJourney.css';
import './grossEvaluations.css';

const Text=({text}:{text:string})=><p><MethodText>{text}</MethodText></p>;

function Takeaway({summary,labels:L}:{summary:string;labels:Data}){
 return <aside className="gross-summary"><h3>{L.summary}</h3><Text text={summary}/></aside>;
}

function UnitAnalysis({row,labels:L}:{row:Data;labels:Data}){
 const {n}=useFormat();
 const a=row.detail.analysis,m=row.detail.analysis_metrics;
 return <section className="gross-unit-analysis" aria-label={L.analysis_title+' · '+row.label}>
  <h4>{L.analysis_title}</h4><div className="gross-analysis-finding"><Text text={a.finding}/></div>
  {row.detail.work_packages.length>0&&<section><h5>{L.work_package_title}</h5><Text text={L.work_package_note}/><table className="core-method-table"><thead><tr><th scope="col">{L.lot}</th><th scope="col">{L.workload+' · '+L.jh}</th><th scope="col">{L.work_package_scope}</th></tr></thead><tbody>{row.detail.work_packages.map((w:Data)=><tr key={w.id}><th scope="row">{w.label}</th><td>{n(w.jh,0)}</td><td><Text text={w.scope}/><small>{L.work_package_reuse}</small><Text text={w.reuse}/></td></tr>)}</tbody></table></section>}
  {row.detail.functional_retained||row.detail.work_packages.length>0?<dl className="gross-analysis-metrics"><div><dt>{L.analysis_cfp}</dt><dd>{n(m.CFP,0)} {L.analysis_cfp_unit}</dd></div><div><dt>{L.analysis_functional}</dt><dd>{n(m.cosmic_jh,1)} {L.jh}</dd></div></dl>:<dl className="gross-analysis-metrics">
   <div><dt>{L.analysis_cfp}</dt><dd>{n(m.CFP,0)} {L.analysis_cfp_unit}</dd></div>
   <div><dt>{L.analysis_raw}</dt><dd>{n(m.reference_jh,1)} {L.jh}</dd></div>
   <div><dt>{L.analysis_functional}</dt><dd>{n(m.cosmic_jh,1)} {L.jh}</dd></div>
   <div><dt>{L.analysis_gap}</dt><dd>{n(Math.abs(m.gap_jh),1)} {L.jh} · {n(Math.abs(m.gap_pct),1)} % {m.gap_jh<0?L.analysis_lower:L.analysis_higher}</dd></div>
   <div><dt>{L.analysis_implied}</dt><dd>{n(m.implied_hours_per_CFP,1)} {L.analysis_hours_unit}</dd></div>
  </dl>}
  {!row.detail.functional_retained&&row.detail.work_packages.length===0&&<p className="gross-analysis-note">{L.analysis_ratio_note}</p>}
  {(['oss','cosmic','decision','remaining'] as const).map(key=><section key={key}><h5>{L['analysis_'+key]}</h5><Text text={a[key]}/></section>)}
 </section>;
}

function RetainedEffortInfo({row,labels:L}:{row:Data;labels:Data}){
 const {n}=useFormat();
 const id=useId(),button=useRef<HTMLButtonElement>(null),tip=useRef<HTMLSpanElement>(null);
 const hide=()=>{if(tip.current?.matches(':popover-open'))tip.current.hidePopover();};
 const show=()=>{
  const element=tip.current,trigger=button.current;
  if(!element||!trigger)return;
  if(!element.matches(':popover-open'))element.showPopover();
  const anchor=trigger.getBoundingClientRect(),box=element.getBoundingClientRect();
  element.style.left=Math.max(12,Math.min(innerWidth-box.width-12,anchor.left-box.width/2+anchor.width/2))+'px';
  element.style.top=Math.max(12,anchor.bottom+box.height+8<innerHeight?anchor.bottom+8:anchor.top-box.height-8)+'px';
 };
 useEffect(()=>{
  const reposition=()=>{if(tip.current?.matches(':popover-open'))show();};
  window.addEventListener('scroll',reposition,true);
  window.addEventListener('resize',hide);
  return()=>{window.removeEventListener('scroll',reposition,true);window.removeEventListener('resize',hide);};
 },[]);
 return <span className="gross-charge-help" onMouseEnter={show} onMouseLeave={hide}>
  <button ref={button} type="button" className="gross-charge-info" aria-label={L.effort_info+' · '+row.label}
   aria-describedby={id} onFocus={show} onBlur={hide} onClick={show}><Info size={17} aria-hidden="true"/></button>
  <span ref={tip} id={id} role="tooltip" popover="auto" className="gross-charge-tooltip">
   <strong>{n(row.adopted_jh,0)} {L.jh} · {row.detail.work_packages.length
    ?L.effort_deliverables.replace('{count}',n(row.detail.work_packages.length,0))
    :row.detail.method}</strong>
   <span><MethodText>{row.detail.analysis.decision}</MethodText></span>
  </span>
 </span>;
}

function CoreResults({core,labels:L,focus}:{core:Data;labels:Data;focus?:string}){
 const {n}=useFormat(),context=useReadingContext();
 const selected=core.rows.find((row:Data)=>row.id===focus);
 const href=(id?:string)=>phaseReadingHash({...context,page:'charges-acquisition',option:'java-spring',focus:id})!;
 return <div className="gross-development">
  <Text text={L.development_intro}/>
  <section className="gross-metric gross-adopted" data-core-status={core.status}>
   <h3>{L.development_total}</h3><p><strong>{n(core.adopted_jh,0)}</strong> {L.jh}</p>
  </section>
  <p className="gross-development-scope">{L.development_scope}</p>
  <section id="gross-focus-roles" tabIndex={-1} className="gross-activities">
   <h3>{L.activity_breakdown}</h3>
   <table className="core-method-table gross-activity-table" aria-label={L.activity_breakdown}>
    <thead><tr><th scope="col">{L.activity_column}</th><th scope="col">{L.effort_column}</th></tr></thead>
    <tbody>{core.activities.map((activity:Data)=><tr key={activity.id}><th scope="row">{activity.label}</th><td>{n(activity.jh,1)}</td></tr>)}</tbody>
   </table>
   <p className="gross-development-note">{L.activity_note}</p>
  </section>
  <section id="gross-focus-comparisons" tabIndex={-1}>
   <h3 id="gross-lots" tabIndex={-1}>{L.feature_breakdown}</h3>
   <p className="gross-development-note">{L.effort_comparison_note}</p>
   <div className="gross-comparison-scroll" role="region" aria-label={L.feature_breakdown} tabIndex={0}>
    <table className="core-method-table gross-comparison-matrix gross-effort-matrix" aria-label={L.feature_breakdown}>
     <thead><tr><th scope="col">{L.feature_column}</th><th scope="col">{L.effort_retained}</th>{core.rows[0].comparisons.map((ref:Data)=><th scope="col" key={ref.id}>{ref.label}<small>{ref.label===ref.method?L.jh:ref.method+' · '+L.jh}</small></th>)}</tr></thead>
     <tbody>{core.rows.map((row:Data)=><tr key={row.id} id={'gross-focus-'+row.id} data-unit={row.id}>
      <th scope="row"><a href={href(row.id)}>{row.label}</a></th>
      <td className="gross-retained-effort"><strong>{n(row.adopted_jh,0)}</strong><RetainedEffortInfo row={row} labels={L}/></td>
      {row.comparisons.map((ref:Data)=><td key={ref.id}>{ref.jh===null?L.unknown:n(ref.jh,1)}</td>)}
     </tr>)}</tbody>
     <tfoot><tr><th scope="row">{L.total}</th><td className="gross-retained-effort">{n(core.adopted_jh,0)}</td>
      {core.comparison_totals.map((total:Data)=><td key={total.id}>{total.jh===null?L.unknown:n(total.jh,1)}</td>)}
     </tr></tfoot>
    </table>
   </div>
  </section>
  {selected&&<Drawer title={selected.label} onClose={()=>{location.hash=href('comparisons');}} wide>
   <p><strong>{n(selected.adopted_jh,0)} {L.jh}</strong> · {selected.detail.method}</p>
   <Text text={selected.detail.analysis.decision}/>
   <details className="gross-detail"><summary>{L.effort_detail}</summary>
    <UnitAnalysis row={selected} labels={L}/>
    <h3>{L.included}</h3><ul>{selected.detail.includes.map((text:string)=><li key={text}>{text}</li>)}</ul>
    {selected.detail.excludes.length>0&&<><h3>{L.excluded}</h3><ul>{selected.detail.excludes.map((text:string)=><li key={text}>{text}</li>)}</ul></>}
   </details>
   <SourceLink path={selected.detail.proof.path}>{L.calculation_proof}</SourceLink>
  </Drawer>}
 </div>;
}

function WorkGroups({groups,labels:L,focus}:{groups:Data[];labels:Data;focus?:string}){
 const {n,amount,annualAmount}=useFormat();
 const value=(row:Data)=>row.value===null?L.unknown:row.unit===L.euro?amount(row.value):row.unit===L.annual_euro?annualAmount(row.value):`${n(row.value,Number.isInteger(row.value)?0:1)} ${row.unit}`;
 return <>{groups.map(group=>{const hasProof=(row:Data)=>Boolean(row.factors||row.terms||row.context||row.exclusions||(row.note&&![group.note,L.initial,L.annual_reference].includes(row.note)));const withDetails=group.rows.some(hasProof);return <section className="gross-group" key={group.id} data-gross-group={group.id}><h3>{group.title}{group.subtotal_jh!==undefined&&<span className="gross-subtotal">{n(group.subtotal_jh,0)} {L.jh}</span>}</h3>{group.note&&<Text text={group.note}/>}<table className={'core-method-table gross-work '+(withDetails?'gross-with-details':'gross-values-only')} aria-label={group.title}><thead><tr><th scope="col">{L.item}</th><th scope="col">{L.workload+' / '+L.amount}</th>{withDetails&&<th scope="col">{L.details}</th>}</tr></thead><tbody>{group.rows.map((row:Data)=><tr key={row.id}><th scope="row">{row.label}</th><td className="gross-work-value">{value(row)}</td>{withDetails&&<td>{hasProof(row)&&<details className="gross-row-proof" id={'gross-focus-'+row.id} tabIndex={-1} open={focus===row.id||undefined}><summary>{L.basis}</summary>{row.note!==group.note&&<Text text={row.note}/>} {row.context&&<Text text={row.context}/>} {row.exclusions&&<><h4>{L.excluded}</h4><Text text={row.exclusions}/></>}{row.factors&&<><dl>{row.factors.map((factor:Data)=><div key={factor.label}><dt>{factor.label}</dt><dd>{n(factor.value,Number.isInteger(factor.value)?0:2)}</dd></div>)}</dl><p className="gross-formula">{row.factors.map((factor:Data,index:number)=><span key={factor.label}>{index>0&&<> × </>}{n(factor.value,Number.isInteger(factor.value)?0:2)}</span>)} = {value(row)}</p></>}{row.terms&&<><dl>{row.terms.map((term:Data)=><div key={term.label}><dt>{term.label}</dt><dd>{n(term.quantity,0)} × {n(term.unit_jh,Number.isInteger(term.unit_jh)?0:6)} {L.jh}{term.note&&<Text text={term.note}/>}</dd></div>)}{row.fixed_jh>0&&<div><dt>{L.fixed}</dt><dd>{n(row.fixed_jh,0)} {L.jh}</dd></div>}</dl></>}</details>}</td>}</tr>)}</tbody></table></section>;})}</>;
}

function Quotes({quotes,phase,labels:L}:{quotes:Data[];phase:string;labels:Data}){
 const {amount,annualAmount,n}=useFormat();
 if(!quotes.length)return null;
 return <section className="gross-quotes"><h3>{L.original_quotes}</h3><Text text={L.quote_note}/>{quotes.map(quote=><article className="gross-quote" key={quote.id} data-quote={quote.id}><h4>{quote.title}</h4><p className="gross-quote-status"><strong>{quote.status}</strong></p><Text text={quote.scope}/>{quote.entries.map((entry:Data)=>{
  const sequence:Data[]=[];
  for(const year of entry.amounts||[]){const last=sequence.at(-1);if(last&&last.amount===year.amount_eur&&last.end+1===year.year)last.end=year.year;else sequence.push({start:year.year,end:year.year,amount:year.amount_eur});}
  return <section key={entry.source_id} className="gross-quote-entry"><h5>{entry.label}</h5><p>{entry.period}</p>{entry.source_year&&<p className="gross-source-date">{L.source_year+' '+entry.source_year}</p>}{entry.amount_eur!==undefined?<strong>{amount(entry.amount_eur)}</strong>:<dl className="gross-price-sequence">{sequence.map(year=><div key={year.start}><dt>{(year.end!==year.start?L.years:L.year)+' '+n(year.start,0)+(year.end!==year.start?' '+L.year_to+' '+n(year.end,0):'')}</dt><dd>{phase==='fonctionnement'?annualAmount(year.amount):amount(year.amount)}</dd></div>)}</dl>}</section>;
 })}</article>)}</section>;
}

export function GrossEvaluationsPage({phase,option,focus,returnTo,horizon,onChoose}:{phase:string;option?:string;focus?:string;returnTo?:string;horizon?:string;onChoose:(id:string)=>void}){
 const {data}=useStudy(),{n}=useFormat(),J=data.ui.essential.framework_vision.journey;
 const scope=useContext(ReadingScopeContext),context=useReadingContext();
 const current=J.options.find((o:Data)=>o.id===option)||J.options[0];
 const [reading,setReading]=useState<Data|null>(null),[error,setError]=useState(''),[retry,setRetry]=useState(0);
 const heading=useRef<HTMLHeadingElement>(null),previous=useRef(current.id);
 const focusedUnit=reading?.phases[phase]?.options[current.id]?.core?.rows.some((row:Data)=>row.id===focus);
 useDossierFocus(reading&&focus&&!focusedUnit?(focus==='lots'?'gross-lots':'gross-focus-'+focus):undefined);
 useEffect(()=>{if(previous.current!==current.id){heading.current?.focus({preventScroll:true});previous.current=current.id;}},[current.id]);
 useEffect(()=>{
  let active=true;if(data.content.gross_zone_reading){setReading(data.content.gross_zone_reading);setError('');return()=>{active=false;};}setReading(null);setError('');
  request<Data>(`/api/gross-evaluations?model_version=${encodeURIComponent(data.model_version)}`).then(result=>{
   if(result.model_version!==data.model_version)throw Object.assign(new Error('version'),{code:'version'});
   if(active)setReading(result);
  }).catch(reason=>{if(active)setError(reason.code==='version'?'version':'network');});
  return()=>{active=false;};
 },[data.model_version,data.content.gross_zone_reading,retry]);
 if(error)return <div className="essential-page" role="alert"><p>{error==='version'?data.ui.server_update.message:data.ui.errors.network}</p><button type="button" className="text-button" onClick={()=>error==='version'?window.location.reload():setRetry(value=>value+1)}>{error==='version'?data.ui.server_update.action:data.ui.labels.retry}</button></div>;
 if(!reading)return <p role="status">{data.ui.labels.loading}</p>;
 const L=reading.labels,P=reading.phases[phase],R=P.options[current.id],index=J.phases.findIndex((p:Data)=>p.id===phase),next=J.phases[index+1];
 const proofs=[...new Map<string,Data>(R.quotes.flatMap((q:Data)=>q.proofs).map((proof:Data)=>[proof.path,proof] as [string,Data])).values()];
 return <div className="essential-page framework-journey gross-evaluations" data-gross-phase={phase}>
  <>{returnTo&&<a className="text-button" href={returnTo}>{returnTo.startsWith('#parametres')?data.ui.essential.economic_dossier.return_assumptions:data.ui.essential.economic_dossier.back} →</a>}</><PhaseOptionNavigation journey={J} phase={phase} option={current.id} onChoose={onChoose} prefix="charges-" horizon={horizon}/>
  {phase==='integration'&&current.id!=='java-spring'&&<Quotes quotes={R.quotes} phase={phase} labels={L}/>}
  <DossierSheet view={phase+'-'+current.id}><h2 ref={heading} tabIndex={-1} className="gross-option-heading" hidden={Boolean(R.core)}>{current.label}</h2>
   <div className="gross-reading-links"><a className="text-button" href={phaseReadingHash({...context,page:phase,option:current.id,horizon})!}>{L.method}<ArrowRight size={16} aria-hidden="true"/></a><a href="#glossaire?term=charge_brute">{L.glossary}</a></div>
   {R.core?<CoreResults core={R.core} labels={L} focus={focus}/>:<>{R.total_jh!==null?<div className="gross-metrics"><section className="gross-metric gross-adopted"><h3>{R.total_label}</h3><p><strong>{n(R.total_jh,Number.isInteger(R.total_jh)?0:1)}</strong> {R.total_unit}</p></section></div>:<p className="gross-unknown-human">{L.unknown_human}</p>}<Takeaway summary={R.summary} labels={L}/>{R.scope&&<Text text={R.scope}/>}</>}
   <WorkGroups groups={R.groups} labels={L} focus={focus}/>
   {!R.core&&R.remaining.length>0&&<section className="gross-gap-reviews"><h3>{L.remaining}</h3>{R.remaining.map((item:Data)=><article key={item.id}><h4>{item.label}</h4><Text text={item.scope}/><p><strong>{L.unknown}</strong></p><Text text={item.proof_to_price}/></article>)}</section>}
   {phase==='integration'&&reading.integration_units&&<IntegrationUnits grid={reading.integration_units}/>}
   {phase!=='integration'&&<Quotes quotes={R.quotes} phase={phase} labels={L}/>}
   {!R.core&&R.construction.length>0&&<details className="gross-detail gross-construction"><summary>{L.assumptions}</summary>{R.construction.map((text:string)=><Text key={text} text={text}/>)}</details>}
   {!R.core&&<section className="gross-proofs"><h3>{L.evidence}</h3><ul>{proofs.map(proof=><li key={proof.path}><SourceLink path={proof.path}>{proof.short_label||proof.label}</SourceLink></li>)}<li><a className="text-button" href="#telechargements">{L.audit_link}</a></li></ul></section>}
  </DossierSheet>
  <a className="framework-phase-next text-button" href={next?phaseReadingHash({...context,page:'charges-'+next.id,returnTo:scope.returnTo,family:scope.family,option:current.id,horizon})!:phaseReadingHash({...context,page:'organisation-delivery',option:current.id,horizon})!}>{next?J.labels.next+' · '+next.title:data.ui.essential.pages['organisation-delivery'].title}<ArrowRight size={18} aria-hidden="true"/></a>
 </div>;
}
