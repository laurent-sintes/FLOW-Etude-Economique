/** Directed ancestry and descendants. Do not cross from an ancestor to a sibling. */
export function modelLineage(edges:readonly {id:string;source:string;target:string}[],focus?:string){
 const nodes=new Set<string>(),relations=new Set<string>();
 if(!focus)return {nodes,relations};
 nodes.add(focus);
 const walk=(backwards:boolean)=>{
  const index=new Map<string,typeof edges[number][]>();
  for(const edge of edges){const key=backwards?edge.target:edge.source;const list=index.get(key)||[];list.push(edge);index.set(key,list);}
  const seen=new Set([focus]),queue=[focus];
  for(let i=0;i<queue.length;i++)for(const edge of index.get(queue[i])||[]){
   const next=backwards?edge.source:edge.target;
   relations.add(edge.id);nodes.add(next);
   if(!seen.has(next)){seen.add(next);queue.push(next);}
  }
 };
 walk(true);walk(false);
 return {nodes,relations};
}
