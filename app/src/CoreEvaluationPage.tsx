import {useStudy,useFormat,type Data} from './context';
import {MethodText} from './MethodDocument';
import {SourceLink} from './components';
import './coreEvaluation.css';

export function CalculationAlignment({unit}:{unit:Data}){
 const {n}=useFormat(),A=unit.alignment,L=A.labels;
 return <section className="calculation-alignment"><h4>{L.alignment}</h4>
  <p>{L.reference} : <strong>{A.reference_label} · {n(A.reference_jh,2)} {L.jh_unit}</strong></p>
  <div className="table-scroll"><table className="core-evaluation-table"><thead><tr><th>{L.candidate}</th><th>{L.common_effort}</th><th>{L.complement_effort}</th><th>{L.effort}</th><th>{L.gap}</th><th>{L.relative_gap}</th></tr></thead>
   <tbody>{[...A.rows,A.functional].map((r:Data)=><tr key={r.id}><th scope="row">{r.label}</th><td>{r.common_jh==null?'—':n(r.common_jh,2)} {r.common_jh==null?'':L.jh_unit}</td><td>{r.complements_jh==null?'—':n(r.complements_jh,2)} {r.complements_jh==null?'':L.jh_unit}</td><td>{n(r.jh,2)} {L.jh_unit}</td><td>{r.gap_jh===null?'—':n(r.gap_jh,2)} {L.jh_unit}</td><td>{r.gap_pct===null?'—':n(r.gap_pct,2)} {L.percent_unit}</td></tr>)}</tbody>
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
  <h4>{L.funding}</h4><ul>{unit.funding.map((m:Data)=><li key={m.id}><strong>{m.label}</strong> — {m.funding_mode==='consumed'?L.funding_consumed:L.funding_funded}. {L.funding_owner} : {m.funding_owner_label}. {m.note}</li>)}</ul>
  <h4>{L.consolidation}</h4><p>{unit.consolidation.note}</p>
 </section>;
}

export function RetainedCoreFamilies({units}:{units:Data[]}){
 const {data}=useStudy(),{n,amount}=useFormat(),R=data.ui.essential.core_results;
 return <>{units.map(unit=><section className="retained-core-family" key={unit.id} data-family={unit.id}>
  <h3>{unit.label}</h3>
  <dl className="economic-value-summary">
   <div><dt>{R.days}</dt><dd>{n(unit.total_jh,0)} {R.jh_unit}</dd></div>
   <div><dt>{R.duration}</dt><dd>{n(unit.months,1)} {R.months}</dd></div>
   <div><dt>{R.average_team}</dt><dd>{n(unit.schedule.average_fte,1)} {R.fte}</dd></div>
  </dl>
  {unit.capabilities.length>0&&<><h4>{R.family_capabilities}</h4><ul>{unit.capabilities.map((c:Data)=>{const row=data.content.delivery_readiness.scope.rows.find((r:Data)=>r.id===c.id);return <li key={c.id}>{row?<SourceLink path={row.href}>{c.id+' · '+row.name}</SourceLink>:c.id}</li>;})}</ul></>}
  {unit.professional_functions?.length>0&&<><h4>{data.content.core_product_scope.reading.inventory_title}</h4><ul>{unit.professional_functions.map((id:string)=><li key={id}>{data.content.core_product_scope.functions.find((f:Data)=>f.id===id)?.label||id}</li>)}</ul></>}
  {unit.trace.component_allocations&&<section className="core-component-allocations"><h4>{R.component_title}</h4><p>{R.component_note}</p><div className="table-scroll" tabIndex={0} role="region" aria-label={R.component_title}><table className="core-evaluation-table"><thead><tr><th scope="col">{R.component_family}</th><th scope="col">{R.component_days}</th></tr></thead><tbody>{unit.trace.component_allocations.map((part:Data)=><tr key={part.id}><th scope="row">{part.label}</th><td>{n(part.jh,0)} {R.jh_unit}</td></tr>)}</tbody></table></div></section>}
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
  <h4>{R.review_title}</h4><p>{R.review_note}</p><h4>{R.provenance}</h4><p><strong>{unit.method}</strong> · {unit.provenance.explanation}</p>
  <p>{R.crosscheck} : <strong>{n(unit.crosscheck.jh,0)} {R.jh_unit}</strong> · {unit.crosscheck.explanation}</p>
  <CalculationAlignment unit={unit}/>
  <h4>{R.uncertainty}</h4><p>{unit.uncertainty.explanation}</p>
  <h4>{R.assumptions}</h4><ul>{unit.assumptions.map((a:Data)=><li key={a.id}><p><strong>{a.hypothesis}</strong></p><p>{R.trigger} : {a.trigger}</p><p>{a.effect}</p></li>)}</ul>
  <h4>{R.includes}</h4><ul>{unit.includes.map((text:string)=><li key={text}>{text}</li>)}</ul>
  <h4>{R.excludes}</h4><ul>{unit.excludes.map((text:string)=><li key={text}>{text}</li>)}</ul>
 </section>)}</>;
}

