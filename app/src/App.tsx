import {FinancialZone} from './FinancialZone';
import {useEffect,useRef,useState} from 'react';
import {Menu,X} from 'lucide-react';
import {studyIcons as icons} from './StudyIcons';
import {StudyContext,request,type Bootstrap,type Data} from './context';
import type {ReaderSession} from './reloadSession';
import {DocumentViewer} from './components';
import {EvidenceProvider,ModelPage,ProofDialog,type Proof} from './EssentialViews';
import {CoreMethodPage,NetCalculationPage,RunCalculationPage} from './CoreMethodPage';
import {MarketMethodPage} from './MarketMethodPage';
import {PreStudyPage} from './PreStudyPage';
import {MarketCostsPage} from './MarketCostsPage';
import {PreStudyOverview,ProductivityPage} from './PreStudyOverview';
import {preStudyDestination} from './preStudyNavigation';
import {economicDestination,economicHash,economicPeriod,economicReadingContext,phaseReadingHash,type EconomicRoute} from './economicNavigation';
import {EconomicComparisonPage,EconomicCostsPage,EconomicAssumptionsPage} from './EconomicDossier';
import {LeversPage} from './LeversPage';
import {FrameworkVisionPage} from './FrameworkVisionPage';
import {FrameworkJourneyPage} from './FrameworkJourneyPage';
import {DeliveryOrganisationPage} from './DeliveryOrganisationPage';
import {GrossEvaluationsPage} from './GrossEvaluationsPage';
import {SynvanceReferencePage} from './SynvanceReferencePage';
import {DeliveryConditionsPage,DeliveryReadinessPage} from './DeliveryReadinessPage';
import {useServerUpdate} from './useServerUpdate';
import {hydrateBootstrap} from './modelTransport';
import {PageHeading} from './ReadingIdentity';
import {GlossaryPage} from './GlossaryPage';
import {CartographyPage} from './CartographyPage';
import {DownloadsPage} from './DownloadsPage';
import {ReadingScopeContext} from './ReadingScopeContext';
import {modelRevisionLabel} from './modelRevision';

