// Content resolver. Names, labels, prose and presentation values come from data.
export function createContentRenderer(presentation,glossary){
 const get=(root,path)=>path.split('.').reduce((obj,key)=>obj?.[key],root);
 const resolve=(raw,params)=>{
  if(raw&&typeof raw==='object'&&raw.ref){const value=get(glossary,raw.ref);if(typeof value!=='string')throw new Error('ERR_GLOSSARY_REF');return value;}
  if(typeof raw!=='string')throw new Error('ERR_CONTENT_TYPE');
  return raw.replace(/\{\{([^}]+)\}\}/g,(_,key)=>{
   if(key in params)return String(params[key]);
   const parts=key.split('.');
   if(parts[0]==='notion'){
    const term=glossary.notions[parts[1]],field=parts[2]==='court'?'forme_courte':'libelle';
    if(!term||!term[field])throw new Error('ERR_GLOSSARY_TERM');return term[field];
   }
   if(parts[0]==='vue'){const view=glossary.vues[parts[1]];if(!view)throw new Error('ERR_GLOSSARY_VIEW');return view.libelle;}
   throw new Error('ERR_CONTENT_PARAM');
  });
 };
 const t=(id,params={})=>{const value=get(presentation,id);if(value===undefined)throw new Error('ERR_CONTENT_REF');return resolve(value,params);};
 t.render=(raw,params={})=>resolve(raw,params);
 return t;
}
