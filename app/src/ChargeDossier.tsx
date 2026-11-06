import {useEffect,useId,useState,type CSSProperties,type ReactNode} from 'react';
import {BriefcaseBusiness,Wrench,Info,Table2,Network,BadgeCheck,Scissors,Blocks,Map,Calculator,Users,Layers,FileText} from 'lucide-react';
import {useStudy,useFormat,request,type Data} from './context';
import {Drawer,SourceLink} from './components';
import {MethodText} from './MethodDocument';
import {TeamBadge} from './TeamTopology';
import './chargeDossier.css';

function Information({summary,label,onClick}:{summary:string;label:string;onClick:()=>void}){
 const tooltipId=useId(),[dismissed,setDismissed]=useState(false);
 return <span className="charge-information" onMouseLeave={()=>setDismissed(false)}>
  <button type="button" aria-label={label} aria-describedby={tooltipId} onFocus={()=>setDismissed(false)} onKeyDown={event=>{if(event.key==='Escape')setDismissed(true);}} onClick={onClick}><Info size={18}/></button>
  <span role="tooltip" id={tooltipId} hidden={dismissed}><MethodText>{summary}</MethodText></span>
 </span>;
}

export function ChargeOptions({pageId,option,view}:{pageId:string;option:string;view?:string}){
 const {data}=useStudy(),journey=data.ui.essential.framework_vision.journey;
 const logos:Record<string,string>={'java-spring':'assets/java-original.svg',microsoft:'assets/microsoft-original.svg',sap:'assets/sap-original.svg'};
 return <nav className="charge-options" aria-label={journey.labels.option}>{journey.options.map((o:Data)=><a key={o.id} href={'#'+pageId+'?option='+o.id+(view==='teams'?'&view=teams':'')} aria-current={option===o.id?'page':undefined}><img src={logos[o.id]} alt="" className={'charge-product-logo '+o.id}/><span>{o.short_label||o.label}</span></a>)}</nav>;
}

function DetailSection({title,icon,tone='',children}:{title:string;icon:ReactNode;tone?:string;children:ReactNode}){
 return <section className={'charge-detail-section '+tone}><h3>{icon}{title}</h3><div className="charge-detail-body">{children}</div></section>;
}

