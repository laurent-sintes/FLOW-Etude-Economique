import {ReadingScopeContext,useReadingContext} from './ReadingScopeContext';
import {IntegrationUnits} from './IntegrationUnits';
import {useContext,useEffect,useRef,useState} from 'react';
import {ArrowRight} from 'lucide-react';
import {request,useStudy,useFormat,type Data} from './context';
import {DossierSheet,useDossierFocus} from './Dossier';
import {PhaseOptionNavigation} from './PhaseOptionNavigation';
import {MethodText} from './MethodDocument';
import {SourceLink} from './components';
import {economicHash,phaseReadingHash} from './economicNavigation';
import './frameworkJourney.css';
import './grossEvaluations.css';

const Text=({text}:{text:string})=><p><MethodText>{text}</MethodText></p>;

function Takeaway({summary,labels:L}:{summary:string;labels:Data}){
 return <aside className="gross-summary"><h3>{L.summary}</h3><Text text={summary}/></aside>;
}

function UnitComparisons({row,labels:L}:{row:Data;labels:Data}){
 const {n,amount}=useFormat();
 return <table className="core-method-table gross-unit-comparisons" aria-label={L.reference_comparison+' · '+row.label}><thead><tr><th scope="col">{L.comparison_reference}</th><th scope="col">{L.workload+' · '+L.jh}</th><th scope="col">{L.comparison_cost}</th></tr></thead><tbody>{row.comparisons.map((ref:Data)=><tr key={ref.id}><th scope="row">{ref.label}<small>{ref.method}</small></th><td>{ref.jh===null?L.unknown:n(ref.jh,1)+' '+L.jh}</td><td>{ref.cost_eur_ht===null?L.unknown:amount(ref.cost_eur_ht)}</td></tr>)}</tbody></table>;
}
function ComparisonMatrix({core,labels:L}:{core:Data;labels:Data}){
 const {n,amount}=useFormat(),context=useReadingContext();
 return <section className="gross-comparison-section" id="gross-focus-comparisons" tabIndex={-1}><h3>{L.reference_comparison}</h3><Text text={L.comparison_note}/><Text text={L.comparison_pricing_note}/><Text text={L.analysis_revision_note}/><aside className="gross-analysis-priorities"><h4>{L.analysis_priorities}</h4><Text text={L.analysis_priority_note}/><ul>{core.analysis_order.slice(0,3).map((id:string)=><li key={id}><a href={phaseReadingHash({...context,page:'charges-acquisition',option:'java-spring',focus:id})!}>{core.rows.find((row:Data)=>row.id===id).label}</a></li>)}</ul></aside><div className="gross-comparison-scroll" role="region" aria-label={L.reference_comparison} tabIndex={0}><table className="core-method-table gross-comparison-matrix"><thead><tr><th scope="col">{L.lot}</th><th scope="col">{L.retained_estimate}</th>{core.rows[0].comparisons.map((ref:Data)=><th scope="col" key={ref.id}>{ref.label}<small>{ref.method}</small></th>)}</tr></thead><tbody>{core.rows.map((row:Data)=><tr key={row.id}><th scope="row"><a href={phaseReadingHash({...context,page:'charges-acquisition',option:'java-spring',focus:row.id})!}>{row.label}</a></th><td><strong>{amount(row.adopted_cost_eur_ht)}</strong><small>{n(row.adopted_jh,0)} {L.jh}</small></td>{row.comparisons.map((ref:Data)=><td key={ref.id}><strong>{ref.cost_eur_ht===null?L.unknown:amount(ref.cost_eur_ht)}</strong><small>{ref.jh===null?L.unknown:n(ref.jh,1)+' '+L.jh}</small></td>)}</tr>)}</tbody></table></div><Text text={L.comparison_cosmic_note}/><Text text={L.analysis_shared}/></section>;
}

