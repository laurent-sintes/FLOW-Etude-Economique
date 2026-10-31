import {useEffect,useRef,useState} from 'react';
import {Compass,Calculator,ChartNoAxesCombined,ListTree,Server,Menu,X,Files,BookOpen} from 'lucide-react';
import {StudyContext,request,type Bootstrap,type Data,type Projection} from './context';
import {encodeSession,restoreSession,type ReaderSession} from './reloadSession';
import {DocumentViewer} from './components';
import {Simulations} from './Simulations';
import {ComparePage,EvidenceProvider,ModelPage,ProjectionPage,ProofDialog,type Proof} from './EssentialViews';
import {CoreMethodPage,NetCalculationPage,RunCalculationPage} from './CoreMethodPage';
import {EconomicEvaluationsPage} from './EconomicEvaluationsPage';
import {FrameworkPage} from './FrameworkPage';
import {MarketMethodPage} from './MarketMethodPage';
import {MarketStudyPage} from './MarketStudyPage';
import {LeversPage} from './LeversPage';
import {FrameworkVisionPage} from './FrameworkVisionPage';
import {SynvanceReferencePage} from './SynvanceReferencePage';
import {DeliveryConditionsPage,DeliveryReadinessPage} from './DeliveryReadinessPage';
import {useServerUpdate} from './useServerUpdate';
import {hydrateBootstrap} from './modelTransport';
import {PageHeading} from './ReadingIdentity';
import {GlossaryPage} from './GlossaryPage';
import {MethodText} from './MethodDocument';
import {CartographyPage} from './CartographyPage';

