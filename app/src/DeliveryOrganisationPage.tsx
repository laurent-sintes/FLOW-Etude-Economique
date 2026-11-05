import {type CSSProperties} from 'react';
import {useStudy,type Data} from './context';
import {MethodText} from './MethodDocument';
import {phaseReadingHash} from './economicNavigation';
import {useReadingContext} from './ReadingScopeContext';
import {DurableTeamsPrinciple,TeamPhaseMatrix} from './TeamPhasePage';
import './deliveryOrganisation.css';
import {TeamBadge,TeamDirectory,TeamMark,InteractionMark,TopologyAttribution} from './TeamTopology';
import {TeamWorkScope} from './WorkUnitsPage';
import {TeamInteractionMap} from './TeamInteractionMap';
import {ReadingTabs} from './ConsolidationViews';

type Page='organisation-delivery'|'organisation-cible'|'equipes-produit'|'integration-transverse'|'gouvernance-delivery';

function OrganisationGraph(){
 const {data}=useStudy(),D=data.content.delivery_organisation,L=D.labels,context=useReadingContext();
 const groups=[{id:'enabling',label:L.graph_enable,types:['enabling']},{id:'platform',label:L.graph_services,types:['platform','complicated-subsystem']},{id:'stream',label:L.graph_streams,types:['stream-aligned']}];
 return <figure className="delivery-target-figure"><figcaption>{L.target_note}</figcaption><div className="delivery-target" role="group" aria-label={L.graph_label}>{groups.map(group=><section key={group.id} className={'delivery-target-'+group.id}><h3>{group.label}</h3>{D.teams.filter((t:Data)=>group.types.includes(t.type)).map((team:Data)=><a className="delivery-team-node" data-team-type={team.type} key={team.id} style={{'--team-color':D.team_types.find((t:Data)=>t.id===team.type).color} as CSSProperties} href={phaseReadingHash({...context,page:'equipes-produit',option:'java-spring',focus:team.id})!}><TeamBadge team={team}/><strong>{team.label}</strong><span>{team.mission}</span></a>)}</section>)}</div><aside className="delivery-board"><strong>{D.governance.label}</strong><p>{D.governance.mission}</p></aside></figure>;
}

export function DeliveryOrganisationPage({page,option,focus,view}:{page:Page;option:string;focus?:string;view?:string}){
 const {data}=useStudy(),D=data.content.delivery_organisation,L=D.labels,context=useReadingContext();
 const team=D.teams.find((t:Data)=>t.id===focus)||D.teams[0];
 const relations=D.interactions;
 const name=(id:string)=>D.teams.find((t:Data)=>t.id===id)?.label||id;
 return <div className="essential-page economic-dossier delivery-page">
  {page==='organisation-delivery'&&<><DurableTeamsPrinciple/><section><h2>{L.theory_title}</h2><p>{L.theory_intro}</p><p>{L.book}</p><p>{L.team_types_note}</p></section><section><h2>{L.types_title}</h2><div className="delivery-type-grid">{D.team_types.map((t:Data)=><article key={t.id} data-team-type={t.id} style={{'--team-color':t.color} as CSSProperties}><h3><TeamMark type={t.id} color={t.color}/>{t.label}</h3><p>{t.definition}</p></article>)}</div></section><section><h2>{L.modes_title}</h2><div className="delivery-type-grid delivery-mode-grid">{D.interaction_modes.map((m:Data)=><article key={m.id} style={{'--team-color':m.color} as CSSProperties}><InteractionMark mode={m.id} color={m.color} illustrated/><h3>{m.label}</h3><p>{m.definition}</p></article>)}</div></section><TopologyAttribution/><section><h2>{L.conway_title}</h2><p>{L.conway}</p><ul>{D.references.map((ref:Data)=><li key={ref.href}><a href={ref.href}>{ref.label}</a></li>)}</ul></section></>}
  {page==='organisation-cible'&&<><DurableTeamsPrinciple/><h2>{L.target_title}</h2><OrganisationGraph/><TopologyAttribution/><p>{L.lifecycle_note}</p></>}
  {page==='equipes-produit'&&<><ReadingTabs page="equipes-produit" option={option} working={view==='working'} focus={team.id}/><p>{L.team_types_note}</p><div className="delivery-team-browser"><TeamDirectory selected={team.id} option={option} view={view}/><article className="delivery-team-sheet" data-team={team.id}><TeamBadge team={team}/><h2>{team.label}</h2><p>{team.mission}</p><h3>{L.scope_title}</h3><p>{team.boundary}</p><TeamWorkScope team={team.id} working={view==='working'}/><h3>{L.responsibilities_title}</h3><div className="delivery-lifecycle">{D.phases.map((p:Data)=><section key={p.id}><h4>{p.label}</h4><p>{team.responsibilities[p.id]}</p><small>{L.capacity_unknown}</small></section>)}</div><TeamPhaseMatrix team={team.id} working={view==='working'}/><TeamPhaseMatrix team={team.id} costs working={view==='working'}/><p>{L.unknown_note}</p><p>{L.capacity_note}</p><nav className="delivery-reading-navigation" aria-label={L.nav_label}><a href={phaseReadingHash({...context,page:'charges-equipes',option,view:view==='working'?'working':'reference',focus:team.id})!}>{L.charges_link}</a><a href={phaseReadingHash({...context,page:'couts-equipes',option,view:view==='working'?'working':'reference',focus:team.id})!}>{L.costs_link}</a></nav></article></div></>}
  {page==='integration-transverse'&&<><h2>{L.interactions_title}</h2><p>{L.interaction_note}</p><TeamInteractionMap option={option}/><h3>{L.relationship_contracts}</h3><div className="delivery-table-scroll" role="region" tabIndex={0} aria-label={L.interactions_title}><table className="eco-table"><thead><tr>{[L.source_team,L.target_team,L.mode,L.interaction_object,L.exit].map((text:string)=><th key={text} scope="col">{text}</th>)}</tr></thead><tbody>{relations.map((r:Data)=><tr key={r.id}><th scope="row">{name(r.source)}</th><td>{name(r.target)}</td><td>{D.interaction_modes.find((m:Data)=>m.id===r.mode).label}</td><td>{r.object}</td><td>{r.exit_criterion||L.permanent_service}</td></tr>)}</tbody></table></div></>}
  {page==='gouvernance-delivery'&&<><h2>{D.governance.label}</h2><p>{D.governance.mission}</p><p className="delivery-note">{D.governance.funding_note}</p><div className="delivery-table-scroll" role="region" aria-label={L.governance} tabIndex={0}><table className="eco-table"><thead><tr><th scope="col">{L.role}</th><th scope="col">{L.responsibilities}</th></tr></thead><tbody>{data.content.framework.transformation.roles.map((r:Data)=><tr key={r.id}><th scope="row">{r.nom}</th><td><MethodText>{r.mission}</MethodText></td></tr>)}</tbody></table></div><h2>{L.capacity_title}</h2><p>{L.capacity_note}</p><p>{L.lifecycle_note}</p></>}
  {option!=='java-spring'&&<p className="delivery-note">{L.buy_note}</p>}

 </div>;
}
