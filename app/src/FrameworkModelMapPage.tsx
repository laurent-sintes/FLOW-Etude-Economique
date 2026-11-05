import {useCallback,useEffect,useMemo,useState,type CSSProperties} from 'react';
import {Background,Controls,Handle,MiniMap,Position,ReactFlow,applyNodeChanges,type Edge,type Node,type NodeProps,type ReactFlowInstance} from '@xyflow/react';
import {modelLineage} from './modelLineage';
import {useStudy,type Data} from './context';
import {MethodText} from './MethodDocument';
import {phaseReadingHash} from './economicNavigation';
import {useReadingContext} from './ReadingScopeContext';
import '@xyflow/react/dist/style.css';
import './frameworkModelMap.css';

type ModelNode=Node<{record:Data;caption:string;lineage?:boolean},'model'|'domain'>;
function ObjectNode({data}:NodeProps<ModelNode>){
 const r=data.record;
 return <div className={'framework-map-node framework-map-node-'+r.kind+(r.id==='work_unit'?' framework-map-work-unit':'')+(data.lineage?' framework-map-lineage':'')} style={{'--map-node-color':r.color} as CSSProperties}><Handle type="target" position={Position.Left}/><small>{data.caption}</small><strong>{r.label}</strong><Handle type="source" position={Position.Right}/></div>;
}
function DomainNode({data}:NodeProps<ModelNode>){
 const d=data.record;
 return <div className={'framework-map-domain'+(data.lineage?' framework-map-domain-lineage':'')} style={{'--domain-color':d.color} as CSSProperties}><strong>{d.label}</strong><span>{data.caption}</span></div>;
}
const nodeTypes={model:ObjectNode,domain:DomainNode};

