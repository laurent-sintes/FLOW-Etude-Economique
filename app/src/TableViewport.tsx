import {useEffect,useLayoutEffect,useRef,useState,type ReactNode} from 'react';
import {Maximize2,Minimize2} from 'lucide-react';
import {useStudy} from './context';

/** A single table: page scrolling in reading mode, one scroll surface when expanded. */
export function TableViewport({title,children,className='',expandable=false,tools}:{title:string;children:ReactNode;className?:string;expandable?:boolean;tools?:ReactNode}){
 const {data}=useStudy();const L=data.ui.table_workspace;
 const [expanded,setExpanded]=useState(false);
 const dialog=useRef<HTMLDialogElement>(null),surface=useRef<HTMLDivElement>(null),trigger=useRef<HTMLButtonElement>(null);
 const saved=useRef({page:0,left:0,top:0,height:0});
 const open=()=>{const e=surface.current!;saved.current={page:window.scrollY,left:e.scrollLeft,top:Math.max(0,-e.getBoundingClientRect().top),height:e.offsetHeight};setExpanded(true);};
 const close=()=>{if(surface.current)saved.current.left=surface.current.scrollLeft;setExpanded(false);};
 useLayoutEffect(()=>{
  const e=surface.current;if(!e)return;
  e.scrollLeft=saved.current.left;
  if(expanded){dialog.current?.showModal();e.scrollTop=saved.current.top;e.focus({preventScroll:true});}
  else if(dialog.current?.open){dialog.current.close();window.scrollTo({top:saved.current.page});trigger.current?.focus({preventScroll:true});}
 },[expanded]);
 useEffect(()=>{
  if(!expanded)return;
  const previous=document.body.style.overflow;document.body.style.overflow='hidden';
  const route=()=>{const [page,query]=location.hash.split('?');return page+'?'+(new URLSearchParams(query||'').get('section')||'');};
  const currentRoute=route();const closeOnNavigation=()=>{if(route()!==currentRoute)setExpanded(false);};window.addEventListener('hashchange',closeOnNavigation);
  return()=>{document.body.style.overflow=previous;window.removeEventListener('hashchange',closeOnNavigation);};
 },[expanded]);
 useLayoutEffect(()=>{
  const e=surface.current;if(!e)return;
  let frame=0;
  const update=()=>{
   frame=0;const head=e.querySelector('thead'),foot=e.querySelector('tfoot');
   const hh=head?.getBoundingClientRect().height||0,fh=foot?.getBoundingClientRect().height||0;
   e.style.setProperty('--head-height',hh+'px');e.style.setProperty('--foot-height',fh+'px');
   if(expanded)return;
   const box=e.getBoundingClientRect(),limit=Math.max(0,e.clientHeight-hh-fh);
   e.style.setProperty('--head-shift',Math.min(limit,Math.max(0,-box.top))+'px');
   e.style.setProperty('--foot-shift',-Math.min(limit,Math.max(0,box.bottom-window.innerHeight))+'px');
  };
  const schedule=()=>{if(!frame)frame=requestAnimationFrame(update);};
  const focus=(event:FocusEvent)=>{
   const target=event.target as HTMLElement;if(target===e||target.closest('thead,tfoot'))return;
   requestAnimationFrame(()=>{
    update();const b=target.getBoundingClientRect(),box=e.getBoundingClientRect();
    const head=e.querySelector('thead')?.getBoundingClientRect(),foot=e.querySelector('tfoot')?.getBoundingClientRect();
    const top=Math.max(0,box.top,head?.bottom||0)+4,bottom=Math.min(window.innerHeight,box.bottom,foot?.top||Infinity)-4;
    const delta=b.top<top?b.top-top:b.bottom>bottom?b.bottom-bottom:0;
    if(delta){if(expanded)e.scrollBy({top:delta});else window.scrollBy({top:delta});}
   });
  };
  const observer=new ResizeObserver(schedule);observer.observe(e);const table=e.querySelector('table');if(table)observer.observe(table);
  window.addEventListener('scroll',schedule,{passive:true});window.addEventListener('resize',schedule);e.addEventListener('focusin',focus);
  update();return()=>{observer.disconnect();cancelAnimationFrame(frame);window.removeEventListener('scroll',schedule);window.removeEventListener('resize',schedule);e.removeEventListener('focusin',focus);};
 },[expanded,children]);
 const table=<div ref={surface} className={'table-scroll table-viewport '+className+(expanded?' is-expanded':'')} role="region" aria-label={title} tabIndex={0}>{children}</div>;
 return <div className="table-workspace">
  {(expandable||tools)&&<div className="table-workspace-tools">{tools}{expandable&&<button ref={trigger} className="secondary" onClick={open}><Maximize2 size={16}/>{L.expand}</button>}</div>}
  {expanded?<div aria-hidden="true" style={{height:saved.current.height}}/>:table}
  <dialog ref={dialog} className="table-dialog" aria-label={title} onCancel={event=>{event.preventDefault();close();}}>
   {expanded&&<><header><h2>{title}</h2><div className="actions">{tools}<button className="secondary" onClick={close}><Minimize2 size={16}/>{L.close}</button></div></header>{table}</>}
  </dialog>
 </div>;
}
