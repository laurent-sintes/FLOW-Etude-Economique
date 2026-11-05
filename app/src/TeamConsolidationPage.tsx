import {useEffect,useRef,useState} from 'react';
import {useStudy,useFormat,type Data} from './context';
import {phaseReadingHash} from './economicNavigation';
import {useReadingContext} from './ReadingScopeContext';
import {TeamSelect} from './TeamTopology';
import './deliveryOrganisation.css';
import {ReadingTabs,WorkReadiness,ContributionPeriod} from './ConsolidationViews';

export function TeamConsolidationPage({costs=false,option='java-spring',focus,view,phase}:{costs?:boolean;option?:string;focus?:string;view?:string;phase?:string}){
 const {data}=useStudy(),{n}=useFormat(),D=data.content.delivery_organisation,C=D.team_consolidations,L=C.labels,O=D.labels,context=useReadingContext();
 const working=view==='working',R=working?C.working:C.reference,page=costs?'couts-equipes':'charges-equipes';
 const allActors=[...D.teams.map((t:Data)=>({id:t.id,label:t.label})),{id:'governance',label:O.governance},{id:null,label:O.unallocated}];
 const actor=allActors.find(a=>(a.id??'unallocated')===focus),phaseId=D.phases.some((p:Data)=>p.id===phase)?phase:undefined;
 const [expanded,setExpanded]=useState(false),detailHeading=useRef<HTMLHeadingElement>(null);
 const showDetails=Boolean(actor||phaseId||expanded);
 useEffect(()=>{if(actor||phaseId){detailHeading.current?.focus();detailHeading.current?.scrollIntoView({block:'start'});}},[focus,phaseId,working]);
 const field=costs?'cost_eur_ht':working?'net_jh':'source_jh';
 const metricLabels:Record<string,string>={cost_eur_ht:L.cost,labour_eur_ht:L.labour_cost,non_labour_eur_ht:L.expense_cost,unclassified_eur_ht:L.unclassified_cost,source_jh:L.source,gross_jh:L.gross,net_jh:L.net};
 const value=(v:number|null,key=field)=>v===null||v===undefined?L.unknown:n(key.endsWith('eur_ht')?v/1000:v,key.endsWith('eur_ht')?0:1);
 const actors=actor?[actor]:allActors;
 const records=R.contributions.filter((r:Data)=>(!actor||r.team_ref===actor.id)&&(!phaseId||r.phase_ref===phaseId));
 const projectionCell=(phase:string)=>(actor?R.rows:R.totals).find((r:Data)=>r.phase_ref===phase&&(!actor||r.team_ref===actor.id));
 const domainLabel=(id:string)=>{const c=D.work_catalog.units.find((u:Data)=>u.id===id)?.domain_classification;return c?.status==='direct'?D.work_catalog.domains.find((d:Data)=>d.id===c.domain_refs[0]).label:D.work_catalog.domain_labels[c?.status||'to_classify'];};
 const label=(id:string|null)=>D.teams.find((t:Data)=>t.id===id)?.label||(id==='governance'?O.governance:O.unallocated);
 const link=(extra:Data={})=>phaseReadingHash({...context,page,option,focus,phase:phaseId,view:working?'working':'reference',...extra})!;
 const unitLink=(id:string)=>phaseReadingHash({...context,page:'unites-travail',view:working?'working':'reference',focus:id})!;
 const detail=(rows:Data[])=>!rows.length?<p>{L.none}</p>:<div className="delivery-table-scroll" role="region" aria-label={L.detail} tabIndex={0}><table className="eco-table delivery-records" role="table" data-consolidation-details><thead><tr>{[L.work,L.team,L.phase,L.version,...(costs?[L.cost,L.labour_cost,L.expense_cost,L.unclassified_cost]:[L.source,L.gross,L.net]),L.period,L.rules].map((v:string)=><th scope="col" key={v}>{v}</th>)}</tr></thead><tbody>{rows.map((r:Data)=><tr key={r.id} data-contribution={r.id}><th scope="row"><a href={unitLink(r.work_unit_ref)}>{r.label||r.work_unit_ref}</a><small className="work-domain-label">{domainLabel(r.work_unit_ref)}</small><small>{r.component_kind==='labour'?L.roles:r.component_kind==='expense'?L.expense:r.component_kind==='included'?L.included+' '+r.included_in_ref:L.source_component}</small></th><td data-label={L.team}>{label(r.team_ref)}</td><td data-label={L.phase}>{D.phases.find((p:Data)=>p.id===r.phase_ref)?.label}<small>{r.recurrence==='annual'?L.annual:L.initial}</small></td><td data-label={L.version}>{L.provenance[r.estimate_source]||L.provenance.proposal}{' · '+(r.estimate_version||1)}</td>{(costs?['cost_eur_ht','labour_eur_ht','non_labour_eur_ht','unclassified_eur_ht']:['source_jh','gross_jh','net_jh']).map(key=><td key={key} data-label={metricLabels[key]}>{r.component_kind==='included'?L.included:costs&&(r.cost_applicable===false||r.component_applicability?.[key]===false)?data.content.delivery_organisation.work_catalog.estimate_labels.not_applicable:value(r[key],key)}</td>)}<td data-label={L.period}><ContributionPeriod period={r.period}/></td><td data-label={L.rules}>{r.rule_refs.join(', ')||L.unknown}</td></tr>)}</tbody></table></div>;
 return <div className="essential-page economic-dossier delivery-page" data-team-consolidation={working?'working':'reference'}>
  <p className="consolidation-purpose">{L.intro}</p>
  <p className="delivery-note">{D.work_catalog.domain_labels.team_scope_note}</p>
  {costs&&<nav className="delivery-reading-navigation" aria-label={data.ui.essential.market_costs.price_zone}>{['paris','province'].map(zone=><a key={zone} href={link({zone})} aria-current={(context.zone||'paris')===zone?'true':undefined}>{data.ui.essential.market_costs.price_zones[zone]}</a>)}</nav>}
  <nav className="delivery-reading-navigation" aria-label={O.nav_label}>{data.ui.essential.framework_vision.journey.options.map((o:Data)=><a key={o.id} href={link({option:o.id,focus:undefined})} aria-current={option===o.id?'true':undefined}>{o.label}</a>)}</nav>
  {option!=='java-spring'?<p className="delivery-note">{O.buy_note}</p>:<>
   <ReadingTabs page={page} option={option} working={working} focus={actor?actor.id??'unallocated':undefined} phase={phaseId}/>
   {working&&<p className="delivery-note">{L.working_note}</p>}
   <div className="consolidation-filters"><TeamSelect shared value={actor?actor.id??'unallocated':''} onChange={id=>{location.hash=link({focus:id||undefined});}}/><label className="delivery-selector"><span>{L.phase_filter}</span><select value={phaseId||''} onChange={event=>{location.hash=link({phase:event.target.value||undefined});}}><option value="">{L.all_phases}</option>{D.phases.map((p:Data)=><option key={p.id} value={p.id}>{p.label}</option>)}</select></label></div>
   <p className="consolidation-matrix-help">{L.matrix_help}</p>
   <p>{working?L.known:costs?O.costs_note:O.charges_note}</p>{!costs&&<p className="delivery-note">{L.measure_note}</p>}
   <div className="delivery-table-scroll" role="region" aria-label={L.title} tabIndex={0}><table className="eco-table delivery-matrix" data-consolidation-matrix><thead><tr><th scope="col">{L.team}</th>{D.phases.map((p:Data)=><th scope="col" key={p.id}>{p.label}<small>{costs?p.cost_unit:p.charge_unit}</small></th>)}</tr></thead><tbody>{actors.map((a:Data)=><tr key={a.id||'unallocated'} data-owner={a.id||'unallocated'}><th scope="row">{a.label}</th>{D.phases.map((p:Data)=>{const cell=R.rows.find((r:Data)=>r.team_ref===a.id&&r.phase_ref===p.id);return <td key={p.id} data-phase={p.id} data-unknown={cell[field]===null}><a className="consolidation-cell-link" aria-label={[a.label,p.label,working&&cell.metric_states[field].status==='not_applicable'?L.no_work:value(cell[field])].join(' · ')} href={link({focus:a.id??'unallocated',phase:p.id})} aria-current={actor?.id===a.id&&phaseId===p.id?'true':undefined}>{working&&cell.metric_states[field].status==='not_applicable'?L.no_work:value(cell[field])}{working&&cell.metric_states[field].status!=='not_applicable'&&<small className="estimate-status">{L[cell.metric_states[field].status]||L.partial}</small>}</a></td>;})}</tr>)}</tbody>{!actor&&<tfoot><tr><th scope="row">{O.totals}</th>{D.phases.map((p:Data)=><td key={p.id}><a className="consolidation-cell-link" href={link({focus:undefined,phase:p.id})} aria-label={[O.totals,p.label].join(' · ')}>{value(R.totals.find((r:Data)=>r.phase_ref===p.id)[field])}</a></td>)}</tr></tfoot>}</table></div>
   {working&&<><WorkReadiness team={actor?.id||undefined} phase={phaseId}/><section>
   <p className="delivery-note">{C.scenario.projection.end_month===null?L.no_projection:L.projection_note}</p>
   {C.scenario.projection.end_month!==null&&<div className="delivery-lifecycle">{D.phases.map((p:Data)=><section key={p.id} data-projection-phase={p.id}><h3>{p.label}</h3><p>{L.projected+' · '+value(projectionCell(p.id).projected_cost_eur_ht,'projected_cost_eur_ht')}</p><small className="estimate-status">{L[projectionCell(p.id).metric_states.projected_cost_eur_ht.status]}</small></section>)}</div>}
   {R.coverage_groups.length>0&&<><h3>{L.coverage}</h3>{R.coverage_groups.map((g:Data)=><article key={g.id}><strong>{g.confirmed===true?L.confirmed:L.unconfirmed}</strong><p>{g.basis||L.unknown}</p><h4>{L.excluded}</h4><ul>{g.replaced_refs.map((id:string)=><li key={id}><a href={unitLink(id)}>{D.work_catalog.units.find((u:Data)=>u.id===id)?.label}</a></li>)}</ul><h4>{L.work}</h4><ul>{g.replacing_refs.map((id:string)=><li key={id}><a href={unitLink(id)}>{D.work_catalog.units.find((u:Data)=>u.id===id)?.label}</a></li>)}</ul><h4>{L.remaining_scope}</h4>{g.remaining_work_refs===null?<p>{L.remaining_unknown}</p>:g.remaining_work_refs.length?<ul>{g.remaining_work_refs.map((id:string)=><li key={id}><a href={unitLink(id)}>{D.work_catalog.units.find((u:Data)=>u.id===id)?.label}</a></li>)}</ul>:<p>{L.no_remaining_scope}</p>}</article>)}</>}
   {R.excluded_work_units.length>0&&<><h3>{L.excluded}</h3><ul>{R.excluded_work_units.map((id:string)=><li key={id}><a href={unitLink(id)}>{D.work_catalog.units.find((u:Data)=>u.id===id)?.label}</a></li>)}</ul></>}
   {R.pending_contributions.length>0&&<><h3>{L.pending}</h3><p>{L.pending_note}</p></>}
   </section></>}
   <p className="delivery-note">{L.residual_note}</p>
   <section className="consolidation-detail" data-consolidation-selection={phaseId||'all'}><h2 ref={detailHeading} tabIndex={-1}>{L.detail}</h2>{showDetails?<><p className="consolidation-detail-scope">{actor?.label||O.all_teams}{' · '+(D.phases.find((p:Data)=>p.id===phaseId)?.label||L.all_phases)}{' · '+n(records.length,0)+' '+(records.length===1?L.record_one:L.record_count)}</p>{detail(records)}</>:<div className="consolidation-detail-prompt"><p>{L.detail_prompt}</p><button className="secondary" onClick={()=>setExpanded(true)}>{L.show_all_details}</button></div>}</section>
  </>}
 </div>;
}
