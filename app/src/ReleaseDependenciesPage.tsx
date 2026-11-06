import type {ElkNode} from 'elkjs/lib/elk.bundled.js';
import {useEffect,useMemo,useState} from 'react';
import {BaseEdge,Background,Controls,Handle,MarkerType,Position,ReactFlow,type Edge,type EdgeProps,type Node,type NodeProps} from '@xyflow/react';

import {Info,Maximize2,Play,PackageCheck} from 'lucide-react';
import {useStudy,useFormat,type Data} from './context';
import {Drawer,SourceLink} from './components';
import {TeamBadge} from './TeamTopology';
import '@xyflow/react/dist/style.css';
import './releaseDependencies.css';

type ReleaseNode=Node<{release:Data;charge:string;active:boolean;ports:{id:string;x:number;incoming:boolean}[];onSelect:()=>void},'release'>;
function ReleaseCard({data}:NodeProps<ReleaseNode>){
 const r=data.release;
 return <div className={'release-node'+(data.active?' selected':'')} style={{background:r.color}} data-release={r.id}>{data.ports.map(port=><Handle key={port.id} id={port.id} type={port.incoming?'target':'source'} position={port.incoming?Position.Top:Position.Bottom} style={{left:port.x}}/>)}<button className="release-node-select nodrag nopan" onClick={event=>{event.stopPropagation();data.onSelect();}}>{r.label}</button><TeamBadge team={r}/><span>{data.charge}</span></div>;
}
const nodeTypes={release:ReleaseCard};
function RoutedDependency({id,data,markerEnd,style,label}:EdgeProps){
 const points=data?.points as {x:number;y:number}[]|undefined;
 if(!points?.length)return null;
 let path='M'+points[0].x+','+points[0].y;
 for(let i=1;i<points.length-1;i++){
  const previous=points[i-1],point=points[i],next=points[i+1];
  const before=Math.hypot(point.x-previous.x,point.y-previous.y),after=Math.hypot(next.x-point.x,next.y-point.y);
  const radius=Math.min(18,before/2,after/2);
  if(!before||!after)continue;
  path+=' L'+(point.x+(previous.x-point.x)*radius/before)+','+(point.y+(previous.y-point.y)*radius/before);
  path+=' Q'+point.x+','+point.y+' '+(point.x+(next.x-point.x)*radius/after)+','+(point.y+(next.y-point.y)*radius/after);
 }
 const last=points[points.length-1];path+=' L'+last.x+','+last.y;
 const position=data?.caption as {x:number;y:number}|undefined;
 return <><BaseEdge id={id} path={path} markerEnd={markerEnd} style={style}/>{position&&<g transform={'translate('+position.x+','+position.y+')'} style={{opacity:style?.opacity}}><rect x={-4} y={-2} width={70} height={30} rx={5} fill="white"/><text x={31} y={19} textAnchor="middle" fontSize={18} fontWeight={700} fill="#203832">{label}</text></g>}</>;
}
const edgeTypes={dependency:RoutedDependency};