export function FrameworkModelMapPage({view,focus,phase}:{view?:string;focus?:string;phase?:string}){
 const {data}=useStudy(),G=data.content.framework_graph,L=G.labels,context=useReadingContext();
 const profile=G.profiles.find((p:Data)=>p.id===view)||G.profiles[0];
 const [query,setQuery]=useState(''),[neighbours,setNeighbours]=useState(false),[nodes,setNodes]=useState<ModelNode[]>([]),[loading,setLoading]=useState(true),[error,setError]=useState(false),[attempt,setAttempt]=useState(0);
 const [flow,setFlow]=useState<ReactFlowInstance<ModelNode>|null>(null);
 const phaseId=G.phases.some((p:Data)=>p.id===phase)?phase:undefined;
 const rawNodes:Data[]=profile.kind==='teams'?G.teams:profile.kind==='rules'?G.rules:G.objects;
 const rawEdges:(Data&{id:string;source:string;target:string})[]=profile.kind==='teams'?G.interactions:profile.kind==='rules'?G.rule_relations:G.relations;
 const selected=rawNodes.find(n=>n.id===focus);
 const navigate=useCallback((values:Data)=>{location.hash=phaseReadingHash({...context,page:'schema-modele',view:profile.id,focus,phase:phaseId,...values})!;},[context,profile.id,focus,phaseId]);
 const graph=useMemo(()=>{
  let chosen=rawNodes.filter(n=>!profile.object_refs.length||profile.object_refs.includes(n.id));
  if(query.trim()){
   const terms=query.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase().split(/\s+/).filter(Boolean);
   chosen=chosen.filter(n=>{const text=[n.label,n.id,n.description,...n.attributes].join(' ').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase();return terms.every(word=>text.includes(word));});
  }
  const eligible=rawEdges.filter(e=>!phaseId||!e.phases||e.phases.includes(phaseId));
  if(neighbours&&focus){const nearby=new Set([focus,...eligible.filter(e=>e.source===focus||e.target===focus).flatMap(e=>[e.source,e.target])]);chosen=chosen.filter(n=>nearby.has(n.id));}
  const ids=new Set(chosen.map(n=>n.id));
  return {nodes:chosen,edges:eligible.filter(e=>ids.has(e.source)&&ids.has(e.target))};
 },[rawNodes,rawEdges,profile,query,neighbours,neighbours?focus:undefined,phaseId]);
 const lineage=useMemo(()=>modelLineage(rawEdges.filter(e=>!phaseId||!e.phases||e.phases.includes(phaseId)),selected?.id),[rawEdges,selected?.id,phaseId]);
 const cardinality=(value:string)=>L['cardinality_'+value]||value;
 const edges:Edge[]=useMemo(()=>graph.edges.map((e:Data)=>({id:e.id,source:e.source,target:e.target,type:'default',
  label:profile.kind==='teams'?e.label:(e.display_label&&e.display_label!==e.cardinality?e.display_label+' · ':'')+cardinality(e.cardinality),ariaLabel:(e.meaning||e.label)+' · '+cardinality(e.cardinality),
  className:lineage.relations.has(e.id)?'framework-map-lineage-edge':undefined,zIndex:0,
  style:{stroke:lineage.relations.has(e.id)?'#236159':e.mode==='facilitating'?'#287247':e.mode==='collaboration'?'#8351A7':'#677985',strokeWidth:lineage.relations.has(e.id)?3.5:1.3,strokeDasharray:e.mode==='facilitating'?'5 4':undefined},
  labelStyle:{fill:'#344954',fontSize:11,fontWeight:lineage.relations.has(e.id)?700:400},labelBgStyle:{fill:'#FFFFFF',fillOpacity:.94},
  markerEnd:{type:'arrowclosed' as const,color:lineage.relations.has(e.id)?'#236159':'#677985'},selectable:false})),[graph.edges,profile.kind,lineage,L]);
 useEffect(()=>{
  let active=true;setLoading(true);setError(false);
  if(!graph.nodes.length){setNodes([]);setLoading(false);return()=>{active=false;};}
  if(profile.kind==='model'){
   const shown:Data[]=G.domains.filter((d:Data)=>graph.nodes.some(n=>n.domain_ref===d.id));
   const width=861,gap=90,header=90,padding=24,columnGap=24,rowGap=24;
   const heights=shown.map(d=>header+Math.ceil(graph.nodes.filter(n=>n.domain_ref===d.id).length/3)*112+Math.max(0,Math.ceil(graph.nodes.filter(n=>n.domain_ref===d.id).length/3)-1)*rowGap+padding);
   const rowHeights=Array.from({length:Math.ceil(shown.length/3)},(_,i)=>Math.max(...heights.slice(i*3,i*3+3)));
   const arranged:ModelNode[]=[];
   shown.forEach((d,index)=>{
    const members=graph.nodes.filter(n=>n.domain_ref===d.id),parentId='domain:'+d.id,row=Math.floor(index/3);
    arranged.push({id:parentId,type:'domain',data:{record:d,caption:members.length+' '+L.nodes_count},position:{x:(index%3)*(width+gap),y:rowHeights.slice(0,row).reduce((sum,h)=>sum+h+gap,0)},style:{width,height:heights[index],zIndex:-1},selectable:false,draggable:false,connectable:false,ariaLabel:d.label});
    members.forEach((r,j)=>arranged.push({id:r.id,type:'model',parentId,extent:'parent',data:{record:r,caption:L.kind_object},position:{x:padding+(j%3)*(255+columnGap),y:header+Math.floor(j/3)*(112+rowGap)},style:{width:255,height:112,zIndex:3},draggable:false,connectable:false,ariaLabel:r.label}));
   });
   setNodes(arranged);setLoading(false);
   return()=>{active=false;};
  }
  import('elkjs/lib/elk.bundled.js').then(async({default:ELK})=>{
   const layout=await new ELK().layout({id:'framework',layoutOptions:{'elk.algorithm':'layered','elk.direction':'RIGHT','elk.spacing.nodeNode':'42','elk.layered.spacing.nodeNodeBetweenLayers':'200','elk.layered.nodePlacement.strategy':'NETWORK_SIMPLEX'},children:graph.nodes.map(n=>({id:n.id,width:255,height:112})),edges:graph.edges.map(e=>({id:e.id,sources:[e.source],targets:[e.target]}))});
   if(active){const positions=new Map(layout.children?.map(n=>[n.id,n]));setNodes(graph.nodes.map(r=>({id:r.id,type:'model',data:{record:r,caption:L['kind_'+r.kind]},position:{x:positions.get(r.id)?.x||0,y:positions.get(r.id)?.y||0},style:{width:255,height:112},draggable:false,connectable:false,ariaLabel:r.label})));setLoading(false);}
  }).catch(()=>{if(active){setError(true);setLoading(false);}});
  return()=>{active=false;};
 },[graph,attempt,L,profile.kind,G.domains]);
 const related=selected?rawEdges.filter(e=>(e.source===selected.id||e.target===selected.id)&&(!phaseId||!e.phases||e.phases.includes(phaseId))):[];
 const name=(id:string)=>rawNodes.find(n=>n.id===id)?.label||id;
 const selectedNodes=useMemo(()=>nodes.map(n=>{
  const active=n.type==='domain'?graph.nodes.some(r=>r.domain_ref===n.data.record.id&&lineage.nodes.has(r.id)):lineage.nodes.has(n.id);
  return {...n,selected:n.type!=='domain'&&n.id===focus,className:n.type!=='domain'&&active?'framework-map-lineage-node':undefined,data:{...n.data,lineage:active}};
 }),[nodes,focus,lineage,graph]);
 const shownDomains:Data[]=profile.kind==='model'?G.domains.filter((d:Data)=>graph.nodes.some(n=>n.domain_ref===d.id)):[];
 return <div className="essential-page framework-model-map">
  <p className="framework-map-intro">{L.intro}</p>
  <nav className="framework-map-profiles" aria-label={L.views}>{G.profiles.map((p:Data)=><a key={p.id} href={phaseReadingHash({...context,page:'schema-modele',view:p.id})!} aria-current={p.id===profile.id?'page':undefined}>{p.label}</a>)}</nav>
  <p>{profile.description}</p>
  {shownDomains.length>0&&<section className="framework-map-domain-key" aria-label={L.domains}><h2>{L.domains}</h2><p>{L.domain_help}</p><div>{shownDomains.map((d:Data)=><button type="button" key={d.id} style={{'--domain-color':d.color} as CSSProperties} onClick={()=>{void flow?.fitView({nodes:[{id:'domain:'+d.id}],padding:.08,maxZoom:1,duration:0});}}><span aria-hidden="true"/><strong>{d.label}</strong><small>{graph.nodes.filter(n=>n.domain_ref===d.id).length}</small></button>)}</div></section>}
  <div className="framework-map-toolbar"><label>{L.search}<input type="search" value={query} onChange={event=>setQuery(event.target.value)} placeholder={L.search_placeholder}/></label><label>{L.select}<select value={selected?.id||''} onChange={event=>navigate({focus:event.target.value||undefined})}><option value="">{L.select_empty}</option>{graph.nodes.map(n=><option key={n.id} value={n.id}>{n.label}</option>)}</select></label>{profile.kind==='teams'&&<label>{L.phase}<select value={phaseId||''} onChange={event=>navigate({phase:event.target.value||undefined})}><option value="">{L.all_phases}</option>{G.phases.map((p:Data)=><option key={p.id} value={p.id}>{p.label}</option>)}</select></label>}<label className="framework-map-neighbours"><input type="checkbox" checked={neighbours} onChange={event=>setNeighbours(event.target.checked)}/>{L.neighbours}</label></div>
  <p className="framework-map-lineage-help">{L.lineage_help}</p><p className="framework-map-help">{L.gestures}<button type="button" className="text-button" disabled={!selected} onClick={()=>{if(selected)void flow?.fitView({nodes:[{id:selected.id}],padding:.45,minZoom:.8,maxZoom:1,duration:0});}}>{L.focus_selection}</button><span>{graph.nodes.length+' '+L.nodes_count+' · '+graph.edges.length+' '+L.edges_count}</span></p>
  <div className="framework-map-workspace"><section className="framework-map-canvas" aria-label={L.canvas}>
   {loading?<p role="status">{L.loading}</p>:error?<div role="alert"><p>{L.layout_error}</p><button onClick={()=>setAttempt(v=>v+1)}>{L.retry}</button></div>:!nodes.length?<p role="status">{L.empty}</p>:<ReactFlow<ModelNode> key={profile.id+'-'+phaseId+'-'+query+'-'+neighbours+'-'+(neighbours?focus:'')} nodes={selectedNodes} edges={edges} onInit={setFlow} nodeTypes={nodeTypes} nodesDraggable={false} nodesConnectable={false} elevateNodesOnSelect={false} elevateEdgesOnSelect={false} edgesReconnectable={false} deleteKeyCode={null} onNodeClick={(_,node)=>{if(node.type==='domain')void flow?.fitView({nodes:[{id:node.id}],padding:.08,maxZoom:1,duration:0});else navigate({focus:node.id});}} onNodesChange={changes=>{for(const change of changes)if(change.type==='select'&&change.selected&&change.id!==focus)navigate({focus:change.id});setNodes(old=>applyNodeChanges(changes,old));}} onPaneClick={()=>navigate({focus:undefined})} fitView fitViewOptions={{padding:.18,maxZoom:1}} minZoom={.025} maxZoom={1.8} zoomOnScroll={false} zoomOnDoubleClick={false} preventScrolling={false} ariaLabelConfig={G.aria}><Background gap={24} size={1} color="#D5DEDA"/><MiniMap pannable zoomable nodeColor={n=>(n.data.record as Data).color}/><Controls showInteractive={false}/></ReactFlow>}
  </section><aside className="framework-map-inspector" aria-label={L.inspector}>
   {!selected?<><h2>{L.inspector}</h2><p>{L.inspect_help}</p></>:<><p className="framework-map-kind">{L['kind_'+selected.kind]}</p><h2>{selected.label}</h2>{selected.domain_ref&&<p className="framework-map-domain-name">{L.domain+' · '+G.domains.find((d:Data)=>d.id===selected.domain_ref).label}</p>}{selected.description&&<p><MethodText>{selected.description}</MethodText></p>}{selected.owner&&<p><strong>{L.owner}</strong><code>{selected.owner}</code></p>}{selected.boundary&&<p>{selected.boundary}</p>}{selected.expression&&<><h3>{L.expression}</h3><code className="framework-map-expression">{selected.expression}</code><p>{selected.unit}</p></>}{selected.attributes.length>0&&<><h3>{L.attributes}</h3><ul>{selected.attributes.map((attribute:string)=><li key={attribute}><code>{attribute}</code>{selected.variables?.[attribute]&&<p>{selected.variables[attribute]}</p>}</li>)}</ul></>}{selected.responsibilities&&<><h3>{L.lifecycle}</h3>{G.phases.map((p:Data)=><section key={p.id}><h4>{p.label}</h4><p>{selected.responsibilities[p.id]}</p></section>)}</>}{selected.href&&<a className="text-button" href={selected.href}>{L.read_team}</a>}<h3>{L.relationships}</h3>{related.length?<ul className="framework-map-relations">{related.map((r:Data)=>{const other=r.source===selected.id?r.target:r.source;return <li key={r.id}><button className="text-button" onClick={()=>navigate({focus:other})}>{name(other)}</button><p>{r.meaning||r.label}</p>{r.cardinality&&<small>{L.direction+' · '+name(r.source)+' → '+name(r.target)}<br/>{L.cardinality+' · '+cardinality(r.cardinality)}</small>}{r.exit_criterion&&<p>{r.exit_criterion}</p>}</li>;})}</ul>:<p>{L.no_relationships}</p>}</>}
  </aside></div>
  <section className="framework-map-list"><h2>{L.list_title}</h2><p>{L.list_note}</p><div role="region" aria-label={L.relationships} tabIndex={0}><table><thead><tr>{[L.source,L.relation,L.target].map((text:string)=><th scope="col" key={text}>{text}</th>)}</tr></thead><tbody>{graph.edges.map((e:Data)=><tr key={e.id}><th scope="row"><button className="text-button" onClick={()=>navigate({focus:e.source})}>{name(e.source)}</button></th><td>{e.meaning||e.label}{e.cardinality&&<small>{cardinality(e.cardinality)}</small>}</td><td><button className="text-button" onClick={()=>navigate({focus:e.target})}>{name(e.target)}</button></td></tr>)}</tbody></table></div></section>
  <p className="framework-map-source">{L.authority}</p>
 </div>;
}