function ScopeRevision({revision:r,labels:L}:{revision:Data;labels:Data}){
 const {n,amount}=useFormat();
 return <section className="gross-unit-revision" aria-label={L.scope_revision_title}>
  <h4>{L.scope_revision_title}</h4><p><strong>{n(r.jh,0)} {L.jh} · {amount(r.cost_eur_ht)}</strong></p>
  <Text text={L.scope_revision_note}/>{r.supersedes_policy_revision&&<Text text={L.scope_revision_supersedes}/>}
  <dl className="gross-analysis-metrics"><div><dt>{L.revision_delta}</dt><dd>+{n(r.delta_jh,0)} {L.jh} · +{amount(r.delta_cost_eur_ht)}</dd></div><div><dt>{L.scope_revision_cfp}</dt><dd>{n(r.baseline_CFP,0)} → {n(r.total_CFP,0)} {L.analysis_cfp_unit}</dd></div></dl>
  <p className="gross-formula">{n(r.total_CFP,0)} {L.analysis_cfp_unit} × {n(r.hours_per_CFP,0)} {L.analysis_hours_unit} ÷ {n(r.day_hours,0)} {L.revision_day_unit} = {n(r.raw_jh,1)} {L.jh}</p>
  <Text text={r.assessment}/><Text text={L.scope_revision_reuse}/>
  <table className="core-method-table"><thead><tr><th scope="col">{L.scope_revision_functions}</th><th scope="col">{L.analysis_cfp_unit}</th></tr></thead><tbody>{r.processes.map((p:Data)=><tr key={p.id}><th scope="row">{p.label}</th><td>{n(p.CFP,0)}</td></tr>)}</tbody></table>
  <SourceLink path={r.proof.path}>{L.calculation_proof}</SourceLink>
 </section>;
}
function ScopeRevisionSummary({revision:r,labels:L}:{revision:Data;labels:Data}){
 const {n,amount}=useFormat(),context=useReadingContext();
 return <section className="gross-unit-revision" id="gross-focus-scope-revision" tabIndex={-1}>
  <h3>{L.scope_revision_title}</h3><p><strong>{n(r.jh,0)} {L.jh} · {amount(r.cost_eur_ht)}</strong></p><p>+{n(r.delta_jh,0)} {L.jh} · +{amount(r.delta_cost_eur_ht)}</p><Text text={L.scope_revision_note}/>
  <table className="core-method-table"><thead><tr><th scope="col">{L.lot}</th><th scope="col">{L.scope_revision_adopted}</th><th scope="col">{L.scope_revision_proposed}</th></tr></thead><tbody>{r.rows.map((row:Data)=><tr key={row.id}><th scope="row"><a href={phaseReadingHash({...context,page:'charges-acquisition',option:'java-spring',focus:row.id})!}>{row.label}</a></th><td>{n(row.baseline_jh,0)}</td><td>{n(row.jh,0)}</td></tr>)}</tbody></table>
 </section>;
}

