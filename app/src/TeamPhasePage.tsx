import {useStudy,useFormat,type Data} from './context';
import {MethodText} from './MethodDocument';
import {phaseReadingHash} from './economicNavigation';
import {useReadingContext} from './ReadingScopeContext';
import './deliveryOrganisation.css';
import {TeamSelect} from './TeamTopology';

export function DurableTeamsPrinciple(){
 const {data}=useStudy(),D=data.content.delivery_organisation;
 return <aside className="delivery-principle"><h2>{D.principle.title}</h2><p><MethodText>{D.principle.text}</MethodText></p></aside>;
}

export function TeamPhaseMatrix({costs=false,team,phase,working=false}:{costs?:boolean;team?:string;phase?:string;working?:boolean}){
 const {data}=useStudy(),{n}=useFormat(),D=data.content.delivery_organisation,L=D.labels,context=useReadingContext();
 const phases=D.reading.phases.filter((p:Data)=>!phase||p.id===phase),teams=D.teams.filter((t:Data)=>!team||t.id===team);
 const field=costs?'cost_eur_ht':working?'net_jh':'jh';
 const value=(v:number|null)=>v===null?L.unknown:n(costs?v/1000:v,costs?0:1);
 const rows=[...teams.map((t:Data)=>({id:t.id,label:t.label})),...(!team?[{id:'governance',label:L.governance},{id:null,label:L.unallocated}]:[])];
 return <><p className="delivery-table-caption">{working?D.team_consolidations.labels.measure_note:costs?L.costs_note:L.charges_note}</p><div className="delivery-table-scroll" role="region" aria-label={costs?L.costs_title:L.charges_title} tabIndex={0}><table className="eco-table delivery-matrix"><caption className="sr-only">{costs?L.costs_title:L.charges_title}</caption><thead><tr><th scope="col">{L.team}</th>{phases.map((p:Data)=><th scope="col" key={p.id}>{p.label}<small>{costs?p.cost_unit:p.charge_unit}</small></th>)}</tr></thead><tbody>{rows.map((row:Data)=><tr key={row.id??'unallocated'} data-owner={row.id??'unallocated'}><th scope="row">{row.id&&row.id!=='governance'?<a href={phaseReadingHash({...context,page:'equipes-produit',option:'java-spring',view:working?'working':'reference',focus:row.id})!}>{row.label}</a>:row.label}</th>{phases.map((p:Data)=>{const cell=(working?D.team_consolidations.working.rows:D.allocation_table.rows).find((r:Data)=>r.phase_ref===p.id&&(working?r.team_ref===row.id:row.id==='governance'?r.owner_kind==='governance':row.id===null?r.owner_kind==='unallocated':r.team_ref===row.id));return <td key={p.id} data-unknown={cell[field]===null}>{!working&&!costs&&D.excluded_workload_phases.includes(p.id)?L.integration_workload_pending:working&&cell.metric_states[field].status==='not_applicable'?D.team_consolidations.labels.no_work:value(cell[field])}{working&&cell.metric_states[field].status!=='not_applicable'&&<small>{D.team_consolidations.labels[cell.metric_states[field].status]}</small>}</td>;})}</tr>)}</tbody>{!team&&<tfoot><tr><th scope="row">{L.totals}</th>{phases.map((p:Data)=><td key={p.id}>{!working&&!costs&&D.excluded_workload_phases.includes(p.id)?L.integration_workload_pending:value((working?D.team_consolidations.working.totals:D.allocation_table.totals).find((r:Data)=>r.phase_ref===p.id)[field])}</td>)}</tr></tfoot>}</table></div></>;
}

export function TeamAllocationCosts({option}:{option:string}){
 const {data}=useStudy(),L=data.content.delivery_organisation.labels,context=useReadingContext();
 return <section className="eco-section delivery-page" id="ventilation-equipes"><h2>{L.allocation_title}</h2>{option!=='java-spring'?<p className="delivery-note">{L.buy_note}</p>:<><p>{L.allocation_note}</p><TeamPhaseMatrix costs/><p className="delivery-note">{L.integration_workload_note}</p><p>{L.unknown_note}</p><p>{L.costs_period_note}</p></>}</section>;
}

export {TeamConsolidationPage as TeamPhasePage} from './TeamConsolidationPage';
