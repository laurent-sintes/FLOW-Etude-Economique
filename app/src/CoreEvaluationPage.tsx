import {useState} from 'react';
import {useStudy,useFormat,type Data} from './context';
import {MethodText} from './MethodDocument';
import './coreEvaluation.css';

export function CalculationAlignment({unit}:{unit:Data}){
 const {n}=useFormat(),A=unit.alignment,L=A.labels;
 return <section className="calculation-alignment"><h4>{L.alignment}</h4>
  <p>{L.reference} : <strong>{A.reference_label} · {n(A.reference_jh,2)} {L.jh_unit}</strong></p>
  <div className="table-scroll"><table className="core-evaluation-table"><thead><tr><th>{L.candidate}</th><th>{L.effort}</th><th>{L.gap}</th><th>{L.relative_gap}</th></tr></thead>
   <tbody>{[...A.rows,A.functional].map((r:Data)=><tr key={r.id}><th scope="row">{r.label}</th><td>{n(r.jh,2)} {L.jh_unit}</td><td>{r.gap_jh===null?'—':n(r.gap_jh,2)} {L.jh_unit}</td><td>{r.gap_pct===null?'—':n(r.gap_pct,2)} {L.percent_unit}</td></tr>)}</tbody>
  </table></div>
  <p>{L.spread} : {n(A.spread_jh,2)} {L.jh_unit} · {n(A.spread_pct,2)} {L.percent_unit}</p>
  <p>{L.rounding} : {n(A.rounding_delta_jh,2)} {L.jh_unit}</p>
  <p><strong>{L.note}</strong></p><p>{A.limitations}</p>
  <p>{L.shared_assumptions} : <strong>{n(A.shared_complements_pct,1)} {L.percent_unit}</strong>. {L.shared_assumptions_note}</p>
  <h4>{L.comparison_matrix}</h4>
  <div className="table-scroll" tabIndex={0} role="region" aria-label={L.comparison_matrix}><table className="core-evaluation-table">
   <thead><tr><th>{L.comparison_subject}</th><th>{L.cocomo_column}</th><th>{L.cosmic_column}</th><th>{L.comparison_decision}</th></tr></thead>
   <tbody>{A.comparison.scope_rows.map((r:Data)=><tr key={r.id}><th scope="row">{r.label}</th><td>{r.cocomo}</td><td>{r.cosmic}</td><td>{r.decision}</td></tr>)}</tbody>
  </table></div>
  <h4>{L.preparation}</h4>
  <dl className="economic-value-summary">
   <div><dt>{L.recorded_files}</dt><dd>{n(unit.trace.recorded_files,0)}</dd></div>
   <div><dt>{L.complement_units}</dt><dd>{n(unit.trace.complement_units,1)}</dd></div>
   <div><dt>{L.cosmic_processes}</dt><dd>{n(unit.trace.processes,0)}</dd></div>
   <div><dt>{L.cosmic_points}</dt><dd>{n(unit.trace.CFP,0)}</dd></div>
  </dl>
  <h4>{L.funding}</h4><ul>{unit.funding.map((m:Data)=><li key={m.id}><strong>{m.label}</strong> — {m.note}</li>)}</ul>
  <p>{L.funding_owner} : {unit.label}</p>
  <h4>{L.consolidation}</h4><p>{unit.consolidation.note}</p>
 </section>;
}