function ProductEstimateProposal({P}:{P:Data}){
 const {data}=useStudy(),{n,amount}=useFormat(),L=P.reading,R=data.ui.essential.core_results;
 const moduleNames=Object.fromEntries(P.module_assumptions.map((m:Data)=>[m.id,m.label]));
 return <section className="product-estimate-proposal"><h3>{L.title}</h3><p><strong>{L.proposal}</strong> · {L.note}</p>
  <dl className="economic-value-summary"><div><dt>{L.total}</dt><dd>{n(P.total_jh,0)} {L.jh}</dd></div><div><dt>{L.cost}</dt><dd>{amount(P.eur_ht)}</dd></div><div><dt>{L.adopted}</dt><dd>{n(P.previous_adopted_jh??P.adopted_jh,0)} {L.jh}</dd></div><div><dt>{L.nominal_schedule}</dt><dd>{n(P.nominal_effort_based_months,1)} {L.months}</dd></div></dl>
  <div className="table-scroll"><table className="core-evaluation-table"><thead><tr><th>{L.module}</th><th>{L.effort}</th><th>{L.schedule}</th></tr></thead><tbody>{P.rows.map((r:Data)=><tr key={r.id}><th scope="row">{r.label}</th><td>{n(r.jh,0)} {L.jh}</td><td>{n(r.months,1)} {L.months}</td></tr>)}</tbody></table></div><p>{L.month_note}</p>
  <dl className="economic-value-summary"><div><dt>{L.current_plan}</dt><dd>{n(P.planning.reference_months,0)} {L.months}</dd></div><div><dt>{L.average_team}</dt><dd>{n(P.planning.average_people_at_reference,1)} {L.people}</dd></div></dl><h4>{L.purpose}</h4><dl className="economic-value-summary">{Object.entries(P.purposes).map(([key,value])=>{const v=value as Data;return <div key={key}><dt>{key==='business-runtime'?L.business:L.it}</dt><dd>{n(v.jh,0)} {L.jh} · {amount(v.eur_ht)}</dd></div>;})}</dl><p>{L.partition_note}</p>
  <h4>{L.roles}</h4><div className="table-scroll"><table className="core-evaluation-table"><thead><tr><th>{L.role}</th><th>{L.business}</th><th>{L.it}</th><th>{L.total}</th><th>{R.rate}</th></tr></thead><tbody>{P.roles.map((r:Data)=><tr key={r.id}><th scope="row">{r.label}</th><td>{n(P.purposes['business-runtime'].roles[r.id],0)} {L.jh}</td><td>{n(P.purposes['it-complement'].roles[r.id],0)} {L.jh}</td><td>{n(r.jh,0)} {L.jh}</td><td>{n(r.rate_eur_jh,0)} {R.rate_unit}</td></tr>)}</tbody></table></div>
  <h4>{L.comparisons}</h4><p>{P.comparability}</p><div className="table-scroll"><table className="core-evaluation-table"><thead><tr><th>{L.module}</th><th>{P.rows[0].label}</th><th>{P.rows[1].label}</th><th>{P.rows[2].label}</th><th>{L.total}</th></tr></thead><tbody>{P.comparative_rows.map((r:Data)=><tr key={r.id}><th scope="row">{r.id}</th><td>{n(r.process_jh,0)} {L.jh}</td><td>{n(r.workbench_jh,0)} {L.jh}</td><td>{n(r.it_jh,0)} {L.jh}</td><td>{n(r.total_jh,0)} {L.jh}</td></tr>)}</tbody></table></div>
  <h4>{L.cosmic}</h4><p>{L.cosmic_note}</p><div className="table-scroll"><table className="core-evaluation-table"><thead><tr><th>{L.module}</th><th>{L.cocomo_column} · {L.jh}</th><th>{L.cosmic_column} · {L.jh}</th><th>{L.cfp_label}</th><th>{L.difference_jh}</th><th>{L.difference_pct}</th></tr></thead><tbody><tr><th scope="row">{P.rows[0].label}</th><td>{n(P.rows[0].jh,0)}</td><td>{n(P.cosmic_process.jh,0)}</td><td>{n(P.cosmic_process.CFP,0)}</td><td>{n(P.cosmic_process.alignment.gap_jh,1)}</td><td>{n(P.cosmic_process.alignment.gap_pct,1)} %</td></tr><tr><th scope="row">{P.rows[2].label}</th><td>{n(P.rows[2].jh,0)}</td><td>{n(P.it_cosmic.jh,0)}</td><td>{n(P.it_cosmic.CFP,0)}</td><td>{n(P.it_cosmic.alignment.gap_jh,1)}</td><td>{n(P.it_cosmic.alignment.gap_pct,1)} %</td></tr></tbody></table></div><p>{L.alignment_denominator}</p><p>{L.raw_reference} : {n(P.cosmic_process.reference_unrounded_jh,2)} {L.jh} · {n(P.it_cosmic.reference_unrounded_jh,2)} {L.jh}</p><p>{P.cosmic.limit}</p><p><strong>{L.alignment_note}</strong></p><p>{L.matching_pdr} : {n(P.cosmic_process.hours_per_CFP_to_match,1)}</p>
  {P.technical_trials&&<section className="product-technical-trials"><h4>{P.technical_trials.reading.title}</h4><p>{P.technical_trials.reading.conclusion}</p><p><strong>{n(P.technical_trials.checks_passed,0)}</strong> {P.technical_trials.reading.checks} · {P.technical_trials.evaluated_on}</p><h5>{P.technical_trials.reading.observed}</h5><ul>{P.technical_trials.observations.map((o:Data)=><li key={o.id}><strong>{o.label}</strong> — {o.detail}</li>)}</ul><h5>{P.technical_trials.reading.funding}</h5><ul>{P.technical_trials.funding.map((f:Data)=><li key={f.requirement}><strong>{f.requirement}</strong> · {f.module_labels.join(', ')} — {f.basis}</li>)}</ul><h5>{P.technical_trials.reading.remaining}</h5><ul>{P.technical_trials.remaining.map((text:string)=><li key={text}>{text}</li>)}</ul><p>{P.technical_trials.reading.stop}</p></section>}
  <h4>{L.assumptions}</h4><p>{L.module_fraction_note}</p><ul>{P.assumptions.map((a:string)=><li key={a}>{a}</li>)}</ul><ul>{P.module_assumptions.map((m:Data)=><li key={m.id}><strong>{m.label||m.id} · {n(m.fraction,2)}</strong> — {m.basis}</li>)}</ul>
  <h4>{L.grouping}</h4><p>{L.grouping_note}</p><p><strong>{n(P.grouping_sensitivity.single_project_jh,0)} {L.jh}</strong> · +{n(P.grouping_sensitivity.gap_pct,1)} %</p><p>{L.code_size} : {n(P.grouping_sensitivity.equivalent_logical_units,0)}</p><h4>{L.sensitivities}</h4><p>{L.sensitivity_note}</p><div className="table-scroll"><table className="core-evaluation-table"><thead><tr><th>{L.module}</th><th>{L.value}</th><th>{L.delta}</th></tr></thead><tbody>{P.sensitivities.map((s:Data)=><tr key={s.id+s.value}><th scope="row">{s.id==='declarative-weight'?L.declarative_weight_label:moduleNames[s.id]||s.id}</th><td>{n(s.value,2)}</td><td>{s.delta_jh>0?'+':''}{n(s.delta_jh,0)} {L.jh}</td></tr>)}</tbody></table></div><p>{L.source}</p>
 </section>;
}

