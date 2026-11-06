import {Info} from 'lucide-react';
import {Drawer} from './components';
import {useState,type CSSProperties} from 'react';
import {useStudy,useFormat,type Data} from './context';
import {MethodText} from './MethodDocument';
import {phaseReadingHash} from './economicNavigation';
import {useReadingContext} from './ReadingScopeContext';
import {DurableTeamsPrinciple} from './TeamPhasePage';
import './deliveryOrganisation.css';
import {TeamBadge,TeamDirectory,TeamMark,InteractionMark,TopologyAttribution} from './TeamTopology';
import {TeamInteractionMap} from './TeamInteractionMap';

type Page='organisation-delivery'|'organisation-cible'|'equipes-produit'|'integration-transverse'|'gouvernance-delivery';

function TeamTheoryIntroduction(){
 const {data}=useStudy(),L=data.content.delivery_organisation.labels;
 return <><section className="delivery-book-panel">
  <a className="delivery-book-cover" href={L.book_href}><img src={L.book_cover} alt={L.book_alt} width="180" height="270"/></a>
  <div className="delivery-book-copy"><h2>{L.book_title}</h2><p className="delivery-book-subtitle">{L.book_subtitle}</p><p className="delivery-book-edition">{L.book_edition}</p><p>{L.theory_intro}</p>
   <div className="delivery-book-authors">{['matthew','manuel'].map(id=><a key={id} href={L.authors_href}><img src={L['author_'+id+'_image']} alt={L['author_'+id]} width="64" height="64"/><span><strong>{L['author_'+id]}</strong><small>{L['author_'+id+'_role']}</small></span></a>)}</div>
   <a className="delivery-book-link" href={L.book_href}>{L.book_link} <span aria-hidden="true">↗</span></a><small className="delivery-image-credit">{L.book_credit}</small>
  </div>
 </section><section className="delivery-conway"><h2>{L.conway_title}</h2><div className="delivery-conway-grid">{['law','inverse'].map(kind=><article key={kind}><h3>{L['conway_'+kind+'_title']}</h3><div className="delivery-conway-direction"><span>{L['conway_'+kind+'_from']}</span><span aria-hidden="true">→</span><span>{L['conway_'+kind+'_to']}</span></div><p>{L['conway_'+kind+'_text']}</p><a href={L['conway_'+kind+'_href']}>{L['conway_'+kind+'_source']}</a></article>)}</div><aside className="delivery-conway-flow"><strong>{L.conway_flow_title}</strong><p>{L.conway_flow_text}</p></aside></section></>;
}

function OrganisationGraph(){
 const {data}=useStudy(),D=data.content.delivery_organisation,L=D.labels,context=useReadingContext();
 const {layers,transverse}=D.target_topology;
 const teams=new Map<string,Data>(D.teams.map((team:Data)=>[team.id,team]));
 const card=(id:string)=>{
  const team=teams.get(id)!;
  const kind=D.team_types.find((type:Data)=>type.id===team.type);
  return <a key={id} className="delivery-team-node" data-team={id} data-team-type={team.type}
   style={{'--team-color':kind.color} as CSSProperties}
   href={phaseReadingHash({...context,page:'equipes-produit',option:'java-spring',focus:id})!}>
   <strong>{team.label}</strong><TeamBadge team={team}/>
  </a>;
 };
 return <figure className="delivery-target-figure">
  <figcaption><p>{L.target_note}</p><strong>{L.flow_direction}</strong></figcaption>
  <div className="delivery-target" role="group" aria-label={L.graph_label}>
   <div className="delivery-target-layers">
    {layers.map((layer:Data)=><section key={layer.id} className="delivery-target-layer" data-topology-layer={layer.id}>
     <h3>{layer.label}</h3>
     {(layer.rows||[layer.team_refs]).map((row:string[],index:number)=><div className="delivery-target-teams" key={index}>{row.map(card)}</div>)}
    </section>)}
   </div>
   <section className="delivery-target-transverse" aria-label={transverse.label}>
    <h3>{transverse.label}</h3>
    <div className="delivery-target-teams">{transverse.team_refs.map(card)}</div>
   </section>
  </div>
 </figure>;
}

