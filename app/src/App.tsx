import {useEffect,useState} from 'react';
import {Compass,Calculator,ChartNoAxesCombined,ListTree,Server,Menu,X} from 'lucide-react';
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
import {useServerUpdate} from './useServerUpdate';
import {hydrateBootstrap} from './modelTransport';
import {PageHeading} from './ReadingIdentity';

const icons:Record<string,typeof Compass>={compass:Compass,calculator:Calculator,chart:ChartNoAxesCombined,grid:ListTree,server:Server};
type Route={page:'vision'|'comparer'|'se-projeter'|'simuler'|'modele'|'complexite'|'marche'|'parametres'|'evaluation-core'|'calcul-net'|'calcul-run'|'leviers'|'etude-marche';proof?:string};
function essentialRoute(hash:string):Route{
 const [raw,query='']=hash.replace(/^#/,'').split('?'),params=new URLSearchParams(query);
 if(raw==='vision'||raw==='comparer'||raw==='se-projeter'||raw==='simuler'||raw==='modele'||raw==='complexite'||raw==='marche'||raw==='parametres'||raw==='evaluation-core'||raw==='calcul-net'||raw==='calcul-run'||raw==='leviers'||raw==='etude-marche')return {page:raw};
 if(raw==='simulation-depenses')return {page:'se-projeter'};
 if(['simulation-hypotheses','simulations'].includes(raw))return {page:'simuler'};
 if(['logique','glossaire','faq','perimetres'].includes(raw))return {page:'modele',proof:raw==='perimetres'?(params.get('capability')?'capability:'+params.get('capability'):'scope'):undefined};
 if(raw==='sources')return {page:params.get('tab')==='market'?'comparer':'modele',proof:'scope'};
 if(['build','exploitation','estimations','market','synvance'].includes(raw))return {page:'comparer',proof:raw==='build'?'build':raw==='market'?'market':raw==='synvance'?'scope':'integration'};
 return {page:'comparer'};
}
export default function App({initial}:{initial:Data}){
 const [data,setData]=useState<Bootstrap|null>(null),[error,setError]=useState(false),[doc,setDoc]=useState<string|null>(null),[menu,setMenu]=useState(false);
 const [route,setRoute]=useState<Route>(()=>essentialRoute(location.hash));
 const [legacyProof,setLegacyProof]=useState<string|null>(null),[proof,setProof]=useState<Proof|null>(null);
 const updateAvailable=useServerUpdate(initial.server_revision||data?.server_revision,data?.ui.id);
 const [session,setSession]=useState<ReaderSession>({draft:{common:{},options:{}},horizon:0,chosen:'',name:''});
 const [recovery,setRecovery]=useState<string|null>(null),[storageError,setStorageError]=useState(false);
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
 useEffect(()=>{let lastHash:string|undefined;const sync=()=>{if(location.hash===lastHash)return;const next=essentialRoute(location.hash);if(location.hash!=='#'+next.page)history.replaceState(null,'','#'+next.page);lastHash=location.hash;setRoute(next);setLegacyProof(next.proof||null);window.scrollTo(0,0);};sync();window.addEventListener('hashchange',sync);window.addEventListener('popstate',sync);return()=>{window.removeEventListener('hashchange',sync);window.removeEventListener('popstate',sync);};},[]);
 useEffect(()=>{
  if(!data||!legacyProof)return;
  let live=true;
  if(legacyProof.startsWith('capability:')){
   request<Proof>('/api/capability?id='+encodeURIComponent(legacyProof.slice('capability:'.length))+'&model_version='+encodeURIComponent(data.model_version)).then(value=>{if(live){setProof(value);setLegacyProof(null);}}).catch(()=>{if(live){setProof(data.ui.essential.proofs.scope);setLegacyProof(null);}});
  }else{setProof(data.ui.essential.proofs[legacyProof]||data.ui.essential.proofs.scope);setLegacyProof(null);}
  return()=>{live=false;};
 },[data,legacyProof]);
 if(!data)return <div className="boot" aria-busy={!error}><div className="boot-mark"/>{error?<><p role="alert">{initial.errors?.network}</p><button onClick={load}>{initial.labels?.retry}</button></>:<p>{initial.labels?.loading}</p>}</div>;
 const {ui}=data,active=ui.essential.nav.find((n:Data)=>n.id===route.page),page=ui.essential.pages[route.page],HeadingIcon=icons[active.icon];
 return <StudyContext.Provider value={{data,openDoc:setDoc,session,setSession}}><EvidenceProvider open={setProof}><div className="app-shell essential-shell"><aside id="study-navigation" className={'sidebar '+(menu?'is-open':'')}><div className="brand"><a className="brand-home" href="#comparer" aria-label={ui.essential.home} onClick={()=>setMenu(false)}><div className="brand-symbol"><img className="flow-source-mark" src={ui.brand_assets.flow} alt={ui.brand_assets.flow_alt}/></div><small>{ui.brand_subtitle}</small></a><button className="mobile icon-button" onClick={()=>setMenu(false)} aria-label={ui.labels.close}><X/></button></div><nav>{<SidebarNav ui={ui} route={route} close={()=>setMenu(false)}/>}</nav><div className="sidebar-foot"><img className="beaumanoir-source-logo" src={ui.brand_assets.beaumanoir} alt={ui.brand_assets.beaumanoir_alt}/><small>{ui.labels.model_version}<br/><code>{data.model_version.slice(0,10)}</code></small></div></aside><div className="workspace"><header className="topbar"><button className="mobile icon-button" aria-label={ui.labels.navigation} aria-expanded={menu} aria-controls="study-navigation" onClick={()=>setMenu(true)}><Menu/></button><span><b>{active.label}</b></span><span className="reference-pill">{ui.editions[data.edition.mode]}<span>{new Intl.DateTimeFormat(ui.locale,{day:'2-digit',month:'short',year:'numeric'}).format(new Date(data.edition.date))}</span></span></header><main>{recovery&&<aside className="session-notice" role="alert"><p>{ui.reload_session.incompatible}</p><div className="actions"><button className="secondary" onClick={downloadRecovery}>{ui.reload_session.download}</button><button className="primary" onClick={()=>setRecovery(null)}>{ui.reload_session.discard}</button></div></aside>}{storageError&&<aside className="session-notice" role="alert">{ui.reload_session.storage}</aside>}{updateAvailable&&<aside className="server-update" role="status"><div><strong>{ui.server_update.message}</strong><p>{ui.server_update.note}</p></div><button className="primary" onClick={()=>window.location.reload()}>{ui.server_update.action}</button></aside>}<PageHeading key={route.page} active={active} page={page} icon={<HeadingIcon/>}/>{route.page==='comparer'&&<ComparePage/>}{route.page==='se-projeter'&&<ProjectionPage/>}<div hidden={route.page!=='simuler'}><Simulations view="essential"/></div>{route.page==='vision'&&<FrameworkVisionPage/>}{route.page==='modele'&&<ModelPage/>}{route.page==='complexite'&&<CoreMethodPage/>}{route.page==='calcul-net'&&<NetCalculationPage/>}{route.page==='calcul-run'&&<RunCalculationPage/>}{route.page==='marche'&&<MarketMethodPage/>}{route.page==='etude-marche'&&<MarketStudyPage/>}{route.page==='leviers'&&<LeversPage/>}{route.page==='parametres'&&<FrameworkPage/>}{route.page==='evaluation-core'&&<EconomicEvaluationsPage/>}</main></div></div>{proof&&<ProofDialog proof={proof} onClose={()=>setProof(null)}/ >}{doc&&<DocumentViewer key={doc} path={doc} onClose={()=>setDoc(null)}/>}</EvidenceProvider></StudyContext.Provider>;
}
function Chevron(){return <span className="nav-current"/>;}
function SidebarNav({ui,route,close}:{ui:Data;route:Route;close:()=>void}){
 const byId=new Map<string,Data>(ui.essential.nav.map((item:Data)=>[item.id,item]));
 return <>{ui.essential.nav_groups.map((group:Data)=><div className="essential-nav-group" role="group" aria-label={group.label} key={group.label}><p className="nav-group-title">{group.label}</p>{group.items.map((id:string)=>{const item=byId.get(id)!;const Icon=icons[item.icon];return <a href={'#'+id} key={id} aria-current={route.page===id?'page':undefined} onClick={close}><Icon size={19}/><span>{item.label}</span>{route.page===id&&<Chevron/>}</a>;})}</div>)}</>;
}
