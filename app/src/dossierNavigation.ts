export type DossierEntry={id:string;label:string;short_label?:string;description?:string;sections?:string[];href?:string};

export function dossierHref(base:string,id:string,defaultId:string,parameter='view',focus?:string){
 const query=new URLSearchParams();
 if(id!==defaultId)query.set(parameter,id);
 if(focus)query.set('focus',focus);
 return '#'+base+(query.size?'?'+query:'');
}
export function navigationPages(base:string,pages:DossierEntry[],parameter='view'){
 return pages.map(page=>({...page,href:dossierHref(base,page.id,pages[0].id,parameter)}));
}
export function selectDossierPage(pages:DossierEntry[],view?:string){return pages.find(page=>page.id===view)||pages[0];}
export function dossierTargetPage(pages:DossierEntry[],section:string){return pages.find(page=>page.sections?.includes(section))||pages[0];}