export function RetainedCoreFamilies({units}:{units:Data[]}){
 const {data}=useStudy(),{n,amount}=useFormat(),R=data.ui.essential.core_results;
 return <>{units.map(unit=><section className="retained-core-family" key={unit.id} data-family={unit.id}>
  <h3>{unit.label}</h3>
  <dl className="economic-value-summary">
   <div><dt>{R.days}</dt><dd>{n(unit.total_jh,0)} {R.jh_unit}</dd></div>
   <div><dt>{R.duration}</dt><dd>{n(unit.months,0)} {R.months}</dd></div>
   <div><dt>{R.average_team}</dt><dd>{n(unit.schedule.average_fte,1)} {R.fte}</dd></div>
  </dl>
  <p>{unit.capabilities.map((c:Data)=>c.id).join(' · ')}</p>
  <p>{unit.schedule.explanation}</p>
  <p className="core-method-formula">{unit.schedule.formula} = {n(unit.schedule.unrounded_months,2)} {R.months}</p>
  <p>{R.role_note}</p>
  <div className="table-scroll" tabIndex={0} role="region" aria-label={R.role}>
   <table className="core-evaluation-table"><thead><tr><th scope="col">{R.role}</th><th scope="col">{R.days}</th><th scope="col">{R.rate}</th><th scope="col">{R.role_cost}</th></tr></thead>
    <tbody>{unit.roles.map((role:Data)=><tr key={role.id}><th scope="row">{role.label}</th><td className="number">{n(role.jh,0)} {R.jh_unit}</td><td className="number">{n(role.rate_eur_jh,0)} {R.rate_unit}</td><td className="number">{amount(role.labour_eur_ht)}</td></tr>)}</tbody>
    <tfoot><tr><th scope="row">{R.role_cost}</th><td className="number">{n(unit.total_jh,0)} {R.jh_unit}</td><td></td><td className="number">{amount(unit.labour_eur_ht)}</td></tr></tfoot>
   </table>
  </div>
  <p>{unit.role_assumption}</p><p>{R.rate_note}</p>
  <dl className="economic-value-summary"><div><dt>{R.tools} · {n(unit.tooling_eur_jh,0)} {R.rate_unit}</dt><dd>{amount(unit.tooling_eur_ht)}</dd></div><div><dt>{R.total}</dt><dd>{amount(unit.cost_eur_ht)}</dd></div></dl>
  <p>{R.tools_note}</p>
  <h4>{R.provenance}</h4><p><strong>{unit.method}</strong> · {unit.provenance.explanation}</p>
  <p>{R.crosscheck} : <strong>{n(unit.crosscheck.jh,0)} {R.jh_unit}</strong> · {unit.crosscheck.explanation}</p>
  <CalculationAlignment unit={unit}/>
  <h4>{R.uncertainty}</h4><p>{unit.uncertainty.explanation}</p>
  <h4>{R.assumptions}</h4><ul>{unit.assumptions.map((a:Data)=><li key={a.id}><p><strong>{a.hypothesis}</strong></p><p>{R.trigger} : {a.trigger}</p><p>{a.effect}</p></li>)}</ul>
  <h4>{R.includes}</h4><ul>{unit.includes.map((text:string)=><li key={text}>{text}</li>)}</ul>
  <h4>{R.excludes}</h4><ul>{unit.excludes.map((text:string)=><li key={text}>{text}</li>)}</ul>
 </section>)}</>;
}

export function CoreEvaluationResults({status,details=true}:{status?:Data;details?:boolean}){
 const {data}=useStudy(),{amount,n}=useFormat(),R=data.ui.essential.core_results;
 const rows=data.content.core_evaluation as Data[];
 const make=rows.filter(row=>row.mode==='Make'),notice=status||R.status;
 return <div className="core-evaluation-results">
   <p><MethodText>{R.make_note}</MethodText></p>
   <aside className="core-method-notice"><h3>{notice.title}</h3><p><MethodText>{notice.text}</MethodText></p></aside>
   <div className="table-scroll" tabIndex={0} role="region" aria-label={R.make_title}><table className="core-evaluation-table" data-evaluation="core"><thead><tr><th scope="col">{R.option}</th><th scope="col">{R.central}</th><th scope="col">{R.coverage}</th><th scope="col">{R.uncertainty}</th><th scope="col">{R.cost}</th></tr></thead><tbody>{make.map(row=><tr key={row.stack} data-option={row.stack}><th scope="row">{row.name}</th><td className="number">{row.coverage.covered?<>{n(row.ranges_jh.central,0)} {R.jh_unit}</>:R.pending}</td><td>{n(row.coverage.covered,0)} / {n(row.coverage.total,0)} · {n(row.coverage.covered_pct,1)} {R.percent_unit}<br/>{n(row.coverage.remaining,0)} {R.remaining.toLowerCase()}</td><td>{R.unknown_uncertainty}</td><td className="number"><strong>{row.coverage.covered?amount(row.build_eur_ht):R.pending}</strong></td></tr>)}</tbody></table></div>
   <p>{R.coverage_note}</p>
   <p className="core-evaluation-qualification"><MethodText>{R.qualification}</MethodText></p>
   {details&&<RetainedCoreFamilies units={make.flatMap(row=>row.units)}/>}
 </div>;
}

