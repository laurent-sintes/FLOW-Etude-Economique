import {useEffect,useRef,useState,type ReactNode} from 'react';
import {GlossaryText} from './GlossaryText';
import {useStudy,type Data} from './context';

// A single, brief cue when the reading landmark first enters the viewport.
export function useReadingArrival<T extends HTMLElement=HTMLElement>(identity:string){
 const ref=useRef<T>(null),[arrived,setArrived]=useState(false);
 useEffect(()=>{
  setArrived(false);
  const element=ref.current;if(!element)return;
  const observer=new IntersectionObserver(entries=>{
   if(entries.some(entry=>entry.isIntersecting)){setArrived(true);observer.disconnect();}
  },{threshold:.15});
  observer.observe(element);return()=>observer.disconnect();
 },[identity]);
 return {ref,arrived};
}

export function PageHeading({active,page,icon}:{active:Data;page:Data;icon:ReactNode}){
 const {data}=useStudy();const ui=data.ui;
 const group=ui.essential.nav_groups.find((g:Data)=>g.items.includes(active.id));
 const {ref,arrived}=useReadingArrival<HTMLDivElement>(active.id);
 return <header className="page-heading reading-hero" data-arrived={arrived}>
  <div className="reading-hero-copy">
   <div className="reading-eyebrow"><span className="reading-page-symbol" aria-hidden="true">{icon}</span><span>{group?.label||active.label}</span>{group&&group.sequential!==false&&<span className="reading-step" aria-hidden="true">{String(group.items.indexOf(active.id)+1).padStart(2,'0')+' / '+String(group.items.length).padStart(2,'0')}</span>}</div>
   <h1><GlossaryText>{page.title}</GlossaryText></h1>
   {page.intro&&<p className="lead"><GlossaryText>{page.intro}</GlossaryText></p>}
  </div>
  <div ref={ref} className="reading-hero-art" aria-hidden="true"><span className="reading-orbit"/><span className="reading-art-icon">{icon}</span><span className="reading-orbit-traveler"><span className="reading-art-dot"/></span></div>
 </header>;
}
