import {useMemo,useState,type CSSProperties} from 'react';
import {Background,Controls,ReactFlow,type Node,type NodeProps} from '@xyflow/react';
import {Maximize2} from 'lucide-react';
import {useStudy,type Data} from './context';
import {phaseReadingHash} from './economicNavigation';
import {useReadingContext} from './ReadingScopeContext';
import {InteractionMark,TeamBadge,TopologyAttribution} from './TeamTopology';
import '@xyflow/react/dist/style.css';
import './deliveryTopology.css';

type TeamNode=Node<{team:Data;kind:Data;relations:Data[];columns:number;active:boolean;interactionId:string;onTeam:()=>void;onInteraction:(id:string)=>void},'team'>;
// Presentation coordinates only. The architecture is read from bottom to top.
const architecture:Record<string,{x:number;y:number;width:number;height:number;columns?:number}>={
 'sourcing-procurement':{x:0,y:0,width:280,height:100},
 b2c:{x:308,y:0,width:280,height:100},
 wholesale:{x:616,y:0,width:280,height:100},
 'master-data':{x:120,y:136,width:300,height:100},
 services:{x:476,y:136,width:300,height:100},
 portal:{x:168,y:272,width:560,height:156},
 'case-management':{x:0,y:464,width:280,height:310},
 'master-plan-supply-policy':{x:308,y:464,width:280,height:310},
 'inventory-availability':{x:616,y:464,width:280,height:310},
 paas:{x:0,y:810,width:896,height:316,columns:3},
 integration:{x:940,y:206,width:208,height:600},
};
function TopologyNode({data}:NodeProps<TeamNode>){
 const {team,kind}=data;
 return <div className="tt-node tt-architecture-node" data-team-type={team.type} data-team={team.id} style={{'--team-color':kind.color} as CSSProperties}><div className="tt-node-surface"/><div className="tt-node-copy"><button className="tt-team-heading nodrag nopan" aria-pressed={data.active} onClick={event=>{event.stopPropagation();data.onTeam();}}><small>{kind.label}</small><strong>{team.label}</strong></button>{data.relations.length>0&&<div className="tt-team-interactions" style={{gridTemplateColumns:`repeat(${data.columns},minmax(0,1fr))`}}>{data.relations.map(r=><button className="tt-relation-chip nodrag nopan" key={r.id} data-relation={r.id} data-source={r.source} data-target={r.target} data-selected={data.interactionId===r.id} aria-pressed={data.interactionId===r.id} aria-label={r.accessibleLabel} title={r.accessibleLabel} onClick={event=>{event.stopPropagation();data.onInteraction(r.id);}}><InteractionMark mode={r.mode} color={r.color}/><span>{r.targetLabel}</span></button>)}</div>}</div></div>;
}
const nodeTypes={team:TopologyNode};

export function TeamInteractionMap({option}:{option:string}){
 const {data}=useStudy(),D=data.content.delivery_organisation,L=D.labels,context=useReadingContext();
 const [selection,setSelection]=useState<{kind:'team'|'interaction';id:string}|null>(null),[canvasKey,setCanvasKey]=useState(0);
 const relation=selection?.kind==='interaction'?D.interactions.find((r:Data)=>r.id===selection.id):undefined;
 const team=selection?.kind==='team'?D.teams.find((t:Data)=>t.id===selection.id):undefined;
 const name=(id:string)=>D.teams.find((t:Data)=>t.id===id)?.label||id;
 const mode=relation?D.interaction_modes.find((m:Data)=>m.id===relation.mode):undefined;
 const nodes=useMemo<TeamNode[]>(()=>D.teams.map((t:Data,i:number)=>{
  const layout=architecture[t.id]||{x:1200+(i%2)*300,y:Math.floor(i/2)*220,width:280,height:210};
  const kind=D.team_types.find((k:Data)=>k.id===t.type);
  const relations=D.interactions.filter((r:Data)=>r.source===t.id).map((r:Data)=>{
   const m=D.interaction_modes.find((m:Data)=>m.id===r.mode);
   return {...r,color:m.color,targetLabel:name(r.target),accessibleLabel:t.label+' · '+m.label+' · '+name(r.target)};
  });
  return {id:t.id,type:'team' as const,data:{team:t,kind,relations,columns:layout.columns||1,active:team?.id===t.id,interactionId:relation?.id||'',onTeam:()=>setSelection(old=>old?.kind==='team'&&old.id===t.id?null:{kind:'team',id:t.id}),onInteraction:(id:string)=>setSelection({kind:'interaction',id})},position:{x:layout.x,y:layout.y},style:{width:layout.width,height:layout.height},selected:team?.id===t.id||relation?.source===t.id||relation?.target===t.id,ariaLabel:t.label+' · '+kind.label};
 }),[D,selection]);
 return <><div className="delivery-map-toolbar"><p>{L.graph_gestures}</p><button className="delivery-map-reset" onClick={()=>setCanvasKey(k=>k+1)}><Maximize2 size={16} aria-hidden="true"/>{L.graph_reset}</button></div><div className="delivery-map-workspace"><section className="delivery-map-canvas delivery-architecture-canvas" aria-label={L.interactions_title}><div className="delivery-map-flow" aria-hidden="true">{L.flow_direction}</div><ReactFlow<TeamNode> key={canvasKey} nodes={nodes} edges={[]} nodeTypes={nodeTypes} nodesDraggable={false} nodesConnectable={false} edgesReconnectable={false} elementsSelectable={false} deleteKeyCode={null} nodesFocusable={false} onNodeClick={(_,node)=>setSelection({kind:'team',id:node.id})} onPaneClick={()=>setSelection(null)} fitView fitViewOptions={{padding:.08,maxZoom:1}} minZoom={.2} maxZoom={1.6} zoomOnScroll={false} zoomOnDoubleClick={false} preventScrolling={false} ariaLabelConfig={data.content.framework_graph.aria}><Background gap={24} size={1} color="#D5DEDA"/><Controls showInteractive={false}/></ReactFlow></section><aside className="delivery-map-inspector" aria-label={L.graph_details} aria-live="polite">{relation?<><p className="delivery-inspector-kicker">{mode.label}</p><h3 className="delivery-interaction-pair"><span>{name(relation.source)}</span><InteractionMark mode={mode.id} color={mode.color}/><span>{name(relation.target)}</span></h3><p>{relation.object}</p><h4>{L.phase}</h4><p>{D.phases.filter((p:Data)=>relation.phases.includes(p.id)).map((p:Data)=>p.label).join(' · ')}</p><h4>{L.exit}</h4><p>{relation.exit_criterion||L.permanent_service}</p></>:team?<><TeamBadge team={team}/><h3>{team.label}</h3><p>{team.mission}</p><p>{team.boundary}</p><a className="text-button" href={phaseReadingHash({...context,page:'equipes-produit',option,focus:team.id})!}>{L.graph_open_team}</a></>:<><p className="delivery-inspector-kicker">{L.graph_details}</p><h3>{L.graph_inspect_title}</h3><p>{L.graph_inspect_help}</p></>}</aside></div><div className="delivery-legend">{D.interaction_modes.map((m:Data)=><span key={m.id}><InteractionMark mode={m.id} color={m.color}/>{m.label}</span>)}</div><p className="delivery-map-reading">{L.graph_reading}</p><TopologyAttribution/></>;
}