export function ReleaseDependenciesPage(){
 const {data}=useStudy(),{n}=useFormat(),D=data.content.delivery_organisation.release_dependencies,L=D.labels;
 const [gate,setGate]=useState<'start'|'production'>('start'),[selected,setSelected]=useState<Data|null>(null),[team,setTeam]=useState<string|null>(null),[positions,setPositions]=useState<Record<string,{x:number;y:number}>>({}),[canvas,setCanvas]=useState(0),[routes,setRoutes]=useState<Record<string,Data>>({}),[bounds,setBounds]=useState({width:1200,height:950});
 const links=useMemo<Data[]>(()=>Array.from(new Map<string,Data>(D.constraints.map((c:Data)=>[c.provider_release_ref+'>'+c.consumer_release_ref,c])).values()),[D]);
 const portsFor=(id:string)=>[true,false].flatMap(incoming=>{
  const related=links.filter(c=>(incoming?c.consumer_release_ref:c.provider_release_ref)===id);
  return related.map((c,index)=>({id:c.provider_release_ref+'>'+c.consumer_release_ref+(incoming?'/in':'/out'),incoming,x:280*(index+1)/(related.length+1)}));
 });
 const constraints:Data[]=D.constraints.filter((c:Data)=>c.gate===gate);
 useEffect(()=>{
  let live=true;
  import('elkjs/lib/elk.bundled.js').then(({default:ELK})=>new ELK().layout<ElkNode>({
   id:'root',layoutOptions:{'elk.algorithm':'layered','elk.edgeRouting':'ORTHOGONAL','elk.direction':'DOWN','elk.randomSeed':'1','elk.layered.mergeEdges':'false','elk.spacing.nodeNode':'45','elk.layered.spacing.nodeNodeBetweenLayers':'90','elk.spacing.edgeNode':'35','elk.spacing.edgeEdge':'25','elk.layered.spacing.edgeEdgeBetweenLayers':'25','elk.layered.considerModelOrder.strategy':'NODES_AND_EDGES'},
   children:D.releases.map((r:Data)=>({id:r.id,width:280,height:168,layoutOptions:{'elk.portConstraints':'FIXED_POS'},ports:portsFor(r.id).map(port=>({id:port.id,width:0,height:0,x:port.x,y:port.incoming?0:168,layoutOptions:{'elk.port.side':port.incoming?'NORTH':'SOUTH'}}))})),
   edges:links.map(c=>({id:c.provider_release_ref+'>'+c.consumer_release_ref,sources:[c.provider_release_ref+'>'+c.consumer_release_ref+'/out'],targets:[c.provider_release_ref+'>'+c.consumer_release_ref+'/in'],labels:[{text:'100 %',width:62,height:28}]}))
  })).then(result=>{if(live){setBounds({width:result.width||1200,height:result.height||950});setRoutes(Object.fromEntries((result.edges||[]).map(edge=>{const section=edge.sections?.[0];return [edge.id,{points:section?[section.startPoint,...(section.bendPoints||[]),section.endPoint]:[],caption:edge.labels?.[0]}];})));setPositions(Object.fromEntries((result.children||[]).map(c=>[c.id,{x:c.x||0,y:c.y||0}])));setCanvas(k=>k+1);}}).catch(()=>{});
  return()=>{live=false;};
 },[D]);
 const nodes=useMemo<ReleaseNode[]>(()=>D.releases.map((r:Data,i:number)=>({id:r.id,type:'release',position:positions[r.id]||{x:(i%4)*300,y:Math.floor(i/4)*180},data:{release:r,ports:portsFor(r.id),charge:n(r.jh,0)+' JH',active:r.id===team,onSelect:()=>setTeam(old=>old===r.id?null:r.id)},style:{width:280,height:168},ariaLabel:r.label})),[D,positions,team,n]);
 const edges:Edge[]=constraints.map(c=>({id:c.id,source:c.provider_release_ref,target:c.consumer_release_ref,sourceHandle:c.provider_release_ref+'>'+c.consumer_release_ref+'/out',targetHandle:c.provider_release_ref+'>'+c.consumer_release_ref+'/in',type:'dependency',data:routes[c.provider_release_ref+'>'+c.consumer_release_ref],label:n(c.threshold_pct,0)+' '+L.percent,markerEnd:{type:MarkerType.ArrowClosed,color:gate==='start'?'#526479':'#176b55'},style:{stroke:gate==='start'?'#526479':'#176b55',strokeWidth:team&&(c.provider_release_ref===team||c.consumer_release_ref===team)?3:1.5,opacity:!team||c.provider_release_ref===team||c.consumer_release_ref===team?1:.12},labelStyle:{fontSize:18,fontWeight:700,fill:'#203832',opacity:!team||c.provider_release_ref===team||c.consumer_release_ref===team?1:.12},labelBgStyle:{fill:'#fff'},ariaLabel:c.provider_label+' → '+c.consumer_label+' · '+n(c.threshold_pct,0)+' '+L.percent}));
 const release=D.releases.find((r:Data)=>r.id===team);
 return <div className="release-dependencies essential-page">
  <p>{L.intro}</p><span className="release-assumption">{L.hypothesis}</span>
  <nav className="charge-view-tabs" aria-label={L.details}>{(['start','production'] as const).map(g=><button key={g} type="button" aria-pressed={gate===g} onClick={()=>{setGate(g);setSelected(null);}}>{g==='start'?<Play size={18}/>:<PackageCheck size={18}/>}<span>{L[g]}</span></button>)}</nav>
  <p>{gate==='start'?L.start_note:L.production_note}</p>
  <aside className="release-legend" aria-label={L.legend}><strong>{L.legend}</strong><div><span>{L.supplier}</span><span className={'release-legend-arrow '+gate} aria-hidden="true">⟶</span><span>{L.consumer}</span></div><p>{L.legend_direction}</p><p>{gate==='start'?L.legend_start:L.legend_production}</p><small>{L.legend_threshold}</small></aside>
  <div className="release-toolbar"><small>{L.instruction}</small><button className="secondary" onClick={()=>setTeam(null)}>{L.clear}</button><button className="secondary" onClick={()=>setCanvas(k=>k+1)}><Maximize2 size={16}/>{L.reset}</button></div>
  <div className="release-canvas" style={{width:'100%',height:'auto',minHeight:950,aspectRatio:bounds.width+'/'+bounds.height}} data-layout-ready={Object.keys(positions).length===D.releases.length}><ReactFlow<ReleaseNode> key={canvas} nodes={nodes} edges={edges} nodeTypes={nodeTypes} edgeTypes={edgeTypes} nodesDraggable={false} nodesConnectable={false} edgesReconnectable={false} deleteKeyCode={null} onInit={instance=>{requestAnimationFrame(()=>instance.fitBounds({x:0,y:0,width:bounds.width,height:bounds.height},{padding:.02}));}} minZoom={.15} maxZoom={2} zoomOnScroll={false} preventScrolling={false} onNodeClick={(_,node)=>setTeam(old=>old===node.id?null:node.id)} onEdgeClick={(_,edge)=>setSelected(constraints.find(c=>c.id===edge.id)||null)} onPaneClick={()=>setTeam(null)} ariaLabelConfig={data.content.framework_graph.aria}><Background gap={24}/><Controls showInteractive={false}/></ReactFlow></div>
  {release&&<aside className="release-scope"><h3>{release.label}</h3><p>{release.scope}</p><strong>{n(release.jh,0)+' JH'}</strong><ul>{release.work_contributions.map((c:Data)=><li key={c.work_unit_ref}>{c.label+' · '+n(c.jh,0)+' JH'}</li>)}</ul></aside>}
  <details className="release-register"><summary>{L.table+' · '+constraints.length}</summary><div className="charge-table-scroll"><table className="eco-table"><thead><tr><th>{L.supplier}</th><th>{L.consumer}</th><th>{L.threshold}</th><th>{L.prerequisite}</th><th>{L.details}</th></tr></thead><tbody>{constraints.map(c=><tr key={c.id} data-dependency={c.id}><th>{c.provider_label}</th><td>{c.consumer_label}</td><td>{n(c.threshold_pct,0)+' '+L.percent}</td><td>{c.prerequisite}</td><td><button className="icon-button" aria-label={L.details+' · '+c.provider_label+' → '+c.consumer_label} title={c.justification} onClick={()=>setSelected(c)}><Info size={18}/></button></td></tr>)}</tbody></table></div></details>
  <p className="release-note">{L.excluded}</p><p className="release-note">{L.no_schedule}</p>
  {selected&&<Drawer title={selected.provider_label+' → '+selected.consumer_label} wide onClose={()=>setSelected(null)}><div className="release-detail"><section><h3>{L[selected.gate]+' · '+n(selected.threshold_pct,0)+' '+L.percent}</h3><p>{selected.prerequisite}</p></section><section><h3>{L.work}</h3><p>{selected.work_scope}</p></section><section><h3>{L.basis}</h3><p>{selected.justification}</p><p>{L.progress}</p></section><section><h3>{L.evidence}</h3>{selected.evidence_refs.map((p:string)=><SourceLink key={p} path={p}>{p.split('/').pop()}</SourceLink>)}</section></div></Drawer>}
 </div>;
}