const icons:Record<string,typeof Compass>={compass:Compass,calculator:Calculator,chart:ChartNoAxesCombined,grid:ListTree,server:Server,files:Files,book:BookOpen};
type Route={page:'cartographie'|'glossaire'|'conditions-realisation'|'capacite-realisation'|'synvance-business'|'synvance-oms'|'synvance-costs'|'synvance-microsoft'|'synvance-sap'|'synvance'|'vision'|'comparer'|'se-projeter'|'simuler'|'modele'|'complexite'|'marche'|'parametres'|'evaluation-core'|'calcul-net'|'calcul-run'|'leviers'|'etude-marche';proof?:string;term?:string;section?:'scope';family?:string;view?:string;focus?:string;detail?:'tarifs'|'diagnostics'};
function essentialRoute(hash:string):Route{
 const [raw,query='']=hash.replace(/^#/,'').split('?'),params=new URLSearchParams(query);
 if(raw==='glossaire'||(raw==='sources'&&params.get('tab')==='glossary'))return {page:'glossaire',term:params.get('term')||undefined};
 if(raw==='evaluation-core')return {page:'evaluation-core',family:params.get('family')||undefined};
 if(raw==='parametres')return {page:'parametres',detail:params.get('detail')==='tarifs'?'tarifs':params.get('detail')==='diagnostics'?'diagnostics':undefined};
 if(raw==='cartographie'||raw==='perimetre-retenu')return {page:'cartographie'};
 if(raw==='modele'||raw==='etude-marche'||raw==='capacite-realisation')return {page:raw,view:params.get('view')||undefined,focus:params.get('focus')||undefined,section:raw==='modele'&&params.get('section')==='scope'?'scope':undefined};
 if(raw==='conditions-realisation'||raw==='capacite-realisation'||raw==='synvance-business'||raw==='synvance-oms'||raw==='synvance-costs'||raw==='synvance-microsoft'||raw==='synvance-sap'||raw==='synvance'||raw==='vision'||raw==='comparer'||raw==='se-projeter'||raw==='simuler'||raw==='modele'||raw==='complexite'||raw==='marche'||raw==='parametres'||raw==='evaluation-core'||raw==='calcul-net'||raw==='calcul-run'||raw==='leviers'||raw==='etude-marche')return {page:raw};
 if(raw==='simulation-depenses')return {page:'se-projeter'};
 if(['simulation-hypotheses','simulations'].includes(raw))return {page:'simuler'};
 if(['logique','faq','perimetres'].includes(raw))return {page:'modele',proof:raw==='perimetres'?(params.get('capability')?'capability:'+params.get('capability'):'scope'):undefined};
 if(raw==='sources')return {page:params.get('tab')==='market'?'comparer':'modele',proof:'scope'};
 if(['build','exploitation','estimations','market'].includes(raw))return {page:'comparer',proof:raw==='build'?'build':raw==='market'?'market':'integration'};
 return {page:'vision'};
}
const navigationPage=(page:Route['page'])=>page.startsWith('synvance-')?'synvance':page;
export default function App({initial}:{initial:Data}){
 const [data,setData]=useState<Bootstrap|null>(null),[error,setError]=useState(false),[doc,setDoc]=useState<string|null>(null),[menu,setMenu]=useState(false);
 const [route,setRoute]=useState<Route>(()=>essentialRoute(location.hash));
 const [legacyProof,setLegacyProof]=useState<string|null>(null),[proof,setProof]=useState<Proof|null>(null);
 const serverStatus=useServerUpdate(initial.server_revision||data?.server_revision,data?.ui.id);
 const [session,setSession]=useState<ReaderSession>({draft:{common:{},options:{}},horizon:0,chosen:'',name:''});
 const [recovery,setRecovery]=useState<string|null>(null),[storageError,setStorageError]=useState(false);
 const navigationRef=useRef<HTMLElement>(null),menuTriggerRef=useRef<HTMLButtonElement>(null),menuCloseRef=useRef<HTMLButtonElement>(null),mainRef=useRef<HTMLElement>(null);
 const previousPage=useRef<string>(route.page),hiddenViewportFocus=useRef<HTMLElement|null>(null);
 const hiddenByViewport=(element:HTMLElement,mobile:boolean)=>mobile
  ?Boolean(navigationRef.current?.contains(element)&&getComputedStyle(element).visibility==='hidden')
  :(element===menuTriggerRef.current||element===menuCloseRef.current)&&element.getClientRects().length===0;
 const focusPage=()=>{
  const heading=mainRef.current?.querySelector<HTMLElement>('h1');
  if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true});}
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
  const destination=route.page+(route.view||route.detail||'');
  if(previousPage.current===destination)return;
  previousPage.current=destination;setMenu(false);focusPage();
 },[route.page,route.section,route.view,route.detail,Boolean(data)]);
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
  request<Bootstrap>('/api/bootstrap?view=essential').then(hydrateBootstrap).then(async next=>{
   let raw:string|null=null;
   try{raw=sessionStorage.getItem(next.ui.reload_storage_key);}catch{setStorageError(true);}
   const resumed=await restoreSession(next,raw,p=>request<Projection>('/api/simulate',{parameters:p,model_version:next.model_version}));
   setSession(resumed.session);setRecovery(resumed.recovery);
   setData({...next,resumedProjection:resumed.projection});
  }).catch(()=>setError(true));
 };
 useEffect(()=>{
  if(!data||recovery)return;
  const persist=()=>{try{sessionStorage.setItem(data.ui.reload_storage_key,encodeSession(data,session));}catch{setStorageError(true);}};
  persist();window.addEventListener('pagehide',persist);
  return()=>window.removeEventListener('pagehide',persist);
 },[data,session,recovery]);
 const downloadRecovery=()=>{
  if(!recovery)return;
  const url=URL.createObjectURL(new Blob([recovery],{type:'application/json'}));
  const a=document.createElement('a');a.href=url;a.download=data!.ui.id+'-draft.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 };
 useEffect(load,[]);
 useEffect(()=>{if(data)document.title=data.ui.document_title;},[data]);
 useEffect(()=>{let lastHash:string|undefined;const sync=()=>{if(location.hash===lastHash)return;const next=essentialRoute(location.hash);const canonical='#'+next.page+(next.page==='glossaire'&&next.term?'?term='+encodeURIComponent(next.term):next.section==='scope'?'?section=scope':next.family?'?family='+encodeURIComponent(next.family):next.detail?'?detail='+next.detail:(next.view?'?view='+encodeURIComponent(next.view):'')+(next.focus?(next.view?'&':'?')+'focus='+encodeURIComponent(next.focus):''));if(location.hash!==canonical)history.replaceState(null,'',canonical);lastHash=location.hash;setRoute(next);setLegacyProof(next.proof||null);window.scrollTo(0,0);};sync();window.addEventListener('hashchange',sync);window.addEventListener('popstate',sync);return()=>{window.removeEventListener('hashchange',sync);window.removeEventListener('popstate',sync);};},[]);
 useEffect(()=>{
  if(!data||!legacyProof)return;
  let live=true;
  if(legacyProof.startsWith('capability:')){
   request<Proof>('/api/capability?id='+encodeURIComponent(legacyProof.slice('capability:'.length))+'&model_version='+encodeURIComponent(data.model_version)).then(value=>{if(live){setProof(value);setLegacyProof(null);}}).catch(()=>{if(live){setProof(data.ui.essential.proofs.scope);setLegacyProof(null);}});
  }else{setProof(data.ui.essential.proofs[legacyProof]||data.ui.essential.proofs.scope);setLegacyProof(null);}
  return()=>{live=false;};
 },[data,legacyProof]);
 if(!data)return <div className="boot" aria-busy={!error}><div className="boot-mark"/>{error?<><p role="alert">{initial.errors?.network}</p><button onClick={load}>{initial.labels?.retry}</button></>:<p>{initial.labels?.loading}</p>}</div>;
 const {ui}=data,active=ui.essential.nav.find((n:Data)=>n.id===navigationPage(route.page)),page=ui.essential.pages[route.page],HeadingIcon=icons[active.icon];
 return <StudyContext.Provider value={{data,openDoc:setDoc,session,setSession}}><EvidenceProvider open={setProof}><div className="app-shell essential-shell" onFocusCapture={()=>{hiddenViewportFocus.current=null;}} onBlurCapture={event=>{if(!event.relatedTarget&&event.target instanceof HTMLElement&&hiddenByViewport(event.target,window.matchMedia('(max-width:900px)').matches))hiddenViewportFocus.current=event.target;}}><aside ref={navigationRef} id="study-navigation" className={'sidebar '+(menu?'is-open':'')} onBlur={event=>{if(menu&&!event.currentTarget.contains(event.relatedTarget))setMenu(false);}}><div className="brand"><a className="brand-home" href="#vision" aria-label={ui.essential.home} onClick={()=>navigate('vision')}><div className="brand-symbol"><img className="flow-source-mark" src={ui.brand_assets.flow} alt={ui.brand_assets.flow_alt}/></div><small>{ui.brand_subtitle}</small></a><button ref={menuCloseRef} className="mobile icon-button" onClick={closeMenu} aria-label={ui.labels.close}><X/></button></div><nav>{<SidebarNav ui={ui} route={route} close={navigate}/>}</nav><div className="sidebar-foot"><img className="beaumanoir-source-logo" src={ui.brand_assets.beaumanoir} alt={ui.brand_assets.beaumanoir_alt}/><small>{ui.labels.model_version}<br/><code>{data.model_version.slice(0,10)}</code></small></div></aside><div className="workspace"><header className="topbar"><button ref={menuTriggerRef} className="mobile icon-button" aria-label={ui.labels.navigation} aria-expanded={menu} aria-controls="study-navigation" onClick={()=>setMenu(open=>!open)}><Menu/></button><span><b>{active.label}</b></span><span className="reference-pill">{ui.editions[data.edition.mode]}<span>{new Intl.DateTimeFormat(ui.locale,{day:'2-digit',month:'short',year:'numeric'}).format(new Date(data.edition.date))}</span></span></header><main ref={mainRef}>{recovery&&<aside className="session-notice" role="alert"><p>{ui.reload_session.incompatible}</p><div className="actions"><button className="secondary" onClick={downloadRecovery}>{ui.reload_session.download}</button><button className="primary" onClick={()=>setRecovery(null)}>{ui.reload_session.discard}</button></div></aside>}{storageError&&<aside className="session-notice" role="alert">{ui.reload_session.storage}</aside>}{serverStatus.unreachable?<aside className="server-update server-unreachable" role="alert"><div><strong>{ui.server_update.unreachable_message}</strong><p>{ui.server_update.unreachable_note}</p></div><button className="secondary" onClick={serverStatus.recheck} disabled={serverStatus.checking} aria-busy={serverStatus.checking}>{serverStatus.checking?ui.server_update.checking:ui.server_update.retry}</button></aside>:serverStatus.available&&<aside className="server-update" role="status"><div><strong>{ui.server_update.message}</strong><p>{ui.server_update.note}</p></div><button className="primary" onClick={()=>window.location.reload()}>{ui.server_update.action}</button></aside>}<PageHeading key={route.page} active={active} page={page} icon={<HeadingIcon/>}/>{['pending_reestimation','partially_estimated'].includes(ui.essential.core_results.estimation_status)&&['comparer','se-projeter','simuler','evaluation-core','parametres'].includes(route.page)&&<aside className="core-method-notice" role="status"><h2>{ui.essential.core_results.status.title}</h2><p><MethodText>{ui.essential.core_status_summary}</MethodText></p></aside>}{route.page==='comparer'&&<ComparePage/>}{route.page==='se-projeter'&&<ProjectionPage/>}<div hidden={route.page!=='simuler'}><Simulations view="essential"/></div>{(route.page==='synvance'||route.page.startsWith('synvance-'))&&<SynvanceReferencePage view={route.page==='synvance-business'?'business':route.page==='synvance-oms'?'oms':route.page==='synvance-costs'?'costs':'overview'} providerId={route.page==='synvance-microsoft'?'microsoft':route.page==='synvance-sap'?'sap':undefined}/>}{route.page==='vision'&&<FrameworkVisionPage/>}{route.page==='glossaire'&&<GlossaryPage key={route.term||'all'} term={route.term}/>}{route.page==='conditions-realisation'&&<DeliveryConditionsPage/>}{route.page==='capacite-realisation'&&<DeliveryReadinessPage view={route.view} focus={route.focus}/>}{route.page==='cartographie'&&<CartographyPage/>}{route.page==='modele'&&<ModelPage view={route.section==='scope'?'scope':route.view}/>}{route.page==='complexite'&&<CoreMethodPage/>}{route.page==='calcul-net'&&<NetCalculationPage/>}{route.page==='calcul-run'&&<RunCalculationPage/>}{route.page==='marche'&&<MarketMethodPage/>}{route.page==='etude-marche'&&<MarketStudyPage view={route.view}/>}{route.page==='leviers'&&<LeversPage/>}{route.page==='parametres'&&<FrameworkPage detail={route.detail}/>}{route.page==='evaluation-core'&&<EconomicEvaluationsPage familyId={route.family}/>}</main></div></div>{proof&&<ProofDialog proof={proof} onClose={()=>setProof(null)}/ >}{doc&&<DocumentViewer key={doc} path={doc} onClose={()=>setDoc(null)}/>}</EvidenceProvider></StudyContext.Provider>;
}
function Chevron(){return <span className="nav-current"/>;}
function SidebarNav({ui,route,close}:{ui:Data;route:Route;close:(destination:string)=>void}){
 const byId=new Map<string,Data>(ui.essential.nav.map((item:Data)=>[item.id,item]));
 return <>{ui.essential.nav_groups.map((group:Data)=><div className="essential-nav-group" role="group" aria-label={group.label} key={group.label}><p className="nav-group-title">{group.label}</p>{group.items.map((id:string)=>{const item=byId.get(id)!;const Icon=icons[item.icon];return <a href={'#'+id} key={id} aria-current={navigationPage(route.page)===id?'page':undefined} onClick={()=>close(id)}><Icon size={19}/><span>{item.label}</span>{navigationPage(route.page)===id&&<Chevron/>}</a>;})}</div>)}</>;
}