export function CoreProductScope({details=false}:{details?:boolean}){
 const {data}=useStudy(),{n,amount}=useFormat(),S=data.content.core_product_scope;
 if(!S)return null;
 const L=S.reading,purposes=Object.fromEntries(S.purposes.map((p:Data)=>[p.id,p.label]));
 return <section className="core-product-scope"><h3>{L.title}</h3><p>{L.intro}</p>
  <div className="table-scroll"><table className="core-evaluation-table"><thead><tr><th>{data.ui.essential.core_results.option}</th><th>{L.adopted}</th><th>{L.business}</th><th>{L.it}</th><th>{L.unallocated}</th></tr></thead><tbody>{S.options.map((o:Data)=><tr key={o.stack}><th scope="row">{data.baseline.options.find(t=>t.stack===o.stack)?.name||o.name}</th><td>{o.status==='no_estimate'?L.no_estimate:<>{n(o.adopted_jh,0)} {L.jh_unit}<br/>{amount(o.adopted_eur_ht)}</>}</td>{S.purposes.map((p:Data)=><td key={p.id}>{o.purposes[p.id].jh==null?L.unknown:<>{n(o.purposes[p.id].jh,0)} {L.jh_unit}<br/>{amount(o.purposes[p.id].eur_ht)}</>}</td>)}<td>{o.status==='no_estimate'?L.no_estimate:n(o.unallocated_jh,0)+' '+L.jh_unit}</td></tr>)}</tbody></table></div>
  <p>{L.allocation_note}</p><p>{L.missing_note}</p><p><strong>{L.process_reservation}</strong></p>
  {S.proposal&&<ProductEstimateProposal P={S.proposal}/>}
  {S.functions&&<><h4>{L.inventory_title}</h4><p>{L.progress_note}</p><div className="table-scroll"><table className="core-evaluation-table"><thead><tr><th>{L.function_label}</th><th>{L.purpose_label}</th><th>{L.scope_label}</th><th>{L.funding_label}</th><th>{L.proof_label}</th></tr></thead><tbody>{S.functions.map((f:Data)=><tr key={f.id}><th scope="row">{f.label}</th><td>{purposes[f.purpose]}</td><td>{f.boundary}<p>{L.unknown_additional}</p></td><td>{f.existing_funding.map((m:Data)=><p key={m.id}>{m.label}</p>)}</td><td>{f.market_evidence.length?f.market_evidence.map((e:Data)=><p key={e.url}><a href={e.url} target="_blank" rel="noreferrer">{e.product} · {e.path.split('/').at(-1)}</a></p>):L.review_label}</td></tr>)}</tbody></table></div></>}
 </section>;
}

