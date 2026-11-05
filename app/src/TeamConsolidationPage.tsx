import {useStudy,useFormat,type Data} from './context';
import {MethodText} from './MethodDocument';
import {phaseReadingHash} from './economicNavigation';
import {useReadingContext} from './ReadingScopeContext';
import {TeamSelect} from './TeamTopology';
import './deliveryOrganisation.css';
import {ReadingTabs,WorkReadiness,ContributionPeriod} from './ConsolidationViews';

export function TeamConsolidationPage({costs=false,option='java-spring',focus,view}:{costs?:boolean;option?:string;focus?:string;view?:string}){
 const {data}=useStudy(),{n}=useFormat(),D=data.content.delivery_organisation,C=D.team_consolidations,L=C.labels,O=D.labels,context=useReadingContext();
 const working=view==='working',R=working?C.working:C.reference,team=D.teams.find((t:Data)=>t.id===focus),page=costs?'couts-equipes':'charges-equipes';
 const field=costs?'cost_eur_ht':working?'net_jh':'source_jh';
 const value=(v:number|null,key=field)=>v===null||v===undefined?L.unknown:n(key.endsWith('eur_ht')?v/1000:v,key.endsWith('eur_ht')?0:1);
 const actors=[...D.teams.filter((t:Data)=>!team||t.id===team.id).map((t:Data)=>({id:t.id,label:t.label})),...(!team?[{id:'governance',label:O.governance},{id:null,label:O.unallocated}]:[])];
 const records=R.contributions.filter((r:Data)=>!team||r.team_ref===team.id);
 const projectionCell=(phase:string)=>(team?R.rows:R.totals).find((r:Data)=>r.phase_ref===phase&&(!team||r.team_ref===team.id));
 const label=(id:string|null)=>D.teams.find((t:Data)=>t.id===id)?.label||(id==='governance'?O.governance:O.unallocated);
 const link=(extra:Data={})=>phaseReadingHash({...context,page,option,focus,view:working?'working':'reference',...extra})!;
 const unitLink=(id:string)=>phaseReadingHash({...context,page:'unites-travail',view:working?'working':'reference',focus:id})!;
 const detail=(rows:Data[])=>!rows.length?<p>{L.none}</p>:<div className="delivery-table-scroll" role="region" aria-label={L.detail} tabIndex={0}><table className="eco-table delivery-records" data-consolidation-details><thead><tr>{[L.work,L.team,L.phase,L.version,...(costs?[L.cost,L.labour_cost,L.expense_cost,L.unclassified_cost]:[L.source,L.gross,L.net]),L.period,L.rules].map((v:string)=><th scope="col" key={v}>{v}</th>)}</tr></thead><tbody>{rows.map((r:Data)=><tr key={r.id} data-contribution={r.id}><th scope="row"><a href={unitLink(r.work_unit_ref)}>{r.label||r.work_unit_ref}</a><small>{r.component_kind==='labour'?L.roles:r.component_kind==='expense'?L.expense:r.component_kind==='included'?L.included+' '+r.included_in_ref:L.source_component}</small></th><td>{label(r.team_ref)}</td><td>{D.phases.find((p:Data)=>p.id===r.phase_ref)?.label}<small>{r.recurrence==='annual'?L.annual:L.initial}</small></td><td>{L.provenance[r.estimate_source]||L.provenance.proposal}{' · '+(r.estimate_version||1)}</td>{(costs?['cost_eur_ht','labour_eur_ht','non_labour_eur_ht','unclassified_eur_ht']:['source_jh','gross_jh','net_jh']).map(key=><td key={key}>{r.component_kind==='included'?L.included:costs&&r.cost_applicable===false?data.content.delivery_organisation.work_catalog.estimate_labels.not_applicable:(key!=='cost_eur_ht'&&key.includes('eur_ht')&&r[key]==null&&r.cost_eur_ht!==null?data.content.delivery_organisation.work_catalog.estimate_labels.not_applicable:value(r[key],key))}</td>)}<td><ContributionPeriod period={r.period}/></td><td>{r.rule_refs.join(', ')||L.unknown}</td></tr>)}</tbody></table></div>;
 return <div className="essential-page economic-dossier delivery-page" data-team-consolidation={working?'working':'reference'}>
  <aside className="delivery-principle"><h2>{D.principle.title}</h2><p><MethodText>{D.principle.text}</MethodText></p></aside>
  {costs&&<nav className="delivery-reading-navigation" aria-label={data.ui.essential.market_costs.price_zone}>{['paris','province'].map(zone=><a key={zone} href={link({zone})} aria-current={(context.zone||'paris')===zone?'true':undefined}>{data.ui.essential.market_costs.price_zones[zone]}</a>)}</nav>}
  <nav className="delivery-reading-navigation" aria-label={O.nav_label}>{data.ui.essential.framework_vision.journey.options.map((o:Data)=><a key={o.id} href={link({option:o.id,focus:undefined})} aria-current={option===o.id?'true':undefined}>{o.label}</a>)}</nav>
  {option!=='java-spring'?<p className="delivery-note">{O.buy_note}</p>:<>
   <ReadingTabs page={page} option={option} working={working} focus={team?.id}/>
   <p>{L.intro}</p>{working&&<p className="delivery-note">{L.working_note}</p>}
   <TeamSelect value={team?.id||''} onChange={id=>{location.hash=link({focus:id||undefined});}}/>
   <p>{working?L.known:costs?O.costs_note:O.charges_note}</p>{!costs&&<p className="delivery-note">{L.measure_note}</p>}
   <div className="delivery-table-scroll" role="region" aria-label={L.title} tabIndex={0}><table className="eco-table delivery-matrix" data-consolidation-matrix><thead><tr><th scope="col">{L.team}</th>{D.phases.map((p:Data)=><th scope="col" key={p.id}>{p.label}<small>{costs?p.cost_unit:p.charge_unit}</small></th>)}</tr></thead><tbody>{actors.map((a:Data)=><tr key={a.id||'unallocated'} data-owner={a.id||'unallocated'}><th scope="row">{a.label}</th>{D.phases.map((p:Data)=>{const cell=R.rows.find((r:Data)=>r.team_ref===a.id&&r.phase_ref===p.id);return <td key={p.id} data-phase={p.id} data-unknown={cell[field]===null}>{working&&cell.metric_states[field].status==='not_applicable'?L.no_work:value(cell[field])}{working&&cell.metric_states[field].status!=='not_applicable'&&<small className="estimate-status">{L[cell.metric_states[field].status]||L.partial}</small>}</td>;})}</tr>)}</tbody>{!team&&<tfoot><tr><th scope="row">{O.totals}</th>{D.phases.map((p:Data)=><td key={p.id}>{value(R.totals.find((r:Data)=>r.phase_ref===p.id)[field])}</td>)}</tr></tfoot>}</table></div>
   {working&&<><WorkReadiness team={team?.id}/><section>
   <p className="delivery-note">{C.scenario.projection.end_month===null?L.no_projection:L.projection_note}</p>
   {C.scenario.projection.end_month!==null&&<div className="delivery-lifecycle">{D.phases.map((p:Data)=><section key={p.id} data-projection-phase={p.id}><h3>{p.label}</h3><p>{L.projected+' · '+value(projectionCell(p.id).projected_cost_eur_ht,'projected_cost_eur_ht')}</p><small className="estimate-status">{L[projectionCell(p.id).metric_states.projected_cost_eur_ht.status]}</small></section>)}</div>}
   {R.coverage_groups.length>0&&<><h3>{L.coverage}</h3>{R.coverage_groups.map((g:Data)=><article key={g.id}><strong>{g.confirmed===true?L.confirmed:L.unconfirmed}</strong><p>{g.basis||L.unknown}</p><h4>{L.excluded}</h4><ul>{g.replaced_refs.map((id:string)=><li key={id}><a href={unitLink(id)}>{D.work_catalog.units.find((u:Data)=>u.id===id)?.label}</a></li>)}</ul><h4>{L.work}</h4><ul>{g.replacing_refs.map((id:string)=><li key={id}><a href={unitLink(id)}>{D.work_catalog.units.find((u:Data)=>u.id===id)?.label}</a></li>)}</ul><h4>{L.remaining_scope}</h4>{g.remaining_work_refs===null?<p>{L.remaining_unknown}</p>:g.remaining_work_refs.length?<ul>{g.remaining_work_refs.map((id:string)=><li key={id}><a href={unitLink(id)}>{D.work_catalog.units.find((u:Data)=>u.id===id)?.label}</a></li>)}</ul>:<p>{L.no_remaining_scope}</p>}</article>)}</>}
   {R.excluded_work_units.length>0&&<><h3>{L.excluded}</h3><ul>{R.excluded_work_units.map((id:string)=><li key={id}><a href={unitLink(id)}>{D.work_catalog.units.find((u:Data)=>u.id===id)?.label}</a></li>)}</ul></>}
   {R.pending_contributions.length>0&&<><h3>{L.pending}</h3><p>{L.pending_note}</p></>}
   </section></>}
   <section><h2>{L.detail}</h2>{detail(records)}</section>
  </>}
 </div>;
}
