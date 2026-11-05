import {useStudy,useFormat,type Data} from './context';
import {phaseReadingHash} from './economicNavigation';
import {useReadingContext} from './ReadingScopeContext';
import './consolidation.css';

export function useConsolidation(){const {data}=useStudy();const D=data.content.delivery_organisation,C=D.team_consolidations;return {D,C,L:C.labels};}
export function ContributionPeriod({period}:{period:Data}){const {L}=useConsolidation(),{n}=useFormat();return <>{period.start_month===null?L.unknown:n(period.start_month,0)}{' → '}{period.end_month===null?L.unknown:n(period.end_month,0)}</>;}
export function ReadingTabs({page,working,focus,phase,option='java-spring',abaque=false}:{page:string;working:boolean;focus?:string;phase?:string;option?:string;abaque?:boolean}){
 const {L}=useConsolidation(),context=useReadingContext();
 return <nav className="delivery-reading-navigation" aria-label={L.title}>{['reference','working'].map(v=><a key={v} href={phaseReadingHash({...context,page,option,focus,phase,view:abaque?(v==='working'?'abaque-working':'abaque'):v})!} aria-current={(working?'working':'reference')===v?'page':undefined}>{L[v]}</a>)}</nav>;
}
export function WorkReadiness({team,phase}:{team?:string;phase?:string}){
 const {D,C,L}=useConsolidation(),{n}=useFormat(),context=useReadingContext();
 const units=C.working.unit_readings.filter((u:Data)=>u.status!=='excluded'&&u.missing.length&&(!phase||u.phase_ref===phase)&&(!team||!u.team_refs.length||u.team_refs.includes(team)));
 return <section className="consolidation-completeness"><h2>{L.readiness}</h2><p>{L.readiness_note}</p><div className="delivery-lifecycle">{C.working.phase_readings.map((p:Data)=><section key={p.phase_ref} data-readiness-phase={p.phase_ref}><h3>{D.phases.find((f:Data)=>f.id===p.phase_ref).label}</h3><strong>{n(p.complete_units,0)+' / '+n(p.units,0)+' '+L.readiness_count}</strong><p>{n(p.pending_units,0)+' '+L.pending_count}</p>{p.missing.includes('scope')&&<p className="estimate-status">{L.scope_not_reviewed}</p>}</section>)}</div>
 {!units.length?<p>{L.no_gaps}</p>:<details className="consolidation-todo"><summary>{L.readiness+' · '+n(units.length,0)+' '+L.unit_count}</summary><div className="delivery-table-scroll" role="region" tabIndex={0} aria-label={L.unit_gaps}><table className="eco-table consolidation-gap-table" data-work-readiness><thead><tr>{[L.work,L.phase,L.unit_status,L.unit_gaps].map((v:string)=><th key={v} scope="col">{v}</th>)}</tr></thead><tbody>{units.map((u:Data)=><tr key={u.work_unit_ref} data-gap-unit={u.work_unit_ref}><th scope="row"><a href={phaseReadingHash({...context,page:'unites-travail',view:'working',focus:u.work_unit_ref})!}>{u.label}</a></th><td>{D.phases.find((p:Data)=>p.id===u.phase_ref).label}</td><td>{L.unit_states[u.status]}</td><td><ul>{u.missing.map((key:string)=><li key={key}>{L.missing[key]}</li>)}</ul></td></tr>)}</tbody></table></div></details>}
 </section>;
}
export function UnitScenarioPanel({unit}:{unit:Data}){
 const {D,C,L}=useConsolidation(),{n}=useFormat(),context=useReadingContext(),u=C.working.unit_readings.find((r:Data)=>r.work_unit_ref===unit.id),s=u.selection;
 const owner=(id:string)=>D.teams.find((t:Data)=>t.id===id)?.label||D.labels.governance;
 const human=s.estimate_source!=='proposal'||unit.estimation.proposal.result.human_applicable!==false;
 const amount=(value:number|null,cost=false)=>value===null?L.unknown:n(cost?value/1000:value,cost?0:1);
 return <section className="unit-scenario-panel" data-unit-scenario={unit.id}><h3>{L.unit_status}</h3><strong className="estimate-status">{L.unit_states[u.status]}</strong><dl className="estimate-metadata"><div><dt>{L.selected_estimate}</dt><dd>{L.provenance[s.estimate_source]+' · '+L.version+' '+n(s.estimate_version,0)}</dd></div><div><dt>{L.accounting}</dt><dd>{L.accounting_values[s.accounting]||L.unknown}</dd></div><div><dt>{L.effective_period}</dt><dd><ContributionPeriod period={u.effective_period}/></dd></div><div><dt>{L.rules}</dt><dd>{u.rule_refs.join(', ')||L.unknown}</dd></div></dl>{s.basis&&<p>{s.basis}</p>}<strong>{u.recurrence==='annual'?L.annual:L.initial}</strong><dl className="estimate-metadata"><div><dt>{L.gross}</dt><dd data-selected-gross>{human?amount(u.gross_jh):L.no_work}</dd></div><div><dt>{L.net}</dt><dd data-selected-net>{human?amount(u.net_jh):L.no_work}</dd></div><div><dt>{L.cost}</dt><dd data-selected-cost>{amount(u.cost_eur_ht,true)}</dd></div></dl>
 {u.status==='excluded'&&<p>{L.excluded_note}</p>}{u.status==='pending'&&<p>{L.pending_note}</p>}
 {u.included_in_ref&&<p>{L.included+' '}<a href={phaseReadingHash({...context,page:'unites-travail',view:'working',focus:u.included_in_ref})!}>{D.work_catalog.units.find((x:Data)=>x.id===u.included_in_ref)?.label}</a></p>}
 <h4>{L.unit_gaps}</h4>{u.missing.length?<ul>{u.missing.map((key:string)=><li key={key}>{L.missing[key]}</li>)}</ul>:<p>{L.no_gaps}</p>}
 {u.team_refs.length>0&&<><h4>{L.working_contributions}</h4><ul>{u.team_refs.map((id:string)=><li key={id}>{id==='governance'?owner(id):<a href={phaseReadingHash({...context,page:'equipes-produit',view:'working',focus:id})!}>{owner(id)}</a>}</li>)}</ul></>}
 </section>;
}
export function ScenarioAllocationRules(){
 const {D,C,L}=useConsolidation(),{n}=useFormat(),context=useReadingContext();
 return <section data-scenario-rules><h3>{L.scenario_rules}</h3>{!C.scenario.assignments.length?<p>{L.no_scenario_rules}</p>:<div className="delivery-table-scroll" role="region" tabIndex={0} aria-label={L.scenario_rules}><table className="eco-table"><thead><tr>{[L.work,L.version,L.role,L.shares,L.rules].map((v:string)=><th scope="col" key={v}>{v}</th>)}</tr></thead><tbody>{C.scenario.assignments.map((r:Data)=><tr key={r.id}><th scope="row"><a href={phaseReadingHash({...context,page:'unites-travail',view:'working',focus:r.work_unit_ref})!}>{D.work_catalog.units.find((u:Data)=>u.id===r.work_unit_ref).label}</a><small>{r.basis}</small></th><td>{L.provenance[r.estimate_source]+' · '+n(r.estimate_version,0)}</td><td>{r.component_ref}</td><td><ul>{r.shares.map((s:Data)=><li key={s.team_ref}>{(D.teams.find((t:Data)=>t.id===s.team_ref)?.label||D.labels.governance)+' · '+n(s.share_pct,1)+' %'}</li>)}</ul></td><td>{r.id}</td></tr>)}</tbody></table></div>}
 <h4>{L.effective_rules}</h4><ul>{C.working.unit_readings.filter((u:Data)=>u.rule_refs.length).map((u:Data)=><li key={u.work_unit_ref}><a href={phaseReadingHash({...context,page:'unites-travail',view:'working',focus:u.work_unit_ref})!}>{u.label}</a>{' · '+L.provenance[u.selection.estimate_source]+' '+n(u.selection.estimate_version,0)+' · '+u.rule_refs.join(', ')}</li>)}</ul>
 </section>;
}
