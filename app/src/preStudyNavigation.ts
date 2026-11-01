/** Preserve the business context of links into the former mixed market dossier. */
export function preStudyDestination(page:string,params:URLSearchParams){
 if(['dotnet','rust'].includes(params.get('option')||params.get('stack')||''))return {page:'preetudes' as const};
 if(page==='preetude-solutions'&&params.get('view')==='productivity')return {page:'preetude-productivite' as const};
 if(page!=='etude-marche')return null;
 const view=params.get('view'),focus=params.get('focus')||undefined;
 if(view==='qualification'||view==='products'||view==='offers'||focus?.includes('~')){
  if(view==='offers')return {page:'synvance' as const};
  return {page:'preetude-solutions' as const,view:view==='products'?'products':view==='qualification'?'qualification':'comparison',focus};
 }
 return null;
}