export function CoreEvaluationPage(){
 const {data}=useStudy(),R=data.ui.essential.core_results;
 const buy=(data.content.core_evaluation as Data[]).filter(row=>row.mode==='Buy');
 return <div className="essential-page core-evaluation-page">
  <section><h2>{R.make_title}</h2><CoreEvaluationResults/></section>
  <section className="core-method-note"><h2>{R.buy_title}</h2><p>{R.buy_note}</p><p>{buy.map(row=>row.name).join(' · ')}</p></section>
  <a className="text-button essential-structure-next" href="#comparer">{R.next} →</a>
 </div>;
}

export function CoreEvaluationTrace({options,editorial}:{options:Data[];editorial:Data}){
 const {data}=useStudy(),{amount}=useFormat(),L=editorial.labels,S=editorial.sections.core,R=data.ui.essential.core_results;
 const make=options.filter(option=>option.core),[stack,setStack]=useState(make[0].stack),[capacity,setCapacity]=useState(make[0].core.features[0].id);
 const current=make.find(option=>option.stack===stack)||make[0],core=current.core;
 const feature=core.features.find((row:Data)=>row.id===capacity)||core.features[0];
 return <div className="economic-trace core-work-trace" aria-labelledby="core-work-trace-title">
  <h3 id="core-work-trace-title">{S.title}</h3><p><MethodText>{S.lead}</MethodText></p>
  <label className="economic-trace-select">{L.choose_option}<select value={current.stack} onChange={event=>setStack(event.target.value)}>{make.map(option=><option key={option.stack} value={option.stack}>{option.name}</option>)}</select></label>
  <RetainedCoreFamilies units={core.units}/>
  {!core.units.length&&<p>{R.pending}</p>}
  <dl className="economic-value-summary"><div><dt>{L.core_work}</dt><dd>{amount(core.amounts.prestations)}</dd></div><div><dt>{L.core_coordination}</dt><dd>{amount(core.amounts.pilotage)}</dd></div><div><dt>{L.core_total}</dt><dd>{amount(core.total_eur_ht)}</dd></div></dl>
  <p><MethodText>{S.note}</MethodText></p>
  <h4>{L.capacity}</h4><p><MethodText>{S.capacity_note}</MethodText></p>
  <label className="economic-trace-select">{L.choose_capacity}<select value={feature.id} onChange={event=>setCapacity(event.target.value)}>{core.features.map((row:Data)=><option key={row.id} value={row.id}>{row.name}</option>)}</select></label>
  <article className="economic-capacity-work" aria-live="polite"><h4>{feature.name}</h4>{feature.definition&&<p>{feature.definition}</p>}<p><strong>{feature.retained_unit?R.no_allocation:R.unestimated_capacity}</strong></p>
   {feature.retained_unit&&<a href="#evaluation-core">{R.family_link}</a>}
  </article>
  <ul className="economic-reading-links">{S.links.map((link:Data)=><li key={link.href}><a className="text-button" href={link.href}>{link.label} →</a></li>)}</ul>
 </div>;
}