export function ChargeDossier({phase,option='java-spring',focus,view}:{phase?:string;option?:string;focus?:string;view?:string}){
 const {data}=useStudy(),{n}=useFormat(),D=data.content.delivery_organisation,W=D.charge_dossier,L=W.labels;
 const [selected,setSelected]=useState<Data|null>(null),[team,setTeam]=useState<Data|null>(null);
 const teamsView=phase==='acquisition'&&view==='teams';
 const pageId=phase?'charges-'+phase:'charges-equipes';
 const scopeList=(summary:Data[])=>summary.length?<ul className="charge-scope-paths">{summary.map(item=><li key={item.ref} data-scope-summary={item.kind+':'+item.ref}>{item.parent&&<span>{item.parent}</span>}<strong>{L.scope_templates[item.kind].replace('{name}',item.label).replace('{excluded}',item.excluded)}</strong></li>)}</ul>:<small>{L.no_mapping}</small>;
 const natureIcons=(natures:string[])=><span className="charge-natures">{natures.map(kind=><span key={kind} role="img" aria-label={L.nature_labels[kind]} title={L.nature_labels[kind]}>{kind==='business'?<BriefcaseBusiness size={17} aria-hidden="true"/>:<Wrench size={17} aria-hidden="true"/>}</span>)}</span>;
 const governanceView=phase==='gouvernance';
 const active=W.phases.find((p:Data)=>p.id===phase);
 const format=(value:number|null,unit='JH')=>value===null?L.pending:n(value,Math.abs(value-Math.round(value))<1e-7?0:1)+' '+unit;
 const teamValue=(t:Data,p:Data)=>t.totals[p.id]===null?(p.pending?L.pending:p.id==='fonctionnement'?L.unallocated:L.no_assignment):format(t.totals[p.id],p.unit);
 const share=(value:number|null)=>value===null?L.unknown:n(value,1)+' %';
 useEffect(()=>{
  if(option!=='java-spring'){setSelected(null);setTeam(null);return;}
  const row=[...W.phases.flatMap((p:Data)=>p.rows),...W.governance.rows].find((r:Data)=>r.id===focus||r.id==='core/'+focus||r.id==='core/'+focus+'-java-spring');
  setSelected(row||null);
  setTeam(W.teams.find((t:Data)=>t.id===focus)||null);
 },[focus,W,option]);
 const functionTable=(rows:Data[],methods=false)=><div className="charge-table-scroll" tabIndex={0}>
  <table className="eco-table charge-table"><thead><tr><th scope="col">{L.unit}{methods&&<small>{L.covered_scope}</small>}</th>
   {methods&&<th scope="col">{L.methods}</th>}
   <th scope="col">{L.charge}</th><th scope="col">{L.teams}</th><th scope="col"><span className="sr-only">{L.details}</span></th>
  </tr></thead><tbody>{rows.map(row=><tr key={row.id} data-charge-function={row.id}>
   <th scope="row"><span className="charge-function-name">{natureIcons(row.natures)}{row.label}</span>{methods&&(row.scope_summary.length?scopeList(row.scope_summary):<small>{row.natures.includes('it')?L.technical_scope:row.scope||L.business_scope}</small>)}</th>
   {methods&&<td>{row.methods.every((m:Data)=>m.jh===null)?L.historical_method:row.methods.map((m:Data)=><span className="charge-method" key={m.id}><span>{L.method_labels[m.id]||m.label}</span><b>{m.jh===null?L.historical_method:format(m.jh)}</b></span>)}</td>}
   <td className="charge-final">{format(row.jh,row.unit)}{row.summary&&<small className="charge-decision-summary">{row.summary}</small>}</td>
   <td>{row.contributions.map((c:Data)=><span className="charge-contribution" key={c.team_ref||'unallocated'}>{c.label} <b>{share(c.share_pct)}</b></span>)}</td>
   <td><Information summary={row.rationale} label={L.details+' · '+row.label} onClick={()=>setSelected(row)}/></td>
  </tr>)}</tbody></table>
 </div>;
 const teamCard=(id:string)=>{
  const t=W.teams.find((t:Data)=>t.id===id),kind=D.team_types.find((k:Data)=>k.id===t.type);
  return <button type="button" className="delivery-team-node charge-team" data-team={id} data-team-type={t.type} key={id}
   style={{'--team-color':kind.color} as CSSProperties} onClick={()=>setTeam(t)}>
   <strong>{t.label}</strong><TeamBadge team={t}/>
   {active&&<ul className="charge-team-functions">{t.functions.filter((f:Data)=>f.phase_ref===phase).map((f:Data)=><li key={f.function_ref}>{f.label} · {share(f.share_pct)}</li>)}</ul>}
   <dl>{(active?[active]:W.phases).map((p:Data)=><div key={p.id}><dt>{p.label}</dt><dd>{teamValue(t,p)}</dd></div>)}</dl>
  </button>;
 };
 const acquisitionSummary=W.acquisition_summaries[option];
 const governanceCard=<article className="charge-governance" data-governance-annual><span>{L.governance_annual}</span><strong>{format(W.governance.annual_jh,L.annual_unit)}</strong><dl>{W.governance.horizons.map((h:Data)=><div key={h.years}><dt>{h.years+' '+L.years}</dt><dd>{format(h.jh)}</dd></div>)}</dl></article>;
 const summary=<div className="charge-totals">{W.phases.map((p:Data)=><a key={p.id} href={'#charges-'+p.id+'?option=java-spring'}>
  <span>{p.label}</span><strong>{format(p.total_jh,p.unit)}</strong>
 </a>)}</div>;
 return <div className="essential-page charge-dossier" data-charge-phase={phase||'overview'}>
  {!phase&&<section className="charge-summary" aria-label={L.total}>
   <div><span>{option==='java-spring'?L.product:L.buy_phase_labels.acquisition}</span><strong>{format(acquisitionSummary.product_jh)}</strong></div>
   <div data-governance-annual><span>{L.governance_annual}</span><strong>{format(W.governance.annual_jh,L.annual_unit)}</strong></div>
   <div className="charge-global"><span>{option==='java-spring'?L.global_make:L.global_buy}</span><dl>{acquisitionSummary.horizons.map((h:Data)=><div key={h.years}><dt>{h.years+' '+L.years}</dt><dd>{format(h.jh)}</dd></div>)}</dl></div>
  </section>}
  {phase==='acquisition'&&<nav className="charge-view-tabs" aria-label={L.overview}>{[['table',L.table_tab],['teams',L.teams_tab]].map(([id,label])=><a key={id} href={'#'+pageId+'?option='+option+'&view='+id} aria-current={(teamsView?id==='teams':id==='table')?'page':undefined}>{id==='table'?<Table2 size={18}/>:<Network size={18}/>}<span>{label}</span></a>)}</nav>}
  {phase==='acquisition'&&<div className="charge-totals"><article><span>{option==='java-spring'?L.product:L.buy_phase_labels.acquisition}</span><strong>{format(acquisitionSummary.product_jh)}</strong></article></div>}
  {governanceView?<><div className="charge-totals">{governanceCard}</div><p>{L.governance_scope}</p>{functionTable(W.governance.rows)}</>:option!=='java-spring'?(teamsView&&phase?<p>{L.buy_team_scope}</p>:phase?<BuyCharges phase={phase} option={option}/>:<div className="charge-totals">{W.option_summaries[option].map((p:Data)=><a key={p.id} href={'#charges-'+p.id+'?option='+option}><span>{p.label}</span><strong>{format(p.jh,p.unit)}</strong></a>)}</div>):<>
   {!active||teamsView?<>
    {!active&&summary}
    {!active&&<><h2>{L.teams}</h2>
    <div className="charge-table-scroll"><table className="eco-table charge-table"><thead><tr><th>{L.teams}</th>{W.phases.map((p:Data)=><th key={p.id}>{p.label}<small>{p.unit}</small></th>)}</tr></thead>
     <tbody>{[...W.teams,{id:'unallocated',label:L.unallocated,totals:Object.fromEntries(W.phases.map((p:Data)=>[p.id,p.pending?null:p.rows.reduce((sum:number,r:Data)=>sum+r.contributions.filter((c:Data)=>c.team_ref===null).reduce((s:number,c:Data)=>s+(c.jh||0),0),0)]))}].map(t=><tr key={t.id}><th scope="row">{t.label}</th>{W.phases.map((p:Data)=><td key={p.id}>{teamValue(t,p)}</td>)}</tr>)}</tbody>
    </table></div></>}
    {!active&&<h2>{L.map}</h2>}{!active&&<p className="charge-period">{L.period_note}</p>}
    <div className="delivery-target charge-team-map"><div className="delivery-target-layers">{D.target_topology.layers.map((layer:Data)=><section className="delivery-target-layer" key={layer.id}><h3>{layer.label}</h3>{(layer.rows||[layer.team_refs]).map((row:string[],index:number)=><div className="delivery-target-teams" key={index}>{row.map(teamCard)}</div>)}</section>)}</div>
     <section className="delivery-target-transverse"><h3>{D.target_topology.transverse.label}</h3>{D.target_topology.transverse.team_refs.map(teamCard)}</section>
    </div>
   </>:active.pending?<p className="charge-pending" data-integration-pending>{L.integration_note}</p>:<>
    {phase!=='acquisition'&&<><div className="charge-totals"><article><span>{L.total}</span><strong>{format(active.total_jh,active.unit)}</strong></article></div><h2>{L.activities}</h2></>}
    {functionTable(active.rows.filter((r:Data)=>r.kind!=='governance'),phase==='acquisition')}
   </>}
  </>}
  {selected&&<Drawer title={selected.label} wide className="charge-detail" headerExtra={<div className="charge-detail-total"><strong>{format(selected.jh,selected.unit)}</strong><span>{L.charge}</span></div>} onClose={()=>setSelected(null)}>
   <DetailSection title={selected.bridge?L.mdm_choice:L.rationale} icon={<BadgeCheck size={20}/>} tone="decision">
    {selected.rationale.split(/\n\s*\n|(?<=[.!?])\s+(?=[A-ZÀÉÈÊÎÔ])/).filter(Boolean).map((text:string,i:number)=><p key={i}><MethodText>{text}</MethodText></p>)}
   </DetailSection>
   {selected.justification&&<>
    <DetailSection title={L.reuse} icon={<Blocks size={20}/>}><p>{selected.justification.reuse}</p></DetailSection>
    <DetailSection title={L.exclusions} icon={<Scissors size={20}/>} tone="exclusions"><p>{selected.justification.exclusions}</p></DetailSection>
    <DetailSection title={L.charge_calculation} icon={<Calculator size={20}/>}><p>{selected.justification.calculation}</p><strong>{format(selected.jh,selected.unit)}</strong></DetailSection>
   </>}
   {selected.exclusions.length>0&&<DetailSection title={L.excluded_functions} icon={<Scissors size={20}/>} tone="exclusions"><div className="charge-exclusions">{selected.exclusions.map((e:Data)=><article key={e.id}><h4>{e.label}</h4><p><MethodText>{e.boundary}</MethodText></p><p><MethodText>{e.preserved}</MethodText></p></article>)}</div></DetailSection>}
   {selected.bridge&&<DetailSection title={L.packages} icon={<Blocks size={20}/>}><p>{L.mdm_bridge}</p><div className="charge-parts">{selected.bridge.parts.map((p:Data)=><article key={p.label}><span>{p.label}</span><strong>{format(p.jh)}</strong></article>)}</div><p className="charge-reference">{L.mdm_reference} · <strong>{format(selected.bridge.reference_jh)}</strong></p></DetailSection>}
   {selected.scope&&<DetailSection title={L.scope} icon={<Map size={20}/>}><ul>{selected.scope.split(' · ').map((s:string)=><li key={s}>{s}</li>)}</ul></DetailSection>}
   {selected.methods.length>0&&<DetailSection title={L.methods} icon={<Calculator size={20}/>}><div className="charge-detail-scroll"><table className="eco-table"><thead><tr><th>{L.methods}</th><th>{L.days}</th></tr></thead><tbody>{selected.methods.map((m:Data)=><tr key={m.id}><th>{m.label}<small>{m.method}</small><small>{m.scope_note}</small></th><td>{m.jh===null?L.historical_method:format(m.jh)}</td></tr>)}</tbody></table></div></DetailSection>}
   {selected.packages.length>0&&<DetailSection title={L.packages} icon={<Blocks size={20}/>}><div className="charge-detail-scroll"><table className="eco-table"><thead><tr><th>{L.unit}</th><th>{L.days}</th></tr></thead><tbody>{selected.packages.map((p:Data)=><tr key={p.id}><th>{p.label}<small>{p.scope}</small></th><td>{format(p.jh)}</td></tr>)}</tbody></table></div></DetailSection>}
   {selected.terms.length>0&&<DetailSection title={L.terms} icon={<Calculator size={20}/>}><div className="charge-detail-scroll"><table className="eco-table"><tbody>{selected.terms.filter((t:Data)=>t.unit_jh!==0).map((t:Data)=><tr key={t.id}><th>{t.basis||t.unit}</th><td>{n(t.quantity,1)} {t.unit===L.months?t.unit:''} × {format(t.unit_jh)}</td></tr>)}</tbody></table></div></DetailSection>}
   {selected.cosmic&&<DetailSection title={L.cosmic_count} icon={<Calculator size={20}/>}>
    <p>{selected.cosmic.counting_basis}</p><p>{selected.cosmic.boundary}</p><p>{selected.cosmic.family_rule}</p>
    <div className="charge-parts">{selected.cosmic.groups.map((g:Data)=><article key={g.id}><span>{L.cosmic_groups[g.id]}</span><strong>{n(g.cfp,0)} {L.cosmic_cfp}</strong></article>)}</div>
    <p>{L.cosmic_conversion} : {n(selected.cosmic.cfp,0)} {L.cosmic_cfp} × {n(selected.cosmic.parameters.hours_per_CFP,0)} {L.cosmic_hours_per_cfp} × {n(selected.cosmic.parameters.factor,1)} ÷ {n(selected.cosmic.parameters.day_hours,0)} {L.cosmic_hours_per_day} = <strong>{format(selected.cosmic.jh)}</strong></p>
    <p>{selected.cosmic.activity_scope}</p>
    <div className="charge-detail-scroll"><table className="eco-table"><thead><tr><th>{L.cosmic_process}</th><th>{L.cosmic_movements}</th><th>{L.cosmic_cfp}</th></tr></thead><tbody>{selected.cosmic.processes.map((p:Data)=><tr key={p.id}><th>{p.label}<small>{p.functional_user}</small></th><td>{Object.entries(p.movements).map(([kind,groups])=><div key={kind}><b>{kind}</b> · {(groups as string[]).join(', ')||'—'}</div>)}</td><td>{n(p.cfp,0)}</td></tr>)}</tbody></table></div>
   </DetailSection>}
   {selected.product_functions.length>0&&<DetailSection title={L.product_functions} icon={<Wrench size={20}/>}><ul>{selected.product_functions.map((f:Data)=><li key={f.id}>{natureIcons([f.nature])}<strong>{f.label}</strong><p>{f.boundary}</p></li>)}</ul></DetailSection>}
   <DetailSection title={L.teams} icon={<Users size={20}/>}><div className="charge-detail-scroll"><table className="eco-table"><thead><tr><th>{L.teams}</th><th>{L.team_share}</th><th>{L.charge}</th><th>{L.allocation_basis}</th></tr></thead><tbody>{selected.contributions.map((c:Data)=><tr key={c.team_ref||'unallocated'}><th>{c.label}</th><td>{share(c.share_pct)}</td><td>{format(c.jh,selected.unit)}</td><td>{c.basis}</td></tr>)}</tbody></table></div></DetailSection>
   <DetailSection title={L.capabilities} icon={<Layers size={20}/>}><div className="charge-detail-scroll">{selected.capabilities.length?<table className="eco-table"><thead><tr><th>{L.capabilities}</th><th>{L.capability_share}</th></tr></thead><tbody>{selected.capabilities.map((c:Data)=><tr key={c.id}><th>{c.label}</th><td>{share(c.share_pct)}</td></tr>)}</tbody></table>:<p>{selected.natures.includes('it')?L.technical_scope:L.business_scope}</p>}</div></DetailSection>
   <DetailSection title={L.proofs} icon={<FileText size={20}/>}><div className="charge-proof-links">{selected.proofs.map((path:string)=><SourceLink key={path} path={path}>{path.split('/').pop()||L.proofs}</SourceLink>)}</div></DetailSection>
  </Drawer>}
  {team&&<Drawer title={team.label} wide onClose={()=>setTeam(null)}>
   {active&&<><h3>{L.covered_scope}</h3>{scopeList(team.scope_summaries[phase!])}</>}
   {!active&&<><h3>{L.capabilities}</h3>{team.capability_scope.length?<ul>{team.capability_scope.map((c:Data)=><li key={c.id}>{c.label}</li>)}</ul>:<p>{L.no_mapping}</p>}</>}
   <h3>{L.mapping}</h3><table className="eco-table"><thead><tr><th>{L.unit}</th><th>{L.team_share}</th><th>{L.capabilities}</th></tr></thead><tbody>{team.functions.filter((row:Data)=>!phase||row.phase_ref===phase).map((row:Data)=><tr key={row.function_ref}><th>{row.label}</th><td>{share(row.share_pct)}</td><td>{row.capabilities.map((c:Data)=><span className="charge-contribution" key={c.id}>{c.label} · {share(c.share_pct)}</span>)}</td></tr>)}</tbody></table>
  </Drawer>}
 </div>;
}

