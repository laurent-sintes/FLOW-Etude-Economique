export const economicPages=['comparer','evaluation-core','parametres'] as const;
export type EconomicPage=typeof economicPages[number];
export type EconomicRoute={page:EconomicPage;option?:string;horizon?:string;origin?:string;options?:string;view?:string;focus?:string;family?:string;zone?:string;detail?:'tarifs'|'diagnostics'};
export const readingOptions=['java-spring','microsoft','sap'];
const options=readingOptions;
const horizons=Array.from({length:15},(_,i)=>String(i+1));
export const readingOrigins=['project','core','production'] as const;
export function readingOrigin(route:{origin?:string}){return readingOrigins.includes(route.origin as typeof readingOrigins[number])?route.origin!:'project';}
export function shownOptions(route:{options?:string}){
 const chosen=(route.options||'').split(',');
 const selected=readingOptions.filter(option=>chosen.includes(option));
 return selected.length?selected:[...readingOptions];
}
export function economicReadingContext(route:{horizon?:string;view?:string;origin?:string;options?:string;zone?:string}){
 return {horizon:String(economicPeriod(route)),origin:readingOrigin(route),options:shownOptions(route).join(','),...(route.zone==='province'?{zone:'province'}:{})};
}
/** Old simulation URLs now open the fixed reference. Only reading choices survive. */
export function economicDestination(page:string,params:URLSearchParams):EconomicRoute|{page:'acquisition';option:string}|null{
 const option=options.includes(params.get('option')||'')?params.get('option')!:undefined;
 const view=horizons.includes(params.get('view')||'')?params.get('view')!:undefined;
 const horizon=horizons.includes(params.get('horizon')||'')?params.get('horizon')!:undefined;
 const origin=readingOrigins.includes(params.get('origin') as typeof readingOrigins[number])?params.get('origin')!:undefined;
 const selected=params.has('options')?shownOptions({options:params.get('options')!}).join(','):undefined;
 const zone=params.get('zone')==='province'?'province':undefined;
 const context={...(zone?{zone}:{}),...(origin?{origin}:{}),...(selected?{options:selected}:{}),...(horizon?{horizon}:{}),...(params.get('family')?{family:params.get('family')!}:{}),...(params.get('focus')?{focus:params.get('focus')!}:{})};
 if(['comparer','se-projeter','simulation-depenses','simuler','simulations','simulation-hypotheses'].includes(page))return {page:'comparer',option,view,...context};
 if(page==='parametres')return {page:'parametres',option,view,...context,detail:params.get('detail')==='tarifs'?'tarifs':params.get('detail')==='diagnostics'?'diagnostics':undefined};
 if(page==='evaluation-core')return {page:'evaluation-core',option,...context,view:['financements','transpositions'].includes(params.get('view')||'')?params.get('view')!:view,family:params.get('family')||undefined,focus:params.get('focus')||undefined};
 if(page==='etude-marche')return params.get('view')==='construction'?{page:'acquisition',option:'java-spring'}:{page:'evaluation-core',option,...context,view:params.get('view')==='references'?'transpositions':'financements',focus:params.get('focus')||undefined};
 return null;
}
export function economicHash(route:{page:string;option?:string;horizon?:string;origin?:string;options?:string;view?:string;family?:string;focus?:string;detail?:string;zone?:string}){
 if(!economicPages.includes(route.page as EconomicPage))return null;
 const query=new URLSearchParams();
 for(const key of ['option','horizon','origin','options','view','family','focus','detail','zone'] as const)if(route[key])query.set(key,route[key]!);
 return '#'+route.page+(query.size?'?'+query.toString():'');
}

/** A detail never changes the reading horizon of its parent. */
export function economicPeriod(route:{horizon?:string;view?:string}){
 const value=route.horizon||route.view;
 return horizons.includes(value||'')?Number(value):10;
}

/** Reading links keep the phase context across summaries, evidence and costs. */
export function phaseReadingHash(route:{page:string;option?:string;horizon?:string;origin?:string;options?:string;focus?:string;returnTo?:string;family?:string;zone?:string}){
 if(!['acquisition','integration','fonctionnement','scenarios','methodes','organisation-delivery','equipes-produit','integration-transverse'].includes(route.page)&&!['charges-acquisition','charges-integration','charges-fonctionnement'].includes(route.page))return null;
 const query=new URLSearchParams();
 for(const key of ['option','focus','horizon','origin','options','returnTo','family','zone'] as const)if(route[key]&&(key!=='horizon'||horizons.includes(route[key]!)))query.set(key,route[key]!);
 return '#'+route.page+(query.size?'?'+query.toString():'');
}
export function contextualEconomicLink(href:string,option:string,horizon?:string,context:{origin?:string;options?:string}={}){
 const [page,query='']=href.replace(/^#/,'').split('?');
 if(!href.startsWith('#'))return href;
 const target=economicDestination(page,new URLSearchParams(query));
 return target&&economicPages.includes(target.page as EconomicPage)?economicHash({...target,option,...context,...(horizon&&horizons.includes(horizon)?{horizon}:{})})!:href;
}