type Route={zone?:string;page:'preetudes'|'preetude-productivite'|'charges-acquisition'|'charges-integration'|'charges-fonctionnement'|'organisation-delivery'|'equipes-produit'|'integration-transverse'|'preetude-couts'|'preetude-projets'|'preetude-solutions'|'acquisition'|'integration'|'fonctionnement'|'scenarios'|'methodes'|'telechargements'|'cartographie'|'glossaire'|'conditions-realisation'|'capacite-realisation'|'synvance-business'|'synvance-oms'|'synvance-costs'|'synvance-delays'|'synvance-microsoft'|'synvance-sap'|'synvance'|'vision'|'comparer'|'se-projeter'|'simuler'|'modele'|'complexite'|'marche'|'parametres'|'evaluation-core'|'calcul-net'|'calcul-run'|'leviers'|'etude-marche';option?:string;proof?:string;term?:string;section?:'scope';family?:string;horizon?:string;origin?:string;options?:string;returnTo?:string;view?:string;focus?:string;detail?:'tarifs'|'diagnostics'};
function essentialRoute(hash:string):Route{
 let [raw,query='']=hash.replace(/^#/,'').split('?'),params=new URLSearchParams(query);
 const moved=preStudyDestination(raw,params);
 if(moved)return moved;
 const economic=economicDestination(raw,params);
 if(economic)return economic;
 if(raw==='preetude-couts'||raw==='preetude-projets'||raw==='preetude-solutions')return {page:raw,view:params.get('view')||undefined,focus:params.get('focus')||undefined};
 if(raw==='organisation-delivery'&&params.get('view')==='equipes')raw='equipes-produit';
 if(raw==='organisation-delivery'&&params.get('view')==='integration')raw='integration-transverse';
 if(raw==='organisation-delivery'||raw==='equipes-produit'||raw==='integration-transverse'||raw==='charges-acquisition'||raw==='charges-integration'||raw==='charges-fonctionnement'||raw==='acquisition'||raw==='integration'||raw==='fonctionnement'||raw==='scenarios'||raw==='methodes')return {page:raw,zone:params.get('zone')==='province'?'province':undefined,option:['java-spring','microsoft','sap'].includes(params.get('option')||'')?params.get('option')!:undefined,focus:raw.startsWith('charges-')||raw==='equipes-produit'?params.get('focus')||undefined:['summary','method'].includes(params.get('focus')||'')?params.get('focus')!:undefined,horizon:/^(?:[1-9]|1[0-5])$/.test(params.get('horizon')||'')?params.get('horizon')!:undefined,origin:params.get('origin')||undefined,options:params.get('options')||undefined,returnTo:['evaluation-core','parametres'].includes(params.get('returnTo')||'')?params.get('returnTo')!:undefined,family:params.get('family')||undefined};
 if(raw==='glossaire'||(raw==='sources'&&params.get('tab')==='glossary'))return {page:'glossaire',term:params.get('term')||undefined};
 if(raw==='preetudes'||raw==='preetude-productivite')return {page:raw};
 if(raw==='telechargements')return {page:'telechargements'};
 if(raw==='evaluation-core')return {page:'evaluation-core',family:params.get('family')||undefined};
 if(raw==='parametres')return {page:'parametres',detail:params.get('detail')==='tarifs'?'tarifs':params.get('detail')==='diagnostics'?'diagnostics':undefined};
 if(raw==='cartographie'||raw==='perimetre-retenu')return {page:'cartographie'};
 if(raw==='modele'||raw==='etude-marche'||raw==='capacite-realisation')return {page:raw,view:params.get('view')||undefined,focus:params.get('focus')||undefined,section:raw==='modele'&&params.get('section')==='scope'?'scope':undefined};
 if(raw==='conditions-realisation'||raw==='capacite-realisation'||raw==='synvance-business'||raw==='synvance-oms'||raw==='synvance-costs'||raw==='synvance-delays'||raw==='synvance-microsoft'||raw==='synvance-sap'||raw==='synvance'||raw==='vision'||raw==='comparer'||raw==='se-projeter'||raw==='simuler'||raw==='modele'||raw==='complexite'||raw==='marche'||raw==='parametres'||raw==='evaluation-core'||raw==='calcul-net'||raw==='calcul-run'||raw==='leviers'||raw==='etude-marche')return {page:raw};
 if(raw==='simulation-depenses')return {page:'se-projeter'};
 if(['simulation-hypotheses','simulations'].includes(raw))return {page:'simuler'};
 if(['logique','faq','perimetres'].includes(raw))return {page:'modele',proof:raw==='perimetres'?(params.get('capability')?'capability:'+params.get('capability'):'scope'):undefined};
 if(raw==='sources')return {page:params.get('tab')==='market'?'comparer':'modele',proof:'scope'};
 if(['build','exploitation','estimations','market'].includes(raw))return {page:'comparer',proof:raw==='build'?'build':raw==='market'?'market':'integration'};
 return {page:'vision'};
}
const navigationPage=(page:Route['page'])=>page.startsWith('synvance-')?'synvance':['modele','conditions-realisation','capacite-realisation','marche','complexite','calcul-net','calcul-run','leviers'].includes(page)?'methodes':page;
export default function App({initial}:{initial:Data}){
 const [data,setData]=useState<Bootstrap|null>(null),[error,setError]=useState(false),[doc,setDoc]=useState<string|null>(null),[menu,setMenu]=useState(false);
 const [frameworkOption,setFrameworkOption]=useState('java-spring');
 const [route,setRoute]=useState<Route>(()=>essentialRoute(location.hash));
 useEffect(()=>{if(['java-spring','microsoft','sap'].includes(route.option||''))setFrameworkOption(route.option!);},[route.option]);
 const [legacyProof,setLegacyProof]=useState<string|null>(null),[proof,setProof]=useState<Proof|null>(null);
 const serverStatus=useServerUpdate(initial.server_revision||data?.server_revision,data?.ui.id);
 const [session,setSession]=useState<ReaderSession>({draft:{common:{},options:{}},horizon:0,chosen:'',name:''});
 const navigationRef=useRef<HTMLElement>(null),menuTriggerRef=useRef<HTMLButtonElement>(null),menuCloseRef=useRef<HTMLButtonElement>(null),mainRef=useRef<HTMLElement>(null);
 const previousPage=useRef<string>(route.page),hiddenViewportFocus=useRef<HTMLElement|null>(null);
 const hiddenByViewport=(element:HTMLElement,mobile:boolean)=>mobile
  ?Boolean(navigationRef.current?.contains(element)&&getComputedStyle(element).visibility==='hidden')
  :(element===menuTriggerRef.current||element===menuCloseRef.current)&&element.getClientRects().length===0;
 const focusPage=()=>{
  const directed=route.page==='evaluation-core'&&!['financements','transpositions'].includes(route.view||'');
  const targetId=directed?(route.family?'economic-lot-'+route.family:route.focus==='economic-expert'?'economic-expert':undefined):undefined;
  const target=targetId?document.getElementById(targetId):null;
  const heading=target||mainRef.current?.querySelector<HTMLElement>('h1');
  if(heading){if(heading.tagName!=='SUMMARY')heading.tabIndex=-1;heading.focus({preventScroll:true});if(target)target.scrollIntoView({block:'start',behavior:'auto'});}
 };
 const closeMenu=()=>{setMenu(false);menuTriggerRef.current?.focus({preventScroll:true});};
 const navigate=(destination:string)=>{
  setMenu(false);
  if(destination===route.page){window.scrollTo(0,0);focusPage();}
 };
 useEffect(()=>{
  if(route.section==='scope'&&data){
   previousPage.current=route.page;setMenu(false);
   const heading=document.getElementById('model-chapter-scope');
   heading?.focus({preventScroll:true});heading?.scrollIntoView({block:'start',behavior:'auto'});
   return;
  }
  const destination=route.page+(route.view||route.detail||route.option||'');
  if(previousPage.current===destination)return;
  previousPage.current=destination;setMenu(false);focusPage();
 },[route.page,route.section,route.view,route.detail,route.option,Boolean(data)]);
 useEffect(()=>{
  const mobile=window.matchMedia('(max-width:900px)');
  const resize=()=>{
   const current=document.activeElement,cached=hiddenViewportFocus.current;
   const focused=current===document.body&&cached?.isConnected&&hiddenByViewport(cached,mobile.matches)?cached:current;
   hiddenViewportFocus.current=null;setMenu(false);
   if(mobile.matches&&navigationRef.current?.contains(focused))menuTriggerRef.current?.focus({preventScroll:true});
   else if(!mobile.matches&&(focused===menuTriggerRef.current||focused===menuCloseRef.current))navigationRef.current?.querySelector<HTMLElement>('a[aria-current="page"]')?.focus({preventScroll:true});
  };
  mobile.addEventListener('change',resize);
  return()=>mobile.removeEventListener('change',resize);
 },[]);
 useEffect(()=>{
  if(!menu)return;
  const panel=navigationRef.current;
  panel?.scrollTo({top:0});menuCloseRef.current?.focus({preventScroll:true});
  const dismiss=(event:KeyboardEvent)=>{if(event.key==='Escape'){event.preventDefault();closeMenu();}};
  const outside=(event:PointerEvent)=>{if(event.target instanceof Node&&!panel?.contains(event.target)&&!menuTriggerRef.current?.contains(event.target))closeMenu();};
  window.addEventListener('keydown',dismiss);document.addEventListener('pointerdown',outside);
  return()=>{window.removeEventListener('keydown',dismiss);document.removeEventListener('pointerdown',outside);};
 },[menu]);
 const load=()=>{
  setError(false);
  request<Bootstrap>('/api/bootstrap?view=essential').then(hydrateBootstrap).then(next=>{
   // Fixed reference reading leaves all personal storage untouched, including legacy sessions.
   setSession({draft:next.baseline.parameters,horizon:10,chosen:next.baseline.options[0].stack,name:''});
   setData(next);
  }).catch(()=>setError(true));
 };
 useEffect(load,[]);
 useEffect(()=>{if(data)document.title=data.ui.document_title;},[data]);
 useEffect(()=>{let lastHash:string|undefined;const sync=()=>{if(location.hash===lastHash)return;const next=essentialRoute(location.hash);const canonical=(phaseReadingHash(next)||economicHash(next))||'#'+next.page+(next.page==='glossaire'&&next.term?'?term='+encodeURIComponent(next.term):next.section==='scope'?'?section=scope':next.family?'?family='+encodeURIComponent(next.family):next.detail?'?detail='+next.detail:next.option?'?option='+encodeURIComponent(next.option)+(next.page.startsWith('charges-')&&next.focus?'&focus='+encodeURIComponent(next.focus):''):(next.view?'?view='+encodeURIComponent(next.view):'')+(next.focus?(next.view?'&':'?')+'focus='+encodeURIComponent(next.focus):''));if(location.hash!==canonical)history.replaceState(null,'',canonical);lastHash=location.hash;setRoute(current=>{if(current.page!==next.page)window.scrollTo(0,0);return next;});setLegacyProof(next.proof||null);};sync();window.addEventListener('hashchange',sync);window.addEventListener('popstate',sync);return()=>{window.removeEventListener('hashchange',sync);window.removeEventListener('popstate',sync);};},[]);
 useEffect(()=>{
  if(!data||!legacyProof)return;
  let live=true;
  if(legacyProof.startsWith('capability:')){
   request<Proof>('/api/capability?id='+encodeURIComponent(legacyProof.slice('capability:'.length))+'&model_version='+encodeURIComponent(data.model_version)).then(value=>{if(live){setProof(value);setLegacyProof(null);}}).catch(()=>{if(live){setProof(data.ui.essential.proofs.scope);setLegacyProof(null);}});
  }else{setProof(data.ui.essential.proofs[legacyProof]||data.ui.essential.proofs.scope);setLegacyProof(null);}
  return()=>{live=false;};
 },[data,legacyProof]);
 if(!data)return <div className="boot" aria-busy={!error}><div className="boot-mark"/>{error?<><p role="alert">{initial.errors?.network}</p><button onClick={load}>{initial.labels?.retry}</button></>:<p>{initial.labels?.loading}</p>}</div>;
 const {ui}=data,active=ui.essential.nav.find((n:Data)=>n.id===navigationPage(route.page)),child=active.children?.find((item:Data)=>item.id===(route.view==='qualification'?'comparison':route.view||active.default_view)),originalPage=ui.essential.pages[route.page],capability=route.page==='preetude-solutions'&&route.view==='qualification'?data.content.complexity.rows.find((row:Data)=>row.capacite_id===route.focus?.split('~')[0]):null,detailTitle=capability?(capability.name||capability.capacite?.nom)+' · '+(ui.essential.dossiers.product_labels[route.focus?.split('~')[1]||'']||''):undefined,page=child?{...originalPage,title:detailTitle||child.label,intro:undefined}:originalPage,HeadingIcon=icons[active.icon];
 return <StudyContext.Provider value={{data,openDoc:setDoc,session,setSession}}><ReadingScopeContext.Provider value={route}><EvidenceProvider open={setProof}><div className="app-shell essential-shell" onFocusCapture={()=>{hiddenViewportFocus.current=null;}} onBlurCapture={event=>{if(!event.relatedTarget&&event.target instanceof HTMLElement&&hiddenByViewport(event.target,window.matchMedia('(max-width:900px)').matches))hiddenViewportFocus.current=event.target;}}><aside ref={navigationRef} id="study-navigation" className={'sidebar '+(menu?'is-open':'')} onBlur={event=>{if(menu&&!event.currentTarget.contains(event.relatedTarget))setMenu(false);}}><div className="brand"><a className="brand-home" href="#vision" aria-label={ui.essential.home} onClick={()=>navigate('vision')}><div className="brand-symbol"><img className="flow-source-mark" src={ui.brand_assets.flow} alt={ui.brand_assets.flow_alt}/></div><small>{ui.brand_subtitle}</small></a><button ref={menuCloseRef} className="mobile icon-button" onClick={closeMenu} aria-label={ui.labels.close}><X/></button></div><nav>{<SidebarNav ui={ui} route={route} option={route.option||frameworkOption} close={navigate}/>}</nav><div className="sidebar-foot"><img className="beaumanoir-source-logo" src={ui.brand_assets.beaumanoir} alt={ui.brand_assets.beaumanoir_alt}/><small>{ui.labels.model_version}<br/><code>{modelRevisionLabel(data.model_revision,ui.locale,ui.labels.model_order)||ui.labels.model_revision_unknown}</code></small></div></aside><div className="workspace"><header className="topbar"><button ref={menuTriggerRef} className="mobile icon-button" aria-label={ui.labels.navigation} aria-expanded={menu} aria-controls="study-navigation" onClick={()=>setMenu(open=>!open)}><Menu/></button><span><b>{child?.label||active.label}</b></span><span className="reference-pill" title={ui.labels.model_version}>{modelRevisionLabel(data.model_revision,ui.locale,ui.labels.model_order)||ui.labels.model_revision_unknown}</span></header><main ref={mainRef}>{serverStatus.unreachable?<aside className="server-update server-unreachable" role="alert"><div><strong>{ui.server_update.unreachable_message}</strong><p>{ui.server_update.unreachable_note}</p></div><button className="secondary" onClick={serverStatus.recheck} disabled={serverStatus.checking} aria-busy={serverStatus.checking}>{serverStatus.checking?ui.server_update.checking:ui.server_update.retry}</button></aside>:serverStatus.available&&<aside className="server-update" role="status"><div><strong>{ui.server_update.message}</strong><p>{ui.server_update.note}</p></div><button className="primary" onClick={()=>window.location.reload()}>{ui.server_update.action}</button></aside>}{ui.essential.nav_groups[0].items.includes(route.page)&&route.page!=='preetudes'&&<nav className="study-location" aria-label={ui.essential.prestudies.location}><a href="#preetudes">{ui.essential.pages.preetudes.title}</a><span aria-hidden="true">›</span>{child?<><a href={'#'+active.id}>{active.label}</a><span aria-hidden="true">›</span><span aria-current="page">{child.label}</span></>:<span aria-current="page">{active.label}</span>}</nav>}<PageHeading key={route.page+(route.view||'')} active={active} page={page} icon={<HeadingIcon/>}/>{['modele','conditions-realisation','marche','complexite','calcul-net','calcul-run','leviers'].includes(route.page)&&<a className="text-button journey-method-back" href="#methodes">{'← '+ui.essential.pages.methodes.title}</a>}{route.page==='comparer'&&<EconomicComparisonPage route={route as EconomicRoute}/>}{(route.page==='synvance'||route.page.startsWith('synvance-'))&&<SynvanceReferencePage view={route.page==='synvance-business'?'business':route.page==='synvance-oms'?'oms':route.page==='synvance-costs'?'costs':route.page==='synvance-delays'?'delays':'overview'} providerId={route.page==='synvance-microsoft'?'microsoft':route.page==='synvance-sap'?'sap':undefined}/>}{route.page==='preetudes'&&<PreStudyOverview/>}{route.page==='preetude-productivite'&&<ProductivityPage/>}{route.page==='telechargements'&&<DownloadsPage/>}{route.page==='vision'&&<FrameworkVisionPage/>}{route.page.startsWith('charges-')&&<FinancialZone route={{page:'evaluation-core',...economicReadingContext(route)}}><GrossEvaluationsPage horizon={route.horizon} phase={route.page.replace('charges-','')} returnTo={route.returnTo?economicHash({page:route.returnTo,option:route.option,...economicReadingContext(route),family:route.family})||undefined:undefined} focus={route.focus} option={route.option||frameworkOption} onChoose={setFrameworkOption}/></FinancialZone>}{['acquisition','integration','fonctionnement','scenarios','methodes'].includes(route.page)&&<FrameworkJourneyPage focus={route.focus} horizon={route.horizon} page={route.page} option={route.option||frameworkOption} onChoose={setFrameworkOption}/>}
{(route.page==='organisation-delivery'||route.page==='equipes-produit'||route.page==='integration-transverse')&&<DeliveryOrganisationPage page={route.page} option={route.option||frameworkOption} focus={route.focus}/>}{route.page==='glossaire'&&<GlossaryPage key={route.term||'all'} term={route.term}/>}{route.page==='conditions-realisation'&&<DeliveryConditionsPage/>}{route.page==='capacite-realisation'&&<DeliveryReadinessPage view={route.view} focus={route.focus}/>}{route.page==='cartographie'&&<CartographyPage/>}{route.page==='modele'&&<ModelPage view={route.section==='scope'?'scope':route.view}/>}{route.page==='complexite'&&<CoreMethodPage/>}{route.page==='calcul-net'&&<NetCalculationPage/>}{route.page==='calcul-run'&&<RunCalculationPage/>}{route.page==='marche'&&<MarketMethodPage/>}{route.page==='preetude-couts'&&<MarketCostsPage view={route.view} focus={route.focus}/>}
{(route.page==='preetude-projets'||route.page==='preetude-solutions')&&<PreStudyPage kind={route.page==='preetude-projets'?'projects':'solutions'} view={route.view} focus={route.focus}/>}{route.page==='leviers'&&<LeversPage/>}{route.page==='parametres'&&<EconomicAssumptionsPage route={route as EconomicRoute}/>}{route.page==='evaluation-core'&&<EconomicCostsPage route={route as EconomicRoute}/>}</main></div></div>{proof&&<ProofDialog proof={proof} onClose={()=>setProof(null)}/ >}{doc&&<DocumentViewer key={doc} path={doc} onClose={()=>setDoc(null)}/>}</EvidenceProvider></ReadingScopeContext.Provider></StudyContext.Provider>;
}
function Chevron(){return <span className="nav-current"/>;}
function SidebarNav({ui,route,option,close}:{ui:Data;route:Route;option:string;close:(destination:string)=>void}){
 const byId=new Map<string,Data>(ui.essential.nav.map((item:Data)=>[item.id,item]));
 return <>{ui.essential.nav_groups.filter((group:Data)=>!group.hidden).map((group:Data)=><div className="essential-nav-group" role="group" aria-label={group.label} key={group.label}><p className="nav-group-title">{group.label}</p>{group.items.map((id:string)=>{const item=byId.get(id)!,Icon=icons[item.icon],selected=navigationPage(route.page)===id;return <a key={id} href={economicHash({page:id,option:route.option,...economicReadingContext(route)})||phaseReadingHash({page:id,option,...economicReadingContext(route)})||'#'+id} aria-current={selected?'page':undefined} onClick={()=>close(id)}><Icon size={19}/><span>{item.label}</span>{selected&&<Chevron/>}</a>;})}</div>)}</>;
}