export function CoreEvaluationResults({status,details=true,showNotice=true}:{status?:Data;details?:boolean;showNotice?:boolean}){
 const {data}=useStudy(),{amount,n}=useFormat(),R=data.ui.essential.core_results;
 const rows=data.content.core_evaluation as Data[];
 const make=rows.filter(row=>row.mode==='Make'),notice=status||R.status;
 return <div className="core-evaluation-results">
   <p><MethodText>{R.make_note}</MethodText></p>
   {showNotice&&<aside className="core-method-notice"><h3>{notice.title}</h3><p><MethodText>{notice.text}</MethodText></p></aside>}
   <div className="table-scroll" tabIndex={0} role="region" aria-label={R.make_title}><table className="core-evaluation-table" data-evaluation="core"><thead><tr><th scope="col">{R.option}</th><th scope="col">{R.central}</th><th scope="col">{R.coverage}</th><th scope="col">{R.uncertainty}</th><th scope="col">{R.cost}</th></tr></thead><tbody>{make.map(row=><tr key={row.stack} data-option={row.stack}><th scope="row">{row.name}</th><td className="number">{row.coverage.covered?<>{n(row.ranges_jh.central,0)} {R.jh_unit}</>:R.pending}</td><td>{n(row.coverage.covered,0)} / {n(row.coverage.total,0)} · {n(row.coverage.covered_pct,1)} {R.percent_unit}<br/>{n(row.coverage.remaining,0)} {R.remaining.toLowerCase()}</td><td>{R.unknown_uncertainty}</td><td className="number"><strong>{row.coverage.covered?amount(row.build_eur_ht):R.pending}</strong></td></tr>)}</tbody></table></div>
   <p>{R.coverage_note}</p>
   <p className="core-evaluation-qualification"><MethodText>{R.qualification}</MethodText></p>
   <CoreProductScope details={details}/>
   {details&&<>{make.flatMap(row=>row.units).map((unit:Data)=>unit.alignment?<RetainedCoreFamilies key={unit.id} units={[unit]}/>:<a key={unit.id} className="text-button" href={'#evaluation-core?family='+encodeURIComponent(unit.id)}>{unit.label} · {R.family_details}</a>)}</>}
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
 const {data}=useStudy(),{amount,n}=useFormat(),R=data.ui.essential.core_results,S=editorial.sections.core;
 const units=options.flatMap(option=>option.core?.units||[]);
 return <div className="economic-trace core-work-trace">
  <div className="economic-family-summaries">{units.map((unit:Data)=><article key={unit.id} data-family-summary={unit.id}>
   <h3>{unit.label}</h3><dl className="economic-value-summary"><div><dt>{R.days}</dt><dd>{n(unit.total_jh,0)} {R.jh_unit}</dd></div><div><dt>{R.duration}</dt><dd>{n(unit.months,1)} {R.months}</dd></div><div><dt>{R.total}</dt><dd>{amount(unit.cost_eur_ht)}</dd></div></dl>
   <a className="text-button" href={'#evaluation-core?family='+encodeURIComponent(unit.id)}>{R.family_details} →</a>
  </article>)}</div>
  <p><MethodText>{S.note}</MethodText></p><ul className="economic-reading-links">{S.links.map((link:Data)=><li key={link.href}><a className="text-button" href={link.href}>{link.label} →</a></li>)}</ul>
 </div>;
}
