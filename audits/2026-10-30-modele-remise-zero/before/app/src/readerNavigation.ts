import {useEffect,useState} from 'react';

export function matchesReadingText(query:string,...values:unknown[]){
 const words=(value:string)=>value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
 const text=words(JSON.stringify(values));
 return words(query).every(token=>text.some(word=>word.startsWith(token)));
}

export function parseReadingHash(hash:string){
 const [raw,query='']=hash.replace(/^#/,'').split('?');
 const params=new URLSearchParams(query);
 let page=raw==='sources'?(params.get('tab')==='market'?'market':params.get('tab')==='glossary'?'glossaire':'synvance'):raw;
 if(raw==='sources')params.delete('tab');
 if(page==='market'&&params.get('section')==='purchases'){page='perimetres';params.set('section','architecture');}
 if(page==='build'&&['integration','annual','run','work'].includes(params.get('section')||''))page='estimations';
 if(page==='perimetres'&&params.get('section')==='features'){page='estimations';params.set('section','work');}
 if(page==='estimations'&&params.get('section')==='work'){params.set('section','build');params.set('focus','work');}
 if(page==='perimetres'){
  const previous=params.get('section');
  if(previous==='complexity'||previous==='buy-coverage'){
   params.set('section','coverage');params.set('view',previous==='complexity'?'complexity':'gaps');
  }
  if(params.has('grid_q')){
   if(previous==='complexity'||!params.has('q'))params.set('q',params.get('grid_q')!);
   params.delete('grid_q');
  }
 }
 // Keep historic deep links readable while the sponsor journey has five destinations.
 if(page==='estimations'){
  const section=params.get('section')||'build';
  if(section==='integration'||section==='annual'||section==='run'){
   page='exploitation';params.set('section',section==='run'?'annual':section);
   params.set('detail',section==='integration'?'integration':'run');
  }else{
   page='build';params.set('section','build');
   if(params.get('focus'))params.set('detail',params.get('focus')==='work'?'work':'method');
  }
 }
 if(page==='market'&&(params.has('section')||params.has('q')||params.has('ref')||params.has('kind'))){
  params.set('detail','references');
 }
 return {page,params,hash:'#'+page+(params.size?'?'+params:'')};
}

/** Carry the reader's business context between the map and its Make work. */
export function capabilityReadingHref(destination:'map'|'work',capability:string,hash:string){
 const {params}=parseReadingHash(hash);
 params.set('capability',capability);
 if(destination==='work'){
  params.set('section','build');params.set('focus','work');
  params.set('detail','work');
  return '#build?'+params;
 }
 params.set('section','coverage');params.delete('focus');params.delete('detail');
 return '#perimetres?'+params;
}

export function shouldRestoreReadingPosition(hash:string){
 const route=parseReadingHash(hash);
 return !(['build','exploitation'].includes(route.page)&&route.params.get('focus'));
}

export function useReaderNavigation(storageKey?:string){
 const [hash,setHash]=useState(()=>location.hash);
 const [memory,setMemory]=useState<Record<string,string>>({});
 useEffect(()=>{
  const sync=()=>setHash(location.hash);
  window.addEventListener('hashchange',sync);window.addEventListener('popstate',sync);
  return()=>{window.removeEventListener('hashchange',sync);window.removeEventListener('popstate',sync);};
 },[]);
 useEffect(()=>{if(storageKey)try{setMemory(JSON.parse(sessionStorage.getItem(storageKey)||'{}'));}catch{}},[storageKey]);
 useEffect(()=>{
  const route=parseReadingHash(hash);if(!route.page||!storageKey)return;
  if(location.hash!==route.hash)history.replaceState(null,'',route.hash);
  setMemory(old=>{const next={...old,[route.page]:route.hash};try{sessionStorage.setItem(storageKey,JSON.stringify(next));}catch{}return next;});
 },[hash,storageKey]);
 const page=parseReadingHash(hash).page;
 useEffect(()=>{
  if(!storageKey||!page)return;
  const key=storageKey+'-positions';let positions:Record<string,number>={};
  try{positions=JSON.parse(sessionStorage.getItem(key)||'{}');}catch{}
  const frame=shouldRestoreReadingPosition(location.hash)?requestAnimationFrame(()=>window.scrollTo(0,Number(positions[page])||0)):null;
  const save=()=>{positions[page]=window.scrollY;try{sessionStorage.setItem(key,JSON.stringify(positions));}catch{}};
  window.addEventListener('scroll',save,{passive:true});window.addEventListener('pagehide',save);
  return()=>{if(frame!==null)cancelAnimationFrame(frame);window.removeEventListener('scroll',save);window.removeEventListener('pagehide',save);};
 },[page,storageKey]);
 return {page,href:(page:string)=>memory[page]||'#'+page};
}

export function useReadingState(){
 const [hash,setHash]=useState(()=>location.hash);
 useEffect(()=>{const sync=()=>setHash(location.hash);window.addEventListener('hashchange',sync);window.addEventListener('popstate',sync);return()=>{window.removeEventListener('hashchange',sync);window.removeEventListener('popstate',sync);};},[]);
 const {params}=parseReadingHash(hash);
 const set=(values:Record<string,string>,push=false)=>{
  const current=parseReadingHash(location.hash);
  Object.entries(values).forEach(([k,v])=>v?current.params.set(k,v):current.params.delete(k));
  const next='#'+current.page+(current.params.size?'?'+current.params:'');
  if(next===location.hash)return;
  history[push?'pushState':'replaceState'](null,'',next);
  window.dispatchEvent(new HashChangeEvent('hashchange'));
 };
 return {get:(key:string,fallback='')=>params.get(key)||fallback,set};
}