export function DeliveryOrganisationPage({page,option,focus,view}:{page:Page;option:string;focus?:string;view?:string}){
 view=undefined;
 const {data}=useStudy(),D=data.content.delivery_organisation,L=D.labels,context=useReadingContext();
 const team=D.teams.find((t:Data)=>t.id===focus)||D.teams[0];
 const relations=D.interactions;
 const name=(id:string)=>D.teams.find((t:Data)=>t.id===id)?.label||id;
 return <div className="essential-page economic-dossier delivery-page">
  {page==='organisation-delivery'&&<><DurableTeamsPrinciple/><TeamTheoryIntroduction/><p>{L.team_types_note}</p><section><h2>{L.types_title}</h2><div className="delivery-type-grid">{D.team_types.map((t:Data)=><article key={t.id} data-team-type={t.id} style={{'--team-color':t.color} as CSSProperties}><h3><TeamMark type={t.id} color={t.color}/>{t.label}</h3><p>{t.definition}</p></article>)}</div></section><section><h2>{L.modes_title}</h2><div className="delivery-type-grid delivery-mode-grid">{D.interaction_modes.map((m:Data)=><article key={m.id} style={{'--team-color':m.color} as CSSProperties}><InteractionMark mode={m.id} color={m.color} illustrated/><h3>{m.label}</h3><p>{m.definition}</p></article>)}</div></section><TopologyAttribution/><section><h2>{L.references_title}</h2><ul>{D.references.map((ref:Data)=><li key={ref.href}><a href={ref.href}>{ref.label}</a></li>)}</ul></section></>}
  {page==='organisation-cible'&&<>
   <h2>{L.target_title}</h2><OrganisationGraph/><TopologyAttribution/>
   <aside className="delivery-board"><strong>{D.governance.label}</strong><p>{D.governance.mission}</p></aside>
   <DurableTeamsPrinciple/><p>{L.lifecycle_note}</p><p>{L.target_evolution}</p>
  </>}
  {page==='equipes-produit'&&<div className="delivery-team-browser"><TeamDirectory selected={team.id} option={option} view={view}/><article className="delivery-team-sheet" data-team={team.id}>
   <TeamBadge team={team}/><h2>{team.label}</h2>
   <a className="delivery-team-position" href="#organisation-cible">{D.target_topology.layers.find((layer:Data)=>layer.team_refs?.includes(team.id)||layer.rows?.flat().includes(team.id))?.label||D.target_topology.transverse.label}</a>
   <p className="delivery-team-mission">{team.mission}</p>
   <h3>{L.scope_title}</h3><p>{team.boundary}</p>
   <h3>{L.responsibilities_title}</h3><div className="delivery-lifecycle">{D.phases.map((p:Data)=><section key={p.id}><h4>{p.label}</h4><p>{team.responsibilities[p.id]}</p></section>)}</div>
   <h3>{L.interactions_title}</h3><div className="delivery-team-partners">{D.interaction_modes.map((mode:Data)=>{
    const peers=[...new Set<string>(relations.filter((r:Data)=>r.mode===mode.id&&(r.source===team.id||r.target===team.id)).map((r:Data)=>r.source===team.id?r.target:r.source))];
    return peers.length>0&&<section key={mode.id}><h4><InteractionMark mode={mode.id} color={mode.color}/>{mode.label}</h4><ul>{peers.map(id=><li key={id}><a href={phaseReadingHash({...context,page:'equipes-produit',option,focus:id})!}>{name(id)}</a></li>)}</ul></section>;
   })}</div>
  </article></div>}
  {page==='integration-transverse'&&<><h2>{L.interactions_title}</h2><p>{L.interaction_note}</p><TeamInteractionMap option={option}/><h3>{L.relationship_contracts}</h3><div className="delivery-table-scroll" role="region" tabIndex={0} aria-label={L.interactions_title}><table className="eco-table"><thead><tr>{[L.source_team,L.target_team,L.mode,L.interaction_object,L.exit].map((text:string)=><th key={text} scope="col">{text}</th>)}</tr></thead><tbody>{relations.map((r:Data)=><tr key={r.id}><th scope="row">{name(r.source)}</th><td>{name(r.target)}</td><td>{D.interaction_modes.find((m:Data)=>m.id===r.mode).label}</td><td>{r.object}</td><td>{r.exit_criterion||L.permanent_service}</td></tr>)}</tbody></table></div></>}
  {page==='gouvernance-delivery'&&<GovernanceSheet/>}
  {option!=='java-spring'&&<p className="delivery-note">{L.buy_note}</p>}

 </div>;
}


function GovernanceSheet(){
 const {data}=useStudy(),{n}=useFormat(),T=data.content.framework.transformation,L=T.pilotage,S=T.build_staffing;
 const [selected,setSelected]=useState<Data|null>(null);
 return <section className="governance-sheet">
  <p>{L.scope}</p>
  <div className="governance-summary"><div><span>{L.total}</span><strong>{n(S.etp,1)} {L.etp}</strong></div><div><span>{L.range}</span><strong>{n(S.min_etp,1)}–{n(S.max_etp,1)} {L.etp}</strong></div></div>
  <div className="delivery-table-scroll"><table className="eco-table"><thead><tr><th>{L.role}</th><th>{L.etp}</th><th>{L.range}</th><th>{L.mission}</th><th><span className="governance-sr-only">{L.detail}</span></th></tr></thead><tbody>{T.roles.map((r:Data)=><tr key={r.id}><th scope="row">{r.nom}</th><td><strong className="governance-etp">{n(r.build_make_etp,1)}</strong></td><td className="governance-range">{n(r.build_make_min_etp,1)}–{n(r.build_make_max_etp,1)}</td><td>{r.build_rationale}</td><td><button className="icon-button" title={r.decision} aria-label={L.detail+' · '+r.nom} onClick={()=>setSelected(r)}><Info size={18}/></button></td></tr>)}</tbody></table></div>
  <p className="governance-note">{L.range_note}</p>
  <div className="governance-flow">
   <article><h3>{L.board_title}</h3><p>{L.board_text}</p></article>
   <div className="governance-flow-link"><span aria-hidden="true">↓</span>{L.decision_flow}</div>
   <article><h3>{L.operations_title}</h3><p>{L.operations_text}</p></article>
   <div className="governance-flow-link"><span aria-hidden="true">↕</span>{L.execution_flow}</div>
   <article><h3>{L.teams_title}</h3><p>{L.teams_text}</p></article>
  </div>
  <aside className="governance-product"><h3>{L.product_title}</h3><p>{L.product_text}</p></aside>
  <p className="governance-note">{L.integration_note}</p>
  {selected&&<Drawer title={selected.nom} onClose={()=>setSelected(null)}><h3>{L.mission}</h3><p>{selected.decision}</p><h3>{L.detail}</h3><p>{selected.build_justification}</p><h3>{L.boundary}</h3><p>{selected.boundary}</p><h3>{L.reinforcement}</h3><p>{selected.reinforcement}</p></Drawer>}
 </section>;
}