function UnitRevision({revision:r,labels:L}:{revision:Data;labels:Data}){
 const {n,amount}=useFormat();
 if(r.kind==='scenario_scope')return <ScopeRevision revision={r} labels={L}/>;
 return <section className="gross-unit-revision" aria-label={L.revision_title}>
  <h4>{L.revision_title}</h4><p><strong>{n(r.jh,0)} {L.jh} · {amount(r.cost_eur_ht)}</strong></p><Text text={L.revision_status}/>
  <dl className="gross-analysis-metrics"><div><dt>{L.revision_delta}</dt><dd>+{n(r.delta_jh,0)} {L.jh} · +{amount(r.delta_cost_eur_ht)}</dd></div><div><dt>{L.revision_core}</dt><dd>{n(r.core_candidate_jh,0)} {L.jh}</dd></div><div><dt>{L.revision_policy}</dt><dd>{n(r.replaced_CFP,0)} → {n(r.policy_CFP,0)} {L.analysis_cfp_unit}</dd></div><div><dt>{L.revision_preserved}</dt><dd>{n(r.kept_CFP,0)} {L.analysis_cfp_unit}</dd></div></dl>
  <p className="gross-formula">({n(r.policy_CFP,0)} + {n(r.kept_CFP,0)}) {L.analysis_cfp_unit} × {n(r.hours_per_CFP,0)} {L.analysis_hours_unit} ÷ {n(r.day_hours,0)} {L.revision_day_unit} = {n(r.raw_jh,1)} {L.jh}</p>
  <Text text={r.assessment}/><Text text={L.revision_reuse}/>
  <table className="core-method-table gross-revision-processes" aria-label={L.revision_functions}><thead><tr><th scope="col">{L.revision_functions}</th><th scope="col">{L.analysis_cfp_unit}</th></tr></thead><tbody>{r.processes.map((p:Data)=><tr key={p.id}><th scope="row">{p.label}<small>{p.reason}</small></th><td>{n(p.CFP,0)} {L.analysis_cfp_unit}</td></tr>)}</tbody></table><SourceLink path={r.proof.path}>{L.calculation_proof}</SourceLink>
 </section>;
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

function CoreResults({core,labels:L,focus,summary,horizon}:{core:Data;labels:Data;focus?:string;summary:string;horizon?:string}){
 const {n,amount}=useFormat();
 const context=useReadingContext();
 const href=(id:string)=>phaseReadingHash({...context,page:'charges-acquisition',option:'java-spring',focus:id})!;
 const lotNames=Object.fromEntries(core.rows.map((row:Data)=>[row.id,row.label]));
 const governanceHref=economicHash({...context,page:'parametres',option:'java-spring',horizon,focus:'programme'})!;
 return <>
  <div className="gross-completeness" data-core-status={core.status}><section className="gross-metric gross-adopted"><h3>{L.current_estimate}</h3><p><strong>{n(core.adopted_jh,0)}</strong> {L.jh}</p><Text text={L.professional_note}/><a href={href('lots')}>{L.breakdown}</a><br/><a href={href('comparisons')}>{L.reference_comparison}</a></section><section className="gross-missing"><h3>{L.missing}</h3><p><strong>{L.incomplete}</strong></p><ul>{core.priority_gaps.map((gap:Data)=><li key={gap.id}><a href={href('gaps')}>{gap.title}</a></li>)}<li><a href={governanceHref}>{L.transformation_short}</a></li></ul><Text text={L.missing_summary}/><a href={href('gaps')}>{L.show_remaining}</a></section></div>
  {core.revision_summary&&<ScopeRevisionSummary revision={core.revision_summary} labels={L}/>}
  <Takeaway summary={summary} labels={L}/><Text text={L.reference_note}/>
  <details className="gross-detail gross-roles" id="gross-focus-roles" tabIndex={-1} open><summary>{L.roles}</summary><dl className="gross-role-values">{core.roles.map((role:Data)=><div key={role.id}><dt>{role.label}</dt><dd>{n(role.jh,0)} {L.jh}</dd></div>)}</dl>
   <h4>{L.programme_roles}</h4><p>{L.programme_financed}</p><a href={governanceHref}>{L.governance_assumptions}</a>
   <h4>{L.transformation}</h4><Text text={L.transformation_note}/><ul>{core.transformation_items.map((item:Data)=><li key={item.id}><strong>{item.label}</strong></li>)}</ul><a className="text-button" href={governanceHref}>{L.governance_assumptions}</a>
  </details>
  <h3 id="gross-lots" tabIndex={-1}>{L.breakdown}</h3>
  <table className="core-method-table gross-adopted-lots" aria-label={L.breakdown}><thead><tr><th scope="col">{L.lot}</th><th scope="col">{L.workload+' · '+L.jh}</th></tr></thead><tbody>{core.rows.map((row:Data)=><tr key={row.id} data-unit={row.id}><th scope="row"><a href={href(row.id)}>{row.label}</a></th><td>{n(row.adopted_jh,0)}</td></tr>)}</tbody><tfoot><tr><th scope="row">{L.total}</th><td>{n(core.adopted_jh,0)}</td></tr></tfoot></table>
  <ComparisonMatrix core={core} labels={L}/>
  <section className="gross-professional"><h3>{L.professional}</h3><Text text={L.professional_note}/><ul>{core.professional_functions.map((feature:Data)=><li key={feature.id}><strong>{feature.label}</strong><span>{feature.owners.map((id:string,index:number)=><span key={id}>{index>0&&' · '}<a href={href(id)}>{lotNames[id]}</a></span>)}</span></li>)}</ul></section>
  <section className="gross-gap-reviews" id="gross-focus-gaps" tabIndex={-1}><h3>{L.remaining}</h3><Text text={L.remaining_note}/>{core.gap_reviews.map((gap:Data)=><article key={gap.id} data-gap={gap.id}><h4>{gap.id+' · '+gap.title}</h4><p className="gross-gap-status"><strong>{gap.status}</strong></p><p><strong>{L.funded+' : '}</strong><MethodText>{gap.funded}</MethodText></p><p><strong>{L.residual+' : '}</strong><MethodText>{gap.residual}</MethodText></p><a className="text-button" href={economicHash({...context,page:'evaluation-core',option:'java-spring',view:'financements',focus:gap.id})!}>{L.gap_review}</a></article>)}</section>
  <section className="gross-unit-proofs"><h3>{L.analysis_details}</h3>{core.analysis_order.map((id:string)=>core.rows.find((row:Data)=>row.id===id)).map((row:Data)=><details className="gross-detail" key={row.id} id={'gross-focus-'+row.id} tabIndex={-1} open={focus===row.id||undefined}><summary>{row.label}</summary><p>{L.decision_date+' '}<time dateTime={row.detail.date}>{row.detail.date}</time> · <strong>{n(row.adopted_jh,0)} {L.jh} · {amount(row.adopted_cost_eur_ht)}</strong></p>{row.detail.revision&&<UnitRevision revision={row.detail.revision} labels={L}/>}<UnitComparisons row={row} labels={L}/><UnitAnalysis row={row} labels={L}/><div className="gross-scope-columns"><section><h4>{L.included}</h4>{row.detail.scope_note&&<Text text={row.detail.scope_note}/>}<ul>{row.detail.includes.map((text:string)=><li key={text}>{text}</li>)}</ul></section>{row.detail.excludes.length>0&&<section><h4>{L.excluded}</h4><ul>{row.detail.excludes.map((text:string)=><li key={text}>{text}</li>)}</ul></section>}</div><h4>{L.roles}</h4><dl className="gross-role-values">{row.detail.roles.map((role:Data)=><div key={role.id}><dt>{role.label}</dt><dd>{n(role.jh,0)} {L.jh}</dd></div>)}</dl><h4>{L.reference_proof}</h4><Text text={row.detail.explanation}/><SourceLink path={row.detail.proof.path}>{L.calculation_proof}</SourceLink><p><a className="text-button" href={href('lots')}>{L.back_lots}</a></p></details>)}</section>
  <section id="gross-focus-proposal" tabIndex={-1}><p>{L.adoption_note}</p><SourceLink path={core.proof.path}>{L.calculation_proof}</SourceLink></section>

 </>;
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
 useDossierFocus(reading&&focus?(focus==='lots'?'gross-lots':'gross-focus-'+focus):undefined);
 useEffect(()=>{if(previous.current!==current.id){heading.current?.focus({preventScroll:true});previous.current=current.id;}},[current.id]);
 useEffect(()=>{
  let active=true;setReading(null);setError('');
  request<Data>(`/api/gross-evaluations?model_version=${encodeURIComponent(data.model_version)}`).then(result=>{
   if(result.model_version!==data.model_version)throw Object.assign(new Error('version'),{code:'version'});
   if(active)setReading(result);
  }).catch(reason=>{if(active)setError(reason.code==='version'?'version':'network');});
  return()=>{active=false;};
 },[data.model_version,retry]);
 if(error)return <div className="essential-page" role="alert"><p>{error==='version'?data.ui.server_update.message:data.ui.errors.network}</p><button type="button" className="text-button" onClick={()=>error==='version'?window.location.reload():setRetry(value=>value+1)}>{error==='version'?data.ui.server_update.action:data.ui.labels.retry}</button></div>;
 if(!reading)return <p role="status">{data.ui.labels.loading}</p>;
 const L=reading.labels,P=reading.phases[phase],R=P.options[current.id],index=J.phases.findIndex((p:Data)=>p.id===phase),next=J.phases[index+1];
 const proofs=[...new Map<string,Data>(R.quotes.flatMap((q:Data)=>q.proofs).map((proof:Data)=>[proof.path,proof] as [string,Data])).values()];
 return <div className="essential-page framework-journey gross-evaluations" data-gross-phase={phase}>
  <>{returnTo&&<a className="text-button" href={returnTo}>{returnTo.startsWith('#parametres')?data.ui.essential.economic_dossier.return_assumptions:data.ui.essential.economic_dossier.back} →</a>}</><PhaseOptionNavigation journey={J} phase={phase} option={current.id} onChoose={onChoose} prefix="charges-" horizon={horizon}/>
  {phase==='integration'&&current.id!=='java-spring'&&<Quotes quotes={R.quotes} phase={phase} labels={L}/>}
  <DossierSheet view={phase+'-'+current.id}><h2 ref={heading} tabIndex={-1} className="gross-option-heading">{current.label}</h2>
   <div className="gross-reading-links"><a className="text-button" href={phaseReadingHash({...context,page:phase,option:current.id,horizon})!}>{L.method}<ArrowRight size={16} aria-hidden="true"/></a><a href="#glossaire?term=charge_brute">{L.glossary}</a></div>
   {R.core?<CoreResults core={R.core} labels={L} focus={focus} summary={R.summary} horizon={horizon}/>:<>{R.total_jh!==null?<div className="gross-metrics"><section className="gross-metric gross-adopted"><h3>{R.total_label}</h3><p><strong>{n(R.total_jh,Number.isInteger(R.total_jh)?0:1)}</strong> {R.total_unit}</p></section></div>:<p className="gross-unknown-human">{L.unknown_human}</p>}<Takeaway summary={R.summary} labels={L}/>{R.scope&&<Text text={R.scope}/>}</>}
   <WorkGroups groups={R.groups} labels={L} focus={focus}/>
   {!R.core&&R.remaining.length>0&&<section className="gross-gap-reviews"><h3>{L.remaining}</h3>{R.remaining.map((item:Data)=><article key={item.id}><h4>{item.label}</h4><Text text={item.scope}/><p><strong>{L.unknown}</strong></p><Text text={item.proof_to_price}/></article>)}</section>}
   {phase==='integration'&&reading.integration_units&&<IntegrationUnits grid={reading.integration_units}/>}
   {phase!=='integration'&&<Quotes quotes={R.quotes} phase={phase} labels={L}/>}
   {R.construction.length>0&&<details className="gross-detail gross-construction"><summary>{L.assumptions}</summary>{R.construction.map((text:string)=><Text key={text} text={text}/>)}</details>}
   <section className="gross-proofs"><h3>{L.evidence}</h3><ul>{proofs.map(proof=><li key={proof.path}><SourceLink path={proof.path}>{proof.short_label||proof.label}</SourceLink></li>)}<li><a className="text-button" href="#telechargements">{L.audit_link}</a></li></ul></section>
  </DossierSheet>
  <a className="framework-phase-next text-button" href={next?phaseReadingHash({...context,page:'charges-'+next.id,returnTo:scope.returnTo,family:scope.family,option:current.id,horizon})!:economicHash({...context,page:'evaluation-core',option:current.id,horizon})!}>{next?J.labels.next+' · '+next.title:L.more_results}<ArrowRight size={18} aria-hidden="true"/></a>
 </div>;
}
