type ArchitectureOrder={layers:{id:string}[];blocks:{cost:string;layers:string[];lane:number}[]};

/** Read top to bottom, then left to right; cross-cutting structures come last. */
export function costsInLayerOrder(costs:string[],architecture:ArchitectureOrder):string[]{
 const ranks=new Map(architecture.layers.map((layer,index)=>[layer.id,index]));
 const blocks=new Map(architecture.blocks.map(block=>[block.cost,block]));
 const position=(cost:string)=>{
  const block=blocks.get(cost);
  if(!block)return [Number.MAX_SAFE_INTEGER,Number.MAX_SAFE_INTEGER];
  const first=block.layers.length===architecture.layers.length?architecture.layers.length:Math.min(...block.layers.map(layer=>ranks.get(layer)??Number.MAX_SAFE_INTEGER));
  return [first,block.lane];
 };
 return [...costs].sort((a,b)=>{const x=position(a),y=position(b);return x[0]-y[0]||x[1]-y[1];});
}
