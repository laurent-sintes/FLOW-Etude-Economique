import {ReadingScopeContext,useReadingContext} from './ReadingScopeContext';
import {useContext,useEffect,useRef,useState} from 'react';
import {ArrowRight} from 'lucide-react';
import {request,useStudy,useFormat,type Data} from './context';
import {DossierSheet,useDossierFocus} from './Dossier';
import {PhaseOptionNavigation} from './PhaseOptionNavigation';
import {MethodText} from './MethodDocument';
import {ReadingNote} from './ReadingNote';
import {SourceLink} from './components';
import {economicHash,phaseReadingHash} from './economicNavigation';
import './frameworkJourney.css';
import './grossEvaluations.css';

const Text=({text}:{text:string})=><p><MethodText>{text}</MethodText></p>;

function Takeaway({summary,labels:L}:{summary:string;labels:Data}){
 return <aside className="gross-summary"><h3>{L.summary}</h3><Text text={summary}/></aside>;
}

function CoreResults({core,labels:L,focus,summary}:{core:Data;labels:Data;focus?:string;summary:string}){
 const {n}=useFormat();
 const signed=(value:number)=>`${value>0?'+':''}${n(value,0)}`;
 const context=useReadingContext();
 const href=(id:string)=>phaseReadingHash({...context,page:'charges-acquisition',option:'java-spring',focus:id})!;
 return <>
  <div className="gross-metrics" data-core-status={core.status}><section className="gross-metric gross-adopted"><h3>{L.adopted}</h3><p><strong>{n(core.adopted_jh,0)}</strong> {L.jh}</p></section></div>
  <Takeaway summary={summary} labels={L}/><Text text={L.reference_note}/>
  <details className="gross-detail"><summary>{L.roles}</summary><dl className="gross-role-values">{core.roles.map((role:Data)=><div key={role.id}><dt>{role.label}</dt><dd>{n(role.jh,0)} {L.jh}</dd></div>)}</dl></details>
  <h3 id="gross-lots" tabIndex={-1}>{L.breakdown}</h3>
  <table className="core-method-table gross-adopted-lots" aria-label={L.breakdown}><thead><tr><th scope="col">{L.lot}</th><th scope="col">{L.adopted+' · '+L.jh}</th></tr></thead><tbody>{core.rows.map((row:Data)=><tr key={row.id} data-unit={row.id}><th scope="row"><a href={href(row.id)}>{row.label}</a></th><td>{n(row.adopted_jh,0)}</td></tr>)}</tbody><tfoot><tr><th scope="row">{L.total}</th><td>{n(core.adopted_jh,0)}</td></tr></tfoot></table>
  <section className="gross-unit-proofs"><h3>{L.details}</h3>{core.rows.map((row:Data)=><details className="gross-detail" key={row.id} id={'gross-focus-'+row.id} tabIndex={-1} open={focus===row.id||undefined}><summary>{row.label}</summary><p>{L.decision_date+' '}<time dateTime={row.detail.date}>{row.detail.date}</time> · <strong>{n(row.adopted_jh,0)} {L.jh}</strong></p><div className="gross-scope-columns"><section><h4>{L.included}</h4><ul>{row.detail.includes.map((text:string)=><li key={text}>{text}</li>)}</ul></section><section><h4>{L.excluded}</h4><ul>{row.detail.excludes.map((text:string)=><li key={text}>{text}</li>)}</ul></section></div><h4>{L.roles}</h4><dl className="gross-role-values">{row.detail.roles.map((role:Data)=><div key={role.id}><dt>{role.label}</dt><dd>{n(role.jh,0)} {L.jh}</dd></div>)}</dl><h4>{L.reference_proof}</h4><Text text={row.detail.explanation}/><ReadingNote>{L.calculation_origin_note}</ReadingNote><SourceLink path={row.detail.proof.path}>{L.calculation_proof}</SourceLink><p><a className="text-button" href={href('lots')}>{L.back_lots}</a></p></details>)}</section>
  <details className="gross-detail gross-proposal" id="gross-focus-proposal" tabIndex={-1} open={focus==='proposal'||undefined}><summary>{L.proposal_open}</summary><p>{L.proposal_date+' '}<time dateTime={core.date}>{core.date}</time></p><ReadingNote title={L.proposed}>{L.no_adoption}</ReadingNote>
   <div className="gross-metrics"><section className="gross-metric gross-proposed"><h4>{L.proposed}</h4><p><strong>{n(core.proposal_jh,0)}</strong> {L.jh}</p></section><section className="gross-metric gross-difference"><h4>{L.difference}</h4><p><strong>{signed(core.delta_jh)}</strong> {L.jh}</p></section></div>
   <table className="core-method-table gross-lots" aria-label={L.proposal_open}><thead><tr>{[L.lot,L.adopted,L.proposed,L.difference].map((label:string)=><th scope="col" key={label}>{label}</th>)}</tr></thead><tbody>{core.rows.map((row:Data)=><tr key={row.id}><th scope="row">{row.label}</th><td data-label={L.adopted}>{n(row.adopted_jh,0)}</td><td data-label={L.proposed}>{n(row.proposal_jh,0)}</td><td data-label={L.difference}>{signed(row.delta_jh)}</td></tr>)}</tbody><tfoot><tr><th scope="row">{L.total}</th><td data-label={L.adopted}>{n(core.adopted_jh,0)}</td><td data-label={L.proposed}>{n(core.proposal_jh,0)}</td><td data-label={L.difference}>{signed(core.delta_jh)}</td></tr></tfoot></table>
   <h3>{L.rationale}</h3><div className="gross-arbitrations">{core.rows.map((row:Data)=><article key={row.id}><h4>{row.label}</h4><Text text={row.rationale}/></article>)}</div>
   <SourceLink path={core.proof.path}>{L.calculation_proof}</SourceLink>
  </details>
  <details className="gross-detail"><summary>{L.reference_comparison}</summary><Text text={L.comparison_note}/><table className="core-method-table gross-references" aria-label={L.reference_comparison}><thead><tr><th scope="col">{L.lot}</th>{core.rows[0].references.map((ref:Data)=><th scope="col" key={ref.id}>{ref.label}</th>)}</tr></thead><tbody>{core.rows.map((row:Data)=><tr key={row.id}><th scope="row">{row.label}</th>{row.references.map((ref:Data)=><td data-label={ref.label} key={ref.id}>{n(ref.jh,1)} {L.jh}</td>)}</tr>)}</tbody></table></details>
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
  <DossierSheet view={phase+'-'+current.id}><h2 ref={heading} tabIndex={-1} className="gross-option-heading">{current.label}</h2>
   <div className="gross-reading-links"><a className="text-button" href={phaseReadingHash({...context,page:phase,option:current.id,horizon})!}>{L.method}<ArrowRight size={16} aria-hidden="true"/></a><a href="#glossaire?term=charge_brute">{L.glossary}</a></div>
   {R.core?<CoreResults core={R.core} labels={L} focus={focus} summary={R.summary}/>:<>{R.total_jh!==null?<div className="gross-metrics"><section className="gross-metric gross-adopted"><h3>{R.total_label}</h3><p><strong>{n(R.total_jh,Number.isInteger(R.total_jh)?0:1)}</strong> {R.total_unit}</p></section></div>:<p className="gross-unknown-human">{L.unknown_human}</p>}<Takeaway summary={R.summary} labels={L}/>{R.scope&&<Text text={R.scope}/>}</>}
   <WorkGroups groups={R.groups} labels={L} focus={focus}/>
   <Quotes quotes={R.quotes} phase={phase} labels={L}/>
   {R.construction.length>0&&<details className="gross-detail gross-construction"><summary>{L.assumptions}</summary>{R.construction.map((text:string)=><Text key={text} text={text}/>)}</details>}
   <section className="gross-proofs"><h3>{L.evidence}</h3><ul>{proofs.map(proof=><li key={proof.path}><SourceLink path={proof.path}>{proof.short_label||proof.label}</SourceLink></li>)}<li><a className="text-button" href="#telechargements">{L.audit_link}</a></li></ul></section>
  </DossierSheet>
  <a className="framework-phase-next text-button" href={next?phaseReadingHash({...context,page:'charges-'+next.id,returnTo:scope.returnTo,family:scope.family,option:current.id,horizon})!:economicHash({...context,page:'evaluation-core',option:current.id,horizon})!}>{next?J.labels.next+' · '+next.title:L.more_results}<ArrowRight size={18} aria-hidden="true"/></a>
 </div>;
}