function BuyCharges({phase,option}:{phase:string;option:string}){
 const {data}=useStudy(),{n}=useFormat(),L=data.content.delivery_organisation.charge_dossier.labels;
 const [reading,setReading]=useState<Data|null>(null),[failed,setFailed]=useState(false);
 useEffect(()=>{let live=true;setFailed(false);
  request<Data>('/api/gross-evaluations?model_version='+encodeURIComponent(data.model_version)).then(result=>{
   if(result.model_version!==data.model_version)throw Error('version');
   if(live)setReading(result);
  }).catch(()=>{if(live)setFailed(true);});
  return()=>{live=false;};
 },[data.model_version]);
 if(failed)return <p role="alert">{data.ui.errors.network}</p>;
 if(!reading)return <p role="status">{data.ui.labels.loading}</p>;
 const R=reading.phases[phase].options[option];
 if(phase==='integration')return <p data-integration-pending>{L.integration_note}</p>;
 return <>{R.groups.map((g:Data)=>g.rows.some((r:Data)=>r.unit.startsWith('JH'))&&<section key={g.id}><h2>{g.title}</h2><table className="eco-table"><thead><tr><th>{L.unit}</th><th>{L.charge}</th></tr></thead><tbody>{g.rows.filter((r:Data)=>r.unit.startsWith('JH')).map((r:Data)=><tr key={r.id}><th>{r.label}</th><td>{r.value===null?L.pending:n(r.value,1)+' '+r.unit}</td></tr>)}</tbody></table></section>)}
  {R.quotes.length>0&&<h2>{L.source_amounts}</h2>}
  {R.quotes.map((q:Data)=><section key={q.id}><h3>{q.title}</h3><table className="eco-table"><tbody>{q.entries.map((e:Data)=><tr key={e.source_id}><th>{e.label}<small>{e.period}</small></th><td>{e.amount_eur!==undefined?n(e.amount_eur,0)+' '+L.currency:e.amounts?.map((a:Data)=><div key={a.year}>{a.year} · {n(a.amount_eur,0)} {L.currency}</div>)}</td><td>{q.proofs.map((p:Data)=><SourceLink key={p.path} path={p.path}>{L.proofs}</SourceLink>)}</td></tr>)}</tbody></table></section>)}
 </>;
}
