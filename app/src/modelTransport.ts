import type {Bootstrap} from './context';

/** Resolve canonical node IDs once; all views then share the same objects. */
export function hydrateBootstrap(data:Bootstrap):Bootstrap{
 const content=data.content;
 if(!content.transport_format)return data;
 if(content.transport_format!==1)throw Error('ERR_CONTENT_FORMAT');
 const map=content.business_map,nodes=map.nodes;
 const node=(id:string)=>{if(!nodes[id])throw Error('ERR_NODE');return nodes[id];};
 for(const row of map.rows){
  row.capacite=node(row.capacite);
  row.hierarchie=row.hierarchie.map(node);
  row.variantes=row.variantes.map(node);
 }
 content.complexity.rows=map.rows;
 delete map.nodes;delete content.transport_format;
 return data;
}
