import {useEffect,useMemo,useState} from 'react';
import {Background,Controls,Handle,MarkerType,Position,ReactFlow,type Edge,type Node,type NodeProps} from '@xyflow/react';

import {Info,Maximize2,Play,PackageCheck} from 'lucide-react';
import {useStudy,useFormat,type Data} from './context';
import {Drawer,SourceLink} from './components';
import {TeamBadge} from './TeamTopology';
import '@xyflow/react/dist/style.css';
import './releaseDependencies.css';

type ReleaseNode=Node<{release:Data;charge:string;active:boolean;onSelect:()=>void},'release'>;
function ReleaseCard({data}:NodeProps<ReleaseNode>){
 const r=data.release;
 return <div className={'release-node'+(data.active?' selected':'')} style={{background:r.color}} data-release={r.id}><Handle type="target" position={Position.Top}/><button className="release-node-select nodrag nopan" onClick={event=>{event.stopPropagation();data.onSelect();}}>{r.label}</button><TeamBadge team={r}/><span>{data.charge}</span><Handle type="source" position={Position.Bottom}/></div>;
}
const nodeTypes={release:ReleaseCard};


export function ReleaseDependenciesPage(){
 const {data}=useStudy(),{n}=useFormat(),D=data.content.delivery_organisation.release_dependencies,L=D.labels;
 const [gate,setGate]=useState<'start'|'production'>('start'),[selected,setSelected]=useState<Data|null>(null),[team,setTeam]=useState<string|null>(null),[positions,setPositions]=useState<Record<string,{x:number;y:number}>>({}),[canvas,setCanvas]=useState(0);
 const constraints:Data[]=D.constraints.filter((c:Data)=>c.gate===gate);
 useEffect(()=>{
  let live=true;
  import('elkjs/lib/elk.bundled.js').then(({default:ELK})=>new ELK().layout({id:'root',layoutOptions:{'elk.algorithm':'layered','elk.direction':'DOWN','elk.spacing.nodeNode':'38','elk.layered.spacing.nodeNodeBetweenLayers':'65'},children:D.releases.map((r:Data)=>({id:r.id,width:220,height:112})),edges:D.constraints.filter((c:Data)=>c.gate==='start').map((c:Data)=>({id:c.id,sources:[c.provider_release_ref],targets:[c.consumer_release_ref]}))})).then(result=>{if(live){setPositions(Object.fromEntries((result.children||[]).map(c=>[c.id,{x:c.x||0,y:c.y||0}])));setCanvas(k=>k+1);}}).catch(()=>{});
  return()=>{live=false;};
 },[D]);
 const nodes=useMemo<ReleaseNode[]>(()=>D.releases.map((r:Data,i:number)=>({id:r.id,type:'release',position:positions[r.id]||{x:(i%4)*300,y:Math.floor(i/4)*180},data:{release:r,charge:n(r.jh,0)+' JH',active:r.id===team,onSelect:()=>setTeam(old=>old===r.id?null:r.id)},style:{width:220,height:112},ariaLabel:r.label})),[D,positions,team,n]);
 const edges:Edge[]=constraints.map(c=>({id:c.id,source:c.provider_release_ref,target:c.consumer_release_ref,type:'smoothstep',label:n(c.threshold_pct,0)+' '+L.percent,markerEnd:{type:MarkerType.ArrowClosed,color:gate==='start'?'#526479':'#176b55'},style:{stroke:gate==='start'?'#526479':'#176b55',strokeWidth:team&&(c.provider_release_ref===team||c.consumer_release_ref===team)?3:1.5,opacity:!team||c.provider_release_ref===team||c.consumer_release_ref===team?1:.12},labelStyle:{fontWeight:650,fill:'#203832',opacity:!team||c.provider_release_ref===team||c.consumer_release_ref===team?1:.12},labelBgStyle:{fill:'#fff'},ariaLabel:c.provider_label+' → '+c.consumer_label+' · '+n(c.threshold_pct,0)+' '+L.percent}));
 const release=D.releases.find((r:Data)=>r.id===team);
 return <div className="release-dependencies essential-page">
  <p>{L.intro}</p><span className="release-assumption">{L.hypothesis}</span>
  <nav className="charge-view-tabs" aria-label={L.details}>{(['start','production'] as const).map(g=><button key={g} type="button" aria-pressed={gate===g} onClick={()=>{setGate(g);setSelected(null);}}>{g==='start'?<Play size={18}/>:<PackageCheck size={18}/>}<span>{L[g]}</span></button>)}</nav>
  <p>{gate==='start'?L.start_note:L.production_note}</p>
  <div className="release-toolbar"><small>{L.instruction}</small><button className="secondary" onClick={()=>setTeam(null)}>{L.clear}</button><button className="secondary" onClick={()=>setCanvas(k=>k+1)}><Maximize2 size={16}/>{L.reset}</button></div>
  <div className="release-canvas" data-layout-ready={Object.keys(positions).length===D.releases.length}><ReactFlow<ReleaseNode> key={canvas} nodes={nodes} edges={edges} nodeTypes={nodeTypes} nodesDraggable={false} nodesConnectable={false} edgesReconnectable={false} deleteKeyCode={null} fitView fitViewOptions={{padding:.08}} minZoom={.15} maxZoom={2} zoomOnScroll={false} preventScrolling={false} onNodeClick={(_,node)=>setTeam(old=>old===node.id?null:node.id)} onEdgeClick={(_,edge)=>setSelected(constraints.find(c=>c.id===edge.id)||null)} onPaneClick={()=>setTeam(null)} ariaLabelConfig={data.content.framework_graph.aria}><Background gap={24}/><Controls showInteractive={false}/></ReactFlow></div>
  {release&&<aside className="release-scope"><h3>{release.label}</h3><p>{release.scope}</p><strong>{n(release.jh,0)+' JH'}</strong><ul>{release.work_contributions.map((c:Data)=><li key={c.work_unit_ref}>{c.label+' · '+n(c.jh,0)+' JH'}</li>)}</ul></aside>}
  <details className="release-register"><summary>{L.table+' · '+constraints.length}</summary><div className="charge-table-scroll"><table className="eco-table"><thead><tr><th>{L.supplier}</th><th>{L.consumer}</th><th>{L.threshold}</th><th>{L.prerequisite}</th><th>{L.details}</th></tr></thead><tbody>{constraints.map(c=><tr key={c.id} data-dependency={c.id}><th>{c.provider_label}</th><td>{c.consumer_label}</td><td>{n(c.threshold_pct,0)+' '+L.percent}</td><td>{c.prerequisite}</td><td><button className="icon-button" aria-label={L.details+' · '+c.provider_label+' → '+c.consumer_label} title={c.justification} onClick={()=>setSelected(c)}><Info size={18}/></button></td></tr>)}</tbody></table></div></details>
  <p className="release-note">{L.excluded}</p><p className="release-note">{L.no_schedule}</p>
  {selected&&<Drawer title={selected.provider_label+' → '+selected.consumer_label} wide onClose={()=>setSelected(null)}><div className="release-detail"><section><h3>{L[selected.gate]+' · '+n(selected.threshold_pct,0)+' '+L.percent}</h3><p>{selected.prerequisite}</p></section><section><h3>{L.work}</h3><p>{selected.work_scope}</p></section><section><h3>{L.basis}</h3><p>{selected.justification}</p><p>{L.progress}</p></section><section><h3>{L.evidence}</h3>{selected.evidence_refs.map((p:string)=><SourceLink key={p} path={p}>{p.split('/').pop()}</SourceLink>)}</section></div></Drawer>}
 </div>;
}
